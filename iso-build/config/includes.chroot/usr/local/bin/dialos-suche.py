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
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time

SAY = "/usr/local/bin/dialos-say.py"
INDEX = "/usr/local/bin/dialos-suche-index.py"
DIKTAT_SKRIPT = "/usr/local/bin/dialos-diktat.py"
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
# ERST DER BEREICH, DANN DER BEGRIFF (Stephan, 2026-09-18: "der erste Befehl ist
# Unterlagen durchsuchen, dann Dokumente oder Postfach/Mails oder Bilder oder
# Videos"). Der Bereich schneidet vorher weg, was ohnehin nicht gemeint ist -
# und er macht die Frage danach kuerzer: Wer "Postfach" gesagt hat, wird nicht
# mehr gefragt, ob er den Brief oder die Mail meint.
ANSAGE_BEREICH = ("Wo soll ich suchen? Sage: Dokumente, Postfach, Bilder oder Videos. "
                  "Im Postfach suche ich die E-Mails.")
BEREICHE = {
    "dokumente": ("Brief", "Notiz", "Ablage"), "dokument": ("Brief", "Notiz", "Ablage"),
    "unterlagen": ("Brief", "Notiz", "Ablage"), "briefe": ("Brief", "Notiz", "Ablage"),
    "brief": ("Brief", "Notiz", "Ablage"), "notizen": ("Brief", "Notiz", "Ablage"),
    "ablage": ("Brief", "Notiz", "Ablage"), "archiv": ("Brief", "Notiz", "Ablage"),
    "postfach": ("Mail",), "post": ("Mail",), "mail": ("Mail",), "mails": ("Mail",),
    "nachrichten": ("Mail",), "nachricht": ("Mail",), "email": ("Mail",),
}
NOCH_NICHT = ("bilder", "bild", "fotos", "foto", "videos", "video", "filme", "film")
ANSAGE_NOCH_NICHT_BEREICH = ("Bilder und Videos kann ich noch nicht durchsuchen. "
                             "Das kommt später.")
# DAS WORT "BEGRIFF" GEHOERT IN DIE FRAGE (Stephan, 2026-09-21: "koennen wir bei
# Dokument, wenn ich einen Begriff sagen soll, in der Frage auch Begriff
# einfliessen lassen"). "Wonach soll ich suchen?" laesst offen, was erwartet
# wird - ein Dateiname? ein Datum? ein ganzer Satz? Wer den Bildschirm nicht
# sieht, hat keine Liste vor sich, an der er das ablesen koennte. Dazu der
# Bereich, den er gerade gewaehlt hat: So hoert er zugleich, dass die Wahl
# angekommen ist.
ANSAGE_START = "Wonach soll ich suchen? Sage einen Begriff."
ANSAGE_BEGRIFF = {
    "dokumente": "Wonach soll ich in den Dokumenten suchen? Sage einen Begriff.",
    "postfach": "Wonach soll ich im Postfach suchen? Sage einen Begriff.",
}
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


class Spaeter:
    """Ein Modell, das noch laedt - `hole()` wartet, bis es da ist.

    WARUM NICHT EINFACH WARTEN (2026-09-18, aus Stephans Probe): Das grosse
    Vosk-Modell braucht 9 s, Parakeet 2 s. Beide vor der Frage zu laden hiess:
    zwoelf Sekunden Stille zwischen "Unterlagen durchsuchen" und "Wonach soll
    ich suchen?". Gebraucht wird Vosk aber erst, wenn der Suchbegriff fertig
    gesprochen ist - bis dahin laedt es im Hintergrund weiter. Die Aufnahme
    wird deshalb roh gesammelt und erst am Ende durch den Erkenner geschickt.
    """

    def __init__(self, lade):
        self.wert = None
        self.faden = threading.Thread(target=self._laden, args=(lade,), daemon=True)
        self.faden.start()

    def _laden(self, lade):
        self.wert = lade()

    def hole(self):
        self.faden.join()
        return self.wert


def modelle_laden():
    """Parakeet sofort, Vosk im Hintergrund - die Frage soll nicht warten."""
    vosk_spaeter = Spaeter(vosk_laden)
    return parakeet_laden(), vosk_spaeter


def erkennen(erkenner, roh):
    import array
    if len(roh) < ABTASTRATE // 5:
        return ""
    werte = array.array("h", bytes(roh[:len(roh) - len(roh) % 2]))
    strom = erkenner.create_stream()
    strom.accept_waveform(ABTASTRATE, [x / 32768.0 for x in werte])
    erkenner.decode_stream(strom)
    return strom.result.text.strip()


def antwort_hoeren(frage, erkenner, modell=None, mit_pegel=False):
    """Eine Frage stellen und die Antwort aufnehmen - Liste der Lesarten.

    DAS MIKROFON IST WAEHREND DER ANSAGE SCHON OFFEN - dieselbe Reihenfolge
    wie bei den Rueckfragen in dialos-notiz.py, und aus demselben Grund: Am
    2026-08-19 fiel Stephans "ja" in genau die Luecke zwischen Frage und
    Aufnahmebeginn. Erst bereit sein, dann fragen.
    """
    prozess = mikrofon_oeffnen()
    try:
        vorrat = sprechen_bei_offener_aufnahme(frage, prozess, frage=True)
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
            if pegel(block) >= PEGEL_SCHWELLE:
                gesprochen, ruhe = True, 0.0
            elif gesprochen:
                ruhe += block_s
                if ruhe >= RUHE_ENDE_S:
                    break
        melde(f"  {len(roh) / 2 / ABTASTRATE:.1f} s aufgenommen, "
              f"gesprochen={gesprochen}")
        if not gesprochen:
            return ([], False) if mit_pegel else []
        begriffe = []
        geladen = modell.hole() if isinstance(modell, Spaeter) else modell
        if geladen is not None:
            try:
                import vosk
                erk = vosk.KaldiRecognizer(geladen, ABTASTRATE)
                erk.AcceptWaveform(bytes(roh))
                text = json.loads(erk.FinalResult()).get("text", "").strip()
                melde(f"  VOSK:     {text!r}")
                if text:
                    begriffe.append(text)
            except (ValueError, ImportError) as fehler:
                melde(f"  Vosk-Ergebnis nicht lesbar: {fehler}")
        if erkenner is not None:
            text = erkennen(erkenner, roh).strip(" .!?,")
            melde(f"  PARAKEET: {text!r}")
            if text and text.lower() not in (x.lower() for x in begriffe):
                begriffe.append(text)
        return (begriffe, gesprochen) if mit_pegel else begriffe
    finally:
        try:
            prozess.terminate()
        except OSError:
            pass


