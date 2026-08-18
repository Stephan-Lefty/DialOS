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

## Aktueller Stand (Stand: 2026-08-18)

**Neu am Abend des 2026-08-16: DialOS hat seinen ersten echten
Sprachbefehl.** `dialos-sprachbefehl-desktop.py` laeuft dauerhaft mit
(erster stets lauschender Dienst des Projekts) und schaltet auf
"auf Linux umschalten" / "auf Windows umschalten" die Desktop-Optik
zwischen GNOME-Standard und einem Windows-11-Nachbau um
(`dialos-desktop-stil.sh`, drei Debian-Erweiterungen: dash-to-panel,
arc-menu, tiling-assistant). Live mit Stephans Stimme bestaetigt.
Hintergrund: Es gibt Interessenten, die DialOS wegen der Sprachsteuerung
wollen, aber aus der Windows-Welt kommen - GNOME bleibt dabei
unangetastet, es kommt nur etwas obendrauf.

**Drei Erkenntnisse daraus, die ueber diese eine Funktion hinausgehen:**

1. **Eingeschraenkte Vosk-Grammatik ist Pflicht, nicht Kuer.** Frei
   erkannt macht das deutsche Modell aus "gnome" zuverlaessig "genug".
   Mit einer auf die Befehlssaetze beschraenkten Grammatik lag alles
   woertlich richtig. Bewaehrte Pruefmethode dafuer: Piper spricht den
   Satz, Vosk hoert zu - ohne dass jemand ins Mikrofon sprechen muss.
2. **Befehle sind ganze Saetze, keine Einzelwoerter** (Stephans
   Vorgabe). Ein beilaeufiges "windows" im Gespraech wuerde sonst den
   Schreibtisch umstellen. Der Stoersatz "ich habe frueher windows
   benutzt" wurde als "auf auf windows" erkannt - mit dem Zielwort, aber
   ohne "umschalten", und loeste damit nichts aus.
