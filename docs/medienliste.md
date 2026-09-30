# Medienliste: Radio, Nachrichten, Podcasts, Hörbücher

Stephan, 2026-09-25: „ich will parallel eine Liste zusammen stellen. Die wir
dann für die Auswahl nutzen können." Daraus wird die Auswahl, die DialOS per
Sprache anbietet - abgespielt wird alles mit Rhythmbox (entschieden am
2026-09-25, siehe [anwendungen.md](anwendungen.md)). Wie das zusammenspielt,
steht im Konzept [medien-konzept.md](medien-konzept.md).

## So wird ausgefüllt

- **Nur die ersten zwei Spalten sind Pflicht:** wie man es sagt, und was es ist.
  Stream-Adressen und Podcast-Feeds sucht Claude heraus und prüft, ob sie
  laufen - die Spalte „Quelle" darf leer bleiben.
- **„So sagt man es"** ist der Satz, den der Nutzer sprechen soll - kurz,
  eindeutig, so wie man es im Alltag sagt: „Ö drei", nicht „Hitradio Ö3".
  Jeder Name wird vor dem Einbau gegen den Wortschatz der Spracherkennung
  geprüft; was dort fehlt, bekommt eine Sprechform (wie bei „Tas tatur").
- **Keine zwei Einträge, die ähnlich klingen** („Radio Tirol" und „Radio
  Tirol Süd") - die Erkennung verwechselt sie, und der Nutzer kann nicht
  nachsehen, was gerade läuft.
- **Weniger ist mehr:** lieber zehn Sender, die der Nutzer wirklich hört, als
  hundert, die er sich nicht merken kann. Die Liste gilt fürs ganze Gerät;
  persönliche Lieblingssender kommen später über die Maske der persönlichen
  Daten.
- Keine personenbezogenen Daten - die Liste liegt im öffentlichen Repository.

## Stephans App dafür - gebaut am 2026-09-25

**Sie ist da: DialOS-Rhythmbox.** Das Programm liegt als
`dialos-rhythmbox.py` im Repo (Oberfläche) mit
`dialos_rhythmbox_sender.py` darunter, das zugleich ein vollständiges
Kommandozeilen-Werkzeug ist. Es holt Sender von radio-browser.info,
testet jeden an - mit `ffprobe`, und zusätzlich wird der ICY-Name
verglichen, den der Sender über sich selbst sendet -, schlägt eine
Sprechform vor und schreibt genau das unten vorgeschlagene Format.
Einzelheiten im [Änderungsprotokoll](../README.md#änderungsprotokoll)
unter 0.5.3 und in [erweiterungen.md](erweiterungen.md).

**Die Warnung bei fast gleichen Sprechformen ist gebaut** - der Wunsch
unten wurde also erfüllt, und zwar sowohl in der Oberfläche (rot
markiert, schon beim Tippen) als auch vor dem Speichern. Sie ist kein
Beiwerk: Über alle 78 zunächst gesammelten Sender gerechnet meldet sie
elf verwechselbare Paare, etwa „we de er zwei" gegen „en de er zwei"
oder „radio niederoesterreich" gegen „radio oberoesterreich". Das ist
zugleich die praktische Bestätigung der Regel „weniger ist mehr" von
weiter oben: Bei 78 Sendern sind Kollisionen unvermeidlich. Die
Oberfläche startet deshalb **ohne gesetzte Haken** - die Auswahl trifft
der Mensch.

**Ein Feld mehr als unten vorgeschlagen:** `stationuuid`. Das
[Konzept](medien-konzept.md) verlangt sie, damit DialOS bei einem
ausgefallenen Stream die aktuelle Adresse nachschlagen kann.

## Wo die Datei liegt - zwei Ebenen (entschieden 2026-09-30)

Hier stand bis zum 2026-09-30 „später als `docs/medienliste.json` neben
dieser Vorlage". **Das wäre eine Sackgasse gewesen:** `dialos-aufspielen`
kopiert ausschließlich den Baum unter `iso-build/config/includes.chroot`,
und `docs/` gehört nicht dazu. Die Datei hätte richtig ausgesehen und wäre
nie auf einem Gerät angekommen.

Stattdessen gibt es sie **zweimal**, und das ist kein Umweg, sondern die
Lehre aus einem teuer bezahlten Fehler. Am 2026-08-22 standen in
`piper-generic.conf` zwei Dinge in einer Datei: die Konfiguration aus dem
Repo und die vom Nutzer gewählte Stimme. Das nächste Aufspielen setzte die
Wahl stillschweigend zurück. Bei der Medienliste steht dieselbe Falle
offen, und sie träfe den Nutzer härter - sein Lieblingssender wäre weg,
ohne dass er nachsehen könnte, warum.

| Datei | Was drinsteht | Wer sie schreibt |
|---|---|---|
| `/usr/local/share/dialos/medienliste.json` | der Auslieferungszustand, gilt fürs ganze Gerät | kommt über `dialos-aufspielen` aus dem Repo |
| `~/.config/dialos/medienliste.json` | was der Nutzer selbst aufnimmt, je Konto | die App am Gerät; **wird nie überschrieben** |

DialOS liest beide und legt die persönliche über die systemweite. Gleiche
Sprechform heißt derselbe Eintrag, wobei über die *Klangform* verglichen
wird - „radio kärnten" und „radio kaernten" sind für die Spracherkennung
derselbe Satz.

**Der Weg von der Werkbank ans Gerät** führt damit über git:

1. DialOS-Rhythmbox auf dem Arbeitsrechner öffnen und auswählen. Das
   Speichern-Ziel ist dort schon vorbelegt mit
   `iso-build/config/includes.chroot/usr/local/share/dialos/medienliste.json`.
2. Committen und pushen.
3. Am Gerät `git pull`, dann `sudo dialos-aufspielen --wirklich`.

Am Gerät selbst schlägt dieselbe App `~/.config/dialos/medienliste.json`
vor - dorthin darf ein normaler Nutzer schreiben, und kein Aufspielen
räumt es weg.

**Alle Gattungen liegen in derselben Datei** und unterscheiden sich nur im
Feld `art`: `radio`, `nachrichten-sender`, `nachrichten-podcast`,
`podcast`, `hoerbuch`. Die gültigen Werte stehen als Konstante `ARTEN` in
`dialos_rhythmbox_sender.py`; ein Test vergleicht sie mit dem Beispiel
unten, damit die beiden Stellen nicht auseinanderlaufen.

**Doppelte werden über alle Gattungen hinweg geprüft**, nicht je Gattung.
Der Nutzer spricht einen Satz, keine Gattung - ein Podcast und ein
Radiosender mit derselben Sprechform wären für ihn ununterscheidbar.

Austauschformat, damit DialOS die Datei direkt liest:

```json
{"stand": "2026-09-25",
 "eintraege": [
  {"art": "radio", "sprechform": "ö drei", "name": "Hitradio Ö3", "land": "AT", "quelle": ""},
  {"art": "nachrichten-sender", "sprechform": "", "name": "", "land": "", "quelle": ""},
  {"art": "nachrichten-podcast", "sprechform": "", "name": "", "land": "", "quelle": ""},
  {"art": "podcast", "sprechform": "", "name": "", "land": "", "quelle": ""},
  {"art": "hoerbuch", "sprechform": "", "name": "", "herkunft": ""}]}
```

`sprechform` klein und mit Zahlen als Wort, `quelle` darf leer bleiben. Hilfreich
wäre eine Warnung der App bei fast gleichen Sprechformen.

## Radio

| So sagt man es | Sender | Land | Quelle | Bemerkung |
|---|---|---|---|---|
|  |  |  |  |  |

## Nachrichten

Noch offen, wie „Nachrichten hören" gemeint ist - beides ist möglich und kann
nebeneinander stehen: ein **Nachrichtensender live** (Art „Sender") oder die
**neueste Folge** eines Nachrichten-Podcasts (Art „Podcast", z. B. eine
Kurznachrichten-Sendung, die mehrmals am Tag neu erscheint).

| So sagt man es | Sendung | Art (Sender/Podcast) | Land | Quelle | Bemerkung |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Podcasts

| So sagt man es | Podcast | Land | Quelle | Bemerkung |
|---|---|---|---|---|
|  |  |  |  |  |

## Hörbücher

Hörbücher sind Dateien, keine Sender: Sie liegen später in einem Ordner auf dem
Gerät oder dem Stick `DIALOS-DATA`. Hier nur, was es geben soll und woher es
kommt (z. B. freie Hörbücher, gekaufte Dateien, Bibliothek).

| So sagt man es | Titel | Herkunft | Bemerkung |
|---|---|---|---|
|  |  |  |  |
