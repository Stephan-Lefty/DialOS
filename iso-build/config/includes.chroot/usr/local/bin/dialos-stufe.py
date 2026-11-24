#!/usr/bin/env python3
"""DialOS: die Unterstützungsstufe ansehen und wechseln.

Seit 2026-11-24 (Stephan: „Lass uns jetzt schon die Schritte einbauen ... Und
wir können DialOS auch Usern an die Hand geben, die heute keine
Beeinträchtigung haben!"). Die Stufen selbst stehen in dialos_stufe.py.

Gewechselt wird per Sprache - „mehr Unterstützung" und „Unterstützung
verringern", eine Stufe je Satz - oder vom Helfer. NIE AUTOMATISCH, und in
beide Richtungen ohne Datenverlust: Eine Stufe schaltet nur Ansagen und
Sehhilfen, sie fasst keine Daten an.

Nach jedem Wechsel sagt Michael, welche Stufe jetzt gilt und was sie tut.
Hat der Erkenner den falschen Satz erwischt, hört der Nutzer es sofort.

SEHHILFEN AB STUFE 1 sind GNOME-Einstellungen dieses Kontos: größere Schrift,
hoher Kontrast, größerer Mauszeiger. Gesetzt werden sie NUR beim Wechsel,
nie bei jedem Anmelden - wer sie danach von Hand anders einstellt, behält
seine Wahl. Unter Stufe 1 werden sie auf die GNOME-Vorgabe zurückgesetzt.

Aufruf:
    dialos-stufe.py zeigen            sagt die aktuelle Stufe an
    dialos-stufe.py mehr              eine Stufe höher, mit Ansage
    dialos-stufe.py weniger           eine Stufe niedriger, mit Ansage
    dialos-stufe.py setzen N [--still]  für den Helfer
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dialos_stufe as st  # noqa: E402

SAY = "/usr/local/bin/dialos-say.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-stufe.log")

# Was jede Stufe TUT - in einem Satz, der beim Wechsel gesprochen wird.
# Kurz, weil der Nutzer ihn nach jedem Wechsel hört.
BESCHREIBUNG = {
    0: "Ich begrüße Dich und antworte, wenn Du mich fragst.",
    1: "Dazu große Schrift und starker Kontrast.",
    2: "Ich sage jetzt auch an, wenn sich etwas ändert.",
    3: "Volle Unterstützung.",
}

# GNOME-Einstellungen, die ab Stufe 1 gelten: (Schema, Schluessel, Wert).
SEHHILFEN = [
    ("org.gnome.desktop.interface", "text-scaling-factor", "1.25"),
    ("org.gnome.desktop.a11y.interface", "high-contrast", "true"),
    ("org.gnome.desktop.interface", "cursor-size", "48"),
]


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    melde(f"sagt: {text}")
    try:
        subprocess.run([SAY, text], timeout=60)
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"Sprachausgabe gescheitert: {fehler}")


def gsettings(*argumente):
    try:
        subprocess.run(["gsettings", *argumente], capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"gsettings gescheitert: {fehler}")


def sehhilfen_anpassen(stufe):
    """Ab Stufe 1 setzen, darunter auf die GNOME-Vorgabe zuruecksetzen."""
    for schema, schluessel, wert in SEHHILFEN:
        if stufe >= 1:
            gsettings("set", schema, schluessel, wert)
        else:
            gsettings("reset", schema, schluessel)
    melde(f"Sehhilfen {'an' if stufe >= 1 else 'aus'}")


def ansage(stufe):
    return f"{st.NAMEN[stufe]}. {BESCHREIBUNG[stufe]}"


def wechseln(neu, still=False):
    alt = st.stufe()
    neu = st.setzen(neu)
    melde(f"Stufe {alt} -> {neu}")
    if (alt >= 1) != (neu >= 1):
        sehhilfen_anpassen(neu)
    if not still:
        sprich(ansage(neu))
    return neu


def main():
    argumente = sys.argv[1:]
    befehl = argumente[0] if argumente else "zeigen"
    jetzt = st.stufe()
    if befehl == "zeigen":
        sprich(f"Du bist bei {st.NAMEN[jetzt]}. {BESCHREIBUNG[jetzt]}")
        return 0
    if befehl == "mehr":
        if jetzt >= st.HOECHSTE:
            sprich(f"Mehr geht nicht. Du bist schon bei {st.NAMEN[jetzt]}.")
            return 0
        wechseln(jetzt + 1)
        return 0
    if befehl == "weniger":
        if jetzt <= st.NIEDRIGSTE:
            sprich(f"Weniger geht nicht. Du bist schon bei {st.NAMEN[jetzt]}.")
            return 0
        wechseln(jetzt - 1)
        return 0
    if befehl == "setzen" and len(argumente) > 1:
        try:
            wert = int(argumente[1])
        except ValueError:
            print("Stufe muss 0 bis 3 sein.", file=sys.stderr)
            return 2
        wechseln(wert, still="--still" in argumente)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
