# SEO-Analyse dialos.org – Stand 16.08.2026

Rein öffentliche Analyse, ohne Login: HTML aller sechs Seiten, `robots.txt`,
Sitemap, offene REST-API (`/wp-json/`) und HTTP-Header.

## Umsetzungsstatus (laufend aktualisiert)

- ✅ **Befund 1** (leerer Seitentitel) – behoben: Website-Titel `DialOS`,
  Untertitel `Sprachgesteuert, einfach, alltagstauglich` gesetzt.
- ✅ **Befund 3** (kein SEO-Plugin) – behoben: SEOPress PRO installiert und
  lizenziert (gültig bis 07.06.2027).
- ✅ **Befund 2 / 7** (Meta-Descriptions/Titel) – behoben: Title + Description
  für alle sechs Seiten über `seopress/v1/posts/{id}/title-description-metas`
  gesetzt und live geprüft.
- ✅ Duplicate-Description-Tag entdeckt und behoben: Theme `wlow` gab in
  `header.php` Zeile 15 einen zweiten, aus der Tagline gespeisten
  Description-Tag aus (`bloginfo('description')`) – das war vor dem Setzen der
  Tagline unsichtbar, da leer. Zeile im Theme-Datei-Editor auskommentiert.
- ✅ **Befund 4** (Social-Media-Vorschau) – behoben: `og:title`/`og:description`
  übernehmen automatisch die gesetzten SEOPress-Metadaten, `og:image` und
  `twitter:image` zeigen jetzt auf `logo-full.png` (1100×950) auf allen sechs
  Seiten.
- ✅ Tippfehler „Sefeld" → „Seefeld" auf der Datenschutzseite korrigiert.
- ✅ **Befund 8** (Alt-Texte) – behoben: alle 10 tatsächlich eingebundenen
  Bilder (auf /, /status/, /fuer-investoren-sponsoren/) haben jetzt
  beschreibende Alt-Texte. Nebenbefund: Theme gibt pro `<img>` zusätzlich ein
  hartcodiertes leeres `alt=""` aus (ungültiges HTML, aber laut Spec gewinnt
  das erste Attribut – unser Alt-Text wird korrekt vorgelesen). Kein
  Sofortthema, ließe sich bei Gelegenheit im Theme beheben.
- ✅ **Befund 6** (Startseiten-Slug) – behoben: Slug von `beispielseite` auf
  `startseite` geändert. `/beispielseite/` liefert jetzt 404 (kein
  automatischer WordPress-Redirect ausgelöst, aber unkritisch, da die Seite
  noch kaum indexiert war). Canonical-Tag zeigt weiterhin korrekt auf `/`.
- ✅ **Befund 5** (Schema/JSON-LD) – behoben, über den SEOPress-PRO-Schema-Editor
  (wp-admin, nicht per REST-API – die API dokumentiert die Feldstruktur für
  `/seopress/v1/schemas` nicht ausreichend):
  - `SoftwareApplication` (Name DialOS, Betriebssystem Debian 13, Kategorie
    `UtilitiesApplication`, Preis 0 EUR) auf Startseite (ID 2) und
    `/status/` (ID 24), per Beitrags-ID-Regel eingeschränkt.
  - `Organization` (Name, URL, Logo `mark.png`, E-Mail) als „Benutzerdefiniert"-
    Schema global auf allen sechs Seiten.
  - Zusätzlich bereits vorhanden: automatisch generiertes `WebSite`-Schema auf
    der Startseite (Standard-SEOPress-Funktion, keine Einrichtung nötig).
- ⬜ Befund 9 (Inhalt) – noch offen.

## Kurzfassung

Die Seite ist technisch sauber aufgesetzt (HTTPS erzwungen, Sitemap vorhanden,
`robots.txt` korrekt, schnelle Auslieferung), aber **inhaltlich für Suchmaschinen
praktisch unsichtbar**: Es gibt keinen Seitentitel, keine einzige
Meta-Description, keine Social-Media-Vorschau und keine strukturierten Daten.
Das sind alles Einstellungen, die nachgeholt werden können – der größte Hebel
liegt bei den ersten vier Punkten unten und kostet zusammen vielleicht zwei
Stunden.

## Bestandsaufnahme

| Merkmal | Befund |
|---|---|
| WordPress | 7.0.4, selbst gehostet, nginx |
| Theme | `wlow` |
| Plugins (im HTML sichtbar) | nur Contact Form 7 |
| SEO-Plugin | **keines** |
| Seiten | 6 |
| Beiträge | 0 |
| Sprache | `de`, Zeitzone Europe/Vienna |
| Sitemap | `wp-sitemap.xml` (WordPress-Kern), 6 URLs |
| TTFB | ~0,55 s |

