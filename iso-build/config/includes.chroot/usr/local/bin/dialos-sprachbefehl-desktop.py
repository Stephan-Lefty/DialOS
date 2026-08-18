#!/usr/bin/env python3
"""DialOS: Sprachbefehle - der Dienst, der zuhoert.

BEDIENMODELL (entschieden mit Stephan am 2026-08-17, ausfuehrlich in
docs/sprachsteuerung.md, Abschnitt "Wann hoert DialOS zu?"):

  AUS   Normalzustand, auch direkt nach dem Anmelden. DialOS hoert
        ausschliesslich auf "Sprachsteuerung starten". Das ist der
        eigentliche Schutz - solange die Erkennung aus ist, kennt die
        Grammatik gar keinen anderen Satz, also kann weder ein Gespraech
        noch das Radio etwas ausloesen.
  AN    "Ich hoere." Jetzt gelten die Befehle, bis "Sprachsteuerung
        stoppen" kommt oder zwei Minuten lang nichts.

Beide Wechsel werden ANGESAGT. Fuer einen blinden Nutzer waere ein
Zustand, den man nur sehen kann, kein Zustand: Er hoert jeden Wechsel,
und ist er unsicher, sagt er "Sprachsteuerung starten" - laeuft sie
schon, sagt das System es ihm.

Der zweite Weg ins Mikrofon laeuft NICHT ueber diesen Dienst: Wenn das
System selbst etwas fragt, oeffnet es die Erkennung fuer die Antwort und
schliesst sie danach wieder (dialos-say.py --frage). Der Nutzer muss sich
dafuer nicht anmelden - er wurde ja gerade angesprochen.

Die Desktop-Umschaltung ("auf Linux/Windows umschalten") ist bisher der
einzige Befehl.

Stephans Vorgabe vom 2026-08-16: Das Umschalten der Desktop-Optik muss
per Sprache gehen - kein Menue, kein Terminal. Fuer die Zielgruppe ist
das nicht Bequemlichkeit, sondern die einzige brauchbare Bedienung.

DER BEFEHL IST EIN GANZER SATZ, KEIN EINZELWORT - ebenfalls Stephans
Vorgabe, und sie loest ein echtes Problem. Ein einzelnes "Windows" faellt
im Gespraech staendig; der Schreibtisch wuerde sich ungefragt umstellen,
und ein blinder Nutzer wuesste nicht, warum plotzlich alles anders
klingt. Im Test am 2026-08-16 hat der Satz "ich habe frueher windows
benutzt" beim Erkenner "auf auf windows" ergeben - also durchaus das Wort
"windows", aber eben NICHT "umschalten". Deshalb muss beides im Satz
vorkommen: das Ziel UND das Wort "umschalten". Damit war der
Stoersatz im Test wirkungslos.

Fuer den Linux-Stil gelten zwei Ziele: "Linux" und "Gnome". Stephan hat
"Linux" nachgereicht, weil es das Wort ist, das jemand aus der
Windows-Welt kennt - "Gnome" sagt ihm nichts. Beide anzunehmen kostet
nichts und erspart dem Nutzer, sich fuer eines zu entscheiden.

Dies ist der erste dauerhaft lauschende Dienst in DialOS. Bisher wurde
Vosk nur punktuell aufgerufen (Lautstaerke-Frage in der Start-Ansage).

FUENF ENTSCHEIDUNGEN, DIE HIER DRINSTECKEN
==========================================

1. EINGESCHRAENKTE GRAMMATIK STATT FREIER ERKENNUNG.
   Vosk bekommt nur die drei Befehlssaetze und "[unk]" zur Auswahl. Das
   ist keine Optimierung, sondern Voraussetzung: Im Test am 2026-08-16
   (Piper spricht den Satz, Vosk hoert zu) erkannte das freie deutsche
   Modell das Wort "gnome" zuverlaessig als **"genug"**. Mit der
   Grammatik lagen alle drei Saetze auf Anhieb woertlich richtig. Nebenbei kostet die
   kleine Grammatik deutlich weniger Rechenzeit - bei einem Dienst, der
   dauerhaft laeuft, zaehlt das fuer die Akkulaufzeit.

2. EINGEBAUTES MIKROFON STATT BLUETOOTH - anders als bei der
   Lautstaerke-Frage, und mit Absicht. Das Referenz-Headset (AIRHUG 01)
   kann A2DP und HFP nicht gleichzeitig: Sobald sein Mikrofon benutzt
   wird, faellt die Wiedergabe auf Telefonqualitaet. Bei einer einmaligen
   Frage ist das ein kurzer Moment; bei dauerhaftem Zuhoeren waere die
   Musik- und Sprachausgabe **fuer immer** verschlechtert. Deshalb hoert
   dieser Dienst ueber das eingebaute Mikrofon. Drei feste Saetze zu
   unterscheiden gelingt auch damit - genau das ist der Vorteil einer
   winzigen Grammatik.

3. WAEHREND DAS SYSTEM SPRICHT, WIRD NICHT ZUGEHOERT - UND DANACH WIRD
   DIE AUFNAHME NEU BEGONNEN.
   Der erste Teil war von Anfang an da (Markierungsdatei, die
   dialos-say.py ohnehin setzt). Der zweite Teil fehlte, und genau daran
   ist der Dienst am 2026-08-17 gescheitert: Er schaltete auf Windows um,
   und 15 Sekunden spaeter von selbst wieder zurueck.

   Der Grund ist Arithmetik, nicht Logik. parec erzeugt bei 16 kHz mono
   16 Bit rund 32.000 Bytes pro Sekunde. Der Dienst verwarf waehrend des
   Sprechens 4.000 Bytes und schlief dann 0,3 Sekunden - also nur rund
   13.000 Bytes pro Sekunde. Er leerte die Warteschlange also LANGSAMER
   als parec sie fuellte. Nach einer acht Sekunden langen Ansage standen
   rund fuenf Sekunden Ansage-Ton in der Pipe, die er anschliessend ganz
   normal auswertete - und weil die eingeschraenkte Grammatik alles auf
   einen der drei Saetze zwingt, wurde daraus ein Befehl.

   Die Markierung allein reicht also nicht: Sie verhindert das Zuhoeren,
   nicht das Aufzeichnen. Deshalb wird die Aufnahme nach jedem Sprechen
   komplett neu begonnen - ein frischer parec-Prozess hat keinen
   Rueckstand. Das kostet ein paar hundert Millisekunden und ist der
   einzige Weg, bei dem nichts von der eigenen Stimme uebrig bleiben
   kann.

4. KEINE RUECKFRAGE, ABER EINE ANSAGE.
   Ein "Willst du wirklich?" bei jedem Wort waere laestig. Stattdessen
   sagt der Dienst nach dem Umschalten, was er getan hat - wer es nicht
   wollte, sagt einfach das andere Wort. Damit ist ein Fehlgriff in zwei
   Sekunden ruecknehmbar, ohne dass jemand sehen muss, was passiert ist.
   Steht die Optik schon so, wird nur das gesagt und nichts geaendert.

5. KEINE SPERRFRIST - sie ist am 2026-08-17 entfallen.
   Sie sollte verhindern, dass ein langgezogener Satz mehrfach ausloest.
   Das erledigt Punkt 3 aber vollstaendig: Ein frischer parec-Prozess
   plus "erkenner.Reset()" hat keinen Rueckstand. Tatsaechlich bewirkt
   hat sie, dass der Dienst nach einem Umschalten rund fuenf Sekunden
   taub war - ausgerechnet in dem Moment, in dem der Nutzer den naechsten
   Befehl sagt. Stephan hat das zweimal als "ich muss viel lauter reden"
   gemeldet. Die ausfuehrliche Rechnung steht bei WARTEN_BEIM_SPRECHEN_S.

Aufruf: laeuft ueber /etc/xdg/autostart/dialos-sprachbefehl-desktop.desktop
automatisch in jeder Sitzung. Von Hand zum Testen einfach starten;
beenden mit Strg+C.
"""

