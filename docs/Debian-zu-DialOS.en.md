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

> **Fast path (as of 2026-08-16): three commands from Debian to DialOS.**
> After the base install (step 1), everything except the ISO build is
> covered by scripts - there is no manual command left to type out of
> this document:
>
> ```bash
> # 1) Steps 2-12 + 15 - as dialosadmin, WITHOUT sudo:
> ./scripts/dialos-full-office-setup.sh
>
> # 2) Step 12b - plug in the security stick, again WITHOUT sudo
> #    (the script raises its own privileges via pkexec):
> /usr/local/sbin/dialos-setup-home-partition.sh
>
> # 3) Step 13 - leave the stick plugged in:
> sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
> ```
>
> Then reboot, then step 16 (build the ISO). The individual steps below
> remain the actual detailed reference - the scripts are built directly
> from them, and if a single step causes trouble, script 1 can be run for
> just that one step (`./scripts/dialos-full-office-setup.sh 08`). Step
> 14 (Bluetooth pairing data) only runs along with
> `--bluetooth-kopplung`, since it's device-specific. Steps 1 (base
> install) and 16 (build the ISO) deliberately remain manual - see there.
>
> **Two pitfalls when invoking these** (both found on 2026-08-16, before
> the first real run started):
> - Do **not** start script 1 with `sudo`. Steps 9 and 10 set up the user
>   account (GNOME extension, default applications); under `sudo`, `~`
>   would be `/root` and everything would silently land in the wrong
>   home. The script therefore refuses to start as root.
> - Do **not** start script 2 with `sudo` either. `sudo` strips
>   `DISPLAY`/`XAUTHORITY` (`env_reset`), so the script's Zenity dialogs
>   might not be able to open. Started without `sudo`, it elevates itself
>   via `pkexec` and keeps the graphical environment.

## 0. Prerequisites

- A Debian 13 ("Trixie") installation medium with the GNOME desktop from
  debian.org - the standard Debian installer is the only installer DialOS
  still uses (see step 5). Debian 13
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

**Timezone/language - decided on 2026-08-16:** the reference and build
device runs **`Europe/Vienna` + `de_AT.UTF-8`** (Stephan's location in
Tyrol), not `Europe/Berlin`. That is deliberate and stays that way.

Since the decision for path A (see step 5) this is straightforward:
every device is set up in the office via the Debian installer, so the
timezone is **chosen per device in step 1**. For a device destined for use
outside Austria, simply pick the appropriate timezone there - there is no
second path left that could inherit a different setting.

**Partitioning - automated since 2026-08-16 (path A).** So that you
neither have to partition by hand nor think about disk size, a preseed
file gives the Debian installer the layout:

| Partition | Size | |
|---|---|---|
| EFI | 538 MB | `/boot/efi` |
| root | **100 GiB**, ext4 | `/` |
| *rest* | **unpartitioned** | reserved for step 12 |

That free remainder is the whole point:
[`dialos-setup-home-partition.sh`](../iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh)
later creates the encrypted swap (8 GiB) and `dialos-nutzer-home` there -
the bigger the disk, the more space `nutzer` gets, without adjusting a
single number anywhere.

> **Why not just use the whole disk and shrink afterwards?** Because that
> is not possible: a **mounted** ext4 filesystem cannot be shrunk, online
> resize can only grow. So a script on the running system could not
> shrink the root partition at all - that would only work from a live
> session, costing an extra reboot per device and risking a destroyed
> system if the shrink is interrupted. Hence the correct layout is
> created during installation instead.

### 1a. Make the preseed file available

The file lives in the repo at
[`website/d-i/trixie/preseed.cfg`](../website/d-i/trixie/preseed.cfg).
The installer must be able to reach it over **plain HTTP**.

> **Why HTTP and not HTTPS:** the Debian docs list only `http://` and
> `tftp://` for `preseed/url`. HTTPS is nowhere guaranteed, nor is the
> behaviour on a 301 redirect. A server that forcibly redirects to HTTPS
> is therefore unsuitable - verified on 2026-08-16 against dialos.org,
> which does exactly that.

#### Route 1 (recommended): a second computer with the external drive

**Important to understand:** the target device is being wiped right now -
so it cannot serve the file itself. The web server runs on a **second
computer**. That is exactly why this repository lives on an external
drive: during the installation you simply plug it into any second
machine. That machine needs nothing but `python3` (present on every Linux
and macOS) and must be on the same network as the target device.

On that second machine, from the external drive:

```bash
./scripts/dialos-preseed-server.sh
```

That is all. The script

- checks that the preseed file exists and the port is free,
- determines its own IP address (listing alternatives if there are
  several network interfaces),
