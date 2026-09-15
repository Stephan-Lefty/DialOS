#!/usr/bin/env python3
"""DialOS-Pruefstand: echte Aufnahmen als Pruef-Faelle, nach jeder Aenderung.

Stephan am 2026-09-15: "Wir muessen ein System hinbekommen, was sauber die
Befehle umsetzt und auf der anderen Seite auch einen Text in deutscher Sprache
sauber zu Papier bringt." Und auf den Vorschlag, dafuer zu messen statt nach
Gefuehl zu urteilen: "Ja, einverstanden, bau den Pruefstand".

WARUM: Jede Verbesserung am Diktat wurde bis dahin an EINEM Versuch beurteilt,
und Piper spricht sauberer als jeder Mensch. Der Pruefstand spielt echte
Aufnahmen durch das ECHTE Diktatprogramm - dieselben Erkenner, dieselben
Regeln, dieselbe Nachbearbeitung - und misst, was herauskommt.

WOHER DIE AUFNAHMEN KOMMEN: dialos-diktat.py schneidet mit, wenn die
Schalterdatei ~/.config/dialos/pruefstand existiert - genau den Ton, den die
Erkenner bekommen haben. Die Mitschnitte liegen auf der externen Platte unter
erkenner-vergleich/pruefstand/, NIE im Repo: Es ist die Stimme des Sprechers,
und die Texte sind persoenlich. Stephans Zustimmung vom 2026-09-15 gilt fuer
seine eigenen Aufnahmen; fuer andere Sprecher braucht es eine eigene.

DER BEFEHLSDIENST SCHNEIDET NUR IN EINER MESSSITZUNG MIT: Er hoert dauernd zu,
ein dauernder Mitschnitt waere jedes Gespraech im Raum. Mit dem Schalter
~/.config/dialos/pruefstand-befehle speichert er jede erkannte Aeusserung -
Schalter danach wieder entfernen. Ohne Mitschnitt wertet "befehle" die
Protokolle aus.

Aufruf (mit /usr/bin/python3 - Vosk ist systemweit installiert):
  scripts/dialos-pruefstand.py mitschnitte
        listet die Mitschnitte
  scripts/dialos-pruefstand.py uebernehmen NAME [MITSCHNITT]
        macht aus dem neuesten (oder genannten) Mitschnitt den Fall NAME;
        referenz.txt ist mit dem Ergebnis vorbefuellt und MUSS von Hand auf
        das wirklich Gesagte korrigiert werden
  scripts/dialos-pruefstand.py pruefen [--vosk|--parakeet|--beide] [--tempo N] [FALL ...]
        spielt die Faelle durch und misst Wortfehler, Satzzeichen, Befehle
  scripts/dialos-pruefstand.py befehle [--tage N]
        wertet die Protokolle der Sprachsteuerung aus

Befehle (Mitschnitt der Sprachsteuerung mit ~/.config/dialos/pruefstand-befehle,
nur fuer eine Messsitzung - er speichert JEDE erkannte Aeusserung, auch Gespraech):
  scripts/dialos-pruefstand.py befehle-beschriften
        spielt jeden unbeschrifteten Mitschnitt vor und fragt, was gesagt wurde
        (Befehlssatz, "nichts" fuer Geraeusch/Gespraech/Fernseher, leer = spaeter)
  scripts/dialos-pruefstand.py befehle-pruefen
        erkennt alle beschrifteten Mitschnitte neu, mit den Regeln des
        Befehlsdienstes, und zaehlt: richtig, verpasst, falsch ausgeloest
"""

import difflib
import glob
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time
import wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO, "iso-build/config/includes.chroot/usr/local/bin")
ORDNER = os.environ.get("DIALOS_PRUEFSTAND",
                        "/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich/pruefstand")
MITSCHNITTE = os.path.join(ORDNER, "mitschnitte")
FAELLE = os.path.join(ORDNER, "faelle")
ERGEBNISSE = os.path.join(ORDNER, "ergebnisse")
RATE = 16000
BLOCK = 4000


