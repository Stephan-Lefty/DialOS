#!/usr/bin/env python3
"""DialOS: Mitschrift - was gerade passiert, fuer sehende Zuschauer.

Stephans Wunsch vom 2026-08-19: ein Fenster, das dokumentiert, was die
Sprachsteuerung tut. Fuer einen sehenden Helfer, fuer Vorfuehrungen, und um
einem blinden Nutzer am Telefon sagen zu koennen, was das Geraet gerade
gehoert hat.

AUF UND ZU MIT DER SPRACHSTEUERUNG (Stephans Praezisierung vom 2026-08-19).
Das Fenster geht auf, wenn die Sprachsteuerung eingeschaltet wird, und zu, wenn
sie ausgeht - von Hand oder durch die Zeitgrenze. Nicht bei jedem einzelnen
Befehl: das wuerde beim Diktieren stoeren und den Fokus stehlen, und wer
diktiert, hat den Bildschirm ohnehin nicht im Blick. Einmal pro Sitzung
aufgehen ist unauffaellig; bei jedem Satz aufspringen waere es nicht.

Geoeffnet und geschlossen wird das Fenster von
`dialos-sprachbefehl-desktop.py` - es haengt an der Sprachsteuerung, nicht
umgekehrt. Geschlossen wird durch Beenden DIESES Skripts; das Terminal-Fenster
schliesst sich dann von selbst, weil sein Befehl endet. So laesst sich ein
Fenster schliessen, ohne dessen Fenster-ID zu kennen - gnome-terminal spaltet
sich vom Aufruf ab, seine eigene PID hilft also nicht weiter.

SUPPORT-PROTOKOLL (Stephans Wunsch vom 2026-08-19). Was hier durchlaeuft, wird
zusaetzlich in eine Tagesdatei geschrieben - damit man beim Anruf nachlesen
kann, was das Geraet wirklich gehoert hat, statt sich auf die Erinnerung zu
verlassen. Eine Datei pro Tag, sieben Tage lang, dann geht die aelteste von
selbst weg.

WAS VOM INHALT HINEINKOMMT - und was nicht (Stephans Praezisierung vom
2026-08-19): die Befehle vollstaendig, vom Diktierten die ERSTE Zeile und
danach nur noch die Anzahl. `~/dialos-diktat.log` enthaelt jeden diktierten
Satz woertlich, also den ganzen Brief; eine Datei fuer einen fremden Helfer
darf die Post des Nutzers nicht enthalten. Eine Zeile genuegt aber, um im
Support zu erkennen, dass ueberhaupt etwas erfasst wurde - und ob es Sinn
ergab. Im Fenster steht weiter alles, denn dort sieht es nur, wer ohnehin vor
dem Geraet sitzt.

DER ZUSAMMENHANG IST DAS WICHTIGSTE (Stephan, 2026-08-19). „Milch“
allein sagt niemandem etwas, „Einkaufszettel: Milch“ sagt alles.
Deshalb steht vor jedem Abschnitt, worum es gerade ging - Diktat,
Einkaufszettel, Frage an das System, spaeter Mail und Brief. Der Zusammenhang
wird nicht geraten, sondern aus den Zeilen mitgefuehrt, die die Programme beim
Starten selbst schreiben.

WARUM EIN FILTER UND KEIN "tail -f": Das Befehlsprotokoll bestand am
2026-08-19 aus 4132 Pegel-Zeilen gegen 13 echte. Ein rohes tail waere
unlesbar. Dieses Skript wirft die Pegelanzeige weg und uebersetzt die
Protokollzeilen in Saetze, die auch jemand versteht, der den Quelltext nicht
kennt.

VIER QUELLEN, EINE ZEITACHSE. Befehlsdienst, Diktat, Auskunft und Notizen
schreiben getrennte Protokolle - hier laufen sie zusammen und werden nach
Uhrzeit gemischt. Genau dieses Zusammenfuehren hat am 2026-08-18 den Beweis
gebracht, dass sich Diktat und Befehlserkennung nicht ins Gehege kommen; von
Hand war es muehsam.

Aufruf:  dialos-mitschrift.py             (folgt laufend)
         dialos-mitschrift.py --alles     (zeigt auch, was vorher schon da war)
         dialos-mitschrift.py --kein-protokoll  (nichts fuer den Support schreiben)
         dialos-mitschrift.py --rueckblick 15   (die letzten 15 Sekunden mitnehmen)
"""

