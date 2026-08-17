#!/usr/bin/env python3
"""DialOS: waehlt das Ausgabegeraet - Bluetooth-Lautsprecher, sonst Laptop.

Stephans Festlegung vom 2026-08-17: Eingabe immer das eingebaute
Mikrofon, Ausgabe der Bluetooth-Lautsprecher solange er aktiv ist, sonst
die eingebauten Lautsprecher. Wird der Lautsprecher mitten in der
Sitzung eingeschaltet, wandert der Ton sofort dorthin - MIT Ansage, damit
der Nutzer den Wechsel mitbekommt.

WARUM ES DIESEN DIENST GIBT, obwohl PipeWire von sich aus das neueste
Geraet zur Vorgabe macht: Weil "vorhanden" und "spielt tatsaechlich ab"
zwei verschiedene Dinge sind. Am 2026-08-17 hat genau diese Verwechslung
die komplette Tonausgabe von DialOS lahmgelegt:

  - BlueZ meldete "Connected: yes", Akku 100 %.
  - Die Senke stand in "pactl list short sinks" und zeigte RUNNING.
  - Ein Testton lief hinein, wurde angenommen - und nie abgespielt.
    "Latency: 0 usec", der Strom stand fuer immer.

Ein blinder Nutzer haette ein totes Geraet vor sich gehabt: kein Ton,
keine Fehlermeldung, nur Ansagen, die sich stapeln. Deshalb fragt dieser
Dienst KEINE Zustandsmeldung ab, sondern probiert es aus - er schickt
einen kurzen stillen Ton hin und schaut, ob der Aufruf durchlaeuft. Nur
was wirklich abspielt, wird Vorgabe.

Stille als Testton ist Absicht: Sie prueft genau das, worauf es ankommt
(laeuft der Strom durch?), ohne dass der Nutzer bei jedem Ereignis ein
Piepen hoert.

BEIM ANMELDEN WIRD NICHT ANGESAGT. Auch das ist eine Lehre vom
2026-08-17: Die Desktop-Wiederherstellung hat beim Anmelden gesprochen
und ist damit der Start-Ansage ins Wort gefallen. Wer sich gerade
anmeldet, hat nichts umgeschaltet - es gibt also nichts zu melden.
Angesagt wird nur ein Wechsel WAEHREND der Sitzung.

Aufruf: laeuft ueber /etc/xdg/autostart/dialos-ton-ausgabe.desktop
automatisch in jeder Sitzung. Von Hand zum Testen einfach starten
("--debug" zeigt jede Entscheidung), beenden mit Strg+C.
"""

import os
import re
import subprocess
import sys
import time
import wave

DEBUG = "--debug" in sys.argv
SAY = "/usr/local/bin/dialos-say.py"

# Der stille Testton. 150 ms reichen: Laeuft der Strom, ist paplay in
# deutlich unter einer Sekunde fertig; haengt die Senke, laeuft es ins
# Zeitlimit.
TESTTON = "/run/user/%d/dialos-ton-test.wav" % os.getuid()
TESTTON_S = 0.15
ZEITLIMIT_S = 3.0

# Bei einem Bluetooth-Verbindungsaufbau feuert PipeWire mehrere
# Ereignisse hintereinander. Ohne diese Beruhigungszeit wuerde die
# Ansage mehrfach kommen.
BERUHIGEN_S = 1.5

ANSAGE_BLUETOOTH = "Ton über Lautsprecher."
ANSAGE_INTERN = "Ton über Laptop."


def melde(text):
    if DEBUG:
        print(text, flush=True)


def sprich(text):
    try:
        subprocess.run([SAY, text], capture_output=True, timeout=60)
    except Exception:
        pass


