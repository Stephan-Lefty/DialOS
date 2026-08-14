#!/usr/bin/env python3
"""DialOS: Technischer Test fuer Vosk-Spracherkennung (Schritt 1 der
Sprachsteuerung, siehe docs/sprachsteuerung.md - Entscheidung: "Erst Vosk
technisch zum Laufen bringen", bevor WLAN/Lautstaerke/Programme an echte
Spracherkennung statt Tastatur-Platzhalter angeschlossen werden).

Zweck: rein technische Verifikation - Mikrofon waehlen, Audio erfassen,
mit Vosk transkribieren, Ergebnis im Terminal anzeigen. NOCH KEINE
Anbindung an Intent-Erkennung oder TTS-Rueckmeldung - das kommt erst,
wenn die Erkennungsqualitaet hier als ausreichend bewertet wurde.

Aufnahme-Modus: Erst vollstaendig aufnehmen (feste Dauer, siehe
AUFNAHME_SEKUNDEN_STANDARD bzw. 2. Kommandozeilen-Argument), DANACH erst
in einem Rutsch erkennen - bewusst NICHT als durchgehendes Live-Streaming
(erster Versuch mit dem grossen Modell zeigte, dass der Erkenner mit
Echtzeit-Streaming beim grossen Modell auf Laptop-Hardware nicht mithaelt
- passt auch zur offiziellen Beschreibung von vosk-model-de-0.21 als
"fuer Telefonie und Server", nicht fuer Echtzeit auf einem Laptop. Beim
Aufnehmen-dann-Erkennen-Ansatz gibt es keinen Zeitdruck mehr - das
Ergebnis darf ein paar Sekunden dauern, das ist bei einem
Sprachassistenten eine akzeptable kurze Pause. Dieser Ansatz passt auch
zur geplanten Zwei-Stufen-Architektur (siehe docs/sprachsteuerung.md):
Aktivierung/Sprachaktivitaet erkennen, dann Aufnahme, dann Erkennung mit
dem grossen Modell.

Mikrofon-Wahl / Zielarchitektur (Stand nach Bluetooth-Vergleichstest):
Gemessene Daten zeigen, dass das AIRHUG-Bluetooth-Geraet dem eingebauten
Laptop-Mikrofon klar ueberlegen ist (siehe Chat-Verlauf: 6 von 8
Testsaetzen exakt korrekt bei normalem Sprechabstand/-lautstaerke ueber
Bluetooth, gegenueber deutlich schwaecheren und nur mit lautem/nahem
Sprechen brauchbaren Ergebnissen beim eingebauten Mikrofon). Zielbild
laut Entscheidung: DialOS wird IMMER mit einem mobilen Bluetooth-
Lautsprecher/Mikrofon (wie AIRHUG) installiert und nutzt dieses als
primaeren Ein-/Ausgabeweg; das eingebaute Laptop-Mikrofon/die
Lautsprecher sind nur Fallback (leerer Akku / kein Bluetooth-Geraet
verbunden). Diese Fallback-Logik ist NOCH NICHT implementiert, siehe
unten - dieses Skript deckt bisher nur den technischen Bluetooth-
Anteil ab, per --bluetooth-erlauben.

Bluetooth-Profilwechsel: AIRHUG wird auch ausserhalb von DialOS fuer
Musik/Medien genutzt, deshalb kommt ein dauerhaftes Verbleiben im
Headset-Profil (niedrigere Wiedergabequalitaet) nicht in Frage. Laut
`pactl -f json list cards` bietet die Bluetooth-Karte u.a. folgende
Profile:
  - a2dp-sink / a2dp-sink-sbc_xq: nur Wiedergabe (sources: 0), aber
    Hi-Fi-Qualitaet - das ist das fuer Musik/Medien gewuenschte Profil
    und daher auch der Normalzustand ausserhalb von DialOS-Interaktionen.
  - headset-head-unit / headset-head-unit-cvsd: Wiedergabe UND Aufnahme
    GLEICHZEITIG (sinks: 1, sources: 1), aber Telefonie-Audioqualitaet
    bei der Wiedergabe. headset-head-unit (mSBC, breitbandig) wird
    gegenueber -cvsd (schmalbandig) bevorzugt versucht.
  Deshalb schaltet dieses Skript bei --bluetooth-erlauben aktiv auf
  headset-head-unit um, BEVOR es die erste Aufnahme startet (nicht nur
  passiv verlassen auf automatisches Umschalten durch die PipeWire-
  Richtlinie - das passiert zwar auch von selbst, sobald eine App vom
  bluez_input.*-Geraet aufnehmen will, aber ohne definierten Zeitpunkt/
  definierte Wartezeit davor, was zu denselben Satzanfang-Aussetzern
  fuehren koennte wie beim urspruenglichen Pipeline-Warmup-Problem).
  Beim Beenden des Skripts (Strg+C) wird aktiv zurueck auf a2dp-sink
  geschaltet, damit AIRHUG danach wieder in Hi-Fi-Qualitaet fuer Musik/
  Medien bereitsteht. WICHTIG: Das ist nur fuer diesen technischen
  Testaufbau so grob (ein Umschalten pro Skript-Lauf) - in der
  spaeteren echten Sprachsteuerung muesste das pro Interaktion
  (Zuhoeren+Antworten) passieren, nicht nur einmal beim Programmstart/
  -ende. Das ist ein bewusst vertagtes TODO fuer die Integration mit
  Intent-Erkennung/TTS, siehe Docstring oben.

Der Bluetooth-Lautsprecher (AIRHUG) wird beim automatischen
Mikrofon-Vorschlag OHNE --bluetooth-erlauben weiterhin bewusst
ausgeschlossen (siehe waehle_mikrofon()) - das Flag ist aktuell noch
ein expliziter Opt-in fuer Tests, bis die Fallback-Logik fuers
Zielbild (Bluetooth immer bevorzugt, eingebaut nur als Fallback)
existiert.

Test ergab: auf dem aktuellen Test-Laptop existiert (Stand jetzt) gar
kein echtes externes Kabelgebunden-/USB-Mikrofon als Audioquelle
(siehe `pactl list short sources`) - nur eingebautes Mikrofon und
Bluetooth-Mikrofon vorhanden.

Voraussetzungen (siehe Installationsblock im Chat):
- `pip install vosk --break-system-packages`
- Deutsches Vosk-Modell heruntergeladen und entpackt nach MODELL_PFAD.
- `parec` (Teil von pipewire-pulse/pulseaudio-utils) verfuegbar - wird
  zur Audioaufnahme genutzt statt einer Python-Audio-Bibliothek wie
  sounddevice/pyaudio, konsistent damit, dass der Rest von DialOS schon
  durchgehend pactl/parec fuer Audio nutzt (kein zusaetzliches
  PortAudio-Paket noetig).
"""
import json
import subprocess
import sys
import time