- prints the **ready-made line** to type in step 1b,
- and starts the web server.

The output looks like this:

```
  Im Debian-Installer diese Zeile an die Startzeile anhaengen
  (UEFI: Taste "e", ans Ende der Zeile mit "linux", dann Strg+X):

      preseed/url=http://192.168.178.45:8080/d-i/trixie/preseed.cfg
```

Stop the server with `Ctrl`+`C` once partitioning is done. If the port is
taken, the script says so and you pass another one
(`./scripts/dialos-preseed-server.sh 8081`).

This works regardless of where the external drive is mounted - the script
derives the repo path from its own location.

Advantages over every other hosting option: plain HTTP with no redirect,
no hosting provider, no internet needed - and the file comes straight
from the repo, so it cannot go stale.

#### Route 2 (optional): dialos.org

Only worthwhile if your web server delivers `/d-i/` **without**
redirecting to HTTPS. Upload the file there via FTP:

```
http://dialos.org/d-i/trixie/preseed.cfg
```

Two pitfalls, both encountered for real on 2026-08-16:

- **The FTP landing folder is usually not the web root.** With many
  hosts you end up one level above it. The `d-i` folder has to sit at the
  same level as `wp-content`, `wp-admin`, `wp-includes` and `index.php` -
  otherwise the server returns 404 even though the file is there.
- **dialos.org runs WordPress and forces HTTPS.** WordPress itself is
  harmless (nginx serves existing files before falling through to
  WordPress), but the forced HTTPS is not: it would have to be excluded
  for `/d-i/` in the server configuration.

**To check it is in place** - use `http://` explicitly, not a browser
(which silently substitutes `https://`):

```bash
curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" -L http://dialos.org/d-i/trixie/preseed.cfg
```

Expected: `200` **without** a switch to `https://` in the output.

> **State of dialos.org on 2026-08-16:** the file is in place and
> reachable (200, byte-identical to the repo), **but only via the
> redirect**: `http://` answers with `301` to `https://`. Whether the
> Debian installer follows that and supports TLS is open - it will only
> show at the next build. If the installer stalls while loading the
> preconfiguration file, that is the reason; fall back to route 1 (office
> machine) or partition by hand (1d). A permanent fix would require the
> host to exempt `/d-i/` from the forced HTTPS - the redirect comes from
> nginx itself, not from WordPress.
>
> Getting there was instructive: the FTP account does **not** land in the
> web root but one level above it. The right directory is recognisable by
> containing `license.txt`, `wp-login.php` and `wp-admin/`.

### 1b. Start the installer with it (for every device)

