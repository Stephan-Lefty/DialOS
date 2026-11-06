#!/bin/bash
# Traegt den SessionStart-Hook (automatischer git pull) auch in den Ordner
# UEBER dem Repo ein. Noetig, wenn die Claude-App dort gestartet wird: Sie
# liest dann nur <Ordner>/.claude/, nicht repo/.claude/settings.json.
# Vorhandene Einstellungen bleiben erhalten; mehrfaches Ausfuehren schadet nicht.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ZIEL="$(dirname "$REPO")/.claude/settings.local.json"

python3 - "$REPO/.claude/settings.json" "$ZIEL" <<'EOF'
import json, os, sys
quelle, ziel = sys.argv[1], sys.argv[2]
hook = json.load(open(quelle))["hooks"]["SessionStart"]
os.makedirs(os.path.dirname(ziel), exist_ok=True)
daten = json.load(open(ziel)) if os.path.exists(ziel) else {}
daten.setdefault("hooks", {})["SessionStart"] = hook
with open(ziel, "w") as f:
    json.dump(daten, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("Eingetragen in", ziel)
EOF
