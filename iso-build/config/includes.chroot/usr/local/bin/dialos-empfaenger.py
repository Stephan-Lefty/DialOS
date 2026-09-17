#!/usr/bin/env python3
"""DialOS: Empfaenger eines Briefs - Thunderbird-Kontakte suchen, anlegen, Adressen richten.

Stephan am 2026-09-16/17: "die genaue Adresse, wohin der Brief gehen soll, muss
eingesprochen werden", "diese Adresse muss automatisch als Kontakt bei
Thunderbird hinterlegt werden", "vielleicht als ein Block Empfaenger". Seine
Wahl: gefuehrter Dialog, und bekannte Kontakte werden zuerst gesucht.

DER DIALOG SELBST LAEUFT IN dialos-diktat.py - dort sind Mikrofon, Vosk und
Parakeet schon geladen. Dieses Modul liefert, was kein Mikrofon braucht und sich
ohne Stimme pruefen laesst: Kontakte lesen und schreiben, Adressen aus
gesprochenem Text richten (Hausnummer, Postleitzahl), Ansagen formulieren.

THUNDERBIRDS ADRESSBUCH: abook.sqlite im Profil, Tabelle properties(card, name,
value). Seit Thunderbird 102 ist jede Karte eine vCard in der Eigenschaft
"_vCard"; DisplayName, FirstName, LastName dienen der Suche und Autovervollstaendigung.
GESCHRIEBEN WIRD NUR, WENN THUNDERBIRD NICHT LAEUFT: Es haelt das Adressbuch im
Speicher und koennte einen Eintrag von aussen beim Beenden verlieren oder
ueberschreiben. Laeuft es, kommt der Kontakt in eine Warteschlange
(~/.config/dialos/kontakte-neu.json) und wird beim naechsten Anmelden eingetragen
(dialos-kontakte.service -> "dialos-empfaenger.py nachholen").

Aufruf:
  dialos-empfaenger.py suchen NAME      Kontakte zu NAME, mit Adresse
  dialos-empfaenger.py nachholen        Warteschlange eintragen (beim Anmelden)
  dialos-empfaenger.py liste            alle Kontakte mit Adresse
"""

import datetime
import difflib
import json
import os
import re
import sqlite3
import sys
import time
import unicodedata
import uuid

HEIM = os.path.expanduser("~")
WARTESCHLANGE = os.path.join(HEIM, ".config", "dialos", "kontakte-neu.json")
PROTOKOLL = os.path.join(HEIM, ".log", "dialos-empfaenger.log")
FIRMEN_WOERTER = ("gmbh", "ag", "kg", "ohg", "e.v.", "ev", "verwaltung", "hausverwaltung",
                  "versicherung", "bank", "sparkasse", "amt", "praxis", "kanzlei", "verein",
                  "stadtwerke", "gemeinde", "krankenkasse", "finanzamt", "genossenschaft",
                  "gesellschaft", "firma", "service", "center", "zentrum", "institut", "ug")
LAENDER_PLZ_LAENGE = {"deutschland": 5, "österreich": 4, "schweiz": 4, "liechtenstein": 4,
                      "luxemburg": 4, "belgien": 4, "dänemark": 4, "frankreich": 5,
                      "italien": 5, "spanien": 5, "niederlande": 4}


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


# ------------------------------------------------------------------ Thunderbird
def profil(heim=HEIM):
    """Das Thunderbird-Profil mit Adressbuch - das mit einem Mailkonto zuerst."""
    wurzel = os.path.join(heim, ".thunderbird")
    if not os.path.isdir(wurzel):
        return None
    kandidaten = []
    for name in sorted(os.listdir(wurzel)):
        ordner = os.path.join(wurzel, name)
        if not os.path.isfile(os.path.join(ordner, "prefs.js")):
            continue
        with open(os.path.join(ordner, "prefs.js"), encoding="utf-8", errors="replace") as f:
            hat_konto = "useremail" in f.read()
        kandidaten.append((not hat_konto, name, ordner))
    return sorted(kandidaten)[0][2] if kandidaten else None


