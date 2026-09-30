#!/usr/bin/env python3
"""DialOS: Radio hoeren.

Der Leser am anderen Ende der Medienliste. DialOS-Rhythmbox schreibt sie,
dieses Programm spielt, was darin steht - abgespielt wird mit Rhythmbox
(Stephans Entscheidung vom 2026-09-25, siehe docs/anwendungen.md).

WARUM DIE LISTE NICHT HIER GELESEN WIRD: medienliste_lesen() steht in
dialos_rhythmbox_sender.py, samt der Regel, dass die persoenliche Liste
des Kontos ueber der systemweiten liegt und ueber die Klangform
verglichen wird. Zwei Stellen mit derselben Aufgabe laufen auseinander -
wer dort etwas aendert, haette hier eine zweite, die anders entscheidet.
Dieselbe Ueberlegung wie in dialos-auskunft.py, das sich die Datums- und
Wetterbausteine aus dialos-start-ansage.py holt.

WARUM RHYTHMBOX NICHT NACH VORN GEHOLT WIRD: Der Nutzer sieht den
Bildschirm nicht, ein Fenster nuetzt ihm nichts - und unter Wayland darf
ein fremder Prozess ohnehin kein Fenster heben (gemessen am 2026-09-21,
siehe CLAUDE.md). Deshalb ueberall --no-present.

Aufruf:
    dialos-radio.py einschalten          Zuletzt gehoerter Sender, sonst Frage
    dialos-radio.py sender "oe drei"     Einen bestimmten Sender
    dialos-radio.py aus                  Anhalten
    dialos-radio.py lauter               In festen Stufen
    dialos-radio.py leiser
    dialos-radio.py was-laeuft           Ansage, was gerade spielt
    dialos-radio.py naechster            Naechster Eintrag der Liste
    dialos-radio.py liste                Was zur Auswahl steht (fuers Pruefen)
    dialos-radio.py --debug ...          Ausgabe zusaetzlich aufs Terminal
"""

import importlib.util
import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
SENDER_MODUL = "/usr/local/bin/dialos_rhythmbox_sender.py"
CLIENT = "rhythmbox-client"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-radio.log")

#: Welcher Sender zuletzt lief - je Konto, nicht systemweit. Die Auswahl
#: gilt fuer das ganze Geraet, die Gewohnheit gehoert dem Menschen.
ZULETZT = os.path.join(os.path.expanduser("~"), ".config", "dialos",
                       "radio-zuletzt.txt")

#: In welchen Stufen die Lautstaerke springt. Rhythmbox rechnet in 0 bis 1.
#: Zehn Prozent sind hoerbar, ohne dass man dreimal nachsteuern muss.
STUFE = 0.1

DEBUG = "--debug" in sys.argv


def melde(text):
    if DEBUG:
        print(text, flush=True)
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    """Ansagen sind hier keine Nettigkeit, sondern die einzige Rueckmeldung.

    Der Nutzer sieht nicht, ob etwas passiert ist. Ein Befehl ohne Ansage
    ist fuer ihn nicht von einem abgestuerzten zu unterscheiden.
    """
    melde(f"sagt: {text}")
    try:
        subprocess.run([SAY, text], timeout=60)
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"Sprachausgabe gescheitert: {fehler}")


def sender_modul():
    """dialos_rhythmbox_sender.py laden - das Modul hinter der Liste."""
    spec = importlib.util.spec_from_file_location("rs", SENDER_MODUL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def client(*argumente, hole_ausgabe=False):
    """rhythmbox-client aufrufen.

    --no-present bei jedem Aufruf: Ohne das holt Rhythmbox sein Fenster
    nach vorn und legt sich ueber das, was gerade offen ist.
    """
    befehl = [CLIENT, "--no-present", *argumente]
    melde("ruft: " + " ".join(befehl))
    try:
        fertig = subprocess.run(befehl, capture_output=True, timeout=25,
                                text=True, errors="replace")
    except FileNotFoundError:
        melde("rhythmbox-client nicht gefunden")
        return None
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"rhythmbox-client gescheitert: {fehler}")
        return None
    if hole_ausgabe:
        return (fertig.stdout or "").strip()
    return fertig.returncode == 0


def laeuft():
    try:
        return subprocess.run([CLIENT, "--check-running"],
                              capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def liste_holen(rs):
    """Die Radiosender aus der Medienliste - beide Ebenen zusammengefuehrt."""
    try:
        return rs.medienliste_lesen(art="radio")
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"Medienliste nicht lesbar: {fehler}")
        return []


def keine_liste_ansagen(rs):
    """Die ehrliche Antwort, wenn nichts zur Auswahl steht.

    Sie nennt den Weg, nicht nur das Problem - und sie nennt ihn ohne
    Dateipfad: Wer den Bildschirm nicht sieht, kann mit
    '/usr/local/share/dialos/medienliste.json' nichts anfangen.
    """
    sprich("Ich habe noch keine Sender. Die Liste wird mit dem Programm "
           "DialOS-Rhythmbox zusammengestellt.")
    melde("Medienliste leer oder nicht vorhanden "
          f"({rs.SYSTEMLISTE}, {rs.eigene_liste()})")


