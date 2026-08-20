#!/bin/bash
# Vergleicht ALLE Dateien des Repos mit den installierten Fassungen.
#
# Warum es das gibt (2026-08-19): Zwei Skripte liefen auf dem Geraet zwei Tage
# lang in einer aelteren Fassung als im Repo - dialos-start-ansage.py fehlte die
# am 2026-08-17 entschiedene Mikrofon-Reihenfolge, dialos-ton-ausgabe.py der
# letzte_wahl-Fix. Beide waren committet, beide nie installiert.
#
# WARUM ES JETZT ALLES DURCHLAEUFT statt einer Liste von Verzeichnissen
# (2026-08-20): Die erste Fassung prueft nur usr/local/bin und meldete deshalb
# "alles identisch", waehrend zwei neue Dateien in usr/local/sbin und
# etc/sudoers.d ungeprueft blieben. Ergaenzt - und am naechsten Tag legte ich
# /etc/logrotate.d an und vergass es wieder, obwohl im Kommentar stand, dass man
# neue Orte hier eintragen muss.
#
# Eine Liste, die von Hand gepflegt werden muss, veraltet. Bei einem Werkzeug,
# das genau gegen "vergessen" gebaut ist, ist das der falsche Entwurf. Deshalb
# laeuft es jetzt ueber den ganzen Baum: Was im Repo liegt, wird verglichen -
# ohne dass jemand daran denken muss.
#
# Aufruf:  scripts/dialos-installstand.sh
#          scripts/dialos-installstand.sh --befehl    (gibt die install-Befehle aus)

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CHROOT="$REPO/iso-build/config/includes.chroot"

# Was nie installiert wird und deshalb nicht verglichen werden darf:
#   __pycache__   Python legt es beim Import an, es gehoert nicht ins System
#   .gitkeep      nur damit git leere Ordner behaelt
AUSNAHMEN='/__pycache__/|/\.gitkeep$'

abweichend=()
fehlend=()
unpruefbar=()

while IFS= read -r pfad; do
    ziel="${pfad#$CHROOT}"
    # DRITTE MOEGLICHKEIT: nicht pruefbar. Ohne sie log das Skript - alles unter
    # /var/lib/bluetooth gehoert root und ist mit 0700 geschuetzt; ein normaler
    # Nutzer sieht dort nichts und bekaeme "NICHT installiert" gemeldet, obwohl
    # die Datei da ist. Ein Pruefwerkzeug, das "fehlt" sagt, wo es "kann ich
    # nicht sehen" heissen muesste, ist schlimmer als keines: Man glaubt ihm.
    if [ ! -r "$(dirname "$ziel")" ]; then
        unpruefbar+=("$ziel")
    elif [ ! -e "$ziel" ]; then
        fehlend+=("$ziel")
    elif ! cmp -s "$pfad" "$ziel" 2>/dev/null; then
        if [ ! -r "$ziel" ]; then
            unpruefbar+=("$ziel")
        else
            abweichend+=("$ziel")
        fi
    fi
done < <(find "$CHROOT" -type f | grep -Ev "$AUSNAHMEN" | sort)

if [ ${#abweichend[@]} -eq 0 ] && [ ${#fehlend[@]} -eq 0 ]; then
    echo "Alles installiert und identisch zum Repo."
    [ ${#unpruefbar[@]} -gt 0 ] && \
        echo "(${#unpruefbar[@]} Dateien nicht pruefbar - Rechte. Mit sudo aufrufen, um auch die zu sehen.)"
    exit 0
fi

for ziel in "${abweichend[@]}"; do
    printf '%-52s abweichend  (installiert %s)\n' "$ziel" \
        "$(stat -c %y "$ziel" 2>/dev/null | cut -d. -f1)"
done
for ziel in "${fehlend[@]}"; do
    printf '%-52s NICHT installiert\n' "$ziel"
done
if [ ${#unpruefbar[@]} -gt 0 ]; then
    printf '%-52s (%d Dateien - mit sudo aufrufen)\n' \
        "nicht pruefbar wegen Rechten" "${#unpruefbar[@]}"
fi

if [ "$1" = "--befehl" ] 2>/dev/null; then
    echo
    for ziel in "${abweichend[@]}" "${fehlend[@]}"; do
        # Rechte nach Ort. Eine sudoers-Datei mit falschen Rechten wird von
        # sudo STILL ignoriert - das waere kein Schoenheitsfehler.
        case "$ziel" in
            /etc/sudoers.d/*)         rechte=0440 ;;
            /usr/local/bin/*|/usr/local/sbin/*) rechte=0755 ;;
            *.sh|*.py)                rechte=0755 ;;
            *)                        rechte=0644 ;;
        esac
        echo "sudo install -D -m $rechte $CHROOT$ziel $ziel"
    done
fi
exit 1
