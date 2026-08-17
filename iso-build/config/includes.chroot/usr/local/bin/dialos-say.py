#!/usr/bin/env python3
"""DialOS: Sprachausgabe mit Audio-Ducking.

Schaltet andere Audioquellen (z.B. Radio, Musik) waehrend der Sprachausgabe
stumm und stellt sie danach wieder her. Speech-Dispatcher-eigene Streams
werden dabei bewusst ausgenommen.

Legt zusaetzlich waehrend der Sprachausgabe eine Markierungsdatei an (und
entfernt sie wieder, auch bei Fehlern und bei Zeitueberschreitung) - darauf
reagiert dialos-tts-indicator.py mit einem Icon im GNOME-Panel, nuetzlich
falls die Lautstaerke zu leise eingestellt ist.
"""
import json
import os
import re
import subprocess
import sys


# Aussprache-Regeln fuer Piper. Jede Zeile: Muster, Ersatz, Begruendung.
# Die Begruendung steht bewusst mit im Code - ohne sie sieht eine solche
# Regel spaeter wie ein Tippfehler aus und wird "korrigiert".
AUSSPRACHE = [
    (
        re.compile(r"\bDialOS\b(?!\.)", re.IGNORECASE),
        "Dial OS",
        "Sonst als ein Wort gelesen; gemeint ist 'Dial O S'.",
    ),
    (
        # Deutsch spricht "st" am Silbenanfang als "scht". Piper setzt die
        # Silbengrenze bei "Ta-statur" und sagt deshalb "Taschtatur".
        # Getrennt geschrieben liegt das s am Silbenende, das t beginnt neu -
        # damit stimmt es. Von Stephan im Hoervergleich aus fuenf Schreib-
        # weisen ausgewaehlt (2026-08-17).
        re.compile(r"\bTastatur(en)?\b", re.IGNORECASE),
        r"Tas tatur\1",
        "Sonst 'Taschtatur' - falsche Silbengrenze.",
    ),
]


def fuer_sprachausgabe(text):
    """Schreibweisen anpassen, die Piper sonst falsch ausspricht.

    "DialOS" wuerde als ein Wort gelesen. Getrennt geschrieben spricht die
    Stimme es als "Dial OS", was gemeint ist.

    Bewusst ZENTRAL hier statt in den einzelnen Texten: So kann keine
    kuenftige Ansage die Trennung vergessen, und die Texte selbst bleiben
    im Quelltext korrekt geschrieben. Wer eine weitere Aussprache-Regel
    braucht, ergaenzt sie an dieser einen Stelle.

    Wortgrenze und die Ausnahme fuer den Punkt sind wichtig:
      "dialosadmin"     bleibt - kein Wortende nach "dialos"
      "dialos.org"      bleibt - der Lookahead schliesst den Punkt aus
      "DialOS-System"   wird getrennt - richtig so, es ist gesprochener Text
    Ein Bindestrich IST eine Wortgrenze, "dialos-say.py" wuerde also
    ebenfalls getrennt. Das ist folgenlos: Skript- und Dateinamen kommen
    in gesprochenen Texten nicht vor, nur in Kommentaren und Pfaden - und
    die laufen nie durch diese Funktion.

    Seit 2026-08-17 eine Liste statt einer einzelnen Ersetzung: Es kam die
    zweite Regel dazu, und es werden weitere kommen. Neue Regel = eine
    Zeile in AUSSPRACHE, mit einem Satz dazu, WARUM sie noetig ist.
    """
    for muster, ersatz, _grund in AUSSPRACHE:
        text = muster.sub(ersatz, text)
    return text


def markierungsdatei():
    """Pro Konto eigener Pfad - bewusst NICHT ein fester Name in /tmp.

    Bis 2026-08-16 stand hier "/tmp/dialos-sprachausgabe-aktiv", also ein
    fester Pfad, den sich ALLE Konten teilen. Live beobachtet: nutzers
    Ansage legte die Datei an, danach zeigte auch dialosadmins Panel
    dauerhaft das Sprechen-Icon - obwohl dort nichts lief. Schlimmer:
    /tmp hat das Sticky-Bit, dialosadmin konnte nutzers Datei also gar
    nicht entfernen, und markierung_setzen() scheiterte still am
    fehlenden Schreibrecht.

    XDG_RUNTIME_DIR (/run/user/<uid>) ist pro Konto privat und wird beim
    Abmelden automatisch geleert - genau richtig fuer eine Markierung,
    die nur waehrend einer Sitzung gilt.
    """
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, "dialos-sprachausgabe-aktiv")
    # Rueckfall: eigener Name je Konto, damit sich auch hier nichts
    # zwischen zwei Konten in die Quere kommt.
    return f"/tmp/dialos-sprachausgabe-aktiv-{os.getuid()}"


