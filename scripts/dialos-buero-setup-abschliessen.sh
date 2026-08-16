#!/bin/sh
# DialOS: Kompletter Buero-Setup-Abschluss nach einer frischen
# Installation - fasst mehrere Einzelschritte in einem Klick zusammen:
# 1. Avatar fuer das Admin-Konto setzen
# 2. Admin-Werkzeuge auf dialosadmins Arbeitsflaeche bereitstellen
# 3. "nutzer"-Konto anlegen + Autologin umschalten
# 4. Firefox-Startseite pruefen (sollte automatisch aus der ISO kommen)
#
# Schritt 2 war bis 2026-08-16 reine Handarbeit aus der Doku (Schritt 13 in
# docs/Debian-zu-DialOS.md) und damit die einzige Luecke, die den Aufbau
# davon abhielt, komplett aus Skripten zu bestehen - jetzt hier mit drin.
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
ADMIN_HOME=$(getent passwd "$ADMIN_USER" | cut -d: -f6)
if [ -z "$ADMIN_HOME" ] || [ ! -d "$ADMIN_HOME" ]; then
  echo "[dialos] Home-Verzeichnis von '$ADMIN_USER' nicht gefunden." >&2
  exit 1
fi

echo "=== [dialos] Schritt 1/4: Avatar setzen ==="
"$SCRIPT_DIR/dialos-set-avatar.sh" "$ADMIN_USER"

echo ""
echo "=== [dialos] Schritt 2/4: Admin-Werkzeuge auf die Arbeitsflaeche ==="
# WICHTIG: bewusst direkt auf das schon existierende Admin-Konto, NICHT
# ueber /etc/skel/Desktop/ - /etc/skel wirkt nur auf kuenftig angelegte
# Konten, und das ist in diesem Rezept ausschliesslich "nutzer". Ueber skel
# landeten die Admin-Werkzeuge also ausgerechnet auf dem Konto, das sie nie
# sehen soll (Korrektur vom 2026-08-14, siehe scripts/README.md).
DESKTOP_DIR="$ADMIN_HOME/Desktop"
mkdir -p "$DESKTOP_DIR"

# Nur kopieren, wenn das Skript NICHT schon von der Arbeitsflaeche selbst
# laeuft - sonst kopierten die Dateien auf sich selbst.
if [ "$SCRIPT_DIR" != "$DESKTOP_DIR" ]; then
  cp "$SCRIPT_DIR"/*.sh "$DESKTOP_DIR/"
  echo "[dialos] Setup-Skripte nach $DESKTOP_DIR kopiert."
else
  echo "[dialos] Skripte liegen bereits auf der Arbeitsflaeche - nichts zu kopieren."
fi
chmod 755 "$DESKTOP_DIR"/*.sh

# Frueher lag hier ein Startsymbol fuer dialos-install. Das Werkzeug ist
# am 2026-08-16 entfallen (Weg A: jedes Geraet entsteht im Buero aus der
# Debian-ISO plus den drei Skripten, es gibt keinen Live-Boot-Installer
# mehr). Ein evtl. noch vorhandenes Symbol einer aelteren Version wird
# hier entfernt, damit es nicht ins Leere zeigt.
rm -f "$DESKTOP_DIR/dialos-install.desktop"

# Claude-Desktop-App: wird bei jedem Buero-Setup frisch geladen, bewusst
# nicht ins Repo committet. Darf den Lauf nicht abbrechen, falls das Paket
# gerade nicht verfuegbar ist - deshalb Fehler abgefangen.
if (cd /tmp && apt-get download claude-desktop >/dev/null 2>&1); then
  cp /tmp/claude-desktop*.deb "$DESKTOP_DIR/" 2>/dev/null || true
  chmod 644 "$DESKTOP_DIR"/claude-desktop*.deb 2>/dev/null || true
  rm -f /tmp/claude-desktop*.deb
  echo "[dialos] Claude-Desktop-App auf der Arbeitsflaeche abgelegt."
else
  echo "[dialos] Hinweis: 'claude-desktop' konnte nicht geladen werden (nicht in den Paketquellen?) - uebersprungen."
fi

# Alles auf der Arbeitsflaeche muss dem Admin-Konto gehoeren, sonst kann es
# die Dateien als normaler Benutzer nicht starten.
chown -R "$ADMIN_USER":"$ADMIN_USER" "$DESKTOP_DIR"

# Ohne "metadata::trusted" zeigt Nautilus beim ersten Doppelklick eine
# "nicht vertrauenswuerdig"-Warnung, statt das Programm zu starten. Das
# Merkmal liegt in der Metadaten-Ablage des BENUTZERS - deshalb als
# ADMIN_USER ausfuehren, nicht als root. Betrifft seit dem Wegfall von
# dialos-install nur noch dialos-rekey (Ersatz fuer einen verlorenen
# Sicherheits-Stick).
REKEY_DESKTOP="/usr/share/applications/dialos-rekey.desktop"
if [ -f "$REKEY_DESKTOP" ]; then
  cp "$REKEY_DESKTOP" "$DESKTOP_DIR/"
  chmod 755 "$DESKTOP_DIR/dialos-rekey.desktop"
  chown "$ADMIN_USER":"$ADMIN_USER" "$DESKTOP_DIR/dialos-rekey.desktop"
  echo "[dialos] Startsymbol fuer dialos-rekey abgelegt."
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "$ADMIN_USER" -- gio set "$DESKTOP_DIR/dialos-rekey.desktop" metadata::trusted true 2>/dev/null \
      || echo "[dialos] Hinweis: 'gio set metadata::trusted' ging nicht (keine laufende Sitzung von '$ADMIN_USER'?) - beim ersten Doppelklick ggf. einmal 'Vertrauen und starten' bestaetigen."
  fi
else
  echo "[dialos] WARNUNG: $REKEY_DESKTOP fehlt - lief Schritt 12 (Sicherheits-Werkzeuge) durch?" >&2
fi

echo ""
echo "=== [dialos] Schritt 3/4: Nutzer-Konto + Autologin ==="
"$SCRIPT_DIR/dialos-setup-nutzer.sh" "$ADMIN_USER"

echo ""
echo "=== [dialos] Schritt 4/4: Firefox-Startseite pruefen ==="
POLICY_FILE="/usr/lib/firefox-esr/distribution/policies.json"
if [ -f "$POLICY_FILE" ] && grep -q "dialos.org" "$POLICY_FILE"; then
  echo "[dialos] Firefox-Startseite ist korrekt gesetzt (automatisch aus der ISO)."
else
  echo "[dialos] WARNUNG: Firefox-Startseiten-Policy fehlt oder ist falsch!" >&2
  echo "[dialos]          Erwartet unter: $POLICY_FILE" >&2
fi

echo ""
echo "=== [dialos] Alles erledigt. Bitte einmal neu starten. ==="
