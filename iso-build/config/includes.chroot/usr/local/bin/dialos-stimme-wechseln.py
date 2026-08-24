#!/usr/bin/env python3
"""Stimme umschalten - Michael <-> Anna. Gedacht fuer eine Tastenkombination.

WARUM ES DIESES SKRIPT GIBT, obwohl dialos-stimme.py schon umstellen kann:
"setzen" macht nur die Haelfte der Arbeit. Es schreibt die
Piper-Konfiguration - dafuer braucht es root - und sagt dem Menschen danach,
er moege speech-dispatcher neu starten. Am Terminal ist das zumutbar. Hinter
einer Taste nicht: Wer eine Taste drueckt, erwartet, dass die naechste Ansage
anders klingt, und keine Hausaufgabe.

Dieses Skript laeuft deshalb OHNE root und teilt die Arbeit auf:
  - Den privilegierten Teil ruft es ueber sudo auf. Die Regel steht in
    /etc/sudoers.d/dialos-stimme und nennt die erlaubten Aufrufe woertlich,
    ohne Platzhalter.
  - Den Sitzungsteil - speech-dispatcher neu starten - macht es selbst. Root
    koennte den Dienst des angemeldeten Nutzers gar nicht neu starten; das
    ist derselbe Grund, aus dem dialos-aufspielen die Sitzungsdienste nur
    MELDET, statt sie anzufassen.

Die Liste der Stimmen wird NICHT hier wiederholt, sondern aus
dialos-stimme.py gelesen. Zwei Listen, die dasselbe wissen muessen, laufen
frueher oder later auseinander - und dann schaltet die Taste auf eine Stimme,
die es nicht gibt.

Aufruf:
    dialos-stimme-wechseln.py     -> auf die naechste Stimme in der Liste
"""

import importlib.util
import os
import subprocess
import sys
import time

STIMME_SKRIPT = "/usr/local/bin/dialos-stimme.py"
SAY = "/usr/local/bin/dialos-say.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-stimme-wechseln.log")


def melde(text):
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
    with open(PROTOKOLL, "a") as f:
        f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")


def sprich(text):
    """Ansage - und wenn die Sprachausgabe streikt, wenigstens ins Protokoll."""
    try:
        subprocess.run([SAY, text], capture_output=True, timeout=60)
    except Exception as fehler:
        melde(f"Ansage nicht moeglich: {fehler}")


def stimme_modul():
    """dialos-stimme.py als Modul laden, um STIMMEN und gelesen() zu nutzen."""
    spec = importlib.util.spec_from_file_location("dialos_stimme", STIMME_SKRIPT)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def naechste(modul):
    """Die naechste Stimme in der Liste - nicht "die andere".

    Bei zwei Stimmen ist das dasselbe. Bei einer dritten waere "die andere"
    keine eindeutige Angabe mehr, und die Taste taete etwas Zufaelliges.
    """
    kennung, _tempo, _name = modul.gelesen()
    kurznamen = list(modul.STIMMEN)
    for i, kurz in enumerate(kurznamen):
        if modul.STIMMEN[kurz]["kennung"] == kennung:
            return kurznamen[(i + 1) % len(kurznamen)]
    # Unbekannte Stimme in der Konfiguration: auf die erste bekannte gehen,
    # statt gar nichts zu tun. Stumm bleiben waere hier der schlechtere Weg.
    melde(f"unbekannte Stimme in der Konfiguration: {kennung}")
    return kurznamen[0]


def main():
    modul = stimme_modul()
    ziel = naechste(modul)
    name = modul.STIMMEN[ziel]["name"]
    melde(f"=== umschalten auf {ziel} ({name}) ===")

    p = subprocess.run(["sudo", "-n", STIMME_SKRIPT, "setzen", ziel],
                       capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        melde(f"setzen fehlgeschlagen: {p.stderr.strip()}")
        sprich("Ich konnte die Stimme nicht umstellen.")
        return 1

    # Erst jetzt greift die neue Stimme. Ohne diesen Neustart spraeche das
    # Geraet bis zur naechsten Anmeldung weiter mit der alten.
    n = subprocess.run(["systemctl", "--user", "restart",
                        "speech-dispatcher.service"],
                       capture_output=True, text=True, timeout=30)
    if n.returncode != 0:
        melde(f"speech-dispatcher nicht neu gestartet: {n.stderr.strip()}")
        # Die Umstellung ist trotzdem geschrieben - beim naechsten Anmelden
        # gilt sie. Das gehoert gesagt, sonst haelt der Nutzer die Taste fuer
        # kaputt.
        sprich("Die Stimme ist umgestellt, sie gilt aber erst nach dem "
               "naechsten Anmelden.")
        return 1

    # speech-dispatcher braucht einen Moment, bis es wieder annimmt. Ohne die
    # Pause faellt die erste Ansage nach dem Umschalten aus - ausgerechnet die,
    # die zeigen soll, dass es geklappt hat.
    time.sleep(1.5)
    melde(f"umgestellt auf {name}")
    sprich(f"Ich bin jetzt {name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
