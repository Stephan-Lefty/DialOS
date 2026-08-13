#!/usr/bin/env python3
"""DialOS: Sprachausgabe mit Audio-Ducking.

Schaltet andere Audioquellen (z.B. Radio, Musik) waehrend der Sprachausgabe
stumm und stellt sie danach wieder her. Speech-Dispatcher-eigene Streams
werden dabei bewusst ausgenommen.

Legt zusaetzlich waehrend der Sprachausgabe eine Markierungsdatei an (und
entfernt sie garantiert wieder, auch bei Fehlern) - darauf reagiert
dialos-tts-indicator.py mit einem Icon im GNOME-Panel, nuetzlich falls die
Lautstaerke zu leise eingestellt ist.
"""
import json
import subprocess
import sys

MARKIERUNGSDATEI = "/tmp/dialos-sprachausgabe-aktiv"


def sink_inputs():
    try:
        out = subprocess.run(
            ["pactl", "-f", "json", "list", "sink-inputs"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        return json.loads(out) if out.strip() else []
    except Exception:
        return []


def set_mute(index, stumm):
    subprocess.run(
        ["pactl", "set-sink-input-mute", str(index), "1" if stumm else "0"],
        capture_output=True, timeout=5,
    )


def ist_speech_dispatcher(stream):
    name = stream.get("properties", {}).get("application.name", "")
    return name.startswith("speech-dispatcher")


def markierung_setzen():
    try:
        open(MARKIERUNGSDATEI, "w").close()
    except Exception:
        pass


def markierung_entfernen():
    try:
        import os
        os.remove(MARKIERUNGSDATEI)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def main():
    text = " ".join(sys.argv[1:])
    if not text:
        return
    streams = sink_inputs()
    stummgeschaltet = []
    for stream in streams:
        index = stream.get("index")
        if index is None or ist_speech_dispatcher(stream):
            continue
        if not stream.get("mute", False):
            set_mute(index, True)
            stummgeschaltet.append(index)
    markierung_setzen()
    try:
        # Kurze "Aufwaerm"-Ansage, damit ein evtl. eingeschlafener
        # Bluetooth-Lautsprecher rechtzeitig aufwacht, bevor der
        # eigentliche Text gesprochen wird (sonst geht der Anfang verloren).
        subprocess.run(["spd-say", "--wait", "."])
        subprocess.run(["spd-say", "--wait", text])
    finally:
        for index in stummgeschaltet:
            set_mute(index, False)
        markierung_entfernen()


if __name__ == "__main__":
    main()
