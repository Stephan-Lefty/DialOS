#!/usr/bin/env python3
"""DialOS: Fernwartung auf Ansage starten und beenden ("Hilfe rufen").

Umgesetzt am 2026-08-19. Bis dahin hatte ein Nutzer, bei dem etwas nicht
funktioniert, KEINEN Weg, den Support zu erreichen - alles, was an
Nachvollziehbarkeit gebaut wurde (Support-Protokoll, Mitschrift), setzt voraus,
dass jemand ueberhaupt an das Geraet kommt.

DIE FESTLEGUNGEN AUS docs/sicherheit-datenschutz.md, die dieses Skript umsetzt:

  * RustDesk laeuft NICHT dauerhaft und nicht im Autostart. Der systemd-Dienst
    ist bewusst "disabled". Erst dieser Sprachbefehl macht eine Verbindung
    ueberhaupt moeglich - und "Fernwartung beenden" macht sie wieder unmoeglich.
    Bewusste Folge: Eine echte Notfall-Fernwartung bei eingefrorenem System gibt
    es damit nicht. Nur was der Nutzer selbst anfordert.

  * Die ID muss vorgelesen werden, weil ein blinder Nutzer sie nicht ablesen
    kann. "rustdesk --get-id" liefert sie und beendet sich sofort.

DREI DINGE, DIE BEIM BAUEN GELERNT WURDEN:

1. ZIFFERN EINZELN SPRECHEN. Die ID ist achtstellig. Als Zahl gesprochen wuerde
   daraus "achtundsechzig Millionen vierhunderttausend dreihundertvierundzwanzig"
   - fuer jemanden, der sie am Telefon weitergeben soll, unbrauchbar. Sie wird
   deshalb Ziffer fuer Ziffer gesprochen, in Vierergruppen mit Pause, und
   ZWEIMAL: Der Nutzer kann nichts mitschreiben.

2. "rustdesk --help" STARTET DIE OBERFLAECHE, statt Hilfe auszugeben (gefunden
   am 2026-08-19, der Aufruf lief in die Zeitgrenze und liess ein RustDesk
   laufen). Deshalb wird hier ausschliesslich "--get-id" benutzt, das geprueft
   sauber zurueckkommt. Wer weitere Schalter ausprobiert, tut das mit
   Zeitgrenze und raeumt danach auf.

3. EIN EINMALPASSWORT IST MIT RUSTDESK 1.4.9 NICHT ZU HABEN - vier Wege am
   2026-08-19 geprueft, alle zu:

     * Das Einmalpasswort, das RustDesk selbst erzeugt, steht in KEINER Datei.
       Es lebt nur im Speicher und in der Oberflaeche - fuer einen blinden
       Nutzer also nirgends.
     * "rustdesk --password <wert>" ist wirkungslos: als Nutzer, mit laufender
       Anwendung, mit laufendem systemd-Dienst und als root. Rueckgabewert 0,
       aber das Feld "password" bleibt leer.
     * "rustdesk-utils", das den Wert berechnen koennte, ist im Paket nicht
       enthalten.
     * Den Wert selbst in die Konfiguration zu schreiben faellt aus: RustDesk
       legt dort keinen einfachen Hash ab, sondern einen mit einem lokalen
       Schluessel verschluesselten Wert (wie bei enc_id, 70 Zeichen). Das
       nachzubauen waere geraten und wuerde bei der naechsten Version still
       brechen.

   Das ist kein Fehler dieses Projekts: rustdesk/rustdesk#5074 heisst
   "Permanent password not deployable without user interaction" und ist offen.

   STATT DESSEN GARANTIERT DIALOS DIE BEGRENZUNG UEBER DIE LAUFZEIT, und das
   ist der haertere Hebel (Stephans Entscheidung vom 2026-08-19): Solange
   RustDesk nicht laeuft, ist keine Verbindung moeglich - unabhaengig davon, wer
   das Passwort kennt. Es startet nie von selbst, nur auf "Hilfe rufen", und
   endet auf "Fernwartung beenden" oder nach ZEITGRENZE_S von selbst, mit
   Ansage. Das Passwort setzt der Betreuer einmal im Buero ueber die
   Oberflaeche; es steht in SEINEN Unterlagen und nicht im Raum des Kunden.

   Und die Ansage sagt genau das, statt etwas Falsches zu behaupten. "Das
   Passwort gilt nur fuer diesen Einsatz" waere eine Luege, solange es dauerhaft
   ist - und einem Nutzer, der den Bildschirm nicht sieht, eine falsche
   Sicherheit zu erzaehlen ist schlimmer, als ihm die richtige zu erklaeren.

Aufruf:
    dialos-hilfe.py starten     fragt nach und startet die Fernwartung
    dialos-hilfe.py beenden     beendet sie wieder
    dialos-hilfe.py ansagen     nur die ID vorlesen (wenn sie schon laeuft)
    dialos-hilfe.py wache       Wache, die die Zeitgrenze durchsetzt
                                (wird von "starten" selbst abgespalten)
"""

