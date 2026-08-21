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
