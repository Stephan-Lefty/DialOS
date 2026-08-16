#!/usr/bin/env bash
# Kleiner Helfer für authentifizierte Aufrufe der WordPress-REST-API von dialos.org.
#
# Warum ein eigenes Skript und nicht jedes Mal curl von Hand: das Application
# Password soll nie in der Shell-History oder in einer Prozessliste landen –
# deshalb kommt es aus der .env und wird über --netrc-artige Basic-Auth an curl
# übergeben, nicht als Teil der URL.
#
# Benutzung:
#   ./wp-api.sh GET  wp/v2/users/me?context=edit
#   ./wp-api.sh GET  wp/v2/pages/2?context=edit
#   ./wp-api.sh POST wp/v2/pages/2 '{"title":"DialOS hört zu"}'
#
# Verbindungstest (Schritt 2 aus dem Briefing):
#   ./wp-api.sh GET wp/v2/users/me?context=edit

set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "Fehler: .env fehlt. Lege sie nach dem Muster von .env.example an." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

if [[ -z "${WP_APP_PASSWORD:-}" ]]; then
  echo "Fehler: WP_APP_PASSWORD ist in .env nicht gesetzt." >&2
  exit 1
fi

method="${1:-GET}"
route="${2:?Route fehlt, z. B. wp/v2/users/me?context=edit}"
body="${3:-}"

args=(-sS -X "$method" -u "${WP_USER}:${WP_APP_PASSWORD}" -w '\n--- HTTP %{http_code} ---\n')
if [[ -n "$body" ]]; then
  args+=(-H 'Content-Type: application/json' -d "$body")
fi

curl "${args[@]}" "${WP_URL}/wp-json/${route}"
