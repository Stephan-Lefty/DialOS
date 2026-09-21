#!/usr/bin/env python3
"""Programme auf Zuruf oeffnen - "Postfach oeffnen", "neue E-Mail schreiben".

WARUM ES DAS GIBT (Stephan, 2026-09-21): "Wir muessen doch sowieso eine Liste
von Befehlen machen, die dann die Programme startet." Bis hierher konnte DialOS
alles selbst - vorlesen, diktieren, drucken, suchen - aber kein Programm
oeffnen. Fuer einen sehenden Helfer am selben Geraet ist das der fehlende
Handgriff, und fuer den Nutzer ist es der Weg zu allem, was DialOS (noch) nicht
per Sprache kann.

ES GIBT EINEN ZWEITEN GRUND, UND DER IST NEU SEIT HEUTE: Entwuerfe und Kontakte
gehen jetzt ueber die Thunderbird-Erweiterung, nicht mehr in dessen Dateien
(siehe dialos-thunderbird-bruecke.py). Damit ist ein GESCHLOSSENER Thunderbird
der einzige Fall, in dem etwas vorgemerkt werden muss. "Postfach oeffnen" loest
genau das auf: Thunderbird startet, die Bruecke arbeitet die Warteschlange ab,
der Entwurf liegt im Postfach.

EINE LISTE, NICHT ZWEI. Die Saetze stehen hier und nur hier;
dialos-sprachbefehl-desktop.py liest sie beim Start aus dieser Datei. Eine
zweite Liste in der Grammatik liefe beim naechsten Programm auseinander, und
zwar unbemerkt - dieselbe Ueberlegung wie bei den Erweiterungen.

WAS NICHT DRIN STEHT: Programme schliessen. Ein "Postfach schliessen" waere
verlockend, kann aber ungespeicherte Arbeit eines sehenden Helfers wegwerfen -
und der Nutzer hoert nicht, was dabei verlorenginge. Beenden bleibt Handarbeit,
bis es einen Grund gibt, der das aufwiegt.

DAS FENSTER NACH VORN ZU HOLEN, BRAUCHT DIE .desktop-DATEI - GEMESSEN AM
2026-09-21. Hier stand vorher, ein zweiter Start hebe das vorhandene Fenster
von selbst. Stephan hat das Gegenteil gesehen: "Wenn Thunderbird bereits offen
ist, dann wird bei Postfach oeffnen das vorhandene Fenster nicht nach vorn
geholt."

WARUM, UND WARUM DAS KEIN FEHLER VON THUNDERBIRD IST: Unter Wayland darf ein
fremder Prozess kein Fenster nach vorn holen - das ist ausdruecklich
unterbunden, damit kein Hintergrundprogramm dem Nutzer ins Bild springt. Heben
darf sich nur die Anwendung selbst, und nur mit einem Aktivierungs-Token
(XDG_ACTIVATION_TOKEN), das ihr beim Start mitgegeben wird. Ein Token gibt es
aber nur, wenn ueber die .desktop-Datei gestartet wird - "/usr/bin/thunderbird"
von Hand aufgerufen bekommt keins. Genau das stand hier.

AUCH MIT DER .desktop-DATEI GEHT ES NICHT - ZWEIMAL GEMESSEN AM 2026-09-21.

Erster Lauf: "Fenster kommt nicht nach vorne, es erscheint nur oben mittig ein
Hinweis von Gnome." Dieser Lauf zaehlte nicht, und das Eingestaendnis gehoert
hierher: Thunderbird war dabei ZU - die Prozessliste zeigte hinterher, dass
der Aufruf es erst gestartet hatte. Gemessen war damit nur der Fokus-Schutz
beim Neustart, nicht das Heben eines vorhandenen Fensters. Ich hatte die
Begruendung schon geschrieben, bevor das auffiel.

Zweiter Lauf, mit LAUFENDEM Thunderbird und derselbe Aufruf: "Fenster bleibt
hinten." Damit steht es: Auch mit Aktivierungs-Token hebt sich das vorhandene
Fenster nicht. GNOME meldet stattdessen "Thunderbird ist bereit" und
ueberlaesst dem Nutzer den Klick - das ist der Schutz davor, dass Programme
sich in den Vordergrund draengen, und er greift auch hier.

DAMIT IST DER PUNKT ERLEDIGT, NICHT OFFEN. Es gibt keinen dritten Weg: wmctrl
und xdotool sind nicht installiert und waeren unter Wayland wirkungslos, die
GNOME-Schnittstelle ist gesperrt, und ein Fenster von aussen zu heben ist dort
ausdruecklich nicht vorgesehen.

"gio launch" BLEIBT TROTZDEM, aus einem anderen Grund: Ueber die
.desktop-Datei gestartet laeuft das Programm in seiner EIGENEN systemd-Einheit
und nicht in der des Sprachdienstes - genau der Fehler, der beim
Bildschirmfoto drei Wochen unbemerkt blieb (CLAUDE.md, Regel vom 2026-09-14).

WAS DER NUTZER STATTDESSEN BEKOMMT: eine Auskunft. Laeuft das Programm schon,
sagt DialOS das ("Das Postfach ist schon offen.") - fuer jemanden, der den
Bildschirm nicht sieht, ist der Zustand die Antwort, nicht das Fenster. Der
sehende Helfer daneben sieht GNOMEs Hinweis.

"gio launch" uebergibt Argumente als DATEINAMEN, nicht als Schalter - fuer
"-compose", "-calendar" und "-addressbook" bleibt der direkte Aufruf. Dort
entsteht ohnehin ein NEUES Fenster, und ein neues kommt nach vorn.

Aufruf:
  dialos-programm.py "postfach öffnen"      # startet und sagt es an
  dialos-programm.py --liste                # alle Saetze, fuer die Doku
"""

