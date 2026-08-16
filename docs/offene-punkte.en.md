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

## Security
- Recovery path for the USB security stick in case of loss/damage:
  provisionally implemented as a master passphrase (second LUKS key
  slot, asked for by the installer on every install) – whether that
  should be the final solution (vs. a backup stick vs. no recovery) is
  not finally decided yet.
- How sudo/admin rights for the default user ("nutzer") should work is
  still open: a normal password (safer, but the voice-guided maintenance
  flow then has to work around it specifically), passwordless sudo
  scoped to specific maintenance commands only, or fully passwordless.
  Currently a random password is generated per build (not stored in
  the repo) instead of a fixed placeholder.
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

## ISO build
- Spell-checking (hunspell-de-de/hunspell-en-us, aspell) is missing
  from the ISO: the package `dictionaries-common`, which both depend
  on, reproducibly fails inside the Docker chroot build environment
  (likely missing D-Bus during package configuration). Left out for
  the first working build for now, needs to be added back (possibly
  installed after first boot instead of at build time).

## Voice control
- Wake-word engine for battery-saving continuous listening not yet
  finally decided (proposal: openWakeWord).
- **Fallback to the built-in devices - Stephan's ruling of 2026-08-16:
  must ALWAYS be guaranteed.** The reference device is the AIRHUG headset
  (see [hardware.en.md](hardware.en.md)), but a switched-off, empty or
  disconnected Bluetooth device must never leave DialOS mute or deaf. For
  a blind user that would be the total failure: they do not notice the
  headset is off and simply get no feedback at all.

  The basis for this is the comparison test of 2026-08-13 (AIRHUG vs. the
  built-in laptop microphone: 6 of 8 test sentences exactly correct over
  Bluetooth at normal speaking volume, noticeably weaker with the
  built-in microphone). Bluetooth is therefore the primary path, the
  built-in devices are the fallback.

  **Implementation status (corrected 2026-08-16 - this previously said
  "not implemented", which was wrong):**
  - **Microphone: implemented.** `waehle_mikrofon_fuer_lautstaerke()` in
    `dialos-start-ansage.py` takes a `bluez_input.` source if one exists,
    otherwise the first non-monitor source - i.e. the built-in mic.
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