ABBRUCH_WORTE = ("abbrechen", "abbruch", "beenden", "stopp", "stop", "aufhören", "aufhoeren")
ARTEN_WORTE = {"brief": "Brief", "briefe": "Brief", "schreiben": "Brief",
               "notiz": "Notiz", "notizen": "Notiz",
               "ablage": "Ablage", "archiv": "Ablage", "akte": "Ablage",
               "mail": "Mail", "mails": "Mail", "email": "Mail", "e-mail": "Mail",
               # "MAIL" IST EIN HARTES WORT (Stephan, 2026-09-18: "mit dem Wort
               # Mail hat sich die Sprachsteuerung schwer getan"). Im Protokoll
               # kam es als "melle", "Man" und "Okay" an. Deshalb zusaetzlich
               # deutsche Woerter, die niemand verwechselt.
               "nachricht": "Mail", "nachrichten": "Mail", "post": "Mail",
               "elektronische": "Mail"}


# GESPROCHEN HEISST ES E-MAIL (Stephan, 2026-09-18: "Mache doch aus Mail EMail").
# In der Datenbank bleibt "Mail" - dort ist es ein Schluessel, kein Satz.
ART_GESPROCHEN = {"Mail": "E-Mail", "Brief": "Brief", "Notiz": "Notiz",
                  "Ablage": "Ablage"}


def gesprochene_art(art):
    return ART_GESPROCHEN.get(art, art)


def art_aus_antwort(texte, gruppen):
    """Welche Art ist gemeint? Wort, Klang, dann Aehnlichkeit.

    Der Klangvergleich kommt aus dem Index (Koelner Phonetik) - "melle" und
    "mail" haben denselben Schluessel, "man" nicht. Was der Erkenner daraus
    gemacht hat, ist nicht zu aendern; erkennen laesst es sich trotzdem.
    """
    koelner = None
    try:
        spec = importlib.util.spec_from_file_location("dialos_suche_index", INDEX)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        koelner = modul.koelner
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"  Klangvergleich nicht nutzbar: {fehler}")
    for text in texte:
        for wort in text.lower().split():
            art = ARTEN_WORTE.get(wort.strip(".,!?"))
            if art in gruppen:
                return art
    if koelner:
        for text in texte:
            for wort in text.lower().split():
                schluessel = koelner(wort.strip(".,!?"))
                for wort_art, art in ARTEN_WORTE.items():
                    if art in gruppen and schluessel and koelner(wort_art) == schluessel:
                        melde(f"  Art {art!r} ueber den Klang von {wort!r}")
                        return art
    beste, bester_wert = None, 0.6
    for text in texte:
        for wort_art, art in ARTEN_WORTE.items():
            if art not in gruppen:
                continue
            wert = _aehnlich(text, wort_art)
            if wert > bester_wert:
                beste, bester_wert = art, wert
    if beste:
        melde(f"  Art {beste!r} ueber Aehnlichkeit ({bester_wert:.2f})")
    return beste
MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember")
OHNE_NAMEN = "ohne Absender"
ORDNUNGSZAHLEN = {"erste": 0, "ersten": 0, "erster": 0, "zweite": 1, "zweiten": 1,
                  "dritte": 2, "dritten": 2, "vierte": 3, "vierten": 3,
                  "fünfte": 4, "fünften": 4}


def _abbruch(texte):
    return any(w in ABBRUCH_WORTE for t in texte for w in t.lower().split())


def _aehnlich(gesagt, kandidat):
    import difflib
    sauber = lambda x: re.sub(r"[^a-z0-9äöüß]", "", x.lower())
    return difflib.SequenceMatcher(None, sauber(gesagt), sauber(kandidat)).ratio()


def jahr_aus_antwort(texte):
    """Die Jahreszahl aus dem Gesagten - Ziffern oder Zahlwoerter.

    Die Zahlwoerter kommen aus dem Diktat (zahlen_in_ziffern), damit "zwanzig
    sechsundzwanzig" und "zweitausendsechsundzwanzig" hier genauso zu 2026
    werden wie in einem Brief. Zwei Zahlenleser waeren zwei Staende.
    """
    for text in texte:
        m = re.search(r"\b(19|20)\d{2}\b", text)
        if m:
            return int(m.group(0))
    try:
        spec = importlib.util.spec_from_file_location("dialos_diktat", DIKTAT_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"  Zahlwoerter nicht lesbar: {fehler}")
        return None
    for text in texte:
        m = re.search(r"\b(19|20)\d{2}\b", modul.zahlen_in_ziffern(text))
        if m:
            return int(m.group(0))
    return None


def merkmal_waehlen(treffer):
    """Wonach als Naechstes gefragt wird - oder None, wenn nichts mehr trennt.

    NUR MERKMALE, DIE WIRKLICH TRENNEN (Stephan, 2026-09-18: "Schritt fuer
    Schritt die Treffer verkleinern, bis nur noch eine Datei uebrig bleibt").
    Eine Frage, deren Antwort alle Treffer behaelt, kostet den Nutzer Zeit und
    bringt ihn keinen Schritt weiter - und er sieht nicht, dass sie sinnlos war.
    Deshalb gilt ein Merkmal nur, wenn es mindestens zwei Gruppen bildet, und
    genommen wird das mit der kleinsten groessten Gruppe: Es schneidet am meisten weg.
    """
    kandidaten = []
    jahre = {}
    monate = {}
    arten = {}
    personen = {}
    for nummer, t in enumerate(treffer):
        if t.get("jahr"):
            jahre.setdefault(t["jahr"], set()).add(nummer)
        monat = time.localtime(t.get("geaendert", 0)).tm_mon
        monate.setdefault(monat, set()).add(nummer)
        if t.get("art"):
            arten.setdefault(t["art"], set()).add(nummer)
        for person in t.get("personen") or []:
            if person.strip():
                personen.setdefault(person.strip(), set()).add(nummer)
    # EIN EINZIGER NAME TRENNT AUCH (2026-09-21, an Stephans Probe gesehen):
    # Nach "Brief" blieben elf Treffer, zwei davon von der GESOBAU AG - gefragt
    # wurde trotzdem nicht, weil die Regel zwei verschiedene Werte verlangte.
    # Zwei mit und neun ohne ist aber genau eine Trennung. Deshalb bekommt die
    # Personenfrage eine Gegengruppe fuer alle, bei denen kein Name steht.
    if personen and len(personen) < 2:
        mit = set().union(*personen.values())
        ohne = set(range(len(treffer))) - mit
        if ohne:
            personen = dict(personen)
            personen[OHNE_NAMEN] = ohne
    for name, gruppen in (("jahr", jahre), ("art", arten), ("person", personen),
                          ("monat", monate)):
        if len(gruppen) > 1:
            kandidaten.append((max(len(x) for x in gruppen.values()), name, gruppen))
    if not kandidaten:
        return None, {}
    kandidaten.sort(key=lambda x: (x[0], ("jahr", "art", "person", "monat").index(x[1])))
    _groesse, name, gruppen = kandidaten[0]
    return name, gruppen


