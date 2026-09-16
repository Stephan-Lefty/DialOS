[Deutsch](pruefstand.md) | [Dictation](diktat.en.md) | [Voice commands](sprachbefehle.en.md) | [Changelog](../README.en.md#changelog)

# Test bench - measurements of 2026-09-15

*State: evening of 2026-09-15. Continuing on Wednesday, 2026-09-16.*

Stephan on 2026-09-15: we need a system that executes commands cleanly and on
the other side puts German text on paper cleanly - only then is DialOS a
solution that can make a difference. And in the evening: "evaluate everything
and document it precisely."

This document summarises the whole day: how things were measured, what came
out, which bugs the measurements found, what is decided and what comes next on
Wednesday. Details on dictation and commands are also in
[diktat.en.md](diktat.en.md) and [sprachbefehle.en.md](sprachbefehle.en.md).

---

## 1. Why a test bench

Until noon every dictation improvement was judged on **one** attempt - mostly
with Piper, which speaks more cleanly than any human. Several times something
was "fixed" that the next real attempt showed to be wrong or incomplete. The
test bench turns this around: **real recordings** are played through the
**real program**, and after every change the same recordings run again.

**Privacy:** all recordings live on the external disk under
`erkenner-vergleich/pruefstand/`, **never in the repo**. Stephan's consent of
2026-09-15 covers his own voice; other speakers need their own consent.

## 2. Setup

| Part | Where | What |
|---|---|---|
| Dictation recording | `dialos-diktat.py`, switch `~/.config/dialos/pruefstand` | exactly the audio the recognisers got (blocks in order, short blocks and epochs noted), plus log excerpt, result, microphone |
| Command recording | `dialos-sprachbefehl-desktop.py`, switch `~/.config/dialos/pruefstand-befehle` | every utterance with more than `[unk]`: audio since the previous result, state on/off, level history, microphone - **for one measurement session only**, includes conversation and TV |
| Microphone choice | `~/.config/dialos/diktat-mikrofon`, `~/.config/dialos/befehl-mikrofon` | name of a source; otherwise the "built-in microphone" decision applies |
| Parakeet test | `~/.config/dialos/parakeet-test` | letters and notes with Parakeet (option 3), commands still Vosk. **Built in for good since 2026-09-16** - switch off with `parakeet-aus`; `pruefen --vosk` sets that itself |
| Evaluation | `scripts/dialos-pruefstand.py` | `uebernehmen`, `pruefen --beide`, `befehle`, `befehle-beschriften`, `befehle-pruefen` |

**Dictation metrics:** word error rate (Levenshtein over normalised words,
numbers as words), wrong punctuation (at every word present in reference and
result, the mark after it: `, . ? ! :`, paragraph, line) and whether the same
commands fired ("Satz löschen", "Satz wiederholen", end).

**Command metrics:** per recording the service's decision against what was
really said - right, missed, rejected as "zu laut", falsely triggered,
non-command rightly ignored. The **effect** is compared ("Brief schreiben" and
"Brief erstellen" are the same).

## 3. Dictation: recognisers and microphones

### 3.1 Morning: recogniser comparison (measurement program, before the bench)

| Recording | Vosk | Parakeet | Whisper small | Whisper turbo |
|---|---|---|---|---|
| Shopping list, 20 items (verbatim right) | **16/20** | 11/20 | 13/20 | 13/20 |
| Letter paragraph, clean (word errors) | 7.6 % | **3.0 %** | 18.2 % | 39.4 % |
| Letter paragraph, disturbed | 60.6 % | **37.9 %** | - | - |

Whisper was dropped (slow, hallucinations). Parakeet drifted into English on
single words - **the shopping list stays with Vosk.**

### 3.2 Parakeet in real dictation - with and without spoken punctuation

| Test (Stephan's voice) | Vosk | Parakeet |
|---|---|---|
| 14:32 - letter **with** "Komma setzen"/"Punkt setzen" | 9.9 % | 14.9 % (command word arrived as "Sätzen") |
| 14:47 - letter spoken **naturally** (option 3) | 4.9 % | 6.2 % - but **all** punctuation, Vosk **none** |

Hence **option 3** (Stephan's choice): speak naturally, Parakeet sets full stops
and commas itself, only "neuer Absatz" and "neue Zeile" are spoken.

### 3.3 Test bench: four recordings of the same letter (state 16:49)

The same letter (71 words, 11 punctuation marks and paragraphs), spoken
naturally, one recording each, all replayed with the same program state:

| Microphone | quiet: Vosk | quiet: Parakeet | TV: Vosk | TV: Parakeet |
|---|---|---|---|---|
| built-in (echo cancellation) | 12.7 % / 5 of 11 marks wrong | **2.8 % / 0 of 11** | 16.9 % / 6 of 11 | 9.9 % / 0 of 11 |
| TONOR TC30 (USB desk microphone) | 8.5 % / 5 of 11 | 4.2 % / 0 of 11 | 8.5 % / 5 of 11 | **4.2 % / 0 of 11** |

Commands ("Diktat beenden") as recorded in all eight runs.

**Findings:**
1. **Parakeet is better in every situation** and sets all punctuation right.
2. **The desk microphone keeps the quality with the TV on, the built-in one
   does not** (2.8 % → 9.9 %). Without disturbance both are level - 2.8 vs 4.2 %
   is one and a half words.
3. On the device, with the TONOR the closing recogniser accepted "Diktat
   beenden" itself even with the TV on; with the built-in one only the fallback
   did.

## 4. Commands: measurement session 17:28-17:52

15 given commands (time, date, screenshot, reading out, PDF, create/print a
letter with confirmation, desktop look, stop/start) plus two sentences that are
not commands - four runs. 90 recordings: 67 labelled from sequence and log
(list command recognised exactly and executed), 10 by Stephan, 13 left open.

| Run | Command attempts | right | missed | rejected "zu laut" | false trigger |
|---|---|---|---|---|---|
| built-in, quiet | 21 | 18 | 3 | 0 | 0 |
| built-in, TV | 18 | 17 | 1 | 0 | 0 |
| TONOR, quiet | 17 | 16 | 1 | 0 | 0 |
| TONOR, TV | 19 | 18 | 0 | 1 | 0 |

**Findings:**
1. **No executed false trigger** among the labelled recordings. (At 17:29 a
   word salad switched to Windows - while Stephan was still reading out the
   list; that recording is unlabelled and not in the table.)
2. **The misses are almost all swallowed beginnings:** "tag haben wir", "datum
   haben wir", "haben sprachsteuerung stoppen". Stephan: between Anna's
   announcement and his answer he always has to wait about 1.5 seconds,
   otherwise the first word is swallowed. In the fourth run he deliberately
   waited a second - no beginning was lost there. **The microphone comparison
   for commands is therefore biased in favour of the TONOR.**
3. **The TV hardly disturbed commands** - the fixed sentence list is robust,
   unlike free text.
4. **Anna's voice reaches the command service through the TONOR** (no echo
   cancellation): "speichern" after "Das Bildschirmfoto ist gespeichert",
   "löschen", "notiz". Nothing was triggered.
5. **The TONOR clips at 100 % gain:** every utterance reached the maximum 32768.
6. **Limit of the command bench:** for 10 of 90 recordings a fresh recogniser
   heard something different from the live service (e.g. live "wie ist die
   uhrzeit", replay "es tag") - the stored excerpt reaches back only to the
   previous result, the running recogniser had more context. The table
   therefore counts the **live decisions**. Improvement for Wednesday: record
   the whole session continuously during a measurement session, so the service
   can be replayed block by block.

**Recordings left open (13)**, to label on Wednesday:
172849 "starten" (off), 172856 "tag haben wir", 172904 "uhrzeit", 172910 the
Windows word salad, 173102 "vorlesen", 173254 "notiz speichern ist", 173427
"stoppen", 173706 "haben wir", 174242 "starten" (off, before run 3), 174516
"notiz", 174534 "[unk] ist es", 174548 "datum haben wir", 174752 "starten".

**From the logs of the past weeks** (`dialos-pruefstand.py befehle`): the most
frequent "Das war kein Befehl" are cut-off questions - "haben wir" (5x), "ist
es" (3x), "wie viel" (2x). That fits finding 2.

## 5. Bugs found by the test bench and fixed

| Found | Bug | Fixed |
|---|---|---|
| first real recording | recording checked a folder only created by the first recording - Stephan's first recording was lost | check the measurement folder, warning in the log |
| TONOR letter 15:24 | **dictation hung:** fixed silence threshold 150, TONOR noise 220-330 - "Diktat beenden" never accepted, time limit never ran out | thresholds from the noise floor (5 % quantile of the last 30 s, 2.5 times, never below the old values); before 9.9 % and no end, after 4.2 % |
| TONOR letter | Vosk split "neue Zeile" in the middle, letter had "neue Zeil Zeile" | "zeil" counts too, remnant at the chunk start is dropped |
| TV letter | **"Neuer Absatz" as a chunk of its own was lost with Parakeet** | a chunk consisting only of a break is not empty |
| replay | **the first fix for that crashed dictation** (empty text) | guarded before it reached the device |
| TV letter | "Mit freundlichen Grüßen." with a full stop before the name | short line before a line break without full stop |
| letter 14:48 | genuine "Diktat beenden" rejected as "not silent afterwards" (reverberation 131-166) | command silence threshold 400 |
| letter 14:33 | "Okay" (Vosk: "ekd" for "Diktat") at the end of the letter | cut the closing remnant by word **end** |

## 6. State of decisions

- **Text (letters, notes): Parakeet, option 3** - decided; built in for good
  after two tests (freely worded letter; the TV test is done). When building it
  in: model (465 MB) and sherpa-onnx for all accounts under `/usr/local`,
  packaging, licence (CC-BY-4.0, credit NVIDIA).
- **Commands and shopping list: Vosk.**
- **Microphone:** the decision of 2026-08-17 ("always built-in") still applies.
  With background noise the measurements clearly favour a microphone close to
  the mouth - outdoors a headset. **Stephan's fundamental question** (whether
  voice control only works without background noise and is therefore
  unsuitable outdoors) can now be answered, but is not yet decided.

## 7. Device state in the evening (admin account)

| Switch | State | Effect |
|---|---|---|
| `parakeet-test` | on | letters and notes with Parakeet |
| `pruefstand` | on | every dictation is recorded |
| `pruefstand-befehle` | **off** | command recording removed after the session |
| `diktat-mikrofon` | off | dictation via the built-in microphone |
| `befehl-mikrofon` | **removed in the evening** | from the next login voice control listens via the built-in microphone again (until then still TONOR) |

The user account is untouched by all switches: Vosk, built-in microphone, no
recording.

## 8. Order for Wednesday

**State 2026-09-16:** items 1 and 2 built, simulated and installed. First test
with Stephan's voice (12:18, first version): 4 of 5 questions on the first try,
"datum haben wir" still lost the beginning - cause measured: the marker ends
0.64-0.70 s after the last sound. Second version with the reader: simulated 0/8
→ 8/8 (answer 0.15 s after the last sound), 3/8 → 8/8 (0.4 s). **Test with
Stephan's voice (12:48): 6 of 6 on the first try** - start, four time and date
questions without waiting, stop; the fastest answer came about one second after
"Ansage vorbei". With the faster new announcements
(13:10) Stephan's verdict: **"It is now like a normal conversation."**

**Side finding:** announcements not yet in the cache (every time of day) start
speaking only 2.3-2.7 s after the call, cached ones after 0.2 s.

1. **Close the gap after Anna's announcement** (command service): keep the
   recording open during the announcement and discard it, evaluate from its end
   with 0.3 s lead-in - as dictation has done since 09-14. With the raw TONOR
   make sure Anna's own words trigger nothing.
2. **Desktop-look rule** ("umschalten" plus a target anywhere) under the limit
   of two extra words.
3. **Lower the TONOR gain** (100 % clips) and measure again.
4. **Repeat the command measurement session** - without deliberate waiting,
   with continuous recording (see 4, finding 6); label the 13 open recordings.
5. **Parakeet test with a freely worded letter**, then decide on building it in.
6. **Noise simulation:** mix street, wind and café noise into the existing
   recordings - at what noise level does what break, per microphone and
   recogniser.
