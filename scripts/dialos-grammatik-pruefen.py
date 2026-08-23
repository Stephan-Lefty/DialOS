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

Aufruf:  scripts/dialos-grammatik-pruefen.py [Satz ...]
         ohne Argumente: alle Saetze der Grammatik
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


def main():
    try:
        import vosk
    except ImportError:
        print("vosk fehlt", file=sys.stderr)
        return 1
    if not os.path.isdir(PIPER_DIR):
        print(f"Piper fehlt: {PIPER_DIR}", file=sys.stderr)
        return 1

    dienst = dienst_laden()
    grammatik = dienst.GRAMMATIK_AN
    alle = [s for s in json.loads(grammatik) if s != "[unk]"]
    gewuenscht = [a for a in sys.argv[1:] if not a.startswith("--")] or alle

    vosk.SetLogLevel(-1)
    modell = vosk.Model(MODELL)

    print(f"{len(alle)} Saetze in der Grammatik, {len(gewuenscht)} werden geprueft.")
    print()
    fehler = 0
    for satz in gewuenscht:
        rohton = sprechen(satz)
        if not rohton:
            print(f"  FEHLT  {satz!r} - Piper lieferte keinen Ton")
            fehler += 1
            continue
        gehoert = hoeren(rohton, grammatik, modell, vosk)
        if gehoert == satz:
            print(f"  ok     {satz!r}")
        else:
            print(f"  FALSCH {satz!r}")
            print(f"         erkannt: {gehoert!r}")
            fehler += 1
    print()
    if fehler:
        print(f"{fehler} von {len(gewuenscht)} Saetzen nicht woertlich erkannt.")
        print("Ein Satz, der hier durchfaellt, ist kaputt - vor dem Einbau aendern.")
        return 1
    print(f"Alle {len(gewuenscht)} Saetze woertlich erkannt.")
    print("Der Test am Geraet mit echter Stimme bleibt trotzdem der Abschluss.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
