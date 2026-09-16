#!/usr/bin/env python3
"""DialOS: die persoenlichen Daten des Nutzers - an EINER Stelle.

Stephan am 2026-09-16: "die persoenlichen Daten des Nutzers, in dem Fall von
mir, fix fuer alle Programme definieren und eintragen" - und dazu ein
Formular, das er fuer jeden Kunden von Hand ausfuellt und an einen festen Ort
legt. Die Feldliste stammt aus seiner Datei "Welche Daten werden benoetigt"
und aus docs/kundendaten-felder.md (2026-08-24), ergaenzt um Titel,
Adresszusatz, Firma, Unterschrift, Grussformel, Bank und Notfall.

WO: ~/.config/dialos/persoenliche-daten.txt im Konto der Person. Im
Nutzerkonto liegt das auf der verschluesselten Partition - genau die
Forderung von 2026-08-24 ("nicht unverschluesselt auf der Wurzelpartition").
Die Vorlage mit leeren Feldern liegt in /usr/local/share/dialos/.

FORMAT: "Feld: Wert", eine Zeile je Feld, # fuer Erklaerungen - so, wie
Stephan seinen Entwurf geschrieben hat. Gross- und Kleinschreibung,
Leerzeichen und Bindestriche im Feldnamen zaehlen nicht.

WER LIEST ES (Stand 2026-09-16):
  dialos-diktat.py        Absender und Unterschrift im Brief
  dialos-namen.py         Name zum Schreiben und zum Sprechen
  dialos-start-ansage.py  Wetter-Ort (auch fuer dialos-auskunft.py)
Die Felder heissen wie in einer vCard, damit die eigene Karte und spaeter die
eingesprochenen Empfaenger als Thunderbird-Kontakte gehen (Befehl "vcard").

Aufruf:
  dialos-persoenliche-daten.py anlegen   Vorlage ins eigene Konto kopieren (nichts ueberschreiben)
  dialos-persoenliche-daten.py pruefen   fehlende Pflichtfelder und Formfehler melden
  dialos-persoenliche-daten.py zeigen    ausgefuellte Felder und Absenderblock
  dialos-persoenliche-daten.py vcard     eigene Karte als vCard 4.0
"""

import os
import re
import shutil
import sys

DATEI = os.path.join(os.path.expanduser("~"), ".config", "dialos", "persoenliche-daten.txt")
VORLAGE = "/usr/local/share/dialos/persoenliche-daten-vorlage.txt"

# (Schluessel, Feldname im Formular, Pflicht)
FELDER = [
    ("anrede", "Anrede", False),
    ("titel", "Titel", False),
    ("vorname", "Vorname", True),
    ("name", "Name", True),
    ("name_gesprochen", "Name gesprochen", False),
    ("ansprache", "Ansprache", False),
    ("strasse", "Straße", True),
    ("hausnummer", "Hausnummer", True),
    ("adresszusatz", "Adresszusatz", False),
    ("postleitzahl", "Postleitzahl", True),
    ("ort", "Ort", True),
    ("bundesland", "Bundesland", False),
    ("land", "Land", True),
    ("laenderkennzeichen", "Länderkennzeichen", False),
    ("wetter_ort", "Wetter-Ort", False),
    ("mail", "E-Mail-Adresse", False),
    ("festnetz_privat", "Telefon Festnetz privat", False),
    ("handy_privat", "Telefon Handy privat", False),
    ("fax_privat", "Fax privat", False),
    ("webseite", "Webseite", False),
    ("firma", "Firma", False),
    ("position", "Position", False),
    ("mail_dienstlich", "E-Mail-Adresse dienstlich", False),
    ("festnetz_dienstlich", "Telefon Festnetz dienstlich", False),
    ("handy_dienstlich", "Telefon Handy dienstlich", False),
    ("fax_dienstlich", "Fax dienstlich", False),
    ("unterschrift_name", "Name für die Unterschrift", False),
    ("grussformel", "Grußformel", False),
    ("unterschrift_bild", "Unterschrift als Bild", False),
    ("kontoinhaber", "Kontoinhaber", False),
    ("iban", "IBAN", False),
    ("bic", "BIC", False),
    ("bank", "Bank", False),
    ("notfall_name", "Notfallkontakt Name", False),
    ("notfall_telefon", "Notfallkontakt Telefon", False),
]
TELEFONFELDER = ("festnetz_privat", "handy_privat", "fax_privat", "festnetz_dienstlich",
                 "handy_dienstlich", "fax_dienstlich", "notfall_telefon")


