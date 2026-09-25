[Deutsch](offene-punkte.md) | [English](offene-punkte.en.md)

# Open questions

A collection of everything not yet conclusively clarified or implemented,
so nothing gets lost from the discussions.

## Hardware
- Reference laptop model not yet finalized (candidate: ThinkPad X1 class
  or a comparable lightweight business laptop with a WWAN option).
- No WWAN module available for practical SIM testing — the test T490 has
  none installed. Needs to be procured for the SIM variant (voice-capable
  modem, e.g. Quectel EM7565).
- Network priority WLAN/wired over SIM for internet connectivity:
  implemented via NetworkManager route metrics (lower metric = preferred).
  Wired profile set to ipv4.route-metric/ipv6.route-metric 100, WLAN
  profile to 600 (verified on the T490 with `nmcli connection show
  "<profile>" | grep route-metric`). UNTESTED: wired metric only set,
  not functionally verified with a cable plugged in (no cable
  available). The SIM profile can't be created yet for lack of WWAN
  hardware — once available, set ipv4.route-metric/ipv6.route-metric
  there to e.g. 900, so SIM only kicks in when neither wired nor WLAN
  provides a route.

## Debian version: 13 stays, no jump to 14 (decided 2026-09-18)

Stephan's question: "Would it already make sense today to test with Debian 14
and the current GNOME version?" Answer after weighing it up: **no, we stay on
Debian 13 and GNOME 48** (state on the device: 13.7, GNOME Shell 48.7,
Python 3.13.5).

The reasons, in order of weight:

1. **Debian 14 ("Forky") is currently *testing*, i.e. a moving base.**
   Security updates arrive there with a delay - for a device that sits in a
   blind user's everyday life, that is the wrong trade.
2. **A bug that is there today is gone tomorrow and a new one has appeared.**
   Exactly this pattern has already cost days in this project: a cause that
   can no longer be reproduced is no cause.
3. **No time pressure:** Debian 13 receives security updates until about
   2028, with LTS until about 2030.
4. **The Windows look breaks first.** `dash-to-panel`, `arc-menu` and
   `tiling-assistant` are GNOME extensions and typically break with every
   GNOME jump. That work is done once - when the target version is fixed.

**What really needs checking at the later jump is not GNOME, but the compiled
third-party libraries:** Vosk, sherpa-onnx (Parakeet), cairo/Pango, GTK4. They
depend on the Python version and glibc; if one of them fails, voice control
itself is affected, not just the look.

**The proposed approach when the time comes** (not built, deliberately
deferred): a container with Debian testing in which the **test bench**
(Prüfstand) runs. It needs neither a microphone nor a desktop - it plays back
the existing recordings and thereby checks Vosk, Parakeet, the number and
punctuation rules and the PDF generation in one pass, without touching the
T490. Sensible timing: **once Forky is frozen.**

## Security
- Recovery path for the USB security stick in case of loss/damage:
  provisionally implemented as a master passphrase (second LUKS key
  slot, asked for by `dialos-setup-home-partition.sh` during setup, at
  least 12 characters) – whether that
  should be the final solution (vs. a backup stick vs. no recovery) is
  not finally decided yet.
- **sudo for the default user `nutzer`: the state is not open, it is FULL
  ADMINISTRATOR** (as of 2026-09-25). `nutzer` is in the `sudo` group,
  `sudo -l -U nutzer` reports `(ALL : ALL) ALL` (checked on 2026-09-14). The
  password is generated randomly during setup, but
  `dialos-buero-setup-abschliessen.sh` **prints it in the terminal** - during
  the rebuild on 2026-09-25 it therefore ended up in the chat with Claude. So
  it is not secret: whoever has seen it or sets a new one has root on the
  device of a user who cannot notice. As far as known, the voice-driven
  maintenance calls do not need the group, because they go through narrow
  NOPASSWD rules on fixed paths. What needs to be clarified before any change
  (where the membership comes from, which groups `nutzer` really needs, the
  counter-check) is in `TODO.md`, item "Das Kundenkonto `nutzer` hat volle
  Root-Rechte" (the customer account has full root rights).

  **Earlier version (until 2026-09-25, superseded):** "How sudo/admin rights
  for the default user should work is still open: a normal password,
  passwordless sudo scoped to specific maintenance commands only, or fully
  passwordless. Currently a random password is generated per build (not
  stored in the repo) instead of a fixed placeholder." - "open" hid the fact
  that full rights already existed, and "per build" dates from the time of
  the ISO builds, which have not existed since 2026-08-16. The three
  variants remain valid as a basis for the decision.
