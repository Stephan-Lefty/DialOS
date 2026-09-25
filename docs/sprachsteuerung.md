[Deutsch](sprachsteuerung.md) | [English](sprachsteuerung.en.md)

# Sprachsteuerung

## Stack

- **Spracherkennung (STT)**: Vosk mit deutschem Modell, offline - für
  Befehle und den Einkaufszettel, mit eingeschränkter Grammatik.
- **Texterkennung für freien Text**: **Parakeet** (NVIDIA Parakeet TDT 0.6B v3
  über sherpa-onnx, offline), seit 2026-09-16 fest eingebaut - für Brief,
  Notizen, den Text einer E-Mail und Suchbegriffe. Gewählt nach dem Prüfstand
  vom 2026-09-15: 2,8 % Wortfehler gegen 12,7 % bei Vosk, und nur Parakeet
  setzt die Satzzeichen selbst (siehe [pruefstand.md](pruefstand.md)).
  Abschaltbar mit `~/.config/dialos/parakeet-aus`.
- **Sprachausgabe (TTS)**: Piper (natürlicher als espeak-ng), als
  Backend für Orca - RHVoice stand zur Wahl und ist verworfen.
- **Screenreader**: Orca (Standard-GNOME-Screenreader).
- **Low-Level-Desktopsteuerung** (Maus, Fenster): Numen – Wayland-nativ,
  ebenfalls Vosk-basiert, Open Source.
