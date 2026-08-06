[Deutsch](sprachsteuerung.md) | [English](sprachsteuerung.en.md)

# Voice control

## Stack

- **Speech recognition (STT)**: Vosk with a German model, offline.
- **Speech output (TTS)**: Piper or RHVoice (more natural than
  espeak-ng), used as a backend for Orca.
- **Screen reader**: Orca (the standard GNOME screen reader).
- **Low-level desktop control** (mouse, windows): Numen – Wayland-native,
  also Vosk-based, open source.
- **Intent recognition**: flexible/LLM-based matching instead of a rigid
  command grammar (see below).

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

## Open questions

- The concrete intent layer (custom middleware vs. an existing framework
  such as Rhasspy as a starting point) has not been decided yet.
- The wake-word engine has not been finally decided yet.
