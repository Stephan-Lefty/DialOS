#!/usr/bin/env python3
"""Programme auf Zuruf oeffnen - "Postfach oeffnen", "neue E-Mail schreiben".

WARUM ES DAS GIBT (Stephan, 2026-09-21): "Wir muessen doch sowieso eine Liste
von Befehlen machen, die dann die Programme startet." Bis hierher konnte DialOS
alles selbst - vorlesen, diktieren, drucken, suchen - aber kein Programm
oeffnen. Fuer einen sehenden Helfer am selben Geraet ist das der fehlende
Handgriff, und fuer den Nutzer ist es der Weg zu allem, was DialOS (noch) nicht
per Sprache kann.

ES GIBT EINEN ZWEITEN GRUND, UND DER IST NEU SEIT HEUTE: Entwuerfe und Kontakte
gehen jetzt ueber die Thunderbird-Erweiterung, nicht mehr in dessen Dateien
(siehe dialos-thunderbird-bruecke.py). Damit ist ein GESCHLOSSENER Thunderbird
der einzige Fall, in dem etwas vorgemerkt werden muss. "Postfach oeffnen" loest
genau das auf: Thunderbird startet, die Bruecke arbeitet die Warteschlange ab,
der Entwurf liegt im Postfach.

EINE LISTE, NICHT ZWEI. Die Saetze stehen hier und nur hier;
dialos-sprachbefehl-desktop.py liest sie beim Start aus dieser Datei. Eine
zweite Liste in der Grammatik liefe beim naechsten Programm auseinander, und
zwar unbemerkt - dieselbe Ueberlegung wie bei den Erweiterungen.

SCHLIESSEN GIBT ES SEIT DEM 2026-09-21 AUCH (Stephan: "wir muessen noch den
Befehl fuer das Schliessen einbauen"). Hier stand vorher das Gegenteil, mit der
Sorge um ungespeicherte Arbeit eines sehenden Helfers. Die Sorge bleibt richtig
- die Antwort darauf ist aber nicht, den Befehl wegzulassen, sondern ihn
vorsichtig zu bauen:

  * RUECKFRAGE wie bei jedem zerstoerenden Befehl ("Soll ich das Postfach
    schliessen? Sage ja oder nein."), mit ja_oder_nein aus dialos-notiz.py -
    in dieser Funktion stecken drei teuer bezahlte Lehren, sie wird nicht
    nachgebaut.
  * SIGTERM, NIEMALS SIGKILL. SIGTERM ist die Bitte "raeum auf und geh" -
    Thunderbird speichert dabei, was zu speichern ist. SIGKILL waere genau
    der Datenverlust, wegen dem der Befehl erst nicht existieren sollte.
  * WER NICHT GEHT, DARF BLEIBEN. Fragt das Programm noch etwas, beendet es
    sich nicht - dann sagt DialOS genau das, statt nachzutreten.
  * VORHER SICHERN, WAS OFFEN IST - und das war kein Vorsatz, sondern eine
    Messung (2026-09-21): Thunderbird fragt bei SIGTERM NICHT nach. Es geht
    nach EINER Sekunde zu, und ein angefangenes Schreibfenster ist lautlos
    weg; der Entwurfsordner wuchs im Versuch um kein einziges Byte. Die
    urspruengliche Sorge ("Schliessen koennte die Arbeit eines sehenden
    Helfers wegwerfen") war also berechtigt, und die Rueckfrage allein haette
    sie nicht aufgefangen. Deshalb fragt DialOS vor dem Schliessen die
    Bruecke, was an Schreibfenstern offen steht, legt es als Entwurf ab und
    SAGT, wie viele es waren.

DAS FENSTER NACH VORN ZU HOLEN, BRAUCHT DIE .desktop-DATEI - GEMESSEN AM
2026-09-21. Hier stand vorher, ein zweiter Start hebe das vorhandene Fenster
von selbst. Stephan hat das Gegenteil gesehen: "Wenn Thunderbird bereits offen
ist, dann wird bei Postfach oeffnen das vorhandene Fenster nicht nach vorn
geholt."

WARUM, UND WARUM DAS KEIN FEHLER VON THUNDERBIRD IST: Unter Wayland darf ein
fremder Prozess kein Fenster nach vorn holen - das ist ausdruecklich
unterbunden, damit kein Hintergrundprogramm dem Nutzer ins Bild springt. Heben
darf sich nur die Anwendung selbst, und nur mit einem Aktivierungs-Token
(XDG_ACTIVATION_TOKEN), das ihr beim Start mitgegeben wird. Ein Token gibt es
aber nur, wenn ueber die .desktop-Datei gestartet wird - "/usr/bin/thunderbird"
von Hand aufgerufen bekommt keins. Genau das stand hier.

AUCH MIT DER .desktop-DATEI GEHT ES NICHT - ZWEIMAL GEMESSEN AM 2026-09-21.

Erster Lauf: "Fenster kommt nicht nach vorne, es erscheint nur oben mittig ein
Hinweis von Gnome." Dieser Lauf zaehlte nicht, und das Eingestaendnis gehoert
hierher: Thunderbird war dabei ZU - die Prozessliste zeigte hinterher, dass
der Aufruf es erst gestartet hatte. Gemessen war damit nur der Fokus-Schutz
beim Neustart, nicht das Heben eines vorhandenen Fensters. Ich hatte die
Begruendung schon geschrieben, bevor das auffiel.

Zweiter Lauf, mit LAUFENDEM Thunderbird und derselbe Aufruf: "Fenster bleibt
hinten." Damit steht es: Auch mit Aktivierungs-Token hebt sich das vorhandene
Fenster nicht. GNOME meldet stattdessen "Thunderbird ist bereit" und
ueberlaesst dem Nutzer den Klick - das ist der Schutz davor, dass Programme
sich in den Vordergrund draengen, und er greift auch hier.

DAMIT IST DER PUNKT ERLEDIGT, NICHT OFFEN. Es gibt keinen dritten Weg: wmctrl
und xdotool sind nicht installiert und waeren unter Wayland wirkungslos, die
GNOME-Schnittstelle ist gesperrt, und ein Fenster von aussen zu heben ist dort
ausdruecklich nicht vorgesehen.

"gio launch" BLEIBT TROTZDEM, aus einem anderen Grund: Ueber die
.desktop-Datei gestartet laeuft das Programm in seiner EIGENEN systemd-Einheit
und nicht in der des Sprachdienstes - genau der Fehler, der beim
Bildschirmfoto drei Wochen unbemerkt blieb (CLAUDE.md, Regel vom 2026-09-14).

WAS DER NUTZER STATTDESSEN BEKOMMT: eine Auskunft. Laeuft das Programm schon,
sagt DialOS das ("Das Postfach ist schon offen.") - fuer jemanden, der den
Bildschirm nicht sieht, ist der Zustand die Antwort, nicht das Fenster. Der
sehende Helfer daneben sieht GNOMEs Hinweis.

"gio launch" uebergibt Argumente als DATEINAMEN, nicht als Schalter - fuer
"-compose", "-calendar" und "-addressbook" bleibt der direkte Aufruf. Dort
entsteht ohnehin ein NEUES Fenster, und ein neues kommt nach vorn.

Aufruf:
  dialos-programm.py "postfach öffnen"      # startet und sagt es an
  dialos-programm.py --liste                # alle Saetze, fuer die Doku
"""

