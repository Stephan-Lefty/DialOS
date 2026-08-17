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
- [ ] **Fahrplan bis zur echten Sprachsteuerung** (festgelegt mit Stephan
  am 2026-08-16, in dieser Reihenfolge):
  1. Referenz-Mikrofon festlegen - **erledigt**, AIRHUG 01.
  2. **Windows-11-Umschaltung für den Desktop** - **gebaut am 2026-08-16**,
     Live-Test steht noch aus (siehe nächster Punkt).
  3. Aufweckwort + dauerhafte Zuhör-Schleife - **teilweise erledigt am
     2026-08-16**: Die Zuhör-Schleife läuft
     (`dialos-sprachbefehl-desktop.py`), ein Aufweckwort gibt es noch
     nicht. Es fehlt bisher auch nicht, weil die eingeschränkte
     Grammatik nur drei feste Sätze zulässt.
  4. hassil-Befehlsgrammatik - **die Desktop-Umschaltung als erster
     echter Sprachbefehl ist am 2026-08-16 erledigt**, allerdings direkt
     über eine Vosk-Grammatik statt über hassil. hassil lohnt sich erst,
     wenn es mehrere Befehle mit Varianten gibt.

- [x] **Optionale Windows-11-Optik für GNOME gebaut** (Stephans Wunsch
  vom 2026-08-16, umgesetzt am selben Tag).
  `/usr/local/bin/dialos-desktop-stil.sh` schaltet in beide Richtungen um
  (`windows` / `gnome` / `status`), die drei Debian-Erweiterungen
  (`dash-to-panel`, `arc-menu`, `tiling-assistant`) stehen in der
  Paketliste und werden mitinstalliert, aber nicht eingeschaltet.
  Beschrieben in `docs/Debian-zu-DialOS.md`, Schritt 11b.

- [x] **Windows-Umschaltung technisch getestet (2026-08-16).** Pakete
  installiert, dreimal hin- und hergeschaltet, jeden berührten Schlüssel
  verglichen: Rückweg stellt den Auslieferungszustand her, mehrfaches
  Ausführen erzeugt keine Doppeleinträge. Dabei zwei Fehler gefunden und
  behoben (GNOME Shell kennt frisch installierte Erweiterungen nicht;
  ArcMenu-Schema liegt in Debian im falschen Ordner) - Details im
  Änderungsprotokoll.

- [x] **Sprachbefehl live getestet und läuft (2026-08-16, von Stephan
  bestätigt).** Dabei kam heraus, dass das eingebaute Mikrofon um 60 dB
  übersteuert war - der Dienst konnte prinzipiell nichts erkennen.
  Behoben und dauerhaft abgesichert (`dialos-mikrofon-pegel.service`).

- [ ] **Bluetooth-Profil gegen Hängenbleiben absichern** (offen seit
  2026-08-17). Nach dem Neustart stand der AIRHUG auf `headset-head-unit`
  statt `a2dp-sink` - die Wiedergabe lief dauerhaft in Telefonqualität,
  ohne dass es jemand bemerkt hätte, der das Gerät nicht kennt.
  `dialos-start-ansage.py` schaltet für die Lautstärke-Frage bewusst auf
  HFP und danach zurück; endet das Skript vorher (Abbruch, Abmelden,
  Zeitüberschreitung), bleibt das Profil hängen. Nötig ist ein Riegel,
  der unabhängig vom Skriptende greift - etwa eine Prüfung beim Anmelden
  oder ein `trap` auf das Skriptende.

- [x] **Ursache der Mikrofon-Übersteuerung geklärt (2026-08-17).** Der
  systemweite Dienst läuft beim Booten, WirePlumber stellt seinen Zustand
  erst in der Sitzung wieder her und hebt den Boost dabei zurück - der
  Dienst war strukturell zu früh dran. Der Sprachdienst richtet den Pegel
  jetzt selbst, nachdem er die Aufnahme geöffnet hat, und regelt bei
  anhaltender Übersteuerung nach. Getestet durch absichtliches
  Hochdrehen.

- [x] **Fehlauslösung durch abgespielte Inhalte behoben (2026-08-17).**
  Echo-Unterdrückung über PipeWires `module-echo-cancel` eingerichtet,
  32 dB Dämpfung gemessen, und der Fall, der vorher scheiterte (Ansage
  per `paplay` abgespielt), löst nichts mehr aus. Details im
  Änderungsprotokoll und in `docs/Debian-zu-DialOS.md`, Schritt 11f.

