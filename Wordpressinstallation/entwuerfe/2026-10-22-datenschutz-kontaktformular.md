# Datenschutzerklärung: Abschnitt zum Kontaktformular

**Entwurf vom 22.10.2026. Nicht veröffentlicht – wartet auf Stephans Freigabe.**

## Warum dieser Entwurf entstanden ist

Am 22.10.2026 wurde **Flamingo** installiert, damit nachlesbar ist, was der
neue Spamschutz aussortiert. Damit hat sich die Datenverarbeitung auf
dialos.org geändert:

**Vorher** leitete das Kontaktformular die Eingaben nur durch – Contact Form 7
baute daraus eine E-Mail und vergaß sie. Nichts blieb auf dem Server liegen.

**Seit Flamingo** wird **jede Einsendung in der Datenbank von dialos.org
gespeichert**, auch die aussortierten. Flamingo legt zusätzlich ein Adressbuch
aller Absender an.

**Beide Datenschutzerklärungen kennen diesen Fall nicht.** Sie beschreiben
unter „Kontaktaufnahme" / „Contacting Us" ausschließlich die Kontaktaufnahme
**per E-Mail** an kontakt@dialos.org. Das Kontaktformular kommt als
Verarbeitung an keiner Stelle vor – der einzige Satz dazu steht unter
„Empfänger und Auftragsverarbeiter" und betrifft nur den Versandweg.

**Ich bin kein Jurist.** Der Text unten ist ein Formulierungsvorschlag im Ton
der bestehenden Erklärung, keine Rechtsberatung.

## Stephans Entscheidungen vom 22.10.2026

> „IP-Adresse und Browserkennung brauchen wir nicht"
> „6 Monate reicht!"

**Beides ist in Theme 1.6.21 umgesetzt**, nicht nur im Text versprochen:

- **IP-Adresse und Browserkennung werden gar nicht erst gespeichert.** Der
  Filter `dialos_flamingo_ohne_kennungen` entfernt `remote_ip` und
  `user_agent`, bevor Flamingo schreibt. Nachgesehen im Quelltext: Die
  Übergabe macht nicht Flamingo, sondern Contact Form 7 in
  `modules/flamingo.php`; Flamingo lässt davor den Filter
  `flamingo_add_inbound` laufen.
- **Nachrichten werden nach fünf Monaten in den Papierkorb gelegt**, täglicher
  Lauf über `dialos_flamingo_aufraeumen`. WordPress entfernt
  Papierkorb-Einträge nach weiteren 30 Tagen – zusammen ergibt das die
  zugesagten sechs Monate, mit Puffer statt knapp darüber. Der Umweg über den
  Papierkorb ist Absicht: Fällt je etwas falsch heraus, bleibt ein Monat, es
  zurückzuholen.

## Korrektur zu einer früheren Aussage

Ich hatte gesagt, Flamingo räume gar nicht auf. **Das stimmt nur zur Hälfte.**
Nachgesehen in `includes/cron.php`: Flamingo verschiebt **Spam** nach
`FLAMINGO_MOVE_TRASH_DAYS` (Standard: 30 Tage) in den Papierkorb. Reguläre
Nachrichten rührt es nicht an – die blieben tatsächlich für immer liegen, und
genau dafür ist der Lauf oben da.

---

## Deutsch – einzufügen unter „Kontaktaufnahme" (Seite 3)

Der bestehende Absatz zur E-Mail bleibt stehen. Darunter:

> Wenn Sie das Kontaktformular auf dieser Website nutzen, verarbeiten wir die
> von Ihnen eingegebenen Daten (Vor- und Nachname, E-Mail-Adresse, Betreff und
> Nachricht sowie die freiwilligen Angaben Anrede, Firma und Abteilung)
> ausschließlich zur Bearbeitung Ihrer Anfrage (Art. 6 Abs. 1 lit. b bzw. f
> DSGVO). Die Nachricht wird uns per E-Mail zugestellt und zusätzlich auf
> unserem Server gespeichert, damit wir Anfragen nachvollziehen können. Ihre
> IP-Adresse und die Kennung Ihres Browsers werden dabei nicht gespeichert.
> Gespeicherte Nachrichten löschen wir spätestens sechs Monate nach Eingang,
> sofern keine gesetzlichen Aufbewahrungspflichten entgegenstehen.
>
> Zum Schutz vor automatisiert versandter Werbung prüfen wir jede Einsendung,
> bevor sie uns zugestellt wird. Dabei wird unter anderem gezählt, wie viele
> Nachrichten in kurzer Zeit von demselben Internetanschluss eingehen. Hierfür
> speichern wir nicht Ihre IP-Adresse, sondern nur einen daraus berechneten
> Prüfwert, aus dem sich die Adresse nicht zurückrechnen lässt; er wird nach
> einer Stunde automatisch gelöscht. Als Werbung eingestufte Nachrichten
> werden uns nicht zugestellt.

## Englisch – einzufügen unter „Contacting Us" (Seite 376)

> If you use the contact form on this website, we process the data you enter
> (first and last name, email address, subject and message, as well as the
> optional fields salutation, company and department) exclusively to handle
> your request (Art. 6(1)(b) or (f) GDPR). The message is sent to us by email
> and additionally stored on our server so that we can trace enquiries. Your
> IP address and browser identification are not stored. We delete stored
> messages no later than six months after receipt, unless statutory retention
> obligations apply.
>
> To protect against automated advertising, we check every submission before
> it reaches us. Among other things, we count how many messages arrive from
> the same internet connection within a short period. For this we do not store
> your IP address, but only a derived check value from which the address
> cannot be reconstructed; it is deleted automatically after one hour. Messages
> classified as advertising are not delivered to us.

---

## Noch offen

**Das Adressbuch.** Flamingo legt neben den Nachrichten auch Kontakte an
(Name und E-Mail-Adresse jedes Absenders, Menüpunkt „Adressbuch"). Diese Liste
räumt der Lauf oben **nicht** mit auf – sie wächst weiter. Zu entscheiden: ob
sie gebraucht wird. Wenn nicht, lässt sie sich über den Filter
`flamingo_add_contact` genauso abschalten wie die IP-Speicherung oben.

**Vor dem Veröffentlichen:** beide Sprachfassungen im selben Zug (Seiten 3 und
376) und das „Stand:"-Datum oben anpassen.

Einzelheiten zum Spamschutz im Abschnitt „Spamschutz" der
[README](../README.md#spamschutz).