def eingrenzen(treffer, erkenner, modell):
    """Fragt so lange nach Merkmalen, bis ein Treffer uebrig ist - oder Schluss.

    Hoechstens vier Fragen: Wer danach noch nicht bei einem Dokument ist, hat
    einen zu allgemeinen Begriff gesucht; weiterzufragen waere Quaelerei.
    """
    for _runde in range(4):
        if len(treffer) <= 1:
            return treffer
        name, gruppen = merkmal_waehlen(treffer)
        if name is None:
            return treffer
        if name == "jahr":
            frage = (f"{len(treffer)} Treffer. Aus welchem Jahr? "
                     + " Oder ".join(str(j) for j in sorted(gruppen)) + ".")
        elif name == "art":
            frage = (f"{len(treffer)} Treffer. Was davon: "
                     + ", ".join(gesprochene_art(a) for a in sorted(gruppen)) + "?")
        elif name == "monat":
            frage = (f"{len(treffer)} Treffer. Aus welchem Monat? "
                     + " Oder ".join(MONATE[m - 1] for m in sorted(gruppen)) + ".")
        else:
            # DIE GEGENGRUPPE GEHOERT ANS ENDE (2026-09-21, an der Ansage
            # gehoert): "Von wem? ohne Absender, GESOBAU AG" stellte sie nach
            # vorn, wo sie wie ein Name klingt. Erst die echten Namen, dann der
            # Ausweg.
            namen = [n for n in sorted(gruppen, key=lambda x: -len(gruppen[x]))
                     if n != OHNE_NAMEN][:4]
            frage = sprechbar(f"{len(treffer)} Treffer. Von wem? " + ", ".join(namen)
                              + (". Oder sage: keiner." if OHNE_NAMEN in gruppen else "."))
        texte, gesprochen = antwort_hoeren(frage, erkenner, modell, mit_pegel=True)
        melde(f"  {name}: Antwort {texte!r}")
        if _abbruch(texte):
            return []
        if not texte and gesprochen:
            # GESPROCHEN, ABER NICHTS VERSTANDEN ist etwas anderes als Stille
            # (2026-09-18, Stephans erste Probe am Mikrofon: 6,7 s aufgenommen,
            # beide Erkenner leer - und der Dialog war zu Ende). Wer geantwortet
            # hat, bekommt die Frage noch einmal; wer schweigt, wird in Ruhe
            # gelassen.
            melde("  gesprochen, aber nichts verstanden - Frage wiederholen")
            sprich("Das habe ich nicht verstanden.")
            continue
        if not texte:
            melde("  keine Antwort - Dialog beendet")
            sprich("Ich höre nichts mehr. Die Suche ist beendet.")
            return []
        gewaehlt = None
        if name == "jahr":
            jahr = jahr_aus_antwort(texte)
            if jahr in gruppen:
                gewaehlt = gruppen[jahr]
        elif name == "art":
            art = art_aus_antwort(texte, gruppen)
            if art:
                gewaehlt = gruppen[art]
        elif name == "monat":
            for text in texte:
                for nummer, monat in enumerate(MONATE, start=1):
                    if monat.lower()[:4] in text.lower() and nummer in gruppen:
                        gewaehlt = gruppen[nummer]
                        break
                if gewaehlt:
                    break
        else:
            beste, bester_wert = None, 0.6
            for text in texte:
                if re.search(r"(?i)\b(keiner|keine|keinen|niemand|ohne)\b", text) \
                        and OHNE_NAMEN in gruppen:
                    beste, bester_wert = OHNE_NAMEN, 1.0
                    break
                for person in gruppen:
                    if person == OHNE_NAMEN:
                        continue
                    wert = _aehnlich(text, person)
                    if wert > bester_wert:
                        beste, bester_wert = person, wert
            if beste:
                melde(f"  Person {beste!r} ({bester_wert:.2f})")
                gewaehlt = gruppen[beste]
        if gewaehlt is None:
            sprich("Das habe ich nicht zuordnen können.")
            continue
        treffer = [t for i, t in enumerate(treffer) if i in gewaehlt]
        melde(f"  eingegrenzt auf {len(treffer)}")
    return treffer


def mit_wort_eingrenzen(treffer, erkenner, modell):
    """Letzter Schritt, wenn kein Merkmal mehr trennt: noch ein Suchwort.

    (2026-09-18) Im ersten Durchlauf blieben nach Art und Jahr vierzehn Briefe
    stehen, die sich in nichts mehr unterschieden - alle aus demselben Monat,
    ohne erkannten Absender. Ohne diesen Schritt endet der Dialog dort, und der
    Nutzer hat vierzehn Treffer und keinen Weg weiter.
    """
    texte = antwort_hoeren(f"Es bleiben {len(treffer)} Treffer. Sage ein weiteres Wort "
                           "zum Eingrenzen, oder sage: aufzählen.", erkenner, modell)
    if not texte or _abbruch(texte):
        return treffer
    # "aufzaehlen" kam am Geraet als "auf zehn" und "Aufziehen" an (2026-09-18) -
    # deshalb nicht auf das Wort prüfen, sondern auf die Aehnlichkeit.
    if any("zähl" in t.lower() or "zaehl" in t.lower()
           or _aehnlich(t, "aufzählen") >= 0.6 for t in texte):
        return treffer
    pfade = set()
    for versuch in texte:
        try:
            r = subprocess.run([INDEX, "suchen", versuch], capture_output=True, timeout=120)
            for x in json.loads(r.stdout.decode("utf-8", errors="replace") or "[]"):
                pfade.add(x["pfad"])
        except (OSError, subprocess.TimeoutExpired, ValueError) as fehler:
            melde(f"  zweite Suche fehlgeschlagen: {fehler}")
    enger = [t for t in treffer if t["pfad"] in pfade]
    melde(f"  mit {texte!r} eingegrenzt: {len(treffer)} -> {len(enger)}")
    if not enger:
        sprich("Damit finde ich nichts mehr. Ich bleibe bei den bisherigen Treffern.")
        return treffer
    return enger


MAILADRESSE = re.compile(r"\b([\w.+-]+)@([\w-]+(?:\.[\w-]+)+)")


def sprechbar(text):
    """Mailadressen hoerbar machen - wie beim Vorlesen eines Briefs.

    Ohne das sagt Piper "web57p6@s111.goserver.host" als Buchstabensalat; der
    Punkt darin klaenge ausserdem wie ein Satzende (2026-09-18, aus Stephans
    Probe: die Mail hatte keinen Anzeigenamen fuer den Empfaenger).
    """
    d = _modul(DIKTAT_SKRIPT_MODUL, "dialos_diktat")
    if d is not None and hasattr(d, "mailadresse_lesbar"):
        return d.mailadresse_lesbar(text)
    lesbar = lambda teil: (teil.replace(".", " Punkt ").replace("-", " Minus ")
                           .replace("_", " Unterstrich ").replace("  ", " ").strip())
    return MAILADRESSE.sub(lambda m: f"{lesbar(m.group(1))} at {lesbar(m.group(2))}", text)


