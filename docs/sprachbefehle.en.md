[Deutsch](sprachbefehle.md) | [English](sprachbefehle.en.md)

# Voice commands

The list of all DialOS voice commands. It grows with every new command
and is the place to look up what the system understands.

Commands are spoken in German — they are listed here verbatim, with the
translation in brackets.

**Two separate tables, deliberately:** what is built, and what is
planned. Mixed together, the planned would look like the existing —
exactly the mistake this project already had to clean up once.

Technical background on recognition is in
[sprachsteuerung.en.md](sprachsteuerung.en.md), the installation in
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md) (step 11c).

## Implemented

| Voice command | Action |
|---|---|
| "auf Windows umschalten" (switch to Windows) | Switches the desktop to the Windows 11 look (taskbar at the bottom, start menu on the left, window buttons on the right). |
| "auf Linux umschalten" (switch to Linux) | Switches back to the GNOME standard. |
| "auf Gnome umschalten" (switch to Gnome) | Equivalent to "auf Linux umschalten". |
| "100" / "75" / "50" / "25" / "aus" (off) | Answer to the volume question in the login announcement. Remembered **once**; "aus" deliberately applies to the current session only. |

## Planned, not built yet

| Voice command | Action |
|---|---|
| "Hallo Michael" (or the chosen assistant name) | Wake word — only afterwards are further commands accepted. Needs a dedicated model, see [sprachsteuerung.en.md](sprachsteuerung.en.md). |
| "Hilfe rufen" (call for help) | Starts RustDesk for remote support. Deliberately only on explicit request, see [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md). |
| "System aktualisieren" (update the system) | System maintenance with a yes/no confirmation before execution. |
| "Radio hören" / "Musik hören" (listen to radio/music) | Starts Shortwave or Rhythmbox. |
| "Ruf {person} an" (call {person}) | Telephony via SIM or paired phone, see [telefonie.en.md](telefonie.en.md). |

## Rules that apply to every new command

They are not theoretical — each comes from a fault that has already
occurred:

- **A command is a whole sentence, not a single word.** A casual
  "Windows" in conversation must not switch the desktop. In the test on
  2026-08-16, "ich habe früher windows benutzt" ("I used to use Windows")
  was recognized as `auf auf windows` — with the target word but without
  "umschalten", and therefore had no effect. Every command needs a
  **trigger word** in addition to the target.
- **Safety-critical commands get a yes/no confirmation** (system
  maintenance, enabling remote support) — regardless of how confident the
  recognition was.
- **Every command announces what it did.** The user cannot see the
  screen; without an announcement they do not know whether anything
  happened.
- **Check new words against the model first.** Not every word is in the
  vocabulary: freely recognized, "gnome" reliably became **"genug"**
  ("enough"). Test method without speaking: Piper says the sentence, Vosk
  listens (examples in `docs/sprachsteuerung.en.md`).
- **Restart the recording afterwards.** When the system speaks, its own
  voice ends up in the recording queue. On 2026-08-17 that made the
  service switch itself back.
