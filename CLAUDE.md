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

## ✅ Calamares-Installer: Deutsch + DialOS-Branding (2026-08-10)

Ausgangslage: Der von Penguins' Eggs ins Live-System eingebundene
Installer war Krill (React+Ink-TUI, textbasiert). Für Krill gibt es
keinen dokumentierten Branding-Mechanismus (Logo/Farben/Schriftfarbe) -
hätte Patches am TypeScript/React-Ink-Quellcode erfordert, als zu
fragil verworfen. Auf Stephans Entscheidung hin auf **Calamares**
(GUI-Installer) umgestiegen, mit der Vorgabe: Branding anpassbar UND
auf Deutsch funktionsfähig.

**Deutsch:** Erst fälschlich angenommen, Debians `calamares`-Paket
bringe gar keine Kern-UI-Übersetzung mit (kein loses
`/usr/share/calamares/lang/`-Verzeichnis per `find`/`dpkg -L`
auffindbar - nur die branding-eigenen, sehr kleinen `lang/`-Ordner mit
ar/en/eo/fr/nl, kein Deutsch). Tatsächlich bettet Calamares seine
Kern-Übersetzungen als kompilierte Qt-Ressourcen direkt ins Programm
ein (nicht als lose Dateien sichtbar) und wählt die Sprache automatisch
nach System-Locale. Da der T490 auf Deutsch eingestellt ist, lief
`sudo calamares` von Anfang an komplett auf Deutsch (Titel,
Seitenüberschriften, Willkommenstext, Buttons) - **kein
Zusatzaufwand nötig**. Der Umweg über das manuelle Herunterladen und
Kompilieren von `calamares_de.ts` → `.qm` (via `lrelease-qt6` aus dem
Paket `qt6-tools-dev-tools`) war am Ende überflüssig, wurde aber nicht
schädlich - kann ignoriert/gelöscht werden.

**Branding:** Das bare `calamares`-Paket liefert kein
`/etc/calamares/`-Config. Das Paket **`calamares-settings-debian`**
liefert dagegen eine vollständige, einsatzbereite
`/etc/calamares/settings.conf` (kompletter Modul-Ablauf
welcome→locale→keyboard→partition→users→summary→exec) plus eine
"debian"-Branding-Komponente unter
`/etc/calamares/branding/debian/`. Eigene Komponente `dialos` als
Kopie davon angelegt (`/etc/calamares/branding/dialos/`):

- `branding.desc`: `componentName: dialos` (**muss exakt dem
  Ordnernamen entsprechen**, sonst Fatal-Error beim Start - genau das
  ist uns beim ersten Testlauf passiert), `productName: DialOS`,
  Bilder `mark.png` (Logo/Icon), `logo-tagline.png` (Willkommensbild),
  Sidebar-Farben `#0B1E2D` (Hintergrund, dunkles Marken-Navy) /
  `#0774D5` (aktueller Schritt, Blauton aus dem Logo gesampelt).
- `show.qml`: Slideshow während der Installation, Bild
  `logo-full.png`, deutscher Willkommenstext.
- `stylesheet.qss`: **neu angelegt** (gab es bei "debian" nicht) -
  einziger Weg, die generelle Schriftfarbe im Hauptbereich zu setzen
  (der `style:`-Block in `branding.desc` deckt nur die Seitenleiste
  ab). Wird automatisch erkannt, sobald die Datei im
  Komponenten-Ordner existiert, gilt app-weit. Aktuell simpel
  `* { color: #1A1A1A; }` (dunkles Grau für Kontrast/Lesbarkeit).
- `/etc/calamares/settings.conf`: `branding: debian` →
  `branding: dialos` geändert (Zeile 105).

Verifiziert per Screenshot (`sudo calamares` direkt auf dem
installierten System gestartet, nur Willkommensseite angesehen, nicht
bis zur Partitionierung durchgeklickt): eigenes Logo, dunkles
Marken-Navy in der Seitenleiste, "DialOS Installationsprogramm" als
Fenstertitel, "Willkommen bei Calamares, dem Installationsprogramm für
DialOS 1.0", Sprachauswahl zeigt "Deutsch" als Standard. **Funktioniert.**