def treffer_nennen(t):
    """Wie ein Treffer angesagt wird - Art, Datum, Titel.

    NICHT DER DATEINAME (2026-09-18, aus der ersten Aufzaehlung): "Brief vom
    15. September, 2026-09-15-1634-Brief.pdf" sagt einem Hoerer nichts. Der
    Titel ist der Betreff, sonst der erste Satz nach der Anrede.
    """
    art = gesprochene_art(t.get("art", "Schreiben"))
    wann = time.strftime("%d. %B", time.localtime(t.get("geaendert", 0)))
    wer = (t.get("personen") or [""])[0]
    titel = (t.get("titel") or os.path.basename(t.get("pfad", ""))).strip()
    if len(titel) > 90:
        titel = titel[:90].rsplit(" ", 1)[0] + " und so weiter"
    return sprechbar(f"{art} vom {wann}" + (f", {wer}" if wer else "")
                     + f": {titel.rstrip('.')}")


DRUCKEN_SKRIPT = "/usr/local/bin/dialos-drucken.py"
ARCHIV_SKRIPT = "/usr/local/bin/dialos-archiv.py"
DRUCK_OPTIONEN = ["-o", "media=A4", "-o", "orientation-requested=3"]
WAHL_WORTE = {"vorlesen": "vorlesen", "lesen": "vorlesen", "lies": "vorlesen",
              "vorlese": "vorlesen", "drucken": "drucken", "druck": "drucken",
              "ausdrucken": "drucken", "papier": "drucken",
              "antworten": "antworten", "antwort": "antworten",
              "weiterleiten": "weiterleiten", "weiterleitung": "weiterleiten",
              "weiter": "weiterleiten",
              "nichts": "nichts", "keine": "nichts", "nein": "nichts",
              "danke": "nichts", "fertig": "nichts"}
DIKTAT_SKRIPT_MODUL = "/usr/local/bin/dialos-diktat.py"
ENTWURF_SKRIPT = "/usr/local/bin/dialos-mail-entwurf.py"
EMPFAENGER_SKRIPT = "/usr/local/bin/dialos-empfaenger.py"


def _modul(pfad, name):
    try:
        spec = importlib.util.spec_from_file_location(name, pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"  {name} nicht nutzbar: {fehler}")
        return None


def text_holen(t):
    """Der Text des Treffers aus dem Index - schon extrahiert."""
    try:
        r = subprocess.run([INDEX, "text", t["pfad"]], capture_output=True, timeout=60)
        return r.stdout.decode("utf-8", errors="replace").strip()
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"  Text nicht lesbar: {fehler}")
        return ""


def drucken_treffer(t, erkenner, modell):
    """Den Treffer auf Papier - PDF direkt, alles andere ueber den PDF-Erzeuger.

    MIT RUECKFRAGE, wie jeder Druckbefehl seit dem 2026-09-14: Ein missverstandenes
    Wort kostet sonst eine Seite Papier, und der Nutzer sieht nicht, was da liegt.
    """
    antwort = antwort_hoeren("Soll ich das drucken? Sage ja oder nein.", erkenner, modell)
    if not any(w in ("ja", "jawohl", "gerne", "bitte")
               for text in antwort or [] for w in text.lower().split()):
        sprich("Gut, ich drucke nicht.")
        return 0
    drucken = _modul(DRUCKEN_SKRIPT, "dialos_drucken")
    ziel = drucken.drucker() if drucken else None
    if not ziel:
        sprich("Ich finde keinen Drucker.")
        return 1
    datei = t["pfad"]
    aufraeumen = None
    if "#" in datei or not datei.lower().endswith(".pdf"):
        # Mail oder Textdatei: dasselbe PDF wie im Archiv, damit Papier und
        # Archiv gleich aussehen.
        archiv = _modul(ARCHIV_SKRIPT, "dialos_archiv")
        text = text_holen(t)
        if archiv is None or not text:
            sprich("Ich kann das nicht drucken.")
            return 1
        import tempfile
        datei = os.path.join(tempfile.mkdtemp(prefix="dialos-suche-"), "druck.pdf")
        aufraeumen = datei
        try:
            archiv.als_pdf(text, datei)
        except Exception as fehler:        # noqa: BLE001 - jede Ursache zaehlt
            melde(f"  PDF fehlgeschlagen: {fehler}")
            sprich("Das PDF ließ sich nicht erstellen.")
            return 1
    try:
        p = subprocess.run(["lp", "-d", ziel] + DRUCK_OPTIONEN + [datei],
                           capture_output=True, timeout=60)
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"  lp nicht aufrufbar: {fehler}")
        sprich("Der Druck hat nicht geklappt.")
        return 1
    finally:
        if aufraeumen:
            try:
                os.unlink(aufraeumen)
            except OSError:
                pass
    if p.returncode != 0:
        melde(f"  lp meldet {p.returncode}: {p.stderr.decode('utf-8', 'replace')[:200]}")
        sprich("Der Druck hat nicht geklappt.")
        return 1
    melde(f"  gedruckt auf {ziel}: {t['pfad']}")
    sprich("Ich drucke das aus.")
    return 0


def mail_daten(t):
    """Absender, Betreff und Text der gefundenen Mail - aus ihrer mbox."""
    try:
        r = subprocess.run([INDEX, "mail", t["pfad"]], capture_output=True, timeout=60)
        return json.loads(r.stdout.decode("utf-8", errors="replace") or "{}")
    except (OSError, subprocess.TimeoutExpired, ValueError) as fehler:
        melde(f"  Mail nicht lesbar: {fehler}")
        return {}


def ja_oder_nein(frage):
    """Kurze Rueckfrage mit dem KLEINEN Modell - es laedt in einer halben Sekunde.

    Die grossen Erkenner sind zu diesem Zeitpunkt absichtlich weggeraeumt (siehe
    text_diktieren): Zwei geladene Saetze zugleich waeren rund 20 GB, das Geraet
    hat sie nicht.
    """
    import vosk
    vosk.SetLogLevel(-1)
    if not os.path.isdir(MODELL_KLEIN):
        return False
    modell = vosk.Model(MODELL_KLEIN)
    grammatik = json.dumps(["ja", "nein", "[unk]"], ensure_ascii=False)
    prozess = mikrofon_oeffnen()
    try:
        vorrat = sprechen_bei_offener_aufnahme(frage, prozess, frage=True)
        erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, grammatik)
        bis = time.time() + 12.0
        while time.time() < bis:
            if vorrat:
                block, vorrat = vorrat[:BLOCK], vorrat[BLOCK:]
            else:
                block = prozess.stdout.read(BLOCK)
            if not block:
                break
            if not erkenner.AcceptWaveform(block):
                continue
            worte = json.loads(erkenner.Result()).get("text", "").split()
            if "ja" in worte:
                return True
            if "nein" in worte:
                return False
        return False
    finally:
        try:
            prozess.terminate()
        except OSError:
            pass


