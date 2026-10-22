[Änderungsprotokoll](#änderungsprotokoll)

# WordPress-Installation dialos.org

Arbeitsverzeichnis für die Pflege und SEO-Optimierung der WordPress-Seite
[dialos.org](https://dialos.org). Die Arbeit läuft über die
WordPress-REST-API (`https://dialos.org/wp-json/wp/v2/...`), da vermutlich kein
SSH-Zugang zum Server besteht.

Dies ist **nicht** die eigentliche WordPress-Installation (kein Code-Abbild des
Servers), sondern die Analyse-, Konfigurations- und Skriptablage dazu.

## Inhalt

- [SEO-Analyse-2026-08-16.md](SEO-Analyse-2026-08-16.md) – vollständige
  Bestandsaufnahme ohne Login: Befunde nach Priorität und empfohlene Reihenfolge
- [wp-api.sh](wp-api.sh) – Helfer für authentifizierte REST-API-Aufrufe
- [sync-changelog.py](sync-changelog.py) – überträgt das Änderungsprotokoll aus
  `README.md`/`README.en.md` auf die WordPress-Seiten `/status/` (deutsch) und
  `/en/idea/` (englisch). **Läuft nur auf Zuruf**, nicht automatisch. Die
  README gilt als Quelle der Wahrheit – Fotos neben einzelnen
  Changelog-Einträgen sind reine WordPress-Deko (siehe `IMAGE_MAP` im Skript,
  neue Versionen ohne Eintrag dort erscheinen einfach ohne Foto). Erst
  `--dry-run` probieren:
  ```bash
  ./sync-changelog.py --dry-run   # nur Vorschau
  ./sync-changelog.py             # schreibt wirklich auf die Website
  ```
- [sprechfassungen/](sprechfassungen/) – die Texte, aus denen die Hörfassungen
  der deutschen Neuigkeiten entstehen, gesprochen von Anna. Eigene Texte, nicht
  die vorgelesenen Beiträge: Ein Text zum Lesen und ein Text zum Hören sind
  nicht derselbe Text. Regeln und Ablauf in
  [sprechfassungen/README.md](sprechfassungen/README.md).
- [dialos-hoerfassung-sprechen.py](dialos-hoerfassung-sprechen.py) – erzeugt aus
  einer Sprechfassung die MP3-Datei (Piper + `de_DE-kerstin-low`, Tempo 0,95 wie
  am Gerät). Meldet Ziffern und Wörter, die Anna schlecht ausspricht, und warnt
  bei Überlänge.
- [dialos-hoerfassung-hochladen.py](dialos-hoerfassung-hochladen.py) – lädt die
  fertige Datei in die Mediathek und setzt den Audio-Block in den Beitrag.
  **Läuft nur auf Zuruf** – erst anhören, dann hochladen.
- [wp-theme/dialos/](wp-theme/dialos/) – das Child-Theme (Eltern-Theme:
  `wlow`), in dem alle eigenen Anpassungen liegen: `style.css`,
  `functions.php`, `screenshot.png`. **Es kommt ausschließlich über eine
  ZIP-Datei auf den Server** – die REST-API kann keine Theme-Dateien
  schreiben, einen zweiten Weg gibt es nicht. Ablauf und Fallstricke stehen
  unten unter [Theme pflegen](#theme-pflegen), die Fassungen unter
  [Theme-Fassungen](#theme-fassungen). Seit 1.6.20 steckt dort auch der
  [Spamschutz](#spamschutz) der Kontaktformulare.
- [wp-plugin/dialos-kommentare/](wp-plugin/dialos-kommentare/) – eigenes
  Plugin für die Kommentarfunktion
- Skripte zum Anlegen einzelner Seiten und Beiträge:
  [dialos-kommentare-einstellen.py](dialos-kommentare-einstellen.py),
  [dialos-mobil-datenschutz.py](dialos-mobil-datenschutz.py),
  [dialos-mobil-neuigkeit.py](dialos-mobil-neuigkeit.py),
  [dialos-mobil-tester-gesucht.py](dialos-mobil-tester-gesucht.py)
- [.env.example](.env.example) – Vorlage für die Zugangsdaten

## Zugang einrichten

```bash
cp .env.example .env
$EDITOR .env          # WP_APP_PASSWORD eintragen
chmod +x wp-api.sh
./wp-api.sh GET wp/v2/users/me?context=edit
```

Der letzte Befehl ist der Verbindungstest: Er sollte den Benutzer `ClaudIA`
samt Rollen und Fähigkeiten zurückgeben.

Das Application Password wird in WordPress unter **Benutzer → Profil →
Application Passwords** erzeugt.

> **Achtung:** Dieses Repository ist öffentlich auf GitHub. Die `.env` ist per
> [.gitignore](.gitignore) ausgeschlossen und darf niemals committet werden. Das
> ursprünglich im Cowork-Chat geteilte Passwort ist als kompromittiert zu
> betrachten und muss in WordPress widerrufen werden.

## Aktueller Stand

SEOPress PRO ist installiert und lizenziert. Alle Befunde aus der
[SEO-Analyse](SEO-Analyse-2026-08-16.md) sind bis auf den inhaltlichen Ausbau
(Befund 9) erledigt – Details und Umsetzungsstatus siehe dort.

Zusätzlich eingerichtet:
- **Matomo Analytics** (WordPress-Plugin, `idSite=1`), cookie-frei und mit
  IP-Anonymisierung konfiguriert – dafür wurde die Datenschutzerklärung
  aktualisiert (Abschnitt „Cookies und Analyse-Tools"). Besucherzahlen
  lassen sich über die REST-API abfragen, z. B.
  `./wp-api.sh GET matomo/v1/visits_summary/get?idSite=1\&period=month\&date=today`.
  **Offen und seit dem 22.10.2026 belegt:** kein echter System-Cron beim
  Hoster, WordPress läuft nur mit Pseudo-Cron – Matomos vorberechnete
  Berichte hinken deshalb hinterher, und ein manueller Archivierungsanstoß
  über die API ändert daran nichts. Messung und Folgen unter
  [Dashboard-Blöcke](#dashboard-blöcke).
- WordPress-Dashboard aufgeräumt (Google-Analytics- und
  Events-Kästchen ausgeblendet) – gilt nur für den eingeloggten Benutzer
  (Stephan), WordPress speichert das nicht zentral.

Verbindungstest erfolgreich: `wp-api.sh GET wp/v2/users/me?context=edit`
liefert Benutzer `ClaudIA` mit Administrator-Rechten.

## Theme pflegen

Das Child-Theme liegt unter [wp-theme/dialos/](wp-theme/dialos/) und besteht
aus genau drei Dateien: `style.css`, `functions.php`, `screenshot.png`. Auf
dem Server liegt nichts darüber hinaus – ein ZIP-Upload ersetzt das ganze
Verzeichnis.

**Der Weg auf den Server führt nur über eine ZIP-Datei.** Die REST-API kann
keine Theme-Dateien schreiben; es gibt keinen zweiten Weg und keinen
SSH-Zugang. Ablauf:

1. Version im Kopf von `style.css` hochzählen (`Version: 1.6.25`). **Ohne
   das greift die Änderung nicht** – siehe die Cache-Marke unten.
2. Archiv packen, mit dem Ordner `dialos/` darin:
   ```bash
   cd wp-theme && zip -rq ~/Schreibtisch/dialos-theme-1.6.25.zip dialos
   ```
3. Ältere ZIPs von der Arbeitsfläche löschen, sonst wird die falsche
   hochgeladen.
4. Hochladen über **Design → Themes → Theme hinzufügen → Theme hochladen**,
   danach gegenprüfen:
   ```bash
   curl -s "https://dialos.org/wp-content/themes/dialos/style.css?x=$(date +%s)" | head -8
   ```

**Drei Fallstricke, die jeweils Zeit gekostet haben:**

- **`functions.php` legt bei einem Syntaxfehler die ganze Seite lahm.** Hier
  ist kein PHP installiert, deshalb vor dem Packen prüfen:
  ```bash
  docker run --rm -v "$PWD/wp-theme/dialos:/x:ro" php:8.2-cli php -l /x/functions.php
  ```
- **Das Eltern-Theme `wlow` bindet unsere `style.css` ein zweites Mal ein.**
  Es ruft `get_stylesheet_uri()` auf – bei aktivem Child-Theme ist das nicht
  seine eigene Datei, sondern unsere. Diese zweite Einbindung trug früher die
  WordPress-Kernversion als Cache-Marke, die sich bei Theme-Änderungen nie
  bewegte; Besucher bekamen dort die alte Datei aus dem Browserspeicher, und
  weil sie später geladen wird, gewann sie. Seit 1.6.16 stellt ein Filter in
  `functions.php` das richtig. Zur Kontrolle müssen **beide** Verweise
  dieselbe Fassung tragen:
  ```bash
  curl -s https://dialos.org/ | grep -o "themes/dialos/style.css?ver=[0-9.]*"
  ```
- **`id="wlow-css"` im HTML ist nicht der Handle.** WordPress hängt beim
  Ausgeben `-css` an. Eine Bedingung auf den Handle-Namen, die sich an der
  HTML-ID orientiert, greift nie.

## Theme-Fassungen

Eigene Zählung, unabhängig vom Änderungsprotokoll dieses Verzeichnisses. Die
Fassung steht im Kopf von `style.css`; die Einzelheiten stehen in den
Commit-Nachrichten und als Begründung im Quelltext.

| Fassung | Datum | Worum es ging |
|---|---|---|
| (ohne Nummer) | 23.08.2026 | Child-Theme angelegt, Startseiten-Hintergrund, Kontaktformular, Fußzeilenfarben, Navigationsleiste transparent |
| 1.0.0 | 23.08.2026 | Menü und Fußzeile neu geordnet, Überlappungsfehler behoben, Suche im Menü, Barrierefreiheit (Sprachmarkierung, Sprunglink, Umschalter), „Nach oben"-Knopf statt Hamburger |
| 1.0.x–1.4.0 | 23.–25.08.2026 | Fußzeilenlinks beim Überfahren sichtbar, Menü blendet beim Scrollen aus, WCAG-Nachprüfung, Linkkontrast auf `#027a5c`, englische Beiträge unter `/en/` mit Flaggen-Umschalter |
| 1.4.1 | 25.08.2026 | Flaggen ins Suchfeld verschoben |
| 1.5.0–1.5.5 | 25.08.2026 | Englische Startseite im Stil der deutschen, News von Neuigkeiten getrennt, `/en/`-Routing repariert, englische Rechtstexte verlinkt |
| 1.6.0–1.6.2 | 25.08.2026 | „Vorheriger/Nächster Beitrag" unter den Kommentaren, Cache wird bei jeder Inhaltsänderung geleert |
| 1.6.3–1.6.4 | 17.09.2026 | Englische Anführungszeichen auf englischen Seiten, Filter kennt auch benannte Entitäten |
| 1.6.5–1.6.11 | 17./18.09.2026 | Die drei neuesten Beiträge in der rechten Spalte, quadratische Kacheln, Schriftgröße in mehreren Schritten auf 18 px |
| 1.6.12–1.6.13 | 22.09.2026 | Seite lässt sich auf dem Handy nicht mehr seitlich schieben; Fußzeilenlinks untereinander. **1.6.12 blieb wirkungslos** – erst 1.6.13 mit `body`-Präfix griff |
| 1.6.14 | 22.09.2026 | Leere Blöcke in den Neuigkeiten, lange Pfade auf `/status/` |
| 1.6.15–1.6.16 | 22.09.2026 | Cache-Marke der doppelten Einbindung richtiggestellt – zwei Fehlversuche, bis der Handle-Name ganz entfiel |
| 1.6.17 | 23.09.2026 | Tester-Hinweis als runder Aufkleber links neben dem Inhaltskasten, fest stehend ab 1640 px Fensterbreite |
| 1.6.18 | 23.09.2026 | Startseiten gestrafft, damit sie ohne Scrollen in den Bildschirm passen |
| 1.6.19 | 23.09.2026 | **Rücknahme aus 1.6.18:** Der `.spacer` ist kein Weißraum, sondern der Platzhalter der fest stehenden Navigationsleiste. Gekürzt saßen „DIALOS" und das Menü im Inhaltskasten |
| 1.6.20 | 22.10.2026 | Spamschutz für die Kontaktformulare in vier Schichten, nachdem über 200 Spam-Nachrichten durchkamen – siehe [Spamschutz](#spamschutz) |
| 1.6.21 | 22.10.2026 | Datensparsamkeit bei Flamingo: IP-Adresse und Browserkennung werden nicht gespeichert, Nachrichten nach fünf Monaten in den Papierkorb |
| 1.6.22 | 22.10.2026 | Flamingos Adressbuch wird gar nicht erst gefüllt |
| 1.6.23 | 22.10.2026 | Zugriffszahlen im Dashboard (Woche, 90 Tage, Jahr, gesamt, Herkunftsländer) – siehe [Dashboard-Blöcke](#dashboard-blöcke) |
| 1.6.24 | 22.10.2026 | Dashboard auf fünf einzelne Blöcke aufgeteilt, dazu Kontaktformular-Zähler, meistbesuchte Seiten und Verweisquellen |
| 1.6.25 | 22.10.2026 | Absendername in Flamingo: `[your-name]` stand dort als Platzhalter, weil unser Formular Vor- und Nachname getrennt führt |

## Spamschutz

**In der Nacht zum 22.10.2026 kamen über 200 Spam-Nachrichten über das
Kontaktformular herein** – russischsprachige Werbung mit einem Link auf eine
`.buzz`-Domain.

Die Ursache war keine Sicherheitslücke, sondern eine Lücke in der eigenen
Einrichtung: Das Plugin **contact-form-7-honeypot ist aktiv und lädt auf jeder
Seite seine Dateien – aber ein Honeypot wirkt nur dort, wo im Formular auch ein
`[honeypot …]`-Tag steht.** Beim Testteilnahme-Formular (ID 205) steht es seit
jeher drin, beim Kontaktformular (ID 49) wurde es vergessen. Das Plugin hatte
dort nichts zu bewachen, und nichts hat je darauf hingewiesen.

**Deshalb liegt der Schutz seit 1.6.20 in `functions.php` und nicht im
Formular.** Ein Tag im Formular hält genau so lange, bis jemand das Formular im
Editor umbaut – und fällt dann wieder lautlos aus. Im Theme gilt er für alle
Formulare, liegt im Git und fällt beim Dateivergleich auf, wenn ihn jemand
entfernt.

### Die vier Schichten

| # | Regel | Greift bei |
|---|---|---|
| 1 | Höchstens fünf Absendungen je Stunde und Quelle | Massenangriff, auch wenn er alle Inhaltsregeln umschifft |
| 2 | Verstecktes Feld (Honigtopf) in jedem Formular | Bots, die stumpf jedes Eingabefeld füllen |
| 3 | Verweise in Vorname, Nachname, Anrede, Firma, Abteilung, Betreff | Werbung, die den Link im Betreff unterbringt |
| 4 | Betreff oder Nachricht ohne einen einzigen lateinischen Buchstaben | Fremdsprachige Massenwerbung |

**Zu Schicht 1:** Gespeichert wird nicht die IP-Adresse, sondern nur ihr Hash
über `wp_hash()`; die Marke verfällt nach einer Stunde von selbst. Fünf ist
großzügig bemessen, weil mehrere Personen hinter einem gemeinsamen Anschluss
dieselbe Adresse haben – in einer Einrichtung für blinde Menschen ist das der
Normalfall.

**Zu Schicht 2:** `aria-hidden` am Umschlag und `tabindex="-1"` am Feld, damit
Screenreader es weder vorlesen noch anspringen. Bewusst **kein**
`display: none` – ein Teil der Bots prüft genau darauf und überspringt solche
Felder; off-screen geschobene füllen sie.

**Zu Schicht 4** – das ist Stephans Regel vom 22.10.2026, und sie ist bewusst
so herum formuliert: nicht „enthält fremde Zeichen" (das wäre eine Liste von
Schriften, die nie vollständig wird und bei jedem Zitat falsch anschlägt),
sondern „enthält **keinen** lateinischen Buchstaben".

| Eingabe | Ergebnis |
|---|---|
| `Новый способ получать результат` | Spam |
| `Frage zu DialOS` | kommt durch |
| `Frage zu DialOS (Привет, Сергей)` | kommt durch |
| `Сергей Иванов – Frage` | kommt durch |
| `2026`, `???` | kommt durch (keine Buchstaben, nichts zu beurteilen) |

Damit deckt eine einzige Prüfung Kyrillisch, Griechisch, Arabisch, Hebräisch,
Chinesisch und jede andere Schrift ab, ohne sie je zu nennen – und ein
deutscher Text fällt auch dann nicht durch, wenn fremde Schrift darin vorkommt.

**Am echten Formular belegt, und zwar versehentlich:** Für einen Testeintrag
in Flamingo wurde am 22.10.2026 eine Nachricht mit dem Betreff „Проверка
22.10.2026 — Testeintrag für Flamingo" abgeschickt – in der Erwartung, sie
werde aussortiert. Sie kam durch, völlig zu Recht: „Testeintrag für Flamingo"
ist lateinisch. Derselbe Versuch mit rein kyrillischem Betreff wurde sofort
als Spam eingestuft. Der Fehler lag im Test, nicht im Filter – und nebenbei
ist damit gezeigt, dass die Regel nicht übereifrig ist.
**Der Preis, und er ist bewusst bezahlt:** Wer dialos.org auf Russisch oder
Griechisch anschreiben will, kommt nicht durch.

### Was es bewusst nicht gibt

**Kein CAPTCHA**, in keiner Form – kein Bilderrätsel, keine Rechenaufgabe, kein
„ich bin kein Roboter". dialos.org wendet sich an blinde und motorisch
eingeschränkte Menschen; ein CAPTCHA wäre genau die Barriere, gegen die dieses
Projekt antritt.

**Keine Zeitfenster-Prüfung** („zu schnell abgeschickt"). Wer per
Sprachsteuerung oder Screenreader ausfüllt, braucht ein Vielfaches der Zeit
eines Sehenden – eine Untergrenze wäre eine Barriere. Eine Obergrenze wäre
wegen WP Super Cache ohnehin nicht verlässlich.

### Wo die aussortierten Nachrichten landen

**Seit dem 22.10.2026 in Flamingo.** Contact Form 7 allein hat keinen
Spam-Ordner – was als Spam gilt, wird nicht versendet und nicht gespeichert,
nur der Grund wird protokolliert (`add_spam_log`, Agent `dialos-spamschutz`).
Damit ein Fehlalarm überhaupt auffallen kann, ist **Flamingo** installiert
(vom selben Autor wie Contact Form 7). Es legt jede Einsendung in der
Datenbank ab und markiert die aussortierten als Spam.

**Das macht dialos.org zu einer Stelle, die Nachrichten speichert** – vorher
wurde nur durchgeleitet. Theme 1.6.21 hält das so sparsam wie möglich:

| Was | Wie |
|---|---|
| IP-Adresse und Browserkennung | werden gar nicht erst gespeichert |
| Nachrichten älter als fünf Monate | täglicher Lauf legt sie in den Papierkorb |
| Papierkorb | WordPress leert ihn nach weiteren 30 Tagen → zusammen sechs Monate |
| Spam älter als 30 Tage | räumt Flamingo selbst weg (`FLAMINGO_MOVE_TRASH_DAYS`) |
| Adressbuch (Name + E-Mail jedes Absenders) | wird gar nicht erst angelegt |

Die Übergabe an Flamingo macht **nicht Flamingo, sondern Contact Form 7** in
`modules/flamingo.php`: Dort wird eine Liste von Special Mail Tags
eingesammelt – darunter `remote_ip` und `user_agent` – und als `meta`
weitergereicht. Flamingo lässt davor den Filter `flamingo_add_inbound` laufen,
und genau dort hängt `dialos_flamingo_ohne_kennungen` die beiden Felder aus.
Die Flamingo-Oberfläche geht die vorhandenen Felder mit `foreach` durch, ein
entferntes Feld fällt dort also sauber weg.

**Am gespeicherten Eintrag belegt** (Stephan, 22.10.2026): In der
Meta-Liste einer Nachricht folgt auf `serial_number` direkt `url` – `remote_ip`
und `user_agent`, die laut Contact Form 7s Quelltext genau dazwischen stehen
müssten, fehlen. Seine Rückmeldung: „keine IP Adressen aufgeführt".

**Dabei gefunden und in 1.6.25 behoben:** Als Absender stand dort wörtlich
`[your-name] <…>` – der Platzhalter statt des Namens. Contact Form 7 sucht für
Flamingo ein Feld `your-name`; unser Kontaktformular führt Vor- und Nachname
aber getrennt, und fehlt das Feld, bleibt der Platzhalter ohne Fehlermeldung
stehen. Kein Schönheitsfehler: Die Nachrichten liegen ein halbes Jahr, und wer
sie später durchsieht, sähe bei jeder Anfrage denselben Platzhalter. Der Filter
`dialos_flamingo_absendername` setzt den Namen jetzt aus den beiden Feldern
zusammen – an `wpcf7_flamingo_get_value`, weil Contact Form 7 aus diesem einen
Wert sowohl `from_name` als auch `from` baut.

**Der Aufräumlauf geht über den Papierkorb, nicht direkt in die Löschung.**
Fällt je etwas falsch heraus, bleibt ein Monat, es zurückzuholen. Fünf Monate
plus dieser Monat ergeben die zugesagten sechs – mit Puffer statt knapp
darüber.

**Das Adressbuch bleibt leer** (seit 1.6.22, Stephans Entscheidung vom
22.10.2026). Flamingo legt sonst neben jeder Nachricht einen Kontakt an – eine
Liste aus Name und E-Mail aller Absender, die unbegrenzt weiterwächst und auch
dann stehen bleibt, wenn die Nachricht längst weggeräumt ist. Contact Form 7
bietet keinen Filter zum Überspringen, aber Flamingos
`Flamingo_Contact::add()` steigt direkt hinter dem Filter
`flamingo_add_contact` aus, wenn keine gültige Adresse übrig ist – ein im Code
vorgesehener Weg, kein Trick.

### Wo die Nachrichten liegen

**Flamingo trennt in drei Reiter, und der Posteingang zeigt den Spam nicht.**
Das hat am 22.10.2026 für Verwirrung gesorgt: Ein Testeintrag war „nicht
auffindbar", lag aber einfach im Spam-Reiter. Wer einem Fehlalarm nachgeht,
muss dort nachsehen – nur die aussortierten Nachrichten liegen da.

```
https://dialos.org/wp-admin/admin.php?page=flamingo_inbound
https://dialos.org/wp-admin/admin.php?page=flamingo_inbound&post_status=spam
https://dialos.org/wp-admin/admin.php?page=flamingo_inbound&post_status=trash
```

Der Papierkorb-Reiter erscheint nur, wenn etwas darin liegt. Gelöscht wird
zweistufig: erst in den Papierkorb, dort dann endgültig – zurückholbar bleibt
es 30 Tage.

**Nicht zu verwechseln:** `page=flamingo` (ohne `_inbound`) ist das Adressbuch,
und das bleibt seit 1.6.22 absichtlich leer.

Die Datenschutzerklärung muss das alles nennen – Entwurf in beiden Sprachen
liegt unter
[entwuerfe/2026-10-22-datenschutz-kontaktformular.md](entwuerfe/2026-10-22-datenschutz-kontaktformular.md),
noch nicht veröffentlicht.

### Prüfen, ohne eine echte Mail auszulösen

Die Schriftzeichen-Regel ist vor dem Einbau gegen 14 Fälle geprüft worden
(echter Spam, deutscher Text mit kyrillischem Einschub, kyrillischer Name mit
lateinischem Rest, Umlaute, Emoji, reine Ziffern, leeres Feld) – 0 Fehler. Die
PHP-Syntax wie immer ohne lokales PHP:

```bash
docker run --rm -v "$PWD/wp-theme/dialos:/x:ro" php:8.2-cli php -l /x/functions.php
```

## Dashboard-Blöcke

Auf der Startseite des Backends stehen seit Theme 1.6.24 **fünf eigene
Kästen** – einer je Thema, nicht einer für alles. Jeder lässt sich einzeln
verschieben, zuklappen oder über „Ansicht anpassen" abschalten; ein
Sammelkasten wäre entweder ganz da oder ganz weg.

| Block | Was drinsteht | Zeitraum |
|---|---|---|
| Zugriffe auf dialos.org | Besuche und Seitenaufrufe, dazu eine Live-Zeile | Woche, 90 Tage, Jahr, gesamt |
| Herkunft der Besuche | die acht häufigsten Länder | laufendes Jahr |
| Kontaktformular | Anfragen und aussortierter Spam | 7 Tage und Bestand |
| Meistbesuchte Seiten | die sechs meistgelesenen Seitentitel | 30 Tage |
| Woher die Besucher kommen | Suche, Verweise, soziale Netze, direkt | 30 Tage |

Gezählt wird seit dem 15.08.2026 – das Anlagedatum der Matomo-Seite wird
abgefragt und nicht fest eingetragen, sonst stünde dort nach einem Neuaufbau
von Matomo eine falsche Zahl, ohne dass es auffiele.

**Woher die Zahlen kommen:** über `rest_do_request()` aus Matomos eigener
REST-Route, im selben Prozess. Bewusst **kein** HTTP-Aufruf an die eigene
Seite – der wäre langsam, könnte an einer Firewall scheitern und hätte WP
Super Cache dazwischen. Und bewusst **kein** Griff in Matomos PHP-Klassen:
die ändern sich zwischen Fassungen, die REST-Route ist die zugesagte
Schnittstelle.

**Jeder Block hat seinen eigenen Zwischenspeicher** (30 Minuten). Wäre es
einer für alle, müsste beim ersten Aufruf jeder Block auf die Abfragen aller
anderen warten – und ein abgeschalteter Block würde trotzdem Zeit kosten.
Alle auf einmal erneuern: `wp-admin/index.php?dialos-zahlen=neu`.

### Warum der Kontaktformular-Block existiert

Er ist die Antwort auf die Lücke vom 22.10.2026: Ein aktives Plugin bewachte
keinen Schutz, und **nichts wies darauf hin** – bis 200 Spam-Mails ankamen.
Ein Wachhund-Skript, das regelmäßig Testnachrichten schickt, wäre Dauerlast
für einen Fall, der sich auch passiv zeigt.

Steht dort eines Tages bei „aussortiert" eine Null, wo vorher Dutzende
standen, greift etwas nicht mehr. Steht umgekehrt eine ungewohnt hohe Zahl bei
den Anfragen, lohnt der Blick, ob echte Post im Spam gelandet ist.

Der Verweis im Block zeigt auf `admin.php?page=flamingo_inbound`, **nicht** auf
`page=flamingo` – Letzteres ist das Adressbuch, und das ist seit 1.6.22
absichtlich leer.

### Warum eine Zeile „letzte 24 Stunden (live)" dabeisteht

**Matomos vorberechnete Berichte hinken auf diesem Hoster hinterher.**
Gemessen am 22.10.2026: Der Bericht meldete für „heute" 0 Besuche, während die
Live-Abfrage im selben Moment einen Besuch kannte. Ursache ist der fehlende
echte System-Cron – WordPress läuft hier nur mit Pseudo-Cron, Matomo archiviert
also bloß gelegentlich.

Ein manueller Anstoß über die API ist **kein** Ausweg: Der Aufruf

```bash
./wp-api.sh POST matomo/v1/core_admin_home/run_cron_archiving
```

kam nach 0,98 Sekunden mit `true` zurück und änderte an der Zahl **nichts**.
Erfolg gemeldet, nichts getan – das ist genau die Sorte Zustandsmeldung, der
man nicht glauben darf, ohne das Ergebnis zu messen.

Die Live-Zeile liest die Besuchstabelle direkt und ist deshalb immer aktuell.
Steht dort eine Zahl und in den Zeilen darüber eine Null, ist das kein
Widerspruch, sondern dieser Rückstand.

### Was an den Zahlen auffällt

Von 463 Besuchen des laufenden Jahres kommen **246 aus den Vereinigten
Staaten** – mehr als die Hälfte, bei einer deutschsprachigen Nischenseite mit
österreichischem und deutschem Publikum (140 bzw. 63 Besuche). Das ist kein
Publikum, das ist mit großer Wahrscheinlichkeit automatisierter Verkehr, den
Matomos Bot-Erkennung nicht erwischt. Wer mit diesen Zahlen arbeitet, sollte
das wissen.

**Der Verweis-Block bestätigt das.** In den letzten 30 Tagen kamen **208 von
214 Besuchen als „direkte Zugriffe"** – bei genau **einem**
Suchmaschinen-Besuch, drei Verweisen von anderen Webseiten und zwei aus
sozialen Netzen. Menschen finden eine Seite über Suche oder Links; wer eine
Adresse direkt aufruft, ohne je gesucht zu haben, ist in dieser Menge fast
immer ein Programm. Die 463 Besuche des Jahres sind realistisch eher 200.

## Änderungsprotokoll

### 0.6.0 (22.10.2026)
- **Spamschutz für die Kontaktformulare** (Theme 1.6.20), nachdem in der Nacht
  über 200 Spam-Nachrichten durchkamen. Vier Schichten, keine davon verlangt
  etwas vom Besucher – Einzelheiten und Begründungen im Abschnitt
  [Spamschutz](#spamschutz).
- **Gefunden dabei:** Das Honeypot-Plugin war seit jeher aktiv, aber im
  Kontaktformular fehlte das `[honeypot …]`-Tag. Ein aktives Plugin ist kein
  Beweis für einen wirksamen Schutz – dieselbe Fehlerklasse wie
  „Installationsstand prüfen, nicht annehmen" im Hauptprojekt.
- **Flamingo installiert**, damit ein Fehlalarm überhaupt auffallen kann.
  Damit speichert dialos.org erstmals Nachrichten, statt sie nur
  durchzuleiten – Theme 1.6.21 hält das sparsam: IP-Adresse und
  Browserkennung werden gar nicht erst gespeichert, Nachrichten wandern nach
  fünf Monaten in den Papierkorb und sind damit nach sechs Monaten weg
  (Stephans Vorgaben vom 22.10.2026).
- **Die Datenschutzerklärung kennt das Kontaktformular nicht.** Beide
  Fassungen beschreiben nur die Kontaktaufnahme per E-Mail. Entwurf in beiden
  Sprachen liegt unter
  [entwuerfe/2026-10-22-datenschutz-kontaktformular.md](entwuerfe/2026-10-22-datenschutz-kontaktformular.md),
  bewusst noch nicht veröffentlicht – siehe `TODO.md` im Hauptverzeichnis.
- **Eigenes Plugin gegen Namensübernahme gesichert** (`dialos-kommentare`
  2.0.1): `Update URI: false`. Mit automatischen Updates würde WordPress ein
  fremdes Plugin gleichen Ordnernamens ohne Rückfrage einspielen.
- **Fünf Dashboard-Blöcke** (Theme 1.6.23/1.6.24): Zugriffe, Herkunftsländer,
  Kontaktformular, meistbesuchte Seiten und Verweisquellen – je ein eigener
  Kasten auf der Startseite des Backends, einzeln abschaltbar. Dabei zwei
  Dinge gemessen, die vorher nur Vermutung waren: dass Matomos vorberechnete
  Berichte hinterherhinken, und dass **208 von 214 Besuchen „direkte
  Zugriffe" bei einem einzigen Suchmaschinen-Besuch** sind – das Muster von
  automatisiertem Verkehr, nicht von Publikum. Siehe
  [Dashboard-Blöcke](#dashboard-blöcke).
- **Die Datenschutzerklärung nennt das Kontaktformular jetzt** (Seiten 3 und
  376, „Stand" auf den 22.10.2026 gesetzt).

### 0.5.0 (23.09.2026)
- **Das Theme steht endlich in diesem Verzeichnis.** Es lag seit dem
  23.08.2026 unter `wp-theme/dialos/` im Repo, kam aber in der Inhaltsliste
  nicht vor, und seine 48 Commits in fünf Wochen standen in keinem
  Änderungsprotokoll – nur im Kopf der `style.css` und in den
  Commit-Nachrichten. Nachgetragen sind jetzt der Eintrag im Verzeichnis,
  der Abschnitt [Theme pflegen](#theme-pflegen) mit dem ZIP-Weg und den drei
  Fallstricken sowie die Übersicht [Theme-Fassungen](#theme-fassungen).
  Gleiches gilt für das Plugin `wp-plugin/dialos-kommentare/` und die vier
  Skripte für einzelne Seiten und Beiträge.
- **Tester-Hinweis als Aufkleber** (Theme 1.6.17): Der Button „Tester für
  DialOS Mobil werden" stand am Fuß beider Startseiten, rund 1200 Pixel unter
  der Oberkante – ohne Scrollen nicht zu sehen. Er ist jetzt ein runder,
  fest stehender Aufkleber links neben dem Inhaltskasten. Platz dafür ist ab
  1640 Pixeln Fensterbreite; darunter steht er im Textfluss unter der
  Überschrift, auf 375 Pixeln Breite endet er 521 Pixel unter der Oberkante.
- **Startseiten gestrafft** (1.6.18/1.6.19): 175 Pixel aus Abständen und
  Polsterung, dazu eine Höhengrenze fürs Splash-Bild. Die deutsche Startseite
  passt damit auf einem großen Bildschirm ohne Scrollen ins Bild (1266 von
  1307 Pixeln). **Dabei ein eigener Fehler:** Der `.spacer` wurde mitgekürzt,
  obwohl er der Platzhalter der `position: fixed`-Navigationsleiste ist –
  danach saßen Logo und Menü im weißen Kasten. 1.6.19 nimmt das zurück.
- **Zwei Absätze auf beiden Startseiten gekürzt**, mit Verweis auf
  `/status/` bzw. `/en/idea/` für die gestrichenen Einzelheiten. **Gemessen
  und ernüchternd:** Auf Bildschirmen ab etwa 1080p bestimmt nicht der Text
  die Seitenhöhe, sondern die rechte Spalte „Neueste Beiträge" mit 1057
  Pixeln. Absätze zu kürzen bringt dort exakt null Pixel. Scrollfrei ist die
  Startseite deshalb nur auf großen Bildschirmen – der Aufkleber ist über
  seine feste Position davon unabhängig immer sichtbar.

### 0.4.0 (22.09.2026)
- **Das Änderungsprotokoll ist geteilt.** `/status/` und `/en/idea/` zeigen je
  Version nur noch eine Kurzfassung mit Verweis auf die vollständige Liste; die
  steht neu auf `/aenderungsprotokoll/` (Seite 644) und `/en/changelog/`
  (Seite 645). Beide neuen Seiten hängen nicht im Menü – Menü 7 hat
  `auto_add = False`, neue Seiten landen dort also nicht von selbst.
- **Der Grund war messbar:** `/status/` war **373 KB** groß, 262 Einzelpunkte
  über sieben Versionen, allein 0.5.1 mit 138. Auf einem Handy im Mobilfunknetz
  ist das eine halbe Minute Laden für eine Seite, die jemand überfliegen will.
  Jetzt sind es 71 KB, und davon ist das Protokoll nur noch ein kleiner Teil.
- **Die Kurzfassung wird nicht erfunden, sondern gefunden.** In den großen
  Versionen beginnt praktisch jeder Punkt mit einem fett gesetzten Kopf (53 von
  53, 138 von 138, 48 von 52), im Schnitt 57 bis 81 Zeichen lang gegenüber 939
  bis 1318 für den ganzen Punkt. Genau dieser Kopf wird übernommen. Ältere
  Versionen ohne Fettschrift liefern den ersten Satz. Damit behauptet das
  Skript nichts über Wichtigkeit, was es nicht wissen kann.
- **Markdown-Links werden endlich umgewandelt.** `md_inline_to_html()` kannte
  Code-Spannen, Fett und Kursiv – aber keine Links. Auf `/status/` standen
  dadurch **17 Stück wörtlich** auf der Seite, Besucher lasen
  `[rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074)`. Dieselbe
  Klasse Fehler wie bei der Fettschrift am 17.09.: Was im Protokoll vorher
  nicht vorkam, fiel nie auf. Verweise auf Repo-Dateien (`docs/…`, `TODO.md`)
  gehen jetzt auf GitHub, weil es auf der Website kein `docs/` gibt. Neu ist
  auch eine Warnung, wenn doch einmal ein Link stehen bleibt.
- Gefunden wurde das alles nebenbei: Die langen Adressen waren es, die
  `/status/` auf dem Handy breiter machten als den Bildschirm.

### 0.3.0 (17.09.2026)
- Hörfassungen der deutschen Neuigkeiten, gesprochen von Anna
  (`de_DE-kerstin-low`, Tempo 0,95 wie am Gerät). Erster Beitrag ist
  „Von drei auf 26 Sätze", 1:43 Minuten.
- Dabei gelernt und in `sprechfassungen/README.md` festgehalten: Der
  vorgelesene Blogbeitrag taugt nicht. Der erste Versuch war 2:23 lang und
  zu technisch – seitdem wird eine eigene Sprechfassung von Hand geschrieben,
  höchstens zwei Minuten, ohne Ziffern und ohne Fachbegriffe.
- Gemessen, warum: Anna schreibt Zahlen zwar aus, hetzt sie aber („26" ist
  22 % kürzer als „sechsundzwanzig"), und „Grammatik" hat die richtige Länge
  bei falscher Betonung. Beides wird umgangen, nicht repariert. **Offen:** ob
  das auch die Ansagen am Gerät betrifft (Akkustand, Uhrzeit) – das ist ein
  Hörtest, den nur Stephan machen kann.
- Beim Vertonen gefunden: Der per CSS versteckte Sprachmarker steht im HTML
  und wurde mitgelesen – Anna sagte „English" mitten im Beitrag. Wer den
  Beitragstext maschinell abgreift, muss ihn herausfiltern.

### 0.2.0 (16.08.2026)
- SEOPress PRO eingerichtet: Titel/Description auf allen 6 Seiten, Open-Graph-
  Bild, Organization- und SoftwareApplication-Schema (JSON-LD), Alt-Texte,
  Startseiten-Slug korrigiert, Duplicate-Description-Tag im Theme behoben.
- Matomo Analytics eingerichtet (cookie-frei, IP-anonymisiert),
  Datenschutzerklärung entsprechend aktualisiert.
- WordPress-Dashboard aufgeräumt.

### 0.1.0 (16.08.2026)
- Verzeichnis angelegt: öffentliche SEO-Bestandsaufnahme von dialos.org,
  REST-API-Helfer und Vorlage für die Zugangsdaten.
