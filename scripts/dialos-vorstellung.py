#!/usr/bin/env python3
"""Erzeugt den Vorstellungs-Dialog als eine Audiodatei.

Stephans Wunsch vom 2026-08-22: rund zwei Minuten, Anna stellt die Fragen,
Michael antwortet, fuer moegliche Nutzer und Angehoerige - und der offene
Punkt kommt vor.

WARUM ALS SKRIPT UND NICHT ALS EINMALIGE DATEI: Stimme, Tempo und Aussprache
aendern sich in diesem Projekt regelmaessig. Am 2026-08-22 allein zweimal.
Eine fertige Audiodatei im Repo waere beim naechsten Mal veraltet, ohne dass
es jemandem auffaellt - dieselbe Falle wie bei den Hoerbeispielen, die
monatelang mit der falschen Stimme dalagen.

WARUM DER OFFENE PUNKT DRIN IST (Stephans Entscheidung): Ein Stand, der nur
Erfolge nennt, klingt nach Werbung. Wer ueberlegt, ein Geraet fuer einen
Angehoerigen anzuschaffen, will wissen, was NICHT geht.

Aufruf:
    scripts/dialos-vorstellung.py [--ziel DATEI]
"""

import importlib.machinery
import importlib.util
import os
import shlex
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO, "iso-build/config/includes.chroot/usr/local/bin")
PIPER_DIR = "/usr/local/share/dialos-piper"
STANDARD_ZIEL = os.path.join(REPO, "docs/video/dialos-vorstellung.ogg")

# Pause zwischen den Sprechern. Kurz genug, dass es ein Gespraech bleibt,
# lang genug, dass man den Sprecherwechsel hoert.
PAUSE_S = 0.45

# A = Anna fragt, M = Michael antwortet.
DIALOG = [
    ("A", "Michael, was ist eigentlich DialOS?"),
    ("M", "DialOS ist ein Betriebssystem, das man mit der Stimme bedient. "
          "Es ist für Menschen gemacht, die den Bildschirm nicht sehen oder "
          "die Maus und Tastatur nicht gut bedienen können."),
    ("A", "Es gibt doch schon Vorleseprogramme. Was ist hier anders?"),
    ("M", "Ein Vorleseprogramm liest vor, was auf dem Bildschirm steht. Es "
          "beschreibt also eine Oberfläche, die für Augen gebaut wurde. "
          "DialOS dreht das um: Es ist von Anfang an fürs Sprechen gemacht. "
          "Man sagt, was man will, und bekommt eine Antwort."),
    ("A", "Hört der Computer denn die ganze Zeit zu?"),
    ("M", "Nein. Im Normalzustand kennt er genau einen Satz: "
          "Sprachsteuerung starten. Erst danach gelten die Befehle, und nach "
          "zwei Minuten ohne Auftrag schaltet er sich von selbst wieder ab. "
          "Jeder Wechsel wird angesagt - wer nicht sieht, muss hören können, "
          "ob zugehört wird."),
    ("A", "Was kann DialOS heute schon?"),
    ("M", "Man kann Notizen und Einkaufszettel diktieren, sie vorlesen "
          "lassen, ergänzen und wegwerfen. Der Computer sagt Uhrzeit und "
          "Datum an, warnt, wenn der Akku zur Neige geht, und kann auf Zuruf "
          "Hilfe holen, wenn jemand von außen unterstützen soll. "
          "Mails bekommen automatisch einen Hinweis, dass sie per Sprache "
          "entstanden sind."),
    ("A", "Und was geht noch nicht?"),
    ("M", "Briefe. Der Weg dahin ist gebaut - man kann diktieren, "
          "Satzzeichen sprechen, und der Brief entsteht mit Datum und "
          "Briefkopf. Aber die Erkennung des Schlusssatzes ist noch zu "
          "empfindlich: Sie hält manchmal ein Stück laufender Rede für den "
          "Befehl Diktat beenden und bricht mitten im Satz ab. Daran wird "
          "gerade gearbeitet."),
    ("A", "Warum sagst Du das so offen?"),
    ("M", "Weil es niemandem hilft, ein Gerät zu bekommen, das etwas "
          "verspricht, was es nicht hält. Wer für einen Angehörigen "
          "überlegt, soll wissen, woran er ist."),
    ("A", "Was war bisher die größte Hürde?"),
    ("M", "Das Mikrofon. Ab Werk war die Aufnahme des Laptops so weit "
          "aufgedreht, dass das Signal dauerhaft am Anschlag klebte. Die "
          "Erkennung braucht aber die Pausen zwischen den Wörtern - und die "
          "gab es nicht mehr. Es sah aus wie ein Erkennungsproblem und war "
          "ein Pegelproblem."),
    ("A", "Und die Erkennung selbst?"),
    ("M", "Die liefert Wörter, keine Sätze. Kein Komma, kein Punkt, alles "
          "klein geschrieben. Für einen Einkaufszettel ist das egal, für "
          "einen Brief an die Krankenkasse nicht. Inzwischen werden neun von "
          "zehn Wörtern richtig groß geschrieben, und Satzzeichen kann man "
          "aussprechen."),
    ("A", "Gab es Überraschungen, mit denen niemand gerechnet hat?"),
    ("M", "Zwei, die ich nie vermutet hätte. Erstens: In völliger Stille "
          "erfindet die Erkennung Wörter. In achtzig Sekunden Ruhe waren es "
          "sieben - die landeten mitten im Text. Zweitens: Der Computer ging "
          "nach einer Viertelstunde von selbst schlafen. Ein Gerät, das man "
          "mit der Stimme bedient, aber nur durch Tastendruck wach bleibt, "
          "widerspricht sich selbst."),
    ("A", "Wie findet man so etwas?"),
    ("M", "Durch Messen, nicht durch Vermuten. Fast jeder dieser Fehler sah "
          "vorher nach etwas anderem aus. Und einige hat kein Programm "
          "gefunden, sondern ein Mensch, der zugehört hat - dass ein Name "
          "falsch betont wird, hört nur, wer ihn kennt."),
    ("A", "Wer entscheidet, wie DialOS spricht?"),
    ("M", "Der Nutzer. Man kann zwischen einer männlichen und einer "
          "weiblichen Stimme wählen, das Tempo einstellen, und der Computer "
          "spricht einen mit dem eigenen Namen an - da, wo es wichtig ist, "
          "und nicht bei jeder Kleinigkeit."),
    ("A", "Was kommt als Nächstes?"),
    ("M", "Der Brief soll zuverlässig zu Ende gehen. Danach das Drucken und "
          "ein Archiv, in dem jeder Brief und jede Mail als PDF liegt. "
          "Und irgendwann das Vorlesen von Post, die auf Papier kommt."),
]


