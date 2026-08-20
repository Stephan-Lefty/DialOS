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

> **Schnellweg (Stand 2026-08-19): fünf Befehle von Debian zu DialOS.**
> Bis zum 2026-08-19 waren es drei; die beiden neuen räumen auf, was Debian
> mitbringt und DialOS nicht braucht (Stephans Vorgabe, siehe Schritt 13b).
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
>
> # 4) Schritt 13b - entfernt, was Debian mitbringt und DialOS nicht braucht.
> #    ERST ohne --wirklich aufrufen und die Liste ansehen:
> ./scripts/dialos-aufraeumen.sh
> sudo ./scripts/dialos-aufraeumen.sh --wirklich
>
> # 5) Schritt 13c - Menue pro Konto: nutzer sieht nur seine Anwendungen,
> #    dialosadmin alles. Ebenfalls erst ohne --wirklich:
> ./scripts/dialos-menue-pro-konto.sh
> sudo ./scripts/dialos-menue-pro-konto.sh --wirklich
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
siehe [Beispiel](beispiele/gdm3-custom.conf)) ist bei dieser
Debian-13/GDM-48-Kombination **nicht** der wirksame Schalter - der eigentliche Mechanismus ist eine Pro-Benutzer-Eigenschaft
im laufenden AccountsService, per D-Bus gesetzt.

> Die Beispieldatei liegt bewusst unter `docs/beispiele/` und **nicht** in
> `iso-build/config/includes.chroot/` (verschoben am 2026-08-20). Alles dort
> heißt „installiere mich" - und eine Datei zu installieren, deren ganze
> Aussage ist, dass sie nichts bewirkt, verwirrt nur. Aufgefallen ist es, weil
> `scripts/dialos-installstand.sh` sie dauerhaft als „nicht installiert"
> meldete. Ein Prüfwerkzeug, das ständig bekannte Einträge zeigt, erzieht dazu,
> es zu ignorieren; dann findet es beim nächsten echten Fund auch niemand mehr.
>
> `custom.conf` ist übrigens der **Ubuntu**-Dateiname. Debian benutzt
> `daemon.conf` - dort steht auf dem Testgerät tatsächlich ein
> `AutomaticLogin`, gesetzt vom Debian-Installer. Wirksam ist trotzdem die
> AccountsService-Eigenschaft, siehe unten.

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
  **Ansagen-Speicher seit 2026-08-17:** Erzeugen und Abspielen eines
  Satzes kostete gut 2,2 Sekunden, davon rund 1,1 Sekunden reiner
  Vorlauf - jedes Mal neu berechnet für Sätze wie "Ich höre.", die sich
  nie ändern. Gesprochene Sätze landen deshalb als WAV unter
  `~/.cache/dialos/ansagen` und werden beim nächsten Mal von dort
  gespielt (gemessen: 2172 ms → rund 1200 ms, und davon sind 1,13 s die
  Ansage selbst). Der Speicher füllt sich von selbst: Beim ersten Mal
  läuft der normale Weg, die Aufzeichnung passiert nebenbei im
  Hintergrund. Es gibt also keine Liste zu pflegen. **Der Schlüssel ist
  ein Hash aus Text + Änderungszeit von `PIPER_CONF` und dem
  Stimmen-Ordner** - ändert sich Tempo oder Stimme, entstehen neue
  Schlüssel und der alte Bestand wird nicht mehr gefunden; ohne das
  spräche DialOS nach einer Tempoänderung teils im alten, teils im neuen
  Tempo. Der Speicher darf jederzeit gelöscht werden, er baut sich neu
  auf.
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
  (seit 2026-08-17 über die echo-bereinigte Quelle am **eingebauten**
  Mikrofon statt wie zuvor über Bluetooth mit `headset-head-unit`-
  Profilwechsel - siehe Schritt 11f), erkennt mit dem kleinen
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

### 11a. Fragen klingen anders als Hinweise (neu 2026-08-17)

Für jemanden, der den Bildschirm nicht sieht, ist „wartet es gerade auf
mich?" die entscheidende Information. Am 2026-08-16 ist genau daran der
erste Test der Lautstärke-Frage gescheitert: Das System fragte, aber
Stephan wusste nicht, wann er antworten soll - die Antwort ging verloren.

`dialos-say.py` kennt deshalb den Schalter **`--frage`**:

```bash
dialos-say.py --frage "War das angenehm laut?"
```

**Standard ist die natürliche Satzmelodie.** Piper ist auf Text mit
Satzzeichen trainiert und erzeugt aus dem Fragezeichen von selbst eine
steigende Melodie - im Hörvergleich am 2026-08-17 gegen eine höhere
Tonlage und gegen einen Signalton gestellt, und von Stephan als beste
Variante gewählt. Sie klingt natürlich und nutzt sich nicht ab.

**Der Signalton ist die Option.** Eingeschaltet über
`~/.config/dialos/frageton` mit dem Inhalt `an`, abgespielt wird
`/usr/local/share/dialos/frage-ton.wav`. Der Grund, ihn überhaupt
anzubieten: Eine steigende Satzmelodie am Ende erkennt nur, wer zugehört
hat - wer den Anfang verpasst hat oder nebenbei Radio hört, braucht ein
Signal, das davon unabhängig ist. Deshalb eine Einstellung und keine
Festlegung.

**Warum ein Schalter im Code und nicht „erkenne das Fragezeichen
selbst":** Ein Fragezeichen kann auch mitten in einem Hinweis stehen, und
eine rhetorische Frage will kein Signal. Der Code, der die Ansage baut,
*weiß*, ob er etwas wissen will - diese Information soll er weitergeben,
statt sie am Satzzeichen raten zu lassen. Nachgewiesen am 2026-08-17: Bei
eingeschalteter Option bekommt eine mit `--frage` markierte Frage den
Ton, ein gewöhnlicher Hinweis nicht.

Bisher einziger Anwendungsfall: die Lautstärke-Frage der Start-Ansage.

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

### 11c. Sprachbefehl für die Umschaltung (neu 2026-08-16)

`dialos-sprachbefehl-desktop.py` ist der **erste dauerhaft lauschende
Dienst in DialOS** - bis dahin wurde Vosk nur punktuell aufgerufen (die
Lautstärke-Frage der Start-Ansage). Er hört über das Mikrofon mit und
schaltet auf Zuruf um:

> "auf Linux umschalten" &nbsp;·&nbsp; "auf Windows umschalten"

"auf Gnome umschalten" gilt gleichbedeutend mit Linux. Gestartet wird er
über `/etc/xdg/autostart/dialos-sprachbefehl-desktop.desktop` in jeder
Sitzung.

**Der Befehl ist bewusst ein ganzer Satz, kein Einzelwort** (Stephans
Vorgabe). Ein einzelnes "Windows" fällt im Gespräch ständig; der
Schreibtisch würde sich ungefragt umstellen, und ein blinder Nutzer
wüsste nicht, warum plötzlich alles anders klingt. Deshalb muss der
erkannte Satz **beides** enthalten: das Ziel *und* das Wort
"umschalten".

Fünf Punkte, die beim Bauen entschieden wurden - alle am 2026-08-16 mit
synthetisch gesprochenen Sätzen (Piper spricht, Vosk hört) nachgemessen:

| Entscheidung | Grund |
|---|---|
| **Eingeschränkte Grammatik** statt freier Erkennung | Voraussetzung, keine Optimierung: Frei erkannt wurde "gnome" zuverlässig als **"genug"**. Mit Grammatik lagen alle drei Sätze wörtlich richtig. Kostet nebenbei viel weniger Rechenzeit - bei einem Dauerdienst zählt das für den Akku. |
| **Eingebautes Mikrofon** statt Bluetooth | Das AIRHUG kann A2DP und HFP nicht gleichzeitig. Bei der einmaligen Lautstärke-Frage ist die Telefonqualität ein kurzer Moment - bei dauerhaftem Zuhören wäre die Wiedergabe **für immer** verschlechtert. Drei feste Sätze zu unterscheiden gelingt auch mit dem eingebauten Mikrofon. |
| **Während das System spricht, wird nicht zugehört** | Sonst hört sich der Dienst selbst. Seine eigene Ansage kann Ziel *und* "umschalten" enthalten - die Satz-Bedingung würde sie also gerade nicht abfangen. Ausgewertet wird die Markierungsdatei, die `dialos-say.py` ohnehin setzt. |
| **Keine Rückfrage, aber eine Ansage** | Ein "Willst du wirklich?" bei jedem Befehl wäre lästig. Stattdessen sagt das System, was es getan hat - wer es nicht wollte, sagt einfach den anderen Satz. Ein Fehlgriff ist damit in Sekunden rücknehmbar, ohne hinsehen zu müssen. |
| **Sperrfrist von 2 s** nach einem Umschalten | Sonst löst ein langgezogener Satz mehrfach aus. Waren zuerst 5 s und galten auch nach "Ich höre." - siehe unten, das war ein Fehler. |