import importlib.util
import os
import signal
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
GIO = "/usr/bin/gio"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-programm.log")

# Satz -> was passiert. "befehl" ist die Programmzeile, "ansage" das, was der
# Nutzer hoert, "fehlt" der Satz fuer den Fall, dass das Programm nicht
# installiert ist (bei einem Kundengeraet ohne Radio zum Beispiel).
#
# DIE ZWECKE STAMMEN AUS docs/anwendungen.md - dort steht, WARUM es dieses
# Programm ist und kein anderes. Hier steht nur, wie man es ruft.
PROGRAMME = {
    "postfach öffnen": {
        "offen": "Das Postfach ist schon offen.",
        "befehl": ["/usr/bin/thunderbird"],
        "fenster": "/usr/share/applications/thunderbird.desktop",
        "ansage": "Ich öffne das Postfach.",
    },
    # "NEUE E-MAIL SCHREIBEN" GEHOERT SEIT DEM 2026-09-21 NICHT MEHR HIERHER.
    # Der Satz oeffnete ein leeres Verfassen-Fenster - fuer jemanden, der den
    # Bildschirm nicht sieht, ist das ein leerer Raum. Jetzt fuehrt er den
    # Dialog: Empfaenger, Betreff, Text, Bestaetigung, senden
    # (dialos-mail-schreiben.py, angemeldet als Erweiterung DialOS-Mail). Wer
    # sehen kann, oeffnet das Fenster in Thunderbird selbst.
    "kalender öffnen": {
        "befehl": ["/usr/bin/thunderbird", "-calendar"],
        "ansage": "Ich öffne den Kalender.",
    },
    "kontakte öffnen": {
        "befehl": ["/usr/bin/thunderbird", "-addressbook"],
        "ansage": "Ich öffne die Kontakte.",
    },
    "internet öffnen": {
        "offen": "Das Internet ist schon offen.",
        "fenster": "/usr/share/applications/firefox-esr.desktop",
        "befehl": ["/usr/bin/firefox-esr"],
        "ansage": "Ich öffne das Internet.",
    },
    "browser öffnen": {
        "offen": "Der Browser ist schon offen.",
        "fenster": "/usr/share/applications/firefox-esr.desktop",
        "befehl": ["/usr/bin/firefox-esr"],
        "ansage": "Ich öffne den Browser.",
    },
    "musik öffnen": {
        "offen": "Die Musik läuft schon.",
        "fenster": "/usr/share/applications/org.gnome.Rhythmbox3.desktop",
        "befehl": ["/usr/bin/rhythmbox"],
        "ansage": "Ich öffne die Musik.",
    },
    "radio öffnen": {
        "offen": "Das Radio läuft schon.",
        "fenster": "/usr/share/applications/de.haeckerfelix.Shortwave.desktop",
        "befehl": ["/usr/bin/shortwave"],
        "ansage": "Ich öffne das Radio.",
    },
}

