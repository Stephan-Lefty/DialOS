#!/usr/bin/env python3
"""DialOS: Stimme des Assistenten umschalten - Klang, Name und Tempo zusammen.

Stephans Entscheidung vom 2026-08-20: eine freundliche Damenstimme. Aus der
Auswahl per Hoervergleich wurde `de_DE-kerstin-low`, und ihr Tempo 1.00 - beides
von ihm gehoert und nicht gerechnet.

WARUM DREI DINGE ZUSAMMEN UMSCHALTEN und nicht nur die Stimmdatei:

  * DER NAME steht in der Start-Ansage ("Hallo, ich bin Michael"). Eine
    Frauenstimme, die sich als Michael vorstellt, waere schlicht falsch - und
    ein Nutzer, der den Bildschirm nicht sieht, hat nur diesen Namen, um das
    Geraet anzusprechen. Die Namen sind seit langem festgelegt, siehe
    docs/ersteinrichtung.md: maennlich Michael und Daniel, weiblich Anna und
    Julia. Das Aufweckwort wird spaeter derselbe Name sein ("Hallo Anna").

  * DAS TEMPO ist pro Stimme verschieden, und zwar deutlich. Gemessen am
    2026-08-20 mit demselben Satz: Thorsten 7,75 s bei 0.88, Kerstin 8,99 s bei
    demselben Wert - 16 % langsamer. Erst 1.00 bringt sie auf 7,91 s und damit
    auf Thorstens Sprechgeschwindigkeit. Ein gemeinsamer Wert fuer alle Stimmen
    waere fuer die eine oder andere immer falsch.

  * DIE ABTASTRATE steht in der .json der Stimme (Kerstin 16000 Hz, Thorsten
    22050 Hz). Sie wird nicht hier eingetragen, sondern von dialos-say.py aus
    der Datei gelesen - eine Zahl, die man abschreibt, ist eine Zahl, die
    auseinanderlaeuft.

WAS MIT DEM ANSAGEN-SPEICHER PASSIERT: Nichts von Hand. Der Schluessel in
dialos-say.py enthaelt die Aenderungszeit von piper-generic.conf; wird sie hier
geschrieben, treffen alte Eintraege nie wieder zu. Sie belegen nur noch Platz,
und der Speicher fuellt sich in der neuen Stimme von selbst wieder.

Aufruf:
    dialos-stimme.py zeigen
    sudo dialos-stimme.py setzen kerstin
"""

import os
import re
import shutil
import sys

PIPER_CONF = "/etc/speech-dispatcher/modules/piper-generic.conf"
PIPER_STIMMEN = "/usr/local/share/dialos-piper/voices"
NAME_DATEI = "/usr/local/share/dialos/assistent-name.txt"
SPEICHER = os.path.join(
    os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
    "dialos", "ansagen")

# Die bekannten Stimmen. Tempo jeweils von Stephan im Hoervergleich gewaehlt -
# NICHT ausgerechnet. Wer eine Stimme ergaenzt, laesst ihn vorher denselben Satz
# in mehreren Tempi hoeren; die Zahl allein sagt nicht, ob es gut klingt.
STIMMEN = {
    "thorsten": {
        "kennung": "de_DE-thorsten-high",
        "name": "Michael",
        "tempo": "0.88",     # gewaehlt 2026-08-17
    },
    "kerstin": {
        "kennung": "de_DE-kerstin-low",
        "name": "Anna",
        # 2026-08-22 von 1.00 auf 0.95. Die 1.00 war am 2026-08-20 aus
        # Hoerproben gewaehlt worden, die 38 % ZU SCHNELL liefen: Der
        # Beispiel-Erzeuger deklarierte Kerstins 16-kHz-Rohdaten als
        # 22050 Hz. Stephan hat es gehoert ("Miky Maus Stimme"), nicht
        # gemessen. Nach der Korrektur neu vorgespielt - 0.80, 0.90, 0.95,
        # 1.00, 1.10, 1.20 - und seine Wahl war 0.95.
        "tempo": "0.95",     # gewaehlt 2026-08-22, siehe oben
    },
}


