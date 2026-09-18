#!/usr/bin/env python3
"""Der Suchindex von DialOS-Suche: findet, was schon da liegt.

Begruendung der Bauart in docs/anwendungen.md, Abschnitt "Archiv und Suche".
Kurz: MAILBURG ARCHIVIERT, DIALOS-SUCHE MUSS NUR FINDEN. Die Dokumente liegen
bereits im Dateisystem - Briefe in ~/Dokumente/, PDFs im Archiv, Notizen in
~/Notizen/, Mails in Thunderbirds mbox. Sie ein zweites Mal in einen eigenen
Speicher zu schreiben waere Verdopplung, und ab da gaebe es zwei Wahrheiten.

DESHALB INDIZIERT DIESE DATEI NUR. Sie merkt sich Pfad, Zeitstempel und Text -
die Datei selbst bleibt, wo sie ist. Faellt der Index aus, ist nichts verloren;
er laesst sich jederzeit neu bauen.

VON MAILBURG WIRD extract/ GETEILT, nicht das Programm. Dort steckt teuer
erarbeitetes Wissen, das niemand ein zweites Mal richtig nachbaut: pdftotext
mit pypdf als Rueckfall, OCR ueber pdftoppm/tesseract mit der gemessenen
Pixelgrenze gegen den 523-Megapixel-Absturz bei iPhone-Scans, Office ohne
Binaermuell. Fehlt MailBurg, faellt diese Datei auf pdftotext und Klartext
zurueck - schlechter, aber nicht tot.

DIE KOELNER PHONETIK IST DER UNTERSCHIED ZU MAILBURG. Dort tippt man, hier
spricht man, und keine Spracherkennung trifft Eigennamen zuverlaessig. "Meier",
"Mayer", "Maier" und "Mayr" bekommen denselben Code und fallen damit in der
Suche zusammen. Das faengt die Unschaerfe strukturell ab, statt sie dem Nutzer
als Rueckfrage aufzubuerden - und Rueckfragen sind fuer jemanden, der den
Bildschirm nicht sieht, teuer.

Aufruf:
    dialos-suche-index.py aufbauen            alles neu einlesen
    dialos-suche-index.py auffrischen         nur Geaendertes
    dialos-suche-index.py suchen BEGRIFF      Treffer als JSON
    dialos-suche-index.py stand               was drinsteht
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import time

BASIS = os.path.join(os.environ.get(
    "XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share")),
    "dialos-suche")
DATENBANK = os.path.join(BASIS, "index.db")
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-suche-index.log")

# DER SICHERHEITS-STICK TRAEGT DEN DATENBEREICH DIALOS-DATA. Aufbau und Gruende
# stehen in docs/sicherheit-datenschutz.md: Der Stick wird immer in DIALOS-KEY
# (2 GiB, ext4, die LUKS-Schluesseldatei, nur fuer root) und DIALOS-DATA (Rest,
# exFAT, der mobile Datenbereich des Nutzers) partitioniert. Bei 64 GB bleiben
# rund 62 GB fuer Dokumente - dort liegt beim ausgelieferten Geraet das Archiv,
# waehrend es beim Entwicklungsnutzer dialosadmin ein Unterordner ist.
#
# GEFUNDEN WIRD ER UEBER DAS LABEL, NICHT UEBER DEN PFAD. Der Einhaengepunkt
# haengt vom Anmeldenamen ab und kann wechseln (/media/nutzer/DIALOS-DATA);
# das Label ist von dialos-setup-home-partition.sh und dialos-rekey fest
# vergeben. Damit erkennt der Index "seinen" Datenbereich wieder, egal wo er
# haengt - und liest einen fremden Stick nicht versehentlich mit.
STICK_LABEL = "DIALOS-DATA"

# WAS SICH LESEN LAESST - an EINER Stelle, nicht je Quelle. Vorher hatte die
# Ablage eine engere Liste als die Briefe, ohne dass ein Grund dafuer bestand:
# Dieselbe Datei war je nach Ordner lesbar oder nicht. Die Suche waechst
# Schritt fuer Schritt (Stephan, 2026-09-18), und sie soll ueberall zugleich
# wachsen - eine Liste, die man an drei Stellen pflegen muss, laeuft
# auseinander. Naechster Schritt sind die Mails aus Thunderbirds mbox; die
# haengen an einer eigenen Quelle, weil eine mbox-Datei viele Nachrichten
# enthaelt und nicht als eine Datei zaehlen darf.
LESBAR = (".txt", ".pdf", ".odt", ".docx", ".rtf")


def stick_datenbereich():
    """Einhaengepunkt von DIALOS-DATA, oder None.

    None heisst NICHT "leer", sondern "gerade nicht da" - der Stick gehoert
    laut Praxishinweis an den Schluesselbund und wird abgezogen. Was daraus
    folgt, steht bei `aufbauen`: Eintraege einer fehlenden Quelle bleiben
    stehen, statt ausgetragen zu werden.
    """
    verweis = f"/dev/disk/by-label/{STICK_LABEL}"
    if not os.path.exists(verweis):
        return None
    geraet = os.path.realpath(verweis)
    try:
        with open("/proc/mounts", encoding="utf-8") as f:
            for zeile in f:
                teile = zeile.split()
                if len(teile) < 2:
                    continue
                if os.path.realpath(teile[0]) != geraet:
                    continue
                # /proc/mounts maskiert Leerzeichen als \040, Tabs als \011.
                ort = (teile[1].replace("\\040", " ").replace("\\011", "\t")
                       .replace("\\012", "\n").replace("\\134", "\\"))
                return ort if os.path.isdir(ort) else None
    except OSError:
        return None
    return None                 # steckt, ist aber nicht eingehaengt


def quellen_bauen():
    """Was durchsucht wird. Reihenfolge ist die Reihenfolge der Ansage.

    Der Stick kommt HINZU und ersetzt nichts: Auf dem Entwicklungsgeraet gibt
    es ihn nicht und das Archiv liegt unter ~/Dokumente/Archiv, auf dem
    ausgelieferten Geraet ist es umgekehrt. Zwei Eintraege, von denen je nach
    Geraet einer ins Leere zeigt, sind einfacher und ehrlicher als eine
    Fallunterscheidung - ein Ordner, den es nicht gibt, wird ohnehin
    uebersprungen.
    """
    heim = os.path.expanduser("~")
    quellen = [
        ("Brief",   os.path.join(heim, "Dokumente"), LESBAR),
        ("Notiz",   os.path.join(heim, "Notizen"), (".txt",)),
        ("Ablage",  os.path.join(heim, "Dokumente", "Archiv"), LESBAR),
    ]
    stick = stick_datenbereich()
    if stick:
        # DER GANZE DATENBEREICH, nicht ein Unterordner (Stephan, 2026-09-18:
        # "ja es soll immer der komplette Datenbereich durchsucht werden").
        # Fotos und Musik liegen dort auch - die fallen ueber die Endungen
        # heraus, nicht ueber eine Ordnerregel, die der Nutzer einhalten
        # muesste. Wer seine Briefe irgendwohin legt, soll sie wiederfinden.
        quellen.append(("Ablage", stick, LESBAR))
    return quellen


QUELLEN = quellen_bauen()

MAX_ZEICHEN = 400_000          # wie bei MailBurg - ein Buch braucht niemand
GRENZE_BYTES = 80 * 1024 * 1024


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


# --------------------------------------------------------------------------
# Koelner Phonetik
#
# Nach Postel (1969), fuer Deutsch gebaut - anders als Soundex, das auf
# englische Namen zugeschnitten ist und bei "Schmidt"/"Schmitt" versagt.
# Bewusst hier ausgeschrieben und nicht aus einer Bibliothek geholt: Es sind
# dreissig Zeilen, und eine Abhaengigkeit mehr auf einem Geraet, das offline
# laufen muss, waere der schlechtere Tausch.
# --------------------------------------------------------------------------

def koelner(wort):
    """Phonetischer Code eines Wortes. Leerer Text, wenn nichts uebrig bleibt."""
    w = wort.upper()
    w = (w.replace("Ä", "A").replace("Ö", "O").replace("Ü", "U")
          .replace("ß", "S").replace("É", "E").replace("È", "E"))
    w = re.sub(r"[^A-Z]", "", w)
    if not w:
        return ""
    codes = []
    for i, z in enumerate(w):
        vor = w[i - 1] if i else ""
        nach = w[i + 1] if i + 1 < len(w) else ""
        if z in "AEIOUYJ":
            c = "0"
        elif z == "H":
            continue                       # H zaehlt nie, nur als Trenner
        elif z == "B" or (z == "P" and nach != "H"):
            c = "1"
        elif (z in "DT") and nach not in "CSZ":
            c = "2"
        elif z in "FVW" or (z == "P" and nach == "H"):
            c = "3"
        elif z in "GKQ":
            c = "4"
        elif z == "C":
            # C ist der Grund, warum es diese Funktion gibt: im Anlaut vor
            # hellen Vokalen "8" (Cilli), sonst meist "4" (Carl).
            if i == 0:
                c = "4" if nach in "AHKLOQRUX" else "8"
            elif vor in "SZ":
                c = "8"
            elif nach in "AHKOQUX":
                c = "4"
            else:
                c = "8"
        elif z == "X":
            c = "48" if vor not in "CKQ" else "8"
        elif z == "L":
            c = "5"
        elif z in "MN":
            c = "6"
        elif z == "R":
            c = "7"
        elif z in "SZ":
            c = "8"
        else:
            continue
        codes.append(c)
    code = "".join(codes)
    code = re.sub(r"(.)\1+", r"\1", code)   # Doppelte zusammenziehen
    return code[0] + code[1:].replace("0", "") if code else ""


def phonetisch(text, hoechstens=400):
    """Phonetische Fassung eines Textes - nur Woerter ab vier Zeichen.

    Kurze Woerter bringen nichts: "der", "und", "im" bekommen Codes, die auf
    Hunderte Woerter passen, und blaehen den Index auf, ohne zu trennen.
    """
    codes, gesehen = [], set()
    for wort in re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", text):
        c = koelner(wort)
        if c and c not in gesehen:
            gesehen.add(c)
            codes.append(c)
            if len(codes) >= hoechstens:
                break
    return " ".join(codes)


# --------------------------------------------------------------------------
# Text aus einer Datei holen
# --------------------------------------------------------------------------

def _mailburg():
    """MailBurgs Extraktionskette, falls vorhanden - sonst None."""
    try:
        from mailburg.extract import text as mb_text
        return mb_text
    except ImportError:
        return None


def text_aus_datei(pfad):
    """Volltext einer Datei. Leerer Text heisst: nicht lesbar, kein Fehler."""
    try:
        groesse = os.path.getsize(pfad)
    except OSError:
        return ""
    if groesse > GRENZE_BYTES:
        melde(f"  uebersprungen (zu gross, {groesse // 1024 // 1024} MB): {pfad}")
        return ""
    endung = os.path.splitext(pfad)[1].lower()

    if endung == ".txt":
        try:
            with open(pfad, encoding="utf-8", errors="replace") as f:
                return f.read(MAX_ZEICHEN)
        except OSError:
            return ""

    try:
        with open(pfad, "rb") as f:
            daten = f.read()
    except OSError:
        return ""

    mb = _mailburg()
    if mb is not None:
        try:
            ergebnis = mb.aus_anhang(os.path.basename(pfad), "", daten)
            gefunden = getattr(ergebnis, "text", None) or ""
            if gefunden.strip():
                return gefunden[:MAX_ZEICHEN]
        except Exception as fehler:        # noqa: BLE001 - nie toedlich
            melde(f"  MailBurg-Extraktion fehlgeschlagen ({pfad}): {fehler}")

    # RUECKFALL ohne MailBurg: pdftotext direkt. Schlechter - kein OCR, keine
    # Office-Dateien -, aber besser als eine Datei, die gar nicht auffindbar ist.
    if endung == ".pdf":
        try:
            r = subprocess.run(["pdftotext", "-layout", pfad, "-"],
                               capture_output=True, timeout=60)
            return r.stdout.decode("utf-8", errors="replace")[:MAX_ZEICHEN]
        except (OSError, subprocess.TimeoutExpired):
            pass
    return ""


# --------------------------------------------------------------------------
# Wer steht drin? - fuer das Eingrenzen nach Ansprechpartner oder Firma
# --------------------------------------------------------------------------

# Rechtsformen und Anreden, an denen sich ein Gegenueber erkennen laesst. Die
# Liste ist bewusst kurz und nicht vollstaendig: Sie muss nicht jeden Fall
# treffen, sie muss dem Nutzer eine Handvoll Namen zum Eingrenzen anbieten.
FIRMA_WORTE = ("GmbH", "AG", "KG", "OHG", "mbH", "e.V", "eG", "SE", "UG",
               "Versicherung", "Krankenkasse", "Bank", "Sparkasse", "Amt",
               "Finanzamt", "Stadtwerke", "Praxis", "Kanzlei", "Apotheke")
ANREDEN = ("Herr", "Herrn", "Frau", "Dr", "Prof")

# Woerter, die gross geschrieben am Satzanfang stehen und keine Namen sind.
KEIN_NAME = {"Sehr", "Mit", "Ich", "Wir", "Sie", "Der", "Die", "Das", "Ein",
             "Eine", "Bitte", "Danke", "Betreff", "Datum", "Liebe", "Lieber",
             "Guten", "Hallo", "Anbei", "Hiermit", "Zu", "Am", "In", "Bei",
             "Für", "Von", "Nach", "Über", "Und", "Aber", "Auch", "Dann"}


def _wie_eine_anschriftzeile(zeile):
    """Sieht die Zeile aus wie eine Zeile der Anschrift - oder wie Fliesstext?

    (2026-09-18, am Geraet gefunden.) Aus Stephans Brief kam als "Person" der
    Satzrest "nicht gesehen? E.V. In Oesterreich." - "e.V" stand in FIRMA_WORTE
    und traf mitten im Fliesstext. Ein falscher Name zum Eingrenzen ist
    schlimmer als ein fehlender: Der Nutzer waehlt ihn und landet bei null
    Treffern, ohne nachsehen zu koennen, warum.

    Drei Merkmale, alle aus dem Fall: Eine Anschriftzeile enthaelt kein
    Satzende mitten drin, ist kurz, und beginnt gross.
    """
    if re.search(r"[.!?]\s+\S", zeile):
        return False
    if len(zeile.split()) > 6:
        return False
    return not zeile[:1].islower()


def personen_aus_text(text, hoechstens=12):
    """Namen und Firmen, nach denen sich eingrenzen laesst.

    KEIN VOLLSTAENDIGES VERFAHREN, und das ist Absicht: Der Nutzer soll aus
    fuenfzig Funden auf einen kommen, dazu genuegen ein paar brauchbare Namen.
    Ein Erkenner, der jeden Fall trifft, waere ein eigenes Projekt - und bei
    fuenf falschen Vorschlaegen von zwoelf verliert der Nutzer nichts, er waehlt
    einfach einen anderen.

    Der KOPF DES BRIEFES zaehlt mehr als der Rest: Dort steht der Empfaenger,
    und danach sucht man. Deshalb nur die ersten 2000 Zeichen.
    """
    kopf = text[:2000]
    gefunden = []

    for zeile in kopf.splitlines():
        zeile = zeile.strip()
        if not zeile or len(zeile) > 80:
            continue
        if re.match(r"(?i)^(sehr geehrt|liebe|hallo|guten)", zeile):
            continue                       # Anrede, nicht der Empfaenger
        if not _wie_eine_anschriftzeile(zeile):
            continue                       # Fliesstext, keine Anschrift
        # Firma: Zeile enthaelt eine Rechtsform oder ein Sachwort
        # MIT WORTGRENZEN, und das ist kein Feinschliff: Ohne sie steckte "AG"
        # in "Frage" und "Abschlagszahlung", und jede Zeile mit einem dieser
        # Woerter wurde als Firma vorgeschlagen. Im ersten Test war jeder
        # zweite Vorschlag so entstanden.
        if any(re.search(r"\b" + re.escape(w) + r"\b", zeile, re.I)
               for w in FIRMA_WORTE):
            name = re.sub(r"[,;].*$", "", zeile).strip().rstrip(".")
            if 3 <= len(name) <= 60 and name not in gefunden:
                gefunden.append(name)
                continue
        # Person: Anrede plus Name
        m = re.match(r"^(?:%s)\.?\s+([A-ZÄÖÜ][\wäöüß-]+(?:\s+[A-ZÄÖÜ][\wäöüß-]+)?)"
                     % "|".join(ANREDEN), zeile)
        if m and m.group(1) not in gefunden:
            gefunden.append(m.group(1))

    # DIE GROSSSCHREIBUNGS-HEURISTIK IST BEWUSST DRAUSSEN. Sie stand hier und
    # lieferte im ersten Test drei unbrauchbare von vier Vorschlaegen ("zu
    # meiner Zuzahlung von 42", "Nordost"). Ein falscher Name zum Eingrenzen
    # ist schlimmer als ein fehlender: Der Nutzer waehlt ihn, landet bei null
    # Treffern und muss von vorn anfangen - und er kann nicht nachsehen, warum.
    # Lieber wenige sichere Namen als viele geratene.
    return gefunden[:hoechstens]


def jahr_aus(pfad, text, zeitstempel):
    """Das Jahr des Dokuments - aus dem Dateinamen, sonst aus dem Text.

    DER DATEINAME ZUERST, weil DialOS seine Briefe seit dem 2026-09-15 mit
    Datum benennt (2026-09-17-1343-Brief.txt) und das verlaesslicher ist als
    der Zeitstempel: Eine Datei, die kopiert wurde, hat ein neues mtime, aber
    denselben Namen.
    """
    m = re.search(r"\b(19|20)\d{2}\b", os.path.basename(pfad))
    if m:
        return int(m.group(0))
    m = re.search(r"\b(19|20)\d{2}\b", text[:2000])
    if m:
        return int(m.group(0))
    return int(time.strftime("%Y", time.localtime(zeitstempel)))


# --------------------------------------------------------------------------
# Index
# --------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS dateien (
    id       INTEGER PRIMARY KEY,
    pfad     TEXT UNIQUE NOT NULL,
    art      TEXT NOT NULL,
    -- AUS WELCHEM QUELLORDNER STAMMT DIE DATEI? Nur so laesst sich spaeter
    -- entscheiden, ob ein fehlender Eintrag geloescht wurde oder ob bloss
    -- seine Quelle gerade nicht angeschlossen ist. Ueber die Quellenliste
    -- allein geht das nicht: Ein abgezogener Stick steht dort gar nicht mehr.
    quelle   TEXT,
    geaendert REAL NOT NULL,
    groesse  INTEGER NOT NULL,
    gelesen  REAL NOT NULL,
    jahr     INTEGER,
    personen TEXT
);
CREATE INDEX IF NOT EXISTS dateien_jahr ON dateien(jahr);
CREATE INDEX IF NOT EXISTS dateien_art  ON dateien(art);
CREATE VIRTUAL TABLE IF NOT EXISTS suche USING fts5(
    name, inhalt, klang,
    tokenize="unicode61 remove_diacritics 2"
);
"""

