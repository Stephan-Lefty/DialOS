#!/bin/bash
# DialOS: Buero-Setup-Konsolidierungsskript. Fuehrt die Schritte 2-12,
# 14 (optional) und 15 aus docs/Debian-zu-DialOS.md automatisiert und
# der Reihe nach aus, statt sie manuell aus der Doku abzutippen.
#
# Deckt BEWUSST NICHT ab (siehe docs/Debian-zu-DialOS.md fuer den Grund):
#   Schritt 1  (Debian+GNOME-Basisinstallation) - manuell/Calamares,
#              legt dabei das Konto "dialosadmin" an.
#   Schritt 13 (nutzer-Konto anlegen) - bleibt eigener, bewusster
#              letzter Schritt (scripts/dialos-buero-setup-
#              abschliessen.sh): braucht den eingesteckten Sicherheits-
#              Stick und erzeugt das eigentliche Kundenkonto - kein
#              Schritt, den man "nebenbei" in einem grossen
#              unbeaufsichtigten Lauf verstecken sollte.
#   Schritt 16 (ISO bauen) - eigener, bewusster letzter Schritt.
#
# Schritt 14 (Bluetooth-Kopplungsdaten uebernehmen) ist zwar als
# Funktion vorhanden, aber NICHT Teil des Standardlaufs - nur sinnvoll,
# wenn dasselbe Testgeraet wie vorher wiederverwendet wird (Kopplungs-
# daten haengen an der MAC-Adresse des eingebauten Bluetooth-Adapters).
# Per --bluetooth-kopplung zuschaltbar oder einzeln aufrufbar.
#
# Jede Funktion entspricht 1:1 einem Doku-Schritt (gleiche Nummer) -
# neuer/geaenderter Doku-Schritt = neue/geaenderte Funktion hier, damit
# Skript und Doku nicht auseinanderlaufen koennen.
#
# Aufruf:
#   ./scripts/dialos-full-office-setup.sh                     # Standardlauf (ohne Schritt 14)
#   ./scripts/dialos-full-office-setup.sh --bluetooth-kopplung # Standardlauf inkl. Schritt 14
#   ./scripts/dialos-full-office-setup.sh 08                   # nur Schritt 8
#   ./scripts/dialos-full-office-setup.sh 14                   # nur Schritt 14
#
# Voraussetzung: wird als dialosadmin mit sudo-Rechten ausgefuehrt,
# aus einem lokal verfuegbaren Klon dieses Repos heraus (siehe
# docs/Debian-zu-DialOS.md, Abschnitt "Praxishinweis: externe Platte").
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

log() { echo; echo "=== [dialos-full-office-setup] $1 ==="; }

pruefe_netzwerk() {
  log "Netzwerk-Check"
  if ! curl -fsS --max-time 5 https://deb.debian.org >/dev/null 2>&1; then
    echo "Kein Internetzugang (deb.debian.org nicht erreichbar) - breche" >&2
    echo "lieber jetzt ab, statt mitten in einem apt-get/Download-Schritt" >&2
    echo "zu scheitern." >&2
    exit 1
  fi
}

schritt_02_paketliste() {
  log "Schritt 2: Paketliste installieren"
  sudo apt-get update
  sudo xargs -a iso-build/config/package-lists/desktop.list.chroot apt-get install -y
}

