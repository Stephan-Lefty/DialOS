#!/usr/bin/env python3
"""DialOS-Suche: Briefe, Dokumente, Notizen und Mails per Sprache finden.

Die erste Erweiterung von DialOS. Entwurf der Schnittstelle in
docs/erweiterungen.md, Programmwahl in docs/anwendungen.md.

STAND 2026-09-17: DIESER SCHRITT SUCHT NOCH NICHT. Er nimmt den Suchbegriff
entgegen, wiederholt ihn und gibt das Mikrofon zurueck. Das ist Absicht und
kein halber Bau: Der Index gibt es noch nicht. Kaeme beides zugleich, waere bei
einem Fehlschlag nicht zu sagen, ob die Schnittstelle oder die Suche schuld
ist. Was hier laeuft, ist genau das, worauf alles Weitere aufbaut: Startsatz,
Mikrofon-Uebergabe, freie Erkennung des Begriffs, saubere Rueckgabe.

WAS DAHINTER KOMMT (Entscheidung vom 2026-09-17, Begruendung in
docs/anwendungen.md): ein EIGENER schlanker SQLite-FTS5-Index ueber die
Dateien, die ohnehin schon da liegen - Briefe, PDFs, Notizen, mbox. Von
MailBurg wird nur die Extraktionskette geteilt (PDF, OCR, Office), nicht das
Programm: MailBurg archiviert, DialOS-Suche muss nur finden.

DER SUCHBEGRIFF IST TEXT, KEIN BEFEHL - deshalb Parakeet und nicht Vosk.
Dieselbe Arbeitsteilung wie beim Diktat (gemessen am 2026-09-15: 2,8 % gegen
12,7 % Wortfehler). "Krankenkasse" kann in keiner geschlossenen Grammatik
stehen; sonst muesste jedes suchbare Wort darin stehen.

DIE MIKROFON-MARKE IST DIESELBE DATEI WIE BEIM DIKTAT, und das ist kein
Zufallsfund, sondern die vorhandene Loesung: Der Befehlsdienst prueft in jeder
Schleifenrunde, ob sie da ist, und verwirft dann alles Gehoerte.
dialos-notiz.py nennt sie fuer Rueckfragen FREMDE_AUFNAHME_MARKE - derselbe
Pfad. Der Name "dialos-diktat-aktiv" ist damit historisch, die Bedeutung ist
"jemand anders hoert gerade zu".

NEU GEGENUEBER DEM DIKTAT: Die Marke bekommt die PID hineingeschrieben. Die
bestehenden Pruefungen sehen nur, OB die Datei da ist, und stoeren sich nicht
daran - aber eine Wache kann damit eine verwaiste Marke erkennen. Stuerzt eine
Erweiterung ab, bliebe das Mikrofon sonst fuer immer belegt, und der Nutzer
spraeche gegen ein taubes Geraet, ohne einen Weg zurueck.

Aufruf:  dialos-suche.py            (startet der Befehlsdienst)
         dialos-suche.py --pruefen  (nur Selbsttest, ohne Mikrofon)
"""

import os
import signal
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
ABTASTRATE = 16000
BLOCK = 4000
ECHO_QUELLE = "dialos_mikrofon_ohne_echo"

MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
PARAKEET_MODELL = ("/usr/local/share/dialos-parakeet/"
                   "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
PARAKEET_AUS = os.path.join(os.path.expanduser("~"), ".config", "dialos",
                            "parakeet-aus")

# Wie lange auf den Suchbegriff gewartet wird, und wann er als zu Ende gilt.
# Beides bewusst grosszuegiger als beim Diktat: Wer sucht, ueberlegt erst.
ZEITGRENZE_S = 20.0
RUHE_ENDE_S = 1.2
PEGEL_SCHWELLE = 150.0

ANSAGE_START = "Wonach soll ich suchen?"
ANSAGE_NICHTS = "Ich habe nichts verstanden. Die Suche ist beendet."
ANSAGE_NOCH_NICHT = ("Das Archiv ist noch nicht eingerichtet. "
                     "Ich konnte deshalb nicht nachsehen.")

PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-suche.log")


def melde(text):
    zeile = f"{time.strftime('%m-%d %H:%M:%S')}  {text}"
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass
    if "--debug" in sys.argv:
        print(zeile)


def marke_pfad(name):
    """Derselbe Weg wie in dialos-diktat.py - abgeschrieben waere er hier
    richtig, aber er muss uebereinstimmen, sonst greift die Uebergabe nicht."""
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


MARKE = marke_pfad("dialos-diktat-aktiv")


def sprich(text, frage=False):
    befehl = [SAY] + (["--frage"] if frage else []) + [text]
    try:
        subprocess.run(befehl, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        print(text)


def mikrofon_oeffnen():
    return subprocess.Popen(
        ["parec", "-d", ECHO_QUELLE, "--format=s16le",
         f"--rate={ABTASTRATE}", "--channels=1", "--latency-msec=30"],
        stdout=subprocess.PIPE)


def pegel(block):
    import array
    if len(block) < 2:
        return 0.0
    werte = array.array("h", block[:len(block) - len(block) % 2])
    return (sum(x * x for x in werte) / len(werte)) ** 0.5 if werte else 0.0


def parakeet_laden():
    """Parakeet, wenn er eingerichtet und nicht abgeschaltet ist - sonst None.

    Kein Abbruch, wenn er fehlt: Der Nutzer soll hoeren, was schiefging, und
    nicht vor einem Geraet stehen, das schweigt.
    """
    if os.path.exists(PARAKEET_AUS):
        melde("  Parakeet ist abgeschaltet")
        return None
    if not os.path.isfile(os.path.join(PARAKEET_MODELL, "tokens.txt")):
        melde(f"  Parakeet nicht eingerichtet ({PARAKEET_MODELL})")
        return None
    try:
        import sherpa_onnx
        t0 = time.time()
        m = PARAKEET_MODELL
        erkenner = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=f"{m}/encoder.int8.onnx", decoder=f"{m}/decoder.int8.onnx",
            joiner=f"{m}/joiner.int8.onnx", tokens=f"{m}/tokens.txt",
            num_threads=4, model_type="nemo_transducer")
        melde(f"  Parakeet geladen in {time.time() - t0:.1f} s")
        return erkenner
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"  Parakeet liess sich nicht laden: {fehler}")
        return None


