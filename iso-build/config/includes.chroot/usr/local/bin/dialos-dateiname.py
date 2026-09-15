#!/usr/bin/env python3
"""DialOS: Dateinamen mit Datum und Uhrzeit vorne.

Stephans Vorgabe vom 2026-09-15: "Wir muessen aber jedes Dokument / pdf
einzigartig im Dateinamen machen. Also nicht Brief.pdf oder Dokument.doc
sondern immer noch das Datum und die Uhrzeit muss Bestand des Dateinamen sein.
Wegen der Suche: Datum-Uhrzeit (ohne Sekunden)-Brief.doc/pdf". Seine Wahl:

    2026-09-15-1343-Brief.txt
    2026-09-15-1343-Brief.pdf
    2026-09-14-1018-Bildschirmfoto.png

Jahr zuerst, damit sich ein Ordner von selbst zeitlich sortiert und "2026-09"
einen ganzen Monat findet. Gilt fuer Briefe (Text und PDF) und Bildschirmfotos;
das Archiv behaelt seine Namen (nicht gewaehlt).

OHNE SEKUNDEN HEISST: ZWEI IN EINER MINUTE SIND MOEGLICH. Am 2026-09-14 sind
drei Bildschirmfotos zwischen 10:18:09 und 10:18:37 entstanden. Das zweite heisst
dann "...-1018-Bildschirmfoto-2.png". Belegt ist ein Name, sobald es IRGENDEINE
Datei mit diesem Stamm gibt - sonst bekaeme ein neuer Brief den Namen eines
aelteren, dessen PDF schon daneben liegt, und "Brief als PDF speichern"
ueberschriebe das fremde PDF.

"DER BRIEF" IST DER NEUESTE. Bis zum 2026-09-15 gab es genau eine brief.txt,
und der vorige wurde beiseitegelegt. Jetzt behaelt jeder Brief seinen Namen,
und "Brief vorlesen", "Brief drucken" und "Brief als PDF speichern" nehmen den
juengsten nach dem Zeitstempel im Namen.

ALTE NAMEN WERDEN BEIM ERSTEN ZUGRIFF UMGESTELLT (umstellen()), nicht von einem
Einmal-Skript: Das Nutzerkonto liegt auf der verschluesselten Partition und ist
nur offen, wenn der Nutzer angemeldet ist - ein Skript des Admins kaeme gar
nicht hinein. Umbenannt wird nur, gelöscht nie. Als Zeit gilt:
  - brief.txt / brief-STEMPEL.txt: das Aenderungsdatum der Datei. Der Stempel
    im alten Namen ist der Moment des BEISEITELEGENS, nicht des Schreibens.
    Text und PDF desselben alten Stamms bleiben ein Paar.
  - bildschirmfoto-JJJJ-MM-TT-HHMMSS.png und GNOMEs "Bildschirmfoto vom
    JJJJ-MM-TT HH-MM-SS.png": der Stempel im Namen, der ist die Aufnahmezeit.

Aufruf von Hand:  dialos-dateiname.py umstellen   (zeigt, was umbenannt wurde)
"""

import os
import re
import sys
import time

DOKUMENTE = os.path.join(os.path.expanduser("~"), "Dokumente")
BRIEF = "Brief"
BILDSCHIRMFOTO = "Bildschirmfoto"

# Gruppen: Zeit, Art, laufende Nummer (fehlt beim ersten), Endung.
MUSTER = re.compile(r"^(\d{4}-\d{2}-\d{2}-\d{4})-([^.]+?)(?:-(\d+))?\.(\w+)$")


def _belegt(ordner, stamm):
    try:
        return any(n.startswith(stamm + ".") for n in os.listdir(ordner))
    except OSError:
        return False


def neuer_stamm(ordner, art, zeit=None):
    """Freier Stamm "JJJJ-MM-TT-HHMM-Art" (bzw. "...-Art-2") fuer diese Minute."""
    grund = time.strftime("%Y-%m-%d-%H%M", time.localtime(zeit))
    stamm, n = f"{grund}-{art}", 1
    while _belegt(ordner, stamm):
        n += 1
        stamm = f"{grund}-{art}-{n}"
    return stamm


