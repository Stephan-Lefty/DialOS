[Deutsch](README.md) | [English](README.en.md) | [Changelog](#changelog)

<img src="assets/logo.png" alt="Stephan-OS logo" width="360">

# Stephan-OS

A fully voice-controlled system based on Debian 13 + GNOME for people who
can only use a computer to a limited extent — in particular blind and
motor-impaired individuals. The goal is a ready-to-use laptop that the
user can operate entirely by speaking: listening to radio and music,
writing letters, searching the web, using streaming media libraries
(ARD/ZDF Mediatheken), writing emails, making phone calls, video calls —
all the way to complete system maintenance.

The initial focus is on the German-speaking region (Germany, Austria,
Switzerland).

This project was created in collaboration with [Claude](https://claude.com).

## Status

Concept phase — no working software exists yet. This repository collects
the architecture and design decisions made so far as a foundation for
implementation.

## Documentation

- [Architecture overview](docs/architektur-uebersicht.en.md) – goal, target audience, core features, software stack
- [Hardware](docs/hardware.en.md) – reference device, test hardware, WWAN requirements
- [Security & privacy](docs/sicherheit-datenschutz.en.md) – autologin, encryption, remote support, shipping
- [Voice control](docs/sprachsteuerung.en.md) – STT/TTS stack, intent recognition, design principles
- [Telephony & video calls](docs/telefonie.en.md) – SIM and phone-tethering, fallback logic
- [Initial setup & rollout](docs/ersteinrichtung.en.md) – two-phase provisioning, voice assistant, privacy variants
- [Open questions](docs/offene-punkte.en.md) – what still needs to be decided

## Logo & branding

More variants are available in [assets/](assets/): `mark.png` (icon
alone), `logo-tagline.png` (with tagline), `logo-full.png` (with the
feature icon row), `logo-horizontal-light.png`/`-dark.png` (horizontal
version for light/dark backgrounds), `app-icon-light.png`/`-dark.png`
(square app icon), and `brand-sheet.png` as a complete reference
overview. Plus `wallpaper-light.png`/`wallpaper-dark.png` (desktop
background) and `splash.png` (boot/login screen).

## Test environment

- Lenovo ThinkPad T490 (no WWAN module)
- USB security stick
- Android test device for phone tethering (USB tethering + GSConnect)

## Changelog

### 0.1.0
- Project started: requirements, architecture, and design decisions from
  the concept phase documented.
