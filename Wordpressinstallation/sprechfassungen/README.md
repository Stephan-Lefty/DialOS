# Sprechfassungen

Hier liegen die Texte, aus denen die Hörfassungen der deutschen Neuigkeiten
entstehen – gesprochen von **Anna** (`de_DE-kerstin-low`), derselben Stimme,
die auf dem Gerät spricht.

## Warum eigene Texte und nicht der Beitrag selbst

Ein Text zum Lesen und ein Text zum Hören sind nicht derselbe Text. Der
Blogbeitrag belegt seine Aussagen mit Zahlen, Beispielen und Verweisen, weil
man beim Lesen zurückspringen kann. Beim Hören geht das nicht.

Der erste Versuch am 2026-09-17 war der vorgelesene Beitrag – 2:23 Minuten,
Stephans Urteil: zu technisch, zu lang. Seitdem wird die Sprechfassung von
Hand geschrieben: kürzer, ohne Fachbegriffe, mit dem Gedanken statt mit allen
Belegen.

**Für wen das gedacht ist:** nicht für blinde Menschen. Die haben einen
Screenreader, der jede Seite in ihrer Stimme und ihrem Tempo vorliest – und
das deutlich schneller als Anna. Die Hörfassung ist eine **Hörprobe des
Systems**: Wer überlegt, ob DialOS etwas für ihn oder einen Angehörigen ist,
hört hier zum ersten Mal, wie sein künftiger Computer klingen wird. Deshalb
auch die Beschriftung „gesprochen von Anna, der Stimme von DialOS" und nicht
„Version für Blinde".

## Regeln für eine Sprechfassung

- **Höchstens zwei Minuten** (Stephans Vorgabe, 2026-09-17). Bei rund
  140 Wörtern pro Minute sind das etwa 270 Wörter.
- **Keine Ziffern.** Anna schreibt Zahlen zwar aus, hetzt sie aber – gemessen
  am 2026-09-17 ist „26" 22 % kürzer als „sechsundzwanzig". Also „über zwei
  Dutzend" schreiben statt „26".
- **Keine Fachbegriffe.** Vosk, Piper, Commit, ISO haben in einer Hörfassung
  nichts verloren.
- **Was Anna schlecht ausspricht, umgehen statt reparieren.** „Grammatik" hat
  die richtige Länge, aber die falsche Betonung – ein Viersilber mit Betonung
  hinten ist genau das, woran ein `low`-Modell scheitert. „Satzbau" sagt
  dasselbe und klingt richtig.
- **Aufzählungen ansagen** („Regel eins", „Regel zwei"). Beim Lesen trägt der
  Absatz diese Information, beim Hören nicht.
- **Begriffe im selben Atemzug erklären.** Wer „Wachstum" sagt, muss gleich
  danach sagen, worin es besteht – zurückspringen geht nicht.

Das Skript meldet Ziffern und bekannte Problemwörter von selbst, ersetzt aber
nichts automatisch: Was an die Stelle gehört, entscheidet der Sinn des Satzes.

## Ablauf

```bash
# 1. Sprechfassung schreiben: sprechfassungen/<beitrags-id>-<slug>.txt
# 2. Sprechen lassen (Piper + Annas Modell nötig, siehe Skriptkopf)
./dialos-hoerfassung-sprechen.py sprechfassungen/315-von-drei-auf-26-saetze.txt
# 3. ANHÖREN. Erst danach:
./dialos-hoerfassung-hochladen.py 315 sprechfassungen/315-von-drei-auf-26-saetze.mp3
```

Der dritte Schritt lädt die Datei in die Mediathek und setzt den Audio-Block
direkt hinter den Sprachmarker im Beitrag. **Die Vertonung läuft bewusst nicht
automatisch mit der Blog-Routine** – sonst steht irgendwann eine Datei auf der
Seite, die niemand gehört hat.

Die MP3-Dateien selbst liegen nicht im Repo. Sie sind erzeugt, nicht
geschrieben, und ihr Zuhause ist die Mediathek von dialos.org.

## Bisher vertont

