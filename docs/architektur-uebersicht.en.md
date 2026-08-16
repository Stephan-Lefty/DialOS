[Deutsch](architektur-uebersicht.md) | [English](architektur-uebersicht.en.md)

# Architecture overview

## Goal

DialOS is a system based on Debian 13 (Trixie) + GNOME 48 for people
who can only use a computer to a limited extent — in particular blind and
motor-impaired individuals. It is not distributed as a live ISO but built
in the office on each device from a regular Debian installation (see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md)); an ISO now exists only
as a backup image. The system must be fully voice-controllable,
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

## Software stack (as of 2026-08-16)

The "state" column separates what is decided from what is actually
built in: **installed** means the package comes from the DialOS package
list; **in use** means DialOS actively drives it; **planned** means
decided, but nothing of it is in the system yet.

| Area | Choice | Rationale | State |
|---|---|---|---|
| Distribution | Debian 13 + GNOME 48 | Best Orca/AT-SPI integration, hardware support | in use |
| Speech recognition (STT) | Vosk 0.3.45 (German models, large + small), offline | Privacy for a vulnerable target group, works on the go without internet | installed, first productive use: the volume prompt in the login announcement |
| Speech output (TTS) | Piper (RHVoice dropped) | More natural than espeak-ng, usable as an Orca backend | in use, via a speech-dispatcher generic module |
| Intent recognition | [hassil](https://github.com/OHF-Voice/hassil) (decided 2026-08-13, instead of Rhasspy) | Must understand different phrasings of the same intent (18 to 80 year olds) | installed, but no command grammar defined yet |
| Low-level desktop control | Numen (Wayland-native, Vosk-based) | Mouse/window control for motor-impaired users | planned, not installed |
| Screen reader | Orca | Standard GNOME screen reader | installed, pairing with Piper still open |
| Mail/calendar/contacts | Thunderbird | One app for all three functions, good Orca support | installed, set as the default for `mailto:`/`text/calendar` |
| Radio | Shortwave | GNOME internet radio app | installed |
| Music | Rhythmbox/GNOME Music | — | installed |
| Podcasts | GNOME Podcasts | — | installed |
| Word processing | LibreOffice Writer | — | installed |
| Browser | Firefox ESR | For search queries and ARD/ZDF Mediatheken (no native Linux client) | installed, home page set via enterprise policy |
| Remote support | RustDesk | Open source, self-hostable, see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md) | installed, autostart deliberately disabled |
| Video calls | Jitsi Meet (browser) | No account needed, WebRTC | planned |
| Telephony | ModemManager + GNOME Calls | see [telefonie.en.md](telefonie.en.md) | planned, not installed (no WWAN module in the test device) |

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
