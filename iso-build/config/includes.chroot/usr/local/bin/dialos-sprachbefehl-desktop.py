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

3. WAEHREND DAS SYSTEM SPRICHT, WIRD NICHT ZUGEHOERT - UND DANACH WIRD
   DIE AUFNAHME NEU BEGONNEN.
   Der erste Teil war von Anfang an da (Markierungsdatei, die
   dialos-say.py ohnehin setzt). Der zweite Teil fehlte, und genau daran
   ist der Dienst am 2026-08-17 gescheitert: Er schaltete auf Windows um,
   und 15 Sekunden spaeter von selbst wieder zurueck.

   Der Grund ist Arithmetik, nicht Logik. parec erzeugt bei 16 kHz mono
   16 Bit rund 32.000 Bytes pro Sekunde. Der Dienst verwarf waehrend des
   Sprechens 4.000 Bytes und schlief dann 0,3 Sekunden - also nur rund
   13.000 Bytes pro Sekunde. Er leerte die Warteschlange also LANGSAMER
   als parec sie fuellte. Nach einer acht Sekunden langen Ansage standen
   rund fuenf Sekunden Ansage-Ton in der Pipe, die er anschliessend ganz
   normal auswertete - und weil die eingeschraenkte Grammatik alles auf
   einen der drei Saetze zwingt, wurde daraus ein Befehl.

   Die Markierung allein reicht also nicht: Sie verhindert das Zuhoeren,
   nicht das Aufzeichnen. Deshalb wird die Aufnahme nach jedem Sprechen
   komplett neu begonnen - ein frischer parec-Prozess hat keinen
   Rueckstand. Das kostet ein paar hundert Millisekunden und ist der
   einzige Weg, bei dem nichts von der eigenen Stimme uebrig bleiben
   kann.

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
PEGEL_SKRIPT = "/usr/local/sbin/dialos-mikrofon-pegel.sh"
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
NACHHALL_WARTEN_S = 0.7     # Pause nach dem Sprechen, bevor neu aufgenommen wird
SAETTIGUNG_GRENZE = 15      # so viele uebersteuerte Bloecke in Folge = Pegel richten
PEGEL_ABSTAND_S = 60.0      # hoechstens einmal pro Minute nachregeln

# Mit "--debug" gestartet zeigt der Dienst jeden erkannten Satz und den
# Aussteuerungspegel an. Das ist kein Entwickler-Spielzeug, sondern die
# Lehre aus dem 2026-08-16: Der Dienst schwieg, und ohne Pegelanzeige war
# nicht zu unterscheiden, ob er nicht zuhoert, nichts versteht oder das
# Mikrofon uebersteuert ist (es war Letzteres).
DEBUG = "--debug" in sys.argv


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


ECHO_QUELLE = "dialos_mikrofon_ohne_echo"


