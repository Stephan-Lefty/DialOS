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
- **Schritt 16: Penguins' Eggs entfällt, Rescuezilla übernimmt
  (Stephans Entscheidung, 2026-08-16).** Der Anlass war profan: `eggs`
  fehlte auf dem neu aufgebauten Gerät. Es ist nicht in Debians
  Paketquellen, stand in keiner Paketliste, und **wie es installiert
  wird, war nirgends dokumentiert** - weder in der Anleitung noch in der
  Commit-Historie. Dieselbe Sorte Lücke wie bei `check_piper_voice.sh`:
  einmal von Hand gemacht, nie aufgeschrieben, beim Reinstall verloren.
  Weil die ISO seit Weg A ohnehin kein Installationsmedium mehr ist,
  sondern nur noch Sicherungs-Schnappschuss, fiel die Wahl auf
  [Rescuezilla](https://rescuezilla.com/) - die grafische Oberfläche für
  Clonezilla, das in Debian liegt und kein Fremd-Repository braucht.
  Stephan erstellt die Abbilder damit selbst; die Doku hält nur die drei
  Punkte fest, die sich aus dem DialOS-Aufbau ergeben: Clonezilla läuft
  nicht aus dem laufenden System, die **LUKS-Partition darf nicht ins
  Abbild** (Clonezilla kann nicht hineinsehen und kopierte alle ~375 GB
  Byte für Byte statt der ~15 GB belegter Blöcke), und `nutzer`s Daten
  sind damit bewusst nicht enthalten. Mit entfernt wurden alle toten
  Reste: die `splash.png` für den eggs-Bootbereich samt Schritt-3-Block,
  das Verzeichnis `/etc/penguins-eggs.d`, und die Sudoers-Regel aus
  `dialos-claude-setup.sh`, die passwortloses `sudo` für ein nicht mehr
  existierendes `/usr/bin/eggs` gewährte - das Skript entfernt sie jetzt,
  statt sie anzulegen.
- **Aussprache: "DialOS" wird jetzt als "Dial OS" gesprochen (Stephans
  Wunsch, 2026-08-16).** Umgesetzt **zentral** in `dialos-say.py`: Jeder
  Text läuft vor dem Sprechen durch `fuer_sprachausgabe()`. Damit kann
  keine künftige Ansage die Trennung vergessen, und die Texte bleiben im
  Quelltext korrekt geschrieben - der Ansagetext sagt wieder schlicht
  "DialOS". Beim Suchen zeigte sich übrigens, dass es in gesprochenen
  Texten nur **eine** Fundstelle gab; alle anderen Treffer waren Pfade,
  Kommentare und Variablennamen, die nie gesprochen werden. Die Regel
  lässt `dialosadmin` und `dialos.org` unangetastet - beides per Test
  abgesichert. Dabei fiel auf, dass mein Kommentar zur Regel falsch war
  (ein Bindestrich *ist* eine Wortgrenze, `DialOS-System` wird also
  getrennt - richtig so); korrigiert wurde der Kommentar, nicht der Code.
- **Ohne Stick ist `nutzer` jetzt gesperrt, nicht nur ohne Autologin
  (2026-08-16, ausgelöst durch Stephans Frage, ob man sich ohne Stick
  überhaupt anmelden kann).** Der Autologin allein war als Schutz
  unvollständig: Ohne Stick zeigt GDM weiterhin beide Konten, und wer
  `nutzer`s Zufallspasswort kennt - es steht einmalig im Terminal, wenn
  `dialos-setup-nutzer.sh` es würfelt - hätte sich trotzdem anmelden
  können. `/home/nutzer` wäre dabei **nicht** gemountet gewesen, die
  Sitzung wäre also gegen ein Verzeichnis auf der **unverschlüsselten**
  root-Partition gelaufen: im besten Fall an den Rechten gescheitert, im
  schlechtesten mit einem Profil im Klartext. `dialos-stick-gate.sh`
  sperrt das Konto jetzt zusätzlich (`usermod -L`) und entsperrt es
  wieder, sobald der Stick da ist. Die Reihenfolge ist dabei nicht
  beliebig - erst entsperren, dann Autologin setzen, weil
  AccountsService `SetAutomaticLogin` für ein gesperrtes Konto mit "user
  is locked" ablehnt (derselbe Fehler, der am 2026-08-11 schon einmal
  Zeit gekostet hat). `dialosadmin` wird nie gesperrt.
  **Noch am selben Tag auf echter Hardware bewiesen** - nach einem Boot
  ohne Stick greifen fünf Ebenen gleichzeitig: Stick physisch weg,
  LUKS-Container zu (`nvme0n1p4` ist `crypto_LUKS` ohne Mapper),
  `/home/nutzer` kein Einhängepunkt, Konto auf `L`, keine `nutzer`-Sitzung.
  Der verschlüsselte Swap läuft dabei weiter - er nutzt einen pro Start
  neu gewürfelten Schlüssel und hängt nicht am Stick. Genau die
  beabsichtigte Trennung. **Auch die Rückrichtung bestätigt:** Stick
  wieder eingesteckt und neu gestartet - Autologin greift, Konto zurück
  auf `P`, und die Ansage kommt auf den gemerkten 25 % **ohne erneute
  Lautstärke-Frage**. Damit ist auch die zweite Hälfte der neuen
  Lautstärke-Logik belegt: nicht nur "wird gefragt und gemerkt", sondern
  "wird beim nächsten Mal nicht mehr gefragt".
  **Zur Klarstellung, weil die Frage naheliegt:** Das
  Wiederherstellungs-Passwort ist *kein* Anmelde-Passwort. Es ist der
  zweite LUKS-Schlüsselslot und entsperrt nur die Partition von Hand
  (`cryptsetup open`) - für den Notfall "Stick verloren", zusammen mit
  `dialos-rekey`.
