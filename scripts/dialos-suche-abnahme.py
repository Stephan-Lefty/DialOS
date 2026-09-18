#!/usr/bin/env python3
"""DialOS: Abnahme der Erweiterungsschnittstelle und von DialOS-Suche.

WOZU: Nach dem Aufspielen steht die Frage "ist jetzt alles sauber?". Sie von
Hand zu beantworten hiess bisher: zwoelf Befehle tippen, jede Ausgabe selbst
deuten. Am 2026-09-18 ging dabei schon das Einfuegen schief - mehrere Zeilen
auf einmal verschmolzen im Terminal zu einer, und "cd: zu viele Argumente" war
alles, was davon uebrig blieb. Ein Befehl statt zwoelf loest beides.

WAS ES NICHT TUT: Es fasst nichts an. Keine Datei wird geschrieben, kein Dienst
neu gestartet, kein Index gebaut. Wer nach der Abnahme etwas reparieren will,
bekommt den Befehl dafuer genannt und fuehrt ihn selbst aus.

WAS ES NICHT PRUEFEN KANN: alles, wofuer ein Mensch ins Mikrofon sprechen
muss. Der Startsatz, die Mikrofon-Uebergabe und die Rueckgabe danach bleiben
Handarbeit; das Skript sagt am Ende, was davon offen ist, statt so zu tun, als
waere es erledigt.

DREI URTEILE, und die Unterscheidung ist der Punkt:
    OK       geprueft und in Ordnung
    FEHLER   geprueft und nicht in Ordnung - hier ist etwas zu tun
    OFFEN    nicht pruefbar, oder nur mit Mikrofon - KEIN Urteil

Die dritte Stufe gibt es, weil ein Werkzeug, das Ungeprueftes als "OK" zaehlt,
schlimmer ist als keines. Am 2026-09-17 sind genau zwei solche Stellen
aufgefallen - eine Wortschatzpruefung, die nie anlief, und eine Wache, die nie
griff. Beide sahen aus wie bestanden.

Aufruf:
    scripts/dialos-suche-abnahme.py            die schnellen Pruefungen (Sekunden)
    scripts/dialos-suche-abnahme.py --lang     dazu die Wortschatz-Gegenprobe
                                               (Piper spricht, Vosk hoert - Minuten)
"""

import json
import os
import subprocess
import sys
import time

# Was am Geraet liegen muss. Die Pfade stehen hier ausgeschrieben statt aus den
# Modulen importiert: Die Abnahme soll melden, wenn eine Datei FEHLT - ein
# Import daraus wuerde genau daran scheitern.
BIN = "/usr/local/bin"
SUCHE = f"{BIN}/dialos-suche.py"
INDEX = f"{BIN}/dialos-suche-index.py"
WERKZEUG = f"{BIN}/dialos-erweiterung.py"
PRUEFER = f"{BIN}/dialos-grammatik-pruefen.py"
DIENST = f"{BIN}/dialos-sprachbefehl-desktop.py"
MANIFEST_ORDNER = "/usr/local/share/dialos/erweiterungen"
MANIFEST = f"{MANIFEST_ORDNER}/dialos-suche.json"
STARTSATZ = "unterlagen durchsuchen"

PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-sprachbefehl.log")

# Dieselbe Datei, die dialos-suche.py setzt und der Befehlsdienst liest. Der
# Name ist historisch "Diktat", die Marke ist es laengst nicht mehr - sie sagt
# nur "ein anderes Programm hoert gerade zu".
MARKE = os.path.join(
    os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
    "dialos-diktat-aktiv")

ergebnisse = []


def urteil(stufe, titel, text="", befehl=""):
    ergebnisse.append((stufe, titel, text, befehl))
    zeichen = {"OK": "OK    ", "FEHLER": "FEHLER", "OFFEN": "OFFEN "}[stufe]
    print(f"  {zeichen}  {titel}")
    if text:
        for zeile in text.splitlines():
            print(f"            {zeile}")
    if befehl:
        print(f"            -> {befehl}")


def lauf(befehl, zeitgrenze=60):
    """(Rueckgabewert, Ausgabe). -1 heisst: liess sich nicht ausfuehren."""
    try:
        r = subprocess.run(befehl, capture_output=True, text=True,
                           timeout=zeitgrenze)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as fehler:
        return -1, str(fehler)


