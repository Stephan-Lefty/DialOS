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
- **Bei Aufzählungen früher aufhören.** Anna spricht sie hörbar langsamer:
  Am 2026-09-21 lag eine Fassung mit „Erstens, Zweitens, Drittens" bei 126
  Wörtern pro Minute, eine gleich lange ohne bei 133 – sechs Sekunden
  Unterschied bei nahezu gleicher Wortzahl. Wer gliedert, rechnet mit rund
  250 Wörtern statt 270. Die Meldung des Skripts, wie viele Wörter zu
  streichen sind, rechnet mit dem Durchschnitt und greift dann zu kurz.
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
# 2. Sprechen lassen (Piper + Annas Modell nötig, siehe unten)
./dialos-hoerfassung-sprechen.py sprechfassungen/315-von-drei-auf-26-saetze.txt
# 3. ANHÖREN. Erst danach:
./dialos-hoerfassung-hochladen.py 315 sprechfassungen/315-von-drei-auf-26-saetze.mp3
```

### Wo Piper und Annas Stimme liegen (Stand 2026-09-21)

Der Vorgabepfad im Skriptkopf – `/usr/local/share/dialos-piper/voices/` – ist
der Pfad **auf dem Zielgerät**, nicht auf dem Arbeitsrechner. Dort liegt die
Stimme, weil DialOS selbst sie zum Sprechen braucht.

Auf dem Arbeitsrechner ist beides am 2026-09-21 neu eingerichtet worden,
nutzerlokal und damit unabhängig von einer Systeminstallation:

```
~/.local/share/dialos-piper/venv/      piper-tts in eigener Umgebung
~/.local/share/dialos-piper/voices/    de_DE-kerstin-low.onnx (61 MB) + .onnx.json
```

Der Aufruf braucht deshalb zwei Umgebungsvariablen:

```bash
ANNA_MODELL="$HOME/.local/share/dialos-piper/voices/de_DE-kerstin-low.onnx" \
ANNA_PYTHON="$HOME/.local/share/dialos-piper/venv/bin/python" \
./dialos-hoerfassung-sprechen.py sprechfassungen/<datei>.txt
```

**Warum das hier steht:** Am 2026-09-21 war von der Einrichtung des
Vertonungstags nichts mehr übrig – weder das `piper`-Modul noch die Stimme,
und zwar nirgendwo auf der Platte. Vermutlich hat eine Neuinstallation sie
mitgenommen; genau davor warnt CLAUDE.md für die interne Platte. Gekostet hat
das eine halbe Stunde Suche, weil die Anleitung nur auf den Skriptkopf verwies
und der auf den Gerätepfad zeigt. Wer die Einrichtung erneuern muss:
`pip install piper-tts` in ein venv, Modell und `.onnx.json` von
`huggingface.co/rhasspy/piper-voices` (`de/de_DE/kerstin/low/`).

Der dritte Schritt lädt die Datei in die Mediathek und setzt den Audio-Block
direkt hinter den Sprachmarker im Beitrag. **Die Vertonung läuft bewusst nicht
automatisch mit der Blog-Routine** – sonst steht irgendwann eine Datei auf der
Seite, die niemand gehört hat.

Die MP3-Dateien selbst liegen nicht im Repo. Sie sind erzeugt, nicht
geschrieben, und ihr Zuhause ist die Mediathek von dialos.org.

## Bisher vertont

Alle zwanzig deutschen Beiträge, Stand 2026-09-22. Die englischen bewusst nicht:
Anna ist eine deutsche Stimme, und eine englische Hörfassung bräuchte eine eigene.

**Die Lücke schließt sich nicht von selbst.** Am 2026-09-21 fehlten zwei
Hörfassungen, weil die Beiträge nach dem Vertonungstag entstanden waren – und
aufgefallen ist das nur zufällig beim Durchsehen. Das ist die Kehrseite davon,
dass die Vertonung bewusst nicht mit der Blog-Routine mitläuft. Wer hier
ergänzt, vergleicht die Tabelle am besten gleich mit allen veröffentlichten
deutschen Beiträgen.

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
| [Der Prüfstand: Messen statt glauben](https://dialos.org/der-pruefstand-messen-statt-glauben/) | 2026-09-19 | 1:58 |
| [Tag 41 bis 47: Schreiben und wiederfinden](https://dialos.org/dialos-tag-41-bis-47-schreiben-und-wiederfinden/) | 2026-09-21 | 1:58 |
| [Ein Text zum Lesen ist kein Text zum Hören](https://dialos.org/ein-text-zum-lesen-ist-kein-text-zum-hoeren/) | 2026-09-22 | 1:51 |
| [Ein Server in Innsbruck](https://dialos.org/ein-server-in-innsbruck/) | 2026-09-24 | 1:49 |

### Was beim Kürzen der Chronik-Folgen zu beachten war

Die sechs Chronik-Beiträge sind zwischen 900 und 2000 Wörter lang. Auf 250
einzudampfen ist keine Kürzung, sondern eine Auswahl: Der Beitrag belegt seine
Aussagen mit Zahlen, Daten und Versionsnummern, die Hörfassung braucht den
Gedanken. Bewährt hat sich, zwei oder drei Episoden herauszugreifen und den
Rest wegzulassen, statt alles anzureißen.

Umschrieben wurde außerdem, was ohne Bild oder Rücksprung nicht trägt:
Screenreader wurde zu "ein ausgereifter Vorleser für den Bildschirm", der
Zugänglichkeits-Standard zu "ein fester Standard für Zugänglichkeit", die
DIN 5008 zu "die übliche Norm", Tastenkombinationen fielen ganz weg.
