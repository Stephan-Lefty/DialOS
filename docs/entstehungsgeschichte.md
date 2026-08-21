[Deutsch](entstehungsgeschichte.md) | [English](entstehungsgeschichte.en.md)

# Dreizehn Tage und mehr …

*Die Entstehung von DialOS, vom 6. bis 21. August 2026. 261 Commits.
Erzählt als das, was es war.*

Alles hier ist belegt - im Änderungsprotokoll in [../README.md](../README.md),
in den Protokolldateien, in der Git-Historie. Es ist nichts hinzugefügt.
Zugespitzt ist nur die Form.

---

## Der Gegenspieler

Jeder Thriller braucht einen, und dieser hat einen guten. Es ist kein
Fehler. Es ist ein Prinzip:

**Ein System, das Erfolg meldet, während es versagt.**

Er tritt bisher siebenmal auf, jedes Mal in anderer Verkleidung, und jedes
Mal glaubt ihm jemand. Meistens ich.

Am letzten Tag trägt er meine eigene.

---

## Tag 1: Die Anforderung, die keinen Rückweg lässt

**6. August, 14:15 Uhr.** Erster Commit. Zwanzig folgen an diesem Tag.

Die Aufgabe klingt harmlos: ein Betriebssystem für blinde und motorisch
eingeschränkte Nutzer, vollständig per Sprache bedienbar. Debian, GNOME,
freie Software.

Der Satz, der alles Weitere bestimmt, steht nicht in der Anforderung. Er
ergibt sich aus ihr: **Der Nutzer kann nicht nachsehen.** Kein Blick auf den
Bildschirm, kein Fenster, das man kurz aufmacht, keine Fehlermeldung, die
man liest. Was das System nicht sagt, existiert für ihn nicht.

Damit wird jede stille Fehlfunktion zur Katastrophe. Und stille
Fehlfunktionen sind die Spezialität des Gegenspielers.

---

## Tage 1 bis 9: Der falsche Weg, achtzehnmal

Der Plan ist vernünftig: eine Live-ISO bauen, automatisiert, in Docker.
`live-build` in einem Container, reproduzierbar, ein Befehl.

**Rund achtzehn Bauversuche.** Keiner liefert eine fertige `.iso`. Nicht
einer.

Praktisch jeder Fehler geht auf dieselbe Ursache zurück - verschachteltes
`live-build` in Docker in einer Sandbox -, und jeder sieht aus wie ein
anderes Problem. Man behebt einen und findet den nächsten. Die Pipeline
meldet Fortschritt. Sie kommt nie an.

Der Ausweg ist kein technischer, sondern eine Entscheidung: **Debian direkt
auf echter Hardware installieren.** Ein ThinkPad T490, von Hand aufgesetzt,
Schritt für Schritt dokumentiert. Die `iso-build/`-Dateien bleiben als
Rezept.

Es ist der erste Moment, in dem jemand sagt: Wir haben in die falsche
Richtung gearbeitet. Es wird nicht der letzte sein.

Gleichzeitig fällt ein zweiter Entwurf. Die Verschlüsselung sollte die
ganze Platte umfassen. Am 14. August wird das ersetzt: **nur die Daten des
Nutzers**, in einer eigenen LUKS-Partition, und ein USB-Stick, der sie
freigibt. Ohne Stick bleiben sie zu. Der Rest bootet normal.

Und ein ganzer Installer - Calamares, Branding, Overlays, ein
Klon-Skript - wird gebaut und dann **vollständig gelöscht**. Er existierte
nur für einen Weg, den es nicht mehr gibt.

---

## Tag 8: Sechzig Dezibel

**13. August.** Ein Mikrofon-Vergleich. Das eingebaute gegen ein
Bluetooth-Headset. Das Ergebnis ist eindeutig: eingebaut deutlich
schlechter.

Die Entscheidung fällt zugunsten von Bluetooth. Sie prägt die nächsten
Tage - die Hardware-Auswahl, die Kaufüberlegungen, das ganze Audio-Konzept.

**16. August.** Beim Suchen nach etwas anderem fällt eine Zahl auf. Am
eingebauten Mikrofon des T490 stehen zwei Verstärkungsstufen auf Anschlag.
`Capture` auf +30 dB. **Und zusätzlich** `Internal Mic Boost` auf +30 dB.

Sechzig Dezibel. Ab Werk.

Was das bedeutet, ist schlimmer als schlechte Qualität. Vosk erkennt
Sprache an den **Pausen zwischen den Wörtern**. In einem Dauervollausschlag
gibt es keine Pausen. Also kam nie ein Ergebnis.

