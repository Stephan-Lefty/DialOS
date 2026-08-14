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

**Admin access:** The autologin account is always `nutzer`
(`AutomaticLogin=true`), the admin account `dialosadmin` stays active but
without autologin (`AutomaticLogin=false`) – see
`scripts/dialos-setup-nutzer.sh`. For interventions on site or via
RustDesk (after `nutzer` has said "call for help" by voice): **properly
log `nutzer` off**, then log in as `dialosadmin` with a password at the
GDM screen. Requires `dialosadmin` to have a valid, non-locked password.

**Important, corrected 2026-08-14:** Deliberately **avoid** GNOME
**"switch user"** (instead of a proper logout) – it leaves `nutzer`'s
session active in the background. Per a test finding from 2026-08-13
(see [offene-punkte.en.md](offene-punkte.en.md), entry "Bluetooth
speaker/voice output sometimes inaudible after login"), two
concurrently running `dialos-start-ansage.py` instances (one per
account) then compete over Bluetooth reconnect and audio muting, making
voice output unreliable. The existing single-instance lock in
`dialos-start-ansage.py` only prevents duplicate logins of the *same*
account, not the cross-account overlap that "switch user" creates.

## Disk encryption with a USB key

The PC should only boot/unlock when a specific USB stick is plugged in.
Implementation: **LUKS disk encryption with a key file on the USB stick**
— a script in the initramfs waits for the stick at boot and automatically
unlocks the disk once it is detected, with no password entry needed. If
the stick is missing, the system stays encrypted.

Combined with autologin, this gives an ideal flow for the target group:
plug in the stick → power on the device → the system is immediately ready
and speaks to the user, without anything needing to be typed or read.

**Installation:** From the running live session there's a dedicated
installer tool (`dialos-install`, launchable from the applications
menu) instead of a standard installer like Calamares - its LUKS module
is built around a typed password, not our stick-keyfile concept. The
tool partitions the target disk, generates a random key onto the chosen
security stick, additionally sets up a recovery passphrase (min. 12
characters) as a second LUKS slot (see below), copies the running
system onto the disk, and sets up the bootloader. Meant for
you/technicians during office setup, not the on-site setup -
deliberately not voice-controlled.

**Practical notes:**
- The stick should be kept separately from the laptop (e.g. on a
  keyring), otherwise the encryption provides little benefit if both are
  stolen together.

## Security stick as a presence token (autologin gate)

**Addition since 2026-08-14**, independent of the encryption above.

**Why:** the real live-boot test of `dialos-install` with the security
stick failed on 2026-08-14. The reason wasn't a single bug but that the
whole LUKS/initramfs path is structurally error-prone: the key file has
to be available at exactly the right moment inside the initramfs (one
bug unmounted the stick before `cryptsetup open` even used it), and the
installer itself didn't run smoothly either (a `pkexec` bug made the
file-save dialog for the key backup fail silently, see README changelog
0.5.0). An initramfs offers almost no error output/debugging options for
the target group on site - any failure there means a device that won't
boot, with no way to help themselves until Stephan steps in. Instead of
continuing to patch the fragile path, there is now also a much more
robust, purely software-based presence check that runs entirely inside
an already-running, normal system environment (no initramfs, no
`pkexec`/xdg-portal pitfalls) - independent of the initramfs/LUKS path
above:

- A systemd service (`dialos-stick-gate.service`, runs as a oneshot
  before `display-manager.service`) checks on **every boot** whether a
  partition labeled `DIALOS-KEY` is found (`blkid -L DIALOS-KEY`, with a
  short retry loop for USB detection that lags behind).
- Stick present: autologin for `nutzer` is enabled
  (`SetAutomaticLogin true` via AccountsService/`gdbus`, the same
  mechanism as in `scripts/dialos-setup-nutzer.sh` and
  [Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 4).
- Stick missing: autologin for `nutzer` is disabled
  (`SetAutomaticLogin false`). GDM shows the normal login screen - on it
  practically only `dialosadmin` is usable, since `nutzer`'s password is
  a random string nobody knows.
- `dialosadmin` is completely unaffected: never autologin, always a
  normal typed password at the GDM screen, as before.

Script: `usr/local/sbin/dialos-stick-gate.sh`, unit:
`etc/systemd/system/dialos-stick-gate.service` (both in the repo under
`iso-build/config/includes.chroot/`, installation see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 12).

**Important limitation:** this is purely an **access filter at login**,
not encryption. The disk itself remains unprotected by this gate -
anyone who removes it or boots the device from a live USB reads all the
data directly, regardless of whether the stick is present. Only the
LUKS encryption above still closes that gap. Whether the LUKS encryption
(with its error-prone initramfs installation) remains alongside this
gate long-term or gets dropped is an open decision (see TODO.md) -
currently both mechanisms run independently side by side.

## Recovery when a stick is lost

Three paths, depending on the situation:

1. **Type the recovery passphrase directly at the boot screen.** Works
   immediately, fully offline, independent of the stick and the network
   — the only way to get a device running again at all when nothing
   else is reachable. Talked through by Stephan over the phone, or
   typed by a trusted person on site — never known by the end user
   themselves.
2. **Set up a new stick remotely** (`dialos-rekey`, runs on the
   installed system). Once the device is running once (e.g. via path 1)
   and the user says "call for help", Stephan connects via RustDesk and
   remotely sets up a new stick: a new key is generated, added as a
   LUKS key, the old (lost) key slot is retired, and a new recovery
   passphrase is set.
3. **Stephan makes a replacement stick and mails it**, if the device
   won't boot at all (path 1 not possible either, e.g. hardware failure
   or the passphrase isn't at hand). For this, Stephan downloads this
   user's encrypted key backup from his own Nextcloud, decrypts it
   locally with the matching recovery passphrase, and writes the key
   onto a new stick.

Paths 2 and 3 need the **encrypted key backup**: the installer
(`dialos-install`) and the rekey tool (`dialos-rekey`) encrypt the
small key file (not the whole disk) with a dedicated, randomly
generated backup password (`openssl rand -base64 32`, encrypted via
`openssl enc -aes-256-cbc -pbkdf2`) and offer to save the file —
Stephan stores it in his own, self-hosted Nextcloud (one file per
user/device), not with a third-party cloud provider.

**Important: the backup password is deliberately NOT the same as the
recovery passphrase** from paths 1/2 above. If the same passphrase were
used for both, anyone who knew the recovery passphrase and had access
to the Nextcloud could decrypt the key — entirely without the physical
stick, which would defeat the whole point of tying unlock to the stick.
The tool shows the generated backup password once after saving; Stephan
must store it separately from the Nextcloud (e.g. in his own password
manager), never together with the backup file itself.

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
