#!/usr/bin/env python3
"""DialOS: den markierten Text vorlesen - „markierten Text vorlesen".

Seit 2026-11-24, der erste Baustein von „Vorlesen auf Zuruf" für Stufe 1
(siehe dialos_stufe.py): Wer noch sieht, aber schlecht liest, markiert mit der
Maus und lässt Michael lesen. Verfügbar in jeder Stufe - es ist ein Befehl,
und auf Befehle antwortet DialOS immer.

WOHER DER TEXT KOMMT: Unter Wayland darf ein Programm ohne Fenster die
Markierung nicht lesen (am 2026-11-24 gemessen). Die GNOME-Erweiterung
dialos@dialos.org darf es und gibt sie über D-Bus heraus.

Der Text wird so vorgelesen, wie er markiert ist. Sehr lange Markierungen
werden angekündigt und gekürzt: Vorlesen lässt sich bisher nicht unterbrechen
(TODO.md), und zehn Minuten am Stück, die man nicht anhalten kann, will
niemand.

Aufruf:
    dialos-markierung.py
"""

import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-markierung.log")
HOECHSTENS_ZEICHEN = 3000
# STUECKE STATT EINER ANSAGE: dialos-say.py spielt eine gespeicherte Ansage
# hoechstens 60 s lang ab (aus_speicher). 400 Zeichen sind rund 30 s - mit
# Abstand darunter. Dieselbe Loesung wie bei den Lizenzen.
STUECK_ZEICHEN = 400

ANSAGE_LEER = "Es ist nichts markiert. Markiere den Text mit der Maus und sage es noch einmal."
ANSAGE_FEHLT = ("Ich komme gerade nicht an den markierten Text. "
                "Vielleicht muss sich das Konto einmal neu anmelden.")


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    try:
        subprocess.run([SAY, text], timeout=900)
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"Sprachausgabe gescheitert: {fehler}")


def markierung_holen():
    """Den markierten Text von der GNOME-Erweiterung - oder None bei Fehler."""
    try:
        aus = subprocess.run(
            ["gdbus", "call", "--session", "--dest", "org.dialos.Shell",
             "--object-path", "/org/dialos/Shell",
             "--method", "org.dialos.Shell.MarkierungLesen"],
            capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"gdbus gescheitert: {fehler}")
        return None
    if aus.returncode != 0:
        melde(f"Erweiterung antwortet nicht: {aus.stderr.strip()[:200]}")
        return None
    return gvariant_text(aus.stdout)


def gvariant_text(ausgabe):
    """gdbus gibt "('Text',)" aus - den Text daraus, mit Escapes aufgeloest."""
    import ast
    try:
        wert = ast.literal_eval(ausgabe.strip())
        return wert[0] if isinstance(wert, tuple) and wert else ""
    except (ValueError, SyntaxError):
        return ""


def zum_vorlesen(text):
    """Zeilenumbrueche zu Pausen, Leerraum zusammenziehen, Laenge begrenzen."""
    text = " ".join(text.split())
    if len(text) <= HOECHSTENS_ZEICHEN:
        return text, False
    schnitt = text.rfind(" ", 0, HOECHSTENS_ZEICHEN)
    return text[:schnitt if schnitt > 0 else HOECHSTENS_ZEICHEN], True


def stuecke(text, laenge=STUECK_ZEICHEN):
    """Zerlegt an Satzenden in Stuecke von hoechstens `laenge` Zeichen.

    Ein einzelner Satz, der laenger ist, wird an einem Leerzeichen geteilt -
    nie mitten im Wort.
    """
    import re
    saetze = [x for x in re.split(r"(?<=[.!?:;])\s+", text) if x]
    teile, aktuell = [], ""
    for satz in saetze:
        while len(satz) > laenge:
            schnitt = satz.rfind(" ", 0, laenge)
            schnitt = schnitt if schnitt > 0 else laenge
            if aktuell:
                teile.append(aktuell)
                aktuell = ""
            teile.append(satz[:schnitt])
            satz = satz[schnitt:].lstrip()
        if aktuell and len(aktuell) + 1 + len(satz) > laenge:
            teile.append(aktuell)
            aktuell = satz
        else:
            aktuell = f"{aktuell} {satz}".strip()
    if aktuell:
        teile.append(aktuell)
    return teile


def main():
    text = markierung_holen()
    if text is None:
        sprich(ANSAGE_FEHLT)
        return 1
    if not text.strip():
        melde("nichts markiert")
        sprich(ANSAGE_LEER)
        return 0
    vorlesen, gekuerzt = zum_vorlesen(text)
    melde(f"lese {len(vorlesen)} von {len(text)} Zeichen")
    if gekuerzt:
        sprich("Der markierte Text ist lang. Ich lese den Anfang.")
    for stueck in stuecke(vorlesen):
        sprich(stueck)
    return 0


if __name__ == "__main__":
    sys.exit(main())
