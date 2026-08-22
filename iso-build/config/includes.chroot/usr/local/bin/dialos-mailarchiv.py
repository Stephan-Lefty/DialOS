#!/usr/bin/env python3
"""DialOS: legt eingegangene und gesendete Mails als PDF im Archiv ab.

Stephans Wunsch vom 2026-08-22: "Thema PDF Archiv - koennen wir dort auch alle
eingehenden und ausgehenden Mails ablegen!"

OHNE PASSWORT, und das ist der entscheidende Punkt. Der naheliegende Weg waere
IMAP - der braucht die Zugangsdaten des Postfachs, die es auf diesem Geraet
noch gar nicht in einer les baren Datei gibt (siehe TODO.md). Thunderbird
haelt aber lokale Kopien im echten mbox-Format:

    ~/.thunderbird/<profil>/ImapMail/<server>/INBOX
    ~/.thunderbird/<profil>/ImapMail/<server>/Sent

Diese Dateien sind schon da. Kein Passwort, kein Netz, kein zweiter Zugang zum
Postfach - und damit auch keine neue Stelle, an der Zugangsdaten liegen.

WAS DER PREIS DAVON IST, ehrlich: Der lokale Speicher enthaelt nur, was
Thunderbird geholt hat. Wurde eine Mail nie geoeffnet und nicht mitgeladen,
fehlt ihr Text - dann steht im PDF, dass der Text nicht lokal vorlag, statt
eine leere Seite zu erzeugen. Und was Thunderbird nie gesehen hat, sieht auch
dieses Skript nicht. Ein vollstaendiges Archiv gibt es erst mit dem eigenen
IMAP-Weg.

ENTWUERFE WERDEN NICHT ARCHIVIERT. Ein Entwurf ist keine Mail - er wurde weder
empfangen noch gesendet, und er aendert sich noch.

JEDE MAIL NUR EINMAL. Gemerkt wird die Message-ID, nicht der Dateiname: Bei
gleichem Betreff am selben Tag waere der Name doppelt, die ID nie.

Aufruf:
    dialos-mailarchiv.py            zeigt, was neu waere
    dialos-mailarchiv.py --wirklich legt die neuen ab
"""

import email
import email.header
import email.utils
import importlib.util
import mailbox
import os
import re
import sys
import textwrap
import time

HEIM = os.path.expanduser("~")
ARCHIV_SKRIPT = "/usr/local/bin/dialos-archiv.py"
# Der Ort kommt aus dialos-archiv.py - EINE Quelle. Sonst laege das
# Mailarchiv eines Tages woanders als das Briefarchiv.
ARCHIV = None          # wird in main() gesetzt
MERKLISTE = None
PROTOKOLL = os.path.join(HEIM, ".log", "dialos-mailarchiv.log")
BREITE = 76

# Welcher Ordner wird was. "Drafts" fehlt mit Absicht.
ORDNER = {"INBOX": "eingang", "Sent": "ausgang"}


# WARUM IN EINEM VERSTECKTEN ORDNER (Stephan, 2026-08-22): Vorher lagen die
# Protokolle offen im Heimatverzeichnis - zehn laufende und fuenfzehn gedrehte
# Fassungen, also 25 Dateien zwischen "Notizen", "Dokumente" und "Bilder". Der
# Nutzer sieht sie nicht, aber ein sehender Helfer sucht dazwischen. In "~/.log"
# stoeren sie niemanden und sind trotzdem da, wo man sie vermutet.
#
# Der Ordner wird beim Schreiben angelegt, nicht vorausgesetzt: Ein neues Konto
# hat ihn noch nicht, und ein fehlendes Protokoll darf keine Ansage aufhalten.
def melde(text):
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')}  {text}\n")
    except OSError:
        pass


def postfaecher():
    """Alle lokalen mbox-Dateien, die uns interessieren."""
    gefunden = []
    wurzel = os.path.join(HEIM, ".thunderbird")
    if not os.path.isdir(wurzel):
        return gefunden
    for profil in sorted(os.listdir(wurzel)):
        imap = os.path.join(wurzel, profil, "ImapMail")
        if not os.path.isdir(imap):
            continue
        for server in sorted(os.listdir(imap)):
            ordner = os.path.join(imap, server)
            if not os.path.isdir(ordner):
                continue
            for name, richtung in ORDNER.items():
                pfad = os.path.join(ordner, name)
                if os.path.isfile(pfad) and os.path.getsize(pfad) > 0:
                    gefunden.append((pfad, richtung, server))
    return gefunden


def lesbar(kopfzeile):
    """RFC-2047-Kopfzeilen entschluesseln - '=?UTF-8?B?...' wird Text."""
    if not kopfzeile:
        return ""
    teile = []
    for text, kodierung in email.header.decode_header(str(kopfzeile)):
        if isinstance(text, bytes):
            teile.append(text.decode(kodierung or "utf-8", errors="replace"))
        else:
            teile.append(text)
    return "".join(teile).strip()


