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

## Punctuation

Unsolved and not yet measured. The classic route is spoken punctuation
("Komma", "Punkt", "Absatz") which the user has to learn. What needs
checking is whether they can be reliably told apart from identical words
inside the text - "Punkt" can also be a word in a sentence.
