[Deutsch](sprachsteuerung.md) | [English](sprachsteuerung.en.md)

# Sprachsteuerung

## Stack

- **Spracherkennung (STT)**: Vosk mit deutschem Modell, offline.
- **Sprachausgabe (TTS)**: Piper oder RHVoice (natürlicher als
  espeak-ng), als Backend für Orca.
- **Screenreader**: Orca (Standard-GNOME-Screenreader).
- **Low-Level-Desktopsteuerung** (Maus, Fenster): Numen – Wayland-nativ,
  ebenfalls Vosk-basiert, Open Source.
- **Intent-Erkennung**: [hassil](https://github.com/OHF-Voice/hassil)
  (Home Assistant Intent Language) - lernfähige Zuordnung über
  Beispielsatz-Vorlagen statt starrer Befehlsgrammatik (siehe unten).

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

## Offene Punkte

- Wake-Word-Engine noch nicht final entschieden.
