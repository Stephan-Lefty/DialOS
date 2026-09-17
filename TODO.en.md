[Deutsch](TODO.md) | [English](TODO.en.md) | [Changelog](README.en.md#changelog)

# TODO

A running list of small open items and next steps that Stephan or Claude
notice during day-to-day work. Unlike
[Open questions](docs/offene-punkte.en.md) (fundamental, not-yet-decided
architecture questions), these are concrete, checkable tasks. What is
still open stays at the top. Completed items are not deleted but moved
down to „Done (for traceability)" - grouped by topic there, chronological
within each topic, each with the date it was finished.

**Why there are still checkmarks at the top:** some completed items belong
to one that is still open - the open one refers back to them ("see above",
"residual risk from this"). Those stay at the top until the open item is
finished too, and then move down together. That way no reference breaks.

- [ ] **Complete letter following DIN 5008** (Stephan, 2026-09-16, after building
  Parakeet in). (1) Define the user's personal data - Stephan's first - once for
  all programs and enter it (letterhead, Thunderbird signature, weather place;
  depends on the customer data and its encryption). **(1) built 2026-09-16:**
  form `persoenliche-daten-vorlage.txt`, `dialos-persoenliche-daten.py`,
  letters/names/weather connected; input form also for `nutzer`, setup step
  6/6 - **confirmed on the device 2026-09-16, 17:37/17:47:** Stephan's data
  entered in both accounts via the form (first attempt for `nutzer` failed on
  `runuser` without full path under pkexec, fixed) - open: Stephan reviews the
  polkit rule, mail
  signature, Du/Sie, signature as image. (2) The recipient's exact
  address is dictated. (3) That address is automatically added as a contact in
  Thunderbird. **(2)+(3) built 2026-09-17:** guided recipient dialogue in
  dictation, search in the Thunderbird contacts, new contact in `abook.sqlite`
  (queue while Thunderbird runs) - simulated with Piper (new, found, none). Open:
  test with Stephan's voice (13:00 and 13:36: names, abort - rebuilt);
  Thunderbird shows the created card **(confirmed 13:40)**;
  **"von vorne"/"alles verwerfen" in dictation and cent amounts from Vosk built
  (14:15 trial; 15:00 trial: "von vorne" ✓, "alles verwerfen" and cents rebuilt,
  checked with the real recording; 15:20 trial: both paths ✓, amounts ✓)** - open: chunk
  without a sentence end runs into the next sentence ("… 2027 In ihrem Schreiben"); wiring
  **DIN PDF wired in 2026-09-17** (archive, PDF, printing; no head, date
  17.09.2026, info block level with the return address) - open: check the paper
  printout; **contact person built 2026-09-17** (simulated, installed 16:30, device
  trial open). **Email addresses in dictation built 2026-09-17** (own / from contact /
  spelled; simulated, installed 16:30, device trial open - enter own email in the form). **Mail
  signature installed** (17.09.). **Draft 2026-09-17:** `dialos-brief-din.py` (form B, preview with sample
  data) - open: Stephan's verdict, recipient address, wiring into
  dictation/printing/PDF. **Mail signature from the data built** (not installed).
  (4) Layout following DIN 5008 so the PDF is always clean - printed
  or sent by mail (address field for window envelopes, reference line/date,
  subject, fold marks). Personal data only on the device; ask before adding new
  data to the repo.

- [ ] **Check the command overview on the device** (built 2026-09-16): "Alle
  Befehle vorlesen" and the six "Befehle für …" with a real voice; is the full
  list (144 s) too long? Open: interrupting during the announcement is not
  possible.

- [ ] **Check the seasonal wallpaper on the device** (built 2026-09-16): summer
  picture after login, autumn from 23.09. 02:06. All eight pictures in 3840 ×
  2160 light and dark included (19:10). Note for the next picture version: the
  logo bottom right is only ~3 % from the edge - on 16:10 screens the zoom cuts
  5 % on the left and right.

- [ ] **Parakeet licence notice on the device** (2026-09-16): CC-BY-4.0 requires
  attribution (wording in docs/lizenzen.en.md). Belongs in a licence overview
  that DialOS can show or read out on the device.

- [ ] **Build the extension interface, then DialOS Search as the first
  extension** (decided with Stephan on 2026-09-17). The draft is complete in
  [docs/erweiterungen.en.md](docs/erweiterungen.en.md) - **only the checkable
  steps here, the why is over there.**

  **The order is deliberate.** Today every voice command sits in three places in
  `dialos-sprachbefehl-desktop.py` (sentence in `GRAMMATIK_AN`, entry in the
  dict, branch in the loop). A fourth program following the same pattern would
  be the fourth copy. The interface comes first, and DialOS Search proves in
  passing that it carries.

  **The design point everything hangs on: switch over, do not add up.** The core
  grammar grows by **exactly one sentence** per extension - its start sentence.
  Everything else the extension recognises itself, as long as it is running.
  Reason: with 27 sentences there were already 382 command-less word
  combinations on 2026-08-22, and the list stands at **47 sentences** today -
  without a single extension. The number does not grow linearly. An interface
  that lets everyone put twenty sentences into the core grammar tears open again
  the fault that has only just been defused since 2026-08-24.

  **Step 1 - the interface:**
  - [ ] `dialos-sprachbefehl-desktop.py`: extend `GRAMMATIK_AN` at start-up from
    the manifests under `/usr/local/share/dialos/erweiterungen/` instead of
    keeping every sentence hard-coded in the source. The existing 47 sentences
    stay where they are - **do not** move them onto manifests in the same go.
    Two rebuilds at once, and a fault can no longer be attributed.
  - [ ] `dialos-erweiterung.py` with `pruefen` / `einbauen` / `entfernen` /
    `liste`.
  - [ ] **A vocabulary check that REFUSES instead of warning.** Every word from
    `startsaetze` and `eigene_grammatik` against the small model. Reason:
    "löschen" (delete) is missing from the vocabulary and was silently thrown
    out of the grammar on 2026-08-18. Nobody reads a warning at install time a
    second time; the fault only shows once the user is alone with the device.
  - [x] **Collision check against the complete grammar - tool finished on
    2026-09-17.** `scripts/dialos-grammatik-pruefen.py` can now check sentences
    that are NOT built in yet: `--neu "satz"`. That did not work before, and the
    gap was not harmless - a candidate passed as a plain argument was heard
    against a grammar that does not contain it at all, and Vosk pressed it onto
    the nearest existing sentence. That looked like a confusion but was a fault
    of the tool; conversely a broken candidate could stay unnoticed.

    The check now runs **in both directions**: whether the candidate is
    recognized, **and whether existing sentences break because of it**. The
    second question is the more important one - a candidate that fails by itself
    costs only itself; one that makes an existing command confusable breaks
    something that works today.

    On top of that the **first** mandatory check now runs along instead of only
    standing in the documentation: vocabulary against `graph/words.txt`, without
    speaking, separately for candidate and existing stock. A missing word in the
    candidate ends the check, one in the existing stock is reported as a legacy
    problem - otherwise a new command would hang on an old problem.
  - [x] **Run the check on the device** - the wording of the start sentence
    depends on it. **Run on 2026-09-17 on the T490: all 51 sentences recognised
    verbatim** (the candidate and all 49 existing ones), the start sentence can
    be built in. **But:** the tool reported "graph/words.txt nicht lesbar -
    Wortschatz UNGEPRUEFT" - the small model under
    `/usr/local/share/vosk-model-de-small/graph/` has no `words.txt` (only
    `Gr.fst`, `HCLr.fst`, `phones/`). The vocabulary check therefore never runs
    there. Done by hand: grammar built with "unterlagen durchsuchen", Vosk
    reported no "missing in vocabulary" - both words known. The tool should
    check via that Vosk message instead of the file (fits the "bildschirmfoto"
    side finding below).

    **The 51 have an explanation, and it is a fault in the tool** (see next
    point): 49 existing sentences plus the candidate makes 50 - the candidate
    was checked twice. That changes nothing about the result.

        scripts/dialos-grammatik-pruefen.py --neu "unterlagen durchsuchen"

    With that, "Unterlagen durchsuchen" (search the documents) is the start
    sentence of DialOS-Suche - it is recognized itself, and **none of the
    existing commands breaks because of it**.

    The pre-selection has been confirmed: "unterlagen" (documents) and
    "durchsuchen" (search) appear in none of the 49 existing sentences (counted:
    71 different words). "briefe" (letters), by contrast, would already be in
    there, "brief" (letter) even six times - which is why "Briefe durchsuchen"
    (search the letters) has been dropped as a second phrasing.

    **What the run still does not replace:** Piper speaks more clearly than a
    human being, more evenly and always from the same distance. That does not
    make the sentence broken - but it is only proven with a real voice.
  - [x] **A counting fault in the tool, found by the first real run and fixed**
    (2026-09-17). The run reported **51 instead of 50** sentences, and Stephan
    saw the cause in the log: "Unterlagen durchsuchen wurde 2x aufgeführt"
    ("Unterlagen durchsuchen was listed twice"). That is exactly what it was -
    `alle` already contained the candidate (appended at the top), and
    `neu + alle` checked it a second time. **Only the number was wrong, not the
    result** - the candidate was checked twice instead of not at all. Fixed, the
    candidate now stands first and exactly once.

    Recorded because the lesson is bigger than the fault: a number that cannot
    be explained has more than once been the beginning of a wrong diagnosis in
    this project. Here it was the beginning of the right one.
  - [ ] **"bildschirmfoto" (screenshot) is missing from the large Tuda model** -
    a side finding from building the tool.
    "Bildschirmfoto erstellen" (take a screenshot) is a documented command and
    works on the device, and the word appears **three times** in the grammar. So
    the small model knows it; the large Tuda model does not.

    **A rule follows from that:** a pre-check of the vocabulary against the
    large model is **worthless** - it has a different vocabulary than the small
    one, and in both directions. Checks are run exclusively against
    `/usr/local/share/vosk-model-de-small`, that is, on the device.

    **The cross-check is done** (Stephan, 2026-09-17): the line
    `ALTLAST … 'bildschirmfoto'` did **not** come - but not because the word
    would be known, rather because the check did not run at all for lack of
    `words.txt`. Fixed in the next point.
  - [x] **Vocabulary check switched to Vosk's own message** (2026-09-17,
    Stephan's finding and suggestion). It read `graph/words.txt` - **which does
    not exist in the small model at all**:
    `/usr/local/share/vosk-model-de-small/graph/` contains only `Gr.fst`,
    `HCLr.fst` and `phones/`. The check therefore never ran there and honestly
    reported "Wortschatz UNGEPRUEFT" (vocabulary UNCHECKED) - that is how it
    stood in the log of the run on the device, too.

    **A mandatory check that never fires cannot be told apart from a missing
    one.** That is exactly what it was until today.

    The check now works the way Vosk does anyway: the grammar is built, and
    Vosk's message `Ignoring word missing in vocabulary` is caught. For that,
    `SetLogLevel` has to be raised briefly and stderr redirected at the
    file-descriptor level - the message comes from the C++ layer, not from
    Python, and `contextlib.redirect_stderr` does not reach it there. That is
    the only way that works independently of how the model is built.
    - [ ] **Cross-check on the device that the new check really fires:** an
      invented word as a candidate has to be refused.

          scripts/dialos-grammatik-pruefen.py --neu "xylofonquark durchsuchen"

      Expected: "KANDIDAT NICHT IM WORTSCHATZ DES MODELLS: 'xylofonquark'"
      (candidate not in the model's vocabulary), return value 1. If a pass
      comes instead, it still checks nothing.
  - [ ] **Microphone handover via a marker file, with a guard.** A crashed
    extension must not keep the microphone - the user would otherwise be
    speaking against a deaf device, and even switching the voice control off
    would no longer be audible.

  **Step 2 - the installation path** (Stephan's requirement of 2026-09-17: "wir
  müssen nachher mit der fertigen Erweiterung nahtlos vom T490 zugreifen können
  und die Erweiterung dort installieren können" ("afterwards we have to be able
  to reach the finished extension seamlessly from the T490 and install the
  extension there")):
  - [ ] Hook the two checks from step 1 into installing: if a manifest is among
    the changed files, it is checked **before** it goes to its place. Only that
    makes "refuse instead of warn" enforceable.
  - [ ] **The restart notice must also come for a new manifest** (found while
    reviewing the code on 2026-09-17). `dialos-aufspielen` does not start the
    command service itself, it **prints** the two commands for it - and only if
    `dialos-sprachbefehl-desktop.py` has changed **itself**
    (`if any(rel.endswith(skript) …)`). A new manifest alone therefore triggers
    nothing: the extension would sit there installed, the service would carry on
    with the old grammar, and its start sentence would do nothing - with no
    error message, no announcement. For a blind user the worst possible outcome.
  - [ ] `scripts/dialos-installstand.sh` has to compare the manifest as well.
    Otherwise "check the installation state, do not assume it" does not apply to
    extensions - and exactly that fault cost two days on 2026-08-19.
  - [ ] **Only due later:** change `QUELLE` in `dialos-aufspielen` from a single
    path to a **list**. Not needed for the first extension, because it lives in
    the DialOS repo; needed as soon as the second moves into a repo of its own.
    **No second installation script** - by its own header the existing sudoers
    rule is "practically root access", a second path would be a second one.
  - [ ] Run `--befehl` after the first real installation. A commit does not
    prove that anything takes effect on the device.

  **Step 3 - DialOS Search**, only once steps 1 and 2 stand:
  - [ ] **MailBurg as the engine**, no new search index. It is the only program
    in the family that fully meets the selection criterion from
    `docs/anwendungen.en.md` (`mailburg suchen ARCHIV "…"`), has FTS5 with
    prefix and trigram index, PDF text extraction, OCR via tesseract and already
    builds itself as a `.deb` for Debian 13. Licence checked: MailBurg is MIT,
    DialOS GPL-3.0 - MIT code may go into a GPL project.
  - [ ] **Call it over the command line, do not import it as a library.** That
    keeps versions and licences apart.
  - [ ] For that MailBurg needs a **JSON output** for `suchen` - a hit list
    typeset for humans is unusable for a voice dialogue. Belongs in the MailBurg
    repo, not here.
  - [ ] **Non-mail sources in MailBurg:** letters from `~/Dokumente/`, scans,
    Denkzettel's `notizen.db`. The extraction chain can already do all of that,
    it is only called via attachments today.
  - [ ] **Free search term via Parakeet**, not via Vosk. A search term is text,
    not a command - the same division of labour as in dictation. Nothing new to
    procure. **Only one thing needs checking:** whether Parakeet can be given a
    dictionary built from the most frequent sender names in its own index, the
    way dictation has its personal dictionary. Every free recognition fails on
    that otherwise.
  - [ ] **Check phonetic search:** an FTS5 column with the Cologne phonetics of
    sender names, so that "Meier/Mayer/Maier" fall together. Catches recognition
    fuzziness structurally instead of loading it onto the user as a question.
  - [ ] **Hit dialogue:** 40 hits cannot be read out. Narrow down first, announce
    the number, name the way - the same rule as with the shopping list ("a
    command does not take a decision away from the user that he can make
    himself").
  - [x] **Icon - done on 2026-09-17.** Stephan's draft
    (`assets/suche-icon-entwurf.png`) fitted stylistically, but measured it
    failed at 32 px: document, envelope and magnifier merged into one blob,
    while DialOS and Denkzettel stayed clear there. The cause was the number,
    not the drawing - three objects on the right instead of one, and only about
    14 × 20 px are left for the right half at 32 px. The yardstick has stood in
    the source of `Denkzettel/assets/icon-bauen.py` since 2026-08-24.

    Stephan's decision afterwards: "reduziere den rechten Bereich auf die Lupe"
    ("reduce the right-hand area to the magnifier"). Built with
    `assets/suche-icon-bauen.py`, derived from
    `Denkzettel/assets/icon-bauen.py`. The magnifier is **drawn**, not cut out
    of the draft - copied it would come with the cut edges of the overlapping
    envelope. Two variants built and compared: "magnifier only" carries at
    32 px, "waves and magnifier" blobs up just like the draft. That makes it
    follow the family pattern - Denkzettel replaces the sound waves with the
    pen, DialOS Search with the magnifier. **Replace, do not add.**

    Twelve files: `suche-icon-light-*.png` and `suche-icon-dark-*.png` at 32,
    48, 64, 128, 256, 512 px, all with an alpha channel. Evidence on a light
    and a dark panel in `assets/suche-icon-groessenvergleich.png`. The script
    checks the distance to the ring before drawing and aborts when it is
    broken - the first attempt ran into exactly that (193.6 against a permitted
    192, at the end of the handle).

    **Found along the way and recorded in the script: DialOS and Denkzettel
    name in opposite directions.** `DialOS/assets/app-icon-light.png` has a
    light disc, `Denkzettel/assets/app-icon-dark.png` a light one as well. So
    at Denkzettel "-dark" means "for dark surroundings", at DialOS "dark icon".
    DialOS Search follows DialOS, because the files sit in the same folder -
    two meanings of the same suffix in one place would be the sure way to the
    wrong file.
    - [ ] **Look at it on the device**, as soon as a `.desktop` entry exists: in
      the panel, in the start menu and in the window list next to DialOS and
      Denkzettel. Decided on screen is not the same as seen in the panel.

  **Delivery as a `.deb`** (decided 2026-09-17), but **not for development**: on
  the T490 `dialos-aufspielen` remains the way, because a package would have to
  be built and counted up at every iteration. For a customer device the package
  is the only way - there `scripts/dialos-aufraeumen.sh` removes
  `dialos-aufspielen` together with its sudoers rule. The real gain is
  `postinst`: there the two mandatory checks cannot be bypassed, and
  `Depends: mailburg` enforces the dependency. Careful: DialOS builds **not a
  single** package today - that is new infrastructure (`debian/control`,
  `changelog`, `rules`), and without a repository server it stays at `dpkg -i`
  by hand.

  **Extensions live in the DialOS repo for now** (Stephan, 2026-09-17). A
  separate repo per extension is the goal, but not for the first one: as long as
  the interface keeps changing, two repos would have to be kept in sync while
  both are unstable - and every fault would first of all not be attributable.

  **Still open** (in `docs/erweiterungen.en.md`): what happens on a core update;
  whether hassil finally finds its place here; whether the archive runs
  encrypted (MailBurg can do it, but the search index stays plain text).

- [ ] **Reading long texts aloud cannot be interrupted - and for an archive that
  becomes the normal case** (2026-09-17). **Not a new fault:** the item "Check
  the command overview on the device" further up already names it - "Alle
  Befehle vorlesen" (read out all commands) runs for 144 s, and "interrupting
  during the announcement is not possible". "Brief vorlesen" (read out the
  letter) likewise reads straight through.

  **What changes:** for the command overview that is an inconvenience one can
  get around with "Befehle für …" (commands for …). For an archive it is the
  normal case - whoever searches gets hits he does not want to hear in full, and
  a two-page letter from the health insurer takes longer than the 144 seconds.
  For comparison: "Windows Desktop." (the announcement after switching the look)
  takes 1.5 s.

  **Planned:** read out paragraph by paragraph, between the paragraphs a short
  listening window with a mini grammar of "stopp" (stop), "weiter" (carry on),
  "zurück" (back), "nochmal" (again). The pattern exists twice already - the
  second recogniser for "Diktat beenden" (end dictation) and the yes/no
  recogniser before emptying the note. It needs no new technology, only the text
  split up before speaking.

  **It belongs in `dialos-say.py`, not in DialOS Search.** The 144 seconds of
  the command overview belong to no extension; whoever builds it for the archive
  solves them for everything.

  **Do NOT build real barge-in first.** The echo-cleaned source
  `dialos_mikrofon_ohne_echo` does exist already, but listening during one's own
  voice means: "Soll ich stoppen?" ("shall I stop?") inside the letter being
  read out stops it.

  **And secondly:** a letter read out must **not** go into the announcement
  cache under `~/.cache/dialos/ansagen`. That one is meant for "Ich höre Dir
  zu." ("I am listening to you"), which comes every day; a document read out
  once fills it with WAV files that never match a second time.
  `dialos-say.py` has no switch for that today - the line is whether a text
  repeats, not how long it is.

- [ ] **A CONVERSATION IN THE ROOM OPERATED DIALOS - with printing,
  dictation and archive** (2026-09-14, 11:01-11:31, during Stephan's break).
  The most serious finding so far, because it does not just annoy but
  **writes down, files and prints other people's conversations**.

  **What happened** (account `dialosadmin`, laptop microphone and speaker,
  AIRHUG off). People were talking loudly and at length nearby, peaks
  27000-30000. Stephan when asked: a conversation in the room.

  | Time | What DialOS did |
  |---|---|
  | from 11:01 | switched voice control on by itself six times |
  | 11:15:47 | "brief schreiben" (+1 word) - 97 s of conversation as a letter, previous letter set aside, **PDF into the archive** |
  | 11:18:47 | switched to the Windows look |
  | 11:19:53 | "notiz drucken" - printed |
  | 11:20:12 | "brief brief brief drucken" (+2) - **printed the conversation** |
  | 11:24:52 | "einkauf wir brief drucken" (+2) - **printed the conversation again** |
  | 11:24:53 | "einkaufszettel aufnehmen" - 50 s of conversation as 8 entries |
  | 11:30:26 | "einkauf erledigt" (+2) - delete question, heard "nein nein ja", not deleted |
  | 11:30:53 | "notizen drucken" (+2) - stuck in the queue, cancelled |

  **Cleaned up** (Stephan chose "restore the old state"): previous letter back,
  shopping list empty again, the conversation versions (letter, archive PDF,
  list) moved into a folder readable only by the account, to review and
  delete. Print job 8 cancelled. Two pages with the conversation were in the
  printer. **The logs under `~/.log/` still contain fragments of the
  conversation** - not in the repo, and deliberately not quoted here.

  **What failed - four places:**
  1. **Switching on.** "Both words" is not enough against a long
     conversation: the grammar forces every utterance into its words, and at
     some point "sprachsteuerung" and "starten" stand next to each other.
  2. **No confirmation before consequential actions.** Printing, dictation
     (overwrites the letter, files a PDF) and switching run immediately. Only
     deleting asks - and that question held, narrowly.
     **Fixed on 2026-09-14** (Stephan: build a confirmation before printing
     and dictation): both now go through `dialos-notiz.py` with the same yes/no
     question as deleting. Checked silently with stubs (yes, no, nothing
     understood, empty list; marker only during the question). **Open:** a
     test on the device with a real voice - and it only takes effect after the
     next login, because the command service has to restart.
     **Test done (2026-09-14, 11:50):** the question came, "nein" prevented the
     print, "ja" started the dictation. But Stephan had to give both answers
     twice - measured 2.03 s parec buffer plus the microphone only opening after
     the question. Fixed (microphone open during the announcement, 30 ms
     buffer), checked on the raw microphone. **Open:** the same test again with a
     real voice after logging in again, plus a shopping-list dictation (word
     start, "Diktat beenden" no longer an entry).
     **Second test (12:10):** "nein" and "ja" each on the first attempt,
     "Bananen" complete right after "Ich schreibe mit". "Diktat beenden" only
     partly cut off, "Den" remained as an entry - the cut is now 0.35 s earlier,
     and the timestamps are logged in the dictation log from now on.
     **Third test (12:22):** "ja" on the first attempt. But the dictation ended
     by itself after "Rote Äpfel" - the small model heard "diktat beenden
     beenden" in "Bananen". Count across all logs: exactly "diktat beenden" 14
     times (genuine as far as traceable), three-word variants 3 times (one
     provably wrong). Now only exactly "diktat beenden" counts. The rest is cut
     by where words START, not where they end.
     **Open:** a fourth test - real timestamps for the cut are still missing. Switching the
     look still does not ask (it does no harm and is instantly reversible).
  3. **The extra-word rule of 2026-08-24** (up to two words too many) made
     three of the four print jobs possible. It was measured on Stephan's real
     voice, not on a conversation.
  4. **The spoken hints** ("Der Befehl heisst: notiz drucken") say command
     words into the room. Notable timing: 11:18:50 hint "notiz drucken",
     11:19:53 recognised "notiz drucken". **Not proven** that it was the
     echo - people were talking in the room after all.

  **Not decided yet, only directions:** confirmation before printing and
  dictation; no extra-word rule for consequential commands; a conversation
  detector (many utterances without a command in a short time -> switch off
  instead of speaking hints); wake word instead of grammar (already an item).
  The item "First false start" below is the same mechanism, now with
  consequences.

  **Repeated at 12:24-12:29 with a TV film** (Stephan: when a film is running
  on TV, the voice control keeps wanting to do something): letter dictation
  despite the confirmation (a "ja" in the film), switching three times, a
  screenshot. The letter is in the trash, the previous one is back.

  **Stephan's decision (2026-09-14): build A and B, plan C, check D.**
  - **A - conversation detection: built.** 5 utterances without a command
    within 30 s → off, with an announcement. Replayed against all sessions: 12
    genuine ones stay on, 7 from conversation/film switch off after 14-23 s,
    before any false command got through. **Open:** test with the TV after
    logging in again.
  - **B - switch on only with silence before and after: measured only for
    now.** For every "sprachsteuerung …" the level curve of the last 4 s is
    logged. Threshold only after real numbers with and without the TV.
    **Film test 12:43-12:50:** the film switched on once in 5 min, then "brief
    schreiben" got through after only 3 fragments (the confirmation held with a
    "nein" from the film), A only kicked in after 2 min. **A alone is not
    enough against TV sound.** **Measurement:** silence BEFORE does not
    separate (the film had a quiet spot itself), silence AFTER does - Stephan
    5 times last values 0, film 11-27. **B built** (Stephan: build B that
    way): the last 0.5 s after the sentence below 3000, otherwise rejected
    with the announcement "… es ist zu laut …" (at most once a minute).
    **Price, accepted deliberately:** with a loud TV the user cannot switch it
    on either. Thin data - re-check.
    **Stephan's assessment of the state (2026-09-14):** the voice control
    currently works when there is almost no background noise. For a loud
    environment, C or D is the real solution.
    **Checked on the device (12:58, after logging in again):** loud TV →
    sentence rejected (values after it up to 8000), the "… zu laut …"
    announcement came; no TV or a quiet TV → switched on (values after 0-1);
    quiet TV afterwards → conversation detection after 20 s, off. Confirmed by
    Stephan.
    **Refined (13:09):** Stephan with the TV on but quiet at that moment - one
    block of 3149 after the sentence, rejected, and because of the 60 s lock
    WITHOUT an announcement. Now one spike is allowed, the announcement at
    most every 15 s. Checked against all 14 switch-on sentences: only this
    case changes.
    **Finding 2026-09-15, 10:51-10:52:** while reading the letter paragraph
    for the recogniser comparison (the recording tool did not set the marker
    yet) Vosk heard **"sprachsteuerung starten" three times in 40 s** in
    ordinary reading - B rejected all three (Stephan kept reading). **But the
    "… es ist zu laut …" announcement came all three times** and interrupted
    him: by definition it comes exactly when someone keeps talking. **Open, to
    decide:** announce less often (e.g. once per 5 min), only with silence
    BEFORE the sentence, or only for exactly two words without further
    fragments. The 60 s lock was lowered to 15 s on 09-14 precisely because of
    a silent failure - weigh both.
    **Decided 2026-09-15 (Stephan: it "always" announces "… zu laut" - "and
    nobody said Sprachsteuerung!"):** the first time is rejected silently; the
    announcement only comes if the sentence is rejected again within 20 s.
    Recomputed on the ten rejections of that day: two announcements instead of
    eight (both while reading aloud at 10:51). The greeting now also says
    "Wenn Du etwas möchtest, sage: Sprachsteuerung starten." - voice control
    deliberately starts on standby, not switched on. Effective after the next
    login; audio samples of the greeting not updated.
  - **Set aside for now: minimum loudness for commands.** Peaks on
    2026-09-14: Stephan's commands 47 times, quietest 7810; film 76 times,
    median 24188, only 5 quiet fragments below 3000; conversation 253 times,
    quietest 4162. A threshold would only have caught a quiet TV (A handles
    that), nothing against a loud film or conversation. On earlier days there
    were recognised utterances from 847 - whether real commands were among
    them (headset microphone) can no longer be established. Revisit once C/D
    are in place.
  - **Setup of the measurements on 2026-09-14** (Stephan: the TV speaker is
    about as far away as he is): TV and user at the same distance from the
    laptop microphone. That is why film and voice arrived at almost the same
    level - loudness cannot separate them. B works through the sequence (the
    user is silent after the sentence, the film is not), not through
    distance. For C this is exactly the test case: same loudness, same
    distance.
  - **C - wake word (openWakeWord):** plan - the item already exists further
    down; today's logs as the test bench.
  - **D - button instead of the switch-on sentence:** check whether the AIRHUG
    or a headset provides a key that can be read (media key via Bluetooth
    AVRCP).

- [ ] **Slips of the tongue in dictation: "Satz löschen" and "Satz
  wiederholen" - built, checked offline, test with a real voice pending**
  (Stephan on 2026-09-15 asked how dictation can know that a sentence has to
  be spoken again; his choice: "Satz löschen", plus "Satz wiederholen").

  **Design:** both sentences are in the grammar of the small closing-phrase
  recogniser. Dictation keeps every utterance as a unit with word timestamps
  (`Aeusserungen`). "Satz löschen" removes the last one and says "Gestrichen:
  …", "Satz wiederholen" reads it out ("Zuletzt: …"). While Anna answers, audio
  is read and discarded, then both recognisers start afresh.

  **Safeguards, all measured:** against Piper, ordinary letter text produced a
  connected "satz wiederholen" and "satz löschen". Silence separated them -
  genuine command: silent 0.5 s before/after (peak 24/18 and 1), errors: loud
  (32653/22769, 27990/22874). Therefore: exactly two words, gap at most 0.6 s,
  0.4 s silence before, 0.5 s silence after, with a 0.15 s margin to the word
  timestamps (without it a genuine command counted as "not silent afterwards" -
  Vosk sets the word end slightly early). Command words are only removed from
  the text once confirmed.

  **Changed at the closing phrase along the way:** "Diktat beenden" now also
  waits for silence afterwards, and the 3 s lock applies again after every
  command. Reason: in the offline test the fresh small model turned "die
  Rechnung liegt dem Schreiben bei" into "diktat beenden" (0.41 s gap) right
  after "Satz löschen" - and in the morning "bis Ende des Monats".

  **Checked offline in real time through the real dictation** (Michael,
  simulated microphone): two false triggers rejected, slip deleted and
  announced, "Satz wiederholen" read the last sentence without deleting,
  clean end, no command words in the letter.

  **First test with a real voice (2026-09-15, 12:27) - two weaknesses, both
  fixed.** Both commands were recognised, three false triggers in running text
  rejected, "bis Ende des Monats" triggered nothing. But:
  1. **The failed first attempt was deleted, not the slip.** Stephan read out
     the bold words of my instructions ("Pause Satz löschen") - the small model
     heard three words, no command, the text went into the letter. The second
     "Satz löschen" then deleted exactly that remnant ("Gestrichen: Pause Satz
     löschen"), "Satz wiederholen" read out "Absatz sagt wiederholen".
     **Now:** a remnant at the end of the text (last word löschen/wiederholen,
     "satz" within the two words before, in letters including a single word
     before it such as "Also") is removed first.
  2. **A recognition chunk was deleted, not a sentence.** "punkt setzen" came
     as a chunk of its own, and "Ich bitte Sie … wäre ich dankbar" as ONE chunk
     of 60 words. **Now:** a sentence reaches back to the previous full stop,
     question mark, exclamation mark or line break; an unfinished sentence is
     the sentence itself. On the shopping list: the last item.
  Also: no more "Müller ." (a punctuation chunk attaches to the word before),
  and after "neuer Absatz"/"neue Zeile" the next word is capitalised ("Mit
  freundlichen Grüßen"). Checked offline in real time with exactly this
  sequence: remnant removed, the Meier sentence deleted, only the last sentence
  taken from the long chunk.

  **Second test with a real voice (2026-09-15, 13:02):** "Satz löschen"
  correctly deleted the Meier sentence. Newly found and fixed:
  1. **"Satz wiederholen" read out "Satz wiederholen Jax".** The large model
     heard "jax wiederholen" and placed "jax" more than 0.35 s before the start
     given by the small model - it stayed. Now removed is what ENDS after 0.35 s
     before the command (before: what BEGINS). The first attempt before it stood
     in the text as a chunk of its own and is now recognised as a remnant.
  2. **The first "Satz wiederholen" counted as "not silent before"** - after a
     five-second pause. Measured offline: the small model places the word start
     about 0.16 s after the sound begins. Margin before the command 0.15 → 0.25
     s; levels are now logged with every such rejection.
  3. **"Kommas" + "Setzen" across a chunk boundary.** Vosk cuts long speech
     even without a pause. If a chunk starts with the second word of a
     punctuation phrase and the previous ended with the first, both are
     processed together; "kommas setzen" counts as a comma.

  **Found and fixed offline along the way:**
  4. **A standalone "Punkt setzen" became "Satz löschen"** - with silence before
     and after, so accepted; the sentence just dictated was gone. Now a
     **cross-check:** the command only counts if the free recogniser heard
     "lösch…"/"wiederhol…" in the same period. In three runs three false
     triggers rejected that way ("punkt setzen" twice, "umsetzen"), all genuine
     commands accepted.
  5. **Without recognised punctuation "Satz löschen" deleted back to the start
     of the text**, salutation included. Now at most the last spoken chunk
     (chunks consisting only of punctuation do not count). First two chunks -
     the next offline run again deleted the salutation with it ("komma neue
     apps" instead of "komma setzen neuer absatz"). The price: a sentence spoken
     across several pauses needs "Satz löschen" several times.

  **Third test (2026-09-15, 13:21), letter without a slip:** two "satz löschen"
  in running text correctly rejected, the "Kommas" merge worked ("komma" +
  "setzen"). Noticed:
  - **The genuine "Diktat beenden" counted as "not silent afterwards"** - only
    the fallback ended it (the free recogniser returned exactly "diktat
    beenden"). Levels are now logged with every such rejection; cause open, not
    guessed.
  - **Anna reported "3 Sätze"** for eight - recognition chunks were counted.
    Sentence ends are counted now.
  - Vosk: "neuer Abschluss" for "neuer Absatz", "kommen ersetzen" for "komma
    setzen" (across a chunk boundary, therefore not merged).
  - Voice control: "Brief erstellen" is not a command, and no suggestion came.
    "Sprachsteuerung beenden" arrived as "welchen"/"windows", only "stoppen"
    worked. **"Brief erstellen" has been a third phrase since 2026-09-15**
    (Stephan's approval, all 29 sentences checked against Piper); test on the
    device after the next login pending. "Sprachsteuerung beenden" stays open.
  - **File names with date and time (2026-09-15, built):** Stephan's choice
    `2026-09-15-1343-Brief.txt/.pdf` and `…-Bildschirmfoto.png`, existing
    files renamed (13 letters, 16 screenshots on the admin account). The user
    account converts itself on the first letter/screenshot. Archive PDFs keep
    their names (not chosen). Test on the device pending.
  - **Personal dictionary (2026-09-15, built):** `~/.config/dialos/
    woerterbuch.txt`, on the device only; created in the admin account with
    Stephan's name and checked against the installed dictation. **Open:**
    entries in the user account (someone logged in there has to create them),
    entries by voice ("Wort merken"?), filling from the customer data (depends
    on their encryption). **Postponed (Stephan, 2026-09-15: the letter and
    entering the customer data come later):** letter test with the name on the
    device, entering the customer data.
  - **Parakeet test in dictation (2026-09-15, built, switch set in the admin
    account):** test with Stephan's voice pending. Then decide: build in for
    good (model to /usr/local/share, sherpa-onnx for all accounts) or drop.
    **Test 14:32 with spoken punctuation: Parakeet 14.9 %, Vosk 9.9 %**
    ("Sätzen"). **Option 3 built (Stephan's choice):** speak naturally,
    Parakeet sets punctuation, only paragraph/line spoken; "12." and "Dr." are
    no sentence end. **Test 14:47 with Stephan's voice: letter practically
    finished** (all punctuation, paragraphs, salutation, closing); word errors
    Vosk 4.9 %, Parakeet 6.2 %, but only Parakeet delivers punctuation.
    **Decided (Stephan):** option 3 for letters and notes, Vosk for commands
    and the shopping list - **after two tests:** freely worded letter, letter
    with a TV playing quietly. Notes in the test since 15:02.
  - **Test bench (2026-09-15, built, recording on in the admin account):** first
    real cases pending. Planned: the same letter with the built-in microphone
    and with the USB desk microphone TONOR TC30, then the two Parakeet tests.
    TONOR is clearly noisier at 100 % (RMS 293 vs 68) - check levels with speech
    before comparing. **Done 15:41:** two cases, Parakeet built-in 2.8 % /
    TONOR 4.2 %, Vosk 12.7 % / 8.5 % (table in docs/diktat.en.md); thresholds
    now follow the noise floor (the TONOR hung before). **Next cases:** freely
    worded letter, letter with a quiet TV - the TV with both microphones. **TV
    done 16:49:** TONOR 4.2 % (same as quiet), built-in 9.9 % with Parakeet.
    **Open:** voice control with the TV - genuine switch-on attempts are
    rejected (fixed limit 3000 for "silent afterwards"), false alarms while
    off. Next step: TONOR and noise floor for the command service on the test
    bench (needs short command recordings with consent, not continuous).
    **Prepared 2026-09-15:** recording with a switch, labelling,
    re-recognition, microphone choice for the service. **Measurement session
    done 17:52** (90 recordings, table in docs/sprachbefehle.en.md): right
    18/21, 17/18, 16/17, 18/19; no executed false trigger; misses almost only
    swallowed beginnings. **2026-09-16: items 1 and 2 built** (recording stays open;
    desktop-look rule limited), installed. First test 12:18: 4/5 on the first
    try; the rest was due to the marker ending 0.64-0.70 s after the sound →
    reader with timestamps, simulated 0/8 → 8/8. **Test 12:48: 6/6 on the
    first try, without waiting.** Items 1 and 2 done. After the faster
    announcements (13:10) Stephan's verdict: **"It is now like a normal
    conversation."** Unresolved: at 13:10:27 "brief als wir" arrived.
    **Fallback answers built (2026-09-16):** standard answer, "Was kann ich
    sagen", honest answers with WUNSCH counting, weather with a fallback place
    and human wording. **Freely dictated letter 13:35: Parakeet 3.4 %, Vosk
    28.8 %** - option 3 confirmed. **Built in for good (2026-09-16, 14:00):**
    `scripts/dialos-parakeet-einrichten.sh` (model to
    /usr/local/share/dialos-parakeet, sherpa-onnx system-wide, checksums,
    self-test), dictation uses Parakeet by default, switch off with
    `parakeet-aus`, both models load at the same time; test bench unchanged
    afterwards (2.8/9.9/4.2/3.4/4.2 %). **Set up on the device, first letter 14:19:**
    loading 12 s instead of 33 s; "Absatz" alone, subject up to sentence end,
    salutation comma, "Cent"→"Euro" added (test bench case `absatz-allein-1`,
    3.8 %). **Open:** test in the user account after re-login; grammar "ein
    Brief geschrieben" (Parakeet, Vosk heard "einen") passes unchecked; date
    following DIN 5008 ("31.08.2026") belongs to the letter work. **Second letter
    14:36:** salutation paragraph, "Betriff", "Yeah.", blank line before closing,
    endings via Vosk+hunspell, Vosk paragraph added (case `absatz-allein-2`,
    4.5 %, all punctuation). Name under the closing ("Stefan Grüßen") → from the
    personal data; numbers ("1229" instead of "12629") remain Parakeet's error. Closing/name lines and subject
    line (bold in PDF and print) built. Open: "-ung" endings with Parakeet
    ("Rechn", "Nebenkostenabrechn"). Place stored in the admin account (wttr.in
    finds it correctly, 47.35/11.20); still missing in the user account. Open:
    test on the device, later free recognition of unknown sentences.
    **New:** announcements not in the cache (every time of day) start speaking
    only 2.3-2.7 s after the call (cached 0.2 s) - warm-up announcement and
    fresh Piper synthesis. **Done 2026-09-16:** generate directly and play,
    1.4-1.7 s. Open: test with a Bluetooth speaker (silence instead of the
    warm-up announcement); a permanently running Piper would save roughly
    another 0.5 s of model loading. **Order afterwards:** 1. close the gap after Anna's
    announcement, 2. desktop-look rule under the extra-word limit, 3. lower the
    TONOR gain (100 % clips), then measure the same 15 commands again. Found: false trigger "auf Windows umschalten" from word salad (old
    desktop-look rule without the extra-word limit) - fix after the
    measurement. **Stephan, 2026-09-15: between Anna's announcement and his
    answer he always has to wait about 1.5 seconds, otherwise the first word is
    swallowed.** Fits the "tag haben wir"/"haben wir" pattern. Cause in the
    service: after every announcement parec is stopped, 0.7 s of reverberation
    waited (NACHHALL_WARTEN_S), plus the 0.3 s polling interval and parec's
    start. Dictation has solved this since 09-14 with the microphone open
    during the announcement and 0.3 s lead-in - build the same here AFTER the
    measurement session (otherwise parts 3/4 are not comparable with 1/2);
    with the raw TONOR without echo cancellation make sure Anna's own words
    ("Der Befehl heisst: …") do not count as a command. **Fundamental question (Stephan):** does DialOS only work in
    silence - and is it therefore unsuitable outdoors? When building it
    in: model (465 MB) and sherpa-onnx
    for all accounts under /usr/local, sort out packaging and licence (model
    CC-BY-4.0, attribution).
  - **"Brief als PDF speichern" proven on the device (2026-09-15, 13:44)**, as
    are "Brief erstellen" and the new closing announcement. And for the first
    time voice control SUGGESTED a command: "als pdf speichern" -> "Der Befehl
    heisst: brief als pdf speichern". **Found and fixed in the same letter:** a
    "Diktat beenden" right after the name (small model: "[unk] diktat beenden",
    no end) stayed at the end of the letter, because only the second one after
    a pause ended dictation. Such a remnant at the end of the text is now
    removed. More from Vosk: "Koffer Absatz", "neue teile" (the second time for
    "neue Zeile"), "Ausrufezeichen" without "setzen" stays a word.
  - **"Brief als PDF speichern" (2026-09-15, built):** Stephan's choice "put
    the PDF where it is visible" and "name all three". Checked offline (PDF,
    empty letter, shopping list, announcement), 30 sentences against Piper.
    Test on the device after the next login pending; the audio samples in
    `docs/sprachbeispiele/alle-ansagen/` do not know the new closing
    announcement yet.

  **Still open, not fixed:** a chunk after a pause always starts with a capital
  ("Ich bitte Sie, Wir diesen Betrag"); a standalone "Punkt setzen" often
  reaches the large model as "und setzen"/"umsetzen" (with Michael offline; with
  Stephan on the device correct so far). **Test with a real voice pending.**

- [ ] **Letter dictated in DialOS (2026-09-15, 11:46) - three program bugs
  found and fixed, proof with a complete letter still pending.**
  Confirmation "ja" on the first attempt; dictation from the letter template
  with spoken punctuation.
  1. **False end in the middle of the text:** the small model heard "diktat"
     (37.92-38.31 s) and "beenden" (39.55-40.19 s) in "…Antwort bis Ende des
     Monats". Stephan could not dictate the last paragraph. **Fixed:** both
     words must follow each other directly (gap at most 0.6 s; here 1.24 s,
     for the genuine end on 09-14 0.00 s).
  2. **"neuer Absatz" at the end of an utterance was lost** -
     `satzzeichen_setzen()` ended with `strip()` and took the "\n\n" along.
     **Fixed:** only strip spaces.
  3. **"neue Zeile" was lost in the letter** - utterances were joined with
     "\n", and the letterhead collapsed every single line break. **Fixed:**
     join utterances with spaces, wrap line by line.
  All three checked offline against the logged values; a letterhead built from
  the spoken sentences now has four paragraphs and the closing on two lines.
  **Open - Vosk recognition:** "rama setzen mit diesem Bit jeden" (komma setzen
  mir diesen), "dr muster", "zweihundert vierzig", "Neuer abstatt";
  Sie/Ihnen/Schreiben lower case. Parakeet recognised the same paragraph with
  one error in the comparison (see recogniser comparison).

- [ ] **Recogniser comparison for dictation: Vosk against Whisper and
  Parakeet - test on 2026-09-15** (Stephan on 2026-09-14: the shopping list
  is still a headache; are there better speech systems - and: commands as
  before, and Whisper for the user's texts?).

  **The split, if the comparison supports it:** commands, yes/no, "später"
  and "Diktat beenden" stay with Vosk (fixed grammar: fast, tightly bounded).
  Only the big Vosk model in dictation would be replaced - for the shopping
  list, notes and letter.

  **Set up (2026-09-14)** with `scripts/dialos-erkenner-einrichten.sh`, for
  measuring only, in `erkenner-vergleich/` next to the repo (nothing in the
  system, no autostart): whisper.cpp v1.9.4 with the models small and
  large-v3-turbo-q5_0, Parakeet TDT 0.6B v3 (CC-BY-4.0, German) via
  sherpa-onnx 1.13.8. All checksums passed, self-test green. Hardware:
  i7-8665U, 4 cores/8 threads, AVX2, 46 GB.

  **Measuring** with `scripts/dialos-erkenner-vergleich.py`: template
  `docs/einkaufszettel-vorlage.md` (20 items + letter text without spoken
  punctuation), one recording, the same pause-cut pieces for every
  recogniser; output: items verbatim, word error rate, load time and time
  per piece. Recordings stay local, never in the repo.

  **Open before any switch:** Whisper sometimes invents text in silence (only
  pass pieces with speech); Whisper does not transcribe while you speak but
  gets finished pieces; the waiting time per item on the T490. Punctuation
  and capitalisation come along with Whisper and Parakeet - commas could
  split entries like "Birnen, Äpfel".

  **Probe with Anna's voice (2026-09-14, 14:26) - pipeline checked, accuracy
  NOT usable.** All four recognisers failed alike on the short items
  ("Bananen" → "fein"/"Dann…"/"Nein."), only long items like "zwei Liter
  Milch" arrived. Cross-check: even uncut and with levelled loudness Vosk
  hears only "ein" in "Bananen.". `kerstin-low` is unsuitable as a speaker for
  single words in free recognition - fine for commands in a fixed grammar.
  **The timings are real, though:**

  | Recogniser | Load | per piece (≈1 s speech) |
  |---|---|---|
  | Vosk big (today) | 11.8 s | 0.30 s |
  | Parakeet v3 | **1.9 s** | **0.26 s** |
  | Whisper small | 12.6 s | **7.05 s** |
  | Whisper turbo q5 | 43.6 s | **40.77 s** |

  **Whisper in this form is too slow on the T490** - presumably because
  whisper.cpp pads every piece to a 30-second window, so compute time per
  piece stays almost the same however short it is. To check: the option
  `--audio-ctx` (shorter window). **Parakeet is as fast as Vosk and loads six
  times faster.** Which one understands Stephan best only his recording on
  2026-09-15 will show.

  **Stephan's shopping list (2026-09-15, 10:36) - VOSK AHEAD.** 36 s, with a
  pause threshold of 0.2 s exactly 20 pieces (at 0.45 s only 14 - he spoke
  briskly, pauses towards the end 0.24-0.45 s, within an item below 0.15 s):

  | Recogniser | Items verbatim | Word errors | per item |
  |---|---|---|---|
  | **Vosk big (today)** | **16/20** | **14.8 %** | 0.25 s |
  | Parakeet v3 | 11/20 | 40.7 % | 0.24 s |
  | Whisper small | 13/20 | 29.6 % | 6.17 s |
  | Whisper small `-ac 512` | 13/20 | 29.6 % | 2.02 s |
  | Whisper turbo `-ac 512` | 13/20 | 40.7 % | 12.99 s |

  **Why:** single words without context are not Whisper's/Parakeet's
  strength. Parakeet drifts into English ("Faz it?", "Rice", "Cacao"),
  Whisper invents ("2 Liter Wildschwein", "Coffee. Coffee.", "Zahnpasta
  Zahnpasta"). Strict scoring also counts spellings ("Brocoli", "Jogurt",
  "500 g") - leniently Whisper small would reach about 15/20, still not ahead
  of Vosk. Vosk's errors: Birne(n), "erzähl" (Äpfel), "Monsterwelle"
  (Mozzarella), "Surimi" (Zucchini) - mostly foreign words. **Conclusion:**
  the shopping-list problems of 09-14 were mostly not Vosk but recording
  start, closing phrase and false end - all fixed on 09-14. One recording, one
  speaker. Open: letter paragraph (whole sentences - where Whisper and
  Parakeet are stronger).

  **Stephan's letter paragraph (2026-09-15, 10:55) - PARAKEET AHEAD.** Second
  recording (the first was interrupted three times by the too-loud
  announcement, see measure B). 40 s, 7 sentence pieces (pause threshold
  0.45 s, longest 9.2 s). Stephan spoke "Komma"/"Punkt" as he is used to in
  DialOS dictation - word errors are therefore computed WITHOUT these words:

  | Recogniser | Word errors | per sentence | Load | disturbed recording |
  |---|---|---|---|---|
  | **Parakeet v3** | **3.0 %** | **0.47 s** | 1.8 s | 37.9 % |
  | Vosk big (today) | 7.6 % | 0.88 s | 9.5 s | 60.6 % |
  | Whisper small | 18.2 % | 5.50 s | 11.6 s | 39.4 % |
  | Whisper small `-ac 512` | 25.8 % | 1.76 s | 6.0 s | 63.6 % |
  | Whisper turbo `-ac 512` | 39.4 % | 13.54 s | 13.4 s | 45.5 % |

  Parakeet: whole paragraph with one error ("teilen das bitte mit"), with
  punctuation and capitalisation; copes with disturbance clearly better than
  Vosk. Whisper: invents (turbo wrote one sentence three times), small dropped
  the last sentence - last in both tests on the T490.

  **Possible split (to decide):** Vosk for commands, shopping list and notes;
  Parakeet for the letter. **Consequence:** Parakeet punctuates itself -
  spoken "Punkt"/"Komma" would give "Muster. Punkt.". For the letter the user
  would then speak naturally, without punctuation commands (simpler, but
  without control over every comma). One speaker, one undisturbed recording
  per kind, quiet room - a clear indication, not proof.

- [x] **Umlaut words are NOT missing from the vocabulary - three decisions
  were open again, all three decided the same day** (found 2026-09-14 when Stephan asked about dialects). Every
  word Vosk reported as "missing in vocabulary" since August contained ä, ö,
  ü or ß. Cause: `json.dumps` without `ensure_ascii=False` turns "ö" into
  `\u00f6`. Passed correctly, the model accepts "später", "löschen",
  "zurücksetzen", "aufräumen", "nö", "tschüss". **Fixed** in all grammars (no
  change in behaviour today - no grammar contained an umlaut word so far,
  precisely because of the wrong finding). **To decide anew (Stephan), each
  with a Piper → Vosk listening test first:**
  1. "später" as the update objection - Stephan's original wish. One word is
     more prone to background noise than two.
  2. "Einkaufszettel löschen" in addition to "wegwerfen"/"Einkauf erledigt".
  3. "Wie spät ist es?" in addition to the two time questions.
  Plus dialect forms for the confirmation ("jo", "joa", "nee", "nö") - see
  the dialect item.
  **Decided on 2026-09-14 after a listening test (Piper → Vosk, Anna and
  Michael):** all three built in. "wie spät ist es" and "einkaufszettel
  löschen" recognised verbatim, all 28 command sentences error-free
  afterwards; "einkaufszettel löschen" is never suggested. "später" for the
  update recognised, "nicht jetzt" with Anna not - "später" is now the
  announced word, "nicht jetzt" still counts. **Open:** test with a real
  voice.

- [ ] **Dialects: Germany, Austria, Switzerland** (Stephan's requirement of
  2026-09-14: the voice control has to be good enough to cope with dialects
  from Germany, Austria and Switzerland). **Situation:** according to its
  README the big model is trained on Tuda-de, SWC, M-AILABS and Common Voice -
  mostly read standard German; Common Voice brings speakers from Austria and
  Switzerland. Swiss German as a dialect is practically not covered.
  **Command recognition is more tolerant than dictation:** it only has to
  choose between 27 sentences. **Nothing has been tested yet** - Piper only
  speaks standard German, so it is no test here. **Proposal:** a test bench
  that sends recorded speech samples through exactly the service's
  recognition and matching and reports the hit rate (the same bench serves B
  and C); recordings of the commands from a few people from AT, CH and German
  dialect regions - with consent, local only, never in the repo; then decide:
  dialect variants in the grammar or a different model (e.g. Whisper - more
  robust with accents, but slower on the T490).
  **Timing, decided by Stephan (2026-09-14): at the very end, once all
  commands are settled.** Otherwise the speakers would have to record again
  after every change. Stephan knows people from Austria and Switzerland for it.

  **What the recordings are integrated for** (Stephan, 2026-09-14: several
  people could provide the commands, and we integrate them into our system -
  then it is integrated cleanly):

  | Use | Benefit |
  |---|---|
  | Test data in the test bench | Hit rate per command and dialect - shows where it fails |
  | Tuning | Dialect variants in the grammar ("jo", "nee" …), adjusting thresholds |
  | Training data for the wake word (measure C) | openWakeWord is trained with many different voices - more speakers from DE/AT/CH make it more robust, including against TV sound |

  **Not planned:** retraining Vosk itself - that needs hours of material, not
  a few dozen recordings.

  **Prerequisite: written consent from every person.** Voice recordings are
  personal data. The consent has to state what the recording is used for
  (testing, training), whether a model trained from it ships with DialOS, and
  how to withdraw it. The recordings themselves **never go into the public
  repo**. The consent template is written when the recordings are due.

- [ ] **The voice service survives logging out - afterwards TWO run**
  (found 2026-09-14, 12:13). After logging out and in,
  `dialos-sprachbefehl-desktop.py` from 11:49 (old version) and from 12:09
  ran side by side, each in its own autostart unit. The log showed
  "anderer Dienst hoert zu" and "fertig" twice each. Two services listening
  can execute a command twice - and after an update the old version silently
  keeps running. The old instance was stopped. **To clarify:** why GNOME does
  not end it at logout (the "manager" session remained), and a single-instance
  lock as in `dialos-start-ansage.py`. Also open whether this played a part in
  earlier tests.
  **Built on 2026-09-14** (Stephan: the voice command has to be reset at
  logout too): at start the service ends every older instance of the same
  account (SIGTERM, SIGKILL after 3 s) - at start rather than at logout,
  because logout is exactly what proved unreliable. Checked with stubs,
  including one that ignores SIGTERM; the running service was untouched.
  **Open:** proof at the next logout/login ("aeltere Instanz beendet" in the
  log, or only one process) - and the cause at logout.

- [ ] **Announcements from other services interrupt dictation** (2026-09-14,
  12:11:29). In the middle of a shopping-list dictation the network monitor
  said "Die Internetverbindung wurde gerade unterbrochen …". Dictation listens
  through echo cancellation, but the user is pulled out of dictating. The
  marker "another service is listening" should also hold back notices like
  this until the dictation has finished.

- [ ] **The customer account `nutzer` has full root rights** (found on
  2026-09-14, when Stephan asked whether the new update rule takes anything
  away from the accounts).

  **The finding.** `sudo -l -U nutzer` says:

      (ALL : ALL) ALL

  `nutzer` is a member of the group `sudo` — alongside `cdrom`, `audio`,
  `video`, `plugdev`, `users`, `netdev`, `scanner`, `bluetooth`, `lpadmin`. So
  with a password the customer account may do **anything**, not just the
  narrowly scoped NOPASSWD calls.

  **Why it is not burning today:** the password was randomly generated during
  setup and is known to nobody. So the door is pulled shut. **It is not
  locked:** whoever sets that password — a helper, a repair shop, somebody with
  brief physical access — has root on the device of a blind user who cannot
  notice it.

  **CLAUDE.md has long listed this as "still open"**, and that wording is
  misleading: it sounds as if nothing had been decided. The actual state is
  **full administrator** — a decision, even if nobody made it.

  **Do not simply remove the group.** What would break is unmeasured. All that
  is measured so far is what DialOS calls through `sudo` as `nutzer` — and that
  is little, because everything runs through NOPASSWD rules on fixed paths:

  | Script | Call |
  |---|---|
  | `dialos-stimme-wechseln.py` | `dialos-stimme.py setzen <voice>` |
  | `dialos-update-lauf.py` | `dialos-systemupdate pruefen/installieren/neustarten` |

  Neither needs the `sudo` group — a NOPASSWD rule works regardless. So the
  suspicion is that the membership was merely carried along because
  `dialos-setup-nutzer.sh` created the account like an ordinary desktop
  account.

  **To settle before anything changes:**
  1. Where does the membership come from? Review
     `scripts/dialos-setup-nutzer.sh` and
     `dialos-buero-setup-abschliessen.sh`. If it is set deliberately there,
     there may have been a reason.
  2. Which of the other groups does `nutzer` really need? `audio`, `video`,
     `bluetooth`, `lpadmin` (printing), `netdev` (Wi-Fi) are plausible;
     `cdrom`, `scanner`, `plugdev` need checking.
  3. What happens to the keyboard shortcuts, remote support and
     `dialos-aufspielen` when it is removed? The latter is for the development
     device only anyway.
  4. **And do not skip the counter-check:** after removal a full run is needed
     — log in, switch voice, update, dictate, print. A loss of rights that only
     surfaces three weeks later is worse than today's state.

- [x] **Automatic updates: built and run on the device - fully proven
  (2026-09-14)** (Stephan's specification of 2026-09-14, built the same day: "Ich
  würde das mit dem Update gerne jetzt einbauen").

  Every 14 days, Mondays after login, with catch-up; ten seconds to object with
  **"nicht jetzt"** ("später" is missing from the model's vocabulary); reboot
  only with the security stick; then "Der Computer ist auf dem neuesten Stand."
  The real run on 2026-09-14 completed, no loop after the reboot. Design,
  reasoning and test record: step 13d in
  [docs/Debian-zu-DialOS.en.md](docs/Debian-zu-DialOS.en.md).

  **Open:**

  1. ~~Stephan's review of the sudoers rule~~ **Done 2026-09-14:** Stephan
     looked at `/etc/sudoers.d/dialos-systemupdate` (checksum device = repo,
     `afa162ca…9ffc`) and approved it: "Ja, ich gebe die Regel frei". The review
     added that `neustarten` only reboots after a real update since the last
     boot. The entry in the NIEMALS list of `dialos-aufspielen` is removed.
  2. **The sentence after the reboot across two accounts, on the device.** In
     the real run only `dialosadmin` (who triggered it) heard it, not `nutzer`.
     Fixed: timestamp on the machine, acknowledgement per person - checked in a
     sandbox with two home directories. There is no timestamp for the 09-14
     run; **at the next real update** log in as `nutzer` first, then as
     `dialosadmin` - both must hear the sentence exactly once.
     **Done on 2026-09-14, 13:26-13:29** - sooner than expected, because the
     firmware update (UEFI dbx) via the automation wrote a real timestamp.
     After the reboot `nutzer` first (autologin): the sentence came after the
     greeting (Stephan confirmed). Then `dialosadmin`: the sentence once,
     13:29:28. Stephan's usual order (always `nutzer` first, then log out and
     into DialOS-Admin) is exactly the one that failed in the morning.

  **To settle on the side:** the voice command "System aktualisieren" is listed
  in `docs/sprachbefehle.md` as planned. It would be a second trigger for the
  same tool - `dialos-update-lauf.py --jetzt` already exists.

- [ ] **Dictate the letter - planned for Tuesday, 2026-09-15** (Stephan on
  2026-09-14: "Punkt 1 bitte auf Dienstag legen"). The template is ready in
  [docs/brief-vorlage.md](docs/brief-vorlage.md): the target, what DialOS can do
  of it today, and the dictation text word for word with the spoken punctuation.
  Nothing to build - it is the missing **proof on the device** that a dictation
  in a real voice runs from beginning to end.

  Worth doing first: `absender.txt` (see section 2 of the template). Otherwise
  the letterhead shows only "Stephan", without street and town.

- [ ] **On 2026-08-24 the voice control could not be switched on once - not
  reproducible on 2026-09-14** - and a level hypothesis is open and untested.

  **ADDENDUM OF 2026-09-14, and it undermines the hypothesis.** At 08:16 and
  08:17 Stephan said "Sprachsteuerung starten" twice and **both times the whole
  phrase arrived** - with the level RESET, because the reboot discarded the
  reduction of 24 August (source back at 32 %, `Capture` at 100 %). The peaks
  were 27663 and 15257, that is, the same range as on the evening when it did
  NOT work.

  **So the level is all but ruled out as the cause.** It was evidently a
  transient state on that one evening. What remains: the item is not solved but
  no longer observable - and that is a difference. Should it recur, the level
  column is now in the log and can be compared against these numbers at once.

  **The finding.** Between 17:01 and 17:06 the log held only `starten`,
  `[unk]` and `sprachsteuerung` - **not once `sprachsteuerung starten`**.
  Thirteen attempts, none successful. So the new announcement never got its
  turn either: it only applies in the switched-on state.

  **The hypothesis, based on the new level column.** Peaks were **21935 to
  30499** out of 32768 - 67 to 93 % of full scale. The service's saturation
  threshold is 32000, so it never fired. But Vosk recognises speech by the
  **pauses between words**; at that level they smear, and two words become one.
  That very mechanism was already the cause on 2026-08-16 - back then through
  "Capture +30 dB AND Internal Mic Boost +30 dB".

  **What was changed on the evening of 2026-08-24 - RUNTIME ONLY, nothing in
  the repo:** the volume of the source `alsa_input.pci-…analog-stereo` from
  35 % to **18 %**. Effect measured: idle level from 52 to **17**, peak from 150
  to 99. The echo source `dialos_mikrofon_ohne_echo` is itself at 100 % and
  inherits from the raw signal, so the control does reach the service.
  **A reboot resets this**, because `dialos-mikrofon-pegel.service` sets
  `CAPTURE_PEGEL="100%"` again.

  **A detour worth recording:** at first ALSA `Capture` was set directly to
  50 %. That dropped the PipeWire volume from 35 to 13 % - the two controls are
  coupled and were moved against each other. It would probably have been too
  quiet. Everything now hangs on one control.

  **Tomorrow, in this order:**
  1. Say "Sprachsteuerung starten". Does the whole phrase come through?
  2. Read the peaks in the log - are they now around 11000 to 15000?
  3. **If it does not help, the diagnosis was wrong.** Then it is not the level,
     and it gets measured differently: record Stephan's voice and check whether
     the pause between "Sprachsteuerung" and "starten" arrives at all. A
     plausible explanation is not yet a cause - that has been the mistake twice
     already in this project.
  4. Only then decide whether `CAPTURE_PEGEL` in the script changes.

- [ ] **Customer data in ONE place - and not unencrypted** (Stephan's prompt of
  2026-08-24: "wo wir zentral alle wichtigen Daten des Kunden einmalig ablegen
  und die Mail, der Brief und das Diktat usw. greifen auf diese Daten immer
  zu").

  **How it looks today.** The same person appears in several places, each with
  its own format:

  | What | Where | Who reads it |
  |---|---|---|
  | Name, spoken and written | `/usr/local/share/dialos/nutzer-name.txt` | startup announcement, letterhead, salutation |
  | Postal address | `/usr/local/share/dialos/absender.txt` | letterhead - **does not exist** |
  | Footer text | `/usr/local/share/dialos/fusszeile.txt` | mail, letter, printout |
  | Mail signature | `mail-signatur.txt` / `.html` | Thunderbird (generated) |
  | Mailbox credentials | a file in `/home/nutzer`, 0600 | mail retrieval |

  **The serious part is not the spread but the location.** Measured on
  2026-08-24:

      /usr/local/share/dialos/nutzer-name.txt  →  /dev/nvme0n1p1  ext4   0644
      /home/nutzer                             →  nvme0n1p4       LUKS

  The customer's name sits **unencrypted and world-readable** on the root
  partition while their letters sit behind LUKS. The postal address is meant to
  go to the same place. With a stolen laptop, exactly what identifies the person
  is readable - and half the purpose of the encrypted home partition is void.
  See `docs/sicherheit-datenschutz.en.md`.

  **A second fault, same location:** the files are system-wide but the data is
  personal. On the development machine `dialosadmin` and `nutzer` share the same
  name - a letter from the admin account would carry the customer's name.

  **To settle before building:**
  1. **Where to?** `/home/nutzer/.config/dialos/` is on the encrypted partition
     and is per-person - both correct. **The boot order is NOT an argument
     against it**; that stood here first and was wrong (corrected 2026-08-24).
     `dialos-stick-gate` runs `Before=display-manager.service`, mounts the
     partition and only then enables autologin - without the stick it even locks
     the account. Whenever `nutzer` has a session the partition is mounted. What
     remains open: the ADMIN account would have no access
     (`/home/dialosadmin` is on the root partition), and the gate itself could
     never read the data should it ever need to speak.
  2. **Which format?** Five files with five formats is today's state. One file
     with clear fields (name spoken, name written, street, town, phone, mail
     address) would be readable and extensible.
  3. **What is NOT customer data?** `assistent-name.txt` (Michael/Anna) and
     `fusszeile.txt` are system settings and do not belong there. That line has
     to be drawn, or everything ends up in one file and nobody knows what to
     delete when the device changes hands.
  4. **What happens on handover?** A device going to a different person must
     shed this data reliably. One central place makes that possible; five
     scattered files make it unreliable.

  **Only after that** is the guided dialogue for recipient and subject worth
  building (see `docs/brief-vorlage.md`): it would otherwise build on a data
  store that is in the middle of moving.

- [ ] **Voice sample at first login - and delete the recording afterwards**
  (Stephan's idea of 2026-08-24: "wenn alles funktioniert, dem neuen Benutzer
  einen Text präsentieren … damit das System eine Stimmenprobe von der Person
  hat, die dann mit DialOS kommuniziert").

  **DO NOT START BEFORE** (Stephan, 2026-08-24): "Das sollten wir ja erst
  angehen, wenn alles mit meiner Stimme reibungslos läuft" - only once
  everything runs smoothly with his voice. That is the right order, and not
  merely for reasons of time: the voice sample MEASURES against the existing
  state. While thresholds, grammar and matching are still changing it measures a
  moving target, and every number it produces would be wrong again after the
  next rebuild. Only once it holds with Stephan's voice is the step to a
  stranger's voice a step at all, rather than a second building site.

  **What it is NOT good for, so nobody builds the wrong thing:** recognition
  does not improve from it. Vosk is speaker-independent and learns nothing from
  a sample; there is no speaker adaptation in this setup.

  **What it is good for: replacing three guessed numbers with measured ones.**
  All three are open items today:

  - **This person's level.** DialOS works with thresholds measured on
    Stephan's voice (speech 3475-4196 against noise 47-84). Anyone speaking
    more quietly falls below them - and then nothing happens, with nobody
    knowing why. See also the item on the missing self-check.
  - **This person's speaking pauses.** Dictation splits entries after a 0.4 s
    pause. That number is **guessed** - it says so explicitly in the "split
    entries" item above. Someone speaking slowly gets their shopping list
    broken into single words.
  - **An acceptance test.** Are all command sentences recognised in THIS
    voice? Today that only emerges once the user is alone with the device.

  **How the text has to be built:** every command sentence exactly once, with
  natural sentences in between for measuring pauses. No longer than a minute -
  reading aloud is an examination for an inexperienced user anyway, and a long
  examination on day one puts people off.

  **The recording is deleted after the measurement** (Stephan's decision of
  2026-08-24). Only the numbers are kept: level, pause lengths, hit rate per
  command. That way no voice recording of the user sits on the device while the
  values DialOS needs are still there. The deletion belongs in the same program
  run as the measurement - a recording deleted "later" stays put.

  **To settle first:**
  1. Where do the numbers go? One file per account, or into the existing
     configuration? They must survive a reinstall, or deliberately not.
  2. What happens when the sample turns out poor - too quiet, too few commands
     recognised? Repeat, try another microphone, or accept it and report to the
     helper? A user who fails on the first attempt must not be left without a
     way forward.
  3. Does it run automatically at FIRST login, or does the helper start it?
     Automatically means the user is tested at first contact, before knowing
     what the device can do.

- [ ] **No self-check on whether the device still speaks at all** (open since
  2026-08-24, surfaced by the muted `paplay`). On 2026-08-24 every `paplay`
  stream was muted because PipeWire remembers that per application. The
  consequence: all **cached** announcements silent, plus the question tone and
  the probe tone. `paplay` returns 0 while doing so, `aus_speicher()` considers
  the announcement successful and does not fall back to `spd-say`.

  **For a blind user this is the worst case there is:** the device is mute, no
  error is recorded anywhere, and he cannot go and look. The cause is fixed
  (see the changelog), but the **class** of fault is not: nothing anywhere
  notices "I spoke, but nothing was audible".

  **To settle before anything gets built:** how can this be measured at all?
  Candidates: check our own stream for `Mute` right after it appears (cheap,
  catches exactly this case), or read the sink's level during the announcement
  (catches more, but is more work and doubtful with headphones). No guessing -
  first find out what PipeWire actually offers.

  **And how would it be reported?** Not by an announcement - that would be
  silent too. What remains: the log, the transcript window, and a visible hint
  for the helper at the next login.

- [ ] **First false start of the voice control - cause unknown** (2026-08-24).
  At 14:41:12 the voice control switched itself on: Vosk recognised
  "sprachsteuerung starten", the transcript window opened, and then came
  "datum vorlesen drucken" and "welchen". **Stephan had not said a word to the
  voice control that day.**

  **What is ruled out:** its own announcement. The audio log holds not a single
  line between 14:35 and 14:42, so DialOS did not speak. The echo cancellation
  was not even called upon.

  **What is open:** what the microphone heard. Ambient speech (a conversation
  in the room, radio, a video) is the obvious guess - but a guess, and this
  project has twice measured past a plausible guess. The first thing to settle
  with Stephan is whether anyone or anything was speaking in the room at 14:41.

  **Why it matters:** the two-word rule exists precisely so that a passing word
  triggers nothing. If ambient speech defeats it, the device can switch itself
  on - window and executed commands included - without anyone addressing it.
  For the blind user the window would be invisible; all he notices is that the
  device is suddenly listening.

- [ ] **Permitted word combinations that form no command fall through
  SILENTLY** (open since 2026-08-22, found during the print test). The most
  serious open item for the target group.

  **What happens.** The restricted grammar is a list of PHRASES, but Vosk turns
  it into a WORD NETWORK and may combine words from different phrases. When the
  result is not a command, nothing happens - and nothing is said either.
  Stephan said "notiz drucken", the grammar only knew "notizen drucken",
  nothing happened, no announcement.

  **Why that is worse than an error.** A sighted user sees a window that does
  not open, or a sheet that does not arrive. A blind user has spoken, the
  device has listened, and nothing tells him that nothing happened. He does not
  even know whether he said it wrong or the device is broken. An error message
  would have been better.

  **Measured on 2026-08-22** across all `~/.log/dialos-sprachbefehl.log*`,
  counting the two states separately:

  | | Count |
  |---|---|
  | Valid commands | 98 |
  | `[unk]` (noise) | 191 |
  | OFF state, no match | 345 |
  | **ON state, no match** | **382** |

  The 345 in the OFF state are nearly all fragments of "sprachsteuerung
  starten". **Silence is correct there and must stay** - that is the two-word
  rule that produced 60 near-misses and, for a long time, zero false starts -
  the first one came on 2026-08-24 (see its own item above). Only the 382 in the
  ON state are the fault.

  **And that is where the dilemma sits:** 382 announcements would be
  unbearable. The device would interrupt every side conversation. The question
  is therefore not WHETHER something is said but WHEN - and a criterion for
  that is missing, one that is measured rather than guessed.

  **What already argues against simply building it:** of the 382, 159 are
  single-word fragments ("wir", "es", "auf", "viel"). That leaves 223
  multi-word ones without `[unk]` - still too many. Among them "haben wir"
  (15x), "die uhrzeit", "welchen haben wir": those are scraps of conversation,
  not attempted commands.

  **Next step, in this order:**
  1. Go through a sample of the 223 with Stephan. Only he can say which of them
     were an attempted command - the log cannot.
  2. Only then settle on a criterion. The level gate from the dictation
     (`PEGEL_SCHWELLE`, speech 3475-4196 against noise 47-84) is a candidate,
     but it distinguishes speaking from silence, not intent from incidental
     talk.
  3. The announcement itself must be short and must not lecture. "Das war kein
     Befehl" is better than a sentence that reads out the whole list.

- [ ] **DEFERRED: rebuild `dialos-hilfe.py` on top of the service** (Stephan,
  2026-08-20: "können den Rustdesk ganz nach hinten schieben, wenn alles
  andere läuft" - RustDesk can go right to the back once everything else
  runs). The two voice commands have therefore been REMOVED from the grammar
  rather than merely left unfinished: the command started the RustDesk
  application, which crashes after 40 s without the service - a voice command
  that half works is worse than one that does not exist. To re-enable:
  uncomment two lines in GRAMMATIK_AN and two in HILFE_SAETZE.
  (Fully prepared on 2026-08-19, just not wired in.) The path is proven and
  the privileged side is written and checked; what is missing is the user
  side.

  **What came out yesterday:** the RustDesk APPLICATION cannot accept a
  connection - without `ipc_service` it crashes after roughly 40 s ("Got
  signal 11 and exit", recorded in the log). Connections are accepted by the
  **service**, and the password belongs to it as well. The decisive
  combination is "service running AND sudo": `sudo rustdesk --password` then
  takes effect; four other combinations had no effect at all.

  **Already built, checked, NOT installed:**
  - `usr/local/sbin/dialos-fernwartung` (root): `starten` switches the service
    on, sets a fresh eight-digit random password, verifies by reading the
    configuration field back that it really is set (the call returns 0 even
    when it had no effect), and prints `id=` and `pw=`. `beenden` changes the
    password - only that makes the one read aloud a genuine one-time password
    - and stops the service.
  - `etc/sudoers.d/dialos-fernwartung`: both calls verbatim, no wildcards,
    `visudo -c` reports it parses cleanly. Must be installed 0440 root:root.

  **What is left to do, in this order:**
  1. Have Stephan review both files - a sudoers rule is a security decision
     and should not be installed unseen.
  2. `dialos-hilfe.py`: replace `rustdesk_pids()` with
     `systemctl is-active rustdesk`. The application is no longer started at
     all, so the crash disappears.
  3. `starten()`: call `sudo /usr/local/sbin/dialos-fernwartung starten`, read
     `id=`/`pw=`, hand them to `nummern_sprechen()`. `einmalpasswort()` then
     stops being a placeholder.
  4. `beenden()`: `sudo ... beenden` instead of SIGTERM on processes.
  5. The watchdog then checks the service rather than the processes.
  6. After that: a real connection attempt from Stephan's second computer -
     which at the same time supplies the signature the idle detection is
     missing (separate item below).

  **Loose end:** since Stephan's test on 2026-08-19 there is an eight-digit
  random password in `/root/.config/rustdesk/RustDesk.toml` that nobody knows.
  That is harmless - the service is stopped and `disabled` - and the first run
  of `dialos-fernwartung starten` overwrites it.

- [ ] **A real one-time password for remote support, as soon as RustDesk
  allows it** (open since 2026-08-19). Five routes checked, all closed - the
  list is in `docs/sicherheit-datenschutz.en.md` so that nobody works through
  them a second time: the one-time password is in no file; `rustdesk
  --password` has no effect as the user, with the application running, with
  the service running, or as root; `--get-temp-password` does not return even
  after 40 s; `rustdesk-utils` is missing from the package; writing the
  encrypted value ourselves would be guesswork. Worth watching:
  [rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074). Until
  then it is the RUNTIME that guarantees the limit, not the password.

- [ ] **Idle detection for remote support** (open since 2026-08-19). The time
  limit is absolute (one hour), although idleness would be the right
  semantics: the risk is a remote session left open with NOBODY on it. Cutting
  off an active session would be harmful, in the middle of an update for
  instance. Why it is not built yet: nobody has ever connected to this device,
  the signature of an active connection is unknown, and guessing it would be
  the worse mistake. `dialos-hilfe.py` therefore notes the process count and
  the size of RustDesk's log for every session (`spur_notieren`).
  **Next step: NO test of its own needed** (Stephan, 2026-08-20: "da ich an
  anderer Stelle Rustdesk täglich benutze, brauchen wir da nicht wirklich
  einen Test machen" - he uses RustDesk daily elsewhere). He is right - what
  is missing is not proof THAT RustDesk works, but the signature of an active
  connection ON THIS device. It will arise by itself at the next ordinary
  support session: `spur_notieren()` records the process count and log size
  each time. After that it is in the log and the detection can be built on
  evidence.

- [ ] **Split entries when the user speaks without "und" in one go** (open
  since 2026-08-19). "Milch sechs Eier Butter" in one breath stays a single
  entry: Vosk delivers one utterance, and one utterance is one entry. Two
  simple routes are handled so far - a short pause (now announced) and the
  word "und" (which splits). The reliable route would be the **word
  timestamps** that Vosk supplies with `SetWords(True)`: a gap of more than
  roughly 0.4 s between two words is a split point, even when it is too short
  to end the utterance. The threshold needs measuring - 0.4 s is guessed, not
  measured, and chosen too small it would break "sechs Eier" into two entries.
  Applies to `LISTEN_ZIELE` only, not to letters.

- [ ] **The timezone does not follow the location - and a blind user cannot
  change it** (noticed 2026-08-19 on Stephan's question "does the time
  follow the actual location?"). Measured: `Time zone: Europe/Vienna`,
  `automatic-timezone: false`. The timezone is chosen per device at setup
  (build recipe step 1). In Berlin or Munich the announcement is still
  correct because the same zone applies - travel to another timezone yields
  a wrong time.
  - **If automatic, then with an announcement.** A silent change would shift
    all times inexplicably for a blind user, appointments included. The
    announcement is what makes it acceptable at all - not the change itself.
  - **For a timezone the imprecise fix is good enough.** The 26 km that are
    useless for weather are irrelevant here: a timezone needs country-level
    accuracy. Near the border it might become Europe/Berlin instead of
    Europe/Vienna - both have the same offset, the spoken time would be
    identical.

- [ ] **Weather on request would need a fallback location** (removed
  2026-08-19, reasoning at the top of `dialos-auskunft.py`). The command
  cannot work at the site of use, because beaconDB does not know the Wi-Fi
  networks there and only returns an IP estimate (Vienna, 26 km). It could
  be brought back with a configured location that steps in **only** when the
  fix is too coarse - in mapped cities the real fix still wins. Stephan's
  objection was justified and is answered: Berlin would stay Berlin. The
  case that goes wrong is a holiday in the countryside - the announcement
  would be stale, but **audibly** stale, because it names the city.

- [ ] **Judge Anna in everyday use** (open since 2026-08-20, Stephan: "das
  werde ich aber erst mit der Zeit mitbekommen" - he will only notice over
  time). Two things are measured but not yet proven in everyday use:
  - **Tempo 0.95** - decided on 2026-08-22 by ear, the same way Thorsten's
    0.88 was at the time. Stephan listened to 1.00, 0.90, 0.80 and 0.95 one
    after another ("0,95 ist super bei Anna! Die ist beschlossen!"). That was
    a verdict on a few sentences; whether it carries across a long text will
    only show in everyday use. Changing it is a one-liner:
    STIMMEN["kerstin"]["tempo"] in dialos-stimme.py, then `setzen kerstin`
    again.
  - **Pronunciation rules have been per voice since 2026-08-24** - the
    structural question raised in this item is answered, and by the first real
    case: Anna says "Dial O S" for "DialOS" while Michael stays with "Dial OS"
    (Stephan's choice, by ear). Every rule now has a fourth field naming the
    voices it applies to.
    **"Tas tatur" and "Ei Di" were confirmed on 2026-09-14** - both played in
    Anna's voice, inside the real sentence ("Akku-Stand Tastatur: achtzig
    Prozent." and "Die Fernwartung laeuft. Die ID ist: ..."), each with and
    without the rule. Stephan's verdict: "mit Regel" - keep them. No code
    change needed, the rules already applied to every voice - and so they need
    NO per-voice field either, contrary to what still seemed possible during
    the rebuild on 2026-08-24. Pronunciation is thereby fully decided for both
    voices.


- [ ] **Add a second voice early, the selection only at the end**
  (Stephan's question, 2026-08-18: "When do we want to add the other voices,
  e.g. a woman's?"). Split, because these are two different things:
  - [ ] **Early (about an hour):** install ONE female voice
    (`de_DE-eva_k-x_low`, `kerstin-low` or `ramona-low` - the configuration
    already knows them, only `thorsten-high` is installed) and check exactly
    three things that could change the architecture:
    - **`stimmen[0]` in `dialos-say.py` line 129 is a bug** as soon as there
      are two voices: the announcement cache takes the first file in the
      directory, not the configured voice. It must read the configured one.
    - **Tempo per voice?** 0.88 was chosen for Thorsten by ear. If it does
      not fit a female voice, the tempo has to become per-voice - which
      changes the structure of `piper-generic.conf`.
    - **Check the pronunciation rules:** "Tas tatur" instead of "Tastatur"
      is tuned to Thorsten. Another voice may not need the split.
    - **Side finding:** in `piper-generic.conf` all ten German voices are
      registered as `MALE1`, including the female ones. Selection by voice
      type therefore does not work.
  - [ ] **At the end:** the selection for the user - speakable by voice,
    remembered across a restart. Needs a settings mechanism that does not
    exist yet, and all announcements in their final state.
  - **The justification for this split is line 129 itself:** such
    assumptions accumulate while there is only one voice. Finding them all
    at once at the end is the expensive way.

- [ ] **Two dictations recorded nothing on 2026-08-18 - not seen again since,
  cause never found** (the "FIRST THING TOMORROW" label was removed on
  2026-09-14).

  **Addendum of 2026-09-14, from the admin account's logs.** Dictation was
  recording again the next day: on 2026-08-19 "milch sechs eier butter" three
  times into the shopping list, once as three separate utterances, then
  "vorlesen: 3 Eintraege" and two successful clears; on 2026-08-21 two notes
  with text. Runs without an `erkannt:` line still occur, but they take only
  3 to 8 seconds until the stop phrase - tests of the stop phrase, not a lost
  dictation. **Not solved, just not observed any more.** The next real proof
  is the letter on 2026-09-15: if it runs through, this item gets ticked; if
  it stays empty, the questions to check are here.

  The original finding (2026-08-18, last run). In the log `~/dialos-diktat.log` there is **not a
  single** `erkannt:` line between "grosses Modell geladen" and "Schlusssatz
  erkannt" - on the second run across 26 seconds. The shopping list stayed
  empty, so "Einkaufszettel vorlesen" and "Einkauf erledigt" were never
  executed (`~/dialos-notiz.log` is empty). **Deliberately no conjecture
  recorded** - none is evidenced. What to check: whether two simultaneous
  `parec` on the same source interfere (the command service keeps reading
  even while discarding), whether the stop recognizer takes the blocks from
  the big one, and whether anything was spoken at all - clarify with Stephan
  first what he said.

- [ ] **Applications: scope approved on 2026-08-18.** Full list with
  reasoning in `docs/anwendungen.en.md`. Settled are Firefox, Thunderbird
  (mail/calendar/contacts), RustDesk, Shortwave (radio), Rhythmbox
  (music/podcasts/audiobooks), LibreOffice Writer (letters), notes as text
  files, Jitsi in Firefox (video chat), unattended-upgrades. To build, in
  a sensible order:
  - [x] **Dictation (speech to text) - working since 2026-08-18.**
    `dialos-diktat.py`, evidenced live in Stephan's voice. Details in
    `docs/diktat.en.md`, installation in `docs/Debian-zu-DialOS.en.md` step
    11h. What is still missing:
    - [ ] **Startable by voice.** So far only from the command line. The
      command has to start the dictation from within the command service -
      and silence its own recognition, which the marker already handles.
    - [ ] **Punctuation.** Vosk delivers none. The classic route is spoken
      punctuation ("Komma", "Punkt", "Absatz"); what needs checking is
      whether they can be told apart from identical words in the text.
    - [ ] **One line per entry.** Vosk only cuts at a pause in speech;
      without a pause everything lands in one line. For a shopping list one
      line per entry would be better.
    - [ ] **Letters:** 98.1 % casing is enough for notes and mail. For a
      letter to the health insurer it must be decided whether that suffices
      or whether it has to be checked before sending.
  - [ ] **Reading out** mails, documents and web pages.
  - [ ] **Radio and music by voice** - Shortwave by station name,
    Rhythmbox via `rhythmbox-client`. Implement the one-player rule while
    doing it: stop one before starting the other.
  - [ ] **Resume position for podcasts and audiobooks** - Rhythmbox does
    not provide it (checked: no `playback-position`, no `bookmark`). DialOS
    reads and sets it over MPRIS and must be able to announce it.
  - [ ] **Scanning post and reading it out** - install `tesseract-ocr`
    (5.5.0); simple-scan/sane/CUPS are present.
  - [ ] **Alarm, timer, reminders.**
  - [ ] **Shutting down and locking the computer by voice**; **announcing
    appointments and weather** (Thunderbird resp. the existing weather
    query).
  - [ ] **Updates:** set up `unattended-upgrades` (security updates
    automatically) and, separately, the voice command with a yes/no
    confirmation for anything larger.
  - Still open, do not build: **telephony** (deferred, depends on the
    hardware decision), **chat** (WhatsApp per `telefonie.en.md`,
    confirmation missing), **video recording** (purpose unclear).

- [ ] **Next block: the applications** (Stephan, 2026-08-17). So far it
  has been foundations - speech output, recognition, audio routing, desktop
  look. Next up is which programs DialOS ships and how they are operated
  by voice. **The entry point is the "Planned, not built yet" table in
  `docs/sprachbefehle.en.md`** (radio/music, call for help, system
  maintenance, telephony) - do not start a new list, work through the
  existing one and follow the rules from that same file for every new
  command.

- [ ] **Unexplained: the Bluetooth sink suddenly stood at 70 %**
  (2026-08-17). Between two measurements the AIRHUG's volume changed from
  100 % to 70 % without DialOS having done anything. Three explanations are
  refuted: the device does not report its volume (tested on button press
  with no audio, on playback start, and on button press **during** an
  active playback - no change in all three), WirePlumber's stored value is
  100 %, and the event log shows no re-creation of the sink in the relevant
  window. **Deliberately no fourth guess** - recorded so that a second
  occurrence yields a second data point. It matters because a volume that
  changes by itself is not comprehensible to a blind user.

- [ ] **Decision open: announcements quieter than music** (Stephan's wish
  of 2026-08-17, "throttle by about 30 %"). On the laptop speaker it is
  doable - signal attenuation works there, confirmed by Stephan by ear. On
  the AIRHUG it does **not**: it undoes the attenuation (measurement in
  `docs/Debian-zu-DialOS.en.md`, step 11g), only the device volume works
  there, and that applies to everything. One option would be to lower it
  briefly via AVRCP **during** the announcement; such a command costs a
  measured 19-36 ms, negligible against a 1200 ms announcement. Open is
  whether lowering it audibly steps or clicks on the device - that decides
  whether it is usable. After Stephan set the volume on the device, the
  question may be moot anyway.
  - **To fix along with it:** `GenericVolume` is ineffective in DialOS,
    because the sox chain ends in `norm` and cancels any attenuation
    before it. Anyone wanting to control the volume through
    speech-dispatcher must write `norm vol <factor>`.

- [ ] **Roadmap to real voice control** (agreed with Stephan on
  2026-08-16, in this order):
  1. Decide on a reference microphone - **done**, AIRHUG 01.
  2. **Windows 11 desktop switch** - **built on 2026-08-16**, live test
     still pending (see next item).
  3. Wake word + continuous listening loop - **partly done on
     2026-08-16**: the listening loop runs
     (`dialos-sprachbefehl-desktop.py`), a wake word does not exist yet.
     It hasn't been missed so far, because the restricted grammar only
     admits three fixed sentences.
  4. hassil command grammar - **the desktop switch as the first real
     voice command was done on 2026-08-16**, though directly via a Vosk
     grammar rather than hassil. hassil only pays off once there are
     several commands with variants.

- [ ] **Guard the Bluetooth profile against getting stuck** (open since
  2026-08-17). After the restart the AIRHUG was on `headset-head-unit`
  instead of `a2dp-sink` - playback ran permanently at phone quality,
  without anyone unfamiliar with the device noticing.
  `dialos-start-ansage.py` deliberately switches to HFP for the volume
  question and back afterwards; if the script ends before that (abort,
  logout, timeout) the profile stays. What is needed is a guard that
  works independently of the script finishing - e.g. a check at login or
  a `trap` on script exit.

- [ ] **Build the wake word with openWakeWord** (decided 2026-08-17).
  The Vosk grammar is ruled out - it forces every utterance into the
  nearest phrase, which is why "ich rufe michael an" came through as
  `hallo michael`, and with full confidence at that (conf 1.00). So a
  threshold does not separate. The wake phrase should be the assistant's
  name ("Hallo Michael", or "Hallo Anna" with a female voice), read from
  the same setting as the voice selection. Details in
  `docs/sprachsteuerung.en.md`.

- [ ] **Record a demo video with voice input and output** (Stephan's
  idea of 2026-08-16, for the next working day). It should show what
  DialOS can actually do today: the login announcement with the volume
  question, then "auf Windows umschalten" / "auf Linux umschalten" by
  voice. The open question is the audio capture - the screen alone is not
  enough, both the system's speech output and the spoken input have to be
  audible. `wf-recorder` or OBS with two audio tracks (system sound +
  microphone) would work; neither is installed yet. **Careful with the
  microphone choice:** the voice-command service listens on the built-in
  microphone so the AIRHUG stays in A2DP - recording via the headset
  microphone would drag playback down to phone quality and make the video
  sound worse than the system actually is.

- [x] **Reference audio device decided (Stephan, 2026-08-17): two
  devices.** The AIRHUG stays as the speaker in A2DP, plus a wireless
  microphone with a **USB** receiver for input - deliberately not a
  second Bluetooth device, which would bring back the HFP trap.
  Requirements and candidates in `docs/hardware.en.md`.

- [ ] **Obtain an inexpensive Bluetooth microphone to try out**
  (Stephan, 2026-08-17 - the test decides the design). Bluetooth has one
  advantage USB does not: **DialOS sees the battery level** via BlueZ and
  can warn before the microphone goes flat. Against it stands a risk that
  can only be settled on the device: a permanently open HFP link
  continuously consumes airtime on the same adapter the AIRHUG plays
  through - A2DP may stutter.

  **Test plan:** pair it, run the radio through the AIRHUG, point the
  voice service at the Bluetooth microphone, and listen for stutter.
  Additionally: range across the flat, battery level appearing in the
  login announcement, recognition quality against the built-in
  microphone, and whether echo cancellation still suffices when the
  microphone lies **next to** the speaker rather than far away.

  If the test goes badly, the fallback is a USB wireless microphone
  (candidates in `docs/hardware.en.md`) - but then without a battery
  indicator, and it must be clarified before buying whether the
  transmitter can run permanently from a power supply.

- [ ] **Detect when the microphone stops delivering** (2026-08-17, to be
  built regardless of the device choice). The voice service measures the
  level continuously anyway. If **nothing at all** arrives for minutes
  even though the source is present, it should say so: "I can't hear
  anything from the microphone any more." That does not replace a battery
  indicator but catches exactly the failure that would otherwise leave
  the user clueless - they would be talking to a dead device without
  noticing. Careful with the threshold: silence in the room is normal, a
  permanently **exact** zero level is not.
  - **On 2026-08-17 the task grew beyond what it was meant to be - the
    case occurred and took the entire audio output with it.** Echo
    cancellation was pointed at the USB headset for testing; at reboot
    its link was not there. The dongle still offers a sound card, ALSA
    even reports `state: RUNNING` - only 0 bytes arrive. Because the
    module needs that capture as its clock, PipeWire no longer started
    the graph, and **nothing** in the system could play audio, not even
    through the built-in speakers. Details in
    `docs/Debian-zu-DialOS.en.md`, step 11f.
  - **So there are two things hanging on this, not one.** (1) The
    announcement when the microphone goes quiet - as above. (2) A
    safeguard that drops echo cancellation instead of taking the audio
    down with it. As long as the target is the built-in microphone the
    case cannot occur; as soon as an external wireless microphone is to
    become the standard - and that is planned - (2) is a precondition,
    not an accessory.
  - **To investigate:** whether PipeWire itself offers a way to keep a
    silent source from becoming the clock would be the clean route.
    Otherwise a service has to check the target before loading (test
    `parec` for bytes) and only then hook cancellation in.
  - **And the finding that makes this hard: there is no reliable
    indicator.** After unplugging and replugging the dongle the same
    device delivered 64000 bytes instead of 0. Stephan explicitly noted
    that **before** replugging, the headset had reported an established
    connection to him, via the dongle too. So: the headset reports
    connected, the dongle offers a sound card, ALSA reports
    `state: RUNNING` - and still 0 bytes arrive. My first reading ("the
    link was not up") was therefore wrong. **Consequence for the
    safeguard:** it must not rely on any status report, neither the
    device's nor ALSA's. Only the bytes that actually arrive count.

- [x] **How the task was worded before (for provenance):** What is measured:
  the device cannot sound good and listen at the same time (A2DP has
  `sources: 0`), its buttons reach the laptop on **neither** channel -
  not as key codes, not as AVRCP volume - and its volume is decoupled
  from GNOME. That rules out the workaround of briefly switching to HFP
  by button. Three options, see `docs/hardware.en.md`: two devices
  (microphone permanently in HFP with the user, speaker in A2DP), a
  different speaker whose buttons get through, or the requirement that
  the laptop be in the same room.

- [x] **Clarified on 2026-08-17: the volume decoupling applies in one
  direction only.** The computer can control the AIRHUG perfectly well
  (10 % vs. 100 % unmistakable by ear); only its own buttons don't report
  back. My first assessment ("DialOS cannot control it at all") was an
  overstatement. Not a disqualification.

- [ ] **Residual risk from this:** DialOS does not know the volume set on
  the device. If someone has turned the AIRHUG down by hand, "louder"
  only helps while the software volume still has headroom - at 100 % it
  stays quiet, and the cause lies outside the system. Worth considering:
  should DialOS detect this case (software at 100 %, user keeps saying
  "louder") and say that the device itself needs turning up?

- [ ] **Repeat the microphone comparison of 2026-08-13.** Back then the
  built-in microphone was judged clearly inferior to the AIRHUG. On
  2026-08-16 it turned out that 60 dB of gain were applied out of the box
  and the signal was permanently clipped - so the test probably did not
  measure the microphone but the clipping. Until this is repeated, the
  rationale for the Bluetooth priority rests on shaky ground.

- [ ] **Visual sign-off of the Windows look after logging in** (open
  since 2026-08-16). The settings are demonstrably correct, but nobody
  has actually seen them: the extensions only take effect after logging
  out and back in once. To check: taskbar at the bottom with centered
  icons, ArcMenu start menu on the left in the Windows 11 layout, window
  buttons on the right, window snapping at the screen edge. Then run
  `dialos-desktop-stil.sh gnome` and verify everything really looks like
  before. Afterwards the same as `nutzer`.

  **As of 2026-09-14 - largely signed off as `dialosadmin`.** Stephan switched
  and sent screenshots:
  - ☑️ Taskbar at the bottom, icons centered, start button on the left.
  - ☑️ Start menu - after two rounds of tidying: the pinned items were
    ArcMenu's defaults, including an empty slot (`firefox.desktop` does not
    exist on Debian) and an overflowing grid. Now six everyday programs as
    large icons, three per row, "Frequent" off, list without letters. Labels
    are left-aligned under centered icons - not configurable in ArcMenu,
    Stephan: leave it.
  - ☑️ Window buttons on the right (minimize, maximize, close) - visible on
    the Claude window in the screenshot.
  - ☑️ Back to GNOME: Stephan says it looks like before; checked that every
    key DialOS sets is back at its default and the three extensions are off.
  - ☑️ Window snapping at the screen edge: Stephan says it works - checked in
    the Windows look (tiling-assistant active, GNOME's own `edge-tiling` off at
    the time, so it really was the extension).
  - ☐ **Open:** the whole round as `nutzer`.

- [ ] **Test the microphone fallback without Bluetooth** (open since
  2026-08-16). The output side is proven - headset off, sound came from
  the built-in speaker. The input side is still missing: does the
  built-in laptop microphone understand the volume question?

  **Important, or the test appears to fail:** since 2026-08-16 the
  question is only asked once. Delete the remembered value first,
  otherwise nothing is asked at all:

  ```bash
  sudo rm /home/nutzer/.config/dialos/lautstaerke
  ```

  Then switch the AIRHUG **off**, log out and back in as `nutzer`, and
  answer into the laptop microphone.

  **Expectation:** noticeably worse than over the headset - the
  comparison test of 2026-08-13 was unambiguous (6 of 8 test sentences
  correct over Bluetooth, clearly fewer with the built-in mic). For a
  fallback it is enough that it works *at all*: it only has to prevent a
  user without a headset from being unable to do anything. If nothing is
  understood, the 100% fallback applies - the announcement stays audible,
  but the user could no longer change the volume themselves.

- [ ] **Check the speaker's German firmware prompts** (open since
  2026-08-16, Stephan's requirement a). This means the device's own
  prompts ("connected", low battery), not those of DialOS. For a blind
  user they are the **only** feedback received from the device
  independently of the laptop - a misunderstood battery warning means
  output fails without notice. Standard Bluetooth profiles offer no
  remote control for this; it depends purely on the device. Not yet
  checked on the AIRHUG.

  *(The earlier wording of this item named the AIRHUG as the sole
  reference device. That is superseded since 2026-08-17: there are two
  devices, see above and `docs/hardware.en.md`.)*

- [x] **DONE on 2026-08-16 - the complete flow has run on real
  hardware.** Result: a freshly installed Debian 13 became a running
  DialOS. Proven: encrypted swap (comes up on its own at boot, evidenced
  by the journal), `dialos-nutzer-home` at 374.9 GiB, autologin for
  `nutzer`, audible speech output, German keyboard, and **both directions
  of the stick gate**: without the stick a login screen requiring a
  password and a closed LUKS container, with the stick a clean autologin
  including announcements. Also confirmed live: the new volume logic -
  announcement, then the question, spoken "25" recognized and stored
  permanently. Eight faults surfaced along the way that no dry run would
  have found (details in README changelog 0.5.0). Original entry:
  completely reinstall the T490 and use it to really
  test the whole new flow (never run end-to-end yet): install Debian 13
  + GNOME manually (step 1, **with** the partitioning note documented
  since 2026-08-14 - 100 GB root, deliberately leave the rest of the
  disk free) → `scripts/dialos-full-office-setup.sh` (steps 2-12 + 15
  automated) → new `dialos-setup-home-partition.sh` (sets up the
  `dialos-nutzer-home` partition + security stick in the free space,
  replaces `dialos-install`'s whole-system copy for this flow) →
  `scripts/dialos-buero-setup-abschliessen.sh` (create `nutzer`).
  Afterward, as Stephan planned: build out speech recognition/voice
  commands step by step on real hardware and keep extending the install
  routine.
  **Groundwork done 2026-08-16:** both scripts were reviewed against
  `docs/Debian-zu-DialOS.en.md` before the first run, cross-checked live
  on the freshly installed T490, and the faults found were fixed (details
  in README changelog 0.5.0). The flow now consists of exactly three
  commands; the manual work from doc step 13 lives in
  `dialos-buero-setup-abschliessen.sh`.

- [ ] **Deferred (Stephan, 2026-08-16):** **Run `dialos-claude-setup.sh`
  on the freshly installed T490.**
  Checked 2026-08-16: `credential.helper` is unset, `~/.git-credentials`
  is missing, `/etc/sudoers.d/` contains only the README, and `~/DialOS`
  does not point at the repo on the external drive. So the script has
  never run on this system - `git push` would prompt for credentials and
  the `eggs produce` NOPASSWD rule is absent. Stephan has to do this
  himself (no script accepts the GitHub token).

- [ ] **Deprioritized, no longer the next step** (see the two new items
  below): Run a real live-boot test with `DialOS-Live-0.5.0-clone.iso`
  (supersedes the old, now outdated live-boot-test item for the 11.08
  ISO): before running `dialos-install`, check via `gdbus` whether
  `dialosadmin`/`nutzer` came along with the correct autologin status
  (see docs/sicherheit-datenschutz.en.md, section "Automatic login");
  then run through `dialos-install` completely with the security stick -
  unplug the external SanDisk-Extreme drive first (otherwise it's
  selectable as the target disk!); verify the new stick partitioning
  (`DIALOS-KEY` 2 GiB + `DIALOS-DATA` ext4).

- [x] **Moot since 2026-08-16:** `dialos-install` has been dropped
  entirely (path A). This entry's checkpoints were covered by the new
  flow instead and all passed - see the completed entry above.
  Originally: run a complete `dialos-install` installation
  with the new home-partition design on real hardware (T490) (see
  docs/sicherheit-datenschutz.en.md, section "Encrypting nutzer's data +
  security stick", for the full design). Check: ~100 GiB unencrypted
  root partition boots normally; `dialos-nutzer-home` (LUKS2) gets set
  up correctly during office setup; `dialos-setup-nutzer.sh` aborts
  cleanly without the stick plugged in instead of creating `nutzer`'s
  home on root; after setup: unplug the stick + reboot → normal GDM
  login screen, `/home/nutzer` empty/unmounted; plug the stick back in +
  reboot → `/home/nutzer` mounted, autologin works. Also verify
  `DIALOS-KEY` (now ext4, no longer FAT32) and `DIALOS-DATA` (now
  exFAT, no longer ext4) on a 64 GB stick. **Partially done already
  (2026-08-14):** the plain stick partitioning was manually tested
  (not via `dialos-install` itself, but by hand with the same commands)
  against a real 59.8 GB USB stick - `DIALOS-KEY` (ext4, root:root 755,
  neither readable nor writable for regular users - stronger protection
  than planned) and `DIALOS-DATA` (exFAT, writable for the current user)
  were created correctly. **Still open:** mount and write-test
  `DIALOS-DATA` on a real Windows machine (only verified on Linux so
  far).

- [x] Fundamental decision made (see above, implemented 2026-08-14):
  whole-disk LUKS encryption is gone entirely, replaced by a dedicated
  `dialos-nutzer-home` partition + the `dialos-stick-gate` gate.
  `dialos-install`/`dialos-rekey`/`dialos-stick-gate.sh` rewritten
  accordingly, dead `dialos-keyscript` initramfs files removed.

- [ ] The Piper voice's speaking rate should be individually adjustable
  by the user (currently hardwired via `GenericRateMultiply` in the
  Piper config, `0.85` chosen as Stephan's personal preference) - needs
  a real setting (e.g. GNOME accessibility settings or a dedicated voice
  command), not just a config value.

- [ ] The Bluetooth audio fix in `dialos-start-ansage.py`
  (single-instance lock/`alte_instanz_beenden()`) hasn't been
  conclusively confirmed over a longer period yet - check
  `/tmp/dialos-bluetooth-debug.log` if the problem recurs.

- [ ] **Own server for dialos.org, Nextcloud, forum, RustDesk relay and
  video conferencing** - sponsorship unsuccessful so far.

  **Status.** Hetzner approached on 2026-08-17, follow-up question about
  the concrete infrastructure on 2026-08-18, answered with specifics on
  2026-08-25 (AX42, 24 months, including an offered quid pro quo),
  closing mail on 2026-09-05. webgo approached as well; the request
  ended up in their support ticket system (#48345) and was answered on
  2026-08-25 asking for it to be forwarded to sales or management.
  Neither had replied on the merits as of 2026-09-05.

  **What it actually costs.** The need is smaller than what was
  requested: a netcup RS 4000 G12 (12 vCores, 32 GB, 1 TB NVMe) at
  roughly EUR 34 net per month covers the website, Nextcloud, forum and
  RustDesk relay. Only regular group video conferences would need more.
  The full provider comparison with prices and links is on Stephan's
  desktop as `DialOS-Server-Anbietervergleich.docx` - deliberately not in
  the repo, because it contains the history of the requests.

  **There is no widespread "free server for open source" programme among
  the German providers** - server.camp and Hostsharing eG are regular
  paid offerings with an open-source focus, not sponsorship. Hetzner's
  approach ("on an individual basis") is already the usual model.
  Approaching one provider after another only prolongs the pattern.

  **An Austrian location needs no change of provider:** netcup runs its
  own datacenter in Vienna and the location is selectable when ordering.
  For comparison, what a purely Austrian provider costs - WUKOTEC
  (Vienna) offers the PS 4000 G12 with exactly the same specification and
  the same naming scheme as netcup's RS 4000 G12, but at EUR 57.56
  instead of 39.92 gross, roughly 44 % more.

  **Sent on 2026-09-09:** a request for a quote to web-crossing GmbH
  (Innsbruck, DC3 datacenter, info@web-crossing.com, phone +43 512
  206567, managing directors Ing. Martin Ennemoser and Stefan Ennemoser)
  with concrete target specifications - deliberately framed as an
  ordinary customer enquiry rather than a sponsorship request, with the
  partnership idea only in the closing paragraph. Plus an enquiry to
  netcup about whether they offer terms for open-source projects (netcup
  publishes no general contact address; the route is the contact form or
  a ticket in the customer account). Await replies; if nothing comes,
  book regularly.

- [ ] **Waiting list: funding programmes** - a far bigger lever than
  server sponsorship, because the bottleneck for DialOS isn't the server
  (about EUR 34 per month) but hardware, time and later certification.
  Research status 2026-09-09.

  **The legal form decides everything else.** As a private individual
  almost nothing is accessible - the sole exception is netidee. A
  non-profit association opens up Licht ins Dunkel and comparable funds,
  founding a company opens up the FFG. That is the real fork in the road
  and a decision with consequences far beyond funding.

  **netidee (Internet Foundation Austria)** - up to EUR 60,000, strictly
  open source, **private individuals resident in Austria are explicitly
  eligible**. Accessibility projects have been funded there before (among
  them an accessible job search for people with disabilities). The
  deadline for Call 2026 was 2026-07-07 and has passed; the next call is
  expected in summer 2027. That timing actually works well, because
  DialOS will be considerably more mature by then. The best thematic fit.

  **FFG Impact Innovation Social** - the largest single item: 70 % of
  eligible costs, max. EUR 105,000 as de minimis aid, explicitly for
  social innovation. Project size max. EUR 150,000 total costs. A
  "company in formation" may apply, so an existing company isn't strictly
  required - but an intention to found one is. The 2026 call has been
  closed since 2026-03-12, budget exhausted; statements about rolling
  submission are contradictory. **Ask the FFG directly**, don't rely on
  secondary sources.

  **Licht ins Dunkel** - only for non-profit associations (registered in
  the ZVR, based in Austria), non-profit GmbHs, foundations or religious
  communities. Not accessible as a private individual. The target groups
  are explicitly people with physical, cognitive, psychological or
  sensory disabilities - which fits DialOS precisely. Rolling submission
  between 1 April and 31 December. Co-financing towards secured total
  costs only, never full funding.

  **NLnet - checked on 2026-09-09, does NOT fit.** The earlier note with
  the 2026-11-03 deadline is therefore void. The currently open funds are
  Restack (open internet infrastructure, standards, secure devices), the
  Open Social Fund (decentralised social media via ActivityPub) and a
  fund for research and education networks. Accessibility and assistive
  technology are not a focus of any of them; the earlier NGI Zero funds
  that did cover this have apparently ended. An application would be a
  long shot and isn't worth the effort.

- [ ] **Check whether DialOS can be classified as a recognised assistive
  device** - a side finding of the funding research on 2026-09-09, and
  possibly more valuable than any project grant.

  The Sozialministeriumservice doesn't fund developers, but it does fund
  those affected: there are subsidies for assistive devices, explicitly
  including **communication aids**, as well as for workplace equipment
  where it is needed to keep or obtain a job. Future customers could
  therefore have a DialOS laptop partly subsidised. For the business
  model that is potentially worth more than a one-off project grant,
  because it lowers the purchasing hurdle precisely for the target group
  that could otherwise not afford a device.

## Done (kept for traceability)

Grouped by topic, chronological within each topic. The date is the day the
item was finished. Nothing here gets deleted - this list is the project's
memory, not just a record of successes.

### Voice control and recognition

- ☑️ **2026-08-14** — Vosk (0.3.45) + hassil (3.11.0) + German Vosk models (large/small)
  documented as a repeatable recipe - done 2026-08-14 (see
  docs/Debian-zu-DialOS.en.md, step 15). Confirmed along the way: the
  original live installation had actually disappeared again
  (`import vosk` failed on re-check) - an interim reinstall of the T490
  had wiped it, exactly the trap this item warned about.
  `dialos-vosk-test.py` is now in the repo under
  `iso-build/config/includes.chroot/usr/local/bin/`. Also found: the
  model folders on the T490 (`/usr/local/share/vosk-model-de-big` and
  `-small`) contain doubly-nested duplicate copies of the model files
  due to an unzip mistake during the original test run (wastes disk
  space, measured ~6.3 GB instead of ~3.2 GB for the large model) - the
  new docs avoid the mistake, but the existing duplicate data on the
  T490 itself hasn't been cleaned up yet.

- ☑️ **2026-08-14** — Ran and verified
  `pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0` on
  the T490 (2026-08-14) - `import vosk`/`hassil` works, `vosk.Model()`
  successfully loads the small German model.

- ☑️ **2026-08-16** — **Voice command tested live and working (2026-08-16, confirmed by
  Stephan).** It surfaced that the built-in microphone was over-amplified
  by 60 dB - the service could not possibly recognize anything. Fixed and
  permanently secured (`dialos-mikrofon-pegel.service`).

- ☑️ **2026-08-17** — **"Sprachsteuerung starten/stoppen" switch built (2026-08-17).**
  Two states with their own grammar, an announcement on every change, and
  a two-minute timeout. That answers the open state question: the user
  hears every change. A live test with a real voice is still pending.

  **How the task was worded before (for provenance):** Until "starten", DialOS listens for that
  one sentence only; afterwards it accepts commands until "stoppen".
  Recognition is already measured as reliable with three distractors
  staying quiet - what is open is the state itself: where is it
  remembered (a file, like the desktop style?), what happens at login (on
  or off?), and **how does a blind user find out which state they are
  in**? Without an answer to that, the switch is more dangerous than no
  switch: anyone who doesn't know recognition is off will think the
  device is broken.
- ☑️ **2026-09-14** — **Done through daily use: end-to-end test of
  `dialos-vosk-test.py`.** The item dates from when only installation and
  model loading had been checked. Since then Vosk recognises a real voice
  every day: 26 grammar sentences in the command service, measured near-hits,
  dictations into the shopping list and notes, the test series in
  `docs/diktat.en.md`. A separate test with the old script would show nothing
  that daily use has not already proven.

### Speech output and announcements

- ☑️ **2026-08-14** — Implemented a volume prompt during the startup announcement (only
  `nutzer`, 100/75/50/25%/off) - done 2026-08-14, see
  docs/Debian-zu-DialOS.en.md step 11. First real production use of
  Vosk, recognition logic verified with Piper-synthesized test words
  (all five options recognized correctly).

- ☑️ **2026-08-16** — Ran a real test of the volume prompt with an actually spoken
  answer (via the Bluetooth microphone, including the
  `headset-head-unit` profile switch) - done 2026-08-16. Found and
  fixed a real bug along the way: the first attempt lacked a clear
  signal for exactly when the 4-second recording window starts -
  Stephan's spoken answer ("25") was missed, only the 100% safety
  fallback came through. Fix: `dialos-start-ansage.py` now additionally
  says "Und jetzt bitte." (And now, please.) right before recording -
  correctly recognized on the second attempt afterward (a real "25" →
  25%).

- ☑️ **2026-08-17** — **Distinguish announcements: question or hint - built on
  2026-08-17.** `dialos-say.py --frage`; the default is the natural
  sentence melody from the question mark, the signal tone is an option
  via `~/.config/dialos/frageton`. See `docs/Debian-zu-DialOS.en.md`,
  step 11a. What remains is making it switchable by voice later ("switch
  on the signal tone") - that needs the "Sprachsteuerung starten/stoppen"
  switch first.

  **Original description (Stephan's question of 2026-08-17).** Today the system knows implicitly - the code
  decides what gets said - but never passes it on: `dialos-say.py`
  receives a text and speaks it. More important than the system knowing
  is that **the user recognizes a question as a question**: for someone
  who cannot see the screen, "is it waiting for me?" is the decisive
  information. On 2026-08-16 the first test of the volume prompt failed
  on exactly this - the system asked, Stephan didn't know when. The
  stopgap was the sentence "Und jetzt bitte.". The clean solution: give
  speech output a kind (hint/question), and on a question automatically
  emit a short, always identical signal. A **tone** would serve better
  than a sentence - faster, unmistakable, and it doesn't wear out.

- ☑️ **2026-08-19** — **Move the lock file of `dialos-start-ansage.py` out of
  `/tmp`** - done 2026-08-19, after the case had actually occurred: two
  startup announcements ran at the same time because `nutzer` owned the shared
  file and `dialosadmin` could not overwrite it. It now lives in
  `$XDG_RUNTIME_DIR`.

  **How the task was worded before (for provenance):**
  `/tmp/dialos-start-ansage.pid` is a fixed path in shared `/tmp` - the
  same design that caused a silent failure with the speaking marker on
  2026-08-16 (sticky bit: one account can neither overwrite nor delete
  another's file). The marker now lives under `$XDG_RUNTIME_DIR`, this
  file does not.

- ☑️ **2026-08-24** — **Pronunciation of "DialOS" decided** - by Stephan, by
  ear, out of eight spellings. **Anna says "Dial O S", Michael stays with
  "Dial OS"** ("Michael lassen wir wie bisher und bei Anne die Variante 2").
  Affects the speech output only; the word itself stays DialOS everywhere.

  Measured so nobody works through it again: **Piper knows no middle pause.**
  Comma, semicolon, colon, ellipsis, dash and multiple spaces all yield exactly
  0 ms of silence; only sentence-ending punctuation produces any (period
  220 ms, question mark 230 ms, exclamation mark 290 ms). The period even
  matched Stephan's own speaking pause - measured from a recording of his
  voice: 105 and 180 ms - but it turned the word into two sentences. His
  verdict: "das zweite ist ja alles aber nicht das Wort DialOS". "Dial O S"
  therefore inserts no silence but speaks the letters singly: 0.47 to 0.64 s.

  An old fault surfaced along the way: at the end of a sentence the rule did
  **nothing at all**. The lookahead excluded any following period, the full
  stop included - "Willkommen bei DialOS." was read as one word. Fixed.
- ☑️ **2026-09-14** — **Longer pauses between sentences** (open since
  2026-08-17). Listening test with three versions of the same announcement;
  Stephan chose "Variante B" twice - first for Anna, then after his own
  listening test for Michael too. `--sentence_silence 0.5` in
  `piper-generic.conf` and `dialos-say.py`. **The item's assumption was
  wrong:** Piper did not join sentences "almost without a pause" - it was
  already about 0.45 s, now about 0.78 s. Measured on the device (760/940 ms).
  The audio samples under `docs/sprachbeispiele/` still use the old pause; the
  scripts that generate them are updated.

### Audio: microphone and speaker

- ☑️ **2026-08-17** — **Cause of the microphone clipping determined (2026-08-17).** The
  system-wide service runs at boot; WirePlumber restores its state only
  within the session and raises the boost back - so the service was
  structurally too early. The voice service now sets the level itself
  after opening the recording, and re-adjusts on sustained clipping.
  Tested by deliberately turning it back up.

- ☑️ **2026-08-17** — **False triggers from played-back content fixed (2026-08-17).**
  Echo cancellation via PipeWire's `module-echo-cancel` set up, 32 dB of
  attenuation measured, and the case that failed before (announcement
  played via `paplay`) no longer triggers anything. Details in the
  changelog and in `docs/Debian-zu-DialOS.en.md`, step 11f.

### Dictation, information and everyday services

- ☑️ **2026-08-14** — Switched the weather location to GeoClue2 instead of IP guessing -
  done 2026-08-14, tested extensively live (see README changelog 0.5.0
  and docs/Debian-zu-DialOS.en.md, step 11, for details). Trigger:
  `wttr.in`'s own IP-based location showed Vienna instead of Stephan's
  real location (Seefeld in Tirol) - a fixed location was ruled out
  since the device is also used while traveling. Live finding along the
  way: GeoClue2 also falls back to a coarse IP estimate ("ipf fallback",
  ~25-26 km inaccurate, ~300 km off in reality) in areas with sparse
  Mozilla WiFi-database coverage - so an accuracy threshold (>10 km gets
  discarded) was added, and the weather announcement is then
  deliberately skipped rather than naming the wrong city/region. Can
  therefore be missing more often in rural areas than before - an
  accepted trade-off.

- ☑️ **2026-08-19** — **Capitalisation in dictation measured instead of
  assumed** - done 2026-08-19. **10 out of 11** cases correct, measured with
  `schreibung_richten()` itself. The one failure is a word list without
  grammar ("milch sechs eier butter") - there LanguageTool lacks the sentence
  it would need to recognise nouns. Individually every word comes out right,
  and since that same day they arrive individually. For letters and mail,
  which are whole sentences, the capitalisation holds up. The earlier
  assessment "most urgent open item" is hereby withdrawn.

- ☑️ **2026-08-19** — **The first correction of every session was a coin
  toss** - done 2026-08-19. LanguageTool's German rules load on the first
  **check request**, not at server start: 9.2 s against a time limit of
  10.0 s. On 2026-08-19 at 10:03:03 it lost. Fixed with
  `dialos-schreibhilfe-warmlaufen.py` as the unit's `ExecStartPost` - proven
  in the journal: 9096 ms at startup, then 985 ms for the first real
  correction. Side finding: `lt_lebt()` checks `/v2/languages` and therefore
  reports "running" while the service still needs nine seconds - a readiness
  check that tests something other than what matters.

### Desktop and user interface

- ☑️ **2026-08-10** — Live desktop icon for the installer (`.desktop` file with its own
  DialOS icon instead of "Install System"/egg icon on the live boot
  desktop) - done 2026-08-10 (branding via skel override).

- ☑️ **2026-08-14** — Anchor the AppIndicator packages for `dialos-tts-indicator.py`
  (`gnome-shell-extension-appindicator`, `gir1.2-ayatanaappindicator3-0.1`)
  in the package list - done 2026-08-14, also added
  `gnome-shell-extension-desktop-icons-ng` (DING) while at it: GNOME
  hasn't shown desktop icons out of the box for years, without this
  extension the office-setup scripts on `dialosadmin`'s desktop (see
  below) would have stayed invisible.

- ☑️ **2026-08-16** — **Optional Windows 11 look for GNOME built** (Stephan's request of
  2026-08-16, implemented the same day).
  `/usr/local/bin/dialos-desktop-stil.sh` switches in both directions
  (`windows` / `gnome` / `status`); the three Debian extensions
  (`dash-to-panel`, `arc-menu`, `tiling-assistant`) are in the package
  list and get installed but not enabled. Documented in
  `docs/Debian-zu-DialOS.en.md`, step 11b.

- ☑️ **2026-08-16** — **Windows switch tested technically (2026-08-16).** Packages
  installed, switched back and forth three times, every touched key
  compared: the way back restores the shipped state, and repeated runs
  create no duplicate entries. Two faults were found and fixed along the
  way (GNOME Shell doesn't know freshly installed extensions; the ArcMenu
  schema is in the wrong directory in Debian) - details in the changelog.

### Installation, ISO and system build

- ☑️ **2026-08-10** — Build a new ISO with all the fixes collected so far (boot screen,
  avatar script, Calamares branding, Piper TTS) - done 2026-08-10/11
  (the 11.08 ISO).

- ☑️ **2026-08-14** — Created the consolidation script
  `scripts/dialos-full-office-setup.sh` + new
  `dialos-setup-home-partition.sh` (runs `dialos-install`'s LUKS/stick
  logic on an already-installed system, without its disk-wipe/rsync
  copy), updated `Debian-zu-DialOS.md`/`.en.md` accordingly (step 1:
  partitioning note; step 12: new tool) - done 2026-08-14, both scripts
  only syntax-checked (`bash -n`) so far, not run for real yet (see the
  item above).

- ☑️ **2026-08-16** — **Done (2026-08-16): `dialos-install` has been dropped entirely**
  (path A - every device is built in the office from the Debian ISO plus
  the three scripts, there is no live-boot installer any more), which
  disposes of its faults too. **`dialos-rekey` stays** and still has
  them - carry them over next time it is touched: same `$HOME` starting
  folder in the backup dialog (line 142) and missing fallbacks in
  `ask_password`. Original entry: **`dialos-install` and
  `dialos-rekey` carried the same faults as the
  reviewed `dialos-setup-home-partition.sh`** - deliberately not fixed
  along with it, because the fate of the clone path was still undecided. Affected: same over-long ext4 label
  `dialos-nutzer-home` (`dialos-install` line 248), same plaintext
  passphrase under a fixed `/tmp/.rp` name (line 199), same `$HOME`
  starting folder in the backup dialog (line 231, `dialos-rekey` line
  142), same missing fallbacks in `ask_password`/`zenity --list`. Either
  carry the fixes over or retire them together with the clone path - but
  don't let them drift apart.

- ☑️ **2026-08-16** — **Timezone/locale decided (Stephan, 2026-08-16): stays
  `Europe/Vienna` + `de_AT.UTF-8`.** Not `Europe/Berlin`, which the guide
  prescribed until then. Consequence, now documented in
  Debian-zu-DialOS.en.md step 1: the build device and every ISO taken
  from it carry the Austrian settings (`eggs produce --clone` clones
  `/etc/localtime` + locale along). Simplified further on the same day by
  the decision for path A: every device is set up in the office via the
  Debian installer, so the timezone is chosen per device in step 1.

- ☑️ **2026-08-16** — **Resolved by removal (2026-08-16):** the Calamares location page
  often suggested a wrong location based
  on GeoIP during live boot (e.g. Rome instead of Berlin) - no
  documented vendor override found for `modules/locale.conf` (only
  branding is officially overridable). Remains a tool limitation for
  now; the person installing must manually check/correct the location
  while clicking through (uncritical under two-phase provisioning, since
  end customers never see the installer).

- ☑️ **2026-08-16** — First entry in `docs/iso-builds.en.md` recorded: `eggs produce
  --clone` ran on 2026-08-16 (21/21 steps without errors, 6.50 GiB),
  `DialOS-Live-0.5.1-clone.iso` as a backup snapshot before the planned
  end-to-end test (see next item) - version/date/commit/SHA256 filled
  in.

- ☑️ **2026-08-16** — **Done 2026-08-16: eight old ISOs deleted (~59 GB).** All came from
  the dropped Penguins' Eggs era. `DialOS-Live-0.5.1-clone.iso`
  deliberately stays until Stephan's first Rescuezilla image exists - it
  exists nowhere else and could not be recreated. Documented in
  `docs/iso-builds.en.md`. Originally: **Premise outdated, needs a fresh decision (checked 2026-08-16):**
  `DialOS-Live-0.5.1-clone.iso` is **no longer** local - the reinstall
  took it too. It still exists on the external drive under `DialOS-ISOs/`,
  together with four older images; **28 GB** in total.

  The real question is now a different one: all five come from the
  Penguins' Eggs era, dropped on 2026-08-16, and represent a system state
  that today's rebuild has substantially superseded. Is a Nextcloud upload
  still worth it, or are they deleted with `docs/iso-builds.en.md` keeping
  them only as a ledger?

  Only Stephan can decide - it is his backup strategy. Original entry:
  `DialOS-Live-0.5.1-clone.iso` currently only exists locally
  (`~/DialOS-Live-0.5.1-clone.iso`) - still needs to be uploaded to
  Nextcloud (only Stephan can do this, no Claude access to it).
- ☑️ **2026-09-14** — **Spell-checking in the package list:**
  `hunspell-de-de` and `hunspell-en-us` in `desktop.list.chroot`. Checked: they
  were already installed on the device, but only as "automatic" via
  `task-german-desktop` - listed explicitly they no longer hang on a
  metapackage. `aspell` left out on purpose: no program on the device uses it;
  LibreOffice, Firefox, Thunderbird and GNOME use hunspell.

### Encryption, accounts and security

- ☑️ **2026-08-16** — **Swap decided (Stephan, 2026-08-16): 8 GiB, encrypted,
  automated in `dialos-setup-home-partition.sh`.** Starting point: a
  37.3 GiB plaintext swap partition (`nvme0n1p3`) that `nutzer`'s memory
  pages - open documents, mail, browser content - could be paged out to;
  readable without the security stick, and likewise after removing the
  SSD, i.e. bypassing exactly the protection `dialos-nutzer-home`
  provides. Implemented: the script replaces any plaintext swap it finds
  with 8 GiB using a key re-randomized on every boot (`/etc/crypttab`,
  `/dev/urandom`, referenced by PARTUUID rather than filesystem UUID),
  sets `vm.swappiness=10` and `RESUME=none`, and hands the freed space to
  the home partition (on the T490: 345.6 → about 375 GiB). Rationale for
  the size: the "swap ≥ RAM" rule exists only because of hibernation, and
  hibernation is ruled out under this security design anyway (the image
  would need a persistent key in the initramfs - the discarded
  `cryptsetup-initramfs` approach). Dropping swap entirely was not an
  option: without swap the OOM killer terminates processes outright under
  memory pressure, and a killed screen reader means a blind user loses all
  feedback. Suspend-to-RAM is unaffected. **Not yet run for real** -
  happens during the first end-to-end run on the actual device.

- ☑️ **2026-08-18** — **Where do the mailbox credentials live? Decided 2026-08-18:** a
  file in `/home/nutzer`, mode 0600 - not the keyring (it does not unlock
  reliably under autologin and adds no protection behind the same LUKS
  door anyway) and not the stick (it carries the LUKS key, can be pulled,
  and would be a second place for the same job). Reasoning in
  `docs/sicherheit-datenschutz.en.md`. Originally this read:
  DialOS reads and writes mail directly over IMAP/SMTP, because from
  outside Thunderbird only knows `-compose` and allows no reading (see
  `docs/anwendungen.en.md`). So DialOS needs the credentials itself. Two
  routes: the GNOME keyring via libsecret, or a file owned only by the
  account. **This belongs to the security architecture**, not to a side
  decision - decide it together with `docs/sicherheit-datenschutz.en.md`.
  The address `proband@dialos.org` is ready for testing (mail server
  `s111.goserver.host`, no autoconfig records).

### Logs, repo and working environment

- ☑️ **2026-08-14** — Extended `scripts/dialos-claude-setup.sh` (Git identity +
  `credential.helper=store` for `dialosadmin`) and actually ran and verified
  it - done 2026-08-14. The `~/DialOS` symlink is now confirmed present (via
  `readlink -f`, pointing correctly at `.../SanDisk-Extreme/DialOS/repo`), the
  sudoers rule was already there, Git identity + `credential.helper` confirmed
  via `git config --global`. (The previous "done" entry for this was wrong -
  the script had never run through successfully under `sudo`, see the commit
  history.)

- ☑️ **2026-08-16** — **Resolved by the rebuild (checked 2026-08-16):** `~/DialOS-repo`
  no longer exists - the T490 reinstall removed the second copy. The
  danger that prompted this entry is therefore gone; the `~/DialOS`
  symlink now points at the repo on the external drive, so only one copy
  is left. Originally: Delete the stale local second repo copy under `~/DialOS-repo`, or
  deliberately keep it as a backup (decision still open) - the
  `~/DialOS` symlink is now correctly set up (see "Done" below), but
  the second copy itself is still sitting there. Two independent copies
  side by side are error-prone - that's exactly how two never-pushed
  commits from 2026-08-13 were nearly lost on 2026-08-14.

- ☑️ **2026-08-16** — **Moot since 2026-08-16:** clean up leftover `/home/eggs/*.iso`
  files - Penguins' Eggs has been dropped (step 16, now Rescuezilla), and
  on the rebuilt T490 it was never installed in the first place.
  Originally: Clean up leftover `/home/eggs/*.iso` files from the last builds
  (owned by `root`; the `eggs produce` NOPASSWD rule only covers
  `eggs produce` itself, not `rm` - needs Stephan's manual `sudo rm`).

- ☑️ **2026-08-20** — **The logs grow without limit** - done 2026-08-20.
  Stephan's decision: seven days, the same period as for the support log.
  Implemented via `/etc/logrotate.d/dialos` rather than inside the six
  programs - logrotate runs daily on a systemd timer, whereas a service that
  runs for a week would never get round to tidying up. Without `copytruncate`,
  because the programs do not hold their file open (checked), and with
  `dateext`, because in support one searches by day and not by number. All
  that remains open is that a NEWLY created file gets 0644 - from the first
  rotation onwards 0600 applies.
