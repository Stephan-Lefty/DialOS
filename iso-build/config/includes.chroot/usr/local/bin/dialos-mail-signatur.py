#!/usr/bin/env python3
"""DialOS: traegt die Fusszeile als Thunderbird-Signatur ein.

WARUM ES DIESES SKRIPT GIBT. Am 2026-08-20 hat Stephan eine Mail verschickt
und die Fusszeile war nicht darin. Sie konnte nicht darin sein:
dialos-fusszeile.py war gebaut und dokumentiert, aber kein einziges Programm
rief es auf - ein Werkzeug ohne Benutzer. Im Thunderbird-Profil standen null
Signatur-Eintraege. Die Vorgabe lautete "in jedes Dokument, jede Mail und auf
jeden Ausdruck"; fuer die Mail fehlte schlicht die Verbindung.

ZWEI MAILWEGE, DIESES SKRIPT DECKT EINEN AB. Laut docs/anwendungen.md ist
Thunderbird die Oberflaeche, nicht der Motor: DialOS soll spaeter selbst ueber
IMAP/SMTP versenden, weil Thunderbird von aussen nicht steuerbar ist. Dieses
Skript sorgt fuer die Mails, die ueber Thunderbird hinausgehen - also fuer
alles, was der sehende Helfer schreibt. Der eigene Versandweg muss die
Fusszeile selbst holen (dialos-fusszeile.py text --art mail); der Hinweis
steht in TODO.md an der Stelle, an der dieser Weg gebaut wird.

WARUM user.js UND NICHT prefs.js. Thunderbird schreibt prefs.js beim Beenden
neu und wuerde einen Fremdeintrag ueberschreiben oder verlieren. user.js wird
bei JEDEM Start gelesen und ueber prefs.js gelegt. Damit ist die Signatur
dauerhaft gesetzt, auch nachdem jemand in den Kontoeinstellungen etwas
verstellt hat. Der Preis: In der Oberflaeche laesst sie sich nicht dauerhaft
abschalten. Fuer eine Herkunftsangabe, die laut Vorgabe in JEDER Mail stehen
soll, ist das genau richtig.

Aufruf:
    dialos-mail-signatur.py            eintragen
    dialos-mail-signatur.py --zeigen   nur anzeigen, nichts aendern
"""

import os
import re
import shutil
import sys

SIGNATUR_HTML = "/usr/local/share/dialos/mail-signatur.html"
SIGNATUR_TEXT = "/usr/local/share/dialos/mail-signatur.txt"

ANFANG = "// >>> DialOS Fusszeile - erzeugt von dialos-mail-signatur.py"
ENDE = "// <<< DialOS Fusszeile"


def thunderbird_laeuft():
    """Laufendes Thunderbird meldet, sonst geht die Aenderung verloren.

    Der eigene Prozess wird ausgeschlossen - ein Suchmuster auf die
    Befehlszeile hat in diesem Projekt mehrfach das eigene Skript getroffen.
    """
    eigen = str(os.getpid())
    for eintrag in os.listdir("/proc"):
        if not eintrag.isdigit() or eintrag == eigen:
            continue
        try:
            ziel = os.readlink(f"/proc/{eintrag}/exe")
        except OSError:
            continue
        if "thunderbird" in os.path.basename(ziel).lower():
            return True
    return False


def profile(heim=None):
    """Alle Profile mit einem Konto darin.

    Nicht ueber profiles.ini: Dort stehen auch Profile ohne Konto (hier lag
    ein zweites, leeres). Massgeblich ist, ob eine prefs.js ueberhaupt eine
    Identitaet kennt - nur dort ist eine Signatur sinnvoll.
    """
    heim = heim or os.path.expanduser("~")
    wurzel = os.path.join(heim, ".thunderbird")
    gefunden = []
    if not os.path.isdir(wurzel):
        return gefunden
    for name in sorted(os.listdir(wurzel)):
        ordner = os.path.join(wurzel, name)
        prefs = os.path.join(ordner, "prefs.js")
        if not os.path.isfile(prefs):
            continue
        ids = identitaeten(prefs)
        if ids:
            gefunden.append((ordner, ids))
    return gefunden


