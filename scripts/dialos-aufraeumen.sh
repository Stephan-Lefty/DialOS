#!/bin/bash
# DialOS: entfernt, was Debian mitbringt und DialOS nicht braucht.
#
# Stephans Vorgabe vom 2026-08-19: Nachdem auf einem neuen Rechner Debian +
# GNOME installiert ist und die drei Setup-Skripte durchgelaufen sind, soll
# alles weg, was mit Debian kam und fuer DialOS nicht benoetigt wird. Dieses
# Skript ist deshalb SCHRITT 4 des Aufbaus, nicht ein Werkzeug fuer den
# laufenden Betrieb.
#
# WARUM DAS NICHT EINFACH "apt purge" IST - der gefaehrliche Teil:
#
# Sobald ein Bestandteil von GNOME entfernt wird, gehen die Meta-Pakete
# "gnome", "gnome-core" und "task-gnome-desktop" mit. Das ist unvermeidlich und
# fuer sich harmlos. Die Folge ist es nicht: Danach gelten 49 Pakete als
# "automatisch installiert", die vorher nur ueber gnome-core gehalten wurden -
# darunter gnome-shell, nautilus, gnome-settings-daemon, gnome-keyring und
# pipewire-audio. Ein spaeteres "apt autoremove" wuerde dann anbieten, den
# ganzen Desktop UND den Ton-Unterbau zu entfernen. Gemessen am 2026-08-19 auf
# dem T490.
#
# Deshalb macht dieses Skript ZUERST die Bestandsaufnahme und markiert alles,
# was bleiben soll, als "manuell installiert" - und erst danach wird entfernt.
# Ohne diesen Schritt ist das Geraet einen "apt autoremove" davon entfernt,
# unbenutzbar zu sein.
#
# Es ruft AUSSERDEM kein autoremove auf, sondern zeigt am Ende nur, was eines
# anbieten wuerde. Bei einem Geraet, das ein blinder Nutzer allein bedient,
# gehoert diese Entscheidung einem Menschen mit Bildschirm.
#
# Aufruf:
#   scripts/dialos-aufraeumen.sh              zeigt nur, was passieren wuerde
#   sudo scripts/dialos-aufraeumen.sh --wirklich   entfernt
#
# Beide Laeufe sind wiederholbar: Schon entfernte Pakete werden uebersprungen.

set -u

WIRKLICH=0
[ "${1:-}" = "--wirklich" ] && WIRKLICH=1

# --- Was weg soll -----------------------------------------------------------
# STUFE A: Doppelungen und Fremdkoerper. Nichts davon hat mit DialOS zu tun,
# und nichts davon wuerde ein sehender Helfer vermissen.
WEG_A="gnome-characters gnome-font-viewer gnome-tour malcontent-gui xterm"

# STUFE B: durch DialOS oder durch die Festlegung in docs/anwendungen.md
# ersetzt. Jeder Eintrag hat dort seine Begruendung:
#   gnome-music, gnome-podcasts  -> Rhythmbox ist der EINE Player
#   totem                        -> VLC bleibt der einzige Videoplayer
#   gnome-contacts               -> Kontakte macht Thunderbird
#   gnome-clocks, gnome-weather  -> Uhrzeit und Wetter sagt DialOS selbst
#   gnome-maps                   -> rein visuell, fuer einen blinden Nutzer wertlos
#   gnome-connections            -> Fernwartung ist RustDesk
#   gnome-sound-recorder         -> Aufnahme macht DialOS
#   simple-scan                  -> kein Scanner im Aufbau
#   shotwell                     -> der Bildbetrachter genuegt
WEG_B="gnome-music gnome-podcasts totem totem-plugins gnome-contacts \
gnome-clocks gnome-weather gnome-maps gnome-connections gnome-sound-recorder \
simple-scan shotwell"

# STUFE C: Grenzfaelle, entschieden von Stephan am 2026-08-19, nachdem die
# Auswirkungen simuliert waren. Nur die vier LibreOffice-Teile gehen mit -
# festgelegt ist in docs/anwendungen.md ausschliesslich WRITER (Briefe), und
# Writer, libreoffice-core und libreoffice-common bleiben nachweislich
# unberuehrt (simuliert am 2026-08-19: 5 Pakete, davon 4 diese und das
# Meta-Paket "gnome").
WEG_C="libreoffice-calc libreoffice-impress libreoffice-draw libreoffice-math"

# BEWUSST NICHT ENTFERNT, obwohl sie fuer nutzer ausgeblendet sind:
#   obs-studio, gnome-snapshot  Videoaufnahme - der Zweck ist ungeklaert
#                               (docs/anwendungen.md). Was noch nicht
#                               entschieden ist, wird nicht vorab weggeworfen.
#   yelp, baobab                Admin-Werkzeuge, die im Support helfen koennen.
#   gnome-software, seahorse    dito. gnome-keyring selbst bleibt ohnehin - es
#                               haengt an der Anmeldung, nur die Oberflaeche
#                               waere entbehrlich.
#   libreoffice-startcenter     Stephan hat nur die vier Anwendungen benannt.
#                               Folge: Das Startzentrum zeigt danach Kacheln fuer
#                               Programme, die es nicht mehr gibt - fuer
#                               dialosadmin ein Schoenheitsfehler, fuer nutzer
#                               unsichtbar.