MARKIERUNGSDATEI = markierungsdatei()

# Zeitgrenzen fuer spd-say. Ohne sie kann ein haengendes "spd-say --wait"
# das ganze Skript blockieren - und dann laeuft der finally-Block NIE, die
# stummgeschalteten Audioquellen bleiben also dauerhaft stumm und das
# Panel-Icon dauerhaft an. Genau das ist am 2026-08-16 passiert: Waehrend
# die Sprachausgabe defekt war (fehlendes check_piper_voice.sh), wartete
# spd-say auf ein Ende-Signal, das nie kam - der Prozess stand nach 75
# Minuten immer noch.
AUFWAERM_TIMEOUT_S = 20
# Grundzeit plus Zuschlag nach Textlaenge: die Start-Ansage ist rund 450
# Zeichen lang und braucht bei Sprechtempo 0.85 etwa 40 Sekunden.
TEXT_TIMEOUT_GRUND_S = 60
TEXT_TIMEOUT_MAX_S = 300


def sink_inputs():
    try:
        out = subprocess.run(
            ["pactl", "-f", "json", "list", "sink-inputs"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        return json.loads(out) if out.strip() else []
    except Exception:
        return []


def set_mute(index, stumm):
    subprocess.run(
        ["pactl", "set-sink-input-mute", str(index), "1" if stumm else "0"],
        capture_output=True, timeout=5,
    )


def ist_speech_dispatcher(stream):
    name = stream.get("properties", {}).get("application.name", "")
    return name.startswith("speech-dispatcher")


def markierung_setzen():
    try:
        open(MARKIERUNGSDATEI, "w").close()
    except Exception:
        pass


def markierung_entfernen():
    try:
        os.remove(MARKIERUNGSDATEI)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def sprich(cmd, grenze_s):
    """spd-say mit Zeitgrenze aufrufen.

    Laeuft die Grenze ab, beendet subprocess.run den Prozess und wirft
    TimeoutExpired - das faengt diese Funktion ab, damit der Aufrufer
    normal weiterlaeuft und vor allem sein finally erreicht. Eine
    hakelnde Sprachausgabe darf niemals dazu fuehren, dass die Audio-
    Stummschaltung nicht wieder aufgehoben wird.
    """
    try:
        subprocess.run(cmd, timeout=grenze_s)
        return True
    except subprocess.TimeoutExpired:
        print(
            f"[dialos-say] spd-say nach {grenze_s}s abgebrochen - "
            "Sprachausgabe antwortet nicht.",
            file=sys.stderr,
        )
        return False
    except Exception as fehler:
        print(f"[dialos-say] spd-say fehlgeschlagen: {fehler}", file=sys.stderr)
        return False


def main():
    argv = sys.argv[1:]
    intensitaet = None
    if argv and argv[0] == "--lautstaerke":
        # Speech-Dispatcher-Lautstaerke (-i, "Intensitaet"), -100 bis
        # +100, siehe dialos-start-ansage.py fuer die Prozent-Zuordnung.
        try:
            intensitaet = int(argv[1])
        except (IndexError, ValueError):
            intensitaet = None
        argv = argv[2:]
    text = fuer_sprachausgabe(" ".join(argv))
    if not text:
        return
    streams = sink_inputs()
    stummgeschaltet = []
    for stream in streams:
        index = stream.get("index")
        if index is None or ist_speech_dispatcher(stream):
            continue
        if not stream.get("mute", False):
            set_mute(index, True)
            stummgeschaltet.append(index)
    markierung_setzen()
    try:
        # Kurze "Aufwaerm"-Ansage, damit ein evtl. eingeschlafener
        # Bluetooth-Lautsprecher rechtzeitig aufwacht, bevor der
        # eigentliche Text gesprochen wird (sonst geht der Anfang verloren).
        spd_cmd = ["spd-say", "--wait"]
        if intensitaet is not None:
            spd_cmd += ["-i", str(intensitaet)]
        text_timeout = min(
            TEXT_TIMEOUT_MAX_S, TEXT_TIMEOUT_GRUND_S + len(text) // 10
        )
        # Auch wenn die Aufwaerm-Ansage in eine Zeitgrenze laeuft, wird der
        # eigentliche Text noch versucht: vielleicht hakte nur der erste
        # Aufruf, und eine ausbleibende Ansage waere fuer einen blinden
        # Nutzer schlimmer als eine verspaetete.
        sprich(spd_cmd + ["."], AUFWAERM_TIMEOUT_S)
        sprich(spd_cmd + [text], text_timeout)
    finally:
        for index in stummgeschaltet:
            set_mute(index, False)
        markierung_entfernen()


if __name__ == "__main__":
    main()