3. **Mikrofon-Pegel sind ein Sicherheitsthema, kein Feinschliff.** Das
   eingebaute Mikrofon des T490 war ab Werk um 60 dB uebersteuert
   (Capture +30 dB UND Internal Mic Boost +30 dB). Vosk erkennt Sprache
   an den Pausen zwischen Woertern; in einem Dauervollausschlag gibt es
   keine, also kam nie ein Ergebnis - ohne Fehlermeldung. Behoben und
   per `dialos-mikrofon-pegel.service` bei jedem Start abgesichert.
   **Folge:** Der Mikrofon-Vergleich vom 2026-08-13 ("eingebaut deutlich
   schlechter als AIRHUG") hat womoeglich nur die Uebersteuerung
   gemessen und gehoert wiederholt (TODO.md).

Dazu zwei Paketfehler in Debians `gnome-shell-extension-arc-menu` (65-2),
beide live gefunden und im Rezept umgangen: Das GSettings-Schema liegt
unter `/usr/share/glib-2/schemas/` statt `/usr/share/glib-2.0/schemas/`
(landet nie im systemweiten Cache), und die fertige deutsche `de.mo`
liegt in `po/` statt in einem `locale`-Ordner (Menue bleibt sonst
englisch).

Der ursprüngliche Zwei-Wege-Versuch ist entschieden, kein "neuer Plan"
mehr, sondern der etablierte Ansatz:

1. **Docker/live-build-Pipeline** (`iso-build/`, `iso-build/build.sh`):
   verworfen nach ca. 18 Build-Versuchen ohne je eine fertige `.iso`
   gesehen zu haben (verschachteltes `live-build` in Docker in Claudes
   eigener Sandbox-Umgebung - praktisch jeder Bug ging darauf zurück).
   Bleibt nur noch als Referenz/Fallback. Die frühere Cubic-Anleitung
   (`iso-build/CUBIC-ANLEITUNG.md`) ist am 2026-08-16 gelöscht worden -
   sie beschrieb den Live-ISO-Bau mit `dialos-install`,
   `dialos-keyscript`, initramfs-Hook und Autologin über
   `/etc/gdm3/custom.conf`. Nichts davon existiert oder funktioniert
   noch; sie hätte beim Nachbauen aktiv in die Irre geführt. Bei Bedarf
   über die Git-Historie erreichbar.
2. **Etablierter Ansatz:** Debian 13 + GNOME wird direkt auf echter
   Zielhardware (Lenovo ThinkPad T490) installiert und interaktiv
   konfiguriert - die `iso-build/`-Dateien dienen dabei nur noch als
   Vorlage/Rezept (siehe [docs/Debian-zu-DialOS.md](docs/Debian-zu-DialOS.md)
   für das vollständige, aktuell gehaltene Schritt-für-Schritt-Rezept).
   Vom fertig eingerichteten System zieht Stephan anschließend ein
   Sicherungs-Abbild mit **[Rescuezilla](https://rescuezilla.com/)**
   (seit 2026-08-16; Penguins' Eggs ist entfallen, siehe Schritt 16).

**Aktuelle Version: 0.5.1** (in Arbeit seit 2026-08-17). 0.5.0 ist mit
dem Sprachbefehl für die Desktop-Umschaltung abgeschlossen. Alle Details
im [README.md-Änderungsprotokoll](README.md#änderungsprotokoll).

> **Dauerregel (Stephan, 2026-08-17):** Neue Änderungsprotokoll-Einträge
> kommen unter die **oberste Versionsnummer** - derzeit `### 0.5.1` -
> **bis Stephan ausdrücklich eine andere ansagt.** Nicht selbst eine neue
> Nummer erfinden, weil viel dazugekommen ist, und nicht auf eine
> abgeschlossene zurückfallen. Sagt Stephan eine neue Nummer an: neuen
> Abschnitt oben anlegen, diese Zeile hier auf die neue Nummer ändern,
> danach dort weiterschreiben.

Von den alten ISOs sind am 2026-08-16 acht gelöscht worden (~59 GB);
übrig ist nur `DialOS-Live-0.5.1-clone.iso`, bis Stephans erstes
Rescuezilla-Abbild existiert - siehe `docs/iso-builds.md`.

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
README-Änderungsprotokoll 0.5.0. **Am 2026-08-16 dann erstmals
end-to-end auf dem frisch aufgebauten T490 durchgelaufen** - alle drei
Skripte, anschließend Neustart mit und ohne Sicherheits-Stick, beide
Richtungen per Journal belegt. Offen bleibt die Sprachsteuerung selbst
(siehe TODO.md).
**Entfallen am 2026-08-16 (Weg A):** `dialos-install` (Zielplatte
löschen, System per rsync klonen, GRUB setzen) und der komplette
Calamares-Unterbau - Branding, `locale.conf`, `shellprocess.conf`, das
Penguins-Eggs-Overlay und `base.yaml.tmpl`. Beide existierten nur für den
Live-Boot-Installationsweg, den es nicht mehr gibt. `dialos-install`s
LUKS-/Stick-Logik lebt unverändert in `dialos-setup-home-partition.sh`
weiter, das daraus abgeleitet wurde. **`dialos-rekey` bleibt** - es
ersetzt einen verlorenen oder defekten Sicherheits-Stick und ist damit
ein Wartungswerkzeug, kein Installer. Die ISO dient nur noch als
Sicherungs-Schnappschuss (seit 2026-08-16 als Rescuezilla-Abbild).

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

**Audio-Festlegung seit 2026-08-17 (Stephan):** Eingabe ist **immer** das
eingebaute Mikrofon, Ausgabe der Bluetooth-Lautsprecher solange er
wirklich abspielt, sonst die eingebauten Lautsprecher - mit Ansage beim
Wechsel waehrend der Sitzung, ohne Ansage beim Anmelden. Externe
Mikrofone kommen erst zum Schluss wieder dran. Das ist keine
Zwischenloesung, sondern loest zwei Probleme mit: Solange DialOS kein
Bluetooth-Mikrofon oeffnet, kann das Geraet nicht in HFP rutschen, und
ein eingebautes Mikrofon kann nicht ausgeschaltet werden - beides hat am
2026-08-17 Ausfaelle verursacht. Umgesetzt in
`dialos-ton-ausgabe.py` und `dialos-sprachbefehl-desktop.py`, beschrieben
in `docs/Debian-zu-DialOS.md` Schritt 11f/11g.

**Regel aus demselben Tag, die weit ueber Audio hinausgeht:** Keiner
Zustandsmeldung glauben, wenn sich das Ergebnis messen laesst. An einem
Tag dreimal derselbe Fehler: BlueZ meldete ein verbundenes Geraet, das 0
Bytes lieferte; eine Senke meldete `RUNNING` und spielte nie ab; und
mein eigener Dienst schwieg, weil er sich auf die Vorgabe-Senke des
Systems statt auf seine eigene letzte Wahl verliess. Deshalb prueft
DialOS Ausgabegeraete jetzt, indem es 150 ms Stille hinschickt und
schaut, ob der Aufruf durchlaeuft.

**Welches Programm für welchen Zweck steht in
[docs/anwendungen.md](docs/anwendungen.md)** (festgelegt mit Stephan am
2026-08-18, als der Block „Anwendungen" begann). Dort steht auch das
Auswahlkriterium, und das ist nicht Bedienbarkeit, sondern
**Steuerbarkeit von außen**: Ein Programm ohne Kommandozeile oder D-Bus
ist für DialOS wertlos, weil der Nutzer den Bildschirm nicht sieht -
daran ist `gnome-podcasts` gescheitert, obwohl es installiert ist. Bei
jeder neuen Anwendung gehört diese Datei mit aktualisiert.

**Alle Sprachbefehle stehen in
[docs/sprachbefehle.md](docs/sprachbefehle.md)** (Stephans Wunsch vom
2026-08-17): eine Tabelle Befehl → Aktion, getrennt nach umgesetzt und
vorgesehen. Dort stehen auch die Regeln, die jeder neue Befehl einhalten
muss - jede davon stammt aus einem Fehler, der schon aufgetreten ist.
Bei jedem neuen Sprachbefehl gehört diese Datei mit aktualisiert.

Konkrete offene Aufgaben stehen ausschließlich in [TODO.md](TODO.md),
nicht hier - so bleibt der Stand an einer einzigen Stelle aktuell.

## Offene Entscheidungen (siehe auch [docs/offene-punkte.md](docs/offene-punkte.md))

- Sudo-Rechte für den Standard-Benutzer "nutzer" (Platzhalter-Passwort
  aktuell zufällig generiert, echte Policy für die spätere
  sprachgesteuerte Wartung noch offen).
- Referenz-Hardware final festlegen: Bluetooth-Lautsprecher ist seit
  2026-08-16 entschieden (AIRHUG 01), Laptop und Sicherheits-Stick noch
  offen (siehe `docs/hardware.md`). **Beim Mikrofon ist die Frage seit
  2026-08-17 vertagt, nicht offen:** Eingabe ist immer das eingebaute
  Mikrofon, ein externes Funkmikrofon wird erst zum Schluss wieder
  betrachtet. Der Ausgabe-Fallback auf die eingebauten Lautsprecher ist
  belegt und läuft jetzt über `dialos-ton-ausgabe.py`.
- Rechtschreibprüfung: **`hunspell-de-de` und `aspell-de` sind entgegen
  einer früheren Notiz installiert** (geprüft 2026-08-18). Offen ist nur
  noch die Einbindung in die Anwendungen. Achtung: hunspell akzeptiert
  „vertrag" und „Vertrag" gleichermaßen, taugt also NICHT zur
  Groß-/Kleinschreibung im Diktat - siehe `docs/diktat.md`.
- Mikrofon-Vergleich eingebaut gegen AIRHUG wiederholen, nachdem die
  60-dB-Übersteuerung behoben ist. **Nicht mehr dringend seit der
  Audio-Festlegung vom 2026-08-17** - die Bluetooth-Priorität beim
  Mikrofon ist damit ohnehin entfallen. Interessant bleibt der Vergleich
  für die spätere Entscheidung über ein externes Mikrofon.

## Aktueller Block: die Anwendungen (seit 2026-08-18)

Bis zum 2026-08-17 ging es um die Grundlagen - Sprachausgabe,
Spracherkennung, Audio-Wege, Desktop-Optik. Seit dem 2026-08-18 läuft der
Anwendungsblock.

**Der Umfang ist entschieden und steht in
[docs/anwendungen.md](docs/anwendungen.md)**, die konkreten Aufgaben in
[TODO.md](TODO.md). Nicht neu sammeln - beides ist vollständig.

Sinnvolle Reihenfolge, und der erste Punkt ist kein Zufall: **Diktat und
Vorlesen zuerst.** Sie sind keine Anwendungen, sondern Voraussetzungen für
vier der freigegebenen - Briefe, Notizen, Mail und Chat kann der Nutzer
ohne Diktat gar nicht erzeugen. `vosk-model-de-big` (3,2 GB) liegt schon
auf der Platte; zu bauen ist der Wechsel zwischen eingeschränkter
Befehlsgrammatik und freier Erkennung.

**Nicht anfangen mit:** Telefonie (nach hinten gestellt, hängt an der
Hardware-Entscheidung), Chat (WhatsApp priorisiert, Bestätigung fehlt),
Videoaufnahme (Zweck ungeklärt).

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
