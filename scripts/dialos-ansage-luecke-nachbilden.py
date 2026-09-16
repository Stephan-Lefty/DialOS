#!/usr/bin/env python3
"""Nachbildung: Wie viele Befehle kommen an, wenn der Nutzer DELAY s nach einer Ansage spricht?

Stephan am 2026-09-15: "Zwischen der Ansage von Anna und meiner Antwort muss ich
immer so 1,5 Sekunden warten. Sonst wird das erste Wort verschluckt!"

Der ECHTE Befehlsdienst laeuft mit echtem Vosk; nachgebildet sind nur das Mikrofon
(eine Pipe, die wie parec bei vollem Puffer verwirft), die Ansagen (Markierungsdatei
und Sprechdauer wie dialos-say, mit "roh" auch mit Michaels Stimme im Mikrofon)
und die Auskunft (spricht nach 0,2 s Start). Michael (Piper) spricht acht Uhrzeit-
und Datumsfragen, jede DELAY s nach dem Ende der vorigen Antwort.

Gemessen am 2026-09-16 (8 Fragen):
    Abstand        vorher   nachher
    0,15 s           4/8      8/8
    0,30 s           4/8      8/8
    0,60 s           4/8      8/8
    0,30 s roh       3/8      8/8

Aufruf:  scripts/dialos-ansage-luecke-nachbilden.py DIENST.py DELAY [roh]
         DIENST.py z. B. iso-build/config/includes.chroot/usr/local/bin/dialos-sprachbefehl-desktop.py
"""
import importlib.util, os, sys, time, threading, subprocess, shlex, array, fcntl, json, math, random

DIENST, DELAY = sys.argv[1], float(sys.argv[2])
ECHO = len(sys.argv) > 3 and sys.argv[3] == "roh"   # rohes Mikrofon: Ansage kommt mit hinein
import tempfile
S = tempfile.mkdtemp(prefix="ansage-luecke-")
MARKE = os.path.join(S, f"marke-{os.getpid()}")
LOG = os.path.join(S, f"log-{os.getpid()}.txt")
RATE = 16000

_cache = {}
def piper(text):
    if text not in _cache:
        cmd = (f"printf %s {shlex.quote(text)} | /usr/local/share/dialos-piper/piper/piper --model "
               f"/usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx --output_raw 2>/dev/null"
               f" | sox -r 22050 -c 1 -b 16 -e signed-integer -t raw - -t raw -r 16000 - 2>/dev/null")
        _cache[text] = array.array("h", subprocess.run(["sh", "-c", cmd], capture_output=True).stdout)
    return _cache[text]

T0 = time.time()
lock = threading.Lock()
klaenge = []      # (start_wallclock, array, faktor)
def einplanen(text, t, faktor=1.0):
    with lock:
        klaenge.append((t, piper(text), faktor))

def raum(von, n):
    """n Samples ab Wandzeit von."""
    out = [random.randint(-30, 30) for _ in range(n)]
    with lock:
        for start, a, f in klaenge:
            i0 = int((von - start) * RATE)
            if i0 + n <= 0 or i0 >= len(a):
                continue
            for k in range(max(0, -i0), min(n, len(a) - i0)):
                out[k] = max(-32768, min(32767, out[k] + int(a[i0 + k] * f)))
    return array.array("h", out).tobytes()

class Proz:
    def __init__(self):
        r, w = os.pipe()
        fcntl.fcntl(w, fcntl.F_SETFL, fcntl.fcntl(w, fcntl.F_GETFL) | os.O_NONBLOCK)
        self.stdout = os.fdopen(r, "rb")
        self._w = w
        self._alive = True
        threading.Thread(target=self._schreiben, daemon=True).start()
    def _schreiben(self):
        t = time.time()
        while self._alive:
            time.sleep(0.03)
            jetzt = time.time()
            n = int((jetzt - t) * RATE)
            if n <= 0:
                continue
            daten = raum(t, n)
            t += n / RATE
            try:
                os.write(self._w, daten)
            except BlockingIOError:
                pass            # Pipe voll: parec verwirft auch
            except (BrokenPipeError, OSError):
                return
    def terminate(self):
        self._alive = False
        try: os.close(self._w)
        except OSError: pass
    def poll(self): return None

