[Deutsch](sprachsteuerung.md) | [English](sprachsteuerung.en.md)

# Voice control

## Stack

- **Speech recognition (STT)**: Vosk with a German model, offline.
- **Speech output (TTS)**: Piper (more natural than espeak-ng), used as
  a backend for Orca - RHVoice was considered and dropped.
- **Screen reader**: Orca (the standard GNOME screen reader).
- **Low-level desktop control** (mouse, windows): Numen – Wayland-native,
  also Vosk-based, open source.
- **Intent recognition**: [hassil](https://github.com/OHF-Voice/hassil)
  (Home Assistant Intent Language) - adaptable matching via
  example-sentence templates instead of a rigid command grammar (see
  below).

## Implementation status (2026-08-16)

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

Solution: a small, locally running language model interprets the Vosk
transcription and maps it to the matching action, instead of expecting
exact phrasings. The flexibility applies to **understanding**, not to
**execution** — security-critical actions (system maintenance, approving
remote support) always stay behind an explicit yes/no confirmation,
regardless of how the command was recognized.

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

**On the wording itself, independent of the technology: the assistant's
name.** So "Hallo Michael", or "Hallo Anna" with a female voice. Two
reasons: two words fire accidentally far less often than one, and the
name is already established - the user picks their voice **by name**
during first-run setup (see
[ersteinrichtung.en.md](ersteinrichtung.en.md): Michael, Daniel, Anna,
Julia). The wake word would therefore come from the same setting as the
voice, with no second value to maintain anywhere.

**What a wake word does NOT solve:** the microphone indicator in the top
bar stays on. To hear the wake word, listening must continue - so the
recording stays open. And that is right: the device really is listening,
and for a target group that cannot see the screen, hiding exactly that
would be the worst option. What matters is that nothing leaves the device
- Vosk runs entirely offline.

## Open questions

- The concrete intent layer (custom middleware vs. an existing framework
  such as Rhasspy as a starting point) has not been decided yet.
- The wake-word engine has not been finally decided yet.
