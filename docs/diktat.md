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
| `hunspell -m`: Substantiv, wenn eine Lesart einen großgeschriebenen Stamm hat (Stephans Idee, die Rechtschreibkontrolle zu benutzen) | 49/53 = **92,5 %** |

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

**Der vierte Versuch ist der lehrreichste, weil er aus der richtigen Idee
kam.** Stephan hat vorgeschlagen, den fertigen Text durch die
Rechtschreibkontrolle der Textverarbeitung zu schicken. Das trifft nicht,
weil es **kein Rechtschreibfehler** ist - „wetter" ist ein korrekt
geschriebenes deutsches Wort, und LibreOffice benutzt für Deutsch dasselbe
hunspell. Eine Prüfung, die fragt „existiert dieses Wort", hat nichts zu
beanstanden.

Eine Ebene tiefer trägt die Idee aber doch: `hunspell -m` gibt die
morphologische Analyse aus, und dort steht der Stamm.

```
vertrag    fl:V st:tragen fl:W                        <- Stamm "tragen", ein Verb
Vertrag    fl:V st:tragen fl:W   Vertrag st:Vertrag   <- zusaetzlich Stamm "Vertrag"
```

Ein Substantiv hat also eine Lesart mit großgeschriebenem Stamm, eine
Verbform nicht. Damit waren die vier alten Fehler behoben - „Vertrag",
„Butter", „Dank" und „Wetter" kamen richtig heraus. **Es entstanden vier
neue:**

- **„ich Meinen Vertrag" und „es Gut das Wetter".** „Das Meinen" und „das
  Gut" sind ebenfalls Substantive. Kein Wörterbuch kann „es geht gut" von
  „das Gut" unterscheiden - dafür braucht man den Satzbau.
- **„einkaufszettel" und „augenarzt" blieben klein.** Zusammengesetzte
  Substantive stehen nicht als Stamm im Wörterbuch. Und das sind genau die
  Wörter, auf die es in einem Einkaufszettel oder einem Brief ankommt.

**Damit ist die Sache entschieden:** vier Verfahren, alle zwischen 90 und
92,5 %, und die Fehler wandern nur von einer Wortgruppe zur anderen.
Lexikalisch ist das Problem nicht lösbar.

**Und der Anspruch ist höher als zunächst angenommen** (Stephan,
2026-08-18): In Mail ist Groß- und Kleinschreibung wichtig. Damit fällt
die Idee, Nachrichten wie privaten Chat zu behandeln. Sofort baubar bleibt
nur der Einkaufszettel; für Mail und Briefe ist korrekte Schreibung eine
harte Anforderung.

### Was Debian dafür anbietet: nichts

Geprüft am 2026-08-18: `languagetool`, `python3-spacy` und
`libreoffice-languagetool` sind **nicht in den Quellen**. `python3-nltk`
ist verfügbar (3.9.1-2), löst diese Aufgabe für Deutsch aber nicht. Ein
Werkzeug dafür wäre also ein Fremdpaket - gegen die Linie des Projekts,
bei Debian-Paketen zu bleiben, und deshalb eine eigene Entscheidung und
kein Nebenschritt.

### LanguageTool gemessen (2026-08-18)

Auf Stephans Freigabe heruntergeladen und geprüft. LanguageTool 6.6, dazu
`openjdk-21-jre-headless` 21.0.12 aus **Debians** Quellen - nur
LanguageTool selbst ist ein Fremdpaket.

| Verfahren | Trefferquote |
|---|---|
| Wortliste, nur eindeutige Substantive | 90,6 % |
| Wortliste plus Begleiter-Regel | 92,5 % |
| hunspell statt Wortliste | 90,6 % |
| hunspell -m, Stamm entscheidet | 92,5 % |
| **LanguageTool** | **52/53 = 98,1 %** |

Es trifft genau die Wörter, an denen alle vier lexikalischen Verfahren
gescheitert sind: `einkaufszettel` und `augenarzt` (zusammengesetzt) sowie
`vertrag`, `dank` und `wetter` über eigene Regeln (`VERTRAG_SUBST`,
`DANK_SUBST`, `ART_KLEINES_NOMEN`). Und es lässt „geehrte", „meinen",
„gut", „nächsten" korrekt klein - die vier Wörter, die meine Regeln falsch
großgeschrieben hatten.

**Der einzige Fehler ist „butter".** In „milch butter und" steht kein
Artikel davor, also greift `ART_KLEINES_NOMEN` nicht, und „butter" ist eine
gültige Verbform. **Die Verfahren zu kombinieren würde es
verschlechtern:** Die Stamm-Regel hätte „Butter" richtig, aber „meinen" und
„gut" falsch - 52 − 2 + 1 = 51.

**Ein Messfehler von mir, der die Zahl erst verfälscht hat:** Beim ersten
Durchlauf habe ich alle vier Sätze als **einen** Text ohne Punkte
übergeben. Damit war nur das allererste Wort ein Satzanfang, und
„bitte"/„lieber"/„ich" konnte LanguageTool nicht großschreiben - Ergebnis
92,5 %, also scheinbar kein Fortschritt. Die anderen vier Verfahren hatten
die Satzanfänge selbst erledigt. Satz für Satz übergeben und den
Satzanfang wie überall selbst gesetzt: 98,1 %. **Wer Verfahren vergleicht,
muss ihnen dieselbe Vorarbeit geben.**