def modul(pfad, name):
    lad = importlib.machinery.SourceFileLoader(name, pfad)
    spec = importlib.util.spec_from_loader(name, lad)
    m = importlib.util.module_from_spec(spec)
    lad.exec_module(m)
    return m


def main():
    argumente = sys.argv[1:]
    ziel = STANDARD_ZIEL
    if "--ziel" in argumente:
        i = argumente.index("--ziel")
        if i + 1 < len(argumente):
            ziel = argumente[i + 1]

    beispiele = modul(os.path.join(REPO, "scripts/dialos-sprachbeispiele.py"), "b")
    say = modul(os.path.join(BIN, "dialos-say.py"), "say")
    stimmen = modul(os.path.join(BIN, "dialos-stimme.py"), "st")
    wer = {"A": stimmen.STIMMEN["kerstin"], "M": stimmen.STIMMEN["thorsten"]}

    ordner = tempfile.mkdtemp(prefix="vorstellung-")
    teile = []
    stille = os.path.join(ordner, "pause.wav")
    subprocess.run(["sox", "-n", "-r", "22050", "-c", "1", "-b", "16",
                    stille, "trim", "0.0", str(PAUSE_S)], check=False)

    for nummer, (sprecher, text) in enumerate(DIALOG, 1):
        a = wer[sprecher]
        modell = "voices/" + a["kennung"] + ".onnx"
        roh = os.path.join(ordner, f"{nummer:02d}.wav")
        befehl = (
            f"cd {shlex.quote(PIPER_DIR)} && "
            f"printf %s {shlex.quote(say.fuer_sprachausgabe(text))} | "
            f"./piper/piper --model {shlex.quote(modell)} --noise_w 0 "
            f"--output_raw 2>/dev/null | "
            f"sox -r {beispiele.abtastrate(modell)} -c 1 -b 16 "
            f"-e signed-integer -t raw - -r 22050 {shlex.quote(roh)} "
            f"tempo {a['tempo']} norm 2>/dev/null")
        subprocess.run(["sh", "-c", befehl], check=False)
        if not os.path.exists(roh) or os.path.getsize(roh) == 0:
            print(f"  FEHLGESCHLAGEN: Zeile {nummer}", file=sys.stderr)
            return 1
        dauer = float(subprocess.run(["soxi", "-D", roh],
                                     capture_output=True, text=True).stdout.strip())
        print(f"  {nummer:02d}  {a['name']:8s} {dauer:5.1f} s  {text[:52]}…")
        teile += [roh, stille]

    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    subprocess.run(["sox"] + teile + ["-C", "5", ziel], check=False)
    gesamt = float(subprocess.run(["soxi", "-D", ziel],
                                  capture_output=True, text=True).stdout.strip())
    print(f"\n  {ziel}")
    print(f"  {gesamt:.0f} s  ({gesamt/60:.1f} Minuten), "
          f"{os.path.getsize(ziel)/1024:.0f} kB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
