# Drehbuch: Vorführvideo „Was DialOS heute kann"

**Stand: 2026-10-05, Entwurf - noch nicht gedreht.** Stephan: ein Video,
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
[sprachbefehle.md](sprachbefehle.md) steht. Radio, Podcasts und Drucken
kommen nicht vor (Radio ist noch nicht gebaut, ein Drucker gehört nicht
zum Aufbau).

## Die Musterdaten

Alles im Video ist erfunden. Keine echte Person, keine echte Adresse,
keine echte Mailadresse - `example.org` ist eine dafür reservierte
Domain, die es nie geben wird.

| Rolle | Name | Anschrift | Mail |
|---|---|---|---|
| Nutzer (Absender) | Max Mustermann | Musterstraße 1, 12345 Musterstadt | `max.mustermann@example.org` |
| Kontakt (Empfängerin) | Erika Musterfrau | Beispielweg 7, 54321 Beispielstadt | `erika.musterfrau@example.org` |

**Gedreht wird in einem eigenen Vorführkonto** (Vorschlag: `vorfuehrung`),
nicht in `nutzer` und nicht in `dialosadmin`. Dort steht nichts von
Stephan, und nach dem Dreh kann das Konto komplett gelöscht werden. Die
Musterdaten kommen über die Maske der persönlichen Daten hinein - genau
wie bei einem echten Kunden. Das ist zugleich ein Test der Maske.

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

Geschätzte Länge: **5 bis 6 Minuten.**

### 1. Aufwachen (ca. 0:15)

| Anna | DialOS | Bild |
|---|---|---|
| „Sprachsteuerung starten" | „Ich höre Dir zu." | Leerer Desktop, das Mitschrift-Fenster geht auf |

### 2. Uhrzeit und Datum (ca. 0:20)

| Anna | DialOS | Bild |
|---|---|---|
| „Wie spät ist es?" | „Es ist … Uhr …." | Mitschrift |
| „Welchen Tag haben wir?" | „Heute ist …, der …." | Mitschrift |

### 3. Einkaufszettel (ca. 1:00)

Zeigt: Rückfrage mit ja/nein, Diktat, Zählen statt Vorlesen, Vorlesen auf
Zuruf.

| Anna | DialOS | Bild |
|---|---|---|
| „Einkaufszettel aufnehmen" | „Soll ich etwas in den Einkaufszettel schreiben? Sage ja oder nein." | Mitschrift |
| „ja" | „Einen Moment, ich hole Zettel und Stift." … „Ich schreibe mit." „Sage jede Ware einzeln, mit einer kleinen Pause dazwischen." | Mitschrift |
| „Milch" - „Brot" - „Äpfel" (je 2 s Pause) | - | Mitschrift |
| „Diktat beenden" | „Diktat beendet, 3 Einträge geschrieben. …" | Mitschrift |
| „Einkaufszettel vorlesen" | „… 3 Einträge: Milch. Brot. Äpfel." *(Probelauf)* | Mitschrift |

### 4. Ein Brief an Erika Musterfrau (ca. 1:45)

Zeigt: Empfänger aus den Kontakten, gesprochene Satzzeichen, Vorlesen,
PDF für den Helfer.

| Anna | DialOS | Bild |
|---|---|---|
| „Brief schreiben" | „Soll ich einen neuen Brief schreiben? Sage ja oder nein." | Mitschrift |
| „ja" | „An wen geht der Brief?" | Mitschrift |
| „Erika Musterfrau" | Liest den Kontakt vor, fragt nach *(Probelauf)* | Mitschrift |
| „ja" | „Einen Moment, ich hole Zettel und Stift." … „Ich schreibe mit." | Mitschrift |
| „Liebe Erika Komma neuer Absatz vielen Dank für Deinen Besuch am Sonntag Punkt Ich habe mich sehr gefreut Punkt neuer Absatz Viele Grüße" | - | Mitschrift |
| „Diktat beenden" | Bestätigung *(Probelauf)* | Mitschrift |
| „Brief vorlesen" | Satzzahl, Empfänger, Datum, Text, dann „Du kannst sagen: Brief drucken oder Brief als PDF speichern." | Mitschrift |
| „Brief als PDF speichern" | „Der Brief liegt jetzt als PDF in Deinen Dokumenten." | **Schnitt-Idee:** das PDF kurz im Dokumentenbetrachter zeigen - der Briefbogen mit Musteranschrift ist das stärkste Bild des Videos *(automatisch öffnen, Probelauf)* |

