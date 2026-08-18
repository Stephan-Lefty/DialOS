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
   A backup image is taken from the finished system at the end (step
   16) - since 2026-08-16 using [Rescuezilla](https://rescuezilla.com/),
   the graphical front-end for Clonezilla. Penguins' Eggs is gone.

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

> **Dropped on 2026-08-16:** until then a second graphic lived here
> (`/etc/penguins-eggs.d/brain.d/assets/splash.png`) for the
> GRUB/isolinux boot area of the live ISO built by Penguins' Eggs. With
> eggs gone (step 16) it has no effect - the Plymouth theme above brings
> its own `background.png`.

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
  **Pronunciation rule since 2026-08-16:** every text passes through
  `fuer_sprachausgabe()` before being spoken, which splits "DialOS" into
  "Dial OS" - otherwise Piper reads it as one word. Deliberately central
  in this one place rather than in each announcement text: no future
  announcement can forget the split, and the texts stay correctly spelled
  in the source. Further pronunciation rules belong there too. Not
  matched: `dialosadmin` (no word end after "dialos") and `dialos.org`
  (the dot is excluded).
  **Announcement cache since 2026-08-17:** generating and playing a
  sentence cost a good 2.2 seconds, about 1.1 seconds of which was pure
  overhead - recomputed every time for sentences like "Ich höre." that
  never change. Spoken sentences are therefore stored as WAV under
  `~/.cache/dialos/ansagen` and played from there next time (measured:
  2172 ms → about 1200 ms, and 1.13 s of that is the announcement
  itself). The cache fills itself: the first time takes the normal
  route, the recording happens alongside in the background. So there is
  no list to maintain. **The key is a hash of the text plus the
  modification times of `PIPER_CONF` and the voices directory** - if the
  tempo or the voice changes, new keys arise and the old stock is no
  longer found; without that, DialOS would speak partly at the old and
  partly at the new tempo after a tempo change. The cache may be deleted
  at any time, it rebuilds itself.
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
  or off), records 4 seconds via `parec` (since
  2026-08-17 via the echo-cancelled source on the **built-in**
  microphone, rather than over Bluetooth with a `headset-head-unit`
  profile switch as before - see step 11f), recognizes it with the small German Vosk
  model. The result drives speech-dispatcher's own volume (`spd-say
  -i`, -100 to +100) for the rest of the announcement - new
  `--lautstaerke` parameter in `dialos-say.py`. On "off", only the
  question itself (at normal volume) is spoken, the rest of the
  announcement is skipped entirely.

  **Changed on 2026-08-16 (Stephan's requirement): ask once, then
  remember - and do it AFTER the announcement.** Until then the question
  came at every login and before the announcement. Both were awkward:
  someone who hears "how loud should I be?" as the very first thing has no
  reference for how loud the system actually is - a meaningless yardstick
  for a blind user. It now works like this:

  - **First login:** announcement at normal volume, then the question. The
    answer is remembered in `~/.config/dialos/lautstaerke` - for `nutzer`
    that means on the encrypted partition, as protected as the rest of
    their data. Then a confirmation **at the newly chosen volume**, so it
    is immediately audible what was settled on.
  - **Every later login:** the remembered value is used, no question.
  - **To be asked again:** delete the file
    (`rm ~/.config/dialos/lautstaerke`).

  > **"off" is deliberately NOT stored permanently** and applies only to
  > the current login. If it were permanent, no announcement would come -
  > and therefore never this question again. A blind user would have no
  > way back without outside help. A real permanent off switch needs a
  > different route back first (a voice command), see TODO.md.

  **On any failure** (nothing/nothing matching understood, Vosk
  unavailable, no microphone) the function returns `None` and **nothing**
  is stored - so the question comes again at the next login, and 100%
  applies until then. Deliberately distinguished from "the user said 100":
  only a real answer is written down. The announcement must never be
  skipped or hang because of this extra question. Right after the question, "Und jetzt
  bitte." (And now, please.) follows as a clear start signal for the
  recording - the first real test with Stephan's voice didn't have this
  signal yet, and the answer was missed (only the 100% fallback came
  through); tested successfully afterward with the signal added (a real
  "25" correctly recognized as 25%, via the Bluetooth microphone
  including the `headset-head-unit` profile switch).
- `dialos-tts-indicator.py`: a panel icon that shows when something is
  currently being spoken (needs the AppIndicator extension from step 9).
- `dialos-desktop-stil.sh`: switches the desktop's look between the GNOME
  standard and a Windows 11 imitation (see below).

### 11a. Questions sound different from hints (new 2026-08-17)

For someone who cannot see the screen, "is it waiting for me right now?"
is the decisive information. On 2026-08-16 the first test of the volume
prompt failed on exactly that: the system asked, but Stephan didn't know
when to answer - the answer was lost.

`dialos-say.py` therefore has the switch **`--frage`** (question):

```bash
dialos-say.py --frage "War das angenehm laut?"
```

**The default is the natural sentence melody.** Piper is trained on text
with punctuation and produces a rising melody from the question mark by
itself - compared on 2026-08-17 against a higher pitch and against a
signal tone, and chosen by Stephan as the best variant. It sounds natural
and does not wear out.

**The signal tone is the option.** Enabled via
`~/.config/dialos/frageton` containing `an`; the file played is
`/usr/local/share/dialos/frage-ton.wav`. The reason to offer it at all: a
rising melody at the end is only noticed by someone who was listening -
anyone who missed the beginning, or has the radio on, needs a signal
independent of that. Hence a setting rather than a decision.

**Why a switch in the code rather than "detect the question mark":** a
question mark can appear in the middle of a hint, and a rhetorical
question wants no signal. The code building the announcement *knows*
whether it wants to know something - that information should be passed
on, not guessed from punctuation. Verified on 2026-08-17: with the option
enabled, a question marked with `--frage` gets the tone, an ordinary hint
does not.

So far the only use: the volume question in the login announcement.

### 11b. Optional Windows 11 look (new 2026-08-16)

**Why this exists:** there are people who want DialOS for the voice
control but have used Windows all their lives. For them the desktop
should look familiar - without DialOS giving up the accessible GNOME
foundation (Orca, AT-SPI). So nothing is replaced: GNOME stays, gets
three extensions on top, and can be switched back at any time in either
direction.

The three extensions come from Debian's own repositories (no third-party
repository, so they keep being maintained through system updates) and
have been in the step 2 package list since 2026-08-16:

| Package | UUID | Job |
|---|---|---|
| `gnome-shell-extension-dash-to-panel` | `dash-to-panel@jderose9.github.com` | taskbar at the bottom |
| `gnome-shell-extension-arc-menu` | `arcmenu@arcmenu.com` | start menu (layout `Eleven` = the Windows 11 imitation) |
| `gnome-shell-extension-tiling-assistant` | `tiling-assistant@leleat-on-github` | window snapping like Windows Snap |

They are **installed but not enabled**. Only the script activates them.
Reason: anyone who had to install the switch on demand would need
internet access and an admin password - neither can be assumed at the
customer's home.

Invocation, **deliberately without `sudo`** (all settings belong to the
user account - under `sudo` they would land in `/root` and have no effect
for the user):

```bash
/usr/local/bin/dialos-desktop-stil.sh windows   # Windows 11 look
/usr/local/bin/dialos-desktop-stil.sh gnome     # back to the standard
/usr/local/bin/dialos-desktop-stil.sh status    # what is currently active
```

What changes: taskbar at the bottom with centered icons (48 px), ArcMenu
layout `Eleven` on the left of the bar, **window buttons on the right in
the order minimize/maximize/close** (GNOME ships with only a close button
there - the most noticeable change day to day), the top-left hot corner
off (people used to Windows trigger it constantly by accident) and the
date next to the clock. `tiling-assistant` needs no settings; out of the
box it behaves like Windows Snap.

Switching back resets every touched key to its **shipped default** via
`gsettings reset`, not to hand-picked "GNOME-ish" values - otherwise
switching back and forth repeatedly would not be lossless.

**The icon on the start button** is our own bundled window symbol
(`/usr/local/share/dialos/dialos-fenster-symbolic.svg`, four tiles in a
square, no frame) - **deliberately not Microsoft's Windows logo.**
DialOS is sold; someone else's trademark on the start button of a sold
device would be a trademark problem. Microsoft's mark is a tilted group
of four without a frame in a specific blue; this is the general symbol
for "a window" and is still read immediately as a start button by people
used to Windows. ArcMenu itself ships no Windows symbol and notes
explicitly in its source that its distribution icons are trademarks of
their respective owners.

**Careful when editing:** the file must start with `<svg` **immediately**
after the XML declaration, with no comment before it - otherwise the
button shows a solid white area, with no error message whatsoever. GNOME
rewrites symbolic icons while recoloring them and trips over anything
preceding the `<svg>` tag. That is why the explanation for the file lives
in `iso-build/config/includes.chroot/usr/local/share/dialos/README.md`
and not inside the file. Always model new symbols on an Adwaita file; a
self-rendered preview proves nothing, because librsvg draws the file
exactly as written.

The file ends in `-symbolic.svg` and is monochrome so GNOME Shell
recolors it like a symbolic icon: it takes on the panel's foreground
color and stays legible in both the light and the dark appearance. A
fixed-color icon would be invisible in one of the two - for visually
impaired users the difference between usable and unusable. If the file is
missing, the button keeps its previous symbol; a start button with no
image would be worse than one with the wrong image.

**Two stumbling blocks, both of which only surfaced during the real
test run on 2026-08-16:**

- **The running GNOME Shell does not know freshly installed
  extensions.** It scans `/usr/share/gnome-shell/extensions` only at
  startup. Right after `apt install` the files are on disk, but
  `gnome-extensions enable` answers "extension does not exist" - and
  under Wayland the shell cannot be restarted while running. The script
  therefore **always additionally writes the UUIDs straight into
  `org.gnome.shell enabled-extensions`** (via Gio, not by string-editing
  the `gsettings` output); the shell then enables them at its next
  start. When it detects this case it says so explicitly: "It will only
  appear once you log out and back in." Without that sentence a blind
  user would face a command that apparently does nothing.
- **Debian's `gnome-shell-extension-arc-menu` (65-2) installs its schema
  into the wrong directory:** `/usr/share/glib-2/schemas/` instead of
  `/usr/share/glib-2.0/schemas/`. As a result it never reaches the
  system-wide schema cache and `gsettings` answers "No such schema" -
  all three ArcMenu settings were silently skipped on the first test run
  (the start menu would have appeared in the GNOME default layout
  instead of the Windows 11 one). The extension itself still works,
  because GNOME Shell reads the bundled `gschemas.compiled` from the
  extension's own directory. That is where the script now looks too
  (`GSETTINGS_SCHEMA_DIR`), deliberately searching all three extension
  directories: if Debian fixes the typo, the system-wide path applies
  again automatically.

Three further details that mattered while building this:

- **No blind `gsettings set`.** For every key the script first checks
  whether the schema knows it. A failure mid-switch would otherwise leave
  a half-converted desktop behind - not something a blind user can repair
  themselves.
- **The centered taskbar applies to the primary monitor only.**
  dash-to-panel stores this setting per monitor and has used the monitor
  serial as the key since version 56, but explicitly falls back to the
  monitor index (`panelSettings.js`, `getMonitorSetting`) - so the script
  writes to `"0"`. A second monitor keeps the default arrangement; that is
  deliberate, rather than reimplementing monitor detection for a cosmetic
  detail.
- **The feedback is spoken**, not just printed (`dialos-say.py`). The
  target group cannot see the screen - a printed-only message would be the
  same as none for them. That is also exactly why this script is the
  intended **first real voice command** once the command grammar exists
  (see TODO.en.md).

### 11c. Voice command for the switch (new 2026-08-16)

`dialos-sprachbefehl-desktop.py` is the **first continuously listening
service in DialOS** - until then Vosk was only invoked at specific
moments (the volume question in the login announcement). It listens on
the microphone and switches on command:

> "auf Linux umschalten" &nbsp;·&nbsp; "auf Windows umschalten"
> (German for "switch to Linux/Windows")

"auf Gnome umschalten" counts the same as Linux. It is started from
`/etc/xdg/autostart/dialos-sprachbefehl-desktop.desktop` in every
session.

**The command is deliberately a whole sentence, not a single word**
(Stephan's requirement). A lone "Windows" comes up in conversation all
the time; the desktop would change unasked, and a blind user would not
know why everything suddenly sounds different. So the recognized
sentence must contain **both**: the target *and* the word "umschalten"
(switch).

Five decisions made while building it - all measured on 2026-08-16 with
synthetically spoken sentences (Piper speaks, Vosk listens):

| Decision | Reason |
|---|---|
| **Restricted grammar** instead of free recognition | A requirement, not an optimization: free recognition turned "gnome" reliably into **"genug"** (German for "enough"). With the grammar all three sentences came out verbatim. It also costs far less CPU - which matters for battery life in a permanently running service. |
| **Built-in microphone** instead of Bluetooth | The AIRHUG cannot do A2DP and HFP at once. For the one-off volume question, phone-grade audio is a brief moment - with continuous listening, playback would be degraded **permanently**. Distinguishing three fixed sentences works with the built-in microphone too. |
| **No listening while the system speaks** | Otherwise the service hears itself. Its own announcement can contain both the target *and* "umschalten" - so the sentence condition would specifically fail to catch it. It watches the marker file `dialos-say.py` sets anyway. |
| **No confirmation prompt, but an announcement** | A "are you sure?" on every command would be tiresome. Instead the system says what it did - anyone who didn't want it just says the other sentence. A misfire is undoable in seconds, without having to look. |
| **No lockout** | It was 5 s at first, then 2 s, now none - see below. Double triggering is prevented by restarting the recording. |

The control test that justifies the sentence condition: the spoken
sentence "ich habe früher windows benutzt" ("I used to use Windows") was
recognized as `auf auf windows` - containing the word "windows", but
**without** "umschalten". It triggered nothing.

**Since 2026-08-17 the lockout is gone entirely** - in two steps, and the
first was only a half fix. At first it also applied after the
announcements "Ich hoere." and "Ich hoere nicht mehr.", then only after a
real switch with 2 s, now not at all. The reason for the second step:
after a switch the service was deaf for about **five seconds** - 2.4 s the
switch script runs and speaks, 2.0 s lockout, 0.7 s reverberation pause.
But the announcement ends after 1.5 s, so the user speaks into a deaf
system for 3.6 seconds. It was not needed anyway: discarding and
restarting the recording after every utterance prevents double triggering
completely.

**The old text on it, because the diagnosis is instructive:**
Before that it also sat behind the announcements "Ich höre." and "Ich
höre nicht mehr." - which left the service deaf for exactly the five
seconds after "Ich höre.", precisely when the user speaks their command.
To Stephan it looked like a volume problem ("I have to speak very
loudly"): he spoke, nothing happened, he repeated it louder - and by
then the lockout had expired. It only came to light through his
clarification that the *second* command was the problem, not the first.
Against the system's own voice, discarding and restarting the recording
after every utterance already protects.

**The announcements after a switch** are "Linux Desktop." and "Windows
Desktop." (1.5 s). They started out as an explanatory sentence about the
taskbar and start menu - some eight seconds during which the service
deliberately does not listen, so eight seconds of waiting before the next
command. The way back via a bare "Windows." was then too short: a
keyword, not a sentence - someone who only listens cannot tell whether it
was the answer to their command. **If the desktop is already on the
requested style**, the announcement is "Steht schon auf Linux Desktop."
("already on Linux Desktop"). The style is still re-applied (the same
guarantee as when restoring), only the announcement differs - before,
an ineffective command was indistinguishable from a real switch if you
cannot see the screen.

### 11d. German menu, and surviving a restart

**German ArcMenu menu:** Debian's package ships the finished translated
`de.mo` but puts it in `po/` instead of a `locale` directory - where
nobody finds it, so the start menu stays English. GNOME extensions
without their own `locale` directory look in `/usr/share/locale`, so
that is where it gets copied (no `msgfmt` needed, the file is already
compiled). This is the second fault in the same package as the schema
path from step 11b. `dash-to-panel` ships its German correctly itself;
`tiling-assistant` has no translation at all, but shows no text in the
panel either.

**Surviving restart and logout:** the chosen look persists because all
settings live in the account's dconf, which survives restarts by itself.
In addition, `dialos-desktop-stil.sh wiederherstellen` runs at login via
`/etc/xdg/autostart/dialos-desktop-stil-wiederherstellen.desktop`
(without an announcement, since nobody triggered anything). That is the
guarantee for the case where something else reset the extension list - a
system update, an accidental `dconf reset`, a freshly created account.
For a blind user a desktop that looks different after switching on than
it did last time is not a cosmetic flaw but a loss of orientation. If
there is no memo file yet, the call deliberately does nothing.

**"Without an announcement" was not true until 2026-08-17.** The call in
the script is redirected with `>/dev/null 2>&1`, and this line here read
that as evidence for "silent". But the redirection only swallows the
terminal line - `melde()` invokes speech output directly, and that keeps
talking. **So at every login the desktop spoke unasked**, straight into
the login announcement, because both autostarts fire at the same time.
That is exactly what Stephan had reported ("the desktop announcement
came in between"), but it had been filed as a timing problem between two
autostarts. Since then there is a `STUMM` (mute) variable:
`wiederherstellen` sets it to 1 and `melde()` then skips the speaking -
the terminal line stays. When checking, the duration is the tell: the
call takes about 800 ms; with the announcement it would be over 1800 ms.

### 11e. Microphone recording level (new 2026-08-16)

**This is not polish, it is the precondition for speech recognition
working at all.** On the T490 two gain stages were at maximum out of the
box: `Capture` at +30 dB *and* `Internal Mic Boost` at another +30 dB,
60 dB combined. Measured:

| State | RMS level | saturated samples |
|---|---|---|
| out of the box (`Internal Mic Boost` +30 dB) | 76 % | **50 %** |
| after the correction (boost 0 dB) | 2.8 % | 0 % |

The result was not noise but **silence on the control side**: Vosk
detects speech from the pauses between words. A permanently railed
signal has no pauses, so the recognizer never returns a result. The
voice-command service was running, listening, and could not possibly
understand anything - with no error message at all. On a system operated
solely by voice, that is total failure.

Fixed by `/usr/local/sbin/dialos-mikrofon-pegel.sh` together with
`dialos-mikrofon-pegel.service`, which runs at every boot. Two decisions
along the way:

- **Boost to zero, not to some middle value.** A too-quiet signal can be
  amplified in software; a clipped one is destroyed irrecoverably, its
  peaks cut off. When in doubt, too quiet.
- **A service instead of `alsactl store`.** `alsactl store` writes the
  complete mixer state of *this* card to `/var/lib/alsa/asound.state` -
  device-specific, and therefore nothing that could go into the ISO
  template. The script instead finds the controls by name (`*Mic
  Boost*`, `Capture`) and works on any device, even if the card is named
  or numbered differently. `alsactl store` is called additionally, as a
  second safeguard.

**This finding calls an earlier conclusion into question:** the
microphone comparison of 2026-08-13 concluded that the built-in
microphone was clearly inferior to the AIRHUG. If 60 dB were already
applied back then, the test did not measure the microphone but the
clipping. The comparison should be repeated before the Bluetooth
priority counts as proven (see TODO.en.md).

### 11f. Echo cancellation for the microphone (new 2026-08-17)

**Without it the voice-command service hears everything the device
plays** - its own announcement as well as radio, music or a media
library. Because recognition uses a restricted grammar, it forces
fragments of that into a command: while playing back the login
announcement, the desktop switched mid-playback. For a system meant to
play radio and music this is not an edge case - a newsreader saying
"Windows" would have the same effect.

The earlier safeguard (the "the system is speaking" marker file) cannot
solve this in principle: it only knows about the system's own
announcement via `dialos-say.py`. So the fix sits one level lower, in the
audio chain.

`/etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf` loads
PipeWire's `module-echo-cancel` with the WebRTC algorithm and provides a
cleaned source **`dialos_mikrofon_ohne_echo`**.
`dialos-sprachbefehl-desktop.py` takes it as first choice.

**Measured on 2026-08-17**, both sources recorded simultaneously while
the speaker played the login announcement:

| Source | Level |
|---|---|
| raw microphone | 6.13 % RMS |
| `dialos_mikrofon_ohne_echo` | **0.15 % RMS** |

That is about **32 dB** of attenuation - over Bluetooth, where far less
would have been expected given the variable latency. Control test: the
same announcement played via `paplay`, i.e. with no safeguard at all -
the service recognized **nothing** and did not switch.

Two decisions in the configuration:

- **`monitor.mode = true`.** Without it, every program would have to play
  its audio into a dedicated sink so the module knows what is currently
  audible - every audio output in DialOS would need rerouting, and every
  new program would have to remember. With `monitor.mode` the module uses
  the output's monitor as the reference instead. Nothing needs rerouting.
- **No `node.target` in `playback.props`.** That way the reference
  follows the default output automatically; if the user switches from the
  Bluetooth speaker to the built-in ones, cancellation keeps working.

**A rule that cost a total outage: the capture target must never be a
device that can be switched off or unplugged.**
`capture.props.target.object` therefore points at the **built-in**
microphone. On 2026-08-17 Stephan's USB headset was in there for testing,
and that test version was left in the system across a reboot. At login
the headset was switched off - and after that **the whole system could no
longer play any sound**, not even through the built-in speakers.

The sequence, because it sounds implausible without the intermediate
steps: the USB dongle is plugged in and registers a sound card whether or
not the headset is on. ALSA even reports `state: RUNNING` for that
capture device. It just delivers nothing - measured **0 bytes in 3
seconds**, while the built-in microphone delivers 64000. Echo
cancellation needs that capture as its clock; without a clock PipeWire
does not start the graph. The sound card then sits at `state: PREPARED`
with `trigger_time: 0.000000000`, and every playback hangs forever:

```
$ paplay -v bell.oga
Connected to device alsa_output.pci-0000_00_1f.3.analog-stereo (index: 70, suspended: no).
Time: 0,000 sec; Latency: 139332 usec.   Time: 0,000 sec; ...
```

What the user hears: nothing. No error, no beep, just speech-output
processes piling up - in this incident three announcements and four GNOME
sounds, all still queued. For a blind user that is not an audio problem
but a dead device.

**Two checks that pin the fault down immediately:**

```bash
# 1) Does the sound card start at all? PREPARED + trigger_time 0 = stalled graph.
grep -E 'state|trigger_time|hw_ptr' /proc/asound/card0/pcm0p/sub0/status
# 2) Does the capture target deliver data? 0 bytes = cause found.
timeout 4 parec -d <target> --format=s16le --rate=16000 --channels=1 | wc -c
```

For bisecting, cancellation can be switched off without a reboot: rename
the file to `.conf.aus` (`.conf.d` only reads `*.conf`) and
`systemctl --user restart pipewire pipewire-pulse wireplumber`. A test
version of your own belongs in `~/.config/pipewire/pipewire.conf.d/` -
**not** in `/etc`, where it survives a reboot.

Suspicion first fell on `webrtc.gain_control`, which had switched from
`false` to `true` the same day and likewise only took effect on reboot.
Both values hung identically - only a series test across capture targets
showed it. Without `target.object` the sound also works, because the
module then follows the default source; but that is not a safeguard, just
a different pick of the same risk.

**What remains open:** as soon as an external wireless microphone is to
become the standard - and that is exactly the plan - a safeguard is
needed that notices no data is arriving and drops cancellation instead of
taking the sound down with it. See `TODO.md`.

**Trap during setup:** restarting PipeWire throws the Bluetooth device
back into HFP, and the card then offers **no A2DP at all** -
`pactl set-card-profile ... a2dp-sink` fails with "No such entity". The
profile only reappears after reconnecting:

```bash
bluetoothctl disconnect <MAC> && sleep 3 && bluetoothctl connect <MAC>
```

### 11g. Choosing the audio output: Bluetooth or laptop (new 2026-08-17)

**Stephan's decision of 2026-08-17:** input is always the built-in
microphone, output is the Bluetooth speaker as long as it actually plays,
otherwise the built-in speakers. External microphones come up again at the
very end.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-ton-ausgabe.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/xdg/autostart/dialos-ton-ausgabe.desktop /etc/xdg/autostart/
```

