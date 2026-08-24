#!/usr/bin/env python3
"""DialOS: legt Briefe und Mails als PDF im Archiv ab.

Stephans Vorgabe vom 2026-08-21: "Jeder Brief und auch jede Mail muss als pdf
Datei in einen extra Ordner gepackt werden."

WO. In ~/Dokumente/Archiv/DialOS-DATA/ - und beim Nutzer zusaetzlich auf dem
Stick. Beide Orte heissen gleich, das ist Stephans Wahl. Die Platte ist der
fuehrende Ort; Begruendung bei ARCHIV weiter unten.

Hier stand bis zum 2026-08-22 das Gegenteil ("auf dem Stick bewusst NICHT",
weil DIALOS-DATA unverschluesseltes exFAT ist und derselbe Stick den
LUKS-Schluessel traegt). Stephan hat anders entschieden, und sein Grund wiegt
schwerer: Ein Archiv nur auf der Platte ist beim naechsten Plattenschaden weg,
und der Nutzer kann es nicht selbst sichern. Der Datenschutz-Einwand ist damit
nicht ausgeraeumt, nur entschieden - ausgefuehrt in
docs/sicherheit-datenschutz.md.

WARUM EIN EIGENER PDF-ERZEUGER UND NICHT LIBREOFFICE. Der Briefbogen ist mit
LEERZEICHEN gesetzt - Absender und Datum stehen rechtsbuendig, weil die Zeile
auf Breite 76 aufgefuellt ist. In einer Proportionalschrift zerfaellt das
sofort. LibreOffice importiert reinen Text mit seiner Standardschrift; das
Ergebnis waere ein Brief, der auf Papier anders aussieht als auf dem Schirm.
Mit cairo (in Debian vorhanden) laesst sich eine Festbreitenschrift setzen,
und die Ausrichtung bleibt genau so, wie sie gemeint war. Nebenbei ist es
schneller: kein Bueroprogramm, das erst startet.

Aufruf:
    dialos-archiv.py ablegen DATEI [--art brief|mail|notiz]
    dialos-archiv.py zeigen                 was im Archiv liegt
"""

import os
import pwd
import subprocess
import sys
import time

HEIM = os.path.expanduser("~")

# ZWEI ORTE, BEIDE PFLICHT (Stephan, 2026-08-22): "alle pdf Dateien ... muessen
# unbedingt auf den Stick Bereich DialOS-DATA und unter Dokumente auf den
# Rechner unter Dokumente/Archiv/DialOS-DATA".
#
# DIE PLATTE IST DER FUEHRENDE ORT, nicht der Stick - und zwar aus einem
# handfesten Grund: Der Stick soll laut docs/sicherheit-datenschutz.md
# getrennt vom Laptop aufbewahrt werden und steckt deshalb meistens NICHT. Ein
# Archiv, das nur dort liegt, waere die meiste Zeit unerreichbar und beim
# Schreiben gar nicht da. Geschrieben wird also immer zuerst auf die Platte;
# der Stick bekommt eine Kopie, sobald er steckt - auch die von frueher.
#
# DER DATENSCHUTZ-EINWAND BLEIBT BESTEHEN und ist nicht ausgeraeumt, nur
# entschieden: DIALOS-DATA ist unverschluesseltes exFAT, und derselbe Stick
# traegt den LUKS-Schluessel. Wer ihn findet, hat beides. Ausgefuehrt in
# docs/sicherheit-datenschutz.md; Stephan kennt den Einwand und will es so.
ARCHIV = os.path.join(HEIM, "Dokumente", "Archiv", "DialOS-DATA")
STICK_KENNUNG = "DIALOS-DATA"