Ohne Fehlermeldung. Das Mikrofon war da. Es lieferte Daten. Der Erkenner
lief. Alles meldete Erfolg, und es kam nie etwas an.

Und die Entscheidung vom 13. August? **Sie hat möglicherweise nie das
Mikrofon gemessen, sondern nur die Übersteuerung.** Drei Tage
Hardware-Überlegungen ruhen auf einem Vergleich, der nicht mehr gilt. Der
Punkt steht bis heute in [../TODO.md](../TODO.md): wiederholen.

**16. August, 58 Commits.** Der dichteste Tag. Alles wird auf echter
Hardware gebaut, geprüft, dokumentiert. Am Abend hat DialOS seinen ersten
echten Sprachbefehl: der Schreibtisch schaltet auf Zuruf zwischen GNOME und
einem Windows-11-Nachbau um.

Es funktioniert. Live, mit Stephans Stimme.

---

## Tag 12: Die Maschine schaltet sich selbst zurück

**17. August.** Der Sprachbefehl läuft. Stephan sagt „auf Windows
umschalten". Der Schreibtisch wechselt.

Fünfzehn Sekunden später wechselt er zurück. Von selbst.

Niemand hat etwas gesagt.

Die Erklärung ist keine Logik, sondern Arithmetik. `parec` liefert bei
16 kHz mono 16 Bit rund **32.000 Bytes pro Sekunde**. Der Dienst verwarf,
während das System sprach, 4.000 Bytes und schlief dann 0,3 Sekunden -
also **13.000 pro Sekunde**.

Er leerte die Warteschlange langsamer, als sie sich füllte.

Nach einer achtsekündigen Ansage standen fünf Sekunden **eigene Stimme** in
der Pipe. Die wertete er anschließend ganz normal aus. Und weil die
Grammatik auf drei Sätze beschränkt ist, presste sie das Bruchstück in
einen Befehl.

Das System hörte sich selbst zu und gehorchte sich selbst. Die
Schutzmarkierung „ich spreche gerade" war vorhanden und hat funktioniert -
sie verhinderte das **Zuhören**, nicht das **Aufzeichnen**.

Behoben, indem die Aufnahme nach jedem Sprechen verworfen und neu begonnen
wird. Ein frischer Prozess hat keinen Rückstand.

---

## Tag 12, später: Vier Anzeiger lügen gleichzeitig

**17. August, nachmittags.** Ein Neustart. Danach kommt bei **beiden**
Benutzerkonten keine Ansage. Kein Ton. Nicht über Bluetooth, nicht über die
eingebauten Lautsprecher. Nichts.

Das Sprech-Symbol erscheint in der Leiste. Es kommt nichts.

Was die Anzeiger sagen:

- BlueZ: `Connected: yes`, Akku 100 %.
- `pactl`: die Senke ist da, Zustand `RUNNING`.
- ALSA für das Aufnahmegerät: `state: RUNNING`.
- Das Headset selbst, auf Nachfrage: verbunden.

Was tatsächlich ankommt: **0 Bytes in 3 Sekunden.**

Die Ursache ist eine Testkonfiguration von mir, die einen Neustart
überlebt hat. Die Echo-Unterdrückung hing an Stephans USB-Headset. Das
Headset war aus. Der Dongle meldet trotzdem eine Soundkarte.

Und weil das Modul diese Aufnahme als **Taktgeber** braucht, startete
PipeWire den Graph nicht. Die Soundkarte blieb auf `state: PREPARED` stehen,
`trigger_time: 0.000000000`, `hw_ptr: 0`. Jede Wiedergabe hing für immer.

Beim Suchen habe ich zuerst „PipeWire ist gesund" gemeldet, weil das Modul
geladen war und die Senke `RUNNING` zeigte. Dann `webrtc.gain_control`
verdächtigt, das am selben Tag geändert worden war. Beides falsch. Erst ein
Reihentest über die Zielgeräte zeigte es.

Was ein blinder Nutzer erlebt hätte: kein Ton, keine Fehlermeldung, nur
Ansagen, die sich stapeln - beim Vorfall drei Sprachausgaben und vier
GNOME-Klänge, alle in der Warteschlange. Für ihn ist das nicht „der Ton ist
weg". Für ihn ist das Gerät kaputt.

