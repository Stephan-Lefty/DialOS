[Deutsch](einkaufszettel-vorlage.md) | [Brief-Vorlage](brief-vorlage.md) | [Änderungsprotokoll](../README.md#änderungsprotokoll)

# Einkaufszettel-Vorlage zum Einsprechen

*Nur auf Deutsch vorhanden, aus demselben Grund wie die Brief-Vorlage: Der Text
existiert, um gesprochen zu werden.*

Stephan am 2026-09-14: „Was mir aktuell noch Kopfzerbrechen macht ist der
Einkaufszettel. Gibt es noch 'bessere' Sprachsteuerungssysteme" - und danach:
„mache zu dem Brief noch einen Einkaufszettel fertig und dann testen wir
morgen beide Systeme!"

**Wozu diese Datei gut ist:** Ein fester Zettel macht aus „hat nur die Hälfte
verstanden" eine Zahl. Dieselbe Aufnahme läuft durch alle Erkenner - Vosk (wie
DialOS heute), Whisper und Parakeet -, und am Ende steht für jeden, wie viele
Waren wörtlich richtig ankamen und wie lange es gedauert hat.

**Das Messskript liest die Waren und den Brieftext direkt aus dieser Datei**
(zwischen den unsichtbaren Markierungen). Wer hier etwas ändert, ändert den
Maßstab - dann sind alte und neue Ergebnisse nicht mehr vergleichbar.

---

## 1. Die Waren

Jede Ware **einzeln**, mit **einer Sekunde Pause** dazwischen - so, wie DialOS
es ansagt („Sage jede Ware einzeln, mit einer kleinen Pause dazwischen").
Zahlen als Wörter sprechen, wie sie dastehen.

<!-- ZETTEL-ANFANG -->
- Bananen
- Pfirsiche
- Birnen
- Äpfel
- sechs Eier
- zwei Liter Milch
- Vollkornbrot
- fünfhundert Gramm Hackfleisch
- Mozzarella
- Zucchini
- Brokkoli
- Joghurt
- Kaffee
- Kakao
- Salz
- Reis
- Spülmittel
- Toilettenpapier
- Zahnpasta
- eine Kiste Mineralwasser
<!-- ZETTEL-ENDE -->

**Warum genau diese zwanzig:**

| Waren | Was sie prüfen |
|---|---|
| Bananen, Pfirsiche | die beiden Fehler vom 14.09.: „erahnen", „Pfizer" |
| Birnen, Äpfel | „Birnen Äpfel" kam als **ein** Eintrag an; Umlaut |
| sechs Eier, zwei Liter Milch, fünfhundert Gramm Hackfleisch | Mengenangaben - Whisper schreibt Ziffern, Vosk Wörter; das Skript gleicht das an |
| Vollkornbrot, Spülmittel, Toilettenpapier, Zahnpasta | lange zusammengesetzte Wörter |
| Mozzarella, Zucchini, Brokkoli, Joghurt | Fremdwörter mit schwankender Schreibweise |
| Kaffee / Kakao | ähnlich klingendes Paar |
| Salz, Reis | sehr kurze Wörter - leicht verschluckt |
| eine Kiste Mineralwasser | mehrere Wörter als eine Ware |

**Erwartung in DialOS:** 20 Einträge, jede Ware eine Zeile.

---

## 2. Ein Brief-Absatz - OHNE gesprochene Satzzeichen

Für den Vergleich wird der Brieftext **natürlich** vorgelesen, ohne „Komma
setzen" und „Punkt". Grund: Whisper und Parakeet setzen Satzzeichen selbst,
Vosk kann das nicht. Mit gesprochenen Satzzeichen würde der Vergleich die
Befehlswörter messen statt der Erkennung. (Das Einsprechen des Briefs **mit**
Satzzeichen-Befehlen in DialOS steht in der [Brief-Vorlage](brief-vorlage.md).)

<!-- BRIEF-ANFANG -->
Sehr geehrte Damen und Herren,

am zwölften August war ich in Behandlung bei Frau Doktor Muster. Die Rechnung
über zweihundertvierzig Euro habe ich bereits selbst bezahlt.

Ich bitte Sie, mir diesen Betrag zu erstatten. Die Rechnung liegt dem
Schreiben bei. Sollten Ihnen Unterlagen fehlen, teilen Sie mir das bitte mit.

Über eine Antwort bis Ende des Monats wäre ich dankbar. Für Rückfragen bin ich
telefonisch erreichbar.
<!-- BRIEF-ENDE -->

---

## 3. Ablauf am Testtag

Das Messprogramm liegt unter `scripts/dialos-erkenner-vergleich.py`, die
Erkenner im Ordner `erkenner-vergleich/` neben dem Repo (eingerichtet mit
`scripts/dialos-erkenner-einrichten.sh`). **Aufnahmen bleiben dort und kommen
nie ins Repo.**

1. **Einkaufszettel aufnehmen** - das Programm startet die Aufnahme, du liest
   Abschnitt 1 vor und drückst danach die Eingabetaste.
2. **Brief-Absatz aufnehmen** - genauso mit Abschnitt 2.
3. **Vergleichen** - das Programm schickt beide Aufnahmen durch alle Erkenner
   und schreibt eine Tabelle: Waren wörtlich richtig, Wortfehlerrate,
   Wartezeit je Ware.
4. **Gegenprobe in DialOS selbst** - „Einkaufszettel aufnehmen" wie im Alltag,
   derselbe Zettel. Das zeigt, ob die Aufnahme im Messprogramm dem entspricht,
   was DialOS wirklich hört.

Die genauen Befehle stehen am Testtag im Chat - je Schritt einer.
