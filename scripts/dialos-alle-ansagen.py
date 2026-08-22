#!/usr/bin/env python3
"""Erzeugt JEDEN Satz, den DialOS sprechen kann - in beiden Stimmen.

Stephans Wunsch vom 2026-08-21: alle Ansagen als einzelne Audiodateien, mit
Michael UND Anna, einschliesslich der Saetze, die erst zur Laufzeit entstehen
(Begruessung, Uhrzeit, Datum).

UNTERSCHIED ZU scripts/dialos-sprachbeispiele.py: Das dort ist eine AUSWAHL
fuers Repo - siebzehn Dateien, die zeigen, wie DialOS klingt. Dieses Werkzeug
hier ist die VOLLSTAENDIGE Liste zum Durchhoeren, in beiden Stimmen, und
landet bewusst NICHT im Repo: rund hundert Dateien, die sich bei jeder
Textaenderung aendern.

DIE SAETZE WERDEN GESAMMELT, NICHT ABGESCHRIEBEN. Drei Quellen:

  1. Jede Konstante ANSAGE_* in den Skripten unter usr/local/bin.
  2. Jeder feste Text, der direkt in einem sprich("...") steht.
  3. Die zusammengesetzten Saetze - Begruessung, Uhrzeit, Datum, Akkustufen,
     Diktatende, Notiz-Rueckfragen. Sie werden ERZEUGT, indem die echten
     Funktionen aufgerufen und ihr sprich() abgefangen wird. Damit steht hier
     kein einziger Satz doppelt im Quelltext, und eine Textaenderung wirkt
     sofort mit.

TEMPO UND STIMME kommen aus dialos-stimme.py, nicht von Hand: Jede Stimme hat
ihr eigenes Tempo (Michael 0,88, Anna 1,00), und derselbe Satz braucht bei
Kerstin mit Thorstens Wert 8,99 s statt 7,91 s.

Aufruf:
    scripts/dialos-alle-ansagen.py [--ziel ORDNER]
"""

import ast
import importlib.util
import os
import shlex
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO, "iso-build/config/includes.chroot/usr/local/bin")
PIPER_DIR = "/usr/local/share/dialos-piper"
STANDARD_ZIEL = os.path.join(REPO, "docs/sprachbeispiele/alle-ansagen")


