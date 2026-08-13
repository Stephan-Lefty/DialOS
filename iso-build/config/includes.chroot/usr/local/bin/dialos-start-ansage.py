#!/usr/bin/env python3
"""DialOS: Sprachansage beim Start (Uhrzeit, Akkustaende, Internet, Wetter)."""
import getpass
import json
import socket
import subprocess
import time
import urllib.request
from datetime import datetime

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]
ORDINAL_TAGE = [
    "", "erste", "zweite", "dritte", "vierte", "fünfte", "sechste", "siebte",
    "achte", "neunte", "zehnte", "elfte", "zwölfte", "dreizehnte", "vierzehnte",
    "fünfzehnte", "sechzehnte", "siebzehnte", "achtzehnte", "neunzehnte",
    "zwanzigste", "einundzwanzigste", "zweiundzwanzigste", "dreiundzwanzigste",
    "vierundzwanzigste", "fünfundzwanzigste", "sechsundzwanzigste",
    "siebenundzwanzigste", "achtundzwanzigste", "neunundzwanzigste",
    "dreißigste", "einunddreißigste",
]
KNOWN_KINDS = {
    "battery", "mouse", "keyboard", "headset", "headphones",
    "speakers", "phone", "tablet", "gaming-input", "pen", "touchpad",
}
KIND_LABEL = {
    "battery": "Laptop",
    "headset": "Lautsprecher",
    "mouse": "Maus",
    "keyboard": "Tastatur",
}
# Volle Abfrage/Ansage (Admin-Konto, z.B. DialOS-Admin): Laptop, Lautsprecher,
# Maus, Tastatur. Kundenkonto ("nutzer") bekommt nur Laptop + Lautsprecher -
# externe Maus/Tastatur sind fuer die sprachgesteuerte Zielgruppe nicht
# relevant und haben das Warten auf "erwartet=3" unnoetig verzoegert, wenn
# gar keine Maus/Tastatur gekoppelt ist.
KIND_REIHENFOLGE_VOLL = ["battery", "headset", "mouse", "keyboard"]
KIND_REIHENFOLGE_NUTZER = ["battery", "headset"]
KUNDENKONTO_BENUTZERNAME = "nutzer"
# upower-"state:"-Werte, die bedeuten "haengt gerade am Stromnetz" - dann
# ist der Laptop-Akku-Stand fuer die Ansage nicht relevant.
LADE_STATUS_AM_NETZ = {"charging", "fully-charged", "pending-charge"}
WETTER_SLOTS = [
    ("600", "Morgens"),
    ("1200", "Mittags"),
    ("1500", "Nachmittags"),
    ("1800", "Abends"),
]
EINER = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun"]
ZEHN_BIS_NEUNZEHN = ["zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn",
                     "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
ZEHNER = {2: "zwanzig", 3: "dreißig", 4: "vierzig", 5: "fünfzig",
          6: "sechzig", 7: "siebzig", 8: "achtzig", 9: "neunzig"}


def zahl_wort_0_99(n):
    if n < 10:
        return EINER[n]
    if n < 20:
        return ZEHN_BIS_NEUNZEHN[n - 10]
    zehner, einer = divmod(n, 10)
    if einer == 0:
        return ZEHNER[zehner]
    einer_wort = "ein" if einer == 1 else EINER[einer]
    return einer_wort + "und" + ZEHNER[zehner]


def ist_kundenkonto():
    """True, wenn dieses Skript unter dem Kundenkonto ("nutzer") laeuft.
    Bei jedem anderen Konto (z.B. DialOS-Admin/dialosadmin) gilt die volle
    Abfrage/Ansage. Bei einem Fehler (z.B. Benutzername nicht ermittelbar)
    wird sicherheitshalber die volle Variante angenommen, nicht die
    eingeschraenkte."""
    try:
        return getpass.getuser() == KUNDENKONTO_BENUTZERNAME
    except Exception:
        return False


def spd_say(text):
    subprocess.run(["/usr/local/bin/dialos-say.py", text])


def upower_geraete():
    """Liefert {kind: [(prozent, status), ...]} fuer alle upower-Geraete mit
    Akku-Stand. status ist der upower-"state:"-Wert (z.B. "charging",
    "discharging", "fully-charged") oder None, falls das Geraet keinen
    Ladezustand meldet (z.B. die meisten Bluetooth-Peripheriegeraete).

    upower -i hat KEIN "kind:"-Feld bei Peripheriegeraeten, sondern eine
    Kopfzeile mit dem reinen Geraetetyp (z.B. "mouse"), darunter eingerueckt
    "percentage:". Wir suchen daher nach dieser Kopfzeile.
    """
    ergebnis = {}
    try:
        pfade = subprocess.run(
            ["upower", "-e"], capture_output=True, text=True, timeout=5
        ).stdout.splitlines()
    except Exception:
        return ergebnis
    for pfad in pfade:
        pfad = pfad.strip()
        if not pfad or "line_power" in pfad or "DisplayDevice" in pfad:
            continue
        try:
            info = subprocess.run(
                ["upower", "-i", pfad], capture_output=True, text=True, timeout=5
            ).stdout
        except Exception:
            continue
        kind = None
        prozent = None
        status = None
        for zeile in info.splitlines():
            gestrippt = zeile.strip()
            if gestrippt in KNOWN_KINDS:
                kind = gestrippt
            elif gestrippt.startswith("percentage:"):
                prozent = gestrippt.split(":", 1)[1].strip().rstrip("%")
            elif gestrippt.startswith("state:"):
                status = gestrippt.split(":", 1)[1].strip()
        if kind and prozent:
            ergebnis.setdefault(kind, []).append((prozent, status))
    return ergebnis


def bluetooth_paired_geraete():
    try:
        out = subprocess.run(
            ["bluetoothctl", "devices", "Paired"], capture_output=True, text=True, timeout=5
        ).stdout
    except Exception:
        return []
    geraete = []
    for zeile in out.splitlines():
        teile = zeile.strip().split(" ", 2)
        if len(teile) >= 2 and teile[0] == "Device":
            geraete.append(teile[1])
    return geraete


def bluetooth_reconnect_alle():
    """Verbindet alle gekoppelten Bluetooth-Geraete neu (v.a. wichtig fuer
    Audiogeraete, deren Audio-Profil nach einem Sitzungswechsel manchmal
    nicht automatisch wiederhergestellt wird). Ein bereits verbundenes
    Geraet erneut zu verbinden ist unschaedlich, daher keine Vorab-Pruefung
    (die durch mehrere schnelle bluetoothctl-Aufrufe hintereinander zu
    Wettlaufsituationen fuehren kann)."""
    for mac in bluetooth_paired_geraete():
        try:
            subprocess.run(
                ["bluetoothctl", "connect", mac], capture_output=True, timeout=20
            )
        except subprocess.TimeoutExpired:
            pass


def warte_auf_geraete(erwartet=3, timeout=12):
    """Wartet kurz, bis Bluetooth-Geraete nach dem Login erkannt wurden."""
    ende = time.time() + timeout
    geraete = upower_geraete()
    while time.time() < ende:
        anzahl = sum(len(v) for k, v in geraete.items() if k != "battery")
        if anzahl >= erwartet:
            break
        time.sleep(1)
        geraete = upower_geraete()
    return geraete


def internet_verfuegbar():
    try:
        socket.create_connection(("wttr.in", 80), timeout=3)
        return True
    except OSError:
        return False


def wetter_text():
    try:
        req = urllib.request.Request(
            "http://wttr.in/?format=j1&lang=de", headers={"User-Agent": "curl"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            daten = json.load(resp)
        ort = daten["nearest_area"][0]["areaName"][0]["value"]
        stundenwerte = {h["time"]: h for h in daten["weather"][0]["hourly"]}
        teile = ["Das Wetter wird heute so sein."]
        regen_erwartet = False
        for zeit_key, label in WETTER_SLOTS:
            eintrag = stundenwerte.get(zeit_key)
            if not eintrag:
                continue
            beschreibung = eintrag["lang_de"][0]["value"]
            temp = eintrag.get("tempC", "").strip()
            if temp:
                teile.append(f"{label}: {beschreibung}, {temp} Grad.")
            else:
                teile.append(f"{label}: {beschreibung}.")
            try:
                if int(eintrag.get("chanceofrain", 0)) >= 50:
                    regen_erwartet = True
            except ValueError:
                pass
        if regen_erwartet:
            teile.append("Es wird Regen erwartet, denk an einen Regenschirm.")
        return " ".join(teile)
    except Exception:
        return ""


UEBERWACHUNGS_INTERVALL_SEKUNDEN = 90


def netzwerk_ueberwachung(letzter_status):
    """Laeuft nach der Start-Ansage dauerhaft im Hintergrund weiter (endet
    erst, wenn der Prozess selbst beendet wird, z.B. beim Abmelden) und
    prueft alle UEBERWACHUNGS_INTERVALL_SEKUNDEN erneut die Internet-
    verbindung. Nur bei einer tatsaechlichen Aenderung gegenueber dem
    zuletzt bekannten Status (verbunden <-> getrennt) gibt es eine kurze,
    freundliche Sprachansage - bei unveraendertem Status bleibt es still.
    """
    while True:
        time.sleep(UEBERWACHUNGS_INTERVALL_SEKUNDEN)
        try:
            aktueller_status = internet_verfuegbar()
        except Exception:
            continue
        if aktueller_status == letzter_status:
            continue
        letzter_status = aktueller_status
        if aktueller_status:
            spd_say("Gute Nachricht, die Internetverbindung wurde gerade hergestellt.")
        else:
            spd_say(
                "Die Internetverbindung wurde gerade unterbrochen. Bitte "
                "stelle die Internetverbindung wieder her, wenn Du magst."
            )


def main():
    jetzt = datetime.now()
    datum = f"{WOCHENTAGE[jetzt.weekday()]}, der {ORDINAL_TAGE[jetzt.day]} {MONATE[jetzt.month - 1]}"
    uhrzeit = f"{zahl_wort_0_99(jetzt.hour)} {zahl_wort_0_99(jetzt.minute)}"

    kind_reihenfolge = KIND_REIHENFOLGE_NUTZER if ist_kundenkonto() else KIND_REIHENFOLGE_VOLL
    erwartete_peripherie = len([k for k in kind_reihenfolge if k != "battery"])

    bluetooth_reconnect_alle()
    time.sleep(3)
    geraete = warte_auf_geraete(erwartet=erwartete_peripherie)

    # Nur Geraete ansagen, die gerade tatsaechlich eingerichtet/verbunden
    # sind - kein "nicht verbunden" mehr fuer Geraete, die der Nutzer gar
    # nicht besitzt (z.B. keine externe Maus). Beim Laptop-Akku selbst wird
    # die Ansage zusaetzlich uebersprungen, wenn er gerade am Stromnetz
    # haengt (laedt/voll) - der Akku-Stand ist dann nicht relevant.
    akku_saetze = []
    for kind in kind_reihenfolge:
        werte = geraete.get(kind)
        if not werte:
            continue
        prozent, status = werte[0]
        if kind == "battery" and status in LADE_STATUS_AM_NETZ:
            continue
        label = KIND_LABEL[kind]
        akku_saetze.append(f"Akku-Stand {label}: {prozent} Prozent.")

    text = (
        "Hallo, ich bin Michael, ich bin Dein persönlicher Assistent. "
        f"Heute ist {datum}. Die aktuelle Uhrzeit ist {uhrzeit}."
    )
    if akku_saetze:
        text += (
            " Dial OS ist so eingerichtet, dass ich Dir jetzt den Akku-Stand aller "
            "angeschlossenen Geräte mitteile. " + " ".join(akku_saetze)
        )

    # Internetstatus und Wetter werden bewusst NICHT als eigene spd_say()-
    # Aufrufe gesprochen, sondern in denselben Text eingehaengt wie der Rest:
    # dialos-say.py mutet waehrend jeder Sprachausgabe die System-Lautstaerke
    # und hebt die Mute-Sperre danach wieder auf - bei mehreren Aufrufen
    # hintereinander war dazwischen kurz Hintergrundmusik zu hoeren (Mute
    # wurde kurz aufgehoben, bevor der naechste Aufruf sie erneut setzte).
    # Ein einziger zusammenhaengender spd_say()-Aufruf haelt die Ansage in
    # einem einzigen Mute-Fenster.
    hat_internet = internet_verfuegbar()
    if hat_internet:
        text += " Es besteht eine Internetverbindung."
        wetter = wetter_text()
        if wetter:
            text += " " + wetter
    else:
        text += (
            " Ich habe aktuell keine Internetverbindung. Bitte stelle eine "
            "Internetverbindung her."
        )

    text += " Ich wünsche Dir einen schönen Tag!"

    spd_say(text)

    netzwerk_ueberwachung(hat_internet)


if __name__ == "__main__":
    main()
