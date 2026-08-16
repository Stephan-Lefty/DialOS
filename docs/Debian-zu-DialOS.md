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

> **Schnellweg seit 2026-08-14:** Die Schritte 2-12 + 15 (sowie
> optional 14) lassen sich jetzt automatisiert per
> [`scripts/dialos-full-office-setup.sh`](../scripts/dialos-full-office-setup.sh)
> ausführen, statt sie einzeln abzutippen (siehe
> [`scripts/README.md`](../scripts/README.md)). Die Einzelschritte unten
> bleiben trotzdem die eigentliche, ausführliche Referenz - genau daraus
> ist das Skript gebaut, und bei Problemen mit einem einzelnen Schritt
> lässt sich das Skript auch gezielt nur für diesen einen Schritt
> aufrufen (`./scripts/dialos-full-office-setup.sh 08`). Schritt 14
> (Bluetooth-Kopplungsdaten) läuft dabei nur mit `--bluetooth-kopplung`
> mit, da er gerätespezifisch ist. Schritt 1 (Basis-Installation), 13
> (`nutzer`-Konto anlegen) und 16 (ISO bauen) bleiben bewusst eigene,
> manuelle Schritte - siehe dort.

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

**Partitionierung - wichtig, manuell statt "geführt - gesamte Platte
verwenden" wählen** (seit 2026-08-14, siehe
[sicherheit-datenschutz.md](sicherheit-datenschutz.md), Abschnitt
"Verschlüsselung von nutzers Daten + Sicherheits-Stick"):

- GPT-Partitionstabelle.
- EFI-Systempartition (~512 MB), `/boot/efi`.
- Root-Partition, **genau 100 GB**, ext4, `/`.
- **Den kompletten Rest der Platte unpartitioniert/frei lassen** - nicht
  dem Installer überlassen, sonst hat
  [`dialos-setup-home-partition.sh`](../iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh)
  später (Schritt 12) keinen Platz mehr für die verschlüsselte
  `dialos-nutzer-home`-Partition.

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
  `parted`, `dosfstools`, `exfatprogs` (für die Windows-lesbare
  `DIALOS-DATA`-Partition auf dem Sicherheits-Stick), `cryptsetup`,
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

**Standortabfrage fürs Wetter (GeoClue2) freischalten** (seit
2026-08-14, siehe TODO.md für die Geschichte dazu) - sonst
`AccessDenied: Geolocation disabled` beim Standortversuch:

```bash
printf '\n[dialos-start-ansage]\nallowed=true\nsystem=true\nusers=\n' | sudo tee -a /etc/geoclue/geoclue.conf > /dev/null
```

(Nur anhängen, nicht überschreiben - sonst gehen Debians eigene
Standard-Einträge für andere Apps verloren. `org.gnome.system.location
enabled=true` steht schon als dconf-Standardwert in
`01-dialos-defaults`, siehe Schritt 3.)

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
  **Wetter-Standort seit 2026-08-14 per GeoClue2 statt fest/IP-geraten**
  (das Gerät wird auch unterwegs genutzt, ein fest hinterlegter Ort war
  deshalb keine Option) - nutzt automatisch die beste verfügbare Quelle
  (WLAN-Abgleich über Mozilla Location Service, sonst IP-Schätzung als
  Fallback). Fixes, die ungenauer als 10 km sind (typischerweise eine
  reine IP-Schätzung ohne WLAN-Treffer in der Mozilla-Datenbank - live
  beobachtet: ~25 km Ungenauigkeit, dabei rund 300 km von der echten
  Position entfernt), werden verworfen und die Wetteransage
  ausgelassen, statt eine falsche Stadt zu nennen. Das bedeutet:
  **in Gegenden mit dünner Mozilla-WLAN-Datenbank-Abdeckung (z. B.
  ländliche/dünn besiedelte Regionen) kann die Wetteransage öfter
  ausbleiben** als mit der alten, ungenaueren aber immer "irgendeine"
  Antwort liefernden IP-Ratelösung - das ist bewusst so gewählt
  (lieber nichts sagen als etwas Falsches).
- `dialos-tts-indicator.py`: Panel-Icon, das anzeigt, wenn gerade
  gesprochen wird (braucht die AppIndicator-Erweiterung aus Schritt 9).

## 12. Sicherheits-Werkzeuge (nutzers Daten verschlüsseln + Autologin-Gate)

**Design seit 2026-08-14** (löst die ursprüngliche Ganze-Platte-
Verschlüsselung ab, siehe README-Änderungsprotokoll 0.5.0 und
[sicherheit-datenschutz.md](sicherheit-datenschutz.md), Abschnitt
"Verschlüsselung von nutzers Daten + Sicherheits-Stick", für Konzept +
Begründung): `dialos-install` verschlüsselt nur noch eine eigene
`dialos-nutzer-home`-Partition (LUKS2, ausschließlich `/home/nutzer`),
root bleibt unverschlüsselt (~100 GiB, ext4). Kein
`cryptsetup-initramfs`/`dialos-keyscript` mehr nötig - die
Home-Partition wird nicht im initramfs geöffnet, sondern von
`dialos-stick-gate.service` nach dem Boot.