**The more important half of the decision is the input.** If DialOS never
opens a Bluetooth microphone, the device can never drop into HFP - the
A2DP/HFP forced choice from step 11c disappears, not because it is solved
but because it is no longer touched. And the total outage from 11f becomes
structurally impossible: a built-in microphone cannot be switched off.

**Why this needs a service of its own**, even though PipeWire makes the
newest device the default by itself: because "present" does not mean
"plays". On 2026-08-17 a sink that reported `RUNNING` and accepted the
stream never played it - and thereby paralysed the entire audio output.
The service therefore queries no status report but **tries it out**: send
150 ms of silence and watch, with a timeout, whether `paplay` completes.
Silence as the test tone so the user does not hear a beep on every event.

Three decisions, each from a fault of the same day:

| Decision | Reason |
|---|---|
| **Choose at login, but do not announce** | Whoever is logging in has not switched anything. That is exactly where the desktop restore failed (11d) - it spoke and talked over the login announcement. |
| **Compare against its OWN last choice**, not the default sink | WirePlumber switches by itself when a device disappears, and it does so before the service looks. Comparing with the system state always yielded "nothing changed" and the announcement stayed away - although the audio had moved. |
| **Filter on `" on sink #"`**, not on `"sink"` | The test tone is itself a `sink-input` event. With the broad filter every test tone would have triggered the next one. |