DIKTAT_HELFER = """
import importlib.util, sys
spec = importlib.util.spec_from_file_location("d", sys.argv[1])
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
d.EMPFAENGER_FRAGEN = False
gesammelt = {}
d.notiz_schreiben = lambda name, zeilen: (
    gesammelt.update(text="\\n".join(zeilen)), "/dev/null")[1]
# DIE SCHLUSSANSAGE GEHOERT HIER ZUR MAIL, NICHT ZU DEN NOTIZEN (Stephan,
# 2026-09-18: "Es wurde zum Schluss Notizen erwaehnt - waere E-Mail nicht
# besser?"). Das Diktat sagt sonst "Diktat beendet, 2 Eintraege geschrieben.
# Moechtest Du Deine Notizen vorgelesen haben" - beides falsch: Es sind Saetze
# einer Mail, und "Notizen vorlesen" laese etwas ganz anderes vor.
d.ansage_ende = lambda name, anzahl: (
    "Die E-Mail ist geschrieben, ein Satz." if anzahl == 1
    else "Die E-Mail ist geschrieben, %d Sätze." % anzahl)
d.diktat_fuehren("notiz", "notizen", sys.argv[2])
sys.stdout.write(gesammelt.get("text", ""))
"""


def text_diktieren(ansage):
    """Laesst den Text diktieren - mit dem Diktat, nicht mit einer zweiten Fassung.

    IN EINEM EIGENEN PROZESS, und das hat zwei Gruende: Das Diktat laedt sein
    eigenes Erkennerpaar (rund 10 GB) - endet der Prozess, ist der Speicher
    sicher wieder frei, ohne dass die Suche ihre eigenen Modelle wegwerfen und
    spaeter neu laden muesste. Und der Text kommt ueber die Standardausgabe
    zurueck, statt dass hier eine zweite Diktat-Fassung entstuende: Was das
    Diktat an Regeln kann - Absaetze, Zahlen, Satzzeichen, "Satz loeschen" -
    gilt damit auch fuer eine Mail.

    DIE MIKROFON-MARKE GEHOERT DANACH WIEDER UNS: Das Diktat raeumt seine eigene
    am Ende weg, und das ist dieselbe Datei. Ohne das Neusetzen hoerte der
    Befehlsdienst mit, waehrend die Suche noch fragt.
    """
    import tempfile
    ordner = tempfile.mkdtemp(prefix="dialos-diktat-")
    helfer = os.path.join(ordner, "diktieren.py")
    with open(helfer, "w", encoding="utf-8") as f:
        f.write(DIKTAT_HELFER)
    sprich(ansage)
    text = ""
    try:
        r = subprocess.run([sys.executable, helfer, DIKTAT_SKRIPT_MODUL, ECHO_QUELLE],
                           capture_output=True, timeout=1200)
        text = r.stdout.decode("utf-8", errors="replace").strip()
        if r.returncode != 0:
            melde(f"  Diktat meldet {r.returncode}: "
                  f"{r.stderr.decode('utf-8', 'replace')[-300:]}")
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"  Diktat fehlgeschlagen: {fehler}")
    finally:
        try:
            with open(MARKE, "w", encoding="utf-8") as f:
                f.write(f"{os.getpid()} dialos-suche\n")
        except OSError as fehler:
            melde(f"  Marke nicht neu gesetzt: {fehler}")
        try:
            os.unlink(helfer)
            os.rmdir(ordner)
        except OSError:
            pass
    melde(f"  diktiert: {len(text)} Zeichen")
    return text


def entwurf_ablegen(an, betreff, text, bezug=None, zitat=""):
    """Ruft dialos-mail-entwurf.py - gesendet wird nichts."""
    import tempfile
    ordner = tempfile.mkdtemp(prefix="dialos-entwurf-")
    t_datei = os.path.join(ordner, "text.txt")
    z_datei = os.path.join(ordner, "zitat.txt")
    with open(t_datei, "w", encoding="utf-8") as f:
        f.write(text)
    with open(z_datei, "w", encoding="utf-8") as f:
        f.write(zitat)
    befehl = [ENTWURF_SKRIPT, "anlegen", "--an", an, "--betreff", betreff,
              "--text", t_datei, "--zitat", z_datei]
    if bezug:
        befehl += ["--bezug", bezug]
    try:
        r = subprocess.run(befehl, capture_output=True, timeout=60)
        ergebnis = r.stdout.decode("utf-8", errors="replace").strip()
        melde(f"  Entwurf: {ergebnis!r} (Rueckgabe {r.returncode})")
        return r.returncode == 0, ergebnis
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"  Entwurf fehlgeschlagen: {fehler}")
        return False, ""
    finally:
        for datei in (t_datei, z_datei):
            try:
                os.unlink(datei)
            except OSError:
                pass


def antworten_auf(t, erkenner, modell, weiterleiten=False):
    """Antwort oder Weiterleitung diktieren und als Entwurf ablegen."""
    daten = mail_daten(t)
    if not daten.get("betreff") and not daten.get("von"):
        sprich("Ich finde die Mail nicht mehr.")
        return 1
    betreff = daten.get("betreff") or "(ohne Betreff)"
    if weiterleiten:
        an = empfaenger_erfragen_fuer_mail(erkenner, modell)
        if not an:
            return 0
        betreff = betreff if betreff.lower().startswith("fwd:") else f"Fwd: {betreff}"
    else:
        an = daten.get("von", "")
        if not an:
            sprich("Diese Mail hat keine Absenderadresse.")
            return 1
        betreff = betreff if betreff.lower().startswith("re:") else f"Re: {betreff}"
    text = text_diktieren("Diktiere jetzt den Text. Sage am Ende: Diktat beenden.")
    if not text:
        sprich("Ich habe nichts mitgeschrieben. Es wird kein Entwurf abgelegt.")
        return 0
    wer = sprechbar(an)
    if not ja_oder_nein(f"Ich habe {len(text.split())} Wörter an {wer}. "
                        "Soll ich den Entwurf ablegen? Sage ja oder nein."):
        sprich("Gut, ich lege nichts ab.")
        return 0
    geklappt, ergebnis = entwurf_ablegen(an, betreff, text,
                                         bezug=daten.get("message_id"),
                                         zitat=daten.get("text", "")[:4000])
    if not geklappt:
        sprich("Der Entwurf ließ sich nicht ablegen.")
        return 1
    if ergebnis == "vorgemerkt":
        sprich("Der Entwurf kommt in die Warteschlange, weil Thunderbird gerade "
               "läuft. Beim nächsten Anmelden liegt er in den Entwürfen. "
               "Gesendet wird nichts.")
    else:
        sprich("Der Entwurf liegt in Thunderbird unter Entwürfe. Gesendet wird "
               "nichts, das machst Du selbst.")
    return 0


