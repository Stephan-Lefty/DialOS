#!/usr/bin/env python3
"""Laesst LanguageTool einmal warmlaufen, direkt nach dem Start des Dienstes.

WARUM (gemessen 2026-08-19): Die deutschen Regeln laden nicht beim Serverstart,
sondern bei der ersten PRUEFANFRAGE. Gemessen nach einem Neustart des Dienstes:

    /v2/languages antwortet nach   1,3 s   <- das prueft lt_lebt() als "laeuft"
    erste /v2/check-Anfrage        9,2 s   <- hier laden die Regeln
    zweite /v2/check-Anfrage       1,0 s

Die Zeitgrenze im Diktat liegt bei 10,0 s. Die erste Korrektur jeder Sitzung
war damit ein Muenzwurf mit 0,8 s Luft - und am 2026-08-19 um 10:03:03 hat sie
verloren: "(LanguageTool nicht erreichbar: timed out)", der Einkaufszettel wurde
klein geschrieben.

Die Unit dokumentierte die 8,8 s des ersten Aufrufs schon seit dem 2026-08-18
und zog daraus den Schluss "dann eben ein Dauerdienst". Der Schluss war
unvollstaendig: Ein Dauerdienst verschiebt die Ladezeit nur auf die erste
Anfrage, er beseitigt sie nicht. Genau das erledigt dieses Skript - die 9 s
fallen einmal beim Anmelden an, wo niemand darauf wartet.

Laeuft als ExecStartPost der Unit, mit vorangestelltem "-": Scheitert das
Warmlaufen, gilt der Dienst trotzdem als gestartet. Ein nicht warmgelaufener
Dienst ist immer noch besser als keiner, und "Restart=on-failure" duerfte
deswegen nicht in eine Schleife geraten.
"""

import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ADRESSE = "http://127.0.0.1:8081/v2/check"
# Warten, bis der Server ueberhaupt Verbindungen annimmt (gemessen 1,3 s).
WARTEN_S = 60.0
# Fuer die Anfrage selbst reichlich Zeit - sie DARF ja lange dauern, das ist
# der Zweck. 120 s ist die Reissleine gegen ein haengendes Java.
ANFRAGE_S = 120.0
# Ein Satz mit Substantiv und Verb, damit die deutschen Regeln wirklich
# angefasst werden. Ein einzelnes Wort wuerde weniger laden.
TEXT = "Hiermit laeuft die Schreibhilfe warm."


def main():
    daten = urllib.parse.urlencode({"language": "de-DE", "text": TEXT}).encode()
    frist = time.time() + WARTEN_S
    t0 = time.time()
    while time.time() < frist:
        try:
            with urllib.request.urlopen(ADRESSE, daten, timeout=ANFRAGE_S) as a:
                a.read()
            print(f"Schreibhilfe warmgelaufen in {time.time()-t0:.1f} s")
            return 0
        except urllib.error.URLError:
            time.sleep(1.0)          # Server nimmt noch nicht an
        except Exception as fehler:
            print(f"Warmlaufen fehlgeschlagen: {fehler}", file=sys.stderr)
            return 1
    print(f"Schreibhilfe antwortete nicht innerhalb von {WARTEN_S:.0f} s",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
