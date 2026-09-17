#!/usr/bin/env python3
"""Prueft jeden Satz der Befehlsgrammatik: Piper spricht, Vosk hoert zu.

Das ist die zweite der beiden Pflichtpruefungen aus docs/sprachbefehle.md. Die
erste (steht das Wort ueberhaupt im Wortschatz?) meldet Vosk beim Bauen der
Grammatik von selbst. Diese hier beantwortet die andere Haelfte: Wird der ganze
Satz in der VOLLSTAENDIGEN Grammatik richtig erkannt - oder mit einem
bestehenden verwechselt?

WARUM ALS WERKZEUG UND NICHT VON HAND: Die Pruefung ist bei jedem neuen Befehl
Pflicht, und sie war es schon, als "gnome" frei erkannt zuverlaessig zu "genug"
wurde. Eine Pflichtpruefung, die davon abhaengt, dass sich jemand an den
Piper-Aufruf erinnert, findet irgendwann nicht mehr statt - dieselbe Ueberlegung
wie bei scripts/dialos-installstand.sh.

WAS SIE NICHT ERSETZT: einen Test mit echter Stimme. Piper spricht deutlicher
als ein Mensch, gleichmaessiger, und immer aus derselben Entfernung. Ein Satz,
der hier durchfaellt, ist sicher kaputt; einer, der besteht, ist noch nicht
bewiesen. Deshalb bleibt der Test am Geraet der Abschluss - dieses Werkzeug
sortiert nur vorher aus, ohne dass jemand sprechen muss.

Die Saetze kommen aus dialos-sprachbefehl-desktop.py selbst, nicht aus einer
Liste hier: Eine zweite Liste liefe beim naechsten neuen Befehl auseinander,
und zwar unbemerkt, weil sie fuer sich genommen richtig aussieht.

EINEN NEUEN SATZ PRUEFEN, BEVOR ER EINGEBAUT IST: "--neu SATZ". Das war bis
zum 2026-09-17 nicht moeglich, und die Luecke war nicht harmlos. Wer einen
Kandidaten einfach als Argument uebergab, liess ihn gegen eine Grammatik
hoeren, die ihn NICHT enthaelt - Vosk presst ihn dann auf den naechstliegenden
bestehenden Satz. Das Ergebnis sah nach einer Verwechslung aus, war aber nur
ein Werkzeugfehler; umgekehrt konnte ein kaputter Kandidat unauffaellig
bleiben. Mit "--neu" kommt der Satz versuchsweise in die Grammatik, und
geprueft wird in BEIDE Richtungen:

  * Wird der Kandidat selbst woertlich erkannt?
  * Gehen BESTEHENDE Saetze durch ihn kaputt?

Die zweite Frage ist die wichtigere. Ein Kandidat, der selbst durchfaellt,
kostet nur ihn; einer, der einen bestehenden Befehl verwechselbar macht, nimmt
etwas kaputt, das heute funktioniert - und das faellt erst auf, wenn der
Nutzer allein mit dem Geraet ist.

AUSSERDEM SEIT DEM 2026-09-17: die erste Pflichtpruefung laeuft mit, statt nur
in der Doku zu stehen. Fehlt ein Wort im Wortschatz des Modells, wirft Vosk es
STILL aus der Grammatik - die Meldung dazu geht in SetLogLevel(-1) unter.
Geprueft wird jetzt vorher gegen graph/words.txt, ohne Sprechen.

Aufruf:  scripts/dialos-grammatik-pruefen.py [Satz ...]
         ohne Argumente:        alle Saetze der Grammatik
         --neu "satz"           Kandidat versuchsweise dazu, beide Richtungen
                                (mehrfach angebbar)
"""

import importlib.util
import json
import os
import shlex
import subprocess
import sys

BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "iso-build/config/includes.chroot/usr/local/bin")
DIENST = os.path.join(BIN, "dialos-sprachbefehl-desktop.py")
PIPER_DIR = "/usr/local/share/dialos-piper"
STIMME = "voices/de_DE-thorsten-high.onnx"
MODELL = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000


