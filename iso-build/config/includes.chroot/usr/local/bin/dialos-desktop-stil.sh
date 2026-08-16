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
#   dialos-desktop-stil.sh wiederherstellen
#                                    -> zuletzt gewaehlten Stil erneut
#                                       anwenden, ohne Ansage (Autostart)
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

# Symbol fuer den Startknopf. Bewusst ein eigenes, generisches
# Fenster-Sinnbild statt des Windows-Logos von Microsoft - Begruendung
# steht in der SVG-Datei selbst. ArcMenu bringt kein Windows-Symbol mit,
# und Debian hat ausserdem saemtliche ArcMenu-Icons aus dem Paket
# entfernt (65-2), weshalb der Knopf ohne diese Datei auf das
# GNOME-Distro-Icon zurueckfaellt.
STARTKNOPF_ICON="/usr/local/share/dialos/dialos-fenster-symbolic.svg"

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

# Kennt die LAUFENDE GNOME Shell die Erweiterung schon? Das ist etwas
# anderes als "installiert": Die Shell durchsucht
# /usr/share/gnome-shell/extensions nur beim Start. Frisch per apt
# installierte Erweiterungen liegen also auf der Platte, sind fuer
# "gnome-extensions" aber noch unsichtbar ("Erweiterung existiert nicht") -
# unter Wayland hilft dagegen nur ab- und wieder anmelden, weil sich die
# Shell dort nicht neu starten laesst. Live gefunden am 2026-08-16.
#
# Die Liste wird EINMAL gelesen und gemerkt. Das ist kein Geschwindigkeits-
# trick, sondern eine Fehlerkorrektur vom 2026-08-16: "gnome-extensions
# list" fragt die laufende Shell ueber D-Bus. Waehrend des Umschaltens auf
# Windows baut die Shell ihre komplette obere Leiste neu auf (dash-to-panel
# ersetzt sie), und in diesem Moment kann die Abfrage leer oder
# unvollstaendig zurueckkommen. Wurde sie - wie vorher - fuer jede
# Erweiterung einzeln MITTEN im Umschalten gestellt, hielt das Skript eine
# laengst bekannte Erweiterung faelschlich fuer unbekannt und sagte an, man
# muesse sich ab- und wieder anmelden. Das war schlicht falsch und
# verunsichert genau die Nutzer, die sich am wenigsten selbst behelfen
# koennen. Jetzt wird die Liste vor der ersten Aenderung aufgenommen, wenn
# die Shell noch ruhig ist.
SHELL_LISTE=""
shell_liste_lesen() {
  SHELL_LISTE="$(gnome-extensions list 2>/dev/null)"
  # Leere Antwort heisst nicht "keine Erweiterungen", sondern meistens
  # "Shell gerade beschaeftigt" - einmal nachfassen, statt daraus die
  # falsche Schlussfolgerung zu ziehen.
  if [ -z "$SHELL_LISTE" ]; then
    sleep 1
    SHELL_LISTE="$(gnome-extensions list 2>/dev/null)"
  fi
}

kennt_shell() {
  [ -n "$SHELL_LISTE" ] || shell_liste_lesen
  printf '%s\n' "$SHELL_LISTE" | grep -qx "$1"
}

# Traegt eine UUID in org.gnome.shell enabled-extensions ein bzw. aus.
# Dieser Weg funktioniert auch dann, wenn die Shell die Erweiterung noch
# nicht kennt - sie schaltet sie dann beim naechsten Start ein. Ueber
# Gio statt per Textbastelei an der gsettings-Ausgabe, damit die Liste
# nicht durch ein falsch gesetztes Anfuehrungszeichen zerstoert wird.
liste_setzen() {
  python3 - "$1" "$2" <<'PY'
import sys
import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio

aktion, uuid = sys.argv[1], sys.argv[2]
s = Gio.Settings.new("org.gnome.shell")
liste = s.get_strv("enabled-extensions")
if aktion == "ein" and uuid not in liste:
    liste.append(uuid)
elif aktion == "aus" and uuid in liste:
    liste = [x for x in liste if x != uuid]
else:
    sys.exit(0)
s.set_strv("enabled-extensions", liste)
Gio.Settings.sync()
PY
}

# ------------------------------------------------------------ Hilfsmittel