import importlib.util
import os
import signal
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
NOTIZ_SKRIPT = "/usr/local/bin/dialos-notiz.py"
RUSTDESK = "/usr/bin/rustdesk"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-hilfe.log")

DEBUG = "--debug" in sys.argv

# Zeitgrenze der Fernwartung: eine STUNDE (Stephan, 2026-08-19 - erst eine halbe
# Stunde, dann auf sein Wort ausgeweitet). Vergisst der Nutzer "Fernwartung
# beenden", endet sie von selbst; ein vergessener Support-Einsatz darf nicht bis
# zum Abmelden offen bleiben.
#
# WARUM ABSOLUT UND NICHT IM LEERLAUF, obwohl Leerlauf die richtige Semantik
# waere: Das Risiko ist eine offene Fernwartung, an der NIEMAND haengt - genau
# der Leerlauf-Fall. Eine laufende Sitzung abzuschneiden waere schaedlich, etwa
# mitten in einem Update. Nur: Auf diesem Geraet hat sich noch nie jemand
# verbunden, die Signatur einer aktiven Verbindung ist also unbekannt. Sie zu
# raten waere der schlechtere Fehler - eine Grenze, die eine aktive Sitzung fuer
# Leerlauf haelt, schneidet den Betreuer bei der Arbeit ab.
#
# Deshalb zweistufig: jetzt absolut mit Vorwarnung, und ein "Hilfe rufen"
# waehrend der Sitzung setzt die Frist neu. Sobald eine echte Verbindung
# stattgefunden hat, steht ihre Signatur im Protokoll (siehe spur_notieren) und
# die Leerlauf-Erkennung laesst sich daraus BELEGT bauen. Steht in TODO.md.
ZEITGRENZE_S = 60 * 60.0

# So lange vorher wird gewarnt. Drei Minuten reichen, um "Hilfe rufen" zu sagen
# und weiterzuarbeiten - und sie sind kurz genug, dass die Warnung nicht
# vergessen ist, wenn es soweit ist.
VORWARNUNG_S = 3 * 60.0

# Wie oft die Wache nachsieht. 20 s sind genau genug: Die Zeitgrenze ist eine
# halbe Stunde, und ein Prozess, der eine halbe Stunde lang wartet, soll dabei
# nichts kosten.
WACHE_TAKT_S = 20.0


def marke_pfad(name):
    """Pro Nutzer, nicht geteilt.

    Dasselbe Muster wie in dialos-diktat.py und dialos-notiz.py - und mit dem
    Grund vom 2026-08-19 im Ruecken: Eine Markendatei an festem Pfad in /tmp
    gehoerte dem ersten Nutzer, der sie anlegte, und der zweite konnte sie nicht
    ueberschreiben. Bei der Start-Ansage liefen dadurch zwei Instanzen.
    """
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


# Enthaelt den Zeitpunkt, zu dem die Fernwartung endet. Zugleich die Sperre
# gegen eine zweite Wache.
FRIST_MARKE = marke_pfad("dialos-fernwartung-frist")

ZIFFERN = {"0": "null", "1": "eins", "2": "zwei", "3": "drei", "4": "vier",
           "5": "fünf", "6": "sechs", "7": "sieben", "8": "acht", "9": "neun"}

