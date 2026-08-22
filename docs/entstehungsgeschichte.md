[Deutsch](entstehungsgeschichte.md) | [English](entstehungsgeschichte.en.md)

# Dreizehn Tage und mehr …

*Die Entstehung von DialOS, vom 6. bis 22. August 2026. 289 Commits.
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

## Tag 14: Zwei Tage lang lief etwas anderes, als im Repo stand

**19. August.** 26 Commits. Der Tag beginnt mit einem Wunsch von Stephan, der
wie eine Kleinigkeit klingt: Es soll sich wie ein **Dialog** anfühlen, nicht
wie eine Maschine, die Zustände meldet. Daraus wird eine Regel, und jede
einzelne Ansage wird gegen sie geprüft. „Ich höre Dir zu" statt
„Spracherkennung aktiv".

Dann kommt die Ja/Nein-Rückfrage vor dem Leeren des Einkaufszettels. Sie
funktioniert nicht. Stephan sagt „ja", nichts passiert.

Der Grund ist eine Reihenfolge: Der Aufrufer sprach die Frage - und **danach**
lud die Funktion ihr Sprachmodell, elf Sekunden lang. Die Antwort fiel in
genau dieses Loch. Die Frage war gestellt, aber niemand hörte zu. Seitdem
stellt die Funktion die Frage selbst, nachdem sie bereit ist.

### Der blinde Fleck des Prüfskripts

Am selben Tag fällt auf, dass **zwei Skripte zwei Tage lang in einer älteren
Fassung liefen, als im Repo stand**. Alles war committet, alles sah richtig
aus, und das Gerät führte etwas anderes aus.

Die Antwort darauf ist ein Prüfskript: Es vergleicht, was im Repo steht, mit
dem, was installiert ist. Genau die Sorte Werkzeug, die dieses Projekt
braucht.

Das Prüfskript hat einen blinden Fleck. Es sieht **ein Verzeichnis** an.
Dateien daneben sind für es nicht vorhanden - und „nicht vorhanden" meldet es
als in Ordnung.

Das ist derselbe Gegenspieler wie an Tag 8 und Tag 12, nur eine Ebene höher:
Diesmal meldet nicht das System Erfolg, sondern **das Werkzeug, das den Erfolg
prüfen soll**. Es wird zweimal nachgebessert - erst eine handgepflegte Liste
(veraltet beim nächsten neuen Skript), dann der ganze Baum. Und es meldet
seitdem ausdrücklich, was es **nicht** lesen darf, statt zu schweigen.

### Ein Münzwurf mit 0,8 Sekunden Vorsprung

Die Schreibhilfe braucht beim ersten Satz einer Sitzung **9,2 Sekunden** - die
deutschen Regeln laden nicht beim Serverstart, sondern bei der ersten
Prüfanfrage. Die Zeitgrenze im Diktat liegt bei 10,0 Sekunden.

Acht Zehntelsekunden Luft. Die erste Korrektur jeder Sitzung war damit ein
Münzwurf, und um 10:03:03 hat sie verloren.

Die Lösung ist ein Aufwärmlauf beim Anmelden: Die neun Sekunden fallen einmal
an, wo niemand darauf wartet. Danach antwortet die Prüfung in 1,0 Sekunden.

Am Abend steht „Hilfe rufen": DialOS liest dem Nutzer eine ID und ein
Einmalpasswort vor, langsam, mit Pause dazwischen, und fragt hinterher nach,
ob beides angekommen ist. Der privilegierte Teil ist gebaut, geprüft - und
**bewusst nicht installiert**, weil der Dienst dahinter noch nicht steht.

---

## Tag 15: Dieselben Daten durch beide Regeln

**20. August.** 19 Commits. Stephan hat DialOS einen Tag lang laufen lassen
und meldet etwas Beunruhigendes: „Immer mal wieder meldete sich Michael." Die
Sprachsteuerung schaltet sich **von selbst** ein. Einmal fragt sie sogar, ob
sie die Fernwartung starten soll.