import datetime
import os
import re
import sys
import time

HEIM = os.path.expanduser("~")
QUELLEN = {
    "Sprache":  os.path.join(HEIM, "dialos-sprachbefehl.log"),
    "Diktat":   os.path.join(HEIM, "dialos-diktat.log"),
    "Auskunft": os.path.join(HEIM, "dialos-auskunft.log"),
    "Notiz":    os.path.join(HEIM, "dialos-notiz.log"),
}

# Zeilen, die niemanden interessieren. Die Pegelanzeige ist eine laufende
# Messung fuers Entwickeln. Und "=== vorlesen einkaufszettel ===" ist die
# Kopfzeile von dialos-notiz.py: dieselbe Aussage wie die uebersetzte Zeile des
# Befehlsdienstes unmittelbar davor, nur unuebersetzt (2026-08-19).
VERWERFEN = re.compile(r'^\s*(Pegel\s|=== (vorlesen|loeschen) \w+ ===|$)')

# Uebersetzungen. Links steht, was im Protokoll steht, rechts, was ein
# Zuschauer lesen soll - in dieser Reihenfolge geprueft.
UEBERSETZUNG = [
    (re.compile(r"erkannt: '(.+)'"),                    "gehört: \u201e{}\u201c"),
    (re.compile(r"erkannt:\s+'(.+)'"),                  "diktiert: \u201e{}\u201c"),
    (re.compile(r"geschrieben:\s+'(.+)'"),              "geschrieben: \u201e{}\u201c"),
    (re.compile(r"Diktat gestartet fuer Notiz '(.+)'"), "Diktat begonnen für \u201e{}\u201c"),
    (re.compile(r"Auskunft '(.+)' gestartet"),          "Auskunft: {}"),
    (re.compile(r"Notiz-Aktion '(.+)' fuer '(.+)' gestartet"), "{1}: {0}"),
    (re.compile(r"Schlusssatz erkannt.*?: '(.+)'"),     "Diktat beendet durch \u201e{}\u201c"),
    (re.compile(r"anderer Dienst hoert zu.*"),          "Befehle sind still - ein anderer Dienst hört zu"),
    (re.compile(r"anderer Dienst fertig.*"),            "Befehle hören wieder zu"),
    (re.compile(r"\(Aufnahme nach Sprechpause neu begonnen\)"), "Aufnahme neu begonnen"),
    # Warum die Sitzung endet, ist die wichtigste Zeile fuer den Support - und
    # stand bis zum 2026-08-19 gar nicht im Protokoll.
    (re.compile(r"Zeitgrenze: (\d+) s ohne Befehl"),
     "Zeitgrenze: {} s ohne Befehl - Sprachsteuerung schaltet ab"),
    (re.compile(r"Mitschrift wird geschlossen.*"), "Mitschrift wird geschlossen"),
    (re.compile(r"grosses Modell geladen in (.+)"),     "Sprachmodell geladen ({})"),
    (re.compile(r"kleines Modell fuer den Schlusssatz in (.+)"), "Schluss-Erkenner bereit ({})"),
    (re.compile(r"=== Diktat gestartet \((.+?),\s*(.+?)\).*"), "Diktat läuft ({1})"),
    (re.compile(r"=== (uhrzeit|datum) ==="),            "Frage: {}"),
    (re.compile(r"uhrzeit: (.+)"),                      "Antwort: {}"),
    (re.compile(r"datum: (.+)"),                        "Antwort: {}"),
    (re.compile(r"geschrieben nach (.+)"),              "gespeichert in {}"),
    (re.compile(r"\(Schluss-Erkenner: '(.+)' - kein Schluss\)"), "kein Schlusssatz (\u201e{}\u201c)"),
    (re.compile(r"vorlesen: (\d+) Eintraege.*"),        "liest {} Einträge vor"),
    (re.compile(r"geleert: (.+?),.*"),                  "geleert: {}"),
    (re.compile(r"Antwort gehoert: '(.+)'"),            "Antwort gehört: \u201e{}\u201c"),
]

ZEIT = re.compile(r'^(\d\d:\d\d:\d\d)\s+(.*)$')