def gelesen():
    """Was gerade eingestellt ist."""
    kennung = tempo = None
    try:
        with open(PIPER_CONF) as f:
            for zeile in f:
                if zeile.startswith("DefaultVoice"):
                    teile = zeile.split('"')
                    if len(teile) > 1:
                        kennung = teile[1]
                elif zeile.startswith("GenericRateMultiply"):
                    tempo = zeile.split()[1]
    except OSError as fehler:
        print(f"{PIPER_CONF} nicht lesbar: {fehler}", file=sys.stderr)
    name = "Michael"
    try:
        with open(NAME_DATEI) as f:
            name = f.read().strip() or name
    except OSError:
        pass
    return kennung, tempo, name


def zeigen():
    kennung, tempo, name = gelesen()
    da = os.path.exists(os.path.join(PIPER_STIMMEN, f"{kennung}.onnx"))
    print(f"Stimme:  {kennung} {'' if da else '(NICHT installiert!)'}")
    print(f"Name:    {name}")
    print(f"Tempo:   {tempo}")
    print()
    print("Bekannt:")
    for kurz, s in STIMMEN.items():
        vorhanden = os.path.exists(os.path.join(PIPER_STIMMEN, s['kennung'] + ".onnx"))
        aktiv = " <- aktiv" if s["kennung"] == kennung else ""
        print(f"  {kurz:10s} {s['kennung']:22s} {s['name']:8s} Tempo {s['tempo']}"
              f"  {'installiert' if vorhanden else 'FEHLT'}{aktiv}")
    return 0


def setzen(kurz):
    if kurz not in STIMMEN:
        print(f"Unbekannt: {kurz}. Bekannt: {', '.join(STIMMEN)}", file=sys.stderr)
        return 2
    s = STIMMEN[kurz]
    modell = os.path.join(PIPER_STIMMEN, s["kennung"] + ".onnx")
    if not os.path.exists(modell):
        # NICHT umschalten auf eine Stimme, die es nicht gibt. Sonst spraeche
        # das Geraet beim naechsten Anmelden gar nicht mehr - und der Nutzer
        # koennte nicht einmal fragen, warum.
        print(f"Stimmdatei fehlt: {modell}", file=sys.stderr)
        return 1
    if os.geteuid() != 0:
        print("setzen braucht root (schreibt nach /etc und /usr/local/share).",
              file=sys.stderr)
        return 1

    shutil.copy2(PIPER_CONF, PIPER_CONF + ".vorher")
    with open(PIPER_CONF) as f:
        inhalt = f.read()
    inhalt, n1 = re.subn(r'^DefaultVoice\s+".*"$',
                         f'DefaultVoice "{s["kennung"]}"', inhalt, flags=re.M)
    inhalt, n2 = re.subn(r'^GenericRateMultiply\s+\S+$',
                         f'GenericRateMultiply {s["tempo"]}', inhalt, flags=re.M)
    if n1 != 1 or n2 != 1:
        print(f"Unerwartete Konfiguration: DefaultVoice {n1}x, "
              f"GenericRateMultiply {n2}x gefunden - nichts geaendert.",
              file=sys.stderr)
        return 1
    with open(PIPER_CONF, "w") as f:
        f.write(inhalt)

    os.makedirs(os.path.dirname(NAME_DATEI), exist_ok=True)
    with open(NAME_DATEI, "w") as f:
        f.write(s["name"] + "\n")
    os.chmod(NAME_DATEI, 0o644)

    print(f"Stimme:  {s['kennung']}")
    print(f"Name:    {s['name']}")
    print(f"Tempo:   {s['tempo']}")
    print(f"(Sicherung der alten Konfiguration: {PIPER_CONF}.vorher)")
    print()
    print("speech-dispatcher neu starten, damit es greift:")
    print("    systemctl --user restart speech-dispatcher.service")
    print("oder einfach ab- und wieder anmelden.")
    return 0


def main():
    was = sys.argv[1] if len(sys.argv) > 1 else "zeigen"
    if was == "zeigen":
        return zeigen()
    if was == "setzen" and len(sys.argv) > 2:
        return setzen(sys.argv[2])
    print("Aufruf: dialos-stimme.py zeigen | setzen <kurzname>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
