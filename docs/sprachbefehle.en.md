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
| **"Sprachsteuerung starten"** (start voice control) | Switches command recognition on, reply: "Ich höre Dir zu." If already running: "Ich höre Dir schon zu." Also opens the [transcript window](Debian-zu-DialOS.en.md) for sighted onlookers - once, not on every command. |
| **"Sprachsteuerung stoppen"** (stop voice control) | Switches it off again, reply: "Ich höre Dir nicht mehr zu." After two minutes without a command this happens by itself, with an announcement. The transcript window closes with it in both cases. |
| "auf Windows umschalten" (switch to Windows) | Switches the desktop to the Windows 11 look (taskbar at the bottom, start menu on the left, window buttons on the right). Reply: "Windows Desktop." If it is already there: "Der Schreibtisch steht schon auf Windows Desktop." |
| "auf Linux umschalten" (switch to Linux) | Switches back to the GNOME standard. Reply: "Linux Desktop." or "Der Schreibtisch steht schon auf Linux Desktop." |
| "auf Gnome umschalten" (switch to Gnome) | Equivalent to "auf Linux umschalten". |
| **"Diktat starten"** (start dictation) | Starts the dictation; everything spoken becomes text and lands in `~/Notizen/notizen.txt`. It says "Einen Moment, ich hole Zettel und Stift." (the big model needs about 9 s), then "Ich schreibe mit." |
| **"Notiz aufnehmen"** (record a note) | Equivalent to "Diktat starten". |
| **"Einkaufszettel aufnehmen"** (record a shopping list) | As above, but says "Sage jede Ware einzeln, mit einer kleinen Pause dazwischen." and writes to `~/Notizen/einkaufszettel.txt` - a shopping list mixed in with appointments and thoughts would be useless. |
| **"Diktat beenden"** (end dictation) | Ends a running dictation, writes the note and announces how many entries it became - **without reading them out** (Stephan, 2026-08-19): "Diktat beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel vorgelesen haben, dann sage: Einkaufszettel vorlesen." Recognized by a **second** recognizer with its own grammar - in the dictation's free recognition the sentence became "diktat wird erhöht" (2026-08-18). Must be the **whole** utterance so it can be mentioned inside a letter. |
| **"Wie viel Uhr ist es?"** (what time is it) | "Es ist acht Uhr siebenundvierzig." On the full hour without the minutes. |
| **"Wie ist die Uhrzeit?"** (what is the time) | Equivalent. |
| **"Welchen Tag haben wir?"** (what day is it) | "Heute ist Mittwoch, der neunzehnte August." The same wording as the login announcement, built from the same functions. |
| **"Welches Datum haben wir?"** (what is the date) | Equivalent. |
| **"Einkaufszettel vorlesen"** (read the shopping list) | Says the number of entries and reads them out, with pauses in between. |
| **"Notizen vorlesen"** (read the notes) | The same for the collective note. |
| **"Einkauf erledigt"** (shopping done) | Empties the shopping list - **with a confirmation**: "Der Einkaufszettel hat vier Einträge. Soll ich ihn löschen? Sage ja oder nein." If no usable answer arrives, DialOS asks **a second time** ("Das habe ich nicht verstanden. Sage ja oder nein."); only then does the list stay. The old content moves to `einkaufszettel-verworfen.txt` so a sighted helper can retrieve it if needed. |
| **"Einkaufszettel wegwerfen"** (throw the shopping list away) | Equivalent to "Einkauf erledigt". Two phrasings for the same thing so the user need not memorise one - as with "auf Linux" and "auf Gnome". |
| **"ja" / "nein"** (yes/no) | Answer to a confirmation - so far only before emptying a note. Valid **only during the confirmation**: a recognizer of its own runs for it, with a grammar of exactly these two words, while the command service keeps out. If nothing usable arrives, DialOS asks once more; after that the list stays. |
| **"Hilfe rufen"** (call for help) | Starts remote support - **with a confirmation** that explains what happens: "Dein Betreuer kann dann sehen, was auf dem Bildschirm steht, und das Gerät bedienen. Soll ich sie starten? Sage ja oder nein." The RustDesk number is then read out **digit by digit and twice**. During a running session the same sentence **extends** it by an hour. |
| **"Fernwartung beenden"** (end remote support) | Ends it. "Niemand kann mehr zusehen." Also happens by itself after an hour, with a warning three minutes before. The core word is **"fernwartung"**, not "beenden": the user knows the latter as the dictation's closing word, and a word in two roles is ambiguous when spoken even when the grammar is not. |
| "100" / "75" / "50" / "25" / "aus" (off) | Answer to the volume question in the login announcement. Remembered **once**; "aus" deliberately applies to the current session only. |

## Planned, not built yet

| Voice command | Action |
|---|---|
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
- **A sentence counts even when the recognizer swallows a word - as long as
  no `[unk]` is present.** On 2026-08-19 Stephan said "Sprachsteuerung
  starten", the recognizer delivered `'starten'`, and the condition on the
  full sentence rejected it. Voice control could not be switched on, and
  everything beyond it was unreachable. Since then the **core word**
  suffices, provided nothing but words of the phrase appears and no `[unk]`
  is present - the same as a day earlier for the dictation's stop phrase.
  - **The core word must be unambiguous.** "stoppen" appears in exactly one
    sentence of the grammar, so it always suffices. "starten" appears in two
    ("Sprachsteuerung starten" and "Diktat starten") - on its own it
    therefore suffices only in the **off** state, where the grammar knows
    just one sentence. Anyone adding a new command with an already-used verb
    must check this.