import json
import os
import subprocess
import sys
import time

MODELL = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
UMSCHALT_SKRIPT = "/usr/local/bin/dialos-desktop-stil.sh"
SAY = "/usr/local/bin/dialos-say.py"
PEGEL_SKRIPT = "/usr/local/sbin/dialos-mikrofon-pegel.sh"
STIL_DATEI = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "dialos", "desktop-stil",
)

# ZWEI ZUSTAENDE, ZWEI GRAMMATIKEN (Bedienmodell vom 2026-08-17, siehe
# docs/sprachsteuerung.md, Abschnitt "Wann hoert DialOS zu?").
#
# AUS ist der Normalzustand, auch direkt nach dem Anmelden. Dann hoert
# DialOS ausschliesslich auf den einen Satz, mit dem der Nutzer sich
# anmeldet. Das ist der eigentliche Schutz: Solange die Erkennung aus
# ist, kann kein Gespraech und kein Radio irgendetwas ausloesen, weil die
# Grammatik gar keinen anderen Satz kennt.
#
# AN kennt zusaetzlich die Befehle und den Satz zum Ausschalten.
#
# "[unk]" ist Vosks Auffangeintrag fuer alles andere - ohne ihn presst
# das Modell jedes Geraeusch in einen der Saetze.
STARTSATZ = "sprachsteuerung starten"
STOPPSATZ = "sprachsteuerung stoppen"