# KEIN content='' MEHR (2026-09-18). Der erste Entwurf sparte damit den Platz
# fuer den Text, den FTS5 sonst ein zweites Mal ablegt - und handelte sich
# dafuer ein, dass sich aus der Tabelle NICHTS LOESCHEN laesst:
#
#     sqlite3.OperationalError: cannot DELETE from contentless fts5 table
#
# Der Fehler blieb verborgen, weil ein DELETE, das nichts trifft, durchgeht.
# Genau das ist der erste Aufbau. Ab dem zweiten Lauf trifft jedes DELETE -
# beim erneuten Einlesen einer Datei, beim Austragen einer verschwundenen -,
# und der Index waere abgestuerzt. Er war also einmal befuellbar und danach
# nicht mehr pflegbar; aufgefallen ist es beim Nachstellen eines abgezogenen
# Sticks, nicht im Betrieb.
#
# Der Preis ist Plattenplatz: FTS5 legt den Text nun selbst ab. Bei einem
# Archiv aus Briefen sind das einige zehn Megabyte - gegen einen Index, der
# sich nicht pflegen laesst, ist das kein Handel, sondern eine Korrektur.


# SCHEMA-STAND: bei JEDER Aenderung an SCHEMA hochzaehlen. Ein alter Index wird
# dann verworfen und neu gebaut (2026-09-18, am Geraet aufgelaufen): Der erste
# Aufbau brach mit "no such column: quelle" ab, weil `CREATE TABLE IF NOT EXISTS`
# eine bestehende Tabelle UNVERAENDERT laesst - die Spalte kam am selben Tag dazu.
# Die Pruefung auf content='' fing nur die FTS-Tabelle ab, nicht `dateien`.
SCHEMA_STAND = 2


