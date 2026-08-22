#!/bin/bash
# Tastenkombinationen fuer das Admin-Konto - Stephans Wunsch vom 2026-08-22:
# "Tastenkombination um von Linux auf Windows umzustellen" und
# "Tastenkombination um die Stimmenausgabe von Michael auf Anna und zurueck
# umzuschalten".
#
# NUR FUER dialosadmin. Das Nutzerkonto bedient beides ueber die Stimme; eine
# Tastenkombination waere dort ein Weg, den niemand findet und den man
# versehentlich ausloest. Hier ist sie richtig: Beim Vorfuehren, Entwickeln
# und Pruefen will man umschalten, ohne zu sprechen.
#
# WARUM ALS SKRIPT UND NICHT EINMAL GETIPPT: gsettings schreibt nach dconf,
# und dconf ueberlebt keine Neuinstallation. Was nicht im Repo steht, ist
# nach dem naechsten Aufsetzen weg.
#
# Aufruf (ohne sudo - die Einstellungen sind benutzereigen):
#   scripts/dialos-admin-tastenkuerzel.sh          -> setzen
#   scripts/dialos-admin-tastenkuerzel.sh zeigen   -> was gerade gilt
#   scripts/dialos-admin-tastenkuerzel.sh entfernen
#
# Mehrfaches Aufrufen ist gefahrlos - die Eintraege werden ersetzt, nicht
# angehaengt.
set -uo pipefail

SCHEMA="org.gnome.settings-daemon.plugins.media-keys"
PFAD="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
EIGEN="$SCHEMA.custom-keybinding:$PFAD"

# Die Tasten: Strg+Alt+W fuer Windows-Optik, Strg+Alt+S fuer Stimme.
# Beide waren am 2026-08-22 frei - geprueft gegen
# org.gnome.desktop.wm.keybindings, .media-keys und org.gnome.shell.keybindings.
# Strg+Alt statt Super, weil Super in GNOME zum Fenstermanager gehoert und
# eine Kollision dort teurer ist als hier.
NAMEN=("dialos-optik" "dialos-stimme")
TITEL=("DialOS: Optik Linux/Windows umschalten" "DialOS: Stimme Michael/Anna umschalten")
BEFEHLE=("/usr/local/bin/dialos-desktop-stil.sh umschalten"
         "/usr/local/bin/dialos-stimme-wechseln.py")
TASTEN=("<Control><Alt>w" "<Control><Alt>s")

zeigen() {
  echo "Eingetragen:"
  gsettings get "$SCHEMA" custom-keybindings
  for n in "${NAMEN[@]}"; do
    local p="$PFAD/$n/"
    if gsettings get "$SCHEMA" custom-keybindings 2>/dev/null | grep -q "$p"; then
      printf "  %-14s %-22s %s\n" \
        "$(gsettings get "$EIGEN/$n/" binding 2>/dev/null | tr -d "'")" \
        "$n" \
        "$(gsettings get "$EIGEN/$n/" command 2>/dev/null | tr -d "'")"
    fi
  done
}

pruefen() {
  local fehlt=0
  for b in "${BEFEHLE[@]}"; do
    local datei="${b%% *}"
    if [ ! -x "$datei" ]; then
      echo "FEHLT: $datei ist nicht ausfuehrbar - die Taste ginge ins Leere." >&2
      fehlt=1
    fi
  done
  return $fehlt
}

setzen() {
  # Lieber gar keine Taste als eine, die nichts tut: Wer sie einmal drueckt
  # und nichts passiert, drueckt sie nie wieder.
  pruefen || { echo "Nichts eingetragen." >&2; return 1; }

  local liste=""
  for n in "${NAMEN[@]}"; do
    liste="$liste'$PFAD/$n/', "
  done
  gsettings set "$SCHEMA" custom-keybindings "[${liste%, }]"

  local i
  for i in "${!NAMEN[@]}"; do
    local ziel="$EIGEN/${NAMEN[$i]}/"
    gsettings set "$ziel" name    "${TITEL[$i]}"
    gsettings set "$ziel" command "${BEFEHLE[$i]}"
    gsettings set "$ziel" binding "${TASTEN[$i]}"
    printf "  %-18s %s\n" "${TASTEN[$i]}" "${BEFEHLE[$i]}"
  done
  echo "Gesetzt. Wirkt sofort, kein Neuanmelden noetig."
}

entfernen() {
  gsettings set "$SCHEMA" custom-keybindings "[]"
  for n in "${NAMEN[@]}"; do
    # reset-recursively raeumt auch die Werte weg, nicht nur den Verweis -
    # sonst bleiben verwaiste Eintraege in dconf stehen.
    gsettings reset-recursively "$EIGEN/$n/" 2>/dev/null
  done
  echo "Entfernt."
}

case "${1:-setzen}" in
  setzen|"")        setzen ;;
  zeigen|status)    zeigen ;;
  entfernen|weg)    entfernen ;;
  *)
    echo "Aufruf: $0 [setzen|zeigen|entfernen]" >&2
    exit 1
    ;;
esac
