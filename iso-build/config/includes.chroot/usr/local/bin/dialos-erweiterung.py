#!/usr/bin/env python3
"""DialOS: Erweiterungen verwalten - einbauen, entfernen, auflisten, pruefen.

Der Entwurf der Schnittstelle steht in docs/erweiterungen.md; hier steht nur,
was der Code tut, und die Gruende, die IM CODE gebraucht werden.

WAS EINE ERWEITERUNG IST: ein Programm, das ohne DialOS nicht laeuft, weil es
auf dessen Grammatik, Stimme und Mikrofon-Uebergabe angewiesen ist. Es meldet
sich mit einer JSON-Datei unter /usr/local/share/dialos/erweiterungen/ an.

DIE KERNREGEL, aus der alles andere folgt: Die Kern-Grammatik waechst pro
Erweiterung um GENAU EINEN SATZ, ihren Startsatz. Alles Weitere erkennt die
Erweiterung selbst, solange sie laeuft. Der Grund ist gemessen - bei 27 Saetzen
standen am 2026-08-22 bereits 382 erlaubte Wortkombinationen ohne Befehl im
Protokoll, und die Zahl waechst nicht linear mit der Satzzahl.

ZWEI PFLICHTPRUEFUNGEN BEIM EINBAUEN, und beide VERWEIGERN statt zu warnen:

  1. Wortschatz: Kennt das Modell jedes Wort? Ein Wort, das es nicht kennt,
     wirft Vosk STILL aus der Grammatik - der Befehl existiert dann nicht, und
     nirgends steht etwas. Am 2026-08-18 bei "loeschen" aufgefallen.
  2. Kollision: Wird der Startsatz in der VOLLSTAENDIGEN Grammatik richtig
     erkannt, und gehen bestehende Saetze durch ihn kaputt? Das zweite ist die
     wichtigere Frage - ein Kandidat, der selbst durchfaellt, kostet nur ihn.

Warnen statt verweigern waere hier wertlos: Eine Warnung beim Einbauen liest
niemand wieder, und der Fehler zeigt sich erst, wenn der Nutzer allein mit dem
Geraet ist.

Aufruf:
    dialos-erweiterung.py liste
    dialos-erweiterung.py pruefen  PFAD.json     nur pruefen, nichts aendern
    dialos-erweiterung.py einbauen PFAD.json
    dialos-erweiterung.py entfernen NAME
"""

import json
import os
import shutil
import subprocess
import sys

ORDNER = "/usr/local/share/dialos/erweiterungen"
PRUEFER = "/usr/local/bin/dialos-grammatik-pruefen.py"

# Pflichtfelder eines Manifests. Fehlt eines, wird nicht geraten - eine
# Erweiterung, die halb angemeldet ist, ist schlimmer als eine, die fehlt:
# Der Nutzer bekaeme einen Satz angesagt, der nichts tut.
PFLICHT = ("name", "version", "braucht_dialos", "startsaetze", "befehl",
           "beschreibung")
ERLAUBT = PFLICHT + ("eigene_grammatik", "braucht_mikrofon")


def lesen(pfad):
    """Ein Manifest laden und auf Form pruefen. Gibt (manifest, fehler) zurueck."""
    try:
        with open(pfad, encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError) as fehler:
        return None, f"nicht lesbar: {fehler}"

    if not isinstance(m, dict):
        return None, "kein JSON-Objekt"
    fehlt = [f for f in PFLICHT if f not in m]
    if fehlt:
        return None, f"Pflichtfelder fehlen: {', '.join(fehlt)}"
    unbekannt = [f for f in m if f not in ERLAUBT]
    if unbekannt:
        # Nicht durchwinken: Ein Tippfehler im Feldnamen waere sonst ein Feld,
        # das stillschweigend ignoriert wird - etwa "startsaetzte".
        return None, f"unbekannte Felder: {', '.join(unbekannt)}"
    if not isinstance(m["startsaetze"], list) or not m["startsaetze"]:
        return None, "startsaetze muss eine nicht leere Liste sein"
    if any(not isinstance(s, str) or not s.strip() for s in m["startsaetze"]):
        return None, "startsaetze enthaelt Leeres oder Nicht-Text"
    if not os.path.isabs(m["befehl"]):
        return None, f"befehl muss ein absoluter Pfad sein: {m['befehl']!r}"

    # Startsaetze KLEIN und ohne doppelte Leerzeichen - so kommen sie auch aus
    # Vosk zurueck. Ein Satz mit grossem Anfangsbuchstaben waere in der
    # Grammatik gueltig und wuerde trotzdem nie zugeordnet.
    for s in m["startsaetze"]:
        if s != " ".join(s.lower().split()):
            return None, (f"startsatz {s!r} muss kleingeschrieben sein und "
                          "einfache Leerzeichen haben")
    return m, None


def alle():
    """Alle eingebauten Manifeste, nach Name sortiert.

    Fehlerhafte Dateien werden UEBERSPRUNGEN und gemeldet, nicht verschwiegen:
    Ein kaputtes Manifest darf die Sprachsteuerung nicht mitreissen - sie ist
    das Einzige, womit der Nutzer das Geraet noch erreicht.
    """
    gefunden, kaputt = [], []
    if not os.path.isdir(ORDNER):
        return gefunden, kaputt
    for name in sorted(os.listdir(ORDNER)):
        if not name.endswith(".json"):
            continue
        pfad = os.path.join(ORDNER, name)
        m, fehler = lesen(pfad)
        if m:
            m["_datei"] = pfad
            gefunden.append(m)
        else:
            kaputt.append((pfad, fehler))
    return gefunden, kaputt


