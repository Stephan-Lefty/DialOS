#!/usr/bin/env python3
"""DialOS: Systemaktualisierung nach dem Anmelden - alle 14 Tage, montags.

Stephans Vorgabe vom 2026-09-14. Sein Wortlaut fuer den Ablauf:
"dem User gesagt wird, es muessen ein paar Updates installiert werden und das
kann etwas dauern und dann wird der Computer neu gestartet. Und nach dem
Neustart und der Begruessung dann noch der Hinweis kommt, der Computer ist auf
den neuesten Stand!"

WARUM NACH DEM ANMELDEN UND NICHT AUF EINEM TIMER (Stephans Entscheidung nach
Rueckfrage): Ein Timer kann mitten in ein Diktat oder ein Telefonat feuern -
dann faellt das Geraet fuer Minuten aus, ohne dass der Nutzer versteht warum.
Direkt nach dem Anmelden hat er noch nichts angefangen, und er weiss zugleich,
warum das Geraet gerade langsam ist.

WARUM "NICHT JETZT" UND NICHT "SPAETER". Stephan wollte "spaeter" als
Widerspruch. Gegen das Modell geprueft, wie es die Projektregel verlangt:

    WARNING  Ignoring word missing in vocabulary: 'spaeter'
    WARNING  Ignoring word missing in vocabulary: 'spaet'

Das Wort steht NICHT im Wortschatz des kleinen Vosk-Modells. Ein Widerspruch
damit waere nie angekommen - der Nutzer sagt "spaeter", und das Geraet startet
trotzdem neu. Das waere derselbe lautlose Fehlschlag, den DialOS am 2026-08-24
abgeschafft hat, nur an einer Stelle, wo er teurer ist. Vorhanden und geprueft
sind: warten, moment, nicht jetzt, stopp, gleich, abbrechen, weiter, pause, ja,
nein. Gewaehlt: "nicht jetzt" - zwei Woerter wie beim Einschalten, damit ein
beilaeufiges Wort nicht dazwischenfunkt. "stopp" faellt aus, es gehoert schon
zum Ausschalten der Sprachsteuerung.

Aufruf:
    dialos-update-lauf.py            beim Anmelden (Autostart)
    dialos-update-lauf.py --pruefen  nur sagen, ob faellig - nichts tun
    dialos-update-lauf.py --jetzt    ohne Faelligkeitspruefung, fuer Tests
"""

import datetime
import json
import os
import subprocess
import sys
import time

SKRIPT = "/usr/local/sbin/dialos-systemupdate"
SAY = "/usr/local/bin/dialos-say.py"
MODELL_KLEIN = "/usr/local/share/vosk-model-de-small"
ABTASTRATE = 16000
ZULETZT = "/var/lib/dialos/systemupdate-zuletzt"

# ABSTAND UND WOCHENTAG (Stephan: "alle 14 Tage ... das immer am Montag, bzw.
# wenn dann der Computer das erste mal gestartet wird").
ABSTAND_TAGE = 14
WOCHENTAG = 0                       # 0 = Montag

# Zehn Sekunden Widerspruch - Stephans Vorgabe. Danach laeuft es durch.
WIDERSPRUCH_S = 10.0
# ensure_ascii=False IST PFLICHT (Fehler gefunden 2026-09-14). Ohne das schreibt
# json.dumps ein "ö" als "\\u00f6", Vosk liest das woertlich und meldet
# "Ignoring word missing in vocabulary" - fuer JEDES Wort mit Umlaut oder ß.
# Genau daraus entstanden die Befunde "spaeter", "loeschen", "zuruecksetzen"
# und "aufraeumen fehlen im Wortschatz". Sie fehlen nicht.
WIDERSPRUCH = json.dumps(["nicht jetzt", "[unk]"], ensure_ascii=False)

ANSAGE_START = ("Es müssen ein paar Updates installiert werden. "
                "Das kann einige Minuten dauern. "
                "Wenn das jetzt nicht passt, sag: nicht jetzt.")
ANSAGE_SPAETER = "Gut, dann später."
ANSAGE_NEUSTART = "Die Updates sind installiert. Der Computer startet jetzt neu."
ANSAGE_OHNE_STICK = ("Die Updates sind installiert. Der Computer wird beim "
                     "nächsten Start fertig.")
ANSAGE_FEHLER = "Die Updates konnten nicht installiert werden."

PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-update.log")

# KEINE MERKDATEI MEHR HIER (seit 2026-09-14). Die erste Fassung schrieb sie
# ins Heimatverzeichnis dessen, der das Update ausloeste - und wer sich nach
# dem Neustart als Erster unter einem ANDEREN Konto anmeldete, hoerte den Satz
# nie. Den Zeitstempel schreibt jetzt dialos-systemupdate nach
# /var/lib/dialos/systemupdate-installiert, und jede Start-Ansage quittiert ihn
# pro Person. Begruendung in dialos-start-ansage.py bei update_meldung().