Die Regel, die daraus wurde, steht seitdem in
[../CLAUDE.md](../CLAUDE.md): **Keiner Zustandsmeldung glauben, wenn sich
das Ergebnis messen lässt.** DialOS prüft Ausgabegeräte jetzt, indem es
150 Millisekunden Stille hinschickt und schaut, ob der Aufruf durchläuft.

---

## Tag 12, abends: „Ich muss lauter reden"

Zweimal an diesem Tag meldet Stephan, er müsse sehr laut sprechen. Zweimal
suche ich am Pegel.

Beide Male ist es eine Zeitspanne, in der das System nicht zuhört.

Das erste Mal: Nach der Ansage „Ich höre." setzte der Dienst eine Sperrfrist
von fünf Sekunden - dieselbe, die nach einem echten Umschalten sinnvoll ist.
Er war also **genau in den fünf Sekunden taub, in denen der Nutzer seinen
Befehl sagt.** Stephan sprach, nichts geschah, er wiederholte lauter, und
dann war die Frist abgelaufen und es klappte.

Aufgeklärt hat es nicht meine Suche, sondern seine Präzisierung: *„Den
**zweiten** Befehl musste ich wesentlich lauter ins Mikro brüllen."* Der
erste ging normal. Damit war klar, dass es keine Frage der Lautstärke war,
sondern der Reihenfolge.

Das zweite Mal, Tage später, dieselbe Ursache an anderer Stelle: nach einem
Umschalten war der Dienst **5,1 Sekunden** taub, während die Ansage schon
nach 1,5 Sekunden endete. Der Nutzer hört die Antwort und redet 3,6
Sekunden gegen ein taubes System.

Am Morgen hatte ich die Begründung dafür selbst aufgeschrieben - und dann
nur die halbe Stelle behoben.

Seitdem steht in [sprachsteuerung.md](sprachsteuerung.md): **„Ich muss
lauter reden" führt als Fehlerbeschreibung fast immer in die Irre.** Die
Frage, die es aufklärt, ist nicht *wie laut*, sondern **welcher** Befehl in
der Reihe nicht ankam.

---

## Tag 13: Der unzuverlässige Erzähler

**18. August.** Das Diktat funktioniert. Freie Erkennung, großes Modell,
Schreibkorrektur. Stephan diktiert einen Einkaufszettel, das System liest
ihn vor.

Er sagt: *„Wenn er das notierte wiederholt, dann stimmt die Geschwindigkeit
nicht mit den anderen Ansagen überein."*

Ich vermute unterschiedliche Verarbeitungsketten und messe: 2,918 Sekunden
gegen 2,575. Sieht überzeugend aus. **Ist ein Artefakt meiner eigenen
Messung.** Schickt man *eine* Sprachausgabe durch beide Ketten, kommt beides
bei 2,549 heraus.

Der Unterschied kam daher, dass ich das Sprachprogramm zweimal aufgerufen
hatte.

Also fünfmal derselbe Satz:

```
2,575 s   2,562 s   2,865 s   2,456 s   2,628 s
```

**Siebzehn Prozent Streuung.** Ohne dass sich etwas geändert hätte.

Piper benutzt ein VITS-Modell mit einem Zufallsanteil in der Lautdauer.
Jeder Satz klingt jedes Mal anders lang.

Die Tragweite ist größer als der Anlass. **Jede Sprechdauer-Messung dieses
Projekts war eine Stichprobe, keine Zahl.** „1,13 Sekunden für ‚Ich
höre.'" - eine Zahl, auf die Entscheidungen gebaut wurden - hatte eine
unbekannte Streuung von bis zu siebzehn Prozent.

Ein Schalter behebt es: `--noise_w 0`. Danach ist die Ausgabe auf die
Millisekunde reproduzierbar. Gespeicherte Ansage 0,939 s, frisch erzeugte
0,939 s.

Gefunden hat es kein Test, keine Messung und kein Werkzeug. Gefunden hat es
ein Mensch, der zugehört hat.

---

## Tag 13, nachmittags: Sieben Minuten

Das Diktat braucht einen Schlusssatz. „Diktat beenden". In der freien
Erkennung wird daraus `'diktat wird erhöht'` - ein *bestimmter* Satz ist
unter zehntausenden Möglichkeiten nicht zuverlässig zu treffen. Zum
**dritten** Mal derselbe Effekt: „gnome" wurde zu „genug", „windows" zu
„sinnlose", „beenden" zu „wird erhöht".

Die Lösung: ein zweiter Erkenner, der **nur diesen einen Satz** kennt. Er
trifft ihn wörtlich.

Aber ich verlange exakte Übereinstimmung. Und notiere am selben Morgen in
der Dokumentation:

