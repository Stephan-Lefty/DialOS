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

# Was durchsucht wird. Reihenfolge ist die Reihenfolge der Ansage.
QUELLEN = [
    ("Brief",   os.path.join(os.path.expanduser("~"), "Dokumente"),
     (".txt", ".pdf", ".odt", ".docx", ".rtf")),
    ("Notiz",   os.path.join(os.path.expanduser("~"), "Notizen"), (".txt",)),
    ("Ablage",  os.path.join(os.path.expanduser("~"), "Dokumente", "Archiv"),
     (".pdf", ".txt")),
]

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
# Index
# --------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS dateien (
    id       INTEGER PRIMARY KEY,
    pfad     TEXT UNIQUE NOT NULL,
    art      TEXT NOT NULL,
    geaendert REAL NOT NULL,
    groesse  INTEGER NOT NULL,
    gelesen  REAL NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS suche USING fts5(
    name, inhalt, klang,
    content='', tokenize="unicode61 remove_diacritics 2"
);
"""


def oeffnen():
    os.makedirs(BASIS, exist_ok=True)
    db = sqlite3.connect(DATENBANK)
    db.executescript(SCHEMA)
    return db


def dateien_finden():
    for art, ordner, endungen in QUELLEN:
        if not os.path.isdir(ordner):
            continue
        for wurzel, _, namen in os.walk(ordner):
            for name in sorted(namen):
                if name.startswith("."):
                    continue
                if os.path.splitext(name)[1].lower() not in endungen:
                    continue
                yield art, os.path.join(wurzel, name)


def aufbauen(db, nur_neue=False):
    """Index fuellen. nur_neue laesst unveraenderte Dateien in Ruhe."""
    bekannt = {p: (m, g) for p, m, g in
               db.execute("SELECT pfad, geaendert, groesse FROM dateien")}
    gelesen = uebersprungen = 0
    gesehen = set()
    for art, pfad in dateien_finden():
        gesehen.add(pfad)
        try:
            st = os.stat(pfad)
        except OSError:
            continue
        if nur_neue and pfad in bekannt and bekannt[pfad] == (st.st_mtime, st.st_size):
            uebersprungen += 1
            continue
        inhalt = text_aus_datei(pfad)
        name = os.path.basename(pfad)
        db.execute("DELETE FROM suche WHERE rowid IN "
                   "(SELECT id FROM dateien WHERE pfad = ?)", (pfad,))
        db.execute("INSERT OR REPLACE INTO dateien "
                   "(pfad, art, geaendert, groesse, gelesen) VALUES (?,?,?,?,?)",
                   (pfad, art, st.st_mtime, st.st_size, time.time()))
        neue_id = db.execute("SELECT id FROM dateien WHERE pfad = ?",
                             (pfad,)).fetchone()[0]
        db.execute("INSERT INTO suche (rowid, name, inhalt, klang) VALUES (?,?,?,?)",
                   (neue_id, name, inhalt, phonetisch(name + " " + inhalt)))
        gelesen += 1
    # Verschwundene Dateien austragen - ein Treffer, den es nicht mehr gibt,
    # ist schlimmer als kein Treffer: Der Nutzer sucht ihn dann am Geraet.
    entfernt = 0
    for pfad in list(bekannt):
        if pfad not in gesehen:
            db.execute("DELETE FROM suche WHERE rowid IN "
                       "(SELECT id FROM dateien WHERE pfad = ?)", (pfad,))
            db.execute("DELETE FROM dateien WHERE pfad = ?", (pfad,))
            entfernt += 1
    db.commit()
    return gelesen, uebersprungen, entfernt


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
                "SELECT d.pfad, d.art, d.geaendert FROM suche s "
                "JOIN dateien d ON d.id = s.rowid "
                f"WHERE {bedingung} ORDER BY d.geaendert DESC LIMIT ?",
                parameter + (hoechstens,)):
            if zeile[0] in gesehen:
                continue
            gesehen.add(zeile[0])
            treffer.append({"pfad": zeile[0], "art": zeile[1],
                            "geaendert": zeile[2], "wie": wie})

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
        gelesen, uebersprungen, entfernt = aufbauen(db, nur_neue=(was == "auffrischen"))
        melde(f"{was}: {gelesen} gelesen, {uebersprungen} unveraendert, "
              f"{entfernt} entfernt, {time.time() - t0:.1f} s")
        print(f"{gelesen} gelesen, {uebersprungen} unveraendert, {entfernt} entfernt "
              f"({time.time() - t0:.1f} s)")
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
            da = "" if os.path.isdir(ordner) else "  (Ordner fehlt)"
            print(f"  {art:8s} {n:5d}  {ordner}{da}")
        print(f"MailBurg:  {'vorhanden' if _mailburg() else 'FEHLT - kein OCR'}")
        return 0

    print(__doc__.rstrip().rsplit("Aufruf:", 1)[-1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
