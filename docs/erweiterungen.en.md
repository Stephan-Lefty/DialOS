[Deutsch](erweiterungen.md) | [English](erweiterungen.en.md)

# Extensions

How a program joins DialOS without anything in the core having to change.

> **Status on 2026-09-17: the interface is a DRAFT, not a line of its code
> is built.** This file describes how it is meant to become, and is
> deliberately kept separate from [sprachbefehle.en.md](sprachbefehle.en.md)
> and [anwendungen.en.md](anwendungen.en.md), which describe what exists.
> The separation is the same one as there: mixed together, the planned
> would look like the existing.
>
> **The only exception is the icon** - that one is built and sits in the
> repo as twelve files, see "The icon" further down. It is stated here
> explicitly so that the exception does not soften the rule.

Decided with Stephan on 2026-09-17: DialOS gets an extension interface,
and the first extension will be **DialOS-Suche** (finding and reading out
letters, documents, notes and mail by voice). The order is deliberate -
the interface first, and the first extension proves along the way that it
holds.

## The problem it solves

Today every voice command sits in three places in
`dialos-sprachbefehl-desktop.py`: as a sentence in `GRAMMATIK_AN`, as an
entry in a dict, and as a branch in the loop. For dictation, printing and
information queries that is the same pattern three times over with
different names.

A fourth program following the same procedure would be the fourth copy,
and each further one makes the core longer without making it better.
Above all though: **there is no way to add a program without touching the
core.** Anyone wanting to contribute a tool would have to change a file
that the switching on and off of voice control also hangs on.

## The core decision: switch over, do not add

**This is the point at which a naive plugin mechanism would fail**, and it
is not a matter of design taste but follows from a measured property of
Vosk.

The restricted grammar is a list of SENTENCES, but Vosk builds a WORD
NETWORK out of it and is allowed to combine words from different
sentences. On 2026-08-22, with **27 sentences**, there were already **382
permitted word combinations that are not a command** in the log (see
`TODO.md`, the item „Erlaubte Wortkombinationen ohne Befehl fallen
LAUTLOS durch" - permitted word combinations that are not a command fall
through SILENTLY). For a blind user that is the worst possible outcome:
they spoke, the device listened, and nothing tells them that nothing
happened.

**The 382 are not today's state, and that makes the argument stronger,
not weaker.** Two things have changed since: the grammar has grown to
**47 command sentences**, and since 2026-08-24 DialOS no longer stays
silent when nothing matched - it says so, and on a strong match it
suggests the right sentence. The item is thus **defused, but not done**:
the two-thirds threshold is never reached on short commands, and the
conversation detection is still waiting for its trial on the device.

What matters is the direction. The number of combinations does **not**
grow linearly with the number of sentences, and the number of sentences
has nearly doubled in four weeks, from 27 to 47 - without a single
extension being involved. If every extension poured its twenty sentences
into the core grammar, the problem with six extensions would not be six
times as large but a multiple of that. The interface would then be the
mechanism that tears open a bug that has only just been defused.

**Therefore the core grammar grows by exactly one sentence per extension:
its start sentence.** Everything beyond that the extension recognizes
itself, with its own small grammar, for as long as it runs - and the core
keeps out of it for that time.

This is not a new procedure but what `dialos-diktat.py` already does
today: its own second recognizer, its own grammar, a marker file, and the
command service stays silent meanwhile. The interface turns that into a
general mechanism instead of a special case.

| | Core grammar | The extension's grammar |
|---|---|---|
| Who builds it | `dialos-sprachbefehl-desktop.py` from all manifests | the extension itself |
| What is in it | the `startsaetze` of each extension | the `eigene_grammatik` |
| When active | always, while voice control is on | only while the extension runs |
| Grows with the number of extensions | yes, by one sentence each | no |

## The manifest

One file per extension under
`/usr/local/share/dialos/erweiterungen/<name>.json`:

