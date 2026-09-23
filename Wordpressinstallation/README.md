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
  [Theme-Fassungen](#theme-fassungen).
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
  Offen: kein echter System-Cron beim Hoster, WordPress läuft nur mit
  Pseudo-Cron (Details siehe Matomo-Systembericht im wp-admin).
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

1. Version im Kopf von `style.css` hochzählen (`Version: 1.6.19`). **Ohne
   das greift die Änderung nicht** – siehe die Cache-Marke unten.
2. Archiv packen, mit dem Ordner `dialos/` darin:
   ```bash
   cd wp-theme && zip -rq ~/Schreibtisch/dialos-theme-1.6.19.zip dialos
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

## Änderungsprotokoll

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
