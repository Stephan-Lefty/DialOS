[Deutsch](hardware.md) | [English](hardware.en.md)

# Hardware

## Target device

A lightweight laptop that can be used not only at home but also while
travelling. This tends to rule out plain USB-stick WWAN dongles (fragile,
less robust) and favors a built-in WWAN module in a lightweight business
laptop.

With the additional, strongly hardware-dependent features (voice control,
encryption stick, possibly WWAN telephony), the project moves from "ISO
for any laptop" towards "ISO + a defined/recommended reference hardware" —
a concrete model choice (e.g. ThinkPad X1 class) is still open.

**Superseded since 2026-08-16, added here on 2026-09-25:** there is no ISO
any more, neither for arbitrary laptops nor as a reference ISO. Every device
is built in the office from a regular Debian 13 installation (see
[installationsanleitung.md](installationsanleitung.md), German only, and
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md)); a finished device is
backed up as a Rescuezilla image. The direction of this paragraph still
holds: DialOS needs defined reference hardware, because microphone,
Bluetooth audio and standby have to be checked per model.

## Computer specification for DialOS (as of 2026-09-17)

Stephan on 2026-09-17: an assessment of the laptop hardware needed so that voice
control, audio and video playback and the whole system run smoothly - with Intel
and, as an alternative, with AMD. His requirement: **32 GB of RAM as the
minimum.**

### What DialOS really needs (measured on the T490, 2026-09-17)

Measured on the test T490 (Intel Core i7-8665U, 4 cores/8 threads, AVX2; 46 GB
usable, NVMe SSD). Estimates for other processors are marked as such.

| Part | RAM | Disk | Time |
|---|---|---|---|
| Dictation: big Vosk model | **5.3 GB** peak while loading | 3.2 GB | 11 s to load |
| Dictation: Parakeet (int8) | about 1 GB | 0.6 GB | 2.3 s to load; 10 s of speech recognised in 0.73 s |
| LanguageTool writing aid (Java, always on) | 0.8 GB | 0.4 GB | – |
| Voice control (always on) | 0.3 GB | 0.1 GB (small model) | – |
| Piper voices | briefly | 0.2 GB | new announcement 1.4–1.7 s |
| GNOME, Firefox, Thunderbird | 2–4 GB | – | – |
| System partition total | – | **19 GB** used | – |

