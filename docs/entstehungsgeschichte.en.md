[Deutsch](entstehungsgeschichte.md) | [English](entstehungsgeschichte.en.md)

# Thirteen Days and Counting …

*How DialOS came to exist, 6 to 21 August 2026. 261 commits. Told as what
it was.*

Everything here is on the record - in the changelog in
[../README.en.md](../README.en.md), in the log files, in the git history.
Nothing has been added. Only the form is sharpened.

---

## The antagonist

Every thriller needs one, and this one has a good one. It is not a bug. It
is a principle:

**A system that reports success while it fails.**

So far it appears seven times, in a different disguise each time, and each
time somebody believes it. Usually me.

On the last day it wears mine.

---

## Day 1: The requirement that leaves no way back

**6 August, 14:15.** First commit. Twenty more follow that day.

The task sounds harmless: an operating system for blind and
motor-impaired users, fully operable by voice. Debian, GNOME, free
software.

The sentence that governs everything afterwards is not in the
requirement. It follows from it: **the user cannot look and check.** No
glance at the screen, no window you open for a second, no error message you
read. What the system does not say does not exist for him.

That turns every silent malfunction into a catastrophe. And silent
malfunctions are the antagonist's speciality.

---

## Days 1 to 9: The wrong road, eighteen times

The plan is sensible: build a live ISO, automated, in Docker. `live-build`
in a container, reproducible, one command.

**Around eighteen build attempts.** Not one produces a finished `.iso`. Not
a single one.

Practically every failure traces back to the same cause - nested
`live-build` in Docker in a sandbox - and every one looks like a different
problem. You fix one and find the next. The pipeline reports progress. It
never arrives.

The way out is not technical but a decision: **install Debian directly on
real hardware.** A ThinkPad T490, set up by hand, documented step by step.
The `iso-build/` files remain as the recipe.

It is the first moment when someone says: we have been working in the wrong
direction. It will not be the last.

A second design falls at the same time. Encryption was meant to cover the
whole disk. On 14 August that is replaced: **only the user's data**, in a
LUKS partition of its own, and a USB stick that releases it. No stick, no
data. The rest boots normally.

And an entire installer - Calamares, branding, overlays, a cloning script -
is built and then **deleted in full**. It existed only for a road that no
longer exists.

---

## Day 8: Sixty decibels

**13 August.** A microphone comparison. The built-in one against a
Bluetooth headset. The result is unambiguous: built-in clearly worse.

The decision goes to Bluetooth. It shapes the following days - the hardware
selection, the purchasing thoughts, the entire audio concept.

**16 August.** While looking for something else, a number stands out. On the
T490's built-in microphone two gain stages are at maximum. `Capture` at
+30 dB. **And on top of that** `Internal Mic Boost` at +30 dB.

Sixty decibels. From the factory.

What that means is worse than poor quality. Vosk recognizes speech by the
**pauses between words**. In permanent full-scale clipping there are no
pauses. So a result never came.

With no error message. The microphone was there. It delivered data. The
recognizer ran. Everything reported success, and nothing ever arrived.

And the decision of 13 August? **It may never have measured the microphone
at all, only the clipping.** Three days of hardware reasoning rest on a
comparison that no longer holds. The item is still in
[../TODO.en.md](../TODO.en.md): repeat it.

**16 August, 58 commits.** The densest day. Everything is built, checked and
documented on real hardware. By evening DialOS has its first real voice
command: the desktop switches between GNOME and a Windows 11 lookalike on
request.

It works. Live, in Stephan's voice.

---

## Day 12: The machine switches itself back

**17 August.** The voice command runs. Stephan says "auf Windows
umschalten". The desktop changes.

Fifteen seconds later it changes back. By itself.

Nobody said anything.

The explanation is not logic but arithmetic. At 16 kHz mono 16 bit `parec`
delivers about **32,000 bytes per second**. While the system spoke, the
service discarded 4,000 bytes and then slept 0.3 seconds - so **13,000 per
second**.

It emptied the queue more slowly than it filled up.

After an eight-second announcement, five seconds of **its own voice** stood
in the pipe. It then evaluated that perfectly normally. And because the
grammar is restricted to three sentences, it pressed the fragment into a
command.

