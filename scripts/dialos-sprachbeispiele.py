#!/usr/bin/env python3
"""Erzeugt die Sprachbeispiele unter docs/sprachbeispiele/.

Zweck: zeigen, wie DialOS klingt, ohne dass jemand das Geraet vor sich hat.
Stephans Wunsch vom 2026-08-18.

WARUM EIN SKRIPT UND KEINE HANDARBEIT: Die Beispiele muessen nach jeder
Aenderung an Stimme oder Tempo neu erzeugt werden, sonst zeigen sie einen
Stand, den es nicht mehr gibt. Ein Skript macht das in einem Aufruf.

WARUM DIE TEXTE AUS DEN ECHTEN SKRIPTEN KOMMEN: Wochentag, Ordinalzahl und
Uhrzeit-als-Wort baut dialos-start-ansage.py selbst zusammen, und
dialos-say.py wendet vor dem Sprechen Aussprache-Regeln an ("Tastatur" wird
zu "Tas tatur", sonst klingt es wie "Taschtatur"). Von Hand geschriebene
Texte klaengen anders als das System - also holt dieses Skript die
Funktionen dort, wo sie stehen.

REPRODUZIERBAR ist das Ergebnis nur wegen "--noise_w 0": Piper hat einen
Zufallsanteil in der Lautdauer und sprach denselben Satz vorher mit bis zu
17 % anderer Dauer (gemessen 2026-08-18, siehe docs/diktat.md).

Aufruf:  scripts/dialos-sprachbeispiele.py [--ziel ORDNER]
"""

import importlib.util
import os
import shlex
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO, "iso-build/config/includes.chroot/usr/local/bin")
PIPER_DIR = "/usr/local/share/dialos-piper"
STIMME = "voices/de_DE-thorsten-high.onnx"
PIPER_CONF = "/etc/speech-dispatcher/modules/piper-generic.conf"


def tempo():
    """Liest das Sprechtempo aus der Sprechkette, statt es zu wiederholen.

    Fest eingetragen war hier "0.88" - derselbe Wert, der in
    piper-generic.conf steht. Das ist genau die Doppelung, die
    auseinanderlaeuft: Wer das Tempo dort aendert (wie am 2026-08-17 von 0.85
    auf 0.88), haette danach Hoerbeispiele in der alten Geschwindigkeit, und
    zwar ohne dass es jemandem auffaellt - denn sie klingen fuer sich genommen
    richtig. "Michael" soll immer gleich klingen (Stephan, 2026-08-19), und
    das geht nur mit einer Quelle.
    """
    try:
        with open(PIPER_CONF, encoding="utf-8") as f:
            for zeile in f:
                if zeile.startswith("GenericRateMultiply"):
                    return zeile.split()[1]
    except OSError:
        pass
    return "1.0"
ZIEL = os.path.join(REPO, "docs/sprachbeispiele")


def modul(pfad, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, pfad))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def erzeugen(datei, text, aussprache):
    """Rendert EINEN Text nach OGG - dieselbe Kette wie speech-dispatcher."""
    fuer_piper = aussprache(text)
    befehl = (
        f"cd {shlex.quote(PIPER_DIR)} && "
        f"printf %s {shlex.quote(fuer_piper)} | "
        f"./piper/piper --model {shlex.quote(STIMME)} --noise_w 0 --output_raw 2>/dev/null | "
        f"sox -r 22050 -c 1 -b 16 -e signed-integer -t raw - "
        f"-C 3 {shlex.quote(datei)} tempo {tempo()} norm 2>/dev/null"
    )
    subprocess.run(["sh", "-c", befehl], check=False)
    if not os.path.exists(datei) or os.path.getsize(datei) == 0:
        print(f"  FEHLGESCHLAGEN: {os.path.basename(datei)}", file=sys.stderr)
        return None
    dauer = subprocess.run(["soxi", "-D", datei], capture_output=True, text=True).stdout.strip()
    return float(dauer), os.path.getsize(datei)


