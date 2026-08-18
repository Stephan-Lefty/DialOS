[Deutsch](sprachbefehle.md) | [English](sprachbefehle.en.md)

# Voice commands

The list of all DialOS voice commands. It grows with every new command
and is the place to look up what the system understands.

Commands are spoken in German — they are listed here verbatim, with the
translation in brackets.

**Two separate tables, deliberately:** what is built, and what is
planned. Mixed together, the planned would look like the existing —
exactly the mistake this project already had to clean up once.

Which program is used for which purpose is in
[anwendungen.en.md](anwendungen.en.md) - this file answers "which
sentence", that one "which program".

**What that sounds like** is in [sprachbeispiele/](sprachbeispiele/README.en.md)
- the replies to the commands in this table are there as audio files.

Technical background on recognition is in
[sprachsteuerung.en.md](sprachsteuerung.en.md), the installation in
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md) (step 11c).

## Implemented

Recognition is **off** after login. Until "Sprachsteuerung starten",
DialOS listens for nothing else - that is the actual protection against a
conversation or the radio triggering something. The model behind it is in
[sprachsteuerung.en.md](sprachsteuerung.en.md), section "When does DialOS
listen?".

| Voice command | Action |
|---|---|
| **"Sprachsteuerung starten"** (start voice control) | Switches command recognition on, reply: "Ich höre." If already running: "Ich höre schon." |
| **"Sprachsteuerung stoppen"** (stop voice control) | Switches it off again, reply: "Ich höre nicht mehr." After two minutes without a command this happens by itself, with an announcement. |
| "auf Windows umschalten" (switch to Windows) | Switches the desktop to the Windows 11 look (taskbar at the bottom, start menu on the left, window buttons on the right). Reply: "Windows Desktop." If it is already there: "Steht schon auf Windows Desktop." |
| "auf Linux umschalten" (switch to Linux) | Switches back to the GNOME standard. Reply: "Linux Desktop." or "Steht schon auf Linux Desktop." |
| "auf Gnome umschalten" (switch to Gnome) | Equivalent to "auf Linux umschalten". |
| **"Diktat starten"** (start dictation) | Starts the dictation; everything spoken becomes text and lands in `~/Notizen/notizen.txt`. It says "Einen Moment, ich hole Zettel und Stift." (the big model needs about 9 s), then "Ich schreibe mit." |
| **"Notiz aufnehmen"** (record a note) | Equivalent to "Diktat starten". |
| **"Einkaufszettel aufnehmen"** (record a shopping list) | As above, but writes to `~/Notizen/einkaufszettel.txt` - a shopping list mixed in with appointments and thoughts would be useless. |
| **"Diktat beenden"** (end dictation) | Ends a running dictation, writes the note and reads it out. Recognized by a **second** recognizer with its own grammar - in the dictation's free recognition the sentence became "diktat wird erhöht" (2026-08-18). Must be the **whole** utterance so it can be mentioned inside a letter. |
| **"Einkaufszettel vorlesen"** (read the shopping list) | Says the number of entries and reads them out, with pauses in between. |
| **"Notizen vorlesen"** (read the notes) | The same for the collective note. |
| **"Einkauf erledigt"** (shopping done) | Empties the shopping list - **with a confirmation**: "Der Einkaufszettel hat vier Einträge. Soll ich ihn löschen?" Answer "ja" or "nein". The old content moves to `einkaufszettel-verworfen.txt` so a sighted helper can retrieve it if needed. |
| **"Einkaufszettel wegwerfen"** (throw the shopping list away) | Equivalent to "Einkauf erledigt". Two phrasings for the same thing so the user need not memorise one - as with "auf Linux" and "auf Gnome". |
| "100" / "75" / "50" / "25" / "aus" (off) | Answer to the volume question in the login announcement. Remembered **once**; "aus" deliberately applies to the current session only. |

## Planned, not built yet

| Voice command | Action |
|---|---|
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
- **And it says it differently when nothing changed.** "Auf Linux
  umschalten" while the desktop is already on Linux gave the same
  announcement as a real switch - indistinguishable for Stephan
  (reported 2026-08-17). Since then: "Steht schon auf Linux Desktop."
- **Keep announcements short, but keep them sentences.** While the system
  speaks it deliberately does not listen - every second of announcement
  is a second the user has to wait. Eight seconds of explanation were too
  much, a bare "Windows." too little: a keyword that is not recognizably
  the answer to the command.
- **During a dictation NO command applies.** The dictation creates a
  marker and the command service keeps out while it exists. Without that a
  dictated sentence would also be evaluated as a command - dictating "auf
  Windows umschalten" into a letter would leave a different desktop behind.
  Evidenced on 2026-08-18 with timestamps in both logs. The only sentence
  that ends a dictation runs through a recognizer of its own.
- **Check new words against the model first - in TWO ways.** Not every
  word is in the vocabulary: freely recognized, "gnome" reliably became
  **"genug"** ("enough").
  - **Is the word in the vocabulary at all?** Vosk reports it itself when
    building the grammar: `Ignoring word missing in vocabulary`. That is
    instant, needs no speaking, and is the faster of the two routes. Found
    on 2026-08-18, because **"löschen" (delete) is not in the
    vocabulary** - Vosk would have dropped it from the grammar silently,
    the command would never have fired, and the log would have shown only
    "einkaufszettel". Also absent: "zurücksetzen", "aufräumen".
  - **Is the whole sentence recognized correctly?** Piper says it, Vosk
    listens - and with the **complete** command grammar, not just the new
    sentence on its own. Only then does it show whether it gets confused
    with an existing one. Examples in `docs/sprachsteuerung.en.md`.
- **Restart the recording afterwards.** When the system speaks, its own
  voice ends up in the recording queue. On 2026-08-17 that made the
  service switch itself back.
