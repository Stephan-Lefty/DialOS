#!/usr/bin/env python3
"""DialOS: Notizen vorlesen und leeren.

Stephans Frage vom 2026-08-18: "Wenn ich heute was in den Einkaufszettel
schreibe, wie kann ich den jederzeit abhoeren, ergaenzen und wenn der
Einkauf zuhause ist loeschen?" Damit war klar, dass "aufnehmen" allein zu
wenig ist - ein Einkaufszettel wird gelesen, ergaenzt und irgendwann
weggeworfen.

Die drei Teile verteilen sich so:

  ergaenzen   braucht kein neues Programm. "Einkaufszettel aufnehmen"
              schreibt an die Datei AN, nicht darueber (dialos-diktat.py,
              notiz_schreiben oeffnet mit "a").
  vorlesen    dieses Skript, Unterbefehl "vorlesen".
  leeren      dieses Skript, Unterbefehl "loeschen" - mit Rueckfrage.

WARUM EINE RUECKFRAGE VOR DEM LEEREN: Die Regel steht in
docs/sprachbefehle.md und stammt nicht von hier - sicherheitskritische
Befehle bekommen eine Ja/Nein-Rueckfrage, unabhaengig davon, wie sicher die
Erkennung war. Ein Einkaufszettel ist nicht sicherheitskritisch, aber der
Verlust ist unumkehrbar und die Arbeit war Sprechen: Wer zwanzig Dinge
diktiert hat und sie durch ein missverstandenes Wort verliert, diktiert sie
nicht gern noch einmal.

UND EIN NETZ DAHINTER: Der alte Inhalt wandert beim Leeren nach
"<name>-verworfen.txt". Fuer den Nutzer ist der Zettel weg - das ist die
Ansage und das Verhalten. Aber ein sehender Helfer kann ihn im Notfall
zurueckholen. Es kostet nichts und deckt genau den Fall ab, den eine
Rueckfrage nicht abdeckt: dass der Nutzer "ja" sagt und es hinterher
bedauert.

RUECKFRAGE AUCH VOR DRUCKEN UND DIKTAT (seit 2026-09-14, Stephans Vorgabe
"Bau eine Rueckfrage vor Drucken und Diktat ein"). Anlass: In Stephans Pause
hat ein Gespraech im Raum die Sprachsteuerung eingeschaltet und daraus
"diktat brief schreiben" und dreimal "... drucken" gemacht - 97 Sekunden
Gespraech wurden als Brief geschrieben, ins Archiv gelegt und zweimal
ausgedruckt. Die Loeschfrage hat an dem Tag als einzige gehalten. Deshalb
laufen Drucken und Diktat jetzt ueber dieses Skript und dieselbe Frage; der
Befehlsdienst startet sie nicht mehr selbst. Einzelheiten in TODO.md.

Aufruf:
    dialos-notiz.py einkaufszettel vorlesen
    dialos-notiz.py einkaufszettel loeschen
    dialos-notiz.py brief drucken      Rueckfrage, dann dialos-drucken.py
    dialos-notiz.py brief diktat       Rueckfrage, dann dialos-diktat.py
    dialos-notiz.py brief pdf          PDF neben den neuesten Brief, ohne Rueckfrage
    dialos-notiz.py --debug ...
"""

import collections
import json
import os
import re
import subprocess
import sys
import threading
import time

MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
SAY = "/usr/local/bin/dialos-say.py"
ECHO_QUELLE = "dialos_mikrofon_ohne_echo"
NOTIZ_ORDNER = os.path.join(os.path.expanduser("~"), "Notizen")
DOKUMENT_ORDNER = os.path.join(os.path.expanduser("~"), "Dokumente")
BRIEF_ZIELE = ("brief",)
FUSSZEILE_SKRIPT = "/usr/local/bin/dialos-fusszeile.py"

# Wie die Notiz in einem Satz heisst. Ohne diese Tabelle entstehen falsche
# Saetze, weil der Dateiname in den Satz eingebaut wird: "Der einkaufszettel
# hat 10 Eintraege" (klein) und - schlimmer - "Der notizen ist leer",
# falsches Geschlecht und falscher Numerus.
#
# Fuer einen Nutzer, der ausschliesslich zuhoert, ist die Ansage der ganze
# Text, den er von DialOS bekommt. Ein falscher Artikel ist dort kein
# Schoenheitsfehler, sondern der Unterschied zwischen einem Programm, das
# spricht, und einem, das Platzhalter vorliest.
#
# (Bezeichnung, Verb im Singular/Plural, Personalpronomen im Akkusativ)
BEZEICHNUNG = {
    "einkaufszettel": ("Der Einkaufszettel", "ist", "hat", "ihn"),
    "notizen": ("Die Notizen", "sind", "haben", "sie"),
    "brief": ("Der Brief", "ist", "hat", "ihn"),
}


