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
- [Lizenzen und Herkunft](docs/lizenzen.md) – was von wem stammt, unter welcher Lizenz, und welche Pflichten beim Weitergeben eines Geräts entstehen

## Lizenz

DialOS steht unter der **GNU General Public License, Version 3** (siehe
[LICENSE](LICENSE)). Wer eine geänderte Fassung weitergibt, muss deren
Quelltext ebenfalls offenlegen – DialOS ist für Menschen gebaut, die auf
Hilfe angewiesen sind, und was daraus entsteht, soll ihnen offen bleiben.

**Ausgenommen sind Name und Erscheinungsbild**: „DialOS", das Logo, das
App-Symbol und die Hintergrundbilder. Umbauen ist erlaubt, das Ergebnis
weiterhin „DialOS" zu nennen nicht – sonst trägt fremde Arbeit einen
Namen, für den jemand anderes einsteht.

Die Lizenz gilt nur für dieses Repository. Debian, GNOME und alle
mitgelieferten Programme behalten ihre eigenen Lizenzen. Was das beim
Weitergeben eines Geräts bedeutet – Quelltext-Pflicht, Markenrecht, die
Lizenzen der Stimmen und Spracherkennungs-Modelle – steht vollständig in
[docs/lizenzen.md](docs/lizenzen.md).

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

## Entstehungsgeschichte

Wie dieses Projekt in dreizehn Tagen entstanden ist - und welche sechs Fehler
es dabei gelehrt hat: [docs/entstehungsgeschichte.md](docs/entstehungsgeschichte.md).
Erzählt als Thriller, weil das Material einen Gegenspieler hat: ein System,
das Erfolg meldet, während es versagt.

## Änderungsprotokoll

### 0.5.1

- **Ein vollstaendiger Befehl mit einem Wort zu viel gilt jetzt** (2026-08-24).
  Die Zuordnung war ein exakter Vergleich; ein Wort zu viel liess den ganzen
  Befehl durchfallen. Grundlage ist Stephans Urteil ueber die Stichprobe: Die
  283 aufgezeichneten befehlslosen Aeusserungen waren ALLE Befehlsversuche.
  21 davon enthielten den kompletten Befehl. Die naheliegende Lockerung
  ("Befehl enthalten genuegt") ist gemessen und VERWORFEN: Sie haette viermal
  aus Wortsalat "einkauf erledigt" ausgefuehrt. Mit einer Grenze von zwei
  Zusatzwoertern: 8 Faelle gerettet, null Salat, Ein- und Ausschalten bewusst
  ausgenommen.

- **Aussprache von "DialOS" pro Stimme entschieden** (2026-08-24, Stephan nach
  Gehoer): Anna sagt "Dial O S", Michael bleibt bei "Dial OS". Die
  Aussprache-Regeln haben dafuer ein viertes Feld bekommen - die Stimmen, fuer
  die sie gelten. Gemessen und dokumentiert, damit es niemand erneut
  durchprobiert: Piper kennt keine MITTLERE Pause. Komma, Semikolon,
  Doppelpunkt, Gedankenstrich und mehrere Leerzeichen ergeben 0 ms Stille, nur
  Satzende-Zeichen erzeugen welche (Punkt 220 ms). Der Punkt traf sogar
  Stephans eigene Sprechpause - an einer Aufnahme seiner Stimme gemessen, 105
  und 180 ms -, machte aber aus dem Wort zwei Saetze.
- **Am Satzende griff die Aussprache-Regel gar nicht** (2026-08-24, beim Umbau
  aufgefallen). Der Lookahead (?!\.) sollte dialos.org schuetzen, schloss aber
  jeden folgenden Punkt aus - also auch den Schlusspunkt. "Willkommen bei
  DialOS." wurde als EIN Wort gelesen, "DialOS ist bereit." dagegen richtig.
  Ausgerechnet der haeufigste Fall war der falsche.

- **Ein stummer `paplay` machte das Geraet lautlos - ohne Fehlermeldung**
  (2026-08-24 gefunden und behoben). Aufgefallen an einer misslungenen
  Hoerprobe: Der paplay-Strom kam stummgeschaltet zur Welt, weil PipeWire
  Lautstaerke und Stummschaltung JE ANWENDUNG merkt. DialOS spielt ueber
  paplay den Frageton, den Testton UND die zwischengespeicherten Ansagen -
  die waren damit alle lautlos, bei Rueckgabewert 0, also ohne dass
  aus_speicher() auf spd-say zurueckgefallen waere. Ursache: dialos-say.py
  schaltet fremde Stroeme stumm und gibt sie im finally frei - das laeuft bei
  SIGTERM aber nicht, und bei zwei kurz aufeinanderfolgenden Ansagen schaltet
  die zweite den paplay der ersten stumm. Behoben durch eine Ausnahme fuer
  eigene Toene und Signalbehandler (Rueckgabewert 143 statt -15 belegt, die
  Sprech-Markierung bleibt nicht mehr liegen).

- **Pegel bei jeder Erkennung im Protokoll** (2026-08-24), und ein Messwerkzeug
  dazu (`scripts/dialos-fehlstart-messen.py`). Zwanzig Minuten Mitschnitt haben
  einen Loesungsweg ausgeschlossen, bevor er gebaut wurde: Vosk lieferte
  `sprachsteuerung` bei Pegel 30 mit Konfidenz 1,000 und `[unk] [unk] starten`
  bei Pegel 28 mit 0,979 - beides LEISER als der Leerlauf von 52, waehrend
  Sprache bei 3475 bis 4196 liegt. Ueber die Konfidenz ist das nicht zu
  filtern: In einer Grammatik mit einem Satz ist der Erkenner
  konstruktionsbedingt sicher. Keiner der Faelle haette eingeschaltet, die
  Regel "Kernwort UND kein [unk]" hat gehalten - das Werkzeug hatte sie im
  ersten Entwurf nicht nachgebildet und vier "Fehlstarts" gemeldet, die keine
  waren.

- **Jede Ansage steht jetzt im Protokoll** (2026-08-24). `dialos-say.py`
  schreibt nach `~/.log/dialos-say.log`. Anlass war eine Beweisluecke: Beim
  Fehlstart um 14:41:12 habe ich behauptet, DialOS habe nicht gesprochen, und
  das mit dem Ton-Protokoll belegt - das aber nur Geraetewechsel aufzeichnet.
  Die Aussage war nicht belegt, nur nicht widerlegt. Der Text wird bei 120
  Zeichen gekuerzt, und zwar aus Datenschutzgruenden: Bei einem
  Vorlese-Befehl waere die Ansage das ganze Dokument.

- **Protokolle tragen jetzt ein Datum** (2026-08-24) - und der Anlass war ein
  Fehlschluss von mir. Zwoelf Skripte schrieben nur die Uhrzeit; logrotate
  dreht taeglich, aber nur bei laufendem Geraet, also lagen drei Tage in einer
  Datei. Ich habe daraus einen Verlauf "von heute" rekonstruiert und Stephan
  einen Vorfall geschildert, den es an dem Tag nie gab. Aufgefallen ist es nur,
  weil er sagte, er habe gar nicht mit der Sprachsteuerung gesprochen.
- **Erster Fehlstart der Sprachsteuerung** (2026-08-24, Ursache offen). Um
  14:41:12 erkannte Vosk "sprachsteuerung starten", ohne dass jemand mit dem
  Geraet sprach; die eigene Ansage ist ausgeschlossen, das Ton-Protokoll ist in
  dem Fenster leer. Die dokumentierten "null Fehlstarts" sind damit ueberholt.
  Eigener Punkt in TODO.md - erst klaeren, was das Mikrofon gehoert hat, dann
  bauen.

- **Die Stimmwahl wurde beim Aufspielen stillschweigend zurueckgesetzt**
  (2026-08-24 gefunden und behoben). `piper-generic.conf` enthaelt sowohl
  Konfiguration als auch die vom Nutzer gewaehlte Stimme; `dialos-aufspielen`
  ueberschrieb sie mit der Repo-Fassung. Stephans Wahl von Michael vom 22.08.
  war damit weg, waehrend die Namensdatei weiter "Michael" sagte - das Geraet
  haette sich mit Annas Stimme als Michael vorgestellt. Die Datei steht jetzt
  in der Ausschlussliste, und das Skript MELDET, was es uebergangen hat: nach
  Grund gruppiert, weil der erste Entwurf 29 Zeilen ausgab und die eine
  wichtige unter 20 Zeilen Python-Bytecode begrub.
- **Kein Stick fuer das Admin-Konto** (2026-08-24, Stephans Entscheidung). Der
  Ordner `~/Dokumente/Archiv/DialOS-DATA/` ist dort das Archiv selbst. Vorher
  meldete das Archiv alle 16 Minuten einen nicht beschreibbaren Stick - exFAT
  gehoert dem Konto, das es einhaengt, und das war `nutzer`. Fuer den Nutzer
  bleibt die Meldung: dort entsteht ohne Stick keine Sicherungskopie.

- **Lizenz: GPL-3.0, dazu eine Bestandsaufnahme aller fremden Bestandteile**
  (2026-08-23, Stephans Entscheidung). DialOS war oeffentlich, aber ohne
  Lizenzdatei - und das heisst nicht "frei", sondern das Gegenteil: volles
  Urheberrecht, sichtbar, aber niemand darf es benutzen, aendern oder
  weitergeben. Stephan hat sich fuer Copyleft entschieden, damit ein Ableger
  von DialOS offen bleiben muss. Name, Logo, App-Symbol und Hintergrundbilder
  sind ausdruecklich ausgenommen, wie es Debian, Firefox und Ubuntu auch
  halten: umbauen ja, weiterhin "DialOS" nennen nein.
  Neu ist [docs/lizenzen.md](docs/lizenzen.md) (+ `.en.md`) mit dem, was beim
  Weitergeben eines verkauften Geraets wirklich zaehlt: die Quelltext-Pflicht
  aus der GPL (erfuellt, solange Debian-Pakete unveraendert bleiben - deshalb
  legt DialOS eigene Skripte daneben, statt fremde Pakete zu patchen), der
  Hinweis, dass `/usr/share/doc/` die Lizenznachweise traegt und beim
  Aufraeumen nicht geloescht werden darf, und die Marken von Debian, GNOME
  und Mozilla. **Die Lizenzen der Stimmen und Erkenner sind nachgelesen, nicht
  geschaetzt:** Piper-Datensaetze `kerstin` und `thorsten` sind CC0, die
  Vosk-Modelle `de-0.21`, `small-de-0.15` und `de-tuda-0.6-900k` Apache 2.0 -
  alle vier duerfen auf verkauften Geraeten ausgeliefert werden. Der schon
  bekannte Gegenfall (openWakeWord, CC BY-NC-SA) steht dort jetzt mit
  Begruendung, damit ihn niemand ein zweites Mal pruefen muss.
- **Zwei Tastenkombinationen fuers Admin-Konto** (2026-08-22, Stephans
  Wunsch). `Strg`+`Alt`+`W` schaltet die Optik zwischen Linux und Windows 11,
  `Strg`+`Alt`+`S` die Stimme zwischen Michael und Anna. Beide Skripte
  schalten jetzt UM, statt ein Ziel zu verlangen. Die Stimme brauchte dafuer
  ein eigenes Skript: `setzen` schreibt nur die Konfiguration und ueberlaesst
  den Neustart von speech-dispatcher dem Menschen - hinter einer Taste ist das
  keine Loesung. Gemessen: 4,4 Sekunden bis zur Ansage in der neuen Stimme.
  Nur fuer `dialosadmin` - das Nutzerkonto bedient beides ueber die Stimme.

- **Ausdruck kam quer statt hochkant** (2026-08-22). Papier und Ausrichtung
  werden jetzt im Auftrag mitgegeben (`-o media=A4 -o
  orientation-requested=3`) statt der Voreinstellung ueberlassen. Gemessen
  ist, dass CUPS nicht schuld war: Filterweg und Drucker melden beide A4
  hochkant. Dabei fiel auf, dass `dialos-fusszeile.py drucken` `lp` ohne Ziel
  aufrief - auf einem Geraet ohne Systemvoreinstellung haette das nie
  funktioniert. Der Nachtest zeigte einen zweiten Fehler: Vosk verstand
  "notiz drucken", die Grammatik kannte nur "notizen drucken", und der Befehl
  fiel lautlos durch. Die Einzahl ist jetzt zweite Formulierung.

*In Arbeit seit 2026-08-17. Alles, was ab jetzt entsteht, wird hier
eingetragen - 0.5.0 ist mit dem Sprachbefehl für die Desktop-Umschaltung
abgeschlossen.*

- **Bildschirmfoto auf Zuruf (Stephan, 2026-08-21).** „Bildschirmfoto
  erstellen" oder „Bildschirmfoto machen". Alle 21 Grammatiksätze danach von
  Piper gesprochen und von Vosk wörtlich erkannt.
    - **Das Mitschrift-Fenster ist nicht mit auf dem Bild** (Stephans
      Nachtrag). Es ist DialOS' eigene Anzeige - ein Terminal mit hundert
      Spalten mitten auf dem Schirm - und verdeckt auf einem Support-Foto
      genau das, was der Helfer sehen will. Der Dienst schließt es deshalb
      **vor** dem Foto und öffnet es danach wieder; das kostet rund vier
      Sekunden, in denen die Erkennung steht. Vertretbar, weil der Nutzer
      gerade selbst einen Befehl gesprochen hat und ohnehin auf die Ansage
      wartet. Wieder geöffnet wird nur, wenn vorher eines lief - wer die
      Mitschrift abgeschaltet hat, bekommt sie nicht durch ein
      Bildschirmfoto zurück.
    - **Nicht für den Nutzer, sondern für den Support.** Er sieht das Bild
      nicht. Aber „was steht da gerade?" lässt sich ohne ein Foto nicht
      beantworten, wenn niemand danebensitzt.
    - **Das Gerät konnte gar keine Bildschirmfotos.** Geprüft: weder
      `gnome-screenshot` noch `grim`, `scrot`, `spectacle` oder `flameshot`
      sind installiert; `xwd` ist X11 und unter Wayland nutzlos.
    - **Und die naheliegende Schnittstelle ist gesperrt.**
      `org.gnome.Shell.Screenshot` antwortet mit
      `AccessDenied: Screenshot is not allowed` - GNOME 48 behält sie der
      Shell selbst vor.
    - **Der Weg ist das XDG-Portal, und die entscheidende Eigenschaft ist
      `interactive: false`:** Es liefert das Bild **ohne Rückfrage**. Ein
      Dialog, den der Nutzer bestätigen müsste, wäre auf diesem Gerät dasselbe
      wie gar keine Funktion. Geprüft, Antwortcode 0, echtes PNG mit
      1920 × 1080.
    - **Den Namen vergibt DialOS, nicht das Portal.** Das Portal legt
      `Screenshot.png` an und zählt hoch. Wer im Support drei Bilder bekommt,
      will wissen, welches wann entstand - deshalb
      `bildschirmfoto-2026-08-21-144048.png` im Ordner `Bildschirmfotos`, den
      GNOME dafür ohnehin vorsieht.

