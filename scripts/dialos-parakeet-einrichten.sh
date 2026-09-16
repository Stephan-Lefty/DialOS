#!/bin/bash
# DialOS: Parakeet fest einrichten - die Texterkennung fuer Brief und Notizen.
#
# Stephan am 2026-09-16: "Ja, bau Parakeet fest ein". Vorher gemessen auf dem
# Pruefstand (docs/pruefstand.md, docs/diktat.md): frei diktierter Brief Parakeet
# 3,4 % Wortfehler, Vosk 28,8 %; vorgelesener Brief 2,8 % gegen 12,7 %, und nur
# Parakeet setzt die Satzzeichen selbst ("Weg 3"). Befehle und Einkaufszettel
# bleiben bei Vosk.
#
# WAS INSTALLIERT WIRD
#   Parakeet TDT 0.6B v3 int8    ~641 MB entpackt   NVIDIA, CC-BY-4.0
#     (sherpa-onnx-Paketierung)  github.com/k2-fsa/sherpa-onnx, asr-models
#     -> /usr/local/share/dialos-parakeet/
#   sherpa-onnx 1.13.8           ~45 MB             Apache-2.0, pypi.org
#     -> systemweit per pip, wie Vosk in Schritt 15
#
# Jede Modelldatei wird gegen ihre sha256 geprueft (gemessen am 2026-09-16 an der
# Kopie, die seit dem 14.09. im Vergleich lief; das Archiv selbst gegen die
# Pruefsumme der Quelle). Mehrfach aufrufbar: Was da ist und stimmt, bleibt.
#
# Aufruf OHNE sudo (fragt selbst nach dem Passwort):
#   scripts/dialos-parakeet-einrichten.sh [ORDNER-MIT-ENTPACKTEM-MODELL]
# Mit Ordner wird von dort kopiert statt geladen - auf dem Entwicklungsgeraet
# liegt das Modell schon im Messordner erkenner-vergleich/modelle/.
set -euo pipefail

ZIEL="/usr/local/share/dialos-parakeet"
MODELL="sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/${MODELL}.tar.bz2"
ARCHIV_SHA256="5793d0fd397c5778d2cf2126994d58e9d56b1be7c04d13c7a15bb1b4eafb16bf"
SHERPA_VERSION="1.13.8"
QUELLE="${1:-}"

declare -A SHA=(
  [encoder.int8.onnx]="acfc2b4456377e15d04f0243af540b7fe7c992f8d898d751cf134c3a55fd2247"
  [decoder.int8.onnx]="179e50c43d1a9de79c8a24149a2f9bac6eb5981823f2a2ed88d655b24248db4e"
  [joiner.int8.onnx]="3164c13fc2821009440d20fcb5fdc78bff28b4db2f8d0f0b329101719c0948b3"
  [tokens.txt]="d58544679ea4bc6ac563d1f545eb7d474bd6cfa467f0a6e2c1dc1c7d37e3c35d"
)

schritt() { echo; echo "=== $1 ==="; }
fehler() { echo "FEHLER: $1" >&2; exit 1; }

if [ "$(id -u)" -eq 0 ]; then
  fehler "Bitte OHNE sudo starten - das Skript fragt selbst."
fi

# Stimmen alle vier Dateien in ORDNER mit den Pruefsummen ueberein?
modell_stimmt() {
  local ordner="$1" datei
  for datei in "${!SHA[@]}"; do
    [ -f "$ordner/$datei" ] || return 1
    [ "$(sha256sum "$ordner/$datei" | cut -d' ' -f1)" = "${SHA[$datei]}" ] || return 1
  done
  return 0
}

schritt "1/3 Modell nach $ZIEL/$MODELL"
if modell_stimmt "$ZIEL/$MODELL"; then
  echo "  vorhanden und geprueft"
else
  tmp="$(mktemp -d)"
  if [ -n "$QUELLE" ] && modell_stimmt "$QUELLE"; then
    echo "  kopiere aus $QUELLE (Pruefsummen stimmen)"
    mkdir -p "$tmp/$MODELL"
    for datei in "${!SHA[@]}"; do cp "$QUELLE/$datei" "$tmp/$MODELL/"; done
  else
    [ -n "$QUELLE" ] && echo "  $QUELLE passt nicht zu den Pruefsummen - lade von der Quelle"
    echo "  lade $URL (465 MB) ..."
    curl -L --fail --retry 3 -o "$tmp/modell.tar.bz2" "$URL"
    [ "$(sha256sum "$tmp/modell.tar.bz2" | cut -d' ' -f1)" = "$ARCHIV_SHA256" ] \
      || fehler "Pruefsumme des Archivs stimmt nicht"
    echo "  entpacke ..."
    tar -xjf "$tmp/modell.tar.bz2" -C "$tmp"
    rm -f "$tmp/modell.tar.bz2"
    modell_stimmt "$tmp/$MODELL" || fehler "Pruefsummen der entpackten Dateien stimmen nicht"
  fi
  sudo mkdir -p "$ZIEL"
  sudo rm -rf "$ZIEL/$MODELL.neu"
  sudo cp -r "$tmp/$MODELL" "$ZIEL/$MODELL.neu"
  sudo rm -rf "$ZIEL/$MODELL"
  sudo mv "$ZIEL/$MODELL.neu" "$ZIEL/$MODELL"
  sudo chmod -R a+rX "$ZIEL"
  rm -rf "$tmp"
  modell_stimmt "$ZIEL/$MODELL" || fehler "Modell nach dem Kopieren nicht vollstaendig"
  echo "  ok"
fi

schritt "2/3 sherpa-onnx $SHERPA_VERSION (systemweit, wie Vosk)"
if python3 -c "import sherpa_onnx, sys; sys.exit(0 if sherpa_onnx.__version__ == '$SHERPA_VERSION' else 1)" 2>/dev/null; then
  echo "  schon installiert"
else
  sudo pip3 install --break-system-packages "sherpa-onnx==$SHERPA_VERSION"
fi

schritt "3/3 Selbsttest"
python3 - "$ZIEL/$MODELL" <<'PY'
import sys, time
import sherpa_onnx
m = sys.argv[1]
t = time.time()
r = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{m}/encoder.int8.onnx", decoder=f"{m}/decoder.int8.onnx",
    joiner=f"{m}/joiner.int8.onnx", tokens=f"{m}/tokens.txt",
    num_threads=4, model_type="nemo_transducer")
print(f"  Modell geladen in {time.time()-t:.1f} s")
stille = [0.0] * 16000
s = r.create_stream(); s.accept_waveform(16000, stille); r.decode_stream(s)
print(f"  Erkennung laeuft (Stille ergibt {s.result.text!r})")
PY

echo
echo "Eingerichtet: $ZIEL/$MODELL"
echo "FERTIG"
