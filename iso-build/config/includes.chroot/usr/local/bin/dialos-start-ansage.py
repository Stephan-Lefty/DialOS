#!/usr/bin/env python3
"""DialOS: Sprachansage beim Start (Uhrzeit, Akkustaende, Internet, Wetter)."""
import getpass
import json
import os
import signal
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
KIND_REIHENFOLGE_VOLL = ["battery", "headset", "mouse", "keyboard"]
KIND_REIHENFOLGE_NUTZER = ["battery", "headset"]
KUNDENKONTO_BENUTZERNAME = "nutzer"
LADE_STATUS_AM_NETZ = {"charging", "fully-charged", "pending-charge"}
WETTER_SLOTS = [
    ("600", "Morgens"),
    ("1200", "Mittags"),
    ("1500", "Nachmittags"),
    ("1800", "Abends"),
]
BLUETOOTH_DEBUG_LOG = "/tmp/dialos-bluetooth-debug.log"
LOCK_DATEI = "/tmp/dialos-start-ansage.pid"
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
    try:
        return getpass.getuser() == KUNDENKONTO_BENUTZERNAME
    except Exception:
        return False


def spd_say(text):
    subprocess.run(["/usr/local/bin/dialos-say.py", text])


def upower_geraete():
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
    for mac in bluetooth_paired_geraete():
        try:
            subprocess.run(
                ["bluetoothctl", "connect", mac], capture_output=True, timeout=20
            )
        except subprocess.TimeoutExpired:
            pass


