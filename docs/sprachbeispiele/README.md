[Deutsch](README.md) | [English](README.en.md)

# Sprachbeispiele

Wie DialOS klingt, ohne dass man das Gerät vor sich hat. Erzeugt am
2026-08-18 auf Stephans Wunsch.

**Neu erzeugen** nach jeder Änderung an Stimme oder Tempo - sonst zeigen
die Dateien einen Stand, den es nicht mehr gibt:

```bash
scripts/dialos-sprachbeispiele.py
```

| Datei | Dauer | Was es ist |
|---|---|---|
| `01-start-ansage-nutzer.ogg` | 29,3 s | Die Ansage beim Einschalten, wie `nutzer` sie hört. |
| `02-lautstaerke-frage.ogg` | 10,0 s | Die Rückfrage nach der Lautstärke - kommt nur beim **ersten** Anmelden. |
| `03-sprachsteuerung-an.ogg` | 0,9 s | Antwort auf „Sprachsteuerung starten". |
| `04-sprachsteuerung-aus.ogg` | 1,2 s | Antwort auf „Sprachsteuerung stoppen". |
| `05-desktop-windows.ogg` | 1,4 s | Nach „auf Windows umschalten". |
| `06-desktop-steht-schon.ogg` | 2,1 s | Wenn der Schreibtisch schon so steht - eine andere Ansage als beim echten Wechsel, weil ein blinder Nutzer beides sonst nicht unterscheiden könnte. |
| `07-diktat-beginn.ogg` | 3,7 s | Beide Sätze beim Diktatstart. Der erste deckt die ~9 s Ladezeit des grossen Sprachmodells ab. |
| `08-einkaufszettel-vorlesen.ogg` | 5,8 s | „Einkaufszettel vorlesen". Die Anzahl kommt voran, dann die Einträge mit Pausen. |
| `09-einkaufszettel-wegwerfen.ogg` | 3,9 s | Die Rückfrage vor dem Leeren. |
| `10-ton-ueber-lautsprecher.ogg` | 1,5 s | Wenn der Bluetooth-Lautsprecher eingeschaltet wird und der Ton dorthin wandert. |
| `11-kein-mikrofon.ogg` | 3,5 s | Ein Fehlerfall - er wird **angesagt**, nicht nur ins Protokoll geschrieben. |

Zusammen 63 s und rund 380 kB. OGG Vorbis, weil `sox` das ohne
Zusatzpaket kann und WAV das Repo unnötig aufblähen würde.

## Die Entwicklungsgeschichte steckt in Git

Stephans Gedanke vom 2026-08-18: nachvollziehbar halten, wie sich „Michaels
Stimme" entwickelt hat. Dafür braucht es **keinen** Ordner pro Datum - jede
Neuerzeugung ist ein Commit, und die vorige Fassung bleibt abrufbar:

```bash
git log --oneline -- docs/sprachbeispiele/
git show <commit>:docs/sprachbeispiele/03-sprachsteuerung-an.ogg > /tmp/alt.ogg
```

Datierte Ordner würden nur verdoppeln, was die Versionsverwaltung ohnehin
tut - und das Repo bei jeder Änderung dauerhaft wachsen lassen statt nur um
den Unterschied.

## Was an diesen Dateien echt ist und was nicht

**Echt:** Stimme (Piper, `de_DE-thorsten-high`), Tempo (0,88), die
Aussprache-Regeln und der **Satzbau** der Start-Ansage - Wochentag,
Ordinalzahl und die Uhrzeit als Wort baut das Skript
`dialos-start-ansage.py` selbst zusammen, und das Beispiel benutzt genau
diese Funktionen statt einer Nachdichtung.

**Beispielwerte:** Datum und Uhrzeit sind fest gewählt, damit sich die
Dateien reproduzierbar erzeugen lassen. Akkustände und Wetter sind
erfunden - im Betrieb kommen sie von der Hardware und aus dem Netz. Fehlt
die Internetverbindung, sagt DialOS das an und lässt das Wetter weg.

**Nicht enthalten:** die Spracheingabe. Diese Dateien zeigen, wie DialOS
klingt, nicht wie es zuhört - dafür braucht es eine Aufnahme mit echter
Stimme, siehe [../video-aufnahme.md](../video-aufnahme.md).

## Warum das reproduzierbar ist

Erst seit `--noise_w 0` (2026-08-18). Piper hat einen Zufallsanteil in
der Lautdauer und sprach denselben Satz vorher mit bis zu **17 %**
anderer Dauer. Zwei Läufe dieses Skripts hätten also unterschiedlich
klingende Dateien erzeugt. Hintergrund in [../diktat.md](../diktat.md).
