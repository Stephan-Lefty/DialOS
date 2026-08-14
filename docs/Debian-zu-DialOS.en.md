[Deutsch](Debian-zu-DialOS.md) | [English](Debian-zu-DialOS.en.md)

# Build guide: From Debian 13 + GNOME 48 to DialOS 0.5.0

> **Maintenance note:** This document is the gap-free "rebuild from
> scratch" recipe, not just a historical retrospective. Any future
> change that affects how a device is built (a new package, a new
> branding/config file, a changed command, a bugfix in one of the
> scripts referenced here) must update this document **in addition to**
> the changelog in README.md - otherwise it drifts out of sync and
> can't be trusted for the next rebuild. Goal: by the final DialOS
> version, the system should be fully reproducible from this one file.

This guide brings together all the steps that, spread across many
separate chat sessions, led to the current state (0.5.0) - in the order
in which they actually make sense, so DialOS can be rebuilt from a
fresh Debian 13/GNOME install in a traceable, reproducible way. The
point is transparency: nothing here is newly invented, everything
points back to the file/commit/doc it comes from.

**Important context:** There are two parallel build paths in the repo
(see `CLAUDE.md`):
1. An older Docker/live-build pipeline (`iso-build/build.sh`) - after
   about 18 attempts it never produced a single finished ISO, and is
   not currently being pursued further.