# Nach dem Start von Thunderbird arbeitet die Bruecke Vorgemerktes ab. Der
# Nutzer soll das hoeren, wenn etwas wartet - sonst wundert er sich, warum
# ploetzlich ein Entwurf da ist.
WARTESCHLANGE = os.path.join(os.path.expanduser("~"), ".config", "dialos",
                             "mail-entwuerfe.json")


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    try:
        subprocess.run([SAY, text], timeout=60)
    except (OSError, subprocess.SubprocessError) as fehler:
        melde(f"Ansage fehlgeschlagen: {fehler}")


def vorgemerkte_entwuerfe():
    """Wie viele Entwuerfe warten? 0, wenn keine Warteschlange da ist."""
    try:
        import json
        with open(WARTESCHLANGE, encoding="utf-8") as f:
            return len(json.load(f))
    except (OSError, ValueError):
        return 0


# Was wieder zugeht. Getrennt von PROGRAMME, weil nicht jedes Programm, das
# sich oeffnen laesst, auch per Sprache zugehen muss - und weil hier jeder
# Eintrag drei Ansagen braucht statt einer.
SCHLIESSEN = {
    "postfach schließen": {
        "programm": "/usr/bin/thunderbird",
        "frage": "Soll ich das Postfach schließen? Sage ja oder nein.",
        "zu": "Das Postfach ist zu.",
        "nicht_offen": "Das Postfach ist gar nicht offen.",
        "bleibt": "Das Postfach ist noch offen. Vielleicht fragt Thunderbird "
                  "nach etwas, das noch nicht gespeichert ist.",
    },
    "internet schließen": {
        "programm": "/usr/bin/firefox-esr",
        "frage": "Soll ich das Internet schließen? Sage ja oder nein.",
        "zu": "Das Internet ist zu.",
        "nicht_offen": "Das Internet ist gar nicht offen.",
        "bleibt": "Der Browser ist noch offen. Vielleicht fragt er nach etwas.",
    },
    "browser schließen": {
        "programm": "/usr/bin/firefox-esr",
        "frage": "Soll ich den Browser schließen? Sage ja oder nein.",
        "zu": "Der Browser ist zu.",
        "nicht_offen": "Der Browser ist gar nicht offen.",
        "bleibt": "Der Browser ist noch offen. Vielleicht fragt er nach etwas.",
    },
    "musik ausschalten": {
        "programm": "/usr/bin/rhythmbox",
        "frage": "Soll ich die Musik ausschalten? Sage ja oder nein.",
        "zu": "Die Musik ist aus.",
        "nicht_offen": "Es läuft gerade keine Musik.",
        "bleibt": "Die Musik läuft noch.",
    },
    "radio ausschalten": {
        "programm": "/usr/bin/shortwave",
        "frage": "Soll ich das Radio ausschalten? Sage ja oder nein.",
        "zu": "Das Radio ist aus.",
        "nicht_offen": "Das Radio läuft gar nicht.",
        "bleibt": "Das Radio läuft noch.",
    },
}

