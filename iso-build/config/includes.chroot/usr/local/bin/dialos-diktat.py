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
import shutil
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


# DIE SCHWELLEN RICHTEN SICH NACH DEM GEMESSENEN RAUSCHEN (2026-09-15, Pruefstand).
# 150 fuer Text und 400 fuer die Ruhe um Befehle waren am eingebauten Mikrofon
# mit Echo-Unterdrueckung gemessen - Rauschen dort 28 bis 68. Stephans erster
# Brief ins USB-Tischmikrofon TONOR TC30 hing: Rauschen 220-330 (5-%-Quantil
# 222), also NIE eine "Sprechpause" unter 150 - "Diktat beenden" wurde dreimal
# verworfen, und weil jedes Rauschen als Lebenszeichen galt, lief auch die
# Zeitgrenze nie ab. Die Stimme kam dabei LAUTER an (80-%-Quantil 6632).
#
# Jetzt: Rauschboden = 5-%-Quantil der letzten 30 s, Schwelle = das 2,5-Fache,
# aber nie unter den bisherigen festen Werten. Am eingebauten Mikrofon aendert
# sich damit nichts (2,5 x 68 = 170 kaum ueber 150, Befehlsruhe bleibt 400).
RAUSCH_FENSTER_S = 30.0
RAUSCH_QUANTIL = 0.05
RAUSCH_FAKTOR = 2.5


class Rauschboden:
    def __init__(self):
        self.werte = collections.deque(maxlen=int(RAUSCH_FENSTER_S / BLOCK_S))

    def neu(self, pegel_wert):
        self.werte.append(pegel_wert)

    def boden(self):
        if len(self.werte) < 8:
            return 0.0
        geordnet = sorted(self.werte)
        return geordnet[int(len(geordnet) * RAUSCH_QUANTIL)]

    def schwelle(self, mindestens):
        return max(mindestens, RAUSCH_FAKTOR * self.boden())


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
        # ALLE DREI WEGE NENNEN (Stephan, 2026-09-15: "muss es nicht nur
        # Vorlesen oder Drucken als Option geben"). Vorlesen zuerst - es ist
        # die einzige Kontrolle auf Erkennungsfehler.
        return satz + " Du kannst sagen: Brief vorlesen, Brief drucken oder Brief als PDF speichern."
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
# Persoenliche Daten (2026-09-16): Absender, Kontakt und Name unter dem Gruss.
# Gibt es sie, gelten sie; sonst der alte Weg ueber nutzer-name.txt/absender.txt.
PERSOENLICHE_DATEN_SKRIPT = "/usr/local/bin/dialos-persoenliche-daten.py"


def persoenliche_daten():
    """(Modul, Daten) oder (None, {}) - ein Brief ohne Absender ist besser als keiner."""
    modul = holen(PERSOENLICHE_DATEN_SKRIPT, "persoenliche_daten")
    if not modul:
        return None, {}
    try:
        return modul, modul.lesen()
    except Exception:
        return None, {}
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

# MIKROFON FUER DEN VERGLEICH (2026-09-15). Stephan hat ein USB-Tischmikrofon
# (TONOR TC30) angeschlossen, um es auf dem Pruefstand gegen das eingebaute zu
# messen. Die Festlegung "immer das eingebaute" vom 2026-08-17 gilt weiter - nur
# wenn diese Datei eine vorhandene Quelle nennt, nimmt das DIKTAT diese. Der
# Befehlsdienst bleibt unberuehrt. Ohne Echo-Unterdrueckung ist das hier
# unkritisch: Waehrend Anna spricht, wird ohnehin verworfen.
MIKROFON_WAHL = os.path.join(os.path.expanduser("~"), ".config", "dialos", "diktat-mikrofon")


def waehle_mikrofon():
    """Wie im Befehlsdienst: bereinigte Quelle, sonst das eingebaute.

    Kein Bluetooth und kein USB - Stephans Festlegung vom 2026-08-17,
    Begruendung in docs/hardware.md. Ausnahme zum Messen: MIKROFON_WAHL.
    """
    try:
        roh = subprocess.run(["pactl", "-f", "json", "list", "sources"],
                             capture_output=True, text=True, timeout=5).stdout
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
        if gewuenscht:
            melde(f"  gewuenschtes Mikrofon nicht da: {gewuenscht!r} - nehme das uebliche")
    except OSError:
        pass
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


# WAS "STILL" VOR UND NACH EINEM BEFEHL HEISST (2026-09-15, Brief mit Weg 3).
# Bis dahin galt PEGEL_SCHWELLE (150), die Grenze fuer TEXT. Stephans echtes
# "Diktat beenden" wurde damit als "danach nicht still" verworfen - gemessen nach
# dem Wort: 131, 166, 102, 81, 56. Das ist Nachhall und Atem, keine Sprache;
# Sprache lag in allen protokollierten Ablehnungen bei ueber 1000 (Fliesstext
# nach einem Fehlausloeser: 3035-9308). 400 laesst dazwischen Abstand nach beiden
# Seiten. Beendet hatte an dem Tag zweimal nur die Rueckfallebene der freien
# Erkennung.
BEFEHL_RUHE_SCHWELLE = 400.0


def ruhig(verlauf, von_s, bis_s, schwelle=BEFEHL_RUHE_SCHWELLE):
    """War es im Zeitraum [von_s, bis_s) still? verlauf = Pegel je Block ab 0 s."""
    a = max(0, int(von_s / BLOCK_S))
    b = max(a + 1, int(math.ceil(bis_s / BLOCK_S)))
    stueck = verlauf[a:b]
    return bool(stueck) and max(stueck) < schwelle


class Aeusserungen:
    """Das Diktat als Folge von Aeusserungen - damit sich die letzte streichen laesst.

    Jede Aeusserung behaelt ihre Woerter mit Zeitmarken (je Erkenner-Durchgang,
    "epoche") und die Eintraege, die daraus geworden sind. Vorher war das Diktat
    nur eine flache Liste von Eintraegen; welcher Eintrag zu welcher Aeusserung
    gehoerte - bei Listen koennen es mehrere sein -, war nicht mehr zu sagen.
    """

    def __init__(self, name):
        self.name = name
        # Woerter -> Text, wenn hinzu() ohne Text gerufen wird (mit Parakeet).
        self.umschreiben = None
        self.liste = []          # dicts: epoche, worte, eintraege

    def hinzu(self, epoche, worte, text=None):
        if text is None:
            text = (self.umschreiben(worte) if self.umschreiben
                    else " ".join(w["word"] for w in worte))
        # Ein Stueck, das NUR aus einem Umbruch besteht, ist nicht leer (Pruefstand,
        # 2026-09-15): Parakeets "Neuer Absatz." wird schon vorher zu "\n\n" - mit
        # der blossen strip()-Pruefung fiel dieser Absatz weg.
        if not text.strip() and "\n" not in text:
            return []
        # EIN GESPROCHENES SATZZEICHEN UEBER DIE STUECKGRENZE (2026-09-15,
        # zweite Brief-Probe). Vosk schneidet lange Rede auch ohne Pause - einmal
        # genau zwischen "kommas" und "setzen". Das eine Stueck endete auf
        # "Kommas", das naechste begann mit "Setzen", und beide standen so im
        # Brief. Beginnt ein Stueck mit dem zweiten Wort eines Satzzeichens und
        # endete das vorige mit dem ersten, wird beides zusammen neu verarbeitet.
        # Mit Parakeet sind die Satzzeichen schon umgesetzt - nichts zu verbinden.
        vorher = self.liste[-1] if self.liste and self.umschreiben is None else None
        erstes = text.split()[0].lower() if text.split() else ""
        if (vorher and self.name not in LISTEN_ZIELE and vorher["epoche"] == epoche
                and vorher.get("text")
                and SATZZEICHEN_FORTSETZUNG.get(vorher["text"].split()[-1].lower()) == erstes):
            self.liste.pop()
            melde(f"  Satzzeichen ueber die Stueckgrenze - mit dem vorigen Stueck "
                  f"zusammengefasst: {vorher['text'].split()[-1]!r} + {erstes!r}")
            text = vorher["text"] + " " + text
            worte = list(vorher["worte"]) + list(worte)
        # Rest eines geteilten "neue Zeile"/"neuer Absatz" am Stueckanfang (Parakeet):
        # Endete das vorige Stueck schon mit dem Umbruch, faellt das Wort weg.
        if (self.umschreiben is not None and self.liste and self.liste[-1]["eintraege"]
                and self.liste[-1]["eintraege"][-1].endswith("\n")):
            ohne = re.sub(r"^(zeile|absatz)\b[,.;:]?\s*", "", text, flags=re.IGNORECASE)
            if ohne != text:
                melde(f"  Rest eines geteilten Umbruchs am Stueckanfang entfernt: {text[:len(text)-len(ohne)]!r}")
                text = ohne
            if not text.strip() and "\n" not in text:
                return []
            # Beginnt das Stueck mit einer neuen Zeile, verliert eine kurze Zeile
            # davor ihren Punkt ("Mit freundlichen Gruessen." | "\nStephan"),
            # dieselbe Regel wie innerhalb eines Stuecks.
            if text.startswith("\n") and not text.startswith("\n\n"):
                vorige = self.liste[-1]["eintraege"][-1]
                neu = kurze_zeile_ohne_punkt(vorige.rstrip() + "\n")[:-1]
                if neu != vorige.rstrip():
                    self.liste[-1]["eintraege"][-1] = neu
        eintraege = aeusserung_verarbeiten(self.name, text, self.umschreiben is not None)
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
        stellen = satzenden(rest)
        satzende = (stellen[-1] + 1) if stellen else 0
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

    def schlussrest_entfernen(self):
        """Streicht ein gescheitertes "Diktat beenden" am Textende.

        Brief vom 2026-09-15, 13:43: Stephan sagte "... Stefan Roesner Diktat
        beenden" ohne Pause - das kleine Modell hoerte "[unk] diktat beenden",
        kein Schluss. Beim zweiten Mal, nach einer Pause, endete das Diktat -
        und im Brief stand "Stefan Roesner Diktat beenden". Das zweite wurde
        nach Zeit abgeschnitten, das erste war da laengst geschrieben.
        """
        while self.liste and not self.liste[-1]["eintraege"]:
            self.liste.pop()
        if not self.liste:
            return
        a = self.liste[-1]
        e = a["eintraege"][-1]
        worte = list(re.finditer(r"\S+", e))
        klein = [re.sub(r"[^\wäöüß]", "", w.group().lower()) for w in worte]
        if len(klein) >= 2 and klein[-2:] == SCHLUSSSATZ.split():
            vorne = e[:worte[-2].start()].rstrip(" ")
            melde(f"  gescheitertes 'Diktat beenden' am Textende entfernt: {e[worte[-2].start():]!r}")
            if vorne.strip():
                a["eintraege"][-1] = vorne
            else:
                a["eintraege"].pop()

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


# KEIN SATZENDE: Punkt nach Abkuerzung oder Ordnungszahl (2026-09-15, Weg 3).
# Parakeet schreibt "Am 12. August" und "Frau Dr. Muster" - mit Vosk kamen
# Punkte nur aus "punkt setzen", jetzt setzt der Erkenner sie selbst.
ABKUERZUNGEN = ("dr", "prof", "nr", "str", "st", "bzw", "usw", "ca", "z", "b", "evtl",
                "ggf", "inkl", "tel", "hr", "fr", "jan", "feb", "febr", "aug", "sept",
                "okt", "nov", "dez", "vgl", "etc", "u", "a", "d", "h", "i")


