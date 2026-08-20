#!/usr/bin/env python3
"""DialOS: die beiden Namen - wie der Assistent heisst und wie der Nutzer.

EIN ORT FUER BEIDE, weil sie zusammengehoeren und weil sonst jedes Skript seine
eigene Fassung baekommt. Genau das ist im Projekt schon zweimal
auseinandergelaufen: das Sprechtempo stand doppelt (fest eingetragen und in
piper-generic.conf), und der Begruessungssatz steht bis heute in zwei Dateien.

WANN DER NUTZERNAME BENUTZT WIRD - und wann nicht (Stephans Vorgabe vom
2026-08-20: "eher da wo es Sinn macht als Ersatz zu Du/Dir"):

  JA   Begruessung beim Anmelden - einmal pro Sitzung, und der Moment, in dem
       es am meisten bedeutet.
  JA   Entscheidungen: Fernwartung freigeben, Einkaufszettel loeschen. Dort,
       wo eine Zustimmung faellt, holt der Name die Aufmerksamkeit zurueck.
  JA   Fehler und Ausfaelle. Wenn etwas nicht geht, muss klar sein, wer
       gemeint ist.
  NEIN Bestaetigungen wie "Diktat beendet" oder "Linux Desktop" - zwanzigmal
       am Tag nutzt sich ein Name ab.
  NEIN Die Zeitgrenze alle zwei Minuten. Dito.

WARUM DAS BEI DIESER ZIELGRUPPE MEHR IST ALS HOEFLICHKEIT: Der Name am
Satzanfang ist ein SIGNAL. Laeuft das Radio oder ist Besuch im Raum, sagt
"Stephan, ..." unmissverstaendlich: das gilt Dir, hoer hin. Genau deshalb darf
er nicht in jeder Ansage stehen - wer ihn dauernd hoert, ueberhoert ihn, und
dann ist das Signal weg.

WOHER DIE NAMEN KOMMEN:
  assistent-name.txt  schreibt dialos-stimme.py, zusammen mit Stimme und Tempo
  nutzer-name.txt     traegt der Betreuer beim Aufsetzen ein. Der
                      Einrichtungs-Assistent, der ihn per Sprache erfragen soll
                      (docs/ersteinrichtung.md), existiert noch nicht.

Fehlt eine Datei, faellt DialOS auf etwas Brauchbares zurueck statt zu
stolpern: "Michael" fuer den Assistenten (der Auslieferungsname), und beim
Nutzer gar nichts - dann bleibt es beim schlichten "Du", das immer stimmt.
"""

import os
import re

ORDNER = "/usr/local/share/dialos"
ASSISTENT_DATEI = os.path.join(ORDNER, "assistent-name.txt")
NUTZER_DATEI = os.path.join(ORDNER, "nutzer-name.txt")

# Was als Name durchgeht. Absichtlich eng: Der Wert landet in einem
# gesprochenen Satz, und eine Datei mit Unsinn darin soll die Ansage nicht
# verunstalten. Buchstaben, Bindestrich, Leerzeichen - mehr braucht ein
# Rufname nicht.
ERLAUBT = re.compile(r"^[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß \-]{0,30}$")


def _lesen(pfad):
    try:
        with open(pfad, encoding="utf-8") as f:
            wert = f.read().strip()
    except OSError:
        return None
    return wert if wert and ERLAUBT.match(wert) else None


def assistent_name():
    """Wie der Assistent heisst. Ohne Datei: "Michael"."""
    return _lesen(ASSISTENT_DATEI) or "Michael"


def nutzer_name():
    """Wie der Nutzer heisst - oder None, wenn niemand ihn eingetragen hat."""
    return _lesen(NUTZER_DATEI)


def anrede(satz):
    """Stellt den Namen voran, wenn einer bekannt ist.

    "Soll ich ihn löschen?"  ->  "Stephan, soll ich ihn löschen?"

    Der erste Buchstabe wird klein, damit kein Satz mitten im Satz anfaengt.
    AUSGENOMMEN sind nur die Hoeflichkeitsformen Du/Dein, die DialOS
    durchgehend gross schreibt - "Stephan, Dein Betreuer kann zusehen" ist
    richtig, "Stephan, Ich finde kein Mikrofon" waere es nicht. Genau diesen
    Fehler hatte die erste Fassung am 2026-08-20: "Ich" stand in der
    Ausnahmeliste, obwohl es mitten im Satz klein gehoert.

    NICHT FUER DIE BEGRUESSUNG. "Stephan, hallo, ich bin Anna" klingt schief;
    dort gehoert der Name in den Gruss selbst ("Hallo Stephan, ich bin Anna").
    Die Begruessung baut ihn deshalb selbst ein.

    Ohne Nutzernamen kommt der Satz unveraendert zurueck. Er muss also fuer
    sich allein stimmen - eine Ansage darf nie DAVON abhaengen, dass ein Name
    eingetragen ist.
    """
    name = nutzer_name()
    if not name or not satz:
        return satz
    erstes = satz.split(" ", 1)[0].rstrip(",.:;?!")
    if erstes not in ("Du", "Dein", "Deine", "Deinen", "Deiner", "Deinem",
                      "Dir", "Dich"):
        satz = satz[0].lower() + satz[1:]
    return f"{name}, {satz}"


if __name__ == "__main__":
    print(f"Assistent: {assistent_name()}")
    print(f"Nutzer:    {nutzer_name() or '(keiner eingetragen)'}")
    print()
    for probe in ("Soll ich ihn löschen? Sage ja oder nein.",
                  "Ich finde kein Mikrofon.",
                  "Dein Betreuer kann jetzt zusehen.",
                  "Du hast mir eine Weile nichts gesagt."):
        print(f"  {probe!r}")
        print(f"    -> {anrede(probe)!r}")