**An internet connection is required - cable OR WiFi.** The installer
configures the network *before* it fetches the preseed file (the Debian
docs are unambiguous here: "the network must be configured before the
preseed file can be fetched"). So both work:

- **Ethernet cable:** the simplest case, the installer sorts everything
  out via DHCP without asking you.
- **WiFi:** works just as well. At the network step the installer asks
  for the WiFi name and password, connects, and only then downloads the
  preseed file. The WiFi firmware for the ThinkPad is included in the
  official Debian 13 images.

Procedure:

1. Boot from the Debian 13 USB stick.
2. In the boot menu, do **not** press Enter - only **highlight** the
   `Graphical install` (or `Install`) entry.
3. Now edit the boot line:
   - **UEFI (the normal case, GRUB menu):** press **`e`**. A block of
     text appears. Use the arrow keys to reach the line starting with
     `linux` and press **End** to jump to its end.
   - **Older BIOS (isolinux menu):** press **`Tab`** instead. The boot
     line then appears directly for editing.
4. Append the address from step 1a at the end, with a space before it.
   For route 1 (office machine):

   ```
   preseed/url=http://192.168.1.50:8080/d-i/trixie/preseed.cfg
   ```

   (replace `192.168.1.50` with your own IP). For route 2:

   ```
   preseed/url=http://dialos.org/d-i/trixie/preseed.cfg
   ```

5. Boot:
   - **UEFI:** **`Ctrl`+`X`** (or `F10`).
   - **BIOS:** **`Enter`**.

> **Why there is deliberately no `auto` here.** The widespread short form
> `auto url=dialos.org` additionally enables automated mode. That
> postpones language and keyboard so *they* can be preseeded too - and
> lowers the question priority in the process. For DialOS that is not
> just unnecessary (we preseed partitioning only) but counterproductive:
> at a lower priority the WiFi prompts of all things could be skipped,
> and without a cable the installation would then stall. With the form
> above, all the usual questions stay visible.

### 1c. What happens next

The installation continues as usual - language, keyboard, network,
timezone and the **`dialosadmin`** account are still asked for normally.
The preseed file governs partitioning only.

One point deliberately stays your decision: **the installer still asks
which disk to partition.** That is intentional - it means the preset can
never hit the wrong disk, such as the installation stick itself or an
attached external drive.

> **After that there is no further prompt.** Once the disk is chosen it
> is wiped and repartitioned. So check beforehand that the internal disk
> is really the one selected (on ThinkPads usually `nvme0n1`, not `sda` -
> `sda` is typically the USB stick).

Account: the first account created (the installer requires one) must be
named **`dialosadmin`** - a convention, so scripts and docs don't need
per-device adjustment.

### 1d. Fallback: partition by hand

Without the preseed - e.g. if no network cable is at hand - choose
**"Manual"** instead of "Guided - use entire disk" in the installer and
create the same layout by hand: GPT partition table, EFI partition
(~512 MB is enough; the Debian installer likes to create around 1 GB on
its own - either is fine), root with **100 GiB** as ext4 on `/`, and
**leave the entire rest of the disk unpartitioned**. The installer may or
may not create a swap partition - step 12 replaces it with an encrypted
one anyway (see there). The script in step 12 requires at least 20 GiB of
free space.

**This is what it looked like on the reference device** (T490, 476.9 GiB
NVMe) during the first build - still partitioned by hand, measured on
2026-08-16:

| Partition | Size | Used for |
|---|---|---|
| `nvme0n1p1` | 100.00 GB (93.13 GiB) | `/`, ext4 |
| `nvme0n1p2` | 954 MB | `/boot/efi`, vfat |
| `nvme0n1p3` | 37.3 GiB | swap (replaced in step 12 by 8 GiB encrypted) |
| *(unpartitioned)* | **345.6 GiB** | became `dialos-nutzer-home` |

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
  `nodejs`/`npm` (for the Claude Code CLI, step 7), `dconf-cli`,
  `unzip` + `python3-pip` (both needed for step 15 - added on 2026-08-16
  because they were missing before: `pip3` is not present on a fresh
  Debian 13 install, so step 15 would have failed at the very end of the
  run).
- **Installer/security tools**: `zenity`, `polkitd`, `pkexec`,
  `parted`, `dosfstools`, `exfatprogs` (for the Windows-readable
  `DIALOS-DATA` partition on the security stick), `cryptsetup`,
  **`systemd-cryptsetup`** (added 2026-08-16: Debian 13 split crypttab
  handling out of the `systemd` package - without it there is neither the
  generator nor `systemd-cryptsetup@.service`, and `/etc/crypttab` has no
  effect at boot whatsoever; see step 12, encrypted swap),
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

**Boot background from `eggs produce` itself (GRUB/isolinux, live
ISO):** separately from the Plymouth theme above, `eggs produce` also
copies `/etc/penguins-eggs.d/brain.d/assets/splash.png` as the
background image into the GRUB and isolinux boot area of the finished
live ISO while building - that's the graphic that appears right at the
very start when booting from the ISO, before Plymouth even runs.
Without a custom file, the `eggs` package shows a default penguin photo
there:

```bash
sudo mkdir -p /etc/penguins-eggs.d/brain.d/assets
sudo cp iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/splash.png /etc/penguins-eggs.d/brain.d/assets/splash.png
```

Reuses the same already-compressed file as the Plymouth theme above
(~2 MB instead of the 14.7 MB raw version in `assets/`). **Not yet
verified via a real live boot** whether the resolution (2559×1440)
scales/centers cleanly in the isolinux context (traditionally a
640×480 VESA expectation) or appears stretched/cropped - check during
the next live-boot test, crop to 640×480 if needed.

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

At the very start (before `nutzer` even exists - that account is only
created in step 13), the admin account (`dialosadmin`) gets autologin for
testing purposes, so you can work on the system. Details and reasoning:
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md), section
"Automatic login".

## 5. Remove Calamares (dropped as of 2026-08-16)

**This step no longer sets anything up - it only cleans up.**

Until 2026-08-16 this step configured the Calamares installer: custom
DialOS branding, a fixed timezone, self-removal after installation, plus
a vendor overlay for Penguins' Eggs and a `base.yaml.tmpl` so that
`eggs produce` wouldn't overwrite the branding again. Calamares was the
installer for the **live-boot path**: the DialOS ISO was booted on the
customer's device, Calamares installed the system and then removed
itself.

**Stephan's decision (2026-08-16): that path is dropped.** Every customer
device is set up in the office - from the Debian 13 ISO off debian.org
plus the three DialOS scripts (see the fast path above). That means
nobody but Stephan ever sees an installer, and Calamares has no job left.

What this removes:

- `/etc/calamares/branding/dialos/`, `locale.conf`, `shellprocess.conf`
- the Penguins' Eggs vendor overlay under
  `/etc/penguins-eggs.d/brain.d/assets/calamares/`
