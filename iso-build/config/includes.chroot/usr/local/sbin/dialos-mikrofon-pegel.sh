#!/bin/bash
# DialOS: setzt die Aufnahme-Verstaerkung der eingebauten Mikrofone auf
# einen Pegel, bei dem nichts uebersteuert.
#
# WARUM ES DAS GIBT (gefunden am 2026-08-16, echter Fehler)
# =========================================================
# Auf dem T490 standen ab Werk ZWEI Verstaerkungsstufen auf Anschlag:
# "Capture" auf +30 dB und zusaetzlich "Internal Mic Boost" auf +30 dB.
# Zusammen 60 dB. Das Signal klebte dadurch dauerhaft am Anschlag:
# gemessen 76 % RMS, jeder zweite Abtastwert gesaettigt.
#
# Die Folge war kein Rauschen, sondern Stille auf der Bedienseite: Vosk
# erkennt Sprache anhand von Pausen zwischen den Woertern. In einem
# Dauervollausschlag gibt es keine Pausen, also liefert der Erkenner nie
# ein Ergebnis. Der Sprachbefehl-Dienst lief, hoerte zu und konnte
# prinzipiell nichts verstehen - ohne jede Fehlermeldung. Fuer ein
# System, das ausschliesslich per Sprache bedient wird, ist das der
# Totalausfall.
#
# Nach dem Zuruecknehmen des Boosts: 2,8 % RMS, null gesaettigte Werte,
# Erkennung laeuft.
#
# WARUM BOOST AUF NULL UND NICHT "IRGENDWAS DAZWISCHEN"
# Ein zu leises Signal laesst sich in Software nachverstaerken; ein
# uebersteuertes ist unwiederbringlich zerstoert, die Spitzen sind
# abgeschnitten. Im Zweifel also lieber zu leise.
#
# WARUM EIN DIENST UND NICHT "alsactl store"
# "alsactl store" schreibt den kompletten Mixer-Zustand DIESER Karte
# nach /var/lib/alsa/asound.state - geraetespezifisch, und damit nichts,
# was sich in die ISO-Vorlage legen laesst. Dieses Skript sucht
# stattdessen die Regler ueber ihren Namen und funktioniert deshalb auf
# jedem Geraet, auch wenn die Karte anders heisst oder anders nummeriert
# ist.
#
# Aufruf: sudo /usr/local/sbin/dialos-mikrofon-pegel.sh
# Laeuft ausserdem bei jedem Start ueber dialos-mikrofon-pegel.service.
set -uo pipefail

CAPTURE_PEGEL="100%"

if ! command -v amixer >/dev/null 2>&1; then
  echo "amixer fehlt (Paket alsa-utils) - nichts zu tun." >&2
  exit 0
fi

geaendert=0

# Ueber alle Karten laufen: Auf Geraeten mit mehreren Audio-Chips (z. B.
# HDMI plus Onboard) traegt nicht zwangslaeufig Karte 0 das Mikrofon.
for karte in $(awk -F'[][]' '/^ *[0-9]+ \[/ {print $2}' /proc/asound/cards 2>/dev/null | tr -d ' '); do
  regler=$(amixer -c "$karte" scontrols 2>/dev/null | sed "s/^Simple mixer control '//; s/',[0-9]*$//")
  [ -n "$regler" ] || continue

  while IFS= read -r name; do
    case "$name" in
      *"Mic Boost"*)
        # Jede Boost-Stufe auf 0 dB. Betrifft "Mic Boost" ebenso wie
        # "Internal Mic Boost" - auf dem T490 waren beide vorhanden.
        if amixer -c "$karte" sset "$name" 0 >/dev/null 2>&1; then
          echo "  Karte $karte: '$name' auf 0 dB"
          geaendert=1
        fi
        ;;
      Capture)
        if amixer -c "$karte" sset "$name" "$CAPTURE_PEGEL" >/dev/null 2>&1; then
          echo "  Karte $karte: 'Capture' auf $CAPTURE_PEGEL"
          geaendert=1
        fi
        ;;
    esac
  done <<< "$regler"
done

if [ "$geaendert" -eq 0 ]; then
  echo "Keine passenden Regler gefunden - Geraet ohne eingebautes Mikrofon?"
fi

# Zusaetzlich in ALSAs eigenen Zustand schreiben, damit der Pegel auch
# dann stimmt, wenn dieser Dienst einmal nicht laeuft. Ergaenzung, kein
# Ersatz - siehe Begruendung oben.
if command -v alsactl >/dev/null 2>&1; then
  alsactl store >/dev/null 2>&1 || true
fi

exit 0