Alle sechs Dateien zusätzlich nach
`iso-build/config/includes.chroot/etc/calamares/` im Git-Repo
gespiegelt (gleiches Muster wie schon bei `background.png`), damit die
Anpassung nicht verloren geht, falls der T490 nochmal neu aufgesetzt
werden muss, bevor der nächste ISO-Build sie einfängt.

`productUrl`/`supportUrl`/etc. in `branding.desc` zeigen vorerst als
Platzhalter auf das GitHub-Repo - Stephans bewusste Entscheidung, erstmal
so zu lassen (Repo ist zwar privat, aber in der aktuellen Testphase
klickt da eh niemand drauf).

### 🐛 Gefundener Bug: Standort-Seite zeigte "New York" statt Deutschland

Beim Kontrollgang durch "Standort" und "Tastatur" zeigte die
Standort-Karte als Startpunkt New York statt Deutschland. Ursache:
`calamares-settings-debian` liefert kein
`/etc/calamares/modules/locale.conf` mit, und Calamares' eigener
eingebauter Standardwert für Region/Zeitzone ist laut Doku
buchstäblich `America/New_York` (kein GeoIP-Fehler - GeoIP war schlicht
nicht konfiguriert, weil die Datei komplett fehlte). Fix: eigene
`locale.conf` angelegt mit festem `region: Europe` / `zone: Berlin`
(GeoIP bewusst nicht aktiviert - ein fester Standardwert ist robuster
als von einem Online-Dienst abzuhängen, der beim Installieren mal
ausfallen könnte). Nach Fix: Standort zeigt Berlin, Tastatur zeigt
"Deutsch"/"Standard" - beides korrekt. Datei nach
`iso-build/config/includes.chroot/etc/calamares/modules/locale.conf`
im Git-Repo gespiegelt.

(Nebenbei geklärt: Der T490 selbst läuft mit Systemzeitzone
Europe/Vienna statt Berlin - das ist **kein Bug**, Stephan sitzt
tatsächlich in Österreich. Betrifft nur die eigene Konfiguration des
Testrechners, nicht den `region`/`zone`-Standardwert für neue
Installationen.)

## ✅ Hardware-Livetest auf dem T490 (2026-08-10)

Erster echter Hardware-Test auf dem installierten System (Konto
`DialOS-Admin`), alle drei Punkte bestanden:

- **WLAN: ✅** Lief ohne jedes Zutun - Gerät automatisch verbunden
  (`nmcli`), echte IP-Adresse, gutes Signal.
- **Sound: ✅** Hardware (`aplay -l`: Intel PCH, Analog + 3× HDMI) und
  Software-Stack (PipeWire/PipeWire-Pulse/WirePlumber) beide sauber
  erkannt/aktiv. Ein Lücke: `pactl` (aus `pulseaudio-utils`) war nicht
  vorinstalliert - nachgerüstet. Testton per `speaker-test` gehört.
- **Orca: ✅** Vorinstalliert (48.1, Wayland/GNOME), Umschalten per
  **Super+Alt+S** funktioniert, liest vor.

### ✅ Natürlichere deutsche Stimme für Orca: Piper statt espeak-ng (2026-08-10)

Die Standard-Orca-Stimme (`espeak-ng`) klang wie erwartet robotisch.
`docs/sprachsteuerung.md` hatte dafür schon "Piper oder RHVoice" als
Zielvorgabe notiert. RHVoice ist in Debian nur im "non-free"-Bereich
verfügbar (nicht aktiviert) und generell schwächer als Piper. Piper
selbst ist kein Debian-Paket, sondern wird direkt von GitHub geladen.

**Umsetzung** (bewährtes Community-Skript, vor Ausführung Zeile für
Zeile geprüft):
1. `sudo apt-get install -y jq sox` (Abhängigkeiten des Skripts).
2. Install-Skript geladen und ausgeführt (**nicht mit `sudo`** - sonst
   landet alles unter `/root` statt im Nutzer-Home und Orca/Sprach-
   ausgabe, die als Nutzer laufen, finden nichts):
   `wget -4 -O install-piper-speechd.sh "https://gist.githubusercontent.com/alexkuz/f24f93245ff80458c9b6ec93c644c40b/raw/"`
   Zeile `apt -qq install jq sox` im Skript selbst hat kein `sudo` -
   vorher auskommentiert, da Abhängigkeiten schon manuell installiert.
   Legt an: `~/.local/share/speech-dispatcher-piper/` (Piper-Binary +
   Stimmdateien, werden bei Bedarf von HuggingFace nachgeladen) und
   `~/.config/speech-dispatcher/modules/piper-generic.conf`
   (`sd_generic`-Modul-Config mit `AddVoice`-Zeilen für alle
   verfügbaren Piper-Stimmen inkl. zehn deutscher, z. B.
   `de_DE-thorsten-high`, `-medium`, `-low`, `de_DE-kerstin-low` usw.).
