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
   Vom fertig eingerichteten System wird zum Schluss ein
   Sicherungs-Abbild gezogen (Schritt 16) - seit 2026-08-16 mit
   [Rescuezilla](https://rescuezilla.com/), der grafischen Oberfläche
   für Clonezilla. Penguins' Eggs ist entfallen.

Diese Anleitung beschreibt Weg 2. Referenz-Testgerät: Lenovo ThinkPad
T490 (siehe [hardware.md](hardware.md)).

> **Schnellweg (Stand 2026-08-16): drei Befehle von Debian zu DialOS.**
> Nach der Basis-Installation (Schritt 1) ist der gesamte Rest bis auf den
> ISO-Bau in Skripten abgebildet - es bleibt keine Handarbeit mehr aus
> dieser Doku abzutippen:
>
> ```bash
> # 1) Schritte 2-12 + 15 - als dialosadmin, OHNE sudo:
> ./scripts/dialos-full-office-setup.sh
>
> # 2) Schritt 12b - Sicherheits-Stick einstecken, ebenfalls OHNE sudo
> #    (das Skript holt sich die Rechte selbst per pkexec):
> /usr/local/sbin/dialos-setup-home-partition.sh
>
> # 3) Schritt 13 - Stick stecken lassen:
> sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
> ```
>
> Danach neu starten, dann Schritt 16 (ISO bauen). Die Einzelschritte
> unten bleiben die eigentliche, ausführliche Referenz - genau daraus sind
> die Skripte gebaut, und bei Problemen mit einem einzelnen Schritt lässt
> sich Skript 1 gezielt nur für diesen einen Schritt aufrufen
> (`./scripts/dialos-full-office-setup.sh 08`). Schritt 14
> (Bluetooth-Kopplungsdaten) läuft nur mit `--bluetooth-kopplung` mit, da
> er gerätespezifisch ist. Schritt 1 (Basis-Installation) und 16 (ISO
> bauen) bleiben bewusst manuell - siehe dort.
>
> **Zwei Fallen bei den Aufrufen** (beide 2026-08-16 gefunden, bevor der
> erste echte Durchlauf startete):
> - Skript 1 **nicht** mit `sudo` starten. Die Schritte 9 und 10 richten
>   das Benutzerkonto ein (GNOME-Erweiterung, Standardprogramme); unter
>   `sudo` wäre `~` gleich `/root` und alles landete lautlos im falschen
>   Home. Das Skript weist einen Start als root deshalb ab.
> - Skript 2 ebenfalls **nicht** mit `sudo` starten. `sudo` entfernt
>   `DISPLAY`/`XAUTHORITY` (`env_reset`), womit die Zenity-Dialoge des
>   Skripts nicht mehr aufgehen könnten. Ohne `sudo` gestartet, hebt es
>   sich selbst per `pkexec` an und behält die Grafik-Umgebung.

## 0. Voraussetzungen

- Debian-13-("Trixie")-Installationsmedium mit GNOME-Desktop von
  debian.org - der Standard-Debian-Installer ist der einzige Installer,
  den DialOS noch verwendet (siehe Schritt 5). Debian
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

**Zeitzone/Sprache - entschieden am 2026-08-16:** Das Referenz- und
Baugerät läuft auf **`Europe/Vienna` + `de_AT.UTF-8`** (Stephans Standort
in Tirol), nicht auf `Europe/Berlin`. Das ist bewusst so und bleibt so.

Seit der Entscheidung für Weg A (siehe Schritt 5) ist das unkompliziert:
Jedes Gerät wird im Büro über den Debian-Installer aufgesetzt, die
Zeitzone wird also **pro Gerät in Schritt 1 gewählt**. Für ein Gerät, das
außerhalb Österreichs eingesetzt wird, dort einfach die passende Zeitzone
angeben - es gibt keinen zweiten Weg mehr, der eine andere Einstellung
vererben könnte.

**Partitionierung - seit 2026-08-16 automatisiert (Weg A).** Damit du
weder von Hand partitionieren noch über die Plattengröße nachdenken
musst, gibt eine Preseed-Datei dem Debian-Installer das Layout vor:

| Partition | Größe | |
|---|---|---|
| EFI | 538 MB | `/boot/efi` |
| root | **100 GiB**, ext4 | `/` |
| *Rest* | **unpartitioniert** | bleibt für Schritt 12 |

Der freie Rest ist der Zweck der Übung: Dort legt
[`dialos-setup-home-partition.sh`](../iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh)
später den verschlüsselten Swap (8 GiB) und `dialos-nutzer-home` an - je
größer die Platte, desto mehr Platz bekommt `nutzer`, ohne dass
irgendwo eine Zahl angepasst werden muss.

> **Warum nicht einfach die ganze Platte nehmen und danach verkleinern?**
> Weil das nicht geht: Ein **eingehängtes** ext4-Dateisystem lässt sich
> nicht schrumpfen, Online-Resize kann ausschließlich wachsen. Ein Skript
> auf dem laufenden System könnte die root-Partition also gar nicht
> verkleinern - das ginge nur aus einer Live-Sitzung heraus, mit einem
> zusätzlichen Neustart pro Gerät und dem Risiko, dass ein Abbruch
> mitten im Schrumpfen das System zerstört. Deshalb entsteht das
> richtige Layout gleich beim Installieren.

### 1a. Die Preseed-Datei bereitstellen

Die Datei liegt im Repo unter
[`website/d-i/trixie/preseed.cfg`](../website/d-i/trixie/preseed.cfg).
Der Installer muss sie über **einfaches HTTP** erreichen können.

> **Warum HTTP und nicht HTTPS:** Die Debian-Doku nennt für `preseed/url`
> ausschließlich `http://` und `tftp://`. HTTPS wird nirgends zugesichert,
> das Verhalten bei einer 301-Umleitung ebenso wenig. Ein Server, der
> zwingend auf HTTPS umleitet, ist deshalb ungeeignet - geprüft am
> 2026-08-16 an dialos.org, das genau das tut.

#### Weg 1 (empfohlen): ein zweiter Rechner mit der externen Platte

**Wichtig zum Verständnis:** Das Zielgerät wird gerade plattgemacht - es
kann die Datei also nicht selbst ausliefern. Der Webserver läuft auf einem
**zweiten Rechner**. Genau dafür liegt dieses Repository auf einer
externen Platte: Die steckst du während der Installation einfach an einen
beliebigen zweiten Rechner an. Der muss nichts können außer `python3`
(auf jedem Linux und macOS vorhanden) und im selben Netz hängen wie das
Zielgerät.

Auf diesem zweiten Rechner - von der externen Platte aus:

```bash
./scripts/dialos-preseed-server.sh
```

Mehr ist nicht zu tun. Das Skript

- prüft, ob die Preseed-Datei da und der Port frei ist,
- ermittelt die eigene IP-Adresse (bei mehreren Netzwerkkarten nennt es
  die Alternativen),
- gibt die **fertige Zeile** aus, die in Schritt 1b einzutippen ist,
- und startet den Webserver.

Die Ausgabe sieht so aus:

```
  Im Debian-Installer diese Zeile an die Startzeile anhaengen
  (UEFI: Taste "e", ans Ende der Zeile mit "linux", dann Strg+X):

      preseed/url=http://192.168.178.45:8080/d-i/trixie/preseed.cfg
```

Nach der Partitionierung den Server mit `Strg`+`C` beenden. Ist der Port
belegt, sagt das Skript das und man gibt einen anderen an
(`./scripts/dialos-preseed-server.sh 8081`).

Der Weg funktioniert unabhängig davon, wo die externe Platte eingehängt
ist - das Skript leitet den Repo-Pfad aus seinem eigenen Ort ab.

Vorteile gegenüber allen anderen Ablageorten: einfaches HTTP ohne
Umleitung, kein Hoster, kein Internet nötig - und die Datei kommt
unmittelbar aus dem Repo, kann also gar nicht veralten.

#### Weg 2 (optional): dialos.org

Nur sinnvoll, wenn dein Webserver `/d-i/` **ohne** Umleitung auf HTTPS
ausliefert. Datei per FTP dorthin legen:

```
http://dialos.org/d-i/trixie/preseed.cfg
```

Zwei Fallstricke, beide am 2026-08-16 real aufgetreten:

- **Der FTP-Startordner ist meist nicht das Web-Wurzelverzeichnis.** Bei
  vielen Hostern landest du eine Ebene darüber. Der Ordner `d-i` muss auf
  derselben Ebene liegen wie `wp-content`, `wp-admin`, `wp-includes` und
  `index.php` - sonst liefert der Server 404, obwohl die Datei da ist.
- **dialos.org läuft auf WordPress und erzwingt HTTPS.** WordPress selbst
  ist unkritisch (nginx liefert vorhandene Dateien vor der
  WordPress-Weiterleitung aus), die HTTPS-Erzwingung dagegen schon: Sie
  müsste für `/d-i/` in der Server-Konfiguration ausgenommen werden.

**Prüfen, ob es liegt** - unbedingt mit `http://`, nicht im Browser
(der ersetzt es stillschweigend durch `https://`):

```bash
curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" -L http://dialos.org/d-i/trixie/preseed.cfg
```

Erwartet wird `200` **ohne** Wechsel auf `https://` in der Ausgabe.

> **Stand auf dialos.org am 2026-08-16:** Die Datei liegt korrekt und ist
> erreichbar (200, byte-identisch mit dem Repo), **aber nur über die
> Umleitung**: `http://` antwortet mit `301` auf `https://`. Ob der
> Debian-Installer dem folgt und TLS beherrscht, ist offen - es zeigt
> sich erst beim nächsten Aufbau. Bleibt der Installer beim Laden der
> Vorkonfiguration hängen, ist das der Grund; dann auf Weg 1 (Rechner im
> Büro) ausweichen oder von Hand partitionieren (1d). Dauerhaft lösen
> ließe sich das nur, indem der Hoster `/d-i/` von der
> HTTPS-Erzwingung ausnimmt - die Umleitung kommt von nginx selbst, nicht
> von WordPress.
>
> Der Weg dorthin war lehrreich: Der FTP-Zugang landet **nicht** im
> Web-Wurzelverzeichnis, sondern eine Ebene darüber. Das richtige
> Verzeichnis erkennt man daran, dass `license.txt`, `wp-login.php` und
> `wp-admin/` darin liegen.

### 1b. Den Installer damit starten (bei jedem Gerät)

**Es braucht eine Internetverbindung - Kabel ODER WLAN.** Der Installer
konfiguriert das Netzwerk, *bevor* er die Preseed-Datei holt (die
Debian-Doku ist dazu eindeutig: „the network must be configured before
the preseed file can be fetched"). Beides funktioniert also:

- **Netzwerkkabel:** einfachster Fall, der Installer holt sich per DHCP
  alles selbst, ohne dich zu fragen.
- **WLAN:** genauso möglich. Der Installer fragt beim Netzwerk-Schritt
  nach dem WLAN-Namen und dem Passwort, verbindet sich - und lädt erst
  danach die Preseed-Datei. Die WLAN-Firmware für das ThinkPad ist in
  den offiziellen Debian-13-Abbildern enthalten.

Ablauf:

1. Vom Debian-13-USB-Stick booten.
2. Im Bootmenü **nicht** Enter drücken, sondern den Eintrag
   `Graphical install` (oder `Install`) nur **auswählen**.
3. Jetzt die Startzeile bearbeiten:
   - **UEFI (der Normalfall, GRUB-Menü):** Taste **`e`** drücken. Es
     erscheint ein Textblock. Mit den Pfeiltasten in die Zeile gehen, die
     mit `linux` beginnt, und mit der **Ende**-Taste an deren Ende
     springen.
   - **Älteres BIOS (isolinux-Menü):** stattdessen **`Tab`** drücken. Die
     Startzeile erscheint dann direkt zum Bearbeiten.
4. Dort ans Ende - mit einem Leerzeichen davor - die Adresse aus
   Schritt 1a anhängen. Bei Weg 1 (Rechner im Büro):

   ```
   preseed/url=http://192.168.1.50:8080/d-i/trixie/preseed.cfg
   ```

   (die `192.168.1.50` durch die eigene IP ersetzen). Bei Weg 2:

   ```
   preseed/url=http://dialos.org/d-i/trixie/preseed.cfg
   ```

5. Starten:
   - **UEFI:** **`Strg`+`X`** (oder `F10`).
   - **BIOS:** **`Enter`**.

> **Warum hier bewusst kein `auto` steht.** Die verbreitete Kurzform
> `auto url=dialos.org` schaltet zusätzlich den Automatik-Modus ein. Der
> schiebt Sprache und Tastatur nach hinten, damit man *auch sie*
> preseeden kann - und senkt dabei die Fragen-Priorität. Für DialOS ist
> das nicht nur unnötig (wir geben ausschließlich die Partitionierung
> vor), sondern kontraproduktiv: Bei niedrigerer Priorität könnten
> ausgerechnet die WLAN-Rückfragen übersprungen werden, und ohne Kabel
> stünde die Installation dann. Mit der Schreibweise oben bleiben alle
> gewohnten Fragen sichtbar.

### 1c. Was dann passiert

Die Installation läuft wie gewohnt weiter - Sprache, Tastatur, Netzwerk,
Zeitzone und das Konto **`dialosadmin`** fragt der Installer weiterhin
ganz normal ab. Die Preseed-Datei gibt ausschließlich die
Partitionierung vor.

Ein Punkt bleibt bewusst deine Entscheidung: **Der Installer fragt
weiterhin, welche Platte er partitionieren soll.** Das ist Absicht - so
kann die Vorgabe niemals die falsche Platte treffen, etwa den
Installations-Stick selbst oder eine angesteckte externe Platte.

> **Danach kommt keine Rückfrage mehr.** Sobald die Platte gewählt ist,
> wird sie gelöscht und neu aufgeteilt. Vorher also prüfen, dass wirklich
> die interne Platte markiert ist (bei ThinkPads meist `nvme0n1`, nicht
> `sda` - `sda` ist typischerweise der USB-Stick).

Konto: Das erste angelegte Konto (der Installer verlangt eines) muss
**`dialosadmin`** heißen - Konvention, damit Skripte und Doku nicht pro
Gerät angepasst werden müssen.

### 1d. Rückfallebene: von Hand partitionieren

Ohne Preseed - etwa wenn kein Netzwerkkabel zur Hand ist - im Installer
**"Manuell"** wählen statt "Geführt - gesamte Platte verwenden" und
dasselbe Layout von Hand anlegen: GPT-Partitionstabelle, EFI-Partition
(~512 MB genügen; der Debian-Installer legt von sich aus gern rund 1 GB
an - beides ist in Ordnung), root mit **100 GiB** als ext4 auf `/`, und
**den kompletten Rest der Platte unpartitioniert lassen**. Einen Swap
kann der Installer anlegen oder auch nicht - Schritt 12 ersetzt ihn
ohnehin durch einen verschlüsselten (siehe dort). Als Untergrenze
verlangt das Skript in Schritt 12 20 GiB freien Platz.

**So sah das auf dem Referenzgerät (T490, 476,9-GiB-NVMe) beim ersten
Aufbau aus** - noch von Hand partitioniert, am 2026-08-16 nachgemessen:

| Partition | Größe | Verwendung |
|---|---|---|
| `nvme0n1p1` | 100,00 GB (93,13 GiB) | `/`, ext4 |
| `nvme0n1p2` | 954 MB | `/boot/efi`, vfat |
| `nvme0n1p3` | 37,3 GiB | Swap (wurde in Schritt 12 durch 8 GiB verschlüsselt ersetzt) |
| *(unpartitioniert)* | **345,6 GiB** | wurde `dialos-nutzer-home` |

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
  `nodejs`/`npm` (für Claude Code CLI, Schritt 7), `dconf-cli`,
  `unzip` + `python3-pip` (beide für Schritt 15 nötig - ergänzt am
  2026-08-16, weil sie vorher fehlten: `pip3` ist auf einer frischen
  Debian-13-Installation nicht vorhanden, und Schritt 15 wäre damit ganz
  am Ende des Laufs gescheitert).
- **Installer-/Sicherheits-Werkzeuge**: `zenity`, `polkitd`, `pkexec`,
  `parted`, `dosfstools`, `exfatprogs` (für die Windows-lesbare
  `DIALOS-DATA`-Partition auf dem Sicherheits-Stick), `cryptsetup`,
  **`systemd-cryptsetup`** (ergänzt 2026-08-16: Debian 13 hat die
  crypttab-Auswertung aus dem `systemd`-Paket herausgelöst - ohne dieses
  Paket gibt es weder den Generator noch `systemd-cryptsetup@.service`,
  und `/etc/crypttab` bleibt beim Booten komplett wirkungslos; siehe
  Schritt 12, verschlüsselter Swap),
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

> **Entfallen am 2026-08-16:** Hier stand bis dahin eine zweite
> Grafik (`/etc/penguins-eggs.d/brain.d/assets/splash.png`) für den
> GRUB-/isolinux-Bootbereich der von Penguins' Eggs gebauten Live-ISO.
> Mit dem Wegfall von eggs (Schritt 16) ist sie wirkungslos - das
> Plymouth-Theme oben bringt seine eigene `background.png` mit.

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

Ganz am Anfang (bevor `nutzer` überhaupt existiert - der wird erst in
Schritt 13 angelegt) bekommt das Admin-Konto (`dialosadmin`) testweise
Autologin, damit man am System arbeiten kann. Details und Begründung:
[sicherheit-datenschutz.md](sicherheit-datenschutz.md), Abschnitt
"Automatische Anmeldung".

## 5. Calamares entfernen (entfällt seit 2026-08-16)

**Dieser Schritt richtet nichts mehr ein - er räumt nur auf.**

Bis zum 2026-08-16 stand hier die Einrichtung des Calamares-Installers:
eigenes DialOS-Branding, feste Zeitzone, Selbstentfernung nach der
Installation, dazu ein Vendor-Overlay für Penguins' Eggs und ein
`base.yaml.tmpl`, damit `eggs produce` das Branding nicht wieder
überschreibt. Calamares war der Installer für den **Live-Boot-Weg**: Die
DialOS-ISO wurde auf dem Kundengerät gestartet, Calamares installierte
das System und entfernte sich anschließend selbst wieder.

**Entscheidung von Stephan (2026-08-16): Dieser Weg entfällt.** Jedes
Kundengerät wird im Büro aufgesetzt - über die Debian-13-ISO von
debian.org plus die drei DialOS-Skripte (siehe Schnellweg oben). Damit
bekommt nie jemand außer Stephan einen Installer zu Gesicht, und
Calamares hat keine Aufgabe mehr.

Was dadurch entfällt:

- `/etc/calamares/branding/dialos/`, `locale.conf`, `shellprocess.conf`
- das Penguins-Eggs-Vendor-Overlay unter
  `/etc/penguins-eggs.d/brain.d/assets/calamares/`
- `base.yaml.tmpl` (existierte nur, um das Live-Installer-Icon
  umzubenennen)
- der offene Punkt „Calamares schlägt einen falschen Standort vor" -
  erledigt sich mit dem Werkzeug selbst

Auslöser der Entscheidung waren zwei Defekte, die beim ersten echten
Aufbau am 2026-08-16 auftraten: `calamares-settings-debian` legt per
`/etc/xdg/autostart/calamares-desktop-icon.desktop` bei **jedem** Login
ein Installer-Icon auf die Arbeitsfläche - auch bei `nutzer`, der einen
Installer nie sehen soll - und trug zusätzlich „Install Debian" in die
Anwendungsübersicht ein.

Das Aufbau-Skript behält die Nummer 5 bei, damit alle Querverweise auf
spätere Schritte gültig bleiben. Es entfernt Calamares samt Resten,
sofern vorhanden:

```bash
./scripts/dialos-full-office-setup.sh 05
```

Auf einer frischen Debian-Installation findet der Schritt nichts vor und
tut nichts - Calamares wird bei Weg A gar nicht erst installiert.

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
sudo npm install -g @anthropic-ai/claude-code
```

`sudo` ist hier Pflicht (korrigiert 2026-08-16 - vorher stand der Befehl
ohne, was auf einem frischen System nicht funktioniert hätte): Debians
npm-Prefix ist `/usr/local`, dort darf `dialosadmin` nicht schreiben, der
Befehl scheitert sonst mit `EACCES`.

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
  **Aussprache-Regel seit 2026-08-16:** Jeder Text läuft vor dem Sprechen
  durch `fuer_sprachausgabe()`, das "DialOS" zu "Dial OS" trennt - sonst
  liest Piper es als ein Wort. Bewusst zentral an dieser einen Stelle
  statt in jedem Ansagetext: So kann keine künftige Ansage die Trennung
  vergessen, und die Texte bleiben im Quelltext korrekt geschrieben.
  Weitere Aussprache-Regeln gehören ebenfalls dorthin. Nicht getroffen
  werden `dialosadmin` (kein Wortende nach "dialos") und `dialos.org`
  (Punkt ist ausgenommen).
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
  **Lautstärke-Abfrage seit 2026-08-14** (nur für `nutzer`, siehe
  TODO.md): Erste echte Vosk-Nutzung im Betrieb (vorher nur das
  Testskript `dialos-vosk-test.py`) - fragt "Wie laut soll ich sein?
  Sage 100, 75, 50, 25 oder aus.", nimmt 4 Sekunden per `parec` auf
  (Bluetooth-Mikrofon bevorzugt, inkl. `headset-head-unit`-
  Profilwechsel wie in `dialos-vosk-test.py`), erkennt mit dem kleinen
  deutschen Vosk-Modell. Ergebnis steuert Speech-Dispatchers eigene
  Lautstärke (`spd-say -i`, -100 bis +100) für den Rest der Ansage -
  neuer `--lautstaerke`-Parameter in `dialos-say.py`. Bei "aus" wird
  nur die Frage selbst (normale Lautstärke) gesprochen, der Rest der
  Ansage komplett ausgelassen.

  **Umgestellt am 2026-08-16 (Stephans Vorgabe): einmal fragen, dann
  merken - und zwar NACH der Ansage.** Bis dahin kam die Frage bei jedem
  Anmelden und noch vor der Ansage. Beides war ungünstig: Wer als
  Allererstes "Wie laut soll ich sein?" hört, hat noch keinen Anhaltspunkt,
  wie laut das System überhaupt ist - für einen blinden Nutzer ein
  sinnloser Maßstab. Jetzt läuft es so:

  - **Erstes Anmelden:** Ansage in normaler Lautstärke, danach die Frage
    ("War das angenehm laut? Du kannst es einmalig festlegen."). Die
    Antwort wird in `~/.config/dialos/lautstaerke` gemerkt - bei `nutzer`
    also auf der verschlüsselten Partition, genauso geschützt wie dessen
    übrige Daten. Anschließend eine Bestätigung **in der neu gewählten
    Lautstärke**, damit sofort hörbar ist, worauf man sich festgelegt hat.
  - **Jedes weitere Anmelden:** gemerkter Wert wird verwendet, es wird
    nicht mehr gefragt.
  - **Erneut fragen lassen:** die Datei löschen
    (`rm ~/.config/dialos/lautstaerke`), dann kommt die Frage beim
    nächsten Anmelden wieder.

  > **"aus" wird bewusst NICHT dauerhaft gespeichert**, sondern gilt nur
  > für die laufende Anmeldung. Wäre es dauerhaft, käme keine Ansage mehr -
  > und damit auch nie wieder diese Frage. Ein blinder Nutzer hätte ohne
  > fremde Hilfe keinen Weg zurück. Ein echter Dauer-Aus-Schalter braucht
  > erst einen anderen Rückweg (Sprachbefehl), siehe TODO.md.

  **Bei jedem Fehlschlag** (nichts/nichts Passendes verstanden, Vosk nicht
  verfügbar, kein Mikrofon) liefert die Funktion `None` und es wird
  **nichts** gemerkt - beim nächsten Anmelden wird also erneut gefragt, bis
  dahin bleibt es bei 100 %. Bewusst unterschieden von "der Nutzer hat 100
  gesagt": Nur eine echte Antwort wird festgeschrieben. Die Ansage darf
  wegen dieser Zusatzfrage nie ausbleiben oder hängen bleiben. Direkt nach der Frage folgt "Und
  jetzt bitte." als klares Startsignal für die Aufnahme - beim ersten
  echten Test mit Stephans Stimme fehlte dieses Signal noch, die Antwort
  wurde verpasst (nur der 100 %-Fallback kam an); mit dem Signal danach
  erfolgreich getestet (echtes "25" korrekt als 25 % erkannt, über das
  Bluetooth-Mikrofon inkl. `headset-head-unit`-Profilwechsel).
- `dialos-tts-indicator.py`: Panel-Icon, das anzeigt, wenn gerade
  gesprochen wird (braucht die AppIndicator-Erweiterung aus Schritt 9).
- `dialos-desktop-stil.sh`: schaltet die Optik des Desktops zwischen
  GNOME-Standard und Windows-11-Nachbau um (siehe unten).

### 11b. Optionale Windows-11-Optik (neu 2026-08-16)

**Warum das drin ist:** Es gibt Interessenten, die DialOS wegen der
Sprachsteuerung wollen, aber ihr Leben lang Windows benutzt haben. Für
die soll der Schreibtisch aussehen wie gewohnt - ohne dass DialOS deshalb
den barrierefreien GNOME-Unterbau (Orca, AT-SPI) aufgibt. Es wird deshalb
nichts ersetzt: GNOME bleibt, bekommt drei Erweiterungen obendrauf und
kann jederzeit in beide Richtungen zurückgeschaltet werden.

Die drei Erweiterungen kommen aus Debians eigenen Paketquellen (kein
Fremd-Repository, damit sie bei Systemaktualisierungen mitgepflegt
werden) und stehen seit 2026-08-16 in der Paketliste aus Schritt 2:

| Paket | UUID | Aufgabe |
|---|---|---|
| `gnome-shell-extension-dash-to-panel` | `dash-to-panel@jderose9.github.com` | Taskleiste unten |
| `gnome-shell-extension-arc-menu` | `arcmenu@arcmenu.com` | Startmenü (Layout `Eleven` = Windows-11-Nachbau) |
| `gnome-shell-extension-tiling-assistant` | `tiling-assistant@leleat-on-github` | Fenster-Andocken wie Windows-Snap |

Sie werden **mitinstalliert, aber nicht eingeschaltet**. Erst das Skript
aktiviert sie. Grund: Wer die Umschaltung erst bei Bedarf nachinstallieren
müsste, bräuchte dafür Internet und ein Admin-Passwort - beim Kunden ist
beides nicht vorausgesetzt.

Aufruf, **bewusst ohne `sudo`** (alle Einstellungen sind benutzereigen -
unter `sudo` landeten sie in `/root` und bewirkten beim Nutzer nichts):

```bash
/usr/local/bin/dialos-desktop-stil.sh windows   # Windows-11-Optik
/usr/local/bin/dialos-desktop-stil.sh gnome     # zurück zum Standard
/usr/local/bin/dialos-desktop-stil.sh status    # was ist gerade aktiv
```

Umgestellt wird: Taskleiste unten mit mittigen Symbolen (48 px),
ArcMenu-Layout `Eleven` links in der Leiste, **Fensterknöpfe rechts in der
Reihenfolge Minimieren/Maximieren/Schließen** (unter GNOME sitzt dort ab
Werk nur ein Schließen-Knopf - im Alltag die auffälligste Umstellung),
heiße Ecke oben links aus (wer Windows gewohnt ist, löst sie ständig
versehentlich aus) und Datum neben der Uhr. `tiling-assistant` braucht
keine Einstellung, es verhält sich ab Werk wie Windows-Snap.

Zurückschalten setzt alle berührten Schlüssel per `gsettings reset` auf
den **Auslieferungszustand** zurück, nicht auf selbst gewählte
"GNOME-artige" Werte - sonst wäre mehrfaches Hin- und Herschalten nicht
verlustfrei.

**Das Symbol auf dem Startknopf** ist ein eigenes, mitgeliefertes
Symbol (`/usr/local/share/dialos/dialos-fenster-symbolic.svg`, vier
Kacheln im Quadrat, ohne Rahmen) - **bewusst nicht das
Windows-Logo von Microsoft.** DialOS wird verkauft; ein fremdes
Markenzeichen auf dem Startknopf eines verkauften Geräts wäre ein
Markenrechtsproblem. Microsofts Zeichen ist eine perspektivisch gekippte
Vierergruppe ohne Rahmen in einem bestimmten Blau; das hier ist das
allgemeine Sinnbild für "ein Fenster" und wird von Windows-Gewohnten
trotzdem sofort als Startknopf gelesen. ArcMenu selbst bringt kein
Windows-Symbol mit und weist im Quelltext ausdrücklich darauf hin, dass
seine Distributions-Icons Marken ihrer Inhaber sind.

**Achtung beim Bearbeiten:** Die Datei muss nach der XML-Zeile **sofort**
mit `<svg` beginnen, ohne Kommentar davor - sonst erscheint auf dem Knopf
eine volle weiße Fläche, ohne jede Fehlermeldung. GNOME baut Symbol-Icons
beim Einfärben um und stolpert über alles, was vor dem `<svg>`-Tag steht.
Deshalb steht die Erklärung zur Datei in
`iso-build/config/includes.chroot/usr/local/share/dialos/README.md` und
nicht in der Datei selbst. Vorlage für neue Symbole ist immer eine
Adwaita-Datei; ein selbst gerendertes Vorschaubild beweist nichts, weil
librsvg die Datei so zeichnet, wie sie dasteht.

Die Datei endet auf `-symbolic.svg` und ist einfarbig, damit GNOME Shell
sie wie ein Symbol-Icon einfärbt: Sie nimmt die Vordergrundfarbe der
Leiste an und bleibt im hellen wie im dunklen Erscheinungsbild lesbar.
Ein fest eingefärbtes Icon wäre in einem der beiden Fälle unsichtbar -
für sehbehinderte Nutzer der Unterschied zwischen bedienbar und nicht
bedienbar. Fehlt die Datei, behält der Knopf sein bisheriges Symbol; ein
Startknopf ohne Bild wäre schlimmer als einer mit dem falschen.

**Zwei Stolpersteine, beide erst beim echten Testlauf am 2026-08-16
sichtbar geworden:**

- **Frisch installierte Erweiterungen kennt die laufende GNOME Shell
  nicht.** Sie durchsucht `/usr/share/gnome-shell/extensions` nur beim
  Start. Direkt nach `apt install` liegen die Dateien also auf der
  Platte, `gnome-extensions enable` antwortet aber mit "Erweiterung
  existiert nicht" - und unter Wayland lässt sich die Shell nicht im
  laufenden Betrieb neu starten. Das Skript trägt die UUIDs deshalb
  **immer zusätzlich direkt in `org.gnome.shell enabled-extensions`**
  ein (über Gio, nicht per Textbastelei an der `gsettings`-Ausgabe); die
  Shell schaltet sie dann beim nächsten Start ein. Erkennt es diesen
  Fall, sagt es ausdrücklich: "Sie erscheint erst, wenn du dich einmal
  abmeldest und wieder anmeldest." Ohne diesen Satz stünde ein blinder
  Nutzer vor einem Befehl, der scheinbar nichts tut.
- **Debians `gnome-shell-extension-arc-menu` (65-2) legt sein Schema in
  den falschen Ordner:** `/usr/share/glib-2/schemas/` statt
  `/usr/share/glib-2.0/schemas/`. Dadurch landet es nie im systemweiten
  Schema-Cache, und `gsettings` antwortet mit "Kein derartiges Schema" -
  alle drei ArcMenu-Einstellungen wurden beim ersten Testlauf still
  übersprungen (das Startmenü wäre im GNOME-Standardlayout erschienen
  statt im Windows-11-Layout). Die Erweiterung selbst läuft trotzdem,
  weil GNOME Shell das mitgelieferte `gschemas.compiled` im Ordner der
  Erweiterung liest. Genau dort sucht das Skript jetzt auch
  (`GSETTINGS_SCHEMA_DIR`), und zwar bewusst allgemein über alle drei
  Erweiterungs-Ordner: Behebt Debian den Tippfehler, greift automatisch
  wieder der systemweite Weg.

Drei weitere Details, die beim Bauen wichtig waren:

- **Kein `gsettings set` ins Blaue.** Das Skript prüft für jeden Schlüssel
  erst, ob das Schema ihn kennt. Ein Fehlschlag mitten in der Umschaltung
  würde sonst einen halb umgestellten Desktop hinterlassen - für einen
  blinden Nutzer nicht selbst zu reparieren.
- **Die mittige Taskleiste gilt nur für den Hauptbildschirm.**
  dash-to-panel legt diese Einstellung pro Monitor ab und benutzt dafür
  seit Version 56 die Seriennummer, fällt aber ausdrücklich auf den
  Bildschirm-Index zurück (`panelSettings.js`, `getMonitorSetting`) -
  deshalb schreibt das Skript auf `"0"`. Ein zweiter Monitor behält die
  Standardanordnung; das ist bewusst so, statt für eine Kosmetik die
  Monitor-Erkennung nachzubauen.
- **Die Rückmeldung wird gesprochen**, nicht nur geschrieben
  (`dialos-say.py`). Die Zielgruppe sieht den Bildschirm nicht - eine rein
  geschriebene Meldung wäre für sie dasselbe wie gar keine. Genau deshalb
  ist dieses Skript auch der vorgesehene **erste echte Sprachbefehl**,
  sobald die Befehlsgrammatik steht (siehe TODO.md).

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
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-rekey /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh /usr/local/sbin/
sudo chmod 755 /usr/local/sbin/dialos-rekey \
  /usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/dialos-setup-home-partition.sh
sudo mkdir -p /usr/share/applications
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
Sitzung).

**Was der Dienst beim Booten tut - zwei Ebenen seit 2026-08-16:**

1. **Autologin** für `nutzer` ein- bzw. ausschalten, je nachdem ob die
   Home-Partition entsperrt werden konnte.
2. **Das Konto `nutzer` sperren bzw. entsperren** (`usermod -L`/`-U`).
   Der Autologin allein reicht als Schutz nämlich nicht: Ohne Stick zeigt
   GDM weiterhin beide Konten an, und wer `nutzer`s Passwort kennt (es
   steht einmalig im Terminal, wenn `dialos-setup-nutzer.sh` es würfelt),
   könnte sich trotzdem anmelden. Dann wäre `/home/nutzer` **nicht**
   gemountet und die Sitzung liefe gegen ein Verzeichnis auf der
   **unverschlüsselten** root-Partition - im besten Fall scheitert sie an
   den Rechten, im schlechtesten legt sie dort ein Profil im Klartext an.
   Mit der Sperre ist die Frage gegenstandslos.

   **Reihenfolge ist dabei nicht beliebig:** erst entsperren, dann
   Autologin setzen - AccountsService lehnt `SetAutomaticLogin` für ein
   gesperrtes Konto mit "user is locked" ab. Beim Abschalten umgekehrt.
   `dialosadmin` wird nie gesperrt, du kannst dich also nicht aussperren.

**Test (am 2026-08-16 bestanden):** Stick abziehen, neu starten - das
System muss am normalen GDM-Anmeldebildschirm landen statt `nutzer`
automatisch anzumelden, und `/home/nutzer` darf nicht gemountet sein.
Danach Stick wieder einstecken und erneut neu starten - `/home/nutzer`
muss gemountet sein und der Autologin wieder greifen. Prüfen lässt sich
der Sperrzustand mit `sudo passwd -S nutzer` (`P` = nutzbar,
`L` = gesperrt).

**Home-Partition auf einem frisch installierten System anlegen**
(neu seit 2026-08-14, für den Weg über die Basis-Installation in
Schritt 1 statt über `dialos-install`s Ganze-System-Kopie):
`dialos-setup-home-partition.sh` übernimmt dieselbe LUKS/Stick-Logik
wie `dialos-install`, aber ohne dessen Festplatten-Wipe/rsync-Kopie -
nutzt stattdessen den in Schritt 1 bewusst frei gelassenen Platz am
Ende der System-Platte:

```bash
/usr/local/sbin/dialos-setup-home-partition.sh
```

**Bewusst ohne `sudo`** (korrigiert 2026-08-16): Das Skript hebt sich
selbst per `pkexec` auf Root-Rechte an und behält dabei die
Grafik-Umgebung. Mit `sudo` gestartet greift dieser Zweig nicht (man ist
ja schon root), und `sudo` entfernt gleichzeitig `DISPLAY`/`XAUTHORITY`
per `env_reset` - die Zenity-Dialoge könnten dann nicht aufgehen. Muss es
doch einmal über ein Terminal ohne Grafik laufen, fragt das Skript
Passwörter seit 2026-08-16 ersatzweise im Terminal ab, statt sich (wie
vorher) an dieser Stelle wortlos zu beenden.

Fragt nach Sicherheits-Stick, Wiederherstellungs-Passwort (≥12 Zeichen)
und Bestätigung ("LOESCHEN" eingeben), bietet danach das gleiche
verschlüsselte Nextcloud-Schlüssel-Backup wie `dialos-install` an. Am
Ende wird `/home/nutzer` gleich gemountet (kein Neustart nötig), sofern
`dialos-stick-gate.sh` schon installiert ist (siehe oben).

**Bei der Stick-Auswahl aufpassen:** Die Liste zeigt seit 2026-08-16 eine
Spalte "Bisheriger Inhalt" (Label + Dateisystem). Der gewählte Stick wird
komplett gelöscht - ohne diese Spalte war z. B. ein eingesteckter
Debian-Installationsstick in der Liste nicht von einem leeren Stick zu
unterscheiden.

### Swap verschlüsseln (Teil desselben Skripts, seit 2026-08-16)

Noch vor der Home-Partition fragt das Skript, ob ein vorgefundener
Klartext-Swap durch **8 GiB verschlüsselten Swap** ersetzt werden soll -
Entscheidung vom 2026-08-16, Begründung siehe Schritt 1. Es erledigt dabei:

- alten Swap abschalten (`swapoff`), Partition löschen, Swap-Zeilen aus
  `/etc/fstab` entfernen (Sicherungskopie:
  `/etc/fstab.dialos-vor-swap-umstellung`),
- 8 GiB neu am **Anfang** des freien Bereichs anlegen, damit der Rest der
  Platte eine zusammenhängende Region für `dialos-nutzer-home` bleibt,
- `/etc/crypttab`-Eintrag mit **`/dev/urandom` als Schlüsselquelle** -
  der Schlüssel wird bei jedem Start neu gewürfelt, es gibt also nichts
  aufzubewahren und nichts, was jemand finden könnte,
- `vm.swappiness=10` (`/etc/sysctl.d/99-dialos-swappiness.conf`): Swap ist
  Notpolster, kein Routine-Ziel - je weniger ausgelagert wird, desto
  weniger von `nutzer`s Daten verlässt überhaupt den Arbeitsspeicher,
- `RESUME=none` + `update-initramfs -u`, damit kein halb konfigurierter
  Ruhezustand zurückbleibt.

**Beim ersten echten Lauf gefunden (2026-08-16), jetzt behoben:**
- **`systemd-cryptsetup` muss installiert sein**, sonst ist der ganze
  crypttab-Eintrag wirkungslos. Debian 13 hat die Auswertung aus dem
  `systemd`-Paket herausgelöst; ohne das Paket existiert weder
  `/usr/lib/systemd/system-generators/systemd-cryptsetup-generator` noch
  `systemd-cryptsetup@.service`, und der Swap bleibt beim Booten einfach
  inaktiv - **ohne jede Fehlermeldung**. Das Paket steht jetzt in der
  Paketliste (Schritt 2), und das Skript prüft es zusätzlich, bevor es die
  Partitionstabelle anfasst. Dass die Home-Partition davon nichts merkt,
  liegt daran, dass `dialos-stick-gate.sh` sie selbst per
  `cryptsetup open` öffnet - deshalb fällt das Fehlen nur beim Swap auf.
- Die neue Swap-Partition wird nach dem Anlegen mit `wipefs -a` gesäubert.
  Sie beginnt am selben Offset wie die alte, deren Swap-Header sonst
  stehen bliebe: `blkid` meldete danach weiterhin `swap` samt **alter**
  UUID auf einer Partition, die künftig verschlüsselt wird.
- Die fstab-Zeile bekommt `nofail`. Ein fehlender Swap ist ein
  Komfortproblem, ein blockierter Start auf einem Gerät für blinde Nutzer
  ein echtes.
- Die Sofort-Aktivierung läuft direkt über `cryptsetup open --type plain`
  + `mkswap` + `swapon`, nicht über `systemctl start`: die
  crypttab-Unit existiert vor dem nächsten Boot noch gar nicht, ein
  `systemctl start` darauf tut nichts und meldet auch keinen brauchbaren
  Fehler.

**Wichtige Details zur Begründung:**
- Der crypttab-Eintrag zeigt bewusst auf `/dev/disk/by-partuuid/…`, nicht
  auf eine Dateisystem-UUID: die Option `swap` legt bei jedem Start ein
  frisches Dateisystem an, die Dateisystem-UUID ändert sich also ständig.
- **Der Ruhezustand (Hibernate) ist damit endgültig ausgeschlossen** - das
  Abbild ließe sich nach einem Neustart nicht mehr entschlüsseln. Kein
  Verlust: Bei diesem Sicherheitsdesign war Hibernate ohnehin unmöglich,
  weil das Abbild `nutzer`s entschlüsselte Daten enthielte und beim Booten
  vor allem anderen lesbar sein müsste - genau der verworfene
  `cryptsetup-initramfs`-Ansatz. Der Standby (Suspend-to-RAM) ist davon
  **nicht** betroffen und funktioniert weiter.
- **Warum überhaupt Swap, statt ihn wegzulassen:** Ohne Swap beendet der
  Kernel bei Speichermangel Prozesse hart (OOM-Killer). Auf einem Gerät
  für blinde Nutzer kann das den Screenreader oder die Sprachausgabe
  treffen - der Nutzer bekäme dann ohne Vorwarnung keinerlei Rückmeldung
  mehr und könnte das Gerät nicht mehr bedienen. 8 GiB sind das Notpolster
  dagegen.
- **Warum 8 GiB und nicht so viel wie RAM:** Die Faustregel "Swap ≥ RAM"
  existiert nur wegen Hibernate. Ohne Hibernate ist alles darüber
  verschenkter Platz, der besser `nutzer`s Daten zur Verfügung steht.

**Wichtig für Schritt 13:** `scripts/dialos-setup-nutzer.sh` legt
`nutzer`s Konto erst an, nachdem es geprüft (und notfalls per
`dialos-stick-gate.sh` selbst ausgelöst) hat, dass `/home/nutzer`
bereits gemountet ist - **`dialos-setup-home-partition.sh` muss also
vor Schritt 13 gelaufen sein und der Sicherheits-Stick beim Ausführen
von Schritt 13 noch eingesteckt sein**, sonst bricht das Skript
kontrolliert ab (siehe sicherheit-datenschutz.md).

## 13. Nutzer-Konto anlegen + Büro-Setup abschließen

Sammel-Skript, das seit 2026-08-16 **alle vier** Teilschritte in einem
Rutsch erledigt (siehe [`scripts/README.md`](../scripts/README.md)) -
vorher waren die Teilschritte 2a-2c unten reine Handarbeit aus dieser
Doku und damit die letzte Lücke, die den Aufbau davon abhielt, komplett
aus Skripten zu bestehen:

```bash
sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
```

Der Sicherheits-Stick muss dabei **noch stecken** (siehe Schritt 12).
Das Skript erledigt nacheinander:

1. `dialos-set-avatar.sh` - setzt `distributor-logo.png` als Profilbild
   für das Admin-Konto (per `gdbus`/AccountsService `SetIconFile`).
2. **Admin-Werkzeuge auf `dialosadmin`s Arbeitsfläche** (neu im Skript
   seit 2026-08-16):
   - a) die Skripte aus `scripts/` (`chmod 755`),
   - b) die Claude-Desktop-App (`apt-get download claude-desktop`,
     `chmod 644`) - wird bei jedem Büro-Setup frisch geladen und bewusst
     nicht ins Repo committet; fehlt das Paket in den Quellen, wird der
     Teilschritt übersprungen statt den Lauf abzubrechen,
   - c) ein klickbares Startsymbol für `dialos-rekey` (Ersatz für einen
     verlorenen Sicherheits-Stick), inklusive
     `gio set … metadata::trusted true`.
3. `dialos-setup-nutzer.sh` - legt `nutzer` an (`adduser
   --disabled-password`, Gruppen `sudo,audio,video,plugdev,netdev,
   bluetooth,scanner,lpadmin,cdrom`, zufälliges Sudo-Passwort), schaltet
   Autologin von `dialosadmin` auf `nutzer` um (Wiederholungslogik gegen
   einen Timing-Bug: "user is locked" direkt nach `chpasswd`, weil
   AccountsService die neue Passwort-Zeile noch nicht bemerkt hatte).
4. Prüft, ob die Firefox-Startseiten-Policy aus Schritt 10 korrekt sitzt.

> **Zwei Fallen beim `nutzer`-Konto, gefunden beim ersten echten Lauf
> (2026-08-16), beide behoben:**
>
> 1. **`adduser` fasst ein vorhandenes Home nicht an.** Bei diesem
>    Aufbauweg ist `/home/nutzer` der Normalfall schon vorhanden -
>    `dialos-setup-home-partition.sh` legt die verschlüsselte Partition an
>    und mountet sie, *bevor* das Konto existiert. `adduser` meldet dann
>    "The home directory already exists. Not touching this directory" und
>    lässt daraufhin **beides** bleiben: den `chown` auf den neuen
>    Benutzer *und* das Kopieren von `/etc/skel`. Ergebnis war ein Home,
>    das `root:root` gehörte - `nutzer` hätte sein eigenes Verzeichnis
>    nicht beschreiben können, GNOME weder `~/.config` noch `~/.cache`
>    anlegen. Bei einem Konto, das per Autologin startet und dessen
>    Nutzer blind ist, ein Totalausfall ohne Selbsthilfemöglichkeit.
>    `dialos-setup-nutzer.sh` arbeitet das jetzt nach (skel kopieren,
>    `chown`, `chmod 700`) - das Kopieren nur, wenn das Home außer
>    `lost+found` leer ist, damit vorhandene Daten nie überschrieben
>    werden.
> 2. **`/etc/skel` des echten Systems wurde nie befüllt.** Die Schritte 9
>    und 10 kopierten die DialOS-Vorlagen aus dem Repo bisher nur in
>    `dialosadmin`s Home. `nutzer` hätte damit weder die
>    Bluetooth-Akku-Erweiterung noch Thunderbird als Standard-Mailprogramm
>    noch die Nautilus-Lesezeichen bekommen - obwohl Schritt 9 `/etc/skel`
>    ausdrücklich als Weg "für neue Konten automatisch" nennt. Beide
>    Schritte legen die Dateien jetzt zusätzlich unter `/etc/skel/` ab.
>    **Wichtig:** dorthin gehören ausschließlich Nutzer-Voreinstellungen,
>    niemals die Admin-Skripte (siehe die Korrektur vom 2026-08-14 direkt
>    darunter).

**Warum Teilschritt 2 so aussieht, wie er aussieht** (wichtige Korrektur
vom 2026-08-14, gilt weiterhin): Alle Skripte in `scripts/` sind **nur
für `dialosadmin`** gedacht - `nutzer` soll sie nie zu Gesicht bekommen.
Sie werden deshalb **nicht** über `/etc/skel/Desktop/` verteilt, sondern
gezielt auf das bereits existierende `dialosadmin`-Konto kopiert:
`/etc/skel/` wirkt nur bei Konten, die *danach* angelegt werden - bei
diesem Rezept ist das ausschließlich `nutzer`, nicht ein weiteres
Admin-Konto. Ein früherer Versuch über `/etc/skel/Desktop/` landete
genau deshalb ungewollt auf `nutzer`s Desktop. Aus demselben Grund gilt
das auch für die Claude-Desktop-`.deb`.

`gio set … metadata::trusted true` ist Pflicht - ohne diesen Schritt
zeigt Nautilus beim ersten Doppelklick eine "nicht vertrauenswürdig"-
Warnung, statt das Programm zu starten (anders als bei den
`.sh`-Skripten auf demselben Desktop, die über die
Textdatei-Ausführen-Einstellung laufen, nicht über den
Launcher-Vertrauensmechanismus). Das Merkmal liegt in der
Metadaten-Ablage des jeweiligen **Benutzers**, das Skript führt den
Befehl deshalb per `runuser` als `dialosadmin` aus, nicht als root. Läuft
gerade keine Sitzung dieses Kontos, meldet es das und man bestätigt beim
ersten Doppelklick einmalig "Vertrauen und starten".

Das Skript nimmt die Vorlage für das Startsymbol bewusst aus
`/usr/share/applications/dialos-rekey.desktop` (dort abgelegt in
Schritt 12; bis 2026-08-16 stand hier `dialos-install.desktop`, das mit
dem Werkzeug entfallen ist) statt aus dem Repo - so funktioniert es auch, wenn es später
von der Arbeitsfläche aus gestartet wird, wo es kein Repo-Verzeichnis
gibt.

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

`pip3` selbst (`python3-pip`) und `unzip` für die Modelle weiter unten
kommen aus der Paketliste in Schritt 2 - beide sind auf einer frischen
Debian-13-Installation nicht zwingend vorhanden und wurden am 2026-08-16
dort nachgetragen.

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

## 16. Sicherungs-Abbild (Clonezilla)

**Entscheidung vom 2026-08-16: Penguins' Eggs entfällt, Clonezilla
übernimmt.** Bis dahin stand hier `eggs produce`. Mit Weg A (siehe
Schritt 5) wird aus der ISO aber kein Installationsmedium mehr - kein
Gerät wird davon installiert, jedes entsteht aus der Debian-ISO plus den
drei Skripten. Übrig blieb der Zweck "Sicherungs-Schnappschuss", und
dafür ist Clonezilla das passendere Werkzeug: Es liegt in Debian
(`clonezilla`), braucht also kein Fremd-Repository, und tut genau eine
Sache.

Auslöser war, dass `eggs` beim Neuaufbau schlicht fehlte: Es ist nicht in
Debians Paketquellen, stand in keiner Paketliste, und **wie es installiert
wird, war nirgends dokumentiert** - weder in dieser Anleitung noch in der
Commit-Historie. Dieselbe Sorte Lücke wie bei `check_piper_voice.sh`:
einmal von Hand gemacht, nie aufgeschrieben, beim Reinstall verloren.

**Stephan erstellt das Abbild selbst mit einer Clonezilla-Variante mit
grafischer Oberfläche** - deshalb steht hier keine Klick-Anleitung.
Festgehalten sind nur die drei Punkte, die man wissen muss, weil sie sich
aus dem DialOS-Aufbau ergeben und beim ersten Mal überraschen:

1. **Clonezilla läuft nicht aus dem laufenden System.** Die Systemplatte
   muss unbenutzt sein, es wird also von einem eigenen Medium gebootet.
2. **Die verschlüsselte Partition gehört NICHT ins Abbild.** Bei ext4 und
   vfat sichert Clonezilla nur belegte Blöcke - root sind damit rund
   15 GB statt 93. In `dialos-nutzer-home` (LUKS2) kann es aber nicht
   hineinsehen und kopiert Byte für Byte alle ~375 GB; verschlüsselte
   Daten lassen sich zudem nicht komprimieren. Deshalb nur `nvme0n1p1`
   (root) und `nvme0n1p2` (EFI) auswählen. Die Swap-Partition ebenfalls
   weglassen - sie wird bei jedem Start ohnehin neu erzeugt.
3. **Das Abbild enthält damit `nutzer`s Daten nicht.** Das ist die Kehr-
   seite der Verschlüsselung und beabsichtigt. Sollen die auch gesichert
   werden, braucht es einen zweiten Weg im **entsperrten** Zustand, also
   eine Dateisicherung statt eines Abbilds.

Werden nur einzelne Partitionen gesichert, ist die Partitionstabelle
nicht mit dabei. Der Rückweg lautet dann: Debian per Preseed
installieren (Schritt 1 legt EFI + 100 GiB root an), danach das Abbild
darüberspielen.

> **Der eigentliche Schnappschuss ist inzwischen dieses Repository.** Am
> 2026-08-16 hat sich gezeigt, dass aus einer nackten
> Debian-Installation in drei Befehlen das komplette System entsteht -
> Skript 1 lief in 5-6 Minuten inklusive 1,9 GB Modell-Download. Ein
> Abbild sichert *einen Zustand*, das Rezept sichert die *Fähigkeit, ihn
> herzustellen*. Letzteres altert nicht, weil es bei jedem Gerät neu
> geprüft wird. Das Abbild spart vor allem Zeit beim Wiederherstellen.

## Praxishinweis: externe Platte

Da Build- und Test-System oft dasselbe Gerät sind und eine Installation
die interne Platte überschreibt, empfiehlt es sich, dieses Repository
(und die gebauten ISOs) auf einer externen Platte zu halten, damit ein
Reinstall des Testgeräts sie nicht mitreißt.

**Zweiter Zweck seit 2026-08-16:** Die Platte ist gleichzeitig die
Preseed-Quelle bei jeder Installation. Das Zielgerät wird ja gerade
plattgemacht und kann die Datei nicht selbst ausliefern - also steckt man
die Platte an einen beliebigen zweiten Rechner und startet dort
[`scripts/dialos-preseed-server.sh`](../scripts/dialos-preseed-server.sh)
(siehe Schritt 1a). Der zweite Rechner braucht dafür nichts außer
`python3` und dasselbe Netz. Das Skript leitet den Repo-Pfad aus seinem
eigenen Ort ab, es ist also egal, wo die Platte eingehängt wird. Nach
jedem Reinstall: Git-Identität (`git config user.name`/`user.email`)
und ggf. ein Symlink wie `~/DialOS` auf den externen Repo-Pfad neu
setzen.

## Was hier bewusst NICHT drinsteht

Diese Anleitung deckt den Weg bis 0.5.0 ab. Bekannte offene
Baustellen (Wake-Word-Engine, Bluetooth-Mikrofon-Fallback,
Rechtschreibprüfung, endgültige sudo-Policy für `nutzer`, u. a.) stehen
in [offene-punkte.md](offene-punkte.md); kleinere, konkrete
Nacharbeiten in [TODO.md](../TODO.md).
