#!/bin/sh
# DialOS: Standard-Benutzer "nutzer" auf einem bereits eingerichteten,
# echten System anlegen und Autologin von einem Admin-Konto (im
# Büro-Setup künftig "DialOS-Admin", auf dem aktuellen Testgerät
# "stephan") auf "nutzer" umschalten.
#
# WICHTIG: Dieses Skript gehört zur "neuen" Vorgehensweise (Debian 13 +
# GNOME direkt auf echter Hardware einrichten, siehe CLAUDE.md), NICHT
# zur alten Docker/Chroot-live-build-Pipeline in iso-build/. Der
# Autologin-Teil braucht einen laufenden D-Bus + AccountsService-Dienst,
# das gibt es in einer Chroot-Build-Umgebung nicht.
#
# Führe dieses Skript als LETZTEN Schritt des Büro-Setups aus, nachdem
# Pakete, Branding, RustDesk, Claude Code CLI installiert und das
# Plymouth-Theme aktiviert sind (siehe CLAUDE.md "Nächste konkrete
# Schritte", Punkte 2-4).
#
# Hintergrund zum Autologin-Mechanismus: Der eigentliche Schalter ist
# NICHT /etc/gdm3/custom.conf (das wird von GDM in dieser Debian-13/
# GDM-48-Kombination für die Benutzerauswahl offenbar ignoriert),
# sondern eine Pro-Benutzer-Eigenschaft direkt im AccountsService-Dienst
# (org.freedesktop.Accounts.User.AutomaticLogin, per D-Bus gesetzt).
# Volle Debugging-Historie dazu in CLAUDE.md, Abschnitt
# "GELÖST: GDM-Autologin".
#
# Nutzung: sudo ./dialos-setup-nutzer.sh [admin-benutzername]
#   admin-benutzername ist das Büro-Setup-Konto, dessen Autologin
#   deaktiviert wird (Standard: $SUDO_USER, also der Benutzer, der
#   gerade "sudo" aufgerufen hat).

set -e

USERNAME=nutzer
ADMIN_USER="${1:-$SUDO_USER}"

if [ -z "$ADMIN_USER" ]; then
  echo "[dialos] Kein Admin-Benutzer angegeben und \$SUDO_USER ist leer." >&2
  echo "[dialos] Aufruf: sudo ./dialos-setup-nutzer.sh <admin-benutzername>" >&2
  exit 1
fi

if id "$USERNAME" >/dev/null 2>&1; then
  echo "[dialos] Benutzer '$USERNAME' existiert bereits, überspringe Anlage."
else
  echo "[dialos] Lege Standard-Benutzer '$USERNAME' an..."
  adduser --disabled-password --gecos "" "$USERNAME"
fi

usermod -aG sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom "$USERNAME"

# Zufälliges Passwort pro Setup-Lauf, nur für Sudo/Admin-Zwecke relevant -
# der Endnutzer tippt nie etwas (Autologin übernimmt die Anmeldung). Wie
# Sudo für die spätere sprachgesteuerte Wartung final gehandhabt wird, ist
# noch offen, siehe docs/sicherheit-datenschutz.md.
GEN_PASSWORD=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16)
echo "$USERNAME:$GEN_PASSWORD" | chpasswd
echo "[dialos] Generiertes Sudo-Passwort für '$USERNAME': $GEN_PASSWORD"

# --- Autologin umschalten (AccountsService, nicht custom.conf!) ---

find_user_object_path() {
  gdbus call --system --dest org.freedesktop.Accounts \
    --object-path /org/freedesktop/Accounts \
    --method org.freedesktop.Accounts.FindUserByName "$1" \
    | sed -E "s/^\(objectpath '([^']+)',?\)\$/\1/"
}

NUTZER_PATH=$(find_user_object_path "$USERNAME")
echo "[dialos] Aktiviere Autologin für '$USERNAME' ($NUTZER_PATH)..."
gdbus call --system --dest org.freedesktop.Accounts \
  --object-path "$NUTZER_PATH" \
  --method org.freedesktop.Accounts.User.SetAutomaticLogin true

ADMIN_PATH=$(find_user_object_path "$ADMIN_USER")
echo "[dialos] Deaktiviere Autologin für Admin-Konto '$ADMIN_USER' ($ADMIN_PATH)..."
gdbus call --system --dest org.freedesktop.Accounts \
  --object-path "$ADMIN_PATH" \
  --method org.freedesktop.Accounts.User.SetAutomaticLogin false

echo "[dialos] Fertig. Nach einem Neustart sollte '$USERNAME' automatisch"
echo "[dialos] angemeldet werden. '$ADMIN_USER' bleibt als Sudo-Konto ohne"
echo "[dialos] Autologin bestehen (für künftige Fernwartung per RustDesk)."