2. **The path described here, currently in use:** Debian 13 + GNOME is
   installed directly on real hardware and set up interactively (no
   chroot, no Docker); the files under `iso-build/config/includes.chroot*/`
   in the repo serve as a **template/recipe, not automatic build
   input** - every file has to be manually copied onto the real system
   after a change. At the end, [Penguins' Eggs](https://penguins-eggs.net/)
   snapshots a bootable ISO from the fully set-up system
   (`eggs produce`).

This guide describes path 2. Reference test device: Lenovo ThinkPad
T490 (see [hardware.en.md](hardware.en.md)).

## 0. Prerequisites

- A Debian 13 ("Trixie") installation medium with the GNOME desktop
  (the standard Debian installer is enough - Calamares only comes into
  play later, as the installer for the *next* installation). Debian 13
  ships GNOME 48 (tested version: GNOME Shell 48.7, package version
  `48.7-0+deb13u2`, checked via `gnome-shell --version`) - no separate
  step needed, that's simply the version that comes with Trixie.
- Root/sudo access on the target system.
- An internet connection (for `apt`, `npm`, model downloads).
- This repository available locally (ideally on an external drive, see
  "Practical note: external drive" below).

## 1. Install Debian 13 + GNOME

Standard Debian installation, choose GNOME as the desktop. The first
account created (the installer requires one) should be named
**`DialOS-Admin`**, or in practice on this test device
**`dialosadmin`** - convention: the admin/setup account gets the same
name on every rollout, so scripts and docs don't need per-device
adjustment.

Timezone: `Europe`/`Berlin` as the default (see step 5 - Calamares
later picks this up automatically for customer installs).

## 2. Install the package list

The complete, current package list lives in
[`iso-build/config/package-lists/desktop.list.chroot`](../iso-build/config/package-lists/desktop.list.chroot).
Install with:

```bash
sudo apt-get update
sudo xargs -a iso-build/config/package-lists/desktop.list.chroot apt-get install -y
```

Notable groups within it (in the order they appear in the file):
- **Language/desktop base**: `task-german`, `task-german-desktop`,
  `gnome-core`, `gdm3`, `orca` (screen reader), `espeak-ng` (later
  replaced by Piper, see step 8), `plymouth` + `plymouth-themes`.
- **Network/firmware**: `network-manager` + GUI, firmware packages for
  the T490 (WLAN/microcode).
- **Applications**: Firefox, Thunderbird, Shortwave (radio), Rhythmbox,
  GNOME Podcasts, LibreOffice Writer.
- **Terminal/development**: `gnome-terminal`, `curl`, `wget`, `git`,
  `nodejs`/`npm` (for the Claude Code CLI, step 7), `dconf-cli`.
- **Installer/security tools**: `zenity`, `polkitd`, `pkexec`,
  `parted`, `dosfstools`, `cryptsetup` + `cryptsetup-initramfs`,
  `rsync`, `grub-efi-amd64` (+ `-bin`), `openssl`,
  `systemd-timesyncd` (NTP, important for the installer later),
  `thunderbird-l10n-de`, `gnome-shell-extension-manager`.

**Deliberately NOT used:** `task-gnome-desktop` (a tasksel metapackage)
- in an earlier attempt, its Recommends pulled in practically all ~70
languages Debian supports, including Japanese input methods, which
overrode the German GNOME default (see README.md, changelog around
0.4.0 / CLAUDE.md). After an accidental `task-gnome-desktop` install:
remove every `task-*` package except `task-desktop`,
`task-gnome-desktop`, `task-laptop`, `task-german`,
`task-german-desktop`, `task-english` via `apt-get purge`+`autoremove`,
explicitly purge `ibus-anthy`/`ibus-mozc`/`anthy` too, then run
`gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'de')]"`.

## 3. Apply branding

All branding assets are already prepared under [`assets/`](../assets/)
and in the ISO recipe. Target paths:

```bash
sudo mkdir -p /usr/share/backgrounds/dialos
sudo cp iso-build/config/includes.chroot/usr/share/backgrounds/dialos/*.png /usr/share/backgrounds/dialos/
sudo cp assets/mark.png /usr/share/pixmaps/distributor-logo.png   # 512x512, login logo + avatar template
sudo cp iso-build/config/includes.chroot/etc/os-release /etc/os-release
```

**dconf branding/defaults** (wallpaper, login logo, mouse acceleration,
battery percentage display, default extensions) - take the files from
[`iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/`](../iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/)
and activate them:

```bash
sudo mkdir -p /etc/dconf/db/local.d /etc/dconf/profile
sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/00-dialos-branding /etc/dconf/db/local.d/
sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/01-dialos-defaults /etc/dconf/db/local.d/
sudo cp iso-build/config/includes.chroot_before_packages/etc/dconf/profile/user /etc/dconf/profile/
sudo dconf update
```

**Plymouth boot splash:**

```bash
sudo mkdir -p /usr/share/plymouth/themes/dialos
sudo cp iso-build/config/includes.chroot_before_packages/usr/share/plymouth/themes/dialos/* /usr/share/plymouth/themes/dialos/
sudo plymouth-set-default-theme -R dialos
```

**Important gotcha:** `plymouth-set-default-theme -R dialos` alone
isn't enough - without the kernel boot argument `splash`, Plymouth
stays in text mode no matter which theme is active:

```bash
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/' /etc/default/grub
sudo update-grub
```

Can only be verified after a real reboot (splash between the firmware
logo and the login/desktop).

## 4. Set up autologin

**Key gotcha:** `/etc/gdm3/custom.conf` (`AutomaticLogin=nutzer`, see
[the file in the repo](../iso-build/config/includes.chroot/etc/gdm3/custom.conf))
is **not** the effective switch on this Debian 13/GDM 48 combination -
the actual mechanism is a per-user property in the running
AccountsService, set via D-Bus:

```bash
# Determine the target user's object path
sudo gdbus call --system --dest org.freedesktop.Accounts \
  --object-path /org/freedesktop/Accounts \
  --method org.freedesktop.Accounts.FindUserByName <username>
# returns e.g. /org/freedesktop/Accounts/User1001

# Enable autologin
sudo gdbus call --system --dest org.freedesktop.Accounts \
  --object-path /org/freedesktop/Accounts/User1001 \
  --method org.freedesktop.Accounts.User.SetAutomaticLogin true
```

At the very start (before `nutzer` even exists, see step 12), the admin
account (`dialosadmin`) gets autologin for testing purposes, so you can
work on the system. Details and reasoning:
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md), section
"Automatic login".

## 5. Set up the Calamares installer

Purpose: a dedicated graphical installer for **future** installations
(not for this running system) with DialOS branding and self-removal
after installation.

```bash
sudo apt-get install -y calamares calamares-settings-debian
```

German comes along automatically (Calamares embeds its core
translations as Qt resources and follows the system locale - no extra
work needed as long as the system runs in German).

Bring in the branding (`calamares-settings-debian` ships
`/etc/calamares/branding/debian/` as a template; the finished `dialos`
variant is already in the repo):

