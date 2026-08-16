#!/bin/bash
# DialOS: Stellt die Preseed-Datei fuer die Dauer einer Installation im
# lokalen Netz bereit und sagt, was im Debian-Installer einzutippen ist.
#
# WARUM DAS DER EMPFOHLENE WEG IST (Stand 2026-08-16): Der
# Debian-Installer holt die Preseed-Datei ueber EINFACHES HTTP - die
# Debian-Doku nennt fuer preseed/url ausschliesslich http:// und tftp://,
# HTTPS wird nirgends zugesichert. Genau daran scheitern die naheliegenden
# Ablageorte:
#   - dialos.org laeuft auf WordPress und leitet http:// per 301 zwingend
#     auf https:// um. Die Datei ist dort zwar erreichbar, aber nur ueber
#     diese Umleitung.
#   - Nextcloud erzwingt HTTPS noch strikter (meist inklusive HSTS) und
#     erzeugt zusaetzlich lange Token-Adressen, die am Boot-Prompt
#     abgetippt werden muessten und bei jeder neuen Freigabe wechseln.
#
# Dieser Weg umgeht alles davon: einfaches HTTP, keine Umleitung, kein
# Hoster, kein Internet noetig. Und die Datei kommt unmittelbar aus dem
# Repo - sie kann also gar nicht veralten.
#
# Passt ohnehin zum Ablauf: Jedes Geraet wird im Buero aufgesetzt, der
# Rechner mit dem Repo steht daneben.
#
# Aufruf:  ./scripts/dialos-preseed-server.sh [Port]
# Beenden: Strg+C
set -euo pipefail

PORT="${1:-8080}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEBROOT="$REPO_ROOT/website"
PRESEED_PFAD="d-i/trixie/preseed.cfg"

if [ ! -f "$WEBROOT/$PRESEED_PFAD" ]; then
  echo "Preseed-Datei nicht gefunden: $WEBROOT/$PRESEED_PFAD" >&2
  echo "Stimmt der Repo-Pfad? (erwartet wird website/$PRESEED_PFAD)" >&2
  exit 1
fi

# Nur IPv4: "hostname -I" liefert auch IPv6-Adressen, die hier niemanden
# interessieren und die Ausgabe unlesbar machen wuerden (beim ersten Test
# am 2026-08-16 waren es vier Stueck).
IPV4S=$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+(\.[0-9]+){3}$' || true)
IP=$(echo "$IPV4S" | head -n1)
if [ -z "$IP" ]; then
  echo "Keine IP-Adresse gefunden - haengt dieser Rechner im Netz?" >&2
  exit 1
fi

if command -v ss >/dev/null 2>&1 && ss -ltn "sport = :$PORT" 2>/dev/null | grep -q LISTEN; then
  echo "Port $PORT ist schon belegt. Anderen Port angeben, z. B.:" >&2
  echo "    $0 8081" >&2
  exit 1
fi

cat <<HINWEIS

  Im Debian-Installer diese Zeile an die Startzeile anhaengen
  (UEFI: Taste "e", ans Ende der Zeile mit "linux", dann Strg+X):

      preseed/url=http://$IP:$PORT/$PRESEED_PFAD

HINWEIS

# Bei mehreren Netzwerkkarten (z. B. LAN und WLAN gleichzeitig) ist die
# erste Adresse nicht zwangslaeufig die, ueber die das Zielgeraet kommt.
if [ "$(echo "$IPV4S" | grep -c .)" -gt 1 ]; then
  echo "  Dieser Rechner hat mehrere Adressen. Falls es nicht klappt,"
  echo "  eine der anderen probieren:"
  echo "$IPV4S" | tail -n +2 | sed 's/^/      /'
  echo
fi

echo "  Zielgeraet und dieser Rechner muessen im selben Netz haengen."
echo "  Beenden mit Strg+C, sobald die Partitionierung durchgelaufen ist."
echo

cd "$WEBROOT"
exec python3 -m http.server "$PORT"
