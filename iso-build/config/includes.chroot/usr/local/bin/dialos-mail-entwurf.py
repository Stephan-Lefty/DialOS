#!/usr/bin/env python3
"""Legt eine diktierte Mail als ENTWURF in Thunderbird ab - gesendet wird nie.

Stephans Entscheidung vom 2026-09-18, aus drei Vorschlaegen: "Diktieren, dann
Entwurf". Die Antwort entsteht per Sprache, landet in Thunderbirds Entwuerfen
und geht erst hinaus, wenn ein Mensch sie absendet. Damit kann ein
missverstandenes Wort nichts anrichten, was sich nicht zurueckholen laesst -
dieselbe Ueberlegung wie beim Drucken mit Rueckfrage, nur ernster: Eine
abgeschickte Mail ist aus der Welt.

WOHIN DER ENTWURF KOMMT: in "Local Folders/Drafts", nicht in den
IMAP-Entwurfsordner. Der IMAP-Ordner ist auf dem Gerät nur eine Kopie des
Servers; was dort hineingeschrieben wird, kennt der Server nicht und
verschwindet beim naechsten Abgleich. Die lokalen Ordner gehoeren dagegen dem
Geraet - Thunderbird zeigt den Entwurf dort, und von dort laesst er sich
absenden oder weiterbearbeiten.

NICHT SCHREIBEN, WAEHREND THUNDERBIRD LAEUFT. Dieselbe Regel und derselbe Weg
wie bei den Kontakten (dialos-empfaenger.py, 2026-09-17): Thunderbird haelt
seine mbox-Dateien offen und wuerde eine Aenderung von aussen ueberschreiben.
Laeuft es, kommt der Entwurf in eine Warteschlange und wird beim naechsten
Anmelden nachgetragen.

Aufruf:
  dialos-mail-entwurf.py anlegen --an ADRESSE --betreff TEXT --text DATEI
                                 [--bezug MESSAGE-ID] [--zitat DATEI]
  dialos-mail-entwurf.py nachholen      Warteschlange abarbeiten
  dialos-mail-entwurf.py zeigen         Was in den Entwuerfen liegt
"""

import email.message
import email.utils
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


def profil():
    """Thunderbirds Profilordner - der mit der groessten abook.sqlite gewinnt."""
    wurzel = os.path.join(HEIM, ".thunderbird")
    if not os.path.isdir(wurzel):
        return None
    beste, groesse = None, -1
    for name in sorted(os.listdir(wurzel)):
        ordner = os.path.join(wurzel, name)
        if not os.path.isdir(ordner):
            continue
        marke = os.path.join(ordner, "prefs.js")
        if not os.path.isfile(marke):
            continue
        wert = os.path.getsize(marke)
        if wert > groesse:
            beste, groesse = ordner, wert
    return beste


def entwurfsordner():
    """Pfad der lokalen Entwurfs-mbox - sie wird bei Bedarf angelegt."""
    ordner = profil()
    if not ordner:
        return None
    lokal = os.path.join(ordner, "Mail", "Local Folders")
    if not os.path.isdir(lokal):
        return None
    return os.path.join(lokal, "Drafts")


def thunderbird_laeuft():
    try:
        p = subprocess.run(["pgrep", "-x", "thunderbird"], capture_output=True, timeout=10)
        return p.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return True            # im Zweifel belegt - lieber vormerken


def eigene_adresse():
    """Die eigene Mailadresse aus den persoenlichen Daten - oder ""."""
    try:
        spec = importlib.util.spec_from_file_location("persoenliche_daten",
                                                      PERSOENLICHE_DATEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        daten = modul.lesen()
        name = modul.voller_name(daten)
        adresse = (daten.get("mail") or "").strip()
        return email.utils.formataddr((name, adresse)) if adresse else ""
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"persoenliche Daten nicht lesbar: {fehler}")
        return ""