Das Einschalten hörte auf ein Kernwort, und das Kernwort war „starten". Im
Protokoll steht, wie oft dieses Wort aus reinem Umgebungsgeräusch entstand:
**27-mal in zwei Stunden.**

### Die beste Messung des Projekts

Die Umstellung ist schnell gemacht - das Kernwort wird „sprachsteuerung", lang
und markant. Interessant ist, wie sie belegt wird: **Dieselben zwei Stunden
Protokoll werden durch beide Regeln gerechnet.** Nicht zwei Zeiträume
verglichen, bei denen jemand anders im Raum war oder das Radio lief - eine
Datenbasis, zwei Regeln.

Ergebnis: Die alte Regel hätte **30-mal** eingeschaltet, die neue **7-mal**.
Ersparnis: 46 Minuten offenes Mikrofon in gut zwei Stunden.

Und dieselbe Messung zeigt die Grenze: Auf **keine** der sieben folgte ein
Befehl. Auch die sieben waren überwiegend Geräusch. Die Umstellung drückt das
Problem um drei Viertel, sie löst es nicht.

Daraus werden zwei kleine Änderungen statt des großen Aufweckworts, dessen
fertige Modelle unter einer nicht-kommerziellen Lizenz stehen: Das Einschalten
verlangt **beide** Wörter, und ohne Befehl ist nach 30 Sekunden Schluss statt
nach zwei Minuten.

Die zweite Änderung greift zunächst nicht. Der Grund ist eine Zeile in der
falschen Reihenfolge: Der Zeitstempel wurde **vor** der Ansage gesetzt, und
die Ansage dauert gut eine Sekunde - danach sah es aus, als sei schon ein
Befehl gekommen. Gefunden hat es Stephans Test, nicht mein Test: Meiner hatte
die Entscheidungsfunktion geprüft, nicht die Reihenfolge.

### Anna

Stephan entscheidet: eine freundliche Damenstimme. Aus dem Hörvergleich wird
`de_DE-kerstin-low`, Tempo 1,00, Name **Anna** - und sie wird
Auslieferungsstimme, nicht nur Testeinstellung. (Das Tempo bleibt nicht so:
Am 2026-08-22 hört Stephan 1,00 / 0,90 / 0,80 / 0,95 nacheinander und
entscheidet **0,95**.)

Das Tempo ist dabei pro Stimme verschieden, und zwar messbar: Derselbe Satz
**Diese Zahlen waren falsch** (berichtigt am 2026-08-22): Sie stammen aus
einem Erzeuger, der Kerstins 16-kHz-Rohdaten als 22050 Hz deklarierte - jede
Kerstin-Probe lief damit 38 % zu schnell. Richtig gemessen braucht derselbe
Satz bei Michael mit 0,88 rund 6,15 s und bei Anna mit 1,00 rund 7,04 s; Anna
ist also **14 % langsamer**, nicht gleichauf. Seit dem 2026-08-22 steht Anna
auf **0,95** - von Stephan aus korrekt erzeugten Proben gewählt.

Auf Stephans Frage hin spricht DialOS den Nutzer jetzt mit Namen an - bei der
Begrüßung, bei Entscheidungen, bei Fehlern. **Nicht** bei Bestätigungen und
nicht bei der Zeitgrenze. Der Grund wiegt schwerer als Höflichkeit: Läuft das
Radio oder ist Besuch im Raum, sagt „Stephan, …" unmissverständlich, dass es
ihn betrifft. Wer den Namen dauernd hört, überhört ihn.

Dann hört Stephan genauer hin: „Michael sagt Stefffan."

Der Name wird bei jeder Begrüßung gesagt, bei jeder Rückfrage, bei jedem
Fehler. Falsch ausgesprochen stört er mehr als jedes andere Wort. Die
Namensdatei bekommt ein zweites Feld: `Stephan | Stefan`. Geschrieben bleibt
„Stephan" - für Briefe, wo „Stefan" schlicht falsch wäre. Gesprochen wird das
zweite.

**Das hätte ich allein nie gefunden.** Ich hatte die Namensanrede an drei
Ansagen geprüft und für fertig erklärt. Dass der Name selbst falsch klingt,
hört nur, wer ihn kennt.

