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
- [ ] **Next block: the applications** (Stephan, 2026-08-17). So far it
  has been foundations - speech output, recognition, audio routing, desktop
  look. Next up is which programs DialOS ships and how they are operated
  by voice. **The entry point is the "Planned, not built yet" table in
  `docs/sprachbefehle.en.md`** (radio/music, call for help, system
  maintenance, telephony) - do not start a new list, work through the
  existing one and follow the rules from that same file for every new
  command.

- [ ] **Unexplained: the Bluetooth sink suddenly stood at 70 %**
  (2026-08-17). Between two measurements the AIRHUG's volume changed from
  100 % to 70 % without DialOS having done anything. Three explanations are
  refuted: the device does not report its volume (tested on button press
  with no audio, on playback start, and on button press **during** an
  active playback - no change in all three), WirePlumber's stored value is
  100 %, and the event log shows no re-creation of the sink in the relevant
  window. **Deliberately no fourth guess** - recorded so that a second
  occurrence yields a second data point. It matters because a volume that
  changes by itself is not comprehensible to a blind user.

- [ ] **Decision open: announcements quieter than music** (Stephan's wish
  of 2026-08-17, "throttle by about 30 %"). On the laptop speaker it is
  doable - signal attenuation works there, confirmed by Stephan by ear. On
  the AIRHUG it does **not**: it undoes the attenuation (measurement in
  `docs/Debian-zu-DialOS.en.md`, step 11g), only the device volume works
  there, and that applies to everything. One option would be to lower it
  briefly via AVRCP **during** the announcement; such a command costs a
  measured 19-36 ms, negligible against a 1200 ms announcement. Open is
  whether lowering it audibly steps or clicks on the device - that decides
  whether it is usable. After Stephan set the volume on the device, the
  question may be moot anyway.
  - **To fix along with it:** `GenericVolume` is ineffective in DialOS,
    because the sox chain ends in `norm` and cancels any attenuation
    before it. Anyone wanting to control the volume through
    speech-dispatcher must write `norm vol <factor>`.

- [ ] **Roadmap to real voice control** (agreed with Stephan on
  2026-08-16, in this order):
  1. Decide on a reference microphone - **done**, AIRHUG 01.
  2. **Windows 11 desktop switch** - **built on 2026-08-16**, live test
     still pending (see next item).
  3. Wake word + continuous listening loop - **partly done on
     2026-08-16**: the listening loop runs
     (`dialos-sprachbefehl-desktop.py`), a wake word does not exist yet.
     It hasn't been missed so far, because the restricted grammar only
     admits three fixed sentences.
  4. hassil command grammar - **the desktop switch as the first real
     voice command was done on 2026-08-16**, though directly via a Vosk
     grammar rather than hassil. hassil only pays off once there are
     several commands with variants.

- [x] **Optional Windows 11 look for GNOME built** (Stephan's request of
  2026-08-16, implemented the same day).
  `/usr/local/bin/dialos-desktop-stil.sh` switches in both directions
  (`windows` / `gnome` / `status`); the three Debian extensions
  (`dash-to-panel`, `arc-menu`, `tiling-assistant`) are in the package
  list and get installed but not enabled. Documented in
  `docs/Debian-zu-DialOS.en.md`, step 11b.

- [x] **Windows switch tested technically (2026-08-16).** Packages
  installed, switched back and forth three times, every touched key
  compared: the way back restores the shipped state, and repeated runs
  create no duplicate entries. Two faults were found and fixed along the
  way (GNOME Shell doesn't know freshly installed extensions; the ArcMenu
  schema is in the wrong directory in Debian) - details in the changelog.

- [x] **Voice command tested live and working (2026-08-16, confirmed by
  Stephan).** It surfaced that the built-in microphone was over-amplified
  by 60 dB - the service could not possibly recognize anything. Fixed and
  permanently secured (`dialos-mikrofon-pegel.service`).

- [ ] **Guard the Bluetooth profile against getting stuck** (open since
  2026-08-17). After the restart the AIRHUG was on `headset-head-unit`
  instead of `a2dp-sink` - playback ran permanently at phone quality,
  without anyone unfamiliar with the device noticing.
  `dialos-start-ansage.py` deliberately switches to HFP for the volume
  question and back afterwards; if the script ends before that (abort,
  logout, timeout) the profile stays. What is needed is a guard that
  works independently of the script finishing - e.g. a check at login or
  a `trap` on script exit.

- [x] **Cause of the microphone clipping determined (2026-08-17).** The
  system-wide service runs at boot; WirePlumber restores its state only
  within the session and raises the boost back - so the service was
  structurally too early. The voice service now sets the level itself
  after opening the recording, and re-adjusts on sustained clipping.
  Tested by deliberately turning it back up.

