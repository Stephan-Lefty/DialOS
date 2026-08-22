#!/bin/bash
# DialOS: Buero-Setup-Konsolidierungsskript. Fuehrt die Schritte 2-12,
# 14 (optional) und 15 aus docs/Debian-zu-DialOS.md automatisiert und
# der Reihe nach aus, statt sie manuell aus der Doku abzutippen.
#
# Deckt BEWUSST NICHT ab (siehe docs/Debian-zu-DialOS.md fuer den Grund):
#   Schritt 1  (Debian+GNOME-Basisinstallation) - manuell mit der
#              Debian-13-ISO von debian.org, legt dabei das Konto
#              "dialosadmin" an.
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

# NICHT mit "sudo" starten! Die Schritte 9 und 10 schreiben bewusst in "~"
# (GNOME-Erweiterung, Standardprogramme, Nautilus-Lesezeichen) - das muss
# dialosadmins Home sein. Unter sudo waere "~" = /root, die Dateien landeten
# dann lautlos im falschen Home: kein Fehler, keine Meldung, aber die
# Erweiterung und die Standardprogramme fehlen auf dem Konto, das sie
# braucht. Die Schritte, die Root-Rechte brauchen, rufen sudo selbst auf.
if [ "$(id -u)" -eq 0 ]; then
  echo "Dieses Skript NICHT als root/mit sudo starten, sondern direkt als" >&2
  echo "dialosadmin:" >&2
  echo "    ./scripts/dialos-full-office-setup.sh" >&2
  echo >&2
  echo "Grund: die Schritte 9 und 10 richten das BENUTZERKONTO ein (GNOME-" >&2
  echo "Erweiterung, Standardprogramme). Als root wuerden sie in /root statt" >&2
  echo "in /home/dialosadmin landen. Alles, was Root-Rechte braucht, ruft" >&2
  echo "sudo von selbst auf." >&2
  exit 1
fi

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

pruefe_sudo() {
  log "Sudo-Check"
  # Passwort einmal vorab abfragen, statt den Nutzer mitten im Lauf (evtl.
  # nach Minuten von Downloads) zu ueberraschen - und sofort abbrechen,
  # falls dieses Konto gar keine sudo-Rechte hat.
  if ! sudo -v; then
    echo "Keine sudo-Rechte fuer '$(id -un)' - dieses Skript braucht sie fuer" >&2
    echo "fast jeden Schritt. Gehoert das Konto zur Gruppe 'sudo'?" >&2
    exit 1
  fi
}

schritt_02_paketliste() {
  log "Schritt 2: Paketliste installieren"
  sudo apt-get update
  sudo xargs -a iso-build/config/package-lists/desktop.list.chroot apt-get install -y
}

