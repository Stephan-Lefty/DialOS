# DialOS manuell über Cubic bauen

Für den Fall, dass die automatisierte Docker/live-build-Pipeline
(`build.sh`) weiter Probleme macht: Diese Anleitung baut dieselbe
Konfiguration manuell über [Cubic](https://github.com/PJ-Singh-001/Cubic)
nach, mit direktem visuellem Feedback statt blinder Log-Auswertung.

## 1. Basis-ISO besorgen

Offizielle Debian-13-Live-ISO (GNOME) laden:
https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/

Datei mit `debian-live-13.*-amd64-gnome.iso` im Namen.

## 2. In Cubic laden

Projektordner: `/mnt/HDD-1.0TB/TEMP` (wie besprochen). Die
heruntergeladene ISO als Quelle auswählen.

## 3. Pakete installieren

Im Cubic-Terminal (läuft direkt in der Chroot-Umgebung):

```sh
apt-get update
apt-get install -y --no-install-recommends \
  task-gnome-desktop gnome-core gdm3 orca espeak-ng plymouth plymouth-themes \
  network-manager network-manager-gnome firmware-linux-free firmware-iwlwifi \
  firmware-misc-nonfree intel-microcode \
  firefox-esr thunderbird shortwave rhythmbox gnome-podcasts libreoffice-writer \
  gnome-terminal curl wget git nodejs npm dconf-cli \
  zenity polkitd pkexec parted dosfstools cryptsetup cryptsetup-initramfs \
  rsync grub-efi-amd64 grub-efi-amd64-bin
```

Falls `dictionaries-common` (Abhängigkeit von gnome-text-editor) beim
Postinst meckert: meist reicht `dbus-daemon --system &` einmal manuell
zu starten, bevor die Pakete installiert werden - in Cubics
Chroot-Terminal läuft normalerweise (anders als in unserer
verschachtelten Docker-Umgebung) bereits ein funktionierendes
Basissystem, das Problem sollte hier gar nicht erst auftreten.

## 4. Standard-Benutzer + Autologin

```sh
adduser --disabled-password --gecos "" nutzer
usermod -aG sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom nutzer
passwd nutzer   # eigenes Passwort setzen statt Zufallspasswort

mkdir -p /etc/gdm3
cat > /etc/gdm3/custom.conf <<'EOF'
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=nutzer
EOF
```

## 5. RustDesk installieren

```sh
DEB_URL=$(curl -fsSL https://api.github.com/repos/rustdesk/rustdesk/releases/latest \
  | grep -oE '"browser_download_url": *"[^"]*x86_64\.deb"' | head -n1 \
  | sed -E 's/"browser_download_url": *"([^"]*)"/\1/')
curl -fsSL -o /tmp/rustdesk.deb "$DEB_URL"
dpkg -i /tmp/rustdesk.deb || apt-get install -f -y
rm -f /tmp/rustdesk.deb
```

## 6. Claude Code CLI installieren

```sh
npm install -g @anthropic-ai/claude-code
```

## 7. Branding-Dateien kopieren

Diese Dateien aus dem Repo direkt über Cubics Dateimanager (oder `cp`
im Terminal, falls das Repo im Chroot erreichbar gemountet ist) an die
gleiche Stelle im Zielsystem kopieren:

- `config/includes.chroot/etc/os-release`
- `config/includes.chroot/etc/gdm3/custom.conf` (falls nicht schon manuell erledigt)
- `config/includes.chroot/usr/share/pixmaps/distributor-logo.png`
- `config/includes.chroot/usr/share/backgrounds/dialos/` (kompletter Ordner)
- `config/includes.chroot_before_packages/etc/dconf/db/local.d/` (beide Dateien)
- `config/includes.chroot_before_packages/etc/dconf/profile/user`
- `config/includes.chroot_before_packages/usr/share/plymouth/themes/dialos/` (kompletter Ordner)
- `config/includes.chroot/usr/local/sbin/dialos-install` und `dialos-keyscript` (ausführbar machen: `chmod +x`)
- `config/includes.chroot/usr/share/applications/dialos-install.desktop`
- `config/includes.chroot/etc/initramfs-tools/hooks/dialos-keyscript` (ausführbar machen)

Danach im Chroot-Terminal:

```sh
dconf update
plymouth-set-default-theme -R dialos
update-initramfs -u
```

## 8. ISO erstellen

Über Cubics eigenen "Generate"-Schritt am Ende des Assistenten.

## Danach

Das Ergebnis genauso wie beim automatisierten Weg testen: ISO auf
Stick schreiben (z. B. mit KDE ISO Image Writer), auf dem T490 booten.
