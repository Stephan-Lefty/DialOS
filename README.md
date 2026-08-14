[Deutsch](README.md) | [English](README.en.md) | [Änderungsprotokoll](#änderungsprotokoll) | [TODO](TODO.md)

<img src="assets/logo.png" alt="DialOS Logo" width="360">

Website: [dialos.org](https://dialos.org)

# DialOS

Ein auf Debian 13 + GNOME 48 basierendes, vollständig sprachgesteuertes
System für Menschen, die einen Computer nur eingeschränkt nutzen können –
insbesondere blinde und motorisch eingeschränkte Personen. Ziel ist ein
fertig eingerichteter Laptop, den der Nutzer allein durch Sprechen
bedienen kann: Radio und Musik hören, Briefe schreiben, im Web suchen,
Mediatheken nutzen, E-Mails schreiben, telefonieren, Videocalls führen –
bis hin zur kompletten Systemwartung.

Fokus liegt zunächst auf dem deutschsprachigen Raum.

Dieses Projekt ist in Zusammenarbeit mit [Claude](https://claude.com) entstanden.

## Status

Konzeptphase – es existiert noch keine lauffähige Software. Dieses
Repository sammelt die bisher getroffenen Architektur- und
Design-Entscheidungen als Grundlage für die Umsetzung.

## Dokumentation

- [Debian-zu-DialOS](docs/Debian-zu-DialOS.md) – Schritt-für-Schritt-Rezept: von einer nackten Debian-13/GNOME-Installation bis zur aktuellen Version
- [Architektur-Übersicht](docs/architektur-uebersicht.md) – Ziel, Zielgruppe, Kernfunktionen, Software-Stack
- [Hardware](docs/hardware.md) – Referenzgerät, Test-Hardware, WWAN-Anforderungen
- [Sicherheit & Datenschutz](docs/sicherheit-datenschutz.md) – Autologin, Verschlüsselung, Fernwartung, Versand
- [Sprachsteuerung](docs/sprachsteuerung.md) – STT/TTS-Stack, Intent-Erkennung, Design-Prinzipien
- [Telefonie & Videocall](docs/telefonie.md) – SIM- und Handy-Anbindung, Fallback-Logik
- [Ersteinrichtung & Rollout](docs/ersteinrichtung.md) – Zwei-Phasen-Provisionierung, Sprachassistent, Datenschutz-Varianten
- [Offene Punkte](docs/offene-punkte.md) – was noch zu klären/entscheiden ist

## Logo & Branding

Weitere Varianten liegen in [assets/](assets/): `mark.png` (Bildmarke
allein), `logo-tagline.png` (mit Slogan), `logo-full.png` (mit
Feature-Icon-Zeile), `logo-horizontal-light.png`/`-dark.png` (horizontale
Version für helle/dunkle Hintergründe), `app-icon-light.png`/`-dark.png`
(quadratisches App-Icon) sowie `brand-sheet.png` als vollständige
Referenzübersicht. Dazu `wallpaper-light.png`/`wallpaper-dark.png`
(Desktop-Hintergrund) und `splash.png` (Boot-/Login-Bildschirm).

## Testumgebung

- Lenovo ThinkPad T490 (ohne WWAN-Modul)
- USB-Sicherheits-Stick
- Android-Testgerät für Handy-Anbindung (USB-Tethering + GSConnect)

## Änderungsprotokoll

### 0.5.0
- **Sicherheitsfix Schlüssel-Backup:** `dialos-install` und `dialos-rekey`
  verschlüsselten das Nextcloud-Backup der LUKS-Schlüsseldatei bisher mit
  demselben Wiederherstellungs-Passwort, das auch als zweiter
  LUKS-Schlüssel-Slot dient - wer beides kannte, hätte den Schlüssel ganz
  ohne den physischen Stick entschlüsseln können. Jetzt: eigenes,
  zufällig erzeugtes Backup-Passwort (`openssl rand -base64 32`),
  Passwortübergabe an `openssl` über eine geshredete Temp-Datei statt
  Kommandozeilen-Argument (verhindert Sichtbarkeit in `ps aux`),
  Wiederherstellungs-Passwort braucht jetzt mindestens 12 Zeichen.
- **Sicherheits-Stick partitioniert jetzt in zwei Bereiche:** `DIALOS-KEY`
  (2 GiB, FAT32, wie bisher für die Schlüsseldatei) + `DIALOS-DATA`
  (Rest der Kapazität, ext4, allgemeiner Datenspeicher) - vorher wurde
  die gesamte Stick-Kapazität für die winzige Schlüsseldatei
  "verschwendet". Neue Mindestgrößen-Prüfung (~2,5 GB) verhindert eine
  kaputte/leere Datenpartition bei zu kleinen Sticks. Dabei außerdem
  einen Bug behoben: Die Sicherheits-Stick-Auswahl in `dialos-install`
  blendete (anders als die Zielfestplatten-Auswahl) das aktuelle
  Live-Boot-Medium nicht aus - bei drei angeschlossenen Medien
  (Boot-Stick, Sicherheits-Stick, interne Platte) hätte der Boot-Stick
  fälschlich als Sicherheits-Stick wählbar sein können.
- **Admin-Zugriff dokumentiert und korrigiert:** Erst wurde GNOME
  "Benutzer wechseln" als Weg für parallelen `dialosadmin`-Zugriff neben
  der laufenden `nutzer`-Sitzung dokumentiert. Beim Rekonstruieren der
  Vortags-Session kam aber ein bereits gefundener Bug ans Licht (siehe
  unten): "Benutzer wechseln" lässt `nutzer`s Sitzung im Hintergrund
  aktiv, zwei gleichzeitig laufende `dialos-start-ansage.py`-Instanzen
  konkurrieren dann um Bluetooth/Audio. Korrigierte Praxis: `nutzer`
  richtig abmelden, danach als `dialosadmin` anmelden. Eine
  Boot-Zeit-Tastenkombination für direkten Admin-Zugriff bleibt als
  offene Verbesserungsoption vorgemerkt (`docs/offene-punkte.md`).
- **Bluetooth-Audio-Bug behoben** (`dialos-start-ansage.py`): Nach dem
  Login blieb die Sprachansage über den Bluetooth-Lautsprecher
  intermittierend aus. Ursache: mehrere gleichzeitig laufende
  Skript-Instanzen (durch Kontowechsel ohne echtes Abmelden)
  konkurrierten um Bluetooth-Reconnect und Audio-Stummschaltung. Fix:
  Ein-Instanz-Lock pro Konto (`alte_instanz_beenden()`) sowie ein
  Bluetooth-Debug-Log (`bluetooth_debug_snapshot()`) für künftige
  Fehlersuche ohne manuelles Nachstellen.
- **Spracherkennung (Vosk) technisch zum Laufen gebracht:** Vosk 0.3.45 +
  deutsche Modelle (groß `vosk-model-de-0.21`, 6,3 GB; klein
  `vosk-model-small-de-0.15`, 183 MB) installiert, reines
  Technik-Testskript `dialos-vosk-test.py` (Mikrofon wählen, aufnehmen,
  transkribieren, im Terminal anzeigen - noch ohne Anbindung an
  Intent-Erkennung/TTS). Aufnahme-Modus bewusst "erst vollständig
  aufnehmen, dann erkennen" statt Echtzeit-Streaming, da das große
  Modell laut offizieller Beschreibung für Telefonie/Server gedacht ist,
  nicht Echtzeit auf Laptop-Hardware. Mikrofon-Vergleichstest AIRHUG
  Bluetooth vs. eingebautes Laptop-Mikrofon: Bluetooth klar überlegen (6
  von 8 Testsätzen exakt korrekt bei normaler Sprechlautstärke, gegenüber
  deutlich schwächeren Ergebnissen beim eingebauten Mikrofon) -
  Zielbild: DialOS wird künftig immer mit einem mobilen
  Bluetooth-Lautsprecher/Mikrofon installiert, eingebautes Mikrofon nur
  als (noch nicht implementierter) Fallback.
- **Intent-Erkennung auf [hassil](https://github.com/OHF-Voice/hassil)
  festgelegt** statt des ursprünglich angedachten Rhasspy, das 2026 vom
  Ersteller archiviert wurde und nicht mehr weiterentwickelt wird -
  hassil bietet denselben Beispielsatz-Ansatz, aber als schlanke
  Python-Bibliothek ohne Docker/eigenen Dienst (siehe
  [docs/sprachsteuerung.md](docs/sprachsteuerung.md)).
- Neue Sprachausgabe-Aktiv-Anzeige im GNOME-Panel
  (`dialos-tts-indicator.py`): Icon erscheint während jeder
  Sprachausgabe und verschwindet danach zuverlässig - nützlich, falls
  die Lautstärke zu leise eingestellt ist und eine sehende Person
  trotzdem sehen soll, dass gerade gesprochen wird.
- `dialos-start-ansage.py` weiter verbessert: Zahlwort-Bug behoben
  ("einsundzwanzig" → "einundzwanzig"), Internetstatus/Wetter/Abschluss
  in einem einzigen Sprachausgabe-Aufruf statt mehrerer (verhinderte
  kurze Hintergrundmusik-Einblendungen zwischen den Aufrufen),
  Akku-Ansage nur noch für tatsächlich verbundene Geräte, neue
  Hintergrund-Überwachung meldet Internet-Statuswechsel auch nach der
  Anmeldung, kontobasierter Filter (Kundenkonto `nutzer` bekommt nur
  Laptop + Lautsprecher abgefragt, jedes andere Konto die volle
  Variante mit Maus/Tastatur).
- Netzwerk-Priorität WLAN/Kabel vor SIM umgesetzt und auf dem T490
  verifiziert (NetworkManager-Routenmetriken).
- Zwei ISO-Testbuilds erstellt: `DialOS-Live-0.5.0.iso` (ohne Klonen,
  generischer Live-Nutzer als Sicherheitsnetz) und
  `DialOS-Live-0.5.0-clone.iso` (mit `--clone`, übernimmt `dialosadmin`
  und `nutzer` inkl. Home-Verzeichnissen aus dem echten System - für
  den geplanten Live-Test von `dialos-install` mit dem Sicherheits-Stick
  gedacht).
- Zwei nie gepushte Commits aus einer veralteten lokalen Repo-Kopie
  wiederhergestellt und ins echte Repository nachgezogen (Bluetooth-Fix
  und dessen Dokumentation) - Repository liegt jetzt vollständig auf der
  externen Platte, veraltete Zweitkopie war zwischenzeitlich ungenutzt
  weitergelaufen.

### 0.4.0
- Evolution und GNOME Kalender aus App-Grid und Suche entfernt (nur
  Thunderbird soll für E-Mail und Kalender genutzt werden): `apt purge`
  ist bei beiden nicht möglich, da `evolution-data-server` bzw.
  `gnome-calendar` fest an die Metapakete `gnome`/`gnome-core`/
  `task-gnome-desktop` gekoppelt sind (ein Entfernungsversuch hätte fast
  den kompletten GNOME-Desktop mitgerissen - vorher per
  `apt-get -s purge` simuliert und rechtzeitig abgebrochen). Stattdessen
  Override-Dateien mit `NoDisplay=true` unter
  `/usr/local/share/applications/org.gnome.Evolution.desktop` bzw.
  `.../org.gnome.Calendar.desktop` angelegt - `/usr/local` wird von
  `apt`/`dpkg` nie angefasst, die Änderung übersteht also künftige
  Debian-Updates.
- Thunderbird als tatsächlicher Standard für E-Mail-Links (`mailto:`)
  und Kalendereinträge (`text/calendar`) gesetzt (`xdg-mime`), inklusive
  deutschem Sprachpaket (`thunderbird-l10n-de`, das - anders als bei
  Firefox und LibreOffice - nicht automatisch über `task-german-desktop`
  mitinstalliert wird). Beides über `/etc/skel/.config/mimeapps.list`
  und die ISO-Paketliste (`desktop.list.chroot`) für jedes künftige
  Konto (DialOS-Admin wie nutzer) hinterlegt.
- Calamares entfernt sich künftig automatisch nach der Installation vom
  fertig installierten Zielsystem (neuer Schritt im
  `shellprocess`-Nachinstallationsmodul) - wird auf dem Zielsystem nicht
  mehr gebraucht. Wichtig dabei: Der Schritt läuft ausschließlich im
  chroot des NEUEN Systems, nicht auf der Live-Vorlage, von der aus
  künftige ISOs gebaut werden - sonst hätte die nächste ISO gar keinen
  Installer mehr enthalten. Noch nicht über eine echte Installation
  verifiziert.
- Bluetooth-Kopplungsdaten für die drei Standard-Peripheriegeräte dieses
  Testgeräts (Maus "Pebble M350s", Tastatur "Pebble K380s", externer
  Lautsprecher/Mikrofon "AIRHUG 01") fest ins Image aufgenommen
  (`/var/lib/bluetooth/<Adapter-MAC>/...`), damit nach einer
  Neuinstallation auf diesem Laptop keine erneute Kopplung nötig ist
  (funktioniert, weil der eingebaute Bluetooth-Adapter des Laptops
  gleich bleibt). Dabei eine unverankerte `.gitignore`-Regel (`cache/`)
  gefunden und korrigiert, die versehentlich auch echte Systemordner
  wie `var/cache/...` in der ISO-Vorlage gefiltert hätte.
- Akkustand-Anzeige in der oberen Leiste eingerichtet: GNOME-Erweiterung
  "Bluetooth Battery Monitor" zeigt Laptop- und Bluetooth-Geräte-Akku
  (liest die Werte über `upower`/UPower aus), Akku-Prozentanzeige
  aktiviert. Erweiterung und Einstellung systemweit als Standard für
  alle künftigen Konten hinterlegt
  (`/etc/skel/.local/share/gnome-shell/extensions/`,
  `/etc/dconf/db/local.d/01-dialos-defaults`).
- Neue Sprachansage beim Anmelden ("Michael", der persönliche
  Assistent, `/usr/local/bin/dialos-start-ansage.py`): begrüßt, nennt
  Datum und Uhrzeit, liest die Akkustände von Laptop, Maus, Tastatur und
  Lautsprecher vor, meldet bei Internetverbindung das Tageswetter
  (Morgens/Mittags/Nachmittags/Abends, inkl. Regenschirm-Hinweis bei
  Regenwahrscheinlichkeit, Standort wird automatisch per IP erkannt) und
  verabschiedet sich. Verbindet dabei automatisch alle gekoppelten
  Bluetooth-Geräte neu (behebt ein Problem, bei dem der
  Bluetooth-Lautsprecher nach einer Ab-/Anmeldung nicht selbstständig
  wiederverbunden wurde) und schaltet über ein wiederverwendbares
  Sprachausgabe-Skript mit Audio-Ducking (`/usr/local/bin/dialos-say.py`)
  andere Audioquellen für die Dauer der Ansage stumm. Läuft automatisch
  bei jedem Login für alle Konten
  (`/etc/xdg/autostart/dialos-start-ansage.desktop`).
- Änderungsprotokoll in dieser Datei in die richtige (neueste zuerst)
  Reihenfolge sortiert.

### 0.3.0
- Login-Avatar für "DialOS-Admin" gesetzt: das schon vorhandene
  Buero-Setup-Skript `scripts/dialos-set-avatar.sh` tatsaechlich
  ausgefuehrt (setzt die DialOS-Bildmarke per AccountsService/D-Bus als
  Profilbild) - vorher nur geschrieben, aber nie angewendet.
- Autologin-Kette repariert und verifiziert: Standard-Benutzer "nutzer"
  angelegt, Autologin laeuft korrekt ueber AccountsService (nicht ueber
  das dafuer ignorierte `/etc/gdm3/custom.conf`), Admin-Konto behaelt
  kein Autologin. Dabei einen Timing-Bug in
  `scripts/dialos-setup-nutzer.sh` gefunden ("user is locked" direkt
  nach `chpasswd`, weil AccountsService die neue Passwort-Zeile noch
  nicht bemerkt hatte) und mit Wiederholungslogik behoben (auch in der
  ISO-Vorlage unter `iso-build/config/includes.chroot/etc/skel/Desktop/`
  nachgezogen).
- Neuer fester Sammelordner `~/Dokumente/DialOS/` auf dem Testgeraet für
  alle Dateien, die nach einer Installation für die Einrichtung
  gebraucht werden - als erstes Werkzeug liegt dort
  `nutzer-anlegen.sh` (robustere Kopie des Autologin-Skripts) sowie ein
  Angaben-Formular für die Thunderbird-Kontoeinrichtung
  (`thunderbird-angaben-formular.md`).
- Firefox: Startseite per Enterprise-Policy auf `https://dialos.org`
  gesetzt (`policies.json` unter
  `usr/lib/firefox-esr/distribution/` im ISO-Rezept - der alternative
  `/etc/firefox-esr/`-Pfad wird von diesem Debian-Paket nicht
  unterstuetzt).
- Versuch, ein DialOS-Wallpaper als Hintergrund der "Neuer Tab"-Seite zu
  hinterlegen, zurueckgestellt: Firefox respektiert `browser.newtab.url`
  in aktuellen Versionen nicht mehr zuverlaessig (fuehrt nur zu einer
  leeren Seite), eine eigene Erweiterung dafuer waere mit
  Signatur-Aufwand verbunden und wurde bewusst nicht umgesetzt.

### 0.2.0
- Erste Live-Boot-Installationstests auf realer Hardware (Lenovo T490)
  durchgeführt und iterativ ausgewertet; ISO-Build-Workflow mit
  Penguins' Eggs eingerichtet (Rezept unter `iso-build/config/`, Build-
  und Testzyklus in CLAUDE.md dokumentiert).
- Kosmetik-Fixes für den Installer erarbeitet und per Live-Boot-Test
  bestätigt: NTP-Client (`systemd-timesyncd`) ergänzt, Partitionen-
  Fenster vergrößert (800×580 → 1000×700), Calamares-Assistent zeigt
  jetzt durchgängig DialOS-Branding statt der Penguins'-Eggs-
  Standardoptik (Vendor-Overlay unter
  `/etc/penguins-eggs.d/brain.d/assets/calamares/`), das Live-
  Installer-Icon im App-Grid heißt jetzt "DialOS installieren" mit
  eigenem Icon statt "Install System" mit Ei-Icon, und während der
  Installation läuft kein Pinguin-Werbematerial mehr.
- Live-Dash-Favoriten angepasst: statt des generischen "Debian
  installieren"-Icons erscheint dort jetzt das DialOS-Icon.
- Zentrale Erkenntnis dabei: `iso-build/config/includes.chroot/...` ist
  nur eine Vorlage im Git-Repo - Änderungen müssen vor jedem
  `eggs produce` manuell aufs echte System kopiert werden, sonst landen
  sie nicht im gebauten Image (Details in CLAUDE.md).
- Bekannte, bewusst zurückgestellte Einschränkung: Die Standort-Seite im
  Installer schlägt GeoIP-basiert manchmal einen falschen Ort vor (z. B.
  Rome statt Berlin) - kein Vendor-Override dafür gefunden, unkritisch
  bei Zwei-Phasen-Provisionierung.
- Git-Repository und ISO-Ausgabeordner liegen jetzt auf einer externen
  Festplatte statt nur lokal auf dem T490, damit sie einen erneuten
  Reinstall des Testrechners überstehen.

### 0.1.0
- Projekt gestartet: Anforderungen, Architektur- und Design-Entscheidungen
  aus der Konzeptphase dokumentiert.
