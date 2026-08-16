#!/bin/bash
# DialOS: richtet auf einem BEREITS installierten System (z. B. frisch
# per Debian-Installer/Calamares aufgesetzt, siehe docs/Debian-zu-
# DialOS.md Schritt 1) nachträglich die verschlüsselte
# "dialos-nutzer-home"-Partition + den Sicherheits-Stick ein - die
# gleiche LUKS/Stick-Logik wie in dialos-install, aber OHNE dessen
# Ganze-Platte-Wipe + rsync-Systemkopie (die braucht es hier nicht, das
# System läuft ja schon).
#
# Voraussetzung: Bei der Basis-Installation muss am Ende der System-
# Platte bewusst FREIER, UNPARTITIONIERTER Platz gelassen worden sein
# (siehe docs/Debian-zu-DialOS.md, Schritt 1) - dieses Werkzeug nutzt
# genau diesen freien Platz, es verkleinert/verschiebt keine
# bestehenden Partitionen.
#
# Sinnvolle Reihenfolge im Gesamtablauf: NACH
# scripts/dialos-full-office-setup.sh (das installiert u. a.
# dialos-stick-gate.sh/.service, die hier am Ende direkt aufgerufen
# werden, damit die Partition ohne Neustart sofort nutzbar ist), VOR
# scripts/dialos-buero-setup-abschliessen.sh (das braucht die
# gemountete Home-Partition, siehe docs/sicherheit-datenschutz.md).
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  # Siehe dialos-install fuer die Begruendung von pkexec + env-Weiterreichung
  # (sonst kein D-Bus fuer den Datei-Speichern-Dialog des Schluessel-Backups).
  exec pkexec env DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" \
    DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
    XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" "$0" "$@"
fi

LABEL="DIALOS-KEY"
DATA_LABEL="DIALOS-DATA"
KEYFILE_NAME=".dialos-key"
HOME_LUKS_NAME="dialos-nutzer-home"
HOME_LUKS_LABEL="dialos-nutzer-home"
MIN_FREE_MIB=20000   # ~20 GiB Mindestgroesse fuer die Home-Partition

say() { zenity --info --width=400 --title="DialOS Home-Partition" --text="$1" 2>/dev/null || echo "$1"; }
warn() { zenity --warning --width=400 --title="DialOS Home-Partition" --text="$1" 2>/dev/null || echo "$1" >&2; }
die() { zenity --error --width=400 --title="DialOS Home-Partition" --text="$1" 2>/dev/null || echo "$1" >&2; exit 1; }
ask_password() { zenity --password --title="$1" 2>/dev/null; }

echo "== DialOS: Home-Partition + Sicherheits-Stick einrichten =="

# --- 1. Finde die System-Platte (die, auf der / liegt) und den freien
#          Platz danach ---
ROOT_SRC=$(findmnt -no SOURCE / || true)
[ -n "$ROOT_SRC" ] || die "Konnte die Root-Partition nicht ermitteln."
ROOT_DISK_NAME=$(lsblk -no PKNAME "$ROOT_SRC" 2>/dev/null || true)
[ -n "$ROOT_DISK_NAME" ] || die "Konnte die System-Platte nicht ermitteln."
SYS_DISK="/dev/$ROOT_DISK_NAME"

FREE_START_MIB=$(parted -s "$SYS_DISK" unit MiB print free 2>/dev/null \
  | grep "Free Space" | tail -1 | awk '{print $1}' | sed 's/MiB$//')
FREE_END_MIB=$(parted -s "$SYS_DISK" unit MiB print free 2>/dev/null \
  | grep "Free Space" | tail -1 | awk '{print $2}' | sed 's/MiB$//')

if [ -z "${FREE_START_MIB:-}" ] || [ -z "${FREE_END_MIB:-}" ]; then
  die "Kein freier Platz auf $SYS_DISK gefunden. Wurde bei der Basis-Installation (Schritt 1) genug Platz nach der root-Partition frei/unpartitioniert gelassen?"
fi

FREE_SIZE_MIB=$(awk -v s="$FREE_START_MIB" -v e="$FREE_END_MIB" 'BEGIN{printf "%d", e-s}')
if [ "$FREE_SIZE_MIB" -lt "$MIN_FREE_MIB" ]; then
  die "Nur ${FREE_SIZE_MIB} MiB freier Platz auf $SYS_DISK gefunden (mind. ${MIN_FREE_MIB} MiB nötig). Basis-Installation hat vermutlich zu wenig Platz frei gelassen."
fi

say "Freier Platz gefunden auf $SYS_DISK: ${FREE_SIZE_MIB} MiB (ab ${FREE_START_MIB} MiB). Dort wird die verschlüsselte nutzer-Partition angelegt - bestehende Partitionen bleiben unangetastet."

# --- 2. Sicherheits-Stick waehlen (System-Platte automatisch ausgeschlossen) ---
mapfile -t USB_ROWS < <(lsblk -dnb -o NAME,SIZE,TRAN | awk -v skip="$ROOT_DISK_NAME" '$1 != skip && $3=="usb"')
USB_ARGS=()
for row in "${USB_ROWS[@]}"; do
  name=$(echo "$row" | awk '{print $1}')
  size=$(echo "$row" | awk '{print $2}')
  sizeh=$(numfmt --to=iec --suffix=B "$size" 2>/dev/null || echo "$size")
  USB_ARGS+=("/dev/$name" "$sizeh")
