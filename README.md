[Deutsch](README.md) | [English](README.en.md) | [Änderungsprotokoll](#änderungsprotokoll) | [TODO](TODO.md)

<img src="assets/logo.png" alt="DialOS Logo" width="360">

Website: [dialos.org](https://dialos.org)

# DialOS

Ein auf Debian 13 + GNOME 48 basierendes, vollständig sprachgesteuertes
System für Menschen, die einen Computer nur eingeschränkt nutzen können –
insbesondere blinde und motorisch eingeschränkte Personen. Ziel ist ein
fertig eingerichteter Laptop, den der Nutzer allein durch Sprechen
bedienen kann: Radio und Musik hören, Briefe schreiben, im Web suchen,
Mediatheken nutzen, E-Mails schreiben, telefonieren, Videocalls führen –
bis hin zur kompletten Systemwartung.

Fokus liegt zunächst auf dem deutschsprachigen Raum.

Dieses Projekt ist in Zusammenarbeit mit [Claude](https://claude.com) entstanden.

## Status

Konzeptphase – es existiert noch keine lauffähige Software. Dieses
Repository sammelt die bisher getroffenen Architektur- und
Design-Entscheidungen als Grundlage für die Umsetzung.

## Dokumentation

- [Debian-zu-DialOS](docs/Debian-zu-DialOS.md) – Schritt-für-Schritt-Rezept: von einer nackten Debian-13/GNOME-Installation bis zur aktuellen Version
- [Architektur-Übersicht](docs/architektur-uebersicht.md) – Ziel, Zielgruppe, Kernfunktionen, Software-Stack
- [Hardware](docs/hardware.md) – Referenzgerät, Test-Hardware, WWAN-Anforderungen
- [Sicherheit & Datenschutz](docs/sicherheit-datenschutz.md) – Autologin, Verschlüsselung, Fernwartung, Versand
- [Sprachsteuerung](docs/sprachsteuerung.md) – STT/TTS-Stack, Intent-Erkennung, Design-Prinzipien
- [Telefonie & Videocall](docs/telefonie.md) – SIM- und Handy-Anbindung, Fallback-Logik
- [Ersteinrichtung & Rollout](docs/ersteinrichtung.md) – Zwei-Phasen-Provisionierung, Sprachassistent, Datenschutz-Varianten
- [Offene Punkte](docs/offene-punkte.md) – was noch zu klären/entscheiden ist
- [ISO-Builds](docs/iso-builds.md) – Verzeichnis gebauter Images (Version, Commit, Prüfsumme, Nextcloud-Ablageort)

## Logo & Branding

Weitere Varianten liegen in [assets/](assets/): `mark.png` (Bildmarke
allein), `logo-tagline.png` (mit Slogan), `logo-full.png` (mit
Feature-Icon-Zeile), `logo-horizontal-light.png`/`-dark.png` (horizontale
Version für helle/dunkle Hintergründe), `app-icon-light.png`/`-dark.png`
(quadratisches App-Icon) sowie `brand-sheet.png` als vollständige
Referenzübersicht. Dazu `wallpaper-light.png`/`wallpaper-dark.png`
(Desktop-Hintergrund) und `splash.png` (Boot-/Login-Bildschirm).

## Testumgebung

- Lenovo ThinkPad T490 (ohne WWAN-Modul)
- USB-Sicherheits-Stick
- Android-Testgerät für Handy-Anbindung (USB-Tethering + GSConnect)

## Änderungsprotokoll

### 0.5.0
- **Weg A entschieden (Stephan, 2026-08-16): Calamares und
  `dialos-install` ersatzlos entfernt.** Jedes Kundengerät wird im Büro
  aufgesetzt - leere Platte, jeweils aktuelle Debian-13/GNOME-ISO von
  debian.org, dabei `dialosadmin` anlegen, danach die drei DialOS-Skripte.
  Damit bekommt nie jemand außer Stephan einen Installer zu sehen, und
  beide Werkzeuge verlieren ihre Aufgabe. Entfernt: das gesamte
  Calamares-Branding (`branding/dialos`, `locale.conf`,
  `shellprocess.conf`), das Penguins-Eggs-Vendor-Overlay,
  `base.yaml.tmpl`, `install-system.desktop` sowie `dialos-install` samt
  Startsymbol. Doku-Schritt 5 heißt jetzt "Calamares entfernen" und
  räumt Geräte auf, die es noch haben - die Schrittnummer bleibt, damit
  alle Querverweise gültig bleiben. **`dialos-rekey` bleibt**: es ersetzt
  einen verlorenen oder defekten Sicherheits-Stick und ist damit ein
  Wartungswerkzeug, kein Installer; sein Startsymbol tritt an die Stelle
  des bisherigen `dialos-install`-Symbols. `dialos-install`s LUKS-/
  Stick-Logik lebt unverändert in `dialos-setup-home-partition.sh`
  weiter, das daraus abgeleitet wurde. Die ISO (`eggs produce`) dient nur
  noch als Sicherungs-Schnappschuss. Erledigt sich damit auch: der offene
  Punkt zum falschen GeoIP-Standortvorschlag von Calamares.
- **`nutzer` hätte ein Home bekommen, das ihm nicht gehört - gefunden
  beim ersten echten Lauf von Skript 3 (2026-08-16).** `adduser` meldete
  "The home directory `/home/nutzer' already exists. Not touching this
  directory" und ließ daraufhin **beides** bleiben: den `chown` auf das
  neue Konto *und* das Kopieren von `/etc/skel`. Das Home gehörte danach
  `root:root` - `nutzer` hätte sein eigenes Verzeichnis nicht beschreiben
  können, GNOME weder `~/.config` noch `~/.cache` anlegen. Bei einem
  Konto, das per Autologin startet und dessen Nutzer blind ist, wäre das
  ein Totalausfall ohne jede Selbsthilfemöglichkeit gewesen. Ursache ist
  der neue Aufbauweg selbst: `dialos-setup-home-partition.sh` legt die
  verschlüsselte Partition an und mountet sie, *bevor* das Konto
  existiert. `dialos-setup-nutzer.sh` arbeitet das jetzt nach (`/etc/skel`
  kopieren, `chown`, `chmod 700`) - das Kopieren nur, wenn das Home außer
  `lost+found` leer ist, damit vorhandene Daten nie überschrieben werden.
- **Dabei aufgefallen: `/etc/skel` des echten Systems wurde nie
  befüllt.** Die Schritte 9 und 10 kopierten die DialOS-Vorlagen aus dem
  Repo bisher ausschließlich in `dialosadmin`s Home. `nutzer` hätte damit
  weder die Bluetooth-Akku-Erweiterung noch Thunderbird als
  Standard-Mailprogramm noch die Nautilus-Lesezeichen bekommen - obwohl
  die Doku `/etc/skel` ausdrücklich als Weg "für neue Konten automatisch"
  nennt. Beide Schritte legen die Dateien jetzt zusätzlich dort ab;
  Admin-Skripte gehören weiterhin ausdrücklich **nicht** nach `/etc/skel`
  (Korrektur vom 2026-08-14 gilt unverändert).
- **Erster echter End-to-end-Lauf auf dem T490 (2026-08-16) - Skript 1
  und 2 komplett durchgelaufen.** Alle vorher behobenen Fehler wären real
  aufgetreten (der RustDesk-Abhängigkeits-Fallback hat sichtbar
  gegriffen), und die Fixes haben sich im Betrieb bestätigt: die
  Vosk-Modelle liegen erstmals korrekt entpackt (3,2 GB statt der früheren
  doppelt verschachtelten 6,3 GB), die Benutzer-Schritte 9/10 landeten in
  `/home/dialosadmin` statt in `/root`, das Schlüssel-Backup gehört jetzt
  `dialosadmin` mit `600` statt wie beim Lauf vom 14.08. `root` mit `664`,
  und das ext4-Label im LUKS-Container heißt ungekürzt `dialos-nutzer`.
  Ergebnis: `dialos-nutzer-home` mit 374,9 GiB, Stick mit `DIALOS-KEY`
  (2 GiB, ext4) + `DIALOS-DATA` (57,8 GiB, exFAT). Nebenbei bestätigt:
  Claude Code 2.1.233 läuft trotz `EBADENGINE`-Warnung auf Debians
  Node 20 - die Doku-Aussage stimmt weiterhin.
- **Dabei aufgedeckt: `systemd-cryptsetup` fehlte in der Paketliste.**
  Debian 13 hat die Auswertung von `/etc/crypttab` aus dem
  `systemd`-Paket herausgelöst. Ohne dieses Paket existiert weder der
  Generator noch `systemd-cryptsetup@.service` - der Eintrag für den
  verschlüsselten Swap blieb dadurch **völlig wirkungslos, ohne jede
  Fehlermeldung**, und nach dem Lauf war schlicht gar kein Swap aktiv.
  Dass die Home-Partition trotzdem lief, liegt daran, dass
  `dialos-stick-gate.sh` sie selbst per `cryptsetup open` öffnet; deshalb
  fiel das Fehlen nur beim Swap auf. Paket nachgetragen, zusätzlich prüft
  das Skript es jetzt, *bevor* es die Partitionstabelle anfasst. Drei
  weitere Nachbesserungen am selben Code: die neue Swap-Partition wird mit
  `wipefs -a` gesäubert (sie beginnt am Offset der alten, deren
  Swap-Header samt alter UUID sonst stehen blieb), die fstab-Zeile bekommt
  `nofail` (ein blockierter Start wäre auf einem Gerät für blinde Nutzer
  gravierender als ein fehlender Swap), und die Sofort-Aktivierung läuft
  direkt über `cryptsetup open --type plain` statt über `systemctl start`
  auf eine Unit, die vor dem nächsten Boot noch gar nicht existiert.
- **Swap wird jetzt verschlüsselt (8 GiB, Schlüssel pro Start neu) -
  entschieden und umgesetzt 2026-08-16.** Bis dahin lag auf dem T490
  eine 37,3-GiB-Klartext-Swap-Partition. Damit konnten `nutzer`s
  Speicherseiten - offene Dokumente, Mails, Browserinhalte - am
  LUKS-Schutz von `dialos-nutzer-home` vorbei im Klartext auf der Platte
  landen: ohne Sicherheits-Stick lesbar, ebenso nach Ausbau der SSD.
  `dialos-setup-home-partition.sh` ersetzt einen vorgefundenen
  Klartext-Swap jetzt durch 8 GiB über `/etc/crypttab` mit
  `/dev/urandom` als Schlüsselquelle, setzt `vm.swappiness=10` und
  `RESUME=none`, und schlägt den freigewordenen Platz gleich der
  Home-Partition zu (auf dem T490: 345,6 → rund 375 GiB).
  - Der crypttab-Eintrag referenziert bewusst die **PARTUUID**, nicht die
    Dateisystem-UUID: die Option `swap` legt bei jedem Start ein frisches
    Dateisystem an, dessen UUID sich damit ständig ändert.
  - **8 GiB statt "so groß wie das RAM":** Die Faustregel `Swap ≥ RAM`
    existiert nur für den Ruhezustand - und der war bei diesem
    Stick-Gate-Design ohnehin unmöglich, weil das Abbild `nutzer`s
    entschlüsselte Daten enthielte und beim Booten vor allem anderen
    lesbar sein müsste (genau der verworfene
    `cryptsetup-initramfs`-Ansatz). Der Zufallsschlüssel schließt
    Hibernate jetzt endgültig aus; Suspend-to-RAM bleibt unberührt.
  - **Swap ganz weglassen** kam trotz 46 GiB RAM nicht in Frage: ohne
    Swap beendet der OOM-Killer bei Speichermangel Prozesse hart, und ein
    abgeschossener Screenreader bzw. eine abgeschossene Sprachausgabe
    bedeutet für einen blinden Nutzer den völligen Verlust jeder
    Rückmeldung. Die 8 GiB sind das Notpolster dagegen.
- **Zeitzone/Locale entschieden:** Bau- und Referenzgerät bleiben auf
  `Europe/Vienna` + `de_AT.UTF-8` statt des bis dahin dokumentierten
  `Europe/Berlin`. Folge, jetzt in Schritt 1 festgehalten: die beiden
  Kundenwege liefern unterschiedliche Zeitzonen - Calamares setzt
  weiterhin fest Berlin aus `locale.conf`, während `dialos-install` als
  Klon-Werkzeug das laufende System kopiert und damit Wien vererbt.
- **Von Debian 13 zu DialOS in drei Befehlen - Skript-Durchsicht vor dem
  ersten echten Durchlauf (2026-08-16).** `dialos-full-office-setup.sh`
  und `dialos-setup-home-partition.sh` waren bis dahin nur syntaktisch
  geprüft und nie gelaufen. Beim Abgleich gegen
  `docs/Debian-zu-DialOS.md` auf einem frisch installierten T490 kamen
  mehrere Fehler heraus, die den ersten Lauf abgebrochen hätten:
  - `python3-pip` fehlte in der Paketliste (`pip3` ist auf einem frischen
    Debian 13 nicht vorhanden) - Schritt 15 wäre ganz am Ende des Laufs
    gescheitert. Zusammen mit `unzip` nachgetragen, das dort ebenfalls
    fehlte und nur zufällig vorinstalliert war.
  - Schritt 7 rief `npm install -g` ohne `sudo` auf - Debians npm-Prefix
    ist `/usr/local`, das scheitert mit `EACCES` und hätte per `set -e`
    die Schritte 8-15 mitgerissen. Auch in der Doku korrigiert, wo der
    Befehl ebenfalls ohne `sudo` stand.
  - Kein Riegel gegen einen Start mit `sudo`: die Schritte 9 und 10
    richten das Benutzerkonto ein und schreiben nach `~`, unter `sudo`
    wäre das `/root` gewesen - lautlos, ohne Fehlermeldung. Start als
    root wird jetzt abgewiesen; `sudo -v` fragt das Passwort einmal zu
    Beginn ab, statt mitten in den Downloads.
  - `systemctl disable --now rustdesk` ohne `|| true` hätte bei einer
    umbenannten/fehlenden Unit den Rest des Laufs abgebrochen.
  - In `dialos-setup-home-partition.sh` hatte als einzige der vier
    Dialog-Hilfsfunktionen ausgerechnet die Passwortabfrage **keinen**
    Fallback: ohne Grafik (z. B. per `sudo` von einer Textkonsole -
    `sudo` entfernt `DISPLAY` per `env_reset`) beendete sich das Skript
    an dieser Stelle wortlos, weil `VAR=$(zenity …)` unter `set -e`
    abbricht. Jetzt Terminal-Eingabe als Rückfall, begrenzt auf drei
    Versuche. Aus demselben Grund waren die erklärenden Abbruch-Meldungen
    bei der Stick-Auswahl toter Code (`|| true` ergänzt).
  - Die neue Partition wurde als "höchste vorhandene Nummer" bestimmt.
    parted vergibt aber die niedrigste **freie** Nummer - bei einer Lücke
    in der Nummerierung wäre eine bestehende Partition per `luksFormat`
    überschrieben worden. Jetzt Vergleich der Nummern vorher/nachher mit
    Abbruch bei Uneindeutigkeit.
  - Der Speichern-Dialog des Schlüssel-Backups startete in `$HOME`, unter
    `pkexec`/`sudo` also in `/root` statt im Nextcloud-Ordner des
    Admin-Kontos, und die gespeicherte Datei gehörte `root`. Jetzt wird
    das Home des aufrufenden Kontos aufgelöst (`PKEXEC_UID`/`SUDO_UID`)
    und die Datei diesem übereignet.
  - Die Notfall-Passphrase landete unter festem Namen `/tmp/.rp` mit der
    Standard-umask, war also kurz weltlesbar (jetzt `mktemp`, 600).
  - Das ext4-Label `dialos-nutzer-home` ist 18 Zeichen lang, ext4 erlaubt
    16 - `mkfs.ext4` kürzte es stumm auf `dialos-nutzer-ho`. Folgenlos,
    weil zum Auffinden das LUKS2-Label zählt, aber irreführend im
    Protokoll; jetzt `dialos-nutzer`.
  - Die Stick-Auswahl zeigt jetzt eine Spalte "Bisheriger Inhalt" - ein
    eingesteckter Installationsstick war vorher nicht von einem leeren zu
    unterscheiden, obwohl er komplett gelöscht wird.
  - **Letzte Handarbeit beseitigt:** Die Desktop-Bereitstellung aus
    Doku-Schritt 13 (Skripte, Claude-Desktop-`.deb`, Startsymbol für
    `dialos-install` samt `gio set metadata::trusted`) steckte in keinem
    Skript. Sie ist jetzt Teil von `dialos-buero-setup-abschliessen.sh`,
    womit der Geräteaufbau nach der Basis-Installation vollständig aus
    drei Skript-Aufrufen besteht.
  - **Doku-Abgleich Schritt 1:** Die reale Partitionierung des T490
    (100,00-GB-root, 954-MB-ESP, 37,3-GiB-Swap, 345,6 GiB frei) ist jetzt
    als Referenztabelle dokumentiert. Die Swap-Partition fehlte in der
    Anleitung komplett - inklusive der Warnung, dass sie unverschlüsselt
    ist und damit `nutzer`s ausgelagerte Speicherseiten am
    LUKS-Schutz vorbei im Klartext auf der Platte liegen können.
- **`dialos-install`-Bugfix:** Der Datei-Speichern-Dialog für das
  Schlüssel-Backup blieb unter `pkexec` lautlos aus (fehlende
  `DBUS_SESSION_BUS_ADDRESS`/`XDG_RUNTIME_DIR` für den Zugriff auf
  `xdg-desktop-portal`) - `pkexec` reicht die nötigen Umgebungsvariablen
  jetzt durch, echte `zenity`-Fehler werden zusätzlich nicht mehr
  verschluckt. Außerdem: klickbares Desktop-Icon für `dialos-install`
  auf `dialosadmin`s Schreibtisch.
- **Sicherheitsfix Schlüssel-Backup:** `dialos-install` und `dialos-rekey`
  verschlüsselten das Nextcloud-Backup der LUKS-Schlüsseldatei bisher mit
  demselben Wiederherstellungs-Passwort, das auch als zweiter
  LUKS-Schlüssel-Slot dient - wer beides kannte, hätte den Schlüssel ganz
  ohne den physischen Stick entschlüsseln können. Jetzt: eigenes,
  zufällig erzeugtes Backup-Passwort (`openssl rand -base64 32`),
  Passwortübergabe an `openssl` über eine geshredete Temp-Datei statt
  Kommandozeilen-Argument (verhindert Sichtbarkeit in `ps aux`),
  Wiederherstellungs-Passwort braucht jetzt mindestens 12 Zeichen.
- **Sicherheits-Stick partitioniert jetzt in zwei Bereiche:** `DIALOS-KEY`
  (2 GiB, FAT32, wie bisher für die Schlüsseldatei) + `DIALOS-DATA`
  (Rest der Kapazität, ext4, allgemeiner Datenspeicher) - vorher wurde
  die gesamte Stick-Kapazität für die winzige Schlüsseldatei
  "verschwendet". Neue Mindestgrößen-Prüfung (~2,5 GB) verhindert eine
  kaputte/leere Datenpartition bei zu kleinen Sticks. Dabei außerdem
  einen Bug behoben: Die Sicherheits-Stick-Auswahl in `dialos-install`
  blendete (anders als die Zielfestplatten-Auswahl) das aktuelle
  Live-Boot-Medium nicht aus - bei drei angeschlossenen Medien
  (Boot-Stick, Sicherheits-Stick, interne Platte) hätte der Boot-Stick
  fälschlich als Sicherheits-Stick wählbar sein können.
- **Admin-Zugriff dokumentiert und korrigiert:** Erst wurde GNOME
  "Benutzer wechseln" als Weg für parallelen `dialosadmin`-Zugriff neben
  der laufenden `nutzer`-Sitzung dokumentiert. Beim Rekonstruieren der
  Vortags-Session kam aber ein bereits gefundener Bug ans Licht (siehe
  unten): "Benutzer wechseln" lässt `nutzer`s Sitzung im Hintergrund
  aktiv, zwei gleichzeitig laufende `dialos-start-ansage.py`-Instanzen
  konkurrieren dann um Bluetooth/Audio. Korrigierte Praxis: `nutzer`
  richtig abmelden, danach als `dialosadmin` anmelden. Eine
  Boot-Zeit-Tastenkombination für direkten Admin-Zugriff bleibt als
  offene Verbesserungsoption vorgemerkt (`docs/offene-punkte.md`).
- **Bluetooth-Audio-Bug behoben** (`dialos-start-ansage.py`): Nach dem
  Login blieb die Sprachansage über den Bluetooth-Lautsprecher
  intermittierend aus. Ursache: mehrere gleichzeitig laufende
  Skript-Instanzen (durch Kontowechsel ohne echtes Abmelden)
  konkurrierten um Bluetooth-Reconnect und Audio-Stummschaltung. Fix:
  Ein-Instanz-Lock pro Konto (`alte_instanz_beenden()`) sowie ein
  Bluetooth-Debug-Log (`bluetooth_debug_snapshot()`) für künftige
  Fehlersuche ohne manuelles Nachstellen.
- **Spracherkennung (Vosk) technisch zum Laufen gebracht:** Vosk 0.3.45 +
  deutsche Modelle (groß `vosk-model-de-0.21`, 6,3 GB; klein
  `vosk-model-small-de-0.15`, 183 MB) installiert, reines
  Technik-Testskript `dialos-vosk-test.py` (Mikrofon wählen, aufnehmen,
  transkribieren, im Terminal anzeigen - noch ohne Anbindung an
  Intent-Erkennung/TTS). Aufnahme-Modus bewusst "erst vollständig
  aufnehmen, dann erkennen" statt Echtzeit-Streaming, da das große
  Modell laut offizieller Beschreibung für Telefonie/Server gedacht ist,
  nicht Echtzeit auf Laptop-Hardware. Mikrofon-Vergleichstest AIRHUG
  Bluetooth vs. eingebautes Laptop-Mikrofon: Bluetooth klar überlegen (6
  von 8 Testsätzen exakt korrekt bei normaler Sprechlautstärke, gegenüber
  deutlich schwächeren Ergebnissen beim eingebauten Mikrofon) -
  Zielbild: DialOS wird künftig immer mit einem mobilen
  Bluetooth-Lautsprecher/Mikrofon installiert, eingebautes Mikrofon nur
  als (noch nicht implementierter) Fallback.
- **Intent-Erkennung auf [hassil](https://github.com/OHF-Voice/hassil)
  festgelegt** statt des ursprünglich angedachten Rhasspy, das 2026 vom
  Ersteller archiviert wurde und nicht mehr weiterentwickelt wird -
  hassil bietet denselben Beispielsatz-Ansatz, aber als schlanke
  Python-Bibliothek ohne Docker/eigenen Dienst (siehe
  [docs/sprachsteuerung.md](docs/sprachsteuerung.md)).
- Neue Sprachausgabe-Aktiv-Anzeige im GNOME-Panel
  (`dialos-tts-indicator.py`): Icon erscheint während jeder
  Sprachausgabe und verschwindet danach zuverlässig - nützlich, falls
  die Lautstärke zu leise eingestellt ist und eine sehende Person
  trotzdem sehen soll, dass gerade gesprochen wird.
- `dialos-start-ansage.py` weiter verbessert: Zahlwort-Bug behoben
  ("einsundzwanzig" → "einundzwanzig"), Internetstatus/Wetter/Abschluss
  in einem einzigen Sprachausgabe-Aufruf statt mehrerer (verhinderte
  kurze Hintergrundmusik-Einblendungen zwischen den Aufrufen),
  Akku-Ansage nur noch für tatsächlich verbundene Geräte, neue
  Hintergrund-Überwachung meldet Internet-Statuswechsel auch nach der
  Anmeldung, kontobasierter Filter (Kundenkonto `nutzer` bekommt nur
  Laptop + Lautsprecher abgefragt, jedes andere Konto die volle
  Variante mit Maus/Tastatur).
- Netzwerk-Priorität WLAN/Kabel vor SIM umgesetzt und auf dem T490
  verifiziert (NetworkManager-Routenmetriken).
- Zwei ISO-Testbuilds erstellt: `DialOS-Live-0.5.0.iso` (ohne Klonen,
  generischer Live-Nutzer als Sicherheitsnetz) und
  `DialOS-Live-0.5.0-clone.iso` (mit `--clone`, übernimmt `dialosadmin`
  und `nutzer` inkl. Home-Verzeichnissen aus dem echten System - für
  den geplanten Live-Test von `dialos-install` mit dem Sicherheits-Stick
  gedacht).
- Zwei nie gepushte Commits aus einer veralteten lokalen Repo-Kopie
  wiederhergestellt und ins echte Repository nachgezogen (Bluetooth-Fix
  und dessen Dokumentation) - Repository liegt jetzt vollständig auf der
  externen Platte, veraltete Zweitkopie war zwischenzeitlich ungenutzt
  weitergelaufen.
- **Neuer `dialos-stick-gate`-Mechanismus:** Der geplante Live-Test von
  `dialos-install` mit dem Sicherheits-Stick ist am 14.08. gescheitert -
  Grund war kein einzelner Bug, sondern dass der ganze LUKS/initramfs-Weg
  strukturell fehleranfällig ist (Schlüsseldatei muss exakt im richtigen
  Moment im initramfs verfügbar sein, kaum Debugging-Möglichkeiten vor
  Ort bei einem Fehler dort). Als robustere Ergänzung (nicht Ersatz -
  siehe TODO.md) gibt es jetzt einen rein softwarebasierten
  Anwesenheits-Check: `dialos-stick-gate.service` prüft bei jedem Boot
  per `blkid`, ob der Sicherheits-Stick (Label `DIALOS-KEY`) gefunden
  wird, und schaltet darüber `nutzer`s Autologin per AccountsService/
  `gdbus` um - Stick da: Autologin an; Stick fehlt: Autologin aus, GDM
  zeigt den normalen Login-Screen (praktisch nur `dialosadmin` nutzbar).
  Läuft komplett in der normalen Systemumgebung statt im initramfs,
  daher ohne dessen Fallstricke. Ursprünglich als reiner Login-Filter
  gedacht (schützte noch nicht die Daten selbst) - **noch am selben Tag
  weiterentwickelt, siehe nächster Eintrag.**
- **Home-Partition-Verschlüsselung ersetzt Ganze-Platte-LUKS:** Statt
  die ganze Zielfestplatte zu verschlüsseln (der ursprüngliche, am
  initramfs gescheiterte Ansatz), verschlüsselt `dialos-install` jetzt
  nur noch eine eigene `dialos-nutzer-home`-Partition (LUKS2,
  ausschließlich `/home/nutzer`) - root (~100 GiB, ext4) bleibt
  unverschlüsselt und bootet immer normal. `dialos-stick-gate.service`
  öffnet die Home-Partition nach dem Boot (nicht mehr im initramfs) und
  schaltet erst danach `nutzer`s Autologin frei - schützt damit jetzt
  tatsächlich `nutzer`s Daten, nicht nur den Login-Zugriff wie in der
  ersten Version oben. `dialos-rekey` und `scripts/dialos-setup-
  nutzer.sh` (Mount-Prüfung vor `adduser`) entsprechend angepasst,
  toter `dialos-keyscript`-initramfs-Code entfernt. Zusätzlich: Der
  Sicherheits-Stick wird jetzt bewusst **unterschiedlich** formatiert -
  `DIALOS-KEY` (Schlüssel) als **ext4** statt FAT32, damit die
  Schlüsseldatei unter Windows gar nicht erst lesbar ist (und dank
  Unix-Rechten `root:root 755` selbst unter Linux nur für root
  zugreifbar); `DIALOS-DATA` (allgemeiner Speicher) als **exFAT** statt
  ext4, damit `nutzer` sie als normalen mobilen Datenträger unter
  Windows/macOS/Linux nutzen kann - empfohlene Standardgröße 64 GB
  (≈62 GB `DIALOS-DATA` nutzbar). Die Stick-Partitionierung wurde
  manuell gegen einen echten 59,8-GB-USB-Stick verifiziert (Labels,
  Dateisysteme, Rechte-Verhalten wie erwartet); die vollständige
  `dialos-install`-Installation auf echter Hardware steht laut TODO.md
  noch aus. Details:
  [docs/sicherheit-datenschutz.md](docs/sicherheit-datenschutz.md),
  Abschnitt "Verschlüsselung von nutzers Daten + Sicherheits-Stick".
- **Vosk/hassil-Spracherkennung als wiederholbares Rezept dokumentiert:**
  Bisher nur manuell live auf dem T490 installiert (TODO.md) - beim
  Nachprüfen bestätigt sich, dass diese Installation zwischenzeitlich
  tatsächlich verloren gegangen war (`import vosk` schlug fehl), durch
  einen Reinstall des Geräts. `docs/Debian-zu-DialOS.md` (Schritt 15)
  enthält jetzt das vollständige Rezept: System-weite Installation via
  `pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0`
  (Debian 13 blockiert `pip install` ins System-Python sonst per PEP
  668), Download + korrektes Entpacken der deutschen Modelle (groß +
  klein). Dabei einen Entpack-Fehler im ursprünglichen Testlauf gefunden
  und in der neuen Doku vermieden: Die Modell-ZIPs enthalten selbst
  schon einen benannten Ordner - `unzip -d <Zielordner>` erzeugt dadurch
  eine doppelt verschachtelte Struktur, unter der `vosk.Model()` nichts
  findet (funktionierte auf dem T490 nur zufällig, weil `unzip` bei
  Namenskollision zusätzlich flach kopiert - kostet aber unnötig
  Festplattenplatz, gemessen ca. 6,3 GB statt ~3,2 GB beim großen
  Modell). `dialos-vosk-test.py` (interaktives technisches Testskript)
  jetzt ebenfalls im Repo. Ein echter Erkennungstest (tatsächlich
  hineinsprechen) steht laut TODO.md noch aus.
- **Konsolidierungs-Skript + eigenständige Home-Partitionierung:**
  Stephan wollte eine durchgehende Schritt-für-Schritt-Anleitung von
  Debian-Installer-Download bis fertigem DialOS - dabei fiel eine echte
  Lücke auf: die `dialos-nutzer-home`-Partition + der Sicherheits-Stick
  ließen sich bisher nur über `dialos-install` einrichten, das dabei
  zusätzlich die ganze Zielfestplatte löscht und das System per rsync
  draufkopiert - für einen normalen Debian-Installer-Aufbau falsch.
  Neu: `scripts/dialos-full-office-setup.sh` führt die Schritte 2-12 +
  15 aus `Debian-zu-DialOS.md` automatisiert aus (eine Funktion pro
  Doku-Schritt, auch einzeln aufrufbar; Schritt 14, Bluetooth-
  Kopplungsdaten, ist als Funktion enthalten, läuft aber nur mit
  `--bluetooth-kopplung` mit, da gerätespezifisch);
  `dialos-setup-home-partition.sh`
  übernimmt `dialos-install`s LUKS/Stick-Logik unverändert, aber ohne
  den Festplatten-Wipe - nutzt stattdessen freien Platz am Ende der
  System-Platte. Dafür muss bei der Basis-Installation (Schritt 1)
  bewusst Platz nach der 100-GB-root-Partition frei gelassen werden -
  jetzt in `Debian-zu-DialOS.md` dokumentiert. Beide neuen Skripte sind
  bisher nur syntaktisch geprüft, noch nicht real getestet - geplant für
  den nächsten kompletten T490-Neuaufbau (siehe TODO.md).
- **Wetter-Standort auf GeoClue2 umgestellt:** Auslöser war ein
  konkreter Live-Fund - `dialos-start-ansage.py` fragte bisher `wttr.in`
  ohne Ortsangabe ab, das rät den Standort selbst per IP; auf Stephans
  Netzwerk zeigte das Wien statt seines echten Standorts (Seefeld in
  Tirol). Ein fest im Skript hinterlegter Ort schied als Lösung aus, da
  das Gerät auch unterwegs genutzt werden soll. Jetzt fragt
  `dialos-start-ansage.py` den Standort per GeoClue2 ab (System-Bus,
  nutzt automatisch die beste verfügbare Quelle - WLAN-Abgleich über
  Mozilla Location Service, sonst IP-Schätzung als Fallback) und übergibt
  die Koordinaten direkt an `wttr.in`. Dabei live am echten Standort
  getestet und einen wichtigen Effekt gefunden: Auch GeoClue2 fällt ohne
  WLAN-Treffer in der Mozilla-Datenbank auf eine grobe IP-Schätzung
  zurück ("ipf fallback", ~25-26 km Ungenauigkeit, real ~300 km daneben)
  - deshalb neuer Genauigkeits-Schwellwert (Fixes ungenauer als 10 km
  werden verworfen), Wetteransage wird dann bewusst ausgelassen statt
  eine falsche Stadt/Region zu nennen (genau wie bei fehlendem Internet
  oder fehlenden Bluetooth-Geräten - lieber nichts sagen als etwas
  Falsches). Bewusster Trade-off: in Gegenden mit dünner
  WLAN-Datenbank-Abdeckung (z. B. ländliche Regionen) kann die
  Wetteransage dadurch öfter fehlen als vorher. Voraussetzung: App in
  `/etc/geoclue/geoclue.conf` freischalten +
  `org.gnome.system.location enabled=true` (jetzt in
  `01-dialos-defaults`), sonst `AccessDenied` - beides live gefunden und
  in `scripts/dialos-full-office-setup.sh`/`Debian-zu-DialOS.md`
  nachgezogen. Nebenbei: die Wetteransage nennt jetzt auch den erkannten
  Ort ("Das Wetter in Seefeld in Tirol wird heute so sein.").
- **Lautstärke-Abfrage bei der Start-Ansage:** Neuer Wunsch von Stephan
  - `dialos-start-ansage.py` fragt `nutzer` jetzt am Anfang der Ansage
  per Sprache "Wie laut soll ich sein? Sage 100, 75, 50, 25 oder aus.",
  nimmt 4 Sekunden auf (Bluetooth-Mikrofon bevorzugt, mit demselben
  `headset-head-unit`-Profilwechsel wie in `dialos-vosk-test.py`) und
  erkennt die Antwort mit dem kleinen deutschen Vosk-Modell - die
  **erste echte Vosk-Nutzung im laufenden Betrieb** (vorher nur das
  technische Testskript). Ergebnis steuert Speech-Dispatchers eigene
  Lautstärke (`spd-say -i`, neuer `--lautstaerke`-Parameter in
  `dialos-say.py`) für den Rest der Ansage; bei "aus" wird nur die
  Frage selbst gesprochen, der Rest komplett ausgelassen. Nur für
  `nutzer` - `dialosadmin` & Co. werden nie gefragt. Bei jedem
  Fehlschlag (nichts verstanden, Vosk fehlt, kein Mikrofon) fällt die
  Funktion auf 100 % zurück, damit die Ansage nie wegen dieser
  Zusatzfrage ausbleibt oder hängen bleibt. Die Erkennungs-/
  Zuordnungslogik wurde verifiziert, indem Piper alle fünf Optionen
  synthetisch aussprach und Vosk sie korrekt erkannte. **Update
  2026-08-16, echter Test mit Stephans Stimme:** Dabei einen echten Bug
  gefunden und behoben - beim ersten Versuch fehlte ein klares
  Startsignal, wann genau das 4-Sekunden-Aufnahmefenster beginnt,
  Stephans gesprochene Antwort ("25") wurde verpasst, nur der
  100 %-Sicherheits-Fallback kam an. Fix: direkt vor der Aufnahme sagt
  die Funktion jetzt zusätzlich "Und jetzt bitte." - danach im zweiten
  Versuch korrekt erkannt (echtes gesprochenes "25" → 25 %, über das
  Bluetooth-Mikrofon inkl. Profilwechsel).

### 0.4.0
- Evolution und GNOME Kalender aus App-Grid und Suche entfernt (nur
  Thunderbird soll für E-Mail und Kalender genutzt werden): `apt purge`
  ist bei beiden nicht möglich, da `evolution-data-server` bzw.
  `gnome-calendar` fest an die Metapakete `gnome`/`gnome-core`/
  `task-gnome-desktop` gekoppelt sind (ein Entfernungsversuch hätte fast
  den kompletten GNOME-Desktop mitgerissen - vorher per
  `apt-get -s purge` simuliert und rechtzeitig abgebrochen). Stattdessen
  Override-Dateien mit `NoDisplay=true` unter
  `/usr/local/share/applications/org.gnome.Evolution.desktop` bzw.
  `.../org.gnome.Calendar.desktop` angelegt - `/usr/local` wird von
  `apt`/`dpkg` nie angefasst, die Änderung übersteht also künftige
  Debian-Updates.
- Thunderbird als tatsächlicher Standard für E-Mail-Links (`mailto:`)
  und Kalendereinträge (`text/calendar`) gesetzt (`xdg-mime`), inklusive
  deutschem Sprachpaket (`thunderbird-l10n-de`, das - anders als bei
  Firefox und LibreOffice - nicht automatisch über `task-german-desktop`
  mitinstalliert wird). Beides über `/etc/skel/.config/mimeapps.list`
  und die ISO-Paketliste (`desktop.list.chroot`) für jedes künftige
  Konto (DialOS-Admin wie nutzer) hinterlegt.
- Calamares entfernt sich künftig automatisch nach der Installation vom
  fertig installierten Zielsystem (neuer Schritt im
  `shellprocess`-Nachinstallationsmodul) - wird auf dem Zielsystem nicht
  mehr gebraucht. Wichtig dabei: Der Schritt läuft ausschließlich im
  chroot des NEUEN Systems, nicht auf der Live-Vorlage, von der aus
  künftige ISOs gebaut werden - sonst hätte die nächste ISO gar keinen
  Installer mehr enthalten. Noch nicht über eine echte Installation
  verifiziert.
- Bluetooth-Kopplungsdaten für die drei Standard-Peripheriegeräte dieses
  Testgeräts (Maus "Pebble M350s", Tastatur "Pebble K380s", externer
  Lautsprecher/Mikrofon "AIRHUG 01") fest ins Image aufgenommen
  (`/var/lib/bluetooth/<Adapter-MAC>/...`), damit nach einer
  Neuinstallation auf diesem Laptop keine erneute Kopplung nötig ist
  (funktioniert, weil der eingebaute Bluetooth-Adapter des Laptops
  gleich bleibt). Dabei eine unverankerte `.gitignore`-Regel (`cache/`)
  gefunden und korrigiert, die versehentlich auch echte Systemordner
  wie `var/cache/...` in der ISO-Vorlage gefiltert hätte.
- Akkustand-Anzeige in der oberen Leiste eingerichtet: GNOME-Erweiterung
  "Bluetooth Battery Monitor" zeigt Laptop- und Bluetooth-Geräte-Akku
  (liest die Werte über `upower`/UPower aus), Akku-Prozentanzeige
  aktiviert. Erweiterung und Einstellung systemweit als Standard für
  alle künftigen Konten hinterlegt
  (`/etc/skel/.local/share/gnome-shell/extensions/`,
  `/etc/dconf/db/local.d/01-dialos-defaults`).
- Neue Sprachansage beim Anmelden ("Michael", der persönliche
  Assistent, `/usr/local/bin/dialos-start-ansage.py`): begrüßt, nennt
  Datum und Uhrzeit, liest die Akkustände von Laptop, Maus, Tastatur und
  Lautsprecher vor, meldet bei Internetverbindung das Tageswetter
  (Morgens/Mittags/Nachmittags/Abends, inkl. Regenschirm-Hinweis bei
  Regenwahrscheinlichkeit, Standort wird automatisch per IP erkannt) und
  verabschiedet sich. Verbindet dabei automatisch alle gekoppelten
  Bluetooth-Geräte neu (behebt ein Problem, bei dem der
  Bluetooth-Lautsprecher nach einer Ab-/Anmeldung nicht selbstständig
  wiederverbunden wurde) und schaltet über ein wiederverwendbares
  Sprachausgabe-Skript mit Audio-Ducking (`/usr/local/bin/dialos-say.py`)
  andere Audioquellen für die Dauer der Ansage stumm. Läuft automatisch
  bei jedem Login für alle Konten
  (`/etc/xdg/autostart/dialos-start-ansage.desktop`).
- Änderungsprotokoll in dieser Datei in die richtige (neueste zuerst)
  Reihenfolge sortiert.

### 0.3.0
- Login-Avatar für "DialOS-Admin" gesetzt: das schon vorhandene
  Buero-Setup-Skript `scripts/dialos-set-avatar.sh` tatsaechlich
  ausgefuehrt (setzt die DialOS-Bildmarke per AccountsService/D-Bus als
  Profilbild) - vorher nur geschrieben, aber nie angewendet.
- Autologin-Kette repariert und verifiziert: Standard-Benutzer "nutzer"
  angelegt, Autologin laeuft korrekt ueber AccountsService (nicht ueber
  das dafuer ignorierte `/etc/gdm3/custom.conf`), Admin-Konto behaelt
  kein Autologin. Dabei einen Timing-Bug in
  `scripts/dialos-setup-nutzer.sh` gefunden ("user is locked" direkt
  nach `chpasswd`, weil AccountsService die neue Passwort-Zeile noch
  nicht bemerkt hatte) und mit Wiederholungslogik behoben (auch in der
  ISO-Vorlage unter `iso-build/config/includes.chroot/etc/skel/Desktop/`
  nachgezogen).
- Neuer fester Sammelordner `~/Dokumente/DialOS/` auf dem Testgeraet für
  alle Dateien, die nach einer Installation für die Einrichtung
  gebraucht werden - als erstes Werkzeug liegt dort
  `nutzer-anlegen.sh` (robustere Kopie des Autologin-Skripts) sowie ein
  Angaben-Formular für die Thunderbird-Kontoeinrichtung
  (`thunderbird-angaben-formular.md`).
- Firefox: Startseite per Enterprise-Policy auf `https://dialos.org`
  gesetzt (`policies.json` unter
  `usr/lib/firefox-esr/distribution/` im ISO-Rezept - der alternative
  `/etc/firefox-esr/`-Pfad wird von diesem Debian-Paket nicht
  unterstuetzt).
- Versuch, ein DialOS-Wallpaper als Hintergrund der "Neuer Tab"-Seite zu
  hinterlegen, zurueckgestellt: Firefox respektiert `browser.newtab.url`
  in aktuellen Versionen nicht mehr zuverlaessig (fuehrt nur zu einer
  leeren Seite), eine eigene Erweiterung dafuer waere mit
  Signatur-Aufwand verbunden und wurde bewusst nicht umgesetzt.

### 0.2.0
- Erste Live-Boot-Installationstests auf realer Hardware (Lenovo T490)
  durchgeführt und iterativ ausgewertet; ISO-Build-Workflow mit
  Penguins' Eggs eingerichtet (Rezept unter `iso-build/config/`, Build-
  und Testzyklus in CLAUDE.md dokumentiert).
- Kosmetik-Fixes für den Installer erarbeitet und per Live-Boot-Test
  bestätigt: NTP-Client (`systemd-timesyncd`) ergänzt, Partitionen-
  Fenster vergrößert (800×580 → 1000×700), Calamares-Assistent zeigt
  jetzt durchgängig DialOS-Branding statt der Penguins'-Eggs-
  Standardoptik (Vendor-Overlay unter
  `/etc/penguins-eggs.d/brain.d/assets/calamares/`), das Live-
  Installer-Icon im App-Grid heißt jetzt "DialOS installieren" mit
  eigenem Icon statt "Install System" mit Ei-Icon, und während der
  Installation läuft kein Pinguin-Werbematerial mehr.
- Live-Dash-Favoriten angepasst: statt des generischen "Debian
  installieren"-Icons erscheint dort jetzt das DialOS-Icon.
- Zentrale Erkenntnis dabei: `iso-build/config/includes.chroot/...` ist
  nur eine Vorlage im Git-Repo - Änderungen müssen vor jedem
  `eggs produce` manuell aufs echte System kopiert werden, sonst landen
  sie nicht im gebauten Image (Details in CLAUDE.md).
- Bekannte, bewusst zurückgestellte Einschränkung: Die Standort-Seite im
  Installer schlägt GeoIP-basiert manchmal einen falschen Ort vor (z. B.
  Rome statt Berlin) - kein Vendor-Override dafür gefunden, unkritisch
  bei Zwei-Phasen-Provisionierung.
- Git-Repository und ISO-Ausgabeordner liegen jetzt auf einer externen
  Festplatte statt nur lokal auf dem T490, damit sie einen erneuten
  Reinstall des Testrechners überstehen.

### 0.1.0
- Projekt gestartet: Anforderungen, Architektur- und Design-Entscheidungen
  aus der Konzeptphase dokumentiert.
