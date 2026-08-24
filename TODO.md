[Deutsch](TODO.md) | [English](TODO.en.md) | [Änderungsprotokoll](README.md#änderungsprotokoll)

# TODO

Laufende Liste offener Kleinigkeiten und nächster Schritte, die Stephan
oder Claude im Arbeitsalltag auffallen. Anders als
[Offene Punkte](docs/offene-punkte.md) (grundsätzliche, noch nicht
entschiedene Architekturfragen) sind das hier konkrete, abhakbare
Aufgaben. Oben steht, was noch offen ist. Erledigtes wird nicht gelöscht,
sondern nach unten unter „Erledigt (zur Nachvollziehbarkeit)" verschoben -
dort nach Thema gruppiert und innerhalb des Themas chronologisch, jeweils
mit dem Datum, an dem es fertig wurde.

**Warum oben trotzdem Häkchen stehen:** Manche erledigten Punkte gehören
zu einem noch offenen - der offene verweist auf sie („siehe oben",
„Restrisiko dazu"). Die bleiben oben stehen, bis auch der offene Punkt
fertig ist, und wandern dann gemeinsam nach unten. So zerreißt kein Bezug.

- [ ] **Keine Selbstprüfung, ob das Gerät überhaupt noch spricht** (offen seit
  2026-08-24, aufgefallen am stummen `paplay`). Am 2026-08-24 war jeder
  `paplay`-Strom stummgeschaltet, weil PipeWire sich das je Anwendung merkt.
  Folge: alle **zwischengespeicherten** Ansagen lautlos, dazu Frageton und
  Testton. `paplay` gibt dabei 0 zurück, `aus_speicher()` hält die Ansage für
  geglückt und fällt nicht auf `spd-say` zurück.

  **Für einen blinden Nutzer ist das der schlimmste Fall überhaupt:** Das
  Gerät ist stumm, es steht nirgends ein Fehler, und er kann nicht nachsehen.
  Die Ursache ist behoben (siehe Änderungsprotokoll), aber die **Klasse** des
  Fehlers nicht: Es gibt keine Stelle, die merkt „ich habe gesprochen, aber es
  war nichts zu hören".

  **Was zu klären ist, bevor etwas gebaut wird:** Woran lässt sich das
  überhaupt messen? Kandidaten: den eigenen Strom nach dem Anlegen auf `Mute`
  prüfen (billig, fängt genau diesen Fall), oder den Pegel der Senke während
  der Ansage lesen (fängt mehr, ist aber aufwendiger und bei Kopfhörern
  zweifelhaft). Nicht raten - erst prüfen, was PipeWire wirklich hergibt.

  **Und wie sagt man es?** Eine Ansage kann es nicht sein - die wäre ja
  ebenfalls stumm. Bleibt: Protokoll, Mitschrift-Fenster, und beim nächsten
  Anmelden ein sichtbarer Hinweis für den Helfer.

- [ ] **Erster Fehlstart der Sprachsteuerung - Ursache offen** (2026-08-24).
  Um 14:41:12 hat sich die Sprachsteuerung selbst eingeschaltet: Vosk erkannte
  „sprachsteuerung starten", das Mitschrift-Fenster ging auf, danach kamen
  „datum vorlesen drucken" und „welchen". **Stephan hatte an diesem Tag kein
  Wort zur Sprachsteuerung gesagt.**

  **Was ausgeschlossen ist:** die eigene Ansage. Im Ton-Protokoll steht
  zwischen 14:35 und 14:42 keine einzige Zeile, DialOS hat also nicht selbst
  gesprochen. Die Echo-Unterdrückung war damit gar nicht gefordert.

  **Was offen ist:** was das Mikrofon gehört hat. Umgebungssprache (Gespräch
  im Raum, Radio, Video) ist die naheliegende Vermutung - aber eine Vermutung,
  und dieses Projekt hat schon zweimal an einer schlüssigen Vermutung
  vorbeigemessen. Zu klären ist zuerst mit Stephan, ob um 14:41 jemand oder
  etwas im Raum gesprochen hat.

  **Warum es zählt:** Die Zwei-Wort-Regel ist genau dafür gebaut, dass ein
  beiläufiges Wort nichts auslöst. Wenn Umgebungssprache sie überwindet, ist
  ein selbsttätiges Einschalten samt Fenster und ausgeführten Befehlen
  möglich, ohne dass jemand mit dem Gerät spricht. Beim blinden Nutzer wäre
  das Fenster unsichtbar - er merkt nur, dass das Gerät plötzlich zuhört.

- [ ] **Erlaubte Wortkombinationen ohne Befehl fallen LAUTLOS durch** (offen
  seit 2026-08-22, gefunden beim Drucktest). Der schwerwiegendste offene Punkt
  für die Zielgruppe.

  **Was passiert.** Die eingeschränkte Grammatik ist eine Liste von SÄTZEN,
  aber Vosk baut daraus ein WORTNETZ und darf Wörter aus verschiedenen Sätzen
  kombinieren. Kommt dabei etwas heraus, das kein Befehl ist, passiert nichts -
  und es wird auch nichts gesagt. Stephan sagte „notiz drucken", die Grammatik
  kannte nur „notizen drucken", nichts geschah, keine Ansage.

  **Warum das schlimmer ist als ein Fehler.** Ein sehender Nutzer sieht ein
  Fenster, das sich nicht öffnet, oder ein Blatt, das nicht kommt. Ein blinder
  Nutzer hat gesprochen, das Gerät hat zugehört, und nichts sagt ihm, dass
  nichts geschah. Er weiß nicht einmal, ob er falsch gesprochen hat oder ob das
  Gerät kaputt ist. Eine Fehlermeldung wäre besser gewesen.

  **Gemessen am 2026-08-22** aus allen `~/.log/dialos-sprachbefehl.log*`,
  Zustände getrennt gezählt:

  | | Anzahl |
  |---|---|
  | Gültige Befehle | 98 |
  | `[unk]` (Geräusch) | 191 |
  | AUS-Zustand, kein Treffer | 345 |
  | **AN-Zustand, kein Treffer** | **382** |

  Die 345 im AUS-Zustand sind fast alle Bruchstücke von „sprachsteuerung
  starten". **Dort ist Schweigen richtig und muss so bleiben** - das ist die
  Zwei-Wort-Regel, die 60 Beinahe-Treffer und lange null Fehlstarts gebracht
  hat - der erste kam am 2026-08-24 (siehe eigener Punkt oben). Nur
  die 382 im EINGESCHALTETEN Zustand sind der Fehler.

  **Und da liegt das Dilemma:** 382 Ansagen wären unerträglich. Das Gerät würde
  bei jedem Nebengespräch dazwischenreden. Die Frage ist also nicht, OB etwas
  gesagt wird, sondern WANN - und dafür fehlt ein Kriterium, das gemessen und
  nicht geraten ist.

  **Was schon dagegen spricht, es einfach zu bauen:** Von den 382 sind 159
  Einwort-Bruchstücke („wir", „es", „auf", „viel"). Bleiben 223 mehrwortige
  ohne `[unk]` - immer noch zu viele. Darunter „haben wir" (15x), „die
  uhrzeit", „welchen haben wir": Das sind Gesprächsfetzen, keine
  Befehlsversuche.

  **Nächster Schritt, in dieser Reihenfolge:**
  1. Eine Stichprobe der 223 mit Stephan durchgehen. Nur er kann sagen, welche
     davon ein Befehlsversuch waren - das Protokoll kann es nicht.
  2. Erst danach ein Kriterium festlegen. Der Pegelmesser aus dem Diktat
     (`PEGEL_SCHWELLE`, Sprache 3475-4196 gegen Rauschen 47-84) ist ein
     Kandidat, aber er unterscheidet Sprechen von Stille, nicht Absicht von
     Beiläufigkeit.
  3. Die Ansage selbst muss knapp sein und darf nicht belehren. „Das war kein
     Befehl" ist besser als ein Satz, der die ganze Liste vorliest.

- [ ] **ZURUECKGESTELLT: dialos-hilfe.py auf den Dienst umbauen** (Stephan,
  2026-08-20: "können den Rustdesk ganz nach hinten schieben, wenn alles
  andere läuft"). Die zwei Sprachbefehle sind deshalb aus der Grammatik
  GENOMMEN und nicht nur unfertig gelassen: Der Befehl startete die
  RustDesk-Anwendung, die ohne den Dienst nach 40 s abstuerzt - ein
  Sprachbefehl, der halb funktioniert, ist schlimmer als einer, der nicht
  existiert. Wieder freigeben: zwei Zeilen in GRAMMATIK_AN und zwei in
  HILFE_SAETZE einkommentieren.
  (2026-08-19 fertig vorbereitet, nicht mehr eingebaut.) Der Weg ist belegt
  und die privilegierte Seite ist geschrieben und geprueft, es fehlt die
  Nutzerseite.

  **Was gestern herauskam:** Die RustDesk-ANWENDUNG kann keine Verbindung
  annehmen - ohne `ipc_service` stuerzt sie nach rund 40 s ab ("Got signal 11
  and exit", im Protokoll belegt). Verbindungen nimmt der **Dienst** an, und ihm
  gehoert auch das Passwort. Die entscheidende Kombination ist "Dienst laeuft UND
  sudo": `sudo rustdesk --password` wirkt dann, vier andere Kombinationen waren
  wirkungslos.

  **Schon gebaut, geprueft, NICHT installiert:**
  - `usr/local/sbin/dialos-fernwartung` (root): `starten` schaltet den Dienst
    an, setzt ein frisches achtstelliges Zufallspasswort, prueft per Gegenprobe
    im Konfigurationsfeld, dass es wirklich gesetzt ist (der Aufruf gibt auch
    bei Wirkungslosigkeit 0 zurueck), und gibt `id=` und `pw=` aus. `beenden`
    wechselt das Passwort - erst dadurch ist das vorgelesene wirklich ein
    Einmalpasswort - und stoppt den Dienst.
  - `etc/sudoers.d/dialos-fernwartung`: beide Aufrufe woertlich, ohne
    Platzhalter, `visudo -c` sagt "Analyse OK". Muss mit 0440 root:root
    installiert werden.

  **Was noch zu tun ist, in dieser Reihenfolge:**
  1. Beide Dateien von Stephan durchsehen lassen - eine sudoers-Regel ist eine
     Sicherheitsentscheidung und gehoert nicht ohne Blick installiert.
  2. `dialos-hilfe.py`: `rustdesk_pids()` durch `systemctl is-active rustdesk`
     ersetzen. Die Anwendung wird gar nicht mehr gestartet, damit faellt der
     Absturz weg.
  3. `starten()`: `sudo /usr/local/sbin/dialos-fernwartung starten` aufrufen,
     `id=`/`pw=` einlesen, an `nummern_sprechen()` uebergeben. `einmalpasswort()`
     entfaellt dann als Platzhalter.
  4. `beenden()`: `sudo ... beenden` statt SIGTERM auf Prozesse.
  5. Die Wache prueft dann den Dienst statt der Prozesse.
  6. Danach: echter Verbindungsversuch von Stephans zweitem Rechner - das ist
     zugleich der Beleg fuer die Signatur, die fuer die Leerlauf-Erkennung
     fehlt (eigener Punkt unten).

  **Loses Ende:** In `/root/.config/rustdesk/RustDesk.toml` steht seit Stephans
  Test vom 2026-08-19 ein achtstelliges Zufallspasswort, das niemand kennt. Das
  ist harmlos - der Dienst ist gestoppt und `disabled` -, und der erste Lauf von
  `dialos-fernwartung starten` ueberschreibt es.

- [ ] **Echtes Einmalpasswort fuer die Fernwartung, sobald RustDesk es zulaesst**
  (offen seit 2026-08-19). Fuenf Wege geprueft, alle zu - die Liste steht in
  `docs/sicherheit-datenschutz.md`, damit niemand sie noch einmal durchprobiert:
  Einmalpasswort steht in keiner Datei; `rustdesk --password` wirkungslos als
  Nutzer, mit laufender Anwendung, mit laufendem Dienst und als root;
  `--get-temp-password` kommt auch nach 40 s nicht zurueck; `rustdesk-utils`
  fehlt im Paket; den verschluesselten Wert selbst zu schreiben waere geraten.
  Zu beobachten ist
  [rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074). Bis dahin
  garantiert die LAUFZEIT die Begrenzung, nicht das Passwort.

- [ ] **Leerlauf-Erkennung fuer die Fernwartung** (offen seit 2026-08-19). Die
  Zeitgrenze ist absolut (eine Stunde), obwohl Leerlauf die richtige Semantik
  waere: Das Risiko ist eine offene Fernwartung, an der NIEMAND haengt. Eine
  aktive Sitzung abzuschneiden waere schaedlich, etwa mitten in einem Update.
  Warum es noch nicht gebaut ist: Auf dem Geraet hat sich nie jemand verbunden,
  die Signatur einer aktiven Verbindung ist unbekannt, und sie zu raten waere der
  schlechtere Fehler. `dialos-hilfe.py` notiert deshalb bei jeder Sitzung
  Prozessanzahl und Groesse von RustDesks Protokoll (`spur_notieren`).
  **Naechster Schritt: KEIN eigener Test noetig** (Stephan, 2026-08-20:
  "da ich an anderer Stelle Rustdesk taeglich benutze, brauchen wir da
  nicht wirklich einen Test machen"). Richtig - was fehlt, ist nicht der
  Nachweis, DASS RustDesk funktioniert, sondern die Signatur einer aktiven
  Verbindung AUF DIESEM Geraet. Die faellt beim naechsten normalen
  Support-Einsatz von selbst an: spur_notieren() schreibt bei jeder
  Sitzung Prozessanzahl und Protokollgroesse mit. Danach steht sie im
  Protokoll und die Erkennung laesst sich belegt bauen.

- [ ] **Eintraege trennen, wenn der Nutzer ohne „und" in einem Zug spricht**
  (offen seit 2026-08-19). „Milch sechs Eier Butter" in einem Atemzug bleibt ein
  Eintrag: Vosk liefert eine Aeusserung, eine Aeusserung ist ein Eintrag.
  Behandelt sind bisher die zwei einfachen Wege - eine kleine Pause (wird jetzt
  angesagt) und das Wort „und" (wird getrennt). Der zuverlaessige Weg waeren die
  **Wort-Zeitstempel**, die Vosk mit `SetWords(True)` mitliefert: eine Luecke von
  mehr als etwa 0,4 s zwischen zwei Woertern ist eine Trennstelle, auch wenn sie
  zu kurz ist, um die Aeusserung zu beenden. Zu messen ist der Schwellwert -
  0,4 s ist geraten, nicht gemessen, und zu klein gewaehlt zerlegt er „sechs
  Eier" in zwei Eintraege. Gilt nur fuer `LISTEN_ZIELE`, nicht fuer Briefe.

- [ ] **Zeitzone folgt dem Standort nicht - und ein blinder Nutzer kann sie
  nicht umstellen** (aufgefallen 2026-08-19 bei Stephans Frage „richtet sich
  die Uhrzeit nach dem tatsächlichen Ort?"). Gemessen: `Time zone:
  Europe/Vienna`, `automatic-timezone: false`. Die Zeitzone wird pro Gerät
  beim Aufsetzen gewählt (Bauanleitung Schritt 1). In Berlin oder München
  stimmt die Ansage trotzdem, weil dieselbe Zone gilt - eine Reise in eine
  andere Zeitzone ergibt eine falsche Uhrzeit.
  - **Wenn automatisch, dann mit Ansage.** Eine stille Umstellung würde für
    einen blinden Nutzer alle Zeiten unerklärlich verschieben, Termine
    eingeschlossen. Die Ansage ist der Teil, der es überhaupt zumutbar
    macht - nicht die Umstellung selbst.
  - **Für die Zeitzone reicht die ungenaue Ortung.** Die 26 km, die fürs
    Wetter unbrauchbar sind, sind hier belanglos: Eine Zeitzone braucht
    Landes-Genauigkeit. Nahe der Grenze könnte es Europe/Berlin statt
    Europe/Vienna werden - beide haben denselben Versatz, die gesprochene
    Zeit wäre identisch.

- [ ] **Wetter auf Nachfrage bräuchte einen Rückfall-Ort** (entfernt am
  2026-08-19, Begründung im Kopf von `dialos-auskunft.py`). Der Befehl kann
  am Einsatzort nicht funktionieren, weil beaconDB die WLAN-Netze dort nicht
  kennt und nur eine IP-Schätzung liefert (Wien, 26 km). Zurückholen ließe
  er sich mit einem hinterlegten Ort, der **nur** einspringt, wenn die
  Messung zu ungenau ist - in erfassten Städten gewinnt weiterhin die echte
  Messung. Stephans Einwand dazu war berechtigt und ist beantwortet: Berlin
  bliebe Berlin. Der Fall, der schiefgeht, ist Urlaub auf dem Land - dann
  wäre die Ansage veraltet, aber **hörbar** veraltet, weil sie die Stadt
  nennt.

- [ ] **Anna im Alltag beurteilen** (offen seit 2026-08-20, Stephan: "das werde
  ich aber erst mit der Zeit mitbekommen"). Zwei Dinge sind gemessen, aber nicht
  im Alltag erprobt:
  - **Tempo 0,95** - entschieden am 2026-08-22 nach Gehoer, so wie Thorstens
    0,88 seinerzeit. Stephan hat 1,00, 0,90, 0,80 und 0,95 nacheinander gehoert
    ("0,95 ist super bei Anna! Die ist beschlossen!"). Das war ein Urteil an
    wenigen Saetzen; ob es ueber einen langen Text traegt, zeigt erst der
    Alltag. Umstellen geht in einer Zeile: STIMMEN["kerstin"]["tempo"] in
    dialos-stimme.py, danach `setzen kerstin` erneut.
  - **Die drei Aussprache-Regeln** ("Tas tatur", "Ei Di", "Dial OS") sind auf
    Thorsten abgestimmt und gelten derzeit fuer alle Stimmen. Vorgespielt wurde
    jede mit und ohne; Stephans Urteil steht aus. Braucht Anna eine davon nicht,
    klingt sie damit falsch getrennt - dann muessen die Regeln pro Stimme
    gelten, und das aendert die Struktur der Tabelle in dialos-say.py. Die drei
    Woerter kommen selten vor, deshalb ist Warten hier vertretbar.

- [ ] **Aussprache von „DialOS" entscheiden** (offen seit 2026-08-22, Stephans
  Wunsch: "bisher wird das System immer so gesprochen DIAL OS könen wir das
  auch noch anpassen das es melodischer klingt dia los"). Betrifft NUR die
  Sprachausgabe - "Das Wort selbst bleibt DialOS", geschrieben ändert sich
  nichts. Drei Varianten wurden vorgespielt, Stephans Entscheidung steht aus.
  Geändert würde die erste Regel in AUSSPRACHE in `dialos-say.py`, dort steht
  derzeit "Dial OS". Solange nichts entschieden ist, bleibt es dabei - und
  genau deshalb steht der Punkt hier: Er existierte bisher nur im Gespräch.

- [ ] **Zweite Stimme früh dazulegen, Auswahl erst zum Schluss**
  (Stephans Frage, 2026-08-18: „Wann wollen wir die anderen Stimmen z.B.
  einer Frau hinzunehmen?"). Aufgeteilt, weil beides verschiedene Dinge sind:
  - [ ] **Früh (rund eine Stunde):** EINE weibliche Stimme installieren
    (`de_DE-eva_k-x_low`, `kerstin-low` oder `ramona-low` - die
    Konfiguration kennt sie schon, installiert ist nur `thorsten-high`) und
    genau drei Dinge prüfen, die den Aufbau ändern könnten:
    - [x] **`stimmen[0]` in `dialos-say.py`** - erledigt 2026-08-20,
      und zwar VOR der zweiten Stimme statt danach: Der Ansagen-Speicher nahm
      die erste Datei im Ordner. Liest jetzt `DefaultVoice` aus
      `piper-generic.conf` und speichert lieber gar nichts, als bei mehreren
      Stimmen zu raten. Fünf Fälle gegengeprüft.
    - **Tempo pro Stimme?** 0,88 ist für Thorsten im Hörvergleich gewählt.
      Passt es für eine Frauenstimme nicht, muss das Tempo pro Stimme
      einstellbar werden - das ändert die Struktur von
      `piper-generic.conf`.
    - **Aussprache-Regeln prüfen:** „Tas tatur" statt „Tastatur" ist auf
      Thorsten abgestimmt. Eine andere Stimme braucht die Trennung
      vielleicht nicht.
    - **Nebenbefund:** In `piper-generic.conf` sind alle zehn deutschen
      Stimmen als `MALE1` eingetragen, auch die weiblichen. Eine Auswahl
      über den Stimmtyp funktioniert dadurch nicht.
  - [ ] **Zum Schluss:** die Auswahl für den Nutzer - per Sprache ansagbar,
    über den Neustart hinweg gemerkt. Braucht eine Einstellungs-Mechanik,
    die es noch nicht gibt, und alle Ansagen im Endzustand.
  - **Die Begründung für diese Aufteilung ist Zeile 129 selbst:** Solche
    Annahmen sammeln sich an, solange es nur eine Stimme gibt. Sie alle am
    Ende gleichzeitig zu finden ist der teure Weg.

- [ ] **ZUERST MORGEN: Zwei Diktate haben nichts aufgenommen** (2026-08-18,
  letzter Lauf). Im Protokoll `~/.log/dialos-diktat.log` steht zwischen „grosses
  Modell geladen" und „Schlusssatz erkannt" **keine einzige** `erkannt:`-
  Zeile - beim zweiten Lauf über 26 Sekunden hinweg. Der Einkaufszettel
  blieb leer, „Einkaufszettel vorlesen" und „Einkauf erledigt" wurden
  deshalb nie ausgeführt (`~/.log/dialos-notiz.log` ist leer). **Absichtlich
  keine Vermutung notiert** - keine ist belegt. Was zu prüfen wäre: ob zwei
  gleichzeitige `parec` auf derselben Quelle sich behindern (der
  Befehlsdienst liest weiter, auch wenn er verwirft), ob der Schluss-Erkenner
  dem grossen die Blöcke wegnimmt, und ob überhaupt gesprochen wurde -
  vorher mit Stephan klären, was er gesagt hat.

- [ ] **Anwendungen: freigegebener Umfang vom 2026-08-18.** Vollständige
  Liste mit Begründung in `docs/anwendungen.md`. Gesetzt sind Firefox,
  Thunderbird (Mail/Kalender/Kontakte), RustDesk, Shortwave (Radio),
  Rhythmbox (Musik/Podcasts/Hörbücher), LibreOffice Writer (Briefe),
  Notizen als Textdateien, Jitsi im Firefox (Videochat),
  unattended-upgrades. Zu bauen, in dieser Reihenfolge sinnvoll:
  - [x] **Diktat (Sprache zu Text) - läuft seit 2026-08-18.**
    `dialos-diktat.py`, live mit Stephans Stimme belegt. Details in
    `docs/diktat.md`, Einbau in `docs/Debian-zu-DialOS.md` Schritt 11h.
    Was daran noch fehlt:
    - [ ] **Per Sprache startbar.** Bisher nur von der Kommandozeile. Der
      Befehl muss aus dem Befehlsdienst heraus das Diktat starten - und
      dabei die eigene Erkennung stilllegen, was über die Marke schon
      funktioniert.
    - [x] **Satzzeichen - gebaut am 2026-08-21.** Gesprochene Satzzeichen:
      Komma, Punkt, Fragezeichen, Ausrufezeichen, Doppelpunkt,
      Gedankenstrich, Absatz, neuer Absatz, neue Zeile. Alle neun stehen im
      Wortschatz des grossen Modells (`graph/words.txt`, 822 389 Einträge).
      Stephans Entscheidung: **immer** als Satzzeichen werten, nicht nur bei
      Sprechpause. Preis: „in diesem Punkt" wird zu „in diesem." - fällt
      beim Vorlesen auf. Ersetzt wird **wortweise**, damit „Punkte" und
      „Kommando" unangetastet bleiben. Listen bekommen keine Satzzeichen.
    - [x] **Sprechpause vor dem Schluss - gebaut und geprüft 2026-08-22.**
      In den letzten 5 s muss eine Ruhephase von mindestens 0,4 s gelegen
      haben. Offline gegen Piper geprüft, bevor Stephan testen musste
      (`scripts/dialos-schlussregel-pruefen.py`, benutzt den echten Code):
      
        - **A** durchgehende Rede: zwei **vollständige** „diktat beenden"
          entstanden, beide abgewiesen - die hätten die Zwei-Wort-Regel
          passiert.
        - **B** Rede, Pause, Schlusssatz: dieselben zwei abgewiesen, der echte
          angenommen.
      
      **Offen bleibt der Beweis am Gerät:** ein Diktat mit echter Stimme, das
      von Anfang bis Ende durchläuft. Und ein Bruchstück, das zufällig direkt
      nach einer Pause entsteht, käme weiterhin durch - klein, aber nicht null.
    - [ ] **Eine Zeile je Eintrag.** Vosk schneidet erst an einer
      Sprechpause; ohne Pause landet alles in einer Zeile. Für einen
      Einkaufszettel wäre eine Zeile je Eintrag besser.
    - [ ] **Briefe:** 98,1 % Schreibung reichen für Notizen und Mail. Für
      einen Brief an die Krankenkasse ist zu entscheiden, ob das genügt
      oder ob er vor dem Absenden geprüft werden muss.
    - [x] **Fußzeile im Brief - erledigt 2026-08-21.**
      `dialos-diktat.py` setzt den diktierten Text in einen Briefbogen aus
      reinem Text: Absender und Datum rechtsbündig, Text auf Breite 76
      umgebrochen, darunter der Hinweis auf die fehlende Unterschrift und
      unten rechts die Herkunftszeile. Den Satz holt es aus
      `dialos-fusszeile.py`, die Monatsnamen aus `dialos-start-ansage.py` -
      geholt, nicht abgeschrieben.
      
      Offen bleibt „**jeder Ausdruck**" aus Stephans ursprünglicher Vorgabe:
      siehe den Punkt „Drucken per Sprache" weiter unten. Eine Writer-Vorlage
      in `~/Vorlagen` braucht es dafür nicht mehr - der Briefbogen entsteht
      im Text selbst.
  - [x] **PDF-Archiv - Briefe und Mails erledigt 2026-08-22.**
    Jeder Brief landet beim Schreiben automatisch als PDF in
    `~/Dokumente/Archiv/DialOS-DATA/` und auf dem Stick. Eigener PDF-Erzeuger
    über `cairo`, weil der
    Briefbogen mit Leerzeichen gesetzt ist und in einer Proportionalschrift
    zerfiele; mit `pdftotext -layout` zurückgelesen und zeichengenau
    verglichen.
    
    **Mails ohne Passwort:** aus Thunderbirds lokalem mbox-Speicher, alle 15
    Minuten per Timer. Jede Mail nur einmal (Message-ID gemerkt). Der
    eigene IMAP-Weg bleibt trotzdem nötig - der lokale Speicher enthält nur,
    was Thunderbird geholt hat.
    
    **Und die Datenschutzfrage bleibt offen** (mit den Bildschirmfotos
    zusammen zu entscheiden): Verfallen die PDFs nach sieben Tagen wie die
    Protokolle? Siehe `docs/sicherheit-datenschutz.md`.
  - [ ] **Vorlesen** von Mails, Dokumenten und Webseiten.
  - [x] **Drucken per Sprache - gebaut 2026-08-22.**
    „Brief drucken", „Einkaufszettel drucken", „Notizen drucken". Alle 24
    Grammatiksätze geprüft.
    
    **Der Drucker wird gesucht, nicht vorausgesetzt.** CUPS hat auf diesem
    Gerät kein Standardziel; ein blosses `lp -` liefe ins Leere. Das Skript
    nimmt das Standardziel, sonst den einzigen Drucker, sonst den ersten -
    und schreibt ins Protokoll, welchen.
    
    **Die Fußzeile kommt nur dahin, wo sie fehlt:** Der Brief hat sie schon,
    Zettel und Notizen bekommen sie erst beim Drucken.
    
    **Auf Papier belegt am 2026-08-22** (Stephan: „Ausdruck ist jetzt
    hochkant"). Der erste Ausdruck kam quer heraus. Nachgemessen wurde,
    dass CUPS nicht schuld war - Filterweg und Drucker melden beide A4
    hochkant -, die Drehung entstand also im Gerät. Papier und
    Ausrichtung stehen jetzt im Auftrag (`-o media=A4 -o
    orientation-requested=3`) statt in irgendeiner Voreinstellung.
    
    Der Nachtest davor fiel **lautlos** durch: Vosk verstand „notiz
    drucken", die Grammatik kannte nur „notizen drucken". Kein Treffer
    heißt keine Ansage - für einen blinden Nutzer der schlechteste
    Ausgang, schlimmer als eine Fehlermeldung. Die Einzahl ist jetzt
    zweite Formulierung. Der allgemeine Fall bleibt offen: erlaubte
    Wortkombinationen, die keinen Befehl ergeben, fallen still durch.
  - [ ] **Radio und Musik per Sprache** - Shortwave nach Stationsname,
    Rhythmbox über `rhythmbox-client`. Dabei die Ein-Player-Regel
    umsetzen: das eine beenden, bevor das andere startet.
  - [ ] **Merkposition für Podcasts und Hörbücher** - Rhythmbox liefert
    sie nicht (geprüft: kein `playback-position`, kein `bookmark`). DialOS
    liest und setzt sie über MPRIS und muss sie ansagen können.
  - [ ] **Post einscannen und vorlesen** - `tesseract-ocr` (5.5.0)
    nachinstallieren, simple-scan/sane/CUPS sind da.
  - [ ] **Wecker, Timer, Erinnerungen.**
  - [ ] **Rechner ausschalten und sperren per Sprache**; **Termine und
    Wetter ansagen** (Thunderbird bzw. die vorhandene Wetterabfrage).
  - [ ] **Updates:** `unattended-upgrades` einrichten (Sicherheitsupdates
    automatisch) und getrennt davon den Sprachbefehl mit Ja/Nein-Rückfrage
    für alles Größere.
  - Noch offen, nicht bauen: **Telefonie** (nach hinten gestellt, hängt an
    der Hardware-Entscheidung), **Chat** (WhatsApp laut `telefonie.md`,
    Bestätigung fehlt), **Videoaufnahme** (Zweck ungeklärt).

- [ ] **Nächster Block: die Anwendungen** (Stephan, 2026-08-17). Bis
  hierher ging es um Grundlagen - Sprachausgabe, Erkennung, Audio-Wege,
  Desktop-Optik. Als Nächstes kommt dran, welche Programme DialOS
  mitbringt und wie sie per Sprache bedient werden. **Einstiegspunkt ist
  die Tabelle „Vorgesehen, noch nicht gebaut" in
  `docs/sprachbefehle.md`** (Radio/Musik, Hilfe rufen, Systemwartung,
  Telefonie) - keine neue Liste anlegen, sondern die bestehende abarbeiten
  und für jeden neuen Befehl die Regeln aus derselben Datei einhalten.

- [ ] **Unerklaert: Die Bluetooth-Senke stand ploetzlich auf 70 %**
  (2026-08-17). Zwischen zwei Messungen wechselte die Lautstaerke des
  AIRHUG von 100 % auf 70 %, ohne dass DialOS etwas getan hatte. Drei
  Erklaerungen sind widerlegt: Das Geraet meldet seine Lautstaerke nicht
  (geprueft bei Tastendruck ohne Ton, bei Wiedergabestart und bei
  Tastendruck **waehrend** laufender Wiedergabe - dreimal keine
  Aenderung), WirePlumbers gespeicherter Wert steht auf 100 %, und im
  Ereignisprotokoll gab es im passenden Zeitraum keinen Neuaufbau der
  Senke. **Absichtlich keine vierte Vermutung** - festgehalten, damit ein
  zweites Auftreten einen zweiten Datenpunkt liefert. Wichtig ist es,
  weil eine Lautstaerke, die sich von selbst aendert, fuer einen blinden
  Nutzer nicht nachvollziehbar ist.

- [ ] **Entscheidung offen: Ansagen leiser als Musik** (Stephans Wunsch
  vom 2026-08-17, "um ca. 30 % drosseln"). Am Laptop-Lautsprecher ist es
  machbar - Daempfung im Signal wirkt dort, von Stephan im Hoervergleich
  bestaetigt. Am AIRHUG **nicht**: Er rechnet die Daempfung wieder weg
  (Messung in `docs/Debian-zu-DialOS.md`, Schritt 11g), dort wirkt nur die
  Geraete-Lautstaerke, und die gilt fuer alles. Moeglich waere, sie per
  AVRCP **waehrend** der Ansage kurz abzusenken; ein solcher Befehl kostet
  gemessen nur 19-36 ms, faellt gegen 1200 ms Ansage also nicht auf.
  Offen ist, ob das Absenken am Geraet hoerbar stuft oder klickt - das
  entscheidet, ob es brauchbar ist. Nach Stephans Einstellung der
  Lautstaerke am Geraet ist die Frage vielleicht ohnehin erledigt.
  - **Dabei zu beheben:** `GenericVolume` ist in DialOS wirkungslos, weil
    die sox-Kette auf `norm` endet und jede Daempfung davor wegrechnet.
    Wer die Lautstaerke ueber speech-dispatcher regeln will, muss
    `norm vol <faktor>` schreiben.

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

- [ ] **Bluetooth-Profil gegen Hängenbleiben absichern** (offen seit
  2026-08-17). Nach dem Neustart stand der AIRHUG auf `headset-head-unit`
  statt `a2dp-sink` - die Wiedergabe lief dauerhaft in Telefonqualität,
  ohne dass es jemand bemerkt hätte, der das Gerät nicht kennt.
  `dialos-start-ansage.py` schaltet für die Lautstärke-Frage bewusst auf
  HFP und danach zurück; endet das Skript vorher (Abbruch, Abmelden,
  Zeitüberschreitung), bleibt das Profil hängen. Nötig ist ein Riegel,
  der unabhängig vom Skriptende greift - etwa eine Prüfung beim Anmelden
  oder ein `trap` auf das Skriptende.

- [ ] **Pausen zwischen den Sätzen der Ansage prüfen** (offen seit
  2026-08-17). Michael klang „hektisch", gewählt wurde dann aber ein
  schnelleres Tempo - das spricht dafür, dass die fehlenden Atempausen
  zwischen den Sätzen das eigentliche Problem sind, nicht die
  Geschwindigkeit. Piper hängt Sätze fast ohne Pause aneinander. Eine
  kurze Pause je Satzende, zentral in `dialos-say.py`, würde die Ansage
  ruhiger machen, ohne einzelne Wörter schleppen zu lassen. Vorher eine
  Hörprobe bauen: gleiches Tempo, nur mit Pausen.

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

- [x] **Referenz-Audiogerät entschieden (Stephan, 2026-08-17): zwei
  Geräte.** AIRHUG bleibt als Lautsprecher in A2DP, dazu ein
  Funkmikrofon mit **USB**-Empfänger für die Eingabe - bewusst kein
  zweites Bluetooth-Gerät, das brächte die HFP-Falle zurück. Anforderungen
  und Kandidaten in `docs/hardware.md`.

- [ ] **Preiswertes Bluetooth-Mikrofon zum Ausprobieren beschaffen**
  (Stephan, 2026-08-17 - der Test entscheidet über die Bauart). Bluetooth
  hat einen Vorteil, den USB nicht hat: **DialOS sieht den Akkustand**
  über BlueZ und kann warnen, bevor das Mikrofon leer ist. Dagegen steht
  ein Risiko, das sich nur am Gerät klären lässt: Ein dauerhaft offenes
  HFP belegt fortlaufend Funkzeit auf demselben Adapter, über den der
  AIRHUG spielt - A2DP kann dabei stottern.

  **Prüfplan:** koppeln, Radio über den AIRHUG laufen lassen, den
  Sprachdienst auf das Bluetooth-Mikrofon legen, und hinhören ob die
  Musik stottert. Zusätzlich: Reichweite durch die Wohnung, Akkustand
  erscheint in der Start-Ansage, Erkennungsqualität gegen das eingebaute
  Mikrofon, und ob die Echo-Unterdrückung noch reicht, wenn das Mikrofon
  **neben** dem Lautsprecher liegt statt weit weg.

  Fällt der Test schlecht aus, ist die Rückfallebene ein USB-Funkmikrofon
  (Kandidaten in `docs/hardware.md`) - dann aber ohne Akkuanzeige, und
  vor dem Kauf zu klären, ob der Sender dauerhaft am Netzteil laufen
  kann.

- [ ] **Erkennen, wenn das Mikrofon nichts mehr liefert** (2026-08-17,
  unabhängig von der Gerätewahl zu bauen). Der Sprachdienst misst ohnehin
  laufend den Pegel. Kommt über Minuten hinweg **gar nichts** an, obwohl
  die Quelle da ist, soll er es ansagen: „Ich höre nichts mehr vom
  Mikrofon." Das ersetzt keine Akkuanzeige, fängt aber genau den Ausfall
  ab, der den Nutzer sonst ratlos zurückließe - er redet sonst gegen ein
  totes Gerät, ohne es zu merken. Achtung beim Schwellwert: Stille im
  Raum ist normal, dauerhaft **exakt** null Pegel dagegen nicht.
  - **Am 2026-08-17 ist die Aufgabe größer geworden, als sie gedacht war
    - der Fall ist eingetreten und hat die komplette Tonausgabe
    mitgenommen.** Die Echo-Unterdrückung stand zum Testen auf dem
    USB-Headset; beim Neustart war dessen Funkverbindung nicht da. Der
    Dongle bietet trotzdem eine Soundkarte an, ALSA meldet sogar
    `state: RUNNING` - es kommen nur 0 Bytes. Weil das Modul diese
    Aufnahme als Taktgeber braucht, startete PipeWire den Graph nicht
    mehr, und **nichts** im System konnte Ton abspielen, auch nicht über
    die eingebauten Lautsprecher. Details in `docs/Debian-zu-DialOS.md`,
    Schritt 11f.
  - **Damit hängen zwei Dinge daran, nicht eines.** (1) Die Ansage, wenn
    das Mikrofon verstummt - wie oben. (2) Eine Absicherung, die die
    Echo-Unterdrückung fallen lässt, statt den Ton mitzunehmen. Solange
    das Ziel das eingebaute Mikrofon ist, kann der Fall nicht auftreten;
    sobald ein externes Funkmikrofon Standard werden soll - und das ist
    geplant -, ist (2) Voraussetzung dafür, nicht Zubehör.
  - **Zu prüfen dabei:** Ob PipeWire selbst einen Weg anbietet, eine
    stumme Quelle nicht zum Taktgeber zu machen, wäre der saubere Weg.
    Sonst muss ein Dienst das Ziel vor dem Laden prüfen (`parec` auf
    Bytes testen) und die Unterdrückung nur dann einhängen.
  - **Und der Befund, der die Aufgabe schwer macht: es gibt keinen
    verlässlichen Anzeiger.** Nach Abziehen und Wiedereinstecken des
    Dongles lieferte dasselbe Gerät 64000 Bytes statt 0. Stephan hat
    dabei ausdrücklich festgestellt, dass ihm das Headset **schon vor dem
    Neustecken** eine bestehende Verbindung gemeldet hatte, auch über den
    Dongle. Also: Headset meldet verbunden, Dongle bietet eine Soundkarte
    an, ALSA meldet `state: RUNNING` - und es kommen trotzdem 0 Bytes.
    Meine erste Deutung („die Funkverbindung stand nicht") war damit
    falsch. **Folge für die Absicherung:** Sie darf sich auf keine
    Zustandsmeldung stützen, weder auf die des Geräts noch auf die von
    ALSA. Nur die tatsächlich ankommenden Bytes zählen.

- [x] **So stand die Aufgabe vorher da (zur Herkunft):** Gemessen ist:
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

- [ ] **Deutsche Firmware-Ansagen des Lautsprechers prüfen** (offen seit
  2026-08-16, Stephans Anforderung a). Gemeint sind die Ansagen des
  Geräts selbst („verbunden", Akku-Warnung), nicht die von DialOS. Sie
  sind für einen blinden Nutzer die **einzige** Rückmeldung, die er vom
  Gerät unabhängig vom Laptop bekommt - eine unverstandene Akkuwarnung
  heißt, dass die Ausgabe unangekündigt ausfällt. Über die
  Bluetooth-Standardprofile lässt sich das nicht fernsteuern, es hängt
  rein am Gerät. Beim AIRHUG noch nicht geprüft.

  *(Die frühere Fassung dieses Punkts nannte den AIRHUG als alleiniges
  Referenzgerät. Das ist seit 2026-08-17 überholt: Es sind zwei Geräte,
  siehe oben und `docs/hardware.md`.)*

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

- [ ] **Zurückgestellt (Stephan, 2026-08-16):** **`dialos-claude-setup.sh`
  auf dem frisch installierten T490
  ausführen.** Geprüft am 2026-08-16: `credential.helper` ist nicht
  gesetzt, `~/.git-credentials` fehlt, `/etc/sudoers.d/` enthält nur die
  README, und `~/DialOS` zeigt nicht auf das Repo der externen Platte.
  Das Skript lief auf diesem System also noch nie - `git push` würde
  nach Zugangsdaten fragen und die `eggs produce`-NOPASSWD-Regel fehlt.
  Muss Stephan selbst machen (das GitHub-Token tippt kein Skript ein).

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

- [ ] Sprechgeschwindigkeit der Piper-Stimme sollte vom Nutzer individuell
  einstellbar sein (aktuell fest über `GenericRateMultiply` in der
  Piper-Config verdrahtet, `0.85` als Stephans persönliche Präferenz
  gewählt) - braucht eine echte Einstellmöglichkeit (z. B. GNOME-
  Barrierefreiheitseinstellungen oder eigener Sprachbefehl), nicht nur
  einen Config-Wert.

- [ ] Echten End-to-End-Test von `dialos-vosk-test.py` durchführen
  (tatsächlich reinsprechen, Erkennungsqualität beurteilen) - bisher nur
  Installation + Modell-Laden technisch verifiziert, noch kein echter
  Spracherkennungs-Test mit einer gesprochenen Aufnahme gelaufen.

- [ ] Bluetooth-Audio-Fix in `dialos-start-ansage.py`
  (Ein-Instanz-Lock/`alte_instanz_beenden()`) ist noch nicht über einen
  längeren Zeitraum endgültig bestätigt - `/tmp/dialos-bluetooth-debug.log`
  bei einem erneuten Auftreten des Problems prüfen.

## Erledigt (zur Nachvollziehbarkeit)

Nach Thema gruppiert, innerhalb des Themas chronologisch. Das Datum ist
der Tag, an dem der Punkt fertig wurde. Nichts hiervon wird gelöscht -
die Liste ist die Erinnerung des Projekts, nicht nur eine Erfolgsbilanz.

### Sprachsteuerung und Erkennung

- ☑️ **2026-08-14** — Vosk (0.3.45) + hassil (3.11.0) + deutsche Vosk-Modelle (groß/klein)
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

- ☑️ **2026-08-14** — `pip3 install --break-system-packages vosk==0.3.45 hassil==3.11.0`
  auf dem T490 ausgeführt und verifiziert (2026-08-14) - `import vosk`/
  `hassil` funktioniert, `vosk.Model()` lädt das kleine deutsche Modell
  erfolgreich.

- ☑️ **2026-08-16** — **Sprachbefehl live getestet und läuft (2026-08-16, von Stephan
  bestätigt).** Dabei kam heraus, dass das eingebaute Mikrofon um 60 dB
  übersteuert war - der Dienst konnte prinzipiell nichts erkennen.
  Behoben und dauerhaft abgesichert (`dialos-mikrofon-pegel.service`).

- ☑️ **2026-08-17** — **Schalter „Sprachsteuerung starten/stoppen" gebaut
  (2026-08-17).** Zwei Zustände mit eigener Grammatik, Ansage bei jedem
  Wechsel, Abschaltung nach zwei Minuten. Die offene Zustandsfrage ist
  damit beantwortet: Der Nutzer hört jeden Wechsel. Live-Test mit echter
  Stimme steht noch aus.

  **So stand die Aufgabe vorher da (zur Herkunft):** Bis zum „starten" hört DialOS nur auf
  diesen einen Satz, danach nimmt es Befehle an, bis „stoppen" kommt.
  Gemessen ist bereits, dass die Erkennung trägt und drei Störsätze ruhig
  bleiben - offen ist der Zustand selbst: Wo wird er gemerkt (Datei wie
  bei der Desktop-Optik?), was passiert beim Anmelden (an oder aus?), und
  **wie erfährt ein blinder Nutzer, in welchem Zustand er ist**? Ohne
  eine Antwort darauf ist der Schalter gefährlicher als kein Schalter:
  Wer nicht weiß, dass die Erkennung aus ist, hält das Gerät für kaputt.

### Sprachausgabe und Ansagen

- ☑️ **2026-08-14** — Lautstärke-Abfrage bei der Start-Ansage (nur `nutzer`, 100/75/50/
  25 Prozent/aus) umgesetzt - erledigt 2026-08-14, siehe
  docs/Debian-zu-DialOS.md Schritt 11. Erste echte Vosk-Nutzung im
  Betrieb, Erkennungslogik mit Piper-synthetisierten Testwörtern
  verifiziert (alle fünf Optionen korrekt erkannt).

- ☑️ **2026-08-16** — Echten Test der Lautstärke-Abfrage mit tatsächlich gesprochener
  Antwort durchgeführt (über das Bluetooth-Mikrofon, inkl.
  `headset-head-unit`-Profilwechsel) - erledigt 2026-08-16. Dabei einen
  echten Bug gefunden und behoben: Beim ersten Versuch fehlte ein
  klares Startsignal, wann genau das 4-Sekunden-Aufnahmefenster
  beginnt - Stephans gesprochene Antwort ("25") wurde verpasst, nur der
  100 %-Sicherheits-Fallback kam an. Fix: `dialos-start-ansage.py`
  sagt jetzt direkt vor der Aufnahme zusätzlich "Und jetzt bitte." -
  danach im zweiten Versuch korrekt erkannt (echtes "25" → 25 %).

- ☑️ **2026-08-17** — **Ansagen unterscheiden: Frage oder Hinweis - gebaut am
  2026-08-17.** `dialos-say.py --frage`, Standard ist die natürliche
  Satzmelodie aus dem Fragezeichen, der Signalton ist Option über
  `~/.config/dialos/frageton`. Siehe `docs/Debian-zu-DialOS.md`,
  Schritt 11a. Offen bleibt nur, das später per Sprachbefehl umschaltbar
  zu machen („Signalton einschalten") - das braucht erst den Schalter
  „Sprachsteuerung starten/stoppen".

  **Ursprüngliche Beschreibung (Stephans Frage vom 2026-08-17).** Heute weiß das System es implizit - der Code entscheidet
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

- ☑️ **2026-08-19** — **Lock-Datei von `dialos-start-ansage.py` aus `/tmp` holen** - erledigt 2026-08-19, nachdem der Fall live eingetreten war: Zwei Start-Ansagen liefen gleichzeitig, weil `nutzer` die geteilte Datei besaß und `dialosadmin` sie nicht überschreiben konnte. Liegt jetzt in `$XDG_RUNTIME_DIR`.
  **So stand die Aufgabe vorher da (zur Herkunft):**
  `/tmp/dialos-start-ansage.pid` ist ein fester Pfad im geteilten `/tmp` -
  dieselbe Bauart, die am 2026-08-16 bei der Sprechen-Markierung zu einem
  stillen Fehlschlag geführt hat (Sticky-Bit: ein Konto kann die Datei
  eines anderen weder überschreiben noch löschen). Die Markierung liegt
  jetzt unter `$XDG_RUNTIME_DIR`, diese Datei noch nicht.

### Audio: Mikrofon und Lautsprecher

- ☑️ **2026-08-17** — **Ursache der Mikrofon-Übersteuerung geklärt (2026-08-17).** Der
  systemweite Dienst läuft beim Booten, WirePlumber stellt seinen Zustand
  erst in der Sitzung wieder her und hebt den Boost dabei zurück - der
  Dienst war strukturell zu früh dran. Der Sprachdienst richtet den Pegel
  jetzt selbst, nachdem er die Aufnahme geöffnet hat, und regelt bei
  anhaltender Übersteuerung nach. Getestet durch absichtliches
  Hochdrehen.

- ☑️ **2026-08-17** — **Fehlauslösung durch abgespielte Inhalte behoben (2026-08-17).**
  Echo-Unterdrückung über PipeWires `module-echo-cancel` eingerichtet,
  32 dB Dämpfung gemessen, und der Fall, der vorher scheiterte (Ansage
  per `paplay` abgespielt), löst nichts mehr aus. Details im
  Änderungsprotokoll und in `docs/Debian-zu-DialOS.md`, Schritt 11f.

### Diktat, Auskunft und Alltagsdienste

- ☑️ **2026-08-14** — Wetter-Standort auf GeoClue2 umgestellt statt IP-geraten - erledigt
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

- ☑️ **2026-08-19** — **Gross-/Kleinschreibung im Diktat gemessen statt vermutet** - erledigt
  2026-08-19. **10 von 11** Faellen richtig, gemessen mit `schreibung_richten()`
  selbst. Der einzige Fehlschlag ist eine Wortliste ohne Grammatik
  ("milch sechs eier butter") - dort fehlt LanguageTool der Satz, um Substantive
  zu erkennen. Einzeln geht jedes Wort richtig, und einzeln kommen sie seit
  demselben Tag. Bei Briefen und Mails, also ganzen Saetzen, ist die Schreibung
  belastbar. Die fruehere Einschaetzung "dringendster offener Punkt" ist damit
  zurueckgenommen.

- ☑️ **2026-08-19** — **Die erste Korrektur jeder Sitzung war ein Muenzwurf** - erledigt
  2026-08-19. LanguageTools deutsche Regeln laden bei der ersten
  **Pruefanfrage**, nicht beim Serverstart: 9,2 s gegen eine Zeitgrenze von
  10,0 s. Am 2026-08-19 um 10:03:03 hat sie verloren. Behoben durch
  `dialos-schreibhilfe-warmlaufen.py` als `ExecStartPost` der Unit - belegt im
  Journal: 9096 ms beim Start, danach 985 ms fuer die erste echte Korrektur.
  Nebenbefund: `lt_lebt()` prueft `/v2/languages` und meldet damit "laeuft",
  waehrend der Dienst neun Sekunden braucht - eine Bereitschaftsmeldung, die
  etwas anderes prueft als das, worauf es ankommt.

### Desktop und Bedienoberfläche

- ☑️ **2026-08-10** — Live-Desktop-Icon für die Installation (`.desktop`-Datei mit
  eigenem DialOS-Icon statt "Install System"/Ei-Icon auf dem
  Live-Boot-Desktop) - erledigt 2026-08-10 (Branding via
  skel-Überschreibung).

- ☑️ **2026-08-14** — AppIndicator-Pakete für `dialos-tts-indicator.py`
  (`gnome-shell-extension-appindicator`, `gir1.2-ayatanaappindicator3-0.1`)
  in der Paketliste verankert - erledigt 2026-08-14, dabei zusätzlich
  `gnome-shell-extension-desktop-icons-ng` (DING) ergänzt: GNOME zeigt
  seit Jahren keine Desktop-Icons mehr von Haus aus, ohne diese
  Erweiterung wären die Büro-Setup-Skripte auf `dialosadmin`s
  Arbeitsfläche (siehe unten) unsichtbar geblieben.

- ☑️ **2026-08-16** — **Optionale Windows-11-Optik für GNOME gebaut** (Stephans Wunsch
  vom 2026-08-16, umgesetzt am selben Tag).
  `/usr/local/bin/dialos-desktop-stil.sh` schaltet in beide Richtungen um
  (`windows` / `gnome` / `status`), die drei Debian-Erweiterungen
  (`dash-to-panel`, `arc-menu`, `tiling-assistant`) stehen in der
  Paketliste und werden mitinstalliert, aber nicht eingeschaltet.
  Beschrieben in `docs/Debian-zu-DialOS.md`, Schritt 11b.

- ☑️ **2026-08-16** — **Windows-Umschaltung technisch getestet (2026-08-16).** Pakete
  installiert, dreimal hin- und hergeschaltet, jeden berührten Schlüssel
  verglichen: Rückweg stellt den Auslieferungszustand her, mehrfaches
  Ausführen erzeugt keine Doppeleinträge. Dabei zwei Fehler gefunden und
  behoben (GNOME Shell kennt frisch installierte Erweiterungen nicht;
  ArcMenu-Schema liegt in Debian im falschen Ordner) - Details im
  Änderungsprotokoll.

### Installation, ISO und Systemaufbau

- ☑️ **2026-08-10** — Neuen ISO-Build mit allen gesammelten Fixes (Bootscreen,
  Avatar-Skript, Calamares-Branding, Piper-TTS) erstellen - erledigt
  2026-08-10/11 (ISO vom 11.08.).

- ☑️ **2026-08-14** — Konsolidierungs-Skript `scripts/dialos-full-office-setup.sh` +
  neues `dialos-setup-home-partition.sh` (führt `dialos-install`s LUKS/
  Stick-Logik auf einem bereits installierten System aus, ohne dessen
  Festplatten-Wipe/rsync-Kopie) erstellt, `Debian-zu-DialOS.md`/`.en.md`
  entsprechend aktualisiert (Schritt 1: Partitionierungs-Hinweis;
  Schritt 12: neues Werkzeug) - erledigt 2026-08-14, beide Skripte nur
  syntaktisch geprüft (`bash -n`), noch nicht real gelaufen (siehe
  Punkt oben).

- ☑️ **2026-08-16** — **Erledigt (2026-08-16): `dialos-install` ist ersatzlos entfallen**
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

- ☑️ **2026-08-16** — **Zeitzone/Locale entschieden (Stephan, 2026-08-16): bleibt
  `Europe/Vienna` + `de_AT.UTF-8`.** Nicht `Europe/Berlin`, wie die Doku
  bis dahin vorschrieb. Folge, jetzt in Debian-zu-DialOS.md Schritt 1
  dokumentiert: Baugerät und jede daraus gezogene ISO tragen die
  österreichischen Einstellungen (`eggs produce --clone` klont
  `/etc/localtime` + Locale mit). Am selben Tag durch die Entscheidung
  für Weg A weiter vereinfacht: Jedes Gerät wird im Büro über den
  Debian-Installer aufgesetzt, die Zeitzone wird also pro Gerät in
  Schritt 1 gewählt.

- ☑️ **2026-08-16** — **Erledigt durch Wegfall (2026-08-16):** Calamares-Standort-Seite
  schlug beim Live-Boot GeoIP-basiert oft
  einen falschen Standort vor (z. B. Rome statt Berlin) - kein
  dokumentierter Vendor-Override für `modules/locale.conf` gefunden (nur
  Branding ist offiziell überschreibbar). Bleibt vorerst
  Werkzeug-Einschränkung; installierende Person muss Standort beim
  Durchklicken manuell prüfen/korrigieren (unkritisch bei
  Zwei-Phasen-Provisionierung, da Endkunden den Installer nie sehen).

- ☑️ **2026-08-16** — Erster Eintrag in `docs/iso-builds.md` erfolgt: `eggs produce
  --clone` am 16.08. gelaufen (21/21 Schritte fehlerfrei, 6,50 GiB),
  `DialOS-Live-0.5.1-clone.iso` als Backup-Snapshot vor dem geplanten
  End-to-end-Test (siehe nächster Punkt) - Version/Datum/Commit/SHA256
  eingetragen.

- ☑️ **2026-08-16** — **Erledigt am 2026-08-16: acht alte ISOs gelöscht (~59 GB).** Alle
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

### Verschlüsselung, Konten und Sicherheit

- ☑️ **2026-08-16** — **Swap entschieden (Stephan, 2026-08-16): 8 GiB, verschlüsselt,
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

- ☑️ **2026-08-18** — **Wo liegen die Mailbox-Zugangsdaten? Entschieden am 2026-08-18:**
  Datei in `/home/nutzer`, Rechte 0600 - nicht der Schlüsselbund (der
  entsperrt sich unter Autologin nicht zuverlässig und schützt hinter
  derselben LUKS-Tür ohnehin nicht zusätzlich) und nicht der Stick (er
  trägt den LUKS-Schlüssel, kann abgezogen werden, und wäre eine zweite
  Stelle für dasselbe). Begründung in `docs/sicherheit-datenschutz.md`.
  Ursprünglich stand hier:
  DialOS liest und schreibt Mail direkt über IMAP/SMTP, weil Thunderbird
  von außen nur `-compose` kennt und kein Lesen erlaubt (siehe
  `docs/anwendungen.md`). Damit braucht DialOS die Zugangsdaten selbst.
  Zwei Wege: GNOME-Schlüsselbund über libsecret, oder eine Datei, die nur
  dem Konto gehört. **Gehört zur Sicherheits-Architektur**, nicht in eine
  Nebenentscheidung - `docs/sicherheit-datenschutz.md` mit entscheiden.
  Zum Testen liegt die Adresse `proband@dialos.org` bereit
  (Mailserver `s111.goserver.host`, keine Autoconfig-Einträge).
  **Fußzeile nicht vergessen:** Dieser Versandweg muss sich die
  Herkunftszeile selbst holen (`dialos-fusszeile.py text --art mail`).
  Die Thunderbird-Signatur vom 2026-08-20 greift nur bei Mails, die
  durch Thunderbird gehen - also bei denen des sehenden Helfers.

### Protokolle, Repo und Arbeitsumgebung

- ☑️ **2026-08-14** — `scripts/dialos-claude-setup.sh` erweitert (Git-Identität +
  `credential.helper=store` für `dialosadmin`) und tatsächlich
  ausgeführt/verifiziert - erledigt 2026-08-14. `~/DialOS`-Symlink jetzt
  bestätigt vorhanden (per `readlink -f`, zeigt korrekt auf
  `.../SanDisk-Extreme/DialOS/repo`), Sudoers-Regel war schon vorhanden,
  Git-Identität + `credential.helper` per `git config --global`
  bestätigt. (Der vorherige "erledigt"-Eintrag hierzu war falsch - das
  Skript war nie erfolgreich mit `sudo` durchgelaufen, siehe
  Commit-Historie.)

- ☑️ **2026-08-16** — **Erledigt durch den Neuaufbau (geprüft 2026-08-16):** `~/DialOS-repo`
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

- ☑️ **2026-08-16** — **Gegenstandslos seit 2026-08-16:** `/home/eggs/*.iso`-Restdateien aufräumen -
  Penguins' Eggs ist entfallen (Schritt 16, jetzt Rescuezilla), und auf dem
  neu aufgebauten T490 war es ohnehin nie installiert. Ursprünglich:
  (gehören `root`, die `eggs produce`-NOPASSWD-Regel deckt nur
  `eggs produce` selbst ab, nicht `rm` - braucht Stephans manuelles
  `sudo rm`).

- ☑️ **2026-08-20** — **Die Protokolle wachsen unbegrenzt** - erledigt 2026-08-20. Stephans
  Entscheidung: sieben Tage, dieselbe Frist wie beim Support-Protokoll.
  Umgesetzt ueber `/etc/logrotate.d/dialos` statt in den sechs Programmen -
  logrotate laeuft taeglich per systemd-Timer, waehrend ein Dienst, der eine
  Woche durchlaeuft, nie zum Aufraeumen kaeme. Ohne `copytruncate`, weil die
  Programme ihre Datei nicht offen halten (geprueft), mit `dateext`, weil im
  Support nach einem Tag gesucht wird und nicht nach einer Nummer. Offen bleibt
  nur, dass eine NEU angelegte Datei 0644 bekommt - ab der ersten Rotation gilt
  0600.
