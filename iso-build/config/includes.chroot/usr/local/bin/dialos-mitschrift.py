#!/usr/bin/env python3
"""DialOS: Mitschrift - was gerade passiert, fuer sehende Zuschauer.

Stephans Wunsch vom 2026-08-19: ein Fenster, das dokumentiert, was die
Sprachsteuerung tut. Fuer einen sehenden Helfer, fuer Vorfuehrungen, und um
einem blinden Nutzer am Telefon sagen zu koennen, was das Geraet gerade
gehoert hat.

EINMAL OEFFNEN, STEHEN LASSEN (Stephans Entscheidung). Kein Fenster, das bei
jedem Befehl in den Vordergrund springt - das wuerde beim Diktieren stoeren
und den Fokus stehlen, und wer diktiert, hat den Bildschirm ohnehin nicht im
Blick.

WARUM EIN FILTER UND KEIN "tail -f": Das Befehlsprotokoll bestand am
2026-08-19 aus 4132 Pegel-Zeilen gegen 13 echte. Ein rohes tail waere
unlesbar. Dieses Skript wirft die Pegelanzeige weg und uebersetzt die
Protokollzeilen in Saetze, die auch jemand versteht, der den Quelltext nicht
kennt.

VIER QUELLEN, EINE ZEITACHSE. Befehlsdienst, Diktat, Auskunft und Notizen
schreiben getrennte Protokolle - hier laufen sie zusammen und werden nach
Uhrzeit gemischt. Genau dieses Zusammenfuehren hat am 2026-08-18 den Beweis
gebracht, dass sich Diktat und Befehlserkennung nicht ins Gehege kommen; von
Hand war es muehsam.

Aufruf:  dialos-mitschrift.py            (folgt laufend)
         dialos-mitschrift.py --alles    (zeigt auch, was vorher schon da war)
"""

import os
import re
import sys
import time

HEIM = os.path.expanduser("~")
QUELLEN = {
    "Sprache":  os.path.join(HEIM, "dialos-sprachbefehl.log"),
    "Diktat":   os.path.join(HEIM, "dialos-diktat.log"),
    "Auskunft": os.path.join(HEIM, "dialos-auskunft.log"),
    "Notiz":    os.path.join(HEIM, "dialos-notiz.log"),
}

# Zeilen, die niemanden interessieren. Die Pegelanzeige ist eine laufende
# Messung fuers Entwickeln, keine Aussage darueber, was passiert.
VERWERFEN = re.compile(r'^\s*(Pegel\s|$)')

# Uebersetzungen. Links steht, was im Protokoll steht, rechts, was ein
# Zuschauer lesen soll - in dieser Reihenfolge geprueft.
UEBERSETZUNG = [
    (re.compile(r"erkannt: '(.+)'"),                    "gehört: \u201e{}\u201c"),
    (re.compile(r"erkannt:\s+'(.+)'"),                  "diktiert: \u201e{}\u201c"),
    (re.compile(r"geschrieben:\s+'(.+)'"),              "geschrieben: \u201e{}\u201c"),
    (re.compile(r"Diktat gestartet fuer Notiz '(.+)'"), "Diktat begonnen für \u201e{}\u201c"),
    (re.compile(r"Auskunft '(.+)' gestartet"),          "Auskunft: {}"),
    (re.compile(r"Notiz-Aktion '(.+)' fuer '(.+)' gestartet"), "{1}: {0}"),
    (re.compile(r"Schlusssatz erkannt.*?: '(.+)'"),     "Diktat beendet durch \u201e{}\u201c"),
    (re.compile(r"anderer Dienst hoert zu.*"),          "Befehle sind still - ein anderer Dienst hört zu"),
    (re.compile(r"anderer Dienst fertig.*"),            "Befehle hören wieder zu"),
    (re.compile(r"\(Aufnahme nach Sprechpause neu begonnen\)"), "Aufnahme neu begonnen"),
    (re.compile(r"grosses Modell geladen in (.+)"),     "Sprachmodell geladen ({})"),
    (re.compile(r"kleines Modell fuer den Schlusssatz in (.+)"), "Schluss-Erkenner bereit ({})"),
    (re.compile(r"=== Diktat gestartet \((.+?),\s*(.+?)\).*"), "Diktat läuft ({1})"),
    (re.compile(r"=== (uhrzeit|datum) ==="),            "Frage: {}"),
    (re.compile(r"uhrzeit: (.+)"),                      "Antwort: {}"),
    (re.compile(r"datum: (.+)"),                        "Antwort: {}"),
    (re.compile(r"geschrieben nach (.+)"),              "gespeichert in {}"),
    (re.compile(r"\(Schluss-Erkenner: '(.+)' - kein Schluss\)"), "kein Schlusssatz (\u201e{}\u201c)"),
    (re.compile(r"vorlesen: (\d+) Eintraege.*"),        "liest {} Einträge vor"),
    (re.compile(r"geleert: (.+?),.*"),                  "geleert: {}"),
    (re.compile(r"Antwort gehoert: '(.+)'"),            "Antwort gehört: \u201e{}\u201c"),
]