```json
{
  "name": "DialOS-Suche",
  "version": "0.1.0",
  "braucht_dialos": "0.6.0",
  "startsaetze": ["unterlagen durchsuchen", "briefe durchsuchen"],
  "befehl": "/usr/local/bin/dialos-suche.py",
  "eigene_grammatik": ["vorlesen", "weiter", "zurueck", "stopp", "abbrechen"],
  "braucht_mikrofon": true,
  "beschreibung": "Briefe, Dokumente, Notizen und Mails im Archiv finden"
}
```

| Field | What for |
|---|---|
| `name` | Display name. Not the voice command - see below. |
| `version` | Version of the extension, for the changelog. |
| `braucht_dialos` | Minimum version of the core. Without it an extension breaks silently when the core changes. |
| `startsaetze` | Go into the core grammar. Each one must obey the rules from [sprachbefehle.en.md](sprachbefehle.en.md). |
| `befehl` | What gets started. Absolute path. |
| `eigene_grammatik` | Does NOT go into the core grammar. Only there so it can be checked along at install time. |
| `braucht_mikrofon` | Whether the extension takes over the microphone. Decides the handover. |
| `beschreibung` | One sentence that can also be read out. |

JSON and not TOML or YAML, because `GRAMMATIK_AN` is already a JSON string
today and `json` is part of the standard library - one dependency less on
a device that is meant to run offline.

## Four rules the interface must enforce

Each one comes from a bug that has already occurred in this project. That
is the same origin as the rules in
[sprachbefehle.en.md](sprachbefehle.en.md), and for the same reason they
are not negotiable.

### 1. The vocabulary is checked at install time, not at runtime

A word the small Vosk model does not know is thrown **silently** out of
the grammar by Vosk. The command then does not exist, and nothing says so
anywhere. On 2026-08-18 this came up with **„löschen"** (delete), which is
missing from the vocabulary; also not included are „zurücksetzen",
„aufräumen" and „spät".

`dialos-erweiterung.py einbauen` therefore checks **every word from both
lists** against the model and **refuses** the installation. Not warn -
refuse. Nobody reads an install-time warning again, and the bug only shows
itself once the user is alone with the device.

Vosk reports the case itself while building the grammar (`Ignoring word
missing in vocabulary`); the check needs no microphone and no voice.

### 2. Collisions between extensions are checked in the same place

Two extensions whose start sentences share words produce exactly the
silent phantom combinations described above. The second check is therefore
the full counter-test: Piper speaks every new start sentence, Vosk listens
with the **complete** grammar of all extensions already installed. Only
then does it show whether a sentence is confused with an existing one.

The tool for that already exists: `scripts/dialos-grammatik-pruefen.py`.

### 3. The microphone always belongs to exactly one party

The same rule as "only one player may run at a time"
([anwendungen.en.md](anwendungen.en.md)), for the same reason: a command
heard by two recognizers is no longer unambiguous - and the user cannot
look to see who is currently listening.

The handover runs over a marker file, as with dictation. **A watchdog is
mandatory with it:** a crashed extension must not keep the microphone
forever. The user would otherwise speak against a deaf device with no way
back - and switching voice control off would itself no longer be audible.

### 4. Speaking happens exclusively through `dialos-say.py`

An extension **never** calls Piper or speech-dispatcher directly.
Otherwise DialOS would have a second voice source, and Stephan's choice
between Anna and Michael would have no effect in the second tool.

Through `dialos-say.py` everything comes along that would otherwise be got
wrong anew in every extension:

- **Voice and speed** from `DefaultVoice` in `piper-generic.conf` - the
  same source that `dialos-stimme.py setzen` writes
- **The sample rate** from the voice's `.json` instead of from a copied
  number. A copied number once made all the audio samples run 38 % too
  fast.
- **The pronunciation rules**, which have been per-voice since 2026-08-24
- **The announcement cache**, which invalidates itself on a voice change

The **name of the assistant** is read from
`/usr/local/share/dialos/assistent-name.txt`. "Anna" and "Michael" belong
in no extension's source code - otherwise a female voice will at some
point introduce itself as Michael.

## The program name is not the voice command

