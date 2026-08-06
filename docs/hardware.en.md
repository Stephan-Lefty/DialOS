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

## Current test hardware

- **Laptop**: Lenovo ThinkPad T490 – no WWAN/LTE module installed.
- **USB stick**: for disk encryption (see
  [sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)).
- **Android phone**: for testing the phone-tethering path (USB tethering
  + GSConnect).

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
- No WWAN module available for practical SIM testing — needs to be
  procured.
