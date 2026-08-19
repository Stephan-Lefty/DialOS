#!/usr/bin/env python3
"""DialOS: Sprachansage beim Start (Uhrzeit, Akkustaende, Internet, Wetter,
Lautstaerke-Abfrage per Vosk fuer nutzer)."""
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
def _sperr_pfad():
    """Pfad der Sperrdatei - PRO NUTZER, nicht geteilt.

    Fehler vom 2026-08-19, live gefunden: Die Datei lag fest auf
    "/tmp/dialos-start-ansage.pid" und damit fuer alle Nutzer an derselben
    Stelle. `nutzer` legte sie beim Anmelden um 08:12 an; `dialosadmin` konnte
    sie danach nicht mehr ueberschreiben (falscher Eigentuemer, 0664). Also
    konnte sich keine seiner Instanzen registrieren, keine sah die andere - und
    es liefen ZWEI Start-Ansagen gleichzeitig, jede mit ihrer eigenen
    Netzwerk-Ueberwachung. Das Risiko stand seit Tagen in TODO.md; notiert ist
    nicht behandelt.

    Zweitens haette die geteilte Datei einen Prozess des ANDEREN Nutzers zum
    Abschuss angeboten - dass das an den Rechten scheitert, ist Glueck und kein
    Entwurf.

    XDG_RUNTIME_DIR ist der richtige Ort: pro Nutzer, nur fuer ihn lesbar (0700),
    und beim Abmelden raeumt systemd ihn selbst weg. Dasselbe Muster wie
    marke_pfad() in dialos-diktat.py und dialos-notiz.py.
    """
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, "dialos-start-ansage.pid")
    return f"/tmp/dialos-start-ansage-{os.getuid()}.pid"


LOCK_DATEI = _sperr_pfad()
LAUTSTAERKE_OPTIONEN = {
    "hundert": 100, "100": 100,
    "fünfundsiebzig": 75, "75": 75,
    "fünfzig": 50, "50": 50,
    "fünfundzwanzig": 25, "25": 25,
    "aus": 0, "stumm": 0,
}
# Prozent -> Speech-Dispatcher-Intensitaet (-i, -100 bis +100, 0 =
# Normalwert) - Speech-Dispatcher kennt keine echten Prozent, "100 %"
# wird deshalb auf den Normalwert 0 abgebildet, nicht auf +100 (das
# waere lauter als normal, nicht "voll"). Grobe, aber nachvollziehbare
# Naeherung - Feinjustierung erst nach echtem Hoertest moeglich (siehe
# TODO.md).
LAUTSTAERKE_ZU_INTENSITAET = {100: 0, 75: -25, 50: -50, 25: -75}
LAUTSTAERKE_VOSK_MODELL = "/usr/local/share/vosk-model-de-small"
LAUTSTAERKE_AUFNAHME_SEKUNDEN = 4
LAUTSTAERKE_ABTASTRATE = 16000
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


def spd_say(text, intensitaet=None, frage=False):
    """Sprechen. frage=True markiert eine echte Frage an den Nutzer.

    Der Text behaelt sein Fragezeichen - Piper erzeugt daraus von selbst
    eine steigende Satzmelodie. Zusaetzlich stellt dialos-say.py einen
    kurzen Signalton voran, WENN der Nutzer das eingeschaltet hat
    (~/.config/dialos/frageton). Standard ist die Melodie allein.
    """
    cmd = ["/usr/local/bin/dialos-say.py"]
    if intensitaet is not None:
        cmd += ["--lautstaerke", str(intensitaet)]
    if frage:
        cmd.append("--frage")
    cmd.append(text)
    subprocess.run(cmd)


def bluetooth_karte_fuer_quelle(quelle_name):
    praefix = "bluez_input."
    if not quelle_name.startswith(praefix):
        return None
    return "bluez_card." + quelle_name[len(praefix):].replace(":", "_")


def bluetooth_profil_setzen(karten_name, profil):
    ergebnis = subprocess.run(
        ["pactl", "set-card-profile", karten_name, profil],
        capture_output=True, text=True,
    )
    return ergebnis.returncode == 0


ECHO_QUELLE = "dialos_mikrofon_ohne_echo"


