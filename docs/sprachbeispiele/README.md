[Deutsch](README.md) | [English](README.en.md)

# Sprachbeispiele

Wie DialOS klingt, ohne dass man das Gerät vor sich hat. Erzeugt am
2026-08-18 auf Stephans Wunsch.

**Das ist Anna** (`de_DE-kerstin-low`, Tempo 1,00), die Auslieferungsstimme
seit dem 2026-08-20. Bis zum 2026-08-21 zeigten diese Dateien noch Michael:
Im Erzeuger stand die Stimme **fest eingetragen**, während das System längst
die andere sprach - dieselbe Falle wie beim Tempo eine Zeile darunter, nur
unbemerkt, weil die Dateien für sich genommen richtig klangen. Stimme und
Tempo kommen jetzt beide aus `piper-generic.conf`.

**Neu erzeugen** nach jeder Änderung an Stimme oder Tempo - sonst zeigen
die Dateien einen Stand, den es nicht mehr gibt:

```bash
scripts/dialos-sprachbeispiele.py
```

| Datei | Dauer | Was es ist |
|---|---|---|
| `01-start-ansage-nutzer.ogg` | 23,2 s | Die Ansage beim Einschalten, wie `nutzer` sie hört. |
| `02-lautstaerke-frage.ogg` | 7,5 s | Die Rückfrage nach der Lautstärke - kommt nur beim **ersten** Anmelden. |
| `03-sprachsteuerung-an.ogg` | 0,8 s | Antwort auf „Sprachsteuerung starten". |
| `04-sprachsteuerung-aus.ogg` | 1,4 s | Antwort auf „Sprachsteuerung stoppen". |
| `04b-sprachsteuerung-zeitgrenze.ogg` | 2,9 s | Wenn zwei Minuten kein Befehl kam. Bewusst **mit** Begründung - ein blosses „Ich höre Dir nicht mehr zu." liesse den Nutzer rätseln, warum. |
| `05-desktop-windows.ogg` | 1,2 s | Nach „auf Windows umschalten". |
| `06-desktop-steht-schon.ogg` | 1,7 s | Wenn der Schreibtisch schon so steht - eine andere Ansage als beim echten Wechsel, weil ein blinder Nutzer beides sonst nicht unterscheiden könnte. |
| `07-diktat-beginn.ogg` | 2,6 s | Beide Sätze beim Diktatstart einer Notiz. Der erste deckt die ~9 s Ladezeit des grossen Sprachmodells ab. |
| `07b-diktat-beginn-einkaufszettel.ogg` | 5,3 s | Dasselbe beim **Einkaufszettel** - mit der Anleitung „Sage jede Ware einzeln, mit einer kleinen Pause dazwischen." Nur hier, weil bei einer Notiz eine Äusserung wirklich ein Satz ist. Im Betrieb liegen zwischen den beiden Sätzen die 9 s Ladezeit; in der Datei stehen sie hintereinander. |
| `07c-diktat-ende-hinweis.ogg` | 6,1 s | Nach „Diktat beenden". Liest **nicht** mehr vor, sondern sagt die Anzahl und wie man das Vorlesen bekommt. **Die längste Ansage im System** - und damit an der Grenze der eigenen Regel, siehe unten. |
| `08-einkaufszettel-vorlesen.ogg` | 3,0 s | „Einkaufszettel vorlesen". Die Anzahl kommt voran, dann die Einträge mit Pausen. |
| `09-einkaufszettel-wegwerfen.ogg` | 4,0 s | Die Rückfrage vor dem Leeren - jetzt mit „Sage ja oder nein.", weil ein blinder Nutzer keine Knöpfe sieht. |
| `09b-rueckfrage-nochmal.ogg` | 2,5 s | Kam keine verwertbare Antwort, wird **einmal** nachgefragt statt abgebrochen. |
| `10-ton-ueber-lautsprecher.ogg` | 1,1 s | Wenn der Bluetooth-Lautsprecher eingeschaltet wird und der Ton dorthin wandert. |
| `11-kein-mikrofon.ogg` | 2,7 s | Ein Fehlerfall - er wird **angesagt**, nicht nur ins Protokoll geschrieben. |
| `12-akku-25.ogg` | 2,1 s | Erste Akkuwarnung bei 25 %. Eine schlichte Feststellung - hier ist noch nichts zu tun. |
| `12b-akku-15.ogg` | 4,0 s | Zweite Warnung bei 15 %, jetzt mit einem Rat. |
| `12c-akku-5.ogg` | 3,8 s | Dritte Warnung bei 5 % - **mit Namen** und als Aufforderung. Der Name steht nur hier: Wer ihn dauernd hört, überhört ihn. |
| `12d-akku-am-netz.ogg` | 1,7 s | Bestätigung nach dem Anstecken. Wer nicht sieht, ob der Stecker sitzt, braucht diese Rückmeldung. |