# Dieselbe Marke wie beim Diktat und bei der Ja/Nein-Rueckfrage. Sie bedeutet
# nicht "ein Diktat laeuft", sondern "ein anderer Dienst hoert gerade zu" -
# der Befehlsdienst haelt sich dann heraus, statt auf dieselbe Quelle zu
# lauschen und den Widerspruch als Befehl zu deuten.
def marke_pfad(name):
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, name)
    return f"/tmp/{name}-{os.getuid()}"


FREMDE_AUFNAHME_MARKE = marke_pfad("dialos-diktat-aktiv")


def warten_bis_still(grenze_s=180.0):
    """Wartet, bis die Start-Ansage zu Ende gesprochen hat.

    Beide laufen ueber denselben Autostart-Mechanismus und starten praktisch
    gleichzeitig. Ohne dieses Warten redete die Update-Ansage in die
    Begruessung hinein - und der Nutzer bekaeme zwei Stimmen gleichzeitig zu
    hoeren, von denen eine nach einer Antwort verlangt.

    Die Markierung setzt dialos-say.py fuer die Dauer jeder Ansage. Sie ist
    dieselbe, an der sich auch der Befehlsdienst orientiert.

    Mit Zeitgrenze: Bleibt die Markierung durch einen Absturz liegen, soll die
    Aktualisierung nicht ewig warten, sondern nach drei Minuten trotzdem
    anfangen.
    """
    marke = marke_pfad("dialos-sprachausgabe-aktiv")
    ende = time.time() + grenze_s
    # Kurz warten, BEVOR geprueft wird: Beim Anmelden ist die Start-Ansage
    # vielleicht noch gar nicht so weit, ihre Markierung zu setzen.
    time.sleep(10)
    while os.path.exists(marke) and time.time() < ende:
        time.sleep(2)
    # Und noch ein Moment Ruhe, damit die beiden Ansagen nicht aneinander
    # kleben.
    time.sleep(2)


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


def sprich(text):
    """Ansage - und wenn die Sprachausgabe streikt, wenigstens ins Protokoll."""
    try:
        subprocess.run([SAY, text], capture_output=True, timeout=120)
    except Exception as fehler:
        melde(f"Ansage nicht moeglich: {fehler}")


def zuletzt_gelaufen():
    """Datum des letzten erfolgreichen Laufs, oder None."""
    try:
        with open(ZULETZT, encoding="utf-8") as f:
            return datetime.date.fromisoformat(f.read().strip())
    except (OSError, ValueError):
        return None


def faellig(heute=None):
    """Ist heute der Tag? Montags, alle 14 Tage, mit Nachholen.

    DIE RECHNUNG, damit sie nachvollziehbar bleibt:
      1. Faellig wird es ABSTAND_TAGE nach dem letzten Lauf.
      2. Getan wird es am ersten MONTAG ab diesem Tag.
      3. War der Computer an diesem Montag aus, ist "heute" spaeter als der
         Montag - und dann laeuft es beim ersten Start nach. Genau das meinte
         Stephan mit "bzw. wenn dann der Computer das erste mal gestartet
         wird".

    Ohne einen letzten Lauf ist es sofort faellig: Ein frisch aufgesetztes
    Geraet soll nicht bis zum uebernaechsten Montag auf dem Auslieferungsstand
    bleiben.
    """
    heute = heute or datetime.date.today()
    letzter = zuletzt_gelaufen()
    if letzter is None:
        return True
    ab = letzter + datetime.timedelta(days=ABSTAND_TAGE)
    # Erster Montag ab "ab" - wenn "ab" selbst ein Montag ist, dieser.
    montag = ab + datetime.timedelta(days=(WOCHENTAG - ab.weekday()) % 7)
    return heute >= montag


def offene_pakete():
    try:
        p = subprocess.run(["sudo", "-n", SKRIPT, "pruefen"],
                           capture_output=True, text=True, timeout=60)
        return int(p.stdout.strip() or 0)
    except Exception as fehler:
        melde(f"pruefen fehlgeschlagen: {fehler}")
        return 0