### 5. Eine E-Mail - ohne sie zu verschicken (ca. 1:30)

Zeigt: den ganzen Mail-Dialog, die Eckdaten vor dem Senden, und dass
DialOS nichts ohne „ja" verschickt.

| Anna | DialOS | Bild |
|---|---|---|
| „E-Mail schreiben" | Fragt nach dem Empfänger *(Probelauf)* | Mitschrift |
| „Erika Musterfrau" | Kontakt vorlesen, nachfragen *(Probelauf)* | Mitschrift |
| „ja" | „Was soll im Betreff stehen?" | Mitschrift |
| „Einladung" | *(Probelauf)* | Mitschrift |
| „Liebe Erika Komma kommst Du am Samstag zum Kaffee Fragezeichen neuer Absatz Viele Grüße" | - | Mitschrift |
| „Diktat beenden" | „2 Sätze an Erika Musterfrau, Betreff Einladung. Soll ich sie verschicken? Sage ja, nein, oder vorlesen." | Mitschrift |
| „nein" | Legt sie als Entwurf ab *(Probelauf)* | Thunderbird mit dem Entwurf |

### 6. Etwas wiederfinden (ca. 0:45, kann entfallen)

| Anna | DialOS | Bild |
|---|---|---|
| „Unterlagen durchsuchen" | Fragt, wo gesucht werden soll | Mitschrift |
| „Dokumente" | „Wonach soll ich in den Dokumenten suchen? Sage einen Begriff." | Mitschrift |
| „Erika" | Nennt den Brief aus Szene 4, fragt nach *(Probelauf)* | Mitschrift |
| „vorlesen" | Liest den Brief | Mitschrift |

### 7. Programme auf Zuruf (ca. 0:30)

| Anna | DialOS | Bild |
|---|---|---|
| „Internet öffnen" | *(Probelauf)* | Firefox geht auf |
| „Internet schließen" | „Soll ich … schließen? Sage ja oder nein." *(Probelauf)* | Firefox |
| „ja" | *(Probelauf)* | Firefox geht zu |

### 8. Schluss (ca. 0:10)

| Anna | DialOS | Bild |
|---|---|---|
| „Sprachsteuerung stoppen" | „Ich höre Dir nicht mehr zu." | Mitschrift geht zu, leerer Desktop, 3 s stehen lassen |

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
3. **Die Erkennung darauf zeigen lassen** über
   `~/.config/dialos/befehl-mikrofon` im Vorführkonto - dieselbe Datei,
   über die man DialOS ein bestimmtes Mikrofon vorgibt. Das
   Standard-Mikrofon des Systems wird **nicht** verändert. Ein
   `.monitor`-Gerät ginge nicht: Die Erkennung lässt diese bewusst aus.
4. Danach Sprachsteuerung neu starten, damit sie die Quelle übernimmt.
5. **Nach dem Dreh aufräumen:** Datei entfernen, virtuelles Mikrofon
   schließen - auch bei Abbruch (das Skript räumt in jedem Fall auf).

### Der Ablauf - vollautomatisch

Ein Skript (`scripts/dialos-video-dreh.py`, noch zu bauen) liest die
Szenen und spielt sie ab:

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

1. Stephan gibt das Drehbuch frei (Szenen, Musterdaten, Länge).
2. Vorführkonto anlegen, Musterdaten über die Maske, Kontakt Erika
   Musterfrau anlegen, Thunderbird offline.
3. `obs-studio` und `ffmpeg` installieren, OBS einrichten.
4. Skript bauen, Probelauf, Wortlaute hier eintragen.
5. Dreh. Danach Vorführkonto löschen.
