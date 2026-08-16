[Deutsch](TODO.md) | [English](TODO.en.md) | [Changelog](README.en.md#changelog)

# TODO

A running list of small open items and next steps that Stephan or Claude
notice during day-to-day work. Unlike
[Open questions](docs/offene-punkte.en.md) (fundamental, not-yet-decided
architecture questions), these are concrete, checkable tasks. Completed
items are marked with a checkmark, not deleted - so it stays traceable
what has already been done.

- [x] Implemented a volume prompt during the startup announcement (only
  `nutzer`, 100/75/50/25%/off) - done 2026-08-14, see
  docs/Debian-zu-DialOS.en.md step 11. First real production use of
  Vosk, recognition logic verified with Piper-synthesized test words
  (all five options recognized correctly).
- [x] Ran a real test of the volume prompt with an actually spoken
  answer (via the Bluetooth microphone, including the
  `headset-head-unit` profile switch) - done 2026-08-16. Found and
  fixed a real bug along the way: the first attempt lacked a clear
  signal for exactly when the 4-second recording window starts -
  Stephan's spoken answer ("25") was missed, only the 100% safety
  fallback came through. Fix: `dialos-start-ansage.py` now additionally
  says "Und jetzt bitte." (And now, please.) right before recording -
  correctly recognized on the second attempt afterward (a real "25" →
  25%).
- [x] Switched the weather location to GeoClue2 instead of IP guessing -
  done 2026-08-14, tested extensively live (see README changelog 0.5.0
  and docs/Debian-zu-DialOS.en.md, step 11, for details). Trigger:
  `wttr.in`'s own IP-based location showed Vienna instead of Stephan's
  real location (Seefeld in Tirol) - a fixed location was ruled out
  since the device is also used while traveling. Live finding along the
  way: GeoClue2 also falls back to a coarse IP estimate ("ipf fallback",
  ~25-26 km inaccurate, ~300 km off in reality) in areas with sparse
  Mozilla WiFi-database coverage - so an accuracy threshold (>10 km gets
  discarded) was added, and the weather announcement is then
  deliberately skipped rather than naming the wrong city/region. Can
  therefore be missing more often in rural areas than before - an
  accepted trade-off.
- [ ] **Reference device settled 2026-08-16: AIRHUG 01** (Bluetooth
  headset, A2DP + HFP, documented in `docs/hardware.en.md`). Only the
  original sub-question remains: whether it supports German as its own
  announcement language (the device's own firmware prompts like
  "connected"/low
  battery, not DialOS itself) - standard Bluetooth profiles (A2DP/HFP)
  offer no remote control for this, it's purely device-/vendor-
  dependent. Factor this into the reference hardware selection.
- [x] **DONE on 2026-08-16 - the complete flow has run on real
  hardware.** Result: a freshly installed Debian 13 became a running
  DialOS. Proven: encrypted swap (comes up on its own at boot, evidenced
  by the journal), `dialos-nutzer-home` at 374.9 GiB, autologin for
  `nutzer`, audible speech output, German keyboard, and **both directions
  of the stick gate**: without the stick a login screen requiring a
  password and a closed LUKS container, with the stick a clean autologin
  including announcements. Also confirmed live: the new volume logic -
  announcement, then the question, spoken "25" recognized and stored
  permanently. Eight faults surfaced along the way that no dry run would
  have found (details in README changelog 0.5.0). Original entry:
  completely reinstall the T490 and use it to really
  test the whole new flow (never run end-to-end yet): install Debian 13
  + GNOME manually (step 1, **with** the partitioning note documented
  since 2026-08-14 - 100 GB root, deliberately leave the rest of the
  disk free) → `scripts/dialos-full-office-setup.sh` (steps 2-12 + 15
  automated) → new `dialos-setup-home-partition.sh` (sets up the
  `dialos-nutzer-home` partition + security stick in the free space,
  replaces `dialos-install`'s whole-system copy for this flow) →
  `scripts/dialos-buero-setup-abschliessen.sh` (create `nutzer`).
  Afterward, as Stephan planned: build out speech recognition/voice
  commands step by step on real hardware and keep extending the install
  routine.
  **Groundwork done 2026-08-16:** both scripts were reviewed against
  `docs/Debian-zu-DialOS.en.md` before the first run, cross-checked live
  on the freshly installed T490, and the faults found were fixed (details
  in README changelog 0.5.0). The flow now consists of exactly three
  commands; the manual work from doc step 13 lives in
  `dialos-buero-setup-abschliessen.sh`.
- [x] **Swap decided (Stephan, 2026-08-16): 8 GiB, encrypted,
  automated in `dialos-setup-home-partition.sh`.** Starting point: a
  37.3 GiB plaintext swap partition (`nvme0n1p3`) that `nutzer`'s memory
  pages - open documents, mail, browser content - could be paged out to;
  readable without the security stick, and likewise after removing the
  SSD, i.e. bypassing exactly the protection `dialos-nutzer-home`
  provides. Implemented: the script replaces any plaintext swap it finds
  with 8 GiB using a key re-randomized on every boot (`/etc/crypttab`,
  `/dev/urandom`, referenced by PARTUUID rather than filesystem UUID),
  sets `vm.swappiness=10` and `RESUME=none`, and hands the freed space to
  the home partition (on the T490: 345.6 → about 375 GiB). Rationale for
  the size: the "swap ≥ RAM" rule exists only because of hibernation, and
  hibernation is ruled out under this security design anyway (the image
  would need a persistent key in the initramfs - the discarded
  `cryptsetup-initramfs` approach). Dropping swap entirely was not an
  option: without swap the OOM killer terminates processes outright under
  memory pressure, and a killed screen reader means a blind user loses all
  feedback. Suspend-to-RAM is unaffected. **Not yet run for real** -
  happens during the first end-to-end run on the actual device.
- [x] **Done (2026-08-16): `dialos-install` has been dropped entirely**
  (path A - every device is built in the office from the Debian ISO plus
  the three scripts, there is no live-boot installer any more), which
  disposes of its faults too. **`dialos-rekey` stays** and still has
  them - carry them over next time it is touched: same `$HOME` starting
  folder in the backup dialog (line 142) and missing fallbacks in
  `ask_password`. Original entry: **`dialos-install` and
  `dialos-rekey` carried the same faults as the
  reviewed `dialos-setup-home-partition.sh`** - deliberately not fixed
  along with it, because the fate of the clone path was still undecided. Affected: same over-long ext4 label
  `dialos-nutzer-home` (`dialos-install` line 248), same plaintext
  passphrase under a fixed `/tmp/.rp` name (line 199), same `$HOME`
  starting folder in the backup dialog (line 231, `dialos-rekey` line
  142), same missing fallbacks in `ask_password`/`zenity --list`. Either
  carry the fixes over or retire them together with the clone path - but
  don't let them drift apart.
- [x] **Timezone/locale decided (Stephan, 2026-08-16): stays
  `Europe/Vienna` + `de_AT.UTF-8`.** Not `Europe/Berlin`, which the guide
  prescribed until then. Consequence, now documented in
  Debian-zu-DialOS.en.md step 1: the build device and every ISO taken
  from it carry the Austrian settings (`eggs produce --clone` clones
  `/etc/localtime` + locale along). Simplified further on the same day by
  the decision for path A: every device is set up in the office via the
  Debian installer, so the timezone is chosen per device in step 1.
- [ ] **Deferred (Stephan, 2026-08-16):** **Run `dialos-claude-setup.sh`
  on the freshly installed T490.**
  Checked 2026-08-16: `credential.helper` is unset, `~/.git-credentials`
  is missing, `/etc/sudoers.d/` contains only the README, and `~/DialOS`
  does not point at the repo on the external drive. So the script has
  never run on this system - `git push` would prompt for credentials and
  the `eggs produce` NOPASSWD rule is absent. Stephan has to do this
  himself (no script accepts the GitHub token).
- [x] Created the consolidation script
  `scripts/dialos-full-office-setup.sh` + new
  `dialos-setup-home-partition.sh` (runs `dialos-install`'s LUKS/stick
  logic on an already-installed system, without its disk-wipe/rsync
  copy), updated `Debian-zu-DialOS.md`/`.en.md` accordingly (step 1:
  partitioning note; step 12: new tool) - done 2026-08-14, both scripts
  only syntax-checked (`bash -n`) so far, not run for real yet (see the
  item above).
- [ ] **Deprioritized, no longer the next step** (see the two new items
  below): Run a real live-boot test with `DialOS-Live-0.5.0-clone.iso`
  (supersedes the old, now outdated live-boot-test item for the 11.08
  ISO): before running `dialos-install`, check via `gdbus` whether
  `dialosadmin`/`nutzer` came along with the correct autologin status
  (see docs/sicherheit-datenschutz.en.md, section "Automatic login");
  then run through `dialos-install` completely with the security stick -
  unplug the external SanDisk-Extreme drive first (otherwise it's
  selectable as the target disk!); verify the new stick partitioning
  (`DIALOS-KEY` 2 GiB + `DIALOS-DATA` ext4).
- [x] **Moot since 2026-08-16:** `dialos-install` has been dropped
  entirely (path A). This entry's checkpoints were covered by the new
  flow instead and all passed - see the completed entry above.
  Originally: run a complete `dialos-install` installation
  with the new home-partition design on real hardware (T490) (see
  docs/sicherheit-datenschutz.en.md, section "Encrypting nutzer's data +
  security stick", for the full design). Check: ~100 GiB unencrypted
  root partition boots normally; `dialos-nutzer-home` (LUKS2) gets set
  up correctly during office setup; `dialos-setup-nutzer.sh` aborts
  cleanly without the stick plugged in instead of creating `nutzer`'s
  home on root; after setup: unplug the stick + reboot → normal GDM
  login screen, `/home/nutzer` empty/unmounted; plug the stick back in +
  reboot → `/home/nutzer` mounted, autologin works. Also verify
  `DIALOS-KEY` (now ext4, no longer FAT32) and `DIALOS-DATA` (now
  exFAT, no longer ext4) on a 64 GB stick. **Partially done already
  (2026-08-14):** the plain stick partitioning was manually tested
  (not via `dialos-install` itself, but by hand with the same commands)
  against a real 59.8 GB USB stick - `DIALOS-KEY` (ext4, root:root 755,
  neither readable nor writable for regular users - stronger protection
  than planned) and `DIALOS-DATA` (exFAT, writable for the current user)
  were created correctly. **Still open:** mount and write-test
  `DIALOS-DATA` on a real Windows machine (only verified on Linux so
  far).
- [x] Fundamental decision made (see above, implemented 2026-08-14):
  whole-disk LUKS encryption is gone entirely, replaced by a dedicated
  `dialos-nutzer-home` partition + the `dialos-stick-gate` gate.
  `dialos-install`/`dialos-rekey`/`dialos-stick-gate.sh` rewritten
  accordingly, dead `dialos-keyscript` initramfs files removed.
- [x] **Resolved by removal (2026-08-16):** the Calamares location page
  often suggested a wrong location based
  on GeoIP during live boot (e.g. Rome instead of Berlin) - no
  documented vendor override found for `modules/locale.conf` (only
  branding is officially overridable). Remains a tool limitation for
  now; the person installing must manually check/correct the location
  while clicking through (uncritical under two-phase provisioning, since
  end customers never see the installer).
- [ ] The Piper voice's speaking rate should be individually adjustable
  by the user (currently hardwired via `GenericRateMultiply` in the
  Piper config, `0.85` chosen as Stephan's personal preference) - needs
  a real setting (e.g. GNOME accessibility settings or a dedicated voice
  command), not just a config value.
- [x] Vosk (0.3.45) + hassil (3.11.0) + German Vosk models (large/small)
  documented as a repeatable recipe - done 2026-08-14 (see
  docs/Debian-zu-DialOS.en.md, step 15). Confirmed along the way: the
  original live installation had actually disappeared again
  (`import vosk` failed on re-check) - an interim reinstall of the T490
  had wiped it, exactly the trap this item warned about.
  `dialos-vosk-test.py` is now in the repo under
  `iso-build/config/includes.chroot/usr/local/bin/`. Also found: the
  model folders on the T490 (`/usr/local/share/vosk-model-de-big` and
  `-small`) contain doubly-nested duplicate copies of the model files
  due to an unzip mistake during the original test run (wastes disk
  space, measured ~6.3 GB instead of ~3.2 GB for the large model) - the
  new docs avoid the mistake, but the existing duplicate data on the
  T490 itself hasn't been cleaned up yet.
- [x] Ran and verified
  `pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0` on
  the T490 (2026-08-14) - `import vosk`/`hassil` works, `vosk.Model()`
  successfully loads the small German model.
- [ ] Run a real end-to-end test of `dialos-vosk-test.py` (actually
  speak into it, judge recognition quality) - so far only installation +
  model loading verified technically, no real speech recognition test
  with an actual spoken recording has run yet.
- [x] First entry in `docs/iso-builds.en.md` recorded: `eggs produce
  --clone` ran on 2026-08-16 (21/21 steps without errors, 6.50 GiB),
  `DialOS-Live-0.5.1-clone.iso` as a backup snapshot before the planned
  end-to-end test (see next item) - version/date/commit/SHA256 filled
  in.
- [ ] `DialOS-Live-0.5.1-clone.iso` currently only exists locally
  (`~/DialOS-Live-0.5.1-clone.iso`) - still needs to be uploaded to
  Nextcloud (only Stephan can do this, no Claude access to it).
- [ ] The Bluetooth audio fix in `dialos-start-ansage.py`
  (single-instance lock/`alte_instanz_beenden()`) hasn't been
  conclusively confirmed over a longer period yet - check
  `/tmp/dialos-bluetooth-debug.log` if the problem recurs.
- [ ] Delete the stale local second repo copy under `~/DialOS-repo`, or
  deliberately keep it as a backup (decision still open) - the
  `~/DialOS` symlink is now correctly set up (see "Done" below), but
  the second copy itself is still sitting there. Two independent copies
  side by side are error-prone - that's exactly how two never-pushed
  commits from 2026-08-13 were nearly lost on 2026-08-14.
- [ ] Clean up leftover `/home/eggs/*.iso` files from the last builds
  (owned by `root`; the `eggs produce` NOPASSWD rule only covers
  `eggs produce` itself, not `rm` - needs Stephan's manual `sudo rm`).

## Done (kept for traceability)

- [x] Live desktop icon for the installer (`.desktop` file with its own
  DialOS icon instead of "Install System"/egg icon on the live boot
  desktop) - done 2026-08-10 (branding via skel override).
- [x] Build a new ISO with all the fixes collected so far (boot screen,
  avatar script, Calamares branding, Piper TTS) - done 2026-08-10/11
  (the 11.08 ISO).
- [x] Set up the `~/DialOS → .../SanDisk-Extreme/DialOS/repo` symlink
  again - done 2026-08-14 via `scripts/dialos-claude-setup.sh`, which
  now also restores the `eggs produce` sudoers rule on every reinstall.
- [x] Anchor the AppIndicator packages for `dialos-tts-indicator.py`
  (`gnome-shell-extension-appindicator`, `gir1.2-ayatanaappindicator3-0.1`)
  in the package list - done 2026-08-14, also added
  `gnome-shell-extension-desktop-icons-ng` (DING) while at it: GNOME
  hasn't shown desktop icons out of the box for years, without this
  extension the office-setup scripts on `dialosadmin`'s desktop (see
  below) would have stayed invisible.
