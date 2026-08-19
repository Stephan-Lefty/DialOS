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
BIN="$REPO/iso-build/config/includes.chroot/usr/local/bin"
abweichend=()
fehlend=()

for pfad in "$BIN"/*; do
    datei="$(basename "$pfad")"
    [ -f "$pfad" ] || continue
    if [ ! -e "/usr/local/bin/$datei" ]; then
        fehlend+=("$datei")
    elif ! cmp -s "$pfad" "/usr/local/bin/$datei"; then
        abweichend+=("$datei")
    fi
done

if [ ${#abweichend[@]} -eq 0 ] && [ ${#fehlend[@]} -eq 0 ]; then
    echo "Alles installiert und identisch zum Repo."
    exit 0
fi

for datei in "${abweichend[@]}"; do
    printf '%-36s abweichend  (Repo %s, installiert %s)\n' "$datei" \
        "$(stat -c %y "$BIN/$datei" | cut -d. -f1)" \
        "$(stat -c %y "/usr/local/bin/$datei" | cut -d. -f1)"
done
for datei in "${fehlend[@]}"; do
    printf '%-36s NICHT installiert\n' "$datei"
done

if [ "$1" = "--befehl" ]; then
    echo
    echo "sudo install -m 0755 \\"
    for datei in "${abweichend[@]}" "${fehlend[@]}"; do
        echo "  $BIN/$datei \\"
    done
    echo "  /usr/local/bin/"
fi
exit 1