# Findet heraus, aus welchem Verzeichnis ein Schema zu lesen ist.
#
# Normalfall: leer, das Schema steckt im systemweiten Cache
# (/usr/share/glib-2.0/schemas/gschemas.compiled).
#
# Ausnahme, live gefunden am 2026-08-16: Debians Paket
# gnome-shell-extension-arc-menu (65-2) legt sein Schema nach
# /usr/share/glib-2/schemas/ statt /usr/share/glib-2.0/schemas/ - ein
# Tippfehler im Paket. Dadurch landet es nie im systemweiten Cache, und
# "gsettings" antwortet mit "Kein derartiges Schema". Die Erweiterung
# selbst funktioniert trotzdem, weil GNOME Shell das mitgelieferte
# gschemas.compiled im Ordner der Erweiterung liest. Genau dort suchen
# wir deshalb auch - statt den Fehler zu umgehen, indem wir die
# ArcMenu-Einstellungen einfach weglassen.
#
# Bewusst allgemein gehalten (Suche ueber alle Erweiterungs-Ordner):
# Sollte Debian den Tippfehler beheben, greift automatisch wieder der
# systemweite Weg, ohne dass hier etwas anzupassen waere.
schema_verzeichnis() {
  local schema="$1" u d
  if gsettings list-schemas 2>/dev/null | grep -qx "$schema"; then
    echo ""
    return 0
  fi
  for u in "${ALLE_UUIDS[@]}"; do
    for d in "/usr/share/gnome-shell/extensions/$u/schemas" \
             "$HOME/.local/share/gnome-shell/extensions/$u/schemas"; do
      [ -f "$d/gschemas.compiled" ] || continue
      if GSETTINGS_SCHEMA_DIR="$d" gsettings list-schemas 2>/dev/null | grep -qx "$schema"; then
        echo "$d"
        return 0
      fi
    done
  done
  echo ""
}

# Setzt einen Wert nur, wenn es den Schluessel im Schema wirklich gibt.
# Ein blindes "gsettings set" auf einen unbekannten Schluessel bricht mit
# einem Fehler ab und wuerde den Rest der Umschaltung mitreissen - was den
# Desktop halb umgestellt zuruecklassen wuerde.
setze() {
  local schema="$1" schluessel="$2" wert="$3" d
  d="$(schema_verzeichnis "$schema")"
  if GSETTINGS_SCHEMA_DIR="$d" gsettings list-keys "$schema" 2>/dev/null | grep -qx "$schluessel"; then
    GSETTINGS_SCHEMA_DIR="$d" gsettings set "$schema" "$schluessel" "$wert" 2>/dev/null \
      || echo "  Hinweis: $schema $schluessel liess sich nicht setzen." >&2
  else
    echo "  Hinweis: $schema kennt den Schluessel $schluessel nicht (andere Version?) - uebersprungen." >&2
  fi
}

zuruecksetzen() {
  local schema="$1" schluessel="$2" d
  d="$(schema_verzeichnis "$schema")"
  if GSETTINGS_SCHEMA_DIR="$d" gsettings list-keys "$schema" 2>/dev/null | grep -qx "$schluessel"; then
    GSETTINGS_SCHEMA_DIR="$d" gsettings reset "$schema" "$schluessel" 2>/dev/null || true
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

  # Zustand der Shell aufnehmen, SOLANGE SIE RUHIG IST - siehe die
  # Begruendung bei shell_liste_lesen(). Danach faengt sie an, die Leiste
  # umzubauen, und antwortet zeitweise nicht verlaesslich.
  shell_liste_lesen

  # 1. Erweiterungen einschalten. Ohne das hier greift keine der
  #    Einstellungen darunter.
  gsettings set org.gnome.shell disable-user-extensions false 2>/dev/null || true
  local u
  neustart_noetig=0
  for u in "${ALLE_UUIDS[@]}"; do
    # Immer in die Liste eintragen - das ist der Weg, der auch dann
    # wirkt, wenn die Shell die Erweiterung noch gar nicht kennt.
    liste_setzen ein "$u" || echo "  Hinweis: $u liess sich nicht eintragen." >&2
    if kennt_shell "$u"; then
      gnome-extensions enable "$u" 2>/dev/null || true
    else
      neustart_noetig=1
    fi
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

  # Startknopf-Symbol. Fehlt die Datei, bleibt es beim bisherigen Symbol -
  # ein Startknopf ohne Bild waere schlimmer als einer mit dem falschen.
  if [ -f "$STARTKNOPF_ICON" ]; then
    setze "$a" menu-button-icon "'Custom_Icon'"
    setze "$a" custom-menu-button-icon "'$STARTKNOPF_ICON'"
  else
    echo "  Hinweis: $STARTKNOPF_ICON fehlt - der Startknopf behaelt sein bisheriges Symbol." >&2
  fi

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
  if [ "$neustart_noetig" -eq 1 ]; then
    melde "Die Windows-Optik ist eingestellt. Sie erscheint aber erst, wenn du dich einmal abmeldest und wieder anmeldest."
  else
    melde "Der Schreibtisch sieht jetzt aus wie unter Windows. Die Taskleiste ist unten, das Startmenue links. Sage Bescheid, wenn du zurueck willst."
  fi
}