3. **Zwei `sed`-Fallen** (gleiches Muster wie beim Calamares-
   `settings.conf` weiter oben - Musterbasierte `sed`-Ersetzung mit
   `^`-Anker schlägt fehl, wenn die Ziel-Zeile mit einem führenden
   Leerzeichen beginnt, was in mehreren dieser generierten Configs der
   Fall ist. **Lehre: bei speech-dispatcher/Calamares-Configs immer
   erst mit `grep -n` die Zeilennummer holen und zeilengenau mit
   `sed -i 'NNNs/.*/neuer Inhalt/'` ersetzen, nicht musterbasiert.**
   - `~/.config/speech-dispatcher/speechd.conf`: `AddModule "piper"
     "sd_generic" "piper-generic.conf"` fehlte und `DefaultModule`
     zeigte noch auf `espeak-ng`.
   - `~/.config/speech-dispatcher/modules/piper-generic.conf`:
     `DefaultVoice` zeigte noch auf die englische Test-Stimme
     `en_GB-alan-low` statt einer deutschen.
4. **Weitere Falle:** Nach Config-Änderungen wirkungslos, weil noch
   ein `speech-dispatcher`-Hintergrundprozess (seit dem ersten
   Orca-Test) mit der alten, beim Start eingelesenen Config lief -
   Config wird nicht automatisch neu geladen. Fix: `pkill -f
   speech-dispatcher`, danach spawnt der nächste `spd-say`/Orca-Aufruf
   den Prozess frisch mit aktueller Config.
5. Stimme `de_DE-thorsten-high` (höchste Qualitätsstufe) als
   `DefaultVoice` gesetzt - deutlich hörbare Verbesserung gegenüber
   espeak-ng, bestätigt sowohl per direktem `spd-say`-Test als auch
   über Orca.
6. Sprechtempo minimal gedrosselt: `GenericRateMultiply` von `1` auf
   `0.85` - Stephans Eindruck bei Orca war "schon etwas besser, aber
   noch nicht so gut wie beim direkten Test", mit `0.85` als "besser"
   bestätigt.

### ✅ Piper systemweit gemacht (2026-08-10, gleicher Tag)

Die anfängliche Einrichtung lag nur unter `~/.config/`/`~/.local/share/`
von `DialOS-Admin` - für echte Endkunden-Konten hätte das nicht
automatisch gegriffen. Deshalb noch am selben Tag systemweit verlagert:

1. Piper-Binary + Stimmdateien nach `/usr/local/share/dialos-piper/`
   verschoben (root, aber `chmod -R a+rX` - für alle Konten lesbar).
   Größe: Piper-Programm selbst ~52 MB, dazu pro geladener Stimme die
   `.onnx`-Datei (`de_DE-thorsten-high.onnx` ~114 MB).
2. `/etc/speech-dispatcher/modules/piper-generic.conf` neu angelegt
   (systemweite Modul-Config, Pfad zeigt jetzt auf
   `/usr/local/share/dialos-piper`; `DefaultVoice
   de_DE-thorsten-high`, `GenericRateMultiply 0.85`). Komplette Datei
   in einem Rutsch per `tee`-Heredoc geschrieben statt einzelner
   `sed`-Änderungen - robuster.
3. In `/etc/speech-dispatcher/speechd.conf` (systemweit, nicht die
   Kopie im Home-Ordner) `AddModule "piper"` ergänzt und
   `DefaultModule` auf `piper` gesetzt.
4. **Verifiziert für den Kundenkonto-Fall:** `DialOS-Admin`s eigene
   Nutzer-Config testweise beiseitegeschoben, `speech-dispatcher`
   neu gestartet, `spd-say` ganz ohne Parameter aufgerufen - lief
   sofort auf Deutsch mit der Thorsten-Stimme. Bestätigt: ein neues
   Kundenkonto ohne jede Vorkonfiguration bekommt das automatisch.
5. Aufgeräumt: alte Kopie unter `~/.local/share/speech-dispatcher-piper/`
   gelöscht, Test-Backup der Nutzer-Config ebenfalls gelöscht.
6. Config-Dateien (nicht die große Binary/Sprachdatei) nach
   `iso-build/config/includes.chroot/etc/speech-dispatcher/` im
   Git-Repo gespiegelt.

**Reproduzierbarkeit** (bei künftigem Neuaufbau):
```bash
sudo apt-get install -y jq sox
sudo mkdir -p /usr/local/share/dialos-piper/voices
curl -s -L -o /tmp/piper.tar.gz "https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz"
sudo tar -xzf /tmp/piper.tar.gz -C /usr/local/share/dialos-piper
curl -s -L -o /tmp/thorsten.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx?download=true"
curl -s -L -o /tmp/thorsten.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json?download=true"
sudo mv /tmp/thorsten.onnx /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx
sudo mv /tmp/thorsten.onnx.json /usr/local/share/dialos-piper/voices/de_DE-thorsten-high.onnx.json
sudo chmod -R a+rX /usr/local/share/dialos-piper
sudo chmod +x /usr/local/share/dialos-piper/piper/piper
```
Die Config-Dateien selbst liegen ja schon im Git-Repo.

## Datei-Workflow mit Stephan (wichtig, 2026-08-10)

Die Geräte-Brücke zu diesem Rechner ist getrennt (seit der
Neuinstallation) - Claude hat keinerlei direkten Zugriff auf den T490.
Dateien, die Claude als Download im Chat anbietet, kommen bei Stephan
NICHT automatisch auf dem T490 an. **Alle Änderungen - auch an
CLAUDE.md/TODO.md/README.md selbst - müssen als Terminal-Befehle
(cat/heredoc, sed, etc.) gegeben werden, die Stephan direkt einfügt.**
Das gilt auch rückwirkend: mehrere CLAUDE.md/TODO.md-Updates vom
10.08.2026 wurden zunächst nur als Chat-Datei geschickt und sind nie im
echten Repo gelandet - nachträglich per Sammel-Befehl nachgeholt.

`TODO.md` im Repo-Root wurde angelegt, verlinkt in der Kopfzeile von
`README.md` rechts neben Änderungsprotokoll. Dort kommen kurzfristige,
konkrete Aufgaben rein - anders als `docs/offene-punkte.md`, das für
grundsätzliche, noch unentschiedene Architekturfragen gedacht ist.
Erledigte Einträge werden aus `TODO.md` gelöscht statt nur abgehakt.

## 🐛 Gefundener Bug: Praktisch alle Sprachpakete installiert (2026-08-10)

Beim Kontrollgang nach dem ersten konsolidierten ISO-Build fiel auf,
dass ganz oben rechts im GNOME-Panel eine japanische Eingabemethode
(Anthy) als aktiv angezeigt wurde statt Deutsch. Untersuchung ergab:
`iso-build/config/package-lists/desktop.list.chroot` enthielt
`task-gnome-desktop` (ein Debian-Tasksel-Metapaket) - dessen
Recommends haben über die komplette `task-*`/`task-*-desktop`-Familie
praktisch **jede** von Debian unterstützte Sprache installiert (~70
Sprachen, von Albanisch bis Xhosa), inklusive japanischer
IBus-Eingabemethoden (`ibus-anthy`, `ibus-mozc`), die dann als erster
Eintrag in `org.gnome.desktop.input-sources` registriert wurden und
damit den GNOME-Standard überstimmt haben.

Fix:
- `task-gnome-desktop` aus `desktop.list.chroot` entfernt (wird eh
  nicht gebraucht, `gnome-core` steht schon separat in der Liste),
  ersetzt durch `task-german` + `task-german-desktop` (gezielt nur
  deutsche Sprachunterstützung: Wörterbücher, Übersetzungen).
- Auf dem laufenden System aufgeräumt: alle `task-*`-Pakete außer
  `task-desktop`, `task-gnome-desktop`, `task-laptop`, `task-german`,
  `task-german-desktop`, `task-english` per `apt-get purge` +
  `autoremove` entfernt. `ibus-anthy`/`ibus-mozc`/`anthy` hingen danach
  noch dran (nicht sauber als "automatisch installiert" markiert),
  explizit nachpurged.
- `org.gnome.desktop.input-sources` für `DialOS-Admin` per `gsettings`
  auf `[('xkb', 'de')]` zurückgesetzt.

**Wichtig:** Die zuerst gebaute konsolidierte ISO
(`egg-of-debian-trixie-laptop-t490-dialos-amd64-2026-08-10_0934.iso`)
enthält diesen Bug noch - **nicht für den Live-Boot-Test verwenden**,
muss nach diesem Fix neu gebaut werden.

## Calamares-Branding wird von eggs/coa live überschrieben (2026-08-11)

Erster echter Live-Boot-Test (USB-Stick, komplette Installation inkl.
Partitionierung) zeigte: Der Calamares-Assistent selbst (Willkommen-
Bildschirm, Fortschrittsanzeige mit Pinguin-Werbebildern) zeigte
Standard-"eggs"-Branding statt DialOS, obwohl `/etc/calamares/
settings.conf` (branding: dialos) und `/etc/calamares/branding/dialos/`
sowohl im Rezept als auch im gebauten Live-Abbild (per Squashfs-Mount
verifiziert) korrekt vorhanden waren.

Ursache (per Quellcode-Recherche in github.com/pieroproietti/
penguins-eggs bestätigt): Der `eggs sysinstall`-Befehl (aufgerufen über
`/usr/share/applications/install-system.desktop`, `Exec=pkexec eggs
sysinstall`) generiert bei jedem Start sein eigenes Standard-"eggs"-
Branding frisch nach `/etc/calamares/branding/eggs/` im beschreibbaren
Live-Overlay (RAM), unabhängig von unserem `/etc/calamares/`-Rezept.
Calamares' `unpackfs`-Modul kopiert beim eigentlichen Installieren aber
direkt aus der (unveränderten) Squashfs, nicht aus dem Live-Overlay -
deshalb landete am Ende trotzdem unser korrektes Branding auf der
Zielplatte, aber der Installations-Bildschirm selbst zeigte die
falschen (generischen) Inhalte.

Fix: `eggs`/`coa` unterstützt einen festen Vendor-Overlay-Pfad
`/etc/penguins-eggs.d/brain.d/assets/calamares/` (Quelle:
`coa/pkg/sysinstall/setup/branding-desc.go`). Existiert dieser Ordner,
kopiert `copyBrandingOverlay()` seinen Inhalt (inkl. `branding.desc`,
falls vorhanden) über das generierte "eggs"-Branding drüber. Der
Zielordner heißt bei eggs aber immer `eggs`, nicht `dialos` - deshalb
muss `componentName` in der Overlay-`branding.desc` auf `eggs` gesetzt
werden (sonst wieder der bekannte "componentName muss zum
Verzeichnisnamen passen"-Fehler). Umgesetzt in
`iso-build/config/includes.chroot/etc/penguins-eggs.d/brain.d/assets/
calamares/` (Kopie von `branding/dialos/` mit angepasstem
componentName).

Für das Ei-Icon selbst (`Install System`, `Icon=penguins-eggs`) wurde
zusätzlich `/usr/share/applications/install-system.desktop` per
`includes.chroot` überschrieben (Name auf "DialOS installieren",
Icon auf `/etc/calamares/branding/dialos/mark.png`).

Kein Vendor-Override-Mechanismus gefunden für `modules/locale.conf` -
GeoIP-basierte Standort-Vorschläge (z. B. "Rome" statt "Berlin") können
also weiterhin auftreten und müssen von der installierenden Person
manuell korrigiert werden. Unkritisch, da Endkunden den Installer im
Rahmen der Zwei-Phasen-Provisionierung nie selbst sehen.

Wichtige Nebenerkenntnis beim Debuggen: Der Live-USB-Stick lässt sich
direkt einsehen, ohne neu zu booten - `mount -o loop,ro
/pfad/zum/stick/live/filesystem.squashfs /mnt/irgendwas` zeigt exakt
den Zustand des Live-Abbilds, das tatsächlich gebaut wurde. Sehr
nützlich, um "steckt der Fix wirklich im Abbild?" von "verhält sich das
Programm zur Laufzeit anders?" zu unterscheiden.
