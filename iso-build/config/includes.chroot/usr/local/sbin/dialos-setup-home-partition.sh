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
# ext4 erlaubt hoechstens 16 Zeichen Label - "dialos-nutzer-home" (18) wuerde
# von mkfs.ext4 mit einer Warnung stumm auf "dialos-nutzer-ho" gekuerzt.
# Zum Auffinden der Partition zaehlt ohnehin nur das LUKS2-Label
# (HOME_LUKS_LABEL, bis 48 Byte), das dialos-stick-gate.sh per "blkid -L"
# sucht; dieses Label hier ist nur INNERHALB des geoeffneten Containers
# sichtbar. Deshalb bewusst kurz und ohne Kuerzungswarnung.
HOME_FS_LABEL="dialos-nutzer"
MIN_FREE_MIB=20000   # ~20 GiB Mindestgroesse fuer die Home-Partition

# Das Skript laeuft ab hier immer als root (per pkexec oben oder per sudo).
# "$HOME" waere dann /root - fuer den Speichern-Dialog des Schluessel-Backups
# ist aber das Home des AUFRUFENDEN Kontos gemeint (dort liegt der
# Nextcloud-Sync-Ordner). Deshalb dessen UID/Home explizit aufloesen.
AUFRUF_UID="${PKEXEC_UID:-${SUDO_UID:-}}"
if [ -n "$AUFRUF_UID" ] && getent passwd "$AUFRUF_UID" >/dev/null 2>&1; then
  AUFRUF_USER=$(getent passwd "$AUFRUF_UID" | cut -d: -f1)
  AUFRUF_HOME=$(getent passwd "$AUFRUF_UID" | cut -d: -f6)
else
  AUFRUF_USER="root"
  AUFRUF_HOME="${HOME:-/root}"
fi

say() { zenity --info --width=400 --title="DialOS Home-Partition" --text="$1" 2>/dev/null || echo "$1"; }
warn() { zenity --warning --width=400 --title="DialOS Home-Partition" --text="$1" 2>/dev/null || echo "$1" >&2; }
die() { zenity --error --width=400 --title="DialOS Home-Partition" --text="$1" 2>/dev/null || echo "$1" >&2; exit 1; }

# Faellt auf eine Terminal-Eingabe zurueck, wenn zenity nicht laufen kann -
# z. B. wenn das Skript per "sudo" von einer Textkonsole/SSH gestartet wurde
# (sudo streicht DISPLAY/XAUTHORITY per env_reset, und der pkexec-Zweig oben
# greift dann nicht, weil man ja schon root ist). Frueher hatte nur diese
# eine Funktion KEINEN Fallback: das Skript beendete sich an dieser Stelle
# wortlos, weil "VAR=$(zenity ...)" unter "set -e" den ganzen Lauf abbricht.
ask_password() {
  local p=""
  if [ -n "${DISPLAY:-}" ] && p=$(zenity --password --title="$1" 2>/dev/null); then
    printf '%s' "$p"
    return 0
  fi
  [ -r /dev/tty ] || return 1
  printf '%s: ' "$1" >&2
  read -rs p </dev/tty || return 1
  printf '\n' >&2
  printf '%s' "$p"
}

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
  # Bisherigen Inhalt mit anzeigen: sonst sind in der Liste z. B. der
  # Debian-Installationsstick und ein leerer Sicherheits-Stick nicht
  # voneinander zu unterscheiden - und die falsche Wahl zerstoert das
  # Installationsmedium.
  inhalt=$(lsblk -no LABEL,FSTYPE "/dev/$name" 2>/dev/null | awk 'NF' | head -n3 | tr '\n' ' ' | sed 's/  */ /g; s/ *$//')
  [ -n "$inhalt" ] || inhalt="(leer/unbekannt)"
  USB_ARGS+=("/dev/$name" "$sizeh" "$inhalt")
done

if [ "${#USB_ARGS[@]}" -eq 0 ]; then
  die "Kein USB-Stick gefunden. Sicherheits-Stick anschließen und erneut versuchen."
