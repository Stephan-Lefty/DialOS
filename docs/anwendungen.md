[Deutsch](anwendungen.md) | [English](anwendungen.en.md)

# Anwendungen: welches Programm für welchen Zweck

Die Stelle, an der nachgesehen wird, **womit** DialOS eine Aufgabe
erledigt - und warum gerade damit. Festgelegt mit Stephan am 2026-08-18,
als der Block „Anwendungen" begann.

Die Sprachbefehle dazu stehen in [sprachbefehle.md](sprachbefehle.md),
nicht hier. Diese Datei beantwortet „welches Programm", jene „welcher
Satz".

## Das Auswahlkriterium ist nicht die Bedienbarkeit

Sondern die **Steuerbarkeit von außen.** Der Nutzer sieht den Bildschirm
nicht; ein Programm, das nur über seine Oberfläche zu bedienen ist, ist
für DialOS wertlos - auch wenn es das beste seiner Art wäre. Gefordert ist
eine Kommandozeile oder eine D-Bus-Schnittstelle.

Daran ist am 2026-08-18 gleich ein installiertes Programm gescheitert:
`gnome-podcasts` ist da und funktioniert, hat aber keine Kommandozeile.
Damit ist es keine Option, obwohl es die naheliegende gewesen wäre.

## Gesetzt

| Zweck | Programm | Warum |
|---|---|---|
| Browser | **Firefox ESR** 140 | Steht seit Beginn; Startseite per Enterprise-Policy, siehe [Debian-zu-DialOS.md](Debian-zu-DialOS.md) Schritt 10. |
| Mail, Kalender, Kontakte | **Thunderbird** 140 | Ein Programm für alle drei - jedes weitere wäre ein weiterer Satz Sprachbefehle. Evolution und GNOME-Kalender sind bewusst nur ausgeblendet, nicht entfernt (sie hängen an `gnome-core`). |
| Support/Fernwartung | **RustDesk** 1.4.9 | Bewusst deaktiviert und nur auf ausdrückliche Ansage startbar, siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md). |
| Radio | **Shortwave** 5.0.0 | Wegen der Stationsdatenbank von radio-browser.info. Nur damit lässt sich ein **gesprochener Name** in einen Stream auflösen - „spiel Radio Tirol". Rhythmbox kann Streams auch, aber nur aus handgepflegten Adressen, und die kennt der Nutzer nicht. |
| Lokale Musik | **Rhythmbox** 3.4.8 | `rhythmbox-client` kann alles, was Sprachbefehle brauchen - geprüft am 2026-08-18: `--play`, `--pause`, `--next`, `--previous`, `--play-uri`, `--set-volume`, `--print-playing`. Das letzte ist wichtig: DialOS kann ansagen, was gerade läuft. |
| Podcasts, Hörbücher | **Rhythmbox** (dasselbe Programm), Merkposition durch DialOS | Podcasts sind im Kern enthalten (GSettings-Schema `org.gnome.rhythmbox.podcast`), nicht als Erweiterung. Ein Programm weniger, und vor allem ein Player weniger - siehe „Nur ein Player" unten. **Die Merkposition liefert Rhythmbox aber nicht** - siehe „Die Position gehört DialOS" unten. |
| Briefe | **LibreOffice Writer** 25.2 | Ein Brief muss gedruckt oder als PDF verschickt werden können, mit Absender und Datum. Das einzige installierte Programm mit Vorlagen und Druck. |
| Notizen, Einkaufszettel | **kein Programm - Textdateien** | Ein Einkaufszettel muss vorgelesen, ergänzt und abgehakt werden, alles per Sprache. Jede Oberfläche ist dafür ein Umweg, den der Nutzer nie sieht. DialOS verwaltet sie als `.txt` in einem Ordner: nichts zu installieren, nichts das bei einem Update kaputtgeht, und der Zettel bleibt lesbar, auch wenn DialOS mal nicht läuft. |
| Videochat | **Jitsi Meet im Firefox** | Kontofrei und per Link startbar, siehe [telefonie.md](telefonie.md). Kamera vorhanden und erkannt (`/dev/video0`). Nicht von der Telefonie-Verschiebung betroffen: Jitsi braucht keine zusätzliche Hardware. |
| Updates | **unattended-upgrades** + Sprachbefehl | Zwei getrennte Dinge, und das mit Absicht: Sicherheitsupdates laufen automatisch im Hintergrund, weil ein blinder Nutzer sich um Sicherheitslücken nicht kümmern können muss. Alles Größere kommt nur auf Ansage mit Ja/Nein-Rückfrage, weil ein Upgrade, das den Desktop verändert, nie ungefragt kommen darf. Paket noch nicht installiert. |

## Offen

