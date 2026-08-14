[Deutsch](Debian-zu-DialOS.md) | [English](Debian-zu-DialOS.en.md)

# Aufbauanleitung: Von Debian 13 + GNOME 48 zu DialOS 0.5.0

> **Pflegehinweis:** Dieses Dokument ist das lückenlose "von Grund auf
> nachbauen"-Rezept, nicht nur ein historischer Rückblick. Bei jeder
> künftigen Änderung, die den Aufbau eines Geräts betrifft (neues
> Paket, neue Branding-/Konfigurationsdatei, geänderter Befehl,
> Bugfix an einem der hier referenzierten Skripte), muss dieses
> Dokument **zusätzlich zum Änderungsprotokoll** in README.md
> aktualisiert werden - sonst driftet es auseinander und ist beim
> nächsten Neuaufbau nicht mehr vertrauenswürdig. Ziel: bei der finalen
> DialOS-Version soll sich das System aus dieser einen Datei heraus
> lückenlos nachbauen lassen.

Diese Anleitung fasst alle Schritte zusammen, die bisher über viele
einzelne Chat-Sessions verteilt zum aktuellen Stand (0.5.0) geführt
haben - in der Reihenfolge, in der sie tatsächlich sinnvoll sind, damit
sich DialOS aus einer frischen Debian-13/GNOME-Installation heraus
nachvollziehbar und reproduzierbar wieder aufbauen lässt. Transparenz
ist der Zweck: nichts hier ist neu erfunden, alles verweist auf die
Datei/den Commit/die Doku, aus der es stammt.

**Wichtig zum Kontext:** Es gibt zwei parallele Bau-Wege im Repo (siehe
`CLAUDE.md`):
1. Eine ältere Docker/live-build-Pipeline (`iso-build/build.sh`) - blieb
   nach ca. 18 Versuchen ohne eine einzige fertige ISO, wird aktuell
   nicht weiterverfolgt.