def abschnitt(titel):
    print(f"\n{titel}")
    print("-" * len(titel))


# ---------------------------------------------------------------------------

def pruefe_dateien():
    abschnitt("1. Liegt alles am Platz?")
    for pfad in (SUCHE, INDEX, WERKZEUG, DIENST):
        if os.access(pfad, os.X_OK):
            urteil("OK", pfad)
        elif os.path.exists(pfad):
            urteil("FEHLER", f"{pfad} ist nicht ausfuehrbar",
                   befehl=f"sudo chmod 755 {pfad}")
        else:
            urteil("FEHLER", f"{pfad} fehlt",
                   "Das Aufspielen hat diese Datei nicht gebracht.",
                   "sudo /usr/local/sbin/dialos-aufspielen --wirklich")

    if os.path.isfile(MANIFEST):
        urteil("OK", MANIFEST)
    else:
        urteil("FEHLER", f"{MANIFEST} fehlt",
               "Ohne Manifest kennt der Dienst die Erweiterung nicht.",
               "sudo /usr/local/sbin/dialos-aufspielen --wirklich")

    # DER PRUEFER IST DER SONDERFALL. Er wird von dialos-erweiterung.py unter
    # genau diesem Pfad erwartet - fehlt er, verweigert JEDES Einbauen einer
    # Erweiterung, weil Wortschatz und Kollisionen ungeprueft blieben.
    if os.access(PRUEFER, os.X_OK):
        urteil("OK", PRUEFER)
    else:
        urteil("FEHLER", f"{PRUEFER} fehlt",
               "dialos-erweiterung.py einbauen verweigert ohne ihn - zu Recht,\n"
               "aber damit laesst sich zurzeit keine Erweiterung einbauen.",
               "git pull im Repo, dann erneut aufspielen")


def pruefe_selbsttest():
    abschnitt("2. Selbsttest der Erweiterung")
    if not os.access(SUCHE, os.X_OK):
        urteil("OFFEN", "uebersprungen - dialos-suche.py fehlt")
        return
    code, ausgabe = lauf([SUCHE, "--pruefen"])
    fehlt = [z.strip() for z in ausgabe.splitlines() if z.startswith("FEHLT:")]
    if code == 0 and not fehlt:
        urteil("OK", "dialos-suche.py --pruefen: nichts fehlt")
    elif code == -1:
        urteil("FEHLER", "dialos-suche.py --pruefen liess sich nicht ausfuehren",
               ausgabe)
    else:
        urteil("FEHLER", "dialos-suche.py meldet fehlende Teile",
               "\n".join(fehlt) or ausgabe.strip())


def pruefe_manifest():
    abschnitt("3. Ist die Erweiterung angemeldet?")
    if not os.access(WERKZEUG, os.X_OK):
        urteil("OFFEN", "uebersprungen - dialos-erweiterung.py fehlt")
        return
    code, ausgabe = lauf([WERKZEUG, "liste"])
    if code != 0:
        urteil("FEHLER", "dialos-erweiterung.py liste schlaegt fehl", ausgabe.strip())
        return
    if "DialOS-Suche" not in ausgabe:
        urteil("FEHLER", "DialOS-Suche taucht in der Liste nicht auf",
               ausgabe.strip() or "(leere Liste)")
        return
    if STARTSATZ not in ausgabe:
        urteil("FEHLER", f"Startsatz '{STARTSATZ}' fehlt in der Liste",
               ausgabe.strip())
        return
    urteil("OK", f"DialOS-Suche ist angemeldet, Startsatz '{STARTSATZ}'")

    # Meldet das Werkzeug kaputte Manifeste? Die stehen in derselben Ausgabe
    # und werden leicht ueberlesen.
    if "kaputt" in ausgabe.lower() or "nicht lesbar" in ausgabe.lower():
        urteil("FEHLER", "Es liegt mindestens ein kaputtes Manifest im Ordner",
               ausgabe.strip())


