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

import collections
import json
import os
import signal
import subprocess
import sys
import threading
import time

SAY = "/usr/local/bin/dialos-say.py"
INDEX = "/usr/local/bin/dialos-suche-index.py"
ABTASTRATE = 16000
BLOCK = 4000
ECHO_QUELLE = "dialos_mikrofon_ohne_echo"

MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
MODELL_GROSS = "/usr/local/share/vosk-model-de-big"
PARAKEET_MODELL = ("/usr/local/share/dialos-parakeet/"
                   "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
PARAKEET_AUS = os.path.join(os.path.expanduser("~"), ".config", "dialos",
                            "parakeet-aus")

# Wie lange auf den Suchbegriff gewartet wird, und wann er als zu Ende gilt.
# Beides bewusst grosszuegiger als beim Diktat: Wer sucht, ueberlegt erst.
ZEITGRENZE_S = 20.0
RUHE_ENDE_S = 1.2
PEGEL_SCHWELLE = 150.0
# Wie viel vom Ton VOR dem Ende der Ansage noch zaehlt - wie im Diktat.
VORLAUF_S = 0.3

ANSAGE_LADEN = "Einen Moment, ich hole das Verzeichnis."
ANSAGE_START = "Wonach soll ich suchen?"
ANSAGE_NICHTS = "Ich habe nichts verstanden. Die Suche ist beendet."
ANSAGE_NOCH_NICHT = ("Der Suchindex ist noch nicht eingerichtet. "
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


def sprechen_bei_offener_aufnahme(text, prozess, frage=False):
    """Spricht die Ansage und liest dabei mit; liefert die letzten VORLAUF_S.

    OHNE DAS STAUT SICH DIE EIGENE ANSAGE IN DER LEITUNG (2026-09-18, Stephans
    erste Probe am Mikrofon): Das Mikrofon ist waehrend der Frage schon offen,
    `parec` fuellt die Pipe weiter, und `sprich()` wartet. Danach las die
    Schleife diesen Stau in Sekundenbruchteilen ein, hielt ihn fuer die Antwort
    - Pegel hoch, dann "Stille" - und brach nach 3,5 s ab, bevor Stephan
    ueberhaupt gesprochen hatte. Im Protokoll stand "verstanden: ''".

    Das Diktat loest das seit dem 2026-08-19 genau so; hier fehlte es. Was
    waehrend der Ansage hereinkommt, wird verworfen - bis auf die letzten
    0,3 s, damit ein sofort begonnenes Wort nicht abgeschnitten wird.
    """
    fertig = threading.Event()

    def ansage():
        try:
            sprich(text, frage=frage)
        finally:
            fertig.set()

    threading.Thread(target=ansage, daemon=True).start()
    zuletzt = collections.deque()
    while not fertig.is_set():
        block = prozess.stdout.read(800)
        if not block:
            break
        jetzt = time.time()
        zuletzt.append((jetzt, block))
        while zuletzt and zuletzt[0][0] < jetzt - 2.0:
            zuletzt.popleft()
    fertig.wait()
    grenze = time.time() - VORLAUF_S
    return b"".join(b for t, b in zuletzt if t >= grenze)


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


def vosk_laden():
    """Das grosse Vosk-Modell - oder None.

    ZWEI ERKENNER FUER DEN SUCHBEGRIFF (2026-09-18, Stephans erste Probe am
    Mikrofon). Der Entwurf setzte allein auf Parakeet, weil ein Suchbegriff
    Text ist. Das stimmt fuer SAETZE - gemessen am 2026-09-15: 2,8 % gegen
    12,7 % Wortfehler. Ein Suchbegriff ist aber meist EIN Wort, und genau dort
    kippt Parakeet: Beim Einkaufszettel traf Vosk 16 von 20 Waren, Parakeet 11,
    und aus einem einzeln gesprochenen "Gesobau" machte es hier "It's a".
    Deshalb hoeren beide zu, und gesucht wird mit beiden Ergebnissen - der
    Index entscheidet, welches Wort etwas findet. Das kostet nichts ausser
    Ladezeit, und die laeuft parallel.
    """
    try:
        import vosk
        vosk.SetLogLevel(-1)
        if not os.path.isdir(MODELL_GROSS):
            melde(f"  grosses Modell fehlt ({MODELL_GROSS})")
            return None
        t0 = time.time()
        modell = vosk.Model(MODELL_GROSS)
        melde(f"  grosses Modell geladen in {time.time() - t0:.1f} s")
        return modell
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"  Vosk liess sich nicht laden: {fehler}")
        return None


def modelle_laden():
    """Beide Erkenner gleichzeitig - nacheinander waeren es 9 s plus 2 s."""
    geladen = {}
    faden = threading.Thread(
        target=lambda: geladen.update(parakeet=parakeet_laden()), daemon=True)
    faden.start()
    geladen["vosk"] = vosk_laden()
    faden.join()
    return geladen.get("parakeet"), geladen.get("vosk")


def erkennen(erkenner, roh):
    import array
    if len(roh) < ABTASTRATE // 5:
        return ""
    werte = array.array("h", bytes(roh[:len(roh) - len(roh) % 2]))
    strom = erkenner.create_stream()
    strom.accept_waveform(ABTASTRATE, [x / 32768.0 for x in werte])
    erkenner.decode_stream(strom)
    return strom.result.text.strip()


def begriff_hoeren(erkenner, modell=None):
    """Ansage stellen und den Suchbegriff aufnehmen.

    DAS MIKROFON IST WAEHREND DER ANSAGE SCHON OFFEN - dieselbe Reihenfolge
    wie bei den Rueckfragen in dialos-notiz.py, und aus demselben Grund: Am
    2026-08-19 fiel Stephans "ja" in genau die Luecke zwischen Frage und
    Aufnahmebeginn. Erst bereit sein, dann fragen.
    """
    prozess = mikrofon_oeffnen()
    vosk_erkenner = None
    if modell is not None:
        import vosk
        vosk_erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE)
    try:
        vorrat = sprechen_bei_offener_aufnahme(ANSAGE_START, prozess, frage=True)
        roh = bytearray()
        ruhe = 0.0
        gesprochen = False
        ende = time.time() + ZEITGRENZE_S
        block_s = BLOCK / 2 / ABTASTRATE
        while time.time() < ende:
            if vorrat:
                block, vorrat = vorrat[:BLOCK], vorrat[BLOCK:]
            else:
                block = prozess.stdout.read(BLOCK)
            if not block:
                break
            roh += block
            if vosk_erkenner is not None:
                vosk_erkenner.AcceptWaveform(bytes(block))
            if pegel(block) >= PEGEL_SCHWELLE:
                gesprochen, ruhe = True, 0.0
            elif gesprochen:
                ruhe += block_s
                if ruhe >= RUHE_ENDE_S:
                    break
        melde(f"  {len(roh) / 2 / ABTASTRATE:.1f} s aufgenommen, "
              f"gesprochen={gesprochen}")
        if not gesprochen:
            return []
        begriffe = []
        if vosk_erkenner is not None:
            try:
                text = json.loads(vosk_erkenner.FinalResult()).get("text", "").strip()
                melde(f"  VOSK:     {text!r}")
                if text:
                    begriffe.append(text)
            except ValueError as fehler:
                melde(f"  Vosk-Ergebnis nicht lesbar: {fehler}")
        if erkenner is not None:
            text = erkennen(erkenner, roh).strip(" .!?,")
            melde(f"  PARAKEET: {text!r}")
            if text and text.lower() not in (x.lower() for x in begriffe):
                begriffe.append(text)
        return begriffe
    finally:
        try:
            prozess.terminate()
        except OSError:
            pass