**During dictation this adds up to 9–10 GB.** The bottleneck is RAM, not the
processor: with 8 GB the system swaps while dictating and stalls noticeably;
16 GB is just enough as long as little else is open. **32 GB as the minimum**
(Stephan's requirement) leaves headroom for a browser with many tabs, video calls
and future, larger speech models.

**Why not 16 GB, even though the measurements would allow it** (Stephan,
2026-09-17). The question is a fair one and it was asked: measured, 16 GB is
enough, used devices with 16 GB are plentiful and considerably cheaper, and the
target group rarely has much money. Three reasons settle it anyway:

1. **Upgrading later is not an option here.** The devices are shipped fully
   configured and supported remotely. A memory upgrade means shipping the
   device there and back plus working time - and in between, a blind person is
   without their computer for a week. That is not the same as for a sighted
   user who reaches for their phone in the meantime. The shipping alone, both
   ways, eats up the surcharge paid at purchase.
2. **With soldered memory, upgrading does not exist at all.** See "Soldered
   memory" below. The decision is made once, at purchase, and it is final.
3. **The first deliveries are planned for 2027**, presumably already with
   Debian 14 and GNOME 50. The lower bound is therefore being set for systems
   that do not exist yet, and the device is meant to last for years after that.

**Socketed memory takes precedence over soldered** (Stephan, 2026-09-17) - not
in order to upgrade later, but so that a faulty module stays a module
replacement instead of becoming a device replacement. For a device the user
cannot do without, repairability is the same argument as headroom, just for the
other failure case. Where only soldered memory is available, the rule stands:
32 GB from the factory.

### Requirements

| | Minimum | Recommended |
|---|---|---|
| **RAM** | **32 GB**, socketed preferred | 32 GB socketed, or 64 GB |
| **Processor** | 4 cores/8 threads with AVX2 (performance like i7-8665U) | 6–8 cores, current generation (see below) |
| **SSD** | 256 GB NVMe | **512 GB NVMe** (100 GB system + encrypted user partition) |
| **Graphics** | integrated (Intel/AMD) | integrated with hardware decoding for H.264, HEVC, VP9, **AV1** |
| **Microphone** | built-in dual microphone | microphone array with good noise suppression, **checked under Debian 13** |
| **Ports** | 1× USB-A, 1× USB-C, audio jack | 2× USB-A (security stick + USB microphone), USB-C with charging, audio jack |
| **Wireless** | Wi-Fi 6, Bluetooth 5 | **Intel AX210/BE200** (Wi-Fi 6E/7, Bluetooth 5.3) |
| **Display** | 14" Full HD, matte | 14" Full HD or higher, matte, bright (≥ 300 cd/m²) |
| **Battery** | 6 hours | 8 hours or more |
| **Keyboard** | tactile marks on F and J | plus backlight, clear actuation |

**Why the processor matters less than expected:** on the 2019 i7-8665U,
Parakeet recognises ten seconds of speech in 0.73 s - fourteen times faster than
spoken. Any current mid-range processor with AVX2 has headroom. Entry-level chips
such as the Intel N100 (4 cores without hyper-threading) should be roughly half
as fast by estimate - usable, but with noticeably longer loading and waiting;
not measured.

### Linux pitfalls when buying - regardless of vendor

- **Check the built-in microphone under Debian 13** before a model becomes the
  reference. Digital microphones hang off the "Smart Sound" DSP (SOF firmware) on
  Intel and off "ACP" on AMD - both need matching kernel and firmware entries per
  model. Without a working microphone DialOS cannot be operated.
- **No Nvidia graphics chip.** It brings nothing for DialOS and makes drivers,
  standby and battery harder.
- **Firmware via LVFS/fwupd** - DialOS installs firmware updates with it (step
  13d). Lenovo ThinkPad, Dell Latitude and HP EliteBook are well represented
  there, many consumer devices hardly.
- **Soldered memory:** many current devices have LPDDR5 soldered on. Then order
  **32 GB from the factory** - it cannot be upgraded.
- **Standby:** newer devices only know "Modern Standby" (s2idle). DialOS turns
  standby off on mains power anyway (step 11j); on battery, check that the device
  wakes up again.

### Intel variant

| | |
|---|---|
| Processor | Intel Core Ultra 5/7 (series 1 or 2) or Core i5/i7 from 12th generation (U/P) |
| Graphics | Intel Iris Xe / Arc integrated - AV1 decoding from 11th generation |
| Wi-Fi/Bluetooth | usually Intel from the factory - most reliable under Linux |
| Microphone | via SOF firmware (`firmware-sof-signed`) - check per model |
| New examples | Lenovo ThinkPad T14 (Intel), Dell Latitude 5450, HP EliteBook 840 |
| Used examples | ThinkPad T14 Gen 2/3 (Intel) - successor of the T490; Gen 3 has one slot, 32 GB possible |

### AMD variant

Current-generation AMD processors are an equivalent, often cheaper alternative
for DialOS with better graphics and battery life.

| | |
|---|---|
| Processor | **AMD Ryzen 5/7 7640U/7840U** (Zen 4, "Phoenix"), **8640U/8840U** ("Hawk Point") or **Ryzen AI 5/7 PRO** (Zen 5); used also Ryzen 5/7 PRO 6650U/6850U (Zen 3+) |
| Advantage for speech recognition | Zen 4/Zen 5 additionally support **AVX-512** - the ONNX runtime behind Parakeet uses it; faster than AVX2 alone (not measured) |
| Graphics | Radeon 760M/780M (Zen 4) or 880M/890M - **AV1 decoding from Ryzen 6000**; Ryzen 5 7530U (Zen 3) has **no** AV1 decoding |
| Kernel | Debian 13 ships kernel 6.12 - Zen 3+/Zen 4 are well supported; Ryzen AI 300 ("Strix Point") is newer, check before buying |
| Wi-Fi/Bluetooth | **often MediaTek MT7922 or Qualcomm from the factory** - works under Linux, but Bluetooth audio is more reliable with Intel. Where possible order or swap to **Intel AX210** (M.2 2230) |
| Microphone | via AMD ACP (`snd_acp`/`snd_pci_ps`) - some models lack the kernel entry, then the microphone stays silent: **check under Debian 13 before deciding** |
| Memory | Zen 4 devices almost always have **LPDDR5 soldered** - order 32 GB from the factory |
| NPU | not used by DialOS (no benefit for Parakeet/Vosk under Linux) - not a reason to buy |
| New examples | Lenovo ThinkPad T14 Gen 5 AMD (Ryzen 7 PRO 8840U), ThinkPad E14 Gen 6 AMD, HP EliteBook 845 G11 |
| Used examples | ThinkPad T14 Gen 3/4 AMD (Ryzen 5/7 PRO 6650U/7840U, 32 GB soldered) |

**For both variants:** before deciding, run a device with Debian 13 through the
DialOS setup and check specifically: built-in microphone (level, echo
cancellation), Bluetooth speaker (A2DP and waking up), standby on battery,
firmware via fwupd, and a dictation through the test bench. Only that makes a
model the reference.

## Reference audio device (decided 2026-08-16)

**AIRHUG 01** – a Bluetooth headset, speaker and microphone in one. This
settles the most important open hardware question: voice control is
developed and tuned against this device.

Technical details, read off the reference device:

| | |
|---|---|
| Bluetooth name | `AIRHUG 01` |
| Device class | `0x00240404` (audio/headset) |
| Profiles | **A2DP** (audio sink) and **HFP** (handsfree) |
| Battery reporting | via UPower, appears in the startup announcement |

**The decisive point for voice control:** the device cannot do A2DP and
HFP at the same time. A2DP gives good playback but has no microphone
channel; HFP provides the microphone but noticeably degrades playback
quality. That is why
[`dialos-start-ansage.py`](../iso-build/config/includes.chroot/usr/local/bin/dialos-start-ansage.py)
switches to `headset-head-unit` before recording and back to `a2dp-sink`
afterwards – this profile switch is not a quirk of the code but a
property of the Bluetooth profiles themselves, and will be needed with
any comparable headset.

Why a headset rather than the built-in laptop microphone: the comparison
test was unambiguous (see [offene-punkte.en.md](offene-punkte.en.md),
section "Voice control"). The built-in microphone remains intended as a
not-yet-implemented fallback.

**Superseded since 2026-08-17 (audio ruling, Stephan):** the AIRHUG now
serves **output** only (A2DP). **Input is always the built-in microphone** -
the voice services take it via the echo source `dialos_mikrofon_ohne_echo`,
which itself sits on the built-in microphone. The switch to HFP
(`headset-head-unit`) above only happens as a **fallback** now, when a
device has no built-in microphone at all. Reasons: switching back to A2DP
got stuck three times on 2026-08-17, echo cancellation exists only on the
built-in path, and the comparison test ran with the built-in microphone
over-amplified by 60 dB (details further down under "What remains" and in
[offene-punkte.en.md](offene-punkte.en.md)). For other programs the raw
built-in microphone deliberately stays the default microphone
(Firefox/Jitsi cancel echo themselves; Stephan's decision of 2026-09-25).
The paragraph above stays as the state of 2026-08-16.

**Mandatory rule (Stephan, 2026-08-16): the fallback to the built-in
speakers and microphone must always be guaranteed.** A switched-off,
empty or disconnected headset must never leave DialOS mute or deaf - for
a blind user that would be the total failure, because they would not even
notice the headset is off. Implementation status and what remains open:
see [offene-punkte.en.md](offene-punkte.en.md).

**Still to clarify:** whether the device announces its own firmware
prompts ("connected", low battery) in German. Standard Bluetooth profiles
offer no remote control over this, it is purely device-dependent – but
not a side issue on a system for blind users, since they necessarily hear
those prompts.

## Range and buttons: why one device is not enough

**Recognized on 2026-08-17 through Stephan's question:** the laptop sits
on the desk, the Bluetooth speaker on the living room table playing the
radio - how does the user change the volume from there? Not via the
laptop's built-in microphone.

This is not a detail but hits the intended normal case. Hence the
requirement: **the input device must be where the user is. The output
device can be anywhere.**

### What the AIRHUG 01 can do - and what it cannot

| | |
|---|---|
| A2DP (good playback) | `sources: 0` - **no microphone** |
| HFP (microphone available) | playback drops to 1 channel / 16000 Hz |
| Buttons on the device | do **not** reach the laptop |
| Volume buttons on the device | do **not** report back to the computer |
| Setting the volume **from the computer** | works (checked twice on 2026-08-17, the second time with the device at 100 %) |

The first two rows are a property of Bluetooth, not a configuration
question: the device cannot sound good and listen at the same time.

Rows three and four were measured on 2026-08-17 along two **separate**
paths, because the first alone would have proven nothing:

- **Key codes** (`/dev/input`): the AIRHUG registers as an input device
  ("AIRHUG 01 (AVRCP)") and the kernel lists media keys for it - but
  pressing them delivers **nothing**, not even while audio plays. Checked
  in three runs; the first two were worthless (once the output was lost
  in a buffer, once playback failed under `sudo` because root has no
  access to the user's PipeWire session).
- **AVRCP volume** (sink volume in PipeWire): a speaker can also send its
  volume buttons over this entirely different channel, which a key reader
  never sees. Nothing arrives there either - Stephan's observation: "the
  volume is controlled only on the device and is not coupled to GNOME's
  volume."

**That rules out the obvious solution** of briefly switching to HFP by
pressing a button on the speaker, listening, and switching back.

### The decoupling applies in ONE direction only

**Correction of 2026-08-17.** This initially said DialOS could not
control the speaker at all. That was an overstatement, based on my not
separating "not coupled" by direction. Re-measured by ear:

- **Computer → device: works.** Between 10 % and 100 % the difference is
  unmistakable. A voice command "louder" is therefore feasible. **Checked
  twice**, the second time with the device explicitly at 100 % and
  alternating quiet-loud-quiet-loud - otherwise the first run could have
  suffered from the device itself being turned down.
- **Device → computer: does not work.** If someone presses plus or minus
  on the AIRHUG, the computer learns nothing about it. **Re-checked in
  three conditions on 2026-08-17**, because an observation seemed to
  contradict it (the sink suddenly stood at 70 %): button press with no
  audio, start of a playback, and button press **during** an active
  playback - the value stayed unchanged every time. The 70 % remain
  unexplained, see [../TODO.en.md](../TODO.en.md).

### How the volume is actually transmitted (measured 2026-08-17)

This matters more than it sounds, because the obvious assumption is wrong
- and it led me into a recommendation I had to retract:

| Route | What happens | Does it work? |
|---|---|---|
| sink volume (GNOME slider, `pactl`) | the value goes **to the device via AVRCP**, the signal is unchanged | yes, audibly |
| attenuation in the signal (sox, `paplay --volume`) | the signal leaves the laptop correctly attenuated | **no** - the AIRHUG undoes it |

Proven on the Bluetooth sink's monitor, i.e. on what leaves the laptop:
half amplitude in the file arrives as **0.071559** against **0.143117**,
exactly a factor of 0.5000. Sink at 100 % versus sink at 30 %, by
contrast, gives **0.143117 both times**, identical to the last digit. So
the sink volume is not computed into the signal at all but commanded to
the device. On the built-in speaker the signal attenuation is audible the
other way round (confirmed by ear).

**Two conclusions:**

- `bluez5.enable-hw-volume = false` would be a mistake, even though on
  paper it does exactly what one wants (device stays at 100 %, OS
  controls). DialOS would then attenuate on the route that does nothing
  on the AIRHUG - there would be **no** volume control left at all.
- "announcements quieter than music" is unreachable on the AIRHUG,
  because only the device volume works there and that applies to
  everything. An AVRCP command costs a measured 19-36 ms, so briefly
  lowering it during an announcement would be affordable - decision open,
  see `TODO.en.md`.

What follows in practice: DialOS can control the volume, but it **does
not know where it stands** once someone has turned the dial. If the user
has turned the AIRHUG down physically, "louder" only helps while the
software volume still has headroom - at 100 % it stays quiet, and the
cause lies outside the system. A residual risk, but not a
disqualification.

### What remains

- **Two devices:** a microphone that stays permanently in HFP with the
  user, and separately the speaker in A2DP. Solves range and quality, at
  the cost of one more device to charge and pair.
- **A different speaker** whose buttons and volume do reach the computer.
  That is a device property, not a Bluetooth limit - other speakerphones
  manage both.
- **Built-in microphone only**, with the requirement that the laptop is
  in the same room. Contradicts the normal case.

**Decided on 2026-08-17 (Stephan): the third variant for now - input is
always the built-in microphone**, output the Bluetooth speaker as long as
it actually plays, otherwise the built-in ones. External microphones will
be revisited only at the very end.

This is explicitly **not a stopgap**; it also solves two problems that
would otherwise need solving in their own right:

1. **The A2DP/HFP forced choice disappears.** As long as DialOS never
   opens a Bluetooth microphone, the device cannot drop into phone
   quality. That trap has cost the audio quality of the video recording
   and sits inside several open items - it is now not solved but
   untouched.
2. **A microphone that can be switched off is a risk to the entire audio
   output.** If echo cancellation hangs on it, its failure takes
   everything down - exactly what happened on 2026-08-17, details in
   `Debian-zu-DialOS.en.md`, step 11f. A built-in microphone cannot be
   switched off.

The price is range: voice control only at the laptop. That is precisely
why the search for an external microphone stays on the list - just not as
a precondition for everything else.

## Two devices instead of one (decision 2026-08-17)

The measurements above lead to one conclusion: a single Bluetooth device
cannot do both. Stephan's decision is therefore a **pair**:

| Job | Device | Path |
|---|---|---|
| Speech output, music, radio | AIRHUG 01, stays | Bluetooth A2DP |
| Speech input | wireless microphone with USB receiver | USB Audio Class |

**Why not a second Bluetooth device:** that would bring back the HFP trap
that cost the whole morning of 2026-08-17. A wireless microphone with a
USB receiver registers as an ordinary USB sound card instead - no
profile, no A2DP/HFP conflict, no pairing, and the speaker stays entirely
untouched.

### Requirements for the microphone

- **No battery in continuous operation**, or at least operation from a
  power supply. This is the hardest requirement and it comes from the
  target group: an empty transmitter makes the system **deaf**, and a
  blind user cannot find the cause - it lies outside the system. The same
  class of fault as the decoupled device volume.
- **USB Audio Class**, so it works on Linux without drivers.
- Range across a flat, so at least 15-20 m through walls.

### Bluetooth or USB? To be tested, not decided

**As of 2026-08-17.** USB was set first because it avoids the HFP trap.
Stephan's objection exposed a point against it - and it concerns the
hardest requirement above:

| | Bluetooth microphone | USB wireless microphone |
|---|---|---|
| **Battery level visible** | **yes**, via BlueZ - the login announcement already reads it out and could warn | **no**, the receiver is only a sound card |
| Interference with music | **risk**: a permanently open HFP link continuously consumes airtime on the same adapter the AIRHUG plays through | no shared scheduling, since it bypasses the Bluetooth stack |
| Profile conflict | affects only the microphone device itself, not the speaker | none at all |

So the difference is not "good versus bad" but **which failure one would
rather have**: a microphone that goes flat unnoticed, or radio that might
stutter while listening.

That A2DP degrades with a simultaneously open SCO link is a known problem
and depends on the adapter - **that can only be settled on the device,
not by reading up on it.**

**Approach (Stephan, 2026-08-17):** first an **inexpensive Bluetooth
microphone to try out** - pair it, run the radio, let it listen, listen
for stutter. If the test goes well it is the better solution, because the
battery level stays visible. If it goes badly, that is known for €30
instead of €150, and USB is the fallback.

**To be built regardless:** the voice service measures the level
continuously anyway. If **nothing at all** arrives for minutes even
though the source is present, it can say so ("I can't hear anything from
the microphone any more"). That does not replace a battery indicator but
catches exactly the failure that would otherwise leave the user
clueless - and it works with either design.

### The USB route is proven on this machine (2026-08-17)

The open question "does a wireless microphone with a USB receiver appear
as a sound card under Linux?" is answered - with hardware Stephan already
owned: a **TeckNet TK-HS005** headset with a 2.4 GHz USB dongle.

| | |
|---|---|
| USB ID | `10d6:dd00` |
| Manufacturer **per device** | "Generic" |
| Product per device | `TK-HS005-PHONE` |
| Brand | **TeckNet** - printed only, not in the descriptor |
| Chipset | Actions Semiconductor |

Plugged in, it registers without drivers and without pairing as a sound
card - and, decisively, with a profile carrying **output and input
simultaneously**:

```
output:analog-stereo+input:mono-fallback   (sinks: 1, sources: 1)
```

That is exactly what Bluetooth cannot do: on the AIRHUG every A2DP
profile has `sources: 0`, forcing a choice between good sound and the
microphone. On the USB device there is no such choice because none is
needed. And it consumes no airtime on the Bluetooth adapter - the
"music stutters" risk disappears entirely on the USB route.

**What the device is not suited for:** reference hardware. The
manufacturer appears nowhere in the descriptor, "Actions Semiconductor"
is only the chip supplier, and the same chip in the same housing is sold
under any number of brand names. A device that must be re-orderable for
years should be identifiable. As **proof that the route works**, it has
served its purpose.

### Checked and rejected: Godox Cube-SC Kit2 (2026-08-17)

2.4 GHz wireless microphone with USB-C receiver, around €60-80. Checked
at Stephan's suggestion.

**What spoke for it:** the receiver explicitly supports **UAC** and is
intended for PC use - the best precondition for running on Linux without
drivers. 300 m range, 48 kHz/24 bit, noise cancelling, two transmitters
in the kit, considerably cheaper than the Lark M2.

**Why it is out anyway:** the transmitters charge **exclusively via
contacts in the charging case** - no charging port of their own. That
rules out continuous operation from a power supply; after 8-10 hours the
transmitter has to go into the case, and the system is deaf for that
time. This is precisely the requirement identified above as the hardest.

On top of that: **the battery level is invisible to DialOS.** Godox shows
it in a phone app - which does not exist on Linux and which a blind user
could not operate anyway.

**What it is still good for:** as a **test device for the USB path**. For
little money it answers whether a 2.4 GHz microphone appears as a sound
card under Linux and how well recognition works with it. It only leaves
the battery question open - and the Bluetooth test answers that better.

**One thing could rescue it**, which no description covers: whether the
transmitter can be **operated inside the opened case**, i.e. permanently
docked and charging. If so, that would be the sought-after mains
solution. A question for the dealer, or a case for the return period.

*(Runtime figures contradict each other between retailers: sometimes 8,
sometimes 10 hours per transmitter; "30 hours" always refers to the
charging case. That changes nothing essential.)*

### Candidates for the USB fallback

- **[Hollyland Lark M2](https://www.hollyland.com/product/lark-m2)**
  (~€120-150): USB-C receiver with explicit UAC support, 10 h per
  transmitter, charging case for 30 h total, two transmitters in the set.
  **To clarify before buying:** whether the transmitter can run
  permanently from a power supply - that determines whether the battery
  requirement is met. Linux is nowhere explicitly named; UAC devices
  usually work there without drivers, but "usually" is not evidence.
- **[Cubilux WM-C1BK](https://www.cubilux.com/products/usb-c-wireless-lavalier-microphone)**:
  names Linux explicitly and is considerably cheaper - but no reliable
  figures on range and runtime were found.

**Considered and rejected:** a USB conference microphone on an active USB
extension. Technically the cleanest solution - no battery, always on,
nothing to charge. But a cable across the living room is a **trip hazard**
for a blind user. Usable for a test device, not for a customer device.

**Check after purchase**, takes an hour: plug it in, `pactl list sources`
- if the device appears, half the battle is won. Then range within the
flat and recognition quality against the built-in microphone.

### Telephony and video calls: which device?

**Not to be decided yet** - telephony is not implemented (see
[telefonie.en.md](telefonie.en.md)). Recorded as a decision aid so the
reasoning is not lost:

The obvious route would be to switch to **HFP** for a call: the AIRHUG
becomes a speakerphone, microphone and playback from one device. Phone
quality is no loss on a phone call.

The better route is probably **not to switch at all**: input the USB
microphone, output the AIRHUG in A2DP. The call then runs in **both**
directions at full quality rather than phone quality. Two further points
favour it: the profile-switching problem disappears entirely (it got
stuck three times on 2026-08-17), and echo cancellation is already set
up.

**The caveat:** with speaker and microphone separated, the other party
hears themselves if echo cancellation does not hold - and during a call
it is more demanding than in our case so far. We currently only subtract
our *own* announcement; in a call, audio runs in both directions
simultaneously. The measured 32 dB are a good sign but no proof for the
call case.

## Current test hardware

- **Laptop**: Lenovo ThinkPad T490 – no WWAN/LTE module fitted.
- **Audio**: AIRHUG 01 (see above) – reference device since 2026-08-16,
  **output only since 2026-08-17**.
- **Microphone**: the T490's built-in one, via the echo source
  `dialos_mikrofon_ohne_echo` - this is the input for all voice services.
- **USB desk microphone TONOR TC30** - **test hardware, not a standard.**
  Measured on the test bench since 2026-09-15 (see
  [pruefstand.en.md](pruefstand.en.md)): for letter dictation with the TV
  running it keeps Parakeet at **4.2 %** word errors, while the built-in
  microphone drops to **9.9 %**; without interference both are on a par.
  Commands are hardly disturbed by the TV with either. Against it so far:
  no echo cancellation on this path (Anna's announcements reached the
  command service through it) and clipping at 100 % gain. It is a measuring tool for the question of an external
  microphone, not a decision for one.
- **Input devices**: Logitech Pebble M350s (mouse) and Pebble K380s
  (keyboard), both over Bluetooth. Their battery level is read out by the
  startup announcement – but only for administrator accounts; `nutzer`
  deliberately only hears about the laptop and the speaker.
- **USB stick**: as the security stick (recommended size 64 GB, see
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)) - so far
  just some stick that was around, no specific reference product.
- **Android phone**: for testing phone tethering (USB tethering +
  GSConnect).

Since the test T490 has no WWAN module, initial practical testing runs
through the phone-tethering path (see [telefonie.en.md](telefonie.en.md)).
The built-in SIM variant will need to be tested on suitable additional
hardware.

## WWAN module selection (for the SIM variant)

Not every LTE modem supports voice calls (Voice/VoLTE via ModemManager) —
many USB/M.2 modules are data-only. For telephony over the built-in SIM, a
voice-capable modem must be specifically selected (e.g. Quectel EM7565,
Sierra Wireless modules).

## Open questions

- ~~Reference audio device~~ – **decided 2026-08-16: AIRHUG 01** (see
  above).
- Reference laptop model not yet finalized. **Requirements recorded since
  2026-09-17** (32 GB minimum, Intel and AMD variant, see "Computer
  specification for DialOS") - still open: trying a candidate under Debian 13.
- Reference security stick (brand/model, USB-A vs. USB-C) not yet
  finalized - the recommended size (64 GB) and filesystem split
  (`DIALOS-KEY`/`DIALOS-DATA`) are already decided (see
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)), but no
  concrete product has been chosen.
- No WWAN module available for practical SIM testing — needs to be
  procured.
