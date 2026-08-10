#!/bin/sh
# DialOS: Setzt die DialOS-Bildmarke als Profilbild (Avatar) für ein
# Benutzerkonto - gedacht für "DialOS-Admin" direkt nach der
# Debian-Installation, funktioniert aber für jedes Konto (z.B. auch
# "nutzer", falls gewünscht).
#
# WICHTIG: Braucht einen laufenden D-Bus + AccountsService-Dienst, geht
# also NICHT in der alten Docker/Chroot-Pipeline - siehe
# scripts/dialos-setup-nutzer.sh für den Hintergrund dazu.
#
# Setzt voraus, dass das Branding schon eingerichtet ist (Punkt 3 im
# Büro-Setup, siehe CLAUDE.md) - die Bildmarke liegt dann unter
# /usr/share/pixmaps/distributor-logo.png (512x512, aus assets/mark.png).
#
# Nutzung: sudo ./dialos-set-avatar.sh [benutzername]
#   benutzername Standard: $SUDO_USER

set -e

ICON_SOURCE="/usr/share/pixmaps/distributor-logo.png"
TARGET_USER="${1:-$SUDO_USER}"

if [ -z "$TARGET_USER" ]; then
  echo "[dialos] Kein Benutzer angegeben und \$SUDO_USER ist leer." >&2
  echo "[dialos] Aufruf: sudo ./dialos-set-avatar.sh <benutzername>" >&2
  exit 1
fi

if [ ! -f "$ICON_SOURCE" ]; then
  echo "[dialos] Icon-Datei $ICON_SOURCE nicht gefunden - wurde das" >&2
  echo "[dialos] Branding (Punkt 3 im Büro-Setup) schon eingerichtet?" >&2
  exit 1
fi

USER_PATH=$(gdbus call --system --dest org.freedesktop.Accounts \
  --object-path /org/freedesktop/Accounts \
  --method org.freedesktop.Accounts.FindUserByName "$TARGET_USER" \
  | sed -E "s/^\(objectpath '([^']+)',?\)\$/\1/")

echo "[dialos] Setze DialOS-Bildmarke als Profilbild für '$TARGET_USER' ($USER_PATH)..."
gdbus call --system --dest org.freedesktop.Accounts \
  --object-path "$USER_PATH" \
  --method org.freedesktop.Accounts.User.SetIconFile "$ICON_SOURCE"

echo "[dialos] Fertig. Sichtbar im Anmeldebildschirm und in den Einstellungen."
