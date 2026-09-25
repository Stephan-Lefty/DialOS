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
source. For the **Debian packages** DialOS satisfies this by installing
them **unmodified** from Debian's own repositories: the source is publicly
available from Debian (`deb-src` sources, https://sources.debian.org). If a
package is **modified**, the modified source has to be provided directly -
one of the reasons DialOS places its own scripts alongside rather than
patching other people's packages.

**Corrected on 2026-09-25:** until then the paragraph above said DialOS
installs "packages unmodified from Debian's own repositories" - as if that
applied to everything. It only applies to the Debian packages. Part of the
system reaches the device bypassing Debian, from GitHub, Hugging Face,
languagetool.org, PyPI or Anthropic's own package repository; for that part
the evidence via `/usr/share/doc/` and sources.debian.org does **not**
apply. It is therefore listed item by item in the next section.

**Trademarks.** "Debian" is a trademark of Software in the Public
Interest, "GNOME" a trademark of the GNOME Foundation. Saying "based on
Debian 13" is descriptive use and explicitly permitted. What is not
permitted is naming or presenting DialOS as though it were an official
Debian or GNOME product.

**Thunderbird** and **Firefox** are likewise Mozilla trademarks. DialOS
does not modify these programs, it only configures them (the footer in
every mail, for instance) - which does not touch trademark law.

## What does not come from Debian

Checked on 2026-09-25, looked up on the freshly built development device
(the programs' licence files, package metadata under
`/usr/local/lib/python3.13/dist-packages/`, `/usr/share/doc/claude-desktop/copyright`).
The speech models and voices are in the section below.

| Component | Origin | Use | Licence |
|---|---|---|---|
| RustDesk 1.4.9 | `.deb` from GitHub (rustdesk.com) | remote support, service off, deliberately deferred | AGPL-3.0 |
| LanguageTool 6.6 | zip archive from languagetool.org, under `/opt/languagetool` | writing aid in dictation | LGPL-2.1 (per `COPYING.txt`); the bundled libraries have licences of their own (`third-party-licenses/`) - **to be checked in detail** |
| Piper (program) | release archive from GitHub (rhasspy/piper), under `/usr/local/share/dialos-piper` | speech output | MIT; the archive bundles **espeak-ng** (GPL-3.0) and ONNX Runtime (MIT) - whether this creates a source obligation of its own for DialOS is **to be checked** |
| vosk 0.3.45 | pip (PyPI) | command recognition | Apache-2.0 |
| hassil 3.11.0 | pip | builds the command grammar | Apache-2.0 |
| sherpa-onnx 1.13.8 (+ `sherpa-onnx-core`) | pip | Parakeet in dictation | Apache-2.0 |
| dependencies of the pip packages | pip | - | unicode-rbnf MIT, PyYAML MIT, srt MIT, tqdm MPL-2.0 and MIT, websockets BSD-3-Clause, cffi MIT-0, pycparser BSD-3-Clause |
| DialOS bridge (MailExtension `bruecke@dialos.org`) | built from this repository, placed in every Thunderbird profile via `policies.json` | drafts and sending through Thunderbird | part of DialOS: GPL-3.0 |
| Claude desktop app | Anthropic's own apt repository | setup and development, so far only on the development device | **proprietary** (Anthropic PBC); includes Electron (MIT) |

**The Claude app is an open question, not a decision.** It is the only
non-free component on the device and so far serves the build only: the
installation guide sets it up in part 2 because the rest runs with its
help. **Whether it may stay on a customer device or is removed before
delivery is open.** To note for the decision: it needs an Anthropic
account, it cannot be passed on freely like the rest of the software, and
whether passing it on with a sold device is permitted at all depends on
Anthropic's terms of use - **to be checked**. Until this is decided: yes on
the development device, not to be regarded as settled on customer devices.

**Why pip packages are listed here although the package list otherwise does
not belong in the repository** (see below): they do **not** travel with a
licence text under `/usr/share/doc/` and are not covered by any
`apt upgrade`. For them the evidence obligation is therefore not met
automatically. Switching eight of the packages to Debian packages is in
`TODO.en.md` - after that this table shrinks.

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
| [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 1.13.8 | text recognition in dictation (since 2026-09-16) | Apache 2.0; includes ONNX Runtime (MIT) |
| [Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3), int8 version by sherpa-onnx | text for letters and notes | **CC-BY-4.0** |

**CC0** means public domain - no conditions, commercial use included.
**Apache 2.0** permits commercial use and adds an explicit patent
licence. Every model used here may therefore ship on devices that are
sold.

**CC-BY-4.0** (Parakeet) permits commercial use and modification but requires
**attribution**: author, licence and a note on changes. For DialOS:
*"Parakeet TDT 0.6B v3" by NVIDIA, licensed under CC-BY-4.0
(https://creativecommons.org/licenses/by/4.0/); converted to ONNX and quantised
to int8 by the sherpa-onnx project (k2-fsa), used unchanged in DialOS.* This
notice also belongs in the licence overview on the device once it exists
(TODO.en.md).

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

## Logo, icons and wallpapers

The image files in [assets/](../assets/) - logo, icon, app icon,
wallpapers, splash screen - were **created by Stephan Rösner together
with ChatGPT (OpenAI)**, over several rounds from his own prompts and
with his own selection. No third-party source, no stock material, no
third-party rights involved.

Under OpenAI's terms of use the rights to generated images pass to the
user, so commercial use is covered.

**What does not follow from that:** whether copyright arises at all in a
substantially machine-generated image is at least doubtful. German law
requires a "personal intellectual creation" (§ 2 (2) UrhG), and the US
Copyright Office explicitly refuses protection without human authorship.
It may well be that these images are in the public domain and anyone may
use them.

**For the trademark reservation above this is irrelevant** - and that is
the decisive point. Protection of the name and visual identity does not
come from copyright but from **trademark law**, which requires no
creative achievement, only use in trade. "DialOS" as the mark of a
product being sold is protected accordingly, regardless of how the logo
came about.

To put that on a firm footing, register the word/figurative mark with the
German Patent and Trade Mark Office. Until then the reservation carries
as far as use and recognition reach - which is enough for now.

## For resellers and customers

Passing on a DialOS device means passing on GPL software and taking on
its obligations. In practice:

1. Leave `/usr/share/doc/` on the device - all licence texts are there.
2. Be able to name the source on request: for Debian packages
   https://sources.debian.org, for DialOS itself
   https://github.com/Stephan-Lefty/DialOS.
3. If you change DialOS yourself, publish your source (GPL-3.0) and use a
   different name (see above).

## No package list in the repository - and why not

The obvious idea: list every additionally installed Debian package with
its licence here. **That is neither required nor useful.**

Not required, because the GPL demands two things - the licence text with
the program and the source on request - but no inventory. Both are
satisfied: the licence text of every package **travels on the device**,
under `/usr/share/doc/PACKAGE/copyright`, and the source is at Debian.

Not useful, because a hand-maintained list goes stale immediately - every
`apt upgrade` shifts versions, packages come and go. Such a list would
soon assert something true of no device any more. That is worse than no
list, because somebody will believe it.

Which packages DialOS additionally installs is already recorded where it
belongs: in [Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), where it is
needed for rebuilding and therefore kept current.

If a customer or reseller does ask for a listing, it is **generated on
the device** rather than copied from the repository - then it is actually
correct:

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Homepage}\n' | sort > packages.txt
```

## Open

- **Claude desktop app on customer devices** (noted here since 2026-09-25):
  does it stay or is it removed before delivery? See "What does not come
  from Debian". Not decided.
- **Licence notice for Parakeet on the device** (CC-BY-4.0 requires
  attribution, wording above) - open item in `TODO.md`, belongs in a licence
  overview that DialOS can show or read out on the device.
- **To be checked:** the libraries in LanguageTool's `third-party-licenses/`,
  and whether the espeak-ng (GPL-3.0) bundled with Piper requires source to
  be provided separately.
- Registration of the "DialOS" word/figurative mark, should the trademark
  reservation need to be enforceable (see above). Until then it carries
  only as far as use and recognition reach.
