[Deutsch](video-aufnahme.md) | [English](video-aufnahme.en.md)

# Recording demo videos

How DialOS is filmed so that speech output and speech input arrive as
separate tracks in the edit. Set up and proven on 2026-08-17.

## What cannot be recorded - and why

Two limits shape the whole procedure. They cannot be programmed away:

- **The system start.** At boot time no recording software is running
  yet.
- **The user switch.** The recorder runs *inside* a session and dies at
  logout.

Both need a **camera on a tripod**. That is not a stopgap: the AIRHUG is
a speaker, not an earpiece - so the camera picks up Michael's
announcement *and* the spoken commands in the room, exactly what a
visitor would hear. For "switch the device on, the stick is in, it
introduces itself" that is even more convincing than a screen recording.

Everything happening **within one session** - the desktop switch, for
instance - is recorded with OBS, because there the screen content is what
matters.

## OBS: the setup

Package `obs-studio` (Debian 13: 30.2.3). The configuration lives in
`~/.config/obs-studio/` and consists of three files:

| File | Purpose |
|---|---|
| `global.ini` | preselects the "DialOS" profile and scene collection, skips the setup wizard |
| `basic/profiles/DialOS/basic.ini` | output mode, resolution, **`RecTracks=7`** |
| `basic/scenes/DialOS.json` | scene with three sources and the track assignment |

**`RecTracks=7` is the decisive value.** It is a bitmask: 1 = track 1,
2 = track 2, 4 = track 3, together 7. Without it OBS writes a single
mixed track and the edit could no longer separate them.

Which source lands on which track is set in the scene as `mixers` (same
bitmask, per source):

| Track | Content | `mixers` |
|---|---|---|
| 1 | mix of both - reference only, for reviewing | – |
| 2 | **DialOS voice**, capture of the output | `3` (tracks 1+2) |
| 3 | **microphone**, the spoken commands | `5` (tracks 1+3) |

Recordings land in `~/Videos/DialOS`, 1920×1080 at 30 fps (scaled down
from 3072×1728), format **MKV**. MKV deliberately rather than MP4: if the
recording aborts, an MKV is still usable, an MP4 would be lost. Kdenlive
reads both.

**The tracks carry no names in the file.** The entries under
`[AudioTracks]` in `basic.ini` only affect the OBS interface, not the
MKV. In the editor they are simply 1, 2, 3 - the order above applies.

## The two traps that ruin the audio

Both occurred for real on 2026-08-17, each shortly before recording:

**1. The headset drops to phone quality.** The AIRHUG cannot do A2DP and
HFP at once. As soon as anything opens its microphone it switches to
`headset-head-unit` - and the very voice meant to be recorded then sounds
like a phone call. Directly readable from the monitor source:

| Profile | Output capture |
|---|---|
| `headset-head-unit` (HFP) | 1 channel, 16000 Hz |
| `a2dp-sink` | 2 channels, 48000 Hz |

That is why the scene has the **built-in microphone hard-wired**, not
"default". Check before every recording:

```bash
pactl list cards | grep -A1 "Name: bluez" ; pactl list short sources | grep bluez_output
```

If it shows HFP, switch back:

```bash
pactl set-card-profile bluez_card.<MAC> a2dp-sink
```

**2. Something grabs the Bluetooth microphone anyway.** The remedy is to
make the built-in microphone the default input, so no program can catch
it by accident:

```bash
pactl set-default-source alsa_input.pci-0000_00_1f.3.analog-stereo
```

## Recording procedure

In OBS under **Settings → Hotkeys**, bind "Start/Stop Recording" to
`F9`/`F10`. This has to happen in the interface: OBS writes its
configuration back on exit and overwrites changes made to the files while
it runs.

1. Start OBS, minimize it with `Super`+`H` (the GNOME standard has no
   minimize button in the title bar, only close)
2. `F9`, then two seconds of silence
3. Demonstrate, speaking the commands
4. `F10`

Two things that would otherwise look like faults when watching: about a
second passes between the spoken command and the reaction - the service
waits for the pause in speech. And **while DialOS speaks it deliberately
does not listen**; a command spoken into the announcement is ignored (see
[sprachbefehle.en.md](sprachbefehle.en.md)).

## When editing

The built-in microphone also picks up the AIRHUG speaker. So track 3
contains Michael as well, only duller. When mixing, pull track 3 down and
take Michael's voice from track 2, otherwise it sounds doubled.