def nachricht_bauen(an, betreff, text, bezug=None, zitat=""):
    """Die Mail als Nachricht - Text, kein HTML.

    REINER TEXT IST ABSICHT: Er ist vorlesbar, klein und in jedem Programm
    lesbar. HTML brauchte eine zweite Fassung, die auseinanderlaufen kann - und
    ein Screenreader liest sie schlechter.
    """
    nachricht = email.message.EmailMessage()
    nachricht["To"] = an
    nachricht["Subject"] = betreff
    absender = eigene_adresse()
    if absender:
        nachricht["From"] = absender
    nachricht["Date"] = email.utils.formatdate(localtime=True)
    nachricht["Message-ID"] = email.utils.make_msgid(domain="dialos.local")
    if bezug:
        nachricht["In-Reply-To"] = bezug
        nachricht["References"] = bezug
    koerper = text.strip()
    if zitat.strip():
        # Das Zitat mit "> " - so kennt es jeder Mailer, und der Vorleser
        # erkennt daran, wo die eigene Antwort aufhoert.
        koerper += "\n\n" + "\n".join("> " + z for z in zitat.strip().splitlines())
    nachricht.set_content(koerper + "\n")
    return nachricht


def als_mbox_eintrag(nachricht):
    """Ein mbox-Eintrag, so wie Thunderbird ihn selbst schreibt.

    ZEILENENDEN CR LF, UND DAS IST DER GANZE PUNKT (2026-09-18, an Stephans
    erstem Entwurf gefunden): Die Datei stand richtig auf der Platte, und
    Thunderbird zeigte den Ordner trotzdem als "0 Nachrichten". Zum Vergleich
    das eigene Postfach angesehen - dort endet JEDE Zeile auf CR LF. Mit
    blossem LF hat Thunderbirds Parser den Eintrag nicht erkannt, ohne Fehler
    und ohne Meldung: genau die Art Fehlschlag, die ein blinder Nutzer nie
    bemerken wuerde.

    X-Mozilla-Status=0008 heisst "Entwurf"; ohne diese Zeilen zeigt Thunderbird
    die Nachricht als gewoehnliche Mail und bietet kein Bearbeiten an.
    """
    roh = nachricht.as_string()
    kopf = (f"From - {time.strftime('%a %b %d %H:%M:%S %Y')}\n"
            "X-Mozilla-Status: 0008\n"
            "X-Mozilla-Status2: 00000000\n")
    # In einer mbox beginnt keine Zeile im Text mit "From " - sonst faengt dort
    # scheinbar eine neue Nachricht an.
    roh = "\n".join((">" + z) if z.startswith("From ") else z
                    for z in roh.splitlines())
    text = kopf + roh + "\n\n"
    return text.replace("\r\n", "\n").replace("\n", "\r\n")


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


def ablegen(an, betreff, text, bezug=None, zitat=""):
    """Entwurf ablegen. True: in Thunderbird, False: vorgemerkt."""
    daten = {"an": an, "betreff": betreff, "text": text, "bezug": bezug,
             "zitat": zitat}
    ziel = entwurfsordner()
    if ziel is None or thunderbird_laeuft():
        _vormerken(daten)
        melde(f"vorgemerkt (Thunderbird laeuft oder kein Profil): {betreff!r}")
        return False
    nachricht = nachricht_bauen(an, betreff, text, bezug, zitat)
    # Binaer anhaengen: Sonst uebersetzt Python die Zeilenenden je nach System
    # wieder zurueck, und genau darauf kam es hier an.
    with open(ziel, "ab") as f:
        f.write(als_mbox_eintrag(nachricht).encode("utf-8"))
    # Die .msf-Datei ist Thunderbirds Verzeichnis der mbox. Ist sie aelter als
    # die mbox, baut Thunderbird sie neu auf - sonst zeigte es den Entwurf nicht.
    msf = ziel + ".msf"
    if os.path.exists(msf):
        try:
            os.unlink(msf)
        except OSError as fehler:
            melde(f".msf nicht loeschbar: {fehler}")
    melde(f"Entwurf abgelegt: {betreff!r} an {an}")
    return True


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
    if thunderbird_laeuft() or entwurfsordner() is None:
        melde("Nachholen verschoben - Thunderbird laeuft oder kein Profil")
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
        ziel = entwurfsordner()
        print(f"Entwuerfe: {ziel or 'kein Thunderbird-Profil'}")
        if ziel and os.path.isfile(ziel):
            anzahl = sum(1 for z in open(ziel, encoding="utf-8", errors="replace")
                         if z.startswith("From - "))
            print(f"Eintraege: {anzahl}")
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
