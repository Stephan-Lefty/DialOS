#!/usr/bin/env python3
"""DialOS: Notizen vorlesen und leeren.

Stephans Frage vom 2026-08-18: "Wenn ich heute was in den Einkaufszettel
schreibe, wie kann ich den jederzeit abhoeren, ergaenzen und wenn der
Einkauf zuhause ist loeschen?" Damit war klar, dass "aufnehmen" allein zu
wenig ist - ein Einkaufszettel wird gelesen, ergaenzt und irgendwann
weggeworfen.

Die drei Teile verteilen sich so:

  ergaenzen   braucht kein neues Programm. "Einkaufszettel aufnehmen"
              schreibt an die Datei AN, nicht darueber (dialos-diktat.py,
              notiz_schreiben oeffnet mit "a").
  vorlesen    dieses Skript, Unterbefehl "vorlesen".
  leeren      dieses Skript, Unterbefehl "loeschen" - mit Rueckfrage.

WARUM EINE RUECKFRAGE VOR DEM LEEREN: Die Regel steht in
docs/sprachbefehle.md und stammt nicht von hier - sicherheitskritische
Befehle bekommen eine Ja/Nein-Rueckfrage, unabhaengig davon, wie sicher die
Erkennung war. Ein Einkaufszettel ist nicht sicherheitskritisch, aber der
Verlust ist unumkehrbar und die Arbeit war Sprechen: Wer zwanzig Dinge
diktiert hat und sie durch ein missverstandenes Wort verliert, diktiert sie
nicht gern noch einmal.

UND EIN NETZ DAHINTER: Der alte Inhalt wandert beim Leeren nach
"<name>-verworfen.txt". Fuer den Nutzer ist der Zettel weg - das ist die
Ansage und das Verhalten. Aber ein sehender Helfer kann ihn im Notfall
zurueckholen. Es kostet nichts und deckt genau den Fall ab, den eine
Rueckfrage nicht abdeckt: dass der Nutzer "ja" sagt und es hinterher
bedauert.

Aufruf:
    dialos-notiz.py einkaufszettel vorlesen
    dialos-notiz.py einkaufszettel loeschen
    dialos-notiz.py --debug ...
"""

import json
import os
import re
import subprocess
import sys
import time

MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
SAY = "/usr/local/bin/dialos-say.py"
ECHO_QUELLE = "dialos_mikrofon_ohne_echo"
NOTIZ_ORDNER = os.path.join(os.path.expanduser("~"), "Notizen")

# Wie die Notiz in einem Satz heisst. Ohne diese Tabelle entstehen falsche
# Saetze, weil der Dateiname in den Satz eingebaut wird: "Der einkaufszettel
# hat 10 Eintraege" (klein) und - schlimmer - "Der notizen ist leer",
# falsches Geschlecht und falscher Numerus.
#
# Fuer einen Nutzer, der ausschliesslich zuhoert, ist die Ansage der ganze
# Text, den er von DialOS bekommt. Ein falscher Artikel ist dort kein
# Schoenheitsfehler, sondern der Unterschied zwischen einem Programm, das
# spricht, und einem, das Platzhalter vorliest.
#
# (Bezeichnung, Verb im Singular/Plural, Personalpronomen im Akkusativ)
BEZEICHNUNG = {
    "einkaufszettel": ("Der Einkaufszettel", "ist", "hat", "ihn"),
    "notizen": ("Die Notizen", "sind", "haben", "sie"),
}


def benennen(name):
    """Gibt (Bezeichnung, ist/sind, hat/haben, ihn/sie) zurueck.

    Unbekannte Namen bekommen eine neutrale Form, die immer aufgeht - besser
    ein etwas steifer Satz als ein falscher.
    """
    return BEZEICHNUNG.get(name, (f"Die Notiz {name}", "ist", "hat", "sie"))


def marke_pfad(name):
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


# DIESELBE Marke wie beim Diktat, mit Absicht. Sie bedeutet nicht "ein
# Diktat laeuft", sondern "ein anderer Dienst hoert gerade zu" - und die
# Rueckfrage vor dem Leeren tut genau das. Ohne sie wuerde der
# Befehlsdienst waehrend der Frage mithoeren und ein "ja" oder "nein"
# irgendwo einordnen.
#
# Zwei Marken mit derselben Bedeutung waeren die schlechtere Wahl: Der
# Befehlsdienst muesste beide kennen, und wer eine dritte Stelle baut,
# vergisst die zweite.
FREMDE_AUFNAHME_MARKE = marke_pfad("dialos-diktat-aktiv")
PROTOKOLL = os.path.join(os.path.expanduser("~"), "dialos-notiz.log")

DEBUG = "--debug" in sys.argv