**Betriebskosten, gemessen:**

| | |
|---|---|
| Antwortzeit als Dienst | **0,6 bis 1,6 s** je Satz |
| erste Anfrage nach dem Start | 8,8 s - der Dienst muss also laufen, nicht je Satz starten |
| Aufruf ohne Dienst (`languagetool-commandline.jar`) | 9,3 s - für ein Diktat unbrauchbar |
| Arbeitsspeicher des Dienstes | **1213 MB** dauerhaft |
| Platte | 391 MB LanguageTool + 193 MB Java |

**Alles lief örtlich.** Jede Anfrage ging an `http://localhost:8081`; der
öffentliche Dienst von languagetool.org wurde nicht benutzt und darf auch
nie benutzt werden - das wären die Briefe und Mails des Nutzers auf einem
fremden Rechner.

**Was es kostet, ehrlich benannt:** LanguageTool ist das erste Fremdpaket
im Projekt. Es kommt nicht über `apt`, überlebt also keine
Systemaktualisierung von sich aus und muss bei jedem Neuaufbau eines
Geräts mitgedacht werden. 1,2 GB Arbeitsspeicher sind auf dem T490 mit
46 GB unerheblich, auf einem kleineren Gerät nicht.

## Vorschlag: nach Verwendungszweck trennen

Nicht ein Diktat für alles, sondern die Anforderung dort stellen, wo sie
zählt:

| Zweck | Anspruch | Stand |
|---|---|---|
| **Notizen, Einkaufszettel** | Kleinschreibung ist belanglos | sofort baubar |
| **Mail, Chat** | **korrekte Schreibung nötig** - Stephan am 2026-08-18: in Mail ist Groß- und Kleinschreibung wichtig | wartet auf die Entscheidung unten |
| **Briefe** | 10 % Fehler sind nicht zumutbar | braucht eine eigene Entscheidung |

Für Briefe gibt es zwei ehrliche Wege, und beide sind bewusst nicht
heimlich gewählt: LanguageTool als Fremdpaket nachziehen, oder den Brief
vor dem Absenden von einem sehenden Helfer prüfen lassen - die
Fernwartung dafür ist ohnehin Teil des Systems
([sicherheit-datenschutz.md](sicherheit-datenschutz.md)).

## Der erste Lauf mit Stephans Stimme (2026-08-18)

Drei Anläufe, und jeder hat etwas anderes gezeigt. Belegt durch zwei
Protokolle mit Zeitstempeln - `~/.log/dialos-diktat.log` und
`~/.log/dialos-sprachbefehl.log`. (Bis zum 2026-08-22 lagen sie offen im
Heimatverzeichnis.)

**Die Erkennung stimmt.** „tomaten bananen äpfel" wörtlich richtig,
inklusive Umlaut, und über LanguageTool in einer Sekunde zu „Tomaten
Bananen Äpfel" gemacht. Das grosse Modell lädt in 8,8 bis 9,1 s statt der
gemessenen 11,6 - beim zweiten Mal liegt die Datei im
Dateisystem-Zwischenspeicher.

**Der Schlusssatz war der eigentliche Fehler, und zwar meiner.** Ich hatte
„diktat beenden" in der freien Erkennung gesucht. Stephan sagte es, das
Protokoll zeigt:

```
erkannt: 'diktat wird erhöht'
```

Bei freier Erkennung hat das Modell zehntausende Möglichkeiten; ein
BESTIMMTER Satz ist darin nicht zuverlässig zu treffen. **Das war die
dritte Begegnung mit demselben Effekt** - „gnome" wurde zu „genug",
„windows" zu „sinnlose", „beenden" zu „wird erhöht". Zweimal hätte es
gereicht, um daraus die Regel zu ziehen.

**Die Lösung sind zwei Erkenner über demselben Audio:** der grosse für den
Text, ein kleiner mit einer Grammatik aus genau einem Satz für den Schluss.
Kosten: 0,4 s Ladezeit und 229 MB - gegenüber 5,5 GB des grossen Modells
belanglos. Im nächsten Lauf traf er den Satz wörtlich.

**Restrisiko, das dabei sichtbar wurde:** Eine Grammatik mit nur einem Satz
versucht, diesen Satz überall zu hören. Aus „Tomaten Bananen Äpfel" machte
der kleine Erkenner `'beenden beenden [unk]'`. Gestoppt hat er nicht, weil
exakte Übereinstimmung mit `diktat beenden` verlangt wird - aber die
Bedingung ist das einzige, was dazwischen steht. Wer den Schlusssatz je
ändert, muss ihn so wählen, dass er nicht aus Alltagssprache entstehen
kann.

**Die Trennung der Erkenner ist belegt, nicht nur beabsichtigt.** Stephan
hat mitten im Diktat absichtlich „auf Windows umschalten" gesprochen. Der
Satz landete als Text in der Notiz, der Schreibtisch blieb unberührt, und
im Protokoll des Befehlsdienstes steht:

```
14:55:31  Diktat laeuft - ich hoere nicht zu
14:55:45  Diktat beendet - ich hoere wieder zu
```