Confirmed live on 2026-08-17: speaker off - "Ton ueber Laptop.", speaker
on - "Ton ueber Lautsprecher.", both transitions logged as real changes.

**On the Bluetooth speaker's volume** - measured the same day, because the
intuition leads the wrong way otherwise:

| Route | What happens | Does it work? |
|---|---|---|
| sink volume (GNOME slider, `pactl`) | the value goes to the device via AVRCP, the signal is unchanged | yes |
| attenuation in the signal (sox, `paplay --volume`) | the signal leaves the laptop correctly attenuated | **no**, the AIRHUG undoes it |

Proven on the Bluetooth sink's monitor: half amplitude in the file arrives
as 0.071559 against 0.143117 (factor 0.5000) - whereas sink at 100 %
against sink at 30 % gives **0.143117 both times**. It follows that
`bluez5.enable-hw-volume = false` would be a mistake. It would force
DialOS to attenuate on the route that does nothing on the AIRHUG, after
which there would be no volume control at all.

**And a side finding that affects a whole feature:** the sox chain in
`piper-generic.conf` ends in `norm`, and that lifts every output back to
full scale. `GenericVolume` is therefore ineffective - speech-dispatcher
cannot control DialOS's volume. Anyone who needs it must put the
attenuation **after** `norm` (`norm vol 0.70`).