With Denkzettel the two coincided, here they do not - and that is not a
subtlety but a hard condition: **"dialos" is not in the Vosk
vocabulary** (checked on 2026-09-17; that is also why Piper speaks it as
"Dial OS" or "Dial O S"). "DialOS-Suche öffnen" would simply not be
possible as something to call out.

The `startsaetze` are therefore built from ordinary words and obey the
rules from [sprachbefehle.en.md](sprachbefehle.en.md) - above all: **one
trigger word in addition to the target**, and long enough. A bare
„suchen" (search) would be too short and too frequent; that is the lesson
from the 30 false starts that „starten" caused as a core word.

## What an extension must not do

- **Extend the core grammar beyond its `startsaetze`.** Otherwise the
  whole purpose is gone.
- **Speak by itself** (see rule 4).
- **Keep the microphone** once it is finished.
- **Fire during a dictation.** The dictation marker applies to extensions
  just as it does to the core - whoever dictates „unterlagen durchsuchen"
  into a letter wants it written down, not executed.
- **Do anything security-critical without a yes/no confirmation.** The
  rule applies regardless of how confident the recognition was.

## How an extension gets onto the test device

**Stephan's requirement from 2026-09-17:** the finished extension must be
deployable from the T490 seamlessly. That is not a side condition - it
determines the design, and that is why it stands here and not under "Open
questions".

The route already exists and is meant to **stay the same**:

```bash
sudo /usr/local/sbin/dialos-aufspielen && /media/dialosadmin/SanDisk-Extreme/DialOS/repo/scripts/dialos-installstand.sh --befehl
```

`dialos-aufspielen` today reads from exactly one source:

```
/media/dialosadmin/SanDisk-Extreme/DialOS/repo/iso-build/config/includes.chroot
```

Everything below it moves to its place in the file system, with a
permissions table, an exclusion list, and a restart only of those services
whose files have changed.

**For an extension inside the DialOS repo this works without any
change.** Both files fall under existing entries of the permissions table:

| File | Place in the repo | Permissions | from |
|---|---|---|---|
| Program | `…/includes.chroot/usr/local/bin/dialos-suche.py` | 0755 | `("usr/local/bin", 0o755)` |
| Manifest | `…/includes.chroot/usr/local/share/dialos/erweiterungen/dialos-suche.json` | 0644 | `("usr/local/share", 0o644)` |

**For the first extension, therefore, `QUELLE` needs nothing at all** - it
lives in the DialOS repo, that is, under the path `dialos-aufspielen`
reads anyway. The switch to a **list** of sources only becomes due once
the second extension moves into a repo of its own; it is in `TODO.md`
nonetheless, because it will certainly be needed then. Only one thing
matters about it: several sources with the same `includes.chroot` layout
are the way, **not** a second deployment script. The existing sudoers rule
is, by its own header, „praktisch ein Root-Zugang" (practically root
access) - a second route would be a second one.

**Two adjustments are needed right away**, on the other hand, and both are
small:

1. **The checks from rules 1 and 2 belong in the deployment.** If a
   manifest is among the changed files, vocabulary and collisions are
   checked **before** it goes to its place - and on failure exactly that
   file is not deployed, with a message. Only that makes "refuse instead
   of warn" enforceable at all.
2. **`dialos-installstand.sh` must compare the manifest too.** Otherwise
   the rule "check the installed state, do not assume it" does not apply
   to extensions - and exactly that mistake cost two days on 2026-08-19,
   when two scripts on the device were older than in the repo. As soon as
   extensions live in their own repos, the opportunity for it doubles.

**The core grammar is built from the manifests when the service starts,
not at deployment time.** So a restart of the command service is enough;
a separate installation step is unnecessary.

**Careful, a silent failure lurks here** - noticed while re-reading the
code on 2026-09-17: `dialos-aufspielen` does **not** restart the command
service. It **prints** the two commands for it, and only if
`dialos-sprachbefehl-desktop.py` **itself** has changed:

```python
for skript in ("dialos-sprachbefehl-desktop.py", ...):
    if any(rel.endswith(skript) for rel, *_ in liste):
```

