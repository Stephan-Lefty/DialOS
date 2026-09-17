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

| Beitrag | Datum | Länge |
|---|---|---|
| [315 – Von drei auf 26 Sätze](https://dialos.org/von-drei-auf-26-saetze/) | 2026-09-17 | 1:43 |
