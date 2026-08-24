#!/usr/bin/env python3
"""Messt, ob die Sprachsteuerung aus GERAEUSCH einschaltet.

ANLASS (2026-08-24): Um 14:41:12 hat sich die Sprachsteuerung selbst
eingeschaltet - Vosk erkannte "sprachsteuerung starten". Stephan hatte kein
Wort gesagt, DialOS selbst hat nicht gesprochen (Ton-Protokoll leer), und auf
die Frage, ob im Raum gesprochen wurde: nein. Also hat ein Geraeusch einen
ganzen Satz ergeben.

WARUM DAS PLAUSIBEL IST, aber gemessen werden muss: Im ausgeschalteten Zustand
ist die Grammatik `[STARTSATZ, "[unk]"]` - genau EIN echter Satz plus Auffang.
`[unk]` gewinnt nicht immer (in diesem Projekt schon dokumentiert). Ein
Geraeusch hat damit ein sehr kleines Ziel zu treffen. Das ist eine Vermutung,
und Vermutungen haben hier zweimal danebengelegen.

WAS DIESES SKRIPT TUT: Es hoert mit derselben Quelle und derselben Grammatik
wie der laufende Dienst, aber es LOEST NICHTS AUS. Zu jedem Ergebnis notiert es
den Pegel und - anders als der Dienst - die Konfidenz je Wort. Damit laesst
sich unterscheiden, ob ein Treffer knapp oder deutlich war.

Es greift nicht in den laufenden Dienst ein: PipeWire erlaubt mehrere Leser
derselben Quelle. Der Dienst laeuft weiter, kann also parallel ausloesen - das
ist Absicht, denn gemessen werden soll der echte Betriebszustand.

Aufruf:
    ./dialos-fehlstart-messen.py [SEKUNDEN]      Standard: 120
"""

import json
import math
import os
import struct
import subprocess
import sys
import time

MODELL = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
STARTSATZ = "sprachsteuerung starten"
GRAMMATIK_AUS = json.dumps([STARTSATZ, "[unk]"])
QUELLE = "dialos_mikrofon_ohne_echo"
BLOCK = 4000                      # Bytes, wie im Dienst: 2000 Proben = 125 ms


def pegel(block):
    """RMS des Blocks. audioop ist in Python 3.13 entfallen, daher zu Fuss."""
    n = len(block) // 2
    if not n:
        return 0.0
    werte = struct.unpack(f"<{n}h", block[:n * 2])
    return math.sqrt(sum(w * w for w in werte) / n)


def main():
    dauer = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    if not os.path.isdir(MODELL):
        print(f"Sprachmodell fehlt: {MODELL}", file=sys.stderr)
        return 1

    import vosk
    vosk.SetLogLevel(-1)
    modell = vosk.Model(MODELL)
    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
    erkenner.SetWords(True)

    quellen = subprocess.run(["pactl", "list", "short", "sources"],
                             capture_output=True, text=True, timeout=10).stdout
    quelle = QUELLE if QUELLE in quellen else None
    befehl = ["parec", f"--rate={ABTASTRATE}", "--channels=1", "--format=s16le"]
    if quelle:
        befehl += [f"--device={quelle}"]
    print(f"    Quelle:    {quelle or '(Systemvorgabe)'}")
    print(f"    Grammatik: {GRAMMATIK_AUS}")
    print(f"    Dauer:     {dauer} s")
    print(f"    Start:     {time.strftime('%H:%M:%S')}")
    print()
    print("    Jede Zeile ist ein Ergebnis. '[unk]' ist der gewuenschte Fall.")
    print("    Alles andere ist AUFFAELLIG - aber noch kein Fehlstart:")
    print("    Einschalten wuerde der Dienst nur bei einem Ergebnis, das das")
    print("    Kernwort enthaelt UND kein [unk]. Das entscheidet die Spalte")
    print("    'schaltet ein'.")
    print()

    p = subprocess.Popen(befehl, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    ende = time.time() + dauer
    pegel_max = 0.0
    pegel_summe, pegel_n = 0.0, 0
    ergebnisse = {"[unk]": 0}
    treffer = []
    try:
        while time.time() < ende:
            block = p.stdout.read(BLOCK)
            if not block:
                break
            p_wert = pegel(block)
            pegel_max = max(pegel_max, p_wert)
            pegel_summe += p_wert
            pegel_n += 1
            if not erkenner.AcceptWaveform(block):
                continue
            r = json.loads(erkenner.Result())
            text = r.get("text", "").strip()
            if not text:
                continue
            ergebnisse[text] = ergebnisse.get(text, 0) + 1
            if text == "[unk]":
                continue
            konf = [(w.get("word"), w.get("conf")) for w in r.get("result", [])]
            # Die Regel des Dienstes: Kernwort vorhanden UND kein [unk].
            # Ohne diese Unterscheidung meldet das Werkzeug jeden Wortfetzen
            # als Fehlstart - am 2026-08-24 hat es genau das getan und vier
            # gemeldet, von denen keiner eingeschaltet haette.
            schaltet = "starten" in text.split() and "[unk]" not in text
            treffer.append((time.strftime("%H:%M:%S"), text, p_wert, konf, schaltet))
            print(f"    {time.strftime('%H:%M:%S')}  '{text}'  "
                  f"Pegel {p_wert:.0f}  "
                  f"{'>>> SCHALTET EIN' if schaltet else '(schaltet nicht ein)'}")
            for wort, c in konf:
                print(f"                  {wort:22s} Konfidenz "
                      f"{c if c is None else f'{c:.3f}'}")
    finally:
        p.terminate()
        rest = json.loads(erkenner.FinalResult()).get("text", "").strip()
        if rest and rest != "[unk]":
            print(f"    (Schlussergebnis: '{rest}')")

    print()
    print(f"    Pegel:  Mittel {pegel_summe / max(1, pegel_n):.0f}, "
          f"Spitze {pegel_max:.0f}   ({pegel_n} Bloecke)")
    print(f"    Ergebnisse: {ergebnisse}")
    echte = [t for t in treffer if t[4]]
    print(f"    Auffaellige Ergebnisse: {len(treffer)}")
    print(f"    Davon ECHTE FEHLSTARTS (haetten eingeschaltet): {len(echte)}")
    if not echte:
        print("    In diesem Fenster keiner. Das WIDERLEGT nichts - es heisst")
        print("    nur, dass das Geraeusch dieses Fensters nicht gereicht hat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