done

if [ "${#USB_ARGS[@]}" -eq 0 ]; then
  die "Kein USB-Stick gefunden. Sicherheits-Stick anschließen und erneut versuchen."
fi

KEY_STICK=$(zenity --list --title="Sicherheits-Stick wählen" \
  --text="Auf diesem Stick werden der Entschlüsselungs-Schlüssel für nutzers Daten (2 GiB) und ein Datenspeicher-Bereich (Rest der Kapazität) angelegt.\nDer Stick wird dabei komplett neu formatiert." \
  --column="Gerät" --column="Größe" --width=500 --height=250 \
  "${USB_ARGS[@]}")
[ -n "$KEY_STICK" ] || die "Abgebrochen: kein Sicherheits-Stick gewählt."

KEY_STICK_SIZE=$(lsblk -dnb -o SIZE "$KEY_STICK" 2>/dev/null || echo 0)
if [ "$KEY_STICK_SIZE" -lt 2684354560 ]; then
  die "Der gewählte Stick ist zu klein (mind. ~2,5 GB nötig für Schlüssel- + Datenpartition)."
fi

# --- 3. Recovery-Passphrase ---
say "Zusätzlich zum Stick wird ein Wiederherstellungs-Passwort als zweiter LUKS-Schlüssel für nutzers Daten-Partition angelegt (Notfall, falls der Stick verloren geht). Bitte sicher verwahren, NICHT dem Endnutzer geben. Mindestens 12 Zeichen."
RECOVERY_PASS=""
while [ -z "$RECOVERY_PASS" ] || [ "${#RECOVERY_PASS}" -lt 12 ]; do
  RECOVERY_PASS=$(ask_password "Wiederherstellungs-Passwort festlegen (mind. 12 Zeichen)")
  if [ -z "$RECOVERY_PASS" ]; then
    warn "Passwort darf nicht leer sein."
  elif [ "${#RECOVERY_PASS}" -lt 12 ]; then
    warn "Passwort ist zu kurz (mind. 12 Zeichen)."
    RECOVERY_PASS=""
  fi
done

# --- 4. Bestaetigung ---
CONFIRM=$(zenity --entry --title="Bestätigung" \
  --text="Auf $SYS_DISK wird im freien Platz (ab ${FREE_START_MIB} MiB) eine neue verschlüsselte Partition angelegt, Stick $KEY_STICK wird KOMPLETT GELÖSCHT.\nZum Bestätigen \"LOESCHEN\" eingeben:" 2>/dev/null || true)
[ "$CONFIRM" = "LOESCHEN" ] || die "Abgebrochen: Bestätigung nicht erhalten."

echo "Lege dialos-nutzer-home auf $SYS_DISK an, Schlüssel-Stick $KEY_STICK ..."

# --- 5. Neue Partition im freien Platz anlegen ---
parted -s "$SYS_DISK" mkpart dialos-nutzer-home "${FREE_START_MIB}MiB" "${FREE_END_MIB}MiB"
partprobe "$SYS_DISK"
sleep 2

NEW_PART_NUM=$(parted -s "$SYS_DISK" print | awk '/^ [0-9]/{n=$1} END{print n}')
if [[ "$SYS_DISK" == *nvme* ]]; then
  HOME_PART="${SYS_DISK}p${NEW_PART_NUM}"
else
  HOME_PART="${SYS_DISK}${NEW_PART_NUM}"
fi
[ -b "$HOME_PART" ] || die "Neue Partition $HOME_PART wurde nicht gefunden - Abbruch vor jeder Formatierung."

# --- 6. Stick vorbereiten: DIALOS-KEY (2 GiB, ext4, bewusst NICHT
#          Windows-lesbar) + DIALOS-DATA (Rest, exFAT, Windows/macOS/
#          Linux-lesbar) - identisch zu dialos-install ---
umount "${KEY_STICK}"* 2>/dev/null || true
wipefs -af "$KEY_STICK"
parted -s "$KEY_STICK" mklabel gpt
parted -s "$KEY_STICK" mkpart "$LABEL" ext4 1MiB 2049MiB
parted -s "$KEY_STICK" mkpart "$DATA_LABEL" fat32 2049MiB 100%
partprobe "$KEY_STICK"
sleep 2
KEY_STICK_PART="${KEY_STICK}1"
DATA_PART="${KEY_STICK}2"
mkfs.ext4 -F -L "$LABEL" "$KEY_STICK_PART"
mkfs.exfat -L "$DATA_LABEL" "$DATA_PART"

mkdir -p /run/dialos-key-write
mount "$KEY_STICK_PART" /run/dialos-key-write
KEYFILE="/run/dialos-key-write/$KEYFILE_NAME"
head -c 512 /dev/urandom > "$KEYFILE"
chmod 600 "$KEYFILE"
sync