```bash
sudo cp -r iso-build/config/includes.chroot/etc/calamares/branding/dialos /etc/calamares/branding/
sudo cp iso-build/config/includes.chroot/etc/calamares/modules/locale.conf /etc/calamares/modules/
sudo cp iso-build/config/includes.chroot/etc/calamares/modules/shellprocess.conf /etc/calamares/modules/
sudo sed -i 's/^branding: debian/branding: dialos/' /etc/calamares/settings.conf
```

**Important gotchas along the way:**
- `componentName` in `branding.desc` must exactly match the folder name
  (`dialos`) - otherwise a fatal error at startup.
- `locale.conf` is missing entirely from the Debian package; without
  this file, Calamares' built-in default of `America/New_York` gets
  suggested as the location (not a GeoIP failure - GeoIP simply isn't
  configured at all). With the file: `region: Europe` / `zone: Berlin`
  fixed.
- `shellprocess.conf` does two things **only inside the chroot of the
  NEWLY installed target system** (`dontChroot: false`): sets
  left-handed mouse for the admin account, and removes Calamares again
  from the finished installation (`apt-get purge calamares
  calamares-settings-debian`) - this step must never run on the live
  template itself, or the next ISO would ship with no installer at all.
- `stylesheet.qss` (font color in the main area) didn't exist in the
  `debian` branding - it's new, and is picked up automatically as soon
  as it's present in the component folder.

**Penguins' Eggs vendor overlay** (important, otherwise
`eggs sysinstall` overwrites the branding again with a generic "eggs"
look during live boot):

```bash
sudo mkdir -p /etc/penguins-eggs.d/brain.d/assets/calamares
sudo cp -r iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/calamares/. /etc/penguins-eggs.d/brain.d/assets/calamares/
```

Here `componentName` in the copy is deliberately `eggs` instead of
`dialos` (the target folder that `eggs sysinstall` expects is always
called `eggs`).

**Rename the live installer icon** ("Install DialOS" instead of
"Install System"/egg icon) - `eggs produce` re-renders
`/usr/share/applications/install-system.desktop` from its own template
on **every** build, so simply overwriting the file isn't enough:

```bash
sudo cp iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/base.yaml.tmpl /etc/penguins-eggs.d/brain.d/base.yaml.tmpl
```

## 6. Install RustDesk (and disable it)

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

**Important:** the `.deb` postinst automatically enables a systemd
autostart - this contradicts the security policy (RustDesk must not run
permanently, see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md),
section "Remote support"). Fix it:

```bash
sudo systemctl disable --now rustdesk
```

## 7. Install the Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

(The `EBADENGINE` warning about the Node version can be ignored, it
works anyway.) For the desktop app: no fixed install step - the `.deb`
is instead freshly downloaded during every office setup and placed on
the desktop of every new account (see step 12).

## 8. Piper instead of espeak-ng (more natural voice output)

System-wide installation (not per user), so new customer accounts get
it automatically too:

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

Bring in the config from the repo:

```bash
sudo mkdir -p /etc/speech-dispatcher/modules
sudo cp iso-build/config/includes.chroot/etc/speech-dispatcher/modules/piper-generic.conf /etc/speech-dispatcher/modules/
sudo cp iso-build/config/includes.chroot/etc/speech-dispatcher/speechd.conf /etc/speech-dispatcher/speechd.conf
```

`DefaultVoice de_DE-thorsten-high`, `GenericRateMultiply 0.85`
(speaking rate, Stephan's personal preference - see TODO.md, should
become user-adjustable later). After config changes, kill any running
`speech-dispatcher` processes so they restart with the current config:
`pkill -f speech-dispatcher`.

## 9. GNOME extensions

- **Bluetooth Battery Monitor** (battery-level display for Bluetooth
  devices in the top bar): the files are ready under
  [`iso-build/config/includes.chroot/etc/skel/.local/share/gnome-shell/extensions/bluetooth-battery-monitor@v8v88v8v88.com/`](../iso-build/config/includes.chroot/etc/skel/.local/share/gnome-shell/extensions/bluetooth-battery-monitor@v8v88v8v88.com/) -
  copy to `~/.local/share/gnome-shell/extensions/` (or automatically
  via `/etc/skel/` for new accounts); activation is already covered by
  `01-dialos-defaults` (step 3).
- **AppIndicator support** (for the voice-output-active indicator, step
  11): install the package `gnome-shell-extension-appindicator` (UUID
  `ubuntu-appindicators@ubuntu.com`) plus
  `gir1.2-ayatanaappindicator3-0.1`, and enable the extension in GNOME
  Settings/the Extensions app. **Not yet anchored in the package list**
  (see TODO.md) - add it manually until then.