def text_von(nachricht):
    """Der lesbare Text einer Mail - text/plain bevorzugt, sonst HTML entkernt."""
    roh_html = None
    for teil in nachricht.walk():
        if teil.get_content_maintype() == "multipart":
            continue
        if teil.get_filename():
            continue                    # Anhang - siehe anhaenge()
        art = teil.get_content_type()
        try:
            inhalt = teil.get_payload(decode=True)
        except Exception:
            continue
        if inhalt is None:
            continue
        zeichensatz = teil.get_content_charset() or "utf-8"
        text = inhalt.decode(zeichensatz, errors="replace")
        if art == "text/plain":
            return text
        if art == "text/html" and roh_html is None:
            roh_html = text
    if roh_html is None:
        return None
    # Grob entkernt: Fuer ein Archiv reicht der Wortlaut. Eine echte
    # HTML-Darstellung waere ein eigenes Vorhaben und braeuchte einen Browser.
    ohne = re.sub(r"(?is)<(script|style).*?</\1>", " ", roh_html)
    ohne = re.sub(r"(?s)<br\s*/?>|</p>", "\n", ohne)
    ohne = re.sub(r"(?s)<[^>]+>", "", ohne)
    import html as html_modul
    return html_modul.unescape(ohne)


def anhaenge(nachricht):
    namen = []
    for teil in nachricht.walk():
        name = teil.get_filename()
        if name:
            namen.append(lesbar(name))
    return namen


def als_text(nachricht, richtung):
    """Die Mail als Seite: Kopfblock, dann Text."""
    kopf = [
        f"{'Eingegangene Mail' if richtung == 'eingang' else 'Gesendete Mail'}",
        "",
        f"Von:     {lesbar(nachricht.get('From'))}",
        f"An:      {lesbar(nachricht.get('To'))}",
    ]
    if nachricht.get("Cc"):
        kopf.append(f"Kopie:   {lesbar(nachricht.get('Cc'))}")
    kopf += [
        f"Datum:   {lesbar(nachricht.get('Date'))}",
        f"Betreff: {lesbar(nachricht.get('Subject')) or '(ohne Betreff)'}",
    ]
    dabei = anhaenge(nachricht)
    if dabei:
        kopf.append(f"Anhänge: {', '.join(dabei)}")
    kopf += ["", "-" * BREITE, ""]

    inhalt = text_von(nachricht)
    if inhalt is None:
        koerper = ["(Der Text dieser Mail lag lokal nicht vor. Thunderbird hat",
                   "sie nur als Kopfzeile geholt - siehe Kopf dieses Skripts.)"]
    else:
        koerper = []
        for absatz in inhalt.replace("\r\n", "\n").split("\n"):
            koerper.extend(textwrap.wrap(absatz, BREITE) or [""])
    return "\n".join(kopf + koerper)


def merkliste_lesen():
    try:
        with open(MERKLISTE, encoding="utf-8") as f:
            return {z.strip() for z in f if z.strip()}
    except OSError:
        return set()


def kurz(betreff):
    sauber = re.sub(r"[^\w -]", "", betreff or "").strip()
    return re.sub(r"\s+", "-", sauber)[:40].lower() or "ohne-betreff"


def main():
    wirklich = "--wirklich" in sys.argv[1:]
    faecher = postfaecher()
    if not faecher:
        print("Kein lokales Thunderbird-Postfach gefunden.")
        return 0

    spec = importlib.util.spec_from_file_location("dialos_archiv", ARCHIV_SKRIPT)
    archiv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archiv)
    global ARCHIV, MERKLISTE
    ARCHIV = archiv.ARCHIV
    MERKLISTE = os.path.join(ARCHIV, ".archivierte-mails.txt")
    bekannt = merkliste_lesen()

    neu, uebersprungen = [], 0
    for pfad, richtung, server in faecher:
        for nachricht in mailbox.mbox(pfad):
            kennung = str(nachricht.get("Message-ID", "")).strip()
            if not kennung:
                # Ohne ID koennten wir sie bei jedem Lauf erneut ablegen.
                kennung = f"ohne-id:{lesbar(nachricht.get('Date'))}:{lesbar(nachricht.get('Subject'))}"
            if kennung in bekannt:
                uebersprungen += 1
                continue
            neu.append((kennung, nachricht, richtung))

    print(f"{len(faecher)} Postfach-Datei(en), {uebersprungen} schon archiviert, "
          f"{len(neu)} neu")
    for kennung, nachricht, richtung in neu:
        betreff = lesbar(nachricht.get("Subject")) or "(ohne Betreff)"
        datum = email.utils.parsedate_to_datetime(nachricht.get("Date")) \
            if nachricht.get("Date") else None
        stempel = datum.strftime("%Y-%m-%d-%H%M") if datum else time.strftime("%Y-%m-%d-%H%M")
        name = f"mail-{richtung}-{stempel}-{kurz(betreff)}.pdf"
        print(f"  {name}")
        if not wirklich:
            continue
        os.makedirs(ARCHIV, exist_ok=True)
        ziel = os.path.join(ARCHIV, name)
        try:
            if not archiv.als_pdf(als_text(nachricht, richtung), ziel):
                melde(f"PDF blieb leer: {name}")
                continue
        except Exception as fehler:
            melde(f"PDF fehlgeschlagen ({name}): {fehler}")
            continue
        with open(MERKLISTE, "a", encoding="utf-8") as f:
            f.write(kennung + "\n")
        melde(f"abgelegt: {name}")
    if wirklich:
        # Auch das nachholen, was entstand, waehrend der Stick nicht steckte.
        archiv.auf_den_stick()
    if neu and not wirklich:
        print("\nNichts abgelegt. Mit --wirklich archivieren.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
