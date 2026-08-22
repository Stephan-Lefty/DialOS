[Deutsch](diktat.md) | [English](diktat.en.md)

# Dictation: speech to text

Measurements and decisions on free dictation. Begun on 2026-08-18.
Dictation is not an application but the precondition for four of them -
the user cannot produce letters, notes, mail or chat messages without it
(see [anwendungen.en.md](anwendungen.en.md)).

Not to be confused with command recognition: those are two operating modes
of the same tool. Command recognition works with a **restricted grammar**
of a few fixed sentences, dictation with **free recognition**. Why the
grammar is mandatory there is in
[sprachsteuerung.en.md](sprachsteuerung.en.md).

## The model: measured, not estimated

Both models are on the disk. Measured on 2026-08-18 with four dictated
sentences (letter, shopping list, private letter, appointment), spoken by
Piper - the established method that needs nobody to speak, see
`sprachsteuerung.en.md`.

| Model | Load time | Memory | Compute per second of audio | Word errors |
|---|---|---|---|---|
| `vosk-model-de-small` (92 MB) | 0.4 s | 229 MB | 0.12 | 2 of 53 (3.8 %) |
| `vosk-model-de-big` (3.2 GB) | 11.6 s | **5468 MB** | 0.17 | **0 of 53 (0.0 %)** |

**Memory is no obstacle:** the T490 has 46 GB. The big model's 5.5 GB do
not register. A compute factor of 0.17 means faster than real time, so
live dictation is possible.

**What the numbers do NOT show:** that was Piper's synthetic voice, which
is considerably cleaner than real speech in a room. The 0.0 % is the
ceiling, not the everyday figure. A test in Stephan's voice is still
missing and will come out worse.

**Consequence for the design:** 11.6 s of load time rules out loading the
big model only when "start dictation" is spoken - 11 seconds of silence
would be a defect to a blind user. Either it is preloaded, or the
announcement comes first and covers the wait.

## The real problem is not the recognition

Vosk delivers **words, not text**:

```
sehr geehrte damen und herren hiermit kündige ich meinen vertrag zum nächsten möglichen termin
```

No comma, no full stop, all lowercase. But German capitalises **all
nouns**. For a shopping list that is irrelevant, for a letter to the
health insurer it is not.

**An earlier statement in this project was too optimistic here.** On the
morning of 2026-08-18 it said "free dictation needs no new technology, only
work". That holds for the recognition. For *readable German text* it does
not.

### Three attempts to solve it without new technology - all around 90 %

