#!/bin/bash
# DialOS: Stellt nach einem Reinstall des T490 die Arbeitsumgebung fuer
# Claude Code wieder her - Dinge, die sonst bei jedem neuen System von
# Hand wieder eingerichtet werden muessten:
#   1. Sudoers-Regel, die "eggs produce" ohne Passwortabfrage erlaubt
#      (eng begrenzt - keine allgemeine sudo-Freigabe).
#   2. Symlink ~/DialOS -> Repo auf der externen Platte.
#
# Deckt bewusst NICHT die Claude-Anmeldung selbst ab (Login-
# Session/Zugangsdaten) - das automatisch zu sichern/wiederherzustellen
# waere Zugangsdaten-Handling, das hier grundsaetzlich nicht gemacht
# wird. Einfach "claude" starten und dich normal neu einloggen, dauert
# nur wenige Sekunden.
#
# Aufruf: sudo ./dialos-claude-setup.sh
set -euo pipefail

ADMIN_USER="dialosadmin"
REPO_PATH="/media/dialosadmin/SanDisk-Extreme/DialOS/repo"
SYMLINK_PATH="/home/$ADMIN_USER/DialOS"
SUDOERS_FILE="/etc/sudoers.d/dialos-eggs"
SUDOERS_RULE='dialosadmin ALL=(root) NOPASSWD: /usr/bin/eggs produce, /usr/bin/eggs produce *'

if [ "$(id -u)" -ne 0 ]; then
  echo "Bitte mit sudo ausfuehren." >&2
  exit 1
fi

echo "=== 1/2: Sudoers-Regel fuer 'eggs produce' ==="
if [ -f "$SUDOERS_FILE" ] && grep -qF "$SUDOERS_RULE" "$SUDOERS_FILE"; then
  echo "  Bereits vorhanden, nichts zu tun."
else
  echo "$SUDOERS_RULE" > "$SUDOERS_FILE"
  chmod 440 "$SUDOERS_FILE"
  if ! visudo -c -f "$SUDOERS_FILE" >/dev/null 2>&1; then
    echo "  FEHLER: Syntaxpruefung fehlgeschlagen, Datei wird wieder entfernt." >&2
    rm -f "$SUDOERS_FILE"
    exit 1
  fi
  echo "  Angelegt: $SUDOERS_FILE"
fi

echo ""
echo "=== 2/2: Symlink ~/DialOS -> externe Platte ==="
if [ ! -d "$REPO_PATH" ]; then
  echo "  WARNUNG: $REPO_PATH nicht gefunden - ist die externe Platte eingesteckt?" >&2
elif [ -L "$SYMLINK_PATH" ] && [ "$(readlink -f "$SYMLINK_PATH")" = "$(readlink -f "$REPO_PATH")" ]; then
  echo "  Bereits korrekt gesetzt, nichts zu tun."
elif [ -e "$SYMLINK_PATH" ] && [ ! -L "$SYMLINK_PATH" ]; then
  echo "  WARNUNG: $SYMLINK_PATH existiert bereits und ist KEIN Symlink - wird nicht angefasst." >&2
else
  ln -sfn "$REPO_PATH" "$SYMLINK_PATH"
  chown -h "$ADMIN_USER:$ADMIN_USER" "$SYMLINK_PATH"
  echo "  Gesetzt: $SYMLINK_PATH -> $REPO_PATH"
fi

echo ""
echo "=== Nicht automatisiert: Claude-Anmeldung ==="
echo "  Bitte einmal 'claude' starten und dich normal einloggen."
echo ""
echo "=== Fertig ==="
