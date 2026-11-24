#!/bin/bash
# DialOS: legt die DialOS-Fassung von os-release an - und schuetzt sie vor
# Debian-Updates.
#
# ANLASS (2026-11-24): Das Debian-Update von base-files (13.8+deb13u8) hat
# /etc/os-release wieder auf "Debian GNU/Linux 13" gesetzt, laut Dateidatum
# schon am 2026-11-08 einmal. base-files liefert die Datei selbst mit und
# ueberschreibt sie bei jedem Update - ein einfaches cp (so stand es bis dahin
# in Aufbau-Schritt 3) haelt nur bis zum naechsten.
#
# WIE: Debian bietet dafuer dpkg-divert. Damit legt base-files seine Fassung
# kuenftig unter *.debian ab, und unsere bleibt stehen. Beide Pfade werden
# umgeleitet, weil base-files beide mitbringt: /usr/lib/os-release (die
# Datei) und /etc/os-release (ein Verweis darauf). Danach steht unsere Datei
# in /usr/lib/os-release, und /etc/os-release zeigt wie bei Debian darauf.
#
# Mehrfaches Ausfuehren schadet nicht.
#
# Aufruf (aus dem Repo-Wurzelverzeichnis oder mit vollem Pfad):
#   sudo scripts/dialos-os-release.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
QUELLE="$REPO/iso-build/config/includes.chroot/etc/os-release"

if [ "$(id -u)" -ne 0 ]; then
  echo "Bitte mit sudo aufrufen." >&2
  exit 1
fi
[ -f "$QUELLE" ] || { echo "Fehlt: $QUELLE" >&2; exit 1; }

umleiten() {
  local pfad="$1"
  if dpkg-divert --list "$pfad" | grep -q "$pfad.debian"; then
    echo "schon umgeleitet: $pfad"
  else
    dpkg-divert --local --rename --divert "$pfad.debian" --add "$pfad"
  fi
}

umleiten /usr/lib/os-release
umleiten /etc/os-release

install -m 644 "$QUELLE" /usr/lib/os-release
ln -sfn ../usr/lib/os-release /etc/os-release

echo "os-release:"
grep -E '^(PRETTY_NAME|VERSION)=' /etc/os-release
echo "Debians Fassung liegt kuenftig unter /usr/lib/os-release.debian."