NOTIZ_SKRIPT = "/usr/local/bin/dialos-notiz.py"
BRUECKE_SKRIPT = "/usr/local/bin/dialos-thunderbird-bruecke.py"
# So lange wird nach dem SIGTERM gewartet, bevor DialOS sagt, dass das
# Programm noch da ist. Thunderbird braucht beim Beenden ein paar Sekunden,
# weil es seine Ordner schreibt.
BEENDEN_GEDULD_S = 12.0


def ja_oder_nein(frage):
    """Die Rueckfrage aus dialos-notiz.py - nicht nachgebaut, sondern geholt.

    WARUM GEHOLT: In dieser Funktion stecken drei Fehler, die schon einmal Geld
    gekostet haben - das Sprachmodell muss VOR der Frage geladen sein (sonst
    faellt das "ja" in die Ladeluecke), das Mikrofon muss waehrend der Frage
    schon offen sein (sonst fehlen die ersten Sekunden), und die eigene Ansage
    darf nicht mitgehoert werden (sonst beantwortet sich das System selbst).
    Eine zweite Fassung davon waere eine zweite Stelle, an der diese drei
    Fehler wieder entstehen koennen.
    """
    try:
        spec = importlib.util.spec_from_file_location("dialos_notiz", NOTIZ_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.ja_oder_nein(frage)
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"Rückfrage nicht möglich: {fehler}")
        return None


def bruecke_fragen(bitte):
    """Eine Bitte an Thunderbird - {} , wenn die Bruecke nicht da ist."""
    try:
        spec = importlib.util.spec_from_file_location("dialos_bruecke", BRUECKE_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.fragen(bitte, zeitgrenze=20.0)
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"Brücke nicht erreichbar: {fehler}")
        return {}


def offenes_sichern():
    """Vor dem Schliessen: angefangene E-Mails als Entwurf ablegen.

    Gibt den Satz zurueck, den der Nutzer dazu hoeren soll - oder "".

    DAS IST DIE ANTWORT AUF EINE MESSUNG, NICHT AUF EINE VERMUTUNG: Thunderbird
    beendet sich auf SIGTERM binnen einer Sekunde und fragt nicht nach. Alles,
    was in einem Schreibfenster steht und nicht gespeichert ist, waere weg -
    und zwar ohne ein Geraeusch.
    """
    stand = bruecke_fragen({"befehl": "schreibfenster"})
    anzahl = stand.get("anzahl", 0) if stand.get("ok") else 0
    if not anzahl:
        return ""
    ergebnis = bruecke_fragen({"befehl": "schreibfenster sichern"})
    gesichert = ergebnis.get("gesichert", 0)
    melde(f"vor dem Schliessen gesichert: {gesichert} von {anzahl} Schreibfenster(n)")
    if gesichert == 0:
        # Lieber gar nicht schliessen als etwas wegwerfen: Der Aufrufer bricht
        # daraufhin ab (siehe schliessen()).
        return "FEHLER"
    if gesichert == 1:
        return "Eine angefangene E-Mail lege ich noch als Entwurf ab."
    return f"{gesichert} angefangene E-Mails lege ich noch als Entwürfe ab."


