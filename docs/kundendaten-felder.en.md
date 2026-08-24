[Deutsch](kundendaten-felder.md) | [English](kundendaten-felder.en.md) | [Changelog](../README.en.md#changelog)

# Customer data: which fields DialOS needs

Stephan's specification of 2026-08-24, prompted by his question about "wo wir
zentral alle wichtigen Daten des Kunden einmalig ablegen und die Mail, der
Brief und das Diktat usw. greifen auf diese Daten immer zu" - where to keep all
important customer data once, centrally, so that mail, letters and dictation
always read from it.

**This file holds the FIELDS, not the values.** That is not tidiness: the
repository is **public** (checked anonymously on 2026-08-24, `private: False`).
Writing a postal address or phone number in here means publishing it. The same
split as with `Wordpressinstallation/.env.example` - the template into the repo,
the values onto the device only.

## The fields

Drawn up by Stephan using his own person as the example. The "today" column says
whether DialOS already knows the field somewhere.

| Field | today | who needs it |
|---|---|---|
| `anrede` (form of address) | no | letter, mail |
| `vorname` (given name) | partly | greeting at login, letterhead |
| `name` (surname) | partly | letterhead, mail signature |
| `name_gesprochen` (spoken form) | **yes** | speech output - see below |
| `strasse` (street) | no | letterhead |
| `hausnummer` (house number) | no | letterhead |
| `postleitzahl` (postcode) | no | letterhead |
| `wohnort` (town) | no | letterhead, weather fallback |
| `bundesland` (region) | no | letterhead for official post |
| `land` (country) | no | letterhead for foreign post |
| `laenderkennzeichen` (country code) | no | dialling code, letterhead |
| `festnetz` (landline) | no | letter ("reachable by phone"), telephony |
| `handy_privat` (mobile, private) | no | ditto |
| `handy_geschaeftlich` (mobile, work) | no | ditto |
| `mailadresse` | no | mail signature, sender |

"Partly" means: `nutzer-name.txt` holds a name today, but not split into given
name and surname. The letterhead therefore prints only the one word it finds.

### A field missing from Stephan's list that is needed

**`name_gesprochen`** - how the name is PRONOUNCED, not how it is written. It
already exists, and for good reason: Piper stresses "Rösner" on the "e" while
the stress belongs on the "ö". On 2026-08-22 Stephan chose "Steffan" from
several spellings. Today `nutzer-name.txt` holds this as `Stephan | Steffan` -
written, spoken.

Without this field the device mispronounces the user's name in every
announcement. Whoever merges the files must not lose it.

### Fields that deliberately do NOT belong here

- **`assistent-name.txt`** (Michael/Anna) is a system setting, not customer
  data. It changes with the voice, not with the person.
- **`fusszeile.txt`** is the DialOS footer sentence and identical on every
  device.
- **The mailbox credentials** stay separate (today a file in `/home/nutzer`,
  mode 0600). A password does not belong in the same file as a postal address:
  a helper reads the one out loud while setting the device up, and must never
  see the other.

That line has to be drawn before anything is built. Otherwise everything ends up
in one file and nobody knows what to delete when the device changes hands.

## The template

One field per line, `key = value`, UTF-8. Empty fields stay empty and are
skipped - do not fill them with placeholders: a letterhead reading "Sample
Street" would be worse than one without a street, because a blind user cannot
see the gap.

```ini
# Customer data. NOT into the repo - that is public.
# Empty fields stay empty and are skipped.

anrede              =
vorname             =
name                =
name_gesprochen     =

strasse             =
hausnummer          =
postleitzahl        =
wohnort             =
bundesland          =
land                =
laenderkennzeichen  =

festnetz            =
handy_privat        =
handy_geschaeftlich =

mailadresse         =
```

## What is not decided yet

**Where the file goes.** That is the open and awkward question, set out at
length in [TODO.en.md](../TODO.en.md). In short: today the user data sits in
`/usr/local/share/dialos/` - on the **unencrypted** root partition, mode 0644,
while `/home/nutzer` is LUKS-encrypted. Measured on 2026-08-24:

    /usr/local/share/dialos/nutzer-name.txt  →  /dev/nvme0n1p1  ext4  0644
    /home/nutzer                             →  nvme0n1p4       LUKS

For a name that is already questionable; for an address and phone number it
would contradict the entire encryption approach. But the obvious location
`/home/nutzer/.config/dialos/` has a catch: `dialos-stick-gate` only opens that
partition **after** boot, and the startup announcement needs the name early.
That order must be checked before anything moves.

**Hence only the structure is here.** Filling in values is worth doing once it
is clear where they belong - otherwise they would be entered twice, and the
first copy would be left behind.