- **Lautstärke-Abfrage: einmal fragen statt bei jedem Anmelden - und
  danach statt davor (Stephans Vorgabe, 2026-08-16).** Bisher kam die
  Frage bei jedem Login und noch **vor** der Ansage. Beides war
  ungünstig: Wer als Allererstes "Wie laut soll ich sein?" hört, hat
  keinen Anhaltspunkt, wie laut das System überhaupt ist - für einen
  blinden Nutzer ein sinnloser Maßstab. Jetzt spricht `nutzer`s erste
  Anmeldung zuerst die normale Ansage, fragt danach ("War das angenehm
  laut? Du kannst es einmalig festlegen."), merkt die Antwort in
  `~/.config/dialos/lautstaerke` und bestätigt sie **in der neu gewählten
  Lautstärke** - so ist sofort hörbar, worauf man sich festgelegt hat. Bei
  jedem weiteren Anmelden wird der gemerkte Wert verwendet, ohne erneut zu
  fragen; zum Zurücksetzen genügt das Löschen der Datei. Da `nutzer`s Home
  auf der verschlüsselten Partition liegt, ist die Einstellung genauso
  geschützt wie dessen übrige Daten. **Am selben Tag live bestätigt:**
  Ansage lief, die Frage kam danach, Stephans gesprochene "25" wurde
  erkannt und dauerhaft gemerkt.
  - **"aus" wird bewusst NICHT dauerhaft gespeichert**, sondern gilt nur
    für die laufende Anmeldung. Wäre es dauerhaft, käme keine Ansage mehr -
    und damit auch nie wieder diese Frage. Ein blinder Nutzer hätte ohne
    fremde Hilfe keinen Weg zurück. Ein echter Dauer-Aus-Schalter braucht
    erst einen anderen Rückweg über die Sprachsteuerung.
  - `frage_lautstaerke()` liefert bei jedem Fehlschlag jetzt `None` statt
    `100`. Nur so lässt sich "der Nutzer hat 100 gesagt" (merken) von "wir
    haben nichts verstanden" (nichts merken, nächstes Mal erneut fragen)
    unterscheiden - vorher wäre ein misslungener Erkennungsversuch
    dauerhaft als bewusste Wahl festgeschrieben worden.
- **Erster Neustart nach dem Aufbau: alle vier offenen Prüfungen bestanden
  (2026-08-16).** Per Journal belegt: `systemd-cryptsetup@cryptswap`
  startet und beendet sich sauber (der verschlüsselte Swap kommt also von
  allein hoch - das war das letzte ungetestete Glied), `dialos-stick-gate`
  findet den Stick, mountet die Home-Partition und aktiviert den Autologin,
  und `nutzer` meldet sich daraufhin automatisch an. Nebenbei bestätigt
  sich ein Designdetail: Der Sicherheits-Stick war von `/dev/sda` nach
  `/dev/sdb` gewandert, weil die externe Platte zuerst erkannt wurde - weil
  `dialos-stick-gate.sh` ihn über `blkid -L DIALOS-KEY` am Label sucht
  statt am Gerätepfad, blieb das folgenlos.
- **Preseed-Bereitstellung auf einen Befehl reduziert (2026-08-16).**
  Der Debian-Installer holt die Datei über **einfaches HTTP** - die
  Debian-Doku nennt für `preseed/url` nur `http://` und `tftp://`. Daran
  scheiterten der Reihe nach beide naheliegenden Ablageorte: dialos.org
  läuft auf WordPress und leitet zwingend auf HTTPS um (die Datei liegt
  dort inzwischen korrekt, aber nur über die Umleitung erreichbar), und
  Nextcloud erzwingt HTTPS noch strikter und erzeugt zusätzlich lange
  Token-Adressen, die am Boot-Prompt abzutippen wären. Neues Skript
  `scripts/dialos-preseed-server.sh`: prüft Datei und Port, ermittelt die
  IP-Adresse, gibt die fertige `preseed/url`-Zeile aus und startet den
  Server. Live geprüft - 200, null Umleitungen, byte-identisch mit dem
  Repo. **Der entscheidende Punkt kam von Stephan:** Das Zielgerät wird
  gerade plattgemacht und kann die Datei nicht selbst ausliefern - die
  externe Platte mit dem Repo steckt man während der Installation an
  einen beliebigen zweiten Rechner. Damit hat die Platte einen zweiten
  Zweck neben "übersteht den Reinstall", was jetzt auch im Praxishinweis
  steht. Kein Eingriff in nginx nötig, WordPress bleibt unangetastet.
- **Die Start-Ansage konnte dauerhaft hängen bleiben - und dabei Audio für
  immer stumm schalten (gefunden 2026-08-16 durch Stephans Frage, warum
  das Sprechen-Icon dauerhaft leuchtet).** Von den vier
  `subprocess.run`-Aufrufen in `dialos-say.py` hatten ausgerechnet die
  beiden `spd-say`-Aufrufe **kein Timeout**; alle anderen nutzen
  `timeout=5`. Solange die Sprachausgabe defekt war (fehlendes
  `check_piper_voice.sh`), wartete `spd-say --wait` auf ein Ende-Signal,
  das nie kam - der Prozess stand beim Nachsehen seit **75 Minuten**.
  Der eigentliche Schaden liegt dabei nicht beim Icon: Weil das Skript
  hängt, wird der `finally`-Block **nie** erreicht - und der hebt die fürs
  Audio-Ducking gesetzte Stummschaltung wieder auf. Hätte `nutzer` beim
  Anmelden Radio gehört, wäre es dauerhaft stumm geblieben, ohne
  erkennbaren Grund und ohne dass ein blinder Nutzer sich hätte selbst
  helfen können. Diesmal traf es nur speech-dispatchers eigene Streams,
  die vom Ducking ohnehin ausgenommen sind - Glück, kein Verdienst.
  Behoben: beide Aufrufe laufen über eine Hilfsfunktion mit Zeitgrenze
  (20 s für die Aufwärm-Ansage, 60 s plus Zuschlag nach Textlänge für den
  Text, gedeckelt bei 300 s - für die reale Start-Ansage 102 s bei rund
  40 s Sprechdauer). Der Docstring behauptete bis dahin, die Markierung
  werde "garantiert wieder entfernt, auch bei Fehlern" - das galt für
  Ausnahmen, nicht fürs Hängen.
- **Die Sprechen-Markierung war ein fester Pfad im geteilten `/tmp`.**
  `/tmp/dialos-sprachausgabe-aktiv` teilten sich alle Konten. Live
  beobachtet: `nutzer`s Ansage legte die Datei an, woraufhin auch
  `dialosadmin`s Panel dauerhaft das Sprechen-Icon zeigte, obwohl dort
  nichts sprach. Verschärfend das Sticky-Bit von `/tmp` - `dialosadmin`
  konnte die fremde Datei weder überschreiben noch löschen, und
  `markierung_setzen()` scheiterte still am fehlenden Schreibrecht. Die
  Markierung liegt jetzt unter `$XDG_RUNTIME_DIR` (`/run/user/<uid>`):
  pro Konto privat und beim Abmelden automatisch weg. `dialos-say.py` und
  `dialos-tts-indicator.py` bilden den Pfad mit identischer Logik.
- **Der erste Neustart legte drei Lücken offen - alle nur auf echter
  Hardware sichtbar (2026-08-16).**
  - **Die Sprachausgabe war vollständig stumm, aus zwei unabhängigen
    Gründen.** `piper-generic.conf` beginnt ihre Synthese-Kette mit
    `./check_piper_voice.sh $VOICE && …` - diese Datei existierte
    nirgends: nicht im System, nicht im Repo, nicht in der Doku. Die
    `&&`-Kette brach sofort ab, es wurde **nie ein einziges Audio-Sample
    erzeugt**. Und das ohne jede Fehlermeldung: Das Panel-Icon erschien
    weiterhin, weil `dialos-tts-indicator.py` unabhängig von der Synthese
    läuft - der Fehler sah also nach "läuft, aber leise" aus. Auf dem
    alten Testgerät muss die Datei als manuell angelegter Rest existiert
    haben und ist beim Reinstall verlorengegangen - genau die Lücke, die
    `docs/Debian-zu-DialOS.md` schließen soll. Zweitens fehlte
    `pulseaudio-utils` in der Paketliste: kein `paplay` (Wiedergabe am
    Ende der piper-Kette), kein `parec` (Aufnahme für die
    Lautstärke-Abfrage), kein `pactl` (Audio-Ducking sowie
    Bluetooth-Profilwechsel in `dialos-start-ansage.py`). Auf dem alten
    System war das Paket zufällig vorhanden, deshalb ist es nie
    aufgefallen. **Beides behoben und am selben Tag akustisch bestätigt** -
    vorher Glied für Glied nachgemessen (129.652 Bytes Rohaudio aus
    piper, 41.140-Byte-WAV nach sox bei 22.050 Hz), danach von Stephan
    per `spd-say` gehört.
  - **Die Tastatur stand auf Japanisch (Mozc).** Ursache ist ein
    Widerspruch in der Doku selbst: Schritt 1 sagt "GNOME im
    Debian-Installer wählen" - und genau diese Auswahl installiert
    `task-gnome-desktop`, also das Paket, vor dem Schritt 2 ausdrücklich
    warnt. Über dessen Recommends kamen **138** fremdsprachige
    `task-*`-Pakete samt `ibus-mozc`/`ibus-anthy` herein; beide Konten
    hatten `[('ibus','mozc-jp'), ('xkb','de')]`, Mozc also an erster
    Stelle. Zwei Ebenen der Lösung: neuer Schritt 2b räumt die
    Sprachpakete weg (`task-gnome-desktop` selbst bleibt, es hält den
    Desktop zusammen), und `01-dialos-defaults` setzt die deutsche
    Tastatur jetzt als **einzige** Eingabequelle - als dconf-Standard für
    jedes Konto, auch für künftig angelegte.
  - **Das Aufräumen riss `gnome-accessibility-themes` mit.**
    `apt-get autoremove --purge` entfernt alles, was nach dem Purge
    niemand mehr anfordert, und kennt den Unterschied zwischen einer
    thailändischen Schriftart und einem Kontrastthema nicht -
    ausgerechnet auf einem System für Menschen mit Seheinschränkung.
    Behoben auf zwei Ebenen: Das Paket steht jetzt ausdrücklich in der
    Paketliste, und Schritt 2b setzt die komplette Liste nach dem
    `autoremove` erneut durch. Damit ist alles darin wieder als "manuell
    installiert" markiert und gegen künftiges `autoremove` geschützt -
    nicht nur dieses eine Paket.
- **Partitionierung wird nicht mehr von Hand gemacht: Preseed für den
  Debian-Installer (2026-08-16).** Stephans Wunsch war, bei der
  Erstinstallation nicht über die Plattengröße nachdenken zu müssen.
  Sein erster Gedanke - die ganze Platte nehmen und hinterher per Skript
  auf 100 GiB verkleinern - geht technisch nicht: Ein **eingehängtes**
  ext4-Dateisystem lässt sich nicht schrumpfen, Online-Resize kann
  ausschließlich wachsen. Auf dem laufenden System kann kein Skript die
  root-Partition verkleinern; das ginge nur aus einer Live-Sitzung, mit
  Zusatz-Neustart pro Gerät und dem Risiko, dass ein Abbruch mitten im
  Schrumpfen das System zerstört. Deshalb der umgekehrte Weg: das richtige
  Layout entsteht gleich beim Installieren. Neu:
  `website/d-i/trixie/preseed.cfg` gibt dem Debian-Installer
  EFI + genau 100 GiB root vor und lässt den **kompletten Rest
  unpartitioniert** - unabhängig von der Plattengröße, ohne dass
  irgendwo eine Zahl angepasst werden muss. Die Zielplatte bleibt bewusst
  eine interaktive Frage: das ist die einzige Sicherung dagegen, dass die
  Vorgabe den Installations-Stick oder eine externe Platte trifft. Kein
  Swap im Rezept - den legt Schritt 12 verschlüsselt an. Doku-Schritt 1
  ist dafür in 1a bis 1d gegliedert: Ablageort auf dialos.org, die genaue
  Tastenfolge im Bootmenü (UEFI `e`, BIOS `Tab`), was danach passiert,
  und die Rückfallebene von Hand. **Korrektur am selben Tag:** Zuerst
  stand dort, ein Netzwerkkabel sei zwingend. Das war falsch - die
  Debian-Doku ist eindeutig, dass das Netzwerk konfiguriert wird, *bevor*
  das Preseed geholt wird ("the network must be configured before the
  preseed file can be fetched"). Über WLAN geht es also genauso: Der
  Installer fragt beim Netzwerk-Schritt nach WLAN-Name und Passwort und
  lädt die Datei erst danach. Aus derselben Prüfung stammt eine zweite
  Verbesserung: Der verbreitete Kurzbefehl `auto url=…` entfällt. Der
  Automatik-Modus dient nur dazu, auch Sprache und Tastatur preseeden zu
  können, senkt dabei aber die Fragen-Priorität - und hätte damit
  ausgerechnet die WLAN-Rückfragen unterdrücken können. Jetzt wird die
  Adresse schlicht ausgeschrieben (`preseed/url=…`).
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