# Hoechstens so lange wird auf das Nachtragen gewartet - siehe
# nachholen_abwarten(). Als FESTE Wartezeit stand hier zuerst 14 Sekunden, und
# Stephan hat es am 2026-09-21 sofort gemerkt: "Punkt 1 die Rückmeldung kam
# sehr spät." Im Protokoll waren es 18 Sekunden Stille zwischen "Ich öffne das
# Postfach" und dem Hinweis - 4 davon brauchte Thunderbird, 14 war mein
# Warten auf etwas, das gar nicht anstand.
NACHHOLEN_GRENZE_S = 25
BRUECKE_GEDULD_S = 40
# Hoechstens so viele Entwuerfe werden einzeln durchgefragt. Beim ersten Lauf
# am 2026-09-21 lagen fuenf aus den Tests im Postfach, und DialOS fragte jeden
# einzeln ab - vier Fragen, bevor Stephan zu dem kam, was er eigentlich wollte.
# Wer mehr Entwuerfe liegen hat, will sie nicht per Sprache sortieren.
EINZELN_HOECHSTENS = 3


def entwuerfe_ansagen(beim_oeffnen):
    """Auf liegende Entwuerfe hinweisen und fragen, was damit geschehen soll.

    WARUM (Stephan, 2026-09-21): "Wir muessen den Nutzer hinweisen, wenn er
    Thunderbird schliesst und/oder oeffnet, dass noch Entwuerfe vorhanden sind
    und natuerlich fragen, wie man weiter damit umgehen soll."

    Der Punkt ist neu entstanden, weil DialOS seit heute selbst Entwuerfe
    ablegt - beim Antworten, beim Weiterleiten, beim Vormerken und beim
    Schliessen mit offenem Schreibfenster. Wer den Bildschirm nicht sieht,
    merkt davon sonst nie etwas: Ein Entwurf ist das einzige Ergebnis in
    DialOS, das NICHT von selbst irgendwo ankommt.

    GEFRAGT WIRD EINZELN UND NUR AUF WUNSCH. Ein "soll ich alle verschicken?"
    waere der gefaehrlichste Satz im System - ein einziges missverstandenes
    "ja" schickte halbfertige Texte an echte Leute.
    """
    stand = bruecke_fragen({"befehl": "entwuerfe"})
    if not stand.get("ok"):
        melde(f"Entwürfe nicht abfragbar: {stand.get('fehler')}")
        return
    entwuerfe = stand.get("entwuerfe") or []
    if not entwuerfe:
        melde("keine Entwürfe")
        return
    anzahl = len(entwuerfe)
    wieviel = ("Ein Entwurf liegt" if anzahl == 1
               else f"{anzahl} Entwürfe liegen")
    wo = "im Postfach" if beim_oeffnen else "noch im Postfach"
    # HOECHSTENS DREI BETREFFZEILEN. Bei zwanzig Entwuerfen waere die Aufzaehlung
    # laenger als alles, was der Nutzer danach noch tun will.
    namen = []
    for eintrag in entwuerfe[:3]:
        betreff = (eintrag.get("betreff") or "ohne Betreff").strip()
        an = (eintrag.get("an") or "").strip()
        namen.append(f"{betreff} an {an}" if an else betreff)
    aufzaehlung = "; ".join(namen)
    if anzahl > 3:
        aufzaehlung += f"; und {anzahl - 3} weitere"
    sprich(f"{wieviel} {wo}: {aufzaehlung}.")
    if ja_oder_nein("Soll ich einen davon verschicken? Sage ja oder nein.") is not True:
        sprich("Gut, sie bleiben liegen.")
        melde(f"{anzahl} Entwürfe, nichts gesendet")
        return
    gefragt = 0
    ohne_empfaenger = 0
    for eintrag in entwuerfe:
        betreff = (eintrag.get("betreff") or "ohne Betreff").strip()
        an = (eintrag.get("an") or "").strip()
        # OHNE EMPFAENGER GAR NICHT ERST FRAGEN: Ein solcher Entwurf laesst sich
        # nicht verschicken, und die Frage danach ist fuer den Nutzer nicht zu
        # beantworten - er hoert "ohne Betreff verschicken?" und weiss nicht
        # einmal, um welche E-Mail es geht. Am 2026-09-21 genau so passiert.
        if not an:
            ohne_empfaenger += 1
            continue
        if gefragt >= EINZELN_HOECHSTENS:
            break
        gefragt += 1
        if ja_oder_nein(f"{betreff} an {an} verschicken? "
                        "Sage ja oder nein.") is not True:
            continue
        antwort = bruecke_fragen({"befehl": "entwurf senden", "id": eintrag.get("id")})
        if antwort.get("ok"):
            sprich("Ist unterwegs.")
            melde(f"Entwurf {eintrag.get('id')} gesendet: {betreff!r}")
        else:
            sprich("Das hat nicht geklappt. Der Entwurf bleibt liegen.")
            melde(f"Entwurf {eintrag.get('id')} nicht gesendet: {antwort.get('fehler')}")
    if ohne_empfaenger:
        sprich("Ein angefangener Entwurf hat keinen Empfänger. Den lasse ich liegen."
               if ohne_empfaenger == 1 else
               f"{ohne_empfaenger} angefangene Entwürfe haben keinen Empfänger. "
               "Die lasse ich liegen.")
    uebrig = len([e for e in entwuerfe if (e.get("an") or "").strip()]) - gefragt
    if uebrig > 0:
        sprich(f"{uebrig} weitere lasse ich liegen. In Thunderbird kannst Du sie "
               "in Ruhe durchgehen.")


