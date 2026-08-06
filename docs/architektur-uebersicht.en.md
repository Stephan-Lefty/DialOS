[Deutsch](architektur-uebersicht.md) | [English](architektur-uebersicht.en.md)

# Architecture overview

## Goal

Stephan-OS is a live ISO based on Debian 13 (Trixie) + GNOME for people
who can only use a computer to a limited extent — in particular blind and
motor-impaired individuals. The system must be fully voice-controllable,
including system maintenance, and work equally well for an 18-year-old as
for an 80-year-old.

## Target audience

Blind and motor-impaired users equally, with no priority given to either
group. The system therefore needs to both read content aloud excellently
(screen contents, notifications, confirmation prompts) and be fully
operable without keyboard or mouse.

## Core features

- Listening to radio and music
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

## Software stack (discussion status, not yet implemented)

| Area | Choice | Rationale |
|---|---|---|
| Distribution | Debian 13 + GNOME, live-build | Best Orca/AT-SPI integration, mature ISO tooling, hardware support |
| Speech recognition (STT) | Vosk (German model), offline | Privacy for a vulnerable target group, works on the go without internet |
| Speech output (TTS) | Piper or RHVoice | More natural than espeak-ng, usable as an Orca backend |
| Intent recognition | flexible/LLM-based matching instead of rigid grammar | Must understand different phrasings of the same intent (18 to 80 year olds) |
| Low-level desktop control | Numen (Wayland-native, Vosk-based) | Mouse/window control for motor-impaired users |
| Screen reader | Orca | Standard GNOME screen reader, paired with Piper/RHVoice |
| Mail/calendar/contacts | Thunderbird | One app for all three functions, good Orca support |
| Radio | Shortwave | GNOME internet radio app |
| Music | Rhythmbox/GNOME Music | — |
| Word processing | LibreOffice Writer | — |
| Browser | Firefox ESR | For search queries and ARD/ZDF Mediatheken (no native Linux client) |
| Remote support | RustDesk | Open source, self-hostable, see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md) |
| Video calls | Jitsi Meet (browser) | No account needed, WebRTC |

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
