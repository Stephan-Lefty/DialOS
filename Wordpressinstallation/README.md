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

## Änderungsprotokoll

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
