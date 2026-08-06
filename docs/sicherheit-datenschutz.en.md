[Deutsch](sicherheit-datenschutz.md) | [English](sicherheit-datenschutz.en.md)

# Security & privacy

## Guiding principle

The target group (blind, motor-impaired, often elderly people) is
particularly vulnerable. Privacy and fail-safety therefore consistently
take priority over convenience or recognition quality:

- Speech recognition runs offline (Vosk/local models), no cloud services.
- Security-critical actions always go through an explicit yes/no
  confirmation.
- It is always assumed that a user may not want to hand over their setup
  data freely (see [ersteinrichtung.en.md](ersteinrichtung.en.md), section
  "Privacy variants").

## Automatic login

The login screen is skipped entirely (GDM autologin), since it would be
one of the biggest obstacles for the target group (typing a password
blind, operating a login chooser). Trade-off: physical access to the
device means direct access to the system — mitigated by disk encryption
with a hardware key (see below).

## Disk encryption with a USB key

The PC should only boot/unlock when a specific USB stick is plugged in.
Implementation: **LUKS disk encryption with a key file on the USB stick**
— a script in the initramfs waits for the stick at boot and automatically
unlocks the disk once it is detected, with no password entry needed. If
the stick is missing, the system stays encrypted.

Combined with autologin, this gives an ideal flow for the target group:
plug in the stick → power on the device → the system is immediately ready
and speaks to the user, without anything needing to be typed or read.

**Practical notes:**
- The stick should be kept separately from the laptop (e.g. on a
  keyring), otherwise the encryption provides little benefit if both are
  stolen together.
- **Open**: recovery path if the stick is lost or damaged (options: a
  master passphrase held by a trusted person, a duplicate backup stick,
  or deliberately no recovery — not yet decided).

## Shipping security

Laptop and security stick should be shipped separately (different
day/carrier), so that an intercepted package alone is useless.

## Remote support (RustDesk)

- Open source, self-hostable — fits the project's privacy stance.
- **Relay**: initially the public rustdesk.com service, later (once the
  system runs stably) a self-hosted server (hbbs/hbbr). The migration is
  a deliberately open point for later.
- **Unattended access** runs with a permanent password, so a helper can
  get in even if the user isn't able to respond. For blind users, the
  RustDesk ID/password must be read aloud via TTS, since they can't read
  it off the screen themselves.
- **Additional safety layer**: RustDesk does NOT run permanently in the
  background/autostart. The user on site must actively start RustDesk via
  a voice command (e.g. "call for help") — only then is a remote
  connection possible at all, despite the permanent password.
  Consequence: "true" emergency remote support (user completely
  unresponsive, system frozen) deliberately does not work this way — only
  help actively requested by the user.

## System base

Debian remains the base (no switch to an atomic/immutable system such as
Fedora Atomic/Silverblue or openSUSE Aeon) — Stephan prioritizes Debian's
stability, hardware support, and the mature live-build tooling over
built-in atomic rollback. A rollback safety net would need to be added
separately via Btrfs snapshots if needed.