schritt_03_branding() {
  log "Schritt 3: Branding einspielen"
  sudo mkdir -p /usr/share/backgrounds/dialos
  sudo cp iso-build/config/includes.chroot/usr/share/backgrounds/dialos/*.png /usr/share/backgrounds/dialos/
  sudo cp assets/mark.png /usr/share/pixmaps/distributor-logo.png
  sudo cp iso-build/config/includes.chroot/etc/os-release /etc/os-release

  sudo mkdir -p /etc/dconf/db/local.d /etc/dconf/profile
  sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/00-dialos-branding /etc/dconf/db/local.d/
  sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/01-dialos-defaults /etc/dconf/db/local.d/
  sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/profile/user /etc/dconf/profile/
  sudo dconf update

  sudo mkdir -p /usr/share/plymouth/themes/dialos
  sudo cp iso-build/config/includes.chroot_before_packages/usr/share/plymouth/themes/dialos/* /usr/share/plymouth/themes/dialos/
  sudo plymouth-set-default-theme -R dialos

  # Ohne Kernel-Boot-Argument "splash" bleibt Plymouth im Textmodus,
  # egal welches Theme aktiv ist (siehe Debian-zu-DialOS.md, Schritt 3).
  sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/' /etc/default/grub
  sudo update-grub

  sudo mkdir -p /etc/penguins-eggs.d/brain.d/assets
  sudo cp iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/splash.png /etc/penguins-eggs.d/brain.d/assets/splash.png
}

schritt_04_autologin() {
  log "Schritt 4: Autologin fuer dialosadmin (Bootstrap, bis nutzer existiert)"
  local pfad
  pfad=$(sudo gdbus call --system --dest org.freedesktop.Accounts \
    --object-path /org/freedesktop/Accounts \
    --method org.freedesktop.Accounts.FindUserByName dialosadmin \
    | sed -E "s/^\(objectpath '([^']+)',?\)\$/\1/")
  sudo gdbus call --system --dest org.freedesktop.Accounts \
    --object-path "$pfad" \
    --method org.freedesktop.Accounts.User.SetAutomaticLogin true
}

schritt_05_calamares() {
  log "Schritt 5: Calamares-Installer einrichten"
  sudo apt-get install -y calamares calamares-settings-debian

  sudo cp -r iso-build/config/includes.chroot/etc/calamares/branding/dialos /etc/calamares/branding/
  sudo cp iso-build/config/includes.chroot/etc/calamares/modules/locale.conf /etc/calamares/modules/
  sudo cp iso-build/config/includes.chroot/etc/calamares/modules/shellprocess.conf /etc/calamares/modules/
  sudo sed -i 's/^branding: debian/branding: dialos/' /etc/calamares/settings.conf

  sudo mkdir -p /etc/penguins-eggs.d/brain.d/assets/calamares
  sudo cp -r iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/calamares/. /etc/penguins-eggs.d/brain.d/assets/calamares/

  sudo cp iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/base.yaml.tmpl /etc/penguins-eggs.d/brain.d/base.yaml.tmpl
}

schritt_06_rustdesk() {
  log "Schritt 6: RustDesk installieren (und deaktivieren)"
  local tmp_deb
  tmp_deb=$(mktemp --suffix=.deb)
  local deb_url
  deb_url=$(curl -fsSL https://api.github.com/repos/rustdesk/rustdesk/releases/latest \
    | grep -oE '"browser_download_url": *"[^"]*x86_64\.deb"' | head -n1 \
    | sed -E 's/"browser_download_url": *"([^"]*)"/\1/')
  curl -fsSL -o "$tmp_deb" "$deb_url"
  sudo apt-get update
  sudo dpkg -i "$tmp_deb" || sudo apt-get install -f -y
  rm -f "$tmp_deb"

  # Das .deb-Postinst aktiviert automatisch einen systemd-Autostart -
  # widerspricht der Sicherheitslinie (RustDesk darf nicht dauerhaft
  # laufen, siehe sicherheit-datenschutz.md, Abschnitt "Fernwartung").
  sudo systemctl disable --now rustdesk
}

schritt_07_claude_cli() {
  log "Schritt 7: Claude Code CLI installieren"
  npm install -g @anthropic-ai/claude-code
}

schritt_08_piper() {
  log "Schritt 8: Piper statt espeak-ng"
  sudo apt-get install -y jq sox
  sudo mkdir -p /usr/local/share/dialos-piper/voices

  if [ ! -x /usr/local/share/dialos-piper/piper/piper ]; then
    curl -s -L -o /tmp/piper.tar.gz "https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz"
    sudo tar -xzf /tmp/piper.tar.gz -C /usr/local/share/dialos-piper
    rm -f /tmp/piper.tar.gz
  fi
  if [ ! -f /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx ]; then
    curl -s -L -o /tmp/thorsten.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx?download=true"
    curl -s -L -o /tmp/thorsten.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json?download=true"
    sudo mv /tmp/thorsten.onnx /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx
    sudo mv /tmp/thorsten.onnx.json /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx.json
  fi
  sudo chmod -R a+rX /usr/local/share/dialos-piper
  sudo chmod +x /usr/local/share/dialos-piper/piper/piper

  sudo mkdir -p /etc/speech-dispatcher/modules
  sudo cp iso-build/config/includes.chroot/etc/speech-dispatcher/modules/piper-generic.conf /etc/speech-dispatcher/modules/
  sudo cp iso-build/config/includes.chroot/etc/speech-dispatcher/speechd.conf /etc/speech-dispatcher/speechd.conf
  pkill -f speech-dispatcher || true
}

schritt_09_gnome_erweiterungen() {
  log "Schritt 9: GNOME-Erweiterungen (Bluetooth Battery Monitor)"
  # AppIndicator + Desktop Icons NG kommen schon per Paketliste (Schritt
  # 2) + dconf-Defaults (Schritt 3) - nur Bluetooth Battery Monitor ist
  # eine nicht paketierte Drittanbieter-Erweiterung, die manuell in
  # dialosadmins eigenes Erweiterungsverzeichnis kopiert werden muss.
  mkdir -p ~/.local/share/gnome-shell/extensions
  cp -r "iso-build/config/includes.chroot/etc/skel/.local/share/gnome-shell/extensions/bluetooth-battery-monitor@v8v88v8v88.com" \
    ~/.local/share/gnome-shell/extensions/
  echo "Hinweis: Neue Erweiterungen werden unter Wayland erst nach einem echten Ab-/Anmelden erkannt."
}

schritt_10_standardprogramme() {
  log "Schritt 10: Standardprogramme setzen"
  sudo mkdir -p /usr/local/share/applications
  sudo cp iso-build/config/includes.chroot/usr/local/share/applications/org.gnome.Evolution.desktop /usr/local/share/applications/
  sudo cp iso-build/config/includes.chroot/usr/local/share/applications/org.gnome.Calendar.desktop /usr/local/share/applications/
  mkdir -p ~/.config
  cp iso-build/config/includes.chroot/etc/skel/.config/mimeapps.list ~/.config/mimeapps.list
  xdg-mime default thunderbird.desktop x-scheme-handler/mailto text/calendar

  sudo mkdir -p /usr/lib/firefox-esr/distribution
  sudo cp iso-build/config/includes.chroot/usr/lib/firefox-esr/distribution/policies.json /usr/lib/firefox-esr/distribution/

  mkdir -p ~/.config/gtk-3.0
  cp iso-build/config/includes.chroot/etc/skel/.config/gtk-3.0/bookmarks ~/.config/gtk-3.0/bookmarks
}

schritt_11_sprachausgabe() {
  log "Schritt 11: Sprachausgabe-Skripte"
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-say.py /usr/local/bin/
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-start-ansage.py /usr/local/bin/
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-tts-indicator.py /usr/local/bin/
  sudo chmod 755 /usr/local/bin/dialos-say.py /usr/local/bin/dialos-start-ansage.py /usr/local/bin/dialos-tts-indicator.py
  sudo mkdir -p /etc/xdg/autostart
  sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-start-ansage.desktop /etc/xdg/autostart/
  sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-tts-indicator.desktop /etc/xdg/autostart/
}

schritt_12_sicherheit() {
  log "Schritt 12: Sicherheits-Werkzeuge (nutzers Daten verschluesseln + Autologin-Gate)"
  sudo mkdir -p /usr/local/sbin
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-install /usr/local/sbin/
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-rekey /usr/local/sbin/
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh /usr/local/sbin/
  sudo chmod 755 /usr/local/sbin/dialos-install /usr/local/sbin/dialos-rekey \
    /usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/dialos-setup-home-partition.sh

  sudo mkdir -p /usr/share/applications
  sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-install.desktop /usr/share/applications/
  sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-rekey.desktop /usr/share/applications/

  sudo cp iso-build/config/includes.chroot/etc/systemd/system/dialos-stick-gate.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable dialos-stick-gate.service
}

schritt_14_bluetooth() {
  log "Schritt 14: Bluetooth-Kopplungsdaten übernehmen (optional, gerätespezifisch)"
  echo "ACHTUNG: nur sinnvoll, wenn dies dasselbe Testgerät wie vorher ist -" >&2
  echo "die Kopplungsdaten haengen an der MAC-Adresse des eingebauten" >&2
  echo "Bluetooth-Adapters. Auf einem neuen/anderen Geraet normal koppeln" >&2
  echo "statt dieses Schritts." >&2
  sudo cp -r "iso-build/config/includes.chroot/var/lib/bluetooth/." /var/lib/bluetooth/
}

schritt_15_vosk() {
  log "Schritt 15: Spracherkennung (Vosk + hassil)"
  sudo pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0

  if [ ! -d /usr/local/share/vosk-model-de-big ]; then
    curl -L -o /tmp/vosk-de-big.zip https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
    (cd /tmp && unzip -q vosk-de-big.zip)
    sudo mv /tmp/vosk-model-de-0.21 /usr/local/share/vosk-model-de-big
    rm -f /tmp/vosk-de-big.zip
  fi
  if [ ! -d /usr/local/share/vosk-model-de-small ]; then
    curl -L -o /tmp/vosk-de-small.zip https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
    (cd /tmp && unzip -q vosk-de-small.zip)
    sudo mv /tmp/vosk-model-small-de-0.15 /usr/local/share/vosk-model-de-small
    rm -f /tmp/vosk-de-small.zip
  fi

  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-vosk-test.py /usr/local/bin/
  sudo chmod 755 /usr/local/bin/dialos-vosk-test.py
}

# Vollstaendige Liste in Doku-Reihenfolge - 14_bluetooth ist bewusst
# NICHT Teil des normalen Laufs (device-spezifisch, siehe Funktion
# oben), nur per --bluetooth-kopplung zuschaltbar oder einzeln per
# "./dialos-full-office-setup.sh 14" aufrufbar.
ALLE_SCHRITTE=(02_paketliste 03_branding 04_autologin 05_calamares 06_rustdesk
  07_claude_cli 08_piper 09_gnome_erweiterungen 10_standardprogramme
  11_sprachausgabe 12_sicherheit 14_bluetooth 15_vosk)

main() {
  local bluetooth_kopplung=0
  local einzelschritt=""
  for arg in "$@"; do
    case "$arg" in
      --bluetooth-kopplung) bluetooth_kopplung=1 ;;
      *) einzelschritt="$arg" ;;
    esac
  done

  pruefe_netzwerk

  if [ -n "$einzelschritt" ]; then
    local treffer=""
    for schritt in "${ALLE_SCHRITTE[@]}"; do
      if [[ "$schritt" == "$einzelschritt"_* || "$schritt" == "$einzelschritt" ]]; then
        treffer="$schritt"
        break
      fi
    done
    if [ -z "$treffer" ]; then
      echo "Unbekannter Schritt '$einzelschritt'. Verfuegbar: ${ALLE_SCHRITTE[*]}" >&2
      exit 1
    fi
    "schritt_${treffer}"
    log "Fertig (nur Schritt $einzelschritt)."
    return
  fi

  for schritt in "${ALLE_SCHRITTE[@]}"; do
    if [ "$schritt" = "14_bluetooth" ] && [ "$bluetooth_kopplung" -ne 1 ]; then
      continue
    fi
    "schritt_${schritt}"
  done
  log "Fertig. Naechster Schritt: sudo /usr/local/sbin/dialos-setup-home-partition.sh (Sicherheits-Stick einstecken), danach sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin."
}

main "$@"