def start_ansage_text(ansage):
    """Baut die Start-Ansage fuer nutzer mit den Funktionen des Originals.

    Die Werte sind Beispielwerte: Datum und Uhrzeit sind fest gewaehlt, damit
    das Beispiel reproduzierbar bleibt, und die Akkustaende sowie das Wetter
    sind erfunden - beides kommt im Betrieb von der Hardware und aus dem Netz.
    Der SATZBAU dagegen ist der echte, aus dialos-start-ansage.py.
    """
    tag, monat, stunde, minute = 18, 8, 7, 30
    import datetime
    wochentag = ansage.WOCHENTAGE[datetime.date(2026, monat, tag).weekday()]
    datum = f"{wochentag}, der {ansage.ORDINAL_TAGE[tag]} {ansage.MONATE[monat - 1]}"
    uhrzeit = f"{ansage.zahl_wort_0_99(stunde)} {ansage.zahl_wort_0_99(minute)}"
    text = ("Hallo, ich bin Michael, ich bin Dein persönlicher Assistent. "
            f"Heute ist {datum}. Die aktuelle Uhrzeit ist {uhrzeit}.")
    # nutzer bekommt nur Laptop und Lautsprecher (KIND_REIHENFOLGE_NUTZER)
    text += (" Ich nenne Dir noch die Akku-Stände."
             " Akku-Stand Laptop: 87 Prozent."
             " Akku-Stand Lautsprecher: 100 Prozent.")
    text += " Es besteht eine Internetverbindung."
    text += (" Das Wetter in Seefeld in Tirol wird heute so sein."
             " Vormittags 14 Grad und leicht bewölkt,"
             " nachmittags 19 Grad und sonnig.")
    text += " Ich wünsche Dir einen schönen Tag!"
    return text


def main():
    ziel = ZIEL
    if "--ziel" in sys.argv:
        ziel = sys.argv[sys.argv.index("--ziel") + 1]
    os.makedirs(ziel, exist_ok=True)

    say = modul("dialos-say.py", "dsay")
    ansage = modul("dialos-start-ansage.py", "dansage")
    aussprache = say.fuer_sprachausgabe

    beispiele = [
        ("01-start-ansage-nutzer", start_ansage_text(ansage)),
        ("02-lautstaerke-frage",
         "War das angenehm laut? Du kannst es einmalig festlegen. "
         "Sage 100, 75, 50, 25 oder aus. Und jetzt bitte."),
        ("03-sprachsteuerung-an", "Ich höre Dir zu."),
        ("04-sprachsteuerung-aus", "Ich höre Dir nicht mehr zu."),
        ("05-desktop-windows", "Windows Desktop."),
        ("06-desktop-steht-schon", "Steht schon auf Linux Desktop."),
        ("07-diktat-beginn",
         "Einen Moment, ich hole Zettel und Stift. Ich schreibe mit."),
        ("08-einkaufszettel-vorlesen",
         "4 Einträge. Tomaten. Bananen. Zwei Liter Milch. Butter."),
        ("09-einkaufszettel-wegwerfen",
         "Der Einkaufszettel hat 4 Einträge. Soll ich ihn löschen?"),
        ("10-ton-ueber-lautsprecher", "Ton über Lautsprecher."),
        ("11-kein-mikrofon", "Ich finde kein Mikrofon. Die Sprachsteuerung ist aus."),
    ]

    print(f"Ziel: {ziel}")
    zeilen = []
    for name, text in beispiele:
        datei = os.path.join(ziel, name + ".ogg")
        erg = erzeugen(datei, text, aussprache)
        if not erg:
            continue
        dauer, groesse = erg
        print(f"  {name+'.ogg':36s} {dauer:5.2f} s  {groesse/1024:5.1f} kB")
        zeilen.append((name, text, dauer, groesse))
    gesamt = sum(g for *_, g in zeilen)
    print(f"  {'zusammen':36s} {sum(d for *_, d, _ in zeilen):5.2f} s  {gesamt/1024:5.1f} kB")
    return zeilen


if __name__ == "__main__":
    main()