- [x] **False triggers from played-back content fixed (2026-08-17).**
  Echo cancellation via PipeWire's `module-echo-cancel` set up, 32 dB of
  attenuation measured, and the case that failed before (announcement
  played via `paplay`) no longer triggers anything. Details in the
  changelog and in `docs/Debian-zu-DialOS.en.md`, step 11f.

- [x] **"Sprachsteuerung starten/stoppen" switch built (2026-08-17).**
  Two states with their own grammar, an announcement on every change, and
  a two-minute timeout. That answers the open state question: the user
  hears every change. A live test with a real voice is still pending.

- [x] **How the task was worded before (for provenance):** Until "starten", DialOS listens for that
  one sentence only; afterwards it accepts commands until "stoppen".
  Recognition is already measured as reliable with three distractors
  staying quiet - what is open is the state itself: where is it
  remembered (a file, like the desktop style?), what happens at login (on
  or off?), and **how does a blind user find out which state they are
  in**? Without an answer to that, the switch is more dangerous than no
  switch: anyone who doesn't know recognition is off will think the
  device is broken.

- [ ] **Check pauses between the sentences of the announcement** (open
  since 2026-08-17). Michael sounded "hectic", yet the tempo chosen was
  faster - which suggests the missing breaths between sentences are the
  real problem, not the speed. Piper strings sentences together almost
  without a pause. A short pause per sentence end, centrally in
  `dialos-say.py`, would calm the announcement without making individual
  words drag. Build a listening sample first: same tempo, only with
  pauses.

