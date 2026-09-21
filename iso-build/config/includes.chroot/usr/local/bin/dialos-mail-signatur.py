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
    dialos-mail-signatur.py --anmelden beim Anmelden: eigene Signatur neu schreiben,
                                       user.js nur, wenn sich etwas aendert

NAME UND KONTAKT AUS DEN PERSOENLICHEN DATEN (2026-09-17). Seit es
~/.config/dialos/persoenliche-daten.txt gibt, steht ueber der DialOS-Zeile die
Signatur der Person: Name, Anschrift, Telefon, Mail. Sie ist je KONTO
verschieden und liegt deshalb im Konto (~/.config/dialos/mail-signatur.html),
nicht in /usr/local/share - dort bleibt die reine DialOS-Zeile fuer Konten
ohne Daten. Die Datei wird bei jedem Anmelden neu geschrieben
(dialos-mail-signatur.service), damit eine in der Eingabemaske geaenderte
Telefonnummer spaetestens beim naechsten Anmelden in der Mail steht.
Thunderbird liest die Signaturdatei beim Verfassen, nicht beim Start.
"""

import os
import re
import shutil
import sys

SIGNATUR_HTML = "/usr/local/share/dialos/mail-signatur.html"
WOERTERBUCH = "de-DE"
SIGNATUR_TEXT = "/usr/local/share/dialos/mail-signatur.txt"
EIGENE_HTML = os.path.join(os.path.expanduser("~"), ".config", "dialos", "mail-signatur.html")
EIGENE_TEXT = os.path.join(os.path.expanduser("~"), ".config", "dialos", "mail-signatur.txt")
PERSOENLICHE_DATEN_SKRIPT = "/usr/local/bin/dialos-persoenliche-daten.py"


def html_sicher(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def eigene_signatur():
    """Schreibt die Signatur mit Name und Kontakt ins Konto. Pfad oder None.

    None heisst: keine persoenlichen Daten - dann gilt die reine DialOS-Zeile.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("persoenliche_daten",
                                                      PERSOENLICHE_DATEN_SKRIPT)
        pd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pd)
        daten = pd.lesen()
    except Exception:
        return None
    name = pd.voller_name(daten)
    if not name:
        return None
    anschrift = " · ".join(z for z in (
        " ".join(daten[k] for k in ("strasse", "hausnummer") if daten.get(k)),
        " ".join(daten[k] for k in ("postleitzahl", "ort") if daten.get(k))) if z)
    kontakt = " · ".join(f"{wort} {daten[k]}" for k, wort in (
        ("festnetz_privat", "Tel."), ("handy_privat", "Mobil"), ("mail", "E-Mail"))
        if daten.get(k))
    zeilen = [z for z in (name, anschrift, kontakt) if z]
    try:
        with open(SIGNATUR_HTML, encoding="utf-8") as f:
            fuss_html = f.read().strip()
        with open(SIGNATUR_TEXT, encoding="utf-8") as f:
            fuss_text = f.read().strip()
    except OSError:
        fuss_html = fuss_text = ""
    # Dezent wie die DialOS-Zeile, aber links: Das ist der Absender, keine Werbung.
    html = ('<div style="font-size:90%; color:#555555;">'
            + "<br>".join(html_sicher(z) for z in zeilen) + "</div>\n" + fuss_html + "\n")
    text = "-- \n" + "\n".join(zeilen) + ("\n\n" + fuss_text if fuss_text else "") + "\n"
    os.makedirs(os.path.dirname(EIGENE_HTML), exist_ok=True)
    for ziel, inhalt in ((EIGENE_HTML, html), (EIGENE_TEXT, text)):
        vorher = None
        try:
            with open(ziel, encoding="utf-8") as f:
                vorher = f.read()
        except OSError:
            pass
        if vorher != inhalt:
            with open(ziel + ".neu", "w", encoding="utf-8") as f:
                f.write(inhalt)
            os.replace(ziel + ".neu", ziel)
    return EIGENE_HTML

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
              "// Nicht von Hand aendern - wird beim Einrichten neu geschrieben.",
              # DEUTSCHE RECHTSCHREIBPRUEFUNG (Stephan, 2026-09-21, im
              # Verfassen-Fenster gesehen: "unten rechts steht was von
              # englisch"). Ohne Einstellung prueft Thunderbird gegen en-US -
              # dann steht unter jedem deutschen Wort eine Wellenlinie, und wer
              # den Bildschirm nicht sieht, merkt nicht einmal, dass die
              # Pruefung nichts taugt. Die Woerterbuecher sind da
              # (hunspell-de-de, thunderbird-l10n-de), nur nicht gewaehlt.
              # Stephans Wahl: Deutschland, weil die Post dorthin geht.
              f'user_pref("spellchecker.dictionary", "{WOERTERBUCH}");']
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
    anmelden = "--anmelden" in sys.argv[1:]
    datei = (None if nur_zeigen else eigene_signatur()) or SIGNATUR_HTML
    if nur_zeigen and os.path.isfile(EIGENE_HTML):
        datei = EIGENE_HTML
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
    if not nur_zeigen and not anmelden and thunderbird_laeuft():
        print("Thunderbird laeuft. Bitte beenden und erneut aufrufen -",
              file=sys.stderr)
        print("sonst ist die Aenderung beim naechsten Beenden wieder weg.",
              file=sys.stderr)
        return 1

    for ordner, ids in gefunden:
        beschreibung = ", ".join(f"{k}={v}" for k, v in sorted(ids.items()))
        print(f"{os.path.basename(ordner)}: {beschreibung}")
        neu = block(ids, datei)
        if nur_zeigen:
            print(neu.rstrip())
            continue
        pfad = os.path.join(ordner, "user.js")
        vorher = ""
        if os.path.isfile(pfad):
            with open(pfad, encoding="utf-8", errors="replace") as f:
                vorher = f.read()
            if einsetzen(vorher, neu) == vorher:
                # Beim Anmelden der Normalfall: nichts zu tun, keine Sicherungskopie.
                continue
        if anmelden and thunderbird_laeuft():
            # Laeuft Thunderbird schon, waere die Aenderung beim Beenden weg - dann
            # beim naechsten Anmelden. Die Signaturdatei selbst ist schon neu.
            print("    Thunderbird laeuft - user.js beim naechsten Anmelden")
            continue
            shutil.copy2(pfad, pfad + ".vorher")
        with open(pfad, "w", encoding="utf-8") as f:
            f.write(einsetzen(vorher, neu))
        print(f"    eingetragen in {pfad}")
    if not nur_zeigen:
        print("Beim naechsten Start von Thunderbird ist die Fusszeile aktiv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