# Grammatik der Rueckfrage. Winzig, und genau darum verlaesslich - dasselbe
# Prinzip wie bei der Befehlserkennung und beim Schlusssatz des Diktats.
GRAMMATIK_JA_NEIN = json.dumps(["ja", "nein", "[unk]"])
ANTWORT_ZEITGRENZE_S = 8.0

# Zweiter Versuch, wenn die erste Antwort nicht ankam (Stephan, 2026-08-19: sein
# "ja" wurde nicht verstanden). Ohne ihn muesste der Nutzer den ganzen Befehl
# neu sprechen, obwohl nur ein Wort gefehlt hat.
ANSAGE_NOCHMAL = "Das habe ich nicht verstanden. Sage ja oder nein."
VERSUCHE = 2


def melde(text):
    if DEBUG:
        print(text, flush=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text, frage=False):
    if not os.access(SAY, os.X_OK):
        print(text)
        return
    befehl = [SAY] + (["--frage"] if frage else []) + [text]
    subprocess.run(befehl, capture_output=True, timeout=120)


def pfad_fuer(name):
    sicher = re.sub(r"[^\w -]", "", name).strip() or "notizen"
    return os.path.join(NOTIZ_ORDNER, sicher + ".txt")


def eintraege_lesen(name):
    try:
        with open(pfad_fuer(name), encoding="utf-8") as f:
            return [z.strip() for z in f if z.strip()]
    except OSError:
        return []


def aufzaehlen(zeilen):
    """Wie in dialos-diktat.py: Punkt statt Komma zwischen den Eintraegen.

    Der Punkt ist Absicht. Piper macht daran eine deutlichere Pause, und die
    braucht der Zuhoerer, um mitzuzaehlen. Ohne Satzzeichen hetzt es durch -
    gemessen 3,670 s gegen 4,884 s fuer dieselbe Liste (2026-08-18).
    """
    saubern = lambda z: z.rstrip(" .,;:")
    return " ".join(saubern(z) + "." for z in zeilen if saubern(z))


def waehle_mikrofon():
    try:
        roh = subprocess.run(["pactl", "-f", "json", "list", "sources"],
                             capture_output=True, text=True, timeout=5).stdout
        quellen = json.loads(roh) if roh.strip() else []
    except Exception:
        return None
    namen = [q.get("name", "") for q in quellen
             if q.get("name") and not q["name"].endswith(".monitor")]
    if ECHO_QUELLE in namen:
        return ECHO_QUELLE
    eingebaut = [n for n in namen if n.startswith("alsa_input.pci-")]
    return eingebaut[0] if eingebaut else None


def ja_oder_nein(frage):
    """Frage stellen und die Antwort hoeren. True, False oder None.

    None heisst "nichts Passendes verstanden" und ist bewusst von False
    getrennt: Bei None bleibt der Zettel stehen UND der Nutzer erfaehrt, dass
    nichts verstanden wurde. Ein stilles Nichtstun waere fuer ihn nicht von
    einem stillen Loeschen zu unterscheiden.

    DIE FRAGE WIRD HIER GESTELLT UND NICHT VOM AUFRUFER - das war der Fehler
    vom 2026-08-19. Vorher sprach der Aufrufer die Frage und rief danach diese
    Funktion, die erst DANN das Sprachmodell lud (rund eine Sekunde) und
    anschliessend die Aufnahme startete. Stephans "ja" fiel genau in diese
    Luecke: im Protokoll stand keine einzige "Antwort gehoert"-Zeile, weil zum
    Zeitpunkt des Sprechens noch nichts aufnahm. Dieselbe Fehlerklasse wie am
    2026-08-18 beim Diktat und am 2026-08-15 bei der Start-Ansage - deshalb
    liegt das Vorbereiten jetzt zwingend VOR der Frage, und zwar dadurch, dass
    die Funktion beides selbst in der Hand hat.

    Aufgenommen wird bewusst NICHT waehrend der Frage. Die Grammatik kennt nur
    "ja", "nein" und "[unk]" - die eigene Stimme des Systems koennte darin als
    "ja" landen, und das wuerde den Zettel loeschen, ohne dass jemand etwas
    gesagt hat. Ein Loeschen ohne Zustimmung ist der schlimmere Fehler.
    """
    bereit = _antwort_vorbereiten()
    if not bereit:
        return None
    modell, quelle = bereit
    for versuch in range(1, VERSUCHE + 1):
        sprich(frage if versuch == 1 else ANSAGE_NOCHMAL, frage=True)
        antwort = _antwort_hoeren(modell, quelle)
        if antwort is not None:
            return antwort
        melde(f"  Versuch {versuch} von {VERSUCHE}: keine verwertbare Antwort")
    return None