def pruefe_dienst():
    """Laeuft der Befehlsdienst - und laeuft er in der NEUEN Fassung?

    Das ist die Pruefung, die am 2026-09-18 gefehlt haette. Der Dienst liest
    die Manifeste EINMAL, beim Start. Wird er nach dem Aufspielen nicht neu
    gestartet, laeuft er mit der alten Grammatik weiter: Die Erweiterung liegt
    installiert da, der Startsatz tut nichts, und es gibt weder Fehlermeldung
    noch Ansage. Fuer einen blinden Nutzer der schlechteste Ausgang.
    """
    abschnitt("4. Laeuft der Befehlsdienst in der neuen Fassung?")
    code, ausgabe = lauf(["pgrep", "-f", f"python3 {DIENST}"])
    pids = [p for p in ausgabe.split() if p.isdigit()] if code == 0 else []
    if not pids:
        urteil("FEHLER", "Der Befehlsdienst laeuft nicht",
               "Ohne ihn reagiert das Geraet auf gar keinen Sprachbefehl.",
               f"setsid {DIENST} >/dev/null 2>&1 &")
        return

    # Startzeit des Prozesses gegen die Aenderungszeit der Dateien, die er
    # beim Start liest. /proc/PID/stat waere genauer, ps ist lesbarer - und
    # die Frage ist grob: Minuten, nicht Millisekunden.
    code, ausgabe = lauf(["ps", "-o", "lstart=", "-p", pids[0]])
    gestartet = None
    try:
        gestartet = time.mktime(time.strptime(ausgabe.strip()))
    except (ValueError, OverflowError):
        pass

    neuer = []
    for pfad in (MANIFEST, DIENST, WERKZEUG):
        try:
            if gestartet and os.path.getmtime(pfad) > gestartet:
                neuer.append(pfad)
        except OSError:
            pass

    if gestartet is None:
        urteil("OFFEN", f"Dienst laeuft (PID {pids[0]}), Startzeit nicht lesbar",
               "Ob er die aktuelle Grammatik hat, bleibt hier ungeprueft.")
    elif neuer:
        urteil("FEHLER", "Der Dienst ist AELTER als die aufgespielten Dateien",
               "Er laeuft mit der alten Grammatik - der Startsatz tut nichts,\n"
               "lautlos. Neuer als der Dienststart:\n  "
               + "\n  ".join(neuer),
               f"pkill -f 'python3 {DIENST}' && setsid {DIENST} >/dev/null 2>&1 &")
    else:
        alter = (time.time() - gestartet) / 60
        urteil("OK", f"Dienst laeuft (PID {pids[0]}, seit {alter:.0f} min), "
                     "neuer als Manifest und Dienstdatei")

    # Hat der Dienst die Erweiterungen beim Start ueberhaupt lesen koennen?
    # Er faengt jeden Fehler ab, damit ein kaputtes Manifest die
    # Sprachsteuerung nicht mitreisst - gemeldet wird er trotzdem.
    if os.path.isfile(PROTOKOLL):
        try:
            with open(PROTOKOLL, encoding="utf-8", errors="replace") as f:
                inhalt = f.read()[-200_000:]
            if "Erweiterungen nicht lesbar" in inhalt:
                urteil("FEHLER", "Im Protokoll steht 'Erweiterungen nicht lesbar'",
                       "Der Dienst laeuft, kennt aber keine Erweiterung.",
                       f"grep 'Erweiterungen nicht lesbar' {PROTOKOLL}")
        except OSError:
            pass


def pruefe_marke():
    """Haengt gerade eine verwaiste Mikrofon-Marke?

    Wenn ja, halten Diktat, Notiz UND Suche das Mikrofon fuer belegt, und die
    Sprachsteuerung schweigt - der Fehler, gegen den die Wache gebaut wurde.
    """
    abschnitt("5. Ist das Mikrofon frei?")
    if not os.path.exists(MARKE):
        urteil("OK", "keine Mikrofon-Marke - das Mikrofon ist frei")
        return
    try:
        with open(MARKE, encoding="utf-8") as f:
            erste = f.readline().split()
        pid = int(erste[0])
    except (OSError, ValueError, IndexError):
        urteil("FEHLER", "Eine Marke liegt da, OHNE PID",
               "Sie stammt von dialos-diktat.py oder dialos-notiz.py - die\n"
               "schreiben noch keine PID hinein, deshalb kann die Wache sie\n"
               "nicht wegraeumen. Laeuft gerade nichts, ist sie verwaist.",
               f"rm {MARKE}")
        return
    try:
        os.kill(pid, 0)
        urteil("OK", f"Marke von PID {pid} - der Prozess lebt, "
                     "es hoert gerade jemand zu")
    except ProcessLookupError:
        urteil("FEHLER", f"VERWAISTE Marke von PID {pid} - der Prozess ist tot",
               "Die Sprachsteuerung haelt das Mikrofon fuer belegt. Die Wache\n"
               "raeumt sie beim naechsten Befehlsversuch weg; bleibt sie\n"
               "liegen, hat die Wache nicht gegriffen.",
               f"rm {MARKE}")
    except PermissionError:
        urteil("OK", f"Marke von PID {pid} - Prozess lebt (fremder Nutzer)")