# --- 7. LUKS-Setup: Keyfile als Hauptschluessel, Recovery-Passphrase
#          als zweiter Slot ---
cryptsetup luksFormat --type luks2 --label "$HOME_LUKS_LABEL" --batch-mode "$HOME_PART" "$KEYFILE"
printf '%s' "$RECOVERY_PASS" > /tmp/.rp
cryptsetup luksAddKey --batch-mode --key-file="$KEYFILE" "$HOME_PART" /tmp/.rp
shred -u /tmp/.rp

# --- 7b. Verschluesseltes Offsite-Backup des Keyfiles (Nextcloud) -
#          separates, zufaellig erzeugtes Backup-Passwort, NICHT die
#          Recovery-Passphrase (Begruendung: siehe dialos-install). ---
BACKUP_LABEL=$(zenity --entry --title="Schlüssel-Backup" \
  --text="Kennzeichnung für dieses Backup (z. B. Kundenname/Kürzel):" \
  --entry-text="dialos-$(date +%Y%m%d)" 2>/dev/null || echo "dialos-$(date +%Y%m%d-%H%M%S)")
BACKUP_PASS=$(openssl rand -base64 32)
BACKUP_TMP="/tmp/${BACKUP_LABEL}.key.enc"
BACKUP_PASS_FILE=$(mktemp)
printf '%s' "$BACKUP_PASS" > "$BACKUP_PASS_FILE"
openssl enc -aes-256-cbc -pbkdf2 -salt -in "$KEYFILE" -out "$BACKUP_TMP" -pass "file:$BACKUP_PASS_FILE"
shred -u "$BACKUP_PASS_FILE"
SAVE_TO_ERR=$(mktemp)
SAVE_TO=$(zenity --file-selection --save --confirm-overwrite \
  --title="Verschlüsseltes Schlüssel-Backup speichern (z. B. im Nextcloud-Sync-Ordner)" \
  --filename="$HOME/${BACKUP_LABEL}.key.enc" 2>"$SAVE_TO_ERR" || true)
ZENITY_ERR=$(cat "$SAVE_TO_ERR" 2>/dev/null || true)
rm -f "$SAVE_TO_ERR"
if [ -n "$SAVE_TO" ]; then
  cp "$BACKUP_TMP" "$SAVE_TO"
  say "Backup gespeichert unter: $SAVE_TO\nFalls der Ordner nicht automatisch synchronisiert wird, manuell in die Nextcloud hochladen.\n\nBACKUP-PASSWORT (getrennt von der Nextcloud aufbewahren, z. B. im eigenen Passwort-Manager - NIEMALS zusammen mit der Backup-Datei!):\n$BACKUP_PASS\n\nEntschlüsselung später: openssl enc -d -aes-256-cbc -pbkdf2 -in $BACKUP_LABEL.key.enc -out neuer-stick.key"
else
  warn "Kein Speicherort gewählt - Schlüssel-Backup wurde NICHT gesichert.${ZENITY_ERR:+ Fehlermeldung: $ZENITY_ERR}"
fi
shred -u "$BACKUP_TMP" 2>/dev/null || rm -f "$BACKUP_TMP"

# --- 7c. Partition kurz oeffnen, leer mit ext4 formatieren, wieder
#          schliessen ---
cryptsetup open --key-file="$KEYFILE" "$HOME_PART" "$HOME_LUKS_NAME"
mkfs.ext4 -F -L dialos-nutzer-home "/dev/mapper/$HOME_LUKS_NAME"
cryptsetup close "$HOME_LUKS_NAME"

umount /run/dialos-key-write

# --- 8. fstab-Eintrag + Mountpoint auf dem LAUFENDEN System (nicht
#          $TARGET_MNT wie bei dialos-install - hier gibt es kein
#          chroot-Ziel, das System läuft schon) ---
FSTAB_LINE="/dev/mapper/$HOME_LUKS_NAME /home/nutzer ext4 noauto,nofail 0 2"
if ! grep -qF "/dev/mapper/$HOME_LUKS_NAME" /etc/fstab; then
  echo "$FSTAB_LINE" >> /etc/fstab
fi
mkdir -p /home/nutzer

# --- 9. Sofort mounten (falls dialos-stick-gate.sh schon installiert
#          ist, siehe scripts/dialos-full-office-setup.sh Schritt 12) -
#          damit die Partition ohne Neustart nutzbar ist. ---
if [ -x /usr/local/sbin/dialos-stick-gate.sh ]; then
  /usr/local/sbin/dialos-stick-gate.sh || true
else
  mount /home/nutzer || warn "Konnte /home/nutzer nicht sofort mounten - dialos-stick-gate.sh ist noch nicht installiert (siehe Schritt 12 in scripts/dialos-full-office-setup.sh). Nach dessen Installation erneut versuchen oder neu starten."
fi

say "Fertig. dialos-nutzer-home ist eingerichtet. Sicherheits-Stick sollte jetzt eingesteckt bleiben, bis scripts/dialos-buero-setup-abschliessen.sh gelaufen ist (braucht die gemountete Partition)."
