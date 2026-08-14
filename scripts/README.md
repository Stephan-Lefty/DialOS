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
`eggs produce` (ohne Passwortabfrage) neu an und setzt den Symlink
`~/DialOS` auf das Repo der externen Platte neu. Deckt bewusst NICHT
die Claude-Anmeldung selbst ab (Login/Zugangsdaten) - dafür einfach
`claude` starten und neu einloggen.

Aufruf: `sudo ./dialos-claude-setup.sh`

## dialos-buero-setup-abschliessen.sh

Sammel-Skript für den letzten Schritt nach einer frischen Installation:
ruft `dialos-set-avatar.sh` und `dialos-setup-nutzer.sh` nacheinander
auf und prüft zusätzlich, ob die Firefox-Startseite korrekt gesetzt ist
(sollte automatisch aus der ISO kommen, wird hier nur kontrolliert).

Aufruf: `sudo ./dialos-buero-setup-abschliessen.sh [admin-benutzername]`
(Standard: `$SUDO_USER`)
