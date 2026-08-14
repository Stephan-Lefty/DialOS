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

## Encrypting nutzer's data + security stick

**Design since 2026-08-14** (replaces the original whole-disk
encryption, see README changelog 0.5.0).

**Why not the initramfs path anymore:** the real live-boot test of
`dialos-install` with whole-disk LUKS encryption failed on 2026-08-14.
The reason wasn't a single bug but that the whole LUKS/initramfs path is
structurally error-prone: the key file had to be available at exactly
the right moment inside the initramfs (one bug unmounted the stick
before `cryptsetup open` even used it), and the installer itself didn't
run smoothly either (a `pkexec` bug made the file-save dialog for the
key backup fail silently). An initramfs offers almost no error
output/debugging options for the target group on site - any failure
there means a device that won't boot, with no way to help themselves
until Stephan steps in.

**Current design:** instead of the whole disk, only a dedicated
partition holding exclusively `nutzer`'s data is encrypted - and that
partition is opened NOT in the initramfs, but after boot, inside the
already-running normal system environment:

- **root partition** (ext4, ~100 GiB): the OS + `dialosadmin`'s home,
  **unencrypted**. Always boots completely normally, no more initramfs
  pitfalls.
- **`dialos-nutzer-home` partition** (LUKS2, remaining capacity):
  holds exclusively `/home/nutzer`. Found via `blkid -L
  dialos-nutzer-home` (LUKS2 label, no `/etc/crypttab` entry needed).
- The security stick (`DIALOS-KEY` partition) still carries the key
  file, plus a second data area `DIALOS-DATA` for general storage -
  **unchanged** from before.
- `dialos-stick-gate.service` (systemd oneshot, runs on **every boot**
  before `display-manager.service`) checks whether the stick is
  present: if so, it opens `dialos-nutzer-home` with the key from the
  stick and mounts it at `/home/nutzer`; only then is `nutzer`'s
  autologin enabled (`SetAutomaticLogin true` via AccountsService/
  `gdbus`, the same mechanism as in `scripts/dialos-setup-nutzer.sh`
  and [Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 4). If any
  step fails (no stick, wrong/damaged stick, home partition missing),
  `/home/nutzer` stays an empty directory and autologin is disabled -
  GDM shows the normal login screen, on which practically only
  `dialosadmin` is usable (`nutzer`'s password is a random string
  nobody knows).
- `dialosadmin` is completely unaffected: never autologin, always a
  normal typed password at the GDM screen, independent of the stick.

This still delivers the original ideal flow for the target group (plug
in the stick → power on the device → the system speaks to the user,
without typing or reading anything), but without the fragile initramfs
chain - and it now actually protects what's most sensitive on the
device: `nutzer`'s own data. System files, `dialosadmin`'s home, and
logs stay deliberately unencrypted (a deliberate trade-off - see README
changelog 0.5.0 for the reasoning).

Scripts/units: `usr/local/sbin/dialos-install`,
`usr/local/sbin/dialos-rekey`, `usr/local/sbin/dialos-stick-gate.sh`,
`etc/systemd/system/dialos-stick-gate.service` (all in the repo under
`iso-build/config/includes.chroot/`, installation see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 12).

**Practical notes:**
- The stick should be kept separately from the laptop (e.g. on a
  keyring), otherwise the encryption provides little benefit if both are
  stolen together.
- **Recommended standard size: 64 GB.** `dialos-install`/`dialos-rekey`
  always partition the stick into `DIALOS-KEY` (2 GiB, key) +
  `DIALOS-DATA` (remaining capacity, general storage) - at 64 GB this
  gives `nutzer` about 62 GB of it automatically as portable storage
  (e.g. for photos, documents) they can take along independently of the
  device.
- `scripts/dialos-setup-nutzer.sh` (creates the `nutzer` account during
  office setup) checks before `adduser` whether `/home/nutzer` is
  already mounted, and aborts cleanly if not - otherwise `nutzer`'s home
  with all its skel default settings would accidentally end up on the
  unencrypted root partition.

## Recovery when a stick is lost

Three paths, depending on the situation:

1. **Manually enter the recovery passphrase, via `dialosadmin`.** Since
   `nutzer`'s home partition is no longer opened in the initramfs,
   there's no more automatic password prompt at the boot screen -
   `dialosadmin`'s own login, however, is completely independent of the
   stick and always works with a typed password. Flow: log in as
   `dialosadmin`, open a terminal, run
   `sudo cryptsetup open --type luks2 $(sudo blkid -L dialos-nutzer-home) dialos-nutzer-home`
   (prompts for the recovery passphrase), then
   `sudo mount /home/nutzer && sudo /usr/local/sbin/dialos-stick-gate.sh`
   - unlocks `nutzer`'s autologin for this session. Fully offline,
   independent of the stick and the network — the only way to get a
   device running again at all when nothing else is reachable. Talked
   through by Stephan over the phone, or typed by a trusted person on
   site — never known by the end user themselves. **Important:** this is
   only a one-time unlock for the current session - after a reboot
   without the stick, the normal lock applies again; use path 2 for a
   permanent fix.
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