def benennen(name):
    """Gibt (Bezeichnung, ist/sind, hat/haben, ihn/sie) zurueck.

    Unbekannte Namen bekommen eine neutrale Form, die immer aufgeht - besser
    ein etwas steifer Satz als ein falscher.
    """
    return BEZEICHNUNG.get(name, (f"Die Notiz {name}", "ist", "hat", "sie"))


def marke_pfad(name):
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


# DIESELBE Marke wie beim Diktat, mit Absicht. Sie bedeutet nicht "ein
# Diktat laeuft", sondern "ein anderer Dienst hoert gerade zu" - und die
# Rueckfrage vor dem Leeren tut genau das. Ohne sie wuerde der
# Befehlsdienst waehrend der Frage mithoeren und ein "ja" oder "nein"
# irgendwo einordnen.
#
# Zwei Marken mit derselben Bedeutung waeren die schlechtere Wahl: Der
# Befehlsdienst muesste beide kennen, und wer eine dritte Stelle baut,
# vergisst die zweite.
FREMDE_AUFNAHME_MARKE = marke_pfad("dialos-diktat-aktiv")
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-notiz.log")

DEBUG = "--debug" in sys.argv

# Grammatik der Rueckfrage. Winzig, und genau darum verlaesslich - dasselbe
# Prinzip wie bei der Befehlserkennung und beim Schlusssatz des Diktats.
# ensure_ascii=False IST PFLICHT (Fehler gefunden 2026-09-14). Ohne das schreibt
# json.dumps ein "ö" als "\\u00f6", Vosk liest das woertlich und meldet
# "Ignoring word missing in vocabulary" - fuer JEDES Wort mit Umlaut oder ß.
# Genau daraus entstanden die Befunde "spaeter", "loeschen", "zuruecksetzen"
# und "aufraeumen fehlen im Wortschatz". Sie fehlen nicht.
GRAMMATIK_JA_NEIN = json.dumps(["ja", "nein", "[unk]"], ensure_ascii=False)
ANTWORT_ZEITGRENZE_S = 8.0

# Zweiter Versuch, wenn die erste Antwort nicht ankam (Stephan, 2026-08-19: sein
# "ja" wurde nicht verstanden). Ohne ihn muesste der Nutzer den ganzen Befehl
# neu sprechen, obwohl nur ein Wort gefehlt hat.
ANSAGE_NOCHMAL = "Das habe ich nicht verstanden. Sage ja oder nein."
VERSUCHE = 2


# WARUM IN EINEM VERSTECKTEN ORDNER (Stephan, 2026-08-22): Vorher lagen die
# Protokolle offen im Heimatverzeichnis - zehn laufende und fuenfzehn gedrehte
# Fassungen, also 25 Dateien zwischen "Notizen", "Dokumente" und "Bilder". Der
# Nutzer sieht sie nicht, aber ein sehender Helfer sucht dazwischen. In "~/.log"
# stoeren sie niemanden und sind trotzdem da, wo man sie vermutet.
#
# Der Ordner wird beim Schreiben angelegt, nicht vorausgesetzt: Ein neues Konto
# hat ihn noch nicht, und ein fehlendes Protokoll darf keine Ansage aufhalten.
def melde(text):
    if DEBUG:
        print(text, flush=True)
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text, frage=False):
    if not os.access(SAY, os.X_OK):
        print(text)
        return
    befehl = [SAY] + (["--frage"] if frage else []) + [text]
    subprocess.run(befehl, capture_output=True, timeout=120)


DATEINAME_SKRIPT = "/usr/local/bin/dialos-dateiname.py"