def widerspruch_hoeren():
    """Zehn Sekunden zuhoeren. True, wenn "nicht jetzt" kam.

    Beide Woerter noetig und kein "[unk]" - dieselbe Bedingung wie beim
    Einschalten der Sprachsteuerung. Ein einzelnes "nicht" aus einem
    Nebensatz soll die Aktualisierung nicht aufhalten; umgekehrt darf sie
    nicht durchlaufen, weil der Erkenner ein Wort verschluckt hat. Deshalb
    zaehlt jedes Ergebnis, das beide Woerter enthaelt, auch wenn noch etwas
    dabeisteht.
    """
    try:
        import vosk
    except ImportError:
        melde("vosk fehlt - kein Widerspruch moeglich")
        return False
    vosk.SetLogLevel(-1)

    quellen = subprocess.run(["pactl", "list", "short", "sources"],
                             capture_output=True, text=True, timeout=10).stdout
    quelle = ("dialos_mikrofon_ohne_echo"
              if "dialos_mikrofon_ohne_echo" in quellen else None)
    # "--latency-msec=30" (2026-09-14): sonst gingen von den zehn Sekunden
    # Widerspruch rund zwei an den Puffer von parec verloren.
    befehl = ["parec", "--format=s16le", f"--rate={ABTASTRATE}", "--channels=1",
              "--latency-msec=30"]
    if quelle:
        befehl += ["-d", quelle]

    open(FREMDE_AUFNAHME_MARKE, "w").close()
    try:
        modell = vosk.Model(MODELL_KLEIN)
        erkenner = vosk.KaldiRecognizer(modell, ABTASTRATE, WIDERSPRUCH)
        p = subprocess.Popen(befehl, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        ende = time.time() + WIDERSPRUCH_S
        try:
            while time.time() < ende:
                block = p.stdout.read(4000)
                if not block:
                    break
                if not erkenner.AcceptWaveform(block):
                    continue
                gehoert = json.loads(erkenner.Result()).get("text", "").strip()
                if not gehoert:
                    continue
                melde(f"  gehoert: {gehoert!r}")
                worte = gehoert.split()
                if "[unk]" in worte:
                    continue
                if "nicht" in worte and "jetzt" in worte:
                    return True
        finally:
            try:
                p.terminate()
            except Exception:
                pass
    except Exception as fehler:
        melde(f"Zuhoeren fehlgeschlagen: {fehler}")
    finally:
        try:
            os.unlink(FREMDE_AUFNAHME_MARKE)
        except OSError:
            pass
    return False


def main():
    argv = sys.argv[1:]
    if "--pruefen" in argv:
        letzter = zuletzt_gelaufen()
        print(f"letzter Lauf: {letzter or '(keiner)'}")
        print(f"faellig:      {faellig()}")
        print(f"offen:        {offene_pakete()} Paket(e)")
        return 0

    if "--jetzt" not in argv and not faellig():
        melde(f"nicht faellig (letzter Lauf {zuletzt_gelaufen()})")
        return 0

    offen = offene_pakete()
    if offen == 0:
        # Nichts zu tun - und BEWUSST ohne Ansage. Der Nutzer soll nicht
        # jeden zweiten Montag hoeren, dass nichts passiert ist.
        melde("faellig, aber nichts offen - keine Ansage")
        subprocess.run(["sudo", "-n", SKRIPT, "installieren"],
                       capture_output=True, timeout=300)
        return 0

    melde(f"=== faellig, {offen} Paket(e) offen ===")
    if "--jetzt" not in argv:
        warten_bis_still()
    sprich(ANSAGE_START)

    if widerspruch_hoeren():
        melde("Widerspruch: nicht jetzt")
        sprich(ANSAGE_SPAETER)
        # KEIN Datum merken: Damit ist es beim naechsten Anmelden wieder
        # faellig. Ein Widerspruch verschiebt um eine Sitzung, nicht um
        # vierzehn Tage - sonst koennte ein einziges "nicht jetzt" die
        # Aktualisierung zwei Wochen lang verhindern.
        return 0

    melde("installieren laeuft")
    p = subprocess.run(["sudo", "-n", SKRIPT, "installieren"],
                       capture_output=True, text=True, timeout=3600)
    if p.returncode != 0:
        melde(f"installieren fehlgeschlagen: {p.stderr.strip()[:200]}")
        sprich(ANSAGE_FEHLER)
        return 1

    melde("installiert - Neustart wird versucht")

    n = subprocess.run(["sudo", "-n", SKRIPT, "neustarten"],
                       capture_output=True, text=True, timeout=60)
    if n.returncode == 3 or "kein-update" in n.stdout:
        # Installiert wurde nichts - etwa weil unattended-upgrades die Pakete
        # zwischen Pruefen und Installieren schon eingespielt hatte. Dann gibt
        # es auch nichts neu zu starten, und der Rechner IST aktuell.
        melde("kein Update in diesem Start - kein Neustart")
        sprich("Der Computer ist auf dem neuesten Stand.")
        return 0
    if n.returncode == 2 or "kein-stick" in n.stdout:
        melde("kein Sicherheits-Stick - kein Neustart")
        sprich(ANSAGE_OHNE_STICK)
        return 0
    if n.returncode != 0:
        melde(f"Neustart fehlgeschlagen: {n.stderr.strip()[:200]}")
        sprich(ANSAGE_OHNE_STICK)
        return 1

    # Die Ansage laeuft, waehrend das Skript schon den Neustart eingeleitet
    # hat - es wartet vier Sekunden, damit der Satz zu Ende gesprochen wird.
    sprich(ANSAGE_NEUSTART)
    return 0


if __name__ == "__main__":
    sys.exit(main())
