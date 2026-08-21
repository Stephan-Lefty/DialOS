#!/usr/bin/env python3
"""DialOS: Diktat - Sprache zu Text.

Zwei Betriebsarten desselben Werkzeugs, und die Unterscheidung ist
wesentlich (siehe docs/diktat.md und docs/sprachsteuerung.md):

  BEFEHLE  dialos-sprachbefehl-desktop.py, eingeschraenkte Grammatik aus
           wenigen festen Saetzen, kleines Modell. Damit kann kein
           Gespraech und kein Radio etwas ausloesen.
  DIKTAT   dieses Skript, FREIE Erkennung, grosses Modell. Hier ist jedes
           Wort erlaubt - deshalb darf es nur laufen, wenn der Nutzer es
           ausdruecklich verlangt hat.

WARUM ZWEI PROZESSE UND NICHT EINER: Das grosse Modell braucht 5,5 GB und
11,6 s zum Laden (gemessen 2026-08-18). Der Befehlsdienst laeuft die ganze
Sitzung mit und muss klein und schnell bleiben.

DAS MIKROFON GEHOERT IMMER NUR EINEM. Liefen beide Erkennungen zugleich,
wuerde ein diktierter Satz auch als Befehl ausgewertet - "auf windows
umschalten" mitten in einem Brief wuerde den Schreibtisch umstellen.
Deshalb legt dieses Skript die Marke DIKTAT_MARKE an, solange es laeuft;
der Befehlsdienst haelt sich dann heraus. Dasselbe Muster wie die
Markierung "das System spricht gerade", die sich bei der Sprachausgabe
bewaehrt hat.

DER SCHLUSSSATZ LAEUFT UEBER EINEN ZWEITEN ERKENNER MIT EINGESCHRAENKTER
GRAMMATIK - und das ist die Lehre aus dem ersten Test am 2026-08-18. Der
Schlusssatz wurde zuerst in der freien Erkennung gesucht. Ergebnis: Stephan
sagte "diktat beenden", das Protokoll zeigt 'diktat wird erhoeht'. Bei
freier Erkennung hat das Modell zehntausende Moeglichkeiten, und ein
BESTIMMTER Satz ist darin nicht zuverlaessig zu treffen - genau der Effekt,
der schon "gnome" zu "genug" und "windows" zu "sinnlose" gemacht hat.

Deshalb laufen jetzt zwei Erkenner ueber dasselbe Audio: der grosse fuer
den Text, und ein kleiner, der NUR den Schlusssatz kennt. Das kostete
gemessen 0,4 s Ladezeit und 229 MB - gegenueber 5,5 GB des grossen Modells
fällt es nicht auf. Und es ist dieselbe Einsicht, auf der die ganze
Befehlserkennung beruht: Wer einen bestimmten Satz sicher erkennen will,
darf dem Modell nichts anderes zur Auswahl geben.

DIE SCHREIBUNG KOMMT VON LANGUAGETOOL. Vosk liefert Woerter ohne
Satzzeichen und alles klein; Deutsch schreibt alle Substantive gross. Vier
Verfahren mit Wortlisten und hunspell kamen auf 90 bis 92,5 %,
LanguageTool auf 98,1 % - die vollstaendige Messung steht in
docs/diktat.md. Laeuft der Dienst nicht, wird trotzdem geschrieben, nur
klein: Ein fehlendes Grosses ist ein Schoenheitsfehler, ein verlorener
Satz ist einer zu viel.

Aufruf:
    dialos-diktat.py notiz [NAME]   Diktat in eine Notiz (Standard: notizen)
    dialos-diktat.py --debug ...    zeigt jeden erkannten Satz
Beenden durch den Satz "diktat beenden" oder mit Strg+C.
"""

import array
import json
import math
import os
import re
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request

MODELL_GROSS = "/usr/local/share/vosk-model-de-big"
MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
SAY = "/usr/local/bin/dialos-say.py"
ECHO_QUELLE = "dialos_mikrofon_ohne_echo"
LT_ADRESSE = "http://127.0.0.1:8081/v2/check"
LT_ZEITGRENZE_S = 10.0

DEBUG = "--debug" in sys.argv

# Das Protokoll wird IMMER geschrieben, nicht nur mit "--debug" (Fehler vom
# 2026-08-18): Beim ersten Test mit Stephans Stimme ging die Ausgabe nur in
# sein Terminal, und damit war hinterher nicht mehr feststellbar, WAS
# erkannt worden war - nur noch, was in der Notiz stand. Bei einer
# Erkennung, die man nur durch Vergleichen von Gesagtem und Geschriebenem
# beurteilen kann, ist das die entscheidende Information.
PROTOKOLL = os.path.join(os.path.expanduser("~"), "dialos-diktat.log")

# Der Satz, der das Diktat beendet. Er wird NUR erkannt, wenn er die
# gesamte Aeusserung ist - sonst koennte man ihn in einem Brief nicht
# erwaehnen, ohne das Diktat abzubrechen.
SCHLUSSSATZ = "diktat beenden"
GRAMMATIK_SCHLUSS = json.dumps([SCHLUSSSATZ, "[unk]"])
SCHLUSS_WOERTER = set(SCHLUSSSATZ.split())          # {"diktat", "beenden"}

# SPERRFRIST FUER DEN SCHLUSS (2026-08-21). Am selben Tag endete ein Diktat
# sechs Sekunden nach dem Start von selbst: Der Schluss-Erkenner lieferte das
# nackte 'beenden', obwohl Stephan nach eigener Aussage nichts gesagt hatte.
# Der Brief blieb leer, und seine Saetze liefen danach in die
# Befehlserkennung, die sie in Unsinn presste ('gnome gnome welchen tag linux').
#
# DIE URSACHE IST NICHT GEFUNDEN, und das steht hier bewusst so. Zwei
# Messungen haben sie NICHT bestaetigt:
#   - 180 s Stille im selben Raum, dieselbe Grammatik: 0 Ergebnisse.
#   - Dreimal die Bereit-Ansage gesprochen und sofort zugehoert: nichts.
# Weder Umgebungsgeraeusch noch die eigene Ansage reichen also als Erklaerung.
#
# DIESE SPERRE IST DESHALB KEINE BEHEBUNG, SONDERN EINE ABSICHERUNG: Niemand
# sagt drei Sekunden nach dem Start "Diktat beenden" - wer diktieren will,
# diktiert. Ein Schluss in diesem Fenster ist mit hoher Wahrscheinlichkeit
# keiner, und der Schaden davon ist gross (leeres Ergebnis), waehrend der
# Schaden der Sperre klein ist (drei Sekunden warten, falls jemand es doch
# sofort abbrechen will).
SCHLUSS_SPERRFRIST_S = 3.0