def veraltet(db):
    """Grund, warum der vorhandene Index nicht mehr passt - oder None."""
    zeile = db.execute("SELECT sql FROM sqlite_master WHERE type = 'table' "
                       "AND name = 'suche'").fetchone()
    if zeile and "content=''" in (zeile[0] or "").replace(" ", ""):
        return "alter Index mit content=''"
    spalten = {z[1] for z in db.execute("PRAGMA table_info(dateien)")}
    if not spalten:
        return None                 # noch gar keine Tabelle - nichts zu verwerfen
    fehlend = {"pfad", "art", "quelle", "geaendert", "groesse", "gelesen",
               "jahr", "personen"} - spalten
    if fehlend:
        return "fehlende Spalte(n) in dateien: " + ", ".join(sorted(fehlend))
    if db.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_STAND:
        return "aelterer Schema-Stand"
    return None


def oeffnen():
    os.makedirs(BASIS, exist_ok=True)
    db = sqlite3.connect(DATENBANK)

    # ALTEN INDEX VERWERFEN, NICHT UMBAUEN. Wer schon eine Datenbank mit
    # content='' hat, kann daraus nichts loeschen - also auch nicht umziehen.
    # Ein Index ist abgeleitet: Er laesst sich jederzeit neu bauen, und genau
    # deshalb ist Wegwerfen hier die richtige Antwort und kein Verlust. Der
    # Neuaufbau kostet Lesezeit, mehr nicht.
    grund = veraltet(db)
    if grund:
        melde(f"Index passt nicht mehr ({grund}) - wird neu aufgebaut")
        db.execute("DROP TABLE IF EXISTS suche")
        db.execute("DROP TABLE IF EXISTS dateien")
        db.commit()

    db.executescript(SCHEMA)
    db.execute(f"PRAGMA user_version = {SCHEMA_STAND}")
    db.commit()
    return db


