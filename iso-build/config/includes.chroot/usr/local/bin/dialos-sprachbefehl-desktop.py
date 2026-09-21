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

import collections
import json
import os
import signal
import subprocess
import importlib.util
import sys
import threading
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

# ensure_ascii=False IST PFLICHT (Fehler gefunden 2026-09-14). Ohne das schreibt
# json.dumps ein "ö" als "\\u00f6", Vosk liest das woertlich und meldet
# "Ignoring word missing in vocabulary" - fuer JEDES Wort mit Umlaut oder ß.
# Genau daraus entstanden die Befunde "spaeter", "loeschen", "zuruecksetzen"
# und "aufraeumen fehlen im Wortschatz". Sie fehlen nicht.
GRAMMATIK_AUS = json.dumps([STARTSATZ, "[unk]"], ensure_ascii=False)
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
    # Dritte Formulierung seit 2026-09-15: Stephan sagte vor seiner dritten
    # Brief-Probe von sich aus "brief erstellen", Vosk erkannte den Satz
    # woertlich - und es kam nur "Das war kein Befehl". Stephans Freigabe:
    # "Ja, nimm Brief erstellen dazu". Passt zu "bildschirmfoto erstellen".
    "brief erstellen",
    "einkaufszettel vorlesen",
    "notizen vorlesen",
    "brief vorlesen",
    "einkauf erledigt",
    "einkaufszettel wegwerfen",
    # Seit 2026-09-14 (Stephans Wahl nach Hoerprobe). Beide galten seit August
    # als "nicht im Wortschatz" - das war ein Pruefehler (Umlaute, siehe
    # GRAMMATIK_AUS). Piper -> Vosk mit Anna und Michael: woertlich erkannt,
    # alle 28 Saetze danach weiter fehlerfrei.
    "einkaufszettel löschen",
    "wie viel uhr ist es",
    "wie ist die uhrzeit",
    "wie spät ist es",
    "welchen tag haben wir",
    "welches datum haben wir",
    # Wetter wieder (2026-09-16), mit Rueckfall-Ort - siehe dialos-auskunft.py.
    "wie ist das wetter",
    "wie wird das wetter",
    # UEBERSICHT UND EHRLICHE ANTWORTEN (Stephan, 2026-09-16: "Muessen wir fuer
    # alles, was der Nutzer direkt Michael/Anna fragt und wo es keine Antwort
    # gibt, eine Art Rueckfall-Antwort geben!"). Seine Wahl: klare
    # Standard-Antwort, "Was kann ich sagen", und erwartbare Fragen mit ehrlicher
    # Antwort - jede wird als WUNSCH protokolliert, damit sichtbar wird, was
    # Nutzer wirklich wollen. Alle Woerter im Wortschatz geprueft.
    "was kann ich sagen",
    "was kannst du",
    # BEFEHLSUEBERSICHT (Stephan, 2026-09-16: "Als blinder Nutzer kann man sich
    # nicht alle Befehle merken"). Alle Befehle oder ein Thema - die Texte
    # entstehen aus den Tabellen unten, siehe befehls_themen(). Alle Woerter im
    # Wortschatz geprueft ("befehlsliste" fehlt dort, deshalb "alle befehle").
    "alle befehle vorlesen",
    "befehle für fragen",
    "befehle für briefe",
    "befehle für notizen",
    "befehle für den einkauf",
    "befehle für den bildschirm",
    "befehle für das diktat",
    "nachrichten vorlesen",
    "was gibt es neues",
    "radio einschalten",
    "musik abspielen",
    "jemanden anrufen",
    "mails vorlesen",
    "termine vorlesen",
    "was steht heute an",
    # Bildschirmfoto (Stephan, 2026-08-21). Zwei Formulierungen wie ueberall.
    # Das Foto ist nicht fuer den Nutzer - er sieht es nicht -, sondern fuer
    # den sehenden Helfer und den Support: "Was steht da gerade?"
    "bildschirmfoto erstellen",
    "bildschirmfoto machen",
    # Dritte Formulierung seit 2026-09-14: Stephan hat an dem Tag zweimal von
    # sich aus "bildschirmfoto aufnehmen" gesagt, und Vosk hat den Satz beide
    # Male woertlich erkannt - nur war er kein Befehl ("Das war kein Befehl").
    # Passt zu "notiz aufnehmen". Stephans Freigabe: "Ja, dazunehmen".
    "bildschirmfoto aufnehmen",
    # Drucken (Stephans Vorgabe vom 2026-08-21). Der Brief traegt seine
    # Fusszeile schon; Zettel und Notizen bekommen sie erst beim Drucken -
    # ein Blatt Papier verlaesst das Haus, eine Notiz auf dem Schirm nicht.
    "brief drucken",
    # PDF sichtbar ablegen (Stephan, 2026-09-15: "Koennen wir pdf erstellen
    # hinzufuegen?"). "pdf" steht im Wortschatz des kleinen Modells (geprueft).
    # Die Formulierung ist dieselbe, die Anna nach dem Diktat nennt.
    "brief als pdf speichern",
    "einkaufszettel drucken",
    "notizen drucken",
    # Einzahl als zweite Formulierung: Am 2026-08-22 hat Vosk beim Test
    # "notiz drucken" verstanden. Beide Woerter stehen in der Grammatik
    # ("notiz aufnehmen", "notizen drucken"), das Netz darf sie also
    # kombinieren - der Satz war dann keiner, und es geschah nichts.
    "notiz drucken",
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
], ensure_ascii=False)

# ERWEITERUNGEN MELDEN SICH MIT EINER JSON-DATEI AN, statt hier eingetragen zu
# werden. Der Entwurf steht in docs/erweiterungen.md; die Kernregel ist, dass
# die Grammatik pro Erweiterung um GENAU EINEN Satz waechst - ihren Startsatz.
# Alles Weitere erkennt die Erweiterung selbst, solange sie laeuft.
#
# WARUM NICHT MEHR: Vosk baut aus der Satzliste ein WORTNETZ und darf Woerter
# aus verschiedenen Saetzen kombinieren. Bei 27 Saetzen standen am 2026-08-22
# bereits 382 erlaubte Wortkombinationen ohne Befehl im Protokoll, und die Zahl
# waechst nicht linear. Duerfte jede Erweiterung zwanzig Saetze beisteuern,
# waere dieser Mechanismus der, der einen gerade entschaerften Fehler wieder
# aufreisst.
#
# EIN KAPUTTES MANIFEST DARF DEN DIENST NICHT MITREISSEN. Die Sprachsteuerung
# ist das Einzige, womit der Nutzer das Geraet noch erreicht - sie faellt
# nicht wegen einer fehlerhaften Zusatzdatei aus. Deshalb wird jeder Fehler
# hier gefangen und nur gemeldet.
ERWEITERUNGEN_ORDNER = "/usr/local/share/dialos/erweiterungen"
ERWEITERUNG_WERKZEUG = "/usr/local/bin/dialos-erweiterung.py"


def erweiterungen_lesen():
    """Startsatz -> Manifest, aus den angemeldeten Erweiterungen."""
    zuordnung = {}
    try:
        spec = importlib.util.spec_from_file_location(
            "dialos_erweiterung", ERWEITERUNG_WERKZEUG)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        zuordnung = modul.satz_zu_erweiterung()
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        print(f"Erweiterungen nicht lesbar: {fehler}", file=sys.stderr)
    return zuordnung


PROGRAMM_WERKZEUG = "/usr/local/bin/dialos-programm.py"


def programme_lesen():
    """Satz -> Programm, aus dialos-programm.py.

    NICHT HIER NOCHMAL AUFSCHREIBEN (Stephan, 2026-09-21: "Wir muessen doch
    sowieso eine Liste von Befehlen machen, die dann die Programme startet").
    Die Liste steht in dialos-programm.py, samt Begruendung, welcher Aufruf
    welches Fenster oeffnet. Eine zweite hier liefe beim naechsten Programm
    auseinander - dieselbe Falle wie bei den Erweiterungen.
    """
    try:
        spec = importlib.util.spec_from_file_location(
            "dialos_programm", PROGRAMM_WERKZEUG)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.saetze()
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        print(f"Programmliste nicht lesbar: {fehler}", file=sys.stderr)
        return ()


ERWEITERUNG_SAETZE = erweiterungen_lesen()
PROGRAMM_SAETZE = programme_lesen()

if ERWEITERUNG_SAETZE:
    _liste = json.loads(GRAMMATIK_AN)
    # "[unk]" bleibt der letzte Eintrag - es ist der Auffangeintrag, und die
    # Reihenfolge ist in der Grammatik nicht bedeutungslos.
    _liste = ([x for x in _liste if x != "[unk]"]
              + [s for s in ERWEITERUNG_SAETZE if s not in _liste]
              + ["[unk]"])
    GRAMMATIK_AN = json.dumps(_liste, ensure_ascii=False)

if PROGRAMM_SAETZE:
    _liste = json.loads(GRAMMATIK_AN)
    _liste = ([x for x in _liste if x != "[unk]"]
              + [s for s in PROGRAMM_SAETZE if s not in _liste]
              + ["[unk]"])
    GRAMMATIK_AN = json.dumps(_liste, ensure_ascii=False)

BEFEHLSSAETZE = tuple(x for x in json.loads(GRAMMATIK_AN)
                      if x not in ("[unk]", STARTSATZ, STOPPSATZ))

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
    "brief erstellen": "brief",
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
DRUCK_SKRIPT = "/usr/local/bin/dialos-drucken.py"
DRUCK_SAETZE = {
    "brief drucken": "brief",
    "einkaufszettel drucken": "einkaufszettel",
    "notizen drucken": "notizen",
    "notiz drucken": "notizen",
}
FOTO_SKRIPT = "/usr/local/bin/dialos-bildschirmfoto.py"
FOTO_SAETZE = ("bildschirmfoto erstellen", "bildschirmfoto machen",
               "bildschirmfoto aufnehmen")