- [x] **Schalter „Sprachsteuerung starten/stoppen" gebaut
  (2026-08-17).** Zwei Zustände mit eigener Grammatik, Ansage bei jedem
  Wechsel, Abschaltung nach zwei Minuten. Die offene Zustandsfrage ist
  damit beantwortet: Der Nutzer hört jeden Wechsel. Live-Test mit echter
  Stimme steht noch aus.

- [x] **So stand die Aufgabe vorher da (zur Herkunft):** Bis zum „starten" hört DialOS nur auf
  diesen einen Satz, danach nimmt es Befehle an, bis „stoppen" kommt.
  Gemessen ist bereits, dass die Erkennung trägt und drei Störsätze ruhig
  bleiben - offen ist der Zustand selbst: Wo wird er gemerkt (Datei wie
  bei der Desktop-Optik?), was passiert beim Anmelden (an oder aus?), und
  **wie erfährt ein blinder Nutzer, in welchem Zustand er ist**? Ohne
  eine Antwort darauf ist der Schalter gefährlicher als kein Schalter:
  Wer nicht weiß, dass die Erkennung aus ist, hält das Gerät für kaputt.

- [ ] **Pausen zwischen den Sätzen der Ansage prüfen** (offen seit
  2026-08-17). Michael klang „hektisch", gewählt wurde dann aber ein
  schnelleres Tempo - das spricht dafür, dass die fehlenden Atempausen
  zwischen den Sätzen das eigentliche Problem sind, nicht die
  Geschwindigkeit. Piper hängt Sätze fast ohne Pause aneinander. Eine
  kurze Pause je Satzende, zentral in `dialos-say.py`, würde die Ansage
  ruhiger machen, ohne einzelne Wörter schleppen zu lassen. Vorher eine
  Hörprobe bauen: gleiches Tempo, nur mit Pausen.