# --- Support-Protokoll --------------------------------------------------
# Eine Datei pro Tag. Das ist der Grund fuer das Datum im Namen: aufraeumen
# heisst dann "alte Datei loeschen" und nicht "in einer laufenden Datei nach der
# Grenze suchen" - und eine Datei, in die gerade geschrieben wird, wird dabei
# nie angefasst.
SUPPORT_ORDNER = os.path.join(
    os.environ.get("XDG_DATA_HOME", os.path.join(HEIM, ".local", "share")),
    "dialos", "support")
SUPPORT_TAGE = 7
SUPPORT_NAME = re.compile(r'^befehle-(\d{4})-(\d{2})-(\d{2})\.log$')

# RUECKBLICK: Wieviele Sekunden Vorgeschichte beim Start mitgenommen werden.
# Grund (Stephans Test vom 2026-08-19): Das Fenster wird von "Sprachsteuerung
# starten" geoeffnet - dieser Satz steht also schon im Protokoll, bevor die
# Mitschrift zu lesen beginnt, und fehlte damit IMMER. Fuer den Support waere
# das die erste Frage gewesen ("hat er ueberhaupt eingeschaltet?").
# Der Befehlsdienst ruft mit --rueckblick auf; von Hand gestartet bleibt es bei
# 0, damit ein Fenster, das man selbst oeffnet, nicht mit alten Zeilen anfaengt.
RUECKBLICK_VORGABE = 0

# Inhalt des Nutzers - im Fenster ja, im Support-Protokoll nur die erste Zeile.
# "diktiert:" ist die rohe Erkennung, "geschrieben:" der Text nach der
# Schreibhilfe. Gezaehlt und protokolliert wird nur "geschrieben:", sonst
# stuende jeder Satz doppelt und die Anzahl waere das Doppelte.
INHALT_ROH = re.compile(r'^diktiert:')
INHALT = re.compile(r'^geschrieben: \u201e(.*)\u201c$')
INHALT_KUERZE = 60

# Wo die Anzahl der nicht protokollierten Zeilen hingehoert: an das Ende des
# Diktats, nicht an den naechsten Befehl. Ohne das trug sie die Uhrzeit des
# naechsten gesprochenen Satzes - Minuten spaeter.
INHALT_ABSCHLUSS = re.compile(r'^gespeichert in')

# Woran der Zusammenhang zu erkennen ist. Beim Diktat steht das Ziel im
# Klammerzusatz - deshalb die Tabelle: aus "einkaufszettel" wird
# "Einkaufszettel", und ein spaeteres Ziel wie "brief" oder "mail" landet
# unuebersetzt, aber lesbar im Protokoll, statt zu fehlen.
ZUSAMMENHANG_START = re.compile(r'^Diktat l\u00e4uft \((.+)\)')
# Ein Abschnitt endet nicht nach einer Zeile, sondern beim naechsten Befehl.
# Erster Versuch am 2026-08-19 setzte nach jeder Zeile zurueck - damit stand
# "gespeichert in ..." nicht mehr unter "Einkaufszettel", und fuer einen
# einzigen Befehl standen zwei Ueberschriften da. Ein gehoerter Satz ist die
# einzige verlaessliche Grenze: er bedeutet immer, dass der Nutzer wieder mit
# der Sprachsteuerung spricht - und er kommt auch dann, wenn ein Diktat
# vorzeitig abbricht und die Schlusszeile fehlt.
ZUSAMMENHANG_ZURUECK = re.compile(r'^(geh\u00f6rt: |=== Befehlsdienst gestartet)')
ZUSAMMENHANG_FRAGE = re.compile(r'^Frage: (uhrzeit|datum)')
ZUSAMMENHANG_NOTIZ = re.compile(r'^(\w+): (vorlesen|loeschen)')
ZIELE = {
    "einkaufszettel": "Einkaufszettel",
    "notizen": "Notiz",
}
ZUSAMMENHANG_GRUND = "Sprachsteuerung"

# Laufender Stand fuer das Support-Protokoll. Bewusst hier und nicht in main():
# support_schreiben() muss sich zwischen zwei Zeilen erinnern koennen, welcher
# Zusammenhang gilt und wie viele Inhaltszeilen schon gezaehlt sind.
STAND = {"zusammenhang": ZUSAMMENHANG_GRUND, "inhalte": 0}


