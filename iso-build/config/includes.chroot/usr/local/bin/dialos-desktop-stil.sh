#!/bin/bash
# DialOS: schaltet die Optik des Desktops zwischen GNOME-Standard und einer
# Windows-11-aehnlichen Variante um - in beide Richtungen, jederzeit.
#
# Hintergrund (Stephans Wunsch vom 2026-08-16): Es gibt Interessenten, die
# DialOS wegen der Sprachsteuerung wollen, aber aus der Windows-Welt kommen.
# Fuer die soll der Desktop aussehen wie gewohnt, ohne dass DialOS deshalb
# den barrierefreien GNOME-Unterbau (Orca, AT-SPI) aufgibt. Es wird also
# NICHTS ersetzt - GNOME bleibt, es bekommt nur drei Erweiterungen und ein
# paar Einstellungen obendrauf.
#
# Aufruf (bewusst OHNE sudo - alle Einstellungen sind benutzereigen):
#   dialos-desktop-stil.sh windows   -> Windows-11-Optik
#   dialos-desktop-stil.sh gnome     -> zurueck zum GNOME-Standard
#   dialos-desktop-stil.sh status    -> was ist gerade aktiv
#   dialos-desktop-stil.sh           -> wie "status"
#
# Spaeter ist genau dieses Skript der erste echte Sprachbefehl (siehe
# TODO.md, Fahrplan zur Sprachsteuerung) - deshalb ist die Rueckmeldung
# von Anfang an gesprochen und nicht nur geschrieben.
set -uo pipefail

UUID_PANEL="dash-to-panel@jderose9.github.com"
UUID_MENUE="arcmenu@arcmenu.com"
UUID_KACHELN="tiling-assistant@leleat-on-github"
ALLE_UUIDS=("$UUID_PANEL" "$UUID_MENUE" "$UUID_KACHELN")

PAKETE="gnome-shell-extension-dash-to-panel gnome-shell-extension-arc-menu gnome-shell-extension-tiling-assistant"
STIL_DATEI="${XDG_CONFIG_HOME:-$HOME/.config}/dialos/desktop-stil"
SAY="/usr/local/bin/dialos-say.py"

# ---------------------------------------------------------------- Ausgabe

# Sagt den Text und schreibt ihn zusaetzlich ins Terminal. Die Zielgruppe
# sieht den Bildschirm nicht - eine rein geschriebene Meldung waere fuer
# sie dasselbe wie gar keine.
melde() {
  echo "$1"
  [ -x "$SAY" ] && "$SAY" "$1" >/dev/null 2>&1
  return 0
}

fehler() {
  echo "FEHLER: $1" >&2
  [ -x "$SAY" ] && "$SAY" "$1" >/dev/null 2>&1
  exit 1
}

# --------------------------------------------------------- Voraussetzungen

if [ "$(id -u)" -eq 0 ]; then
  echo "Bitte OHNE sudo starten: $0 $*" >&2
  echo "Die Einstellungen gehoeren dem jeweiligen Benutzerkonto; als root" >&2
  echo "wuerden sie in /root landen und beim Nutzer nichts bewirken." >&2
  exit 1
fi

