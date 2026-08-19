[Deutsch](sprachbefehle.md) | [English](sprachbefehle.en.md)

# Sprachbefehle

Die Liste aller Sprachbefehle von DialOS. Sie wächst mit jedem neuen
Befehl mit und ist die Stelle, an der nachgesehen wird, was das System
versteht.

**Zwei getrennte Tabellen, und das mit Absicht:** Was gebaut ist, und was
vorgesehen ist. Vermischt sähe Geplantes wie Vorhandenes aus - genau der
Fehler, der in diesem Projekt schon einmal aufgeräumt werden musste.

Welches Programm für welchen Zweck benutzt wird, steht in
[anwendungen.md](anwendungen.md) - diese Datei beantwortet „welcher
Satz", jene „welches Programm".

**Wie das klingt**, steht als Hörbeispiele in
[sprachbeispiele/](sprachbeispiele/README.md) - dort liegen die Antworten
zu den Befehlen dieser Tabelle als Tondateien.

Technischer Hintergrund zur Erkennung steht in
[sprachsteuerung.md](sprachsteuerung.md), der Einbau in
[Debian-zu-DialOS.md](Debian-zu-DialOS.md) (Schritt 11c).

## Umgesetzt

Die Erkennung ist nach dem Anmelden **aus**. Bis auf „Sprachsteuerung
starten" hört DialOS dann auf nichts - das ist der eigentliche Schutz
davor, dass ein Gespräch oder das Radio etwas auslöst. Das Modell
dahinter steht in [sprachsteuerung.md](sprachsteuerung.md), Abschnitt
„Wann hört DialOS zu?".

| Sprachbefehl | Aktion |
|---|---|
| **„Sprachsteuerung starten"** | Schaltet die Befehlserkennung ein, Antwort: „Ich höre Dir zu." Läuft sie schon: „Ich höre Dir schon zu." |
| **„Sprachsteuerung stoppen"** | Schaltet sie wieder aus, Antwort: „Ich höre Dir nicht mehr zu." Nach zwei Minuten ohne Befehl geschieht das von selbst, mit Ansage. |
| „auf Windows umschalten" | Schaltet den Schreibtisch auf die Windows-11-Optik um (Taskleiste unten, Startmenü links, Fensterknöpfe rechts). Antwort: „Windows Desktop." Steht er schon so: „Steht schon auf Windows Desktop." |
| „auf Linux umschalten" | Schaltet zurück auf den GNOME-Standard. Antwort: „Linux Desktop." bzw. „Steht schon auf Linux Desktop." |
| „auf Gnome umschalten" | Gleichbedeutend mit „auf Linux umschalten". |
| **„Diktat starten"** | Startet das Diktat; alles Gesprochene wird Text und landet in `~/Notizen/notizen.txt`. Es sagt „Einen Moment, ich hole Zettel und Stift." (das grosse Sprachmodell braucht rund 9 s), dann „Ich schreibe mit." |
| **„Notiz aufnehmen"** | Gleichbedeutend mit „Diktat starten". |
| **„Einkaufszettel aufnehmen"** | Wie oben, schreibt aber nach `~/Notizen/einkaufszettel.txt` - eine Einkaufsliste zwischen Terminen und Gedanken wäre unbrauchbar. |
| **„Diktat beenden"** | Beendet ein laufendes Diktat, schreibt die Notiz und liest sie vor. Erkannt von einem **zweiten** Erkenner mit eigener Grammatik - in der freien Erkennung des Diktats wurde der Satz zu „diktat wird erhöht" (2026-08-18). Muss die **ganze** Äußerung sein, damit man ihn in einem Brief erwähnen kann. |
| **„Wie viel Uhr ist es?"** | „Es ist acht Uhr siebenundvierzig." Bei voller Stunde ohne Minutenangabe. |
| **„Wie ist die Uhrzeit?"** | Gleichbedeutend. |
| **„Welchen Tag haben wir?"** | „Heute ist Mittwoch, der neunzehnte August." Dieselbe Formulierung wie in der Start-Ansage, aus denselben Funktionen gebaut. |
| **„Welches Datum haben wir?"** | Gleichbedeutend. |
| **„Einkaufszettel vorlesen"** | Sagt die Anzahl der Einträge und liest sie vor, mit Pausen dazwischen. |
| **„Notizen vorlesen"** | Dasselbe für die Sammelnotiz. |
| **„Einkauf erledigt"** | Leert den Einkaufszettel - **mit Rückfrage**: „Der Einkaufszettel hat vier Einträge. Soll ich ihn löschen?" Antwort „ja" oder „nein". Der alte Inhalt wandert nach `einkaufszettel-verworfen.txt`, damit ein sehender Helfer ihn im Notfall zurückholen kann. |
| **„Einkaufszettel wegwerfen"** | Gleichbedeutend mit „Einkauf erledigt". Zwei Formulierungen für dasselbe, damit der Nutzer sich keine merken muss - wie bei „auf Linux" und „auf Gnome". |
| „100" / „75" / „50" / „25" / „aus" | Antwort auf die Lautstärke-Frage der Start-Ansage. Wird **einmalig** gemerkt; „aus" gilt bewusst nur für die laufende Anmeldung. |

## Vorgesehen, noch nicht gebaut

