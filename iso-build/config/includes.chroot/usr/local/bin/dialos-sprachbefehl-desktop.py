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
import signal
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
    # Zwei Formulierungen fuer dasselbe (Stephan, 2026-08-21: "und vielleicht
    # optional Brief schreiben") - dieselbe Ueberlegung wie bei "auf Linux" und
    # "auf Gnome": Zwei Eintraege kosten nichts, und der Nutzer muss sich keine
    # Formulierung merken. Beide Saetze sind im Wortschatz des kleinen Modells
    # geprueft, ebenso "brief vorlesen" und "brief wegwerfen" fuer spaeter.
    "brief aufnehmen",
    "brief schreiben",
    "einkaufszettel vorlesen",
    "notizen vorlesen",
    "brief vorlesen",
    "einkauf erledigt",
    "einkaufszettel wegwerfen",
    "wie viel uhr ist es",
    "wie ist die uhrzeit",
    "welchen tag haben wir",
    "welches datum haben wir",
    # Bildschirmfoto (Stephan, 2026-08-21). Zwei Formulierungen wie ueberall.
    # Das Foto ist nicht fuer den Nutzer - er sieht es nicht -, sondern fuer
    # den sehenden Helfer und den Support: "Was steht da gerade?"
    "bildschirmfoto erstellen",
    "bildschirmfoto machen",
    # "hilfe rufen" und "fernwartung beenden" sind ZURUECKGESTELLT
    # (Stephan, 2026-08-20: "können den Rustdesk ganz nach hinten schieben,
    # wenn alles andere läuft"). Sie stehen bewusst NICHT in der Grammatik,
    # solange der Umbau auf den systemd-Dienst offen ist - der Befehl wuerde
    # heute die RustDesk-ANWENDUNG starten, und die stuerzt ohne ipc_service
    # nach rund 40 Sekunden ab ("Got signal 11 and exit", am 2026-08-19 im
    # Protokoll belegt). Der Nutzer bekaeme die ID vorgelesen, sein Betreuer
    # koennte sich nicht verbinden, und beim naechsten Mal glaubt er dem
    # Geraet nicht mehr.
    #
    # Ein Sprachbefehl, der halb funktioniert, ist schlimmer als einer, der
    # nicht existiert - und ausgerechnet bei dem, mit dem Hilfe geholt wird,
    # wenn nichts mehr geht.
    #
    # Der Code bleibt vollstaendig liegen: dialos-hilfe.py, die Wache, die
    # Zeitgrenze, die Nachfragen. Wieder freigeben heisst, diese zwei Zeilen
    # wieder einzukommentieren - siehe TODO.md, erster Punkt.
    #   "hilfe rufen",
    #   "fernwartung beenden",
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
    "brief aufnehmen": "brief",
    "brief schreiben": "brief",
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
# Auskunft: Uhrzeit und Datum (Stephans Wunsch, 2026-08-19).
#
# "Wie spaet ist es?" waere die naheliegende Frage gewesen und ist NICHT
# moeglich: "spaet" steht nicht im Wortschatz des Modells (geprueft, dieselbe
# Falle wie "loeschen" am Tag vorher). Deshalb zwei Formulierungen, die beide
# geprueft und woertlich erkannt wurden.
#
# "Wie wird das Wetter?" gibt es bewusst nicht - Begruendung in
# dialos-auskunft.py: Am Einsatzort liefert die Standortbestimmung nur eine
# IP-Schaetzung mit 26 km Ungenauigkeit, und der Befehl haette fast immer
# geantwortet, dass er nichts abrufen kann.
FOTO_SKRIPT = "/usr/local/bin/dialos-bildschirmfoto.py"
FOTO_SAETZE = ("bildschirmfoto erstellen", "bildschirmfoto machen")
AUSKUNFT_SKRIPT = "/usr/local/bin/dialos-auskunft.py"
AUSKUNFT_SAETZE = {
    "wie viel uhr ist es": "uhrzeit",
    "wie ist die uhrzeit": "uhrzeit",
    "welchen tag haben wir": "datum",
    "welches datum haben wir": "datum",
}

NOTIZ_SKRIPT = "/usr/local/bin/dialos-notiz.py"
HILFE_SKRIPT = "/usr/local/bin/dialos-hilfe.py"
NOTIZ_SAETZE = {
    "einkaufszettel vorlesen": ("einkaufszettel", "vorlesen"),
    "notizen vorlesen": ("notizen", "vorlesen"),
    "brief vorlesen": ("brief", "vorlesen"),
    "einkauf erledigt": ("einkaufszettel", "loeschen"),
    "einkaufszettel wegwerfen": ("einkaufszettel", "loeschen"),
}

