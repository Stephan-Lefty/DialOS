#!/bin/bash
# DialOS: Autologin von "nutzer" abhaengig davon umschalten, ob dessen
# verschluesselte Home-Partition erfolgreich entsperrt/gemountet werden
# konnte - siehe docs/sicherheit-datenschutz.md, Abschnitt "Sicherheits-
# Stick als Anwesenheits-Token".
#
# Design (seit 2026-08-14): NICHT mehr die ganze Platte per LUKS
# verschluesselt (das war der urspruengliche initramfs-Ansatz, der beim
# Live-Boot-Test gescheitert ist), sondern nur eine eigene Partition
# "dialos-nutzer-home" (LUKS2, Label ueber "blkid -L dialos-nutzer-home"
# auffindbar), die ausschliesslich /home/nutzer enthaelt. Root ist
# unverschluesselt und bootet immer ganz normal - dieses Skript
# oeffnet/mountet die Home-Partition NACH dem Boot, in der normalen
# Systemumgebung, kein initramfs involviert.
#
# Ablauf:
#   Stick (Label DIALOS-KEY) da UND Home-Partition erfolgreich
#   entsperrt/gemountet -> Autologin fuer nutzer aktivieren.
#   Sonst (Stick fehlt, falscher/beschaedigter Stick, Entschluesselung
#   schlaegt fehl) -> Autologin deaktivieren. GDM zeigt den normalen
#   Login-Bildschirm, auf dem praktisch nur dialosadmin nutzbar ist -
#   nutzers Passwort ist ein zufaelliger, niemandem bekannter String
#   (siehe scripts/dialos-setup-nutzer.sh). dialosadmin selbst bleibt
#   unangetastet (nie Autologin, immer Passwort-Login).
#
# Laeuft als systemd-oneshot-Dienst (dialos-stick-gate.service) VOR
# display-manager.service, also bei jedem Boot neu ausgewertet. Wird
# auch direkt (ausserhalb eines Boots) von scripts/dialos-setup-
# nutzer.sh aufgerufen, um vor dem Anlegen des Kontos sicherzustellen,
# dass die Home-Partition schon gemountet ist.
#
# Wichtig: Der eigentliche Autologin-Schalter ist NICHT
# /etc/gdm3/custom.conf (wird von GDM 48 auf Debian 13 ignoriert,
# gefunden 2026-08-11, siehe scripts/dialos-setup-nutzer.sh), sondern die
# Pro-Benutzer-Eigenschaft org.freedesktop.Accounts.User.AutomaticLogin
# im AccountsService-Dienst, gesetzt per gdbus - exakt derselbe
# Mechanismus wie in scripts/dialos-setup-nutzer.sh.
set -uo pipefail

STICK_LABEL="DIALOS-KEY"
KEYFILE_NAME=".dialos-key"
HOME_LUKS_LABEL="dialos-nutzer-home"
HOME_LUKS_NAME="dialos-nutzer-home"
HOME_MOUNT="/home/nutzer"
USERNAME="nutzer"
MAX_WAIT=8   # Sekunden Wiederholpruefung - USB-Erkennung beim Boot kann kurz nachhinken
STICK_MNT="/run/dialos-stick-gate"

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
  blkid -L "$STICK_LABEL" >/dev/null 2>&1
}

# Versucht, nutzers verschluesselte Home-Partition zu entsperren und zu
# mounten. Gibt 0 zurueck, wenn sie danach (oder schon vorher) gemountet
# ist, 1 bei jedem Fehlschlag (kein Stick, falscher Schluessel, Home-
# Partition fehlt/beschaedigt).
ensure_home_mounted() {
  if mountpoint -q "$HOME_MOUNT"; then
    return 0
  fi

  KEY_PART=$(blkid -L "$STICK_LABEL" 2>/dev/null)
  [ -n "$KEY_PART" ] || return 1

  HOME_PART=$(blkid -L "$HOME_LUKS_LABEL" 2>/dev/null)
  if [ -z "$HOME_PART" ]; then
    log "Keine Partition mit Label '$HOME_LUKS_LABEL' auf der internen Platte gefunden."
    return 1
  fi

  mkdir -p "$STICK_MNT"
  if ! mount -o ro "$KEY_PART" "$STICK_MNT" 2>/dev/null; then
    return 1
  fi
  KEYFILE="$STICK_MNT/$KEYFILE_NAME"
  if [ ! -f "$KEYFILE" ]; then
    umount "$STICK_MNT" 2>/dev/null || true
    log "Schlüsseldatei '$KEYFILE_NAME' fehlt auf dem Stick."
    return 1
  fi

  if [ ! -e "/dev/mapper/$HOME_LUKS_NAME" ]; then
    if ! cryptsetup open --key-file="$KEYFILE" "$HOME_PART" "$HOME_LUKS_NAME" 2>/tmp/dialos-stick-gate-crypt-out; then
      umount "$STICK_MNT" 2>/dev/null || true
      log "cryptsetup open fehlgeschlagen: $(cat /tmp/dialos-stick-gate-crypt-out 2>/dev/null)"
      return 1
    fi
  fi
  umount "$STICK_MNT" 2>/dev/null || true

  # fstab enthaelt einen noauto-Eintrag fuer /dev/mapper/$HOME_LUKS_NAME
  # -> "mount $HOME_MOUNT" reicht normalerweise; expliziter Fallback
  # falls der fstab-Eintrag mal fehlt.
  if mount "$HOME_MOUNT" 2>/dev/null; then
    return 0
  fi
  mount "/dev/mapper/$HOME_LUKS_NAME" "$HOME_MOUNT" 2>/dev/null || return 1
  return 0
}

i=0
STICK_FOUND=0
while [ "$i" -lt "$MAX_WAIT" ]; do
  if stick_present; then
    STICK_FOUND=1
    break
  fi
  i=$((i + 1))
  sleep 1
done

HOME_OK=0
if [ "$STICK_FOUND" -eq 1 ]; then
  if ensure_home_mounted; then
    HOME_OK=1
    log "Sicherheits-Stick gefunden, Home-Partition gemountet."
  else
    log "Sicherheits-Stick gefunden, aber Home-Partition konnte nicht entsperrt/gemountet werden."
  fi
else
  log "Kein Sicherheits-Stick gefunden."
fi

NUTZER_PATH=$(find_user_object_path "$USERNAME")
if [ -z "$NUTZER_PATH" ]; then
  log "Benutzer '$USERNAME' nicht gefunden (AccountsService noch nicht bereit oder Konto fehlt), überspringe Autologin-Umschaltung."
  exit 0
fi

if [ "$HOME_OK" -eq 1 ]; then
  log "Aktiviere Autologin für '$USERNAME'."
  set_automatic_login "$NUTZER_PATH" true
else
  log "Deaktiviere Autologin für '$USERNAME'."
  set_automatic_login "$NUTZER_PATH" false
fi
