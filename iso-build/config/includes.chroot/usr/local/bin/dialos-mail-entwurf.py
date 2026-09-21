#!/usr/bin/env python3
"""Legt eine diktierte Mail als ENTWURF in Thunderbird ab - gesendet wird nie.

Stephans Entscheidung vom 2026-09-18, aus drei Vorschlaegen: "Diktieren, dann
Entwurf". Die Antwort entsteht per Sprache, landet in Thunderbirds Entwuerfen
und geht erst hinaus, wenn ein Mensch sie absendet. Damit kann ein
missverstandenes Wort nichts anrichten, was sich nicht zurueckholen laesst -
dieselbe Ueberlegung wie beim Drucken mit Rueckfrage, nur ernster: Eine
abgeschickte Mail ist aus der Welt.

SEIT DEM 2026-09-21 FRAGT DIALOS THUNDERBIRD, STATT IN SEINE DATEIEN ZU
SCHREIBEN. Der Entwurf geht ueber die Bruecke (dialos-thunderbird-bruecke.py)
an die MailExtension, und Thunderbird legt ihn selbst ab - im Entwurfsordner
des KONTOS, der zum Server hochgeladen wird. Am Geraet gemessen und belegt.

WARUM DER ALTE WEG WEG IST: Vorher schrieb DialOS den Entwurf selbst in
"Local Folders/Drafts". Das ging nur bei geschlossenem Thunderbird, landete
nie beim Server - und kostete zwei Fehler, die niemand sehen konnte: LF statt
CR LF (Thunderbird zeigte den Ordner leer) und "X-Mozilla-Status: 0008", was
nicht "Entwurf" heisst, sondern GELOESCHT. Beides ist gegenstandslos, sobald
das Programm gefragt wird, dem die Dateien gehoeren.

IST THUNDERBIRD ZU, WIRD VORGEMERKT (Stephans Wahl vom 2026-09-21): Die
Bruecke arbeitet die Warteschlange ab, sobald Thunderbird startet. Der Entwurf
landet dann ebenfalls im Konto-Ordner - nur spaeter. Der Nutzer hoert beides,
das Ablegen wie das Vormerken.

Aufruf:
  dialos-mail-entwurf.py anlegen --an ADRESSE --betreff TEXT --text DATEI
                                 [--bezug MESSAGE-ID] [--zitat DATEI]
  dialos-mail-entwurf.py nachholen      Warteschlange abarbeiten
  dialos-mail-entwurf.py zeigen         Was in den Entwuerfen liegt
"""

import importlib.util
import json
import os
import subprocess
import sys
import time

HEIM = os.path.expanduser("~")
WARTESCHLANGE = os.path.join(HEIM, ".config", "dialos", "mail-entwuerfe.json")
PROTOKOLL = os.path.join(HEIM, ".log", "dialos-mail-entwurf.log")
PERSOENLICHE_DATEN_SKRIPT = "/usr/local/bin/dialos-persoenliche-daten.py"


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass








def _vormerken(daten):
    os.makedirs(os.path.dirname(WARTESCHLANGE), exist_ok=True)
    liste = []
    if os.path.isfile(WARTESCHLANGE):
        try:
            with open(WARTESCHLANGE, encoding="utf-8") as f:
                liste = json.load(f)
        except (OSError, ValueError):
            liste = []
    liste.append(daten)
    with open(WARTESCHLANGE, "w", encoding="utf-8") as f:
        json.dump(liste, f, ensure_ascii=False, indent=1)


# WAS HIER BIS ZUM 2026-09-21 STAND, UND WARUM ES WEG IST: profil(),
# entwurfsordner(), thunderbird_laeuft(), nachricht_bauen() und
# als_mbox_eintrag() - der ganze Weg, der eine Nachricht selbst zusammenbaute
# und an "Local Folders/Drafts" anhaengte. Er ist nicht auskommentiert, sondern
# geloescht: Ein zweiter Schreibweg, der noch dasteht, wird irgendwann wieder
# benutzt, und dann sind die beiden Fehler vom 2026-09-18 zurueck (LF statt
# CR LF, und "X-Mozilla-Status: 0008" heisst GELOESCHT). Ueber die Git-Historie
# ist er erreichbar, falls jemand nachsehen will, wie es aussah.

BRUECKE_SKRIPT = "/usr/local/bin/dialos-thunderbird-bruecke.py"


def bruecke():
    """Das Bruecken-Modul laden. None, wenn es nicht da ist."""
    try:
        spec = importlib.util.spec_from_file_location("dialos_bruecke", BRUECKE_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"Brücke nicht ladbar: {fehler}")
        return None


