[Deutsch](diktat.md) | [English](diktat.en.md)

# Diktat: Sprache zu Text

Messungen und Entscheidungen zum freien Diktat. Begonnen am 2026-08-18.
Das Diktat ist keine Anwendung, sondern die Voraussetzung für vier davon -
Briefe, Notizen, Mail und Chat kann der Nutzer ohne es gar nicht erzeugen
(siehe [anwendungen.md](anwendungen.md)).

Nicht zu verwechseln mit der Befehlserkennung: Das sind zwei Betriebsarten
desselben Werkzeugs. Die Befehlserkennung arbeitet mit einer
**eingeschränkten Grammatik** aus wenigen festen Sätzen, das Diktat mit
**freier Erkennung**. Warum die Grammatik dort Pflicht ist, steht in
[sprachsteuerung.md](sprachsteuerung.md).

## Das Modell: gemessen, nicht geschätzt

Beide Modelle liegen auf der Platte. Gemessen am 2026-08-18 mit vier
diktierten Sätzen (Brief, Einkaufszettel, Privatbrief, Termin), gesprochen
von Piper - das ist die bewährte Methode ohne Sprechen, siehe
`sprachsteuerung.md`.

| Modell | Ladezeit | Speicher | Rechenzeit je Sekunde Audio | Wortfehler |
|---|---|---|---|---|
| `vosk-model-de-small` (92 MB) | 0,4 s | 229 MB | 0,12 | 2 von 53 (3,8 %) |
| `vosk-model-de-big` (3,2 GB) | 11,6 s | **5468 MB** | 0,17 | **0 von 53 (0,0 %)** |

**Der Speicher ist kein Hindernis:** Der T490 hat 46 GB. Die 5,5 GB des
großen Modells fallen nicht auf. Rechenfaktor 0,17 heißt schneller als
Echtzeit, Live-Diktat ist also möglich.

**Was die Zahlen NICHT zeigen:** Das war Pipers synthetische Stimme, die
deutlich saubener ist als echte Sprache in einem Raum. Die 0,0 % sind die
Obergrenze, nicht der Alltagswert. Ein Test mit Stephans Stimme fehlt noch
und wird schlechter ausfallen.

**Folge für den Aufbau:** 11,6 s Ladezeit verbieten es, das große Modell
erst beim Befehl „Diktat starten" zu laden - 11 Sekunden Stille wären für
einen blinden Nutzer ein Defekt. Entweder wird vorgeladen, oder die
Ansage kommt zuerst und deckt die Wartezeit ab.

## Das eigentliche Problem ist nicht die Erkennung

Vosk liefert **Wörter, keinen Text**:

```
sehr geehrte damen und herren hiermit kündige ich meinen vertrag zum nächsten möglichen termin
```

Kein Komma, kein Punkt, alles klein. Deutsch schreibt aber **alle
Substantive groß**. Für einen Einkaufszettel ist das belanglos, für einen
Brief an die Krankenkasse nicht.

**Hier war eine frühere Aussage in diesem Projekt zu optimistisch.** Am
Morgen des 2026-08-18 stand hier „freies Diktat braucht keine neue Technik,
nur Arbeit". Das gilt für die Erkennung. Für *lesbaren deutschen Text*
gilt es nicht.

### Drei Versuche, es ohne neue Technik zu lösen - alle bei etwa 90 %

| Verfahren | Ergebnis |
|---|---|
| Wortliste `/usr/share/dict/ngerman`, nur eindeutige Substantive groß | 48/53 = **90,6 %** |
| dieselbe Liste plus „nach Artikel/Präposition groß" | 49/53 = 92,5 % |
| `hunspell -d de_DE` statt Wortliste, plus dieselbe Regel | 48/53 = **90,6 %** |

Warum es dort stehen bleibt, und beide Fehlerarten sind lehrreich:

- **Die Wortliste ist lückenhaft bei Grundformen.** Sie enthält
  „Vertrages", „Vertrags" und „Vertragsabschluss", aber **nicht**
  „Vertrag". Ebenso fehlen „Butter", „Dank", „Wetter" groß, während
  „Termin" drin ist. Wer sie als Wahrheit über Groß- und Kleinschreibung
  benutzt, bekommt zufällige Ergebnisse.
- **hunspell ist vollständig, aber zu tolerant.** Es akzeptiert „vertrag"
  UND „Vertrag", „wetter" UND „Wetter" - beide sind gültige deutsche
  Formen (Verbform gegen Substantiv). Es kann die Frage also nicht
  entscheiden. Nützlich ist es trotzdem an einer Stelle: Es lehnt
  „einkaufszettel" ab und akzeptiert „Einkaufszettel", kennt also die
  Regeln für zusammengesetzte Substantive.
- **Die Heuristik „nach einem Artikel kommt ein Substantiv" ist falsch.**
  Nach „den" kann ein Adjektiv kommen. Sie erzeugte „Sehr Geehrte", „Den
  Einkaufszettel", „für Deinen Brief" - sie verschiebt die Fehler, statt
  sie zu beseitigen.

**Das Fazit ist eine Grenze, keine Zwischenlösung:** Die verbleibenden
10 % brauchen echtes Grammatikwissen, keine Regel. Bei 150 Wörtern sind
das rund 14 falsch geschriebene Wörter pro Brief.

### Was Debian dafür anbietet: nichts

Geprüft am 2026-08-18: `languagetool`, `python3-spacy` und
`libreoffice-languagetool` sind **nicht in den Quellen**. `python3-nltk`
ist verfügbar (3.9.1-2), löst diese Aufgabe für Deutsch aber nicht. Ein
Werkzeug dafür wäre also ein Fremdpaket - gegen die Linie des Projekts,
bei Debian-Paketen zu bleiben, und deshalb eine eigene Entscheidung und
kein Nebenschritt.

## Vorschlag: nach Verwendungszweck trennen

Nicht ein Diktat für alles, sondern die Anforderung dort stellen, wo sie
zählt:

| Zweck | Anspruch | Stand |
|---|---|---|
| **Notizen, Einkaufszettel** | Kleinschreibung ist belanglos | sofort baubar |
| **Mail, Chat** | Kleinschreibung ist in privater Nachricht üblich; DialOS liest den Text ohnehin vor dem Senden vor | sofort baubar |
| **Briefe** | 10 % Fehler sind nicht zumutbar | braucht eine eigene Entscheidung |

Für Briefe gibt es zwei ehrliche Wege, und beide sind bewusst nicht
heimlich gewählt: LanguageTool als Fremdpaket nachziehen, oder den Brief
vor dem Absenden von einem sehenden Helfer prüfen lassen - die
Fernwartung dafür ist ohnehin Teil des Systems
([sicherheit-datenschutz.md](sicherheit-datenschutz.md)).

## Satzzeichen

Ungelöst und noch nicht gemessen. Der klassische Weg sind gesprochene
Satzzeichen („Komma", „Punkt", „Absatz"), die der Nutzer lernen muss. Zu
prüfen ist, ob sie sich zuverlässig von gleichlautenden Wörtern im Text
trennen lassen - „Punkt" kann auch ein Wort im Satz sein.
