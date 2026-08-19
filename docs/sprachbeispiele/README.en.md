[Deutsch](README.md) | [English](README.en.md)

# Speech samples

What DialOS sounds like without having the device in front of you. Created
on 2026-08-18 at Stephan's request.

**Regenerate** after every change to voice or tempo - otherwise the files
show a state that no longer exists:

```bash
scripts/dialos-sprachbeispiele.py
```

| File | Duration | What it is |
|---|---|---|
| `01-start-ansage-nutzer.ogg` | 29.3 s | The announcement at switch-on, as `nutzer` hears it. |
| `02-lautstaerke-frage.ogg` | 10.0 s | The volume question - only on the **first** login. |
| `03-sprachsteuerung-an.ogg` | 0.9 s | Reply to "Sprachsteuerung starten". |
| `04b-sprachsteuerung-zeitgrenze.ogg` | 3.5 s | When no command arrived for two minutes. Deliberately **with** a reason - a bare "Ich höre Dir nicht mehr zu." would leave the user guessing why. |
| `04-sprachsteuerung-aus.ogg` | 1.6 s | Reply to "Sprachsteuerung stoppen". |
| `05-desktop-windows.ogg` | 1.4 s | After "auf Windows umschalten". |
| `06-desktop-steht-schon.ogg` | 2.1 s | When the desktop is already in that style - a different announcement from a real switch, because a blind user could not otherwise tell them apart. |
| `07-diktat-beginn.ogg` | 3.7 s | Both sentences at the start of dictating a note. The first covers the ~9 s load time of the big speech model. |
| `07b-diktat-beginn-einkaufszettel.ogg` | 7.3 s | The same for the **shopping list** - with the instruction "Sage jede Ware einzeln, mit einer kleinen Pause dazwischen." Only here, because for a note an utterance really is a sentence. In operation the 9 s load time sits between the two sentences; in the file they follow one another. |
| `07c-diktat-ende-hinweis.ogg` | 8.1 s | After "Diktat beenden". No longer reads the note back but announces the count and how to get it read out. **The longest announcement in the system** - and thus at the limit of the project's own rule, see below. |
| `08-einkaufszettel-vorlesen.ogg` | 5.8 s | "Einkaufszettel vorlesen". The count comes first, then the entries with pauses. |
| `09-einkaufszettel-wegwerfen.ogg` | 5.3 s | The confirmation before emptying - now with "Sage ja oder nein.", because a blind user sees no buttons. |
| `09b-rueckfrage-nochmal.ogg` | 3.1 s | If no usable answer arrived, DialOS asks **once** more instead of aborting. |
| `10-ton-ueber-lautsprecher.ogg` | 1.5 s | When the Bluetooth speaker is switched on and the audio moves there. |
| `11-kein-mikrofon.ogg` | 3.5 s | A failure case - it is **announced**, not only written to the log. |

87 s and about 526 kB in total. OGG Vorbis, because `sox` can write it
without an extra package and WAV would bloat the repository needlessly.

## What the duration reveals about the announcements

The "duration" column is not decoration. While DialOS speaks it **deliberately
does not listen** - every second of announcement is a second the user has to
wait. That is why [../sprachbefehle.en.md](../sprachbefehle.en.md) carries the
rule "keep announcements short, but keep them sentences", and it comes from a
fault on 2026-08-17: **eight seconds of explanation were too much.**

`07c-diktat-ende-hinweis.ogg` runs **8.1 s** and therefore sits exactly at that
limit.

**Decided on 2026-08-19: the wording stays** (Stephan, after listening to all
four variants). Not against the rule, but because the rule does not apply here -
and that is the distinction the rule itself failed to record:

- It comes from the **desktop switch**. There the user is waiting to carry on;
  every second of announcement is in their way.
- After a **finished dictation** nothing is waiting. The user has just wrapped
  up and has no next command queued.

On top of that: the hint addresses whoever does **not** know the read-out
command. For them those two seconds of politeness are the difference between a
sentence they understand and a keyword they would have to memorise. And "the
system should sound personal" is Stephan's requirement from the same day.

The measured shortenings stay here regardless - should the judgement change in
everyday use, nobody has to measure again:

| Wording | Duration |
|---|---|
| "Diktat beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel vorgelesen haben, dann sage: Einkaufszettel vorlesen." | 8.05 s |
| "Diktat beendet, 3 Einträge geschrieben. Zum Vorlesen sage: Einkaufszettel vorlesen." | 6.07 s |
| "3 Einträge geschrieben. Zum Vorlesen sage: Einkaufszettel vorlesen." | 4.94 s |
| "Diktat beendet, 3 Einträge geschrieben." (no hint) | 2.88 s |

## The history lives in Git

Stephan's thought of 2026-08-18: keep it traceable how "Michael's voice"
developed. That needs **no** folder per date - every regeneration is a
commit, and the previous version stays retrievable:

```bash
git log --oneline -- docs/sprachbeispiele/
git show <commit>:docs/sprachbeispiele/03-sprachsteuerung-an.ogg > /tmp/old.ogg
```

Dated folders would merely duplicate what version control already does - and
grow the repository permanently on every change instead of only by the
difference.

## What is real about these files and what is not

**Real:** the voice (Piper, `de_DE-thorsten-high`), the tempo (0.88), the
pronunciation rules, and the **sentence structure** of the login
announcement - weekday, ordinal and the time as words are assembled by
`dialos-start-ansage.py` itself, and the sample uses exactly those
functions rather than a paraphrase.

**Example values:** date and time are fixed so the files can be generated
reproducibly. Battery levels and weather are invented - in operation they
come from the hardware and from the network. With no internet connection
DialOS says so and omits the weather.

**Not included:** speech input. These files show how DialOS sounds, not
how it listens - that needs a recording with a real voice, see
[../video-aufnahme.en.md](../video-aufnahme.en.md).

## Why this is reproducible

Only since `--noise_w 0` (2026-08-18). Piper has a random component in
phoneme duration and previously spoke the same sentence with up to **17 %**
different duration. So two runs of this script would have produced
differently sounding files. Background in [../diktat.en.md](../diktat.en.md).