- A self-hosted RustDesk relay server (hbbs/hbbr) is planned for later,
  once the system runs stably — no concrete timing/process yet.
- Boot-time key combination for direct `dialosadmin` access (instead of
  properly logging off/on, see sicherheit-datenschutz.en.md, section
  "Automatic login"): technically possible (a dedicated early boot
  service that briefly listens for a held key, e.g. via raw
  `/dev/input` access, and reroutes the autologin target via `gdbus`
  depending on the result), but deliberately deferred. **Corrected
  2026-08-14:** This entry originally listed GNOME "switch user" as an
  already-reliable alternative - that was wrong. A test finding from
  2026-08-13 shows that "switch user" leaves `nutzer`'s session active
  in the background and can trigger a Bluetooth/audio conflict between
  two concurrently running `dialos-start-ansage.py` instances. Current
  practice instead: properly log `nutzer` off, then log in as
  `dialosadmin` - works, but is one more step than a boot-time key
  combination would offer. This key combination therefore remains a
  genuine, still-open improvement option (not just a "nice-to-have" as
  originally noted), precisely because the direct route via "switch
  user" is off the table. Risk if implemented: needs a clean time
  window, otherwise a random keypress during a normal customer boot
  could unintentionally trigger the admin path instead of the normal
  `nutzer` autologin.

## System
- ~~Spell-checking is missing~~ **Done 2026-09-14:** `hunspell-de-de` and
  `hunspell-en-us` are now in the package list. They were already on the
  device, but only indirectly via `task-german-desktop`. `aspell` on purpose
  not - no program on the device uses it. The old rationale (Docker chroot)
  had been outdated since the move to path A anyway.
- The single-instance lock of `dialos-start-ansage.py` uses a fixed path
  in shared `/tmp` (`/tmp/dialos-start-ansage.pid`). The same design
  caused trouble on 2026-08-16 with the speaking marker: because of the
  sticky bit one account can neither overwrite nor delete another's
  file, and the failure stays silent. The marker was moved to
  `$XDG_RUNTIME_DIR`; this lock file has not been.

## Voice control
- Wake-word engine for battery-saving continuous listening not yet
  finally decided (proposal: openWakeWord).