def waehle_mikrofon():
    """Reihenfolge: Echo-bereinigte Quelle, sonst eingebaut, zuletzt Bluetooth.

    ERSTE WAHL ist seit 2026-08-17 die Quelle ohne Echo (PipeWire-Modul
    module-echo-cancel, eingerichtet in
    /etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf). Sie
    rechnet das Lautsprechersignal aus dem Mikrofon heraus. Ohne sie hoert
    der Dienst alles mit, was das Geraet abspielt - die eigene Ansage
    ebenso wie Radio oder Mediathek - und die eingeschraenkte Grammatik
    presst Bruchstuecke davon in einen Befehl. Gemessen am selben Tag:
    waehrend der Lautsprecher sprach, 6,13 % Pegel am rohen Mikrofon
    gegenueber 0,15 % an der bereinigten Quelle, also rund 32 dB weniger.

    ZWEITE WAHL das eingebaute Mikrofon - Begruendung siehe Punkt 2 oben.

    LETZTE WAHL eine Bluetooth-Quelle: schlechtere Wiedergabe ist immer
    noch besser als ein Geraet, das gar nicht zuhoert.
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
    if ECHO_QUELLE in namen:
        return ECHO_QUELLE
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


def pegel_richten():
    """Setzt die Aufnahme-Verstaerkung zurueck, falls sie uebersteuert.

    Warum das hier steht und nicht nur im Systemdienst (gefunden
    2026-08-17): dialos-mikrofon-pegel.service laeuft beim Booten, also
    VOR der Benutzeranmeldung. WirePlumber stellt seine gespeicherten
    Geraete-Einstellungen aber erst in der Sitzung wieder her - und
    hebt "Internal Mic Boost" dabei zurueck auf +30 dB. Der Systemdienst
    ist damit strukturell zu frueh dran.

    Deshalb richtet der Dienst, der das Mikrofon tatsaechlich benutzt,
    den Pegel selbst - direkt nachdem die Aufnahme geoeffnet ist, also
    nach WirePlumbers Zugriff. Das Skript braucht keine Root-Rechte:
    amixer darf jedes Konto der Gruppe "audio" bedienen.
    """
    if not os.access(PEGEL_SKRIPT, os.X_OK):
        return
    try:
        subprocess.run([PEGEL_SKRIPT], capture_output=True, timeout=15)
    except Exception:
        pass


def aufnahme_starten(quelle):
    befehl = ["parec", f"--rate={ABTASTRATE}", "--channels=1", "--format=s16le"]
    if quelle:
        befehl.append(f"--device={quelle}")
    p = subprocess.Popen(befehl, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    # Erst nach dem Oeffnen des Datenstroms - vorher greift WirePlumber
    # noch einmal auf die Regler zu.
    time.sleep(0.3)
    pegel_richten()
    return p


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
    aufnahme_verwerfen = False
    saettigungen = 0
    letzte_pegelkorrektur = 0.0

    try:
        while True:
            # Es gibt zwei Gruende, gerade NICHT zuzuhoeren: Das System
            # spricht selbst, oder das letzte Umschalten liegt noch keine
            # Sperrfrist zurueck. Beide werden gleich behandelt, weil in
            # beiden Faellen dasselbe passieren muss - siehe unten.
            if spricht_gerade() or time.time() - letzte_aktion < SPERRFRIST_S:
                aufnahme_verwerfen = True
                time.sleep(WARTEN_BEIM_SPRECHEN_S)
                continue

            if aufnahme_verwerfen:
                # Waehrend der Pause hat parec weiter aufgezeichnet - unter
                # anderem die eigene Ansage. Diese Aufzeichnung steht jetzt
                # in der Warteschlange und wuerde als Naechstes ganz normal
                # ausgewertet. Genau daran ist der Dienst am 2026-08-17
                # gescheitert: Er schaltete auf Windows um und 15 Sekunden
                # spaeter von selbst zurueck.
                #
                # Die Markierungsdatei verhindert das Zuhoeren, nicht das
                # Aufzeichnen. Deshalb wird die Aufnahme hier komplett
                # verworfen und neu begonnen - ein frischer parec-Prozess
                # hat keinen Rueckstand.
                aufnahme_verwerfen = False
                try:
                    prozess.terminate()
                    prozess.stdout.close()
                except Exception:
                    pass
                # Kurz warten, damit auch der Nachhall der Ansage im Raum
                # nicht mehr in die neue Aufnahme faellt.
                time.sleep(NACHHALL_WARTEN_S)
                prozess = aufnahme_starten(quelle)
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK)
                if DEBUG:
                    print("\n  (Aufnahme nach Sprechpause neu begonnen)")
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

            pegel = max(abs(int.from_bytes(block[i:i + 2], "little", signed=True))
                        for i in range(0, len(block) - 1, 2))
            gesaettigt = pegel >= 32000
            if DEBUG:
                print(f"\rPegel {100 * pegel / 32768:5.1f} %"
                      f"{'  UEBERSTEUERT' if gesaettigt else '            '}",
                      end="", flush=True)

            # Selbstheilung: Uebersteuert die Aufnahme laenger, ist die
            # Erkennung wertlos - Vosk braucht die Pausen zwischen den
            # Woertern, und die gibt es im Dauervollausschlag nicht.
            # Statt still nichts zu verstehen, wird der Pegel neu
            # gerichtet. Hoechstens einmal pro Minute, damit ein
            # tatsaechlich lautes Umfeld keine Dauerschleife ausloest.
            if gesaettigt:
                saettigungen += 1
                if (saettigungen >= SAETTIGUNG_GRENZE
                        and time.time() - letzte_pegelkorrektur > PEGEL_ABSTAND_S):
                    if DEBUG:
                        print("\n  (uebersteuert - Pegel wird neu gerichtet)")
                    pegel_richten()
                    letzte_pegelkorrektur = time.time()
                    saettigungen = 0
            else:
                saettigungen = 0

            if not erkenner.AcceptWaveform(block):
                continue
            text = json.loads(erkenner.Result()).get("text", "")
            if DEBUG and text:
                print(f"\n  erkannt: {text!r}")
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
