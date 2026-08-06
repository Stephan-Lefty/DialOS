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

## Voice control
- The concrete intent layer (custom middleware vs. an existing framework
  as a starting point) not yet decided.
- Wake-word engine for battery-saving continuous listening not yet
  finally decided (proposal: openWakeWord).

## Telephony
- Prioritization of WhatsApp vs. Signal as messenger still open.

## Project/repository
- GitHub repository for Stephan-OS not yet created — started locally,
  decision on public/private and timing of the push still pending.
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