## 10. Set default applications

Thunderbird instead of Evolution/GNOME Calendar, without removing the
packages tightly coupled to `gnome`/`gnome-core` (that would pull
almost the whole desktop along with it):

```bash
sudo mkdir -p /usr/local/share/applications
sudo cp iso-build/config/includes.chroot/usr/local/share/applications/org.gnome.Evolution.desktop /usr/local/share/applications/
sudo cp iso-build/config/includes.chroot/usr/local/share/applications/org.gnome.Calendar.desktop /usr/local/share/applications/
mkdir -p ~/.config
cp iso-build/config/includes.chroot/etc/skel/.config/mimeapps.list ~/.config/mimeapps.list
xdg-mime default thunderbird.desktop x-scheme-handler/mailto text/calendar
```

(`/usr/local/share/applications/*.desktop` files with `NoDisplay=true`
override the default entries without `apt`/`dpkg` ever touching them -
survives future Debian updates.)

Firefox homepage via enterprise policy:

```bash
sudo mkdir -p /usr/lib/firefox-esr/distribution
sudo cp iso-build/config/includes.chroot/usr/lib/firefox-esr/distribution/policies.json /usr/lib/firefox-esr/distribution/
```

Nautilus bookmark to `/usr/local/bin`:

```bash
cp iso-build/config/includes.chroot/etc/skel/.config/gtk-3.0/bookmarks ~/.config/gtk-3.0/bookmarks
```

## 11. Voice-output scripts

Three scripts that work together, all under
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

- `dialos-say.py`: a reusable voice-output script with audio ducking
  (mutes other audio sources for the duration of the announcement).
- `dialos-start-ansage.py` ("Michael"): runs at every login, greets the
  user, states date/time, battery levels (filtered by account -
  `nutzer` only gets laptop+speaker, every other account also gets
  mouse/keyboard), the weather, and reconnects Bluetooth devices. Keeps
  running in the background afterward (network monitoring every 90s).
  Includes a single-instance lock (prevents duplicate instances of the
  same account) and a Bluetooth debug log - see
  [offene-punkte.en.md](offene-punkte.en.md), entry "Bluetooth speaker
  ... sometimes inaudible after login" for the background. **Important
  practical rule here:** always switch accounts via a proper logout,
  never via GNOME "switch user" (see
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)).
- `dialos-tts-indicator.py`: a panel icon that shows when something is
  currently being spoken (needs the AppIndicator extension from step 9).

## 12. Security tools (stick encryption)

```bash
sudo mkdir -p /usr/local/sbin
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-install /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-rekey /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-keyscript /usr/local/sbin/
sudo chmod 755 /usr/local/sbin/dialos-install /usr/local/sbin/dialos-rekey /usr/local/sbin/dialos-keyscript
sudo mkdir -p /etc/initramfs-tools/hooks
sudo cp iso-build/config/includes.chroot/etc/initramfs-tools/hooks/dialos-keyscript /etc/initramfs-tools/hooks/
sudo chmod 755 /etc/initramfs-tools/hooks/dialos-keyscript
sudo mkdir -p /usr/share/applications
sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-install.desktop /usr/share/applications/
sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-rekey.desktop /usr/share/applications/
```

What these tools do: see
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md) (concept)
and the detailed walkthrough further up in this repo (README changelog
0.5.0) for the current state (separate backup password, minimum
length, `DIALOS-KEY`+`DIALOS-DATA` stick partitioning). **Important
permissions gotcha:** files newly written via a device bridge/editor
often end up with `600` permissions - `chmod +x` alone then results in
`711` (no read permission for other accounts), and the script is then
"not found" for other accounts. Always use `chmod 755` for scripts,
`chmod 644` for plain files like `.desktop`/`.deb`.

## 13. Create the customer account + finish office setup

A collector script that handles three individual steps in one go (see
[`scripts/README.md`](../scripts/README.md)):

```bash
sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
```

That calls, in order:
1. `dialos-set-avatar.sh` - sets `distributor-logo.png` as the profile
   picture for the admin account (via `gdbus`/AccountsService
   `SetIconFile`).
