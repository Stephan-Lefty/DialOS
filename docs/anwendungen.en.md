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
| Radio | **Shortwave** 5.0.0 today - **Rhythmbox in future** (Stephan's decision of 2026-09-25, **not built yet**) | **In future:** DialOS looks the station up itself in the radio-browser.info database - the same one Shortwave uses - and has Rhythmbox play the address it found via `rhythmbox-client --play-uri`. **Why the change:** Shortwave has no command line and no interface through which a station could be set; over MPRIS there is only play/pause of whatever was heard last. By the criterion above - controllability from outside - that is not enough for "play Radio Tirol". This leaves **one** player for radio, music, podcasts and audiobooks (see "Only one player" below). **Today** "Radio öffnen" opens Shortwave, and "Radio einschalten" says DialOS cannot do that yet. **Before (until 2026-09-25) this read:** Shortwave for the radio-browser.info station database - only that would let a **spoken name** be resolved into a stream; Rhythmbox could play streams too, but only from hand-maintained addresses, which the user does not know. That is exactly the gap DialOS now closes itself, by looking the address up. |
| Local music | **Rhythmbox** 3.4.8 | `rhythmbox-client` does everything voice commands need - verified 2026-08-18: `--play`, `--pause`, `--next`, `--previous`, `--play-uri`, `--set-volume`, `--print-playing`. The last one matters: DialOS can announce what is playing. |
| Podcasts, audiobooks | **Rhythmbox** (the same program), resume position by DialOS | Podcasts are in the core (GSettings schema `org.gnome.rhythmbox.podcast`), not an extension. One program less, and above all one player less - see "Only one player" below. **But Rhythmbox does not provide the resume position** - see "The position belongs to DialOS" below. |
| Letters | **LibreOffice Writer** 25.2 | A letter must be printable or sendable as a PDF, with sender and date. The only installed program with templates and printing. |
| Notes, shopping lists | **no program - text files** | A shopping list must be read out, added to and ticked off, all by voice. Any interface is a detour the user never sees. DialOS manages them as `.txt` in a folder: nothing to install, nothing that breaks on an update, and the list stays readable even when DialOS is not running. |
| Video chat | **Jitsi Meet in Firefox** | Account-free and startable from a link, see [telefonie.en.md](telefonie.en.md). Camera present and detected (`/dev/video0`). Not affected by deferring telephony: Jitsi needs no extra hardware. |
| Updates | **unattended-upgrades** + voice command | Two separate things, deliberately: security updates run automatically in the background, because a blind user must not have to look after security holes. Anything larger comes only on request with a yes/no confirmation, because an upgrade that changes the desktop must never arrive unasked. Installed and set up on 2026-08-20 (`unattended-upgrades` 2.12). Configuration in `/etc/apt/apt.conf.d/52dialos-unattended-upgrades`, with the reasoning in the source itself. Confirmed by a trial run: everything except `Debian-Security` is pinned at `-32768`, i.e. "never" - including `trixie-updates` and the Anthropic source of the admin machine. |

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

**Status 2026-09-25:** two items on this list have been built since -
dictation and the weather announcement on request. They stay here, clearly
marked, so that the approval of 2026-08-18 remains readable in full; what
they can do today is in [sprachbefehle.en.md](sprachbefehle.en.md).

The first two are not applications but preconditions for four of the
above:

- **Dictation (speech to text) - built.** Letters and notes are recognised
  by **Parakeet** (built in for good since 2026-09-16, because on the test
  bench it made far fewer word errors and is the only one that sets
  punctuation itself), commands and the shopping list still by **Vosk**.
  Details in [diktat.en.md](diktat.en.md) and [pruefstand.en.md](pruefstand.en.md).
  **Before (until 2026-09-16) this read:** measurements and open points in
  [diktat.en.md](diktat.en.md). The user cannot produce letters, notes,
  mail or chat messages at all without dictation. **`vosk-model-de-big`,
  3.2 GB, is already on the disk** - so free dictation needs no new
  technology, only work. Not to be confused with the restricted grammar of
  command recognition: those are two operating modes of the same tool.
- **Reading out mails, documents and web pages.** The counterpart to
  dictation and just as central for the target group.
- **Scanning post and reading it out.** `sane-utils` (`scanimage`) and
  CUPS are installed (`simple-scan` deliberately removed on 2026-09-25 -
  DialOS scans via `scanimage`), only `tesseract-ocr` is missing (5.5.0 available).
  With it DialOS solves a problem no screen reader can: the letter from the
  health insurer that arrives on paper.
- **Audiobooks.** Deliberately to be considered separately from music,
  because the resume position matters there - someone who has to restart an
  eight-hour audiobook after switching on will not listen to it.
- **Alarm, timer, reminders.** "Remind me at three about the tablets."
- **Shutting down and locking the computer by voice**, and **announcing
  appointments and weather** (from Thunderbird; the weather query is
  already in the login announcement). **Weather on request has been built
  since 2026-09-16** ("Wie ist das Wetter?", "Wie wird das Wetter?").
  Shutting down, locking and announcing appointments are still not built.

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

> **Corrected on 2026-09-21: the paragraph above holds for the command line
> only.** Thunderbird *is* controllable from outside - not through arguments
> but through a **MailExtension**. Measured on the device: create a contact,
> file a draft in the *account's* drafts folder (which is uploaded to the
> server), list accounts and address books. No Experiment API needed, and
> Debian's Thunderbird accepts the unsigned extension
> (`xpinstall.signatures.required=false`). The route is described in
> [erweiterungen.en.md](erweiterungen.en.md), section "The Thunderbird bridge"
> (only there since 2026-09-25 - before, this sentence pointed to a place where
> it was not yet written), the extension's source in the folder
> `thunderbird-erweiterung/`, the counterpart in `dialos-thunderbird-bruecke.py`.
>
> **What follows is a line, not a replan:** *reading from outside is fine,
> writing is not.* The search index keeps reading the mbox files - that
> disturbs nobody and needs no running Thunderbird. Writing happens through
> Thunderbird itself, exclusively. The two errors that cost 2026-09-18 (LF
> instead of CR LF, and `X-Mozilla-Status: 0008`, which means DELETED) cannot
> return: both came from rebuilding someone else's file format.
>
> **The division of labour in the table still stands.** For *reading out and
> sending* without Thunderbird, DialOS still needs IMAP/SMTP - an extension
> can only act while the program runs. It is the way into Thunderbird's data,
> not a replacement for having one's own access to the mailbox.