def thunderbird_laeuft():
    eigen = str(os.getpid())
    for eintrag in os.listdir("/proc"):
        if not eintrag.isdigit() or eintrag == eigen:
            continue
        try:
            if "thunderbird" in os.path.basename(os.readlink(f"/proc/{eintrag}/exe")).lower():
                return True
        except OSError:
            continue
    return False


def _vcard_feld(vcard, name):
    """Alle Werte einer vCard-Eigenschaft (ohne Parameter), entfaltet und entschluesselt."""
    entfaltet = re.sub(r"\r?\n[ \t]", "", vcard)
    werte = []
    for zeile in entfaltet.splitlines():
        kopf, _, wert = zeile.partition(":")
        if kopf.split(";")[0].upper() == name:
            werte.append(wert)
    return werte


def _vcard_teile(wert):
    teile, aktuell, i = [], "", 0
    while i < len(wert):
        z = wert[i]
        if z == "\\" and i + 1 < len(wert):
            aktuell += {"n": "\n", ",": ",", ";": ";", "\\": "\\"}.get(wert[i + 1], wert[i + 1])
            i += 2
            continue
        if z == ";":
            teile.append(aktuell)
            aktuell = ""
        else:
            aktuell += z
        i += 1
    teile.append(aktuell)
    return teile


def _vcard_sicher(text):
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def kontakte(pfad=None):
    """[{'uid', 'name', 'firma', 'strasse', 'plz', 'ort', 'land'}] aus abook.sqlite."""
    if pfad is None:
        ordner = profil()
        if not ordner:
            return []
        pfad = os.path.join(ordner, "abook.sqlite")
    if not os.path.isfile(pfad):
        return []
    try:
        verbindung = sqlite3.connect(f"file:{pfad}?mode=ro", uri=True, timeout=5)
        zeilen = verbindung.execute(
            "SELECT card, value FROM properties WHERE name = '_vCard'").fetchall()
        verbindung.close()
    except sqlite3.Error as fehler:
        melde(f"Adressbuch nicht lesbar: {fehler}")
        return []
    ergebnis = []
    for karte, vcard in zeilen:
        fn = (_vcard_feld(vcard, "FN") or [""])[0]
        org = _vcard_teile((_vcard_feld(vcard, "ORG") or [""])[0])[0]
        adr = _vcard_teile((_vcard_feld(vcard, "ADR") or [";;;;;;"])[0]) + [""] * 7
        ergebnis.append({"uid": karte, "name": _vcard_teile(fn)[0] if fn else "",
                         "firma": org, "zusatz": adr[1], "strasse": adr[2], "ort": adr[3],
                         "plz": adr[5], "land": adr[6]})
    return ergebnis


def _vergleichbar(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(z for z in text if not unicodedata.combining(z))
    text = text.replace("ß", "ss")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text).split())


def koelner_phonetik(text):
    """Klangschluessel nach Koelner Phonetik: "G so bau" und "GESOBAU" -> "481".

    Am 2026-09-17 kam Stephans "Gesobau" als "G so bau" an - kein Buchstabenvergleich
    findet das, der Klang ist aber derselbe. Der Schluessel fasst gleich klingende
    Buchstaben zusammen und laesst Vokale weg.
    """
    w = _vergleichbar(text).replace(" ", "")
    code = []
    for i, z in enumerate(w):
        vor = w[i - 1] if i else ""
        nach = w[i + 1] if i + 1 < len(w) else ""
        if z in "aeijouy":
            c = "0"
        elif z == "h":
            c = ""
        elif z == "b":
            c = "1"
        elif z == "p":
            c = "3" if nach == "h" else "1"
        elif z in "dt":
            c = "8" if nach in "csz" else "2"
        elif z in "fvw":
            c = "3"
        elif z in "gkq":
            c = "4"
        elif z == "c":
            if i == 0:
                c = "4" if nach in "ahkloqrux" else "8"
            else:
                c = "8" if vor in "sz" or nach not in "ahkoqux" else "4"
        elif z == "x":
            c = "8" if vor in "ckq" else "48"
        elif z == "l":
            c = "5"
        elif z in "mn":
            c = "6"
        elif z == "r":
            c = "7"
        elif z in "sz":
            c = "8"
        elif z.isdigit():
            c = z
        else:
            c = ""
        code.append(c)
    zusammen = []
    for c in "".join(code):
        if not zusammen or zusammen[-1] != c:
            zusammen.append(c)
    ergebnis = "".join(zusammen)
    return ergebnis[:1] + ergebnis[1:].replace("0", "")