That is correct for session services - they run as the user, not as root,
and a script with sudo rights should not touch them. For extensions,
though, it means: **a new manifest on its own triggers no hint at all.**
The extension would then sit installed on the disk, the service would go
on running with the old grammar, and its start sentence would do nothing -
without an error message, without an announcement. Exactly the outcome
that is the worst one for a blind user.

The condition must therefore include the manifest folder, not just the
script names.

**What this does NOT solve:** it applies to the development device. How an
extension gets onto a customer device, where neither `dialos-aufspielen`
nor the sudoers rule may exist (`scripts/dialos-aufraeumen.sh` removes
both), is open - see below.

## The third naming category

`CLAUDE.md` so far knew two cases: core component (named `dialos-*.py`
and living in the DialOS repo) and family member without a prefix
(Denkzettel). **Extensions are the third** - and they carry the prefix
rightly:

- They do not run without DialOS, because they depend on its grammar,
  voice and microphone handover.
- Installed on their own they make no sense.
- They are not a separate product on different hardware (that is
  DialOS-Mobil) and not a standalone program with its own engine and its
  own target group (that is Denkzettel).

So **DialOS-Suche** is named correctly, and the rule "new family members
are NOT renamed" stays untouched - it applies to standalone programs, not
to something that does not run without DialOS at all.

## The icon: the draft failed at 32 pixels, the magnifying glass carries

Stephan delivered a draft on 2026-09-17. It sits in the repo as
`assets/suche-icon-entwurf.png`, **deliberately with „Entwurf" (draft) in
the name**: it is not the shipping version yet.

**Stylistically it works.** The same circle, the same lady, the same
carrying hand, the same blue-green gradient as on the DialOS app icon -
the family resemblance is there at first glance. On the right, instead of
the sound waves, come a document, an envelope and a magnifying glass.

**What counts was measured: recognizability at small sizes.** The
yardstick has been in the source of `Denkzettel/assets/icon-bauen.py`
since 2026-08-24: „Wenn beide Programme nebeneinander in der
Fensterleiste liegen, muss man sie bei 32 Pixeln auseinanderhalten
können." (If both programs sit side by side in the window list, you have
to be able to tell them apart at 32 pixels.) All three icons were
rendered at 32, 48 and 64 pixels and placed next to each other
(`assets/suche-icon-groessenvergleich.png`, rows from top to bottom
32/48/64, columns DialOS, Denkzettel, Suche):

| Size | DialOS | Denkzettel | Suche (draft) |
|---|---|---|---|
| 64 px | clear | clear | clear |
| 48 px | clear | clear | still clear - magnifying glass as a circle, document as a block |
| **32 px** | **clear** | **clear** | **fails** - document, envelope and magnifying glass merge into one blob |

**The cause is not the drawing but the count.** DialOS has **one** object
on the right (sound waves), Denkzettel **one** (pen with a line), the
draft **three**. At 32 pixels the right-hand half has roughly 14 × 20
pixels left - the text lines in the document end up less than a pixel
apart there and run together. On top of that, the space needed on the
right pushes the face to the left, which makes the left-hand half look
tighter than in the other two as well.

### Built on 2026-09-17: reduced to the magnifying glass

Stephan's decision after the measurement: „reduziere den rechten Bereich
auf die Lupe" (reduce the right-hand area to the magnifying glass). Built
with `assets/suche-icon-bauen.py`, derived from
`Denkzettel/assets/icon-bauen.py` - the same technique, because it already
solved exactly this problem there once.

**The magnifying glass is drawn, not cut out of the draft.** Copied, it
would come along with the cut edges of the overlapping envelope. Drawn, it
has clean edges and a free size. Denkzettel drew the pen for the same
reason.

**Two variants were built and compared**, so that nobody checks it a
second time:

| Variant | Result at 32 px |
|---|---|
| **magnifier only** (sound waves removed) | **clear** - circle with a handle, unmistakably distinguishable from DialOS and Denkzettel. **Chosen.** |
| waves **and** magnifier (closer to the draft) | rejected - waves and ring overlap into the same blob the draft already had |