def waehle_mikrofon_fuer_lautstaerke():
    try:
        out = subprocess.run(
            ["pactl", "-f", "json", "list", "sources"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        quellen = json.loads(out) if out.strip() else []
    except Exception:
        return None
    # UMGESTELLT AM 2026-08-17 (Stephans Entscheidung). Bis dahin stand
    # hier das Bluetooth-Mikrofon an erster Stelle. Jetzt dieselbe
    # Reihenfolge wie im Sprachbefehl-Dienst:
    #
    #   1. die echo-bereinigte Quelle (haengt selbst am eingebauten Mikrofon)
    #   2. das eingebaute Mikrofon
    #   3. Bluetooth nur, wenn es kein eingebautes gibt
    #
    # Drei Gruende fuer die Umstellung:
    #
    # - Das Umschalten auf HFP und wieder zurueck ist am 2026-08-17
    #   DREIMAL haengengeblieben. Der AIRHUG stand dann dauerhaft auf
    #   headset-head-unit, und die Wiedergabe lief in Telefonqualitaet -
    #   ohne dass jemand, der das Geraet nicht kennt, den Grund erraten
    #   koennte. Wer das Bluetooth-Mikrofon gar nicht erst oeffnet, kann
    #   auch nicht darin steckenbleiben.
    # - Die Echo-Unterdrueckung gibt es nur auf dem eingebauten Weg. Ueber
    #   Bluetooth wuerde die Frage also wieder die eigene Ansage mithoeren.
    # - Die Begruendung fuer die frueher bevorzugte Bluetooth-Quelle stammt
    #   aus dem Mikrofon-Vergleich vom 2026-08-13. Der stand unter 60 dB
    #   Uebersteuerung und ist damit nicht belastbar (siehe TODO.md).
    kandidaten = [q.get("name", "") for q in quellen if q.get("name") and not q["name"].endswith(".monitor")]
    if ECHO_QUELLE in kandidaten:
        return ECHO_QUELLE
    eingebaut = [n for n in kandidaten if not n.startswith("bluez_input.")]
    if eingebaut:
        return eingebaut[0]
    return kandidaten[0] if kandidaten else None


def lautstaerke_datei():
    """Pfad der gemerkten Lautstaerke - im Home des jeweiligen Kontos.

    Bei "nutzer" liegt das Home auf der verschluesselten Partition, die
    Einstellung ist damit genauso geschuetzt wie dessen uebrige Daten.
    """
    basis = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(basis, "dialos", "lautstaerke")


def gespeicherte_lautstaerke():
    """Gemerkte Lautstaerke in Prozent, oder None wenn noch keine da ist.

    None bedeutet "noch nie beantwortet" - dann wird nach der ersten
    Ansage gefragt (siehe main). Unplausible Werte werden verworfen, damit
    eine beschaedigte Datei nicht die Ansage verstellt.
    """
    try:
        with open(lautstaerke_datei(), encoding="utf-8") as datei:
            wert = int(datei.read().strip())
        return wert if wert in LAUTSTAERKE_ZU_INTENSITAET else None
    except Exception:
        return None


def lautstaerke_speichern(prozent):
    """Merkt die Lautstaerke dauerhaft. Fehler werden bewusst geschluckt -
    liesse sie sich nicht schreiben, wird beim naechsten Anmelden eben
    erneut gefragt. Das ist unschoen, aber harmlos."""
    try:
        pfad = lautstaerke_datei()
        os.makedirs(os.path.dirname(pfad), exist_ok=True)
        with open(pfad, "w", encoding="utf-8") as datei:
            datei.write(f"{prozent}\n")
        return True
    except Exception:
        return False


def frage_lautstaerke():
    """Fragt per Sprache nach der gewuenschten Ansage-Lautstaerke
    (100/75/50/25 Prozent oder "aus").

    Rueckgabe: die verstandene Prozentzahl, 0 fuer "aus", oder None bei
    JEDEM Fehlschlag (Vosk fehlt, kein Mikrofon, nichts oder nichts
    Passendes verstanden). None wird bewusst NICHT als 100 ausgegeben:
    der Aufrufer soll unterscheiden koennen zwischen "der Nutzer hat 100
    gesagt" (merken) und "wir haben nichts verstanden" (nichts merken,
    beim naechsten Mal erneut fragen).
    """
    try:
        import vosk
    except ImportError:
        return None

    quelle = waehle_mikrofon_fuer_lautstaerke()
    bluetooth_karte = None
    bluetooth_umgeschaltet = False
    if quelle and quelle.startswith("bluez_input."):
        bluetooth_karte = bluetooth_karte_fuer_quelle(quelle)
        if bluetooth_karte and (
            bluetooth_profil_setzen(bluetooth_karte, "headset-head-unit")
            or bluetooth_profil_setzen(bluetooth_karte, "headset-head-unit-cvsd")
        ):
            bluetooth_umgeschaltet = True
            time.sleep(1.5)
    if quelle:
        # Frueher wurde hier die systemweite Standard-Eingabe umgebogen.
        # Das ist ein Eingriff, der ueber diese eine Frage hinaus wirkt -
        # jedes andere Programm bekommt danach eine andere Quelle. Statt
        # dessen bekommt parec die Quelle jetzt direkt uebergeben (siehe
        # einmal_zuhoeren).
        pass

    # Formulierung bewusst als Rueckfrage NACH der Ansage: Der Nutzer hat
    # sie gerade gehoert und kann die Lautstaerke daran messen. Vorher
    # gefragt (bis 2026-08-16) musste er raten, wie laut das System
    # ueberhaupt ist - fuer einen blinden Nutzer ein sinnloser Massstab.
    spd_say(
        "War das angenehm laut? Du kannst es einmalig festlegen. "
        "Sage 100, 75, 50, 25 oder aus.",
        frage=True,
    )
    # Klares Startsignal direkt vor der Aufnahme - live am 2026-08-14
    # getestet: ohne dieses Signal wusste der Testnutzer nicht genau,
    # wann das Aufnahme-Fenster beginnt, und die Antwort wurde verpasst.
    spd_say("Und jetzt bitte.")

    def einmal_zuhoeren():
        """Ein Aufnahmefenster: aufnehmen, erkennen, Antwort zurueckgeben."""
        try:
            vosk.SetLogLevel(-1)
            modell = vosk.Model(LAUTSTAERKE_VOSK_MODELL)
            erkenner = vosk.KaldiRecognizer(modell, LAUTSTAERKE_ABTASTRATE)
            befehl = ["parec", f"--rate={LAUTSTAERKE_ABTASTRATE}",
                      "--channels=1", "--format=s16le"]
            if quelle:
                befehl.append(f"--device={quelle}")
            prozess = subprocess.Popen(befehl, stdout=subprocess.PIPE)
            audiodaten = bytearray()
            ende = time.time() + LAUTSTAERKE_AUFNAHME_SEKUNDEN
            while time.time() < ende:
                chunk = prozess.stdout.read(4000)
                if not chunk:
                    break
                audiodaten.extend(chunk)
            prozess.terminate()
            prozess.stdout.close()
            erkenner.AcceptWaveform(bytes(audiodaten))
            text = json.loads(erkenner.FinalResult()).get("text", "")
            for wort in text.split():
                if wort in LAUTSTAERKE_OPTIONEN:
                    return LAUTSTAERKE_OPTIONEN[wort]
        except Exception:
            pass
        return None

    # EINMAL NACHFRAGEN, dann aufgeben (Stephan, 2026-08-17).
    #
    # Warum ueberhaupt nachfragen: Ein einzelner Versuch scheitert schon
    # an einem Rauspern oder daran, dass jemand den Beginn des Fensters
    # verpasst. Genau das ist am 2026-08-16 beim ersten echten Test
    # passiert.
    #
    # Warum nur EINMAL und dann mit Ansage aufgeben: Ein Geraet, das
    # immer weiter fragt, ist fuer jemanden, der es nicht wegklicken
    # kann, eine Zumutung. Und das stille Aufgeben waere schlimmer als
    # das laute - wer nicht hoert, dass die Frage vorbei ist, spricht
    # womoeglich ins Leere.
    ergebnis = einmal_zuhoeren()
    if ergebnis is None:
        spd_say("Ich habe Dich nicht verstanden.", frage=True)
        spd_say("Und jetzt bitte.")
        ergebnis = einmal_zuhoeren()
        if ergebnis is None:
            spd_say("Schade, dass Du nicht antwortest.")

    if bluetooth_umgeschaltet and bluetooth_karte:
        bluetooth_profil_setzen(bluetooth_karte, "a2dp-sink")

    return ergebnis


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
    except PermissionError:
        # Fremder Nutzer - kann seit der Umstellung auf XDG_RUNTIME_DIR nicht
        # mehr vorkommen. Wenn doch, dann NICHT die eigene PID hineinschreiben:
        # eine Datei, in die man nicht schreiben darf, ist keine Sperre, und die
        # naechste Instanz wuerde sich wieder auf einen fremden Eintrag
        # verlassen.
        return
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

    # Lautstaerke nur fuer nutzer (Kundenkonto) - dialosadmin und andere
    # Konten werden nie gefragt, siehe TODO.md.
    #
    # Ablauf seit 2026-08-16 (Stephans Vorgabe): Beim ERSTEN Anmelden wird
    # zuerst normal angesagt und erst DANACH gefragt - so hat der Nutzer
    # die Lautstaerke gerade gehoert und kann sie beurteilen. Vorher
    # gefragt musste er raten. Die Antwort wird gemerkt und bei jedem
    # weiteren Anmelden verwendet, ohne erneut zu fragen.
    lautstaerke_prozent = 100
    frage_noetig = False
    if ist_kundenkonto():
        gespeichert = gespeicherte_lautstaerke()
        if gespeichert is None:
            frage_noetig = True   # noch nie beantwortet
        else:
            lautstaerke_prozent = gespeichert
    intensitaet = LAUTSTAERKE_ZU_INTENSITAET.get(lautstaerke_prozent, 0)

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
        # Frueher stand hier "DialOS ist so eingerichtet, dass ich Dir
        # jetzt den Akku-Stand aller angeschlossenen Geraete mitteile."
        # Zwei Gruende fuer die Kuerzung (Stephan, 2026-08-17): Der
        # Produktname wurde als "Dial OS" gesprochen und klang sperrig -
        # und der Satz erklaerte eine EINRICHTUNG, statt die Information
        # zu geben. Der Nutzer hoert das bei JEDER Anmeldung; Michael hat
        # sich zwei Saetze vorher vorgestellt und kann es direkt sagen.
        text += " Ich nenne Dir noch die Akku-Stände. " + " ".join(akku_saetze)

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

    if lautstaerke_prozent > 0:
        spd_say(text, intensitaet=intensitaet)
    # Bei gemerkter "aus"-Einstellung kaeme man hier nie an - "aus" wird
    # bewusst nicht gespeichert, siehe unten.

    if frage_noetig:
        gewaehlt = frage_lautstaerke()
        if gewaehlt is None:
            # Nichts verstanden: NICHT merken, damit beim naechsten
            # Anmelden erneut gefragt wird. Bis dahin bleibt es bei 100 %.
            pass
        elif gewaehlt > 0:
            gemerkt = lautstaerke_speichern(gewaehlt)
            neue_intensitaet = LAUTSTAERKE_ZU_INTENSITAET.get(gewaehlt, 0)
            # Bestaetigung in der NEU gewaehlten Lautstaerke - so hoert der
            # Nutzer sofort, worauf er sich gerade festgelegt hat.
            spd_say(
                f"Alles klar, ich bleibe bei {gewaehlt} Prozent."
                if gemerkt
                else f"Alles klar, {gewaehlt} Prozent - merken konnte ich es "
                     "leider nicht, ich frage beim nächsten Mal erneut.",
                intensitaet=neue_intensitaet,
            )
        else:
            # "aus" gilt bewusst NUR fuer diese Anmeldung und wird NICHT
            # gespeichert. Waere es dauerhaft, kaeme keine Ansage mehr -
            # und damit auch nie wieder diese Frage. Ein blinder Nutzer
            # haette dann ohne fremde Hilfe keinen Weg zurueck.
            spd_say("Alles klar, für diesmal bin ich still.")

    netzwerk_ueberwachung(hat_internet)


if __name__ == "__main__":
    main()
