[Deutsch](telefonie.md) | [English](telefonie.en.md)

# Telephony & video calls

## Goal

Telephony (landline replacement + mobile) and video calls should be fully
usable via voice control.

**Status 2026-08-16: none of this is implemented.** This document
describes the target architecture throughout, not the current state.
Neither ModemManager nor GNOME Calls is in the package list, and the test
device (ThinkPad T490) has no WWAN module fitted - practical SIM tests
are therefore not possible at all so far (see
[hardware.en.md](hardware.en.md)).

## Shipping goal: built-in SIM

The actual default configuration at delivery is a laptop with a
**built-in, activated SIM card** (WWAN module with voice support, see
[hardware.en.md](hardware.en.md)). A single SIM handles both landline and
mobile telephony in a unified way, instead of maintaining separate
solutions such as a Fritzbox SIP trunk and phone pairing — that was the
original idea but was dropped in favor of the SIM solution, because it
doesn't depend on the user's home network/router and therefore also works
while travelling. Existing phone numbers of the user can be forwarded to
the new SIM number if needed, so they remain reachable under their usual
number.

Software: ModemManager + GNOME Calls as the softphone interface.

## Alternative: phone tethering

The system must also work without a built-in SIM — the user can
alternatively connect their own phone. This is the flexible
alternative/fallback, **not** the default case.

- **Connection method**: USB cable as the primary method (more reliable
  than Bluetooth, charges the phone at the same time, fits the "plug in
  once and forget" principle). Bluetooth only as a fallback if a cable is
  impractical.
- **Internet**: USB tethering, works regardless of phone platform.
- **Telephony**: on Android, additionally possible via GSConnect/KDE
  Connect (answering/placing calls from the laptop). Not possible on
  iPhone due to Apple restrictions — only internet tethering there.
- **Fallback logic (variant B, per capability)**: the phone handles
  whatever it can (tethering always, telephony only on Android). Missing
  capabilities (e.g. telephony on iPhone) automatically fall back to the
  built-in SIM, if present. No manual configuration needed — fits the
  "equally simple for 18 and 80 year olds" principle.

### Mandatory constraint

The user never operates the connected phone themselves — many older
users struggle with operating a phone. The phone is connected/paired once
during setup and then stays untouched afterwards (e.g. in a drawer). Any
interaction (calling, answering, hanging up) happens exclusively via
voice control on the laptop.

## Checked: telephony via an external modem (dongle)

**Stephan's question of 2026-11-15**, raised while configuring the first
reference device: can telephony be decoupled from the built-in SIM and
handled by an external device? That would be independent of the laptop
model, replaceable if it fails, and would take pressure off the purchase
decision.

**Technically yes, but only with certain modules.** A modem needs to do
two things, and they are not the same:

1. **Voice calls** – many LTE modules are data-only.
2. **Audio over USB** – the call also has to reach the computer. Quite a
   few voice-capable modules only expose audio on PCM pins, which a USB
   enclosure leaves unconnected.

This is proven to work with the **Quectel EC25-E**: it registers as a USB
audio device (USB Audio Class), call control runs over AT commands, and
ModemManager with GNOME Calls drives it – exactly the architecture
described above.

**Three limitations remain:**

- **8 kHz, hard-wired.** The EC25's USB audio interface is fixed at 8 kHz
  in firmware – landline telephone quality. Fine for telephony; HD voice
  is ruled out.
- **There is no ready-made dongle.** The EC25 comes as an M.2 or
  Mini-PCIe module; USB requires an enclosure, and those are hobbyist
  products. On a device shipped ready to use, that is one more part that
  can come loose or get lost.
- **The antenna is tiny.** A built-in WWAN module uses the antennas in
  the display frame and has noticeably better reception than a dongle in
  a USB port.

## A fourth option: SIP over the internet

While checking the dongle question, it became clear that one option had
been missing. What was rejected above is the **Fritzbox SIP trunk**, and
rightly so – it depends on the user's router. A SIP account with a
provider depends only on an internet connection, which the device has
anyway.

The advantages fit the project:

- **No voice-capable modem needed.** A data-only module is enough –
  including the one Lenovo ships by default in the L14 (see
  [hardware.en.md](hardware.en.md)).
- **A landline number is possible**, including number porting. For
  someone who has had the same number for decades, that is worth more
  than any technical elegance.
- **Linphone can be driven from outside** – the selection criterion from
  [anwendungen.en.md](anwendungen.en.md).
- No additional hardware, no module question when buying the device.

## To be decided before the technology: emergency calls

**This question determines whether mobile network access is mandatory or
merely convenient** – and for this target group it is not a footnote.

Over a mobile network, 112 can be reached without credit, without a
contract and on any available network; the location is transmitted along
with the call. Over VoIP both are harder: location handling works
differently, and if the internet is down, nothing works at all.

People using this device cannot fall back on a mobile phone in an
emergency, and usually cannot call out of a window either. As long as
this question is open, the built-in SIM remains the shipping goal – SIP
is then an addition for everyday use, not a replacement.

**Recommendation for the device purchase (2026-11-15):** separate the
telephony decision from the purchase. A data-only module is enough for
now, the M.2 slot stays available, and a voice-capable module can be
fitted later. SIP and phone tethering can both be tried out in the
meantime without new hardware.

## Video calls

Jitsi Meet in the browser as the simplest, account-free solution — open
source, launchable directly with a voice command via a link.

## Messenger (text messages, in addition to real telephony)

Only for writing/receiving messages - calls always go through SIM/phone
as above, never through the messenger.

**Priority: WhatsApp**, despite the project's otherwise strict privacy
stance - the deciding factor is reach: the user's family/friends are
far more likely to already have WhatsApp than Signal, and reaching
existing contacts matters more here than for the project's other
(purely internal) system decisions. There is no official WhatsApp
Linux client; implemented via WhatsApp Web in the browser or an
unofficial wrapper.

**Signal** (official Linux app, voice/video calls, real encryption)
remains available as a more privacy-friendly option, but not
prioritized.
