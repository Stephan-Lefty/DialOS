#!/bin/bash
# DialOS: schaltet den Treiber einer NVIDIA-ZUSATZKARTE ab (nouveau).
#
# ANLASS (2026-11-24, Stephan: "beim Neustart blieb das System am
# Startbildschirm haengen. Das darf einem blinden Menschen nicht passieren!"):
# Mit dem Debian-Kernel 6.12.118 stuerzt nouveau auf dem T490 bei JEDEM Start
# ab ("BUG: unable to handle page fault" in gp102_acr_wpr_patch, beim
# Einrichten der GeForce MX250). Ob der Start dabei haengen bleibt, ist
# Glueckssache - um 09:35 blieb er stehen, um 09:46 lief er weiter, mit
# demselben Absturz im Protokoll. Mit 6.12.115 richtete sich nouveau sauber ein.
#
# DialOS braucht die Karte nicht: Bildschirm und Anzeige laufen ueber die
# Intel-Grafik. docs/hardware.md raet ohnehin von NVIDIA-Chips ab.
#
# NUR WENN ES SICHER IST: Abgeschaltet wird nur, wenn die NVIDIA-Karte ein
# "3D controller" ist (PCI-Klasse 0302, eine Zusatzkarte ohne eigenen
# Bildschirmausgang) UND eine andere Grafik den Bildschirm treibt (Klasse
# 0300, nicht NVIDIA). Ist NVIDIA die einzige oder die Haupt-Grafik, bliebe
# der Bildschirm sonst schwarz - dann tut das Skript nichts.
#
# Aufruf:
#   sudo scripts/dialos-nvidia-abschalten.sh            abschalten, falls sicher
#   scripts/dialos-nvidia-abschalten.sh --pruefen       nur sagen, was passieren wuerde
#
# Danach einmal neu starten.
set -euo pipefail

ZIEL=/etc/modprobe.d/dialos-kein-nouveau.conf
INHALT='# DialOS: nouveau abgeschaltet - NVIDIA-Zusatzkarte, Anzeige ueber eine andere
# Grafik. Angelegt von scripts/dialos-nvidia-abschalten.sh, Begruendung dort.
blacklist nouveau
options nouveau modeset=0'

pruefen=0
[ "${1:-}" = "--pruefen" ] && pruefen=1

# PCI-Klasse und Hersteller jedes Grafikgeraets: "0302 10de", "0300 8086" ...
geraete=$(lspci -n | awk '$2 ~ /^030[02]:?$/ {sub(":", "", $2); split($3, k, ":"); print $2, k[1]}')
nvidia_zusatz=$(echo "$geraete" | awk '$1 == "0302" && $2 == "10de"' | wc -l)
andere_anzeige=$(echo "$geraete" | awk '$1 == "0300" && $2 != "10de"' | wc -l)
nvidia_anzeige=$(echo "$geraete" | awk '$1 == "0300" && $2 == "10de"' | wc -l)

if [ "$nvidia_zusatz" -eq 0 ]; then
  echo "Keine NVIDIA-Zusatzkarte - nichts zu tun."
  exit 0
fi
if [ "$andere_anzeige" -eq 0 ] || [ "$nvidia_anzeige" -gt 0 ]; then
  echo "NVIDIA treibt hier (auch) den Bildschirm - nouveau bleibt AN." >&2
  echo "Sonst bliebe der Bildschirm schwarz. Bitte von Hand pruefen." >&2
  exit 0
fi

if [ -f "$ZIEL" ] && [ "$(cat "$ZIEL")" = "$INHALT" ]; then
  echo "nouveau ist schon abgeschaltet ($ZIEL)."
  exit 0
fi

if [ "$pruefen" -eq 1 ]; then
  echo "WUERDE abschalten: NVIDIA-Zusatzkarte gefunden, Anzeige ueber andere Grafik."
  echo "  schreibt $ZIEL und baut das initramfs neu (update-initramfs -u)."
  exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Bitte mit sudo aufrufen." >&2
  exit 1
fi

printf '%s\n' "$INHALT" > "$ZIEL"
chmod 644 "$ZIEL"
echo "geschrieben: $ZIEL"
# nouveau steckt auch im initramfs - ohne Neubau wuerde es dort weiter geladen.
update-initramfs -u
echo "Fertig. Bitte einmal neu starten."