import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
GIO = "/usr/bin/gio"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-programm.log")

# Satz -> was passiert. "befehl" ist die Programmzeile, "ansage" das, was der
# Nutzer hoert, "fehlt" der Satz fuer den Fall, dass das Programm nicht
# installiert ist (bei einem Kundengeraet ohne Radio zum Beispiel).
#
# DIE ZWECKE STAMMEN AUS docs/anwendungen.md - dort steht, WARUM es dieses
# Programm ist und kein anderes. Hier steht nur, wie man es ruft.
PROGRAMME = {
    "postfach öffnen": {
        "offen": "Das Postfach ist schon offen.",
        "befehl": ["/usr/bin/thunderbird"],
        "fenster": "/usr/share/applications/thunderbird.desktop",
        "ansage": "Ich öffne das Postfach.",
    },
    # ZWEI SAETZE FUER DASSELBE, wie bei "auf Linux"/"auf Gnome" und
    # "Brief aufnehmen"/"Brief schreiben": Niemand soll sich eine Formulierung
    # merken muessen. "e mail" ohne Bindestrich, weil die Grammatik Woerter
    # zaehlt, nicht Schreibweisen - gesprochen ist es dasselbe.
    "neue e mail schreiben": {
        "befehl": ["/usr/bin/thunderbird", "-compose"],
        "ansage": "Ich öffne ein leeres E-Mail-Fenster.",
    },
    "e mail schreiben": {
        "befehl": ["/usr/bin/thunderbird", "-compose"],
        "ansage": "Ich öffne ein leeres E-Mail-Fenster.",
    },
    "kalender öffnen": {
        "befehl": ["/usr/bin/thunderbird", "-calendar"],
        "ansage": "Ich öffne den Kalender.",
    },
    "kontakte öffnen": {
        "befehl": ["/usr/bin/thunderbird", "-addressbook"],
        "ansage": "Ich öffne die Kontakte.",
    },
    "internet öffnen": {
        "offen": "Das Internet ist schon offen.",
        "fenster": "/usr/share/applications/firefox-esr.desktop",
        "befehl": ["/usr/bin/firefox-esr"],
        "ansage": "Ich öffne das Internet.",
    },
    "browser öffnen": {
        "offen": "Der Browser ist schon offen.",
        "fenster": "/usr/share/applications/firefox-esr.desktop",
        "befehl": ["/usr/bin/firefox-esr"],
        "ansage": "Ich öffne den Browser.",
    },
    "musik öffnen": {
        "offen": "Die Musik läuft schon.",
        "fenster": "/usr/share/applications/org.gnome.Rhythmbox3.desktop",
        "befehl": ["/usr/bin/rhythmbox"],
        "ansage": "Ich öffne die Musik.",
    },
    "radio öffnen": {
        "offen": "Das Radio läuft schon.",
        "fenster": "/usr/share/applications/de.haeckerfelix.Shortwave.desktop",
        "befehl": ["/usr/bin/shortwave"],
        "ansage": "Ich öffne das Radio.",
    },
}

# Nach dem Start von Thunderbird arbeitet die Bruecke Vorgemerktes ab. Der
# Nutzer soll das hoeren, wenn etwas wartet - sonst wundert er sich, warum
# ploetzlich ein Entwurf da ist.
WARTESCHLANGE = os.path.join(os.path.expanduser("~"), ".config", "dialos",
                             "mail-entwuerfe.json")


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    try:
        subprocess.run([SAY, text], timeout=60)
    except (OSError, subprocess.SubprocessError) as fehler:
        melde(f"Ansage fehlgeschlagen: {fehler}")