2. **Der hier beschriebene, aktuell genutzte Weg:** Debian 13 + GNOME
   wird direkt auf echter Hardware installiert und interaktiv
   eingerichtet (kein Chroot, kein Docker), die Dateien unter
   `iso-build/config/includes.chroot*/` im Repo dienen dabei als
   **Vorlage/Rezept, kein automatischer Build-Input** - jede Datei muss
   nach einer Änderung manuell auf das echte System kopiert werden.
   Am Ende wird mit [Penguins' Eggs](https://penguins-eggs.net/) eine
   startfähige ISO aus dem fertig eingerichteten System gezogen
   (`eggs produce`).

Diese Anleitung beschreibt Weg 2. Referenz-Testgerät: Lenovo ThinkPad
T490 (siehe [hardware.md](hardware.md)).

## 0. Voraussetzungen

- Debian-13-("Trixie")-Installationsmedium mit GNOME-Desktop
  (Standard-Debian-Installer reicht, Calamares kommt erst später als
  eigener Installer für die *nächste* Installation ins Spiel). Debian
  13 bringt GNOME 48 mit (getesteter Stand: GNOME Shell 48.7,
  Paketversion `48.7-0+deb13u2`, per `gnome-shell --version` geprüft) -
  kein separater Schritt nötig, das ist einfach die Version, die mit
  Trixie kommt.
- Root-/Sudo-Zugriff auf dem Zielsystem.
- Internetverbindung (für `apt`, `npm`, Modell-Downloads).
- Dieses Repository lokal verfügbar (am besten auf einer externen
  Platte, siehe "Praxishinweis: externe Platte" unten).

## 1. Debian 13 + GNOME installieren

Standard-Debian-Installation, GNOME als Desktop wählen. Das erste
angelegte Konto (der Installer verlangt eines) sollte **`DialOS-Admin`**
bzw. auf diesem Testgerät praktisch **`dialosadmin`** heißen -
Konvention: Das Admin-/Setup-Konto trägt bei jedem Rollout denselben
Namen, damit Skripte und Doku nicht pro Gerät angepasst werden müssen.

Zeitzone: `Europe`/`Berlin` als Standard (siehe Schritt 5, Calamares
übernimmt das später automatisch für Kundeninstallationen).

## 2. Paketliste installieren

Die vollständige, aktuelle Paketliste steht in
[`iso-build/config/package-lists/desktop.list.chroot`](../iso-build/config/package-lists/desktop.list.chroot).
Installieren mit:

```bash
sudo apt-get update
sudo xargs -a iso-build/config/package-lists/desktop.list.chroot apt-get install -y
```

Wichtige Gruppen darin (Reihenfolge wie in der Datei):
- **Sprache/Desktop-Basis**: `task-german`, `task-german-desktop`,
  `gnome-core`, `gdm3`, `orca` (Screenreader), `espeak-ng` (wird später
  durch Piper ersetzt, siehe Schritt 8), `plymouth` + `plymouth-themes`.
- **Netzwerk/Firmware**: `network-manager` + GUI, Firmware-Pakete fürs
  T490 (WLAN/Mikrocode).
- **Programme**: Firefox, Thunderbird, Shortwave (Radio), Rhythmbox,
  GNOME Podcasts, LibreOffice Writer.
- **Terminal/Entwicklung**: `gnome-terminal`, `curl`, `wget`, `git`,
  `nodejs`/`npm` (für Claude Code CLI, Schritt 7), `dconf-cli`.
- **Installer-/Sicherheits-Werkzeuge**: `zenity`, `polkitd`, `pkexec`,
  `parted`, `dosfstools`, `cryptsetup` + `cryptsetup-initramfs`,
  `rsync`, `grub-efi-amd64` (+ `-bin`), `openssl`,
  `systemd-timesyncd` (NTP, wichtig für den späteren Installer),
  `thunderbird-l10n-de`, `gnome-shell-extension-manager`.

**Bewusst NICHT verwenden:** `task-gnome-desktop` (Tasksel-Metapaket) -
zog in einem früheren Versuch über Recommends praktisch alle ~70
von Debian unterstützten Sprachen inklusive japanischer
Eingabemethoden mit rein und überstimmte damit den deutschen
GNOME-Standard (siehe README.md, Änderungsprotokoll 0.4.0-Vorstufe /
CLAUDE.md). Nach einem versehentlichen `task-gnome-desktop`-Einsatz:
alle `task-*`-Pakete außer `task-desktop`, `task-gnome-desktop`,
`task-laptop`, `task-german`, `task-german-desktop`, `task-english`
per `apt-get purge`+`autoremove` entfernen, `ibus-anthy`/`ibus-mozc`/
`anthy` explizit nachpurgen, danach
`gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'de')]"`.

## 3. Branding einspielen

Alle Branding-Assets liegen fertig aufbereitet unter
[`assets/`](../assets/) und im ISO-Rezept. Zielpfade:

```bash
sudo mkdir -p /usr/share/backgrounds/dialos
sudo cp iso-build/config/includes.chroot/usr/share/backgrounds/dialos/*.png /usr/share/backgrounds/dialos/
sudo cp assets/mark.png /usr/share/pixmaps/distributor-logo.png   # 512x512, Login-Logo + Avatar-Vorlage
sudo cp iso-build/config/includes.chroot/etc/os-release /etc/os-release
```

**dconf-Branding/-Defaults** (Wallpaper, Login-Logo, Mausbeschleunigung,
Akku-Prozentanzeige, Standard-Erweiterungen) - Dateien aus
[`iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/`](../iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/)
übernehmen und aktivieren:

```bash
sudo mkdir -p /etc/dconf/db/local.d /etc/dconf/profile
sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/00-dialos-branding /etc/dconf/db/local.d/
sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/01-dialos-defaults /etc/dconf/db/local.d/
sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/profile/user /etc/dconf/profile/
sudo dconf update
```

**Plymouth-Bootsplash:**

```bash
sudo mkdir -p /usr/share/plymouth/themes/dialos
sudo cp iso-build/config/includes.chroot_before_packages/usr/share/plymouth/themes/dialos/* /usr/share/plymouth/themes/dialos/
sudo plymouth-set-default-theme -R dialos
```

**Wichtige Falle:** `plymouth-set-default-theme -R dialos` allein
reicht nicht - ohne das Kernel-Boot-Argument `splash` bleibt Plymouth im
Text-Modus, egal welches Theme aktiv ist:

```bash
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/' /etc/default/grub
sudo update-grub
```

Verifikation erst nach einem echten Neustart möglich (Splash zwischen
Firmware-Logo und Anmeldung/Desktop).

**Boot-Hintergrund von `eggs produce` selbst (GRUB/isolinux, Live-ISO):**
Getrennt vom Plymouth-Theme oben kopiert `eggs produce` beim Bauen
zusätzlich `/etc/penguins-eggs.d/brain.d/assets/splash.png` als
Hintergrundbild in den GRUB- und isolinux-Bootbereich der fertigen
Live-ISO - das ist die Grafik, die ganz am Anfang beim Booten von der
ISO erscheint, noch vor Plymouth. Ohne eigene Datei zeigt das Paket
`eggs` dort standardmäßig ein Pinguin-Foto:

```bash
sudo mkdir -p /etc/penguins-eggs.d/brain.d/assets
sudo cp iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/splash.png /etc/penguins-eggs.d/brain.d/assets/splash.png
```

Nutzt dieselbe schon komprimierte Datei wie das Plymouth-Theme oben
(~2 MB statt der 14,7-MB-Rohversion aus `assets/`). **Noch nicht per
echtem Live-Boot verifiziert**, ob die Auflösung (2559×1440) im
isolinux-Kontext (traditionell 640×480-VESA-Erwartung) sauber
skaliert/zentriert wird oder verzerrt/beschnitten erscheint - beim
nächsten Live-Boot-Test mit prüfen, ggf. auf 640×480 zuschneiden falls
nötig.

## 4. Autologin einrichten

**Zentrale Falle:** `/etc/gdm3/custom.conf` (`AutomaticLogin=nutzer`,
siehe [Datei im Repo](../iso-build/config/includes.chroot/etc/gdm3/custom.conf))
ist bei dieser Debian-13/GDM-48-Kombination **nicht** der wirksame
Schalter - der eigentliche Mechanismus ist eine Pro-Benutzer-Eigenschaft
im laufenden AccountsService, per D-Bus gesetzt:

```bash
# Objekt-Pfad des Zielbenutzers ermitteln
sudo gdbus call --system --dest org.freedesktop.Accounts \
  --object-path /org/freedesktop/Accounts \
  --method org.freedesktop.Accounts.FindUserByName <benutzername>
# liefert z.B. /org/freedesktop/Accounts/User1001

# Autologin aktivieren
sudo gdbus call --system --dest org.freedesktop.Accounts \
  --object-path /org/freedesktop/Accounts/User1001 \
  --method org.freedesktop.Accounts.User.SetAutomaticLogin true
```

Ganz am Anfang (bevor `nutzer` überhaupt existiert, siehe Schritt 12)
bekommt das Admin-Konto (`dialosadmin`) testweise Autologin, damit man
am System arbeiten kann. Details und Begründung:
[sicherheit-datenschutz.md](sicherheit-datenschutz.md), Abschnitt
"Automatische Anmeldung".

## 5. Calamares-Installer einrichten

Zweck: eigener grafischer Installer für **künftige** Installationen
(nicht für dieses laufende System) mit DialOS-Branding und
Selbstentfernung nach der Installation.

```bash
sudo apt-get install -y calamares calamares-settings-debian
```

Deutsch läuft automatisch mit (Calamares bettet seine
Kern-Übersetzungen als Qt-Ressourcen ein und folgt der System-Locale -
kein Zusatzaufwand nötig, sofern das System auf Deutsch läuft).

Branding übernehmen (`calamares-settings-debian` liefert
`/etc/calamares/branding/debian/` als Vorlage; die fertige
`dialos`-Variante liegt schon im Repo):

```bash
sudo cp -r iso-build/config/includes.chroot/etc/calamares/branding/dialos /etc/calamares/branding/
sudo cp iso-build/config/includes.chroot/etc/calamares/modules/locale.conf /etc/calamares/modules/
sudo cp iso-build/config/includes.chroot/etc/calamares/modules/shellprocess.conf /etc/calamares/modules/
sudo sed -i 's/^branding: debian/branding: dialos/' /etc/calamares/settings.conf
```

**Wichtige Fallen dabei:**
- `componentName` in `branding.desc` muss exakt dem Ordnernamen
  entsprechen (`dialos`) - sonst Fatal-Error beim Start.
- `locale.conf` fehlt im Debian-Paket komplett; ohne diese Datei
  schlägt Calamares' eingebauter Standardwert `America/New_York` als
  Standort vor (kein GeoIP-Fehler, GeoIP ist schlicht nicht
  konfiguriert). Mit der Datei: `region: Europe` / `zone: Berlin` fest.
- `shellprocess.conf` macht zwei Dinge **nur im chroot des NEU
  installierten Zielsystems** (`dontChroot: false`): Linkshänder-Maus
  für das Admin-Konto setzen, und Calamares von der fertigen Installation
  wieder entfernen (`apt-get purge calamares calamares-settings-debian`)
  - dieser Schritt darf niemals auf der Live-Vorlage selbst laufen,
    sonst hätte die nächste ISO gar keinen Installer mehr.
- `stylesheet.qss` (Schriftfarbe im Hauptbereich) gab es im
  `debian`-Branding nicht - ist neu, wird automatisch erkannt, sobald
  sie im Komponenten-Ordner liegt.

**Penguins'-Eggs-Vendor-Overlay** (wichtig, sonst überschreibt
`eggs sysinstall` das Branding beim Live-Boot wieder mit generischem
"eggs"-Look):