| Sprachbefehl | Aktion |
|---|---|
| „Hilfe rufen" | Startet RustDesk für die Fernwartung. Bewusst nur auf ausdrückliche Ansage, siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md). |
| „System aktualisieren" | Systemwartung mit Ja/Nein-Rückfrage vor der Ausführung. |
| „Radio hören" / „Musik hören" | Startet Shortwave bzw. Rhythmbox. |
| „Ruf {Person} an" | Telefonie über SIM oder gekoppeltes Handy, siehe [telefonie.md](telefonie.md). |

## Regeln, die für jeden neuen Befehl gelten

Sie sind nicht theoretisch - jede stammt aus einem Fehler, der schon
einmal aufgetreten ist:

- **Ein Befehl ist ein ganzer Satz, kein Einzelwort.** Ein beiläufiges
  „Windows" im Gespräch darf den Schreibtisch nicht umstellen. Beim Test
  am 2026-08-16 wurde „ich habe früher windows benutzt" als
  `auf auf windows` erkannt - mit dem Zielwort, aber ohne „umschalten",
  und blieb damit wirkungslos. Jeder Befehl braucht deshalb ein
  **Auslösewort** zusätzlich zum Ziel.
- **Ein Satz gilt auch, wenn der Erkenner ein Wort verschluckt - solange
  kein `[unk]` dabei ist.** Am 2026-08-19 sagte Stephan „Sprachsteuerung
  starten", der Erkenner lieferte `'starten'`, und die Bedingung auf den
  vollen Satz wies es ab. Die Sprachsteuerung liess sich damit nicht
  einschalten, und alles danach war unerreichbar. Seitdem genügt das
  **Kernwort**, wenn ausser Wörtern der Phrase nichts weiter vorkommt und
  kein `[unk]` dabei ist - dasselbe schon einen Tag vorher beim Schlusssatz
  des Diktats.
  - **Das Kernwort muss eindeutig sein.** „stoppen" kommt in genau einem
    Satz der Grammatik vor, genügt also immer. „starten" kommt in zwei vor
    („Sprachsteuerung starten" und „Diktat starten") - allein genügt es
    deshalb nur im **ausgeschalteten** Zustand, wo die Grammatik nur einen
    Satz kennt. Wer einen neuen Befehl mit einem schon benutzten Verb
    anlegt, muss das prüfen.
- **Sicherheitskritische Befehle bekommen eine Ja/Nein-Rückfrage**
  (Systemwartung, Fernwartung freigeben) - unabhängig davon, wie sicher
  die Erkennung war.
- **Jeder Befehl sagt an, was er getan hat.** Der Nutzer sieht den
  Bildschirm nicht; ohne Ansage weiß er nicht, ob etwas passiert ist.
- **Und er sagt es anders, wenn sich nichts geändert hat.** „Auf Linux
  umschalten", während der Schreibtisch schon auf Linux steht, gab
  dieselbe Ansage wie ein echter Wechsel - für Stephan nicht zu
  unterscheiden (gemeldet am 2026-08-17). Seitdem: „Steht schon auf Linux
  Desktop."
- **Ansagen kurz halten, aber als Satz.** Während das System spricht,
  hört es bewusst nicht zu - jede Sekunde Ansage ist eine Sekunde, in der
  der Nutzer warten muss. Acht Sekunden Erklärung waren zu viel, ein
  einzelnes „Windows." war zu wenig: ein Stichwort, das nicht erkennbar
  zum Befehl gehört.
- **Während eines Diktats gilt KEIN Befehl.** Das Diktat legt eine Marke
  an, und der Befehlsdienst hält sich heraus, solange sie da ist. Ohne das
  würde ein diktierter Satz auch als Befehl ausgewertet - wer „auf Windows
  umschalten" in einen Brief diktiert, hätte danach einen anderen
  Schreibtisch. Am 2026-08-18 mit Zeitstempeln in beiden Protokollen belegt.
  Der einzige Satz, der ein Diktat beendet, läuft über einen eigenen
  Erkenner.
- **Neue Wörter erst gegen das Modell prüfen - und zwar auf ZWEI Arten.**
  Nicht jedes Wort steht im Wortschatz: „gnome" wurde frei erkannt
  zuverlässig zu **„genug"**.
  - **Steht das Wort überhaupt im Wortschatz?** Vosk meldet es beim Bauen
    der Grammatik selbst: `Ignoring word missing in vocabulary`. Das geht
    sofort und ohne Sprechen und ist der schnellere der beiden Wege.
    Gefunden am 2026-08-18, weil **„löschen" nicht im Wortschatz steht** -
    Vosk hätte es still aus der Grammatik geworfen, der Befehl wäre nie
    ausgelöst worden, und im Protokoll hätte nur „einkaufszettel"
    gestanden. Ebenfalls nicht enthalten: „zurücksetzen", „aufräumen" - und **„spät"**,
    weshalb aus „Wie spät ist es?" die geprüften Formulierungen „Wie viel Uhr
    ist es?" und „Wie ist die Uhrzeit?" wurden (2026-08-19).
  - **Wird der ganze Satz richtig erkannt?** Piper spricht ihn, Vosk hört
    zu - und zwar mit der **vollständigen** Befehlsgrammatik, nicht nur mit
    dem neuen Satz allein. Erst dann zeigt sich, ob er mit einem
    bestehenden verwechselt wird. Beispiele in `docs/sprachsteuerung.md`.
- **Danach neu aufnehmen.** Spricht das System selbst, steht seine eigene
  Stimme anschließend in der Aufnahme-Warteschlange. Am 2026-08-17 hat
  sich der Dienst dadurch selbst zurückgeschaltet.