> *„Gestoppt hat er nicht, weil exakte Übereinstimmung verlangt wird - aber
> diese Bedingung ist das einzige, was dazwischen steht."*

Am Nachmittag sagt Stephan „diktat beenden". Der Erkenner liefert
`'beenden'`.

Die Bedingung weist es ab.

**Sieben Minuten** läuft das Diktat weiter. Es schreibt alles mit, was im
Raum gesprochen wird - 42 Einträge, darunter „Ja Silvia erwerben" und „Also
brieselang". Zu stoppen war es nur von Hand.

Die Lehre steht seitdem als Satz im Protokoll: **Ein notiertes Risiko ist
kein behandeltes Risiko.**

---

## Tag 16: Die Reparatur von Tag 13 schlägt zurück

**21. August.** Stephan will den Brief. Alles dafür ist da: Diktat,
Schreibhilfe, Fußzeile. Es fehlen Satzzeichen, ein Ablageort und ein
Briefkopf. Ein Tagewerk, denkt man.

Am Vormittag läuft es. Gesprochene Satzzeichen, gemessen statt geraten: Die
nackten Wörter treffen bei Stephans Stimme **drei von sechs** - „Komma" wird
zu „komme", „Punkt" zu „kommt", „Doppelpunkt" zu „dörte depots". Die
zweiwortigen Formen treffen **drei von drei**. Also „Komma setzen". Nebenbei
fällt damit ein Preis weg, den Stephan vorher akzeptiert hatte: „in diesem
Punkt" bleibt jetzt stehen.

Dann diktiert er den ersten Brief. Das Diktat endet nach sechs Sekunden. Von
selbst.

### Der unzuverlässige Erzähler bin diesmal ich

Ich habe eine Erklärung: Umgebungsgeräusch. Der Schluss-Erkenner kennt nur
„diktat beenden" und `[unk]`, er muss jedes Geräusch auf eines von beidem
abbilden. Klingt schlüssig.

Ich messe es: 180 Sekunden Stille im selben Raum, dieselbe Grammatik. **Null
Ergebnisse.** Die Erklärung ist falsch.

Ich habe eine zweite: Anna hört sich selbst. Die Bereit-Ansage läuft, die
Aufnahme startet, die Echo-Unterdrückung braucht einen Moment. Auch schlüssig.

Ich messe es: dreimal Ansage, dreimal sofort zuhören. **Nichts.** Auch falsch.

Zwei Diagnosen, beide in sich stimmig, beide widerlegt. Bisher hat der
Gegenspieler Systeme benutzt, die Erfolg melden. An diesem Tag benutzt er
mich.

### Vier Reparaturen an einem Nachmittag

Ich baue eine Sperrfrist: kein Schluss in den ersten drei Sekunden. Der
nächste Test bricht nach 4,2 ab.

Ich baue ein Pegel-Tor: zu leise ist kein Schluss. Das Geräusch ist laut
genug.

Ich zähle aus - alle Schluss-Ereignisse des Tages: **sechs Fehlauslöser, jeder
einzelne ein nacktes „beenden"**, null bei „diktat beenden". Also verlangt der
Schluss beide Wörter. Damit fällt die Regel von **Tag 13**, die genau
umgekehrt entstanden war: Damals hatte exakte Übereinstimmung ein Diktat
sieben Minuten laufen lassen, und die Lehre hieß, das Wort genüge. Sie stammte
aus sieben Minuten Dauergerede - und hatte nie geprüft, was beim *Diktieren*
passiert.

Ich baue eine Ansage: Wenn nur „beenden" ankommt, soll DialOS es sagen, damit
niemand ins Leere spricht. Sie unterbricht Stephan nach vier Sekunden mitten
im Brief. Sein Urteil ist der Satz des Tages:

> **„Diesen Text kann ich nie zu Ende bringen."**

Die Ansage kommt noch am selben Tag wieder raus. Eine Hilfe, die häufiger
stört als sie hilft, ist keine.

### Zwei Fehler, die seit Wochen dort lagen

Zwischen den Reparaturen kommen zwei Dinge ans Licht, die nichts mit dem
Schlusssatz zu tun haben und älter sind als er.

**Vosk liefert erst an einer Sprechpause ab.** Wer den Brief in einem Zug
spricht und dann „Diktat beenden" sagt, hat beides in *derselben* Pause: Der
Schluss bricht die Schleife ab, bevor die Erkennung ihren gesammelten Text
abliefern konnte. `FinalResult()` wurde nie aufgerufen. Im Protokoll steht
„0 Äußerungen", während ein ganzer Brief gesprochen wurde.

