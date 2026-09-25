#!/usr/bin/env python3
"""Eine E-Mail diktieren - Empfaenger, Betreff, Text, und auf Wunsch senden.

WARUM ES DAS GIBT (Stephan, 2026-09-21): "Dann muessen wir ja bei einer neuen
Mail die Mailadresse, den Betreff und den Text noch hin bekommen und dann auch
die Mail verschicken!" Bis dahin konnte DialOS auf eine gefundene Mail
antworten und sie weiterleiten - aber keine neue schreiben. Und gesendet wurde
nie, alles blieb Entwurf.

GESENDET WIRD JETZT - ABER NUR NACH EINER BESTAETIGUNG, UND DIE IST STEPHANS
ENTSCHEIDUNG: "Nur die Eckdaten, mit vorlesen als Moeglichkeit" und "als Option
alles vorlesen". Also: "Vier Saetze an Michael Meier, Betreff Terminabsage.
Soll ich sie verschicken? Sage ja, nein, oder vorlesen." Der ganze Text kommt
auf Zuruf, nicht von selbst.

WARUM NICHT IMMER DER GANZE TEXT: Wer vor jedem Senden vier Absaetze abwarten
muss, sagt irgendwann "ja", ohne hinzuhoeren - dann ist die Sicherung nur noch
Zierde. Den Text hat der Nutzer beim Diktieren ausserdem schon einmal gehoert.

BEI ALLEM ANDEREN ALS EINEM KLAREN "JA" WIRD NICHT GESENDET, sondern abgelegt.
Auch bei "nicht verstanden". Eine Mail laesst sich nicht zurueckholen, und wer
den Bildschirm nicht sieht, hat keine zweite Kontrolle.

WAS HIER NICHT NOCHMAL GESCHRIEBEN WIRD: der Empfaengerdialog, das Diktat, die
Rueckfragen. Das steht alles in dialos-suche.py und wird von dort geholt - in
jedem dieser Stuecke steckt mindestens ein Fehler, der am Geraet schon einmal
weh getan hat (die zerstoerte Adresse, die Ladeluecke vor der Antwort, das
Diktat im eigenen Prozess wegen 10 GB Modellen).

Aufruf (durch die Sprachsteuerung, ueber das Erweiterungs-Manifest):
  dialos-mail-schreiben.py
"""

import importlib.util
import os
import signal
import subprocess
import sys
import time

