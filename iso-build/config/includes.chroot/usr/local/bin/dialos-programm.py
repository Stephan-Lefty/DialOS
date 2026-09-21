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

NOCHMAL STARTEN HOLT DAS FENSTER NACH VORN. Thunderbird, Firefox und Rhythmbox
erkennen eine laufende Sitzung und heben deren Fenster, statt ein zweites zu
oeffnen. Deshalb braucht es hier keine Fensterverwaltung (wmctrl ist nicht
installiert, und die GNOME-Schnittstelle dafuer ist gesperrt).

Aufruf:
  dialos-programm.py "postfach öffnen"      # startet und sagt es an
  dialos-programm.py --liste                # alle Saetze, fuer die Doku
"""

import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-programm.log")

# Satz -> was passiert. "befehl" ist die Programmzeile, "ansage" das, was der
# Nutzer hoert, "fehlt" der Satz fuer den Fall, dass das Programm nicht
# installiert ist (bei einem Kundengeraet ohne Radio zum Beispiel).
#
# DIE ZWECKE STAMMEN AUS docs/anwendungen.md - dort steht, WARUM es dieses
# Programm ist und kein anderes. Hier steht nur, wie man es ruft.
PROGRAMME = {
    "postfach öffnen": {
        "befehl": ["/usr/bin/thunderbird"],
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
        "befehl": ["/usr/bin/firefox-esr"],
        "ansage": "Ich öffne das Internet.",
    },
    "browser öffnen": {
        "befehl": ["/usr/bin/firefox-esr"],
        "ansage": "Ich öffne den Browser.",
    },
    "musik öffnen": {
        "befehl": ["/usr/bin/rhythmbox"],
        "ansage": "Ich öffne die Musik.",
    },
    "radio öffnen": {
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
    wartende = vorgemerkte_entwuerfe() if "thunderbird" in programm else 0
    if wartende:
        ansage += (" Ich trage dabei den vorgemerkten Entwurf ein."
                   if wartende == 1
                   else f" Ich trage dabei {wartende} vorgemerkte Entwürfe ein.")
    sprich(ansage)
    try:
        # start_new_session: Das Programm soll weiterlaufen, wenn die
        # Sprachsteuerung neu startet - es haengt sonst an deren Prozessgruppe.
        subprocess.Popen(eintrag["befehl"], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        melde(f"Start fehlgeschlagen ({programm}): {fehler}")
        sprich("Das Programm ließ sich nicht öffnen.")
        return False
    melde(f"{satz!r} -> {' '.join(eintrag['befehl'])}")
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