def dienst_laden():
    spec = importlib.util.spec_from_file_location("dienst", DIENST)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def sprechen(text):
    """Piper spricht den Satz und liefert rohe 16-kHz-Mono-Abtastwerte.

    "--noise_w 0" ist Pflicht, sonst klingt derselbe Satz bei jedem Aufruf
    anders (gemessen 2026-08-18: bis zu 17 % andere Dauer) und ein Fehlschlag
    liesse sich nicht wiederholen.
    """
    befehl = (
        f"cd {shlex.quote(PIPER_DIR)} && "
        f"printf %s {shlex.quote(text)} | "
        f"./piper/piper --model {shlex.quote(STIMME)} --noise_w 0 "
        f"--output_raw 2>/dev/null | "
        f"sox -r 22050 -c 1 -b 16 -e signed-integer -t raw - "
        f"-t raw -r {ABTASTRATE} -c 1 -b 16 -e signed-integer - 2>/dev/null"
    )
    r = subprocess.run(["sh", "-c", befehl], capture_output=True, timeout=120)
    return r.stdout


def hoeren(rohton, grammatik, modell, vosk):
    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, grammatik)
    for i in range(0, len(rohton), 4000):
        erkenner.AcceptWaveform(rohton[i:i + 4000])
    return json.loads(erkenner.FinalResult()).get("text", "").strip()


def wortschatz_pruefen(woerter, modell_pfad):
    """Stehen alle Woerter im Wortschatz des Modells? DIE ERSTE PFLICHTPRUEFUNG.

    Vosk meldet fehlende Woerter beim Bauen der Grammatik selbst
    ("Ignoring word missing in vocabulary") - aber diese Meldung geht in
    SetLogLevel(-1) unter, und genau deshalb stand sie bisher nicht hier. Ein
    fehlendes Wort wird STILL aus der Grammatik geworfen: Der Befehl existiert
    dann nicht, und im Protokoll steht nur, dass nichts erkannt wurde.

    Am 2026-08-18 ist das bei "loeschen" aufgefallen, das im Wortschatz fehlt;
    ebenfalls nicht enthalten sind "zuruecksetzen", "aufraeumen" und "spaet".
    Jedes davon haette einen Befehl lautlos unwirksam gemacht.

    Gelesen wird graph/words.txt des Modells - das geht sofort, ohne Sprechen
    und ohne das Modell zu laden.
    """
    pfad = os.path.join(modell_pfad, "graph", "words.txt")
    if not os.path.exists(pfad):
        return None                      # Modell anders aufgebaut - nicht raten
    with open(pfad, encoding="utf-8", errors="replace") as f:
        bekannt = {z.split(" ", 1)[0].lower() for z in f if z.strip()}
    return sorted({w for w in woerter if w.lower() not in bekannt})


