[Deutsch](ersteinrichtung.md) | [English](ersteinrichtung.en.md)

# Initial setup & rollout

## Two-phase provisioning

**Clarification since 2026-08-16 (path A):** there is no "golden image"
that gets duplicated. Every device is set up individually in the office -
empty disk, the current Debian 13/GNOME ISO from debian.org, then the
three DialOS scripts (see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md)). A customer never sees
an installer; Calamares and `dialos-install` were removed accordingly.

1. **Office setup (Stephan)**: the device is fully set up, including a
   test run. Everything that can be handled in advance for privacy or
   security reasons (see below) happens here — not on site.
2. **Shipping**: laptop and security stick are shipped separately (see
   [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)).
3. **On-site setup at the user's home**: plug in the laptop, connect the
   stick, make the final settings.

## On-site setup is mandatorily voice-only

There is no exception to this: every on-site touchpoint must be either
purely physical (plugging in the stick, connecting power) or a pure voice
dialog — nothing may require seeing, typing, or reading. Consequence:
things like SIM activation also belong in the office setup, not on site.

## Fully voice-guided initial setup assistant

Runs automatically on the very first system start — independent of the
"call for help" command for RustDesk — and must also work if the user is
completely alone. A new software component (a state-machine dialog based
on Vosk+Piper, triggered by a first-run marker file).

**Status 2026-08-16: not implemented.** What does exist is the login
announcement (`dialos-start-ansage.py`) with its spoken volume question -
the system's first real voice dialog and therefore the template for this
assistant (announce → ask → answer via Vosk → remember the result). The
assistant itself, with name capture and voice selection, does not exist
yet.

Only the following is asked for on site, via voice:
- The user's **name**, with confirmation back ("I understood: Anna
  Schmidt. Is that correct?") and an option to correct it.
- **Greeting voice**: choosing between **two** voices via audio samples -
  **Michael** (`de_DE-thorsten-high`) and **Anna** (`de_DE-kerstin-low`).
  Changeable again at any time later, not just during initial setup.

  **Two instead of four, and that is a tightening rather than a saving**
  (Stephan, 2026-08-20: "rather 2 optimised voices than 8 that are merely
  OK"). The reason lies in what was measured the same day:

  - **Every voice needs settings of its own.** The speaking rate does not
    carry over: the same sentence takes 7.75 s for Thorsten at rate 0.88
    and **8.99 s** for Kerstin at the same value. And the pronunciation
    rules ("Tas tatur", "Ei Di", "Dial OS") are tuned to Thorsten - whether
    Anna needs them is still open. Eight voices would mean eight times that
    work, and without it each one sounds worse than it needs to.
  - **For a blind user the voice is not a feature but the entire
    interface.** A mediocre voice is therefore not a blemish to be offset
    by choice - a wide choice of mediocre voices is worse than two good
    ones.
  - **Two cover the actual preference:** male or female. Anything beyond
    that is taste, and taste can be added later when it is asked for.

  **Correction of an earlier assumption:** this used to say "each at the
  highest available speech quality". That is unreachable for the female
  voices - Piper offers only `eva_k-x_low`, `kerstin-low` and `ramona-low`
  for German, all at **16 000 Hz** against Thorsten's 22 050 Hz. Anna
  sounds audibly rougher than Michael, and that is not a settings question
  but the state of the available models.
- Possibly confirming pre-prepared accounts (see privacy variants below)
  — a plain yes/no answer, no dictation.

**Important design constraint**: email address/password are never
dictated by voice — speech recognition is error-prone for character
strings, and speaking a password out loud is a security risk in itself.

## Privacy variants for account setup

Not every user wants to simply hand over their credentials (email,
contacts). Two variants:

- **Variant 1 – "all data provided in advance"**: the user shares the
  necessary credentials with Stephan beforehand (e.g. by phone). The
  office sets up the email account and CardDAV contact sync completely.
  On site, only name + greeting voice remain, via voice.
- **Variant 2 – "user enters everything themselves" (privacy preserved)**:
  nothing is shared in advance. The voice assistant guides the user
  through the complete setup on site. For password-protected accounts,
  the **OAuth device flow** is used (as with smart TV logins): the system
  reads out a short code and a short URL, and the user confirms it on
  their own, already-trusted smartphone — the password is never spoken
  aloud, never typed, and Stephan never sees it at any point. Google
  supports this natively; iCloud is more limited (may require an
  app-specific password generated by the user themselves).

## Contact data: continuous synchronization

Contacts should be synchronized **continuously**, not just imported once.
Implementation: set up the CardDAV link once in the office (provided the
user's Google/iCloud credentials are available in advance), after which
it runs permanently and automatically in the background — new contacts on
the user's phone automatically appear in the Thunderbird address book,
with no further action needed. If the credentials aren't available yet
when packing the device, the link can be set up later via RustDesk remote
support, once the user has approved "call for help" at least once. As a
platform-independent fallback (if live sync isn't wanted/possible), a
one-time vCard (.vcf) export/import is used.

## Open questions

- Who ultimately decides between variant 1 or 2 per user (contacting
  Stephan in advance) is an organizational, not a technical, question.
