#!/usr/bin/env python3
"""DialOS: Sprachansage beim Start (Uhrzeit, Akkustaende, Wetter)."""
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
KIND_REIHENFOLGE = ["battery", "headset", "mouse", "keyboard"]

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
    return EINER[einer] + "und" + ZEHNER[zehner]


def spd_say(text):
    subprocess.run(["/usr/local/bin/dialos-say.py", text])


def upower_geraete():
    """Liefert {kind: [prozent, ...]} fuer alle upower-Geraete mit Akku-Stand.

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
        for zeile in info.splitlines():
            gestrippt = zeile.strip()
            if gestrippt in KNOWN_KINDS:
                kind = gestrippt
            elif gestrippt.startswith("percentage:"):
                prozent = gestrippt.split(":", 1)[1].strip().rstrip("%")
        if kind and prozent:
            ergebnis.setdefault(kind, []).append(prozent)
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


def bluetooth_ist_verbunden(mac):
    try:
        out = subprocess.run(
            ["bluetoothctl", "info", mac], capture_output=True, text=True, timeout=5
        ).stdout
    except Exception:
        return False
    for zeile in out.splitlines():
        if zeile.strip().startswith("Connected:"):
            return "yes" in zeile
    return False


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


def bluetooth_ist_verbunden(mac):
    try:
        out = subprocess.run(
            ["bluetoothctl", "info", mac], capture_output=True, text=True, timeout=5
        ).stdout
    except Exception:
        return False
    for zeile in out.splitlines():
        if zeile.strip().startswith("Connected:"):
            return "yes" in zeile
    return False


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
    if not internet_verfuegbar():
        return ""
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


def main():
    jetzt = datetime.now()
    datum = f"{WOCHENTAGE[jetzt.weekday()]}, der {ORDINAL_TAGE[jetzt.day]} {MONATE[jetzt.month - 1]}"
    uhrzeit = f"{zahl_wort_0_99(jetzt.hour)} {jetzt.strftime('%M')}"

    bluetooth_reconnect_alle()
    bluetooth_reconnect_alle()
    time.sleep(3)
    geraete = warte_auf_geraete()

    akku_saetze = []
    for kind in KIND_REIHENFOLGE:
        werte = geraete.get(kind)
        label = KIND_LABEL[kind]
        if werte:
            akku_saetze.append(f"Akku-Stand {label}: {werte[0]} Prozent.")
        else:
            akku_saetze.append(f"Akku-Stand {label}: nicht verbunden.")

    text = (
        "Hallo, ich bin Michael, ich bin Dein persönlicher Assistent. "
        f"Heute ist {datum}. Die aktuelle Uhrzeit ist {uhrzeit}. "
        "Dial OS ist so eingerichtet, dass ich Dir jetzt den Akku-Stand aller "
        "angeschlossenen Geräte mitteile. " + " ".join(akku_saetze)
    )

    wetter = wetter_text()
    if wetter:
        text += " " + wetter

    text += " Ich wünsche Dir einen schönen Tag!"

    spd_say(text)


if __name__ == "__main__":
    main()
