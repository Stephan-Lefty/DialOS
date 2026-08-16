#!/usr/bin/env python3
"""DialOS: hoert dauerhaft auf "auf Linux umschalten" / "auf Windows
umschalten" und stellt die Desktop-Optik entsprechend um.

Stephans Vorgabe vom 2026-08-16: Das Umschalten der Desktop-Optik muss
per Sprache gehen - kein Menue, kein Terminal. Fuer die Zielgruppe ist
das nicht Bequemlichkeit, sondern die einzige brauchbare Bedienung.

DER BEFEHL IST EIN GANZER SATZ, KEIN EINZELWORT - ebenfalls Stephans
Vorgabe, und sie loest ein echtes Problem. Ein einzelnes "Windows" faellt
im Gespraech staendig; der Schreibtisch wuerde sich ungefragt umstellen,
und ein blinder Nutzer wuesste nicht, warum plotzlich alles anders
klingt. Im Test am 2026-08-16 hat der Satz "ich habe frueher windows
benutzt" beim Erkenner "auf auf windows" ergeben - also durchaus das Wort
"windows", aber eben NICHT "umschalten". Deshalb muss beides im Satz
vorkommen: das Ziel UND das Wort "umschalten". Damit war der
Stoersatz im Test wirkungslos.

Fuer den Linux-Stil gelten zwei Ziele: "Linux" und "Gnome". Stephan hat
"Linux" nachgereicht, weil es das Wort ist, das jemand aus der
Windows-Welt kennt - "Gnome" sagt ihm nichts. Beide anzunehmen kostet
nichts und erspart dem Nutzer, sich fuer eines zu entscheiden.

Dies ist der erste dauerhaft lauschende Dienst in DialOS. Bisher wurde
Vosk nur punktuell aufgerufen (Lautstaerke-Frage in der Start-Ansage).

FUENF ENTSCHEIDUNGEN, DIE HIER DRINSTECKEN
==========================================

1. EINGESCHRAENKTE GRAMMATIK STATT FREIER ERKENNUNG.
   Vosk bekommt nur die drei Befehlssaetze und "[unk]" zur Auswahl. Das
   ist keine Optimierung, sondern Voraussetzung: Im Test am 2026-08-16
   (Piper spricht den Satz, Vosk hoert zu) erkannte das freie deutsche
   Modell das Wort "gnome" zuverlaessig als **"genug"**. Mit der
   Grammatik lagen alle drei Saetze auf Anhieb woertlich richtig. Nebenbei kostet die
   kleine Grammatik deutlich weniger Rechenzeit - bei einem Dienst, der
   dauerhaft laeuft, zaehlt das fuer die Akkulaufzeit.

2. EINGEBAUTES MIKROFON STATT BLUETOOTH - anders als bei der
   Lautstaerke-Frage, und mit Absicht. Das Referenz-Headset (AIRHUG 01)
   kann A2DP und HFP nicht gleichzeitig: Sobald sein Mikrofon benutzt
   wird, faellt die Wiedergabe auf Telefonqualitaet. Bei einer einmaligen
   Frage ist das ein kurzer Moment; bei dauerhaftem Zuhoeren waere die
   Musik- und Sprachausgabe **fuer immer** verschlechtert. Deshalb hoert
   dieser Dienst ueber das eingebaute Mikrofon. Drei feste Saetze zu
   unterscheiden gelingt auch damit - genau das ist der Vorteil einer
   winzigen Grammatik.

3. WAEHREND DAS SYSTEM SPRICHT, WIRD NICHT ZUGEHOERT.
   Sonst hoert sich der Dienst selbst - und weil seine eigene Ansage
   sowohl das Ziel als auch das Wort "umschalten" enthalten kann, wuerde
   die Satz-Bedingung aus dem Kopf dieser Datei sie gerade NICHT
   abfangen. Endlosschleife. Ausgewertet wird die
   Markierungsdatei, die dialos-say.py ohnehin schon setzt.

4. KEINE RUECKFRAGE, ABER EINE ANSAGE.
   Ein "Willst du wirklich?" bei jedem Wort waere laestig. Stattdessen
   sagt der Dienst nach dem Umschalten, was er getan hat - wer es nicht
   wollte, sagt einfach das andere Wort. Damit ist ein Fehlgriff in zwei
   Sekunden ruecknehmbar, ohne dass jemand sehen muss, was passiert ist.
   Steht die Optik schon so, wird nur das gesagt und nichts geaendert.

5. SPERRFRIST NACH JEDEM UMSCHALTEN.
   Ohne die wuerde ein einzelnes langgezogenes "Windows" mehrfach
   ausgeloest, und die Ansage des Umschaltens koennte trotz Punkt 3 in
   einer Randlage noch einmal greifen.

Aufruf: laeuft ueber /etc/xdg/autostart/dialos-sprachbefehl-desktop.desktop
automatisch in jeder Sitzung. Von Hand zum Testen einfach starten;
beenden mit Strg+C.
"""

import json
import os
import subprocess
import sys
import time

MODELL = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
UMSCHALT_SKRIPT = "/usr/local/bin/dialos-desktop-stil.sh"
SAY = "/usr/local/bin/dialos-say.py"
STIL_DATEI = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "dialos", "desktop-stil",
)