Zwischen diesen Zeilen kein einziger erkannter Satz.

**Zwei Protokoll-Fehler von mir, beide am selben Tag und beide mit
derselben Ursache.** Beim ersten Test schrieb das Diktat nur ins Terminal -
hinterher war nicht mehr feststellbar, WAS erkannt worden war. Beim zweiten
hatte der Befehlsdienst kein Zeitstempel, also liess sich nicht zeigen, ob
sein erkannter Satz WAEHREND des Diktats kam. **Ein Protokoll ohne Uhrzeit
kann Gleichzeitigkeit nicht belegen** - und genau darum ging es bei dieser
Sperre die ganze Zeit. Beides ist nachgerüstet: Das Diktat protokolliert
immer, der Befehlsdienst mit Uhrzeit.

**Noch offen:** Vosk schneidet eine Äusserung erst an einer Sprechpause.
Ohne Pause landet alles in einer Zeile - im zweiten Lauf wurde aus zwei
Sätzen `'tomaten bananen und äpfel auf sinnlose umschalten'`. Für einen
Einkaufszettel wäre eine Zeile je Eintrag besser. Ob sich das über die
Pausenerkennung steuern lässt oder ob der Nutzer die Pause machen muss, ist
nicht geprüft.

## Piper sprach jedes Mal anders (gefunden 2026-08-18)

Stephan hörte, dass die vorgelesene Notiz nicht zum Tempo der übrigen
Ansagen passt. Die Ursache lag zwei Ebenen tiefer als vermutet, und meine
erste Erklärung war falsch.

**Was ich zuerst annahm:** Kurze Ansagen kommen aus dem Speicher, ein
neuer Satz läuft über speech-dispatcher - also müssten die beiden
sox-Ketten unterschiedliche Tempi rechnen. Die Messung schien das zu
stützen: 2,918 s gegen 2,575 s für denselben Text.

**Widerlegt durch Einzelmessung.** Mit **einer** Piper-Ausgabe durch beide
Ketten geschickt kommt beides bei 2,549 s heraus. `pitch 1.00`, der einzige
Unterschied, ändert die Dauer nicht. Die 13 % kamen also nicht aus den
Ketten - sie kamen daher, dass ich Piper zweimal aufgerufen hatte.

**Die eigentliche Ursache: Piper ist nicht reproduzierbar.** Derselbe Text,
fünf Durchläufe:

```
2,575 s   2,562 s   2,865 s   2,456 s   2,628 s
```

**17 % Streuung**, ohne dass sich eine Einstellung geändert hätte. Piper
benutzt ein VITS-Modell mit einem Zufallsanteil in der Lautdauer
(`--noise_w`, Standard 0.8).

| `--noise_w` | drei Läufe |
|---|---|
| 0 | 2,390 / 2,390 / **2,390 s** |
| 0.4 | 2,470 / 2,351 / 2,430 s |
| 0.8 (vorher) | 2,615 / 2,865 / 2,984 s |

**Entschieden: `--noise_w 0`** (Stephan im Hörvergleich, jede Variante
zweimal hintereinander gespielt, damit die Reihenfolge nicht täuscht).

**Warum das mehr ist als Gleichmäßigkeit:**

- **Der Ansagen-Speicher wird erst dadurch richtig.** Er friert eine
  Ausgabe ein; solange Piper würfelte, klang eine gespeicherte Ansage
  hörbar anders als dieselbe frisch gesprochene. Genau das hat Stephan
  gehört. Nachgeprüft nach der Änderung: Speicher-Datei 0,939 s, frisch
  erzeugt 0,939 s - auf die Millisekunde gleich.
- **Alle Sprechdauer-Messungen dieses Projekts waren Stichproben, keine
  Zahlen.** „1,13 s für ‚Ich höre.'" hatte eine unbekannte Streuung von bis
  zu 17 %. Erst jetzt ist ein Vergleich zwischen zwei Einstellungen
  überhaupt aussagekräftig.
- **Nebeneffekt: rund 12 % kürzere Ansagen** ohne Eingriff ins Tempo.
  „Ich höre." fiel von 1,13 s auf 0,939 s.

**Der Schalter muss an ZWEI Stellen stehen** - in `piper-generic.conf` und
in der Speicher-Kette von `dialos-say.py`. Stehen sie auseinander, klingt
gespeichert wieder anders als frisch. Der Speicher entwertet sich bei einer
Änderung von selbst, weil sein Schlüssel die Änderungszeit von
`piper-generic.conf` enthält.

**Eine Messung, die ich als untauglich verworfen habe:** Auf die Frage, ob
es innerhalb eines Satzes schneller wird, habe ich die Wortdauern der
ersten gegen die zweite Satzhälfte gemittelt. Das Ergebnis (zweite Hälfte
3 bis 35 % langsamer) ist wertlos, weil die Wörter unterschiedlich lang
sind - „ich" gegen „Kartoffeln". Es belegt weder das eine noch das andere.

## Satzzeichen

