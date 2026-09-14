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

**GitHub-Repo:** https://github.com/Stephan-Lefty/DialOS - **ÖFFENTLICH.**
Hier stand bis zum 2026-08-24 „(privat)", und das war falsch: Anonym
abgefragt meldet die GitHub-API `private: False`. Aufgefallen ist es, als
Stephan seine Anschrift und Telefonnummer für die zentralen Kundendaten
durchgegeben hat - ein Commit hätte sie veröffentlicht. **Keine
personenbezogenen Werte ins Repo**, nur Vorlagen mit leeren Feldern (siehe
[docs/kundendaten-felder.md](docs/kundendaten-felder.md) und
`Wordpressinstallation/.env.example`). Bereits öffentlich und nicht mehr
rückholbar: `stephan.roesner@protonmail.com` in
`scripts/dialos-claude-setup.sh` sowie vier Autoradressen in der
Commit-Historie.

> **Dauerregel (Stephan, 2026-08-24):** „Meine persönlichen Daten, die bereits
> im Repo sind, die können dort bleiben. Bei allen neuen Daten, einfach
> fragen." Also: nichts nachträglich entfernen und keine Historie umschreiben —
> aber **jedes neue personenbezogene Datum vor dem Commit erfragen**, auch wenn
> Stephan es selbst im Gespräch genannt hat. Ein Wert im Chat ist nicht
> dasselbe wie ein Wert auf GitHub, und er hat den Unterschied ausdrücklich
> gezogen.

## Die DialOS-Familie (Regel seit 2026-08-24)

Stephan führt nach und nach mehrere Programme und Apps zusammen, die
Sprachsteuerung nutzen. Aktuell gehören dazu:

| Projekt | Was es ist | Engine | Lizenz |
|---|---|---|---|
| **DialOS** | die Live-ISO selbst | Vosk | GPL-3.0 |
| **DialOS-Mobil** | DialOS auf dem Handy, gleiche Zielgruppe | Vosk | Apache-2.0 |
| **Denkzettel** | Sprachnotizbuch für Debian/Arch, freie Rede | whisper.cpp | MIT |