def nachholen_abwarten():
    """Warten, bis die Warteschlange leer ist - aber nur, wenn eine da ist.

    WARUM NICHT EINFACH EINE FESTE PAUSE: Weil sie in dem Fall falsch ist, der
    fast immer vorliegt. Vorgemerkt wird nur, wenn DialOS bei geschlossenem
    Thunderbird einen Entwurf ablegen wollte - sonst ist die Datei gar nicht
    da, und es gibt nichts abzuwarten. Die Datei verschwindet, sobald die
    Bruecke sie abgearbeitet hat; das ist ein genaueres Signal als jede Zahl.
    """
    if not os.path.isfile(WARTESCHLANGE):
        return
    melde("Warteschlange ist noch da - warte aufs Nachtragen")
    ende = time.time() + NACHHOLEN_GRENZE_S
    while time.time() < ende and os.path.isfile(WARTESCHLANGE):
        time.sleep(0.5)


def auf_bruecke_warten(geduld=BRUECKE_GEDULD_S):
    """Wartet, bis Thunderbird die Bruecke gestartet hat. True, wenn sie da ist."""
    ende = time.time() + geduld
    while time.time() < ende:
        if bruecke_fragen({"befehl": "hallo"}).get("ok"):
            return True
        time.sleep(1.0)
    return False


def prozesse(programm):
    """Die Prozesse des Programms - eigene, ohne Hilfsprozesse.

    UEBER /proc UND NICHT UEBER pgrep, seit dem zweiten Anlauf am 2026-09-21:
    Ein pgrep-Muster sucht in Befehlszeilen, und dabei findet es auch die
    Befehlszeile der Suche selbst - beim Probieren meldete "/thunderbird"
    einen laufenden Thunderbird, obwohl keiner lief. Hier wird stattdessen
    genau hingesehen: erstes Argument, eigener Benutzer, keine Hilfsprozesse.

    "-contentproc" schliesst die Unterprozesse von Thunderbird und Firefox aus.
    Sie gehoeren zum selben Programm, aber ihnen ein SIGTERM zu schicken waere,
    als zoege man einem Haus einzelne Waende weg - das Hauptprogramm raeumt sie
    selbst ab, sobald es geht.
    """
    name = os.path.basename(programm)
    meine = os.getuid()
    gefunden = []
    for eintrag in os.listdir("/proc"):
        if not eintrag.isdigit():
            continue
        ordner = os.path.join("/proc", eintrag)
        try:
            if os.stat(ordner).st_uid != meine:
                continue
            with open(os.path.join(ordner, "cmdline"), "rb") as f:
                argv = f.read().split(b"\0")
        except OSError:
            continue
        if not argv or not argv[0]:
            continue
        if b"-contentproc" in argv:
            continue
        erstes = argv[0].decode("utf-8", errors="replace")
        if not erstes.startswith(("/usr/bin/", "/usr/lib/")):
            continue
        if os.path.basename(erstes) in (name, name + "-bin"):
            gefunden.append(int(eintrag))
    return gefunden