**Alle Ansagen, in beiden Stimmen:** [alle-ansagen/](alle-ansagen/VERZEICHNIS.md)
- 62 Sätze × 2 Stimmen, mit dem Datum und der Uhrzeit des Erzeugungstags.
Erzeugt von `scripts/dialos-alle-ansagen.py`. Diese Auswahl hier bleibt die
kurze Runde zum Reinhören.

Zusammen 77 s und rund 501 kB. OGG Vorbis, weil `sox` das ohne
Zusatzpaket kann und WAV das Repo unnötig aufblähen würde.

## Was die Dauer über die Ansagen verrät

Die Spalte „Dauer" ist nicht Beiwerk. Während DialOS spricht, hört es
**bewusst nicht zu** - jede Sekunde Ansage ist eine Sekunde, in der der Nutzer
warten muss. Deshalb steht in [../sprachbefehle.md](../sprachbefehle.md) die
Regel „Ansagen kurz halten, aber als Satz", und sie stammt aus einem Fehler
vom 2026-08-17: **acht Sekunden Erklärung waren zu viel.**

`07c-diktat-ende-hinweis.ogg` dauert **8,1 s** und liegt damit genau an dieser
Grenze.

**Entschieden am 2026-08-19: Der Wortlaut bleibt** (Stephan, nachdem er alle
vier Varianten gehört hat). Nicht gegen die Regel, sondern weil die Regel hier
nicht greift - und das ist der Unterschied, den die Regel selbst nicht
festhielt:

- Sie stammt aus der **Desktop-Umschaltung**. Dort wartet der Nutzer darauf,
  weitermachen zu können; jede Sekunde Ansage steht ihm im Weg.
- Nach einem **beendeten Diktat** wartet nichts. Der Nutzer hat gerade
  abgeschlossen und hat keinen nächsten Befehl in der Warteschlange.

Dazu kommt: Der Hinweis richtet sich an den, der den Vorlese-Befehl **nicht**
kennt. Für ihn sind die zwei Sekunden Höflichkeit der Unterschied zwischen
einem Satz, den er versteht, und einem Stichwort, das er sich merken müsste.
Und „das System soll persönlich klingen" ist Stephans Vorgabe vom selben Tag.

Die gemessenen Kürzungen bleiben trotzdem hier stehen - falls sich die
Einschätzung im Alltag ändert, muss niemand neu messen:

| Wortlaut | Dauer |
|---|---|
| „Diktat beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel vorgelesen haben, dann sage: Einkaufszettel vorlesen." | 8,05 s |
| „Diktat beendet, 3 Einträge geschrieben. Zum Vorlesen sage: Einkaufszettel vorlesen." | 6,07 s |
| „3 Einträge geschrieben. Zum Vorlesen sage: Einkaufszettel vorlesen." | 4,94 s |
| „Diktat beendet, 3 Einträge geschrieben." (ohne Hinweis) | 2,88 s |

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
