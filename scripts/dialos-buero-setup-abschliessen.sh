#!/bin/sh
# DialOS: Kompletter Buero-Setup-Abschluss nach einer frischen
# Installation - fasst mehrere Einzelschritte in einem Klick zusammen:
# 1. Avatar fuer das Admin-Konto setzen
# 2. "nutzer"-Konto anlegen + Autologin umschalten
# 3. Firefox-Startseite pruefen (sollte automatisch aus der ISO kommen)
#
# Aufruf: sudo ./dialos-buero-setup-abschliessen.sh [admin-benutzername]
#   admin-benutzername Standard: $SUDO_USER (also "dialosadmin")
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ADMIN_USER="${1:-$SUDO_USER}"
if [ -z "$ADMIN_USER" ]; then
  echo "[dialos] Kein Admin-Benutzer angegeben und \$SUDO_USER ist leer." >&2
  echo "[dialos] Aufruf: sudo ./dialos-buero-setup-abschliessen.sh <admin-benutzername>" >&2
  exit 1
fi

echo "=== [dialos] Schritt 1/3: Avatar setzen ==="
"$SCRIPT_DIR/dialos-set-avatar.sh" "$ADMIN_USER"

echo ""
echo "=== [dialos] Schritt 2/3: Nutzer-Konto + Autologin ==="
"$SCRIPT_DIR/dialos-setup-nutzer.sh" "$ADMIN_USER"

echo ""
echo "=== [dialos] Schritt 3/3: Firefox-Startseite pruefen ==="
POLICY_FILE="/usr/lib/firefox-esr/distribution/policies.json"
if [ -f "$POLICY_FILE" ] && grep -q "dialos.org" "$POLICY_FILE"; then
  echo "[dialos] Firefox-Startseite ist korrekt gesetzt (automatisch aus der ISO)."
else
  echo "[dialos] WARNUNG: Firefox-Startseiten-Policy fehlt oder ist falsch!" >&2
  echo "[dialos]          Erwartet unter: $POLICY_FILE" >&2
fi

echo ""
echo "=== [dialos] Alles erledigt. Bitte einmal neu starten. ==="