- [x] **Ansagen unterscheiden: Frage oder Hinweis - gebaut am
  2026-08-17.** `dialos-say.py --frage`, Standard ist die natürliche
  Satzmelodie aus dem Fragezeichen, der Signalton ist Option über
  `~/.config/dialos/frageton`. Siehe `docs/Debian-zu-DialOS.md`,
  Schritt 11a. Offen bleibt nur, das später per Sprachbefehl umschaltbar
  zu machen („Signalton einschalten") - das braucht erst den Schalter
  „Sprachsteuerung starten/stoppen".

- [x] **Ursprüngliche Beschreibung (Stephans Frage vom 2026-08-17).** Heute weiß das System es implizit - der Code entscheidet
  ja, was gesagt wird -, gibt es aber nirgends weiter: `dialos-say.py`
  bekommt einen Text und spricht ihn. Wichtiger als das Wissen des
  Systems ist, dass **der Nutzer die Frage als Frage erkennt**: Für
  jemanden, der den Bildschirm nicht sieht, ist „wartet es auf mich?" die
  entscheidende Information. Am 2026-08-16 ist genau daran der erste Test
  der Lautstärke-Frage gescheitert - das System fragte, Stephan wusste
  nicht wann. Behelf war der Satz „Und jetzt bitte.". Sauber wäre: der
  Sprachausgabe eine Art mitgeben (Hinweis/Frage), und bei einer Frage
  automatisch ein kurzes, immer gleiches Signal. Ein **Ton** wäre dafür
  besser als ein Satz - schneller, unmissverständlich, nutzt sich nicht ab.

- [ ] **Aufweckwort mit openWakeWord bauen** (entschieden 2026-08-17).
  Die Vosk-Grammatik scheidet aus - sie presst jede Äußerung in die
  nächstliegende Phrase, weshalb "ich rufe michael an" als `hallo
  michael` durchkam, und zwar mit voller Sicherheit (conf 1.00). Ein
  Schwellwert trennt also nicht. Weckphrase soll der Name des
  Assistenten sein ("Hallo Michael", bei weiblicher Stimme "Hallo
  Anna"), gelesen aus derselben Einstellung wie die Stimmenwahl. Details
  in `docs/sprachsteuerung.md`.

- [ ] **Vorführvideo mit Sprachein- und -ausgabe aufnehmen** (Stephans
  Idee vom 2026-08-16, für den nächsten Arbeitstag). Zeigen soll es, was
  DialOS heute wirklich kann: Start-Ansage mit Lautstärke-Frage, dann
  "auf Windows umschalten" / "auf Linux umschalten" per Zuruf. Zu klären
  ist dabei die Tonaufnahme - der Bildschirminhalt allein genügt nicht,
  es müssen sowohl die Sprachausgabe des Systems als auch die gesprochene
  Eingabe hörbar sein. Denkbar wäre `wf-recorder` oder OBS mit zwei
  Tonspuren (Systemklang + Mikrofon); beides ist noch nicht installiert.
  **Achtung bei der Mikrofonwahl:** Der Sprachbefehl-Dienst hört über das
  eingebaute Mikrofon, damit das AIRHUG in A2DP bleibt - eine Aufnahme
  über das Headset-Mikrofon würde die Wiedergabe auf Telefonqualität
  ziehen und das Video schlechter klingen lassen, als das System ist.

- [ ] **Referenz-Audiogerät neu entscheiden - der AIRHUG allein reicht
  nicht** (offen seit 2026-08-17, Stephans Entscheidung). Gemessen ist:
  Das Gerät kann nicht gleichzeitig gut klingen und zuhören (A2DP hat
  `sources: 0`), seine Tasten erreichen den Laptop auf **keinem** Kanal -
  weder als Tastencode noch als AVRCP-Lautstärke -, und seine Lautstärke
  ist von GNOME entkoppelt. Damit fällt der Ausweg aus, per Tastendruck
  kurz auf HFP zu schalten. Drei Möglichkeiten, siehe
  `docs/hardware.md`: zwei Geräte (Mikrofon dauerhaft in HFP beim
  Nutzer, Lautsprecher in A2DP), ein anderer Lautsprecher dessen Tasten
  durchkommen, oder die Auflage dass der Laptop im selben Raum steht.

- [x] **Geklärt am 2026-08-17: Die Lautstärke-Entkopplung gilt nur in
  eine Richtung.** Der Rechner kann den AIRHUG sehr wohl regeln (10 %
  gegen 100 % im Hörvergleich eindeutig); nur seine eigenen Tasten melden
  sich nicht zurück. Meine erste Einschätzung („DialOS kann überhaupt
  nicht regeln") war zu weit gegriffen. Kein Ausschlusskriterium.

- [ ] **Restrisiko dazu:** DialOS kennt die am Gerät eingestellte
  Lautstärke nicht. Hat jemand den AIRHUG am Rad heruntergedreht, hilft
  „mach lauter" nur, solange die Software-Lautstärke noch Spielraum hat -
  bei 100 % bleibt es leise, und die Ursache liegt außerhalb des Systems.
  Zu überlegen: Erkennt DialOS diesen Fall (Software auf 100 %, Nutzer
  sagt weiter „lauter") und sagt dann, dass am Gerät selbst gedreht
  werden muss?

- [ ] **Mikrofon-Vergleich vom 2026-08-13 wiederholen.** Damals galt das
  eingebaute Mikrofon als dem AIRHUG deutlich unterlegen. Am 2026-08-16
  stellte sich heraus, dass ab Werk 60 dB Verstärkung anlagen und das
  Signal dauerhaft übersteuert war - vermutlich hat der Test also nicht
  das Mikrofon gemessen, sondern die Übersteuerung. Solange das nicht
  wiederholt ist, steht die Begründung für die Bluetooth-Priorität auf
  wackligem Grund.

- [ ] **Optische Abnahme der Windows-Optik nach dem Anmelden** (offen seit
  2026-08-16). Die Einstellungen stimmen nachweislich, gesehen hat sie
  aber noch niemand: Die Erweiterungen greifen erst nach einmaligem
  Ab- und Anmelden. Zu prüfen: Taskleiste unten mit mittigen Symbolen,
  ArcMenu-Startmenü links im Windows-11-Layout, Fensterknöpfe rechts,
  Fenster-Andocken am Bildschirmrand. Danach `dialos-desktop-stil.sh
  gnome` und kontrollieren, dass wirklich alles wieder wie vorher
  aussieht. Anschließend dasselbe als `nutzer`.

- [ ] **Rechtschreibprüfung nachrüsten** (`hunspell-de-de`,
  `hunspell-en-us`, `aspell`). Steht in keiner Paketliste. Die frühere
  Begründung in `docs/offene-punkte.md` ("scheitert in der
  Docker-Chroot-Build-Umgebung") ist mit Weg A hinfällig - heute wird auf
  einem laufenden System per `apt` installiert, wo das Problem nicht
  auftritt. Gehört in `iso-build/config/package-lists/desktop.list.chroot`.

- [ ] **Lock-Datei von `dialos-start-ansage.py` aus `/tmp` holen.**
  `/tmp/dialos-start-ansage.pid` ist ein fester Pfad im geteilten `/tmp` -
  dieselbe Bauart, die am 2026-08-16 bei der Sprechen-Markierung zu einem
  stillen Fehlschlag geführt hat (Sticky-Bit: ein Konto kann die Datei
  eines anderen weder überschreiben noch löschen). Die Markierung liegt
  jetzt unter `$XDG_RUNTIME_DIR`, diese Datei noch nicht.

- [ ] **Mikrofon-Fallback ohne Bluetooth testen** (offen seit
  2026-08-16). Die Ausgabeseite ist bewiesen - Headset aus, Ton kam aus
  dem eingebauten Lautsprecher. Die Eingabeseite fehlt noch: versteht das
  eingebaute Laptop-Mikrofon die Lautstärke-Frage?

  **Wichtig, sonst schlägt der Test scheinbar fehl:** Die Frage kommt seit
  2026-08-16 nur noch einmalig. Vorher den gemerkten Wert löschen, sonst
  wird gar nicht gefragt:

  ```bash
  sudo rm /home/nutzer/.config/dialos/lautstaerke
  ```

  Dann AIRHUG **ausschalten**, als `nutzer` ab- und wieder anmelden, und
  ins Laptop-Mikrofon antworten.

  **Erwartung:** deutlich schlechter als über das Headset - der
  Vergleichstest vom 2026-08-13 war eindeutig (6 von 8 Testsätzen über
  Bluetooth korrekt, spürbar weniger beim eingebauten Mikrofon). Für den
  Fallback reicht es, wenn es *überhaupt* trägt: Er soll nur verhindern,
  dass ein Nutzer ohne Headset gar nichts mehr ausrichten kann. Wird gar
  nichts verstanden, greift der 100-%-Rückfall - die Ansage bleibt also
  hörbar, aber der Nutzer könnte die Lautstärke nicht mehr selbst ändern.

- [ ] **Referenzgerät steht seit 2026-08-16: AIRHUG 01** (Bluetooth-
  Headset, A2DP + HFP, in `docs/hardware.md` dokumentiert). Offen bleibt
  davon nur noch die ursprüngliche Teilfrage: ob es Deutsch als
  Ansage-Sprache unterstützt (eigene
  Firmware-Ansagen des Geräts wie "verbunden"/Akku-Warnung, nicht
  DialOS selbst) - Bluetooth-Standardprofile (A2DP/HFP) bieten dafür
  keine Fernsteuerung, rein geräte-/herstellerabhängig. Bei der Auswahl
  der Referenz-Hardware als Kriterium berücksichtigen.
- [x] **ERLEDIGT am 2026-08-16 - der komplette Ablauf ist auf echter
  Hardware durchgelaufen.** Ergebnis: Aus einem frisch installierten
  Debian 13 wurde ein laufendes DialOS. Bewiesen sind: verschlüsselter
  Swap (kommt beim Boot von allein hoch, per Journal belegt),
  `dialos-nutzer-home` mit 374,9 GiB, Autologin für `nutzer`,
  Sprachausgabe hörbar, deutsche Tastatur, und **beide Richtungen des
  Stick-Gates**: ohne Stick Anmeldebildschirm mit Passwortzwang und
  geschlossenem LUKS-Container, mit Stick sauberer Autologin samt
  Ansagen. Ebenfalls live bestätigt: die neue Lautstärke-Logik - Ansage,
  danach die Frage, gesprochene "25" erkannt und dauerhaft gemerkt.
  Dabei kamen acht Fehler ans Licht, die kein Trockenlauf gefunden hätte
  (Details im README-Änderungsprotokoll 0.5.0). Ursprünglicher Eintrag:
  T490 komplett neu aufsetzen und dabei den
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
  **Vorarbeit erledigt 2026-08-16:** Beide Skripte wurden vor dem ersten
  Lauf gegen `docs/Debian-zu-DialOS.md` durchgesehen, auf dem frisch
  installierten T490 live gegengeprüft und die gefundenen Fehler behoben
  (Details im README-Änderungsprotokoll 0.5.0). Der Ablauf besteht jetzt
  aus genau drei Befehlen; die Handarbeit aus Doku-Schritt 13 steckt in
  `dialos-buero-setup-abschliessen.sh`.
- [x] **Swap entschieden (Stephan, 2026-08-16): 8 GiB, verschlüsselt,
  automatisch in `dialos-setup-home-partition.sh`.** Ausgangslage: eine
  37,3-GiB-Klartext-Swap-Partition (`nvme0n1p3`), in die `nutzer`s
  Speicherseiten - offene Dokumente, Mails, Browserinhalte - ausgelagert
  werden konnten; ohne Sicherheits-Stick lesbar, ebenso nach Ausbau der
  SSD, also genau am Schutz von `dialos-nutzer-home` vorbei. Umgesetzt:
  Das Skript ersetzt einen vorgefundenen Klartext-Swap durch 8 GiB mit
  einem bei jedem Start neu gewürfelten Schlüssel (`/etc/crypttab`,
  `/dev/urandom`, Referenz per PARTUUID statt Dateisystem-UUID),
  setzt `vm.swappiness=10` und `RESUME=none`, und schlägt den
  freigewordenen Platz der Home-Partition zu (auf dem T490: 345,6 →
  rund 375 GiB). Begründung der Größe: die Regel "Swap ≥ RAM" existiert
  nur wegen des Ruhezustands, und der ist bei diesem Sicherheitsdesign
  ohnehin ausgeschlossen (das Abbild bräuchte einen dauerhaften Schlüssel
  im initramfs - der verworfene `cryptsetup-initramfs`-Ansatz). Ganz
  weglassen kam nicht in Frage: ohne Swap beendet der OOM-Killer bei
  Speichermangel Prozesse hart, und ein abgeschossener Screenreader
  bedeutet für einen blinden Nutzer den völligen Verlust der Rückmeldung.
  Suspend-to-RAM bleibt unberührt. **Noch nicht real gelaufen** - passiert
  beim ersten Durchlauf mit auf dem echten Gerät.
- [x] **Erledigt (2026-08-16): `dialos-install` ist ersatzlos entfallen**
  (Weg A - jedes Gerät entsteht im Büro aus der Debian-ISO plus den drei
  Skripten, es gibt keinen Live-Boot-Installer mehr). Damit erledigen
  sich auch dessen Fehler. **`dialos-rekey` bleibt** und hat sie noch -
  dort nachziehen, wenn es das nächste Mal angefasst wird: gleicher
  `$HOME`-Startordner im Backup-Dialog (Zeile 142) und fehlende Fallbacks
  in `ask_password`. Ursprünglicher Eintrag: **`dialos-install` und
  `dialos-rekey` hatten dieselben Fehler wie
  das durchgesehene `dialos-setup-home-partition.sh`** - bewusst nicht
  mitkorrigiert, weil über den Klon-Pfad noch nicht entschieden ist (Punkt
  weiter unten). Betroffen: gleiches zu langes ext4-Label
  `dialos-nutzer-home` (`dialos-install` Zeile 248), gleiche
  Klartext-Passphrase unter festem Namen `/tmp/.rp` (Zeile 199), gleicher
  `$HOME`-Startordner im Backup-Dialog (Zeile 231, `dialos-rekey` Zeile
  142), gleiche fehlende Fallbacks in `ask_password`/`zenity --list`.
  Entweder mitziehen oder zusammen mit dem Klon-Pfad entfallen lassen -
  aber nicht auseinanderlaufen lassen.
- [x] **Zeitzone/Locale entschieden (Stephan, 2026-08-16): bleibt
  `Europe/Vienna` + `de_AT.UTF-8`.** Nicht `Europe/Berlin`, wie die Doku
  bis dahin vorschrieb. Folge, jetzt in Debian-zu-DialOS.md Schritt 1
  dokumentiert: Baugerät und jede daraus gezogene ISO tragen die
  österreichischen Einstellungen (`eggs produce --clone` klont
  `/etc/localtime` + Locale mit). Am selben Tag durch die Entscheidung
  für Weg A weiter vereinfacht: Jedes Gerät wird im Büro über den
  Debian-Installer aufgesetzt, die Zeitzone wird also pro Gerät in
  Schritt 1 gewählt.
- [ ] **Zurückgestellt (Stephan, 2026-08-16):** **`dialos-claude-setup.sh`
  auf dem frisch installierten T490
  ausführen.** Geprüft am 2026-08-16: `credential.helper` ist nicht
  gesetzt, `~/.git-credentials` fehlt, `/etc/sudoers.d/` enthält nur die
  README, und `~/DialOS` zeigt nicht auf das Repo der externen Platte.
  Das Skript lief auf diesem System also noch nie - `git push` würde
  nach Zugangsdaten fragen und die `eggs produce`-NOPASSWD-Regel fehlt.
  Muss Stephan selbst machen (das GitHub-Token tippt kein Skript ein).
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
- [x] **Hinfällig seit 2026-08-16:** `dialos-install` ist ersatzlos
  entfallen (Weg A). Die Prüfpunkte dieses Eintrags wurden stattdessen
  über den neuen Ablauf abgedeckt und sind alle bestanden - siehe den
  erledigten Eintrag oben. Ursprünglich: komplette
  `dialos-install`-Installation
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
- [x] **Erledigt durch Wegfall (2026-08-16):** Calamares-Standort-Seite
  schlug beim Live-Boot GeoIP-basiert oft
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
- [x] **Erledigt am 2026-08-16: acht alte ISOs gelöscht (~59 GB).** Alle
  stammten aus der entfallenen Penguins-Eggs-Zeit. `DialOS-Live-0.5.1-
  clone.iso` bleibt bewusst liegen, bis Stephans erstes
  Rescuezilla-Abbild da ist - sie existiert nirgendwo sonst und ließe
  sich nicht neu erzeugen. Dokumentiert in `docs/iso-builds.md`.
  Ursprünglich: **Prämisse überholt, neu zu entscheiden (geprüft 2026-08-16):**
  `DialOS-Live-0.5.1-clone.iso` liegt **nicht** mehr lokal - der Reinstall
  hat sie mitgenommen. Sie existiert weiterhin auf der externen Platte
  unter `DialOS-ISOs/`, zusammen mit vier älteren Abbildern; zusammen
  **28 GB**.

  Die eigentliche Frage ist jetzt eine andere: Alle fünf stammen aus der
  Penguins-Eggs-Zeit, die am 2026-08-16 entfallen ist, und bilden einen
  Systemstand ab, den der heutige Neuaufbau deutlich überholt hat. Lohnt
  sich dafür noch ein Nextcloud-Upload, oder werden sie gelöscht und
  `docs/iso-builds.md` behält sie nur als Verzeichnis?

  Das kann nur Stephan entscheiden - es ist seine Sicherungsstrategie.
  Ursprünglicher Eintrag: liegt bisher nur lokal, noch in die Nextcloud
  hochladen (kein Claude-Zugriff darauf).
- [ ] Bluetooth-Audio-Fix in `dialos-start-ansage.py`
  (Ein-Instanz-Lock/`alte_instanz_beenden()`) ist noch nicht über einen
  längeren Zeitraum endgültig bestätigt - `/tmp/dialos-bluetooth-debug.log`
  bei einem erneuten Auftreten des Problems prüfen.
- [x] **Erledigt durch den Neuaufbau (geprüft 2026-08-16):** `~/DialOS-repo`
  existiert nicht mehr - der Reinstall des T490 hat die Zweitkopie
  beseitigt. Damit ist die Gefahr weg, die den Eintrag ausgelöst hatte.
  Der Symlink `~/DialOS` zeigt jetzt auf das Repo der externen Platte,
  es gibt also nur noch eine Kopie. Ursprünglich: Veraltete lokale
  Repo-Zweitkopie unter `~/DialOS-repo` löschen oder
  bewusst als Backup behalten (Entscheidung noch offen) - der Symlink
  `~/DialOS` ist jetzt tatsächlich korrekt gesetzt (siehe "Erledigt"
  unten), aber die Zweitkopie selbst liegt noch da. Zwei unabhängige
  Kopien nebeneinander sind fehleranfällig - genau dadurch sind zwei nie
  gepushte Commits vom 13.08. am 14.08. fast verloren gegangen.
- [x] **Gegenstandslos seit 2026-08-16:** `/home/eggs/*.iso`-Restdateien aufräumen -
  Penguins' Eggs ist entfallen (Schritt 16, jetzt Rescuezilla), und auf dem
  neu aufgebauten T490 war es ohnehin nie installiert. Ursprünglich:
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