def uebersetzen(rohtext):
    for muster, form in UEBERSETZUNG:
        m = muster.search(rohtext)
        if m:
            try:
                return form.format(*m.groups())
            except (IndexError, KeyError):
                return form
    return rohtext.strip()


def zeilen_lesen(pfad, stand):
    """Neue Zeilen seit dem letzten Blick. Gibt (Zeilen, neuer Stand)."""
    try:
        groesse = os.path.getsize(pfad)
    except OSError:
        return [], stand
    if groesse < stand:          # Datei wurde geleert - von vorn
        stand = 0
    if groesse == stand:
        return [], stand
    try:
        with open(pfad, encoding="utf-8", errors="replace") as f:
            f.seek(stand)
            roh = f.read()
            return roh.replace("\r", "\n").split("\n"), f.tell()
    except OSError:
        return [], stand


def aufbereiten(quelle, zeile):
    """Eine Protokollzeile zu (Zeit, Quelle, Satz) - oder None zum Verwerfen."""
    if VERWERFEN.match(zeile):
        return None
    m = ZEIT.match(zeile.strip())
    if m:
        zeit, rest = m.group(1), m.group(2)
    else:
        zeit, rest = time.strftime("%H:%M:%S"), zeile.strip()
    if not rest or VERWERFEN.match(rest):
        return None
    return zeit, quelle, uebersetzen(rest)


def support_aufraeumen(heute):
    """Tagesdateien loeschen, die aelter als SUPPORT_TAGE sind."""
    grenze = heute - datetime.timedelta(days=SUPPORT_TAGE)
    weg = 0
    try:
        namen = os.listdir(SUPPORT_ORDNER)
    except OSError:
        return 0
    for name in namen:
        m = SUPPORT_NAME.match(name)
        if not m:
            continue          # nichts anfassen, was nicht von hier stammt
        try:
            tag = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if tag < grenze:
            try:
                os.remove(os.path.join(SUPPORT_ORDNER, name))
                weg += 1
            except OSError:
                pass
    return weg


def support_datei(heute):
    """Pfad der heutigen Tagesdatei - oder None, wenn sie nicht anzulegen ist.

    Rechte bewusst eng: 0700 auf den Ordner, 0600 auf die Datei. Es steht darin,
    was der Nutzer gesagt hat; das ist nichts fuer andere Konten auf demselben
    Geraet.
    """
    try:
        os.makedirs(SUPPORT_ORDNER, mode=0o700, exist_ok=True)
        os.chmod(SUPPORT_ORDNER, 0o700)
    except OSError:
        return None
    pfad = os.path.join(SUPPORT_ORDNER, f"befehle-{heute.isoformat()}.log")
    if not os.path.exists(pfad):
        try:
            with open(pfad, "w", encoding="utf-8") as f:
                f.write(f"# DialOS - Befehle vom {heute.isoformat()}\n")
                f.write("# Nur fuer den Support. Vom Diktierten steht hier "
                        "bewusst nur die erste Zeile.\n")
                f.write(f"# Wird nach {SUPPORT_TAGE} Tagen von selbst "
                        "geloescht.\n")
            os.chmod(pfad, 0o600)
        except OSError:
            return None
    return pfad


def abschluss_zeilen(zeit):
    """Was am Ende eines Abschnitts noch zu vermerken ist: die Anzahl der
    Inhaltszeilen, die nicht protokolliert wurden."""
    weitere = STAND["inhalte"] - 1
    STAND["inhalte"] = 0
    if weitere > 0:
        wort = "Zeile" if weitere == 1 else "Zeilen"
        return [f"{zeit}  {'':9s} ({weitere} weitere {wort} erfasst, "
                f"nicht protokolliert)"]
    return []


def zusammenhang_von(satz, jetzt):
    """Welcher Zusammenhang gilt fuer diese Zeile, welcher danach?

    Zwei Werte, weil eine Zeile den Abschnitt sowohl beenden als auch einen
    neuen beginnen kann - ein gehoerter Befehl schliesst den vorigen ab und
    gehoert schon zum naechsten.
    """
    if ZUSAMMENHANG_ZURUECK.match(satz):
        return ZUSAMMENHANG_GRUND, ZUSAMMENHANG_GRUND
    m = ZUSAMMENHANG_START.match(satz)
    if m:
        ziel = m.group(1).strip()
        gewaehlt = ZIELE.get(ziel, ziel)
        return gewaehlt, gewaehlt
    if ZUSAMMENHANG_FRAGE.match(satz):
        return "Frage an das System", "Frage an das System"
    m = ZUSAMMENHANG_NOTIZ.match(satz)
    if m:
        gewaehlt = ZIELE.get(m.group(1), m.group(1))
        return gewaehlt, gewaehlt
    return jetzt, jetzt


