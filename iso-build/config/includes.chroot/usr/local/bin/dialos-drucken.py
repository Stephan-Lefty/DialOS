#!/usr/bin/env python3
"""DialOS: druckt einen Brief, eine Notiz oder den Einkaufszettel.

Stephans Vorgabe vom 2026-08-21: "der Brief muss dann, wenn er fertig ist,
gedruckt werden".

DER DRUCKER WIRD GESUCHT, NICHT VORAUSGESETZT. Auf diesem Geraet ist ein
Brother HL-L2350DW eingerichtet, aber CUPS hat KEIN Standardziel ("keine
systemvoreingestellten Ziele", geprueft 2026-08-22). Ein blosses "lp -" liefe
damit ins Leere - genau der stille Fehler, den ein blinder Nutzer nicht sieht.
Statt auf jedem Geraet eine Voreinstellung zu setzen, die anders heisst,
fragt dieses Skript CUPS:

  1. Gibt es ein Standardziel? Dann das.
  2. Sonst: Gibt es genau einen Drucker? Dann den.
  3. Sonst: Nachfragen waere hier falsch - der Nutzer sieht die Liste nicht.
     Es nimmt den ersten und SAGT, welchen.

DIE FUSSZEILE KOMMT NUR DAHIN, WO SIE FEHLT. Ein Brief traegt sie schon, er
ist als Briefbogen entstanden - ein zweites Mal angehaengt stuende sie doppelt
auf dem Blatt. Notizen und Einkaufszettel haben bewusst keine (Stephans
Entscheidung vom 2026-08-19: Arbeitszettel, keine Dokumente); beim Ausdruck
kommt sie dazu, weil ein Blatt Papier das Haus verlaesst.

Aufruf:
    dialos-drucken.py brief
    dialos-drucken.py einkaufszettel
    dialos-drucken.py notizen
"""

import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
NAMEN_SKRIPT = "/usr/local/bin/dialos-namen.py"
FUSSZEILE_SKRIPT = "/usr/local/bin/dialos-fusszeile.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-drucken.log")

# Papier und Ausrichtung werden ausdruecklich mitgegeben, nicht dem Drucker
# ueberlassen: Am 2026-08-22 kam ein Ausdruck quer statt hochkant heraus.
# Nachgemessen ist, dass es NICHT an CUPS lag - texttopdf und pdftopdf
# liefern mit dem PPD dieser Warteschlange 595x842 Punkte, Drehung 0, also
# A4 hochkant. Die Drehung entstand erst danach, im Drucker. Den fragt man
# an dieser Stelle nicht, dem sagt man es.
#   orientation-requested: 3 = hochkant, 4 = quer (RFC 8011)
DRUCK_OPTIONEN = ["-o", "media=A4", "-o", "orientation-requested=3"]


HEIM = os.path.expanduser("~")
# Wo was liegt - dieselbe Aufteilung wie beim Schreiben: Briefe sind
# Dokumente, Zettel sind Notizen.
# Bezeichnung MIT Beugung. Ohne sie sagt DialOS "Die Notizen wird gedruckt"
# und "Die Notizen ist leer" - genau der Fehler, den dialos-notiz.py mit
# benennen() schon einmal geloest hat. Aufgefallen erst beim Nachziehen der
# Ansagen-Sammlung am 2026-08-22; gesprochen haette ihn jeder sofort gehoert.
#
# Felder: Pfad, Bezeichnung, "wird/werden", "ist/sind", Fusszeile noetig?
ZIELE = {
    "brief": (os.path.join(HEIM, "Dokumente", "brief.txt"),
              "Der Brief", "wird", "ist", False),
    "notizen": (os.path.join(HEIM, "Notizen", "notizen.txt"),
                "Die Notizen", "werden", "sind", True),
    "einkaufszettel": (os.path.join(HEIM, "Notizen", "einkaufszettel.txt"),
                       "Der Einkaufszettel", "wird", "ist", True),
}


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


