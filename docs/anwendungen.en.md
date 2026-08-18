[Deutsch](anwendungen.md) | [English](anwendungen.en.md)

# Applications: which program for which purpose

The place to look up **what** DialOS uses to do a job - and why that one.
Settled with Stephan on 2026-08-18, when the "applications" block began.

The voice commands are in [sprachbefehle.en.md](sprachbefehle.en.md), not
here. This file answers "which program", that one "which sentence".

## The selection criterion is not usability

It is **controllability from outside.** The user cannot see the screen; a
program that can only be operated through its own interface is worthless to
DialOS - even if it were the best of its kind. What is required is a
command line or a D-Bus interface.

An already installed program failed on this on 2026-08-18:
`gnome-podcasts` is present and works, but has no command line. That rules
it out, although it would have been the obvious choice.

## Settled

| Purpose | Program | Why |
|---|---|---|
| Browser | **Firefox ESR** 140 | In place from the start; start page via enterprise policy, see [Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md) step 10. |
| Mail, calendar, contacts | **Thunderbird** 140 | One program for all three - each additional one would mean another set of voice commands. Evolution and GNOME Calendar are deliberately only hidden, not removed (they hang off `gnome-core`). |
| Support/remote help | **RustDesk** 1.4.9 | Deliberately disabled and startable only on explicit request, see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md). |
| Radio | **Shortwave** 5.0.0 | For the radio-browser.info station database. Only that lets a **spoken name** be resolved into a stream - "play Radio Tirol". Rhythmbox can play streams too, but only from hand-maintained addresses, and the user does not know those. |
| Local music | **Rhythmbox** 3.4.8 | `rhythmbox-client` does everything voice commands need - verified 2026-08-18: `--play`, `--pause`, `--next`, `--previous`, `--play-uri`, `--set-volume`, `--print-playing`. The last one matters: DialOS can announce what is playing. |
| Podcasts, audiobooks | **Rhythmbox** (the same program), resume position by DialOS | Podcasts are in the core (GSettings schema `org.gnome.rhythmbox.podcast`), not an extension. One program less, and above all one player less - see "Only one player" below. **But Rhythmbox does not provide the resume position** - see "The position belongs to DialOS" below. |
| Letters | **LibreOffice Writer** 25.2 | A letter must be printable or sendable as a PDF, with sender and date. The only installed program with templates and printing. |
| Notes, shopping lists | **no program - text files** | A shopping list must be read out, added to and ticked off, all by voice. Any interface is a detour the user never sees. DialOS manages them as `.txt` in a folder: nothing to install, nothing that breaks on an update, and the list stays readable even when DialOS is not running. |
| Video chat | **Jitsi Meet in Firefox** | Account-free and startable from a link, see [telefonie.en.md](telefonie.en.md). Camera present and detected (`/dev/video0`). Not affected by deferring telephony: Jitsi needs no extra hardware. |
| Updates | **unattended-upgrades** + voice command | Two separate things, deliberately: security updates run automatically in the background, because a blind user must not have to look after security holes. Anything larger comes only on request with a yes/no confirmation, because an upgrade that changes the desktop must never arrive unasked. Package not installed yet. |

## Open

| Purpose | State |
|---|---|
| **Telephony** | **Deferred** (Stephan, 2026-08-18). It depends on the hardware decision in [telefonie.en.md](telefonie.en.md) - built-in SIM or paired phone - and that is open. |
| **Chat** | [telefonie.en.md](telefonie.en.md) prioritises WhatsApp Web in the browser, because of its prevalence among family and friends. Confirmation for this list is still pending. |
| **Video recording** | Purpose not yet clarified. A video message to the family is a different thing from "record what the tradesman said" - the choice depends on it. `gnome-snapshot` is installed but has no command line; `ffmpeg` would be available (7.1.5). |

## Approved, not yet built