The system listened to itself and obeyed itself. The guard marker "I am
speaking" was in place and did work - it prevented **listening**, not
**recording**.

Fixed by discarding the recording after every utterance and starting a new
one. A fresh process has no backlog.

---

## Day 12, later: Four indicators lie at once

**17 August, afternoon.** A reboot. Afterwards no announcement in **either**
account. No sound. Not over Bluetooth, not through the built-in speakers.
Nothing.

The speech icon appears in the panel. Nothing comes out.

What the indicators say:

- BlueZ: `Connected: yes`, battery 100 %.
- `pactl`: the sink is there, state `RUNNING`.
- ALSA for the capture device: `state: RUNNING`.
- The headset itself, when asked: connected.

What actually arrives: **0 bytes in 3 seconds.**

The cause is a test configuration of mine that survived a reboot. Echo
cancellation was hanging on Stephan's USB headset. The headset was switched
off. The dongle presents a sound card regardless.

And because the module needs that capture as its **clock**, PipeWire never
started the graph. The sound card stayed at `state: PREPARED`,
`trigger_time: 0.000000000`, `hw_ptr: 0`. Every playback hung forever.

While searching I first reported "PipeWire is healthy", because the module
was loaded and the sink showed `RUNNING`. Then I suspected
`webrtc.gain_control`, which had been changed the same day. Both wrong. Only
a series test across the capture targets showed it.

What a blind user would have experienced: no sound, no error, only
announcements piling up - three speech outputs and four GNOME sounds in the
queue at the time of the incident. To him that is not "the sound is gone".
To him the device is broken.

The rule that came out of it has been in [../CLAUDE.md](../CLAUDE.md) ever
since: **believe no status report when the result can be measured.** DialOS
now tests output devices by sending 150 milliseconds of silence and watching
whether the call completes.

---

## Day 12, evening: "I have to speak louder"

Twice that day Stephan reports having to speak very loudly. Twice I look at
the gain.

Both times it is a window in which the system is not listening.

The first time: after the announcement "Ich höre." the service set a lockout
of five seconds - the same one that makes sense after a real switch. So it
was **deaf for exactly the five seconds in which the user speaks his
command.** Stephan spoke, nothing happened, he repeated it louder, and by
then the lockout had expired and it worked.

What solved it was not my search but his clarification: *"I had to shout
the **second** command into the mic much louder."* The first was fine. That
made clear it was not a question of volume but of sequence.

The second time, days later, the same cause elsewhere: after a switch the
service was deaf for **5.1 seconds** while the announcement had already
ended after 1.5. The user hears the answer and talks into a deaf system for
3.6 seconds.

That morning I had written the reasoning for it down myself - and then fixed
only half the place.

Since then [sprachsteuerung.en.md](sprachsteuerung.en.md) says: **"I have to
speak louder" is almost always a misleading fault description.** The
question that solves it is not *how loud* but **which** command in the
sequence failed to arrive.

---

## Day 13: The unreliable narrator

**18 August.** Dictation works. Free recognition, big model, casing
correction. Stephan dictates a shopping list, the system reads it back.

He says: *"When it repeats what it noted, the speed doesn't match the other
announcements."*

I suspect differing processing chains and measure: 2.918 seconds against
2.575. Looks convincing. **It is an artefact of my own measurement.** Send
*one* speech output through both chains and both come out at 2.549.

The difference came from my having invoked the speech program twice.

So, five times the same sentence:

```
2.575 s   2.562 s   2.865 s   2.456 s   2.628 s
```

**Seventeen per cent spread.** With nothing having changed.

Piper uses a VITS model with a random component in phoneme duration. Every
sentence comes out a different length every time.

The reach of this is larger than its occasion. **Every speech-duration
measurement in this project was a sample, not a number.** "1.13 seconds for
'Ich höre.'" - a figure decisions were built on - carried an unknown spread
of up to seventeen per cent.

One switch fixes it: `--noise_w 0`. After that the output is reproducible to
the millisecond. Cached announcement 0.939 s, freshly generated 0.939 s.