```bash
sudo mkdir -p /etc/penguins-eggs.d/brain.d/assets/calamares
sudo cp -r iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/calamares/. /etc/penguins-eggs.d/brain.d/assets/calamares/
```

Hier heißt `componentName` in der Kopie bewusst `eggs` statt `dialos`
(der Zielordner, den `eggs sysinstall` erwartet, heißt immer `eggs`).

**Live-Installer-Icon umbenennen** ("DialOS installieren" statt
"Install System"/Ei-Icon) - `eggs produce` rendert
`/usr/share/applications/install-system.desktop` bei **jedem Build**
neu aus einem eigenen Template, ein einfaches Überschreiben der Datei
reicht also nicht:

```bash
sudo cp iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/base.yaml.tmpl /etc/penguins-eggs.d/brain.d/base.yaml.tmpl
```

## 6. RustDesk installieren (und deaktivieren)

```bash
cd /tmp
DEB_URL=$(curl -fsSL https://api.github.com/repos/rustdesk/rustdesk/releases/latest \
  | grep -oE '"browser_download_url": *"[^"]*x86_64\.deb"' | head -n1 \
  | sed -E 's/"browser_download_url": *"([^"]*)"/\1/')
curl -fsSL -o rustdesk.deb "$DEB_URL"
sudo apt-get update
sudo dpkg -i rustdesk.deb || sudo apt-get install -f -y
rm -f rustdesk.deb
```