AUSKUNFT_SKRIPT = "/usr/local/bin/dialos-auskunft.py"
AUSKUNFT_SAETZE = {
    "wie viel uhr ist es": "uhrzeit",
    "wie ist die uhrzeit": "uhrzeit",
    "wie spät ist es": "uhrzeit",
    "welchen tag haben wir": "datum",
    "welches datum haben wir": "datum",
    "wie ist das wetter": "wetter",
    "wie wird das wetter": "wetter",
}
UEBERSICHT_SAETZE = ("was kann ich sagen", "was kannst du")
ANSAGE_UEBERSICHT = (
    "Du kannst mich fragen: Wie spät ist es. Welchen Tag haben wir. Wie ist das "
    "Wetter. Für Briefe: Brief erstellen, Brief vorlesen, Brief drucken, Brief als "
    "PDF speichern. Für Notizen: Notiz aufnehmen, Notizen vorlesen. Für den "
    "Einkauf: Einkaufszettel aufnehmen, Einkaufszettel vorlesen. Außerdem: "
    "Bildschirmfoto machen. Und zum Schluss: Sprachsteuerung stoppen. "
    "Alle Befehle hörst Du mit: Alle Befehle vorlesen.")

# ALLE BEFEHLE ZUM ANHOEREN (Stephan, 2026-09-16: "eine Audiodatei ..., wo alle
# bestehenden und noch folgenden Befehle enthalten sind, und dem Nutzer einen
# Befehl geben, womit er sich diese vorsprechen lassen kann").
#
# AUS DEN TABELLEN ERZEUGT, NICHT VON HAND GESCHRIEBEN: Ein neuer Satz in
# DIKTAT_SAETZE, NOTIZ_SAETZE, DRUCK_SAETZE, AUSKUNFT_SAETZE oder FOTO_SAETZE
# steht damit von selbst in der Uebersicht. Fehlt fuer eine neue Aktion die
# Beschriftung, erscheint der Satz unter "Ausserdem" - und
# befehle_ohne_uebersicht() meldet beim Start jeden Satz der Grammatik, der
# nirgends vorkommt.
#
# NACH THEMEN, weil die ganze Liste rund zwei Minuten dauert und sich in einem
# Stueck niemand merkt. Jedes Thema wird einzeln gesprochen (sprich() hat 60 s
# Zeitgrenze) und liegt als fertige Audiodatei im Speicher von dialos-say.py -
# befehle_vorbereiten() erzeugt sie kurz nach dem Start im Hintergrund.
UEBERSICHT_THEMEN_SAETZE = {
    "befehle für fragen": "fragen",
    "befehle für briefe": "briefe",
    "befehle für notizen": "notizen",
    "befehle für den einkauf": "einkauf",
    "befehle für den bildschirm": "bildschirm",
    "befehle für das diktat": "diktat",
}
ALLE_BEFEHLE_SATZ = "alle befehle vorlesen"
THEMEN_NAMEN = {"fragen": "Fragen", "briefe": "Briefe", "notizen": "Notizen",
                "einkauf": "den Einkauf", "bildschirm": "den Bildschirm",
                "diktat": "das Diktat", "erweiterungen": "Erweiterungen"}
# (Thema, Beschriftung) je Aktion. Schluessel: (Tabelle, Wert der Tabelle).
AKTIONEN = {
    ("auskunft", "uhrzeit"): ("fragen", "Die Uhrzeit"),
    ("auskunft", "datum"): ("fragen", "Das Datum"),
    ("auskunft", "wetter"): ("fragen", "Das Wetter"),
    ("diktat", "brief"): ("briefe", "Einen Brief diktieren"),
    ("notiz", ("brief", "vorlesen")): ("briefe", "Den Brief vorlesen"),
    ("druck", "brief"): ("briefe", "Den Brief drucken"),
    ("notiz", ("brief", "pdf")): ("briefe", "Den Brief als PDF speichern"),
    ("diktat", "notizen"): ("notizen", "Eine Notiz diktieren"),
    ("notiz", ("notizen", "vorlesen")): ("notizen", "Die Notizen vorlesen"),
    ("druck", "notizen"): ("notizen", "Die Notizen drucken"),
    ("diktat", "einkaufszettel"): ("einkauf", "Den Einkaufszettel diktieren"),
    ("notiz", ("einkaufszettel", "vorlesen")): ("einkauf", "Den Einkaufszettel vorlesen"),
    ("druck", "einkaufszettel"): ("einkauf", "Den Einkaufszettel drucken"),
    ("notiz", ("einkaufszettel", "loeschen")): ("einkauf", "Den Einkaufszettel leeren"),
    ("foto", None): ("bildschirm", "Ein Bildschirmfoto für Deinen Helfer"),
    ("umschalten", "gnome"): ("bildschirm", "Linux-Ansicht"),
    ("umschalten", "windows"): ("bildschirm", "Windows-Ansicht"),
}
THEMEN_REIHENFOLGE = ("fragen", "briefe", "notizen", "einkauf", "bildschirm", "diktat",
                      "erweiterungen")
GROSS_SCHREIBEN = {"pdf": "PDF", "linux": "Linux", "gnome": "Gnome", "windows": "Windows",
                   "brief": "Brief", "notiz": "Notiz", "notizen": "Notizen",
                   "einkaufszettel": "Einkaufszettel", "einkauf": "Einkauf",
                   "bildschirmfoto": "Bildschirmfoto", "uhrzeit": "Uhrzeit",
                   "tag": "Tag", "uhr": "Uhr", "datum": "Datum", "wetter": "Wetter",
                   "diktat": "Diktat", "satz": "Satz", "absatz": "Absatz", "zeile": "Zeile",
                   "betreff": "Betreff", "befehle": "Befehle", "fragen": "Fragen",
                   "briefe": "Briefe", "bildschirm": "Bildschirm",
                   "sprachsteuerung": "Sprachsteuerung"}


def gesprochen(satz):
    """"brief als pdf speichern" -> "Brief als PDF speichern" (fuer Anzeige und Piper)."""
    worte = [GROSS_SCHREIBEN.get(w, w) for w in satz.split()]
    if worte:
        worte[0] = worte[0][:1].upper() + worte[0][1:]
    return " ".join(worte)