Der Gegentest, der die Satz-Bedingung rechtfertigt: Der gesprochene Satz
"ich habe früher windows benutzt" wurde als `auf auf windows` erkannt -
also durchaus mit dem Wort "windows", aber **ohne** "umschalten". Er
löste nichts aus.

**Die Sperrfrist ist seit 2026-08-17 ganz entfallen** - in zwei Schritten,
und der erste war nur eine halbe Behebung. Zuerst galt sie auch hinter den
Ansagen "Ich hoere." und "Ich hoere nicht mehr.", dann nur noch nach
echtem Umschalten mit 2 s, jetzt nicht mehr. Der Grund fuer den zweiten
Schritt: Nach einem Umschalten war der Dienst rund **fuenf Sekunden** taub
- 2,4 s laeuft das Umschalt-Skript und spricht dabei, 2,0 s Sperrfrist,
0,7 s Nachhall-Pause. Die Ansage endet aber schon nach 1,5 s, der Nutzer
spricht also 3,6 Sekunden gegen ein taubes System. Noetig war sie
ohnehin nicht mehr: Das Verwerfen und Neubeginnen der Aufnahme nach jedem
Sprechen verhindert Doppelausloesung vollstaendig.

**Der alte Text dazu, weil die Diagnose lehrreich ist:**
Vorher stand sie auch hinter den Ansagen "Ich höre." und "Ich höre nicht
mehr." - der Dienst war damit ausgerechnet in den fünf Sekunden nach
"Ich höre." taub, also genau dann, wenn der Nutzer seinen Befehl sagt.
Für Stephan sah das aus wie ein Lautstärkeproblem ("ich muss sehr laut
reden"): Er sprach, nichts geschah, er wiederholte lauter - und dann war
die Frist abgelaufen. Aufgefallen ist es erst durch seine Präzisierung,
dass der *zweite* Befehl das Problem war, nicht der erste. Gegen die
eigene Stimme schützt ohnehin schon das Verwerfen und Neubeginnen der
Aufnahme nach jedem Sprechen.

**Die Ansagen nach dem Umschalten** lauten "Linux Desktop." und "Windows
Desktop." (1,5 s). Sie waren zuerst ein erklärender Satz über Taskleiste
und Startmenü - rund acht Sekunden, in denen der Dienst bewusst nicht
zuhört, also acht Sekunden Wartezeit vor dem nächsten Befehl. Der Weg
zurück über ein einzelnes "Windows." war dann zu kurz: ein Stichwort,
kein Satz - wer nur zuhört, weiß nicht, ob das die Antwort auf seinen
Befehl war. **Steht der Schreibtisch schon auf dem angesagten Stil**,
lautet die Ansage "Steht schon auf Linux Desktop." Der Stil wird trotzdem
neu gesetzt (dieselbe Zusicherung wie beim Wiederherstellen), nur die
Ansage unterscheidet - vorher war ein wirkungsloser Befehl von einem
echten Wechsel nicht zu unterscheiden, wenn man den Bildschirm nicht
sieht.

### 11d. Deutsches Menü und Erhalt über den Neustart

**Deutsches ArcMenu-Menü:** Debians Paket liefert die fertig übersetzte
`de.mo` mit, legt sie aber nach `po/` statt in einen `locale`-Ordner -
dort findet sie niemand, und das Startmenü bleibt englisch.
GNOME-Erweiterungen ohne eigenen `locale`-Ordner suchen in
`/usr/share/locale`, also wird sie dorthin kopiert (kein `msgfmt` nötig,
die Datei ist bereits kompiliert). Zweiter Fehler im selben Paket wie der
Schema-Pfad aus Schritt 11b. `dash-to-panel` bringt sein Deutsch selbst
korrekt mit; `tiling-assistant` hat gar keine Übersetzung, zeigt in der
Leiste aber auch keinen Text.

**Erhalt über Neustart und Abmelden:** Die gewählte Optik bleibt, weil
alle Einstellungen in dconf des jeweiligen Kontos liegen - das übersteht
Neustarts von sich aus. Zusätzlich wird
`dialos-desktop-stil.sh wiederherstellen` über
`/etc/xdg/autostart/dialos-desktop-stil-wiederherstellen.desktop` beim
Anmelden ausgeführt (ohne
Ansage, weil dabei niemand etwas ausgelöst hat). Das ist die Zusicherung
für den Fall, dass etwas anderes die Erweiterungsliste zurückgesetzt hat -
eine Systemaktualisierung, ein versehentliches `dconf reset`, ein neu
angelegtes Konto. Für einen blinden Nutzer wäre ein Schreibtisch, der
nach dem Einschalten anders aussieht als zuletzt, kein Schönheitsfehler,
sondern Orientierungsverlust. Gibt es noch keine Merkdatei, tut der
Aufruf bewusst nichts.

**„Ohne Ansage" war bis zum 2026-08-17 nicht wahr.** Der Aufruf im
Skript ist mit `>/dev/null 2>&1` umgeleitet, und diese Zeile hier hat
das als Beleg für „stumm" gelesen. Die Umleitung schluckt aber nur die
Terminal-Zeile - `melde()` ruft die Sprachausgabe direkt auf, und die
spricht weiter. **Bei jedem Anmelden hat der Schreibtisch also ungefragt
geredet**, mitten in die Start-Ansage hinein, weil beide Autostarts
gleichzeitig loslaufen. Genau das hatte Stephan gemeldet („die Ansage
mit dem Desktop kam dazwischen"), es war aber als Zeitproblem zwischen
zwei Autostarts abgelegt worden. Seitdem gibt es die Variable `STUMM`:
`wiederherstellen` setzt sie auf 1, `melde()` überspringt dann das
Sprechen - die Terminal-Zeile bleibt. Beim Prüfen zählt die Dauer: Der
Aufruf braucht rund 800 ms; käme die Ansage dazu, wären es über 1800 ms.

### 11e. Mikrofon-Aufnahmepegel (neu 2026-08-16)

**Das ist kein Feinschliff, sondern die Voraussetzung dafür, dass
Spracherkennung überhaupt funktioniert.** Auf dem T490 standen ab Werk
zwei Verstärkungsstufen auf Anschlag: `Capture` auf +30 dB *und*
zusätzlich `Internal Mic Boost` auf +30 dB, zusammen 60 dB. Gemessen:

| Zustand | RMS-Pegel | gesättigte Abtastwerte |
|---|---|---|
| ab Werk (`Internal Mic Boost` +30 dB) | 76 % | **50 %** |
| nach der Korrektur (Boost 0 dB) | 2,8 % | 0 % |

Die Folge war kein Rauschen, sondern **Stille auf der Bedienseite**:
Vosk erkennt Sprache anhand der Pausen zwischen den Wörtern. In einem
Dauervollausschlag gibt es keine Pausen, also liefert der Erkenner nie
ein Ergebnis. Der Sprachbefehl-Dienst lief, hörte zu und konnte
prinzipiell nichts verstehen - ohne jede Fehlermeldung. Für ein System,
das ausschließlich per Sprache bedient wird, ist das der Totalausfall.

Behoben durch `/usr/local/sbin/dialos-mikrofon-pegel.sh` samt
`dialos-mikrofon-pegel.service`, das bei jedem Start läuft. Zwei
Entscheidungen dabei:

- **Boost auf Null, nicht auf einen Mittelwert.** Ein zu leises Signal
  lässt sich in Software nachverstärken; ein übersteuertes ist
  unwiederbringlich zerstört, die Spitzen sind abgeschnitten. Im Zweifel
  lieber zu leise.
- **Ein Dienst statt `alsactl store`.** `alsactl store` schreibt den
  kompletten Mixer-Zustand *dieser* Karte nach
  `/var/lib/alsa/asound.state` - gerätespezifisch, und damit nichts, was
  sich in die ISO-Vorlage legen ließe. Das Skript sucht die Regler
  stattdessen über ihren Namen (`*Mic Boost*`, `Capture`) und läuft auf
  jedem Gerät, auch wenn die Karte anders heißt oder nummeriert ist.
  `alsactl store` wird zusätzlich aufgerufen, als zweite Sicherung.

**Dieser Fund stellt eine ältere Schlussfolgerung in Frage:** Der
Mikrofon-Vergleich vom 2026-08-13 kam zu dem Ergebnis, das eingebaute
Mikrofon sei dem AIRHUG deutlich unterlegen. Wenn schon damals 60 dB
anlagen, hat der Test nicht das Mikrofon gemessen, sondern die
Übersteuerung. Der Vergleich gehört wiederholt, bevor die
Bluetooth-Priorität als bewiesen gilt (siehe TODO.md).

### 11f. Echo-Unterdrückung fürs Mikrofon (neu 2026-08-17)

**Ohne sie hört der Sprachbefehl-Dienst alles mit, was das Gerät
abspielt** - die eigene Ansage ebenso wie Radio, Musik oder eine
Mediathek. Weil die Erkennung mit einer eingeschränkten Grammatik
arbeitet, presst sie Bruchstücke davon in einen Befehl: Beim Vorspielen
der Start-Ansage schaltete sich der Desktop mitten in der Wiedergabe um.
Für ein System, das Radio und Musik abspielen soll, ist das kein
Randfall - ein Nachrichtensprecher, der „Windows" sagt, würde denselben
Effekt auslösen.

Der frühere Schutz (Markierungsdatei „das System spricht gerade") kann
das prinzipiell nicht lösen: Er kennt nur die eigene Ansage über
`dialos-say.py`. Deshalb setzt die Lösung eine Stufe tiefer an, in der
Audiokette.

`/etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf` lädt
PipeWires `module-echo-cancel` mit dem WebRTC-Algorithmus und stellt eine
bereinigte Quelle **`dialos_mikrofon_ohne_echo`** bereit.
`dialos-sprachbefehl-desktop.py` nimmt sie als erste Wahl.

**Gemessen am 2026-08-17**, beide Quellen gleichzeitig aufgenommen,
während der Lautsprecher die Start-Ansage abspielte:

| Quelle | Pegel |
|---|---|
| rohes Mikrofon | 6,13 % RMS |
| `dialos_mikrofon_ohne_echo` | **0,15 % RMS** |

Das sind rund **32 dB** Dämpfung - und zwar über Bluetooth, wo wegen der
schwankenden Laufzeit deutlich weniger zu erwarten gewesen wäre.
Gegenprobe: dieselbe Ansage per `paplay` abgespielt, also ohne jeden
Schutz - der Dienst erkannte **nichts** und schaltete nicht um.

Zwei Entscheidungen in der Konfiguration:

- **`monitor.mode = true`.** Ohne diese Option müssten alle Programme
  ihren Ton in eine eigens angelegte Senke spielen, damit das Modul
  weiß, was gerade zu hören ist - jede Audio-Ausgabe von DialOS wäre
  umzubiegen, und jedes neue Programm müsste daran denken. Mit
  `monitor.mode` nimmt das Modul den Mitschnitt der Ausgabe als Referenz.
  Nichts muss umgeleitet werden.
- **Kein `node.target` bei `playback.props`.** So folgt die Referenz
  automatisch der Standard-Ausgabe; wechselt der Nutzer vom
  Bluetooth-Lautsprecher auf die eingebauten, greift die Unterdrückung
  weiter.

**Regel, die einen Totalausfall gekostet hat: Das Ziel der Aufnahme
darf kein Gerät sein, das man ausschalten oder abziehen kann.**
`capture.props.target.object` zeigt deshalb auf das **eingebaute**
Mikrofon. Am 2026-08-17 stand dort zum Testen Stephans USB-Headset, und
diese Testfassung blieb über einen Neustart im System stehen. Beim
Anmelden war das Headset ausgeschaltet - und danach konnte **das ganze
System keinen Ton mehr abspielen**, auch nicht über die eingebauten
Lautsprecher.

Der Ablauf, weil er ohne die Zwischenschritte unglaubwürdig klingt: Der
USB-Dongle steckt und meldet eine Soundkarte, unabhängig davon, ob das
Headset an ist. ALSA meldet für dieses Aufnahmegerät sogar
`state: RUNNING`. Es kommt nur nichts - gemessen **0 Bytes in 3
Sekunden**, während das eingebaute Mikrofon 64000 liefert. Die
Echo-Unterdrückung braucht diese Aufnahme als Taktgeber; ohne Takt
startet PipeWire den Graph nicht. Die Soundkarte bleibt dann auf
`state: PREPARED` mit `trigger_time: 0.000000000` stehen, und jede
Wiedergabe hängt für immer:

```
$ paplay -v bell.oga
Connected to device alsa_output.pci-0000_00_1f.3.analog-stereo (index: 70, suspended: no).
Time: 0,000 sec; Latency: 139332 usec.   Time: 0,000 sec; ...
```

Der Nutzer hört: nichts. Keine Fehlermeldung, kein Piepen, nur
Sprachausgabe-Prozesse, die sich stapeln - beim Vorfall drei Ansagen und
vier GNOME-Klänge, alle noch in der Warteschlange. Für einen blinden
Nutzer ist das kein Tonproblem, sondern ein totes Gerät.

**Zwei Prüfschritte, die den Fehler sofort einkreisen:**

```bash
# 1) Startet die Soundkarte ueberhaupt? PREPARED + trigger_time 0 = Graph steht.
grep -E 'state|trigger_time|hw_ptr' /proc/asound/card0/pcm0p/sub0/status
# 2) Liefert das Aufnahmeziel Daten? 0 Bytes = Ursache gefunden.
timeout 4 parec -d <ziel> --format=s16le --rate=16000 --channels=1 | wc -c
```

Zum Einkreisen lässt sich die Unterdrückung ohne Neustart abschalten:
Die Datei nach `.conf.aus` umbenennen (`.conf.d` liest nur `*.conf`) und
`systemctl --user restart pipewire pipewire-pulse wireplumber`. Eine
eigene Testfassung gehört nach
`~/.config/pipewire/pipewire.conf.d/` - **nicht** nach `/etc`, wo sie
einen Neustart überlebt.

Der Verdacht lag zuerst auf `webrtc.gain_control`, das am selben Tag von
`false` auf `true` gewechselt war und ebenfalls erst beim Neustart wirksam
wurde. Beide Werte hingen gleich - erst der Reihentest über die
Zielgeräte hat es gezeigt. Ohne `target.object` läuft der Ton übrigens
auch, weil das Modul dann der Standardquelle folgt; das ist aber keine
Absicherung, sondern nur eine andere Wahl desselben Risikos.

**Offen bleibt damit:** Sobald ein externes Funkmikrofon zum Standard
werden soll - und genau das ist geplant -, braucht es eine Absicherung,
die erkennt, dass keine Daten kommen, und die Unterdrückung dann fallen
lässt statt den Ton mitzunehmen. Siehe `TODO.md`.

**Falle beim Einrichten:** Der Neustart von PipeWire wirft das
Bluetooth-Gerät in HFP zurück, und die Karte bietet danach **gar kein
A2DP mehr an** - `pactl set-card-profile ... a2dp-sink` scheitert mit
„No such entity". Das Profil taucht erst nach einem erneuten Verbinden
wieder auf:

```bash
bluetoothctl disconnect <MAC> && sleep 3 && bluetoothctl connect <MAC>
```

### 11g. Tonausgabe waehlen: Bluetooth oder Laptop (neu 2026-08-17)

**Stephans Festlegung vom 2026-08-17:** Eingabe immer das eingebaute
Mikrofon, Ausgabe der Bluetooth-Lautsprecher solange er wirklich
abspielt, sonst die eingebauten Lautsprecher. Externe Mikrofone kommen
zum Schluss noch einmal dran.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-ton-ausgabe.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/xdg/autostart/dialos-ton-ausgabe.desktop /etc/xdg/autostart/
```

**Der wichtigere Teil der Entscheidung ist die Eingabe.** Wenn DialOS nie
ein Bluetooth-Mikrofon oeffnet, kann das Geraet auch nie in HFP rutschen -
die A2DP/HFP-Zwangswahl aus Schritt 11c faellt damit weg, nicht weil sie
geloest waere, sondern weil sie nicht mehr beruehrt wird. Und der
Totalausfall aus 11f wird strukturell unmoeglich: Ein eingebautes
Mikrofon kann man nicht ausschalten.

**Warum es dafuer einen eigenen Dienst braucht**, obwohl PipeWire von
sich aus das neueste Geraet zur Vorgabe macht: Weil "vorhanden" nicht
"spielt ab" heisst. Am 2026-08-17 hat eine Senke, die `RUNNING` meldete
und den Strom annahm, nie abgespielt - und damit die komplette
Tonausgabe lahmgelegt. Der Dienst fragt deshalb keine Zustandsmeldung ab,
sondern **probiert es aus**: 150 ms Stille hinschicken und mit Zeitlimit
schauen, ob `paplay` durchlaeuft. Stille als Testton, damit der Nutzer
nicht bei jedem Ereignis ein Piepen hoert.

Drei Entscheidungen, jede aus einem Fehler desselben Tages:

| Entscheidung | Grund |
|---|---|
| **Beim Anmelden waehlen, aber nicht ansagen** | Wer sich anmeldet, hat nichts umgeschaltet. Genau daran ist die Desktop-Wiederherstellung gescheitert (11d) - sie sprach und fiel der Start-Ansage ins Wort. |
| **Vergleich mit der EIGENEN letzten Wahl**, nicht mit der Vorgabe-Senke | WirePlumber stellt beim Verschwinden eines Geraets selbst um, und zwar bevor der Dienst hinschaut. Der Vergleich mit dem Systemzustand ergab immer "nichts geaendert", und die Ansage blieb aus - obwohl der Ton gewandert war. |
| **Filter auf `" on sink #"`**, nicht auf `"sink"` | Der eigene Testton ist selbst ein `sink-input`-Ereignis. Mit dem breiten Filter haette jeder Testton den naechsten ausgeloest. |

Live bestaetigt am 2026-08-17: Lautsprecher aus - "Ton ueber Laptop.",
Lautsprecher an - "Ton ueber Lautsprecher.", beide Wechsel im Protokoll
als echte Aenderung.

**Zur Lautstaerke des Bluetooth-Lautsprechers** - gemessen am selben Tag,
weil die Vermutung sonst in die falsche Richtung fuehrt:

| Weg | Was passiert | Wirkt es? |
|---|---|---|
| Senken-Lautstaerke (GNOME-Regler, `pactl`) | Wert geht per AVRCP ans Geraet, das Signal bleibt unveraendert | ja |
| Daempfung im Signal (sox, `paplay --volume`) | Signal verlaesst den Laptop korrekt gedaempft | **nein**, der AIRHUG rechnet es weg |

Nachgewiesen am Monitor der Bluetooth-Senke: halbe Amplitude in der Datei
ergibt dort 0,071559 gegen 0,143117 (Faktor 0,5000) - Senke 100 % gegen
Senke 30 % dagegen **beide Male 0,143117**. Daraus folgt: `bluez5.enable-
hw-volume = false` waere ein Fehler. Es wuerde DialOS zwingen, auf dem
Weg zu daempfen, der beim AIRHUG nichts bewirkt - danach gaebe es
ueberhaupt keine Lautstaerkeregelung mehr.

**Und ein Nebenbefund, der eine ganze Funktion betrifft:** Die sox-Kette
in `piper-generic.conf` endet auf `norm`, und das hebt jede Ausgabe
wieder auf Vollausschlag. `GenericVolume` ist damit wirkungslos -
speech-dispatcher kann die Lautstaerke von DialOS nicht regeln. Wer das
braucht, muss die Daempfung **hinter** `norm` setzen (`norm vol 0.70`).

### 11h. Diktat und Schreibhilfe (neu 2026-08-18)

Der erste Schritt im Anwendungsblock. Diktat ist keine Anwendung, sondern
die Voraussetzung fuer vier davon - Briefe, Notizen, Mail und Chat kann der
Nutzer ohne es nicht erzeugen. Alle Messungen und die Begruendungen stehen
in [diktat.md](diktat.md).

**Java aus Debians Quellen, LanguageTool von Hand.** Nur LanguageTool ist
ein Fremdpaket - das erste im Projekt, und es ueberlebt keine
Systemaktualisierung von sich aus.

```bash
sudo apt-get install -y openjdk-21-jre-headless
# LanguageTool 6.6, 241 MB gepackt / 392 MB entpackt:
curl -L -o /tmp/lt.zip https://languagetool.org/download/LanguageTool-stable.zip
unzip -q /tmp/lt.zip -d /tmp/lt
sudo mkdir -p /opt/languagetool
sudo cp -r /tmp/lt/LanguageTool-*/. /opt/languagetool/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/user/dialos-languagetool.service /etc/systemd/user/
sudo systemctl --global enable dialos-languagetool.service
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-diktat.py /usr/local/bin/
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-notiz.py /usr/local/bin/
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-auskunft.py /usr/local/bin/
```

`dialos-auskunft.py` sagt Uhrzeit und Datum. Es holt die Sprech-Bausteine
per Import aus `dialos-start-ansage.py` - Wochentag, Ordinalzahl,
Zahl-als-Wort - statt sie nachzubauen: Zwei Stellen mit derselben Aufgabe
wuerden auseinanderlaufen, und der Nutzer hoerte den Unterschied sofort.
Der Import ist gefahrlos, weil jenes Skript ausschliesslich unter
`if __name__ == "__main__"` handelt.

**Wetter auf Nachfrage gibt es bewusst nicht** (Stephan, 2026-08-19). Der
Befehl war gebaut und wurde wieder entfernt: Am Einsatzort kennt beaconDB
keines der sichtbaren WLAN-Netze und faellt auf IP-Ortung zurueck -
gemessen Wien mit 26 km Ungenauigkeit, rund 300 km entfernt. Der
Schwellwert von 10 km verwirft das korrekt, und der Befehl haette fast
immer nur geantwortet, dass er nichts abrufen kann. In der Start-Ansage
bleibt das Wetter, weil es dort ohne Nachfrage einfach ausfaellt.

`dialos-notiz.py` liest Notizen vor und leert sie - die Sprachbefehle dazu
stehen in [sprachbefehle.md](sprachbefehle.md). Das Leeren fragt zurueck und
legt den alten Inhalt nach `<name>-verworfen.txt`, damit ein sehender Helfer
ihn zurueckholen kann.

**Woerter vor dem Einbau gegen den Wortschatz pruefen, nicht nur gegen die
Erkennung.** Der naheliegende Befehl "Einkaufszettel loeschen" ist
unmoeglich - "loeschen" steht nicht im Wortschatz des kleinen Modells, und
Vosk wirft es beim Bauen der Grammatik STILL hinaus. Vosk meldet das selbst:

```bash
python3 -c "import json,vosk; vosk.Model('/usr/local/share/vosk-model-de-small'); \
  vosk.KaldiRecognizer(vosk.Model('/usr/local/share/vosk-model-de-small'),16000, \
  json.dumps(['loeschen','[unk]']))" 2>&1 | grep -i 'missing in vocabulary'
```

Ebenfalls nicht enthalten: "zuruecksetzen", "aufraeumen". Enthalten und
deshalb benutzt: wegwerfen, leeren, erledigt.

**Warum ein dauerhafter Dienst und kein Aufruf je Satz** (gemessen): Das
Kommandozeilenwerkzeug braucht 9,3 s je Aufruf, die erste Anfrage an den
laufenden Dienst 8,8 s - danach 0,6 bis 1,6 s. Fuer ein Diktat ist nur der
Dienst brauchbar. Er belegt dauerhaft rund 1213 MB.

**Kein `--public`.** Ohne diesen Schalter bindet der Server auf 127.0.0.1
(geprueft: von der Netzadresse des Rechners nicht erreichbar). Der
oeffentliche Dienst von languagetool.org wird nie benutzt - er wuerde die
Briefe und Mails des Nutzers auf einen fremden Rechner schicken.

**Zwei Erkenner ueber demselben Audio.** Das grosse Vosk-Modell (5,5 GB,
8,8 s Ladezeit) fuer den Text, ein kleines (229 MB, 0,4 s) mit einer
Grammatik aus genau einem Satz fuer `diktat beenden`. Der Grund ist ein
Fehler aus dem ersten Test: In der freien Erkennung wurde "diktat beenden"
zu `'diktat wird erhoeht'`. Ein BESTIMMTER Satz ist in freier Erkennung
nicht zuverlaessig zu treffen - dasselbe, was "gnome" zu "genug" und
"windows" zu "sinnlose" macht.

**Nur einer darf das Mikrofon haben.** `dialos-diktat.py` legt
`$XDG_RUNTIME_DIR/dialos-diktat-aktiv` an; `dialos-sprachbefehl-desktop.py`
haelt sich dann heraus und schreibt es ins Protokoll. Ohne das wuerde ein
diktierter Satz auch als Befehl ausgewertet - wer "auf Windows umschalten"
in einen Brief diktiert, haette danach einen anderen Schreibtisch. Live
belegt am 2026-08-18 mit Zeitstempeln in beiden Protokollen.

**`--noise_w 0` in der Sprechkette** - siehe Schritt 8 und den Kommentar in
`piper-generic.conf`. Ohne den Schalter sprach Piper jeden Satz mit bis zu
17 % anderer Dauer, und eine gespeicherte Ansage klang hoerbar anders als
dieselbe frisch gesprochene.

### 11i. Fusszeile, Mitschrift und halbtransparente Leisten (neu 2026-08-19)

Drei Wuensche von Stephan, die nichts miteinander zu tun haben ausser dem
Tag.

**Fusszeile fuer Dokumente, Mails und Ausdrucke.**

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-fusszeile.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/usr/local/share/dialos/fusszeile.txt /usr/local/share/dialos/
```

Der Text steht in `/usr/local/share/dialos/fusszeile.txt` und **nur dort** -
Briefe, Mails und Ausdrucke lesen ihn von da. Waere er an drei Stellen im
Code, wuerden zwei davon veralten, ohne dass es auffaellt, weil kaum jemand
alle drei Wege am selben Tag benutzt.

Rechtsbuendig wird im reinen Text durch Leerzeichen erreicht (Breite 76).
Ist der Satz laenger als die Breite, bleibt er ungekuerzt linksbuendig
stehen - ein abgeschnittener Herkunftshinweis waere schlechter als ein nicht
ausgerichteter.

**Notizen bekommen sie NICHT** (Stephans Entscheidung). Der Einkaufszettel
wird bei jedem Diktat ergaenzt; eine Fusszeile landete dort bei jedem
Durchgang mitten im Text. Notizen sind Arbeitszettel, keine Dokumente. Wird
ein Zettel gedruckt, kommt die Zeile beim Drucken dazu:
`dialos-fusszeile.py drucken DATEI`.

In einer Mail wird aus "Dieses Dokument" ein "Diese Nachricht" (`--art mail`)
- eine Mail ist kein Dokument.

**Die Fusszeile in JEDE Mail (nachgezogen 2026-08-20).** Am Tag darauf hat
Stephan eine Mail verschickt, und die Zeile war nicht darin. Sie konnte nicht
darin sein: `dialos-fusszeile.py` war gebaut und dokumentiert, aber **kein
einziges Programm rief es auf** - ein Werkzeug ohne Benutzer. Im
Thunderbird-Profil standen null Signatur-Eintraege. Eine Vorgabe ist nicht
erfuellt, weil das Werkzeug dafuer existiert, sondern erst, wenn etwas es
benutzt.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-mail-signatur.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/system/dialos-fusszeile.service /etc/systemd/system/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/system/dialos-fusszeile.path /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dialos-fusszeile.path dialos-fusszeile.service
dialos-mail-signatur.py          # als der angemeldete Benutzer, Thunderbird geschlossen
```

`dialos-fusszeile.py signatur` erzeugt `mail-signatur.html` und
`mail-signatur.txt` neben der Quelle. Thunderbird kann eine Signatur nur aus
einer **Datei** lesen, nicht aus einem Programm - diese Datei ist damit eine
zweite Stelle, an der der Satz steht, also genau die Kopie, die dieser
Abschnitt vermeiden will. Sie wird deshalb nie von Hand gepflegt: Die
`.path`-Einheit beobachtet `fusszeile.txt` und erzeugt sie neu, sobald sich
der Satz aendert. Damit kann sie nicht still veralten.

`dialos-mail-signatur.py` schreibt die Eintraege in die **`user.js`** des
Profils, nicht in `prefs.js`: Thunderbird schreibt `prefs.js` beim Beenden neu
und wuerde einen Fremdeintrag verlieren. `user.js` wird bei jedem Start
darueber gelegt. Preis: In den Kontoeinstellungen laesst sich die Signatur
nicht dauerhaft abschalten - fuer eine Herkunftsangabe, die laut Vorgabe in
JEDER Mail steht, ist das richtig herum. Gesetzt wird sie fuer **jede**
Identitaet, die die `prefs.js` kennt, und `sig_bottom=false` stellt sie beim
Antworten direkt unter den eigenen Text statt unter das ganze Zitat (das
Profil antwortet oberhalb des Zitats).

Zwei Formate mit Absicht: Thunderbird verfasst hier in HTML, und nur dort geht
"dezent und rechtsbuendig" sauber - im reinen Text ginge es nur ueber
Leerzeichen, die auf einem Telefon umbrechen. Die `.txt` liegt daneben, falls
ein Konto in reinem Text schreibt; dann wird in der Kontoeinstellung
umgestellt, ohne dass etwas gebaut werden muss. Der Eintrag `sig_file` ist
intern ein Datei-Typ (`datatype="nsIFile"` in `am-main.xhtml`), dessen
gespeicherte Form unter Linux der absolute Pfad ist - ein Pfad als Text
genuegt also.

**Das deckt einen von zwei Mailwegen.** Laut `docs/anwendungen.md` ist
Thunderbird die Oberflaeche, nicht der Motor: DialOS soll spaeter selbst ueber
IMAP/SMTP versenden, weil Thunderbird von aussen nicht steuerbar ist. Die
Signatur greift nur bei Mails, die durch Thunderbird gehen - also bei allem,
was der sehende Helfer schreibt. Der eigene Versandweg muss sich die Zeile
selbst holen (`dialos-fusszeile.py text --art mail`); der Hinweis steht in
`TODO.md` bei diesem Punkt.

**Das Konto ist nicht Teil des Abbilds.** Es wird bei der Ersteinrichtung von
Hand angelegt (Formular `thunderbird-angaben-formular.md`), und erst danach
gibt es eine Identitaet, fuer die eine Signatur gesetzt werden kann. Deshalb
gehoert `dialos-mail-signatur.py` an das **Ende** der Ersteinrichtung, nach dem
Einrichten des Kontos. Ohne Konto bricht es mit einem Hinweis ab, statt
stillschweigend nichts zu tun.

**Mitschrift fuer sehende Zuschauer.**

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-mitschrift.py /usr/local/bin/
```

Das Fenster geht **mit der Sprachsteuerung auf und zu** (Stephans
Praezisierung vom 2026-08-19): auf bei "Sprachsteuerung starten", zu bei
"Sprachsteuerung stoppen" und auch dann, wenn die Zeitgrenze von zwei Minuten
abschaltet. Geoeffnet und geschlossen wird es von
`dialos-sprachbefehl-desktop.py` - es haengt an der Sprachsteuerung, nicht am
Anmelden: wo nicht gesprochen wird, gibt es auch nichts mitzuschreiben.

Bewusst NICHT bei jedem einzelnen Befehl - das wuerde beim Diktieren den Fokus
stehlen, und wer diktiert, sieht den Bildschirm ohnehin nicht. Einmal pro
Sitzung aufgehen ist unauffaellig, bei jedem Satz aufspringen waere es nicht.

Zwei Fallen, die dabei gelernt wurden:

- **Vor dem Oeffnen pruefen, ob schon eines laeuft.** Ohne das stuenden nach
  zwanzig Aktivierungen zwanzig Fenster uebereinander. Geprueft wird ueber
  `/proc`, gesucht nach dem Python-Skript.
- **Geschlossen wird das SKRIPT, nicht das Terminal.** `gnome-terminal`
  spaltet sich vom Aufruf ab und uebergibt an einen schon laufenden
  `gnome-terminal-server`; die PID des Aufrufs ist sofort wieder weg und die
  des Servers gehoert allen Fenstern. Endet dagegen das Skript, endet der
  Befehl des Fensters - und das Fenster schliesst sich von selbst.

**Rueckblick beim Oeffnen - gefunden durch Stephans Test.** Das Fenster wird
von "Sprachsteuerung starten" geoeffnet; dieser Satz steht also schon im
Protokoll, bevor die Mitschrift zu lesen beginnt, und fehlte damit **immer** -
im Fenster wie im Support-Protokoll. Fuer den Support waere das die erste Frage
gewesen ("hat er ueberhaupt eingeschaltet?"). Der Dienst ruft deshalb mit
`--rueckblick 20` auf: 20 Sekunden Vorgeschichte, was auch die nicht erkannten
Versuche davor mitnimmt - fuer den Support oft die aufschlussreichere Haelfte.
Von Hand gestartet bleibt es bei 0, damit ein selbst geoeffnetes Fenster nicht
mit alten Zeilen anfaengt.

Zwei Fallen darin, die beides kaputt gemacht haetten:

- **Dopplung.** Zweimal kurz hintereinander einschalten wuerde dieselben Zeilen
  zweimal ins Support-Protokoll schreiben. Merker ist die Datei selbst: die
  Uhrzeit ihrer letzten Zeile ist die Grenze. Kein zusaetzlicher Zustand, der
  veralten koennte.
- **Der Tageswechsel.** Die vier Protokolle schreiben nur `HH:MM:SS` und werden
  nicht gedreht (siehe `TODO.md`). Vorwaerts verglichen sieht ein Eintrag von
  **gestern** 17:52 wie "spaeter heute" aus - ein Rueckblick am Abend haette
  diktierten Text aus einer fremden Sitzung mitgenommen. Beim Testen mit einem
  weiten Rueckblick standen genau solche Zeilen in der Liste. Deshalb wird das
  Dateiende **rueckwaerts** gelesen: die Uhrzeit laeuft dabei fallend, und wo
  sie nach oben springt, ist der Tageswechsel und wird abgebrochen.

**Und dasselbe am Ende der Sitzung** (gefunden am 2026-08-19, nachdem der
Rueckblick den Anfang geheilt hatte). Im Protokoll stand um 10:53:27 nur
"Mitschrift geschlossen" - warum die Sprachsteuerung aufgehoert hatte, stand
nirgends. Zwei Ursachen, beide behoben:

- **Die Zeitgrenze wurde gar nicht protokolliert.** Der Dienst schaltete nach
  zwei Minuten ab, sagte es an und schloss das Fenster - ohne eine Zeile
  darueber zu schreiben. Damit stand im Protokoll die Wirkung und nicht die
  Ursache. Jetzt kommt `Zeitgrenze: 120 s ohne Befehl`, und zwar **vor** der
  Ansage: die dauert 3,5 s, in denen die Mitschrift die Zeile noch liest.
- **Die letzte Zeile war beim Schreiben schon zu spaet.** `melde()` stand
  hinter dem `kill` - das Fenster war tot, bevor die Meldung geschrieben war.
  Jetzt wird erst gemeldet, dann `NACHLAUF_S = 1.0` gewartet, dann geschlossen.
  Die Mitschrift sieht alle 0,4 s nach; eine Sekunde ist reichlich, und sie
  faellt nicht auf, weil davor ohnehin eine Ansage laeuft.

Beides ist dieselbe Fehlerklasse wie der fehlende Rueckblick: **Das Protokoll
zeigte, was passiert ist, aber nicht, warum.** Fuer die Fehlersuche ist das die
unbrauchbare Haelfte.

Wer den Bildschirm frei haben will, legt `~/.config/dialos/mitschrift` mit dem
Inhalt `aus` an. Vorgabe ist **an**, und zwar wegen des Support-Protokolls
(gleich darunter): waere das Fenster ab Werk aus, gaebe es beim Anruf auch
nichts nachzulesen.

**Warum ein Filter und kein `tail -f`:** Das Befehlsprotokoll bestand am
2026-08-19 aus **4132 Pegel-Zeilen gegen 13 echte**. Die Mitschrift wirft die
Pegelanzeige weg und uebersetzt die Protokollzeilen in Saetze:

```
08:47:51  Sprache   gehoert: "wie viel uhr ist es"
08:47:51  Sprache   Auskunft: uhrzeit
17:52:41  Diktat    geschrieben: "Marisa"
```

Sie liest **fünf** Protokolle zusammen (Befehlsdienst, Diktat, Auskunft,
Notizen, Ton-Beobachter - der fünfte seit dem 2026-08-19, siehe unten) und mischt sie nach Uhrzeit. Genau dieses Zusammenfuehren hat am
2026-08-18 den Beweis gebracht, dass Diktat und Befehlserkennung sich nicht
ins Gehege kommen - von Hand war es muehsam. **Eigener Fehler dabei:** Erst
gab sie Quelle fuer Quelle aus, sah dadurch chronologisch aus und war es
nicht. Bei einem Werkzeug, dessen Zweck es ist, Gleichzeitigkeit zu zeigen,
waere das die falsche Eigenschaft gewesen.

**Support-Protokoll (Stephans Wunsch vom 2026-08-19).** Was durch das Fenster
laeuft, wird zusaetzlich in eine Tagesdatei geschrieben:
`~/.local/share/dialos/support/befehle-JJJJ-MM-TT.log`, Ordner 0700, Datei
0600. Eine Datei pro Tag, **sieben Tage** lang; beim Start und um Mitternacht
raeumt die Mitschrift die aelteren selbst weg. Datum im Dateinamen heisst:
aufraeumen ist "alte Datei loeschen" und nicht "in einer laufenden Datei nach
der Grenze suchen" - die Datei, in die gerade geschrieben wird, wird dabei nie
angefasst. Dateien, die nicht dem Namensmuster entsprechen, bleiben unberuehrt.

Zweck ist der Anruf beim Support: nachlesen, was das Geraet wirklich gehoert
hat, statt sich auf die Erinnerung zu verlassen.

**Was hineinkommt - und was nicht.** Die Befehle vollstaendig, vom Diktierten
die **erste Zeile** (auf 60 Zeichen gekuerzt) und danach nur noch die Anzahl:

```
09:50:10  Sprache   gehoert: "einkaufszettel aufnehmen"
09:50:12  --- Einkaufszettel ---
09:50:12  Diktat    Diktat laeuft (einkaufszettel)
09:50:26  Diktat    erste Zeile: "Milch"
09:50:41  Diktat    gespeichert in /home/nutzer/Notizen/einkaufszettel.txt
09:50:41            (2 weitere Zeilen erfasst, nicht protokolliert)
09:53:30  --- Sprachsteuerung ---
```

`~/dialos-diktat.log` enthaelt jeden diktierten Satz woertlich, also den ganzen
Brief - eine Datei fuer einen fremden Helfer darf die Post des Nutzers nicht
enthalten. Eine Zeile genuegt aber, um zu erkennen, DASS etwas erfasst wurde
und ob es Sinn ergab. Im Fenster steht weiter alles; dort sieht es nur, wer
ohnehin vor dem Geraet sitzt.

**Der Zusammenhang ist das Wichtigste** (Stephan): "Milch" allein sagt
niemandem etwas, "Einkaufszettel: Milch" sagt alles. Deshalb steht vor jedem
Abschnitt, worum es ging - Diktat, Einkaufszettel, Frage an das System,
spaeter Mail und Brief. Er wird nicht geraten, sondern aus den Zeilen
mitgefuehrt, die die Programme beim Starten selbst schreiben; ein unbekanntes
Ziel landet unuebersetzt, aber lesbar im Protokoll statt zu fehlen.

**Eigener Fehler dabei:** Der erste Entwurf setzte den Zusammenhang nach jeder
Zeile zurueck. Damit stand "gespeichert in ..." nicht mehr unter
"Einkaufszettel", und fuer einen einzigen Befehl standen zwei Ueberschriften
da. Ein gehoerter Satz ist die einzige verlaessliche Grenze - er bedeutet
immer, dass der Nutzer wieder mit der Sprachsteuerung spricht, und er kommt
auch dann, wenn ein Diktat vorzeitig abbricht und die Schlusszeile fehlt.

**Halbtransparente Leisten - zwei Leisten, zwei Wege.**

| Leiste | Wie | Paket |
|---|---|---|
| unten (Windows-Optik) | dash-to-panel, `trans-panel-opacity 0.5` | keines, bringt es mit |
| oben (GNOME-Optik) | blur-my-shell, `color` mit Alpha 0.5 | `gnome-shell-extension-blur-my-shell` |

Die Werte stehen in `01-dialos-defaults` bzw. setzt `dialos-desktop-stil.sh`
beim Umschalten. **In der Windows-Optik gibt es oben keine Leiste** -
dash-to-panel ersetzt sie. blur-my-shell hat dort nichts zu tun und muss
beim Umschalten weder ein- noch ausgeschaltet werden.

**Zweimal dieselbe Falle bei beiden Erweiterungen:** Ein gesetzter Wert
allein tut nichts. dash-to-panel hatte `trans-panel-opacity` ab Werk auf
0.4, wirkungslos weil `trans-use-custom-opacity` auf false stand; bei
blur-my-shell braucht es `customize=true`, sonst gelten die allgemeinen
Werte statt der eigenen.

**Und: `color` mit Alpha statt Weichzeichnung.** Die Voreinstellung der
Erweiterung ist `sigma 30`, also kraeftig verwaschen. Gefordert war
"halbtransparent" - das ist halb deckendes Schwarz ueber dem Hintergrund und
entspricht mit Alpha 0.5 genau dem Wert der unteren Leiste.

**Alle uebrigen Wirkungen der Erweiterung sind ausdruecklich abgeschaltet**
(Uebersicht, Dash, Anwendungsfenster, Sperrbildschirm und vier weitere). Sie
kann viel mehr als gebraucht wird, und jede zusaetzliche Wirkung ist eine
mehr, die beim naechsten GNOME-Sprung brechen kann - bei drei Erweiterungen
sind in diesem Projekt schon zwei Debian-Paketfehler gefunden worden. Auf
Standardwerten zu lassen waere das Gegenteil einer Entscheidung.

**Beim Nachbauen zu wissen:** Eine frisch installierte Shell-Erweiterung ist
fuer die LAUFENDE Shell unsichtbar - sie durchsucht das Verzeichnis nur beim
Start, und unter Wayland laesst sie sich nicht neu starten. Es hilft nur
abmelden und wieder anmelden.

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
3. **Admin-Konto in die Gruppe `adm`** (neu 2026-08-16, Stephans
   Entscheidung). Ohne sie liest `dialosadmin` keine Systemprotokolle:
   `journalctl -u <dienst>` antwortet mit "-- No entries --", obwohl der
   Dienst protokolliert hat. Aufgefallen bei der Suche nach dem
   übersteuerten Mikrofon (Schritt 11e) - der naheliegende Fehlschluss
   "der Dienst tut nichts" wäre dort teuer geworden. `adm` ist Debians
   Standardgruppe dafür und gibt ausschließlich **lesenden** Zugriff auf
   Protokolle, keine weiteren Rechte; `systemd-journal` ist nicht nötig,
   weil systemd dieser Gruppe die Journal-Rechte ohnehin einräumt.
   Bewusst nur fürs Admin-Konto - für `nutzer` wären Systemprotokolle
   nutzlos und nur zusätzliche Angriffsfläche. Wirkt erst nach dem
   nächsten Anmelden.
4. `dialos-setup-nutzer.sh` - legt `nutzer` an (`adduser
   --disabled-password`, Gruppen `sudo,audio,video,plugdev,netdev,
   bluetooth,scanner,lpadmin,cdrom`, zufälliges Sudo-Passwort), schaltet
   Autologin von `dialosadmin` auf `nutzer` um (Wiederholungslogik gegen
   einen Timing-Bug: "user is locked" direkt nach `chpasswd`, weil
   AccountsService die neue Passwort-Zeile noch nicht bemerkt hatte).
5. Prüft, ob die Firefox-Startseiten-Policy aus Schritt 10 korrekt sitzt.

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

## 12c. Zweite Stimme und die beiden Namen (neu 2026-08-20)

Stephans Entscheidung: eine freundliche Damenstimme. Aus dem Hörvergleich wurde
**`de_DE-kerstin-low`**, Tempo **1.00**, Name **Anna**.

```bash
# Stimme holen (rund 60 MB)
BASIS=https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE
curl -s -L -o /tmp/kerstin.onnx      "$BASIS/kerstin/low/de_DE-kerstin-low.onnx?download=true"
curl -s -L -o /tmp/kerstin.onnx.json "$BASIS/kerstin/low/de_DE-kerstin-low.onnx.json?download=true"
sudo install -m 0644 /tmp/kerstin.onnx      /usr/local/share/dialos-piper/voices/de_DE-kerstin-low.onnx
sudo install -m 0644 /tmp/kerstin.onnx.json /usr/local/share/dialos-piper/voices/de_DE-kerstin-low.onnx.json

# Umschalten - Stimme, Name und Tempo ZUSAMMEN
sudo dialos-stimme.py setzen kerstin
systemctl --user restart speech-dispatcher.service
```

**Warum drei Dinge zusammen umschalten.** Eine Frauenstimme, die sich als
Michael vorstellt, wäre falsch - und ein Nutzer, der den Bildschirm nicht sieht,
hat nur diesen Namen, um das Gerät anzusprechen. Das Tempo ist pro Stimme
verschieden, und zwar messbar: derselbe Satz braucht bei Thorsten 7,75 s mit
Tempo 0,88, bei Kerstin **8,99 s** mit demselben Wert. Erst 1.00 bringt sie auf
7,91 s. Ein gemeinsamer Wert für alle Stimmen wäre für die eine oder andere
immer falsch.

**Die Auswahl kam per Ohr, nicht per Rechnung.** Drei weibliche Piper-Stimmen
standen zur Wahl (`eva_k-x_low`, `kerstin-low`, `ramona-low`); bessere gibt es
für Deutsch nicht. Alle drei laufen mit 16 000 Hz gegen Thorstens 22 050 Hz -
das ist der hörbare Qualitätsunterschied und der Preis dieser Entscheidung.

**Der Nutzername.** `/usr/local/share/dialos/nutzer-name.txt`, eine Zeile,
Beispiel in [beispiele/nutzer-name.txt](beispiele/nutzer-name.txt). Auf dem
Testgerät steht dort „Stephan" - **stellvertretend für den Kundennamen**, der
beim Aufsetzen im Büro eingetragen wird. Die Datei liegt bewusst nicht im Repo:
Ein Kundenname gehört nicht in die Versionsverwaltung.

Wo der Name benutzt wird, steht in `dialos-namen.py`, und die Regel ist
sparsam:

| Stelle | Name? | Warum |
|---|---|---|
| Begrüßung beim Anmelden | **ja** | einmal pro Sitzung, und der Moment, in dem es am meisten bedeutet |
| Entscheidungen (Fernwartung, Notiz löschen) | **ja** | wo eine Zustimmung fällt, holt der Name die Aufmerksamkeit zurück |
| Fehler („Ich finde kein Mikrofon") | **ja** | wenn etwas nicht geht, muss klar sein, wer gemeint ist |
| Bestätigungen („Diktat beendet") | nein | zwanzigmal am Tag nutzt sich ein Name ab |
| Zeitgrenze alle zwei Minuten | nein | dito |

**Warum das mehr ist als Höflichkeit:** Der Name am Satzanfang ist ein
**Signal**. Läuft das Radio oder ist Besuch im Raum, sagt „Stephan, …"
unmissverständlich: das gilt Dir, hör hin. Genau deshalb darf er nicht überall
stehen - wer ihn dauernd hört, überhört ihn.

**Ohne Namensdatei bleibt es beim schlichten „Du",** und jede Ansage stimmt
trotzdem. Keine hängt davon ab, dass ein Name eingetragen ist - das war die
Bedingung beim Bauen.

## 13a. Sicherheitsupdates unbeaufsichtigt (neu 2026-08-20)

```bash
sudo apt-get install -y unattended-upgrades
sudo install -m 0644 iso-build/config/includes.chroot/etc/apt/apt.conf.d/52dialos-unattended-upgrades /etc/apt/apt.conf.d/
sudo install -m 0644 iso-build/config/includes.chroot/etc/apt/apt.conf.d/20auto-upgrades /etc/apt/apt.conf.d/
```

Festgelegt in [anwendungen.md](anwendungen.md): Sicherheitsupdates laufen
automatisch, alles Größere nur auf Ansage. Drei Einstellungen tragen das, und
jede hat einen Grund, der über den Normalfall hinausgeht:

**`#clear` vor `Origins-Pattern` ist Pflicht.** Eine `Origins-Pattern`-Zeile
**hängt an** (`::`), sie ersetzt nicht. Ohne das Leeren standen nach dem ersten
Versuch fünf Muster in der Liste - die eigenen zwei **und** Debians drei,
darunter `label=Debian` ohne `-Security`. Das ist die normale Stable-Quelle: Es
wäre unbeaufsichtigt alles eingespielt worden, was aus Stable kommt. Aufgefallen
nur, weil nach dem Installieren `apt-config dump` gelesen wurde statt der eigenen
Datei zu glauben - **eine Konfigurationsdatei zu schreiben ist nicht dasselbe wie
eine Einstellung zu setzen.**

**`Remove-Unused-Dependencies "false"` ist die wichtigste Zeile.** Nach
Schritt 13b gelten 49 Pakete als „automatisch installiert", die vorher nur über
`gnome-core` gehalten wurden - darunter `gnome-shell`, `nautilus` und
`pipewire-audio`. Ein automatisches `autoremove` würde also nachts anbieten, den
Desktop und den Ton-Unterbau zu entfernen. Das Aufräum-Skript schützt sie zwar,
aber diese Einstellung darf sich nicht darauf verlassen: Übersieht der Schutz
dort **ein** Paket, wäre das Gerät am Morgen unbenutzbar - und der Nutzer könnte
nicht einmal Hilfe rufen.

**`Automatic-Reboot "false"`,** und zwar aus einem Grund, der schwerer wiegt als
der übliche: `/home/nutzer` liegt auf der LUKS-Partition, die
`dialos-stick-gate.service` mit dem Sicherheits-Stick öffnet. Startet das Gerät
nachts neu, während der Stick nicht steckt, kommt der Nutzer am Morgen überhaupt
nicht mehr in seine Sitzung - und versteht nicht, warum.

**Gegenprobe, nicht Vertrauen.** Der Probelauf zeigt in
`/var/log/unattended-upgrades/unattended-upgrades.log`, was wirklich gilt:

```
Marking not allowed <... trixie ... l=Debian ...> with -32768 pin
Applying pin -32768 to ... trixie-updates ... l=Debian
Applying pin -32768 to ... downloads.claude.ai ... l=Anthropic
left to upgrade set()
```

`-32768` ist apts „auf keinen Fall". Nur `Debian-Security` fehlt in dieser
Liste, ist also erlaubt.

**Bewusst mit gesperrt: `trixie-updates`.** Dort kommt unter anderem `tzdata`
her. Die Zeitzonen-Datenbank veraltet damit, bis jemand „System aktualisieren"
sagt - erwähnenswert bei einem Gerät, dessen Uhrzeit-Ansage ein Kernbefehl ist.
Bleibt gesperrt, weil „nur Sicherheit" die Festlegung war.

## 13b. Aufräumen: entfernen, was Debian mitbringt und DialOS nicht braucht

Stephans Vorgabe vom 2026-08-19: Nachdem Debian + GNOME auf einem neuen Rechner
installiert ist und die Skripte durchgelaufen sind, soll alles weg, was mit
Debian kam und für DialOS nicht benötigt wird. Deshalb steht dieser Schritt hier
und nicht im laufenden Betrieb - und **vor** Schritt 16, damit das
Sicherungs-Abbild das aufgeräumte System enthält.

```bash
./scripts/dialos-aufraeumen.sh                 # zeigt nur, was passieren würde
sudo ./scripts/dialos-aufraeumen.sh --wirklich  # entfernt
```

**Warum das nicht einfach `apt purge` ist - der gefährliche Teil.** Sobald ein
Bestandteil von GNOME entfernt wird, gehen die Meta-Pakete `gnome`, `gnome-core`
und `task-gnome-desktop` mit. Das ist unvermeidlich und für sich harmlos. Die
Folge ist es nicht: Danach gelten **49 Pakete** als „automatisch installiert",
die vorher nur über `gnome-core` gehalten wurden - darunter `gnome-shell`,
`nautilus`, `gnome-settings-daemon`, `gnome-keyring` und `pipewire-audio`. Ein
späteres `apt autoremove` würde anbieten, **den ganzen Desktop und den
Ton-Unterbau** zu entfernen. Gemessen am 2026-08-19 auf dem T490.

Das Skript markiert deshalb **zuerst** alles, was bleiben soll, als „manuell
installiert" (64 Pakete), und entfernt erst danach. Anschließend prüft es
ausdrücklich nach, dass `gnome-shell`, `nautilus`, `gnome-settings-daemon`,
`gnome-keyring`, `pipewire-audio` und `gdm3` noch da sind, und bricht mit
Fehler ab, wenn nicht.

**Und es ruft kein `autoremove` auf**, sondern zeigt nur, was eines anbieten
würde. Bei einem Gerät, das ein blinder Nutzer allein bedient, gehört diese
Entscheidung einem Menschen mit Bildschirm.

**Was entfernt wird** (17 Pakete, 20 mit den Meta-Paketen):

| Stufe | Pakete | Begründung |
|---|---|---|
| A - Doppelungen und Fremdkörper | `gnome-characters`, `gnome-font-viewer`, `gnome-tour`, `malcontent-gui`, `xterm` | nichts davon hat mit DialOS zu tun |
| B - ersetzt | `gnome-music`, `gnome-podcasts` | Rhythmbox ist der EINE Player |
| | `totem`, `totem-plugins` | VLC bleibt der einzige Videoplayer |
| | `gnome-contacts` | Kontakte macht Thunderbird |
| | `gnome-clocks`, `gnome-weather` | Uhrzeit und Wetter sagt DialOS selbst |
| | `gnome-maps` | rein visuell |
| | `gnome-connections` | Fernwartung ist RustDesk |
| | `gnome-sound-recorder` | Aufnahme macht DialOS |
| | `simple-scan` | kein Scanner im Aufbau |
| | `shotwell` | der Bildbetrachter genügt |
| C - entschieden 2026-08-19 | `libreoffice-calc`, `libreoffice-impress`, `libreoffice-draw`, `libreoffice-math` | festgelegt ist nur **Writer** (Briefe). Writer, `libreoffice-core` und `libreoffice-common` bleiben nachweislich unberührt - simuliert, bevor entschieden wurde. |

**Bewusst NICHT entfernt**, obwohl für `nutzer` ausgeblendet: `obs-studio` und
`gnome-snapshot` (Videoaufnahme - der Zweck ist laut
[anwendungen.md](anwendungen.md) ungeklärt, und was nicht entschieden ist, wird
nicht vorab weggeworfen), `yelp`, `baobab`, `gnome-software`, `seahorse` (können
im Support helfen). `libreoffice-startcenter` bleibt ebenfalls - mit der Folge,
dass es danach Kacheln für Programme zeigt, die es nicht mehr gibt. Für
`dialosadmin` ein Schönheitsfehler, für `nutzer` unsichtbar.

**Drei „Doppelungen" lassen sich NICHT per Paket entfernen** - aufgefallen am
2026-08-19, weil `dpkg -S` auf die Doppelung dasselbe Paket nennt wie das
Original:

| Menüeintrag | steckt in | Folge beim Entfernen |
|---|---|---|
| `gnome-system-monitor-kde.desktop` | `gnome-system-monitor` | die echte Systemüberwachung wäre auch weg |
| `mintstick-kde.desktop`, `mintstick-format-kde.desktop` | `mintstick` | beide USB-Werkzeuge wären weg |
| `vim.desktop` | `vim-common` | daran hängt `vim-tiny` - kein `vi` mehr |

Diese vier werden in Schritt 13c pro Konto ausgeblendet.

## 13c. Menü pro Konto: nutzer sieht seine Anwendungen, dialosadmin alles

Stephans Präzisierung vom 2026-08-19: „Wenn du das nur ausblendest, dann passe
das für den Nutzer an, bei dialosadmin kann mehr sichtbar sein, was ich z.B. für
den Support benötige."

```bash
./scripts/dialos-menue-pro-konto.sh                 # zeigt nur
sudo ./scripts/dialos-menue-pro-konto.sh --wirklich
```

**Für wen das Menü überhaupt da ist:** `nutzer` sieht den Bildschirm nicht - das
Menü ist für den **sehenden Helfer**, der neben ihm sitzt. Und für den ist eine
kurze Liste mehr wert als eine vollständige: Er soll auf Anhieb finden, was zum
Gerät gehört, und nicht zwischen Formeleditor und Schriftvorschau suchen.

**Weiße Liste, keine schwarze.** Für `nutzer` wird alles ausgeblendet, was nicht
auf der Behalten-Liste steht - nicht umgekehrt. Eine schwarze Liste veraltet mit
jedem Debian-Update still: Käme ein neues Programm dazu, wäre es sofort sichtbar
und niemandem fiele es auf. Bei einer weißen Liste ist der Standard
„unsichtbar", und jede Ausnahme steht im Skript begründet.

**`nutzer` sieht 11 Einträge**, `dialosadmin` alles außer den vier Doppelungen:

| Eintrag | Warum |
|---|---|
| Firefox ESR | Browser, Jitsi-Videochat, WhatsApp Web |
| Thunderbird | Mail, Kalender, Kontakte - für den Helfer |
| LibreOffice Writer | Briefe |
| Rhythmbox | Musik, Podcasts, Hörbücher |
| Shortwave | Radio |
| VLC | Videos |
| Dateien | der Helfer muss an `~/Notizen` kommen |
| Texteditor | Einkaufszettel und Notizen sind `.txt`-Dateien |
| Dokumentenbetrachter | Briefe als PDF lesen |
| Bildbetrachter | Bilder von der Familie |
| Taschenrechner | harmlos, und ein Helfer rechnet mal etwas |

**Bewusst NICHT für `nutzer` sichtbar:** Einstellungen, Terminal, Laufwerke,
Protokolle, Systemüberwachung, Optimierungen, Erweiterungs-Manager, die
DialOS-Werkzeuge und RustDesk. Alles Administrative läuft auf `dialosadmin`.
**Das hat eine Konsequenz, die bedacht sein muss:** Ein Helfer beim Kunden kann
ohne Kontowechsel keinen Bluetooth-Lautsprecher koppeln. Die Kopplung geschieht
im Büro (Schritt 14); für den Ausnahmefall bleibt der Wechsel zu `dialosadmin`.

**Stephan hat das am 2026-08-19 so entschieden**, nachdem die Konsequenz
benannt war - und der Grund wiegt schwerer als die Bequemlichkeit: Die
Einstellungen sind das gefährlichste Fenster des Systems für ein Gerät, dessen
Nutzer den Bildschirm nicht sieht. Ein Fehlklick in der Tonausgabe oder beim
Mikrofon macht DialOS stumm oder taub, und der Nutzer hätte keine Möglichkeit,
den Grund zu finden. Verworfen wurde auch die Zwischenlösung, nur die
Bluetooth-Seite über einen eigenen Menüeintrag erreichbar zu machen.

**Überlagerung statt Löschen:** Die Dateien in
`~/.local/share/applications/*.desktop` mit `NoDisplay=true` überschreiben die
systemweiten, ohne dass `apt`/`dpkg` sie je anfasst - das übersteht
Debian-Updates und ist durch Löschen einer Datei rückgängig zu machen. Kopiert
wird jeweils das **Original** samt `Exec` und `MimeType`, nicht eine
Minimaldatei: Eine Überlagerung ersetzt das Original vollständig, und fehlte
darin `MimeType`, wäre das Programm auch als Standardanwendung für seine
Dateitypen weg. Dasselbe Muster wie bei den vorhandenen Überlagerungen für
Evolution und Kalender. Geschrieben wird zusätzlich nach `/etc/skel`, damit ein
später angelegtes Konto dieselbe Sicht bekommt - mit `chown` auf das jeweilige
Konto, weil eine Datei, die `root` gehört, vom Nutzer nicht mehr geändert werden
kann.

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

Zur Aufteilung von Ein- und Ausgabe, **Stand 2026-08-17**:

- **Spracheingabe: immer das eingebaute Mikrofon**, über die
  echo-bereinigte Quelle (Schritt 11f). Bluetooth nur als letzter Ausweg
  auf Geräten ohne eingebautes Mikrofon.
- **Sprachausgabe: der Bluetooth-Lautsprecher**, sofern verbunden -
  sonst die eingebauten Lautsprecher.

Das klingt widersprüchlich, ist aber genau der Punkt: Weil Lautsprecher
und Mikrofon verschiedene Geräte sind, hört das Mikrofon die Ausgabe im
Raum mit - und genau das rechnet die Echo-Unterdrückung heraus (32 dB
gemessen). Würde stattdessen das Bluetooth-Mikrofon benutzt, fiele das
Headset auf HFP und die Ausgabe auf Telefonqualität.

Der frühere Mikrofon-Vergleichstest kam zum gegenteiligen Ergebnis
(Bluetooth klar überlegen), lief aber unter 60 dB Übersteuerung des
eingebauten Mikrofons und ist deshalb nicht belastbar - er gehört
wiederholt (TODO.md). Details:
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
