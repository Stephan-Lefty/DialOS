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
| `04-sprachsteuerung-aus.ogg` | 1.2 s | Reply to "Sprachsteuerung stoppen". |
| `05-desktop-windows.ogg` | 1.4 s | After "auf Windows umschalten". |
| `06-desktop-steht-schon.ogg` | 2.1 s | When the desktop is already in that style - a different announcement from a real switch, because a blind user could not otherwise tell them apart. |
| `07-diktat-beginn.ogg` | 3.7 s | Both sentences at the start of a dictation. The first covers the ~9 s load time of the big speech model. |
| `08-einkaufszettel-vorlesen.ogg` | 5.8 s | "Einkaufszettel vorlesen". The count comes first, then the entries with pauses. |
| `09-einkaufszettel-wegwerfen.ogg` | 3.9 s | The confirmation before emptying. |
| `10-ton-ueber-lautsprecher.ogg` | 1.5 s | When the Bluetooth speaker is switched on and the audio moves there. |
| `11-kein-mikrofon.ogg` | 3.5 s | A failure case - it is **announced**, not only written to the log. |

63 s and about 380 kB in total. OGG Vorbis, because `sox` can write it
without an extra package and WAV would bloat the repository needlessly.

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