**The consequence is not a new choice of program but a division of
labour:**

| Task | Who |
|---|---|
| reading mail out, dictating and sending mail | **DialOS directly over IMAP/SMTP** (`imaplib`, `smtplib` - Python's standard library, no extra package) |
| viewing and editing mail by a sighted helper | Thunderbird |
| calendar and contacts | Thunderbird, uncontested |

> **Superseded since 2026-09-25: the first row of the table was never built,
> and that is how it stays.** DialOS has no IMAP/SMTP access of its own
> (planned on 2026-08-18). Instead DialOS controls Thunderbird through its own
> MailExtension **DialOS-Brücke** (`bruecke@dialos.org`, see
> [erweiterungen.en.md](erweiterungen.en.md), section "The Thunderbird
> bridge"): filing drafts, sending, contacts. The concern from the box above -
> "an extension can only act while the program runs" - got a different answer
> than expected: if Thunderbird is closed, a draft is queued and filed at the
> next start, and for sending DialOS opens Thunderbird itself. Reading still
> happens from outside, from Thunderbird's mbox files (the search index of the
> DialOS-Suche extension).
>
> **Why it stays that way:** it follows from the line of 2026-09-21 in the box
> above - *reading from outside is fine, writing is not*. A mail sent over
> DialOS's own SMTP would be written past Thunderbird. And since 2026-09-25 the
> password lives in Thunderbird's password store; an access of our own would
> need a second place for the same password.
>
> The table stays as the state of 2026-08-18.

**Open and deliberately not decided here:** this means DialOS needs the
mailbox credentials itself. Whether they belong in the GNOME keyring
(libsecret) or in a file owned only by the account is a question of
security architecture - see
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md) and
`TODO.en.md`.