It was found by no test, no measurement and no tool. It was found by a human
being who listened.

---

## Day 13, afternoon: Seven minutes

The dictation needs a stop phrase. "Diktat beenden". In free recognition it
becomes `'diktat wird erhöht'` - a *specific* sentence cannot be hit
reliably among tens of thousands of possibilities. The **third** time for
the same effect: "gnome" became "genug" (enough), "windows" became
"sinnlose" (pointless), "beenden" became "wird erhöht" (is being raised).

The answer: a second recognizer that knows **only that one sentence**. It
hits it verbatim.

But I require an exact match. And that same morning I note in the
documentation:

> *"It did not stop, because an exact match is required - but that condition
> is the only thing standing in between."*

In the afternoon Stephan says "diktat beenden". The recognizer delivers
`'beenden'`.

The condition rejects it.

For **seven minutes** the dictation keeps running. It writes down everything
spoken in the room - 42 entries, among them "Ja Silvia erwerben" and "Also
brieselang", both nonsense. It could only be stopped by hand.

The lesson has been a sentence in the changelog ever since: **a recorded
risk is not a handled risk.**

---

## Day 14: For two days something else was running than the repo said

**19 August.** 26 commits. The day starts with a wish from Stephan that sounds
like a detail: it should feel like a **dialogue**, not like a machine
reporting states. That becomes a rule, and every single announcement is
checked against it. "Ich höre Dir zu" instead of "speech recognition active".

Then comes the yes/no question before emptying the shopping list. It does not
work. Stephan says "ja", nothing happens.

The reason is an ordering: the caller spoke the question - and **then** the
function loaded its speech model, for eleven seconds. The answer fell into
exactly that hole. The question had been asked, but nobody was listening.
Since then the function asks the question itself, once it is ready.

### The check script's blind spot

The same day it turns out that **two scripts had been running for two days in
an older version than the repo held**. Everything was committed, everything
looked right, and the device was executing something else.

The answer to that is a check script: it compares what is in the repo with
what is installed. Exactly the kind of tool this project needs.

The check script has a blind spot. It looks at **one directory**. Files beside
it do not exist for it - and "does not exist" it reports as fine.

That is the same antagonist as on day 8 and day 12, one level up: this time it
is not the system reporting success but **the tool meant to verify the
success**. It is improved twice - first a hand-maintained list (out of date
with the next new script), then the whole tree. And since then it explicitly
reports what it is **not allowed** to read, instead of staying silent.

### A coin toss with 0.8 seconds of margin

The writing aid needs **9.2 seconds** for the first sentence of a session -
the German rules do not load when the server starts but on the first check
request. The timeout in the dictation is 10.0 seconds.

Eight tenths of a second of headroom. The first correction of every session
was a coin toss, and at 10:03:03 it lost.

The fix is a warm-up at login: the nine seconds happen once, where nobody is
waiting for them. After that the check answers in 1.0 seconds.

By evening "Hilfe rufen" exists: DialOS reads an ID and a one-time password to
the user, slowly, with a pause between them, and asks afterwards whether both
arrived. The privileged part is built, checked - and **deliberately not
installed**, because the service behind it is not ready.

---

## Day 15: The same data through both rules

**20 August.** 19 commits. Stephan has let DialOS run for a day and reports
something unsettling: "every now and then Michael spoke up." The voice control
switches itself **on**. Once it even asks whether it should start remote
support.

Switching on listened for a core word, and the core word was "starten". The
log records how often that word arose from pure ambient noise: **27 times in
two hours.**

### The best measurement of the project

The change itself is quick - the core word becomes "sprachsteuerung", long and
distinctive. What is interesting is how it is proven: **the same two hours of
log are run through both rules.** Not two periods compared, where somebody
else was in the room or the radio was on - one body of data, two rules.

Result: the old rule would have switched on **30 times**, the new one **7**.
Saving: 46 minutes of open microphone in a good two hours.

And the same measurement shows the limit: **not one** of the seven was
followed by a command. Those seven were largely noise too. The change pushes
the problem down by three quarters; it does not solve it.