Ungelöst und noch nicht gemessen. Der klassische Weg sind gesprochene
Satzzeichen („Komma", „Punkt", „Absatz"), die der Nutzer lernen muss. Zu
prüfen ist, ob sie sich zuverlässig von gleichlautenden Wörtern im Text
trennen lassen - „Punkt" kann auch ein Wort im Satz sein.

## Nach dem Diktat: Hinweis statt Vorlesen (Stephan, 2026-08-19)

Bis zum 2026-08-19 las „Diktat beenden" die fertige Notiz komplett vor. Das
klang nach Sorgfalt, war aber ein Fehler in zwei Richtungen:

1. **Es machte „Einkaufszettel vorlesen" überflüssig.** Ein Befehl, der schon
   von selbst passiert, braucht niemand.
2. **Es nahm dem Nutzer die Wahl.** Wer drei Waren aufschreibt, will sie nicht
   dreimal hören. Wer zwanzig diktiert hat, will es vielleicht doch.

Seitdem bestätigt DialOS und sagt, **wie** man das Vorlesen bekommt:

> „Diktat beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel
> vorgelesen haben, dann sage: Einkaufszettel vorlesen."

**Warum die Anzahl drin bleibt.** Sie ersetzt das Vorlesen: Sie ist das
einzige, woran ein blinder Nutzer merkt, dass überhaupt etwas angekommen ist -
und wie viel. Ein bloßes „Diktat beendet." ließe ihn im Dunkeln.

**Warum ein Hinweis und keine Rückfrage.** Eine Rückfrage („Soll ich
vorlesen?") verlangt eine Antwort und hält das Gerät auf, bis sie kommt. Ein
Hinweis kostet nichts, wenn man ihn nicht braucht.

**Warum der Hinweis aus einer Tabelle kommt.** Genannt werden nur Ziele, für
die es den Vorlese-Befehl wirklich gibt (`einkaufszettel`, `notizen` - siehe
`docs/sprachbefehle.md`). Ein späteres Ziel wie „brief" bekommt vorerst nur
die Bestätigung. Einem blinden Nutzer einen Satz zu nennen, den die Grammatik
nicht kennt, wäre schlimmer als kein Hinweis: er würde ihn sagen, nichts
würde passieren, und er hätte keine Möglichkeit herauszufinden warum.

Das Vorlesen **mit Satzzeichen** lebt unverändert in `dialos-notiz.py` weiter,
wo es auf Ansage geschieht. Die dort gemessene Begründung gilt weiter: 3,670 s
ohne gegen 4,884 s mit Satzzeichen, und der Unterschied besteht ausschließlich
aus Pausen.

## Ein Eintrag pro Ware - und wie der Nutzer das erfahren soll (2026-08-19)

**Der Fehler, wie er sich zeigte.** Stephan diktierte „Milch sechs Eier
Butter" in einem Zug, dreimal in drei Tests. Danach klagte er über zwei Dinge:
Michael habe „3x die Liste vorgelesen" und sei „wieder zu schnell" gewesen.

Beides war dieselbe Ursache, und keines der beiden war ein Fehler im
Vorlesen. Im Zettel standen wirklich drei Zeilen - je eine pro Test:

```
Milch sechs Eier butter
Milch sechs Eier butter
Milch sechs Eier butter
```

DialOS las korrekt „3 Einträge" vor. Nur war jeder Eintrag der ganze Einkauf.
**Vosk liefert eine in einem Atemzug gesprochene Folge als EINE Äußerung, und
eine Äußerung ist ein Eintrag.** Und weil die Pause zwischen Einträgen sitzt
und nicht innerhalb, kam jede Zeile in einem Zug heraus - genau das, was
Stephan als „zu schnell" hörte.

**Was daran nicht kaputt war.** Der Mechanismus funktioniert: Wer zwischen den
Waren eine kleine Pause macht, bekommt drei Äußerungen und damit drei
Einträge. Es fehlte nichts am Programm - es fehlte, dass DialOS es **sagt**.

**Die Lehre, und sie gilt über das Diktat hinaus:** Wo der Nutzer das Ergebnis
nicht sehen kann, ist eine Bedienregel wertlos, solange sie ungesagt bleibt.
Ein sehender Nutzer hätte nach der ersten Ware bemerkt, dass eine einzige
Zeile entsteht, und von selbst anders gesprochen. Ein blinder erfährt es erst
beim Vorlesen - eine Minute später und zu spät.

Deshalb sagt DialOS es beim Einkaufszettel jetzt am Anfang:

> „Ich schreibe mit. Sage jede Ware einzeln, mit einer kleinen Pause
> dazwischen."

Ein Satz, nicht drei - während DialOS spricht, hört es nicht zu. Und nur beim
Einkaufszettel: bei einer Notiz oder einem Brief ist eine Äußerung tatsächlich
ein Satz und die Anleitung wäre falsch.

**Rückfallebene für den, der es trotzdem in einem Zug sagt.** „Milch **und**
sechs Eier **und** Butter" wird an „und" getrennt - so spricht man eine
Einkaufsliste ohnehin. Bewusst nur bei Listen-Zielen (`LISTEN_ZIELE`): in
einem Brief würde aus „Ich habe Milch und Butter gekauft" sonst zwei Zeilen.

Jeder getrennte Eintrag fängt groß an. Die Schreibhilfe hat die Äußerung als
**einen** Satz gesehen und nur das erste Wort großgeschrieben; ohne
Nachbesserung stünde „Milch / sechs Eier / Butter" im Zettel - und den Zettel
liest ein sehender Helfer auch.

**Was damit nicht gelöst ist:** „Milch sechs Eier Butter" ohne „und" und ohne
Pause bleibt ein Eintrag. Zuverlässig zerlegen ließe sich das nur über die
Wort-Zeitstempel, die Vosk mit `SetWords(True)` mitliefert - eine Lücke von
mehr als etwa 0,4 s zwischen zwei Wörtern wäre eine Trennstelle, auch wenn sie
für das Ende einer Äußerung zu kurz ist. Ungemessen und deshalb in `TODO.md`,
nicht hier als gelöst.

## Die erste Korrektur jeder Sitzung war ein Münzwurf (2026-08-19)

Am 2026-08-19 stand im Diktat-Protokoll:

```
10:02:53    erkannt:     'milch sechs eier butter'
10:03:03    (LanguageTool nicht erreichbar: timed out)
10:03:03    geschrieben: 'Milch sechs eier butter'
```

Zehn Sekunden zwischen Erkennung und Ausgabe - genau die Zeitgrenze. Gemessen,
nachdem der Dienst neu gestartet wurde:

| Anfrage | Dauer |
|---|---|
| `/v2/languages` - **das** prüft `lt_lebt()` als „läuft" | **1,3 s** |
| erste `/v2/check`-Anfrage - hier laden die deutschen Regeln | **9,2 s** |
| zweite `/v2/check`-Anfrage | 1,0 s |
| Zeitgrenze im Diktat (`LT_ZEITGRENZE_S`) | 10,0 s |

**9,2 s gegen 10,0 s.** Die erste Korrektur jeder Sitzung hing an 0,8 Sekunden,
und an diesem Morgen hat sie verloren. Danach lief alles - jede weitere Anfrage
kostet rund eine Sekunde, und im Protokoll blieb ein einmaliger Ausfall zurück,
der wie ein Zufall aussah.

**Warum das niemandem auffiel:** `lt_lebt()` fragt `/v2/languages`. Der
Endpunkt antwortet nach 1,3 s und lädt keine Regeln - der Dienst meldet also
„läuft", während er auf die erste echte Anfrage noch neun Sekunden braucht. Eine
Bereitschaftsmeldung, die etwas anderes prüft als das, worauf es ankommt.

**Der frühere Schluss war unvollständig, nicht falsch.** Die Unit dokumentiert
seit dem 2026-08-18 „der erste Aufruf kostet 8,8 s" und zog daraus „dann eben
ein Dauerdienst". Ein Dauerdienst **verschiebt** die Ladezeit aber nur auf die
erste Prüfanfrage, statt sie zu beseitigen.

**Behoben an der Wurzel:** `dialos-schreibhilfe-warmlaufen.py` läuft als
`ExecStartPost` der Unit und schickt einmal einen echten Satz durch. Die neun
Sekunden fallen damit beim Anmelden an, wo niemand darauf wartet. Das `-` vor
dem `ExecStartPost` macht ein Scheitern unschädlich: Ein nicht warmgelaufener
Dienst ist besser als keiner, und `Restart=on-failure` darf deswegen nicht in
eine Schleife geraten.

## Wie gut die Groß-/Kleinschreibung wirklich ist (gemessen 2026-08-19)

Gemessen mit `schreibung_richten()` selbst, nicht mit einer Nachbildung -
**10 von 11** Fällen richtig:

| Diktiert | DialOS schreibt |
|---|---|
| `milch` | Milch |
| `butter` | Butter |
| `sechs eier` | Sechs Eier |
| `zwei liter milch` | Zwei Liter Milch |
| `kaffee und brot` | Kaffee und Brot |
| `sehr geehrte damen und herren` | Sehr geehrte Damen und Herren |
| `hiermit kündige ich meine mitgliedschaft zum nächstmöglichen termin` | Hiermit kündige ich meine Mitgliedschaft zum nächstmöglichen Termin |
| `ich rufe morgen den arzt an` | Ich rufe morgen den Arzt an |
| `der termin ist am dienstag` | Der Termin ist am Dienstag |
| `bitte den vertrag mitbringen` | Bitte den Vertrag mitbringen |
| `milch sechs eier butter` | Milch sechs **e**ier butter ← **falsch** |

**Der einzige Fehlschlag ist eine Wortliste ohne Grammatik.** LanguageTool kann
dort nicht entscheiden, was Substantiv ist - es fehlt der Satz drumherum.
Einzeln geht jedes dieser Wörter richtig, und einzeln kommen sie seit dem
2026-08-19, weil beim Einkaufszettel jede Ware ein eigener Eintrag ist.

**Damit ist die Schreibung bei Briefen und Mails belastbar** - dort sind es
ganze Sätze. Eine frühere Einschätzung, die Schreibung sei der dringendste
offene Punkt, ist damit zurückgenommen: Der dringendere war die Ladezeit
darüber.

## Gesprochene Satzzeichen (2026-08-21)

Vosk liefert Wörter, keine Zeichen. Für einen Einkaufszettel belanglos, für
einen Brief das Ende der Brauchbarkeit. Der Nutzer spricht sie deshalb aus:

| gesagt | wird zu |
|---|---|
| **Komma setzen** | `,` |
| **Punkt setzen** | `.` |
| **Fragezeichen setzen** | `?` |
| **Ausrufezeichen setzen** | `!` |
| **Doppelpunkt setzen** | `:` |
| **Gedankenstrich setzen** | ` - ` |
| **neuer Absatz** | Leerzeile |
| **neue Zeile** | Zeilenumbruch |

*Der erste Entwurf benutzte die nackten Wörter („Komma", „Punkt"). Warum daraus
zweiwortige Merkwörter wurden, steht weiter unten unter „Gesprochene
Satzzeichen tragen nur zum Teil" - kurz: gemessen wurden die kurzen Wörter
nicht zuverlässig erkannt.*

**Alle neun stehen im Wortschatz** des grossen Modells - geprüft in
`graph/words.txt` mit 822 389 Einträgen. Diese Prüfung war Pflicht: Bei
„löschen" hatte genau das gefehlt, und der Befehl wäre still nie ausgelöst
worden.

**Und die naheliegende Prüfmethode trägt hier nicht.** Der Weg über eine
eingeschränkte Grammatik, der beim kleinen Modell fehlende Wörter meldet,
liefert beim grossen ein leeres Versprechen: Es nimmt gar keine Grammatik an
(`Runtime graphs are not supported by this model`) und meldet deshalb auch
nichts. Neun Wörter sahen „vorhanden" aus, geprüft worden war nichts. Erst die
Wortliste des Modells gibt eine Antwort.

**Immer als Satzzeichen** (Stephans Entscheidung). Der Preis: „in diesem Punkt"
wird zu „in diesem." Das fällt beim Vorlesen auf, und die Stelle wird neu
diktiert. Die Alternative wäre gewesen, nur bei einer Sprechpause zu trennen -
Vosk liefert Wortzeitstempel -, aber dann bekäme, wer flüssig diktiert, gar
keine Satzzeichen.

**Ersetzt wird wortweise, nicht per Textsuche.** Sonst hätte es „Punkte",
„Kommando" und „Absatzweise" mitgetroffen, und der Text zerfiele an Stellen,
an denen niemand ein Satzzeichen gesagt hat.

### Was Satzzeichen für die Schreibung bringen - gemessen

Die Vermutung war, LanguageTool entscheide mit Satzzeichen die Grossschreibung
besser. **Für die Substantive stimmt das nicht:** „Damen", „Herren",
„Vertrag", „Termin", „Kündigung", „Grüßen" kamen mit und ohne Zeichen gleich
heraus. Was Satzzeichen bringen, sind die **Satzanfänge**:

```
ohne:  ... schriftlich mit freundlichen Grüßen
mit:   ... schriftlich. Mit freundlichen Grüßen
```

In einem Brief ist das kein Schönheitsfehler, sondern falsch. Deshalb laufen
die Satzzeichen **vor** LanguageTool. Listen bleiben aussen vor - auf einem
Einkaufszettel wäre „Butter." keine Verbesserung.

## Stille erzeugt Text - das Pegel-Tor (gemessen 2026-08-21)

Das große Modell **erfindet in Stille Wörter**. Gemessen mit Stephans Mikrofon
in 80 Sekunden Ruhe: sieben Stück - `köln`, `einen gefunden`, `vom`, `ln`,
`einen`, `nun`, `schon`. Im Diktat landen die im Text. Wer beim Diktieren
nachdenkt, bekommt „köln" mitten in seine Kündigung geschrieben. Das betrifft
**jedes** Diktat; beim Einkaufszettel dürfte es bisher als falsch verstandene
Ware durchgegangen sein.

Die Messung des Mittelpegels je erkannter Äußerung trennt sauber:

| Äußerung | Spitze | Mittel |
|---|---|---|
| `'köln'` (Rauschen) | 601 | **71** |
| `'nun'` (Rauschen) | 1265 | **84** |
| `'einen'` (Rauschen) | 528 | **47** |
| `'sechsundzwanzig'` (leise gesprochen) | 2383 | **350** |
| ganze Sätze | 11606-13447 | **3475-4196** |

**Die Schwelle liegt bei 150** - das Doppelte des lautesten gemessenen
Rauschens und weniger als die Hälfte der leisesten echten Äußerung.

**Geprüft wird am Ergebnis, nicht am Audiostrom.** Ein Tor, das leise Blöcke
gar nicht erst durchlässt, zerschneidet Wörter: Zwischen zwei Silben ist es
still. Am fertigen Ergebnis zu prüfen kostet nichts und kann nichts zerteilen.

**Dieselbe Prüfung schützt den Schlusssatz** - allerdings nicht so weit, wie
ich zunächst annahm. Ich hatte sie für den besten Verdacht bei der ungeklärten
Selbstbeendigung gehalten. **Der nächste Test hat das widerlegt:** Ein Diktat
beendete sich erneut von selbst, nach 4,2 s, und das Pegel-Tor griff nicht -
das Geräusch war laut genug. Was die neue Protokollzeile dabei verriet, steht
im nächsten Abschnitt.

## Ein nacktes „beenden" vor der ersten Äußerung ist kein Schluss

Zweimal am 2026-08-21 beendete sich ein Diktat von selbst, beide Male mit
**0 Äußerungen davor** - einmal nach 6 s, einmal nach 4,2 s. Beim zweiten Mal
griffen weder die Sperrfrist von 3 s noch das Pegel-Tor.

Der Hinweis steckte in der Zeile, die für genau diesen Zweck eingebaut worden
war: Die **freie Erkennung lieferte in derselben Zeit nichts**, der
Schluss-Erkenner aber „beenden". Dieselbe Audiospur, zwei Erkenner, zwei
Ergebnisse. Das ist die eingeschränkte Grammatik: Sie **muss** jedes Geräusch
auf eine ihrer Phrasen abbilden, und der `[unk]`-Auffang gewinnt nicht immer.

Die erste Antwort darauf war eine Sonderregel: ein nacktes „beenden" **vor der
ersten Äußerung** verwerfen. Sie hat einen Tag gehalten.

### Ausgezählt - und deshalb verlangt der Schluss jetzt beide Wörter

Alle Schluss-Ereignisse des 2026-08-21:

| | nacktes „beenden" | volles „diktat beenden" |
|---|---|---|
| **falsch** ausgelöst | **6×** | 0× |
| **echt** vom Nutzer | 3× | 2× |

**Jeder einzelne Fehlauslöser war ein nacktes „beenden".** Einmal machte der
Erkenner aus einem Bruchstück von Stephans Diktat ein „beenden", **während er
den Brief sprach**. Die Sonderregel rettete ihn dort zufällig - es war noch
nichts abgeschlossen. Sobald ein Satz angekommen ist, hätte dasselbe
Bruchstück ihn mitten im Brief gestoppt.

Der Folgeschaden war sichtbar: Stephan hielt das Diktat für beendet, sagte
„Brief vorlesen" - und **das landete im Brieftext**.

**Warum es vorher anders entschieden war:** Am 2026-08-18 lieferte der
Schluss-Erkenner in sieben Minuten Dauergerede nur zweimal etwas anderes als
`[unk]`, beide Male ein echtes „beenden". Daraus wurde „es genügt das Wort".
Diese Messung hat aber nie geprüft, was beim **Diktieren** passiert - und
genau dort entstehen die Bruchstücke.

Der Preis ist gering: Der volle Satz wurde am selben Tag zweimal sauber
erkannt. Und wird er einmal nicht erkannt, **sagt DialOS es**: „Sage bitte:
Diktat beenden.", höchstens alle 15 Sekunden, damit die Ansage nicht selbst
zum Geräusch wird und ins Mikrofon läuft. Der Nutzer spricht nie wieder ins
Leere, ohne es zu merken - das war der eigentliche Schaden der alten Regel.

Damit entfällt auch die Sonderregel „noch nichts diktiert" - ein Flickwerk
weniger.

**Jede verworfene Äußerung wird protokolliert.** Fällt dort echte Sprache
hinein, sieht man es sofort, und die Schwelle gehört nach unten.

## Gesprochene Satzzeichen tragen nur zum Teil (gemessen 2026-08-21)

Nach dem Einbau gemessen, erst mit Piper, dann mit Stephans Stimme:

| gesagt | Piper hört | Stephan spricht, Vosk hört |
|---|---|---|
| „…Herren **Komma**" | ✅ | `komme` ✗ |
| „…Herren *(Pause)* **Komma**" | `komme` ✗ | ✅ |
| **„Komma"** allein | `ja` ✗ | `einen koffer` ✗ |
| „…Vertrag **Punkt**" | ✅ | ✅ |
| **„Punkt"** allein | `das` ✗ | `kommt` ✗ |
| **„neuer Absatz"** | ✅ | ✅ |
| **„Doppelpunkt"** allein | `dörte depots` ✗ | - |

**Drei von sechs bei Stephans Stimme.** Das Muster ist nicht die Aussprache
und nicht die Pause - bei Piper klappte genau das Gegenteil. Es ist das
Sprachmodell: Es rät aus dem Zusammenhang, und bei kurzen Wörtern rät es
falsch. Durchgehend scheitern die **allein stehenden kurzen Wörter**;
durchgehend trägt **„neuer Absatz"**, zwei Silben mehr und ohne
Verwechslungsmöglichkeit.

Das ist dieselbe Lektion wie beim Einschalten der Sprachsteuerung: Ein
Merkwort muss **eindeutig und lang genug** sein. „Komma" und „Punkt"
kollidieren mit „komme", „kommt", „Koffer", „das", „ja" - allesamt Wörter, die
in einem Brief vorkommen. **Offen** ist damit, ob längere Merkwörter („Komma
setzen", „neuer Satz") den Fall lösen.

### Gelöst mit zweiwortigen Merkwörtern (zweite Messung, 2026-08-21)

Dieselbe Stimme, dieselbe Kette, die längeren Formen:

| gesagt | gehört | |
|---|---|---|
| „…Rößner **Komma setzen**" | `komma setzen` | ✅ |
| „…Vertrag **Punkt setzen**" | `punkt setzen` | ✅ |
| „…helfen **Fragezeichen setzen**" | `fragezeichen setzen` | ✅ |
| „**neuer Satz**" | `neuer ersatz` | ✗ |
| „…Rößner **Komma**" *(Vergleich)* | `komma` | ✅ **diesmal** |

**Dreimal von drei.** „neuer Satz" wurde deshalb nicht aufgenommen.

Das nackte „Komma" traf hier, nachdem es zweimal gescheitert war - und genau
das ist der schlechteste Fall: Der Nutzer merkt sich, dass es geht, und dann
geht es doch nicht.

**Die nackten Formen sind deshalb entfernt**, und das ist ein doppelter
Gewinn: Die Erkennung wird zuverlässig, **und** der anfangs akzeptierte Preis
entfällt. „In diesem Punkt", „drei Punkte" und „ein Komma an dieser Stelle"
bleiben unangetastet, weil nur „Punkt **setzen**" ein Zeichen erzeugt.

## Was nach der letzten Sprechpause kam, ging verloren (2026-08-21)

**Der schwerste Fehler des Tages, und er war von Anfang an da.** Vosk sammelt
Audio und liefert erst an einer Sprechpause ab. Wer einen Brief **in einem
Zug** spricht und danach „Diktat beenden" sagt, hat beides in **derselben**
Pause: Der Schluss-Erkenner bricht die Schleife ab, bevor die freie Erkennung
ihren angesammelten Text abliefern konnte. `FinalResult()` wurde nie
aufgerufen - der Text war weg.

Im Protokoll stand `0 Aeusserungen`, obwohl ein ganzer Brief gesprochen worden
war. Zweimal habe ich daraus die falschen Schlüsse gezogen und an anderen
Stellen gesucht.

**Warum es nie aufgefallen ist:** Beim Einkaufszettel macht man zwischen den
Waren Pausen. Jede Ware wird für sich abgeschlossen, und nach der letzten
Pause kam meist nichts mehr. Erst der Brief, den man am Stück spricht, macht
den Fehler sichtbar.

Behoben: Nach der Schleife wird `FinalResult()` geholt und **denselben Weg**
geschickt wie jede andere Äußerung - Satzzeichen, Schreibung, Zerlegung. Die
Schlussworte werden dabei abgeschnitten, denn die freie Erkennung hört „Diktat
beenden" mit, und das gehört nicht in den Brief.

## Der Schluss braucht eine Sprechpause (2026-08-22, offline geprüft)

Vier Reparaturen an einem Nachmittag haben es nicht dicht bekommen -
Sperrfrist, Pegel-Tor, beide Wörter verlangen, Ansage. Jedes Mal fand der
nächste Test die nächste Lücke, und einmal brach Stephans Diktat nach
12,1 Sekunden mitten im Satz ab. Sein Urteil war das Maß: **„Diesen Text kann
ich nie zu Ende bringen."**

**Der Unterschied, den es wirklich gibt:** Ein echtes „Diktat beenden" kommt,
*nachdem* der Nutzer mit dem Text fertig ist - davor liegt eine Pause. Jedes
Bruchstück entsteht mitten im Redefluss, wo es keine gibt. Genau das schützt
den Einkaufszettel seit jeher, ohne dass es jemand geplant hätte: „Milch."
Pause. „Butter." Pause.

Die Regel: In den letzten **5 Sekunden** muss eine zusammenhängende Ruhephase
von mindestens **0,4 Sekunden** gelegen haben. Umgesetzt als reine Funktion
`pause_davor()` - ohne Uhr, ohne Mikrofon, damit sie gegen aufgezeichnete
Fälle prüfbar ist.

### Offline geprüft, bevor jemand sprechen musste

`scripts/dialos-schlussregel-pruefen.py` lässt Piper sprechen und schickt das
Ergebnis durch den **echten** Code - `ist_schluss()`, `pause_davor()` und die
Pegelschwelle kommen aus `dialos-diktat.py`, nicht aus einer Nachbildung.

| Fall | Ergebnis |
|---|---|
| **A** durchgehende Rede, kein Schlusssatz | 2 vollständige `'diktat beenden'` entstanden - **beide abgewiesen**, kein Schluss |
| **B** dieselbe Rede, Pause, dann „Diktat beenden" | dieselben zwei abgewiesen, der echte bei 21,4 s **angenommen** |

Bemerkenswert an Fall A: Aus reiner Rede entstanden **zwei vollständige**
Schlusssätze. Die hätten die Zwei-Wort-Regel vom Vortag passiert - die
Sprechpause weist sie ab.

### Wie kurz darf die Pause sein?

Gemessen mit eingefügten Pausen von 0,0 bis 1,5 Sekunden: **alle wurden
erkannt.** Der Grund ist lehrreich - Piper macht nach einem Satzpunkt von
selbst eine Atempause. Die Regel greift also nicht an einer künstlich
eingefügten Stille, sondern an der **natürlichen Satzgrenze**. Für den Nutzer
heißt das: Er muss nichts anders machen als bisher.

**Was sie nicht kann:** Ein Bruchstück, das zufällig direkt nach einer
Sprechpause entsteht, kommt weiterhin durch. Zusammen mit den drei anderen
Bedingungen - beide Wörter, Pegel über der Schwelle, nicht in den ersten drei
Sekunden - ist das Restrisiko klein, aber es ist nicht null. Der Beweis dafür
steht noch aus: ein Diktat mit echter Stimme, das von Anfang bis Ende durchläuft.