# PEGEL-TOR (gemessen am 2026-08-21, Stephans Stimme, 120 s).
#
# DAS PROBLEM: Das grosse Modell erfindet in Stille Woerter. Gemessen wurden
# in 80 s Ruhe sieben Stueck - 'koeln', 'einen gefunden', 'vom', 'ln'. Im
# Diktat landen die im Brief: Wer beim Diktieren nachdenkt, bekommt "koeln"
# mitten in seine Kuendigung geschrieben. Das betrifft JEDES Diktat, nicht nur
# Briefe; beim Einkaufszettel duerfte es bisher als falsch verstandene Ware
# durchgegangen sein.
#
# DIE MESSUNG trennt sauber - Mittelpegel je Aeusserung:
#
#     'koeln'   (Rauschen)          71
#     'nun'     (Rauschen)          84
#     'einen'   (Rauschen)          47
#     Stephans Saetze         3475 - 4196
#     'sechsundzwanzig'            350   <- echte Sprache, aber leise
#
# WARUM AM ERGEBNIS UND NICHT AM AUDIOSTROM: Ein Tor, das leise Bloecke gar
# nicht erst durchlaesst, zerschneidet Woerter - zwischen zwei Silben ist es
# still. Am fertigen Ergebnis zu pruefen kostet nichts und kann nichts
# zerteilen.
#
# DIE SCHWELLE liegt bewusst naeher am Rauschen als an der Sprache: 150 ist
# das Doppelte des lautesten gemessenen Rauschens und weniger als die Haelfte
# der leisesten echten Aeusserung. Jede verworfene Aeusserung wird
# protokolliert - faellt dort echte Sprache hinein, sieht man es sofort.
PEGEL_SCHWELLE = 150.0