- [x] **Distinguish announcements: question or hint - built on
  2026-08-17.** `dialos-say.py --frage`; the default is the natural
  sentence melody from the question mark, the signal tone is an option
  via `~/.config/dialos/frageton`. See `docs/Debian-zu-DialOS.en.md`,
  step 11a. What remains is making it switchable by voice later ("switch
  on the signal tone") - that needs the "Sprachsteuerung starten/stoppen"
  switch first.

- [x] **Original description (Stephan's question of 2026-08-17).** Today the system knows implicitly - the code
  decides what gets said - but never passes it on: `dialos-say.py`
  receives a text and speaks it. More important than the system knowing
  is that **the user recognizes a question as a question**: for someone
  who cannot see the screen, "is it waiting for me?" is the decisive
  information. On 2026-08-16 the first test of the volume prompt failed
  on exactly this - the system asked, Stephan didn't know when. The
  stopgap was the sentence "Und jetzt bitte.". The clean solution: give
  speech output a kind (hint/question), and on a question automatically
  emit a short, always identical signal. A **tone** would serve better
  than a sentence - faster, unmistakable, and it doesn't wear out.

- [ ] **Build the wake word with openWakeWord** (decided 2026-08-17).
  The Vosk grammar is ruled out - it forces every utterance into the
  nearest phrase, which is why "ich rufe michael an" came through as
  `hallo michael`, and with full confidence at that (conf 1.00). So a
  threshold does not separate. The wake phrase should be the assistant's
  name ("Hallo Michael", or "Hallo Anna" with a female voice), read from
  the same setting as the voice selection. Details in
  `docs/sprachsteuerung.en.md`.

- [ ] **Record a demo video with voice input and output** (Stephan's
  idea of 2026-08-16, for the next working day). It should show what
  DialOS can actually do today: the login announcement with the volume
  question, then "auf Windows umschalten" / "auf Linux umschalten" by
  voice. The open question is the audio capture - the screen alone is not
  enough, both the system's speech output and the spoken input have to be
  audible. `wf-recorder` or OBS with two audio tracks (system sound +
  microphone) would work; neither is installed yet. **Careful with the
  microphone choice:** the voice-command service listens on the built-in
  microphone so the AIRHUG stays in A2DP - recording via the headset
  microphone would drag playback down to phone quality and make the video
  sound worse than the system actually is.

- [x] **Reference audio device decided (Stephan, 2026-08-17): two
  devices.** The AIRHUG stays as the speaker in A2DP, plus a wireless
  microphone with a **USB** receiver for input - deliberately not a
  second Bluetooth device, which would bring back the HFP trap.
  Requirements and candidates in `docs/hardware.en.md`.

- [ ] **Obtain an inexpensive Bluetooth microphone to try out**
  (Stephan, 2026-08-17 - the test decides the design). Bluetooth has one
  advantage USB does not: **DialOS sees the battery level** via BlueZ and
  can warn before the microphone goes flat. Against it stands a risk that
  can only be settled on the device: a permanently open HFP link
  continuously consumes airtime on the same adapter the AIRHUG plays
  through - A2DP may stutter.

  **Test plan:** pair it, run the radio through the AIRHUG, point the
  voice service at the Bluetooth microphone, and listen for stutter.
  Additionally: range across the flat, battery level appearing in the
  login announcement, recognition quality against the built-in
  microphone, and whether echo cancellation still suffices when the
  microphone lies **next to** the speaker rather than far away.

  If the test goes badly, the fallback is a USB wireless microphone
  (candidates in `docs/hardware.en.md`) - but then without a battery
  indicator, and it must be clarified before buying whether the
  transmitter can run permanently from a power supply.

- [ ] **Detect when the microphone stops delivering** (2026-08-17, to be
  built regardless of the device choice). The voice service measures the
  level continuously anyway. If **nothing at all** arrives for minutes
  even though the source is present, it should say so: "I can't hear
  anything from the microphone any more." That does not replace a battery
  indicator but catches exactly the failure that would otherwise leave
  the user clueless - they would be talking to a dead device without
  noticing. Careful with the threshold: silence in the room is normal, a
  permanently **exact** zero level is not.
  - **On 2026-08-17 the task grew beyond what it was meant to be - the
    case occurred and took the entire audio output with it.** Echo
    cancellation was pointed at the USB headset for testing; at reboot
    its link was not there. The dongle still offers a sound card, ALSA
    even reports `state: RUNNING` - only 0 bytes arrive. Because the
    module needs that capture as its clock, PipeWire no longer started
    the graph, and **nothing** in the system could play audio, not even
    through the built-in speakers. Details in
    `docs/Debian-zu-DialOS.en.md`, step 11f.
  - **So there are two things hanging on this, not one.** (1) The
    announcement when the microphone goes quiet - as above. (2) A
    safeguard that drops echo cancellation instead of taking the audio
    down with it. As long as the target is the built-in microphone the
    case cannot occur; as soon as an external wireless microphone is to
    become the standard - and that is planned - (2) is a precondition,
    not an accessory.
  - **To investigate:** whether PipeWire itself offers a way to keep a
    silent source from becoming the clock would be the clean route.
    Otherwise a service has to check the target before loading (test
    `parec` for bytes) and only then hook cancellation in.
  - **And the finding that makes this hard: there is no reliable
    indicator.** After unplugging and replugging the dongle the same
    device delivered 64000 bytes instead of 0. Stephan explicitly noted
    that **before** replugging, the headset had reported an established
    connection to him, via the dongle too. So: the headset reports
    connected, the dongle offers a sound card, ALSA reports
    `state: RUNNING` - and still 0 bytes arrive. My first reading ("the
    link was not up") was therefore wrong. **Consequence for the
    safeguard:** it must not rely on any status report, neither the
    device's nor ALSA's. Only the bytes that actually arrive count.

- [x] **How the task was worded before (for provenance):** What is measured:
  the device cannot sound good and listen at the same time (A2DP has
  `sources: 0`), its buttons reach the laptop on **neither** channel -
  not as key codes, not as AVRCP volume - and its volume is decoupled
  from GNOME. That rules out the workaround of briefly switching to HFP
  by button. Three options, see `docs/hardware.en.md`: two devices
  (microphone permanently in HFP with the user, speaker in A2DP), a
  different speaker whose buttons get through, or the requirement that
  the laptop be in the same room.

- [x] **Clarified on 2026-08-17: the volume decoupling applies in one
  direction only.** The computer can control the AIRHUG perfectly well
  (10 % vs. 100 % unmistakable by ear); only its own buttons don't report
  back. My first assessment ("DialOS cannot control it at all") was an
  overstatement. Not a disqualification.

- [ ] **Residual risk from this:** DialOS does not know the volume set on
  the device. If someone has turned the AIRHUG down by hand, "louder"
  only helps while the software volume still has headroom - at 100 % it
  stays quiet, and the cause lies outside the system. Worth considering:
  should DialOS detect this case (software at 100 %, user keeps saying
  "louder") and say that the device itself needs turning up?

- [ ] **Repeat the microphone comparison of 2026-08-13.** Back then the
  built-in microphone was judged clearly inferior to the AIRHUG. On
  2026-08-16 it turned out that 60 dB of gain were applied out of the box
  and the signal was permanently clipped - so the test probably did not
  measure the microphone but the clipping. Until this is repeated, the
  rationale for the Bluetooth priority rests on shaky ground.

- [ ] **Visual sign-off of the Windows look after logging in** (open
  since 2026-08-16). The settings are demonstrably correct, but nobody
  has actually seen them: the extensions only take effect after logging
  out and back in once. To check: taskbar at the bottom with centered
  icons, ArcMenu start menu on the left in the Windows 11 layout, window
  buttons on the right, window snapping at the screen edge. Then run
  `dialos-desktop-stil.sh gnome` and verify everything really looks like
  before. Afterwards the same as `nutzer`.

- [ ] **Add spell-checking** (`hunspell-de-de`, `hunspell-en-us`,
  `aspell`). It is in no package list. The earlier rationale in
  `docs/offene-punkte.en.md` ("fails inside the Docker chroot build
  environment") is moot with path A - installation happens today via
  `apt` on a running system, where the problem doesn't occur. Belongs in
  `iso-build/config/package-lists/desktop.list.chroot`.

- [ ] **Move the lock file of `dialos-start-ansage.py` out of `/tmp`.**
  `/tmp/dialos-start-ansage.pid` is a fixed path in shared `/tmp` - the
  same design that caused a silent failure with the speaking marker on
  2026-08-16 (sticky bit: one account can neither overwrite nor delete
  another's file). The marker now lives under `$XDG_RUNTIME_DIR`, this
  file does not.

- [ ] **Test the microphone fallback without Bluetooth** (open since
  2026-08-16). The output side is proven - headset off, sound came from
  the built-in speaker. The input side is still missing: does the
  built-in laptop microphone understand the volume question?

  **Important, or the test appears to fail:** since 2026-08-16 the
  question is only asked once. Delete the remembered value first,
  otherwise nothing is asked at all:

  ```bash
  sudo rm /home/nutzer/.config/dialos/lautstaerke
  ```

  Then switch the AIRHUG **off**, log out and back in as `nutzer`, and
  answer into the laptop microphone.

  **Expectation:** noticeably worse than over the headset - the
  comparison test of 2026-08-13 was unambiguous (6 of 8 test sentences
  correct over Bluetooth, clearly fewer with the built-in mic). For a
  fallback it is enough that it works *at all*: it only has to prevent a
  user without a headset from being unable to do anything. If nothing is
  understood, the 100% fallback applies - the announcement stays audible,
  but the user could no longer change the volume themselves.

- [ ] **Check the speaker's German firmware prompts** (open since
  2026-08-16, Stephan's requirement a). This means the device's own
  prompts ("connected", low battery), not those of DialOS. For a blind
  user they are the **only** feedback received from the device
  independently of the laptop - a misunderstood battery warning means
  output fails without notice. Standard Bluetooth profiles offer no
  remote control for this; it depends purely on the device. Not yet
  checked on the AIRHUG.

  *(The earlier wording of this item named the AIRHUG as the sole
  reference device. That is superseded since 2026-08-17: there are two
  devices, see above and `docs/hardware.en.md`.)*
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
- [x] **Done 2026-08-16: eight old ISOs deleted (~59 GB).** All came from
  the dropped Penguins' Eggs era. `DialOS-Live-0.5.1-clone.iso`
  deliberately stays until Stephan's first Rescuezilla image exists - it
  exists nowhere else and could not be recreated. Documented in
  `docs/iso-builds.en.md`. Originally: **Premise outdated, needs a fresh decision (checked 2026-08-16):**
  `DialOS-Live-0.5.1-clone.iso` is **no longer** local - the reinstall
  took it too. It still exists on the external drive under `DialOS-ISOs/`,
  together with four older images; **28 GB** in total.

  The real question is now a different one: all five come from the
  Penguins' Eggs era, dropped on 2026-08-16, and represent a system state
  that today's rebuild has substantially superseded. Is a Nextcloud upload
  still worth it, or are they deleted with `docs/iso-builds.en.md` keeping
  them only as a ledger?

  Only Stephan can decide - it is his backup strategy. Original entry:
  `DialOS-Live-0.5.1-clone.iso` currently only exists locally
  (`~/DialOS-Live-0.5.1-clone.iso`) - still needs to be uploaded to
  Nextcloud (only Stephan can do this, no Claude access to it).
- [ ] The Bluetooth audio fix in `dialos-start-ansage.py`
  (single-instance lock/`alte_instanz_beenden()`) hasn't been
  conclusively confirmed over a longer period yet - check
  `/tmp/dialos-bluetooth-debug.log` if the problem recurs.
- [x] **Resolved by the rebuild (checked 2026-08-16):** `~/DialOS-repo`
  no longer exists - the T490 reinstall removed the second copy. The
  danger that prompted this entry is therefore gone; the `~/DialOS`
  symlink now points at the repo on the external drive, so only one copy
  is left. Originally: Delete the stale local second repo copy under `~/DialOS-repo`, or
  deliberately keep it as a backup (decision still open) - the
  `~/DialOS` symlink is now correctly set up (see "Done" below), but
  the second copy itself is still sitting there. Two independent copies
  side by side are error-prone - that's exactly how two never-pushed
  commits from 2026-08-13 were nearly lost on 2026-08-14.
- [x] **Moot since 2026-08-16:** clean up leftover `/home/eggs/*.iso`
  files - Penguins' Eggs has been dropped (step 16, now Rescuezilla), and
  on the rebuilt T490 it was never installed in the first place.
  Originally: Clean up leftover `/home/eggs/*.iso` files from the last builds
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