def main():
    try:
        import vosk
    except ImportError:
        print("vosk fehlt", file=sys.stderr)
        return 1
    if not os.path.isdir(PIPER_DIR):
        print(f"Piper fehlt: {PIPER_DIR}", file=sys.stderr)
        return 1

    neu = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--neu"
           and i + 1 < len(sys.argv)]
    rest = []
    ueberspringen = False
    for a in sys.argv[1:]:
        if ueberspringen:
            ueberspringen = False
            continue
        if a == "--neu":
            ueberspringen = True
        elif not a.startswith("--"):
            rest.append(a)

    dienst = dienst_laden()
    alle = [s for s in json.loads(dienst.GRAMMATIK_AN) if s != "[unk]"]

    # EIN NEUER SATZ MUSS IN DIE GRAMMATIK, BEVOR ER PRUEFBAR IST. Ohne das
    # hoert Vosk ihn gegen eine Grammatik, die ihn nicht kennt, presst ihn auf
    # den naechstliegenden bestehenden Satz - und das Ergebnis saehe aus wie
    # eine Verwechslung, waere aber nur ein Werkzeugfehler. Genau daran ist die
    # Pruefung eines Kandidaten bisher gescheitert.
    if neu:
        schon = [s for s in neu if s in alle]
        if schon:
            print(f"Stehen bereits in der Grammatik: {schon} - ohne --neu pruefen.")
            return 2
        alle = alle + neu

    grammatik = json.dumps(alle + ["[unk]"], ensure_ascii=False)
    gewuenscht = rest or (neu + alle if neu else alle)

    # Erste Pflichtpruefung, vor allem anderen - sie braucht kein Sprechen.
    #
    # GETRENNT NACH KANDIDAT UND BESTAND, und das ist kein Feinschliff: Fehlt
    # ein Wort im KANDIDATEN, ist er unbrauchbar und die Pruefung endet hier.
    # Fehlt eines im BESTAND, ist das eine Altlast - sie gehoert gemeldet, darf
    # aber den Kandidaten nicht blockieren, sonst haengt ein neuer Befehl an
    # einem alten Problem, mit dem er nichts zu tun hat.
    kandidat_woerter = {w for s in neu for w in s.split()}
    bestand_woerter = {w for s in alle if s not in neu for w in s.split()}

    fehlend_k = wortschatz_pruefen(kandidat_woerter, MODELL) if neu else []
    fehlend_b = wortschatz_pruefen(bestand_woerter, MODELL)

    if fehlend_b is None:
        print(f"Hinweis: {MODELL}/graph/words.txt nicht lesbar - "
              "Wortschatz UNGEPRUEFT.")
    elif fehlend_b:
        print("ALTLAST - diese Woerter BESTEHENDER Saetze fehlen im Wortschatz:")
        print("  " + ", ".join(repr(w) for w in fehlend_b))
        print("Vosk wirft sie still aus der Grammatik; die betroffenen Befehle")
        print("sind nicht ausloesbar. Eigener Punkt, nicht Sache des Kandidaten.")
        print()

    if fehlend_k:
        print("KANDIDAT NICHT IM WORTSCHATZ DES MODELLS:",
              ", ".join(repr(w) for w in fehlend_k))
        print("Vosk wirft diese Woerter STILL aus der Grammatik - der Befehl")
        print("waere nie ausloesbar, ohne dass irgendwo etwas stuende.")
        print("Andere Formulierung waehlen, dann erneut pruefen.")
        return 1

    vosk.SetLogLevel(-1)
    modell = vosk.Model(MODELL)

    if neu:
        print(f"{len(alle) - len(neu)} Saetze in der Grammatik, "
              f"{len(neu)} Kandidat(en) versuchsweise dazu.")
        print("Geprueft wird in BEIDE Richtungen: ob der Kandidat erkannt wird,")
        print("UND ob die bestehenden Saetze durch ihn kaputtgehen.")
    else:
        print(f"{len(alle)} Saetze in der Grammatik, "
              f"{len(gewuenscht)} werden geprueft.")
    print()

    fehler = 0
    kandidat_fehler = 0
    for satz in gewuenscht:
        rohton = sprechen(satz)
        if not rohton:
            print(f"  FEHLT  {satz!r} - Piper lieferte keinen Ton")
            fehler += 1
            continue
        gehoert = hoeren(rohton, grammatik, modell, vosk)
        marke = "*" if satz in neu else " "
        if gehoert == satz:
            print(f" {marke}ok     {satz!r}")
        else:
            print(f" {marke}FALSCH {satz!r}")
            print(f"         erkannt: {gehoert!r}")
            fehler += 1
            if satz in neu:
                kandidat_fehler += 1
    print()
    if neu:
        print("(* = Kandidat)")
    if fehler:
        print(f"{fehler} von {len(gewuenscht)} Saetzen nicht woertlich erkannt.")
        if neu and kandidat_fehler < fehler:
            print("DARUNTER BESTEHENDE SAETZE: Der Kandidat macht sie")
            print("verwechselbar. Das ist der schlimmere Fall - er nimmt etwas")
            print("kaputt, das heute funktioniert.")
        print("Ein Satz, der hier durchfaellt, ist kaputt - vor dem Einbau aendern.")
        return 1
    print(f"Alle {len(gewuenscht)} Saetze woertlich erkannt.")
    if neu:
        print("Der Kandidat ist damit einbaubar - die bestehenden Saetze")
        print("haben ihn ueberstanden.")
    print("Der Test am Geraet mit echter Stimme bleibt trotzdem der Abschluss.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