### 11h. Dictation and the writing aid (new 2026-08-18)

The first step in the applications block. Dictation is not an application
but the precondition for four of them - the user cannot produce letters,
notes, mail or chat without it. All measurements and the reasoning are in
[diktat.en.md](diktat.en.md).

**Java from Debian's sources, LanguageTool by hand.** Only LanguageTool is
a foreign package - the first in the project, and it survives no system
update by itself.

```bash
sudo apt-get install -y openjdk-21-jre-headless
# LanguageTool 6.6, 241 MB packed / 392 MB unpacked:
curl -L -o /tmp/lt.zip https://languagetool.org/download/LanguageTool-stable.zip
unzip -q /tmp/lt.zip -d /tmp/lt
sudo mkdir -p /opt/languagetool
sudo cp -r /tmp/lt/LanguageTool-*/. /opt/languagetool/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/user/dialos-languagetool.service /etc/systemd/user/
sudo systemctl --global enable dialos-languagetool.service
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-diktat.py /usr/local/bin/
```

**Why a permanent service and not an invocation per sentence** (measured):
the command-line tool needs 9.3 s per call, the first request to the running
service 8.8 s - after that 0.6 to 1.6 s. For dictation only the service is
usable. It occupies about 1213 MB permanently.

**No `--public`.** Without that switch the server binds to 127.0.0.1
(verified: not reachable from the machine's network address). The public
service at languagetool.org is never used - it would send the user's letters
and mails to someone else's computer.

**Two recognizers over the same audio.** The big Vosk model (5.5 GB, 8.8 s
load time) for the text, a small one (229 MB, 0.4 s) with a grammar of
exactly one sentence for `diktat beenden`. The reason is a fault from the
first test: in free recognition "diktat beenden" became
`'diktat wird erhoeht'`. A SPECIFIC sentence cannot be hit reliably in free
recognition - the same thing that turns "gnome" into "genug" and "windows"
into "sinnlose".

**Only one may have the microphone.** `dialos-diktat.py` creates
`$XDG_RUNTIME_DIR/dialos-diktat-aktiv`; `dialos-sprachbefehl-desktop.py`
then keeps out and logs it. Without that a dictated sentence would also be
evaluated as a command - dictating "auf Windows umschalten" into a letter
would leave a different desktop behind. Evidenced live on 2026-08-18 with
timestamps in both logs.

**`--noise_w 0` in the speech chain** - see step 8 and the comment in
`piper-generic.conf`. Without that switch Piper spoke every sentence with up
to 17 % different duration, and a cached announcement sounded audibly
different from the same one freshly spoken.

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
session).