```bash
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

`dialos-stick-gate.service` wirkt erst ab dem **nächsten** Neustart
(läuft nur beim Boot, nicht rückwirkend auf die aktuell laufende
Sitzung). Test nach einer echten `dialos-install`-Installation: Stick
abziehen, neu starten - System muss am normalen GDM-Login-Screen
landen statt `nutzer` automatisch anzumelden und `/home/nutzer` muss
leer/nicht gemountet sein; Stick wieder einstecken, erneut neu starten
- `/home/nutzer` muss gemountet sein und Autologin muss wieder greifen.

**Home-Partition auf einem frisch installierten System anlegen**
(neu seit 2026-08-14, für den Weg über die Basis-Installation in
Schritt 1 statt über `dialos-install`s Ganze-System-Kopie):
`dialos-setup-home-partition.sh` übernimmt dieselbe LUKS/Stick-Logik
wie `dialos-install`, aber ohne dessen Festplatten-Wipe/rsync-Kopie -
nutzt stattdessen den in Schritt 1 bewusst frei gelassenen Platz am
Ende der System-Platte:

```bash
sudo /usr/local/sbin/dialos-setup-home-partition.sh
```

Fragt nach Sicherheits-Stick, Wiederherstellungs-Passwort (≥12 Zeichen)
und Bestätigung ("LOESCHEN" eingeben), bietet danach das gleiche
verschlüsselte Nextcloud-Schlüssel-Backup wie `dialos-install` an. Am
Ende wird `/home/nutzer` gleich gemountet (kein Neustart nötig), sofern
`dialos-stick-gate.sh` schon installiert ist (siehe oben).

**Wichtig für Schritt 13:** `scripts/dialos-setup-nutzer.sh` legt
`nutzer`s Konto erst an, nachdem es geprüft (und notfalls per
`dialos-stick-gate.sh` selbst ausgelöst) hat, dass `/home/nutzer`
bereits gemountet ist - **`dialos-setup-home-partition.sh` muss also
vor Schritt 13 gelaufen sein und der Sicherheits-Stick beim Ausführen
von Schritt 13 noch eingesteckt sein**, sonst bricht das Skript
kontrolliert ab (siehe sicherheit-datenschutz.md).

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

**Klickbares Icon für `dialos-install` auf `dialosadmin`s Desktop**
(2026-08-14): Die App-Menü-Vorlage
(`iso-build/config/includes.chroot/usr/share/applications/
dialos-install.desktop`) zusätzlich direkt auf den Desktop kopieren -
kein `sudo` nötig, `dialosadmin` besitzt sein eigenes Desktop-Verzeichnis:

```bash
cp iso-build/config/includes.chroot/usr/share/applications/dialos-install.desktop /home/dialosadmin/Desktop/
chmod 755 /home/dialosadmin/Desktop/dialos-install.desktop
gio set /home/dialosadmin/Desktop/dialos-install.desktop metadata::trusted true
```

Der letzte Befehl (`gio set ... metadata::trusted true`) ist Pflicht -
ohne ihn zeigt Nautilus beim ersten Doppelklick eine
"nicht vertrauenswürdig"-Warnung statt das Programm zu starten (anders
als bei den `.sh`-Skripten auf demselben Desktop, die über die
Textdatei-Ausführen-Einstellung laufen, nicht über den
Launcher-Vertrauensmechanismus).

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

## 15. Spracherkennung (Vosk + hassil)

**Seit 2026-08-14 als wiederholbares Rezept verankert** (löst den
bisherigen TODO.md-Punkt "nur live installiert" ab - der ursprüngliche
Testlauf ging bei einem zwischenzeitlichen Reinstall des T490 sogar
tatsächlich wieder verloren, genau die Falle, vor der TODO.md gewarnt
hatte, siehe README-Änderungsprotokoll 0.5.0).

**System-weite Installation** (nicht `--user`) - damit später auch
`nutzer` darauf zugreifen kann, nicht nur das Konto, das die Pakete
installiert hat. Debian 13 blockiert `pip install` ins System-Python
ohne Weiteres (PEP 668, "externally-managed-environment") -
`--break-system-packages` ist Debians offiziell vorgesehener Weg dafür,
kein Hack. Versionen wie beim ursprünglichen Testlauf gepinnt:

```bash
sudo pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0
```

Deutsche Vosk-Modelle (groß für Genauigkeit, klein für Geschwindigkeit -
siehe `dialos-vosk-test.py`):

```bash
cd /tmp
curl -L -o vosk-de-big.zip https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
curl -L -o vosk-de-small.zip https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip vosk-de-big.zip
unzip vosk-de-small.zip
sudo mv vosk-model-de-0.21 /usr/local/share/vosk-model-de-big
sudo mv vosk-model-small-de-0.15 /usr/local/share/vosk-model-de-small
```

**Entpack-Falle:** Die ZIPs enthalten selbst schon einen benannten
Ordner (`vosk-model-de-0.21/` bzw. `vosk-model-small-de-0.15/`) - mit
`unzip -d <Zielordner>` entsteht dadurch eine doppelt verschachtelte
Struktur (`<Zielordner>/vosk-model-de-0.21/...` statt direkt
`<Zielordner>/...`), unter der `vosk.Model()` die Dateien nicht findet.
Deshalb hier stattdessen ohne `-d` ins aktuelle Verzeichnis entpacken
und danach den bereits richtig benannten Ordner an den Zielort
verschieben (`mv`) - so landen `am/`, `conf/`, `graph/`, `ivector/` etc.
direkt in `/usr/local/share/vosk-model-de-big`
bzw. `-small`, wie es `dialos-vosk-test.py`
(`MODELL_PFAD_STANDARD = "/usr/local/share/vosk-model-de-small"`)
erwartet. Genau diese doppelte Verschachtelung ist beim ursprünglichen
Testlauf auf dem T490 passiert (dort per `unzip ... -d <Zielordner>`) -
funktioniert nur zufällig trotzdem, weil `unzip` bei einer
Namenskollision die Dateien zusätzlich auch flach ins Zielverzeichnis
kopiert; sauber ist das nicht (doppelter Festplattenplatz, siehe
TODO.md).

Testskript installieren:

```bash
sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-vosk-test.py /usr/local/bin/
sudo chmod 755 /usr/local/bin/dialos-vosk-test.py
```

Aufruf: `dialos-vosk-test.py [Modellpfad] [Aufnahmesekunden]
[--bluetooth-erlauben]` - interaktiv (wartet auf [Enter], nimmt danach
per `parec` echtes Mikrofon-Audio auf, erkennt mit Vosk, zeigt das
Ergebnis im Terminal). Kein automatisierter Test möglich, braucht eine
Person, die tatsächlich hineinspricht.

Entscheidung **hassil statt Rhasspy** für die Intent-Erkennung
(Rhasspy vom Ersteller archiviert, nicht mehr gepflegt) - Details und
Begründung in [sprachsteuerung.md](sprachsteuerung.md).

Kernergebnis des Mikrofon-Vergleichstests: ein Bluetooth-Headset (z. B.
AIRHUG) ist dem eingebauten Laptop-Mikrofon klar überlegen - Zielbild
ist Bluetooth-Mikrofon als primärer Weg, eingebautes Mikrofon als (noch
nicht implementierter) Fallback. Details:
[offene-punkte.md](offene-punkte.md), Abschnitt "Sprachsteuerung".

## 16. ISO bauen (Penguins' Eggs)

Sobald alle vorigen Schritte durchgeführt sind, System einmal neu
starten und verifizieren (Autologin, Splash, Ton, Orca, Piper,
Programme). Dann:

```bash
sudo eggs produce
# oder, um dialosadmin/nutzer inkl. Home-Verzeichnissen zu übernehmen:
sudo eggs produce --clone
```

`--clone` ist Pflicht, wenn die gebaute ISO später mit `dialos-install`
getestet werden soll (das Werkzeug kopiert beim Installieren nur, was
im Live-System tatsächlich läuft - ohne `--clone` gäbe es dort kein
`dialosadmin`/`nutzer`, nur einen generischen `live`-Nutzer). Ohne
`--clone` eignet sich die ISO für den klassischen Weg: Live-Boot →
Calamares-Installation → Konten manuell per Schritt 13 einrichten.

Ausgabe liegt standardmäßig unter `/home/eggs/<generierter-name>.iso` -
zur besseren Nachvollziehbarkeit passend umbenennen und auf die externe
Platte verschieben, z. B. nach `DialOS-ISOs/DialOS-Live-0.5.0.iso`.

**Versuch verworfen (2026-08-14): `--path` auf die externe Platte
zeigen lassen**, um das mehrere GB große Zwischenmaterial gar nicht
erst auf der internen Platte anfallen zu lassen. Schlägt fehl: Der
`bootloader-copy`-Schritt von `eggs`/`coa` schreibt seine Dateien
(u. a. `isolinux.bin`) unabhängig von `--path` hartkodiert nach
`/home/eggs/isodir` - der Rest des Builds nutzt korrekt den
`--path`-Zielordner, das fertige Image landet also ohne funktionierenden
Bootloader (`xorriso`-Fehler: "Cannot find in ISO image ...
bin_path='/isolinux/isolinux.bin'"). Bug in `eggs`/`coa`
(Version 48.x), nicht an unserer Konfiguration. Bis das stromaufwärts
gefixt ist: `--path` nicht verwenden, immer den internen
Standardpfad `/home/eggs` nutzen und danach manuell verschieben.

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
