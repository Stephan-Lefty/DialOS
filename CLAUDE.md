# Hinweise für Claude

Dieses Repository ist DialOS – eine barrierefreie Debian-13/GNOME-
Live-ISO mit voller Sprachsteuerung für blinde und motorisch
eingeschränkte Nutzer. Stephan arbeitet allein an diesem Projekt (kein
Team) – bitte durchgehend "du" statt "ihr/euch" verwenden, und Stephan
darf dich gerne "ClaudIA" nennen.

**Lies zuerst [README.md](README.md) und alle Dateien in [docs/](docs/)**
für den vollständigen Kontext (Architektur, Zielgruppe, Sicherheit,
Sprachsteuerung, Telefonie, Ersteinrichtung, offene Punkte). Diese
Datei hier ist nur eine kurze Landkarte + der aktuelle Stand, keine
Doppelung der eigentlichen Doku.

## Aktueller Stand (Stand: 2026-08-07, Wochenende vor der nächsten Session)

Wir stecken mitten in der ersten funktionierenden ISO. Zwei parallele
Wege wurden verfolgt:

1. **Docker/live-build-Pipeline** (`iso-build/`, `iso-build/build.sh`):
   Nach ca. 18 Build-Versuchen und etlichen sehr eigenwilligen
   Umgebungs-Bugs (siehe Kommentare oben in `build.sh` und die
   Commit-Historie von `iso-build/`) kamen wir zuletzt bis kurz vor eine
   fertige ISO-Datei, haben aber noch NIE tatsächlich eine fertige
   `.iso` gesehen. Grund für die vielen Probleme: `live-build` läuft
   hier verschachtelt in einem Docker-Container, der wiederum in
   Claudes eigener Sandbox-Umgebung läuft – eine sehr untypische
   Konstellation, die für praktisch jeden Bug verantwortlich war
   (fehlende Geräte-Rechte, kein D-Bus, sich überdeckende Mounts, ...).

2. **NEUER PLAN (aktuell bevorzugt):** Stephan hat Debian 13 + GNOME
   testweise direkt auf dem Ziel-Testgerät (Lenovo ThinkPad T490)
   installiert – echte Hardware, kein Chroot/Docker. Das umgeht die
   Ursache fast aller bisherigen Probleme. Plan: Auf diesem echten
   System direkt unsere Konfiguration nachziehen (Paketliste aus
   `iso-build/config/package-lists/desktop.list.chroot`, Branding aus
   `iso-build/config/includes.chroot*/`, RustDesk/Claude-Code-Installation
   aus `iso-build/config/hooks/live/`, Autologin, Installer/Rekey-Tools
   aus `iso-build/config/includes.chroot/usr/local/sbin/`) – die
   bestehenden Skripte dabei als **Vorlage/Rezept** nutzen, aber
   **interaktiv auf dem echten System ausführen** statt blind in einer
   Chroot-Umgebung. Anschließend mit **[Penguins' Eggs](https://penguins-eggs.net/)**
   (unterstützt Debian, hat laut FAQ deutsche Sprachunterstützung) eine
   startfähige ISO aus dem fertig eingerichteten System snapshotten,
   statt sie blind aus Konfigurationsdateien zusammenzubauen.

Die Docker-Pipeline bleibt als Referenz/Fallback bestehen (falls
Penguins' Eggs auch nicht klappt, dazu gibt es zusätzlich noch eine
Cubic-Anleitung: `iso-build/CUBIC-ANLEITUNG.md`), wird aber erstmal
nicht weiterverfolgt.

## Nächste konkrete Schritte

1. Auf dem T490 (oder wo auch immer diese Session läuft): prüfen, ob
   `penguins-eggs` schon installiert ist, sonst installieren.
2. Paketliste aus `iso-build/config/package-lists/desktop.list.chroot`
   per `apt-get install` auf dem echten System nachziehen.
3. Branding-Dateien aus `iso-build/config/includes.chroot*/` an die
   jeweils gleiche Stelle im echten System kopieren (Pfade siehe
   Dateistruktur, z.B. `usr/share/backgrounds/dialos/` →
   `/usr/share/backgrounds/dialos/`), `dconf update` danach ausführen.
4. Hook-Skripte aus `iso-build/config/hooks/live/*.hook.chroot` als
   Vorlage für die manuelle Einrichtung nutzen (RustDesk, Claude Code
   CLI, Standard-Benutzer + Autologin, Plymouth-Theme aktivieren).
5. `dialos-install`/`dialos-rekey` aus
   `iso-build/config/includes.chroot/usr/local/sbin/` sind für die
   LUKS+USB-Stick-Verschlüsselung gedacht - auf dem bereits installierten
   Test-System vermutlich nicht direkt anwendbar (das System läuft ja
   schon unverschlüsselt), das wäre ein späterer Schritt.
6. Alles live auf der Hardware durchtesten (WLAN, Ton, Anzeige, Orca,
   RustDesk, ...) - das können wir über die Docker-Pipeline nie
   verifizieren.
7. Sobald alles läuft: mit Penguins' Eggs eine ISO ziehen.

## Offene Entscheidungen (siehe auch [docs/offene-punkte.md](docs/offene-punkte.md))

- Sudo-Rechte für den Standard-Benutzer "nutzer" (Platzhalter-Passwort
  aktuell zufällig generiert, echte Policy für die spätere
  sprachgesteuerte Wartung noch offen).
- Referenz-Hardware final festlegen (aktuell T490 zum Testen, kein
  WWAN-Modul verbaut).
- Rechtschreibprüfung (hunspell/aspell) fehlt noch, siehe
  `docs/offene-punkte.md`.
- Neue Grafiken (`assets/slogan.png`, aktualisierte
  `assets/splash.png`/`assets/wallpaper-dark.png`) liegen im Repo, sind
  aber noch nicht verkleinert/komprimiert oder ins ISO-Build eingebunden.

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
