# Drehbuch: Vorführvideo „Was DialOS heute kann"

**Stand: 2026-10-05, von Stephan freigegeben - noch nicht gedreht.** Stephan: ein Video,
vollautomatisch erstellt, in dem zu sehen und zu hören ist, was DialOS
heute kann. **Anna spielt die Nutzerin, Michael ist DialOS.** Mit
Musterdaten, hochauflösend, jede Stimme auf einer eigenen Tonspur.

Nur Deutsch: Das Video ist deutschsprachig, eine englische Fassung des
Drehbuchs hätte keinen Gegenstand. Wie DialOS grundsätzlich gefilmt wird
(OBS, Spuren, Fallen), steht in [video-aufnahme.md](video-aufnahme.md).

## Grundsatz: nichts ist gestellt

Anna spricht nicht einfach über das Video, sie spricht **mit DialOS**.
Ihre Sätze gehen in ein virtuelles Mikrofon, und die echte Spracherkennung
hört sie so, als säße jemand vor dem Gerät. Was im Video passiert, hat
DialOS wirklich verstanden und wirklich getan. Versteht es einen Satz
nicht, sieht man das - dann wird die Szene im Probelauf angepasst, nicht
im Schnitt geschönt.

Gezeigt wird nur, was unter „Umgesetzt" in
[sprachbefehle.md](sprachbefehle.md) steht. Radio, Podcasts, Drucken und
die Suche kommen nicht vor (Radio ist noch nicht gebaut, ein Drucker gehört nicht
zum Aufbau; die Suche hat Stephan am 2026-10-05 gestrichen, damit das
Video kurz bleibt).

## Die Musterdaten

Alles im Video ist erfunden. Keine echte Person, keine echte Adresse,
keine echte Mailadresse - `example.org` ist eine dafür reservierte
Domain, die es nie geben wird.

| Rolle | Name | Anschrift | Mail |
|---|---|---|---|
| Nutzer (Absender) | Max Mustermann | Musterstraße 1, 12345 Musterstadt | `max.mustermann@example.org` |
| Kontakt (Empfängerin) | Frau Erika Musterfrau | Beispielweg 7, 54321 Beispielstadt | `erika.musterfrau@example.org` |

**Gedreht wird in einem eigenen Vorführkonto** (Vorschlag: `vorfuehrung`),
nicht in `nutzer` und nicht in `dialosadmin`. Dort steht nichts von
Stephan, und nach dem Dreh kann das Konto komplett gelöscht werden. Die
Musterdaten trägt `scripts/dialos-video-dreh.py einrichten` in die Datei der
persönlichen Daten ein und verteilt sie mit `dialos-mailkonto.py` an
Thunderbird - derselbe Weg wie aus der Maske, nur ohne Tippen.

**Der Kontakt heißt „Frau Erika Musterfrau", mit Anrede.** Ohne Anrede hält
DialOS den Empfänger für eine mögliche Firma und fragt nach einem
Ansprechpartner; mit Anrede steht die Anschrift im Brief nach DIN richtig
da. Angelegt wird er mit Mailadresse (die braucht die Mail-Szene).

**Das Mailkonto bleibt offline** (Thunderbird `offline.startup_state = 3`):
`example.org` hat keinen Mailserver, online käme eine Fehlermeldung ins
Bild. Die Mail-Szene endet ohnehin mit „nein" - **es wird nichts
verschickt**, die Mail landet als Entwurf.

## Die Szenen

Je Szene: was Anna sagt, was DialOS (Michael) antwortet, was man sieht.
Wörtlich übernommen aus [sprachbefehle.md](sprachbefehle.md); wo dort kein
fester Wortlaut steht, ist die Stelle mit *(Probelauf)* markiert und wird
beim ersten Durchlauf festgehalten. Das Mitschrift-Fenster ist während
des ganzen Videos offen - es zeigt sehenden Zuschauern, was erkannt wurde,
und wirkt im Video wie ein Untertitel.

Geschätzte Länge: **rund 5 bis 6 Minuten.**

### 1. Aufwachen (ca. 0:15)

| Anna | DialOS | Bild |
|---|---|---|
| „Sprachsteuerung starten" | „Ich höre Dir zu." | Leerer Desktop, das Mitschrift-Fenster geht auf |

### 2. Uhrzeit und Datum (ca. 0:20)

| Anna | DialOS | Bild |
|---|---|---|
| „Wie viel Uhr ist es?" | „Es ist … Uhr …." | Mitschrift |
| „Welchen Tag haben wir?" | „Heute ist …, der …." | Mitschrift |

