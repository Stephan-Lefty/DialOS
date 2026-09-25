[Deutsch](architektur-uebersicht.md) | [English](architektur-uebersicht.en.md)

# Architecture overview

## Goal

DialOS is a system based on Debian 13 (Trixie) + GNOME 48 for people
who can only use a computer to a limited extent — in particular blind and
motor-impaired individuals. It is not distributed as a live ISO but built
in the office on each device from a regular Debian installation (see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md); authoritative guide
since 2026-09-25: [installationsanleitung.md](installationsanleitung.md),
German only). There is no ISO any more, not even as a backup: a finished
device is backed up as a Rescuezilla image. (Until 2026-09-25 this said "an
ISO now exists only as a backup image" - outdated since the switch to
Rescuezilla on 2026-08-16.) The system must be fully voice-controllable,
including system maintenance, and work equally well for an 18-year-old as
for an 80-year-old.

## Target audience

Blind and motor-impaired users equally, with no priority given to either
group. The system therefore needs to both read content aloud excellently
(screen contents, notifications, confirmation prompts) and be fully
operable without keyboard or mouse.

## Core features

- Listening to radio, music, and podcasts
- Writing letters/texts
- Browser for search queries
- Using streaming media libraries (ARD, ZDF Mediatheken)
- Writing/sending emails
- Calendar with reminders
- Central, continuously synchronized contact database
- Telephony (landline replacement + mobile) and video calls
- Optional: WhatsApp/Signal as messenger
- Text-to-speech (reading the screen aloud)
- System maintenance fully controllable by voice
- Remote support for family members/technicians (RustDesk)

Details: see [telefonie.en.md](telefonie.en.md), [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md),
[sprachsteuerung.en.md](sprachsteuerung.en.md), [ersteinrichtung.en.md](ersteinrichtung.en.md).

## Software stack (as of 2026-09-25)

The "state" column separates what is decided from what is actually
built in: **installed** means the package comes from the DialOS package
list; **in use** means DialOS actively drives it; **planned** means
decided, but nothing of it is in the system yet.

This table replaces the version of 2026-08-16. The old one is in this
file's Git history; it was the state before the first voice command ran
(hassil "no command grammar yet", Vosk only for the volume question). Rows
nobody has re-checked since are marked as such.

| Area | Choice | Rationale | State |
|---|---|---|---|
| Distribution | Debian 13 + GNOME 48 | Best Orca/AT-SPI integration, hardware support; no jump to Debian 14 (decided 2026-09-18, see [offene-punkte.en.md](offene-punkte.en.md)) | in use |
| Command recognition | Vosk 0.3.45, small German model, **restricted grammar** (about 64 sentences) | Offline for privacy; free recognition reliably turns "gnome" into "genug" - with the sentence list it is word-for-word correct | in use, for all commands and the shopping list |
| Sentence templates → grammar | [hassil](https://github.com/OHF-Voice/hassil) (decided 2026-08-13, instead of Rhasspy) | Different phrasings of the same intent (18 to 80 year olds) from one template | in use, builds the command grammar |
| Free dictation (letters, notes) | Parakeet TDT 0.6B v3 (int8) via sherpa-onnx, model under `/usr/local/share/dialos-parakeet` | Test bench 2026-09-15: 2.8 % word errors and all punctuation right, Vosk 12.7 % without full stops | in use since 2026-09-16 |
| Writing aid | LanguageTool (local, Java) | Spelling and grammar in dictation, offline | in use |
| Speech output (TTS) | Piper (RHVoice dropped), voices Anna (`de_DE-kerstin-low`, shipping voice) and Michael (`de_DE-thorsten-high`) | More natural than espeak-ng | in use, via a speech-dispatcher generic module |
| Audio | PipeWire with echo cancellation (`module-echo-cancel`, WebRTC), source `dialos_mikrofon_ohne_echo` | Recognition must not hear its own announcement (about 32 dB attenuation measured) | in use; the voice services pick the echo source themselves, the default microphone for other programs deliberately stays the raw one (see [hardware.en.md](hardware.en.md)) |
| Mail/calendar/contacts | Thunderbird + **DialOS bridge** (MailExtension `bruecke@dialos.org`, native messaging, in every profile via `policies.json`) | Thunderbird saves and sends itself; DialOS has no IMAP/SMTP access of its own and does not need the mail password (see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)) | in use: drafts, sending, contacts; mail account via the personal-data form |
| Letter as PDF | own generator via cairo/Pango | Letterhead per DIN 5008, window envelope | in use |
| Low-level desktop control | Numen (Wayland-native, Vosk-based) | Mouse/window control for motor-impaired users | planned, not installed (as of 2026-08-16, not re-checked) |
| Screen reader | Orca | Standard GNOME screen reader | installed, pairing with Piper still open (as of 2026-08-16, not re-checked) |
| Radio | Shortwave today, Rhythmbox in future | Shortwave cannot be controlled from outside, see [anwendungen.en.md](anwendungen.en.md) | installed, "Radio öffnen" opens Shortwave; switch decided 2026-09-25, not built |
| Music, podcasts, audiobooks | Rhythmbox (one player for everything) | GNOME Music and GNOME Podcasts are removed by `dialos-aufraeumen.sh`, see [anwendungen.en.md](anwendungen.en.md) | installed |
| Word processing | LibreOffice Writer | — | installed |
| Browser | Firefox ESR | For search queries and ARD/ZDF Mediatheken (no native Linux client) | installed, home page set via enterprise policy |
| Remote support | RustDesk 1.4.9 (`.deb` from GitHub) | Open source, self-hostable, see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md) | package installed, service off; the "Hilfe rufen" voice command is built but deliberately deferred (not in the command grammar) |
| Video calls | Jitsi Meet (browser) | No account needed, WebRTC | planned |
| Telephony | ModemManager + GNOME Calls | see [telefonie.en.md](telefonie.en.md) | planned, not installed (no WWAN module in the test device) |
| Setup | Claude desktop app (Anthropic, proprietary, from their apt repository) | Helps with building and development | so far only on the development device; **whether it stays on customer devices is open** (see [lizenzen.en.md](lizenzen.en.md)) |

## Design principles

- **Offline-first**: speech recognition and output run locally, no cloud
  dependency — important for privacy with a vulnerable target group and
  for use while travelling without reliable internet.
- **Safety over convenience**: security-critical actions (system
  maintenance, approving remote support) always go through an explicit
  yes/no confirmation, regardless of how the voice command was recognized.
- **No seeing/typing/reading required**: neither day-to-day use nor the
  on-site initial setup may assume anything that requires seeing, typing,
  or reading.
- **Simple across generations**: no command words to memorize, patient
  and clarifying rather than aborting voice dialogs, no jargon.