- `base.yaml.tmpl` (existed only to rename the live installer icon)
- the open item "Calamares suggests the wrong location" - moot along
  with the tool itself

The decision was triggered by two defects that showed up during the
first real build on 2026-08-16: `calamares-settings-debian` ships
`/etc/xdg/autostart/calamares-desktop-icon.desktop`, which drops an
installer icon onto **every** user's desktop at login - including
`nutzer`, who must never see an installer - and it also added "Install
Debian" to the application overview.

The build script keeps the number 5 so that all cross-references to
later steps stay valid. It removes Calamares and its leftovers if
present:

```bash
./scripts/dialos-full-office-setup.sh 05
```

On a fresh Debian install the step finds nothing and does nothing -
Calamares is never installed in the first place on path A.

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
sudo npm install -g @anthropic-ai/claude-code
```

`sudo` is mandatory here (corrected 2026-08-16 - the command was
previously listed without it, which would not have worked on a fresh
system): Debian's npm prefix is `/usr/local`, which `dialosadmin` cannot
write to, so the command otherwise fails with `EACCES`.

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
  11): package `gnome-shell-extension-appindicator` (UUID
  `ubuntu-appindicators@ubuntu.com`) plus
  `gir1.2-ayatanaappindicator3-0.1` - now part of the package list
  (step 2), activation is covered by `01-dialos-defaults` (step 3).
- **Desktop Icons NG (DING)** (`gnome-shell-extension-desktop-icons-ng`,
  UUID `ding@rastersoft.com`): GNOME hasn't shown desktop icons out of
  the box for years - without this extension, the scripts from step 13
  would sit in the `~/Desktop/` folder but not be visible. Also part of
  the package list; activation plus the three settings
  `show-home`/`show-trash`/`show-volumes` set to `false` (only the
  actually placed files should be visible, no trash/home/volume icons)
  are covered by `01-dialos-defaults` (step 3). **Important gotcha:** an
  already-running GNOME Shell session only detects newly installed
  extensions after a real logout/login under Wayland (no live reload
  like the old X11 Alt+F2 trick) - log out and back in once after
  installing.

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

**Unlock location lookup for the weather (GeoClue2)** (since
2026-08-14, see TODO.md for the backstory) - otherwise
`AccessDenied: Geolocation disabled` when a location is requested:

```bash
printf '\n[dialos-start-ansage]\nallowed=true\nsystem=true\nusers=\n' | sudo tee -a /etc/geoclue/geoclue.conf > /dev/null
```

(Only append, don't overwrite - otherwise Debian's own default entries
for other apps get lost. `org.gnome.system.location enabled=true` is
already a dconf default in `01-dialos-defaults`, see step 3.)

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
  **Weather location via GeoClue2 since 2026-08-14, instead of a fixed
  or IP-guessed location** (the device is also used while traveling, so
  a fixed location wasn't an option) - automatically uses the best
  available source (WiFi lookup via Mozilla Location Service, otherwise
  an IP estimate as a fallback). Fixes less accurate than 10 km
  (typically a plain IP estimate with no WiFi match in Mozilla's
  database - observed live: ~25 km inaccuracy, off by about 300 km from
  the real position) are discarded and the weather announcement is
  skipped rather than naming the wrong city. This means: **in areas
  with sparse Mozilla WiFi-database coverage (e.g. rural/sparsely
  populated regions), the weather announcement may be skipped more
  often** than with the old, less accurate but always-"some answer"
  IP-guess approach - that's a deliberate trade-off (better to say
  nothing than something wrong).
  **Volume prompt since 2026-08-14** (only for `nutzer`, see TODO.md):
  the first real production use of Vosk (previously only the test
  script `dialos-vosk-test.py`) - asks "Wie laut soll ich sein? Sage
  100, 75, 50, 25 oder aus." (How loud should I be? Say 100, 75, 50, 25
  or off), records 4 seconds via `parec` (Bluetooth microphone
  preferred, including the `headset-head-unit` profile switch like in
  `dialos-vosk-test.py`), recognizes it with the small German Vosk
  model. The result drives speech-dispatcher's own volume (`spd-say
  -i`, -100 to +100) for the rest of the announcement - new
  `--lautstaerke` parameter in `dialos-say.py`. On "off", only the
  question itself (at normal volume) is spoken, the rest of the
  announcement is skipped entirely. **On any failure** (nothing/nothing
  matching understood, Vosk unavailable, no microphone), the function
  falls back to 100% - the announcement must never be skipped or hang
  because of this extra question. Right after the question, "Und jetzt
  bitte." (And now, please.) follows as a clear start signal for the
  recording - the first real test with Stephan's voice didn't have this
  signal yet, and the answer was missed (only the 100% fallback came
  through); tested successfully afterward with the signal added (a real
  "25" correctly recognized as 25%, via the Bluetooth microphone
  including the `headset-head-unit` profile switch).
- `dialos-tts-indicator.py`: a panel icon that shows when something is
  currently being spoken (needs the AppIndicator extension from step 9).

## 12. Security tools (encrypt nutzer's data + autologin gate)

**Design since 2026-08-14** (replaces the original whole-disk
encryption, see README changelog 0.5.0 and
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md), section
"Encrypting nutzer's data + security stick", for concept + rationale):
`dialos-install` now only encrypts a dedicated `dialos-nutzer-home`
partition (LUKS2, exclusively `/home/nutzer`), root stays unencrypted
(~100 GiB, ext4). No more `cryptsetup-initramfs`/`dialos-keyscript` -
the home partition isn't opened in the initramfs but by
`dialos-stick-gate.service` after boot.

```bash
sudo mkdir -p /usr/local/sbin
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-rekey /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/
sudo cp iso-build/config/includes.chroot/usr/local/sbin/dialos-setup-home-partition.sh /usr/local/sbin/
sudo chmod 755 /usr/local/sbin/dialos-rekey \
  /usr/local/sbin/dialos-stick-gate.sh /usr/local/sbin/dialos-setup-home-partition.sh
