# Hinweise für Claude

Dieses Repository ist DialOS – eine barrierefreie Debian-13/GNOME-48-
Live-ISO mit voller Sprachsteuerung für blinde und motorisch
eingeschränkte Nutzer. Stephan arbeitet allein an diesem Projekt (kein
Team) – bitte durchgehend "du" statt "ihr/euch" verwenden, und Stephan
darf dich gerne "ClaudIA" nennen.

**Lies zuerst [README.md](README.md) und alle Dateien in [docs/](docs/)**
für den vollständigen Kontext (Architektur, Zielgruppe, Sicherheit,
Sprachsteuerung, Telefonie, Ersteinrichtung, offene Punkte). Diese
Datei hier ist nur eine kurze Landkarte + der aktuelle Stand, keine
Doppelung der eigentlichen Doku.

**GitHub-Repo:** https://github.com/Stephan-Lefty/DialOS (privat).

**Wichtig für Claude selbst:** Dein eigenes Memory-System
(`~/.claude/...`) liegt auf der internen Platte des T490 und wird bei
jedem Reinstall gelöscht - genau wie der bisherige Chat und alle
Connector-/GitHub-Integration-Verbindungen der Claude-App (dafür gibt
es keine Wiederherstellung, weder automatisiert noch manuell in der
App). **Diese Datei hier (im Git-Repo auf der externen Platte, nach
GitHub gepusht) ist die einzige Erinnerung, die einen Reinstall
übersteht.** Alles, was über eine einzelne Session hinaus wichtig ist,
gehört deshalb hierher oder in `docs/`/`TODO.md` - nicht ins eigene
Memory-System verlassen.

**Wichtige, dauerhafte Regel (seit 2026-08-14):**
[docs/Debian-zu-DialOS.md](docs/Debian-zu-DialOS.md) (+ `.en.md`) ist
das lückenlose "von einer nackten Debian-13/GNOME-Installation bis zur
aktuellen DialOS-Version nachbauen"-Rezept. Bei **jeder** Änderung, die
den Aufbau eines Geräts betrifft (neues Paket, neue Branding-/Config-
Datei, geänderter Befehl, Bugfix an einem referenzierten Skript), muss
dieses Dokument **zusätzlich zum Änderungsprotokoll** in README.md
aktualisiert werden - in beiden Sprachen. Ziel: Das System soll sich
bei der finalen Version lückenlos aus dieser einen Datei heraus
reproduzieren lassen. Alle technischen Rezepte/Bugfixes (GDM-Autologin,
Plymouth-Splash, Calamares-Branding, Piper-TTS, Vosk/hassil, Rechte-
Fallen bei `/etc/skel/` usw.) stehen dort - nicht hier, um Doppelung zu
vermeiden.

## Aktueller Stand (Stand: 2026-08-14)

Der ursprüngliche Zwei-Wege-Versuch ist entschieden, kein "neuer Plan"
mehr, sondern der etablierte Ansatz:

1. **Docker/live-build-Pipeline** (`iso-build/`, `iso-build/build.sh`):
   verworfen nach ca. 18 Build-Versuchen ohne je eine fertige `.iso`
   gesehen zu haben (verschachteltes `live-build` in Docker in Claudes
   eigener Sandbox-Umgebung - praktisch jeder Bug ging darauf zurück).
   Bleibt nur noch als Referenz/Fallback (zusätzlich gibt es eine
   Cubic-Anleitung: `iso-build/CUBIC-ANLEITUNG.md`).