# --- Was NICHT per Paket geht ----------------------------------------------
# Drei Menue-Doppelungen stecken in Paketen, die bleiben MUESSEN:
#
#   gnome-system-monitor-kde.desktop  -> gnome-system-monitor (die echte auch!)
#   mintstick-kde.desktop, -format-kde -> mintstick (beide Werkzeuge bleiben)
#   vim.desktop                        -> vim-common, und daran haengt vim-tiny
#
# Aufgefallen am 2026-08-19: "dpkg -S" auf die Doppelung nennt dasselbe Paket
# wie das Original. Wer sie per purge loeschen will, loescht das Werkzeug.
# Diese drei werden deshalb pro Konto ausgeblendet - siehe
# scripts/dialos-menue-pro-konto.sh.

WEG="$WEG_A $WEG_B $WEG_C"

sag() { printf '%s\n' "$*"; }
trenner() { sag ""; sag "=== $* ==="; }

trenner "Was ueberhaupt noch installiert ist"
VORHANDEN=""
for p in $WEG; do
    if dpkg-query -W -f='${Status}' "$p" 2>/dev/null | grep -q "install ok installed"; then
        VORHANDEN="$VORHANDEN $p"
    fi
done
VORHANDEN="${VORHANDEN# }"
if [ -z "$VORHANDEN" ]; then
    sag "Nichts zu tun - alle Pakete sind schon entfernt."
    exit 0
fi
sag "$(printf '%s\n' $VORHANDEN | wc -l) Pakete: $VORHANDEN"

trenner "Schutz: was bleiben soll, wird 'manuell installiert'"
# Die Abhaengigkeiten von gnome-core AUSSER denen, die weg sollen. LC_ALL=C,
# weil "apt-cache depends" sonst "Haengt ab:" ausgibt und das Muster nicht
# passt - eigener Fehler vom 2026-08-19.
BEHALTEN=$(LC_ALL=C apt-cache depends --installed --no-recommends --no-suggests \
             gnome gnome-core task-gnome-desktop 2>/dev/null \
           | awk '/^ *Depends:/{print $2}' | sort -u)
SCHUTZ=""
for p in $BEHALTEN; do
    case " $WEG " in
        *" $p "*) continue ;;      # soll ja weg
    esac
    SCHUTZ="$SCHUTZ $p"
done
SCHUTZ="${SCHUTZ# }"
sag "$(printf '%s\n' $SCHUTZ | wc -l) Pakete werden geschuetzt, darunter:"
printf '%s\n' $SCHUTZ | grep -E '^(gnome-shell|nautilus|gnome-settings-daemon|gnome-keyring|pipewire-audio|gdm3)$' \
    | sed 's/^/  /' || true

if [ "$WIRKLICH" = "0" ]; then
    trenner "PROBELAUF - es wird nichts geaendert"
    sag "Was ein purge mitnehmen wuerde:"
    LC_ALL=C apt-get -s purge $VORHANDEN 2>&1 | grep -E '^(Purg|Remv|[0-9]+ upgraded)' | sed 's/^/  /'
    sag ""
    sag "Zum Ausfuehren:  sudo $0 --wirklich"
    exit 0
fi

if [ "$(id -u)" != "0" ]; then
    sag "FEHLER: --wirklich braucht root. Bitte mit sudo aufrufen." >&2
    exit 1
fi

trenner "Schutz setzen"
apt-mark manual $SCHUTZ >/dev/null || { sag "apt-mark fehlgeschlagen - Abbruch" >&2; exit 1; }
sag "erledigt"

trenner "Entfernen"
DEBIAN_FRONTEND=noninteractive apt-get -y purge $VORHANDEN || {
    sag "purge fehlgeschlagen - Abbruch, es wurde nichts weiter geaendert" >&2
    exit 1
}

trenner "Gegenprobe: laeuft der Desktop-Unterbau noch?"
FEHLT=""
for p in gnome-shell nautilus gnome-settings-daemon gnome-keyring pipewire-audio gdm3; do
    dpkg-query -W -f='${Status}' "$p" 2>/dev/null | grep -q "install ok installed" \
        || FEHLT="$FEHLT $p"
done
if [ -n "$FEHLT" ]; then
    sag "ACHTUNG, das darf nicht sein - fehlt jetzt:$FEHLT" >&2
    exit 1
fi
sag "gnome-shell, nautilus, gnome-settings-daemon, gnome-keyring,"
sag "pipewire-audio und gdm3 sind unversehrt."

trenner "Was ein autoremove ANBIETEN wuerde - bewusst nicht ausgefuehrt"
LC_ALL=C apt-get -s autoremove 2>&1 | grep -E '^(Remv|[0-9]+ upgraded)' | sed 's/^/  /' \
    || sag "  nichts"
sag ""
sag "Diese Entscheidung gehoert einem Menschen mit Bildschirm. Wenn die Liste"
sag "leer ist oder nur Bibliotheken enthaelt, ist 'sudo apt autoremove' in"
sag "Ordnung. Steht dort gnome-etwas, dann NICHT - dann hat der Schutz oben"
sag "etwas uebersehen, und das gehoert in dieses Skript nachgetragen."