> **Superseded - decided, and the decision has since been superseded itself.**
> On 2026-08-18 it fell, in `TODO.md`, on a file in `/home/nutzer` with mode
> 0600. **That file was never built**, because it was only meant for DialOS's
> own IMAP access, which does not exist (see above). **Since 2026-09-25:** the
> mail account comes from the personal-data form; on saving,
> `dialos-mailkonto.py` creates it in Thunderbird. The **password is
> deliberately not a field** in `persoenliche-daten.txt` but goes straight into
> Thunderbird's encrypted password store - so it never stands in a DialOS file
> (Stephan's choice against the simpler route "Thunderbird asks by itself").
> The fields are in [kundendaten-felder.en.md](kundendaten-felder.en.md).

On the test mailbox: dialos.org's mail server is `s111.goserver.host`.
**There are no autoconfig records** (`_imaps._tcp`, `_submission._tcp`,
`_autodiscover._tcp` are all empty), so Thunderbird has to guess the
settings - the host's IMAP/SMTP details should be kept at hand.

> **Since 2026-09-25 the servers come from the form.** `persoenliche-daten.txt`
> has `imap_server`, `imap_port`, `smtp_server` and `smtp_port` for this (plus
> `mail_benutzer`, if the provider requires a different login name). **For
> well-known providers they stay empty** - the servers then come from Mozilla's
> provider database (ISPDB), the same one Thunderbird itself draws on. Only for
> own domains such as dialos.org does the database not help; there the server
> details have to be entered in the form. A hint based on the domain's MX record
> is an open item in `TODO.en.md`.

### Which server name DialOS uses - and why not the obvious one

> **Note since 2026-09-25:** this section was about DialOS's planned own
> IMAP/SMTP access, which is not being built (see above). DialOS today opens no
> mail connection of its own; Thunderbird holds the connection, with the server
> details from the form. The measurements and the lesson on TLS verification
> still hold, which is why they stay here.

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

## Archive and search: MailBurg's extraction, but an index of our own

Settled with Stephan on 2026-09-17, when he asked for an archive solution
with reading out and a voice dialogue - searching letters, documents,
notes and e-mails by voice. This is being built as the first
**extension**, called DialOS-Suche, see
[erweiterungen.en.md](erweiterungen.en.md).

**The decision went against a fourth archive of our own.** DialOS already
has two halves: `dialos-archiv.py` (PDF archive in
`~/Dokumente/Archiv/DialOS-DATA/` and on the stick) and
`dialos-mailarchiv.py` (mail from Thunderbird's local mbox files). A third
route alongside them would, by the one-player rule below, be exactly the
mistake this file is meant to prevent.

**The draft first had MailBurg as the whole engine. Stephan's question of
2026-09-17 corrected that:** „Brauchen wir denn MailBurg als komplettes
Programm oder nur Teile? Denn MailBurg wird ja mit einem anderen Anliegen
erstellt." (Do we need MailBurg as a complete program or only parts? After
all, MailBurg is being built with a different concern.) That is exactly
it, and the difference is not size.

### MailBurg archives. DialOS-Suche only has to find.

MailBurg copies mail into a content-addressed store of its own (`.eml.zst`,
SHA-256 as the file name, hash chain in the journal) - because it must be
able to **prove** that nothing was altered. For a GoBD archive of business
post that is right.

**But DialOS's documents are already lying there:** letters in
`~/Dokumente/`, PDFs under `~/Dokumente/Archiv/DialOS-DATA/`, notes in
`~/Notizen/`, mail in Thunderbird's mbox. Writing them out a second time
would be duplication - twice the space, and from then on two truths that
can drift apart.

On top of that comes everything that has no business on a private device:
audit-proof storage, tombstones instead of real deletion, RFC 3161
timestamps, retention periods. For private individuals the GDPR's
household exemption applies. MailBurg does have a mode of its own for
that, but the apparatus would stay installed.

### What is shared and what is not

Counted on 2026-09-17:

| Part of MailBurg | Lines | DialOS-Suche |
|---|---|---|
| `extract/` - making PDF, OCR, Office readable | 1.360 | **is shared** |
| `core/` - archive, index, encryption, journal | 12.091 | no |
| `ui/` - graphical interface | 12.542 | no |
| `server/` - web interface | 1.600 | no |

**What is shared is the extraction chain**, because dearly earned
knowledge sits in there that nobody gets right a second time: `pdftotext`
with `pypdf` as a fallback, OCR via `pdftoppm` and `tesseract` with the
measured pixel limit `MAX_KANTE=5000` against the 523-megapixel crash on
iPhone scans, Office files without binary rubbish.

**The index is built anew, lean.** SQLite FTS5 is part of the standard
library; an index over files that already lie in the file system is a few
hundred lines - without archive storage, without a journal, without
retention periods. In exchange it has what DialOS needs and MailBurg does
not have: a column with the **Cologne phonetics** of sender names, so that
„Meier", „Mayer" and „Maier" fall together. That catches recognition
fuzziness structurally instead of loading it onto the user as a follow-up
question.

**Imported rather than called over the command line** - and that is a
correction of the first draft, which settled it the other way round.
Calling over the command line was right as long as MailBurg was to be the
whole engine; for a shared module, importing is the right way. It also
costs nothing: MailBurg's core has `dependencies = []`. Without the extras
neither PySide6 nor the server comes along.

**Licence checked:** MailBurg is MIT, DialOS GPL-3.0 - MIT code may go
into a GPL project.

### The recognizer for the search term is already there

A spoken search term is **text, not a command** - the same division of
labour applies as in dictation: Vosk takes the start sentence,
**Parakeet** the term. The only new thing to clarify is whether Parakeet
can be given a dictionary built from the most frequent sender names in
one's own index - the way dictation has its personal dictionary.

### Open

Whether the index has to lie encrypted. It sits on the LUKS partition of
`nutzer`, so it is protected while the device is switched off - an
encryption of its own would only help against an attacker inside the
running session, and he would have the documents themselves as well.
Equally open: whether `dialos-archiv.py` and `dialos-mailarchiv.py`
remain or are absorbed into the index.

## Two rules that follow from this list

**Only one player may run at a time.** If the user says "louder" or "stop"
while music plays in one program and a podcast in another, the command is
no longer unambiguous - and the user cannot look to see which window is in
front. Hence Rhythmbox for music AND podcasts: exactly two players remain,
Rhythmbox and Shortwave, and DialOS must stop one before starting the
other.

> **Changed decision of 2026-09-25 (Stephan): radio in future through
> Rhythmbox as well** - see the "Radio" row in the table above. Then there is
> only **one** player for radio, music, podcasts and audiobooks, and the rule
> takes care of itself: there is nothing left that DialOS would have to stop
> before starting, and "louder" or "stop" always means the same program. **Not
> built yet** - until then there are still two programs: "Radio öffnen" opens
> Shortwave, "Musik öffnen" Rhythmbox.

**The echo-cancelled source must never become the default source.**
Checked on 2026-08-18, and it currently holds only because it is
WirePlumber's default - nobody laid it down:

> **Superseded since 2026-09-25: today it is laid down explicitly.**
> `/etc/pipewire/pipewire.conf.d/99-dialos-echo-unterdrueckung.conf` says
> "BEWUSST KEIN priority.session" (deliberately no priority.session) at the echo
> source, with the reasoning. The DialOS voice services pick
> `dialos_mikrofon_ohne_echo` themselves; the default microphone deliberately
> stays the raw built-in one. The occasion was the incident in the paragraph
> below.

| Who records | Source |
|---|---|
| voice service (`parec`) | `dialos_mikrofon_ohne_echo` |
| Firefox, hence Jitsi too | raw built-in microphone (default) |

Firefox brings its own echo cancellation for WebRTC. If it got our
cleaned-up source, the processing would run twice and the far end would
hear thin, washed-out speech with artefacts. So whoever changes the default
source degrades audio quality in video calls, without the connection being
visible.

**On 2026-09-25 exactly that happened - and was reverted.** After the rebuild
both accounts had the raw microphone set, which looked like a fault, and the
echo source was made the default via `priority.session` - without reading this
rule. Reverted the same evening on Stephan's decision. The raw microphone as the
default is the intended state, not a fault. Since then the sentence stands as a
warning in the configuration file itself - where the next change would start,
not only in this file.

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
