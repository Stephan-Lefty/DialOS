# Sprachsteuerung

## Stack

- **Spracherkennung (STT)**: Vosk mit deutschem Modell, offline.
- **Sprachausgabe (TTS)**: Piper oder RHVoice (natürlicher als
  espeak-ng), als Backend für Orca.
- **Screenreader**: Orca (Standard-GNOME-Screenreader).
- **Low-Level-Desktopsteuerung** (Maus, Fenster): Numen – Wayland-nativ,
  ebenfalls Vosk-basiert, Open Source.
- **Intent-Erkennung**: flexible/LLM-gestützte Zuordnung statt starrer
  Befehlsgrammatik (siehe unten).

## Intent-Erkennung: flexibel statt starr

Eine starre Befehlsgrammatik (exakte Formulierungen wie bei klassischen
Sprachassistenten-Frameworks) passt schlecht zur Anforderung, dass das
System für 18-Jährige genauso einfach sein muss wie für 80-Jährige –
unterschiedliche Generationen formulieren denselben Befehl
unterschiedlich ("Ruf Anna an" vs. "Verbind mich mit Anna" vs.
"Telefonier mal mit Anna").

Deshalb: ein kleines, lokal laufendes Sprachmodell interpretiert die
Vosk-Transkription und ordnet sie der passenden Aktion zu, statt exakte
Formulierungen zu erwarten. Die Flexibilität gilt fürs **Verstehen**,
nicht fürs **Ausführen** – sicherheitskritische Aktionen (Systemwartung,
Freigabe der Fernwartung) bleiben immer hinter einer expliziten
Ja/Nein-Rückfrage, unabhängig davon, wie der Befehl erkannt wurde.

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

- Konkrete Intent-Schicht (eigene Middleware vs. bestehendes Framework
  wie Rhasspy als Ausgangsbasis) noch nicht festgelegt.
- Wake-Word-Engine noch nicht final entschieden.