# -------------------------------------------------------------- GNOME-Stil

auf_gnome() {
  echo "Schalte zurueck auf den GNOME-Standard ..."

  shell_liste_lesen

  local u
  for u in "${ALLE_UUIDS[@]}"; do
    kennt_shell "$u" && { gnome-extensions disable "$u" 2>/dev/null || true; }
    # Zusaetzlich aus der Liste austragen: Sonst schaltet die Shell sie
    # beim naechsten Start wieder ein, obwohl gerade "gnome" gewaehlt
    # wurde - der Nutzer haette nach dem Abmelden ungefragt wieder
    # Windows-Optik.
    liste_setzen aus "$u" || true
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
  for k in menu-layout position-in-panel dash-to-panel-standalone \
           menu-button-icon custom-menu-button-icon; do
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
  local stil fehlt u eingetragen unbekannt=0
  stil="$(gemerkter_stil)"
  eingetragen="$(gsettings get org.gnome.shell enabled-extensions 2>/dev/null)"
  echo "Gemerkter Stil: $stil"
  echo
  echo "Erweiterungen:"
  for u in "${ALLE_UUIDS[@]}"; do
    if ! ist_installiert "$u"; then
      printf "  %-40s nicht installiert\n" "$u"
    elif ! kennt_shell "$u"; then
      unbekannt=1
      printf "  %-40s installiert, aber der laufenden Shell noch unbekannt\n" "$u"
    elif [[ "$eingetragen" == *"'$u'"* ]]; then
      printf "  %-40s aktiv\n" "$u"
    else
      printf "  %-40s installiert, ausgeschaltet\n" "$u"
    fi
  done
  echo
  mapfile -t fehlt < <(fehlende_erweiterungen)
  if [ "${#fehlt[@]}" -gt 0 ] && [ -n "${fehlt[0]}" ]; then
    echo "Zum Nachinstallieren: sudo apt install $PAKETE"
  elif [ "$unbekannt" -eq 1 ]; then
    echo "Einmal abmelden und wieder anmelden - dann liest GNOME die neuen"
    echo "Erweiterungen ein. (Unter Wayland laesst sich die Shell nicht im"
    echo "laufenden Betrieb neu starten.)"
  fi

  if [ "$stil" = "windows" ]; then
    melde "Der Schreibtisch steht gerade auf Windows-Optik."
  else
    melde "Der Schreibtisch steht gerade auf GNOME-Standard."
  fi
}

# ------------------------------------------------------------------- Start

# Stellt beim Anmelden den zuletzt gewaehlten Stil wieder her - ohne
# Ansage, weil dabei niemand etwas ausgeloest hat.
#
# Streng genommen ist das doppelt gemoppelt: Die Einstellungen liegen in
# dconf und ueberleben einen Neustart von sich aus. Der Aufruf ist die
# Zusicherung dafuer - er faengt den Fall ab, dass etwas anderes die
# Erweiterungsliste zurueckgesetzt hat (Systemaktualisierung, ein
# versehentliches "dconf reset", ein neu angelegtes Konto, das die
# Merkdatei geerbt hat). Fuer einen blinden Nutzer waere ein Schreibtisch,
# der nach dem Einschalten anders aussieht als zuletzt, kein
# Schoenheitsfehler, sondern Orientierungsverlust.
wiederherstellen() {
  # Ohne Merkdatei gab es noch nie eine Wahl - dann NICHTS tun, statt
  # ungefragt Einstellungen zurueckzusetzen.
  [ -r "$STIL_DATEI" ] || { echo "Kein gemerkter Stil - nichts wiederherzustellen."; return 0; }
  case "$(gemerkter_stil)" in
    windows) auf_windows >/dev/null 2>&1 ;;
    *)       auf_gnome  >/dev/null 2>&1 ;;
  esac
  echo "Stil wiederhergestellt: $(gemerkter_stil)"
}

case "${1:-status}" in
  windows|Windows|win) auf_windows ;;
  gnome|Gnome|GNOME|standard) auf_gnome ;;
  wiederherstellen|--wiederherstellen) wiederherstellen ;;
  status|"") zeige_status ;;
  *)
    echo "Aufruf: $0 [windows|gnome|status|wiederherstellen]" >&2
    exit 1
    ;;
esac