### „Nur Sicherheitsupdates", bevor ich nachgesehen hatte

`unattended-upgrades` wird eingerichtet. Ich sage Stephan, es seien nur
Sicherheitsupdates.

Dann sehe ich nach. Eine `Origins-Pattern`-Zeile **hängt an**, sie ersetzt
nicht. Nach dem ersten Versuch standen fünf Muster in der Liste: meine zwei
**und** Debians drei, darunter das gewöhnliche Stable ohne `-Security`. Das
Gerät hätte nachts alles aktualisiert.

Behoben mit `#clear`, belegt mit einem Probelauf, bei dem alles außer
`Debian-Security` mit Pin `-32768` auf „auf keinen Fall" steht. Aber die
Aussage war vor der Prüfung schon draußen. Stephans Antwort darauf ist der
Satz, der diesen Tag zusammenfasst: **„Fehler sind menschlich."**

Am selben Tag verliere ich Daten: Mein Neustart-Werkzeug legte das Protokoll
immer unter demselben Namen beiseite und überschrieb beim zweiten Lauf die
erste Sicherung. Die Rohdaten der 157 Äußerungen sind weg; das Ergebnis steht
in den Commits, die Daten nicht. Das Werkzeug legt seitdem gar nichts mehr
beiseite - seit demselben Tag räumt logrotate die Protokolle nach sieben Tagen
auf, und ein zweiter Mechanismus daneben schafft nur Namenskollisionen.

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

## Tag 17: Der Fehler, der nichts sagt

Der Tag beginnt mit einem Ordner voller Krempel. Fünfundzwanzig Protokolldateien
liegen offen im Heimatverzeichnis, zwischen `Notizen`, `Dokumente` und `Bilder`.
Stephan fragt, ob die gebraucht werden. Sechs davon speisen das
Mitschrift-Fenster, alle zusammen sind das Gedächtnis für den Support - aber
liegen müssen sie da nicht. Sie ziehen nach `~/.log`, und der Punkt am Anfang
macht den Ordner unsichtbar.

Dann kommt ein Satz, der die Änderung von der anderen Seite beleuchtet:

> „immer dran denken wir haben auch sehende User"

Das trifft genau diesen Umzug. Für den blinden Nutzer ist ein versteckter
Ordner gleichgültig; er sieht ohnehin nichts. Für den Helfer, der neben ihm
sitzt, ist etwas, das er nicht sieht, eine Hürde. Also kommt in die Anleitung
eine Tabelle: was wo liegt und was davon sichtbar ist. Barrierefreiheit heißt
nicht, dass nur eine Seite bedient wird.

### Der Ausdruck kommt quer

Nachmittags druckt Stephan zum ersten Mal wirklich. Das Blatt kommt quer heraus.

Ich messe den ganzen Weg nach. `texttopdf` liefert mit dem PPD dieser
Warteschlange 595 × 842 Punkte - A4 hochkant. `pdftopdf` gibt genau das weiter,
Drehung 0. Der Drucker meldet per IPP `orientation-requested-default =
portrait` und `media-default = iso_a4`. Die Warteschlange steht auf A4.

Jede Stelle, die ich prüfen kann, sagt hochkant. **Und das Blatt ist quer.**

Die Ursache liegt hinter allem, was auf diesem Gerät messbar ist. Ich kann sie
nicht benennen - und das ist unbefriedigend, aber es ist die Wahrheit. Was ich
ändern kann, ist die Haltung: Der Aufruf war nacktes `lp -d ZIEL -`, ohne eine
einzige Option. Die Ausrichtung hing damit an einer Voreinstellung, auf die
sich niemand festgelegt hatte. Jetzt steht sie im Auftrag:
`-o media=A4 -o orientation-requested=3`.

**Eine Voreinstellung, auf die man sich verlässt, ist eine Annahme.** Diese war
nachweislich falsch, auch wenn ich nicht sagen kann, wo genau sie kippte.

