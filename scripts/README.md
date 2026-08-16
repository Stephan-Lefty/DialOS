# Übersicht: Skripte in diesem Ordner

Diese Datei wird von Claude bei jeder Änderung an einem Skript in
diesem Ordner (neu angelegt, geändert, gelöscht) mit aktualisiert.

**Wichtig:** Alle Skripte hier sind ausschließlich für `dialosadmin`
gedacht - `nutzer` soll sie nie sehen. Deshalb werden sie explizit auf
`dialosadmin`s Desktop kopiert (siehe
[Debian-zu-DialOS.md](../docs/Debian-zu-DialOS.md), Schritt 13), **nicht**
über `/etc/skel/Desktop/` verteilt - das würde ungewollt auch bei
`nutzer` landen, da `/etc/skel/` in diesem Rezept nur `nutzer` als
"künftig angelegtes Konto" betrifft, kein zweites Admin-Konto
(Korrektur vom 2026-08-14, betraf vorher auch `dialos-setup-nutzer.sh`
und die `claude-desktop.deb`).

## dialos-full-office-setup.sh

Konsolidierungs-Skript (neu 2026-08-14): führt die Schritte 2-12, 14
(optional) und 15 aus [Debian-zu-DialOS.md](../docs/Debian-zu-DialOS.md)
automatisiert und der Reihe nach aus (Paketliste, Branding,
Autologin-Bootstrap, Calamares, RustDesk, Claude-CLI, Piper,
GNOME-Erweiterungen, Standardprogramme, Sprachausgabe-Skripte,
Sicherheits-Werkzeuge, Bluetooth-Kopplungsdaten, Vosk/hassil) - eine
Funktion pro Doku-Schritt, gleiche Nummerierung, damit Skript und Doku
nicht auseinanderlaufen. Deckt bewusst NICHT Schritt 1
(Basis-Installation), 13 (`nutzer`-Konto anlegen - bleibt eigener
letzter Schritt, siehe unten) und 16 (ISO bauen) ab.

Schritt 14 (Bluetooth-Kopplungsdaten übernehmen) ist zwar als Funktion
vorhanden, läuft aber NICHT im Standardlauf mit - nur sinnvoll, wenn
dasselbe Testgerät wie vorher wiederverwendet wird (Kopplungsdaten
hängen an der MAC-Adresse des eingebauten Bluetooth-Adapters).

Aufruf (**ohne `sudo`**, siehe unten):
- `./dialos-full-office-setup.sh` - Standardlauf ohne Schritt 14.
- `./dialos-full-office-setup.sh --bluetooth-kopplung` - Standardlauf
  inkl. Schritt 14.
- `./dialos-full-office-setup.sh 08` - nur ein einzelner Schritt, zum
  gezielten Nachholen/Debuggen (funktioniert für jeden Schritt,
  einschließlich 14).

**Nicht mit `sudo` starten** (Riegel eingebaut 2026-08-16): Die Schritte
9 und 10 richten das Benutzerkonto ein (GNOME-Erweiterung,
Standardprogramme, Nautilus-Lesezeichen) und schreiben dafür nach `~` -
unter `sudo` wäre das `/root`, und die Dateien landeten ohne jede
Fehlermeldung im falschen Home. Alles, was Root-Rechte braucht, ruft
`sudo` selbst auf; das Passwort wird zu Beginn einmal abgefragt
(`sudo -v`), damit der Lauf nicht mitten in den Downloads stehen bleibt.

**Noch nicht auf einem frischen System end-to-end getestet** - geplant
für den nächsten kompletten Neuaufbau des T490.

## dialos-set-avatar.sh

Setzt die DialOS-Bildmarke als Profilbild (Avatar) für ein
Benutzerkonto - für "DialOS-Admin" direkt nach der Installation.
Braucht laufenden D-Bus + AccountsService, geht nur auf einem echten,
schon laufenden System (nicht im Chroot-Build).

Aufruf: `sudo ./dialos-set-avatar.sh [benutzername]`
(Standard: `$SUDO_USER`)

## dialos-setup-nutzer.sh

Legt den Standard-Benutzer "nutzer" an (mit zufälligem Sudo-Passwort,
das der Endnutzer nie eingibt) und schaltet den Autologin von einem
Admin-Konto auf "nutzer" um. Autologin läuft über AccountsService, nicht
über `/etc/gdm3/custom.conf` (wird bei dieser Debian-13/GDM-48-Kombi
ignoriert). Enthält Wiederholungslogik gegen einen bekannten
Timing-Bug ("user is locked" direkt nach dem Passwort setzen).

Aufruf: `sudo ./dialos-setup-nutzer.sh [admin-benutzername]`
(Standard: `$SUDO_USER`)

## dialos-claude-setup.sh

Stellt nach einem Reinstall des T490 die Arbeitsumgebung für Claude
Code wieder her: legt die eng begrenzte Sudoers-Regel für
`eggs produce` (ohne Passwortabfrage) neu an, setzt den Symlink
`~/DialOS` auf das Repo der externen Platte neu, und setzt Git-Identität
(`user.name`/`user.email`) + `credential.helper=store` für
`dialosadmin`, damit `git push` nach einem Reinstall nicht mehr an
fehlender Identität scheitert.

Deckt bewusst NICHT ab (Sicherheitsgrenze, kein Bug): die
Claude-Chat-Anmeldung selbst (Login/Zugangsdaten - einfach `claude`
starten und neu einloggen), und das GitHub-Token selbst (`git push`
fragt beim ersten Mal einmalig danach - manuell einzutippen, kein
Skript nimmt Tokens/Passwörter entgegen). Der Connector für die externe
Platte, die GitHub-Integration und der bisherige Chat lassen sich nach
einem Reinstall **gar nicht** wiederherstellen (weder per Skript noch
in der App selbst) - komplette Neueinrichtung, bestätigt von Stephan
am 2026-08-14.

Aufruf: `sudo ./dialos-claude-setup.sh`

## dialos-buero-setup-abschliessen.sh

Sammel-Skript für den letzten Schritt nach einer frischen Installation,
seit 2026-08-16 vier Teilschritte:

1. `dialos-set-avatar.sh` - Profilbild fürs Admin-Konto.
2. **Admin-Werkzeuge auf `dialosadmin`s Arbeitsfläche** (neu 2026-08-16):
   die Skripte aus diesem Ordner, die frisch geladene
   Claude-Desktop-`.deb` und ein klickbares Startsymbol für
   `dialos-install` inklusive `gio set … metadata::trusted true`. Das war
   vorher reine Handarbeit aus der Doku (Schritt 13) und damit die letzte
   Lücke, die den Geräteaufbau davon abhielt, komplett aus Skripten zu
   bestehen. `gio set` läuft per `runuser` als das Admin-Konto, nicht als
   root - das Vertrauens-Merkmal liegt in dessen eigener
   Metadaten-Ablage.
3. `dialos-setup-nutzer.sh` - `nutzer`-Konto + Autologin-Umschaltung.
   Braucht den **noch eingesteckten** Sicherheits-Stick, sonst bricht es
   kontrolliert ab.
4. Prüft, ob die Firefox-Startseite korrekt gesetzt ist (sollte
   automatisch aus der ISO kommen, wird hier nur kontrolliert).

Aufruf: `sudo ./dialos-buero-setup-abschliessen.sh [admin-benutzername]`
(Standard: `$SUDO_USER`)