def brief_pfad():
    """Der neueste Brief ("2026-09-15-1343-Brief.txt"), sonst ein Pfad, den es nicht gibt.

    Seit 2026-09-15 behaelt jeder Brief seinen Namen mit Datum und Uhrzeit;
    "der Brief" ist der juengste. Die Regel steht in dialos-dateiname.py.
    Gibt es keinen, kommt ein nicht vorhandener Pfad zurueck - alle Aufrufer
    behandeln das schon als "leer".
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dateiname", DATEINAME_SKRIPT)
        namen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(namen)
        return namen.neuester(DOKUMENT_ORDNER, namen.BRIEF, "txt") or \
            os.path.join(DOKUMENT_ORDNER, "kein-Brief.txt")
    except Exception as fehler:
        melde(f"  dialos-dateiname.py nicht nutzbar: {fehler}")
        return os.path.join(DOKUMENT_ORDNER, "kein-Brief.txt")


def pfad_fuer(name):
    sicher = re.sub(r"[^\w -]", "", name).strip() or "notizen"
    # Der Brief liegt bei den Dokumenten, nicht bei den Notizen - er ist ein
    # fertiges Stueck und kein Arbeitszettel. Geschrieben wird er von
    # dialos-diktat.py, gelesen hier; beide muessen denselben Ort meinen.
    if sicher in BRIEF_ZIELE:
        return brief_pfad()
    return os.path.join(NOTIZ_ORDNER, sicher + ".txt")


def eintraege_lesen(name):
    try:
        with open(pfad_fuer(name), encoding="utf-8") as f:
            return [z.strip() for z in f if z.strip()]
    except OSError:
        return []


def aufzaehlen(zeilen):
    """Wie in dialos-diktat.py: Punkt statt Komma zwischen den Eintraegen.

    Der Punkt ist Absicht. Piper macht daran eine deutlichere Pause, und die
    braucht der Zuhoerer, um mitzuzaehlen. Ohne Satzzeichen hetzt es durch -
    gemessen 3,670 s gegen 4,884 s fuer dieselbe Liste (2026-08-18).
    """
    saubern = lambda z: z.rstrip(" .,;:")
    return " ".join(saubern(z) + "." for z in zeilen if saubern(z))


def waehle_mikrofon():
    try:
        roh = subprocess.run(["pactl", "-f", "json", "list", "sources"],
                             capture_output=True, text=True, timeout=5).stdout
        quellen = json.loads(roh) if roh.strip() else []
    except Exception:
        return None
    namen = [q.get("name", "") for q in quellen
             if q.get("name") and not q["name"].endswith(".monitor")]
    if ECHO_QUELLE in namen:
        return ECHO_QUELLE
    eingebaut = [n for n in namen if n.startswith("alsa_input.pci-")]
    return eingebaut[0] if eingebaut else None


NAMEN_SKRIPT = "/usr/local/bin/dialos-namen.py"


def anrede(satz):
    """Stellt den Nutzernamen voran, wo es Sinn macht - siehe dialos-namen.py.

    Geholt statt kopiert: Die Regel, WANN ein Name benutzt wird, gehoert an eine
    Stelle. Faellt das Modul aus, kommt der Satz unveraendert zurueck - eine
    Ansage darf nie davon abhaengen, dass ein Name eingetragen ist.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dialos_namen", NAMEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.anrede(satz)
    except Exception:
        return satz


def ja_oder_nein(frage):
    """Frage stellen und die Antwort hoeren. True, False oder None.

    None heisst "nichts Passendes verstanden" und ist bewusst von False
    getrennt: Bei None bleibt der Zettel stehen UND der Nutzer erfaehrt, dass
    nichts verstanden wurde. Ein stilles Nichtstun waere fuer ihn nicht von
    einem stillen Loeschen zu unterscheiden.

    DIE FRAGE WIRD HIER GESTELLT UND NICHT VOM AUFRUFER - das war der Fehler
    vom 2026-08-19. Vorher sprach der Aufrufer die Frage und rief danach diese
    Funktion, die erst DANN das Sprachmodell lud (rund eine Sekunde) und
    anschliessend die Aufnahme startete. Stephans "ja" fiel genau in diese
    Luecke: im Protokoll stand keine einzige "Antwort gehoert"-Zeile, weil zum
    Zeitpunkt des Sprechens noch nichts aufnahm. Dieselbe Fehlerklasse wie am
    2026-08-18 beim Diktat und am 2026-08-15 bei der Start-Ansage - deshalb
    liegt das Vorbereiten jetzt zwingend VOR der Frage, und zwar dadurch, dass
    die Funktion beides selbst in der Hand hat.

    AUSGEWERTET wird bewusst NICHT waehrend der Frage. Die Grammatik kennt nur
    "ja", "nein" und "[unk]" - die eigene Stimme des Systems koennte darin als
    "ja" landen, und das wuerde den Zettel loeschen, ohne dass jemand etwas
    gesagt hat. Ein Loeschen ohne Zustimmung ist der schlimmere Fehler.

    AUFGENOMMEN wird seit 2026-09-14 schon waehrend der Frage - und verworfen,
    bis auf die letzten VORLAUF_S. Siehe _sprechen_bei_offenem_mikrofon().
    Geprueft am ROHEN Laptop-Mikrofon ohne Echo-Unterdrueckung, also im
    schlimmsten Fall: Frage mit sofort abgespieltem "nein" -> beim ersten
    Versuch erkannt; Frage ohne Antwort, zweimal gestellt -> beide Male nichts
    erkannt, obwohl das Mikrofon Annas "ja oder nein" laut gehoert hat.
    """
    bereit = _antwort_vorbereiten()
    if not bereit:
        return None
    modell, quelle = bereit
    for versuch in range(1, VERSUCHE + 1):
        prozess = _mikrofon_oeffnen(quelle)
        vorrat = _sprechen_bei_offenem_mikrofon(
            frage if versuch == 1 else ANSAGE_NOCHMAL, prozess)
        antwort = _antwort_hoeren(modell, prozess, vorrat)
        if antwort is not None:
            return antwort
        melde(f"  Versuch {versuch} von {VERSUCHE}: keine verwertbare Antwort")
    return None