2. **Etablierter Ansatz:** Debian 13 + GNOME wird direkt auf echter
   Zielhardware (Lenovo ThinkPad T490) installiert und interaktiv
   konfiguriert - die `iso-build/`-Dateien dienen dabei nur noch als
   Vorlage/Rezept (siehe [docs/Debian-zu-DialOS.md](docs/Debian-zu-DialOS.md)
   für das vollständige, aktuell gehaltene Schritt-für-Schritt-Rezept).
   Anschließend zieht **[Penguins' Eggs](https://penguins-eggs.net/)**
   eine startfähige ISO aus dem fertig eingerichteten System.

**Aktuelle Version: 0.5.0** (in Arbeit) - alle Details im
[README.md-Änderungsprotokoll](README.md#änderungsprotokoll). Zwei
Test-ISOs bereits gebaut (`DialOS-Live-0.5.0.iso`,
`DialOS-Live-0.5.0-clone.iso`).

**Aktueller Blocker (14.08.):** Der geplante echte Live-Boot-Test von
`dialos-install` mit dem Sicherheits-Stick (bisher erster Punkt in
TODO.md) ist gescheitert - es wird gerade an einer neuen Lösung
gearbeitet.

Konkrete offene Aufgaben stehen ausschließlich in [TODO.md](TODO.md),
nicht hier - so bleibt der Stand an einer einzigen Stelle aktuell.

## Offene Entscheidungen (siehe auch [docs/offene-punkte.md](docs/offene-punkte.md))

- Sudo-Rechte für den Standard-Benutzer "nutzer" (Platzhalter-Passwort
  aktuell zufällig generiert, echte Policy für die spätere
  sprachgesteuerte Wartung noch offen).
- Referenz-Hardware final festlegen (aktuell T490 zum Testen, kein
  WWAN-Modul verbaut).
- Rechtschreibprüfung (hunspell/aspell) fehlt noch, siehe
  `docs/offene-punkte.md`.
- `scripts/dialos-setup-nutzer.sh` noch nicht als Ganzes (nur in
  Einzelschritten) durchgetestet.

## Arbeitsweise mit Stephan

- Stephan ist technisch versiert, aber kein Linux-Systembau-Experte -
  Erklärungen gerne kompakt, aber nicht zu knapp weglassen warum etwas
  gemacht wird.
- Bei Unklarheiten lieber kurz nachfragen als lange Annahmen treffen -
  Stephan antwortet schnell und direkt.
- Sicherheitsrelevante/destruktive Aktionen (Festplatte formatieren,
  GitHub-Repo-Sichtbarkeit ändern, etc.) immer transparent ankündigen.
- Commit-Nachrichten ausführlich mit Begründung ("warum"), nicht nur
  "was" - hat sich in diesem Projekt als hilfreich erwiesen, um die
  vielen Debugging-Iterationen nachvollziehbar zu halten.
- Terminal-Befehle: Stephan ist mit der Kommandozeile noch nicht extrem
  vertraut (z.B. Unsicherheit bei Pager-Ausgaben, `/tmp` vs. Home-Ordner,
  Ordner öffnen). Befehle immer mit absoluten Pfaden geben (funktioniert
  unabhängig vom aktuellen Verzeichnis), `--no-pager`-Flags bei
  `systemctl`/`journalctl` nicht vergessen, und wo möglich Ausgaben in
  eine Datei umleiten + direkt danach per `cat` anzeigen, statt auf
  manuelles Navigieren zu setzen.

## Datei-Workflow mit Stephan

**Update 2026-08-14:** Stephan hat einen Connector für die externe
SanDisk-Extreme-Platte eingerichtet und am selben Tag zusätzlich die
GitHub-Integration verbunden - Claude hat dadurch direkten Lese-/
Schreibzugriff auf dieses Repo unter `repo/` (anders als in der
früheren Situation mit getrennter Geräte-Brücke) und kann Dateien
direkt bearbeiten/committen, ohne den Umweg über Copy-Paste-
Terminalbefehle für Stephan. **Weiterhin offen:** die lokale
Git-Identität (`user.name`/`user.email`/`credential.helper`) ist in
dieser Umgebung noch nicht gesetzt - vor einem `git push` muss das
erst eingerichtet werden.

`TODO.md` im Repo-Root ist für kurzfristige, konkrete Aufgaben gedacht -
anders als `docs/offene-punkte.md`, das für grundsätzliche, noch
unentschiedene Architekturfragen gedacht ist. Erledigte Einträge werden
mit einem Häkchen (`[x]`) markiert und bleiben stehen (nicht löschen) -
so bleibt nachvollziehbar, was schon erledigt ist.
