#!/usr/bin/env python3
"""Prueft die Schlussregel des Diktats OFFLINE - Piper spricht, niemand muss reden.

WARUM ES DIESES WERKZEUG GIBT: Am 2026-08-21 wurde die Schlusserkennung an
einem Nachmittag VIERMAL geflickt, und jedes Mal hat erst Stephans naechster
Test die naechste Luecke gefunden - eine der "Reparaturen" unterbrach ihn sogar
mitten im Diktieren. Als Regel festgehalten in CLAUDE.md: Was sich offline
gegen Piper pruefen laesst, wird VORHER offline geprueft.

ZWEI FAELLE, beide ohne Mikrofon:

  A  Durchgehende Rede, wie beim Diktieren eines Briefes.
     ERWARTUNG: kein Schluss. Der Erkenner liefert dabei im Sekundentakt
     Bruchstuecke ('beenden', 'diktat'), aber keines folgt auf eine Pause.

  B  Derselbe Text, dann eine Sprechpause, dann "Diktat beenden".
     ERWARTUNG: genau ein Schluss, und zwar am Ende.

Geprueft wird der ECHTE Code: ist_schluss(), pause_davor() und die
Pegelschwelle kommen aus dialos-diktat.py, nicht aus einer Nachbildung.

Aufruf:  scripts/dialos-schlussregel-pruefen.py
"""

import importlib.util
import json
import os
import shlex
import subprocess
import sys
import tempfile
import wave

import vosk

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO, "iso-build/config/includes.chroot/usr/local/bin")
PIPER_DIR = "/usr/local/share/dialos-piper"
MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"

TEXT = ("Sehr geehrte Damen und Herren, wir arbeiten stetig daran, uns noch "
        "weiter zu verbessern und bitten Sie deshalb um Ihre Mithilfe bei der "
        "Beantwortung der folgenden Fragen. Die Angaben werden vertraulich "
        "behandelt und ausschliesslich fuer statistische Zwecke verwendet. "
        "Bitte senden Sie uns den ausgefuellten Bogen bis zum Ende des Monats "
        "zurueck.")
SCHLUSS = "Diktat beenden"


def modul(pfad, name):
    spec = importlib.util.spec_from_file_location(name, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sprechen(text, ziel, rate, modell):
    befehl = (f"cd {shlex.quote(PIPER_DIR)} && printf %s {shlex.quote(text)} | "
              f"./piper/piper --model {shlex.quote(modell)} --noise_w 0 "
              f"--output_raw 2>/dev/null | "
              f"sox -r {rate} -c 1 -b 16 -e signed-integer -t raw - "
              f"-r 16000 {shlex.quote(ziel)} norm 2>/dev/null")
    subprocess.run(["sh", "-c", befehl], check=False)
    return os.path.exists(ziel) and os.path.getsize(ziel) > 0


def durchlauf(wav, diktat, name, erwartet_schluss):
    """Spielt die Datei blockweise durch die echte Schlusslogik."""
    erkenner = vosk.KaldiRecognizer(vosk.Model(MODELL_KLEIN), 16000,
                                    diktat.GRAMMATIK_SCHLUSS)
    import collections
    verlauf = collections.deque(
        maxlen=int(diktat.RUHE_FENSTER_S / diktat.BLOCK_S) + 8)
    puffer = []
    zeit = 0.0
    schluesse, verworfen = [], []
    with wave.open(wav) as w:
        while True:
            block = w.readframes(2000)          # 4000 Bytes wie im Diktat
            if not block:
                break
            zeit += len(block) / 2 / 16000.0
            p = diktat.pegel(block)
            puffer.append(p)
            verlauf.append(p)
            if erkenner.AcceptWaveform(block):
                gehoert = json.loads(erkenner.Result()).get("text", "").strip()
                if not gehoert:
                    continue
                mittel = sum(puffer) / len(puffer)
                puffer = []
                if not diktat.ist_schluss(gehoert):
                    continue
                if mittel < diktat.PEGEL_SCHWELLE:
                    verworfen.append((zeit, gehoert, "zu leise"))
                    continue
                if not diktat.pause_davor(verlauf):
                    verworfen.append((zeit, gehoert, "keine Sprechpause davor"))
                    continue
                schluesse.append((zeit, gehoert))
    print(f"\n  {name}")
    for z, g, grund in verworfen:
        print(f"    {z:5.1f} s  {g!r} verworfen - {grund}")
    for z, g in schluesse:
        print(f"    {z:5.1f} s  SCHLUSS {g!r}")
    if not verworfen and not schluesse:
        print("    (nichts, was nach Schluss aussah)")
    passt = (len(schluesse) == 1) if erwartet_schluss else (len(schluesse) == 0)
    print(f"    -> {'BESTANDEN' if passt else 'DURCHGEFALLEN'} "
          f"({len(schluesse)} Schluss/Schluesse, erwartet "
          f"{'genau einen' if erwartet_schluss else 'keinen'})")
    return passt


def main():
    vosk.SetLogLevel(-1)
    diktat = modul(os.path.join(BIN, "dialos-diktat.py"), "d")
    beispiele = modul(os.path.join(REPO, "scripts/dialos-sprachbeispiele.py"), "b")
    stimmen = modul(os.path.join(BIN, "dialos-stimme.py"), "st")
    a = stimmen.STIMMEN["kerstin"]
    modell = "voices/" + a["kennung"] + ".onnx"
    rate = beispiele.abtastrate(modell)

    ordner = tempfile.mkdtemp(prefix="schlussregel-")
    rede = os.path.join(ordner, "rede.wav")
    schluss = os.path.join(ordner, "schluss.wav")
    stille = os.path.join(ordner, "stille.wav")
    fall_b = os.path.join(ordner, "fall_b.wav")
    if not sprechen(TEXT, rede, rate, modell) or not sprechen(SCHLUSS, schluss, rate, modell):
        print("Piper hat nichts geliefert", file=sys.stderr)
        return 1
    subprocess.run(["sox", "-n", "-r", "16000", "-c", "1", "-b", "16",
                    stille, "trim", "0.0", "1.0"], check=False)
    # STILLE AUCH HINTER DEN SCHLUSSSATZ. Ohne sie steht die Phrase am
    # Dateiende, und der Erkenner liefert sie nie ab - er schliesst eine
    # Aeusserung erst an der Sprechpause danach. Beim ersten Lauf am
    # 2026-08-22 fiel Fall B genau daran durch, nicht an der Regel. Im Betrieb
    # ist diese Pause selbstverstaendlich: Wer "Diktat beenden" sagt, sagt
    # danach nichts mehr.
    subprocess.run(["sox", rede, stille, schluss, stille, fall_b], check=False)

    print("Schlussregel, offline gegen Piper geprueft")
    a_ok = durchlauf(rede, diktat, "A  durchgehende Rede, kein Schlusssatz", False)
    b_ok = durchlauf(fall_b, diktat, "B  Rede, 1 s Pause, dann 'Diktat beenden'", True)
    print(f"\n  Ergebnis: {'beide Faelle bestanden' if a_ok and b_ok else 'NICHT bestanden'}")
    return 0 if (a_ok and b_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