**Wichtig:** Das `.deb`-Postinst aktiviert automatisch einen
systemd-Autostart - das widerspricht der Sicherheitslinie
(RustDesk darf nicht dauerhaft laufen, siehe
[sicherheit-datenschutz.md](sicherheit-datenschutz.md), Abschnitt
"Fernwartung"). Korrigieren:

```bash
sudo systemctl disable --now rustdesk
```

## 7. Claude Code CLI installieren

```bash
npm install -g @anthropic-ai/claude-code
```

(`EBADENGINE`-Warnung wegen Node-Version ist ignorierbar, funktioniert
trotzdem.) Für die Desktop-App: kein fester Installationsschritt, das
`.deb` wird stattdessen bei jedem Büro-Setup frisch heruntergeladen und
auf den Desktop jedes neuen Kontos gelegt (siehe Schritt 12).

## 8. Piper statt espeak-ng (natürlichere Sprachausgabe)

Systemweite Installation (nicht pro Benutzer), damit auch neue Kunden-
konten es automatisch bekommen:

```bash
sudo apt-get install -y jq sox
sudo mkdir -p /usr/local/share/dialos-piper/voices
curl -s -L -o /tmp/piper.tar.gz "https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz"
sudo tar -xzf /tmp/piper.tar.gz -C /usr/local/share/dialos-piper
curl -s -L -o /tmp/thorsten.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx?download=true"
curl -s -L -o /tmp/thorsten.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json?download=true"
sudo mv /tmp/thorsten.onnx /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx
sudo mv /tmp/thorsten.onnx.json /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx.json
sudo chmod -R a+rX /usr/local/share/dialos-piper
sudo chmod +x /usr/local/share/dialos-piper/piper/piper
```