GRAMMATIK_AUS = json.dumps([STARTSATZ, "[unk]"])
GRAMMATIK_AN = json.dumps([
    STARTSATZ,
    STOPPSATZ,
    "auf linux umschalten",
    "auf gnome umschalten",
    "auf windows umschalten",
    "diktat starten",
    "einkaufszettel aufnehmen",
    "notiz aufnehmen",
    "einkaufszettel vorlesen",
    "notizen vorlesen",
    "einkauf erledigt",
    "einkaufszettel wegwerfen",
    "[unk]",
])

# Welcher Satz welche Notiz fuellt. "diktat starten" und "notiz aufnehmen"
# schreiben in dieselbe Sammelnotiz; der Einkaufszettel bekommt eine eigene,
# weil er der Fall ist, den Stephan als Beispiel genannt hat - und weil eine
# Einkaufsliste zwischen Terminen und Gedanken unbrauchbar waere.
#
# Alle drei Saetze am 2026-08-18 gegen das Modell geprueft (Piper spricht,
# Vosk hoert): woertlich richtig erkannt. Das ist Pflicht vor jedem neuen
# Befehl, siehe docs/sprachbefehle.md - "gnome" wurde frei erkannt zu
# "genug".
DIKTAT_SAETZE = {
    "diktat starten": "notizen",
    "notiz aufnehmen": "notizen",
    "einkaufszettel aufnehmen": "einkaufszettel",
}
DIKTAT_SKRIPT = "/usr/local/bin/dialos-diktat.py"

# Notizen vorlesen und wegwerfen. Zwei Saetze fuer dasselbe Leeren, weil
# Stephan beide wollte (2026-08-18) - "Einkauf erledigt" beschreibt die
# Situation, "Einkaufszettel wegwerfen" die Handlung. Dieselbe Ueberlegung
# wie bei "auf Linux" und "auf Gnome": Zwei Eintraege kosten nichts, und der
# Nutzer muss sich keine Formulierung merken.
#
# "loeschen" waere der naheliegende Satz gewesen und ist NICHT moeglich: Das
# Wort steht nicht im Wortschatz des Modells. Vosk wirft es beim Bauen der
# Grammatik still hinaus, der Befehl waere nie ausgeloest worden, und im
# Protokoll haette nur "einkaufszettel" gestanden. Geprueft am 2026-08-18 -
# ebenso fehlen "zuruecksetzen" und "aufraeumen".
NOTIZ_SKRIPT = "/usr/local/bin/dialos-notiz.py"
NOTIZ_SAETZE = {
    "einkaufszettel vorlesen": ("einkaufszettel", "vorlesen"),
    "notizen vorlesen": ("notizen", "vorlesen"),
    "einkauf erledigt": ("einkaufszettel", "loeschen"),
    "einkaufszettel wegwerfen": ("einkaufszettel", "loeschen"),
}

# Nach so langer Stille schaltet sich die Erkennung von selbst ab
# (Stephan, 2026-08-17: zwei Minuten, mit Ansage). Der Grund ist nicht
# Stromsparen, sondern Sicherheit: Wer das "stoppen" vergisst, haette
# sonst dauerhaft ein offenes Mikrofon.
ZEITGRENZE_S = 120.0

# Erkannt wird nur, was BEIDES enthaelt: ein Ziel und das Wort
# "umschalten". Siehe Kopf der Datei - ohne die zweite Bedingung reicht
# ein beilaeufiges "windows" im Gespraech.
AUSLOESER = "umschalten"
ZIELE = {"linux": "gnome", "gnome": "gnome", "windows": "windows"}

# Kurz und immer gleich - der Nutzer hoert sie taeglich, da zaehlt
# Wiedererkennbarkeit mehr als Abwechslung. Aus Michaels Sicht
# formuliert, nicht als Statusmeldung ("Sprachsteuerung ist
# eingeschaltet").
ANSAGE_AN = "Ich höre."
ANSAGE_AUS = "Ich höre nicht mehr."
ANSAGE_ZEITGRENZE = "Ich schalte die Sprachsteuerung wieder aus."
ANSAGE_LAEUFT_SCHON = "Ich höre schon."

