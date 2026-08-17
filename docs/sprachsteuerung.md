[Deutsch](sprachsteuerung.md) | [English](sprachsteuerung.en.md)

# Sprachsteuerung

## Stack

- **Spracherkennung (STT)**: Vosk mit deutschem Modell, offline.
- **Sprachausgabe (TTS)**: Piper (natürlicher als espeak-ng), als
  Backend für Orca - RHVoice stand zur Wahl und ist verworfen.
- **Screenreader**: Orca (Standard-GNOME-Screenreader).
- **Low-Level-Desktopsteuerung** (Maus, Fenster): Numen – Wayland-nativ,
  ebenfalls Vosk-basiert, Open Source.
- **Intent-Erkennung**: [hassil](https://github.com/OHF-Voice/hassil)
  (Home Assistant Intent Language) - lernfähige Zuordnung über
  Beispielsatz-Vorlagen statt starrer Befehlsgrammatik (siehe unten).

## Stand der Umsetzung (2026-08-16)

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

**Zur Wortwahl, unabhängig von der Technik: der Name des Assistenten.**
Also „Hallo Michael", bei einer weiblichen Stimme „Hallo Anna". Zwei
Gründe: Zwei Wörter lösen deutlich seltener versehentlich aus als eines,
und der Name steht ohnehin schon fest - der Nutzer wählt seine Stimme bei
der Ersteinrichtung **mit Namen** (siehe
[ersteinrichtung.md](ersteinrichtung.md): Michael, Daniel, Anna, Julia).
Das Weckwort käme damit aus derselben Einstellung wie die Stimme, ohne
dass irgendwo ein zweiter Wert gepflegt werden muss.

**Was ein Aufweckwort NICHT löst:** Das Mikrofon-Symbol in der oberen
Leiste bleibt an. Um das Weckwort zu hören, muss weiter zugehört werden -
die Aufnahme bleibt also offen. Das ist auch richtig so: Das Gerät hört
tatsächlich zu, und bei einer Zielgruppe, die den Bildschirm nicht sieht,
wäre es das Schlechteste, genau das zu verstecken. Entscheidend ist, dass
nichts das Gerät verlässt - Vosk läuft vollständig offline.

## Offene Punkte

- Wake-Word-Engine noch nicht final entschieden.