### 3. Einkaufszettel (ca. 1:00)

Zeigt: Rückfrage mit ja/nein, Diktat, Zählen statt Vorlesen, Vorlesen auf
Zuruf.

| Anna | DialOS | Bild |
|---|---|---|
| „Einkaufszettel aufnehmen" | „Soll ich etwas in den Einkaufszettel schreiben? Sage ja oder nein." | Mitschrift |
| „Ja!" | „Einen Moment, ich hole Zettel und Stift." … „Ich schreibe mit. Sage jede Ware einzeln, mit einer kleinen Pause dazwischen." | Mitschrift |
| „Zwei Liter Milch." - „Ein Laib Brot." - „Ein Kilo Äpfel." (je 2 s Pause) | - | Mitschrift |
| „Diktat beenden" | „Diktat beendet, 3 Einträge geschrieben. …" | Mitschrift |
| „Einkaufszettel vorlesen" | Anzahl der Einträge, dann die drei Waren *(Wortlaut: Probelauf)* | Mitschrift |

### 4. Ein Brief an Frau Erika Musterfrau (ca. 1:45)

Zeigt: Empfänger aus den Kontakten, natürliches Sprechen (die Satzzeichen
setzt Parakeet), Vorlesen, PDF für den Helfer.

| Anna | DialOS | Bild |
|---|---|---|
| „Brief schreiben" | „Soll ich einen neuen Brief schreiben? Sage ja oder nein." | Mitschrift |
| „Ja!" | „An wen geht der Brief? Sage den Namen oder die Firma. …" | Mitschrift |
| „Frau Erika Musterfrau." | „In den Kontakten steht: Frau Erika Musterfrau, Beispielweg 7, Postleitzahl 5 4 3 2 1, Beispielstadt. Ist das der Empfänger? Sage ja oder nein." | Mitschrift |
| „Ja!" | „Einen Moment, ich hole Zettel und Stift." … „Ich schreibe mit." | Mitschrift |
| „Liebe Frau Musterfrau, vielen Dank für Ihren Besuch am Sonntag. Ich habe mich sehr gefreut. Herzliche Grüße" | - | Mitschrift |
| „Diktat beenden" | Bestätigung *(Probelauf)* | Mitschrift |
| „Brief vorlesen" | Satzzahl, Empfänger, Datum, Text, dann „Du kannst sagen: Brief drucken oder Brief als PDF speichern." | Mitschrift |
| „Brief als PDF speichern" | „Der Brief liegt jetzt als PDF in Deinen Dokumenten." | Mitschrift. **Schnitt-Idee für später:** das PDF kurz im Dokumentenbetrachter zeigen - der Briefbogen mit Musteranschrift ist das stärkste Bild des Videos |

### 5. Eine E-Mail - ohne sie zu verschicken (ca. 1:30)

Zeigt: den ganzen Mail-Dialog, die Eckdaten vor dem Senden, und dass
DialOS nichts ohne „ja" verschickt.

| Anna | DialOS | Bild |
|---|---|---|
| „E-Mail schreiben" | „Einen Moment, ich hole Zettel und Stift." „An wen soll die E-Mail gehen? Sage den Namen aus Deinen Kontakten, oder sage: buchstabieren." | Mitschrift |
| „Frau Erika Musterfrau." | „An Frau Erika Musterfrau, … Stimmt das? Sage ja oder nein." | Mitschrift |
| „Ja!" | „Was soll im Betreff stehen?" | Mitschrift |
| „Eine Einladung zum Kaffee." | „Sage jetzt den Text der E-Mail. Wenn Du fertig bist, sage: Diktat beenden." | Mitschrift |
| „Hallo Erika, kommst Du am Samstag zum Kaffee? Viele Grüße" | - | Mitschrift |
| „Diktat beenden" | „2 Sätze an Frau Erika Musterfrau, Betreff Eine Einladung zum Kaffee. Soll ich sie verschicken? Sage ja, nein, oder vorlesen." | Mitschrift |
| „Nein!" | Legt sie als Entwurf ab *(Wortlaut: Probelauf)* | Mitschrift |

### 6. Programme auf Zuruf (ca. 0:30)

| Anna | DialOS | Bild |
|---|---|---|
| „Internet öffnen" | *(Probelauf)* | Firefox geht auf |
| „Internet schließen" | „Soll ich … schließen? Sage ja oder nein." *(Probelauf)* | Firefox |
| „Ja!" | *(Probelauf)* | Firefox geht zu |

### 7. Radio (ca. 0:40)

