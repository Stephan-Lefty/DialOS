#!/bin/bash
# DialOS: blendet Menueeintraege PRO KONTO aus.
#
# Stephans Vorgabe vom 2026-08-19: "Wenn du das nur ausblendest, dann passe das
# fuer den Nutzer an, bei dialosadmin kann mehr sichtbar sein, was ich z.B. fuer
# den Support benoetige."
#
# ZWEI KONTEN, ZWEI ZWECKE:
#
#   nutzer       sieht nur die Anwendungen aus docs/anwendungen.md. Er selbst
#                sieht den Bildschirm nicht - das Menue ist fuer den SEHENDEN
#                HELFER, der neben ihm sitzt. Und fuer den ist eine kurze Liste
#                mehr wert als eine vollstaendige: Er soll auf Anhieb finden,
#                was zum Geraet gehoert, und nicht zwischen Formeleditor und
#                Schriftvorschau suchen.
#
#   dialosadmin  sieht alles. Hier wird gewartet, hier laeuft der Support.
#                Ausgeblendet werden nur die drei echten Doppelungen.
#
# WEISSE LISTE, KEINE SCHWARZE. Fuer nutzer wird alles ausgeblendet, was NICHT
# auf der Behalten-Liste steht - nicht umgekehrt. Grund: Eine schwarze Liste
# veraltet mit jedem Debian-Update still. Kommt ein neues Programm dazu, waere
# es sofort sichtbar, und niemand merkt es. Bei einer weissen Liste ist der
# Standard "unsichtbar", und jede Ausnahme steht hier begruendet.
#
# WARUM UEBERLAGERUNG UND KEIN LOESCHEN: Die Dateien in ~/.local/share/
# applications ueberschreiben die systemweiten, ohne dass apt/dpkg sie je
# anfasst. Das uebersteht Debian-Updates, und es ist durch Loeschen einer Datei
# rueckgaengig zu machen. Was gar nicht gebraucht wird, ist ohnehin schon per
# scripts/dialos-aufraeumen.sh entfernt.
#
# Aufruf:
#   scripts/dialos-menue-pro-konto.sh              zeigt nur, was passieren wuerde
#   sudo scripts/dialos-menue-pro-konto.sh --wirklich
#
# Wiederholbar: bestehende Ueberlagerungen werden neu geschrieben.

set -u

WIRKLICH=0
[ "${1:-}" = "--wirklich" ] && WIRKLICH=1

# --- Was nutzer sehen darf --------------------------------------------------
# Jeder Eintrag mit Grund. Wer hier etwas hinzufuegt, gehoert auch nach
# docs/anwendungen.md.
BEHALTEN_NUTZER="
firefox-esr.desktop                 Browser, Jitsi-Videochat, WhatsApp Web
thunderbird.desktop                 Mail, Kalender, Kontakte - fuer den Helfer
libreoffice-writer.desktop          Briefe
org.gnome.Rhythmbox3.desktop        Musik, Podcasts, Hoerbuecher
de.haeckerfelix.Shortwave.desktop   Radio
vlc.desktop                         Videos
org.gnome.Nautilus.desktop          Dateien - der Helfer muss an ~/Notizen kommen
org.gnome.TextEditor.desktop        Einkaufszettel und Notizen sind .txt-Dateien
org.gnome.Evince.desktop            Briefe als PDF lesen
org.gnome.Loupe.desktop             Bilder von der Familie
org.gnome.Calculator.desktop        harmlos, und ein Helfer rechnet mal etwas
"

# --- Was auch dialosadmin nicht braucht ------------------------------------
# Die drei Doppelungen, die NICHT per Paket zu entfernen sind: Der
# KDE-Menueeintrag steckt jeweils im selben Paket wie das Original, und
# vim.desktop gehoert zu vim-common, an dem vim-tiny haengt. Aufgefallen am
# 2026-08-19 mit "dpkg -S" - wer sie per purge loeschen will, loescht das
# Werkzeug selbst.
DOPPELUNGEN="
gnome-system-monitor-kde.desktop    Doppelung, gleiches Paket wie die echte
mintstick-kde.desktop               Doppelung, gleiches Paket
mintstick-format-kde.desktop        Doppelung, gleiches Paket
vim.desktop                         Terminal-Editor braucht keinen Menueeintrag
"

sag() { printf '%s\n' "$*"; }

# Findet die systemweite Fassung eines Eintrags.
finde() {
    for ort in /usr/local/share/applications /usr/share/applications; do
        [ -f "$ort/$1" ] && { printf '%s\n' "$ort/$1"; return 0; }
    done
    return 1
}

# Schreibt eine Ueberlagerung mit NoDisplay=true nach ZIELORDNER.
# Kopiert das Original und haengt NoDisplay an, statt eine Minimaldatei zu
# bauen: Eine Ueberlagerung ERSETZT das Original vollstaendig, und fehlten
# darin Exec oder MimeType, waere das Programm auch als Standardanwendung fuer
# seine Dateitypen weg. Dasselbe Muster wie bei den vorhandenen
# Ueberlagerungen fuer Evolution und Kalender.
verstecke() {
    quelle="$1"; ziel="$2"
    grep -v '^NoDisplay=' "$quelle" > "$ziel"
    printf 'NoDisplay=true\n' >> "$ziel"
}

