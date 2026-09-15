#!/usr/bin/env python3
"""Vergleicht Spracherkenner fuers Diktat: Vosk, Whisper, Parakeet.

Stephan am 2026-09-14: "Was mir aktuell noch Kopfzerbrechen macht ist der
Einkaufszettel. Gibt es noch 'bessere' Sprachsteuerungssysteme" - Aufteilung:
Befehle weiter mit Vosk, freier Text vielleicht mit Whisper. Dieses Skript
liefert die Zahlen fuer die Entscheidung.

DIESELBE AUFNAHME FUER ALLE. Ein Vergleich, bei dem jeder Erkenner eine andere
Aufnahme bekommt, misst die Tagesform des Sprechers mit. Deshalb wird einmal
aufgenommen und dann jeder Erkenner mit genau denselben Stuecken gefuettert.

DIESELBEN STUECKE WIE IM DIKTAT. DialOS schneidet an Sprechpausen; eine Ware
ist ein Stueck. Genau so wird hier geschnitten - sonst haette Whisper, das
lange Zusammenhaenge mag, einen Vorteil, den es im Alltag nicht haette.

Die Waren und der Brieftext kommen aus docs/einkaufszettel-vorlage.md, nicht
aus einer Liste hier - zwei Listen laufen beim naechsten Aendern auseinander.

Aufruf (mit der Python-Umgebung aus dialos-erkenner-einrichten.sh):
  PY=/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich/venv/bin/python
  $PY scripts/dialos-erkenner-vergleich.py aufnehmen  NAME
  $PY scripts/dialos-erkenner-vergleich.py vergleichen NAME einkaufszettel|brief
  $PY scripts/dialos-erkenner-vergleich.py piper      NAME einkaufszettel|brief
        (erzeugt eine Aufnahme mit Annas Stimme - zum Pruefen des Ablaufs)
"""

import array
import json
import math
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIEL = os.environ.get("DIALOS_ERKENNER",
                      "/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich")
VORLAGE = os.path.join(REPO, "docs", "einkaufszettel-vorlage.md")
RATE = 16000

VOSK_GROSS = "/usr/local/share/vosk-model-de-big"
WHISPER_CLI = os.path.join(ZIEL, "whisper.cpp/build/bin/whisper-cli")
# (Kennung, Modell, zusaetzliche Optionen). "-ac 512" verkuerzt das
# Rechenfenster von 30 s auf rund 10 s: Am 2026-09-14 brauchte Whisper je Ware
# (~1 s Sprache) 7 s (small) bzw. 41 s (turbo), weil jedes Stueck auf 30 s
# aufgefuellt wird. Turbo ohne -ac ist damit schon verworfen und fehlt hier.
WHISPER_LAEUFE = [("whisper-small", "ggml-small.bin", []),
                  ("whisper-small -ac 512", "ggml-small.bin", ["-ac", "512"]),
                  ("whisper-turbo -ac 512", "ggml-large-v3-turbo-q5_0.bin", ["-ac", "512"])]
PARAKEET = os.path.join(ZIEL, "modelle", "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
THREADS = int(os.environ.get("DIALOS_THREADS", "4"))     # 4 echte Kerne im T490
PAUSE_S = float(os.environ.get("DIALOS_PAUSE", "0.2"))


# ------------------------------------------------------------- Vorlage ---

def referenz(art):
    text = open(VORLAGE, encoding="utf-8").read()
    if art == "einkaufszettel":
        block = text.split("<!-- ZETTEL-ANFANG -->")[1].split("<!-- ZETTEL-ENDE -->")[0]
        return [z[2:].strip() for z in block.splitlines() if z.startswith("- ")]
    if art == "brief":
        block = text.split("<!-- BRIEF-ANFANG -->")[1].split("<!-- BRIEF-ENDE -->")[0]
        return [" ".join(block.split())]
    sys.exit(f"unbekannte Art: {art} (einkaufszettel|brief)")


# ------------------------------------------------------ Normalisieren ---

EINER = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun",
         "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn",
         "achtzehn", "neunzehn"]
ZEHNER = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig",
          "achtzig", "neunzig"]