That makes the result follow the family pattern: Denkzettel replaces the
sound waves with the pen, DialOS-Suche with the magnifying glass.
**Replace, do not add** - exactly the lesson from the draft.

The handle is deliberately short. It explains the shape at 512 pixels,
contributes nothing at 32 any more, and the longer it is, the closer it
comes to the arc. The script **checks the distance to the ring before
drawing** and aborts when it is broken - the first attempt ran into
exactly that (193.6 against a permitted 192, at the end of the handle).

**Twelve files are produced:** `suche-icon-light-*.png` and
`suche-icon-dark-*.png`, each at 32, 48, 64, 128, 256 and 512 pixels, all
with an alpha channel. The comparison comes with it as
`assets/suche-icon-groessenvergleich.png` - on the left on a light panel,
on the right on a dark one, each in the version that belongs there.

**A trap, measured and recorded: DialOS and Denkzettel name their two
versions in opposite directions.**

| File | Disc |
|---|---|
| `DialOS/assets/app-icon-light.png` | rgb(254,255,255) - light |
| `DialOS/assets/app-icon-dark.png` | rgb(4,22,47) - dark |
| `Denkzettel/assets/app-icon-dark.png` | rgb(255,255,255) - **light** |

So at Denkzettel "-dark" means "file for dark surroundings" (Stephan's
decision of 2026-08-24), at DialOS plainly "dark icon". Each is coherent
on its own, together they are a trap. **DialOS-Suche follows DialOS**,
because the files sit in the same folder next to `app-icon-light.png` -
two opposing meanings of the same suffix in one place would be the sure
way to grab the wrong file when wiring it up. And a wrong icon never
strikes a blind user, but strikes the sighted helper at once.

**The draft stays where it is** (`assets/suche-icon-entwurf.png`). It is
the template of the idea, and the measurement it failed is above - the two
belong together.

## Where an extension lives, and how it is shipped

Both decided with Stephan on 2026-09-17.

### Development: in the DialOS repo, not in one of its own

A repo of its own per extension is the goal - its own versioning, its own
changelog, and the DialOS repo does not grow any further (it already
carries `iso-build/` and eight background images of around 11 MB each).

**For the first extension, though, not yet.** As long as the interface
itself keeps changing, two repos would have to be kept in sync while both
are unstable - and for every bug the first question would be which of the
two it belongs to. Splitting it out later is a manageable step; merging
two moving states would not be.

So `QUELLE` in `dialos-aufspielen` stays a single path for now. The switch
to a list only becomes due once the second extension moves into a repo of
its own - it is in `TODO.md` nonetheless, because it will certainly be
needed then.

### Shipping: as a `.deb`, but not for development

| Device | Route | Why |
|---|---|---|
| Development device (T490) | `dialos-aufspielen` | Changed files in seconds. A `.deb` would have to be built, version-bumped and installed on every iteration - with a voice dialogue where a wording gets reworked twenty times a day, that is the difference between "it runs" and "it grates". |
| Customer device | `.deb` | There is no `dialos-aufspielen` there at all. `scripts/dialos-aufraeumen.sh` removes it along with the sudoers rule, and that is meant to stay that way. |

**The strongest argument for the package is `postinst`.** The two
mandatory checks from rules 1 and 2 need a place where they cannot be
bypassed: if the check in the installation script fails, the installation
fails. With a script that copies files, "refuse instead of warn" remains a
courtesy.

On top of that comes `Depends: mailburg` - DialOS-Suche's dependency on
MailBurg is then enforced by the package manager instead of by a line in
the documentation. MailBurg already builds itself as a `.deb` anyway.

**To be honest about it:** DialOS builds not a single package today. Setup
runs over shell scripts (`dialos-parakeet-einrichten.sh`,
`dialos-erkenner-einrichten.sh`). A `.deb` is therefore new infrastructure
- `debian/control`, `changelog`, `rules` -, and without a repository
server it stays a `dpkg -i` by hand, that is, without automatic updates.