def _schluessel(feldname):
    return re.sub(r"[\s\-_]", "", feldname).lower()


NACH_FELDNAME = {_schluessel(beschriftung): schluessel for schluessel, beschriftung, _ in FELDER}


def lesen(pfad=None, unbekannt=None):
    """Alle ausgefuellten Felder als dict. Fehlt die Datei: leeres dict.

    Unbekannte Feldnamen kommen in die Liste unbekannt (fuer "pruefen") -
    ein Tippfehler im Feldnamen soll nicht still verschwinden.
    """
    try:
        with open(pfad or DATEI, encoding="utf-8") as f:
            return aus_text(f.read(), unbekannt)
    except OSError:
        return {}


def aus_text(text, unbekannt=None):
    """Wie lesen(), aber aus einem Text - die Eingabemaske liest fremde Konten so."""
    daten = {}
    for nummer, zeile in enumerate(text.splitlines(), 1):
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#") or ":" not in zeile:
            continue
        feld, wert = zeile.split(":", 1)
        schluessel = NACH_FELDNAME.get(_schluessel(feld))
        wert = " ".join(wert.split())
        if schluessel is None:
            if unbekannt is not None:
                unbekannt.append((nummer, feld.strip(), zeile))
            continue
        if wert:
            daten[schluessel] = wert
    return daten


ABSCHNITT = re.compile(r"^#\s*-{5,}\s*(.+?)\s*$")


def aufbau(vorlage=None):
    """[(Abschnitt, [(schluessel, Feldname, Pflicht, Hinweis)])] aus der Vorlage.

    DIE VORLAGE IST DIE EINZIGE QUELLE fuer Reihenfolge, Abschnitte und Hinweise:
    Die Eingabemaske baut sich daraus, damit Datei und Maske nie auseinanderlaufen.
    Ein Hinweis sind die #-Zeilen direkt ueber dem Feld.
    """
    pflicht = {k: p for k, _, p in FELDER}
    abschnitte = []
    hinweis = []
    with open(vorlage or VORLAGE, encoding="utf-8") as f:
        for zeile in f:
            zeile = zeile.rstrip("\n")
            kopf = ABSCHNITT.match(zeile)
            if kopf:
                abschnitte.append((kopf.group(1), []))
                hinweis = []
            elif zeile.startswith("#"):
                hinweis.append(zeile.lstrip("#").strip())
            elif ":" in zeile and abschnitte:
                feld = zeile.split(":", 1)[0].strip()
                schluessel = NACH_FELDNAME.get(_schluessel(feld))
                if schluessel:
                    text = " ".join(h for h in hinweis if h)
                    # "Titel: z.B. Dr." - der Feldname steht in der Maske schon davor.
                    if text.lower().startswith(feld.lower() + ":"):
                        text = text[len(feld) + 1:].strip()
                    abschnitte[-1][1].append((schluessel, feld, pflicht[schluessel],
                                              text[:1].upper() + text[1:]))
                hinweis = []
            else:
                hinweis = []
    return abschnitte