def erkennen(erkenner, roh):
    import array
    if len(roh) < ABTASTRATE // 5:
        return ""
    werte = array.array("h", bytes(roh[:len(roh) - len(roh) % 2]))
    strom = erkenner.create_stream()
    strom.accept_waveform(ABTASTRATE, [x / 32768.0 for x in werte])
    erkenner.decode_stream(strom)
    return strom.result.text.strip()


def begriff_hoeren(erkenner):
    """Ansage stellen und den Suchbegriff aufnehmen.

    DAS MIKROFON IST WAEHREND DER ANSAGE SCHON OFFEN - dieselbe Reihenfolge
    wie bei den Rueckfragen in dialos-notiz.py, und aus demselben Grund: Am
    2026-08-19 fiel Stephans "ja" in genau die Luecke zwischen Frage und
    Aufnahmebeginn. Erst bereit sein, dann fragen.
    """
    prozess = mikrofon_oeffnen()
    try:
        sprich(ANSAGE_START, frage=True)
        roh = bytearray()
        ruhe = 0.0
        gesprochen = False
        ende = time.time() + ZEITGRENZE_S
        block_s = BLOCK / 2 / ABTASTRATE
        while time.time() < ende:
            block = prozess.stdout.read(BLOCK)
            if not block:
                break
            roh += block
            if pegel(block) >= PEGEL_SCHWELLE:
                gesprochen, ruhe = True, 0.0
            elif gesprochen:
                ruhe += block_s
                if ruhe >= RUHE_ENDE_S:
                    break
        melde(f"  {len(roh) / 2 / ABTASTRATE:.1f} s aufgenommen, "
              f"gesprochen={gesprochen}")
        if not gesprochen:
            return ""
        return erkennen(erkenner, roh) if erkenner else ""
    finally:
        try:
            prozess.terminate()
        except OSError:
            pass


def suchen(begriff):
    """Hier kommt der Index hinein - noch nicht gebaut.

    Vorgesehen: ein eigener SQLite-FTS5-Index ueber die vorhandenen Dateien,
    mit einer Koelner-Phonetik-Spalte gegen Erkennungsunschaerfe. Danach der
    Trefferdialog: 40 Treffer kann man nicht vorlesen; erst eingrenzen, Anzahl
    ansagen, Weg nennen.
    """
    melde(f"  Suche nach {begriff!r} - Motor fehlt noch")
    sprich(f"Du suchst nach {begriff}. " + ANSAGE_NOCH_NICHT)
    return 0


def selbsttest():
    """Was sich ohne Mikrofon pruefen laesst - fuer das Aufspielen."""
    fehlt = []
    if not os.access(SAY, os.X_OK):
        fehlt.append(SAY)
    if not os.path.isdir(MODELL_KLEIN):
        fehlt.append(MODELL_KLEIN)
    if not os.path.isfile(os.path.join(PARAKEET_MODELL, "tokens.txt")):
        fehlt.append(PARAKEET_MODELL + " (Suchbegriff bliebe unerkannt)")
    print(f"Marke:     {MARKE}")
    print(f"Protokoll: {PROTOKOLL}")
    for f in fehlt:
        print(f"FEHLT:     {f}")
    return 1 if fehlt else 0


def main():
    if "--pruefen" in sys.argv:
        return selbsttest()

    # Die Marke VOR allem Langsamen setzen: Solange sie fehlt, hoert der
    # Befehlsdienst mit, und das Laden von Parakeet dauert Sekunden.
    try:
        with open(MARKE, "w", encoding="utf-8") as f:
            f.write(f"{os.getpid()} dialos-suche\n")
    except OSError as fehler:
        melde(f"Marke liess sich nicht setzen: {fehler} - Abbruch")
        sprich("Die Suche liess sich nicht starten.")
        return 1

    def aufraeumen(nummer, _rahmen):
        # Ohne Handler bliebe die Marke bei SIGTERM liegen - und das Mikrofon
        # damit fuer immer belegt.
        raise SystemExit(128 + nummer)

    for nummer in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(nummer, aufraeumen)

    try:
        melde("=== DialOS-Suche gestartet ===")
        erkenner = parakeet_laden()
        begriff = begriff_hoeren(erkenner)
        melde(f"  verstanden: {begriff!r}")
        if not begriff:
            sprich(ANSAGE_NICHTS)
            return 0
        return suchen(begriff)
    finally:
        try:
            os.unlink(MARKE)
        except OSError:
            pass
        melde("=== beendet, Mikrofon zurueckgegeben ===")


if __name__ == "__main__":
    sys.exit(main())
