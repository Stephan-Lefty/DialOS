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
# 8 GiB Swap: bewusst NICHT "so gross wie das RAM" - diese Faustregel gilt
# nur fuer den Ruhezustand, der hier ausgeschlossen ist (Begruendung bei
# swap_verschluesseln unten). Ohne Hibernate reicht ein Notpolster.
SWAP_SIZE_MIB=8192
SWAP_MAPPER="cryptswap"

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

# --- Kleine Helfer rund um die Partitionstabelle ---
# parted liefert seine Ausgabe unabhaengig von der Systemsprache auf
# Englisch (Debians parted-Paket bringt keine Uebersetzungen mit, geprueft
# 2026-08-16) - "Free Space" ist als Suchbegriff also sicher.
letzte_freie_region() {
  parted -s "$1" unit MiB print free 2>/dev/null \
    | grep "Free Space" | tail -1 | awk '{gsub(/MiB/,""); print $1, $2}'
}
partitionsnummern() { parted -s "$1" print 2>/dev/null | awk '/^ [0-9]/{print $1}'; }
# Geraetenamen, die auf eine Ziffer enden (nvme0n1, mmcblk0), haengen ihre
# Partitionsnummer mit "p" an - klassische (sda) direkt.
partitionsgeraet() {
  case "$1" in
    *[0-9]) echo "${1}p${2}" ;;
    *)      echo "${1}${2}" ;;
  esac
}

# --- 1. Finde die System-Platte (die, auf der / liegt) ---
ROOT_SRC=$(findmnt -no SOURCE / || true)
[ -n "$ROOT_SRC" ] || die "Konnte die Root-Partition nicht ermitteln."
ROOT_DISK_NAME=$(lsblk -no PKNAME "$ROOT_SRC" 2>/dev/null || true)
[ -n "$ROOT_DISK_NAME" ] || die "Konnte die System-Platte nicht ermitteln."
SYS_DISK="/dev/$ROOT_DISK_NAME"

