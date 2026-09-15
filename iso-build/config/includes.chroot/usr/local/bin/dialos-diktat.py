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
import collections
import json
import math
import os
import re
import subprocess
import sys
import textwrap
import threading
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
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-diktat.log")

# Der Satz, der das Diktat beendet. Er wird NUR erkannt, wenn er die
# gesamte Aeusserung ist - sonst koennte man ihn in einem Brief nicht
# erwaehnen, ohne das Diktat abzubrechen.
SCHLUSSSATZ = "diktat beenden"
# ensure_ascii=False IST PFLICHT (Fehler gefunden 2026-09-14). Ohne das schreibt
# json.dumps ein "ö" als "\\u00f6", Vosk liest das woertlich und meldet
# "Ignoring word missing in vocabulary" - fuer JEDES Wort mit Umlaut oder ß.
# Genau daraus entstanden die Befunde "spaeter", "loeschen", "zuruecksetzen"
# und "aufraeumen fehlen im Wortschatz". Sie fehlen nicht.
#
# "SATZ LOESCHEN" UND "SATZ WIEDERHOLEN" (Stephan, 2026-09-15: "wie bauen wir
# 'Versprecher' ein, also das die Sprachsteuerung weiss, das ich einen Satz neu
# einsprechen muss"). Sie laufen ueber denselben kleinen Erkenner wie der
# Schluss. Gegen Piper geprueft: Beide werden mit Anna und Michael erkannt -
# aber auch aus normalem Text: "Ich bitte Sie, mir diesen Betrag zu erstatten.
# Die Rechnung liegt ..." ergab ein zusammenhaengendes "satz wiederholen", "Den
# ersten Satz habe ich geloescht" ein "satz loeschen". Getrennt hat sie die
# Stille: Beim echten Befehl war es 0,5 s davor und danach still (Spitze 24 und
# 1), bei beiden Fehlausloesern laut (32653/22769 und 27990/22874). Deshalb
# gelten die Befehle nur mit Ruhe davor UND danach - siehe BEFEHL_*.
BEFEHL_LOESCHEN = "satz löschen"
BEFEHL_WIEDERHOLEN = "satz wiederholen"
GRAMMATIK_SCHLUSS = json.dumps([SCHLUSSSATZ, BEFEHL_LOESCHEN, BEFEHL_WIEDERHOLEN, "[unk]"],
                               ensure_ascii=False)
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


# SPRECHPAUSE VOR DEM SCHLUSS (2026-08-22).
#
# WARUM ES DIESE REGEL BRAUCHT: Der Schluss-Erkenner arbeitet mit einer
# eingeschraenkten Grammatik und MUSS deshalb jedes Stueck Ton auf eine seiner
# Phrasen abbilden. Gemessen mit Piper an 30 s zusammenhaengendem Brieftext:
#
#     bei  4,8 s  'diktat'
#     bei  8,4 s  'beenden'
#     bei 12,2 s  'diktat [unk] beenden'
#     bei 15,1 s  'beenden'
#
# Bruchstuecke im Sekundentakt, aus ganz normaler Rede. Vier Reparaturen haben
# das nicht dicht bekommen - Sperrfrist, Pegel-Tor, beide Woerter verlangen,
# Ansage. Am 2026-08-21 brach Stephans Diktat nach 12,1 s mitten im Satz ab,
# sein Urteil: "Diesen Text kann ich nie zu Ende bringen."
#
# DER UNTERSCHIED, DEN ES WIRKLICH GIBT: Ein echtes "Diktat beenden" kommt,
# NACHDEM der Nutzer mit dem Text fertig ist - davor liegt eine Pause. Jedes
# Bruchstueck entsteht mitten im Redefluss, wo es keine gibt. Genau das
# schuetzt den Einkaufszettel seit jeher, ohne dass es jemand geplant haette:
# "Milch." Pause. "Butter." Pause.
#
# DIE REGEL: In den letzten RUHE_FENSTER_S Sekunden muss es eine
# zusammenhaengende Ruhephase von mindestens RUHE_MINDESTENS_S gegeben haben.
RUHE_FENSTER_S = 5.0
RUHE_MINDESTENS_S = 0.4

# Wie lange ein Block dauert: 4000 Bytes, 16 Bit, mono, 16 kHz.
BLOCK_S = 4000 / 2 / 16000.0


