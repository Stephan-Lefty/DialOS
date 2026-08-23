[Deutsch](lizenzen.md) | [English](lizenzen.en.md) | [Changelog](../README.en.md#changelog)

# Licences and provenance

Whoever passes on an operating system passes on a thousand other
people's programs. This document states what comes from where, under
which licence it stands, and what obligations follow - for customers,
for resellers, and for anyone who wants to develop DialOS further.

## The principle

**The DialOS licence covers only what is in this repository** - the
scripts, the configuration files, the documentation. Debian, GNOME and
every bundled program keep their own licences; DialOS does not change
that and could not.

Legally, a distribution is a **collection**. The GPL calls this "mere
aggregation" (GPLv3 § 5, GPLv2 § 2 final paragraph) and states
explicitly that programs merely sharing a storage medium do not impose
their licence on one another.

## DialOS itself

**GNU General Public License, version 3** (see [LICENSE](../LICENSE)).

This is a deliberate choice for copyleft: anyone who **distributes** a
modified version of DialOS must publish its source under GPL-3.0 as
well. DialOS is built for people who depend on assistance - what grows
out of it should remain available to them, not disappear into a closed
product.

Copyleft applies to **distribution**, not to use: anyone who adapts
DialOS for themselves and does not hand it on need publish nothing.

### Excluded: name and appearance

**The name and the visual identity are not covered by the GPL**: the
name "DialOS", the logo, the app icon and the wallpapers in
[assets/](../assets/).

This is not a contradiction of a free licence but common practice among
distributions (Debian, Firefox and Ubuntu all do the same). The reason is
practical: anyone may rebuild DialOS - but the result should not still be
called "DialOS". Otherwise other people's changes carry Stephan's name,
and users take something for DialOS that is not. So please give a derived
build its own name and its own logo.

## Debian and GNOME

DialOS builds on **Debian 13** with **GNOME 48**. Both are compilations
spanning many licences - GPL-2, GPL-3, LGPL, MIT, BSD, Apache and more.

**Proof on the device:** Debian stores the licence of every installed
package under `/usr/share/doc/PACKAGE/copyright`. That directory ships
the evidence with the system and **must not be removed** when cleaning
up.

**Source code obligation.** Anyone distributing GPL software - including
on a device that has been sold - owes the recipient the corresponding
source. DialOS satisfies this by installing packages **unmodified** from
Debian's own repositories: the source is publicly available from Debian
(`deb-src` sources, https://sources.debian.org). If a package is
**modified**, the modified source has to be provided directly - one of
the reasons DialOS places its own scripts alongside rather than patching
other people's packages.

**Trademarks.** "Debian" is a trademark of Software in the Public
Interest, "GNOME" a trademark of the GNOME Foundation. Saying "based on
Debian 13" is descriptive use and explicitly permitted. What is not
permitted is naming or presenting DialOS as though it were an official
Debian or GNOME product.

**Thunderbird** and **Firefox** are likewise Mozilla trademarks. DialOS
does not modify these programs, it only configures them (the footer in
every mail, for instance) - which does not touch trademark law.

## Speech output and speech recognition

The most delicate part, because models and datasets are shipped here and
**not** all of them are freely usable. Checked on 2026-08-23.

| Component | Use in DialOS | Licence |
|---|---|---|
| [Piper](https://github.com/rhasspy/piper) | speech output | MIT |
| Voice `de_DE-kerstin-low` ("Anna") | shipping voice | dataset **CC0**, model collection MIT |
| Voice `de_DE-thorsten-high` ("Michael") | second voice | dataset **CC0**, model collection MIT |
| [Vosk](https://alphacephei.com/vosk/) | speech recognition | Apache 2.0 |
| `vosk-model-small-de-0.15` | command recognition | Apache 2.0 |
| `vosk-model-de-0.21` | dictation | Apache 2.0 |
| `vosk-model-de-tuda-0.6-900k` | dictation (alternative) | Apache 2.0 |

**CC0** means public domain - no conditions, commercial use included.
**Apache 2.0** permits commercial use and adds an explicit patent
licence. Every model used here may therefore ship on devices that are
sold.

These statements come from the sources themselves: the `MODEL_CARD`
files next to the Piper voices' `.onnx` files, and the model overview at
https://alphacephei.com/vosk/models.

### Deliberately not used

**Wake word (openWakeWord, ready-made models): CC BY-NC-SA** -
non-commercial. DialOS ships on devices that are sold, which rules it
out. A self-trained model would be possible (the code and Google's
embedding are Apache 2.0), the ready-made model set is not. This is why
switching on voice control requires two spoken words rather than a wake
word, for the time being.

That is the reason this page exists: a clause like that only surfaces
when somebody reads up.

## Announcements and speech samples

The files under [docs/sprachbeispiele/](sprachbeispiele/) were generated
with Piper from the voices named above. As both datasets are CC0, the
generated audio carries no obligations from the voice. The **texts** of
the announcements originate in DialOS and are under GPL-3.0 like the rest
of this repository.

## For resellers and customers

Passing on a DialOS device means passing on GPL software and taking on
its obligations. In practice:

1. Leave `/usr/share/doc/` on the device - all licence texts are there.
2. Be able to name the source on request: for Debian packages
   https://sources.debian.org, for DialOS itself
   https://github.com/Stephan-Lefty/DialOS.
3. If you change DialOS yourself, publish your source (GPL-3.0) and use a
   different name (see above).

## Open

- A complete list of the Debian packages DialOS installs on top, with
  their respective licences. Traceable on the device via
  `/usr/share/doc/`, not yet compiled in the repository.
- Record the provenance of the wallpapers and the logo in writing (own
  work or source), so that the trademark reservation above is documented
  as well.
