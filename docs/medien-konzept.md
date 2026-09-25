[Deutsch](medien-konzept.md) | [English](medien-konzept.en.md)

# Konzept: Radio, Musik, Nachrichten und Podcasts

**Stand: 2026-09-25, Ideensammlung - noch nichts davon ist gebaut.** Stephan:
„als nächstes kümmern wir uns um Radio, Musik hören, Nachrichten hören,
Podcast hören." Dieses Papier sammelt, was dafür entschieden, vorgeschlagen
und offen ist, damit der Bau mit einem Plan beginnt statt mit dem ersten
Befehl.

## Entschieden

**Ein Player für alles: Rhythmbox** (Stephan, 2026-09-25). Radio, Musik,
Nachrichten, Podcasts und Hörbücher laufen über dasselbe Programm.

- **Warum nicht Shortwave fürs Radio:** Shortwave lässt sich von außen kein
  Sender vorgeben - keine Kommandozeile dafür, und über MPRIS nur Abspielen
  und Pause des zuletzt gehörten Senders. „Spiel Radio Tirol" wäre damit nicht
  machbar. Shortwave bleibt installiert, aber ohne Sprachsteuerung.
- **Warum nur ein Player:** Sagt der Nutzer „lauter", „stopp" oder „was läuft
  gerade?", muss eindeutig sein, was gemeint ist. Mit zwei Playern wäre es das
  nicht - und der Nutzer kann nicht nachsehen, welches Fenster vorn ist. Die
  Ein-Player-Regel aus [anwendungen.md](anwendungen.md) erledigt sich damit.
- **DialOS ist die Zentrale, Rhythmbox nur der Lautsprecher.** DialOS nimmt
  den Befehl an, sucht Sender oder Folge heraus und sagt Rhythmbox, was es
  spielen soll. Das Rhythmbox-Fenster braucht nur der sehende Helfer.

## Die Bausteine

### 1. Die Medienliste - die Auswahl

Eine kuratierte Liste statt der ganzen Senderdatenbank:
[medienliste.md](medienliste.md). Sie gilt fürs ganze Gerät. Zwei Gründe:

- **Überschaubar:** Zehn Sender, die der Nutzer wirklich hört, sind mehr wert
  als zehntausend, die er sich nicht merken kann.
- **Sprechbar:** Die Befehlserkennung (Vosk mit eingeschränkter Grammatik)
  kennt nur Wörter aus ihrem Wortschatz. Jeder Name der Liste wird vorher
  geprüft und bekommt bei Bedarf eine Sprechform - wie „Tas tatur".

**Stephan baut dafür eine kleine App** zum Erfassen. Vorgeschlagenes
Austauschformat (noch nicht entschieden) steht in [medienliste.md](medienliste.md):
eine JSON-Datei mit `art`, `sprechform`, `name`, `land`, `quelle`. DialOS
liest sie beim Start der Sprachsteuerung und baut daraus die Befehlssätze.

**Später: persönliche Lieblingssender** je Konto über die Maske der
persönlichen Daten - dieselbe Idee wie beim Mailkonto: zentral erfassen, an
die Programme verteilen.

### 2. Sender finden - radio-browser.info

Dieselbe freie Senderdatenbank, die Shortwave benutzt, ohne Konto und ohne
Schlüssel. Abgefragt wird sie **beim Pflegen der Liste**, nicht bei jedem
Befehl: Die geprüfte Stream-Adresse steht dann in der Liste, und das Abspielen
hängt nicht davon ab, dass die Datenbank gerade erreichbar ist.

- Suche nach Name: `https://de1.api.radio-browser.info/json/stations/byname/<name>?hidebroken=true`
- Maßgeblich ist `url_resolved` (die aufgelöste Stream-Adresse), dazu
  `stationuuid`, um einen Sender später wiederzufinden.
- Am 2026-09-25 probiert: „Radio Tirol" liefert sofort drei Streams von Life
  Radio Tirol (MP3 und AAC).
- **Fällt ein Stream aus**, sucht DialOS über die `stationuuid` die aktuelle
  Adresse nach und sagt das an - statt still nichts zu spielen.

### 3. Abspielen - rhythmbox-client

Alles, was die Sprachbefehle brauchen, ist da (am 2026-08-18 und 2026-09-25
geprüft): `--play-uri`, `--pause`, `--play-pause`, `--stop`, `--next`,
`--set-volume`, `--print-playing`. Das letzte ist wichtig: DialOS kann
ansagen, was gerade läuft. Für die Position (Podcasts, Hörbücher) kommt MPRIS
über D-Bus dazu (`Position`, `SetPosition`).

### 4. Podcasts und Nachrichten-Podcasts