ZEIT = re.compile(r'^(\d\d:\d\d:\d\d)\s+(.*)$')


def uebersetzen(rohtext):
    for muster, form in UEBERSETZUNG:
        m = muster.search(rohtext)
        if m:
            try:
                return form.format(*m.groups())
            except (IndexError, KeyError):
                return form
    return rohtext.strip()


def zeilen_lesen(pfad, stand):
    """Neue Zeilen seit dem letzten Blick. Gibt (Zeilen, neuer Stand)."""
    try:
        groesse = os.path.getsize(pfad)
    except OSError:
        return [], stand
    if groesse < stand:          # Datei wurde geleert - von vorn
        stand = 0
    if groesse == stand:
        return [], stand
    try:
        with open(pfad, encoding="utf-8", errors="replace") as f:
            f.seek(stand)
            roh = f.read()
            return roh.replace("\r", "\n").split("\n"), f.tell()
    except OSError:
        return [], stand


def aufbereiten(quelle, zeile):
    """Eine Protokollzeile zu (Zeit, Quelle, Satz) - oder None zum Verwerfen."""
    if VERWERFEN.match(zeile):
        return None
    m = ZEIT.match(zeile.strip())
    if m:
        zeit, rest = m.group(1), m.group(2)
    else:
        zeit, rest = time.strftime("%H:%M:%S"), zeile.strip()
    if not rest or VERWERFEN.match(rest):
        return None
    return zeit, quelle, uebersetzen(rest)


def ausgeben(eintrag):
    zeit, quelle, satz = eintrag
    print(f"  {zeit}  {quelle:9s} {satz}", flush=True)


def main():
    alles = "--alles" in sys.argv
    breite = 74
    print("=" * breite)
    print("  DialOS - Mitschrift")
    print("  Was die Sprachsteuerung gerade tut. Beenden mit Strg+C.")
    print("=" * breite)

    stand = {}
    for name, pfad in QUELLEN.items():
        try:
            stand[name] = 0 if alles else os.path.getsize(pfad)
        except OSError:
            stand[name] = 0
    if not alles:
        print("  (wartet auf das naechste Ereignis)")
        print()

    try:
        while True:
            # ALLE Quellen einsammeln und dann nach Uhrzeit sortiert
            # ausgeben (Fehler vom 2026-08-19): Quelle fuer Quelle
            # ausgegeben sah die Ausgabe chronologisch aus und war es nicht -
            # erst kam alles vom Befehlsdienst, dann alles vom Diktat. Bei
            # genau dem Zweck, fuer den vier Protokolle zusammengefuehrt
            # werden - zeigen, was GLEICHZEITIG passiert ist -, waere das
            # irrefuehrend.
            gesammelt = []
            for name, pfad in QUELLEN.items():
                neu, stand[name] = zeilen_lesen(pfad, stand[name])
                for z in neu:
                    eintrag = aufbereiten(name, z)
                    if eintrag:
                        gesammelt.append(eintrag)
            for eintrag in sorted(gesammelt, key=lambda e: e[0]):
                ausgeben(eintrag)
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\n  Mitschrift beendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
