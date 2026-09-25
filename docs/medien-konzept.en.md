[Deutsch](medien-konzept.md) | [English](medien-konzept.en.md)

# Concept: radio, music, news and podcasts

**As of 2026-09-25, a collection of ideas - none of it is built yet.** Stephan:
"next we'll take care of radio, listening to music, listening to the news,
listening to podcasts." This paper collects what is decided, proposed and open
for that, so the build starts with a plan instead of with the first command.

## Decided

**One player for everything: Rhythmbox** (Stephan, 2026-09-25). Radio, music,
news, podcasts and audiobooks all run through the same program.

- **Why not Shortwave for radio:** Shortwave cannot be told a station from
  outside - no command line for it, and over MPRIS only play and pause of the
  station last listened to. "Spiel Radio Tirol" would not be possible.
  Shortwave stays installed, but without voice control.
- **Why only one player:** when the user says "lauter", "stopp" or "was läuft
  gerade?", it must be clear what is meant. With two players it would not be -
  and the user cannot look which window is in front. The one-player rule from
  [anwendungen.en.md](anwendungen.en.md) takes care of itself.
- **DialOS is the hub, Rhythmbox only the loudspeaker.** DialOS takes the
  command, finds the station or episode and tells Rhythmbox what to play. Only
  the sighted helper needs the Rhythmbox window.

## The building blocks

### 1. The media list - the selection

A curated list instead of the whole station database:
[medienliste.md](medienliste.md) (German). It applies to the whole device. Two
reasons:

- **Manageable:** ten stations the user really listens to are worth more than
  ten thousand they cannot remember.
- **Speakable:** command recognition (Vosk with a restricted grammar) only
  knows words from its vocabulary. Every name on the list is checked first and
  gets a spoken form where needed - like "Tas tatur".

**Stephan is building a small app** to capture it. The proposed exchange format
(not decided yet) is in [medienliste.md](medienliste.md): a JSON file with
`art`, `sprechform`, `name`, `land`, `quelle`. DialOS reads it when voice
control starts and builds the command sentences from it.

**Later: personal favourite stations** per account through the personal-data
mask - the same idea as the mail account: capture centrally, distribute to the
programs.

### 2. Finding stations - radio-browser.info

The same free station database Shortwave uses, without account or key. It is
queried **when the list is maintained**, not on every command: the checked
stream address is then in the list, and playing does not depend on the
database being reachable at that moment.

- Search by name: `https://de1.api.radio-browser.info/json/stations/byname/<name>?hidebroken=true`
- What counts is `url_resolved` (the resolved stream address), plus
  `stationuuid` to find a station again later.
- Tried on 2026-09-25: "Radio Tirol" immediately returns three streams of Life
  Radio Tirol (MP3 and AAC).
- **If a stream fails**, DialOS looks up the current address via the
  `stationuuid` and announces it - instead of silently playing nothing.

### 3. Playing - rhythmbox-client

Everything the voice commands need is there (checked 2026-08-18 and
2026-09-25): `--play-uri`, `--pause`, `--play-pause`, `--stop`, `--next`,
`--set-volume`, `--print-playing`. The last one matters: DialOS can announce
what is playing. For the position (podcasts, audiobooks) MPRIS over D-Bus is
added (`Position`, `SetPosition`).

### 4. Podcasts and news podcasts

Podcasts are RSS feeds. DialOS reads the feed, takes the newest episode (the
address in the `enclosure`) and hands it to Rhythmbox. **DialOS manages the
resume position itself** - Rhythmbox stores no playback position (checked
2026-08-18: no `playback-position`, no `bookmark`). When stopping, the position
is read over MPRIS and remembered per episode under `~/.config/dialos/`, and
set again on "weiter hören".

### 5. News - still open, both are possible

- **As a station:** "Nachrichten hören" starts a news station live.
- **As the newest episode:** a short news programme as a podcast that appears
  several times a day - the user always hears the current edition, in a few
  minutes, and then it is quiet.

Both can stand side by side in the list; which form the sentence
"Nachrichten hören" triggers is Stephan's decision.

### 6. Audiobooks

Audiobooks are files, not stations - a folder on the device or on the
`DIALOS-DATA` stick. The resume position matters here as with podcasts: nobody
listens to an eight-hour audiobook that starts from the beginning every time.

## Voice commands - first draft

None of it is checked. Every sentence has to pass both mandatory checks from
[sprachbefehle.en.md](sprachbefehle.en.md): the model's vocabulary AND the
full grammar.

| Sentence | What happens |
|---|---|
| "Radio einschalten" | Last station - or the question "Welcher Sender?" with the list |
| "Spiel <spoken form>" / "<spoken form> einschalten" | Station from the list |
| "Nachrichten hören" | News station or newest news episode (open) |
| "Podcast <spoken form>" | Newest episode, or where it was left off |
| "Musik abspielen" | Own music, shuffled or the last one played |
| "Weiter hören" | Podcast/audiobook at the remembered position |
| "Was läuft gerade" | Announcement via `--print-playing` |
| "Lauter" / "Leiser" | Volume in fixed steps |
| "Nächster Sender" | Next entry of the list |
| "Stopp" / "Radio ausschalten" / "Musik ausschalten" | Stop, remember the position |

**Resolving the existing contradiction:** today "Radio öffnen" and "Musik
öffnen" open Shortwave and Rhythmbox, while "Radio einschalten" and "Musik
abspielen" say that DialOS cannot do it yet. With the build all four get the
same meaning: play through Rhythmbox.

## Things to keep in mind

- **Announcements during music.** When DialOS speaks while something is
  playing, the music has to get quieter or pause - otherwise the announcement
  is lost. Quieter or pause is an open decision (TODO "announcements quieter
  than music").
- **Command recognition is listening.** Music and radio go through the echo
  cancellation (`dialos_mikrofon_ohne_echo`), so a newsreader who happens to
  say a command triggers nothing. That is exactly what it was built for on
  2026-08-17 - check it with radio playing in the background during the build.
- **Bluetooth speaker:** music through the AIRHUG in A2DP; the device must not
  slip into the headset profile (HFP) - which is why DialOS opens no Bluetooth
  microphone (audio decision 2026-08-17).
- **Privacy:** the query to radio-browser.info reveals the station name
  searched for, nothing else; no account. Streams and feeds come directly from
  the broadcaster. The log records what was played - less sensitive than a
  dictation, but it belongs in the log table of
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md).
- **Account `nutzer`:** the media list is system-wide, resume positions are per
  account. After the build both belong in `dialos-nutzerkonto-pruefen.sh`.

## Proposed order

1. Fill the media list (Stephan, with his app) and settle the format.
2. Radio: play a station from the list, stop, louder/quieter, "was läuft
   gerade". The smallest path that is needed every day.
3. News - once the form is decided.
4. Podcasts with resume position.
5. Music from the own collection, audiobooks.
6. Update the docs: sprachbefehle, anwendungen, recipe, installation guide.
