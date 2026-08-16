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
