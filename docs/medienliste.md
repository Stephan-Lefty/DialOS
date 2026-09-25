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

Vorgeschlagenes
Austauschformat (noch nicht entschieden), damit DialOS die Datei direkt liest -
später als `docs/medienliste.json` neben dieser Vorlage:

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