# Nur diese Saetze stehen zur Auswahl. "[unk]" ist Vosks Auffangeintrag
# fuer alles andere - ohne ihn presst das Modell jedes Geraeusch in einen
# der Saetze und schaltet staendig um.
GRAMMATIK = json.dumps([
    "auf linux umschalten",
    "auf gnome umschalten",
    "auf windows umschalten",
    "[unk]",
])

# Erkannt wird nur, was BEIDES enthaelt: ein Ziel und das Wort
# "umschalten". Siehe Kopf der Datei - ohne die zweite Bedingung reicht
# ein beilaeufiges "windows" im Gespraech.
AUSLOESER = "umschalten"
ZIELE = {"linux": "gnome", "gnome": "gnome", "windows": "windows"}

SPERRFRIST_S = 5.0          # nach einem Umschalten so lange nicht zuhoeren
WARTEN_BEIM_SPRECHEN_S = 0.3


def markierungsdatei():
    """Gleiche Logik wie in dialos-say.py - pro Konto privat."""
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, "dialos-sprachausgabe-aktiv")
    return f"/tmp/dialos-sprachausgabe-aktiv-{os.getuid()}"


MARKIERUNG = markierungsdatei()


def spricht_gerade():
    return os.path.exists(MARKIERUNG)


def sprich(text):
    if os.access(SAY, os.X_OK):
        subprocess.run([SAY, text], capture_output=True, timeout=60)
    else:
        print(text)


def waehle_mikrofon():
    """Eingebautes Mikrofon bevorzugt - Begruendung siehe Punkt 2 oben.

    Ist keines da (Geraet ohne eingebautes Mikrofon), wird als letzter
    Ausweg doch eine Bluetooth-Quelle genommen: schlechtere Wiedergabe
    ist immer noch besser als ein Geraet, das gar nicht zuhoert.
    """
    try:
        roh = subprocess.run(
            ["pactl", "-f", "json", "list", "sources"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        quellen = json.loads(roh) if roh.strip() else []
    except Exception:
        return None
    namen = [q.get("name", "") for q in quellen
             if q.get("name") and not q["name"].endswith(".monitor")]
    eingebaut = [n for n in namen if not n.startswith("bluez_input.")]
    if eingebaut:
        return eingebaut[0]
    return namen[0] if namen else None


def aktueller_stil():
    try:
        with open(STIL_DATEI) as f:
            return f.read().strip()
    except OSError:
        return "gnome"


def umschalten(ziel):
    if aktueller_stil() == ziel:
        sprich("Der Schreibtisch steht schon auf Linux."
               if ziel == "gnome"
               else "Der Schreibtisch steht schon auf Windows.")
        return
    if not os.access(UMSCHALT_SKRIPT, os.X_OK):
        sprich("Ich kann die Umschaltung nicht finden.")
        return
    # Das Umschalt-Skript sagt selbst an, was es getan hat - deshalb hier
    # keine zweite Ansage.
    subprocess.run([UMSCHALT_SKRIPT, ziel], capture_output=True, timeout=120)


def aufnahme_starten(quelle):
    befehl = ["parec", f"--rate={ABTASTRATE}", "--channels=1", "--format=s16le"]
    if quelle:
        befehl.append(f"--device={quelle}")
    return subprocess.Popen(befehl, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)


def main():
    try:
        import vosk
    except ImportError:
        print("Vosk ist nicht installiert - Sprachbefehle sind aus.", file=sys.stderr)
        return 1
    if not os.path.isdir(MODELL):
        print(f"Sprachmodell fehlt: {MODELL}", file=sys.stderr)
        return 1

    vosk.SetLogLevel(-1)
    modell = vosk.Model(MODELL)
    quelle = waehle_mikrofon()
    if not quelle:
        print("Kein Mikrofon gefunden.", file=sys.stderr)
        return 1

    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK)
    prozess = aufnahme_starten(quelle)
    letzte_aktion = 0.0

    try:
        while True:
            if spricht_gerade():
                # Aufnahme laeuft weiter, wird aber verworfen: Wuerde sie
                # angehalten, muesste parec staendig neu starten, was
                # jedes Mal ein paar hundert Millisekunden kostet.
                prozess.stdout.read(4000)
                erkenner.Reset()
                time.sleep(WARTEN_BEIM_SPRECHEN_S)
                continue

            if time.time() - letzte_aktion < SPERRFRIST_S:
                prozess.stdout.read(4000)
                erkenner.Reset()
                continue

            block = prozess.stdout.read(4000)
            if not block:
                # parec beendet (z. B. Audiogeraet gewechselt) - neu
                # aufsetzen statt den Dienst sterben zu lassen.
                time.sleep(1)
                quelle = waehle_mikrofon()
                prozess = aufnahme_starten(quelle)
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK)
                continue

            if not erkenner.AcceptWaveform(block):
                continue
            text = json.loads(erkenner.Result()).get("text", "")
            if not text:
                continue
            worte = text.split()
            if AUSLOESER not in worte:
                continue
            for wort in worte:
                ziel = ZIELE.get(wort)
                if ziel:
                    umschalten(ziel)
                    letzte_aktion = time.time()
                    erkenner.Reset()
                    break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            prozess.terminate()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