From that come two small changes instead of the big wake word, whose
ready-made models carry a non-commercial licence: switching on requires
**both** words, and without a command it ends after 30 seconds instead of two
minutes.

The second change does not take effect at first. The reason is one line in the
wrong order: the timestamp was set **before** the announcement, and the
announcement takes a good second - after which it looked as though a command
had already come. Stephan's test found it, not mine: mine had checked the
decision function, not the ordering.

### Anna

Stephan decides: a friendly female voice. The listening comparison produces
`de_DE-kerstin-low`, tempo 1.00, name **Anna** - and she becomes the delivery
voice, not just a test setting.

Tempo differs per voice, measurably so: the same sentence takes Thorsten 7.75
**These figures were wrong** (corrected 2026-08-22): they came from a
generator that declared Kerstin's 16 kHz raw data as 22050 Hz - every Kerstin
sample ran 38 % too fast. Measured correctly, the same sentence takes about
6.15 s for Michael at 0.88 and about 7.04 s for Anna at 1.00; Anna is
therefore **14 % slower**, not on a par. Since 2026-08-22 Anna is set to
**0.95**, chosen by Stephan from correctly generated samples.

At Stephan's suggestion DialOS now addresses the user by name - in the
greeting, at decisions, at errors. **Not** at confirmations and not at the
timeout. The reason weighs more than politeness: with the radio on or a
visitor in the room, "Stephan, …" says unmistakably that this concerns him.
Someone who hears the name constantly stops hearing it.

Then Stephan listens more closely: "Michael says Stefffan."

The name is spoken in every greeting, every question, every error.
Mispronounced it grates more than any other word. The name file gets a second
field: `Stephan | Stefan`. The written form stays "Stephan" - for letters,
where "Stefan" would simply be wrong. The second field is what gets spoken.

**I would never have found this alone.** I had checked the name form of
address against three announcements and declared it done. That the name itself
sounds wrong is only audible to someone who knows it.

### "Security updates only", before I had checked

`unattended-upgrades` is set up. I tell Stephan it is security updates only.

Then I look. An `Origins-Pattern` line **appends**, it does not replace. After
the first attempt five patterns were in the list: my two **and** Debian's
three, including ordinary stable without `-Security`. The device would have
updated everything overnight.

Fixed with `#clear`, proven with a dry run in which everything except
`Debian-Security` sits at pin `-32768`, "under no circumstances". But the claim
had gone out before the check. Stephan's reply is the sentence that sums up the
day: **"Mistakes are human."**

The same day I lose data: my restart helper always set the log aside under the
same name and overwrote the first backup on the second run. The raw data of the
157 utterances is gone; the result is in the commits, the data is not. The
helper sets nothing aside at all any more - since that same day logrotate
cleans up the logs after seven days, and a second mechanism beside it only
creates name collisions.

---

## Day 16: The repair from day 13 turns on us

**21 August.** Stephan wants the letter. Everything for it exists: dictation,
writing aid, footer. What is missing is punctuation, a place to put it and a
letterhead. A day's work, one would think.

The morning goes well. Spoken punctuation, measured rather than guessed: the
bare words score **three out of six** with Stephan's voice - "Komma" becomes
"komme", "Punkt" becomes "kommt", "Doppelpunkt" becomes "dörte depots". The
two-word forms score **three out of three**. So "Komma setzen". In passing
that removes a price Stephan had accepted beforehand: "in diesem Punkt" now
stays intact.

Then he dictates the first letter. The dictation ends after six seconds. By
itself.

### This time the unreliable narrator is me

I have an explanation: ambient noise. The stop recogniser knows only "diktat
beenden" and `[unk]`; it has to map every sound onto one of the two. Sounds
plausible.

I measure it: 180 seconds of silence in the same room, same grammar. **Zero
results.** The explanation is wrong.

I have a second one: Anna hears herself. The ready announcement plays, the
recording starts, echo cancellation needs a moment. Also plausible.

I measure it: three times announcement, three times listening immediately.
**Nothing.** Also wrong.

Two diagnoses, both internally consistent, both refuted. Until now the
antagonist has used systems that report success. On this day he uses me.

### Four repairs in one afternoon