def satzenden(text):
    """Positionen der Zeichen, die einen Satz beenden (. ? ! und Zeilenwechsel)."""
    stellen = []
    for m in re.finditer(r"[.?!\n]", text):
        if m.group() == ".":
            davor = re.search(r"([\wäöüÄÖÜß]+)$", text[:m.start()])
            if davor and (davor.group(1).isdigit() or davor.group(1).lower() in ABKUERZUNGEN):
                continue
        stellen.append(m.start())
    return stellen


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
    """Behaelt die Woerter des Rests, die deutlich VOR dem Schlusssatz ENDEN.

    Bis 2026-09-15 galt der Beginn (ein Bruchstueck wie "Den" beginnt
    unmittelbar davor oder mittendrin). Das reichte nicht, siehe unten.
    """
    # SEIT 2026-09-15 NACH DEM ENDE (Parakeet-Brief, 14:33). Das grosse Modell
    # hoerte "Diktat" als "ekd" (59,34-59,88 s), das kleine setzte den Schluss
    # auf 60,09 s - 0,75 s spaeter. "ekd" BEGANN vor der Grenze (59,74), blieb
    # stehen und wurde als "Okay" in den Brief geschrieben. Ein echtes letztes
    # Wort ENDET vor der Sprechpause, die pause_davor() verlangt; was nach der
    # Grenze endet, gehoert zum Schlusssatz. Nachgerechnet an den Schluessen vom
    # 2026-09-15 (12:29, 13:43): dort fiel auch vorher schon alles Richtige weg.
    grenze = schluss_beginn - SCHLUSS_SPIELRAUM_S
    return [w["word"] for w in worte
            if w.get("end", w.get("start", 0)) <= grenze], grenze


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


DATEINAME_SKRIPT = "/usr/local/bin/dialos-dateiname.py"


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
    modul, daten = persoenliche_daten()
    if daten:
        return modul.absenderzeilen(daten) + modul.kontaktzeilen(daten)
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


def empfaenger_zeilen(empfaenger):
    """Anschriftzeilen des Empfaengers nach DIN 5008 - Land nur bei Auslandspost."""
    if not empfaenger:
        return []
    em = holen(EMPFAENGER_SKRIPT, "empfaenger")
    _, daten = persoenliche_daten()
    if em:
        return em.zeilen(empfaenger, (daten or {}).get("land", ""))
    return [z for z in (empfaenger.get("name"), empfaenger.get("strasse"),
                        f"{empfaenger.get('plz', '')} {empfaenger.get('ort', '')}".strip()) if z]


def briefbogen(text, empfaenger=()):
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
    # EMPFAENGER LINKS ZWISCHEN ABSENDER UND DATUM (2026-09-17) - wie im Anschriftfeld
    # eines Briefs. dialos-notiz.py erkennt ihn daran: links, vor der Datumszeile.
    if empfaenger:
        teile += list(empfaenger)
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


# GRUSSFORMEL UND NAME AUF EIGENE ZEILEN (2026-09-16, Stephans frei diktierter
# Brief). Er sagte "neuer Absatz mit freundlichen Gruessen Stefan Roesner" ohne
# "neue Zeile" - im Brief stand "Mit freundlichen Gruessen, Stephan Roesner" in
# einer Zeile. Nach DIN 5008 steht der Name unter dem Gruss; wer das nicht
# ansagt, meint es trotzdem so. Ein Punkt oder Komma hinter Gruss oder Name
# (Parakeet setzt beides) faellt weg.
GRUSSFORMELN = ("mit freundlichen grüßen", "mit freundlichem gruß", "freundliche grüße",
                "viele grüße", "liebe grüße", "herzliche grüße", "beste grüße",
                "hochachtungsvoll")


def grussformel_richten(text):
    """Nur ganz am Ende, nur am Satz- oder Zeilenanfang, und der Name hat hoechstens vier Woerter."""
    muster = re.compile(r"(?i)(^|\n|[.!?][ \t]+)[ \t]*(" + "|".join(re.escape(g) for g in GRUSSFORMELN)
                        + r")[,.]?[ \t]*\n?[ \t]*([^\n.,!?]{1,50}?)[.,]?[ \t]*$")
    rest = text.rstrip()
    treffer = muster.search(rest)
    if not treffer or len(treffer.group(3).split()) > 4:
        return text
    # Vor dem Gruss eine Leerzeile (DIN 5008), auch wenn kein Absatz gesprochen
    # wurde - am 2026-09-16 stand "... ueberweisen. Mit freundlichen Gruessen".
    davor = rest[:treffer.start(2)].rstrip(" \t\n")
    davor = davor + "\n\n" if davor else ""
    # DER NAME KOMMT AUS DEN PERSOENLICHEN DATEN, wenn es sie gibt (2026-09-16):
    # Parakeet schrieb unter Stephans Gruss "Stefan Gruesse" - ein Name ist fuer
    # jeden Erkenner ein unbekanntes Wort, und der eigene steht ohnehin fest.
    modul, daten = persoenliche_daten()
    name = (modul.unterschrift_name(daten) if daten else "") or treffer.group(3).strip()
    if name != treffer.group(3).strip():
        melde(f"  Unterschrift aus den persoenlichen Daten: {treffer.group(3).strip()!r} -> {name!r}")
    return davor + treffer.group(2) + "\n" + name


# BETREFFZEILE (Stephan, 2026-09-16: "fett geschrieben und Betreff: ......").
# Sein frei diktierter Brief begann mit "Betreff Nebenkostenabrechnung 2025" -
# Parakeet machte daraus "Betreff Nebenkostenabrechn 2025." mit Punkt. Jetzt
# steht am Briefanfang immer "Betreff: ..." ohne Punkt am Ende. FETT wird die Zeile
# im PDF (dialos-archiv.py als_pdf) - eine Textdatei kennt kein Fett; deshalb
# druckt dialos-drucken.py den Brief ueber dasselbe PDF.
# "Betriff"/"Betrifft" auch: So schrieb Parakeet es am 2026-09-16 (Vosk: "betreff").
BETREFF = re.compile(r"(?i)^\s*betr[ie]ff?t?\b\s*[:,.]?\s*")


ANREDE = re.compile(r"(?im)^((?:sehr geehrte|liebe|lieber|hallo)\b[^\n.!?]*?)[ \t]*[.!,]?[ \t]*\n\n")


ANREDE_ANFANG = re.compile(r"(?i)\b(sehr geehrte[rs]?|liebe[rs]?(?!\s+grü)|hallo|guten tag)\b")


def anrede_absetzen(text):
    """Die Anrede steht allein, mit Komma und Leerzeile danach - auch nach dem Betreff.

    GEFUNDEN AM 2026-09-17: Stephan sagte "Betreff", Pause, "Mieter Stephan
    Roesner", Pause, "Sehr geehrte Damen und Herren". Parakeet setzte erst hinter
    "Herren" ein Ausrufezeichen - und die Betreffzeile lautete "Mieter Stephan
    Roesner Sehr geehrte Damen und Herren". Eine Anrede beendet den Betreff immer.

    Gesucht wird nur am Briefanfang (erste 300 Zeichen): "Liebe Gruesse" am Ende
    und ein "Hallo" mitten im Text sind keine Anrede. Das Ende der Anrede ist das
    erste Komma, Ausrufezeichen, Punkt oder Zeilenende; fehlt eins, "Damen und
    Herren" oder hoechstens fuenf Woerter.
    """
    for treffer in ANREDE_ANFANG.finditer(text[:300]):
        davor = text[:treffer.start(1)]
        # Nur am Anfang, nach einem Satzende oder Umbruch, oder direkt nach dem
        # Betreff - "Ich wollte nur hallo sagen" ist keine Anrede.
        if (not davor.strip() or re.search(r"[.!?:\n]\s*$", davor)
                or re.match(r"(?i)\s*betr[ie]ff?t?\b[^.!?\n]*$", davor)):
            break
    else:
        return text
    start = treffer.start(1)
    rest = text[start:]
    # Das erste Satzzeichen hinter mehr als der blossen Formel beendet die Anrede:
    # "Sehr geehrte, sehr geehrte Damen und Herren" (Stephan, 16.09., verhaspelt)
    # endet nicht nach "Sehr geehrte".
    formel = len(treffer.group(1).split())
    satzende = set(satzenden(rest[:120]))
    ende = next((m for m in re.finditer(r"[,.!]|\n", rest[:120])
                 if (len(rest[:m.start()].split()) > formel
                     or not ANREDE_ANFANG.match(rest[m.end():].lstrip()))
                 and (m.group() != "." or m.start() in satzende)), None)
    if ende and len(rest[:ende.start()].split()) <= 9:
        anrede, danach = rest[:ende.start()], rest[ende.end():]
    else:
        herren = re.search(r"(?i)damen und herren", rest[:80])
        if herren:
            anrede, danach = rest[:herren.end()], rest[herren.end():]
        else:
            return text
    davor = text[:start].rstrip(" ,")
    anrede = " ".join(anrede.split())
    danach = danach.lstrip(" \n")
    return (davor + "\n\n" if davor.strip() else "") + anrede + ",\n\n" + danach


def anrede_richten(text):
    """Die Anrede endet mit Komma - auch ueber Stueckgrenzen.

    parakeet_natuerlich richtet das nur, wenn Anrede und Absatz im selben Stueck
    kommen. Am 2026-09-16 sprach Stephan nach der Anrede eine Pause, der Absatz
    kam im naechsten Stueck, und es blieb "Damen und Herren."
    """
    return ANREDE.sub(r"\1,\n\n", text, count=1)


def betreff_richten(text):
    """Macht aus "Betreff ..." am Anfang die Betreffzeile samt Absatz danach.

    DER BETREFF ENDET AM ERSTEN SATZENDE, nicht erst am Absatz (2026-09-16,
    Stephans erster Brief mit festem Parakeet): Er sagte "Absatz" statt "neuer
    Absatz", es gab keinen Umbruch - und der ganze Brief stand fett in der
    Betreffzeile. Der Punkt am Ende faellt weg, eine Betreffzeile hat keinen.
    """
    treffer = BETREFF.match(text)
    if not treffer:
        return text
    rest = text[treffer.end():]
    enden = satzenden(rest)
    ende = enden[0] if enden else len(rest)
    inhalt = rest[:ende].strip(" ,;:").rstrip(".")
    if not inhalt:
        return text
    inhalt = inhalt[:1].upper() + inhalt[1:]
    rest = rest[ende + 1:].lstrip("\n ")
    return f"Betreff: {inhalt}\n\n{rest}" if rest else f"Betreff: {inhalt}"


def brief_text(zeilen):
    """Der Brieftext aus den Aeusserungen: Gruss, Anrede, Betreff gerichtet.

    Leerzeichen am Zeilenanfang fallen weg - sie entstehen, wo ein Stueck mit
    einem gesprochenen Absatz endet und das naechste mit Leerzeichen angehaengt
    wird. Der Pruefstand ruft genau diese Funktion.
    """
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", " ".join(zeilen))
    return betreff_richten(anrede_richten(anrede_absetzen(grussformel_richten(text))))