# KONTEN OHNE STICK-ROLLE (Stephan, 2026-08-24): "Beim Admin brauchen wir den
# Stick nicht, stell die Meldung ab. Und wir simulieren beim Admin den Stick
# mit einem Verzeichnis unter Dokumente/Archiv/DialOS-DATA. Den haben wir ja
# dafuer angelegt!"
#
# Fuer diese Konten ist der Ordner auf der Platte nicht die Vorstufe zum Stick,
# sondern das Archiv selbst. Der Stick wird nicht gesucht und nicht bemaengelt.
#
# WARUM ES DIESE LISTE BRAUCHT: exFAT wird mit uid/gid dessen eingehaengt, der
# es einhaengt. Auf dem Entwicklungsgeraet mit zwei Konten heisst das: Wer den
# Stick zuerst einsteckt, besitzt ihn, und das andere Konto kommt nicht einmal
# lesend hinein (gemessen am 2026-08-24: uid=1001,gid=1001,dmask=0022, fuer
# dialosadmin "Keine Berechtigung"). Das ist keine Fehlkonfiguration, sondern
# wie GNOME Wechseldatentraeger einhaengt. Ohne diese Liste schrieb
# dialos-archiv.py deshalb alle 16 Minuten "nicht beschreibbar" ins Protokoll -
# eine Meldung, die niemand liest und die nichts aendert.
#
# Fuer den NUTZER bleibt die Meldung bestehen. Dort ist ein nicht beschreibbarer
# Stick ein echter Fehler: Seine Sicherungskopie entsteht dann nicht.
OHNE_STICK = {"dialosadmin"}
KONTO = pwd.getpwuid(os.getuid()).pw_name
PROTOKOLL = os.path.join(HEIM, ".log", "dialos-archiv.log")

# Seitenmasse in Punkt (1/72 Zoll). A4 = 595 x 842.
SEITE_B, SEITE_H = 595.0, 842.0
RAND = 56.0                 # rund 2 cm
SCHRIFTGROESSE = 10.0
ZEILENHOEHE = 12.5
# Courier ist eine der Grundschriften, die jeder PDF-Betrachter kennt - kein
# eingebetteter Zeichensatz noetig, und sie ist festbreit.
SCHRIFT = "monospace"


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
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def als_pdf(text, ziel):
    """Schreibt reinen Text als PDF - festbreit, damit die Ausrichtung bleibt."""
    import cairo
    zeilen = text.split("\n")
    je_seite = int((SEITE_H - 2 * RAND) / ZEILENHOEHE)
    flaeche = cairo.PDFSurface(ziel, SEITE_B, SEITE_H)
    stift = cairo.Context(flaeche)
    stift.select_font_face(SCHRIFT, cairo.FONT_SLANT_NORMAL,
                           cairo.FONT_WEIGHT_NORMAL)
    stift.set_font_size(SCHRIFTGROESSE)
    stift.set_source_rgb(0, 0, 0)
    for nummer, zeile in enumerate(zeilen):
        if nummer and nummer % je_seite == 0:
            flaeche.show_page()
        y = RAND + (nummer % je_seite + 1) * ZEILENHOEHE
        stift.move_to(RAND, y)
        stift.show_text(zeile)
    flaeche.finish()
    return os.path.exists(ziel) and os.path.getsize(ziel) > 0


def stick():
    """Wohin der Stick eingehaengt ist - oder None.

    Ueber die Datentraeger-KENNUNG, nicht ueber einen festen Pfad: Der
    Einhaengepunkt haengt am angemeldeten Konto (/media/nutzer/... gegen
    /media/dialosadmin/...) und aendert sich mit dem Geraet. Die Kennung
    DIALOS-DATA vergibt dialos-setup-home-partition.sh und ist ueberall
    dieselbe.
    """
    if KONTO in OHNE_STICK:
        # Stumm, mit Absicht. Es ist kein Mangel, dass hier kein Stick ist -
        # dieses Konto hat keine Stick-Rolle. Eine Meldung waere reines
        # Rauschen, und Rauschen macht ein Protokoll unlesbar, in dem sonst
        # echte Fehler stehen.
        return None
    try:
        p = subprocess.run(["findmnt", "-rn", "--source",
                            f"LABEL={STICK_KENNUNG}", "-o", "TARGET"],
                           capture_output=True, text=True, timeout=10)
    except Exception as fehler:
        melde(f"findmnt nicht nutzbar: {fehler}")
        return None
    ziel = p.stdout.strip().splitlines()
    if not ziel:
        return None
    pfad = ziel[0]
    if not os.access(pfad, os.W_OK):
        # Fuer ein Konto MIT Stick-Rolle ist das ein echter Fehler: Die
        # Sicherungskopie entsteht nicht. Deshalb gemeldet, jedes Mal.
        # Konten ohne Stick-Rolle kommen hier nicht mehr an (OHNE_STICK).
        melde(f"Stick unter {pfad}, aber nicht beschreibbar")
        return None
    return pfad


