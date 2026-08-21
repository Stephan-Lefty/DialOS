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

import json
import os
import re
import subprocess
import sys
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


def ist_schluss(gehoert):
    """Beendet diese Aeusserung das Diktat?

    NICHT exakte Uebereinstimmung - das war der Fehler vom 2026-08-18. Der
    Nutzer sagte "diktat beenden", der Erkenner lieferte nur 'beenden', und
    die exakte Bedingung wies es ab. Ergebnis: ein sieben Minuten langes
    Diktat, das den ganzen Raum mitschrieb und nur von Hand zu stoppen war.

    Die neue Bedingung ist aus den Messdaten desselben Laufs abgeleitet. Der
    Schluss-Erkenner lieferte in sieben Minuten Dauergerede genau zwei
    Ergebnisse ausser "[unk]", und beide waren 'beenden' - jeweils als
    Stephan es gesagt hat. Ein falsches Ergebnis kam NIE zustande.

    Deshalb: Es genuegt, wenn die Aeusserung
      - "beenden" enthaelt,
      - ausser Woertern des Schlusssatzes nichts weiter enthaelt, und
      - kein "[unk]" enthaelt.

    Das letzte Kriterium ist das wichtige. Beim ersten Test machte der
    Erkenner aus "Tomaten Bananen Aepfel" ein 'beenden beenden [unk]' - mit
    [unk] als Kennzeichen dafuer, dass da noch etwas anderes gesprochen
    wurde. Ohne diese Bedingung waere jenes Geraeusch als Schluss
    durchgegangen.
    """
    worte = gehoert.split()
    if not worte or "[unk]" in worte:
        return False
    if "beenden" not in worte:
        return False
    return set(worte) <= SCHLUSS_WOERTER

ANSAGE_BEREIT = "Ich schreibe mit."

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
}


def ansage_ende(name, anzahl):
    """Bestaetigung nach dem Diktat, mit Hinweis aufs Vorlesen.

    Die Anzahl gehoert hinein, weil sie das Vorlesen ersetzt: Sie ist das
    einzige, woran ein blinder Nutzer merkt, dass ueberhaupt etwas angekommen
    ist - und wieviel. "Diktat beendet." allein liesse ihn im Dunkeln.
    """
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


# GESPROCHENE SATZZEICHEN (Stephans Entscheidung, 2026-08-21: "immer als
# Satzzeichen"). Vosk liefert Woerter, keine Zeichen - fuer einen
# Einkaufszettel belanglos, fuer einen Brief das Ende der Brauchbarkeit.
#
# ALLE NEUN WOERTER STEHEN IM WORTSCHATZ des grossen Modells (geprueft am
# 2026-08-21 in graph/words.txt, 822 389 Eintraege). Das musste geprueft
# werden - bei "loeschen" hatte genau das gefehlt, und der Befehl waere still
# nie ausgeloest worden. Vorsicht bei der Pruefmethode: Das grosse Modell nimmt
# KEINE eingeschraenkte Grammatik an ("Runtime graphs are not supported by
# this model") und meldet deshalb auch kein fehlendes Wort. Der Grammatik-Weg,
# der beim kleinen Modell funktioniert, liefert hier ein leeres Versprechen -
# neun Woerter sahen "vorhanden" aus, geprueft worden war nichts.
#
# DER PREIS DER ENTSCHEIDUNG: "in diesem Punkt" wird zu "in diesem." Das faellt
# beim Vorlesen auf, und der Nutzer diktiert die Stelle neu. Die Alternative
# waere gewesen, nur bei einer Sprechpause zu trennen (Vosk liefert
# Wortzeitstempel) - dann bekaeme aber, wer fluessig diktiert, gar keine
# Satzzeichen.
#
# Laengere Wendungen zuerst, sonst frisst "absatz" den "neuen absatz".
SATZZEICHEN = [
    ("neuer absatz", "\n\n"),
    ("neue zeile", "\n"),
    ("absatz", "\n\n"),
    ("gedankenstrich", " - "),
    ("ausrufezeichen", "!"),
    ("fragezeichen", "?"),
    ("doppelpunkt", ":"),
    ("komma", ","),
    ("punkt", "."),
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
            # ZUERST den Schluss-Erkenner fragen. Er bekommt denselben
            # Block; wer zuerst fertig ist, ist unerheblich - entscheidend
            # ist, dass der Schlusssatz nicht erst durch die freie
            # Erkennung muss, wo er verloren geht.
            if schluss is not None and schluss.AcceptWaveform(block):
                gehoert = json.loads(schluss.Result()).get("text", "").strip()
                if ist_schluss(gehoert):
                    melde(f"  Schlusssatz erkannt (kleines Modell): {gehoert!r}")
                    break
                if gehoert:
                    letzte_aeusserung = time.time()
                    melde(f"  (Schluss-Erkenner: {gehoert!r} - kein Schluss)")

            if not erkenner.AcceptWaveform(block):
                continue
            text = json.loads(erkenner.Result()).get("text", "").strip()
            if not text:
                continue
            letzte_aeusserung = time.time()
            melde(f"  erkannt:     {text!r}")
            if text == SCHLUSSSATZ:
                # Kommt praktisch nie vor - die freie Erkennung trifft den
                # Satz nicht (siehe Kopf). Bleibt als Rueckfallebene, falls
                # das kleine Modell fehlt.
                melde("  -> Schlusssatz in der freien Erkennung, Diktat endet")
                break
            # VOR LanguageTool, und der Grund ist GEMESSEN, nicht vermutet
            # (2026-08-21). Ich hatte behauptet, mit Satzzeichen entscheide
            # LanguageTool die Grossschreibung besser. Fuer die SUBSTANTIVE
            # stimmt das nicht - "Damen", "Herren", "Vertrag", "Termin",
            # "Kuendigung", "Gruessen" kamen mit und ohne Zeichen gleich
            # heraus. Was Satzzeichen bringen, sind die SATZANFAENGE:
            #
            #   ohne:  ... schriftlich mit freundlichen Gruessen
            #   mit:   ... schriftlich. Mit freundlichen Gruessen
            #
            # In einem Brief ist das kein Schoenheitsfehler, sondern falsch.
            # Listen bleiben aussen vor - auf einem Einkaufszettel waere
            # "Butter." keine Verbesserung.
            mit_zeichen = (text if name in LISTEN_ZIELE
                           else satzzeichen_setzen(text))
            if mit_zeichen != text:
                melde(f"  Satzzeichen:  {mit_zeichen!r}")
            gefasst = schreibung_richten(mit_zeichen)
            if gefasst.lower() != mit_zeichen.lower():
                melde(f"  ACHTUNG: Schreibhilfe hat mehr als die Schreibung geaendert")
            melde(f"  geschrieben: {gefasst!r}")
            neue = eintraege_aus(name, gefasst)
            if len(neue) > 1:
                melde(f"  in {len(neue)} Eintraege getrennt: {neue!r}")
            gesammelt += neue
    except KeyboardInterrupt:
        pass
    finally:
        if prozess:
            try:
                prozess.terminate()
            except Exception:
                pass

    if not gesammelt:
        sprich(ANSAGE_LEER)
        return 0

    pfad = notiz_schreiben(name, gesammelt)
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