sudo mkdir -p /usr/share/applications
sudo cp iso-build/config/includes.chroot/usr/share/applications/dialos-rekey.desktop /usr/share/applications/
sudo cp iso-build/config/includes.chroot/etc/systemd/system/dialos-stick-gate.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dialos-stick-gate.service
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

`dialos-stick-gate.service` only takes effect from the **next** reboot
onward (only runs at boot, not retroactively on the currently running
session). Test after a real `dialos-install` install: unplug the
stick, reboot - the system must land on the normal GDM login screen
instead of autologging `nutzer`, and `/home/nutzer` must be
empty/unmounted; plug the stick back in, reboot again - `/home/nutzer`
must be mounted and autologin must work again.

**Setting up the home partition on a freshly installed system** (new
since 2026-08-14, for the path via the base install in step 1 instead
of via `dialos-install`'s whole-system copy):
`dialos-setup-home-partition.sh` uses the same LUKS/stick logic as
`dialos-install`, but without its disk-wipe/rsync copy - instead it
uses the space deliberately left free at the end of the system disk in
step 1:

```bash
/usr/local/sbin/dialos-setup-home-partition.sh
```

**Deliberately without `sudo`** (corrected 2026-08-16): the script raises
itself to root via `pkexec` and keeps the graphical environment while
doing so. Started with `sudo`, that branch never runs (you are already
root), and `sudo` simultaneously strips `DISPLAY`/`XAUTHORITY` via
`env_reset` - the Zenity dialogs might then fail to open. If it does have
to run from a non-graphical terminal, the script has asked for passwords
on the terminal instead since 2026-08-16, rather than (as before)
terminating silently at that point.

Asks for the security stick, a recovery passphrase (≥12 characters),
and confirmation (type "LOESCHEN"), then offers the same encrypted
Nextcloud key backup as `dialos-install`. At the end it mounts
`/home/nutzer` right away (no reboot needed), provided
`dialos-stick-gate.sh` is already installed (see above).

**Take care when picking the stick:** since 2026-08-16 the list shows a
"Bisheriger Inhalt" (current content) column with label + filesystem. The
selected stick is wiped completely - without that column, a plugged-in
Debian installation stick was indistinguishable from an empty one.

### Encrypting swap (part of the same script, since 2026-08-16)

Before touching the home partition, the script asks whether a plaintext
swap it found should be replaced with **8 GiB of encrypted swap** -
decision from 2026-08-16, rationale in step 1. It does the following:

- switches the old swap off (`swapoff`), deletes the partition, removes
  swap lines from `/etc/fstab` (backup:
  `/etc/fstab.dialos-vor-swap-umstellung`),
- creates 8 GiB at the **start** of the free area, so the rest of the disk
  stays one contiguous region for `dialos-nutzer-home`,
- writes an `/etc/crypttab` entry with **`/dev/urandom` as the key
  source** - the key is re-randomized on every boot, so there is nothing
  to keep safe and nothing for anyone to find,
- sets `vm.swappiness=10` (`/etc/sysctl.d/99-dialos-swappiness.conf`):
  swap is an emergency cushion, not a routine target - the less gets
  paged out, the less of `nutzer`'s data ever leaves RAM,
- sets `RESUME=none` + `update-initramfs -u`, so no half-configured
  hibernation setup is left behind.

**Found during the first real run (2026-08-16), now fixed:**
- **`systemd-cryptsetup` must be installed**, otherwise the whole crypttab
  entry has no effect. Debian 13 split the handling out of the `systemd`
  package; without it neither
  `/usr/lib/systemd/system-generators/systemd-cryptsetup-generator` nor
  `systemd-cryptsetup@.service` exists, and swap simply stays inactive at
  boot - **with no error message at all**. The package is now in the
  package list (step 2), and the script additionally checks for it before
  touching the partition table. The home partition is unaffected because
  `dialos-stick-gate.sh` opens it itself via `cryptsetup open` - which is
  why the omission only shows up for swap.
- The new swap partition is cleaned with `wipefs -a` after creation. It
  starts at the same offset as the old one, whose swap header would
  otherwise remain: `blkid` kept reporting `swap` with the **old** UUID on
  a partition that is about to be encrypted.
- The fstab line gets `nofail`. A missing swap is a comfort problem; a
  blocked boot on a device for blind users is a real one.
- Immediate activation goes directly through `cryptsetup open --type
  plain` + `mkswap` + `swapon`, not `systemctl start`: the crypttab unit
  does not exist before the next boot, so `systemctl start` does nothing
  and reports no useful error either.

**Important details behind the reasoning:**
- The crypttab entry deliberately points at `/dev/disk/by-partuuid/…`,
  not at a filesystem UUID: the `swap` option creates a fresh filesystem
  on every boot, so the filesystem UUID keeps changing.
- **Hibernation is thereby ruled out for good** - the image could no
  longer be decrypted after a reboot. No loss: hibernation was already
  impossible under this security design, because the image would contain
  `nutzer`'s decrypted data and would have to be readable at boot before
  anything else - exactly the discarded `cryptsetup-initramfs` approach.
  Suspend-to-RAM is **not** affected and keeps working.
- **Why have swap at all rather than dropping it:** without swap, the
  kernel kills processes outright when memory runs short (OOM killer). On
  a device for blind users that can hit the screen reader or the speech
  output - the user would then get no feedback at all, without warning,
  and could no longer operate the device. The 8 GiB are the cushion
  against that.
- **Why 8 GiB and not as much as RAM:** the "swap ≥ RAM" rule of thumb
  exists only because of hibernation. Without hibernation, anything above
  this is wasted space that `nutzer`'s data could use instead.

**Important for step 13:** `scripts/dialos-setup-nutzer.sh` only
creates `nutzer`'s account after checking (and, if needed, triggering
`dialos-stick-gate.sh` itself) that `/home/nutzer` is already mounted -
**`dialos-setup-home-partition.sh` must have run before step 13, and
the security stick must still be plugged in when running step 13**,
otherwise the script aborts cleanly (see sicherheit-datenschutz.en.md).