def modul(name, kennung=None):
    pfad = os.path.join(BIN, name)
    spec = importlib.util.spec_from_file_location(kennung or name.replace(".", "_"), pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BEGRUESSUNG_MARKE = "<<begruessung>>"


def begruessung_fuer(stimmenname):
    """Die echte Start-Ansage mit dem Namen DIESER Stimme und der Uhr von jetzt.

    Geholt aus scripts/dialos-sprachbeispiele.py, nicht nachgebaut - mein
    erster Nachbau hier liess "ich bin Dein persoenlicher Assistent" weg und
    stellte die Uhrzeit falsch.
    """
    import datetime
    beispiele = modul_aus_scripts("dialos-sprachbeispiele.py", "d_beispiele")
    ansage = modul("dialos-start-ansage.py", "d_ansage")
    ansage.assistent_name = lambda: stimmenname
    return beispiele.start_ansage_text(ansage, datetime.datetime.now())


def modul_aus_scripts(name, kennung):
    pfad = os.path.join(REPO, "scripts", name)
    spec = importlib.util.spec_from_file_location(kennung, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def feste_saetze():
    """Alle ANSAGE_*-Konstanten und alle festen sprich("...")-Texte."""
    gefunden = []
    for datei in sorted(f for f in os.listdir(BIN) if f.endswith(".py")):
        quelle = datei[len("dialos-"):-len(".py")]
        baum = ast.parse(open(os.path.join(BIN, datei), encoding="utf-8").read())
        for k in baum.body:
            if not isinstance(k, ast.Assign):
                continue
            for ziel in k.targets:
                if (isinstance(ziel, ast.Name) and ziel.id.startswith("ANSAGE")
                        and isinstance(k.value, ast.Constant)
                        and isinstance(k.value.value, str)
                        # ANSAGE_SKRIPT ist ein Pfad, kein Satz.
                        and not k.value.value.startswith("/")):
                    gefunden.append((quelle, ziel.id.lower(), k.value.value))
        for k in ast.walk(baum):
            if (isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
                    and k.func.id == "sprich" and k.args
                    and isinstance(k.args[0], ast.Constant)
                    and isinstance(k.args[0].value, str)):
                gefunden.append((quelle, "im-code", k.args[0].value))
    return gefunden


def gebaute_saetze():
    """Die Saetze, die erst zur Laufzeit entstehen - echt aufgerufen."""
    gefunden = []

    # Uhrzeit und Datum: das echte sprich() abfangen, statt den Satz
    # nachzubauen. So gilt hier automatisch jede Formulierungsaenderung.
    auskunft = modul("dialos-auskunft.py", "d_auskunft")
    gesagt = []
    auskunft.sprich = gesagt.append
    auskunft.melde = lambda t: None
    a = auskunft.bausteine()
    if a:
        auskunft.uhrzeit(a)
        auskunft.datum(a)
        for name, satz in zip(("uhrzeit", "datum"), gesagt):
            gefunden.append(("auskunft", name, satz))

    # BEGRUESSUNG: geholt, nicht nachgebaut. Mein erster Nachbau hier war
    # falsch - er liess "ich bin Dein persoenlicher Assistent" weg und sagte
    # "es ist elf sechsunddreissig Uhr" statt "Die aktuelle Uhrzeit ist elf
    # sechsunddreissig". Aufgefallen ist es nur, weil Auskunft und Begruessung
    # nebeneinander lagen und unterschiedlich klangen. Der Satz steht schon in
    # scripts/dialos-sprachbeispiele.py nachgebaut; eine dritte Fassung waere
    # eine dritte Stelle, an der er veraltet.
    #
    # JE STIMME NEU: Die Begruessung nennt den Namen des Assistenten, und der
    # haengt an der eingestellten Stimme. Ohne diesen Umweg saegte Michaels
    # Datei "ich bin Anna" - der Name kaeme aus assistent-name.txt, also aus
    # der Stimme, die gerade EINGESTELLT ist, nicht aus der, die gerade
    # gerendert wird. Deshalb steht hier ein Platzhalter, den main() je Stimme
    # ersetzt.
    gefunden.append(("start", "begruessung", BEGRUESSUNG_MARKE))

    # Akkustufen, die dringende mit Namensanrede - genau wie im Betrieb
    akku = modul("dialos-akku-warnung.py", "d_akku")
    for grenze, text, dringend in akku.STUFEN:
        gefunden.append(("akku", f"stufe-{grenze}",
                         akku.anrede(text) if dringend else text))

    # Diktatende je Ziel
    diktat = modul("dialos-diktat.py", "d_diktat")
    for ziel, anzahl in (("notizen", 3), ("einkaufszettel", 4), ("brief", 2)):
        gefunden.append(("diktat", f"ende-{ziel}", diktat.ansage_ende(ziel, anzahl)))

    # Notizen: Vorlesen und die Rueckfrage vor dem Leeren
    notiz = modul("dialos-notiz.py", "d_notiz")
    waren = ["Milch", "Butter", "Sechs Eier"]
    gefunden.append(("notiz", "vorlesen",
                     f"{len(waren)} Einträge. " + notiz.aufzaehlen(waren)))
    bez, _ist, hat, ihn = notiz.benennen("einkaufszettel")
    gefunden.append(("notiz", "rueckfrage-leeren",
                     f"{bez} {hat} {len(waren)} Einträge. "
                     f"Soll ich {ihn} löschen? Sage ja oder nein."))

    # Schreibtisch-Umschaltung
    for name, satz in (("linux", "Linux Desktop."),
                       ("windows", "Windows Desktop."),
                       ("steht-schon", "Der Schreibtisch steht schon auf Linux Desktop.")):
        gefunden.append(("desktop", name, satz))
    return gefunden


def erzeugen(datei, text, modell, tempo, aussprache):
    """Dieselbe Kette wie speech-dispatcher - siehe dialos-sprachbeispiele.py."""
    fuer_piper = aussprache(text)
    befehl = (
        f"cd {shlex.quote(PIPER_DIR)} && "
        f"printf %s {shlex.quote(fuer_piper)} | "
        f"./piper/piper --model {shlex.quote(modell)} --noise_w 0 --output_raw 2>/dev/null | "
        f"sox -r 22050 -c 1 -b 16 -e signed-integer -t raw - "
        f"-C 3 {shlex.quote(datei)} tempo {tempo} norm 2>/dev/null")
    subprocess.run(["sh", "-c", befehl], check=False)
    return os.path.exists(datei) and os.path.getsize(datei) > 0


def main():
    argumente = sys.argv[1:]
    ziel = STANDARD_ZIEL
    if "--ziel" in argumente:
        i = argumente.index("--ziel")
        if i + 1 < len(argumente):
            ziel = argumente[i + 1]

    say = modul("dialos-say.py", "d_say")
    stimmen = modul("dialos-stimme.py", "d_stimme")

    saetze = feste_saetze() + gebaute_saetze()
    # Doppelte entfernen, Reihenfolge behalten
    gesehen, einmalig = set(), []
    for quelle, name, text in saetze:
        if text in gesehen:
            continue
        gesehen.add(text)
        einmalig.append((quelle, name, text))

    print(f"{len(einmalig)} verschiedene Sätze, {len(stimmen.STIMMEN)} Stimmen")
    verzeichnis = []
    for kennung, angaben in stimmen.STIMMEN.items():
        modell = "voices/" + angaben["kennung"] + ".onnx"
        if not os.path.exists(os.path.join(PIPER_DIR, modell)):
            print(f"  {angaben['name']}: {modell} fehlt - übersprungen")
            continue
        # EIN Ordner, die Stimme HINTEN im Namen (Stephans Vorgabe vom
        # 2026-08-22). So liegen dieselbe Ansage in beiden Stimmen direkt
        # untereinander, wenn man den Ordner sortiert - zum Vergleichen ist
        # das der kuerzeste Weg.
        os.makedirs(ziel, exist_ok=True)
        stimme = angaben["name"].lower()
        print(f"\n  {angaben['name']} ({angaben['kennung']}, Tempo {angaben['tempo']})")
        gemacht = 0
        for nummer, (quelle, name, text) in enumerate(einmalig, 1):
            basis = f"{nummer:02d}-{quelle}-{name}-{stimme}.ogg"
            if text == BEGRUESSUNG_MARKE:
                text = begruessung_fuer(angaben["name"])
            if erzeugen(os.path.join(ziel, basis), text, modell,
                        angaben["tempo"], say.fuer_sprachausgabe):
                gemacht += 1
            else:
                print(f"    FEHLGESCHLAGEN: {basis}")
            if kennung == list(stimmen.STIMMEN)[0]:
                verzeichnis.append((f"{nummer:02d}-{quelle}-{name}", quelle, text))
        print(f"    {gemacht} Dateien")

    # Verzeichnis, damit man ohne Anhoeren weiss, was worin steckt
    with open(os.path.join(ziel, "VERZEICHNIS.md"), "w", encoding="utf-8") as f:
        f.write("# Alle Ansagen von DialOS\n\n")
        f.write(f"Erzeugt am {time.strftime('%Y-%m-%d %H:%M')} mit "
                "`scripts/dialos-alle-ansagen.py`.\n\n")
        f.write("Jede Ansage liegt zweimal vor: `...-michael.ogg` und "
                "`...-anna.ogg`.\n\n| Dateiname (ohne Stimme) | Quelle | Text |"
                "\n|---|---|---|\n")
        for basis, quelle, text in verzeichnis:
            f.write(f"| `{basis}-*.ogg` | {quelle} | {text} |\n")
        f.write("\n*Eine Ausnahme: Die **Begrüßung** nennt den Namen des "
                "Assistenten und lautet deshalb in jeder Stimme anders - "
                "Michael sagt „ich bin Michael\", Anna sagt „ich bin Anna\". "
                "In der Tabelle steht die Fassung der ersten Stimme.*\n")
    print(f"\nVerzeichnis: {os.path.join(ziel, 'VERZEICHNIS.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