def support_schreiben(pfad, eintrag):
    """Eine Zeile ins Support-Protokoll - mit Zusammenhang, ohne Inhalte.

    Drei Regeln, alle aus Stephans Vorgabe vom 2026-08-19:
      1. Befehle vollstaendig.
      2. Vom Diktierten die erste Zeile, gekuerzt - damit man sieht, DASS und
         ungefaehr WAS erfasst wurde.
      3. Alles weitere nur als Anzahl.
    """
    zeit, quelle, satz = eintrag
    if INHALT_ROH.match(satz):
        return                     # rohe Erkennung: steht gleich nochmal da

    vorher, nachher = zusammenhang_von(satz, STAND["zusammenhang"])
    zeilen = []

    if vorher != STAND["zusammenhang"]:
        zeilen += abschluss_zeilen(zeit)
        zeilen.append(f"{zeit}  --- {vorher} ---")
        STAND["zusammenhang"] = vorher

    m = INHALT.match(satz)
    if m:
        STAND["inhalte"] += 1
        if STAND["inhalte"] == 1:
            text = m.group(1)
            if len(text) > INHALT_KUERZE:
                text = text[:INHALT_KUERZE].rstrip() + " ..."
            zeilen.append(f"{zeit}  {quelle:9s} erste Zeile: \u201e{text}\u201c")
    else:
        zeilen.append(f"{zeit}  {quelle:9s} {satz}")
        if INHALT_ABSCHLUSS.match(satz):
            zeilen += abschluss_zeilen(zeit)

    if nachher != STAND["zusammenhang"]:
        zeilen += abschluss_zeilen(zeit)
        zeilen.append(f"{zeit}  --- {nachher} ---")
        STAND["zusammenhang"] = nachher

    try:
        with open(pfad, "a", encoding="utf-8") as f:
            f.write("".join(z + "\n" for z in zeilen))
    except OSError:
        pass          # ein volles Dateisystem darf das Fenster nicht anhalten


def zuletzt_protokolliert(pfad):
    """Uhrzeit der letzten Zeile im Support-Protokoll - oder "" wenn keine.

    Das ist die Dopplungssperre fuer den Rueckblick: Wer die Sprachsteuerung
    zweimal kurz hintereinander einschaltet, wuerde dieselben Zeilen sonst
    zweimal ins Protokoll schreiben. Die Datei selbst ist der Merker - es
    braucht keinen zusaetzlichen Zustand, der auch noch veralten koennte.
    """
    letzte = ""
    try:
        with open(pfad, encoding="utf-8", errors="replace") as f:
            for zeile in f:
                m = ZEIT.match(zeile)
                if m:
                    letzte = m.group(1)
    except OSError:
        pass
    return letzte


def rueckblick_sekunden(argumente):
    """--rueckblick N auswerten, tolerant gegen Unsinn."""
    try:
        i = argumente.index("--rueckblick")
        return max(0, int(argumente[i + 1]))
    except (ValueError, IndexError):
        return RUECKBLICK_VORGABE