Alle siebzehn deutschen Beiträge, Stand 2026-09-17. Die englischen bewusst nicht:
Anna ist eine deutsche Stimme, und eine englische Hörfassung bräuchte eine eigene.

| Beitrag | Datum | Länge |
|---|---|---|
| [Dreizehn Tage](https://dialos.org/dialos-dreizehn-tage/) | 2026-08-19 | 1:59 |
| [DialOS Mobil sucht Testerinnen und Tester](https://dialos.org/dialos-mobil-tester-gesucht/) | 2026-08-20 | 1:37 |
| [Wer ist eigentlich Claude?](https://dialos.org/wer-ist-claude/) | 2026-08-23 | 1:51 |
| [Tag 14 bis 19: Was niemand bestätigt hatte](https://dialos.org/dialos-tag-14-bis-19-was-niemand-bestaetigt-hatte/) | 2026-08-24 | 1:59 |
| [Wie hört und spricht DialOS eigentlich?](https://dialos.org/sprachsteuerung-erklaert/) | 2026-08-25 | 1:48 |
| [Das schweigende Missverständnis](https://dialos.org/das-schweigende-missverstaendnis/) | 2026-08-27 | 1:58 |
| [Tag 20 bis 26: Die englische Hälfte](https://dialos.org/dialos-tag-20-bis-26-die-englische-haelfte/) | 2026-08-31 | 1:59 |
| [Warum Linux und nicht Windows?](https://dialos.org/warum-linux-debian-gnome/) | 2026-09-01 | 1:43 |
| [Warum zwei Stimmen?](https://dialos.org/warum-zwei-stimmen/) | 2026-09-05 | 1:24 |
| [DialOS Mobil: Zwei Rückmeldungen, fünf Fehler](https://dialos.org/dialos-mobil-zwei-rueckmeldungen-fuenf-fehler/) | 2026-09-05 | 1:57 |
| [DialOS Mobil: Die App, die sich selbst taub machte](https://dialos.org/dialos-mobil-die-app-die-sich-selbst-taub-machte/) | 2026-09-06 | 1:56 |
| [Tag 27 bis 33: Die Woche, in der es um Geld ging](https://dialos.org/dialos-tag-27-bis-33-die-woche-in-der-es-um-geld-ging/) | 2026-09-07 | 1:54 |
| [69 Ansagen, zwei versteckte Fehler](https://dialos.org/69-ansagen-zwei-versteckte-fehler/) | 2026-09-08 | 1:48 |
| [DialOS Mobil: Ein Knopf, so breit wie der Bildschirm](https://dialos.org/dialos-mobil-ein-knopf-so-breit-wie-der-bildschirm/) | 2026-09-09 | 1:53 |
| [Der Brief, der nur durch Sprechen entsteht](https://dialos.org/der-brief-der-nur-durch-sprechen-entsteht/) | 2026-09-11 | 1:53 |
| [Tag 34 bis 40: Als die Landkarte wieder zum Gebiet passte](https://dialos.org/dialos-tag-34-bis-40-als-die-landkarte-wieder-zum-gebiet-passte/) | 2026-09-14 | 1:57 |
| [Von drei auf 26 Sätze](https://dialos.org/von-drei-auf-26-saetze/) | 2026-09-16 | 1:43 |

### Was beim Kürzen der Chronik-Folgen zu beachten war

Die fünf Chronik-Beiträge sind zwischen 900 und 2000 Wörter lang. Auf 250
einzudampfen ist keine Kürzung, sondern eine Auswahl: Der Beitrag belegt seine
Aussagen mit Zahlen, Daten und Versionsnummern, die Hörfassung braucht den
Gedanken. Bewährt hat sich, zwei oder drei Episoden herauszugreifen und den
Rest wegzulassen, statt alles anzureißen.

Umschrieben wurde außerdem, was ohne Bild oder Rücksprung nicht trägt:
Screenreader wurde zu "ein ausgereifter Vorleser für den Bildschirm", der
Zugänglichkeits-Standard zu "ein fester Standard für Zugänglichkeit", die
DIN 5008 zu "die übliche Norm", Tastenkombinationen fielen ganz weg.
