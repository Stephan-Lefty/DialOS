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
PROTOKOLL = os.path.join(os.path.expanduser("~"), "dialos-hilfe.log")

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
                "sehen, was auf dem Bildschirm steht, und das Gerät bedienen. "
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
ANSAGE_KEINE_ID = ("Die Fernwartung läuft, aber ich konnte die Nummer nicht "
                   "ablesen. Bitte ruf Deinen Betreuer an, er kommt auch ohne "
                   "sie weiter.")


def melde(text):
    if DEBUG:
        print(text, flush=True)
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


def ziffern_sprechen(text):
    """"68400324" -> "sechs acht vier null. null drei zwei vier."

    Vierergruppen mit Punkt dazwischen: Piper macht am Punkt eine deutliche
    Pause, und die braucht der Nutzer, um die Nummer am Telefon nachzusprechen.
    """
    worte = [ZIFFERN.get(z, z) for z in text if z.strip()]
    gruppen = [" ".join(worte[i:i + 4]) for i in range(0, len(worte), 4)]
    return ". ".join(gruppen) + "."


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


def id_ansagen():
    kenn = kennung()
    if not kenn:
        sprich(ANSAGE_KEINE_ID)
        return 1
    melde(f"  ID angesagt ({len(kenn)} Ziffern)")   # NICHT die ID selbst
    gesprochen = ziffern_sprechen(kenn)
    sprich(f"Die Fernwartung läuft. Deine Nummer ist: {gesprochen}")
    time.sleep(0.4)
    sprich(f"Noch einmal: {gesprochen} Sage sie Deinem Betreuer am Telefon.")
    sprich(ANSAGE_SCHUTZ)
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

    # Marke setzen, damit der Befehlsdienst sich waehrend der Rueckfrage
    # heraushaelt - sonst hoerten zwei Erkenner auf dasselbe Mikrofon.
    open(notiz.FREMDE_AUFNAHME_MARKE, "w").close()
    try:
        antwort = notiz.ja_oder_nein(ANSAGE_FRAGE)
    finally:
        try:
            os.unlink(notiz.FREMDE_AUFNAHME_MARKE)
        except OSError:
            pass

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
               "Deinem Betreuer, dass er das Gerät neu starten soll.")
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
        return id_ansagen()
    if was == "wache":
        return wache()
    print("Aufruf: dialos-hilfe.py starten|beenden|ansagen|wache",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