def identitaeten(prefs):
    """Die Kennungen aller Identitaeten, z.B. ['id1', 'id2']."""
    muster = re.compile(r'mail\.identity\.(id\d+)\.useremail"\s*,\s*"([^"]*)"')
    gefunden = {}
    try:
        with open(prefs, encoding="utf-8", errors="replace") as f:
            for zeile in f:
                treffer = muster.search(zeile)
                if treffer:
                    gefunden[treffer.group(1)] = treffer.group(2)
    except OSError:
        return {}
    return gefunden


def block(ids, datei=SIGNATUR_HTML):
    """Die Zeilen fuer user.js.

    sig_bottom=false: Beim Antworten steht die Fusszeile direkt unter dem
    eigenen Text und nicht unter dem gesamten Zitat. Das Profil antwortet
    oberhalb des Zitats (reply_on_top=1) - stuende die Zeile ganz unten,
    faende sie in einem langen Verlauf niemand.
    """
    zeilen = [ANFANG,
              "// Quelle des Satzes: /usr/local/share/dialos/fusszeile.txt",
              "// Nicht von Hand aendern - wird beim Einrichten neu geschrieben."]
    for kennung in sorted(ids):
        zeilen += [
            f'user_pref("mail.identity.{kennung}.attach_signature", true);',
            f'user_pref("mail.identity.{kennung}.sig_file", "{datei}");',
            f'user_pref("mail.identity.{kennung}.sig_bottom", false);',
        ]
    zeilen.append(ENDE)
    return "\n".join(zeilen) + "\n"


def einsetzen(vorher, neu):
    """Ersetzt einen frueheren DialOS-Block, statt ihn zu verdoppeln."""
    muster = re.compile(re.escape(ANFANG) + r".*?" + re.escape(ENDE) + r"\n?",
                        re.S)
    if muster.search(vorher):
        return muster.sub(neu, vorher, count=1)
    if vorher and not vorher.endswith("\n"):
        vorher += "\n"
    return vorher + neu


def main():
    nur_zeigen = "--zeigen" in sys.argv[1:]
    gefunden = profile()
    if not gefunden:
        print("Kein Thunderbird-Profil mit Konto gefunden - nichts zu tun.",
              file=sys.stderr)
        print("Das Konto wird bei der Ersteinrichtung angelegt; danach dieses "
              "Skript erneut aufrufen.", file=sys.stderr)
        return 1
    if not os.path.isfile(SIGNATUR_HTML):
        print(f"{SIGNATUR_HTML} fehlt. Erst erzeugen mit:", file=sys.stderr)
        print("    dialos-fusszeile.py signatur", file=sys.stderr)
        return 1
    if not nur_zeigen and thunderbird_laeuft():
        print("Thunderbird laeuft. Bitte beenden und erneut aufrufen -",
              file=sys.stderr)
        print("sonst ist die Aenderung beim naechsten Beenden wieder weg.",
              file=sys.stderr)
        return 1

    for ordner, ids in gefunden:
        beschreibung = ", ".join(f"{k}={v}" for k, v in sorted(ids.items()))
        print(f"{os.path.basename(ordner)}: {beschreibung}")
        neu = block(ids)
        if nur_zeigen:
            print(neu.rstrip())
            continue
        pfad = os.path.join(ordner, "user.js")
        vorher = ""
        if os.path.isfile(pfad):
            with open(pfad, encoding="utf-8", errors="replace") as f:
                vorher = f.read()
            shutil.copy2(pfad, pfad + ".vorher")
        with open(pfad, "w", encoding="utf-8") as f:
            f.write(einsetzen(vorher, neu))
        print(f"    eingetragen in {pfad}")
    if not nur_zeigen:
        print("Beim naechsten Start von Thunderbird ist die Fusszeile aktiv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