def diktat_befehle():
    """Die Befehle IM Diktat - aus dialos-diktat.py geholt, wo sie gelten."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("diktat_befehle", DIKTAT_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        schluss, loeschen, wiederholen = (modul.SCHLUSSSATZ, modul.BEFEHL_LOESCHEN,
                                          modul.BEFEHL_WIEDERHOLEN)
    except Exception:
        schluss, loeschen, wiederholen = "diktat beenden", "satz löschen", "satz wiederholen"
    return [
        ("Einen neuen Absatz", ["absatz", "neuer absatz"]),
        ("Eine neue Zeile", ["neue zeile"]),
        ("Den letzten Satz streichen, mit kurzer Pause davor und danach", [loeschen]),
        ("Den letzten Satz noch einmal hören, ebenso mit Pause", [wiederholen]),
        ("Eine Betreffzeile, ganz am Anfang des Briefs", ["betreff"]),
        ("Alles bisher Diktierte verwerfen und neu beginnen, mit Rückfrage", ["von vorne"]),
        ("Das Diktat abbrechen, ohne etwas zu speichern, mit Rückfrage", ["alles verwerfen"]),
        ("Eine Mailadresse Zeichen für Zeichen einfügen", ["mailadresse buchstabieren"]),
        ("Die eigene Mailadresse einsetzen: im Satz sagen", ["meine mailadresse"]),
        ("Das Diktat beenden, nach einer kurzen Pause", [schluss]),
    ]


def befehls_themen():
    """{thema: [(beschriftung, [saetze])]} aus den Befehlstabellen."""
    zuordnung = collections.OrderedDict()

    def dazu(schluessel, satz):
        thema, beschriftung = AKTIONEN.get(schluessel, ("ausserdem", None))
        eintraege = zuordnung.setdefault(thema, collections.OrderedDict())
        eintraege.setdefault(beschriftung or gesprochen(satz), []).append(satz)

    for satz, wert in AUSKUNFT_SAETZE.items():
        dazu(("auskunft", wert), satz)
    for satz, wert in DIKTAT_SAETZE.items():
        dazu(("diktat", wert), satz)
    for satz, wert in NOTIZ_SAETZE.items():
        dazu(("notiz", wert), satz)
    for satz, wert in DRUCK_SAETZE.items():
        dazu(("druck", wert), satz)
    for satz in FOTO_SAETZE:
        dazu(("foto", None), satz)
    for satz in BEFEHLSSAETZE:
        worte = satz.split()
        if AUSLOESER in worte:
            ziel = next((ZIELE[w] for w in worte if w in ZIELE), None)
            dazu(("umschalten", ziel), satz)
    zuordnung["diktat"] = collections.OrderedDict(diktat_befehle())
    # ERWEITERUNGEN GEHOEREN IN DIE UEBERSICHT (2026-09-18). Beim Start meldete
    # der Dienst "Befehle ohne Platz in der Uebersicht: ['unterlagen
    # durchsuchen']" - der Startsatz stand in der Grammatik, aber in keiner
    # Ansage. Fuer jemanden, der den Bildschirm nicht sieht, ist ein Befehl, den
    # niemand nennt, so gut wie nicht vorhanden. Die Beschriftung kommt aus dem
    # Manifest ("beschreibung"), damit jede Erweiterung sich selbst erklaert.
    for satz, manifest in sorted(ERWEITERUNG_SAETZE.items()):
        beschriftung = (manifest.get("beschreibung") or manifest.get("name")
                        or gesprochen(satz))
        eintraege = zuordnung.setdefault("erweiterungen", collections.OrderedDict())
        eintraege.setdefault(beschriftung, []).append(satz)
    return {thema: list(eintraege.items()) for thema, eintraege in zuordnung.items()}


def thema_text(thema, themen=None):
    themen = themen or befehls_themen()
    teile = [f"Befehle für {THEMEN_NAMEN.get(thema, thema)}."]
    for beschriftung, saetze in themen.get(thema, []):
        gesagt = ". Oder: ".join(gesprochen(x) for x in saetze)
        teile.append(f"{beschriftung}: {gesagt}.")
    return " ".join(teile)


def alle_befehle_texte():
    """Die ganze Uebersicht als Folge einzelner Ansagen - je Thema eine."""
    themen = befehls_themen()
    einzeln = ", ".join(gesprochen(x) for x in UEBERSICHT_THEMEN_SAETZE)
    texte = [f"Hier sind alle Befehle, nach Themen. Ein einzelnes Thema hörst Du "
             f"mit: {einzeln}. Zuerst: Du schaltest mich ein mit Sprachsteuerung "
             f"starten, und aus mit Sprachsteuerung stoppen."]
    for thema in THEMEN_REIHENFOLGE:
        texte.append(thema_text(thema, themen))
    if themen.get("ausserdem"):
        texte.append(" ".join(["Außerdem:"] + [f"{gesprochen(x[1][0])}."
                                               for x in themen["ausserdem"]]))
    texte.append("Das waren alle Befehle.")
    return texte


def befehle_ohne_uebersicht():
    """Saetze der Grammatik, die in keiner Uebersicht vorkommen - fuers Protokoll."""
    bekannt = {x for eintraege in befehls_themen().values() for _, saetze in eintraege
               for x in saetze}
    bekannt |= set(UEBERSICHT_SAETZE) | set(UEBERSICHT_THEMEN_SAETZE) | {ALLE_BEFEHLE_SATZ}
    bekannt |= set(WUNSCH_SAETZE) | set(HILFE_SAETZE)
    return [x for x in BEFEHLSSAETZE if x not in bekannt]


def befehle_vorbereiten():
    """Legt alle Uebersichts-Ansagen als Audiodatei in den Speicher von dialos-say.py.

    Im Hintergrund und erst nach einer Minute: Beim Anmelden laufen Begruessung
    und Wetter, die sollen nicht auf Piper warten. Schon Gespeichertes wird
    uebersprungen - nach einem Stimmwechsel entstehen die Dateien neu.
    """
    time.sleep(60)
    try:
        # Niedrige Prioritaet nur fuer diesen Faden und seine Piper-Aufrufe
        # (unter Linux gilt setpriority je Thread-ID und vererbt sich): Alle
        # Ansagen zu erzeugen kostete am 2026-09-16 rund 50 s Rechenzeit auf
        # allen Kernen - ein Befehl in dieser Zeit soll davon nichts merken.
        os.setpriority(os.PRIO_PROCESS, threading.get_native_id(), 15)
    except (OSError, AttributeError):
        pass
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dialos_say", SAY)
        say = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(say)
        texte = alle_befehle_texte() + [thema_text(t) for t in THEMEN_REIHENFOLGE]
        neu = 0
        for text in texte:
            fertig = say.fuer_sprachausgabe(text)
            pfad = os.path.join(say.SPEICHER, say.speicher_schluessel(fertig) + ".wav")
            if not os.path.exists(pfad):
                say.speicher_fuellen(fertig, warten=True)
                neu += 1
        melde(f"Befehlsuebersicht vorbereitet ({len(texte)} Ansagen, {neu} neu erzeugt)")
    except Exception as fehler:
        melde(f"Befehlsuebersicht nicht vorbereitet: {fehler}")


# Thema (fuers Protokoll), ehrliche Antwort. Kein Versprechen, wann.
WUNSCH_SAETZE = {
    "nachrichten vorlesen": ("nachrichten", "Nachrichten kann ich noch nicht vorlesen."),
    "was gibt es neues": ("nachrichten", "Nachrichten kann ich noch nicht vorlesen."),
    "radio einschalten": ("radio", "Radio und Musik kann ich noch nicht abspielen."),
    "musik abspielen": ("radio", "Radio und Musik kann ich noch nicht abspielen."),
    "jemanden anrufen": ("telefon", "Telefonieren kann ich noch nicht."),
    "mails vorlesen": ("mails", "E-Mails kann ich noch nicht vorlesen."),
    "termine vorlesen": ("termine", "Termine kann ich noch nicht vorlesen."),
    "was steht heute an": ("termine", "Termine kann ich noch nicht vorlesen."),
}

NOTIZ_SKRIPT = "/usr/local/bin/dialos-notiz.py"
HILFE_SKRIPT = "/usr/local/bin/dialos-hilfe.py"
NOTIZ_SAETZE = {
    "einkaufszettel vorlesen": ("einkaufszettel", "vorlesen"),
    "notizen vorlesen": ("notizen", "vorlesen"),
    "brief vorlesen": ("brief", "vorlesen"),
    "brief als pdf speichern": ("brief", "pdf"),
    "einkauf erledigt": ("einkaufszettel", "loeschen"),
    "einkaufszettel wegwerfen": ("einkaufszettel", "loeschen"),
    "einkaufszettel löschen": ("einkaufszettel", "loeschen"),
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

# GESPRAECHS-ERKENNUNG (Stephans Freigabe vom 2026-09-14, Massnahme A).
#
# Anlass: Ein Gespraech im Raum und spaeter ein Fernsehfilm haben die
# Sprachsteuerung bedient - Diktate, Druckauftraege, ein Bildschirmfoto. Die
# Grammatik presst jeden Ton in Befehlswoerter, und weil jeder Wortfetzen als
# Aktivitaet galt, blieb die Steuerung minutenlang an. Stephan: "wenn z.B.
# parallel ein Film im TV laeuft, dann will die Sprachsteuerung staendig
# etwas machen".
#
# Die Regel: GESPRAECH_GRENZE Aeusserungen ohne Befehl innerhalb von
# GESPRAECH_FENSTER_S -> ausschalten, mit Ansage. Durchgespielt an ALLEN
# Sitzungen der Protokolle bis zum 2026-09-14 mittags:
#
#     Stephans echte Sitzungen (12)    hoechstens 2-4 in 30 s  -> alle bleiben an
#     Gespraech und Fernseher (7)      6-13 in 30 s            -> alle nach 14-23 s aus,
#                                                                 BEVOR ein Fehlbefehl durchkam
#
# Mit 4 waere eine echte Sitzung beendet worden, 5 und 6 wirken gleich.
# Die beiden Briefe aus Gespraech und Film (11:15 und 12:24) waeren nicht
# entstanden.
GESPRAECH_GRENZE = 5
GESPRAECH_FENSTER_S = 30.0
ANSAGE_GESPRAECH = ("Hier wird gerade viel gesprochen. Ich höre Dir nicht mehr zu. "
                    "Wenn Du mich brauchst, sage: Sprachsteuerung starten.")

# PEGELVERLAUF BEIM EINSCHALTSATZ - vorerst NUR GEMESSEN (Massnahme B).
# Ob "Sprachsteuerung starten" von Stille eingerahmt war, laesst sich an
# diesem Verlauf ablesen; eine Schwelle wird erst festgelegt, wenn echte
# Zahlen mit und ohne Fernseher vorliegen. 32 Bloecke = 4 Sekunden.
PEGEL_VERLAUF_BLOECKE = 32

# EINSCHALTEN NUR MIT STILLE DANACH (Massnahme B, Stephans Freigabe vom
# 2026-09-14: "Ja, bau B so ein").
#
# Gemessen am 2026-09-14 mit dem Pegelverlauf oben, Werte in Tausend je 1/8 s,
# die letzten Bloecke liegen NACH dem Satz:
#
#     Stephan, 4 x "Sprachsteuerung starten"   letzte 6: 0 0 0 0 0 0 (jedes Mal)
#     Film, hat eingeschaltet (12:47:52)       letzte 6: 27 27 19 1 11 25
#     Film, nur "sprachsteuerung"              letzte 6: 0 0 12 18 27 27 / 15 8 8 15 10 15
#
# "Stille DAVOR" trennt NICHT - der Film hatte vor seinem Satz selbst eine
# ruhige Stelle (1-3). "Stille DANACH" trennt: Wer die Sprachsteuerung wirklich
# einschaltet, schweigt und wartet auf "Ich hoere Dir zu". Ein Film redet weiter.
#
# DER PREIS, und Stephan hat ihn bewusst angenommen: Laeuft der Fernseher laut,
# laesst sich die Sprachsteuerung auch vom Nutzer nicht einschalten. Deshalb
# eine Ansage statt Stille - ein Satz, der nicht wirkt, ohne dass jemand es
# sagt, waere derselbe lautlose Fehlschlag, den DialOS am 2026-08-24
# abgeschafft hat. Hoechstens einmal pro Minute, damit ein Film sie nicht in
# Dauerschleife ausloest.
#
# Datenlage duenn (5 echte Saetze, 1 vollstaendiger aus dem Film). Die
# Messzeile bleibt im Protokoll, damit die Schwelle nachgeprueft werden kann.
STILLE_DANACH_BLOECKE = 4          # eine halbe Sekunde
STILLE_DANACH_GRENZE = 3000
ANSAGE_ZU_LAUT = ("Ich habe Sprachsteuerung starten gehört, aber es ist zu laut. "
                  "Bitte stelle den Ton leiser und sage es noch einmal.")
# EIN AUSSCHLAG IST ERLAUBT, UND DIE ANSAGE KOMMT ALLE 15 S (beides noch am
# 2026-09-14, nach Stephans erstem Alltagsversuch). Um 13:09:26 hat Stephan bei
# laufendem, aber gerade leisem Fernseher "Sprachsteuerung starten" gesagt -
# davor und danach Pegel 1, nach dem Satz EIN Block mit 3149. Verworfen, und
# weil die Ansage da noch fuer 60 s gesperrt war, OHNE ein Wort. Genau der
# lautlose Fehlschlag, den die Ansage verhindern sollte. Durchgespielt an allen
# 13 Einschaltsaetzen des Tages: Die neue Fassung aendert nur diesen einen Fall;
# jeder Film-Verlauf hat mindestens zwei laute Bloecke danach.
ZU_LAUT_ABSTAND_S = 15.0
# DIE ANSAGE ERST BEIM ZWEITEN MAL (Stephan, 2026-09-15: "die Sprachsteuerung
# meldet sich immer mit dem Hinweis ... zu laut" - "und niemand hat
# Sprachsteuerung gesagt!"). An dem Tag achtmal: Jedes Mal hatte ein Geraeusch
# den ganzen Einschaltsatz ergeben, und die Stille-Pruefung hat richtig NICHT
# eingeschaltet - erst die Ansage machte aus dem abgewehrten Fehlalarm eine
# Stoerung. Jetzt wird das erste Mal still verworfen. Wer wirklich einschalten
# will und keine Antwort bekommt, sagt es noch einmal; zwei ganze Einschaltsaetze
# aus Geraeusch binnen 20 s sind selten. Nachgerechnet an den zehn Ablehnungen
# vom 2026-09-15 (acht davon mit Ansage): Sie waere zweimal gekommen - bei drei
# Einschaltsaetzen binnen 37 s (10:51:31, 10:51:49, 10:52:08).
ZU_LAUT_WIEDERHOLUNG_S = 20.0
STILLE_DANACH_AUSSCHLAEGE = 1


def still_danach(verlauf):
    """War es nach dem Einschaltsatz eine halbe Sekunde lang still?

    Hoechstens STILLE_DANACH_AUSSCHLAEGE laute Bloecke - ein Atemzug oder ein
    Klicken soll das Einschalten nicht verhindern.
    """
    letzte = list(verlauf)[-STILLE_DANACH_BLOECKE:]
    if len(letzte) < STILLE_DANACH_BLOECKE:
        return True             # zu wenig Daten - nicht blockieren
    laut = sum(1 for x in letzte if x >= STILLE_DANACH_GRENZE)
    return laut <= STILLE_DANACH_AUSSCHLAEGE
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
# Markierungsdatei) - seit 2026-09-16 ohne Pause danach, siehe VORLAUF_MARKE_S.
# DIE AUFNAHME BLEIBT WAEHREND DER ANSAGE OFFEN (2026-09-16).
#
# Stephan am 2026-09-15: "Zwischen der Ansage von Anna und meiner Antwort muss ich
# immer so 1,5 Sekunden warten. Sonst wird das erste Wort verschluckt!" Die
# Befehls-Messsitzung am selben Tag bestaetigte es: Fast alle Verpasser waren
# abgeschnittene Anfaenge ("tag haben wir", "datum haben wir"), und im Durchgang,
# in dem Stephan bewusst wartete, fehlte keiner.
#
# Die Zeit steckte hier: Nach jeder Ansage eines anderen Programms (Uhrzeit, Datum,
# Vorlesen) wurde parec beendet, NACHHALL_WARTEN_S (0,7 s) gewartet, parec neu
# gestartet (0,3 s Wartezeit in aufnahme_starten, dazu pegel_richten) - plus bis zu
# 0,3 s Abfragetakt. Nach den EIGENEN Ansagen ("Ich hoere Dir zu", Bildschirmfoto,
# Umschalten) passierte dagegen gar nichts: Der Ton, der waehrend der Ansage in
# der Leitung aufgelaufen war, wurde ausgewertet - daher am 15.09. "speichern"
# direkt nach "Das Bildschirmfoto ist gespeichert".
#
# Jetzt, wie beim Diktat seit dem 14.09.: parec laeuft durch. Solange jemand
# spricht (Markierung) oder ein Diktat laeuft, wird gelesen und verworfen. Hat der
# Dienst selbst laenger nicht gelesen (eigene Ansage, Umschalt-Skript), wird der
# Rueckstand weggelesen, bis wieder frischer Ton kommt. Danach sofort ein neuer
# Erkenner - ohne Pause.
#
# QUELLEN OHNE ECHO-UNTERDRUECKUNG: Am TONOR (roh) kam am 15.09. Annas Stimme als
# "speichern", "loeschen", "notiz" an. Dort wird nur VORLAUF_MARKE_ROH_S der Stille
# mitgenommen - der Anfang dieser Stille kann noch Nachhall enthalten.
WARTEN_BEIM_SPRECHEN_S = 0.3   # nur noch, wenn gar keine Aufnahme laeuft
STAU_S = 0.5                   # so lange nicht gelesen = Rueckstand wegwerfen
# DIE MARKIERUNG ENDET SPAETER ALS DER TON (gemessen 2026-09-16 am Ausgang des
# Lautsprechers): 0,64 / 0,66 s bei frisch gesprochener, 0,70 s bei gespeicherter
# Ansage. Das ist die halbe Sekunde Satzpause (--sentence_silence 0.5, seit
# 14.09.), die Piper auch hinter den LETZTEN Satz haengt, plus Abspielende. Wer
# in dieser Stille antwortet, verlor das erste Wort - bei Stephans erster Probe
# des neuen Stands "datum haben wir". Deshalb werden die letzten VORLAUF_MARKE_S
# vor dem Ende der Markierung mitgenommen: Sie liegen in dieser Stille, von der
# Ansage ist darin nichts. Dasselbe gilt nach eigenen Ansagen fuer das Ende des
# Rueckstands - sprich() kehrt erst mit dem Ende der Markierung zurueck.
VORLAUF_MARKE_S = 0.625
VORLAUF_MARKE_ROH_S = 0.5

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
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-sprachbefehl.log")


# WARUM IN EINEM VERSTECKTEN ORDNER (Stephan, 2026-08-22): Vorher lagen die
# Protokolle offen im Heimatverzeichnis - zehn laufende und fuenfzehn gedrehte
# Fassungen, also 25 Dateien zwischen "Notizen", "Dokumente" und "Bilder". Der
# Nutzer sieht sie nicht, aber ein sehender Helfer sucht dazwischen. In "~/.log"
# stoeren sie niemanden und sind trotzdem da, wo man sie vermutet.
#
# Der Ordner wird beim Schreiben angelegt, nicht vorausgesetzt: Ein neues Konto
# hat ihn noch nicht, und ein fehlendes Protokoll darf keine Ansage aufhalten.
def melde(text):
    """Meldung MIT Zeitstempel - immer ins Protokoll, mit --debug auch auf den
    Bildschirm.

    Der Zeitstempel ist nicht Zierde (Fehler vom 2026-08-18): Beim Test der
    Diktat-Sperre stand im Protokoll ein erkannter Satz, und ohne Uhrzeit
    liess sich nicht feststellen, ob er WAEHREND des Diktats kam - also ob
    die Sperre versagt hat - oder davor. Ein Protokoll ohne Zeit kann
    Gleichzeitigkeit nicht belegen, und genau darum ging es.
    """
    # MIT DATUM, seit dem 2026-08-24 - und das ist keine Kosmetik.
    # Vorher stand hier nur die Uhrzeit. logrotate dreht taeglich, aber
    # nur, wenn das Geraet laeuft; steht es zwei Tage, liegen drei Tage
    # in EINER Datei - und niemand sieht es, weil die Uhrzeit einfach
    # zurueckspringt. Genau daran bin ich am 2026-08-24 gescheitert: Ich
    # habe drei Tage zu einem Verlauf verlesen und Stephan einen Vorfall
    # geschildert, den es nie gab. Aufgefallen ist es nur, weil er sagte,
    # er habe an dem Tag gar nicht mit dem Geraet gesprochen.
    zeile = f"{time.strftime('%m-%d %H:%M:%S')}  {text}"
    if DEBUG:
        print("\n" + zeile, flush=True)
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
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


ZUSATZWORTE_MAX = 2


def enthaltener_befehl(worte):
    """Steckt genau EIN Befehl als zusammenhaengende Wortfolge in der Aeusserung?

    ANLASS (2026-08-24). Die Zuordnung war ein exakter Vergleich
    ("if satz in DRUCK_SAETZE"). Ein einziges Wort zu viel, und der
    vollstaendige Befehl fiel durch. Gemessen an 283 aufgezeichneten
    Aeusserungen, die Stephan alle als Befehlsversuche bestaetigt hat
    ("das waren alles Befehsversuche"), enthielten 21 den kompletten Befehl
    und loesten trotzdem nichts aus:

        'auf windows umschalten windows'  ->  auf windows umschalten
        'notiz notiz drucken'             ->  notiz drucken
        'wir notiz aufnehmen'             ->  notiz aufnehmen

    WARUM DIE GRENZE VON ZWEI ZUSATZWOERTERN, und warum sie nicht verhandelbar
    ist: Ohne Grenze haette dieselbe Regel viermal Wortsalat ausgefuehrt, und
    zwar den heikelsten Befehl. Dieser Fall stand im Protokoll:

        'es wir auf machen welchen tag haben tag haben wir einkauf erledigt
         bildschirmfoto es drucken notiz uhr notiz datum gnome es uhr wir ...'
             ->  einkauf erledigt      (der Einkaufszettel waere weg)

    Gemessen ueber dieselben 283 Aeusserungen:

        erlaubte Zusatzwoerter    gerettet    davon Wortsalat
                 0                    0             0
                 1                    8             0
                 2                   10             0
                 3                   13             0
                 5                   16             0
              ohne Grenze            21             4     <- kippt

    Zwei ist bewusst kein Optimum, sondern der konservative Rand: Bei 5 waere
    in DIESER Aufzeichnung ebenfalls kein Salat dabei gewesen, aber die
    Aufzeichnung ist keine Garantie. Wer die Zahl erhoehen will, messe erst
    neu - der teure Fehler ist hier nicht der nicht erkannte Befehl, sondern
    der falsch erkannte.

    DREI BEDINGUNGEN, alle noetig:
      - zusammenhaengend, nicht bloss "alle Woerter kommen vor". Sonst wuerde
        'wie viel wir viel wegwerfen' als 'einkaufszettel wegwerfen' gelten.
      - GENAU EIN Treffer. Bei zweien ist unklar, was gemeint war, und Raten
        waere hier schlimmer als Nichtstun. Genau einmal kam das vor.
      - kein "[unk]" - dasselbe Argument wie bei ist_phrase(): "[unk]" heisst,
        dass noch etwas anderes gesprochen wurde.

    Nicht angewandt auf das Ein- und Ausschalten. Diese beiden Saetze haben
    ihre eigene, enger gefasste Pruefung (ist_phrase), die mehrfach nachjustiert
    wurde und die Fehlstarts von 30 auf 7 gedrueckt hat. Eine Lockerung dort
    waere genau der Rueckschritt, der schon einmal ein selbsttaetiges
    Einschalten erzeugt hat.
    """
    if "[unk]" in worte:
        return None
    treffer = []
    for satz in BEFEHLSSAETZE:
        sw = satz.split()
        if len(worte) - len(sw) > ZUSATZWORTE_MAX:
            continue
        for i in range(len(worte) - len(sw) + 1):
            if worte[i:i + len(sw)] == sw:
                treffer.append(satz)
                break
    return treffer[0] if len(treffer) == 1 else None


# --- ANSAGE, WENN NICHTS GEPASST HAT (Stephans Freigabe vom 2026-08-24) ---
#
# WARUM ES DIE ANSAGE GIBT. Bis heute passierte bei einer Aeusserung, die kein
# Befehl ist, NICHTS - und es wurde auch nichts gesagt. Fuer einen blinden
# Nutzer ist das der schlechteste Ausgang: Er hat gesprochen, das Geraet hat
# zugehoert, und nichts sagt ihm, dass nichts geschah. Er weiss nicht einmal,
# ob er falsch gesprochen hat oder ob das Geraet kaputt ist.
#
# Ich hatte dagegen argumentiert, eine Ansage wuerde noergeln. Stephan hat die
# 283 aufgezeichneten Faelle durchgesehen und das widerlegt: "Daran kann ich
# mich erinnern, das waren alles Befehsversuche." Alle 283. Die Ansage waere
# also in 283 von 283 Faellen richtig gewesen.
#
# Und sein zweiter Satz ist der Grund fuer die FORM der Ansage: "Ich muss
# selbst die genauen Befehle erst lernen und dann wundere ich mich, dass ein
# anderer nicht funktioniert. Auch fuer mich eine Lernphase." Die Ansage soll
# also nicht bloss melden, dass etwas schiefging - sie soll den richtigen Satz
# nennen.
#
# KEINE FRAGEFORM, und das ist wichtig. "Meintest du: welchen Tag haben wir?"
# laedt zu einem "ja" ein, und dieses "ja" wuerde DialOS nicht verarbeiten -
# damit waere ein neuer lautloser Fehlschlag gebaut, um einen alten zu heilen.
# Der Vorschlag kommt deshalb als Aussage: "Der Befehl heisst ..."
HINWEIS_ABSTAND_S = 10.0
HINWEIS_ANTEIL = 2.0 / 3.0

# ZERSTOERENDE BEFEHLE WERDEN NIE VORGESCHLAGEN. Ein Vorschlag ist eine
# Empfehlung, und fuer "Einkaufszettel wegwerfen" darf das Geraet nichts
# empfehlen - schon gar nicht jemandem, der die Befehle noch lernt und der die
# Folge nicht auf dem Schirm nachlesen kann.
NICHT_VORSCHLAGEN = ("einkauf erledigt", "einkaufszettel wegwerfen",
                     "einkaufszettel löschen")


def naechster_befehl(worte):
    """Bester Befehl und der Anteil SEINER Woerter, die vorkommen.

    Anteil an den Woertern des BEFEHLS, nicht an den gehoerten: Sonst waere
    ein einzelnes Wort aus einem langen Befehl schon ein Volltreffer.
    """
    gehoert = set(worte)
    beste, wert = None, 0.0
    for satz in BEFEHLSSAETZE:
        sw = set(satz.split())
        anteil = len(gehoert & sw) / len(sw)
        if anteil > wert:
            wert, beste = anteil, satz
    return beste, wert


def teil_von_genau_einem_befehl(worte):
    """Der Befehl, in dem die Woerter (mind. zwei) zusammenhaengend stehen - wenn es genau einer ist."""
    if len(worte) < 2:
        return None
    gehoert = " " + " ".join(worte) + " "
    treffer = [b for b in BEFEHLSSAETZE if gehoert in " " + b + " "]
    return treffer[0] if len(treffer) == 1 else None


def hinweis_text(worte):
    """Was gesagt wird - immer das Gehoerte, den Befehl nur bei starker Naehe.

    DIE SCHWELLE IST GEMESSEN, nicht gewaehlt: Bei 51 Prozent der 283
    aufgezeichneten Versuche stimmte nur die HAELFTE der Woerter. Ein Vorschlag
    aus so wenig Uebereinstimmung laege oft daneben - und ein falscher
    Vorschlag ist fuer einen blinden Nutzer nicht neutral, er LEHRT einen
    Befehl, den es nicht gibt. Ab zwei Dritteln sind es 34 Prozent der Faelle;
    darunter wird nur das Gehoerte genannt.
    """
    gehoert = " ".join(worte)
    befehl, anteil = naechster_befehl(worte)
    # EIN EINDEUTIGES STUECK EINES BEFEHLS (2026-09-17): Stephan sagte "pdf
    # speichern" und bekam "Das kann ich noch nicht" - zwei von vier Woertern
    # liegen unter der Zwei-Drittel-Schwelle. Stehen aber alle gehoerten Woerter
    # zusammenhaengend in GENAU einem Befehl, ist klar, welcher gemeint war.
    teil = teil_von_genau_einem_befehl(worte)
    if teil:
        befehl, anteil = teil, 1.0
    if befehl and anteil >= HINWEIS_ANTEIL and befehl not in NICHT_VORSCHLAGEN:
        return (f"Ich habe verstanden: {gehoert}. "
                f"Der Befehl heisst: {befehl}.")
    # KLARE STANDARD-ANTWORT (Stephan, 2026-09-16). Vorher: "Ich habe verstanden:
    # brief als wir. Das war kein Befehl." - so kam "Wie ist das Wetter?" an, als es
    # den Befehl nicht gab. Der Wortsalat half niemandem; wohin man sich wendet,
    # schon.
    return "Das kann ich noch nicht. Sage: Was kann ich sagen."


def hinweis_faellig(worte, letzter):
    """Lohnt sich eine Ansage - und ist die Bremse abgelaufen?

    DREI BEDINGUNGEN:
      - mindestens zwei Woerter. Einwort-Bruchstuecke ("wir", "es", "auf")
        sind keine Befehlsversuche; genau diese hat Stephan in der Stichprobe
        auch nicht zu beurteilen bekommen.
      - kein "[unk]". Dann war noch etwas anderes im Raum, und das Geraet
        wuerde in ein Gespraech hineinreden.
      - Abstand zur letzten Ansage. DIE BREMSE IST GEMESSEN: Von 277
        aufeinanderfolgenden Anlaessen lagen 48 Prozent unter 5 Sekunden und
        68 Prozent unter 10, Median 6 Sekunden. Ohne Bremse redete das Geraet
        waehrend einer misslingenden Sitzung fast durchgehend - und jede Ansage
        dauert selbst zwei bis drei Sekunden, sie wuerden sich also stauen.
        Zehn Sekunden lassen etwa jeden dritten Anlass durch: genug, um den
        richtigen Satz zu lernen, wenig genug, um nicht zu noergeln.
    """
    if len(worte) < 2 or "[unk]" in worte:
        return False
    return letzter is None or (time.time() - letzter) >= HINWEIS_ABSTAND_S


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
    """Haelt gerade jemand anders das Mikrofon? Mit Wache gegen verwaiste Marken.

    Die Marke bedeutet "jemand anders hoert zu" - das Diktat, eine Rueckfrage
    in dialos-notiz.py oder eine Erweiterung. Solange sie da ist, verwirft
    dieser Dienst alles Gehoerte.

    DIE WACHE, ergaenzt am 2026-09-17: Steht eine PID in der Datei, wird
    geprueft, ob der Prozess noch lebt. Lebt er nicht, ist die Marke verwaist
    und wird weggeraeumt. Ohne das bliebe das Mikrofon nach einem harten
    Abbruch (SIGKILL, Stromausfall waehrend der Sitzung) FUER IMMER belegt -
    der Nutzer spraeche gegen ein taubes Geraet, und nicht einmal
    "Sprachsteuerung stoppen" kaeme noch durch. Fuer einen blinden Nutzer gibt
    es aus diesem Zustand keinen Weg zurueck.

    RUECKWAERTSKOMPATIBEL, und das ist Absicht: dialos-diktat.py und
    dialos-notiz.py legen die Datei LEER an. Ohne PID verhaelt sich die Pruefung
    wie bisher - vorhanden heisst belegt. Nur wer eine PID hineinschreibt,
    bekommt die Wache dazu. Damit ist hier nichts kaputtzumachen, was heute
    laeuft; die beiden koennen spaeter nachziehen.
    """
    if not os.path.exists(DIKTAT_MARKE):
        return False
    try:
        with open(DIKTAT_MARKE, encoding="utf-8") as f:
            pid = int(f.readline().split()[0])
    except (OSError, ValueError, IndexError):
        return True                      # keine PID - alte Form, wie bisher
    try:
        os.kill(pid, 0)                  # Signal 0 prueft nur, ob es ihn gibt
    except ProcessLookupError:
        melde(f"  verwaiste Mikrofon-Marke von PID {pid} - weggeraeumt")
        try:
            os.unlink(DIKTAT_MARKE)
        except OSError:
            pass
        return False
    except PermissionError:
        return True                      # fremdes Konto, aber er lebt
    return True


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
                  # EIN DRITTEL KLEINER (Stephan, 2026-08-22). Vorher
                  # 100x30, gemessen rund 1170 x 738 px auf 1920 x 1080 -
                  # das Fenster nahm die halbe Breite ein.
                  #
                  # WARUM NUR DIE GROESSE UND NICHT DIE POSITION: Stephan
                  # wollte es unten rechts. Auf Wayland kann ein Fenster
                  # seine Position NICHT selbst bestimmen - gemessen am
                  # 2026-08-22: "--geometry=53x20+1440+720" landete mittig,
                  # der Versatz wurde ignoriert. Nur X11-Clients ueber
                  # XWayland duerfen das (mit xterm nachgewiesen: es landete
                  # wirklich bei +1440+790). Stephans Entscheidung: lieber
                  # die GNOME-Optik behalten und auf die Position verzichten.
                  "--geometry=67x20", "--",
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


# MIKROFON ZUM VERGLEICH (2026-09-15, Pruefstand). Nennt diese Datei eine
# vorhandene Quelle, hoert der Befehlsdienst dort - fuer den Vergleich mit dem
# USB-Tischmikrofon TONOR TC30, das beim Diktat mit laufendem Fernseher 4,2 %
# statt 9,9 % Wortfehler hatte. OHNE Echo-Unterdrueckung: Anna waere zu hoeren,
# aber waehrend sie spricht, hoert der Dienst ohnehin nicht zu und beginnt die
# Aufnahme danach neu (siehe aufnahme_verwerfen). Wirkt nach dem Neustart des
# Dienstes (Ab- und Anmelden).
MIKROFON_WAHL = os.path.join(os.path.expanduser("~"), ".config", "dialos", "befehl-mikrofon")

# MITSCHNITT FUER DEN PRUEFSTAND (Stephan, 2026-09-15: "Ja, bereite das so vor").
# NUR MIT SCHALTER, und dann wird JEDE Aeusserung gespeichert, die mehr als
# "[unk]" ergab - auch Gespraech und Fernseher, genau darum geht es beim Messen.
# Deshalb: Schalter nur fuer eine Messsitzung setzen und danach entfernen. Nur
# auf die externe Platte, nie ins Repo. Gespeichert wird das Stueck Ton, aus dem
# der Erkenner das Ergebnis gebaut hat (seit dem vorigen Ergebnis, hoechstens
# MITSCHNITT_HOECHSTENS_S), dazu Zustand, Pegelverlauf und Mikrofon.
MITSCHNITT_SCHALTER = os.path.join(os.path.expanduser("~"), ".config", "dialos", "pruefstand-befehle")
MITSCHNITT_ORDNER = "/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich/pruefstand/befehle"
MITSCHNITT_HOECHSTENS_S = 20.0


def mitschnitt_an():
    return (os.path.exists(MITSCHNITT_SCHALTER)
            and os.path.isdir(os.path.dirname(os.path.dirname(MITSCHNITT_ORDNER))))


def mitschnitt_speichern(ton, text, hoert_zu, verlauf, quelle):
    try:
        import wave
        os.makedirs(MITSCHNITT_ORDNER, exist_ok=True)
        stamm = os.path.join(MITSCHNITT_ORDNER, time.strftime("%Y-%m-%d-%H%M%S")
                             + ("-an" if hoert_zu else "-aus"))
        with wave.open(stamm + ".wav", "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(ABTASTRATE)
            w.writeframes(bytes(ton))
        with open(stamm + ".json", "w", encoding="utf-8") as f:
            json.dump({"erkannt": text, "hoert_zu": hoert_zu, "quelle": quelle,
                       "pegel_verlauf": list(verlauf), "gesagt": None}, f,
                      ensure_ascii=False, indent=1)
    except Exception as fehler:
        melde(f"  Mitschnitt nicht gespeichert: {fehler}")


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
    try:
        with open(MIKROFON_WAHL, encoding="utf-8") as f:
            gewuenscht = f.read().strip()
        if gewuenscht in namen:
            return gewuenscht
    except OSError:
        pass
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


def programm_starten(satz):
    """Ein Programm oeffnen - die Ansage macht dialos-programm.py selbst.

    IM EIGENEN PROZESS, nicht hier im Dienst: Ein Programm, das an dieser
    Prozessgruppe haengt, geht mit, wenn die Sprachsteuerung neu startet. Beim
    Bildschirmfoto war genau das der Fehler, der drei Wochen unbemerkt blieb.
    """
    try:
        subprocess.Popen([PROGRAMM_WERKZEUG, satz], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        print(f"Programm {satz!r} nicht startbar: {fehler}", file=sys.stderr)


def erweiterung_starten(manifest):
    """Eine Erweiterung starten und ihr das Mikrofon ueberlassen.

    NICHT BLOCKIEREND (Popen, eigene Sitzung) - wie beim Diktat. Der Dienst
    muss weiterlaufen, sonst koennte der Nutzer die Sprachsteuerung nicht mehr
    ausschalten.

    DIE MARKE SETZT DIE ERWEITERUNG SELBST, und zwar bevor sie etwas Langsames
    tut. Hier waere sie zu frueh: Zwischen Popen und dem ersten Befehl der
    Erweiterung lagen sonst Millisekunden, in denen niemand das Mikrofon haelt -
    und der Dienst wuerde die erste Silbe des Nutzers noch als Befehl werten.
    """
    befehl = manifest.get("befehl")
    if not befehl or not os.access(befehl, os.X_OK):
        melde(f"  Erweiterung {manifest.get('name')!r}: {befehl!r} fehlt "
              "oder ist nicht ausfuehrbar")
        sprich("Das Programm dazu fehlt.")
        return
    try:
        subprocess.Popen([befehl], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        melde(f"  Erweiterung gestartet: {manifest.get('name')}")
    except OSError as fehler:
        melde(f"  Erweiterung liess sich nicht starten: {fehler}")
        sprich("Das hat nicht geklappt.")


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
    if not os.access(DIKTAT_SKRIPT, os.X_OK) or not os.access(NOTIZ_SKRIPT, os.X_OK):
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
        # MIT RUECKFRAGE (seit 2026-09-14): gestartet wird dialos-notiz.py,
        # das "Soll ich ...? Sage ja oder nein." fragt und erst bei einem
        # klaren "ja" das Diktat startet. Anlass: Ein Gespraech im Raum hat
        # "diktat brief schreiben" ergeben und 97 Sekunden als Brief
        # geschrieben, archiviert und gedruckt. Begruendung in dialos-notiz.py.
        subprocess.Popen([NOTIZ_SKRIPT, notiz, "diktat"],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        melde(f"Rueckfrage vor Diktat gestartet fuer Notiz {notiz!r}")
    except Exception as fehler:
        melde(f"Diktat liess sich nicht starten: {fehler}")
        sprich("Ich kann das Diktat nicht starten.")


# Wie lange das Fenster braucht, um wirklich vom Bildschirm zu verschwinden.
# Ohne diese Pause steht es noch auf dem Foto - der Fenstermanager raeumt es
# nicht in dem Augenblick weg, in dem der Prozess endet.
FOTO_NACHLAUF_S = 0.8


def drucken(was):
    """Startet den Druck und wartet NICHT darauf.

    Wie bei der Auskunft: Der Dienst muss seine Schleife weiterlaufen lassen.
    Der Druckauftrag ist in Millisekunden abgegeben, aber die Ansage danach
    dauert - und der Drucker braucht ohnehin laenger als jede Schleife.
    """
    if not os.access(DRUCK_SKRIPT, os.X_OK) or not os.access(NOTIZ_SKRIPT, os.X_OK):
        sprich("Ich kann das Drucken nicht finden.")
        return
    try:
        # MIT RUECKFRAGE (seit 2026-09-14) - wie beim Diktat, siehe dort.
        # Am 2026-09-14 kamen aus einem Gespraech vier Druckauftraege.
        subprocess.Popen([NOTIZ_SKRIPT, was, "drucken"],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
        melde(f"Rueckfrage vor Druck {was!r} gestartet")
    except Exception as fehler:
        melde(f"Druck liess sich nicht starten: {fehler}")
        sprich("Ich kann das nicht ausführen.")


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
        p = subprocess.run([FOTO_SKRIPT], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=60)
        # Was WIRKLICH passiert ist (2026-09-14): Hier stand "Bildschirmfoto
        # erstellt" auch dann, wenn das Skript "kein Bild entstanden" meldete.
        # Die Ansage kommt vom Skript selbst; das Protokoll soll nicht
        # widersprechen.
        if p.returncode == 0:
            melde("Bildschirmfoto erstellt")
        else:
            melde(f"Bildschirmfoto misslungen (Rueckgabe {p.returncode}) - "
                  "Einzelheiten in dialos-bildschirmfoto.log")
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


class Leser:
    """Liest parec IMMER aus, auch waehrend der Dienst spricht (2026-09-16).

    Jeder Block kommt mit seiner Ankunftszeit in einen Vorrat. Waehrend einer
    eigenen Ansage steht die Hauptschleife in sprich() - vorher las dann niemand,
    der Puffer lief ueber, und was verloren ging, war nicht zu steuern: In der
    Nachbildung waren es genau die Wortanfaenge nach "Ich hoere Dir zu". Mit dem
    Leser bleibt alles da, und nach einer Ansage wird nach ZEIT verworfen
    (verwerfen_vor), nicht nach dem, was zufaellig im Puffer stand.
    """

    HOECHSTENS = int(20 / 0.125)        # 20 s Vorrat

    def __init__(self, prozess):
        self.prozess = prozess
        self.vorrat = collections.deque(maxlen=self.HOECHSTENS)
        self.bedingung = threading.Condition()
        self.ende = False
        threading.Thread(target=self._lesen, daemon=True).start()

    def _lesen(self):
        while True:
            try:
                block = self.prozess.stdout.read(4000)
            except Exception:
                block = b""
            with self.bedingung:
                if not block:
                    self.ende = True
                    self.bedingung.notify_all()
                    return
                self.vorrat.append((time.time(), block))
                self.bedingung.notify_all()

    def naechster(self, warten_s=1.0):
        """Naechster Block, oder None (Zeitgrenze oder Ende des Datenstroms)."""
        with self.bedingung:
            if not self.vorrat and not self.ende:
                self.bedingung.wait(warten_s)
            return self.vorrat.popleft()[1] if self.vorrat else None

    def verwerfen_vor(self, zeitpunkt):
        with self.bedingung:
            while self.vorrat and self.vorrat[0][0] < zeitpunkt:
                self.vorrat.popleft()


def aufnahme_starten(quelle):
    # "--latency-msec=30" (2026-09-14): ohne die Angabe kam jeder Befehl rund
    # zwei Sekunden spaeter an - parec puffert ab Werk so lange (gemessen
    # 2,03 s gegen 0,10 s). Nach jeder eigenen Ansage wird die Aufnahme neu
    # gestartet, und auch dieser Neustart brauchte jedes Mal zwei Sekunden.
    befehl = ["parec", f"--rate={ABTASTRATE}", "--channels=1", "--format=s16le",
              "--latency-msec=30"]
    if quelle:
        befehl.append(f"--device={quelle}")
    p = subprocess.Popen(befehl, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    # Erst nach dem Oeffnen des Datenstroms - vorher greift WirePlumber
    # noch einmal auf die Regler zu.
    time.sleep(0.3)
    pegel_richten()
    return p


# NUR EIN SPRACHDIENST JE KONTO (Fehler vom 2026-09-14).
#
# Nach Ab- und Anmelden liefen zwei: der von 11:49 hatte das Abmelden
# ueberlebt, der neue kam um 12:09 dazu. Beide hoerten zu - ein Befehl konnte
# doppelt ausgefuehrt werden, und der alte lief mit der Fassung von VOR dem
# Aufspielen weiter. Stephan: "Dann musst du beim Abmelden den Sprachbefehl
# auch resetten."
#
# Erledigt wird es beim START, nicht beim Abmelden: Auf das Abmelden ist kein
# Verlass - genau dort ist es schiefgegangen. Beim Start ist dagegen sicher,
# dass diese Instanz die richtige ist: die neueste, aus dem Autostart der
# aktuellen Sitzung.
#
# Gesucht wird in /proc und nicht ueber eine Sperrdatei: Eine Datei unter
# XDG_RUNTIME_DIR ueberlebt das Abmelden ebenso wie der alte Prozess, und ihr
# Inhalt beweist nichts. Nur Prozesse DESSELBEN Kontos werden beendet.
def alte_instanzen_beenden():
    eigene = os.getpid()
    uid = os.getuid()
    alte = []
    for eintrag in os.listdir("/proc"):
        if not eintrag.isdigit() or int(eintrag) == eigene:
            continue
        try:
            if os.stat(f"/proc/{eintrag}").st_uid != uid:
                continue
            with open(f"/proc/{eintrag}/cmdline", "rb") as f:
                teile = f.read().split(b"\0")
        except OSError:
            continue
        if any(t.endswith(b"dialos-sprachbefehl-desktop.py") for t in teile[:3]):
            alte.append(int(eintrag))
    for pid in alte:
        try:
            os.kill(pid, signal.SIGTERM)
            melde(f"aeltere Instanz beendet (PID {pid})")
        except (ProcessLookupError, PermissionError):
            pass
    if alte:
        ende = time.time() + 3.0
        while time.time() < ende and any(os.path.exists(f"/proc/{p}") for p in alte):
            time.sleep(0.1)
        for pid in alte:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass


def main():
    alte_instanzen_beenden()
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
    fehlend = befehle_ohne_uebersicht()
    if fehlend:
        melde(f"ACHTUNG: Befehle ohne Platz in der Uebersicht: {fehlend!r}")
    threading.Thread(target=befehle_vorbereiten, daemon=True).start()

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
    leser = Leser(prozess)
    letzte_aktivitaet = time.time()
    leer_zeiten = collections.deque()
    pegel_verlauf = collections.deque(maxlen=PEGEL_VERLAUF_BLOECKE)
    zu_laut_gesagt = 0.0
    zu_laut_verworfen = 0.0
    # Gleich gesetzt: Es kam noch kein Befehl. Bewegt sich
    # letzte_aktivitaet spaeter darueber hinaus, war einer dabei - daran
    # haengt, welche der beiden Fristen gilt.
    an_seit = letzte_aktivitaet
    aufnahme_verwerfen = False
    zuletzt_gelesen = time.time()
    nach_diktat = False
    saettigungen = 0
    letzte_pegelkorrektur = 0.0
    letzter_hinweis = None
    # PEGELSPITZE SEIT DEM LETZTEN ERGEBNIS (seit 2026-08-24). Gemessen am
    # selben Tag: Vosk baut aus etwas, das LEISER als Stille ist, ganze
    # Befehlswoerter - 'sprachsteuerung' bei Pegel 30 mit Konfidenz 1,000,
    # '[unk] [unk] starten' bei Pegel 28 mit 0,979. Der Leerlauf dieses
    # Raumes liegt bei 52, Sprache lag bei der Diktat-Messung zwischen 3475
    # und 4196.
    #
    # Die Konfidenz taugt hier NICHT als Filter: In einer Grammatik mit einem
    # einzigen Satz ist der Erkenner konstruktionsbedingt sicher, er hat ja
    # keine Alternative. Der Pegel trennt dagegen sauber - deshalb steht er
    # jetzt bei jeder Erkennung im Protokoll. Beim naechsten echten Fehlstart
    # steht damit im Protokoll, ob eine Pegelschwelle ihn verhindert haette.
    # Erst messen, dann bauen.
    #
    # ACHTUNG BEIM VERGLEICHEN: Hier steht der SPITZENWERT der Amplitude
    # (0 bis 32768), nicht der RMS. scripts/dialos-fehlstart-messen.py
    # rechnet RMS, dialos-diktat.py ebenfalls. Die Zahlen sind deshalb NICHT
    # untereinander vergleichbar - der Spitzenwert liegt bei Sprache um ein
    # Mehrfaches hoeher. Deshalb heisst es im Protokoll "Spitze" und nicht
    # "Pegel". Wer beide Zahlen gegenueberstellen will, muss dasselbe Mass
    # rechnen.
    pegel_spitze = 0
    # Ton seit dem letzten Ergebnis - nur fuer den Pruefstand-Mitschnitt.
    stueck = bytearray()
    stueck_erkenner = None

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
                # Nicht zuhoeren - der Leser sammelt weiter, danach wird nach Zeit
                # verworfen (siehe VORLAUF_MARKE_S).
                aufnahme_verwerfen = True
                if diktat_laeuft():
                    nach_diktat = True
                time.sleep(0.05)
                continue

            if diktat_gemeldet and not diktat_laeuft():
                melde("anderer Dienst fertig - ich hoere wieder zu")
                diktat_gemeldet = False

            # EIGENE ANSAGE ODER LANGE AKTION: Die Hauptschleife stand in sprich()
            # oder im Umschalt-Skript - sprich() kehrt erst mit dem Ende der
            # Markierung zurueck, also gilt dasselbe wie nach fremden Ansagen.
            if time.time() - zuletzt_gelesen > STAU_S:
                aufnahme_verwerfen = True

            if aufnahme_verwerfen:
                # Nach der Ansage: Was waehrend der Ansage ankam, wird verworfen
                # (seit 2026-08-17 der Grund fuer diesen Schritt: Der Dienst
                # schaltete damals auf Windows um und 15 s spaeter von selbst
                # zurueck). Seit 2026-09-16 ohne Neustart von parec - das kostete
                # mit dem Nachhall rund 1,5 s -, und die Stille zwischen letztem Ton
                # und Ende der Markierung bleibt, damit ein sofort gesprochenes
                # erstes Wort ankommt. Nach einem Diktat bleibt nichts.
                aufnahme_verwerfen = False
                vorlauf = (0.0 if nach_diktat else
                           VORLAUF_MARKE_S if quelle == ECHO_QUELLE else VORLAUF_MARKE_ROH_S)
                nach_diktat = False
                leser.verwerfen_vor(time.time() - vorlauf)
                erkenner = vosk.KaldiRecognizer(
                    modell, ABTASTRATE,
                    GRAMMATIK_AN if hoert_zu else GRAMMATIK_AUS)
                zuletzt_gelesen = time.time()
                # Immer protokollieren: Diese Zeile erklaert Luecken im
                # Protokoll. Ohne sie sieht eine Pause zwischen zwei
                # Befehlen aus wie ein Aussetzer.
                melde("(Ansage vorbei - hoere sofort weiter)")
                continue

            block = leser.naechster()
            zuletzt_gelesen = time.time()
            if block is None and not leser.ende:
                continue
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
                leser = Leser(prozess)
                erkenner = vosk.KaldiRecognizer(
                    modell, ABTASTRATE,
                    GRAMMATIK_AN if hoert_zu else GRAMMATIK_AUS)
                continue

            pegel = max(abs(int.from_bytes(block[i:i + 2], "little", signed=True))
                        for i in range(0, len(block) - 1, 2))
            pegel_spitze = max(pegel_spitze, pegel)
            pegel_verlauf.append(pegel)
            if stueck_erkenner is not erkenner:
                # Neuer Erkenner (Zustandswechsel, neue Aufnahme): sein
                # Ergebnis entsteht nur aus Ton ab jetzt.
                stueck = bytearray()
                stueck_erkenner = erkenner
            stueck.extend(block)
            if len(stueck) > MITSCHNITT_HOECHSTENS_S * 2 * ABTASTRATE:
                del stueck[:len(block)]
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
            if text and set(text.split()) != {"[unk]"} and mitschnitt_an():
                mitschnitt_speichern(stueck, text, hoert_zu, pegel_verlauf, quelle)
            stueck = bytearray()
            # KEIN "if DEBUG" davor (Fehler vom 2026-08-19). Das ist die
            # wichtigste Zeile des ganzen Protokolls - was der Dienst gehoert
            # hat. Beim Umbau auf "immer protokollieren" blieb der alte
            # Vorbehalt stehen, und heraus kam ein Protokoll, in dem die
            # AUSGEFUEHRTE Aktion stand, aber nicht der Satz, der sie
            # ausgeloest hat. Genau das Gegenteil dessen, was man beim
            # Fehlersuchen braucht.
            if text:
                melde(f"erkannt: {text!r}  (Spitze {pegel_spitze})")
                if "sprachsteuerung" in text.split():
                    # In Tausendern, je 1/8 s, der letzte Wert zuletzt. Vosk
                    # liefert erst nach einer kurzen Pause ab - das Ende des
                    # Verlaufs ist also schon die Zeit NACH dem Satz.
                    melde("  Pegelverlauf 4 s: " + " ".join(
                        str(round(x / 1000)) for x in pegel_verlauf))
            pegel_spitze = 0
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
            if (not hoert_zu
                    and ist_phrase(satz, STARTSATZ, ("sprachsteuerung", "starten"))
                    and not still_danach(pegel_verlauf)):
                # Massnahme B - Begruendung bei STILLE_DANACH_GRENZE.
                melde("  Einschaltsatz verworfen - danach nicht still "
                      f"(letzte {STILLE_DANACH_BLOECKE} Bloecke bis "
                      f"{max(list(pegel_verlauf)[-STILLE_DANACH_BLOECKE:])})")
                jetzt = time.time()
                if jetzt - zu_laut_verworfen > ZU_LAUT_WIEDERHOLUNG_S:
                    melde("  (erstes Mal - still verworfen, siehe ZU_LAUT_WIEDERHOLUNG_S)")
                elif jetzt - zu_laut_gesagt > ZU_LAUT_ABSTAND_S:
                    zu_laut_gesagt = jetzt
                    sprich(ANSAGE_ZU_LAUT)
                zu_laut_verworfen = jetzt
                continue

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
                    leer_zeiten.clear()
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

            # --- Vollstaendiger Befehl mit einem Wort zu viel ---
            # Erst hier, nach dem Ein- und Ausschalten: Deren Pruefung ist
            # enger gefasst und bleibt unberuehrt (Begruendung in
            # enthaltener_befehl()).
            if satz not in BEFEHLSSAETZE:
                genauer = enthaltener_befehl(worte)
                if genauer:
                    melde(f"  als {genauer!r} zugeordnet "
                          f"(+{len(worte) - len(genauer.split())} Wort zu viel)")
                    satz = genauer
                    worte = genauer.split()

            # --- Befehle: Erweiterungen ---
            # GANZ VORN, weil eine Erweiterung das Mikrofon uebernimmt: Sie
            # setzt die Marke selbst, und der Dienst haelt sich danach heraus
            # (dieselbe Marke wie beim Diktat, siehe diktat_laeuft()).
            if satz in ERWEITERUNG_SAETZE:
                erweiterung_starten(ERWEITERUNG_SAETZE[satz])
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            # --- Befehle: Programme oeffnen ---
            # NACH den Erweiterungen, VOR allem anderen: Ein Programm zu
            # starten nimmt das Mikrofon nicht - die Sprachsteuerung hoert
            # weiter zu, und der naechste Befehl kommt sofort durch.
            if satz in PROGRAMM_SAETZE:
                programm_starten(satz)
                letzte_aktivitaet = time.time()
                erkenner.Reset()
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

            # --- Befehle: Drucken ---
            if satz in DRUCK_SAETZE:
                drucken(DRUCK_SAETZE[satz])
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
            if satz in UEBERSICHT_SAETZE:
                melde("Uebersicht der Befehle angesagt")
                sprich(ANSAGE_UEBERSICHT)
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            if satz == ALLE_BEFEHLE_SATZ or satz in UEBERSICHT_THEMEN_SAETZE:
                if satz == ALLE_BEFEHLE_SATZ:
                    melde("Alle Befehle angesagt")
                    for text in alle_befehle_texte():
                        sprich(text)
                else:
                    melde(f"Befehle angesagt: {UEBERSICHT_THEMEN_SAETZE[satz]}")
                    sprich(thema_text(UEBERSICHT_THEMEN_SAETZE[satz]))
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

            if satz in WUNSCH_SAETZE:
                thema, antwort = WUNSCH_SAETZE[satz]
                melde(f"WUNSCH {thema}: {satz!r}")
                sprich(antwort)
                letzte_aktivitaet = time.time()
                erkenner.Reset()
                continue

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
            getroffen = False
            # DIESELBE GRENZE WIE BEI ALLEN ANDEREN BEFEHLEN (2026-09-16). Diese
            # Regel ist aelter als enthaltener_befehl() und nahm "umschalten" plus
            # ein Ziel IRGENDWO in der Aeusserung. In der Messsitzung vom 15.09.
            # schaltete so "welchen windows umschalten windows brief notizen wir es
            # welchen haben wir" (zwoelf Woerter) auf Windows um. Sie bleibt fuer
            # verkuerzte Saetze wie "windows umschalten" (am selben Tag echt
            # gesagt und so erkannt), aber nur ohne [unk] und mit hoechstens
            # ZUSATZWORTE_MAX Woertern mehr als "auf windows umschalten".
            if (AUSLOESER in worte and "[unk]" not in worte
                    and len(worte) <= len("auf windows umschalten".split()) + ZUSATZWORTE_MAX):
                for wort in worte:
                    ziel = ZIELE.get(wort)
                    if ziel:
                        umschalten(ziel)
                        letzte_aktivitaet = time.time()
                        erkenner.Reset()
                        getroffen = True
                        break
            if getroffen:
                continue

            # --- Nichts hat gepasst: erst pruefen, ob hier gesprochen wird ---
            # VOR dem Hinweis: Die Aeusserung, die die Grenze erreicht, soll
            # keinen Hinweis mehr in den Raum sprechen. Begruendung bei
            # GESPRAECH_GRENZE.
            jetzt = time.time()
            leer_zeiten.append(jetzt)
            while leer_zeiten and jetzt - leer_zeiten[0] > GESPRAECH_FENSTER_S:
                leer_zeiten.popleft()
            if len(leer_zeiten) >= GESPRAECH_GRENZE:
                melde(f"Gespraech erkannt: {len(leer_zeiten)} Aeusserungen ohne Befehl "
                      f"in {GESPRAECH_FENSTER_S:.0f} s - Sprachsteuerung aus")
                hoert_zu = False
                leer_zeiten.clear()
                erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, GRAMMATIK_AUS)
                sprich(ANSAGE_GESPRAECH)
                mitschrift_schliessen()
                continue

            # --- Nichts hat gepasst: sagen, was gehoert wurde ---
            # Vorher endete der Ablauf hier mit einem stummen "continue". Das
            # war die Stelle, an der 283 Befehlsversuche lautlos verpufften.
            if hinweis_faellig(worte, letzter_hinweis):
                letzter_hinweis = time.time()
                text_hinweis = hinweis_text(worte)
                melde(f"  kein Befehl - Hinweis: {text_hinweis!r}")
                sprich(text_hinweis)
            else:
                melde("  kein Befehl - kein Hinweis (zu kurz, [unk] oder Bremse)")
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