# Fernwartung (neu 2026-08-19). Beide Woerter am selben Tag gegen den Wortschatz
# geprueft - Vosk meldete kein "Ignoring word missing in vocabulary" -, und beide
# Kernwoerter sind eindeutig: "rufen" und "fernwartung" kommen in keinem anderen
# Satz der Grammatik vor.
#
# WARUM "fernwartung" DAS KERNWORT DES SCHLUSSSATZES IST und nicht "beenden":
# "beenden" steht zwar in dieser Grammatik in keinem zweiten Satz, aber der
# Nutzer kennt es als Schlusswort des Diktats. Ein Wort, das in zwei Rollen
# vorkommt, ist beim Sprechen zweideutig, auch wenn es die Grammatik nicht ist.
# Leer, solange die Saetze nicht in der Grammatik stehen (siehe dort). Die
# Zuordnung bleibt STEHEN und wird nicht geloescht: Sie ist der Ort, an dem der
# Zusammenhang dokumentiert ist, und beim Wiederfreigeben soll niemand sie neu
# erfinden muessen.
HILFE_SAETZE = {
    # "hilfe rufen": "starten",
    # "fernwartung beenden": "beenden",
}

# Nach so langer Stille schaltet sich die Erkennung von selbst ab
# (Stephan, 2026-08-17: zwei Minuten, mit Ansage). Der Grund ist nicht
# Stromsparen, sondern Sicherheit: Wer das "stoppen" vergisst, haette
# sonst dauerhaft ein offenes Mikrofon.
ZEITGRENZE_S = 120.0

# KURZE FRIST, SOLANGE KEIN BEFEHL KAM (neu 2026-08-20). Wer wirklich
# "Sprachsteuerung starten" sagt, sagt binnen Sekunden auch den Befehl - dafuer
# hat er ja eingeschaltet. Eine Einschaltung, auf die nichts folgt, war mit
# hoher Wahrscheinlichkeit keine.
#
# Gemessen an zwei Stunden vom 2026-08-20: Alle 7 Einschaltungen liefen in die
# Zwei-Minuten-Grenze, auf KEINE folgte ein Befehl - zusammen 14 Minuten scharfe
# Befehlsgrammatik, die niemand wollte. Mit 30 Sekunden waeren daraus 3,5
# Minuten geworden.
#
# 30 und nicht 20: Wer den Bildschirm nicht sieht, formuliert manchmal
# langsamer, und ihn mitten im Nachdenken abzuschalten waere aergerlich fuer
# nichts. Sobald EIN Befehl gekommen ist, gilt wieder die volle
# Zwei-Minuten-Grenze - dann ist ein Gespraech im Gange.
ERSTE_BEFEHL_FRIST_S = 30.0

# Erkannt wird nur, was BEIDES enthaelt: ein Ziel und das Wort
# "umschalten". Siehe Kopf der Datei - ohne die zweite Bedingung reicht
# ein beilaeufiges "windows" im Gespraech.
AUSLOESER = "umschalten"
ZIELE = {"linux": "gnome", "gnome": "gnome", "windows": "windows"}

# Kurz und immer gleich - der Nutzer hoert sie taeglich, da zaehlt
# Wiedererkennbarkeit mehr als Abwechslung. Aus Michaels Sicht
# formuliert, nicht als Statusmeldung ("Sprachsteuerung ist
# eingeschaltet").
# Die Ansagen sprechen den Nutzer AN (Stephan, 2026-08-19: "Das System soll
# ja persoenlich klingen"). "Ich hoere." ist eine Zustandsmeldung, "Ich hoere
# Dir zu." ist eine Zusage. Fuer jemanden, der das Geraet nur hoert, ist das
# der Unterschied zwischen einem Apparat und einem Gegenueber.
ANSAGE_AN = "Ich höre Dir zu."
# "Ich höre Dir nicht mehr zu." statt "Ich höre nicht mehr." (Stephan,
# 2026-08-19). Der kuerzere Satz ist zweideutig: Er kann auch heissen,
# dass das Geraet nichts mehr hoert - also kaputt ist. Mit "Dir" ist klar,
# dass es eine Entscheidung ist und kein Defekt.
ANSAGE_AUS = "Ich höre Dir nicht mehr zu."
# Sagt AUCH, warum sie kommt (Stephan, 2026-08-19). "Ich schalte die
# Sprachsteuerung wieder aus." war sachlich richtig und liess den Nutzer
# raten, weshalb - wer den Bildschirm nicht sieht, kann nicht nachsehen,
# ob er etwas falsch gemacht hat. Und sie sprach ihn nicht an, waehrend die
# drei anderen Ansagen es tun.
# "Du hast MIR eine Weile nichts gesagt" (Stephan, 2026-08-19) - das "mir" ist
# nicht Schmuck, es macht den Satz erst richtig. Der Zaehler laeuft ab dem
# letzten BEFEHL, nicht ab der letzten Aeusserung: ein erkanntes Bruchstueck aus
# einem Gespraech im Raum setzt ihn absichtlich NICHT zurueck, sonst hielte ein
# laufendes Radio die Sprachsteuerung endlos wach. Beim Test am 2026-08-19 stand
# genau das im Protokoll - 'es' um 11:08:18, Zeitgrenze um 11:08:46. "Du hast
# eine Weile nichts gesagt" waere in diesem Fall falsch gewesen; "mir nichts
# gesagt" ist es nicht.
ANSAGE_ZEITGRENZE = ("Du hast mir eine Weile nichts gesagt. "
                     "Ich höre Dir nicht mehr zu.")