def testton_anlegen():
    """Legt eine kurze stille WAV-Datei an - einmal pro Sitzung."""
    if os.path.exists(TESTTON):
        return
    with wave.open(TESTTON, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00\x00" * int(48000 * TESTTON_S))


def senken():
    """Alle Ausgabegeraete als Liste von Namen, in der Reihenfolge von pactl."""
    try:
        roh = subprocess.run(["pactl", "list", "short", "sinks"],
                             capture_output=True, timeout=10)
    except Exception:
        return []
    namen = []
    for zeile in roh.stdout.decode(errors="replace").splitlines():
        teile = zeile.split("\t")
        if len(teile) >= 2:
            namen.append(teile[1])
    return namen


def spielt_wirklich(senke):
    """Der einzige verlaessliche Test: kurz hinspielen und schauen.

    Kein Rueckgriff auf Zustandsmeldungen - siehe Kopf der Datei. Ein
    Zeitlimit ist Pflicht, weil eine haengende Senke den Aufruf sonst
    NIE zurueckkehren laesst.
    """
    try:
        p = subprocess.run(["paplay", "-d", senke, TESTTON],
                           capture_output=True, timeout=ZEITLIMIT_S)
    except subprocess.TimeoutExpired:
        melde(f"  {senke}: haengt (Zeitlimit {ZEITLIMIT_S} s)")
        return False
    except Exception as e:
        melde(f"  {senke}: Fehler ({e})")
        return False
    if p.returncode != 0:
        melde(f"  {senke}: paplay endet mit {p.returncode}")
        return False
    return True


# Die letzte Wahl, die DIESER Dienst getroffen hat. Bewusst nicht die
# Vorgabe-Senke des Systems (Fehler vom 2026-08-17): WirePlumber stellt
# beim Verschwinden eines Geraets selbst um, und zwar BEVOR dieser Dienst
# hinschaut. Der Vergleich mit dem Systemzustand ergab deshalb immer
# "nichts geaendert", und die Ansage blieb aus - obwohl der Ton sehr wohl
# gewandert war. Belegt im Protokoll: bei "remove" und bei "new" stand
# jeweils "Vorgabe bleibt".
letzte_wahl = None


def waehle(ansagen):
    """Setzt die Vorgabe-Senke und gibt ihren Namen zurueck.

    Bluetooth hat Vorrang, aber nur wenn es den Test besteht. Sonst das
    eingebaute Geraet.
    """
    global letzte_wahl
    alle = senken()
    bluetooth = [s for s in alle if s.startswith("bluez_output.")]
    # Erst das eingebaute Geraet am PCI-Bus, dann als letzte Rueckfall-
    # ebene alles, was nicht Bluetooth ist (ein anderer Laptop koennte
    # seine Lautsprecher anders anbinden).
    intern = ([s for s in alle if re.match(r"alsa_output\.pci-", s)]
              + [s for s in alle if not s.startswith("bluez_output.")])

    ziel = None
    for kandidat in bluetooth:
        if spielt_wirklich(kandidat):
            ziel = kandidat
            break
    if ziel is None:
        for kandidat in intern:
            if spielt_wirklich(kandidat):
                ziel = kandidat
                break
    if ziel is None:
        # Weder Bluetooth noch eingebaut - dann ist etwas grundlegend
        # kaputt, und eine Ansage kaeme ohnehin nicht an. Nichts tun ist
        # besser als eine Vorgabe zu setzen, die nicht spielt.
        melde("  kein spielendes Ausgabegeraet gefunden")
        return None

    # Setzen auf jeden Fall - kostet nichts, wenn es schon stimmt, und
    # faengt den Fall ab, dass WirePlumber etwas anderes gewaehlt hat.
    if ziel != vorgabe():
        try:
            subprocess.run(["pactl", "set-default-sink", ziel],
                           capture_output=True, timeout=10)
        except Exception:
            pass

    geaendert = (ziel != letzte_wahl)
    melde(f"  Ausgabe: {letzte_wahl} -> {ziel}" if geaendert
          else f"  Ausgabe bleibt: {ziel}")
    letzte_wahl = ziel
    if geaendert and ansagen:
        sprich(ANSAGE_BLUETOOTH if ziel.startswith("bluez_output.")
               else ANSAGE_INTERN)
    return ziel


def vorgabe():
    try:
        roh = subprocess.run(["pactl", "get-default-sink"],
                             capture_output=True, timeout=10)
        return roh.stdout.decode(errors="replace").strip()
    except Exception:
        return ""


def main():
    testton_anlegen()

    # Erste Wahl STUMM - beim Anmelden hat niemand etwas umgeschaltet.
    melde("Erste Wahl beim Anmelden (ohne Ansage):")
    waehle(ansagen=False)

    # Danach auf Ereignisse warten. "pactl subscribe" schlaeft, bis sich
    # etwas aendert - kein Nachfragen im Sekundentakt, das waere bei
    # einem Dienst, der die ganze Sitzung laeuft, unnoetige Akkulast.
    while True:
        try:
            p = subprocess.Popen(["pactl", "subscribe"],
                                 stdout=subprocess.PIPE, text=True)
        except Exception:
            time.sleep(5)
            continue
        try:
            letzte = 0.0
            for zeile in p.stdout:
                # NUR Geraete-Ereignisse, nicht "sink-input": Der eigene
                # Testton ist selbst ein sink-input. Mit einem Filter auf
                # "sink" haette jeder Testton den naechsten ausgeloest -
                # eine Endlosschleife, die den Akku leerdreht.
                if " on sink #" not in zeile:
                    continue
                if time.time() - letzte < BERUHIGEN_S:
                    continue
                # Kurz warten: Ein Bluetooth-Verbindungsaufbau ist beim
                # ersten Ereignis noch nicht fertig, das Profil wechselt
                # danach noch.
                time.sleep(BERUHIGEN_S)
                melde(f"Ereignis: {zeile.strip()}")
                waehle(ansagen=True)
                letzte = time.time()
        except Exception:
            pass
        finally:
            try:
                p.terminate()
            except Exception:
                pass
        # pactl beendet sich, wenn PipeWire neu startet - dann neu
        # aufsetzen statt den Dienst sterben zu lassen.
        time.sleep(2)


if __name__ == "__main__":
    main()
