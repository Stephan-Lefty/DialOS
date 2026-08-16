#!/bin/bash
# DialOS: Stellt nach einem Reinstall des T490 die Arbeitsumgebung fuer
# Claude Code wieder her - Dinge, die sonst bei jedem neuen System von
# Hand wieder eingerichtet werden muessten:
#   1. Entfernt die alte Sudoers-Regel fuer "eggs produce" (Penguins'
#      Eggs ist am 2026-08-16 entfallen, siehe Schritt 16 der Doku -
#      eine passwortlose sudo-Regel soll nicht als Altlast bleiben).
#   2. Symlink ~/DialOS -> Repo auf der externen Platte.
#   3. Git-Identitaet (user.name/user.email) + credential.helper=store
#      fuer den Admin-Nutzer, damit "git push" nicht bei jedem Reinstall
#      erneut mit "Identitaet unbekannt" abbricht.
#
# Deckt ABSICHTLICH NICHT ab (kein Bug, sondern Sicherheitsgrenze):
#   - Die Claude-Chat-Anmeldung selbst (Login-Session/Zugangsdaten) -
#     einfach "claude" starten und dich normal neu einloggen, dauert nur
#     wenige Sekunden.
#   - Den Connector fuer die externe Platte bzw. die GitHub-Integration
#     in der Claude-App: keine Wiederherstellung moeglich, weder per
#     Skript noch in der App selbst - nach einem Reinstall muessen
#     diese Verbindungen (und der bisherige Chat) komplett neu
#     eingerichtet werden, es gibt dafuer keinen Speicher-/Restore-
#     Mechanismus (bestaetigt von Stephan, 2026-08-14).
#   - Das GitHub-Token selbst: "git push" fragt beim allerersten Mal
#     nach diesem Reinstall einmalig nach Benutzername + Token - das
#     muss von Hand eingetippt werden, kein Skript/keine KI nimmt
#     Passwoerter/Tokens entgegen.
#
# Aufruf: sudo ./dialos-claude-setup.sh
set -euo pipefail

ADMIN_USER="dialosadmin"
REPO_PATH="/media/dialosadmin/SanDisk-Extreme/DialOS/repo"
SYMLINK_PATH="/home/$ADMIN_USER/DialOS"
# Bis 2026-08-16 legte dieses Skript hier eine Sudoers-Regel an, die
# "eggs produce" ohne Passwortabfrage erlaubte. Penguins' Eggs ist mit
# der Umstellung auf Clonezilla/Rescuezilla entfallen (siehe
# docs/Debian-zu-DialOS.md, Schritt 16). Die Regel zeigte damit auf ein
# /usr/bin/eggs, das es nicht mehr gibt - harmlos, aber eine
# passwortlose sudo-Regel soll nicht als Altlast herumliegen. Sie wird
# jetzt entfernt statt angelegt.
SUDOERS_FILE="/etc/sudoers.d/dialos-eggs"
GIT_NAME="Stephan Rösner"
GIT_EMAIL="stephan.roesner@protonmail.com"

if [ "$(id -u)" -ne 0 ]; then
  echo "Bitte mit sudo ausfuehren: sudo $0" >&2
  exit 1
fi

echo "=== 1/3: Alte 'eggs produce'-Sudoers-Regel entfernen ==="
if [ -f "$SUDOERS_FILE" ]; then
  rm -f "$SUDOERS_FILE"
  echo "  Entfernt: $SUDOERS_FILE (eggs wird nicht mehr verwendet)."
else
  echo "  Nicht vorhanden, nichts zu tun."
fi

echo ""
echo "=== 2/3: Symlink ~/DialOS -> externe Platte ==="
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
echo "=== 3/3: Git-Identitaet + Credential-Speicher fuer $ADMIN_USER ==="
CURRENT_NAME=$(sudo -u "$ADMIN_USER" -H git config --global user.name 2>/dev/null || true)
CURRENT_EMAIL=$(sudo -u "$ADMIN_USER" -H git config --global user.email 2>/dev/null || true)
if [ "$CURRENT_NAME" = "$GIT_NAME" ] && [ "$CURRENT_EMAIL" = "$GIT_EMAIL" ]; then
  echo "  Identitaet bereits korrekt gesetzt ($GIT_NAME <$GIT_EMAIL>)."
else
  sudo -u "$ADMIN_USER" -H git config --global user.name "$GIT_NAME"
  sudo -u "$ADMIN_USER" -H git config --global user.email "$GIT_EMAIL"
  echo "  Gesetzt: $GIT_NAME <$GIT_EMAIL>"
fi

CURRENT_HELPER=$(sudo -u "$ADMIN_USER" -H git config --global credential.helper 2>/dev/null || true)
if [ "$CURRENT_HELPER" = "store" ]; then
  echo "  credential.helper bereits auf 'store' gesetzt."
else
  sudo -u "$ADMIN_USER" -H git config --global credential.helper store
  echo "  credential.helper auf 'store' gesetzt."
fi
echo "  Hinweis: Beim naechsten 'git push' fragt Git einmalig nach"
echo "  Benutzername (Stephan-Lefty) + GitHub-Token - danach gemerkt."

echo ""
echo "=== Nicht automatisiert (siehe Kommentar oben) ==="
echo "  - Claude-Chat-Anmeldung: 'claude' starten, normal einloggen."
echo "  - Connector fuer externe Platte + GitHub-Integration sowie der"
echo "    bisherige Chat: keine Wiederherstellung moeglich, muessen in"
echo "    der Claude-App komplett neu eingerichtet werden."
echo ""
echo "=== Fertig ==="
