[Deutsch](TODO.md) | [English](TODO.en.md) | [Änderungsprotokoll](README.md#änderungsprotokoll)

# TODO

Laufende Liste offener Kleinigkeiten und nächster Schritte, die Stephan
oder Claude im Arbeitsalltag auffallen. Anders als
[Offene Punkte](docs/offene-punkte.md) (grundsätzliche, noch nicht
entschiedene Architekturfragen) sind das hier konkrete, abhakbare
Aufgaben. Erledigte Punkte werden mit einem Häkchen markiert, nicht
gelöscht - so bleibt nachvollziehbar, was schon erledigt ist.

- [x] Lautstärke-Abfrage bei der Start-Ansage (nur `nutzer`, 100/75/50/
  25 Prozent/aus) umgesetzt - erledigt 2026-08-14, siehe
  docs/Debian-zu-DialOS.md Schritt 11. Erste echte Vosk-Nutzung im
  Betrieb, Erkennungslogik mit Piper-synthetisierten Testwörtern
  verifiziert (alle fünf Optionen korrekt erkannt).
- [x] Echten Test der Lautstärke-Abfrage mit tatsächlich gesprochener
  Antwort durchgeführt (über das Bluetooth-Mikrofon, inkl.
  `headset-head-unit`-Profilwechsel) - erledigt 2026-08-16. Dabei einen
  echten Bug gefunden und behoben: Beim ersten Versuch fehlte ein
  klares Startsignal, wann genau das 4-Sekunden-Aufnahmefenster
  beginnt - Stephans gesprochene Antwort ("25") wurde verpasst, nur der
  100 %-Sicherheits-Fallback kam an. Fix: `dialos-start-ansage.py`
  sagt jetzt direkt vor der Aufnahme zusätzlich "Und jetzt bitte." -
  danach im zweiten Versuch korrekt erkannt (echtes "25" → 25 %).
- [x] Wetter-Standort auf GeoClue2 umgestellt statt IP-geraten - erledigt
  2026-08-14, ausführlich live getestet (siehe README-Änderungsprotokoll
  0.5.0 und docs/Debian-zu-DialOS.md, Schritt 11, für Details). Auslöser:
  `wttr.in`s eigene IP-Standorterkennung zeigte Wien statt Stephans
  echtem Standort (Seefeld in Tirol) - ein fest hinterlegter Ort schied
  aus, da das Gerät auch unterwegs genutzt wird. Live-Erkenntnis dabei:
  GeoClue2 fällt in Gegenden mit dünner Mozilla-WLAN-Datenbank-Abdeckung
  ebenfalls auf eine grobe IP-Schätzung zurück ("ipf fallback",
  ~25-26 km ungenau, real ~300 km daneben) - deshalb Genauigkeits-
  Schwellwert (>10 km wird verworfen) eingebaut, Wetteransage wird dann
  bewusst ausgelassen statt eine falsche Stadt/Region zu nennen. Kann
  dadurch in ländlichen Gegenden öfter fehlen als vorher - gewollter
  Trade-off.
- [ ] `docs/hardware.md` fehlt noch: ob der finale Referenz-Bluetooth-
  Lautsprecher/-Mikrofon Deutsch als Ansage-Sprache unterstützt (eigene
  Firmware-Ansagen des Geräts wie "verbunden"/Akku-Warnung, nicht
  DialOS selbst) - Bluetooth-Standardprofile (A2DP/HFP) bieten dafür
  keine Fernsteuerung, rein geräte-/herstellerabhängig. Bei der Auswahl
  der Referenz-Hardware als Kriterium berücksichtigen.
- [ ] **Nächster Schritt:** T490 komplett neu aufsetzen und dabei den
  kompletten neuen Ablauf real testen (noch nie end-to-end
  durchgelaufen): Debian 13 + GNOME manuell installieren (Schritt 1,
  **mit** dem seit 2026-08-14 dokumentierten Partitionierungs-Hinweis -
  100 GB root, Rest der Platte bewusst frei lassen) →
  `scripts/dialos-full-office-setup.sh` (Schritte 2-12 + 15
  automatisiert) → neues `dialos-setup-home-partition.sh`
  (`dialos-nutzer-home`-Partition + Sicherheits-Stick auf dem
  freigelassenen Platz einrichten, ersetzt für diesen Ablauf
  `dialos-install`s Ganze-System-Kopie) →
  `scripts/dialos-buero-setup-abschliessen.sh` (`nutzer` anlegen).
  Danach wie von Stephan geplant: darauf aufbauend Spracherkennung/
  Sprachbefehle Schritt für Schritt auf echter Hardware ausarbeiten und
  die Installationsroutine weiter erweitern.
- [x] Konsolidierungs-Skript `scripts/dialos-full-office-setup.sh` +
  neues `dialos-setup-home-partition.sh` (führt `dialos-install`s LUKS/
  Stick-Logik auf einem bereits installierten System aus, ohne dessen
  Festplatten-Wipe/rsync-Kopie) erstellt, `Debian-zu-DialOS.md`/`.en.md`
  entsprechend aktualisiert (Schritt 1: Partitionierungs-Hinweis;
  Schritt 12: neues Werkzeug) - erledigt 2026-08-14, beide Skripte nur
  syntaktisch geprüft (`bash -n`), noch nicht real gelaufen (siehe
  Punkt oben).
- [ ] **Zurückgestellt, nicht mehr nächster Schritt** (siehe die zwei
  neuen Punkte unten): Echten Live-Boot-Test mit
  `DialOS-Live-0.5.0-clone.iso` erneut durchführen: erster Versuch am
  2026-08-14 ist bei `dialos-install` gescheitert, zwei Bugs im Skript
  gefunden und behoben (siehe
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
- [ ] **Neuer nächster Schritt:** komplette `dialos-install`-Installation
  mit dem neuen Home-Partition-Design auf echter Hardware (T490)
  durchspielen (siehe docs/sicherheit-datenschutz.md, Abschnitt
  "Verschlüsselung von nutzers Daten + Sicherheits-Stick", für das
  vollständige Design). Prüfpunkte: root-Partition ~100 GiB
  unverschlüsselt bootet normal; `dialos-nutzer-home` (LUKS2) wird beim
  Büro-Setup korrekt angelegt; `dialos-setup-nutzer.sh` bricht ohne
  gestecktem Stick kontrolliert ab statt `nutzer`s Home auf root
  anzulegen; nach Abschluss: Stick abziehen + neu starten → normaler
  GDM-Login-Screen, `/home/nutzer` leer/nicht gemountet; Stick wieder
  einstecken + neu starten → `/home/nutzer` gemountet, Autologin greift.
  Zusätzlich `DIALOS-KEY` (jetzt ext4, nicht mehr FAT32) und
  `DIALOS-DATA` (jetzt exFAT, nicht mehr ext4) auf einem 64-GB-Stick
  verifizieren. **Teilweise bereits erledigt (2026-08-14):** Die reine
  Stick-Partitionierung wurde manuell (nicht über `dialos-install`
  selbst, sondern per Hand mit denselben Befehlen) gegen einen echten
  59,8-GB-USB-Stick getestet - `DIALOS-KEY` (ext4, root:root 755, für
  normale Nutzer weder less- noch schreibbar - stärkerer Schutz als
  geplant) und `DIALOS-DATA` (exFAT, für den aktuellen Nutzer beschreib-
  bar) wurden korrekt angelegt. **Noch offen:** `DIALOS-DATA` an einem
  echten Windows-Rechner einbinden und beschreiben testen (nur
  Linux-seitig verifiziert bisher).
- [x] Grundsatzentscheidung getroffen (siehe oben, umgesetzt
  2026-08-14): Ganze-Platte-LUKS-Verschlüsselung ist komplett entfallen,
  ersetzt durch eine reine `dialos-nutzer-home`-Partition + das
  `dialos-stick-gate`-Gate. `dialos-install`/`dialos-rekey`/
  `dialos-stick-gate.sh` entsprechend umgeschrieben, tote
  `dialos-keyscript`-initramfs-Dateien entfernt.
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
- [x] Vosk (0.3.45) + hassil (3.11.0) + deutsche Vosk-Modelle (groß/klein)
  als wiederholbares Rezept dokumentiert - erledigt 2026-08-14 (siehe
  docs/Debian-zu-DialOS.md, Schritt 15). Dabei bestätigt: Die
  ursprüngliche Live-Installation war zwischenzeitlich tatsächlich
  wieder verschwunden (`import vosk` schlug beim Nachprüfen fehl) - ein
  zwischenzeitlicher Reinstall des T490 hatte sie gelöscht, genau die
  hier befürchtete Falle. `dialos-vosk-test.py` jetzt im Repo unter
  `iso-build/config/includes.chroot/usr/local/bin/`. Außerdem gefunden:
  Die Modell-Ordner auf dem T490 (`/usr/local/share/vosk-model-de-big`
  und `-small`) enthalten wegen eines Entpack-Fehlers beim ursprünglichen
  Testlauf doppelt verschachtelte Kopien der Modelldateien (unnötiger
  Festplattenplatz, gemessen ca. 6,3 GB statt ~3,2 GB beim großen
  Modell) - die
  neue Doku vermeidet den Fehler, die vorhandenen doppelten Daten auf
  dem T490 selbst sind aber noch nicht aufgeräumt.
- [x] `pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0`
  auf dem T490 ausgeführt und verifiziert (2026-08-14) - `import vosk`/
  `hassil` funktioniert, `vosk.Model()` lädt das kleine deutsche Modell
  erfolgreich.
- [ ] Echten End-to-End-Test von `dialos-vosk-test.py` durchführen
  (tatsächlich reinsprechen, Erkennungsqualität beurteilen) - bisher nur
  Installation + Modell-Laden technisch verifiziert, noch kein echter
  Spracherkennungs-Test mit einer gesprochenen Aufnahme gelaufen.
- [x] Erster Eintrag in `docs/iso-builds.md` erfolgt: `eggs produce
  --clone` am 16.08. gelaufen (21/21 Schritte fehlerfrei, 6,50 GiB),
  `DialOS-Live-0.5.1-clone.iso` als Backup-Snapshot vor dem geplanten
  End-to-end-Test (siehe nächster Punkt) - Version/Datum/Commit/SHA256
  eingetragen.
- [ ] `DialOS-Live-0.5.1-clone.iso` liegt bisher nur lokal
  (`~/DialOS-Live-0.5.1-clone.iso`) - noch in die Nextcloud hochladen
  (kann nur Stephan selbst machen, kein Claude-Zugriff darauf).
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