def brief_schreiben(zeilen, empfaenger=None):
    """Schreibt den Brief unter einem eigenen Namen mit Datum und Uhrzeit.

    JEDER BRIEF BEHAELT SEINEN NAMEN (Stephan, 2026-09-15): "2026-09-15-1343-
    Brief.txt" statt "brief.txt". Vorher gab es genau eine brief.txt, und der
    vorige Brief wurde mit Stempel beiseitegelegt - jetzt wird nichts mehr
    verschoben, und "Brief vorlesen" meint den neuesten. Die Regel fuer Namen
    und Reihenfolge steht in dialos-dateiname.py und nur dort.

    Ueberschreiben kann dabei nichts: Zwei Briefe in derselben Minute bekommen
    "-2" angehaengt. Ein Brief ist Arbeit von Minuten, und wer ihn verliert,
    merkt es erst, wenn er ihn braucht.
    """
    namen = holen(DATEINAME_SKRIPT, "dateiname")
    if namen:
        namen.umstellen(DOKUMENT_ORDNER, melde)
        pfad = namen.neuer_pfad(DOKUMENT_ORDNER, namen.BRIEF, "txt")
    else:
        # Ohne das Hilfsskript derselbe Name, nur ohne Kollisionsschutz -
        # lieber das als gar kein Brief.
        os.makedirs(DOKUMENT_ORDNER, exist_ok=True)
        pfad = os.path.join(DOKUMENT_ORDNER, time.strftime("%Y-%m-%d-%H%M") + "-Brief.txt")
        melde("  ACHTUNG: dialos-dateiname.py fehlt")
    with open(pfad, "w", encoding="utf-8") as f:
        # MIT LEERZEICHEN VERBINDEN, NICHT MIT ZEILENUMBRUCH (2026-09-15). Jede
        # Aeusserung ist ein Stueck desselben Fliesstexts. Mit "\n" verbunden
        # konnte der Briefbogen einen Stueck-Uebergang nicht von einem
        # gesprochenen "neue zeile" unterscheiden - und zog beide zusammen: "Mit
        # freundlichen Gruessen neue zeile Stephan Roesner" stand in einer Zeile.
        f.write(briefbogen(brief_text(zeilen), empfaenger_zeilen(empfaenger)))

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
            # Jeder Eintrag steht ohnehin auf einer eigenen Zeile - ein "neue
            # zeile" am Anfang (Parakeet-Test, 2026-09-15) gaebe sonst eine
            # Leerzeile zu viel; aus "neuer absatz" wird genau eine.
            if z.startswith("\n"):
                z = z[1:]
            f.write(z.rstrip(" ") + "\n")
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


# PERSOENLICHES WOERTERBUCH (Stephan, 2026-09-15: "mein Name Stephan Roesner
# wird zu Stefan Roessner"). Beide klingen gleich - kein Erkenner kann die
# Schreibweise hoeren, auch Whisper oder Parakeet nicht. Also wird NACH der
# Erkennung korrigiert, mit Eintraegen "gehoert = geschrieben".
#
# NUR AUF DEM GERAET, im eigenen Konto (Stephans Wahl): Die Datei enthaelt
# Namen. Ins oeffentliche Repo kommt nur die Vorlage mit erfundenen Beispielen.
WOERTERBUCH = os.path.join(os.path.expanduser("~"), ".config", "dialos", "woerterbuch.txt")
WOERTERBUCH_VORLAGE = "/usr/local/share/dialos/woerterbuch-vorlage.txt"
_WORTZEICHEN = r"[\wäöüÄÖÜß]"


def woerterbuch_laden():
    """[(Muster, Ersatz, gehoert)], laengste Eintraege zuerst.

    Fehlt die Datei, wird die Vorlage hineinkopiert - dann weiss ein Helfer, wo
    er Eintraege machen kann, ohne eine Anleitung zu suchen.
    """
    if not os.path.exists(WOERTERBUCH) and os.path.exists(WOERTERBUCH_VORLAGE):
        try:
            os.makedirs(os.path.dirname(WOERTERBUCH), exist_ok=True)
            shutil.copyfile(WOERTERBUCH_VORLAGE, WOERTERBUCH)
        except OSError:
            pass
    eintraege = []
    try:
        with open(WOERTERBUCH, encoding="utf-8") as f:
            for zeile in f:
                zeile = zeile.strip()
                if not zeile or zeile.startswith("#") or "=" not in zeile:
                    continue
                gehoert, geschrieben = (t.strip() for t in zeile.split("=", 1))
                worte = gehoert.split()
                if not worte or not geschrieben:
                    continue
                # Zwischen den Woertern jeder Leerraum, auch ein Zeilenwechsel
                # ("Gruessen\nMax Maier"); davor und danach kein Wortzeichen,
                # damit "maier" nicht in "Maierhof" greift.
                muster = re.compile(
                    rf"(?<!{_WORTZEICHEN})" + r"\s+".join(re.escape(w) for w in worte)
                    + rf"(?!{_WORTZEICHEN})", re.IGNORECASE)
                eintraege.append((muster, geschrieben, gehoert))
    except OSError:
        return []
    eintraege.sort(key=lambda e: len(e[2]), reverse=True)
    return eintraege


def woerterbuch_anwenden(text, eintraege=None):
    eintraege = woerterbuch_laden() if eintraege is None else eintraege
    for muster, geschrieben, _ in eintraege:  # _ = der gehoerte Wortlaut
        # Ersatz als Funktion, nicht als Zeichenkette: Sonst liest re.sub einen
        # Backslash oder "\\1" im Eintrag als Rueckverweis.
        neu = muster.sub(lambda _m, g=geschrieben: g, text)
        if neu != text:
            melde(f"  Woerterbuch: {_!r} -> {geschrieben!r}")
            text = neu
    return text


def aeusserung_verarbeiten(name, text, satzzeichen_fertig=False):
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
    # satzzeichen_fertig: Parakeet-Text (Weg 3) - dort sind Zeichen, Absaetze und
    # Zeilen schon gesetzt; satzzeichen_setzen() wuerde die Zeilenwechsel beim
    # Zerlegen in Woerter verlieren.
    mit_zeichen = text if (name in LISTEN_ZIELE or satzzeichen_fertig) else satzzeichen_setzen(text)
    if mit_zeichen != text:
        melde(f"  Satzzeichen:  {mit_zeichen!r}")
    gefasst = schreibung_richten(mit_zeichen)
    if gefasst.lower() != mit_zeichen.lower():
        melde("  ACHTUNG: Schreibhilfe hat mehr als die Schreibung geaendert")
    # NACH der Schreibhilfe: Sie wuerde eine gewollte Schreibweise sonst wieder
    # "verbessern". Steht der Eintrag am Satzanfang und ist klein geschrieben,
    # bleibt der Anfang gross (schreibung_richten hat ihn schon gross gemacht).
    mit_buch = woerterbuch_anwenden(gefasst)
    if mit_buch != gefasst and gefasst[:1].isupper():
        mit_buch = mit_buch[:1].upper() + mit_buch[1:]
    gefasst = mit_buch
    melde(f"  geschrieben: {gefasst!r}")
    neue = eintraege_aus(name, gefasst)
    if len(neue) > 1:
        melde(f"  in {len(neue)} Eintraege getrennt: {neue!r}")
    return neue



# PARAKEET SCHREIBT BRIEF UND NOTIZEN (Stephan, 2026-09-16: "Ja, bau Parakeet
# fest ein"). Getestet seit 2026-09-15 mit der Schalterdatei parakeet-test und
# dem Pruefstand (docs/pruefstand.md): frei diktierter Brief 3,4 % Wortfehler
# gegen Vosk 28,8 %, vorgelesener Brief 2,8 % gegen 12,7 %, und alle Satzzeichen
# richtig - Vosk setzt keine.
#
# SO GEBAUT, DASS VOSK DIE ZEIT FUEHRT: Vosk bleibt fuer alles, was Zeit
# braucht - Sprechpausen, Schlusssatz, "Satz loeschen", Gegenprobe. Parakeet
# erkennt jedes Stueck, das Vosk abliefert, noch einmal aus DERSELBEN Aufnahme,
# und sein Text kommt in den Brief. Beide Texte stehen im Protokoll.
#
# FUER ALLE KONTEN: Modell unter /usr/local/share/dialos-parakeet, sherpa-onnx
# systemweit (scripts/dialos-parakeet-einrichten.sh). Fehlt etwas, schreibt Vosk
# wie vor dem 15.09. - das Diktat faellt nie aus, nur weil Parakeet fehlt.
# Abschalten je Konto mit der Datei ~/.config/dialos/parakeet-aus (fuer
# Vergleiche auf dem Pruefstand; die Schalterdatei parakeet-test gilt nicht mehr).
PARAKEET_AUS = os.path.join(os.path.expanduser("~"), ".config", "dialos", "parakeet-aus")
PARAKEET_MODELL = "/usr/local/share/dialos-parakeet/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
PARAKEET_RAND_S = 0.3


def parakeet_laden():
    if not os.path.isfile(os.path.join(PARAKEET_MODELL, "tokens.txt")):
        melde(f"  PARAKEET: nicht eingerichtet ({PARAKEET_MODELL} fehlt), Vosk schreibt")
        return None
    try:
        import sherpa_onnx
        t0 = time.time()
        m = PARAKEET_MODELL
        erkenner = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=f"{m}/encoder.int8.onnx", decoder=f"{m}/decoder.int8.onnx",
            joiner=f"{m}/joiner.int8.onnx", tokens=f"{m}/tokens.txt",
            num_threads=4, model_type="nemo_transducer")
        melde(f"  PARAKEET: Modell geladen in {time.time()-t0:.1f} s")
        return erkenner
    except Exception as fehler:
        melde(f"  PARAKEET: nicht ladbar, Vosk schreibt ({fehler})")
        return None


def parakeet_bereinigen(text):
    """Parakeet setzt eigene Satzzeichen - im Diktat zaehlen nur gesprochene.

    Punkt, Komma usw. fallen weg; Gross- und Kleinschreibung bleibt, sie ist bei
    Parakeet meist richtig, und die Schreibhilfe macht danach nur noch gross.

    GESPROCHENES "KOMMA" ALS ZEICHEN (offline gefunden, 2026-09-15): Aus "Herren
    komma setzen" machte Parakeet "Herren, setzen" - das Wort wurde zum Zeichen,
    und nach dem Entfernen blieb "setzen" im Brief. Steht ein Zeichen direkt vor
    "setzen" und davor kein Satzzeichen-Wort, kommt das Wort zurueck. "Punkt.
    Setzen" bleibt dabei, wie es ist.
    """
    woerter = {",": "komma", ".": "punkt", "?": "fragezeichen", "!": "ausrufezeichen",
               ":": "doppelpunkt"}

    def zurueck(m):
        if m.group(1).lower() in woerter.values():
            return m.group(0)
        return f"{m.group(1)} {woerter[m.group(2)]} {m.group(3)}"
    text = re.sub(r"([\wäöüÄÖÜß]+)\s*([,.?!:])\s+(setzen)\b", zurueck, text, flags=re.IGNORECASE)
    text = re.sub(r"[.,;:!?\"„“”‚‘’»«()]", " ", text)
    return " ".join(text.split())


def kurze_zeile_ohne_punkt(text, hoechstens=4):
    """Streicht den Punkt am Ende kurzer Zeilen vor einem einfachen Zeilenwechsel."""
    def weg(m):
        zeile = m.group(1)
        if len(zeile.split()) <= hoechstens:
            return zeile.rstrip(". ") + m.group(2)
        return m.group(0)
    return re.sub(r"(?m)([^\n]*?\.)[ \t]*(\n)(?!\n)", weg, text)


