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

**GitHub-Repo:** https://github.com/Stephan-Lefty/DialOS (privat).

## Aktueller Stand (Stand: 2026-08-10)

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

2. **NEUER PLAN (aktuell bevorzugt, in Umsetzung):** Stephan hat Debian 13
   + GNOME testweise direkt auf dem Ziel-Testgerät (Lenovo ThinkPad T490)
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

1. ✅ **Erledigt (2026-08-09):** `penguins-eggs` auf dem T490 installiert
   (via `fresh-eggs.sh` — Achtung, das Skript im Repo heißt `fresh-eggs.sh`,
   nicht `fresh-eggs` wie in älterer Doku beschrieben. Node 20.19.2 aus
   Debian-Repo reicht aus, die in der fresh-eggs-Doku genannte
   Node-≥22-Anforderung griff hier nicht).
2. ✅ **Erledigt (2026-08-09):** Paketliste aus
   `iso-build/config/package-lists/desktop.list.chroot` per
   `apt-get install` auf dem T490 nachgezogen, per `dpkg -l` verifiziert.
3. ✅ **Erledigt (2026-08-09):** Branding-Dateien aus
   `iso-build/config/includes.chroot*/` auf das T490-System kopiert
   (Backgrounds, Login-Logo, dconf-Branding/Defaults, Plymouth-Theme-
   Dateien), `dconf update` ausgeführt und per `dconf dump` verifiziert.

   Dabei zusätzlich die neuen Grafiken aus `assets/` verarbeitet:
   `wallpaper-dark.png` und `splash.png` waren unkomprimiert (je ~14 MB,
   gleiche Auflösung 2559×1440 wie die bereits genutzten Bilder) –
   verlustfrei nachkomprimiert (auf ~2,5 MB bzw. ~2,0 MB) und ins Rezept
   übernommen: `wallpaper-dark.png` → `includes.chroot/usr/share/backgrounds/dialos/`,
   `splash.png` → als `background.png` nach
   `includes.chroot_before_packages/usr/share/plymouth/themes/dialos/`
   (passend zur README-Beschreibung "Boot-/Login-Bildschirm"). `slogan.png`
   bleibt bewusst unbenutzt im Repo liegen (aktuell keine geplante Verwendung).