Konfiguration aus dem Repo übernehmen:

```bash
sudo mkdir -p /etc/speech-dispatcher/modules
sudo cp iso-build/config/includes.chroot/etc/speech-dispatcher/modules/piper-generic.conf /etc/speech-dispatcher/modules/
sudo cp iso-build/config/includes.chroot/etc/speech-dispatcher/speechd.conf /etc/speech-dispatcher/speechd.conf
```

`DefaultVoice de_DE-thorsten-high`, `GenericRateMultiply 0.85`
(Sprechtempo, Stephans persönliche Präferenz - siehe TODO.md, sollte
später einstellbar werden). Nach Config-Änderungen laufende
`speech-dispatcher`-Prozesse beenden, damit sie neu mit aktueller
Config starten: `pkill -f speech-dispatcher`.

## 9. GNOME-Erweiterungen

- **Bluetooth Battery Monitor** (Akkustand-Anzeige für Bluetooth-Geräte
  in der oberen Leiste): Dateien liegen fertig unter
  [`iso-build/config/includes.chroot/etc/skel/.local/share/gnome-shell/extensions/bluetooth-battery-monitor@v8v88v8v88.com/`](../iso-build/config/includes.chroot/etc/skel/.local/share/gnome-shell/extensions/bluetooth-battery-monitor@v8v88v8v88.com/) -
  nach `~/.local/share/gnome-shell/extensions/` kopieren (bzw. via
  `/etc/skel/` für neue Konten automatisch), Aktivierung steckt schon in
  `01-dialos-defaults` (Schritt 3).
- **AppIndicator-Support** (für die Sprachausgabe-Aktiv-Anzeige,
  Schritt 11): Paket `gnome-shell-extension-appindicator`
  (UUID `ubuntu-appindicators@ubuntu.com`) sowie
  `gir1.2-ayatanaappindicator3-0.1` - inzwischen Teil der Paketliste
  (Schritt 2), Aktivierung steckt in `01-dialos-defaults` (Schritt 3).
- **Desktop Icons NG (DING)** (`gnome-shell-extension-desktop-icons-ng`,
  UUID `ding@rastersoft.com`): GNOME zeigt seit Jahren von Haus aus
  keine Icons mehr auf der Arbeitsfläche - ohne diese Erweiterung wären
  die Skripte aus Schritt 13 zwar im `~/Desktop/`-Ordner, aber nicht
  sichtbar. Ebenfalls Teil der Paketliste, Aktivierung + die drei
  Einstellungen `show-home`/`show-trash`/`show-volumes` auf `false`
  (nur die tatsächlich abgelegten Dateien sollen sichtbar sein, keine
  Papierkorb-/Persönlicher-Ordner-/Laufwerks-Icons) stecken in
  `01-dialos-defaults` (Schritt 3). **Wichtige Falle:** Eine schon
  laufende GNOME-Shell-Sitzung erkennt neu installierte Erweiterungen
  unter Wayland erst nach einem echten Ab-/Anmelden (kein Live-Neuladen
  wie früher unter X11) - nach der Installation einmal neu anmelden.

## 10. Standardprogramme setzen

Thunderbird statt Evolution/GNOME-Kalender, ohne die an
`gnome`/`gnome-core` gekoppelten Pakete zu entfernen (das würde fast
den ganzen Desktop mitreißen):

```bash
sudo mkdir -p /usr/local/share/applications
sudo cp iso-build/config/includes.chroot/usr/local/share/applications/org.gnome.Evolution.desktop /usr/local/share/applications/
sudo cp iso-build/config/includes.chroot/usr/local/share/applications/org.gnome.Calendar.desktop /usr/local/share/applications/
mkdir -p ~/.config
cp iso-build/config/includes.chroot/etc/skel/.config/mimeapps.list ~/.config/mimeapps.list
xdg-mime default thunderbird.desktop x-scheme-handler/mailto text/calendar
```