# KEINE Sperrfrist mehr - zweimal am 2026-08-17 als Ursache derselben
# Fehlermeldung entlarvt, und beim ersten Mal habe ich nur die Haelfte
# behoben.
#
# Sie sollte verhindern, dass ein langgezogener Satz mehrfach ausloest.
# Dafuer ist sie ueberfluessig, seit die Aufnahme nach jedem Sprechen
# verworfen und neu begonnen wird (siehe "aufnahme_verwerfen"): Ein
# frischer parec-Prozess plus "erkenner.Reset()" hat keinen Rueckstand,
# aus dem heraus etwas doppelt ausloesen koennte.
#
# Was sie tatsaechlich bewirkt hat: Nach einem Umschalten war der Dienst
# rund fuenf Sekunden taub - 2,4 s laeuft das Umschalt-Skript und spricht
# dabei, 2,0 s Sperrfrist, 0,7 s Nachhall-Pause. Die Ansage endet aber
# schon nach 1,5 s. Der Nutzer hoert also die Antwort, spricht weiter und
# redet 3,6 Sekunden gegen ein taubes System. Stephan hat das zweimal
# als "ich muss viel lauter reden" gemeldet - lauter half nie, das
# Warten half. Beim ersten Mal habe ich die Frist nur nach "Ich hoere."
# entfernt und von 5 s auf 2 s gekuerzt, statt die eigene Begruendung
# auch auf das Umschalten anzuwenden.
#
# Bleibt taub ist damit nur noch: solange das System spricht (ueber die
# Markierungsdatei) plus NACHHALL_WARTEN_S danach.
WARTEN_BEIM_SPRECHEN_S = 0.3
NACHHALL_WARTEN_S = 0.7     # Pause nach dem Sprechen, bevor neu aufgenommen wird
SAETTIGUNG_GRENZE = 15      # so viele uebersteuerte Bloecke in Folge = Pegel richten
PEGEL_ABSTAND_S = 60.0      # hoechstens einmal pro Minute nachregeln

# Mit "--debug" gestartet zeigt der Dienst jeden erkannten Satz und den
# Aussteuerungspegel an. Das ist kein Entwickler-Spielzeug, sondern die
# Lehre aus dem 2026-08-16: Der Dienst schwieg, und ohne Pegelanzeige war
# nicht zu unterscheiden, ob er nicht zuhoert, nichts versteht oder das
# Mikrofon uebersteuert ist (es war Letzteres).
DEBUG = "--debug" in sys.argv


def melde(text):
    """Debug-Ausgabe MIT Zeitstempel.

    Der Zeitstempel ist nicht Zierde (Fehler vom 2026-08-18): Beim Test der
    Diktat-Sperre stand im Protokoll ein erkannter Satz, und ohne Uhrzeit
    liess sich nicht feststellen, ob er WAEHREND des Diktats kam - also ob
    die Sperre versagt hat - oder davor. Ein Protokoll ohne Zeit kann
    Gleichzeitigkeit nicht belegen, und genau darum ging es.
    """
    if DEBUG:
        print(f"\n{time.strftime('%H:%M:%S')}  {text}", flush=True)


def markierungsdatei():
    """Gleiche Logik wie in dialos-say.py - pro Konto privat."""
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, "dialos-sprachausgabe-aktiv")
    return f"/tmp/dialos-sprachausgabe-aktiv-{os.getuid()}"


MARKIERUNG = markierungsdatei()

# Marke des Diktats. Solange sie da ist, laeuft dialos-diktat.py mit freier
# Erkennung und dem grossen Modell - dann muss DIESER Dienst schweigen.
#
# Der Grund ist nicht Hoeflichkeit, sondern ein echter Fehlerfall: Liefen
# beide Erkennungen zugleich, wuerde ein diktierter Satz auch als Befehl
# ausgewertet. Wer in einem Brief "auf windows umschalten" diktiert, haette
# danach einen anderen Schreibtisch - und wuesste nicht, warum.
#
# Dasselbe Muster wie MARKIERUNG oben, und aus demselben Grund gewaehlt:
# Eine Datei im Laufzeitverzeichnis ueberlebt keinen Neustart, kann also
# nicht als Altlast zurueckbleiben und den Dienst dauerhaft stumm schalten.
DIKTAT_MARKE = markierungsdatei().replace("dialos-sprachausgabe-aktiv",
                                          "dialos-diktat-aktiv")


def spricht_gerade():
    return os.path.exists(MARKIERUNG)


def diktat_laeuft():
    return os.path.exists(DIKTAT_MARKE)


