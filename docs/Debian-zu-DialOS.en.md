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

> **Fast path (as of 2026-08-19): five commands from Debian to DialOS.**
> Three until 2026-08-19; the two new ones clear out what Debian ships and
> DialOS does not need (Stephan's requirement, see step 13b).
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
grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' iso-build/config/package-lists/desktop.list.chroot \
  | sudo xargs apt-get install -y
```

**Comment lines have to be stripped first** (bug found on 2026-09-14). Until
then this said `sudo xargs -a …desktop.list.chroot apt-get install -y`.
`xargs` passes on every word, including those of a comment. Since the comment
on the Windows look was added to the list on 2026-08-16, apt received words
like "Optionale" as package names, aborted and installed **not a single
package**. The same applied to `scripts/dialos-full-office-setup.sh` (which,
because of `set -e`, stopped in step 2). Found while adding spell-checking,
reproduced with `apt-get install -s`. This device was not affected: the
simulation shows every package in the list is installed.

Notable groups within it (in the order they appear in the file):
- **Language/desktop base**: `task-german`, `task-german-desktop`,
  `gnome-core`, `gdm3`, `orca` (screen reader), `espeak-ng` (later
  replaced by Piper, see step 8), `plymouth` + `plymouth-themes`.
- **Network/firmware**: `network-manager` + GUI, firmware packages for
  the T490 (WLAN/microcode).
- **Applications**: Firefox, Thunderbird, Shortwave (radio), Rhythmbox,
  GNOME Podcasts, LibreOffice Writer. Plus spell-checking
  `hunspell-de-de` + `hunspell-en-us` (added 2026-09-14): before, it only
  came in indirectly via `task-german-desktop` and so counted as
  "automatically installed". `aspell` is left out on purpose - no program on
  the device uses it; LibreOffice, Firefox, Thunderbird and GNOME use
  hunspell.
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

**Background by season (since 2026-09-16).** Stephan: bring "some swing" into
the wallpaper - four pictures of the same mountain lake
(`wallpaper-fruehling/sommer/herbst/winter.png`, sources in `assets/` as
`…-light.png`/`…-dark.png`, losslessly repacked: same pixels, 6-11 MB instead of 32 MB).
`dialos-jahreszeit.py` computes the **astronomical** start of each season every
year (Meeus, accurate to minutes; 2026: 20.03. 15:46, 21.06. 10:26, 23.09.
02:06, 21.12. 21:51) and sets `picture-uri` and `picture-uri-dark` to the season
picture and its dark version `wallpaper-<season>-dark.png`. The pictures (3840 ×
2160, light and dark since 19:10) are in `/usr/share/backgrounds/dialos` on every
installation; the user only switches the style (quick settings top right: "Dark
Style"), the picture follows by itself. Southern
hemisphere via the country in the personal data. **Only a DialOS picture** from
`/usr/share/backgrounds/dialos` is switched; a self-chosen photo stays. User
timer at login (20 s) and hourly.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-jahreszeit.py /usr/local/bin/
sudo cp iso-build/config/includes.chroot/etc/systemd/user/dialos-jahreszeit.service iso-build/config/includes.chroot/etc/systemd/user/dialos-jahreszeit.timer /etc/systemd/user/
sudo systemctl --global enable dialos-jahreszeit.timer
```

Check: `dialos-jahreszeit.py --zeigen`; log `~/.log/dialos-jahreszeit.log`.

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
[the file in the repo](beispiele/gdm3-custom.conf))
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
  **New sentences generated directly since 2026-09-16:** every time of day
  is new and started only 2.3-2.7 s after the call - a warm-up
  announcement "." via speech-dispatcher (0.87 s, Piper loads the model),
  then the sentence (0.95 s, the model a second time), then a third time in
  the background for the cache. Now `dialos-say.py` generates the sentence
  once with the cache chain (`speicher_fuellen(text, warten=True)`) and
  plays the file immediately - measured at the speaker output 1.4-1.7 s to
  the first sound, depending on sentence length, and the sentence is cached
  afterwards. Instead of the warm-up announcement, **only with Bluetooth
  output** 0.3 s of silence plays during generation (`bluetooth_wecken()`).
  With `--lautstaerke` (start announcement) and as a fallback the
  speech-dispatcher route stays.
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

**Since 2026-09-21 the tone is switched on - Stephan's decision after the
spelling measurement** ("the tone never comes"). The trigger was a measurement
that announced single words: **on a single "a" or "be" the intonation carries
nothing** - there is no sentence for it to be heard in. The same holds wherever
DialOS asks a short question. The choice of 2026-08-17 remains right for whole
sentences - the tone now comes in addition, not instead of the melody.

It is set up via `/etc/skel/.config/dialos/frageton` (for every account created
from now on) and for existing accounts with a file:

```bash
printf 'an\n' > ~/.config/dialos/frageton
```

For the account `nutzer` as root, because that home belongs to the account:

```bash
sudo -u nutzer mkdir -p /home/nutzer/.config/dialos && sudo -u nutzer sh -c "printf 'an\n' > /home/nutzer/.config/dialos/frageton"
```

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

**What is in the start menu** (since 2026-09-14, after Stephan's review: it
still looked chaotic). Before, DialOS only set the kind of menu; the content was
ArcMenu's defaults. They did not fit: `firefox.desktop` was pinned - on Debian
Firefox is `firefox-esr.desktop`, so the slot stayed empty, without icon or
name - plus "ArcMenu-Einstellungen" without an icon. Now, as Stephan chose:

| Key | Value | Why |
|---|---|---|
| `pinned-apps` | Firefox, Thunderbird, Writer, Files, Text Editor, Calculator | everyday programs only, the same for both accounts; all six are on the keep list of step 13c |
| `eleven-disable-frequent-apps` | `true` | "Frequent" changes with use - a helper on the phone has to be able to say where something is |
| `group-apps-alphabetically-list-layouts` | `false` | with few programs almost every one stood alone under its letter |
| `menu-item-grid-icon-size` + `custom-grid-icon-size` | `'Custom'`, 170 × 130, icon 64 | three large icons per row (Stephan: make the icons a bit bigger and spread the programs over 2 rows) |

**Why the fixed size is needed:** ArcMenu estimates the columns from the menu
width using icon width + 10 points - in the `Eleven` layout
(650 − 12) / (92 + 10) = 6. In reality an icon with its label was about 116
points wide; six of them stuck out on the left and right ("refox ESR",
"Taschenrech|ner"). With 170 points the estimate gives 3 columns, really about
3 × 194 = 582 of 638 - and a seventh program would go into a new row instead of
overflowing.

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

**Since 2026-09-16 the recording is no longer restarted but stays open.**
Stephan: between Anna's announcement and his answer he always has to wait
about 1.5 seconds, otherwise the first word is swallowed. The restart cost a
0.7 s reverberation pause, 0.3 s in `aufnahme_starten()` and up to 0.3 s of
polling. After its own announcements, on the other hand, the backlog stayed
("speichern" after "Das Bildschirmfoto ist gespeichert").

Now a dedicated **reader** (`class Leser`) reads parec continuously and stores
every block with its arrival time - also while the main loop is inside
`sprich()`; before, the buffer then overflowed and what got lost was not under
control. After every announcement (other programs' via the marker, its own via
"not read for longer than `STAU_S`") audio is discarded **by time**: what
arrived in the last `VORLAUF_MARKE_S` (0.625 s) before the marker ended is kept,
on sources without echo cancellation `VORLAUF_MARKE_ROH_S` (0.5 s), after a
dictation nothing. Reason: **the marker ends 0.64-0.70 s after the last audible
sound** (measured at the speaker output) - Piper appends the sentence pause
(`--sentence_silence 0.5`) after the last sentence too. Anyone answering in that
silence lost the first word.

Simulated with `scripts/dialos-ansage-luecke-nachbilden.py` (real service, real
Vosk, answer timed from the last audible sound): old state 0/8 at 0.15 s and
3/8 at 0.4 s; with the reader 8/8, 8/8, at 1.0 s 7/8 (one recognition error),
with the announcement in the raw microphone 8/8.

**Letter post-processing since 2026-09-16:** `brief_schreiben()` in
`dialos-diktat.py` puts closing and name on separate lines
(`grussformel_richten`) and turns a "Betreff" at the start of the letter into
the line "Betreff: …" (`betreff_richten`). `als_pdf()` in `dialos-archiv.py`
sets that line in bold; `dialos-drucken.py` prints letters via that PDF. No new
packages (cairo, DejaVu Sans Mono are present).

**Fallback answers since 2026-09-16:** 42 command sentences - plus "was kann
ich sagen"/"was kannst du" (overview), "wie ist/wird das wetter" (via
`dialos-auskunft.py wetter`, fallback place from `~/.config/dialos/wetter-ort`,
wording in `wetter_satz()` in `dialos-start-ansage.py`) and eight sentences with
an honest answer (`WUNSCH_SAETZE`, logged as `WUNSCH`). Without a matching
command: "Das kann ich noch nicht. Sage: Was kann ich sagen." Checked with
`/usr/local/bin/dialos-grammatik-pruefen.py`: all 42 sentences verbatim.

**Command overview since 2026-09-16:** 49 command sentences - plus "alle befehle
vorlesen" and "befehle für fragen/briefe/notizen/den einkauf/den bildschirm/das
diktat". `befehls_themen()` in the command service builds the texts from the
command tables (`AKTIONEN` labels them; the dictation commands come from
`dialos-diktat.py`). One minute after start `befehle_vorbereiten()` stores all
announcements in `dialos-say.py`'s cache at low priority (measured: about 50 s
CPU time, 144 s of audio in total, each topic under 30 s).
`befehle_ohne_uebersicht()` reports every sentence without a place at start. No
new packages. Checked: all 49 sentences verbatim.

**The desktop-look rule** ("umschalten" plus a target anywhere in the utterance)
applies since 2026-09-16 only without `[unk]` and with at most two words more
than "auf windows umschalten" - on 09-15 a twelve-word salad switched to
Windows.

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
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-notiz.py /usr/local/bin/
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-auskunft.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/usr/local/share/dialos/woerterbuch-vorlage.txt /usr/local/share/dialos/
```

`woerterbuch-vorlage.txt` (since 2026-09-15) is the template for dictation's
personal dictionary; dictation copies it to `~/.config/dialos/woerterbuch.txt`
the first time. Details in [diktat.en.md](diktat.en.md).

`dialos-auskunft.py` announces the time and the date. It imports the speech
building blocks from `dialos-start-ansage.py` - weekday, ordinal, number as
words - rather than rebuilding them: two places with the same job would
drift apart, and the user would hear the difference at once. The import is
safe because that script only acts under `if __name__ == "__main__"`.

**Weather on request deliberately does not exist** (Stephan, 2026-08-19).
The command was built and removed again: at the site of use beaconDB knows
none of the visible Wi-Fi networks and falls back to IP geolocation -
measured as Vienna with 26 km accuracy, about 300 km away. The 10 km
threshold correctly discards that, and the command would almost always have
answered only that it cannot fetch anything. In the login announcement the
weather stays, because there it simply drops out without anyone asking.

`dialos-notiz.py` reads notes out and empties them - the voice commands are
in [sprachbefehle.en.md](sprachbefehle.en.md). Emptying asks for
confirmation and moves the old content to `<name>-verworfen.txt` so a
sighted helper can retrieve it.

**Check words against the vocabulary before building them in, not only
against the recognition.** The obvious command "Einkaufszettel loeschen" is
impossible - "loeschen" is not in the small model's vocabulary, and Vosk
drops it from the grammar SILENTLY. Vosk reports it itself:

```bash
python3 -c "import json,vosk; vosk.Model('/usr/local/share/vosk-model-de-small'); \
  vosk.KaldiRecognizer(vosk.Model('/usr/local/share/vosk-model-de-small'),16000, \
  json.dumps(['loeschen','[unk]']))" 2>&1 | grep -i 'missing in vocabulary'