def auf_den_stick(nur_neu=None):
    """Kopiert das Archiv auf den Stick, soweit er da ist.

    Holt auch nach, was frueher entstanden ist, waehrend er nicht steckte -
    sonst waere die Kopie genau dann unvollstaendig, wenn man sie braucht.
    """
    ziel_wurzel = stick()
    if not ziel_wurzel:
        return 0
    ziel = os.path.join(ziel_wurzel, "DialOS-Archiv")
    try:
        os.makedirs(ziel, exist_ok=True)
    except OSError as fehler:
        melde(f"Stick-Ordner nicht anlegbar: {fehler}")
        return 0
    import shutil
    kopiert = 0
    for name in sorted(os.listdir(ARCHIV)) if os.path.isdir(ARCHIV) else []:
        if not name.endswith(".pdf"):
            continue
        if nur_neu and name not in nur_neu:
            continue
        quelle = os.path.join(ARCHIV, name)
        drueben = os.path.join(ziel, name)
        if os.path.exists(drueben) and os.path.getsize(drueben) == os.path.getsize(quelle):
            continue
        try:
            shutil.copyfile(quelle, drueben)
            kopiert += 1
        except OSError as fehler:
            melde(f"Kopie auf den Stick fehlgeschlagen ({name}): {fehler}")
    if kopiert:
        melde(f"{kopiert} Datei(en) auf den Stick kopiert: {ziel}")
    return kopiert


def ablegen(pfad, art):
    if not os.path.exists(pfad) or os.path.getsize(pfad) == 0:
        melde(f"nichts abzulegen: {pfad}")
        return None
    with open(pfad, encoding="utf-8") as f:
        text = f.read()
    os.makedirs(ARCHIV, exist_ok=True)
    ziel = os.path.join(ARCHIV, f"{art}-{time.strftime('%Y-%m-%d-%H%M%S')}.pdf")
    try:
        if not als_pdf(text, ziel):
            melde(f"PDF blieb leer: {ziel}")
            return None
    except Exception as fehler:
        # Ein fehlgeschlagenes Archiv darf den Brief nicht aufhalten - er ist
        # als Textdatei ohnehin schon geschrieben.
        melde(f"PDF fehlgeschlagen: {fehler}")
        return None
    melde(f"abgelegt: {ziel} ({os.path.getsize(ziel)/1024:.0f} kB)")
    auf_den_stick({os.path.basename(ziel)})
    return ziel


def zeigen():
    ort = stick()
    print(f"Platte: {ARCHIV}")
    # "nicht erreichbar" klingt nach Mangel. Fuer ein Konto ohne Stick-Rolle
    # fehlt aber nichts - dort IST die Platte das Archiv.
    if KONTO in OHNE_STICK:
        print("Stick:  keiner fuer dieses Konto - die Platte ist das Archiv")
    else:
        print(f"Stick:  {ort or 'nicht erreichbar'}")
    if not os.path.isdir(ARCHIV):
        print(f"{ARCHIV} gibt es noch nicht.")
        return 0
    dateien = sorted(f for f in os.listdir(ARCHIV) if f.endswith(".pdf"))
    if not dateien:
        print(f"{ARCHIV} ist leer.")
        return 0
    print(f"{len(dateien)} Datei(en) in {ARCHIV}:")
    for name in dateien:
        groesse = os.path.getsize(os.path.join(ARCHIV, name))
        print(f"  {name}  ({groesse/1024:.0f} kB)")
    return 0


def main():
    argumente = sys.argv[1:]
    if argumente and argumente[0] == "zeigen":
        return zeigen()
    art = "brief"
    if "--art" in argumente:
        i = argumente.index("--art")
        if i + 1 < len(argumente):
            art = argumente[i + 1]
        del argumente[i:i + 2]
    if len(argumente) < 2 or argumente[0] != "ablegen":
        print(__doc__.strip().split("Aufruf:")[-1].strip(), file=sys.stderr)
        return 2
    ziel = ablegen(argumente[1], art)
    if not ziel:
        return 1
    print(ziel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
