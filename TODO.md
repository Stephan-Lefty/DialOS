[Deutsch](TODO.md) | [English](TODO.en.md) | [Änderungsprotokoll](README.md#änderungsprotokoll)

# TODO

Laufende Liste offener Kleinigkeiten und nächster Schritte, die Stephan
oder Claude im Arbeitsalltag auffallen. Anders als
[Offene Punkte](docs/offene-punkte.md) (grundsätzliche, noch nicht
entschiedene Architekturfragen) sind das hier konkrete, abhakbare
Aufgaben. Oben steht, was noch offen ist. Erledigtes wird nicht gelöscht,
sondern nach unten unter „Erledigt (zur Nachvollziehbarkeit)" verschoben -
dort nach Thema gruppiert und innerhalb des Themas chronologisch, jeweils
mit dem Datum, an dem es fertig wurde.

**Warum oben trotzdem Häkchen stehen:** Manche erledigten Punkte gehören
zu einem noch offenen - der offene verweist auf sie („siehe oben",
„Restrisiko dazu"). Die bleiben oben stehen, bis auch der offene Punkt
fertig ist, und wandern dann gemeinsam nach unten. So zerreißt kein Bezug.

- [ ] **Kompletter Brief nach DIN 5008** (Stephan, 2026-09-16, nach dem festen
  Einbau von Parakeet). (1) Persönliche Daten des Nutzers - zuerst Stephans -
  einmal fest für alle Programme festlegen und eintragen (Briefbogen,
  Thunderbird-Signatur, Wetter-Ort; hängt an den Kundendaten und deren
  Verschlüsselung). **(1) gebaut 2026-09-16:** Formular
  `persoenliche-daten-vorlage.txt`, `dialos-persoenliche-daten.py`, Brief/Namen/
  Wetter angebunden; Eingabemaske auch für `nutzer`, Schritt 6/6 der Einrichtung
  - **am Gerät belegt 2026-09-16, 17:37/17:47:** Stephans Daten in beiden Konten
  über die Maske eingetragen (erster Versuch für `nutzer` scheiterte an `runuser`
  ohne vollen Pfad unter pkexec, behoben) - offen: polkit-Regel von Stephan
  durchsehen, Mail-Signatur,
  Du/Sie, Unterschrift als Bild. (2) Die genaue Empfängeradresse wird eingesprochen.
  (3) Diese Adresse wird automatisch als Kontakt in Thunderbird angelegt.
  **(2)+(3) gebaut 2026-09-17:** geführter Empfänger-Dialog im Diktat, Suche in
  den Thunderbird-Kontakten, neuer Kontakt in `abook.sqlite` (Warteschlange,
  wenn Thunderbird läuft) - mit Piper simuliert (neu, gefunden, ohne). Offen:
  Probe mit Stephans Stimme (13:00 und 13:36: Namen, Abbruch - nachgebaut);
  Thunderbird zeigt die angelegte Karte **(bestätigt 13:40)**;
  **„von vorne"/„alles verwerfen" im Diktat und Cent-Beträge von Vosk gebaut
  (14:15-Probe; 15:00-Probe: „von vorne" ✓, „alles verwerfen" und Cent nachgebaut,
  mit der echten Aufnahme geprüft; 15:20-Probe: beide Wege ✓, Beträge ✓)** - offen: Stück
  ohne Satzende läuft in den nächsten Satz („… 2027 In ihrem Schreiben");
  **DIN-PDF eingebunden 2026-09-17** (Archiv, PDF, Drucken; ohne Kopf, Datum
  17.09.2026, Infoblock auf Höhe der Rücksendeangabe) - offen: Ausdruck auf Papier
  prüfen; **Ansprechpartner gebaut 2026-09-17** (simuliert, installiert 16:30, Probe am
  Gerät offen). **Mailadressen im Diktat gebaut 2026-09-17** (meine / von Kontakt /
  buchstabieren; simuliert, installiert 16:30, Probe am Gerät offen - eigene E-Mail in
  der Maske eintragen).
  **Mail-Signatur installiert** (17.09.).
  **Entwurf 2026-09-17:** `dialos-brief-din.py` (Form B, Vorschau mit
  Beispieldaten) - offen: Stephans Urteil, Empfängeradresse, Einbindung in
  Diktat/Drucken/PDF. **Mail-Signatur aus den Daten gebaut** (nicht installiert).
  (4) Aufbau nach DIN 5008, damit das PDF immer sauber ist - ob gedruckt oder
  per Mail verschickt (Anschriftfeld für Fensterumschlag, Bezugszeichen/Datum,
  Betreff, Falzmarken). Persönliche Daten nur auf dem Gerät, neue Daten fürs
  Repo erst fragen.

- [ ] **Befehlsübersicht am Gerät prüfen** (gebaut 2026-09-16): „Alle Befehle
  vorlesen" und die sechs „Befehle für …" mit echter Stimme; ist die ganze Liste
  (144 s) zu lang? Offen: Unterbrechen während der Ansage geht nicht.

- [ ] **Jahreszeiten-Hintergrund am Gerät prüfen** (gebaut 2026-09-16): nach
  dem Anmelden Sommerbild, am 23.09. ab 02:06 Herbst. Alle acht Bilder in
  3840 × 2160 hell und dunkel eingebunden (19:10). Hinweis für die nächste
  Bildfassung: Das Logo unten rechts liegt nur ~3 % vom Rand - auf 16:10-Bildschirmen
  schneidet der Zoom links/rechts je 5 % ab.

- [ ] **Lizenzhinweis für Parakeet am Gerät** (2026-09-16): CC-BY-4.0 verlangt
  Namensnennung (Wortlaut in docs/lizenzen.md). Gehört in eine
  Lizenzübersicht, die DialOS am Gerät zeigen oder vorlesen kann.

- [ ] **Eigene GNOME-Shell-Erweiterung, um zwischen Fenstern zu wechseln**
  (Stephans Frage vom 2026-09-21: „Man kann nicht per Sprachbefehl durch die
  Fenster wandern?"). Heute nicht, und das liegt nicht an DialOS: Unter
  Wayland darf ein fremder Prozess kein Fenster heben. Zweimal am Geräte
  gemessen - auch mit Aktivierungs-Token über die `.desktop`-Datei bleibt ein
  offenes Thunderbird-Fenster hinten, GNOME meldet nur „Thunderbird ist
  bereit".

  **Der einzige saubere Weg ist derselbe wie bei Thunderbird: das Programm
  fragen, dem die Sache gehört.** Eine Erweiterung läuft IM Fenstermanager und
  darf dort alles - Fenster auflisten, benennen, aktivieren, schließen. Damit
  ginge: „Welche Fenster sind offen?", „Wechsle zu Thunderbird", „Nächstes
  Fenster", „Fenster schließen".

  **Was es kostet, ehrlich:** ein neues Bauteil in GJS (zweite Sprache im
  Projekt), gebunden an die GNOME-Version - bei einem GNOME-Sprung muss es
  nachgezogen werden, sonst schaltet GNOME es ab. Dazu die Anbindung an den
  Sprachdienst (D-Bus), also dasselbe Muster wie die Thunderbird-Brücke.

  **`ydotool` ist die Abkürzung und wird nicht genommen:** Es speist
  Tastendrücke wie Alt+Tab direkt in den Kernel ein und braucht dafür einen
  Dienst mit Root-Rechten, der beliebige Eingaben erzeugen kann. Auf einem
  Gerät, das bei fremden Leuten steht, ist das die falsche Ecke zum Sparen.

- [ ] **Werkzeug: prüfen, ob im Konto `nutzer` wirklich alles ankommt**
  (Stephans Regel vom 2026-09-21, ausführlich in [CLAUDE.md](CLAUDE.md)). Die
  Regel selbst hält nur so lange, wie jemand daran denkt - bei
  `dialos-installstand.sh` war das die Lehre, und dort hat ein Werkzeug sie
  ersetzt. Dasselbe hier.

  **Was es vergleichen muss** (alles, was pro Konto liegt): Thunderbird-Profil
  auf die Erweiterung `bruecke@dialos.org` und auf die `user.js`-Einträge
  (Signatur, Wörterbuch `de-DE`), `systemctl --user is-enabled` für die
  DialOS-Dienste und -Timer, `~/.config/autostart/`, und die Schalter unter
  `~/.config/dialos/` (Frageton, persönliche Daten).

  **Es braucht `sudo`**, weil `/home/nutzer` dem anderen Konto gehört - also
  dasselbe Muster wie `dialos-installstand.sh --befehl`: melden, was fehlt, und
  den Befehl ausgeben, der es einrichtet.

  **Zwei Dinge sind heute schon bekannt und wären der erste Testfall:** die
  MailExtension (hängt nur bei `dialosadmin`) und der Frageton im Nutzerkonto
  (`sudo -u nutzer …` wurde am 2026-09-21 genannt, aber nie bestätigt).

- [ ] **Die Programmliste weiterziehen - und einen Widerspruch auflösen**
  (2026-09-21, aus Stephans Anstoß „Wir müssen doch sowieso eine Liste von
  Befehlen machen, die dann die Programme startet"). Neun Sätze stehen in
  `dialos-programm.py` und sind geprüft. Offen ist zweierlei:

  - **„Radio einschalten" und „Musik abspielen" sagen weiter, dass DialOS das
    noch nicht kann** - „Radio öffnen" und „Musik öffnen" öffnen aber jetzt
    Shortwave und Rhythmbox. Zwei Sätze für dasselbe Thema mit verschiedener
    Antwort sind für den Nutzer nicht erklärbar. **Zu entscheiden von
    Stephan:** entweder die alten Sätze öffnen dasselbe Programm, oder die
    neuen bekommen denselben ehrlichen Hinweis, bis die Sprachbedienung von
    Musik und Radio wirklich steht.
  - **Welche Programme fehlen?** LibreOffice Writer und die Dateien liegen
    nahe; „Einstellungen öffnen" wäre für den Nutzer eher eine Falle als eine
    Hilfe. Jeder neue Satz muss durch beide Pflichtprüfungen.

  **Nachgetragen am selben Tag** (Stephan: „wir müssen noch den Befehl für das
  Schließen einbauen"): fünf Sätze zum Schließen, mit Rückfrage und `SIGTERM`.
  Offen bleibt dabei **die Probe mit einem ungespeicherten Entwurf** - dann
  fragt Thunderbird nach und beendet sich nicht; DialOS soll in dem Fall
  sagen, dass es noch offen ist, statt nachzutreten. Am Gerät noch nicht
  nachgestellt.

- [ ] **Thunderbird eine MailExtension geben, statt an seinen Dateien vorbei
  zu schreiben - und ihn NICHT forken** (Stephans Frage vom 2026-09-18: „Wäre
  es sinnvoll, Thunderbird zu clonen … und auf die Bedürfnisse von DialOS und
  die Spracheingabe zu optimieren?").

  **Nicht verwechseln:** Gemeint ist eine Erweiterung **in Thunderbird**
  (MailExtension, das ist Thunderbirds WebExtension-Schnittstelle) - nicht
  eine DialOS-Erweiterung nach [docs/erweiterungen.md](docs/erweiterungen.md).
  Dasselbe Wort, zwei verschiedene Dinge.

  **Der Fork ist verneint, und zwar aus zwei Gründen.** Die Wartungslast ist
  der offensichtliche: Thunderbird ist die Gecko-Plattform samt Mail-Schicht,
  und genau die Teile, die niemand anfassen will (MIME-Parser, TLS, S/MIME,
  OpenPGP), bekommen monatlich Sicherheitsupdates. Der schwerere Grund ist
  **OAuth2**: Thunderbirds Wert liegt nicht im Quelltext, sondern darin, dass
  er bei Google und Microsoft als geprüfter Client registriert ist. Eine
  umbenannte Abspaltung erbt das nicht, und die Client-IDs mitzubenutzen ist
  kein Ausweg - eine ältere Thunderbird-Client-ID wurde von Google bereits
  deaktiviert und hat Drittprojekte mit abgeräumt. Wir stünden vor derselben
  Wand wie bei MailBurg.

  **Der Fund steckt in der Gegenrichtung.** In `docs/anwendungen.md` steht
  seit dem 2026-08-18, Mails ließen sich „von außen gar nicht" lesen, weil
  Thunderbirds Kommandozeile nur `-compose` kennt. Für die **Kommandozeile**
  stimmt das - inzwischen tut DialOS es trotzdem, nur eben **an Thunderbird
  vorbei, direkt auf seinen Dateien**. Und jeder dieser drei Wege hat bereits
  einen Fehler erzeugt:

  - **Entwurf in die mbox** (2026-09-18): erst LF statt CR LF, worauf
    Thunderbird den ganzen Ordner leer zeigte; dann `X-Mozilla-Status: 0008`,
    was nicht „Entwurf" heißt, sondern **gelöscht**.
  - **Kontakt in `abook.sqlite`** (2026-09-17): braucht eine Warteschlange,
    weil in die Datenbank eines laufenden Thunderbird nicht geschrieben werden
    darf.
  - **Index liest die mbox** (2026-09-18): sieht nur INBOX und Sent, keine
    weiteren IMAP-Ordner und keine Anhänge - beides steht dort als offen.

  Das sind nicht drei Einzelfehler, sondern dreimal dasselbe Muster: in fremde
  Dateiformate schreiben, statt das Programm zu fragen, dem sie gehören. Die
  MailExtension-API kennt Konten, Ordner, Nachrichten und Adressbücher, und wo
  sie nicht reicht, geben
  [Experiments](https://developer.thunderbird.net/add-ons/mailextensions/experiments)
  vollen Zugriff auf Thunderbirds Interna. Das ist zugleich der Weg, der den
  Fork überflüssig macht.

  **Zu klären, in dieser Reihenfolge:**
  - [x] 1. **Erst messen, dann glauben.** Erledigt am 2026-09-21, am Gerät:
     Kontakt anlegen ✓, Entwurf ablegen ✓ - und zwar im **Konto**-Ordner
     `ImapMail/imap.dialos.org/Drafts`, der zum Server hochgeladen wird.
     **Kein Experiment nötig.** Zwei Befunde nebenbei: `compose` und
     `compose.save` sind getrennte Berechtigungen (ohne die zweite:
     `browser.compose.saveMessage is not a function`), und Debians Thunderbird
     nimmt die unsignierte Erweiterung an (`xpinstall.signatures.required=false`).
  - [x] 2. **Der Weg vom Befehlsdienst zur Erweiterung** (2026-09-21):
     Native Messaging (4 Byte Länge, dann JSON) zu `dialos-thunderbird-bruecke.py`,
     das nach außen einen UNIX-Socket mit `0600` aufmacht. **Ein Socket und
     keine Datei**, weil eine Datei wieder ein Format wäre, auf das sich zwei
     Programme einigen müssten - genau der Fehler, den die Brücke ablöst. Und
     er gibt die ehrliche Auskunft: kein Socket, kein Thunderbird.
  - [x] 3. **Was, wenn Thunderbird zu ist?** Entschieden von Stephan am
     2026-09-21: **vormerken und nachholen.** DialOS sagt „Thunderbird ist zu.
     Ich lege den Entwurf beim nächsten Start von Thunderbird ab.", die Brücke
     arbeitet die Warteschlange ab, sobald Thunderbird sie startet. Seit
     demselben Tag gibt es dafür auch den Sprachbefehl **„Postfach öffnen"** -
     der Nutzer kann den Zustand also selbst auflösen.
  - [x] 4. **`docs/anwendungen.md` berichtigt** (2026-09-21, beide Sprachen).
     Der Satz stimmt für die Kommandozeile und nur für sie; die Arbeitsteilung
     in der Tabelle bleibt, weil eine Erweiterung nur wirkt, solange
     Thunderbird läuft.
  - [x] 5. **Vorgelesen wird weiter von DialOS** - die Erweiterung hat keine
     Stimme und bekommt keine.

  **Offen aus diesem Punkt (2026-09-21):**
  - [ ] **Kontakte laufen noch über `abook.sqlite`** (`dialos-empfaenger.py`,
    mit Warteschlange bei laufendem Thunderbird). Der Entwurf geht schon über
    die Brücke, der Kontakt noch nicht - und damit steht das alte Muster noch
    an einer Stelle. `{"befehl": "kontakt"}` ist in der Erweiterung gebaut und
    gemessen; es fehlt nur das Umhängen.
  - [ ] **Die Erweiterung muss im Konto `nutzer` ankommen - nicht nur bei
    `dialosadmin`** (Stephan, 2026-09-21: „Wichtig ist auch, dass die
    Erweiterungen dann auch beim Account des Nutzers ankommen"). **Das ist
    heute NICHT der Fall**: Sie hängt im Thunderbird-Profil von `dialosadmin`,
    weil sie dort von Hand installiert wurde. Im Nutzerkonto wäre alles, was am
    2026-09-21 gebaut wurde, wirkungslos - Entwurf, Senden, Entwurfs-Hinweis,
    Sichern vor dem Schließen. Und genau dieses Konto ist das, das der Kunde
    benutzt.

    **Vorarbeit ist getan** (am 2026-09-21 nachgesehen): Es gibt **weder**
    `/usr/lib/thunderbird/distribution/` **noch** eine `policies.json` - Debian
    belegt den Platz nicht, der Weg ist frei. Die Brücke selbst liegt schon
    systemweit richtig (`/usr/lib/thunderbird/native-messaging-hosts/`), gilt
    also für jedes Konto.

    **Zwei Wege, und sie unterscheiden sich an einer Stelle:**
    - `distribution/extensions/bruecke@dialos.org.xpi` wird nur in **neue**
      Profile übernommen. Für ein Gerät aus dem Büro (Weg A) reicht das, für
      ein bestehendes Profil nicht.
    - `distribution/policies.json` mit `ExtensionSettings` und
      `installation_mode: force_installed` greift **auch in vorhandenen
      Profilen** und lässt sich vom Nutzer nicht versehentlich entfernen. Das
      ist der Weg für ein Kundengerät. Unsigniert ist dabei in Ordnung, weil
      Debians Thunderbird `xpinstall.signatures.required=false` hat.

    **Zu tun:** `.xpi` an einen festen Ort (z. B.
    `/usr/local/share/dialos/dialos-bruecke.xpi`), `policies.json` ins Repo,
    im Nutzerkonto proben (anmelden als `nutzer`, „Postfach öffnen"), dann in
    `docs/Debian-zu-DialOS.md` Schritt 15c aufnehmen. **Nicht blind
    aufspielen**: `force_installed` wirkt sofort in allen Profilen, das gehört
    einmal beobachtet.

- [ ] **Erweiterungsschnittstelle bauen, danach DialOS-Suche als erste
  Erweiterung** (entschieden mit Stephan am 2026-09-17). Der Entwurf steht
  vollständig in [docs/erweiterungen.md](docs/erweiterungen.md) - **hier nur
  die abhakbaren Schritte, dort das Warum.**

  **Die Reihenfolge ist Absicht.** Heute steht jeder Sprachbefehl an drei
  Stellen in `dialos-sprachbefehl-desktop.py` (Satz in `GRAMMATIK_AN`, Eintrag
  im Dict, Zweig in der Schleife). Ein viertes Programm nach demselben Muster
  wäre die vierte Kopie. Die Schnittstelle kommt zuerst, und DialOS-Suche
  beweist dabei, dass sie trägt.

  **Der Entwurfspunkt, an dem alles hängt: umschalten, nicht addieren.** Die
  Kern-Grammatik wächst pro Erweiterung um **genau einen Satz** - ihren
  Startsatz. Alles Weitere erkennt die Erweiterung selbst, solange sie läuft.
  Grund: Bei 27 Sätzen waren es am 2026-08-22 schon 382 befehlslose
  Wortkombinationen, und die Liste steht heute bei **47 Sätzen** - ohne eine
  einzige Erweiterung. Die Zahl wächst nicht linear. Eine Schnittstelle, die
  jedem zwanzig Sätze in die Kern-Grammatik erlaubt, reißt den Fehler wieder
  auf, der seit dem 2026-08-24 gerade erst entschärft ist.

  **Schritt 1 - die Schnittstelle:**
  - [x] **`GRAMMATIK_AN` wird aus den Manifesten ergänzt** (2026-09-17). Die
    bestehenden Sätze bleiben, wo sie sind - nicht im selben Zug umgestellt,
    zwei Umbauten gleichzeitig wären nicht mehr zuzuordnen. Geprüft: 51
    Einträge, Startsatz drin, `[unk]` bleibt letzter Eintrag, Satz auch in
    `BEFEHLSSAETZE` (also für die Fuzzy-Zuordnung sichtbar). Ein kaputtes
    Manifest wird gefangen und nur gemeldet - die Sprachsteuerung ist das
    Einzige, womit der Nutzer das Gerät noch erreicht.
  - [x] **`dialos-erweiterung.py`** mit `pruefen` / `einbauen` / `entfernen` /
    `liste` (2026-09-17). Sieben Validierungsfälle gegengeprüft.
  - [x] **Das Prüfwerkzeug lag am falschen Ort** (2026-09-18, beim Bauen der
    Abnahme gefunden). `dialos-erweiterung.py` sucht es unter
    `/usr/local/bin/dialos-grammatik-pruefen.py`, es lag aber nur in `scripts/`
    und wurde nie aufgespielt. Da `einbauen` ohne den Prüfer verweigert, ließ
    sich am Gerät **keine** Erweiterung einbauen. Datei in den Aufspielbaum
    verschoben, Doku durchgehend nachgezogen. Aufgefallen wäre es sonst erst
    beim ersten Einbau durch einen Nutzer.
  - [x] **Abnahme-Werkzeug** `scripts/dialos-suche-abnahme.py` (2026-09-18).
    Ein Befehl prüft Dateien, Manifest, Dienstalter, Mikrofon-Marke, Wache und
    Index. Drei Urteile: `OK`, `FEHLER`, `OFFEN` - die dritte Stufe für alles,
    was Mikrofon braucht. **Ungeprüftes darf nicht als bestanden zählen**;
    genau so sahen die beiden Fehler vom 2026-09-17 aus.
    - [x] **Am Gerät gelaufen** (Stephan, 2026-09-18): 9 in Ordnung, 1 Fehler,
      4 offen. Sie hat dabei **ihren eigenen Fehler gefunden**: Der
      Altersvergleich las die Startzeit über `ps -o lstart=`, das den Wochentag
      in der Systemsprache ausgibt („Fr" statt „Fri"), woran `time.strptime`
      scheitert. Behoben über `/proc/PID`. Dass sie den Ausfall als `OFFEN`
      meldete und nicht als Erfolg, ist genau der Zweck der dritten Stufe.
    - [ ] **Nach dem Fix erneut laufen lassen** - dabei zeigt sich zugleich,
      ob der Befehlsdienst den Neustart wirklich bekommen hat. Am 2026-09-18
      ging beim Einfügen das Semikolon verloren, `pkill` bekam zwei Muster und
      brach mit Exit 2 ab; der Dienst lief unverändert weiter.
  - [ ] **Wortschatzprüfung, die VERWEIGERT statt warnt.** Jedes Wort aus
    `startsaetze` und `eigene_grammatik` gegen das kleine Modell. Grund:
    „löschen" fehlt im Wortschatz und wurde am 2026-08-18 still aus der
    Grammatik geworfen. Eine Warnung beim Einbauen liest niemand wieder; der
    Fehler zeigt sich erst, wenn der Nutzer allein mit dem Gerät ist.
  - [x] **Kollisionsprüfung gegen die vollständige Grammatik - Werkzeug fertig
    am 2026-09-17.** `/usr/local/bin/dialos-grammatik-pruefen.py` kann jetzt Sätze
    prüfen, die noch NICHT eingebaut sind: `--neu "satz"`. Das ging vorher
    nicht, und die Lücke war nicht harmlos - ein Kandidat als bloßes Argument
    wurde gegen eine Grammatik gehört, die ihn gar nicht enthält, und von Vosk
    auf den nächstliegenden bestehenden Satz gepresst. Das sah nach einer
    Verwechslung aus, war aber ein Werkzeugfehler; umgekehrt konnte ein
    kaputter Kandidat unauffällig bleiben.

    Geprüft wird jetzt **in beide Richtungen**: ob der Kandidat erkannt wird,
    **und ob bestehende Sätze durch ihn kaputtgehen**. Die zweite Frage ist die
    wichtigere - ein Kandidat, der selbst durchfällt, kostet nur sich; einer,
    der einen bestehenden Befehl verwechselbar macht, nimmt etwas kaputt, das
    heute funktioniert.

    Dazu läuft die **erste** Pflichtprüfung jetzt mit, statt nur in der Doku zu
    stehen: Wortschatz gegen `graph/words.txt`, ohne Sprechen, getrennt nach
    Kandidat und Bestand. Ein fehlendes Wort im Kandidaten beendet die Prüfung,
    eines im Bestand wird als Altlast gemeldet - sonst hinge ein neuer Befehl
    an einem alten Problem.
  - [x] **Prüfung am Gerät ausführen** - der Wortlaut des Startsatzes hängt
    daran. **Ausgeführt am 2026-09-17 auf dem T490: alle 51 Sätze wörtlich
    erkannt** (Kandidat selbst und alle 49 bestehenden), der Startsatz ist
    einbaubar. **Aber:** Das Werkzeug meldete „graph/words.txt nicht lesbar -
    Wortschatz UNGEPRUEFT" - das kleine Modell unter
    `/usr/local/share/vosk-model-de-small/graph/` hat keine `words.txt` (nur
    `Gr.fst`, `HCLr.fst`, `phones/`). Die Wortschatz-Prüfung läuft dort also
    nie. Von Hand nachgeholt: Grammatik mit „unterlagen durchsuchen" gebaut,
    Vosk meldete kein „missing in vocabulary" - beide Wörter bekannt. Das
    Werkzeug sollte deshalb über diese Vosk-Meldung prüfen statt über die Datei
    (passt auch zum Nebenbefund „bildschirmfoto" unten).

    **Die 51 erklären sich, und zwar durch einen Fehler im Werkzeug** (siehe
    nächster Punkt): Es sind 49 bestehende Sätze plus der Kandidat, macht 50 -
    der Kandidat wurde doppelt geprüft. Am Ergebnis ändert das nichts.
    Die Vorauswahl hat sich damit bestätigt: „unterlagen" und „durchsuchen"
    kommen in keinem der 49 bestehenden Sätze vor (ausgezählt: **71**
    verschiedene Wörter - die zwischenzeitlich genannten 69 waren eine
    Fehlzählung). „briefe" stünde dagegen schon drin, „brief" sogar sechsmal -
    deshalb ist „Briefe durchsuchen" als zweite Formulierung gestrichen.

    **Was der Lauf nicht ersetzt:** Piper spricht deutlicher als ein Mensch,
    gleichmäßiger und immer aus derselben Entfernung. Der Satz ist damit nicht
    kaputt - bewiesen ist er erst mit echter Stimme.
  - [x] **Zählfehler im Werkzeug, vom ersten echten Lauf gefunden und behoben**
    (2026-09-17). Der Lauf meldete **51 statt 50** Sätze, und Stephan hat die
    Ursache im Protokoll gesehen: „Unterlagen durchsuchen wurde 2x aufgeführt".
    Genau so war es - `alle` enthielt den Kandidaten bereits (oben angehängt),
    und `neu + alle` hat ihn ein zweites Mal geprüft. **Falsch war nur die
    Zahl, nicht das Ergebnis** - der Kandidat wurde doppelt statt gar nicht
    geprüft. Behoben, der Kandidat steht jetzt zuerst und genau einmal.

    Festgehalten, weil die Lehre größer ist als der Fehler: Eine Zahl, die man
    nicht erklären kann, war in diesem Projekt schon mehrfach der Anfang einer
    falschen Diagnose. Hier war sie der Anfang der richtigen.
  - [ ] **„bildschirmfoto" fehlt im großen Tuda-Modell** - Nebenbefund vom
    Bau des Werkzeugs. „Bildschirmfoto erstellen" ist ein belegter Befehl und
    funktioniert am Gerät, das Wort kommt **dreimal** in der Grammatik vor. Das
    kleine Modell kennt es also; das große Tuda-Modell nicht.

    **Daraus folgt eine Regel:** Eine Vorprüfung des Wortschatzes gegen das
    große Modell ist **wertlos** - die Modelle haben verschiedene Wortschätze,
    und zwar in beide Richtungen. Geprüft wird ausschließlich am Gerät, gegen
    das Modell, das dort auch läuft.

    **Die Gegenprobe ist erledigt** (Stephan, 2026-09-17): Die Zeile
    `ALTLAST … 'bildschirmfoto'` kam **nicht** - aber nicht, weil das Wort
    bekannt wäre, sondern weil die Prüfung mangels `words.txt` gar nicht lief.
    Behoben im nächsten Punkt.
  - [x] **Wortschatz-Prüfung auf Vosks eigene Meldung umgestellt** (2026-09-17,
    Stephans Befund und Vorschlag). Sie las `graph/words.txt` - **die es im
    kleinen Modell gar nicht gibt**: `/usr/local/share/vosk-model-de-small/graph/`
    enthält nur `Gr.fst`, `HCLr.fst` und `phones/`. Die Prüfung lief dort also
    nie und meldete ehrlich „Wortschatz UNGEPRUEFT" - so stand es auch im
    Protokoll des Laufs am Gerät.

    **Eine Pflichtprüfung, die nie anschlägt, ist von einer fehlenden nicht zu
    unterscheiden.** Genau das war sie bis heute.

    Geprüft wird jetzt so, wie Vosk es ohnehin tut: Die Grammatik wird gebaut,
    und Vosks Meldung `Ignoring word missing in vocabulary` wird abgefangen.
    Dafür muss `SetLogLevel` kurz hochgesetzt und stderr auf
    Dateideskriptor-Ebene umgeleitet werden - die Meldung kommt aus der
    C++-Ebene, nicht aus Python, und `contextlib.redirect_stderr` greift dort
    nicht. Das ist der einzige Weg, der unabhängig vom Aufbau des Modells
    funktioniert.
    - [x] **Am Gerät gegengeprüft - sie schlägt an** (Stephan, 2026-09-18).
      Der Kandidat „xylofonquark durchsuchen" wurde mit
      „KANDIDAT NICHT IM WORTSCHATZ DES MODELLS: 'xylofonquark'" abgewiesen.

          /usr/local/bin/dialos-grammatik-pruefen.py --neu "xylofonquark durchsuchen"

      **Damit ist die Lücke vom 2026-09-17 nachweislich geschlossen** - die
      Pflichtprüfung prüft wieder. Ein Durchlauf wäre hier das schlechte
      Ergebnis gewesen, kein gutes.
  - [x] **Mikrofon-Übergabe** (2026-09-17) - kleiner als gedacht: Der Dienst
    prüft schon heute in jeder Schleifenrunde auf eine Markierungsdatei und
    verwirft dann alles Gehörte, und `dialos-notiz.py` benutzt für Rückfragen
    **exakt dieselbe Datei** unter dem Namen `FREMDE_AUFNAHME_MARKE`. Es gibt
    also längst eine allgemeine Mikrofon-Marke, nur unter historischem Namen
    („dialos-diktat-aktiv"). Für die Übergabe war am Dienst nichts zu ändern.
    - [x] **Wache gebaut** (2026-09-17). `diktat_laeuft()` liest die PID aus der
      Marke und prüft mit Signal 0, ob der Prozess lebt; eine verwaiste Marke
      wird weggeräumt und gemeldet. Ohne das bliebe das Mikrofon nach einem
      harten Abbruch (SIGKILL) **für immer** belegt - der Nutzer spräche gegen
      ein taubes Gerät, und nicht einmal „Sprachsteuerung stoppen" käme noch
      durch. Für einen blinden Nutzer gibt es aus diesem Zustand keinen Weg
      zurück.

      **Rückwärtskompatibel, und das ist Absicht:** `dialos-diktat.py` und
      `dialos-notiz.py` legen die Datei leer an. Ohne PID verhält sich die
      Prüfung wie bisher - vorhanden heißt belegt. Damit ist nichts
      kaputtzumachen, was heute läuft. Fünf Fälle geprüft: keine Marke, leere
      Marke, lebende PID, tote PID (wird weggeräumt), unlesbarer Inhalt (gilt
      sicherheitshalber als belegt).
      - [ ] **Nachziehen:** `dialos-diktat.py` und `dialos-notiz.py` sollten
        ihre PID ebenfalls hineinschreiben, sonst gilt die Wache nur für
        Erweiterungen - und das Diktat hat das Problem, seit es die Marke gibt.

  **Schritt 2 - der Aufspielweg** (Stephans Anforderung vom 2026-09-17: „wir
  müssen nachher mit der fertigen Erweiterung nahtlos vom T490 zugreifen
  können und die Erweiterung dort installieren können"):
  - [x] **Der Neustart-Hinweis kommt jetzt auch bei einem Manifest**
    (2026-09-17) - `dialos-aufspielen` zählt eine Datei unter
    `share/dialos/erweiterungen/` wie eine Änderung am Befehlsdienst selbst.
    - [ ] **Die Pflichtprüfungen bleiben bewusst bei `dialos-erweiterung.py
      einbauen`, nicht im Aufspielen.** Die Kollisionsprüfung lässt Piper jeden
      Satz sprechen - das dauert Minuten und hätte beim Aufspielen einer
      geänderten Zeile nichts zu suchen. Zu entscheiden ist, ob das genügt:
      Wer eine Manifest-Datei von Hand in den Ordner kopiert, umgeht die
      Prüfung. Ein Paket mit `postinst` würde das schließen.
  - [x] **`scripts/dialos-installstand.sh` vergleicht das Manifest bereits**
    (geprüft 2026-09-17) - es läuft seit dem 2026-08-20 über den **ganzen**
    Baum unter `includes.chroot`, nicht über eine gepflegte Liste von Ordnern.
    Genau dafür wurde es damals umgebaut: „Eine Liste, die von Hand gepflegt
    werden muss, veraltet." Hier zahlt sich das aus - es war nichts zu tun.
  - [ ] **Erst später fällig:** `QUELLE` in `dialos-aufspielen` von einem
    einzelnen Pfad auf eine **Liste** umstellen. Für die erste Erweiterung
    nicht nötig, weil sie im DialOS-Repo liegt; nötig, sobald die zweite in
    ein eigenes Repo zieht. **Kein zweites Aufspielskript** - die bestehende
    sudoers-Regel ist ausweislich ihres eigenen Kopfes „praktisch ein
    Root-Zugang", ein zweiter Weg wäre ein zweiter.
  - [ ] Nach dem ersten echten Aufspielen `--befehl` laufen lassen. Ein Commit
    beweist nicht, dass etwas auf dem Gerät wirkt.

  **Schritt 3 - DialOS-Suche**, erst wenn Schritt 1 und 2 stehen:
  - [ ] **Von MailBurg wird `extract/` geteilt, nicht das Programm**
    (korrigiert am 2026-09-17 nach Stephans Frage, ob es MailBurg ganz braucht
    „oder nur Teile"). Der Unterschied ist nicht die Größe, sondern die
    Aufgabe: **MailBurg archiviert, DialOS-Suche muss nur finden.** Vollständig
    begründet in `docs/anwendungen.md`; kurz: Die Dokumente liegen schon in
    `~/Dokumente/`, `~/Notizen/` und im mbox - sie ein zweites Mal in einen
    inhaltsadressierten Speicher zu schreiben wäre Verdopplung, und
    Revisionssicherheit, Grabsteine und Aufbewahrungsfristen haben auf einem
    privaten Gerät nichts zu suchen.
    - [ ] **Am T490 bestätigt: `extract/` fehlt** (Stephan, 2026-09-18).
      `dialos-suche-index.py stand` meldet „MailBurg: FEHLT - kein OCR". Der
      Index läuft damit nur über `pdftotext` und Klartext - **gescannte Briefe
      bleiben stumm**, und gerade die sind der Grund, warum jemand ein Archiv
      durchsuchen will. Kein Fehler, aber die Grenze des heutigen Standes.
    - [ ] **`extract/` einbinden** (1.360 Zeilen): `pdftotext` mit `pypdf` als
      Rückfall, OCR über `pdftoppm`/`tesseract` mit der gemessenen Pixelgrenze
      `MAX_KANTE=5000`, Office ohne Binärmüll. Dort steckt teuer erarbeitetes
      Wissen - das baut niemand ein zweites Mal richtig nach.
    - [ ] **Import statt Kommandozeile** - Korrektur des ersten Entwurfs, der
      es umgekehrt festlegte. Der Aufruf über die Kommandozeile war richtig,
      solange MailBurg der ganze Motor sein sollte; für ein geteiltes Modul ist
      der Import richtig. Kostet nichts: MailBurgs Kern hat
      `dependencies = []`, ohne Extras kommen weder PySide6 noch der Server
      mit. Lizenz geprüft: MIT darf in ein GPL-3.0-Projekt.
    - [ ] **Offen, gehört ins MailBurg-Repo:** ob `extract/` in ein eigenes
      kleines Paket wandert, das beide benutzen. Sauberer als der Import aus
      dem Kern, aber ein Umbau an MailBurg - und dort zu entscheiden.
  - [x] **Eigener Index, schlank - gebaut am 2026-09-17**
    (`dialos-suche-index.py`). SQLite-FTS5 gehört zur Standardbibliothek;
    ein Index über Dateien, die schon da sind, sind einige hundert Zeilen -
    ohne Archivablage, ohne Journal, ohne Fristen. Quellen: Briefe aus
    `~/Dokumente/`, PDFs aus `~/Dokumente/Archiv/DialOS-DATA/`, Notizen aus
    `~/Notizen/`, Mails aus Thunderbirds mbox.
    - [x] **`content=''` war ein Fehler** (2026-09-18). Aus einer contentless
      FTS5-Tabelle lässt sich nichts löschen; der Index wäre ab dem zweiten
      Lauf abgestürzt. Behoben, alter Index wird beim Öffnen verworfen und neu
      gebaut. Ganzer Lebenslauf gegengeprüft.
    - [x] **Fehlende Quelle wirft nichts mehr aus dem Index** (2026-09-18,
      nach Stephans Hinweis auf den Stick). Nur einzelne Dateien innerhalb
      einer vorhandenen Quelle werden ausgetragen.
    - [x] **Der Stick wird über sein Label gefunden** (2026-09-18, nach
      Stephans Verweis auf `docs/sicherheit-datenschutz.md`). Eine
      Kennzeichnungsdatei, wie hier zuerst vorgeschlagen, wäre überflüssig
      gewesen: `dialos-setup-home-partition.sh` und `dialos-rekey`
      partitionieren den Sicherheits-Stick **immer** in `DIALOS-KEY` (2 GiB,
      ext4, Schlüsseldatei) und `DIALOS-DATA` (Rest, exFAT, der mobile
      Datenbereich). Das Label steht damit schon fest.

      Der Index löst `/dev/disk/by-label/DIALOS-DATA` auf und sucht den
      Einhängepunkt in `/proc/mounts` - beides ohne root. Der Pfad darf
      wechseln, das Label nicht, und ein fremder Stick wird nicht mitgelesen.
      Der Datenbereich **kommt hinzu** und ersetzt `~/Dokumente/Archiv` nicht:
      Auf dem Entwicklungsgerät gibt es den Stick nicht, auf dem
      ausgelieferten ist es umgekehrt - ein Ordner, den es nicht gibt, wird
      ohnehin übersprungen.
    - [x] **Der ganze Datenbereich wird durchsucht, kein Unterordner**
      (Stephan, 2026-09-18: „ja es soll immer der komplette Datenbereich
      durchsucht werden"). Fotos und Musik fallen über die Endungen heraus,
      nicht über eine Ordnerregel, die der Nutzer einhalten müsste - wer seine
      Briefe irgendwohin legt, soll sie wiederfinden. Die Liste der lesbaren
      Endungen steht dafür jetzt an einer Stelle statt je Quelle; vorher war
      dieselbe Datei je nach Ordner lesbar oder nicht.
    - [x] **Mails aus Thunderbird im Index** (2026-09-18, Stephans Frage).
      Lokale mbox-Dateien aus Eingang und Gesendet, eine Mail je Eintrag
      (`<mbox>#<Message-ID>`), Betreff als Titel, Absender und Empfänger als
      Namen; Pfade und Lesen kommen aus `dialos-mailarchiv.py`. Am T490 fünf
      Mails. Offen: IMAP-Ordner jenseits von INBOX/Sent, Anhänge.
    - [x] **Mails bleiben auch auf dem Stick** (Stephan, 2026-09-18, auf die
      Frage nach MailBurg auf dem Stick: „Dann hätte man alle Mails immer auch
      auf den Stick"). Das läuft schon: `dialos-mailarchiv.py` legt ein- und
      ausgehende Mails als PDF im Archiv ab, `dialos-archiv.py` kopiert sie auf
      den Stick (fünf Mail-PDFs am T490). **Programme gehören nicht auf den
      Stick** - exFAT kennt kein Ausführbar-Bit, und eine Datenbank auf einem
      Wechselmedium ist beim Abziehen mitten im Schreiben hin. Bewusst in Kauf
      genommen: Der Stick ist unverschlüsselt, ein Finder liest die Mails mit;
      Stephans Entscheidung, weil sie an jedem Rechner lesbar sein sollen.
    - [x] **Am Gerät belegt: Suche → Fund → Papier** (Stephan, 2026-09-18,
      12:22): „Unterlagen durchsuchen" → „Postfach" → Begriff „Postfach" → ein
      Treffer → „drucken" → Rückfrage → Ausdruck auf dem Brother. Stephan:
      „Druck lief einwandfrei durch." Damit ist die ganze Kette belegt: Startsatz,
      Mikrofon-Übergabe, Bereich, Begriff über zwei Erkenner, Index, Trefferdialog,
      PDF aus dem Mailtext, Drucker - und das Mikrofon war danach zurück.
    - [x] **Antworten am Gerät belegt** (Stephan, 2026-09-18, 12:45): Fund →
      „antworten" → Diktat („Ich schreibe mit") → „Diktat beenden" → Rückfrage
      „17 Wörter an support at webgo Punkt de" → Entwurf abgelegt, Mikrofon
      danach zurück. Dabei gefunden: Die Schlussansage des Diktats sprach von
      Notizen - behoben, sie nennt jetzt die E-Mail.
    - [x] **Antwort als Entwurf in Thunderbird sichtbar** (Stephan, 2026-09-18:
      „Entwurf ist da"). Zwei Fehler davor: LF statt CR LF, und
      `X-Mozilla-Status: 0008` heißt gelöscht, nicht Entwurf. Offen: Senden per
      Sprache (bewusst nicht gebaut - eine abgeschickte Mail ist aus der Welt),
      Weiterleiten am Gerät noch nicht geprobt.
    - [x] **Weiterleiten mit buchstabierter Adresse** (2026-09-18, Stephans
      Wahl). Kontakte zuerst, sonst buchstabieren; Prüfung auf At-Zeichen und
      Punkt. Mit Piper simuliert. **Am Gerät geprobt (13:21):** Ablauf
      vollständig, Entwurf mit Fwd: abgelegt - aber die Adresse kam als
      komteakte@teialos.or an statt kontakt@dialos.org. Daraus gebaut:
      Gegenlesen mit bekannten Adressen und Domains, getrenntes Vorlesen vor
      und nach dem At, bis zu drei Anläufe.
      **Zweite Probe (2026-09-21):** Buchstabieren fehlerfrei
      (`kontakt@dialos.org`), aber der Vorschlag ersetzte den Teil vor dem At und
      schickte den Entwurf an `proband@dialos.org`. Behoben: Der lokale Teil wird
      nie ersetzt, bei bekannter Domain kommt kein Vorschlag.
      **Dritte Probe (2026-09-21, 13:29) bestanden:** buchstabiert
      `kontakt@dialos.org`, kein Vorschlag mehr, Kontrolle getrennt vor und nach
      dem At, Entwurf an die richtige Adresse. Damit ist das Weiterleiten vom
      Zuruf bis zum Entwurf belegt. Der Fehl-Entwurf an `proband@dialos.org`
      liegt noch in den Entwürfen und kann dort gelöscht werden.
    - [x] **Buchstaben-Messung mit Stephans Stimme ausgewertet** (2026-09-21):
      Buchstabieralphabet 43 von 43, Buchstabennamen 16 von 26 - und „ef", „vau",
      „ix" fehlen im Wortschatz des kleinen Modells, F, V und X wären damit
      unbuchstabierbar. **Das Alphabet bleibt.** Werkzeug:
      `scripts/dialos-buchstaben-messen.py`, Aufnahmen unter
      `erkenner-vergleich/buchstaben/`.
    - [x] **Frageton bei Rückfragen eingeschaltet** (Stephans Entscheidung,
      2026-09-21: „Ja, bei jeder Rückfrage"). Bei kurzen Fragen trägt Pipers
      Satzmelodie allein nicht - bei einem einzelnen „a" ist sie nicht hörbar.
      Gesetzt für `dialosadmin` und in `/etc/skel`, damit jedes künftige Konto
      ihn hat. **Offen: für das bestehende Konto `nutzer` setzen** (Befehl in
      `docs/Debian-zu-DialOS.md`).
    - [x] **Suche in Dokumenten am Gerät belegt** (2026-09-21, 14:17): Bereich,
      Begriff, Art, weiteres Suchwort, Aufzählung, Auswahl, Vorlesen ab der
      Anrede. Zwei Lücken dabei gefunden und behoben: nach dem Vorlesen endete
      die Suche, und ein einzelner Absendername galt nicht als Merkmal zum
      Eingrenzen. **Zweiter Durchlauf (14:26) vollständig bestanden:**
      Personenfrage kam („Von wem? GESOBAU AG. Oder sage: keiner."), „Gesobau"
      wurde trotz „wieso bau" zugeordnet (0,71), nach dem Vorlesen kam „Noch
      etwas damit?". Dabei stürzte die Suche einmal still ab, weil beim Umbau
      eine Funktion verlorenging - seitdem wird jeder Absturz angesagt und
      protokolliert.
    - [ ] **Am echten Stick prüfen.** Bisher nur mit einem nachgestellten
      Einhängepunkt getestet, nicht gegen `/dev/disk/by-label`. Am T490 heißt
      das: Stick einstecken, `dialos-suche-index.py stand` muss den
      Einhängepunkt zeigen; dann abziehen und erneut - die Einträge müssen
      bleiben.
    - [x] **Ansage für nicht angeschlossene Treffer** (2026-09-18): Vor dem
      Vorlesen wird `erreichbar` geprüft - „Diese Datei liegt im Archiv, das
      gerade nicht angeschlossen ist."
    - [x] **Trefferdialog gebaut** (2026-09-18, Stephans Wahl „DialOS fragt der
      Reihe nach"): Jahr, Art, Person oder Monat - nur Merkmale, die wirklich
      trennen, das schärfste zuerst; dann bis zu drei weitere Suchwörter; sonst
      die drei neuesten aufzählen und „den ersten/zweiten/dritten" wählen; zum
      Schluss vorlesen ab der Anrede. Mit Piper simuliert, Probe am Mikrofon
      steht aus.
    - [ ] **Bilder und Videos durchsuchbar machen** (Stephan, 2026-09-18: „Bilder
      Videos Suche in die Todo für später packen"; die Suche danach ist anders
      als bei Dokumenten). Erst wenn Dokumente, Notizen und Mails fertig sind.
      Zu entscheiden ist dann: nur Dateiname, Aufnahmedatum und Ordner (dann
      geht „Fotos vom Juli", nicht „Foto vom Auto"), oder zusätzlich
      Texterkennung auf Bildern - das braucht MailBurgs `extract/` und deutlich
      mehr Rechenzeit beim Aufbau. Die Endungen fallen heute bewusst heraus.
    - [x] **Kölner-Phonetik-Spalte gebaut.** Geprüft: „Meier"/„Mayer"/„Maier"/
      „Mayr" fallen auf `67` zusammen, „Müller"/„Mueller"/„Miller" auf `657`.
      Im Test findet der gesprochene Begriff „Meier" den Brief mit „Mayer", und
      „Schmidt" die Notiz mit „Schmitt" - beides über den Klang. „Fahrrad"
      liefert korrekt nichts.

      **Die Phonetik läuft als ZWEITER Durchgang**, nicht als erster: Sie
      kollidiert naturgemäß („Müller" und „Mahler" haben beide `657`). Wörtlich
      gefundene Treffer stehen deshalb vorn, und die Ansage sagt „klingt nur
      ähnlich", wenn es nur phonetische gab - sonst wundert sich der Nutzer
      beim Vorlesen über die Schreibweise.
    - [ ] **Am Gerät mit echten Dokumenten prüfen.** Bisher nur mit zwei
      Testdateien belegt. Interessant wird die Laufzeit bei den PDFs im Archiv.
  - [ ] **Freier Suchbegriff über Parakeet**, nicht über Vosk. Ein Suchbegriff
    ist Text, kein Befehl - dieselbe Arbeitsteilung wie beim Diktat. Nichts neu
    zu beschaffen. **Zu prüfen ist nur eines:** ob sich Parakeet ein Wörterbuch
    aus den häufigsten Absendernamen des eigenen Index mitgeben lässt, so wie
    das Diktat sein persönliches Wörterbuch hat. Daran scheitert sonst jede
    freie Erkennung.
  - [ ] **Phonetische Suche prüfen:** eine FTS5-Spalte mit der Kölner Phonetik
    von Absendernamen, damit „Meier/Mayer/Maier" zusammenfallen. Fängt
    Erkennungsunschärfe strukturell ab, statt sie dem Nutzer als Nachfrage
    aufzubürden.
  - [ ] **Trefferdialog:** 40 Treffer kann man nicht vorlesen. Erst eingrenzen,
    Anzahl ansagen, Weg nennen - dieselbe Regel wie beim Einkaufszettel („ein
    Befehl nimmt dem Nutzer keine Entscheidung ab, die er selbst treffen
    kann").
  - [x] **Symbol - fertig am 2026-09-17.** Stephans Entwurf
    (`assets/suche-icon-entwurf.png`) saß stilistisch, fiel aber gemessen bei
    32 px durch: Dokument, Briefumschlag und Lupe verschmolzen zu einem
    Klumpen, während DialOS und Denkzettel dort klar blieben. Ursache war die
    Anzahl, nicht die Zeichnung - rechts drei Objekte statt einem, und für die
    rechte Hälfte bleiben bei 32 px nur etwa 14 × 20 px. Der Maßstab steht
    seit dem 2026-08-24 im Quelltext von `Denkzettel/assets/icon-bauen.py`.

    Stephans Entscheidung danach: „reduziere den rechten Bereich auf die
    Lupe". Gebaut mit `assets/suche-icon-bauen.py`, abgeleitet von
    `Denkzettel/assets/icon-bauen.py`. Die Lupe wird **gezeichnet**, nicht aus
    dem Entwurf ausgeschnitten - kopiert käme sie mit den Schnittkanten des
    überlappenden Briefumschlags. Zwei Varianten gebaut und verglichen: „nur
    Lupe" trägt bei 32 px, „Wellen und Lupe" verklumpt genauso wie der
    Entwurf. Damit folgt es dem Familienmuster - Denkzettel ersetzt die
    Schallwellen durch den Stift, DialOS-Suche durch die Lupe. **Ersetzen,
    nicht ergänzen.**

    Zwölf Dateien: `suche-icon-light-*.png` und `suche-icon-dark-*.png` in 32,
    48, 64, 128, 256, 512 px, alle mit Alpha-Kanal. Beleg auf hellem und
    dunklem Panel in `assets/suche-icon-groessenvergleich.png`. Das Skript
    prüft den Abstand zum Ring vor dem Zeichnen und bricht ab, wenn er
    gerissen wird - der erste Versuch ist genau daran aufgelaufen (193,6 gegen
    erlaubte 192, am Griffende).

    **Dabei gefunden und im Skript festgehalten: DialOS und Denkzettel
    benennen gegenläufig.** `DialOS/assets/app-icon-light.png` hat eine helle
    Scheibe, `Denkzettel/assets/app-icon-dark.png` ebenfalls eine helle. Bei
    Denkzettel heißt „-dark" also „für dunkle Umgebungen", bei DialOS
    „dunkles Icon". DialOS-Suche folgt DialOS, weil die Dateien im selben
    Ordner liegen - zwei Bedeutungen desselben Suffixes an einem Ort wären der
    sichere Weg zur falschen Datei.
    - [ ] **Am Gerät ansehen**, sobald ein `.desktop`-Eintrag existiert: im
      Panel, im Startmenü und in der Fensterleiste neben DialOS und
      Denkzettel. Am Bildschirm entschieden ist nicht dasselbe wie im Panel
      gesehen.

  **Auslieferung als `.deb`** (entschieden 2026-09-17), aber **nicht für die
  Entwicklung**: Auf dem T490 bleibt `dialos-aufspielen` der Weg, weil ein
  Paket bei jeder Iteration gebaut und hochgezählt werden müsste. Für ein
  Kundengerät ist das Paket der einzige Weg - dort entfernt
  `scripts/dialos-aufraeumen.sh` `dialos-aufspielen` samt sudoers-Regel. Der
  eigentliche Gewinn ist `postinst`: Dort sind die beiden Pflichtprüfungen
  nicht umgehbar, und `Depends: mailburg` erzwingt die Abhängigkeit. Achtung:
  DialOS baut heute **kein einziges** Paket - das ist neue Infrastruktur
  (`debian/control`, `changelog`, `rules`), und ohne Repository-Server bleibt
  es bei `dpkg -i` von Hand.

  **Erweiterungen wohnen vorerst im DialOS-Repo** (Stephan, 2026-09-17). Ein
  eigenes Repo je Erweiterung ist das Ziel, aber nicht für die erste: Solange
  sich die Schnittstelle ändert, müssten zwei Repos synchron gehalten werden,
  während beide instabil sind - und jeder Fehler wäre erst einmal nicht
  zuzuordnen.

  **Noch offen** (in `docs/erweiterungen.md`): was bei einem Kern-Update
  passiert; ob hassil hier endlich seinen Platz findet; ob das Archiv
  verschlüsselt läuft (MailBurg kann es, aber der Suchindex bleibt Klartext).

- [ ] **Vorlesen langer Texte ist nicht unterbrechbar - und für ein Archiv wird
  das zum Normalfall** (2026-09-17). **Kein neuer Fehler:** Der Punkt
  „Befehlsübersicht am Gerät prüfen" weiter oben nennt ihn schon - „Alle
  Befehle vorlesen" läuft 144 s, und „Unterbrechen während der Ansage geht
  nicht". „Brief vorlesen" liest ebenso am Stück.

  **Was sich ändert:** Bei der Befehlsübersicht ist das eine Unbequemlichkeit,
  die man mit „Befehle für …" umgehen kann. Bei einem Archiv ist es der
  Normalfall - wer sucht, bekommt Treffer, die er nicht alle hören will, und
  ein zweiseitiger Brief von der Krankenkasse dauert länger als die 144
  Sekunden. Zum Vergleich: „Windows Desktop." dauert 1,5 s.

  **Vorgesehen:** absatzweise vorlesen, zwischen den Absätzen ein kurzes
  Lauschfenster mit einer Mini-Grammatik aus „stopp", „weiter", „zurück",
  „nochmal". Das Muster gibt es zweimal - der zweite Erkenner für „Diktat
  beenden" und der ja/nein-Erkenner vor dem Leeren des Zettels. Es braucht
  keine neue Technik, nur die Zerlegung des Textes vor dem Sprechen.

  **Gebaut gehört es in `dialos-say.py`, nicht in DialOS-Suche.** Die 144
  Sekunden der Befehlsübersicht gehören keiner Erweiterung; wer es fürs Archiv
  baut, löst sie für alles mit.

  **Echtes Barge-in NICHT zuerst bauen.** Die echo-bereinigte Quelle
  `dialos_mikrofon_ohne_echo` gibt es zwar schon, aber während der eigenen
  Stimme zuzuhören heißt: „Soll ich stoppen?" im vorgelesenen Brief stoppt ihn.

  **Und zweitens:** Ein vorgelesener Brief darf **nicht** in den
  Ansagen-Speicher unter `~/.cache/dialos/ansagen`. Der ist für „Ich höre Dir
  zu." gedacht, das täglich kommt; ein einmalig vorgelesenes Dokument füllt ihn
  mit WAV-Dateien, die nie ein zweites Mal treffen. Einen Schalter dafür hat
  `dialos-say.py` heute nicht - die Grenze ist, ob ein Text sich wiederholt,
  nicht wie lang er ist.

- [ ] **EIN GESPRÄCH IM RAUM HAT DIALOS BEDIENT - mit Druck, Diktat und
  Archiv** (2026-09-14, 11:01-11:31, während Stephans Pause). Der
  schwerwiegendste Befund bisher, weil er nicht nur stört, sondern **fremde
  Gespräche aufschreibt, ablegt und ausdruckt**.

  **Was passiert ist** (Konto `dialosadmin`, Laptop-Mikrofon und
  -Lautsprecher, AIRHUG aus). In der Nähe wurde laut und länger gesprochen,
  Spitzen 27000-30000. Stephan auf Nachfrage: „Gespräch im Raum".

  | Zeit | Was DialOS tat |
  |---|---|
  | ab 11:01 | Sprachsteuerung sechsmal selbst eingeschaltet |
  | 11:15:47 | „brief schreiben" (+1 Wort) - 97 s Gespräch als Brief, voriger Brief beiseitegelegt, **PDF ins Archiv** |
  | 11:18:47 | auf Windows-Optik umgeschaltet |
  | 11:19:53 | „notiz drucken" - gedruckt |
  | 11:20:12 | „brief brief brief drucken" (+2) - **das Gespräch gedruckt** |
  | 11:24:52 | „einkauf wir brief drucken" (+2) - **das Gespräch noch einmal gedruckt** |
  | 11:24:53 | „einkaufszettel aufnehmen" - 50 s Gespräch als 8 Einträge |
  | 11:30:26 | „einkauf erledigt" (+2) - Löschfrage, gehört „nein nein ja", nicht gelöscht |
  | 11:30:53 | „notizen drucken" (+2) - hing in der Warteschlange, abgebrochen |

  **Aufgeräumt** (Stephans Wahl „Alten Stand wiederherstellen"): voriger Brief
  zurück, Einkaufszettel wieder leer, die Gesprächsfassungen (Brief, Archiv-PDF,
  Zettel) nur für das Konto lesbar in einen eigenen Ordner zum Ansehen und
  Löschen. Druckauftrag 8 abgebrochen. Zwei Seiten mit dem Gespräch lagen im
  Drucker. **Die Protokolle unter `~/.log/` enthalten weiter Gesprächsfetzen**
  - nicht im Repo, bewusst auch hier nicht zitiert.

  **Was dabei versagt hat - vier Stellen:**
  1. **Einschalten.** „Beide Wörter" genügt nicht gegen ein langes Gespräch:
     Die Grammatik presst jede Äußerung in ihre Wörter, und irgendwann stehen
     „sprachsteuerung" und „starten" nebeneinander.
  2. **Kein Nachfragen vor Folgenreichem.** Drucken, Diktat (überschreibt den
     Brief, legt ein PDF ab) und Umschalten laufen sofort. Nur das Löschen
     fragt - und die Frage hat gehalten, knapp.
     **Behoben am 2026-09-14** (Stephan: „Bau eine Rückfrage vor Drucken und
     Diktat ein"): Beide laufen jetzt über `dialos-notiz.py` mit derselben
     Ja/Nein-Frage wie das Löschen. Still mit Attrappen geprüft (ja, nein,
     nichts verstanden, leerer Zettel; Marke nur während der Frage). **Offen:**
     Probe am Gerät mit echter Stimme - und sie wirkt erst nach dem nächsten
     Anmelden, weil der Befehlsdienst neu starten muss.
     **Probe gemacht (2026-09-14, 11:50):** Die Frage kam, „nein" verhinderte
     den Druck, „ja" startete das Diktat. Aber Stephan musste beide Antworten
     zweimal geben - gemessen 2,03 s parec-Puffer plus Mikrofon erst nach der
     Frage. Behoben (offenes Mikrofon während der Ansage, 30 ms Puffer), am
     rohen Mikrofon geprüft. **Offen:** dieselbe Probe noch einmal mit echter
     Stimme nach dem Neuanmelden, dazu ein Einkaufszettel-Diktat (Wortanfang,
     „Diktat beenden" nicht mehr als Eintrag).
     **Zweite Probe (12:10):** „nein" und „ja" je beim ersten Versuch, „Bananen"
     direkt nach „Ich schreibe mit" vollständig. „Diktat beenden" nur teilweise
     abgeschnitten, „Den" blieb als Eintrag - Schnitt jetzt 0,35 s früher, die
     Zeitmarken stehen ab sofort im Diktat-Protokoll.
     **Dritte Probe (12:22):** „ja" beim ersten Versuch. Aber das Diktat endete
     nach „Rote Äpfel" von selbst - das kleine Modell hörte in „Bananen" ein
     „diktat beenden beenden". Auszählung aller Protokolle: genau „diktat
     beenden" 14 x (soweit nachvollziehbar echt), Dreiwort-Varianten 3 x (davon
     einmal nachweislich falsch). Jetzt gilt nur noch genau „diktat beenden".
     Der Rest wird nach dem BEGINN der Wörter geschnitten, nicht nach dem Ende.
     **Offen:** vierte Probe - echte Zeitmarken für den Schnitt fehlen noch. Umschalten fragt
     weiterhin nicht (es richtet keinen Schaden an und ist sofort umkehrbar).
  3. **Die Zusatzwort-Regel vom 2026-08-24** (bis zu zwei Wörter zu viel)
     hat drei der vier Druckaufträge erst ermöglicht. Sie war an Stephans
     echter Stimme gemessen, nicht an einem Gespräch.
  4. **Die gesprochenen Hinweise** („Der Befehl heisst: notiz drucken")
     sprechen Befehlswörter in den Raum. Zeitlich auffällig: 11:18:50 Hinweis
     „notiz drucken", 11:19:53 erkannt „notiz drucken". **Nicht belegt**, dass
     es das Echo war - im Raum wurde ja gesprochen.

  **Noch nicht entschieden, nur Richtungen:** Rückfrage vor Drucken und Diktat;
  Zusatzwort-Regel nicht für folgenreiche Befehle; ein Gesprächs-Erkenner
  (viele Äußerungen ohne Befehl in kurzer Zeit -> ausschalten statt
  Hinweise sprechen); Aufweckwort statt Grammatik (steht schon als Punkt).
  Der Punkt „Erster Fehlstart" unten ist damit derselbe Mechanismus, jetzt mit
  Folgen.

  **Wiederholt um 12:24-12:29 mit einem Fernsehfilm** (Stephan: „wenn z.B.
  parallel ein Film im TV läuft, dann will die Sprachsteuerung ständig etwas
  machen"): Brief-Diktat trotz Rückfrage (ein „ja" im Film), dreimal
  Umschalten, ein Bildschirmfoto. Der Brief liegt im Papierkorb, der vorige
  ist zurück.

  **Stephans Entscheidung (2026-09-14): A und B bauen, C planen, D prüfen.**
  - **A - Gesprächs-Erkennung: gebaut.** 5 Äußerungen ohne Befehl in 30 s →
    aus, mit Ansage. An allen Sitzungen durchgespielt: 12 echte bleiben an, 7
    aus Gespräch/Film gehen nach 14-23 s aus, bevor ein Fehlbefehl durchkam.
    **Offen:** Probe mit Fernseher nach dem Neuanmelden.
  - **B - Einschalten nur mit Stille davor und danach: erst gemessen.** Bei
    jedem „sprachsteuerung …" steht jetzt der Pegelverlauf der letzten 4 s im
    Protokoll. Schwelle erst nach echten Zahlen mit und ohne Fernseher.
    **Film-Probe 12:43-12:50:** Der Film schaltete in 5 min einmal ein, danach
    kam „brief schreiben" nach nur 3 Fetzen durch (die Rückfrage hielt mit
    einem „nein" aus dem Film), A griff erst nach 2 min. **A allein reicht gegen
    Fernsehton nicht.** **Messung:** Stille DAVOR trennt nicht (der Film hatte
    selbst eine ruhige Stelle), Stille DANACH trennt - Stephan 5 x letzte
    Werte 0, Film 11-27. **B gebaut** (Stephan: „Ja, bau B so ein"): letzte
    0,5 s nach dem Satz unter 3000, sonst verworfen mit Ansage „… es ist zu
    laut …" (höchstens einmal pro Minute). **Preis, bewusst angenommen:** Bei
    lautem Fernseher lässt sich die Steuerung auch vom Nutzer nicht
    einschalten. Datenlage dünn - nachprüfen.
    **Stephans Einschätzung des Stands (2026-09-14):** „Aktuell funktioniert
    die Sprachsteuerung, wenn fast keine Umgebungsgeräusche vorhanden sind!"
    Für laute Umgebung sind C oder D die eigentliche Lösung.
    **Am Gerät geprüft (12:58, nach Neuanmelden):** lauter Fernseher → Satz
    verworfen (Werte danach bis 8000), Ansage „… zu laut …" kam; ohne bzw.
    leiser Fernseher → eingeschaltet (Werte danach 0-1); leiser Fernseher
    danach → nach 20 s Gesprächs-Erkennung, aus. Von Stephan bestätigt.
    **Nachgebessert (13:09):** Stephan bei laufendem, aber gerade leisem
    Fernseher - ein einzelner Block mit 3149 nach dem Satz, verworfen, und
    wegen der 60-s-Sperre OHNE Ansage. Jetzt ist ein Ausschlag erlaubt, die
    Ansage höchstens alle 15 s. An allen 14 Einschaltsätzen geprüft: nur
    dieser Fall ändert sich.
    **Befund 2026-09-15, 10:51-10:52:** Beim Vorlesen des Brief-Absatzes für
    den Erkenner-Vergleich (das Aufnahmeprogramm setzte noch keine Marke) hat
    Vosk in 40 s **dreimal „sprachsteuerung starten"** aus normalem Vorlesen
    herausgehört - B hat alle drei verworfen (Stephan las weiter). **Aber die
    Ansage „… es ist zu laut …" kam alle drei Mal** und unterbrach ihn: Sie
    kommt per Definition genau dann, wenn jemand weiterspricht. **Offen, zu
    entscheiden:** Ansage seltener (z. B. einmal je 5 min), nur bei Stille
    VOR dem Satz, oder nur bei genau zwei Wörtern ohne weitere Fetzen. Die
    60-s-Sperre war am 14.09. gerade wegen eines stummen Fehlschlags auf 15 s
    gesenkt worden - beides gegeneinander abwägen.
    **Entschieden 2026-09-15 (Stephan: „meldet sich immer mit dem Hinweis …
    zu laut" - „und niemand hat Sprachsteuerung gesagt!"):** Das erste Mal
    wird still verworfen, die Ansage kommt erst, wenn der Satz binnen 20 s
    erneut verworfen wird. An den zehn Ablehnungen des Tages nachgerechnet:
    zwei Ansagen statt acht (beide beim Vorlesen um 10:51). Dazu nennt die
    Begrüßung jetzt „Wenn Du etwas möchtest, sage: Sprachsteuerung starten." -
    die Sprachsteuerung startet bewusst in Bereitschaft, nicht eingeschaltet.
    Wirksam nach dem nächsten Anmelden; Hörproben der Begrüßung nicht
    nachgezogen.
  - **Verworfen vorerst: Mindestlautstärke für Befehle.** Spitzen am
    2026-09-14: Stephans Befehle 47 x, leisester 7810; Film 76 x, Median
    24188, nur 5 leise Fetzen unter 3000; Gespräch 253 x, leisester 4162.
    Eine Schwelle hätte nur leisen Fernseher abgefangen (das erledigt A),
    gegen lauten Film und Gespräch nichts. In den Vortagen gab es erkannte
    Äußerungen ab 847 - ob echte Befehle darunter waren (Headset-Mikrofon),
    ist nicht mehr zu klären. Wieder aufgreifen, wenn C/D stehen.
  - **Aufbau der Messungen vom 2026-09-14** (Stephan: „Der TV-Lautsprecher ist
    in etwa genauso weit weg wie ich"): Fernseher und Nutzer gleich weit vom
    Laptop-Mikrofon. Deshalb kamen Film und Stimme mit fast gleichem Pegel an
    - über die Lautstärke ist beides nicht zu trennen. B wirkt über den
    Ablauf (Nutzer schweigt nach dem Satz, Film nicht), nicht über den
    Abstand. Für C ist genau das der Prüffall: gleiche Lautstärke, gleiche
    Entfernung.
  - **C - Aufweckwort (openWakeWord):** planen - der Punkt steht schon weiter
    unten; mit den heutigen Protokollen als Prüfstein.
  - **D - Knopf statt Einschaltsatz:** prüfen, ob AIRHUG oder ein Headset eine
    Taste liefert, die sich abgreifen lässt (Medientaste über Bluetooth AVRCP).

- [ ] **Versprecher im Diktat: „Satz löschen" und „Satz wiederholen" - gebaut,
  offline geprüft, Probe mit echter Stimme steht aus** (Stephan am 2026-09-15:
  „wie bauen wir 'Versprecher' ein, also das die Sprachsteuerung weiß, das ich
  einen Satz neu einsprechen muss"; seine Wahl: „Satz löschen", dazu „Satz
  wiederholen").

  **Aufbau:** Beide Sätze stehen in der Grammatik des kleinen Schluss-Erkenners.
  Das Diktat merkt sich jede Äußerung als Einheit mit Wort-Zeitmarken
  (`Aeusserungen`). „Satz löschen" streicht die letzte und sagt „Gestrichen:
  …", „Satz wiederholen" liest sie vor („Zuletzt: …"). Während Anna antwortet,
  wird mitgelesen und verworfen, danach beginnen beide Erkenner neu.

  **Sicherungen, alle gemessen:** Gegen Piper ergab normaler Brieftext ein
  zusammenhängendes „satz wiederholen" und „satz löschen". Getrennt hat die
  Ruhe - echter Befehl: 0,5 s davor/danach still (Spitze 24/18 und 1), Fehler:
  laut (32653/22769, 27990/22874). Deshalb: genau zwei Wörter, höchstens 0,6 s
  Lücke, 0,4 s Ruhe davor, 0,5 s Ruhe danach, mit 0,15 s Abstand zu den
  Wortmarken (ohne den Abstand galt ein echter Befehl als „danach nicht
  still" - Vosk setzt das Wortende etwas zu früh). Befehlswörter werden erst
  bei Bestätigung aus dem Text genommen.

  **Dabei am Schluss mitgeändert:** Auch „Diktat beenden" wartet jetzt auf
  Ruhe danach, und nach jedem Befehl gilt die 3-s-Sperrfrist neu. Anlass: Im
  Offline-Test machte das frische kleine Modell nach „Satz löschen" aus „die
  Rechnung liegt dem Schreiben bei" ein „diktat beenden" (0,41 s Lücke) - und
  am Vormittag „bis Ende des Monats".

  **Offline in Echtzeit durch das echte Diktat geprüft** (Michael, nachgebildetes
  Mikrofon): zwei Fehlauslöser verworfen, Versprecher gestrichen und angesagt,
  „Satz wiederholen" las den letzten Satz ohne Löschen, Schluss sauber, keine
  Befehlswörter im Brief.

  **Erste Probe mit echter Stimme (2026-09-15, 12:27) - zwei Schwächen, beide
  behoben.** Beide Befehle wurden erkannt, drei Fehlauslöser im Fließtext
  verworfen, „bis Ende des Monats" löste nichts aus. Aber:
  1. **Gestrichen wurde der gescheiterte erste Versuch, nicht der Versprecher.**
     Stephan sprach die fett gedruckten Wörter meiner Anleitung mit („Pause
     Satz löschen") - das kleine Modell hörte drei Wörter, kein Befehl, der
     Text landete im Brief. Das zweite „Satz löschen" strich dann genau diesen
     Rest („Gestrichen: Pause Satz löschen"), „Satz wiederholen" las „Absatz
     sagt wiederholen" vor. **Jetzt:** Ein Rest am Textende (letztes Wort
     löschen/wiederholen, „satz" in den zwei Wörtern davor, im Brief samt einem
     einzelnen Wort davor wie „Also") wird vorher entfernt.
  2. **Gestrichen wurde ein Erkennungsstück, kein Satz.** „punkt setzen" kam
     als eigenes Stück, und „Ich bitte Sie … wäre ich dankbar" als EIN Stück
     mit 60 Wörtern. **Jetzt:** Ein Satz reicht bis zum vorletzten Punkt,
     Frage-, Ausrufezeichen oder Zeilenwechsel; ein angefangener Satz ist er
     selbst. Auf dem Einkaufszettel: die letzte Ware.
  Dazu: kein „Müller ." mehr (Satzzeichen-Stück hängt am Wort davor), und nach
  „neuer Absatz"/„neue Zeile" wird großgeschrieben („Mit freundlichen Grüßen").
  Offline in Echtzeit mit genau diesem Ablauf geprüft: Rest entfernt, der
  Meier-Satz gestrichen, aus dem langen Stück nur der letzte Satz.

  **Zweite Probe mit echter Stimme (2026-09-15, 13:02):** „Satz löschen" hat den
  Meier-Satz richtig gestrichen. Neu gefunden und behoben:
  1. **„Satz wiederholen" las „Satz wiederholen Jax".** Das große Modell hörte
     „jax wiederholen" und setzte „jax" mehr als 0,35 s vor den Beginn laut
     kleinem Modell - es blieb stehen. Jetzt fällt weg, was nach 0,35 s vor dem
     Befehl ENDET (vorher: BEGINNT). Der erste Versuch davor stand als eigenes
     Stück im Text und wird jetzt als Rest erkannt.
  2. **Das erste „Satz wiederholen" galt als „davor nicht still"** - nach fünf
     Sekunden Pause. Offline gemessen: Das kleine Modell setzt den Wortanfang
     rund 0,16 s nach dem Tonbeginn. Abstand vor dem Befehl 0,15 → 0,25 s; die
     Pegel stehen jetzt bei jeder solchen Ablehnung im Protokoll.
  3. **„Kommas" + „Setzen" über eine Stückgrenze.** Vosk schneidet lange Rede
     auch ohne Pause. Beginnt ein Stück mit dem zweiten Wort eines Satzzeichens
     und endete das vorige mit dem ersten, werden beide zusammen verarbeitet;
     „kommas setzen" gilt als Komma.

  **Offline dabei gefunden und behoben:**
  4. **Ein einzeln gesprochenes „Punkt setzen" wurde zu „Satz löschen"** - mit
     Ruhe davor und danach, also angenommen; der eben diktierte Satz war weg.
     Jetzt **Gegenprobe:** Der Befehl gilt nur, wenn die freie Erkennung im
     selben Zeitraum „lösch…"/„wiederhol…" gehört hat. In drei Läufen drei
     Fehlauslöser so verworfen („punkt setzen", 2x; „umsetzen"), alle echten
     Befehle angenommen.
  5. **Ohne erkannte Satzzeichen strich „Satz löschen" bis zum Textanfang**,
     samt Anrede. Jetzt höchstens das letzte gesprochene Stück (Stücke nur aus
     Satzzeichen zählen nicht). Zuerst zwei Stücke - der nächste Offline-Lauf
     strich damit wieder die Anrede mit („komma neue apps" statt „komma setzen
     neuer absatz"). Preis: Ein Satz, der über mehrere Pausen gesprochen wurde,
     braucht mehrmals „Satz löschen".

  **Dritte Probe (2026-09-15, 13:21), Brief ohne Versprecher:** Zwei „satz
  löschen" im Fließtext richtig verworfen, „Kommas"-Zusammenfassung griff
  („komma" + „setzen"). Aufgefallen:
  - **Das echte „Diktat beenden" galt als „danach nicht still"** - beendet hat
    nur die Rückfallebene (die freie Erkennung lieferte genau „diktat beenden").
    Pegel werden jetzt bei jeder solchen Ablehnung protokolliert; Ursache offen,
    nicht geraten.
  - **Anna meldete „3 Sätze"** bei acht - gezählt wurden Erkennungsstücke. Jetzt
    werden Satzenden gezählt.
  - Vosk: „neuer Abschluss" statt „neuer Absatz", „kommen ersetzen" statt „komma
    setzen" (über eine Stückgrenze, deshalb nicht zusammengefasst).
  - Sprachsteuerung: „Brief erstellen" ist kein Befehl, und ein Vorschlag kam
    nicht. „Sprachsteuerung beenden" kam als „welchen"/„windows", erst
    „stoppen" ging. **„Brief erstellen" ist seit 2026-09-15 dritter Satz**
    (Stephans Freigabe, alle 29 Sätze gegen Piper geprüft); Test am Gerät nach
    dem nächsten Anmelden steht aus. „Sprachsteuerung beenden" bleibt offen.
  - **Dateinamen mit Datum und Uhrzeit (2026-09-15, gebaut):** Stephans Wahl
    `2026-09-15-1343-Brief.txt/.pdf` und `…-Bildschirmfoto.png`, bestehende
    Dateien umbenannt (13 Briefe, 16 Fotos am Admin-Konto). Das Nutzerkonto
    stellt sich beim ersten Brief/Foto selbst um. Archiv-PDFs behalten ihre
    Namen (nicht gewählt). Test am Gerät steht aus.
  - **Persönliches Wörterbuch (2026-09-15, gebaut):** `~/.config/dialos/
    woerterbuch.txt`, nur auf dem Gerät; im Admin-Konto mit Stephans Namen
    angelegt und am installierten Diktat geprüft. **Offen:** Einträge im
    Nutzerkonto (dort muss es jemand angemeldet anlegen), Einträge per Sprache
    („Wort merken"?), Füllen aus den Kundendaten (hängt an deren
    Verschlüsselung). **Zurückgestellt (Stephan, 2026-09-15: „Das mit dem Brief
    und den Kundendaten eintragen machen wir später"):** Brief-Test mit dem
    Namen am Gerät, Kundendaten eintragen.
  - **Parakeet-Test im Diktat (2026-09-15, gebaut, Schalter im Admin-Konto
    gesetzt):** Probe mit Stephans Stimme steht aus. Danach entscheiden: fest
    einbauen (Modell nach /usr/local/share, sherpa-onnx für alle Konten) oder
    verwerfen. **Probe 14:32 mit gesprochenen Satzzeichen: Parakeet 14,9 %,
    Vosk 9,9 %** („Sätzen"). **Weg 3 gebaut (Stephans Wahl):** natürlich
    sprechen, Parakeet setzt die Satzzeichen, gesprochen nur Absatz/Zeile;
    „12." und „Dr." kein Satzende. **Probe 14:47 mit Stephans Stimme: Brief
    praktisch fertig** (alle Satzzeichen, Absätze, Anrede, Gruß); Wortfehler
    Vosk 4,9 %, Parakeet 6,2 %, aber nur Parakeet liefert Satzzeichen.
    **Entschieden (Stephan):** Weg 3 für Brief und Notizen, Vosk für Befehle
    und Einkaufszettel - **nach zwei Proben:** frei formulierter Brief, Brief
    mit leise laufendem Fernseher. Notizen seit 15:02 im Test.
  - **Prüfstand (2026-09-15, gebaut, Mitschnitt im Admin-Konto an):** erste
    echte Fälle stehen aus. Geplant: derselbe Brief mit eingebautem Mikrofon und
    mit dem USB-Tischmikrofon TONOR TC30, dann die zwei Parakeet-Proben. TONOR
    rauscht bei 100 % deutlich stärker (RMS 293 gegen 68) - vor dem Vergleich
    Pegel mit Sprache prüfen. **Erledigt 15:41:** zwei Fälle, Parakeet eingebaut
    2,8 % / TONOR 4,2 %, Vosk 12,7 % / 8,5 % (Tabelle in docs/diktat.md);
    Schwellen richten sich jetzt nach dem Rauschboden (TONOR hing vorher).
    **Nächste Fälle:** frei formulierter Brief, Brief mit leisem Fernseher -
    der Fernseher mit beiden Mikrofonen. **Fernseher erledigt 16:49:** TONOR
    4,2 % (wie ruhig), eingebaut 9,9 % mit Parakeet. **Offen:** Sprachsteuerung
    mit Fernseher - echte Einschaltversuche werden verworfen (feste Grenze 3000
    für „danach still"), Fehlalarme im Aus-Zustand. Nächster Schritt: TONOR und
    Rauschboden für den Befehlsdienst auf dem Prüfstand (braucht kurze
    Befehls-Mitschnitte mit Zustimmung, nicht dauernd). **Vorbereitet
    2026-09-15:** Mitschnitt mit Schalter, Beschriften, Neu-Erkennen,
    Mikrofonwahl für den Dienst. **Messsitzung erledigt 17:52** (90 Mitschnitte,
    Tabelle in docs/sprachbefehle.md): richtig 18/21, 17/18, 16/17, 18/19;
    kein ausgeführter Fehlauslöser; Verpasser fast nur verschluckte Anfänge.
    **2026-09-16: Punkt 1 und 2 gebaut** (Aufnahme bleibt offen; Optik-Regel
    begrenzt), aufgespielt. Erste Probe 12:18: 4/5 beim ersten Versuch; Rest
    lag an der Markierung, die 0,64-0,70 s nach dem Ton endet → Leser mit
    Zeitstempeln, nachgebildet 0/8 → 8/8. **Probe 12:48: 6/6 beim ersten
    Versuch, ohne Warten.** Punkt 1 und 2 erledigt. Nach den schnelleren
    Ansagen (13:10) Stephans Urteil: **„Es ist jetzt so wie in einem normalen
    Gespräch."** Ungeklärt: 13:10:27 kam „brief als wir" an.
    **Rückfall-Antworten gebaut (2026-09-16):** Standard-Antwort, „Was kann ich
    sagen", ehrliche Antworten mit WUNSCH-Zählung, Wetter mit Rückfall-Ort und
    menschlicher Formulierung. **Frei diktierter Brief 13:35: Parakeet 3,4 %,
    Vosk 28,8 %** - Weg 3 bestätigt. **Fest eingebaut (2026-09-16, 14:00):**
    `scripts/dialos-parakeet-einrichten.sh` (Modell nach
    /usr/local/share/dialos-parakeet, sherpa-onnx systemweit, Prüfsummen,
    Selbsttest), Diktat standardmäßig mit Parakeet, abschaltbar mit
    `parakeet-aus`, beide Modelle laden gleichzeitig; Prüfstand danach
    unverändert (2,8/9,9/4,2/3,4/4,2 %). **Am Gerät eingerichtet, erster Brief 14:19:**
    Laden 12 s statt 33 s; „Absatz" allein, Betreff bis Satzende, Anrede-Komma,
    „Cent"→„Euro" nachgebaut (Prüfstand-Fall `absatz-allein-1`, 3,8 %).
    **Offen:** Probe im Nutzerkonto nach Neuanmeldung; Grammatik „ein Brief
    geschrieben" (Parakeet, Vosk hörte „einen") kommt ungeprüft durch;
    Datum nach DIN 5008 („31.08.2026") gehört zum Brief-Ausbau. **Zweiter Brief
    14:36:** Anrede-Absatz, „Betriff", „Yeah.", Gruß-Leerzeile, Endungen über
    Vosk+hunspell, Vosk-Absatz nachgebaut (Fall `absatz-allein-2`, 4,5 %, alle
    Satzzeichen). Name unter dem Gruß („Stefan Grüßen") → aus den persönlichen
    Daten; Zahlen („1229" statt „12629") bleiben Parakeets Fehler. Gruß/Name-Zeilen und
    Betreffzeile (fett im PDF und Druck) gebaut. Offen: „-ung"-Endungen bei
    Parakeet („Rechn", „Nebenkostenabrechn"). Ort im Admin-Konto hinterlegt (wttr.in
    findet ihn richtig, 47,35/11,20); im Nutzerkonto fehlt er noch. Offen:
    Probe am Gerät, später freie Erkennung unbekannter Sätze.
    **Neu:** Nicht gespeicherte Ansagen (jede Uhrzeit) sprechen erst 2,3-2,7 s
    nach dem Aufruf (gespeicherte 0,2 s) - Aufwärm-Ansage und frische Piper-
    Synthese. **Erledigt 2026-09-16:** direkt erzeugen und abspielen, 1,4-1,7 s.
    Offen: mit Bluetooth-Lautsprecher prüfen (Stille statt Aufwärm-Ansage);
    ein dauerhaft laufendes Piper sparte weitere rund 0,5 s Modell-Laden. **Reihenfolge danach:** 1. Lücke nach Annas Ansage schließen, 2.
    Optik-Regel an die Zusatzwort-Grenze, 3. TONOR-Verstärkung senken (100 %
    übersteuert), dann dieselben 15 Befehle erneut messen. Gefunden: Fehlauslöser
    „auf Windows umschalten" aus Wortsalat (alte Optik-Regel ohne
    Zusatzwort-Grenze) - nach der Messung reparieren.
    **Stephan, 2026-09-15: „Zwischen der Ansage von Anna und meiner Antwort muss
    ich immer so 1,5 Sekunden warten. Sonst wird das erste Wort verschluckt!"**
    Passt zum Muster „tag haben wir"/„haben wir" (Teil 1 und 2). Ursache im
    Dienst: Nach jeder Ansage wird parec beendet, 0,7 s Nachhall abgewartet
    (NACHHALL_WARTEN_S), dazu 0,3 s Abfragetakt und der Start von parec. Das
    Diktat löst dasselbe seit dem 14.09. mit offenem Mikrofon während der
    Ansage und 0,3 s Vorlauf - dasselbe hier bauen, NACH der Messsitzung
    (sonst sind Teil 3/4 nicht mit 1/2 vergleichbar); beim rohen TONOR ohne
    Echo-Unterdrückung darauf achten, dass Annas eigene Worte („Der Befehl
    heisst: …") nicht als Befehl zählen. **Grundsatzfrage
    (Stephan):** Taugt DialOS nur bei Stille - und damit nicht für draußen? Beim festen
    Einbau: Modell (465 MB) und
    sherpa-onnx für alle Konten nach /usr/local, Paketierung und Lizenz
    (Modell CC-BY-4.0, Namensnennung) klären.
  - **„Brief als PDF speichern" am Gerät belegt (2026-09-15, 13:44)**, ebenso
    „Brief erstellen" und die neue Schlussansage. Und zum ersten Mal hat die
    Sprachsteuerung einen Befehl VORGESCHLAGEN: „als pdf speichern" -> „Der
    Befehl heisst: brief als pdf speichern". **Im selben Brief gefunden und
    behoben:** Ein „Diktat beenden" direkt hinter dem Namen (kleines Modell:
    „[unk] diktat beenden", kein Schluss) stand am Ende im Brief, weil erst das
    zweite nach einer Pause beendete. Ein solcher Rest am Textende wird jetzt
    entfernt. Weiter von Vosk: „Koffer Absatz", „neue teile" (zum zweiten Mal
    für „neue Zeile"), „Ausrufezeichen" ohne „setzen" bleibt Wort.
  - **„Brief als PDF speichern" (2026-09-15, gebaut):** Stephans Wahl
    „PDF sichtbar ablegen" und „alle drei nennen". Offline geprüft (PDF,
    leerer Brief, Einkaufszettel, Ansage), 30 Sätze gegen Piper. Test am Gerät
    nach dem nächsten Anmelden steht aus; die Hörproben in
    `docs/sprachbeispiele/alle-ansagen/` kennen die neue Schlussansage noch
    nicht.

  **Noch offen, nicht behoben:** Ein Stück nach einer Pause beginnt immer groß
  („Ich bitte Sie, Wir diesen Betrag"); einzeln gesprochenes „Punkt setzen"
  kommt beim großen Modell oft als „und setzen"/„umsetzen" an (mit Michael
  offline; bei Stephan am Gerät bisher richtig). **Probe mit echter Stimme
  steht aus.**

- [ ] **Brief in DialOS eingesprochen (2026-09-15, 11:46) - drei Programmfehler
  gefunden und behoben, Beweis mit vollständigem Brief steht aus.** Rückfrage
  „ja" beim ersten Versuch; Diktat nach Brief-Vorlage mit gesprochenen
  Satzzeichen.
  1. **Falscher Schluss mitten im Text:** Das kleine Modell hörte in „…Antwort
     bis Ende des Monats" ein „diktat" (37,92-38,31 s) und ein „beenden"
     (39,55-40,19 s). Stephan: „Konnte den letzten Absatz nicht mehr
     einsprechen". **Behoben:** Die beiden Wörter müssen unmittelbar
     aufeinander folgen (Lücke höchstens 0,6 s; hier 1,24 s, beim echten
     Schluss am 14.09. 0,00 s).
  2. **„neuer Absatz" am Ende einer Äußerung ging verloren** -
     `satzzeichen_setzen()` schloss mit `strip()` und nahm das „\n\n" mit.
     **Behoben:** nur noch Leerzeichen abschneiden.
  3. **„neue Zeile" ging im Brief verloren** - Äußerungen wurden mit „\n"
     verbunden, der Briefbogen zog jeden einfachen Umbruch zusammen.
     **Behoben:** Äußerungen mit Leerzeichen verbinden, Zeilen je Zeile
     umbrechen.
  Alle drei offline an den Protokollwerten geprüft; ein Briefbogen aus den
  gesprochenen Sätzen hat jetzt vier Absätze und den Gruß auf zwei Zeilen.
  **Offen - Vosk-Erkennung:** „rama setzen mit diesem Bit jeden" (komma
  setzen mir diesen), „dr muster", „zweihundert vierzig", „Neuer abstatt";
  Sie/Ihnen/Schreiben klein. Parakeet hatte denselben Absatz im Vergleich mit
  einem Fehler erkannt (siehe Erkenner-Vergleich).

- [ ] **Erkenner-Vergleich fürs Diktat: Vosk gegen Whisper und Parakeet -
  Test am 2026-09-15** (Stephan am 2026-09-14: „Was mir aktuell noch
  Kopfzerbrechen macht ist der Einkaufszettel. Gibt es noch 'bessere'
  Sprachsteuerungssysteme" - und: „Du meinst Befehle und Sprachbefehle wie
  bisher und für 'Texte' vom Nutzer Whisper?").

  **Die Aufteilung, falls der Vergleich es trägt:** Befehle, Ja/Nein,
  „später" und „Diktat beenden" bleiben bei Vosk (feste Grammatik: schnell,
  eng begrenzt). Nur das große Vosk-Modell im Diktat würde ersetzt - für
  Einkaufszettel, Notizen und Brief.

  **Eingerichtet (2026-09-14)** mit `scripts/dialos-erkenner-einrichten.sh`,
  nur zum Messen, in `erkenner-vergleich/` neben dem Repo (nichts im System,
  kein Autostart): whisper.cpp v1.9.4 mit den Modellen small und
  large-v3-turbo-q5_0, Parakeet TDT 0.6B v3 (CC-BY-4.0, Deutsch) über
  sherpa-onnx 1.13.8. Alle Prüfsummen bestanden, Selbsttest grün. Hardware:
  i7-8665U, 4 Kerne/8 Threads, AVX2, 46 GB.

  **Messen** mit `scripts/dialos-erkenner-vergleich.py`: Vorlage
  `docs/einkaufszettel-vorlage.md` (20 Waren + Brieftext ohne gesprochene
  Satzzeichen), eine Aufnahme, dieselben an Sprechpausen geschnittenen Stücke
  für alle Erkenner; ausgegeben werden Waren wörtlich, Wortfehlerrate,
  Ladezeit und Zeit je Stück. Aufnahmen bleiben lokal, nie im Repo.

  **Offen, bevor gewechselt werden könnte:** Whisper erfindet in Stille
  manchmal Text (nur Stücke mit Sprache übergeben); Whisper schreibt nicht
  mit, sondern bekommt fertige Stücke; die Wartezeit je Ware auf dem T490.
  Satzzeichen und Großschreibung kämen bei Whisper und Parakeet mit - an
  Kommas ließen sich Einträge wie „Birnen, Äpfel" trennen.

  **Probe mit Annas Stimme (2026-09-14, 14:26) - Ablauf geprüft, Genauigkeit
  NICHT verwertbar.** Alle vier Erkenner scheiterten gleich an den kurzen
  Waren („Bananen" → „fein"/„Dann…"/„Nein."), nur lange Waren wie „zwei Liter
  Milch" kamen an. Gegenprobe: auch ungeschnitten und mit angeglichener
  Lautstärke versteht Vosk aus „Bananen." nur „ein". `kerstin-low` taugt als
  Sprecherin für einzelne Wörter in freier Erkennung nicht - für Befehle in
  fester Grammatik schon. **Die Zeiten sind aber echt:**

  | Erkenner | Laden | je Stück (≈1 s Sprache) |
  |---|---|---|
  | Vosk groß (heute) | 11,8 s | 0,30 s |
  | Parakeet v3 | **1,9 s** | **0,26 s** |
  | Whisper small | 12,6 s | **7,05 s** |
  | Whisper turbo q5 | 43,6 s | **40,77 s** |

  **Whisper ist in dieser Form auf dem T490 zu langsam** - vermutlich, weil
  whisper.cpp jedes Stück auf ein 30-Sekunden-Fenster auffüllt und die
  Rechenzeit damit je Stück fast gleich bleibt, egal wie kurz es ist. Zu
  prüfen: die Option `--audio-ctx` (kürzeres Fenster). **Parakeet ist so
  schnell wie Vosk und lädt sechsmal schneller.** Welcher Stephan am besten
  versteht, zeigt erst seine Aufnahme am 2026-09-15.

  **Stephans Einkaufszettel (2026-09-15, 10:36) - VOSK VORN.** 36 s, mit
  Pausengrenze 0,2 s genau 20 Stücke (bei 0,45 s nur 14 - er sprach zügig,
  Pausen gegen Ende 0,24-0,45 s, innerhalb einer Ware unter 0,15 s):

  | Erkenner | Waren wörtlich | Wortfehler | je Ware |
  |---|---|---|---|
  | **Vosk groß (heute)** | **16/20** | **14,8 %** | 0,25 s |
  | Parakeet v3 | 11/20 | 40,7 % | 0,24 s |
  | Whisper small | 13/20 | 29,6 % | 6,17 s |
  | Whisper small `-ac 512` | 13/20 | 29,6 % | 2,02 s |
  | Whisper turbo `-ac 512` | 13/20 | 40,7 % | 12,99 s |

  **Warum:** Einzelne Wörter ohne Zusammenhang sind nicht die Stärke von
  Whisper/Parakeet. Parakeet rutscht ins Englische („Faz it?", „Rice",
  „Cacao"), Whisper erfindet („2 Liter Wildschwein", „Coffee. Coffee.",
  „Zahnpasta Zahnpasta"). Strenge Wertung zählt auch Schreibweisen
  („Brocoli", „Jogurt", „500 g") - mit Nachsicht käme Whisper small auf etwa
  15/20, weiter nicht vor Vosk. Vosks Fehler: Birne(n), „erzähl" (Äpfel),
  „Monsterwelle" (Mozzarella), „Surimi" (Zucchini) - vor allem Fremdwörter.
  **Folgerung:** Die Einkaufszettel-Probleme vom 14.09. lagen überwiegend nicht
  an Vosk, sondern an Aufnahmebeginn, Schlusssatz und Fehl-Schluss - alle am
  14.09. behoben. Eine Aufnahme, ein Sprecher. Offen: Brief-Absatz (ganze
  Sätze - dort sind Whisper und Parakeet stärker).

  **Stephans Brief-Absatz (2026-09-15, 10:55) - PARAKEET VORN.** Zweite
  Aufnahme (die erste wurde dreimal von der Zu-laut-Ansage unterbrochen, siehe
  Maßnahme B). 40 s, 7 Satz-Stücke (Pausengrenze 0,45 s, längstes 9,2 s).
  Stephan sprach „Komma"/„Punkt" mit, wie im DialOS-Diktat gewohnt - die
  Wortfehler sind deshalb OHNE diese Wörter gerechnet:

  | Erkenner | Wortfehler | je Satz | Laden | gestörte Aufnahme |
  |---|---|---|---|---|
  | **Parakeet v3** | **3,0 %** | **0,47 s** | 1,8 s | 37,9 % |
  | Vosk groß (heute) | 7,6 % | 0,88 s | 9,5 s | 60,6 % |
  | Whisper small | 18,2 % | 5,50 s | 11,6 s | 39,4 % |
  | Whisper small `-ac 512` | 25,8 % | 1,76 s | 6,0 s | 63,6 % |
  | Whisper turbo `-ac 512` | 39,4 % | 13,54 s | 13,4 s | 45,5 % |

  Parakeet: ganzer Absatz mit einem Fehler („teilen das bitte mit"), mit
  Satzzeichen und Großschreibung; verkraftet Störungen deutlich besser als
  Vosk. Whisper: erfindet (turbo schrieb einen Satz dreimal), small ließ den
  letzten Satz weg - auf dem T490 in beiden Tests hinten.

  **Mögliche Aufteilung (zu entscheiden):** Vosk für Befehle, Einkaufszettel
  und Notizen; Parakeet für den Brief. **Folge:** Parakeet setzt Satzzeichen
  selbst - gesprochene „Punkt"/„Komma" ergäben „Muster. Punkt.". Beim Brief
  spräche der Nutzer dann natürlich, ohne Satzzeichen-Befehle (einfacher,
  aber ohne Kontrolle über jedes Komma). Ein Sprecher, eine ungestörte
  Aufnahme je Art, ruhiger Raum - deutlicher Hinweis, kein Beweis.

- [x] **Umlaut-Wörter fehlen NICHT im Wortschatz - drei Entscheidungen waren
  wieder offen, alle drei am selben Tag entschieden** (gefunden 2026-09-14 bei Stephans Frage nach Dialekten).
  Jedes Wort, das Vosk seit August als „missing in vocabulary" gemeldet hat,
  enthielt ä, ö, ü oder ß. Ursache: `json.dumps` ohne `ensure_ascii=False`
  macht aus „ö" ein `\u00f6`. Richtig übergeben, nimmt das Modell „später",
  „löschen", „zurücksetzen", „aufräumen", „nö", „tschüss" an. **Behoben** in
  allen Grammatiken (am Verhalten ändert das heute nichts - es gab bisher
  kein Umlaut-Wort in einer Grammatik, eben wegen des falschen Befunds).
  **Neu zu entscheiden (Stephan), jeweils mit Hörprobe Piper → Vosk vorher:**
  1. „später" als Widerspruch beim Update - Stephans ursprünglicher Wunsch.
     Ein Wort ist anfälliger für Nebengeräusche als zwei.
  2. „Einkaufszettel löschen" zusätzlich zu „wegwerfen"/„Einkauf erledigt".
  3. „Wie spät ist es?" zusätzlich zu den beiden Uhrzeit-Fragen.
  Dazu Mundart-Formen für die Rückfrage („jo", „joa", „nee", „nö") - siehe
  den Punkt zu Dialekten.
  **Entschieden am 2026-09-14 nach Hörprobe (Piper → Vosk, Anna und
  Michael):** alle drei eingebaut. „wie spät ist es" und „einkaufszettel
  löschen" wörtlich erkannt, alle 28 Befehlssätze danach fehlerfrei;
  „einkaufszettel löschen" wird nie vorgeschlagen. „später" beim Update
  erkannt, „nicht jetzt" mit Anna dagegen nicht - „später" ist jetzt das
  angesagte Wort, „nicht jetzt" gilt weiter. **Offen:** Probe mit echter
  Stimme.

- [ ] **Dialekte: Deutschland, Österreich, Schweiz** (Stephans Anforderung vom
  2026-09-14: „Wir müssen die Sprachsteuerung ja so sauber hinbekommen, dass
  auch sowas wie Dialekte Deutschland/Österreich/Schweiz auch mit
  aufgefangen werden"). **Lage:** Das große Modell ist laut README auf
  Tuda-de, SWC, M-AILABS und Common Voice trainiert - überwiegend
  vorgelesenes Hochdeutsch; Common Voice bringt Sprecher aus Österreich und
  der Schweiz mit. Schweizerdeutsch als Mundart ist praktisch nicht abgedeckt.
  **Die Befehlserkennung ist toleranter als das Diktat:** Sie muss nur
  zwischen 27 Sätzen wählen. **Geprüft ist bisher nichts** - Piper spricht nur
  Hochdeutsch, als Prüfung taugt es hier nicht. **Vorschlag:** ein Prüfstand,
  der aufgenommene Sprechproben durch genau die Erkennung und Zuordnung des
  Dienstes schickt und die Trefferquote ausgibt (derselbe Prüfstand dient B
  und C); Aufnahmen der Befehle von einigen Menschen aus AT, CH und
  deutschen Mundartregionen - mit Einwilligung, nur lokal, nie im Repo;
  danach entscheiden: Mundart-Varianten in der Grammatik oder ein anderes
  Modell (z. B. Whisper - robuster bei Akzenten, aber auf dem T490 langsamer).
  **Zeitpunkt, von Stephan entschieden (2026-09-14): ganz zum Schluss, wenn
  alle Befehle stehen** - „das würde ich ganz zum Schluss machen, wenn alle
  Befehle stehen!". Sonst müssten die Sprecher nach jeder Änderung neu
  aufnehmen. Stephan kennt Leute aus Österreich und der Schweiz dafür.

  **Wofür die Aufnahmen eingebunden werden** (Stephan, 2026-09-14: „Dann
  können wir mehrere Personen die Befehle zur Verfügung stellen und dann in
  unser System mit einbinden. Dann ist das sauber integriert"):

  | Verwendung | Nutzen |
  |---|---|
  | Prüfdaten im Prüfstand | Trefferquote je Befehl und Mundart - zeigt, wo es hakt |
  | Einstellen | Mundart-Varianten in die Grammatik („jo", „nee" …), Schwellen anpassen |
  | Trainingsdaten fürs Aufweckwort (Maßnahme C) | openWakeWord wird mit vielen verschiedenen Stimmen trainiert - mehr Sprecher aus DE/AT/CH machen es robuster, auch gegen Fernsehton |

  **Nicht vorgesehen:** Vosk selbst nachtrainieren - dafür braucht es Stunden
  an Material, nicht einige Dutzend Aufnahmen.

  **Voraussetzung: schriftliche Einwilligung jeder Person.** Stimmaufnahmen
  sind personenbezogene Daten. Die Einwilligung muss nennen, wofür die
  Aufnahme verwendet wird (Prüfung, Training), ob ein daraus trainiertes
  Modell mit DialOS ausgeliefert wird, und wie man sie zurückzieht. Die
  Aufnahmen selbst kommen **nie ins öffentliche Repo**. Die
  Einwilligungsvorlage wird geschrieben, wenn die Aufnahmen anstehen.

- [ ] **Der Sprachdienst überlebt das Abmelden - danach laufen ZWEI**
  (gefunden 2026-09-14, 12:13). Nach Ab- und Anmelden liefen
  `dialos-sprachbefehl-desktop.py` von 11:49 (alte Fassung) und von 12:09
  nebeneinander, beide in eigenen Autostart-Einheiten. Im Protokoll standen
  „anderer Dienst hoert zu" und „fertig" je doppelt. Zwei Dienste, die
  zuhören, können einen Befehl doppelt ausführen - und nach einem Update läuft
  still die alte Fassung weiter. Die alte Instanz ist beendet. **Zu klären:**
  warum GNOME sie beim Abmelden nicht beendet (die Sitzung „manager" blieb
  bestehen), und eine Ein-Instanz-Sperre wie bei `dialos-start-ansage.py`.
  Offen auch, ob das bei früheren Tests mitgespielt hat.
  **Gebaut am 2026-09-14** (Stephan: „Dann musst du beim Abmelden den
  Sprachbefehl auch resetten"): Beim Start beendet der Dienst jede ältere
  Instanz desselben Kontos (SIGTERM, nach 3 s SIGKILL) - beim Start statt beim
  Abmelden, weil genau das Abmelden unzuverlässig war. Mit Attrappen geprüft,
  auch mit einer, die SIGTERM ignoriert; der laufende Dienst blieb unberührt.
  **Offen:** Beweis beim nächsten Ab- und Anmelden („aeltere Instanz beendet"
  im Protokoll oder nur ein Prozess) - und die Ursache beim Abmelden.

- [ ] **Ansagen anderer Dienste unterbrechen das Diktat** (2026-09-14, 12:11:29).
  Mitten im Einkaufszettel-Diktat sagte die Netzwerküberwachung „Die
  Internetverbindung wurde gerade unterbrochen …". Das Diktat hört über die
  Echo-Unterdrückung, aber der Nutzer wird aus dem Diktieren gerissen. Die
  Marke „ein anderer Dienst hört zu" müsste auch Hinweise wie diesen
  zurückhalten, bis das Diktat fertig ist.

- [ ] **Das Kundenkonto `nutzer` hat volle Root-Rechte** (gefunden am
  2026-09-14, als Stephan fragte, ob die neue Update-Regel den Konten etwas
  wegnimmt).

  **Der Befund.** `sudo -l -U nutzer` sagt:

      (ALL : ALL) ALL

  `nutzer` ist Mitglied der Gruppe `sudo` — zusammen mit `cdrom`, `audio`,
  `video`, `plugdev`, `users`, `netdev`, `scanner`, `bluetooth`, `lpadmin`.
  Damit darf das Kundenkonto mit Passwort **alles**, nicht nur die eng
  gefassten NOPASSWD-Aufrufe.

  **Warum es heute nicht brennt:** Das Passwort wurde bei der Einrichtung
  zufällig erzeugt und ist niemandem bekannt. Die Tür ist also zugezogen.
  **Abgeschlossen ist sie nicht:** Wer das Passwort setzt — ein Helfer, ein
  Reparaturdienst, jemand mit kurzem physischem Zugang —, hat root auf dem
  Gerät eines blinden Nutzers, der das nicht bemerken kann.

  **In CLAUDE.md steht das seit Langem als „noch offen"**, und diese
  Formulierung ist irreführend: Sie klingt, als sei noch nichts entschieden.
  Der tatsächliche Zustand ist **voller Administrator** — eine Entscheidung,
  auch wenn sie niemand getroffen hat.

  **Nicht einfach die Gruppe entfernen.** Was dann bricht, ist ungemessen.
  Gemessen ist bisher nur, was DialOS als `nutzer` über `sudo` aufruft — und
  das ist wenig, weil alles über NOPASSWD-Regeln auf feste Pfade läuft:

  | Skript | Aufruf |
  |---|---|
  | `dialos-stimme-wechseln.py` | `dialos-stimme.py setzen <stimme>` |
  | `dialos-update-lauf.py` | `dialos-systemupdate pruefen/installieren/neustarten` |

  Beide brauchen die Gruppe `sudo` **nicht** — eine NOPASSWD-Regel wirkt
  unabhängig davon. Der Verdacht ist also, dass die Mitgliedschaft nur
  mitgeschleppt wurde, weil `dialos-setup-nutzer.sh` das Konto wie ein
  normales Desktop-Konto angelegt hat.

  **Zu klären, bevor etwas geändert wird:**
  1. Woher kommt die Mitgliedschaft? `scripts/dialos-setup-nutzer.sh` bzw.
     `dialos-buero-setup-abschliessen.sh` durchsehen. Wenn sie dort
     ausdrücklich gesetzt wird, gab es vielleicht einen Grund.
  2. Welche der übrigen Gruppen braucht `nutzer` wirklich? `audio`, `video`,
     `bluetooth`, `lpadmin` (Drucken), `netdev` (WLAN) sind plausibel;
     `cdrom`, `scanner`, `plugdev` sind zu prüfen.
  3. Was passiert beim Entfernen mit den Tastenkürzeln, der Fernwartung und
     `dialos-aufspielen`? Letzteres ist ohnehin nur für das
     Entwicklungsgerät.
  4. **Und die Gegenprobe nicht vergessen:** Nach dem Entfernen muss ein
     vollständiger Durchlauf her — anmelden, Stimme wechseln, Update, Diktat,
     Drucken. Ein Rechteentzug, der erst drei Wochen später auffällt, ist
     schlimmer als der heutige Zustand.

- [x] **Update-Automatik: gebaut und am Gerät gelaufen - vollständig belegt (2026-09-14)** (Stephans Vorgabe vom 2026-09-14, am selben Tag gebaut: „Ich würde das
  mit dem Update gerne jetzt einbauen").

  Alle 14 Tage, montags nach dem Anmelden, mit Nachholen; zehn Sekunden
  Widerspruch auf **„nicht jetzt"** („später" fehlt im Wortschatz des Modells);
  Neustart nur mit Sicherheits-Stick; danach „Der Computer ist auf dem neuesten
  Stand." Der echte Lauf am 2026-09-14 ist durchgelaufen, ohne Schleife nach dem
  Neustart. Aufbau, Begründungen und Prüfprotokoll: Schritt 13d in
  [docs/Debian-zu-DialOS.md](docs/Debian-zu-DialOS.md).

  **Offen:**

  1. ~~Stephans Durchsicht der sudoers-Regel~~ **Erledigt 2026-09-14:** Stephan
     hat `/etc/sudoers.d/dialos-systemupdate` angesehen (Prüfsumme Gerät =
     Repo, `afa162ca…9ffc`) und freigegeben: „Ja, ich gebe die Regel frei". Bei
     der Durchsicht kam dazu, dass `neustarten` nur nach einem echten Update
     seit dem letzten Start neu startet. Der Eintrag in der NIEMALS-Liste von
     `dialos-aufspielen` ist entfernt.
  2. **Der Satz nach dem Neustart über zwei Konten, am Gerät.** Im echten Lauf
     hörte ihn nur `dialosadmin` (der ausgelöst hatte), nicht `nutzer`.
     Repariert: Zeitstempel beim Rechner, Quittung pro Person - in einer
     Sandbox mit zwei Heimatverzeichnissen geprüft. Für den Lauf vom 14.09.
     gibt es keinen Zeitstempel; **beim nächsten echten Update** zuerst als
     `nutzer`, dann als `dialosadmin` anmelden - beide müssen den Satz genau
     einmal hören.
     **Erledigt am 2026-09-14, 13:26-13:29** - früher als gedacht, weil das
     Firmware-Update (UEFI dbx) über die Automatik einen echten Zeitstempel
     geschrieben hat. Nach dem Neustart zuerst `nutzer` (Autologin): Satz kam
     nach der Begrüßung (Stephan: „Der Eintrag war dort auch richtig"). Dann
     `dialosadmin`: Satz einmal, 13:29:28. Stephans übliche Reihenfolge („Ich
     starte ja immer mit dem Nutzer und melde mich dann ab und DialOS-Admin
     an") ist genau die, die am Vormittag gescheitert war.

  **Nebenbei zu klären:** Der Sprachbefehl „System aktualisieren" steht in
  `docs/sprachbefehle.md` als vorgesehen. Er wäre ein zweiter Auslöser für
  dasselbe Werkzeug - `dialos-update-lauf.py --jetzt` gibt es schon.

- [ ] **Brief einsprechen - geplant für Dienstag, 2026-09-15** (Stephan am
  2026-09-14: „Punkt 1 bitte auf Dienstag legen"). Die Vorlage liegt fertig in
  [docs/brief-vorlage.md](docs/brief-vorlage.md): Zielbild, was DialOS davon
  heute kann, und der Diktattext Wort für Wort mit den gesprochenen
  Satzzeichen. Nichts zu bauen — es ist der fehlende **Beweis am Gerät**, dass
  ein Diktat mit echter Stimme von Anfang bis Ende durchläuft.

  Vorher lohnt sich `absender.txt` (siehe Abschnitt 2 der Vorlage): Sonst steht
  im Briefkopf nur „Stephan" ohne Straße und Ort.

- [ ] **Die Sprachsteuerung ließ sich am 2026-08-24 einmalig nicht einschalten
  - am 2026-09-14 nicht mehr nachstellbar** — und ein Pegelverdacht ist ungeprüft offen.

  **NACHTRAG VOM 2026-09-14, und er entkräftet den Verdacht.** Stephan hat um
  08:16 und 08:17 zweimal „Sprachsteuerung starten" gesprochen, und **beide Male
  ist der ganze Satz angekommen** — bei ZURÜCKGESETZTEM Pegel, denn der Neustart
  hat die Absenkung vom 24.08. verworfen (Quelle wieder bei 32 %, `Capture` bei
  100 %). Die Spitzen lagen bei 27663 und 15257, also im selben Bereich wie an
  dem Abend, an dem es NICHT ging.

  **Damit ist der Pegel als Ursache so gut wie ausgeschlossen.** Es war
  offenbar ein vorübergehender Zustand an diesem einen Abend. Was übrig bleibt:
  Der Punkt ist nicht gelöst, sondern nicht mehr beobachtbar — und das ist ein
  Unterschied. Tritt es wieder auf, steht jetzt die Pegelspalte im Protokoll
  und lässt sich sofort mit diesen Zahlen vergleichen.

  **Der Befund.** Zwischen 17:01 und 17:06 stand im Protokoll ausschließlich
  `starten`, `[unk]` und `sprachsteuerung` — **kein einziges Mal
  `sprachsteuerung starten`**. Dreizehn Versuche, keiner erfolgreich. Damit kam
  auch die neue Ansage nie zum Zug: Sie greift nur im eingeschalteten Zustand.

  **Der Verdacht, gestützt auf die neue Pegelspalte.** Die Spitzen lagen bei
  **21935 bis 30499** von 32768 — 67 bis 93 % des Vollausschlags. Die
  Sättigungsschwelle im Dienst liegt bei 32000, sie hat also nie gegriffen.
  Vosk erkennt Sprache aber an den **Pausen zwischen Wörtern**; bei diesem
  Pegel verschmieren die, und aus zwei Wörtern wird eines. Genau dieser
  Mechanismus war am 2026-08-16 schon einmal die Ursache — damals durch
  „Capture +30 dB UND Internal Mic Boost +30 dB".

  **Was am 2026-08-24 abends geändert wurde — NUR ZUR LAUFZEIT, nichts im
  Repo:** die Lautstärke der Quelle `alsa_input.pci-…analog-stereo` von 35 %
  auf **18 %**. Wirkung gemessen: Leerlaufpegel von 52 auf **17**, Spitze von
  150 auf 99. Die Echo-Quelle `dialos_mikrofon_ohne_echo` steht selbst auf
  100 % und erbt vom Rohsignal, der Regler greift also beim Dienst.
  **Ein Neustart setzt das zurück**, weil `dialos-mikrofon-pegel.service`
  wieder `CAPTURE_PEGEL="100%"` setzt.

  **Ein Umweg, der dokumentiert gehört:** Zuerst wurde ALSA `Capture` direkt
  auf 50 % gestellt. Dabei fiel die PipeWire-Lautstärke von 35 auf 13 % —
  beide Regler sind gekoppelt und wurden gegeneinander verstellt. Das wäre
  vermutlich zu leise geworden. Es hängt jetzt alles an einem Regler.

  **Morgen zuerst:**
  1. „Sprachsteuerung starten" sprechen. Kommt der ganze Satz durch?
  2. Die Spitzen im Protokoll ablesen — liegen sie jetzt bei etwa
     11000 bis 15000?
  3. **Hilft es nicht, war die Diagnose falsch.** Dann liegt es nicht am Pegel,
     und es wird anders gemessen: Stephans Stimme aufnehmen und prüfen, ob die
     Pause zwischen „Sprachsteuerung" und „starten" überhaupt ankommt. Eine
     plausible Erklärung ist noch keine Ursache — das war in diesem Projekt
     schon zweimal der Fehler.
  4. Erst danach entscheiden, ob `CAPTURE_PEGEL` im Skript geändert wird.

- [ ] **Kundendaten an EINER Stelle - und nicht unverschlüsselt** (Stephans
  Anstoß vom 2026-08-24: „wo wir zentral alle wichtigen Daten des Kunden
  einmalig ablegen und die Mail, der Brief und das Diktat usw. greifen auf
  diese Daten immer zu").

  **Wie es heute aussieht.** Dieselbe Person steht an mehreren Stellen, jede
  mit eigenem Format:

  | Was | Wo | Wer liest es |
  |---|---|---|
  | Name, gesprochen und geschrieben | `/usr/local/share/dialos/nutzer-name.txt` | Start-Ansage, Briefbogen, Anrede |
  | Anschrift | `/usr/local/share/dialos/absender.txt` | Briefbogen - **existiert nicht** |
  | Fußzeilentext | `/usr/local/share/dialos/fusszeile.txt` | Mail, Brief, Ausdruck |
  | Mail-Signatur | `mail-signatur.txt` / `.html` | Thunderbird (erzeugt) |
  | Mailbox-Zugangsdaten | Datei in `/home/nutzer`, 0600 | Mailabruf |

  **Der schwerwiegende Teil ist nicht die Verteilung, sondern der Ort.**
  Gemessen am 2026-08-24:

      /usr/local/share/dialos/nutzer-name.txt  →  /dev/nvme0n1p1  ext4   0644
      /home/nutzer                             →  nvme0n1p4       LUKS

  Der Name des Kunden liegt **unverschlüsselt und für jeden lesbar** auf der
  Wurzelpartition, während seine Briefe hinter LUKS liegen. Die Anschrift soll
  laut Briefbogen an denselben Ort. Bei einem gestohlenen Laptop ist damit
  genau das lesbar, was die Person identifiziert - und der Zweck der
  verschlüsselten Home-Partition ist zur Hälfte hinfällig. Siehe
  `docs/sicherheit-datenschutz.md`.

  **Zweiter Fehler, derselbe Ort:** Die Dateien sind systemweit, die Daten aber
  personenbezogen. Auf dem Entwicklungsgerät teilen sich `dialosadmin` und
  `nutzer` denselben Namen - ein Brief des Admin-Kontos trüge den Namen des
  Kunden.

  **Vor dem Bauen zu klären:**
  1. **Wohin?** `/home/nutzer/.config/dialos/` liegt auf der verschlüsselten
     Partition und ist personenbezogen - beides richtig. **Die Startreihenfolge
     spricht NICHT dagegen**; das stand hier zuerst und war falsch (berichtigt
     2026-08-24). `dialos-stick-gate` läuft `Before=display-manager.service`,
     mountet die Partition und schaltet erst danach Autologin ein - ohne Stick
     sperrt er das Konto sogar. Hat `nutzer` eine Sitzung, ist die Partition
     immer gemountet. Offen bleibt nur: Das ADMIN-Konto käme nicht heran
     (`/home/dialosadmin` liegt auf der Wurzelpartition), und der Gate selbst
     könnte die Daten nie lesen, falls er einmal sprechen soll.
  2. **Welches Format?** Fünf Dateien mit fünf Formaten sind der heutige Stand.
     Eine Datei mit klaren Feldern (Name gesprochen, Name geschrieben, Straße,
     Ort, Telefon, Mailadresse) wäre lesbar und erweiterbar.
  3. **Was ist NICHT Kundendatum?** `assistent-name.txt` (Michael/Anna) und
     `fusszeile.txt` sind Systemeinstellungen und gehören nicht dorthin. Die
     Trennlinie muss gezogen werden, sonst wandert am Ende alles in eine Datei
     und niemand weiß mehr, was beim Kundenwechsel zu löschen ist.
  4. **Was passiert beim Wechsel?** Ein Gerät, das an eine andere Person geht,
     muss diese Daten sicher loswerden. Eine zentrale Stelle macht das
     möglich - fünf verstreute Dateien machen es unzuverlässig.

  **Erst danach** lohnt sich der geführte Dialog für Empfänger und Betreff
  (siehe `docs/brief-vorlage.md`): Er würde sonst auf einen Datenbestand
  aufsetzen, der gerade umzieht.

- [ ] **Stimmprobe beim ersten Anmelden - und die Aufnahme danach löschen**
  (Stephans Idee vom 2026-08-24: „wenn alles funktioniert, dem neuen Benutzer
  einen Text präsentieren … damit das System eine Stimmenprobe von der Person
  hat, die dann mit DialOS kommuniziert").

  **NICHT VORHER ANFANGEN** (Stephan, 2026-08-24): „Das sollten wir ja erst
  angehen, wenn alles mit meiner Stimme reibungslos läuft." Das ist die richtige
  Reihenfolge, und zwar nicht nur aus Zeitgründen: Die Stimmprobe MISST gegen
  den bestehenden Stand. Solange sich Schwellen, Grammatik und Zuordnung noch
  ändern, misst sie ein bewegliches Ziel - und jede Zahl, die dabei
  herauskommt, wäre beim nächsten Umbau wieder falsch. Erst wenn es mit
  Stephans Stimme trägt, ist der Schritt zu einer fremden Stimme überhaupt ein
  Schritt und nicht bloß eine zweite Baustelle.

  **Wofür sie NICHT gut ist, damit niemand das Falsche baut:** Die Erkennung
  wird davon nicht besser. Vosk ist sprecherunabhängig und lernt aus einer
  Probe nichts; es gibt in diesem Aufbau keine Sprecheranpassung.

  **Wofür sie gut ist: drei geratene Zahlen durch gemessene ersetzen.** Alle
  drei sind heute offene Punkte:

  - **Der Pegel dieser Person.** DialOS arbeitet mit Schwellen, die an
    Stephans Stimme gemessen sind (Sprache 3475-4196 gegen Rauschen 47-84).
    Wer leiser spricht, fällt darunter - und dann passiert nichts, ohne dass
    jemand weiß warum. Siehe auch den Punkt zur fehlenden Selbstprüfung.
  - **Die Sprechpausen dieser Person.** Das Diktat trennt Einträge nach
    0,4 s Pause. Diese Zahl ist **geraten** - es steht ausdrücklich so im
    Punkt „Einträge trennen" weiter oben. Wer langsam spricht, bekommt seinen
    Einkaufszettel in Einzelwörter zerlegt.
  - **Ein Abnahmetest.** Werden alle Befehlssätze in DIESER Stimme erkannt?
    Heute stellt sich das erst heraus, wenn der Nutzer allein mit dem Gerät
    ist.

  **Wie der Text gebaut sein muss:** jeder Befehlssatz genau einmal darin, und
  dazwischen natürliche Sätze für die Pausenmessung. Nicht länger als eine
  Minute - für einen ungeübten Nutzer ist Vorlesen ohnehin eine Prüfung, und
  eine lange Prüfung am ersten Tag schreckt ab.

  **Die Aufnahme wird nach der Messung gelöscht** (Stephans Entscheidung vom
  2026-08-24). Behalten werden nur die Zahlen: Pegel, Pausenlängen,
  Trefferquote je Befehl. Damit liegt kein Sprachmitschnitt des Nutzers auf
  dem Gerät, und die Werte, die DialOS braucht, sind trotzdem da. Das Löschen
  gehört in denselben Programmlauf wie die Messung - eine Aufnahme, die
  „später" gelöscht wird, bleibt liegen.

  **Vorher zu klären:**
  1. Wohin mit den Zahlen? Eine Datei je Konto, oder in die bestehende
     Konfiguration? Sie müssen einen Reinstall überleben oder bewusst nicht.
  2. Was passiert, wenn die Probe schlecht ausfällt - zu leise, zu wenige
     Befehle erkannt? Wiederholen, mit anderem Mikrofon versuchen, oder
     abnehmen und dem Helfer melden? Ein Nutzer, der beim ersten Versuch
     durchfällt, darf nicht ohne Weg dastehen.
  3. Läuft sie beim ERSTEN Anmelden automatisch, oder ruft der Helfer sie auf?
     Automatisch heißt: Der Nutzer wird beim ersten Kontakt geprüft, bevor er
     weiß, was das Gerät kann.

- [ ] **Keine Selbstprüfung, ob das Gerät überhaupt noch spricht** (offen seit
  2026-08-24, aufgefallen am stummen `paplay`). Am 2026-08-24 war jeder
  `paplay`-Strom stummgeschaltet, weil PipeWire sich das je Anwendung merkt.
  Folge: alle **zwischengespeicherten** Ansagen lautlos, dazu Frageton und
  Testton. `paplay` gibt dabei 0 zurück, `aus_speicher()` hält die Ansage für
  geglückt und fällt nicht auf `spd-say` zurück.

  **Für einen blinden Nutzer ist das der schlimmste Fall überhaupt:** Das
  Gerät ist stumm, es steht nirgends ein Fehler, und er kann nicht nachsehen.
  Die Ursache ist behoben (siehe Änderungsprotokoll), aber die **Klasse** des
  Fehlers nicht: Es gibt keine Stelle, die merkt „ich habe gesprochen, aber es
  war nichts zu hören".

  **Was zu klären ist, bevor etwas gebaut wird:** Woran lässt sich das
  überhaupt messen? Kandidaten: den eigenen Strom nach dem Anlegen auf `Mute`
  prüfen (billig, fängt genau diesen Fall), oder den Pegel der Senke während
  der Ansage lesen (fängt mehr, ist aber aufwendiger und bei Kopfhörern
  zweifelhaft). Nicht raten - erst prüfen, was PipeWire wirklich hergibt.

  **Und wie sagt man es?** Eine Ansage kann es nicht sein - die wäre ja
  ebenfalls stumm. Bleibt: Protokoll, Mitschrift-Fenster, und beim nächsten
  Anmelden ein sichtbarer Hinweis für den Helfer.

- [ ] **Erster Fehlstart der Sprachsteuerung - Ursache offen** (2026-08-24).
  Um 14:41:12 hat sich die Sprachsteuerung selbst eingeschaltet: Vosk erkannte
  „sprachsteuerung starten", das Mitschrift-Fenster ging auf, danach kamen
  „datum vorlesen drucken" und „welchen". **Stephan hatte an diesem Tag kein
  Wort zur Sprachsteuerung gesagt.**

  **Was ausgeschlossen ist:** die eigene Ansage. Im Ton-Protokoll steht
  zwischen 14:35 und 14:42 keine einzige Zeile, DialOS hat also nicht selbst
  gesprochen. Die Echo-Unterdrückung war damit gar nicht gefordert.

  **Was offen ist:** was das Mikrofon gehört hat. Umgebungssprache (Gespräch
  im Raum, Radio, Video) ist die naheliegende Vermutung - aber eine Vermutung,
  und dieses Projekt hat schon zweimal an einer schlüssigen Vermutung
  vorbeigemessen. Zu klären ist zuerst mit Stephan, ob um 14:41 jemand oder
  etwas im Raum gesprochen hat.

  **Warum es zählt:** Die Zwei-Wort-Regel ist genau dafür gebaut, dass ein
  beiläufiges Wort nichts auslöst. Wenn Umgebungssprache sie überwindet, ist
  ein selbsttätiges Einschalten samt Fenster und ausgeführten Befehlen
  möglich, ohne dass jemand mit dem Gerät spricht. Beim blinden Nutzer wäre
  das Fenster unsichtbar - er merkt nur, dass das Gerät plötzlich zuhört.

- [ ] **Erlaubte Wortkombinationen ohne Befehl fallen LAUTLOS durch** (offen
  seit 2026-08-22, gefunden beim Drucktest). Der schwerwiegendste offene Punkt
  für die Zielgruppe.

  **Was passiert.** Die eingeschränkte Grammatik ist eine Liste von SÄTZEN,
  aber Vosk baut daraus ein WORTNETZ und darf Wörter aus verschiedenen Sätzen
  kombinieren. Kommt dabei etwas heraus, das kein Befehl ist, passiert nichts -
  und es wird auch nichts gesagt. Stephan sagte „notiz drucken", die Grammatik
  kannte nur „notizen drucken", nichts geschah, keine Ansage.

  **Warum das schlimmer ist als ein Fehler.** Ein sehender Nutzer sieht ein
  Fenster, das sich nicht öffnet, oder ein Blatt, das nicht kommt. Ein blinder
  Nutzer hat gesprochen, das Gerät hat zugehört, und nichts sagt ihm, dass
  nichts geschah. Er weiß nicht einmal, ob er falsch gesprochen hat oder ob das
  Gerät kaputt ist. Eine Fehlermeldung wäre besser gewesen.

  **Gemessen am 2026-08-22** aus allen `~/.log/dialos-sprachbefehl.log*`,
  Zustände getrennt gezählt:

  | | Anzahl |
  |---|---|
  | Gültige Befehle | 98 |
  | `[unk]` (Geräusch) | 191 |
  | AUS-Zustand, kein Treffer | 345 |
  | **AN-Zustand, kein Treffer** | **382** |

  Die 345 im AUS-Zustand sind fast alle Bruchstücke von „sprachsteuerung
  starten". **Dort ist Schweigen richtig und muss so bleiben** - das ist die
  Zwei-Wort-Regel, die 60 Beinahe-Treffer und lange null Fehlstarts gebracht
  hat - der erste kam am 2026-08-24 (siehe eigener Punkt oben). Nur
  die 382 im EINGESCHALTETEN Zustand sind der Fehler.

  **Und da liegt das Dilemma:** 382 Ansagen wären unerträglich. Das Gerät würde
  bei jedem Nebengespräch dazwischenreden. Die Frage ist also nicht, OB etwas
  gesagt wird, sondern WANN - und dafür fehlt ein Kriterium, das gemessen und
  nicht geraten ist.

  **Was schon dagegen spricht, es einfach zu bauen:** Von den 382 sind 159
  Einwort-Bruchstücke („wir", „es", „auf", „viel"). Bleiben 223 mehrwortige
  ohne `[unk]` - immer noch zu viele. Darunter „haben wir" (15x), „die
  uhrzeit", „welchen haben wir": Das sind Gesprächsfetzen, keine
  Befehlsversuche.

  **Nächster Schritt, in dieser Reihenfolge:**
  1. Eine Stichprobe der 223 mit Stephan durchgehen. Nur er kann sagen, welche
     davon ein Befehlsversuch waren - das Protokoll kann es nicht.
  2. Erst danach ein Kriterium festlegen. Der Pegelmesser aus dem Diktat
     (`PEGEL_SCHWELLE`, Sprache 3475-4196 gegen Rauschen 47-84) ist ein
     Kandidat, aber er unterscheidet Sprechen von Stille, nicht Absicht von
     Beiläufigkeit.
  3. Die Ansage selbst muss knapp sein und darf nicht belehren. „Das war kein
     Befehl" ist besser als ein Satz, der die ganze Liste vorliest.

- [ ] **ZURUECKGESTELLT: dialos-hilfe.py auf den Dienst umbauen** (Stephan,
  2026-08-20: "können den Rustdesk ganz nach hinten schieben, wenn alles
  andere läuft"). Die zwei Sprachbefehle sind deshalb aus der Grammatik
  GENOMMEN und nicht nur unfertig gelassen: Der Befehl startete die
  RustDesk-Anwendung, die ohne den Dienst nach 40 s abstuerzt - ein
  Sprachbefehl, der halb funktioniert, ist schlimmer als einer, der nicht
  existiert. Wieder freigeben: zwei Zeilen in GRAMMATIK_AN und zwei in
  HILFE_SAETZE einkommentieren.
  (2026-08-19 fertig vorbereitet, nicht mehr eingebaut.) Der Weg ist belegt
  und die privilegierte Seite ist geschrieben und geprueft, es fehlt die
  Nutzerseite.

  **Was gestern herauskam:** Die RustDesk-ANWENDUNG kann keine Verbindung
  annehmen - ohne `ipc_service` stuerzt sie nach rund 40 s ab ("Got signal 11
  and exit", im Protokoll belegt). Verbindungen nimmt der **Dienst** an, und ihm
  gehoert auch das Passwort. Die entscheidende Kombination ist "Dienst laeuft UND
  sudo": `sudo rustdesk --password` wirkt dann, vier andere Kombinationen waren
  wirkungslos.

  **Schon gebaut, geprueft, NICHT installiert:**
  - `usr/local/sbin/dialos-fernwartung` (root): `starten` schaltet den Dienst
    an, setzt ein frisches achtstelliges Zufallspasswort, prueft per Gegenprobe
    im Konfigurationsfeld, dass es wirklich gesetzt ist (der Aufruf gibt auch
    bei Wirkungslosigkeit 0 zurueck), und gibt `id=` und `pw=` aus. `beenden`
    wechselt das Passwort - erst dadurch ist das vorgelesene wirklich ein
    Einmalpasswort - und stoppt den Dienst.
  - `etc/sudoers.d/dialos-fernwartung`: beide Aufrufe woertlich, ohne
    Platzhalter, `visudo -c` sagt "Analyse OK". Muss mit 0440 root:root
    installiert werden.

  **Was noch zu tun ist, in dieser Reihenfolge:**
  1. Beide Dateien von Stephan durchsehen lassen - eine sudoers-Regel ist eine
     Sicherheitsentscheidung und gehoert nicht ohne Blick installiert.
  2. `dialos-hilfe.py`: `rustdesk_pids()` durch `systemctl is-active rustdesk`
     ersetzen. Die Anwendung wird gar nicht mehr gestartet, damit faellt der
     Absturz weg.
  3. `starten()`: `sudo /usr/local/sbin/dialos-fernwartung starten` aufrufen,
     `id=`/`pw=` einlesen, an `nummern_sprechen()` uebergeben. `einmalpasswort()`
     entfaellt dann als Platzhalter.
  4. `beenden()`: `sudo ... beenden` statt SIGTERM auf Prozesse.
  5. Die Wache prueft dann den Dienst statt der Prozesse.
  6. Danach: echter Verbindungsversuch von Stephans zweitem Rechner - das ist
     zugleich der Beleg fuer die Signatur, die fuer die Leerlauf-Erkennung
     fehlt (eigener Punkt unten).

  **Loses Ende:** In `/root/.config/rustdesk/RustDesk.toml` steht seit Stephans
  Test vom 2026-08-19 ein achtstelliges Zufallspasswort, das niemand kennt. Das
  ist harmlos - der Dienst ist gestoppt und `disabled` -, und der erste Lauf von
  `dialos-fernwartung starten` ueberschreibt es.

- [ ] **Echtes Einmalpasswort fuer die Fernwartung, sobald RustDesk es zulaesst**
  (offen seit 2026-08-19). Fuenf Wege geprueft, alle zu - die Liste steht in
  `docs/sicherheit-datenschutz.md`, damit niemand sie noch einmal durchprobiert:
  Einmalpasswort steht in keiner Datei; `rustdesk --password` wirkungslos als
  Nutzer, mit laufender Anwendung, mit laufendem Dienst und als root;
  `--get-temp-password` kommt auch nach 40 s nicht zurueck; `rustdesk-utils`
  fehlt im Paket; den verschluesselten Wert selbst zu schreiben waere geraten.
  Zu beobachten ist
  [rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074). Bis dahin
  garantiert die LAUFZEIT die Begrenzung, nicht das Passwort.

- [ ] **Leerlauf-Erkennung fuer die Fernwartung** (offen seit 2026-08-19). Die
  Zeitgrenze ist absolut (eine Stunde), obwohl Leerlauf die richtige Semantik
  waere: Das Risiko ist eine offene Fernwartung, an der NIEMAND haengt. Eine
  aktive Sitzung abzuschneiden waere schaedlich, etwa mitten in einem Update.
  Warum es noch nicht gebaut ist: Auf dem Geraet hat sich nie jemand verbunden,
  die Signatur einer aktiven Verbindung ist unbekannt, und sie zu raten waere der
  schlechtere Fehler. `dialos-hilfe.py` notiert deshalb bei jeder Sitzung
  Prozessanzahl und Groesse von RustDesks Protokoll (`spur_notieren`).
  **Naechster Schritt: KEIN eigener Test noetig** (Stephan, 2026-08-20:
  "da ich an anderer Stelle Rustdesk taeglich benutze, brauchen wir da
  nicht wirklich einen Test machen"). Richtig - was fehlt, ist nicht der
  Nachweis, DASS RustDesk funktioniert, sondern die Signatur einer aktiven
  Verbindung AUF DIESEM Geraet. Die faellt beim naechsten normalen
  Support-Einsatz von selbst an: spur_notieren() schreibt bei jeder
  Sitzung Prozessanzahl und Protokollgroesse mit. Danach steht sie im
  Protokoll und die Erkennung laesst sich belegt bauen.

- [ ] **Eintraege trennen, wenn der Nutzer ohne „und" in einem Zug spricht**
  (offen seit 2026-08-19). „Milch sechs Eier Butter" in einem Atemzug bleibt ein
  Eintrag: Vosk liefert eine Aeusserung, eine Aeusserung ist ein Eintrag.
  Behandelt sind bisher die zwei einfachen Wege - eine kleine Pause (wird jetzt
  angesagt) und das Wort „und" (wird getrennt). Der zuverlaessige Weg waeren die
  **Wort-Zeitstempel**, die Vosk mit `SetWords(True)` mitliefert: eine Luecke von
  mehr als etwa 0,4 s zwischen zwei Woertern ist eine Trennstelle, auch wenn sie
  zu kurz ist, um die Aeusserung zu beenden. Zu messen ist der Schwellwert -
  0,4 s ist geraten, nicht gemessen, und zu klein gewaehlt zerlegt er „sechs
  Eier" in zwei Eintraege. Gilt nur fuer `LISTEN_ZIELE`, nicht fuer Briefe.

- [ ] **Zeitzone folgt dem Standort nicht - und ein blinder Nutzer kann sie
  nicht umstellen** (aufgefallen 2026-08-19 bei Stephans Frage „richtet sich
  die Uhrzeit nach dem tatsächlichen Ort?"). Gemessen: `Time zone:
  Europe/Vienna`, `automatic-timezone: false`. Die Zeitzone wird pro Gerät
  beim Aufsetzen gewählt (Bauanleitung Schritt 1). In Berlin oder München
  stimmt die Ansage trotzdem, weil dieselbe Zone gilt - eine Reise in eine
  andere Zeitzone ergibt eine falsche Uhrzeit.
  - **Wenn automatisch, dann mit Ansage.** Eine stille Umstellung würde für
    einen blinden Nutzer alle Zeiten unerklärlich verschieben, Termine
    eingeschlossen. Die Ansage ist der Teil, der es überhaupt zumutbar
    macht - nicht die Umstellung selbst.
  - **Für die Zeitzone reicht die ungenaue Ortung.** Die 26 km, die fürs
    Wetter unbrauchbar sind, sind hier belanglos: Eine Zeitzone braucht
    Landes-Genauigkeit. Nahe der Grenze könnte es Europe/Berlin statt
    Europe/Vienna werden - beide haben denselben Versatz, die gesprochene
    Zeit wäre identisch.

- [ ] **Wetter auf Nachfrage bräuchte einen Rückfall-Ort** (entfernt am
  2026-08-19, Begründung im Kopf von `dialos-auskunft.py`). Der Befehl kann
  am Einsatzort nicht funktionieren, weil beaconDB die WLAN-Netze dort nicht
  kennt und nur eine IP-Schätzung liefert (Wien, 26 km). Zurückholen ließe
  er sich mit einem hinterlegten Ort, der **nur** einspringt, wenn die
  Messung zu ungenau ist - in erfassten Städten gewinnt weiterhin die echte
  Messung. Stephans Einwand dazu war berechtigt und ist beantwortet: Berlin
  bliebe Berlin. Der Fall, der schiefgeht, ist Urlaub auf dem Land - dann
  wäre die Ansage veraltet, aber **hörbar** veraltet, weil sie die Stadt
  nennt.

- [ ] **Anna im Alltag beurteilen** (offen seit 2026-08-20, Stephan: "das werde
  ich aber erst mit der Zeit mitbekommen"). Zwei Dinge sind gemessen, aber nicht
  im Alltag erprobt:
  - **Tempo 0,95** - entschieden am 2026-08-22 nach Gehoer, so wie Thorstens
    0,88 seinerzeit. Stephan hat 1,00, 0,90, 0,80 und 0,95 nacheinander gehoert
    ("0,95 ist super bei Anna! Die ist beschlossen!"). Das war ein Urteil an
    wenigen Saetzen; ob es ueber einen langen Text traegt, zeigt erst der
    Alltag. Umstellen geht in einer Zeile: STIMMEN["kerstin"]["tempo"] in
    dialos-stimme.py, danach `setzen kerstin` erneut.
  - **Die Aussprache-Regeln gelten seit dem 2026-08-24 PRO STIMME** - die
    Strukturfrage aus diesem Punkt ist damit beantwortet, und zwar durch den
    ersten echten Fall: "DialOS" spricht Anna als "Dial O S", Michael bleibt
    bei "Dial OS" (Stephans Wahl nach Gehoer). Jede Regel hat ein viertes
    Feld fuer die Stimmen, fuer die sie gilt.
    **„Tas tatur" und „Ei Di" sind am 2026-09-14 bestaetigt** - beide mit
    Anna vorgespielt, im echten Satz („Akku-Stand Tastatur: achtzig Prozent."
    und „Die Fernwartung laeuft. Die ID ist: ..."), jeweils mit und ohne
    Regel. Stephans Urteil: „mit Regel". Keine Codeaenderung noetig, die
    Regeln galten schon fuer alle Stimmen - und sie brauchen damit AUCH KEIN
    Stimmen-Feld, anders als es beim Umbau am 2026-08-24 noch moeglich schien.
    Damit ist die Aussprache fuer beide Stimmen vollstaendig entschieden.


- [ ] **Zweite Stimme früh dazulegen, Auswahl erst zum Schluss**
  (Stephans Frage, 2026-08-18: „Wann wollen wir die anderen Stimmen z.B.
  einer Frau hinzunehmen?"). Aufgeteilt, weil beides verschiedene Dinge sind:
  - [ ] **Früh (rund eine Stunde):** EINE weibliche Stimme installieren
    (`de_DE-eva_k-x_low`, `kerstin-low` oder `ramona-low` - die
    Konfiguration kennt sie schon, installiert ist nur `thorsten-high`) und
    genau drei Dinge prüfen, die den Aufbau ändern könnten:
    - [x] **`stimmen[0]` in `dialos-say.py`** - erledigt 2026-08-20,
      und zwar VOR der zweiten Stimme statt danach: Der Ansagen-Speicher nahm
      die erste Datei im Ordner. Liest jetzt `DefaultVoice` aus
      `piper-generic.conf` und speichert lieber gar nichts, als bei mehreren
      Stimmen zu raten. Fünf Fälle gegengeprüft.
    - **Tempo pro Stimme?** 0,88 ist für Thorsten im Hörvergleich gewählt.
      Passt es für eine Frauenstimme nicht, muss das Tempo pro Stimme
      einstellbar werden - das ändert die Struktur von
      `piper-generic.conf`.
    - **Aussprache-Regeln prüfen:** „Tas tatur" statt „Tastatur" ist auf
      Thorsten abgestimmt. Eine andere Stimme braucht die Trennung
      vielleicht nicht.
    - **Nebenbefund:** In `piper-generic.conf` sind alle zehn deutschen
      Stimmen als `MALE1` eingetragen, auch die weiblichen. Eine Auswahl
      über den Stimmtyp funktioniert dadurch nicht.
  - [ ] **Zum Schluss:** die Auswahl für den Nutzer - per Sprache ansagbar,
    über den Neustart hinweg gemerkt. Braucht eine Einstellungs-Mechanik,
    die es noch nicht gibt, und alle Ansagen im Endzustand.
  - **Die Begründung für diese Aufteilung ist Zeile 129 selbst:** Solche
    Annahmen sammeln sich an, solange es nur eine Stimme gibt. Sie alle am
    Ende gleichzeitig zu finden ist der teure Weg.

- [ ] **Zwei Diktate haben am 2026-08-18 nichts aufgenommen - seitdem nicht
  wieder aufgetreten, Ursache nie gefunden** (das Etikett „ZUERST MORGEN" ist
  am 2026-09-14 entfernt).

  **Nachtrag vom 2026-09-14, aus den Protokollen des Admin-Kontos.** Schon am
  Tag danach nahm das Diktat auf: am 2026-08-19 dreimal „milch sechs eier
  butter" in den Einkaufszettel, einmal als drei einzelne Äußerungen, danach
  „vorlesen: 3 Einträge" und zweimal erfolgreich geleert; am 2026-08-21 zwei
  Notizen mit Text. Läufe ohne `erkannt:`-Zeile gibt es weiter, sie dauern
  aber nur 3 bis 8 Sekunden bis zum Schlusssatz - Tests des Schlusssatzes,
  kein verlorenes Diktat. **Nicht gelöst, sondern nicht mehr beobachtet.**
  Der nächste echte Beweis ist der Brief am 2026-09-15: Läuft er durch, wird
  dieser Punkt abgehakt; bleibt er leer, stehen hier die Prüffragen.

  Der ursprüngliche Befund (2026-08-18, letzter Lauf). Im Protokoll `~/.log/dialos-diktat.log` steht zwischen „grosses
  Modell geladen" und „Schlusssatz erkannt" **keine einzige** `erkannt:`-
  Zeile - beim zweiten Lauf über 26 Sekunden hinweg. Der Einkaufszettel
  blieb leer, „Einkaufszettel vorlesen" und „Einkauf erledigt" wurden
  deshalb nie ausgeführt (`~/.log/dialos-notiz.log` ist leer). **Absichtlich
  keine Vermutung notiert** - keine ist belegt. Was zu prüfen wäre: ob zwei
  gleichzeitige `parec` auf derselben Quelle sich behindern (der
  Befehlsdienst liest weiter, auch wenn er verwirft), ob der Schluss-Erkenner
  dem grossen die Blöcke wegnimmt, und ob überhaupt gesprochen wurde -
  vorher mit Stephan klären, was er gesagt hat.

- [ ] **Anwendungen: freigegebener Umfang vom 2026-08-18.** Vollständige
  Liste mit Begründung in `docs/anwendungen.md`. Gesetzt sind Firefox,
  Thunderbird (Mail/Kalender/Kontakte), RustDesk, Shortwave (Radio),
  Rhythmbox (Musik/Podcasts/Hörbücher), LibreOffice Writer (Briefe),
  Notizen als Textdateien, Jitsi im Firefox (Videochat),
  unattended-upgrades. Zu bauen, in dieser Reihenfolge sinnvoll:
  - [x] **Diktat (Sprache zu Text) - läuft seit 2026-08-18.**
    `dialos-diktat.py`, live mit Stephans Stimme belegt. Details in
    `docs/diktat.md`, Einbau in `docs/Debian-zu-DialOS.md` Schritt 11h.
    Was daran noch fehlt:
    - [ ] **Per Sprache startbar.** Bisher nur von der Kommandozeile. Der
      Befehl muss aus dem Befehlsdienst heraus das Diktat starten - und
      dabei die eigene Erkennung stilllegen, was über die Marke schon
      funktioniert.
    - [x] **Satzzeichen - gebaut am 2026-08-21.** Gesprochene Satzzeichen:
      Komma, Punkt, Fragezeichen, Ausrufezeichen, Doppelpunkt,
      Gedankenstrich, Absatz, neuer Absatz, neue Zeile. Alle neun stehen im
      Wortschatz des grossen Modells (`graph/words.txt`, 822 389 Einträge).
      Stephans Entscheidung: **immer** als Satzzeichen werten, nicht nur bei
      Sprechpause. Preis: „in diesem Punkt" wird zu „in diesem." - fällt
      beim Vorlesen auf. Ersetzt wird **wortweise**, damit „Punkte" und
      „Kommando" unangetastet bleiben. Listen bekommen keine Satzzeichen.
    - [x] **Sprechpause vor dem Schluss - gebaut und geprüft 2026-08-22.**
      In den letzten 5 s muss eine Ruhephase von mindestens 0,4 s gelegen
      haben. Offline gegen Piper geprüft, bevor Stephan testen musste
      (`scripts/dialos-schlussregel-pruefen.py`, benutzt den echten Code):
      
        - **A** durchgehende Rede: zwei **vollständige** „diktat beenden"
          entstanden, beide abgewiesen - die hätten die Zwei-Wort-Regel
          passiert.
        - **B** Rede, Pause, Schlusssatz: dieselben zwei abgewiesen, der echte
          angenommen.
      
      **Offen bleibt der Beweis am Gerät:** ein Diktat mit echter Stimme, das
      von Anfang bis Ende durchläuft. Und ein Bruchstück, das zufällig direkt
      nach einer Pause entsteht, käme weiterhin durch - klein, aber nicht null.
    - [ ] **Eine Zeile je Eintrag.** Vosk schneidet erst an einer
      Sprechpause; ohne Pause landet alles in einer Zeile. Für einen
      Einkaufszettel wäre eine Zeile je Eintrag besser.
    - [ ] **Briefe:** 98,1 % Schreibung reichen für Notizen und Mail. Für
      einen Brief an die Krankenkasse ist zu entscheiden, ob das genügt
      oder ob er vor dem Absenden geprüft werden muss.
    - [x] **Fußzeile im Brief - erledigt 2026-08-21.**
      `dialos-diktat.py` setzt den diktierten Text in einen Briefbogen aus
      reinem Text: Absender und Datum rechtsbündig, Text auf Breite 76
      umgebrochen, darunter der Hinweis auf die fehlende Unterschrift und
      unten rechts die Herkunftszeile. Den Satz holt es aus
      `dialos-fusszeile.py`, die Monatsnamen aus `dialos-start-ansage.py` -
      geholt, nicht abgeschrieben.
      
      Offen bleibt „**jeder Ausdruck**" aus Stephans ursprünglicher Vorgabe:
      siehe den Punkt „Drucken per Sprache" weiter unten. Eine Writer-Vorlage
      in `~/Vorlagen` braucht es dafür nicht mehr - der Briefbogen entsteht
      im Text selbst.
  - [x] **PDF-Archiv - Briefe und Mails erledigt 2026-08-22.**
    Jeder Brief landet beim Schreiben automatisch als PDF in
    `~/Dokumente/Archiv/DialOS-DATA/` und auf dem Stick. Eigener PDF-Erzeuger
    über `cairo`, weil der
    Briefbogen mit Leerzeichen gesetzt ist und in einer Proportionalschrift
    zerfiele; mit `pdftotext -layout` zurückgelesen und zeichengenau
    verglichen.
    
    **Mails ohne Passwort:** aus Thunderbirds lokalem mbox-Speicher, alle 15
    Minuten per Timer. Jede Mail nur einmal (Message-ID gemerkt). Der
    eigene IMAP-Weg bleibt trotzdem nötig - der lokale Speicher enthält nur,
    was Thunderbird geholt hat.
    
    **Und die Datenschutzfrage bleibt offen** (mit den Bildschirmfotos
    zusammen zu entscheiden): Verfallen die PDFs nach sieben Tagen wie die
    Protokolle? Siehe `docs/sicherheit-datenschutz.md`.
  - [ ] **Vorlesen** von Mails, Dokumenten und Webseiten.
  - [x] **Drucken per Sprache - gebaut 2026-08-22.**
    „Brief drucken", „Einkaufszettel drucken", „Notizen drucken". Alle 24
    Grammatiksätze geprüft.
    
    **Der Drucker wird gesucht, nicht vorausgesetzt.** CUPS hat auf diesem
    Gerät kein Standardziel; ein blosses `lp -` liefe ins Leere. Das Skript
    nimmt das Standardziel, sonst den einzigen Drucker, sonst den ersten -
    und schreibt ins Protokoll, welchen.
    
    **Die Fußzeile kommt nur dahin, wo sie fehlt:** Der Brief hat sie schon,
    Zettel und Notizen bekommen sie erst beim Drucken.
    
    **Auf Papier belegt am 2026-08-22** (Stephan: „Ausdruck ist jetzt
    hochkant"). Der erste Ausdruck kam quer heraus. Nachgemessen wurde,
    dass CUPS nicht schuld war - Filterweg und Drucker melden beide A4
    hochkant -, die Drehung entstand also im Gerät. Papier und
    Ausrichtung stehen jetzt im Auftrag (`-o media=A4 -o
    orientation-requested=3`) statt in irgendeiner Voreinstellung.
    
    Der Nachtest davor fiel **lautlos** durch: Vosk verstand „notiz
    drucken", die Grammatik kannte nur „notizen drucken". Kein Treffer
    heißt keine Ansage - für einen blinden Nutzer der schlechteste
    Ausgang, schlimmer als eine Fehlermeldung. Die Einzahl ist jetzt
    zweite Formulierung. Der allgemeine Fall bleibt offen: erlaubte
    Wortkombinationen, die keinen Befehl ergeben, fallen still durch.
  - [ ] **Radio und Musik per Sprache** - Shortwave nach Stationsname,
    Rhythmbox über `rhythmbox-client`. Dabei die Ein-Player-Regel
    umsetzen: das eine beenden, bevor das andere startet.
  - [ ] **Merkposition für Podcasts und Hörbücher** - Rhythmbox liefert
    sie nicht (geprüft: kein `playback-position`, kein `bookmark`). DialOS
    liest und setzt sie über MPRIS und muss sie ansagen können.
  - [ ] **Post einscannen und vorlesen** - `tesseract-ocr` (5.5.0)
    nachinstallieren, simple-scan/sane/CUPS sind da.
  - [ ] **Wecker, Timer, Erinnerungen.**
  - [ ] **Rechner ausschalten und sperren per Sprache**; **Termine und
    Wetter ansagen** (Thunderbird bzw. die vorhandene Wetterabfrage).
  - [ ] **Updates:** `unattended-upgrades` einrichten (Sicherheitsupdates
    automatisch) und getrennt davon den Sprachbefehl mit Ja/Nein-Rückfrage
    für alles Größere.
  - Noch offen, nicht bauen: **Telefonie** (nach hinten gestellt, hängt an
    der Hardware-Entscheidung), **Chat** (WhatsApp laut `telefonie.md`,
    Bestätigung fehlt), **Videoaufnahme** (Zweck ungeklärt).

- [ ] **Nächster Block: die Anwendungen** (Stephan, 2026-08-17). Bis
  hierher ging es um Grundlagen - Sprachausgabe, Erkennung, Audio-Wege,
  Desktop-Optik. Als Nächstes kommt dran, welche Programme DialOS
  mitbringt und wie sie per Sprache bedient werden. **Einstiegspunkt ist
  die Tabelle „Vorgesehen, noch nicht gebaut" in
  `docs/sprachbefehle.md`** (Radio/Musik, Hilfe rufen, Systemwartung,
  Telefonie) - keine neue Liste anlegen, sondern die bestehende abarbeiten
  und für jeden neuen Befehl die Regeln aus derselben Datei einhalten.

- [ ] **Unerklaert: Die Bluetooth-Senke stand ploetzlich auf 70 %**
  (2026-08-17). Zwischen zwei Messungen wechselte die Lautstaerke des
  AIRHUG von 100 % auf 70 %, ohne dass DialOS etwas getan hatte. Drei
  Erklaerungen sind widerlegt: Das Geraet meldet seine Lautstaerke nicht
  (geprueft bei Tastendruck ohne Ton, bei Wiedergabestart und bei
  Tastendruck **waehrend** laufender Wiedergabe - dreimal keine
  Aenderung), WirePlumbers gespeicherter Wert steht auf 100 %, und im
  Ereignisprotokoll gab es im passenden Zeitraum keinen Neuaufbau der
  Senke. **Absichtlich keine vierte Vermutung** - festgehalten, damit ein
  zweites Auftreten einen zweiten Datenpunkt liefert. Wichtig ist es,
  weil eine Lautstaerke, die sich von selbst aendert, fuer einen blinden
  Nutzer nicht nachvollziehbar ist.

- [ ] **Entscheidung offen: Ansagen leiser als Musik** (Stephans Wunsch
  vom 2026-08-17, "um ca. 30 % drosseln"). Am Laptop-Lautsprecher ist es
  machbar - Daempfung im Signal wirkt dort, von Stephan im Hoervergleich
  bestaetigt. Am AIRHUG **nicht**: Er rechnet die Daempfung wieder weg
  (Messung in `docs/Debian-zu-DialOS.md`, Schritt 11g), dort wirkt nur die
  Geraete-Lautstaerke, und die gilt fuer alles. Moeglich waere, sie per
  AVRCP **waehrend** der Ansage kurz abzusenken; ein solcher Befehl kostet
  gemessen nur 19-36 ms, faellt gegen 1200 ms Ansage also nicht auf.
  Offen ist, ob das Absenken am Geraet hoerbar stuft oder klickt - das
  entscheidet, ob es brauchbar ist. Nach Stephans Einstellung der
  Lautstaerke am Geraet ist die Frage vielleicht ohnehin erledigt.
  - **Dabei zu beheben:** `GenericVolume` ist in DialOS wirkungslos, weil
    die sox-Kette auf `norm` endet und jede Daempfung davor wegrechnet.
    Wer die Lautstaerke ueber speech-dispatcher regeln will, muss
    `norm vol <faktor>` schreiben.

- [ ] **Fahrplan bis zur echten Sprachsteuerung** (festgelegt mit Stephan
  am 2026-08-16, in dieser Reihenfolge):
  1. Referenz-Mikrofon festlegen - **erledigt**, AIRHUG 01.
  2. **Windows-11-Umschaltung für den Desktop** - **gebaut am 2026-08-16**,
     Live-Test steht noch aus (siehe nächster Punkt).
  3. Aufweckwort + dauerhafte Zuhör-Schleife - **teilweise erledigt am
     2026-08-16**: Die Zuhör-Schleife läuft
     (`dialos-sprachbefehl-desktop.py`), ein Aufweckwort gibt es noch
     nicht. Es fehlt bisher auch nicht, weil die eingeschränkte
     Grammatik nur drei feste Sätze zulässt.
  4. hassil-Befehlsgrammatik - **die Desktop-Umschaltung als erster
     echter Sprachbefehl ist am 2026-08-16 erledigt**, allerdings direkt
     über eine Vosk-Grammatik statt über hassil. hassil lohnt sich erst,
     wenn es mehrere Befehle mit Varianten gibt.

- [ ] **Bluetooth-Profil gegen Hängenbleiben absichern** (offen seit
  2026-08-17). Nach dem Neustart stand der AIRHUG auf `headset-head-unit`
  statt `a2dp-sink` - die Wiedergabe lief dauerhaft in Telefonqualität,
  ohne dass es jemand bemerkt hätte, der das Gerät nicht kennt.
  `dialos-start-ansage.py` schaltet für die Lautstärke-Frage bewusst auf
  HFP und danach zurück; endet das Skript vorher (Abbruch, Abmelden,
  Zeitüberschreitung), bleibt das Profil hängen. Nötig ist ein Riegel,
  der unabhängig vom Skriptende greift - etwa eine Prüfung beim Anmelden
  oder ein `trap` auf das Skriptende.

- [ ] **Aufweckwort mit openWakeWord bauen** (entschieden 2026-08-17).
  Die Vosk-Grammatik scheidet aus - sie presst jede Äußerung in die
  nächstliegende Phrase, weshalb "ich rufe michael an" als `hallo
  michael` durchkam, und zwar mit voller Sicherheit (conf 1.00). Ein
  Schwellwert trennt also nicht. Weckphrase soll der Name des
  Assistenten sein ("Hallo Michael", bei weiblicher Stimme "Hallo
  Anna"), gelesen aus derselben Einstellung wie die Stimmenwahl. Details
  in `docs/sprachsteuerung.md`.

- [ ] **Vorführvideo mit Sprachein- und -ausgabe aufnehmen** (Stephans
  Idee vom 2026-08-16, für den nächsten Arbeitstag). Zeigen soll es, was
  DialOS heute wirklich kann: Start-Ansage mit Lautstärke-Frage, dann
  "auf Windows umschalten" / "auf Linux umschalten" per Zuruf. Zu klären
  ist dabei die Tonaufnahme - der Bildschirminhalt allein genügt nicht,
  es müssen sowohl die Sprachausgabe des Systems als auch die gesprochene
  Eingabe hörbar sein. Denkbar wäre `wf-recorder` oder OBS mit zwei
  Tonspuren (Systemklang + Mikrofon); beides ist noch nicht installiert.
  **Achtung bei der Mikrofonwahl:** Der Sprachbefehl-Dienst hört über das
  eingebaute Mikrofon, damit das AIRHUG in A2DP bleibt - eine Aufnahme
  über das Headset-Mikrofon würde die Wiedergabe auf Telefonqualität
  ziehen und das Video schlechter klingen lassen, als das System ist.

- [x] **Referenz-Audiogerät entschieden (Stephan, 2026-08-17): zwei
  Geräte.** AIRHUG bleibt als Lautsprecher in A2DP, dazu ein
  Funkmikrofon mit **USB**-Empfänger für die Eingabe - bewusst kein
  zweites Bluetooth-Gerät, das brächte die HFP-Falle zurück. Anforderungen
  und Kandidaten in `docs/hardware.md`.

- [ ] **Preiswertes Bluetooth-Mikrofon zum Ausprobieren beschaffen**
  (Stephan, 2026-08-17 - der Test entscheidet über die Bauart). Bluetooth
  hat einen Vorteil, den USB nicht hat: **DialOS sieht den Akkustand**
  über BlueZ und kann warnen, bevor das Mikrofon leer ist. Dagegen steht
  ein Risiko, das sich nur am Gerät klären lässt: Ein dauerhaft offenes
  HFP belegt fortlaufend Funkzeit auf demselben Adapter, über den der
  AIRHUG spielt - A2DP kann dabei stottern.

  **Prüfplan:** koppeln, Radio über den AIRHUG laufen lassen, den
  Sprachdienst auf das Bluetooth-Mikrofon legen, und hinhören ob die
  Musik stottert. Zusätzlich: Reichweite durch die Wohnung, Akkustand
  erscheint in der Start-Ansage, Erkennungsqualität gegen das eingebaute
  Mikrofon, und ob die Echo-Unterdrückung noch reicht, wenn das Mikrofon
  **neben** dem Lautsprecher liegt statt weit weg.

  Fällt der Test schlecht aus, ist die Rückfallebene ein USB-Funkmikrofon
  (Kandidaten in `docs/hardware.md`) - dann aber ohne Akkuanzeige, und
  vor dem Kauf zu klären, ob der Sender dauerhaft am Netzteil laufen
  kann.

- [ ] **Erkennen, wenn das Mikrofon nichts mehr liefert** (2026-08-17,
  unabhängig von der Gerätewahl zu bauen). Der Sprachdienst misst ohnehin
  laufend den Pegel. Kommt über Minuten hinweg **gar nichts** an, obwohl
  die Quelle da ist, soll er es ansagen: „Ich höre nichts mehr vom
  Mikrofon." Das ersetzt keine Akkuanzeige, fängt aber genau den Ausfall
  ab, der den Nutzer sonst ratlos zurückließe - er redet sonst gegen ein
  totes Gerät, ohne es zu merken. Achtung beim Schwellwert: Stille im
  Raum ist normal, dauerhaft **exakt** null Pegel dagegen nicht.
  - **Am 2026-08-17 ist die Aufgabe größer geworden, als sie gedacht war
    - der Fall ist eingetreten und hat die komplette Tonausgabe
    mitgenommen.** Die Echo-Unterdrückung stand zum Testen auf dem
    USB-Headset; beim Neustart war dessen Funkverbindung nicht da. Der
    Dongle bietet trotzdem eine Soundkarte an, ALSA meldet sogar
    `state: RUNNING` - es kommen nur 0 Bytes. Weil das Modul diese
    Aufnahme als Taktgeber braucht, startete PipeWire den Graph nicht
    mehr, und **nichts** im System konnte Ton abspielen, auch nicht über
    die eingebauten Lautsprecher. Details in `docs/Debian-zu-DialOS.md`,
    Schritt 11f.
  - **Damit hängen zwei Dinge daran, nicht eines.** (1) Die Ansage, wenn
    das Mikrofon verstummt - wie oben. (2) Eine Absicherung, die die
    Echo-Unterdrückung fallen lässt, statt den Ton mitzunehmen. Solange
    das Ziel das eingebaute Mikrofon ist, kann der Fall nicht auftreten;
    sobald ein externes Funkmikrofon Standard werden soll - und das ist
    geplant -, ist (2) Voraussetzung dafür, nicht Zubehör.
  - **Zu prüfen dabei:** Ob PipeWire selbst einen Weg anbietet, eine
    stumme Quelle nicht zum Taktgeber zu machen, wäre der saubere Weg.
    Sonst muss ein Dienst das Ziel vor dem Laden prüfen (`parec` auf
    Bytes testen) und die Unterdrückung nur dann einhängen.
  - **Und der Befund, der die Aufgabe schwer macht: es gibt keinen
    verlässlichen Anzeiger.** Nach Abziehen und Wiedereinstecken des
    Dongles lieferte dasselbe Gerät 64000 Bytes statt 0. Stephan hat
    dabei ausdrücklich festgestellt, dass ihm das Headset **schon vor dem
    Neustecken** eine bestehende Verbindung gemeldet hatte, auch über den
    Dongle. Also: Headset meldet verbunden, Dongle bietet eine Soundkarte
    an, ALSA meldet `state: RUNNING` - und es kommen trotzdem 0 Bytes.
    Meine erste Deutung („die Funkverbindung stand nicht") war damit
    falsch. **Folge für die Absicherung:** Sie darf sich auf keine
    Zustandsmeldung stützen, weder auf die des Geräts noch auf die von
    ALSA. Nur die tatsächlich ankommenden Bytes zählen.

- [x] **So stand die Aufgabe vorher da (zur Herkunft):** Gemessen ist:
  Das Gerät kann nicht gleichzeitig gut klingen und zuhören (A2DP hat
  `sources: 0`), seine Tasten erreichen den Laptop auf **keinem** Kanal -
  weder als Tastencode noch als AVRCP-Lautstärke -, und seine Lautstärke
  ist von GNOME entkoppelt. Damit fällt der Ausweg aus, per Tastendruck
  kurz auf HFP zu schalten. Drei Möglichkeiten, siehe
  `docs/hardware.md`: zwei Geräte (Mikrofon dauerhaft in HFP beim
  Nutzer, Lautsprecher in A2DP), ein anderer Lautsprecher dessen Tasten
  durchkommen, oder die Auflage dass der Laptop im selben Raum steht.

- [x] **Geklärt am 2026-08-17: Die Lautstärke-Entkopplung gilt nur in
  eine Richtung.** Der Rechner kann den AIRHUG sehr wohl regeln (10 %
  gegen 100 % im Hörvergleich eindeutig); nur seine eigenen Tasten melden
  sich nicht zurück. Meine erste Einschätzung („DialOS kann überhaupt
  nicht regeln") war zu weit gegriffen. Kein Ausschlusskriterium.

- [ ] **Restrisiko dazu:** DialOS kennt die am Gerät eingestellte
  Lautstärke nicht. Hat jemand den AIRHUG am Rad heruntergedreht, hilft
  „mach lauter" nur, solange die Software-Lautstärke noch Spielraum hat -
  bei 100 % bleibt es leise, und die Ursache liegt außerhalb des Systems.
  Zu überlegen: Erkennt DialOS diesen Fall (Software auf 100 %, Nutzer
  sagt weiter „lauter") und sagt dann, dass am Gerät selbst gedreht
  werden muss?

- [ ] **Mikrofon-Vergleich vom 2026-08-13 wiederholen.** Damals galt das
  eingebaute Mikrofon als dem AIRHUG deutlich unterlegen. Am 2026-08-16
  stellte sich heraus, dass ab Werk 60 dB Verstärkung anlagen und das
  Signal dauerhaft übersteuert war - vermutlich hat der Test also nicht
  das Mikrofon gemessen, sondern die Übersteuerung. Solange das nicht
  wiederholt ist, steht die Begründung für die Bluetooth-Priorität auf
  wackligem Grund.

- [ ] **Optische Abnahme der Windows-Optik nach dem Anmelden** (offen seit
  2026-08-16). Die Einstellungen stimmen nachweislich, gesehen hat sie
  aber noch niemand: Die Erweiterungen greifen erst nach einmaligem
  Ab- und Anmelden. Zu prüfen: Taskleiste unten mit mittigen Symbolen,
  ArcMenu-Startmenü links im Windows-11-Layout, Fensterknöpfe rechts,
  Fenster-Andocken am Bildschirmrand. Danach `dialos-desktop-stil.sh
  gnome` und kontrollieren, dass wirklich alles wieder wie vorher
  aussieht. Anschließend dasselbe als `nutzer`.

  **Stand 2026-09-14 - als `dialosadmin` weitgehend abgenommen.** Stephan hat
  umgeschaltet und Bildschirmfotos geschickt:
  - ☑️ Taskleiste unten, Symbole mittig, Startknopf links.
  - ☑️ Startmenü - nach zwei Runden Aufräumen: Angeheftet waren ArcMenus
    Voreinstellungen, darunter ein leerer Platz (`firefox.desktop` gibt es
    unter Debian nicht) und ein überlaufendes Raster. Jetzt sechs
    Alltagsprogramme als große Symbole, drei pro Zeile, „Häufig" aus, Liste
    ohne Buchstaben. Beschriftungen stehen linksbündig unter mittigen
    Symbolen - in ArcMenu nicht einstellbar, Stephan: „So lassen".
  - ☑️ Fensterknöpfe rechts (Minimieren, Maximieren, Schließen) - im Foto am
    Claude-Fenster zu sehen.
  - ☑️ Zurück auf GNOME: Stephan „sieht wieder aus wie vorher"; nachgelesen,
    dass alle von DialOS gesetzten Schlüssel wieder auf Standard stehen und
    die drei Erweiterungen aus sind.
  - ☑️ Fenster-Andocken am Bildschirmrand: Stephan „andocken funktioniert
    auch" - geprüft in der Windows-Optik (tiling-assistant aktiv, GNOMEs
    eigenes Andocken `edge-tiling` dabei aus, es war also wirklich die
    Erweiterung).
  - ☐ **Offen:** die ganze Runde als `nutzer`.

- [ ] **Mikrofon-Fallback ohne Bluetooth testen** (offen seit
  2026-08-16). Die Ausgabeseite ist bewiesen - Headset aus, Ton kam aus
  dem eingebauten Lautsprecher. Die Eingabeseite fehlt noch: versteht das
  eingebaute Laptop-Mikrofon die Lautstärke-Frage?

  **Wichtig, sonst schlägt der Test scheinbar fehl:** Die Frage kommt seit
  2026-08-16 nur noch einmalig. Vorher den gemerkten Wert löschen, sonst
  wird gar nicht gefragt:

  ```bash
  sudo rm /home/nutzer/.config/dialos/lautstaerke
  ```

  Dann AIRHUG **ausschalten**, als `nutzer` ab- und wieder anmelden, und
  ins Laptop-Mikrofon antworten.

  **Erwartung:** deutlich schlechter als über das Headset - der
  Vergleichstest vom 2026-08-13 war eindeutig (6 von 8 Testsätzen über
  Bluetooth korrekt, spürbar weniger beim eingebauten Mikrofon). Für den
  Fallback reicht es, wenn es *überhaupt* trägt: Er soll nur verhindern,
  dass ein Nutzer ohne Headset gar nichts mehr ausrichten kann. Wird gar
  nichts verstanden, greift der 100-%-Rückfall - die Ansage bleibt also
  hörbar, aber der Nutzer könnte die Lautstärke nicht mehr selbst ändern.

- [ ] **Deutsche Firmware-Ansagen des Lautsprechers prüfen** (offen seit
  2026-08-16, Stephans Anforderung a). Gemeint sind die Ansagen des
  Geräts selbst („verbunden", Akku-Warnung), nicht die von DialOS. Sie
  sind für einen blinden Nutzer die **einzige** Rückmeldung, die er vom
  Gerät unabhängig vom Laptop bekommt - eine unverstandene Akkuwarnung
  heißt, dass die Ausgabe unangekündigt ausfällt. Über die
  Bluetooth-Standardprofile lässt sich das nicht fernsteuern, es hängt
  rein am Gerät. Beim AIRHUG noch nicht geprüft.

  *(Die frühere Fassung dieses Punkts nannte den AIRHUG als alleiniges
  Referenzgerät. Das ist seit 2026-08-17 überholt: Es sind zwei Geräte,
  siehe oben und `docs/hardware.md`.)*

- [x] **ERLEDIGT am 2026-08-16 - der komplette Ablauf ist auf echter
  Hardware durchgelaufen.** Ergebnis: Aus einem frisch installierten
  Debian 13 wurde ein laufendes DialOS. Bewiesen sind: verschlüsselter
  Swap (kommt beim Boot von allein hoch, per Journal belegt),
  `dialos-nutzer-home` mit 374,9 GiB, Autologin für `nutzer`,
  Sprachausgabe hörbar, deutsche Tastatur, und **beide Richtungen des
  Stick-Gates**: ohne Stick Anmeldebildschirm mit Passwortzwang und
  geschlossenem LUKS-Container, mit Stick sauberer Autologin samt
  Ansagen. Ebenfalls live bestätigt: die neue Lautstärke-Logik - Ansage,
  danach die Frage, gesprochene "25" erkannt und dauerhaft gemerkt.
  Dabei kamen acht Fehler ans Licht, die kein Trockenlauf gefunden hätte
  (Details im README-Änderungsprotokoll 0.5.0). Ursprünglicher Eintrag:
  T490 komplett neu aufsetzen und dabei den
  kompletten neuen Ablauf real testen (noch nie end-to-end
  durchgelaufen): Debian 13 + GNOME manuell installieren (Schritt 1,
  **mit** dem seit 2026-08-14 dokumentierten Partitionierungs-Hinweis -
  100 GB root, Rest der Platte bewusst frei lassen) →
  `scripts/dialos-full-office-setup.sh` (Schritte 2-12 + 15
  automatisiert) → neues `dialos-setup-home-partition.sh`
  (`dialos-nutzer-home`-Partition + Sicherheits-Stick auf dem
  freigelassenen Platz einrichten, ersetzt für diesen Ablauf
  `dialos-install`s Ganze-System-Kopie) →
  `scripts/dialos-buero-setup-abschliessen.sh` (`nutzer` anlegen).
  Danach wie von Stephan geplant: darauf aufbauend Spracherkennung/
  Sprachbefehle Schritt für Schritt auf echter Hardware ausarbeiten und
  die Installationsroutine weiter erweitern.
  **Vorarbeit erledigt 2026-08-16:** Beide Skripte wurden vor dem ersten
  Lauf gegen `docs/Debian-zu-DialOS.md` durchgesehen, auf dem frisch
  installierten T490 live gegengeprüft und die gefundenen Fehler behoben
  (Details im README-Änderungsprotokoll 0.5.0). Der Ablauf besteht jetzt
  aus genau drei Befehlen; die Handarbeit aus Doku-Schritt 13 steckt in
  `dialos-buero-setup-abschliessen.sh`.

- [ ] **Zurückgestellt (Stephan, 2026-08-16):** **`dialos-claude-setup.sh`
  auf dem frisch installierten T490
  ausführen.** Geprüft am 2026-08-16: `credential.helper` ist nicht
  gesetzt, `~/.git-credentials` fehlt, `/etc/sudoers.d/` enthält nur die
  README, und `~/DialOS` zeigt nicht auf das Repo der externen Platte.
  Das Skript lief auf diesem System also noch nie - `git push` würde
  nach Zugangsdaten fragen und die `eggs produce`-NOPASSWD-Regel fehlt.
  Muss Stephan selbst machen (das GitHub-Token tippt kein Skript ein).

- [ ] **Zurückgestellt, nicht mehr nächster Schritt** (siehe die zwei
  neuen Punkte unten): Echten Live-Boot-Test mit
  `DialOS-Live-0.5.0-clone.iso` erneut durchführen: erster Versuch am
  2026-08-14 ist bei `dialos-install` gescheitert, zwei Bugs im Skript
  gefunden und behoben (siehe
  Commit-Historie): 1) Sicherheits-Stick wurde vor der `cryptsetup
  open`-Nutzung der Schlüsseldatei ausgehängt, 2) Datei-Speichern-Dialog
  für das Schlüssel-Backup blieb unter `pkexec` lautlos aus (fehlende
  `DBUS_SESSION_BUS_ADDRESS`/`XDG_RUNTIME_DIR` für den
  xdg-desktop-portal-Zugriff). **Wichtig vor dem nächsten Versuch:** Die
  gepatchte `dialos-install` liegt bisher nur im Git-Repo - sie muss
  zusätzlich auf das aktuell laufende System kopiert werden UND eine neue
  ISO mit `eggs produce` gebaut werden, sonst testet der nächste
  Live-Boot wieder die alte, fehlerhafte Version (siehe "Root Cause
  des 'nichts hat sich verändert'-Tests", 2026-08-11, in der
  Commit-Historie). Danach wie ursprünglich geplant: vor `dialos-install`
  per `gdbus` prüfen, ob `dialosadmin`/`nutzer` mit korrektem
  Autologin-Status mitgekommen sind (siehe docs/sicherheit-
  datenschutz.md, Abschnitt "Automatische Anmeldung"); `dialos-install`
  mit dem Sicherheits-Stick komplett durchspielen - externe
  SanDisk-Extreme-Platte vorher abstecken (sonst als Zielfestplatte
  wählbar!); neue Stick-Partitionierung (`DIALOS-KEY` 2 GiB +
  `DIALOS-DATA` ext4) verifizieren.

- [x] **Hinfällig seit 2026-08-16:** `dialos-install` ist ersatzlos
  entfallen (Weg A). Die Prüfpunkte dieses Eintrags wurden stattdessen
  über den neuen Ablauf abgedeckt und sind alle bestanden - siehe den
  erledigten Eintrag oben. Ursprünglich: komplette
  `dialos-install`-Installation
  mit dem neuen Home-Partition-Design auf echter Hardware (T490)
  durchspielen (siehe docs/sicherheit-datenschutz.md, Abschnitt
  "Verschlüsselung von nutzers Daten + Sicherheits-Stick", für das
  vollständige Design). Prüfpunkte: root-Partition ~100 GiB
  unverschlüsselt bootet normal; `dialos-nutzer-home` (LUKS2) wird beim
  Büro-Setup korrekt angelegt; `dialos-setup-nutzer.sh` bricht ohne
  gestecktem Stick kontrolliert ab statt `nutzer`s Home auf root
  anzulegen; nach Abschluss: Stick abziehen + neu starten → normaler
  GDM-Login-Screen, `/home/nutzer` leer/nicht gemountet; Stick wieder
  einstecken + neu starten → `/home/nutzer` gemountet, Autologin greift.
  Zusätzlich `DIALOS-KEY` (jetzt ext4, nicht mehr FAT32) und
  `DIALOS-DATA` (jetzt exFAT, nicht mehr ext4) auf einem 64-GB-Stick
  verifizieren. **Teilweise bereits erledigt (2026-08-14):** Die reine
  Stick-Partitionierung wurde manuell (nicht über `dialos-install`
  selbst, sondern per Hand mit denselben Befehlen) gegen einen echten
  59,8-GB-USB-Stick getestet - `DIALOS-KEY` (ext4, root:root 755, für
  normale Nutzer weder less- noch schreibbar - stärkerer Schutz als
  geplant) und `DIALOS-DATA` (exFAT, für den aktuellen Nutzer beschreib-
  bar) wurden korrekt angelegt. **Noch offen:** `DIALOS-DATA` an einem
  echten Windows-Rechner einbinden und beschreiben testen (nur
  Linux-seitig verifiziert bisher).

- [x] Grundsatzentscheidung getroffen (siehe oben, umgesetzt
  2026-08-14): Ganze-Platte-LUKS-Verschlüsselung ist komplett entfallen,
  ersetzt durch eine reine `dialos-nutzer-home`-Partition + das
  `dialos-stick-gate`-Gate. `dialos-install`/`dialos-rekey`/
  `dialos-stick-gate.sh` entsprechend umgeschrieben, tote
  `dialos-keyscript`-initramfs-Dateien entfernt.

- [ ] Sprechgeschwindigkeit der Piper-Stimme sollte vom Nutzer individuell
  einstellbar sein (aktuell fest über `GenericRateMultiply` in der
  Piper-Config verdrahtet, `0.85` als Stephans persönliche Präferenz
  gewählt) - braucht eine echte Einstellmöglichkeit (z. B. GNOME-
  Barrierefreiheitseinstellungen oder eigener Sprachbefehl), nicht nur
  einen Config-Wert.

- [ ] Bluetooth-Audio-Fix in `dialos-start-ansage.py`
  (Ein-Instanz-Lock/`alte_instanz_beenden()`) ist noch nicht über einen
  längeren Zeitraum endgültig bestätigt - `/tmp/dialos-bluetooth-debug.log`
  bei einem erneuten Auftreten des Problems prüfen.

- [ ] **Eigener Server für dialos.org, Nextcloud, Forum, RustDesk-Relay
  und Videokonferenzen** - Sponsoring bisher ohne Erfolg.

  **Stand.** Hetzner angefragt am 2026-08-17, Rückfrage nach der konkreten
  Infrastruktur am 2026-08-18, konkretisiert nachgefasst am 2026-08-25
  (AX42, 24 Monate, mit angebotener Gegenleistung), Abschlussmail am
  2026-09-05. webgo angefragt, landete im Support-Ticketsystem (#48345),
  am 2026-08-25 mit Bitte um Weiterleitung an Vertrieb/Geschäftsleitung
  geantwortet. Beide bis 2026-09-05 ohne inhaltliche Antwort.

  **Was es tatsächlich kostet.** Der Bedarf ist kleiner als angefragt:
  netcup RS 4000 G12 (12 vCore, 32 GB, 1 TB NVMe) für rund 34 EUR netto
  im Monat deckt Website, Nextcloud, Forum und RustDesk-Relay ab. Erst
  regelmäßige Gruppen-Videokonferenzen bräuchten mehr. Vollständiger
  Anbietervergleich mit Preisen und Links liegt als
  `DialOS-Server-Anbietervergleich.docx` auf Stephans Schreibtisch -
  bewusst nicht im Repo, weil er den Verlauf der Anfragen enthält.

  **Ein verbreitetes „Gratis-Server für Open Source"-Programm gibt es bei
  den deutschen Anbietern nicht** - server.camp und Hostsharing eG sind
  reguläre kostenpflichtige Angebote mit Open-Source-Schwerpunkt, kein
  Sponsoring. Hetzners Ansatz („auf individueller Basis") ist bereits das
  übliche Modell. Weitere Anbieter reihum anzuschreiben verlängert nur
  das Muster.

  **Standort Österreich braucht keinen Anbieterwechsel:** netcup betreibt
  selbst ein Rechenzentrum in Wien, der Standort ist bei der Bestellung
  wählbar. Zum Vergleich, was ein rein österreichischer Anbieter kostet -
  WUKOTEC (Wien) hat mit dem PS 4000 G12 exakt dieselbe Ausstattung und
  dieselbe Namenslogik wie netcups RS 4000 G12, aber für 57,56 statt
  39,92 EUR brutto, also rund 44 % Aufschlag.

  **Am 2026-09-09 verschickt:** Angebotsanfrage an web-crossing GmbH
  (Innsbruck, Rechenzentrum DC3, info@web-crossing.com, Tel. +43 512
  206567, Geschäftsführer Ing. Martin Ennemoser und Stefan Ennemoser) mit
  konkreter Zielausstattung - bewusst als normale Kundenanfrage, nicht
  als Sponsoring-Bitte, der Partnerschaftsgedanke steht nur im
  Schlussabsatz. Dazu eine Anfrage an netcup, ob es Konditionen für
  Open-Source-Projekte gibt (netcup veröffentlicht keine allgemeine
  Kontaktadresse, Weg ist das Kontaktformular bzw. ein Ticket im
  Kundenkonto). Rückmeldungen abwarten; kommt nichts, regulär buchen.

- [ ] **Warteliste Förderprogramme** - deutlich größerer Hebel als
  Server-Sponsoring, weil das Nadelöhr bei DialOS nicht der Server ist
  (rund 34 EUR im Monat), sondern Hardware, Zeit und später
  Zertifizierung. Recherchestand 2026-09-09.

  **Die Rechtsform entscheidet über alles andere.** Als Privatperson ist
  fast nichts zugänglich - die einzige Ausnahme ist netidee. Ein
  gemeinnütziger Verein öffnet Licht ins Dunkel und vergleichbare Töpfe,
  eine Unternehmensgründung öffnet die FFG. Das ist die eigentliche
  Weiche und eine Entscheidung mit Folgen weit über Förderungen hinaus.

  **netidee (Internet Stiftung Austria)** - bis 60.000 EUR, strikt Open
  Source, **Privatpersonen mit österreichischem Wohnsitz ausdrücklich
  zugelassen**. Barrierefreiheits-Projekte wurden dort bereits gefördert
  (u. a. barrierefreie Jobsuche für Menschen mit Behinderung). Frist für
  Call 2026 war der 2026-07-07 und ist verpasst; nächster Call
  voraussichtlich Sommer 2027. Zeitlich passt das sogar gut, weil DialOS
  dann deutlich reifer ist als heute. Inhaltlich die beste Passung.

  **FFG Impact Innovation Social** - der größte Einzelposten: 70 % der
  anerkennbaren Kosten, max. 105.000 EUR als De-minimis-Beihilfe,
  ausdrücklich für soziale Innovation. Projektgröße max. 150.000 EUR
  Gesamtkosten. Auch ein „Unternehmen in Gründung" darf einreichen, eine
  bestehende Firma ist also nicht zwingend - eine Gründungsabsicht schon.
  Call 2026 seit 2026-03-12 geschlossen, Budget ausgeschöpft; die Angaben
  zur laufenden Einreichung sind widersprüchlich. **Direkt bei der FFG
  erfragen**, nicht auf Zweitquellen verlassen.

  **Licht ins Dunkel** - nur für gemeinnützige Vereine (ZVR-eingetragen,
  Sitz in Österreich), gemeinnützige GmbHs, Stiftungen oder
  Religionsgemeinschaften. Als Privatperson nicht zugänglich. Zielgruppe
  sind ausdrücklich Menschen mit körperlichen, kognitiven, psychischen
  oder Sinnesbehinderungen - trifft auf DialOS genau zu. Einreichung
  laufend zwischen 1. April und 31. Dezember. Nur Kofinanzierung zu
  gesicherten Gesamtkosten, nie Vollfinanzierung.

  **NLnet - geprüft am 2026-09-09, passt NICHT.** Frühere Notiz mit der
  Frist 2026-11-03 ist damit erledigt. Die aktuell offenen Fonds sind
  Restack (offene Internet-Infrastruktur, Standards, sichere Geräte), der
  Open Social Fund (dezentrale soziale Netzwerke über ActivityPub) und
  ein Fonds für Wissenschaftsnetze. Barrierefreiheit oder assistive
  Technik ist in keinem davon Schwerpunkt; die früheren NGI-Zero-Fonds,
  die so etwas gefördert haben, sind offenbar ausgelaufen. Ein Antrag
  wäre ein Langschuss und lohnt den Aufwand nicht.

- [ ] **Prüfen, ob DialOS als anerkanntes Hilfsmittel eingestuft werden
  kann** - Nebenfund der Förderrecherche vom 2026-09-09 und womöglich
  wichtiger als jede Projektförderung.

  Das Sozialministeriumservice fördert keine Entwickler, wohl aber
  Betroffene: Es gibt Zuschüsse für Hilfsmittel, ausdrücklich auch für
  **Kommunikationshilfen**, sowie für Arbeitsplatzausstattung, wenn sie
  zum Erhalt oder zur Erlangung eines Arbeitsplatzes nötig ist. Spätere
  Kunden könnten einen DialOS-Laptop also bezuschusst bekommen. Für das
  Geschäftsmodell ist das potenziell mehr wert als eine einmalige
  Projektförderung, weil es die Kaufhürde genau bei der Zielgruppe senkt,
  die sich ein Gerät sonst nicht leisten kann.

## Erledigt (zur Nachvollziehbarkeit)

Nach Thema gruppiert, innerhalb des Themas chronologisch. Das Datum ist
der Tag, an dem der Punkt fertig wurde. Nichts hiervon wird gelöscht -
die Liste ist die Erinnerung des Projekts, nicht nur eine Erfolgsbilanz.

### Sprachsteuerung und Erkennung

- ☑️ **2026-08-14** — Vosk (0.3.45) + hassil (3.11.0) + deutsche Vosk-Modelle (groß/klein)
  als wiederholbares Rezept dokumentiert - erledigt 2026-08-14 (siehe
  docs/Debian-zu-DialOS.md, Schritt 15). Dabei bestätigt: Die
  ursprüngliche Live-Installation war zwischenzeitlich tatsächlich
  wieder verschwunden (`import vosk` schlug beim Nachprüfen fehl) - ein
  zwischenzeitlicher Reinstall des T490 hatte sie gelöscht, genau die
  hier befürchtete Falle. `dialos-vosk-test.py` jetzt im Repo unter
  `iso-build/config/includes.chroot/usr/local/bin/`. Außerdem gefunden:
  Die Modell-Ordner auf dem T490 (`/usr/local/share/vosk-model-de-big`
  und `-small`) enthalten wegen eines Entpack-Fehlers beim ursprünglichen
  Testlauf doppelt verschachtelte Kopien der Modelldateien (unnötiger
  Festplattenplatz, gemessen ca. 6,3 GB statt ~3,2 GB beim großen
  Modell) - die
  neue Doku vermeidet den Fehler, die vorhandenen doppelten Daten auf
  dem T490 selbst sind aber noch nicht aufgeräumt.

- ☑️ **2026-08-14** — `pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0`
  auf dem T490 ausgeführt und verifiziert (2026-08-14) - `import vosk`/
  `hassil` funktioniert, `vosk.Model()` lädt das kleine deutsche Modell
  erfolgreich.

- ☑️ **2026-08-16** — **Sprachbefehl live getestet und läuft (2026-08-16, von Stephan
  bestätigt).** Dabei kam heraus, dass das eingebaute Mikrofon um 60 dB
  übersteuert war - der Dienst konnte prinzipiell nichts erkennen.
  Behoben und dauerhaft abgesichert (`dialos-mikrofon-pegel.service`).

- ☑️ **2026-08-17** — **Schalter „Sprachsteuerung starten/stoppen" gebaut
  (2026-08-17).** Zwei Zustände mit eigener Grammatik, Ansage bei jedem
  Wechsel, Abschaltung nach zwei Minuten. Die offene Zustandsfrage ist
  damit beantwortet: Der Nutzer hört jeden Wechsel. Live-Test mit echter
  Stimme steht noch aus.

  **So stand die Aufgabe vorher da (zur Herkunft):** Bis zum „starten" hört DialOS nur auf
  diesen einen Satz, danach nimmt es Befehle an, bis „stoppen" kommt.
  Gemessen ist bereits, dass die Erkennung trägt und drei Störsätze ruhig
  bleiben - offen ist der Zustand selbst: Wo wird er gemerkt (Datei wie
  bei der Desktop-Optik?), was passiert beim Anmelden (an oder aus?), und
  **wie erfährt ein blinder Nutzer, in welchem Zustand er ist**? Ohne
  eine Antwort darauf ist der Schalter gefährlicher als kein Schalter:
  Wer nicht weiß, dass die Erkennung aus ist, hält das Gerät für kaputt.
- ☑️ **2026-09-14** — **Erledigt durch den Betrieb: End-to-End-Test von
  `dialos-vosk-test.py`.** Der Punkt stammte aus der Zeit, als nur Installation
  und Laden der Modelle geprüft waren. Seitdem erkennt Vosk täglich echte
  Stimme: 26 Grammatiksätze im Befehlsdienst, gemessene Beinahe-Treffer,
  Diktate in Einkaufszettel und Notizen, die Messreihe in `docs/diktat.md`.
  Ein eigener Test mit dem alten Skript würde nichts mehr zeigen, was der
  Betrieb nicht schon belegt.

### Sprachausgabe und Ansagen

- ☑️ **2026-08-14** — Lautstärke-Abfrage bei der Start-Ansage (nur `nutzer`, 100/75/50/
  25 Prozent/aus) umgesetzt - erledigt 2026-08-14, siehe
  docs/Debian-zu-DialOS.md Schritt 11. Erste echte Vosk-Nutzung im
  Betrieb, Erkennungslogik mit Piper-synthetisierten Testwörtern
  verifiziert (alle fünf Optionen korrekt erkannt).

- ☑️ **2026-08-16** — Echten Test der Lautstärke-Abfrage mit tatsächlich gesprochener
  Antwort durchgeführt (über das Bluetooth-Mikrofon, inkl.
  `headset-head-unit`-Profilwechsel) - erledigt 2026-08-16. Dabei einen
  echten Bug gefunden und behoben: Beim ersten Versuch fehlte ein
  klares Startsignal, wann genau das 4-Sekunden-Aufnahmefenster
  beginnt - Stephans gesprochene Antwort ("25") wurde verpasst, nur der
  100 %-Sicherheits-Fallback kam an. Fix: `dialos-start-ansage.py`
  sagt jetzt direkt vor der Aufnahme zusätzlich "Und jetzt bitte." -
  danach im zweiten Versuch korrekt erkannt (echtes "25" → 25 %).

- ☑️ **2026-08-17** — **Ansagen unterscheiden: Frage oder Hinweis - gebaut am
  2026-08-17.** `dialos-say.py --frage`, Standard ist die natürliche
  Satzmelodie aus dem Fragezeichen, der Signalton ist Option über
  `~/.config/dialos/frageton`. Siehe `docs/Debian-zu-DialOS.md`,
  Schritt 11a. Offen bleibt nur, das später per Sprachbefehl umschaltbar
  zu machen („Signalton einschalten") - das braucht erst den Schalter
  „Sprachsteuerung starten/stoppen".

  **Ursprüngliche Beschreibung (Stephans Frage vom 2026-08-17).** Heute weiß das System es implizit - der Code entscheidet
  ja, was gesagt wird -, gibt es aber nirgends weiter: `dialos-say.py`
  bekommt einen Text und spricht ihn. Wichtiger als das Wissen des
  Systems ist, dass **der Nutzer die Frage als Frage erkennt**: Für
  jemanden, der den Bildschirm nicht sieht, ist „wartet es auf mich?" die
  entscheidende Information. Am 2026-08-16 ist genau daran der erste Test
  der Lautstärke-Frage gescheitert - das System fragte, Stephan wusste
  nicht wann. Behelf war der Satz „Und jetzt bitte.". Sauber wäre: der
  Sprachausgabe eine Art mitgeben (Hinweis/Frage), und bei einer Frage
  automatisch ein kurzes, immer gleiches Signal. Ein **Ton** wäre dafür
  besser als ein Satz - schneller, unmissverständlich, nutzt sich nicht ab.

- ☑️ **2026-08-19** — **Lock-Datei von `dialos-start-ansage.py` aus `/tmp` holen** - erledigt 2026-08-19, nachdem der Fall live eingetreten war: Zwei Start-Ansagen liefen gleichzeitig, weil `nutzer` die geteilte Datei besaß und `dialosadmin` sie nicht überschreiben konnte. Liegt jetzt in `$XDG_RUNTIME_DIR`.
  **So stand die Aufgabe vorher da (zur Herkunft):**
  `/tmp/dialos-start-ansage.pid` ist ein fester Pfad im geteilten `/tmp` -
  dieselbe Bauart, die am 2026-08-16 bei der Sprechen-Markierung zu einem
  stillen Fehlschlag geführt hat (Sticky-Bit: ein Konto kann die Datei
  eines anderen weder überschreiben noch löschen). Die Markierung liegt
  jetzt unter `$XDG_RUNTIME_DIR`, diese Datei noch nicht.

- ☑️ **2026-08-24** — **Aussprache von „DialOS" entschieden** - Stephan nach
  Gehoer, aus acht Schreibweisen. **Anna sagt „Dial O S", Michael bleibt bei
  „Dial OS"** („Michael lassen wir wie bisher und bei Anne die Variante 2").
  Betrifft nur die Sprachausgabe; das Wort selbst bleibt ueberall DialOS.

  Gemessen, damit es niemand erneut durchprobiert: **Piper kennt keine
  mittlere Pause.** Komma, Semikolon, Doppelpunkt, Auslassungspunkte,
  Gedankenstrich und mehrere Leerzeichen ergeben alle exakt 0 ms Stille; nur
  Satzende-Zeichen erzeugen welche (Punkt 220 ms, Fragezeichen 230 ms,
  Ausrufezeichen 290 ms). Der Punkt traf sogar Stephans eigene Sprechpause -
  an einer Aufnahme seiner Stimme gemessen: 105 und 180 ms -, machte aber aus
  dem Wort zwei Saetze. Sein Urteil: „das zweite ist ja alles aber nicht das
  Wort DialOS". „Dial O S" fuegt deshalb keine Stille ein, sondern spricht die
  Buchstaben einzeln: 0,47 auf 0,64 s.

  Dabei fiel ein alter Fehler auf: Am Satzende griff die Regel **gar nicht**.
  Der Lookahead schloss jeden folgenden Punkt aus, also auch den Schlusspunkt -
  „Willkommen bei DialOS." wurde als ein Wort gelesen. Behoben.
- ☑️ **2026-09-14** — **Längere Pausen zwischen den Sätzen** (offen seit
  2026-08-17). Hörprobe mit drei Fassungen derselben Ansage; Stephan wählte
  zweimal „Variante B" - erst für Anna, dann nach eigener Hörprobe auch für
  Michael. `--sentence_silence 0.5` in `piper-generic.conf` und
  `dialos-say.py`. **Die Annahme des Punkts war falsch:** Piper hing die Sätze
  nicht „fast ohne Pause" aneinander - gemessen waren es schon rund 0,45 s,
  jetzt rund 0,78 s. Am Gerät nachgemessen (760/940 ms). Die Hörbeispiele unter
  `docs/sprachbeispiele/` sind noch mit der alten Pause erzeugt; die Skripte
  dafür sind nachgezogen.

### Audio: Mikrofon und Lautsprecher

- ☑️ **2026-08-17** — **Ursache der Mikrofon-Übersteuerung geklärt (2026-08-17).** Der
  systemweite Dienst läuft beim Booten, WirePlumber stellt seinen Zustand
  erst in der Sitzung wieder her und hebt den Boost dabei zurück - der
  Dienst war strukturell zu früh dran. Der Sprachdienst richtet den Pegel
  jetzt selbst, nachdem er die Aufnahme geöffnet hat, und regelt bei
  anhaltender Übersteuerung nach. Getestet durch absichtliches
  Hochdrehen.

- ☑️ **2026-08-17** — **Fehlauslösung durch abgespielte Inhalte behoben (2026-08-17).**
  Echo-Unterdrückung über PipeWires `module-echo-cancel` eingerichtet,
  32 dB Dämpfung gemessen, und der Fall, der vorher scheiterte (Ansage
  per `paplay` abgespielt), löst nichts mehr aus. Details im
  Änderungsprotokoll und in `docs/Debian-zu-DialOS.md`, Schritt 11f.

### Diktat, Auskunft und Alltagsdienste

- ☑️ **2026-08-14** — Wetter-Standort auf GeoClue2 umgestellt statt IP-geraten - erledigt
  2026-08-14, ausführlich live getestet (siehe README-Änderungsprotokoll
  0.5.0 und docs/Debian-zu-DialOS.md, Schritt 11, für Details). Auslöser:
  `wttr.in`s eigene IP-Standorterkennung zeigte Wien statt Stephans
  echtem Standort (Seefeld in Tirol) - ein fest hinterlegter Ort schied
  aus, da das Gerät auch unterwegs genutzt wird. Live-Erkenntnis dabei:
  GeoClue2 fällt in Gegenden mit dünner Mozilla-WLAN-Datenbank-Abdeckung
  ebenfalls auf eine grobe IP-Schätzung zurück ("ipf fallback",
  ~25-26 km ungenau, real ~300 km daneben) - deshalb Genauigkeits-
  Schwellwert (>10 km wird verworfen) eingebaut, Wetteransage wird dann
  bewusst ausgelassen statt eine falsche Stadt/Region zu nennen. Kann
  dadurch in ländlichen Gegenden öfter fehlen als vorher - gewollter
  Trade-off.

- ☑️ **2026-08-19** — **Gross-/Kleinschreibung im Diktat gemessen statt vermutet** - erledigt
  2026-08-19. **10 von 11** Faellen richtig, gemessen mit `schreibung_richten()`
  selbst. Der einzige Fehlschlag ist eine Wortliste ohne Grammatik
  ("milch sechs eier butter") - dort fehlt LanguageTool der Satz, um Substantive
  zu erkennen. Einzeln geht jedes Wort richtig, und einzeln kommen sie seit
  demselben Tag. Bei Briefen und Mails, also ganzen Saetzen, ist die Schreibung
  belastbar. Die fruehere Einschaetzung "dringendster offener Punkt" ist damit
  zurueckgenommen.

- ☑️ **2026-08-19** — **Die erste Korrektur jeder Sitzung war ein Muenzwurf** - erledigt
  2026-08-19. LanguageTools deutsche Regeln laden bei der ersten
  **Pruefanfrage**, nicht beim Serverstart: 9,2 s gegen eine Zeitgrenze von
  10,0 s. Am 2026-08-19 um 10:03:03 hat sie verloren. Behoben durch
  `dialos-schreibhilfe-warmlaufen.py` als `ExecStartPost` der Unit - belegt im
  Journal: 9096 ms beim Start, danach 985 ms fuer die erste echte Korrektur.
  Nebenbefund: `lt_lebt()` prueft `/v2/languages` und meldet damit "laeuft",
  waehrend der Dienst neun Sekunden braucht - eine Bereitschaftsmeldung, die
  etwas anderes prueft als das, worauf es ankommt.

### Desktop und Bedienoberfläche

- ☑️ **2026-08-10** — Live-Desktop-Icon für die Installation (`.desktop`-Datei mit
  eigenem DialOS-Icon statt "Install System"/Ei-Icon auf dem
  Live-Boot-Desktop) - erledigt 2026-08-10 (Branding via
  skel-Überschreibung).

- ☑️ **2026-08-14** — AppIndicator-Pakete für `dialos-tts-indicator.py`
  (`gnome-shell-extension-appindicator`, `gir1.2-ayatanaappindicator3-0.1`)
  in der Paketliste verankert - erledigt 2026-08-14, dabei zusätzlich
  `gnome-shell-extension-desktop-icons-ng` (DING) ergänzt: GNOME zeigt
  seit Jahren keine Desktop-Icons mehr von Haus aus, ohne diese
  Erweiterung wären die Büro-Setup-Skripte auf `dialosadmin`s
  Arbeitsfläche (siehe unten) unsichtbar geblieben.

- ☑️ **2026-08-16** — **Optionale Windows-11-Optik für GNOME gebaut** (Stephans Wunsch
  vom 2026-08-16, umgesetzt am selben Tag).
  `/usr/local/bin/dialos-desktop-stil.sh` schaltet in beide Richtungen um
  (`windows` / `gnome` / `status`), die drei Debian-Erweiterungen
  (`dash-to-panel`, `arc-menu`, `tiling-assistant`) stehen in der
  Paketliste und werden mitinstalliert, aber nicht eingeschaltet.
  Beschrieben in `docs/Debian-zu-DialOS.md`, Schritt 11b.

- ☑️ **2026-08-16** — **Windows-Umschaltung technisch getestet (2026-08-16).** Pakete
  installiert, dreimal hin- und hergeschaltet, jeden berührten Schlüssel
  verglichen: Rückweg stellt den Auslieferungszustand her, mehrfaches
  Ausführen erzeugt keine Doppeleinträge. Dabei zwei Fehler gefunden und
  behoben (GNOME Shell kennt frisch installierte Erweiterungen nicht;
  ArcMenu-Schema liegt in Debian im falschen Ordner) - Details im
  Änderungsprotokoll.

### Installation, ISO und Systemaufbau

- ☑️ **2026-08-10** — Neuen ISO-Build mit allen gesammelten Fixes (Bootscreen,
  Avatar-Skript, Calamares-Branding, Piper-TTS) erstellen - erledigt
  2026-08-10/11 (ISO vom 11.08.).

- ☑️ **2026-08-14** — Konsolidierungs-Skript `scripts/dialos-full-office-setup.sh` +
  neues `dialos-setup-home-partition.sh` (führt `dialos-install`s LUKS/
  Stick-Logik auf einem bereits installierten System aus, ohne dessen
  Festplatten-Wipe/rsync-Kopie) erstellt, `Debian-zu-DialOS.md`/`.en.md`
  entsprechend aktualisiert (Schritt 1: Partitionierungs-Hinweis;
  Schritt 12: neues Werkzeug) - erledigt 2026-08-14, beide Skripte nur
  syntaktisch geprüft (`bash -n`), noch nicht real gelaufen (siehe
  Punkt oben).

- ☑️ **2026-08-16** — **Erledigt (2026-08-16): `dialos-install` ist ersatzlos entfallen**
  (Weg A - jedes Gerät entsteht im Büro aus der Debian-ISO plus den drei
  Skripten, es gibt keinen Live-Boot-Installer mehr). Damit erledigen
  sich auch dessen Fehler. **`dialos-rekey` bleibt** und hat sie noch -
  dort nachziehen, wenn es das nächste Mal angefasst wird: gleicher
  `$HOME`-Startordner im Backup-Dialog (Zeile 142) und fehlende Fallbacks
  in `ask_password`. Ursprünglicher Eintrag: **`dialos-install` und
  `dialos-rekey` hatten dieselben Fehler wie
  das durchgesehene `dialos-setup-home-partition.sh`** - bewusst nicht
  mitkorrigiert, weil über den Klon-Pfad noch nicht entschieden ist (Punkt
  weiter unten). Betroffen: gleiches zu langes ext4-Label
  `dialos-nutzer-home` (`dialos-install` Zeile 248), gleiche
  Klartext-Passphrase unter festem Namen `/tmp/.rp` (Zeile 199), gleicher
  `$HOME`-Startordner im Backup-Dialog (Zeile 231, `dialos-rekey` Zeile
  142), gleiche fehlende Fallbacks in `ask_password`/`zenity --list`.
  Entweder mitziehen oder zusammen mit dem Klon-Pfad entfallen lassen -
  aber nicht auseinanderlaufen lassen.

- ☑️ **2026-08-16** — **Zeitzone/Locale entschieden (Stephan, 2026-08-16): bleibt
  `Europe/Vienna` + `de_AT.UTF-8`.** Nicht `Europe/Berlin`, wie die Doku
  bis dahin vorschrieb. Folge, jetzt in Debian-zu-DialOS.md Schritt 1
  dokumentiert: Baugerät und jede daraus gezogene ISO tragen die
  österreichischen Einstellungen (`eggs produce --clone` klont
  `/etc/localtime` + Locale mit). Am selben Tag durch die Entscheidung
  für Weg A weiter vereinfacht: Jedes Gerät wird im Büro über den
  Debian-Installer aufgesetzt, die Zeitzone wird also pro Gerät in
  Schritt 1 gewählt.

- ☑️ **2026-08-16** — **Erledigt durch Wegfall (2026-08-16):** Calamares-Standort-Seite
  schlug beim Live-Boot GeoIP-basiert oft
  einen falschen Standort vor (z. B. Rome statt Berlin) - kein
  dokumentierter Vendor-Override für `modules/locale.conf` gefunden (nur
  Branding ist offiziell überschreibbar). Bleibt vorerst
  Werkzeug-Einschränkung; installierende Person muss Standort beim
  Durchklicken manuell prüfen/korrigieren (unkritisch bei
  Zwei-Phasen-Provisionierung, da Endkunden den Installer nie sehen).

- ☑️ **2026-08-16** — Erster Eintrag in `docs/iso-builds.md` erfolgt: `eggs produce
  --clone` am 16.08. gelaufen (21/21 Schritte fehlerfrei, 6,50 GiB),
  `DialOS-Live-0.5.1-clone.iso` als Backup-Snapshot vor dem geplanten
  End-to-end-Test (siehe nächster Punkt) - Version/Datum/Commit/SHA256
  eingetragen.

- ☑️ **2026-08-16** — **Erledigt am 2026-08-16: acht alte ISOs gelöscht (~59 GB).** Alle
  stammten aus der entfallenen Penguins-Eggs-Zeit. `DialOS-Live-0.5.1-
  clone.iso` bleibt bewusst liegen, bis Stephans erstes
  Rescuezilla-Abbild da ist - sie existiert nirgendwo sonst und ließe
  sich nicht neu erzeugen. Dokumentiert in `docs/iso-builds.md`.
  Ursprünglich: **Prämisse überholt, neu zu entscheiden (geprüft 2026-08-16):**
  `DialOS-Live-0.5.1-clone.iso` liegt **nicht** mehr lokal - der Reinstall
  hat sie mitgenommen. Sie existiert weiterhin auf der externen Platte
  unter `DialOS-ISOs/`, zusammen mit vier älteren Abbildern; zusammen
  **28 GB**.

  Die eigentliche Frage ist jetzt eine andere: Alle fünf stammen aus der
  Penguins-Eggs-Zeit, die am 2026-08-16 entfallen ist, und bilden einen
  Systemstand ab, den der heutige Neuaufbau deutlich überholt hat. Lohnt
  sich dafür noch ein Nextcloud-Upload, oder werden sie gelöscht und
  `docs/iso-builds.md` behält sie nur als Verzeichnis?

  Das kann nur Stephan entscheiden - es ist seine Sicherungsstrategie.
  Ursprünglicher Eintrag: liegt bisher nur lokal, noch in die Nextcloud
  hochladen (kein Claude-Zugriff darauf).
- ☑️ **2026-09-14** — **Rechtschreibprüfung in der Paketliste:**
  `hunspell-de-de` und `hunspell-en-us` in `desktop.list.chroot`. Nachgesehen:
  Auf dem Gerät waren sie schon installiert, aber nur als „automatisch" über
  `task-german-desktop` - ausdrücklich gelistet hängen sie nicht mehr an einem
  Metapaket. `aspell` bewusst weggelassen: Kein Programm auf dem Gerät nutzt
  es; LibreOffice, Firefox, Thunderbird und GNOME greifen auf hunspell.

### Verschlüsselung, Konten und Sicherheit

- ☑️ **2026-08-16** — **Swap entschieden (Stephan, 2026-08-16): 8 GiB, verschlüsselt,
  automatisch in `dialos-setup-home-partition.sh`.** Ausgangslage: eine
  37,3-GiB-Klartext-Swap-Partition (`nvme0n1p3`), in die `nutzer`s
  Speicherseiten - offene Dokumente, Mails, Browserinhalte - ausgelagert
  werden konnten; ohne Sicherheits-Stick lesbar, ebenso nach Ausbau der
  SSD, also genau am Schutz von `dialos-nutzer-home` vorbei. Umgesetzt:
  Das Skript ersetzt einen vorgefundenen Klartext-Swap durch 8 GiB mit
  einem bei jedem Start neu gewürfelten Schlüssel (`/etc/crypttab`,
  `/dev/urandom`, Referenz per PARTUUID statt Dateisystem-UUID),
  setzt `vm.swappiness=10` und `RESUME=none`, und schlägt den
  freigewordenen Platz der Home-Partition zu (auf dem T490: 345,6 →
  rund 375 GiB). Begründung der Größe: die Regel "Swap ≥ RAM" existiert
  nur wegen des Ruhezustands, und der ist bei diesem Sicherheitsdesign
  ohnehin ausgeschlossen (das Abbild bräuchte einen dauerhaften Schlüssel
  im initramfs - der verworfene `cryptsetup-initramfs`-Ansatz). Ganz
  weglassen kam nicht in Frage: ohne Swap beendet der OOM-Killer bei
  Speichermangel Prozesse hart, und ein abgeschossener Screenreader
  bedeutet für einen blinden Nutzer den völligen Verlust der Rückmeldung.
  Suspend-to-RAM bleibt unberührt. **Noch nicht real gelaufen** - passiert
  beim ersten Durchlauf mit auf dem echten Gerät.

- ☑️ **2026-08-18** — **Wo liegen die Mailbox-Zugangsdaten? Entschieden am 2026-08-18:**
  Datei in `/home/nutzer`, Rechte 0600 - nicht der Schlüsselbund (der
  entsperrt sich unter Autologin nicht zuverlässig und schützt hinter
  derselben LUKS-Tür ohnehin nicht zusätzlich) und nicht der Stick (er
  trägt den LUKS-Schlüssel, kann abgezogen werden, und wäre eine zweite
  Stelle für dasselbe). Begründung in `docs/sicherheit-datenschutz.md`.
  Ursprünglich stand hier:
  DialOS liest und schreibt Mail direkt über IMAP/SMTP, weil Thunderbird
  von außen nur `-compose` kennt und kein Lesen erlaubt (siehe
  `docs/anwendungen.md`). Damit braucht DialOS die Zugangsdaten selbst.
  Zwei Wege: GNOME-Schlüsselbund über libsecret, oder eine Datei, die nur
  dem Konto gehört. **Gehört zur Sicherheits-Architektur**, nicht in eine
  Nebenentscheidung - `docs/sicherheit-datenschutz.md` mit entscheiden.
  Zum Testen liegt die Adresse `proband@dialos.org` bereit
  (Mailserver `s111.goserver.host`, keine Autoconfig-Einträge).
  **Fußzeile nicht vergessen:** Dieser Versandweg muss sich die
  Herkunftszeile selbst holen (`dialos-fusszeile.py text --art mail`).
  Die Thunderbird-Signatur vom 2026-08-20 greift nur bei Mails, die
  durch Thunderbird gehen - also bei denen des sehenden Helfers.

### Protokolle, Repo und Arbeitsumgebung

- ☑️ **2026-08-14** — `scripts/dialos-claude-setup.sh` erweitert (Git-Identität +
  `credential.helper=store` für `dialosadmin`) und tatsächlich
  ausgeführt/verifiziert - erledigt 2026-08-14. `~/DialOS`-Symlink jetzt
  bestätigt vorhanden (per `readlink -f`, zeigt korrekt auf
  `.../SanDisk-Extreme/DialOS/repo`), Sudoers-Regel war schon vorhanden,
  Git-Identität + `credential.helper` per `git config --global`
  bestätigt. (Der vorherige "erledigt"-Eintrag hierzu war falsch - das
  Skript war nie erfolgreich mit `sudo` durchgelaufen, siehe
  Commit-Historie.)

- ☑️ **2026-08-16** — **Erledigt durch den Neuaufbau (geprüft 2026-08-16):** `~/DialOS-repo`
  existiert nicht mehr - der Reinstall des T490 hat die Zweitkopie
  beseitigt. Damit ist die Gefahr weg, die den Eintrag ausgelöst hatte.
  Der Symlink `~/DialOS` zeigt jetzt auf das Repo der externen Platte,
  es gibt also nur noch eine Kopie. Ursprünglich: Veraltete lokale
  Repo-Zweitkopie unter `~/DialOS-repo` löschen oder
  bewusst als Backup behalten (Entscheidung noch offen) - der Symlink
  `~/DialOS` ist jetzt tatsächlich korrekt gesetzt (siehe "Erledigt"
  unten), aber die Zweitkopie selbst liegt noch da. Zwei unabhängige
  Kopien nebeneinander sind fehleranfällig - genau dadurch sind zwei nie
  gepushte Commits vom 13.08. am 14.08. fast verloren gegangen.

- ☑️ **2026-08-16** — **Gegenstandslos seit 2026-08-16:** `/home/eggs/*.iso`-Restdateien aufräumen -
  Penguins' Eggs ist entfallen (Schritt 16, jetzt Rescuezilla), und auf dem
  neu aufgebauten T490 war es ohnehin nie installiert. Ursprünglich:
  (gehören `root`, die `eggs produce`-NOPASSWD-Regel deckt nur
  `eggs produce` selbst ab, nicht `rm` - braucht Stephans manuelles
  `sudo rm`).

- ☑️ **2026-08-20** — **Die Protokolle wachsen unbegrenzt** - erledigt 2026-08-20. Stephans
  Entscheidung: sieben Tage, dieselbe Frist wie beim Support-Protokoll.
  Umgesetzt ueber `/etc/logrotate.d/dialos` statt in den sechs Programmen -
  logrotate laeuft taeglich per systemd-Timer, waehrend ein Dienst, der eine
  Woche durchlaeuft, nie zum Aufraeumen kaeme. Ohne `copytruncate`, weil die
  Programme ihre Datei nicht offen halten (geprueft), mit `dateext`, weil im
  Support nach einem Tag gesucht wird und nicht nach einer Nummer. Offen bleibt
  nur, dass eine NEU angelegte Datei 0644 bekommt - ab der ersten Rotation gilt
  0600.