schritt_02b_sprachen_aufraeumen() {
  log "Schritt 2b: Fremdsprachige Eingabemethoden entfernen"
  # WARUM DAS NOETIG IST: Schritt 1 der Doku sagt "Standard-Debian-
  # Installation, GNOME als Desktop waehlen". Genau diese Auswahl
  # installiert das Metapaket task-gnome-desktop - dasselbe Paket, vor dem
  # Schritt 2 ausdruecklich warnt. Ueber dessen Recommends kommen die
  # task-*-Pakete praktisch aller von Debian unterstuetzten Sprachen mit
  # herein, darunter task-japanese samt ibus-mozc/ibus-anthy.
  #
  # Folge auf dem echten Geraet (gemessen 2026-08-16, erster Aufbau):
  # ~140 task-Pakete installiert, und GNOME setzte die Tastatur auf
  # Japanisch (Mozc) statt Deutsch - fuer BEIDE Konten. Die Doku kannte
  # die Falle, hatte aber nicht bemerkt, dass ihr eigener Schritt 1 sie
  # ausloest. Deshalb jetzt ein fester Schritt statt einer Fussnote.
  #
  # task-gnome-desktop selbst bleibt bewusst stehen: es haelt den
  # GNOME-Desktop zusammen. Entfernt werden nur die Sprachpakete.
  local behalten="task-desktop|task-gnome-desktop|task-laptop|task-german|task-german-desktop|task-english"
  local weg
  weg=$(dpkg-query -W -f='${Package} ${Status}\n' 'task-*' 2>/dev/null \
    | awk '/ok installed/{print $1}' | grep -vE "^($behalten)$" || true)

  if [ -n "$weg" ]; then
    echo "Entferne $(printf '%s\n' "$weg" | wc -l) fremdsprachige task-Pakete ..."
    # shellcheck disable=SC2086
    sudo apt-get purge -y $weg
  else
    echo "Keine fremdsprachigen task-Pakete gefunden - nichts zu tun."
  fi

  # Eingabemethoden explizit nachpurgen: sie sind es, die die Tastatur
  # umstellen, und autoremove erwischt sie nicht zuverlaessig.
  sudo apt-get purge -y ibus-anthy ibus-mozc anthy anthy-common \
    mozc-data mozc-server mozc-utils-gui 2>/dev/null || true
  sudo apt-get autoremove --purge -y

  # SICHERHEITSNETZ: "autoremove --purge" entfernt alles, was nach dem
  # Purge der Sprachpakete niemand mehr anfordert - und trifft dabei auch
  # Dinge, die wir sehr wohl wollen. Beim ersten echten Lauf am 2026-08-16
  # erwischte es gnome-accessibility-themes, ausgerechnet auf einem System
  # fuer Menschen mit Seheinschraenkung. Deshalb die Paketliste danach
  # erneut durchsetzen: sie ist die Quelle der Wahrheit, und alles darin
  # gilt anschliessend wieder als "manuell installiert" und ist damit vor
  # kuenftigem autoremove geschuetzt.
  echo "Stelle sicher, dass nichts aus der Paketliste mitentfernt wurde ..."
  sudo xargs -a iso-build/config/package-lists/desktop.list.chroot apt-get install -y

  # Der dauerhafte Teil der Loesung steckt in 01-dialos-defaults (Schritt
  # 3): dort ist die deutsche Tastatur als einzige Eingabequelle fuer JEDES
  # Konto hinterlegt. Das Aufraeumen hier entfernt nur, was gar nicht erst
  # haette installiert werden sollen.
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

  # Hier lag bis 2026-08-16 eine splash.png fuer den GRUB-/isolinux-
  # Bootbereich der von "eggs produce" gebauten Live-ISO. Penguins' Eggs
  # ist entfallen (Schritt 16), die Datei damit wirkungslos - das
  # Plymouth-Theme oben bringt seine eigene background.png mit.
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

schritt_05_calamares_entfernen() {
  log "Schritt 5: Calamares entfernen"
  # ENTSCHEIDUNG VOM 2026-08-16 (Stephan): Jedes Kundengeraet wird im
  # Buero aufgesetzt - ueber die Debian-13-ISO von debian.org plus die
  # drei DialOS-Skripte. Damit sieht nie jemand ausser Stephan einen
  # Installer, und Calamares hat keine Aufgabe mehr.
  #
  # Bis dahin war Calamares der Installer fuer den Live-Boot-Weg: die
  # DialOS-ISO wurde auf dem Kundengeraet gestartet, Calamares
  # installierte das System und entfernte sich danach per
  # shellprocess.conf selbst wieder. Der ganze Pflegeaufwand dafuer
  # (Branding-Ordner, locale.conf, shellprocess.conf, das
  # Penguins-Eggs-Vendor-Overlay und base.yaml.tmpl) entfaellt.
  #
  # Dieser Schritt heisst weiter "05", damit alle Querverweise auf die
  # spaeteren Schritte in Doku und Commit-Historie gueltig bleiben. Auf
  # einer frischen Debian-Installation findet er nichts vor und tut
  # nichts - er raeumt nur Geraete auf, die Calamares noch haben.
  if dpkg-query -W -f='${Status}' calamares 2>/dev/null | grep -q "ok installed"; then
    sudo apt-get purge -y calamares calamares-settings-debian
  else
    echo "Calamares ist nicht installiert - nichts zu entfernen."
  fi

  # Reste, die beim Purge stehen bleiben koennen bzw. von frueheren
  # DialOS-Versionen stammen.
  # /etc/penguins-eggs.d komplett: seit dem Wegfall von eggs (Schritt 16)
  # gibt es dort nichts mehr, was gebraucht wuerde.
  sudo rm -rf /etc/calamares /etc/penguins-eggs.d
  sudo rm -f /usr/local/share/applications/calamares-install-debian.desktop
  # Das Icon, das der frueher mitgelieferte Autostart auf jede
  # Arbeitsflaeche gelegt hat - auch auf die von "nutzer", dessen Home
  # 700 ist und dessen Glob sich deshalb nur als root aufloest.
  sudo sh -c 'rm -f /home/*/Desktop/calamares-install-debian.desktop'

  # Wie in Schritt 2b: nach autoremove die Paketliste erneut durchsetzen,
  # damit nichts Gewolltes mitgerissen wird.
  sudo apt-get autoremove --purge -y
  sudo xargs -a iso-build/config/package-lists/desktop.list.chroot apt-get install -y
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
  # "|| true": heisst die Unit in einer kuenftigen RustDesk-Version anders
  # oder fehlt sie, soll das nicht per "set -e" den kompletten Lauf (und
  # damit die Schritte 7-15) abbrechen - dann lieber weiterlaufen und den
  # Autostart im Nachgang pruefen.
  sudo systemctl disable --now rustdesk || true
}

schritt_07_claude_cli() {
  log "Schritt 7: Claude Code CLI installieren"
  # sudo ist Pflicht: Debians npm-Prefix ist /usr/local, dort darf
  # dialosadmin nicht schreiben. Ohne sudo bricht "npm install -g" mit
  # EACCES ab und reisst per "set -e" die Schritte 8-15 mit.
  sudo npm install -g @anthropic-ai/claude-code
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
  # Wachposten fuer die Synthese-Kette. piper-generic.conf ruft ihn in
  # GenericExecuteSynth als ERSTES Glied einer &&-Kette auf. Fehlte er
  # (bis 2026-08-16 war er weder im Repo noch dokumentiert), brach die
  # Kette sofort ab und es wurde NIE etwas synthetisiert - die
  # Sprachausgabe blieb vollstaendig stumm, ohne sichtbaren Fehler.
  sudo cp iso-build/config/includes.chroot/usr/local/share/dialos-piper/check_piper_voice.sh \
    /usr/local/share/dialos-piper/check_piper_voice.sh

  sudo chmod -R a+rX /usr/local/share/dialos-piper
  sudo chmod +x /usr/local/share/dialos-piper/piper/piper
  sudo chmod 755 /usr/local/share/dialos-piper/check_piper_voice.sh

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

  # Zusaetzlich nach /etc/skel, damit "nutzer" (Schritt 13) die Erweiterung
  # automatisch mitbekommt. Ergaenzt 2026-08-16: vorher wurde die Vorlage
  # aus dem Repo NUR in dialosadmins Home kopiert und /etc/skel des echten
  # Systems nie befuellt - "nutzer" hatte die Erweiterung damit nie, obwohl
  # die Doku sie als Standard fuer neue Konten beschreibt.
  sudo mkdir -p /etc/skel/.local/share/gnome-shell/extensions
  sudo cp -r "iso-build/config/includes.chroot/etc/skel/.local/share/gnome-shell/extensions/bluetooth-battery-monitor@v8v88v8v88.com" \
    /etc/skel/.local/share/gnome-shell/extensions/
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

  # Ebenfalls nach /etc/skel, aus demselben Grund wie in Schritt 9: sonst
  # bekommt "nutzer" weder Thunderbird als Standard-Mailprogramm noch die
  # Nautilus-Lesezeichen. Wichtig: hier landen NUR Nutzer-Voreinstellungen
  # in /etc/skel - die Admin-Skripte gehoeren ausdruecklich NICHT dorthin
  # (siehe scripts/README.md, Korrektur vom 2026-08-14).
  sudo mkdir -p /etc/skel/.config/gtk-3.0
  sudo cp iso-build/config/includes.chroot/etc/skel/.config/mimeapps.list /etc/skel/.config/mimeapps.list
  sudo cp iso-build/config/includes.chroot/etc/skel/.config/gtk-3.0/bookmarks /etc/skel/.config/gtk-3.0/bookmarks
}

schritt_11_sprachausgabe() {
  log "Schritt 11: Sprachausgabe-Skripte"
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-say.py /usr/local/bin/
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-start-ansage.py /usr/local/bin/
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-tts-indicator.py /usr/local/bin/
  sudo chmod 755 /usr/local/bin/dialos-say.py /usr/local/bin/dialos-start-ansage.py /usr/local/bin/dialos-tts-indicator.py

  # Umschaltung der Desktop-Optik (GNOME <-> Windows 11). Liegt hier, weil
  # sie wie die Ansagen jedem Konto zur Verfuegung stehen muss - auch
  # "nutzer", der spaeter per Sprachbefehl umschalten koennen soll.
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-desktop-stil.sh /usr/local/bin/
  sudo chmod 755 /usr/local/bin/dialos-desktop-stil.sh

  # Stimme umschalten in einem Aufruf (Michael <-> Anna). Braucht selbst kein
  # root - es ruft nur den privilegierten Teil ueber sudo auf und startet
  # danach speech-dispatcher in der SITZUNG neu, was root gar nicht koennte.
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-stimme-wechseln.py /usr/local/bin/
  sudo chmod 755 /usr/local/bin/dialos-stimme-wechseln.py
  # Eigenes Startknopf-Symbol fuer die Windows-Optik (generisches Fenster,
  # bewusst nicht Microsofts Markenzeichen - Begruendung in der Datei).
  sudo mkdir -p /usr/local/share/dialos
  sudo cp iso-build/config/includes.chroot/usr/local/share/dialos/dialos-fenster-symbolic.svg /usr/local/share/dialos/
  sudo chmod 644 /usr/local/share/dialos/dialos-fenster-symbolic.svg
  # Signalton fuer Fragen. Wird nur abgespielt, wenn der Nutzer ihn
  # eingeschaltet hat (~/.config/dialos/frageton) - Standard ist die
  # natuerliche Satzmelodie aus dem Fragezeichen.
  sudo cp iso-build/config/includes.chroot/usr/local/share/dialos/frage-ton.wav /usr/local/share/dialos/
  sudo chmod 644 /usr/local/share/dialos/frage-ton.wav

  # Mikrofon-Aufnahmepegel. MUSS vor dem Sprachbefehl kommen: Ab Werk
  # lagen auf dem T490 60 dB Verstaerkung an (Capture +30 dB UND Internal
  # Mic Boost +30 dB), das Signal klebte am Anschlag, und Vosk konnte
  # deshalb prinzipiell nichts erkennen - ohne Fehlermeldung. Details im
  # Skript.
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-mikrofon-pegel.sh /usr/local/sbin/
  sudo chmod 755 /usr/local/sbin/dialos-mikrofon-pegel.sh
  sudo cp iso-build/config/includes.chroot/etc/systemd/system/dialos-mikrofon-pegel.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now dialos-mikrofon-pegel.service

  # Echo-Unterdrueckung fuer das Mikrofon. MUSS vor dem Sprachbefehl
  # kommen: Ohne sie hoert der Dienst alles mit, was das Geraet abspielt
  # (eigene Ansage, Radio, Mediathek) und schaltet dadurch von selbst um.
  # Gemessen am 2026-08-17: 6,13 % Pegel roh gegenueber 0,15 % bereinigt.
  sudo mkdir -p /etc/pipewire/pipewire.conf.d
  sudo cp iso-build/config/includes.chroot/etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf /etc/pipewire/pipewire.conf.d/
  sudo chmod 644 /etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf
  systemctl --user restart pipewire pipewire-pulse wireplumber 2>/dev/null || true

  # Sprachbefehl "auf Linux/Windows umschalten" - der erste dauerhaft
  # lauschende Dienst in DialOS. Braucht Vosk aus Schritt 15; fehlt es,
  # beendet sich der Dienst mit einer Meldung, statt die Anmeldung
  # aufzuhalten.
  sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-sprachbefehl-desktop.py /usr/local/bin/
  sudo chmod 755 /usr/local/bin/dialos-sprachbefehl-desktop.py
  sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-sprachbefehl-desktop.desktop /etc/xdg/autostart/
  # Stellt beim Anmelden den zuletzt gewaehlten Desktop-Stil wieder her.
  # Fehlte bis 2026-08-17, obwohl die Doku ihn beschrieb.
  sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-desktop-stil-wiederherstellen.desktop /etc/xdg/autostart/

  # Deutsches Menue fuer ArcMenu. Debians Paket liefert die fertig
  # uebersetzte de.mo mit, legt sie aber nach po/ statt in einen
  # locale-Ordner - dort findet sie niemand, das Menue bleibt englisch.
  # GNOME-Erweiterungen ohne eigenen locale-Ordner suchen in
  # /usr/share/locale, also kommt sie dorthin. Kein msgfmt noetig, die
  # Datei ist bereits kompiliert.
  ARCMENU_MO="/usr/share/gnome-shell/extensions/arcmenu@arcmenu.com/po/de.mo"
  if [ -f "$ARCMENU_MO" ]; then
    sudo mkdir -p /usr/share/locale/de/LC_MESSAGES
    sudo cp "$ARCMENU_MO" /usr/share/locale/de/LC_MESSAGES/arcmenu.mo
    sudo chmod 644 /usr/share/locale/de/LC_MESSAGES/arcmenu.mo
  fi
  sudo mkdir -p /etc/xdg/autostart
  sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-start-ansage.desktop /etc/xdg/autostart/
  sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-tts-indicator.desktop /etc/xdg/autostart/

  # Standortabfrage fuers Wetter (GeoClue2) freischalten - Pflicht, sonst
  # "AccessDenied: Geolocation disabled" (live am 2026-08-14 gefunden).
  # Nur anhaengen, nicht die ganze Datei ueberschreiben - sonst gehen
  # Debians eigene Standard-Eintraege fuer andere Apps verloren.
  if ! sudo grep -q "^\[dialos-start-ansage\]" /etc/geoclue/geoclue.conf 2>/dev/null; then
    printf '\n[dialos-start-ansage]\nallowed=true\nsystem=true\nusers=\n' \
      | sudo tee -a /etc/geoclue/geoclue.conf > /dev/null
  fi
}

schritt_11c_admin_tastenkuerzel() {
  log "Schritt 11c: Tastenkombinationen fuer das Admin-Konto"

  # Die Regel erlaubt dialosadmin, die Stimme ohne Passwort umzustellen.
  # Hinter einer Taste ist eine Passwortabfrage kein Schutz, sondern ein
  # Abbruch: Das Fenster erscheint, hat keinen Fokus, nichts passiert.
  # Eng gefasst - zwei woertliche Aufrufe, kein Platzhalter, und das Skript
  # gehoert root. Die Begruendung steht ausfuehrlich in der Datei selbst.
  sudo install -o root -g root -m 0440 \
    iso-build/config/includes.chroot/etc/sudoers.d/dialos-stimme \
    /etc/sudoers.d/dialos-stimme

  # NUR fuer das Admin-Konto. "nutzer" bedient beides ueber die Stimme; eine
  # Tastenkombination waere dort ein Weg, den niemand findet.
  ./scripts/dialos-admin-tastenkuerzel.sh
}

schritt_12_sicherheit() {
  log "Schritt 12: Sicherheits-Werkzeuge (nutzers Daten verschluesseln + Autologin-Gate)"
  # dialos-install ist am 2026-08-16 entfallen (siehe Schritt 5): es war
  # der Installer fuer den Live-Boot-Weg - Zielplatte loeschen, neu
  # partitionieren, das laufende System per rsync klonen, GRUB setzen.
  # Bei Weg A erledigen das der Debian-Installer und diese drei Skripte.
  # Seine LUKS-/Stick-Logik lebt unveraendert in
  # dialos-setup-home-partition.sh weiter, das daraus abgeleitet wurde.
  #
  # dialos-rekey BLEIBT: es ersetzt einen verlorenen oder defekten
  # Sicherheits-Stick und ist damit ein Wartungswerkzeug, kein Installer.
  sudo mkdir -p /usr/local/sbin
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-rekey /usr/local/sbin/
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/
  sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh /usr/local/sbin/
  sudo chmod 755 /usr/local/sbin/dialos-rekey \
    /usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/dialos-setup-home-partition.sh
  # Reste einer frueheren DialOS-Version wegraeumen.
  sudo rm -f /usr/local/sbin/dialos-install /usr/share/applications/dialos-install.desktop
  sudo sh -c 'rm -f /home/*/Desktop/dialos-install.desktop'

  sudo mkdir -p /usr/share/applications
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
ALLE_SCHRITTE=(02_paketliste 02b_sprachen_aufraeumen 03_branding 04_autologin 05_calamares_entfernen 06_rustdesk
  07_claude_cli 08_piper 09_gnome_erweiterungen 10_standardprogramme
  11_sprachausgabe 11c_admin_tastenkuerzel 12_sicherheit 14_bluetooth 15_vosk)

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
  pruefe_sudo

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
  log "Fertig (Schritte 2-12 + 15)."
  cat <<'HINWEIS'

Noch zwei Befehle bis zum fertigen DialOS:

  2) Sicherheits-Stick einstecken, dann OHNE sudo starten (das Skript holt
     sich die Rechte selbst per pkexec - unter "sudo" fehlt ihm die
     Grafik-Umgebung fuer seine Dialoge):

       /usr/local/sbin/dialos-setup-home-partition.sh

  3) Stick STECKEN LASSEN, dann:

       sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin

Danach einmal neu starten. Hinweis: neu installierte GNOME-Erweiterungen
werden unter Wayland erst nach einem echten Ab-/Anmelden aktiv.
HINWEIS
}

main "$@"