def parakeet_natuerlich(text):
    """Weg 3 (Stephan, 2026-09-15): Parakeets eigene Satzzeichen bleiben.

    Nach der Probe mit gesprochenen Satzzeichen (Parakeet 14,9 % gegen Vosk
    9,9 %, das Befehlswort kam als "Saetzen") und dem Vergleich vom Morgen ohne
    sie (3,0 % gegen 7,6 %): Der Nutzer spricht natuerlich, Parakeet setzt Punkt
    und Komma. Gesprochen bleiben nur Absatz und Zeile - und wer aus Gewohnheit
    doch "Komma setzen" sagt, bekommt trotzdem das Zeichen, nicht die Woerter.
    """
    text = re.sub(r"\bs[äa]tzen\b", "setzen", text, flags=re.IGNORECASE)
    zeichen = {"komma": ",", "punkt": ".", "fragezeichen": "?", "ausrufezeichen": "!",
               "doppelpunkt": ":"}
    # Gesprochenes Satzzeichen samt der Zeichen, die Parakeet drumherum setzte
    # ("dankbar, Punkt setzen." -> "dankbar.").
    text = re.sub(r"\s*[,;:.!?]?\s*\b(komma|punkt|fragezeichen|ausrufezeichen|doppelpunkt)"
                  r"\s*[,.]?\s+setzen\b[,;:.!?]*",
                  lambda m: zeichen[m.group(1).lower()], text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\bgedankenstrich\s+setzen\b[,;:.!?]*", " -", text, flags=re.IGNORECASE)
    # Absatz und Zeile: die Zeichen danach fallen weg. Vor dem Absatz bleibt ein
    # Komma ("Herren,\n\n" - die Anrede braucht es), vor der Zeile nicht
    # ("Gruessen, neue Zeile, Stefan" -> "Gruessen\nStefan").
    text = re.sub(r"\s*\bneuer\s*[,.]?\s*absatz\b[,;:.!?]*\s*", "\n\n", text,
                  flags=re.IGNORECASE)
    # "ABSATZ" ALLEIN AM SATZANFANG (2026-09-16, Stephans erster Brief mit festem
    # Parakeet): Er sagte fuenfmal nur "Absatz" - Parakeet schrieb "Absatz." als
    # eigenen Satz oder "Absatz mit freundlichen Gruessen", und der Brief hatte
    # keinen einzigen Absatz. Nicht, wenn eine Zahl oder ein Artikel folgt:
    # "Absatz 3 des Vertrags", "Absatz des Vertrags" bleiben Text. Nur klein
    # geschrieben: "Absatz. Den Betrag ..." ist ein neuer Satz.
    text = re.sub(r"(?:^|(?<=[.!?])\s+|\n\n)absatz\b"
                  r"(?![,;:.!?]*\s*(?:\d|(?-i:des|der|dem|den|eins|zwei|drei|vier|fünf|sechs"
                  r"|sieben|acht|neun|zehn)\b))[,;:.!?]*\s*",
                  "\n\n", text, flags=re.IGNORECASE)
    # "zeil" auch: Am 2026-09-15 (TONOR) teilte Vosk genau in "neue Zeile" -
    # Parakeet schrieb "neue Zeil." und im naechsten Stueck "Zeile Stephan".
    text = re.sub(r"[,;]?\s*\bneue\s*[,.]?\s*zeile?\b[,;:.!?]*\s*", "\n", text,
                  flags=re.IGNORECASE)
    # Kurze Zeile vor einem Zeilenwechsel ohne Punkt ("Mit freundlichen Gruessen.
    # neue Zeile" -> "...Gruessen\n"): Gruss und Anschriftzeilen enden nicht mit Punkt.
    text = kurze_zeile_ohne_punkt(text)
    # Die Anrede endet mit Komma, auch wenn Parakeet keins oder einen Punkt setzte.
    text = re.sub(r"^((?:sehr geehrte|liebe|lieber|hallo)\b[^\n.,]*)[.]?\n\n", r"\1,\n\n",
                  text, flags=re.IGNORECASE)
    # Kurze Zeile nach einem Zeilenwechsel (Name unter dem Gruss) ohne den Punkt,
    # den Parakeet ans Ende jedes Stuecks setzt: "Gruessen\nMax Muster."
    # Nur nach EINEM Zeilenwechsel und ohne Umbrueche am Ende zu schlucken: Mit
    # "\.\s*$" fiel am 2026-09-16 der Absatz nach "\n\nSehr geehrte Damen und
    # Herren. Absatz." weg - und die Anrede lief in den ersten Satz.
    text = re.sub(r"((?<!\n)\n(?!\n)[^\n.?!]{1,40}?)\.[ \t]*$", r"\1", text)
    # "322,40 Cent" fuer "dreihundertzweiundzwanzig Euro und vierzig Cent"
    # (2026-09-16): Parakeet fasste den Betrag zusammen und behielt die falsche
    # Einheit. Ein Betrag mit zwei Nachkommastellen in Cent gibt es nicht.
    text = re.sub(r"\b(\d+,\d\d)\s+Cent\b", r"\1 Euro", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip(" ")


# PARAKEET-FUELLWOERTER (2026-09-16): Ein kurzes Geraeusch, das Vosk "apfel"
# nannte, schrieb Parakeet als "Yeah." in den Brief - bei Einzelwoertern kippt es
# ins Englische (so schon beim Einkaufszettel). Besteht Parakeets ganzes Stueck
# aus so einem Wort, faellt es weg.
PARAKEET_FUELLWOERTER = {"yeah", "yes", "yep", "okay", "ok", "oh", "uh", "um", "hmm", "mhm",
                         "mm", "ah", "so", "and", "the", "no", "hey", "hi", "wow", "thank you",
                         "thanks", "bye"}


ABSATZ_BEI_VOSK = {"absatz", "absätze", "abseits", "absender", "absenders"}
UMBRUCH_ALLEIN = {"absatz": "\n\n", "neuer absatz": "\n\n", "abseits": "\n\n",
                  "neue zeile": "\n", "neue zeil": "\n"}


def parakeet_fuellwort(text):
    return re.sub(r"[^\w ]", "", text).strip().lower() in PARAKEET_FUELLWOERTER


# ABGESCHNITTENE ENDUNGEN (2026-09-15/16): Parakeet schrieb "Rechn",
# "Nebenkostenabrechn", "aufführ" - Vosk hoerte im selben Stueck "rechnung",
# "aufführen". Ist ein Parakeet-Wort kein Vosk-Wort, aber der Anfang genau eines
# Vosk-Worts, dem nur eine uebliche Endung fehlt, kommt die Endung dazu.
#
# NUR WENN DIE RECHTSCHREIBPRUEFUNG DAS WORT NICHT KENNT: Ohne diese Bedingung
# wurde auf dem Pruefstand aus einem richtigen "Rechnung" ein "Rechnungen", weil
# Vosk dort die Mehrzahl hoerte. hunspell mit dem deutschen Woerterbuch ist
# auf dem Geraet (Paketliste desktop); fehlt es, wird nichts ergaenzt.
ENDUNGEN = ("ungen", "ung", "en", "n", "e", "er", "es", "em", "st", "t")


def unbekannte_woerter(woerter):
    if not woerter or not shutil.which("hunspell"):
        return set()
    try:
        ausgabe = subprocess.run(["hunspell", "-d", "de_DE", "-l"], input="\n".join(woerter),
                                 capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return set(ausgabe.split())


def endungen_ergaenzen(text, vosk_worte):
    vosk = {w.lower() for w in vosk_worte}
    kandidaten = {}
    for wort in set(re.findall(r"[A-Za-zÄÖÜäöüß]+", text)):
        klein = wort.lower()
        if len(klein) < 4 or klein in vosk:
            continue
        passend = {v for v in vosk if v.startswith(klein) and v[len(klein):] in ENDUNGEN}
        if len(passend) == 1:
            kandidaten[wort] = wort + passend.pop()[len(klein):]
    falsch = unbekannte_woerter(list(kandidaten))
    ersatz = {w: e for w, e in kandidaten.items() if w in falsch}
    if not ersatz:
        return text
    return re.sub(r"[A-Za-zÄÖÜäöüß]+", lambda m: ersatz.get(m.group(0), m.group(0)), text)


# ZAHLEN IM BRIEF (Stephan, 2026-09-17). Parakeet schrieb am 16.09. Ziffern
# ("31.8.2026", "322,40 Euro"), am 17.09. im selben Brief Woerter - und teils
# verstuemmelt: "Dreihund zweiundzwanzig Euro und vierzig Cent",
# "zweitaussechdzwanzig". Vosk hoerte dieselben Stellen sauber
# ("dreihundert zweiundzwanzig", "zweitausend sechsundzwanzig").
#
# ZWEI SCHRITTE:
#   1. VERSTUEMMELTE ZAHLWOERTER AUS VOSK: Parakeet- und Vosk-Woerter werden
#      ausgerichtet (difflib). Wo Parakeet ein Wort hat, das weder Zahl noch
#      bekanntes Wort ist, und Vosk an derselben Stelle nur Zahlwoerter, gelten
#      Vosks Zahlwoerter.
#   2. ZAHLWOERTER -> ZIFFERN nach den Schreibregeln fuer Briefe (DIN 5008):
#        Datum    "einunddreissigsten August zweitausendsechsundzwanzig" -> "31. August 2026"
#                 "ersten zehnten [zweitausendsechsundzwanzig]"            -> "01.10.[2026]"
#        Betrag   "dreihundertzweiundzwanzig Euro und vierzig Cent"       -> "322,40 Euro"
#        Uhrzeit  "zehn Uhr dreissig"                                     -> "10:30 Uhr"
#        sonst    ab 13 als Ziffern ("zweitausendsechsundzwanzig" -> "2026"),
#                 bis zwoelf bleiben Woerter ("drei Punkte") - so die Norm.
#   Ziffern-Daten von Parakeet ("31.8.2026") bekommen die fuehrenden Nullen.
#
# "ein", "eine", "einen" sind nie Zahlen - das Wort ist fast immer der Artikel.

EINER = {"null": 0, "eins": 1, "ein": 1, "eine": 1, "zwei": 2, "zwo": 2, "drei": 3, "vier": 4,
         "fünf": 5, "sechs": 6, "sieben": 7, "acht": 8, "neun": 9}
ZEHNER_FEST = {"zehn": 10, "elf": 11, "zwölf": 12, "dreizehn": 13, "vierzehn": 14,
               "fünfzehn": 15, "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19}
ZEHNER = {"zwanzig": 20, "dreißig": 30, "vierzig": 40, "fünfzig": 50, "sechzig": 60,
          "siebzig": 70, "achtzig": 80, "neunzig": 90}
MONATE = ("januar", "februar", "märz", "april", "mai", "juni", "juli", "august",
          "september", "oktober", "november", "dezember")
ORDINAL_UNREGELMAESSIG = {"erst": 1, "zweit": 2, "dritt": 3, "viert": 4, "fünft": 5, "sechst": 6,
                          "siebt": 7, "siebent": 7, "acht": 8, "neunt": 9, "zehnt": 10,
                          "elft": 11, "zwölft": 12}


def _unter_hundert(s):
    if s in ZEHNER_FEST:
        return ZEHNER_FEST[s]
    if s in ZEHNER:
        return ZEHNER[s]
    if s in EINER and s not in ("ein", "eine"):
        return EINER[s]
    m = re.fullmatch(r"(ein|zwei|drei|vier|fünf|sechs|sieben|acht|neun)und(\w+)", s)
    if m and m.group(2) in ZEHNER:
        return EINER[m.group(1)] + ZEHNER[m.group(2)]
    return None


def _unter_tausend(s):
    if "hundert" in s:
        vor, _, nach = s.partition("hundert")
        h = 1 if vor in ("", "ein", "eins") else EINER.get(vor)
        if h is None or vor == "null":
            return None
        if not nach:
            return h * 100
        rest = _unter_hundert(nach[3:] if nach.startswith("und") else nach)
        return None if rest is None else h * 100 + rest
    return _unter_hundert(s)


def grundzahl(s):
    """"dreihundertzweiundzwanzig" -> 322, "zweitausendsechsundzwanzig" -> 2026, sonst None."""
    s = s.lower()
    if "tausend" in s:
        vor, _, nach = s.partition("tausend")
        t = 1 if vor in ("", "ein", "eins") else _unter_tausend(vor)
        if t is None:
            return None
        if not nach:
            return t * 1000
        rest = _unter_tausend(nach[3:] if nach.startswith("und") else nach)
        return None if rest is None else t * 1000 + rest
    return _unter_tausend(s)


def ordnungszahl(s):
    """"einunddreissigsten" -> 31, "ersten" -> 1, "siebten" -> 7, sonst None.

    Alle Endungen werden probiert: "ersten" ist "ers"+"ten" (erst-), nicht
    "er"+"sten" - die kuerzeste Aufteilung waere falsch.
    """
    s = s.lower()
    for endung in ("sten", "ster", "stem", "stes", "ste", "ten", "ter", "tem", "tes", "te"):
        if not s.endswith(endung) or len(s) <= len(endung):
            continue
        stamm = s[:-len(endung)]
        if endung.startswith("s"):
            wert = grundzahl(stamm)
            if wert is not None and wert >= 20:
                return wert
        else:
            wert = ORDINAL_UNREGELMAESSIG.get(stamm + "t") or ORDINAL_UNREGELMAESSIG.get(stamm)
            if wert:
                return wert
            # "einunddreissigten" statt "-sten" (Parakeet, 2026-09-17)
            wert = grundzahl(stamm)
            if wert is not None and wert >= 20:
                return wert
    return None


WORT = re.compile(r"[A-Za-zÄÖÜäöüß]+|\d+(?:[.,]\d+)*")


def _ist_zahlwort(w):
    return w.lower() not in ("ein", "eine", "einen", "einer", "eines", "einem") and \
        (grundzahl(w) is not None or ordnungszahl(w) is not None)


def zahlwoerter_aus_vosk(text, vosk_worte):
    """Schritt 1: verstuemmelte Zahlwoerter bei Parakeet durch Vosks ersetzen."""
    import difflib
    stellen = [(m.start(), m.end(), m.group(0)) for m in WORT.finditer(text)]
    p = [w.lower() for _, _, w in stellen]
    v = [w.lower() for w in vosk_worte]
    # VERSCHLUCKTE BETRAGSTEILE (2026-09-17): Vosk "dreihundert zweiundzwanzig euro
    # und vierzig cent", Parakeet "dreihundert zweiundzwanzig Cent" - "Euro und
    # vierzig" fehlte. Fuegt Vosk nur Zahl- und Waehrungswoerter zwischen zwei
    # Zahl-/Waehrungswoertern ein, kommen sie in den Text.
    betrag = {"euro", "cent", "und", "komma"}
    opcodes = difflib.SequenceMatcher(None, p, v, autojunk=False).get_opcodes()
    for tag, i1, i2, j1, j2 in reversed(opcodes):
        if tag != "insert" or i1 == 0 or i1 >= len(stellen):
            continue
        neu = v[j1:j2]
        nachbarn = (p[i1 - 1], p[i1])
        if (all(_ist_zahlwort(w) or w in betrag for w in neu)
                and any(_ist_zahlwort(w) or w in ("euro", "cent") for w in neu)
                and all(_ist_zahlwort(w) or w in ("euro", "cent") for w in nachbarn)):
            text = text[:stellen[i1][0]] + " ".join(neu) + " " + text[stellen[i1][0]:]
            stellen = [(m.start(), m.end(), m.group(0)) for m in WORT.finditer(text)]
            p = [w.lower() for _, _, w in stellen]
    kandidaten = [(i1, i2, j1, j2) for tag, i1, i2, j1, j2
                  in difflib.SequenceMatcher(None, p, v, autojunk=False).get_opcodes()
                  if tag == "replace"
                  and all(_ist_zahlwort(w) for w in v[j1:j2])
                  and any(not _ist_zahlwort(w) and not w.isdigit() for w in p[i1:i2])]
    if not kandidaten:
        return text
    unbekannt = unbekannte_woerter([stellen[i][2] for i1, i2, _, _ in kandidaten
                                    for i in range(i1, i2)])
    for i1, i2, j1, j2 in reversed(kandidaten):
        woerter = [stellen[i][2] for i in range(i1, i2)]
        # Nur wenn das Parakeet-Wort kein echtes Wort ist ("Dreihund") - ein
        # richtiges Wort an der Stelle ("Forderung") bleibt stehen.
        if not all(w in unbekannt or _ist_zahlwort(w) for w in woerter):
            continue
        text = text[:stellen[i1][0]] + " ".join(v[j1:j2]) + text[stellen[i2 - 1][1]:]
    return text


def _zweistellig(n):
    return f"{n:02d}"


def zahlen_in_ziffern(text):
    """Schritt 2: Zahlwoerter nach Schreibregeln in Ziffern."""
    # Ziffern-Daten mit fuehrenden Nullen: "31.8.2026" -> "31.08.2026", "1.10." -> "01.10."
    text = re.sub(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})?(?!\d)",
                  lambda m: f"{int(m.group(1)):02d}.{int(m.group(2)):02d}.{m.group(3) or ''}",
                  text)
    stellen = [(m.start(), m.end(), m.group(0)) for m in WORT.finditer(text)]
    ergebnis = []   # (start, ende, ersatz)
    i = 0

    def zahl_ab(k):
        """Laengste Grundzahl ab Wort k (auch ueber mehrere Woerter), (wert, naechstes k)."""
        beste = None
        for ende in range(k + 1, min(k + 4, len(stellen)) + 1):
            teile = [stellen[x][2] for x in range(k, ende)]
            if any(t.lower() in ("ein", "eine", "einen") for t in teile):
                break
            wert = grundzahl("".join(teile).lower())
            if wert is None:
                break
            beste = (wert, ende)
        return beste

    while i < len(stellen):
        start, _, wort = stellen[i]
        klein = wort.lower()
        tag = ordnungszahl(wort)
        grund = zahl_ab(i) if klein not in ("ein", "eine", "einen") else None
        naechstes = stellen[i + 1][2].lower() if i + 1 < len(stellen) else ""
        # Datum mit Monatsnamen: Tag (Ordnungs- oder Grundzahl) + Monat [+ Jahr]
        if (tag or (grund and grund[1] == i + 1 and 1 <= grund[0] <= 31)) and naechstes in MONATE:
            tagzahl = tag or grund[0]
            ersatz = f"{tagzahl}. {stellen[i + 1][2].capitalize()}"
            ende = i + 2
            jahr = zahl_ab(ende) if ende < len(stellen) else None
            if jahr and 1000 <= jahr[0] <= 2999:
                ersatz += f" {jahr[0]}"
                ende = jahr[1]
            ergebnis.append((start, stellen[ende - 1][1], ersatz))
            i = ende
            continue
        # Datum mit Monat als Zahl und Jahr: "einunddreissig(sten) acht zweitausendsechsundzwanzig"
        # -> "31.08.2026" (2026-09-17). Das Jahr ist Pflicht - ohne es waere
        # "drei vier" schon ein Datum.
        tageswert = tag or (grund[0] if grund and grund[1] == i + 1 else None)
        if tageswert and 1 <= tageswert <= 31 and i + 1 < len(stellen):
            monat_wort = stellen[i + 1][2]
            monat_wert = ordnungszahl(monat_wort) or grundzahl(monat_wort.lower())
            jahr = zahl_ab(i + 2) if monat_wert and 1 <= monat_wert <= 12 and i + 2 < len(stellen) else None
            if jahr and 1000 <= jahr[0] <= 2999:
                ergebnis.append((start, stellen[jahr[1] - 1][1],
                                 f"{tageswert:02d}.{monat_wert:02d}.{jahr[0]}"))
                i = jahr[1]
                continue
        # Jahreszahl zweigeteilt gesprochen: "zwanzig fuenfundzwanzig" -> "2025"
        if grund and grund[1] == i + 1 and grund[0] in (19, 20) and i + 1 < len(stellen):
            zweiter = zahl_ab(i + 1)
            if zweiter and zweiter[1] == i + 2 and 10 <= zweiter[0] <= 99:
                ergebnis.append((start, stellen[i + 1][1], f"{grund[0]}{zweiter[0]:02d}"))
                i += 2
                continue
        # Datum aus zwei Ordnungszahlen: "ersten zehnten [zweitausendsechsundzwanzig]"
        monat = ordnungszahl(naechstes) if tag else None
        if tag and monat and 1 <= tag <= 31 and 1 <= monat <= 12:
            ersatz = f"{tag:02d}.{monat:02d}."
            ende = i + 2
            jahr = zahl_ab(ende) if ende < len(stellen) else None
            if jahr and 1000 <= jahr[0] <= 2999:
                ersatz += str(jahr[0])
                ende = jahr[1]
            ergebnis.append((start, stellen[ende - 1][1], ersatz))
            i = ende
            continue
        if grund:
            wert, ende = grund
            folge = [stellen[x][2].lower() for x in range(ende, min(ende + 4, len(stellen)))]
            # Betrag: "... Euro [und] vierzig [Cent]"
            if folge[:1] == ["euro"]:
                cent_ab = ende + 1 + (1 if folge[1:2] == ["und"] else 0)
                cent = zahl_ab(cent_ab) if cent_ab < len(stellen) else None
                if cent and cent[0] < 100 and (cent[1] >= len(stellen)
                                               or stellen[cent[1]][2].lower() in ("cent", "ct")
                                               or folge[1:2] != ["und"]):
                    stop = cent[1] + (1 if cent[1] < len(stellen)
                                      and stellen[cent[1]][2].lower() in ("cent", "ct") else 0)
                    ergebnis.append((start, stellen[stop - 1][1], f"{wert},{cent[0]:02d} Euro"))
                    i = stop
                    continue
                ergebnis.append((start, stellen[ende][1], f"{wert} Euro"))
                i = ende + 1
                continue
            # Uhrzeit: "zehn Uhr [dreissig]"
            if folge[:1] == ["uhr"] and wert <= 24:
                minuten = zahl_ab(ende + 1) if ende + 1 < len(stellen) else None
                if minuten and minuten[0] < 60:
                    ergebnis.append((start, stellen[minuten[1] - 1][1], f"{wert}:{minuten[0]:02d} Uhr"))
                    i = minuten[1]
                else:
                    ergebnis.append((start, stellen[ende][1], f"{wert} Uhr"))
                    i = ende + 1
                continue
            if wert > 12 or ende - i > 1:
                ergebnis.append((start, stellen[ende - 1][1], str(wert)))
                i = ende
                continue
        i += 1
    for start, ende, ersatz in reversed(ergebnis):
        text = text[:start] + ersatz + text[ende:]
    # "am 20.12." am Satzende: der Satzpunkt kam dazu - "20.12.." wird "20.12."
    return re.sub(r"(\d{2}\.\d{2}\.)\.", r"\1", text)


def parakeet_erkennen(erkenner, audio, worte):
    """Erkennt die Zeitspanne der Vosk-Woerter aus der Aufnahme dieser Epoche."""
    if not worte:
        return None
    von = max(0.0, worte[0].get("start", 0) - PARAKEET_RAND_S)
    bis = worte[-1].get("end", worte[-1].get("start", 0)) + PARAKEET_RAND_S
    a = int(von * ABTASTRATE) * 2
    b = min(len(audio), int(bis * ABTASTRATE) * 2)
    if b - a < ABTASTRATE // 5:
        return None
    werte = array.array("h", bytes(audio[a:b - (b - a) % 2]))
    strom = erkenner.create_stream()
    strom.accept_waveform(ABTASTRATE, [x / 32768.0 for x in werte])
    erkenner.decode_stream(strom)
    return strom.result.text.strip()


# MITSCHNITT FUER DEN PRUEFSTAND (Stephan, 2026-09-15: "Ja, einverstanden, bau
# den Pruefstand"). Jede Probe mit echter Stimme soll ein Pruef-Fall werden, der
# nach jeder Aenderung wieder durchlaeuft - statt einer Verbesserung, die an
# EINEM Versuch beurteilt wird.
#
# GESPEICHERT WIRD GENAU DAS, WAS DIE ERKENNER BEKOMMEN HABEN - jeder Block in
# Reihenfolge, inklusive des Vorlaufs nach Annas Antworten, ohne das, was waehrend
# ihrer Antworten verworfen wurde. Nur so laeuft die Wiederholung
# (scripts/dialos-pruefstand.py) durch dieselben Entscheidungen.
#
# NUR MIT SCHALTER UND NUR AUF DIE EXTERNE PLATTE, nie ins Repo: Es ist die
# Stimme des Sprechers. Fehlt der Ordner (Nutzerkonto, Platte nicht da), wird
# nichts aufgenommen.
MITSCHNITT_SCHALTER = os.path.join(os.path.expanduser("~"), ".config", "dialos", "pruefstand")
MITSCHNITT_ORDNER = "/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich/pruefstand/mitschnitte"


def mitschnitt_speichern(ton, epochen, kurz, name, protokoll_ab, ergebnis, pfad, quelle=None,
                         parakeet=False):
    try:
        import wave
        os.makedirs(MITSCHNITT_ORDNER, exist_ok=True)
        stamm = os.path.join(MITSCHNITT_ORDNER, time.strftime("%Y-%m-%d-%H%M%S") + f"-{name}")
        with wave.open(stamm + ".wav", "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(ABTASTRATE)
            w.writeframes(bytes(ton))
        try:
            with open(PROTOKOLL, encoding="utf-8") as f:
                f.seek(protokoll_ab)
                protokoll = f.read()
        except OSError:
            protokoll = ""
        with open(stamm + ".json", "w", encoding="utf-8") as f:
            json.dump({"name": name, "epochen_ab_s": [e / (2 * ABTASTRATE) for e in epochen],
                       "kurze_bloecke": kurz, "quelle": quelle,
                       "dauer_s": len(ton) / (2 * ABTASTRATE), "ergebnis": ergebnis,
                       "datei": pfad, "parakeet": parakeet,
                       "protokoll": protokoll}, f, ensure_ascii=False, indent=1)
        melde(f"  Mitschnitt fuer den Pruefstand: {stamm}.wav")
    except Exception as fehler:
        melde(f"  Mitschnitt nicht gespeichert: {fehler}")


# EMPFAENGER-DIALOG VOR DEM BRIEF (Stephan, 2026-09-17: "Gefuehrter Dialog",
# "Ja, erst suchen"). Nach dem Laden der Modelle, vor "Ich schreibe mit":
#
#   "An wen geht der Brief?"  -> Name oder Firma
#       im Thunderbird-Adressbuch gefunden -> Adresse vorlesen, "ja oder nein"
#       sonst / "nein" -> Strasse und Hausnummer, Postleitzahl und Ort, Land
#   Adresse vorlesen (Postleitzahl Ziffer fuer Ziffer), "Stimmt das?"
#   neue Adresse -> Kontakt in Thunderbird (dialos-empfaenger.py)
#
# JEDE ANTWORT HOEREN BEIDE ERKENNER: Vosk bestimmt, wann die Antwort zu Ende
# ist (eine Sekunde Stille nach dem letzten Wort), Parakeet schreibt den Text -
# Namen und Strassen gross und richtig. Ja/Nein erkennt das kleine Modell mit
# einer Grammatik aus genau diesen zwei Woertern (wie die Rueckfragen in
# dialos-notiz.py). Wer nichts sagt oder "ohne Empfaenger", bekommt den Brief
# ohne Anschrift - das Diktat faellt nie wegen des Dialogs aus.
EMPFAENGER_FRAGEN = True        # der Pruefstand schaltet ab: seine Aufnahmen haben keinen Dialog
EMPFAENGER_SKRIPT = "/usr/local/bin/dialos-empfaenger.py"
ANSAGE_EMPFAENGER = ("An wen geht der Brief? Sage den Namen oder die Firma. "
                     "Wenn es keinen Empfänger gibt, sage: ohne Empfänger. "
                     "Du kannst jederzeit sagen: abbrechen, oder: von vorne.")
ANSAGE_STRASSE = "Wie heißen Straße und Hausnummer?"
ANSAGE_PLZ_ORT = "Wie heißen Postleitzahl und Ort?"
ANSAGE_LAND_FREI = "In welchem Land?"
ANSAGE_JA_NEIN_NOCHMAL = "Das habe ich nicht verstanden. Sage bitte ja oder nein."
ANSAGE_OHNE_EMPFAENGER = "Ich schreibe den Brief ohne Empfänger."
ANTWORT_ZEITGRENZE_S = 12.0     # bis die Antwort BEGINNT
ANTWORT_NACHLAUF_S = 1.2        # Stille nach dem letzten Wort, bis sie zu Ende ist
OHNE_EMPFAENGER = re.compile(r"(?i)\b(ohne|kein\w*)\s+empf")


# JEDERZEIT ABBRECHEN ODER NEU BEGINNEN (Stephan, 2026-09-17: "wenn Gesobau nicht
# verstanden wird, dann habe ich keinen Einfluss, das noch mal zu aendern. Und ich
# kann den Brief nicht neu starten oder das Diktat einfach beenden!"). Sein
# "Diktat beenden" landete als Strassenname "Um die Tat beenden" im Dialog. Jetzt
# prueft JEDE Antwort - frei, ja/nein, Buchstaben - zuerst diese Saetze.
class DialogAbbruch(Exception):
    pass


class DialogNeustart(Exception):
    pass


DIALOG_ABBRUCH = re.compile(r"(?i)\b(?:diktat|brief)\s+(?:beenden|abbrechen)\b|\babbrechen\b")
DIALOG_NEUSTART = re.compile(r"(?i)\bvon\s+vorn(?:e)?\b|\bneu\s+anfangen\b")
STEUERWOERTER = ["abbrechen", "diktat", "brief", "beenden", "von", "vorne"]
ABBRUCH = "abbruch"
ANSAGE_ABBRUCH = "Ich breche den Brief ab."
ANSAGE_NEUSTART = "Gut, noch einmal von vorne."


def steuerung_pruefen(*texte):
    for text in texte:
        if text and DIALOG_ABBRUCH.search(text):
            raise DialogAbbruch()
        if text and DIALOG_NEUSTART.search(text):
            raise DialogNeustart()


def antwort_hoeren(frage, prozess, modell, parakeet):
    """Stellt die Frage; liefert (Text, Vosk-Text) - Text von Parakeet, sonst Vosk - oder ("", "")."""
    import vosk
    vorrat = sprechen_bei_offener_aufnahme(frage, prozess)
    erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE)
    erkenner.SetWords(True)
    audio = bytearray()
    worte, texte = [], []
    beginn_bis = time.time() + ANTWORT_ZEITGRENZE_S
    ende = None
    while True:
        jetzt = time.time()
        if (ende is None and jetzt > beginn_bis) or (ende is not None and jetzt > ende):
            break
        if vorrat:
            block, vorrat = vorrat[:4000], vorrat[4000:]
        else:
            block = prozess.stdout.read(4000)
        if not block:
            break
        audio.extend(block)
        if erkenner.AcceptWaveform(block):
            ergebnis = json.loads(erkenner.Result())
            if ergebnis.get("text", "").strip():
                texte.append(ergebnis["text"])
                worte += ergebnis.get("result", [])
                ende = time.time() + ANTWORT_NACHLAUF_S
        elif json.loads(erkenner.PartialResult()).get("partial", "").strip():
            # Es wird noch gesprochen - die Antwort ist nicht zu Ende.
            ende = time.time() + ANTWORT_NACHLAUF_S + 2.0
    if not texte:
        schluss = json.loads(erkenner.FinalResult())
        if schluss.get("text", "").strip():
            texte.append(schluss["text"])
            worte += schluss.get("result", [])
    vosk_text = " ".join(texte).strip()
    if not vosk_text:
        melde(f"  Empfaenger-Dialog: keine Antwort auf {frage[:30]!r}")
        return "", ""
    steuerung_pruefen(vosk_text)
    text = vosk_text
    if parakeet is not None and worte:
        try:
            roh = parakeet_erkennen(parakeet, audio, worte)
            if roh and not parakeet_fuellwort(roh):
                text = roh
        except Exception as fehler:
            melde(f"  Empfaenger-Dialog: Parakeet-Fehler ({fehler})")
    text = woerterbuch_anwenden(komposita_nach_vosk(re.sub(r"[.!?]+$", "", text.strip()), vosk_text))
    melde(f"  Empfaenger-Dialog: Vosk {vosk_text!r}, geschrieben {text!r}")
    steuerung_pruefen(text)
    return text, vosk_text


def komposita_nach_vosk(text, vosk_text):
    """"Muster Strasse 5a" -> "Musterstrasse 5a", wenn Vosk das Wort zusammen hoerte.

    Parakeet trennt zusammengesetzte Strassennamen (Simulation 2026-09-17), Vosk
    kennt sie als ein Wort. Zwei Parakeet-Woerter, die zusammen genau ein
    Vosk-Wort ergeben, werden verbunden. "Berliner Strasse" bleibt getrennt,
    denn Vosk schreibt es ebenfalls getrennt.
    """
    vosk = {w.lower() for w in vosk_text.split()}
    woerter = text.split()
    i = 0
    while i < len(woerter) - 1:
        zusammen = woerter[i] + woerter[i + 1].lower()
        if zusammen.lower() in vosk and woerter[i].lower() not in vosk:
            woerter[i:i + 2] = [zusammen]
        else:
            i += 1
    return " ".join(woerter)


def auswahl_hoeren(frage, prozess, modell_klein, optionen, nochmal):
    """Eine der optionen (Woerter) - zwei Versuche - oder None. Steuerwoerter gelten immer."""
    import vosk
    grammatik = json.dumps(list(optionen) + STEUERWOERTER + ["[unk]"], ensure_ascii=False)
    for versuch in (1, 2):
        vorrat = sprechen_bei_offener_aufnahme(frage if versuch == 1 else nochmal, prozess)
        erkenner = vosk.KaldiRecognizer(modell_klein, ABTASTRATE, grammatik)
        bis = time.time() + 8.0
        while time.time() < bis:
            if vorrat:
                block, vorrat = vorrat[:4000], vorrat[4000:]
            else:
                block = prozess.stdout.read(4000)
            if not block:
                break
            if not erkenner.AcceptWaveform(block):
                continue
            worte = json.loads(erkenner.Result()).get("text", "").split()
            if not worte:
                continue
            melde(f"  Empfaenger-Dialog: Antwort {worte!r}")
            steuerung_pruefen(" ".join(worte))
            if "[unk]" in worte:
                continue
            treffer = [o for o in optionen if o in worte]
            if len(treffer) == 1:
                return treffer[0]
    return None


def ja_oder_nein_hoeren(frage, prozess, modell_klein):
    """True, False oder None."""
    antwort = auswahl_hoeren(frage, prozess, modell_klein, ("ja", "nein"), ANSAGE_JA_NEIN_NOCHMAL)
    return None if antwort is None else antwort == "ja"


# BUCHSTABIEREN (Stephan, 2026-09-17, nachdem "Gesobau" als "G so bau" im Brief
# stand - und beim Vorlesen richtig klang). Nach einem NEUEN Namen bietet DialOS
# an, ihn zu buchstabieren; stimmt die Schreibweise nicht, spricht der Nutzer die
# Buchstaben ein. Erkannt mit dem kleinen Modell und einer Grammatik nur aus
# Buchstaben. GEMESSEN (Piper -> Vosk, 2026-09-17): Buchstabennamen ("Ge", "E",
# "Es") 15 von 26 richtig, das Buchstabieralphabet ("Gustav", "Emil", "Samuel")
# 26 von 26. Angesagt wird deshalb das Alphabet; die Buchstabennamen gelten
# trotzdem, falls jemand sie sagt. Nicht im Wortschatz sind "ef", "vau",
# "ix", "eszett" - dafuer gelten "f", "v", "x", "friedrich", "viktor", "xaver"
# und "scharfes es".
BUCHSTABEN_HOEREN = {
    "a": "a", "anton": "a", "be": "b", "berta": "b", "ce": "c", "ze": "c", "cäsar": "c",
    "de": "d", "dora": "d", "e": "e", "emil": "e", "f": "f", "friedrich": "f", "ge": "g",
    "gustav": "g", "ha": "h", "heinrich": "h", "i": "i", "ida": "i", "jot": "j", "julius": "j",
    "ka": "k", "kaufmann": "k", "el": "l", "ludwig": "l", "em": "m", "martha": "m", "en": "n",
    "nordpol": "n", "o": "o", "otto": "o", "pe": "p", "paula": "p", "ku": "q", "quelle": "q",
    "er": "r", "richard": "r", "es": "s", "samuel": "s", "te": "t", "theodor": "t", "u": "u",
    "ulrich": "u", "v": "v", "viktor": "v", "we": "w", "wilhelm": "w", "x": "x", "xaver": "x",
    "ypsilon": "y", "zett": "z", "zeppelin": "z", "zacharias": "z", "ä": "ä", "ö": "ö", "ü": "ü",
    "leerzeichen": " ", "bindestrich": "-", "punkt": ".",
}
# Vorgelesen wird ebenfalls mit dem Alphabet: "Berta" und "Paula" verwechselt
# niemand, "Be" und "Pe" schon.
BUCHSTABEN_SPRECHEN = {
    "a": "Anton", "b": "Berta", "c": "Cäsar", "d": "Dora", "e": "Emil", "f": "Friedrich",
    "g": "Gustav", "h": "Heinrich", "i": "Ida", "j": "Julius", "k": "Kaufmann", "l": "Ludwig",
    "m": "Martha", "n": "Nordpol", "o": "Otto", "p": "Paula", "q": "Quelle", "r": "Richard",
    "s": "Samuel", "t": "Theodor", "u": "Ulrich", "v": "Viktor", "w": "Wilhelm", "x": "Xaver",
    "y": "Ypsilon", "z": "Zacharias", "ä": "Ä", "ö": "Ö", "ü": "Ü", "ß": "scharfes S",
    " ": "Leerzeichen", "-": "Bindestrich", ".": "Punkt",
}
ANSAGE_BUCHSTABIEREN = ("Buchstabiere den Namen mit dem Buchstabieralphabet, zum Beispiel: "
                        "Gustav, Emil, Samuel. Für ein Leerzeichen sage Leerzeichen, für einen "
                        "Fehler sage zurück. Am Ende sage: fertig.")


def buchstabiert(name):
    """"GESOBAU" -> "Gustav. Emil. Samuel. ..." - Satzpunkte, weil nur sie bei Piper Pausen machen."""
    return ". ".join(BUCHSTABEN_SPRECHEN[z] for z in name.lower() if z in BUCHSTABEN_SPRECHEN) + "."


def buchstaben_hoeren(prozess, modell_klein):
    """Buchstaben bis "fertig" (oder 10 s Stille). Der Name mit grossen Wortanfaengen, oder ""."""
    import vosk
    vorrat = sprechen_bei_offener_aufnahme(ANSAGE_BUCHSTABIEREN, prozess)
    woerter = list(BUCHSTABEN_HOEREN) + ["scharfes", "fertig", "zurück", "abbrechen", "[unk]"]
    erkenner = vosk.KaldiRecognizer(modell_klein, ABTASTRATE, json.dumps(woerter, ensure_ascii=False))
    zeichen = []
    bis = time.time() + 15.0
    ende_gesamt = time.time() + 90.0
    fertig = False
    while not fertig and time.time() < min(bis, ende_gesamt):
        if vorrat:
            block, vorrat = vorrat[:4000], vorrat[4000:]
        else:
            block = prozess.stdout.read(4000)
        if not block:
            break
        if not erkenner.AcceptWaveform(block):
            continue
        gehoert = json.loads(erkenner.Result()).get("text", "").split()
        if not gehoert:
            continue
        bis = time.time() + 10.0
        melde(f"  Buchstabieren: {gehoert!r}")
        if "abbrechen" in gehoert:
            raise DialogAbbruch()
        i = 0
        while i < len(gehoert):
            w = gehoert[i]
            if w == "fertig":
                fertig = True
                break
            if w == "zurück" and zeichen:
                zeichen.pop()
            elif w == "scharfes" and i + 1 < len(gehoert) and gehoert[i + 1] == "es":
                zeichen.append("ß")
                i += 1
            elif w in BUCHSTABEN_HOEREN:
                zeichen.append(BUCHSTABEN_HOEREN[w])
            i += 1
    name = "".join(zeichen).strip()
    return " ".join(t[:1].upper() + t[1:] for t in name.split(" ") if t)


def name_erfragen(prozess, modell, modell_klein, parakeet, em):
    """Name bis zur Bestaetigung. Liefert ein Kontakt-dict, {"name": ...} oder None.

    "Der Name ist: X. Stimmt das? Sage ja, nein oder buchstabieren." Bei "nein"
    wird der Name neu gesagt, bei "buchstabieren" liest DialOS ihn im Alphabet
    vor und laesst ihn bei Bedarf buchstabieren (Stephan, 2026-09-17: sein "nein"
    auf "Soll ich ihn buchstabieren?" meinte "der Name stimmt nicht").
    """
    frage = ANSAGE_EMPFAENGER
    for _ in range(4):
        text, vosk_text = antwort_hoeren(frage, prozess, modell, parakeet)
        if not text:
            return None
        if OHNE_EMPFAENGER.search(text) or OHNE_EMPFAENGER.search(vosk_text):
            return None
        if re.match(r"(?i)\s*buchstab", vosk_text):
            name = buchstaben_hoeren(prozess, modell_klein)
            if not name:
                frage = "Sage den Namen noch einmal. Du kannst auch sagen: buchstabieren."
                continue
        else:
            name = text[:1].upper() + text[1:]
        # Kontakte mit beiden Erkennungen suchen: "Gesobau" kam als "wieso bau"
        # (Vosk) und "Gilball" (Parakeet) an. Ein falscher Treffer schadet nicht -
        # er wird ja erst nach "ja" genommen.
        gefunden = []
        for such in (name, vosk_text):
            for k in em.suchen(such):
                if k not in gefunden:
                    gefunden.append(k)
        for k in gefunden[:2]:
            kontakt = {"name": k["name"] or k["firma"], "zusatz": k["zusatz"],
                       "strasse": k["strasse"], "plz": k["plz"], "ort": k["ort"], "land": k["land"]}
            antwort = ja_oder_nein_hoeren(f"In den Kontakten steht: {em.gesprochen(kontakt)}. "
                                          "Ist das der Empfänger? Sage ja oder nein.",
                                          prozess, modell_klein)
            if antwort:
                melde(f"  Empfaenger aus den Kontakten: {kontakt!r}")
                return kontakt
            if antwort is None:
                return None
        while True:
            wahl = auswahl_hoeren(f"Der Name ist: {name}. Stimmt das? Sage ja, nein oder buchstabieren.",
                                  prozess, modell_klein, ("ja", "nein", "buchstabieren"),
                                  "Das habe ich nicht verstanden. Sage ja, nein oder buchstabieren.")
            if wahl == "ja":
                return {"name": name}
            if wahl is None:
                return None
            if wahl == "nein":
                frage = "Sage den Namen noch einmal. Du kannst auch sagen: buchstabieren."
                break
            stimmt = ja_oder_nein_hoeren(f"Ich buchstabiere: {buchstabiert(name)} "
                                         "Stimmt die Schreibweise? Sage ja oder nein.",
                                         prozess, modell_klein)
            if stimmt:
                return {"name": name}
            if stimmt is None:
                return None
            neu = buchstaben_hoeren(prozess, modell_klein)
            melde(f"  Name buchstabiert: {neu!r}")
            if neu:
                name = neu
    return None


def empfaenger_erfragen(quelle, modell, modell_klein, parakeet):
    """Der Dialog. Liefert ein Empfaenger-dict, None (ohne Empfaenger) oder ABBRUCH."""
    em = holen(EMPFAENGER_SKRIPT, "empfaenger")
    if em is None or modell_klein is None:
        melde("  Empfaenger-Dialog nicht moeglich (dialos-empfaenger.py oder kleines Modell fehlt)")
        return None
    modul, daten = persoenliche_daten()
    eigenes_land = daten.get("land", "") if daten else ""
    import types
    zahlen = types.SimpleNamespace(grundzahl=grundzahl)
    prozess = aufnahme_starten(quelle)
    try:
        for _ in range(3):
            try:
                ergebnis = name_erfragen(prozess, modell, modell_klein, parakeet, em)
                if ergebnis is None:
                    sprich(ANSAGE_OHNE_EMPFAENGER)
                    return None
                if "strasse" in ergebnis:
                    return ergebnis
                name = ergebnis["name"]
                # KEINE ANTWORT = OHNE EMPFAENGER (Simulation 2026-09-17): sonst fragte
                # der Dialog bei Stille stur weiter, eine halbe Minute ins Leere.
                gehoert, _ = antwort_hoeren(ANSAGE_STRASSE, prozess, modell, parakeet)
                if not gehoert:
                    sprich(ANSAGE_OHNE_EMPFAENGER)
                    return None
                strasse = em.strasse_richten(gehoert, zahlen)
                land = eigenes_land
                if eigenes_land:
                    im_land = ja_oder_nein_hoeren(f"Liegt die Adresse in {eigenes_land}? "
                                                  "Sage ja oder nein.", prozess, modell_klein)
                    if im_land is None:
                        sprich(ANSAGE_OHNE_EMPFAENGER)
                        return None
                    if im_land is False:
                        land, _ = antwort_hoeren(ANSAGE_LAND_FREI, prozess, modell, parakeet)
                        land = land[:1].upper() + land[1:]
                gehoert, _ = antwort_hoeren(ANSAGE_PLZ_ORT, prozess, modell, parakeet)
                if not gehoert:
                    sprich(ANSAGE_OHNE_EMPFAENGER)
                    return None
                plz, ort = em.plz_ort_richten(gehoert, zahlen, em.plz_laenge(land))
                neu = {"name": name, "zusatz": "", "strasse": strasse, "plz": plz, "ort": ort,
                       "land": land}
                antwort = ja_oder_nein_hoeren(f"Der Brief geht an: {em.gesprochen(neu)}. "
                                              "Stimmt das? Sage ja oder nein.", prozess, modell_klein)
                if antwort:
                    melde(f"  Empfaenger neu: {neu!r}")
                    try:
                        em.eintragen(neu)
                    except Exception as fehler:
                        melde(f"  Kontakt nicht angelegt: {fehler}")
                    return neu
                if antwort is None:
                    sprich(ANSAGE_OHNE_EMPFAENGER)
                    return None
                raise DialogNeustart()
            except DialogNeustart:
                melde("  Empfaenger-Dialog: von vorne")
                sprich(ANSAGE_NEUSTART)
        sprich(ANSAGE_OHNE_EMPFAENGER)
        return None
    except DialogAbbruch:
        melde("  Empfaenger-Dialog: Brief abgebrochen")
        sprich(ANSAGE_ABBRUCH)
        return ABBRUCH
    finally:
        try:
            prozess.terminate()
        except Exception:
            pass


def diktat_fuehren(zweck, name, quelle):
    import vosk
    vosk.SetLogLevel(-1)
    # 11,6 s Ladezeit - deshalb VOR der Bereitschaftsansage laden und die
    # Wartezeit ansagen, statt den Nutzer in die Stille sprechen zu lassen.
    melde(f"=== Diktat gestartet ({zweck}, {name}), Quelle {quelle} ===")
    sprich(ANSAGE_LADEN)
    # BEIDE MODELLE GLEICHZEITIG LADEN: Nacheinander dauerte es am 2026-09-16
    # 33 s bis "Ich schreibe mit" (Vosk 12 s, Parakeet 17 s von der externen
    # Platte). Vosk laedt ueber cffi und gibt dabei den Python-Lock frei, beide
    # laufen also wirklich nebeneinander. Brief und Notizen (Stephan, 2026-09-15:
    # "Ja, Notizen auch zu Parakeet") - beides sind ganze Saetze. Der
    # Einkaufszettel bleibt bei Vosk: Einzelne Waren traf Vosk 16 von 20,
    # Parakeet 11 (es kippte bei Einzelwoertern ins Englische).
    parakeet_geladen = {}
    parakeet_faden = None
    if name not in LISTEN_ZIELE and not os.path.exists(PARAKEET_AUS):
        parakeet_faden = threading.Thread(
            target=lambda: parakeet_geladen.update(erkenner=parakeet_laden()), daemon=True)
        parakeet_faden.start()
    elif name not in LISTEN_ZIELE:
        melde(f"  PARAKEET: abgeschaltet ({PARAKEET_AUS}), Vosk schreibt")
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

    # Geprueft wird der Messordner (erkenner-vergleich), nicht "pruefstand" darin -
    # den legt erst der erste Mitschnitt an. So stand es zuerst, und Stephans
    # erste Aufnahme am 2026-09-15 (15:20) wurde deshalb nicht gespeichert.
    mitschnitt = (bytearray() if os.path.exists(MITSCHNITT_SCHALTER)
                  and os.path.isdir(os.path.dirname(os.path.dirname(MITSCHNITT_ORDNER)))
                  else None)
    if os.path.exists(MITSCHNITT_SCHALTER) and mitschnitt is None:
        melde("  ACHTUNG: Mitschnitt eingeschaltet, aber Messordner fehlt - keine Aufnahme")
    mitschnitt_epochen = [0]
    mitschnitt_kurz = []
    try:
        protokoll_ab = os.path.getsize(PROTOKOLL)
    except OSError:
        protokoll_ab = 0
    if parakeet_faden is not None:
        parakeet_faden.join()
    parakeet = parakeet_geladen.get("erkenner")
    empfaenger = None
    if name in BRIEF_ZIELE and EMPFAENGER_FRAGEN:
        try:
            empfaenger = empfaenger_erfragen(quelle, modell, modell_klein, parakeet)
        except Exception as fehler:
            melde(f"  Empfaenger-Dialog abgebrochen: {fehler}")
            empfaenger = None
        if empfaenger == ABBRUCH:
            # "abbrechen" oder "Diktat beenden" im Dialog: kein Brief, nichts geschrieben.
            return 0
    # Aufnahme der aktuellen Epoche - gleiche Zeitachse wie die Vosk-Woerter.
    epoche_audio = bytearray()

    def frei_text(worte, vosk_text):
        """Text fuer den Brief: Parakeets, falls eingeschaltet, sonst Vosks."""
        if parakeet is None:
            return vosk_text
        if not worte:
            # Rueckfall: Die Aeusserung gilt als fertig
            # gesetzt, also die gesprochenen Satzzeichen hier umsetzen.
            return satzzeichen_setzen(vosk_text)
        t0 = time.time()
        try:
            roh = parakeet_erkennen(parakeet, epoche_audio, worte)
        except Exception as fehler:
            melde(f"  PARAKEET: Fehler, Vosk-Text bleibt ({fehler})")
            return satzzeichen_setzen(vosk_text)
        if not roh:
            return satzzeichen_setzen(vosk_text)
        melde(f"  VOSK:        {vosk_text!r}")
        melde(f"  PARAKEET:    {roh!r} ({time.time()-t0:.2f} s)")
        if parakeet_fuellwort(roh):
            melde(f"  PARAKEET: nur Fuellwort {roh!r} - Stueck faellt weg")
            return ""
        # NUR EIN UMBRUCH GESPROCHEN (2026-09-17): Vosk hoerte "absatz", Parakeet
        # machte daraus "Upsets." - der Absatz kam, das Wort blieb im Brief.
        # Besteht Vosks ganzes Stueck aus einem Umbruch-Befehl, gilt nur dieser.
        nur_umbruch = UMBRUCH_ALLEIN.get(" ".join(vosk_text.lower().split()))
        if nur_umbruch:
            melde(f"  nur Umbruch laut Vosk ({vosk_text!r}), Parakeet {roh!r} verworfen")
            return nur_umbruch
        ergaenzt = endungen_ergaenzen(roh, vosk_text.split())
        if ergaenzt != roh:
            melde(f"  Endungen nach Vosk ergaenzt: {ergaenzt!r}")
        mit_zahlen = zahlen_in_ziffern(zahlwoerter_aus_vosk(ergaenzt, vosk_text.split()))
        if mit_zahlen != ergaenzt:
            melde(f"  Zahlen: {mit_zahlen!r}")
        text = parakeet_natuerlich(mit_zahlen)
        # ABSATZ, DEN NUR VOSK HOERTE (2026-09-16, 14:36): Stephan sagte "Absatz
        # Diesen Betrag ...", Vosk hoerte "absender diesen betrag", Parakeet liess
        # das Wort ganz weg - und der Absatz fehlte. Vosk schreibt dieses "Absatz"
        # am Stueckanfang oft als "absender(s)"/"abseits"; steht das bei Parakeet
        # nicht als eigenes Wort da, gilt es als Absatz.
        erstes = vosk_text.split()[0].lower() if vosk_text.split() else ""
        if (erstes in ABSATZ_BEI_VOSK and text and not text.startswith("\n")
                and not re.match(r"(?i)\W*" + erstes + r"\b", text)):
            melde(f"  Absatz nach Vosk ({erstes!r} am Stueckanfang, bei Parakeet fehlt es)")
            text = "\n\n" + text
        return text or satzzeichen_setzen(vosk_text)

    prozess = None
    gesammelt = []
    aeusserungen = Aeusserungen(name)
    if parakeet is not None:
        aeusserungen.umschreiben = lambda worte: frei_text(
            worte, " ".join(w["word"] for w in worte))
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
        rauschen = Rauschboden()
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
            if mitschnitt is not None:
                # Kurze Bloecke (Rest des Vorlaufs) merken - die Wiederholung
                # liefert dieselben Stuecke, Vosk schneidet sonst minimal anders.
                if len(block) != 4000:
                    mitschnitt_kurz.append([len(mitschnitt), len(block)])
                mitschnitt.extend(block)
            pegel_verlauf.append(pegel_puffer[-1])
            zeitverlauf.append(pegel_puffer[-1])
            rauschen.neu(pegel_puffer[-1])
            text_schwelle = rauschen.schwelle(PEGEL_SCHWELLE)
            ruhe_schwelle = rauschen.schwelle(BEFEHL_RUHE_SCHWELLE)
            if parakeet is not None:
                epoche_audio.extend(block)

            # EIN BEFEHL WARTET AUF SEINE RUHE DANACH. Erst wenn die halbe
            # Sekunde nach dem letzten Befehlswort aufgenommen ist, wird
            # entschieden - bis dahin laeuft alles normal weiter, nichts geht
            # verloren.
            if (befehl_offen and len(zeitverlauf) * BLOCK_S
                    >= befehl_offen["ende"] + BEFEHL_RAND_S + BEFEHL_RUHE_DANACH_S):
                b, befehl_offen = befehl_offen, None
                if not ruhig(zeitverlauf, b["ende"] + BEFEHL_RAND_S,
                             b["ende"] + BEFEHL_RAND_S + BEFEHL_RUHE_DANACH_S, ruhe_schwelle):
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
                        del epoche_audio[:]
                        if mitschnitt is not None:
                            mitschnitt_epochen.append(len(mitschnitt))
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
                                   anfang - BEFEHL_RAND_DAVOR_S, ruhe_schwelle):
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
                    if mittel < text_schwelle:
                        melde(f"  Schluss {gehoert!r} verworfen - zu leise "
                              f"(Pegel {mittel:.0f} unter {text_schwelle:.0f})")
                        continue
                    # KEIN SCHLUSS OHNE SPRECHPAUSE DAVOR - siehe pause_davor().
                    # Das ist die Regel, die die vier vorherigen Reparaturen nicht
                    # geschafft haben: Bruchstuecke entstehen MITTEN im Redefluss, ein
                    # echtes 'Diktat beenden' folgt auf eine Pause.
                    if not pause_davor(pegel_verlauf, schwelle=text_schwelle):
                        melde(f"  Schluss {gehoert!r} verworfen - keine Sprechpause davor "
                              f"(Pegel {mittel:.0f}, Pausen-Schwelle {text_schwelle:.0f})")
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
                    if mittel >= text_schwelle:
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
            if mittel < text_schwelle:
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
            aeusserungen.hinzu(epoche, worte_frei, frei_text(worte_frei, text))
    except KeyboardInterrupt:
        pass
    finally:
        if prozess:
            try:
                prozess.terminate()
            except Exception:
                pass

    aeusserungen.schlussrest_entfernen()
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
    rest_worte = []
    try:
        ergebnis_rest = json.loads(erkenner.FinalResult())
        rest = ergebnis_rest.get("text", "").strip()
        rest_worte = ergebnis_rest.get("result", [])
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
            rest_worte = rest_worte[:len(behalten)]
    except Exception as fehler:
        melde(f"  Resttext nicht lesbar: {fehler}")
    if rest:
        worte = rest.split()
        while worte and worte[-1] in SCHLUSS_WOERTER:
            worte.pop()
        rest = " ".join(worte).strip()
        rest_worte = rest_worte[:len(worte)]
        if rest and len(rest_worte) == len(worte):
            rest = frei_text(rest_worte, rest)
    if rest:
        melde(f"  Resttext aus dem Erkenner: {rest!r}")
        gesammelt += aeusserung_verarbeiten(name, rest, parakeet is not None)
    gesammelt = zusammenziehen(gesammelt)

    if not gesammelt:
        if mitschnitt is not None:
            mitschnitt_speichern(mitschnitt, mitschnitt_epochen, mitschnitt_kurz, name, protokoll_ab, [], None, quelle,
                                 parakeet is not None)
        sprich(ANSAGE_LEER)
        return 0

    pfad = (brief_schreiben(gesammelt, empfaenger) if name in BRIEF_ZIELE
            else notiz_schreiben(name, gesammelt))
    melde(f"  geschrieben nach {pfad}")
    if mitschnitt is not None:
        mitschnitt_speichern(mitschnitt, mitschnitt_epochen, mitschnitt_kurz, name, protokoll_ab, gesammelt, pfad, quelle,
                             parakeet is not None)
    # SAETZE ZAEHLEN, NICHT STUECKE (2026-09-15): Der Brief mit elf Saetzen
    # meldete "3 Sätze" - gezaehlt wurden die Stuecke der Erkennung.
    anzahl = len(gesammelt)
    if name in BRIEF_ZIELE:
        text = " ".join(gesammelt).strip()
        ende = [i for i in satzenden(text) if text[i] != "\n"]
        anzahl = len(ende) + (0 if ende and ende[-1] == len(text) - 1 else 1)
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