def suchen(gesprochen, liste=None):
    """Kontakte mit Adresse, die zum gesprochenen Namen passen - beste zuerst.

    Aehnlichkeit statt Gleichheit: Die Erkennung schreibt "Hausverwaltung
    Beispiel" als "Hausverwaltung Beispiele" oder "Maier" als "Meier". Ein
    Treffer braucht 80 % Aehnlichkeit des ganzen Namens oder alle gesprochenen
    Woerter im Kontakt.
    """
    ziel = _vergleichbar(gesprochen)
    if not ziel:
        return []
    treffer = []
    for k in (liste if liste is not None else kontakte()):
        if not (k["strasse"] or k["ort"]):
            continue
        besten = 0.0
        for feld in (k["name"], k["firma"], f"{k['name']} {k['firma']}"):
            v = _vergleichbar(feld)
            if not v:
                continue
            wert = difflib.SequenceMatcher(None, ziel, v).ratio()
            # Gleicher Klang ("G so bau" / "GESOBAU") zaehlt wie ein Treffer.
            # Rechtsform zaehlt nicht: "Gesobau" ist gemeint, im Kontakt steht "GESOBAU AG".
            ohne_form = " ".join(w for w in v.split() if w not in RECHTSFORMEN) or v
            klang_ziel, klang_v = koelner_phonetik(ziel), koelner_phonetik(ohne_form)
            if len(klang_ziel) >= 3 and difflib.SequenceMatcher(None, klang_ziel, klang_v).ratio() >= 0.9:
                wert = max(wert, 0.85)
            if all(any(difflib.SequenceMatcher(None, w, x).ratio() >= 0.8 for x in v.split())
                   for w in ziel.split()):
                wert = max(wert, 0.9)
            besten = max(besten, wert)
        if besten >= 0.8:
            treffer.append((besten, k))
    return [k for _, k in sorted(treffer, key=lambda t: -t[0])]


def ist_firma(name):
    return any(w in FIRMEN_WOERTER for w in _vergleichbar(name).split())


ANREDEN = ("herr", "frau", "dr", "prof")
RECHTSFORMEN = ("ag", "gmbh", "kg", "ohg", "ev", "ug", "se", "co", "mbh", "gbr", "eg")


def ist_person(name):
    """Nur mit Anrede ("Frau Erika Musterfrau") - "G so bau" wurde 2026-09-17 zu
    Vorname "G so", Nachname "bau". Ohne Anrede ist nicht zu entscheiden, also
    kein Vor- und Nachname, nur der Anzeigename."""
    woerter = [w.strip(".").lower() for w in name.split()]
    return bool(woerter) and woerter[0] in ANREDEN and len(woerter) >= 3 - (woerter[0] in ("dr", "prof"))


def vcard(empfaenger, uid):
    name = empfaenger["name"]
    zeilen = ["BEGIN:VCARD", "VERSION:4.0", f"UID:{uid}", f"FN:{_vcard_sicher(name)}"]
    if not ist_person(name):
        zeilen.append(f"ORG:{_vcard_sicher(name)}")
    else:
        teile = name.split()
        teile = [t for t in teile if t.lower() not in ("herr", "frau", "dr.", "dr", "prof.")]
        if len(teile) >= 2:
            zeilen.append(f"N:{_vcard_sicher(teile[-1])};{_vcard_sicher(' '.join(teile[:-1]))};;;")
    adr = ["", _vcard_sicher(empfaenger.get("zusatz", "")), _vcard_sicher(empfaenger.get("strasse", "")),
           _vcard_sicher(empfaenger.get("ort", "")), "", _vcard_sicher(empfaenger.get("plz", "")),
           _vcard_sicher(empfaenger.get("land", ""))]
    zeilen.append("ADR:" + ";".join(adr))
    zeilen.append("NOTE:Angelegt von DialOS beim Brief-Diktat")
    zeilen.append("END:VCARD")
    return "\r\n".join(zeilen) + "\r\n"