def als_text(daten, vorlage=None, unbekannte_zeilen=()):
    """Die Datei zum Speichern: die Vorlage mit ihren Erklaerungen, die Werte eingesetzt.

    Zeilen mit unbekanntem Feldnamen aus der alten Datei gehen nicht verloren -
    sie stehen am Ende, damit niemand eine Angabe still verliert.
    """
    ausgabe = []
    with open(vorlage or VORLAGE, encoding="utf-8") as f:
        for zeile in f:
            zeile = zeile.rstrip("\n")
            if not zeile.startswith("#") and ":" in zeile:
                feld = zeile.split(":", 1)[0].strip()
                schluessel = NACH_FELDNAME.get(_schluessel(feld))
                if schluessel:
                    wert = " ".join(str(daten.get(schluessel, "")).split())
                    zeile = f"{feld}: {wert}" if wert else f"{feld}:"
            ausgabe.append(zeile)
    if unbekannte_zeilen:
        ausgabe += ["", "# ---------------------------------------------------------------- "
                    "Nicht erkannt", "# Diese Zeilen standen in der alten Datei, passen aber "
                    "zu keinem Feld."]
        ausgabe += list(unbekannte_zeilen)
    return "\n".join(ausgabe) + "\n"


def voller_name(daten):
    return " ".join(daten[k] for k in ("titel", "vorname", "name") if daten.get(k))


def unterschrift_name(daten):
    return daten.get("unterschrift_name") or voller_name(daten)


def wetter_ort(daten):
    """Wetter-Ort, sonst der Wohnort. Ohne Land: Der Ort wird in der Ansage gesprochen."""
    return daten.get("wetter_ort") or daten.get("ort")


def absenderzeilen(daten):
    """Absender nach DIN 5008: Name, Zusatz, Strasse, PLZ Ort, Land in Grossbuchstaben.

    Das Land steht nur, wenn es eingetragen ist - ob ein Brief ins Ausland
    geht, weiss erst die Empfaengeranschrift (kommt mit dem Brief-Ausbau).
    """
    zeilen = []
    if voller_name(daten):
        zeilen.append(voller_name(daten))
    if daten.get("firma"):
        zeilen.append(daten["firma"])
    if daten.get("adresszusatz"):
        zeilen.append(daten["adresszusatz"])
    strasse = " ".join(daten[k] for k in ("strasse", "hausnummer") if daten.get(k))
    if strasse:
        zeilen.append(strasse)
    ort = " ".join(daten[k] for k in ("postleitzahl", "ort") if daten.get(k))
    if ort:
        zeilen.append(ort)
    if daten.get("land"):
        zeilen.append(daten["land"].upper())
    return zeilen


def kontaktzeilen(daten):
    zeilen = []
    for schluessel, wort in (("festnetz_privat", "Telefon"), ("handy_privat", "Mobil"),
                             ("mail", "E-Mail")):
        if daten.get(schluessel):
            zeilen.append(f"{wort}: {daten[schluessel]}")
    return zeilen


def pruefen(daten, unbekannt=()):
    """Liste von Saetzen, was fehlt oder nicht passt. Leer heisst: in Ordnung."""
    meldungen = []
    for nummer, feld, *_ in unbekannt:
        meldungen.append(f"Zeile {nummer}: Das Feld „{feld}“ kenne ich nicht.")
    for schluessel, beschriftung, pflicht in FELDER:
        if pflicht and not daten.get(schluessel):
            meldungen.append(f"Es fehlt: {beschriftung}.")
    for schluessel in TELEFONFELDER:
        wert = daten.get(schluessel)
        if wert and not re.match(r"^(\+|00)[1-9][\d /\-()]{5,}$", wert):
            beschriftung = next(b for s, b, _ in FELDER if s == schluessel)
            meldungen.append(f"{beschriftung}: bitte mit Ländervorwahl, zum Beispiel +49 oder 0043.")
    for schluessel in ("mail", "mail_dienstlich"):
        wert = daten.get(schluessel)
        if wert and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", wert):
            meldungen.append(f"Die E-Mail-Adresse „{wert}“ sieht nicht vollständig aus.")
    if daten.get("postleitzahl") and not re.match(r"^[A-Z0-9][A-Z0-9 \-]{2,9}$",
                                                   daten["postleitzahl"].upper()):
        meldungen.append("Die Postleitzahl sieht nicht richtig aus.")
    if daten.get("ansprache") and daten["ansprache"].lower() not in ("du", "sie"):
        meldungen.append("Ansprache: bitte Du oder Sie.")
    if daten.get("iban") and not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$",
                                          daten["iban"].replace(" ", "").upper()):
        meldungen.append("Die IBAN sieht nicht vollständig aus.")
    if daten.get("unterschrift_bild") and not os.path.isfile(daten["unterschrift_bild"]):
        meldungen.append("Das Bild der Unterschrift gibt es nicht.")
    return meldungen