ADRESSE_GUELTIG = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PERSOENLICHE_DATEN_SKRIPT = "/usr/local/bin/dialos-persoenliche-daten.py"


def bekannte_adressen():
    """Mailadressen, die auf diesem Geraet schon vorkommen - zum Gegenlesen.

    (2026-09-18, aus Stephans erster buchstabierter Adresse: Aus
    "kontakte@dialos.org" wurde "komteakte@teialos.or" - Nordpol als Martha,
    Dora als Theodor, das Gustav am Ende verschluckt.) Das Buchstabieralphabet
    ist gut, aber nicht fehlerfrei; die richtige Schreibweise steht oft schon
    irgendwo: in den eigenen Daten, in den Kontakten, in den Absendern der
    indizierten Mails. Ein Vorschlag daraus ist billiger als ein zweites
    Buchstabieren - und eine Mail an eine erfundene Adresse kommt nie an.
    """
    gefunden = set()
    _, daten = (None, {})
    pd = _modul(PERSOENLICHE_DATEN_SKRIPT, "persoenliche_daten")
    if pd is not None:
        try:
            daten = pd.lesen() or {}
        except Exception:                  # noqa: BLE001 - keine Daten, kein Problem
            daten = {}
    for schluessel in ("mail", "mail_dienstlich"):
        if daten.get(schluessel):
            gefunden.add(daten[schluessel].strip().lower())
    em = _modul(EMPFAENGER_SKRIPT, "dialos_empfaenger")
    if em is not None:
        try:
            for kontakt in em.kontakte():
                if kontakt.get("mail"):
                    gefunden.add(kontakt["mail"].strip().lower())
        except Exception as fehler:        # noqa: BLE001
            melde(f"  Kontakte nicht lesbar: {fehler}")
    try:
        r = subprocess.run([INDEX, "adressen"], capture_output=True, timeout=60)
        for zeile in r.stdout.decode("utf-8", errors="replace").splitlines():
            if "@" in zeile:
                gefunden.add(zeile.strip().lower())
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"  Adressen aus dem Index nicht lesbar: {fehler}")
    return {a for a in gefunden if ADRESSE_GUELTIG.match(a)}


def adresse_pruefen(adresse):
    """Eine bekannte Adresse, die fast so aussieht - oder None.

    DER TEIL VOR DEM AT WIRD NIE ERSETZT (2026-09-21, am Geraet aufgelaufen).
    Stephan buchstabierte "kontakt@dialos.org" - fehlerfrei, das Protokoll
    belegt es. Dann schlug diese Funktion "proband@dialos.org" vor (0,72
    Aehnlichkeit), er sagte ja, und der Entwurf ging an den falschen
    Empfaenger. Der Fehler lag im Entwurf, nicht in der Erkennung: "kontakt@"
    und "proband@" sind ZWEI POSTFAECHER, kein Tippfehler. Eine Hilfe, die aus
    einer richtigen Adresse eine falsche macht, ist schlimmer als keine.

    Deshalb jetzt:
      1. Ist die Domain bekannt, gilt die Adresse als plausibel - kein Vorschlag.
      2. Sonst wird die GANZE Adresse nur bei sehr hoher Aehnlichkeit (0,9)
         vorgeschlagen - das faengt einen verhoerten Buchstaben, nicht ein
         anderes Postfach.
      3. Sonst wird nur die DOMAIN ersetzt, der Teil davor bleibt unangetastet.
    """
    import difflib
    lokal, _, domain = adresse.partition("@")
    bekannte = bekannte_adressen()
    bekannte_domains = {a.partition("@")[2] for a in bekannte}
    if domain in bekannte_domains:
        return None
    beste, bester_wert = None, 0.9
    for bekannt in bekannte:
        if bekannt == adresse:
            return None                    # sie ist schon genau richtig
        wert = difflib.SequenceMatcher(None, adresse, bekannt).ratio()
        if wert > bester_wert:
            beste, bester_wert = bekannt, wert
    if beste:
        melde(f"  aehnliche bekannte Adresse: {beste!r} ({bester_wert:.2f})")
        return beste
    # NUR DIE DOMAIN VERGLEICHEN (2026-09-18): "kontakt@dialos.org" steht
    # nirgends, "dialos.org" dagegen schon. Der Teil hinter dem At ist der, bei
    # dem ein Buchstabierfehler die Mail unzustellbar macht - der Teil davor
    # gehoert dem Nutzer und bleibt, wie er ihn buchstabiert hat.
    beste_domain, wert_domain = None, 0.7
    for bekannt in bekannte_domains:
        wert = difflib.SequenceMatcher(None, domain, bekannt).ratio()
        if wert > wert_domain:
            beste_domain, wert_domain = bekannt, wert
    if beste_domain:
        melde(f"  aehnliche Domain: {beste_domain!r} statt {domain!r} ({wert_domain:.2f})")
        return f"{lokal}@{beste_domain}"
    return None