```

Also absent: "zuruecksetzen", "aufraeumen". Present and therefore used:
wegwerfen, leeren, erledigt.

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

**`--sentence_silence 0.5` in the speech chain** (2026-09-14, Stephan chose
"Variante B" in a listening comparison, for Anna and Michael). The pause after
each sentence: 0.2 s by default, measured at about 0.45 s between two
sentences; now about 0.78 s. Variant C (0.75 → about 1.04 s) dragged. The pause
at a comma stays the same. It is in `piper-generic.conf` **and** in
`dialos-say.py` (cache), for the same reason as `noise_w`. `dialos-aufspielen`
does not install the configuration file - do it by hand with `sudo install`,
then `systemctl --user restart speech-dispatcher.service`. Measured on the
device: pauses of 760 and 940 ms in a freshly cached announcement.

### 11i. Footer, live transcript and half-transparent bars (new 2026-08-19)

Three wishes of Stephan's that have nothing in common except the day.

**Footer for documents, mails and printouts.**

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-fusszeile.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/usr/local/share/dialos/fusszeile.txt /usr/local/share/dialos/
```

The text lives in `/usr/local/share/dialos/fusszeile.txt` and **only there** -
letters, mails and printouts read it from that one place. Were it in three
places in the code, two of them would go stale unnoticed, because hardly
anyone uses all three routes on the same day.

Right alignment in plain text is done with spaces (width 76). If the sentence
is longer than the width it stays unshortened and left-aligned - a truncated
provenance note would be worse than an unaligned one.

