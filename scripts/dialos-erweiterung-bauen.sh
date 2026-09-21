#!/bin/bash
# Packt die Thunderbird-Erweiterung an ihren festen Platz.
#
# WARUM NICHT DIE FERTIGE .xpi INS REPO: Sie waere eine zweite Fassung
# derselben zwei Dateien - und die erste, die vergessen wird, wenn jemand
# hintergrund.js aendert. Dann laeuft auf dem Geraet eine andere Erweiterung
# als im Repo steht, und niemand sieht es. Dieselbe Lehre wie bei
# dialos-installstand.sh: Das Repo ist die Vorlage, nicht der Beweis.
#
# Nach jeder Aenderung an der Erweiterung aufrufen - und die Fassung in
# manifest.json hochzaehlen, sonst nimmt Thunderbird die neue Datei nicht an.
#
# Aufruf:  sudo scripts/dialos-erweiterung-bauen.sh
set -eu
HIER="$(cd "$(dirname "$0")/.." && pwd)"
QUELLE="$HIER/thunderbird-erweiterung"
ZIEL="/usr/local/share/dialos/dialos-bruecke.xpi"

if [ "$(id -u)" -ne 0 ]; then
    echo "Bitte mit sudo aufrufen - $ZIEL gehoert root." >&2
    exit 2
fi
FASSUNG=$(python3 -c "import json;print(json.load(open('$QUELLE/manifest.json'))['version'])")
install -d -m 0755 /usr/local/share/dialos
python3 - "$QUELLE" "$ZIEL" <<'PY'
import sys, zipfile, os
quelle, ziel = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(ziel, "w") as z:
    for datei in ("manifest.json", "hintergrund.js"):
        z.write(os.path.join(quelle, datei), datei)
PY
chmod 0644 "$ZIEL"
echo "Erweiterung $FASSUNG gepackt: $ZIEL"
echo "Thunderbird uebernimmt sie beim naechsten Start (policies.json, force_installed)."
