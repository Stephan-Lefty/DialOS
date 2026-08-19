#!/usr/bin/env python3
"""DialOS: die Fusszeile fuer Dokumente, Mails und Ausdrucke.

Stephans Vorgabe vom 2026-08-19, Text woertlich:

    Dieses Dokument wurde per Spracheingabe powered by DialOS.org erstellt!

"Ganz dezent und rechtsbuendig."

EINE QUELLE, MEHRERE FORMATE. Der Text steht in
/usr/local/share/dialos/fusszeile.txt und nur dort. Wer ihn aendert, aendert
ihn ueberall - in Briefen, in Mails und auf Ausdrucken. Waere er an drei
Stellen im Code, wuerden zwei davon irgendwann veralten, und niemand
bemerkte es, weil kaum jemand alle drei Wege am selben Tag benutzt.

NICHT IN NOTIZEN (Stephans Entscheidung, 2026-08-19). Der Einkaufszettel
wird bei jedem Diktat ERGAENZT - eine Fusszeile landete dort bei jedem
Durchgang mitten im Text und muesste bei jedem Anhaengen nach unten
geschoben werden. Notizen sind Arbeitszettel, keine Dokumente. Wird ein
Zettel gedruckt, kommt die Zeile beim Drucken dazu.

"DOKUMENT" ODER "NACHRICHT": In einer Mail klingt "Dieses Dokument" schief -
eine Mail ist kein Dokument. Mit "--art mail" wird daraus "Diese Nachricht".
Der Rest des Satzes bleibt woertlich wie vorgegeben.

Aufruf:
    dialos-fusszeile.py text                  nur den Satz
    dialos-fusszeile.py text --art mail       mit "Diese Nachricht"
    dialos-fusszeile.py anhaengen DATEI       Inhalt + rechtsbuendige Fusszeile
    dialos-fusszeile.py drucken DATEI         dasselbe direkt an den Drucker
"""

import os
import subprocess
import sys

QUELLE = "/usr/local/share/dialos/fusszeile.txt"
ERSATZ = "Dieses Dokument wurde per Spracheingabe powered by DialOS.org erstellt!"

# Breite fuer den rechtsbuendigen Satz im reinen Text. 76 Zeichen passen in
# jedes Terminal und auf jeden Ausdruck in Standardschrift.
BREITE = 76


def text(art="dokument"):
    """Der Satz, aus der einen Quelle.

    Faellt die Datei aus, wird der eingebaute Satz benutzt - eine fehlende
    Fusszeile waere ein stiller Fehler, und stille Fehler sind in diesem
    Projekt teuer geworden.
    """
    try:
        with open(QUELLE, encoding="utf-8") as f:
            satz = f.read().strip()
    except OSError:
        satz = ERSATZ
    if not satz:
        satz = ERSATZ
    if art == "mail":
        satz = satz.replace("Dieses Dokument wurde", "Diese Nachricht wurde", 1)
    return satz


def rechtsbuendig(satz, breite=BREITE):
    """Rechtsbuendig durch Leerzeichen - im reinen Text der einzige Weg.

    Ist der Satz laenger als die Breite, bleibt er ungekuerzt linksbuendig
    stehen. Ein abgeschnittener Herkunftshinweis waere schlechter als ein
    nicht ausgerichteter.
    """
    return satz.rjust(breite) if len(satz) < breite else satz


def anhaengen(pfad, art="dokument", breite=BREITE):
    try:
        with open(pfad, encoding="utf-8") as f:
            inhalt = f.read().rstrip("\n")
    except OSError as fehler:
        print(f"Nicht lesbar: {fehler}", file=sys.stderr)
        return None
    # Zwei Leerzeilen Abstand - "ganz dezent" heisst auch, dass die Zeile
    # nicht am Text klebt.
    return f"{inhalt}\n\n\n{rechtsbuendig(text(art), breite)}\n"


def drucken(pfad, art="dokument"):
    fertig = anhaengen(pfad, art)
    if fertig is None:
        return 1
    try:
        p = subprocess.run(["lp", "-"], input=fertig.encode("utf-8"),
                           capture_output=True, timeout=30)
    except FileNotFoundError:
        print("lp fehlt - CUPS nicht installiert?", file=sys.stderr)
        return 1
    if p.returncode != 0:
        print(p.stderr.decode(errors="replace").strip(), file=sys.stderr)
        return 1
    print(p.stdout.decode(errors="replace").strip())
    return 0


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    art = "mail" if "mail" in " ".join(sys.argv) else "dokument"
    if not argumente:
        print(__doc__.strip().split("Aufruf:")[-1].strip(), file=sys.stderr)
        return 2
    was = argumente[0]
    if was == "text":
        print(text(art))
        return 0
    if was in ("anhaengen", "drucken"):
        if len(argumente) < 2:
            print(f"Aufruf: dialos-fusszeile.py {was} DATEI", file=sys.stderr)
            return 2
        if was == "anhaengen":
            fertig = anhaengen(argumente[1], art)
            if fertig is None:
                return 1
            sys.stdout.write(fertig)
            return 0
        return drucken(argumente[1], art)
    print(f"Unbekannt: {was}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