def vorgemerkte_entwuerfe():
    """Wie viele Entwuerfe warten? 0, wenn keine Warteschlange da ist."""
    try:
        import json
        with open(WARTESCHLANGE, encoding="utf-8") as f:
            return len(json.load(f))
    except (OSError, ValueError):
        return 0


def laeuft_schon(programm):
    """Laeuft das Programm bereits? Nur fuer die Ansage, nicht fuer den Start.

    ABSICHTLICH UEBER pgrep UND NICHT UEBER EIN FENSTER: Fenster sind unter
    Wayland von aussen nicht abfragbar - dieselbe Grenze, die das Heben
    verhindert. Der Prozess ist es sehr wohl, und fuer die Auskunft "ist es
    offen?" reicht er.
    """
    name = os.path.basename(programm)
    # ZWEI PRUEFUNGEN, WEIL DER PROZESSNAME NICHT DER PROGRAMMNAME SEIN MUSS:
    # "/usr/bin/thunderbird" ist bei Debian ein Startskript, der laufende
    # Prozess ist "/usr/lib/thunderbird/thunderbird". "-x" trifft den
    # einfachen Fall (rhythmbox, shortwave), das verankerte Muster den mit
    # Wrapper (thunderbird, firefox-esr).
    #
    # DAS "^" IST NICHT KOSMETIK - beim Probieren am 2026-09-21 meldete ein
    # unverankertes "/thunderbird" einen laufenden Thunderbird, obwohl keiner
    # lief: Getroffen hatte es die Befehlszeile der Pruefung selbst. Eine
    # Auskunft, die sich selbst sieht, ist schlimmer als gar keine.
    for befehl in (["/usr/bin/pgrep", "-x", name],
                   ["/usr/bin/pgrep", "-f", f"^/usr/lib/{name}/{name}"]):
        try:
            fertig = subprocess.run(befehl, capture_output=True, timeout=5)
        except (OSError, subprocess.SubprocessError) as fehler:
            melde(f"pgrep fehlgeschlagen: {fehler}")
            return False
        if fertig.returncode == 0:
            melde(f"{name} laeuft schon (gefunden mit {' '.join(befehl[1:])})")
            return True
    return False


def starten(satz):
    """Das Programm zum Satz starten. True, wenn es losgelaufen ist."""
    eintrag = PROGRAMME.get(satz)
    if eintrag is None:
        melde(f"Kein Programm zu {satz!r}")
        return False
    programm = eintrag["befehl"][0]
    if not os.path.exists(programm):
        melde(f"{programm} ist nicht installiert")
        sprich(eintrag.get("fehlt", "Dieses Programm ist auf dem Gerät nicht "
                                     "eingerichtet."))
        return False
    ansage = eintrag["ansage"]
    # NUR BEI DEN SAETZEN OHNE SCHALTER: "neue E-Mail schreiben" oeffnet immer
    # ein neues Fenster, da waere "ist schon offen" schlicht falsch.
    if eintrag.get("fenster") and laeuft_schon(programm):
        ansage = eintrag.get("offen", "Das Programm läuft schon.")
    wartende = vorgemerkte_entwuerfe() if "thunderbird" in programm else 0
    if wartende:
        ansage += (" Ich trage dabei den vorgemerkten Entwurf ein."
                   if wartende == 1
                   else f" Ich trage dabei {wartende} vorgemerkte Entwürfe ein.")
    sprich(ansage)
    # UEBER DIE .desktop-DATEI, WENN ES EINE GIBT - siehe oben: nur so bekommt
    # die Anwendung das Aktivierungs-Token, mit dem sie ihr vorhandenes Fenster
    # nach vorn holen darf.
    zeile = eintrag["befehl"]
    fenster = eintrag.get("fenster")
    if fenster and os.path.exists(fenster) and os.path.exists(GIO):
        zeile = [GIO, "launch", fenster]
    try:
        # start_new_session: Das Programm soll weiterlaufen, wenn die
        # Sprachsteuerung neu startet - es haengt sonst an deren Prozessgruppe.
        subprocess.Popen(zeile, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        melde(f"Start fehlgeschlagen ({programm}): {fehler}")
        sprich("Das Programm ließ sich nicht öffnen.")
        return False
    melde(f"{satz!r} -> {' '.join(zeile)}")
    return True


def saetze():
    """Alle Saetze - fuer die Grammatik und fuer die Doku."""
    return tuple(PROGRAMME)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--liste", "-l"):
        for satz in saetze():
            print(f"{satz}\t{' '.join(PROGRAMME[satz]['befehl'])}")
        return 0
    return 0 if starten(" ".join(sys.argv[1:]).strip().lower()) else 1


if __name__ == "__main__":
    sys.exit(main())