def laden(pfad, name):
    spec = importlib.util.spec_from_file_location(name, pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


# ------------------------------------------------------------ Faelle ---

def mitschnitte():
    dateien = sorted(glob.glob(os.path.join(MITSCHNITTE, "*.wav")))
    if not dateien:
        print(f"Keine Mitschnitte in {MITSCHNITTE}")
        print("Einschalten: touch ~/.config/dialos/pruefstand")
    for d in dateien:
        with open(d[:-4] + ".json", encoding="utf-8") as f:
            info = json.load(f)
        text = " ".join(" ".join(info["ergebnis"]).split())
        print(f"{os.path.basename(d)[:-4]}  {info['dauer_s']:5.1f} s  "
              f"{'Parakeet' if info['parakeet'] else 'Vosk'}  {text[:70]!r}")
    return 0


def befehle_aus_protokoll(protokoll):
    return {"satz löschen": protokoll.count("SATZ LOESCHEN:"),
            "satz wiederholen": protokoll.count("SATZ WIEDERHOLEN:"),
            "schluss": ("Schlusssatz erkannt" in protokoll
                        or "Schlusssatz in der freien Erkennung" in protokoll)}


def uebernehmen(name, mitschnitt=None):
    if not re.fullmatch(r"[\w-]+", name):
        print("NAME nur aus Buchstaben, Ziffern, - und _")
        return 2
    if mitschnitt is None:
        alle = sorted(glob.glob(os.path.join(MITSCHNITTE, "*.wav")))
        if not alle:
            print(f"Keine Mitschnitte in {MITSCHNITTE}")
            return 1
        quelle = alle[-1][:-4]
    else:
        quelle = os.path.join(MITSCHNITTE, os.path.basename(mitschnitt).removesuffix(".wav"))
    ziel = os.path.join(FAELLE, name)
    if os.path.exists(ziel):
        print(f"Fall {name} gibt es schon: {ziel}")
        return 1
    os.makedirs(ziel)
    shutil.copyfile(quelle + ".wav", os.path.join(ziel, "aufnahme.wav"))
    shutil.copyfile(quelle + ".json", os.path.join(ziel, "mitschnitt.json"))
    with open(quelle + ".json", encoding="utf-8") as f:
        info = json.load(f)
    trenner = "\n" if info["name"] in ("notizen",) else " "
    with open(os.path.join(ziel, "referenz.txt"), "w", encoding="utf-8") as f:
        f.write(trenner.join(info["ergebnis"]).strip() + "\n")
    with open(os.path.join(ziel, "erwartet.json"), "w", encoding="utf-8") as f:
        json.dump({"name": info["name"], "befehle": befehle_aus_protokoll(info["protokoll"])},
                  f, ensure_ascii=False, indent=1)
    print(f"Fall angelegt: {ziel}")
    print("  referenz.txt ist das ERGEBNIS von damals - jetzt auf das wirklich")
    print("  Gesagte korrigieren (Satzzeichen und Absaetze so, wie sie sein sollen).")
    print("  erwartet.json: welche Befehle wie oft - ebenfalls pruefen.")
    return 0


# ---------------------------------------------------------- Messung ---

TRENNZEICHEN = ",.?!:"


def zerlegen(text, diktat):
    """[(Wort normalisiert, Zeichen danach)] - Zeichen: , . ? ! : ¶ (Absatz) ↵ (Zeile)."""
    vergleich = laden(os.path.join(REPO, "scripts/dialos-erkenner-vergleich.py"), "vergleich")
    enden = set(diktat.satzenden(text))
    teile = []
    worte = list(re.finditer(r"[\wäöüÄÖÜß]+(?:[-'][\wäöüÄÖÜß]+)*", text))
    for i, m in enumerate(worte):
        bis = worte[i + 1].start() if i + 1 < len(worte) else len(text)
        zwischen = text[m.end():bis]
        zeichen = ""
        if "\n\n" in zwischen:
            zeichen = "¶"
        elif "\n" in zwischen:
            zeichen = "↵"
        else:
            for k, c in enumerate(zwischen):
                if c in TRENNZEICHEN and (c != "." or (m.end() + k) in enden):
                    zeichen = c
                    break
        for wort in vergleich.normal(m.group()).split():
            teile.append([wort, ""])
        if teile:
            teile[-1][1] = zeichen
    return teile


def messen(referenz, ergebnis, diktat):
    vergleich = laden(os.path.join(REPO, "scripts/dialos-erkenner-vergleich.py"), "vergleich")
    r, h = zerlegen(referenz, diktat), zerlegen(ergebnis, diktat)
    rw, hw = [w for w, _ in r], [w for w, _ in h]
    fehler, anzahl = vergleich.wortfehler(" ".join(rw), " ".join(hw))
    # Satzzeichen: an jedem Wort, das in beiden steht, das Zeichen danach vergleichen.
    zeichen_soll = sum(1 for _, z in r if z)
    zeichen_falsch = 0
    abgleich = difflib.SequenceMatcher(None, rw, hw, autojunk=False)
    for a, b, n in abgleich.get_matching_blocks():
        for k in range(n):
            if r[a + k][1] != h[b + k][1]:
                zeichen_falsch += 1
    return {"woerter": anzahl, "wortfehler": fehler,
            "wer": round(100 * fehler / max(1, anzahl), 1),
            "zeichen_soll": zeichen_soll, "zeichen_falsch": zeichen_falsch}


# ----------------------------------------------------- Wiederholung ---

class Strom:
    """Liefert die Aufnahme in denselben Bloecken und im Takt der Zeit."""

    def __init__(self, daten, kurz, tempo):
        self.daten, self.pos, self.tempo = daten, 0, tempo
        self.kurz = {a: n for a, n in kurz}
        self.t0 = time.time()

    def read(self, n):
        if self.pos >= len(self.daten):
            time.sleep(n / (2 * RATE) / self.tempo)
            return bytes(n)
        n = self.kurz.get(self.pos, n)
        stueck = self.daten[self.pos:self.pos + n]
        self.pos += len(stueck)
        warten = self.t0 + self.pos / (2 * RATE) / self.tempo - time.time()
        if warten > 0:
            time.sleep(warten)
        return stueck


class Prozess:
    def __init__(self, strom):
        self.stdout = strom

    def terminate(self):
        pass


def fall_abspielen(fall, parakeet, tempo):
    with open(os.path.join(fall, "erwartet.json"), encoding="utf-8") as f:
        erwartet = json.load(f)
    with open(os.path.join(fall, "mitschnitt.json"), encoding="utf-8") as f:
        info = json.load(f)
    with wave.open(os.path.join(fall, "aufnahme.wav")) as w:
        daten = w.readframes(w.getnframes())
    with open(os.path.join(fall, "referenz.txt"), encoding="utf-8") as f:
        referenz = f.read().strip()

    sys.argv = ["dialos-diktat.py"]
    d = laden(os.path.join(BIN, "dialos-diktat.py"), "diktat_pruefstand")
    tmp = tempfile.mkdtemp(prefix="pruefstand-")
    d.DOKUMENT_ORDNER = d.NOTIZ_ORDNER = tmp
    d.ARCHIV_SKRIPT = "/nicht/vorhanden"
    d.PROTOKOLL = os.path.join(tmp, "diktat.log")
    d.MITSCHNITT_SCHALTER = os.path.join(tmp, "kein-mitschnitt")
    d.PARAKEET_SCHALTER = os.path.join(tmp, "parakeet")
    if parakeet:
        open(d.PARAKEET_SCHALTER, "w").close()
    d.DIKTAT_ZEITGRENZE_S = 15.0
    d.sprich = lambda text, *a, **k: None
    d.sprechen_bei_offener_aufnahme = lambda text, prozess: b""
    d.aufnahme_starten = lambda quelle: Prozess(Strom(daten, info.get("kurze_bloecke", []), tempo))
    ergebnis = {}

    def brief(zeilen):
        ergebnis["text"] = " ".join(zeilen)
        return os.path.join(tmp, "brief.txt")

    def notiz(name, zeilen):
        ergebnis["text"] = "\n".join(zeilen)
        return os.path.join(tmp, name + ".txt")
    d.brief_schreiben, d.notiz_schreiben = brief, notiz

    t0 = time.time()
    d.diktat_fuehren("notiz", erwartet["name"], "pruefstand")
    dauer = time.time() - t0
    with open(d.PROTOKOLL, encoding="utf-8") as f:
        protokoll = f.read()
    text = ergebnis.get("text", "")
    werte = messen(referenz, text, d)
    werte["befehle"] = befehle_aus_protokoll(protokoll)
    werte["befehle_ok"] = werte["befehle"] == erwartet["befehle"]
    werte["dauer_s"] = round(dauer, 1)
    werte["text"] = text
    shutil.rmtree(tmp, ignore_errors=True)
    return werte


def pruefen(argumente):
    tempo = 1.0
    if "--tempo" in argumente:
        i = argumente.index("--tempo")
        tempo = float(argumente[i + 1])
        del argumente[i:i + 2]
    arten = [("Parakeet", True)]
    if "--vosk" in argumente:
        arten = [("Vosk", False)]
    if "--beide" in argumente:
        arten = [("Vosk", False), ("Parakeet", True)]
    namen = [a for a in argumente if not a.startswith("--")]
    faelle = sorted(glob.glob(os.path.join(FAELLE, "*"))) if not namen else \
        [os.path.join(FAELLE, n) for n in namen]
    if not faelle:
        print(f"Keine Faelle in {FAELLE} - erst: uebernehmen NAME")
        return 1
    alle = {}
    for fall in faelle:
        for art, parakeet in arten:
            print(f"... {os.path.basename(fall)} mit {art}", flush=True)
            alle[f"{os.path.basename(fall)}|{art}"] = fall_abspielen(fall, parakeet, tempo)
    print()
    print(f"{'Fall':28s} {'Erkenner':9s} {'Wortfehler':>12s} {'Satzzeichen falsch':>19s}  Befehle")
    for schluessel, w in alle.items():
        fall, art = schluessel.split("|")
        print(f"{fall:28s} {art:9s} {w['wortfehler']:3d}/{w['woerter']:<3d} {w['wer']:4.1f} %"
              f" {w['zeichen_falsch']:6d} von {w['zeichen_soll']:<3d}     "
              f"{'ok' if w['befehle_ok'] else 'ABWEICHUNG ' + json.dumps(w['befehle'], ensure_ascii=False)}")
    os.makedirs(ERGEBNISSE, exist_ok=True)
    ablage = os.path.join(ERGEBNISSE, time.strftime("%Y-%m-%d-%H%M") + "-pruefstand.json")
    with open(ablage, "w", encoding="utf-8") as f:
        json.dump(alle, f, ensure_ascii=False, indent=1)
    print(f"\nEinzelheiten (mit Texten): {ablage}")
    return 0


# ---------------------------------------------------------- Befehle ---

def befehle(argumente):
    """Zaehlt aus den Protokollen der Sprachsteuerung, was mit Aeusserungen geschah."""
    tage = None
    if "--tage" in argumente:
        tage = int(argumente[argumente.index("--tage") + 1])
    dateien = sorted(glob.glob(os.path.expanduser("~/.log/dialos-sprachbefehl.log-*")))
    dateien = [d for d in dateien if not d.endswith(".gz") and "messung" not in d]
    dateien.append(os.path.expanduser("~/.log/dialos-sprachbefehl.log"))
    ausgefuehrt = ("Rueckfrage vor Diktat", "Diktat gestartet", "Rueckfrage vor Druck",
                   "Druck ", "Notiz-Aktion", "Auskunft ", "Bildschirmfoto erstellt")
    je_tag = {}
    hinweise = {}
    heute = time.strftime("%m-%d")
    for pfad in dateien:
        tag_datei = None
        m = re.search(r"log-\d{4}-(\d{2}-\d{2})$", pfad)
        if m:
            tag_datei = m.group(1)
        an = False
        with open(pfad, encoding="utf-8", errors="replace") as f:
            for zeile in f:
                m = re.match(r"^(\d{2}-\d{2}) ", zeile)
                tag = m.group(1) if m else (tag_datei or heute)
                t = je_tag.setdefault(tag, {"eingeschaltet": 0, "einschalten_verworfen": 0,
                                            "aeusserungen_an": 0, "befehle": 0,
                                            "kein_befehl_hinweis": 0, "kein_befehl_still": 0,
                                            "gespraech_aus": 0, "zeitgrenze": 0})
                if "Mitschrift geoeffnet" in zeile or "Mitschrift laeuft schon" in zeile:
                    t["eingeschaltet"] += 1
                    an = True
                elif "Mitschrift wird geschlossen" in zeile or "Zeitgrenze:" in zeile:
                    if "Zeitgrenze:" in zeile:
                        t["zeitgrenze"] += 1
                    an = False
                elif "Einschaltsatz verworfen" in zeile:
                    t["einschalten_verworfen"] += 1
                elif "Gespraech erkannt" in zeile:
                    t["gespraech_aus"] += 1
                    an = False
                elif "erkannt: " in zeile and an:
                    t["aeusserungen_an"] += 1
                elif any(a in zeile for a in ausgefuehrt):
                    t["befehle"] += 1
                elif "kein Befehl - Hinweis" in zeile:
                    t["kein_befehl_hinweis"] += 1
                    h = re.search(r"Hinweis: '(.*)'", zeile)
                    if h:
                        hinweise[h.group(1)] = hinweise.get(h.group(1), 0) + 1
                elif "kein Befehl - kein Hinweis" in zeile:
                    t["kein_befehl_still"] += 1
    tage_liste = sorted(je_tag)
    if tage:
        tage_liste = tage_liste[-tage:]
    print(f"{'Tag':6s} {'an':>4s} {'an verw.':>8s} {'Aeuss.':>7s} {'Befehle':>8s} "
          f"{'kein B. (Hinw.)':>16s} {'kein B. (still)':>16s} {'Gespr.':>7s} {'Zeitgr.':>8s}")
    for tag in tage_liste:
        t = je_tag[tag]
        print(f"{tag:6s} {t['eingeschaltet']:4d} {t['einschalten_verworfen']:8d} "
              f"{t['aeusserungen_an']:7d} {t['befehle']:8d} {t['kein_befehl_hinweis']:16d} "
              f"{t['kein_befehl_still']:16d} {t['gespraech_aus']:7d} {t['zeitgrenze']:8d}")
    print("\nHaeufigste Hinweise 'Das war kein Befehl' (was gemeint gewesen sein koennte):")
    for text, n in sorted(hinweise.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:3d} x  {text}")
    print("\nNicht in den Zahlen: Umschalten der Optik und Ein-/Ausschalten selbst werden")
    print("nicht als Befehl gezaehlt; ob ein ausgefuehrter Befehl GEMEINT war, steht in")
    print("keinem Protokoll - das kann nur der Sprecher sagen.")
    return 0


# ------------------------------------------------ Befehls-Mitschnitte ---

BEFEHL_ORDNER = os.path.join(ORDNER, "befehle")


def dienst_laden():
    sys.argv = ["dialos-sprachbefehl-desktop.py"]
    return laden(os.path.join(BIN, "dialos-sprachbefehl-desktop.py"), "befehlsdienst")


def befehle_beschriften():
    import subprocess
    dienst = dienst_laden()
    erlaubt = set(dienst.BEFEHLSSAETZE) | {dienst.STARTSATZ, dienst.STOPPSATZ, "nichts"}
    dateien = sorted(glob.glob(os.path.join(BEFEHL_ORDNER, "*.json")))
    offen = []
    for d in dateien:
        with open(d, encoding="utf-8") as f:
            if json.load(f).get("gesagt") is None:
                offen.append(d)
    print(f"{len(offen)} unbeschriftete Mitschnitte von {len(dateien)}.")
    print("Antwort: der gesagte Befehlssatz oder 'nichts' (kein Befehl gesagt).")
    print("Eingabetaste = Vorschlag uebernehmen (ohne Vorschlag: nochmal anhoeren),")
    print("'n' = nochmal anhoeren, 'w' = weiter ohne Beschriftung, 'q' = aufhoeren.\n")
    for d in offen:
        with open(d, encoding="utf-8") as f:
            info = json.load(f)
        vorschlag = info.get("vorschlag")
        subprocess.run(["paplay", d[:-5] + ".wav"])
        while True:
            print(f"{os.path.basename(d)[:-5]}  erkannt: {info['erkannt']!r}"
                  + (f"   Vorschlag: {vorschlag!r}" if vorschlag else ""))
            antwort = input("  gesagt: ").strip().lower()
            if antwort == "q":
                return 0
            if antwort == "w":
                break
            if antwort == "n" or (not antwort and not vorschlag):
                subprocess.run(["paplay", d[:-5] + ".wav"])
                continue
            if not antwort:
                antwort = vorschlag
            if antwort not in erlaubt:
                print("  unbekannt - einer der Befehlssaetze oder 'nichts'")
                continue
            info["gesagt"] = antwort
            info["beschriftet"] = "von Hand"
            with open(d, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=1)
            break
    return 0


def wirkung(dienst, satz):
    """Was ein Befehlssatz BEWIRKT - Synonyme ("brief schreiben"/"brief erstellen")
    und die Optik-Umschaltung zaehlen so gleich."""
    for tabelle, art in ((dienst.DIKTAT_SAETZE, "diktat"), (dienst.DRUCK_SAETZE, "drucken"),
                         (dienst.AUSKUNFT_SAETZE, "auskunft"), (dienst.HILFE_SAETZE, "hilfe")):
        if satz in tabelle:
            return f"{art}:{tabelle[satz]}"
    if satz in dienst.NOTIZ_SAETZE:
        return "notiz:" + ":".join(dienst.NOTIZ_SAETZE[satz])
    if satz in dienst.FOTO_SAETZE:
        return "foto"
    worte = satz.split()
    if dienst.AUSLOESER in worte:
        for w in worte:
            if dienst.ZIELE.get(w):
                return "optik:" + dienst.ZIELE[w]
    if satz in (dienst.STARTSATZ, dienst.STOPPSATZ):
        return satz
    return satz


def befehl_entscheiden(dienst, text, hoert_zu, verlauf):
    """Was der Befehlsdienst mit dieser Aeusserung taete - ohne es zu tun.

    Dieselbe Reihenfolge wie in dialos-sprachbefehl-desktop.py main(): Start,
    Stopp, exakter Satz oder enthaltener Befehl, zuletzt die Optik-Regel
    ("umschalten" plus Ziel irgendwo in der Aeusserung). Ergebnis ist die
    WIRKUNG (siehe wirkung()), "nichts" oder "verworfen:zu laut".
    """
    worte = text.split()
    satz = " ".join(worte)
    if not hoert_zu:
        if dienst.ist_phrase(satz, dienst.STARTSATZ, ("sprachsteuerung", "starten")):
            return dienst.STARTSATZ if dienst.still_danach(verlauf) else "verworfen:zu laut"
        return "nichts"
    if dienst.ist_phrase(satz, dienst.STARTSATZ, ("sprachsteuerung", "starten")) or dienst.STARTSATZ in satz:
        return dienst.STARTSATZ
    if dienst.ist_phrase(satz, dienst.STOPPSATZ, "stoppen"):
        return dienst.STOPPSATZ
    if satz not in dienst.BEFEHLSSAETZE:
        genauer = dienst.enthaltener_befehl(worte)
        if genauer:
            satz, worte = genauer, genauer.split()
    w = wirkung(dienst, satz)
    if w != satz or satz in dienst.BEFEHLSSAETZE:
        return w
    if dienst.AUSLOESER in worte:
        for wort in worte:
            if dienst.ZIELE.get(wort):
                return "optik:" + dienst.ZIELE[wort]
    return "nichts"


def befehle_pruefen():
    import vosk
    import array
    vosk.SetLogLevel(-1)
    dienst = dienst_laden()
    modell = vosk.Model(dienst.MODELL)
    zaehler = {"richtig": 0, "verpasst": 0, "falsch_ausgeloest": 0, "richtig_nichts": 0,
               "zu_laut_verworfen_obwohl_gesagt": 0}
    zeilen = []
    for d in sorted(glob.glob(os.path.join(BEFEHL_ORDNER, "*.json"))):
        with open(d, encoding="utf-8") as f:
            info = json.load(f)
        if info.get("gesagt") is None:
            continue
        with wave.open(d[:-5] + ".wav") as w:
            daten = w.readframes(w.getnframes())
        erkenner = vosk.KaldiRecognizer(
            modell, RATE, dienst.GRAMMATIK_AN if info["hoert_zu"] else dienst.GRAMMATIK_AUS)
        verlauf = []
        text = ""
        for i in range(0, len(daten), BLOCK):
            block = daten[i:i + BLOCK]
            werte = array.array("h", block[:len(block) // 2 * 2])
            verlauf.append(max((abs(x) for x in werte), default=0))
            if erkenner.AcceptWaveform(block):
                text = json.loads(erkenner.Result()).get("text", "") or text
        text = text or json.loads(erkenner.FinalResult()).get("text", "")
        # Stille nach dem Satz: der Verlauf aus dem Dienst (reicht ueber das
        # Ergebnis hinaus nicht - Vosk liefert erst nach einer Pause ab).
        entscheidung = befehl_entscheiden(dienst, text, info["hoert_zu"],
                                          info.get("pegel_verlauf") or verlauf)
        gesagt = info["gesagt"] if info["gesagt"] == "nichts" else wirkung(dienst, info["gesagt"])
        if gesagt == "nichts":
            art = "richtig_nichts" if entscheidung in ("nichts", "verworfen:zu laut") else "falsch_ausgeloest"
        elif entscheidung == gesagt:
            art = "richtig"
        elif entscheidung == "verworfen:zu laut" and gesagt == dienst.STARTSATZ:
            art = "zu_laut_verworfen_obwohl_gesagt"
        else:
            art = "verpasst" if entscheidung in ("nichts", "verworfen:zu laut") else "falsch_ausgeloest"
        zaehler[art] += 1
        zeilen.append((os.path.basename(d)[:-5], gesagt, text, entscheidung, art))
    for name, gesagt, text, entscheidung, art in zeilen:
        print(f"{name}  gesagt={gesagt!r:28s} erkannt={text!r:34s} -> {entscheidung:26s} {art}")
    print()
    for k, v in zaehler.items():
        print(f"  {k:32s} {v}")
    return 0


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__.split("Aufruf")[1])
        return 2
    if a[0] == "mitschnitte":
        return mitschnitte()
    if a[0] == "uebernehmen" and len(a) >= 2:
        return uebernehmen(a[1], a[2] if len(a) > 2 else None)
    if a[0] == "pruefen":
        return pruefen(a[1:])
    if a[0] == "befehle":
        return befehle(a[1:])
    if a[0] == "befehle-beschriften":
        return befehle_beschriften()
    if a[0] == "befehle-pruefen":
        return befehle_pruefen()
    print(__doc__.split("Aufruf")[1])
    return 2


if __name__ == "__main__":
    sys.exit(main())