Aufgenommen am 2026-10-08 (Stephan: „Du kannst ja das Radio schon mit ins
Drehbuch nehmen"). **Achtung beim Veröffentlichen:** Hier läuft echte Musik
von Ö3 - für die Website gehört die Szene gekürzt oder die Musik leiser
gelegt, damit kein ganzes Lied im Video steht.

| Anna | DialOS | Bild |
|---|---|---|
| „Ö3 einschalten" | „Hitradio Oe3." - Ö3 spielt | Mitschrift |
| „Was läuft gerade?" | „Es läuft Hitradio Oe3: …" mit Liedtitel, wenn Ö3 einen mitschickt | Mitschrift |
| „Lauter machen" | „Lauter." | Mitschrift |
| „Radio abstellen" | „Radio aus." | Mitschrift |

„Ö3" statt „Ö drei" in Annas Text: Piper spricht „Ö drei" so, dass Vosk
„wie drei" hört - offline geprüft. Während Musik läuft, wird es auf dem
Lautsprecher nie still; der Dreh wartet hier deshalb auf Michaels Ansage im
Protokoll und dann feste Sekunden.

### 8. Schluss (ca. 0:10)

| Anna | DialOS | Bild |
|---|---|---|
| „Sprachsteuerung stoppen" | „Ich höre Dir nicht mehr zu." | Mitschrift geht zu, leerer Desktop, 3 s stehen lassen |

## Annas Sätze - vorher geprüft

Am 2026-10-05 lief jeder Satz offline gegen dieselben Erkenner wie im Betrieb:
Piper spricht mit Annas Stimme (`kerstin-low`, Tempo 0,95), Vosk hört die
Befehle mit der vollständigen Grammatik, Parakeet das Diktat. Die Befehle kamen
alle wörtlich an. Was **nicht** ging, hat das Drehbuch verändert - nicht
geschönt, sondern so umformuliert, wie es ein Mensch auch sagen würde:

| Gesagt | Erkannt | Darum im Drehbuch |
|---|---|---|
| „nein" | **„ja"** | „Nein!" - sonst hätte DialOS die Mail verschickt |
| „ja" | nichts | „Ja!" |
| „Milch", „Brot", „Äpfel" | „fest", „das", „pfiffe" | mit Menge: „Zwei Liter Milch." usw. |
| „Liebe Erika, …" | „Liebe Edika, …" | Brief förmlich: „Liebe Frau Musterfrau, …" |
| „Einladung" (Betreff) | „I know." | „Eine Einladung zum Kaffee." |
| „Wie spät ist es?" | „wie spät ist das" (mit Michaels Stimme) | „Wie viel Uhr ist es?" |

Kurze Einzelwörter scheitern bei dieser einfachen Stimme, ganze Sätze nicht.
„Hallo Erika, …" in der Mail kam dagegen fehlerfrei an, samt Fragezeichen.
**Das gehört nicht in die Erkennung „repariert"** - Annas Stimme ist kein
Mensch. Ob echte Nutzer mit „nein" dasselbe Problem haben, beantworten die
Protokolle vom Gerät, nicht diese Probe.

**Bewusst nicht im Video:** Die Start-Ansage nach dem Anmelden mit der
Lautstärke-Frage. Sie passiert beim Anmelden, und dabei läuft noch kein
Rekorder (siehe [video-aufnahme.md](video-aufnahme.md)). Sie kann später
als eigener kurzer Teil mit Kamera und Stativ gedreht werden.

## Technik

### Bild: hochauflösend

- **1920×1080 bei 30 Bildern/s** - das ist die volle Auflösung des
  Laptop-Bildschirms (eDP-1, geprüft 2026-10-05). Mehr wäre nur
  hochgerechnet und keinen Deut schärfer.
- Aufgenommen mit **OBS** wie in [video-aufnahme.md](video-aufnahme.md),
  Format MKV, aber mit **hoher Qualität** (konstante Qualität statt fester
  Bitrate, Schrift im Mitschrift-Fenster muss gestochen scharf sein).
- OBS ist seit dem Neuaufbau nicht mehr installiert (`obs-studio`, für den
  Dreh nachinstallieren; ins Rezept gehört es nicht).

### Ton: jede Stimme auf eigener Spur

| Spur | Inhalt | Quelle |
|---|---|---|
| 1 | Mischung - zum Anhören und für die Web-Fassung | beide |
| 2 | **Michael / DialOS** - Ansagen und Frageton | Mitschnitt der Lautsprecher-Ausgabe |
| 3 | **Anna / Nutzerin** | das virtuelle Mikrofon |

**Diesmal ganz sauber getrennt.** Bei der Aufnahme vom 2026-08-17 hörte das
eingebaute Mikrofon den Lautsprecher mit, Spur 3 enthielt Michael dumpf
mit. Hier gibt es kein Raummikrofon: Anna geht direkt in das virtuelle
Mikrofon, Michael nur auf den Lautsprecher. Keine Spur hört die andere.

### Anna ins virtuelle Mikrofon

1. **Annas Sätze vorab erzeugen** - jede Zeile der Szenen als eigene
   WAV-Datei, mit derselben Stimme, die DialOS als „Anna" kennt
   (Piper `kerstin-low`, Tempo 0,95).
2. **Virtuelles Mikrofon anlegen** mit `pw-loopback`: ein Eingang, in den
   die WAVs gespielt werden, und eine Quelle `dialos_anna_mikrofon`, die
   wie ein echtes Mikrofon aussieht.
3. **Die Echo-Unterdrückung darauf umhängen** - siehe „Was die ersten Drehs
   gelehrt haben", Punkt 4. Die Mikrofonwahl der Befehlserkennung
   (`befehl-mikrofon`) reicht nicht: Rückfragen und Diktat kennen sie nicht.
4. Danach Sprachsteuerung neu starten, damit sie die Quelle übernimmt.
5. **Nach dem Dreh aufräumen:** Echo-Unterdrückung zurück aufs eingebaute
   Mikrofon, virtuelles Mikrofon schließen - auch bei Abbruch.

### Der Ablauf - vollautomatisch

Das Skript `scripts/dialos-video-dreh.py` liest die Szenen und spielt sie ab
(gebaut am 2026-10-05):

1. OBS startet mit `--startrecording`, minimiert.
2. Zwei Sekunden Ruhe.
3. Für jede Zeile: Annas WAV ins virtuelle Mikrofon spielen, dann **warten,
   bis DialOS fertig gesprochen hat** (Stille auf Spur 2 für 1,5 s), dann
   eine kleine Pause wie bei einem Menschen. Feste Wartezeiten gingen
   schief - das Diktat braucht beim Start rund 9 s, eine Uhrzeit eine.
4. Am Ende drei Sekunden stehen lassen, OBS beenden.

**Einmal muss Stephan klicken:** Beim allerersten Start fragt GNOME, ob OBS
den Bildschirm aufnehmen darf. Das gehört zum Probelauf; danach merkt OBS
sich die Freigabe, und jeder weitere Dreh läuft ohne Klick.

### Was herauskommt

- `dialos-vorfuehrung.mkv` - Bild mit allen drei Spuren, für den Schnitt.
- `dialos-vorfuehrung.mp4` - Bild mit der Mischung, für Website und
  Weitergabe (aus der MKV erzeugt, braucht `ffmpeg` - ebenfalls nur für
  den Dreh).
- `dialos-vorfuehrung-anna.wav`, `dialos-vorfuehrung-dialos.wav` - die
  beiden Stimmen einzeln, 48 kHz.

## Gedreht im Konto dialosadmin - der Vorführmodus (seit 2026-10-08)

Stephan: „Können wir das nicht im DialOSadmin Account machen" - ohne
Kontowechsel, ohne Streit um die Soundkarte, und Claude ist dabei. Damit
dort nichts Persönliches ins Bild kommt und nichts durcheinandergerät,
schaltet `dialos-video-dreh.py drehen --vorfuehrmodus` für die Dauer des
Drehs um und danach in jedem Fall zurück (auch bei Abbruch):

- **Gesichert und gegen Musterdaten getauscht:** persönliche Daten; dazu
  gesichert Mail-Vormerkungen, Kontakt-Warteschlange, zuletzt gehörter
  Sender und das ganze Thunderbird-Adressbuch (als Datei - SQLite ändert sie
  schon durch Einfügen und Löschen, Trockenlauf: Prüfsumme danach gleich).
- **Gelöscht wird danach nur, was neu ist** - in Dokumente, Notizen und
  Bilder wird vorher alles aufgelistet.
- **Thunderbird muss zu sein**, sonst bricht der Dreh vorher ab: Der
  Mail-Entwurf wird dann nur vorgemerkt, nicht ins echte Postfach gelegt.
- **Benachrichtigungen** sind währenddessen aus.
- **Kein Neustart von PipeWire und keiner der Erkennung** - umgehängt wird
  nur der Eingang der Echo-Unterdrückung.
- **Firefox darf ins Bild** (Stephan: „das ist nur der Tab dialos.org").
- Sicherungen liegen unter `~/.local/state/dialos-vorfuehrung/`.

Das Claude-Fenster kann der Dreh nicht selbst ausblenden - vor dem Start mit
Super+H weg, sonst steht es im Bild.

## Was die ersten Drehs gelehrt haben (2026-10-05)

Fünf Anläufe, keiner bis zum Ende - aber jeder hat genau eine Ursache
gezeigt, und jede ist im Skript behoben:

1. **Die Soundkarte gehört dem Konto `dialosadmin`.** Es steht in der Gruppe
   `audio`, und seine Spracherkennung hält das Mikrofon dauernd offen. Das
   Vorführkonto bekam deshalb nur `auto_null` - keinen Ton, kein Mikrofon.
   **Vor jedem Dreh** wird PipeWire in `dialosadmin` angehalten
   (`systemctl --user stop pipewire.socket pipewire-pulse.socket pipewire
   pipewire-pulse wireplumber filter-chain`) und danach wieder gestartet; das
   Skript startet PipeWire im Vorführkonto neu, damit es die Karte findet.
2. **Annas Eingang wurde Standard-Lautsprecher** - im frischen Konto ist kein
   Standard gespeichert. Das Skript setzt Lautsprecher und Mikrofon jetzt
   ausdrücklich.
3. **Ein kurzer Ton galt als Michaels Antwort**, Annas „Ja!" fiel in seine
   Frage. Gewartet wird jetzt auf mindestens eine halbe Sekunde Sprache.
4. **Rückfragen, Diktat und Mail hören fest auf `dialos_mikrofon_ohne_echo`**,
   nur die Befehlserkennung kennt eine Mikrofonwahl. Die Befehle hörten Anna,
   die Rückfrage danach nichts. Jetzt wird der Aufnahme-Strom der
   Echo-Unterdrückung auf Annas Mikrofon umgehängt (`pactl move-source-output`)
   - alle Programme hören sie auf dem Weg, den sie auch im Betrieb nehmen.
   Hier am Gerät geprüft: „ja" und „wie viel uhr ist es" kamen so an.
   *Nicht* gegangen ist eine gleichnamige Datei unter
   `~/.config/pipewire/pipewire.conf.d/` - PipeWire hat sie ignoriert.

5. **Annas Sätze kamen stumm zur Welt** (2026-10-08, erster Dreh im Konto
   dialosadmin). Michael antwortete auf „Wie viel Uhr ist es?", während
   Annas Strom noch auslief; `dialos-say.py` schaltet für jede Ansage alle
   fremden Ströme stumm, Annas Strom endete, die Freigabe ging ins Leere -
   und PipeWire merkt sich die Stummschaltung je Programmname. Jeder weitere
   Satz startete mit „Mute: yes". Dieselbe Falle wie paplay am 2026-08-24.
   Annas Ströme heißen jetzt `speech-dispatcher-dialos-video-anna`: Ströme
   mit diesem Namensanfang lässt `dialos-say.py` bewusst in Ruhe, und Anna
   ist eine Stimme. Am Produkt wurde nichts geändert.

Michael sagt außerdem an, wann der Dreh beginnt, endet oder abbricht - vor
und nach der Aufnahme, also nicht im Video. Ohne Ton erscheint ein Fenster.

**Stand:** Szenen 1 und 2 laufen, der Einkaufszettel bricht bisher an der
Rückfrage ab. Der nächste Dreh ist der erste mit allen vier Korrekturen.

## Risiken, die erst der Probelauf zeigt

- **Versteht das Diktat Annas Stimme?** `kerstin-low` ist eine einfache
  Stimme. Die Befehle (Vosk mit fester Grammatik) sind unkritisch, das
  freie Diktat (Parakeet) könnte stolpern. Wenn ja: Sätze vereinfachen,
  nicht das Ergebnis schönen.
- **Wortlaute** an den mit *(Probelauf)* markierten Stellen.
- **Thunderbird offline:** Ob der Entwurf ohne Server sauber abgelegt wird.
- **Benachrichtigungen** im Vorführkonto vorher abschalten („Nicht
  stören"), damit kein Update-Hinweis ins Bild rutscht.

## Reihenfolge

1. ~~Stephan gibt das Drehbuch frei~~ - erledigt 2026-10-05 (Szene
   „Etwas wiederfinden" gestrichen, sonst wie entworfen).
2. Vorführkonto anlegen, Musterdaten über die Maske, Kontakt Erika
   Musterfrau anlegen, Thunderbird offline.
3. `obs-studio` und `ffmpeg` installieren, OBS einrichten.
4. Skript bauen, Probelauf, Wortlaute hier eintragen.
5. Dreh. Danach Vorführkonto löschen.
