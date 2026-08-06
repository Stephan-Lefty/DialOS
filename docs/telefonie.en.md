[Deutsch](telefonie.md) | [English](telefonie.en.md)

# Telephony & video calls

## Goal

Telephony (landline replacement + mobile) and video calls should be fully
usable via voice control.

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

## Video calls

Jitsi Meet in the browser as the simplest, account-free solution — open
source, launchable directly with a voice command via a link.

## Messenger (optional)

There is no official WhatsApp Linux client, only WhatsApp Web in the
browser or unofficial wrappers. Since this is about reaching existing
contacts, WhatsApp remains a sensible option despite the project's
otherwise strict privacy stance; **Signal** (official Linux app,
voice/video calls) is a more privacy-friendly alternative in parallel.
Prioritization is still open.