Beim Nachsehen fällt noch etwas auf: `dialos-fusszeile.py drucken` rief `lp -`
**ohne Ziel** auf. Auf diesem Gerät gibt es kein Standardziel - der Aufruf wäre
gescheitert, sobald ihn jemand benutzt hätte. Zwei Monate lang hätte niemand
etwas gemerkt, weil niemand diesen Weg ging.

### Und dann sagt das Gerät gar nichts

Stephan testet nach. Ich schaue ins Protokoll. Im Druckprotokoll steht nichts
Neues. Im Befehlsprotokoll steht:

```
15:07:32  erkannt: 'notiz drucken'
```

Einzahl. Die Grammatik kennt nur „notizen drucken".

Das ist kein Hörfehler. Die eingeschränkte Grammatik ist eine Liste von
**Sätzen**, aber Vosk baut daraus ein **Wortnetz** - und darf Wörter aus
verschiedenen Sätzen kombinieren. „notiz" kommt aus „notiz aufnehmen",
„drucken" aus den drei Druckbefehlen. Die Kombination ist erlaubt und ergibt
doch keinen Befehl.

Und weil kein Treffer vorliegt, gibt es auch keine Ansage.

**Das ist der schlechteste mögliche Ausgang.** Nicht der Fehlschlag - die
Stille. Ein sehender Nutzer sieht ein Fenster, das sich nicht öffnet, ein
Blatt, das nicht kommt. Ein blinder Nutzer hat gesprochen, das Gerät hat
zugehört, und nichts sagt ihm, dass nichts geschah. Er weiß nicht einmal, ob er
falsch gesprochen hat oder ob das Gerät kaputt ist. Eine Fehlermeldung wäre
besser gewesen. Fast alles wäre besser gewesen.

Die Einzahl kommt in die Grammatik. Aber der eigentliche Fall bleibt offen, und
er ist größer als dieser eine Satz: Im selben Protokoll stehen `'wie viel uhr
schreiben'` und `'linux auf tag einkauf auf einkauf'`. Auch erlaubte
Kombinationen. Auch ohne Befehl. Auch lautlos.

Der zweite Ausdruck kommt hochkant.

### Zwei Tasten und eine Regel, die ich nicht anfassen durfte

Zum Schluss zwei Tastenkombinationen fürs Admin-Konto: `Strg`+`Alt`+`W`
schaltet die Optik zwischen Linux und Windows, `Strg`+`Alt`+`S` die Stimme
zwischen Michael und Anna. Beide Skripte schalten jetzt *um*, statt ein Ziel zu
verlangen - wer eine Taste drückt, will nicht wissen, in welchem Zustand er ist.

Die Stimme braucht dafür ein eigenes Skript, denn `setzen` macht nur die
Hälfte: Es schreibt die Konfiguration und sagt dem Menschen dann, er möge
speech-dispatcher neu starten. Am Terminal zumutbar. Hinter einer Taste nicht -
wer eine Taste drückt, erwartet eine andere Stimme, keine Hausaufgabe.

Dazwischen liegt noch eine kleine Lektion, und sie ist nicht technisch. Beim
Aufräumen der TODO-Liste wollte ich alle erledigten Punkte nach unten sortieren.
Sechs von ihnen hängen an noch offenen Punkten - „siehe oben", „Restrisiko
dazu", „die zwei neuen Punkte unten". Ich hatte schon angefangen, fünf von
Stephans Formulierungen umzuschreiben, damit meine Sortierung aufgeht. Er
stoppt das:

> „die bleiben oben, bis auch die anderen Punkte erledigt sind und wandern dann
> gemeinsam hoch"

Seine Regel ist besser als meine. Meine hätte seinen Text der Ordnung
angepasst; seine passt die Ordnung dem Text an. Beim Nachzählen sind es dann
sechs statt vier - einen Bezug hatte ich übersehen.

**Die Lehre des Tages:** Ein Fehler, der etwas sagt, ist ein Fehler. Ein
Fehler, der nichts sagt, ist ein Rätsel - und Rätsel sind für diese Zielgruppe
keine Unannehmlichkeit, sondern eine Sackgasse.

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