def _antwort_vorbereiten():
    """Sprachmodell und Mikrofon - alles Langsame VOR der Frage."""
    try:
        import vosk
    except ImportError:
        melde("  vosk fehlt - keine Rueckfrage moeglich")
        return None
    quelle = waehle_mikrofon()
    if not quelle:
        melde("  kein Mikrofon - keine Rueckfrage moeglich")
        return None
    vosk.SetLogLevel(-1)
    t0 = time.time()
    modell = vosk.Model(MODELL_KLEIN)
    melde(f"  Antwort-Erkenner bereit in {time.time()-t0:.1f} s")
    return modell, quelle


def _antwort_hoeren(modell, quelle):
    """Einmal zuhoeren. True, False oder None."""
    import vosk
    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_JA_NEIN)
    prozess = subprocess.Popen(
        ["parec", "-d", quelle, "--format=s16le",
         f"--rate={ABTASTRATE}", "--channels=1"],
        stdout=subprocess.PIPE)
    ende = time.time() + ANTWORT_ZEITGRENZE_S
    try:
        while time.time() < ende:
            block = prozess.stdout.read(4000)
            if not block:
                break
            if not erkenner.AcceptWaveform(block):
                continue
            gehoert = json.loads(erkenner.Result()).get("text", "").strip()
            if not gehoert:
                continue
            melde(f"  Antwort gehoert: {gehoert!r}")
            worte = gehoert.split()
            if "[unk]" in worte:
                continue            # es wurde noch etwas anderes gesagt
            if "ja" in worte and "nein" not in worte:
                return True
            if "nein" in worte:
                return False
    finally:
        try:
            prozess.terminate()
        except Exception:
            pass
    return None


# ------------------------------------------------------------ Unterbefehle

def vorlesen(name):
    eintraege = eintraege_lesen(name)
    bez, ist, _hat, _ihn = benennen(name)
    if not eintraege:
        sprich(f"{bez} {ist} leer.")
        return 0
    # Anzahl VORAN, damit der Nutzer weiss, was auf ihn zukommt - bei zwanzig
    # Eintraegen ist das der Unterschied zwischen Zuhoeren und Abwarten.
    zahl = len(eintraege)
    kopf = "Ein Eintrag." if zahl == 1 else f"{zahl} Einträge."
    melde(f"  vorlesen: {zahl} Eintraege aus {pfad_fuer(name)}")
    sprich(f"{kopf} {aufzaehlen(eintraege)}")
    return 0


def loeschen(name):
    # Marke fuer die Dauer der Rueckfrage - siehe FREMDE_AUFNAHME_MARKE.
    open(FREMDE_AUFNAHME_MARKE, "w").close()
    try:
        return _loeschen(name)
    finally:
        try:
            os.unlink(FREMDE_AUFNAHME_MARKE)
        except OSError:
            pass


def _loeschen(name):
    eintraege = eintraege_lesen(name)
    bez, ist, hat, ihn = benennen(name)
    if not eintraege:
        sprich(f"{bez} {ist} schon leer.")
        return 0
    zahl = len(eintraege)
    was = "einen Eintrag" if zahl == 1 else f"{zahl} Einträge"
    # "Sage ja oder nein." gehoert in die Frage (Stephan, 2026-08-19). Der
    # Nutzer sieht keine Knoepfe; welche Woerter erwartet werden, muss gesagt
    # werden - dieselbe Regel wie bei der Anleitung zum Einkaufszettel.
    antwort = ja_oder_nein(
        f"{bez} {hat} {was}. Soll ich {ihn} löschen? Sage ja oder nein.")
    if antwort is None:
        sprich(f"Ich habe nichts verstanden. Ich lasse {ihn} stehen.")
        return 0
    if antwort is False:
        sprich(f"Gut, ich lasse {ihn} stehen.")
        return 0

    # Netz: Inhalt beiseitelegen, statt ihn wirklich zu vernichten.
    quelle = pfad_fuer(name)
    ablage = quelle[:-4] + "-verworfen.txt"
    try:
        with open(ablage, "a", encoding="utf-8") as f:
            f.write(f"# verworfen {time.strftime('%Y-%m-%d %H:%M')}\n")
            for z in eintraege:
                f.write(z + "\n")
        open(quelle, "w", encoding="utf-8").close()
    except OSError as fehler:
        melde(f"  Loeschen fehlgeschlagen: {fehler}")
        sprich("Das hat nicht geklappt.")
        return 1
    melde(f"  geleert: {quelle}, Sicherung in {ablage}")
    sprich(f"{bez} {ist} gelöscht.")
    return 0


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(argumente) < 2:
        print(__doc__.strip().splitlines()[-4], file=sys.stderr)
        print("Aufruf: dialos-notiz.py NAME vorlesen|loeschen", file=sys.stderr)
        return 2
    name, was = argumente[0], argumente[1]
    melde(f"=== {was} {name} ===")
    if was == "vorlesen":
        return vorlesen(name)
    if was in ("loeschen", "löschen"):
        return loeschen(name)
    print(f"Unbekannt: {was}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
