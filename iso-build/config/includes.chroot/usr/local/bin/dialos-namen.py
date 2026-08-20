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
    """Erste nicht-leere, nicht-kommentierte Zeile - geprueft.

    Kommentarzeilen sind erlaubt, damit die Datei sich selbst erklaeren kann.
    """
    try:
        with open(pfad, encoding="utf-8") as f:
            for zeile in f:
                zeile = zeile.strip()
                if zeile and not zeile.startswith("#"):
                    return zeile
    except OSError:
        pass
    return None


def _geprueft(wert):
    return wert if wert and ERLAUBT.match(wert) else None


def _nutzer_felder():
    """(geschrieben, gesprochen) aus nutzer-name.txt.

    ZWEI FELDER, getrennt durch "|" - und der Grund ist Stephans Beobachtung
    vom 2026-08-20: Michael sprach "Stephan" als "Stefffan". Der Name des
    Nutzers wird bei JEDER Begruessung, jeder Rueckfrage und jedem Fehler
    gesagt; falsch ausgesprochen ist er stoerender als jedes andere Wort.

    WARUM NICHT IN DIE AUSSPRACHE-TABELLE von dialos-say.py: Dort stehen
    Regeln, die fuer alle Geraete gelten ("Tastatur", "ID", "DialOS"). Ein
    Kundenname gilt fuer EIN Geraet. Eine Regel pro Kunde in einer globalen
    Tabelle waere in einem Jahr eine Liste von Namen fremder Leute im Repo -
    und sie wuerde beim naechsten Kunden wieder nicht passen. Die Aussprache
    gehoert dorthin, wo der Name steht.

    Beide Felder getrennt, weil sie verschiedene Zwecke haben: Gesprochen wird
    das zweite, geschrieben das erste - fuer Briefe und Ausdrucke, wo "Stefan"
    statt "Stephan" schlicht falsch waere. Fehlt das zweite, gilt das erste
    fuer beides.
    """
    roh = _lesen(NUTZER_DATEI)
    if not roh:
        return None, None
    teile = [t.strip() for t in roh.split("|", 1)]
    geschrieben = _geprueft(teile[0])
    gesprochen = _geprueft(teile[1]) if len(teile) > 1 else None
    return geschrieben, (gesprochen or geschrieben)


def assistent_name():
    """Wie der Assistent heisst. Ohne Datei: "Michael"."""
    return _geprueft(_lesen(ASSISTENT_DATEI)) or "Michael"


def nutzer_name():
    """Wie der Nutzer heisst - zum SPRECHEN. Oder None."""
    return _nutzer_felder()[1]


def nutzer_name_geschrieben():
    """Wie der Nutzer heisst - zum SCHREIBEN (Briefe, Ausdrucke). Oder None."""
    return _nutzer_felder()[0]


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
    print(f"Assistent:  {assistent_name()}")
    print(f"Nutzer, geschrieben: {nutzer_name_geschrieben() or '(keiner eingetragen)'}")
    print(f"Nutzer, gesprochen:  {nutzer_name() or '(keiner eingetragen)'}")
    print()
    for probe in ("Soll ich ihn löschen? Sage ja oder nein.",
                  "Ich finde kein Mikrofon.",
                  "Dein Betreuer kann jetzt zusehen.",
                  "Du hast mir eine Weile nichts gesagt."):
        print(f"  {probe!r}")
        print(f"    -> {anrede(probe)!r}")