**Notes deliberately do NOT get it** (Stephan's decision). The shopping list
is appended to on every dictation; a footer would land in the middle of the
text each time. Notes are working lists, not documents. When a list is
printed, the line is added at print time: `dialos-fusszeile.py drucken FILE`.

**Paper size and orientation are dictated to the printer.** On 2026-08-22
Stephan's first real printout came out landscape instead of portrait. Where
the rotation happens was measured: not in this queue's CUPS filter chain.
With the Brother HL-L2350DW's PPD, `texttopdf` produces 595x842 points - A4
portrait - and `pdftopdf` passes exactly that through, rotation 0. The printer
itself reports `orientation-requested-default = portrait` and
`media-default = iso_a4` over IPP. So the rotation happens beyond that, inside
the device.

It is therefore part of the job now instead of being nobody's default:

    lp -d TARGET -o media=A4 -o orientation-requested=3 -

`3` is portrait, `4` would be landscape (RFC 8011). The value is spelled out
rather than omitted - a default you rely on is an assumption, and this
assumption was demonstrably wrong.

**Confirmed on 2026-08-22:** printouts have come out portrait since (Stephan:
„Ausdruck ist jetzt hochkant"). That does not name the cause - it lies beyond
anything measurable here. But an explicit setting beats any default, and that
was the point.

This surfaced a second print path: `dialos-fusszeile.py drucken` called
`lp -` **without a destination**. This device has no system default
(`lpstat -d` reports "no system default destination"), so the call would have
failed. It now looks up the destination exactly as `dialos-drucken.py` does.

**"notiz drucken" now counts as well.** In the retest on 2026-08-22 Stephan
spoke the command and nothing happened - the log reads `erkannt: 'notiz
drucken'` while the grammar only had `notizen drucken`. That is not a
mishearing but how the restricted grammar is built: Vosk turns the phrases
into a word network. It knows "notiz" from "notiz aufnehmen" and "drucken"
from the three print commands - the combination is permitted but is not one of
the listed phrases. The command therefore fell through silently, with no
announcement, because there was no match at all. The singular is now in the
list as a second wording.


In a mail "Dieses Dokument" becomes "Diese Nachricht" (`--art mail`) - a mail
is not a document.

**The footer in EVERY mail (added 2026-08-20).** The next day Stephan sent a
mail and the line was not in it. It could not have been:
`dialos-fusszeile.py` was built and documented, but **not a single program
called it** - a tool without users. The Thunderbird profile held zero
signature entries. A requirement is not met because the tool for it exists,
only once something uses it.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-mail-signatur.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/system/dialos-fusszeile.service /etc/systemd/system/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/system/dialos-fusszeile.path /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dialos-fusszeile.path dialos-fusszeile.service
dialos-mail-signatur.py          # as the logged-in user, with Thunderbird closed
```

`dialos-fusszeile.py signatur` generates `mail-signatur.html` and
`mail-signatur.txt` next to the source. Thunderbird can only read a signature
from a **file**, not from a program - so that file is a second place holding
the sentence, exactly the copy this section is meant to avoid. It is therefore
never maintained by hand: the `.path` unit watches `fusszeile.txt` and
regenerates it as soon as the sentence changes. That way it cannot go stale
unnoticed. **Measured 2026-08-20:** `touch` on
`fusszeile.txt` at 18:34:07, both signature files rewritten 80 ms later
(`journalctl -u dialos-fusszeile.service`).

`dialos-mail-signatur.py` writes the entries into the profile's **`user.js`**,
not into `prefs.js`: Thunderbird rewrites `prefs.js` on exit and would lose a
foreign entry. `user.js` is layered on top at every start. The price: the
signature cannot be switched off permanently in the account settings - for an
origin notice that is required in EVERY mail, that is the right way round. It
is set for **every** identity the `prefs.js` knows, and `sig_bottom=false`
places it directly below the user's own text when replying instead of below
the whole quote (the profile replies above the quote).

Two formats on purpose: Thunderbird composes in HTML here, and only there does
"discreet and right-aligned" work cleanly - in plain text it would need spaces
that wrap on a phone. The `.txt` sits alongside in case an account composes in
plain text; then the account setting is switched over, with nothing to build.
The `sig_file` entry is internally a file type (`datatype="nsIFile"` in
`am-main.xhtml`), whose stored form on Linux is the absolute path - so a path
as text is enough.

**The name is clickable (Stephan's follow-up, 2026-08-20).** In the HTML
version "DialOS.org" becomes a link to `https://dialos.org` - canonical
without "www", since `www.dialos.org` redirects there with a 301 (checked the
same day). It inherits the line's colour (`color:inherit`) and is only
underlined: the usual link blue would be the loudest thing on the page in a
line that is meant to be "discreet" - without the underline, conversely,
nobody would see it is a link. **The `.txt` stays without an address.** In
plain text a spelled-out address would be a second version of the same
sentence, and the recipient would have to retype it; their mail client
usually turns "DialOS.org" into a link by itself anyway.

**Name and contact in the signature (since 2026-09-17).** If there is personal
data, `dialos-mail-signatur.py` writes a signature PER ACCOUNT to
`~/.config/dialos/mail-signatur.html` (and `.txt` with the `-- ` delimiter):
name, street and town, phone/mobile and mail, small and grey on the left, below
it the DialOS line from `/usr/local/share/dialos/mail-signatur.html`. `user.js`
then points to the file in the account; without data the plain DialOS line
stays. The user service `dialos-mail-signatur.service` runs
`dialos-mail-signatur.py --anmelden` at login: rewrite the signature, touch
`user.js` only if something changes and Thunderbird is not running. So a phone
number changed in the input form - also for `nutzer` - is in the mail after the
next login.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-mail-signatur.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/user/dialos-mail-signatur.service /etc/systemd/user/
sudo systemctl --global enable dialos-mail-signatur.service
```

**This covers one of two mail paths.** According to `docs/anwendungen.md`
Thunderbird is the interface, not the engine: DialOS is to send via IMAP/SMTP
itself later, because Thunderbird cannot be driven from outside. The signature
only applies to mail going through Thunderbird - that is, to everything the
sighted helper writes. The own sending path has to fetch the line itself
(`dialos-fusszeile.py text --art mail`); the note sits in `TODO.md` at that
point.

**The account is not part of the image.** It is created by hand during initial
setup (form `thunderbird-angaben-formular.md`), and only after that is there an
identity a signature can be set for. `dialos-mail-signatur.py` therefore
belongs at the **end** of initial setup, after the account has been set up.
Without an account it stops with a message instead of silently doing nothing.

**Live transcript for sighted onlookers.**

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-mitschrift.py /usr/local/bin/
```

The window **opens and closes with the voice control** (Stephan's
clarification of 2026-08-19): open on "Sprachsteuerung starten", closed on
"Sprachsteuerung stoppen" and also when the two-minute timeout switches off.
It is opened and closed by `dialos-sprachbefehl-desktop.py` - it hangs off the
voice control, not off the login: where nothing is spoken there is nothing to
transcribe.

Deliberately NOT on every single command - that would steal focus during
dictation, and whoever is dictating cannot see the screen anyway. Opening once
per session is unobtrusive; jumping up at every sentence would not be.

Two traps learned in the process:

- **Check whether one is already running before opening.** Without that,
  twenty activations would leave twenty windows stacked up. The check goes
  through `/proc`, looking for the Python script.
- **What gets closed is the SCRIPT, not the terminal.** `gnome-terminal`
  detaches from the invocation and hands over to an already running
  `gnome-terminal-server`; the invocation's PID is gone immediately and the
  server's belongs to every window. End the script, however, and the window's
  command ends - so the window closes by itself.

**Backlog on opening - found by Stephan's test.** The window is opened by
"Sprachsteuerung starten", so that sentence is already in the log before the
transcript starts reading, and was therefore **always** missing - from the
window and from the support log alike. For support that would have been the
first question ("did they switch it on at all?"). The service therefore invokes
it with `--rueckblick 20`: 20 seconds of history, which also picks up the
unrecognized attempts before it - often the more revealing half for support.
Started by hand it stays at 0, so a window you open yourself does not begin with
old lines.

Two traps in it that would have broken both:

- **Duplication.** Switching on twice in quick succession would write the same
  lines to the support log twice. The file itself is the marker: the timestamp
  of its last line is the cut-off. No extra state that could go stale.
- **The day boundary.** The four logs write only `HH:MM:SS` and are not rotated
  (see `TODO.md`). Compared forwards, an entry from **yesterday** at 17:52 looks
  like "later today" - a backlog in the evening would have picked up dictated
  text from someone else's session. Testing with a wide backlog put exactly such
  lines in the list. So the end of the file is read **backwards**: the timestamps
  run downwards, and where one jumps up, that is the day boundary and reading
  stops.

**And the same at the end of the session** (found on 2026-08-19, after the
backlog had healed the beginning). At 10:53:27 the log held only "Mitschrift
geschlossen" - why the voice control had stopped was nowhere. Two causes, both
fixed:

- **The timeout was not logged at all.** The service switched off after two
  minutes, announced it and closed the window - without writing a line about it.
  So the log held the effect and not the cause. Now `Zeitgrenze: 120 s ohne
  Befehl` is written, and **before** the announcement: that runs 3.5 s, during
  which the transcript still reads the line.
- **The last line came too late to be read.** `melde()` sat behind the `kill` -
  the window was dead before the message was written. Now it reports first,
  waits `NACHLAUF_S = 1.0`, then closes. The transcript polls every 0.4 s; one
  second is ample, and it goes unnoticed because an announcement is running
  anyway.

Both are the same class of fault as the missing backlog: **the log showed what
happened but not why.** For debugging that is the useless half.

Anyone who wants the screen free creates `~/.config/dialos/mitschrift`
containing `aus`. The default is **on**, because of the support log (right
below): were the window off by default, there would be nothing to read back
when the phone rings.

**Why a filter and not `tail -f`:** on 2026-08-19 the command log consisted of
**4132 level lines against 13 real ones**. The transcript discards the level
display and translates the log lines into sentences:

```
08:47:51  Sprache   gehoert: "wie viel uhr ist es"
08:47:51  Sprache   Auskunft: uhrzeit
17:52:41  Diktat    geschrieben: "Marisa"
```

It reads **five** logs together (command service, dictation, information,
notes, audio watcher - the fifth since 2026-08-19, see below) and merges them by time. Exactly this merging produced the proof on
2026-08-18 that dictation and command recognition do not interfere - by hand
it was laborious. **A mistake of my own:** at first it printed source by
source, which looked chronological and was not. For a tool whose purpose is
to show simultaneity that would have been the wrong property.

**Support log (Stephan's request of 2026-08-19).** Whatever passes through the
window is additionally written to a daily file:
`~/.local/share/dialos/support/befehle-YYYY-MM-DD.log`, directory 0700, file
0600. One file per day, kept **seven days**; on startup and at midnight the
transcript clears out the older ones itself. The date in the filename means
that cleaning up is "delete an old file" and not "search a running file for the
cut-off" - the file currently being written is never touched. Files that do not
match the naming pattern are left alone.

The purpose is the support call: read back what the device actually heard
instead of relying on memory.

**What goes in - and what does not.** The commands in full, of the dictated
text the **first line** (truncated to 60 characters) and after that only the
count:

```
09:50:10  Sprache   gehoert: "einkaufszettel aufnehmen"
09:50:12  --- Einkaufszettel ---
09:50:12  Diktat    Diktat laeuft (einkaufszettel)
09:50:26  Diktat    erste Zeile: "Milch"
09:50:41  Diktat    gespeichert in /home/nutzer/Notizen/einkaufszettel.txt
09:50:41            (2 weitere Zeilen erfasst, nicht protokolliert)
09:53:30  --- Sprachsteuerung ---
```

`~/dialos-diktat.log` contains every dictated sentence verbatim - the whole
letter. A file meant for an outside helper must not contain the user's mail.
One line is enough, though, to see THAT something was captured and whether it
made sense. The window still shows everything; there it is seen only by someone
sitting in front of the device anyway.

**The context matters most** (Stephan): "Milch" on its own tells nobody
anything, "Einkaufszettel: Milch" tells the whole story. So every section is
preceded by what it was about - dictation, shopping list, question to the
system, later mail and letter. It is not guessed but carried along from the
lines the programs write themselves on startup; an unknown target lands
untranslated but readable in the log instead of missing.

**A mistake of my own:** the first draft reset the context after every line.
That put "gespeichert in ..." outside its "Einkaufszettel" section, and a single
command ended up with two headings. A heard sentence is the only reliable
boundary - it always means the user is talking to the voice control again, and
it also arrives when a dictation breaks off early and the closing line is
missing.

**Half-transparent bars - two bars, two routes.**

| Bar | How | Package |
|---|---|---|
| bottom (Windows look) | dash-to-panel, `trans-panel-opacity 0.5` | none, it ships with it |
| top (GNOME look) | blur-my-shell, `color` with alpha 0.5 | `gnome-shell-extension-blur-my-shell` |

The values are in `01-dialos-defaults` and set by `dialos-desktop-stil.sh`
when switching. **In the Windows look there is no top bar** - dash-to-panel
replaces it. blur-my-shell has nothing to do there and needs no switching on
or off.

**The same trap twice, in both extensions:** a value on its own does nothing.
dash-to-panel had `trans-panel-opacity` at 0.4 from the factory, ineffective
because `trans-use-custom-opacity` was false; blur-my-shell needs
`customize=true`, otherwise its general values apply instead of the specific
ones.

**And: `color` with alpha instead of blur.** The extension's default is
`sigma 30`, i.e. heavily blurred. What was asked for was "half-transparent" -
that is half-opaque black over the background, and with alpha 0.5 it matches
the bottom bar exactly.

**All other effects of the extension are explicitly switched off** (overview,
dash, application windows, lock screen and four more). It can do much more
than is needed, and every additional effect is one more that can break at the
next GNOME jump - with three extensions this project has already found two
Debian packaging bugs. Leaving them at defaults would be the opposite of a
decision.

**Worth knowing when rebuilding:** a freshly installed shell extension is
invisible to the RUNNING shell - it scans the directory only at startup, and
under Wayland it cannot be restarted. Only logging out and back in helps.

### 11j. Power: no standby, no lock screen, three battery warnings (new 2026-08-21)

Three things that belong together: the device must not fall asleep, it must not
lock the user out, and it must say when the battery is running low.

**The first two were found in passing.** Stephan wanted to let DialOS run
through a night in order to measure self-activation with nobody in the room.
While preparing that it turned out nothing would have come of it - and why that
concerns more than the test.

```bash
sudo install -m 644 iso-build/config/includes.chroot_before_packages/etc/dconf/db/local.d/01-dialos-defaults /etc/dconf/db/local.d/
sudo dconf update
# Switch the lock back on for the support account only:
gsettings set org.gnome.desktop.screensaver lock-enabled true
```

**No standby on mains.** Out of the box GNOME sleeps after 900 seconds without
keyboard or mouse input, on mains just as on battery. Proven in this device's
system log on 2026-08-20: twice `Starting systemd-suspend.service` while DialOS
was running (16:26 and 18:20). Speech does **not** reset GNOME's idle counter -
only input devices do, and none of the ten inhibitors blocks (all are "delay").
A blind user who touches nothing for a quarter of an hour and then says
"Sprachsteuerung starten" would get no reaction and would not see why. On mains
therefore `'nothing'`; on battery standby stays as protection against a flat
battery, but only after 30 minutes (Stephan's decision).

**No screen lock for the user.** `lock-enabled=true` with `lock-delay=0` means
locking the moment the screen goes dark, i.e. after five minutes. Together with
the autologin the user would be locked out of their own device after five
minutes - for someone with impaired motor control that is precisely the reason
DialOS exists. The door is the LUKS full-disk encryption (see
`docs/sicherheit-datenschutz.md`), not the lock screen. For `dialosadmin` the
lock is switched back on individually, because that is where the support tools
live and where a person sits who can type a password. The **screen** may still
go dark - that does not stop the voice control.

**Three battery warnings** (Stephan's requirement the same day: 25 %, 15 %, 5 %,
"the last one with an announcement that the device must go to the mains socket"):

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-akku-warnung.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/user/dialos-akku-warnung.service /etc/systemd/user/
sudo systemctl --global enable dialos-akku-warnung.service
systemctl --user daemon-reload && systemctl --user start dialos-akku-warnung.service
```

GNOME does warn about a low battery itself - with an on-screen message the user
cannot see. For them the device shuts down without warning, mid-sentence, and a
flat battery is harder for them to interpret than almost any other fault: the
device simply stops answering.

Three levels, three tones - at 25 % a statement, at 15 % advice, at 5 % a demand
**with the name**. The same sentence three times would carry the same weight
three times, leaving no escalation for the serious case. Spoken is "Steckdose"
rather than Stephan's "Netzdose", because everyone understands that without
thinking - the announcement comes at a moment when little time is left.

**"Computer" and not "Gerät"** (Stephan, 2026-08-21: "when we say Gerät we
mean the laptop, the computer - so let us call it Computer"). This applies
everywhere DialOS speaks, not only to the battery - five announcements
affected, three in the battery warning and two in remote support. "Gerät" is a
technician's word; someone who cannot see what is being talked about needs the
word they use themselves. Note the grammatical gender: "das Gerät" becomes "der
Computer" - a plain word swap would have left wrong articles behind.

**Via the mains indicator, not the battery status.** `BAT0/status` on this
device reported `Not charging` while the power supply was plugged in - a charge
threshold holds the battery at 78 %. Equating "not charging" with "on battery"
warns with the cable connected. What is read is therefore `online` of the source
of type `Mains`.

**The check runs every 10 seconds, and the reason is not the battery.** For
the warnings 60 s was ample - hours pass between 25 % and 15 %. It was too slow
only for the confirmation when plugging in: someone who cannot see whether the
plug is seated waited up to a minute for the answer. Measured on 2026-08-21:
Stephan pulled the cable and plugged it back in within a minute - at a 60 s
interval not a single check fell in the window where it was disconnected, and
no log line appeared in 130 s. What is checked less often than it happens gets
missed. The price is two tiny files more per check; the earlier two intervals
(60 s, dropping to 20 s below 10 %) are gone without replacement.

**Every change is logged, in both directions.** The first version only wrote
"Netz getrennt"; reconnecting was only logged if a warning had been given
before. Found on 2026-08-21 when Stephan pulled the cable to try it out and
plugged it back in - the log read "Netz getrennt bei 77 %" with no end to it.
For a sighted helper looking later, that is half the story.

The whole chain was tested against a **simulated power supply** (a `/sys` tree
in scratch space) rather than waiting for a genuinely flat battery:
unplugging, 24 %, 20 % with no second message, 14 %, 4 %, plugging in with
confirmation, and a jump from 60 % straight to 3 % that says "almost empty"
and not "25 percent".

**Once per discharge**, and skipped levels count as done: if the device drops
from 30 % to 4 % while suspended, "almost empty" is the right announcement, not
"25 percent". During a dictation 25 % and 15 % wait; the 5 % speaks anyway,
because an interrupted sentence is better than a device that dies mid-letter.
And someone who cannot see whether the plug is seated gets a short confirmation
after plugging in.

As a **systemd user service** with `Restart=always`, not via
`/etc/xdg/autostart` like the other DialOS services - the same reasoning as for
the LanguageTool service: if it fails, nobody notices until the device goes off,
and then the failure is indistinguishable from a flat battery. A user service
and not a system service, because it speaks and speech output hangs off the
session. The warning is also the **sixth source** of the live transcript
(`dialos-akku.log`).


## Every letter as a PDF in the archive (new 2026-08-22)

Stephan's requirement from 2026-08-21: "every letter and every mail must be
put into a separate folder as a PDF file."

```bash
sudo /usr/local/sbin/dialos-aufspielen --wirklich   # or install by hand
```

**Where: `~/Dokumente/Archiv/DialOS-DATA/` — and on the stick.** The name is
Stephan's choice so that both places are called the same thing.

**Until 2026-08-22 this said the opposite**, and the reasoning was not wrong:
the `DIALOS-DATA` partition is unencrypted exFAT, per
`sicherheit-datenschutz.md` the stick is meant to be kept apart from the
laptop, and letters to a health insurer do not belong from the LUKS disk onto
an open medium.

**Stephan decided otherwise** ("alle pdf Dateien … müssen unbedingt auf den
Stick Bereich DialOS-DATA und unter Dokumente auf den Rechner unter
Dokumente/Archiv/DialOS-DATA"). His reason outweighs mine: an archive that
only lives on the disk is gone with the next disk failure, and the user cannot
back it up himself. The encryption question is untouched by this and belongs
in `sicherheit-datenschutz.md`, not in a silent refusal here.

An archive that is usually not plugged in still cannot be written to — so
**`dialos-archiv.py` catches up** as soon as the stick appears: the disk
always holds everything, the stick everything added since it was last
plugged in.


**The admin has no stick — and that is not a shortcoming.** Stephan's decision
of 2026-08-24: "Beim Admin brauchen wir den Stick nicht, stell die Meldung ab.
Und wir simulieren beim Admin den Stick mit einem Verzeichnis unter
Dokumente/Archiv/DialOS-DATA. Den haben wir ja dafür angelegt!" So for
`dialosadmin` the folder on disk is not a staging area for the stick but the
archive itself. `dialos-archiv.py` neither looks for a stick there nor
complains about one (list `OHNE_STICK` at the top of the script).

**"Brief als PDF speichern" (since 2026-09-15)** uses the same PDF generator
but without archiving: `dialos-archiv.py pdf FILE TARGET`, called by
`dialos-notiz.py brief pdf`. The target is the PDF with the same name next to
the newest letter.

**Footer at the very bottom, small, with slogan (since 2026-09-17).** Stephan:
the sentence must always be the last line on the page, may be smaller so it does
not distract, plus logo and slogan. `als_pdf()` takes the footer out of the text
flow and puts it at the bottom of **every** page: 7 pt grey on the left,
`fuss-slogan.png` on the right (copy of `assets/slogan.png`: "Dein Alltag. Deine
Stimme. Dein System." with logo, 4.4 mm high). `dialos-drucken.py` therefore
prints **everything** via this PDF, shopping lists and notes too - CUPS text
printing put the line right below the last entry.

```bash
sudo install -m 644 iso-build/config/includes.chroot/usr/local/share/dialos/fuss-slogan.png /usr/local/share/dialos/
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-archiv.py iso-build/config/includes.chroot/usr/local/bin/dialos-drucken.py /usr/local/bin/
```

**The letter as a PDF following DIN 5008 (since 2026-09-17, wired in).** `als_pdf()`
in `dialos-archiv.py` recognises a dictated letter sheet by the note "Dieser Brief
wurde per Spracheingabe …" and hands it to `dialos-brief-din.py`
(`briefbogen_als_pdf`). Since the archive, "Brief als PDF speichern" and "Brief
drucken" all call this function, paper, PDF and archive look the same. If DIN
typesetting fails, the PDF is created in fixed width as before (message in the
archive log). Lists and notes stay fixed width. The layout after Stephan's verdict
on two previews:
- **no letterhead** ("I don't like the head"; `KOPF = "name"` would put the name
  centred at the top),
- **address field** form B: return address without address suffix and country
  ("Stephan Rösner · street · postcode town" fits the 80 mm completely - with the
  floor it was cut off), below it the recipient from the dialogue,
- **information block** on the right: name, address (street, postcode town,
  country - without floor), phone/mobile, email, date as **17.09.2026** (from the
  date line of the letter sheet, i.e. the date of dictation, not of printing). The
  first line sits **on the baseline of the return address** (Stephan: "at the same
  height"),
- subject in bold without "Betreff:", fold and punch marks, footer with slogan; the
  text starts at 98.5 mm or two lines below a longer information block; closing,
  name and note stay on one page, from two pages "Seite 1 von 2".

Personal data come from the logged-in account. Checked: letter with and without
recipient, two-page letter, account without data file, list (fixed width).

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-brief-din.py iso-build/config/includes.chroot/usr/local/bin/dialos-archiv.py /usr/local/bin/
```

**File names with date and time (since 2026-09-15, Stephan's requirement "for
searching").** Letters are named `2026-09-15-1343-Brief.txt` (and `.pdf`),
screenshots `2026-09-14-1018-Bildschirmfoto.png`; two in one minute get `-2`.
"The letter" is the newest. The rule lives in ONE file, `dialos-dateiname.py`,
loaded by dictation, note handling, printing and screenshots. Old names
(`brief.txt`, `brief-STAMP.txt`, `bildschirmfoto-…png`, GNOME's `Bildschirmfoto
vom …png`) are converted on first access - also in the encrypted user account,
which an admin script could not get into. By hand: `dialos-dateiname.py
umstellen`.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-dateiname.py /usr/local/bin/
```

**Personal data (since 2026-09-16).** One form for name, address, contact,
signature, bank and emergency contact - filled in once per account in
`~/.config/dialos/persoenliche-daten.txt` (0600). Letters (sender, name under
the closing), names and weather read from it; without the file the old way
applies. Fields and decisions: [kundendaten-felder.en.md](kundendaten-felder.en.md).

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-persoenliche-daten.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/usr/local/share/dialos/persoenliche-daten-vorlage.txt /usr/local/share/dialos/
```

In the person's account: `dialos-persoenliche-daten.py anlegen`, fill it in,
then `dialos-persoenliche-daten.py pruefen`. **Never put the file into the
repo.**

**Recipient dialogue and Thunderbird contacts (since 2026-09-17).** Stephan: dictate
the recipient's address and store it "automatically as a contact in Thunderbird";
his choice: guided dialogue, search known contacts first. After "Brief schreiben"
and loading the models, `dialos-diktat.py` asks "An wen geht der Brief?" - found in
the Thunderbird contacts → read the address, yes/no; otherwise street and house
number, country (only if not the own one from the personal data), postcode and
town, then read the whole address (postcode digit by digit) and "Stimmt das?".
Answers are heard by Vosk (end of answer: 1.2 s of silence) and Parakeet
(spelling); yes/no by the small model with a grammar. "Ohne Empfänger" or no
answer: letter without address. House number and postcode always as digits (also
"fünf a" → "5a", "eins zwei sechs zwei neun" → "12629", length by country). In
the letter sheet the recipient stands on the left between sender and date; "Brief
vorlesen" names it, the DIN draft puts it in the address field.

`dialos-empfaenger.py` reads and writes the Thunderbird profile's address book
`abook.sqlite` (card as vCard 4.0 in `_vCard`, plus `DisplayName`, `FirstName`,
`LastName`). **It only writes while Thunderbird is not running**; otherwise the
contact goes to `~/.config/dialos/kontakte-neu.json` and `dialos-kontakte.service`
adds it at login. Checked with a Piper voice (new recipient abroad, found contact,
no recipient); test bench unchanged.

**After the first trial (2026-09-17, 13:00):** "Gesobau" arrived as "Visual" and "G
so bau" - and sounded right when read back. Hence: (1) after a new name DialOS
asks "Soll ich ihn buchstabieren?", reads it in the **spelling alphabet**
("Gustav. Emil. Samuel. …") and lets it be dictated that way if needed - measured
Piper → Vosk: letter names 15/26, alphabet 26/26. (2) The contact search also
compares the **sound** (Kölner Phonetik, legal forms like "AG" ignored): "G so
bau" finds "GESOBAU AG". (3) First and last name only with "Herr/Frau/Dr." at the
start, otherwise company. (4) No answer ends the dialogue (letter without
address). The personal dictionary also applies in the dialogue. In dictation:
dates with the month as a number ("31.08.2026", also Parakeet's
"einunddreißigten"), year "zwanzig fünfundzwanzig" → "2025", amount parts
swallowed by Parakeet taken from Vosk ("322 Cent" → "322,40 Euro"). "Brief
vorlesen" without sender (it comes from the data), phone numbers digit by digit
in blocks of three, then "Du kannst sagen: Brief drucken oder Brief als PDF
speichern." Test bench: new case `brief-zahlen-2` 1.7 %, none worse.

**After the second trial (13:36):** Stephan: if Gesobau is not understood he has no
way to change it, and he cannot restart the letter or simply end the dictation.
His "Diktat beenden" became the street "Um die Tat beenden". Now: after the name
DialOS asks "Stimmt das? Sage ja, nein oder buchstabieren." - "nein": say the name
again; "buchstabieren": DialOS reads it in the alphabet and lets it be spelled;
also as the answer to "An wen geht der Brief?". **At any time** "abbrechen" /
"Diktat beenden" / "Brief abbrechen" (no letter) and "von vorne" (restart the
dialogue) apply, in free answers as well as yes/no and spelling. The contact
search uses Vosk and Parakeet text and compares sound more generously, but only
for keys of similar length ("wieso bau" → GESOBAU AG, "Sparkasse" not).
Simulated: name corrected by spelling and found in the address book, abort at
the street, "von vorne" followed by "ohne Empfänger". Claude corrected the contact
"G so bau" to "GESOBAU AG" (company) at Stephan's request; Thunderbird shows
externally created and corrected contacts (confirmed on the device).

**Third trial (13:49):** "Gesobau" arrived as "jesu bau" and was found in the
contacts by sound, confirmed, letter with recipient. Newly found: "Tag, Absatz mit
freundlichen Grüßen." - an "Absatz" in mid-sentence before a closing or
salutation is now always the command (otherwise the closing stayed in the
sentence and the signature from the data did not apply). Test bench unchanged.

**Fourth trial (14:15):** name corrected ("Gizzle ball" → nein → GESOBAU AG found),
"abbrechen" in the dialogue ✓. New: (1) amounts - Parakeet wrote "12 Euro und
vierzig" for Vosk's "dreihundert zweiundzwanzig euro und vierzig cent": if only
Vosk hears "cent", Vosk's whole amount applies. (2) In **dictation** there are now
**"von vorne"** (discard what was dictated, the recipient stays) and **"alles
verwerfen"** (save nothing), both with a yes/no question and the same safeguards
as "Satz löschen". A separate third recogniser (`GRAMMATIK_STEUER`): in the
closing grammar the small model heard "Diktat beenden" as "diktat vorne", and a
letter on the test bench no longer ended. Not "Diktat abbrechen" - it sounds like
"Diktat beenden", and one command saves while the other discards. Simulated: von
vorne, alles verwerfen, Diktat beenden - each right; test bench 9 cases as before.

**Fifth trial (15:00):** "von vorne" ✓. "Alles verwerfen" landed in the letter
twice: (1) the large Vosk model heard "alles verlaufen" - the cross-check now also
looks at Parakeet's text ("Alles verwerfen."). (2) At the same moment the closing
recogniser heard "satz wiederholen" and overwrote the pending command. Now the
first one stays, the second becomes an alternative, and free recognition decides
(`befehl_vormerken`/`befehl_entscheiden`, also between a command and the closing
phrase). (3) "322 Euro und 40 Cent" becomes "322,40 Euro"; if Parakeet swallows
"Euro" ("dreihundersundzwanzig und vierzig Cent"), Vosk's amount applies. The real
recording replayed: both "alles verwerfen" with a question, amount 322,40 Euro; with
"ja" dictation ends without a file. Piper simulation and test bench unchanged.

**Sixth trial (15:20):** "alles verwerfen" → nein → continue, and → ja → nothing
saved, both ✓; a simultaneously heard "satz löschen" correctly discarded. Amounts
"3675,75 Euro" and "1746,78 Euro" ✓. Newly fixed: "31.05. 2027" (year spoken in two
parts) → "31.05.2027". Open: a chunk without a sentence end runs into the next
sentence ("… 2027 In ihrem Schreiben").

**Seventh trial (15:53) - contact person.** Stephan: "I couldn't add a contact
person to the address yet." After the name - new or from the contacts - the
dialogue now asks: "Gibt es einen Ansprechpartner? Sage den Namen mit Frau oder Herr
… Sonst sage: nein." Confirmation as for the name (ja, nein, buchstabieren); no
answer means none. If the recipient itself starts with Frau/Herr/Dr./Prof., the
question is skipped. Following DIN 5008 the line sits directly below the company,
without "z. Hd.", and only in the letter - the Thunderbird card stays the company's.
Also: "12345 in Musterhausen" → town "Musterhausen" (the "in" was not dropped).
Simulated with Piper: company from contacts with and without contact person, new
company with contact person, person without the question.

**Email addresses in dictation (2026-09-17).** Stephan: "The system can't cope with
an email address either." Spoken freely, Vosk heard the domain as "geit o s t",
Parakeet as "guides" - an unknown address is never recognised reliably. Three ways,
Stephan's choice, none needs the address itself to be recognised:
- **"meine Mailadresse"** in a sentence ("unter meiner Mailadresse erreichen") - the
  email from the personal data goes after the words, also after "lautet"/"ist"; if an
  address is already there, nothing changes.
- **"Mailadresse von GESOBAU"** - the email from the Thunderbird card (search as in
  the recipient dialogue, up to three words after "von"). `kontakte()` now returns
  `mail` (vCard `EMAIL`). Without a match the text stays, message in the log.
- **"Mailadresse buchstabieren"** - command in dictation (third sentence in the
  control recogniser, cross-check "buchstab"): spelling alphabet plus at, Punkt,
  Minus, Unterstrich and digits, confirmation character by character, then the
  address goes to the end of the text - bypassing the writing aid. Parakeet's full
  stop on the chunk before is dropped, and the next chunk starts in lower case if
  hunspell knows the word in lower case ("… an ste@beispiel.de oder telefonisch").

A full stop inside an address does not count as a sentence end (Satz
löschen/wiederholen). "Brief vorlesen" reads addresses as "max at beispiel Punkt de".
The overview "Befehle für das Diktat" now also names von vorne, alles verwerfen and
the email address. Simulated with Piper; test bench 9 cases unchanged.

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-empfaenger.py iso-build/config/includes.chroot/usr/local/bin/dialos-diktat.py iso-build/config/includes.chroot/usr/local/bin/dialos-notiz.py /usr/local/bin/
sudo install -m 644 iso-build/config/includes.chroot/etc/systemd/user/dialos-kontakte.service /etc/systemd/user/
sudo systemctl --global enable dialos-kontakte.service
```

**Input form (since 2026-09-16, fixed part of the setup).** Stephan asked for "a
proper input form … also for a user I set up" and for it to be "a fixed part of
setting up DialOS". `dialos-persoenliche-daten-maske.py` (GTK 4, libadwaita)
builds itself from the template: sections, order, hints, salutation and Du/Sie as
choices. The account is chosen at the top. For its own account the form writes
directly; for another one it calls
`/usr/local/sbin/dialos-persoenliche-daten-konto` via `pkexec`, which
- only touches this one file in a person account (UID 1000-59999),
- reads and writes **as that account** (`runuser`) - as root it would follow a
  symlink placed by the account,
- refuses (exit 3) if `/etc/fstab` mounts the home directory separately but it
  is not mounted - otherwise address and IBAN would land unencrypted on the root
  partition.

The polkit action `org.dialos.persoenliche-daten` requires the admin password
(`auth_admin_keep`: loading and saving ask only once). The form is only in the
admin account's menu. New packages listed explicitly: `python3-gi`,
`gir1.2-gtk-4.0`, `gir1.2-adw-1` (previously pulled in by GNOME).

```bash
sudo install -m 755 iso-build/config/includes.chroot/usr/local/bin/dialos-persoenliche-daten-maske.py /usr/local/bin/
sudo install -m 755 iso-build/config/includes.chroot/usr/local/sbin/dialos-persoenliche-daten-konto /usr/local/sbin/
sudo install -D -m 644 iso-build/config/includes.chroot/usr/share/polkit-1/actions/org.dialos.persoenliche-daten.policy /usr/share/polkit-1/actions/org.dialos.persoenliche-daten.policy
sudo install -m 644 iso-build/config/includes.chroot/usr/share/applications/dialos-persoenliche-daten.desktop /usr/share/applications/
```

In the setup run: `dialos-full-office-setup.sh` step 12 installs everything,
`dialos-buero-setup-abschliessen.sh` step 6/6 puts the launcher on the desktop
and opens the form for `nutzer` - while `/home/nutzer` is mounted, i.e. before
the reboot.

**Why this was needed.** exFAT is mounted with the `uid`/`gid` of whoever
mounts it. On a device with two accounts that means: whoever plugs the stick in
first owns it, and the other account cannot even read it. Measured on
2026-08-24: `uid=1001,gid=1001,dmask=0022`, for `dialosadmin` "permission
denied". That is not a misconfiguration but how GNOME mounts removable media.
Before this, the archive therefore wrote "Stick unter
/media/nutzer/DIALOS-DATA, aber nicht beschreibbar" **every 16 minutes** — a
message nobody reads and that changes nothing.

**For the user the message stays.** There, a stick that cannot be written to is
a real fault: their backup copy does not come into existence.

### The voice choice is running state, not configuration

**A mistake from 2026-08-24 that shows how easily this is missed.**
`/etc/speech-dispatcher/modules/piper-generic.conf` holds two different things:
how the Piper module is invoked — that is configuration and belongs in the repo
— and `DefaultVoice` plus `GenericRateMultiply`, that is, the voice the user
chose. `dialos-stimme.py` writes into exactly that file.

On 2026-08-22 at 15:21 Stephan had switched to Michael with the keyboard
shortcut. The next `dialos-aufspielen` silently reset that choice to the repo's
version — while `assistent-name.txt` still said "Michael". The device would
have introduced itself **as Michael in Anna's voice**. Precisely the fault that
already happened on 2026-08-19.

The file is therefore now in `dialos-aufspielen`'s `NIEMALS` exclusion list,
alongside the Bluetooth pairing data for the same reason. Anyone who really
wants to change it (a new Piper invocation, different module parameters)
installs it deliberately by hand.

**And the script now says what it passed over.** Until then, excluded files
vanished silently — the same fault as a voice command without feedback: hear
nothing, assume it worked. The message is grouped by **reason** and names at
most three paths per reason; the first draft listed 29 files, 20 of them Python
bytecode, and buried the one that mattered. That is why every `NIEMALS` entry
now has a third column: *is this omission worth reporting?*

**Why an own PDF writer and not LibreOffice.** The letterhead is laid out with
**spaces**: sender and date are right-aligned because the line is padded to
width 76. In a proportional font that falls apart immediately, and LibreOffice
imports plain text with its default font. With `cairo` (present in Debian) a
**monospace** font can be set — the alignment stays exactly as intended. It is
also faster: no office suite to start.

**Proven, not assumed:** the generated PDF was read back with `pdftotext
-layout` and compared line by line with the text file. Every line matches
character for character; the only deviation is one extra space introduced by
`pdftotext` itself.

**The archive must not hold up the letter.** It is started concurrently, and
if it fails that goes into the log — the letter has already been written as a
text file.

**The mail half is still missing**, for a reason that has nothing to do with
the archive: DialOS does not send mail itself yet. As long as that runs
through Thunderbird there is no point at which DialOS could step in. The note
sits in `TODO.md` at the item where the own sending path gets built.


### Mail in the archive - without a password (new 2026-08-22)

Stephan's addition the same day: "can we also put all incoming and outgoing
mail in there!"

**The obvious route would be IMAP - and it is ruled out.** It would need the
mailbox credentials, which do not exist in any readable file on this device
yet, and it would be a second way into the mailbox. But Thunderbird keeps
local copies in real mbox format:

```
~/.thunderbird/<profile>/ImapMail/<server>/INBOX
~/.thunderbird/<profile>/ImapMail/<server>/Sent
```

Those files are already there. **No password, no network, no new place where
credentials live.**

`dialos-mailarchiv.py` reads them, decodes the headers (`=?UTF-8?B?...`
becomes text again), takes the `text/plain` part and files each mail as a PDF -
with a header block of From, To, Date, Subject and the attachment names. If
only HTML exists it is crudely stripped; for an archive the wording is what
counts.

**Each mail only once.** What is remembered is the `Message-ID` in
`.archivierte-mails.txt`, not the file name: with the same subject on the same
day the name would collide, the ID never. Proven - the second run reported
"4 already archived, 0 new".

**Drafts stay out.** A draft was neither received nor sent, and it still
changes.

**Every 15 minutes**, via `dialos-mailarchiv.timer`. Not more often, because a
mail arriving in the archive a quarter of an hour later is no problem; not
less often, because a mail just written should be findable there.

**The price, stated openly:** the local store contains only what Thunderbird
has fetched. A mail never opened has no text there - then the PDF says so
instead of producing an empty page. A complete archive only comes with the own
IMAP path.


### Screenshot: DialOS enters the permission itself (2026-09-14)

**The bug.** Stephan on 2026-09-14: he wanted to take screenshots, but the
command did not work. Recognised four times, four times "Ich konnte kein
Bildschirmfoto machen", in the log `Portal antwortete mit 2` or no answer at
all. On 2026-08-21 and 22 it had worked six times.

**The cause.** The XDG portal only delivers a picture without a prompt if the
permission store (table `screenshot`) holds a permission **for the calling
program**. It reads which program that is from the process's systemd unit.
Exactly one permission was stored: for `com.anthropic.Claude`, created on
2026-08-21 at 14:39 - one minute before the first successful screenshot. Back
then the voice service ran inside Claude's unit, because it had been restarted
from there. After the reboot on 2026-09-14 autostart launched it, and since
then the portal knows it as `dialos-sprachbefehl-desktop`. There was no
permission for that, and the prompt can never appear:

    Failed to show access dialog: ... Only the focused app is allowed to show
    a system access dialog

**Proven, not assumed** - with a silent portal call that deletes the test
picture right away:

| Called from | Permission | Result |
|---|---|---|
| Claude's unit | `com.anthropic.Claude` | picture |
| unit `app-gnome-dialos\x2dsprachbefehl\x2ddesktop-…` | none | response 2 |
| same | `dialos-sprachbefehl-desktop` | picture |
| same | `""` | response 2 |

**The fix.** Before the call, `dialos-bildschirmfoto.py` determines its own ID
from `/proc/self/cgroup` and enters the permission if it is missing - **only
for IDs starting with `dialos-`**. The permission store belongs to the account
and has no access control; entering it is the equivalent of clicking "Allow",
which the user cannot do. Checked: without a permission it was entered and a
picture came; a second call enters nothing twice; a foreign ID gets nothing
and still fails with 2. Takes effect immediately for the running voice
service, because it calls the script anew for every command, and for every
account on its first screenshot.

**Fixed on the side:** the voice service logged `Bildschirmfoto erstellt` even
when no picture was taken. The entry now follows the return code.

**The lesson, and it reaches beyond the screenshot: a service restarted from
Claude's session is not a test under customer conditions.** It inherits
Claude's unit and with it Claude's permissions. Proof only comes from a start
via autostart - after login or a reboot. In the code the screenshot is the only
path through a portal (searched for portal, PermissionStore, org.gnome.Shell,
busctl, notify-send, secret-tool); the greeting's location lookup goes through
geoclue with a fixed permission in `/etc/geoclue/geoclue.conf`, not through
the permission store.

## Where things live — for the sighted helper (as of 2026-08-22)

Stephan's reminder the same day: "always remember, we have sighted users too."
That applies to the logs: since today they live in `~/.log/` and are therefore
**invisible** in the file manager. For the user that makes no difference — he
sees nothing anyway. For the helper sitting next to him, a folder he cannot
see is an obstacle. So here is where everything is:

| What | Where | Visible |
|---|---|---|
| Program logs | `~/.log/` | **no** (leading dot) |
| PDF archive, letters and mail | `~/Dokumente/Archiv/DialOS-DATA/` | yes |
| The same on the stick | `<DIALOS-DATA>/DialOS-Archiv/` | yes, once plugged in |
| Letters as text | `~/Dokumente/` | yes |
| Notes and shopping list | `~/Notizen/` | yes |
| Screenshots | `~/Bilder/Bildschirmfotos/` | yes |

**Why the logs are hidden** (Stephan's wish): previously 25 files sat openly in
the home folder — ten live and fifteen rotated — among `Notizen`, `Dokumente`
and `Bilder`. That is exactly the clutter in which a helper fails to find what
he is looking for.

**Anyone doing support rarely needs them.** The live transcript window shows
the same thing as it happens, and the support log summarises what occurred.
The raw logs are the case where neither is enough.

**The folder may be deleted.** Every script recreates it when writing; only the
past would be lost. `logrotate` clears it after seven days anyway.


### Keyboard shortcuts for the admin account

Stephan's request of 2026-08-22: two keys that switch without having to
speak - when demonstrating, developing and checking, that is the faster way.

| Key | What happens |
|---|---|
| `Ctrl`+`Alt`+`W` | Look: Linux ↔ Windows 11 |
| `Ctrl`+`Alt`+`S` | Voice: Michael ↔ Anna |

**For `dialosadmin` only.** The user account does both by voice. A keyboard
shortcut there would be a path nobody finds and everybody triggers by
accident.

They are set by `scripts/dialos-admin-tastenkuerzel.sh` (no sudo - the
settings belong to the user), as step 11c of the office setup. The script
checks first whether the targets are executable at all: better no key than
one that does nothing - press it once with no effect and you never press it
again. `zeigen` lists the current state, `entfernen` removes both.

**Both scripts toggle rather than demand a target.**
`dialos-desktop-stil.sh umschalten` reads the remembered style and takes the
other one - not the state of the loaded extensions, which can be half loaded
mid-switch. `dialos-stimme-wechseln.py` takes the NEXT voice from the list in
`dialos-stimme.py`, not "the other one": with a third voice, "the other one"
would no longer be unambiguous.

**Why the voice needs a script of its own.** `dialos-stimme.py setzen` only
does half the job: it writes the Piper configuration - which needs root - and
then tells the human to restart speech-dispatcher. At a terminal that is
reasonable; behind a key it is not. The new script therefore runs WITHOUT
root and splits the work: the privileged part via `sudo`, the
speech-dispatcher restart itself - root could not touch the logged-in user's
service at all. The same split as in `dialos-aufspielen`.

It comes with `/etc/sudoers.d/dialos-stimme` (0440 root:root). The rule names
two calls verbatim, with their argument, no wildcards:

    dialosadmin ALL=(root) NOPASSWD: /usr/local/bin/dialos-stimme.py setzen thorsten
    dialosadmin ALL=(root) NOPASSWD: /usr/local/bin/dialos-stimme.py setzen kerstin

A `setzen *` would be the gap something else fits through later. A third
voice therefore needs a third line - deliberately: whoever adds a voice
should trip over this file.

**Reviewed and approved by Stephan on 2026-08-22** ("Regel passt so, lass sie
drin" - the rule is fine, leave it in). This is recorded because the project
has committed to never letting a sudoers rule reach a device unseen - and a
review nobody can point to is not one.

Measured on 2026-08-22: the voice switches in 4.4 seconds, announcing itself
in the new voice, in both directions. The look switches without delay.








### When nothing matched, DialOS now says so

**Until 2026-08-24 an utterance that was not a command did nothing - and
nothing was said either.** For a blind user that is the worst outcome: he has
spoken, the device has listened, and nothing tells him that nothing happened.
He does not even know whether he said it wrongly or the device is broken.

**I argued against it** - 283 announcements would be nagging. Stephan went
through the 283 recorded cases and refuted that: "Daran kann ich mich erinnern,
das waren alles Befehsversuche" - all 283 were attempted commands. So the
announcement would have been right in 283 out of 283 cases.

**The form follows from his second sentence:** "Ich muss selbst die genauen
Befehle erst lernen und dann wundere ich mich, dass ein anderer nicht
funktioniert. Auch für mich eine Lernphase." So the announcement does not
merely report a failure, it names the correct sentence:

    Ich habe verstanden: datum haben wir.
    Der Befehl heisst: welches datum haben wir.

With a weak match, only the first half plus "Das war kein Befehl."

**No question form, and that matters.** "Meintest du: welchen Tag haben wir?"
invites a "ja" - and DialOS does not process that "ja". It would have built a
new silent failure in order to heal an old one.

**Three numbers, all measured and none chosen:**

- **Two thirds** of a command's words must be present for it to be named. In
  51 % of the 283 attempts only *half* matched - a suggestion from that little
  overlap would often be wrong, and a wrong suggestion is not neutral for a
  blind user: it **teaches** a command that does not exist. From two thirds
  upwards it covers 34 % of cases.
- **Ten seconds** between two announcements. Of 277 consecutive occasions,
  **48 % were less than 5 seconds apart** and 68 % less than 10, median 6.
  Without a brake the device would talk almost continuously through a failing
  session, and since each announcement itself takes two to three seconds they
  would pile up. Ten seconds lets roughly every third occasion through.
- **At least two words**, no `[unk]`. Single-word fragments ("wir", "es",
  "auf") are not attempted commands - those were not put to Stephan in the
  sample either. An `[unk]` means something else was in the room; the device
  would be talking into a conversation.

**Destructive commands are never suggested.** `einkauf erledigt` and
`einkaufszettel wegwerfen` are on an exception list. A suggestion is a
recommendation, and for those the device must recommend nothing - least of all
to someone still learning the commands who cannot read the consequence off a
screen. Verified: `viel wegwerfen einkaufszettel` contains **both** words of the
delete command and is still not named.

Every announcement is logged, and so is every suppressed one - with the reason.

### A complete command with one word too many now counts

**Matching was an exact comparison** (`if satz in DRUCK_SAETZE`). One word too
many and the complete command fell through. Measured against 283 recorded
utterances - which Stephan **confirmed on 2026-08-24 were all attempted
commands** ("das waren alles Befehsversuche") - 21 contained the complete
command and still did nothing:

    'auf windows umschalten windows'   →  auf windows umschalten
    'notiz notiz drucken'              →  notiz drucken
    'wir notiz aufnehmen'              →  notiz aufnehmen

**Why the limit of two extra words is not negotiable.** Without a limit the same
rule would have executed word salad four times, and the most sensitive command
at that:

    'es wir auf machen welchen tag haben tag haben wir einkauf erledigt
     bildschirmfoto es drucken notiz uhr notiz datum gnome es uhr wir …'
         →  einkauf erledigt      (the shopping list would be gone)

| extra words allowed | rescued | of those, word salad |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 8 | 0 |
| **2** | **10** | **0** |
| 3 | 13 | 0 |
| 5 | 16 | 0 |
| no limit | 21 | **4** ← tips over |

Two is deliberately not an optimum but the conservative edge. At 5 there would
have been no salad in *this* recording either - but a recording is no guarantee.
Anyone raising the number should measure afresh: the expensive fault here is not
the unrecognised command but the wrongly recognised one.

**Three conditions, all required:**

- **Contiguous**, not merely "all words occur". Otherwise
  `wie viel wir viel wegwerfen` would count as "throw the shopping list away".
- **Exactly one** match. With two it is unclear what was meant, and guessing
  would be worse than doing nothing. That happened exactly once.
- **No `[unk]`** - the same argument as in `ist_phrase()`.

**Not applied to switching on and off.** Those two sentences keep their
narrower check (`ist_phrase`), which has been adjusted repeatedly and brought
false starts down from 30 to 7. That is why the new rule fires in 8 cases rather
than 10: the two "Sprachsteuerung stoppen" are deliberately left out.

Verified against all 283 recordings: 8 are matched; word salad, ambiguity and
`[unk]` do not get through. Every match is logged - `als 'notiz drucken'
zugeordnet (+1 Wort zu viel)` - so that what the loosening actually does stays
traceable.

### Pronunciation rules are now per voice

**Stephan's decision of 2026-08-24:** "Michael lassen wir wie bisher und bei
Anne die Variante 2" - Michael stays as he was, Anna gets variant 2. Every rule
in `AUSSPRACHE` therefore has a fourth field: the voices it applies to, or
`None` for all.

| Voice | "DialOS" is read as | Word duration |
|---|---|---|
| Anna (`de_DE-kerstin-low`) | `Dial O S` | 0.47 → 0.64 s |
| Michael (`de_DE-thorsten-high`) | `Dial OS` | unchanged, 0.98 s |
| any other | `Dial OS` | fallback |

The order in the list is **not arbitrary**: specific before general. For Anna
the first rule fires, after which the general one finds nothing.

**How the choice came about, so nobody works through it again.** Piper knows no
*middle* pause. Measured on Anna's voice:

| Spelling | Silence | Word duration |
|---|---|---|
| `Dial OS` | 0 ms | 0.47 s |
| `Dial, OS` | 0 ms | 0.53 s |
| `Dial - OS` | 0 ms | 0.46 s |
| `Dial; OS` / `Dial: OS` / `Dial ... OS` | 0 ms | ~0.45 s |
| `Dial O S` | 0 ms | **0.64 s** |
| `Dial. OS` | **220 ms** | 0.70 s |
| `Dial? OS` | 230 ms | 0.71 s |
| `Dial! OS` | 290 ms | 0.69 s |

Only sentence-ending punctuation produces silence. The period even matched
Stephan's own speaking pause - measured from a recording of his voice: **105
and 180 ms** - but it turned the word into two sentences, with the melody
falling after "Dial". His verdict: "das zweite ist ja alles aber nicht das Wort
DialOS". `Dial O S` therefore inserts no silence but speaks the letters singly.

**The sample generators must pass the voice.** `fuer_sprachausgabe` now takes a
second parameter. `dialos-alle-ansagen.py` and `dialos-vorstellung.py` pass the
identifier through - without it Michael's file would get Anna's pronunciation,
unnoticed, because both sound right on their own. That very confusion has
happened here before, back then with the voice itself.

### A fault the rebuild surfaced: at the end of a sentence the rule did nothing

The lookahead was `(?!\.)` and was meant to protect `dialos.org`. But it
excluded **any** following period - including the full stop of a sentence:

    Willkommen bei DialOS.   →   unchanged, read as one word
    DialOS ist bereit.       →   Dial OS ist bereit.

The most common case was the broken one. It surfaced only because **both
sentence positions** were checked while fitting the new rule. Now
`(?!\.[A-Za-z])`: a period counts as part of the word only when a letter
follows. That covers `dialos.org` and spares the full stop.

### A muted paplay makes the device silent - with no error

**Found on 2026-08-24 because Stephan said "ich höre nix" during a listening
test.** The `paplay` stream was **born muted**:

    Sink Input #602
        Mute: yes
        module-stream-restore.id = "sink-input-by-application-name:paplay"

PipeWire remembers volume and mute **per application**, persistently and across
reboots. Mute a `paplay` stream once without releasing it and every future
`paplay` is silent.

**Why this is more than a failed listening test.** DialOS plays via `paplay`:
the question tone, the silent probe tone for output selection, **and cached
announcements** (`dialos-say.py`, `aus_speicher`). All cached announcements
would be silent. And `paplay` returns **0** in that case — `aus_speicher()`
considers the announcement successful and does **not** fall back to `spd-say`.
The device would be mute for a blind user without any error anywhere. He would
have no way to find the cause, and we none to see it in the log.

**How it happens.** `dialos-say.py` mutes other streams while it speaks and
releases them in a `finally`. Two gaps:

1. With two announcements in quick succession, the second sees the first's
   `paplay` stream and mutes it.
2. A `finally` does **not** run on SIGTERM - Python's default terminates the
   process at once. Kill an announcement and the mute stays in PipeWire's
   store.

**Fixed in both directions:**

- `ist_eigener_ton()` excludes streams of the application `paplay` from
  muting. The price: were a foreign application playing music through
  `paplay`, it would not duck during an announcement - the cheaper fault.
- Signal handlers for SIGTERM, SIGINT and SIGHUP turn the signal into an
  exception so the cleanup runs. Evidenced: exit code **143** instead of -15,
  and the speaking marker is not left behind. That matters in its own right -
  a stale marker keeps the voice-command service from listening for good.

**Repair, should it recur** (the store can only be changed through a live
stream):

    paplay SOMEFILE.ogg &
    pactl set-sink-input-mute $(pactl list sink-inputs | awk '/Sink Input #/{i=$3} /application.name = "paplay"/{print substr(i,2); exit}') 0

**What stays open:** there is no self-check. A device that has stopped speaking
does not report it - see `TODO.md`.

### The level is now in the log for every recognition

**Measured on 2026-08-24, after the voice control switched itself on.** Twenty
minutes of listening on the same source with the same grammar as the service
produced four notable results — and two numbers that rule out one line of
attack before it gets built:

| Time | Result | Level (RMS) | Confidence |
|---|---|---|---|
| 15:25:48 | `sprachsteuerung` | **30** | 1.000 |
| 15:28:10 | `[unk] [unk] starten` | **28** | 0.979 |
| 15:28:14 | `[unk] [unk] starten` | 5552 | 0.631 |

This room idles at **52**, and speech measured between 3475 and 4196 in the
dictation tests. So Vosk built whole command words out of something **quieter
than silence** — and was more confident about those than about the loud case.

**That disposes of confidence as a filter.** In a grammar holding a single
phrase the recogniser is confident by construction: it has no alternative
except `[unk]`. A confidence threshold would have discarded the loud, genuine
case and let the quiet ghosts through — exactly backwards.

**None of the four would have switched on**, and that is the good news:
`sprachsteuerung` lacks its second word, and the others contain `[unk]`. The
rule "core word AND no `[unk]`" held. The measuring tool did not reproduce that
rule in its first draft and therefore reported four "false starts" that were
none — since corrected; it now separates "notable" from "would have switched
on".

The service now records the **peak level since the previous result** with every
recognition. When the next genuine false start happens, the log will show
whether a level threshold would have prevented it. Until then none gets built.

**Careful when comparing:** the service writes the PEAK amplitude, while the
measuring tool and `dialos-diktat.py` compute RMS. The numbers are not
comparable with each other; that is why the log says "Spitze".

### What was spoken goes into the log

**Since 2026-08-24 — and the trigger was a gap in my own reasoning.** After the
false start at 14:41:12 I claimed DialOS had not spoken at that time, citing
`dialos-ton-ausgabe.log`. But that only records **device changes**, not
announcements. My statement was therefore not established, merely not
refuted — a difference that has already been expensive twice in this project.

`dialos-say.py` now writes to `~/.log/dialos-say.log`, with date and time, and
questions marked `FRAGE`. Without that file the first suspect in any false
start — the device's own announcement, should echo cancellation fail — can
neither be confirmed nor ruled out.

**The text is truncated at 120 characters**, and that is a data-protection
decision, not thrift: for a read-aloud command the announcement would be the
whole document. A full transcript of every announcement would be a verbatim
record of the user, which nobody asked for. For the purpose — roughly when was
roughly what said — 120 characters suffice.

Logging never holds up speaking: if the write fails it is swallowed. An
announcement lost to a full filesystem would be the worse fault.

`logrotate` covers the file without any change — the rule matches
`dialos-*.log`.

### Logs carry a date, not just a time

**Since 2026-08-24, and the trigger was a false conclusion of mine.** Every
`melde()` wrote `%H:%M:%S` — the time only. logrotate rotates daily, but only
while the device is running. Leave it off for two days and three days end up in
**one** file, and nobody notices: the clock simply jumps backwards.

That is exactly what caught me. From `~/.log/dialos-sprachbefehl.log` I
reconstructed a sequence "from today", described an incident to Stephan —
thirteen failed attempts to switch on, a triggered print job — and drew
conclusions about usability from it. All of it was from **22 August**. It only
surfaced because Stephan replied that he had not spoken to the voice control
that day at all. Two backward jumps in the file (15:39 → 15:09 and
15:21 → 10:23) prove the three days.

Twelve scripts now write `%m-%d %H:%M:%S`. The format stays short enough for
the live transcript and makes a change of day visible.

**The lesson is not the format.** A log without a date is not a cosmetic flaw
but a trap for exactly the person reading it during support — under time
pressure. It cost me a whole line of analysis, and without Stephan's objection
a wrong conclusion would have ended up in the documentation.

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

## 13b. Cleanup: remove what Debian ships and DialOS does not need

Stephan's requirement of 2026-08-19: once Debian + GNOME is installed on a new
machine and the scripts have run, everything that came with Debian and is not
needed for DialOS should go. Hence this step here and not in day-to-day
operation - and **before** step 16, so the backup image holds the tidied system.

```bash
./scripts/dialos-aufraeumen.sh                  # shows only what would happen
sudo ./scripts/dialos-aufraeumen.sh --wirklich   # removes
```

**Why this is not simply `apt purge` - the dangerous part.** As soon as any GNOME
component is removed, the meta-packages `gnome`, `gnome-core` and
`task-gnome-desktop` go with it. That is unavoidable and harmless in itself. The
consequence is not: afterwards **49 packages** count as "automatically
installed" that were previously held only through `gnome-core` - among them
`gnome-shell`, `nautilus`, `gnome-settings-daemon`, `gnome-keyring` and
`pipewire-audio`. A later `apt autoremove` would offer to remove **the whole
desktop and the audio stack**. Measured on 2026-08-19 on the T490.

The script therefore **first** marks everything that should stay as "manually
installed" (64 packages) and only removes afterwards. It then explicitly verifies
that `gnome-shell`, `nautilus`, `gnome-settings-daemon`, `gnome-keyring`,
`pipewire-audio` and `gdm3` are still present, and exits with an error if not.

**And it runs no `autoremove`**, it only shows what one would offer. On a device a
blind user operates alone, that decision belongs to a human with a screen.

**What gets removed** (17 packages, 20 including the meta-packages):

| Tier | Packages | Reason |
|---|---|---|
| A - duplicates and foreign bodies | `gnome-characters`, `gnome-font-viewer`, `gnome-tour`, `malcontent-gui`, `xterm` | none of it has anything to do with DialOS |
| B - superseded | `gnome-music`, `gnome-podcasts` | Rhythmbox is the ONE player |
| | `totem`, `totem-plugins` | VLC stays as the only video player |
| | `gnome-contacts` | contacts are Thunderbird's job |
| | `gnome-clocks`, `gnome-weather` | DialOS says time and weather itself |
| | `gnome-maps` | purely visual |
| | `gnome-connections` | remote support is RustDesk |
| | `gnome-sound-recorder` | recording is DialOS's job |
| | `simple-scan` | no scanner in the build |
| | `shotwell` | the image viewer is enough |
| C - decided 2026-08-19 | `libreoffice-calc`, `libreoffice-impress`, `libreoffice-draw`, `libreoffice-math` | only **Writer** is specified (letters). Writer, `libreoffice-core` and `libreoffice-common` are demonstrably untouched - simulated before the decision. |

**Deliberately NOT removed**, although hidden for `nutzer`: `obs-studio` and
`gnome-snapshot` (video recording - the purpose is unresolved per
[anwendungen.en.md](anwendungen.en.md), and what is not decided is not thrown
away in advance), `yelp`, `baobab`, `gnome-software`, `seahorse` (can help during
support). `libreoffice-startcenter` also stays - with the consequence that it
then shows tiles for programs that no longer exist. A blemish for `dialosadmin`,
invisible for `nutzer`.

**Three "duplicates" canNOT be removed by package** - found on 2026-08-19,
because `dpkg -S` on the duplicate names the same package as the original:

| Menu entry | lives in | consequence of removing |
|---|---|---|
| `gnome-system-monitor-kde.desktop` | `gnome-system-monitor` | the real system monitor would go too |
| `mintstick-kde.desktop`, `mintstick-format-kde.desktop` | `mintstick` | both USB tools would go |
| `vim.desktop` | `vim-common` | `vim-tiny` depends on it - no more `vi` |

Those four are hidden per account in step 13c.

## 13c. Menu per account: nutzer sees their applications, dialosadmin sees all

Stephan's clarification of 2026-08-19: "If you are only hiding them, then tailor
it for the user; dialosadmin may show more, what I need for support."

```bash
./scripts/dialos-menue-pro-konto.sh                 # shows only
sudo ./scripts/dialos-menue-pro-konto.sh --wirklich
```

**Who the menu is actually for:** `nutzer` cannot see the screen - the menu is for
the **sighted helper** sitting next to them. And for that person a short list is
worth more than a complete one: they should find what belongs to the device at a
glance, not hunt between a formula editor and a font viewer.

**A whitelist, not a blacklist.** For `nutzer` everything not on the keep list is
hidden - not the other way round. A blacklist goes stale silently with every
Debian update: a newly added program would be visible at once and nobody would
notice. With a whitelist the default is "invisible", and every exception is
justified in the script.

**`nutzer` sees 11 entries**, `dialosadmin` everything but the four duplicates:

| Entry | Why |
|---|---|
| Firefox ESR | browser, Jitsi video chat, WhatsApp Web |
| Thunderbird | mail, calendar, contacts - for the helper |
| LibreOffice Writer | letters |
| Rhythmbox | music, podcasts, audiobooks |
| Shortwave | radio |
| VLC | videos |
| Files | the helper needs to reach `~/Notizen` |
| Text Editor | shopping list and notes are `.txt` files |
| Document Viewer | reading letters as PDF |
| Image Viewer | pictures from the family |
| Calculator | harmless, and a helper does the odd sum |

**Deliberately NOT visible for `nutzer`:** Settings, Terminal, Disks, Logs, System
Monitor, Tweaks, Extension Manager, the DialOS tools and RustDesk. Everything
administrative happens on `dialosadmin`. **That has a consequence which must be
understood:** a helper at the customer's home cannot pair a Bluetooth speaker
without switching accounts. Pairing happens in the office (step 14); for the
exceptional case, switching to `dialosadmin` remains.

**Stephan decided this on 2026-08-19** after the consequence had been named -
and the reason outweighs the convenience: Settings is the most dangerous window
in the system on a device whose user cannot see the screen. One wrong click in
audio output or the microphone leaves DialOS mute or deaf, and the user would
have no way of finding out why. A middle option - exposing only the Bluetooth
page through a menu entry of its own - was rejected as well.

**Override instead of deletion:** files in
`~/.local/share/applications/*.desktop` with `NoDisplay=true` override the
system-wide ones without `apt`/`dpkg` ever touching them - that survives Debian
updates and is undone by deleting one file. What gets copied is the **original**
including `Exec` and `MimeType`, not a minimal file: an override replaces the
original entirely, and were `MimeType` missing, the program would also be gone as
the default application for its file types. The same pattern as the existing
overrides for Evolution and Calendar. It is additionally written to `/etc/skel`
so a later account gets the same view - with `chown` to the respective account,
because a file owned by `root` can no longer be changed by the user.

## 13d. Update automation: every 14 days, on Mondays, with announcement (new 2026-09-14)

Stephan's requirement from 2026-09-14: at some point DialOS will be finished,
and then the packages it needs to run smoothly should always be up to date.
Step 13a only installs **security** updates; everything else waited for someone
with a terminal. On 2026-09-14 that meant **94 packages** from Debian 13.7 were
pending.

```bash
B=iso-build/config/includes.chroot
sudo install -m 0755 $B/usr/local/sbin/dialos-systemupdate /usr/local/sbin/
sudo install -m 0755 $B/usr/local/bin/dialos-update-lauf.py /usr/local/bin/
sudo install -m 0755 $B/usr/local/bin/dialos-start-ansage.py /usr/local/bin/
sudo install -m 0644 $B/etc/xdg/autostart/dialos-update-lauf.desktop /etc/xdg/autostart/
sudo visudo -cf $B/etc/sudoers.d/dialos-systemupdate \
  && sudo install -m 0440 -o root -g root $B/etc/sudoers.d/dialos-systemupdate /etc/sudoers.d/
```

**The sequence, as Stephan decided it:**

| | |
|---|---|
| When | after login, on Mondays, every 14 days |
| Catch-up | if the computer was off on Monday, at the first start afterwards |
| 1. Announcement | "Es müssen ein paar Updates installiert werden. Das kann einige Minuten dauern. Wenn das jetzt nicht passt, sag: später." (until the afternoon of 2026-09-14: "… sag: nicht jetzt.") |
| Objection | ten seconds for "später" or "nicht jetzt"; after that it proceeds |
| 2. Install | `apt-get upgrade` |
| 3. Announcement | "Die Updates sind installiert. Der Computer startet jetzt neu." |
| 4. Reboot | **only with the security stick** |
| 5. After start | greeting, then "Der Computer ist auf dem neuesten Stand." |

**Four parts, and the split is deliberate.**
`/usr/local/sbin/dialos-systemupdate` runs as root and can do exactly three
things: `pruefen`, `installieren`, `neustarten`. Decision, announcements and
listening live in `/usr/local/bin/dialos-update-lauf.py`, which runs **without**
root. Plus an autostart entry and the rule `/etc/sudoers.d/dialos-systemupdate`,
which names the three calls **literally**, for both `nutzer` and `dialosadmin`.
Same split as for the voice: whatever goes through sudo should be as small and
as literal as possible. A `dialos-systemupdate *` would practically be root
access. **Reviewed and approved by Stephan on 2026-09-14** (his rule from
2026-08-24: no sudoers rule without his review). The file on the device was
checked against the repo, checksum `afa162ca…9ffc`; the review added the reboot
condition below. Until the approval the rule was on the NIEMALS list of
`dialos-aufspielen`; now it is installed normally.

**Firmware is included since 2026-09-14** (Stephan's choice: into the 14-day
automation, only on mains power). Reason: GNOME Software showed a UEFI dbx
update the automation never saw - apt knows no firmware, it comes via
fwupd/LVFS. `pruefen` now prints two numbers (`<packages> <firmware>`),
`installieren` installs firmware after the packages (`fwupdmgr update
--assume-yes --no-reboot-check`). **Only when a mains adapter (`type=Mains`,
`online=1`) is connected and every battery is at least 50 %** - checked when
counting and once more right before installing. A BIOS update is applied on
reboot; if power fails then, the device can be bricked, and a blind user does
not notice one is running. USB-C ports deliberately do not count as mains. If
firmware is included, the announcement adds "Bitte ziehe dabei das Netzteil
nicht ab." The sudoers rule is unchanged - no new call. Dry-checked: on mains
"0 1", without mains and with the battery below the limit "0 0". Firmware
state on 2026-09-14: BIOS, embedded controller, Intel ME, Thunderbolt and SSD
up to date; only UEFI dbx 20260402 → 20260707 pending; Secure Boot off on this
T490.
**Real run on 2026-09-14, 13:20** (Stephan: install it now), via `sudo
dialos-systemupdate installieren`: "offen vor dem Lauf: 0 Paket(e), 1
Firmware" → "Firmware eingespielt", return code 0; afterwards `pruefen` "0 0".
fwupd reports "needs reboot" - the dbx takes effect at the next start.
**After the reboot (13:26):** the device reports UEFI dbx **20260707** without
an error, `pruefen` "0 0". The fwupd history still records the operation as
"failed": `failed to run update on reboot: expected 20260707 and got (null)` -
the check at boot apparently read the version too early. Treated as a false
error entry, not a failed update. The sentence "Der Computer ist auf dem
neuesten Stand." came once after the greeting for `dialosadmin` (13:29:28).

**After login, not on a timer** (Stephan's decision after asking). A timer can
fire in the middle of a dictation or a phone call, and the device drops out for
minutes without the user understanding why. Right after login they have not
started anything yet. The run waits until the greeting has finished (marker
`dialos-sprachausgabe-aktiv`, at most three minutes) - otherwise two voices
would talk at once, one of them expecting an answer.

**The due calculation.** It becomes due 14 days after the last successful run
(`/var/lib/dialos/systemupdate-zuletzt`), it is done on the first Monday from
that day, and if "today" is already later, it catches up. Without a last run it
is due immediately: a freshly set-up device should not stay on its delivery
state for weeks. If nothing is pending there is **no** announcement - the user
should not hear every other Monday that nothing happened.

**"Später" does not work.** Stephan wanted "später" ("later") as the objection.
Checked against the model:

    WARNING  Ignoring word missing in vocabulary: 'später'
    WARNING  Ignoring word missing in vocabulary: 'spät'

The word is not in the small Vosk model's vocabulary. The user would have said
"später" and the device would have rebooted anyway - the same silent failure
DialOS removed on 2026-08-24, only more expensive. Chosen: **"nicht jetzt"**
("not now"): two words like switching on, both required, no `[unk]`. `stopp`
was ruled out, it belongs to switching voice control off.

**CORRECTION OF 2026-09-14: "später" is in the vocabulary after all.** The
warning above came from the check: `json.dumps` without `ensure_ascii=False`
writes "ä" as `\u00e4`, and Vosk then reports every umlaut word as missing.
Passed correctly, the model accepts "später". "Nicht jetzt" stays until
Stephan decides anew; whether "später" as ONE word is as safe against
background noise as two would have to be measured first.

**Measured and decided, still on 2026-09-14:** Piper → Vosk with Anna and
Michael. "Später." was recognised with both, "Nicht jetzt." with Anna **not**
(only "jetzt"). "gestern spät gegessen" became "später" - one word arises by
chance more easily. That is the harmless direction: a false "später" postpones
the update by one session, an objection that does not arrive reboots the
machine. Stephan chose "später"; "nicht jetzt" still counts.

**An objection stores no date.** It postpones by **one session**, not fourteen
days - otherwise a single "nicht jetzt" could block the update for two weeks.

**`upgrade`, not `dist-upgrade`, and no `autoremove`.** `dist-upgrade` may
remove packages to resolve dependencies; after step 13b `autoremove` would offer
to remove the desktop and the audio stack (reasoning in 13a).
`--force-confdef --force-confold` keeps changed configuration files - otherwise
apt would stop at a prompt nobody can answer.

**The stick check lives in the privileged part, not in the caller.**
`dialos-stick-gate` locks `nutzer` if the security stick is missing at boot. A
reboot without the stick locks the user out of their own device. So
`dialos-systemupdate neustarten` checks itself with `blkid -L DIALOS-KEY` and
refuses if it is missing. The announcement then is: "Die Updates sind
installiert. Der Computer wird beim nächsten Start fertig." Trusting the caller
would make access to the user's data depend on a swapped condition.

**And it only reboots after a real update during this boot** (added on
2026-09-14 during Stephan's review of the sudoers rule). Before, any program
running as `nutzer` or `dialosadmin` could reboot the machine without a password
whenever the stick was present - repeatedly, too. Now a real installation also
creates `/run/dialos-systemupdate-installiert`, and `neustarten` refuses without
that file (return code 3, `kein-update`). `/run` is empty after every boot: the
condition does not depend on the clock, only root can create the file, and **a
reboot loop is ruled out in the root part itself** - before, only the due
calculation in the unprivileged program prevented it. If the refusal happens in
the normal sequence (e.g. because unattended-upgrades installed the packages
between checking and installing), the run says "Der Computer ist auf dem
neuesten Stand." Verified: in a copy with `systemctl reboot` replaced, refused
without the file and "would reboot" with file and stick; then refused on the
device via sudo.

**The final sentence overstates slightly, and that is decided.** "Up to date"
only applies to the Debian packages; Piper, Vosk and the voices do not come via
apt. Stephan: keep the sentence. The caveat lives here, not in the announcement.

**Verified on 2026-09-14, in three stages:**

| Stage | Result |
|---|---|
| Dry | due calculation correct in six cases (never / 1 / 13 / 14 / 15 / 30 days ago); catch-up on Tuesday after a missed Monday; a wrong argument to `dialos-systemupdate` is rejected by sudo |
| Listening | 09:30:30 `'[unk] jetzt'` - **not** counted as objection; 09:30:36 `'nicht jetzt'` - recognised |
| Real run | 09:32:00 due, 1 package pending (`claude-desktop`; Stephan had installed the 94 by hand beforehand); 09:32:19-09:32:26 installed; stick present, reboot; 09:35:29 after the reboot "not due" - **no loop** |

**A bug only the real run showed: the sentence after the reboot reached only
the account that triggered it.** The first version wrote the marker into the
home directory of whoever started the update - here `dialosadmin`. After the
reboot `nutzer` logged in first and did not hear the sentence; only after
logging in as `dialosadmin` did Stephan hear the full announcement. In real use
that would mean: if the helper triggers the update, the customer never learns
about it.

**The fix: the event belongs to the machine, the acknowledgement to each
person.** After a **real** installation `dialos-systemupdate` writes a timestamp
to `/var/lib/dialos/systemupdate-installiert` (0644; not in the "nothing to do"
branch). `dialos-start-ansage.py` compares it with
`~/.config/dialos/update-gemeldet` and speaks the sentence when the state is
new. Every person hears it exactly once, no matter who triggered the update or
who logs in first. Nothing is deleted any more - the acknowledgement prevents
repetition. **The acknowledgement is written before speaking**, and if it cannot
be written the sentence stays off: a sentence that is missed once is better
than one that comes every morning and nobody can switch off.

Checked in a sandbox with two home directories: first login speaks, second
login of the same person stays silent, the other person speaks once; a new
timestamp speaks again for both; an unwritable acknowledgement stays silent.
**Proven on the device across two accounts on 2026-09-14, 13:26-13:29:**
after the firmware update via the automation and a reboot, the sentence came
first for `nutzer` (autologin), then for `dialosadmin` - once each.

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

### 15b. Parakeet text recognition for letters and notes (new 2026-09-16)

Stephan: "Ja, bau Parakeet fest ein" (build Parakeet in for good). On the test
bench ([pruefstand.en.md](pruefstand.en.md)) Parakeet wrote the freely dictated
letter with 3.4 % word errors (Vosk 28.8 %) and set all punctuation itself.
Vosk stays for everything that needs timing (pauses, closing sentence, "Satz
löschen"), for commands and the shopping list; Parakeet re-recognises every
chunk Vosk delivers from the same recording and supplies the text.

| Component | Location | Size | Licence |
|---|---|---|---|
| Parakeet TDT 0.6B v3, int8 (sherpa-onnx packaging) | `/usr/local/share/dialos-parakeet/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/` | 641 MB | CC-BY-4.0 (NVIDIA) |
| sherpa-onnx 1.13.8 with sherpa-onnx-core | system-wide via pip, like Vosk | ~45 MB | Apache-2.0 |

```bash
scripts/dialos-parakeet-einrichten.sh
```

Run without sudo, the script asks itself. It downloads the archive from
`github.com/k2-fsa/sherpa-onnx` (release `asr-models`), checks its sha256 and
then each of the four model files, copies to `/usr/local/share/dialos-parakeet/`,
runs `sudo pip3 install --break-system-packages sherpa-onnx==1.13.8` and loads
the model as a check. If the model is already unpacked (development device:
`erkenner-vergleich/modelle/`), pass that folder as argument - it is copied
after checking instead of downloaded. Safe to run repeatedly. In the setup run
this is step `15b_parakeet`.

**Dictation (`dialos-diktat.py`):** Parakeet is on as soon as the model is
present. If it is missing or sherpa-onnx cannot be loaded, Vosk writes as
before - the log says `PARAKEET: nicht eingerichtet` or `nicht ladbar`. Switch
off per account: `touch ~/.config/dialos/parakeet-aus` (for comparisons on the
test bench). The test switch file `parakeet-test` of 09-15 no longer applies and
can be removed. Both models load at the same time: one after the other it took
33 s until "Ich schreibe mit", at the same time 12 s on the device (first letter
14:19).

**Post-processing after the first letter (2026-09-16):** "Absatz" alone at a
sentence start counts as a paragraph (not before a number or a lower-case
article), the subject ends at the first sentence end and without full stop
(`betreff_richten`), the salutation gets its comma across chunk boundaries too
(`anrede_richten`), "322,40 Cent" becomes "322,40 Euro". All combined in
`brief_text()`, which the test bench calls as well.

**After the second letter (14:36):** "Betriff/Betrifft" counts as subject; a
chunk that Parakeet renders as a single English filler word ("Yeah.") is
dropped; there is always a blank line before the closing; cut-off endings
("aufführ") are completed by `endungen_ergaenzen()` from Vosk's words, but only
if `hunspell -d de_DE -l` does not know the word - hence `hunspell` is now listed
explicitly in `package-lists/desktop.list.chroot`; if only Vosk hears
"absatz/abseits/absender" at a chunk start, a paragraph is made.

**After the third letter (2026-09-17):** number words become digits following
the writing rules (`zahlen_in_ziffern`): "31. August 2026", "01.10.2026",
"322,40 Euro", "10:30 Uhr", from 13 as digits, up to twelve as words; digit
dates get leading zeros. Mangled number words from Parakeet ("Dreihund",
"zweitaussechdzwanzig") are replaced by Vosk's number words by
`zahlwoerter_aus_vosk` (alignment with difflib, only if hunspell does not know
the Parakeet word). A salutation ("Sehr geehrte …", "Liebe …", "Hallo …", "Guten
Tag") always stands alone with comma and blank line and ends the subject
(`anrede_absetzen`). If Vosk only hears "absatz"/"neue zeile", only the break
counts (before, Parakeet's "Upsets." remained). Test bench: 8 cases, none worse,
all punctuation right.

### 15c. Thunderbird gets an extension instead of DialOS writing into its files (new 2026-09-21)

**Why this is the day's most important rebuild.** DialOS wrote contacts into
`abook.sqlite`, drafts into the mbox, and built the search index over the
mailbox files. Each of the three routes produced its own error: a queue,
because you must not write into a running Thunderbird's database; LF instead
of CR LF, which made the drafts folder look empty; and
`X-Mozilla-Status: 0008`, which does not mean "draft" but **deleted**. The
same pattern three times - rebuilding someone else's file format instead of
asking the program that owns it.

**The line since 2026-09-21: reading from outside is fine, writing is not.**
The search index keeps reading the mbox files (that disturbs nobody and needs
no running Thunderbird). Everything that has to go *into* Thunderbird's data
goes through Thunderbird itself.

Four parts, in this order:

```bash
# 1. Build the MailExtension (from thunderbird-erweiterung/ in the repo)
cd /path/to/repo/thunderbird-erweiterung && python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/dialos-bruecke.xpi','w'); [z.write(d) for d in ('manifest.json','hintergrund.js')]; z.close()"
```

```bash
# 2. Install the bridge and the host manifest
sudo install -m 755 /path/to/repo/iso-build/config/includes.chroot/usr/local/bin/dialos-thunderbird-bruecke.py /usr/local/bin/ && sudo install -m 644 -D /path/to/repo/iso-build/config/includes.chroot/usr/lib/thunderbird/native-messaging-hosts/dialos_bruecke.json /usr/lib/thunderbird/native-messaging-hosts/dialos_bruecke.json
```

3. In Thunderbird: hamburger menu → Add-ons → gear → *Install Add-on From
   File* → `/tmp/dialos-bruecke.xpi`. **Unsigned is fine here:** Debian's
   Thunderbird has `xpinstall.signatures.required=false`; a Thunderbird from
   Mozilla would refuse it.

4. Restart Thunderbird. It must then have started the bridge:

```bash
ls -l "$XDG_RUNTIME_DIR/dialos-thunderbird.sock" && /usr/local/bin/dialos-thunderbird-bruecke.py --bitte '{"befehl": "hallo"}'
```

The answer names the Thunderbird version and the accounts. If
`{"ok": false, "fehler": "Thunderbird läuft nicht"}` comes back, the socket is
missing - the extension is not active, or the host manifest is in the wrong
place (`~/.log/dialos-thunderbird.log` says what happened).

**The socket's permissions are deliberate:** `0600`, for the logged-in user
only. The socket carries mail addresses and subject lines.

**Two permissions, not one.** `compose` allows opening a compose window -
`compose.save` is what allows filing it as a draft. Without the second one
Thunderbird reports `browser.compose.saveMessage is not a function`, and the
cause looks like a programming error.

**If Thunderbird is closed, the draft is queued and caught up** (Stephan's
choice): `dialos-mail-entwurf.py` puts it into
`~/.config/dialos/mail-entwuerfe.json`, DialOS says "Thunderbird ist zu. Ich
lege den Entwurf beim nächsten Start von Thunderbird ab.", and the bridge
works the queue off as soon as Thunderbird starts it. **The condition has
flipped:** a running Thunderbird used to be the obstacle, now it is the
prerequisite.

**German spell checking** (Stephan saw "something about English in the bottom
right"): `user_pref("spellchecker.dictionary", "de-DE");` is written into the
profile's `user.js` by `dialos-mail-signatur.py`.

### 11k. Opening programs on command (new 2026-09-21)

```bash
sudo install -m 755 /path/to/repo/iso-build/config/includes.chroot/usr/local/bin/dialos-programm.py /usr/local/bin/
```

Nine sentences - "Postfach öffnen", "neue E-Mail schreiben", "E-Mail
schreiben", "Kalender öffnen", "Kontakte öffnen", "Internet öffnen", "Browser
öffnen", "Musik öffnen", "Radio öffnen". They live in `dialos-programm.py` and
nowhere else; `dialos-sprachbefehl-desktop.py` reads the list at startup, like
the extensions' sentences. **After installing, the voice service must be
restarted** (log out and in), otherwise the grammar does not know them.

"Postfach öffnen" is also the resolution for queued drafts: it starts
Thunderbird, and the bridge files whatever is waiting - announcing it first.

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
