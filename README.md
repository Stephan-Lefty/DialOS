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

### 0.1.0
- Projekt gestartet: Anforderungen, Architektur- und Design-Entscheidungen
  aus der Konzeptphase dokumentiert.
