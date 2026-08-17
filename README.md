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

**Seit dem 2026-08-16 läuft DialOS auf echter Hardware.** Aus einer
nackten Debian-13/GNOME-Installation entsteht das fertige System in drei
Befehlen – am Referenzgerät (ThinkPad T490) end-to-end durchgeprüft:

```bash
./scripts/dialos-full-office-setup.sh                    # Pakete, Branding, Sprachausgabe, Vosk
/usr/local/sbin/dialos-setup-home-partition.sh           # verschlüsselter Swap + nutzer-Partition
sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin   # Konto + Autologin
```

**Was funktioniert:** Sprachausgabe über Piper, Spracherkennung über
Vosk, das vollständige Sicherheitskonzept (verschlüsselte
`nutzer`-Partition und verschlüsselter Swap, Sicherheits-Stick als
Anwesenheits-Token – in beiden Richtungen nachgewiesen: ohne Stick ist
das Konto gesperrt und die Daten sind verschlossen, mit Stick meldet sich
`nutzer` automatisch an), Autologin, Branding, Standardprogramme.

**Seit dem Abend des 2026-08-16 gehört dazu der erste echte
Sprachbefehl.** Ein dauerhaft lauschender Dienst schaltet auf Zuruf die
Optik des Schreibtischs um:

> "auf Windows umschalten" &nbsp;·&nbsp; "auf Linux umschalten"

Dahinter steht die optionale Windows-11-Optik – für Menschen, die DialOS
wegen der Sprachsteuerung wollen, aber aus der Windows-Welt kommen. GNOME
bleibt dabei vollständig erhalten (Orca, AT-SPI), es kommen nur drei
Erweiterungen obendrauf, und es lässt sich jederzeit in beide Richtungen
zurückschalten. Die gewählte Optik bleibt über Neustarts hinweg
bestehen.

**Was noch fehlt – der eigentliche Kern:** die Sprachsteuerung in der
Breite. Was es gibt, ist eine auf drei feste Sätze beschränkte
Erkennung; was fehlt, ist ein Aufweckwort und eine Befehlsgrammatik für
alles andere (Radio, Briefe, Termine). Ebenso offen: Telefonie und die
WWAN-Variante.

