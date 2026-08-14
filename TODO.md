[Deutsch](TODO.md) | [English](TODO.en.md) | [Änderungsprotokoll](README.md#änderungsprotokoll)

# TODO

Laufende Liste offener Kleinigkeiten und nächster Schritte, die Stephan
oder Claude im Arbeitsalltag auffallen. Anders als
[Offene Punkte](docs/offene-punkte.md) (grundsätzliche, noch nicht
entschiedene Architekturfragen) sind das hier konkrete, abhakbare
Aufgaben. Erledigte Punkte werden mit einem Häkchen markiert, nicht
gelöscht - so bleibt nachvollziehbar, was schon erledigt ist.

- [ ] Echten Live-Boot-Test mit `DialOS-Live-0.5.0-clone.iso` erneut
  durchführen: erster Versuch am 2026-08-14 ist bei `dialos-install`
  gescheitert, zwei Bugs im Skript gefunden und behoben (siehe
  Commit-Historie): 1) Sicherheits-Stick wurde vor der `cryptsetup
  open`-Nutzung der Schlüsseldatei ausgehängt, 2) Datei-Speichern-Dialog
  für das Schlüssel-Backup blieb unter `pkexec` lautlos aus (fehlende
  `DBUS_SESSION_BUS_ADDRESS`/`XDG_RUNTIME_DIR` für den
  xdg-desktop-portal-Zugriff). **Wichtig vor dem nächsten Versuch:** Die
  gepatchte `dialos-install` liegt bisher nur im Git-Repo - sie muss
  zusätzlich auf das aktuell laufende System kopiert werden UND eine neue
  ISO mit `eggs produce` gebaut werden, sonst testet der nächste
  Live-Boot wieder die alte, fehlerhafte Version (siehe "Root Cause
  des 'nichts hat sich verändert'-Tests", 2026-08-11, in der
  Commit-Historie). Danach wie ursprünglich geplant: vor `dialos-install`
  per `gdbus` prüfen, ob `dialosadmin`/`nutzer` mit korrektem
  Autologin-Status mitgekommen sind (siehe docs/sicherheit-
  datenschutz.md, Abschnitt "Automatische Anmeldung"); `dialos-install`
  mit dem Sicherheits-Stick komplett durchspielen - externe
  SanDisk-Extreme-Platte vorher abstecken (sonst als Zielfestplatte
  wählbar!); neue Stick-Partitionierung (`DIALOS-KEY` 2 GiB +
  `DIALOS-DATA` ext4) verifizieren.
- [ ] Calamares-Standort-Seite schlägt beim Live-Boot GeoIP-basiert oft
  einen falschen Standort vor (z. B. Rome statt Berlin) - kein
  dokumentierter Vendor-Override für `modules/locale.conf` gefunden (nur
  Branding ist offiziell überschreibbar). Bleibt vorerst
  Werkzeug-Einschränkung; installierende Person muss Standort beim
  Durchklicken manuell prüfen/korrigieren (unkritisch bei
  Zwei-Phasen-Provisionierung, da Endkunden den Installer nie sehen).
- [ ] Sprechgeschwindigkeit der Piper-Stimme sollte vom Nutzer individuell
  einstellbar sein (aktuell fest über `GenericRateMultiply` in der
  Piper-Config verdrahtet, `0.85` als Stephans persönliche Präferenz
  gewählt) - braucht eine echte Einstellmöglichkeit (z. B. GNOME-
  Barrierefreiheitseinstellungen oder eigener Sprachbefehl), nicht nur
  einen Config-Wert.
- [ ] Vosk (0.3.45) + hassil (3.11.0) + deutsche Vosk-Modelle (groß/klein)
  sind bisher nur live auf dem T490 installiert (pip, manuell
  heruntergeladene Modelle unter `/usr/local/share/`), noch nicht als
  wiederholbares Rezept/Doku festgehalten - gleiche Falle wie früher bei
  Piper, bevor es systemweit verankert wurde. `dialos-vosk-test.py` liegt
  ebenfalls noch nicht im Repo (nur unter `/usr/local/bin/` auf dem
  Testgerät).
- [ ] Bluetooth-Audio-Fix in `dialos-start-ansage.py`
  (Ein-Instanz-Lock/`alte_instanz_beenden()`) ist noch nicht über einen
  längeren Zeitraum endgültig bestätigt - `/tmp/dialos-bluetooth-debug.log`
  bei einem erneuten Auftreten des Problems prüfen.
- [ ] Veraltete lokale Repo-Zweitkopie unter `~/DialOS-repo` löschen oder
  bewusst als Backup behalten (Entscheidung noch offen) - der Symlink
  `~/DialOS` ist jetzt tatsächlich korrekt gesetzt (siehe "Erledigt"
  unten), aber die Zweitkopie selbst liegt noch da. Zwei unabhängige
  Kopien nebeneinander sind fehleranfällig - genau dadurch sind zwei nie
  gepushte Commits vom 13.08. am 14.08. fast verloren gegangen.
- [ ] `/home/eggs/*.iso`-Restdateien der letzten Builds aufräumen
  (gehören `root`, die `eggs produce`-NOPASSWD-Regel deckt nur
  `eggs produce` selbst ab, nicht `rm` - braucht Stephans manuelles
  `sudo rm`).

## Erledigt (zur Nachvollziehbarkeit)

- [x] Live-Desktop-Icon für die Installation (`.desktop`-Datei mit
  eigenem DialOS-Icon statt "Install System"/Ei-Icon auf dem
  Live-Boot-Desktop) - erledigt 2026-08-10 (Branding via
  skel-Überschreibung).
- [x] Neuen ISO-Build mit allen gesammelten Fixes (Bootscreen,
  Avatar-Skript, Calamares-Branding, Piper-TTS) erstellen - erledigt
  2026-08-10/11 (ISO vom 11.08.).
- [x] `scripts/dialos-claude-setup.sh` erweitert (Git-Identität +
  `credential.helper=store` für `dialosadmin`) und tatsächlich
  ausgeführt/verifiziert - erledigt 2026-08-14. `~/DialOS`-Symlink jetzt
  bestätigt vorhanden (per `readlink -f`, zeigt korrekt auf
  `.../SanDisk-Extreme/DialOS/repo`), Sudoers-Regel war schon vorhanden,
  Git-Identität + `credential.helper` per `git config --global`
  bestätigt. (Der vorherige "erledigt"-Eintrag hierzu war falsch - das
  Skript war nie erfolgreich mit `sudo` durchgelaufen, siehe
  Commit-Historie.)
- [x] AppIndicator-Pakete für `dialos-tts-indicator.py`
  (`gnome-shell-extension-appindicator`, `gir1.2-ayatanaappindicator3-0.1`)
  in der Paketliste verankert - erledigt 2026-08-14, dabei zusätzlich
  `gnome-shell-extension-desktop-icons-ng` (DING) ergänzt: GNOME zeigt
  seit Jahren keine Desktop-Icons mehr von Haus aus, ohne diese
  Erweiterung wären die Büro-Setup-Skripte auf `dialosadmin`s
  Arbeitsfläche (siehe unten) unsichtbar geblieben.