Zur offenen Frage aus dem Briefing (welches SEO-Plugin läuft): **gar keins.**
Die REST-API meldet nur die Namensräume `oembed/1.0`, `contact-form-7/v1`,
`wp/v2`, `wp-site-health/v1`, `wp-block-editor/v1`, `wp-abilities/v1`. Yoast
würde `yoast/v1` registrieren, Rank Math `rankmath/v1` – beides fehlt. Damit
gibt es aktuell **keine REST-Felder für Meta-Titel, Description oder
Fokus-Keyword**; die müssen erst durch ein Plugin geschaffen werden.

## Befunde nach Priorität

### 1. Der Seitentitel ist komplett leer (kritisch)

Die Startseite liefert `<title></title>`. Ursache: In WordPress sind
**Website-Titel und Untertitel nicht gesetzt** – die API meldet `"name":""` und
`"description":""`.

Folgen: Google erfindet sich den Titel im Suchergebnis selbst (meist aus der
H1 oder dem Domainnamen), Browser-Tabs und Lesezeichen bleiben namenlos, und der
RSS-Feed heißt wörtlich " » Feed". Der Title-Tag ist das mit Abstand
wichtigste einzelne SEO-Signal.

**Fix:** Einstellungen → Allgemein → Website-Titel = `DialOS`, Untertitel z. B.
`Sprachgesteuertes Linux für blinde und motorisch eingeschränkte Menschen`.

### 2. Keine Meta-Descriptions (kritisch)

Alle sechs Seiten liefern `<meta name="description" content="" />` – der Tag
kommt leer aus dem Theme. Google baut sich das Snippet dann aus zufälligen
Textfragmenten der Seite zusammen, was die Klickrate spürbar drückt.

Ein leerer Description-Tag ist außerdem schlechter als gar keiner. Beim
Einrichten eines SEO-Plugins darauf achten, dass nicht **zwei**
Description-Tags entstehen (Theme + Plugin) – ggf. muss der Theme-Tag raus.

### 3. Kein SEO-Plugin installiert (kritisch)

Ohne Plugin lassen sich Title und Description pro Seite gar nicht pflegen. Für
dieses Projekt ist **SEOPress** die passendere Wahl (Korrektur ggü. der
ursprünglichen Einschätzung, s. u.): Es bringt eine eigene, dokumentierte
REST-API (`seopress/v1`) mit, die Title, Description und Fokus-Keyword schon
in der **Gratisversion** schreibbar macht –
`PUT /wp-json/seopress/v1/posts/{id}/title-description-metas`. Genau das
brauchen wir, da wir ausschließlich über die API arbeiten.

Rank Math wäre die naheliegendere Alternative gewesen, registriert seine
Meta-Felder (`rank_math_title` etc.) aber standardmäßig **nicht** für die
WordPress-REST-API – ohne Zusatz-Plugin oder eigenen Code bleiben sie von
außen nicht schreibbar (bestätigt durch ein offizielles Rank-Math-
Support-Ticket dazu). Einziger Nachteil von SEOPress: Strukturierte Daten
(JSON-LD/Schema) sind in der Gratisversion manueller einzurichten statt
automatisch generiert – für unsere Kernaufgabe hier zweitrangig.

### 4. Keine Social-Media-Vorschau (hoch)

Es gibt **keine** Open-Graph- und keine Twitter-Card-Tags. Wer
`dialos.org/fuer-investoren-sponsoren/` in WhatsApp, LinkedIn, Mastodon oder
Signal teilt, sieht einen nackten Link ohne Bild, Titel und Beschreibung.

Für eine Seite, die aktiv Investoren und Sponsoren ansprechen soll, ist das der
teuerste Punkt in dieser Liste – und mit dem Logo aus `assets/` in fünf Minuten
erledigt (Rank Math bringt OG-Tags mit).

### 5. Keine strukturierten Daten (mittel)

Null JSON-LD auf der ganzen Seite. Sinnvoll wären `Organization` (Name, Logo,
Kontakt) plus `SoftwareApplication` für DialOS selbst. Das ist die Grundlage
dafür, dass Google das Projekt als Entität versteht und im
Knowledge-Panel/AI-Antworten korrekt wiedergibt.

### 6. Startseite hat noch den Beispielseiten-Slug (mittel)

Die Startseite ist Seite ID 2 mit dem Slug `beispielseite` – die
WordPress-Standardseite „Sample Page", nur umbenannt. Über `/` ist das
unkritisch (Canonical zeigt korrekt auf `https://dialos.org/`), aber der Slug
sollte auf `startseite` o. Ä. geändert werden, und es ist zu prüfen, ob
`/beispielseite/` parallel erreichbar bleibt (Duplicate Content).

