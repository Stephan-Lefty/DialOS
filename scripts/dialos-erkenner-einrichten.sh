#!/bin/bash
# DialOS: richtet den Vergleich der Spracherkenner fuers Diktat ein.
#
# Stephan am 2026-09-14: "Was mir aktuell noch Kopfzerbrechen macht ist der
# Einkaufszettel. Gibt es noch 'bessere' Sprachsteuerungssysteme" - und nach
# der Aufteilung (Befehle weiter Vosk, freier Text vielleicht Whisper):
# "bereite die Messung vor und stelle mir die Befehle fuer Download &
# Installation zur Verfuegung".
#
# WAS HIER INSTALLIERT WIRD - NUR ZUM MESSEN, NICHT FUER DEN BETRIEB. Alles
# landet in einem eigenen Ordner neben dem Repo, nichts unter /usr/local und
# nichts im Autostart. Faellt der Vergleich gegen Whisper und Parakeet aus,
# genuegt es, den Ordner zu loeschen.
#
#   whisper.cpp v1.9.4    github.com/ggml-org/whisper.cpp      MIT, aus dem Quelltext gebaut
#   ggml-small.bin          465 MB  huggingface.co/ggerganov/whisper.cpp   MIT
#   ggml-large-v3-turbo-q5_0.bin
#                           547 MB  huggingface.co/ggerganov/whisper.cpp   MIT
#   Parakeet TDT 0.6B v3 int8
#                           465 MB  github.com/k2-fsa/sherpa-onnx (asr-models)
#                                   Modell CC-BY-4.0 (NVIDIA), 25 Sprachen inkl. Deutsch
#   sherpa-onnx 1.13.8       ~14 MB  pypi.org                             Apache-2.0
#   cmake, python3-venv            Debian-Pakete (apt)
#
# Zusammen rund 1,5 GB. Adressen, Groessen und Pruefsummen am 2026-09-14 per
# Kopfabfrage an den Quellen geprueft. Jede Modelldatei wird nach dem Laden
# gegen die Pruefsumme der Quelle kontrolliert; stimmt sie nicht, bricht das
# Skript ab und die Datei bleibt als ".teil" liegen.
#
# Mehrfach aufrufbar: Was schon da ist und stimmt, wird uebersprungen.
#
# Aufruf (OHNE sudo - nur der apt-Schritt fragt nach dem Passwort):
#   scripts/dialos-erkenner-einrichten.sh [ZIELORDNER]
set -euo pipefail

ZIEL="${1:-/media/dialosadmin/SanDisk-Extreme/DialOS/erkenner-vergleich}"
WHISPER_VERSION="v1.9.4"
SHERPA_VERSION="1.13.8"
HF="https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
PARAKEET="sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
PARAKEET_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/${PARAKEET}.tar.bz2"
PARAKEET_SHA256="5793d0fd397c5778d2cf2126994d58e9d56b1be7c04d13c7a15bb1b4eafb16bf"

schritt() { echo; echo "=== $1 ==="; }
fehler() { echo "FEHLER: $1" >&2; exit 1; }

if [ "$(id -u)" -eq 0 ]; then
  fehler "Bitte OHNE sudo starten - sonst gehoeren die Dateien root."
fi
mkdir -p "$ZIEL/modelle" "$ZIEL/aufnahmen" "$ZIEL/ergebnisse"

# Laedt eine Datei nach ZIEL/modelle und prueft sie gegen die erwartete
# sha256. Abgebrochene Downloads werden fortgesetzt (-C -).
laden() {
  local url="$1" datei="$2" soll="$3"
  local pfad="$ZIEL/modelle/$datei"
  if [ -f "$pfad" ]; then
    echo "  vorhanden: $datei - pruefe Pruefsumme ..."
    if [ "$(sha256sum "$pfad" | cut -d' ' -f1)" = "$soll" ]; then
      echo "  ok"; return 0
    fi
    echo "  Pruefsumme stimmt nicht - lade neu"; rm -f "$pfad"
  fi
  echo "  lade $datei ..."
  curl -L --fail --retry 3 -C - -o "$pfad.teil" "$url"
  echo "  pruefe Pruefsumme ..."
  [ "$(sha256sum "$pfad.teil" | cut -d' ' -f1)" = "$soll" ] \
    || fehler "Pruefsumme von $datei stimmt nicht (Datei bleibt als $pfad.teil)"
  mv "$pfad.teil" "$pfad"
  echo "  ok"
}