- **Intent-Erkennung**: [hassil](https://github.com/OHF-Voice/hassil)
  (Home Assistant Intent Language) - lernfähige Zuordnung über
  Beispielsatz-Vorlagen statt starrer Befehlsgrammatik (siehe unten).
  **Stand 2026-09-25: installiert, aber im Code nicht eingebunden** - siehe
  „Stand der Umsetzung".

## Stand der Umsetzung (2026-09-25)

Damit klar bleibt, was hier Konzept und was gebaut ist - der Stand vom
2026-08-16 steht darunter als Geschichte.

- **Sprachausgabe: im Einsatz.** Piper über speech-dispatcher,
  `dialos-say.py` spricht jede Ansage; Stimmen Michael und Anna.
- **Befehle: im Einsatz, rund 64 Befehlssätze** (gezählt bei der
  Pflichtprüfung vom 2026-09-21), die Sätze aus `dialos-programm.py` und die
  Startsätze der Erweiterungen eingeschlossen. Erkannt vom kleinen
  Vosk-Modell mit eingeschränkter Grammatik. Die vollständige Liste steht in [sprachbefehle.md](sprachbefehle.md).
- **Einschalten per Satz statt Aufweckwort:** „Sprachsteuerung starten" /
  „Sprachsteuerung stoppen" (entschieden am 2026-08-17, siehe unten). Ein
  eigenes Aufweckwort gibt es weiterhin nicht.
- **Freier Text: Parakeet seit 2026-09-16** für Brief, Notizen und den Text
  einer E-Mail; der Einkaufszettel bleibt bei Vosk. Einzelheiten in
  [diktat.md](diktat.md).
- **Intent-Erkennung: hassil ist installiert, aber im Code nicht
  eingebunden** (nachgesehen am 2026-09-25: kein DialOS-Skript importiert
  es). Die Zuordnung von Erkanntem zu Befehl macht der Sprachdienst selbst:
  Die Vosk-Grammatik lässt nur die Wörter der Befehlssätze zu, und eigene
  Regeln entscheiden, wann ein Satz gilt - Kernwort, ganze Wortfolge mit
  höchstens zwei Zusatzwörtern, kein `[unk]`. Warum die Entscheidung vom
  2026-08-13 so nie umgesetzt wurde: siehe den Hinweis im Abschnitt
  „Intent-Erkennung" unten.
- **Mikrofon:** Die Sprachdienste nehmen die echo-bereinigte Quelle
  `dialos_mikrofon_ohne_echo` selbst. Das Standard-Mikrofon des Systems
  bleibt bewusst das rohe eingebaute - Begründung in
  [anwendungen.md](anwendungen.md), Abschnitt „Zwei Regeln".
- **Screenreader Orca:** installiert; ob er an Piper gekoppelt ist, wurde für
  diesen Stand nicht neu geprüft. **Numen:** nicht installiert.

## Stand der Umsetzung (2026-08-16)

> **Überholt seit 2026-08-16 abends** (erster echter Sprachbefehl) - der
> aktuelle Stand steht direkt darüber. Dieser Abschnitt bleibt als
> Momentaufnahme stehen: So sah es aus, bevor die Sprachsteuerung gebaut wurde.

Damit klar bleibt, was hier Konzept und was gebaut ist:

- **Sprachausgabe: im Einsatz.** Piper läuft über ein
  speech-dispatcher-Generic-Modul, `dialos-say.py` spricht jede Ansage
  mit Audio-Ducking und Panel-Anzeige.
- **Spracherkennung: installiert und erstmals produktiv.** Vosk beantwortet
  die Lautstärke-Frage in der Start-Ansage (echt gesprochen getestet am
  15./16.08.). Alles darüber hinaus ist noch nicht gebaut.
- **Intent-Erkennung: hassil ist installiert, aber ungenutzt** - es gibt
  noch keine einzige Beispielsatz-Vorlage im System.
- **Dauerhaftes Zuhören mit Aufweckwort: nicht vorhanden.** Erkennung
  läuft nur, wenn ein Skript sie gezielt aufruft.
- **Screenreader Orca: installiert, aber noch nicht an Piper gekoppelt.**
- **Numen: nicht installiert.**

Das heißt: Die Sprach*ausgabe* ist fertig, die Sprach*steuerung* im
eigentlichen Sinn - jederzeit ansprechbar sein und Befehle ausführen -
steht noch aus. Sie ist der nächste große Arbeitsblock.

## Intent-Erkennung: flexibel statt starr

Eine starre Befehlsgrammatik (exakte Formulierungen wie bei klassischen
Sprachassistenten-Frameworks) passt schlecht zur Anforderung, dass das
System für 18-Jährige genauso einfach sein muss wie für 80-Jährige –
unterschiedliche Generationen formulieren denselben Befehl
unterschiedlich ("Ruf Anna an" vs. "Verbind mich mit Anna" vs.
"Telefonier mal mit Anna").

**Entscheidung (2026-08-13): [hassil](https://github.com/OHF-Voice/hassil)**
übernimmt die Zuordnung von Vosk-Transkription zu Aktion. Statt exakte
Formulierungen zu verlangen, werden pro Aktion mehrere
Beispielsatz-Vorlagen mit Alternativen/optionalen Wörtern hinterlegt
(z. B. `(ruf|verbind mich mit) [bitte] {person} an`) - neue
Formulierungen lassen sich durch Ergänzen weiterer Vorlagen "anlernen",
ohne Code zu ändern.

Ausschlaggebende Kriterien und geprüfte Alternativen:

- **Offline/Datenschutz**: Cloud-Lösungen (z. B. die bereits
  installierte Claude Code CLI zur Klassifikation nutzen) damit
  ausgeschlossen - hassil läuft komplett lokal, keine
  Internetverbindung nötig.
- **Kostenfrei**: Open Source, keine laufenden API-Kosten.
- **Lernfähig**: durch Ergänzen von Beispielsatz-Vorlagen, ohne
  Neu-Training/Fine-Tuning eines Modells.
- Ursprünglich war **Rhasspy** als Ausgangsbasis angedacht (nutzt
  intern denselben Beispielsatz-Ansatz). Bei der Installationsrecherche
  stellte sich aber heraus, dass Rhasspy 2026 vom Ersteller archiviert
  wurde (Begründung: drohender Burnout) und nicht mehr weiterentwickelt
  wird - ungeeignet als Basis für ein System, das über Jahre laufen
  soll. hassil ist die aktiv gepflegte Nachfolge-Komponente (Teil der
  Open Home Foundation/Home Assistant, Stand 2026: über 600 Commits),
  die denselben Beispielsatz-Ansatz bietet, aber ohne Docker/eigenen
  Dienst - nur eine schlanke Python-Bibliothek (einzige Abhängigkeit:
  PyYAML), die sich direkt in eigene Skripte wie
  `dialos-vosk-test.py`/`dialos-say.py` einbinden lässt.
- Ein eigenes kleines lokales Sprachmodell (z. B. via llama.cpp) wäre
  freier in der Formulierungs-Erkennung gewesen, aber deutlich
  aufwändiger in Auswahl/Einbindung/Qualitätssicherung - für die
  überschaubare, klar abgegrenzte Anzahl an Aktionen (WLAN, Lautstärke,
  Programme starten, Anrufen, ...) erschien der Beispielsatz-Ansatz von
  hassil als besseres Aufwand-Nutzen-Verhältnis.

> **Stand 2026-09-25: so nicht umgesetzt.** Gebaut wurde ab dem 2026-08-16
> eine eingeschränkte Vosk-Grammatik mit eigener Zuordnung (siehe „Stand der
> Umsetzung" oben). Den Grund nennt `TODO.md` schon am 2026-08-16: hassil lohnt
> sich erst, wenn es mehrere Befehle mit Varianten gibt. Mehrere Formulierungen
> für denselben Befehl stehen seitdem als eigene Sätze in der Grammatik („Wie
> viel Uhr ist es?", „Wie spät ist es?"). Ob hassil bei den Erweiterungen noch
> seinen Platz findet, ist in [erweiterungen.md](erweiterungen.md) offen.

Die Flexibilität gilt fürs **Verstehen**, nicht fürs **Ausführen** –
sicherheitskritische Aktionen (Systemwartung, Freigabe der
Fernwartung) bleiben immer hinter einer expliziten Ja/Nein-Rückfrage,
unabhängig davon, wie der Befehl erkannt wurde.

## Sprachgesteuerte Systemwartung

Geführter Dialog mit Rückfrage statt direkter Befehlsausführung, z. B.:

> "Computer, System aktualisieren" → "Jetzt Updates installieren? Ja/Nein"

Keine direkten Befehle ohne Bestätigung – Sicherheit vor Fehlerkennung
hat hier Priorität.

## Design-Prinzipien für Sprachdialoge

- Geduldig, nachfragend statt abbrechend bei Unklarheit.
- Keine Fachbegriffe.
- Keine auswendig zu lernenden Befehlswörter.
- Bei Rückfragen/Bestätigungen (z. B. Namenserfassung bei der
  Ersteinrichtung) immer eine Korrekturmöglichkeit anbieten.

## Ressourcen-Überlegung (Akkulaufzeit)

Da das Gerät auch unterwegs genutzt wird, ist ständiges Zuhören mit
vollem STT spürbar akkukostend. Vorschlag: zweistufiges Modell mit einem
sehr sparsamen Wake-Word-Modell (z. B. openWakeWord), das permanent nur
auf ein Trigger-Wort lauscht; erst danach wird die rechenintensivere
volle Spracherkennung aktiviert. Noch nicht final entschieden/umgesetzt.

Welche Befehle es konkret gibt, steht in
[sprachbefehle.md](sprachbefehle.md).

## Wann hört DialOS zu? Das Bedienmodell

**Entschieden am 2026-08-17 mit Stephan.** Es gibt **zwei verschiedene
Wege**, auf denen das Mikrofon scharf wird - und der Unterschied ist
nicht technisch, sondern liegt daran, wer das Gespräch begonnen hat.

### 1. Das System fragt - es macht selbst auf und wieder zu

Wenn DialOS etwas wissen will, weiß es das ja. Es öffnet die Erkennung
selbst, nimmt die Antwort entgegen und schließt sie danach wieder. **Der
Nutzer muss sich nicht anmelden** - er wurde gerade angesprochen.

Genau dafür trägt `dialos-say.py` den Schalter `--frage` (siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 11a): Die Information
„ich will jetzt etwas wissen" ist im Code ohnehin vorhanden.

**Antwortet der Nutzer nicht**, wird **einmal** nachgefragt. Bleibt es
auch dann still, sagt Michael „Schade, dass Du nicht antwortest." und
schließt das Fenster. Bewusst kein stilles Schließen: Der Nutzer soll
hören, dass die Frage vorbei ist - sonst spricht er womöglich ins Leere.

### 2. Der Nutzer will etwas - er meldet sich an

Hier kann das System nicht ahnen, dass es gemeint ist. Deshalb:

> „Sprachsteuerung starten" → **„Ich höre Dir zu."**
> … Befehle …
> „Sprachsteuerung stoppen" → **„Ich höre Dir nicht mehr zu."**

Die Bestätigungen sind kurz und immer gleich - der Nutzer hört sie
täglich, da zählt Wiedererkennbarkeit mehr als Abwechslung. Sie sind aus
Michaels Sicht formuliert, nicht als Statusmeldung („Sprachsteuerung ist
eingeschaltet").

**Nach zwei Minuten ohne Befehl schaltet sich die Erkennung von selbst
ab**, mit Ansage: „Du hast eine Weile nichts gesagt. Ich höre Dir nicht mehr zu." Der Grund
ist kein Stromsparen, sondern Sicherheit: Wer das „stoppen" vergisst,
hätte sonst dauerhaft ein offenes Mikrofon - und damit wären wir zurück
bei dem Radio, das den Schreibtisch umschaltet.

**Beim Anmelden ist die Erkennung immer aus.** Vorhersagbar und sicher;
der Nutzer schaltet sie ein, wenn er sie braucht.

### Warum das die Zustandsfrage löst

Die offene Frage war: Woher weiß ein blinder Nutzer, ob die Erkennung an
ist? Antwort: **Er hört jeden Wechsel** - beim Ein- und Ausschalten,
und auch, wenn die Zeit abläuft. Und ist er unsicher, sagt er einfach
„Sprachsteuerung starten": Läuft sie schon, sagt das System es ihm.

Ein Zustand, den man nur sehen kann, wäre für diese Zielgruppe kein
Zustand.

## Aufweckwort: gemessen, und der naheliegende Weg scheidet aus

**Stand 2026-08-17.** Ein Aufweckwort fehlt weiterhin. Die naheliegende
Umsetzung - dieselbe eingeschränkte Vosk-Grammatik wie beim
Desktop-Sprachbefehl, nur mit dem Weckwort darin - wurde gemessen und
**verworfen**.

Geprüft mit der bewährten Methode (Piper spricht, Vosk hört):

| gesagt | erkannt | |
|---|---|---|
| „Michael" | `michael` | erkannt |
| „Hallo Michael" | `hallo michael` | erkannt |
| „Anna" / „Computer" | `anna` / `computer` | erkannt |
| **„ich rufe michael an"** | **`hallo michael`** | **Fehlalarm** |
| **„der computer ist langsam"** | **`computer`** | **Fehlalarm** |
| „hallo wie geht es dir" | `hallo` | ruhig |

Die Wörter selbst sind also alle im Wortschatz des Modells - das war
nicht selbstverständlich (siehe „gnome" → „genug" beim
Desktop-Sprachbefehl). Das Problem liegt woanders: **Eine eingeschränkte
Grammatik hat keine Wahl. Sie presst jede Äußerung in die nächstliegende
Phrase.** Für Befehle ist das ein Vorteil - man sagt sie absichtlich und
deutlich. Für ein Weckwort ist es fatal, denn es muss im normalen
Gespräch gerade *nicht* anspringen.

Die naheliegende Rettung greift nicht: Vosk liefert auf Wunsch
Wort-Sicherheiten, aber „ich rufe michael an" wurde mit **conf 1.00** -
also voller Sicherheit - als „michael" durchgereicht. Ein Schwellwert
trennt echte von falschen Treffern nicht.

**Konsequenz:** Für das Weckwort braucht es ein eigenes Modell, das eine
echte Wahrscheinlichkeit liefert statt eines erzwungenen Treffers -
[openWakeWord](https://github.com/dscripka/openWakeWord) stand oben schon
als Vorschlag und bleibt es.

**Entschieden am 2026-08-17: „Sprachsteuerung starten" und
„Sprachsteuerung stoppen"** (Stephans Vorschlag). Das ist kein Weckwort
vor jedem Befehl, sondern ein **Schalter**: Bis zum „starten" hört DialOS
nur auf diesen einen Satz, danach nimmt es Befehle an, bis „stoppen"
kommt.

Der Vorschlag hat sich im selben Test als **deutlich besser als der
Assistentenname** erwiesen:

| gesagt | erkannt | |
|---|---|---|
| „sprachsteuerung starten" | `sprachsteuerung starten` | löst aus |
| „sprachsteuerung stoppen" | `sprachsteuerung stoppen` | löst aus |
| „die **sprachsteuerung** von dialos ist praktisch" | `sprachsteuerung [unk]` | ruhig |
| „kannst du das **starten**" | `starten` | ruhig |
| „wir müssen das mal **stoppen**" | `stoppen stoppen` | ruhig |

Wo „Hallo Michael" am Störsatz scheiterte, hält hier der Auffangeintrag
`[unk]` sauber dagegen: Zwei bestimmte Wörter direkt hintereinander
fallen im Gespräch praktisch nicht, und jedes für sich löst nichts aus.
Damit ist offen, ob openWakeWord überhaupt nötig wird - **das ist noch
kein Beweis**, geprüft wurde mit synthetischer Stimme und drei
Störsätzen, nicht mit echtem Gespräch über längere Zeit.

Der frühere Vorschlag, den Assistentennamen zu nehmen, bleibt als
Rückfallebene notiert: Er käme aus derselben Einstellung wie die
Stimmenwahl bei der Ersteinrichtung (siehe
[ersteinrichtung.md](ersteinrichtung.md): Michael, Daniel, Anna, Julia).

**Was ein Aufweckwort NICHT löst:** Das Mikrofon-Symbol in der oberen
Leiste bleibt an. Um das Weckwort zu hören, muss weiter zugehört werden -
die Aufnahme bleibt also offen. Das ist auch richtig so: Das Gerät hört
tatsächlich zu, und bei einer Zielgruppe, die den Bildschirm nicht sieht,
wäre es das Schlechteste, genau das zu verstecken. Entscheidend ist, dass
nichts das Gerät verlässt - Vosk läuft vollständig offline.

## Wie schnell antwortet DialOS? (gemessen 2026-08-17)

Das ist kein Komfortthema. Wer den Bildschirm nicht sieht, hat nur die
Antwort als Rückmeldung - und wenn sie ausbleibt, spricht er lauter,
statt zu warten. Genau das ist an einem Tag zweimal passiert.

| Was | Vorher | Jetzt |
|---|---|---|
| Ansage „Ich höre." | 2172 ms | **rund 1200 ms**, davon 1130 ms die Ansage selbst |
| Taubheit nach einem Umschalten | ≈ 5,1 s | solange gesprochen wird, plus 0,7 s |

Die Ansagezeit kam durch einen **Ansagen-Speicher** herunter: Gesprochene
Sätze liegen als WAV unter `~/.cache/dialos/ansagen` und werden beim
nächsten Mal von dort gespielt (Details in `Debian-zu-DialOS.md`,
Schritt 11).

Die Taubheit kam durch das **Entfernen der Sperrfrist** herunter. Sie
sollte doppeltes Auslösen verhindern, war dafür aber überflüssig, seit die
Aufnahme nach jedem Sprechen verworfen und neu begonnen wird. Was sie
tatsächlich bewirkte: Nach einem Umschalten liefen 2,4 s Skript samt
Ansage, 2,0 s Sperrfrist und 0,7 s Nachhall-Pause - die Ansage endete
aber nach 1,5 s. Der Nutzer hörte also die Antwort und sprach 3,6
Sekunden gegen ein taubes System.

**Die Lehre, die über diesen Fall hinausgeht:** „Ich muss lauter reden"
ist als Fehlerbeschreibung fast immer irreführend. Zweimal an einem Tag
war die Ursache eine Zeitspanne, in der das System nicht zuhörte - und
beide Male klang die Meldung nach einem Pegelproblem. Wer so eine Meldung
bekommt, sollte zuerst fragen, **welcher** Befehl in der Reihe nicht
ankam: Stephans Präzisierung „den *zweiten* Befehl" hat den Fall beide
Male aufgeklärt.

## Welches Mikrofon? (festgelegt 2026-08-17)

**Immer das eingebaute.** Kein Bluetooth, kein USB - die Begründung steht
in `hardware.md`, Abschnitt „Was bleibt". Kurz: Solange DialOS nie ein
Bluetooth-Mikrofon öffnet, kann das Gerät nicht in Telefonqualität
rutschen, und ein Mikrofon, das man ausschalten kann, gefährdet über die
Echo-Unterdrückung die ganze Tonausgabe.

Fällt das eingebaute Mikrofon aus, gibt es **keine** Rückfallebene mehr -
das ist Absicht. Der Dienst sagt es dann an („Ich finde kein Mikrofon.")
statt still tot zu sein.

## Offene Punkte

- Wake-Word-Engine noch nicht final entschieden.