def sprich(text):
    if os.access(SAY, os.X_OK):
        subprocess.run([SAY, text], capture_output=True, timeout=60)
    else:
        print(text)


ECHO_QUELLE = "dialos_mikrofon_ohne_echo"


def waehle_mikrofon():
    """Reihenfolge: Echo-bereinigte Quelle, sonst eingebaut, zuletzt Bluetooth.

    ERSTE WAHL ist seit 2026-08-17 die Quelle ohne Echo (PipeWire-Modul
    module-echo-cancel, eingerichtet in
    /etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf). Sie
    rechnet das Lautsprechersignal aus dem Mikrofon heraus. Ohne sie hoert
    der Dienst alles mit, was das Geraet abspielt - die eigene Ansage
    ebenso wie Radio oder Mediathek - und die eingeschraenkte Grammatik
    presst Bruchstuecke davon in einen Befehl. Gemessen am selben Tag:
    waehrend der Lautsprecher sprach, 6,13 % Pegel am rohen Mikrofon
    gegenueber 0,15 % an der bereinigten Quelle, also rund 32 dB weniger.

    ZWEITE WAHL das eingebaute Mikrofon - Begruendung siehe Punkt 2 oben.

    KEIN BLUETOOTH, KEIN USB - Stephans Festlegung vom 2026-08-17: Die
    Eingabe ist bis auf Weiteres immer das eingebaute Mikrofon, externe
    Geraete kommen zum Schluss noch einmal dran. Hier stand vorher eine
    Bluetooth-Quelle als letzte Rueckfallebene, mit der Begruendung
    "schlechtere Wiedergabe ist besser als ein Geraet, das nicht
    zuhoert". Diese Begruendung war falsch herum gedacht, aus zwei
    Gruenden:

    1. Greift DialOS nie ein Bluetooth-Mikrofon an, kann das Geraet auch
       nie in HFP rutschen. Die ganze A2DP/HFP-Zwangswahl faellt weg -
       nicht weil wir sie geloest haetten, sondern weil wir sie nicht
       mehr beruehren. Sie hat bisher die Tonqualitaet der Videoaufnahme
       gekostet und steckt in mehreren offenen Punkten.
    2. Ein abschaltbares Mikrofon ist ein Risiko fuer die GANZE
       Tonausgabe, nicht nur fuer die Erkennung: Haengt die
       Echo-Unterdrueckung daran, nimmt sein Ausfall alles mit (siehe
       docs/Debian-zu-DialOS.md, Schritt 11f - am 2026-08-17 passiert).
       Das eingebaute Mikrofon kann man nicht ausschalten.
    """
    try:
        roh = subprocess.run(
            ["pactl", "-f", "json", "list", "sources"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        quellen = json.loads(roh) if roh.strip() else []
    except Exception:
        return None
    namen = [q.get("name", "") for q in quellen
             if q.get("name") and not q["name"].endswith(".monitor")]
    if ECHO_QUELLE in namen:
        return ECHO_QUELLE
    eingebaut = [n for n in namen if n.startswith("alsa_input.pci-")]
    if eingebaut:
        return eingebaut[0]
    # Bewusst KEINE weitere Rueckfallebene: Findet sich kein eingebautes
    # Mikrofon, ist die Erkennung aus - lieber gar nicht zuhoeren als
    # ueber ein Geraet, das die Wiedergabe verschlechtert oder beim
    # Ausschalten den ganzen Ton mitnimmt. Der Aufrufer sagt das an.
    return None


def aktueller_stil():
    try:
        with open(STIL_DATEI) as f:
            return f.read().strip()
    except OSError:
        return "gnome"


def umschalten(ziel):
    if aktueller_stil() == ziel:
        sprich("Der Schreibtisch steht schon auf Linux."
               if ziel == "gnome"
               else "Der Schreibtisch steht schon auf Windows.")
        return
    if not os.access(UMSCHALT_SKRIPT, os.X_OK):
        sprich("Ich kann die Umschaltung nicht finden.")
        return
    # Das Umschalt-Skript sagt selbst an, was es getan hat - deshalb hier
    # keine zweite Ansage.
    subprocess.run([UMSCHALT_SKRIPT, ziel], capture_output=True, timeout=120)


def diktat_starten(notiz):
    """Startet das Diktat als eigenen Prozess und kehrt sofort zurueck.

    NICHT abwarten: Ein Diktat kann Minuten dauern, und dieser Dienst muss
    in der Zwischenzeit seine Schleife weiterlaufen lassen - schon damit er
    die Marke sieht und sich heraushaelt.

    Die Marke legt das Diktat selbst an, und zwar VOR dem Laden seines
    Modells. Das ist wesentlich: Das Laden dauert rund 9 Sekunden, und ohne
    diese Reihenfolge waeren die ersten diktierten Saetze hier als Befehle
    ausgewertet worden.
    """
    if not os.access(DIKTAT_SKRIPT, os.X_OK):
        sprich("Ich kann das Diktat nicht finden.")
        return
    if diktat_laeuft():
        # Kann vorkommen, wenn der Nutzer den Satz zweimal sagt, weil er die
        # Ladezeit fuer einen Fehlschlag haelt. Zwei Diktate gleichzeitig
        # wuerden sich das Mikrofon streiten.
        sprich("Ich schreibe schon mit.")
        return
    try:
        # start_new_session: Das Diktat soll weiterlaufen, auch wenn dieser
        # Dienst neu gestartet wird.
        #
        # OHNE "--debug" und mit verworfener Ausgabe (Fehler vom 2026-08-18):
        # Das Diktat schreibt sein Protokoll ohnehin selbst, mit Uhrzeit. Mit
        # "--debug" gibt es dieselben Zeilen zusaetzlich auf die
        # Standardausgabe - und die hier in dieselbe Datei umzuleiten liess
        # jede Zeile doppelt erscheinen, einmal mit und einmal ohne Uhrzeit.
        # Ein Protokoll, das jede Zeile zweimal zeigt, laedt zu falschen
        # Schluessen ein.
        subprocess.Popen([DIKTAT_SKRIPT, "notiz", notiz],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        melde(f"Diktat gestartet fuer Notiz {notiz!r}")
    except Exception as fehler:
        melde(f"Diktat liess sich nicht starten: {fehler}")
        sprich("Das Diktat lässt sich nicht starten.")


def notiz_aktion(name, was):
    """Startet die Notiz-Verwaltung und kehrt sofort zurueck.

    NICHT abwarten, aus demselben Grund wie beim Diktat: Das Vorlesen einer
    langen Liste dauert eine Minute, und dieser Dienst muss in der Zeit
    seine Schleife weiterlaufen lassen. Beim Leeren kommt noch die
    Rueckfrage dazu, die selbst zuhoert.
    """
    if not os.access(NOTIZ_SKRIPT, os.X_OK):
        sprich("Ich kann die Notizen nicht finden.")
        return
    try:
        subprocess.Popen([NOTIZ_SKRIPT, name, was],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        melde(f"Notiz-Aktion {was!r} fuer {name!r} gestartet")
    except Exception as fehler:
        melde(f"Notiz-Aktion liess sich nicht starten: {fehler}")
        sprich("Das lässt sich nicht ausführen.")


def pegel_richten():
    """Setzt die Aufnahme-Verstaerkung zurueck, falls sie uebersteuert.

    Warum das hier steht und nicht nur im Systemdienst (gefunden
    2026-08-17): dialos-mikrofon-pegel.service laeuft beim Booten, also
    VOR der Benutzeranmeldung. WirePlumber stellt seine gespeicherten
    Geraete-Einstellungen aber erst in der Sitzung wieder her - und
    hebt "Internal Mic Boost" dabei zurueck auf +30 dB. Der Systemdienst
    ist damit strukturell zu frueh dran.

    Deshalb richtet der Dienst, der das Mikrofon tatsaechlich benutzt,
    den Pegel selbst - direkt nachdem die Aufnahme geoeffnet ist, also
    nach WirePlumbers Zugriff. Das Skript braucht keine Root-Rechte:
    amixer darf jedes Konto der Gruppe "audio" bedienen.
    """
    if not os.access(PEGEL_SKRIPT, os.X_OK):
        return
    try:
        subprocess.run([PEGEL_SKRIPT], capture_output=True, timeout=15)
    except Exception:
        pass


def aufnahme_starten(quelle):
    befehl = ["parec", f"--rate={ABTASTRATE}", "--channels=1", "--format=s16le"]
    if quelle:
        befehl.append(f"--device={quelle}")
    p = subprocess.Popen(befehl, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    # Erst nach dem Oeffnen des Datenstroms - vorher greift WirePlumber
    # noch einmal auf die Regler zu.
    time.sleep(0.3)
    pegel_richten()
    return p


def main():
    try:
        import vosk
    except ImportError:
        print("Vosk ist nicht installiert - Sprachbefehle sind aus.", file=sys.stderr)
        return 1
    if not os.path.isdir(MODELL):
        print(f"Sprachmodell fehlt: {MODELL}", file=sys.stderr)
        return 1

    vosk.SetLogLevel(-1)
    modell = vosk.Model(MODELL)
    quelle = waehle_mikrofon()
    if not quelle:
        # ANSAGEN, nicht nur nach stderr schreiben: Die Zielgruppe sieht
        # kein Terminal. Ohne Ansage waere die Sprachsteuerung einfach
        # stumm tot - und niemand wuesste, warum nichts reagiert.
        print("Kein Mikrofon gefunden.", file=sys.stderr)
        sprich("Ich finde kein Mikrofon. Die Sprachsteuerung ist aus.")
        return 1

    # Merker fuer die Ansage "kein Mikrofon" - damit sie einmal kommt und
    # nicht alle fuenf Sekunden.
    mikrofon_fehlt_gemeldet = False
    # Damit "Diktat laeuft" einmal im Protokoll steht und nicht dreimal je
    # Sekunde. Zurueckgesetzt, sobald das Diktat vorbei ist.
    diktat_gemeldet = False

    # Beim Anmelden ist die Erkennung immer AUS - vorhersagbar und sicher.
    hoert_zu = False
    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
    prozess = aufnahme_starten(quelle)
    letzte_aktivitaet = time.time()
    aufnahme_verwerfen = False
    saettigungen = 0
    letzte_pegelkorrektur = 0.0

    try:
        while True:
            # Zeitgrenze: Wer das "stoppen" vergisst, haette sonst dauerhaft
            # ein offenes Mikrofon. Mit Ansage, damit der Nutzer den Wechsel
            # hoert - ein Zustand, den man nur sehen kann, waere fuer diese
            # Zielgruppe kein Zustand.
            # Waehrend eines Diktats laeuft die Zeitgrenze NICHT. Sonst
            # schaltete sich die Sprachsteuerung nach zwei Minuten Diktat von
            # selbst ab, und der Nutzer stuende nach "diktat beenden" vor
            # einer stummen Steuerung, ohne zu wissen warum.
            if diktat_laeuft():
                letzte_aktivitaet = time.time()

            if hoert_zu and time.time() - letzte_aktivitaet > ZEITGRENZE_S:
                hoert_zu = False
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
                sprich(ANSAGE_ZEITGRENZE)
                continue

            # Nicht zuhoeren, solange das System selbst spricht oder ein
            # Diktat laeuft. Danach wird die Aufnahme verworfen und neu
            # begonnen, siehe unten - beim Diktat ist das besonders
            # wichtig, weil sonst der halbe diktierte Text in der
            # Warteschlange steht und anschliessend als Befehl ausgewertet
            # wuerde.
            if spricht_gerade() or diktat_laeuft():
                if diktat_laeuft() and not diktat_gemeldet:
                    melde("anderer Dienst hoert zu - ich halte mich heraus")
                    diktat_gemeldet = True
                aufnahme_verwerfen = True
                time.sleep(WARTEN_BEIM_SPRECHEN_S)
                continue

            if diktat_gemeldet and not diktat_laeuft():
                melde("anderer Dienst fertig - ich hoere wieder zu")
                diktat_gemeldet = False

            if aufnahme_verwerfen:
                # Waehrend der Pause hat parec weiter aufgezeichnet - unter
                # anderem die eigene Ansage. Diese Aufzeichnung steht jetzt
                # in der Warteschlange und wuerde als Naechstes ganz normal
                # ausgewertet. Genau daran ist der Dienst am 2026-08-17
                # gescheitert: Er schaltete auf Windows um und 15 Sekunden
                # spaeter von selbst zurueck.
                #
                # Die Markierungsdatei verhindert das Zuhoeren, nicht das
                # Aufzeichnen. Deshalb wird die Aufnahme hier komplett
                # verworfen und neu begonnen - ein frischer parec-Prozess
                # hat keinen Rueckstand.
                aufnahme_verwerfen = False
                try:
                    prozess.terminate()
                    prozess.stdout.close()
                except Exception:
                    pass
                # Kurz warten, damit auch der Nachhall der Ansage im Raum
                # nicht mehr in die neue Aufnahme faellt.
                time.sleep(NACHHALL_WARTEN_S)
                prozess = aufnahme_starten(quelle)
                erkenner = vosk.KaldiRecognizer(
                    modell, ABTASTRATE,
                    GRAMMATIK_AN if hoert_zu else GRAMMATIK_AUS)
                if DEBUG:
                    melde("(Aufnahme nach Sprechpause neu begonnen)")
                continue

            block = prozess.stdout.read(4000)
            if not block:
                # parec beendet (z. B. Audiogeraet gewechselt) - neu
                # aufsetzen statt den Dienst sterben zu lassen.
                time.sleep(1)
                neu = waehle_mikrofon()
                if not neu:
                    # Seit die Bluetooth-Rueckfallebene weg ist, kann hier
                    # tatsaechlich None stehen (Mikrofon abgemeldet, Karte
                    # verschwunden). Einmal ansagen und weiter warten -
                    # aufnahme_starten(None) waere ein Absturz, und ein
                    # abgestuerzter Dienst kommt in dieser Sitzung nicht
                    # mehr wieder.
                    if not mikrofon_fehlt_gemeldet:
                        sprich("Ich finde kein Mikrofon mehr.")
                        mikrofon_fehlt_gemeldet = True
                    time.sleep(5)
                    continue
                if mikrofon_fehlt_gemeldet:
                    sprich("Das Mikrofon ist wieder da.")
                    mikrofon_fehlt_gemeldet = False
                quelle = neu
                prozess = aufnahme_starten(quelle)
                erkenner = vosk.KaldiRecognizer(
                    modell, ABTASTRATE,
                    GRAMMATIK_AN if hoert_zu else GRAMMATIK_AUS)
                continue

            pegel = max(abs(int.from_bytes(block[i:i + 2], "little", signed=True))
                        for i in range(0, len(block) - 1, 2))
            gesaettigt = pegel >= 32000
            if DEBUG:
                print(f"\rPegel {100 * pegel / 32768:5.1f} %"
                      f"{'  UEBERSTEUERT' if gesaettigt else '            '}",
                      end="", flush=True)

            # Selbstheilung: Uebersteuert die Aufnahme laenger, ist die
            # Erkennung wertlos - Vosk braucht die Pausen zwischen den
            # Woertern, und die gibt es im Dauervollausschlag nicht.
            # Statt still nichts zu verstehen, wird der Pegel neu
            # gerichtet. Hoechstens einmal pro Minute, damit ein
            # tatsaechlich lautes Umfeld keine Dauerschleife ausloest.
            if gesaettigt:
                saettigungen += 1
                if (saettigungen >= SAETTIGUNG_GRENZE
                        and time.time() - letzte_pegelkorrektur > PEGEL_ABSTAND_S):
                    if DEBUG:
                        melde("(uebersteuert - Pegel wird neu gerichtet)")
                    pegel_richten()
                    letzte_pegelkorrektur = time.time()
                    saettigungen = 0
            else:
                saettigungen = 0

            if not erkenner.AcceptWaveform(block):
                continue
            text = json.loads(erkenner.Result()).get("text", "")
            if DEBUG and text:
                melde(f"erkannt: {text!r}")
            if not text:
                continue
            worte = text.split()
            satz = " ".join(worte)

            # --- Zustandswechsel: anmelden ---
            if STARTSATZ in satz:
                if hoert_zu:
                    sprich(ANSAGE_LAEUFT_SCHON)
                else:
                    hoert_zu = True
                    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AN)
                    sprich(ANSAGE_AN)
                # KEINE Sperrfrist hier - siehe Kommentar bei
                # SPERRFRIST_S. Direkt nach "Ich hoere." erwartet der
                # Nutzer, dass er sprechen kann. Gegen die eigene Ansage
                # schuetzt das Neubeginnen der Aufnahme.
                letzte_aktivitaet = time.time()
                continue

            # Ist die Erkennung aus, kann hier nichts anderes mehr kommen -
            # die Grammatik kennt in diesem Zustand keinen weiteren Satz.
            if not hoert_zu:
                continue

            # --- Zustandswechsel: abmelden ---
            if STOPPSATZ in satz:
                hoert_zu = False
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
                sprich(ANSAGE_AUS)
                continue

            # --- Befehle: Diktat ---
            # VOR der Umschaltung geprueft, weil diese Saetze das Wort
            # "umschalten" nicht enthalten und sonst an der
            # Ausloeser-Bedingung unten haengen blieben.
            if satz in DIKTAT_SAETZE:
                diktat_starten(DIKTAT_SAETZE[satz])
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            # --- Befehle: Notizen vorlesen und wegwerfen ---
            if satz in NOTIZ_SAETZE:
                notiz_aktion(*NOTIZ_SAETZE[satz])
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            # --- Befehle: Schreibtisch ---
            if AUSLOESER not in worte:
                continue
            for wort in worte:
                ziel = ZIELE.get(wort)
                if ziel:
                    umschalten(ziel)
                    letzte_aktivitaet = time.time()
                    erkenner.Reset()
                    break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            prozess.terminate()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