def neuer_pfad(ordner, art, endung, zeit=None):
    os.makedirs(ordner, exist_ok=True)
    return os.path.join(ordner, f"{neuer_stamm(ordner, art, zeit)}.{endung}")


def _schluessel(name):
    """Sortierung nach Zeit und laufender Nummer ("-2" nach dem ohne Nummer)."""
    m = MUSTER.match(name)
    return (m.group(1), int(m.group(3) or 1)) if m else ("", 0)


def neuester(ordner, art, endung):
    """Pfad der juengsten Datei dieser Art, oder None."""
    umstellen(ordner)
    try:
        namen = os.listdir(ordner)
    except OSError:
        return None
    passend = []
    for name in namen:
        m = MUSTER.match(name)
        if m and m.group(2) == art and m.group(4) == endung:
            passend.append(name)
    if not passend:
        return None
    return os.path.join(ordner, max(passend, key=_schluessel))


ALT_BRIEF = re.compile(r"^brief(?:-(\d{4}-\d{2}-\d{2}-\d{6}))?\.(txt|pdf)$")
ALT_FOTO = re.compile(r"^bildschirmfoto-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})\.png$")
# GNOMEs eigene Namen (Druck-Taste) liegen im selben Ordner - mit umgestellt,
# damit der Ordner EINE Sortierung hat.
ALT_GNOME = re.compile(r"^Bildschirmfoto vom (\d{4})-(\d{2})-(\d{2}) (\d{2})-(\d{2})-(\d{2})\.png$")


def umstellen(ordner, melde=None):
    """Benennt alte DialOS-Namen im Ordner um. Gibt [(alt, neu)] zurueck."""
    try:
        namen = sorted(os.listdir(ordner))
    except OSError:
        return []
    erledigt = []

    # Briefe: nach altem Stamm gruppieren, damit Text und PDF ein Paar bleiben.
    gruppen = {}
    for name in namen:
        m = ALT_BRIEF.match(name)
        if m:
            gruppen.setdefault(m.group(1) or "", []).append(name)
    reihenfolge = []
    for alt_stamm, dateien in gruppen.items():
        txt = [d for d in dateien if d.endswith(".txt")]
        bezug = os.path.join(ordner, (txt or dateien)[0])
        try:
            zeit = os.path.getmtime(bezug)
        except OSError:
            continue
        reihenfolge.append((zeit, dateien))
    for zeit, dateien in sorted(reihenfolge):
        stamm = neuer_stamm(ordner, BRIEF, zeit)
        for d in dateien:
            neu = f"{stamm}.{d.rsplit('.', 1)[1]}"
            os.replace(os.path.join(ordner, d), os.path.join(ordner, neu))
            erledigt.append((d, neu))

    # Bildschirmfotos: Zeit steht im Namen.
    for name in namen:
        m = ALT_FOTO.match(name) or ALT_GNOME.match(name)
        if not m:
            continue
        j, mo, t, h, mi, s = (int(x) for x in m.groups())
        zeit = time.mktime((j, mo, t, h, mi, s, 0, 0, -1))
        neu = f"{neuer_stamm(ordner, BILDSCHIRMFOTO, zeit)}.png"
        os.replace(os.path.join(ordner, name), os.path.join(ordner, neu))
        erledigt.append((name, neu))

    if melde:
        for alt, neu in erledigt:
            melde(f"  umbenannt: {alt} -> {neu}")
    return erledigt


def bilder_ordner():
    """Ordner der Bildschirmfotos - wie in dialos-bildschirmfoto.py."""
    import subprocess
    try:
        p = subprocess.run(["xdg-user-dir", "PICTURES"], capture_output=True,
                           text=True, timeout=5)
        ziel = p.stdout.strip()
        if ziel and os.path.isdir(ziel):
            return os.path.join(ziel, "Bildschirmfotos")
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "Bilder", "Bildschirmfotos")


def main():
    if sys.argv[1:] != ["umstellen"]:
        print("Aufruf: dialos-dateiname.py umstellen", file=sys.stderr)
        return 2
    for ordner in (DOKUMENTE, bilder_ordner()):
        paare = umstellen(ordner)
        print(f"{ordner}: {len(paare)} umbenannt")
        for alt, neu in paare:
            print(f"  {alt} -> {neu}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
