#!/usr/bin/env python3
"""DialOS: Auskunft geben - Uhrzeit, Datum, Wetter.

Stephans Wunsch vom 2026-08-19. Drei Fragen, die ein Nutzer taeglich hat und
die er ohne Bildschirm nicht selbst nachsehen kann.

WARUM DIE BAUSTEINE AUS dialos-start-ansage.py KOMMEN und nicht neu gebaut
sind: Dort steht schon, wie DialOS ein Datum und eine Uhrzeit ausspricht -
Wochentag, Ordinalzahl, Zahl als Wort - und dort steht die Wetterabfrage
ueber GeoClue2 und wttr.in. Zwei Stellen mit derselben Aufgabe wuerden
auseinanderlaufen: Wer die Formulierung in der Start-Ansage aendert, haette
sonst eine zweite, die anders klingt. Der Nutzer wuerde es sofort hoeren.

Das Importieren ist gefahrlos - dialos-start-ansage.py handelt
ausschliesslich unter "if __name__ == '__main__'".

EIN WORT, DAS NICHT GEHT: "spaet". Stephan wollte "Wie spaet ist es?", und
das Wort steht NICHT im Wortschatz des Vosk-Modells (geprueft 2026-08-19,
dieselbe Falle wie "loeschen" einen Tag vorher). Vosk haette es still aus
der Grammatik geworfen. Deshalb "Wie viel Uhr ist es?" und "Wie ist die
Uhrzeit?" - beide geprueft, beide woertlich erkannt.

Aufruf:
    dialos-auskunft.py uhrzeit
    dialos-auskunft.py datum
    dialos-auskunft.py --debug ...
"""

import importlib.util
import os
import subprocess
import sys
import time
from datetime import datetime

SAY = "/usr/local/bin/dialos-say.py"
ANSAGE_SKRIPT = "/usr/local/bin/dialos-start-ansage.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-auskunft.log")

DEBUG = "--debug" in sys.argv


# WARUM IN EINEM VERSTECKTEN ORDNER (Stephan, 2026-08-22): Vorher lagen die
# Protokolle offen im Heimatverzeichnis - zehn laufende und fuenfzehn gedrehte
# Fassungen, also 25 Dateien zwischen "Notizen", "Dokumente" und "Bilder". Der
# Nutzer sieht sie nicht, aber ein sehender Helfer sucht dazwischen. In "~/.log"
# stoeren sie niemanden und sind trotzdem da, wo man sie vermutet.
#
# Der Ordner wird beim Schreiben angelegt, nicht vorausgesetzt: Ein neues Konto
# hat ihn noch nicht, und ein fehlendes Protokoll darf keine Ansage aufhalten.
def melde(text):
    if DEBUG:
        print(text, flush=True)
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    if not os.access(SAY, os.X_OK):
        print(text)
        return
    subprocess.run([SAY, text], capture_output=True, timeout=180)


def bausteine():
    """Laedt die Sprech-Bausteine aus der Start-Ansage.

    Faellt das aus, gibt es keine Ersatzformulierung - eine zweite,
    abweichende Aussprache waere schlechter als eine ehrliche Fehlmeldung.
    """
    try:
        spec = importlib.util.spec_from_file_location("dialos_ansage", ANSAGE_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    except Exception as fehler:
        melde(f"  Bausteine nicht ladbar: {fehler}")
        return None


# ------------------------------------------------------------- Uhrzeit

def uhrzeit(a):
    jetzt = datetime.now()
    stunde = a.zahl_wort_0_99(jetzt.hour)
    # Volle Stunde ohne Minutenangabe. "acht Uhr null" waere richtig
    # gerechnet und falsch gesprochen.
    if jetzt.minute == 0:
        satz = f"Es ist {stunde} Uhr."
    else:
        satz = f"Es ist {stunde} Uhr {a.zahl_wort_0_99(jetzt.minute)}."
    melde(f"  uhrzeit: {satz}")
    sprich(satz)
    return 0


# --------------------------------------------------------------- Datum

def datum(a):
    jetzt = datetime.now()
    # Genau die Formulierung der Start-Ansage, damit beide gleich klingen.
    text = (f"Heute ist {a.WOCHENTAGE[jetzt.weekday()]}, "
            f"der {a.ORDINAL_TAGE[jetzt.day]} {a.MONATE[jetzt.month - 1]}.")
    melde(f"  datum: {text}")
    sprich(text)
    return 0


# WETTER AUF NACHFRAGE GIBT ES BEWUSST NICHT (Stephan, 2026-08-19:
# "Wetter nur beim Start lassen").
#
# Der Befehl war gebaut und getestet und wurde wieder entfernt, weil er am
# Einsatzort nicht funktionieren kann - nicht heute und nicht naechste
# Woche. Gemessen am 2026-08-19:
#
#   - GeoClue sieht neun WLAN-Netze, beaconDB ist erreichbar (HTTP 200 in
#     0,4 s), kennt aber KEINES davon und faellt auf IP-Ortung zurueck
#     ("fallback":"ipf").
#   - Heraus kommt Wien mit 26 km Ungenauigkeit - rund 300 km vom
#     tatsaechlichen Standort entfernt.
#   - Der Schwellwert von 10 km verwirft das korrekt, und damit gaebe es
#     auf die Frage fast immer nur "Ich kann das Wetter gerade nicht
#     abrufen".
#
# Ein Befehl, der nie funktioniert, ist fuer einen blinden Nutzer schlechter
# als keiner: Er kann nicht nachsehen, ob es an ihm oder am System liegt.
#
# In der Start-Ansage bleibt das Wetter, weil es dort ohne Nachfrage
# einfach ausfaellt und niemand darauf wartet.
#
# Was es braeuchte, um es zurueckzuholen: einen hinterlegten Rueckfall-Ort
# fuer den Fall, dass die Messung zu ungenau ist - siehe TODO.md. Die
# Funktion wetter_text() in dialos-start-ansage.py bleibt unveraendert
# nutzbar.


def main():
    argumente = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not argumente:
        print("Aufruf: dialos-auskunft.py uhrzeit|datum", file=sys.stderr)
        return 2
    was = argumente[0]
    melde(f"=== {was} ===")
    a = bausteine()
    if a is None:
        sprich("Ich kann die Auskunft gerade nicht geben.")
        return 1
    if was == "uhrzeit":
        return uhrzeit(a)
    if was == "datum":
        return datum(a)
    print(f"Unbekannt: {was}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