def schliessen(satz):
    """Ein Programm bitten, sich zu beenden. True, wenn es weg ist."""
    eintrag = SCHLIESSEN.get(satz)
    if eintrag is None:
        return False
    pids = prozesse(eintrag["programm"])
    if not pids:
        sprich(eintrag["nicht_offen"])
        melde(f"{satz!r}: laeuft nicht")
        return False
    if ja_oder_nein(eintrag["frage"]) is not True:
        # None (nichts verstanden) wird wie nein behandelt - bei etwas, das
        # sich nicht rueckgaengig machen laesst, ist Nichtstun die richtige
        # Auslegung eines unklaren Wortes.
        sprich("Gut, ich lasse es offen.")
        melde(f"{satz!r}: abgelehnt oder nichts verstanden")
        return False
    # NUR BEI THUNDERBIRD, UND NUR WEIL ES DIE BRUECKE GIBT: Was Firefox oder
    # Rhythmbox offen haben, kann DialOS nicht sichern - dort ist SIGTERM alles,
    # was geht, und beide fragen selbst nach, wenn etwas offen ist.
    if "thunderbird" in eintrag["programm"]:
        # VOR DEM SCHLIESSEN HINWEISEN, NICHT DANACH: Ist Thunderbird erst zu,
        # laesst sich kein Entwurf mehr verschicken - die Bruecke ist dann weg.
        entwuerfe_ansagen(beim_oeffnen=False)
        # EIGENER NAME, NICHT "satz" (Fehler vom 2026-09-21): Die erste Fassung
        # ueberschrieb damit den Befehlssatz - im Protokoll stand danach
        # "'Eine angefangene E-Mail lege ich noch als Entwurf ab.': SIGTERM an
        # [44557]" statt "'postfach schliessen': SIGTERM an [44557]". Gelaufen
        # ist alles richtig, aber das Protokoll log: Es nannte als Befehl eine
        # Ansage. Ein Protokoll ist die Beweiskette - steht dort der falsche
        # Befehl, fuehrt die naechste Fehlersuche in die Irre.
        hinweis = offenes_sichern()
        if hinweis == "FEHLER":
            sprich("Es ist noch eine E-Mail offen, die ich nicht speichern "
                   "konnte. Ich lasse das Postfach offen.")
            melde(f"{satz!r}: abgebrochen, Sichern fehlgeschlagen")
            return False
        if hinweis:
            sprich(hinweis)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as fehler:
            melde(f"  SIGTERM an {pid} fehlgeschlagen: {fehler}")
    melde(f"{satz!r}: SIGTERM an {pids}")
    # AUCH DER GUTE AUSGANG GEHOERT INS PROTOKOLL (2026-09-21). Beim ersten
    # echten Lauf stand dort nur das SIGTERM - ob das Programm danach wirklich
    # weg war und was der Nutzer gehoert hat, liess sich hinterher nur noch
    # erraten. Ein Protokoll, das nur Fehler kennt, beantwortet die haeufigste
    # Frage nicht: "Hat es funktioniert?"
    begonnen = time.time()
    ende = begonnen + BEENDEN_GEDULD_S
    while time.time() < ende:
        if not prozesse(eintrag["programm"]):
            melde(f"{satz!r}: beendet nach {time.time() - begonnen:.1f} s")
            sprich(eintrag["zu"])
            return True
        time.sleep(0.5)
    sprich(eintrag["bleibt"])
    melde(f"{satz!r}: laeuft nach {BEENDEN_GEDULD_S:.0f} s immer noch")
    return False


def laeuft_schon(programm):
    """Laeuft das Programm schon? Nur fuer die Ansage, nicht fuer den Start.

    DIESELBE PRUEFUNG WIE BEIM SCHLIESSEN (prozesse()), mit Absicht: Zwei
    verschiedene Arten zu fragen "laeuft es?" wuerden irgendwann verschieden
    antworten, und dann sagt DialOS "ist schon offen" und schliesst im
    naechsten Satz nichts - oder umgekehrt.

    NACH DEM FENSTER ZU FRAGEN GEHT NICHT: Fenster sind unter Wayland von
    aussen nicht abfragbar - dieselbe Grenze, die das Heben verhindert. Der
    Prozess ist es sehr wohl, und fuer "ist es offen?" reicht er.
    """
    gefunden = prozesse(programm)
    if gefunden:
        melde(f"{os.path.basename(programm)} laeuft schon (PID {gefunden[0]})")
    return bool(gefunden)