def suchen(begriffe):
    """Den Index fragen und das Ergebnis ansagen.

    MEHRERE BEGRIFFE, EINE ANTWORT (2026-09-18): Vosk und Parakeet hoeren
    dasselbe Wort verschieden. Gesucht wird mit beiden, angesagt wird der
    Begriff, der etwas gefunden hat - der Index entscheidet damit, welche
    Erkennung recht hatte, und der Nutzer hoert, wonach gesucht wurde.

    DIE ANZAHL KOMMT ZUERST, dann der neueste Treffer - nicht die Liste. Wer
    vierzig Briefe findet, will sie nicht hoeren; er will wissen, dass es
    vierzig sind, und dann eingrenzen. Dieselbe Regel wie beim Einkaufszettel:
    Ein Befehl nimmt dem Nutzer keine Entscheidung ab, die er selbst treffen
    kann - er sagt die Zahl und nennt den Weg.

    "KLINGT WIE" WIRD AUSGESPROCHEN. Findet der Index nur ueber die Koelner
    Phonetik, stimmt die Schreibweise nicht mit dem Gesprochenen ueberein
    ("Meier" gesagt, "Mayer" gefunden). Das gehoert gesagt, sonst wundert sich
    der Nutzer beim Vorlesen - und er kann den Bildschirm nicht danebenhalten.
    """
    if not os.access(INDEX, os.X_OK):
        melde(f"  Index-Werkzeug fehlt: {INDEX}")
        sprich(ANSAGE_NOCH_NICHT)
        return 1
    begriff, treffer = begriffe[0], []
    for versuch in begriffe:
        try:
            r = subprocess.run([INDEX, "suchen", versuch],
                               capture_output=True, timeout=120)
            gefunden = json.loads(r.stdout.decode("utf-8", errors="replace") or "[]")
        except (OSError, subprocess.TimeoutExpired, ValueError) as fehler:
            melde(f"  Suche fehlgeschlagen: {fehler}")
            sprich("Bei der Suche ist etwas schiefgegangen.")
            return 1
        melde(f"  {len(gefunden)} Treffer fuer {versuch!r}")
        if gefunden:
            begriff, treffer = versuch, gefunden
            break
    if not treffer:
        sprich(f"Zu {begriff} habe ich nichts gefunden.")
        return 0

    nur_klang = all(x.get("wie") == "klang" for x in treffer)
    klang = " Die Schreibweise klingt nur aehnlich." if nur_klang else ""
    erster = treffer[0]
    art = erster.get("art", "Schreiben")
    name = os.path.basename(erster.get("pfad", ""))
    wann = time.strftime("%d. %B", time.localtime(erster.get("geaendert", 0)))

    if len(treffer) == 1:
        sprich(f"Ich habe einen Treffer zu {begriff}.{klang} "
               f"Es ist {art} {name} vom {wann}.")
    else:
        sprich(f"Ich habe {len(treffer)} Treffer zu {begriff}.{klang} "
               f"Der neueste ist {art} {name} vom {wann}.")
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
    if not os.access(INDEX, os.X_OK):
        fehlt.append(INDEX + " (es gaebe nichts zu durchsuchen)")
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
        sprich(ANSAGE_LADEN)
        erkenner, modell = modelle_laden()
        begriffe = begriff_hoeren(erkenner, modell)
        melde(f"  verstanden: {begriffe!r}")
        if not begriffe:
            sprich(ANSAGE_NICHTS)
            return 0
        return suchen(begriffe)
    finally:
        try:
            os.unlink(MARKE)
        except OSError:
            pass
        melde("=== beendet, Mikrofon zurueckgegeben ===")


if __name__ == "__main__":
    sys.exit(main())
