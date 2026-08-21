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
| **„Sprachsteuerung starten"** | Schaltet die Befehlserkennung ein, Antwort: „Ich höre Dir zu." Läuft sie schon: „Ich höre Dir schon zu." Öffnet zugleich das [Mitschrift-Fenster](Debian-zu-DialOS.md) für sehende Zuschauer - einmal, nicht bei jedem Befehl. |
| **„Sprachsteuerung stoppen"** | Schaltet sie wieder aus, Antwort: „Ich höre Dir nicht mehr zu." Von selbst geschieht das nach **30 Sekunden**, wenn überhaupt kein Befehl kam, und nach **zwei Minuten** im laufenden Gespräch - mit unterschiedlicher Ansage: die lange Begründung nur dann, wenn wirklich ein Gespräch lief. Das Mitschrift-Fenster geht in beiden Fällen mit zu. |
| „auf Windows umschalten" | Schaltet den Schreibtisch auf die Windows-11-Optik um (Taskleiste unten, Startmenü links, Fensterknöpfe rechts). Antwort: „Windows Desktop." Steht er schon so: „Der Schreibtisch steht schon auf Windows Desktop." |
| „auf Linux umschalten" | Schaltet zurück auf den GNOME-Standard. Antwort: „Linux Desktop." bzw. „Der Schreibtisch steht schon auf Linux Desktop." |
| „auf Gnome umschalten" | Gleichbedeutend mit „auf Linux umschalten". |
| **„Diktat starten"** | Startet das Diktat; alles Gesprochene wird Text und landet in `~/Notizen/notizen.txt`. Es sagt „Einen Moment, ich hole Zettel und Stift." (das grosse Sprachmodell braucht rund 9 s), dann „Ich schreibe mit." |
| **„Notiz aufnehmen"** | Gleichbedeutend mit „Diktat starten". |
| **„Einkaufszettel aufnehmen"** | Wie oben, sagt aber „Sage jede Ware einzeln, mit einer kleinen Pause dazwischen." und schreibt nach `~/Notizen/einkaufszettel.txt` - eine Einkaufsliste zwischen Terminen und Gedanken wäre unbrauchbar. |
| **„Diktat beenden"** | Beendet ein laufendes Diktat, schreibt die Notiz und sagt an, wie viele Einträge es geworden sind - **ohne vorzulesen** (Stephan, 2026-08-19): „Diktat beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel vorgelesen haben, dann sage: Einkaufszettel vorlesen." Erkannt von einem **zweiten** Erkenner mit eigener Grammatik - in der freien Erkennung des Diktats wurde der Satz zu „diktat wird erhöht" (2026-08-18). Muss die **ganze** Äußerung sein, damit man ihn in einem Brief erwähnen kann. |
| **„Wie viel Uhr ist es?"** | „Es ist acht Uhr siebenundvierzig." Bei voller Stunde ohne Minutenangabe. |
| **„Wie ist die Uhrzeit?"** | Gleichbedeutend. |
| **„Welchen Tag haben wir?"** | „Heute ist Mittwoch, der neunzehnte August." Dieselbe Formulierung wie in der Start-Ansage, aus denselben Funktionen gebaut. |
| **„Welches Datum haben wir?"** | Gleichbedeutend. |
| **„Bildschirmfoto erstellen"** | Legt ein Foto des Bildschirms unter `~/Bilder/Bildschirmfotos/` ab, mit Datum und Uhrzeit im Namen, und sagt „Das Bildschirmfoto ist gespeichert." **Nicht für den Nutzer** - er sieht es nicht -, sondern für den sehenden Helfer und den Support: „Was steht da gerade?" lässt sich sonst nicht beantworten. Das Gerät hat kein Screenshot-Werkzeug installiert und die GNOME-Schnittstelle ist gesperrt; DialOS geht deshalb über das XDG-Portal - **ohne Rückfrage**, denn ein Dialog wäre hier dasselbe wie keine Funktion. Das **Mitschrift-Fenster wird vorher geschlossen** und danach wieder geöffnet - es ist DialOS' eigene Anzeige und verdeckt auf einem Support-Foto genau das, was der Helfer sehen will. |
| **„Bildschirmfoto machen"** | Gleichbedeutend. |
| **„Einkaufszettel vorlesen"** | Sagt die Anzahl der Einträge und liest sie vor, mit Pausen dazwischen. |
| **„Notizen vorlesen"** | Dasselbe für die Sammelnotiz. |
| **„Einkauf erledigt"** | Leert den Einkaufszettel - **mit Rückfrage**: „Der Einkaufszettel hat vier Einträge. Soll ich ihn löschen? Sage ja oder nein." Kommt keine verwertbare Antwort, fragt DialOS **ein zweites Mal** („Das habe ich nicht verstanden. Sage ja oder nein."); erst danach bleibt der Zettel stehen. Der alte Inhalt wandert nach `einkaufszettel-verworfen.txt`, damit ein sehender Helfer ihn im Notfall zurückholen kann. |
| **„Einkaufszettel wegwerfen"** | Gleichbedeutend mit „Einkauf erledigt". Zwei Formulierungen für dasselbe, damit der Nutzer sich keine merken muss - wie bei „auf Linux" und „auf Gnome". |
| **„ja" / „nein"** | Antwort auf eine Rückfrage - bisher nur vor dem Leeren einer Notiz. Gilt **nur während der Rückfrage**: dafür läuft ein eigener Erkenner mit einer Grammatik aus genau diesen zwei Wörtern, der Befehlsdienst hält sich heraus. Kommt nichts Verwertbares, wird einmal nachgefragt, danach bleibt der Zettel stehen. |
| **„Hilfe rufen"** ⏸ **zurückgestellt** | *Nicht in der Grammatik, siehe unten.* Startet die Fernwartung - **mit Rückfrage**, die erklärt, was passiert: „Dein Betreuer kann dann sehen, was auf dem Bildschirm steht, und das Gerät bedienen. Soll ich sie starten? Sage ja oder nein." Danach wird die RustDesk-Nummer **ziffernweise und zweimal** vorgelesen. Während einer laufenden Sitzung **verlängert** derselbe Satz sie um eine Stunde. Danach fragt DialOS nach: „Hast Du das Deinem Betreuer weitergegeben?" - bei „nein" oder wenn nichts verstanden wurde: „Soll ich es wiederholen?" Höchstens zwei Wiederholungen, danach der Hinweis, dass „Hilfe rufen" die Zahlen jederzeit wiederholt. Der Nutzer sieht die Zahlen nicht und kann nichts mitschreiben; ein wartender Betreuer und ein Nutzer, der die Hälfte verloren hat, sind der wahrscheinlichste Fehlerfall dieses Befehls. |
| **„Fernwartung beenden"** ⏸ **zurückgestellt** | Beendet sie. „Niemand kann mehr zusehen." Passiert auch von selbst nach einer Stunde, mit Vorwarnung drei Minuten vorher. Kernwort ist **„fernwartung"** und nicht „beenden": Letzteres kennt der Nutzer als Schlusswort des Diktats, und ein Wort in zwei Rollen ist beim Sprechen zweideutig, auch wenn die Grammatik es nicht ist. |
| „100" / „75" / „50" / „25" / „aus" | Antwort auf die Lautstärke-Frage der Start-Ansage. Wird **einmalig** gemerkt; „aus" gilt bewusst nur für die laufende Anmeldung. |

> **⏸ Zurückgestellt am 2026-08-20** (Stephan: „können den Rustdesk ganz nach
> hinten schieben, wenn alles andere läuft"). „Hilfe rufen" und „Fernwartung
> beenden" stehen **nicht** in der Grammatik und sind damit nicht auslösbar.
>
> **Nicht nur verschoben, sondern abgeschaltet - und das ist der Punkt:** Der
> Befehl war halb gebaut und installiert. Er startet die RustDesk-**Anwendung**,
> und die stürzt ohne den systemd-Dienst nach rund 40 Sekunden ab („Got signal 11
> and exit", am 2026-08-19 im Protokoll belegt). Der Nutzer bekäme die ID
> vorgelesen, sein Betreuer könnte sich nicht verbinden - und beim nächsten Mal
> glaubt er dem Gerät nicht mehr. **Ein Sprachbefehl, der halb funktioniert, ist
> schlimmer als einer, der nicht existiert**, und ausgerechnet bei dem, mit dem
> Hilfe geholt wird, wenn nichts mehr geht.
>
> Der Code bleibt vollständig liegen - `dialos-hilfe.py` mit Rückfrage, Wache,
> Zeitgrenze und Nachfragen. Wieder freigeben heißt: zwei Zeilen in
> `GRAMMATIK_AN` und zwei in `HILFE_SAETZE` einkommentieren. Was vorher fehlt,
> steht als erster Punkt in `TODO.md`.

## Vorgesehen, noch nicht gebaut

| Sprachbefehl | Aktion |
|---|---|
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
    Satz der Grammatik vor, genügt also immer.
  - **Und es muss LANG genug sein - das ist die teurere Lehre**
    (2026-08-20). Bis dahin galt beim Einschalten „starten" als Kernwort. Über
    157 aufgezeichnete Äußerungen gemessen: **18-mal `'starten'` allein gegen
    4-mal den vollen Satz.** Kurze, häufige Wörter entstehen aus
    Umgebungsgeräusch, und die Sprachsteuerung hat sich dadurch 18-mal von
    selbst eingeschaltet - jedes Mal für zwei Minuten offenes Mikrofon.
    Am 2026-08-20 um 14:04 kam in einer dieser Phasen aus reinem Geräusch
    `'hilfe rufen'`, und die Fernwartung wurde angefordert, ohne dass jemand
    etwas gesagt hatte. Nur die Ja/Nein-Rückfrage hat es verhindert.
    Zuerst wurde das Kernwort auf **„sprachsteuerung"** umgestellt: lang,
    markant, in nur 16 von 157 Äußerungen vorgekommen.
  - **Und am selben Abend weiter auf BEIDE Wörter**, weil auch das noch nicht
    reichte. Zwei Stunden Betrieb, dieselben Daten durch alle drei Regeln
    gerechnet:

    | verlangt | Einschaltungen in 2 Std. |
    |---|---|
    | Kernwort „starten" | **30** |
    | Kernwort „sprachsteuerung" | 7 |
    | **beide Wörter** | **3** |

    Die 27 Fehlstarts der ersten Regel kamen aus `'starten'` allein, vier der
    sieben aus `'sprachsteuerung'` allein - und auf **keine** der sieben folgte
    ein Befehl. Zwei bestimmte Wörter hintereinander fallen im Gespräch
    praktisch nicht; eines schon.

    Der Preis ist bewusst in Kauf genommen: Verschluckt der Erkenner eines der
    beiden, muss der Nutzer den Satz wiederholen. Genau dieser Fehler hatte am
    2026-08-19 zur Lockerung geführt - nur liegt die Gegenrechnung inzwischen
    gemessen vor. Wiederholen ist eine Unbequemlichkeit; ein Mikrofon, das sich
    von selbst scharf schaltet, ist es nicht.
  - **Vertauschte oder doppelte Wörter zählen weiter.** Geprüft wird als
    **Menge**, nicht als Zeichenkette - der Erkenner liefert Wörter auch
    doppelt oder in anderer Reihenfolge („sprachsteuerung sprachsteuerung
    stoppen" kam vor). Nur `[unk]` schließt aus: dann war noch etwas anderes
    dabei.
- **Eine Bedienregel, die der Nutzer nicht sehen kann, muss gesagt werden.**
  Ein Einkaufszettel entsteht nur dann als Liste, wenn zwischen den Waren eine
  kleine Pause liegt - das war von Anfang an so gebaut, aber nie angesagt. Am
  2026-08-19 diktierte Stephan „Milch sechs Eier Butter" in einem Zug und hatte
  einen einzigen Eintrag. Ein sehender Nutzer hätte es nach der ersten Ware
  gemerkt; ein blinder erfährt es erst beim Vorlesen, eine Minute später.
- **Ein Befehl nimmt dem Nutzer keine Entscheidung ab, die er selbst
  treffen kann.** „Diktat beenden" las bis zum 2026-08-19 den ganzen Zettel
  vor. Damit war „Einkaufszettel vorlesen" überflüssig - und wer drei Waren
  aufgeschrieben hatte, musste sie ein zweites Mal hören. Seitdem sagt DialOS
  die Anzahl und **wie** man das Vorlesen bekommt. Eine Rückfrage wäre der
  falsche Weg gewesen: sie verlangt eine Antwort, ein Hinweis nicht.
  - **Ein Hinweis darf nur Sätze nennen, die es gibt.** Der Hinweis kommt aus
    einer Tabelle mit genau den Zielen, für die ein Vorlese-Befehl in dieser
    Datei steht. Ein unbekanntes Ziel bekommt nur die Bestätigung - einem
    blinden Nutzer einen Satz zu nennen, den die Grammatik nicht kennt, wäre
    schlimmer als kein Hinweis.
- **Sicherheitskritische Befehle bekommen eine Ja/Nein-Rückfrage**
  (Systemwartung, Fernwartung freigeben) - unabhängig davon, wie sicher
  die Erkennung war.
  - **Die erwarteten Wörter gehören in die Frage.** „Soll ich ihn löschen?"
    allein sagt einem blinden Nutzer nicht, was er antworten soll - es gibt
    keine Knöpfe zu sehen. Seit dem 2026-08-19: „Soll ich ihn löschen? Sage ja
    oder nein."
  - **Wer die Frage stellt, muss auch zuhören.** Bis zum 2026-08-19 sprach der
    Aufrufer die Frage und rief danach die Antwortfunktion - die erst dann das
    Sprachmodell lud und anschließend die Aufnahme startete. Stephans „ja" fiel
    in genau diese Lücke; im Protokoll stand keine einzige „Antwort
    gehoert"-Zeile. Seitdem stellt die Antwortfunktion die Frage **selbst**, und
    alles Langsame passiert davor. Dieselbe Fehlerklasse gab es schon am
    2026-08-15 (Start-Ansage) und am 2026-08-18 (Diktat-Marke) - die Reihenfolge
    „erst bereit sein, dann fragen" ist deshalb keine Feinheit, sondern Regel.
  - **Während der Frage wird nicht aufgenommen.** Die Grammatik kennt nur „ja",
    „nein" und „[unk]" - die eigene Stimme des Systems könnte darin als „ja"
    landen und den Zettel löschen, ohne dass jemand etwas gesagt hat. Ein
    Löschen ohne Zustimmung ist der schlimmere Fehler.
  - **Eine Nachfrage statt eines Abbruchs.** Kommt keine verwertbare Antwort,
    wird einmal nachgefragt. Ohne das müsste der Nutzer den ganzen Befehl neu
    sprechen, obwohl nur ein Wort gefehlt hat.
- **Es soll sich wie ein Dialog zwischen dem Nutzer und Michael anfühlen**
  (Stephans Grundsatz, 2026-08-19). Das ist die Regel, aus der die anderen
  Formulierungsregeln folgen, und sie hat einen praktischen Grund: Wer den
  Bildschirm nicht sieht, hat nichts als diese Stimme. Eine Zustandsmeldung
  lässt ihn allein, ein Satz nicht.
  - **Michael spricht den Nutzer an** („Ich höre **Dir** zu.", „Möchtest **Du**
    Deinen Einkaufszettel vorgelesen haben", „Sage ja oder nein.") und **von
    sich** („**Ich** schreibe mit.", „**Ich** habe nichts verstanden.").
  - **Und das Wort dazwischen kann entscheiden, ob der Satz stimmt.** „Du hast
    eine Weile nichts gesagt." war falsch, wenn im Raum gesprochen wurde - der
    Zähler läuft ab dem letzten **Befehl**, nicht ab der letzten Äußerung.
    Stephans „Du hast **mir** eine Weile nichts gesagt." ist richtig, weil das
    „mir" den Satz auf das begrenzt, was Michael gesagt wurde. Aus einem Wort
    Höflichkeit wurde eine Wahrheitsbedingung.
  - **Ausnahmen sind die kurzen Rückmeldungen auf eine Umschaltung**
    („Windows Desktop.", „Ton über Lautsprecher."). Sie sind bewusst so kurz,
    weil der Nutzer dort weitermachen will - siehe die Regel zur Länge unten.
- **Jeder Befehl sagt an, was er getan hat.** Der Nutzer sieht den
  Bildschirm nicht; ohne Ansage weiß er nicht, ob etwas passiert ist.
- **Und er sagt es anders, wenn sich nichts geändert hat.** „Auf Linux
  umschalten", während der Schreibtisch schon auf Linux steht, gab
  dieselbe Ansage wie ein echter Wechsel - für Stephan nicht zu
  unterscheiden (gemeldet am 2026-08-17). Seitdem: „Steht schon auf Linux
  Desktop."
- **Ansagen kurz halten, aber als Satz.** Während das System spricht,
  hört es bewusst nicht zu - jede Sekunde Ansage ist eine Sekunde, in der
  der Nutzer warten muss.
  - **Es kommt darauf an, ob der Nutzer wartet.** Diese Regel stammt von der
    Desktop-Umschaltung, wo er weitermachen will. Nach einem **beendeten**
    Diktat wartet nichts - deshalb darf der Hinweis dort 8 s dauern, und
    Stephan hat das am 2026-08-19 nach dem Vergleich von vier gemessenen
    Varianten so entschieden. Die Sekunden sind nicht das Maß; das Maß ist,
    was dem Nutzer im Weg steht. Messungen in
    [sprachbeispiele/README.md](sprachbeispiele/README.md). Acht Sekunden Erklärung waren zu viel, ein
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