fi

# "|| true" ist noetig, damit ein Abbruch im Dialog hier unten sauber mit
# der erklaerenden Meldung endet. Ohne das beendet "set -e" das Skript
# schon bei der Zuweisung - die "die"-Zeile darunter waere toter Code.
KEY_STICK=$(zenity --list --title="Sicherheits-Stick wählen" \
  --text="Auf diesem Stick werden der Entschlüsselungs-Schlüssel für nutzers Daten (2 GiB) und ein Datenspeicher-Bereich (Rest der Kapazität) angelegt.\nDer Stick wird dabei komplett neu formatiert.\n\nACHTUNG: Spalte \"Bisheriger Inhalt\" prüfen - ein Installations- oder Datenstick wäre danach unwiederbringlich leer." \
  --column="Gerät" --column="Größe" --column="Bisheriger Inhalt" --width=620 --height=280 \
  "${USB_ARGS[@]}" 2>/dev/null || true)
[ -n "$KEY_STICK" ] || die "Abgebrochen: kein Sicherheits-Stick gewählt."

KEY_STICK_SIZE=$(lsblk -dnb -o SIZE "$KEY_STICK" 2>/dev/null || echo 0)
if [ "$KEY_STICK_SIZE" -lt 2684354560 ]; then
  die "Der gewählte Stick ist zu klein (mind. ~2,5 GB nötig für Schlüssel- + Datenpartition)."
fi

# --- 3. Recovery-Passphrase ---
say "Zusätzlich zum Stick wird ein Wiederherstellungs-Passwort als zweiter LUKS-Schlüssel für nutzers Daten-Partition angelegt (Notfall, falls der Stick verloren geht). Bitte sicher verwahren, NICHT dem Endnutzer geben. Mindestens 12 Zeichen."
RECOVERY_PASS=""
VERSUCHE=0
while [ -z "$RECOVERY_PASS" ] || [ "${#RECOVERY_PASS}" -lt 12 ]; do
  VERSUCHE=$((VERSUCHE + 1))
  if [ "$VERSUCHE" -gt 3 ]; then
    # Begrenzt, damit das Skript bei fehlender Eingabemoeglichkeit (weder
    # zenity noch Terminal) nicht endlos fragt. An dieser Stelle wurde noch
    # nichts veraendert - Abbruch ist gefahrlos.
    die "Kein gültiges Wiederherstellungs-Passwort eingegeben - Abbruch. Es wurde noch nichts verändert."
  fi
  RECOVERY_PASS=$(ask_password "Wiederherstellungs-Passwort festlegen (mind. 12 Zeichen)") || true
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
# Die Nummer der neuen Partition wird durch Vergleich VORHER/NACHHER
# ermittelt, nicht als "hoechste vorhandene Nummer": parted vergibt immer
# die niedrigste FREIE Nummer. Bei einer Luecke in der Nummerierung (z. B.
# 1, 2 und 4 vorhanden -> die neue wird 3) waere "hoechste Nummer" die
# falsche Partition - und der naechste Schritt wuerde sie per luksFormat
# unwiederbringlich ueberschreiben.
NUMMERN_VORHER=$(parted -s "$SYS_DISK" print | awk '/^ [0-9]/{print $1}')

parted -s "$SYS_DISK" mkpart dialos-nutzer-home "${FREE_START_MIB}MiB" "${FREE_END_MIB}MiB"
partprobe "$SYS_DISK"
udevadm settle --timeout=10 >/dev/null 2>&1 || sleep 2

NUMMERN_NACHHER=$(parted -s "$SYS_DISK" print | awk '/^ [0-9]/{print $1}')
NEW_PART_NUM=$(printf '%s\n' "$NUMMERN_NACHHER" \
  | grep -vxF -f <(printf '%s\n' "$NUMMERN_VORHER") || true)