Podcasts sind RSS-Feeds. DialOS liest den Feed, nimmt die neueste Folge (die
Adresse im `enclosure`) und gibt sie an Rhythmbox. **Die Merkposition verwaltet
DialOS selbst** - Rhythmbox speichert keine Wiedergabeposition (geprüft
2026-08-18: kein `playback-position`, kein `bookmark`). Beim Anhalten wird die
Position über MPRIS gelesen und je Folge unter `~/.config/dialos/` gemerkt,
beim „weiter hören" wieder gesetzt.

### 5. Nachrichten - noch offen, beides denkbar

- **Als Sender:** „Nachrichten hören" startet einen Nachrichtensender live.
- **Als neueste Folge:** eine Kurznachrichten-Sendung als Podcast, die mehrmals
  am Tag neu erscheint - der Nutzer hört immer die aktuelle Ausgabe, in wenigen
  Minuten, und danach ist Ruhe.

Beides kann nebeneinander in der Liste stehen; welche Form der Satz
„Nachrichten hören" auslöst, entscheidet Stephan.

### 6. Hörbücher

Hörbücher sind Dateien, keine Sender - ein Ordner auf dem Gerät oder auf dem
Stick `DIALOS-DATA`. Wichtig ist hier die Merkposition wie bei Podcasts: Ein
achtstündiges Hörbuch, das nach dem Einschalten von vorn beginnt, hört niemand.

## Sprachbefehle - erster Entwurf

Nichts davon ist geprüft. Jeder Satz muss durch die beiden Pflichtprüfungen
aus [sprachbefehle.md](sprachbefehle.md): Wortschatz des Modells UND die
vollständige Grammatik.

| Satz | Was passiert |
|---|---|
| „Radio einschalten" | Letzter Sender - oder Frage „Welcher Sender?" mit der Liste |
| „Spiel <Sprechform>" / „<Sprechform> einschalten" | Sender aus der Liste |
| „Nachrichten hören" | Nachrichtensender oder neueste Nachrichtenfolge (offen) |
| „Podcast <Sprechform>" | Neueste Folge, bzw. dort weiter, wo aufgehört wurde |
| „Musik abspielen" | Eigene Musik, zufällig oder die zuletzt gehörte |
| „Weiter hören" | Podcast/Hörbuch an der gemerkten Stelle |
| „Was läuft gerade" | Ansage über `--print-playing` |
| „Lauter" / „Leiser" | Lautstärke in festen Stufen |
| „Nächster Sender" | Nächster Eintrag der Liste |
| „Stopp" / „Radio ausschalten" / „Musik ausschalten" | Anhalten, Position merken |

**Den bestehenden Widerspruch auflösen:** Heute öffnen „Radio öffnen" und
„Musik öffnen" Shortwave bzw. Rhythmbox, während „Radio einschalten" und
„Musik abspielen" sagen, dass DialOS das noch nicht kann. Mit dem Bau
bekommen alle vier dieselbe Bedeutung: abspielen über Rhythmbox.

## Was dabei zu beachten ist

- **Ansagen während der Musik.** Spricht DialOS, während etwas läuft, muss die
  Musik leiser werden oder pausieren - sonst geht die Ansage unter. Ob leiser
  oder Pause, ist eine offene Entscheidung (TODO „Ansagen leiser als Musik").
- **Die Befehlserkennung hört mit.** Musik und Radio laufen durch die
  Echo-Unterdrückung (`dialos_mikrofon_ohne_echo`), damit ein
  Nachrichtensprecher, der zufällig einen Befehl sagt, nichts auslöst. Genau
  dafür wurde sie am 2026-08-17 gebaut - beim Bau mit Radio im Hintergrund
  prüfen.
- **Bluetooth-Lautsprecher:** Musik über den AIRHUG in A2DP; das Gerät darf
  dabei nicht ins Headset-Profil (HFP) rutschen - DialOS öffnet deshalb kein
  Bluetooth-Mikrofon (Audio-Festlegung 2026-08-17).
- **Datenschutz:** Die Abfrage bei radio-browser.info verrät den gesuchten
  Sendernamen, sonst nichts; ohne Konto. Streams und Feeds kommen direkt vom
  Sender. Ins Protokoll kommt, was gespielt wurde - das ist unkritischer als
  ein Diktat, gehört aber in die Protokoll-Tabelle von
  [sicherheit-datenschutz.md](sicherheit-datenschutz.md).
- **Konto `nutzer`:** Die Medienliste liegt systemweit, Merkpositionen je Konto.
  Nach dem Bau gehört beides in `dialos-nutzerkonto-pruefen.sh`.

## Vorschlag für die Reihenfolge

1. Medienliste füllen (Stephan, mit seiner App) und das Format festlegen.
2. Radio: Sender aus der Liste abspielen, anhalten, lauter/leiser, „was läuft
   gerade". Der kleinste Weg, der jeden Tag gebraucht wird.
3. Nachrichten - sobald entschieden ist, welche Form.
4. Podcasts mit Merkposition.
5. Musik aus der eigenen Sammlung, Hörbücher.
6. Doku nachziehen: sprachbefehle.md, anwendungen.md, Rezept, Installationsanleitung.
