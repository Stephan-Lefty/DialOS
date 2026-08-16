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

**Still to clarify:** whether the device announces its own firmware
prompts ("connected", low battery) in German. Standard Bluetooth profiles
offer no remote control over this, it is purely device-dependent – but
not a side issue on a system for blind users, since they necessarily hear
those prompts.

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

- Reference laptop model not yet finalized.
- Reference security stick (brand/model, USB-A vs. USB-C) not yet
  finalized - the recommended size (64 GB) and filesystem split
  (`DIALOS-KEY`/`DIALOS-DATA`) are already decided (see
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)), but no
  concrete product has been chosen.
- No WWAN module available for practical SIM testing — needs to be
  procured.