def anrede(satz):
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dialos_namen", NAMEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.anrede(satz)
    except Exception:
        return satz


def sprich(text):
    try:
        if os.access(SAY, os.X_OK):
            subprocess.run([SAY, text], capture_output=True, timeout=60)
        else:
            print(text, flush=True)
    except Exception as fehler:
        melde(f"Ansage fehlgeschlagen: {fehler}")


def drucker():
    """Das Ziel, an das gedruckt wird - oder None."""
    try:
        p = subprocess.run(["lpstat", "-d"], capture_output=True, text=True, timeout=10)
        for zeile in p.stdout.splitlines():
            if ":" in zeile:
                name = zeile.split(":", 1)[1].strip()
                if name:
                    melde(f"Standardziel: {name}")
                    return name
    except Exception as fehler:
        melde(f"lpstat -d nicht nutzbar: {fehler}")
    try:
        p = subprocess.run(["lpstat", "-p"], capture_output=True, text=True, timeout=10)
        namen = [z.split()[1] for z in p.stdout.splitlines()
                 if z.startswith("Drucker") or z.startswith("printer")]
    except Exception as fehler:
        melde(f"lpstat -p nicht nutzbar: {fehler}")
        return None
    if not namen:
        return None
    if len(namen) > 1:
        melde(f"{len(namen)} Drucker, genommen wird der erste: {namen[0]}")
    return namen[0]


def text_fuer(name):
    """Der zu druckende Text - mit Fusszeile, wo sie fehlt."""
    pfad, bezeichnung, _wird, _ist, braucht_fusszeile = ZIELE[name]
    if not os.path.exists(pfad) or os.path.getsize(pfad) == 0:
        return None, bezeichnung
    if not braucht_fusszeile:
        with open(pfad, encoding="utf-8") as f:
            return f.read(), bezeichnung
    try:
        p = subprocess.run([FUSSZEILE_SKRIPT, "anhaengen", pfad],
                           capture_output=True, text=True, timeout=30)
        if p.returncode == 0 and p.stdout:
            return p.stdout, bezeichnung
        melde(f"Fusszeile fehlgeschlagen: {p.stderr.strip()}")
    except Exception as fehler:
        melde(f"Fusszeile nicht aufrufbar: {fehler}")
    # Lieber ohne Fusszeile drucken als gar nicht.
    with open(pfad, encoding="utf-8") as f:
        return f.read(), bezeichnung


def main():
    if not sys.argv[1:] or sys.argv[1] not in ZIELE:
        print(f"Aufruf: dialos-drucken.py {'|'.join(ZIELE)}", file=sys.stderr)
        return 2
    name = sys.argv[1]
    melde(f"=== drucken {name} ===")

    _pfad, bezeichnung, wird, ist, _f = ZIELE[name]
    text, _bez = text_fuer(name)
    if text is None:
        melde("nichts zu drucken")
        sprich(f"{bezeichnung} {ist} leer. Es gibt nichts zu drucken.")
        return 0

    ziel = drucker()
    if not ziel:
        melde("kein Drucker gefunden")
        sprich(anrede("ich finde keinen Drucker."))
        return 1

    try:
        p = subprocess.run(["lp", "-d", ziel] + DRUCK_OPTIONEN + ["-"],
                           input=text.encode("utf-8"),
                           capture_output=True, timeout=60)
    except Exception as fehler:
        melde(f"lp nicht aufrufbar: {fehler}")
        sprich(anrede("ich konnte nicht drucken."))
        return 1
    if p.returncode != 0:
        melde(f"lp meldet: {p.stderr.decode(errors='replace').strip()}")
        sprich(anrede("der Drucker hat den Auftrag nicht angenommen."))
        return 1

    auftrag = p.stdout.decode(errors="replace").strip()
    melde(f"gedruckt auf {ziel}: {auftrag}")
    # Die Anzahl der Seiten waere schoener, aber lp kennt sie nicht - und eine
    # geratene Zahl waere schlechter als keine.
    sprich(f"{bezeichnung} {wird} gedruckt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