def dateien_finden():
    """Jede Datei GENAU EINMAL, mit der Art des spezifischsten Ordners.

    WARUM DAS NOETIG IST: "Ablage" ist ~/Dokumente/Archiv und liegt damit
    INNERHALB von "Brief" (~/Dokumente), das rekursiv durchsucht wird. Ohne
    diese Ausnahme wird jede Archivdatei zweimal gelesen - einmal als Brief,
    einmal als Ablage. Weil `pfad` in der Tabelle UNIQUE ist, entstehen dabei
    keine Doppeltreffer; es kostet aber die doppelte Lesezeit, und bei
    gescannten PDFs heisst das die doppelte OCR-Zeit. Dazu meldet `aufbauen`
    mehr gelesene Dateien, als es Dateien gibt.

    Gefunden am 2026-09-18, bevor der erste echte Aufbau am T490 lief.
    """
    eigene = {os.path.normpath(o) for _art, o, _e in QUELLEN}
    for art, ordner, endungen in QUELLEN:
        if not os.path.isdir(ordner):
            continue
        # Alles ausser diesem Ordner selbst - sonst schnitte sich die Quelle
        # gleich an der Wurzel ab.
        fremde = eigene - {os.path.normpath(ordner)}
        for wurzel, unterordner, namen in os.walk(ordner):
            # os.walk laeuft von oben nach unten; wer hier aus der Liste
            # streicht, wird nicht betreten.
            unterordner[:] = [
                u for u in unterordner
                if os.path.normpath(os.path.join(wurzel, u)) not in fremde]
            for name in sorted(namen):
                if name.startswith("."):
                    continue
                if os.path.splitext(name)[1].lower() not in endungen:
                    continue
                yield art, ordner, os.path.join(wurzel, name)