- **Fallback to the built-in devices - Stephan's ruling of 2026-08-16:
  must ALWAYS be guaranteed.** The reference device is the AIRHUG headset
  (see [hardware.en.md](hardware.en.md)), but a switched-off, empty or
  disconnected Bluetooth device must never leave DialOS mute or deaf. For
  a blind user that would be the total failure: they do not notice the
  headset is off and simply get no feedback at all.

  The basis for this was the comparison test of 2026-08-13 (AIRHUG vs.
  the built-in laptop microphone: 6 of 8 test sentences exactly correct
  over Bluetooth, noticeably weaker with the built-in microphone).

  **Reversed since 2026-08-17, and for input completely:** speech input
  now always uses the **built-in microphone**; output continues over the
  Bluetooth speaker whenever it is connected. Three reasons:

  - As soon as anything opens the Bluetooth microphone, the headset drops
    to HFP - playback then runs at phone quality (1 channel, 16000 Hz
    instead of 2 channels, 48000 Hz). On 2026-08-17 switching back got
    stuck **three times**.
  - Echo cancellation exists only on the built-in path; over Bluetooth,
    recognition would again hear the system's own announcement.
  - The comparison test itself is **not reliable**: it ran with the
    built-in microphone over-amplified by 60 dB (see TODO.en.md, "repeat
    the microphone comparison"). It may not have measured the microphone
    at all, but the clipping.

  **Implementation status (corrected 2026-08-16 - this previously said
  "not implemented", which was wrong):**
  - **Microphone: implemented.** ~~`waehle_mikrofon_fuer_lautstaerke()` in
    `dialos-start-ansage.py` takes a `bluez_input.` source if one exists,
    otherwise the first non-monitor source - i.e. the built-in mic.~~
    **Superseded since 2026-08-17** (only added here on 2026-09-25): the
    order is reversed. The voice services pick their microphone
    themselves, in this order: (1) the echo source
    `dialos_mikrofon_ohne_echo`, which itself sits on the built-in
    microphone, (2) the built-in microphone, (3) Bluetooth **only** if
    there is no built-in one at all. Switching the AIRHUG to HFP therefore
    only happens in that fallback.
  - **The default microphone for all other programs deliberately stays
    the raw built-in one** (Stephan's decision, 2026-09-25). Firefox, and
    therefore Jitsi, has its own echo cancellation; with the cleaned
    source it would run twice and the other side would hear washed-out
    speech. On 2026-09-25 the echo source was the default for a few hours
    via `priority.session = 2500` and was reverted the same evening
    (details in [Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md) and
    [anwendungen.en.md](anwendungen.en.md)).
  - **Speaker: implicitly implemented.** `spd-say` speaks through
    speech-dispatcher's default sink; when the Bluetooth device
    disappears, PipeWire moves the default sink to the built-in one by
    itself.
  - **Speaker: verified on 2026-08-16 with the headset switched off -
    sound came from the built-in speaker.** The output side is therefore
    proven.
  - **Microphone: not yet tested without Bluetooth.** That is the
    remaining open item - not a missing implementation. It can be checked
    by deleting the remembered volume value
    (`sudo rm /home/nutzer/.config/dialos/lautstaerke`) and logging in as
    `nutzer` with the headset off: the question then comes again and has
    to be understood through the built-in microphone.
    **Settled by the switch of 2026-08-17** (added 2026-09-25): since then
    DialOS always listens through the built-in microphone, even when the
    speaker is connected. The path listed here as untested is therefore
    the everyday one and has been used in every session since.

  **Not covered and harder:** a device that is *connected* but transmits
  nothing (nearly dead battery, radio interference). No fallback triggers
  there, because from the system's point of view everything looks fine.
  That would need real feedback about playback, not just about the
  connection.
- Prioritization of WhatsApp vs. Signal as messenger still open.

## Project/repository
- Logo: a first draft exists as a placeholder, Stephan is working on his
  own design in parallel.

## Already decided (to avoid re-discussing)
- Debian remains the base (no switch to an atomic system).
- Initial setup runs fully voice-guided, including for users who are
  completely alone.
- The shipping goal is a laptop with a built-in SIM, phone tethering is
  the fallback.
- Contacts are synchronized continuously (CardDAV), not just imported
  once.

## 2026-08-13: Bluetooth speaker/voice output sometimes inaudible after login

**Symptom:** After logging in, the startup announcement over the
Bluetooth speaker (AIRHUG 01) intermittently stayed silent - sometimes
it worked, sometimes not, with no recognizable pattern.

**Suspected root cause:** GNOME "switch user" (instead of a proper
logout) left old sessions active in the background - at times `nutzer`
and `dialosadmin` sessions ran simultaneously on `seat0`, each with its
own `dialos-start-ansage.py` instance (the script never ends on its
own because of the network background monitoring). Multiple instances
presumably competed over `bluetooth_reconnect_alle()` and the audio
muting in `dialos-say.py`.

**Fix (dialos-start-ansage.py):**
- `alte_instanz_beenden()` ("terminate old instance"): lock file
  `/tmp/dialos-start-ansage.pid`, terminates any still-running old
  instance of the same account on startup (doesn't work across
  accounts, since the script has no sudo rights - that's intentional).
- `bluetooth_debug_snapshot()`: writes two timestamped snapshots on
  every run (`bluetoothctl info` per paired device + `pactl list sinks
  short` + `pactl get-default-sink`) to
  `/tmp/dialos-bluetooth-debug.log`, right before and after the
  reconnect attempt.

**Practical rule:** Always switch accounts via a proper **logout**,
never via "switch user" - otherwise old sessions stay active and
compete for Bluetooth/audio hardware.

**Status:** No further failure observed since the fix, including
across a real reboot with autologin for `nutzer`. Not yet conclusively
confirmed over a longer period - check
`/tmp/dialos-bluetooth-debug.log` if it recurs.