# --- 1b. Unverschluesselten Swap durch verschluesselten ersetzen ---
# Warum ueberhaupt: /home/nutzer liegt zwar in LUKS2, aber Speicherseiten
# dieses Kontos - offene Dokumente, Mails, Browserinhalte - koennen vom
# Kernel in einen Klartext-Swap ausgelagert werden. Die waeren dann ohne
# Sicherheits-Stick lesbar und ebenso nach Ausbau der SSD, also genau an
# dem Schutz vorbei, den die Home-Partition herstellen soll (siehe
# docs/sicherheit-datenschutz.md).
#
# Warum ein bei jedem Start neu gewuerfelter Schluessel (/dev/urandom) und
# nicht ein dauerhafter: ein dauerhafter Schluessel muesste irgendwo
# liegen, wo er beim Booten lesbar ist - das waere wieder der verworfene
# cryptsetup-initramfs-Ansatz. Ein Zufallsschluessel pro Start braucht
# nichts davon. Er schliesst den Ruhezustand (Hibernate) endgueltig aus:
# das Abbild liesse sich nach einem Neustart nicht mehr entschluesseln.
# Das ist kein Verlust - Hibernate war beim Stick-Gate-Design ohnehin
# unmoeglich, und ein Swap kleiner als der Arbeitsspeicher taugt dafuer
# ohnehin nicht.
#
# Warum 8 GiB statt "so gross wie das RAM": die alte Faustregel
# "Swap >= RAM" existiert nur wegen Hibernate. Ohne Hibernate ist der Swap
# reines Notpolster gegen den OOM-Killer - wichtig auf einem Geraet fuer
# blinde Nutzer, weil ein abgeschossener Screenreader/TTS-Prozess bedeutet,
# dass der Nutzer keinerlei Rueckmeldung mehr bekommt.
swap_verschluesseln() {
  local plain_swaps swap_part partuuid nummern_vorher nummern_nachher neue_nr
  local frei start_mib end_mib frage antwort name nr swap_status

  plain_swaps=$(lsblk -nlo NAME,FSTYPE "$SYS_DISK" 2>/dev/null | awk '$2=="swap"{print $1}')

  if [ -z "$plain_swaps" ] && grep -q "^${SWAP_MAPPER}[[:space:]]" /etc/crypttab 2>/dev/null; then
    echo "Verschluesselter Swap ist bereits eingerichtet - uebersprungen."
    return 0
  fi

  if [ -n "$plain_swaps" ]; then
    frage="Auf $SYS_DISK liegt unverschlüsselter Swap ($(echo "$plain_swaps" | tr '\n' ' ')).\n\nDaten von 'nutzer' können dorthin ausgelagert werden und wären ohne Sicherheits-Stick im Klartext lesbar.\n\nJetzt durch ${SWAP_SIZE_MIB} MiB verschlüsselten Swap ersetzen (Schlüssel wird bei jedem Start neu gewürfelt)?\n\nDer Ruhezustand ist danach nicht mehr möglich - er ist bei diesem Sicherheitsdesign ohnehin ausgeschlossen."
  else
    frage="Auf $SYS_DISK gibt es keinen Swap.\n\nJetzt ${SWAP_SIZE_MIB} MiB verschlüsselten Swap anlegen (Schlüssel wird bei jedem Start neu gewürfelt)?\n\nEmpfohlen: dient als Notpolster, damit bei Speichermangel nicht der Screenreader abgeschossen wird."
  fi

  # Wichtig: erst pruefen, OB zenity ueberhaupt laufen kann, und nur dann
  # dessen Antwort auswerten. Sonst waere ein "Nein" im Dialog nicht von
  # "zenity gar nicht startbar" zu unterscheiden - die Frage wuerde dann
  # trotz Ablehnung nochmal im Terminal gestellt.
  if [ -n "${DISPLAY:-}" ] && command -v zenity >/dev/null 2>&1; then
    if ! zenity --question --width=460 --title="DialOS: Swap verschlüsseln" --text="$frage" 2>/dev/null; then
      warn "Swap unveraendert gelassen - er bleibt unverschluesselt."
      return 0
    fi
  elif [ -r /dev/tty ]; then
    printf '%b\n' "$frage" >&2
    printf 'Swap jetzt verschluesseln? [J/n]: ' >&2
    read -r antwort </dev/tty || antwort="n"
    case "$antwort" in
      [NnQq]*) warn "Swap unveraendert gelassen - er bleibt unverschluesselt."; return 0 ;;
    esac
  else
    warn "Swap-Umstellung uebersprungen (keine Rueckfrage moeglich) - der Swap bleibt unverschluesselt."
    return 0
  fi

  # /etc/crypttab wird von systemd nur ausgewertet, wenn die Integration
  # ueberhaupt installiert ist. Debian 13 hat sie aus dem systemd-Paket
  # herausgeloest ("systemd-cryptsetup") - ohne dieses Paket gibt es weder
  # den Generator noch systemd-cryptsetup@.service, der crypttab-Eintrag
  # bliebe beim Booten also wirkungslos und der Swap einfach inaktiv.
  # Genau das ist beim ersten echten Lauf am 2026-08-16 passiert. Die
  # Home-Partition merkt davon nichts, weil dialos-stick-gate.sh sie
  # selbst per "cryptsetup open" oeffnet - deshalb faellt es nur hier auf.
  # Pruefung bewusst VOR jeder Aenderung an der Partitionstabelle.
  if [ ! -x /usr/lib/systemd/system-generators/systemd-cryptsetup-generator ]; then
    echo "Paket 'systemd-cryptsetup' fehlt - wird nachinstalliert ..."
    apt-get install -y systemd-cryptsetup >/dev/null 2>&1 \
      || die "Konnte 'systemd-cryptsetup' nicht installieren. Ohne dieses Paket wertet Debian 13 /etc/crypttab nicht aus, der verschlüsselte Swap bliebe wirkungslos. Abbruch - an der Partitionstabelle wurde noch nichts geändert."
  fi

  # Alte Swap-Partitionen abschalten und entfernen. swapoff zuerst, sonst
  # laesst sich die Partition nicht loeschen.
  for name in $plain_swaps; do
    swapoff "/dev/$name" 2>/dev/null || true
  done
  cp /etc/fstab /etc/fstab.dialos-vor-swap-umstellung
  # Alle bisherigen Swap-Zeilen raus (Feld 3 = "swap"); die neue Zeile auf
  # /dev/mapper/... kommt weiter unten neu dazu. Betrifft bewusst ALLE
  # Swap-Zeilen - ein zweiter Swap auf einer anderen Platte waere in
  # diesem Geraetekonzept nicht vorgesehen. Sicherungskopie steht daneben.
  sed -i '/[[:space:]]swap[[:space:]]/d' /etc/fstab

  # Fehler hier NICHT verschlucken: bliebe die alte Partition stehen,
  # waere ihr fstab-Eintrag schon entfernt (Platz dauerhaft verschenkt)
  # und die Freiplatz-Rechnung unten falsch.
  for name in $plain_swaps; do
    nr=$(cat "/sys/class/block/$name/partition" 2>/dev/null || true)
    if [ -n "$nr" ]; then
      parted -s "$SYS_DISK" rm "$nr" \
        || die "Konnte die alte Swap-Partition $name (Nr. $nr) nicht entfernen - Abbruch. /etc/fstab wurde bereits angepasst, Sicherungskopie: /etc/fstab.dialos-vor-swap-umstellung"
    fi
  done
  partprobe "$SYS_DISK" 2>/dev/null || true
  udevadm settle --timeout=10 >/dev/null 2>&1 || sleep 2

  # Neuen Swap an den ANFANG der letzten freien Region legen - so bleibt
  # der Rest der Platte eine zusammenhaengende freie Region fuer
  # dialos-nutzer-home direkt dahinter.
  frei=$(letzte_freie_region "$SYS_DISK")
  start_mib=$(echo "$frei" | awk '{printf "%d", $1}')
  end_mib=$(echo "$frei" | awk '{printf "%d", $2}')
  if [ -z "$start_mib" ] || [ "$((end_mib - start_mib))" -lt "$((SWAP_SIZE_MIB + MIN_FREE_MIB))" ]; then
    die "Zu wenig Platz, um Swap ($SWAP_SIZE_MIB MiB) UND die Home-Partition (mind. $MIN_FREE_MIB MiB) anzulegen. Die alten Swap-Zeilen wurden aus /etc/fstab entfernt (Sicherungskopie: /etc/fstab.dialos-vor-swap-umstellung)."
  fi

  nummern_vorher=$(partitionsnummern "$SYS_DISK")
  parted -s "$SYS_DISK" mkpart dialos-swap "${start_mib}MiB" "$((start_mib + SWAP_SIZE_MIB))MiB"
  partprobe "$SYS_DISK" 2>/dev/null || true
  udevadm settle --timeout=10 >/dev/null 2>&1 || sleep 2
  nummern_nachher=$(partitionsnummern "$SYS_DISK")
  neue_nr=$(printf '%s\n' "$nummern_nachher" | grep -vxF -f <(printf '%s\n' "$nummern_vorher") || true)
  if [ "$(printf '%s\n' "$neue_nr" | grep -c .)" -ne 1 ]; then
    die "Konnte die neue Swap-Partition nicht eindeutig bestimmen - Abbruch."
  fi
  swap_part=$(partitionsgeraet "$SYS_DISK" "$neue_nr")
  [ -b "$swap_part" ] || die "Neue Swap-Partition $swap_part nicht gefunden - Abbruch."

  # Frische Partition saeubern: sie beginnt am selben Offset wie die alte
  # Swap-Partition, deren Header sonst einfach stehen bliebe. blkid meldet
  # dann weiterhin "swap" samt ALTER UUID auf einer Partition, die kuenftig
  # verschluesselt wird - das verwirrt die Sicherheitspruefungen von
  # systemd-cryptsetup und sieht bei jeder spaeteren Fehlersuche falsch aus
  # (beobachtet beim ersten echten Lauf, 2026-08-16).
  wipefs -a "$swap_part" >/dev/null 2>&1 || true

  # Referenz per PARTUUID, NICHT per UUID: die crypttab-Option "swap" legt
  # bei jedem Start ein frisches Dateisystem an, die Dateisystem-UUID
  # aendert sich also staendig. Die PARTUUID steht dagegen fest in der
  # Partitionstabelle.
  partuuid=$(blkid -s PARTUUID -o value "$swap_part" 2>/dev/null || true)
  [ -n "$partuuid" ] || die "Konnte die PARTUUID von $swap_part nicht ermitteln - Abbruch."

  touch /etc/crypttab
  sed -i "/^${SWAP_MAPPER}[[:space:]]/d" /etc/crypttab
  # Fuehrender Zeilenumbruch, falls die vorhandene Datei nicht mit einem
  # endet - sonst klebte der neue Eintrag an die letzte Zeile. Eine
  # zusaetzliche Leerzeile stoert in beiden Dateien nicht.
  printf '\n%s /dev/disk/by-partuuid/%s /dev/urandom swap,cipher=aes-xts-plain64,size=256\n' \
    "$SWAP_MAPPER" "$partuuid" >> /etc/crypttab
  # "nofail": taucht der Mapper beim Booten einmal nicht auf, soll der
  # Start deswegen nicht haengen bleiben - ein fehlender Swap ist ein
  # Komfortproblem, ein blockierter Boot auf einem Geraet fuer blinde
  # Nutzer ein echtes.
  printf '\n/dev/mapper/%s none swap sw,nofail 0 0\n' "$SWAP_MAPPER" >> /etc/fstab

  # Hibernate-Rest aufraeumen: ohne das versucht das initramfs weiter, von
  # einer Swap-Partition zu erwachen, die es so nicht mehr gibt.
  mkdir -p /etc/initramfs-tools/conf.d
  echo "RESUME=none" > /etc/initramfs-tools/conf.d/resume
  update-initramfs -u >/dev/null 2>&1 || warn "update-initramfs meldete einen Fehler - vor dem naechsten Neustart pruefen."

  # Swap als Notpolster, nicht fuer Routine-Auslagerung: je weniger
  # ausgelagert wird, desto weniger von nutzers Daten verlaesst ueberhaupt
  # den Arbeitsspeicher.
  printf '# DialOS: Swap ist Notpolster, kein Routine-Ziel (viel RAM vorhanden).\nvm.swappiness=10\n' \
    > /etc/sysctl.d/99-dialos-swappiness.conf
  sysctl -q vm.swappiness=10 2>/dev/null || true

  # Sofort aktivieren - bewusst DIREKT per cryptsetup statt ueber
  # "systemctl start systemd-cryptsetup@...": den crypttab-Eintrag wertet
  # erst der Generator beim naechsten Boot aus, die Unit existiert also
  # jetzt noch gar nicht. Ein "systemctl start" darauf tut schlicht nichts
  # und meldet auch keinen brauchbaren Fehler - genau so blieb der Swap
  # beim ersten echten Lauf am 2026-08-16 stumm inaktiv. Die Parameter
  # hier entsprechen exakt der crypttab-Zeile oben.
  systemctl daemon-reload 2>/dev/null || true
  if cryptsetup open --type plain --key-file /dev/urandom --key-size 256 \
       --cipher aes-xts-plain64 "$swap_part" "$SWAP_MAPPER" 2>/dev/null \
     && mkswap -q "/dev/mapper/$SWAP_MAPPER" >/dev/null 2>&1 \
     && swapon "/dev/mapper/$SWAP_MAPPER" 2>/dev/null; then
    swap_status="sofort aktiv, kein Neustart nötig"
  else
    swap_status="wird erst beim nächsten Neustart aktiv"
  fi

  say "Verschlüsselter Swap eingerichtet: $swap_part → /dev/mapper/$SWAP_MAPPER (${SWAP_SIZE_MIB} MiB, Schlüssel bei jedem Start neu).\nStatus: $swap_status\n\nvm.swappiness steht jetzt auf 10, der Ruhezustand ist deaktiviert.\nSicherungskopie der alten fstab: /etc/fstab.dialos-vor-swap-umstellung"
}