def startsaetze():
    """Alle Startsaetze aller Erweiterungen - das, was in die Kern-Grammatik geht."""
    gefunden, _ = alle()
    return [s for m in gefunden for s in m["startsaetze"]]


def satz_zu_erweiterung():
    """Startsatz -> Manifest. Die Zuordnung, die der Befehlsdienst braucht."""
    gefunden, _ = alle()
    return {s: m for m in gefunden for s in m["startsaetze"]}


def pruefen(m, gegen_bestand=True):
    """Beide Pflichtpruefungen. Gibt eine Liste von Fehlertexten zurueck.

    Die eigentliche Arbeit macht dialos-grammatik-pruefen.py - dasselbe
    Werkzeug, mit dem auch die Kernbefehle geprueft werden. Eine zweite
    Pruefroutine hier liefe beim naechsten Umbau auseinander, und zwar
    unbemerkt, weil sie fuer sich genommen richtig aussieht.
    """
    fehler = []

    schon = satz_zu_erweiterung()
    for s in m["startsaetze"]:
        if s in schon and schon[s].get("name") != m.get("name"):
            fehler.append(f"Startsatz {s!r} gehoert schon zu "
                          f"{schon[s]['name']!r}")

    if not os.path.exists(m["befehl"]):
        fehler.append(f"Programm fehlt: {m['befehl']}")
    elif not os.access(m["befehl"], os.X_OK):
        fehler.append(f"Programm nicht ausfuehrbar: {m['befehl']}")

    if fehler or not gegen_bestand:
        return fehler

    if not os.access(PRUEFER, os.X_OK):
        fehler.append(f"Pruefwerkzeug fehlt: {PRUEFER} - "
                      "Wortschatz und Kollisionen UNGEPRUEFT")
        return fehler

    befehl = [PRUEFER]
    for s in m["startsaetze"]:
        befehl += ["--neu", s]
    print(f"  Pruefe gegen die vollstaendige Grammatik: {' '.join(befehl)}")
    print("  (Piper spricht, Vosk hoert - das dauert einen Moment.)")
    try:
        r = subprocess.run(befehl, timeout=1800)
    except (OSError, subprocess.TimeoutExpired) as f:
        fehler.append(f"Pruefung liess sich nicht ausfuehren: {f}")
        return fehler
    if r.returncode != 0:
        fehler.append("Die Grammatik-Pruefung ist fehlgeschlagen - Ausgabe oben. "
                      "NICHT eingebaut.")
    return fehler


def befehl_liste():
    gefunden, kaputt = alle()
    if not gefunden and not kaputt:
        print(f"Keine Erweiterungen in {ORDNER}")
        return 0
    for m in gefunden:
        marke = " (kein Mikrofon)" if not m.get("braucht_mikrofon") else ""
        print(f"{m['name']} {m['version']}{marke}")
        print(f"    {m['beschreibung']}")
        for s in m["startsaetze"]:
            print(f"    Startsatz: {s!r}")
        print(f"    Programm:  {m['befehl']}")
        eigen = m.get("eigene_grammatik") or []
        if eigen:
            print(f"    Eigene Grammatik ({len(eigen)}): {', '.join(eigen)}")
    for pfad, fehler in kaputt:
        print(f"KAPUTT  {pfad}: {fehler}", file=sys.stderr)
    return 1 if kaputt else 0


def befehl_pruefen(pfad, einbauen=False):
    m, fehler = lesen(pfad)
    if fehler:
        print(f"{pfad}: {fehler}", file=sys.stderr)
        return 1
    print(f"{m['name']} {m['version']} - {m['beschreibung']}")
    for s in m["startsaetze"]:
        print(f"  Startsatz: {s!r}")

    probleme = pruefen(m)
    if probleme:
        print()
        for p in probleme:
            print(f"ABGELEHNT: {p}", file=sys.stderr)
        return 1

    if not einbauen:
        print("\nGeprueft und in Ordnung - noch nicht eingebaut "
              "(dafuer: einbauen).")
        return 0

    os.makedirs(ORDNER, exist_ok=True)
    ziel = os.path.join(ORDNER, os.path.basename(pfad))
    m.pop("_datei", None)
    shutil.copyfile(pfad, ziel)
    os.chmod(ziel, 0o644)
    print(f"\nEingebaut: {ziel}")
    print("Der Befehlsdienst liest Manifeste beim Start - er muss neu starten:")
    print("    pkill -f 'python3 /usr/local/bin/dialos-sprachbefehl-desktop.py'")
    print("    setsid /usr/local/bin/dialos-sprachbefehl-desktop.py "
          ">/dev/null 2>&1 &")
    return 0


def befehl_entfernen(name):
    gefunden, _ = alle()
    treffer = [m for m in gefunden if m["name"] == name]
    if not treffer:
        print(f"Keine Erweiterung namens {name!r}. "
              f"Vorhanden: {', '.join(m['name'] for m in gefunden) or 'keine'}",
              file=sys.stderr)
        return 1
    for m in treffer:
        os.remove(m["_datei"])
        print(f"Entfernt: {m['_datei']}")
    print("Das PROGRAMM bleibt liegen - entfernt wird nur die Anmeldung.")
    print("Der Befehlsdienst muss neu starten, damit der Satz verschwindet.")
    return 0


def main():
    was = sys.argv[1] if len(sys.argv) > 1 else "liste"
    if was == "liste":
        return befehl_liste()
    if was in ("pruefen", "einbauen") and len(sys.argv) > 2:
        return befehl_pruefen(sys.argv[2], einbauen=(was == "einbauen"))
    if was == "entfernen" and len(sys.argv) > 2:
        return befehl_entfernen(sys.argv[2])
    print(__doc__.rstrip().rsplit("Aufruf:", 1)[-1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