2. `dialos-setup-nutzer.sh` - creates `nutzer` (`adduser
   --disabled-password`, groups
   `sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom`,
   random sudo password), switches autologin from `dialosadmin` to
   `nutzer` (with retry logic against a timing bug: "user is locked"
   right after `chpasswd`, because AccountsService hadn't yet noticed
   the new password entry).
3. Checks that the Firefox homepage policy from step 10 is set
   correctly.

Provide the Claude desktop app for the new account (freshly downloaded
during every office setup, not committed to the repo):

```bash
cd /tmp && apt-get download claude-desktop
sudo cp /tmp/claude-desktop*.deb /etc/skel/Desktop/
sudo chmod 644 /etc/skel/Desktop/claude-desktop*.deb
sudo chown root:root /etc/skel/Desktop/claude-desktop*.deb
```

After this step: reboot and verify that `nutzer` starts automatically
with no login screen.

## 14. Bake in Bluetooth pairing data (optional, device-specific)

Only relevant if you stay on the **same** test device (the built-in
Bluetooth adapter has to stay the same, since the pairing data is tied
to its MAC address):

```bash
sudo cp -r "iso-build/config/includes.chroot/var/lib/bluetooth/." /var/lib/bluetooth/
```

Saves re-pairing the mouse/keyboard/speaker after a reinstall. On a
new/different device, pair normally instead.

## 15. Speech recognition (Vosk + hassil) - status: installed live only

**Note: not yet anchored as a repeatable recipe in the repo** (see
TODO.md) - here are the steps as they were carried out live on the
T490, for reference/reproduction:

```bash
pip install --user vosk hassil
sudo mkdir -p /usr/local/share/vosk-model-de-big /usr/local/share/vosk-model-de-small
curl -L -o /tmp/vosk-de-big.zip https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
curl -L -o /tmp/vosk-de-small.zip https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
sudo unzip /tmp/vosk-de-big.zip -d /usr/local/share/vosk-model-de-big
sudo unzip /tmp/vosk-de-small.zip -d /usr/local/share/vosk-model-de-small
```

Decision: **hassil instead of Rhasspy** for intent recognition (Rhasspy
was archived by its creator, no longer maintained) - details and
reasoning in [sprachsteuerung.en.md](sprachsteuerung.en.md).

The technical test script `dialos-vosk-test.py` so far only lives under
`/usr/local/bin/` on the test device, not yet in the repo. Core result
of the microphone comparison test: a Bluetooth headset (e.g. AIRHUG) is
clearly superior to the built-in laptop microphone - the target design
is a Bluetooth microphone as the primary path, with the built-in
microphone as a (not yet implemented) fallback. Details:
[offene-punkte.en.md](offene-punkte.en.md), section "Voice control".

## 16. Build the ISO (Penguins' Eggs)

Once all the previous steps are done, reboot the system once and
verify everything (autologin, splash, sound, Orca, Piper, apps). Then:

```bash
sudo eggs produce            # generic image, live user "live"
# or, to carry over dialosadmin/nutzer including home directories:
sudo eggs produce --clone
```

`--clone` is required if the built ISO is later going to be tested with
`dialos-install` (that tool only copies what's actually running in the
live system when installing - without `--clone` there would be no
`dialosadmin`/`nutzer` there, only a generic `live` user). Without
`--clone`, the ISO is suited to the classic path: live boot →
Calamares installation → set up accounts manually via step 13.

Output lands under `/home/eggs/<generated-name>.iso` by default -
rename it appropriately for clarity, e.g.
`DialOS-Live-0.5.0.iso` / `DialOS-Live-0.5.0-clone.iso`.

## Practical note: external drive

Since the build and test system are often the same machine, and a
live-boot install test overwrites the internal disk, it's a good idea
to keep this repository (and the built ISOs) on an external drive, so
a reinstall of the test device doesn't take them down with it. After
every reinstall: reset the git identity
(`git config user.name`/`user.email`) and, if applicable, a symlink
like `~/DialOS` pointing at the external repo path.

## What's deliberately NOT covered here

This guide covers the path up to 0.5.0. Known open items (wake-word
engine, Bluetooth microphone fallback, spell-checking, the final sudo
policy for `nutzer`, among others) are listed in
[offene-punkte.en.md](offene-punkte.en.md); smaller, concrete follow-ups
are in [TODO.en.md](../TODO.en.md).