def eintragen(empfaenger, pfad=None):
    """Legt den Kontakt an. True: eingetragen, False: in die Warteschlange."""
    if pfad is None:
        ordner = profil()
        pfad = os.path.join(ordner, "abook.sqlite") if ordner else None
    if pfad is None or not os.path.isfile(pfad) or thunderbird_laeuft():
        _vormerken(empfaenger)
        melde(f"vorgemerkt (Thunderbird laeuft oder kein Adressbuch): {empfaenger['name']!r}")
        return False
    uid = str(uuid.uuid4())
    karte = vcard(empfaenger, uid)
    teile = empfaenger["name"].split()
    eigenschaften = [("_vCard", karte), ("DisplayName", empfaenger["name"]),
                     ("LastModifiedDate", str(int(time.time())))]
    teile = [t for t in teile if t.lower().strip(".") not in ("herr", "frau", "dr", "prof")]
    if ist_person(empfaenger["name"]) and len(teile) >= 2:
        eigenschaften += [("FirstName", " ".join(teile[:-1])), ("LastName", teile[-1])]
    try:
        verbindung = sqlite3.connect(pfad, timeout=5)
        with verbindung:
            verbindung.executemany("INSERT INTO properties (card, name, value) VALUES (?, ?, ?)",
                                   [(uid, n, w) for n, w in eigenschaften])
        verbindung.close()
    except sqlite3.Error as fehler:
        melde(f"Kontakt nicht eingetragen ({fehler}) - vorgemerkt")
        _vormerken(empfaenger)
        return False
    melde(f"Kontakt eingetragen: {empfaenger['name']!r} ({uid})")
    return True


def _vormerken(empfaenger):
    liste = []
    try:
        with open(WARTESCHLANGE, encoding="utf-8") as f:
            liste = json.load(f)
    except (OSError, ValueError):
        pass
    liste.append(empfaenger)
    os.makedirs(os.path.dirname(WARTESCHLANGE), exist_ok=True)
    with open(WARTESCHLANGE + ".neu", "w", encoding="utf-8") as f:
        json.dump(liste, f, ensure_ascii=False, indent=1)
    os.chmod(WARTESCHLANGE + ".neu", 0o600)
    os.replace(WARTESCHLANGE + ".neu", WARTESCHLANGE)


def nachholen():
    try:
        with open(WARTESCHLANGE, encoding="utf-8") as f:
            liste = json.load(f)
    except (OSError, ValueError):
        return 0
    if thunderbird_laeuft():
        return 0
    os.remove(WARTESCHLANGE)
    vorhanden = kontakte()
    eingetragen = 0
    for e in liste:
        if any(_vergleichbar(k["name"]) == _vergleichbar(e["name"])
               and _vergleichbar(k["strasse"]) == _vergleichbar(e.get("strasse", ""))
               for k in vorhanden):
            continue
        if eintragen(e):
            eingetragen += 1
    return eingetragen


# ------------------------------------------------------------------ Adressen
def _zahl_als_ziffern(wort, zahlen):
    """"fuenf" -> "5", "zwoelf" -> "12", "neunundzwanzig" -> "29"; Ziffern bleiben."""
    if wort.isdigit():
        return wort
    wert = zahlen.grundzahl(wort.lower())
    return None if wert is None else str(wert)