def starten(satz):
    """Das Programm zum Satz starten. True, wenn es losgelaufen ist."""
    if satz in SCHLIESSEN:
        return schliessen(satz)
    eintrag = PROGRAMME.get(satz)
    if eintrag is None:
        melde(f"Kein Programm zu {satz!r}")
        return False
    programm = eintrag["befehl"][0]
    if not os.path.exists(programm):
        melde(f"{programm} ist nicht installiert")
        sprich(eintrag.get("fehlt", "Dieses Programm ist auf dem Gerät nicht "
                                     "eingerichtet."))
        return False
    ansage = eintrag["ansage"]
    lief_schon = bool(eintrag.get("fenster")) and laeuft_schon(programm)
    # NUR BEI DEN SAETZEN OHNE SCHALTER: "Kalender öffnen" oeffnet ein Fenster
    # in einem schon laufenden Thunderbird, da waere "ist schon offen" falsch.
    if lief_schon:
        ansage = eintrag.get("offen", "Das Programm läuft schon.")
    wartende = vorgemerkte_entwuerfe() if "thunderbird" in programm else 0
    if wartende:
        ansage += (" Ich trage dabei den vorgemerkten Entwurf ein."
                   if wartende == 1
                   else f" Ich trage dabei {wartende} vorgemerkte Entwürfe ein.")
    sprich(ansage)
    # UEBER DIE .desktop-DATEI, WENN ES EINE GIBT - siehe oben: nur so bekommt
    # die Anwendung das Aktivierungs-Token, mit dem sie ihr vorhandenes Fenster
    # nach vorn holen darf.
    zeile = eintrag["befehl"]
    fenster = eintrag.get("fenster")
    if fenster and os.path.exists(fenster) and os.path.exists(GIO):
        zeile = [GIO, "launch", fenster]
    try:
        # start_new_session: Das Programm soll weiterlaufen, wenn die
        # Sprachsteuerung neu startet - es haengt sonst an deren Prozessgruppe.
        subprocess.Popen(zeile, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        melde(f"Start fehlgeschlagen ({programm}): {fehler}")
        sprich("Das Programm ließ sich nicht öffnen.")
        return False
    melde(f"{satz!r} -> {' '.join(zeile)}")
    # NUR BEIM POSTFACH, NICHT BEI KALENDER ODER KONTAKTEN: Wer den Kalender
    # aufmacht, will von Entwuerfen nichts hoeren - der Hinweis gehoert dorthin,
    # wo der Nutzer ohnehin an E-Mails denkt.
    if satz == "postfach öffnen":
        if auf_bruecke_warten():
            # ERST NACH DEM NACHHOLEN FRAGEN: Die Bruecke traegt in den ersten
            # Sekunden ein, was vorgemerkt war. Wer frueher zaehlt, uebersieht
            # genau den Entwurf, den DialOS gerade selbst abgelegt hat. Lief
            # Thunderbird schon, gibt es nichts nachzuholen - dann sofort.
            if not lief_schon:
                nachholen_abwarten()
            entwuerfe_ansagen(beim_oeffnen=True)
        else:
            melde("Brücke kam nicht - keine Entwurfsansage")
    return True


def saetze():
    """Alle Saetze - fuer die Grammatik und fuer die Doku."""
    return tuple(PROGRAMME) + tuple(SCHLIESSEN)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--liste", "-l"):
        for satz in PROGRAMME:
            print(f"{satz}\t{' '.join(PROGRAMME[satz]['befehl'])}")
        for satz in SCHLIESSEN:
            print(f"{satz}\tSIGTERM an {SCHLIESSEN[satz]['programm']}")
        return 0
    return 0 if starten(" ".join(sys.argv[1:]).strip().lower()) else 1


if __name__ == "__main__":
    sys.exit(main())
