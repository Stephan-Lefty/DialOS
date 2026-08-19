#!/bin/bash
# Vergleicht ALLE Skripte des Repos mit den installierten Fassungen.
#
# Warum es das gibt (2026-08-19): Zwei Skripte liefen auf dem Geraet zwei Tage
# lang in einer aelteren Fassung als im Repo - dialos-start-ansage.py fehlte die
# am 2026-08-17 entschiedene Mikrofon-Reihenfolge, dialos-ton-ausgabe.py der
# letzte_wahl-Fix. Beide waren committet, beide nie installiert: die Repo-Datei
# wurde jeweils zehn Minuten NACH dem install noch bearbeitet.
#
# Aufgefallen ist es nur, weil einmal alles verglichen wurde statt nur die
# Dateien des Tages. Genau das macht dieses Skript - es ist die Version davon,
# die nicht vergessen wird.
#
# Aufruf:  scripts/dialos-installstand.sh
#          scripts/dialos-installstand.sh --befehl    (gibt den install-Befehl aus)

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CHROOT="$REPO/iso-build/config/includes.chroot"
# MEHRERE ORTE, nicht nur usr/local/bin (ergaenzt 2026-08-19). Das Skript sagte
# "alles identisch", waehrend zwei neue Dateien in usr/local/sbin und
# etc/sudoers.d gar nicht geprueft wurden - ein blinder Fleck in genau dem
# Werkzeug, das blinde Flecken verhindern soll. Wer einen neuen Ort im Repo
# anlegt, ergaenzt ihn hier.
ORTE="usr/local/bin usr/local/sbin etc/sudoers.d etc/systemd/user usr/local/share/applications"
abweichend=()
fehlend=()

for ort in $ORTE; do
    [ -d "$CHROOT/$ort" ] || continue
    for pfad in "$CHROOT/$ort"/*; do
        [ -f "$pfad" ] || continue
        datei="$(basename "$pfad")"
        ziel="/$ort/$datei"
        if [ ! -e "$ziel" ]; then
            fehlend+=("$ziel")
        elif ! cmp -s "$pfad" "$ziel"; then
            abweichend+=("$ziel")
        fi
    done
done

if [ ${#abweichend[@]} -eq 0 ] && [ ${#fehlend[@]} -eq 0 ]; then
    echo "Alles installiert und identisch zum Repo."
    exit 0
fi

for ziel in "${abweichend[@]}"; do
    printf '%-44s abweichend  (installiert %s)\n' "$ziel" \
        "$(stat -c %y "$ziel" | cut -d. -f1)"
done
for ziel in "${fehlend[@]}"; do
    printf '%-44s NICHT installiert\n' "$ziel"
done

if [ "$1" = "--befehl" ]; then
    echo
    for ziel in "${abweichend[@]}" "${fehlend[@]}"; do
        # sudoers-Dateien brauchen 0440, alles andere 0755 bzw. 0644.
        case "$ziel" in
            /etc/sudoers.d/*) rechte=0440 ;;
            /etc/*)           rechte=0644 ;;
            *)                rechte=0755 ;;
        esac
        echo "sudo install -m $rechte $CHROOT${ziel} $ziel"
    done
fi
exit 1