# Alle derzeit sichtbaren Eintraege.
sichtbare_eintraege() {
    python3 - <<'PYENDE'
import configparser, glob, os
gewinner = {}
for ort in ("/usr/local/share/applications", "/usr/share/applications"):
    for pfad in sorted(glob.glob(os.path.join(ort, "*.desktop"))):
        datei = os.path.basename(pfad)
        if datei in gewinner:
            continue                      # XDG: der erste Ort gewinnt
        c = configparser.RawConfigParser(strict=False)
        try:
            c.read(pfad, encoding="utf-8"); d = c["Desktop Entry"]
        except Exception:
            continue
        gewinner[datei] = (d.get("NoDisplay", "false").lower() == "true",
                           d.get("Type", "Application"))
for datei, (versteckt, typ) in sorted(gewinner.items()):
    if not versteckt and typ == "Application":
        print(datei)
PYENDE
}

# Auf EINE Zeile bringen, mit Leerzeichen getrennt. Der Vergleich unten prueft
# mit " $datei " auf Wortgrenzen - stehen die Namen durch Zeilenumbrueche
# getrennt da, passt kein Muster, und die weisse Liste greift stillschweigend
# nicht. Genau so ist es am 2026-08-19 im Probelauf passiert: Firefox und
# Thunderbird standen auf der Ausblenden-Liste.
BEHALTEN=$(printf '%s\n' "$BEHALTEN_NUTZER" | awk 'NF{print $1}' | tr '\n' ' ')
DOPPEL=$(printf '%s\n' "$DOPPELUNGEN" | awk 'NF{print $1}' | tr '\n' ' ')
SICHTBAR=$(sichtbare_eintraege)

# --- nutzer ----------------------------------------------------------------
FUER_NUTZER=""
for datei in $SICHTBAR; do
    case " $BEHALTEN " in *" $datei "*) continue ;; esac
    FUER_NUTZER="$FUER_NUTZER $datei"
done
FUER_NUTZER="${FUER_NUTZER# }"

sag "=== nutzer ==="
sag "sichtbar bleiben $(printf '%s\n' $BEHALTEN | wc -l), ausgeblendet werden $(printf '%s\n' $FUER_NUTZER | wc -l)"
sag ""
sag "bleibt sichtbar:"
printf '%s\n' "$BEHALTEN_NUTZER" | awk 'NF{printf "  %-36s %s\n", $1, substr($0, index($0,$2))}'
sag ""
sag "=== dialosadmin ==="
sag "ausgeblendet werden nur die Doppelungen:"
printf '%s\n' "$DOPPELUNGEN" | awk 'NF{printf "  %-36s %s\n", $1, substr($0, index($0,$2))}'

if [ "$WIRKLICH" = "0" ]; then
    sag ""
    sag "PROBELAUF - es wird nichts geschrieben."
    sag "Fuer nutzer wuerden ausgeblendet:"
    printf '%s\n' $FUER_NUTZER | sed 's/^/  /'
    sag ""
    sag "Zum Ausfuehren:  sudo $0 --wirklich"
    exit 0
fi

if [ "$(id -u)" != "0" ]; then
    sag "FEHLER: --wirklich braucht root. Bitte mit sudo aufrufen." >&2
    exit 1
fi

schreibe_fuer() {
    konto="$1"; heim="$2"; shift 2
    ordner="$heim/.local/share/applications"
    mkdir -p "$ordner" || return 1
    anzahl=0
    for datei in "$@"; do
        quelle=$(finde "$datei") || continue
        verstecke "$quelle" "$ordner/$datei" && anzahl=$((anzahl+1))
    done
    # RECHTE NICHT VERGESSEN. In diesem Projekt sind Rechte-Fallen bei
    # /etc/skel und fremden Heimatverzeichnissen schon mehrfach aufgetreten:
    # Eine Datei, die root gehoert, kann der Nutzer nicht mehr aendern, und
    # ein Ordner mit falschem Eigentuemer bleibt beim naechsten Anmelden
    # unbenutzt - ohne Fehlermeldung.
    if [ "$konto" != "skel" ]; then
        chown -R "$konto:$konto" "$heim/.local" 2>/dev/null || true
    fi
    sag "  $konto: $anzahl Ueberlagerungen in $ordner"
}

sag ""
sag "=== schreibe ==="
[ -d /home/nutzer ] && schreibe_fuer nutzer /home/nutzer $FUER_NUTZER \
    || sag "  /home/nutzer fehlt - uebersprungen (Konto noch nicht angelegt?)"
[ -d /home/dialosadmin ] && schreibe_fuer dialosadmin /home/dialosadmin $DOPPEL \
    || sag "  /home/dialosadmin fehlt - uebersprungen"
# Damit ein spaeter angelegtes Konto dieselbe Sicht bekommt.
schreibe_fuer skel /etc/skel $FUER_NUTZER

sag ""
sag "Rueckgaengig: die betreffende Datei in"
sag "<heim>/.local/share/applications/ loeschen und neu anmelden."
