#!/usr/bin/env python3
"""Misst, wie gut das kleine Modell BUCHSTABEN von Stephans Stimme versteht.

Anlass (2026-09-18): Stephan buchstabierte "kontakt@dialos.org" fuer eine
Weiterleitung, und es kam "komteakte@teialos.or" an - Nordpol als Martha, Dora
als Theodor, das Gustav am Ende verschluckt. Seine Frage danach: "Buchstabieren
nur mit den Buchstaben, ist das nicht sinnvoller?"

DIE VORHANDENE MESSUNG WIDERSPRICHT DEM - ABER SIE IST MIT PIPER GEMACHT.
Am 2026-09-17 traf das kleine Modell das Buchstabieralphabet 26 von 26, die
Buchstabennamen ("be", "ce", "de") nur 15 von 26. Gesprochen hat das aber
Piper: deutlicher als ein Mensch, gleichmaessig laut, immer gleich weit vom
Mikrofon. Eine Entscheidung ueber die Bedienung gehoert an die Stimme, die sie
spaeter benutzt. Deshalb dieses Werkzeug.

WAS ES MISST: Es sagt ein Wort an, nimmt die Wiederholung auf und laesst das
kleine Modell mit GENAU DER Grammatik hoeren, die auch beim Buchstabieren
gilt. Verglichen wird Wort fuer Wort; am Ende steht, welche Woerter bei DIESER
Stimme haengen und wie oft.

DREI DURCHGAENGE MOEGLICH:
  --alphabet   Anton, Berta, Caesar ...            (Vorgabe)
  --namen      a, be, ce, de ...                    die Buchstabennamen
  --beides     beide Listen in EINER Grammatik      - so wuerde es laufen,
               wenn DialOS beides zulaesst; hier zeigt sich, ob die Namen die
               Alphabetwoerter mit herunterziehen.

DIE AUFNAHMEN BLEIBEN AUF DER EXTERNEN PLATTE (Regel seit 2026-09-15, Stephans
Zustimmung fuer seine Stimme gilt fuer Messungen, nicht fuer das Repo):
erkenner-vergleich/buchstaben/. So laesst sich ein Ergebnis spaeter nachhoeren,
statt es neu sprechen zu muessen.

Aufruf:
  scripts/dialos-buchstaben-messen.py [--alphabet|--namen|--beides]
                                      [--mal N] [--ohne-aufnahme]
  scripts/dialos-buchstaben-messen.py --auswerten DATEI.json
"""

import json
import os
import subprocess
import sys
import time
import wave

SAY = "/usr/local/bin/dialos-say.py"
DIKTAT = "/usr/local/bin/dialos-diktat.py"
MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
QUELLE = "dialos_mikrofon_ohne_echo"
ABTASTRATE = 16000
BLOCK = 4000
PEGEL_SCHWELLE = 150.0
RUHE_ENDE_S = 1.0
ZEITGRENZE_S = 8.0

MESSORDNER = ("/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich/"
              "buchstaben")

# Die Buchstabennamen, wie man sie spricht. "ha" und "ka" stehen mit Absicht so
# da - "h" allein waere kein Wort fuer den Erkenner.
NAMEN = {
    "a": "a", "be": "b", "ce": "c", "de": "d", "e": "e", "ef": "f", "ge": "g",
    "ha": "h", "i": "i", "jot": "j", "ka": "k", "el": "l", "em": "m", "en": "n",
    "o": "o", "pe": "p", "ku": "q", "er": "r", "es": "s", "te": "t", "u": "u",
    "vau": "v", "we": "w", "ix": "x", "ypsilon": "y", "zett": "z",
}


def marke_pfad(name):
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


MARKE = marke_pfad("dialos-diktat-aktiv")


