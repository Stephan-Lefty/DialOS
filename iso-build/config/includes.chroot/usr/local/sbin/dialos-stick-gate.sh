#!/bin/bash
# DialOS: Autologin von "nutzer" abhaengig davon umschalten, ob der
# Sicherheits-Stick (Partition mit Label DIALOS-KEY) beim Boot gefunden
# wird - rein als Anwesenheits-Pruefung, OHNE Festplattenverschluesselung
# (siehe docs/sicherheit-datenschutz.md, Abschnitt "Sicherheits-Stick als
# Anwesenheits-Token"). Ergaenzt die bestehende LUKS-Stick-Verschluesselung
# aus dialos-install/dialos-keyscript, ersetzt sie (noch) nicht - siehe
# TODO.md fuer die offene Frage, ob LUKS langfristig entfaellt.
#
# Steckt der Stick: nutzer wird wie gewohnt automatisch angemeldet.
# Fehlt er: Autologin fuer nutzer wird deaktiviert, GDM zeigt den
# normalen Login-Bildschirm. Dort ist praktisch nur dialosadmin nutzbar -
# nutzers Passwort ist ein zufaelliger, niemandem bekannter String (siehe
# scripts/dialos-setup-nutzer.sh). dialosadmin selbst bleibt unangetastet
# (nie Autologin, immer Passwort-Login).
#
# Laeuft als systemd-oneshot-Dienst (dialos-stick-gate.service) VOR
# display-manager.service, also bei jedem Boot neu ausgewertet.
#
# Wichtig: Der eigentliche Autologin-Schalter ist NICHT
# /etc/gdm3/custom.conf (wird von GDM 48 auf Debian 13 ignoriert,
# gefunden 2026-08-11, siehe scripts/dialos-setup-nutzer.sh), sondern die
# Pro-Benutzer-Eigenschaft org.freedesktop.Accounts.User.AutomaticLogin
# im AccountsService-Dienst, gesetzt per gdbus - exakt derselbe
# Mechanismus wie in scripts/dialos-setup-nutzer.sh.
set -uo pipefail

LABEL="DIALOS-KEY"
USERNAME="nutzer"
MAX_WAIT=8   # Sekunden Wiederholpruefung - USB-Erkennung beim Boot kann kurz nachhinken

log() { echo "[dialos-stick-gate] $1"; }

find_user_object_path() {
  gdbus call --system --dest org.freedesktop.Accounts \
    --object-path /org/freedesktop/Accounts \
    --method org.freedesktop.Accounts.FindUserByName "$1" 2>/dev/null \
    | sed -E "s/^\(objectpath '([^']+)',?\)\$/\1/"
}

set_automatic_login() {
  path="$1"; value="$2"; i=0
  while [ "$i" -lt 5 ]; do
    if gdbus call --system --dest org.freedesktop.Accounts \
        --object-path "$path" \
        --method org.freedesktop.Accounts.User.SetAutomaticLogin "$value" \
        >/tmp/dialos-stick-gate-out 2>&1; then
      return 0
    fi
    i=$((i + 1))
    sleep 1
  done
  cat /tmp/dialos-stick-gate-out >&2
  return 1
}

stick_present() {
  udevadm settle --timeout=2 >/dev/null 2>&1 || true
  blkid -L "$LABEL" >/dev/null 2>&1
}

i=0
FOUND=0
while [ "$i" -lt "$MAX_WAIT" ]; do
  if stick_present; then
    FOUND=1
    break
  fi
  i=$((i + 1))
  sleep 1
done

NUTZER_PATH=$(find_user_object_path "$USERNAME")
if [ -z "$NUTZER_PATH" ]; then
  log "Benutzer '$USERNAME' nicht gefunden (AccountsService noch nicht bereit oder Konto fehlt), ueberspringe."
  exit 0
fi

if [ "$FOUND" -eq 1 ]; then
  log "Sicherheits-Stick gefunden, aktiviere Autologin fuer '$USERNAME'."
  set_automatic_login "$NUTZER_PATH" true
else
  log "Kein Sicherheits-Stick gefunden, deaktiviere Autologin fuer '$USERNAME'."
  set_automatic_login "$NUTZER_PATH" false
fi
