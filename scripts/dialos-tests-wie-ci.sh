#!/bin/bash
# DialOS: die Tests so laufen lassen, als waere DialOS NICHT installiert -
# wie am Arbeitsrechner und in der CI auf GitHub.
#
# ANLASS (2026-11-24): test_jeder_gestrichene_satz_nennt_einen_bestehenden war
# am Laptop gruen und am Arbeitsrechner zwoelf Tage lang rot. Der Sprachdienst
# laedt Erweiterungs- und Programmsaetze ueber /usr/local/bin/dialos-
# erweiterung.py und dialos-programm.py - also aus dem INSTALLIERTEN System. Am
# Laptop ist das da, also lief der Test gegen etwas, das es in der CI nicht
# gibt. "Alle Tests gruen" am Geraet hiess deshalb nicht "gruen in der CI".
#
# WIE: Das Repo wird in einen Arbeitsordner kopiert, dort zeigen die beiden
# Werkzeugpfade ins Leere, dann laufen alle Tests. Das Repo selbst bleibt
# unberuehrt.
#
# Aufruf (aus dem Repo-Wurzelverzeichnis):
#   scripts/dialos-tests-wie-ci.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ARBEIT="$(mktemp -d "${TMPDIR:-/tmp}/dialos-tests-wie-ci.XXXXXX")"
trap 'rm -rf "$ARBEIT"' EXIT

cd "$REPO"
git ls-files -z tests docs iso-build/config/includes.chroot | \
  xargs -0 cp --parents -t "$ARBEIT"
# Auch noch nicht committete Aenderungen an Tests und Geraetedateien mitnehmen.
git diff --name-only -z -- tests docs iso-build/config/includes.chroot | \
  xargs -0 -r cp --parents -t "$ARBEIT"

DIENST="$ARBEIT/iso-build/config/includes.chroot/usr/local/bin/dialos-sprachbefehl-desktop.py"
sed -i 's#^ERWEITERUNG_WERKZEUG = .*#ERWEITERUNG_WERKZEUG = "/gibt/es/nicht.py"#;
        s#^PROGRAMM_WERKZEUG = .*#PROGRAMM_WERKZEUG = "/gibt/es/nicht.py"#' "$DIENST"
grep -q '^ERWEITERUNG_WERKZEUG = "/gibt/es/nicht.py"' "$DIENST" || {
  echo "Pfad nicht umgebogen - hat sich der Name im Sprachdienst geaendert?" >&2; exit 1; }

cd "$ARBEIT"
python3 -m unittest discover -s tests