MODELL_PFAD_STANDARD = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
AUFNAHME_SEKUNDEN_STANDARD = 5
AUFWAERM_SEKUNDEN = 0.4
BLUETOOTH_PROFIL_WARTEZEIT_SEKUNDEN = 1.5

BLUETOOTH_ERLAUBEN_FLAG = "--bluetooth-erlauben"


def waehle_mikrofon(bluetooth_erlauben=False):
    try:
        out = subprocess.run(
            ["pactl", "-f", "json", "list", "sources"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        quellen = json.loads(out) if out.strip() else []
    except Exception:
        return None
    kandidaten = []
    bluetooth_kandidaten = []
    for quelle in quellen:
        name = quelle.get("name", "")
        if not name or name.endswith(".monitor"):
            continue
        if name.startswith("bluez_input."):
            bluetooth_kandidaten.append(name)
            continue
        kandidaten.append(name)
    if bluetooth_erlauben and bluetooth_kandidaten:
        return bluetooth_kandidaten[0]
    if not kandidaten:
        return None
    extern = [n for n in kandidaten if not n.startswith("alsa_input.pci-")]
    if extern:
        return extern[0]
    eingebaut = [n for n in kandidaten if n.startswith("alsa_input.pci-")]
    return eingebaut[0] if eingebaut else kandidaten[0]


def bluetooth_karte_fuer_quelle(quelle_name):
    praefix = "bluez_input."
    if not quelle_name.startswith(praefix):
        return None
    mac = quelle_name[len(praefix):]
    return "bluez_card." + mac.replace(":", "_")


def bluetooth_profil_setzen(karten_name, profil):
    ergebnis = subprocess.run(
        ["pactl", "set-card-profile", karten_name, profil],
        capture_output=True, text=True,
    )
    return ergebnis.returncode == 0


def main():
    try:
        import vosk
    except ImportError:
        print(
            "Das Python-Paket 'vosk' ist nicht installiert. "
            "Bitte zuerst: pip install vosk --break-system-packages",
            file=sys.stderr,
        )
        sys.exit(1)

    argv = sys.argv[1:]
    bluetooth_erlauben = BLUETOOTH_ERLAUBEN_FLAG in argv
    argv = [a for a in argv if a != BLUETOOTH_ERLAUBEN_FLAG]

    modell_pfad = argv[0] if len(argv) > 0 else MODELL_PFAD_STANDARD
    aufnahme_sekunden = float(argv[1]) if len(argv) > 1 else AUFNAHME_SEKUNDEN_STANDARD

    vosk.SetLogLevel(-1)

    quelle = waehle_mikrofon(bluetooth_erlauben=bluetooth_erlauben)

    bluetooth_karte = None
    bluetooth_profil_umgeschaltet = False
    if quelle and quelle.startswith("bluez_input."):
        bluetooth_karte = bluetooth_karte_fuer_quelle(quelle)
        if bluetooth_karte:
            print(f"Schalte Bluetooth-Karte {bluetooth_karte} auf headset-head-unit um "
                  "(fuer gleichzeitige Aufnahme+Wiedergabe) ...")
            if bluetooth_profil_setzen(bluetooth_karte, "headset-head-unit"):
                bluetooth_profil_umgeschaltet = True
            elif bluetooth_profil_setzen(bluetooth_karte, "headset-head-unit-cvsd"):
                bluetooth_profil_umgeschaltet = True
                print("(mSBC-Profil 'headset-head-unit' nicht verfuegbar, "
                      "CVSD-Fallback 'headset-head-unit-cvsd' verwendet.)")
            else:
                print(
                    "Achtung: Bluetooth-Profilwechsel fehlgeschlagen - "
                    "Aufnahme ist damit evtl. nicht moeglich.",
                    file=sys.stderr,
                )
            if bluetooth_profil_umgeschaltet:
                print(
                    f"Warte {BLUETOOTH_PROFIL_WARTEZEIT_SEKUNDEN:.1f}s, bis der "
                    "Bluetooth-Profilwechsel sich stabilisiert hat ..."
                )
                time.sleep(BLUETOOTH_PROFIL_WARTEZEIT_SEKUNDEN)

    if quelle:
        print(f"Verwende Mikrofon: {quelle}")
        subprocess.run(["pactl", "set-default-source", quelle], capture_output=True)
    else:
        print("Kein passendes Mikrofon gefunden - verwende PipeWire-Standardquelle.")

    print(f"Lade Vosk-Modell aus {modell_pfad} ...")
    try:
        modell = vosk.Model(modell_pfad)
    except Exception as fehler:
        print(f"Modell konnte nicht geladen werden: {fehler}", file=sys.stderr)
        if bluetooth_profil_umgeschaltet and bluetooth_karte:
            bluetooth_profil_setzen(bluetooth_karte, "a2dp-sink")
        sys.exit(1)
    print(
        f"Bereit. Jede Aufnahme dauert {aufnahme_sekunden:.0f} Sekunden - "
        "nach [Enter] bitte sofort sprechen. Strg+C zum Beenden.\n"
    )

    while True:
        try:
            input("[Enter] fuer naechste Aufnahme... ")
        except (KeyboardInterrupt, EOFError):
            break

        erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE)

        prozess = subprocess.Popen(
            ["parec", f"--rate={ABTASTRATE}", "--channels=1", "--format=s16le"],
            stdout=subprocess.PIPE,
        )
        time.sleep(AUFWAERM_SEKUNDEN)
        try:
            import os
            os.set_blocking(prozess.stdout.fileno(), False)
            try:
                prozess.stdout.read(1_000_000)
            except Exception:
                pass
            os.set_blocking(prozess.stdout.fileno(), True)
        except Exception:
            pass

        print(f"Aufnahme laeuft ({aufnahme_sekunden:.0f}s) - jetzt sprechen ...")
        audiodaten = bytearray()
        ende = time.time() + aufnahme_sekunden
        try:
            while time.time() < ende:
                chunk = prozess.stdout.read(4000)
                if not chunk:
                    break
                audiodaten.extend(chunk)
        finally:
            prozess.terminate()
            prozess.stdout.close()

        print("Aufnahme beendet, erkenne Sprache (kann beim grossen Modell ein paar Sekunden dauern) ...")
        erkenner.AcceptWaveform(bytes(audiodaten))
        ergebnis = json.loads(erkenner.FinalResult())
        text = ergebnis.get("text", "")
        print(f"Erkannt: {text}\n" if text else "Erkannt: (nichts verstanden)\n")

    if bluetooth_profil_umgeschaltet and bluetooth_karte:
        print(f"Schalte Bluetooth-Karte {bluetooth_karte} zurueck auf a2dp-sink "
              "(Hi-Fi-Wiedergabe fuer Musik/Medien) ...")
        if not bluetooth_profil_setzen(bluetooth_karte, "a2dp-sink"):
            print(
                "Achtung: Rueckschalten auf a2dp-sink fehlgeschlagen - "
                "bitte manuell in den Audioeinstellungen pruefen.",
                file=sys.stderr,
            )

    print("Beendet.")


if __name__ == "__main__":
    main()