def adresse_buchstabieren_lassen():
    """Eine Mailadresse Zeichen fuer Zeichen - dieselbe Tabelle wie im Diktat.

    (Stephan, 2026-09-18: "Weiterleiten fertig bauen mit buchstabierter
    Adresse".) Die Kontakte im Adressbuch haben oft keine Mailadresse - beim
    T490 keiner von beiden -, und eine fremde Adresse frei zu sprechen trifft
    kein Erkenner. Buchstabiert wird sie mit dem Buchstabieralphabet plus at,
    Punkt, Minus, Unterstrich und Ziffern; die Tabelle dafuer steht im Diktat
    und wird von dort geholt, nicht abgeschrieben.
    """
    d = _modul(DIKTAT_SKRIPT_MODUL, "dialos_diktat")
    if d is None:
        return ""
    import vosk
    vosk.SetLogLevel(-1)
    if not os.path.isdir(MODELL_KLEIN):
        return ""
    modell_klein = vosk.Model(MODELL_KLEIN)
    prozess = mikrofon_oeffnen()
    try:
        adresse = d.buchstaben_hoeren(prozess, modell_klein,
                                      ansage=d.ANSAGE_MAIL_BUCHSTABIEREN,
                                      zusatz=d.MAIL_ZEICHEN).replace(" ", "").lower()
    except Exception as fehler:            # noqa: BLE001 - auch ein Abbruch
        melde(f"  Buchstabieren abgebrochen: {fehler}")
        return ""
    finally:
        try:
            prozess.terminate()
        except OSError:
            pass
    melde(f"  Adresse buchstabiert: {adresse!r}")
    if not adresse:
        return ""
    if not ADRESSE_GUELTIG.match(adresse):
        # LIEBER NICHTS ALS EINE HALBE ADRESSE: Eine Mail an "stephanguideos.de"
        # kaeme nie an, und der Nutzer erfuehre es erst Tage spaeter.
        sprich("Das ergibt keine Mailadresse. Es fehlt das At-Zeichen oder der Punkt.")
        return ""
    # GEGENLESEN MIT DEM, WAS DAS GERAET SCHON KENNT (2026-09-18): Ein
    # Buchstabierfehler faellt beim Vorlesen kaum auf - "teialos" klingt wie
    # "dialos", wenn man weiss, was gemeint ist. Eine bekannte Adresse, die fast
    # passt, wird deshalb ausdruecklich angeboten.
    vorschlag = adresse_pruefen(adresse)
    if vorschlag and ja_oder_nein(f"Meinst Du {d.mail_vorlesbar(vorschlag)} "
                                  "Sage ja oder nein."):
        return vorschlag
    # VOR DEM AT UND DANACH GETRENNT VORLESEN: Eine Kette aus achtzehn
    # Buchstabierwoertern behaelt niemand im Kopf.
    vorne, _, hinten = adresse.partition("@")
    if ja_oder_nein(f"Vor dem At-Zeichen: {d.buchstabiert(vorne)} "
                    f"Danach: {d.buchstabiert(hinten)} "
                    "Stimmt das? Sage ja oder nein."):
        return adresse
    return ""


def empfaenger_erfragen_fuer_mail(erkenner, modell):
    """An wen weitergeleitet wird - aus den Kontakten oder buchstabiert."""
    em = _modul(EMPFAENGER_SKRIPT, "dialos_empfaenger")
    for _versuch in range(2):
        texte = antwort_hoeren("An wen soll ich weiterleiten? Sage den Namen aus "
                               "Deinen Kontakten, oder sage: buchstabieren.",
                               erkenner, modell)
        if not texte or _abbruch(texte):
            return ""
        if any(re.search(r"(?i)buchstab", t) or _aehnlich(t, "buchstabieren") >= 0.7
               for t in texte):
            # BIS ZU DREI ANLAEUFE: Beim ersten Versuch am Geraet kam
            # "komteakte@teialos.or" heraus - wer dann "nein" sagt, will es noch
            # einmal versuchen und nicht den ganzen Vorgang verlieren.
            for _mal in range(3):
                adresse = adresse_buchstabieren_lassen()
                if adresse:
                    return adresse
                if not ja_oder_nein("Noch einmal buchstabieren? Sage ja oder nein."):
                    return ""
            return ""
        for gesagt in texte:
            for kontakt in (em.suchen(gesagt) if em else []):
                adresse = (kontakt.get("mail") or "").strip()
                name = kontakt.get("name") or kontakt.get("firma") or adresse
                if not adresse:
                    melde(f"  Kontakt {name!r} ohne Mailadresse")
                    continue
                if ja_oder_nein(f"An {name}, {sprechbar(adresse)}. "
                                "Stimmt das? Sage ja oder nein."):
                    return adresse
        # KEIN KONTAKT MIT ADRESSE: Das ist der Normalfall, solange das
        # Adressbuch aus Brief-Empfaengern besteht - dort steht eine Anschrift,
        # keine Mailadresse. Deshalb hier gleich das Buchstabieren anbieten,
        # statt ein zweites Mal nach einem Namen zu fragen.
        if ja_oder_nein("Dazu finde ich keine Mailadresse. Soll ich sie "
                        "buchstabieren lassen? Sage ja oder nein."):
            return adresse_buchstabieren_lassen()
    return ""


def vorlesen(t):
    """Liest den Treffer vor - ab der Anrede."""
    text = text_holen(t)
    if not text:
        sprich("Ich kann den Text nicht vorlesen.")
        return 1
    # AB DER ANREDE VORLESEN (2026-09-18, aus der Simulation): Davor stehen
    # Absender, Anschriftfeld und Informationsblock - bei einem PDF kommen die
    # Spalten beim Extrahieren durcheinander ("Name Stephan Rösner Guide O S").
    # Wer einen Brief sucht, will wissen, was drinsteht, nicht seinen eigenen
    # Briefkopf hoeren. Dieselbe Entscheidung wie bei "Brief vorlesen", wo
    # Stephan am 2026-09-17 den Absender abbestellt hat.
    zeilen = text.splitlines()
    anfang = next((i for i, z in enumerate(zeilen)
                   if re.match(r"(?i)^\s*(sehr geehrt|liebe[rn]?\b|hallo|guten (tag|morgen))",
                               z)), None)
    if anfang is None:
        anfang = next((i for i, z in enumerate(zeilen)
                       if re.match(r"(?i)^\s*betreff", z)), 0)
    zeilen = [z for z in zeilen[anfang:]
              if "powered by DialOS" not in z
              and not z.strip().startswith("Dieser Brief wurde per Spracheingabe")
              and z.strip() != "unterschrieben."]
    melde(f"  vorlesen: {len(' '.join(zeilen))} Zeichen")
    sprich(sprechbar(" ".join(z.strip() for z in zeilen if z.strip())))
    return 0


def vorlesen_anbieten(t, erkenner, modell):
    """Was mit dem Fund geschehen soll - und danach die Frage noch einmal.

    NACH DEM VORLESEN IST NICHT SCHLUSS (Stephan, 2026-09-21: "nach dem
    Vorlesen kommt nix mehr!"). Wer einen Brief gehoert hat, will ihn oft gleich
    drucken, und wer eine Mail gehoert hat, will antworten - das ist der Moment,
    in dem er weiss, was drinsteht. Frueher endete die Suche hier, und der
    Nutzer musste den ganzen Weg noch einmal sprechen. Jetzt fragt DialOS nach
    jeder Handlung erneut, hoechstens viermal, und endet bei "nichts" oder
    Schweigen.
    """
    if not t.get("erreichbar"):
        sprich("Diese Datei liegt im Archiv, das gerade nicht angeschlossen ist.")
        return 0
    ist_mail = t.get("art") == "Mail"
    moeglich = ("vorlesen, drucken, antworten, weiterleiten oder nichts"
                if ist_mail else "vorlesen, drucken oder nichts")
    ergebnis = 0
    for runde in range(4):
        if runde == 0:
            frage = (f"Es bleibt: {treffer_nennen(t)}. Was soll ich damit tun? "
                     f"Sage: {moeglich}.")
        else:
            frage = f"Noch etwas damit? Sage: {moeglich}."
        texte = antwort_hoeren(frage, erkenner, modell)
        wahl = None
        for text in texte or []:
            for wort in text.lower().split():
                wahl = wahl or WAHL_WORTE.get(wort.strip(".,!?"))
        if wahl is None and texte:
            for wort, ziel in WAHL_WORTE.items():
                if any(_aehnlich(text, wort) >= 0.7 for text in texte):
                    wahl = ziel
                    break
        melde(f"  Wahl: {wahl!r} aus {texte!r}")
        if wahl is None or wahl == "nichts":
            sprich("Gut, ich lasse es." if runde == 0 else "Gut.")
            return ergebnis
        if wahl == "drucken":
            ergebnis = drucken_treffer(t, erkenner, modell)
        elif wahl in ("antworten", "weiterleiten"):
            if not ist_mail:
                sprich("Antworten kann ich nur bei einer E-Mail.")
                continue
            ergebnis = antworten_auf(t, erkenner, modell,
                                     weiterleiten=(wahl == "weiterleiten"))
        else:
            ergebnis = vorlesen(t)
    return ergebnis