| Zweck | Stand |
|---|---|
| **Telefonie** | **Nach hinten gestellt** (Stephan, 2026-08-18). Sie hängt an der Hardware-Entscheidung aus [telefonie.md](telefonie.md) - eingebaute SIM oder gekoppeltes Handy -, und die ist offen. |
| **Chat** | In [telefonie.md](telefonie.md) ist WhatsApp Web im Browser priorisiert, wegen der Verbreitung bei Familie und Freunden. Bestätigung für diese Liste steht noch aus. |
| **Videoaufnahme** | Zweck noch nicht geklärt. Eine Videobotschaft an die Familie ist etwas anderes als „festhalten, was der Handwerker gesagt hat" - davon hängt die Wahl ab. `gnome-snapshot` ist installiert, aber ohne Kommandozeile; `ffmpeg` wäre verfügbar (7.1.5). |

## Freigegeben, noch nicht gebaut

Stephan hat diese Punkte am 2026-08-18 vollständig freigegeben („deine
Punkte müssen alle mit rein"). Sie sind damit im Umfang, aber noch nicht
umgesetzt - die Trennung ist Absicht, damit Geplantes nicht wie
Vorhandenes aussieht.

Die ersten zwei sind keine Anwendungen, sondern Voraussetzungen für vier
der obigen:

- **Diktat (Sprache zu Text).** Briefe, Notizen, Mail und Chat kann der
  Nutzer ohne Diktat gar nicht erzeugen. **`vosk-model-de-big` mit 3,2 GB
  liegt schon auf der Platte** - freies Diktat braucht also keine neue
  Technik, nur Arbeit. Nicht zu verwechseln mit der eingeschränkten
  Grammatik der Befehlserkennung: Das sind zwei verschiedene Betriebsarten
  desselben Werkzeugs.
- **Vorlesen von Mails, Dokumenten und Webseiten.** Das Gegenstück zum
  Diktat und für die Zielgruppe genauso zentral.
- **Post einscannen und vorlesen.** `simple-scan`, `sane-utils` und CUPS
  sind installiert, nur `tesseract-ocr` fehlt (5.5.0 verfügbar). Damit
  löst DialOS ein Problem, das kein Screenreader lösen kann: den Brief von
  der Krankenkasse, der auf Papier kommt.
- **Hörbücher.** Bewusst getrennt von Musik zu betrachten, weil dort die
  Merkposition zählt - wer ein achtstündiges Hörbuch nach dem Einschalten
  von vorn beginnen muss, hört es nicht.
- **Wecker, Timer, Erinnerungen.** „Erinnere mich um drei an die
  Tabletten."
- **Rechner ausschalten und sperren per Sprache**, und **Termine und
  Wetter ansagen** (aus Thunderbird; die Wetterabfrage steckt schon in der
  Start-Ansage).

## Mail: Thunderbird ist die Oberfläche, nicht der Motor

Geprüft am 2026-08-18, als Stephan die Testadresse `proband@dialos.org`
angelegt hat. Thunderbirds Kommandozeile kennt genau **eine** Funktion:

```
thunderbird -compose "to='empfaenger@tld.org'"
```

Mails **lesen** lässt sich von außen gar nicht, und `-compose` öffnet nur
ein vorbefülltes Fenster, das jemand anklicken muss. Nach dem Kriterium
oben - Steuerbarkeit von außen - fällt Thunderbird damit als Motor für die
Sprachbedienung durch, genau wie `gnome-podcasts`.

**Die Folge ist keine neue Programmwahl, sondern eine Arbeitsteilung:**

| Aufgabe | Wer |
|---|---|
| Mail vorlesen, Mail diktieren und senden | **DialOS direkt über IMAP/SMTP** (`imaplib`, `smtplib` - Pythons Standardbibliothek, kein zusätzliches Paket) |
| Mail ansehen und bearbeiten durch einen sehenden Helfer | Thunderbird |
| Kalender und Kontakte | Thunderbird, unangefochten |

**Offen und bewusst nicht hier entschieden:** Damit braucht DialOS die
Zugangsdaten der Mailbox selbst. Ob sie in den GNOME-Schlüsselbund
(libsecret) gehören oder in eine Datei, die nur dem Konto gehört, ist eine
Frage der Sicherheits-Architektur - siehe
[sicherheit-datenschutz.md](sicherheit-datenschutz.md) und `TODO.md`.

Zur Testmailbox: Der Mailserver von dialos.org ist `s111.goserver.host`.
**Autoconfig-Einträge gibt es nicht** (`_imaps._tcp`, `_submission._tcp`,
`_autodiscover._tcp` sind alle leer), Thunderbird muss die Einstellungen
also raten - die IMAP-/SMTP-Daten des Hosters gehören bereitgehalten.

### Welchen Servernamen DialOS benutzt - und warum nicht den offensichtlichen

Gemessen am 2026-08-18 an der Testmailbox. Das Zertifikat des Hosters
lautet `CN=*.goserver.host`, die Alternativnamen sind nur
`*.goserver.host` und `goserver.host`. **`imap.dialos.org` steht nicht
darin.** Ergebnis mit strenger Prüfung (`ssl.create_default_context()`):

| Verbindung | Ergebnis |
|---|---|
| `imap.dialos.org:993` | abgelehnt, Hostname passt nicht |
| `imap.dialos.org:143` + STARTTLS | abgelehnt, derselbe Grund |
| `s111.goserver.host:993` | **OK** |
| `smtp.dialos.org:587` | abgelehnt |
| `s111.goserver.host:587` + STARTTLS | **OK** |

**DialOS benutzt deshalb `s111.goserver.host`.** Thunderbird läuft nur,
weil beim Einrichten eine Zertifikats-Ausnahme bestätigt wurde - in der
Profildatei `cert_override.txt` steht `imap.dialos.org:143`. Für eine
Oberfläche, an der ein Mensch bewusst zustimmt, ist das in Ordnung;
**DialOS darf diesen Weg nicht kopieren.** Eine stillschweigend
ungeprüfte Verbindung ist für einen blinden Nutzer unsichtbar - er könnte
nie merken, dass jemand dazwischensitzt.

**Nicht fest einbauen:** `s111` ist der Name eines gemeinsam genutzten
Servers beim Hoster und ändert sich, wenn die Mailbox umzieht. Der Name
gehört in die Konfiguration. Er lässt sich auch aus dem MX-Eintrag der
Domain ableiten - heute zeigt `dialos.org` MX genau auf
`s111.goserver.host`.

**Ein Gewinn nebenbei: der Server kann IDLE.** DialOS muss also nicht im
Minutentakt nachfragen, sondern kann sich benachrichtigen lassen. „Du hast
eine neue Mail von..." kommt dann, wenn sie ankommt, und kostet dazwischen
keine Akkulaufzeit.

**Ein eigener Fehler beim Prüfen, weil er sich wiederholen kann:** Mein
erster Test meldete `imap.dialos.org` als in Ordnung. Ursache war, dass
`imaplib.IMAP4_SSL` ohne ausdrücklichen `ssl_context` aufgerufen wurde -
dann steht nicht fest, ob überhaupt geprüft wird. Bei SMTP hatte ich den
Kontext gesetzt, und genau dort schlug es fehl; der Vergleich war also
wertlos. **Wer TLS prüft, muss den Prüfkontext ausdrücklich übergeben.**

## Zwei Regeln, die aus dieser Liste folgen

**Nur ein Player darf gleichzeitig laufen.** Sagt der Nutzer „lauter" oder
„stopp" und es läuft Musik in einem und ein Podcast in einem anderen
Programm, ist der Befehl nicht mehr eindeutig - und der Nutzer kann nicht
nachsehen, welches Fenster gerade vorn ist. Deshalb Rhythmbox für Musik
UND Podcasts: Es bleiben genau zwei Player, Rhythmbox und Shortwave, und
DialOS muss das eine beenden, bevor es das andere startet.

**Die echo-bereinigte Quelle darf nie die Vorgabe-Quelle werden.**
Geprüft am 2026-08-18, und es stimmt derzeit nur, weil es WirePlumbers
Standard ist - festgelegt hat es niemand:

| Wer nimmt auf | Quelle |
|---|---|
| Sprachdienst (`parec`) | `dialos_mikrofon_ohne_echo` |
| Firefox, also auch Jitsi | rohes internes Mikrofon (Vorgabe) |

Firefox bringt für WebRTC seine eigene Echo-Unterdrückung mit. Bekäme es
unsere bereinigte Quelle, liefe die Verarbeitung doppelt, und die
Gegenseite hört dünne, verwaschene Sprache mit Artefakten. Wer die
Vorgabe-Quelle umstellt, verschlechtert also die Tonqualität in
Videocalls, ohne dass der Zusammenhang sichtbar wäre.

**Die Position gehört DialOS, nicht dem Player.** Geprüft am 2026-08-18:
Rhythmbox' Bibliothek kennt `play-count` und `last-played`, aber **kein**
`playback-position` und kein `bookmark`. Ein achtstündiges Hörbuch würde
also nach dem Einschalten von vorn beginnen - genau der Fall, den Stephan
als Ausschlusskriterium genannt hat.

Die Lösung ist nicht ein zweiter Player (das würde die Regel oben
brechen), sondern: **DialOS liest die Position über MPRIS und setzt sie
wieder.** Die MPRIS-Erweiterung ist in Rhythmbox vorhanden, `gdbus` ist
installiert.

Das ist kein Notbehelf, sondern die bessere Lösung. DialOS muss die
Position ohnehin kennen, um sie ansagen zu können - „weiter bei drei
Stunden zwölf" kann kein Player der Welt für uns sprechen. Und es ist
dieselbe Regel, die am 2026-08-17 dreimal zugeschlagen hat: **nicht auf
den Zustand einer fremden Komponente verlassen, sondern den eigenen
führen** (siehe `CLAUDE.md`).