def pause_davor(verlauf, fenster_s=RUHE_FENSTER_S,
                mindestens_s=RUHE_MINDESTENS_S, schwelle=PEGEL_SCHWELLE):
    """Lag in den letzten Sekunden eine Sprechpause?

    "verlauf" ist eine Folge von Pegeln, aeltester zuerst, je Block einer.
    Geprueft wird nur das letzte Fenster; alles davor ist fuer die Frage
    "kam der Satz nach einer Pause" ohne Bedeutung.

    Reine Funktion ohne Uhr und ohne Mikrofon - damit ist sie gegen
    aufgezeichnete Faelle pruefbar, und genau das ist am 2026-08-22 passiert,
    bevor Stephan wieder testen musste.
    """
    bloecke_fenster = max(1, int(fenster_s / BLOCK_S))
    noetig = max(1, int(mindestens_s / BLOCK_S))
    lauf = 0
    for pegel in list(verlauf)[-bloecke_fenster:]:
        if pegel < schwelle:
            lauf += 1
            if lauf >= noetig:
                return True
        else:
            lauf = 0
    return False


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

    SEIT 2026-09-14 NUR NOCH GENAU "diktat beenden" - zwei Woerter, in dieser
    Reihenfolge. Vorher genuegten beide Woerter plus beliebig viele weitere
    Schlusswoerter. Bei der dritten Probe des Tages beendete sich ein
    Einkaufszettel nach "Rote Aepfel" von selbst: Das kleine Modell hoerte in
    "Bananen" ein "diktat beenden beenden", und die Ware war verloren. Stephan:
    "nach einem Eintrag brach der Einkaufszettel ab". Die Auszaehlung aller
    Protokolle bis dahin:

        genau 'diktat beenden'          14 x, soweit nachvollziehbar echt
        'diktat beenden beenden'         2 x, einmal nachweislich falsch
        'beenden diktat beenden'         1 x, nach 10 s ohne ein Wort - verdaechtig

    Der Preis: Kommt ein echtes Ende einmal als drei Woerter an, muss der
    Nutzer den Satz wiederholen. Das kostet einen Satz; ein falsches Ende
    kostet, was er als Naechstes diktiert.
    """
    return gehoert.split() == SCHLUSSSATZ.split()


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
ARCHIV_SKRIPT = "/usr/local/bin/dialos-archiv.py"

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


# WARUM IN EINEM VERSTECKTEN ORDNER (Stephan, 2026-08-22): Vorher lagen die
# Protokolle offen im Heimatverzeichnis - zehn laufende und fuenfzehn gedrehte
# Fassungen, also 25 Dateien zwischen "Notizen", "Dokumente" und "Bilder". Der
# Nutzer sieht sie nicht, aber ein sehender Helfer sucht dazwischen. In "~/.log"
# stoeren sie niemanden und sind trotzdem da, wo man sie vermutet.
#
# Der Ordner wird beim Schreiben angelegt, nicht vorausgesetzt: Ein neues Konto
# hat ihn noch nicht, und ein fehlendes Protokoll darf keine Ansage aufhalten.
def melde(text):
    if DEBUG:
        print(text, flush=True)
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
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
    # So hoerte das grosse Modell "komma setzen" in der Brief-Probe vom
    # 2026-09-15 - im Text stand "Kommas Setzen".
    ("kommas setzen", ","),
]
# Erstes Wort -> zweites Wort, fuer Satzzeichen ueber eine Stueckgrenze
# (Aeusserungen.hinzu).
SATZZEICHEN_FORTSETZUNG = {w.split()[0]: w.split()[1] for w, _ in SATZZEICHEN}


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
    # NUR LEERZEICHEN ABSCHNEIDEN, KEINE ZEILENUMBRUECHE (Fehler vom
    # 2026-09-15, Stephans erster ganzer Brief). Hier stand "text.strip()" -
    # das entfernte auch das "\n\n", das ein "neuer absatz" am ENDE einer
    # Aeusserung gerade gesetzt hatte. Im Protokoll: erkannt '... bezahlt punkt
    # setzen neuer absatz', daraus '... bezahlt.' - und im Brief lief der
    # naechste Absatz ohne Leerzeile weiter. Mitten in einer Aeusserung ("Herren
    # komma setzen neuer absatz am zwoelften") ging es, deshalb fiel es nie auf.
    return text.strip(" ")


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
    # GROSS NACH SATZENDE UND ZEILENWECHSEL (2026-09-15): Im Brief stand
    # "\n\nmit freundlichen Gruessen" - LanguageTool macht Satzanfaenge nur
    # hinter einem Punkt gross, nicht hinter einem gesprochenen "neuer absatz".
    # Punkte kommen im Diktat nur aus "punkt setzen", Abkuerzungen gibt es nicht.
    neu = re.sub(r"([.?!][ \n]+|\n\s*)([a-zäöü])", lambda m: m.group(1) + m.group(2).upper(), neu)
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


# "--latency-msec=30" (2026-09-14): Ohne die Angabe puffert parec rund ZWEI
# SEKUNDEN, bevor der erste Block ankommt - gemessen 2,03 s gegen 0,10 s mit
# 30 ms. Verloren geht dabei nichts, aber jede Reaktion kommt zwei Sekunden zu
# spaet, und ein Zeitfenster, das beim Start des Prozesses zu zaehlen beginnt,
# ist in Wahrheit zwei Sekunden kuerzer.
def aufnahme_starten(quelle):
    return subprocess.Popen(
        ["parec", "-d", quelle, "--format=s16le",
         f"--rate={ABTASTRATE}", "--channels=1", "--latency-msec=30"],
        stdout=subprocess.PIPE)


# DIE AUFNAHME LAEUFT SCHON WAEHREND "ICH SCHREIBE MIT" (2026-09-14).
#
# Vorher startete parec erst NACH der Ansage. Wer direkt losdiktierte, verlor
# den Wortanfang - Stephans erste Ware "Bananen" kam als "erahnen" an. Jetzt
# wird waehrend der Ansage mitgelesen und verworfen; ausgewertet wird ab
# VORLAUF_S vor ihrem Ende, also noch in der Stille hinter der letzten Silbe.
# Dieselbe Loesung wie bei der Rueckfrage in dialos-notiz.py.
VORLAUF_S = 0.3

# SPIELRAUM BEIM ABSCHNEIDEN DES SCHLUSSSATZES (2026-09-14). Mit genau dem
# Beginn laut kleinem Modell blieb beim ersten echten Test "Den" stehen: Das
# grosse Modell laesst den Satz offenbar etwas frueher beginnen. 0,35 s frueher
# schneiden kostet nichts Echtes - vor dem Schlusssatz verlangt pause_davor()
# ohnehin eine Sprechpause, ein echtes letztes Wort endet also nicht
# unmittelbar davor. Die Zeiten stehen im Protokoll; der Wert ist vorlaeufig.
SCHLUSS_SPIELRAUM_S = 0.35

# Wie lang "Diktat beenden" hoechstens dauert. Liegen die letzten zwei
# Schlusswoerter weiter auseinander, gehoert das vordere nicht zum Satz.
SCHLUSS_HOECHSTENS_S = 2.0

# DIE BEIDEN SCHLUSSWOERTER MUESSEN UNMITTELBAR AUFEINANDER FOLGEN (Fehler vom
# 2026-09-15, Stephans erster ganzer Brief). Mitten im Satz "Ueber eine Antwort
# bis Ende des Monats" hoerte das kleine Modell "diktat" (37,92-38,31 s) und in
# "bis Ende" ein "beenden" (39,55-40,19 s) - genau zwei Woerter, in der richtigen
# Reihenfolge, nach einer Sprechpause. Die Regel "genau diktat beenden" liess es
# durch, das Diktat endete, und Stephan "konnte den letzten Absatz nicht mehr
# einsprechen". Zwischen den Woertern lagen 1,24 s. Beim echten Schluss vom
# 2026-09-14 lagen sie direkt aneinander (8,61 -> 8,61 s). 0,6 s laesst Raum
# fuer ein langsames "Diktat - beenden".
SCHLUSS_LUECKE_MAX_S = 0.6

# Ruhe vor und nach "Satz loeschen"/"Satz wiederholen" (Messung bei
# GRAMMATIK_SCHLUSS). Davor 0,4 s wie beim Schluss (RUHE_MINDESTENS_S), danach
# 0,5 s - wer einen Befehl gibt, wartet auf die Antwort.
BEFEHL_RUHE_DAVOR_S = 0.4
BEFEHL_RUHE_DANACH_S = 0.5
# Woerter der freien Erkennung, die nach diesem Zeitpunkt vor dem Befehl ENDEN,
# gehoeren zum Befehl (bis 2026-09-15: die danach BEGINNEN - siehe Aufruf).
BEFEHL_SPIELRAUM_S = 0.35
# ABSTAND ZU DEN WORTMARKEN beim Pruefen der Ruhe. Offline gefunden, bevor
# Stephan testen musste: Vosk setzte das Ende von "loeschen" auf 4,23 s, das
# Wort klang aber bis 4,25 s aus - in den Block ab 4,125 s (Pegel 2615). Ohne
# Abstand galt der echte Befehl als "danach nicht still".
BEFEHL_RAND_S = 0.15
# VOR DEM BEFEHL ETWAS MEHR ABSTAND (2026-09-15). Das kleine Modell setzt den
# Wortanfang spaeter als der Ton beginnt: offline "satz" bei 9,03 s, laut ab
# 8,875 s - mit 0,15 s lag der Tonbeginn im Ruhefenster, und der Befehl galt als
# "davor nicht still". Am Geraet wurde so vermutlich Stephans erstes "Satz
# wiederholen" nach fuenf Sekunden Pause verworfen. Seit der Gegenprobe mit der
# freien Erkennung ist dieser Abstand vertretbar.
BEFEHL_RAND_DAVOR_S = 0.25


def ruhig(verlauf, von_s, bis_s):
    """War es im Zeitraum [von_s, bis_s) still? verlauf = Pegel je Block ab 0 s."""
    a = max(0, int(von_s / BLOCK_S))
    b = max(a + 1, int(math.ceil(bis_s / BLOCK_S)))
    stueck = verlauf[a:b]
    return bool(stueck) and max(stueck) < PEGEL_SCHWELLE


class Aeusserungen:
    """Das Diktat als Folge von Aeusserungen - damit sich die letzte streichen laesst.

    Jede Aeusserung behaelt ihre Woerter mit Zeitmarken (je Erkenner-Durchgang,
    "epoche") und die Eintraege, die daraus geworden sind. Vorher war das Diktat
    nur eine flache Liste von Eintraegen; welcher Eintrag zu welcher Aeusserung
    gehoerte - bei Listen koennen es mehrere sein -, war nicht mehr zu sagen.
    """

    def __init__(self, name):
        self.name = name
        self.liste = []          # dicts: epoche, worte, eintraege

    def hinzu(self, epoche, worte, text=None):
        text = text if text is not None else " ".join(w["word"] for w in worte)
        if not text.strip():
            return []
        # EIN GESPROCHENES SATZZEICHEN UEBER DIE STUECKGRENZE (2026-09-15,
        # zweite Brief-Probe). Vosk schneidet lange Rede auch ohne Pause - einmal
        # genau zwischen "kommas" und "setzen". Das eine Stueck endete auf
        # "Kommas", das naechste begann mit "Setzen", und beide standen so im
        # Brief. Beginnt ein Stueck mit dem zweiten Wort eines Satzzeichens und
        # endete das vorige mit dem ersten, wird beides zusammen neu verarbeitet.
        vorher = self.liste[-1] if self.liste else None
        erstes = text.split()[0].lower()
        if (vorher and self.name not in LISTEN_ZIELE and vorher["epoche"] == epoche
                and vorher.get("text")
                and SATZZEICHEN_FORTSETZUNG.get(vorher["text"].split()[-1].lower()) == erstes):
            self.liste.pop()
            melde(f"  Satzzeichen ueber die Stueckgrenze - mit dem vorigen Stueck "
                  f"zusammengefasst: {vorher['text'].split()[-1]!r} + {erstes!r}")
            text = vorher["text"] + " " + text
            worte = list(vorher["worte"]) + list(worte)
        eintraege = aeusserung_verarbeiten(self.name, text)
        self.liste.append({"epoche": epoche, "worte": list(worte), "eintraege": eintraege,
                           "text": text})
        return eintraege

    def ab_zeit_entfernen(self, epoche, ab_s, nach_ende=False):
        """Entfernt alle Woerter dieser Epoche, die ab ab_s beginnen (Befehlswoerter).

        nach_ende: stattdessen alle, die nach ab_s ENDEN - siehe BEFEHL_RAND_S
        am Aufruf fuer "Satz loeschen"/"Satz wiederholen".
        """
        while self.liste and self.liste[-1]["epoche"] == epoche and self.liste[-1]["worte"]:
            letzte = self.liste[-1]
            if nach_ende:
                bleiben = [w for w in letzte["worte"]
                           if w.get("end", w.get("start", 0)) <= ab_s]
            else:
                bleiben = [w for w in letzte["worte"] if w.get("start", 0) < ab_s]
            if len(bleiben) == len(letzte["worte"]):
                return
            self.liste.pop()
            if bleiben:
                melde(f"  Befehlswoerter aus der Aeusserung entfernt, bleibt: "
                      f"{' '.join(w['word'] for w in bleiben)!r}")
                self.hinzu(epoche, bleiben)
                return
            melde("  Aeusserung bestand nur aus Befehlswoertern - entfernt")

    # EIN SATZ IST EIN SATZ, KEIN STUECK DER ERKENNUNG (2026-09-15, Stephans
    # Brief mit Versprecher). Zuerst strichen die Befehle die letzte
    # AEUSSERUNG - das, was Vosk an einer Sprechpause abliefert. Das passt nicht
    # zu Saetzen: "punkt setzen" kam als eigenes Stueck (gestrichen waere nur
    # der Punkt), und von "Ich bitte Sie" bis "waere ich dankbar" kam EIN Stueck
    # mit 60 Woertern (gestrichen waeren drei Saetze). Jetzt gilt: der Text seit
    # dem vorletzten Satzende - Punkt, Frage-, Ausrufezeichen oder Zeilenwechsel.
    # Ist der letzte Satz noch nicht beendet, ist er es selbst. Auf einer Liste
    # ist der "Satz" die letzte Ware.
    SATZ_ENDE = ".?!\n"

    def _flach(self):
        """(Aeusserung, Eintrag, Anfang im Gesamttext) und der Gesamttext."""
        teile, text = [], ""
        for i, a in enumerate(self.liste):
            for j, e in enumerate(a["eintraege"]):
                if text and not text.endswith((" ", "\n")) and not e.startswith(
                        (" ", "\n") + tuple(",.?!:;")):
                    text += " "
                teile.append((i, j, len(text)))
                text += e
        return teile, text

    # HOECHSTENS DAS LETZTE GESPROCHENE STUECK (2026-09-15, offline gefunden).
    # Hatte der Erkenner Punkt und Absatz nicht verstanden ("neue Apps",
    # "Umsetzen"), gab es kein Satzende, und "Satz loeschen" strich bis zum
    # Textanfang - samt Anrede. Zu wenig gestrichen holt ein zweites "Satz
    # loeschen" nach, zu viel holt nichts zurueck. Stuecke nur aus Satzzeichen
    # zaehlen nicht mit: "Am zwoelften ... Meier" / "." ist ein Stueck.
    #
    # EINS, NICHT ZWEI: Mit zwei Stuecken strich der naechste Offline-Lauf
    # wieder die Anrede mit, weil dort "komma setzen neuer absatz" als "komma neue
    # apps" ankam. Der Preis: "Ich bitte Sie" / "," / "mir diesen Betrag" / "."
    # braucht zweimal "Satz loeschen".
    STUECKE_HOECHSTENS = 1

    def _satz_anfang(self, text, teile):
        rest = text.rstrip()
        if rest and rest[-1] in ".?!":
            rest = rest[:-1]
        satzende = max(rest.rfind(z) for z in self.SATZ_ENDE) + 1
        anfaenge = []
        for i, a in enumerate(self.liste):
            if any(re.search(r"\w", e) for e in a["eintraege"]):
                anfaenge.append(min(p for k, _, p in teile if k == i))
        grenze = anfaenge[-self.STUECKE_HOECHSTENS] if len(anfaenge) >= self.STUECKE_HOECHSTENS else 0
        return max(satzende, grenze)

    def worte_nach(self, epoche, ab_s):
        """Woerter dieser Epoche, die nach ab_s enden (fuer die Gegenprobe)."""
        worte = []
        for a in reversed(self.liste):
            if a["epoche"] != epoche:
                break
            spaeter = [w for w in a["worte"] if w.get("end", w.get("start", 0)) > ab_s]
            if not spaeter:
                break
            worte = spaeter + worte
        return worte

    def befehlsrest_entfernen(self):
        """Streicht den Rest eines gescheiterten Befehlsversuchs am Textende.

        Am 2026-09-15 kam "Satz loeschen" zweimal: Der erste Versuch ging
        unter (das kleine Modell hoerte "satz satz loeschen") und stand als
        "Pause Satz loeschen" im Text; der zweite wurde erkannt - und strich
        genau diesen Rest statt des Versprechers. Bei "Satz wiederholen" las
        Anna "Absatz sagt wiederholen" vor. Erkannt wird ein Rest am letzten
        Wort (loeschen/wiederholen) UND einem "satz" in den zwei Woertern davor;
        "die Daten loeschen" bleibt also stehen.
        """
        entfernt = []
        while self.liste:
            a = self.liste[-1]
            if not a["eintraege"]:
                self.liste.pop()
                continue
            e = a["eintraege"][-1]
            worte = list(re.finditer(r"\S+", e))
            klein = [re.sub(r"[^\wäöüß]", "", w.group().lower()) for w in worte]
            if not klein or klein[-1] not in ("löschen", "wiederholen"):
                break
            ab = next((k for k in range(len(klein) - 2, max(-1, len(klein) - 4), -1)
                       if "satz" in klein[k]), None)
            if ab is None:
                break
            # EIN EINZELNES WORT DAVOR GEHOERT ZUM VERSUCH ("Also, Satz
            # loeschen"). Offline gefunden: Aus "Pause Satz loeschen" blieb
            # "Hause" stehen, und der naechste Befehl strich nur dieses Wort
            # statt des Versprechers davor. Nicht auf Listen - dort kann das
            # eine Wort eine Ware sein ("Bananen, Satz loeschen").
            if ab == 1 and self.name not in LISTEN_ZIELE:
                ab = 0
            entfernt.append(e[worte[ab].start():].strip())
            e = e[:worte[ab].start()].rstrip(" ")
            if e.strip():
                a["eintraege"][-1] = e
                break
            a["eintraege"].pop()
        if entfernt:
            melde(f"  Rest eines Befehlsversuchs entfernt: {entfernt!r}")

    def satz_entfernen(self):
        """Streicht den letzten Satz (Liste: die letzte Ware); gibt ihn zurueck."""
        while self.liste and not self.liste[-1]["eintraege"]:
            self.liste.pop()
        if not self.liste:
            return ""
        if self.name in LISTEN_ZIELE:
            weg = self.liste[-1]["eintraege"].pop()
            return weg.strip()
        teile, text = self._flach()
        schnitt = self._satz_anfang(text, teile)
        for i, j, anfang in reversed(teile):
            e = self.liste[i]["eintraege"][j]
            if anfang >= schnitt:
                self.liste[i]["eintraege"].pop(j)
            elif anfang + len(e) > schnitt:
                vorne = e[:schnitt - anfang].rstrip(" ")
                if vorne:
                    self.liste[i]["eintraege"][j] = vorne
                else:
                    self.liste[i]["eintraege"].pop(j)
        self.liste = [a for a in self.liste if a["eintraege"]]
        return text[schnitt:].strip()

    def satz(self):
        """Der letzte Satz (Liste: die letzte Ware), ohne etwas zu streichen."""
        eintraege = self.eintraege()
        if not eintraege:
            return ""
        if self.name in LISTEN_ZIELE:
            return eintraege[-1].strip()
        teile, text = self._flach()
        return text[self._satz_anfang(text, teile):].strip()

    def eintraege(self):
        return [e for a in self.liste for e in a["eintraege"]]


def zusammenziehen(eintraege):
    """Haengt Eintraege, die mit einem Satzzeichen beginnen, an den vorigen.

    Kam "punkt setzen" als eigene Aeusserung, stand im Brief "Mueller ." -
    brief_schreiben verbindet die Eintraege mit Leerzeichen (2026-09-15).
    """
    ergebnis = []
    for e in eintraege:
        if ergebnis and e[:1] in ",.?!:;":
            ergebnis[-1] = ergebnis[-1].rstrip(" ") + e
        elif e.strip() or "\n" in e:
            ergebnis.append(e)
    return ergebnis


def zum_vorlesen(text):
    text = " ".join(text.split())
    return text if len(text) <= 300 else text[:300].rsplit(" ", 1)[0] + " ..."


def schluss_luecke(worte):
    """Luecke zwischen "diktat" und "beenden" in Sekunden, oder None."""
    if len(worte) != 2 or worte[0].get("end") is None or worte[1].get("start") is None:
        return None
    return worte[1]["start"] - worte[0]["end"]


def schluss_beginn_aus(worte):
    """Wo "Diktat beenden" beginnt - aus den Woertern des kleinen Erkenners.

    MASSGEBLICH SIND DIE LETZTEN ZWEI WOERTER, nicht das erste (Fehler vom
    2026-09-14, dritte Probe). Das kleine Modell kennt nur den Schlusssatz und
    presst alles in dessen Woerter. Aus "Rote Aepfel. Bananen. Diktat beenden."
    wurde "diktat beenden beenden" - das erste "diktat" bei 1,14 s lag mitten in
    "Rote Aepfel". Mit dem ersten Wort als Beginn wurde "Bananen" (3,75 s)
    abgeschnitten, und die Ware war weg. Der Schlusssatz steht aber immer am
    ENDE; seine zwei Woerter sind die letzten zwei.
    """
    if not worte:
        return None
    ende = worte[-1].get("end")
    kandidat = worte[-2] if len(worte) >= 2 else worte[-1]
    beginn = kandidat.get("start")
    if beginn is None or ende is None:
        return None
    if ende - beginn > SCHLUSS_HOECHSTENS_S:
        beginn = worte[-1].get("start", beginn)
    return beginn


def rest_kuerzen(worte, schluss_beginn):
    """Behaelt die Woerter des Rests, die deutlich VOR dem Schlusssatz BEGINNEN.

    Nach dem Beginn und nicht nach dem Ende: Ein echtes letztes Wort beginnt
    lange vor dem Schlusssatz - es hat seine eigene Dauer, und pause_davor()
    verlangt danach noch eine Sprechpause. Ein Bruchstueck des Schlusssatzes
    wie "Den" beginnt dagegen unmittelbar davor oder mittendrin.
    """
    grenze = schluss_beginn - SCHLUSS_SPIELRAUM_S
    return [w["word"] for w in worte if w.get("start", 0) < grenze], grenze


def sprechen_bei_offener_aufnahme(text, prozess):
    """Spricht und liest dabei mit. Gibt die letzten VORLAUF_S zurueck."""
    fertig = threading.Event()

    def ansage():
        try:
            sprich(text)
        finally:
            fertig.set()

    threading.Thread(target=ansage, daemon=True).start()
    zuletzt = collections.deque()
    while not fertig.is_set():
        block = prozess.stdout.read(800)
        if not block:
            break
        jetzt = time.time()
        zuletzt.append((jetzt, block))
        while zuletzt and zuletzt[0][0] < jetzt - 2.0:
            zuletzt.popleft()
    fertig.wait()
    grenze = time.time() - VORLAUF_S
    return b"".join(b for t, b in zuletzt if t >= grenze)


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
    # strip() statt rstrip(): Seit Absaetze am Aeusserungsende erhalten bleiben
    # (2026-09-15), kann auch der Anfang mit einem Absatz beginnen - eine
    # Leerzeile vor der Anrede waere falsch.
    #
    # EINZELNE ZEILEN BLEIBEN ERHALTEN (2026-09-15): Ein "\n" im Text kommt nur
    # noch von einem gesprochenen "neue zeile" (siehe brief_schreiben) und wird
    # nicht mehr zusammengezogen - umgebrochen wird je Zeile.
    for absatz in text.strip().split("\n\n"):
        zeilen = [" ".join(z.split()) for z in absatz.split("\n")]
        zeilen = [z for z in zeilen if z]
        absaetze.append("\n".join(textwrap.fill(z, breite) for z in zeilen))
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
        # MIT LEERZEICHEN VERBINDEN, NICHT MIT ZEILENUMBRUCH (2026-09-15). Jede
        # Aeusserung ist ein Stueck desselben Fliesstexts. Mit "\n" verbunden
        # konnte der Briefbogen einen Stueck-Uebergang nicht von einem
        # gesprochenen "neue zeile" unterscheiden - und zog beide zusammen: "Mit
        # freundlichen Gruessen neue zeile Stephan Roesner" stand in einer Zeile.
        f.write(briefbogen(" ".join(zeilen)))

    # JEDER BRIEF WANDERT ALS PDF INS ARCHIV (Stephans Vorgabe vom
    # 2026-08-21). Nicht abwarten und nicht daran scheitern: Der Brief ist als
    # Textdatei bereits geschrieben - ein fehlgeschlagenes Archiv darf ihn
    # nicht mitreissen. Was schiefging, steht in dialos-archiv.log.
    if os.access(ARCHIV_SKRIPT, os.X_OK):
        try:
            subprocess.Popen([ARCHIV_SKRIPT, "ablegen", pfad, "--art", "brief"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
            melde("  ins Archiv gegeben")
        except Exception as fehler:
            melde(f"  Archiv nicht aufrufbar: {fehler}")
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
    aeusserungen = Aeusserungen(name)
    letzte_aeusserung = time.time()
    # Wo der Schlusssatz in der Aufnahme BEGINNT, in Sekunden. Beide Erkenner
    # bekommen dieselben Bloecke vom selben Anfang an, ihre Zeitmarken sind
    # also vergleichbar (gemessen 2026-09-14: "beenden" bei beiden 2,64-3,15 s).
    schluss_beginn = None
    try:
        erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE)
        schluss = (vosk.KaldiRecognizer(modell_klein, ABTASTRATE, GRAMMATIK_SCHLUSS)
                   if modell_klein else None)
        # Zeitmarken je Wort - fuer das Abschneiden des Schlusssatzes am Ende,
        # siehe schluss_beginn.
        erkenner.SetWords(True)
        if schluss is not None:
            schluss.SetWords(True)
        prozess = aufnahme_starten(quelle)
        vorrat = sprechen_bei_offener_aufnahme(
            ANSAGE_BEREIT_LISTE if name in LISTEN_ZIELE else ANSAGE_BEREIT, prozess)
        # Beginn der AUFNAHME, nicht der Funktion: Davor liegen rund neun
        # Sekunden Modellladezeit, in denen niemand sprechen kann.
        aufnahme_seit = time.time()
        anzahl_aeusserungen = 0
        pegel_puffer = []
        # Der VERLAUF wird nie zurueckgesetzt - anders als pegel_puffer, der zu
        # jeder Aeusserung gehoert. Er beantwortet eine andere Frage: War es
        # kurz vorher still?
        pegel_verlauf = collections.deque(maxlen=int(RUHE_FENSTER_S / BLOCK_S) + 8)
        # Pegel je Block ab dem Start des aktuellen Erkenner-Paars - fuer die
        # Ruhe vor und nach einem Befehl, gemessen an den Wort-Zeitmarken.
        # Nach jedem Befehl beginnen beide Erkenner neu, dann auch dieser Verlauf.
        zeitverlauf = []
        epoche = 0
        befehl_offen = None
        while True:
            # Zeitgrenze: Sie wird bei JEDER Aeusserung zurueckgesetzt, auch
            # bei einer, die verworfen wird - wer spricht, ist da.
            if time.time() - letzte_aeusserung > DIKTAT_ZEITGRENZE_S:
                melde(f"  Zeitgrenze: {DIKTAT_ZEITGRENZE_S:.0f} s ohne Aeusserung")
                sprich(ANSAGE_ZEITGRENZE)
                break

            if vorrat:
                block, vorrat = vorrat[:4000], vorrat[4000:]
            else:
                block = prozess.stdout.read(4000)
            if not block:
                time.sleep(0.5)
                prozess = aufnahme_starten(quelle)
                continue
            pegel_puffer.append(pegel(block))
            pegel_verlauf.append(pegel_puffer[-1])
            zeitverlauf.append(pegel_puffer[-1])

            # EIN BEFEHL WARTET AUF SEINE RUHE DANACH. Erst wenn die halbe
            # Sekunde nach dem letzten Befehlswort aufgenommen ist, wird
            # entschieden - bis dahin laeuft alles normal weiter, nichts geht
            # verloren.
            if (befehl_offen and len(zeitverlauf) * BLOCK_S
                    >= befehl_offen["ende"] + BEFEHL_RAND_S + BEFEHL_RUHE_DANACH_S):
                b, befehl_offen = befehl_offen, None
                if not ruhig(zeitverlauf, b["ende"] + BEFEHL_RAND_S,
                             b["ende"] + BEFEHL_RAND_S + BEFEHL_RUHE_DANACH_S):
                    # Mit Pegeln (2026-09-15): Stephans echtes "Diktat beenden" wurde
                    # so verworfen - beendet hat nur die Rueckfallebene der freien
                    # Erkennung. Ohne Zahlen ist nicht zu sagen, ob das Wortende zu
                    # frueh gesetzt war oder danach wirklich etwas laut war.
                    a_i = max(0, int(b["ende"] / BLOCK_S) - 1)
                    b_i = int(math.ceil((b["ende"] + BEFEHL_RAND_S + BEFEHL_RUHE_DANACH_S) / BLOCK_S)) + 1
                    melde(f"  {b['satz']!r} verworfen - danach nicht still (Fliesstext) "
                          f"(Ende {b['ende']:.2f} s, Pegel ab {a_i * BLOCK_S:.2f} s: "
                          f"{[round(x) for x in zeitverlauf[a_i:b_i]]})")
                elif b["satz"] == SCHLUSSSATZ:
                    melde(f"  Schlusssatz erkannt (kleines Modell): {b['gehoert']!r} "
                          f"nach {b['seit_start']:.1f} s, "
                          f"{anzahl_aeusserungen} Aeusserungen, Pegel {b['mittel']:.0f}")
                    schluss_beginn = schluss_beginn_aus(b["worte"])
                    if schluss_beginn is not None:
                        aeusserungen.ab_zeit_entfernen(epoche, schluss_beginn - SCHLUSS_SPIELRAUM_S)
                    melde("  Schlusssatz mit Zeiten: " + ", ".join(
                        f"{w.get('word')} {w.get('start', 0):.2f}-{w.get('end', 0):.2f}"
                        for w in b["worte"])
                          + (f" | Beginn {schluss_beginn:.2f}" if schluss_beginn is not None else ""))
                    break
                else:
                    try:
                        rest = json.loads(erkenner.FinalResult())
                        if rest.get("result"):
                            aeusserungen.hinzu(epoche, rest["result"])
                    except Exception as fehler:
                        melde(f"  Rest vor dem Befehl nicht lesbar: {fehler}")
                    # GEGENPROBE MIT DER FREIEN ERKENNUNG (2026-09-15, offline
                    # gefunden). Ein einzeln gesprochenes "punkt setzen" hoerte das
                    # kleine Modell als "satz loeschen" - mit Ruhe davor und danach,
                    # also angenommen, und der gerade diktierte Satz war weg. Das
                    # grosse Modell hoerte dort "umsetzen". Bei jedem echten Befehl
                    # bisher hatte es das zweite Wort: "Satz loeschen" (2x), "jax
                    # wiederholen", "satz wiederholen". Also gilt der Befehl nur,
                    # wenn die freie Erkennung im selben Zeitraum "loesch..." bzw.
                    # "wiederhol..." gehoert hat.
                    stamm = "lösch" if b["satz"] == BEFEHL_LOESCHEN else "wiederhol"
                    gegen = aeusserungen.worte_nach(epoche, b["start"] - BEFEHL_SPIELRAUM_S)
                    if not any(stamm in w.get("word", "") for w in gegen):
                        melde(f"  {b['satz']!r} verworfen - die freie Erkennung hoerte "
                              f"{' '.join(w.get('word', '') for w in gegen)!r}")
                    else:
                        # NACH DEM WORTENDE SCHNEIDEN, NICHT NACH DEM ANFANG (2026-09-15,
                        # zweite Brief-Probe). Das grosse Modell hoerte "jax wiederholen"
                        # und liess "jax" mehr als 0,35 s vor dem "satz" des kleinen
                        # beginnen - "Jax" blieb stehen, Anna las "Satz wiederholen Jax".
                        # Vor dem Befehl ist es nachweislich still (0,65 s bis 0,25 s vor
                        # seinem Beginn, siehe oben); ein echtes Wort davor endet also
                        # frueher. Was spaeter endet, gehoert zum Befehl. Die Grenze liegt
                        # mitten im Ruhefenster (0,35 s vor dem Beginn): Ein echtes Wort
                        # endet vor 0,65 s, das grosse Modell setzt Marken bis 0,5 s
                        # frueher als das kleine - sein "satz" endet also nach -0,2 s.
                        aeusserungen.ab_zeit_entfernen(epoche, b["start"] - BEFEHL_SPIELRAUM_S,
                                                       nach_ende=True)
                        aeusserungen.befehlsrest_entfernen()
                        if b["satz"] == BEFEHL_LOESCHEN:
                            weg = aeusserungen.satz_entfernen()
                            melde(f"  SATZ LOESCHEN: gestrichen {weg!r}")
                            antwort = (f"Gestrichen: {zum_vorlesen(weg)}" if weg
                                       else "Es gibt noch nichts zu streichen.")
                        else:
                            zuletzt = aeusserungen.satz()
                            melde(f"  SATZ WIEDERHOLEN: {zuletzt!r}")
                            antwort = (f"Zuletzt: {zum_vorlesen(zuletzt)}" if zuletzt
                                       else "Ich habe noch nichts geschrieben.")
                        # Waehrend der Antwort mitlesen und verwerfen, danach beide
                        # Erkenner frisch - die eigene Stimme soll nicht im Text landen.
                        vorrat = sprechen_bei_offener_aufnahme(antwort, prozess)
                        erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE)
                        erkenner.SetWords(True)
                        schluss = vosk.KaldiRecognizer(modell_klein, ABTASTRATE, GRAMMATIK_SCHLUSS)
                        schluss.SetWords(True)
                        epoche += 1
                        zeitverlauf = []
                        pegel_puffer = []
                        letzte_aeusserung = time.time()
                        # Die Sperrfrist fuer den Schluss gilt nach jedem Befehl neu:
                        # Offline gefunden - direkt nach "Satz loeschen" machte das
                        # frische kleine Modell aus "die Rechnung liegt dem Schreiben
                        # bei" ein "diktat beenden" (0,41 s Luecke) nach 1,9 s.
                        aufnahme_seit = time.time()
                        continue

            # ZUERST den Schluss-Erkenner fragen. Er bekommt denselben
            # Block; wer zuerst fertig ist, ist unerheblich - entscheidend
            # ist, dass der Schlusssatz nicht erst durch die freie
            # Erkennung muss, wo er verloren geht.
            if schluss is not None and schluss.AcceptWaveform(block):
                ergebnis_schluss = json.loads(schluss.Result())
                gehoert = ergebnis_schluss.get("text", "").strip()
                mittel = ((sum(pegel_puffer) / len(pegel_puffer))
                          if pegel_puffer else 0.0)
                worte_befehl = ergebnis_schluss.get("result", [])
                if gehoert in (BEFEHL_LOESCHEN, BEFEHL_WIEDERHOLEN) and len(worte_befehl) == 2:
                    luecke = schluss_luecke(worte_befehl)
                    anfang, ende = worte_befehl[0].get("start", 0), worte_befehl[1].get("end", 0)
                    if luecke is not None and luecke > SCHLUSS_LUECKE_MAX_S:
                        melde(f"  {gehoert!r} verworfen - Woerter nicht zusammenhaengend ({luecke:.2f} s)")
                    elif not ruhig(zeitverlauf, anfang - BEFEHL_RAND_DAVOR_S - BEFEHL_RUHE_DAVOR_S,
                                   anfang - BEFEHL_RAND_DAVOR_S):
                        # Mit Pegeln: Am 2026-09-15 wurde ein echtes "Satz
                        # wiederholen" nach fuenf Sekunden Pause so verworfen, und
                        # ohne Zahlen war nicht zu sagen, was davor laut war.
                        a_i = max(0, int((anfang - BEFEHL_RAND_DAVOR_S - BEFEHL_RUHE_DAVOR_S) / BLOCK_S) - 2)
                        b_i = int(math.ceil(anfang / BLOCK_S)) + 1
                        melde(f"  {gehoert!r} verworfen - davor nicht still "
                              f"({anfang:.2f} s, Pegel ab {a_i * BLOCK_S:.2f} s: "
                              f"{[round(x) for x in zeitverlauf[a_i:b_i]]})")
                    else:
                        melde(f"  {gehoert!r} erkannt ({anfang:.2f}-{ende:.2f} s) - warte auf Ruhe danach")
                        befehl_offen = {"satz": gehoert, "start": anfang, "ende": ende}
                    continue
                if ist_schluss(gehoert):
                    # ZU LEISE IST KEIN SCHLUSS - ein Stoergeraeusch hat nicht den
                    # Pegel einer Stimme. Dieselbe Schwelle wie bei der freien
                    # Erkennung weiter unten.
                    if mittel < PEGEL_SCHWELLE:
                        melde(f"  Schluss {gehoert!r} verworfen - zu leise "
                              f"(Pegel {mittel:.0f} unter {PEGEL_SCHWELLE:.0f})")
                        continue
                    # KEIN SCHLUSS OHNE SPRECHPAUSE DAVOR - siehe pause_davor().
                    # Das ist die Regel, die die vier vorherigen Reparaturen nicht
                    # geschafft haben: Bruchstuecke entstehen MITTEN im Redefluss, ein
                    # echtes 'Diktat beenden' folgt auf eine Pause.
                    if not pause_davor(pegel_verlauf):
                        melde(f"  Schluss {gehoert!r} verworfen - keine Sprechpause davor "
                              f"(Pegel {mittel:.0f})")
                        continue
                    luecke = schluss_luecke(ergebnis_schluss.get("result", []))
                    if luecke is not None and luecke > SCHLUSS_LUECKE_MAX_S:
                        melde(f"  Schluss {gehoert!r} verworfen - Woerter nicht zusammenhaengend "
                              f"({luecke:.2f} s Luecke, erlaubt {SCHLUSS_LUECKE_MAX_S:.1f} s)")
                        continue
                    seit_start = time.time() - aufnahme_seit
                    if seit_start < SCHLUSS_SPERRFRIST_S:
                        # Niemand beendet drei Sekunden nach dem Start; wer
                        # diktieren will, diktiert.
                        melde(f"  Schluss {gehoert!r} nach nur {seit_start:.1f} s "
                              f"- Sperrfrist, wird verworfen")
                        continue
                    # AUCH DER SCHLUSS WARTET AUF RUHE DANACH (2026-09-15). Zweimal
                    # an einem Tag entstand ein vollstaendiges "diktat beenden"
                    # mitten im Fliesstext ("bis Ende des Monats", und nach "Satz
                    # loeschen" aus "die Rechnung liegt dem Schreiben bei"). Wer
                    # "Diktat beenden" sagt, schweigt danach; ein Fliesstext geht
                    # weiter. Dieselbe Pruefung wie bei den beiden Befehlen.
                    worte_s = ergebnis_schluss.get("result", [])
                    ende_s = worte_s[-1].get("end", 0) if worte_s else len(zeitverlauf) * BLOCK_S
                    melde(f"  {gehoert!r} gehoert - warte auf Ruhe danach")
                    befehl_offen = {"satz": SCHLUSSSATZ, "gehoert": gehoert, "worte": worte_s,
                                    "start": worte_s[0].get("start", 0) if worte_s else ende_s,
                                    "ende": ende_s, "mittel": mittel, "seit_start": seit_start}
                    continue
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
            ergebnis_frei = json.loads(erkenner.Result())
            text = ergebnis_frei.get("text", "").strip()
            worte_frei = ergebnis_frei.get("result", [])
            mittel = ((sum(pegel_puffer) / len(pegel_puffer))
                      if pegel_puffer else 0.0)
            pegel_puffer = []
            # Waehrend ein Befehl auf seine Ruhe wartet, wird hier NICHTS
            # herausgenommen: Stellt er sich als Fehlausloeser heraus, waeren
            # echte Woerter weg. Entfernt wird erst bei der Bestaetigung
            # (Aeusserungen.ab_zeit_entfernen).
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
            aeusserungen.hinzu(epoche, worte_frei, text)
    except KeyboardInterrupt:
        pass
    finally:
        if prozess:
            try:
                prozess.terminate()
            except Exception:
                pass

    gesammelt = aeusserungen.eintraege()

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
    #
    # UND NICHT NUR DIE EXAKTEN SCHLUSSWORTE (2026-09-14). Die freie Erkennung
    # versteht "diktat beenden" nicht zwingend als diese Woerter: Bei Stephans
    # Einkaufszettel kam es als "der cat" an und stand als eigener Eintrag auf
    # dem Zettel. Deshalb wird jetzt nach ZEIT geschnitten: Alles, was die freie
    # Erkennung ab dem Beginn des Schlusssatzes gehoert hat, faellt weg - egal,
    # was sie daraus gemacht hat. Die Wortliste bleibt als Rueckfall, falls
    # keine Zeitmarken vorliegen.
    rest = ""
    try:
        ergebnis_rest = json.loads(erkenner.FinalResult())
        rest = ergebnis_rest.get("text", "").strip()
        if rest and schluss_beginn is not None and ergebnis_rest.get("result"):
            # Die Zeitmarken ins Protokoll - nur die des Rests. Beim ersten
            # echten Test blieb "Den" stehen, und ohne Zahlen war nicht zu
            # sagen, wo das grosse Modell den Schlusssatz hingelegt hatte.
            melde("  Resttext mit Zeiten: " + ", ".join(
                f"{w['word']} {w.get('start', 0):.2f}-{w.get('end', 0):.2f}"
                for w in ergebnis_rest["result"])
                  + f" | Schlusssatz ab {schluss_beginn:.2f}")
            behalten, grenze = rest_kuerzen(ergebnis_rest["result"], schluss_beginn)
            weg = len(ergebnis_rest["result"]) - len(behalten)
            if weg:
                melde(f"  vom Resttext {weg} Wort/Woerter ab dem Schlusssatz "
                      f"abgeschnitten (ab {grenze:.2f} s)")
            rest = " ".join(behalten).strip()
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
    gesammelt = zusammenziehen(gesammelt)

    if not gesammelt:
        sprich(ANSAGE_LEER)
        return 0

    pfad = (brief_schreiben(gesammelt) if name in BRIEF_ZIELE
            else notiz_schreiben(name, gesammelt))
    melde(f"  geschrieben nach {pfad}")
    # SAETZE ZAEHLEN, NICHT STUECKE (2026-09-15): Der Brief mit elf Saetzen
    # meldete "3 Sätze" - gezaehlt wurden die Stuecke der Erkennung.
    anzahl = len(gesammelt)
    if name in BRIEF_ZIELE:
        text = " ".join(gesammelt).strip()
        anzahl = len(re.findall(r"[.?!](?=\s|$)", text)) + (0 if text[-1:] in ".?!" else 1)
    sprich(ansage_ende(name, anzahl))
    # KEIN Vorlesen mehr an dieser Stelle (Stephan, 2026-08-19) - siehe
    # VORLESEN_HINWEIS oben. Das Vorlesen mit Satzzeichen lebt unveraendert in
    # dialos-notiz.py weiter, wo es auf Ansage geschieht; die dort gemessene
    # Begruendung (3,670 s ohne gegen 4,884 s mit Satzzeichen, der Unterschied
    # besteht ausschliesslich aus Pausen) gilt weiter und steht in
    # docs/diktat.md.
    return 0


if __name__ == "__main__":
    sys.exit(main())