def zahl_als_wort(n):
    """Ganze Zahl 0-9999 als deutsches Wort ("500" -> "fünfhundert")."""
    if n < 20:
        return EINER[n]
    if n < 100:
        e, z = n % 10, n // 10
        return ZEHNER[z] if e == 0 else ("ein" if e == 1 else EINER[e]) + "und" + ZEHNER[z]
    if n < 1000:
        h, r = divmod(n, 100)
        return ("ein" if h == 1 else EINER[h]) + "hundert" + (zahl_als_wort(r) if r else "")
    t, r = divmod(n, 1000)
    return ("ein" if t == 1 else zahl_als_wort(t)) + "tausend" + (zahl_als_wort(r) if r else "")


def normal(text):
    """Kleinschreibung, Ziffern als Woerter, ohne Satzzeichen.

    Whisper und Parakeet schreiben "6 Eier", Vosk "sechs eier" - ohne dieses
    Angleichen zaehlte eine richtig verstandene Menge als Fehler.
    """
    text = text.lower().replace("-", " ")
    text = re.sub(r"\d+", lambda m: zahl_als_wort(int(m.group())) if len(m.group()) <= 4 else m.group(), text)
    text = re.sub(r"[^\wäöüß ]", " ", text)
    return " ".join(text.split())


def wortfehler(ref, hyp):
    """Levenshtein ueber Woerter: (Fehler, Referenzwoerter)."""
    r, h = ref.split(), hyp.split()
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        vorher, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            alt = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, vorher + (r[i - 1] != h[j - 1]))
            vorher = alt
    return d[len(h)], len(r)


# ------------------------------------------------------------ Audio ---

def wav_lesen(pfad):
    with wave.open(pfad) as w:
        if w.getframerate() != RATE or w.getnchannels() != 1 or w.getsampwidth() != 2:
            sys.exit(f"{pfad}: erwartet 16 kHz, mono, 16 Bit")
        return array.array("h", w.readframes(w.getnframes()))


