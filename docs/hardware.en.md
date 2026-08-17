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
  on the AIRHUG, the computer learns nothing about it.

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

**Open - Stephan's decision** (see [../TODO.en.md](../TODO.en.md)). Until
then the built-in microphone stays, because it at least does not damage
output quality.

## Current test hardware

- **Laptop**: Lenovo ThinkPad T490 – no WWAN/LTE module fitted.
- **Audio**: AIRHUG 01 (see above) – reference device since 2026-08-16.
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
- Reference laptop model not yet finalized.
- Reference security stick (brand/model, USB-A vs. USB-C) not yet
  finalized - the recommended size (64 GB) and filesystem split
  (`DIALOS-KEY`/`DIALOS-DATA`) are already decided (see
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)), but no
  concrete product has been chosen.
- No WWAN module available for practical SIM testing — needs to be
  procured.