ANSAGE_FRAGE = ("Ich kann die Fernwartung starten. Dein Betreuer kann dann "
                "sehen, was auf dem Bildschirm steht, und den Computer bedienen. "
                "Soll ich sie starten? Sage ja oder nein.")
ANSAGE_NEIN = "Gut, ich lasse die Fernwartung aus."
ANSAGE_UNKLAR = "Ich habe nichts verstanden. Ich lasse die Fernwartung aus."
ANSAGE_LAEUFT_SCHON = "Die Fernwartung läuft schon."
ANSAGE_BEENDET = "Die Fernwartung ist beendet. Niemand kann mehr zusehen."
ANSAGE_ZEITGRENZE = ("Die Stunde ist um. Ich habe die Fernwartung beendet. "
                     "Niemand kann mehr zusehen.")
ANSAGE_VORWARNUNG = ("Die Fernwartung endet in drei Minuten. Wenn Du sie länger "
                     "brauchst, sage einfach noch einmal: Hilfe rufen.")
ANSAGE_VERLAENGERT = ("Die Fernwartung läuft weiter. Sie endet jetzt erst in "
                      "einer Stunde.")
# Sagt die WAHRHEIT ueber das, was den Nutzer schuetzt: nicht das Passwort,
# sondern die Laufzeit. Siehe Punkt 3 im Kopf.
ANSAGE_SCHUTZ = ("Das Passwort kennt Dein Betreuer schon. Die Fernwartung "
                 "läuft nur, bis Du sagst: Fernwartung beenden. Wenn Du es "
                 "vergisst, beende ich sie nach einer Stunde von selbst.")
ANSAGE_LIEF_NICHT = "Die Fernwartung lief nicht."
ANSAGE_KEIN_RUSTDESK = "Ich finde das Fernwartungs-Programm nicht."
# "ID" und nicht "Nummer" (Stephan, 2026-08-19). Der Betreuer fragt am Telefon
# nach der ID; sagt das Geraet ein anderes Wort, sucht ein Nutzer, der den
# Bildschirm nicht sieht, zwei verschiedene Dinge. Die englische Aussprache
# erledigt die Aussprache-Tabelle in dialos-say.py - hier steht sie richtig
# geschrieben.
ANSAGE_KEINE_ID = ("Die Fernwartung läuft, aber ich konnte die ID nicht "
                   "ablesen. Bitte ruf Deinen Betreuer an, er kommt auch ohne "
                   "sie weiter.")

# Pause zwischen Nummer und Passwort (Stephan, 2026-08-19: "eine etwas groessere
# Pause zwischen ID und Einmalpasswort"). Zwei Dinge sorgen dafuer: die
# Wartezeit hier UND ein eigener Satz davor - eine Ansage, die neu ansetzt,
# trennt hoerbar besser als jede Stille.
PAUSE_ZWISCHEN_S = 1.6
ANSAGE_PASSWORT_FOLGT = "Und jetzt das Einmalpasswort:"

# NACHFRAGE, OB ES ANGEKOMMEN IST (Stephan, 2026-08-19). Der Nutzer hoert die
# Zahlen, aber niemand weiss, ob er sie am Telefon durchgeben konnte - er kann
# nicht nachsehen und nichts mitschreiben. Ein Betreuer, der wartet, und ein
# Nutzer, der die Haelfte verloren hat, sind der wahrscheinlichste Fehlerfall
# dieses ganzen Befehls.
FRAGE_WEITERGEGEBEN = "Hast Du das Deinem Betreuer weitergegeben? Sage ja oder nein."
FRAGE_WIEDERHOLEN = "Soll ich es wiederholen? Sage ja oder nein."
ANSAGE_ANGEKOMMEN = "Gut. Dein Betreuer kann sich jetzt verbinden."
ANSAGE_SPAETER = ("Wenn Du es später noch einmal brauchst, sage einfach: "
                  "Hilfe rufen.")