Details zum jeweiligen Stand stehen im
[Änderungsprotokoll](#änderungsprotokoll), konkrete nächste Schritte in
[TODO.md](TODO.md).

## Dokumentation

- [Debian-zu-DialOS](docs/Debian-zu-DialOS.md) – Schritt-für-Schritt-Rezept: von einer nackten Debian-13/GNOME-Installation bis zur aktuellen Version
- [Architektur-Übersicht](docs/architektur-uebersicht.md) – Ziel, Zielgruppe, Kernfunktionen, Software-Stack
- [Hardware](docs/hardware.md) – Referenzgerät, Test-Hardware, WWAN-Anforderungen
- [Sicherheit & Datenschutz](docs/sicherheit-datenschutz.md) – Autologin, Verschlüsselung, Fernwartung, Versand
- [Sprachbefehle](docs/sprachbefehle.md) – die Liste aller Sprachbefehle: was das System versteht und was es dann tut
- [Sprachsteuerung](docs/sprachsteuerung.md) – STT/TTS-Stack, Intent-Erkennung, Design-Prinzipien
- [Telefonie & Videocall](docs/telefonie.md) – SIM- und Handy-Anbindung, Fallback-Logik
- [Ersteinrichtung & Rollout](docs/ersteinrichtung.md) – Zwei-Phasen-Provisionierung, Sprachassistent, Datenschutz-Varianten
- [Vorführvideos aufnehmen](docs/video-aufnahme.md) – OBS-Einrichtung mit getrennten Tonspuren, und die zwei Fallen, die den Ton ruinieren
- [Offene Punkte](docs/offene-punkte.md) – was noch zu klären/entscheiden ist
- [Abbild-Verzeichnis](docs/iso-builds.md) – welches Sicherungs-Abbild zu welchem Code-Stand gehört (Rescuezilla/Clonezilla)

## Logo & Branding

Weitere Varianten liegen in [assets/](assets/): `mark.png` (Bildmarke
allein), `logo-tagline.png` (mit Slogan), `logo-full.png` (mit
Feature-Icon-Zeile), `logo-horizontal-light.png`/`-dark.png` (horizontale
Version für helle/dunkle Hintergründe), `app-icon-light.png`/`-dark.png`
(quadratisches App-Icon) sowie `brand-sheet.png` als vollständige
Referenzübersicht. Dazu `wallpaper-light.png`/`wallpaper-dark.png`
(Desktop-Hintergrund) und `splash.png` (Boot-/Login-Bildschirm).

## Testumgebung

- **Laptop:** Lenovo ThinkPad T490 (ohne WWAN-Modul)
- **Audio:** AIRHUG 01 – Bluetooth-Headset, seit 2026-08-16 das
  Referenzgerät für die Sprachsteuerung (siehe
  [hardware.md](docs/hardware.md)). Rückfall auf die eingebauten
  Lautsprecher/Mikrofone ist Pflicht und für die Ausgabe nachgewiesen.
  Das eingebaute Mikrofon war bis zum 2026-08-16 um 60 dB übersteuert –
  seither korrigiert und per Dienst bei jedem Start abgesichert.
- **Eingabegeräte:** Logitech Pebble M350s (Maus), Pebble K380s (Tastatur)
- **Sicherheits-Stick:** 64 GB, aufgeteilt in `DIALOS-KEY` (Schlüssel,
  ext4) und `DIALOS-DATA` (exFAT, auch an Windows/macOS lesbar)
- **Android-Testgerät** für die Handy-Anbindung (USB-Tethering +
  GSConnect)

## Änderungsprotokoll

### 0.5.1

*In Arbeit seit 2026-08-17. Alles, was ab jetzt entsteht, wird hier
eingetragen - 0.5.0 ist mit dem Sprachbefehl für die Desktop-Umschaltung
abgeschlossen.*

- **Ein ausgeschaltetes Headset hat die komplette Tonausgabe des Systems
  mitgenommen - und die Ursache war meine Testkonfiguration
  (2026-08-17).** Nach Stephans Neustart kam bei **beiden** Konten keine
  Ansage mehr. Im Protokoll stand nur „spd-say nach 20s abgebrochen -
  Sprachausgabe antwortet nicht."; das Sprech-Symbol erschien, es kam
  nichts. Ursache: `capture.props.target.object` der Echo-Unterdrückung
  zeigte auf Stephans USB-Headset, weil ich das am Vormittag zum Testen
  umgehängt und **in `/etc` stehen gelassen** hatte. Beim Anmelden lieferte
  das Gerät keine Daten. Das Modul braucht diese Aufnahme als Taktgeber -
  ohne Takt startet PipeWire den Graph nicht, die Soundkarte bleibt auf
  `state: PREPARED` mit `trigger_time: 0.000000000`, und **jede**
  Wiedergabe hängt für immer, auch über die eingebauten Lautsprecher.
  Behoben durch Rückkehr auf das eingebaute Mikrofon; als Regel in
  `docs/Debian-zu-DialOS.md` Schritt 11f festgehalten: **Das Ziel der
  Echo-Unterdrückung darf kein Gerät sein, das man ausschalten oder
  abziehen kann.**
  - **Die Testfassung hätte nie über einen Neustart in `/etc` bleiben
    dürfen.** Eine eigene Testkonfiguration gehört nach
    `~/.config/pipewire/pipewire.conf.d/` - dort ist sie ohne Passwort
    änderbar und tut niemandem weh. Genau darüber habe ich am Ende auch
    die Ursache eingekreist.
  - **Zwei Fehlschlüsse auf dem Weg, beide durch Messen widerlegt:** Ich
    habe zuerst „PipeWire ist gesund" gemeldet, weil das Modul geladen
    war und die Senke „RUNNING" zeigte - dass die Uhr nicht tickt, war an
    derselben Stelle schon sichtbar. Und ich habe `webrtc.gain_control`
    verdächtigt, das am selben Tag von `false` auf `true` gewechselt war
    und ebenfalls erst beim Neustart wirksam wurde. Der Reihentest zeigte:
    beide Werte hängen gleich, es war das Zielgerät. Auch der AIRHUG war
    unschuldig - der eingebaute Lautsprecher hing genauso.
  - **Der Befund, der die künftige Absicherung schwer macht: es gibt
    keinen verlässlichen Anzeiger.** Das Aufnahmegerät lieferte **0 Bytes
    in 3 Sekunden** (das eingebaute Mikrofon zum Vergleich 64000) -
    während ALSA für dasselbe Gerät `state: RUNNING` meldete, der Dongle
    eine Soundkarte anbot und, wie Stephan feststellte, das Headset ihm
    selbst eine bestehende Verbindung meldete. Erst Abziehen und
    Wiedereinstecken des Dongles brachte die 64000 Bytes. Eine Prüfung
    darf sich deshalb auf keine Zustandsmeldung stützen, nur auf die
    tatsächlich ankommenden Bytes. Siehe `TODO.md`.
  - **Was der Nutzer erlebt hätte:** ein totes Gerät. Keine Fehlermeldung,
    kein Piepen, nur Ansagen, die sich stapeln - beim Vorfall drei
    Sprachausgaben und vier GNOME-Klänge, alle noch in der Warteschlange.
    Für einen blinden Nutzer ist das nicht „der Ton ist weg", sondern
    „das Gerät ist kaputt".

- **Der Schreibtisch heißt jetzt „Linux Desktop" und „Windows Desktop"
  (Stephans Wunsch, 2026-08-17).** Die Ansagen waren am Vormittag von
  einem erklärenden Satz auf ein einzelnes Wort zusammengestrichen
  worden - das war zu weit gekürzt. „Windows." allein ist kein Satz,
  sondern ein Stichwort; wer nur zuhört, weiß nicht, ob das die Antwort
  auf seinen Befehl war oder eine Meldung von irgendwoher. Mit dem
  Zusatz kostet es 0,6 Sekunden mehr (1,59 s statt 0,93 s) und ist
  eindeutig.
  - **Dazu die Rückmeldung, die Stephan schon gemeldet hatte:** Befiehlt
    er den Stil, auf dem er ohnehin steht, sagt DialOS jetzt „Steht schon
    auf Linux Desktop." Vorher kam dieselbe Ansage wie bei einem echten
    Wechsel - für einen blinden Nutzer ununterscheidbar. Der Stil wird in
    dem Fall trotzdem neu gesetzt; das ist die Absicherung dagegen, dass
    eine Systemaktualisierung die Erweiterungsliste zurückgesetzt hat.

- **Die Start-Ansage wurde von der Desktop-Ansage überredet - und zwar
  seit dem ersten Tag (gefunden 2026-08-17).** Stephan hatte das am
  Vormittag gemeldet („die Ansage mit dem Desktop kam dazwischen"), und
  ich hatte es für ein Zeitproblem zwischen zwei Autostarts gehalten. Es
  war ein Fehler im Skript: `wiederherstellen` ruft beim Anmelden
  `auf_gnome` bzw. `auf_windows` mit `>/dev/null 2>&1` auf, und im
  Kommentar darüber stand „ohne Ansage, weil dabei niemand etwas
  ausgelöst hat". Die Umleitung schluckt aber nur die Terminal-Zeile -
  `melde()` ruft die Sprachausgabe direkt auf, und die spricht weiter.
  **Bei jedem Anmelden hat der Schreibtisch also ungefragt geredet**,
  mitten in die Start-Ansage hinein, weil beide Autostarts gleichzeitig
  loslaufen. Behoben mit einem `STUMM`-Schalter, der nur das Sprechen
  abschaltet, nicht die Terminal-Zeile.
  - **Was daran lehrreich ist:** Der Kommentar hat die Absicht
    beschrieben, nicht das Verhalten - und ich habe ihn beim Suchen als
    Beleg gelesen statt als Behauptung. Bis heute stand acht Sekunden
    Windows-Text in dieser Lücke, ohne dass jemand die Ursache gesucht
    hätte.

- **Ansagen kommen jetzt aus einem Speicher: 2172 ms auf rund 1200 ms
  (Stephans Meldung „die Pause ist zu groß", 2026-08-17).** Zwischen
  „Sprachsteuerung starten" und Michaels „Ich höre." lagen gut zwei
  Sekunden. Gemessen: Die Ansage selbst dauert 1,13 s, `paplay` einer
  fertigen Datei braucht 1,18 s - **rund 1,1 Sekunden waren reiner
  Vorlauf**, jedes Mal neu erzeugt für einen Satz, der sich nie ändert.
  `dialos-say.py` legt gesprochene Sätze deshalb unter
  `~/.cache/dialos/ansagen` ab und spielt sie beim nächsten Mal von dort.
  - **Der Speicher füllt sich von selbst.** Beim ersten Mal geht der Satz
    den normalen Weg und wird nebenbei im Hintergrund aufgezeichnet; ab
    dem zweiten Mal kommt er aus der Datei. Keine Liste, die gepflegt
    werden muss, und nichts, das veralten kann, weil jemand einen neuen
    Satz eingebaut und den Speicher vergessen hat.
  - **Der Schlüssel enthält die Änderungszeit von `PIPER_CONF` und dem
    Stimmen-Ordner.** Ändert sich das Tempo - wie heute von 0,85 auf 0,88 -
    oder die Stimme, entstehen automatisch neue Schlüssel und der alte
    Bestand wird nicht mehr gefunden. Ohne das spräche DialOS nach einer
    Tempoänderung teils im alten, teils im neuen Tempo.
  - **Ein eigener Fehler, der sich selbst versteckt hat:** Ich fange in
    der Speicher-Funktion alle Ausnahmen ab, damit ein Fehler dort nie
    eine Ansage verhindert - und habe damit den eigenen Fehler unsichtbar
    gemacht. Der Speicher blieb leer, ohne dass irgendwo etwas stand.
    Erst ein Nachbau mit sichtbaren Ausnahmen brachte es heraus: Die
    Zwischendatei hieß `….wav.teil`, und **sox bestimmt das
    Ausgabeformat an der Dateiendung**. Die Vorsichtsmaßnahme gegen
    halbfertige Dateien hat die Datei verhindert. Behoben mit `-t wav`.

- **„Ich muss sehr laut reden" war kein Pegelproblem, sondern eine
  selbstgebaute Taubheit (Stephans Meldung, 2026-08-17).** Ich habe
  zuerst an der Mikrofon-Verstärkung gesucht, weil die Beschreibung genau
  danach klang. Stephans Präzisierung hat es gedreht: **„Den *zweiten*
  Befehl musste ich wesentlich lauter ins Mikro brüllen."** Der erste
  ging also normal. Im Code stand nach der Ansage „Ich höre."
  `letzte_aktion = time.time()` - dieselbe Sperrfrist von fünf Sekunden,
  die nach einem echten Umschalten sinnvoll ist. Der Dienst war damit
  **ausgerechnet in den fünf Sekunden nach „Ich höre." taub**, also genau
  dann, wenn der Nutzer seinen Befehl sagt. Für Stephan sah das aus wie
  zu leise: Er sprach, nichts geschah, er wiederholte lauter - und dann
  war die Frist abgelaufen und es klappte. Die Sperrfrist gilt jetzt nur
  noch nach echtem Umschalten und liegt bei zwei Sekunden; gegen die
  eigene Stimme schützt ohnehin das Verwerfen der Aufnahme nach jedem
  Sprechen.
  - **Und ein echter Beitrag am Pegel:** `webrtc.gain_control` steht
    jetzt auf `true`. Die Begründung für `false` bezog sich auf das
    eingebaute Mikrofon, das um 60 dB übersteuert war - dort hätte eine
    zusätzliche Verstärkung geschadet. Am Headset ist die Lage umgekehrt.
    **Im Auge behalten:** Eine Verstärkungsregelung hebt in Sprechpausen
    auch das Grundrauschen an. Arbeitet sie zu kräftig, hört die
    Erkennung überall Sprache und die Fehlauslösungen kommen zurück -
    nach einer Umstellung also nicht nur prüfen, ob es lauter wird,
    sondern auch, ob es in Ruhephasen still bleibt.

- **Der USB-Weg ist bewiesen - mit Hardware, die schon da war
  (2026-08-17).** Stephans vorhandenes Headset, ein **TeckNet TK-HS005**
  mit 2,4-GHz-USB-Dongle, meldet sich ohne Treiber und ohne Kopplung als
  Soundkarte. Entscheidend ist sein Profil:
  `output:analog-stereo+input:mono-fallback` mit `sinks: 1, sources: 1` -
  **Ausgabe und Eingabe gleichzeitig.** Genau das, was Bluetooth nicht
  kann: Beim AIRHUG hat jedes A2DP-Profil `sources: 0`, man muss zwischen
  gutem Klang und Mikrofon wählen. Damit ist die offene Frage aus
  `hardware.md` beantwortet, und das Risiko „Musik stottert" entfällt auf
  dem USB-Weg vollständig, weil keine Funkzeit auf dem Bluetooth-Adapter
  belegt wird.
  - **Als Referenz-Hardware taugt das Gerät trotzdem nicht:** Im
    USB-Deskriptor steht als Hersteller wörtlich „Generic"; „Actions
    Semiconductor" ist nur der Chiplieferant, und die Marke TeckNet steht
    lediglich aufgedruckt auf dem Gehäuse. Derselbe Chip im selben
    Gehäuse wird unter beliebig vielen Namen verkauft. Ein Gerät, das
    über Jahre nachkaufbar sein muss, sollte identifizierbar sein.
  - **Beim Umhängen der Echo-Unterdrückung ein eigener Fehler:** Ich
    hatte nur die Testkopie im Benutzerordner geändert. Die Systemdatei
    unter `/etc/pipewire/pipewire.conf.d/` wird aber zuerst geladen und
    belegt den Knotennamen - die Benutzerdatei scheiterte still an der
    Kollision, und die Unterdrückung hing weiter am eingebauten Mikrofon.
    Beim Prüfen aufgefallen, weil die Aufnahme an Quelle 68 statt 63 hing.

- **Godox Cube-SC Kit2 geprüft und verworfen (Stephans Vorschlag,
  2026-08-17).** Ein 2,4-GHz-Funkmikrofon mit USB-C-Empfänger, das auf
  dem Papier gut passt: **UAC** ausdrücklich unterstützt und für den
  PC-Einsatz vorgesehen, 300 m Reichweite, 48 kHz/24 Bit, zwei Sender im
  Set, rund halb so teuer wie der Lark M2. Es scheitert an einem Detail,
  das in keiner Datenblatt-Zeile steht, sondern erst im Testbericht
  auftaucht: **Die Sender laden ausschließlich über Kontakte im Ladecase
  und haben keine eigene Ladebuchse.** Damit ist Dauerbetrieb am Netzteil
  ausgeschlossen - nach 8 bis 10 Stunden muss der Sender ins Case, und
  das System ist so lange taub. Genau die Anforderung, die als härteste
  bestimmt worden war. Dazu bleibt der Akkustand für DialOS unsichtbar;
  Godox zeigt ihn in einer Handy-App, die es unter Linux nicht gibt und
  die ein blinder Nutzer nicht bedienen könnte.
  - **Als Testgerät bleibt es brauchbar:** Es beantwortet billig, ob ein
    2,4-GHz-Mikrofon unter Linux als Soundkarte erscheint und wie die
    Erkennung damit klappt. Die wichtigere Frage - Akkustand-Sichtbarkeit
    gegen mögliches Stottern der Musik - beantwortet nur der
    Bluetooth-Test.
  - **Offen geblieben, weil keine Beschreibung es hergibt:** ob der
    Sender im geöffneten Case betrieben werden kann, also dauerhaft
    gedockt und geladen. Wäre das so, wäre es die gesuchte
    Netzteil-Lösung.

- **Bluetooth gegen USB beim Mikrofon: doch offen, und aus einem Grund,
  den ich unterschätzt hatte (Stephans Einwand, 2026-08-17).** Ich hatte
  USB gesetzt, weil es die HFP-Falle umgeht. Sein Einwand trifft
  ausgerechnet die Anforderung, die ich selbst als härteste bezeichnet
  hatte: **Bei Bluetooth sieht DialOS den Akkustand** - die Start-Ansage
  liest ihn über BlueZ heute schon vor und könnte warnen, bevor das
  Mikrofon leer ist. Bei USB ist der Empfänger nur eine Soundkarte; der
  Sender kann leer sein, ohne dass das System es merkt.
  - **Dagegen steht ein Risiko, das sich nicht durch Nachlesen klären
    lässt:** Ein dauerhaft offenes HFP belegt fortlaufend Funkzeit auf
    demselben Adapter, über den der AIRHUG spielt - dass A2DP dabei
    stottert, ist ein bekanntes Problem und hängt vom Adapter ab.
  - **Der Unterschied ist also nicht „gut gegen schlecht", sondern welchen
    Fehler man lieber hätte:** ein Mikrofon, das unbemerkt leer wird, oder
    Radio, das während des Zuhörens stottern könnte. Deshalb zuerst ein
    preiswertes Bluetooth-Mikrofon zum Ausprobieren - fällt der Test gut
    aus, ist es die bessere Lösung; fällt er schlecht aus, weiß man es für
    30 Euro statt für 150.
- **Neue Aufgabe, unabhängig von der Gerätewahl: erkennen, wenn das
  Mikrofon nichts mehr liefert.** Der Sprachdienst misst ohnehin laufend
  den Pegel. Kommt über Minuten hinweg gar nichts an, obwohl die Quelle
  da ist, soll er ansagen „Ich höre nichts mehr vom Mikrofon." Das
  ersetzt keine Akkuanzeige, fängt aber den Ausfall ab, der den Nutzer
  sonst ratlos zurückließe: Er redet gegen ein totes Gerät, ohne es zu
  merken.

- **Referenz-Audiogerät entschieden: zwei Geräte statt einem (Stephan,
  2026-08-17).** Der AIRHUG bleibt als Lautsprecher in A2DP, dazu kommt
  ein Funkmikrofon mit **USB**-Empfänger für die Eingabe. Bewusst kein
  zweites Bluetooth-Gerät: Das brächte die HFP-Falle zurück, die den
  ganzen Vormittag gekostet hat. Ein USB-Empfänger meldet sich als
  gewöhnliche Soundkarte - kein Profil, kein Konflikt, keine Kopplung,
  und der Lautsprecher bleibt unangetastet.
  - **Die härteste Anforderung ist der Akku, nicht der Klang.** Ein
    leerer Sender macht das System **taub**, und ein blinder Nutzer
    findet die Ursache nicht - sie liegt außerhalb des Systems. Dieselbe
    Sorte Fehler wie die entkoppelte Gerätelautstärke. Der Hollyland
    Lark M2 hält 10 Stunden pro Sender; vor dem Kauf ist deshalb zu
    klären, ob der Sender **dauerhaft am Netzteil** laufen kann.
  - **Geprüft und verworfen: USB-Konferenzmikrofon an aktiver
    Verlängerung.** Technisch die sauberste Lösung - kein Akku, immer an.
    Aber ein Kabel quer durchs Wohnzimmer ist bei einem blinden Nutzer
    eine Stolperfalle. Für ein Testgerät brauchbar, für ein Kundengerät
    nicht.
- **Entscheidungsvorlage für Telefonie festgehalten (Stephans Frage,
  2026-08-17).** Telefonie ist nicht umgesetzt, die Überlegung wäre sonst
  aber verloren: Der naheliegende Weg für ein Gespräch wäre, auf HFP zu
  schalten - der AIRHUG wird zum Freisprecher. Der **bessere** Weg ist
  vermutlich, gar nicht umzuschalten: Eingang das USB-Mikrofon, Ausgang
  der AIRHUG in A2DP. Dann läuft das Gespräch in **beide** Richtungen in
  voller Qualität statt in Telefonqualität, das Profilwechsel-Problem
  entfällt vollständig, und die Echo-Unterdrückung ist ohnehin da. **Der
  Vorbehalt:** Im Gespräch läuft der Ton gleichzeitig in beide
  Richtungen - das ist für eine Echo-Unterdrückung anspruchsvoller als
  unser bisheriger Fall. Die gemessenen 32 dB sind ein gutes Zeichen,
  aber kein Beweis dafür.

- **Stephans Reichweiten-Frage entwertet die Mikrofon-Entscheidung von
  derselben Stunde - und deckt eine Lücke in der Referenz-Hardware auf
  (2026-08-17).** Seine Frage: Der Laptop steht auf dem Schreibtisch, der
  Bluetooth-Lautsprecher auf dem Wohnzimmertisch und spielt Radio - wie
  ändert man von dort die Lautstärke? Über das eingebaute Mikrofon gar
  nicht. Damit ist die Anforderung klar: **Das Eingabegerät muss dort
  sein, wo der Nutzer ist; das Ausgabegerät darf überall stehen.**
  - **Der naheliegende Ausweg wurde geprüft und ist tot:** eine Taste am
    Lautsprecher als Startsignal, dann kurz HFP, zuhören, zurück. Gemessen
    auf **zwei getrennten Wegen**, weil einer allein nichts bewiesen
    hätte. Tastencodes (`/dev/input`): Der AIRHUG meldet sich als
    Eingabegerät und der Kernel führt Medientasten für ihn auf - gedrückt
    kommt nichts an, auch nicht während Audio läuft. AVRCP-Lautstärke
    (ein völlig anderer Kanal, den ein Tastenleser nie sieht): ebenfalls
    nichts. Stephans Befund dazu: „Die Lautstärke wird nur am Gerät
    gesteuert, ist aber nicht mit der Lautstärke von GNOME gekoppelt."
  - **Zwei der drei Testläufe waren wertlos, und beide Male lag es an
    mir:** Beim ersten ging die Ausgabe im Puffer von `xxd | head`
    verloren, beim zweiten scheiterte die Wiedergabe, weil das Skript
    unter `sudo` lief und root keinen Zugriff auf die PipeWire-Sitzung
    des Benutzers hat („Connection refused"). Erst der dritte Lauf war
    sauber. Festgehalten, weil beide Fallen bei jedem künftigen
    Hardware-Test wieder drohen.
  - **Zweite Folge - und hier musste ich mich am selben Tag
    korrigieren.** Zuerst stand hier, DialOS könne den Lautsprecher
    überhaupt nicht regeln. Das war zu weit gegriffen: Ich hatte „nicht
    gekoppelt" nicht nach Richtung getrennt. Im Hörvergleich (10 % gegen
    100 %) zeigte sich, dass der **Rechner den AIRHUG sehr wohl steuern
    kann** - nur seine eigenen Tasten melden sich nicht zurück. „Mach
    lauter" ist also umsetzbar. Was bleibt, ist ein Restrisiko: DialOS
    **weiß nicht, wo die Lautstärke steht**, wenn jemand am Gerät gedreht
    hat. Steht die Software schon auf 100 %, hilft kein Sprachbefehl mehr,
    und die Ursache liegt außerhalb des Systems.
  - **Damit steht die Festlegung vom 2026-08-16 („Referenzgerät ist der
    AIRHUG 01") wieder zur Entscheidung.** Drei Möglichkeiten in
    `docs/hardware.md`, alle mit ihrem Preis. Bis zur Entscheidung bleibt
    es beim eingebauten Mikrofon, weil das wenigstens die Ausgabequalität
    nicht beschädigt.

- **Aufteilung von Ein- und Ausgabe festgelegt und in der Doku
  richtiggestellt (Stephans Nachfrage, 2026-08-17):
  Spracheingabe immer über das eingebaute Mikrofon, Sprachausgabe über
  den Bluetooth-Lautsprecher, sofern verbunden.** Die letzte Stelle, die
  noch anders arbeitete - die Lautstärke-Frage der Start-Ansage - ist
  umgestellt; sie nimmt jetzt dieselbe echo-bereinigte Quelle wie der
  Sprachbefehl-Dienst.
  - **Das klingt widersprüchlich, ist aber genau der Punkt.** Weil
    Lautsprecher und Mikrofon verschiedene Geräte sind, hört das Mikrofon
    die Ausgabe im Raum mit - und genau das rechnet die
    Echo-Unterdrückung heraus. Über das Bluetooth-Mikrofon ginge das
    nicht, und das Headset fiele dabei auf Telefonqualität.
  - **Der HFP-Profilwechsel entfällt damit ersatzlos** - am 2026-08-17
    ist er dreimal hängengeblieben und hat den AIRHUG dauerhaft auf
    Telefonqualität stehen lassen. Wer das Bluetooth-Mikrofon gar nicht
    erst öffnet, kann auch nicht darin steckenbleiben.
  - **Nebenbei behoben:** Die Lautstärke-Frage bog bisher die
    **systemweite** Standard-Eingabe um (`pactl set-default-source`) - ein
    Eingriff, der über diese eine Frage hinaus wirkt, weil jedes andere
    Programm danach eine andere Quelle bekommt. Jetzt bekommt `parec` die
    Quelle direkt übergeben.
  - **Vier Doku-Stellen richtiggestellt**, die noch das Gegenteil
    behaupteten („Bluetooth ist also der primäre Weg"). Sie stützten sich
    auf den Mikrofon-Vergleich vom 2026-08-13 - der lief unter 60 dB
    Übersteuerung und ist damit nicht belastbar; er steht als zu
    wiederholen in TODO.md.
- **Live-Test des Bedienmodells bestanden (2026-08-17, Stephans Stimme).**
  Das Debug-Protokoll belegt beide Enden, nicht nur die Mitte: **Vor** dem
  ersten „Sprachsteuerung starten" zeigt der Pegel gesprochene Sprache
  (12 Messwerte über 5 %, Spitze 66,8 %) - und **keine einzige
  Erkennung**. Dazwischen wurden alle sechs Befehle wörtlich erkannt.
  **Nach** „Sprachsteuerung stoppen" wieder Sprache im Pegel, wieder
  keine Erkennung. Der Schutz greift also nicht, indem etwas erkannt und
  dann verworfen wird - im Zustand „aus" kann es gar nicht erst gebildet
  werden.

- **Bedienmodell entschieden und gebaut: Wann hört DialOS zu?
  (2026-08-17, Stephans Entwurf).** Der Anlass war seine Frage, ob das
  System merkt, dass es gerade etwas wissen will - dahinter steckte ein
  vollständiges Modell mit **zwei Wegen ins Mikrofon**, je nachdem, wer
  das Gespräch begonnen hat.
  - **Das System fragt** → es öffnet die Erkennung selbst und schließt
    sie danach wieder. Der Nutzer meldet sich nicht an, er wurde ja
    gerade angesprochen. **Antwortet er nicht, wird einmal nachgefragt**;
    bleibt es still, sagt Michael „Schade, dass Du nicht antwortest."
    Bewusst kein stilles Aufgeben - wer nicht hört, dass die Frage vorbei
    ist, spricht womöglich ins Leere. Und bewusst nur *einmal*: Ein
    Gerät, das immer weiter fragt, ist für jemanden, der es nicht
    wegklicken kann, eine Zumutung. Eingebaut in die Lautstärke-Frage.
  - **Der Nutzer will etwas** → „Sprachsteuerung starten" → **„Ich
    höre."** … Befehle … „Sprachsteuerung stoppen" → **„Ich höre nicht
    mehr."** Läuft sie schon: „Ich höre schon."
  - **Nach zwei Minuten ohne Befehl schaltet sie sich selbst ab**, mit
    Ansage. Nicht zum Stromsparen: Wer das „stoppen" vergisst, hätte
    sonst dauerhaft ein offenes Mikrofon - und damit wären wir zurück
    beim Radio, das den Schreibtisch umschaltet.
  - **Beim Anmelden ist die Erkennung immer aus.** Technisch ist das der
    eigentliche Schutz: Im Zustand „aus" kennt die Vosk-Grammatik nur
    einen einzigen Satz, also kann nichts anderes überhaupt erkannt
    werden - nicht bloß ignoriert, sondern gar nicht erst gebildet.
  - **Damit ist die offene Zustandsfrage beantwortet**, an der ich mich
    festgefahren hatte: Woher weiß ein blinder Nutzer, ob die Erkennung
    an ist? Er **hört jeden Wechsel** - beim Ein- und Ausschalten und
    beim Ablauf der Zeit. Und ist er unsicher, sagt er einfach
    „Sprachsteuerung starten"; läuft sie schon, sagt das System es ihm.
    Ein Zustand, den man nur sehen kann, wäre für diese Zielgruppe kein
    Zustand.

- **Fragen klingen jetzt anders als Hinweise (Stephans Frage vom
  2026-08-17, am selben Tag gebaut).** `dialos-say.py` kennt den Schalter
  `--frage`; die Lautstärke-Frage der Start-Ansage ist der erste
  Anwendungsfall.
  - **Standard ist die natürliche Satzmelodie.** Im Hörvergleich wurden
    vier Varianten gegeneinander gestellt: derselbe Satz als Aussage, als
    Frage (nur das Satzzeichen anders), mit erhöhter Tonlage, und mit
    einem Signalton davor. Stephan hat die reine Satzmelodie gewählt -
    Piper erzeugt sie aus dem Fragezeichen von selbst, sie klingt
    natürlich und nutzt sich nicht ab. Technisch kostet sie nichts: Der
    Text trägt das Fragezeichen ohnehin.
  - **Der Signalton bleibt als Option** (`~/.config/dialos/frageton` mit
    Inhalt `an`, Stephans Wunsch: der Nutzer soll später entscheiden).
    Der Grund, ihn anzubieten: Eine steigende Melodie am Satzende erkennt
    nur, wer zugehört hat - wer den Anfang verpasst hat oder nebenbei
    Radio hört, braucht ein davon unabhängiges Signal.
  - **Warum ein Schalter im Code und nicht „erkenne das Fragezeichen
    selbst":** Ein Fragezeichen kann mitten in einem Hinweis stehen, und
    eine rhetorische Frage will kein Signal. Der Code, der die Ansage
    baut, *weiß*, ob er etwas wissen will. Nachgewiesen: Bei
    eingeschalteter Option bekommt eine mit `--frage` markierte Frage den
    Ton, ein gewöhnlicher Hinweis nicht.
  - Der Anlass dafür liegt am 2026-08-16: Beim ersten Test der
    Lautstärke-Frage wusste das System, dass es fragt - **Stephan wusste
    nur nicht, wann er antworten soll**, und die Antwort ging verloren.
    Behelf war damals der Satz „Und jetzt bitte.".

- **Echo-Unterdrückung gebaut - der Fehler von heute früh ist damit an
  der Wurzel behoben (2026-08-17).** PipeWires `module-echo-cancel` mit
  dem WebRTC-Algorithmus rechnet das Lautsprechersignal aus dem Mikrofon
  heraus und stellt die Quelle `dialos_mikrofon_ohne_echo` bereit; der
  Sprachbefehl-Dienst nimmt sie als erste Wahl. **Gemessen**, beide
  Quellen gleichzeitig aufgenommen, während der Lautsprecher die
  Start-Ansage abspielte: rohes Mikrofon 6,13 % RMS gegenüber 0,15 % an
  der bereinigten Quelle - rund **32 dB** Dämpfung, und das über
  Bluetooth, wo wegen der schwankenden Laufzeit deutlich weniger zu
  erwarten war. **Gegenprobe mit genau dem Fall, der vorher scheiterte:**
  dieselbe 23-Sekunden-Ansage per `paplay` abgespielt, also ohne jeden
  Schutz - der Dienst erkannte nichts und schaltete nicht um.
  - **`monitor.mode = true`** ist die entscheidende Einstellung: Ohne sie
    müssten alle Programme ihren Ton in eine eigens angelegte Senke
    spielen, damit das Modul weiß, was gerade zu hören ist. Jede
    Audio-Ausgabe von DialOS wäre umzubiegen, und jedes neue Programm
    müsste daran denken. So genügt der Mitschnitt der Ausgabe als
    Referenz, und nichts muss umgeleitet werden.
  - **Falle beim Einrichten, gleich zweimal aufgetreten:** Der Neustart
    von PipeWire wirft das Bluetooth-Gerät in HFP zurück, und die Karte
    bietet danach **gar kein A2DP mehr an** - `pactl set-card-profile`
    scheitert mit „No such entity". Erst ein `bluetoothctl
    disconnect`/`connect` bringt das Profil zurück. Steht im Rezept.
- **Weckphrase entschieden: „Sprachsteuerung starten" / „Sprachsteuerung
  stoppen" (Stephans Vorschlag, 2026-08-17).** Kein Weckwort vor jedem
  Befehl, sondern ein **Schalter**. Der Vorschlag ist messbar besser als
  mein Vorschlag mit dem Assistentennamen: „ich rufe michael an" kam
  vorher als `hallo michael` mit voller Sicherheit durch; hier bleiben
  alle drei Störsätze ruhig - „die **sprachsteuerung** von dialos ist
  praktisch" wird zu `sprachsteuerung [unk]`, „kannst du das **starten**"
  zu `starten`, „wir müssen das mal **stoppen**" zu `stoppen stoppen`.
  Zwei bestimmte Wörter direkt hintereinander fallen im Gespräch
  praktisch nicht, und jedes für sich löst nichts aus. Damit ist offen,
  ob openWakeWord überhaupt nötig wird - **noch kein Beweis**, geprüft
  wurde mit synthetischer Stimme und drei Störsätzen. Gebaut ist der
  Schalter noch nicht, er steht in TODO.md und in
  [docs/sprachbefehle.md](docs/sprachbefehle.md).
- **Aussprache: „Tastatur" klang wie „Taschtatur" (Stephan,
  2026-08-17).** Deutsch spricht „st" am Silbenanfang als „scht", und
  Piper setzt die Silbengrenze bei „Ta-statur". Behoben über die zentrale
  Aussprache-Stelle in `dialos-say.py`: „Tas tatur", von Stephan aus fünf
  Schreibweisen herausgehört. Bei der Gelegenheit sind die Regeln von
  einer einzelnen Ersetzung auf eine **Liste** umgestellt worden - es kam
  die zweite dazu, und es werden weitere kommen. Jede Regel trägt jetzt
  ihre Begründung im Code; ohne die sieht so eine Schreibweise später wie
  ein Tippfehler aus und wird „korrigiert".

- **Michael spricht jetzt etwas zügiger: `GenericRateMultiply` von 0.85
  auf 0.88 (Stephan, 2026-08-17, im Hörvergleich ausgewählt).** Verglichen
  wurden 0.72, 0.78, 0.85, 0.88 und 0.90 am selben Satz. Der Wert wirkt in
  der sox-Kette des Piper-Moduls und damit auf **jede** Sprachausgabe,
  nicht nur auf die Start-Ansage.
  - **Nebenbei eine offene Frage:** Zuerst hieß es, Michael klinge
    „hektisch" - gewählt wurde dann ein *schnellerer* Wert. Das spricht
    dafür, dass nicht das Tempo das Problem war, sondern die **fehlenden
    Pausen zwischen den Sätzen**: Piper hängt sie fast atemlos aneinander,
    was bei einer achtsätzigen Ansage gehetzt wirkt, obwohl jedes
    einzelne Wort normal schnell kommt. Langsamer sprechen macht es dann
    zäh statt ruhig. Steht als Vorschlag in TODO.md.
- **Ernster Fund beim Vorspielen der Ansage: Der Schutz gegen
  Selbst-Auslösung greift nur bei `dialos-say.py` (2026-08-17).** Beim
  Abspielen einer WAV-Datei mit `paplay` - also an `dialos-say.py` vorbei
  - schaltete der Sprachdienst mitten in der Wiedergabe den Desktop um.
  Grund: Nur `dialos-say.py` setzt die Markierung „das System spricht
  gerade". Der Dienst hörte also 23 Sekunden lang dem Lautsprecher zu,
  und die eingeschränkte Grammatik presste Bruchstücke in einen Befehl.
  **Das ist derselbe Mechanismus wie beim Selbst-Auslöser vom selben Tag,
  aber deutlich breiter:** Betroffen ist alles, was das Gerät abspielt -
  und DialOS soll Radio, Musik und Mediatheken abspielen. Ein
  Nachrichtensprecher, der „Windows" sagt, würde den Schreibtisch
  umstellen. Die Markierungsdatei reicht dafür prinzipiell nicht; nötig
  ist Echo-Unterdrückung (PipeWire bringt ein Modul mit) oder das
  ohnehin anstehende Aufweckwort. In TODO.md aufgenommen.

- **Aufnahme von Vorführvideos eingerichtet und belegt (2026-08-17).**
  OBS mit **drei getrennten Tonspuren**: Spur 2 die DialOS-Stimme als
  Mitschnitt der Ausgabe, Spur 3 das Mikrofon, Spur 1 beides gemischt als
  Referenz. Stephan schneidet damit in kdenlive mit den richtigen Spuren.
  Fertige Konfiguration unter `~/.config/obs-studio/`, beschrieben in
  [docs/video-aufnahme.md](docs/video-aufnahme.md) - die Datei ist nötig,
  weil die Einrichtung sonst bei einem Reinstall verloren wäre.
  Nachgeprüft: Die erzeugte MKV enthält tatsächlich eine Video- und
  **drei** Tonspuren.
  - **Zwei Grenzen, die den Ablauf bestimmen und sich nicht
    wegprogrammieren lassen:** Der Systemstart lässt sich nicht vom Gerät
    selbst aufnehmen (es läuft noch keine Aufnahmesoftware), und der
    Benutzerwechsel beendet den Rekorder, weil er in der Sitzung läuft.
    Beides braucht eine Kamera. Das ist keine Notlösung - der AIRHUG ist
    ein Lautsprecher, die Kamera hört also Ansage und Befehle so, wie ein
    Besucher sie hört.
  - **Zwei Fallen, beide kurz vor der Aufnahme real aufgetreten.** Der
    AIRHUG stand zweimal auf `headset-head-unit`; der Mitschnitt der
    Ausgabe hatte dann 1 Kanal bei 16000 Hz statt 2 Kanälen bei 48000 Hz -
    die aufgenommene Stimme hätte nach Telefon geklungen. Deshalb ist in
    der Szene fest das **eingebaute** Mikrofon eingetragen, obwohl die
    Standard-Eingabe das AIRHUG war, und das eingebaute ist jetzt
    zusätzlich die Standard-Eingabe: So kann kein Programm mehr
    versehentlich zum Bluetooth-Mikrofon greifen und HFP erzwingen.
- **„DialOS" kommt in der Start-Ansage nicht mehr vor (Stephans Wunsch,
  2026-08-17).** Es gab genau eine gesprochene Fundstelle: „DialOS ist so
  eingerichtet, dass ich Dir jetzt den Akku-Stand aller angeschlossenen
  Geräte mitteile." Gesprochen wurde daraus „Dial OS ist so
  eingerichtet…". Ersetzt durch **„Ich nenne Dir noch die
  Akku-Stände."** - kürzer, und vor allem: Der alte Satz erklärte eine
  *Einrichtung*, statt die Information zu geben, und der Nutzer hört das
  bei **jeder** Anmeldung. Michael hat sich zwei Sätze vorher vorgestellt
  und kann es direkt sagen. Die Aussprache-Regel in `dialos-say.py`
  bleibt bestehen, ist damit aber rein vorbeugend - gesprochen kommt der
  Name jetzt nirgends mehr vor.

### 0.5.0
- **Neue Datei `docs/sprachbefehle.md` (Stephans Wunsch, 2026-08-17):
  eine Tabelle Sprachbefehl → Aktion**, die mit jedem neuen Befehl
  mitwächst. Bewusst **zwei getrennte Tabellen** - umgesetzt und
  vorgesehen. Vermischt sähe Geplantes wie Vorhandenes aus, und genau
  dieser Fehler musste in diesem Projekt schon einmal aufgeräumt werden.
  Dazu die Regeln, die jeder neue Befehl einhalten muss; jede davon
  stammt aus einem tatsächlich aufgetretenen Fehler: ganzer Satz statt
  Einzelwort, Ja/Nein-Rückfrage bei sicherheitskritischen Aktionen,
  jeder Befehl sagt an was er getan hat, neue Wörter erst gegen das
  Modell prüfen, und nach jedem Sprechen die Aufnahme neu beginnen.
  Verlinkt aus README, `sprachsteuerung.md` und CLAUDE.md.
- **Der Sprachdienst hat sich selbst umgeschaltet - Ursache war
  Arithmetik, nicht Fehlerkennung (gefunden und behoben 2026-08-17).**
  Er schaltete auf Windows um und 15 Sekunden später von selbst zurück.
  Die Schutzmaßnahme "während das System spricht, wird nicht zugehört"
  war eingebaut und griff auch - sie verhindert aber nur das **Zuhören**,
  nicht das **Aufzeichnen**. `parec` erzeugt bei 16 kHz mono 16 Bit rund
  32.000 Bytes pro Sekunde; der Dienst verwarf währenddessen 4.000 Bytes
  alle 0,3 Sekunden, also nur rund 13.000 pro Sekunde. Er leerte die
  Warteschlange langsamer, als sie volllief - nach einer acht Sekunden
  langen Ansage standen rund fünf Sekunden **eigene Stimme** in der Pipe,
  die er danach ganz normal auswertete. Und weil die eingeschränkte
  Grammatik alles in einen der drei Sätze presst, wurde daraus ein
  Befehl. Behoben, indem die Aufnahme nach jedem Sprechen **komplett neu
  begonnen** wird - ein frischer `parec`-Prozess hat keinen Rückstand.
  Dieselbe Behandlung gilt jetzt für die Sperrfrist nach dem Umschalten.
  Regressionstest ohne Sprechen möglich, weil die eigene Ansage der
  Auslöser war: umgeschaltet, 30 Sekunden beobachtet, kein
  Zurückschalten mehr.
- **Der Pegel-Dienst lief strukturell zu früh - jetzt richtet der
  Sprachdienst den Pegel selbst (2026-08-17).**
  `dialos-mikrofon-pegel.service` läuft beim Booten, also **vor** der
  Anmeldung. WirePlumber stellt seine gespeicherten Geräte-Einstellungen
  aber erst in der Sitzung wieder her und hebt `Internal Mic Boost` dabei
  zurück auf +30 dB. Im Debug-Protokoll war die Folge unmittelbar zu
  sehen: durchgehend "ÜBERSTEUERT", und Stephans Befehle kamen nur als
  Bruchstücke an (`'linux'`, `'auf'`, `'windows gnome'` - ohne
  "umschalten", also ohne Wirkung). Der Sprachdienst richtet den Pegel
  jetzt selbst, **nachdem** er die Aufnahme geöffnet hat, also nach
  WirePlumbers Zugriff; zusätzlich erkennt er anhaltende Übersteuerung im
  Betrieb und regelt nach (höchstens einmal pro Minute, damit ein lautes
  Umfeld keine Dauerschleife auslöst). Getestet, indem der Boost
  absichtlich wieder hochgedreht wurde - der Dienst hat ihn beim Start
  selbst zurückgenommen. Damit ist auch die gestern zurückgenommene
  Erklärung wieder belastbar: Die 60 dB waren die Ursache, nur lag der
  Boost bei der Gegenmessung am Morgen gerade nicht auf dem aktiven
  Aufnahmeweg.
- **Aufweckwort durchgemessen - und der naheliegende Weg scheidet aus
  (2026-08-17).** Die Idee, dieselbe eingeschränkte Vosk-Grammatik auch
  fürs Weckwort zu nehmen, wurde geprüft und **verworfen**. Erkannt
  werden alle Kandidaten sauber ("Michael", "Hallo Michael", "Anna",
  "Computer") - die Wörter stehen also im Wortschatz des Modells, was
  nach "gnome" → "genug" nicht selbstverständlich war. Aber die
  Störsätze lösen aus: "ich rufe michael an" wird zu `hallo michael`,
  "der computer ist langsam" zu `computer`. Der Grund ist derselbe wie
  beim Selbst-Auslöser oben: **Eine eingeschränkte Grammatik hat keine
  Wahl, sie presst alles in die nächstliegende Phrase.** Für Befehle ist
  das ein Vorteil, fürs Weckwort das Gegenteil. Und die naheliegende
  Rettung greift nicht - "ich rufe michael an" wurde mit **conf 1.00**
  durchgereicht, ein Schwellwert trennt also nicht. Konsequenz:
  openWakeWord bleibt der Weg. Zur Wortwahl entschieden: **der Name des
  Assistenten** ("Hallo Michael", bei weiblicher Stimme "Hallo Anna") -
  er steht durch die Stimmenwahl bei der Ersteinrichtung ohnehin fest,
  womit auch Stephans geplante weibliche Stimme abgedeckt ist.
  **Korrektur einer eigenen Aussage:** Ein Aufweckwort schaltet das
  Mikrofon-Symbol **nicht** aus - um das Weckwort zu hören, muss weiter
  zugehört werden. Das ist auch richtig so: Das Gerät hört tatsächlich
  zu, und das zu verstecken wäre bei dieser Zielgruppe das Schlechteste.
- **Zwei Fehler, die der erste Morgen im Echtbetrieb aufgedeckt hat
  (2026-08-17).**
  - **Der Autostart für die Stil-Wiederherstellung fehlte - mein
    Fehler.** Der Modus `dialos-desktop-stil.sh wiederherstellen` war
    gebaut, dokumentiert ("läuft beim Anmelden") und im
    Änderungsprotokoll beschrieben, aber **nie verdrahtet**: Es gab
    keinen Eintrag unter `/etc/xdg/autostart/`. Die Doku behauptete damit
    etwas, das es nicht gab - genau die Sorte Lücke, die im selben
    Protokoll bei anderen Dateien aufgeräumt wurde. Nachgeholt als
    `dialos-desktop-stil-wiederherstellen.desktop`.
  - **Das Bluetooth-Headset hing nach dem Neustart in HFP.** Der AIRHUG
    stand auf `headset-head-unit` statt `a2dp-sink`, die Wiedergabe lief
    also dauerhaft in Telefonqualität. Ausgelöst hat das vermutlich die
    Lautstärke-Frage der Start-Ansage, die für die Aufnahme bewusst auf
    HFP umschaltet und danach zurückstellen soll - endet das Skript
    vorher, bleibt das Profil hängen. Von Hand zurückgesetzt; ein
    dauerhafter Riegel dagegen steht in TODO.md.
- **Korrektur zur Mikrofon-Übersteuerung vom 2026-08-16.** Dort steht,
  60 dB Verstärkung hätten die Erkennung unmöglich gemacht. Der
  Zusammenhang ist belegt für den damaligen Moment - Boost zurücknehmen
  behob die Sättigung sofort -, aber **nicht als allgemeine Regel**: Am
  Morgen des 2026-08-17 stand `Internal Mic Boost` wieder auf +30 dB
  (WirePlumber stellt seinen gespeicherten Zustand beim Anmelden wieder
  her, nach dem systemweiten Dienst), und das Signal war trotzdem sauber
  (0,2 % RMS, null gesättigte Werte). Der Pegel-Dienst bleibt richtig und
  hat im Journal nachweislich gearbeitet, aber die Ursachenkette ist
  offenkundig komplexer als beschrieben. Sie gehört sauber untersucht,
  bevor sie als verstanden gilt.
- **`dialosadmin` gehört jetzt zur Gruppe `adm` (Stephans Entscheidung,
  2026-08-16).** Aufgefallen ist die Lücke bei der Fehlersuche am
  übersteuerten Mikrofon: `journalctl -u dialos-mikrofon-pegel.service`
  antwortete mit "-- No entries --", obwohl der Dienst sehr wohl
  protokolliert hatte. Ohne `adm` liest das Admin-Konto keine
  Systemprotokolle - und der naheliegende Fehlschluss "der Dienst tut
  nichts" wäre bei einem Dienst, der genau das Gegenteil tut, teuer
  geworden. `adm` ist Debians Standardgruppe dafür und gibt
  ausschließlich **lesenden** Zugriff auf Protokolle, keine weiteren
  Rechte am System; `systemd-journal` ist nicht nötig, weil systemd
  dieser Gruppe die Journal-Rechte ohnehin einräumt. Gilt bewusst nur
  fürs Admin-Konto - für `nutzer` wären Systemprotokolle nutzlos und nur
  eine zusätzliche Angriffsfläche. Eingebaut als Schritt 3 von 5 in
  `dialos-buero-setup-abschliessen.sh`, wirkt nach dem nächsten
  Anmelden.
- **Das eingebaute Mikrofon war um 60 dB übersteuert - und genau das
  machte den Sprachbefehl wirkungslos (gefunden 2026-08-16).** Stephan
  meldete "Umschalten funktioniert nicht". Der Dienst lief einwandfrei;
  der Fehler saß im Mixer: `Capture` stand auf +30 dB **und**
  zusätzlich `Internal Mic Boost` auf +30 dB. Gemessen 76 % RMS, jeder
  zweite Abtastwert am Anschlag. Die Folge war kein Rauschen, sondern
  **Stille auf der Bedienseite**: Vosk erkennt Sprache an den Pausen
  zwischen den Wörtern, und in einem Dauervollausschlag gibt es keine -
  der Erkenner liefert deshalb nie ein Ergebnis. Nach dem Zurücknehmen
  des Boosts: 2,8 % RMS, null gesättigte Werte, Erkennung läuft (von
  Stephan bestätigt). Dauerhaft gelöst über
  `/usr/local/sbin/dialos-mikrofon-pegel.sh` +
  `dialos-mikrofon-pegel.service`, das die Regler bei jedem Start über
  ihren **Namen** sucht statt über eine gerätespezifische
  Zustandsdatei - so wirkt es auf jedem Gerät, nicht nur auf dem T490.
  Boost bewusst auf Null: Ein zu leises Signal lässt sich nachverstärken,
  ein übersteuertes ist zerstört.
  - **Dieser Fund stellt eine ältere Schlussfolgerung in Frage.** Der
    Mikrofon-Vergleich vom 2026-08-13 ergab, das eingebaute Mikrofon sei
    dem AIRHUG deutlich unterlegen (6 von 8 Sätzen über Bluetooth
    korrekt, eingebaut merklich schwächer). Lagen schon damals 60 dB an,
    hat der Test nicht das Mikrofon gemessen, sondern die Übersteuerung.
    Der Vergleich gehört wiederholt, bevor die Bluetooth-Priorität als
    bewiesen gilt - steht in TODO.md.
  - **Eigener Fehler, der die Suche verzögert hat:** Im Sprachdienst ging
    `stderr` von `parec` nach `/dev/null`, und es gab keine
    Pegelanzeige. Von außen war dadurch nicht zu unterscheiden, ob der
    Dienst nicht zuhört, nichts versteht oder das Mikrofon übersteuert
    ist. Der Dienst hat jetzt einen festen `--debug`-Modus, der Pegel und
    jeden erkannten Satz zeigt - nicht als Wegwerf-Diagnose, sondern
    eingebaut.
- **Falsche Ansage "du musst dich ab- und wieder anmelden" beim
  Umschalten auf Windows (gemeldet und behoben 2026-08-16).** Die
  Prüfung, ob GNOME Shell eine Erweiterung schon kennt, lief über
  `gnome-extensions list` - eine D-Bus-Abfrage an die laufende Shell, und
  sie wurde **für jede Erweiterung einzeln mitten im Umschalten**
  gestellt. Genau dann baut die Shell aber ihre komplette obere Leiste
  neu auf (dash-to-panel ersetzt sie), und die Abfrage kommt zeitweise
  leer zurück. Das Skript hielt eine längst bekannte Erweiterung dann für
  unbekannt und sagte eine Abmeldung an, die gar nicht nötig war. Dass es
  nur in Richtung Windows auftrat, passt dazu: Beim Zurückschalten wird
  nichts geladen, die Shell bleibt ruhig. Jetzt wird die Liste **einmal
  vor der ersten Änderung** aufgenommen, und eine leere Antwort führt zu
  einem zweiten Versuch statt zu einer Schlussfolgerung. Für einen
  blinden Nutzer ist eine falsche Handlungsanweisung schlimmer als gar
  keine.
- **Sprachbefehl für die Desktop-Umschaltung - der erste dauerhaft
  lauschende Dienst in DialOS (Stephans Vorgabe, 2026-08-16).** Bis
  dahin wurde Vosk nur punktuell aufgerufen. `auf Linux umschalten` /
  `auf Windows umschalten` (`auf Gnome umschalten` gilt gleich)
  stellen die Optik jetzt auf Zuruf um, gestartet über
  `/etc/xdg/autostart/`. Damit ist Punkt 4 des Fahrplans - die
  Desktop-Umschaltung als erster echter Sprachbefehl - vorgezogen und
  erreicht.
  - **Der Befehl ist ein ganzer Satz, kein Einzelwort** - Stephans
    Vorgabe, und sie löst ein echtes Problem: Ein einzelnes "Windows"
    fällt im Gespräch ständig, der Schreibtisch würde sich ungefragt
    umstellen, und ein blinder Nutzer wüsste nicht, warum plötzlich
    alles anders klingt. Erkannt wird nur, was **beides** enthält, Ziel
    *und* das Wort "umschalten". Der Gegentest dazu: Der gesprochene
    Satz "ich habe früher windows benutzt" wurde als `auf auf windows`
    erkannt - mit dem Wort "windows", aber ohne "umschalten", und löste
    nichts aus.
  - **Eingeschränkte Grammatik ist Voraussetzung, nicht Optimierung.**
    Frei erkannt machte das deutsche Modell aus "gnome" zuverlässig
    **"genug"**. Mit einer auf die drei Befehlssätze beschränkten
    Grammatik lagen alle wörtlich richtig - geprüft mit synthetisch
    gesprochenen Sätzen (Piper spricht, Vosk hört), derselbe Trick wie
    schon bei der Lautstärke-Abfrage. Nebenbei kostet die kleine
    Grammatik viel weniger Rechenzeit, was bei einem Dauerdienst den
    Akku schont.
  - **Zugehört wird über das eingebaute Mikrofon - anders als bei der
    Lautstärke-Frage, und mit Absicht.** Das AIRHUG kann A2DP und HFP
    nicht gleichzeitig: Bei einer einmaligen Frage ist Telefonqualität
    ein kurzer Moment, bei dauerhaftem Zuhören wäre die Wiedergabe
    **für immer** verschlechtert. Drei feste Sätze zu unterscheiden
    gelingt auch mit dem eingebauten Mikrofon - genau der Vorteil einer
    winzigen Grammatik.
  - **Während das System spricht, wird nicht zugehört.** Sonst hört sich
    der Dienst selbst - und weil seine eigene Ansage Ziel *und*
    "umschalten" enthalten kann, würde die Satz-Bedingung sie gerade
    nicht abfangen. Ausgewertet wird die Markierungsdatei, die
    `dialos-say.py` ohnehin setzt. Dazu eine Sperrfrist von 5 Sekunden.
  - **Keine Rückfrage, aber eine Ansage:** Ein "Willst du wirklich?" bei
    jedem Befehl wäre lästig. Stattdessen sagt das System, was es getan
    hat - wer es nicht wollte, sagt einfach den anderen Satz. Ein
    Fehlgriff ist in Sekunden rücknehmbar, ohne hinsehen zu müssen.
- **Deutsches Startmenü - zweiter Paketfehler in derselben Erweiterung
  (2026-08-16).** Stephan meldete, dass "All Apps" und Konsorten
  englisch bleiben. Ursache: Debians `gnome-shell-extension-arc-menu`
  liefert die fertig übersetzte `de.mo` mit, legt sie aber nach `po/`
  statt in einen `locale`-Ordner. Im GNOME-Quelltext nachgesehen
  (`sharedInternals.js`): Fehlt der `locale`-Ordner, bindet die
  Erweiterung gegen `/usr/share/locale` - also wird die Datei genau
  dorthin kopiert. Kein `msgfmt` nötig, sie ist bereits kompiliert.
  Nachgeprüft, dass es die richtige Datei ist: "All Apps" → "Alle
  Anwendungen", "Frequent Apps" → "Häufige Anwendungen". Ein paar
  Einträge (Power Off, Log Out, Restart, Search) sind auch in der
  Übersetzung des Projekts unübersetzt und bleiben englisch.
  `dash-to-panel` bringt sein Deutsch selbst korrekt mit;
  `tiling-assistant` hat keine Übersetzung, zeigt in der Leiste aber
  auch keinen Text.
- **Die gewählte Optik übersteht Neustart und Abmelden.** Sie tut es
  ohnehin, weil alle Einstellungen in dconf des Kontos liegen -
  zusätzlich läuft jetzt `dialos-desktop-stil.sh wiederherstellen` beim
  Anmelden, ohne Ansage. Das ist die Zusicherung für den Fall, dass
  etwas anderes die Erweiterungsliste zurückgesetzt hat: eine
  Systemaktualisierung, ein versehentliches `dconf reset`, ein neu
  angelegtes Konto. Für einen blinden Nutzer wäre ein Schreibtisch, der
  nach dem Einschalten anders aussieht als zuletzt, kein
  Schönheitsfehler, sondern Orientierungsverlust. Ohne Merkdatei tut der
  Aufruf bewusst nichts, statt ungefragt Einstellungen zurückzusetzen.
- **Windows-11-Optik als umschaltbare Option gebaut (Stephans Wunsch vom
  2026-08-16, umgesetzt am selben Tag).** Anlass: Es gibt Interessenten,
  die DialOS wegen der Sprachsteuerung wollen, aber ihr Leben lang
  Windows benutzt haben. Für die soll der Schreibtisch aussehen wie
  gewohnt - ohne dass DialOS deshalb den barrierefreien GNOME-Unterbau
  (Orca, AT-SPI) aufgibt. Deshalb wird **nichts ersetzt**: GNOME bleibt
  und bekommt drei Erweiterungen obendrauf, die
  `/usr/local/bin/dialos-desktop-stil.sh` in beide Richtungen
  ein- und ausschaltet (`windows` / `gnome` / `status`). Alle drei liegen
  in Debians eigenen Paketquellen - `dash-to-panel` (Taskleiste unten),
  `arc-menu` (Startmenü, Layout `Eleven` ist der Windows-11-Nachbau) und
  `tiling-assistant` (Fenster-Andocken wie Windows-Snap) -, es braucht
  also kein Fremd-Repository, das bei Systemaktualisierungen zur
  Altlast würde.
  - **Mitinstalliert, aber nicht eingeschaltet.** Wer die Umschaltung
    erst bei Bedarf nachinstallieren müsste, bräuchte dafür Internet und
    ein Admin-Passwort - beim Kunden ist beides nicht vorausgesetzt.
  - **Die auffälligste Einzeländerung sind die Fensterknöpfe**
    (`appmenu:minimize,maximize,close`). GNOME zeigt dort ab Werk nur
    einen Schließen-Knopf; das fällt im Alltag mehr auf als die
    Taskleiste. Dazu: heiße Ecke oben links aus, weil sie von
    Windows-Gewohnten ständig versehentlich ausgelöst wird.
  - **Kein `gsettings set` ins Blaue.** Das Skript prüft für jeden
    Schlüssel erst, ob das Schema ihn kennt, und macht sonst weiter
    statt abzubrechen. Ein Fehlschlag mitten in der Umschaltung würde
    einen halb umgestellten Desktop hinterlassen - für einen blinden
    Nutzer nicht selbst zu reparieren. Aus demselben Grund setzt der
    Rückweg alle berührten Schlüssel per `gsettings reset` auf den
    **Auslieferungszustand**, nicht auf selbst gewählte "GNOME-artige"
    Werte: Sonst wäre mehrfaches Hin- und Herschalten nicht verlustfrei.
  - **Die mittige Taskleiste gilt nur für den Hauptbildschirm.**
    dash-to-panel legt sie pro Monitor ab und benutzt seit Version 56 die
    Seriennummer als Schlüssel, fällt aber ausdrücklich auf den
    Bildschirm-Index zurück (`panelSettings.js`, `getMonitorSetting`) -
    deshalb schreibt das Skript auf `"0"`. Bewusst nicht die
    Monitor-Erkennung nachgebaut, nur für eine Kosmetik.
  - **Rückmeldung wird gesprochen, nicht nur geschrieben.** Die
    Zielgruppe sieht den Bildschirm nicht; eine rein geschriebene Meldung
    wäre für sie dasselbe wie gar keine. Genau deshalb ist dieses Skript
    auch der vorgesehene erste echte Sprachbefehl, sobald die
    hassil-Grammatik steht.
  - **Am selben Tag mit installierten Paketen durchgetestet - und der
    Testlauf hat zwei Fehler gefunden, die auf dem Papier nicht sichtbar
    waren.**
    - **Die laufende GNOME Shell kennt frisch installierte Erweiterungen
      nicht.** Sie durchsucht `/usr/share/gnome-shell/extensions` nur
      beim Start; direkt nach `apt install` antwortet
      `gnome-extensions enable` mit "Erweiterung existiert nicht", und
      unter Wayland lässt sich die Shell nicht im Betrieb neu starten.
      Das Skript trug damit zwar alle Einstellungen ein, schaltete aber
      keine einzige Erweiterung ein - es sah aus, als täte der Befehl
      nichts. Jetzt werden die UUIDs immer zusätzlich direkt in
      `org.gnome.shell enabled-extensions` geschrieben (über Gio), und
      der Fall wird erkannt und ausgesprochen: "Sie erscheint erst, wenn
      du dich einmal abmeldest und wieder anmeldest." Für einen blinden
      Nutzer ist genau dieser Satz der Unterschied zwischen "funktioniert
      nicht" und "gleich fertig".
    - **Ein Paketfehler in Debian:**
      `gnome-shell-extension-arc-menu` (65-2) legt sein Schema nach
      `/usr/share/glib-2/schemas/` statt `/usr/share/glib-2.0/schemas/`.
      Es landet dadurch nie im systemweiten Schema-Cache, `gsettings`
      meldet "Kein derartiges Schema", und alle drei
      ArcMenu-Einstellungen wurden still übersprungen - das Startmenü
      wäre im GNOME-Standardlayout erschienen statt im
      Windows-11-Layout. Aufgefallen ist es nur, weil das Skript
      unbekannte Schlüssel meldet, statt sie kommentarlos zu
      überspringen. Das Skript liest die Einstellungen jetzt aus dem
      `schemas`-Ordner der Erweiterung (`GSETTINGS_SCHEMA_DIR`), und
      zwar über alle drei Erweiterungen hinweg gesucht: Behebt Debian
      den Tippfehler, greift automatisch wieder der systemweite Weg.
    - **Eigenes Startknopf-Symbol** (`dialos-fenster-symbolic.svg`,
      Stephans Wunsch): Debian hat sämtliche ArcMenu-Icons aus dem Paket
      entfernt, weshalb der Knopf auf das GNOME-Distro-Icon zurückfiel -
      ausgerechnet das GNOME-Logo in der Windows-Optik. Jetzt liegt dort
      ein generisches Fenster-Sinnbild (Rahmen mit Kreuzsprosse, vier
      Scheiben). **Bewusst nicht Microsofts Windows-Logo:** DialOS wird
      verkauft, und ein fremdes Markenzeichen auf dem Startknopf eines
      verkauften Geräts wäre ein Markenrechtsproblem - ArcMenu selbst
      weist im Quelltext darauf hin, dass seine Distributions-Icons
      Marken ihrer Inhaber sind. Einfarbig und auf `-symbolic.svg`
      endend, damit GNOME es einfärbt und es im hellen wie im dunklen
      Erscheinungsbild lesbar bleibt; ein fest eingefärbtes Icon wäre in
      einem der beiden Fälle unsichtbar. Die Form sind vier Kacheln im
      Quadrat ohne Rahmen (Stephans Wahl) - dieselbe allgemeine Form, die
      GNOME selbst als `view-grid-symbolic` verwendet.
    - **Zwei Anläufe erschienen als volle weiße Fläche auf dem Knopf** -
      ohne Fehlermeldung, ohne Eintrag im Journal. Meine erste Diagnose
      (ausgesparte Flächen per `fill-rule="evenodd"` überstünden das
      Einfärben nicht) war **falsch**: Die zweite Fassung kam ganz ohne
      Aussparungen aus und sah trotzdem genauso aus. Gefunden wurde die
      Ursache erst durch einen Gegentest mit einem Icon, das GNOME
      sicher richtig darstellt (`view-grid-symbolic` aus Adwaita) - das
      erschien korrekt, womit die Datei überführt war und nicht ArcMenu.
      Der einzige strukturelle Unterschied zu Adwaitas Datei: **Bei mir
      stand ein Erklärungs-Kommentar vor dem `<svg>`-Tag.** GNOME baut
      Symbol-Icons beim Einfärben um und stolpert über alles, was davor
      steht. Die Erklärung ist deshalb in eine `README.md` neben die
      Datei gewandert, und die Datei ist jetzt bis auf die Pfaddaten
      Zeile für Zeile identisch mit Adwaitas Aufbau (per `diff`
      gegengeprüft, nicht vermutet).
    - **Zwei Lehren, festgehalten neben der Datei**, damit sie beim
      nächsten Symbol nicht wiederholt werden: Vorlage ist immer eine
      Adwaita-Datei - und **ein selbst gerendertes Vorschaubild beweist
      bei Symbol-Icons nichts.** librsvg zeichnet die Datei so, wie sie
      dasteht, und zeigte sie beide Male korrekt an; GNOME zeichnet sie
      umgefärbt. Ich hatte die Vorschau als Beleg genommen - der Fehler,
      der die zweite Runde überhaupt nötig gemacht hat.
    - Danach dreimal hin- und hergeschaltet und jeden berührten
      Schlüssel verglichen: `gnome` stellt tatsächlich den
      Auslieferungszustand wieder her (`appmenu:close`, heiße Ecke an,
      dash-to-panel und ArcMenu auf `{}` bzw. `Default`), `windows`
      stellt danach wieder exakt dasselbe her, und mehrfaches Ausführen
      erzeugt keine Doppeleinträge in der Erweiterungsliste. Was noch
      aussteht, ist die optische Abnahme nach dem nächsten Anmelden.
- **Alle Markdown-Dateien des Repos gegen den Ist-Zustand geprüft
  (2026-08-16).** Auslöser war Stephans Frage, ob der "Konzept"-Stand
  nicht auch überarbeitet gehört - er traf einen wunden Punkt: Mehrere
  `docs/`-Dateien waren noch in der Sprache der Konzeptphase verfasst,
  obwohl das Beschriebene längst läuft oder gerade nicht läuft.
  Durchgesehen wurden alle 25 (jetzt 24) `.md`-Dateien.
  - **`architektur-uebersicht`**: hieß noch "Live-ISO" und führte den
    Software-Stack unter der Überschrift "Diskussionsstand, noch nicht
    umgesetzt". Beides falsch - DialOS wird seit Weg A pro Gerät aus
    einer regulären Debian-Installation aufgebaut, und der halbe Stack
    läuft. Die Tabelle hat jetzt eine Spalte **Stand** mit drei klaren
    Stufen (installiert / im Einsatz / geplant), damit Entschiedenes
    nicht mehr wie Gebautes aussieht. Nebenbei korrigiert: `live-build`
    als Distributions-Begründung, "Piper oder RHVoice" (Piper ist
    entschieden) und "LLM-gestützte Zuordnung" bei der Intent-Erkennung
    (hassil ist seit dem 13.08. entschieden).
  - **`sprachsteuerung`**: neuer Abschnitt "Stand der Umsetzung" mit dem
    Satz, auf den es ankommt - die Sprach*ausgabe* ist fertig, die
    Sprach*steuerung* im eigentlichen Sinn steht noch aus. Die englische
    Fassung hing zusätzlich hinterher: Sie nannte noch die
    LLM-Zuordnung, während die deutsche längst hassil beschrieb.
  - **`ersteinrichtung`**: sprach vom "generischen Golden Image", das
    vervielfältigt wird - genau das gibt es bei Weg A nicht mehr. Und
    der sprachgeführte Ersteinrichtungs-Assistent ist weiterhin nicht
    gebaut; das steht jetzt dort, zusammen mit dem Hinweis, dass die
    Lautstärke-Frage der Start-Ansage bereits die Vorlage dafür ist.
  - **`telefonie`**: liest sich wie eine Beschreibung des Systems, ist
    aber durchgehend Zielarchitektur - weder ModemManager noch GNOME
    Calls sind installiert, und das Testgerät hat gar kein WWAN-Modul.
    Steht jetzt als Status gleich am Anfang.
  - **`sicherheit-datenschutz`**: die inhaltlich gewichtigsten Funde.
    Es fehlte die **Konto-Sperre ohne Stick** komplett (das Dokument
    behauptete noch, ohne Stick sei "praktisch nur `dialosadmin`
    nutzbar" - genau der Irrtum, den die Sperre behoben hat), es fehlte
    der **verschlüsselte Swap**, und die Stick-Dateisysteme standen als
    "unverändert" statt als ext4/exFAT. Dazu drei Verweise auf das
    entfallene `dialos-install` und "ausgereiftes live-build-Tooling"
    als Begründung, Debian zu behalten. Ergänzt: der Nachweis vom
    2026-08-16 in beide Richtungen.
  - **`offene-punkte`**: die Überschrift "ISO-Build" gab es nicht mehr;
    die Rechtschreibprüfung fehlt nicht wegen der Docker-Chroot-Umgebung
    (die es nicht mehr gibt), sondern weil sie in keiner Paketliste
    steht - damit keine offene Frage mehr, sondern eine Aufgabe.
  - **`scripts/README.md`**: behauptete "noch nicht end-to-end
    getestet" und beschrieb `dialos-claude-setup.sh` als Anleger einer
    passwortlosen Sudoers-Regel für `eggs produce` - das Skript
    *entfernt* diese Regel inzwischen.
  - **`Debian-zu-DialOS`**: Schritt 13 nahm die Vorlage fürs Startsymbol
    aus `dialos-install.desktop` - diese Datei ist gelöscht, tatsächlich
    liegt dort `dialos-rekey.desktop`.
  - **`iso-build/CUBIC-ANLEITUNG.md` gelöscht.** Sie beschrieb den
    Live-ISO-Bau mit `dialos-install`, `dialos-keyscript`,
    initramfs-Hook und Autologin über `/etc/gdm3/custom.conf` - vier
    Dinge, die es nicht mehr gibt oder die nachweislich nicht
    funktionieren. Eine Anleitung, die beim Befolgen in die Irre führt,
    ist schlechter als keine; über die Git-Historie bleibt sie
    erreichbar.
  - **`TODO`**: der mit Stephan vereinbarte Fahrplan zur Sprachsteuerung
    stand nirgends im Repo, ebenso wenig die gewünschte
    Windows-11-Umschaltung. Beides nachgetragen, dazu zwei beim Prüfen
    gefundene Aufgaben (Rechtschreibprüfung; die Lock-Datei von
    `dialos-start-ansage.py` liegt weiterhin im geteilten `/tmp` -
    dieselbe Bauart, die bei der Sprechen-Markierung schon einen stillen
    Fehlschlag verursacht hat).
- **README-Status und Änderungsprotokoll auf den tatsächlichen Stand
  gebracht (2026-08-16).** Der Status-Abschnitt stand noch auf
  "Konzeptphase - es existiert noch keine lauffähige Software"; seit dem
  Neuaufbau desselben Tages war das schlicht falsch. Er nennt jetzt die
  drei Aufbau-Befehle, was nachweislich funktioniert (Sprachausgabe,
  Sicherheitskonzept, Autologin, Standardprogramme) und was fehlt - die
  Sprachsteuerung selbst. Im selben Durchgang das Protokoll geprüft:
  Innerhalb von 0.5.0 hatten spätere Entscheidungen frühere Einträge
  **derselben** Version überholt, ohne dass man das den Einträgen ansah -
  die Stick-Formatierung (FAT32/ext4 → ext4/exFAT), `dialos-install`
  (inzwischen ersatzlos entfallen) und mehrere "steht noch aus"-Vermerke,
  die längst erledigt sind. Diese Einträge sind entfernt bzw. berichtigt
  statt als scheinbar gültige Aussagen stehenzubleiben: Das Protokoll ist
  in diesem Projekt kein Archiv, sondern die Erinnerung, die einen
  Reinstall übersteht - eine überholte Aussage darin richtet mehr Schaden
  an als eine fehlende. In 0.2.0 und 0.4.0 bleiben die Einträge dagegen
  stehen, tragen aber jetzt einen Hinweis, dass der dort beschriebene
  Installationsweg seit 0.5.0 nicht mehr existiert.
- **Acht alte ISOs gelöscht, Abbild-Verzeichnis auf Rescuezilla
  umgestellt (2026-08-16).** Rund 59 GB auf der externen Platte frei
  geworden (danach 486 GB frei). Alle acht stammten aus der
  Penguins-Eggs-Zeit, die am selben Tag entfallen ist, und bildeten
  Systemstände ab, die der Neuaufbau vom 2026-08-16 deutlich überholt
  hat; Prüfsummen lagen für keine davon vor. Stehen geblieben ist einzig
  `DialOS-Live-0.5.1-clone.iso` - sie bleibt bewusst, bis Stephans erstes
  Rescuezilla-Abbild existiert, damit nie der Zustand "gar keine
  Sicherung" eintritt. `docs/iso-builds.md` heißt deshalb jetzt
  "Abbild-Verzeichnis" statt "ISO-Verzeichnis", beschreibt Rescuezilla
  statt `eggs produce` und hält die Löschaktion mit fest.
- **Regel festgelegt: Der Rückfall auf die eingebauten Geräte muss immer
  gewährleistet sein (Stephan, 2026-08-16).** Ein ausgeschaltetes, leeres
  oder nicht verbundenes Headset darf DialOS nie stumm oder taub machen -
  für einen blinden Nutzer wäre genau das der Totalausfall, weil er nicht
  bemerkt, dass das Headset aus ist. Beim Nachprüfen zeigte sich ein
  **Widerspruch zwischen Doku und Code**: `docs/offene-punkte.md` führte
  die Fallback-Umschaltung als "noch nicht implementiert", tatsächlich
  wählt `waehle_mikrofon_fuer_lautstaerke()` längst die erste
  Nicht-Monitor-Quelle, wenn kein `bluez_input` da ist - also das
  eingebaute Mikrofon. Auf der Ausgabeseite zieht PipeWire die
  Standard-Senke selbst um. Der offene Punkt ist damit nicht das Fehlen
  der Logik, sondern dass **beides noch nie ohne Bluetooth getestet
  wurde**; die Doku ist entsprechend korrigiert. **Die Ausgabeseite ist
  noch am selben Tag belegt worden:** Headset ausgeschaltet, Ansage
  gestartet - Ton kam aus dem eingebauten Lautsprecher. Offen bleibt nur
  noch die Eingabeseite, also ob das eingebaute Mikrofon die
  Lautstärke-Frage versteht. Als schwierigerer,
  weiterhin offener Fall benannt: ein Gerät, das *verbunden* ist, aber
  nichts überträgt - dann greift kein Fallback, weil von außen alles in
  Ordnung aussieht.
- **Referenz-Audiogerät festgelegt: AIRHUG 01 (Stephan, 2026-08-16).**
  Damit ist der Hardware-Punkt entschieden, der die Sprachsteuerung
  blockierte - Erkennungsschwellen und Aufnahmedauer gegen ein Mikrofon
  zu justieren, das später wechselt, hieße zweimal arbeiten. Am Gerät
  ausgelesen und in `docs/hardware.md` festgehalten: Klasse `0x00240404`,
  Profile **A2DP** und **HFP**. Der wichtigste Punkt daran ist, dass es
  beide nicht gleichzeitig kann - A2DP hat keinen Mikrofonkanal, HFP
  senkt die Wiedergabequalität. Der Profilwechsel in
  `dialos-start-ansage.py` ist damit keine Eigenart des Codes, sondern
  eine Eigenschaft der Bluetooth-Profile, und wird bei jedem
  vergleichbaren Headset nötig sein. Mit dokumentiert: die
  Eingabegeräte (Logitech Pebble M350s/K380s), deren Akkustand die
  Start-Ansage nur Administratorkonten vorliest.
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
  weiter, das daraus abgeleitet wurde. Die ISO dient nur noch als
  Sicherungs-Schnappschuss (seit Schritt 16 als Rescuezilla-Abbild
  statt `eggs produce`). Erledigt sich damit auch: der offene
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
  `Europe/Berlin`. Der damit verbundene Widerspruch - Calamares setzte
  fest Berlin aus `locale.conf`, während `dialos-install` als
  Klon-Werkzeug das laufende System kopierte und damit Wien vererbte -
  hat sich mit Weg A erledigt: Es gibt nur noch einen Aufbauweg, Wien
  gilt überall.
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
- **`zenity` unter `pkexec`:** Der Datei-Speichern-Dialog für das
  Schlüssel-Backup blieb unter `pkexec` lautlos aus (fehlende
  `DBUS_SESSION_BUS_ADDRESS`/`XDG_RUNTIME_DIR` für den Zugriff auf
  `xdg-desktop-portal`) - `pkexec` reicht die nötigen Umgebungsvariablen
  jetzt durch, echte `zenity`-Fehler werden zusätzlich nicht mehr
  verschluckt. Gefunden an `dialos-install`; das Werkzeug ist seither
  entfallen, der Fix lebt unverändert in
  `dialos-setup-home-partition.sh` weiter, das dessen Logik geerbt hat.
- **Sicherheitsfix Schlüssel-Backup:** `dialos-rekey` und der daraus
  abgeleitete `dialos-setup-home-partition.sh`
  verschlüsselten das Nextcloud-Backup der LUKS-Schlüsseldatei bisher mit
  demselben Wiederherstellungs-Passwort, das auch als zweiter
  LUKS-Schlüssel-Slot dient - wer beides kannte, hätte den Schlüssel ganz
  ohne den physischen Stick entschlüsseln können. Jetzt: eigenes,
  zufällig erzeugtes Backup-Passwort (`openssl rand -base64 32`),
  Passwortübergabe an `openssl` über eine geshredete Temp-Datei statt
  Kommandozeilen-Argument (verhindert Sichtbarkeit in `ps aux`),
  Wiederherstellungs-Passwort braucht jetzt mindestens 12 Zeichen.
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
  Bluetooth-Lautsprecher/Mikrofon installiert, eingebautes Mikrofon als Fallback.
  **Berichtigung:** Der Fallback war entgegen dieser Formulierung längst
  implementiert, nur nie ohne Bluetooth getestet - siehe den Eintrag zur
  Fallback-Regel ganz oben.
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
  zeigt den normalen Login-Screen. Der Zusatz "praktisch nur
  `dialosadmin` nutzbar" stand hier ursprünglich und war falsch - wer
  `nutzer`s Passwort kannte, kam trotzdem hinein. Geschlossen hat das
  erst die Konto-Sperre weiter oben.
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
  (≈62 GB `DIALOS-DATA` nutzbar). Eine Mindestgrößen-Prüfung (~2,5 GB)
  verhindert eine kaputte oder leere Datenpartition bei zu kleinen
  Sticks. Die Stick-Partitionierung wurde
  manuell gegen einen echten 59,8-GB-USB-Stick verifiziert (Labels,
  Dateisysteme, Rechte-Verhalten wie erwartet); der vollständige Aufbau auf echter Hardware ist
  inzwischen durchgelaufen (2026-08-16), allerdings über die drei
  Büro-Skripte - `dialos-install` selbst ist seither entfallen. Details:
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
  hineinsprechen) folgte am 15./16.08. mit Stephans Stimme - siehe den
  Eintrag zur Lautstärke-Abfrage.
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
  jetzt in `Debian-zu-DialOS.md` dokumentiert. Beide neuen Skripte waren zu diesem
  Zeitpunkt nur syntaktisch geprüft; der erste echte Lauf folgte am
  2026-08-16 auf dem neu aufgebauten T490 (siehe weiter oben).
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
  verifiziert - **und seit 0.5.0 gegenstandslos:** Mit Weg A ist
  Calamares ersatzlos entfallen, dieser Schritt wird nie verifiziert
  werden.
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

*Hinweis, nachgetragen am 2026-08-16: Die Einträge dieser Version
beschreiben den Live-Boot-Installationsweg über Calamares und Penguins'
Eggs. Beides ist seit 0.5.0 ersatzlos entfallen - die Einträge bleiben
als Verlauf stehen, taugen aber nicht mehr als Bauanleitung.*

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
