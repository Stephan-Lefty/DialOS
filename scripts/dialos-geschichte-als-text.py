#!/usr/bin/env python3
"""Macht aus der Entstehungsgeschichte eine reine Textdatei.

Fuer Stephan auf der externen Platte - lesbar mit jedem Programm und mit
jedem Screenreader, ohne Markdown-Zeichen im Weg.

ZWEI FEHLER, DIE HIER SCHON BEHOBEN SIND, weil sie beim ersten Anlauf am
2026-08-18 beide zugeschlagen haben:

1. Der Kopf stand elfmal in der Datei. In Python werden aufeinanderfolgende
   Zeichenketten verkettet, BEVOR "* 76" greift - multipliziert wurde also
   der ganze Block statt der Trennlinie. Deshalb wird der Kopf hier Zeile
   fuer Zeile als Liste gebaut.
2. Kursiv-Sternchen ueberlebten, weil die Auszeichnung ueber zwei Zeilen
   ging und ich zeilenweise ersetzt habe. Deshalb laufen die
   Auszeichnungs-Ersetzungen jetzt ueber den GANZEN Text, mit re.S.

Aufruf:  scripts/dialos-geschichte-als-text.py [de|en] [ZIELDATEI]
"""

import os
import re
import sys
import textwrap

BREITE = 76
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATTE = "/media/dialosadmin/SanDisk-Extreme/DialOS"

FASSUNGEN = {
    "de": {
        "quelle": "docs/entstehungsgeschichte.md",
        "ziel": os.path.join(PLATTE, "DialOS-Entstehungsgeschichte.txt"),
        "h1": r'^#\s+Dreizehn Tage\s*$',
        "kopf": [
            "DIALOS - DREIZEHN TAGE",
            "Die Entstehung, vom 6. bis 18. August 2026. 194 Commits.",
        ],
        "hinweis": [
            "Erzeugt aus docs/entstehungsgeschichte.md im DialOS-Repository.",
            "Alles darin ist belegt - im Aenderungsprotokoll, in den",
            "Protokolldateien und in der Git-Historie. Es ist nichts",
            "hinzugefuegt. Zugespitzt ist nur die Form.",
        ],
    },
    "en": {
        "quelle": "docs/entstehungsgeschichte.en.md",
        "ziel": os.path.join(PLATTE, "DialOS-Thirteen-Days.txt"),
        "h1": r'^#\s+Thirteen Days\s*$',
        "kopf": [
            "DIALOS - THIRTEEN DAYS",
            "How it came to exist, 6 to 18 August 2026. 194 commits.",
        ],
        "hinweis": [
            "Generated from docs/entstehungsgeschichte.en.md in the DialOS",
            "repository. Everything in it is on the record - in the changelog,",
            "in the log files and in the git history. Nothing has been added.",
            "Only the form is sharpened.",
        ],
    },
}


def umwandeln(roh, h1_muster):
    roh = re.sub(r'^\[Deutsch\][^\n]*\n', '', roh)
    roh = re.sub(h1_muster, '', roh, flags=re.M)
    # Fehler 2: ueber den ganzen Text, nicht je Zeile
    roh = re.sub(r'\*\*(.+?)\*\*', r'\1', roh, flags=re.S)
    roh = re.sub(r'(?<!\*)\*(.+?)\*(?!\*)', r'\1', roh, flags=re.S)

    aus, in_code = [], False
    for zeile in roh.split("\n"):
        if zeile.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            aus.append("      " + zeile)
            continue
        if zeile.strip() == "---":
            aus += ["", "-" * BREITE]
            continue
        m = re.match(r'^(#{2,3})\s+(.*)$', zeile)
        if m:
            titel = m.group(2)
            aus += ["", titel, "-" * min(len(titel), BREITE), ""]
            continue
        t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', zeile).replace('`', '')
        if not t.strip():
            aus.append("")
            continue
        if t.startswith(">"):
            aus += ["      " + u
                    for u in textwrap.wrap(t.lstrip("> ").strip(), BREITE - 6)]
            continue
        if t.startswith("- "):
            umbruch = textwrap.wrap(t[2:].strip(), BREITE - 4)
            aus.append("  - " + (umbruch[0] if umbruch else ""))
            aus += ["    " + u for u in umbruch[1:]]
            continue
        aus += textwrap.wrap(t.strip(), BREITE)
    return re.sub(r'\n{3,}', '\n\n', "\n".join(aus)).strip()


def main():
    sprachen = [a for a in sys.argv[1:] if a in FASSUNGEN] or list(FASSUNGEN)
    for sprache in sprachen:
        f = FASSUNGEN[sprache]
        quelle = os.path.join(REPO, f["quelle"])
        text = umwandeln(open(quelle, encoding="utf-8").read(), f["h1"])
        linie = "=" * BREITE
        # Fehler 1: Kopf als LISTE, nicht als verkettete Literale
        kopf = [linie] + f["kopf"] + [linie, ""] + f["hinweis"] + [""]
        with open(f["ziel"], "w", encoding="utf-8") as z:
            z.write("\n".join(kopf) + "\n" + text + "\n")
        groesse = os.path.getsize(f["ziel"])
        zeilen = text.count("\n") + len(kopf) + 1
        print(f"  {sprache}: {f['ziel']}")
        print(f"      {groesse} Bytes, {zeilen} Zeilen")


if __name__ == "__main__":
    main()