def pruefe_wache():
    """Hat die Wache jemals gegriffen?

    Kein Urteil, sondern ein Befund: Steht die Zeile im Protokoll, ist sie
    mindestens einmal angelaufen. Steht sie nicht, heisst das nur, dass es
    noch keinen harten Abbruch gab - nicht, dass die Wache kaputt ist.
    """
    abschnitt("6. Ist die Wache schon einmal angelaufen?")
    if not os.path.isfile(PROTOKOLL):
        urteil("OFFEN", f"Kein Protokoll unter {PROTOKOLL}")
        return
    try:
        with open(PROTOKOLL, encoding="utf-8", errors="replace") as f:
            zeilen = [z.strip() for z in f
                      if "verwaiste Mikrofon-Marke" in z]
    except OSError as fehler:
        urteil("OFFEN", f"Protokoll nicht lesbar: {fehler}")
        return
    if zeilen:
        urteil("OK", f"{len(zeilen)}x im Protokoll - die Wache greift",
               "\n".join(zeilen[-2:]))
    else:
        urteil("OFFEN", "Noch nie angelaufen",
               "Das ist erwartbar, solange nichts hart abgebrochen wurde.\n"
               "Zum Pruefen: dialos-suche.py waehrend der Suche mit\n"
               "'pkill -9 -f dialos-suche.py' abschiessen, dann einen Befehl\n"
               "geben und hier erneut nachsehen.")


def pruefe_index():
    abschnitt("7. Steht der Suchindex?")
    if not os.access(INDEX, os.X_OK):
        urteil("OFFEN", "uebersprungen - dialos-suche-index.py fehlt")
        return
    code, ausgabe = lauf([INDEX, "stand"])
    if code != 0:
        urteil("FEHLER", "dialos-suche-index.py stand schlaegt fehl",
               ausgabe.strip())
        return

    anzahl = 0
    for zeile in ausgabe.splitlines():
        if zeile.startswith("Dateien:"):
            try:
                anzahl = int(zeile.split()[1])
            except (IndexError, ValueError):
                pass
    print("            " + "\n            ".join(ausgabe.strip().splitlines()))
    if anzahl == 0:
        urteil("FEHLER", "Der Index ist leer",
               "Jede Suche findet nichts - das sagt ueber die Suche nichts aus.",
               f"{INDEX} aufbauen --debug")
    else:
        urteil("OK", f"{anzahl} Dateien im Index")

    if "FEHLT" in ausgabe:
        urteil("OFFEN", "MailBurgs extract/ fehlt",
               "Kein OCR, keine Office-Dateien; PDFs laufen nur ueber\n"
               "pdftotext. Kein Fehler - aber gescannte Briefe bleiben stumm.")

    if anzahl:
        # Eine echte Suche, nicht nur der Stand. Ein Wort, das in fast jedem
        # Archiv vorkommt; findet es nichts, ist das ein Hinweis, kein Urteil.
        code, ausgabe = lauf([INDEX, "suchen", "rechnung"])
        try:
            treffer = json.loads(ausgabe)
        except ValueError:
            urteil("FEHLER", "Die Suche liefert kein gueltiges JSON",
                   ausgabe.strip()[:400])
            return
        wie = {t.get("wie") for t in treffer} if isinstance(treffer, list) else set()
        if treffer:
            urteil("OK", f"Suche nach 'rechnung': {len(treffer)} Treffer, "
                         f"Herkunft {sorted(w for w in wie if w)}")
        else:
            urteil("OFFEN", "Suche nach 'rechnung' findet nichts",
                   "Kann am Archiv liegen. Mit einem Wort gegenpruefen, das\n"
                   "sicher in einem Dokument steht.")