def alte_instanz_beenden():
    try:
        with open(LOCK_DATEI) as f:
            alte_pid = int(f.read().strip())
        with open(f"/proc/{alte_pid}/cmdline", "rb") as f:
            cmdline = f.read().decode(errors="replace")
        if "dialos-start-ansage" not in cmdline:
            raise ValueError("PID gehoert nicht mehr zu diesem Skript")
        os.kill(alte_pid, signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.kill(alte_pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except (FileNotFoundError, ValueError, ProcessLookupError):
        pass
    except Exception:
        pass
    try:
        with open(LOCK_DATEI, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


def bluetooth_debug_snapshot(label):
    zeilen = [f"=== {datetime.now().isoformat(timespec='seconds')} - {label} ==="]
    for mac in bluetooth_paired_geraete():
        try:
            ausgabe = subprocess.run(
                ["bluetoothctl", "info", mac], capture_output=True, text=True, timeout=5
            ).stdout.strip() or "(keine Ausgabe)"
        except Exception as fehler:
            ausgabe = f"(Fehler beim Ausfuehren: {fehler})"
        zeilen.append(f"--- bluetoothctl info {mac} ---")
        zeilen.append(ausgabe)
    for beschriftung, befehl in [
        ("pactl list sinks short", ["pactl", "list", "sinks", "short"]),
        ("pactl get-default-sink", ["pactl", "get-default-sink"]),
    ]:
        try:
            ausgabe = subprocess.run(
                befehl, capture_output=True, text=True, timeout=5
            ).stdout.strip() or "(keine Ausgabe)"
        except Exception as fehler:
            ausgabe = f"(Fehler beim Ausfuehren: {fehler})"
        zeilen.append(f"--- {beschriftung} ---")
        zeilen.append(ausgabe)
    zeilen.append("")
    try:
        with open(BLUETOOTH_DEBUG_LOG, "a") as f:
            f.write("\n".join(zeilen) + "\n")
    except Exception:
        pass


def warte_auf_geraete(erwartet=3, timeout=12):
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


GEOCLUE_DESKTOP_ID = "dialos-start-ansage"
GEOCLUE_ANGEFRAGTE_GENAUIGKEIT = 4  # GCLUE_ACCURACY_LEVEL_CITY - nicht mehr
    # Praezision anfragen als fuers Wetter noetig (Datenschutz).
GEOCLUE_MAX_UNGENAUIGKEIT_METER = 10000  # Fixes, die groeber sind als das
    # (typischerweise eine reine IP-Schaetzung, "ipf fallback" - live am
    # 2026-08-14 mit ~25-26 km Ungenauigkeit beobachtet, dabei komplett
    # falsche Stadt), werden verworfen - lieber die Wetteransage auslassen
    # als eine falsche Stadt/Region anzusagen (siehe Chat-Verlauf: Wien
    # statt Seefeld in Tirol).
GEOCLUE_WARTE_SEKUNDEN = 10


def geoclue_standort():
    """Aktuellen Standort (Breite, Laenge) per GeoClue2 ermitteln - nutzt
    automatisch die beste verfuegbare Quelle (WLAN-Abgleich ueber Mozilla
    Location Service, ggf. GPS/Mobilfunk falls vorhanden, sonst IP-
    Schaetzung als Fallback). Laeuft ueber den System-Bus, nicht den
    Session-Bus (GeoClue2 ist ein systemweiter Dienst). Gibt None zurueck,
    wenn kein ausreichend genauer Standort ermittelt werden konnte -
    absichtlich KEIN Fallback auf einen fest hinterlegten Ort, da das
    Geraet auch unterwegs genutzt wird.

    Voraussetzung: "dialos-start-ansage" muss in /etc/geoclue/geoclue.conf
    freigeschaltet sein (siehe scripts/dialos-full-office-setup.sh,
    Schritt 11) und org.gnome.system.location muss aktiviert sein (siehe
    01-dialos-defaults) - sonst "AccessDenied", von diesem try/except
    genauso abgefangen wie jeder andere Fehler.
    """
    try:
        import dbus

        bus = dbus.SystemBus()
        manager = bus.get_object(
            "org.freedesktop.GeoClue2", "/org/freedesktop/GeoClue2/Manager"
        )
        client_pfad = manager.GetClient(
            dbus_interface="org.freedesktop.GeoClue2.Manager"
        )
        client = bus.get_object("org.freedesktop.GeoClue2", client_pfad)
        client_props = dbus.Interface(client, "org.freedesktop.DBus.Properties")
        client_props.Set(
            "org.freedesktop.GeoClue2.Client", "DesktopId", GEOCLUE_DESKTOP_ID
        )
        client_props.Set(
            "org.freedesktop.GeoClue2.Client",
            "RequestedAccuracyLevel",
            dbus.UInt32(GEOCLUE_ANGEFRAGTE_GENAUIGKEIT),
        )
        client.Start(dbus_interface="org.freedesktop.GeoClue2.Client")

        standort_pfad = None
        for _ in range(GEOCLUE_WARTE_SEKUNDEN):
            pfad = client_props.Get("org.freedesktop.GeoClue2.Client", "Location")
            if str(pfad) != "/":
                standort_pfad = str(pfad)
                break
            time.sleep(1)

        client.Stop(dbus_interface="org.freedesktop.GeoClue2.Client")

        if not standort_pfad:
            return None

        standort = bus.get_object("org.freedesktop.GeoClue2", standort_pfad)
        standort_props = dbus.Interface(standort, "org.freedesktop.DBus.Properties")
        breite = float(
            standort_props.Get("org.freedesktop.GeoClue2.Location", "Latitude")
        )
        laenge = float(
            standort_props.Get("org.freedesktop.GeoClue2.Location", "Longitude")
        )
        genauigkeit = float(
            standort_props.Get("org.freedesktop.GeoClue2.Location", "Accuracy")
        )
        if genauigkeit > GEOCLUE_MAX_UNGENAUIGKEIT_METER:
            return None
        return breite, laenge
    except Exception:
        return None


def wetter_text():
    standort = geoclue_standort()
    if not standort:
        return ""
    breite, laenge = standort
    try:
        req = urllib.request.Request(
            f"http://wttr.in/{breite},{laenge}?format=j1&lang=de",
            headers={"User-Agent": "curl"},
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            daten = json.load(resp)
        ort = daten["nearest_area"][0]["areaName"][0]["value"]
        stundenwerte = {h["time"]: h for h in daten["weather"][0]["hourly"]}
        teile = [f"Das Wetter in {ort} wird heute so sein."]
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
    alte_instanz_beenden()

    jetzt = datetime.now()
    datum = f"{WOCHENTAGE[jetzt.weekday()]}, der {ORDINAL_TAGE[jetzt.day]} {MONATE[jetzt.month - 1]}"
    uhrzeit = f"{zahl_wort_0_99(jetzt.hour)} {zahl_wort_0_99(jetzt.minute)}"

    kind_reihenfolge = KIND_REIHENFOLGE_NUTZER if ist_kundenkonto() else KIND_REIHENFOLGE_VOLL
    erwartete_peripherie = len([k for k in kind_reihenfolge if k != "battery"])

    bluetooth_debug_snapshot("01-Skriptstart (vor bluetooth_reconnect_alle)")

    bluetooth_reconnect_alle()
    time.sleep(3)
    geraete = warte_auf_geraete(erwartet=erwartete_peripherie)

    bluetooth_debug_snapshot("02-Direkt vor der Ansage (nach Reconnect + Wartezeit)")

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