**Und der Notausgang war selbst kaputt.** Zwei Minuten Stille sollten jedes
Diktat beenden. Sie konnten nie greifen: Jedes `[unk]` aus Raumgeräusch setzte
die Uhr zurück. Ein Diktat läuft neun Minuten weiter, hält die Marke „ein
anderer Dienst hört zu" - und Stephan kann die Sprachsteuerung nicht mehr
starten. Ausgerechnet die Geisterwörter, die das neue Pegel-Tor beim Schreiben
aussortiert, halten es am Leben.

Beide Fehler sind so alt wie das Diktat. Beide fallen erst auf, als jemand
einen *Brief* diktiert statt eines Einkaufszettels.

### Die beste Frage des Tages

Am Abend fragt Stephan: Warum funktioniert der Einkaufszettel dann sauber?

Die Antwort steht in der Messung, die schon dalag. Dreißig Sekunden
zusammenhängender Brieftext durch den Schluss-Erkenner:

```
bei  4,8 s  'diktat'
bei  8,4 s  'beenden'
bei 12,2 s  'diktat [unk] beenden'
bei 15,1 s  'beenden'
```

Bruchstücke im Sekundentakt - aus *durchgehender* Rede. Ein Einkaufszettel
klingt anders: „Milch." Pause. „Butter." Pause. Und 180 Sekunden Stille hatten
**null** Ergebnisse geliefert. Die Pausen zwischen den Waren schützen den
Einkaufszettel, ohne dass es jemand so geplant hätte.

Damit ist auch klar, wo der Hebel liegt: Ein echtes „Diktat beenden" folgt auf
eine Pause. Jedes Bruchstück entsteht mittendrin.

### Was der Tag gekostet hat

Sechs Testläufe von Stephan, jeder mit einem Fehler darin, den ich vorher
hätte finden können. Vier Regeln stehen seitdem ganz oben in
[../CLAUDE.md](../CLAUDE.md), und die wichtigste lautet: **Was gegen Piper
offline prüfbar ist, wird vorher offline geprüft.** Nicht Stephan ist der
Testlauf.

Die zweite: **Eine Erklärung, die zu allen Beobachtungen passt, ist noch keine
Ursache.**

---

## Wie es ausgeht

Es geht nicht aus. Am 21. August, 14:19 Uhr, steht der 261. Commit.

Was existiert: eine Sprachsteuerung, die nur auf Ansage zuhört und das
ansagt. Ein Diktat, das Notizen schreibt, mit 98,1 % richtiger Groß- und
Kleinschreibung. Ein Einkaufszettel, der sich vorlesen, ergänzen und
wegwerfen lässt - mit Rückfrage, weil er nur durch Sprechen entstanden ist.
Eine Tonausgabe, die keinem Gerät glaubt, sondern es ausprobiert. Und eine
Dokumentation, die jeden dieser Fehler mitträgt, weil sie sonst wieder
gemacht werden.

Dazu, seit den letzten drei Tagen: eine Herkunftszeile in jeder Mail, drei
Akkuwarnungen, ein Gerät das nicht mehr einschläft und den Nutzer nicht
aussperrt - und ein Brief, der als Briefbogen entsteht, mit Datum, Fußzeile
und dem Hinweis, warum er nicht unterschrieben ist.

Was nicht existiert: Telefonie, Vorlesen von Mails, das Einscannen von Post.
Und der Brief lässt sich nicht zu Ende diktieren, weil der Schluss-Erkenner
aus laufender Rede ein „diktat beenden" macht. Das ist der einzige Punkt, der
zwischen dem fertigen Weg und einem brauchbaren Brief steht.

Der Gegenspieler ist nicht besiegt. Er ist erkannt. Das ist bei diesem
Gegenspieler der ganze Unterschied: **Ein System, das lügt, ist harmlos,
sobald man aufhört, ihm zu glauben, und anfängt zu messen.**

Tag 16 hat dem einen Satz hinzugefügt: Das gilt auch für den, der misst.

---

*Für die Zahlen und Belege: [../README.md](../README.md) hat das
vollständige Änderungsprotokoll, [../TODO.md](../TODO.md) die offenen
Punkte, [../CLAUDE.md](../CLAUDE.md) die Regeln, die aus diesen
Tagen entstanden sind. Wie DialOS klingt, steht als Hörbeispiele in
[sprachbeispiele/](sprachbeispiele/README.md).*
