[Deutsch](sprachbefehle.md) | [English](sprachbefehle.en.md)

# Sprachbefehle

Die Liste aller Sprachbefehle von DialOS. Sie wächst mit jedem neuen
Befehl mit und ist die Stelle, an der nachgesehen wird, was das System
versteht.

**Zwei getrennte Tabellen, und das mit Absicht:** Was gebaut ist, und was
vorgesehen ist. Vermischt sähe Geplantes wie Vorhandenes aus - genau der
Fehler, der in diesem Projekt schon einmal aufgeräumt werden musste.

Technischer Hintergrund zur Erkennung steht in
[sprachsteuerung.md](sprachsteuerung.md), der Einbau in
[Debian-zu-DialOS.md](Debian-zu-DialOS.md) (Schritt 11c).

## Umgesetzt

| Sprachbefehl | Aktion |
|---|---|
| „auf Windows umschalten" | Schaltet den Schreibtisch auf die Windows-11-Optik um (Taskleiste unten, Startmenü links, Fensterknöpfe rechts). |
| „auf Linux umschalten" | Schaltet zurück auf den GNOME-Standard. |
| „auf Gnome umschalten" | Gleichbedeutend mit „auf Linux umschalten". |
| „100" / „75" / „50" / „25" / „aus" | Antwort auf die Lautstärke-Frage der Start-Ansage. Wird **einmalig** gemerkt; „aus" gilt bewusst nur für die laufende Anmeldung. |

## Vorgesehen, noch nicht gebaut

| Sprachbefehl | Aktion |
|---|---|
| „Sprachsteuerung starten" | Schaltet die Befehlserkennung ein. Bis dahin hört DialOS nur auf diesen einen Satz. |
| „Sprachsteuerung stoppen" | Schaltet die Befehlserkennung wieder aus - für Gespräche, Besuch, Telefonate. |
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
- **Sicherheitskritische Befehle bekommen eine Ja/Nein-Rückfrage**
  (Systemwartung, Fernwartung freigeben) - unabhängig davon, wie sicher
  die Erkennung war.
- **Jeder Befehl sagt an, was er getan hat.** Der Nutzer sieht den
  Bildschirm nicht; ohne Ansage weiß er nicht, ob etwas passiert ist.
- **Neue Wörter erst gegen das Modell prüfen.** Nicht jedes Wort steht im
  Wortschatz: „gnome" wurde frei erkannt zuverlässig zu **„genug"**.
  Prüfmethode ohne Sprechen: Piper spricht den Satz, Vosk hört zu
  (Beispiele in `docs/sprachsteuerung.md`).
- **Danach neu aufnehmen.** Spricht das System selbst, steht seine eigene
  Stimme anschließend in der Aufnahme-Warteschlange. Am 2026-08-17 hat
  sich der Dienst dadurch selbst zurückgeschaltet.