if [ "$(printf '%s\n' "$NEW_PART_NUM" | grep -c .)" -ne 1 ]; then
  die "Konnte die neu angelegte Partition nicht eindeutig bestimmen (gefunden: '$(printf '%s' "$NEW_PART_NUM" | tr '\n' ' ')'). Abbruch vor jeder Formatierung - es wurde nichts verschlüsselt."
fi

# Geraetenamen, die auf eine Ziffer enden (nvme0n1, mmcblk0), haengen ihre
# Partitionsnummer mit "p" an - klassische (sda) direkt.
case "$SYS_DISK" in
  *[0-9]) HOME_PART="${SYS_DISK}p${NEW_PART_NUM}" ;;
  *)      HOME_PART="${SYS_DISK}${NEW_PART_NUM}" ;;
esac
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
# mktemp statt eines festen /tmp/.rp: legt die Datei direkt mit 600 an (der
# feste Name entstand mit der Standard-umask, war also kurz weltlesbar) und
# ist nicht vorhersagbar - in einem weltschreibbaren /tmp sonst eine
# Symlink-Falle. Inhalt ist die Notfall-Passphrase im Klartext.
# Bewusst ohne abschliessenden Zeilenumbruch ("printf '%s'"): cryptsetup
# nimmt den kompletten Dateiinhalt als Schluessel, bei der spaeteren
# interaktiven Eingabe wird der Zeilenumbruch abgeschnitten - nur so passen
# beide zusammen.
RP_FILE=$(mktemp)
printf '%s' "$RECOVERY_PASS" > "$RP_FILE"
cryptsetup luksAddKey --batch-mode --key-file="$KEYFILE" "$HOME_PART" "$RP_FILE"
shred -u "$RP_FILE"

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
# Startordner ist bewusst $AUFRUF_HOME, nicht $HOME: das Skript laeuft als
# root, $HOME waere also /root - und damit gerade NICHT der Ordner, in dem
# der Nextcloud-Sync des Admin-Kontos liegt.
SAVE_TO=$(zenity --file-selection --save --confirm-overwrite \
  --title="Verschlüsseltes Schlüssel-Backup speichern (z. B. im Nextcloud-Sync-Ordner)" \
  --filename="$AUFRUF_HOME/${BACKUP_LABEL}.key.enc" 2>"$SAVE_TO_ERR" || true)
ZENITY_ERR=$(cat "$SAVE_TO_ERR" 2>/dev/null || true)
rm -f "$SAVE_TO_ERR"
if [ -n "$SAVE_TO" ]; then
  cp "$BACKUP_TMP" "$SAVE_TO"
  # Sonst gehoert die Datei root und das Admin-Konto (bzw. dessen
  # Nextcloud-Client) kann sie weder lesen noch synchronisieren.
  chown "$AUFRUF_USER" "$SAVE_TO" 2>/dev/null || true
  chmod 600 "$SAVE_TO" 2>/dev/null || true
  say "Backup gespeichert unter: $SAVE_TO\nFalls der Ordner nicht automatisch synchronisiert wird, manuell in die Nextcloud hochladen.\n\nBACKUP-PASSWORT (getrennt von der Nextcloud aufbewahren, z. B. im eigenen Passwort-Manager - NIEMALS zusammen mit der Backup-Datei!):\n$BACKUP_PASS\n\nEntschlüsselung später: openssl enc -d -aes-256-cbc -pbkdf2 -in $BACKUP_LABEL.key.enc -out neuer-stick.key"
else
  warn "Kein Speicherort gewählt - Schlüssel-Backup wurde NICHT gesichert.${ZENITY_ERR:+ Fehlermeldung: $ZENITY_ERR}"
fi
shred -u "$BACKUP_TMP" 2>/dev/null || rm -f "$BACKUP_TMP"

# --- 7c. Partition kurz oeffnen, leer mit ext4 formatieren, wieder
#          schliessen ---
cryptsetup open --key-file="$KEYFILE" "$HOME_PART" "$HOME_LUKS_NAME"
mkfs.ext4 -F -L "$HOME_FS_LABEL" "/dev/mapper/$HOME_LUKS_NAME"
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