def _antwort_vorbereiten():
    """Sprachmodell und Mikrofon - alles Langsame VOR der Frage."""
    try:
        import vosk
    except ImportError:
        melde("  vosk fehlt - keine Rueckfrage moeglich")
        return None
    quelle = waehle_mikrofon()
    if not quelle:
        melde("  kein Mikrofon - keine Rueckfrage moeglich")
        return None
    vosk.SetLogLevel(-1)
    t0 = time.time()
    modell = vosk.Model(MODELL_KLEIN)
    melde(f"  Antwort-Erkenner bereit in {time.time()-t0:.1f} s")
    return modell, quelle


# "--latency-msec=30" (2026-09-14): Ohne die Angabe puffert parec rund ZWEI
# SEKUNDEN, bevor der erste Block ankommt - gemessen 2,03 s gegen 0,10 s mit
# 30 ms. Verloren geht dabei nichts, aber jede Reaktion kommt zwei Sekunden zu
# spaet, und ein Zeitfenster, das beim Start des Prozesses zu zaehlen beginnt,
# ist in Wahrheit zwei Sekunden kuerzer.
def _mikrofon_oeffnen(quelle):
    return subprocess.Popen(
        ["parec", "-d", quelle, "--format=s16le",
         f"--rate={ABTASTRATE}", "--channels=1", "--latency-msec=30"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


# DAS MIKROFON IST SCHON OFFEN, WAEHREND DIE FRAGE GESTELLT WIRD (2026-09-14).
#
# Stephan nach dem ersten Test der Rueckfrage vor Drucken und Diktat: "Kann es
# sein, dass zwischen den Fragen ... und der Aufnahmemoeglichkeit gefuehlt 5
# Sekunden liegen. Ich musste zwei mal nein und zweimal ja sagen." Gemessen:
# Die Frage klingt 3,5 s, danach 0,7 s Stille (die Satzpause steht auch hinter
# dem letzten Satz), und erst DANN wurde parec gestartet - das seine ersten
# Daten weitere 2,0 s spaeter lieferte. Wer direkt nach "ja oder nein"
# antwortete, sprach ins Leere; der Anfang seines Worts fehlte, und es kam
# "nicht verstanden".
#
# Jetzt laeuft die Aufnahme schon waehrend der Frage mit, wird aber VERWORFEN.
# Ausgewertet wird ab VORLAUF_S vor dem Ende der Ansage - das liegt noch in
# der Stille hinter der letzten Silbe. Die eigene Stimme bleibt damit weiter
# draussen, und das ist hier nicht verhandelbar: Die Frage ENDET auf "ja oder
# nein". Warum das zaehlt, steht bei ja_oder_nein().
VORLAUF_S = 0.3


def _sprechen_bei_offenem_mikrofon(text, prozess):
    """Spricht die Frage und liest dabei mit. Gibt die letzten VORLAUF_S zurueck.

    Gelesen werden MUSS waehrend der Ansage: Liest niemand, laeuft der Puffer
    der Pipe nach rund zwei Sekunden voll, und parec verliert Daten.
    """
    fertig = threading.Event()

    def ansage():
        try:
            sprich(text, frage=True)
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


def _antwort_hoeren(modell, prozess, vorrat=b""):
    """Einmal zuhoeren. True, False oder None."""
    import vosk
    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_JA_NEIN)
    # Die Zeitgrenze zaehlt ab JETZT - ab dem Moment, ab dem wirklich
    # ausgewertet wird, nicht ab dem Start der Aufnahme.
    ende = time.time() + ANTWORT_ZEITGRENZE_S
    try:
        while time.time() < ende:
            if vorrat:
                block, vorrat = vorrat[:4000], vorrat[4000:]
            else:
                block = prozess.stdout.read(4000)
            if not block:
                break
            if not erkenner.AcceptWaveform(block):
                continue
            gehoert = json.loads(erkenner.Result()).get("text", "").strip()
            if not gehoert:
                continue
            melde(f"  Antwort gehoert: {gehoert!r}")
            worte = gehoert.split()
            if "[unk]" in worte:
                continue            # es wurde noch etwas anderes gesagt
            if "ja" in worte and "nein" not in worte:
                return True
            if "nein" in worte:
                return False
    finally:
        try:
            prozess.terminate()
        except Exception:
            pass
    return None


# ------------------------------------------------------------ Unterbefehle

UNTERSCHRIFT_HINWEIS_ANFANG = "Dieser Brief wurde per Spracheingabe erstellt"


def ohne_unterschrift_hinweis(text):
    """Schneidet den Hinweis (mit seiner umgebrochenen Fortsetzung) am Briefende ab."""
    for i, zeile in enumerate(text):
        if zeile.startswith(UNTERSCHRIFT_HINWEIS_ANFANG):
            text = text[:i]
            break
    while text and not text[-1]:
        text.pop()
    return text


def briefteile(pfad):
    """Zerlegt den Briefbogen in Kopf, Text und Fusszeile.

    WIE UNTERSCHIEDEN WIRD: Kopf und Fusszeile sind rechtsbuendig, stehen also
    mit Leerzeichen am Zeilenanfang; der diktierte Text ist linksbuendig und
    auf dieselbe Breite umgebrochen. Das ist keine Schaetzung, sondern die
    Regel, nach der dialos-diktat.py die Datei BAUT - wer dort etwas aendert,
    muss hier mitaendern. Der Hinweis steht deshalb an beiden Stellen.
    """
    try:
        with open(pfad, encoding="utf-8") as f:
            zeilen = f.read().split("\n")
    except OSError:
        return [], [], []
    eingerueckt = [bool(z) and z.startswith(" ") for z in zeilen]
    kopf, text, fuss = [], [], []
    # EMPFAENGER (seit 2026-09-17): linksbuendige Zeilen VOR der rechtsbuendigen
    # Datumszeile. Sie gehoeren nicht zum Text - sonst zaehlten sie als Saetze.
    datum = next((i for i, (z, r) in enumerate(zip(zeilen, eingerueckt))
                  if r and re.search(r"\b\d{1,2}\. \w+ \d{4}\s*$", z)), None)
    empfaenger = []
    if datum is not None:
        for zeile, rechts in zip(zeilen[:datum + 1], eingerueckt[:datum + 1]):
            if rechts:
                kopf.append(zeile.strip())
            elif zeile.strip():
                empfaenger.append(zeile.strip())
        zeilen, eingerueckt = zeilen[datum + 1:], eingerueckt[datum + 1:]
    briefteile.empfaenger = empfaenger
    gesehen_text = False
    for zeile, rechts in zip(zeilen, eingerueckt):
        if rechts:
            (fuss if gesehen_text else kopf).append(zeile.strip())
        elif zeile.strip():
            gesehen_text = True
            text.append(zeile.strip())
        elif gesehen_text:
            text.append("")
    while text and not text[-1]:
        text.pop()
    return kopf, text, fuss


def vorlesen(name):
    """Weiche: ein Brief wird anders vorgelesen als ein Zettel."""
    if name in BRIEF_ZIELE:
        return brief_vorlesen(name)
    return _vorlesen_liste(name)


DIKTAT_MODUL = "/usr/local/bin/dialos-diktat.py"


def saetze_zaehlen(fliesstext):
    """Saetze wie beim Diktat gezaehlt - "12." und "Dr." beenden keinen Satz.

    Geholt aus dialos-diktat.py (satzenden), nicht nachgebaut: Am 2026-09-15
    sagte das Diktat "8 Saetze" und das Vorlesen desselben Briefs "10 Saetze",
    weil hier jeder Punkt zaehlte. Zwei Zaehlweisen fuer denselben Brief sind
    fuer einen blinden Nutzer eine falsche Auskunft.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("diktat_geholt", DIKTAT_MODUL)
        diktat = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(diktat)
        stellen = [i for i in diktat.satzenden(fliesstext) if fliesstext[i] != "\n"]
        teile, anfang = [], 0
        for i in stellen:
            teile.append(fliesstext[anfang:i + 1])
            anfang = i + 1
        teile.append(fliesstext[anfang:])
        return [t for t in teile if t.strip()]
    except Exception:
        return [s for s in re.split(r"(?<=[.!?])\s+", fliesstext) if s.strip()]


def brief_vorlesen(name):
    """Liest den Brief am Stueck vor - mit benannten Teilen, ohne Fusszeile und Hinweis.

    SEIT 2026-09-17 OHNE FUSSZEILE UND UNTERSCHRIFT-HINWEIS (siehe unten). Kopf und
    Text bleiben ganz, aus dem Grund von damals - Stephans Einwand vom 2026-08-21: "Es sollte immer alles
    vorgelesen werden oder?" Der erste Entwurf liess Kopf und Fusszeile weg,
    weil sie sich bei jedem Hoeren wiederholen. Das war zu kurz gedacht - was
    der Nutzer nicht hoert, existiert fuer ihn nicht. Steht im Absender ein
    falscher Name oder ein falsches Datum, faellt es sonst nie auf.

    BENANNT, damit das Datum nicht wie ein Satz im Brief klingt. Ein Brief ist
    kein Zettel: "Vier Eintraege" waere hier eine falsche Auskunft, und Pausen
    zwischen den Saetzen wie beim Einkaufszettel zerhackten den Text.
    """
    pfad = pfad_fuer(name)
    kopf, text, fuss = briefteile(pfad)
    text = ohne_unterschrift_hinweis(text)
    bez, ist, _hat, _ihn = benennen(name)
    if not text:
        sprich(f"{bez} {ist} leer.")
        return 0
    fliesstext = " ".join(z for z in text if z)
    saetze = saetze_zaehlen(fliesstext)

    teile = ["Ein Satz." if len(saetze) == 1 else f"{len(saetze)} Sätze."]
    if kopf:
        # Die letzte Kopfzeile ist das Datum (so baut dialos-diktat.py sie).
        # DER ABSENDER WIRD NICHT MEHR VORGELESEN (Stephan, 2026-09-17: "Meine
        # Absenderadresse ist ja auch immer fix und muss nicht vorgelesen
        # werden"). Er kommt seit dem 16.09. aus den persoenlichen Daten und nicht
        # aus der Erkennung - pruefen muss man ihn einmal in der Eingabemaske,
        # nicht bei jedem Brief.
        if getattr(briefteile, "empfaenger", None):
            teile.append("Empfänger: " + ", ".join(briefteile.empfaenger) + ".")
        teile.append("Datum: " + kopf[-1] + ".")
    teile.append(fliesstext if re.search(r"[.!?]$", fliesstext) else fliesstext + ".")
    # FUSSZEILE UND UNTERSCHRIFT-HINWEIS WERDEN NICHT MEHR VORGELESEN (Stephan,
    # 2026-09-17: "Das ist ja eher eine Info fuer den Empfaenger und brauche ich
    # nicht fuer die Kontrolle"). Beides steht weiter im Brief, im PDF und auf dem
    # Ausdruck - es aendert sich nie und ist beim Kontrollhoeren nur Laenge. Der
    # Hinweis zaehlte ausserdem als Satz mit: "9 Saetze" fuer einen Brief mit 8.
    # NACH DEM VORLESEN DIE NAECHSTEN SCHRITTE (Stephan, 2026-09-17: "nach dem
    # Vorlesen muss die Option des Druckens und der PDF kommen").
    teile.append("Du kannst sagen: Brief drucken oder Brief als PDF speichern.")
    melde(f"  vorlesen: Brief mit {len(saetze)} Saetzen aus {pfad}")
    sprich(mail_vorlesbar(telefon_vorlesbar(" ".join(teile))))
    return 0


# TELEFONNUMMERN IN DREIERBLOECKEN (Stephan, 2026-09-17). Als Zahl gesprochen wird
# aus "664 1234567" "sechshundertvierundsechzig eine Million ..." - zum
# Mitschreiben unbrauchbar. Jede Ziffer einzeln, je drei zusammen, mit Satzpause
# dazwischen: Nur Satzzeichen erzeugen bei Piper hoerbare Pausen (gemessen
# 2026-08-24: Punkt 220 ms, Komma 0 ms). Erkannt wird eine Nummer an "+" oder
# "0" am Anfang und mindestens sechs Ziffern.
TELEFON = re.compile(r"(?<![\w.,])(\+|00?)(\d[\d /-]{4,}\d)(?![\w.,]\d)")


MAILADRESSE = re.compile(r"\b([\w.+-]+)@([\w-]+(?:\.[\w-]+)+)")


def mail_vorlesbar(text):
    """"stephan@beispiel.de" -> "stephan at beispiel Punkt de" (2026-09-17).

    Piper liest das @ sonst nicht oder als Fremdwort, und der Punkt in der Adresse
    klaenge wie ein Satzende. Zur Kontrolle der Schreibweise gibt es beim
    Buchstabieren im Diktat die Rueckfrage Zeichen fuer Zeichen.
    """
    def lesbar(teil):
        return (teil.replace(".", " Punkt ").replace("-", " Minus ")
                .replace("_", " Unterstrich ").replace("  ", " ").strip())
    return MAILADRESSE.sub(lambda m: f"{lesbar(m.group(1))} at {lesbar(m.group(2))}", text)


def telefon_vorlesbar(text):
    """"+43 664 1234567" -> "plus 4 3. 6 6 4. 1 2 3. 4 5 6. 7."

    Laendervorwahl und Ortsvorwahl bleiben je ein Block, so wie sie geschrieben
    sind; die Rufnummer danach in Dreierbloecken.
    """
    def bloecke(m):
        vorne, rest = m.group(1), m.group(2)
        if len(re.sub(r"\D", "", vorne + rest)) < 6:
            return m.group(0)
        teile = [t for t in re.split(r"[ /-]+", rest) if t]
        if vorne != "+":
            teile[0] = vorne + teile[0]
        feste = []
        if vorne == "+" and len(teile) == 1 and len(teile[0]) > 6:
            # "+436933011151" ohne Leerzeichen: Laendervorwahl zweistellig (43, 49, 41)
            teile = [teile[0][:2], teile[0][2:]]
        if vorne == "+" or vorne == "00":
            feste.append(teile.pop(0))          # Laendervorwahl
        if len(teile) > 1 and len(teile[0]) <= 5:
            feste.append(teile.pop(0))          # Ortsvorwahl
        nummer = "".join(teile)
        gruppen = feste + [nummer[i:i + 3] for i in range(0, len(nummer), 3)]
        gesprochen = ". ".join(" ".join(g) for g in gruppen if g)
        return ("plus " if vorne == "+" else "") + gesprochen + "."
    return re.sub(r"\.\.", ".", TELEFON.sub(bloecke, text))


def _vorlesen_liste(name):
    eintraege = eintraege_lesen(name)
    bez, ist, _hat, _ihn = benennen(name)
    if not eintraege:
        sprich(f"{bez} {ist} leer.")
        return 0
    # Anzahl VORAN, damit der Nutzer weiss, was auf ihn zukommt - bei zwanzig
    # Eintraegen ist das der Unterschied zwischen Zuhoeren und Abwarten.
    zahl = len(eintraege)
    kopf = "Ein Eintrag." if zahl == 1 else f"{zahl} Einträge."
    melde(f"  vorlesen: {zahl} Eintraege aus {pfad_fuer(name)}")
    sprich(f"{kopf} {aufzaehlen(eintraege)}")
    return 0


def loeschen(name):
    # Marke fuer die Dauer der Rueckfrage - siehe FREMDE_AUFNAHME_MARKE.
    open(FREMDE_AUFNAHME_MARKE, "w").close()
    try:
        return _loeschen(name)
    finally:
        try:
            os.unlink(FREMDE_AUFNAHME_MARKE)
        except OSError:
            pass


def _loeschen(name):
    eintraege = eintraege_lesen(name)
    bez, ist, hat, ihn = benennen(name)
    if not eintraege:
        sprich(f"{bez} {ist} schon leer.")
        return 0
    zahl = len(eintraege)
    was = "einen Eintrag" if zahl == 1 else f"{zahl} Einträge"
    # "Sage ja oder nein." gehoert in die Frage (Stephan, 2026-08-19). Der
    # Nutzer sieht keine Knoepfe; welche Woerter erwartet werden, muss gesagt
    # werden - dieselbe Regel wie bei der Anleitung zum Einkaufszettel.
    # MIT Namen: Hier wird etwas geloescht.
    antwort = ja_oder_nein(
        anrede(f"{bez} {hat} {was}. Soll ich {ihn} löschen? Sage ja oder nein."))
    if antwort is None:
        sprich(f"Ich habe nichts verstanden. Ich lasse {ihn} stehen.")
        return 0
    if antwort is False:
        sprich(f"Gut, ich lasse {ihn} stehen.")
        return 0

    # Netz: Inhalt beiseitelegen, statt ihn wirklich zu vernichten.
    quelle = pfad_fuer(name)
    ablage = quelle[:-4] + "-verworfen.txt"
    try:
        with open(ablage, "a", encoding="utf-8") as f:
            f.write(f"# verworfen {time.strftime('%Y-%m-%d %H:%M')}\n")
            for z in eintraege:
                f.write(z + "\n")
        open(quelle, "w", encoding="utf-8").close()
    except OSError as fehler:
        melde(f"  Loeschen fehlgeschlagen: {fehler}")
        sprich(f"Das hat nicht geklappt. Ich lasse {ihn} stehen.")
        return 1
    melde(f"  geleert: {quelle}, Sicherung in {ablage}")
    sprich(f"Ich habe {ihn} gelöscht.")
    return 0


# ------------------------------------------- Rueckfrage vor Drucken/Diktat

DRUCK_SKRIPT = "/usr/local/bin/dialos-drucken.py"
DIKTAT_SKRIPT = "/usr/local/bin/dialos-diktat.py"

# Akkusativ fuer die Frage. Unbekannte Namen bekommen wie bei benennen() eine
# neutrale Form, die immer aufgeht.
AKKUSATIV = {
    "einkaufszettel": "den Einkaufszettel",
    "notizen": "die Notizen",
    "brief": "den Brief",
}

# OHNE Namen in der Frage - anders als beim Loeschen. Dort steht der Name, weil
# etwas verloren geht; hier soll die Frage kurz sein, denn sie kommt jetzt vor
# jedem Druck und jedem Diktat.
#
# Der Brief fragt nach einem NEUEN Brief: Das Diktat legt den vorigen beiseite
# und schreibt einen neuen - "aufnehmen" allein verschwiege das.
DIKTAT_FRAGEN = {
    "brief": "Soll ich einen neuen Brief schreiben? Sage ja oder nein.",
    "einkaufszettel": "Soll ich etwas in den Einkaufszettel schreiben? Sage ja oder nein.",
    "notizen": "Soll ich eine Notiz aufnehmen? Sage ja oder nein.",
}


def _ist_leer(name):
    if name in BRIEF_ZIELE:
        _, text, _ = briefteile(pfad_fuer(name))
        return not any(z.strip() for z in text)
    return not eintraege_lesen(name)


def mit_rueckfrage(frage, bei_nein, bei_nichts):
    """Stellt die Frage unter der Marke. True nur bei einem klaren "ja".

    Die Marke gilt nur fuer die Dauer der Frage - der Befehlsdienst haelt sich
    so lange heraus. Die Auswertung ist dieselbe wie beim Loeschen: "ja" zaehlt
    nur ohne "nein" und ohne "[unk]" in derselben Aeusserung. Am 2026-09-14
    hat genau das gehalten: Aus dem Gespraech kam "nein nein ja", und der
    Zettel blieb stehen.
    """
    open(FREMDE_AUFNAHME_MARKE, "w").close()
    try:
        antwort = ja_oder_nein(frage)
    finally:
        try:
            os.unlink(FREMDE_AUFNAHME_MARKE)
        except OSError:
            pass
    if antwort is True:
        melde("  Rueckfrage: ja")
        return True
    melde(f"  Rueckfrage: {'nein' if antwort is False else 'nichts verstanden'} - nicht ausgefuehrt")
    sprich(bei_nein if antwort is False else bei_nichts)
    return False


def drucken(name):
    # Leer? Dann gar nicht erst fragen - das Druckskript sagt selbst, dass es
    # nichts zu drucken gibt. Eine Frage, auf die "ja" nur "ist leer" folgt,
    # waere eine Frage zu viel.
    if not _ist_leer(name):
        akk = AKKUSATIV.get(name, f"die Notiz {name}")
        if not mit_rueckfrage(f"Soll ich {akk} drucken? Sage ja oder nein.",
                              "Gut, ich drucke nicht.",
                              "Ich habe nichts verstanden. Ich drucke nicht."):
            return 0
    return subprocess.run([DRUCK_SKRIPT, name]).returncode


def diktat(name):
    frage = DIKTAT_FRAGEN.get(name, f"Soll ich in die Notiz {name} schreiben? Sage ja oder nein.")
    if not mit_rueckfrage(frage, "Gut, ich schreibe nicht mit.",
                          "Ich habe nichts verstanden. Ich schreibe nicht mit."):
        return 0
    # Das Diktat legt dieselbe Marke selbst an, bevor es sein Modell laedt.
    # Zwischen dem Ende der Frage und diesem Moment liegen Sekunden, in denen
    # der Befehlsdienst wieder zuhoert - das ist derselbe Zustand wie vorher
    # nach "Diktat starten", also nichts Neues. Gewartet wird auf das Diktat,
    # damit dieser Prozess nicht vorher endet; der Befehlsdienst wartet auf
    # diesen hier ohnehin nicht.
    return subprocess.run([DIKTAT_SKRIPT, "notiz", name]).returncode


ARCHIV_SKRIPT = "/usr/local/bin/dialos-archiv.py"


def pdf(name):
    """Legt den Brief als PDF sichtbar in Dokumente ab (Stephan, 2026-09-15).

    "Wenn man den Brief fertig hat und Diktat beenden sagt, dann muss es nicht
    nur Vorlesen oder Drucken als Option geben." Eine PDF entstand schon
    vorher bei jedem Brief - aber im Archiv, ohne Ansage und per Sprache nicht
    erreichbar. Das PDF liegt neben dem Brief und traegt denselben Namen
    ("2026-09-15-1343-Brief.pdf" neben "...-Brief.txt"), wo ein Helfer es
    findet oder an eine Mail haengt.

    OHNE RUECKFRAGE, anders als beim Drucken: Hier verlaesst nichts das Haus,
    und nichts geht verloren. Ein versehentliches PDF kostet nichts.
    """
    if name not in BRIEF_ZIELE:
        sprich("Als PDF speichern kann ich nur den Brief.")
        return 2
    quelle = pfad_fuer(name)
    if _ist_leer(name):
        melde(f"  pdf: kein Brief in {quelle}")
        sprich("Es gibt noch keinen Brief.")
        return 0
    ziel = os.path.splitext(quelle)[0] + ".pdf"
    r = subprocess.run([ARCHIV_SKRIPT, "pdf", quelle, ziel], capture_output=True, text=True)
    if r.returncode != 0:
        melde(f"  pdf fehlgeschlagen: {r.stderr.strip()[-300:]}")
        sprich("Das PDF ließ sich nicht erstellen.")
        return 1
    melde(f"  pdf: {ziel}")
    sprich("Der Brief liegt jetzt als PDF in Deinen Dokumenten.")
    return 0


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(argumente) < 2:
        print(__doc__.strip().splitlines()[-4], file=sys.stderr)
        print("Aufruf: dialos-notiz.py NAME vorlesen|loeschen|drucken|diktat|pdf", file=sys.stderr)
        return 2
    name, was = argumente[0], argumente[1]
    melde(f"=== {was} {name} ===")
    if was == "vorlesen":
        return vorlesen(name)
    if was in ("loeschen", "löschen"):
        return loeschen(name)
    if was == "drucken":
        return drucken(name)
    if was == "diktat":
        return diktat(name)
    if was == "pdf":
        return pdf(name)
    print(f"Unbekannt: {was}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
