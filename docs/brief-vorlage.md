[Deutsch](brief-vorlage.md) | [Änderungsprotokoll](../README.md#änderungsprotokoll)

# Brief-Vorlage zum Einsprechen

*Der Diktattext ist bewusst nur auf Deutsch vorhanden: Er existiert, um
gesprochen zu werden, und die gesprochenen Satzzeichen sind deutsche Befehle.
Eine Übersetzung wäre ein anderer Test, nicht derselbe in einer anderen
Sprache.*

Stephans Vorschlag vom 2026-08-24: „Du erstellst einen Brief mit Adresse,
Datum, Betreff und einen Text aus 3 Absätzen, Grußwort … Den werden wir als
Vorlage nehmen und dann einsprechen bis er sitzt."

**Wozu diese Datei gut ist:** Ein fester Text macht aus „läuft nicht rund" eine
Abweichung, die man zeigen kann. Nach jedem Versuch lässt sich Zeile für Zeile
vergleichen, was ankam und was nicht — statt nach Gefühl zu urteilen.

---

## 1. Das Zielbild — so soll der Brief aussehen

Ein vollständiger Brief nach DIN 5008. **Achtung: Das ist noch nicht, was
DialOS heute erzeugt** — siehe Abschnitt 2.

```
                                                        Stephan Rösner
                                                        Musterweg 12
                                                        6100 Seefeld in Tirol

                                                        24. August 2026

Muster Versicherung AG
Kundenservice
Beispielgasse 7
6020 Innsbruck


Antrag auf Kostenerstattung, Vertragsnummer 4711


Sehr geehrte Damen und Herren,

am zwölften August war ich in Behandlung bei Frau Doktor Muster. Die Rechnung
über zweihundertvierzig Euro habe ich bereits selbst bezahlt.

Ich bitte Sie, mir diesen Betrag zu erstatten. Die Rechnung liegt dem
Schreiben bei. Sollten Ihnen Unterlagen fehlen, teilen Sie mir das bitte mit.

Über eine Antwort bis Ende des Monats wäre ich dankbar. Für Rückfragen bin ich
telefonisch erreichbar.

Mit freundlichen Grüßen
Stephan Rösner

Dieser Brief wurde per Spracheingabe erstellt und ist deshalb nicht
unterschrieben.

              Dieses Dokument wurde per Spracheingabe powered by DialOS.org erstellt!
```

## 2. Was DialOS heute davon kann — und was nicht

Geprüft am 2026-08-24 an `briefbogen()` in `dialos-diktat.py` und an dem
zuletzt erzeugten `~/Dokumente/brief.txt`.

| Teil | heute | Anmerkung |
|---|---|---|
| Absender rechtsbündig | **teilweise** | Nur der Name. `/usr/local/share/dialos/absender.txt` fehlt, deshalb keine Straße und kein Ort. |
| Datum rechtsbündig, ausgeschrieben | **ja** | „24. August 2026" |
| Empfängeranschrift | **nein** | Wird nicht gefragt und nicht gesetzt. |
| Betreffzeile | **nein** | Dito. |
| Anrede, Text, Grußformel | **ja** | Kommt vollständig aus dem Diktat. |
| Absätze | **ja** | Über „neuer Absatz". |
| Unterschriftshinweis | **ja** | Automatisch, linksbündig. |
| Fußzeile | **ja** | Automatisch, rechtsbündig. |

**Damit ist die Vorlage zugleich die Anforderung** an den geführten Dialog, der
noch fehlt: Empfänger und Betreff müssen erfragt werden. Solange es den nicht
gibt, ist Abschnitt 3 der Teil, der sich wirklich einsprechen lässt.

**Die Anschrift lässt sich sofort nachtragen** — dafür braucht es keinen Code,
nur die Datei. Sie steht bewusst nicht im Abbild, weil sie dem Nutzer gehört:

```bash
printf 'Musterweg 12\n6100 Seefeld in Tirol\n' | sudo tee /usr/local/share/dialos/absender.txt
```

## 3. Der Diktattext — Wort für Wort so sprechen

**Vorher:** „Sprachsteuerung starten", dann „Brief aufnehmen" (oder „Brief
schreiben").

Die **fett** gesetzten Stellen sind gesprochene Befehle, kein Brieftext. Nach
jedem Absatz eine kurze Atempause — nicht nötig, aber es hilft dem Erkenner.

> Sehr geehrte Damen und Herren **komma setzen** **neuer Absatz**
>
> am zwölften August war ich in Behandlung bei Frau Doktor Muster **punkt
> setzen** Die Rechnung über zweihundertvierzig Euro habe ich bereits selbst
> bezahlt **punkt setzen** **neuer Absatz**
>
> Ich bitte Sie **komma setzen** mir diesen Betrag zu erstatten **punkt
> setzen** Die Rechnung liegt dem Schreiben bei **punkt setzen** Sollten Ihnen
> Unterlagen fehlen **komma setzen** teilen Sie mir das bitte mit **punkt
> setzen** **neuer Absatz**
>
> Über eine Antwort bis Ende des Monats wäre ich dankbar **punkt setzen** Für
> Rückfragen bin ich telefonisch erreichbar **punkt setzen** **neuer Absatz**
>
> Mit freundlichen Grüßen **neue Zeile** Stephan Rösner

**Danach: eine Sprechpause, dann „Diktat beenden".** Die Pause ist Pflicht —
seit dem 2026-08-22 verlangt der Schluss sie ausdrücklich, weil sonst ein
„diktat beenden" mitten aus dem Fließtext das Diktat abgebrochen hat.

### Warum der Text so gebaut ist

- **Er enthält die Wörter „Diktat" und „beenden" nicht.** Auch wenn der
  Schluss inzwischen eine Pause davor verlangt: Ein Testtext, der die
  Abbruchbedingung in sich trägt, prüft nicht den Brief, sondern die
  Abbruchlogik.
- **Er übt vier verschiedene Satzzeichen-Befehle** — Komma, Punkt, neuer
  Absatz, neue Zeile. Doppelpunkt, Fragezeichen, Ausrufezeichen und
  Gedankenstrich fehlen bewusst: Sie kommen in einem echten Brief selten vor,
  und ein Testtext, der alles einmal enthält, ist kein Brief mehr.
- **Er enthält Umlaute und ein ß** („Über", „wäre", „Grüßen"). Die
  Groß-/Kleinschreibung übernimmt LanguageTool; genau daran lässt sich sehen,
  ob sie trägt.
- **Er enthält ausgeschriebene Zahlen** („zwölften",
  „zweihundertvierzig"). Ziffern liefert das Modell nicht zuverlässig — wenn
  hier etwas schiefgeht, ist das ein eigener Befund und kein Zufall.
- **Er ist kurz genug**, um ihn mehrfach hintereinander zu sprechen. Ein Test,
  den man nur einmal am Tag machen will, findet keine Fehler.

## 4. Nach jedem Versuch

```bash
cat ~/Dokumente/brief.txt
```

Der vorige Brief wird nicht überschrieben, sondern als
`brief-JJJJ-MM-TT-HHMMSS.txt` daneben gelegt — mehrere Versuche lassen sich
also vergleichen.

Im Protokoll steht, was der Erkenner gehört hat:

```bash
tail -40 ~/.log/dialos-diktat.log
```

**Worauf zu achten ist:** fehlende Absätze (ein „neuer Absatz" ist
durchgefallen), zusammengezogene Sätze (ein „punkt setzen" fehlt), ein zu früh
beendetes Diktat, und ob die Groß-/Kleinschreibung am Satzanfang stimmt.
