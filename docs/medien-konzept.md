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

## Nachrichten: entschieden, aber nicht überall machbar (2026-10-05)

> **Stephan, 2026-10-05:** „Beim Nachrichtensender dachte ich - die neueste
> Folge einer Kurznachrichten-Sendung" und „Prio regional - Land - Europa -
> Welt"

**Die Form ist damit entschieden:** nicht ein Sender live, sondern die neueste
Folge. Das war seit dem 2026-09-25 offen und ist der Grund, warum
„Nachrichten hören" bisher nicht gebaut werden konnte.

**„Regional - Land - Europa - Welt" ist das ANGEBOT, nicht die Reihenfolge**
(Stephan, 2026-10-05 auf die Rückfrage): „Wir müssen dem Nutzer die Chance
geben das er sich gezielt über regionale Nachrichten, aber auch landesweite
und weltweite Nachrichten in deutscher Sprachen informieren kann. Und er kann
dann gezielt sagen was er jetzt hören möchte."

Es gibt also **je Ebene einen eigenen Satz**, und der Nutzer wählt. Kein
Block, der alles hintereinander spielt - das wäre bequem für den, der alles
hören will, und im Weg für den, der nur das Wetter von morgen in Tirol sucht.

**Die Formulierungen sind geprüft** (2026-10-05, gegen
`vosk-model-small-de-0.15`): „regionale nachrichten", „landesweite
nachrichten", „weltweite nachrichten", „deutsche nachrichten",
„österreichische nachrichten", „europäische nachrichten" und die Varianten
mit „nachrichten aus ..." - **kein Wort fehlt im Wortschatz**, und keine
Formulierung kollidiert mit einer anderen oder mit einem der 55 bestehenden
Sätze. Die Wahl der Formulierung ist damit frei und nicht durch den Erkenner
eingeschränkt.