sys.argv = ["dialos-sprachbefehl-desktop.py"]
spec = importlib.util.spec_from_file_location("dienst", DIENST)
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
d.MARKIERUNG = MARKE
d.DIKTAT_MARKE = MARKE + "-diktat"
d.PROTOKOLL = LOG
for name in ("alte_instanzen_beenden", "mitschrift_oeffnen", "mitschrift_schliessen", "pegel_richten"):
    setattr(d, name, lambda *a, **k: None)
d.waehle_mikrofon = lambda: ("test-roh" if ECHO else d.ECHO_QUELLE)
def starten(quelle):
    time.sleep(0.3)             # wie im Original: Warten vor pegel_richten
    return Proz()
d.aufnahme_starten = starten
os.environ["FAKE_MARKE"] = MARKE

def ansage(text):
    """Wie dialos-say: Marke, Sprechen (mit Echo?), Marke weg."""
    open(MARKE, "w").close()
    a = piper(text)
    if ECHO:
        einplanen(text, time.time(), 0.4)
    time.sleep(len(a) / RATE + 0.1)
    os.remove(MARKE)
d.sprich = ansage
auskunft_skript = os.path.join(S, "auskunft-fake.py")
with open(auskunft_skript, "w") as f:
    f.write("#!/usr/bin/env python3\nimport sys,time,os\n"
            "sys.path.insert(0, %r)\n" % S +
            "time.sleep(0.2)\n")
os.chmod(auskunft_skript, 0o755)
# Auskunft: spricht wie im Echten nach kurzem Start
_popen = d.subprocess.Popen
class SubWrap:
    def __getattr__(self, k): return getattr(subprocess, k)
    def Popen(self, args, **kw):
        if args and args[0] == d.AUSKUNFT_SKRIPT:
            text = "Es ist siebzehn Uhr fünfundvierzig." if args[1] == "uhrzeit" else "Heute ist Mittwoch, der sechzehnte September."
            threading.Thread(target=lambda: (time.sleep(0.2), ansage(text)), daemon=True).start()
            return None
        return _popen(args, **kw)
d.subprocess = SubWrap()
d.AUSKUNFT_SKRIPT = auskunft_skript

folge = ["Sprachsteuerung starten", "Welchen Tag haben wir", "Wie viel Uhr ist es",
         "Welches Datum haben wir", "Wie spät ist es", "Welchen Tag haben wir",
         "Wie ist die Uhrzeit", "Welches Datum haben wir", "Wie viel Uhr ist es"]
for t in folge: piper(t)

def regie():
    time.sleep(2.0)
    einplanen(folge[0], time.time())
    for text in folge[1:]:
        # warten auf Ende einer Ansage (Marke kommt und geht), hoechstens 8 s
        frist = time.time() + 8
        while not os.path.exists(MARKE) and time.time() < frist: time.sleep(0.01)
        while os.path.exists(MARKE) and time.time() < frist: time.sleep(0.01)
        time.sleep(DELAY)
        einplanen(text, time.time())
        time.sleep(len(piper(text)) / RATE)
    time.sleep(6)
    log = open(LOG, encoding="utf-8").read()
    erkannt = [z.split("erkannt: ")[1].split("  (")[0] for z in log.splitlines() if "erkannt: " in z]
    ausgefuehrt = log.count("Auskunft '")
    print(json.dumps({"delay": DELAY, "roh": ECHO, "dienst": os.path.basename(DIENST),
                      "auskuenfte": ausgefuehrt, "von": len(folge) - 1, "erkannt": erkannt}, ensure_ascii=False), flush=True)
    for p in (MARKE, LOG):
        try: os.remove(p)
        except OSError: pass
    os._exit(0)

threading.Thread(target=regie, daemon=True).start()
d.main()