**Neue Familienmitglieder werden NICHT umbenannt.** Die Frage stand am
2026-08-24 im Raum („aus Denkzettel ein DialOS-Denkzettel machen, passend
zu DialOS-Mobil") und wurde bewusst verneint: Die Familie wächst über
Zugehörigkeit, nicht über Namenspräfixe. Jedes Programm behält seinen
eigenen, kurzen Namen - auch weil er als Sprachbefehl taugen muss
(„Denkzettel öffnen" schlägt „DialOS-Denkzettel öffnen"), und weil der
Name in Konfigurationspfaden, Datenverzeichnissen, `.desktop`-Dateien und
damit an registrierten Tastenkürzeln hängt.

DialOS-Mobil trägt das Präfix zu Recht, weil es **dasselbe Produkt auf
anderer Hardware** ist. Ein Programm mit anderer Engine, anderer
Zielgruppe oder anderer Lizenz bekommt es nicht - sonst behauptet der
Name eine Zusammengehörigkeit, die technisch und rechtlich nicht besteht.

Stattdessen macht ein neues Familienmitglied fünf Dinge:

1. Symbol vom DialOS-App-Icon ableiten, aber klar unterscheidbar
   (Vorbild: `Denkzettel/assets/icon-bauen.py`)
2. GitHub-Beschreibung mit „Aus der DialOS-Familie:" beginnen
3. GitHub-Topic `dialos` setzen
4. Im `.desktop`-Eintrag `GenericName` mit dem Zusatz „DialOS-Familie"
5. Im README die Zugehörigkeit **und** die bewussten Unterschiede nennen

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

## Aktueller Stand (Stand: 2026-09-14)

**Wo das Projekt am 2026-09-14 steht.** Der ausfuehrliche Verlauf steht im
Aenderungsprotokoll in `README.md` unter 0.5.1; hier nur die Lage.

**ZWISCHEN DEM 2026-08-24 UND DEM 2026-09-14 LAG EINE PAUSE VON DREI WOCHEN.**
Am Geraet wurde in dieser Zeit nichts geaendert; Stephan hat am 25.08. sowie am
05. und 09.09. an der WordPress-Seite und an der Foerderrecherche gearbeitet
(siehe TODO.md). Wer hier weiterliest, sollte wissen: Die Lage unten ist der
Stand vom 24.08. plus das, was der 14.09. dazu ergeben hat - nicht drei Wochen
Entwicklung.

**AM 2026-09-14 HAT EIN GESPRAECH IM RAUM DIALOS BEDIENT** (11:01-11:31,
Stephans Pause): Sprachsteuerung sechsmal selbst eingeschaltet, ein Brief-
und ein Einkaufszettel-Diktat aus dem Gespraech, Archiv-PDF, viermal Drucken
(zweimal das mitgeschriebene Gespraech). Aufgeraeumt, Einzelheiten und die
vier Schwachstellen im obersten TODO-Punkt. Bis das geloest ist, gilt: Die
Sprachsteuerung ist gegen Gespraeche in der Naehe NICHT sicher.

**Laeuft und ist belegt:**

- Sprachsteuerung mit 27 Grammatiksaetzen (seit 2026-09-14 auch "bildschirmfoto aufnehmen"). Das Einschalten verlangt beide
  Woerter ("Sprachsteuerung starten") - im Betrieb gemessen: 60
  Beinahe-Treffer. **Die Zahl "null Fehlstarts" ist ueberholt:** Am 2026-08-24
  um 14:41:12 hat sich die Sprachsteuerung selbst eingeschaltet, per Journal
  belegt (ein gnome-terminal "DialOS - Mitschrift" wurde wirklich gestartet).
  Stephan hatte an dem Tag kein Wort zu ihr gesagt, DialOS selbst sprach nicht
  (dialos-say.log leer), und auf die Frage nach Umgebungssprache: nein. Also
  hat ein GERAEUSCH einen ganzen Satz ergeben. Ursache offen.
- **Am Abend des 2026-08-24 liess sich die Sprachsteuerung umgekehrt gar nicht
  mehr einschalten** - dreizehn Versuche, im Protokoll nur 'starten' und
  'sprachsteuerung'. Mein Verdacht war ein zu hoher Aufnahmepegel. **Am
  2026-09-14 nicht mehr nachstellbar:** Stephan hat zweimal "Sprachsteuerung
  starten" gesprochen, beide Male kam der ganze Satz - bei zurueckgesetztem
  Pegel und mit Spitzen (27663, 15257) im selben Bereich wie an dem Abend, an
  dem es NICHT ging. Der Pegel ist damit als Ursache so gut wie aus dem
  Rennen. Nicht geloest, sondern nicht mehr beobachtbar.
- Anna (`de_DE-kerstin-low`) ist Auslieferungsstimme, **Tempo 0,95**, und
  spricht den Nutzer mit Namen an ("Steffan"). Beide Werte hat Stephan mit den
  Ohren entschieden.
- Diktat in Notizen und Einkaufszettel, Schreibhilfe ueber LanguageTool.
- Fusszeile in jeder Thunderbird-Mail, mit anklickbarem Verweis. Die
  Textquelle ist `/usr/local/share/dialos/fusszeile.txt` und nur die.
- Akkuwarnung bei 25/15/5 %, Ansagen von Stephan abgenommen.
- Kein Standby am Netz, keine Bildschirmsperre fuer `nutzer`.
- Unattended-upgrades, Protokoll-Aufbewahrung sieben Tage.
- **Update-Automatik (2026-09-14):** alle 14 Tage montags nach dem Anmelden,
  zehn Sekunden Widerspruch auf "nicht jetzt" ("spaeter fehlt im Wortschatz" war
  ein Pruefehler, siehe unten),
  `apt-get upgrade` ohne autoremove, Neustart nur mit Stick (Pruefung im
  root-Teil) und nur nach einem echten Update seit dem letzten Start (Marke
  unter /run - schliesst Neustart-Schleifen und fremde Neustarts im root-Teil
  aus). Echter Lauf belegt. Der Satz "auf dem neuesten Stand" kam zuerst
  nur beim ausloesenden Konto - jetzt Zeitstempel unter /var/lib/dialos und
  Quittung pro Person; der Beweis ueber zwei Konten am Geraet kommt mit dem
  naechsten echten Update. **sudoers-Regel dialos-systemupdate von Stephan
  am 2026-09-14 freigegeben** (Pruefsumme Geraet = Repo), nicht mehr in NIEMALS.
  Doku: Schritt 13d.
- **Bildschirmfoto auf Zuruf** ueber das XDG-Portal (die GNOME-Schnittstelle
  ist gesperrt, Werkzeuge sind keine installiert). Das Mitschrift-Fenster wird
  vorher geschlossen. **Ging vom 21.08. bis 14.09. nur, weil der Sprachdienst
  in Claudes Sitzung lief** und Claudes Portal-Freigabe erbte; seit 2026-09-14
  traegt das Skript die Freigabe fuer DialOS-Kennungen selbst ein.
- **Drucken per Sprache** fuer Brief, Zettel und Notizen - **auf Papier
  belegt am 2026-08-22**. Der Drucker wird gesucht, nicht vorausgesetzt (CUPS
  hat kein Standardziel), und Papier und Ausrichtung stehen ausdruecklich im
  Auftrag: `-o media=A4 -o orientation-requested=3`.
- **PDF-Archiv an zwei Orten:** `~/Dokumente/Archiv/DialOS-DATA/` auf der
  Platte und `DialOS-Archiv/` auf dem Stick `DIALOS-DATA`, mit Nachholen,
  sobald der Stick steckt. Eigener PDF-Erzeuger ueber cairo, weil der
  Briefbogen mit Leerzeichen gesetzt ist.
- **Mail-Archiv** aus Thunderbirds lokalen mbox-Dateien - ein- und ausgehend,
  ohne Zugangsdaten. Dedup ueber Message-IDs, Entwuerfe ausgenommen.
- **Alle Programmprotokolle liegen in `~/.log/`**, nicht mehr offen im
  Heimatverzeichnis. Der Punkt am Anfang macht den Ordner unsichtbar; er darf
  geloescht werden, jedes Skript legt ihn neu an.
- **Zwei Tastenkombinationen fuers Admin-Konto:** `Strg`+`Alt`+`W` schaltet
  die Optik Linux/Windows um, `Strg`+`Alt`+`S` die Stimme Michael/Anna
  (gemessen 4,4 s bis zur Ansage in der neuen Stimme). NUR fuer
  `dialosadmin` - das Nutzerkonto bedient beides ueber die Stimme.
- **`/usr/local/sbin/dialos-aufspielen`** spielt den Repo-Stand auf, mit enger
  sudoers-Regel. NUR fuer das Entwicklungsgeraet - die Regel ist praktisch ein
  Root-Zugang, Begruendung im Kopf des Skripts.
- **Alle 69 Ansagen** liegen in beiden Stimmen unter
  `docs/sprachbeispiele/alle-ansagen/`. Diese Sammlung hat an einem Tag ZWEI
  Fehler sichtbar gemacht, die kein Test gefunden haette: eine falsche
  Abtastrate (16 kHz als 22050 deklariert, alle Hoerproben 38 % zu schnell)
  und ein "Die Notizen wird gedruckt".
- **Vorstellungsdialog** (Anna fragt, Michael antwortet, 3,5 Minuten) unter
  `docs/video/dialos-vorstellung.ogg`, erzeugt von
  `scripts/dialos-vorstellung.py`.

**Ausserdem neu am 2026-08-24:**

- **Ein stummer `paplay` machte das Geraet lautlos - ohne Fehlermeldung.**
  PipeWire merkt sich Stummschaltung JE ANWENDUNG, dauerhaft. Da DialOS die
  zwischengespeicherten Ansagen, den Frageton und den Testton ueber paplay
  abspielt, waren alle gespeicherten Ansagen stumm - bei Rueckgabewert 0, also
  ohne dass aus_speicher() auf spd-say zurueckgefallen waere. Zwei Ursachen,
  beide behoben: dialos-say.py schaltete fremde Stroeme stumm und gab sie im
  "finally" frei - das laeuft bei SIGTERM NICHT -, und bei zwei Ansagen kurz
  hintereinander schaltete die zweite den paplay der ersten stumm.
- **Alle Protokolle tragen ein Datum** (`%m-%d %H:%M:%S`). Vorher nur die
  Uhrzeit - und logrotate dreht nur bei laufendem Geraet, also lagen drei Tage
  in einer Datei. Ich habe daraus einen Vorfall rekonstruiert, den es an dem Tag
  nie gab; aufgefallen ist es nur, weil Stephan sagte, er habe gar nicht mit dem
  Geraet gesprochen.
- **Jede Ansage steht im Protokoll** (`~/.log/dialos-say.log`), auf 120 Zeichen
  gekuerzt - das ist eine Datenschutz-Entscheidung, kein Platzsparen: Bei einem
  Vorlese-Befehl waere die Ansage das ganze Dokument.
- **Der Pegel steht bei jeder Erkennung im Protokoll.** Gemessen: Vosk baut aus
  etwas, das LEISER als Stille ist, ganze Befehlswoerter - 'sprachsteuerung' bei
  Pegel 30 mit Konfidenz 1,000 - und ist sich dabei SICHERER als im lauten Fall.
  Damit ist die Konfidenz als Filter erledigt, bevor sie gebaut wurde.
- **Kein Stick beim Admin-Konto.** Dort ist der Plattenordner das Archiv. Vorher
  meldete es alle 16 Minuten einen nicht beschreibbaren Stick: exFAT gehoert dem
  Konto, das es einhaengt.
- **Die Stimmwahl wird beim Aufspielen nicht mehr ueberschrieben.**
  piper-generic.conf enthaelt Konfiguration UND die gewaehlte Stimme; sie steht
  jetzt in der Ausschlussliste von dialos-aufspielen, und das Skript MELDET, was
  es uebergangen hat.
- **Brief-Vorlage zum Einsprechen** unter `docs/brief-vorlage.md` - Zielbild,
  was DialOS davon heute kann, und der Diktattext Wort fuer Wort.
- **Feldstruktur der Kundendaten** unter `docs/kundendaten-felder.md` - die
  FELDER, nicht die Werte.

**Drei Befunde vom 2026-08-24, die vorher niemand kannte:**

1. **Die Kundendaten liegen unverschluesselt.**
   `/usr/local/share/dialos/nutzer-name.txt` steht mit 0644 auf der
   unverschluesselten Wurzelpartition, waehrend `/home/nutzer` LUKS ist. Bei
   einem gestohlenen Laptop ist genau das lesbar, was die Person identifiziert.
   Der Umzug ist moeglich - die Startreihenfolge steht ihm NICHT entgegen, das
   war ein Irrtum von mir und ist berichtigt.
2. **Das Repo ist OEFFENTLICH**, nicht privat wie hier lange behauptet.
   Aufgefallen, als Stephan seine Anschrift fuer die Kundendaten durchgegeben
   hat - ein Commit haette sie veroeffentlicht. Siehe die Dauerregel oben.
3. **Der erste Fehlstart** (siehe die Liste oben).

**Am 2026-09-14 entschieden:** "Tas tatur" und "Ei Di" bleiben auch bei Anna -
beide im echten Satz vorgespielt, Urteil "mit Regel". Damit ist die Aussprache
fuer beide Stimmen vollstaendig, und die zwei Regeln brauchen KEIN
Stimmen-Feld.

**Der Brief - fast fertig.** Der ganze Weg steht: "Brief schreiben" nimmt auf,
gesprochene Satzzeichen ("Komma setzen", "neuer Absatz") werden umgesetzt, der
Text landet als Briefbogen nach DIN 5008 in `~/Dokumente/brief.txt` mit Datum,
Unterschriftshinweis und Fusszeile, "Brief vorlesen" liest alles vor, "Brief
drucken" druckt. Der Punkt, der ihn unbrauchbar machte, ist am 2026-08-22
behoben: Der Schluss verlangt jetzt eine **Sprechpause davor**. Offline gegen
Piper geprueft, bevor Stephan testen musste - aus durchgehender Rede entstanden
zwei VOLLSTAENDIGE "diktat beenden", beide abgewiesen; der echte nach einer
Pause angenommen.

**Was fehlt, ist der Beweis am Geraet:** ein Diktat mit echter Stimme, das von
Anfang bis Ende durchlaeuft. Erst danach ist der Brief-Weg fertig. Ausserdem
fragt DIN 5008 nach Empfaenger und Betreff - der gefuehrte Dialog dafuer ist
noch nicht gebaut.

**Das Fehlermuster "lautlos durchgefallen" ist am 2026-08-24 von BEIDEN
Seiten angegangen worden** - es stand hier vorher als offener Punkt mit
Vorrang. Die eingeschraenkte Grammatik ist eine Liste von SAETZEN, aber Vosk
baut daraus ein WORTNETZ und darf Woerter aus verschiedenen Saetzen
kombinieren. Kam dabei etwas heraus, das kein Befehl ist, passierte nichts -
und es wurde auch nichts gesagt.

**Grundlage war Stephans Urteil ueber die Stichprobe**, um die er zweimal
gebeten hatte: "das waren alles Befehsversuche." Alle 283. Damit war meine
Sorge widerlegt, eine Ansage wuerde noergeln. Und sein zweiter Satz gab die
Form vor: "Ich muss selbst die genauen Befehle erst lernen und dann wundere ich
mich, dass ein anderer nicht funktioniert. Auch fuer mich eine Lernphase."

1. **Tolerantere Zuordnung.** Die Zuordnung war ein EXAKTER Vergleich; 21 der
   283 Aeusserungen enthielten den kompletten Befehl und loesten trotzdem
   nichts aus ('notiz notiz drucken', 'wir notiz aufnehmen'). Jetzt gilt ein
   Befehl, der als zusammenhaengende Wortfolge darin steckt - mit hoechstens
   ZWEI Zusatzwoertern. Ohne diese Grenze haette dieselbe Regel viermal aus
   Wortsalat "einkauf erledigt" ausgefuehrt und den Einkaufszettel abgeraeumt.
2. **Ansage, wenn nichts passt.** Nennt bei starker Uebereinstimmung den
   richtigen Satz, sonst nur das Gehoerte. KEINE Frageform - ein "ja" wuerde
   DialOS nicht verarbeiten, das waere ein neuer lautloser Fehlschlag gewesen.
   Zerstoerende Befehle werden nie vorgeschlagen.

**Am 2026-09-14 im Betrieb geprueft, mit einem Vorbehalt:** Die Ansage hat in
Stephans Sitzung fuenfmal ausgeloest und die Bremse hat gegriffen - aber KEIN
EINZIGES MAL wurde ein Befehl vorgeschlagen, immer nur "Das war kein Befehl".
Die Zwei-Drittel-Schwelle war in einer echten Sitzung nie erreicht ('vorlesen
uhrzeit' liegt beim naechsten Befehl bei 50 %). Damit fehlt genau die Haelfte,
die beim Lernen helfen soll. Die Schwelle gehoert an Stephans echten
Aeusserungen durchgerechnet - nicht geraten.

**Zurueckgestellt:** RustDesk-Fernwartung (Code fertig, geprueft, bewusst
nicht installiert - siehe die Ausschlussliste in `dialos-aufspielen`),
Aufweckwort (Lizenz der fertigen Modelle ist nicht kommerziell).

**Die Aussprache ist entschieden, fuer beide Stimmen.** Am 2026-08-24 hat
Stephan aus acht Schreibweisen gewaehlt: Anna sagt "Dial O S", Michael bleibt
bei "Dial OS". Die Regeln in AUSSPRACHE haben dafuer ein viertes Feld - die
Stimmen, fuer die sie gelten. Am 2026-09-14 kamen "Tas tatur" und "Ei Di" dazu,
beide mit Anna im echten Satz vorgespielt, Urteil "mit Regel" - sie gelten also
weiter fuer alle Stimmen und brauchen kein eigenes Feld.

**Offen aus Stephans Wuenschen:** ob PDF-ANHAENGE aus Mails ebenfalls ins
Archiv sollen.


## Frueherer Stand (2026-08-19)

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
Aufbau nach der Basis-Installation aus genau fünf Befehlen** (drei bis zum 2026-08-19, dann kamen `dialos-aufraeumen.sh` und `dialos-menue-pro-konto.sh` dazu - Schritt 13b/13c) - die letzte
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

- Sudo-Rechte für den Standard-Benutzer "nutzer". **Der Zustand ist nicht
  „offen", sondern VOLLER ADMINISTRATOR** - am 2026-09-14 nachgesehen:
  `sudo -l -U nutzer` meldet `(ALL : ALL) ALL`, weil das Konto in der Gruppe
  `sudo` steckt. Praktisch greift das heute nicht, weil das Passwort zufällig
  erzeugt wurde und niemand es kennt - aber die Tür ist nur zugezogen, nicht
  abgeschlossen. Eigener Punkt in TODO.md, mit dem, was vor einer Änderung zu
  klären ist.
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

**Erledigt seit dem 2026-08-18:** Diktat (`dialos-diktat.py`, freie
Erkennung mit dem grossen Modell, Schreibkorrektur über LanguageTool),
Notizen vorlesen und wegwerfen (`dialos-notiz.py`), Uhrzeit und Datum
(`dialos-auskunft.py`). Die Befehlsgrammatik ist auf **17 Sätze**
gewachsen, alle gegeneinander geprüft.

**Zwei Regeln, die sich dabei herausgebildet haben und für jeden neuen
Befehl gelten** - ausführlich in `docs/sprachbefehle.md`:

1. **Neue Wörter zweifach prüfen:** erst, ob sie überhaupt im Wortschatz
   des Modells stehen (Vosk meldet `Ignoring word missing in vocabulary`
   beim Bauen der Grammatik - sofort und ohne Sprechen), dann, ob der
   ganze Satz in der **vollständigen** Grammatik richtig erkannt wird.
   Nicht enthalten sind zum Beispiel „löschen", „spät", „zurücksetzen",
   „aufräumen" - jedes davon hätte einen Befehl lautlos unwirksam gemacht.
2. **Ein Satz gilt auch, wenn der Erkenner ein Wort verschluckt**, solange
   kein `[unk]` dabei ist und das Kernwort eindeutig ist. Zweimal an zwei
   Tagen hat die Bedingung auf den vollen Satz einen Befehl blockiert -
   einmal den Schlusssatz des Diktats, einmal das Einschalten selbst.

**Nicht anfangen mit:** Telefonie (nach hinten gestellt, hängt an der
Hardware-Entscheidung), Chat (WhatsApp priorisiert, Bestätigung fehlt),
Videoaufnahme (Zweck ungeklärt).

## Installationsstand prüfen, nicht annehmen (Regel seit 2026-08-19)

**Das Repo ist die Vorlage, nicht der Beweis.** Am 2026-08-19 kam heraus, dass
`dialos-start-ansage.py` und `dialos-ton-ausgabe.py` auf dem Gerät **zwei Tage
lang** in einer älteren Fassung liefen als im Repo. Beide Änderungen vom
2026-08-17 waren committet und nie installiert: Die Repo-Datei wurde jeweils
rund zehn Minuten **nach** dem `install` noch bearbeitet.

Es fehlte nichts Kosmetisches - auf dem Gerät stand noch „Bluetooth-Mikrofon
bevorzugt" (genau die Reihenfolge, die dreimal in HFP hängengeblieben war) und
der Senken-Vergleich, der die Umschalt-Ansage ausfallen ließ.

Aufgefallen ist es nur, weil einmal **alle** Skripte verglichen wurden statt
nur die des Tages. Deshalb:

```bash
scripts/dialos-installstand.sh --befehl
```

vergleicht alles und gibt bei Abweichung gleich den `install`-Befehl aus. **Am
Ende einer Arbeitssitzung ausführen** - ein Commit beweist nur, dass die
Änderung im Repo ist, nicht dass sie auf dem Gerät wirkt. Und ein Test gegen
eine nicht installierte Änderung testet den alten Stand, ohne es zu sagen.

## Wortschatz-Pruefung: Umlaute nur mit ensure_ascii=False (Regel seit 2026-09-14)

**`json.dumps(grammatik)` ohne `ensure_ascii=False` macht aus "ö" ein
`\u00f6` - und Vosk meldet dann JEDES Umlaut-Wort als "missing in
vocabulary".** Seit August wurden so "loeschen", "spaeter", "spaet",
"zuruecksetzen" und "aufraeumen" faelschlich als unbekannt verworfen. Jede
Grammatik und jede Wortschatz-Pruefung uebergibt mit `ensure_ascii=False`.
Eine Warnung zu einem Wort mit ae/oe/ue/ss-Laut zuerst DARAUF pruefen.

## Dienste nicht aus Claudes Sitzung heraus testen (Regel seit 2026-09-14)

**Ein DialOS-Dienst, den Claude neu startet, laeuft in Claudes systemd-Einheit
(`app-com.anthropic.Claude-….scope`) - und erbt damit alles, was an diese
Einheit gebunden ist.** Am 2026-09-14 kam heraus, dass das Bildschirmfoto drei
Wochen lang nur deshalb funktioniert hatte: Die Portal-Freigabe galt
`com.anthropic.Claude`, nicht DialOS. Nach dem ersten echten Neustart startete
der Autostart den Dienst unter eigenem Namen, und der Befehl war tot.

Deshalb: **Ein Test gegen einen aus Claudes Sitzung gestarteten Dienst beweist
nichts fuer den Kunden.** Den Beweis liefert erst ein Start ueber den Autostart
(Ab- und Anmelden oder Neustart). Fuer stille Einzelproben die Einheit
nachbilden: `systemd-run --user --scope --unit='app-gnome-dialos\x2d…-<nr>' …`.

## Arbeitsweise mit Stephan

**Vier Regeln, die am 2026-08-21 teuer gelernt wurden. Sie stehen zuerst,
weil sie den Tag gekostet haben:**

1. **Nur EIN Befehlsblock je Nachricht.** Mehrere Bloecke landen in Stephans
   Oberflaeche ohne Zeilenumbruch in derselben Eingabezeile - aus zwei
   Befehlen wird ein dritter, der nicht existiert
   (`dialos-akku-warnung.servicesudo.service`: "Unit not found"). Es laeuft
   dann WEDER der erste NOCH der zweite, und es sieht aus, als sei nichts
   passiert. Braucht ein Schritt mehrere Befehle: mit `&&` in einen Block
   oder ueber mehrere Nachrichten verteilen.
2. **Nach "Befehl ist durch" erst kurz warten, dann pruefen.** Zweimal an
   diesem Tag habe ich zu frueh nachgesehen und daraus geschlossen, es sei
   nichts ausgefuehrt worden - und Stephan denselben Befehl mehrfach
   ausfuehren lassen.
3. **Keine Regel bauen, die Stephan ungeprueft testen muss.** Ich habe die
   Schlusserkennung des Diktats an einem Nachmittag viermal geflickt, und
   jedes Mal hat der naechste Test die naechste Luecke gefunden - eine der
   "Reparaturen" unterbrach ihn sogar mitten im Diktieren. Was gegen Piper
   offline pruefbar ist, wird VORHER offline geprueft. Der Aufbau dafuer
   steht: Piper spricht, beide Erkenner hoeren mit, jedes Ergebnis mit
   Zeitstempel.
4. **Eine Erklaerung, die zu allen Beobachtungen passt, ist noch keine
   Ursache.** Zwei meiner Diagnosen an diesem Tag waren in sich schluessig
   und gemessen falsch (Umgebungsgeraeusch, die eigene Ansage). Erst messen,
   dann behaupten - und wenn die Messung die eigene Behauptung widerlegt,
   gehoert das in den Quelltext, damit es niemand ein zweites Mal prueft.


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