(`/usr/local/share/applications/*.desktop` mit `NoDisplay=true`
überschreiben die Standard-Einträge, ohne dass `apt`/`dpkg` sie je
anfasst - übersteht künftige Debian-Updates.)

Firefox-Startseite per Enterprise-Policy:

```bash
sudo mkdir -p /usr/lib/firefox-esr/distribution
sudo cp iso-build/config/includes.chroot/usr/lib/firefox-esr/distribution/policies.json /usr/lib/firefox-esr/distribution/
```

Nautilus-Lesezeichen zu `/usr/local/bin`:

```bash
cp iso-build/config/includes.chroot/etc/skel/.config/gtk-3.0/bookmarks ~/.config/gtk-3.0/bookmarks
```

## 11. Sprachausgabe-Skripte

Drei zusammenspielende Skripte, alle unter
[`iso-build/config/includes.chroot/usr/local/bin/`](../iso-build/config/includes.chroot/usr/local/bin/):

```bash
sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-say.py /usr/local/bin/
sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-start-ansage.py /usr/local/bin/
sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-tts-indicator.py /usr/local/bin/
sudo chmod 755 /usr/local/bin/dialos-say.py /usr/local/bin/dialos-start-ansage.py /usr/local/bin/dialos-tts-indicator.py
sudo mkdir -p /etc/xdg/autostart
sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-start-ansage.desktop /etc/xdg/autostart/
sudo cp iso-build/config/includes.chroot/etc/xdg/autostart/dialos-tts-indicator.desktop /etc/xdg/autostart/
```

- `dialos-say.py`: wiederverwendbares Sprachausgabe-Skript mit
  Audio-Ducking (mutet andere Audioquellen für die Dauer der Ansage).
- `dialos-start-ansage.py` ("Michael"): läuft bei jedem Login, begrüßt,
  nennt Datum/Uhrzeit, Akkustände (kontobasiert gefiltert - `nutzer`
  bekommt nur Laptop+Lautsprecher, jedes andere Konto zusätzlich
  Maus/Tastatur), Wetter, verbindet Bluetooth-Geräte neu. Läuft danach
  im Hintergrund weiter (Netzwerk-Überwachung alle 90s). Enthält einen
  Ein-Instanz-Lock (verhindert doppelte Instanzen desselben Kontos) und
  ein Bluetooth-Debug-Log - siehe
  [offene-punkte.md](offene-punkte.md), Eintrag "Bluetooth-Lautsprecher
  ... nicht hörbar nach Login" für den Hintergrund. **Praxisregel dabei
  wichtig:** Kontowechsel immer über echtes Abmelden, nie über GNOME
  "Benutzer wechseln" (siehe
  [sicherheit-datenschutz.md](sicherheit-datenschutz.md)).
- `dialos-tts-indicator.py`: Panel-Icon, das anzeigt, wenn gerade
  gesprochen wird (braucht die AppIndicator-Erweiterung aus Schritt 9).

## 12. Sicherheits-Werkzeuge (Stick-Verschlüsselung)

```bash
sudo mkdir -p /usr/local/sbin
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-install /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-rekey /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-keyscript /usr/local/sbin/
sudo chmod 755 /usr/local/sbin/dialos-install /usr/local/sbin/dialos-rekey /usr/local/sbin/dialos-keyscript
sudo mkdir -p /etc/initramfs-tools/hooks
sudo cp iso-build/config/includes.chroot/etc/initramfs-tools/hooks/dialos-keyscript /etc/initramfs-tools/hooks/
sudo chmod 755 /etc/initramfs-tools/hooks/dialos-keyscript
sudo mkdir -p /usr/share/applications
sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-install.desktop /usr/share/applications/
sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-rekey.desktop /usr/share/applications/
```