- **An operating rule the user cannot see has to be spoken.** A shopping list
  only becomes a list if there is a small pause between items - that was how it
  was built from the start, but it was never announced. On 2026-08-19 Stephan
  dictated "Milch sechs Eier Butter" in one breath and got a single entry. A
  sighted user would have noticed after the first item; a blind user finds out at
  the read-back, a minute later.
- **A command does not take a decision away from the user that they can make
  themselves.** Until 2026-08-19 "Diktat beenden" read the whole list back.
  That made "Einkaufszettel vorlesen" redundant - and anyone who had noted
  three items had to hear them a second time. Since then DialOS announces the
  count and **how** to get it read out. A confirmation prompt would have been
  the wrong route: it demands an answer, a hint does not.
  - **A hint may only name sentences that exist.** The hint comes from a table
    holding exactly those targets for which a read-out command is listed in
    this file. An unknown target gets the confirmation only - naming a sentence
    the grammar does not know would be worse for a blind user than no hint.
- **Safety-critical commands get a yes/no confirmation** (system
  maintenance, enabling remote support) — regardless of how confident the
  recognition was.
  - **The expected words belong in the question.** "Soll ich ihn löschen?" on
    its own does not tell a blind user what to answer - there are no buttons to
    see. Since 2026-08-19: "Soll ich ihn löschen? Sage ja oder nein."
  - **Whoever asks the question must also do the listening.** Until 2026-08-19
    the caller spoke the question and then called the answer function - which
    only then loaded the speech model and afterwards started recording.
    Stephan's "ja" fell into exactly that gap; not a single "Antwort gehoert"
    line was in the log. Since then the answer function asks the question
    **itself**, and everything slow happens before that. The same class of fault
    occurred on 2026-08-15 (login announcement) and 2026-08-18 (dictation
    marker) - so the order "be ready first, then ask" is a rule, not a nicety.
  - **Nothing is recorded while the question is spoken.** The grammar knows only
    "ja", "nein" and "[unk]" - the system's own voice could land in it as "ja"
    and delete the list without anyone having said a thing. Deleting without
    consent is the worse fault.
  - **A follow-up question instead of an abort.** If no usable answer arrives,
    DialOS asks once more. Without that the user would have to speak the whole
    command again although only one word was missing.
- **It should feel like a dialogue between the user and Michael** (Stephan's
  principle, 2026-08-19). This is the rule the other wording rules follow from,
  and it has a practical reason: whoever cannot see the screen has nothing but
  this voice. A status message leaves them alone; a sentence does not.
  - **Michael addresses the user** ("Ich höre **Dir** zu.", "Möchtest **Du**
    Deinen Einkaufszettel vorgelesen haben", "Sage ja oder nein.") and **speaks
    of himself** ("**Ich** schreibe mit.", "**Ich** habe nichts verstanden.").
  - **And the word in between can decide whether the sentence is true.** "Du
    hast eine Weile nichts gesagt." was false when someone had been talking in
    the room - the counter runs from the last **command**, not the last
    utterance. Stephan's "Du hast **mir** eine Weile nichts gesagt." is true,
    because the "mir" narrows the sentence to what was said to Michael. One word
    of politeness became a truth condition.
  - **The exceptions are the short acknowledgements of a switch** ("Windows
    Desktop.", "Ton über Lautsprecher."). They are deliberately that short
    because the user wants to carry on there - see the rule on length below.
- **Every command announces what it did.** The user cannot see the
  screen; without an announcement they do not know whether anything
  happened.
- **And it says it differently when nothing changed.** "Auf Linux
  umschalten" while the desktop is already on Linux gave the same
  announcement as a real switch - indistinguishable for Stephan
  (reported 2026-08-17). Since then: "Steht schon auf Linux Desktop."
- **Keep announcements short, but keep them sentences.** While the system
  speaks it deliberately does not listen - every second of announcement
  is a second the user has to wait.
  - **What matters is whether the user is waiting.** This rule comes from the
    desktop switch, where they want to carry on. After a **finished** dictation
    nothing is waiting - so the hint there may run 8 s, and Stephan decided so
    on 2026-08-19 after comparing four measured variants. Seconds are not the
    yardstick; the yardstick is what stands in the user's way. Measurements in
    [sprachbeispiele/README.en.md](sprachbeispiele/README.en.md). Eight seconds of explanation were too
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
    "einkaufszettel". Also absent: "zurücksetzen", "aufräumen" - and **"spät"** (late), which is
    why "Wie spät ist es?" became the tested phrasings "Wie viel Uhr ist
    es?" and "Wie ist die Uhrzeit?" (2026-08-19).
  - **Is the whole sentence recognized correctly?** Piper says it, Vosk
    listens - and with the **complete** command grammar, not just the new
    sentence on its own. Only then does it show whether it gets confused
    with an existing one. Examples in `docs/sprachsteuerung.en.md`.
- **Restart the recording afterwards.** When the system speaks, its own
  voice ends up in the recording queue. On 2026-08-17 that made the
  service switch itself back.