def pegel(block):
    """Effektivwert eines Audioblocks (16 Bit, mono)."""
    werte = array.array("h")
    werte.frombytes(block[:len(block) // 2 * 2])
    if not werte:
        return 0.0
    return math.sqrt(sum(w * w for w in werte) / len(werte))


def ist_schluss(gehoert):
    """Beendet diese Aeusserung das Diktat? Nur der VOLLE Satz zaehlt.

    GEZAEHLT AM 2026-08-21, alle Schluss-Ereignisse eines Testtages:

        nacktes 'beenden'        6 x falsch ausgeloest, 3 x echt
        volles 'diktat beenden'  0 x falsch,            2 x echt

    Jeder einzelne Fehlauslöser war ein nacktes 'beenden'. Zweimal beendete
    sich ein Diktat dadurch, bevor ueberhaupt etwas gesprochen war; einmal
    machte der Erkenner aus einem Bruchstueck von Stephans Diktat ein
    'beenden', waehrend er gerade den Brief sprach. Beim naechsten Mal haette
    dasselbe Bruchstueck ihn mitten im Satz gestoppt.

    WARUM DAS FRUEHER ANDERS ENTSCHIEDEN WAR: Am 2026-08-18 lieferte der
    Schluss-Erkenner in sieben Minuten Dauergerede nur zweimal etwas anderes
    als '[unk]', und beide Male war es ein echtes 'beenden'. Daraus wurde die
    Regel "es genuegt das Wort". Diese Messung hat aber nie geprueft, was beim
    normalen DIKTIEREN passiert - und genau dort entstehen die Bruchstuecke.

    Der Preis ist gering: Der volle Satz wurde an demselben Tag zweimal sauber
    erkannt, und wird er einmal nicht erkannt, sagt DialOS es (siehe
    ANSAGE_SCHLUSS_UNKLAR). Der Nutzer spricht also nie ins Leere, ohne es zu
    merken - das war der eigentliche Schaden der alten Regel.

    Die Bedingungen im Einzelnen:
      - kein "[unk]" (da wurde noch etwas anderes gesprochen),
      - BEIDE Woerter des Schlusssatzes kommen vor,
      - und ausser Woertern des Schlusssatzes nichts weiter.
    """
    worte = gehoert.split()
    if not worte or "[unk]" in worte:
        return False
    if not SCHLUSS_WOERTER <= set(worte):
        return False
    return set(worte) <= SCHLUSS_WOERTER


def ist_halber_schluss(gehoert):
    """Klingt nach Schluss, ist aber nicht der volle Satz.

    Dafuer gibt es die Ansage: Wer "beenden" sagt und nichts passiert, wuerde
    sonst dasselbe Wort wiederholen, bis er aufgibt.
    """
    worte = gehoert.split()
    if not worte or "[unk]" in worte:
        return False
    return "beenden" in worte and set(worte) <= SCHLUSS_WOERTER


ANSAGE_BEREIT = "Ich schreibe mit."

# WENN EIN SCHLUSS VERWORFEN WIRD, MUSS DER NUTZER DAS HOEREN (2026-08-21).
#
# Stephan sagte dreimal "Diktat beenden", zweimal wurde es verworfen
# (nacktes 'beenden' ohne vorherige Aeusserung), und er bekam kein Wort
# zurueck. Am Bildschirm ist das aergerlich; wer den Bildschirm nicht sieht,
# hat keine Moeglichkeit herauszufinden, warum nichts passiert - er
# wiederholt dasselbe Wort, und es passiert wieder nichts.
#
# EINMAL je Diktat, nicht bei jedem Verwerfen: Eine Ansage, die sich
# wiederholt, wird zum Geraeusch - und sie liefe selbst wieder ins Mikrofon.
ANSAGE_SCHLUSS_UNKLAR = "Sage bitte: Diktat beenden."
# ZURZEIT UNBENUTZT - siehe die Begruendung an der Auswertung des halben
# Schlusses. Die Ansage bleibt stehen, weil sie mit der Sprechpause-Regel
# zurueckkommt; geloescht muesste sie dann wortgleich neu erfunden werden.

# ZIELE, DIE EINE LISTE SIND UND KEIN TEXT (2026-08-19). Bei einem
# Einkaufszettel ist jede Ware ein eigener Eintrag; in einem Brief ist eine
# Aeusserung ein Satz. Das aendert zwei Dinge - die Anleitung am Anfang und die
# Zerlegung einer Aeusserung.
#
# Warum ueberhaupt: Stephan sagte "Milch sechs Eier Butter" in einem Zug. Vosk
# liefert das als EINE Aeusserung, eine Aeusserung ist ein Eintrag, und beim
# Vorlesen kam die ganze Liste in einem Atemzug - die Pause setzt DialOS
# zwischen Eintraege, nicht innerhalb. Nach drei Tests standen drei solche
# Zeilen im Zettel, und "3 Eintraege" klang wie dreimal dasselbe.
LISTEN_ZIELE = ("einkaufszettel",)

# BRIEFE GEHEN NICHT IN DEN NOTIZORDNER (Stephan, 2026-08-21). Eine Notiz ist
# ein Arbeitszettel, der bei jedem Diktat ERGAENZT wird; ein Brief ist ein
# fertiges Stueck, das einen Kopf, ein Datum und eine Fusszeile hat. Wuerde er
# angehaengt, staende der zweite Brief unter der Fusszeile des ersten.
BRIEF_ZIELE = ("brief",)

# Anleitung nur bei einer Liste, und nur EIN Satz. Der Nutzer sieht nicht, dass
# gerade ein einziger Eintrag entsteht statt drei - gesagt werden muss es
# deshalb, aber kurz: waehrend DialOS spricht, hoert es nicht zu.
ANSAGE_BEREIT_LISTE = ("Ich schreibe mit. Sage jede Ware einzeln, "
                       "mit einer kleinen Pause dazwischen.")

# Rueckfallebene, wenn doch alles in einem Zug kommt: an "und" trennen. Das ist
# die Art, wie man eine Einkaufsliste ohnehin spricht ("Milch und sechs Eier
# und Butter"). Bewusst NUR bei Listen-Zielen - in einem Brief wuerde aus "Ich
# habe Milch und Butter gekauft" sonst zwei Zeilen.
TRENNWORT = re.compile(r"\s+und\s+", re.IGNORECASE)


def eintraege_aus(name, text):
    """Eine Aeusserung in Eintraege zerlegen - bei Listen an "und"."""
    if name not in LISTEN_ZIELE:
        return [text]
    teile = [t.strip(" .,;:") for t in TRENNWORT.split(text)]
    teile = [t for t in teile if t]
    if len(teile) < 2:
        return teile or [text]
    # Jeder Eintrag faengt gross an. Die Schreibhilfe hat die Aeusserung als
    # EINEN Satz gesehen und nur das erste Wort gross gemacht - nach dem
    # Trennen stuende sonst "Milch / sechs Eier / Butter" im Zettel, und ein
    # sehender Helfer liest den Zettel auch.
    return [t[0].upper() + t[1:] for t in teile]
# ANSAGE_ENDE ist am 2026-08-19 entfallen: Der Satz "Diktat beendet." wird
# jetzt in ansage_ende() zusammengesetzt, zusammen mit der Anzahl und dem
# Hinweis aufs Vorlesen. Eine Konstante, die niemand mehr benutzt, sieht beim
# Lesen wie die gueltige Ansage aus - das ist schlimmer als eine fehlende.

# Nach dem Diktat: HINWEIS statt Vorlesen (Stephan, 2026-08-19). Bis dahin las
# "Diktat beenden" den ganzen Zettel vor - und machte damit den Befehl
# "Einkaufszettel vorlesen" ueberfluessig, ohne dem Nutzer die Wahl zu lassen.
# Wer nur drei Waren aufschreibt, will sie nicht dreimal hoeren; wer zwanzig
# diktiert hat, will es vielleicht doch. Also fragt DialOS nicht nach, sondern
# sagt, wie man es bekommt - eine Rueckfrage waere eine Pflicht zum Antworten.
#
# Nur Ziele, fuer die es den Vorlese-Befehl WIRKLICH gibt (siehe
# docs/sprachbefehle.md): einem blinden Nutzer einen Satz nennen, den die
# Grammatik nicht kennt, waere schlimmer als gar kein Hinweis. Ein unbekanntes
# Ziel bekommt deshalb nur die Bestaetigung ohne Hinweis.
VORLESEN_HINWEIS = {
    "einkaufszettel": ("Deinen Einkaufszettel", "Einkaufszettel vorlesen"),
    "notizen": ("Deine Notizen", "Notizen vorlesen"),
    # Beim Brief ist das Vorlesen keine Bequemlichkeit, sondern die einzige
    # Kontrolle: Vosk liefert rund 2 % falsch geschriebene Woerter, und wer
    # den Bildschirm nicht sieht, findet sie nur beim Hoeren.
    "brief": ("Deinen Brief", "Brief vorlesen"),
}


def ansage_ende(name, anzahl):
    """Bestaetigung nach dem Diktat, mit Hinweis aufs Vorlesen.

    Die Anzahl gehoert hinein, weil sie das Vorlesen ersetzt: Sie ist das
    einzige, woran ein blinder Nutzer merkt, dass ueberhaupt etwas angekommen
    ist - und wieviel. "Diktat beendet." allein liesse ihn im Dunkeln.
    """
    # EIN BRIEF HAT KEINE EINTRAEGE (2026-08-21). "Diktat beendet, 4 Einträge
    # geschrieben" beschreibt einen Zettel, keinen Brief - und die Anzahl sagt
    # dem Nutzer hier nichts, weil ein Brief nicht aus Posten besteht. Was ihm
    # etwas sagt, ist die Anzahl der SAETZE, denn danach hat er diktiert.
    if name in BRIEF_ZIELE:
        satz = ("Der Brief ist geschrieben, ein Satz." if anzahl == 1
                else f"Der Brief ist geschrieben, {anzahl} Sätze.")
    else:
        satz = ("Diktat beendet, ein Eintrag geschrieben." if anzahl == 1
                else f"Diktat beendet, {anzahl} Einträge geschrieben.")
    hinweis = VORLESEN_HINWEIS.get(name)
    if hinweis:
        besitz, befehl = hinweis
        satz += f" Möchtest Du {besitz} vorgelesen haben, dann sage: {befehl}."
    return satz
ANSAGE_LEER = "Ich habe nichts verstanden."
ANSAGE_ZEITGRENZE = "Ich höre auf mitzuschreiben."

# Nach so langer STILLE beendet sich das Diktat von selbst (Stephan,
# 2026-08-18, nach einem Diktat, das sieben Minuten offen blieb).
#
# Bewusst nach Stille und NICHT nach Laufzeit: Wer einen langen Brief
# diktiert, darf nicht mitten im Satz unterbrochen werden. Bleibt es aber
# zwei Minuten still, hat der Nutzer entweder das Beenden vergessen oder ist
# gar nicht mehr da.
#
# Hier ist die Grenze wichtiger als bei der Befehlserkennung, obwohl sie
# dort schon existiert: Die Befehlserkennung kennt fuenf Saetze, das Diktat
# schreibt JEDES Wort mit - auch ein Gespraech, das gar nicht an DialOS
# gerichtet war.
DIKTAT_ZEITGRENZE_S = 120.0
# "Zettel und Stift" statt "Schreibhilfe" (Stephan, 2026-08-18). Der Satz
# deckt die rund 9 s Ladezeit des grossen Modells ab. Er erklaert dem
# Nutzer in seiner Sprache, was gerade passiert, ohne von Modellen zu
# reden - und macht aus einer technischen Wartezeit einen verstaendlichen
# Vorgang.
ANSAGE_LADEN = "Einen Moment, ich hole Zettel und Stift."

NOTIZ_ORDNER = os.path.join(os.path.expanduser("~"), "Notizen")
DOKUMENT_ORDNER = os.path.join(os.path.expanduser("~"), "Dokumente")
FUSSZEILE_SKRIPT = "/usr/local/bin/dialos-fusszeile.py"
NAMEN_SKRIPT_PFAD = "/usr/local/bin/dialos-namen.py"
ABSENDER = "/usr/local/share/dialos/absender.txt"

# DER HINWEIS AN DER STELLE DER UNTERSCHRIFT (Stephan, 2026-08-21). Ein Brief
# ohne Unterschrift wirft beim Empfaenger die Frage auf, ob jemand etwas
# vergessen hat - der Hinweis beantwortet sie, bevor sie entsteht.
#
# WARUM NICHT "ohne Unterschrift gueltig", die uebliche Formel: Das ist eine
# rechtliche Aussage. Bei Schriftform-Erfordernis - und Kuendigungen sind
# genau der Fall, den wir als Beispiel benutzen - ist ein Brief ohne
# eigenhaendige Unterschrift eben NICHT gueltig. Der Hinweis erklaert die
# fehlende Unterschrift, er ersetzt sie nicht.
#
# WARUM ER TROTZ DER FUSSZEILE NOETIG IST, die dasselbe Verfahren nennt: Die
# Fusszeile steht unten rechts als Herkunftsangabe und gehoert zum Blatt. Der
# Unterschriftshinweis steht dort, wo der Empfaenger die Unterschrift SUCHT.
# Zwei Stellen, zwei Aufgaben.
#
# DASS "per Spracheingabe" DAMIT ZWEIMAL AUF DEM BLATT STEHT, ist gesehen und
# so entschieden (Stephan, 2026-08-21, nach Vorlage der drei Moeglichkeiten:
# so lassen, Hinweis kuerzen, Fusszeile im Brief weglassen). Wer das spaeter
# fuer eine Doppelung haelt und eine der beiden Zeilen streicht, nimmt dem
# Brief entweder die Herkunftsangabe oder die Erklaerung der fehlenden
# Unterschrift - es ist keine Nachlaessigkeit, sondern eine Wahl.
UNTERSCHRIFT_HINWEIS = ("Dieser Brief wurde per Spracheingabe erstellt und "
                        "ist deshalb nicht unterschrieben.")


def marke_pfad(name):
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


DIKTAT_MARKE = marke_pfad("dialos-diktat-aktiv")


def melde(text):
    if DEBUG:
        print(text, flush=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')}  {text}\n")
    except OSError:
        pass          # ein fehlendes Protokoll darf kein Diktat verhindern


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


# ------------------------------------------------------------ Schreibung

def lt_lebt():
    try:
        urllib.request.urlopen("http://127.0.0.1:8081/v2/languages", timeout=3).read(1)
        return True
    except Exception:
        return False


# GESPROCHENE SATZZEICHEN - ZWEIWORTIGE MERKWOERTER (gemessen 2026-08-21).
#
# ERSTER ENTWURF WAREN DIE NACKTEN WOERTER "komma", "punkt", "absatz".
# Stephans Entscheidung dazu lautete "immer als Satzzeichen werten", mit dem
# bewussten Preis, dass "in diesem Punkt" zu "in diesem." wird. GEMESSEN hat
# sich das nicht gehalten - die kurzen Woerter werden gar nicht zuverlaessig
# erkannt:
#
#     gesagt                       Piper            Stephans Stimme
#     "...Herren komma"            komma  ok        komme        falsch
#     "...Herren (Pause) komma"    komme  falsch    komma        ok
#     "komma" allein               ja     falsch    einen koffer falsch
#     "punkt" allein               das    falsch    kommt        falsch
#     "doppelpunkt" allein         doerte depots    -
#
# Drei von sechs. Es liegt weder an der Aussprache noch an der Pause - bei
# Piper klappte das Gegenteil. Es ist das Sprachmodell: Es raet aus dem
# Zusammenhang, und nach "Roessner" ist "komme" wahrscheinlicher als "Komma".
#
# DIE ZWEITE MESSUNG hat die Loesung gezeigt - dieselbe Stimme, dieselbe Kette:
#
#     "...Roessner komma setzen"        komma setzen        ok
#     "...Vertrag punkt setzen"         punkt setzen        ok
#     "...helfen fragezeichen setzen"   fragezeichen setzen ok
#     "neuer satz"                      neuer ersatz        falsch
#
# Dreimal von drei. Dieselbe Lektion wie beim Einschalten der
# Sprachsteuerung: Ein Merkwort muss eindeutig UND lang genug sein.
#
# DIE NACKTEN FORMEN SIND DESHALB RAUS, und das ist ein doppelter Gewinn: Die
# Erkennung wird zuverlaessig, UND der eingangs akzeptierte Preis entfaellt -
# "in diesem Punkt" bleibt stehen, weil nur "Punkt setzen" ein Zeichen macht.
# "neuer satz" wurde nicht aufgenommen, weil es gemessen scheitert.
#
# Laengere Wendungen zuerst, sonst frisst "absatz" den "neuen absatz".
SATZZEICHEN = [
    ("neuer absatz", "\n\n"),
    ("neue zeile", "\n"),
    ("komma setzen", ","),
    ("punkt setzen", "."),
    ("fragezeichen setzen", "?"),
    ("ausrufezeichen setzen", "!"),
    ("doppelpunkt setzen", ":"),
    ("gedankenstrich setzen", " - "),
]


def satzzeichen_setzen(satz):
    """Ersetzt gesprochene Satzzeichen durch die Zeichen selbst.

    WORTWEISE UND NICHT PER TEXTSUCHE. Eine Ersetzung im Fliesstext haette
    "Punkte", "Kommando" und "Absatzweise" mitgetroffen - der Text zerfiele an
    Stellen, an denen der Nutzer nie ein Satzzeichen gesagt hat.

    Das Zeichen haengt am Wort davor, ohne Leerzeichen; danach kommt eines.
    Absaetze raeumen die Leerzeichen davor weg, damit keine Zeile mit einem
    Leerzeichen endet.
    """
    tabelle = dict(SATZZEICHEN)
    worte = satz.split()
    teile = []
    i = 0
    while i < len(worte):
        zwei = " ".join(worte[i:i + 2]).lower()
        if len(worte) - i >= 2 and zwei in tabelle:
            teile.append(("zeichen", tabelle[zwei]))
            i += 2
            continue
        eins = worte[i].lower()
        if eins in tabelle:
            teile.append(("zeichen", tabelle[eins]))
            i += 1
            continue
        teile.append(("wort", worte[i]))
        i += 1

    text = ""
    for art, wert in teile:
        if art == "wort":
            if text and not text.endswith(("\n", " ")):
                text += " "
            text += wert
        elif wert.startswith("\n"):
            text = text.rstrip() + wert
        elif wert == " - ":
            text = text.rstrip() + wert
        else:
            text = text.rstrip() + wert + " "
    return text.strip()


def schreibung_richten(satz):
    """Gross- und Kleinschreibung ueber LanguageTool, Satzanfang selbst.

    Uebernommen werden AUSSCHLIESSLICH reine Schreibungs-Korrekturen, also
    Vorschlaege, die dasselbe Wort nur gross schreiben. Alles andere wird
    verworfen - LanguageTool wuerde sonst auch Woerter ersetzen ("milch"
    zu "mich"), und ein diktierter Text darf nicht inhaltlich verbessert
    werden. Was der Nutzer gesagt hat, bleibt stehen.
    """
    if not satz:
        return satz
    try:
        daten = urllib.parse.urlencode({"text": satz, "language": "de-DE"}).encode()
        with urllib.request.urlopen(LT_ADRESSE, daten, timeout=LT_ZEITGRENZE_S) as a:
            treffer = json.load(a).get("matches", [])
    except Exception as fehler:
        # Bewusst nur eine Meldung, kein Abbruch: Klein geschriebener Text
        # ist besser als kein Text.
        melde(f"  (LanguageTool nicht erreichbar: {fehler})")
        return satz[:1].upper() + satz[1:]

    aenderungen = []
    for t in treffer:
        o, l = t["offset"], t["length"]
        urspruenglich = satz[o:o + l]
        if not urspruenglich[:1].islower():
            continue
        gross = urspruenglich[:1].upper() + urspruenglich[1:]
        for vorschlag in t.get("replacements", []):
            if vorschlag["value"] == gross:
                aenderungen.append((o, l, gross))
                break
    neu = satz
    for o, l, wort in sorted(aenderungen, reverse=True):
        neu = neu[:o] + wort + neu[o + l:]
    return neu[:1].upper() + neu[1:]


# -------------------------------------------------------------- Aufnahme

def waehle_mikrofon():
    """Wie im Befehlsdienst: bereinigte Quelle, sonst das eingebaute.

    Kein Bluetooth und kein USB - Stephans Festlegung vom 2026-08-17,
    Begruendung in docs/hardware.md.
    """
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


def aufnahme_starten(quelle):
    return subprocess.Popen(
        ["parec", "-d", quelle, "--format=s16le",
         f"--rate={ABTASTRATE}", "--channels=1"],
        stdout=subprocess.PIPE)


# ----------------------------------------------------------------- Ablauf

def aufzaehlen(zeilen):
    """Macht aus den Eintraegen eine Aufzaehlung, die sich anhoeren laesst.

    Der Punkt am Ende jedes Eintrags ist Absicht und nicht das Komma: Ein
    Einkaufszettel ist keine Aufzaehlung in einem Satz, sondern eine Folge
    einzelner Dinge. Piper macht am Punkt eine deutlichere Pause als am
    Komma, und genau die braucht der Zuhoerer, um mitzuzaehlen.
    """
    saubern = lambda z: z.rstrip(" .,;:")
    return " ".join(saubern(z) + "." for z in zeilen if saubern(z))


def holen(pfad, name, ersatz=None):
    """Holt eine Funktion oder einen Wert aus einem anderen DialOS-Skript.

    Geholt statt kopiert - dieselbe Regel wie bei anrede(). Faellt das Skript
    aus, kommt der Ersatz zurueck: Ein Brief ohne Fusszeile ist besser als kein
    Brief.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("geholt_" + name, pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    except Exception:
        return ersatz


def datum_ausgeschrieben(heute=None):
    """"21. August 2026" - Monatsnamen aus dialos-start-ansage.py.

    Nicht abgeschrieben: Die Liste steht dort schon, und zwei Listen mit
    Monatsnamen laufen irgendwann auseinander.
    """
    import datetime
    heute = heute or datetime.date.today()
    ansage = holen("/usr/local/bin/dialos-start-ansage.py", "ansage")
    monate = getattr(ansage, "MONATE", None) if ansage else None
    if not monate:
        return heute.strftime("%d.%m.%Y")
    return f"{heute.day}. {monate[heute.month - 1]} {heute.year}"


def absenderzeilen():
    """Der Absenderblock, falls er erfasst ist - sonst nichts.

    Die Anschrift steht bewusst NICHT im Abbild: Sie gehoert dem Nutzer und
    wird bei der Ersteinrichtung eingetragen. Fehlt sie, faellt der Block
    ersatzlos weg - ein Brief mit leeren Platzhalterzeilen waere schlimmer als
    einer ohne Kopf, weil ein blinder Nutzer die Luecke nicht sieht.
    """
    zeilen = []
    namen = holen(NAMEN_SKRIPT_PFAD, "namen")
    if namen:
        try:
            geschrieben = namen.nutzer_name_geschrieben()
            if geschrieben:
                zeilen.append(geschrieben)
        except Exception:
            pass
    try:
        with open(ABSENDER, encoding="utf-8") as f:
            for zeile in f:
                zeile = zeile.strip()
                if zeile and not zeile.startswith("#"):
                    zeilen.append(zeile)
    except OSError:
        pass
    return zeilen


def briefbogen(text):
    """Setzt den diktierten Text in einen Briefbogen aus reinem Text.

    Absender und Datum rechtsbuendig, der Text linksbuendig, die Fusszeile
    unten rechts - dieselbe Breite und dasselbe Verfahren wie in
    dialos-fusszeile.py, weil es dieselbe Seite ist.
    """
    fuss = holen(FUSSZEILE_SKRIPT, "fusszeile")
    breite = getattr(fuss, "BREITE", 76) if fuss else 76

    def rechts(zeile):
        if fuss:
            return fuss.rechtsbuendig(zeile, breite)
        return zeile.rjust(breite) if len(zeile) < breite else zeile

    teile = []
    absender = absenderzeilen()
    if absender:
        teile += [rechts(z) for z in absender]
        teile.append("")
    teile.append(rechts(datum_ausgeschrieben()))
    teile.append("")
    teile.append("")
    # UMBRUCH AUF DIESELBE BREITE. Ohne ihn stuende der Fliesstext in einer
    # einzigen 118 Zeichen langen Zeile, waehrend Datum und Fusszeile bei 76
    # ausgerichtet sind - ein Briefbogen mit zwei Breiten ist keiner. Absaetze
    # bleiben Absaetze: umgebrochen wird je Absatz, nicht ueber den ganzen Text.
    absaetze = []
    for absatz in text.rstrip().split("\n\n"):
        einzeln = " ".join(absatz.split())
        absaetze.append(textwrap.fill(einzeln, breite) if einzeln else "")
    teile.append("\n\n".join(absaetze))
    teile.append("")
    # Linksbuendig und nicht rechts: Er gehoert zum Brief, nicht zum Briefkopf -
    # und beim Vorlesen zaehlt er deshalb zum Text, wird also mitgelesen.
    teile.append(textwrap.fill(UNTERSCHRIFT_HINWEIS, breite))
    teile.append("")
    teile.append("")
    satz = fuss.text("dokument") if fuss else \
        "Dieses Dokument wurde per Spracheingabe powered by DialOS.org erstellt!"
    teile.append(rechts(satz))
    return "\n".join(teile) + "\n"


def brief_schreiben(zeilen):
    """Schreibt den Brief - und legt einen vorhandenen zur Seite, statt ihn
    zu ueberschreiben.

    "brief.txt" bleibt der eine Brief, den der Nutzer meint, wenn er "Brief
    vorlesen" sagt. Der vorige wandert mit Datum und Uhrzeit im Namen daneben.
    Ueberschreiben waere hier schlimmer als bei einer Notiz: Ein Brief ist
    Arbeit von Minuten, und wer ihn verliert, merkt es erst, wenn er ihn
    braucht.
    """
    os.makedirs(DOKUMENT_ORDNER, exist_ok=True)
    pfad = os.path.join(DOKUMENT_ORDNER, "brief.txt")
    if os.path.exists(pfad) and os.path.getsize(pfad) > 0:
        beiseite = os.path.join(
            DOKUMENT_ORDNER,
            "brief-" + time.strftime("%Y-%m-%d-%H%M%S") + ".txt")
        try:
            os.replace(pfad, beiseite)
            melde(f"  vorigen Brief beiseitegelegt: {beiseite}")
        except OSError as fehler:
            melde(f"  konnte den vorigen Brief nicht beiseitelegen: {fehler}")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(briefbogen("\n".join(zeilen)))
    return pfad


def notiz_schreiben(name, zeilen):
    os.makedirs(NOTIZ_ORDNER, exist_ok=True)
    sicher = re.sub(r"[^\w -]", "", name).strip() or "notizen"
    pfad = os.path.join(NOTIZ_ORDNER, sicher + ".txt")
    with open(pfad, "a", encoding="utf-8") as f:
        for z in zeilen:
            f.write(z + "\n")
    return pfad


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    zweck = argumente[0] if argumente else "notiz"
    name = argumente[1] if len(argumente) > 1 else "notizen"

    if not os.path.isdir(MODELL_GROSS):
        sprich("Mir fehlt das große Sprachmodell. Ich kann nicht mitschreiben.")
        print(f"Modell fehlt: {MODELL_GROSS}", file=sys.stderr)
        return 1

    quelle = waehle_mikrofon()
    if not quelle:
        sprich(anrede("Ich finde kein Mikrofon. Diktat ist nicht möglich."))
        return 1

    if not lt_lebt():
        # Ansagen und trotzdem weitermachen. Der Nutzer soll wissen, dass
        # die Schreibung diesmal nicht stimmt - stillschweigend kleinen
        # Text zu liefern waere die schlechtere Wahl.
        melde("  (Schreibhilfe laeuft nicht - es wird klein geschrieben)")
        sprich("Die Schreibhilfe läuft nicht. Ich schreibe klein weiter.")

    # DIE MARKE MUSS VOR DEM LADEN GESETZT WERDEN (Fehler vom 2026-08-18).
    # Sie stand zuerst hinter dem Modell-Laden, und das dauert rund 9
    # Sekunden. In dieser Zeit hoerte der Befehlsdienst noch mit - der
    # Nutzer sagt "Diktat starten", faengt nach der Ansage an zu sprechen,
    # und seine ersten Saetze waeren als Befehle ausgewertet worden. Genau
    # der Fall, den die Marke verhindern soll, nur zeitversetzt.
    #
    # Ab hier gilt: alles bis zum Ende in try/finally, damit die Marke auch
    # bei einem Fehler beim Laden wieder verschwindet. Eine liegengebliebene
    # Marke wuerde die Sprachsteuerung fuer den Rest der Sitzung stumm
    # schalten.
    open(DIKTAT_MARKE, "w").close()
    try:
        return diktat_fuehren(zweck, name, quelle)
    finally:
        try:
            os.unlink(DIKTAT_MARKE)
        except OSError:
            pass


def aeusserung_verarbeiten(name, text):
    """Der Weg jeder Aeusserung: Satzzeichen, Schreibung, Zerlegung.

    Herausgeloest, damit der Resttext nach dem Schluss GENAU denselben Weg
    nimmt wie jede andere Aeusserung. Zwei Kopien dieses Ablaufs waeren zwei
    Stellen, an denen kuenftig eine Aenderung vergessen wird.

    SATZZEICHEN VOR LanguageTool, und der Grund ist GEMESSEN, nicht vermutet
    (2026-08-21). Ich hatte behauptet, mit Satzzeichen entscheide LanguageTool
    die Grossschreibung besser. Fuer die SUBSTANTIVE stimmt das nicht -
    "Damen", "Herren", "Vertrag", "Termin", "Kuendigung", "Gruessen" kamen mit
    und ohne Zeichen gleich heraus. Was Satzzeichen bringen, sind die
    SATZANFAENGE:

        ohne:  ... schriftlich mit freundlichen Gruessen
        mit:   ... schriftlich. Mit freundlichen Gruessen

    In einem Brief ist das kein Schoenheitsfehler, sondern falsch. Listen
    bleiben aussen vor - auf einem Einkaufszettel waere "Butter." keine
    Verbesserung.
    """
    mit_zeichen = text if name in LISTEN_ZIELE else satzzeichen_setzen(text)
    if mit_zeichen != text:
        melde(f"  Satzzeichen:  {mit_zeichen!r}")
    gefasst = schreibung_richten(mit_zeichen)
    if gefasst.lower() != mit_zeichen.lower():
        melde("  ACHTUNG: Schreibhilfe hat mehr als die Schreibung geaendert")
    melde(f"  geschrieben: {gefasst!r}")
    neue = eintraege_aus(name, gefasst)
    if len(neue) > 1:
        melde(f"  in {len(neue)} Eintraege getrennt: {neue!r}")
    return neue



def diktat_fuehren(zweck, name, quelle):
    import vosk
    vosk.SetLogLevel(-1)
    # 11,6 s Ladezeit - deshalb VOR der Bereitschaftsansage laden und die
    # Wartezeit ansagen, statt den Nutzer in die Stille sprechen zu lassen.
    melde(f"=== Diktat gestartet ({zweck}, {name}), Quelle {quelle} ===")
    sprich(ANSAGE_LADEN)
    t0 = time.time()
    modell = vosk.Model(MODELL_GROSS)
    melde(f"  grosses Modell geladen in {time.time()-t0:.1f} s")
    # Der kleine Erkenner hoert NUR auf den Schlusssatz. Ohne ihn ist das
    # Diktat nur per Strg+C zu beenden - fuer einen blinden Nutzer keine
    # Bedienung.
    modell_klein = None
    if os.path.isdir(MODELL_KLEIN):
        t0 = time.time()
        modell_klein = vosk.Model(MODELL_KLEIN)
        melde(f"  kleines Modell fuer den Schlusssatz in {time.time()-t0:.1f} s")
    else:
        melde("  ACHTUNG: kleines Modell fehlt - Schluss nur mit Strg+C")

    prozess = None
    gesammelt = []
    letzte_aeusserung = time.time()
    try:
        erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE)
        schluss = (vosk.KaldiRecognizer(modell_klein, ABTASTRATE, GRAMMATIK_SCHLUSS)
                   if modell_klein else None)
        sprich(ANSAGE_BEREIT_LISTE if name in LISTEN_ZIELE else ANSAGE_BEREIT)
        prozess = aufnahme_starten(quelle)
        # Beginn der AUFNAHME, nicht der Funktion: Davor liegen rund neun
        # Sekunden Modellladezeit, in denen niemand sprechen kann.
        aufnahme_seit = time.time()
        anzahl_aeusserungen = 0
        pegel_puffer = []
        while True:
            # Zeitgrenze: Sie wird bei JEDER Aeusserung zurueckgesetzt, auch
            # bei einer, die verworfen wird - wer spricht, ist da.
            if time.time() - letzte_aeusserung > DIKTAT_ZEITGRENZE_S:
                melde(f"  Zeitgrenze: {DIKTAT_ZEITGRENZE_S:.0f} s ohne Aeusserung")
                sprich(ANSAGE_ZEITGRENZE)
                break

            block = prozess.stdout.read(4000)
            if not block:
                time.sleep(0.5)
                prozess = aufnahme_starten(quelle)
                continue
            pegel_puffer.append(pegel(block))

            # ZUERST den Schluss-Erkenner fragen. Er bekommt denselben
            # Block; wer zuerst fertig ist, ist unerheblich - entscheidend
            # ist, dass der Schlusssatz nicht erst durch die freie
            # Erkennung muss, wo er verloren geht.
            if schluss is not None and schluss.AcceptWaveform(block):
                gehoert = json.loads(schluss.Result()).get("text", "").strip()
                mittel = ((sum(pegel_puffer) / len(pegel_puffer))
                          if pegel_puffer else 0.0)
                if ist_schluss(gehoert):
                    # ZU LEISE IST KEIN SCHLUSS - ein Stoergeraeusch hat nicht den
                    # Pegel einer Stimme. Dieselbe Schwelle wie bei der freien
                    # Erkennung weiter unten.
                    if mittel < PEGEL_SCHWELLE:
                        melde(f"  Schluss {gehoert!r} verworfen - zu leise "
                              f"(Pegel {mittel:.0f} unter {PEGEL_SCHWELLE:.0f})")
                        continue
                    seit_start = time.time() - aufnahme_seit
                    if seit_start < SCHLUSS_SPERRFRIST_S:
                        # Niemand beendet drei Sekunden nach dem Start; wer
                        # diktieren will, diktiert.
                        melde(f"  Schluss {gehoert!r} nach nur {seit_start:.1f} s "
                              f"- Sperrfrist, wird verworfen")
                        continue
                    melde(f"  Schlusssatz erkannt (kleines Modell): {gehoert!r} "
                          f"nach {seit_start:.1f} s, "
                          f"{anzahl_aeusserungen} Aeusserungen, Pegel {mittel:.0f}")
                    break
                if ist_halber_schluss(gehoert):
                    # NUR DAS HALBE WORT - kein Schluss, aber der Nutzer muss es
                    # HOEREN. Wer 'beenden' sagt und nichts passiert, wiederholt
                    # dasselbe Wort, bis er aufgibt; wer den Bildschirm nicht sieht,
                    # hat keine andere Moeglichkeit, den Grund zu erfahren. Genau so
                    # ist am 2026-08-21 'Brief vorlesen' im Brieftext gelandet:
                    # Stephan hielt das Diktat fuer beendet.
                    #
                    # Nicht bei jedem Mal - die Ansage liefe sonst selbst wieder ins
                    # Mikrofon und wuerde zum Geraeusch.
                    melde(f"  {gehoert!r} ist kein Schluss - der volle Satz zaehlt "
                          f"(Pegel {mittel:.0f})")
                    # DIE ANSAGE IST WIEDER RAUS (2026-08-21, noch am selben Tag).
                    #
                    # Sie war als Hilfe gedacht: Wer 'beenden' sagt und nichts passiert,
                    # soll erfahren, warum. Gemessen entstehen diese Bruchstuecke aber im
                    # Sekundentakt aus ganz normaler Rede - die Ansage unterbrach Stephan
                    # also MITTEN IM DIKTIEREN, nach rund vier Sekunden. Sein Urteil:
                    # "Diesen Text kann ich nie zu Ende bringen."
                    #
                    # Eine Hilfe, die haeufiger stoert als sie hilft, ist keine. Sie kommt
                    # erst zurueck, wenn wir sie an eine Sprechpause binden koennen - dann
                    # trifft sie nur den Fall, fuer den sie gedacht war.
                    melde("  (kein Hinweis gesprochen - er wuerde das Diktat stoeren)")
                    continue
                if gehoert:
                    melde(f"  (Schluss-Erkenner: {gehoert!r} - kein Schluss)")
                    # DIE STILLE-UHR NUR BEI ECHTER SPRACHE ZURUECKSETZEN.
                    #
                    # Vorher stand hier ein blosses "letzte_aeusserung = time.time()":
                    # Jedes Geraeusch im Raum erzeugt beim Schluss-Erkenner ein '[unk]',
                    # und jedes davon hat die Uhr zurueckgesetzt. Damit konnte ein Diktat
                    # NIE von selbst enden - am 2026-08-21 lief eines neun Minuten weiter,
                    # hielt die Marke 'ein anderer Dienst hoert zu', und Stephan konnte die
                    # Sprachsteuerung nicht mehr starten. Der Notausgang, auf den ich ihn
                    # kurz zuvor verwiesen hatte, war also selbst defekt.
                    #
                    # Dieselbe Schwelle wie ueberall: Was zu leise fuer den Text ist, ist
                    # auch zu leise, um als Lebenszeichen zu gelten.
                    if mittel >= PEGEL_SCHWELLE:
                        letzte_aeusserung = time.time()

            if not erkenner.AcceptWaveform(block):
                continue
            text = json.loads(erkenner.Result()).get("text", "").strip()
            mittel = ((sum(pegel_puffer) / len(pegel_puffer))
                      if pegel_puffer else 0.0)
            pegel_puffer = []
            if not text:
                continue
            if mittel < PEGEL_SCHWELLE:
                # Protokolliert und nicht stillschweigend verworfen: Faellt hier
                # echte Sprache hinein, sieht man es sofort - und die Schwelle
                # gehoert dann nach unten.
                melde(f"  verworfen, zu leise (Pegel {mittel:.0f}): {text!r}")
                continue
            letzte_aeusserung = time.time()
            anzahl_aeusserungen += 1
            melde(f"  erkannt:     {text!r}")
            if text == SCHLUSSSATZ:
                # Kommt praktisch nie vor - die freie Erkennung trifft den
                # Satz nicht (siehe Kopf). Bleibt als Rueckfallebene, falls
                # das kleine Modell fehlt.
                melde("  -> Schlusssatz in der freien Erkennung, Diktat endet")
                break
            gesammelt += aeusserung_verarbeiten(name, text)
    except KeyboardInterrupt:
        pass
    finally:
        if prozess:
            try:
                prozess.terminate()
            except Exception:
                pass

    # DER REST IM ERKENNER - gefunden am 2026-08-21 durch Stephans Test.
    #
    # Vosk sammelt Audio und liefert erst an einer Sprechpause ab. Wer den
    # Brief in einem Zug spricht und dann "Diktat beenden" sagt, hat beides in
    # DERSELBEN Pause: Der Schluss-Erkenner bricht die Schleife ab, bevor die
    # freie Erkennung ihren angesammelten Text abliefern konnte - und der war
    # damit weg. Im Protokoll stand '0 Aeusserungen', obwohl ein ganzer Brief
    # gesprochen worden war.
    #
    # DER FEHLER WAR VON ANFANG AN DA und ist nur nie aufgefallen: Beim
    # Einkaufszettel macht man zwischen den Waren Pausen, jede Ware wird fuer
    # sich abgeschlossen, und was nach der letzten Pause kam, war meist nichts.
    #
    # Die Schlussworte muessen weg: Die freie Erkennung hoert "diktat beenden"
    # mit, und es gehoert nicht in den Brief.
    rest = ""
    try:
        rest = json.loads(erkenner.FinalResult()).get("text", "").strip()
    except Exception as fehler:
        melde(f"  Resttext nicht lesbar: {fehler}")
    if rest:
        worte = rest.split()
        while worte and worte[-1] in SCHLUSS_WOERTER:
            worte.pop()
        rest = " ".join(worte).strip()
    if rest:
        melde(f"  Resttext aus dem Erkenner: {rest!r}")
        gesammelt += aeusserung_verarbeiten(name, rest)
    
    if not gesammelt:
        sprich(ANSAGE_LEER)
        return 0

    pfad = (brief_schreiben(gesammelt) if name in BRIEF_ZIELE
            else notiz_schreiben(name, gesammelt))
    melde(f"  geschrieben nach {pfad}")
    sprich(ansage_ende(name, len(gesammelt)))
    # KEIN Vorlesen mehr an dieser Stelle (Stephan, 2026-08-19) - siehe
    # VORLESEN_HINWEIS oben. Das Vorlesen mit Satzzeichen lebt unveraendert in
    # dialos-notiz.py weiter, wo es auf Ansage geschieht; die dort gemessene
    # Begruendung (3,670 s ohne gegen 4,884 s mit Satzzeichen, der Unterschied
    # besteht ausschliesslich aus Pausen) gilt weiter und steht in
    # docs/diktat.md.
    return 0


if __name__ == "__main__":
    sys.exit(main())