**Alles auf Deutsch** ist Stephans ausdrückliche Vorgabe („in deutscher
Sprachen"). Das schließt die naheliegenden fremdsprachigen Kurzformate aus -
auch bei „weltweit" bleibt die Quelle deutschsprachig.

### „Landesweit" hängt am Gerät, nicht an der Liste (2026-10-05)

> **Stephan, 2026-10-05:** „Wir müssen ja immer für 3 Länder denken, DialOS
> soll für Deutschland, Österreich und die Schweiz sein"

**Damit war meine Frage „Österreich oder Deutschland?" falsch gestellt** - und
die Radio-Liste vom selben Tag ist es auch: Sie enthält ORF Radio Tirol, weil
Stephan in Tirol wohnt. Auf einem Gerät für einen Schweizer Kunden wäre
„radio tirol einschalten" ein Befehl, der niemandem nützt, und „landesweite
Nachrichten" müsste dort SRF bringen, nicht Ö3.

**Die Lösung ist schon angelegt, sie wird nur noch nicht benutzt:** Die
persönlichen Daten haben die Felder `Land` und `Bundesland`
(`persoenliche-daten-vorlage.txt`, Zeilen 38/39), und jeder Eintrag der
Medienliste hat ein `land` (DE/AT/CH). Es fehlt nur die Verbindung:

- **Die systemweite Liste darf Einträge für alle drei Länder haben.** Sie ist
  der Vorrat, nicht das Angebot.
- **In die Grammatik kommt nur, was zum Land des Geräts passt** - sonst hat
  ein Schweizer Nutzer dreißig Sätze, von denen zwanzig ins Leere gehen, und
  die Regel „weniger ist mehr" ist unterlaufen.
- **„Regionale Nachrichten" löst sich über `Bundesland` auf.** In Tirol ORF
  Radio Tirol, in Bayern Bayern 1, im Kanton Zürich Radio 24 - die
  Bundesland-Tabelle in `dialos_rhythmbox_sender.py` kennt alle 49 Länder
  und Kantone schon.
- **Steht in den persönlichen Daten kein Land**, gilt alles. Ein leeres Feld
  darf das Radio nicht abschalten; das wäre schlimmer als eine zu lange
  Liste.

**Noch nicht gebaut.** `medienliste_lesen()` filtert heute nur nach `art`,
nicht nach Land. Die Radio-Liste vom 2026-10-05 ist deshalb bis auf weiteres
**Stephans Liste**, keine Auslieferungsliste - für ein Kundengerät müsste sie
nach dessen Land zusammengestellt werden.

**Zwei Punkte bleiben beim Bauen zu klären:**

1. **„Nachrichten vorlesen" und „Was gibt es Neues" stehen noch unter den
   Wunsch-Sätzen** mit der Antwort „Nachrichten kann ich noch nicht
   vorlesen." Sobald die Ebenen gebaut sind, verdecken diese zwei Einträge
   etwas, das es gibt - sie gehören dann aufgelöst, so wie „radio
   einschalten" am 2026-09-30.
2. **Quellen je Land**, und die fehlen für zwei Drittel: Belegt ist nur die
   tagesschau (DE). Für Österreich ist ein Ö3-Nachrichten-Podcast bekannt,
   aber ungeprüft; für die Schweiz ist noch nichts gesucht; für „weltweit"
   und „Europa" fehlt eine deutschsprachige Quelle.

**Was die Prüfung am 2026-10-05 ergeben hat - und es passt nicht glatt
zusammen:**

| Ebene | Befund |
|---|---|
| **Regional (Tirol)** | **Es gibt keinen Kurznachrichten-Podcast.** ORF Tirol bietet nur „Stehaufmenschen" und „Bei die Leut'" an, beides keine Nachrichten. Regionale Nachrichten gibt es dort **nur im laufenden Programm**, zur vollen Stunde. |
| Land (DE) | „tagesschau in 100 Sekunden" läuft: ein Feed mit **genau einem** `<item>`, also immer die neueste Folge, 3,7 kB, direkte MP3-Adresse im `<enclosure>`. Geprüft und brauchbar. |
| Land (AT) | Ein „Ö3 Nachrichten Podcast" ist belegt, aber noch nicht technisch geprüft. |
| Europa | Noch keine Quelle gefunden. Reine Europa-Nachrichten als Kurzformat sind selten. |
| Welt | Deckt die tagesschau mit ab. |

**Daraus folgt: Die regionale Ebene braucht den Sender, nicht den Podcast.**
Genau dafür hat das Format von Anfang an **zwei** Werte - `nachrichten-sender`
und `nachrichten-podcast` -, und genau deshalb wurden sie am 2026-09-30 beide
stehen gelassen, statt die Entscheidung vorwegzunehmen. Für Tirol heißt das:
ORF Radio Tirol live als `nachrichten-sender`, die übrigen Ebenen als
`nachrichten-podcast`.

**Ein Befund, der über die Nachrichten hinausgeht:** Nicht jeder RSS-Feed hat
Audio. Die beiden Nachrichten-Feeds des Deutschlandfunks
(`nachrichten-100.rss` und `die-nachrichten.353.de.rss`) liefern 39 Einträge
und **kein einziges `<enclosure>`** - das sind Textartikel. Eine Prüffunktion
für Podcast-Feeds muss das als Erstes feststellen, sonst steht ein Eintrag in
der Liste, der nie einen Ton macht.

## Eine zentrale Liste auf einem Server (Stephans Idee vom 2026-10-05)

> **Stephan, 2026-10-05:** „Aber wir müssen uns offen halten immer welche
> hinzuzufügen oder zu entfernen und das eventuell zentral über eine Liste
> auf einen Server für alle Nutzer"

**Der Bedarf ist unstrittig.** Streamadressen veralten - allein beim Bau am
2026-09-25 waren drei von 78 Einträgen falsch, und bei SWR Kultur musste eine
Adresse von Hand nachgetragen werden. Ohne einen Weg, das nachzuliefern, hängt
jeder Kunde auf dem Stand seines Aufbautags fest, und ein verstummter Sender
sieht für einen blinden Nutzer wie ein kaputtes Gerät aus.

**Die gebaute Struktur trägt das schon.** `medienliste_lesen()` liest mehrere
Dateien in einer Rangfolge und legt die höhere über die niedrigere; eine
Server-Liste wäre schlicht eine dritte Ebene. Sinnvolle Ordnung:

| Rang | Ebene | Wer pflegt |
|---|---|---|
| 1 (gewinnt) | `~/.config/dialos/medienliste.json` | der Nutzer selbst |
| 2 | die nachgeladene Liste vom Server | zentral |
| 3 | `/usr/local/share/dialos/medienliste.json` | Auslieferungszustand |

**Fünf Fragen sind vor dem Bau zu klären. Nichts davon ist entschieden:**

1. **Offline-first gilt weiter.** DialOS muss ohne Netz vollständig
   funktionieren. Eine Server-Liste darf deshalb nur eine *Ergänzung* sein,
   nie eine Voraussetzung - und wenn der Abruf scheitert, muss das
   **lautlos** bleiben und die vorhandene Liste weiter gelten. Eine
   Fehlermeldung über eine nicht erreichbare Senderliste nützt einem blinden
   Nutzer nichts; sie beunruhigt ihn nur.
2. **Der Abruf verrät etwas, und zwar Personenbezogenes.** Jede Anfrage zeigt
   dem Server eine IP-Adresse und damit: Hier steht ein DialOS-Gerät. Da die
   Zielgruppe blinde und motorisch eingeschränkte Menschen sind, entsteht beim
   Betreiber - also bei Stephan - eine Liste, die mehr aussagt als eine
   gewöhnliche Zugriffsstatistik. Das gehört in
   [sicherheit-datenschutz.md](sicherheit-datenschutz.md) und in die
   Datenschutzerklärung, bevor der erste Abruf stattfindet. Denkbare
   Entschärfung: kein Protokoll der IP-Adressen, Abruf über ein CDN, oder die
   Liste als Teil eines Paket-Updates statt als eigener Dienst.
3. **Wer die Liste ändern kann, bestimmt, was auf jedem Gerät spielt.** Ein
   übernommener Server könnte jede beliebige Adresse einspielen - auf Geräten
   von Menschen, die nicht nachsehen können, was sie hören. HTTPS schützt den
   Transportweg, nicht vor einem kompromittierten Server. Nötig wäre eine
   Signatur, die das Gerät prüft, mit einem Schlüssel aus dem Aufbau.
4. **Die eigene Wahl des Nutzers darf nie überschrieben werden.** Das ist
   dieselbe Falle wie bei `piper-generic.conf` am 2026-08-22, nur schärfer:
   Dort hat ein Aufspielen die Stimmwahl zurückgesetzt. Hier könnte ein
   fremder Server die Lieblingssender ersetzen. Die Rangfolge oben ist
   deshalb keine Feinheit, sondern die Bedingung.
5. **Wann wird nachgeladen?** Beim Anmelden, wöchentlich, oder nur auf
   Zuruf („Senderliste auffrischen")? Jeder Abruf ist ein Zeitpunkt, an dem
   etwas schiefgehen kann, und beim Anmelden wartet der Nutzer.

**Vorschlag für den Zwischenstand:** Solange das nicht entschieden ist, bleibt
es bei den zwei Ebenen. Nachliefern geht schon heute über `git pull` und
`dialos-aufspielen` - für Stephans eigenes Gerät reicht das, und für Kunden
gibt es noch keine. Die Entscheidung wird erst fällig, wenn das erste Gerät
außer Haus ist.

## Vorschlag für die Reihenfolge

1. ~~Medienliste füllen~~ **Radio erledigt am 2026-10-05:** zehn Sender,
   geprüft (Wortschatz, Kollisionen, ffprobe) - siehe
   [medienliste.md](medienliste.md).
2. ~~Radio: Sender abspielen, anhalten, lauter/leiser, „was läuft gerade"~~
   **gebaut am 2026-09-30** (`dialos-radio.py`); die zweite Pflichtprüfung
   steht noch am Gerät aus.
3. Nachrichten - sobald entschieden ist, welche Form.
4. Podcasts mit Merkposition.
5. Musik aus der eigenen Sammlung, Hörbücher.
6. Doku nachziehen: sprachbefehle.md, anwendungen.md, Rezept, Installationsanleitung.