def strasse_richten(text, zahlen):
    """"Musterstrasse fuenf a" -> "Musterstraße 5a"; "Am Klosterwald sechshundertsiebenundsechzig b" -> "... 667b"."""
    text = " ".join(re.sub(r"[.,;:!?]+$", "", text.strip()).split())
    woerter = text.split()
    ausgabe = []
    for i, w in enumerate(woerter):
        ziffern = _zahl_als_ziffern(w.strip(","), zahlen) if w.lower() not in ("ein", "eine") else None
        if ziffern is not None and i > 0:
            if ausgabe and re.fullmatch(r"\d+", ausgabe[-1]):
                # "sechshundert siebenundsechzig" in zwei Woertern
                zusammen = zahlen.grundzahl((woerter[i - 1] + w).lower())
                ausgabe[-1] = str(zusammen) if zusammen is not None else ausgabe[-1] + ziffern
            else:
                ausgabe.append(ziffern)
        elif (len(w) == 1 and w.isalpha() and ausgabe and re.fullmatch(r"\d+", ausgabe[-1])):
            ausgabe[-1] += w.lower()          # Hausnummer-Zusatz "5 a" -> "5a"
        else:
            ausgabe.append(w)
    ergebnis = " ".join(ausgabe)
    ergebnis = re.sub(r"(?i)strasse\b", "straße", ergebnis)
    return ergebnis[:1].upper() + ergebnis[1:]


def plz_ort_richten(text, zahlen, laenge=5):
    """"zwoelf sechs neunundzwanzig Berlin" -> ("12629", "Berlin"); "1010 Wien." -> ("1010", "Wien")."""
    text = " ".join(re.sub(r"[.,;:!?]+$", "", text.strip()).split())
    woerter = text.split()
    zahlteile = []
    while woerter and _zahl_als_ziffern(woerter[0].strip(","), zahlen) is not None \
            and woerter[0].lower() not in ("ein", "eine"):
        zahlteile.append(woerter.pop(0).strip(","))
    ort = " ".join(woerter).strip(" ,")
    ort = ort[:1].upper() + ort[1:]
    if not zahlteile:
        return "", ort
    kandidaten = ["".join(_zahl_als_ziffern(t, zahlen) for t in zahlteile)]
    zusammen = zahlen.grundzahl("".join(t.lower() for t in zahlteile))
    if zusammen is not None:
        kandidaten.append(str(zusammen))
    passend = [k for k in kandidaten if len(k) == laenge]
    return (passend[0] if passend else kandidaten[0]), ort


def plz_laenge(land):
    return LAENDER_PLZ_LAENGE.get((land or "").strip().lower(), 5)


def zeilen(empfaenger, eigenes_land=""):
    """Anschriftzeilen nach DIN 5008: Name, Zusatz, Strasse, PLZ Ort, LAND (nur Ausland)."""
    ergebnis = [empfaenger["name"]]
    if empfaenger.get("zusatz"):
        ergebnis.append(empfaenger["zusatz"])
    if empfaenger.get("strasse"):
        ergebnis.append(empfaenger["strasse"])
    ort = " ".join(x for x in (empfaenger.get("plz", ""), empfaenger.get("ort", "")) if x)
    if ort:
        ergebnis.append(ort)
    land = empfaenger.get("land", "")
    if land and land.strip().lower() != (eigenes_land or "").strip().lower():
        ergebnis.append(land.upper())
    return ergebnis


def gesprochen(empfaenger):
    """Fuer die Ansage: Postleitzahl Ziffer fuer Ziffer, damit ein Hoerfehler auffaellt."""
    teile = [empfaenger["name"]]
    if empfaenger.get("strasse"):
        teile.append(empfaenger["strasse"])
    if empfaenger.get("plz"):
        teile.append("Postleitzahl " + " ".join(empfaenger["plz"]))
    if empfaenger.get("ort"):
        teile.append(empfaenger["ort"])
    if empfaenger.get("land"):
        teile.append(empfaenger["land"])
    return ", ".join(teile)


def main():
    befehl = sys.argv[1] if len(sys.argv) > 1 else ""
    if befehl == "nachholen":
        anzahl = nachholen()
        if anzahl:
            print(f"{anzahl} Kontakt(e) eingetragen")
        return 0
    if befehl == "liste":
        for k in kontakte():
            print(f"{k['name'] or k['firma']}: {k['strasse']}, {k['plz']} {k['ort']} {k['land']}")
        return 0
    if befehl == "suchen" and len(sys.argv) > 2:
        for k in suchen(" ".join(sys.argv[2:])):
            print(f"{k['name'] or k['firma']}: {k['strasse']}, {k['plz']} {k['ort']} {k['land']}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