I build a guard period: no stop in the first three seconds. The next test
breaks off after 4.2.

I build a level gate: too quiet is no stop. The noise is loud enough.

I count them - all stop events of the day: **six false triggers, every single
one a bare "beenden"**, none from "diktat beenden". So the stop requires both
words. That overturns the rule from **day 13**, which had been created the
other way round: back then exact matching had let a dictation run for seven
minutes, and the lesson was that the word alone suffices. It came from seven
minutes of continuous talking - and had never checked what happens while
*dictating*.

I build an announcement: if only "beenden" arrives, DialOS should say so, so
nobody speaks into the void. It interrupts Stephan after four seconds in the
middle of his letter. His verdict is the sentence of the day:

> **"I can never get to the end of this text."**

The announcement is removed the same day. A help that disturbs more often than
it helps is not one.

### Two faults that had been sitting there for weeks

Between the repairs two things come to light that have nothing to do with the
stop phrase and are older than it.

**Vosk only delivers at a speech pause.** Anyone who speaks the letter in one
go and then says "Diktat beenden" has both in *the same* pause: the stop
breaks the loop before the recognition could deliver its buffered text.
`FinalResult()` was never called. The log says "0 utterances" while a whole
letter was spoken.

**And the emergency exit was broken itself.** Two minutes of silence were
meant to end any dictation. They could never take effect: every `[unk]` from
room noise reset the clock. One dictation runs on for nine minutes, holds the
"another service is listening" marker - and Stephan can no longer start the
voice control. The very phantom words the new level gate discards when writing
are what keep it alive.

Both faults are as old as the dictation. Both only show up when somebody
dictates a *letter* instead of a shopping list.

### The best question of the day

In the evening Stephan asks: then why does the shopping list work cleanly?

The answer is in a measurement that was already there. Thirty seconds of
continuous letter text through the stop recogniser:

```
at  4.8 s  'diktat'
at  8.4 s  'beenden'
at 12.2 s  'diktat [unk] beenden'
at 15.1 s  'beenden'
```

Fragments by the second - out of *continuous* speech. A shopping list sounds
different: "Milch." Pause. "Butter." Pause. And 180 seconds of silence had
produced **zero** results. The pauses between the items protect the shopping
list, without anyone having planned it that way.

That also makes clear where the lever is: a genuine "Diktat beenden" follows a
pause. Every fragment arises in the middle of the flow.

### What the day cost

Six test runs by Stephan, each containing a fault I could have found
beforehand. Four rules have sat at the top of [../CLAUDE.md](../CLAUDE.md)
since then, and the most important one is: **whatever can be checked offline
against Piper gets checked offline first.** Stephan is not the test run.

The second: **an explanation that fits all the observations is not yet a
cause.**

---

## How it ends

It does not end. On 21 August at 14:19 the 261st commit is in place.

What exists: a voice control that listens only when told to, and says so. A
dictation that writes notes, with 98.1 % correct capitalisation. A shopping
list that can be read out, added to and thrown away - with a confirmation,
because it came into being by speaking alone. An audio output that believes
no device but tries it. And documentation that carries every one of these
faults, because otherwise they get made again.

Added over the last three days: an origin line in every mail, three battery
warnings, a machine that no longer falls asleep and no longer locks its user
out - and a letter that comes into being as a letterhead, with date, footer
and the note explaining why it is not signed.

What does not exist: telephony, reading out mail, scanning post. And the
letter cannot be dictated to the end, because the stop recogniser turns
ongoing speech into "diktat beenden". That is the single point standing
between a finished path and a usable letter.

The antagonist is not defeated. He is recognized. With this antagonist that
is the whole difference: **a system that lies is harmless the moment you
stop believing it and start measuring.**

Day 16 added one sentence to that: the same goes for whoever is measuring.

---

*For the figures and the evidence: [../README.en.md](../README.en.md) has
the full changelog, [../TODO.en.md](../TODO.en.md) the open items,
[../CLAUDE.md](../CLAUDE.md) the rules that came out of these days.
What DialOS sounds like is in
[sprachbeispiele/](sprachbeispiele/README.en.md).*