def thunderbird_erreichbar():
    """Laeuft Thunderbird MIT Erweiterung? Nur dann kann etwas abgelegt werden.

    GEFRAGT WIRD MIT "hallo", NICHT MIT EINEM ENTWURF. Die erste Fassung hat
    hier einen leeren Entwurf losgeschickt, um zu sehen, ob jemand antwortet -
    und haette bei jedem Anmelden einen leeren Entwurf im Postfach hinterlassen.
    Eine Probe darf nichts anlegen.
    """
    modul = bruecke()
    if modul is None:
        return False
    return bool(modul.fragen({"befehl": "hallo"}, zeitgrenze=5.0).get("ok"))


def ueber_bruecke(an, betreff, text, bezug=None, zitat=""):
    """Thunderbird bitten, den Entwurf abzulegen. Antwort-dict."""
    modul = bruecke()
    if modul is None:
        return {"ok": False, "fehler": "Brücke nicht ladbar"}
    koerper = text.strip()
    if zitat.strip():
        koerper += "\n\n" + "\n".join("> " + z for z in zitat.strip().splitlines())
    return modul.fragen({"befehl": "entwurf", "an": an, "betreff": betreff,
                         "text": koerper, "bezug": bezug})


def ablegen(an, betreff, text, bezug=None, zitat=""):
    """Entwurf ablegen. True: in Thunderbird, False: vorgemerkt."""
    antwort = ueber_bruecke(an, betreff, text, bezug, zitat)
    if antwort.get("ok"):
        melde(f"Entwurf über die Brücke abgelegt: {betreff!r} an {an}")
        return True
    melde(f"Brücke nicht nutzbar ({antwort.get('fehler')}) - wird vorgemerkt")
    _vormerken({"an": an, "betreff": betreff, "text": text, "bezug": bezug,
                "zitat": zitat})
    return False


def nachholen():
    """Was vorgemerkt wurde, jetzt eintragen - beim Anmelden aufgerufen."""
    if not os.path.isfile(WARTESCHLANGE):
        return 0
    try:
        with open(WARTESCHLANGE, encoding="utf-8") as f:
            liste = json.load(f)
    except (OSError, ValueError) as fehler:
        melde(f"Warteschlange nicht lesbar: {fehler}")
        return 0
    # NACHGEHOLT WIRD NUR, WENN DIE BRUECKE DA IST - also wenn Thunderbird
    # laeuft. Genau umgekehrt wie frueher: Damals war ein laufender Thunderbird
    # das Hindernis, jetzt ist er die Voraussetzung.
    if not thunderbird_erreichbar():
        melde("Nachholen verschoben - Thunderbird ist zu")
        return 0
    geschafft = 0
    for daten in liste:
        if ablegen(daten.get("an", ""), daten.get("betreff", ""),
                   daten.get("text", ""), daten.get("bezug"),
                   daten.get("zitat", "")):
            geschafft += 1
    if geschafft == len(liste):
        try:
            os.unlink(WARTESCHLANGE)
        except OSError:
            pass
    return geschafft


def main():
    befehl = sys.argv[1] if len(sys.argv) > 1 else "zeigen"
    if befehl == "nachholen":
        anzahl = nachholen()
        if anzahl:
            print(f"{anzahl} Entwurf/Entwuerfe eingetragen")
        return 0
    if befehl == "zeigen":
        print("Thunderbird erreichbar: "
              + ("ja" if thunderbird_erreichbar() else "nein (dann wird vorgemerkt)"))
        if os.path.isfile(WARTESCHLANGE):
            with open(WARTESCHLANGE, encoding="utf-8") as f:
                print(f"Vorgemerkt: {len(json.load(f))}")
        return 0
    if befehl != "anlegen":
        print(__doc__)
        return 2

    werte = {}
    argumente = sys.argv[2:]
    for schalter in ("--an", "--betreff", "--text", "--bezug", "--zitat"):
        if schalter in argumente:
            i = argumente.index(schalter)
            werte[schalter] = argumente[i + 1]
    if "--an" not in werte:
        print("Ohne --an geht es nicht.", file=sys.stderr)
        return 2
    text = ""
    if "--text" in werte:
        with open(werte["--text"], encoding="utf-8") as f:
            text = f.read()
    zitat = ""
    if "--zitat" in werte:
        with open(werte["--zitat"], encoding="utf-8") as f:
            zitat = f.read()
    sofort = ablegen(werte["--an"], werte.get("--betreff", "(ohne Betreff)"),
                     text, werte.get("--bezug"), zitat)
    print("abgelegt" if sofort else "vorgemerkt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
