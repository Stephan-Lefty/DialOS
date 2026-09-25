[Deutsch](erweiterungen.md) | [English](erweiterungen.en.md)

# Erweiterungen

Wie ein Programm zu DialOS dazukommt, ohne dass am Kern etwas geändert
werden muss.

> **Stand am 2026-09-25: zwei Erweiterungen, dazu die Brücke zu Thunderbird.**
>
> - **DialOS-Suche** („Unterlagen durchsuchen") - seit 2026-09-18 gebaut und
>   am Gerät erprobt, im Postfach und in den Dokumenten (Einzelheiten im
>   Kasten darunter).
> - **DialOS-Mail** („Neue E-Mail schreiben", `dialos-mail-schreiben.py`) -
>   seit 2026-09-21 gebaut, am 2026-09-25 am Gerät vom Empfänger bis zum
>   Entwurf durchgelaufen. Siehe „Die zweite Erweiterung: DialOS-Mail" am Ende.
> - **Die DialOS-Brücke** ist die Schnittstelle zu Thunderbird, über die beide
>   Entwürfe ablegen, senden und Kontakte eintragen. Sie ist eine Erweiterung
>   *von Thunderbird*, keine von DialOS - siehe „Die Thunderbird-Brücke" am
>   Ende.
>
> Aufgaben in [TODO.md](../TODO.md), Einzelheiten im Änderungsprotokoll unter
> 0.5.2.
>
> **Früherer Stand am 2026-09-18: gebaut und am Gerät belegt.** Die Schnittstelle steht
> (Manifest, `dialos-erweiterung.py`, Startsatz in der Kern-Grammatik,
> Mikrofon-Übergabe mit Wache), und **DialOS-Suche läuft**: Index über Briefe,
> Notizen, Ablage und Thunderbird-Mails, Sprachdialog mit Eingrenzen bis zu einer
> Datei, dann vorlesen, drucken, auf eine Mail antworten oder sie weiterleiten -
> die Antwort wird diktiert und landet als Entwurf in Thunderbird, gesendet wird
> nie von selbst. Auf Papier und im Entwurfsordner von Stephan bestätigt.
> Einzelheiten im Änderungsprotokoll unter 0.5.2, Aufgaben in [TODO.md](../TODO.md).
>
> Der Text unten ist der Entwurf vom 2026-09-17 - er beschreibt das Warum und
> gilt unverändert; was daraus geworden ist, steht im Änderungsprotokoll.
>
> **Ursprünglicher Vermerk vom 2026-09-17: Die Schnittstelle ist ENTWURF, keine
> Zeile Code davon ist gebaut.** Diese Datei beschreibt, wie es werden soll, und steht
> bewusst getrennt von [sprachbefehle.md](sprachbefehle.md) und
> [anwendungen.md](anwendungen.md), die beschreiben, was ist. Die Trennung
> ist dieselbe wie dort: Vermischt sähe Geplantes wie Vorhandenes aus.
>
> **Die einzige Ausnahme ist das Symbol** - das ist gebaut und liegt als
> zwölf Dateien im Repo, siehe „Das Symbol" weiter unten. Es steht hier
> ausdrücklich, damit die Ausnahme nicht die Regel aufweicht.

Entschieden mit Stephan am 2026-09-17: DialOS bekommt eine
Erweiterungsschnittstelle, und die erste Erweiterung wird **DialOS-Suche**
(Briefe, Dokumente, Notizen und Mails per Sprache finden und vorlesen).
Die Reihenfolge ist Absicht - die Schnittstelle zuerst, und die erste
Erweiterung beweist dabei, dass sie trägt.

## Das Problem, das sie löst

Heute steht jeder Sprachbefehl an drei Stellen in
`dialos-sprachbefehl-desktop.py`: als Satz in `GRAMMATIK_AN`, als Eintrag
in einem Dict, und als Zweig in der Schleife. Für Diktat, Drucken und
Auskunft ist das dreimal dasselbe Muster mit anderen Namen.

Ein viertes Programm nach demselben Verfahren wäre die vierte Kopie, und
jede weitere macht den Kern länger, ohne ihn besser zu machen. Vor allem
aber: **Es gibt keinen Weg, ein Programm hinzuzufügen, ohne den Kern
anzufassen.** Wer ein Werkzeug beisteuern will, müsste eine Datei ändern,
an der auch das Ein- und Ausschalten der Sprachsteuerung hängt.

## Die Kernentscheidung: umschalten, nicht addieren

**Das ist die Stelle, an der ein naiver Plugin-Mechanismus scheitern
würde**, und sie ist kein Entwurfsgeschmack, sondern folgt aus einer
gemessenen Eigenschaft von Vosk.

Die eingeschränkte Grammatik ist eine Liste von SÄTZEN, aber Vosk baut
daraus ein WORTNETZ und darf Wörter aus verschiedenen Sätzen kombinieren.
Am 2026-08-22 standen bei **27 Sätzen** bereits **382 erlaubte
Wortkombinationen ohne Befehl** im Protokoll (siehe `TODO.md`, der Punkt
„Erlaubte Wortkombinationen ohne Befehl fallen LAUTLOS durch"). Für den
blinden Nutzer ist das der schlechteste Ausgang überhaupt: Er hat
gesprochen, das Gerät hat zugehört, und nichts sagt ihm, dass nichts
geschah.

**Die 382 sind nicht der heutige Stand, und das macht das Argument
stärker, nicht schwächer.** Zweierlei hat sich seither geändert: Die
Grammatik ist auf **47 Befehlssätze** gewachsen (49 Einträge mit Ein-
und Ausschalten), und seit dem 2026-08-24
schweigt DialOS nicht mehr, wenn nichts gepasst hat - es sagt es an und
schlägt bei starker Übereinstimmung den richtigen Satz vor. Der Punkt ist
damit **entschärft, aber nicht erledigt**: Die Zwei-Drittel-Schwelle wird
bei kurzen Befehlen nie erreicht, und die Gesprächs-Erkennung wartet noch
auf die Probe am Gerät.

Entscheidend ist die Richtung. Die Zahl der Kombinationen wächst **nicht
linear** mit der Satzzahl, und die Satzzahl hat sich in vier Wochen von 27
auf 47 fast verdoppelt - ohne dass eine einzige Erweiterung dabei war.
Würde jede Erweiterung ihre zwanzig Sätze in die Kern-Grammatik schütten,
wäre das Problem bei sechs Erweiterungen nicht sechsmal so groß, sondern
ein Vielfaches. Die Schnittstelle wäre dann der Mechanismus, der einen
gerade erst entschärften Fehler wieder aufreißt.

**Deshalb wächst die Kern-Grammatik pro Erweiterung um genau einen Satz:
ihren Startsatz.** Alles Weitere erkennt die Erweiterung selbst, mit
ihrer eigenen kleinen Grammatik, solange sie läuft - und der Kern hält
sich so lange heraus.

Das ist kein neues Verfahren, sondern das, was `dialos-diktat.py` heute
schon tut: eigener zweiter Erkenner, eigene Grammatik, Markierungsdatei,
und der Befehlsdienst schweigt derweil. Die Schnittstelle macht daraus
einen allgemeinen Mechanismus statt eines Sonderfalls.

| | Kern-Grammatik | Grammatik der Erweiterung |
|---|---|---|
| Wer baut sie | `dialos-sprachbefehl-desktop.py` aus allen Manifesten | die Erweiterung selbst |
| Was steht drin | je Erweiterung die `startsaetze` | die `eigene_grammatik` |
| Wann aktiv | immer, wenn die Sprachsteuerung an ist | nur, solange die Erweiterung läuft |
| Wächst mit der Zahl der Erweiterungen | ja, um einen Satz je Stück | nein |

## Das Manifest

Eine Datei je Erweiterung unter
`/usr/local/share/dialos/erweiterungen/<name>.json`:

```json
{
  "name": "DialOS-Suche",
  "version": "0.1.0",
  "braucht_dialos": "0.6.0",
  "startsaetze": ["unterlagen durchsuchen"],
  "befehl": "/usr/local/bin/dialos-suche.py",
  "eigene_grammatik": ["vorlesen", "weiter", "zurueck", "stopp", "abbrechen"],
  "braucht_mikrofon": true,
  "beschreibung": "Briefe, Dokumente, Notizen und Mails im Archiv finden"
}
```

| Feld | Wofür |
|---|---|
| `name` | Anzeigename. Nicht der Sprachbefehl - siehe unten. |
| `version` | Version der Erweiterung, für das Änderungsprotokoll. |
| `braucht_dialos` | Mindestversion des Kerns. Ohne sie bricht eine Erweiterung still, wenn der Kern sich ändert. |
| `startsaetze` | Kommen in die Kern-Grammatik. Jeder muss die Regeln aus [sprachbefehle.md](sprachbefehle.md) einhalten. |
| `befehl` | Was gestartet wird. Absoluter Pfad. |
| `eigene_grammatik` | Steht NICHT in der Kern-Grammatik. Nur da, damit sie beim Einbauen mitgeprüft werden kann. |
| `braucht_mikrofon` | Ob die Erweiterung das Mikrofon übernimmt. Entscheidet über die Übergabe. |
| `beschreibung` | Ein Satz, der auch vorgelesen werden kann. |

JSON und nicht TOML oder YAML, weil `GRAMMATIK_AN` heute schon ein
JSON-String ist und `json` zur Standardbibliothek gehört - eine
Abhängigkeit weniger auf einem Gerät, das offline laufen soll.

## Vier Regeln, die die Schnittstelle erzwingen muss

Jede stammt aus einem Fehler, der in diesem Projekt schon aufgetreten
ist. Das ist dieselbe Herkunft wie bei den Regeln in
[sprachbefehle.md](sprachbefehle.md), und sie sind aus demselben Grund
nicht verhandelbar.

### 1. Der Wortschatz wird beim Einbauen geprüft, nicht zur Laufzeit

Ein Wort, das das kleine Vosk-Modell nicht kennt, wirft Vosk **still**
aus der Grammatik. Der Befehl existiert dann nicht, und nirgends steht
etwas. Am 2026-08-18 ist das bei **„löschen"** aufgefallen, das im
Wortschatz fehlt; ebenfalls nicht enthalten sind „zurücksetzen",
„aufräumen" und „spät".

`dialos-erweiterung.py einbauen` prüft deshalb **jedes Wort aus beiden
Listen** gegen das Modell und **verweigert** die Installation. Nicht
warnen - verweigern. Eine Warnung beim Einbauen liest niemand wieder,
und der Fehler zeigt sich erst, wenn der Nutzer allein mit dem Gerät ist.

Vosk meldet den Fall beim Bauen der Grammatik selbst
(`Ignoring word missing in vocabulary`); die Prüfung braucht kein
Mikrofon und keine Stimme.

### 2. Kollisionen zwischen Erweiterungen werden ebenfalls dort geprüft

Zwei Erweiterungen, deren Startsätze sich Wörter teilen, erzeugen genau
die lautlosen Phantomkombinationen von oben. Die zweite Prüfung ist
deshalb der volle Gegentest: Piper spricht jeden neuen Startsatz, Vosk
hört mit der **vollständigen** Grammatik aller bereits eingebauten
Erweiterungen zu. Erst dann zeigt sich, ob ein Satz mit einem
bestehenden verwechselt wird.

Das Werkzeug dafür gibt es: `/usr/local/bin/dialos-grammatik-pruefen.py`. **Seit dem
2026-09-17 kann es auch Sätze prüfen, die noch nicht eingebaut sind** - vorher
ging genau das nicht, und die Lücke war nicht harmlos:

```bash
/usr/local/bin/dialos-grammatik-pruefen.py --neu "unterlagen durchsuchen"
```

Ohne `--neu` hörte Vosk den Kandidaten gegen eine Grammatik, die ihn **nicht
enthält**, und presste ihn auf den nächstliegenden bestehenden Satz. Das sah
nach einer Verwechslung aus, war aber nur ein Werkzeugfehler - und umgekehrt
konnte ein kaputter Kandidat unauffällig bleiben. Mit `--neu` kommt er
versuchsweise in die Grammatik, und geprüft wird **in beide Richtungen**:

| Frage | Warum sie zählt |
|---|---|
| Wird der Kandidat wörtlich erkannt? | Sonst ist er als Befehl unbrauchbar. |
| **Gehen bestehende Sätze durch ihn kaputt?** | **Die wichtigere Frage.** Ein Kandidat, der selbst durchfällt, kostet nur sich selbst; einer, der einen bestehenden Befehl verwechselbar macht, nimmt etwas kaputt, das heute funktioniert - und das fällt erst auf, wenn der Nutzer allein mit dem Gerät ist. |

Ebenfalls seit dem 2026-09-17 läuft die **erste** Pflichtprüfung dort mit,
statt nur in der Doku zu stehen: Fehlt ein Wort im Wortschatz, meldet Vosk das
zwar selbst - aber die Meldung ging in `SetLogLevel(-1)` unter. Geprüft wird
jetzt vorher gegen `graph/words.txt`, ohne Sprechen, und **getrennt nach
Kandidat und Bestand**: Ein fehlendes Wort im Kandidaten beendet die Prüfung,
eines im Bestand wird als Altlast gemeldet, blockiert den Kandidaten aber
nicht. Sonst hinge ein neuer Befehl an einem alten Problem, mit dem er nichts
zu tun hat.

**Mehrere Kandidaten in einem Lauf prüfen bedeutet, sie GEMEINSAM zu prüfen**
(`--neu "…" --neu "…"`). Das ist richtig, wenn beide eingebaut werden sollen -
dann müssen sie auch miteinander verträglich sein. Wer zwei Formulierungen
gegeneinander abwägen will, prüft sie **einzeln**.

### 3. Das Mikrofon gehört immer genau einem

Dieselbe Regel wie „nur ein Player darf gleichzeitig laufen"
([anwendungen.md](anwendungen.md)), aus demselben Grund: Ein Befehl, den
zwei Erkenner hören, ist nicht mehr eindeutig - und der Nutzer kann nicht
nachsehen, wer gerade zuhört.

Die Übergabe läuft über eine Markierungsdatei, wie beim Diktat. **Dazu
gehört zwingend eine Wache:** Eine abgestürzte Erweiterung darf das
Mikrofon nicht für immer behalten. Der Nutzer würde sonst gegen ein
taubes Gerät sprechen, ohne einen Weg zurück - und das Ausschalten der
Sprachsteuerung wäre selbst nicht mehr hörbar.

### 4. Gesprochen wird ausschließlich über `dialos-say.py`

Eine Erweiterung ruft **nie** Piper oder speech-dispatcher direkt auf.
Sonst hätte DialOS eine zweite Stimmquelle, und Stephans Wahl zwischen
Anna und Michael wäre beim zweiten Werkzeug wirkungslos.

Über `dialos-say.py` kommt alles mit, was sonst je Erweiterung neu
falsch gemacht würde:

- **Stimme und Tempo** aus `DefaultVoice` in `piper-generic.conf` -
  dieselbe Quelle, die `dialos-stimme.py setzen` schreibt
- **Die Abtastrate** aus der `.json` der Stimme statt aus einer
  abgeschriebenen Zahl. Eine abgeschriebene Zahl hat schon einmal alle
  Hörproben 38 % zu schnell laufen lassen.
- **Die Aussprache-Regeln**, die seit dem 2026-08-24 pro Stimme gelten
- **Der Ansagen-Speicher**, der sich beim Stimmwechsel selbst entwertet

Der **Name des Assistenten** wird aus
`/usr/local/share/dialos/assistent-name.txt` gelesen. „Anna" und
„Michael" gehören in keinen Quelltext einer Erweiterung - sonst stellt
sich eine Frauenstimme irgendwann als Michael vor.

## Der Programmname ist nicht der Sprachbefehl

Bei Denkzettel fiel beides zusammen, hier nicht - und das ist keine
Feinheit, sondern eine harte Bedingung: **„dialos" steht nicht im
Vosk-Wortschatz** (geprüft am 2026-09-17; deshalb spricht Piper es auch
als „Dial OS" beziehungsweise „Dial O S"). „DialOS-Suche öffnen" wäre als
Zuruf schlicht nicht möglich.

Die `startsaetze` werden deshalb aus gewöhnlichen Wörtern gebaut und
halten die Regeln aus [sprachbefehle.md](sprachbefehle.md) ein - vor
allem: **ein Auslösewort zusätzlich zum Ziel**, und lang genug. Ein
bloßes „suchen" wäre zu kurz und zu häufig; das ist die Lehre aus den
30 Fehlstarts, die „starten" als Kernwort verursacht hat.

## Was eine Erweiterung nicht darf

- **Die Kern-Grammatik über ihre `startsaetze` hinaus erweitern.** Sonst
  ist der ganze Zweck dahin.
- **Selbst sprechen** (siehe Regel 4).
- **Das Mikrofon behalten**, wenn sie fertig ist.
- **Während eines Diktats anspringen.** Die Marke des Diktats gilt für
  Erweiterungen genauso wie für den Kern - wer „unterlagen durchsuchen"
  in einen Brief diktiert, will es geschrieben haben, nicht ausgeführt.
- **Sicherheitskritisches ohne Ja/Nein-Rückfrage tun.** Die Regel gilt
  unabhängig davon, wie sicher die Erkennung war.

## Wie eine Erweiterung aufs Testgerät kommt

**Stephans Anforderung vom 2026-09-17:** Die fertige Erweiterung muss sich
vom T490 aus nahtlos aufspielen lassen. Das ist keine Nebenbedingung - es
entscheidet über den Aufbau, und deshalb steht es hier und nicht unter
„Offene Punkte".

Der Weg existiert bereits und soll **derselbe bleiben**:

```bash
sudo /usr/local/sbin/dialos-aufspielen && /media/dialosadmin/SanDisk-Extreme/DialOS/repo/scripts/dialos-installstand.sh --befehl
```

`dialos-aufspielen` liest heute aus genau einer Quelle:

```
/media/dialosadmin/SanDisk-Extreme/DialOS/repo/iso-build/config/includes.chroot
```

Alles darunter wandert an seinen Platz im Dateisystem, mit Rechte-Tabelle,
Ausschlussliste und Neustart nur der Dienste, deren Dateien sich geändert
haben.

**Für eine Erweiterung im DialOS-Repo funktioniert das ohne jede
Änderung.** Beide Dateien fallen in bestehende Einträge der
Rechte-Tabelle:

| Datei | Ort im Repo | Rechte | woher |
|---|---|---|---|
| Programm | `…/includes.chroot/usr/local/bin/dialos-suche.py` | 0755 | `("usr/local/bin", 0o755)` |
| Manifest | `…/includes.chroot/usr/local/share/dialos/erweiterungen/dialos-suche.json` | 0644 | `("usr/local/share", 0o644)` |

**Für die erste Erweiterung braucht es deshalb an `QUELLE` gar nichts** -
sie liegt im DialOS-Repo, also unter dem Pfad, den `dialos-aufspielen`
ohnehin liest. Die Umstellung auf eine **Liste** von Quellen wird erst
fällig, wenn die zweite Erweiterung in ein eigenes Repo zieht; sie steht
trotzdem in `TODO.md`, weil sie dann sicher gebraucht wird. Wichtig ist
dabei nur eines: Mehrere Quellen mit demselben `includes.chroot`-Aufbau
sind der Weg, **kein** zweites Aufspielskript. Die bestehende
sudoers-Regel ist ausweislich ihres eigenen Kopfes „praktisch ein
Root-Zugang" - ein zweiter Weg wäre ein zweiter.

**Zwei Anpassungen braucht es dagegen sofort**, und beide sind klein:

1. **Die Prüfungen aus Regel 1 und 2 gehören ins Aufspielen.** Ist ein
   Manifest unter den geänderten Dateien, werden Wortschatz und
   Kollisionen geprüft, **bevor** es an seinen Platz kommt - und bei
   Fehlschlag wird genau diese Datei nicht aufgespielt, mit Meldung. Erst
   dadurch ist „verweigern statt warnen" überhaupt erzwingbar.
2. **`dialos-installstand.sh` muss das Manifest mit vergleichen.** Sonst
   gilt die Regel „Installationsstand prüfen, nicht annehmen" für
   Erweiterungen nicht - und genau dieser Fehler hat am 2026-08-19 zwei
   Tage gekostet, als zwei Skripte auf dem Gerät älter waren als im Repo.
   Sobald Erweiterungen in eigenen Repos liegen, verdoppelt sich die
   Gelegenheit dazu.

**Die Kern-Grammatik wird beim Start des Dienstes aus den Manifesten
gebaut, nicht beim Aufspielen.** Damit genügt ein Neustart des
Befehlsdienstes, ein eigener Installationsschritt entfällt.

**Achtung, hier lauert ein lautloser Fehlschlag** - beim Gegenlesen des
Codes am 2026-09-17 aufgefallen: `dialos-aufspielen` startet den
Befehlsdienst **nicht** neu. Es **druckt** die beiden Befehle dafür, und
zwar nur dann, wenn sich `dialos-sprachbefehl-desktop.py` **selbst**
geändert hat:

```python
for skript in ("dialos-sprachbefehl-desktop.py", ...):
    if any(rel.endswith(skript) for rel, *_ in liste):
```

Das ist für Sitzungsdienste richtig so - sie laufen als Nutzer, nicht als
root, und ein Skript mit sudo-Rechten sollte sie nicht anfassen. Für
Erweiterungen bedeutet es aber: **Ein neues Manifest allein löst keinen
Hinweis aus.** Die Erweiterung läge dann installiert auf der Platte, der
Dienst liefe weiter mit der alten Grammatik, und ihr Startsatz täte
nichts - ohne Fehlermeldung, ohne Ansage. Genau der Ausgang, der für
einen blinden Nutzer der schlechteste ist.

Die Bedingung muss deshalb den Manifest-Ordner mit einschließen, nicht
nur die Skriptnamen.

**Was damit NICHT gelöst ist:** Das gilt für das Entwicklungsgerät. Wie
eine Erweiterung auf ein Kundengerät kommt, auf dem es weder
`dialos-aufspielen` noch die sudoers-Regel geben darf
(`scripts/dialos-aufraeumen.sh` entfernt beides), ist offen - siehe unten.

### Nach dem Aufspielen: die Abnahme

```
scripts/dialos-suche-abnahme.py
```

Prüft in einem Durchgang, was sich ohne Mikrofon prüfen lässt: liegen alle
Dateien am Platz, ist das Manifest angemeldet, **ist der laufende
Befehlsdienst jünger als das aufgespielte Manifest**, hängt eine verwaiste
Mikrofon-Marke, steht der Index. Der Altersvergleich ist die Antwort auf
den lautlosen Fehlschlag von oben - er sieht den vergessenen Neustart,
statt ihn den Nutzer beim Zurufen entdecken zu lassen.

**Drei Urteile, nicht zwei:** `OK`, `FEHLER` und `OFFEN`. Die dritte Stufe
steht für alles, was nur mit Mikrofon zu prüfen ist, und für Prüfungen, die
nicht liefen. Ungeprüftes als bestanden zu zählen wäre genau der Fehler,
den die Abnahme finden soll - am 2026-09-17 sahen eine nie anlaufende
Wortschatzprüfung und eine nie greifende Wache beide aus wie ein Erfolg.

Mit `--lang` läuft die Wortschatz-Gegenprobe mit: Der Kandidat
`xylofonquark durchsuchen` **muss** abgewiesen werden. Hier gilt ein
Durchlauf als Fehler.

## Die dritte Namenskategorie

`CLAUDE.md` kannte bisher zwei Fälle: Kernbestandteil (heißt
`dialos-*.py` und liegt im DialOS-Repo) und Familienmitglied ohne Präfix
(Denkzettel). **Erweiterungen sind der dritte** - und sie tragen das
Präfix zu Recht:

- Sie laufen ohne DialOS nicht, weil sie auf dessen Grammatik, Stimme und
  Mikrofon-Übergabe angewiesen sind.
- Einzeln installiert ergeben sie keinen Sinn.
- Sie sind kein eigenes Produkt auf anderer Hardware (das ist
  DialOS-Mobil) und kein eigenständiges Programm mit eigener Engine und
  eigener Zielgruppe (das ist Denkzettel).

Damit ist **DialOS-Suche** richtig benannt, und die Regel „neue
Familienmitglieder werden NICHT umbenannt" bleibt unangetastet - sie gilt
für eigenständige Programme, nicht für das, was ohne DialOS gar nicht
läuft.

## Das Symbol: der Entwurf fiel bei 32 Pixeln durch, die Lupe trägt

Stephan hat am 2026-09-17 einen Entwurf geliefert. Er liegt als
`assets/suche-icon-entwurf.png` im Repo, **bewusst „Entwurf" im Namen**:
Er ist noch nicht die Auslieferungsfassung.

**Stilistisch sitzt er.** Derselbe Kreis, dieselbe Dame, dieselbe
tragende Hand, derselbe Blau-Grün-Verlauf wie beim DialOS-App-Icon - die
Zugehörigkeit ist auf den ersten Blick da. Rechts kommen statt der
Schallwellen ein Dokument, ein Briefumschlag und eine Lupe.

**Gemessen wurde, was zählt: die Erkennbarkeit bei kleiner Darstellung.**
Der Maßstab steht seit dem 2026-08-24 im Quelltext von
`Denkzettel/assets/icon-bauen.py`: „Wenn beide Programme nebeneinander in
der Fensterleiste liegen, muss man sie bei 32 Pixeln auseinanderhalten
können." Alle drei Icons wurden auf 32, 48 und 64 Pixel gerechnet und
nebeneinandergelegt (`assets/suche-icon-groessenvergleich.png`, Zeilen von
oben nach unten 32/48/64, Spalten DialOS, Denkzettel, Suche):

| Größe | DialOS | Denkzettel | Suche (Entwurf) |
|---|---|---|---|
| 64 px | klar | klar | klar |
| 48 px | klar | klar | noch klar - Lupe als Kreis, Dokument als Block |
| **32 px** | **klar** | **klar** | **fällt durch** - Dokument, Brief und Lupe verschmelzen zu einem Klumpen |

**Die Ursache ist nicht die Zeichnung, sondern die Anzahl.** DialOS hat
rechts **ein** Objekt (Schallwellen), Denkzettel **eines** (Stift mit
Zeile), der Entwurf **drei**. Bei 32 Pixeln stehen für die rechte Hälfte
noch etwa 14 × 20 Pixel zur Verfügung - die Textzeilen im Dokument liegen
dort unter einem Pixel Abstand und laufen zusammen. Zusätzlich drängt der
Platzbedarf rechts das Gesicht nach links, wodurch auch die linke Hälfte
enger wirkt als bei den beiden anderen.

### Gebaut am 2026-09-17: auf die Lupe reduziert

Stephans Entscheidung nach der Messung: „reduziere den rechten Bereich auf
die Lupe". Gebaut mit `assets/suche-icon-bauen.py`, abgeleitet von
`Denkzettel/assets/icon-bauen.py` - dieselbe Technik, weil sie dort schon
einmal genau dieses Problem gelöst hat.

**Die Lupe wird gezeichnet, nicht aus dem Entwurf ausgeschnitten.**
Kopiert käme sie mit den Schnittkanten des überlappenden Briefumschlags.
Gezeichnet hat sie saubere Kanten und freie Größe. Denkzettel hat den
Stift aus demselben Grund gezeichnet.

**Zwei Varianten wurden gebaut und verglichen**, damit es niemand ein
zweites Mal prüft:

| Variante | Ergebnis bei 32 px |
|---|---|
| **nur Lupe** (Schallwellen entfernt) | **klar** - Kreis mit Griff, von DialOS und Denkzettel eindeutig unterscheidbar. **Gewählt.** |
| Wellen **und** Lupe (näher am Entwurf) | verworfen - Wellen und Ring überlagern sich zu demselben Klumpen, den der Entwurf schon hatte |

Damit folgt das Ergebnis dem Muster der Familie: Denkzettel ersetzt die
Schallwellen durch den Stift, DialOS-Suche durch die Lupe. **Ersetzen,
nicht ergänzen** - genau die Lehre aus dem Entwurf.

Der Griff ist bewusst kurz. Er erklärt die Form bei 512 Pixeln, trägt bei
32 nichts mehr bei, und je länger er ist, desto näher kommt er dem Bogen.
Das Skript **prüft den Abstand zum Ring vor dem Zeichnen** und bricht ab,
wenn er gerissen wird - der erste Versuch ist genau daran aufgelaufen
(193,6 gegen erlaubte 192, am Griffende).

**Erzeugt werden zwölf Dateien:** `suche-icon-light-*.png` und
`suche-icon-dark-*.png`, je in 32, 48, 64, 128, 256 und 512 Pixeln, alle
mit Alpha-Kanal. Der Vergleich liegt als
`assets/suche-icon-groessenvergleich.png` bei - links auf hellem Panel,
rechts auf dunklem, jeweils in der Fassung, die dort hingehört.

**Eine Falle, gemessen und festgehalten: DialOS und Denkzettel benennen
gegenläufig.**

| Datei | Scheibe |
|---|---|
| `DialOS/assets/app-icon-light.png` | rgb(254,255,255) - hell |
| `DialOS/assets/app-icon-dark.png` | rgb(4,22,47) - dunkel |
| `Denkzettel/assets/app-icon-dark.png` | rgb(255,255,255) - **hell** |

Bei Denkzettel heißt „-dark" also „Datei für dunkle Umgebungen" (Stephans
Entscheidung vom 2026-08-24), bei DialOS schlicht „dunkles Icon". Beide
sind für sich stimmig, zusammen sind sie eine Falle. **DialOS-Suche folgt
DialOS**, weil die Dateien in demselben Ordner neben `app-icon-light.png`
liegen - zwei gegenläufige Bedeutungen desselben Suffixes an einem Ort
wären der sichere Weg, beim Einbinden die falsche Datei zu erwischen. Und
ein falsches Icon fällt einem blinden Nutzer nie auf, dem sehenden Helfer
aber sofort.

**Der Entwurf bleibt liegen** (`assets/suche-icon-entwurf.png`). Er ist
die Vorlage der Idee, und die Messung, an der er gescheitert ist, steht
oben - beides gehört zusammen.

## Wo eine Erweiterung wohnt, und wie sie ausgeliefert wird

Beides entschieden mit Stephan am 2026-09-17.

### Entwicklung: im DialOS-Repo, nicht in einem eigenen

Ein eigenes Repo je Erweiterung ist das Ziel - eigene Versionierung,
eigenes Changelog, und das DialOS-Repo wächst nicht weiter (es trägt schon
`iso-build/` und acht Hintergrundbilder zu je rund 11 MB).

**Für die erste Erweiterung aber noch nicht.** Solange sich die
Schnittstelle selbst ändert, müssten zwei Repos synchron gehalten werden,
während beide instabil sind - und jeder Fehler wäre erst einmal nicht
zuzuordnen, welchem von beiden er gehört. Das Herauslösen später ist ein
überschaubarer Schritt; das Zusammenführen zweier wandernder Stände wäre
es nicht.

Damit bleibt `QUELLE` in `dialos-aufspielen` vorerst ein einzelner Pfad.
Die Umstellung auf eine Liste wird erst fällig, wenn die zweite
Erweiterung in ein eigenes Repo zieht - sie steht trotzdem in `TODO.md`,
weil sie dann sicher gebraucht wird.

### Auslieferung: als `.deb`, aber nicht für die Entwicklung

| Gerät | Weg | Warum |
|---|---|---|
| Entwicklungsgerät (T490) | `dialos-aufspielen` | Geänderte Dateien in Sekunden. Ein `.deb` müsste bei jeder Iteration gebaut, hochgezählt und installiert werden - bei einem Sprachdialog, an dem eine Formulierung zwanzigmal am Tag gedreht wird, ist das der Unterschied zwischen „läuft" und „nervt". |
| Kundengerät | `.deb` | Dort gibt es `dialos-aufspielen` gar nicht. `scripts/dialos-aufraeumen.sh` entfernt es samt sudoers-Regel, und das soll so bleiben. |

**Das stärkste Argument für das Paket ist `postinst`.** Die beiden
Pflichtprüfungen aus Regel 1 und 2 brauchen einen Ort, an dem sie nicht
umgangen werden können: Schlägt die Prüfung im Installationsskript fehl,
schlägt die Installation fehl. Bei einem Skript, das Dateien kopiert,
bleibt „verweigern statt warnen" eine Höflichkeit.

Dazu kommt `Depends:` - die Abhängigkeiten von DialOS-Suche werden vom
Paketmanager erzwungen statt von einer Zeile in der Doku. Das sind
`poppler-utils` und `tesseract-ocr` für die Extraktion und, solange
`extract/` aus MailBurg geteilt wird, dessen Kern. MailBurg baut sich
ohnehin schon als `.deb`.

**Ehrlich dazu:** DialOS baut heute kein einziges Paket. Einrichtung läuft
über Shell-Skripte (`dialos-parakeet-einrichten.sh`,
`dialos-erkenner-einrichten.sh`). Ein `.deb` ist damit neue Infrastruktur -
`debian/control`, `changelog`, `rules` -, und ohne Repository-Server bleibt
es bei `dpkg -i` von Hand, also ohne automatische Updates.

## Offene Punkte

Bewusst nicht entschieden, weil sie Stephans Entscheidung sind oder weil
die Antwort gemessen werden muss:

1. **Was passiert bei einem Kern-Update?** `braucht_dialos` erkennt den
   Fall, aber es steht nicht fest, was dann geschieht: Erweiterung
   abschalten und ansagen, oder trotzdem starten und hoffen. Für einen
   blinden Nutzer ist ein stiller Ausfall die schlechtere Antwort.
2. **Ob hassil hier seinen Platz findet.** Es ist seit 2026-08-13
   installiert und bis heute ungenutzt (keine einzige Vorlage im System).
   Die Zuordnung Satz → Aktion je Erweiterung wäre der erste Ort, an dem
   es etwas beitragen könnte - entschieden ist das nicht.
3. **Ob der Index verschlüsselt liegen muss.** Er steht auf der
   LUKS-Partition von `nutzer`, ist bei ausgeschaltetem Gerät also
   geschützt. Eine eigene Verschlüsselung käme nur gegen einen Angreifer in
   der laufenden Sitzung - und der hätte auch die Dokumente selbst, die
   unverschlüsselt danebenliegen. Ein Passwort, das ein blinder Nutzer
   sprechen müsste, wäre dafür ein hoher Preis.
4. **Wie `extract/` geteilt wird, ohne zu kopieren.** Import aus MailBurgs
   Kern ist der einfache Weg und kostet nichts (`dependencies = []`). Sauberer
   wäre ein eigenes kleines Paket, das beide benutzen - das ist aber ein
   Umbau an MailBurg und gehört dorthin entschieden, nicht hierher.

## Die erste Erweiterung: DialOS-Suche

Zweck: Briefe, Dokumente, Notizen und E-Mails per Sprache suchen und
vorlesen. Die Programmwahl steht in [anwendungen.md](anwendungen.md), die
Sätze in [sprachbefehle.md](sprachbefehle.md) (seit 2026-09-18 unter
„Umgesetzt", davor unter „Vorgesehen"), die Aufgaben
in [TODO.md](../TODO.md).

**Von MailBurg wird die Extraktionskette geteilt, nicht das Programm**
(korrigiert am 2026-09-17 nach Stephans Frage, ob es MailBurg ganz braucht
„oder nur Teile"). Der Unterschied ist nicht die Größe, sondern die Aufgabe:
**MailBurg archiviert, DialOS-Suche muss nur finden.** Die Dokumente liegen
schon im Dateisystem; sie ein zweites Mal in einen inhaltsadressierten Speicher
zu schreiben wäre Verdopplung. Geteilt wird `extract/` (1.360 Zeilen, PDF, OCR,
Office), neu gebaut wird ein schlanker FTS5-Index über die vorhandenen Dateien.
Vollständig mit Zahlen in [anwendungen.md](anwendungen.md).

**Zwei Anforderungen stellt DialOS-Suche, die über eine gewöhnliche
Erweiterung hinausgehen** und deshalb hier stehen, weil sie den Entwurf
mitbestimmt haben:

- **Ein Suchbegriff passt in keine geschlossene Grammatik.** „Krankenkasse"
  kann nicht in einer Satzliste stehen, sonst müsste jedes suchbare Wort
  darin stehen. Es braucht denselben Zweistufen-Wechsel wie beim Diktat -
  der kleine Vosk-Erkenner nimmt den Startsatz, dann freie Erkennung für
  den Begriff.

  **Welcher Erkenner das ist, steht dabei schon fest: Parakeet.** Seit dem
  2026-09-16 fest eingebaut
  (`sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` über sherpa-onnx, Modell
  unter `/usr/local/share/dialos-parakeet/`, 12 s Laden statt 33 s beim
  großen Vosk-Modell, abschaltbar mit `parakeet-aus`). Gemessen am
  2026-09-15 am vorgelesenen Brief: **2,8 % Wortfehler gegen Vosk 12,7 %**.
  DialOS-Suche muss dafür also nichts beschaffen und nichts neu messen, und
  die Arbeitsteilung steht ohnehin schon so: **Vosk für Befehle, Parakeet
  für Text** - und ein Suchbegriff ist Text.

  Zu prüfen bleibt genau eine Sache, und die ist neu: ob sich Parakeet ein
  **Wörterbuch aus dem eigenen Archiv** mitgeben lässt. Die häufigsten
  Absendernamen aus dem FTS5-Index wären genau die Wörter, an denen jede
  freie Erkennung scheitert. Für denselben Zweck hat das Diktat bereits ein
  persönliches Wörterbuch („gehört = geschrieben"), das nur auf dem Gerät
  liegt.
- **Ein Dokument ist lang, und während DialOS spricht, hört es nicht zu.**
  **Das ist nicht hypothetisch, sondern am Gerät belegt:** „Alle Befehle
  vorlesen" läuft **144 Sekunden**, und in
  [sprachbefehle.md](sprachbefehle.md) steht dazu ausdrücklich „nicht
  unterbrechbar - dafür gibt es die Themen". „Brief vorlesen" liest ebenso
  am Stück. Zum Vergleich: „Windows Desktop." dauert 1,5 Sekunden.

  Für ein Archiv wird daraus der Normalfall statt der Ausnahme - wer sucht,
  bekommt Treffer, die er nicht alle hören will. Es ist dieselbe
  Fehlerklasse wie die gemessene Taubheit von 3,6 Sekunden nach dem
  Umschalten (siehe [sprachsteuerung.md](sprachsteuerung.md)), nur
  hundertfach länger. Vorgesehen: absatzweise vorlesen, zwischen den
  Absätzen ein kurzes Lauschfenster mit einer Mini-Grammatik aus „stopp",
  „weiter", „zurück", „nochmal". Kein echtes Barge-in - „Soll ich stoppen?"
  im vorgelesenen Brief würde ihn stoppen.

  **Gebaut gehört das nicht in DialOS-Suche, sondern in `dialos-say.py`.**
  Die 144 Sekunden der Befehlsübersicht sind heute schon ein offener Punkt,
  und sie gehören keiner Erweiterung. Wer die Unterbrechbarkeit für das
  Archiv baut, löst sie für alles mit.

## Die zweite Erweiterung: DialOS-Mail

Seit 2026-09-21 (Stephan: „Dann müssen wir ja bei einer neuen Mail die
Mailadresse, den Betreff und den Text noch hin bekommen und dann auch die Mail
verschicken!"). **Am 2026-09-25 am Gerät durchgelaufen**, vom Empfänger bis zum
Entwurf.

- **Manifest:** `/usr/local/share/dialos/erweiterungen/dialos-mail.json`,
  Startsätze „neue e mail schreiben" und „e mail schreiben", eigene Grammatik
  „ja", „nein", „vorlesen", „abbrechen". Programm:
  `dialos-mail-schreiben.py`.
- **Der Dialog:** Empfänger aus den Thunderbird-Kontakten oder buchstabiert →
  Betreff → Text diktieren wie im Brief → nur die **Eckdaten** („3 Sätze an …,
  Betreff …"), der ganze Text auf Zuruf. Bei allem außer einem klaren „ja"
  wird **abgelegt statt gesendet**. Die Sätze im Einzelnen stehen in
  [sprachbefehle.md](sprachbefehle.md).
- **Nichts davon ist neu geschrieben:** Empfängerdialog, Diktat und
  Rückfragen kommen aus DialOS-Suche (`dialos-suche.py`). Die zweite
  Erweiterung ist damit zum größten Teil aus Bausteinen der ersten
  zusammengesetzt - ein zweiter Empfängerdialog hätte beim nächsten Fehler
  zweimal repariert werden müssen.
- **Geschrieben wird nur durch Thunderbird selbst**, über die Brücke
  (nächster Abschnitt). Senden ist gebaut, am Gerät aber noch nicht geprobt
  (Stand 2026-09-25: bei der Frage wurde bisher immer „nein" gesagt).

## DialOS-Rhythmbox: eine Erweiterung ohne Manifest (seit 2026-09-25)

Stephan am 2026-09-25, auf die Frage nach der Einordnung: „Ja es ist eine
Erweiterung für DialOS." Sie trägt das Präfix damit zu Recht - sie ergibt
ohne DialOS keinen Sinn, weil ihr einziges Erzeugnis die Medienliste
dieses Systems ist.

**Sie ist trotzdem der erste Fall ohne Manifest**, und das ist keine
Nachlässigkeit, sondern folgt aus dem Manifest selbst: Seine Felder sind
`startsaetze`, `eigene_grammatik` und `braucht_mikrofon`. DialOS-Rhythmbox
hat nichts davon. Es wird mit Maus und Tastatur bedient, nimmt das
Mikrofon nie, spricht nicht und wird nie durch einen Satz gestartet. Ein
Manifest mit leeren Startsätzen würde behaupten, es gäbe einen
Sprachbefehl, den es nicht gibt - und die Grammatikprüfung beim Einbauen
liefe über nichts.

Damit ist sie strukturell die Zwillingsschwester von
`dialos-persoenliche-daten-maske.py`: eine Maske, die eine Datei pflegt,
aus der andere Programme lesen. Auch die hat kein Manifest.

**Was sie tut:** Sender bei radio-browser.info suchen - landesweit, nach
Bundesland, Stadt oder Genre -, jeden antesten und als `medienliste.json`
im Format aus [medienliste.md](medienliste.md) ausgeben. Auf Wunsch trägt
sie die Auswahl auch gleich in Rhythmbox ein.

- **Programm:** `/usr/local/bin/dialos-rhythmbox.py` (Oberfläche,
  GTK4/libadwaita), `/usr/local/bin/dialos_rhythmbox_sender.py` (die
  Arbeit, zugleich Kommandozeilen-Werkzeug), `/usr/local/bin/dialos_farben.py`
  (die gemeinsame Palette).
- **Menüeintrag:** `/usr/share/applications/dialos-rhythmbox.desktop`,
  Symbol unter `/usr/share/icons/hicolor/<größe>/apps/dialos-rhythmbox.png`.
- **Kein Manifest**, siehe oben. Keine Einträge in der Kern-Grammatik.

**Geprüft wird, ob Ton kommt - nicht, ob der Server antwortet.** Jeder
Stream wird von `ffprobe` dekodiert, und zusätzlich wird der ICY-Name
verglichen, den der Sender über sich selbst sendet. Das ist dieselbe
Haltung wie die Regel „keiner Zustandsmeldung glauben, wenn sich das
Ergebnis messen lässt" aus der Audio-Arbeit - und sie hat sich sofort
bezahlt gemacht: „MDR Aktuell" zeigte über eine `.m3u`-Datei auf **MDR
Kultur**, „Radio Swiss Classic" war die **italienische** Fassung (sie
meldete sich als „Swiss Classic I"), und „Kronehit" zeigte auf eine
JSON-Schnittstelle. Alle drei hätten HTTP 200 geliefert.

**Nur frei zugängliche Quellen** (Stephan: „Ohne einen Account oder so").
Adressen mit `token`, `sid` oder Benutzername werden abgewertet, HTTP
401/403 wird als „verlangt Zugangsdaten" gemeldet. Dabei kam ein
grundsätzlicher Fehler heraus: Gespeichert wurde `url_resolved`, die
**aufgelöste** Adresse - bei der ARD-Verteilung hängt die eine
Sitzungskennung an, die abläuft. `http://radioeins.de/stream` ist der
dauerhafte Einstieg. Auf einem Gerät, das jahrelang läuft, ist das keine
Feinheit: Der Sender verstummt irgendwann ohne erkennbaren Grund, und der
blinde Nutzer kann nicht nachsehen, warum.

**Das Symbol wurde gemessen, nicht beurteilt.** Stephans Entwurf hatte
rechts Schallwellen **und** ein Mikrofon - zwei Objekte, also genau die
Konstellation, an der der Suche-Entwurf bei 32 Pixeln gescheitert ist
(siehe oben). Nachgemessen mit demselben Verfahren: bei 64 px klar, bei
48 px verschmelzend, bei 32 px ein Klumpen. Gebaut wurde deshalb die
reduzierte Fassung mit `assets/rhythmbox-icon-bauen.py` - Wellen raus,
Mikrofon gezeichnet statt ausgeschnitten. Der Entwurf liegt als
`assets/rhythmbox-icon-entwurf.png` daneben.

## Die Thunderbird-Brücke

**Keine Erweiterung im Sinne dieser Datei, obwohl beide so heißen.** Die
DialOS-Brücke ist eine *MailExtension für Thunderbird*: Sie hat kein
DialOS-Manifest, keine Grammatik und kein Mikrofon. Sie steht hier, weil
beide Erweiterungen über sie mit Thunderbird sprechen - und weil
[anwendungen.md](anwendungen.md) seit dem 2026-09-21 auf diese Datei verweist,
hier aber bis zum 2026-09-25 nichts darüber stand.

**Warum es sie gibt** (seit 2026-09-21): DialOS hatte vorher selbst in
Thunderbirds Dateien geschrieben - Entwürfe in die mbox, Kontakte in
`abook.sqlite`. Jeder dieser Wege hat einen Fehler erzeugt (LF statt CR LF,
`X-Mozilla-Status: 0008` heißt GELÖSCHT). Dreimal dasselbe Muster: in fremde
Dateiformate schreiben, statt das Programm zu fragen, dem sie gehören. Seitdem
gilt: *Lesen darf man von außen, Schreiben nicht.*

| Teil | Wo |
|---|---|
| Quelltext der MailExtension (`manifest.json`, `hintergrund.js`) | Ordner `thunderbird-erweiterung/` im Repo |
| Kennung | `bruecke@dialos.org` |
| Gepackte `.xpi` | `/usr/local/share/dialos/dialos-bruecke.xpi`, gebaut von `sudo scripts/dialos-erweiterung-bauen.sh` |
| Einbau in jedes Profil | `/usr/lib/thunderbird/distribution/policies.json`, `force_installed` |
| Gegenstelle auf DialOS-Seite (Native Messaging) | `dialos-thunderbird-bruecke.py`, angemeldet über `/usr/lib/thunderbird/native-messaging-hosts/dialos_bruecke.json` |

**Was sie kann:** Entwürfe im Entwurfsordner des *Kontos* ablegen (der wird
zum Server hochgeladen, anders als die lokalen Ordner), senden, Kontakte
anlegen, offene Schreibfenster vor dem Schließen als Entwurf sichern und
liegende Entwürfe auflisten. Ist Thunderbird zu, merkt DialOS einen Entwurf
vor, und die Brücke holt ihn nach, sobald Thunderbird sie startet.
**Noch offen:** Der Empfänger-Dialog des Briefs trägt Kontakte weiter selbst
in `abook.sqlite` ein; die Brücke kann es, das Umhängen fehlt (`TODO.md`).

**Drei Entscheidungen und ihr Grund:**

- **Die `.xpi` liegt nicht im Repo.** Sie wäre eine zweite Fassung derselben
  zwei Dateien - und die erste, die vergessen wird, wenn jemand
  `hintergrund.js` ändert. Dann liefe auf dem Gerät eine andere Erweiterung,
  als im Repo steht, und niemand sähe es. Nach jeder Änderung die Fassung in
  `manifest.json` hochzählen, sonst nimmt Thunderbird die neue Datei nicht an.
- **`force_installed` über `policies.json`, nicht von Hand.** Am 2026-09-21
  war die Erweiterung zuerst von Hand installiert - und damit nur im Profil
  von `dialosadmin`. Im Konto des Kunden wäre ein ganzer Tag Arbeit
  wirkungslos gewesen, ohne jede Fehlermeldung. `force_installed` greift auch
  in vorhandenen Profilen, entsteht mit jedem neuen und lässt sich nicht
  versehentlich entfernen.
- **Unsigniert ist in Ordnung**, weil Debians Thunderbird
  `xpinstall.signatures.required` auf `false` hat. Bei einem Thunderbird von
  Mozilla wäre das anders.