def pruefe_wortschatz():
    """Die Gegenprobe, bei der Bestehen heisst: sie weist ab.

    Am 2026-09-17 lief diese Pruefung monatelang, ohne irgendetwas zu pruefen -
    sie las eine Datei, die im kleinen Modell gar nicht existiert. Ein
    Durchlauf ohne Befund war damals das FALSCHE Ergebnis. Deshalb steht sie
    hier so, dass ein Durchlauf als FEHLER gilt.
    """
    abschnitt("8. Wortschatz-Gegenprobe (das dauert)")
    # Zweiter Ort: der Aufspielbaum im Repo. Damit laeuft die Gegenprobe auch
    # auf einem Geraet, auf dem noch nicht aufgespielt wurde - sonst haette
    # ausgerechnet die wichtigste Pruefung das Aufspielen zur Voraussetzung.
    wurzel = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_pruefer = os.path.join(
        wurzel, "iso-build/config/includes.chroot/usr/local/bin",
        "dialos-grammatik-pruefen.py")
    werkzeug = PRUEFER if os.access(PRUEFER, os.X_OK) else repo_pruefer
    if not os.access(werkzeug, os.X_OK):
        urteil("OFFEN", "uebersprungen - kein Grammatik-Pruefwerkzeug gefunden")
        return
    print(f"  laeuft: {werkzeug} --neu 'xylofonquark durchsuchen'")
    code, ausgabe = lauf([werkzeug, "--neu", "xylofonquark durchsuchen"],
                         zeitgrenze=1800)
    if code == -1:
        urteil("FEHLER", "Die Gegenprobe liess sich nicht ausfuehren", ausgabe)
    elif code == 0:
        urteil("FEHLER", "Die Gegenprobe ist DURCHGELAUFEN",
               "'xylofonquark' steht in keinem Wortschatz. Dass die Pruefung\n"
               "das durchwinkt, heisst: sie prueft den Wortschatz nicht.\n"
               "Das ist der wichtigste Befund dieser Abnahme.")
    elif "NICHT IM WORTSCHATZ" in ausgabe.upper():
        urteil("OK", "Abgewiesen mit der erwarteten Begruendung "
                     "(Rueckgabewert 1)")
    else:
        urteil("OFFEN", f"Abgewiesen, aber anders als erwartet "
                        f"(Rueckgabewert {code})",
               "\n".join(ausgabe.strip().splitlines()[-6:]))


def main():
    lang = "--lang" in sys.argv[1:]
    print("Abnahme: Erweiterungsschnittstelle und DialOS-Suche")
    print(f"Geraet:  {os.uname().nodename}")

    pruefe_dateien()
    pruefe_selbsttest()
    pruefe_manifest()
    pruefe_dienst()
    pruefe_marke()
    pruefe_wache()
    pruefe_index()
    if lang:
        pruefe_wortschatz()
    else:
        abschnitt("8. Wortschatz-Gegenprobe")
        urteil("OFFEN", "uebersprungen - mit --lang mitlaufen lassen",
               "Sie dauert Minuten, weil Piper spricht und Vosk hoert.")

    abschnitt("Was nur mit Mikrofon geht")
    for satz in (
            f"'{STARTSATZ}' zurufen - die Erweiterung muss starten und "
            "'Wonach soll ich suchen?' fragen",
            "Suchbegriff sprechen - Anzahl und neuester Treffer werden angesagt",
            "Danach einen normalen Befehl geben - das Mikrofon muss zurueck sein",
            "Einen Namen suchen, der im Archiv anders geschrieben ist "
            "(Meier/Mayer) - muss ueber den Klang gefunden werden"):
        print(f"  OFFEN   {satz}")

    fehler = [e for e in ergebnisse if e[0] == "FEHLER"]
    offen = [e for e in ergebnisse if e[0] == "OFFEN"]
    abschnitt("Ergebnis")
    print(f"  {len(ergebnisse) - len(fehler) - len(offen)} in Ordnung, "
          f"{len(fehler)} Fehler, {len(offen)} offen (nicht geprueft)")
    if fehler:
        print("\n  Zu tun:")
        for _stufe, titel, _text, befehl in fehler:
            print(f"    - {titel}")
            if befehl:
                print(f"      {befehl}")
    else:
        print("\n  Kein Fehler in dem, was sich ohne Mikrofon pruefen laesst.")
        print("  Das Ungepruefte steht oben unter OFFEN - es ist nicht "
              "dasselbe wie bestanden.")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