Was diese Werkzeuge tun: siehe
[sicherheit-datenschutz.md](sicherheit-datenschutz.md) (Konzept) und
den ausführlichen Walkthrough weiter unten in diesem Repo (README-
Änderungsprotokoll 0.5.0) für den aktuellen Stand (separates
Backup-Passwort, Mindestlänge, `DIALOS-KEY`+`DIALOS-DATA`-
Stick-Partitionierung). **Wichtige Rechte-Falle:** Dateien, die über
eine Geräte-Brücke/einen Editor neu geschrieben werden, landen oft mit
`600`-Rechten - `chmod +x` allein ergibt dann `711` (kein Leserecht für
andere), das Skript ist dann für andere Konten "nicht gefunden".
Immer `chmod 755` für Skripte, `chmod 644` für reine Dateien wie
`.desktop`/`.deb`.

## 13. Nutzer-Konto anlegen + Büro-Setup abschließen

Sammel-Skript, das drei Einzelschritte in einem Rutsch erledigt (siehe
[`scripts/README.md`](../scripts/README.md)):

```bash
sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
```

Das ruft nacheinander auf:
1. `dialos-set-avatar.sh` - setzt `distributor-logo.png` als Profilbild
   für das Admin-Konto (per `gdbus`/AccountsService `SetIconFile`).
2. `dialos-setup-nutzer.sh` - legt `nutzer` an (`adduser
   --disabled-password`, Gruppen `sudo,audio,video,plugdev,netdev,
   bluetooth,scanner,lpadmin,cdrom`, zufälliges Sudo-Passwort), schaltet
   Autologin von `dialosadmin` auf `nutzer` um (Wiederholungslogik gegen
   einen Timing-Bug: "user is locked" direkt nach `chpasswd`, weil
   AccountsService die neue Passwort-Zeile noch nicht bemerkt hatte).
3. Prüft, ob die Firefox-Startseiten-Policy aus Schritt 10 korrekt sitzt.

**Wichtige Korrektur (2026-08-14):** Alle Skripte in `scripts/` sind
**nur für `dialosadmin`** gedacht - `nutzer` soll sie nie zu Gesicht
bekommen. Sie deshalb **nicht** über `/etc/skel/Desktop/` verteilen,
sondern gezielt auf das bereits existierende `dialosadmin`-Konto
kopieren (`/etc/skel/` wirkt nur bei Konten, die *danach* angelegt
werden - bei diesem Rezept ist das ausschließlich `nutzer`, nicht ein
weiteres Admin-Konto; ein früherer Versuch, das über `/etc/skel/Desktop/`
zu lösen, landete deshalb ungewollt auf `nutzer`s Desktop):

```bash
mkdir -p /home/dialosadmin/Desktop
cp scripts/*.sh /home/dialosadmin/Desktop/
chmod 755 /home/dialosadmin/Desktop/*.sh
chown dialosadmin:dialosadmin /home/dialosadmin/Desktop/*.sh
```

Claude-Desktop-App fürs Admin-Konto bereitstellen (wird bei jedem
Büro-Setup frisch heruntergeladen, nicht ins Repo committet) - aus
demselben Grund ebenfalls direkt auf `dialosadmin`s Desktop, nicht über
`/etc/skel/`:

```bash
cd /tmp && apt-get download claude-desktop
sudo cp /tmp/claude-desktop*.deb /home/dialosadmin/Desktop/
sudo chmod 644 /home/dialosadmin/Desktop/claude-desktop*.deb
sudo chown dialosadmin:dialosadmin /home/dialosadmin/Desktop/claude-desktop*.deb
```

Nach diesem Schritt: neu starten, verifizieren dass `nutzer` automatisch
ohne Anmeldebildschirm startet - und dass `nutzer`s eigener Desktop
**leer** von Admin-Werkzeugen ist.

## 14. Bluetooth-Kopplungsdaten fest einbauen (optional, geräte­spezifisch)

Nur relevant, wenn du auf **demselben** Testgerät bleibst (der
eingebaute Bluetooth-Adapter muss gleich bleiben, da die Kopplungsdaten
an dessen MAC-Adresse hängen):

```bash
sudo cp -r "iso-build/config/includes.chroot/var/lib/bluetooth/." /var/lib/bluetooth/
```

Erspart erneutes Koppeln von Maus/Tastatur/Lautsprecher nach einer
Neuinstallation. Auf einem neuen/anderen Gerät stattdessen normal koppeln.

## 15. Spracherkennung (Vosk + hassil) - Status: nur live installiert

