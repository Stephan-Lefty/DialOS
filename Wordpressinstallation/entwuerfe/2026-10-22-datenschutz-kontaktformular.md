# Datenschutzerklärung: Abschnitt zum Kontaktformular

**Entwurf vom 22.10.2026. Nicht veröffentlicht – wartet auf Stephans Freigabe.**

## Warum dieser Entwurf entstanden ist

Am 22.10.2026 wurde **Flamingo** installiert, damit nachlesbar ist, was der
neue Spamschutz aussortiert. Damit hat sich die Datenverarbeitung auf
dialos.org geändert, und zwar grundlegend:

**Vorher** leitete das Kontaktformular die Eingaben nur durch – Contact Form 7
baute daraus eine E-Mail und vergaß sie. Nichts blieb auf dem Server liegen.

**Seit Flamingo** wird **jede Einsendung dauerhaft in der Datenbank von
dialos.org gespeichert** – auch die aussortierten. Flamingo löscht nichts von
selbst, und es legt zusätzlich ein Adressbuch aller Absender an.

**Beide Datenschutzerklärungen kennen diesen Fall nicht.** Sie beschreiben
unter „Kontaktaufnahme" / „Contacting Us" ausschließlich die Kontaktaufnahme
**per E-Mail** an kontakt@dialos.org. Das Kontaktformular kommt als
Verarbeitung an keiner Stelle vor – der einzige Satz dazu steht unter
„Empfänger und Auftragsverarbeiter" und betrifft nur den Versandweg.

Solange nichts gespeichert wurde, war das eine kleine Lücke. Jetzt ist es
eine Verarbeitung, über die nicht informiert wird.

**Ich bin kein Jurist.** Der Text unten ist ein Formulierungsvorschlag im Ton
der bestehenden Erklärung, keine Rechtsberatung.

## Vorher zu klären

1. **Welche Felder Flamingo tatsächlich speichert.** Dass die Formularfelder
   drin sind, ist sein Zweck. Ob **IP-Adresse und Browserkennung** dabeistehen,
   steht in einem gespeicherten Eintrag selbst – bitte einmal nachsehen und
   den Entwurf danach anpassen oder die Klammer streichen.
2. **Wie lange die Nachrichten bleiben sollen.** Unten steht „zwölf Monate" als
   Vorschlag. Flamingo räumt nicht selbst auf; was dort steht, muss von Hand
   gelöscht werden, sonst stimmt die Angabe nach einem Jahr nicht mehr.
3. Danach **beide Sprachfassungen im selben Zug** (Seiten 3 und 376) und das
   „Stand:"-Datum oben anpassen.

---

## Deutsch – einzufügen unter „Kontaktaufnahme" (Seite 3)

Der bestehende Absatz zur E-Mail bleibt stehen. Darunter:

> Wenn Sie das Kontaktformular auf dieser Website nutzen, verarbeiten wir die
> von Ihnen eingegebenen Daten (Vor- und Nachname, E-Mail-Adresse, Betreff und
> Nachricht sowie die freiwilligen Angaben Anrede, Firma und Abteilung)
> ausschließlich zur Bearbeitung Ihrer Anfrage (Art. 6 Abs. 1 lit. b bzw. f
> DSGVO). Die Nachricht wird uns per E-Mail zugestellt und zusätzlich auf
> unserem Server gespeichert, damit wir Anfragen nachvollziehen können[ –
> zusammen mit Ihrer IP-Adresse und der Kennung Ihres Browsers]. Gespeicherte
> Nachrichten löschen wir spätestens zwölf Monate nach Abschluss der
> Bearbeitung, sofern keine gesetzlichen Aufbewahrungspflichten entgegenstehen.
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
> and additionally stored on our server so that we can trace enquiries[,
> together with your IP address and browser identification]. We delete stored
> messages no later than twelve months after the enquiry has been dealt with,
> unless statutory retention obligations apply.
>
> To protect against automated advertising, we check every submission before
> it reaches us. Among other things, we count how many messages arrive from
> the same internet connection within a short period. For this we do not store
> your IP address, but only a derived check value from which the address
> cannot be reconstructed; it is deleted automatically after one hour. Messages
> classified as advertising are not delivered to us.

---

## Hinweis zum Spamschutz selbst

Der zweite Absatz beschreibt die Mengenbremse aus Theme 1.6.20. Sie speichert
einen Hash der IP-Adresse über `wp_hash()` mit einer Stunde Lebensdauer – aus
dem gespeicherten Wert lässt sich keine Adresse zurückrechnen. Die übrigen
drei Schichten (Honigtopf, Verweise in Kurzfeldern, Schriftzeichen) verarbeiten
nur das, was ohnehin abgeschickt wurde, und speichern nichts.

Einzelheiten im Abschnitt „Spamschutz" der
[README](../README.md#spamschutz).
