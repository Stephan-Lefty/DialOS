#!/usr/bin/env python3
"""Macht aus einer Sprechfassung eine Hoerfassung mit Annas Stimme.

WARUM EINE EIGENE SPRECHFASSUNG und nicht der Blogbeitrag selbst: Ein Text
zum Lesen und ein Text zum Hoeren sind nicht derselbe Text. Der Beitrag belegt
seine Aussagen mit Zahlen und Beispielen, weil man beim Lesen zurueckspringen
kann. Beim Hoeren geht das nicht. Der erste Versuch am 2026-09-17 war der
vorgelesene Beitrag - Stephans Urteil: zu technisch, zu lang. Seitdem wird die
Sprechfassung von Hand geschrieben und liegt in `sprechfassungen/`.

TONAUFBEREITUNG wie in scripts/dialos-vorstellung.py: Piper liefert Rohton in
der Modellrate (kerstin-low: 16 kHz), danach Tempo 0,95, 22050 Hz,
spitzennormalisiert. Die 0,95 hat Stephan am 2026-08-22 im Hoervergleich
gewaehlt - nicht ausgerechnet, nicht aendern ohne neuen Hoervergleich.

STATT sox (im Repo ueblich) rechnet hier ffmpeg, weil das Skript auch auf
Rechnern ohne DialOS laufen soll. Die Spitzennormalisierung laeuft deshalb in
zwei Durchgaengen: erst messen, dann anheben - das ist, was sox' "norm" tut.

Voraussetzungen:
    pip install piper-tts
    de_DE-kerstin-low.onnx (+ .onnx.json) von huggingface.co/rhasspy/piper-voices
    ffmpeg, ffprobe

Pfade ueber Umgebungsvariablen, sonst die Standardorte von DialOS:
    ANNA_MODELL   Pfad zur .onnx-Datei
    ANNA_PYTHON   Python mit installiertem piper-tts

Aufruf:
    ./dialos-hoerfassung-sprechen.py sprechfassungen/315-von-drei-auf-26-saetze.txt
    ./dialos-hoerfassung-sprechen.py <datei.txt> <ziel.mp3>
"""
import os
import re
import subprocess
import sys

MODELL = os.environ.get(
    "ANNA_MODELL", "/usr/local/share/dialos-piper/voices/de_DE-kerstin-low.onnx")
PYTHON = os.environ.get("ANNA_PYTHON", sys.executable)

TEMPO = 0.95              # Stephans Wahl im Hoervergleich, 2026-08-22
ZIELRATE = 22050
PAUSE_SATZ = 0.45
HOECHSTDAUER = 120        # Stephans Vorgabe, 2026-09-17: nie laenger als zwei Minuten

# Woerter, die Stephan beim Hoeren beanstandet hat - entweder weil Anna sie
# falsch betont oder weil sie zu technisch klingen. Die Liste waechst mit jedem
# Hoertest. Ersetzt wird NIE automatisch, nur gemeldet: Was an die Stelle
# gehoert, entscheidet der Sinn des Satzes, nicht eine Tabelle.
HEIKEL = {
    "Grammatik": "richtige Laenge, falsche Betonung - besser: Satzbau",
    "Labor": "zu technisch",
    "Gegenteil": "von Stephan beanstandet",
    "Dazuschreiben": "von Stephan beanstandet",
    "Vosk": "Fachbegriff",
    "Piper": "Fachbegriff",
    "ISO": "Fachbegriff",
    "Commit": "Fachbegriff",
    "Repository": "Fachbegriff",
}


def anna_aussprache(text):
    """Dieselbe Regel wie fuer_sprachausgabe() in dialos-say.py.

    Anna spricht die Buchstaben einzeln ("Dial O S"). Der Lookahead schont
    "dialos.org": ein Punkt zaehlt nur dann zum Wort, wenn ein Buchstabe folgt.
    """
    return re.compile(r"\bDialOS\b(?!\.[A-Za-z])", re.IGNORECASE).sub(
        "Dial O S", text)


def pruefen(text):
    """Meldet, was Anna erfahrungsgemaess schlecht ausspricht."""
    warnungen = []
    for zahl in sorted(set(re.findall(r"\b\d+\b", text))):
        warnungen.append(
            f'Ziffer "{zahl}" - wird zwar ausgeschrieben, aber gehetzt '
            f"(gemessen 2026-09-17: 22 % kuerzer als das Wort). Ausschreiben.")
    for wort, grund in HEIKEL.items():
        if re.search(rf"\b{re.escape(wort)}\b", text, re.IGNORECASE):
            warnungen.append(f'Wort "{wort}" - {grund}')
    return warnungen


def dauer(datei):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", datei], capture_output=True, text=True).stdout.strip())


def spitze_db(datei):
    aus = subprocess.run(
        ["ffmpeg", "-i", datei, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    treffer = re.search(r"max_volume: (-?[\d.]+) dB", aus)
    return float(treffer.group(1)) if treffer else 0.0


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 1
    quelle = sys.argv[1]
    ziel = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(quelle)[0] + ".mp3"

    if not os.path.exists(MODELL):
        print(f"Stimmmodell nicht gefunden: {MODELL}\n"
              f"Pfad ueber ANNA_MODELL setzen.", file=sys.stderr)
        return 1

    with open(quelle) as f:
        text = f.read().strip()

    woerter = len(text.split())
    print(f"Sprechfassung: {os.path.basename(quelle)}  ({woerter} Woerter)")
    for warnung in pruefen(text):
        print(f"  ACHTUNG: {warnung}")

    roh = ziel + ".roh.wav"
    tempo = ziel + ".tempo.wav"
    lauf = subprocess.run(
        [PYTHON, "-m", "piper", "-m", MODELL, "-f", roh,
         "--sentence-silence", str(PAUSE_SATZ)],
        input=anna_aussprache(text), capture_output=True, text=True)
    if not os.path.exists(roh) or os.path.getsize(roh) == 0:
        print(f"Piper hat nichts erzeugt:\n{lauf.stderr[-800:]}", file=sys.stderr)
        return 1

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", roh,
                    "-af", f"atempo={TEMPO}", "-ar", str(ZIELRATE), tempo],
                   check=True)
    anheben = -spitze_db(tempo)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tempo,
                    "-af", f"volume={anheben:.2f}dB",
                    "-codec:a", "libmp3lame", "-qscale:a", "5", ziel], check=True)
    for weg in (roh, tempo):
        os.remove(weg)

    d = dauer(ziel)
    print(f"  {ziel}")
    print(f"  {int(d // 60)}:{int(d % 60):02d} Minuten, "
          f"{os.path.getsize(ziel) / 1024:.0f} kB, "
          f"{woerter / (d / 60):.0f} Woerter pro Minute")
    if d > HOECHSTDAUER:
        zuviel = d - HOECHSTDAUER
        print(f"  ZU LANG: {zuviel:.0f} s ueber der Grenze von zwei Minuten - "
              f"rund {int(zuviel / (d / woerter))} Woerter streichen")
        return 2
    print(f"  in der Zeit ({HOECHSTDAUER - d:.0f} s Luft)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