def zuletzt_lesen():
    try:
        with open(ZULETZT, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def zuletzt_merken(sprechform):
    try:
        os.makedirs(os.path.dirname(ZULETZT), exist_ok=True)
        with open(ZULETZT, "w", encoding="utf-8") as f:
            f.write(sprechform + "\n")
    except OSError as fehler:
        melde(f"Konnte den Sender nicht merken: {fehler}")


def sender_finden(rs, liste, gesucht):
    """Den Eintrag zu einer gesprochenen Sprechform suchen.

    Verglichen wird ueber die Klangform, nicht ueber die Zeichenkette -
    derselbe Massstab, mit dem die Doppelten-Pruefung arbeitet. Sonst
    faende "radio kärnten" den Eintrag "radio kaernten" nicht, obwohl
    beides derselbe gesprochene Satz ist.

    Zusaetzlich wird der Anfang zugelassen: Der Erkenner verschluckt
    gelegentlich ein Wort, und "radio" allein soll "radio eins" finden,
    solange nur EIN Eintrag dazu passt. Passen mehrere, wird nichts
    geraten - ein falscher Sender ist schlimmer als eine Rueckfrage.
    """
    ziel = rs._klangform(gesucht or "")
    if not ziel:
        return None, []
    genau = [e for e in liste
             if rs._klangform(e.get("sprechform") or "") == ziel]
    if len(genau) == 1:
        return genau[0], []
    anfang = [e for e in liste
              if rs._klangform(e.get("sprechform") or "").startswith(ziel)]
    if len(anfang) == 1:
        return anfang[0], []
    return None, anfang


def abspielen(rs, eintrag):
    quelle = (eintrag.get("quelle") or "").strip()
    name = eintrag.get("name") or eintrag.get("sprechform") or "der Sender"
    if not quelle:
        sprich(f"Zu {eintrag.get('sprechform', name)} habe ich keine Adresse.")
        melde(f"Eintrag ohne Quelle: {eintrag!r}")
        return False

    if not client("--play-uri", quelle):
        sprich("Ich konnte das Radio nicht starten.")
        return False

    zuletzt_merken(eintrag.get("sprechform") or "")
    # Kurz, weil der Nutzer weiterhoeren will - die Regel zur Laenge aus
    # docs/sprachbefehle.md. Der Sendername steht drin, damit er merkt,
    # wenn der Erkenner den falschen erwischt hat.
    sprich(f"{name}.")
    melde(f"spielt: {name} <{quelle}>")
    return True


def einschalten(rs, gesucht=None):
    liste = liste_holen(rs)
    if not liste:
        keine_liste_ansagen(rs)
        return 1

    if gesucht:
        eintrag, nah = sender_finden(rs, liste, gesucht)
        if eintrag:
            return 0 if abspielen(rs, eintrag) else 1
        if nah:
            # Mehrere Treffer: NICHT raten. Die Namen werden genannt,
            # damit der Nutzer den vollstaendigen Satz sprechen kann.
            namen = ", ".join(e.get("sprechform", "") for e in nah[:5])
            sprich(f"Das könnten mehrere sein: {namen}. "
                   "Sage den Sender noch einmal ganz.")
        else:
            sprich(f"{gesucht} habe ich nicht in der Liste.")
        melde(f"nicht gefunden: {gesucht!r} ({len(nah)} aehnliche)")
        return 1

    # Ohne Sendernamen: der zuletzt gehoerte. Das ist die Gewohnheit, die
    # ein Radio ausmacht - wer einschaltet, will meistens dasselbe wie
    # gestern und soll dafuer nicht den Namen sagen muessen.
    vorher = zuletzt_lesen()
    if vorher:
        eintrag, _ = sender_finden(rs, liste, vorher)
        if eintrag:
            return 0 if abspielen(rs, eintrag) else 1
        melde(f"Gemerkter Sender steht nicht mehr in der Liste: {vorher!r}")

    if len(liste) == 1:
        return 0 if abspielen(rs, liste[0]) else 1

    # Noch nie gehoert und mehrere zur Wahl: Es wird NICHT einfach der
    # erste gespielt. Der Nutzer bekommt die Auswahl - hoechstens fuenf,
    # weil eine Ansage mit dreissig Namen niemand behaelt.
    namen = ", ".join(e.get("sprechform", "") for e in liste[:5])
    rest = "" if len(liste) <= 5 else f" Und {len(liste) - 5} weitere."
    sprich(f"Welchen Sender möchtest Du hören? Zur Auswahl stehen: "
           f"{namen}.{rest}")
    melde(f"Auswahl angesagt ({len(liste)} Sender)")
    return 0


def ausschalten():
    if not laeuft():
        # Die Regel "anders sagen, wenn sich nichts geaendert hat" -
        # sonst klingt ein wirkungsloser Befehl wie ein erfolgreicher.
        sprich("Es läuft gerade nichts.")
        return 0
    client("--stop")
    sprich("Radio aus.")
    melde("angehalten")
    return 0


def lautstaerke(richtung):
    if not laeuft():
        sprich("Es läuft gerade nichts.")
        return 0
    jetzt = client("--print-volume", hole_ausgabe=True)
    try:
        wert = float((jetzt or "").split()[-1])
    except (ValueError, IndexError):
        # Rueckfall auf die Schritte von Rhythmbox selbst. Sie sind
        # kleiner als unsere Stufe, aber besser als gar nichts.
        client("--volume-up" if richtung > 0 else "--volume-down")
        sprich("Lauter." if richtung > 0 else "Leiser.")
        return 0

    neu = min(1.0, max(0.0, wert + richtung * STUFE))
    client("--set-volume", f"{neu:.2f}")
    if neu >= 1.0 and wert >= 1.0:
        sprich("Lauter geht nicht.")
    elif neu <= 0.0 and wert <= 0.0:
        sprich("Leiser geht nicht, es ist schon aus.")
    else:
        sprich("Lauter." if richtung > 0 else "Leiser.")
    melde(f"Lautstaerke {wert:.2f} -> {neu:.2f}")
    return 0


def was_laeuft():
    if not laeuft():
        sprich("Es läuft gerade nichts.")
        return 0
    text = client("--print-playing", hole_ausgabe=True)
    if not text:
        sprich("Ich kann gerade nicht sagen, was läuft.")
        return 1
    # Bei einem Stream steht hier der ICY-Titel, also meist
    # "Interpret - Titel" des laufenden Stuecks. Das ist genau die
    # Auskunft, die ein blinder Nutzer sonst nirgends bekommt.
    sprich(f"Es läuft: {text}")
    melde(f"laeuft: {text}")
    return 0


def naechster(rs):
    """Zum naechsten Sender der Liste - nicht zum naechsten Titel.

    rhythmbox-client --next waere das Naheliegende und ist hier falsch:
    Bei einem laufenden Radiostream gibt es kein naechstes Stueck, der
    Befehl liefe ins Leere. Gemeint ist der naechste SENDER.
    """
    liste = liste_holen(rs)
    if not liste:
        keine_liste_ansagen(rs)
        return 1
    if len(liste) == 1:
        sprich("Ich habe nur einen Sender in der Liste.")
        return 0

    vorher = zuletzt_lesen()
    stelle = -1
    for i, eintrag in enumerate(liste):
        if rs._klangform(eintrag.get("sprechform") or "") == rs._klangform(vorher):
            stelle = i
            break
    return 0 if abspielen(rs, liste[(stelle + 1) % len(liste)]) else 1


def liste_zeigen(rs):
    """Fuers Pruefen am Geraet - und fuer die Grammatik.

    Die Sprechformen, die hier stehen, sind genau die, die der
    Befehlsdienst in die Vosk-Grammatik aufnimmt.
    """
    liste = liste_holen(rs)
    if not liste:
        print("Keine Sender. Gesucht in:")
        print(f"  {rs.SYSTEMLISTE}")
        print(f"  {rs.eigene_liste()}")
        return 1
    for eintrag in liste:
        print(f"{eintrag.get('sprechform', ''):<28} "
              f"{eintrag.get('name', ''):<28} {eintrag.get('quelle', '')}")
    return 0


def main():
    argumente = [a for a in sys.argv[1:] if a != "--debug"]
    if not argumente:
        print(__doc__)
        return 2

    befehl = argumente[0]
    rest = " ".join(argumente[1:]).strip()

    # Die Sender-Befehle brauchen das Modul, die Steuerbefehle nicht -
    # und ein Import, der scheitert, darf "Radio aus" nicht verhindern.
    if befehl in ("einschalten", "sender", "naechster", "liste"):
        try:
            rs = sender_modul()
        except Exception as fehler:        # noqa: BLE001
            melde(f"Sendermodul nicht ladbar: {fehler}")
            sprich("Ich komme gerade nicht an die Senderliste.")
            return 1

    if befehl == "einschalten":
        return einschalten(rs, rest or None)
    if befehl == "sender":
        if not rest:
            sprich("Welchen Sender möchtest Du hören?")
            return 2
        return einschalten(rs, rest)
    if befehl == "naechster":
        return naechster(rs)
    if befehl == "liste":
        return liste_zeigen(rs)
    if befehl == "aus":
        return ausschalten()
    if befehl == "lauter":
        return lautstaerke(+1)
    if befehl == "leiser":
        return lautstaerke(-1)
    if befehl == "was-laeuft":
        return was_laeuft()

    print(f"Unbekannter Befehl: {befehl}", file=sys.stderr)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
