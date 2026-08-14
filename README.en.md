[Deutsch](README.md) | [English](README.en.md) | [Changelog](#changelog)

<img src="assets/logo.png" alt="DialOS logo" width="360">

Website: [dialos.org](https://dialos.org)

# DialOS

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

- [Debian to DialOS](docs/Debian-zu-DialOS.en.md) – step-by-step recipe: from a bare Debian 13/GNOME install to the current version
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

### 0.5.0
- **Key-backup security fix:** `dialos-install` and `dialos-rekey` used
  to encrypt the Nextcloud backup of the LUKS key file with the same
  recovery passphrase that also serves as the second LUKS key slot -
  anyone who knew both could have decrypted the key entirely without the
  physical stick. Now: a dedicated, randomly generated backup password
  (`openssl rand -base64 32`), the password is passed to `openssl` via a
  shredded temp file instead of a command-line argument (prevents
  visibility in `ps aux`), and the recovery passphrase now requires at
  least 12 characters.
- **Security stick now partitioned into two areas:** `DIALOS-KEY` (2
  GiB, FAT32, as before for the key file) + `DIALOS-DATA` (remaining
  capacity, ext4, general-purpose storage) - previously the stick's
  entire capacity was "wasted" on the tiny key file. A new minimum-size
  check (~2.5 GB) prevents a broken/empty data partition on sticks that
  are too small. Also fixed a bug: the security-stick picker in
  `dialos-install` (unlike the target-disk picker) didn't exclude the
  current live boot medium - with three media plugged in (boot stick,
  security stick, internal disk), the boot stick could have been
  mistakenly selectable as the security stick.
- **Admin access documented, then corrected:** GNOME "switch user" was
  first documented as a way to get parallel `dialosadmin` access
  alongside the running `nutzer` session. While reconstructing the
  previous day's session, an already-discovered bug came to light (see
  below): "switch user" leaves `nutzer`'s session active in the
  background, and two concurrently running `dialos-start-ansage.py`
  instances then compete over Bluetooth/audio. Corrected practice:
  properly log `nutzer` off, then log in as `dialosadmin`. A boot-time
  key combination for direct admin access remains noted as an open
  improvement option (`docs/offene-punkte.md`).
- **Bluetooth audio bug fixed** (`dialos-start-ansage.py`): after login,
  the voice announcement over the Bluetooth speaker intermittently
  stayed silent. Cause: multiple concurrently running script instances
  (from switching accounts without a proper logout) competed over
  Bluetooth reconnect and audio muting. Fix: a per-account
  single-instance lock (`alte_instanz_beenden()`) plus a Bluetooth debug
  log (`bluetooth_debug_snapshot()`) for future troubleshooting without
  manual reproduction.
- **Speech recognition (Vosk) brought up technically:** Vosk 0.3.45 +
  German models (large `vosk-model-de-0.21`, 6.3 GB; small
  `vosk-model-small-de-0.15`, 183 MB) installed, a pure technical test
  script `dialos-vosk-test.py` (choose microphone, record, transcribe,
  display in the terminal - not yet wired to intent recognition/TTS).
  Recording mode deliberately "record fully first, then recognize"
  rather than real-time streaming, since the large model is described
  officially as intended for telephony/servers, not real-time use on
  laptop hardware. Microphone comparison test, AIRHUG Bluetooth vs.
  built-in laptop microphone: Bluetooth clearly superior (6 out of 8
  test sentences exactly correct at normal speaking volume, vs.
  noticeably weaker results with the built-in microphone) - target
  design: DialOS will always be installed with a mobile Bluetooth
  speaker/microphone, with the built-in microphone only as a (not yet
  implemented) fallback.
- **Intent recognition set to [hassil](https://github.com/OHF-Voice/hassil)**
  instead of the originally planned Rhasspy, which was archived by its
  creator in 2026 and is no longer maintained - hassil offers the same
  example-sentence approach, but as a lightweight Python library with no
  Docker/dedicated service (see
  [docs/sprachsteuerung.en.md](docs/sprachsteuerung.en.md)).
- New voice-output-active indicator in the GNOME panel
  (`dialos-tts-indicator.py`): an icon appears during every voice
  announcement and reliably disappears afterward - useful if the volume
  is set too low and a sighted person should still be able to see that
  something is being/was spoken.
- `dialos-start-ansage.py` further improved: fixed a German number-word
  bug, folded the internet-status/weather/closing remarks into a single
  voice-output call instead of several (this had caused brief flashes of
  background music between calls), battery announcements now only for
  devices that are actually connected, a new background monitor reports
  internet status changes after login too, account-based filtering
  (the customer account `nutzer` is only asked about laptop + speaker,
  every other account gets the full variant including mouse/keyboard).
- Network priority WLAN/wired over SIM implemented and verified on the
  T490 (NetworkManager route metrics).
- Built two test ISOs: `DialOS-Live-0.5.0.iso` (without cloning, a
  generic live user as a safety net) and `DialOS-Live-0.5.0-clone.iso`
  (with `--clone`, carries over `dialosadmin` and `nutzer` including
  home directories from the real system - intended for the planned live
  test of `dialos-install` with the security stick).
- Recovered two never-pushed commits from a stale local repo copy and
  brought them into the real repository (the Bluetooth fix and its
  documentation) - the repository now lives entirely on the external
  drive; the stale second copy had kept running unused in the meantime.

### 0.4.0
- Removed Evolution and GNOME Calendar from the app grid and search
  (only Thunderbird should be used for email and calendar): `apt purge`
  isn't possible for either, since `evolution-data-server` and
  `gnome-calendar` respectively are tightly coupled to the
  `gnome`/`gnome-core`/`task-gnome-desktop` metapackages (an attempted
  removal would have pulled almost the entire GNOME desktop along with
  it - simulated beforehand via `apt-get -s purge` and aborted in time).
  Instead, override files with `NoDisplay=true` were created under
  `/usr/local/share/applications/org.gnome.Evolution.desktop` and
  `.../org.gnome.Calendar.desktop` - `/usr/local` is never touched by
  `apt`/`dpkg`, so the change survives future Debian updates.
- Set Thunderbird as the actual default for email links (`mailto:`) and
  calendar entries (`text/calendar`) (`xdg-mime`), including the German
  language pack (`thunderbird-l10n-de`, which - unlike Firefox and
  LibreOffice - isn't installed automatically via
  `task-german-desktop`). Both stored via
  `/etc/skel/.config/mimeapps.list` and the ISO package list
  (`desktop.list.chroot`) for every future account (DialOS-Admin as
  well as nutzer).
- Calamares now automatically removes itself after installation from
  the freshly installed target system (a new step in the
  `shellprocess` post-install module) - no longer needed on the target
  system. Important detail: the step runs exclusively inside the chroot
  of the NEW system, not on the live template that future ISOs are
  built from - otherwise the next ISO would ship without an installer
  at all. Not yet verified via a real installation.
- Baked the Bluetooth pairing data for this test device's three
  standard peripherals (mouse "Pebble M350s", keyboard "Pebble K380s",
  external speaker/microphone "AIRHUG 01") directly into the image
  (`/var/lib/bluetooth/<adapter-MAC>/...`), so that no re-pairing is
  needed after a reinstall on this laptop (works because the laptop's
  built-in Bluetooth adapter stays the same). While doing so, found and
  fixed an unanchored `.gitignore` rule (`cache/`) that would have
  accidentally filtered out real system directories like
  `var/cache/...` in the ISO template too.
- Set up a battery-level display in the top bar: the GNOME extension
  "Bluetooth Battery Monitor" shows laptop and Bluetooth device battery
  levels (reads the values via `upower`/UPower), battery percentage
  display enabled. Extension and setting stored system-wide as the
  default for all future accounts
  (`/etc/skel/.local/share/gnome-shell/extensions/`,
  `/etc/dconf/db/local.d/01-dialos-defaults`).
- New voice announcement at login ("Michael", the personal assistant,
  `/usr/local/bin/dialos-start-ansage.py`): greets the user, states the
  date and time, reads out the battery levels of laptop, mouse,
  keyboard, and speaker, reports the day's weather if there's an
  internet connection (morning/midday/afternoon/evening, including an
  umbrella hint if rain is likely, location auto-detected via IP), and
  says goodbye. Automatically reconnects all paired Bluetooth devices
  while doing so (fixes an issue where the Bluetooth speaker didn't
  reconnect on its own after a logout/login) and mutes other audio
  sources for the duration of the announcement via a reusable
  voice-output script with audio ducking (`/usr/local/bin/dialos-say.py`).
  Runs automatically at every login for all accounts
  (`/etc/xdg/autostart/dialos-start-ansage.desktop`).
- Sorted the changelog in this file into the correct (newest first)
  order.

### 0.3.0
- Set the login avatar for "DialOS-Admin": actually ran the office-setup
  script that already existed (`scripts/dialos-set-avatar.sh`, sets the
  DialOS mark as the profile picture via AccountsService/D-Bus) - it had
  previously only been written, never applied.
- Fixed and verified the autologin chain: created the standard user
  "nutzer", autologin now correctly runs via AccountsService (not via
  the ignored `/etc/gdm3/custom.conf`), the admin account keeps no
  autologin. Found and fixed a timing bug in
  `scripts/dialos-setup-nutzer.sh` along the way ("user is locked" right
  after `chpasswd`, because AccountsService hadn't yet noticed the new
  password entry) with retry logic (also backported into the ISO
  template under
  `iso-build/config/includes.chroot/etc/skel/Desktop/`).
- New fixed collection folder `~/Dokumente/DialOS/` on the test device
  for all files needed for setup after an installation - the first tool
  placed there is `nutzer-anlegen.sh` (a more robust copy of the
  autologin script) plus a form for Thunderbird account setup details
  (`thunderbird-angaben-formular.md`).
- Firefox: set the homepage to `https://dialos.org` via an enterprise
  policy (`policies.json` under `usr/lib/firefox-esr/distribution/` in
  the ISO recipe - the alternative `/etc/firefox-esr/` path isn't
  supported by this Debian package).
- Deferred an attempt to set a DialOS wallpaper as the background of the
  Firefox "New Tab" page: current Firefox versions no longer reliably
  respect `browser.newtab.url` (it just results in a blank page), and a
  custom extension for this would have required signing overhead, so it
  was deliberately not implemented.

### 0.2.0
- Ran and iteratively evaluated the first live-boot install tests on
  real hardware (Lenovo T490); set up the ISO build workflow with
  Penguins' Eggs (recipe under `iso-build/config/`, build and test cycle
  documented in CLAUDE.md).
- Worked out cosmetic fixes for the installer and confirmed them via a
  live-boot test: added an NTP client (`systemd-timesyncd`), enlarged
  the partitioning window (800×580 → 1000×700), the Calamares assistant
  now consistently shows DialOS branding instead of the Penguins' Eggs
  default look (vendor overlay under
  `/etc/penguins-eggs.d/brain.d/assets/calamares/`), the live installer
  icon in the app grid is now called "Install DialOS" with its own icon
  instead of "Install System" with the egg icon, and no more penguin
  promotional material shows during installation.
- Adjusted the live dash favorites: the generic "Install Debian" icon is
  now replaced there by the DialOS icon.
- Key insight along the way: `iso-build/config/includes.chroot/...` is
  only a template in the git repo - changes must be manually copied onto
  the real system before every `eggs produce`, otherwise they don't end
  up in the built image (details in CLAUDE.md).
- Known, deliberately deferred limitation: the location page in the
  installer sometimes suggests a wrong location based on GeoIP (e.g.
  Rome instead of Berlin) - no vendor override found for this;
  uncritical given two-phase provisioning.
- The git repository and ISO output folder now live on an external hard
  drive instead of only locally on the T490, so they survive a
  reinstall of the test machine.

### 0.1.0
- Project started: requirements, architecture, and design decisions from
  the concept phase documented.