# Die erwartete Pruefsumme eines Hugging-Face-Modells steht im Kopf der
# Antwort (X-Linked-ETag = sha256 der Datei).
hf_sha256() {
  curl -sIL --max-time 60 "$HF/$1" | tr -d '\r' \
    | awk 'tolower($1)=="x-linked-etag:"{gsub(/"/,"",$2); print $2}' | tail -1
}

schritt "1/6 Werkzeuge: cmake, python3-venv (fragt nach dem Passwort)"
if command -v cmake >/dev/null 2>&1 && dpkg -s python3-venv >/dev/null 2>&1; then
  echo "  schon installiert"
else
  sudo apt-get install -y cmake python3-venv
fi

schritt "2/6 whisper.cpp $WHISPER_VERSION holen und bauen"
if [ ! -d "$ZIEL/whisper.cpp/.git" ]; then
  git clone --depth 1 --branch "$WHISPER_VERSION" https://github.com/ggml-org/whisper.cpp "$ZIEL/whisper.cpp"
else
  echo "  Quelltext vorhanden"
fi
if [ ! -x "$ZIEL/whisper.cpp/build/bin/whisper-cli" ]; then
  cmake -S "$ZIEL/whisper.cpp" -B "$ZIEL/whisper.cpp/build" -DCMAKE_BUILD_TYPE=Release \
    -DWHISPER_BUILD_TESTS=OFF -DWHISPER_BUILD_EXAMPLES=ON >/dev/null
  cmake --build "$ZIEL/whisper.cpp/build" -j"$(nproc)" --target whisper-cli
else
  echo "  schon gebaut"
fi

schritt "3/6 Whisper-Modelle (465 MB + 547 MB)"
for m in ggml-small.bin ggml-large-v3-turbo-q5_0.bin; do
  soll="$(hf_sha256 "$m")"
  [ -n "$soll" ] || fehler "Pruefsumme fuer $m nicht abrufbar (Netz?)"
  laden "$HF/$m" "$m" "$soll"
done

schritt "4/6 Parakeet TDT 0.6B v3 (465 MB)"
if [ ! -f "$ZIEL/modelle/$PARAKEET/tokens.txt" ]; then
  laden "$PARAKEET_URL" "$PARAKEET.tar.bz2" "$PARAKEET_SHA256"
  echo "  entpacke ..."
  tar -xjf "$ZIEL/modelle/$PARAKEET.tar.bz2" -C "$ZIEL/modelle"
  rm -f "$ZIEL/modelle/$PARAKEET.tar.bz2"
else
  echo "  schon entpackt"
fi

schritt "5/6 Python-Umgebung mit sherpa-onnx $SHERPA_VERSION"
# --system-site-packages: Vosk ist systemweit installiert und soll im
# Vergleich GENAU die Fassung sein, die DialOS benutzt.
if [ ! -x "$ZIEL/venv/bin/python" ]; then
  python3 -m venv --system-site-packages "$ZIEL/venv"
fi
"$ZIEL/venv/bin/pip" install --quiet "sherpa-onnx==$SHERPA_VERSION"

schritt "6/6 Selbsttest"
"$ZIEL/venv/bin/python" - "$ZIEL" "$PARAKEET" <<'PY'
import sys, os, subprocess, time
ziel, parakeet = sys.argv[1], sys.argv[2]
import vosk, sherpa_onnx
print("  vosk und sherpa-onnx laden: ok")
m = os.path.join(ziel, "modelle", parakeet)
t = time.time()
sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{m}/encoder.int8.onnx", decoder=f"{m}/decoder.int8.onnx",
    joiner=f"{m}/joiner.int8.onnx", tokens=f"{m}/tokens.txt",
    num_threads=4, model_type="nemo_transducer")
print(f"  Parakeet-Modell laden: ok ({time.time()-t:.1f} s)")
cli = os.path.join(ziel, "whisper.cpp/build/bin/whisper-cli")
probe = os.path.join(ziel, "whisper.cpp/samples/jfk.wav")
t = time.time()
r = subprocess.run([cli, "-m", os.path.join(ziel, "modelle/ggml-small.bin"), "-f", probe,
                    "-l", "en", "-nt", "-np", "-t", "4"], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f"  whisper-cli: FEHLER\n{r.stderr[-500:]}")
print(f"  whisper-cli mit Beispiel: ok ({time.time()-t:.1f} s) - {r.stdout.strip()[:60]!r}")
PY

echo
echo "Eingerichtet in: $ZIEL"
echo "FERTIG"