| Method | Result |
|---|---|
| word list `/usr/share/dict/ngerman`, capitalise only unambiguous nouns | 48/53 = **90.6 %** |
| the same list plus "capitalise after an article/preposition" | 49/53 = 92.5 % |
| `hunspell -d de_DE` instead of the word list, plus the same rule | 48/53 = **90.6 %** |
| `hunspell -m`: a noun when one reading has a capitalised stem (Stephan's idea of using the spellchecker) | 49/53 = **92.5 %** |

Why it stops there, and both kinds of error are instructive:

- **The word list has gaps in base forms.** It contains "Vertrages",
  "Vertrags" and "Vertragsabschluss" but **not** "Vertrag". Likewise
  "Butter", "Dank" and "Wetter" are missing in capitalised form while
  "Termin" is present. Anyone using it as the truth about capitalisation
  gets random results.
- **hunspell is complete but too tolerant.** It accepts "vertrag" AND
  "Vertrag", "wetter" AND "Wetter" - both are valid German forms (verb
  form versus noun). So it cannot decide the question. It is useful in one
  place nonetheless: it rejects "einkaufszettel" and accepts
  "Einkaufszettel", so it knows the rules for compound nouns.
- **The heuristic "a noun follows an article" is wrong.** An adjective can
  follow "den". It produced "Sehr Geehrte", "Den Einkaufszettel", "für
  Deinen Brief" - it moves the errors instead of removing them.

**The conclusion is a limit, not an interim solution:** the remaining 10 %
need real grammatical knowledge, not a rule. At 150 words that is about 14
misspelled words per letter.

**The fourth attempt is the most instructive, because it came from the
right idea.** Stephan suggested running the finished text through the word
processor's spellchecker. That does not hit the mark, because it is **not a
spelling error** - "wetter" is a correctly spelled German word, and
LibreOffice uses the same hunspell for German. A check asking "does this
word exist" has nothing to object to.

One level deeper the idea does lead somewhere: `hunspell -m` prints the
morphological analysis, and that contains the stem.

```
vertrag    fl:V st:tragen fl:W                        <- stem "tragen", a verb
Vertrag    fl:V st:tragen fl:W   Vertrag st:Vertrag   <- additionally stem "Vertrag"
```

So a noun has a reading with a capitalised stem, a verb form does not. That
fixed the four old errors - "Vertrag", "Butter", "Dank" and "Wetter" came
out right. **Four new ones appeared:**

- **"ich Meinen Vertrag" and "es Gut das Wetter".** "Das Meinen" and "das
  Gut" are nouns as well. No dictionary can tell "es geht gut" from "das
  Gut" - that needs syntax.
- **"einkaufszettel" and "augenarzt" stayed lowercase.** Compound nouns are
  not in the dictionary as stems. And those are exactly the words that
  matter in a shopping list or a letter.

**That settles it:** four methods, all between 90 and 92.5 %, and the errors
merely move from one group of words to another. Lexically the problem is
not solvable.

**And the requirement is higher than first assumed** (Stephan, 2026-08-18):
in mail, capitalisation matters. That rules out treating messages like
private chat. Only the shopping list stays buildable right away; for mail
and letters correct casing is a hard requirement.

### What Debian offers for it: nothing

Checked on 2026-08-18: `languagetool`, `python3-spacy` and
`libreoffice-languagetool` are **not in the sources**. `python3-nltk` is
available (3.9.1-2) but does not solve this task for German. A tool for it
would therefore be a foreign package - against the project's line of
staying with Debian packages, and therefore a decision of its own rather
than a side step.

### LanguageTool measured (2026-08-18)

Downloaded and checked on Stephan's approval. LanguageTool 6.6, plus
`openjdk-21-jre-headless` 21.0.12 from **Debian's** sources - only
LanguageTool itself is a foreign package.

| Method | Hit rate |
|---|---|
| word list, unambiguous nouns only | 90.6 % |
| word list plus determiner rule | 92.5 % |
| hunspell instead of the word list | 90.6 % |
| hunspell -m, stem decides | 92.5 % |
| **LanguageTool** | **52/53 = 98.1 %** |

It catches exactly the words all four lexical methods failed on:
`einkaufszettel` and `augenarzt` (compounds) plus `vertrag`, `dank` and
`wetter` through dedicated rules (`VERTRAG_SUBST`, `DANK_SUBST`,
`ART_KLEINES_NOMEN`). And it correctly leaves "geehrte", "meinen", "gut",
"nächsten" lowercase - the four words my rules capitalised wrongly.

**The only error is "butter".** In "milch butter und" there is no article
before it, so `ART_KLEINES_NOMEN` does not fire, and "butter" is a valid
verb form. **Combining the methods would make it worse:** the stem rule
would get "Butter" right but "meinen" and "gut" wrong - 52 − 2 + 1 = 51.

**A measurement error of mine that distorted the figure at first:** on the
first run I passed all four sentences as **one** text without full stops.
That left only the very first word as a sentence start, so LanguageTool
could not capitalise "bitte"/"lieber"/"ich" - result 92.5 %, apparently no
progress at all. The other four methods had handled sentence starts
themselves. Passed sentence by sentence with the sentence start set by us
as everywhere else: 98.1 %. **Whoever compares methods must give them the
same preparation.**

**Operating cost, measured:**

| | |
|---|---|
| response time as a service | **0.6 to 1.6 s** per sentence |
| first request after start | 8.8 s - so the service must run, not start per sentence |
| invocation without a service (`languagetool-commandline.jar`) | 9.3 s - unusable for dictation |
| service memory | **1213 MB** resident |
| disk | 391 MB LanguageTool + 193 MB Java |

**Everything ran locally.** Every request went to
`http://localhost:8081`; the public service at languagetool.org was not
used and must never be - that would put the user's letters and mails on
someone else's computer.

**What it costs, named honestly:** LanguageTool is the project's first
foreign package. It does not come through `apt`, so it survives no system
update by itself and has to be remembered whenever a device is rebuilt.
1.2 GB of memory is negligible on the T490 with 46 GB, but not on a smaller
machine.

## Proposal: separate by purpose

Not one dictation for everything, but the requirement placed where it
matters:

| Purpose | Requirement | State |
|---|---|---|
| **Notes, shopping lists** | lowercase is irrelevant | buildable now |
| **Mail, chat** | **correct casing required** - Stephan on 2026-08-18: in mail, capitalisation matters | waits for the decision below |
| **Letters** | 10 % errors are not acceptable | needs a decision of its own |

For letters there are two honest routes, and neither is chosen quietly:
add LanguageTool as a foreign package, or have the letter checked by a
sighted helper before sending - the remote support for that is part of the
system anyway
([sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)).

## The first run in Stephan's voice (2026-08-18)

Three attempts, each showing something different. Evidenced by two
timestamped logs - `~/dialos-diktat.log` and `~/dialos-sprachbefehl.log`.

**The recognition is right.** "tomaten bananen äpfel" verbatim correct,
umlaut included, and turned into "Tomaten Bananen Äpfel" by LanguageTool in
one second. The big model loads in 8.8 to 9.1 s rather than the measured
11.6 - on the second run the file is in the filesystem cache.

**The stop phrase was the real fault, and it was mine.** I had looked for
"diktat beenden" in the free recognition. Stephan said it; the log shows:

```
erkannt: 'diktat wird erhöht'
```

In free recognition the model has tens of thousands of options; a SPECIFIC
sentence cannot be hit reliably. **That was the third encounter with the
same effect** - "gnome" became "genug", "windows" became "sinnlose",
"beenden" became "wird erhöht". Two would have been enough to draw the
rule.

**The answer is two recognizers over the same audio:** the big one for the
text, a small one with a grammar of exactly one sentence for the stop.
Cost: 0.4 s load time and 229 MB - negligible against the big model's
5.5 GB. On the next run it hit the sentence verbatim.

**A residual risk that became visible:** a grammar with only one sentence
tries to hear that sentence everywhere. Out of "Tomaten Bananen Äpfel" the
small recognizer made `'beenden beenden [unk]'`. It did not stop, because
an exact match with `diktat beenden` is required - but that condition is
the only thing standing in between. Whoever ever changes the stop phrase
must choose one that cannot arise from everyday speech.

**The separation of the recognizers is proven, not merely intended.**
Stephan deliberately said "auf Windows umschalten" in the middle of the
dictation. The sentence landed as text in the note, the desktop stayed
untouched, and the command service's log says:

```
14:55:31  Diktat laeuft - ich hoere nicht zu
14:55:45  Diktat beendet - ich hoere wieder zu
```

Between those lines not a single recognized sentence.

**Two logging mistakes of mine, both the same day and both from the same
cause.** On the first test the dictation wrote only to the terminal -
afterwards it was no longer possible to establish WHAT had been recognized.
On the second the command service had no timestamps, so it could not be
shown whether its recognized sentence came DURING the dictation. **A log
without a clock cannot evidence simultaneity** - and that was the whole
point of this guard. Both are retrofitted: the dictation always logs, the
command service logs with a clock.

**Still open:** Vosk only cuts an utterance at a pause in speech. Without a
pause everything lands in one line - on the second run two sentences became
`'tomaten bananen und äpfel auf sinnlose umschalten'`. For a shopping list
one line per entry would be better. Whether that can be steered through
the silence detection or whether the user has to make the pause is
untested.

## Piper spoke differently every time (found 2026-08-18)

Stephan heard that the read-back note did not match the tempo of the other
announcements. The cause lay two levels deeper than assumed, and my first
explanation was wrong.

**What I assumed first:** short announcements come from the cache, a new
sentence goes through speech-dispatcher - so the two sox chains must
compute different tempos. The measurement seemed to support it: 2.918 s
against 2.575 s for the same text.

**Refuted by a single measurement.** Passing **one** Piper output through
both chains yields 2.549 s either way. `pitch 1.00`, the only difference,
does not change the duration. So the 13 % did not come from the chains -
they came from my having invoked Piper twice.

**The real cause: Piper is not reproducible.** The same text, five runs:

```
2.575 s   2.562 s   2.865 s   2.456 s   2.628 s
```

**17 % spread**, without any setting having changed. Piper uses a VITS
model with a random component in phoneme duration (`--noise_w`, default
0.8).

| `--noise_w` | three runs |
|---|---|
| 0 | 2.390 / 2.390 / **2.390 s** |
| 0.4 | 2.470 / 2.351 / 2.430 s |
| 0.8 (before) | 2.615 / 2.865 / 2.984 s |

**Decided: `--noise_w 0`** (Stephan by ear, each variant played twice in a
row so the order could not mislead).

**Why this is more than uniformity:**

- **The announcement cache only becomes correct through it.** It freezes
  one output; as long as Piper was rolling dice, a cached announcement
  sounded audibly different from the same one freshly spoken. That is
  exactly what Stephan heard. Verified after the change: cached file
  0.939 s, freshly generated 0.939 s - identical to the millisecond.
- **Every speech-duration measurement in this project was a sample, not a
  number.** "1.13 s for 'Ich höre.'" carried an unknown spread of up to
  17 %. Only now is a comparison between two settings meaningful at all.
- **Side effect: about 12 % shorter announcements** without touching the
  tempo. "Ich höre." fell from 1.13 s to 0.939 s.

**The switch must be in TWO places** - in `piper-generic.conf` and in the
cache chain of `dialos-say.py`. If they diverge, cached sounds different
from fresh again. The cache invalidates itself on a change, because its key
contains the modification time of `piper-generic.conf`.

**A measurement I discarded as unfit:** asked whether it speeds up within a
sentence, I averaged word durations of the first against the second half.
The result (second half 3 to 35 % slower) is worthless, because the words
have different lengths - "ich" against "Kartoffeln". It evidences neither
way.

## Punctuation

Unsolved and not yet measured. The classic route is spoken punctuation
("Komma", "Punkt", "Absatz") which the user has to learn. What needs
checking is whether they can be reliably told apart from identical words
inside the text - "Punkt" can also be a word in a sentence.

## After the dictation: a hint instead of a read-back (Stephan, 2026-08-19)

Until 2026-08-19 "Diktat beenden" read the finished note out in full. That
sounded conscientious but was a mistake in two directions:

1. **It made "Einkaufszettel vorlesen" redundant.** Nobody needs a command for
   something that happens by itself anyway.
2. **It took the choice away from the user.** Whoever notes three items does not
   want to hear them three times. Whoever dictated twenty might well want to.

Since then DialOS confirms and says **how** to get the read-back:

> "Diktat beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel
> vorgelesen haben, dann sage: Einkaufszettel vorlesen."

**Why the count stays in.** It replaces the read-back: it is the only thing by
which a blind user notices that anything arrived at all - and how much. A bare
"Diktat beendet." would leave them in the dark.

**Why a hint and not a prompt.** A prompt ("shall I read it out?") demands an
answer and holds the device up until it comes. A hint costs nothing when it is
not needed.

**Why the hint comes from a table.** Only targets for which the read-out command
actually exists are named (`einkaufszettel`, `notizen` - see
`docs/sprachbefehle.en.md`). A later target such as "brief" gets the
confirmation only for now. Naming a sentence the grammar does not know would be
worse for a blind user than no hint at all: they would say it, nothing would
happen, and they would have no way of finding out why.

The read-back **with punctuation** lives on unchanged in `dialos-notiz.py`,
where it happens on request. The measurement behind it still holds: 3.670 s
without against 4.884 s with punctuation, and the difference consists entirely
of pauses.

## One entry per item - and how the user is supposed to learn that (2026-08-19)

**How the fault showed up.** Stephan dictated "Milch sechs Eier Butter" in one
breath, three times across three tests. He then complained about two things:
Michael had "read the list out 3x" and was "too fast again".

Both had the same cause, and neither was a fault in the read-back. The list
really did hold three lines - one per test:

```
Milch sechs Eier butter
Milch sechs Eier butter
Milch sechs Eier butter
```

DialOS correctly announced "3 Einträge". It is just that each entry was the
whole shopping trip. **Vosk delivers a sequence spoken in one breath as ONE
utterance, and one utterance is one entry.** And because the pause sits between
entries and not inside them, each line came out in a single breath - exactly
what Stephan heard as "too fast".

**What was not broken about it.** The mechanism works: pause briefly between
items and you get three utterances and therefore three entries. Nothing was
missing from the program - what was missing was DialOS **saying** so.

**The lesson, and it reaches beyond dictation:** where the user cannot see the
result, an operating rule is worthless as long as it goes unsaid. A sighted user
would have noticed after the first item that a single line was forming and would
have spoken differently of their own accord. A blind user finds out at the
read-back - a minute later and too late.

So for the shopping list DialOS now says it up front:

> "Ich schreibe mit. Sage jede Ware einzeln, mit einer kleinen Pause
> dazwischen."

One sentence, not three - while DialOS speaks it does not listen. And only for
the shopping list: for a note or a letter an utterance really is a sentence and
the instruction would be wrong.

**A fallback for whoever says it in one breath anyway.** "Milch **und** sechs
Eier **und** Butter" is split at "und" - which is how one speaks a shopping list
anyway. Deliberately only for list targets (`LISTEN_ZIELE`): in a letter "Ich
habe Milch und Butter gekauft" would otherwise become two lines.

Every split entry starts with a capital. The spell helper saw the utterance as
**one** sentence and capitalised only the first word; without the fix-up the list
would read "Milch / sechs Eier / Butter" - and a sighted helper reads that list
too.

**What this does not solve:** "Milch sechs Eier Butter" without "und" and
without a pause stays one entry. Splitting it reliably would need the word
timestamps Vosk supplies with `SetWords(True)` - a gap of more than roughly
0.4 s between two words would be a split point, even when it is too short to end
an utterance. Unmeasured, and therefore in `TODO.md` rather than presented here
as solved.

## The first correction of every session was a coin toss (2026-08-19)

On 2026-08-19 the dictation log held:

```
10:02:53    erkannt:     'milch sechs eier butter'
10:03:03    (LanguageTool nicht erreichbar: timed out)
10:03:03    geschrieben: 'Milch sechs eier butter'
```

Ten seconds between recognition and output - exactly the timeout. Measured after
restarting the service:

| Request | Duration |
|---|---|
| `/v2/languages` - **this** is what `lt_lebt()` checks as "running" | **1.3 s** |
| first `/v2/check` request - the German rules load here | **9.2 s** |
| second `/v2/check` request | 1.0 s |
| dictation timeout (`LT_ZEITGRENZE_S`) | 10.0 s |

**9.2 s against 10.0 s.** The first correction of every session hung on 0.8
seconds, and that morning it lost. Everything after that worked - each further
request costs about a second - leaving a one-off failure in the log that looked
like chance.

**Why nobody noticed:** `lt_lebt()` asks `/v2/languages`. That endpoint answers
in 1.3 s and loads no rules - so the service reports "running" while it still
needs nine seconds for the first real request. A readiness check that tests
something other than what matters.

**The earlier conclusion was incomplete, not wrong.** The unit has documented
"the first call costs 8.8 s" since 2026-08-18 and concluded "then make it a
long-running service". But a long-running service only **defers** the load time
to the first check request instead of removing it.

**Fixed at the root:** `dialos-schreibhilfe-warmlaufen.py` runs as the unit's
`ExecStartPost` and pushes one real sentence through. The nine seconds now fall
at login, where nobody is waiting for them. The `-` before `ExecStartPost` makes
a failure harmless: a service that has not warmed up is still better than none,
and `Restart=on-failure` must not loop because of it.

## How good the capitalization actually is (measured 2026-08-19)

Measured with `schreibung_richten()` itself, not with a reimplementation -
**10 out of 11** cases correct:

| Dictated | DialOS writes |
|---|---|
| `milch` | Milch |
| `butter` | Butter |
| `sechs eier` | Sechs Eier |
| `zwei liter milch` | Zwei Liter Milch |
| `kaffee und brot` | Kaffee und Brot |
| `sehr geehrte damen und herren` | Sehr geehrte Damen und Herren |
| `hiermit kündige ich meine mitgliedschaft zum nächstmöglichen termin` | Hiermit kündige ich meine Mitgliedschaft zum nächstmöglichen Termin |
| `ich rufe morgen den arzt an` | Ich rufe morgen den Arzt an |
| `der termin ist am dienstag` | Der Termin ist am Dienstag |
| `bitte den vertrag mitbringen` | Bitte den Vertrag mitbringen |
| `milch sechs eier butter` | Milch sechs **e**ier butter ← **wrong** |

**The only failure is a word list without grammar.** LanguageTool cannot decide
what is a noun there - the surrounding sentence is missing. Individually each of
those words comes out right, and individually is how they arrive since
2026-08-19, because each shopping-list item is its own entry.

**So capitalization is dependable for letters and mails** - those are whole
sentences. An earlier assessment that capitalization was the most urgent open
point is hereby withdrawn: the more urgent one was the load time above it.

## Spoken punctuation (2026-08-21)

Vosk delivers words, not characters. Irrelevant for a shopping list, the end of
usability for a letter. So the user speaks them:

| spoken | becomes |
|---|---|
| **Komma setzen** | `,` |
| **Punkt setzen** | `.` |
| **Fragezeichen setzen** | `?` |
| **Ausrufezeichen setzen** | `!` |
| **Doppelpunkt setzen** | `:` |
| **Gedankenstrich setzen** | ` - ` |
| **neuer Absatz** | blank line |
| **neue Zeile** | line break |

*The first draft used the bare words ("Komma", "Punkt"). Why they became
two-word markers is below under "Spoken punctuation only partly works" - in
short: measured, the short words were not recognised reliably.*

**All nine are in the vocabulary** of the big model - checked in
`graph/words.txt` with 822,389 entries. That check was mandatory: it was exactly
what had been missing for "löschen", where the command would silently never have
fired.

**And the obvious checking method does not work here.** The route via a
restricted grammar, which reports missing words on the small model, gives an
empty promise on the big one: it accepts no grammar at all (`Runtime graphs are
not supported by this model`) and therefore reports nothing either. Nine words
looked "present"; nothing had been checked. Only the model's word list answers
the question.

**Always punctuation** (Stephan's decision). The price: "in diesem Punkt"
becomes "in diesem." That shows up during read-back, and the passage gets
dictated again. The alternative would have been to split only at a speech pause -
Vosk provides word timestamps - but then anyone dictating fluently would get no
punctuation at all.

**Replacement is word-wise, not by text search.** Otherwise it would have hit
"Punkte", "Kommando" and "Absatzweise", and the text would fall apart at places
where nobody spoke a punctuation mark.

### What punctuation does for capitalisation - measured

The assumption was that LanguageTool decides capitalisation better with
punctuation. **For the nouns that is not true:** "Damen", "Herren", "Vertrag",
"Termin", "Kündigung", "Grüßen" came out the same with and without. What
punctuation delivers is the **sentence beginnings**:

```
without:  ... schriftlich mit freundlichen Grüßen
with:     ... schriftlich. Mit freundlichen Grüßen
```

In a letter that is not a cosmetic flaw but wrong. That is why punctuation runs
**before** LanguageTool. Lists are left out - on a shopping list "Butter." would
be no improvement.

## Silence produces text - the level gate (measured 2026-08-21)

The big model **invents words in silence**. Measured with Stephan's microphone
over 80 seconds of quiet: seven of them - `köln`, `einen gefunden`, `vom`,
`ln`, `einen`, `nun`, `schon`. In a dictation those land in the text. Someone
who pauses to think gets "köln" written into the middle of their termination
letter. This affects **every** dictation; on a shopping list it will so far
have passed as a misheard item.

Measuring the mean level per recognised utterance separates them cleanly:

| utterance | peak | mean |
|---|---|---|
| `'köln'` (noise) | 601 | **71** |
| `'nun'` (noise) | 1265 | **84** |
| `'einen'` (noise) | 528 | **47** |
| `'sechsundzwanzig'` (spoken quietly) | 2383 | **350** |
| whole sentences | 11606-13447 | **3475-4196** |

**The threshold is 150** - twice the loudest measured noise and less than half
the quietest genuine utterance.

**The check happens on the result, not on the audio stream.** A gate that
never lets quiet blocks through cuts words apart: between two syllables it is
silent. Checking the finished result costs nothing and can sever nothing.

**The same check protects the stop phrase** - though not as far as I first
assumed. I had thought it the best suspect for the unexplained
self-termination. **The next test disproved that:** a dictation terminated
itself again, after 4.2 s, and the level gate did not catch it - the noise was
loud enough. What the new log line revealed is in the next section.

## A bare "beenden" before the first utterance is not a stop

Twice on 2026-08-21 a dictation terminated itself, both times with **0
utterances beforehand** - once after 6 s, once after 4.2 s. The second time
neither the 3 s guard period nor the level gate caught it.

The clue sat in the line that had been added for exactly this purpose: the
**free recognition delivered nothing** in the same span, while the stop
recogniser delivered "beenden". The same audio, two recognisers, two results.
That is the restricted grammar: it **must** map every noise onto one of its
phrases, and the `[unk]` catch-all does not always win.

The first answer to that was a special case: discard a bare "beenden" **before
the first utterance**. It lasted one day.

### Counted - and that is why the stop now requires both words

All stop events of 2026-08-21:

| | bare "beenden" | full "diktat beenden" |
|---|---|---|
| **false** triggers | **6×** | 0× |
| **genuine** from the user | 3× | 2× |

**Every single false trigger was a bare "beenden".** Once the recogniser turned
a fragment of Stephan's dictation into "beenden" **while he was speaking the
letter**. The special case saved him there by chance - nothing had been
finalised yet. Once one sentence has arrived, the same fragment would have
stopped him mid-letter.

The consequential damage was visible: Stephan believed the dictation had
ended, said "Brief vorlesen" - and **that landed in the letter text**.

**Why it was decided differently before:** on 2026-08-18 the stop recogniser
produced something other than `[unk]` only twice in seven minutes of continuous
talking, both times a genuine "beenden". From that came "the word is enough".
But that measurement never checked what happens while **dictating** - and that
is exactly where the fragments arise.

The price is small: the full sentence was recognised cleanly twice on the same
day. And if it is not recognised, **DialOS says so**: "Sage bitte: Diktat
beenden.", at most every 15 seconds so the announcement does not itself become
noise and run back into the microphone. The user never again speaks into the
void without noticing - that was the real damage of the old rule.

This also removes the "nothing dictated yet" special case - one patch fewer.

**Every discarded utterance is logged.** If genuine speech ends up there, it
shows immediately, and the threshold belongs lower.

## Spoken punctuation only partly works (measured 2026-08-21)

Measured after building it, first with Piper, then with Stephan's voice:

| spoken | Piper is heard as | Stephan speaks, Vosk hears |
|---|---|---|
| "…Herren **Komma**" | ✅ | `komme` ✗ |
| "…Herren *(pause)* **Komma**" | `komme` ✗ | ✅ |
| **"Komma"** alone | `ja` ✗ | `einen koffer` ✗ |
| "…Vertrag **Punkt**" | ✅ | ✅ |
| **"Punkt"** alone | `das` ✗ | `kommt` ✗ |
| **"neuer Absatz"** | ✅ | ✅ |
| **"Doppelpunkt"** alone | `dörte depots` ✗ | - |

**Three out of six with Stephan's voice.** The pattern is neither the
pronunciation nor the pause - with Piper the exact opposite worked. It is the
language model: it guesses from context, and with short words it guesses
wrong. What consistently fails are the **isolated short words**; what
consistently works is **"neuer Absatz"**, two syllables longer and with
nothing to confuse it with.

This is the same lesson as for switching the voice control on: a marker word
must be **unambiguous and long enough**. "Komma" and "Punkt" collide with
"komme", "kommt", "Koffer", "das", "ja" - all words that occur in a letter.
**Open:** whether longer markers ("Komma setzen", "neuer Satz") solve it.

### Solved with two-word markers (second measurement, 2026-08-21)

Same voice, same chain, the longer forms:

| spoken | heard | |
|---|---|---|
| "…Rößner **Komma setzen**" | `komma setzen` | ✅ |
| "…Vertrag **Punkt setzen**" | `punkt setzen` | ✅ |
| "…helfen **Fragezeichen setzen**" | `fragezeichen setzen` | ✅ |
| "**neuer Satz**" | `neuer ersatz` | ✗ |
| "…Rößner **Komma**" *(control)* | `komma` | ✅ **this time** |

**Three out of three.** "neuer Satz" was therefore not adopted.

The bare "Komma" hit here after failing twice - and that is the worst case:
the user learns that it works, and then it does not.

**The bare forms were therefore removed**, and that is a double win: the
recognition becomes reliable **and** the price accepted at the outset
disappears. "In diesem Punkt", "drei Punkte" and "ein Komma an dieser Stelle"
stay untouched, because only "Punkt **setzen**" produces a mark.

## Whatever came after the last pause was lost (2026-08-21)

**The most serious fault of the day, and it had been there from the start.**
Vosk buffers audio and only delivers at a speech pause. Anyone who speaks a
letter **in one go** and then says "Diktat beenden" has both in the **same**
pause: the stop recogniser breaks the loop before the free recognition could
deliver its buffered text. `FinalResult()` was never called - the text was
gone.

The log said `0 Aeusserungen` although a whole letter had been spoken. Twice I
drew the wrong conclusions from that and searched elsewhere.

**Why it never showed:** on a shopping list you pause between items. Each item
is finalised on its own, and after the last pause there was usually nothing
left. Only the letter, spoken in one go, makes the fault visible.

Fixed: after the loop `FinalResult()` is fetched and sent down **the same
path** as every other utterance - punctuation, capitalisation, splitting. The
stop words are trimmed off, because the free recognition hears "Diktat
beenden" too, and that does not belong in the letter.

## The stop needs a speech pause (2026-08-22, verified offline)

Four repairs in one afternoon did not close it - guard period, level gate,
requiring both words, an announcement. Each time the next test found the next
gap, and once Stephan's dictation broke off mid-sentence after 12.1 seconds.
His verdict was the measure: **"I can never get to the end of this text."**

**The difference that actually exists:** a genuine "Diktat beenden" comes
*after* the user has finished the text - a pause precedes it. Every fragment
arises in the middle of the flow, where there is none. That is exactly what
has always protected the shopping list, without anyone planning it: "Milch."
Pause. "Butter." Pause.

The rule: within the last **5 seconds** there must have been a continuous
quiet stretch of at least **0.4 seconds**. Implemented as a pure function
`pause_davor()` - no clock, no microphone, so it can be checked against
recorded cases.

### Verified offline before anyone had to speak

`scripts/dialos-schlussregel-pruefen.py` lets Piper speak and sends the result
through the **real** code - `ist_schluss()`, `pause_davor()` and the level
threshold come from `dialos-diktat.py`, not from a reimplementation.

| Case | Result |
|---|---|
| **A** continuous speech, no stop phrase | 2 complete `'diktat beenden'` arose - **both rejected**, no stop |
| **B** same speech, pause, then "Diktat beenden" | the same two rejected, the genuine one accepted at 21.4 s |

What is remarkable about case A: plain speech produced **two complete** stop
phrases. Those would have passed the previous day's two-word rule - the pause
requirement rejects them.

### How short may the pause be?

Measured with inserted pauses from 0.0 to 1.5 seconds: **all were detected.**
The reason is instructive - Piper takes a breath of its own after a full stop.
So the rule keys not on an artificially inserted silence but on the **natural
sentence boundary**. For the user that means: nothing has to be done
differently.

**What it cannot do:** a fragment that happens to arise right after a speech
pause still gets through. Together with the three other conditions - both
words, level above the threshold, not within the first three seconds - the
residual risk is small, but it is not zero. The proof is still outstanding: a
dictation with a real voice that runs from beginning to end.
