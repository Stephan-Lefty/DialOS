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
Plymouth-Splash, Piper-TTS, Vosk/hassil, Rechte-
Fallen bei `/etc/skel/` usw.) stehen dort - nicht hier, um Doppelung zu
vermeiden.

## Aktueller Stand (Stand: 2026-08-16)

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
`DialOS-Live-0.5.0-clone.iso`, beide nicht mehr lokal vorhanden - siehe
`docs/iso-builds.md`).

**Grundlegende Sicherheits-Architektur seit 14./15.08. neu** (löst den
früheren Ganze-Platte-LUKS-Ansatz komplett ab, siehe
[docs/sicherheit-datenschutz.md](docs/sicherheit-datenschutz.md),
Abschnitt "Verschlüsselung von nutzers Daten + Sicherheits-Stick"):
Nur noch eine eigene `dialos-nutzer-home`-Partition (LUKS2,
ausschließlich `/home/nutzer`) ist verschlüsselt, root (~100 GiB,
ext4) bootet immer unverschlüsselt normal.
`dialos-stick-gate.service` öffnet die Home-Partition nach dem Boot
(nicht im initramfs) und schaltet erst danach `nutzer`s Autologin frei.
Sicherheits-Stick: `DIALOS-KEY` (Schlüssel) als ext4 - bewusst NICHT
Windows-lesbar; `DIALOS-DATA` als exFAT - bewusst Windows/macOS/Linux-
lesbar als Zusatzspeicher für `nutzer` (empfohlene Standardgröße 64 GB).

**Einziger Installations-Pfad seit 2026-08-16 ("Weg A", Stephans
Entscheidung):** Jedes Gerät wird im Büro aufgesetzt - leere Platte,
jeweils aktuelle Debian-13/GNOME-ISO von debian.org, dabei `dialosadmin`
anlegen. Kein Kunde bekommt je einen Installer zu sehen. Damit sind
**Calamares und `dialos-install` ersatzlos entfallen** (siehe unten).
Ablauf: Basis-Installation (Schritt 1, Debian-Installer,
**muss** dabei bewusst Platz nach der 100-GB-root-Partition frei
lassen) → [`scripts/dialos-full-office-setup.sh`](scripts/dialos-full-office-setup.sh)
(automatisiert Schritte 2-12+15 aus Debian-zu-DialOS.md) →
`dialos-setup-home-partition.sh` (richtet `dialos-nutzer-home` +
Sicherheits-Stick im freigelassenen Platz ein) →
`scripts/dialos-buero-setup-abschliessen.sh` (`nutzer` anlegen +
Admin-Werkzeuge auf die Arbeitsfläche). **Seit 2026-08-16 besteht der
Aufbau nach der Basis-Installation aus genau drei Befehlen** - die letzte
Handarbeit aus Doku-Schritt 13 steckt jetzt im dritten Skript. Achtung
bei den Aufrufen: Skript 1 und 2 werden **ohne** `sudo` gestartet (Skript
1 richtet Benutzer-Dateien in `~` ein, Skript 2 hebt sich selbst per
`pkexec` an und braucht dafür die Grafik-Umgebung, die `sudo` streicht),
nur Skript 3 mit `sudo`.

Die Skripte wurden am 2026-08-16 vor dem ersten Lauf gegen
`docs/Debian-zu-DialOS.md` durchgesehen und auf dem frisch installierten
T490 live gegengeprüft; dabei kamen mehrere Fehler heraus, die den ersten
Durchlauf abgebrochen hätten (fehlendes `python3-pip`, `npm install -g`
ohne `sudo`, stummer Abbruch bei der Passwortabfrage ohne Grafik,
Partitionsnummer-Bestimmung, die bei Nummerierungslücken die falsche
Partition getroffen hätte) - alle behoben, Details im
README-Änderungsprotokoll 0.5.0. **Trotzdem weiterhin noch nie
end-to-end auf einem frischen System durchgelaufen** - das bleibt der
nächste geplante Schritt (kompletter T490-Neuaufbau, siehe TODO.md
"Nächster Schritt").
**Entfallen am 2026-08-16 (Weg A):** `dialos-install` (Zielplatte
löschen, System per rsync klonen, GRUB setzen) und der komplette
Calamares-Unterbau - Branding, `locale.conf`, `shellprocess.conf`, das
Penguins-Eggs-Overlay und `base.yaml.tmpl`. Beide existierten nur für den
Live-Boot-Installationsweg, den es nicht mehr gibt. `dialos-install`s
LUKS-/Stick-Logik lebt unverändert in `dialos-setup-home-partition.sh`
weiter, das daraus abgeleitet wurde. **`dialos-rekey` bleibt** - es
ersetzt einen verlorenen oder defekten Sicherheits-Stick und ist damit
ein Wartungswerkzeug, kein Installer. Die ISO (`eggs produce`) dient nur
noch als Sicherungs-Schnappschuss.

**Vosk/hassil ist jetzt produktiv im Einsatz** (nicht mehr nur das
Testskript `dialos-vosk-test.py`): `dialos-start-ansage.py` fragt
`nutzer` bei der Start-Ansage per Sprache nach der gewünschten
Lautstärke (100/75/50/25 %/aus) - echt mit Stephans Stimme getestet
(15./16.08.), dabei einen Timing-Bug gefunden und behoben (fehlendes
Startsignal vor der Aufnahme). Außerdem: Wetter-Standort läuft jetzt
über GeoClue2 statt IP-Raten (Auslöser: `wttr.in` zeigte Wien statt
Stephans echtem Standort Seefeld in Tirol) - mit Genauigkeits-
Schwellwert, der zu grobe Schätzungen verwirft und die Wetteransage
dann bewusst ausfallen lässt, statt eine falsche Stadt zu nennen.

Konkrete offene Aufgaben stehen ausschließlich in [TODO.md](TODO.md),
nicht hier - so bleibt der Stand an einer einzigen Stelle aktuell.

## Offene Entscheidungen (siehe auch [docs/offene-punkte.md](docs/offene-punkte.md))

- Sudo-Rechte für den Standard-Benutzer "nutzer" (Platzhalter-Passwort
  aktuell zufällig generiert, echte Policy für die spätere
  sprachgesteuerte Wartung noch offen).
- Referenz-Hardware final festlegen (Laptop UND Sicherheits-Stick UND
  Bluetooth-Lautsprecher/-Mikrofon - alle drei noch offen, siehe
  `docs/hardware.md`).
- Rechtschreibprüfung (hunspell/aspell) fehlt noch, siehe
  `docs/offene-punkte.md`.
- Kompletter neuer Installations-Pfad (siehe oben) noch nicht
  end-to-end auf einem frischen System getestet.

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
Terminalbefehle für Stephan. Lokale Git-Identität
(`user.name`/`user.email`/`credential.helper=store`) ist seit 2026-08-14
eingerichtet und verifiziert - `git push` funktioniert direkt.

`TODO.md` im Repo-Root ist für kurzfristige, konkrete Aufgaben gedacht -
anders als `docs/offene-punkte.md`, das für grundsätzliche, noch
unentschiedene Architekturfragen gedacht ist. Erledigte Einträge werden
mit einem Häkchen (`[x]`) markiert und bleiben stehen (nicht löschen) -
so bleibt nachvollziehbar, was schon erledigt ist.