def vorgeschichte(sekunden):
    """Eintraege der letzten 'sekunden' aus allen Quellen, nach Zeit sortiert.

    RUECKWAERTS GELESEN, und das aus einem Grund, der beim ersten Versuch
    Inhalte von GESTERN ins Protokoll geholt haette: Die vier Protokolle
    schreiben nur "HH:MM:SS" und werden nicht gedreht (siehe TODO.md). Vorwaerts
    verglichen sieht ein Eintrag von gestern 17:52 wie "spaeter heute" aus und
    kaeme bei einem Rueckblick am Abend mit - samt diktiertem Text aus einer
    fremden Sitzung. Rueckwaerts gelesen laeuft die Uhrzeit fallend; springt sie
    nach oben, ist das der Tageswechsel, und dort wird abgebrochen.
    """
    if sekunden <= 0:
        return []
    jetzt = time.strftime("%H:%M:%S")
    grenze = time.strftime("%H:%M:%S", time.localtime(time.time() - sekunden))
    if grenze > jetzt:                 # Rueckblick reicht ueber Mitternacht
        grenze = "00:00:00"
    gesammelt = []
    for name, pfad in QUELLEN.items():
        try:
            with open(pfad, encoding="utf-8", errors="replace") as f:
                f.seek(0, os.SEEK_END)
                f.seek(max(0, f.tell() - 65536))   # mehr braucht es nie
                roh = f.read()
        except OSError:
            continue
        vorige = jetzt
        je_quelle = []
        for zeile in reversed(roh.replace("\r", "\n").split("\n")):
            m = ZEIT.match(zeile.strip())
            if not m:
                continue
            zeit = m.group(1)
            if zeit > vorige or zeit < grenze:
                break                  # Tageswechsel bzw. alt genug
            vorige = zeit
            eintrag = aufbereiten(name, zeile)
            if eintrag:
                je_quelle.append(eintrag)
        # Wieder in Leserichtung drehen, BEVOR sortiert wird: sorted() ist
        # stabil, also entscheidet die Eingabereihenfolge bei gleicher Uhrzeit.
        # Ohne das stand "Mitschrift geoeffnet" vor dem Satz, der sie geoeffnet
        # hat - beide in derselben Sekunde (2026-08-19).
        je_quelle.reverse()
        gesammelt += je_quelle
    return sorted(gesammelt, key=lambda e: e[0])


def ausgeben(eintrag):
    zeit, quelle, satz = eintrag
    print(f"  {zeit}  {quelle:9s} {satz}", flush=True)


def main():
    alles = "--alles" in sys.argv
    breite = 74
    print("=" * breite)
    print("  DialOS - Mitschrift")
    print("  Was die Sprachsteuerung gerade tut. Beenden mit Strg+C.")
    print("=" * breite)

    heute = datetime.date.today()
    support = None if "--kein-protokoll" in sys.argv else support_datei(heute)
    grenze_protokoll = zuletzt_protokolliert(support) if support else ""
    if support:
        weg = support_aufraeumen(heute)
        print(f"  Support-Protokoll: {support}")
        print(f"  (Befehle mit Zusammenhang, vom Diktierten nur die erste "
              f"Zeile; nach {SUPPORT_TAGE} Tagen"
              + (f" geloescht - {weg} alte gerade entfernt)" if weg
                 else " geloescht)"))
        print()

    for eintrag in vorgeschichte(rueckblick_sekunden(sys.argv)):
        ausgeben(eintrag)
        if support and eintrag[0] > grenze_protokoll:
            support_schreiben(support, eintrag)

    stand = {}
    for name, pfad in QUELLEN.items():
        try:
            stand[name] = 0 if alles else os.path.getsize(pfad)
        except OSError:
            stand[name] = 0
    if not alles:
        print("  (wartet auf das naechste Ereignis)")
        print()

    try:
        while True:
            # ALLE Quellen einsammeln und dann nach Uhrzeit sortiert
            # ausgeben (Fehler vom 2026-08-19): Quelle fuer Quelle
            # ausgegeben sah die Ausgabe chronologisch aus und war es nicht -
            # erst kam alles vom Befehlsdienst, dann alles vom Diktat. Bei
            # genau dem Zweck, fuer den vier Protokolle zusammengefuehrt
            # werden - zeigen, was GLEICHZEITIG passiert ist -, waere das
            # irrefuehrend.
            gesammelt = []
            for name, pfad in QUELLEN.items():
                neu, stand[name] = zeilen_lesen(pfad, stand[name])
                for z in neu:
                    eintrag = aufbereiten(name, z)
                    if eintrag:
                        gesammelt.append(eintrag)
            if gesammelt and support and datetime.date.today() != heute:
                # Mitternacht: neue Tagesdatei, und die aelteste geht weg. Nur
                # bei echten Eintraegen geprueft - ein Fenster, das die Nacht
                # ueber offen steht, soll nicht 200000-mal das Datum holen.
                heute = datetime.date.today()
                support = support_datei(heute)
                support_aufraeumen(heute)
            for eintrag in sorted(gesammelt, key=lambda e: e[0]):
                ausgeben(eintrag)
                if support:
                    support_schreiben(support, eintrag)
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\n  Mitschrift beendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