4. ✅ **Erledigt (2026-08-10):** Hook-Skripte aus
   `iso-build/config/hooks/live/*.hook.chroot` manuell nachgezogen:

   - a) ✅ Benutzer `nutzer` angelegt (`adduser --disabled-password`,
     Gruppen `sudo,audio,video,plugdev,netdev,bluetooth,scanner,lpadmin,cdrom`,
     zufälliges Sudo-Passwort per `chpasswd` gesetzt — unkritisch, siehe
     `docs/offene-punkte.md`, Sudo-Policy für `nutzer` ist noch offen).
     **Autologin funktioniert jetzt** (Lösung siehe unten).
   - b) ✅ RustDesk installiert. Wichtig: das `.deb`-Postinst aktiviert den
     systemd-Autostart automatisch (`multi-user.target.wants/rustdesk.service`)
     — das widerspricht `docs/sicherheit-datenschutz.md` (RustDesk darf
     NICHT dauerhaft laufen, nur auf "Hilfe rufen"-Zuruf). Korrigiert mit
     `sudo systemctl disable --now rustdesk` — verifiziert: `disabled`/`inactive`.
     Für die spätere Sprachsteuerungs-Anbindung: die bereits in der
     Paketliste enthaltenen `zenity`/`polkitd`/`pkexec` sehen wie die
     passenden Bausteine für einen passwortlosen, gezielten
     `systemctl start rustdesk`-PolicyKit-Trigger aus.
   - c) ✅ Claude Code CLI via `npm install -g @anthropic-ai/claude-code`
     installiert. `npm` warnt wegen `EBADENGINE` (Paket verlangt Node ≥22,
     wir haben 20.19.2), funktioniert aber einwandfrei (`claude --version`
     liefert `2.1.226`) — Warnung ist ignorierbar.
   - d) ✅ `sudo plymouth-set-default-theme -R dialos` ausgeführt, initramfs
     sauber neu gebaut, **und der grafische Splash läuft jetzt** (Ursache
     und Fix siehe unten).
   - e) ✅ `dconf update` erneut ausgeführt (Sicherheitsnetz).

   ### ✅ GELÖST (2026-08-10): GDM-Autologin

   **Ursache gefunden:** Der eigentliche Schalter ist **nicht**
   `/etc/gdm3/custom.conf`, sondern eine **Pro-Benutzer-Eigenschaft direkt
   im AccountsService-Dienst** (`org.freedesktop.Accounts.User.AutomaticLogin`,
   per D-Bus gesetzt/abgefragt) — offenbar der primäre Mechanismus bei
   dieser Debian-13/GDM-48-Kombination, unabhängig von `custom.conf`
   (das bleibt trotzdem unverändert bestehen, vermutlich als globaler
   Master-Schalter über `AutomaticLoginEnable=true`, das haben wir nicht
   weiter angefasst). Gefunden über Stephans Vorschlag, es über die
   GNOME-Einstellungen-GUI zu probieren: dort den Schalter bei `stephan`
   testweise aktiviert → Autologin funktionierte sofort, obwohl
   `custom.conf` dabei nachweislich unverändert blieb. Live-Check per
   `gdbus` bestätigte danach: `stephan` hatte `AutomaticLogin=true`,
   `nutzer` `AutomaticLogin=false` in AccountsService, obwohl `custom.conf`
   die ganze Zeit `AutomaticLogin=nutzer` sagte.

   Alle >10 in der vorherigen Session ausgeschlossenen Ursachen
   (Dateiinhalt, Rechte, AppArmor, PAM, Pfad, journald, dconf, systemd-
   Unit) waren also korrekterweise unauffällig — sie waren schlicht nicht
   der relevante Mechanismus.

   **Der Fix (reproduzierbar, skriptbar, kein GUI nötig):**
   ```bash
   # AutomaticLogin-Property des Zielbenutzers ermitteln (Objekt-Pfad)
   sudo gdbus call --system --dest org.freedesktop.Accounts \
     --object-path /org/freedesktop/Accounts \
     --method org.freedesktop.Accounts.FindUserByName nutzer
   # liefert z.B. /org/freedesktop/Accounts/User1001

   # Autologin für nutzer aktivieren
   sudo gdbus call --system --dest org.freedesktop.Accounts \
     --object-path /org/freedesktop/Accounts/User1001 \
     --method org.freedesktop.Accounts.User.SetAutomaticLogin true

   # Autologin für das Admin-/Setup-Konto deaktivieren (siehe DialOS-Admin
   # unten — wichtig, sonst würde das Kundengerät als Admin statt als
   # nutzer starten!)
   sudo gdbus call --system --dest org.freedesktop.Accounts \
     --object-path /org/freedesktop/Accounts/User1000 \
     --method org.freedesktop.Accounts.User.SetAutomaticLogin false
   ```
   Verifiziert per Neustart (2026-08-10): `nutzer` wird jetzt ganz ohne
   Anmeldebildschirm automatisch eingeloggt. **Das ist der Weg, der ins
   künftige Setup-Skript gehört** (siehe "DialOS-Admin" unten), nicht das
   Bearbeiten von `custom.conf`.

   System-Kontext (für spätere Sessions): Debian 13 (Trixie), GDM 48.0-2,
   Wayland-Session. `/var/lib/AccountsService/users/` ist auf diesem
   System übrigens leer — der AccountsService persistiert den
   Autologin-Status offenbar nicht in dieser klassischen Datei-Ablage,
   sondern anderswo (nicht weiter untersucht, war für den Fix nicht nötig).

   ### 🆕 Neues Konzept: `DialOS-Admin`-Konto (Entscheidung 2026-08-10)

   Da Stephan (oder später ggf. jemand anderes) jedes Gerät im Büro-Setup
   einrichtet, wird das bisher genutzte persönliche Konto (`stephan` auf
   dem Testgerät) konzeptionell durch ein generisches Konto **`DialOS-Admin`**
   ersetzt, das bei jedem Rollout gleich heißt:

   - Bei der Debian-Installation für ein echtes Zielgerät wird das erste
     (Installer-)Konto künftig `DialOS-Admin` genannt statt eines
     persönlichen Namens.
   - Am Ende des Büro-Setups (nach allen Schritten 1-6) richtet ein
     Skript `nutzer` ein und schaltet Autologin von `DialOS-Admin` auf
     `nutzer` um (siehe Fix oben).
   - **Entscheidung:** `DialOS-Admin` bleibt danach aktiv (mit Sudo),
     nur ohne Autologin — nicht sperren oder löschen. Grund: praktisch
     für künftige Fernwartung per RustDesk, Stephan kann sich als
     `DialOS-Admin` einloggen, ohne `nutzer`s laufende Sitzung anzufassen.
   - ✅ **Erledigt (2026-08-10):** Setup-Skript geschrieben unter
     `scripts/dialos-setup-nutzer.sh` (bewusst NICHT unter
     `iso-build/config/hooks/live/`, da dieser Ordner zur alten
     Chroot-Pipeline gehört und der `gdbus`/AccountsService-Teil einen
     laufenden D-Bus braucht, den es im Chroot-Build nicht gibt). Legt
     `nutzer` an (wie bisheriger Hook `0050-create-default-user.hook.chroot`)
     und schaltet danach per `gdbus` den Autologin vom übergebenen
     Admin-Konto auf `nutzer` um. Aufruf: `sudo ./dialos-setup-nutzer.sh
     [admin-benutzername]` (Standard: `$SUDO_USER`). Auf dem Testgerät
     bisher nur die Einzelschritte manuell ausgeführt, das Skript selbst
     noch nicht als Ganzes durchgetestet — beim nächsten Mal einmal
     laufen lassen (sollte idempotent sein, auch wenn `nutzer` schon
     existiert) um es zu verifizieren.
   - ✅ Geprüft: `docs/sicherheit-datenschutz.md` (Abschnitt "Automatische
     Anmeldung") beschreibt nur *dass* und *warum* es GDM-Autologin gibt,
     nicht den technischen Mechanismus (kein `custom.conf`-Verweis) —
     kein Korrekturbedarf.

   ### ✅ GELÖST (2026-08-10): Plymouth-Splash zeigte Text statt Grafik

   **Ursache:** In `/etc/default/grub` fehlte in
   `GRUB_CMDLINE_LINUX_DEFAULT` das Kernel-Boot-Argument `splash` (dort
   stand nur `"quiet"`). Ohne `splash` startet Plymouth zwar, bleibt aber
   im Text-Modus, egal wie das Theme konfiguriert ist — das erklärt,
   warum `plymouth-set-default-theme -R dialos` fehlerfrei lief, aber
   trotzdem nur ein Text-„Terminal"-Bildschirm zu sehen war.

   **Fix:**
   ```bash
   sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/' /etc/default/grub
   sudo update-grub
   ```
   Verifiziert per Neustart (2026-08-10, Stephans Bestätigung "Punkt 1
   und 2 sind ok"): grafischer DialOS-Splash läuft jetzt zwischen
   Lenovo-Logo und Anmeldung/Desktop. **Dieser `sed`-Befehl gehört mit
   ins künftige Büro-Setup-Rezept**, direkt nach der Theme-Aktivierung
   aus Punkt 4d.

   ### 🆕 Profilbild (Avatar) für `DialOS-Admin` automatisch setzen

   Stephans Wunsch: Wenn `DialOS-Admin` angelegt wird, soll das Konto
   sofort die DialOS-Bildmarke als Profilbild haben (Anmeldebildschirm +
   GNOME-Einstellungen), statt des Linux-Standardbilds.

   - ✅ **Erledigt (2026-08-10):** Skript geschrieben unter
     `scripts/dialos-set-avatar.sh` (gleicher Grund wie bei
     `dialos-setup-nutzer.sh`: braucht laufenden D-Bus/AccountsService,
     geht NICHT in der Chroot-Pipeline). Setzt per `gdbus`
     (`org.freedesktop.Accounts.User.SetIconFile`) die bereits als
     Login-Logo genutzte Datei `/usr/share/pixmaps/distributor-logo.png`
     (512×512, aus `assets/mark.png`, siehe Branding-Schritt 3) als
     `IconFile` für ein übergebenes Konto. Aufruf:
     `sudo ./dialos-set-avatar.sh [benutzername]` (Standard: `$SUDO_USER`).
   - Bewusst **nicht** unter `/etc/skel/Desktop/` abgelegt — anders als
     `dialos-setup-nutzer.sh` ist das kein Skript, das der Kunde je zu
     Gesicht bekommt, sondern ein reines Büro-Setup-Werkzeug für
     Stephan selbst (für `DialOS-Admin` bzw. testweise `stephan`).
   - 🔶 Beim ersten Testlauf auf `stephan` schlug der Aufruf mit
     „Befehl nicht gefunden" fehl — Ursache war (wie beim
     Setup-Nutzer-Skript, siehe Rechte-Falle unten) fehlendes
     Ausführen/Lese-Recht auf der frisch ins Repo geschriebenen Datei.
     Fix: `chmod 755 scripts/dialos-set-avatar.sh`.
   - ✅ **Verifiziert (2026-08-10):** Nach dem Rechte-Fix lief das
     Skript fehlerfrei. `IconFile`-Property per `gdbus ... Get ...
     org.freedesktop.Accounts.User IconFile` zeigt jetzt korrekt
     `/usr/share/pixmaps/distributor-logo.png` (statt vorher
     `/home/stephan/.face`). `/var/lib/AccountsService/icons/` bleibt
     dabei leer — wie schon beim Autologin-Property (siehe oben)
     scheint dieses System den AccountsService-Status nicht in der
     klassischen Datei-Ablage zu persistieren; der Live-D-Bus-Wert ist
     die maßgebliche Quelle und der ist korrekt.

   ### 🆕 Claude-Desktop-App als `.deb` auf dem Desktop

   Stephan kommuniziert lieber über die Claude-Desktop-App (diese
   Cowork-Bridge) als über die Claude Code CLI — die App soll deshalb
   nicht bei jedem Rollout händisch nachinstalliert werden müssen.

   - ✅ **Erledigt (2026-08-10):** Paketname ermittelt: `claude-desktop`
     (apt-Quelle `downloads.claude.ai/claude-desktop/apt/stable`, war auf
     dem T490 schon eingerichtet). Aktuelle Version zum Zeitpunkt des
     Schreibens: `1.26832.0` (amd64), ca. 172 MB.
   - ✅ Das `.deb` wird **nicht** ins Git-Repo committet (zu groß für
     Git, Binärdatei) — stattdessen hier der Befehl dokumentiert, der bei
     jedem Büro-Setup erneut ausgeführt wird und automatisch die
     passende/aktuelle Version für die System-Architektur zieht:
     ```bash
     cd /tmp && apt-get download claude-desktop
     sudo cp /tmp/claude-desktop*.deb /etc/skel/Desktop/
     sudo chmod 644 /etc/skel/Desktop/claude-desktop*.deb
     sudo chown root:root /etc/skel/Desktop/claude-desktop*.deb
     ```
     `644` reicht hier (anders als bei den `.sh`-Skripten), weil ein
     `.deb` per Doppelklick über eine grafische Paketinstallation
     (z.B. GNOME Software) geöffnet wird, die nur Leserecht braucht,
     kein Ausführen-Recht.
   - Verifiziert auf dem T490: Datei liegt korrekt unter
     `/etc/skel/Desktop/claude-desktop_1.26832.0_amd64.deb`,
     `-rw-r--r-- root root`. Landet damit automatisch auf dem Desktop
     jedes künftig angelegten `DialOS-Admin`-Kontos.

   ### ⚠️ Wichtige Rechte-Falle: `chmod +x` reicht bei `/etc/skel/`-Dateien NICHT

   Dateien, die über die Cowork-Geräte-Bridge auf den T490 geschrieben
   werden, starten mit Rechten `600` (nur Eigentümer darf lesen/schreiben).
   Ein einfaches `chmod +x` addiert dann nur die Ausführen-Bits, das
   Ergebnis ist `711` (`rwx--x--x`) — **kein Leserecht für andere
   Benutzer**. Für Skripte in `/etc/skel/Desktop/` ist das ein Problem:
   Ein neu angelegtes Konto (anderer Benutzer als der Eigentümer der
   Datei) kann die Datei dann zwar theoretisch ausführen, aber weder der
   Datei-Manager noch der Shell-Interpreter können sie lesen, um sie
   tatsächlich zu starten → „Befehl nicht gefunden". Trat zweimal auf
   (`dialos-setup-nutzer.sh` und `dialos-set-avatar.sh`), jeweils gefixt
   mit **`chmod 755`** statt `chmod +x`. **Faustregel fürs künftige
   Setup:** Bei jeder neuen Datei unter `/etc/skel/` immer explizit
   `chmod 755` (Skripte) oder `chmod 644` (reine Dateien wie `.deb`)
   setzen, nie nur `chmod +x`.

5. `dialos-install`/`dialos-rekey` aus
   `iso-build/config/includes.chroot/usr/local/sbin/` sind für die
   LUKS+USB-Stick-Verschlüsselung gedacht - auf dem bereits installierten
   Test-System vermutlich nicht direkt anwendbar (das System läuft ja
   schon unverschlüsselt), das wäre ein späterer Schritt.
6. Alles live auf der Hardware durchtesten (WLAN, Ton, Anzeige, Orca,
   RustDesk, ...) - das können wir über die Docker-Pipeline nie
   verifizieren. Plymouth-Theme visuell bestätigen (siehe Punkt 4d oben).
7. Sobald alles läuft: mit Penguins' Eggs eine ISO ziehen.

## Offene Entscheidungen (siehe auch [docs/offene-punkte.md](docs/offene-punkte.md))

- Sudo-Rechte für den Standard-Benutzer "nutzer" (Platzhalter-Passwort
  aktuell zufällig generiert, echte Policy für die spätere
  sprachgesteuerte Wartung noch offen).
- Referenz-Hardware final festlegen (aktuell T490 zum Testen, kein
  WWAN-Modul verbaut).
- Rechtschreibprüfung (hunspell/aspell) fehlt noch, siehe
  `docs/offene-punkte.md`.
- `scripts/dialos-setup-nutzer.sh` noch nicht als Ganzes (nur in
  Einzelschritten) durchgetestet, siehe Punkt 4 oben.

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