ANSAGE_LAEUFT_SCHON = "Ich höre Dir schon zu."

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


# Das Protokoll wird IMMER geschrieben, nicht nur mit "--debug" (Fehler vom
# 2026-08-19). Vorher musste der Dienst zum Mitschreiben von Hand mit
# "--debug" neu gestartet werden - und weil er dazu mit "setsid" von der
# Sitzung geloest wurde, ueberlebte er das Abmelden. Nach einem
# Benutzerwechsel liefen dann ZWEI Befehlsdienste: jeder Befehl waere zweimal
# ausgefuehrt worden, und beide streiten sich um das Mikrofon.
#
# Dieselbe Lehre wie beim Diktat einen Tag vorher, nur an der anderen Stelle:
# Ein Protokoll, das man erst einschalten muss, ist beim Fehler nicht da.
# Die Pegelanzeige bleibt bewusst NUR auf dem Bildschirm - sie erzeugte am
# 2026-08-19 allein 4132 Zeilen gegen 13 echte.
PROTOKOLL = os.path.join(os.path.expanduser("~"), "dialos-sprachbefehl.log")


def melde(text):
    """Meldung MIT Zeitstempel - immer ins Protokoll, mit --debug auch auf den
    Bildschirm.

    Der Zeitstempel ist nicht Zierde (Fehler vom 2026-08-18): Beim Test der
    Diktat-Sperre stand im Protokoll ein erkannter Satz, und ohne Uhrzeit
    liess sich nicht feststellen, ob er WAEHREND des Diktats kam - also ob
    die Sperre versagt hat - oder davor. Ein Protokoll ohne Zeit kann
    Gleichzeitigkeit nicht belegen, und genau darum ging es.
    """
    zeile = f"{time.strftime('%H:%M:%S')}  {text}"
    if DEBUG:
        print("\n" + zeile, flush=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass          # ein fehlendes Protokoll darf keinen Befehl verhindern


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


def ist_phrase(gehoert, phrase, kernwort):
    """Beendet/beginnt diese Aeusserung die Sprachsteuerung?

    NICHT der volle Satz als Teilkette - das war der Fehler vom 2026-08-19.
    Stephan sagte "Sprachsteuerung starten", der Erkenner lieferte 'starten',
    und die Bedingung wies es ab. Damit liess sich die Sprachsteuerung nicht
    einschalten, und alles danach war unerreichbar - an der wichtigsten
    Stelle, denn dieser Satz ist das Tor zu allem.

    Dieselbe Lockerung wie beim Schlusssatz des Diktats einen Tag vorher, und
    dieselben drei Bedingungen:
      - das Kernwort muss vorkommen ("starten" bzw. "stoppen"),
      - es darf ausser Woertern der Phrase nichts weiter vorkommen,
      - und es darf KEIN "[unk]" dabei sein.

    Die dritte ist die wichtige: "[unk]" ist Vosks Kennzeichen dafuer, dass
    noch etwas anderes gesprochen wurde. Gemessen am 2026-08-18 ueber sieben
    Minuten Dauergerede lieferte eine solche Kleingrammatik genau zweimal ein
    Ergebnis ausser "[unk]" - beide Male, als der Satz wirklich gesagt wurde.
    """
    worte = gehoert.split()
    if not worte or "[unk]" in worte:
        return False
    # Ein Wort oder mehrere. Beim Einschalten sind es seit dem 2026-08-20 BEIDE
    # ("sprachsteuerung" UND "starten"), siehe die Begruendung dort.
    pflicht = (kernwort,) if isinstance(kernwort, str) else tuple(kernwort)
    if any(w not in worte for w in pflicht):
        return False
    # Bewusst als MENGE geprueft und nicht als Zeichenkette: Der Erkenner
    # liefert Woerter auch doppelt oder vertauscht ("sprachsteuerung
    # sprachsteuerung stoppen" kam am 2026-08-19 vor). Solange nichts
    # Fremdes dabei ist, zaehlt es.
    return set(worte) <= set(phrase.split())


def spricht_gerade():
    return os.path.exists(MARKIERUNG)


def diktat_laeuft():
    return os.path.exists(DIKTAT_MARKE)


NAMEN_SKRIPT = "/usr/local/bin/dialos-namen.py"


def anrede(satz):
    """Stellt den Nutzernamen voran, wo es Sinn macht - siehe dialos-namen.py.

    Geholt statt kopiert: Die Regel, WANN ein Name benutzt wird, gehoert an eine
    Stelle. Faellt das Modul aus, kommt der Satz unveraendert zurueck - eine
    Ansage darf nie davon abhaengen, dass ein Name eingetragen ist.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dialos_namen", NAMEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.anrede(satz)
    except Exception:
        return satz


def sprich(text):
    if os.access(SAY, os.X_OK):
        subprocess.run([SAY, text], capture_output=True, timeout=60)
    else:
        print(text)


# --- Mitschrift-Fenster -------------------------------------------------
# Stephans Wunsch vom 2026-08-19: Das Fenster soll aufgehen, wenn die
# Sprachsteuerung eingeschaltet wird, und zugehen, wenn sie ausgeht - von Hand
# oder durch die Zeitgrenze. Es haengt damit an der Sprachsteuerung und nicht
# am Anmelden: wo nicht gesprochen wird, gibt es auch nichts mitzuschreiben.
MITSCHRIFT = "/usr/local/bin/dialos-mitschrift.py"

# Wartezeit zwischen der letzten Protokollzeile und dem Schliessen des Fensters.
# Die Mitschrift sieht alle 0,4 s nach; wird sofort geschlossen, liest sie ihre
# eigenen letzten Zeilen nie - im Protokoll vom 2026-08-19 fehlte deshalb, WARUM
# die Sprachsteuerung aufgehoert hatte. Eine Sekunde ist reichlich Abstand und
# faellt beim Abschalten nicht auf, weil davor ohnehin eine Ansage laeuft.
NACHLAUF_S = 1.0


def mitschrift_gewuenscht():
    """Soll das Fenster mit der Sprachsteuerung aufgehen?

    Vorgabe ist AN, und zwar aus einem Grund, der ueber das Fenster
    hinausgeht: Das Support-Protokoll wird von der Mitschrift geschrieben.
    Waere das Fenster ab Werk aus, gaebe es beim Anruf auch nichts nachzulesen
    - genau der Fall, fuer den es gedacht ist. Wer den Bildschirm frei haben
    will, legt eine Datei ~/.config/dialos/mitschrift mit "aus" an.
    """
    pfad = os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        "dialos", "mitschrift")
    try:
        with open(pfad) as f:
            return f.read().strip().lower() not in ("aus", "nein", "0", "off")
    except OSError:
        return True


def mitschrift_pids():
    """PIDs laufender Mitschriften.

    Gesucht wird das Python-Skript, nicht das Terminal: gnome-terminal spaltet
    sich vom Aufruf ab und uebergibt an einen schon laufenden
    gnome-terminal-server, dessen PID nichts mit diesem Fenster zu tun hat.
    Endet dagegen das Skript, endet der Befehl des Fensters, und das Fenster
    schliesst sich von selbst.
    """
    gefunden = []
    try:
        eintraege = os.listdir("/proc")
    except OSError:
        return gefunden
    for eintrag in eintraege:
        if not eintrag.isdigit():
            continue
        try:
            with open(f"/proc/{eintrag}/cmdline", "rb") as f:
                zeile = f.read().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue          # Prozess ist inzwischen weg - kein Fehler
        if MITSCHRIFT in zeile:
            gefunden.append(int(eintrag))
    return gefunden


def mitschrift_oeffnen():
    """Fenster oeffnen - aber nur, wenn keines laeuft.

    Ohne diese Pruefung stuenden nach zwanzig Aktivierungen zwanzig Fenster
    uebereinander.
    """
    if not mitschrift_gewuenscht():
        return
    if mitschrift_pids():
        melde("  Mitschrift laeuft schon")
        return
    for kandidat in ("/usr/bin/gnome-terminal", "/usr/bin/x-terminal-emulator"):
        if os.access(kandidat, os.X_OK):
            terminal = kandidat
            break
    else:
        melde("  kein Terminal gefunden - keine Mitschrift")
        return
    # RUECKBLICK: Der Satz, der das Fenster oeffnet, steht schon im Protokoll,
    # bevor die Mitschrift zu lesen beginnt - "sprachsteuerung starten" fehlte
    # deshalb IMMER, im Fenster wie im Support-Protokoll (Stephans Test vom
    # 2026-08-19). 20 Sekunden nehmen ihn mit und dazu die Versuche davor, die
    # nicht erkannt wurden - fuer den Support die aufschlussreichere Haelfte.
    RUECKBLICK = "20"
    if terminal.endswith("gnome-terminal"):
        befehl = [terminal, "--title=DialOS - Mitschrift",
                  "--geometry=100x30", "--",
                  MITSCHRIFT, "--rueckblick", RUECKBLICK]
    else:
        # -e nimmt bei den meisten Terminals nur EINE Zeichenkette.
        befehl = [terminal, "-e", f"{MITSCHRIFT} --rueckblick {RUECKBLICK}"]
    try:
        subprocess.Popen(befehl, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        melde("  Mitschrift geoeffnet")
    except OSError as fehler:
        melde(f"  Mitschrift liess sich nicht oeffnen: {fehler}")


def mitschrift_schliessen():
    """Alle laufenden Mitschriften beenden; die Fenster gehen mit.

    ERST MELDEN, DANN WARTEN, DANN SCHLIESSEN. Vorher stand die Meldung hinter
    dem Beenden - das Fenster war beim Schreiben schon tot und konnte die Zeile
    nicht mehr lesen. Fuer den Zweck des Fensters ist das die falsche
    Reihenfolge: gerade die letzten Zeilen einer Sitzung sagen, warum sie zu
    Ende ging.
    """
    pids = mitschrift_pids()
    if not pids:
        return
    for pid in pids:
        melde(f"  Mitschrift wird geschlossen (PID {pid})")
    time.sleep(NACHLAUF_S)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass          # schon weg - dann ist das Ziel ja erreicht


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
        # "Linux Desktop" / "Windows Desktop", nicht "Linux" / "Windows"
        # (Stephans Benennung vom 2026-08-19). Der Code sagte hier nur "Linux",
        # waehrend docs/sprachbefehle.md schon die Fassung mit "Desktop"
        # auswies - aufgefallen am 2026-08-19 beim Pruefen aller Ansagen gegen
        # Stephans Grundsatz "es soll sich wie ein Dialog anfuehlen". Der ganze
        # Satz bleibt: ein Dialogpartner antwortet in Saetzen, und die
        # Kurzform stand hier ohnehin nie.
        sprich("Der Schreibtisch steht schon auf Linux Desktop."
               if ziel == "gnome"
               else "Der Schreibtisch steht schon auf Windows Desktop.")
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
        sprich("Ich kann das Diktat nicht starten.")


# Wie lange das Fenster braucht, um wirklich vom Bildschirm zu verschwinden.
# Ohne diese Pause steht es noch auf dem Foto - der Fenstermanager raeumt es
# nicht in dem Augenblick weg, in dem der Prozess endet.
FOTO_NACHLAUF_S = 0.8


def bildschirmfoto():
    """Bildschirmfoto - OHNE das Mitschrift-Fenster (Stephan, 2026-08-21).

    WARUM DAS FENSTER WEG MUSS: Die Mitschrift ist DialOS' eigene Anzeige, ein
    Terminal mit hundert Spalten mitten auf dem Schirm. Auf einem Foto fuer den
    Support verdeckt sie genau das, was der Helfer sehen will - und zeigt ihm
    dafuer Zeilen, die er im Support-Protokoll ohnehin lesen kann.

    DESHALB SYNCHRON, anders als bei der Auskunft: schliessen, fotografieren,
    wieder oeffnen. Das haelt die Schleife rund vier Sekunden auf. Das ist
    vertretbar, weil der Nutzer gerade selbst einen Befehl gesprochen hat und
    ohnehin auf die Ansage wartet - und die Alternative waere ein Foto, auf dem
    das Wichtigste verdeckt ist.

    WIEDER GEOEFFNET WIRD NUR, WENN VORHER EINES LIEF. Wer die Mitschrift
    abgeschaltet hat, bekommt sie nicht durch ein Bildschirmfoto zurueck.
    """
    if not os.access(FOTO_SKRIPT, os.X_OK):
        sprich("Ich kann das Bildschirmfoto nicht finden.")
        return
    lief = bool(mitschrift_pids())
    if lief:
        melde("  Mitschrift wird fuers Foto geschlossen")
        mitschrift_schliessen()
        time.sleep(FOTO_NACHLAUF_S)
    try:
        subprocess.run([FOTO_SKRIPT], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=60)
        melde("Bildschirmfoto erstellt")
    except Exception as fehler:
        melde(f"Bildschirmfoto liess sich nicht erstellen: {fehler}")
        sprich("Ich kann das nicht ausführen.")
    finally:
        if lief:
            mitschrift_oeffnen()


def auskunft(was):
    """Startet die Auskunft und kehrt sofort zurueck.

    Nicht abwarten, aus demselben Grund wie bei den Notizen: Der Dienst muss
    seine Schleife weiterlaufen lassen. Uhrzeit und Datum sind zwar in
    Millisekunden bestimmt, aber das Sprechen dauert.
    """
    if not os.access(AUSKUNFT_SKRIPT, os.X_OK):
        sprich("Ich kann die Auskunft nicht finden.")
        return
    try:
        subprocess.Popen([AUSKUNFT_SKRIPT, was],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        melde(f"Auskunft {was!r} gestartet")
    except Exception as fehler:
        melde(f"Auskunft liess sich nicht starten: {fehler}")
        sprich("Ich kann das nicht ausführen.")


def hilfe_aktion(was):
    """Startet oder beendet die Fernwartung und kehrt sofort zurueck.

    Nicht abwarten, wie beim Diktat und bei den Notizen: Das Starten enthaelt
    eine Rueckfrage, die selbst zuhoert, dazu sechs Sekunden Anmeldung beim
    Vermittlungsdienst und das zweimalige Vorlesen der Nummer. Waehrend dieser
    Zeit muss dieser Dienst seine Schleife weiterlaufen lassen.
    """
    if not os.access(HILFE_SKRIPT, os.X_OK):
        sprich("Ich kann die Fernwartung nicht finden.")
        return
    try:
        subprocess.Popen([HILFE_SKRIPT, was],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        melde(f"Fernwartung {was!r} gestartet")
    except OSError as fehler:
        melde(f"Fernwartung liess sich nicht starten: {fehler}")
        sprich("Ich kann das nicht ausführen.")


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
        sprich("Ich kann das nicht ausführen.")


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
        # MIT Namen: Wenn etwas nicht geht, muss klar sein, wer gemeint ist.
        sprich(anrede("Ich finde kein Mikrofon. Die Sprachsteuerung ist aus."))
        return 1

    # Eine Startzeile ins Protokoll, damit "leeres Protokoll" nicht zweideutig
    # ist (Fehler vom 2026-08-19). Ohne sie sieht "es ist nichts passiert"
    # genauso aus wie "der Dienst laeuft gar nicht" - und beim Suchen nach
    # einem Fehler ist das der Unterschied zwischen zwei ganz verschiedenen
    # Vermutungen. Dieselbe Ueberlegung, die beim Diktat schon zur Meldung
    # "Diktat laeuft - ich hoere nicht zu" gefuehrt hat.
    melde(f"=== Befehlsdienst gestartet, Quelle {quelle} ===")

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
    # Gleich gesetzt: Es kam noch kein Befehl. Bewegt sich
    # letzte_aktivitaet spaeter darueber hinaus, war einer dabei - daran
    # haengt, welche der beiden Fristen gilt.
    an_seit = letzte_aktivitaet
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

            # Welche Frist gilt: die kurze, solange seit dem Einschalten kein
            # Befehl kam, sonst die lange. Erkennbar daran, ob letzte_aktivitaet
            # sich seit dem Einschalten bewegt hat - jeder ausgefuehrte Befehl
            # setzt sie neu.
            frist = (ZEITGRENZE_S if letzte_aktivitaet > an_seit
                     else ERSTE_BEFEHL_FRIST_S)
            if hoert_zu and time.time() - letzte_aktivitaet > frist:
                hoert_zu = False
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
                # PROTOKOLLIEREN, UND ZWAR VOR DER ANSAGE (2026-08-19). Bisher
                # stand ueber die Zeitgrenze nichts im Protokoll - nur, dass die
                # Mitschrift geschlossen wurde. Damit stand dort die Wirkung und
                # nicht die Ursache, und im Support-Protokoll fehlte die Antwort
                # auf die Frage, warum die Sprachsteuerung aufgehoert hat.
                # Dieselbe Luecke wie am Morgen bei "erkannt:", nur am anderen
                # Ende der Sitzung.
                #
                # Vor der Ansage, weil die Ansage 3,5 s dauert - in dieser Zeit
                # liest die Mitschrift die Zeile noch, bevor sie zugeht.
                melde(f"Zeitgrenze: {frist:.0f} s ohne Befehl")
                # Zwei Ansagen fuer zwei Lagen. Nach einem Gespraech gehoert die
                # Begruendung dazu. War dagegen ueberhaupt kein Befehl dabei, war
                # das Einschalten vermutlich Geraeusch - dann ist die kurze
                # Ansage richtig: Eine lange Erklaerung fuer etwas, das der
                # Nutzer nie ausgeloest hat, ist selbst nur Laerm.
                sprich(ANSAGE_ZEITGRENZE if letzte_aktivitaet > an_seit
                       else ANSAGE_AUS)
                mitschrift_schliessen()
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
                # Immer protokollieren: Diese Zeile erklaert Luecken im
                # Protokoll. Ohne sie sieht eine Pause zwischen zwei
                # Befehlen aus wie ein Aussetzer.
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
                        sprich(anrede("Ich finde kein Mikrofon mehr."))
                        mikrofon_fehlt_gemeldet = True
                    time.sleep(5)
                    continue
                if mikrofon_fehlt_gemeldet:
                    sprich("Ich höre Dich wieder.")
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
                    # Immer protokollieren: Uebersteuerung ist die Ursache, an
                    # der am 2026-08-16 die ganze Erkennung gescheitert ist
                    # (60 dB ab Werk). Tritt sie wieder auf, muss es im
                    # Protokoll stehen und nicht nur auf einem Bildschirm, den
                    # niemand ansieht.
                    melde("(uebersteuert - Pegel wird neu gerichtet)")
                    pegel_richten()
                    letzte_pegelkorrektur = time.time()
                    saettigungen = 0
            else:
                saettigungen = 0

            if not erkenner.AcceptWaveform(block):
                continue
            text = json.loads(erkenner.Result()).get("text", "")
            # KEIN "if DEBUG" davor (Fehler vom 2026-08-19). Das ist die
            # wichtigste Zeile des ganzen Protokolls - was der Dienst gehoert
            # hat. Beim Umbau auf "immer protokollieren" blieb der alte
            # Vorbehalt stehen, und heraus kam ein Protokoll, in dem die
            # AUSGEFUEHRTE Aktion stand, aber nicht der Satz, der sie
            # ausgeloest hat. Genau das Gegenteil dessen, was man beim
            # Fehlersuchen braucht.
            if text:
                melde(f"erkannt: {text!r}")
            if not text:
                continue
            worte = text.split()
            satz = " ".join(worte)

            # --- Zustandswechsel: anmelden ---
            # "starten" ALLEIN genuegt nur im ausgeschalteten Zustand. Dort
            # kennt die Grammatik genau einen Satz, das Wort kann also nichts
            # anderes bedeuten. Im eingeschalteten Zustand gibt es zusaetzlich
            # "diktat starten" - ein blosses 'starten' waere dann
            # zweideutig, und ein falsch geratenes Diktat waere schlimmer als
            # ein nicht erkannter Satz.
            # KERNWORT IST "sprachsteuerung", NICHT "starten" (2026-08-20).
            #
            # Gestern galt "starten" als Kernwort, weil der Erkenner am
            # 2026-08-19 einmal nur dieses Wort geliefert hatte und die
            # Sprachsteuerung sich dadurch nicht einschalten liess. Die
            # Lockerung hat den Fehler behoben und einen groesseren geschaffen.
            #
            # GEMESSEN am 2026-08-20 ueber 157 aufgezeichnete Aeusserungen:
            #
            #     'starten' allein            18x   <- fast alles Geraeusch
            #     'sprachsteuerung starten'    4x   <- die echten Male
            #     'sprachsteuerung' allein     5x
            #
            # Die Sprachsteuerung hat sich also 18-mal von selbst eingeschaltet,
            # weil "starten" kurz ist und aus Umgebungsgeraeusch entsteht. Und
            # weil danach die volle Grammatik gilt, kam am 2026-08-20 um
            # 14:04:43 aus reinem Geraeusch der vollstaendige Satz
            # 'hilfe rufen' - die Fernwartung wurde angefordert, ohne dass
            # jemand etwas gesagt hatte. Nur die Ja/Nein-Rueckfrage hat es
            # verhindert.
            #
            # "sprachsteuerung" ist lang und markant und kam in nur 16 von 157
            # Aeusserungen ueberhaupt vor. Es zu verlangen kostet den Fall, dass
            # der Erkenner GENAU dieses Wort verschluckt - dann muss der Nutzer
            # den Satz wiederholen. Das ist eine Unbequemlichkeit; ein
            # Mikrofon, das sich unaufgefordert einschaltet, ist es nicht.
            # BEIDE WOERTER, seit 2026-08-20 nachmittags. Die Umstellung vom
            # Kernwort "starten" auf "sprachsteuerung" am selben Vormittag hat
            # die Fehlstarts von 30 auf 7 in zwei Stunden gedrueckt - aber vier
            # der sieben kamen aus 'sprachsteuerung' ALLEIN, und auf keinen
            # einzigen der sieben folgte ein Befehl. Zwei bestimmte Woerter
            # hintereinander fallen im Gespraech praktisch nicht; eines schon.
            #
            # Preis: Verschluckt der Erkenner eines der beiden, muss der Nutzer
            # den Satz wiederholen. Das ist genau der Fehler vom 2026-08-19, der
            # zur Lockerung gefuehrt hat - er ist jetzt bewusst in Kauf genommen,
            # weil die Gegenrechnung inzwischen gemessen vorliegt. Wiederholen
            # ist eine Unbequemlichkeit; ein Mikrofon, das sich von selbst
            # scharf schaltet, ist es nicht.
            if (ist_phrase(satz, STARTSATZ, ("sprachsteuerung", "starten"))
                    if not hoert_zu else STARTSATZ in satz):
                # In BEIDEN Faellen, und VOR der Ansage. Vor der Ansage, weil
                # das Fenster einen Moment braucht und die Ansage ohnehin gut
                # eine Sekunde dauert - so steht es, wenn der Nutzer den ersten
                # Befehl sagt. In beiden Faellen wegen Stephans Test vom
                # 2026-08-19: Die Sprachsteuerung lief schon, also lief der
                # Aufruf nur im else-Zweig und kein Fenster ging auf. Wer
                # "Sprachsteuerung starten" sagt, will, dass etwas passiert -
                # und ein von Hand geschlossenes Fenster kaeme sonst nie
                # zurueck, ohne die Steuerung erst auszuschalten.
                mitschrift_oeffnen()
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
                #
                # BEIDE GEMEINSAM UND GLEICH, und zwar HIER. Der erste Versuch
                # setzte an_seit vor sprich(ANSAGE_AN) - die Ansage dauert gut
                # eine Sekunde, danach war letzte_aktivitaet groesser als
                # an_seit, und die Bedingung "es kam schon ein Befehl" war von
                # Anfang an wahr. Ergebnis: Die kurze Frist griff nie, im Test
                # vom 2026-08-20 um 17:42 lief es in die vollen 120 s.
                #
                # Der eigene Test hatte das nicht gefunden, weil er die
                # ENTSCHEIDUNGSFUNKTION geprueft hat und nicht die REIHENFOLGE.
                # Zwei Werte, die gleich sein muessen, gehoeren in eine
                # Zuweisung - dann kann keine Ansage dazwischenrutschen.
                letzte_aktivitaet = an_seit = time.time()
                continue

            # Ist die Erkennung aus, kann hier nichts anderes mehr kommen -
            # die Grammatik kennt in diesem Zustand keinen weiteren Satz.
            if not hoert_zu:
                continue

            # --- Zustandswechsel: abmelden ---
            # "stoppen" kommt in keinem anderen Satz der Grammatik vor -
            # allein genuegt es deshalb immer.
            if ist_phrase(satz, STOPPSATZ, "stoppen"):
                hoert_zu = False
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
                sprich(ANSAGE_AUS)
                # NACH der Ansage geschlossen, damit die letzte Zeile noch im
                # Fenster steht, solange Michael spricht.
                mitschrift_schliessen()
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

            # --- Befehl: Bildschirmfoto ---
            if satz in FOTO_SAETZE:
                bildschirmfoto()
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            # --- Befehle: Auskunft ---
            if satz in AUSKUNFT_SAETZE:
                auskunft(AUSKUNFT_SAETZE[satz])
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            # --- Befehle: Fernwartung ---
            # VOR der Umschaltung, wie Diktat und Auskunft: Diese Saetze
            # enthalten "umschalten" nicht.
            if satz in HILFE_SAETZE:
                hilfe_aktion(HILFE_SAETZE[satz])
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