## 13. Create the customer account + finish office setup

A collector script that since 2026-08-16 handles **all four** sub-steps
in one go (see [`scripts/README.md`](../scripts/README.md)) - before
that, sub-steps 2a-2c below were manual work copied out of this document,
and thus the last gap keeping the build from consisting purely of
scripts:

```bash
sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
```

The security stick must **still be plugged in** at this point (see step
12). The script performs, in order:

1. `dialos-set-avatar.sh` - sets `distributor-logo.png` as the profile
   picture for the admin account (via `gdbus`/AccountsService
   `SetIconFile`).
2. **Admin tools onto `dialosadmin`'s desktop** (new in the script since
   2026-08-16):
   - a) the scripts from `scripts/` (`chmod 755`),
   - b) the Claude desktop app (`apt-get download claude-desktop`,
     `chmod 644`) - freshly downloaded during every office setup and
     deliberately not committed to the repo; if the package isn't in the
     sources, this sub-step is skipped rather than aborting the run,
   - c) a clickable launcher for `dialos-rekey` (replacement for a lost
     security stick), including `gio set … metadata::trusted true`.
3. `dialos-setup-nutzer.sh` - creates `nutzer` (`adduser
   --disabled-password`, groups
   `sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom`,
   random sudo password), switches autologin from `dialosadmin` to
   `nutzer` (with retry logic against a timing bug: "user is locked"
   right after `chpasswd`, because AccountsService hadn't yet noticed
   the new password entry).
4. Checks that the Firefox homepage policy from step 10 is set
   correctly.