**Achtung, noch nicht als wiederholbares Rezept im Repo verankert**
(siehe TODO.md) - hier die Schritte, wie sie live auf dem T490
durchgeführt wurden, zum Nachvollziehen/Reproduzieren:

```bash
pip install --user vosk hassil
sudo mkdir -p /usr/local/share/vosk-model-de-big /usr/local/share/vosk-model-de-small
curl -L -o /tmp/vosk-de-big.zip https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
curl -L -o /tmp/vosk-de-small.zip https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
sudo unzip /tmp/vosk-de-big.zip -d /usr/local/share/vosk-model-de-big
sudo unzip /tmp/vosk-de-small.zip -d /usr/local/share/vosk-model-de-small
```

Entscheidung **hassil statt Rhasspy** für die Intent-Erkennung
(Rhasspy vom Ersteller archiviert, nicht mehr gepflegt) - Details und
Begründung in [sprachsteuerung.md](sprachsteuerung.md).

Technisches Testskript `dialos-vosk-test.py` liegt bisher nur unter
`/usr/local/bin/` auf dem Testgerät, noch nicht im Repo. Kernergebnis
des Mikrofon-Vergleichstests: ein Bluetooth-Headset (z. B. AIRHUG) ist
dem eingebauten Laptop-Mikrofon klar überlegen - Zielbild ist
Bluetooth-Mikrofon als primärer Weg, eingebautes Mikrofon als (noch
nicht implementierter) Fallback. Details:
[offene-punkte.md](offene-punkte.md), Abschnitt "Sprachsteuerung".

## 16. ISO bauen (Penguins' Eggs)

Sobald alle vorigen Schritte durchgeführt sind, System einmal neu
starten und verifizieren (Autologin, Splash, Ton, Orca, Piper,
Programme). Dann:

**Wichtig: `--path` auf die externe Platte zeigen lassen**, statt das
Standard-Arbeitsverzeichnis `/home/eggs` (intern) zu nutzen - so landet
das mehrere GB große Zwischenmaterial gar nicht erst auf der internen
Platte (und die fertige ISO muss nicht mehr manuell rüberkopiert
werden):

```bash
sudo eggs produce --path /media/dialosadmin/SanDisk-Extreme/DialOS/eggs-workdir
# oder, um dialosadmin/nutzer inkl. Home-Verzeichnissen zu übernehmen:
sudo eggs produce --path /media/dialosadmin/SanDisk-Extreme/DialOS/eggs-workdir --clone
```

`--clone` ist Pflicht, wenn die gebaute ISO später mit `dialos-install`
getestet werden soll (das Werkzeug kopiert beim Installieren nur, was
im Live-System tatsächlich läuft - ohne `--clone` gäbe es dort kein
`dialosadmin`/`nutzer`, nur einen generischen `live`-Nutzer). Ohne
`--clone` eignet sich die ISO für den klassischen Weg: Live-Boot →
Calamares-Installation → Konten manuell per Schritt 13 einrichten.

Die fertige ISO liegt danach direkt unter
`.../DialOS/eggs-workdir/<generierter-name>.iso` - zur besseren
Nachvollziehbarkeit passend umbenennen, z. B. nach
`DialOS-ISOs/DialOS-Live-0.5.0.iso`.

## Praxishinweis: externe Platte

Da Build- und Test-System oft dasselbe Gerät sind und ein Live-Boot-
Installationstest die interne Platte überschreibt, empfiehlt es sich,
dieses Repository (und die gebauten ISOs) auf einer externen Platte zu
halten, damit ein Reinstall des Testgeräts sie nicht mitreißt. Nach
jedem Reinstall: Git-Identität (`git config user.name`/`user.email`)
und ggf. ein Symlink wie `~/DialOS` auf den externen Repo-Pfad neu
setzen.

## Was hier bewusst NICHT drinsteht

Diese Anleitung deckt den Weg bis 0.5.0 ab. Bekannte offene
Baustellen (Wake-Word-Engine, Bluetooth-Mikrofon-Fallback,
Rechtschreibprüfung, endgültige sudo-Policy für `nutzer`, u. a.) stehen
in [offene-punkte.md](offene-punkte.md); kleinere, konkrete
Nacharbeiten in [TODO.md](../TODO.md).