if [ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
  fehler "Es laeuft keine Grafik-Sitzung. Bitte am Schreibtisch anmelden und dort noch einmal versuchen."
fi

command -v gsettings >/dev/null 2>&1 || fehler "Das Programm gsettings fehlt. Ohne das kann ich die Einstellungen nicht aendern."
command -v gnome-extensions >/dev/null 2>&1 || fehler "Das Programm gnome-extensions fehlt. Es gehoert zu GNOME Shell."

# Prueft, ob eine Erweiterung ueberhaupt installiert ist. Systemweit
# installierte Debian-Pakete liegen unter /usr/share, von Hand
# nachinstallierte unter ~/.local/share - beide Orte zaehlen.
ist_installiert() {
  [ -d "/usr/share/gnome-shell/extensions/$1" ] || [ -d "$HOME/.local/share/gnome-shell/extensions/$1" ]
}

fehlende_erweiterungen() {
  local fehlt=()
  local u
  for u in "${ALLE_UUIDS[@]}"; do
    ist_installiert "$u" || fehlt+=("$u")
  done
  printf '%s\n' "${fehlt[@]}"
}

# ------------------------------------------------------------ Hilfsmittel

# Setzt einen Wert nur, wenn es den Schluessel im Schema wirklich gibt.
# Ein blindes "gsettings set" auf einen unbekannten Schluessel bricht mit
# einem Fehler ab und wuerde den Rest der Umschaltung mitreissen - was den
# Desktop halb umgestellt zuruecklassen wuerde.
setze() {
  local schema="$1" schluessel="$2" wert="$3"
  if gsettings list-keys "$schema" 2>/dev/null | grep -qx "$schluessel"; then
    gsettings set "$schema" "$schluessel" "$wert" 2>/dev/null \
      || echo "  Hinweis: $schema $schluessel liess sich nicht setzen." >&2
  else
    echo "  Hinweis: $schema kennt den Schluessel $schluessel nicht (andere Version?) - uebersprungen." >&2
  fi
}

zuruecksetzen() {
  local schema="$1" schluessel="$2"
  if gsettings list-keys "$schema" 2>/dev/null | grep -qx "$schluessel"; then
    gsettings reset "$schema" "$schluessel" 2>/dev/null || true
  fi
}

stil_merken() {
  mkdir -p "$(dirname "$STIL_DATEI")"
  echo "$1" > "$STIL_DATEI"
}

gemerkter_stil() {
  [ -r "$STIL_DATEI" ] && cat "$STIL_DATEI" || echo "gnome"
}

# ------------------------------------------------------------ Windows-Stil

# Die Taskleiste wird ueber "panel-element-positions" mittig gestellt -
# das ist das auffaelligste Merkmal von Windows 11. dash-to-panel legt
# diese Einstellung pro Bildschirm ab und benutzt dafuer seit Version 56
# die Seriennummer des Monitors als Schluessel, faellt aber ausdruecklich
# auf den Bildschirm-Index zurueck (panelSettings.js, getMonitorSetting).
# Deshalb schreiben wir auf "0" = Hauptbildschirm. Bei mehreren Monitoren
# bleibt der zweite auf dem Standard (Symbole links) - das ist bewusst so,
# statt fuer eine Kosmetik die Monitor-Erkennung nachzubauen.
D2P_ELEMENTE='{"0":[{"element":"showAppsButton","visible":false,"position":"stackedTL"},{"element":"activitiesButton","visible":false,"position":"stackedTL"},{"element":"leftBox","visible":true,"position":"stackedTL"},{"element":"taskbar","visible":true,"position":"centerMonitor"},{"element":"centerBox","visible":true,"position":"stackedBR"},{"element":"rightBox","visible":true,"position":"stackedBR"},{"element":"dateMenu","visible":true,"position":"stackedBR"},{"element":"systemMenu","visible":true,"position":"stackedBR"},{"element":"desktopButton","visible":true,"position":"stackedBR"}]}'

auf_windows() {
  local fehlt
  mapfile -t fehlt < <(fehlende_erweiterungen)
  if [ "${#fehlt[@]}" -gt 0 ] && [ -n "${fehlt[0]}" ]; then
    echo "Nicht installiert: ${fehlt[*]}" >&2
    echo "Nachinstallieren mit:" >&2
    echo "  sudo apt install $PAKETE" >&2
    fehler "Die Windows-Optik ist nicht eingerichtet. Es fehlen noch Programmteile."
  fi

  echo "Schalte auf Windows-11-Optik um ..."

  # 1. Erweiterungen einschalten. Ohne das hier greift keine der
  #    Einstellungen darunter.
  gsettings set org.gnome.shell disable-user-extensions false 2>/dev/null || true
  local u
  for u in "${ALLE_UUIDS[@]}"; do
    gnome-extensions enable "$u" 2>/dev/null || echo "  Hinweis: $u liess sich nicht einschalten." >&2
  done

  # 2. Taskleiste unten, Symbole mittig, Windows-typische Groesse.
  local s="org.gnome.shell.extensions.dash-to-panel"
  setze "$s" panel-positions '{"0":"BOTTOM"}'
  setze "$s" panel-sizes '{"0":48}'
  setze "$s" panel-element-positions "$D2P_ELEMENTE"
  setze "$s" dot-position "'BOTTOM'"
  setze "$s" group-apps true
  setze "$s" show-favorites true
  setze "$s" show-running-apps true
  setze "$s" appicon-margin 4
  setze "$s" animate-appicon-hover true
  setze "$s" intellihide false
  setze "$s" stockgs-keep-dash false

  # 3. Startmenue. ArcMenus Layout "Eleven" ist der Windows-11-Nachbau;
  #    "standalone" aus, damit der Knopf in der Taskleiste sitzt und nicht
  #    daneben.
  local a="org.gnome.shell.extensions.arcmenu"
  setze "$a" menu-layout "'Eleven'"
  setze "$a" position-in-panel "'Left'"
  setze "$a" dash-to-panel-standalone false

  # 4. Fensterknoepfe nach rechts, in der Reihenfolge von Windows. Das ist
  #    die Umstellung, die im Alltag am meisten ausmacht - unter GNOME sitzt
  #    dort standardmaessig nur ein Schliessen-Knopf.
  setze org.gnome.desktop.wm.preferences button-layout "'appmenu:minimize,maximize,close'"

  # 5. Die heisse Ecke oben links oeffnet unter GNOME die Uebersicht. Wer
  #    Windows gewohnt ist, loest sie staendig versehentlich aus.
  setze org.gnome.desktop.interface enable-hot-corners false
  setze org.gnome.desktop.interface clock-show-date true

  # tiling-assistant braucht nichts: es verhaelt sich ab Werk wie
  # Windows-Snap (an den Rand ziehen, Kachel-Vorschlag danach).

  stil_merken windows
  melde "Der Schreibtisch sieht jetzt aus wie unter Windows. Die Taskleiste ist unten, das Startmenue links. Sage Bescheid, wenn du zurueck willst."
}

# -------------------------------------------------------------- GNOME-Stil

auf_gnome() {
  echo "Schalte zurueck auf den GNOME-Standard ..."

  local u
  for u in "${ALLE_UUIDS[@]}"; do
    ist_installiert "$u" && { gnome-extensions disable "$u" 2>/dev/null || true; }
  done

  # Alles wieder auf Auslieferungszustand - nicht auf selbst gewaehlte
  # "GNOME-artige" Werte. Sonst waere ein spaeteres Hin- und Herschalten
  # nicht verlustfrei, weil sich unsere Vorstellung vom Standard und der
  # echte Standard auseinanderentwickeln koennen.
  local s="org.gnome.shell.extensions.dash-to-panel"
  local k
  for k in panel-positions panel-sizes panel-element-positions dot-position \
           group-apps show-favorites show-running-apps appicon-margin \
           animate-appicon-hover intellihide stockgs-keep-dash; do
    zuruecksetzen "$s" "$k"
  done

  local a="org.gnome.shell.extensions.arcmenu"
  for k in menu-layout position-in-panel dash-to-panel-standalone; do
    zuruecksetzen "$a" "$k"
  done

  zuruecksetzen org.gnome.desktop.wm.preferences button-layout
  zuruecksetzen org.gnome.desktop.interface enable-hot-corners
  zuruecksetzen org.gnome.desktop.interface clock-show-date

  stil_merken gnome
  melde "Der Schreibtisch ist wieder im GNOME-Standard."
}

# ----------------------------------------------------------------- Status

zeige_status() {
  local stil fehlt aktiv u
  stil="$(gemerkter_stil)"
  echo "Gemerkter Stil: $stil"
  echo
  echo "Erweiterungen:"
  for u in "${ALLE_UUIDS[@]}"; do
    if ! ist_installiert "$u"; then
      printf "  %-40s nicht installiert\n" "$u"
    else
      aktiv=$(gnome-extensions info "$u" 2>/dev/null | awk -F': ' '/^ *Enabled:/ {print $2}')
      printf "  %-40s installiert, aktiv: %s\n" "$u" "${aktiv:-unbekannt}"
    fi
  done
  echo
  mapfile -t fehlt < <(fehlende_erweiterungen)
  if [ "${#fehlt[@]}" -gt 0 ] && [ -n "${fehlt[0]}" ]; then
    echo "Zum Nachinstallieren: sudo apt install $PAKETE"
  fi

  if [ "$stil" = "windows" ]; then
    melde "Der Schreibtisch steht gerade auf Windows-Optik."
  else
    melde "Der Schreibtisch steht gerade auf GNOME-Standard."
  fi
}

# ------------------------------------------------------------------- Start

case "${1:-status}" in
  windows|Windows|win) auf_windows ;;
  gnome|Gnome|GNOME|standard) auf_gnome ;;
  status|"") zeige_status ;;
  *)
    echo "Aufruf: $0 [windows|gnome|status]" >&2
    exit 1
    ;;
esac