## Open questions

Deliberately not decided, because they are Stephan's call or because the
answer has to be measured:

1. **What happens on a core update?** `braucht_dialos` detects the case,
   but it is not settled what happens then: switch the extension off and
   announce it, or start anyway and hope. For a blind user a silent
   failure is the worse answer.
2. **Whether hassil finds its place here.** It has been installed since
   2026-08-13 and is unused to this day (not a single template in the
   system). Mapping sentence → action per extension would be the first
   place where it could contribute something - that is not decided.
3. **Whether the archive runs encrypted.** MailBurg can do it (AES-256-GCM
   per file), but the search index stays plain text in the process - and a
   blind user who would have to speak their archive password is a problem
   of its own.

## The first extension: DialOS-Suche

Purpose: searching and reading out letters, documents, notes and e-mails
by voice. The choice of program is in
[anwendungen.en.md](anwendungen.en.md), the intended sentences in
[sprachbefehle.en.md](sprachbefehle.en.md), the tasks in
[TODO.en.md](../TODO.en.md).

**MailBurg is intended as the engine, not a new search index.** The
reasoning follows the selection criterion from
[anwendungen.en.md](anwendungen.en.md) - controllability from outside -
and MailBurg is the only program in the family that fully meets it:
`mailburg suchen ARCHIV "…"` is a ready-made command line.

**DialOS-Suche makes two demands that go beyond an ordinary extension**
and are therefore listed here, because they shaped the design:

- **A search term does not fit into any closed grammar.** „Krankenkasse"
  (health insurer) cannot sit in a sentence list, otherwise every
  searchable word would have to be in it. It needs the same two-stage
  switch as dictation - the small Vosk recognizer takes the start
  sentence, then free recognition for the term.

  **Which recognizer that is, is already settled: Parakeet.** Built in
  firmly since 2026-09-16
  (`sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` via sherpa-onnx, model
  under `/usr/local/share/dialos-parakeet/`, 12 s to load instead of 33 s
  for the large Vosk model, switchable off with `parakeet-aus`). Measured
  on 2026-09-15 on the letter read out aloud: **2.8 % word errors against
  Vosk's 12.7 %**. DialOS-Suche therefore has nothing to procure and
  nothing to measure anew for it, and the division of labour already
  stands that way anyhow: **Vosk for commands, Parakeet for text** - and a
  search term is text.

  Exactly one thing remains to be checked, and it is new: whether Parakeet
  can be given a **dictionary from the archive itself**. The most frequent
  sender names from the FTS5 index would be precisely the words every free
  recognition trips over. For the same purpose dictation already has a
  personal dictionary („gehört = geschrieben" - heard = written) that
  lives on the device only.
- **A document is long, and while DialOS speaks, it does not listen.**
  **That is not hypothetical but proven on the device:** „Alle Befehle
  vorlesen" (read out all commands) runs for **144 seconds**, and
  [sprachbefehle.en.md](sprachbefehle.en.md) says about it explicitly
  „nicht unterbrechbar - dafür gibt es die Themen" (not interruptible -
  that is what the topics are for). „Brief vorlesen" (read out the letter)
  likewise reads in one go. For comparison: "Windows Desktop." takes
  1.5 seconds.

  For an archive that becomes the normal case instead of the exception -
  whoever searches gets hits they do not all want to hear. It is the same
  class of fault as the measured deafness of 3.6 seconds after a switch
  (see [sprachsteuerung.en.md](sprachsteuerung.en.md)), only a hundred
  times longer. Intended: read out paragraph by paragraph, with a short
  listening window between paragraphs using a mini grammar of „stopp"
  (stop), „weiter" (continue), „zurück" (back), „nochmal" (again). No real
  barge-in - "Soll ich stoppen?" inside the letter being read out would
  stop it.

  **That does not belong built into DialOS-Suche but into
  `dialos-say.py`.** The 144 seconds of the command overview are already
  an open item today, and they belong to no extension. Whoever builds
  interruptibility for the archive solves it for everything.
