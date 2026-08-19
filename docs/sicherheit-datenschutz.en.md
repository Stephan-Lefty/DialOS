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
device means direct access to the system — mitigated by the fact that
`nutzer`'s data lives on a dedicated partition encrypted with a hardware
key, and that the account is locked without that key (see below).

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
- The security stick still carries the key file on the `DIALOS-KEY`
  partition (**ext4**, so the file isn't even readable under Windows,
  and with `root:root 755` accessible only to root even under Linux),
  plus a second data area `DIALOS-DATA` (**exFAT**, so `nutzer` can use
  it as an ordinary portable drive under Windows/macOS/Linux).
- **Swap has been encrypted as well since 2026-08-16** (8 GiB, key
  re-drawn from `/dev/urandom` on every boot, entry in `/etc/crypttab`).
  Otherwise `nutzer`'s paged-out memory - open documents, mail, browser
  content - could end up on disk in the clear, bypassing the LUKS
  protection. The random key rules out hibernation for good;
  suspend-to-RAM is unaffected. Important when rebuilding: Debian 13
  needs the separate `systemd-cryptsetup` package for this, otherwise
  `/etc/crypttab` is ignored **without any error message**.
- `dialos-stick-gate.service` (systemd oneshot, runs on **every boot**
  before `display-manager.service`) checks whether the stick is
  present: if so, it opens `dialos-nutzer-home` with the key from the
  stick and mounts it at `/home/nutzer`; only then is `nutzer`'s
  autologin enabled (`SetAutomaticLogin true` via AccountsService/
  `gdbus`, the same mechanism as in `scripts/dialos-setup-nutzer.sh`
  and [Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 4). If any
  step fails (no stick, wrong/damaged stick, home partition missing),
  `/home/nutzer` stays an empty directory and autologin is disabled -
  GDM shows the normal login screen.
- **In addition, `nutzer`'s account is locked without the stick**
  (`usermod -L`, since 2026-08-16). Disabling autologin alone was not
  enough: without the stick GDM still lists both accounts, and anyone
  who knew `nutzer`'s random password - it is printed once in the
  terminal when `dialos-setup-nutzer.sh` generates it - could still have
  logged in, into a session against an empty directory on the
  **unencrypted** root partition. The order matters: unlock first, then
  set autologin, because AccountsService rejects `SetAutomaticLogin` for
  a locked account with "user is locked". `dialosadmin` is never
  locked.
- `dialosadmin` is completely unaffected: never autologin, always a
  normal typed password at the GDM screen, independent of the stick.

This still delivers the original ideal flow for the target group (plug
in the stick → power on the device → the system speaks to the user,
without typing or reading anything), but without the fragile initramfs
chain - and it now actually protects what's most sensitive on the
device: `nutzer`'s own data. System files, `dialosadmin`'s home, and
logs stay deliberately unencrypted (a deliberate trade-off - see README
changelog 0.5.0 for the reasoning).

**Proven in both directions on real hardware on 2026-08-16** (backed by
the journal): without the stick, five layers apply at once - stick
physically absent, LUKS container closed, `/home/nutzer` not a mount
point, account at `L`, no `nutzer` session. With the stick, `nutzer` logs
in automatically and the account is back at `P`. The encrypted swap runs
in both cases, because it depends on the random key, not on the stick.

Scripts/units:
`usr/local/sbin/dialos-rekey`, `usr/local/sbin/dialos-stick-gate.sh`,
`etc/systemd/system/dialos-stick-gate.service` (all in the repo under
`iso-build/config/includes.chroot/`, installation see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 12).

**Practical notes:**
- The stick should be kept separately from the laptop (e.g. on a
  keyring), otherwise the encryption provides little benefit if both are
  stolen together.
- **Recommended standard size: 64 GB.**
  `dialos-setup-home-partition.sh`/`dialos-rekey`
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

Paths 2 and 3 need the **encrypted key backup**: the setup script
(`dialos-setup-home-partition.sh`) and the rekey tool (`dialos-rekey`)
encrypt the small key file (not the whole disk) with a dedicated, randomly
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

## Credentials for services (mail, and more later)

Decided with Stephan on 2026-08-18. Trigger: DialOS reads and writes mail
directly over IMAP/SMTP, because Thunderbird cannot be controlled from
outside (see [anwendungen.en.md](anwendungen.en.md)). So DialOS needs the
mailbox password itself.

**Decided: a file in `/home/nutzer`, mode `0600`, owned by `nutzer`.** Not
the GNOME keyring, not the security stick.

The reason is the structure that already exists: `/home/nutzer` sits on the
LUKS partition that only opens if the stick was present at boot. **A file
there therefore has exactly the stick's protection** - no stick, no
decrypted home, no credentials. Without a single line of extra machinery.

**Why not the stick itself**, although it would be the obvious place:

- It carries the LUKS key. Further secrets there would mean that a lost
  stick takes mail access with it - and `dialos-rekey` only replaces the
  LUKS key, nothing else.
- It can be pulled out mid-session while the home stays mounted.
  Everything needing credentials after that would fail.
- It would be a second place to maintain doing the same job as the first.

**Why not the keyring** - here a recommendation previously voiced in this
project has been retracted:

- It sits in `/home/nutzer` itself, i.e. behind the same LUKS door. It adds
  a lock but **no new protection**: a process running as `nutzer` that
  could read the file can just as well ask the unlocked keyring.
- In exchange it adds a failure mode. `nutzer` is logged in **by
  autologin** (`AutomaticLogin=nutzer` in the GDM configuration), so there
  is no password for PAM to unlock the login keyring with. If it stays
  locked, a **password dialog the user cannot see** appears - and mail
  blocks silently. For this target group that is the worst conceivable
  outcome.
- **Not proven, and the decision does not depend on it:** the measurement
  was taken in `dialosadmin`, where the keyring is unlocked
  (`Locked = false` via the Secret Service interface) - but there a
  password is entered. For `nutzer` under autologin this could only be
  settled by logging in as `nutzer` and running the same query. Even an
  unlocked keyring would, per the point above, add no protection.

**What is deliberately accepted:** the password sits in plain text on the
disk. On a partition that only opens with the stick, in a file only
`nutzer` may read. The keyring would be in the same position - its store
lives there too, and whatever unlocks it must also come from somewhere.

## Shipping security

Laptop and security stick should be shipped separately (different
day/carrier), so that an intercepted package alone is useless.

## Logs: what DialOS records about the user

Four programs write logs - command service, dictation, information and notes.
That is indispensable for debugging and has more than once been the only way to
find a fault at all. But it also means: **what the user said is on the
device.** So this is the place to record what sits where, and who can see it.

| File | Content | Mode | Retention |
|---|---|---|---|
| `~/dialos-sprachbefehl.log` | recognized commands | 0644 (default umask) | grows, not rotated |
| `~/dialos-diktat.log` | **every dictated sentence verbatim** | 0644 | grows, not rotated |
| `~/dialos-auskunft.log` | questions and answers | 0644 | grows, not rotated |
| `~/dialos-notiz.log` | actions, **not** the entries | 0644 | grows, not rotated |
| `~/.local/share/dialos/support/befehle-YYYY-MM-DD.log` | commands + first line of a dictation | **0600** | **7 days**, self-clearing |

All of them live in `/home/nutzer` and therefore **inside the encrypted home
partition** - without the security stick none of them is readable. None leaves
the device: no DialOS program uploads a log anywhere.

**The support log is the file meant to be handed on** (Stephan's request of
2026-08-19) - on a support call it should be possible to read back what the
device actually heard. That is precisely why it is the only one that
**filters**:

- the commands in full,
- of the dictated text only the **first line**, truncated to 60 characters,
  after that just the count of further lines,
- plus the context as a heading (dictation, shopping list, question to the
  system, later mail and letter).

The reason for the boundary: `~/dialos-diktat.log` contains every dictated
sentence verbatim - the whole letter. A file meant for an outside helper must
not contain the user's mail. One line is enough to see **that** something was
captured and whether it made sense - and without the context even that would be
worthless: "Milch" on its own tells nobody anything, "Einkaufszettel: Milch"
tells the whole story.

Modes deliberately 0600 on the file and 0700 on the directory: it holds what the
user said, and that is not for other accounts on the same device. Seven days,
because a support case is settled within that time; the transcript deletes older
daily files on startup and at midnight by itself.

**Open:** the four program logs grow without limit and are not rotated - for the
dictation that is not merely a disk-space question but means every letter ever
dictated stays on disk in plain text permanently. Recorded in `TODO.md`.

## Remote support (RustDesk)

- Open source, self-hostable — fits the project's privacy stance.
- **Relay**: initially the public rustdesk.com service, later (once the
  system runs stably) a self-hosted server (hbbs/hbbr). The migration is
  a deliberately open point for later.
- **The ID is read out via TTS**, digit by digit in groups of four and twice
  over - a blind user can neither read it nor write it down. Spoken as a number
  it would be useless ("sixty-eight million...").
- **A one-time password is not obtainable with RustDesk 1.4.9** (five routes
  tested on 2026-08-19, all closed):
  - The one-time password RustDesk generates itself is in **no file** - memory
    and UI only, so nowhere for a blind user.
  - `rustdesk --password <value>` has no effect: as the user, with the app
    running, with the systemd service running **and as root**. Exit code 0, but
    the field stays empty.
  - `rustdesk --get-temp-password` does not return even after 40 s - it starts a
    full instance.
  - `rustdesk-utils`, which could compute the value, is not in the package.
  - Writing the value directly is out: RustDesk stores no plain hash there but a
    value encrypted with a local key (like `enc_id`, 70 characters). Recreating
    that would be guesswork and would break silently on the next version.

  This is not a fault of this project:
  [rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074) is titled
  "Permanent password not deployable without user interaction" and is open.
  **The supporter therefore sets the password once in the office via the UI** -
  it lives in their records, not in the customer's room.
- **Instead DialOS guarantees the limit through RUNTIME**, which is the harder
  lever: as long as RustDesk is not running, no connection is possible -
  regardless of who knows the password.
  - It never starts by itself, only on "Hilfe rufen".
  - "Fernwartung beenden" stops it.
  - If the user forgets, it ends **by itself after one hour, with an
    announcement** (Stephan, 2026-08-19). A warning comes three minutes before,
    and another "Hilfe rufen" extends it - so a supporter is not cut off
    mid-work.
- **The announcement says exactly that, instead of claiming something false:**
  "Das Passwort kennt Dein Betreuer schon. Die Fernwartung läuft nur, bis Du
  sagst: Fernwartung beenden." Telling a user who cannot see the screen a false
  sense of security ("the password is only valid for this session") would be
  worse than explaining the real one.
- **Open, and in `TODO.md`:** the timeout is **absolute**, not idle-based, even
  though idle would be the right semantics - the risk is a remote session left
  open with nobody attached. But nobody has ever connected to this device, so the
  signature of an active connection is unknown, and guessing it would be the
  worse error. `dialos-hilfe.py` therefore records process count and log size
  during every session; after the first real connection the idle detection can be
  built from **evidence**.
- **RustDesk phones home:** on startup it contacts `api.rustdesk.com` and the
  rendezvous service (shown in its log). That is the price of the public relay
  and one more reason for our own server later.
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