SUCHE_SKRIPT = "/usr/local/bin/dialos-suche.py"
BRUECKE_SKRIPT = "/usr/local/bin/dialos-thunderbird-bruecke.py"
PROGRAMM_SKRIPT = "/usr/local/bin/dialos-programm.py"
SAY = "/usr/local/bin/dialos-say.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-mail-schreiben.log")
# DIE MARKE WIRD NICHT SELBST AUSGEDACHT, SONDERN GEHOLT (Fehler vom
# 2026-09-21, gefunden vor dem ersten Lauf): Ich hatte hier einen eigenen
# Pfad hingeschrieben - "dialos-mikrofon-belegt" statt "dialos-diktat-aktiv".
# Der Befehlsdienst haette waehrend des ganzen Dialogs mitgehoert, und jedes
# diktierte Wort waere zugleich ein Befehlsversuch gewesen. Der Pfad steht in
# dialos-suche.py, die ihn ihrerseits von dialos-diktat.py hat; drei gleiche
# Zeichenketten an drei Stellen waeren drei Gelegenheiten fuer denselben
# Fehler.
MARKE = None            # wird in main() aus dialos-suche.py uebernommen
# So lange wird auf Thunderbird gewartet, wenn es fuers Senden erst starten muss.
START_GEDULD_S = 45
ANTWORT_VERSUCHE = 3


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def modul(pfad, name):
    spec = importlib.util.spec_from_file_location(name, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sprich(text):
    try:
        subprocess.run([SAY, text], timeout=300)
    except (OSError, subprocess.SubprocessError) as fehler:
        melde(f"Ansage fehlgeschlagen: {fehler}")


def marke_setzen():
    """Das Mikrofon gehoert jetzt uns - sonst hoert der Befehlsdienst mit."""
    if MARKE is None:
        return False
    try:
        with open(MARKE, "w", encoding="utf-8") as f:
            f.write(f"{os.getpid()} dialos-mail-schreiben\n")
        return True
    except OSError as fehler:
        melde(f"Marke liess sich nicht setzen: {fehler}")
        return False


def marke_weg():
    if MARKE is None:
        return
    try:
        os.unlink(MARKE)
    except OSError:
        pass


def saetze_zaehlen(text):
    """Wie viele Saetze - fuer die Eckdaten, nicht fuer die Statistik."""
    anzahl = sum(text.count(z) for z in ".!?")
    return max(anzahl, 1 if text.strip() else 0)


def betreff_waehlen(texte):
    """Von mehreren Lesarten die mit Grossbuchstaben - das ist der Betreff.

    GEMESSEN AM 2026-09-25, ERSTER ECHTER LAUF: Vosk hoerte "probe am freitag",
    Parakeet "Probe am Freitag". Genommen wurde die erste Lesart, und im
    Entwurf stand die kleingeschriebene - in einer Betreffzeile, die der
    Empfaenger sieht. Parakeet kann Gross- und Kleinschreibung, Vosk nicht;
    welche Lesart an welcher Stelle steht, ist nicht garantiert. Also wird
    danach gesucht, statt sich auf die Reihenfolge zu verlassen.
    """
    kandidaten = [t.strip() for t in (texte or []) if t and t.strip()]
    if not kandidaten:
        return ""
    for text in kandidaten:
        if any(zeichen.isupper() for zeichen in text):
            return text
    return kandidaten[0]


def eckdaten(an, betreff, text, suche):
    """Der Satz, den der Nutzer vor dem Senden hoert."""
    zahl = saetze_zaehlen(text)
    wieviel = "Ein Satz" if zahl == 1 else f"{zahl} Sätze"
    betreff_teil = f", Betreff {betreff}" if betreff else ", ohne Betreff"
    return f"{wieviel} an {suche.sprechbar(an)}{betreff_teil}."


def senden_ueber_bruecke(an, betreff, text):
    """Thunderbird bitten, die Mail zu senden. (geklappt, Auskunft)."""
    bruecke = modul(BRUECKE_SKRIPT, "dialos_bruecke")
    bitte = {"befehl": "senden", "an": an, "betreff": betreff, "text": text}
    antwort = bruecke.fragen(bitte, zeitgrenze=60.0)
    if antwort.get("ok"):
        return True, ""
    fehler = str(antwort.get("fehler", ""))
    if "läuft nicht" not in fehler:
        return False, fehler
    # THUNDERBIRD IST ZU - UND DAS WIRD HIER NICHT VORGEMERKT.
    # Beim Entwurf ist Vormerken richtig: Er liegt dann eben spaeter im
    # Postfach, und bis dahin ist nichts geschehen. Eine Mail, die
    # "irgendwann spaeter" hinausgeht, ist etwas anderes - der Nutzer waere
    # sich sicher, sie sei weg, und wuesste nicht, wann sie wirklich geht.
    # Also wird Thunderbird jetzt gestartet und gewartet.
    sprich("Thunderbird ist zu. Ich öffne es zum Senden.")
    try:
        subprocess.Popen([PROGRAMM_SKRIPT, "postfach öffnen"],
                         start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        return False, f"Thunderbird liess sich nicht starten: {fehler}"
    ende = time.time() + START_GEDULD_S
    while time.time() < ende:
        time.sleep(1.0)
        antwort = bruecke.fragen(bitte, zeitgrenze=60.0)
        if antwort.get("ok"):
            return True, ""
        if "läuft nicht" not in str(antwort.get("fehler", "")):
            return False, str(antwort.get("fehler", ""))
    return False, "Thunderbird ist nicht rechtzeitig gestartet"


def entscheiden(an, betreff, text, suche, erkenner, modell):
    """Senden, ablegen oder vorlesen - Stephans Form vom 2026-09-21.

    DREI ANTWORTEN STATT ZWEI, und deshalb nicht ja_oder_nein: "vorlesen" ist
    die Moeglichkeit, die die Bestaetigung ueberhaupt wirksam macht. Ohne sie
    muesste der Nutzer entweder jedes Mal den ganzen Text hoeren oder blind
    zustimmen.
    """
    frage = (eckdaten(an, betreff, text, suche) +
             " Soll ich sie verschicken? Sage ja, nein, oder vorlesen.")
    for versuch in range(1, ANTWORT_VERSUCHE + 1):
        texte = suche.antwort_hoeren(frage, erkenner, modell)
        gesagt = " ".join(texte).lower() if texte else ""
        melde(f"  Entscheidung {versuch}: {gesagt!r}")
        if "vorles" in gesagt or "alles" in gesagt:
            sprich(f"An {suche.sprechbar(an)}. Betreff: {betreff or 'ohne Betreff'}. "
                   f"Der Text lautet: {text}")
            frage = "Soll ich sie jetzt verschicken? Sage ja oder nein."
            continue
        if any(w in gesagt.split() for w in ("ja", "jawohl", "senden", "verschicken")):
            return "senden"
        if any(w in gesagt.split() for w in ("nein", "nicht", "abbrechen", "stopp")):
            return "entwurf"
        frage = "Das habe ich nicht verstanden. Sage ja, nein, oder vorlesen."
    # NICHTS VERSTANDEN HEISST NICHT SENDEN. Der Entwurf bleibt, und der Nutzer
    # kann es noch einmal versuchen - eine gesendete Mail koennte er das nicht.
    melde("  nichts Verwertbares - es wird abgelegt")
    return "entwurf"


def selbsttest():
    """Was sich ohne Mikrofon pruefen laesst - vor jedem Aufspielen.

    NICHT WEIL ES SCHOEN IST, SONDERN WEGEN DES 2026-09-21: Ein Umbau an der
    Suche hatte eine Funktion geloescht; py_compile und der Selbsttest liefen
    durch, und der Fehler zeigte sich erst am Geraet - mitten im Dialog, vor
    einem schweigenden Rechner. Ein Selbsttest, der die Namen NICHT nachschaut,
    ist keiner.
    """
    fehlt = []
    try:
        suche = modul(SUCHE_SKRIPT, "dialos_suche")
    except Exception as fehler:            # noqa: BLE001
        print(f"FEHLER: dialos-suche.py nicht ladbar: {fehler}")
        return 1
    for name in ("MARKE", "modelle_laden", "antwort_hoeren", "ja_oder_nein",
                 "text_diktieren", "empfaenger_erfragen_fuer_mail",
                 "entwurf_ablegen", "sprechbar"):
        if not hasattr(suche, name):
            fehlt.append(f"dialos-suche.{name}")
    try:
        bruecke = modul(BRUECKE_SKRIPT, "dialos_bruecke")
        if not hasattr(bruecke, "fragen"):
            fehlt.append("dialos-thunderbird-bruecke.fragen")
        else:
            antwort = bruecke.fragen({"befehl": "hallo"}, zeitgrenze=5.0)
            print("Thunderbird: " + ("erreichbar, Konten "
                                     + ", ".join(antwort.get("konten", []))
                                     if antwort.get("ok")
                                     else f"nicht erreichbar ({antwort.get('fehler')})"))
    except Exception as fehler:            # noqa: BLE001
        fehlt.append(f"Brücke: {fehler}")
    class Probe:
        sprechbar = staticmethod(lambda a: a)
    print("Eckdaten-Probe:",
          eckdaten("kontakt@dialos.org", "Terminabsage",
                   "Guten Tag. Ich kann morgen nicht kommen. Viele Grüße.", Probe))
    if fehlt:
        print("FEHLT: " + ", ".join(fehlt))
        return 1
    print("Selbsttest bestanden.")
    return 0


def main():
    global MARKE
    if "--pruefen" in sys.argv:
        return selbsttest()
    try:
        suche = modul(SUCHE_SKRIPT, "dialos_suche")
        MARKE = suche.MARKE
    except Exception as fehler:            # noqa: BLE001
        melde(f"dialos-suche.py nicht ladbar: {fehler}")
        sprich("Ich kann die E-Mail-Hilfe nicht starten.")
        return 1
    if not marke_setzen():
        sprich("Ich kann das Mikrofon nicht übernehmen.")
        return 1

    def aufraeumen(nummer, _rahmen):
        raise SystemExit(128 + nummer)

    for nummer in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(nummer, aufraeumen)

    try:
        melde("=== Neue E-Mail ===")
        sprich("Einen Moment, ich hole Zettel und Stift.")
        erkenner, modell = suche.modelle_laden()

        an = suche.empfaenger_erfragen_fuer_mail(
            erkenner, modell,
            frage=("An wen soll die E-Mail gehen? Sage den Namen aus Deinen "
                   "Kontakten, oder sage: buchstabieren."))
        if not an:
            sprich("Gut, ich schreibe keine E-Mail.")
            return 0
        melde(f"  an: {an}")

        texte = suche.antwort_hoeren("Was soll im Betreff stehen?", erkenner, modell)
        betreff = betreff_waehlen(texte)
        melde(f"  Betreff: {betreff!r}")

        text = suche.text_diktieren(
            "Sage jetzt den Text der E-Mail. Wenn Du fertig bist, sage: "
            "Diktat beenden.")
        # DIE MARKE GEHOERT NACH DEM DIKTAT WIEDER UNS - das Diktat setzt sie
        # auf "dialos-suche", weil es aus deren Helfer kommt.
        marke_setzen()
        if not text.strip():
            sprich("Ich habe nichts mitgeschrieben. Es wird nichts verschickt.")
            return 0

        was = entscheiden(an, betreff, text, suche, erkenner, modell)
        if was == "senden":
            geklappt, auskunft = senden_ueber_bruecke(an, betreff, text)
            if geklappt:
                sprich("Die E-Mail ist unterwegs.")
                melde(f"  gesendet an {an}")
                return 0
            melde(f"  Senden fehlgeschlagen: {auskunft}")
            sprich("Das Senden hat nicht geklappt. Ich lege die E-Mail als "
                   "Entwurf ab.")
        geklappt, ergebnis = suche.entwurf_ablegen(an, betreff or "(ohne Betreff)",
                                                   text)
        if not geklappt:
            sprich("Der Entwurf ließ sich nicht ablegen.")
            return 1
        if ergebnis == "vorgemerkt":
            sprich("Thunderbird ist zu. Ich lege den Entwurf beim nächsten "
                   "Start von Thunderbird ab.")
        else:
            sprich("Die E-Mail liegt in Thunderbird unter Entwürfe.")
        return 0
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        import traceback
        melde("ABSTURZ: " + traceback.format_exc().strip().replace("\n", " | "))
        sprich("Beim Schreiben der E-Mail ist etwas schiefgegangen. "
               "Ich höre wieder zu.")
        return 1
    finally:
        marke_weg()
        melde("=== beendet ===")


if __name__ == "__main__":
    sys.exit(main())
