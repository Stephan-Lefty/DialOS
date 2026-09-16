[English](pruefstand.en.md) | [Diktat](diktat.md) | [Sprachbefehle](sprachbefehle.md) | [Änderungsprotokoll](../README.md#änderungsprotokoll)

# Prüfstand - Messungen vom 2026-09-15

*Stand: Abend des 2026-09-15. Weiter am Mittwoch, 2026-09-17.*

Stephan am 2026-09-15: „Wir müssen ein System hinbekommen, was sauber die
Befehle umsetzt und auf der anderen Seite auch einen Text in deutscher Sprache
sauber zu Papier bringt. Nur dann ist DialOS eine Lösung, mit der wir etwas
bewegen können." Und am Abend: „Werte alles aus und dokumentiere es genau."

Dieses Dokument fasst den ganzen Tag zusammen: wie gemessen wurde, was
herauskam, welche Fehler die Messungen gefunden haben, was entschieden ist und
was am Mittwoch als Nächstes kommt. Einzelheiten zu Diktat und Befehlen
stehen zusätzlich in [diktat.md](diktat.md) und
[sprachbefehle.md](sprachbefehle.md).

---

## 1. Warum ein Prüfstand

Bis zum Mittag wurde jede Verbesserung am Diktat an **einem** Versuch
beurteilt - meist mit Piper, das sauberer spricht als jeder Mensch. Dabei
wurde mehrfach „repariert", was sich beim nächsten echten Versuch als falsch
oder unvollständig herausstellte. Der Prüfstand dreht das um: **echte
Aufnahmen** werden durch das **echte Programm** gespielt, und nach jeder
Änderung laufen dieselben Aufnahmen erneut.

**Datenschutz:** Alle Aufnahmen liegen auf der externen Platte unter
`erkenner-vergleich/pruefstand/`, **nie im Repo**. Stephans Zustimmung vom
2026-09-15 („Ja, einverstanden, bau den Prüfstand") gilt für seine eigene
Stimme; für andere Sprecher braucht es eine eigene Zustimmung.

## 2. Aufbau

| Teil | Wo | Was |
|---|---|---|
| Diktat-Mitschnitt | `dialos-diktat.py`, Schalter `~/.config/dialos/pruefstand` | genau der Ton, den die Erkenner bekamen (Blöcke in Reihenfolge, kurze Blöcke und Epochen vermerkt), dazu Protokollausschnitt, Ergebnis, Mikrofon |
| Befehls-Mitschnitt | `dialos-sprachbefehl-desktop.py`, Schalter `~/.config/dialos/pruefstand-befehle` | jede Äußerung mit mehr als `[unk]`: Ton seit dem vorigen Ergebnis, Zustand an/aus, Pegelverlauf, Mikrofon - **nur für eine Messsitzung**, schließt Gespräch und Fernseher ein |
| Mikrofonwahl | `~/.config/dialos/diktat-mikrofon`, `~/.config/dialos/befehl-mikrofon` | Name einer Quelle; sonst gilt die Festlegung „eingebautes Mikrofon" |
| Parakeet-Test | `~/.config/dialos/parakeet-test` | Brief und Notizen mit Parakeet (Weg 3), Befehle weiter Vosk |
| Auswertung | `scripts/dialos-pruefstand.py` | `uebernehmen`, `pruefen --beide`, `befehle`, `befehle-beschriften`, `befehle-pruefen` |

**Gemessen wird beim Diktat:** Wortfehlerrate (Levenshtein über normalisierte
Wörter, Zahlen als Wörter), falsche Satzzeichen (an jedem Wort, das in
Referenz und Ergebnis steht, das Zeichen danach: `, . ? ! :`, Absatz, Zeile)
und ob dieselben Befehle ausgelöst wurden („Satz löschen", „Satz wiederholen",
Schluss).

**Gemessen wird bei Befehlen:** je Mitschnitt die Entscheidung des Dienstes
gegen das, was wirklich gesagt wurde - richtig, verpasst, als „zu laut"
verworfen, falsch ausgelöst, Nicht-Befehl richtig ignoriert. Verglichen wird
die **Wirkung** („Brief schreiben" und „Brief erstellen" sind dasselbe).

## 3. Diktat: Erkenner und Mikrofone

### 3.1 Vormittag: Erkenner-Vergleich (Messprogramm, vor dem Prüfstand)

| Aufnahme | Vosk | Parakeet | Whisper small | Whisper turbo |
|---|---|---|---|---|
| Einkaufszettel, 20 Waren (wörtlich richtig) | **16/20** | 11/20 | 13/20 | 13/20 |
| Brief-Absatz, sauber (Wortfehler) | 7,6 % | **3,0 %** | 18,2 % | 39,4 % |
| Brief-Absatz, gestört | 60,6 % | **37,9 %** | - | - |

Whisper schied aus (langsam, Halluzinationen). Parakeet kippte bei
Einzelwörtern ins Englische - **der Einkaufszettel bleibt bei Vosk.**

### 3.2 Parakeet im echten Diktat - mit und ohne gesprochene Satzzeichen

| Probe (Stephans Stimme) | Vosk | Parakeet |
|---|---|---|
| 14:32 - Brief **mit** „Komma setzen"/„Punkt setzen" | 9,9 % | 14,9 % (Befehlswort kam als „Sätzen") |
| 14:47 - Brief **natürlich** gesprochen (Weg 3) | 4,9 % | 6,2 % - aber **alle** Satzzeichen, Vosk **keine** |

Daraus **Weg 3** (Stephans Wahl): natürlich sprechen, Parakeet setzt Punkt und
Komma selbst, gesprochen werden nur „neuer Absatz" und „neue Zeile".

### 3.3 Prüfstand: vier Aufnahmen desselben Briefs (Stand 16:49)

Derselbe Brief (71 Wörter, 11 Satzzeichen und Absätze), natürlich gesprochen,
je ein Mitschnitt, alle mit demselben Programmstand wiederholt:

| Mikrofon | ruhig: Vosk | ruhig: Parakeet | Fernseher: Vosk | Fernseher: Parakeet |
|---|---|---|---|---|
| eingebaut (Echo-Unterdrückung) | 12,7 % / 5 von 11 Zeichen falsch | **2,8 % / 0 von 11** | 16,9 % / 6 von 11 | 9,9 % / 0 von 11 |
| TONOR TC30 (USB-Tischmikrofon) | 8,5 % / 5 von 11 | 4,2 % / 0 von 11 | 8,5 % / 5 von 11 | **4,2 % / 0 von 11** |

Befehle („Diktat beenden") in allen acht Läufen wie aufgenommen.

**Befunde:**
1. **Parakeet ist in jeder Lage besser** und setzt alle Satzzeichen richtig.
2. **Das Tischmikrofon hält die Qualität bei Fernseher, das eingebaute nicht**
   (2,8 % → 9,9 %). Ohne Störung liegen beide Mikrofone gleichauf - der
   Unterschied zwischen 2,8 und 4,2 % sind eineinhalb Wörter.
3. Am Gerät nahm mit dem TONOR der Schluss-Erkenner „Diktat beenden" auch bei
   Fernseher selbst an; am eingebauten Mikrofon nur die Rückfallebene.

## 4. Befehle: Messsitzung 17:28-17:52

15 vorgegebene Befehle (Uhrzeit, Datum, Bildschirmfoto, Vorlesen, PDF, Brief
erstellen/drucken mit Rückfrage, Optik, Stoppen/Starten) plus zwei Sätze, die
kein Befehl sind - vier Durchgänge. 90 Mitschnitte: 67 aus Ablauf und Protokoll
beschriftet (Listenbefehl genau erkannt und ausgeführt), 10 von Stephan, 13
offen gelassen.

| Durchgang | Befehlsversuche | richtig | verpasst | „zu laut" verworfen | falsch ausgelöst |
|---|---|---|---|---|---|
| eingebaut, ruhig | 21 | 18 | 3 | 0 | 0 |
| eingebaut, Fernseher | 18 | 17 | 1 | 0 | 0 |
| TONOR, ruhig | 17 | 16 | 1 | 0 | 0 |
| TONOR, Fernseher | 19 | 18 | 0 | 1 | 0 |

**Befunde:**
1. **Kein ausgeführter Fehlauslöser** unter den beschrifteten Mitschnitten.
   (Um 17:29 schaltete ein Wortsalat auf Windows um - als Stephan die Liste noch
   vorlas; dieser Mitschnitt ist nicht beschriftet und fehlt in der Tabelle.)
2. **Die Verpasser sind fast alle verschluckte Anfänge:** „tag haben wir",
   „datum haben wir", „haben sprachsteuerung stoppen". Stephan: „Zwischen der
   Ansage von Anna und meiner Antwort muss ich immer so 1,5 Sekunden warten.
   Sonst wird das erste Wort verschluckt!" Im vierten Durchgang wartete er
   bewusst eine Sekunde - dort fehlte kein Anfang. **Der Mikrofon-Vergleich bei
   Befehlen ist deshalb zugunsten des TONOR verzerrt.**
3. **Der Fernseher störte die Befehle kaum** - die feste Satzliste ist robust,
   anders als freier Text.
4. **Annas Stimme erreicht über das TONOR den Befehlsdienst** (keine
   Echo-Unterdrückung): „speichern" nach „Das Bildschirmfoto ist gespeichert",
   „löschen", „notiz". Ausgelöst hat es nichts.
5. **Das TONOR ist bei 100 % Verstärkung übersteuert:** jede Äußerung erreichte
   den Höchstwert 32768.
6. **Grenze des Befehls-Prüfstands:** Bei 10 von 90 Mitschnitten erkannte ein
   frischer Erkenner etwas anderes als der Dienst live (z. B. live „wie ist die
   uhrzeit", neu „es tag") - der gespeicherte Ausschnitt reicht bis zum vorigen
   Ergebnis, der laufende Erkenner hatte mehr Zusammenhang. Die Tabelle zählt
   deshalb die **Live-Entscheidungen**. Verbesserung für Mittwoch: in der
   Messsitzung die ganze Sitzung durchgehend aufnehmen, dann lässt sich der
   Dienst Block für Block nachspielen.

**Offen gelassene Mitschnitte (13)**, zum Beschriften am Mittwoch:
172849 „starten" (aus), 172856 „tag haben wir", 172904 „uhrzeit", 172910 der
Windows-Wortsalat, 173102 „vorlesen", 173254 „notiz speichern ist", 173427
„stoppen", 173706 „haben wir", 174242 „starten" (aus, vor Durchgang 3), 174516
„notiz", 174534 „[unk] ist es", 174548 „datum haben wir", 174752 „starten".

**Aus den Protokollen der letzten Wochen** (`dialos-pruefstand.py befehle`):
Die häufigsten „Das war kein Befehl" sind abgeschnittene Fragen - „haben wir"
(5x), „ist es" (3x), „wie viel" (2x). Das passt zu Befund 2.

## 5. Vom Prüfstand gefundene und behobene Fehler

| Gefunden | Fehler | Behoben |
|---|---|---|
| erste echte Aufnahme | Mitschnitt prüfte einen Ordner, den erst der erste Mitschnitt anlegt - Stephans erste Aufnahme ging verloren | Messordner prüfen, Warnung im Protokoll |
| TONOR-Brief 15:24 | **Diktat hing:** feste Stille-Schwelle 150, TONOR rauscht bei 220-330 - „Diktat beenden" nie angenommen, Zeitgrenze lief nie ab | Schwellen nach Rauschboden (5-%-Quantil der letzten 30 s, 2,5-fach, nie unter den alten Werten); vorher 9,9 % und kein Schluss, danach 4,2 % |
| TONOR-Brief | Vosk teilte „neue Zeile" in der Mitte, im Brief „neue Zeil Zeile" | „zeil" gilt mit, Rest am Stückanfang fällt weg |
| Fernseher-Brief | **„Neuer Absatz" als eigenes Stück fiel bei Parakeet weg** | Stück aus nur einem Umbruch gilt nicht als leer |
| Wiederholung | **die erste Reparatur dafür ließ das Diktat abstürzen** (leerer Text) | abgesichert, bevor es aufs Gerät kam |
| Fernseher-Brief | „Mit freundlichen Grüßen." mit Punkt vor dem Namen | kurze Zeile vor Zeilenwechsel ohne Punkt |
| Brief 14:48 | echtes „Diktat beenden" als „danach nicht still" verworfen (Nachhall 131-166) | Befehlsruhe-Schwelle 400 |
| Brief 14:33 | „Okay" (Vosk: „ekd" für „Diktat") am Briefende | Schlussrest nach Wort-**Ende** abschneiden |

## 6. Stand der Entscheidungen

- **Text (Brief, Notizen): Parakeet, Weg 3** - entschieden, fest eingebaut wird
  nach zwei Proben (frei formulierter Brief; Fernseher ist erledigt). Beim
  festen Einbau: Modell (465 MB) und sherpa-onnx für alle Konten nach
  `/usr/local`, Paketierung, Lizenz (CC-BY-4.0, NVIDIA nennen).
- **Befehle und Einkaufszettel: Vosk.**
- **Mikrofon:** Festlegung vom 2026-08-17 („immer eingebaut") gilt weiter. Die
  Messungen sprechen bei Nebengeräuschen klar für ein Mikrofon nah am Mund -
  für draußen ein Headset. **Stephans Grundsatzfrage** („ob die Sprachsteuerung
  … nur dann funktioniert, wenn Nebengeräusche nicht vorhanden sind. Damit ist
  das System auch für draußen ungeeignet.") ist damit beantwortbar, aber noch
  nicht entschieden.

## 7. Zustand des Geräts am Abend (Admin-Konto)

| Schalter | Zustand | Wirkung |
|---|---|---|
| `parakeet-test` | an | Brief und Notizen mit Parakeet |
| `pruefstand` | an | jedes Diktat wird mitgeschnitten |
| `pruefstand-befehle` | **aus** | Befehls-Mitschnitt nach der Sitzung entfernt |
| `diktat-mikrofon` | aus | Diktat über das eingebaute Mikrofon |
| `befehl-mikrofon` | **entfernt am Abend** | ab der nächsten Anmeldung hört die Sprachsteuerung wieder über das eingebaute Mikrofon (bis dahin noch TONOR) |

Das Nutzerkonto ist von allen Schaltern unberührt: Vosk, eingebautes Mikrofon,
kein Mitschnitt.

## 8. Reihenfolge für Mittwoch

**Stand 2026-09-16:** Punkt 1 und 2 gebaut, nachgebildet und aufgespielt - vorher
4 von 8 Fragen nach einer Ansage angekommen, nachher 8 von 8 (auch mit Ansage im
rohen Mikrofon). Probe mit Stephans Stimme steht aus (wirkt nach Ab- und
Anmelden).

1. **Lücke nach Annas Ansage schließen** (Befehlsdienst): Aufnahme während der
   Ansage offen lassen und verwerfen, ab ihrem Ende mit 0,3 s Vorlauf auswerten
   - wie beim Diktat seit dem 14.09. Beim rohen TONOR darauf achten, dass Annas
   eigene Worte nichts auslösen.
2. **Optik-Regel** („umschalten" plus Ziel irgendwo) an die Grenze von zwei
   Zusatzwörtern binden.
3. **TONOR-Verstärkung senken** (100 % übersteuert) und neu messen.
4. **Befehls-Messsitzung wiederholen** - ohne bewusstes Warten, mit
   durchgehender Aufnahme (siehe 4, Befund 6); die 13 offenen Mitschnitte
   beschriften.
5. **Parakeet-Probe mit frei formuliertem Brief**, danach Entscheidung über den
   festen Einbau.
6. **Geräusch-Simulation:** Straßen-, Wind- und Cafégeräusche in die
   vorhandenen Aufnahmen mischen - ab welchem Lärm kippt was, je Mikrofon und
   Erkenner.