**What the service does at boot - two layers since 2026-08-16:**

1. **Autologin** for `nutzer` on or off, depending on whether the home
   partition could be unlocked.
2. **Locking or unlocking the `nutzer` account** (`usermod -L`/`-U`).
   Autologin alone is not enough protection: without the stick, GDM still
   lists both accounts, and anyone who knows `nutzer`'s password (printed
   once when `dialos-setup-nutzer.sh` generates it) could still log in.
   `/home/nutzer` would then **not** be mounted and the session would run
   against a directory on the **unencrypted** root partition - at best it
   fails on permissions, at worst it creates a profile there in the
   clear. With the lock, the question is moot.

   **The order matters:** unlock first, then set autologin -
   AccountsService rejects `SetAutomaticLogin` for a locked account with
   "user is locked". Reversed when switching off. `dialosadmin` is never
   locked, so you cannot lock yourself out.

**Test (passed on 2026-08-16):** unplug the stick, reboot - the system
must land on the normal GDM login screen instead of autologging `nutzer`,
and `/home/nutzer` must not be mounted. Then plug the stick back in and
reboot again - `/home/nutzer` must be mounted and autologin must work
again. The lock state can be checked with `sudo passwd -S nutzer`
(`P` = usable, `L` = locked).

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
3. **Admin account into the `adm` group** (new 2026-08-16, Stephan's
   decision). Without it `dialosadmin` reads no system logs:
   `journalctl -u <service>` answers "-- No entries --" even though the
   service did log. Noticed while hunting the over-amplified microphone
   (step 11e) - the obvious wrong conclusion "the service does nothing"
   would have been expensive there. `adm` is Debian's standard group for
   this and grants **read** access to logs only, no further rights;
   `systemd-journal` isn't needed because systemd grants that group the
   journal rights anyway. Deliberately for the admin account only - for
   `nutzer` system logs would be useless and merely extra attack
   surface. Takes effect at the next login.
