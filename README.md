[Deutsch](README.md) | [English](README.en.md) | [Änderungsprotokoll](#änderungsprotokoll) | [TODO](TODO.md)

<img src="assets/logo.png" alt="DialOS Logo" width="360">

Website: [dialos.org](https://dialos.org)

# DialOS

Ein auf Debian 13 + GNOME basierendes, vollständig sprachgesteuertes
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
