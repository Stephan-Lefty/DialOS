#!/usr/bin/env python3
"""
dialos_podcast.py - RSS-Feeds pruefen und die neueste Folge finden.

Das Gegenstueck zu dialos_rhythmbox_sender.py, eine Gattung weiter:
Radiosender haben eine Stream-Adresse, Podcasts einen Feed, aus dem die
Adresse der jeweils neuesten Folge erst herausgelesen werden muss.

WARUM ES DIESE DATEI GIBT - der Befund vom 2026-10-05: Nicht jeder
RSS-Feed hat Audio. Die beiden Nachrichten-Feeds des Deutschlandfunks
(nachrichten-100.rss und die-nachrichten.353.de.rss) liefern 39
Eintraege und KEIN EINZIGES <enclosure> - das sind Textartikel. Ein
solcher Feed stuende in der Medienliste und machte nie einen Ton, und
der blinde Nutzer koennte nicht nachsehen, warum.

Das ist dieselbe Fehlerklasse wie ein Radiosender, der mit "200 OK"
antwortet und kein Audio liefert. Dort hat ffprobe sie gefunden; hier
muss zuerst der Feed selbst befragt werden.

WARUM KEIN feedparser: Nicht installiert, und fuer diese Aufgabe nicht
noetig. xml.etree.ElementTree aus der Standardbibliothek liest RSS
ausreichend genau - gebraucht werden Titel, <enclosure url>, <pubDate>
und die iTunes-Dauer. Ein zusaetzliches Paket waere eine
Abhaengigkeit mehr im Kunden-Rezept, fuer nichts.

Aufruf:
    dialos_podcast.py pruefen ADRESSE [ADRESSE ...]
    dialos_podcast.py neueste ADRESSE      nur die neueste Folge zeigen
    dialos_podcast.py --schnell pruefen ...  ohne ffprobe
"""

import argparse
import email.utils
import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

#: Die Audio-Pruefung kommt aus dem Sender-Modul - dort steht sie samt
#: der Lehre, warum ein HTTP-Test nicht genuegt. Eine zweite Fassung hier
#: liefe beim naechsten Fehler auseinander.
SENDER_MODUL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "dialos_rhythmbox_sender.py")
if not os.path.isfile(SENDER_MODUL):
    SENDER_MODUL = "/usr/local/bin/dialos_rhythmbox_sender.py"

#: Ab wann ein Feed als eingeschlafen gilt. Eine Kurznachrichten-Sendung
#: erscheint mehrmals taeglich; vierzehn Tage ohne neue Folge heisst, dass
#: dort nichts mehr kommt. Der Wert ist absichtlich grosszuegig - ein
#: Wochenend-Podcast soll nicht als tot gelten.
TOT_NACH_TAGEN = 14

#: Nachrichten sollen kurz sein. Laenger als das ist keine
#: Kurznachrichten-Sendung mehr, sondern ein Magazin - das gehoert dem
#: Menschen gesagt, nicht stillschweigend aussortiert.
KURZ_BIS_SEKUNDEN = 600

KOPF = {"User-Agent": "DialOS-Medienliste/1.0 (+https://dialos.org)"}

#: Hier liegen heruntergeladene Folgen, je Podcast ein Ordner mit nur der
#: neuesten Datei. Im Cache, weil sie jederzeit neu geholt werden koennen.
FOLGEN = os.path.join(os.path.expanduser("~"), ".cache", "dialos", "folgen")

#: Dauert das Herunterladen laenger als das, wird angesagt, dass es dauert.
#: Die tagesschau (2 MB) ist in unter einer Sekunde da und bleibt still; ein
#: Hoerspiel von 70 MB braucht etliche Sekunden, und Stille so lange klingt
#: fuer jemanden, der nichts sieht, wie ein Fehler.
WARTEN_ANSAGE_NACH_S = 2


def sagen(text=""):
    print(text, flush=True)


def fehler(text):
    print(f"  ! {text}", file=sys.stderr, flush=True)


