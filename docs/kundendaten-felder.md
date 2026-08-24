[Deutsch](kundendaten-felder.md) | [English](kundendaten-felder.en.md) | [Änderungsprotokoll](../README.md#änderungsprotokoll)

# Kundendaten: welche Felder DialOS braucht

Stephans Vorgabe vom 2026-08-24, entstanden aus der Frage, „wo wir zentral alle
wichtigen Daten des Kunden einmalig ablegen und die Mail, der Brief und das
Diktat usw. greifen auf diese Daten immer zu".

**Diese Datei enthält die FELDER, nicht die Werte.** Das ist keine
Ordnungsliebe: Das Repo ist **öffentlich** (am 2026-08-24 anonym geprüft,
`private: False`). Eine Anschrift oder Telefonnummer hier hineinzuschreiben
heißt, sie zu veröffentlichen. Dieselbe Trennung wie bei
`Wordpressinstallation/.env.example` — die Vorlage ins Repo, die Werte nur auf
das Gerät.

## Die Felder

Von Stephan am Beispiel seiner eigenen Person aufgestellt. Die Spalte „heute"
sagt, ob DialOS das Feld schon irgendwo kennt.

| Feld | heute | wer braucht es |
|---|---|---|
| `anrede` | nein | Brief (Empfängeranrede später), Mail |
| `vorname` | teilweise | Anrede beim Anmelden, Briefkopf |
| `name` | teilweise | Briefkopf, Mail-Signatur |
| `name_gesprochen` | **ja** | Sprachausgabe — siehe unten |
| `strasse` | nein | Briefkopf |
| `hausnummer` | nein | Briefkopf |
| `postleitzahl` | nein | Briefkopf |
| `wohnort` | nein | Briefkopf, Wetter als Rückfall |
| `bundesland` | nein | Briefkopf bei Behördenpost |
| `land` | nein | Briefkopf bei Auslandspost |
| `laenderkennzeichen` | nein | Briefkopf bei Auslandspost — gehört zur ANSCHRIFT |
| `festnetz` | nein | Brief („telefonisch erreichbar"), Telefonie |
| `handy_privat` | nein | dito |
| `handy_geschaeftlich` | nein | dito |
| `mailadresse` | nein | Mail-Signatur, Absender |

„Teilweise" heißt: `nutzer-name.txt` enthält heute einen Namen, aber nicht
getrennt nach Vor- und Nachname. Der Briefkopf setzt deshalb nur das eine Wort,
das dort steht.

### Ein Feld, das in Stephans Liste fehlte und nötig ist

**`name_gesprochen`** — wie der Name AUSGESPROCHEN wird, nicht wie er
geschrieben wird. Das gibt es schon, und aus gutem Grund: „Rösner" wird von
Piper auf dem „e" betont, richtig wäre die Betonung auf dem „ö". Stephan hat am
2026-08-22 aus mehreren Schreibweisen „Steffan" gewählt. In
`nutzer-name.txt` steht das heute als `Stephan | Steffan` — geschrieben,
gesprochen.

Ohne dieses Feld spricht das Gerät den Nutzer bei jeder Ansage falsch an. Wer
die Felder zusammenlegt, darf es nicht verlieren.

### Die Vorwahl gehört zur Nummer, nicht zum Land

Stephan am 2026-08-24: „Ich habe ein deutsches Handy und ein
österreichisches." Damit ist `laenderkennzeichen` **nicht** die Vorwahl: Es
gehört zur Postanschrift (bei Stephan `AT`), während jede Telefonnummer ihre
eigene Länderkennung trägt — `0049…` für das deutsche Gerät, `0043…` für das
österreichische.

Telefonnummern werden deshalb **vollständig in internationaler Form**
gespeichert, mit Vorwahl. Wer aus `laenderkennzeichen` eine Vorwahl ableitet,
wählt bei einem der beiden Geräte falsch — und das fällt erst auf, wenn jemand
nicht erreicht wird.

### Felder, die bewusst NICHT dazugehören

- **`assistent-name.txt`** (Michael/Anna) ist eine Systemeinstellung, keine
  Kundendatei. Sie wechselt mit der Stimme, nicht mit der Person.
- **`fusszeile.txt`** ist der Werbesatz von DialOS und für alle Geräte
  derselbe.
- **Die Mailbox-Zugangsdaten** bleiben getrennt (heute eine Datei in
  `/home/nutzer`, Rechte 0600). Ein Passwort gehört nicht in dieselbe Datei wie
  eine Postanschrift: Die eine liest ein Helfer beim Einrichten vor, die andere
  darf er nie sehen.

Diese Trennlinie gehört gezogen, bevor etwas gebaut wird. Sonst wandert am Ende
alles in eine Datei, und beim Gerätewechsel weiß niemand mehr, was zu löschen
ist.

## Die Vorlage

Ein Feld je Zeile, `schlüssel = wert`, UTF-8. Leere Felder bleiben leer und
werden übersprungen — nicht mit Platzhaltern füllen: Ein Briefkopf mit
„Musterstraße" wäre schlimmer als einer ohne Straße, weil ein blinder Nutzer
die Lücke nicht sieht.

```ini
# Kundendaten. NICHT ins Repo - das ist oeffentlich.
# Leere Felder bleiben leer und werden uebersprungen.

anrede              =
vorname             =
name                =
name_gesprochen     =

strasse             =
hausnummer          =
postleitzahl        =
wohnort             =
bundesland          =
land                =
laenderkennzeichen  =

festnetz            =
handy_privat        =
handy_geschaeftlich =

mailadresse         =
```

## Was noch nicht entschieden ist

**Wohin die Datei kommt.** Heute liegen die Nutzerdaten in
`/usr/local/share/dialos/` — auf der **unverschlüsselten** Wurzelpartition,
Rechte 0644, während `/home/nutzer` mit LUKS verschlüsselt ist. Am 2026-08-24
gemessen:

    /usr/local/share/dialos/nutzer-name.txt  →  /dev/nvme0n1p1  ext4  0644
    /home/nutzer                             →  nvme0n1p4       LUKS

Für einen Namen ist das schon fragwürdig; für Anschrift und Telefonnummer wäre
es der Widerspruch zum ganzen Verschlüsselungsansatz.

**Die Startreihenfolge ist KEIN Hindernis** — das stand hier zuerst anders und
war falsch (berichtigt am 2026-08-24, nachdem Stephan nachgefragt hat).
Nachgesehen in `dialos-stick-gate.service` und `-.sh`: Der Dienst läuft mit
`Before=display-manager.service`, mountet `/home/nutzer` und schaltet **danach**
Autologin ein. Ohne Stick sperrt er das Konto zusätzlich mit `usermod -L` — im
Skript ausdrücklich begründet, weil eine Sitzung sonst „gegen ein Verzeichnis
auf der UNVERSCHLÜSSELTEN root-Partition" liefe. **Wenn `nutzer` eine Sitzung
hat, ist die Partition also immer gemountet**, und die Start-Ansage ist ein
XDG-Autostart innerhalb dieser Sitzung. Der Fehler war, „nach dem Booten" mit
„nach dem Anmelden" zu verwechseln.

**Zwei echte Einschränkungen bleiben, beide kleiner:**

- **Der Gate selbst** läuft vor dem Mount und könnte die Daten nie lesen. Heute
  spricht er nicht, nur ins Journal. Sollte er einmal „Bitte Sicherheits-Stick
  einstecken" sagen, könnte er den Namen nicht verwenden.
- **Das Admin-Konto** käme nicht heran; `/home/dialosadmin` liegt auf der
  Wurzelpartition. Ein Brief, der zum Testen dort geschrieben wird, hätte keinen
  Absender. Das ist wahrscheinlich richtig — es sind die Daten des Kunden —,
  muss aber eine bewusste Entscheidung sein und kein Nebeneffekt.

**Deshalb steht hier nur die Struktur.** Die Werte einzutragen lohnt erst, wenn
klar ist, wohin sie gehören — sonst müssten sie zweimal erfasst werden, und
beim zweiten Mal bleibt die erste Kopie liegen.