def aufbauen(db, nur_neue=False):
    """Index fuellen. nur_neue laesst unveraenderte Dateien in Ruhe."""
    bekannt = {p: (m, g, q) for p, m, g, q in
               db.execute("SELECT pfad, geaendert, groesse, quelle FROM dateien")}
    gelesen = uebersprungen = 0
    gesehen = set()
    for art, quelle, pfad in dateien_finden():
        gesehen.add(pfad)
        try:
            st = os.stat(pfad)
        except OSError:
            continue
        if (nur_neue and pfad in bekannt
                and bekannt[pfad] == (st.st_mtime, st.st_size, quelle)):
            uebersprungen += 1
            continue
        inhalt = text_aus_datei(pfad)
        name = os.path.basename(pfad)
        db.execute("DELETE FROM suche WHERE rowid IN "
                   "(SELECT id FROM dateien WHERE pfad = ?)", (pfad,))
        db.execute("INSERT OR REPLACE INTO dateien "
                   "(pfad, art, quelle, geaendert, groesse, gelesen, jahr, personen) "
                   "VALUES (?,?,?,?,?,?,?,?)",
                   (pfad, art, quelle, st.st_mtime, st.st_size, time.time(),
                    jahr_aus(pfad, inhalt, st.st_mtime),
                    "\n".join(personen_aus_text(inhalt))))
        neue_id = db.execute("SELECT id FROM dateien WHERE pfad = ?",
                             (pfad,)).fetchone()[0]
        db.execute("INSERT INTO suche (rowid, name, inhalt, klang) VALUES (?,?,?,?)",
                   (neue_id, name, inhalt, phonetisch(name + " " + inhalt)))
        gelesen += 1
    # Verschwundene Dateien austragen - ein Treffer, den es nicht mehr gibt,
    # ist schlimmer als kein Treffer: Der Nutzer sucht ihn dann am Geraet.
    #
    # ABER NICHT, WENN DIE GANZE QUELLE FEHLT (2026-09-18, nach Stephans
    # Hinweis, dass das Archiv beim Testnutzer ein Unterordner ist, beim
    # spaeteren Nutzer aber ein Ordner AUF EINEM STICK). Ein Stick steckt mal
    # und mal nicht. Liefe der Aufbau ohne ihn, wuerde jede Archivdatei als
    # "verschwunden" ausgetragen - und beim naechsten Einstecken muesste alles
    # neu gelesen werden, bei gescannten PDFs die gesamte OCR. Schlimmer noch
    # ist die Zwischenzeit: Der Nutzer sucht einen Brief, den es gibt, und
    # DialOS sagt, es gebe ihn nicht.
    #
    # EINE FEHLENDE QUELLE IST KEINE LEERE QUELLE. Nur das Verschwinden
    # EINZELNER Dateien innerhalb einer vorhandenen Quelle ist ein echtes
    # Verschwinden.
    #
    # GEPRUEFT WIRD DIE QUELLE DES EINTRAGS, NICHT DIE HEUTIGE QUELLENLISTE.
    # Das ist der Unterschied, der zaehlt: Ein abgezogener Stick steht in der
    # heutigen Liste gar nicht mehr drin - wer nur sie befragt, findet keine
    # fehlende Quelle und traegt genau die Dateien aus, die er schuetzen soll.
    # Jeder Eintrag bringt seinen Quellordner deshalb selbst mit.
    # DA SEIN HEISST: IN DER HEUTIGEN LISTE **UND** VORHANDEN (2026-09-18, in
    # der Nachstellung aufgelaufen). Die Pruefung auf os.path.isdir() allein
    # genuegt nicht: Der Einhaengepunkt eines abgezogenen Sticks bleibt je nach
    # System als LEERER Ordner stehen. Dann ist er "vorhanden", der Stick aber
    # weg - und genau die Archivdateien, die geschuetzt werden sollen, wurden
    # ausgetragen. Steht die Quelle heute nicht in QUELLEN (kein Stick
    # gefunden), bleiben ihre Eintraege ohne weitere Frage stehen.
    heutige = {os.path.normpath(o) for _a, o, _e in QUELLEN}
    entfernt = gehalten = 0
    verfuegbar = {}
    for pfad, (_m, _g, quelle) in list(bekannt.items()):
        if pfad in gesehen:
            continue
        if quelle:
            if quelle not in verfuegbar:
                verfuegbar[quelle] = (os.path.normpath(quelle) in heutige
                                      and os.path.isdir(quelle))
            if not verfuegbar[quelle]:
                gehalten += 1
                continue
        db.execute("DELETE FROM suche WHERE rowid IN "
                   "(SELECT id FROM dateien WHERE pfad = ?)", (pfad,))
        db.execute("DELETE FROM dateien WHERE pfad = ?", (pfad,))
        entfernt += 1
    if gehalten:
        melde(f"{gehalten} Eintraege gehalten - ihre Quelle ist gerade nicht da")
    db.commit()
    return gelesen, uebersprungen, entfernt, gehalten