### 7. Titel sagen nichts (mittel)

Aktuell sind die Title-Tags die reinen Seitennamen:

| URL | Title heute | Vorschlag |
|---|---|---|
| `/` | *(leer)* | DialOS – Der sprachgesteuerte Computer für blinde Menschen |
| `/status/` | `Idee` | Idee & Entwicklungsstand – DialOS |
| `/fuer-investoren-sponsoren/` | `Investoren & Sponsoren` | Investoren & Sponsoren – DialOS unterstützen |
| `/kontakt/` | `Kontakt` | Kontakt – DialOS |

`Idee` als alleinstehender Titel ist für ein Suchergebnis wertlos. Zusätzlich:
Die Seite `/status/` trägt den Titel „Idee" – Slug und Titel passen nicht
zusammen, das sollte vereinheitlicht werden.

### 8. Bilder ohne Alternativtext (mittel)

Beide Bilder auf der Startseite haben keinen gefüllten `alt`-Text. Bei einem
Projekt, dessen Kernthema Barrierefreiheit für blinde Menschen ist, ist das
inhaltlich unpassend – ein Screenreader liest dort nichts vor. Zusätzlich
verschenkt es Bild-SEO.

### 9. Zu wenig Inhalt (mittel, aber langfristig der größte Hebel)

Die Startseite hat ~314 Wörter, eine H1 und **keine einzige H2**. Es gibt
**null Blog-Beiträge**. Damit fehlt jede Fläche, um für die eigentlich
relevanten Suchanfragen zu ranken:

- „Computer für blinde Menschen"
- „Linux Sprachsteuerung deutsch"
- „PC per Sprache bedienen Sehbehinderung"
- „barrierefreies Betriebssystem"

Der vorhandene Stoff liegt bereits im Repo: `docs/sprachsteuerung.md`,
`docs/telefonie.md`, `docs/sicherheit-datenschutz.md`, `docs/hardware.md`. Daraus
lassen sich ohne neue Recherche vier bis sechs gut rankende Seiten machen. Das
Änderungsprotokoll auf `/status/` ist außerdem ein natürlicher Kandidat für
echte Blog-Beiträge statt einer langen Einzelseite.

### 10. Keine englische Version (niedrig, aber Chance)

Die Website ist rein deutsch, obwohl im Repo bereits eine vollständige
englische Doku liegt (`README.en.md`, `docs/*.en.md`). Für EU-Fördertöpfe und
internationale Accessibility-Netzwerke wäre eine englische Fassung mit
`hreflang`-Auszeichnung wertvoll. Kein Sofortthema.

### 11. Technische Kleinigkeiten (niedrig)

- **Kein HSTS-Header.** Die Weiterleitungen `http://` → `https://` und
  `www.` → ohne `www.` funktionieren korrekt (jeweils 301), aber ein
  `Strict-Transport-Security`-Header fehlt.
- **TTFB ~0,55 s.** Für sechs statische Seiten viel – es läuft offenbar kein
  Page-Cache. Ein Caching-Plugin oder nginx-FastCGI-Cache bringt das auf unter
  0,1 s. Kein Ranking-Notstand, aber leicht zu holen.
- **Nur gzip, kein Brotli.** Bei nginx eine Zeile Konfiguration – setzt
  allerdings Serverzugriff voraus, der laut Briefing noch unklar ist.

## Empfohlene Reihenfolge

**Sofort, im WordPress-Backend (ohne uns, ~15 Minuten):**

1. Website-Titel und Untertitel setzen (Befund 1).
2. SEOPress installieren und den Einrichtungsassistenten durchlaufen
   (Befunde 2–5 auf einen Schlag).
3. Altes Application Password widerrufen, neues erzeugen (siehe Briefing).

**Danach gemeinsam über die REST-API:**

4. ✅ Verbindungstest mit `./wp-api.sh GET wp/v2/users/me?context=edit`.
5. ✅ Title + Description für alle sechs Seiten über SEOPress gesetzt.
6. Alt-Texte nachtragen, Startseiten-Slug korrigieren, `/status/` in Titel und
   Slug vereinheitlichen.
7. Startseite inhaltlich ausbauen (H2-Struktur, Keywords).
8. Redaktionsplan für die Inhaltsseiten aus `docs/` aufsetzen.

## Rohdaten

Erhoben am 16.08.2026 mit `curl` gegen die öffentlichen Endpunkte:
`/`, `/status/`, `/fuer-investoren-sponsoren/`, `/kontakt/`, `/impressum/`,
`/datenschutzerklaerung/`, `/robots.txt`, `/wp-sitemap.xml`, `/wp-json/`,
`/wp-json/wp/v2/pages`, `/wp-json/wp/v2/posts`.