def sprich(text):
    try:
        subprocess.run([SAY, text], capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        print(f"[Ansage] {text}")


def diktat_modul():
    """Die Buchstabentabellen aus dem Diktat - geholt, nicht abgeschrieben."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("dialos_diktat", DIKTAT)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def pegel(block):
    import array
    if len(block) < 2:
        return 0.0
    werte = array.array("h", block[:len(block) - len(block) % 2])
    return (sum(x * x for x in werte) / len(werte)) ** 0.5 if werte else 0.0


def aufnehmen(prozess):
    """Ein gesprochenes Wort - roh, bis es eine Sekunde still ist."""
    roh = bytearray()
    gesprochen = False
    ruhe = 0.0
    block_s = BLOCK / 2 / ABTASTRATE
    ende = time.time() + ZEITGRENZE_S
    while time.time() < ende:
        block = prozess.stdout.read(BLOCK)
        if not block:
            break
        roh += block
        if pegel(block) >= PEGEL_SCHWELLE:
            gesprochen, ruhe = True, 0.0
        elif gesprochen:
            ruhe += block_s
            if ruhe >= RUHE_ENDE_S:
                break
    return bytes(roh) if gesprochen else b""


def messen(art, wiederholungen, mit_aufnahme):
    import vosk
    vosk.SetLogLevel(-1)
    d = diktat_modul()
    # Die Grammatik ist die aus dem Betrieb: Buchstabieralphabet UND
    # Buchstabennamen stehen dort ohnehin nebeneinander, dazu die Zeichen fuer
    # Mailadressen. Nur "--namen" schraenkt sie ein - dann wird gemessen, wie
    # gut die Namen ohne die Konkurrenz des Alphabets ankommen.
    tabelle = dict(NAMEN) if art == "namen" else dict(d.BUCHSTABEN_HOEREN,
                                                      **d.MAIL_ZEICHEN)
    # GEFRAGT WIRD NACH DEM, WAS DER NUTZER SAGEN SOLL - nicht nach allem, was
    # die Tabelle kennt. Sie enthaelt zu jedem Buchstaben BEIDES (Anton und be),
    # weil beim Buchstabieren beides gilt; eine Messung, die beides abfragt,
    # misst nicht die Frage, um die es geht.
    alphabet = [d.BUCHSTABEN_SPRECHEN[z].lower()
                for z in "abcdefghijklmnopqrstuvwxyzäöü"]
    if art == "namen":
        fragen = list(NAMEN)
    else:
        # Die Zeichen fuer Mailadressen gehoeren dazu: Genau an ihnen haengt der
        # Fall, aus dem die Messung kommt (at, Punkt, Minus, Ziffern).
        fragen = alphabet + [w for w in d.MAIL_ZEICHEN if w != "bindestrich"]
    grammatik = json.dumps(list(tabelle) + ["fertig", "zurück", "abbrechen", "[unk]"],
                           ensure_ascii=False)
    modell = vosk.Model(MODELL_KLEIN)

    os.makedirs(MESSORDNER, exist_ok=True)
    stempel = time.strftime("%Y-%m-%d-%H%M%S")
    ergebnisse = []
    # DIE SPRACHSTEUERUNG MUSS WEGHOEREN (2026-09-18): Wer hier "Otto" und
    # "Punkt" sagt, spricht eine halbe Stunde lang Woerter ins Mikrofon - ohne
    # die Marke haette der Befehlsdienst sie alle mitgehoert. Dieselbe Datei wie
    # beim Diktat und bei der Suche; die PID darin laesst die Wache eine
    # verwaiste Marke erkennen.
    with open(MARKE, "w", encoding="utf-8") as f:
        f.write(f"{os.getpid()} dialos-buchstaben-messen\n")
    prozess = subprocess.Popen(
        ["parec", "-d", QUELLE, "--format=s16le", f"--rate={ABTASTRATE}",
         "--channels=1", "--latency-msec=30"], stdout=subprocess.PIPE)
    try:
        sprich(f"Ich messe jetzt {len(fragen)} Wörter, je {wiederholungen} mal. "
               "Ich sage ein Wort, Du sprichst es nach. Los geht es.")
        for runde in range(1, wiederholungen + 1):
            for wort in fragen:
                sprich(wort)
                roh = aufnehmen(prozess)
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, grammatik)
                erkenner.AcceptWaveform(roh)
                gehoert = json.loads(erkenner.FinalResult()).get("text", "").strip()
                richtig = (gehoert == wort)
                # AUCH DAS ZEICHEN VERGLEICHEN: "Nordpol" statt "en" ist bei
                # gemischter Grammatik kein Fehler - beide meinen N.
                zeichen_soll = tabelle.get(wort, "")
                zeichen_ist = tabelle.get(gehoert.split()[0], "") if gehoert else ""
                ergebnisse.append({"runde": runde, "soll": wort, "gehoert": gehoert,
                                   "zeichen_soll": zeichen_soll,
                                   "zeichen_ist": zeichen_ist,
                                   "richtig": richtig,
                                   "zeichen_richtig": bool(zeichen_soll)
                                   and zeichen_soll == zeichen_ist,
                                   "sekunden": round(len(roh) / 2 / ABTASTRATE, 2)})
                zeichen = "ok " if richtig else ("(" + (zeichen_ist or "-") + ")"
                                                 if ergebnisse[-1]["zeichen_richtig"]
                                                 else "FALSCH")
                print(f"  {runde}. {wort:12s} -> {gehoert or '(nichts)':14s} {zeichen}",
                      flush=True)
                if mit_aufnahme and roh:
                    pfad = os.path.join(MESSORDNER, f"{stempel}-{art}-{runde}-{wort}.wav")
                    with wave.open(pfad, "wb") as w:
                        w.setnchannels(1)
                        w.setsampwidth(2)
                        w.setframerate(ABTASTRATE)
                        w.writeframes(roh)
    finally:
        prozess.terminate()
        try:
            os.unlink(MARKE)
        except OSError:
            pass

    datei = os.path.join(MESSORDNER, f"{stempel}-{art}.json")
    with open(datei, "w", encoding="utf-8") as f:
        json.dump({"art": art, "wiederholungen": wiederholungen,
                   "ergebnisse": ergebnisse}, f, ensure_ascii=False, indent=1)
    auswerten(ergebnisse, art)
    print(f"\nEinzelheiten: {datei}")
    sprich("Die Messung ist fertig.")
    return 0


def auswerten(ergebnisse, art=""):
    gesamt = len(ergebnisse)
    wort_richtig = sum(1 for e in ergebnisse if e["richtig"])
    zeichen_richtig = sum(1 for e in ergebnisse if e["zeichen_richtig"])
    print(f"\n{art or 'Messung'}: {wort_richtig} von {gesamt} Wörtern wörtlich "
          f"richtig, {zeichen_richtig} von {gesamt} ergeben den richtigen "
          f"Buchstaben.")
    fehler = {}
    for e in ergebnisse:
        if not e["zeichen_richtig"]:
            fehler.setdefault(e["soll"], []).append(e["gehoert"] or "(nichts)")
    if not fehler:
        print("Kein Fehler - jedes Wort ergab den richtigen Buchstaben.")
        return
    print("\nWas hängt, mit dem, was stattdessen ankam:")
    for wort, gehoert in sorted(fehler.items(), key=lambda x: -len(x[1])):
        print(f"  {wort:12s} {len(gehoert)}x falsch: {', '.join(gehoert)}")


def main():
    argumente = sys.argv[1:]
    if "--auswerten" in argumente:
        datei = argumente[argumente.index("--auswerten") + 1]
        with open(datei, encoding="utf-8") as f:
            daten = json.load(f)
        auswerten(daten["ergebnisse"], daten.get("art", ""))
        return 0
    art = "alphabet"
    if "--namen" in argumente:
        art = "namen"
    if "--beides" in argumente:
        art = "beides"
    mal = 1
    if "--mal" in argumente:
        mal = int(argumente[argumente.index("--mal") + 1])
    return messen(art, mal, "--ohne-aufnahme" not in argumente)


if __name__ == "__main__":
    sys.exit(main())