def sender_modul():
    spec = importlib.util.spec_from_file_location("rs", SENDER_MODUL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def feed_holen(url, zeit=25):
    """Den Feed als Text. Gibt (text, fehlermeldung) zurueck.

    Mit curl, nicht mit urllib: Es ist dasselbe Werkzeug, das die
    Senderpruefung benutzt, es folgt Weiterleitungen zuverlaessig und
    bringt die Zeitgrenze mit.
    """
    try:
        fertig = subprocess.run(
            ["curl", "-sL", "--max-time", str(zeit), "-A", KOPF["User-Agent"], url],
            capture_output=True, timeout=zeit + 5)
    except FileNotFoundError:
        return "", "curl fehlt"
    except (OSError, subprocess.TimeoutExpired):
        return "", f"keine Antwort in {zeit} s"
    if fertig.returncode != 0:
        return "", f"curl-Fehler {fertig.returncode}"
    # Feeds sind fast immer UTF-8, aber nicht immer sauber deklariert -
    # dieselbe Nachsicht wie bei den ICY-Kopfzeilen.
    return fertig.stdout.decode("utf-8", errors="replace"), ""


def _text(element, pfad):
    gefunden = element.find(pfad)
    return (gefunden.text or "").strip() if gefunden is not None else ""


def _dauer_in_sekunden(wert):
    """iTunes schreibt die Dauer als Sekunden, "M:SS" oder "H:MM:SS"."""
    wert = (wert or "").strip()
    if not wert:
        return None
    if wert.isdigit():
        return int(wert)
    teile = wert.split(":")
    try:
        zahlen = [int(t) for t in teile]
    except ValueError:
        return None
    sekunden = 0
    for zahl in zahlen:
        sekunden = sekunden * 60 + zahl
    return sekunden


def _datum(wert):
    """RFC-2822 aus <pubDate> in einen Zeitstempel. None, wenn unlesbar."""
    try:
        zerlegt = email.utils.parsedate_to_datetime(wert)
    except (TypeError, ValueError):
        return None
    return zerlegt.timestamp() if zerlegt else None


def _ordnername(name):
    """Ein Ordnername aus dem Namen des Podcasts - nur Kleinbuchstaben und -."""
    name = name.lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        name = name.replace(alt, neu)
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-") or "podcast"


def folge_herunterladen(audio, name, bei_wartezeit=None, zeit=600, wurzel=None):
    """Die Folge als Datei holen. Gibt (pfad, fehlermeldung) zurueck.

    WARUM NICHT STREAMEN - die Probe am Geraet vom 2026-11-06: Rhythmbox
    spielt eine HTTPS-Adresse nur, wenn sie in seiner Datenbank steht
    (--play-uri, MPRIS OpenUri und eine .pls-Liste blieben stumm,
    AddToQueue sagte "Keine registrierte Quelle kann die Adresse
    verarbeiten"). Bei einem Sender ist das ein einmaliger Eintrag; bei
    Podcasts hat aber jede Folge eine neue Adresse. Jede neue Folge hiess
    also: Rhythmbox beenden, Datenbank beschreiben, neu starten - das
    laufende Radio brach ab, bis zu fuenfzehn Sekunden Stille, und die
    Datenbank wuchs um einen Eintrag je Folge, fuer immer.

    Eine lokale Datei (file://) spielt Rhythmbox dagegen sofort und legt
    den Eintrag selbst an, ohne Neustart. Gemessen mit laufendem Oe1: kein
    Abbruch, dieselbe Prozessnummer. Wird die Datei geloescht, versteckt
    Rhythmbox den Eintrag und entfernt ihn nach "grace-period" Tagen
    (am Geraet 45) - die Datenbank waechst damit nicht mehr unbegrenzt.

    JE PODCAST NUR DIE NEUESTE DATEI: Nach dem Holen wird der Rest des
    Ordners geloescht. Liegt die Folge schon da, wird sie nicht erneut
    geholt. Geschrieben wird erst in eine ".teil"-Datei - eine halb
    geladene Folge darf nie abgespielt werden.
    """
    ordner = os.path.join(wurzel or FOLGEN, _ordnername(name))
    endung = os.path.splitext(urllib.parse.urlparse(audio).path)[1].lower()
    if not re.fullmatch(r"\.[a-z0-9]{2,4}", endung):
        endung = ".mp3"
    pfad = os.path.join(ordner, hashlib.sha1(audio.encode()).hexdigest()[:16] + endung)

    if not (os.path.isfile(pfad) and os.path.getsize(pfad) > 0):
        os.makedirs(ordner, exist_ok=True)
        teil = pfad + ".teil"
        try:
            prozess = subprocess.Popen(
                ["curl", "-sL", "--fail", "--max-time", str(zeit),
                 "-A", KOPF["User-Agent"], "-o", teil, audio],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (FileNotFoundError, OSError):
            return "", "curl fehlt"
        try:
            rueckgabe = prozess.wait(timeout=WARTEN_ANSAGE_NACH_S)
        except subprocess.TimeoutExpired:
            if bei_wartezeit:
                bei_wartezeit()
            try:
                rueckgabe = prozess.wait(timeout=zeit + 5)
            except subprocess.TimeoutExpired:
                prozess.kill()
                rueckgabe = None
        if rueckgabe != 0 or not os.path.isfile(teil) or os.path.getsize(teil) == 0:
            try:
                os.remove(teil)
            except OSError:
                pass
            return "", ("keine Antwort" if rueckgabe is None
                        else f"Herunterladen gescheitert (curl {rueckgabe})")
        os.replace(teil, pfad)

    for datei in os.listdir(ordner):
        alt = os.path.join(ordner, datei)
        if alt != pfad and os.path.isfile(alt):
            try:
                os.remove(alt)
            except OSError:
                pass
    return pfad, ""


def feed_lesen(text):
    """Den Feed zerlegen: (kopf, folgen, fehlermeldung).

    `folgen` ist nach Datum sortiert, die neueste zuerst. Ohne Datum
    bleibt die Reihenfolge des Feeds - die meisten Anbieter stellen die
    neueste Folge nach vorn, und das ist besser als zu raten.
    """
    if not text.strip():
        return {}, [], "leere Antwort"

    # HTML VOR dem Parsen erkennen, nicht erst im Fehlerzweig. Eine
    # Uebersichtsseite statt eines Feeds ist der haeufigste Fehlgriff -
    # und schlankes HTML ist durchaus gueltiges XML, landet also gar
    # nicht im ParseError. Dann kaeme nur "kein <channel>" heraus, was
    # richtig, aber nicht hilfreich ist (2026-10-05 von einem Test
    # gefunden, der genau diesen Fall nachstellte).
    anfang = text.lstrip()[:200].lower()
    if anfang.startswith(("<!doctype html", "<html")):
        return {}, [], "HTML-Seite, kein RSS-Feed"

    try:
        wurzel = ET.fromstring(text)
    except ET.ParseError as e:
        return {}, [], f"kein gueltiges XML ({e})"

    kanal = wurzel.find("channel")
    if kanal is None:
        if wurzel.tag.endswith("feed"):
            return {}, [], "Atom-Feed - wird noch nicht gelesen"
        return {}, [], "kein <channel> - das ist kein RSS-Feed"

    kopf = {"titel": _text(kanal, "title"),
            "beschreibung": _text(kanal, "description")}

    folgen = []
    for eintrag in kanal.findall("item"):
        anhang = eintrag.find("enclosure")
        url = (anhang.get("url") or "").strip() if anhang is not None else ""
        art = (anhang.get("type") or "").strip() if anhang is not None else ""
        dauer = None
        for marke in ("{http://www.itunes.com/dtds/podcast-1.0.dtd}duration",
                      "duration"):
            gefunden = eintrag.find(marke)
            if gefunden is not None:
                dauer = _dauer_in_sekunden(gefunden.text)
                break
        folgen.append({
            "titel": _text(eintrag, "title"),
            "audio": url,
            "art": art,
            "datum": _datum(_text(eintrag, "pubDate")),
            "dauer": dauer,
        })

    mit_datum = [f for f in folgen if f["datum"]]
    if len(mit_datum) == len(folgen) and folgen:
        folgen.sort(key=lambda f: f["datum"], reverse=True)
    return kopf, folgen, ""


def neueste_folge(folgen, mindestdauer=0):
    """Die neueste Folge MIT Audio - und lang genug.

    Nicht einfach die erste: Manche Feeds mischen Text- und
    Audiobeitraege, und ein Eintrag ohne <enclosure> ist fuer DialOS
    nichts wert - er wuerde nur schweigen.

    MINDESTDAUER, der Befund vom 2026-10-08: Sieben der dreissig
    ausgewaehlten Podcast-Feeds mischen Einzelbeitraege mit ganzen
    Sendungen. "Deutschlandfunk Hintergrund" reicht von 1 bis 19
    Minuten, der WDR-Hoerspiel-Speicher von 6 bis 74. Bei der Messung
    war die neueste Folge jedes Mal eine richtige Sendung - aber beim
    naechsten Abruf kann es ein Einminueter sein, und dann sagt der
    Nutzer "hoerspiel speicher" und bekommt eine Ankuendigung. Fuer
    jemanden, der den Bildschirm nicht sieht, ist das von einem Fehler
    nicht zu unterscheiden.

    EINE FOLGE OHNE DAUERANGABE WIRD NICHT VERWORFEN. Zwei der
    geprueften Feeds (SR2, hr2 Doppelkopf) liefern gar kein
    itunes:duration. Wer am fehlenden Feld aussortiert, loescht den
    ganzen Podcast - also gilt im Zweifel "lang genug". Der Filter soll
    Schnipsel abweisen, die sich selbst als kurz ausweisen, nicht Feeds
    bestrafen, die ihre Dauer verschweigen.

    IST KEINE FOLGE LANG GENUG, kommt die neueste mit Audio zurueck.
    Lieber eine zu kurze Sendung als Stille: Der Nutzer hoert dann
    etwas und kann selbst urteilen, statt vor einem stummen Geraet zu
    sitzen - dasselbe Prinzip wie bei den Ansagen, die einen Zustand
    nennen statt zu schweigen.
    """
    mit_audio = [f for f in folgen if f["audio"]]
    if not mit_audio:
        return None
    if mindestdauer:
        for folge in mit_audio:
            dauer = folge.get("dauer")
            if dauer is None or dauer >= mindestdauer:
                return folge
    return mit_audio[0]


def feed_pruefen(url, gruendlich=True, mindestdauer=0):
    """Ein Feed von vorn bis hinten. Gibt einen Bericht als dict zurueck.

    Die Reihenfolge der Pruefungen ist die der Fehlerhaeufigkeit: zuerst
    ueberhaupt erreichbar, dann ein Feed, dann Audio darin, dann aktuell,
    dann spielt es wirklich.

    `mindestdauer` wird durchgereicht, damit die Pruefung DIESELBE Folge
    ansieht, die der Nutzer spaeter hoert. Ohne das prueft man einen
    Einminueter und spielt eine Stunde - oder umgekehrt.
    """
    bericht = {"url": url, "laeuft": False, "problem": "", "titel": "",
               "folgen": 0, "mit_audio": 0, "neueste": None,
               "alter_tage": None, "dauer": None, "audio": None}

    text, meldung = feed_holen(url)
    if meldung:
        bericht["problem"] = meldung
        return bericht

    kopf, folgen, meldung = feed_lesen(text)
    if meldung:
        bericht["problem"] = meldung
        return bericht

    bericht["titel"] = kopf.get("titel", "")
    bericht["folgen"] = len(folgen)
    bericht["mit_audio"] = sum(1 for f in folgen if f["audio"])

    if not folgen:
        bericht["problem"] = "Feed ohne Eintraege"
        return bericht
    if not bericht["mit_audio"]:
        # DER BEFUND VOM 2026-10-05, der diese Datei veranlasst hat.
        bericht["problem"] = (f"{len(folgen)} Eintraege, aber kein Audio - "
                              "das sind Textartikel, kein Podcast")
        return bericht

    folge = neueste_folge(folgen, mindestdauer)
    bericht["neueste"] = folge["titel"]
    bericht["audio"] = folge["audio"]
    bericht["dauer"] = folge["dauer"]
    if folge["datum"]:
        bericht["alter_tage"] = (time.time() - folge["datum"]) / 86400

    if bericht["alter_tage"] is not None and bericht["alter_tage"] > TOT_NACH_TAGEN:
        bericht["problem"] = (f"neueste Folge ist {bericht['alter_tage']:.0f} "
                              "Tage alt - der Feed schlaeft")
        return bericht

    if not gruendlich:
        bericht["laeuft"] = True
        return bericht

    try:
        rs = sender_modul()
    except Exception as e:                      # noqa: BLE001
        bericht["problem"] = f"Audiopruefung nicht moeglich: {e}"
        return bericht

    audio, problem = rs.dekodieren(folge["audio"])
    if audio is None:
        bericht["problem"] = problem or "Audiodatei liess sich nicht lesen"
        return bericht
    bericht["audio_daten"] = audio
    bericht["laeuft"] = True
    return bericht


def bericht_zeigen(bericht):
    url = bericht["url"]
    sagen(f"{url}")
    if bericht["titel"]:
        sagen(f"  Titel:   {bericht['titel']}")
    sagen(f"  Folgen:  {bericht['folgen']} "
          f"({bericht['mit_audio']} mit Audio)")
    if bericht["neueste"]:
        alter = ("" if bericht["alter_tage"] is None
                 else f", {bericht['alter_tage']:.1f} Tage alt")
        sagen(f"  Neueste: {bericht['neueste']}{alter}")
    if bericht["dauer"]:
        minuten, sekunden = divmod(bericht["dauer"], 60)
        lang = ("" if bericht["dauer"] <= KURZ_BIS_SEKUNDEN
                else "  (laenger als eine Kurznachrichten-Sendung)")
        sagen(f"  Dauer:   {minuten}:{sekunden:02d}{lang}")
    if bericht.get("audio_daten"):
        a = bericht["audio_daten"]
        sagen(f"  Ton:     {a.get('codec')} {a.get('kbps')} kbit/s")
    if bericht["laeuft"]:
        sagen("  ERGEBNIS: brauchbar")
    else:
        sagen(f"  ERGEBNIS: NICHT brauchbar - {bericht['problem']}")
    sagen()


def main():
    zerleger = argparse.ArgumentParser(
        description="RSS-Feeds fuer die DialOS-Medienliste pruefen.")
    zerleger.add_argument("befehl", choices=["pruefen", "neueste"])
    zerleger.add_argument("adressen", nargs="+")
    zerleger.add_argument("--schnell", action="store_true",
                          help="ohne ffprobe - nur Feed und Datum")
    args = zerleger.parse_args()

    gut = 0
    for url in args.adressen:
        bericht = feed_pruefen(url, gruendlich=not args.schnell)
        if args.befehl == "neueste":
            if bericht["audio"]:
                sagen(bericht["audio"])
            else:
                fehler(f"{url}: {bericht['problem']}")
        else:
            bericht_zeigen(bericht)
        gut += 1 if bericht["laeuft"] else 0

    if args.befehl == "pruefen":
        sagen(f"{gut} von {len(args.adressen)} brauchbar.")
    return 0 if gut == len(args.adressen) else 1


if __name__ == "__main__":
    sys.exit(main())