def wav_schreiben(pfad, werte):
    with wave.open(pfad, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(werte.tobytes())


def stuecke(werte):
    """Schneidet an Sprechpausen - wie das Diktat: eine Ware, ein Stueck.

    Rahmen 30 ms; Sprache ist, was deutlich ueber dem Grundrauschen liegt
    (4 x das 20-%-Quantil, mindestens 300). Luecken unter PAUSE_S gehoeren zum
    Stueck; Stuecke unter 0,25 s fallen weg; 0,2 s Rand davor und danach.

    PAUSE_S 0,2 statt 0,45 (2026-09-15, Stephans erste Aufnahme): Er sprach
    zuegig, zwischen den Waren lagen gegen Ende nur 0,24-0,45 s - bei 0,45
    kamen 14 statt 20 Stuecke heraus, das letzte 6,9 s lang. Innerhalb einer
    Ware ("sechs Eier") lagen die Luecken unter 0,15 s. Mit 0,2 s: genau 20.
    """
    rahmen = int(RATE * 0.03)
    rms = []
    for i in range(0, len(werte) - rahmen, rahmen):
        s = werte[i:i + rahmen]
        rms.append(math.sqrt(sum(x * x for x in s) / len(s)))
    if not rms:
        return []
    grund = sorted(rms)[len(rms) // 5]
    schwelle = max(grund * 4, 300)
    sprache = [x > schwelle for x in rms]
    teile, start, stille = [], None, 0
    luecke = int(PAUSE_S / 0.03)
    for i, s in enumerate(sprache + [False] * (luecke + 1)):
        if s:
            if start is None:
                start = i
            stille = 0
        elif start is not None:
            stille += 1
            if stille > luecke:
                ende = i - stille + 1
                if (ende - start) * 0.03 >= 0.25:
                    teile.append((start, ende))
                start, stille = None, 0
    rand = int(0.2 * RATE)
    return [werte[max(0, a * rahmen - rand):min(len(werte), b * rahmen + rand)] for a, b in teile]


# ---------------------------------------------------------- Erkenner ---

def mit_vosk(teile):
    import vosk
    vosk.SetLogLevel(-1)
    t0 = time.time(); modell = vosk.Model(VOSK_GROSS); laden = time.time() - t0
    texte, t0 = [], time.time()
    for s in teile:
        e = vosk.KaldiRecognizer(modell, RATE)
        e.AcceptWaveform(s.tobytes())
        texte.append(json.loads(e.FinalResult()).get("text", ""))
    return texte, laden, time.time() - t0


def mit_whisper(teile, datei, extra=()):
    modell = os.path.join(ZIEL, "modelle", datei)
    with tempfile.TemporaryDirectory() as tmp:
        # Ladezeit getrennt messen: ein halbe Sekunde Stille allein.
        stille = os.path.join(tmp, "stille.wav")
        wav_schreiben(stille, array.array("h", [0] * (RATE // 2)))
        t0 = time.time()
        subprocess.run([WHISPER_CLI, "-m", modell, "-f", stille, "-l", "de", "-nt", "-np",
                        "-t", str(THREADS), *extra], capture_output=True)
        laden = time.time() - t0
        pfade = []
        for i, s in enumerate(teile):
            p = os.path.join(tmp, f"s{i:03d}.wav"); wav_schreiben(p, s); pfade.append(p)
        befehl = [WHISPER_CLI, "-m", modell, "-l", "de", "-nt", "-np", "-otxt", "-t", str(THREADS), *extra]
        for p in pfade:
            befehl += ["-f", p]
        t0 = time.time()
        r = subprocess.run(befehl, capture_output=True, text=True)
        gesamt = time.time() - t0
        if r.returncode != 0:
            sys.exit(f"whisper-cli: {r.stderr[-400:]}")
        texte = []
        for p in pfade:
            try:
                texte.append(" ".join(open(p + ".txt", encoding="utf-8").read().split()))
            except OSError:
                texte.append("")
    # Ein Aufruf laedt das Modell einmal fuer alle Stuecke - abgezogen, damit
    # "je Stueck" die Wartezeit im Diktat ist, wenn das Modell schon geladen ist.
    return texte, laden, max(0.0, gesamt - laden)


def mit_parakeet(teile):
    import sherpa_onnx
    m = PARAKEET
    t0 = time.time()
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f"{m}/encoder.int8.onnx", decoder=f"{m}/decoder.int8.onnx",
        joiner=f"{m}/joiner.int8.onnx", tokens=f"{m}/tokens.txt",
        num_threads=THREADS, model_type="nemo_transducer")
    laden = time.time() - t0
    texte, t0 = [], time.time()
    for s in teile:
        st = rec.create_stream()
        st.accept_waveform(RATE, [x / 32768.0 for x in s])
        rec.decode_stream(st)
        texte.append(st.result.text.strip())
    return texte, laden, time.time() - t0


# ------------------------------------------------------------ Befehle ---

def aufnehmen(name):
    os.makedirs(os.path.join(ZIEL, "aufnahmen"), exist_ok=True)
    pfad = os.path.join(ZIEL, "aufnahmen", f"{name}.wav")
    quellen = subprocess.run(["pactl", "list", "short", "sources"], capture_output=True, text=True).stdout
    quelle = "dialos_mikrofon_ohne_echo" if "dialos_mikrofon_ohne_echo" in quellen else None
    befehl = ["parec", "--format=s16le", f"--rate={RATE}", "--channels=1", "--latency-msec=30"]
    if quelle:
        befehl += ["-d", quelle]
    # DIESELBE MARKE WIE DAS DIKTAT (2026-09-15). Ohne sie hoerte der
    # Sprachdienst beim Vorlesen des Briefs mit, hoerte dreimal
    # "sprachsteuerung starten" heraus und unterbrach Stephan jedes Mal mit der
    # Zu-laut-Ansage. Beim echten Diktat haelt er sich wegen dieser Marke heraus.
    laufzeit = os.environ.get("XDG_RUNTIME_DIR")
    marke = (os.path.join(laufzeit, "dialos-diktat-aktiv") if laufzeit and os.path.isdir(laufzeit)
             else f"/tmp/dialos-diktat-aktiv-{os.getuid()}")
    open(marke, "w").close()
    try:
        return _aufnehmen(pfad, befehl, quelle)
    finally:
        try:
            os.unlink(marke)
        except OSError:
            pass


def _aufnehmen(pfad, befehl, quelle):
    print(f"Aufnahme laeuft -> {pfad}")
    print(f"Quelle: {quelle or 'Standard-Mikrofon'}")
    print("Jetzt vorlesen. Danach die EINGABETASTE druecken.")
    p = subprocess.Popen(befehl, stdout=subprocess.PIPE)
    daten = bytearray()
    import threading
    fertig = threading.Event()
    threading.Thread(target=lambda: (sys.stdin.readline(), fertig.set()), daemon=True).start()
    while not fertig.is_set():
        block = p.stdout.read(1600)
        if not block:
            break
        daten += block
    p.terminate()
    werte = array.array("h"); werte.frombytes(bytes(daten[:len(daten) // 2 * 2]))
    wav_schreiben(pfad, werte)
    print(f"Gespeichert: {len(werte) / RATE:.1f} s, {len(stuecke(werte))} Stuecke erkannt.")


def piper(name, art):
    """Erzeugt die Vorlage mit Annas Stimme - nur um den Ablauf zu pruefen."""
    os.makedirs(os.path.join(ZIEL, "aufnahmen"), exist_ok=True)
    stimme = "/usr/local/share/dialos-piper/voices/de_DE-kerstin-low.onnx"
    werte = array.array("h", [0] * RATE)
    for teil in referenz(art):
        cmd = (f"printf %s {shlex.quote(teil)} | /usr/local/share/dialos-piper/piper/piper "
               f"--model {stimme} --noise_w 0 --output_raw 2>/dev/null")
        roh = subprocess.run(["sh", "-c", cmd], capture_output=True).stdout
        a = array.array("h"); a.frombytes(roh[:len(roh) // 2 * 2])
        werte.extend(a); werte.extend([0] * int(RATE * 1.2))
    pfad = os.path.join(ZIEL, "aufnahmen", f"{name}.wav")
    wav_schreiben(pfad, werte)
    print(f"Piper-Aufnahme: {pfad} ({len(werte) / RATE:.1f} s)")


def vergleichen(name, art):
    pfad = os.path.join(ZIEL, "aufnahmen", f"{name}.wav")
    werte = wav_lesen(pfad)
    teile = stuecke(werte)
    ref = referenz(art)
    ref_text = normal(" ".join(ref))
    dauer = sum(len(s) for s in teile) / RATE
    print(f"Aufnahme {name}: {len(werte) / RATE:.1f} s, {len(teile)} Stuecke "
          f"({dauer:.1f} s Sprache), Vorlage {len(ref)} {'Waren' if art == 'einkaufszettel' else 'Absatz'}")
    erkenner = [("vosk-gross (DialOS heute)", lambda: mit_vosk(teile)),
                ("parakeet-v3", lambda: mit_parakeet(teile))]
    for k, datei, extra in WHISPER_LAEUFE:
        erkenner.append((k, lambda d=datei, x=extra: mit_whisper(teile, d, x)))
    zeilen, details = [], []
    for kennung, lauf in erkenner:
        print(f"  {kennung} ...", flush=True)
        texte, laden, rechnen = lauf()
        hyp = normal(" ".join(texte))
        fehler, n = wortfehler(ref_text, hyp)
        waren = ""
        if art == "einkaufszettel":
            eintraege = {normal(x) for t in texte for x in re.split(r"[,.;]", t) if normal(x)}
            treffer = sum(1 for w in ref if normal(w) in eintraege)
            waren = f"{treffer}/{len(ref)}"
        je = rechnen / max(1, len(teile))
        zeilen.append((kennung, waren, 100 * fehler / max(1, n), laden, je, rechnen / max(0.01, dauer)))
        details.append((kennung, texte))
    zeitstempel = time.strftime("%Y-%m-%d-%H%M%S")
    bericht = [f"# Erkenner-Vergleich {name} ({art}), {zeitstempel}", "",
               f"{len(teile)} Stuecke, {dauer:.1f} s Sprache, {THREADS} Threads", "",
               "| Erkenner | Waren wörtlich | Wortfehler | Laden | je Stück | Rechenzeit/Sprechzeit |",
               "|---|---|---|---|---|---|"]
    for k, w, wer, l, je, rtf in zeilen:
        bericht.append(f"| {k} | {w or '-'} | {wer:.1f} % | {l:.1f} s | {je:.2f} s | {rtf:.2f} |")
    bericht += ["", "## Erkannt je Stück", ""]
    for k, texte in details:
        bericht.append(f"### {k}")
        bericht += [f"{i + 1}. {t}" for i, t in enumerate(texte)] + [""]
    os.makedirs(os.path.join(ZIEL, "ergebnisse"), exist_ok=True)
    ausgabe = os.path.join(ZIEL, "ergebnisse", f"{name}-{zeitstempel}.md")
    open(ausgabe, "w", encoding="utf-8").write("\n".join(bericht) + "\n")
    print()
    print("\n".join(bericht[4:4 + 2 + len(zeilen)]))
    print(f"\nBericht mit allen erkannten Texten: {ausgabe}")


def main():
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "aufnehmen":
        return aufnehmen(a[1])
    if len(a) >= 3 and a[0] == "vergleichen":
        return vergleichen(a[1], a[2])
    if len(a) >= 3 and a[0] == "piper":
        return piper(a[1], a[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
