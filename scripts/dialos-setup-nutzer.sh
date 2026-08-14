#!/bin/sh
# DialOS: Standard-Benutzer "nutzer" auf einem bereits eingerichteten,
# echten System anlegen und Autologin von einem Admin-Konto (im
# Buero-Setup kuenftig "DialOS-Admin") auf "nutzer" umschalten.
#
# WICHTIG: Dieses Skript gehoert zur "neuen" Vorgehensweise (Debian 13 +
# GNOME direkt auf echter Hardware einrichten, siehe CLAUDE.md), NICHT
# zur alten Docker/Chroot-live-build-Pipeline in iso-build/. Der
# Autologin-Teil braucht einen laufenden D-Bus + AccountsService-Dienst,
# das gibt es in einer Chroot-Build-Umgebung nicht.
#
# Fuehre dieses Skript als LETZTEN Schritt des Buero-Setups aus, nachdem
# Pakete, Branding, RustDesk, Claude Code CLI installiert und das
# Plymouth-Theme aktiviert sind (siehe CLAUDE.md "Naechste konkrete
# Schritte").
#
# Hintergrund zum Autologin-Mechanismus: Der eigentliche Schalter ist
# NICHT /etc/gdm3/custom.conf (das wird von GDM in dieser Debian-13/
# GDM-48-Kombination fuer die Benutzerauswahl offenbar ignoriert),
# sondern eine Pro-Benutzer-Eigenschaft direkt im AccountsService-Dienst
# (org.freedesktop.Accounts.User.AutomaticLogin, per D-Bus gesetzt).
# Volle Debugging-Historie dazu in CLAUDE.md, Abschnitt
# "GELOEST: GDM-Autologin".
#
# Nutzung: sudo ./dialos-setup-nutzer.sh [admin-benutzername]
#   admin-benutzername ist das Buero-Setup-Konto, dessen Autologin
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

# --- Sicherstellen, dass nutzers verschluesselte Home-Partition schon
# gemountet ist, BEVOR das Konto angelegt wird. Sonst wuerde "adduser"
# /home/nutzer samt Skel-Dateien auf der unverschluesselten root-
# Partition anlegen - beim naechsten Boot mit Stick wuerde die (dann
# leere) verschluesselte Partition das wieder verdecken
# (Konfigurationsverlust), bei einem Boot ohne Stick waeren diese Daten
# ungeschuetzt sichtbar (Datenleck). Siehe docs/sicherheit-
# datenschutz.md, Abschnitt "Sicherheits-Stick als Anwesenheits-Token".
if ! id "$USERNAME" >/dev/null 2>&1; then
  if [ -x /usr/local/sbin/dialos-stick-gate.sh ]; then
    /usr/local/sbin/dialos-stick-gate.sh || true
  fi
  if ! mountpoint -q "/home/$USERNAME"; then
    echo "[dialos] Abbruch: /home/$USERNAME ist nicht gemountet." >&2
    echo "[dialos] Sicherheits-Stick einstecken und erneut versuchen - sonst" >&2
    echo "[dialos] würde '$USERNAME's Home auf der UNVERSCHLÜSSELTEN Platte" >&2
    echo "[dialos] angelegt werden." >&2
    exit 1
  fi
fi

if id "$USERNAME" >/dev/null 2>&1; then
  echo "[dialos] Benutzer '$USERNAME' existiert bereits, ueberspringe Anlage."
else
  echo "[dialos] Lege Standard-Benutzer '$USERNAME' an..."
  adduser --disabled-password --gecos "" "$USERNAME"
fi
usermod -aG sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom "$USERNAME"
# Zufaelliges Passwort pro Setup-Lauf, nur fuer Sudo/Admin-Zwecke relevant -
# der Endnutzer tippt nie etwas (Autologin uebernimmt die Anmeldung).
GEN_PASSWORD=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16)
echo "$USERNAME:$GEN_PASSWORD" | chpasswd
echo "[dialos] Generiertes Sudo-Passwort fuer '$USERNAME': $GEN_PASSWORD"

# --- Autologin umschalten (AccountsService, nicht custom.conf!) ---
find_user_object_path() {
  gdbus call --system --dest org.freedesktop.Accounts \
    --object-path /org/freedesktop/Accounts \
    --method org.freedesktop.Accounts.FindUserByName "$1" \
    | sed -E "s/^\(objectpath '([^']+)',?\)\$/\1/"
}

set_automatic_login() {
  # Direkt nach chpasswd braucht AccountsService manchmal ein paar
  # Sekunden, um die neue Passwort-Zeile zu bemerken - erster Versuch
  # kann mit "user is locked" fehlschlagen, obwohl das Passwort schon
  # gesetzt ist. Deshalb hier bis zu 5x mit kurzer Pause wiederholen
  # (gefunden und geloest 2026-08-11).
  path="$1"; value="$2"; i=0
  while [ $i -lt 5 ]; do
    if gdbus call --system --dest org.freedesktop.Accounts \
        --object-path "$path" \
        --method org.freedesktop.Accounts.User.SetAutomaticLogin "$value" >/tmp/dialos-autologin-out 2>&1; then
      return 0
    fi
    i=$((i + 1))
    sleep 2
  done
  cat /tmp/dialos-autologin-out >&2
  return 1
}

NUTZER_PATH=$(find_user_object_path "$USERNAME")
echo "[dialos] Aktiviere Autologin fuer '$USERNAME' ($NUTZER_PATH)..."
set_automatic_login "$NUTZER_PATH" true

ADMIN_PATH=$(find_user_object_path "$ADMIN_USER")
echo "[dialos] Deaktiviere Autologin fuer Admin-Konto '$ADMIN_USER' ($ADMIN_PATH)..."
set_automatic_login "$ADMIN_PATH" false

echo "[dialos] Fertig. Nach einem Neustart sollte '$USERNAME' automatisch"
echo "[dialos] angemeldet werden. '$ADMIN_USER' bleibt als Sudo-Konto ohne"
echo "[dialos] Autologin bestehen (fuer kuenftige Fernwartung per RustDesk)."