# Wie oft wiederholt wird. Nach der dritten Ansage wird nicht weiter gefragt,
# sondern gesagt, wie man sie jederzeit wiederbekommt - eine Schleife, die nur
# der Nutzer beenden kann, ist bei einem Nutzer, den der Erkenner gerade nicht
# versteht, keine Schleife, aus der er herauskommt.
WIEDERHOLUNGEN_MAX = 2


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
            f.write(f"{time.strftime('%H:%M:%S')}  {text}\n")
    except OSError:
        pass          # ein fehlendes Protokoll darf die Hilfe nicht aufhalten


def sprich(text):
    if not os.access(SAY, os.X_OK):
        print(text)
        return
    subprocess.run([SAY, text], capture_output=True, timeout=180)


def notiz_bausteine():
    """Holt ja_oder_nein() aus dialos-notiz.py.

    BEWUSST GEHOLT UND NICHT KOPIERT. Die Funktion enthaelt die Lehre vom
    2026-08-19: Sie stellt die Frage SELBST und laedt das Sprachmodell vorher,
    weil sonst die Antwort in die Luecke zwischen Frage und Aufnahmebeginn
    faellt. Eine Kopie hier wuerde diesen Fehler beim naechsten Aendern wieder
    einbauen - dieselbe Ueberlegung wie bei dialos-auskunft.py, das seine
    Sprech-Bausteine aus der Start-Ansage holt.
    """
    try:
        spec = importlib.util.spec_from_file_location("dialos_notiz", NOTIZ_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    except Exception as fehler:
        melde(f"  Bausteine nicht ladbar: {fehler}")
        return None


# JEDE ZIFFER EINZELN, mit Punkt und Auslassungspunkten dazwischen (Stephan,
# 2026-08-19, in drei Schritten: erst Vierergruppen, dann "langsam", dann "noch
# langsamer"). Gemessen fuer eine zehnstellige Nummer:
#
#     zwei Ziffern, Punkt          3,74 s
#     eine Ziffer,  Punkt          3,74 s   <- Punkt allein bringt NICHTS
#     eine Ziffer,  Komma          6,09 s
#     eine Ziffer,  ". .."         8,62 s   <- gewaehlt
#
# ZWEI ERKENNTNISSE DARAUS, die der frueheren Annahme widersprechen: Der Punkt
# allein aendert bei kurzen Woertern gar nichts - Zweier- und Einzelgruppen
# dauern gleich lang. Und das KOMMA dehnt mehr als der Punkt, obwohl im Projekt
# bisher das Gegenteil stand (die Messung vom 2026-08-18 verglich "ohne
# Satzzeichen" gegen "mit Punkt", nicht Punkt gegen Komma - kein Widerspruch,
# aber eine Luecke, die jetzt geschlossen ist).
#
# Warum so langsam ueberhaupt: Der Nutzer sieht die Nummer nicht und kann nichts
# mitschreiben. Er muss sie am Telefon nachsprechen, und wer eine Ziffer
# verliert, verliert die ganze Nummer - nachfragen kann er nur, indem er von
# vorn anfaengt.
ZIFFERN_TRENNER = ". .. "


def ziffern_sprechen(text):
    """"6840" -> "sechs. .. acht. .. vier. .. null." """
    worte = [ZIFFERN.get(z, z) for z in text if z.strip()]
    return ZIFFERN_TRENNER.join(worte) + "."


def rustdesk_pids():
    """PIDs laufender RustDesk-Prozesse.

    Geprueft wird die ausfuehrbare Datei und nicht die Befehlszeile: Ein Scan
    ueber die Befehlszeile trifft den eigenen Aufruf, wenn dessen Text das
    Suchmuster enthaelt - am 2026-08-19 fuenfmal passiert.
    """
    gefunden = []
    try:
        eintraege = os.listdir("/proc")
    except OSError:
        return gefunden
    for e in eintraege:
        if not e.isdigit() or int(e) == os.getpid():
            continue
        try:
            exe = os.readlink(f"/proc/{e}/exe")
        except OSError:
            continue
        if "rustdesk" in os.path.basename(exe).lower():
            gefunden.append(int(e))
    return gefunden


def kennung():
    """Die RustDesk-ID, oder None.

    NUR "--get-id" - geprueft am 2026-08-19: kommt mit Rueckgabewert 0 zurueck
    und startet keine Oberflaeche. Die Zeitgrenze ist die Reissleine, falls eine
    kuenftige Version das aendert.
    """
    try:
        r = subprocess.run([RUSTDESK, "--get-id"], capture_output=True,
                           text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as fehler:
        melde(f"  ID nicht ablesbar: {fehler}")
        return None
    for zeile in (r.stdout or "").splitlines():
        z = zeile.strip()
        if z.isdigit() and len(z) >= 6:
            return z
    melde(f"  keine ID in der Ausgabe (Rueckgabe {r.returncode})")
    return None


def frist_setzen():
    """Legt fest, wann die Fernwartung endet, und gibt den Zeitpunkt zurueck."""
    ende = time.time() + ZEITGRENZE_S
    try:
        with open(FRIST_MARKE, "w") as f:
            f.write(str(ende))
    except OSError as fehler:
        melde(f"  Frist nicht schreibbar: {fehler}")
    return ende


def frist_lesen():
    try:
        with open(FRIST_MARKE) as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return None


def frist_loeschen():
    try:
        os.unlink(FRIST_MARKE)
    except OSError:
        pass


def spur_notieren(anlass):
    """Schreibt die Signatur des aktuellen Zustands ins Protokoll.

    ZWECK: Die Leerlauf-Erkennung fehlt noch, weil auf diesem Geraet nie eine
    Verbindung stattgefunden hat und niemand weiss, wie eine aussieht. Diese
    Funktion sammelt die Anhaltspunkte, waehrend die Fernwartung laeuft - Anzahl
    der RustDesk-Prozesse und Groesse des RustDesk-Protokolls. Verbindet sich
    einmal wirklich jemand, steht danach im Protokoll, WAS sich dabei geaendert
    hat, und daraus laesst sich die Erkennung belegt bauen statt geraten.

    Bewusst nur Zahlen: keine Namen, keine Adressen, keine Inhalte.
    """
    prot = os.path.expanduser(
        "~/.local/share/logs/RustDesk/rustdesk_rCURRENT.log")
    try:
        groesse = os.path.getsize(prot)
    except OSError:
        groesse = -1
    melde(f"  Spur ({anlass}): {len(rustdesk_pids())} Prozesse, "
          f"Protokoll {groesse} Bytes")


def wache():
    """Beendet die Fernwartung, wenn die Frist ablaeuft.

    Laeuft als eigener Prozess, den "starten" abspaltet. Sie beendet sich von
    selbst, wenn RustDesk schon weg ist - dann hat der Nutzer "Fernwartung
    beenden" gesagt, und es gibt nichts mehr zu tun UND nichts anzusagen.
    """
    melde("  Wache begonnen")
    gewarnt = False
    while True:
        if not rustdesk_pids():
            melde("  Wache endet: Fernwartung ist schon beendet")
            frist_loeschen()
            return 0
        ende = frist_lesen()
        if ende is None:
            melde("  Wache endet: keine Frist mehr eingetragen")
            return 0
        rest = ende - time.time()
        if rest <= 0:
            melde("=== Zeitgrenze erreicht ===")
            spur_notieren("Zeitgrenze")
            beenden(ansage=ANSAGE_ZEITGRENZE)
            return 0
        if rest <= VORWARNUNG_S and not gewarnt:
            melde(f"  Vorwarnung ({rest:.0f} s Rest)")
            sprich(ANSAGE_VORWARNUNG)
            gewarnt = True
        # Wird per "Hilfe rufen" verlaengert, ist die Warnung wieder faellig.
        if rest > VORWARNUNG_S:
            gewarnt = False
        spur_notieren("Wache")
        time.sleep(WACHE_TAKT_S)


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


def frage(notiz, text):
    """Ja/Nein-Rueckfrage stellen. True, False oder None.

    SETZT DIE MARKE, die den Befehlsdienst heraushaelt - zentral hier und nicht
    an jeder Aufrufstelle. Vorher tat das nur starten(); mit vier Fragen im
    Ablauf waere das Vergessen an einer Stelle eine Frage der Zeit gewesen, und
    die Folge waeren zwei Erkenner auf demselben Mikrofon.
    """
    open(notiz.FREMDE_AUFNAHME_MARKE, "w").close()
    try:
        return notiz.ja_oder_nein(text)
    finally:
        try:
            os.unlink(notiz.FREMDE_AUFNAHME_MARKE)
        except OSError:
            pass


def nummern_sprechen(kenn, passwort=None):
    """Liest ID und - sobald verfuegbar - das Einmalpasswort vor.

    Zweimal die ID, dazwischen die Pause. Das Passwort kommt mit eigenem
    Ansatzsatz, weil eine Ansage, die neu ansetzt, hoerbar besser trennt als
    Stille (Stephans Wunsch nach einer groesseren Pause zwischen beiden).
    """
    g = ziffern_sprechen(kenn)
    sprich(f"Die Fernwartung läuft. Die ID ist: {g}")
    time.sleep(PAUSE_ZWISCHEN_S)
    sprich(f"Noch einmal die ID: {g}")
    if passwort:
        time.sleep(PAUSE_ZWISCHEN_S)
        p = ziffern_sprechen(passwort)
        sprich(f"{ANSAGE_PASSWORT_FOLGT} {p}")
        time.sleep(PAUSE_ZWISCHEN_S)
        sprich(f"Noch einmal das Einmalpasswort: {p}")


def einmalpasswort():
    """Das Einmalpasswort - oder None, solange RustDesk keines hergibt.

    NOCH IMMER None, und das ist belegt und nicht vergessen: Fuenf Wege am
    2026-08-19 geprueft, alle zu (Liste im Kopf dieses Skripts und in
    docs/sicherheit-datenschutz.md). Offen ist genau eine Kombination -
    "sudo rustdesk --password" MIT laufendem systemd-Dienst; Stephans Test dazu
    steht noch aus.

    Sobald der Weg offen ist, gehoert hierher: ein frisches achtstelliges
    Zufallspasswort erzeugen, es ueber ein root-eigenes Skript ohne Argumente
    setzen (kein sudo-Platzhalter, keine Nutzereingabe) und zurueckgeben. Beim
    "Fernwartung beenden" wird dann ein neues gesetzt, das niemand erfaehrt -
    erst DAS macht das vorgelesene zu einem echten Einmalpasswort.

    Alles darueber ist schon dafuer gebaut: nummern_sprechen() liest es vor,
    sobald es da ist, und die Fragetexte sind so formuliert, dass sie mit einer
    Zahl und mit zwei stimmen ("Hast Du das ... weitergegeben?").
    """
    return None


def id_ansagen(nachfragen=True):
    kenn = kennung()
    if not kenn:
        sprich(ANSAGE_KEINE_ID)
        return 1
    melde(f"  ID angesagt ({len(kenn)} Ziffern)")   # NICHT die ID selbst
    passwort = einmalpasswort()
    notiz = notiz_bausteine() if nachfragen else None

    for runde in range(WIEDERHOLUNGEN_MAX + 1):
        nummern_sprechen(kenn, passwort)
        if notiz is None:
            # Ohne Rueckfrage-Bausteine wird nur angesagt. Kein Grund zur
            # Fehlmeldung: Die Zahlen sind angekommen, nur das Nachfragen faellt
            # aus.
            break
        if runde == 0:
            sprich(ANSAGE_SCHUTZ)
        antwort = frage(notiz, FRAGE_WEITERGEGEBEN)
        melde(f"  weitergegeben? {antwort}")
        if antwort is True:
            sprich(ANSAGE_ANGEKOMMEN)
            return 0
        if runde >= WIEDERHOLUNGEN_MAX:
            break
        # "nein" UND "nichts verstanden" fuehren zur selben Frage: Wer nicht
        # antworten konnte, hat es mit hoher Wahrscheinlichkeit auch nicht
        # weitergegeben.
        nochmal = frage(notiz, FRAGE_WIEDERHOLEN)
        melde(f"  wiederholen? {nochmal}")
        if nochmal is not True:
            break

    sprich(ANSAGE_SPAETER)
    return 0


def starten():
    if not os.access(RUSTDESK, os.X_OK):
        melde("  rustdesk fehlt")
        sprich(ANSAGE_KEIN_RUSTDESK)
        return 1
    if rustdesk_pids():
        # "Hilfe rufen" WAEHREND einer Sitzung verlaengert sie. Das ist der
        # natuerliche Weg, wenn die Vorwarnung gekommen ist: Der Nutzer muss
        # sich keinen zweiten Satz merken, und der Betreuer wird nicht mitten
        # in der Arbeit abgeschnitten.
        melde("  laeuft schon - Frist wird neu gesetzt")
        frist_setzen()
        sprich(ANSAGE_LAEUFT_SCHON)
        sprich(ANSAGE_VERLAENGERT)
        return id_ansagen()

    notiz = notiz_bausteine()
    if notiz is None:
        # Ohne Rueckfrage wird NICHT gestartet. Eine Fernwartung ohne
        # Zustimmung ist der schlimmere Fehler als eine, die nicht zustande
        # kommt - der Nutzer kann es erneut versuchen, einen fremden Blick auf
        # seinen Bildschirm kann er nicht zurueckholen.
        sprich("Ich kann gerade nicht nachfragen. Ich starte die Fernwartung "
               "deshalb nicht.")
        return 1

    # MIT Namen: Hier faellt die Entscheidung, einen fremden Blick auf
    # den Bildschirm freizugeben. Die zwei Nachfragen danach bleiben
    # ohne - sie kommen bis zu dreimal hintereinander.
    antwort = frage(notiz, anrede(ANSAGE_FRAGE))
    melde(f"  Antwort: {antwort}")
    if antwort is None:
        sprich(ANSAGE_UNKLAR)
        return 0
    if antwort is False:
        sprich(ANSAGE_NEIN)
        return 0

    melde("=== Fernwartung gestartet ===")
    try:
        subprocess.Popen([RUSTDESK], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        melde(f"  Start fehlgeschlagen: {fehler}")
        sprich("Das hat nicht geklappt. Ich habe die Fernwartung nicht "
               "gestartet.")
        return 1
    # RustDesk braucht einen Moment, bis es beim Vermittlungsdienst angemeldet
    # ist. Vorher waere die Nummer da, die Verbindung aber noch nicht moeglich.
    time.sleep(6)
    frist_setzen()
    spur_notieren("Start")
    # Die Wache als eigener Prozess. Sie muss den Aufrufer ueberleben: Dieses
    # Skript kehrt zurueck, sobald die Nummer angesagt ist, und der
    # Befehlsdienst wartet ohnehin nicht darauf.
    try:
        subprocess.Popen([sys.argv[0], "wache"], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as fehler:
        melde(f"  Wache liess sich nicht starten: {fehler}")
        sprich("Achtung: Ich kann die Fernwartung nicht von selbst beenden. "
               "Sage bitte unbedingt: Fernwartung beenden, wenn Du fertig bist.")
    return id_ansagen()


def beenden(ansage=None):
    """Beendet die Fernwartung. 'ansage' erlaubt der Wache eine eigene."""
    pids = rustdesk_pids()
    if not pids:
        melde("  lief nicht")
        frist_loeschen()
        sprich(ANSAGE_LIEF_NICHT)
        return 0
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    time.sleep(3)
    rest = rustdesk_pids()
    for pid in rest:
        try:
            os.kill(pid, signal.SIGKILL)      # Reissleine
        except OSError:
            pass
    time.sleep(1)
    uebrig = rustdesk_pids()
    if uebrig:
        melde(f"  ACHTUNG: laeuft noch: {uebrig}")
        sprich("Ich konnte die Fernwartung nicht sicher beenden. Bitte sag "
               "Deinem Betreuer, dass er den Computer neu starten soll.")
        return 1
    melde("=== Fernwartung beendet ===")
    frist_loeschen()
    sprich(ansage or ANSAGE_BEENDET)
    return 0


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    was = argumente[0] if argumente else "starten"
    melde(f"=== {was} ===")
    if was == "starten":
        return starten()
    if was == "beenden":
        return beenden()
    if was == "ansagen":
        # Von Hand aufgerufen wird nur angesagt, nicht nachgefragt.
        return id_ansagen(nachfragen=False)
    if was == "wache":
        return wache()
    print("Aufruf: dialos-hilfe.py starten|beenden|ansagen|wache",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