def _vcard_wert(text):
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def vcard(daten):
    """Eigene Karte als vCard 4.0 - das Format der Thunderbird-Kontakte."""
    z = ["BEGIN:VCARD", "VERSION:4.0"]
    n = [daten.get("name", ""), daten.get("vorname", ""), "", daten.get("titel", ""), ""]
    z.append("N:" + ";".join(_vcard_wert(t) for t in n))
    z.append("FN:" + _vcard_wert(voller_name(daten)))
    adresse = ["", daten.get("adresszusatz", ""),
               " ".join(daten[k] for k in ("strasse", "hausnummer") if daten.get(k)),
               daten.get("ort", ""), daten.get("bundesland", ""), daten.get("postleitzahl", ""),
               daten.get("land", "")]
    if any(adresse):
        z.append("ADR;TYPE=home:" + ";".join(_vcard_wert(t) for t in adresse))
    for schluessel, typ in (("festnetz_privat", "home,voice"), ("handy_privat", "cell"),
                            ("fax_privat", "home,fax"), ("festnetz_dienstlich", "work,voice"),
                            ("handy_dienstlich", "work,cell"), ("fax_dienstlich", "work,fax")):
        if daten.get(schluessel):
            z.append(f"TEL;TYPE=\"{typ}\";VALUE=uri:tel:"
                     + re.sub(r"[^\d+]", "", re.sub(r"^00", "+", daten[schluessel])))
    for schluessel, typ in (("mail", "home"), ("mail_dienstlich", "work")):
        if daten.get(schluessel):
            z.append(f"EMAIL;TYPE={typ}:{daten[schluessel]}")
    if daten.get("webseite"):
        z.append("URL:" + daten["webseite"])
    if daten.get("firma"):
        z.append("ORG:" + _vcard_wert(daten["firma"]))
    if daten.get("position"):
        z.append("TITLE:" + _vcard_wert(daten["position"]))
    z.append("END:VCARD")
    return "\r\n".join(z) + "\r\n"


def main():
    befehl = sys.argv[1] if len(sys.argv) > 1 else "zeigen"
    if befehl == "anlegen":
        if os.path.exists(DATEI):
            print(f"Schon vorhanden, nichts geändert: {DATEI}")
            return 0
        os.makedirs(os.path.dirname(DATEI), exist_ok=True)
        shutil.copyfile(VORLAGE, DATEI)
        os.chmod(DATEI, 0o600)
        print(f"Angelegt: {DATEI} - jetzt ausfüllen.")
        return 0
    if not os.path.exists(DATEI):
        print(f"Keine persönlichen Daten: {DATEI} fehlt. Anlegen mit: {sys.argv[0]} anlegen")
        return 1
    unbekannt = []
    daten = lesen(unbekannt=unbekannt)
    if befehl == "pruefen":
        meldungen = pruefen(daten, unbekannt)
        for m in meldungen:
            print(m)
        if os.stat(DATEI).st_mode & 0o077:
            print(f"Hinweis: Die Datei ist für andere Konten lesbar - chmod 600 {DATEI}")
        if not meldungen:
            print(f"In Ordnung: {len(daten)} Felder ausgefüllt.")
        return 1 if meldungen else 0
    if befehl == "zeigen":
        for schluessel, beschriftung, _ in FELDER:
            if daten.get(schluessel):
                print(f"{beschriftung}: {daten[schluessel]}")
        print("\nAbsender im Brief:")
        for zeile in absenderzeilen(daten) + kontaktzeilen(daten):
            print("  " + zeile)
        print(f"Unterschrift: {unterschrift_name(daten)}")
        print(f"Wetter-Ort: {wetter_ort(daten)}")
        return 0
    if befehl == "vcard":
        sys.stdout.write(vcard(daten))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
