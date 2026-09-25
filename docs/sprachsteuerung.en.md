[Deutsch](sprachsteuerung.md) | [English](sprachsteuerung.en.md)

# Voice control

## Stack

- **Speech recognition (STT)**: Vosk with a German model, offline - for
  commands and the shopping list, with a restricted grammar.
- **Recognition of free text**: **Parakeet** (NVIDIA Parakeet TDT 0.6B v3
  via sherpa-onnx, offline), built in for good since 2026-09-16 - for letters,
  notes, the text of an e-mail and search terms. Chosen after the test bench of
  2026-09-15: 2.8 % word errors against 12.7 % for Vosk, and only Parakeet sets
  punctuation itself (see [pruefstand.en.md](pruefstand.en.md)). Can be
  switched off with `~/.config/dialos/parakeet-aus`.
- **Speech output (TTS)**: Piper (more natural than espeak-ng), used as
  a backend for Orca - RHVoice was considered and dropped.
- **Screen reader**: Orca (the standard GNOME screen reader).
- **Low-level desktop control** (mouse, windows): Numen – Wayland-native,
  also Vosk-based, open source.
- **Intent recognition**: [hassil](https://github.com/OHF-Voice/hassil)
  (Home Assistant Intent Language) - adaptable matching via
  example-sentence templates instead of a rigid command grammar (see
  below). **Status 2026-09-25: installed, but not wired into the code** -
  see "Implementation status".

## Implementation status (2026-09-25)

So it stays clear what is concept and what is built - the state of
2026-08-16 follows below as history.

- **Speech output: in use.** Piper via speech-dispatcher; `dialos-say.py`
  speaks every announcement; voices Michael and Anna.
- **Commands: in use, around 64 command sentences** (counted at the mandatory
  check of 2026-09-21), including the sentences from `dialos-programm.py` and
  the extensions' start sentences. Recognised by the small Vosk model with a
  restricted grammar. The full list is in
  [sprachbefehle.en.md](sprachbefehle.en.md).
- **Switching on by sentence instead of a wake word:** "Sprachsteuerung
  starten" / "Sprachsteuerung stoppen" (decided on 2026-08-17, see below).
  There is still no wake word of its own.
- **Free text: Parakeet since 2026-09-16** for letters, notes and the text of
  an e-mail; the shopping list stays with Vosk. Details in
  [diktat.en.md](diktat.en.md).
- **Intent recognition: hassil is installed but not wired into the code**
  (checked on 2026-09-25: no DialOS script imports it). The voice service maps
  what was recognised to a command itself: the Vosk grammar only admits the
  words of the command sentences, and rules of our own decide when a sentence
  counts - core word, the whole word sequence with at most two extra words, no
  `[unk]`. Why the decision of 2026-08-13 was never implemented that way: see
  the note in the section "Intent recognition" below.
- **Microphone:** the voice services pick the echo-cancelled source
  `dialos_mikrofon_ohne_echo` themselves. The system's default microphone
  deliberately stays the raw built-in one - reasoning in
  [anwendungen.en.md](anwendungen.en.md), section "Two rules".
- **Orca screen reader:** installed; whether it is paired with Piper was not
  rechecked for this status. **Numen:** not installed.

## Implementation status (2026-08-16)

> **Superseded since the evening of 2026-08-16** (first real voice command) -
> the current status is directly above. This section stays as a snapshot:
> this is how things looked before voice control was built.

So it stays clear what is concept and what is built:

- **Speech output: in use.** Piper runs via a speech-dispatcher generic
  module; `dialos-say.py` speaks every announcement with audio ducking
  and a panel indicator.
- **Speech recognition: installed and productive for the first time.**
  Vosk answers the volume question in the login announcement (tested with
  a real voice on 2026-08-15/16). Nothing beyond that is built yet.
- **Intent recognition: hassil is installed but unused** - there is not a
  single example-sentence template in the system yet.
- **Continuous listening with a wake word: does not exist.** Recognition
  only runs when a script explicitly invokes it.
- **Orca screen reader: installed, but not yet paired with Piper.**
- **Numen: not installed.**

In short: speech *output* is finished, voice *control* in the real sense
- being addressable at any time and executing commands - is still
pending. It is the next major block of work.

## Intent recognition: flexible instead of rigid

A rigid command grammar (exact phrasings as used by classic voice
assistant frameworks) fits poorly with the requirement that the system
must be just as easy for an 18-year-old as for an 80-year-old — different
generations phrase the same command differently ("call Anna" vs. "connect
me to Anna" vs. "phone Anna please").

**Decision (2026-08-13): [hassil](https://github.com/OHF-Voice/hassil)**
takes over mapping the Vosk transcription to an action. Instead of demanding
exact phrasings, several example-sentence templates with alternatives and
optional words are stored per action (e.g.
`(ruf|verbind mich mit) [bitte] {person} an`) - new phrasings can be "taught"
by adding further templates, without changing code.

Decisive criteria and alternatives examined:

- **Offline/privacy**: cloud solutions (e.g. using the already installed
  Claude Code CLI for classification) are ruled out by this - hassil runs
  entirely locally, no internet connection needed.
- **Free of charge**: open source, no running API costs.
- **Adaptable**: by adding example-sentence templates, without retraining or
  fine-tuning a model.
- Originally **Rhasspy** was considered as a starting point (it uses the same
  example-sentence approach internally). During the installation research,
  however, it turned out that Rhasspy was archived by its author in 2026
  (reason: looming burnout) and is no longer developed - unsuitable as the
  basis for a system meant to run for years. hassil is the actively
  maintained successor component (part of the Open Home Foundation/Home
  Assistant, as of 2026: over 600 commits), offering the same
  example-sentence approach but without Docker or a service of its own - just
  a lean Python library (only dependency: PyYAML) that can be embedded
  directly in our own scripts such as `dialos-vosk-test.py`/`dialos-say.py`.
- A small local language model of our own (e.g. via llama.cpp) would have
  been freer in recognising phrasings, but considerably more effort in
  selection, integration and quality assurance - for the manageable, clearly
  bounded number of actions (Wi-Fi, volume, starting programs, calling, ...)
  hassil's example-sentence approach seemed the better effort-to-benefit
  ratio.

> **Status 2026-09-25: not implemented this way.** From 2026-08-16 onwards
> what was built is a restricted Vosk grammar with a mapping of our own (see
> "Implementation status" above). `TODO.md` already gives the reason on
> 2026-08-16: hassil only pays off once there are several commands with
> variants. Several phrasings for the same command have stood as separate
> sentences in the grammar since then ("Wie viel Uhr ist es?", "Wie spät ist
> es?"). Whether hassil still finds its place with the extensions is open in
> [erweiterungen.en.md](erweiterungen.en.md).

The flexibility applies to **understanding**, not to **execution** —
security-critical actions (system maintenance, approving remote support)
always stay behind an explicit yes/no confirmation, regardless of how the
command was recognized.

## Voice-controlled system maintenance

A guided dialog with confirmation instead of direct command execution,
e.g.:

> "Computer, update the system" → "Install updates now? Yes/No"

No direct commands without confirmation — safety takes priority over
misrecognition here.

## Design principles for voice dialogs

- Patient, clarifying rather than aborting when something is unclear.
- No jargon.
- No command words that need to be memorized.
- When confirming input (e.g. capturing the name during initial setup),
  always offer a way to correct it.

## Resource consideration (battery life)

Since the device is also used on the go, constantly listening with full
STT noticeably drains the battery. Proposal: a two-stage model with a
very low-power wake-word model (e.g. openWakeWord) that permanently
listens only for a trigger word; only after that is the more
compute-intensive full speech recognition activated. Not yet finally
decided/implemented.

The concrete list of commands is in
[sprachbefehle.en.md](sprachbefehle.en.md).

## When does DialOS listen? The interaction model

**Decided on 2026-08-17 with Stephan.** There are **two different ways**
the microphone goes live - and the difference is not technical but comes
down to who started the conversation.

### 1. The system asks - it opens and closes the window itself

When DialOS wants to know something, it knows that. It opens recognition
itself, takes the answer and closes again afterwards. **The user does not
have to announce themselves** - they were just addressed.

That is exactly what the `--frage` switch in `dialos-say.py` is for (see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 11a): the
information "I want to know something now" exists in the code anyway.

**If the user does not answer**, the question is repeated **once**. If it
stays silent after that, Michael says "Schade, dass Du nicht antwortest."
(a shame you're not answering) and closes the window. Deliberately not a
silent close: the user should hear that the question is over - otherwise
they may be speaking into the void.

### 2. The user wants something - they announce themselves

Here the system cannot guess that it is being addressed. Hence:

> "Sprachsteuerung starten" → **"Ich höre Dir zu."** (I'm listening to you.)
> … commands …
> "Sprachsteuerung stoppen" → **"Ich höre Dir nicht mehr zu."** (I'm not listening to you any more.)

The confirmations are short and always identical - the user hears them
daily, so recognizability matters more than variety. They are phrased
from Michael's perspective, not as a status report ("voice control is
enabled").

**After two minutes without a command, recognition switches itself off**,
with an announcement: "Du hast eine Weile nichts gesagt. Ich höre Dir nicht mehr zu." The
reason is not power saving but safety: anyone who forgets the "stoppen"
would otherwise have a permanently open microphone - and we would be back
to the radio switching the desktop.

**At login, recognition is always off.** Predictable and safe; the user
switches it on when they need it.

### Why this solves the state question

The open question was: how does a blind user know whether recognition is
on? Answer: **they hear every change** - when switching on and off, and
when the timeout expires too. And if unsure, they simply say
"Sprachsteuerung starten": if it is already running, the system says so.

A state that can only be seen would be no state at all for this target
group.

## Wake word: measured, and the obvious route is ruled out

**Status 2026-08-17.** A wake word is still missing. The obvious
implementation - the same restricted Vosk grammar as for the desktop
voice command, just with the wake word in it - was measured and
**rejected**.

Tested with the proven method (Piper speaks, Vosk listens):

| said | recognized | |
|---|---|---|
| "Michael" | `michael` | recognized |
| "Hallo Michael" | `hallo michael` | recognized |
| "Anna" / "Computer" | `anna` / `computer` | recognized |
| **"ich rufe michael an"** | **`hallo michael`** | **false alarm** |
| **"der computer ist langsam"** | **`computer`** | **false alarm** |
| "hallo wie geht es dir" | `hallo` | quiet |

So the words themselves are all in the model's vocabulary - which was not
a given (see "gnome" → "genug" for the desktop voice command). The
problem lies elsewhere: **a restricted grammar has no choice. It forces
every utterance into the nearest phrase.** For commands that is an
advantage - you say them deliberately and clearly. For a wake word it is
fatal, because it specifically must *not* fire during ordinary
conversation.

The obvious remedy does not work: Vosk can return per-word confidences,
but "ich rufe michael an" was passed through as "michael" with **conf
1.00** - full confidence. A threshold does not separate real from false
hits.

**Consequence:** the wake word needs its own model, one that returns a
real probability instead of a forced match -
[openWakeWord](https://github.com/dscripka/openWakeWord) was already
suggested above and remains the candidate.

**Decided on 2026-08-17: "Sprachsteuerung starten" and
"Sprachsteuerung stoppen"** (Stephan's proposal). This is not a wake word
before every command but a **switch**: until "starten", DialOS listens
for that one sentence only; afterwards it accepts commands until
"stoppen" arrives.

In the same test the proposal proved **clearly better than the
assistant's name**:

| said | recognized | |
|---|---|---|
| "sprachsteuerung starten" | `sprachsteuerung starten` | fires |
| "sprachsteuerung stoppen" | `sprachsteuerung stoppen` | fires |
| "die **sprachsteuerung** von dialos ist praktisch" | `sprachsteuerung [unk]` | quiet |
| "kannst du das **starten**" | `starten` | quiet |
| "wir müssen das mal **stoppen**" | `stoppen stoppen` | quiet |

Where "Hallo Michael" failed on the distractor, the `[unk]` catch-all
holds up cleanly here: two specific words in direct succession barely
occur in conversation, and neither on its own triggers anything. That
leaves open whether openWakeWord is needed at all - **this is not proof
yet**, it was tested with a synthetic voice and three distractors, not
with real conversation over time.

The earlier proposal of using the assistant's name stays noted as a
fallback: it would come from the same setting as the voice selection
during first-run setup (see
[ersteinrichtung.en.md](ersteinrichtung.en.md): Michael, Daniel, Anna,
Julia).

**What a wake word does NOT solve:** the microphone indicator in the top
bar stays on. To hear the wake word, listening must continue - so the
recording stays open. And that is right: the device really is listening,
and for a target group that cannot see the screen, hiding exactly that
would be the worst option. What matters is that nothing leaves the device
- Vosk runs entirely offline.

## How fast does DialOS answer? (measured 2026-08-17)

This is not a comfort question. Someone who cannot see the screen has only
the answer as feedback - and when it fails to come, they speak louder
instead of waiting. That happened twice in one day.

| What | Before | Now |
|---|---|---|
| announcement "Ich höre." | 2172 ms | **about 1200 ms**, 1130 ms of which is the announcement itself |
| deafness after a switch | ≈ 5.1 s | while it speaks, plus 0.7 s |

The announcement time came down through an **announcement cache**: spoken
sentences are stored as WAV under `~/.cache/dialos/ansagen` and played
from there next time (details in `Debian-zu-DialOS.en.md`, step 11).

The deafness came down through **removing the lockout**. It was meant to
prevent double triggering, but it was redundant once the recording is
discarded and restarted after every utterance. What it actually did: after
a switch, 2.4 s of script including its announcement, 2.0 s of lockout and
0.7 s of reverberation pause - but the announcement ended after 1.5 s. So
the user heard the answer and spoke into a deaf system for 3.6 seconds.

**The lesson beyond this case:** "I have to speak louder" is almost always
a misleading fault description. Twice in one day the cause was a window in
which the system was not listening - and both times the report sounded
like a level problem. Anyone receiving such a report should first ask
**which** command in the sequence failed: Stephan's clarification "the
*second* command" solved it both times.

## Which microphone? (settled 2026-08-17)

**Always the built-in one.** No Bluetooth, no USB - the reasoning is in
`hardware.en.md`, section "What remains". In short: as long as DialOS
never opens a Bluetooth microphone, the device cannot drop into phone
quality, and a microphone that can be switched off endangers the entire
audio output through echo cancellation.

If the built-in microphone fails there is **no** fallback left - that is
deliberate. The service then announces it ("Ich finde kein Mikrofon.")
instead of being silently dead.

## Open questions

- ~~The concrete intent layer (custom middleware vs. an existing framework
  such as Rhasspy as a starting point) has not been decided yet.~~
  **Settled:** decided on 2026-08-13 in favour of hassil (see "Intent
  recognition" above); in practice a restricted Vosk grammar with a mapping of
  our own has been doing the job since 2026-08-16.
- The wake-word engine has not been finally decided yet.
