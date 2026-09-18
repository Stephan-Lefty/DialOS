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
Gefragt wird deshalb VOSK SELBST, indem seine Meldung abgefangen wird; der Weg
ueber graph/words.txt war die erste Fassung und lief ins Leere, weil das kleine
Modell diese Datei gar nicht hat. Einzelheiten bei wortschatz_pruefen().

Aufruf:  /usr/local/bin/dialos-grammatik-pruefen.py [Satz ...]
         ohne Argumente:        alle Saetze der Grammatik
         --neu "satz"           Kandidat versuchsweise dazu, beide Richtungen
                                (mehrfach angebbar)
"""

import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

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


def wortschatz_pruefen(saetze, modell, vosk):
    """Welche Woerter wirft Vosk aus der Grammatik? DIE ERSTE PFLICHTPRUEFUNG.

    Ein fehlendes Wort wird STILL entfernt: Der Befehl existiert dann nicht,
    und im Protokoll steht nur, dass nichts erkannt wurde. Am 2026-08-18 ist
    das bei "loeschen" aufgefallen; ebenfalls nicht enthalten sind
    "zuruecksetzen", "aufraeumen" und "spaet". Jedes davon haette einen Befehl
    lautlos unwirksam gemacht.

    GEFRAGT WIRD VOSK SELBST, nicht die Modelldatei - und das ist eine
    Korrektur vom 2026-09-17. Die erste Fassung las graph/words.txt, DIE ES IM
    KLEINEN MODELL GAR NICHT GIBT: /usr/local/share/vosk-model-de-small/graph/
    enthaelt nur Gr.fst, HCLr.fst und phones/. Die Pruefung lief dort also nie
    und meldete "Wortschatz UNGEPRUEFT" - was beim ersten Lauf am Geraet auch
    so im Protokoll stand. Eine Pflichtpruefung, die nie anschlaegt, ist von
    einer fehlenden nicht zu unterscheiden.

    Vosk meldet den Fall beim Bauen der Grammatik von selbst ("Ignoring word
    missing in vocabulary"). Die Meldung kommt aus der C++-Ebene und geht in
    SetLogLevel(-1) unter; deshalb wird der Pegel kurz hochgesetzt und stderr
    auf DATEIDESKRIPTOR-Ebene umgeleitet - contextlib.redirect_stderr greift
    dort nicht, es tauscht nur sys.stderr auf Python-Seite.

    Unabhaengig vom Aufbau des Modells, weil es dasselbe Verfahren ist, das
    spaeter auch im Betrieb greift.
    """
    grammatik = json.dumps(list(saetze) + ["[unk]"], ensure_ascii=False)
    with tempfile.TemporaryFile() as auffang:
        gemerkt = os.dup(2)
        try:
            os.dup2(auffang.fileno(), 2)
            vosk.SetLogLevel(0)
            vosk.KaldiRecognizer(modell, ABTASTRATE, grammatik)
        finally:
            vosk.SetLogLevel(-1)
            os.dup2(gemerkt, 2)
            os.close(gemerkt)
        auffang.seek(0)
        meldungen = auffang.read().decode("utf-8", errors="replace")
    return sorted(set(re.findall(
        r"Ignoring word missing in vocabulary:\s*'([^']+)'", meldungen)))


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

    # Kandidat zuerst, dann die uebrigen - wer einen neuen Satz prueft, will
    # sein Ergebnis nicht am Ende von fuenfzig Zeilen suchen.
    #
    # DER FILTER IST NICHT KOSMETIK: "alle" enthaelt den Kandidaten an dieser
    # Stelle bereits (oben angehaengt). Ein schlichtes "neu + alle" haette ihn
    # ein zweites Mal geprueft - gemeldet am 2026-09-17 vom ersten echten Lauf
    # am T490, der 51 statt 50 Saetze zaehlte. Falsch war daran nur die Zahl,
    # nicht das Ergebnis; aber eine Zahl, die man nicht erklaeren kann, ist in
    # diesem Projekt schon mehrfach der Anfang einer falschen Diagnose gewesen.
    uebrige = [s for s in alle if s not in neu]
    gewuenscht = rest or (neu + uebrige if neu else alle)

    vosk.SetLogLevel(-1)
    modell = vosk.Model(MODELL)

    # Erste Pflichtpruefung, vor dem Sprechen - sie braucht nur das Modell.
    #
    # GETRENNT NACH KANDIDAT UND BESTAND, und das ist kein Feinschliff: Fehlt
    # ein Wort im KANDIDATEN, ist er unbrauchbar und die Pruefung endet hier.
    # Fehlt eines im BESTAND, ist das eine Altlast - sie gehoert gemeldet, darf
    # aber den Kandidaten nicht blockieren, sonst haengt ein neuer Befehl an
    # einem alten Problem, mit dem er nichts zu tun hat.
    #
    # Zweimal gefragt statt einmal, weil Vosk nur sagt WELCHES Wort fehlt, nicht
    # aus welchem Satz es stammt.
    fehlend_b = wortschatz_pruefen([s for s in alle if s not in neu],
                                   modell, vosk)
    fehlend_k = [w for w in wortschatz_pruefen(neu, modell, vosk)
                 if w not in fehlend_b] if neu else []

    if fehlend_b:
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