- **Der Brief-Weg: gebaut, gemessen - und an einer Stelle noch offen
  (2026-08-21).** Stephans Wunsch, den Brief anzugehen. Entstanden ist ein
  vollständiger Weg von der Sprache zum fertigen Briefbogen; **nicht gelöst**
  ist, dass sich das Diktat mitten im Satz selbst beendet.
    - **Drei neue Sprachbefehle:** „Brief aufnehmen", „Brief schreiben"
      (Stephan wollte beide Formulierungen) und „Brief vorlesen". Alle 19
      Sätze der Grammatik von Piper gesprochen und von Vosk wörtlich erkannt.
    - **Der Brief geht nach `~/Dokumente/brief.txt`,** nicht in den
      Notizordner: Eine Notiz wird bei jedem Diktat ergänzt, ein Brief ist ein
      fertiges Stück. Ein vorhandener Brief wird mit Datum und Uhrzeit im
      Namen beiseitegelegt, nicht überschrieben.
    - **Briefbogen aus reinem Text** - Absender und Datum rechtsbündig, Text
      auf dieselbe Breite 76 umgebrochen, Fußzeile unten rechts. Monatsnamen
      und Fußzeilensatz werden aus den vorhandenen Skripten **geholt, nicht
      abgeschrieben**. Die Anschrift steht bewusst nicht im Abbild; fehlt
      `absender.txt`, fällt der Block weg.
    - **Hinweis auf die fehlende Unterschrift** (Stephans Wunsch), dort wo der
      Empfänger sie sucht. **Nicht** „ohne Unterschrift gültig" - das wäre eine
      rechtliche Aussage, und bei Schriftform-Erfordernis ist sie falsch.
    - **Vorgelesen wird alles**, mit benannten Teilen („Absender:", „Datum:",
      „Fußzeile:"). Mein erster Entwurf ließ Kopf und Fußzeile weg; Stephans
      Einwand: „Es sollte immer alles vorgelesen werden oder?" Er hat recht -
      was der Nutzer nicht hört, existiert für ihn nicht.
    - **Gesprochene Satzzeichen, zweimal gemessen und einmal verworfen.** Die
      nackten Wörter („Komma", „Punkt") kamen bei Stephans Stimme auf **drei
      von sechs**: `komma` → `komme`, `punkt` → `kommt`, `doppelpunkt` →
      `dörte depots`. Die zweiwortigen Formen („Komma setzen", „Punkt setzen")
      trafen **dreimal von drei**. Damit entfiel auch der Preis, den Stephan
      vorher akzeptiert hatte: „in diesem Punkt" bleibt jetzt stehen.
    - **Stille erzeugte Text.** In 80 Sekunden Ruhe erfand das große Modell
      **sieben Wörter** - „köln", „einen gefunden", „vom". Die landeten im
      Brief. Ein Pegel-Tor bei Mittelwert 150 trennt sauber: Rauschen liegt bei
      47-84, Sprache bei 3475-4196. Live belegt: „köln" mit Pegel 37 und „ln"
      mit 33 wurden aussortiert.
    - **Der schwerste Fehler war von Anfang an da: `FinalResult()` fehlte.**
      Vosk liefert erst an einer Sprechpause ab. Wer den Brief in einem Zug
      spricht und dann „Diktat beenden" sagt, hat beides in **derselben**
      Pause - der Schluss brach die Schleife ab, und der gesammelte Text war
      weg. Im Protokoll stand „0 Äußerungen", obwohl ein ganzer Brief
      gesprochen worden war. Aufgefallen ist es nie, weil man beim
      Einkaufszettel zwischen den Waren Pausen macht.
    - **Und der Notausgang war ebenfalls defekt.** Die Zwei-Minuten-Zeitgrenze
      konnte nie greifen: Jedes `[unk]` aus Raumgeräusch setzte die Stille-Uhr
      zurück. Ein Diktat lief neun Minuten weiter, hielt die Marke „ein anderer
      Dienst hört zu" - und Stephan konnte die Sprachsteuerung nicht mehr
      starten. Ausgerechnet die Geisterwörter, die das neue Pegel-Tor beim
      Schreiben aussortiert, hielten es am Leben.
    - **OFFEN und der Grund, warum der Weg noch nicht benutzbar ist:** Der
      Schluss-Erkenner macht aus laufender Rede ein „diktat beenden".
      Gemessen mit Piper: aus 30 Sekunden Brieftext entstehen im Sekundentakt
      Bruchstücke - `'beenden'` bei 8,4 s, `'diktat'` bei 4,8 s,
      `'beenden [unk]'` bei 18,2 s. Ausgezählt über den Tag: **sechs
      Fehlauslöser, alle aus nacktem „beenden"** - deshalb verlangt der Schluss
      jetzt beide Wörter. Das reicht nicht: Am selben Tag entstand zweimal ein
      sauberes „diktat beenden" aus reiner Rede, und Stephans Urteil dazu ist
      das Maß: **„Diesen Text kann ich nie zu Ende bringen."**
    - **Zur Arbeitsweise, weil es zum Ergebnis gehört:** Ich habe die
      Schlusserkennung an einem Nachmittag **viermal** geflickt - Sperrfrist,
      Pegel-Tor, beide Wörter, Ansage - und jedes Mal hat der nächste Test die
      nächste Lücke gefunden. Zwei meiner Erklärungen (Umgebungsgeräusch, die
      eigene Ansage) waren gemessen **falsch**, und eine der Reparaturen - die
      Ansage „Sage bitte: Diktat beenden." - unterbrach Stephan mitten im
      Diktieren und musste noch am selben Tag zurückgebaut werden. Der nächste
      Schritt ist deshalb festgelegt: **Sprechpause als Bedingung, offline
      gegen Piper geprüft, bevor Stephan wieder testet.**

- **Drei Akkuwarnungen - und die Hörbeispiele sprachen noch mit der alten
  Stimme (2026-08-21).** Stephans Vorgabe: Warnungen bei 25 %, 15 % und 5 %,
  „bei der letzten mit einer Ansage, das Gerät muss an die Netzdose".
    - **Und der Takt war zu langsam - nicht für den Akku, für die**
      **Bestätigung.** Stephan zog das Kabel und steckte es in unter einer
      Minute wieder ein: Bei 60 s Takt lag zwischen zwei Blicken kein
      einziger, bei dem es getrennt war - **in 130 s kam keine einzige
      Protokollzeile**. Für die Warnungen wäre das egal (von 25 % auf 15 %
      vergehen Stunden), für „Der Computer hängt am Netz und lädt." nicht:
      Wer nicht sieht, ob der Stecker sitzt, wartete bis zu einer Minute.
      Jetzt 10 s, und die beiden früheren Takte sind ersatzlos entfallen -
      ein Sonderfall weniger.
    - **Das Wiedereinstecken stand nicht im Protokoll** - gefunden, weil
      Stephan das Kabel zum Ausprobieren zog und wieder einsteckte. Da stand
      „Netz getrennt bei 77 %" und kein Ende dazu: Die Zeile fürs Einstecken
      schrieb ich nur, wenn vorher gewarnt worden war. Jetzt wird **jeder**
      Wechsel protokolliert, in beide Richtungen. Geprüft wurde die Kette
      gegen eine **nachgebaute Stromversorgung** statt gegen einen echten
      leeren Akku - inklusive Sprung von 60 % direkt auf 3 %.
    - **„Computer" statt „Gerät"** (Stephans Nachtrag am selben Tag: „Wir
      meinen bei Gerät ja das Laptop bzw. den Computer"). Gilt überall, wo
      DialOS spricht - fünf Ansagen, drei beim Akku und zwei in der
      Fernwartung. „Gerät" ist das Wort eines Technikers; wer nicht sieht,
      worüber gesprochen wird, braucht das Wort, das er selbst benutzt. Dabei
      ändert sich das Geschlecht mit: aus „das Gerät" wird „der Computer",
      aus „das Gerät bedienen" ein „den Computer bedienen". Eine reine
      Wortersetzung hätte falsche Artikel hinterlassen.
    - **Warum GNOME das nicht schon erledigt:** Es warnt mit einer
      Bildschirmmeldung. Der Nutzer sieht sie nicht. Für ihn fährt das Gerät
      ohne Vorwarnung herunter, mitten im Satz - und ein leerer Akku ist für
      ihn schwerer zu deuten als fast jeder andere Fehler, weil das Gerät
      einfach nicht mehr antwortet.
    - **Drei Stufen, drei Tonfälle:** bei 25 % eine Feststellung, bei 15 % ein
      Rat, bei 5 % eine Aufforderung **mit Namen**. Dreimal derselbe Satz wäre
      dreimal dasselbe Gewicht, und für den Ernstfall bliebe keine Steigerung.
      Gesprochen wird „Steckdose" statt „Netzdose" - die Ansage kommt in dem
      Moment, in dem wenig Zeit bleibt, und muss auf Anhieb sitzen.
    - **Über die Netzteil-Anzeige, nicht über den Akkustatus.** `BAT0/status`
      meldete `Not charging`, während das Netzteil steckte: Eine Ladeschwelle
      hält den Akku bei 78 %. Wer „nicht am Laden" mit „am Akku" gleichsetzt,
      warnt bei gestecktem Kabel.
    - **Übersprungene Stufen gelten als erledigt.** Fällt das Gerät im
      Ruhezustand von 30 % auf 4 %, ist „fast leer" die richtige Ansage und
      nicht „25 Prozent". Während eines Diktats warten 25 % und 15 %; die 5 %
      sprechen trotzdem - ein unterbrochener Satz ist besser als ein Gerät, das
      mitten im Brief ausgeht.
    - **Ein Fehler, den ich beim Schreiben der Ansagen fast gemacht hätte:**
      „Das Geraet muss an die Steckdose" - im Projekt sind Bezeichner und
      Kommentare ASCII, **gesprochene Texte tragen echte Umlaute**. Piper hätte
      „Ge-ra-et" gesagt, ausgerechnet in der dringendsten Ansage. Gefunden beim
      Vergleich mit den vorhandenen Ansagen, vor dem ersten Sprechen.
    - **Und ein Fehler, der schon einen Tag alt war:** Im Erzeuger der
      Hörbeispiele stand die Stimme **fest eingetragen**
      (`de_DE-thorsten-high`), während seit dem 2026-08-20 Anna ausgeliefert
      wird. Alle 15 Beispiele im Repo waren also noch Michael - unbemerkt, weil
      sie für sich genommen richtig klingen. Exakt die Falle, die der Kommentar
      bei `tempo()` **eine Zeile darunter** beschreibt und die dort schon
      behoben war. Stimme und Tempo kommen jetzt beide aus
      `piper-generic.conf`; alle 19 Beispiele sind neu erzeugt, und die Dauern
      in der Tabelle wurden aus den Dateien gelesen statt abgeschrieben.

- **Das Gerät schlief von allein ein - und sperrte den Nutzer aus
  (2026-08-21).** Beide Funde kamen beim Vorbereiten der Nachtmessung, und
  beide betreffen das Produkt, nicht den Test.
    - **Standby:** Ab Werk schläft GNOME nach 900 s ohne Tastatur- oder
      Mauseingabe ein, am Netz wie im Akkubetrieb. Belegt im Systemprotokoll:
      zweimal `Starting systemd-suspend.service`, während DialOS lief (16:26
      und 18:20 am 2026-08-20). **Sprache setzt GNOMEs Untätigkeits-Zähler
      nicht zurück** - das tun nur Eingabegeräte, und keiner der zehn
      Inhibitoren blockiert. Ein blinder Nutzer, der eine Viertelstunde nichts
      anfasst und dann „Sprachsteuerung starten" sagt, bekäme keine Reaktion
      und sähe nicht, warum. Am Netz jetzt `'nothing'`, im Akku Standby nach 30
      statt 15 Minuten.
    - **Sperre:** `lock-enabled=true` bei `lock-delay=0` - Sperre in dem
      Moment, in dem der Bildschirm dunkel wird. Mit Autologin wäre der Nutzer
      nach fünf Minuten aus seinem eigenen Gerät ausgesperrt. Für einen
      motorisch eingeschränkten Menschen ist genau das der Grund, warum es
      DialOS gibt. Die Tür ist die LUKS-Vollverschlüsselung, nicht der
      Sperrbildschirm; für `dialosadmin` bleibt sie einzeln eingeschaltet.
    - **Der Bildschirm darf weiter dunkel werden** (Stephans Entscheidung) - er
      stoppt nichts und spart Strom. Ausdrücklich gesetzt statt geerbt: Ein
      geerbter Wert ist keine Entscheidung und kann beim nächsten
      GNOME-Sprung anders lauten.

- **Die Fußzeile war gebaut, aber niemand rief sie auf (2026-08-20).**
  Stephan: „ich habe gestern mal eine Mail geschickt und da ist die Zeile
  nicht drin gewesen!" Sie **konnte** nicht drin sein. `dialos-fusszeile.py`
  war einen Tag zuvor gebaut, dokumentiert und mit einer einzigen Textquelle
  sauber entworfen - nur rief kein einziges Programm es auf. Ein Werkzeug ohne
  Benutzer. Im Thunderbird-Profil standen null Signatur-Einträge. **Eine
  Vorgabe ist nicht erfüllt, weil das Werkzeug dafür existiert, sondern erst,
  wenn etwas es benutzt** - und genau diese letzte Verbindung fehlte, ohne
  dass es beim Bauen oder beim Dokumentieren aufgefallen wäre.
    - **`dialos-fusszeile.py signatur`** erzeugt `mail-signatur.html` und
      `mail-signatur.txt` aus `fusszeile.txt`. Thunderbird kann eine Signatur
      nur aus einer **Datei** lesen, nicht aus einem Programm - diese Datei ist
      damit eine zweite Stelle, an der der Satz steht, also genau die Kopie,
      die der Entwurf vermeiden wollte.
    - **Deshalb wird sie nie von Hand gepflegt.** `dialos-fusszeile.path`
      beobachtet die Textquelle und lässt sie neu erzeugen, sobald sich der
      Satz ändert. Änderst du den Satz, sind Briefe, Ausdrucke **und** Mails
      sofort umgestellt. Ohne das wäre die Kopie irgendwann still veraltet -
      dieselbe Falle, die der Entwurf für den Code schon vermieden hatte.
    - **`dialos-mail-signatur.py` schreibt in `user.js`, nicht in `prefs.js`.**
      Thunderbird schreibt `prefs.js` beim Beenden neu und verlöre einen
      Fremdeintrag; `user.js` wird bei jedem Start darüber gelegt. Preis: In
      den Kontoeinstellungen lässt sie sich nicht dauerhaft abschalten - für
      eine Herkunftsangabe, die in **jeder** Mail stehen soll, ist das richtig
      herum. Gesetzt wird sie für jede Identität, die das Profil kennt.
    - **Zwei Formate.** Das Profil verfasst in HTML, und nur dort geht „dezent
      und rechtsbündig" sauber - im reinen Text ginge es nur über Leerzeichen,
      die auf einem Telefon umbrechen. Die `.txt` liegt daneben, falls ein
      Konto in reinem Text schreibt; dann wird umgestellt statt gebaut.
    - **Der Name ist anklickbar** (Stephans Nachfrage am selben Tag). In der
      HTML-Fassung führt „DialOS.org“ auf `https://dialos.org` - kanonisch
      ohne „www“, denn `www.dialos.org` leitet mit 301 dorthin um. Der
      Verweis erbt die Farbe der Zeile und ist nur unterstrichen: Das übliche
      Linkblau wäre in einer Zeile, die „ganz dezent“ sein soll, das Lauteste
      auf der Seite - ohne Unterstreichung sähe umgekehrt niemand, dass es
      ein Verweis ist. Die `.txt` bleibt ohne Adresse; im reinen Text wäre sie
      eine zweite Fassung desselben Satzes, die niemand anklicken kann.
    - **Was das *nicht* löst:** Laut `docs/anwendungen.md` ist Thunderbird die
      Oberfläche, nicht der Motor - DialOS soll später selbst über IMAP/SMTP
      versenden. Die Signatur greift nur bei Mails, die durch Thunderbird
      gehen, also bei denen des sehenden Helfers. Der eigene Versandweg muss
      sich die Zeile selbst holen; der Hinweis steht jetzt in `TODO.md` an
      genau der Stelle, an der dieser Weg gebaut wird.

- **Der Name des Nutzers klang falsch - und die Aussprache gehört in die
  Namensdatei, nicht in die Regeltabelle (2026-08-20).** Stephans Beobachtung:
  „Michael sagt Stefffan". Der Name wird bei **jeder** Begrüßung, jeder
  Rückfrage und jedem Fehler gesagt - falsch ausgesprochen stört er mehr als
  jedes andere Wort.
    - **`nutzer-name.txt` hat jetzt zwei Felder:** `Stephan | Stefan`.
      Geschrieben bleibt „Stephan" - für Briefe und Ausdrucke, wo „Stefan"
      schlicht falsch wäre. Gesprochen wird das zweite Feld. Fehlt es, gilt das
      erste für beides.
    - **Warum nicht in die Aussprache-Tabelle** von `dialos-say.py`, wo
      „Tastatur" und „ID" stehen: Dort gelten Regeln für **alle** Geräte. Ein
      Kundenname gilt für **eines**. Eine Regel pro Kunde wäre in einem Jahr
      eine Liste von Namen fremder Leute im Repo - und beim nächsten Kunden
      wieder falsch. Die Aussprache gehört dorthin, wo der Name steht.
    - **Das hätte ich allein nicht gefunden.** Ich hatte die Namensanrede an
      drei Ansagen geprüft und für fertig erklärt; dass der Name selbst falsch
      klingt, hört nur, wer ihn kennt.
    - Randfälle gegengeprüft: Unsinn im zweiten Feld fällt auf den geschriebenen
      Namen zurück, Kommentarzeilen in der Datei sind erlaubt, leere Datei
      ergibt weiter das schlichte „Du".

- **30 → 7 → 3: das Einschalten verlangt jetzt beide Wörter, und ohne Befehl
  ist nach 30 Sekunden Schluss (2026-08-20 abends).** Zwei kleine Änderungen
  anstelle des Aufweckworts - beide an denselben zwei Stunden Betriebsdaten
  gerechnet.
    - **„Sprachsteuerung starten" braucht beide Wörter.** `'starten'` allein
      hatte 27-mal ausgelöst, `'sprachsteuerung'` allein viermal - und auf
      **keine** der sieben Einschaltungen folgte ein Befehl. Aus 30 möglichen
      Fehlstarts werden **3**, und die drei sind genau die echten Versuche. Zwei
      bestimmte Wörter hintereinander fallen im Gespräch praktisch nicht.
    - **Zwei Fristen statt einer:** 30 Sekunden, solange **kein** Befehl kam,
      danach die vollen zwei Minuten. Heute liefen alle 7 Einschaltungen in die
      120 s - zusammen 14 Minuten scharfe Befehlsgrammatik, die niemand wollte;
      mit der kurzen Frist wären es 3,5 gewesen.
    - **Und zwei verschiedene Ansagen dazu.** Nach einem Gespräch die
      Begründung („Du hast mir eine Weile nichts gesagt"), sonst nur das kurze
      „Ich höre Dir nicht mehr zu." Eine lange Erklärung für etwas, das der
      Nutzer nie ausgelöst hat, ist selbst nur Lärm.
    - **Warum das statt des Aufweckworts:** openWakeWords fertige Modelle sind
      **CC BY-NC-SA** - nicht kommerziell, und DialOS wird verkauft. Ein eigenes
      Modell ist möglich (Code und Googles Einbettung sind Apache 2.0), aber die
      Trainingsdaten entscheiden über die Verkäuflichkeit: Genau daran sind die
      mitgelieferten Modelle gescheitert. Das ist ein Projekt von Tagen, nicht
      von Stunden - und **ein Aufweckwort schließt das Mikrofon ohnehin nicht**,
      es muss zuhören, um das Weckwort zu hören. Diese zwei Änderungen bringen
      heute mehr und machen die Messung für später besser.
    - **Im Betrieb bestätigt (2026-08-21 früh).** Die Zahlen oben waren
      *gerechnet* - dieselben zwei Stunden Daten durch beide Regeln geschickt.
      Jetzt liegen sie *gemessen* vor: **2 h 19 min** Zuhörzeit am Abend des
      2026-08-20 (Dienststart 16:45:06 bis zum Herunterfahren um 19:04:39; das
      Gerät lief **nicht** über Nacht). **46-mal** `'starten'` allein,
      **7-mal** `'sprachsteuerung'` allein, **7-mal** `'[unk] starten'` - also
      **60 Beinahe-Treffer und null Fehlstarts**. Alle sieben Einschaltungen
      kamen mit dem vollen Satz und waren Stephans Tests. Die Vorhersage „zwei
      bestimmte Wörter hintereinander fallen im Gespräch praktisch nicht" hat
      im Feld gehalten. Das sind rund **26 Beinahe-Treffer je Stunde** -
      Umgebungsgeräusch, das die alte Regel eingeschaltet hätte.

      **Nachtrag vom 2026-08-24:** Der erste Fehlstart ist da. Um 14:41:12
      erkannte Vosk „sprachsteuerung starten", ohne dass jemand mit dem Gerät
      gesprochen hatte. Die Messung oben bleibt richtig für ihr Fenster von
      2 h 19 min - sie war nur zu kurz, um diesen Fall zu enthalten. Siehe
      `TODO.md`.
    - **Auch die kurze Frist greift.** Am Vortag liefen **alle** sieben
      Einschaltungen in die 120 s. Jetzt endeten **6 von 8** nach 30 Sekunden
      und nur 2 nach 120 - das sind 9 Minuten weniger scharfe
      Befehlsgrammatik an einem einzigen Testtag.

- **Die Kernwort-Umstellung ist im Betrieb gemessen - 30 gegen 7 (2026-08-20).**
  Zwei Stunden Protokoll aus dem laufenden Gerät, **dieselben Daten durch beide
  Regeln** gerechnet:
    - `'starten'` allein wurde **27-mal** erkannt - reines Umgebungsgeräusch.
    - Die alte Regel hätte **30-mal** eingeschaltet, die neue hat **7-mal**
      eingeschaltet. Ersparnis: **23 Einschaltungen à zwei Minuten = 46 Minuten
      offenes Mikrofon** in gut zwei Stunden.
    - Das ist eine bessere Messung als die vom Vormittag, weil sie nicht zwei
      Zeiträume vergleicht, sondern eine Datenbasis durch beide Regeln schickt.
    - **Und sie zeigt die Grenze:** 7 Einschaltungen, 7 Zeitgrenzen-Abschaltungen
      - auf keine einzige folgte ein Befehl. Auch die 7 waren also überwiegend
      Geräusch, vor allem die vier mit `'sprachsteuerung'` allein. Die Umstellung
      drückt das Problem um gut drei Viertel, sie löst es nicht. Der eigentliche
      Weg bleibt das Aufweckwort (`TODO.md`).
    - **Eigener Fehler dabei:** Mein Neustart-Werkzeug legte das Protokoll immer
      unter demselben Namen beiseite und hat beim zweiten Lauf die erste
      Sicherung überschrieben - die Rohdaten der 157 Äußerungen vom Vormittag
      sind weg. Das Ergebnis steht in den Commits, die Daten nicht. Das Werkzeug
      legt jetzt gar nichts mehr beiseite: Seit heute räumt logrotate die
      Protokolle auf, und ein zweiter Mechanismus daneben schafft nur
      Namenskollisionen.

- **Anna ist die neue Stimme von DialOS (2026-08-20).** Stephans Entscheidung:
  eine freundliche Damenstimme. Aus dem Hörvergleich dreier Piper-Stimmen wurde
  **`de_DE-kerstin-low`** mit Tempo **1,00**, Name **Anna** - und seit dieser
  Änderung auch die **Auslieferungsstimme** in der Vorlage, nicht nur auf dem
  Testgerät.
    - **Drei Dinge schalten zusammen um** (`dialos-stimme.py setzen kerstin`):
      Stimme, Name und Tempo. Einzeln wäre jedes falsch - eine Frauenstimme, die
      sich als Michael vorstellt, ebenso wie ein Tempo, das zur vorigen Stimme
      gehört.
    - **Das Tempo ist pro Stimme verschieden, und zwar messbar:** derselbe Satz
      **Diese Zahlen waren falsch** (berichtigt am 2026-08-22): Sie stammen
      aus einem Erzeuger, der Kerstins 16-kHz-Rohdaten als 22050 Hz
      deklarierte - jede Kerstin-Probe lief damit 38 % zu schnell. Richtig
      gemessen braucht derselbe Satz bei Michael mit 0,88 rund 6,15 s und bei
      Anna mit 1,00 rund 7,04 s; Anna ist also **14 % langsamer**, nicht
      gleichauf. Seit dem 2026-08-22 steht Anna auf **0,95** - von Stephan aus
      korrekt erzeugten Proben gewählt. Damit ist der zweite der
      drei Punkte vor der zweiten Stimme beantwortet - mit ja.
    - **Der Name stand längst fest** und wurde nicht neu erfunden:
      `docs/ersteinrichtung.md` nennt seit Langem männlich Michael und Daniel,
      weiblich Anna und Julia. Stephan hat mich darauf hingewiesen, bevor ich
      danach gefragt hatte.
    - **Und Anna kennt den Namen des Nutzers.** Auf Stephans Frage hin
      („können wir auch den Benutzernamen einbauen … eher da wo es Sinn macht
      als Ersatz zu Du/Dir") spricht DialOS ihn jetzt an - bei der Begrüßung,
      bei Entscheidungen und bei Fehlern, **nicht** bei Bestätigungen und nicht
      bei der Zeitgrenze. Der Grund wiegt hier schwerer als Höflichkeit: Der
      Name am Satzanfang ist ein **Signal** - läuft das Radio oder ist Besuch im
      Raum, sagt „Stephan, …" unmissverständlich, dass es ihn betrifft. Wer ihn
      dauernd hört, überhört ihn.
    - **Ohne Namensdatei bleibt es beim schlichten „Du",** und jede Ansage stimmt
      trotzdem. Keine hängt davon ab, dass ein Name eingetragen ist.
    - **Vier eigene Fehler dabei:** „Stephan, **I**ch finde kein Mikrofon" (nach
      dem Komma gehört es klein); „Stephan, hallo, ich bin Anna" (die Begrüßung
      baut den Namen selbst ein); der Begrüßungssatz steht an **zwei** Stellen
      und ich änderte nur eine; und ich legte eine Beispieldatei nach
      `includes.chroot` - genau das, was ich eine Stunde vorher beim
      `gdm3/custom.conf` als falsch erkannt hatte. Beide letzten fand das
      Prüfskript, nicht ich.

- **Sicherheitsupdates laufen jetzt unbeaufsichtigt (2026-08-20).**
  `unattended-upgrades` 2.12 installiert und eingerichtet - in
  `docs/anwendungen.md` war es seit dem 2026-08-18 entschieden und stand als
  „Paket noch nicht installiert" da.
    - **`#clear` vor `Origins-Pattern` ist Pflicht, und das habe ich erst falsch
      gemacht.** Eine `Origins-Pattern`-Zeile **hängt an** (`::`), sie ersetzt
      nicht. Nach dem ersten Versuch standen fünf Muster in der Liste - meine
      zwei **und** Debians drei, darunter `label=Debian` ohne `-Security`, also
      die normale Stable-Quelle. Ich hatte Stephan vorher „nur
      Sicherheitsupdates" gesagt; das stimmte nicht. Aufgefallen nur, weil nach
      dem Installieren `apt-config dump` gelesen wurde statt der eigenen Datei zu
      glauben - **eine Konfigurationsdatei zu schreiben ist nicht dasselbe wie
      eine Einstellung zu setzen.**
    - **`Remove-Unused-Dependencies "false"` ist die wichtigste Zeile.** Nach dem
      Aufräum-Schritt gelten 49 Pakete als „automatisch installiert" - darunter
      `gnome-shell`, `nautilus`, `pipewire-audio`. Ein automatisches
      `autoremove` würde nachts anbieten, den Desktop und den Ton-Unterbau zu
      entfernen. Das Aufräum-Skript schützt sie, aber diese Einstellung darf sich
      nicht darauf verlassen: Übersieht der Schutz **ein** Paket, wäre das Gerät
      am Morgen unbenutzbar - und der Nutzer könnte nicht einmal Hilfe rufen.
    - **`Automatic-Reboot "false"`** wiegt hier schwerer als üblich: `/home/nutzer`
      liegt auf der LUKS-Partition, die der Sicherheits-Stick öffnet. Ein
      nächtlicher Neustart ohne steckenden Stick sperrt den Nutzer am Morgen
      komplett aus.
    - **Belegt statt geglaubt:** Der Probelauf zeigt in
      `/var/log/unattended-upgrades/unattended-upgrades.log`, dass `trixie`,
      `trixie-updates` **und** die Anthropic-Quelle mit Pin `-32768` gesperrt
      sind - apts „auf keinen Fall". Nur `Debian-Security` fehlt in dieser Liste.
    - **Bewusst mit gesperrt: `trixie-updates`,** wo unter anderem `tzdata`
      herkommt. Die Zeitzonen-Datenbank veraltet damit bis zum Sprachbefehl
      „System aktualisieren" - erwähnenswert bei einem Gerät, dessen
      Uhrzeit-Ansage ein Kernbefehl ist.

- **Die Protokolle werden nach sieben Tagen gelöscht (2026-08-20).** Stephans
  Entscheidung, dieselbe Frist wie beim Support-Protokoll. Bis dahin wuchsen
  sechs Protokolle unbegrenzt - beim Diktat hieß das, dass jeder je diktierte
  Brief dauerhaft im Klartext auf dem Gerät lag.
    - **Über `/etc/logrotate.d/dialos`, nicht in den Programmen.** Das
      Support-Protokoll räumt sich selbst auf, weil `dialos-mitschrift.py`
      ohnehin läuft, während es geschrieben wird. Bei sechs Programmen wäre das
      sechsmal derselbe Code - und ein Dienst, der eine Woche durchläuft, käme
      nie zum Aufräumen, weil er nur beim Start nachsähe.
    - **Kein `copytruncate`, und das ist geprüft:** Die Programme halten ihre
      Datei **nicht** offen, sie öffnen zum Schreiben und schließen wieder
      (über `/proc/*/fd` nachgesehen). Damit ist normales Umbenennen gefahrlos.
      `copytruncate` wäre die Antwort auf ein Problem, das hier nicht besteht,
      und es kann Zeilen verlieren.
    - **`dateext`** statt laufender Nummer: `dialos-diktat.log-2026-08-20`. Wer
      im Support nachsieht, sucht einen Tag - dieselbe Überlegung wie beim
      Support-Protokoll.
    - **Belegt statt geglaubt:** erzwungener Lauf, alle sechs rotiert, neue
      Dateien mit **0600** statt 0644. Die beiden Messsicherungen blieben
      unangetastet, weil sie nicht auf `.log` enden.
    - **Rest-Lücke, benannt:** Eine *neu* angelegte Datei bekommt 0644 (Standard-
      umask der Programme), erst die Rotation setzt 0600. Und die heute
      weggerotierten Dateien tragen noch die alten Rechte - das korrigiert sich
      ab morgen von selbst.

- **Die Sprachsteuerung hat sich selbst eingeschaltet - und dabei fast die
  Fernwartung angefordert (2026-08-20).** Stephan ließ DialOS über Nacht laufen:
  „immer mal wieder meldete sich Michael. Und eben beim dialosadmin fragte er
  mich, ob er die Fernwartung einschalten soll."
    - **Das Protokoll erklärt beides auf einmal:** `14:04:07 erkannt: 'starten'`
      schaltet die Sprachsteuerung ein, `14:04:43 erkannt: 'hilfe rufen'` fordert
      die Fernwartung an - **niemand hat gesprochen.** Nur die Ja/Nein-Rückfrage
      hat es verhindert.
    - **Gemessen über 157 aufgezeichnete Äußerungen:** `'starten'` allein **18×**
      gegen den vollen Satz 4×. Die Sprachsteuerung hat sich also 18-mal
      unaufgefordert eingeschaltet, jedes Mal für zwei Minuten offenes Mikrofon -
      rund 26 Minuten, die niemand wollte.
    - **Kernwort ist jetzt „sprachsteuerung"** statt „starten": lang, markant, in
      nur 16 von 157 Äußerungen vorgekommen. Gegen dieselben Daten geprüft: aus
      22 Einschaltungen werden 9. Der Preis ist, dass ein verschlucktes
      „sprachsteuerung" den Satz wiederholen lässt - eine Unbequemlichkeit, im
      Gegensatz zu einem Mikrofon, das sich von selbst einschaltet.
    - **Die Lockerung von gestern hat einen Fehler behoben und einen größeren
      geschaffen.** Als Regel eingetragen: Ein Kernwort muss nicht nur eindeutig,
      sondern auch **lang genug** sein.
    - **Bestätigt hat sich dabei die Rückfrage.** Sie war die einzige Schicht,
      die gehalten hat - genau dafür steht in `docs/sprachbefehle.md`, dass
      sicherheitskritische Befehle eine Rückfrage bekommen, „unabhängig davon,
      wie sicher die Erkennung war".

- **Der Ansagen-Speicher nahm die falsche Stimme (2026-08-20).**
  `speicher_fuellen()` in `dialos-say.py` griff die **erste** `.onnx`-Datei im
  Ordner statt der eingestellten. Solange nur Thorsten installiert ist, fällt das
  nicht auf; mit einer zweiten Stimme spräche der Speicher je nach Sortierung
  eine andere als das System - und zwar unbemerkt, weil beide Wege für sich
  richtig klingen. Gelesen wird jetzt `DefaultVoice` aus `piper-generic.conf`,
  dieselbe Datei wie beim Tempo. Ist die eingestellte Stimme nicht installiert
  und liegen mehrere im Ordner, wird **nicht geraten**, sondern nichts
  gespeichert. Fünf Fälle gegengeprüft. (Die Code-Änderung ist versehentlich in
  den Commit davor gerutscht - `git add -A` nimmt mit, was da ist.)

- **„Hilfe rufen" - DialOS kann jetzt um Hilfe rufen (2026-08-19).** Bis dahin
  hatte ein Nutzer, bei dem etwas nicht funktioniert, **keinen Weg**, den Support
  zu erreichen; alles, was an Nachvollziehbarkeit gebaut wurde, setzte voraus,
  dass überhaupt jemand an das Gerät kommt.
    - **„Hilfe rufen"** fragt mit einer Rückfrage nach, die erklärt, was passiert
      („Dein Betreuer kann dann sehen, was auf dem Bildschirm steht"), startet
      RustDesk und liest die Nummer **ziffernweise in Vierergruppen und zweimal**
      vor. Als Zahl gelesen wäre sie unbrauchbar, und mitschreiben kann der
      Nutzer nicht. **„Fernwartung beenden"** beendet sie wieder.
    - **Ein Einmalpasswort ist mit RustDesk 1.4.9 nicht zu haben** - fünf Wege
      geprüft, alle zu (Details in `docs/sicherheit-datenschutz.md`). Es steht in
      keiner Datei, `rustdesk --password` ist wirkungslos selbst als root, und
      [rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074) ist offen.
    - **Deshalb garantiert die LAUFZEIT die Begrenzung, nicht das Passwort** - der
      härtere Hebel: Solange RustDesk nicht läuft, ist keine Verbindung möglich,
      egal wer das Passwort kennt. Es startet nie von selbst und endet nach
      **einer Stunde** von selbst, mit Vorwarnung drei Minuten vorher; ein
      erneutes „Hilfe rufen" verlängert.
    - **Und die Ansage sagt das, statt etwas Falsches zu behaupten.** „Das
      Passwort gilt nur für diesen Einsatz" wäre eine Lüge, solange es dauerhaft
      ist - einem Nutzer, der den Bildschirm nicht sieht, eine falsche Sicherheit
      zu erzählen ist schlimmer, als ihm die richtige zu erklären.
    - **Absolut statt im Leerlauf, und warum:** Stephans Frage war richtig -
      Leerlauf wäre die bessere Semantik. Nur hat sich auf diesem Gerät noch nie
      jemand verbunden, die Signatur einer aktiven Verbindung ist unbekannt, und
      eine Grenze, die eine aktive Sitzung für Leerlauf hält, schneidet den
      Betreuer bei der Arbeit ab. `spur_notieren()` sammelt deshalb die
      Anhaltspunkte mit; nach dem ersten echten Verbindungsversuch lässt sich die
      Erkennung **belegt** bauen.
    - **Zwei Funde am Rand:** `rustdesk --help` **startet die Oberfläche** statt
      Hilfe auszugeben - der Aufruf lief in die Zeitgrenze und ließ ein RustDesk
      laufen, das ich beendet habe. Und RustDesk kontaktiert beim Start
      `api.rustdesk.com`; das steht jetzt in der Datenschutz-Doku.
    - **Neues Werkzeug:** `scripts/dialos-grammatik-pruefen.py` - Piper spricht
      jeden Satz der Grammatik, Vosk hört zu. Eine Pflichtprüfung, die davon
      abhängt, dass sich jemand an den Piper-Aufruf erinnert, findet irgendwann
      nicht mehr statt. **Alle 18 Sätze wörtlich erkannt**, auch die 16
      bestehenden.

- **Die erste Korrektur jeder Sitzung war ein Muenzwurf - und die Schreibung ist
  besser als gedacht (2026-08-19).** Der Ausfall vom Morgen ("LanguageTool nicht
  erreichbar: timed out", 10:03:03) war kein Zufall, sondern systematisch.
    - **Gemessen nach einem Neustart des Dienstes:** `/v2/languages` - der
      Endpunkt, den `lt_lebt()` als "laeuft" prueft - antwortet nach **1,3 s** und
      laedt keine Regeln. Die **erste** `/v2/check`-Anfrage kostet **9,2 s**, weil
      dort die deutschen Regeln laden; jede weitere 1,0 s. Die Zeitgrenze im
      Diktat liegt bei 10,0 s. **0,8 Sekunden Luft** - und an diesem Morgen hat
      sie verloren.
    - **Der fruehere Schluss war unvollstaendig, nicht falsch.** Die Unit
      dokumentiert seit dem 2026-08-18 "der erste Aufruf kostet 8,8 s" und zog
      daraus "dann eben ein Dauerdienst". Ein Dauerdienst **verschiebt** die
      Ladezeit aber nur auf die erste Pruefanfrage.
    - **Behoben an der Wurzel:** `dialos-schreibhilfe-warmlaufen.py` laeuft als
      `ExecStartPost` der Unit. Belegt im Journal: `Handled request in 9096ms`
      direkt beim Start, danach `985ms` fuer die erste echte Korrektur des
      Diktats. Das `-` vor dem `ExecStartPost` macht ein Scheitern unschaedlich -
      ein nicht warmgelaufener Dienst ist besser als keiner, und
      `Restart=on-failure` darf deswegen nicht in eine Schleife geraten.
    - **Eine Bereitschaftsmeldung, die das Falsche prueft**, war der Grund, dass
      es niemandem auffiel: `lt_lebt()` meldet "laeuft", waehrend der Dienst fuer
      die erste echte Anfrage noch neun Sekunden braucht.
    - **Dazu die Schreibung selbst gemessen** - mit `schreibung_richten()` selbst,
      nicht mit einer Nachbildung: **10 von 11** Faellen richtig. Der einzige
      Fehlschlag ist die Wortliste ohne Grammatik; einzeln geht jedes Wort
      richtig, und einzeln kommen sie seit dem Umbau desselben Tages. Bei Briefen
      und Mails ist die Schreibung damit belastbar, und meine Einschaetzung vom
      Morgen, sie sei der dringendste offene Punkt, ist zurueckgenommen: der
      dringendere war die Ladezeit darueber.

- **Der Ton-Beobachter protokollierte im Normalbetrieb nichts (2026-08-19).**
  Stephan schaltete nach dem Neustart den Bluetooth-Lautsprecher ein und meldete
  „hat funktioniert" - nachweisen konnte ich es nicht: `melde()` in
  `dialos-ton-ausgabe.py` gab nur bei `--debug` etwas aus und schrieb **nie** eine
  Datei. Die Zeilen in `~/dialos-ton-ausgabe.log` stammten von einem Handlauf am
  2026-08-17.
    - **Das traf genau den falschen Dienst.** Seine Ausfälle waren am 2026-08-17
      die am schwersten zu findenden („es kam keine Info weder beim Aus- noch beim
      Einschalten"), und nachweisen ließ sich etwas nur, indem man ihn mit
      `--debug` neu startete - womit der Zustand, den man messen wollte, schon
      ein anderer war.
    - **Behoben wie am Morgen beim Befehlsdienst:** `melde()` schreibt jetzt
      immer mit Zeitstempel nach `~/dialos-ton-ausgabe.log`, `--debug` gibt
      zusätzlich aus. Dazu eine Startzeile, damit „keine Zeile" nicht
      ununterscheidbar von „Dienst läuft nicht" ist.
    - **Und er ist jetzt die fünfte Quelle der Mitschrift** - ein Wechsel des
      Ausgabegeräts ist die eine Änderung, die der Nutzer sofort hört, ohne sie
      ausgelöst zu haben. Im Fenster erscheint nur der echte Wechsel; die rohen
      PipeWire-Ereignisse und „Ausgabe bleibt" bleiben im Protokoll (dort haben
      sie am 2026-08-17 den Fehler bewiesen), werden aber ausgefiltert - bei
      einem Bluetooth-Verbindungsaufbau feuert PipeWire ein Dutzend davon.
    - **Gerätenamen werden übersetzt:** aus
      `bluez_output.41_42_AF_06_24_5C.1` wird „Bluetooth-Lautsprecher", aus
      `alsa_output.pci-...` „Laptop-Lautsprecher". Die Mitschrift ist dazu da,
      Protokoll in Sprache zu übersetzen - dann auch das.
    - **Damit ist der `letzte_wahl`-Fix vom 2026-08-17 erstmals belegt** - er
      war zwei Tage lang committet und nicht installiert. Stephans Test am
      2026-08-19: Bluetooth aus um 11:51:58, ein um 11:52:08, und fünf Sekunden
      später ein Folge-`change`-Ereignis von PipeWire, das richtig als „Ausgabe
      bleibt" erkannt wurde - **keine** doppelte Ansage. Am 2026-08-17 war es
      umgekehrt: „Vorgabe bleibt" kam immer, auch beim echten Wechsel, und genau
      deshalb blieb die Ansage aus.
    - **Falscher Alarm dabei, den ich zurückziehe:** Ich hielt einen zweiten
      `dialos-ton-ausgabe.py`-Prozess für einen doppelten Beobachter. Er war
      Sekunden später weg - ein kurzlebiger Einzelaufruf, der die Senke wählt.

- **Zwei Start-Ansagen liefen gleichzeitig - die Sperrdatei lag im geteilten
  `/tmp` (2026-08-19).** Beim Vergleich des Installationsstands fiel auf, dass
  `dialos-start-ansage.py` **zweimal** lief (PID 5526 seit 08:14, PID 19451 seit
  09:26). Das Skript beendet sich nicht, sondern überwacht danach das Netz - es
  liefen also zwei Netzwerk-Beobachter, die beide ansagen können.
    - **Ursache:** `LOCK_DATEI = "/tmp/dialos-start-ansage.pid"` - ein fester
      Pfad für **alle** Nutzer. `nutzer` legte die Datei beim Anmelden um 08:12
      an (`-rw-rw-r-- nutzer nutzer`), `dialosadmin` konnte sie danach nicht mehr
      überschreiben. Also konnte sich keine seiner Instanzen registrieren, und
      keine sah die andere.
    - **Und die Sperre hätte im Fehlerfall auf einen fremden Prozess gezeigt.**
      `alte_instanz_beenden()` liest die PID und schickt ihr SIGTERM; dass das
      über Nutzergrenzen an den Rechten scheitert, ist Glück und kein Entwurf.
    - **Behoben:** Die Datei liegt jetzt in `$XDG_RUNTIME_DIR` (`/run/user/1000/`)
      - pro Nutzer, 0700, und beim Abmelden räumt systemd sie selbst weg.
      Dasselbe Muster wie `marke_pfad()` in `dialos-diktat.py` und
      `dialos-notiz.py`. `PermissionError` wird jetzt ausdrücklich behandelt:
      eine Datei, in die man nicht schreiben darf, ist keine Sperre - dann wird
      die eigene PID auch nicht hineingeschrieben.
    - **Das Risiko stand seit Tagen in `TODO.md`** („Lock-Datei aus /tmp
      holen"). Ein notiertes Risiko ist kein behandeltes - dieselbe Lehre wie am
      2026-08-18, als die dokumentierte Gefahr eines nicht erkannten
      Schlusssatzes am selben Tag ein siebenminütiges Diktat verursachte.

- **„Es soll sich wie ein Dialog zwischen dem Nutzer und Michael anfühlen"
  (Stephans Grundsatz, 2026-08-19)** - jetzt als Regel in
  `docs/sprachbefehle.md`, und zwar als die Regel, aus der die anderen
  Formulierungsregeln folgen. Praktischer Grund: Wer den Bildschirm nicht sieht,
  hat nichts als diese Stimme. Eine Zustandsmeldung lässt ihn allein, ein Satz
  nicht.
    - **Die Zeitgrenzen-Ansage heißt jetzt „Du hast **mir** eine Weile nichts
      gesagt."** Das „mir" ist nicht Höflichkeit, es macht den Satz erst wahr:
      Der Zähler läuft ab dem letzten **Befehl**, nicht ab der letzten
      Äußerung - ein Bruchstück aus einem Gespräch im Raum setzt ihn absichtlich
      nicht zurück, sonst hielte ein laufendes Radio die Sprachsteuerung endlos
      wach. Im Test stand genau das im Protokoll: `erkannt: 'es'` um 11:08:18,
      Zeitgrenze um 11:08:46. „Du hast eine Weile nichts gesagt" wäre da falsch
      gewesen.
    - **Alle 37 Ansagen des Systems gegen den Grundsatz geprüft** - 22 sprachen
      den Nutzer an, 15 klangen nach Maschine. Sieben davon umgestellt: „Das
      lässt sich nicht ausführen." → „Ich kann das nicht ausführen.", „Das
      Mikrofon ist wieder da." → „Ich höre Dich wieder.", „Das grosse
      Sprachmodell fehlt." → „Mir fehlt das große Sprachmodell. Ich kann nicht
      mitschreiben.", und drei weitere.
    - **Bewusst nicht umgestellt:** die kurzen Rückmeldungen auf eine
      Umschaltung („Windows Desktop.", „Ton über Lautsprecher.") - dort will der
      Nutzer weitermachen, und die Kürze war eine eigene Entscheidung vom
      2026-08-17. Und „Der Einkaufszettel ist leer." bleibt, weil ein Mensch auf
      diese Frage genauso antworten würde.
    - **Zwei Fehler dabei aufgefallen:** `ANSAGE_ENDE = "Diktat beendet."` war
      seit dem Umbau am Mittag **toter Code** - eine Konstante, die niemand mehr
      benutzt, sieht beim Lesen wie die gültige Ansage aus. Und der Code sagte
      „Der Schreibtisch steht schon auf **Linux**.", während
      `docs/sprachbefehle.md` schon „Linux **Desktop**" auswies - Stephans
      Benennung war im Code nie angekommen. Beides behoben, die Doku an den
      vollen Satz angeglichen.

- **Warum die Sitzung endete, stand nirgends (2026-08-19).** Stephan fiel im
  Support-Protokoll eine Lücke auf: Zwischen 10:51 und 10:57 hatte sich die
  Sprachsteuerung per Zeitgrenze abgeschaltet, aber im Protokoll stand um
  10:53:27 nur „Mitschrift geschlossen". Zwei Ursachen:
    - **Die Zeitgrenze wurde überhaupt nicht protokolliert.** Der Dienst
      schaltete ab, sagte es an, schloss das Fenster - und schrieb keine Zeile
      darüber. Damit stand im Protokoll die Wirkung und nicht die Ursache. Jetzt
      kommt `Zeitgrenze: 120 s ohne Befehl`, und zwar **vor** der Ansage: die
      dauert 3,5 s, in denen die Mitschrift die Zeile noch liest.
    - **Die letzte Zeile war beim Schreiben schon zu spät:** `melde()` stand
      hinter dem `kill`, das Fenster war tot, bevor die Meldung geschrieben war.
      Jetzt wird erst gemeldet, dann eine Sekunde gewartet (`NACHLAUF_S`), dann
      geschlossen - die Mitschrift sieht alle 0,4 s nach.
    - **Dieselbe Fehlerklasse wie der fehlende Rückblick am Morgen**, nur am
      anderen Ende der Sitzung: Das Protokoll zeigte, *was* passiert ist, aber
      nicht *warum*. Für die Fehlersuche ist das die unbrauchbare Hälfte. Beide
      Zeilen sind jetzt end-to-end belegt.

- **Sprachbeispiele für die neuen Ansagen, und zwei Fehler in der Fußzeile
  (2026-08-19).** `docs/sprachbeispiele/` ist von 12 auf **15** Dateien
  gewachsen: der Diktatstart beim Einkaufszettel mit der Anleitung, der Hinweis
  nach „Diktat beenden", und die Nachfrage bei unverstandener Antwort. Die
  Rückfrage vor dem Leeren und das Vorlesen wurden neu erzeugt, weil sich ihr
  Wortlaut geändert hat; `04b` (Zeitgrenze) fehlte bisher in der Tabelle.
    - **Die Texte kommen jetzt aus den echten Skripten**, nicht mehr aus
      abgeschriebenen Zeichenketten: Das Erzeugungsskript importiert
      `dialos-diktat.py` und `dialos-notiz.py` und ruft `ansage_ende()`,
      `benennen()` und `aufzaehlen()` genauso auf wie das System. Von Hand
      abgeschrieben liefen die Beispiele beim nächsten Wortlaut auseinander -
      und zwar unbemerkt, weil sie für sich genommen richtig klingen.
    - **Gemessen, vorgelegt, entschieden:** Der Hinweis nach dem Diktat dauert
      **8,05 s** und ist damit die längste Ansage im System - die eigene Regel
      sagt „acht Sekunden Erklärung waren zu viel" (Fehler vom 2026-08-17). Drei
      Kürzungen wurden gemessen und vorgespielt (6,07 / 4,94 / 2,88 s);
      **Stephan hat sich für den vollen Wortlaut entschieden.**
    - **Und dabei kam heraus, dass die Regel unvollständig war.** Sie stammt von
      der Desktop-Umschaltung, wo der Nutzer darauf wartet, weitermachen zu
      können. Nach einem **beendeten** Diktat wartet nichts - er hat gerade
      abgeschlossen und hat keinen nächsten Befehl in der Warteschlange. Nicht
      die Sekunden sind das Maß, sondern was dem Nutzer im Weg steht. Diese
      Unterscheidung steht jetzt in der Regel selbst, damit die Entscheidung
      nicht später als Versehen „korrigiert" wird.
    - **Zwei Fehler in `dialos-fusszeile.py`, gefunden weil Stephan die Fußzeile
      sehen wollte:** `--art mail` filterte nur `--art` heraus und nicht dessen
      Wert - „mail" landete als **Dateiname**, die dokumentierte Aufrufform war
      also gar nicht benutzbar. Und die Art wurde per Textsuche in der ganzen
      Befehlszeile bestimmt: eine Datei `mailand-reise.txt` hätte „Diese
      Nachricht" bekommen. Beide behoben, beide gegengeprüft.
    - **„ja" / „nein" fehlten in der Befehlsliste** - eingebaut am Vormittag,
      eingetragen erst jetzt. Sie gelten nur während einer Rückfrage, mit einem
      eigenen Erkenner und einer Grammatik aus genau diesen zwei Wörtern.

- **Die Ja/Nein-Rückfrage hörte nicht zu, wenn geantwortet wurde
  (2026-08-19).** Stephans „ja" beim Löschen des Einkaufszettels kam nie an - im
  Protokoll stand nach 15 Sekunden nur „keine verwertbare Antwort" und **keine
  einzige** „Antwort gehoert"-Zeile. Ursache: Der Aufrufer sprach die Frage und
  rief danach die Antwortfunktion, die erst dann das Sprachmodell lud und
  anschließend die Aufnahme startete. Die Antwort fiel in genau diese Lücke.
    - **Erst geprüft, was das Projekt sich selbst zur Regel gemacht hat:**
      Stehen „ja" und „nein" im Wortschatz? Ja - Vosk meldete beim Bauen der
      Grammatik nichts. Damit war diese Spur ausgeschlossen, bevor geraten
      wurde.
    - **Behoben, indem die Antwortfunktion die Frage jetzt selbst stellt.** Alles
      Langsame (Modell laden, Mikrofon wählen) passiert davor. Dieselbe
      Fehlerklasse gab es schon am 2026-08-15 (Start-Ansage) und am 2026-08-18
      (Diktat-Marke); die Reihenfolge „erst bereit sein, dann fragen" steht jetzt
      als Regel in `docs/sprachbefehle.md`.
    - **Die erwarteten Wörter gehören in die Frage** (Stephans Vorgabe): „Soll
      ich ihn löschen? **Sage ja oder nein.**" Ein blinder Nutzer sieht keine
      Knöpfe. Und kommt keine verwertbare Antwort, wird **einmal nachgefragt**
      statt abgebrochen - sonst müsste er den ganzen Befehl neu sprechen,
      obwohl nur ein Wort gefehlt hat.
    - **Während der Frage wird bewusst nicht aufgenommen.** Die Grammatik kennt
      nur „ja", „nein" und „[unk]" - die eigene Stimme des Systems könnte darin
      als „ja" landen und den Zettel löschen, ohne dass jemand etwas gesagt hat.
    - **End-to-end belegt, ohne Stephans Stimme:** Piper sagt „ja", Vosk hört
      über das Mikrofon zu. Ergebnis im Protokoll: „Antwort-Erkenner bereit in
      0.5 s" **vor** der Frage, dann „Antwort gehoert: 'ja'", dann geleert mit
      Sicherung. Nebenbefund: Die Echounterdrückung rechnet Michaels Stimme
      **nicht** weg - damit ist die Rückfrage genauso automatisch testbar wie
      die Befehlsgrammatik.

- **Ein Eintrag pro Ware - und DialOS sagt jetzt, wie das geht (2026-08-19).**
  Stephan diktierte „Milch sechs Eier Butter" in einem Zug und meldete, Michael
  habe „3x die Liste vorgelesen" und sei „wieder zu schnell". Beides war
  dieselbe Ursache und keines ein Fehler im Vorlesen: Im Zettel standen wirklich
  drei Zeilen - je eine pro Test -, und jede war der ganze Einkauf. Vosk liefert
  eine in einem Atemzug gesprochene Folge als **eine** Äußerung, eine Äußerung
  ist ein Eintrag, und die Pause sitzt zwischen Einträgen, nicht innerhalb.
    - **Am Programm war nichts kaputt.** Wer zwischen den Waren eine kleine
      Pause macht, bekommt drei Einträge - das war von Anfang an so gebaut. Es
      fehlte, dass DialOS es **sagt**. Beim Einkaufszettel heißt es jetzt: „Ich
      schreibe mit. Sage jede Ware einzeln, mit einer kleinen Pause dazwischen."
      Nur beim Einkaufszettel - bei einer Notiz ist eine Äußerung wirklich ein
      Satz.
    - **Die Lehre, die über das Diktat hinausgeht** und jetzt als Regel in
      `docs/sprachbefehle.md` steht: Wo der Nutzer das Ergebnis nicht sehen
      kann, ist eine Bedienregel wertlos, solange sie ungesagt bleibt. Ein
      sehender Nutzer hätte nach der ersten Ware bemerkt, dass eine einzige
      Zeile entsteht. Ein blinder erfährt es erst beim Vorlesen, eine Minute
      später.
    - **Rückfallebene:** „Milch **und** sechs Eier **und** Butter" wird an
      „und" getrennt - so spricht man eine Einkaufsliste ohnehin. Bewusst nur
      bei Listen-Zielen: in einem Brief würde aus „Ich habe Milch und Butter
      gekauft" sonst zwei Zeilen. Jeder getrennte Eintrag fängt groß an, weil
      die Schreibhilfe die Äußerung als einen Satz gesehen hat und den Zettel
      auch ein sehender Helfer liest.
    - **Nicht gelöst und deshalb in `TODO.md`:** ohne „und" und ohne Pause
      bleibt es ein Eintrag. Zuverlässig ginge das nur über die
      Wort-Zeitstempel von Vosk (`SetWords(True)`) - ungemessen.

- **„Diktat beenden" liest nicht mehr vor, sondern sagt, wie man es bekommt
  (Stephan, 2026-08-19).** Bisher las der Befehl die fertige Notiz komplett vor.
  Das machte „Einkaufszettel vorlesen" überflüssig - und nahm dem Nutzer die
  Wahl: wer drei Waren aufschreibt, will sie nicht dreimal hören. Jetzt: „Diktat
  beendet, 3 Einträge geschrieben. Möchtest Du Deinen Einkaufszettel vorgelesen
  haben, dann sage: Einkaufszettel vorlesen."
    - **Die Anzahl bleibt drin, weil sie das Vorlesen ersetzt** - sie ist das
      einzige, woran ein blinder Nutzer merkt, dass etwas angekommen ist und wie
      viel. Ein bloßes „Diktat beendet." ließe ihn im Dunkeln.
    - **Hinweis statt Rückfrage:** Eine Rückfrage verlangt eine Antwort und hält
      das Gerät auf, bis sie kommt. Ein Hinweis kostet nichts, wenn man ihn
      nicht braucht.
    - **Der Hinweis kommt aus einer Tabelle mit genau den Zielen, für die es
      den Vorlese-Befehl wirklich gibt.** Ein späteres Ziel wie „brief" bekommt
      vorerst nur die Bestätigung: einem blinden Nutzer einen Satz zu nennen,
      den die Grammatik nicht kennt, wäre schlimmer als kein Hinweis - er würde
      ihn sagen, nichts würde passieren, und er hätte keine Möglichkeit
      herauszufinden warum.
    - Das Vorlesen mit Satzzeichen lebt unverändert in `dialos-notiz.py`
      weiter, wo es auf Ansage geschieht.

- **Mitschrift geht mit der Sprachsteuerung auf und zu - und schreibt ein
  Support-Protokoll (Stephans Präzisierung, 2026-08-19).** Bisher musste das
  Fenster von Hand geöffnet werden; jetzt öffnet es
  `dialos-sprachbefehl-desktop.py` bei „Sprachsteuerung starten" und schließt es
  bei „Sprachsteuerung stoppen" und bei der Zwei-Minuten-Zeitgrenze. Es hängt
  damit an der Sprachsteuerung und nicht am Anmelden: wo nicht gesprochen wird,
  gibt es nichts mitzuschreiben. Bewusst nicht bei jedem einzelnen Befehl -
  einmal pro Sitzung aufgehen ist unauffällig, bei jedem Satz aufspringen wäre
  es nicht.
    - **Zwei Fallen, beide gelöst:** Vor dem Öffnen wird über `/proc` geprüft,
      ob schon ein Fenster läuft - ohne das stünden nach zwanzig Aktivierungen
      zwanzig Fenster übereinander. Und geschlossen wird das **Skript**, nicht
      das Terminal: `gnome-terminal` spaltet sich vom Aufruf ab und übergibt an
      einen schon laufenden `gnome-terminal-server`, dessen PID allen Fenstern
      gehört. Endet das Skript, endet der Befehl des Fensters - und das Fenster
      schließt sich von selbst.
    - **Support-Protokoll:** `~/.local/share/dialos/support/befehle-JJJJ-MM-TT.log`,
      Ordner 0700, Datei 0600, eine Datei pro Tag, **sieben Tage**, räumt sich
      beim Start und um Mitternacht selbst auf. Zweck ist der Anruf beim
      Support: nachlesen, was das Gerät wirklich gehört hat.
    - **Die Grenze beim Inhalt, und warum sie dort liegt:** `~/dialos-diktat.log`
      enthält jeden diktierten Satz wörtlich, also den ganzen Brief. Eine Datei
      für einen fremden Helfer darf die Post des Nutzers nicht enthalten.
      Deshalb: Befehle vollständig, vom Diktierten die **erste Zeile** (auf 60
      Zeichen gekürzt), danach nur die Anzahl. Im Fenster steht weiter alles -
      dort sieht es nur, wer ohnehin vor dem Gerät sitzt.
    - **Der Zusammenhang ist das Wichtigste (Stephan):** „Milch" allein sagt
      niemandem etwas, „Einkaufszettel: Milch" sagt alles. Vor jedem Abschnitt
      steht deshalb, worum es ging - Diktat, Einkaufszettel, Frage an das
      System, später Mail und Brief. Er wird nicht geraten, sondern aus den
      Zeilen mitgeführt, die die Programme beim Starten selbst schreiben.
    - **Eigener Fehler dabei:** Der erste Entwurf setzte den Zusammenhang nach
      jeder Zeile zurück - damit stand „gespeichert in …" nicht mehr unter
      „Einkaufszettel", und für einen einzigen Befehl standen zwei
      Überschriften da. Ein gehörter Satz ist die einzige verlässliche Grenze;
      er kommt auch dann, wenn ein Diktat vorzeitig abbricht.
    - **Und ein Fehler, der Arbeit gekostet hat:** Beim Umbau habe ich
      `dialos-mitschrift.py` mit einem `re.sub`-Muster `.*\n` unter `re.S`
      bearbeitet - das ist bis zum Dateiende gierig und hat alles hinter der
      Trefferstelle ersetzt. Wiederhergestellt aus `git HEAD` (identisch zur
      installierten Fassung, nur meine eigenen Änderungen waren verloren).
      Seitdem: wörtlich ersetzen, Treffer auf Eindeutigkeit prüfen und nach
      jedem Schreiben prüfen, dass die Datei noch auf `sys.exit(main())` endet.
    - **Rückblick beim Öffnen, gefunden durch Stephans Test:** Das Fenster
      wird von „Sprachsteuerung starten" geöffnet - dieser Satz stand also
      schon im Protokoll, bevor die Mitschrift zu lesen begann, und fehlte
      damit **immer**. Für den Support wäre das die erste Frage gewesen („hat er
      überhaupt eingeschaltet?"). Der Dienst ruft jetzt mit `--rueckblick 20`
      auf, was auch die nicht erkannten Versuche davor mitnimmt.
    - **Zwei Fallen darin, beide gelöst:** Dopplung beim zweimaligen
      Einschalten - Merker ist die Uhrzeit der letzten Zeile im Protokoll
      selbst, kein zusätzlicher Zustand, der veralten könnte. Und der
      **Tageswechsel**: Die Protokolle schreiben nur `HH:MM:SS` und werden nicht
      gedreht, ein Eintrag von **gestern** 17:52 sieht vorwärts verglichen wie
      „später heute" aus. Beim Testen mit weitem Rückblick stand genau solcher
      Diktattext aus einer fremden Sitzung in der Liste. Das Dateiende wird
      deshalb **rückwärts** gelesen: wo die Uhrzeit nach oben springt, ist der
      Tageswechsel.
    - Neu dokumentiert: `docs/sicherheit-datenschutz.md` hat jetzt einen
      Abschnitt **„Protokolle: was DialOS über den Nutzer mitschreibt"** mit
      Tabelle über alle fünf Dateien, Rechten und Aufbewahrung. Dabei
      aufgefallen und in `TODO.md` notiert: die vier Programm-Protokolle
      wachsen unbegrenzt und werden nicht gedreht.

- **Fußzeile für Dokumente, Mails und Ausdrucke (Stephans Vorgabe,
  2026-08-19).** Text wörtlich: „Dieses Dokument wurde per Spracheingabe
  powered by DialOS.org erstellt!", dezent und rechtsbündig. Neues Skript
  `dialos-fusszeile.py`, der Text in einer **einzigen** Datei unter
  `/usr/local/share/dialos/fusszeile.txt`.
  - **Notizen bleiben frei davon** (Stephans Entscheidung). Der
    Einkaufszettel wird bei jedem Diktat ergänzt; eine Fußzeile landete dort
    bei jedem Durchgang mitten im Text. Notizen sind Arbeitszettel, keine
    Dokumente - beim Drucken kommt die Zeile dazu.
  - **In Mails „Diese Nachricht"** statt „Dieses Dokument" - eine Mail ist
    kein Dokument. Der Rest bleibt wörtlich wie vorgegeben.
  - Rechtsbündig geht im reinen Text nur über Leerzeichen. Ist der Satz
    länger als die Breite, bleibt er linksbündig und ungekürzt: Ein
    abgeschnittener Herkunftshinweis wäre schlechter als ein nicht
    ausgerichteter.

- **Mitschrift: was gerade passiert, für sehende Zuschauer (Stephans Wunsch,
  2026-08-19).** Ein Fenster, das man einmal öffnet und stehen lässt.
  `dialos-mitschrift.py` liest **vier** Protokolle zusammen und mischt sie
  nach Uhrzeit.
  - **Ein `tail -f` wäre unbrauchbar gewesen:** Das Befehlsprotokoll bestand
    aus **4132 Pegel-Zeilen gegen 13 echte**. Die Mitschrift wirft die
    Pegelanzeige weg und übersetzt die Protokollzeilen in Sätze, die auch
    jemand versteht, der den Quelltext nicht kennt.
  - **Bewusst kein Fenster, das bei jedem Befehl aufgeht** - Stephans
    ursprüngliche Beschreibung. Es würde beim Diktieren den Fokus stehlen,
    und wer diktiert, sieht den Bildschirm ohnehin nicht.
  - **Eigener Fehler, vor der Auslieferung gefunden:** Sie gab Quelle für
    Quelle aus, sah dadurch chronologisch aus und war es nicht - erst alles
    vom Befehlsdienst, dann alles vom Diktat. Bei einem Werkzeug, dessen
    Zweck es ist, **Gleichzeitigkeit** zu zeigen, wäre das die falsche
    Eigenschaft gewesen.

- **Halbtransparente Leisten - und zweimal dieselbe Falle (Stephans Wunsch,
  2026-08-19).** Oben und unten sind zwei verschiedene Leisten und brauchen
  zwei Wege: unten dash-to-panel mit `trans-panel-opacity 0.5` (kein
  zusätzliches Paket), oben `gnome-shell-extension-blur-my-shell` aus
  **Debians** Quellen mit `color` und Alpha 0,5.
  - **Ein gesetzter Wert allein tut nichts.** dash-to-panel hatte
    `trans-panel-opacity` ab Werk auf 0,4 - wirkungslos, weil der Schalter
    `trans-use-custom-opacity` darüber auf `false` stand. Bei blur-my-shell
    braucht es `customize=true`, sonst gelten die allgemeinen statt der
    eigenen Werte. Zwei Erweiterungen, dieselbe Bauart.
  - **`color` mit Alpha statt Weichzeichnung.** Die Voreinstellung ist
    `sigma 30`, also kräftig verwaschen - ein anderer Effekt als
    „halbtransparent". Mit Alpha 0,5 entspricht die obere Leiste genau dem
    Wert der unteren.
  - **Alle acht übrigen Wirkungen der Erweiterung sind ausdrücklich
    abgeschaltet.** Sie kann viel mehr als gebraucht wird, und jede
    zusätzliche Wirkung ist eine mehr, die beim nächsten GNOME-Sprung
    brechen kann - bei drei Erweiterungen sind hier schon zwei
    Debian-Paketfehler gefunden worden. Auf Standardwerten zu lassen wäre
    das Gegenteil einer Entscheidung.
  - **In der Windows-Optik gibt es oben keine Leiste** - dash-to-panel
    ersetzt sie. blur-my-shell muss beim Umschalten deshalb weder ein- noch
    ausgeschaltet werden.

- **Die Ansagen sprechen den Nutzer jetzt an (Stephan, 2026-08-19: „Das
  System soll ja persönlich klingen").** Aus „Ich höre." wurde „Ich höre Dir
  zu.", aus „Ich höre nicht mehr." wurde „Ich höre Dir nicht mehr zu.", aus
  „Ich höre schon." wurde „Ich höre Dir schon zu."
  - **Stephans Begründung für den Stopp-Satz geht über die Formulierung
    hinaus:** „Ich höre nicht mehr" ist zweideutig - es kann auch heißen,
    dass das Gerät nichts mehr hört, also kaputt ist. Mit „Dir" ist klar,
    dass es eine Entscheidung war und kein Defekt. Für jemanden, der den
    Bildschirm nicht sieht, ist das nicht Kosmetik.
  - **Nachgezogen wurde nur die Gegenwart**, nicht die Geschichte: Im
    Änderungsprotokoll und in den Fehlerbeschreibungen bleibt „Ich höre."
    stehen, weil es das ist, was damals gesagt wurde. Eine rückwirkend
    umgeschriebene Doku wäre unwahr.
  - **Gemessen, dass „Michael" gleich klingt:** Speicher und frische
    Erzeugung liefern für alle drei neuen Sätze denselben Wert auf die
    Millisekunde (1,217 / 1,309 / 1,599 s).

- **Und ein Fund aus Stephans Erinnerung an das Sprechtempo (2026-08-19):**
  In `scripts/dialos-sprachbeispiele.py` stand `TEMPO = "0.88"` **fest
  eingetragen**, mit dem Kommentar „wie in piper-generic.conf". Genau die
  Doppelung, die auseinanderläuft: Nach einer Tempoänderung - wie am
  2026-08-17 von 0,85 auf 0,88 - wären die Hörbeispiele in der alten
  Geschwindigkeit geblieben, **ohne dass es auffällt**, denn für sich
  genommen klingen sie richtig. Das Skript liest das Tempo jetzt aus der
  Sprechkette.

- **Uhrzeit und Datum auf Zuruf - und ein Wort, das es unmöglich machte
  (Stephans Wunsch, 2026-08-19).** Vier neue Sprachbefehle, live mit
  Stephans Stimme belegt: „Wie viel Uhr ist es?", „Wie ist die Uhrzeit?",
  „Welchen Tag haben wir?", „Welches Datum haben wir?". Neues Skript
  `dialos-auskunft.py`.
  - **„Wie spät ist es?" war die gewünschte Formulierung und ist
    unmöglich:** „spät" steht nicht im Wortschatz des Modells. Dieselbe
    Falle wie „löschen" einen Tag vorher, und wieder hätte Vosk das Wort
    still aus der Grammatik geworfen. Die Prüfmethode von gestern hat es in
    Sekunden gefunden. Ebenfalls geprüft und nicht enthalten:
    „zurücksetzen", „aufräumen".
  - **Die Bausteine kommen aus `dialos-start-ansage.py`**, nicht neu
    gebaut - Wochentag, Ordinalzahl, Zahl-als-Wort. Zwei Stellen mit
    derselben Aufgabe würden auseinanderlaufen, und der Nutzer hörte den
    Unterschied sofort. Der Import ist gefahrlos, weil jenes Skript nur
    unter `if __name__ == "__main__"` handelt.
  - **Volle Stunde ohne Minutenangabe:** „Es ist acht Uhr", nicht „acht Uhr
    null". Richtig gerechnet wäre falsch gesprochen.
  - **Belegt:** sechs von sechs Sätzen wörtlich erkannt, jeweils rund eine
    Sekunde zwischen Befehl und Antwort. Vorher alle sechzehn Sätze der
    Grammatik gegeneinander geprüft - keine Verwechslung, obwohl die
    Grammatik gewachsen ist.

- **Die Sprachsteuerung liess sich nicht mehr einschalten - der Fehler
  saß an der wichtigsten Stelle (2026-08-19).** Stephan sagte
  „Sprachsteuerung starten", das Protokoll zeigt `erkannt: 'starten'`. Die
  Bedingung verlangte den vollen Satz und wies es ab. Damit war nicht ein
  Befehl kaputt, sondern **das Tor zu allen** - der Test danach konnte gar
  nicht stattfinden.
  - **Dieselbe Lockerung wie beim Schlusssatz des Diktats einen Tag
    vorher**, nur hatte ich sie damals nur dort angewandt. Jetzt genügt das
    **Kernwort**, wenn ausser Wörtern der Phrase nichts weiter vorkommt und
    kein `[unk]` dabei ist.
  - **Das Kernwort muss eindeutig sein, und das ist der interessante
    Teil.** „stoppen" kommt in genau einem Satz der Grammatik vor, genügt
    also immer. „starten" kommt in zwei vor - „Sprachsteuerung starten" und
    „Diktat starten". Allein genügt es deshalb nur im **ausgeschalteten**
    Zustand, wo die Grammatik nur einen Satz kennt; eingeschaltet wäre es
    zweideutig, und ein falsch geratenes Diktat wäre schlimmer als ein
    nicht erkannter Satz. Gegen zehn Fälle geprüft, darunter
    `'diktat starten'`, das korrekt **nicht** greift.
  - **Im nächsten Lauf wurde der Satz vollständig erkannt** - die Lockerung
    war also nicht nötig und ist im echten Betrieb noch ungeprüft. Sie
    bleibt als Versicherung.

- **Wetter auf Nachfrage: gebaut, gemessen, wieder entfernt
  (2026-08-19).** Stephan wollte „Wie wird das Wetter?". Der Befehl kann am
  Einsatzort nicht funktionieren, und die Messkette dahinter ist
  festgehalten, damit sie niemand wiederholen muss:
  - GeoClue sieht neun WLAN-Netze, beaconDB ist erreichbar (HTTP 200 in
    0,4 s) - kennt aber **keines** davon und fällt auf IP-Ortung zurück
    (`"fallback":"ipf"`). Heraus kommt Wien mit 26 km Ungenauigkeit, rund
    300 km vom tatsächlichen Standort.
  - Der Schwellwert von 10 km verwirft das **korrekt**. Der Befehl hätte
    fast immer nur geantwortet, dass er nichts abrufen kann - und ein
    Befehl, der nie funktioniert, ist für einen blinden Nutzer schlechter
    als keiner: Er kann nicht nachsehen, ob es an ihm oder am System liegt.
  - **Zwei eigene Fehlvermutungen auf dem Weg:** Erst hielt ich die
    GeoClue-Freigabe für die Ursache - sie greift, weil das Skript sich
    ausdrücklich als `dialos-start-ansage` anmeldet und die Freigabe an
    diesem Namen hängt. Dann verdächtigte ich den abgeschalteten
    Mozilla-Dienst - Debian hat längst auf beaconDB umgestellt. Erst die
    Anfrage mit erfundenen Netzkennungen zeigte den IP-Rückfall.
  - **In der Start-Ansage bleibt das Wetter**, weil es dort ohne Nachfrage
    einfach ausfällt und niemand darauf wartet. Die Begründung steht im
    Kopf von `dialos-auskunft.py` an der Stelle des entfernten Befehls -
    wer in einem Jahr fragt, findet dort die 26 Kilometer statt es neu
    herauszufinden.

- **Bestätigt statt geändert: die Sprachsteuerung bleibt an, bis sie
  gestoppt wird (Stephan, 2026-08-19).** Ich hatte vorgeschlagen, sie nach
  kurzen Auskünften automatisch abzuschalten - Stephan hat es abgelehnt,
  und es bleibt bei: einschalten mit „Sprachsteuerung starten", ausschalten
  durch den Nutzer oder nach zwei Minuten durch Michael, mit Ansage. Zwei
  Feinheiten dazu nachgeprüft: Die zwei Minuten laufen ab dem **letzten
  Befehl**, nicht ab dem Einschalten, und während eines Diktats laufen sie
  gar nicht.

- **Der Einkaufszettel lässt sich jetzt verwalten, nicht nur füllen
  (Stephans Frage, 2026-08-18).** Er fragte: „Wenn ich heute was in den
  Einkaufszettel schreibe, wie kann ich den jederzeit abhören, ergänzen und
  wenn der Einkauf zuhause ist löschen?" Damit war klar, dass „aufnehmen"
  allein zu wenig ist. Neues Skript `dialos-notiz.py`, vier neue
  Sprachbefehle in [docs/sprachbefehle.md](docs/sprachbefehle.md).
  - **Ergänzen brauchte kein neues Programm** - das Diktat schrieb schon
    immer an die Datei an, nicht darüber.
  - **Vor dem Leeren wird zurückgefragt**, nach der Projektregel für
    unumkehrbare Befehle. Und dahinter liegt ein Netz: Der alte Inhalt
    wandert nach `einkaufszettel-verworfen.txt`. Für den Nutzer ist der
    Zettel weg, aber ein sehender Helfer kann ihn zurückholen - das deckt
    genau den Fall ab, den eine Rückfrage nicht abdeckt, nämlich dass der
    Nutzer „ja" sagt und es hinterher bedauert.
  - **Zwei Sätze für dasselbe Leeren** (Stephans Wunsch): „Einkauf
    erledigt" beschreibt die Situation, „Einkaufszettel wegwerfen" die
    Handlung.

- **„löschen" steht nicht im Wortschatz des Modells - und das wäre
  lautlos schiefgegangen (2026-08-18).** Der naheliegende Befehl
  „Einkaufszettel löschen" ist unmöglich: Vosk meldet
  `Ignoring word missing in vocabulary: 'löschen'` und wirft das Wort still
  aus der Grammatik. Der Befehl wäre nie ausgelöst worden, und im Protokoll
  hätte nur „einkaufszettel" gestanden - ohne Hinweis auf die Ursache.
  Dieselbe Falle wie „gnome" → „genug", nur leiser.
  - **Dabei ein besseres Prüfverfahren gefunden**, das jetzt als Regel in
    `sprachbefehle.md` steht: Vosk meldet fehlende Wörter beim **Bauen der
    Grammatik** selbst. Das geht sofort und ohne Sprechen - der bisherige
    Weg über Piper braucht eine halbe Minute je Satz. Ebenfalls nicht im
    Wortschatz: „zurücksetzen", „aufräumen".
  - **Gewählt wurden Wörter, die nachweislich drin sind:** wegwerfen,
    leeren, erledigt, streichen, entfernen, verwerfen, abhaken.

- **Ansagen werden grammatisch gebaut, nicht zusammengesetzt
  (2026-08-18).** Beim Trockentest kam „Der einkaufszettel hat 10
  Einträge" heraus - klein geschrieben, weil ich den Dateinamen in den Satz
  eingebaut hatte. Bei der anderen Notiz wäre daraus „Der notizen ist leer"
  geworden, falsches Geschlecht und falscher Numerus. Jetzt gibt es eine
  kleine Tabelle mit Bezeichnung, Verbform und Pronomen: „Der
  Einkaufszettel ist leer" gegen „Die Notizen sind leer", „Soll ich ihn
  löschen?" gegen „Soll ich sie löschen?".
  - **Für einen Nutzer, der ausschließlich zuhört, ist die Ansage der ganze
    Text**, den er von DialOS bekommt. Ein falscher Artikel ist dort kein
    Schönheitsfehler, sondern der Unterschied zwischen einem Programm, das
    spricht, und einem, das Platzhalter vorliest.

- **Die gelockerte Schlussregel hat sich im ersten Lauf bewährt
  (2026-08-18).** Belegt: `Schlusssatz erkannt: 'diktat beenden beenden'` -
  genau die Ausgabe, an der die vorherige, exakte Bedingung gescheitert
  wäre. Vorher hatte ein Diktat deshalb sieben Minuten offen gestanden und
  42 Einträge Raumgeräusch mitgeschrieben.
  - **Der Fehler dahinter war keine Überraschung**, und das ist das
    Unangenehme: Ich hatte die exakte Übereinstimmung am selben Morgen
    selbst als Restrisiko in die Doku geschrieben - „die Bedingung ist das
    einzige, was dazwischen steht" - und sie dann so gelassen. **Ein
    notiertes Risiko ist kein behandeltes Risiko.**
  - **Die neue Bedingung stammt aus den Messdaten**, nicht aus einem
    Gefühl: Der Schluss-Erkenner lieferte in sieben Minuten Dauergerede
    genau zwei Ergebnisse ausser „[unk]", und beide waren „beenden" -
    jeweils, als Stephan es gesagt hat. Ein falsches Ergebnis kam nie
    zustande. Entscheidend ist das Fehlen von „[unk]": Es kennzeichnet,
    dass noch etwas anderes gesprochen wurde.

- **Offen und ungeklärt: Zwei Diktate haben nichts aufgenommen
  (2026-08-18, letzter Lauf des Tages).** Im Protokoll steht zwischen
  „Modell geladen" und „Schlusssatz erkannt" keine einzige `erkannt:`-Zeile,
  beim zweiten Lauf über 26 Sekunden hinweg. Der Einkaufszettel blieb leer,
  und „vorlesen" und „Einkauf erledigt" wurden dadurch nie ausgeführt - das
  Notiz-Protokoll ist leer. **Bewusst keine Vermutung festgehalten**, weil
  keine belegt ist. Erster Punkt für den nächsten Tag.

- **Das Diktat läuft - erster Anwendungs-Baustein fertig und live belegt
  (2026-08-18).** `dialos-diktat.py` nimmt auf, erkennt frei mit dem grossen
  Vosk-Modell, lässt LanguageTool die Gross- und Kleinschreibung richten und
  schreibt eine Notiz nach `~/Notizen`. Mit Stephans Stimme getestet:
  „tomaten bananen äpfel" wörtlich richtig, in einer Sekunde zu „Tomaten
  Bananen Äpfel" gemacht. Alle Messungen in
  [docs/diktat.md](docs/diktat.md), der Einbau in
  [Debian-zu-DialOS.md](docs/Debian-zu-DialOS.md) Schritt 11h.
  - **LanguageTool eingebaut, nach Messung und mit Stephans Freigabe.**
    98,1 % richtige Schreibung gegen 90,6 bis 92,5 % aller vier
    lexikalischen Verfahren. Es läuft als örtlicher Dienst über systemd
    (`Restart=on-failure`), gebunden auf 127.0.0.1 - geprüft, dass es von
    der Netzadresse des Rechners nicht erreichbar ist. Der öffentliche
    Dienst von languagetool.org wird nie benutzt; er würde die Briefe und
    Mails des Nutzers auf einen fremden Rechner schicken. Java kommt als
    Debian-Paket, nur LanguageTool selbst ist ein Fremdpaket - das erste im
    Projekt.
  - **Bewusst vorsichtig:** Übernommen werden ausschliesslich reine
    Schreibungs-Korrekturen. LanguageTool wollte im Test „milch" zu „mich"
    verbessern - ein diktierter Text darf nicht inhaltlich verändert
    werden. Gegenprobe am installierten Skript: „bitte kaufe milch" wird zu
    „Bitte kaufe Milch".
  - **Und wenn die Schreibhilfe nicht läuft**, wird trotzdem geschrieben,
    nur klein, mit Ansage. Ein fehlender Grossbuchstabe ist ein
    Schönheitsfehler, ein verlorener Satz ist einer zu viel.

- **Der Schlusssatz brauchte einen zweiten Erkenner - mein Entwurf war an
  dieser Stelle falsch gebaut (2026-08-18).** Ich hatte „diktat beenden" in
  der freien Erkennung gesucht. Stephan sagte es, das Protokoll zeigt
  `'diktat wird erhöht'`. **Das war die dritte Begegnung mit demselben
  Effekt** - „gnome" wurde zu „genug", „windows" zu „sinnlose". Zweimal
  hätte gereicht, um die Regel zu ziehen: Ein *bestimmter* Satz ist in
  freier Erkennung nicht zuverlässig zu treffen.
  - **Behoben mit zwei Erkennern über demselben Audio:** der grosse für den
    Text, ein kleiner mit einer Grammatik aus genau einem Satz für den
    Schluss. Kosten 0,4 s und 229 MB gegenüber 5,5 GB - belanglos. Im
    nächsten Lauf traf er den Satz wörtlich.
  - **Restrisiko, festgehalten statt weggelächelt:** Eine Grammatik mit nur
    einem Satz versucht, diesen Satz überall zu hören. Aus „Tomaten Bananen
    Äpfel" machte der kleine Erkenner `'beenden beenden [unk]'`. Gestoppt
    hat er nicht, weil exakte Übereinstimmung verlangt wird - aber diese
    Bedingung ist das einzige, was dazwischen steht.

- **Die Trennung von Diktat und Befehlserkennung ist bewiesen, nicht nur
  beabsichtigt (2026-08-18).** Stephan hat mitten im Diktat absichtlich
  „auf Windows umschalten" gesprochen. Der Satz landete als Text in der
  Notiz, der Schreibtisch blieb unberührt, und im Protokoll des
  Befehlsdienstes steht `14:55:31 Diktat laeuft - ich hoere nicht zu` bis
  `14:55:45 Diktat beendet` - dazwischen kein einziger erkannter Satz.
  - **Der Beweis kostete zwei Anläufe, beide an meinen Protokollen
    gescheitert.** Beim ersten Test schrieb das Diktat nur ins Terminal;
    hinterher war nicht feststellbar, WAS erkannt worden war. Beim zweiten
    hatte der Befehlsdienst keine Zeitstempel, also liess sich nicht
    zeigen, ob sein erkannter Satz WÄHREND des Diktats kam. **Ein Protokoll
    ohne Uhrzeit kann Gleichzeitigkeit nicht belegen** - und genau darum
    ging es bei dieser Sperre. Beides nachgerüstet.
  - **Eine Aussage von mir war dabei unbegründet und ist zurückgenommen:**
    Ich hatte nach dem ersten Test gemeldet, die Trennung habe gehalten.
    Der laufende Dienst startete aber um 13:19, die Datei mit der Sperre kam
    um 14:32 - er kannte sie gar nicht. Dass sich nichts rührte, hatte einen
    anderen Grund.

- **Piper sprach jedes Mal anders - gefunden, weil Stephan es gehört hat
  (2026-08-18).** Seine Beobachtung: Die vorgelesene Notiz passt nicht zum
  Tempo der übrigen Ansagen. Derselbe Text ergab in fünf Durchläufen 2,456
  bis 2,865 s - **17 % Streuung**, ohne dass sich eine Einstellung geändert
  hatte. Ursache ist der Zufallsanteil in der Lautdauer des VITS-Modells
  (`--noise_w`, Standard 0.8). Auf 0 gesetzt ist die Ausgabe auf die
  Millisekunde reproduzierbar; Stephan hat die Varianten im Hörvergleich
  entschieden.
  - **Meine erste Erklärung war falsch und wurde durch Messung widerlegt.**
    Ich hatte unterschiedliche sox-Ketten verdächtigt (Speicher gegen
    speech-dispatcher) und schien mit 2,918 gegen 2,575 s recht zu haben.
    Mit **einer** Piper-Ausgabe durch beide Ketten kommt beides bei 2,549 s
    heraus - die Differenz kam daher, dass ich Piper zweimal aufgerufen
    hatte.
  - **Der Ansagen-Speicher wird erst dadurch richtig.** Er friert eine
    Ausgabe ein; solange Piper würfelte, klang gespeichert hörbar anders als
    frisch gesprochen. Nachgeprüft: Speicher-Datei 0,939 s, frisch erzeugt
    0,939 s.
  - **Und alle Sprechdauer-Messungen dieses Projekts waren Stichproben,
    keine Zahlen.** „1,13 s für ‚Ich höre.'" hatte eine unbekannte Streuung
    von bis zu 17 %. Erst jetzt ist ein Vergleich zwischen zwei
    Einstellungen aussagekräftig.
  - **Nebeneffekt: rund 12 % kürzere Ansagen** ohne Eingriff ins Tempo.
    „Ich höre." fiel von 1,13 s auf 0,939 s.
  - **Der Schalter steht an zwei Stellen** - in `piper-generic.conf` und in
    der Speicher-Kette von `dialos-say.py`. Laufen sie auseinander, klingt
    gespeichert wieder anders als frisch.

- **Der Anwendungsblock hat begonnen: festgelegt, welches Programm welchen
  Zweck erfüllt (Stephan, 2026-08-18).** Neue Datei
  [docs/anwendungen.md](docs/anwendungen.md) - eine Tabelle Zweck →
  Programm mit Begründung, getrennt nach gesetzt, freigegeben-noch-nicht-
  gebaut und offen.
  - **Das Auswahlkriterium ist nicht Bedienbarkeit, sondern Steuerbarkeit
    von außen.** Der Nutzer sieht den Bildschirm nicht; ein Programm, das
    nur über seine Oberfläche zu bedienen ist, ist für DialOS wertlos -
    auch wenn es das beste seiner Art wäre. Daran ist gleich ein
    installiertes Programm gescheitert: `gnome-podcasts` (25.2) ist da und
    funktioniert, hat aber keine Kommandozeile und ist damit keine Option,
    obwohl es die naheliegende gewesen wäre.
  - **Gesetzt:** Firefox ESR (Browser), Thunderbird (Mail, Kalender,
    Kontakte - ein Programm für alle drei, weil jedes weitere einen
    weiteren Satz Sprachbefehle bedeuten würde), RustDesk (Support),
    Shortwave (Radio - wegen der Stationsdatenbank, nur damit lässt sich
    ein gesprochener *Name* in einen Stream auflösen), Rhythmbox (Musik,
    Podcasts, Hörbücher), LibreOffice Writer (Briefe), Jitsi im Firefox
    (Videochat), `unattended-upgrades` plus Sprachbefehl (Updates).
  - **Notizen bewusst ohne Programm.** Ein Einkaufszettel muss vorgelesen,
    ergänzt und abgehakt werden, alles per Sprache - jede Oberfläche ist
    dafür ein Umweg, den der Nutzer nie sieht. DialOS verwaltet sie als
    `.txt` in einem Ordner: nichts zu installieren, nichts das bei einem
    Update kaputtgeht, und der Zettel bleibt lesbar, auch wenn DialOS mal
    nicht läuft.
  - **Vollständig freigegeben, noch nicht gebaut** (Stephans „deine Punkte
    müssen alle mit rein"): Diktat, Vorlesen, Post einscannen und
    vorlesen, Hörbücher, Wecker/Timer/Erinnerungen, Ausschalten und
    Sperren per Sprache, Termine und Wetter ansagen.
  - **Die wichtigste Erkenntnis daraus:** Diktat und Vorlesen sind keine
    Anwendungen, sondern Voraussetzungen für vier der obigen - Briefe,
    Notizen, Mail und Chat kann der Nutzer ohne Diktat gar nicht erzeugen.
    Und es ist billiger als befürchtet: **`vosk-model-de-big` mit 3,2 GB
    liegt schon auf der Platte.** Freies Diktat braucht keine neue
    Technik, nur den Betriebsartwechsel zwischen eingeschränkter
    Befehlsgrammatik und freier Erkennung.
  - **Telefonie nach hinten gestellt** (Stephans Entscheidung). Sie hängt
    an der Hardware-Frage aus `telefonie.md`. Videochat ist davon
    ausdrücklich **nicht** betroffen - Jitsi braucht keine zusätzliche
    Hardware, Kamera und Mikrofon sind da und erkannt.
  - **Offen geblieben:** Chat (WhatsApp ist in `telefonie.md` priorisiert,
    Bestätigung für die Liste fehlt) und der Zweck der Videoaufnahme - eine
    Videobotschaft an die Familie ist etwas anderes als „festhalten, was
    der Handwerker gesagt hat", und davon hängt die Wahl ab.

- **Zwei Regeln, die aus der Anwendungsliste folgen - beide aus einer
  Messung, nicht aus Vorsicht (2026-08-18).**
  - **Nur ein Player darf gleichzeitig laufen.** Sagt der Nutzer „lauter"
    oder „stopp" und es läuft Musik in einem und ein Podcast in einem
    anderen Programm, ist der Befehl nicht mehr eindeutig - und er kann
    nicht nachsehen, welches Fenster vorn ist. Deshalb Rhythmbox für
    Musik, Podcasts UND Hörbücher: Es bleiben genau zwei Player.
  - **Die echo-bereinigte Quelle darf nie die Vorgabe-Quelle werden.**
    Geprüft: Der Sprachdienst nimmt von `dialos_mikrofon_ohne_echo` auf,
    Firefox von der rohen internen Quelle. Genau so muss es sein, denn
    Firefox bringt für WebRTC seine eigene Echo-Unterdrückung mit -
    bekäme es unsere bereinigte Quelle, liefe die Verarbeitung doppelt und
    die Gegenseite hörte dünne, verwaschene Sprache. Es stimmt derzeit
    nur, weil es WirePlumbers Standard ist; festgelegt hatte es niemand.

- **Rhythmbox merkt die Abspielposition nicht - der Fund, der die
  „ein Player"-Empfehlung fast gekippt hat (2026-08-18).** Stephan hat die
  Merkposition ausdrücklich als Ausschlusskriterium genannt: Wer ein
  achtstündiges Hörbuch nach dem Einschalten von vorn beginnen muss, hört
  es nicht. Geprüft: Rhythmbox' Bibliothek kennt `play-count` und
  `last-played`, aber **kein** `playback-position` und kein `bookmark`.
  - **Die Antwort ist kein zweiter Player**, das würde die Regel oben
    brechen, sondern: **DialOS liest die Position über MPRIS und setzt sie
    wieder.** Die MPRIS-Erweiterung ist in Rhythmbox vorhanden, `gdbus`
    ist installiert.
  - **Und das ist nicht der Notbehelf, sondern die bessere Lösung.**
    DialOS muss die Position ohnehin kennen, um sie ansagen zu können -
    „weiter bei drei Stunden zwölf" kann kein Player für uns sprechen. Es
    ist dieselbe Regel, die am 2026-08-17 dreimal zugeschlagen hat: nicht
    auf den Zustand einer fremden Komponente verlassen, sondern den
    eigenen führen.
  - **Ein zweiter eigener Fehler beim Prüfen:** Mein erster Test war
    `strings` auf `/usr/bin/rhythmbox` - null Treffer für „podcast", was
    nach fehlender Unterstützung aussah. Der Test war wertlos, weil der
    Code in der Bibliothek steckt, nicht im Startprogramm. Erst das
    GSettings-Schema `org.gnome.rhythmbox.podcast` und die Suche in
    `librhythmbox-core.so` haben belastbare Antworten geliefert - einmal
    ja (Podcasts), einmal nein (Position).

- **Korrektur an mir selbst: „die Paketquellen sind nicht aktuell" war
  falsch (2026-08-18).** Ich hatte gemeldet, `apt-cache policy` liefere
  für alles „nicht in den Quellen". Ursache war mein eigenes Suchmuster,
  das an der deutschen Ausgabe vorbeiging. Tatsächlich verfügbar:
  `gpodder` 3.11.3, `tesseract-ocr` 5.5.0, `playerctl` 2.4.1,
  `unattended-upgrades` 2.12, `ffmpeg` 7.1.5.

- **Eingabe und Ausgabe sind festgelegt - und die Vereinfachung löst
  gleich zwei Probleme mit, die wir sonst noch hätten lösen müssen
  (Stephans Entscheidung, 2026-08-17).** Eingabe ist **immer** das
  eingebaute Mikrofon, Ausgabe der Bluetooth-Lautsprecher solange er
  wirklich abspielt, sonst die eingebauten Lautsprecher. Externe Mikrofone
  kommen zum Schluss noch einmal dran.
  - **Das eigentlich Wichtige daran ist nicht die Vereinfachung.** Wenn
    DialOS nie ein Bluetooth-Mikrofon öffnet, kann das Gerät auch nie in
    HFP rutschen - die A2DP/HFP-Zwangswahl fällt damit weg, nicht weil wir
    sie gelöst hätten, sondern weil wir sie nicht mehr berühren. Sie hat
    bisher die Tonqualität der Videoaufnahme gekostet und steckt in
    mehreren offenen Punkten. Und der Totalausfall von heute wird
    strukturell unmöglich: Die Echo-Unterdrückung braucht ihr
    Aufnahmegerät als Taktgeber, und ein eingebautes Mikrofon kann man
    nicht ausschalten.
  - **Neu gebaut: `dialos-ton-ausgabe.py`** mit
    `/etc/xdg/autostart/dialos-ton-ausgabe.desktop`. Er läuft die ganze
    Sitzung mit, weil der Lautsprecher auch mitten in der Sitzung ein-
    oder ausgeschaltet werden kann, und wartet über `pactl subscribe` auf
    Ereignisse statt im Sekundentakt nachzufragen.
  - **Er glaubt keiner Zustandsmeldung.** Statt zu prüfen, ob ein Gerät
    „da" ist, schickt er 150 ms Stille hin und schaut mit Zeitlimit, ob
    der Aufruf durchläuft. Genau der Fall von heute - Senke meldet
    `RUNNING`, nimmt den Strom an, spielt nie - fällt damit auf. Stille
    als Testton, damit der Nutzer nicht bei jedem Ereignis ein Piepen
    hört.
  - **Beim Anmelden wird gewählt, aber nicht angesagt.** Dieselbe Lehre
    wie bei der Desktop-Wiederherstellung von heute: Wer sich anmeldet,
    hat nichts umgeschaltet, und eine Ansage würde der Start-Ansage ins
    Wort fallen.
  - **Zwei Fehler beim Bauen, beide von mir.** Erstens hätte der eigene
    Testton eine Endlosschleife ausgelöst: Er erzeugt selbst ein
    `sink-input`-Ereignis, und mein Filter hörte auf „sink". Vor dem
    ersten Lauf gefunden. Zweitens kam die Ansage im Test **nicht**,
    obwohl der Ton korrekt wanderte - ich verglich mit der Vorgabe-Senke
    des Systems, und die hatte WirePlumber schon umgestellt, bevor mein
    Dienst hinsah. Beide Seiten kamen zum selben Ergebnis, also schwieg
    er. Jetzt merkt er sich seine **eigene** letzte Wahl. Derselbe
    Fehlertyp wie zweimal zuvor an diesem Tag: einer Zustandsmeldung
    geglaubt, statt die eigene Sache mitzuführen.
  - **Danach live bestätigt** (Stephan, Lautsprecher aus und wieder an):
    beide Wechsel im Protokoll als echte Änderung, beide Ansagen als neue
    Speicher-Dateien belegt, und „hat aber jetzt funktioniert".

- **Die Sperrfrist ist ganz entfallen - und ich hatte denselben Fehler am
  Morgen schon halb behoben (2026-08-17).** Stephan meldete, Befehl 1 und
  2 gingen normal, Befehl 3 und 4 habe er „viel lauter" sprechen müssen.
  Befehl 2 war ein echtes Umschalten. Danach war der Dienst **rund fünf
  Sekunden taub:**

  | Abschnitt | Dauer |
  |---|---|
  | Umschalt-Skript läuft und spricht dabei, blockiert den Dienst | 2,4 s |
  | Sperrfrist danach | 2,0 s |
  | Nachhall-Pause, dann neue Aufnahme | 0,7 s |
  | **zusammen** | **≈ 5,1 s** |

  Die Ansage endet aber nach 1,5 s. Der Nutzer hört also die Antwort,
  spricht weiter - und redet 3,6 Sekunden gegen ein taubes System. Dann
  wiederholt er lauter, und in dem Moment ist die Frist gerade abgelaufen.
  **Lauter war nie die Lösung, nur das Warten.**
  - **Der Vorwurf an mich selbst:** Genau diese Begründung hatte ich am
    Morgen aufgeschrieben, als ich die Frist nach „Ich höre." entfernte -
    und dann nicht auf das Umschalten angewandt, sondern die Zahl von 5 s
    auf 2 s gekürzt. Eine halbe Behebung sieht wie eine Behebung aus und
    kostet einen zweiten Testlauf.
  - **Nötig war sie ohnehin nicht mehr.** Sie sollte verhindern, dass ein
    langgezogener Satz mehrfach auslöst; das erledigt seit heute früh
    schon das Verwerfen und Neubeginnen der Aufnahme nach jedem Sprechen.
    Taub bleibt der Dienst jetzt nur, solange er spricht, plus 0,7 s.
  - **Belegt:** Zwei vollständige Durchläufe mit Stephans Stimme, sieben
    Befehle, alle erkannt, ohne lauter zu werden.

- **Gemessen, wie die Lautstärke des Bluetooth-Lautsprechers wirklich
  geregelt wird - und ich muss eine Empfehlung zurücknehmen
  (2026-08-17).** Auslöser war Stephans Wunsch, die Ansagen 30 % leiser
  zu machen, und seine Frage, wie man das Gerät dauerhaft auf 100 % stellt
  und alles über das OS regelt.

  | Weg | Was passiert | Wirkt es? |
  |---|---|---|
  | Senken-Lautstärke (GNOME-Regler, `pactl`) | Wert geht **per AVRCP ans Gerät**, das Signal bleibt unverändert | ja, hörbar |
  | Dämpfung im Signal (Datei, sox, `paplay --volume`) | Signal verlässt den Laptop korrekt gedämpft | **nein** - der AIRHUG rechnet es weg |

  Der Nachweis ist eine Messung am Monitor der Bluetooth-Senke, also an
  dem, was den Laptop verlässt: Bei halber Amplitude in der Datei kommt
  dort **0,071559** gegen **0,143117** an, genau Faktor 0,5000. Bei
  Senke 100 % gegen Senke 30 % dagegen **beide Male 0,143117**, auf die
  letzte Stelle identisch - die Senken-Lautstärke wird also gar nicht ins
  Signal gerechnet, sondern dem Gerät befohlen. Am Laptop-Lautsprecher
  ist die Dämpfung im Signal umgekehrt hörbar (von Stephan bestätigt).
  - **Zurückgenommen:** Ich hatte `bluez5.enable-hw-volume = false`
    vorgeschlagen, damit das Gerät auf 100 % bleibt und das OS in Software
    regelt. Das wäre genau falsch gewesen - dann würde DialOS auf dem Weg
    dämpfen, der beim AIRHUG nachweislich nichts bewirkt, und es gäbe
    **überhaupt keine** Lautstärkeregelung mehr. Der Vorschlag beruhte auf
    meiner Annahme, Software-Dämpfung käme an; die Messung sagt das
    Gegenteil.
  - **Stephans Ziel ist damit schon erfüllt:** Der GNOME-Regler *ist* das
    OS, das den Lautsprecher steuert - er tut es, indem er dem Gerät einen
    Wert schickt, statt am Signal zu drehen.
  - **Nebenbefund, der eine ganze Funktion betraf:** Unsere sox-Kette
    endet auf `norm`, und das hebt jede Ausgabe wieder auf Vollausschlag.
    Damit ist `GenericVolume` in DialOS **wirkungslos** - speech-dispatcher
    kann die Lautstärke gar nicht regeln, und das war nie aufgefallen,
    weil es nie jemand gebraucht hat. Aufgefallen ist es nur, weil mein
    erster Vorführversuch zweimal identisch laut war (RMS 0,1428 gegen
    0,1489).
  - **Folge für „Ansagen 30 % leiser":** Am Laptop-Lautsprecher machbar,
    am AIRHUG nicht - dort wirkt nur die Geräte-Lautstärke, und die gilt
    für alles. Ein AVRCP-Befehl kostet gemessen nur 19-36 ms, ein kurzes
    Absenken während der Ansage wäre also bezahlbar. Noch nicht gebaut,
    Entscheidung offen.

- **Dreifach geprüft und bestätigt: Der AIRHUG meldet seine Lautstärke
  nie zurück (2026-08-17).** Anlass war eine Beobachtung, die dem Befund
  vom Mittag zu widersprechen schien - die Senke stand plötzlich auf 70 %,
  ohne dass DialOS etwas getan hatte. Geprüft wurden drei Bedingungen:
  Tastendruck ohne Ton, Start einer Wiedergabe, und Tastendruck **während**
  laufender Wiedergabe. In allen drei Fällen blieb der Wert unverändert.
  - **Die 70 % bleiben unerklärt.** Drei Erklärungsversuche sind
    widerlegt, WirePlumbers gespeicherter Wert steht auf 100 %, und im
    Ereignisprotokoll gab es keinen Neuaufbau der Senke im passenden
    Zeitraum. Eine vierte Vermutung wäre geraten - festgehalten in
    `TODO.md`, damit ein zweites Auftreten einen zweiten Datenpunkt
    liefert statt wieder von vorn zu beginnen.

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