> **Two pitfalls around the `nutzer` account, found during the first real
> run (2026-08-16), both fixed:**
>
> 1. **`adduser` does not touch an existing home.** On this build path
>    `/home/nutzer` normally already exists -
>    `dialos-setup-home-partition.sh` creates the encrypted partition and
>    mounts it *before* the account exists. `adduser` then reports "The
>    home directory already exists. Not touching this directory" and as a
>    result skips **both** the `chown` to the new user *and* copying
>    `/etc/skel`. The result was a home owned by `root:root` - `nutzer`
>    could not have written to their own directory, and GNOME could have
>    created neither `~/.config` nor `~/.cache`. On an account that starts
>    via autologin and whose user is blind, that is a total failure with
>    no way to self-recover. `dialos-setup-nutzer.sh` now handles this
>    afterwards (copy skel, `chown`, `chmod 700`) - copying only when the
>    home is empty apart from `lost+found`, so existing data is never
>    overwritten.
> 2. **The real system's `/etc/skel` was never populated.** Steps 9 and 10
>    previously copied the DialOS templates from the repo only into
>    `dialosadmin`'s home. `nutzer` would therefore have received neither
>    the Bluetooth battery extension, nor Thunderbird as the default mail
>    client, nor the Nautilus bookmarks - even though step 9 explicitly
>    names `/etc/skel` as the route "automatically for new accounts". Both
>    steps now additionally place the files under `/etc/skel/`.
>    **Important:** only user preferences belong there, never the admin
>    scripts (see the 2026-08-14 correction directly below).

**Why sub-step 2 looks the way it does** (important correction from
2026-08-14, still applies): all scripts in `scripts/` are **for
`dialosadmin` only** - `nutzer` should never see them. They are therefore
**not** distributed via `/etc/skel/Desktop/` but copied directly onto the
already-existing `dialosadmin` account: `/etc/skel/` only affects
accounts created *after* it's populated - in this recipe that's
exclusively `nutzer`, not a second admin account. An earlier attempt via
`/etc/skel/Desktop/` therefore ended up on `nutzer`'s desktop
unintentionally. The same reasoning applies to the Claude desktop `.deb`.

`gio set … metadata::trusted true` is mandatory - without it, Nautilus
shows an "untrusted" warning on the first double-click instead of
launching the program (unlike the `.sh` scripts on the same desktop,
which run via the executable-text-file setting, not the launcher trust
mechanism). The attribute lives in the respective **user's** metadata
store, so the script runs the command as `dialosadmin` via `runuser`,
not as root. If no session of that account is running, it says so and you
confirm "trust and launch" once on the first double-click.

The script deliberately takes the launcher template from
`/usr/share/applications/dialos-install.desktop` (placed there in step
12) rather than from the repo - that way it also works when started from
the desktop later, where no repo directory exists.

After this step: reboot, verify that `nutzer` starts automatically with
no login screen - and that `nutzer`'s own desktop is **empty** of admin
tools.

## 14. Bake in Bluetooth pairing data (optional, device-specific)

Only relevant if you stay on the **same** test device (the built-in
Bluetooth adapter has to stay the same, since the pairing data is tied
to its MAC address):

```bash
sudo cp -r "iso-build/config/includes.chroot/var/lib/bluetooth/." /var/lib/bluetooth/
```

Saves re-pairing the mouse/keyboard/speaker after a reinstall. On a
new/different device, pair normally instead.

## 15. Speech recognition (Vosk + hassil)

**Anchored as a repeatable recipe since 2026-08-14** (replaces the
previous TODO.md item "installed live only" - the original test run
actually got lost again during an interim reinstall of the T490,
exactly the trap TODO.md had warned about, see README changelog 0.5.0).

**System-wide installation** (not `--user`) - so `nutzer` can access it
later too, not just whichever account installed the packages. Debian 13
blocks `pip install` into system Python by default (PEP 668,
"externally-managed-environment") - `--break-system-packages` is
Debian's officially intended way around that, not a hack. Versions
pinned to match the original test run:

```bash
sudo pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0
```

`pip3` itself (`python3-pip`) and `unzip` for the models below come from
the package list in step 2 - neither is necessarily present on a fresh
Debian 13 install, and both were added there on 2026-08-16.

German Vosk models (large for accuracy, small for speed - see
`dialos-vosk-test.py`):

```bash
cd /tmp
curl -L -o vosk-de-big.zip https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
curl -L -o vosk-de-small.zip https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip vosk-de-big.zip
unzip vosk-de-small.zip
sudo mv vosk-model-de-0.21 /usr/local/share/vosk-model-de-big
sudo mv vosk-model-small-de-0.15 /usr/local/share/vosk-model-de-small
```