def suchen(db, begriff, hoechstens=40):
    """Treffer zu einem gesprochenen Begriff.

    ZWEI DURCHGAENGE, und der zweite ist der Grund fuer diese Datei: Zuerst
    woertlich, dann phonetisch. Wer "Meier" sagt und "Maier" im Brief stehen
    hat, bekommt ihn im zweiten Durchgang - markiert als "klang", damit die
    Ansage es sagen kann ("klingt wie").
    """
    worte = [w for w in re.findall(r"[\wÄÖÜäöüß]+", begriff) if len(w) > 1]
    if not worte:
        return []
    treffer, gesehen = [], set()

    def hole(bedingung, parameter, wie):
        for zeile in db.execute(
                "SELECT d.pfad, d.art, d.geaendert, d.jahr, d.personen "
                "FROM suche s "
                "JOIN dateien d ON d.id = s.rowid "
                f"WHERE {bedingung} ORDER BY d.geaendert DESC LIMIT ?",
                parameter + (hoechstens,)):
            if zeile[0] in gesehen:
                continue
            gesehen.add(zeile[0])
            treffer.append({"pfad": zeile[0], "art": zeile[1],
                            "geaendert": zeile[2], "jahr": zeile[3],
                            "personen": (zeile[4] or "").split("\n") if zeile[4] else [],
                            "wie": wie,
                            # IST DIE DATEI GERADE ERREICHBAR? Bei einem Archiv
                            # auf einem Stick kann der Index sie kennen, ohne
                            # dass sie da ist. Die Ansage muss den Unterschied
                            # sagen koennen - "im Archiv, das gerade nicht
                            # angeschlossen ist" statt einer Fundstelle, die
                            # sich nicht oeffnen laesst.
                            "erreichbar": os.path.exists(zeile[0])})

    hole("suche MATCH ?", (" OR ".join(f'"{w}"' for w in worte),), "wort")
    if len(treffer) < hoechstens:
        codes = [koelner(w) for w in worte if len(w) >= 4]
        codes = [c for c in codes if c]
        if codes:
            hole("klang MATCH ?", (" OR ".join(codes),), "klang")
    return treffer[:hoechstens]