Stephan approved these in full on 2026-08-18 ("all your points have to go
in"). They are therefore in scope but not yet implemented - the separation
is deliberate, so that the planned does not look like the existing.

The first two are not applications but preconditions for four of the
above:

- **Dictation (speech to text)** - measurements and open points in
  [diktat.en.md](diktat.en.md). The user cannot produce letters, notes,
  mail or chat messages at all without dictation. **`vosk-model-de-big`,
  3.2 GB, is already on the disk** - so free dictation needs no new
  technology, only work. Not to be confused with the restricted grammar of
  command recognition: those are two operating modes of the same tool.
- **Reading out mails, documents and web pages.** The counterpart to
  dictation and just as central for the target group.
- **Scanning post and reading it out.** `simple-scan`, `sane-utils` and
  CUPS are installed, only `tesseract-ocr` is missing (5.5.0 available).
  With it DialOS solves a problem no screen reader can: the letter from the
  health insurer that arrives on paper.
- **Audiobooks.** Deliberately to be considered separately from music,
  because the resume position matters there - someone who has to restart an
  eight-hour audiobook after switching on will not listen to it.
- **Alarm, timer, reminders.** "Remind me at three about the tablets."
- **Shutting down and locking the computer by voice**, and **announcing
  appointments and weather** (from Thunderbird; the weather query is
  already in the login announcement).

## Mail: Thunderbird is the interface, not the engine

Checked on 2026-08-18, when Stephan created the test address
`proband@dialos.org`. Thunderbird's command line knows exactly **one**
function:

```
thunderbird -compose "to='recipient@tld.org'"
```

**Reading** mail from outside is not possible at all, and `-compose` only
opens a prefilled window that somebody has to click. By the criterion
above - controllability from outside - Thunderbird therefore fails as the
engine for voice operation, exactly like `gnome-podcasts`.

**The consequence is not a new choice of program but a division of
labour:**

| Task | Who |
|---|---|
| reading mail out, dictating and sending mail | **DialOS directly over IMAP/SMTP** (`imaplib`, `smtplib` - Python's standard library, no extra package) |
| viewing and editing mail by a sighted helper | Thunderbird |
| calendar and contacts | Thunderbird, uncontested |

**Open and deliberately not decided here:** this means DialOS needs the
mailbox credentials itself. Whether they belong in the GNOME keyring
(libsecret) or in a file owned only by the account is a question of
security architecture - see
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md) and
`TODO.en.md`.

On the test mailbox: dialos.org's mail server is `s111.goserver.host`.
**There are no autoconfig records** (`_imaps._tcp`, `_submission._tcp`,
`_autodiscover._tcp` are all empty), so Thunderbird has to guess the
settings - the host's IMAP/SMTP details should be kept at hand.

### Which server name DialOS uses - and why not the obvious one

Measured on 2026-08-18 against the test mailbox. The host's certificate is
`CN=*.goserver.host`, with alternative names only `*.goserver.host` and
`goserver.host`. **`imap.dialos.org` is not among them.** Result with
strict verification (`ssl.create_default_context()`):

| Connection | Result |
|---|---|
| `imap.dialos.org:993` | rejected, hostname mismatch |
| `imap.dialos.org:143` + STARTTLS | rejected, same reason |
| `s111.goserver.host:993` | **OK** |
| `smtp.dialos.org:587` | rejected |
| `s111.goserver.host:587` + STARTTLS | **OK** |

**DialOS therefore uses `s111.goserver.host`.** Thunderbird only works
because a certificate exception was confirmed during setup - the profile
file `cert_override.txt` contains `imap.dialos.org:143`. For an interface
where a human consciously agrees, that is fine; **DialOS must not copy
that route.** A silently unverified connection is invisible to a blind
user - they could never notice someone sitting in between.

**Do not hardcode it:** `s111` is the name of a shared server at the host
and changes if the mailbox is migrated. The name belongs in the
configuration. It can also be derived from the domain's MX record - today
`dialos.org` MX points exactly at `s111.goserver.host`.

**A side benefit: the server supports IDLE.** So DialOS does not have to
poll every minute but can be notified. "You have a new mail from..."
arrives when it arrives, and costs no battery in between.

**A mistake of my own while checking, because it can recur:** my first
test reported `imap.dialos.org` as fine. The cause was calling
`imaplib.IMAP4_SSL` without an explicit `ssl_context` - then it is not
established whether verification happens at all. For SMTP I had set the
context, and that is exactly where it failed; so the comparison was
worthless. **Whoever tests TLS must pass the verification context
explicitly.**

## Two rules that follow from this list

**Only one player may run at a time.** If the user says "louder" or "stop"
while music plays in one program and a podcast in another, the command is
no longer unambiguous - and the user cannot look to see which window is in
front. Hence Rhythmbox for music AND podcasts: exactly two players remain,
Rhythmbox and Shortwave, and DialOS must stop one before starting the
other.

**The echo-cancelled source must never become the default source.**
Checked on 2026-08-18, and it currently holds only because it is
WirePlumber's default - nobody laid it down:

| Who records | Source |
|---|---|
| voice service (`parec`) | `dialos_mikrofon_ohne_echo` |
| Firefox, hence Jitsi too | raw built-in microphone (default) |

Firefox brings its own echo cancellation for WebRTC. If it got our
cleaned-up source, the processing would run twice and the far end would
hear thin, washed-out speech with artefacts. So whoever changes the default
source degrades audio quality in video calls, without the connection being
visible.

**The position belongs to DialOS, not to the player.** Checked on
2026-08-18: Rhythmbox's library knows `play-count` and `last-played`, but
**no** `playback-position` and no `bookmark`. So an eight-hour audiobook
would restart from the beginning after switching on - exactly the case
Stephan named as disqualifying.

The answer is not a second player (that would break the rule above) but:
**DialOS reads the position over MPRIS and sets it again.** The MPRIS
extension is present in Rhythmbox, `gdbus` is installed.

This is not a workaround but the better solution. DialOS has to know the
position anyway in order to announce it - "resuming at three hours twelve"
is something no player in the world can speak for us. And it is the same
rule that struck three times on 2026-08-17: **do not rely on another
component's state, keep your own** (see `CLAUDE.md`).