**Unzip pitfall:** the ZIPs already contain a named folder of their own
(`vosk-model-de-0.21/` resp. `vosk-model-small-de-0.15/`) - using
`unzip -d <target>` therefore creates a doubly-nested structure
(`<target>/vosk-model-de-0.21/...` instead of directly
`<target>/...`), under which `vosk.Model()` can't find the files.
Instead, unzip without `-d` into the current directory here and then
move the already-correctly-named folder to the target location (`mv`)
- that way `am/`, `conf/`, `graph/`, `ivector/` etc. end up directly in
`/usr/local/share/vosk-model-de-big` resp. `-small`, as
`dialos-vosk-test.py`
(`MODELL_PFAD_STANDARD = "/usr/local/share/vosk-model-de-small"`)
expects. This exact double-nesting is what happened during the
original test run on the T490 (done via `unzip ... -d <target>`) - it
only worked anyway by accident, because `unzip` also copies the files
flat into the target directory on a name collision; not clean (wastes
disk space, see TODO.md).

Install the test script:

```bash
sudo cp iso-build/config/includes.chroot/usr/local/bin/dialos-vosk-test.py /usr/local/bin/
sudo chmod 755 /usr/local/bin/dialos-vosk-test.py
```

Usage: `dialos-vosk-test.py [model path] [recording seconds]
[--bluetooth-erlauben]` - interactive (waits for [Enter], then records
real microphone audio via `parec`, recognizes it with Vosk, prints the
result in the terminal). Can't be automated - needs an actual person
speaking into the microphone.

Decision: **hassil instead of Rhasspy** for intent recognition (Rhasspy
was archived by its creator, no longer maintained) - details and
reasoning in [sprachsteuerung.en.md](sprachsteuerung.en.md).

Core result of the microphone comparison test: a Bluetooth headset
(e.g. AIRHUG) is clearly superior to the built-in laptop microphone -
the target design is a Bluetooth microphone as the primary path, with
the built-in microphone as a (not yet implemented) fallback. Details:
[offene-punkte.en.md](offene-punkte.en.md), section "Voice control".

## 16. Build the ISO (Penguins' Eggs)

Once all the previous steps are done, reboot the system once and
verify everything (autologin, splash, sound, Orca, Piper, apps). Then:

```bash
sudo eggs produce
# or, to carry over dialosadmin/nutzer including home directories:
sudo eggs produce --clone
```

**What the ISO is still for, as of 2026-08-16:** with the decision for
path A (see step 5), no device is installed from a DialOS ISO any more -
every one is built from the Debian ISO plus the three scripts. The ISO is
therefore a **backup snapshot** of the fully configured build device (see
[iso-builds.en.md](iso-builds.en.md)).

`--clone` carries over `dialosadmin` and `nutzer` including their home
directories; without it the ISO contains only a generic `live` user. For
a snapshot, `--clone` is therefore the sensible choice.

Output lands under `/home/eggs/<generated-name>.iso` by default -
rename it appropriately for clarity and move it to the external drive,
e.g. to `DialOS-ISOs/DialOS-Live-0.5.0.iso`.

**Attempted and abandoned (2026-08-14): pointing `--path` at the
external drive**, to keep the several-GB intermediate build material
off the internal disk entirely. Fails: `eggs`/`coa`'s
`bootloader-copy` step writes its files (including `isolinux.bin`)
hardcoded to `/home/eggs/isodir` regardless of `--path` - the rest of
the build correctly uses the `--path` target folder, so the finished
image ends up without a working bootloader (`xorriso` error: "Cannot
find in ISO image ... bin_path='/isolinux/isolinux.bin'"). A bug in
`eggs`/`coa` (version 48.x), not our configuration. Until this is
fixed upstream: don't use `--path`, always use the internal default
path `/home/eggs` and move the result manually afterward.

## Practical note: external drive

Since the build and test system are often the same machine, and an
installation overwrites the internal disk, it's a good idea to keep this
repository (and the built ISOs) on an external drive, so a reinstall of
the test device doesn't take them down with it.

**Second purpose since 2026-08-16:** the drive doubles as the preseed
source for every installation. The target device is being wiped and
cannot serve the file itself - so you plug the drive into any second
computer and run
[`scripts/dialos-preseed-server.sh`](../scripts/dialos-preseed-server.sh)
there (see step 1a). That second machine needs nothing but `python3` and
the same network. The script derives the repo path from its own location,
so it does not matter where the drive is mounted. After
every reinstall: reset the git identity
(`git config user.name`/`user.email`) and, if applicable, a symlink
like `~/DialOS` pointing at the external repo path.

## What's deliberately NOT covered here

This guide covers the path up to 0.5.0. Known open items (wake-word
engine, Bluetooth microphone fallback, spell-checking, the final sudo
policy for `nutzer`, among others) are listed in
[offene-punkte.en.md](offene-punkte.en.md); smaller, concrete follow-ups
are in [TODO.en.md](../TODO.en.md).