4. `dialos-setup-nutzer.sh` - creates `nutzer` (`adduser
   --disabled-password`, groups
   `sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom`,
   random sudo password), switches autologin from `dialosadmin` to
   `nutzer` (with retry logic against a timing bug: "user is locked"
   right after `chpasswd`, because AccountsService hadn't yet noticed
   the new password entry).
5. Checks that the Firefox homepage policy from step 10 is set
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
`/usr/share/applications/dialos-rekey.desktop` (up to 2026-08-16 this
was `dialos-install.desktop`, which went away with the tool) (placed there in step
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

On the split between input and output, **as of 2026-08-17**:

- **Speech input: always the built-in microphone**, via the
  echo-cancelled source (step 11f). Bluetooth only as a last resort on
  devices without a built-in microphone.
- **Speech output: the Bluetooth speaker** whenever connected -
  otherwise the built-in speakers.

That sounds contradictory but is exactly the point: because speaker and
microphone are different devices, the microphone picks up the output in
the room - and that is precisely what echo cancellation subtracts (32 dB
measured). Using the Bluetooth microphone instead would drop the headset
to HFP and the output to phone quality.

The earlier microphone comparison test reached the opposite conclusion
(Bluetooth clearly superior) but ran with the built-in microphone
over-amplified by 60 dB and is therefore not reliable - it should be
repeated (TODO.en.md). Details:
[offene-punkte.en.md](offene-punkte.en.md), section "Voice control".

## 16. Backup image (Clonezilla)

**Decision of 2026-08-16: Penguins' Eggs is dropped, Clonezilla takes
over.** This step used to read `eggs produce`. With path A (see step 5)
the ISO is no longer an installation medium - no device is installed from
it, every one is built from the Debian ISO plus the three scripts. What
remained was the "backup snapshot" purpose, and Clonezilla suits that
better: it is in Debian (`clonezilla`), so no third-party repository is
needed, and it does exactly one thing.

The trigger was that `eggs` was simply missing on the rebuilt system: it
is not in Debian's repositories, was in no package list, and **how to
install it was documented nowhere** - neither in this guide nor in the
commit history. The same kind of gap as `check_piper_voice.sh`: done by
hand once, never written down, lost in the reinstall.

**Stephan creates the image himself using a Clonezilla variant with a
graphical interface** - hence no click-by-click instructions here. Only
the three points that follow from the DialOS layout are recorded, because
they surprise you the first time:

1. **Clonezilla does not run from the running system.** The system disk
   must be idle, so you boot from separate media.
2. **The encrypted partition must NOT go into the image.** For ext4 and
   vfat, Clonezilla saves only used blocks - root is therefore about
   15 GB rather than 93. But it cannot see inside `dialos-nutzer-home`
   (LUKS2) and copies all ~375 GB byte by byte; encrypted data also does
   not compress. So select only `nvme0n1p1` (root) and `nvme0n1p2`
   (EFI). Leave out the swap partition too - it is recreated at every
   boot anyway.
3. **The image therefore does not contain `nutzer`'s data.** That is the
   flip side of the encryption and intended. To back those up as well,
   a second route in the **unlocked** state is needed - a file-level
   backup rather than an image.

If only individual partitions are saved, the partition table is not
included. The restore path is then: install Debian via the preseed (step
1 creates EFI + 100 GiB root), then write the image over it.

> **The real snapshot is now this repository.** On 2026-08-16 it was
> shown that three commands turn a bare Debian install into the complete
> system - script 1 ran in 5-6 minutes including a 1.9 GB model download.
> An image preserves *a state*; the recipe preserves the *ability to
> produce it*. The latter does not age, because it is exercised on every
> device. The image mainly saves restore time.

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