swap_verschluesseln

# --- 1c. Freien Platz fuer die Home-Partition ermitteln (erst JETZT, nach
#          der Swap-Umstellung - die veraendert die Aufteilung) ---
FREI=$(letzte_freie_region "$SYS_DISK")
FREE_START_MIB=$(echo "$FREI" | awk '{printf "%d", $1}')
FREE_END_MIB=$(echo "$FREI" | awk '{printf "%d", $2}')

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
NUMMERN_VORHER=$(partitionsnummern "$SYS_DISK")

parted -s "$SYS_DISK" mkpart dialos-nutzer-home "${FREE_START_MIB}MiB" "${FREE_END_MIB}MiB"
partprobe "$SYS_DISK"
udevadm settle --timeout=10 >/dev/null 2>&1 || sleep 2

NUMMERN_NACHHER=$(partitionsnummern "$SYS_DISK")
NEW_PART_NUM=$(printf '%s\n' "$NUMMERN_NACHHER" \
  | grep -vxF -f <(printf '%s\n' "$NUMMERN_VORHER") || true)
if [ "$(printf '%s\n' "$NEW_PART_NUM" | grep -c .)" -ne 1 ]; then
  die "Konnte die neu angelegte Partition nicht eindeutig bestimmen (gefunden: '$(printf '%s' "$NEW_PART_NUM" | tr '\n' ' ')'). Abbruch vor jeder Formatierung - es wurde nichts verschlüsselt."
fi

HOME_PART=$(partitionsgeraet "$SYS_DISK" "$NEW_PART_NUM")
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