def main():
    was = sys.argv[1] if len(sys.argv) > 1 else "stand"
    db = oeffnen()

    if was in ("aufbauen", "auffrischen"):
        t0 = time.time()
        gelesen, uebersprungen, entfernt, gehalten = aufbauen(
            db, nur_neue=(was == "auffrischen"))
        melde(f"{was}: {gelesen} gelesen, {uebersprungen} unveraendert, "
              f"{entfernt} entfernt, {gehalten} gehalten, {time.time() - t0:.1f} s")
        print(f"{gelesen} gelesen, {uebersprungen} unveraendert, {entfernt} entfernt "
              f"({time.time() - t0:.1f} s)")
        if gehalten:
            print(f"{gehalten} Eintraege behalten, weil ihre Quelle gerade nicht "
                  "angeschlossen ist - nicht ausgetragen.")
        if _mailburg() is None:
            print("Hinweis: MailBurgs extract/ fehlt - kein OCR, keine "
                  "Office-Dateien. PDFs nur ueber pdftotext.")
        return 0

    if was == "suchen" and len(sys.argv) > 2:
        # JSON, weil eine fuer Menschen gesetzte Liste fuer einen Sprachdialog
        # unbrauchbar waere - die Erweiterung muss zaehlen und eingrenzen.
        print(json.dumps(suchen(db, " ".join(sys.argv[2:])), ensure_ascii=False))
        return 0

    if was == "stand":
        anzahl = db.execute("SELECT COUNT(*) FROM dateien").fetchone()[0]
        print(f"Index:     {DATENBANK}")
        print(f"Dateien:   {anzahl}")
        for art, ordner, _ in QUELLEN:
            n = db.execute("SELECT COUNT(*) FROM dateien WHERE art = ?",
                           (art,)).fetchone()[0]
            da = ("" if os.path.isdir(ordner)
                  else "  (Ordner fehlt - Eintraege bleiben erhalten)")
            print(f"  {art:8s} {n:5d}  {ordner}{da}")
        # QUELLEN, DIE DER INDEX KENNT, DIE ES HEUTE ABER NICHT GIBT. Ohne
        # diese Zeile sieht ein abgezogener Stick aus wie gar nichts: Die
        # Eintraege zaehlen oben mit, aber kein Ordner dazu ist zu sehen.
        bekannte = {q for (q,) in db.execute(
            "SELECT DISTINCT quelle FROM dateien WHERE quelle IS NOT NULL")}
        fehlend = sorted(q for q in bekannte if not os.path.isdir(q))
        for ordner in fehlend:
            n = db.execute("SELECT COUNT(*) FROM dateien WHERE quelle = ?",
                           (ordner,)).fetchone()[0]
            print(f"  {'nicht da':8s} {n:5d}  {ordner}  (Eintraege bleiben)")
        stick = stick_datenbereich()
        print(f"Stick:     {stick or f'{STICK_LABEL} nicht eingehaengt'}")
        print(f"MailBurg:  {'vorhanden' if _mailburg() else 'FEHLT - kein OCR'}")
        return 0

    print(__doc__.rstrip().rsplit("Aufruf:", 1)[-1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