def bereich_erfragen(erkenner, modell):
    """Welcher Bereich - Dokumente oder Postfach. Arten-Tupel oder None."""
    for _versuch in range(2):
        texte, gesprochen = antwort_hoeren(ANSAGE_BEREICH, erkenner, modell, mit_pegel=True)
        if _abbruch(texte):
            return None
        worte = [w.strip(".,!?").lower() for text in texte for w in text.split()]
        for wort in worte:
            if wort in NOCH_NICHT:
                sprich(ANSAGE_NOCH_NICHT_BEREICH)
                return None
            if wort in BEREICHE:
                melde(f"  Bereich: {BEREICHE[wort]}")
                return BEREICHE[wort]
        # Klang und Aehnlichkeit wie bei der Art - "Postfach" kam als "Hostwa" an.
        arten = {a for arten in BEREICHE.values() for a in arten}
        art = art_aus_antwort(texte, arten)
        if art:
            return ("Mail",) if art == "Mail" else ("Brief", "Notiz", "Ablage")
        if not gesprochen:
            sprich("Ich höre nichts mehr. Die Suche ist beendet.")
            return None
        sprich("Das habe ich nicht verstanden.")
    return None


def suchen(begriffe, erkenner=None, modell=None, arten=None):
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
        if arten:
            gefunden = [x for x in gefunden if x.get("art") in arten]
        melde(f"  {len(gefunden)} Treffer fuer {versuch!r}")
        if gefunden:
            begriff, treffer = versuch, gefunden
            break
    if not treffer:
        sprich(f"Zu {begriff} habe ich nichts gefunden.")
        return 0

    nur_klang = all(x.get("wie") == "klang" for x in treffer)
    klang = " Die Schreibweise klingt nur ähnlich." if nur_klang else ""
    if len(treffer) == 1:
        sprich(f"Ich habe einen Treffer zu {begriff}.{klang}")
        return vorlesen_anbieten(treffer[0], erkenner, modell)

    # SCHRITT FUER SCHRITT EINGRENZEN (Stephan, 2026-09-18: "so aufbauen, dass
    # man Schritt fuer Schritt die Treffer verkleinert, bis nur noch eine Datei
    # uebrig bleibt"). Erst die Zahl, dann Fragen nach Jahr, Art und Person -
    # und nur nach dem, was die Treffer wirklich auseinanderhaelt.
    sprich(f"Ich habe {len(treffer)} Treffer zu {begriff}.{klang}")
    if erkenner is None and modell is None:
        return 0
    treffer = eingrenzen(treffer, erkenner, modell)
    if not treffer:
        sprich("Gut, ich höre auf zu suchen.")
        return 0
    # Bis zu drei weitere Woerter: Jedes schneidet, und wer aufhoeren will, sagt
    # "aufzaehlen" - dann kommt die Liste.
    for _runde in range(3):
        if len(treffer) <= 1:
            break
        enger = mit_wort_eingrenzen(treffer, erkenner, modell)
        if enger is treffer or len(enger) == len(treffer):
            treffer = enger
            break
        treffer = enger
    if len(treffer) == 1:
        return vorlesen_anbieten(treffer[0], erkenner, modell)

    # MEHR ALS EINER BLEIBT UEBRIG: Dann wird nicht weitergefragt, sondern
    # aufgezaehlt - hoechstens drei, nach Datum. Wer bis hierher gekommen ist,
    # hat vier Fragen beantwortet; eine fuenfte waere Quaelerei.
    sprich(f"Es bleiben {len(treffer)} Treffer. Die neuesten sind: "
           + ". ".join(treffer_nennen(t) for t in treffer[:3]) + ".")
    texte = antwort_hoeren("Welchen soll ich vorlesen? Sage: den ersten, den zweiten "
                           "oder den dritten. Oder sage: keinen.", erkenner, modell)
    for text in texte or []:
        for wort in text.lower().split():
            nummer = ORDNUNGSZAHLEN.get(wort.strip(".,"))
            if nummer is not None and nummer < min(3, len(treffer)):
                return vorlesen_anbieten(treffer[nummer], erkenner, modell)
    sprich("Gut, ich lese nichts vor.")
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
        arten = bereich_erfragen(erkenner, modell)
        if arten is None:
            return 0
        frage = ANSAGE_BEGRIFF["postfach" if arten == ("Mail",) else "dokumente"]
        begriffe = antwort_hoeren(frage, erkenner, modell)
        melde(f"  verstanden: {begriffe!r}")
        if not begriffe:
            sprich(ANSAGE_NICHTS)
            return 0
        if _abbruch(begriffe):
            sprich("Gut, ich suche nicht.")
            return 0
        return suchen(begriffe, erkenner, modell, arten)
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        # EIN ABSTURZ DARF NICHT STILL SEIN (2026-09-21, Stephan: "Nach Punkt 1
        # kommt keine Sprachausgabe mehr"). Eine fehlende Funktion liess die
        # Erweiterung sofort enden; im Protokoll stand nur "beendet", gesagt
        # wurde gar nichts - und wer den Bildschirm nicht sieht, steht vor einem
        # Geraet, das schweigt. Jetzt steht der ganze Fehler im Protokoll, und
        # der Nutzer hoert, dass etwas schiefging.
        import traceback
        melde("ABSTURZ: " + traceback.format_exc().strip().replace("\n", " | "))
        sprich("Bei der Suche ist etwas schiefgegangen. Ich höre wieder zu.")
        return 1
    finally:
        try:
            os.unlink(MARKE)
        except OSError:
            pass
        melde("=== beendet, Mikrofon zurueckgegeben ===")


if __name__ == "__main__":
    sys.exit(main())
