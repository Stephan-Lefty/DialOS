[Deutsch](lizenzen.md) | [English](lizenzen.en.md) | [Änderungsprotokoll](../README.md#änderungsprotokoll)

# Lizenzen und Herkunft

Wer ein Betriebssystem weitergibt, gibt tausend fremde Programme mit
weiter. Dieses Dokument sagt, was von wem stammt, unter welcher Lizenz es
steht und welche Pflichten daraus folgen - für Kunden, für
Wiederverkäufer und für jeden, der DialOS weiterentwickeln will.

## Der Grundsatz

**Die DialOS-Lizenz gilt nur für das, was in diesem Repository steht** -
die Skripte, die Konfigurationsdateien, die Doku. Debian, GNOME und alle
mitgelieferten Programme behalten ihre eigenen Lizenzen; daran ändert
DialOS nichts und kann es auch nicht.

Rechtlich ist eine Distribution eine **Sammlung**. Die GPL nennt das
„mere aggregation" (GPLv3 § 5, GPLv2 § 2 letzter Absatz) und stellt
ausdrücklich klar, dass Programme, die nur auf demselben Datenträger
liegen, sich nicht gegenseitig ihre Lizenz aufzwingen.

## DialOS selbst

**GNU General Public License, Version 3** (siehe [LICENSE](../LICENSE)).

Das ist eine bewusste Entscheidung für Copyleft: Wer eine geänderte
Fassung von DialOS **weitergibt**, muss deren Quelltext ebenfalls unter
GPL-3.0 offenlegen. DialOS ist für Menschen gebaut, die auf Hilfe
angewiesen sind - was daraus entsteht, soll ihnen offen zur Verfügung
stehen und nicht in einem geschlossenen Produkt verschwinden.

Copyleft greift beim **Weitergeben**, nicht beim Benutzen: Wer DialOS für
sich umbaut und nicht verteilt, muss nichts veröffentlichen.

### Ausgenommen: Name und Erscheinungsbild

Nicht unter der GPL stehen **Wortmarke und Erscheinungsbild**: der Name
„DialOS", das Logo, das App-Symbol und die Hintergrundbilder in
[assets/](../assets/).

Das ist kein Widerspruch zur freien Lizenz, sondern in Distributionen
üblich (Debian, Firefox und Ubuntu handhaben es genauso). Der Grund ist
praktisch: Wer DialOS umbaut, soll das dürfen - aber das Ergebnis nicht
weiterhin „DialOS" nennen. Sonst tragen fremde Änderungen Stephans Namen,
und Nutzer halten für DialOS, was keines ist. Für einen abgeleiteten
Aufbau also bitte einen eigenen Namen und ein eigenes Logo verwenden.

## Debian und GNOME

DialOS setzt auf **Debian 13** mit **GNOME 48** auf. Beide sind
Zusammenstellungen aus vielen Lizenzen - GPL-2, GPL-3, LGPL, MIT, BSD,
Apache und weitere.

**Nachweis auf dem Gerät:** Debian legt zu jedem installierten Paket die
Lizenz unter `/usr/share/doc/PAKET/copyright` ab. Dieses Verzeichnis
liefert die Nachweise mit und **darf beim Aufräumen nicht entfernt
werden**.

**Quelltext-Pflicht.** Wer GPL-Software weitergibt - auch auf einem
verkauften Gerät -, schuldet dem Empfänger den zugehörigen Quelltext.
DialOS erfüllt das, indem es die Pakete **unverändert** aus Debians
Quellen installiert: Der Quelltext liegt öffentlich bei Debian
(`deb-src`-Quellen, https://sources.debian.org). Wird ein Paket
**geändert**, muss der geänderte Quelltext selbst bereitgestellt werden -
das ist einer der Gründe, warum DialOS eigene Skripte danebenlegt,
statt fremde Pakete zu patchen.

**Marken.** „Debian" ist eine Marke von Software in the Public Interest,
„GNOME" eine Marke der GNOME Foundation. Die Aussage „basiert auf
Debian 13" ist beschreibender Gebrauch und ausdrücklich erlaubt. Nicht
erlaubt ist es, DialOS so zu benennen oder darzustellen, als sei es ein
offizielles Debian- oder GNOME-Produkt.

Ebenso sind **Thunderbird** und **Firefox** Marken von Mozilla. DialOS
verändert diese Programme nicht, sondern konfiguriert sie nur (etwa die
Fußzeile in jeder Mail) - das berührt das Markenrecht nicht.

## Sprachausgabe und Spracherkennung

Der heikelste Teil, weil hier Modelle und Datensätze mitgeliefert werden
und **nicht** alle frei verwendbar sind. Stand der Prüfung: 2026-08-23.

| Bestandteil | Verwendung in DialOS | Lizenz |
|---|---|---|
| [Piper](https://github.com/rhasspy/piper) | Sprachausgabe | MIT |
| Stimme `de_DE-kerstin-low` („Anna") | Auslieferungsstimme | Datensatz **CC0**, Modellsammlung MIT |
| Stimme `de_DE-thorsten-high` („Michael") | zweite Stimme | Datensatz **CC0**, Modellsammlung MIT |
| [Vosk](https://alphacephei.com/vosk/) | Spracherkennung | Apache 2.0 |
| `vosk-model-small-de-0.15` | Befehlserkennung | Apache 2.0 |
| `vosk-model-de-0.21` | Diktat | Apache 2.0 |
| `vosk-model-de-tuda-0.6-900k` | Diktat (Alternative) | Apache 2.0 |

**CC0** heißt Gemeinfreiheit - keine Auflagen, auch nicht bei
kommerzieller Nutzung. **Apache 2.0** erlaubt kommerzielle Nutzung und
enthält zusätzlich eine ausdrückliche Patentlizenz. Alle hier
eingesetzten Modelle dürfen also mit verkauften Geräten ausgeliefert
werden.

Die Angaben stammen aus den Quellen selbst: den `MODEL_CARD`-Dateien
neben den `.onnx`-Dateien der Piper-Stimmen und der Modellübersicht unter
https://alphacephei.com/vosk/models.

### Absichtlich nicht verwendet

**Aufweckwort (openWakeWord, fertige Modelle): CC BY-NC-SA** - nicht
kommerziell. DialOS wird auf verkauften Geräten ausgeliefert, damit
scheidet es aus. Ein selbst trainiertes Modell wäre möglich (der Code und
Googles Einbettung stehen unter Apache 2.0), der fertige Modellsatz ist
es nicht. Deshalb verlangt das Einschalten der Sprachsteuerung bis auf
Weiteres zwei gesprochene Wörter statt eines Aufweckworts.

Das ist der Grund, warum es diese Seite gibt: Eine solche Klausel fällt
erst auf, wenn jemand nachliest.

## Ansagen und Sprachbeispiele

Die Dateien unter [docs/sprachbeispiele/](sprachbeispiele/) sind mit
Piper aus den oben genannten Stimmen erzeugt. Da beide Datensätze CC0
sind, unterliegen die erzeugten Audiodateien keinen Auflagen aus der
Stimme. Die **Texte** der Ansagen stammen aus DialOS und stehen wie der
übrige Inhalt dieses Repositories unter GPL-3.0.

## Für Wiederverkäufer und Kunden

Wer ein DialOS-Gerät weitergibt, gibt GPL-Software weiter und übernimmt
damit deren Pflichten. Praktisch heißt das:

1. `/usr/share/doc/` auf dem Gerät belassen - dort stehen alle
   Lizenztexte.
2. Auf Nachfrage den Quelltext benennen können: für Debian-Pakete
   https://sources.debian.org, für DialOS selbst
   https://github.com/Stephan-Lefty/DialOS.
3. Bei eigenen Änderungen an DialOS deren Quelltext offenlegen (GPL-3.0)
   und einen anderen Namen verwenden (siehe oben).

## Offen

- Vollständige Liste der Debian-Pakete, die DialOS zusätzlich
  installiert, mit ihren jeweiligen Lizenzen. Auf dem Gerät nachvollzieh-
  bar über `/usr/share/doc/`, im Repo bisher nicht zusammengestellt.
- Herkunft der Hintergrundbilder und des Logos schriftlich festhalten
  (Eigenerstellung oder Quelle), damit der Markenvorbehalt oben auch
  belegt ist.
