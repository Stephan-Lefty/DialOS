[Deutsch](offene-punkte.md) | [English](offene-punkte.en.md)

# Offene Punkte

Sammlung aller noch nicht abschließend geklärten oder umgesetzten Themen,
damit nichts aus den Diskussionen verloren geht.

## Hardware
- Referenz-Laptop-Modell noch nicht final festgelegt (Kandidat:
  ThinkPad-X1-Klasse oder vergleichbarer leichter Business-Laptop mit
  WWAN-Option).
- Kein WWAN-Modul für praktische SIM-Tests vorhanden – Test-T490 hat
  keins verbaut. Muss für die SIM-Variante beschafft werden (sprachfähiges
  Modem, z. B. Quectel EM7565).
- Netzwerk-Priorität WLAN/Kabel vor SIM fuer Internetverbindung: ueber
  NetworkManager-Routenmetriken umgesetzt (niedrigere Metrik = bevorzugt).
  Kabel-Profil auf ipv4.route-metric/ipv6.route-metric 100, WLAN-Profil
  auf 600 gesetzt (auf dem T490 mit `nmcli connection show "<Profil>" |
  grep route-metric` verifiziert). UNGETESTET: Kabel-Metrik nur gesetzt,
  nicht mit eingestecktem Kabel funktional geprueft - **Kabel sind seit
  2026-11-25 vorhanden** (vorher war keins da), die Probe steht also an
  und ist kein Hindernis mehr. SIM-Profil kann mangels WWAN-Hardware noch nicht angelegt
  werden - sobald vorhanden, dort ipv4.route-metric/ipv6.route-metric auf
  z. B. 900 setzen, damit SIM nur greift, wenn weder Kabel noch WLAN eine
  Route liefern.

## Debian-Version: 13 bleibt, kein Sprung auf 14 (entschieden 2026-09-18)

Stephans Frage: „Würde es heute schon Sinn machen, mit Debian 14 und der
aktuellen GNOME-Version zu testen?" Antwort nach dem Abwägen: **nein, wir
bleiben bei Debian 13 und GNOME 48** (Stand am Gerät: 13.7, GNOME Shell 48.7,
Python 3.13.5).

Die Gründe, in der Reihenfolge ihres Gewichts:

1. **Debian 14 („Forky") ist heute *testing*, also eine bewegliche Basis.**
   Sicherheitsupdates kommen dort verzögert - für ein Gerät, das bei einem
   blinden Nutzer im Alltag steht, ist das der falsche Handel.
2. **Ein Fehler von heute ist morgen weg und ein neuer da.** Genau dieses Muster
   hat in diesem Projekt schon Tage gekostet: eine Ursache, die sich nicht mehr
   nachstellen lässt, ist keine Ursache.
3. **Kein Zeitdruck:** Debian 13 bekommt Sicherheitsupdates bis etwa 2028, mit
   LTS bis etwa 2030.
4. **Die Windows-Optik bricht als Erstes.** `dash-to-panel`, `arc-menu` und
   `tiling-assistant` sind GNOME-Erweiterungen und brechen typischerweise bei
   jedem GNOME-Sprung. Diese Arbeit macht man einmal - wenn die Zielversion
   feststeht.

**Was beim späteren Sprung wirklich zu prüfen ist, ist nicht GNOME, sondern die
kompilierten Fremdbibliotheken:** Vosk, sherpa-onnx (Parakeet), cairo/Pango,
GTK4. Sie hängen an Python-Version und glibc; fällt eine aus, ist die
Sprachsteuerung selbst betroffen und nicht nur die Optik.

**Der vorgeschlagene Weg, wenn es soweit ist** (nicht gebaut, bewusst
zurückgestellt): ein Container mit Debian testing, in dem der **Prüfstand**
läuft. Er braucht kein Mikrofon und keinen Desktop - er spielt die vorhandenen
Aufnahmen ab und prüft damit Vosk, Parakeet, Zahlen- und Satzzeichenregeln und
die PDF-Erzeugung in einem Durchlauf, ohne das T490 anzufassen. Sinnvoller
Zeitpunkt: **wenn Forky eingefroren ist.**

## Sicherheit
- Wiederherstellungsweg für den USB-Sicherheits-Stick bei Verlust/Defekt:
  vorläufig als Master-Passphrase umgesetzt (zweiter LUKS-Schlüsselslot,
  wird beim Einrichten von `dialos-setup-home-partition.sh` abgefragt,
  mindestens 12 Zeichen) – ob das die
  endgültige Lösung sein soll (vs. Ersatz-Stick vs. kein Recovery) ist
  noch nicht final entschieden.
- **sudo für den Standard-Benutzer `nutzer`: Der Zustand ist nicht offen,
  sondern VOLLER ADMINISTRATOR** (Stand 2026-09-25). `nutzer` steckt in der
  Gruppe `sudo`, `sudo -l -U nutzer` meldet `(ALL : ALL) ALL` (nachgesehen am
  2026-09-14). Das Passwort wird bei der Einrichtung zufällig erzeugt, aber
  `dialos-buero-setup-abschliessen.sh` **gibt es im Terminal aus** - beim
  Neuaufbau am 2026-09-25 stand es dadurch im Chat mit Claude. Geheim ist es
  damit nicht: Wer es gesehen hat oder neu setzt, hat root auf dem Gerät
  eines Nutzers, der das nicht bemerken kann. Die sprachgesteuerten
  Wartungsaufrufe brauchen die Gruppe nach bisherigem Stand nicht, weil sie
  über enge NOPASSWD-Regeln auf feste Pfade laufen. Was vor einer Änderung zu
  klären ist (woher die Mitgliedschaft kommt, welche Gruppen `nutzer` wirklich
  braucht, Gegenprobe), steht in `TODO.md`, Punkt „Das Kundenkonto `nutzer`
  hat volle Root-Rechte".

  **Frühere Fassung (bis 2026-09-25, überholt):** „Wie sudo/Admin-Rechte für
  den Standard-Benutzer gehandhabt werden sollen, ist noch offen: normales
  Passwort, auf einzelne Wartungsbefehle beschränktes passwortloses sudo, oder
  komplett passwortlos. Aktuell wird pro Build ein zufälliges Passwort erzeugt
  (nicht im Repo hinterlegt) statt eines festen Platzhalters." - „offen"
  verschleierte, dass faktisch schon volle Rechte bestanden, und „pro Build"
  stammt aus der Zeit der ISO-Builds, die es seit 2026-08-16 nicht mehr gibt.
  Die drei Varianten bleiben als Entscheidungsvorlage gültig.
- Eigener RustDesk-Relay-Server (hbbs/hbbr) ist für später geplant, sobald
  das System stabil läuft – noch kein konkreter Zeitpunkt/Ablauf.
- Boot-Zeit-Tastenkombination für direkten `dialosadmin`-Zugriff (statt
  richtigem Ab-/Anmelden, siehe sicherheit-datenschutz.md, Abschnitt
  "Automatische Anmeldung"): technisch möglich (eigener früher Boot-Dienst,
  der kurz auf einen gehaltenen Tastendruck lauscht, z. B. über rohen
  `/dev/input`-Zugriff, und je nach Ergebnis per `gdbus` das Autologin-Ziel
  umbiegt), aber bewusst zurückgestellt. **Korrigiert am 2026-08-14:**
  Ursprünglich stand hier GNOME "Benutzer wechseln" als bereits
  zuverlässige Alternative - das war falsch. Testbefund vom 2026-08-13
  zeigt, dass "Benutzer wechseln" `nutzer`s Sitzung aktiv im Hintergrund
  lässt und dadurch einen Bluetooth-/Audio-Konflikt zwischen zwei
  gleichzeitig laufenden `dialos-start-ansage.py`-Instanzen auslösen kann.
  Aktuelle Praxis ist stattdessen: `nutzer` richtig abmelden, dann als
  `dialosadmin` anmelden - funktioniert, ist aber ein Zwischenschritt mehr
  als eine Boot-Zeit-Tastenkombination böte. Diese Tastenkombination bleibt
  also eine echte, noch offene Verbesserungsoption (nicht nur ein
  "nice-to-have" wie ursprünglich vermerkt), gerade weil der direkte Weg
  über "Benutzer wechseln" wegfällt. Risiko bei Umsetzung: sauberes
  Zeitfenster nötig, sonst könnte ein zufälliger Tastendruck während des
  normalen Kundenboots ungewollt den Admin-Pfad statt des normalen
  `nutzer`-Autologins auslösen.

## System
- ~~Rechtschreibprüfung fehlt~~ **Erledigt 2026-09-14:** `hunspell-de-de` und
  `hunspell-en-us` stehen jetzt in der Paketliste. Sie waren auf dem Gerät
  schon da, aber nur indirekt über `task-german-desktop`. `aspell` bewusst
  nicht - kein Programm auf dem Gerät nutzt es. Die alte Begründung
  (Docker-Chroot) war seit dem Wechsel auf Weg A ohnehin überholt.
- Die Ein-Instanz-Sperre von `dialos-start-ansage.py` liegt auf einem
  festen Pfad im geteilten `/tmp` (`/tmp/dialos-start-ansage.pid`).
  Dieselbe Bauart hat am 2026-08-16 bei der Sprechen-Markierung Ärger
  gemacht: Wegen des Sticky-Bits kann ein Konto die Datei eines anderen
  weder überschreiben noch löschen, der Fehler bleibt still. Für die
  Markierung ist das auf `$XDG_RUNTIME_DIR` umgestellt worden, für diese
  Lock-Datei noch nicht.

## Sprachsteuerung
- Wake-Word-Engine für Akku-sparendes Dauerlauschen noch nicht final
  entschieden (Vorschlag: openWakeWord).
- **Fallback auf die eingebauten Geräte - Stephans Festlegung vom
  2026-08-16: muss IMMER gewährleistet sein.** Referenzgerät ist das
  AIRHUG-Headset (siehe [hardware.md](hardware.md)), aber ein
  ausgeschaltetes, leeres oder nicht verbundenes Bluetooth-Gerät darf
  DialOS nie stumm oder taub machen. Für einen blinden Nutzer wäre genau
  das der Totalausfall: Er merkt nicht, dass das Headset aus ist, und
  bekommt keinerlei Rückmeldung mehr.

  Grundlage der Entscheidung war der Vergleichstest vom 2026-08-13
  (AIRHUG gegen eingebautes Laptop-Mikrofon: 6 von 8 Testsätzen exakt
  korrekt über Bluetooth, deutlich schwächer beim eingebauten Mikrofon).

  **Umgekehrt seit 2026-08-17, und zwar für die Eingabe vollständig:**
  Zur Spracheingabe wird jetzt **immer das eingebaute Mikrofon** benutzt,
  die Ausgabe läuft weiter über den Bluetooth-Lautsprecher, sofern er
  verbunden ist. Drei Gründe:

  - Sobald etwas das Bluetooth-Mikrofon öffnet, fällt das Headset auf
    HFP - die Wiedergabe läuft dann in Telefonqualität (1 Kanal,
    16000 Hz statt 2 Kanäle, 48000 Hz). Am 2026-08-17 ist das
    Zurückschalten **dreimal** hängengeblieben.
  - Die Echo-Unterdrückung gibt es nur auf dem eingebauten Weg; über
    Bluetooth würde die Erkennung wieder die eigene Ansage mithören.
  - Der Vergleichstest selbst ist **nicht belastbar**: Er lief unter
    60 dB Übersteuerung des eingebauten Mikrofons (siehe TODO.md,
    „Mikrofon-Vergleich wiederholen"). Er hat womöglich nicht das
    Mikrofon gemessen, sondern die Übersteuerung.

  **Stand der Umsetzung (korrigiert am 2026-08-16 - hier stand vorher
  fälschlich "nicht implementiert"):**
  - **Mikrofon: umgesetzt.** ~~`waehle_mikrofon_fuer_lautstaerke()` in
    `dialos-start-ansage.py` nimmt eine `bluez_input.`-Quelle, wenn eine
    da ist, sonst die erste Nicht-Monitor-Quelle - also das eingebaute
    Mikrofon.~~ **Überholt seit 2026-08-17** (hier erst am 2026-09-25
    nachgetragen): Die Reihenfolge ist umgedreht. Die Sprachdienste wählen
    ihr Mikrofon selbst, in dieser Reihenfolge: (1) die Echo-Quelle
    `dialos_mikrofon_ohne_echo`, die selbst am eingebauten Mikrofon hängt,
    (2) das eingebaute Mikrofon, (3) Bluetooth **nur**, wenn es gar kein
    eingebautes gibt. Das Umschalten des AIRHUG auf HFP kommt damit nur noch
    in diesem Rückfall vor.
  - **Standard-Mikrofon für alle anderen Programme bleibt bewusst das rohe
    eingebaute** (Stephans Entscheidung, 2026-09-25). Firefox und damit
    Jitsi haben eine eigene Echo-Unterdrückung; mit der bereinigten Quelle
    liefe sie doppelt, und die Gegenseite hörte verwaschene Sprache. Am
    2026-09-25 war die Echo-Quelle für einige Stunden per
    `priority.session = 2500` Standard und wurde am selben Abend
    zurückgenommen (Einzelheiten in
    [Debian-zu-DialOS.md](Debian-zu-DialOS.md) und
    [anwendungen.md](anwendungen.md)).
  - **Lautsprecher: implizit umgesetzt.** `spd-say` spricht über
    Speech-Dispatchers Standard-Senke; verschwindet das
    Bluetooth-Gerät, zieht PipeWire die Standard-Senke selbst auf die
    eingebaute um.
  - **Lautsprecher: am 2026-08-16 mit ausgeschaltetem Headset geprüft -
    Ton kam aus dem eingebauten Lautsprecher.** Damit ist die
    Ausgabeseite belegt.
  - **Mikrofon: noch nicht ohne Bluetooth getestet.** Das ist der
    verbleibende offene Punkt - nicht das Fehlen der Logik. Prüfen lässt
    es sich, indem man den gemerkten Lautstärke-Wert löscht
    (`sudo rm /home/nutzer/.config/dialos/lautstaerke`) und sich bei
    ausgeschaltetem Headset als `nutzer` anmeldet: Dann kommt die Frage
    erneut und muss über das eingebaute Mikrofon verstanden werden.
    **Erledigt durch die Umstellung vom 2026-08-17** (nachgetragen
    2026-09-25): Seitdem hört DialOS immer über das eingebaute Mikrofon,
    auch wenn der Lautsprecher verbunden ist. Der Weg, der hier als
    ungetestet stand, ist damit der tägliche und seither in jeder Sitzung
    benutzt.

  **Nicht abgedeckt und schwieriger:** ein Gerät, das *verbunden* ist,
  aber nichts überträgt (fast leerer Akku, Funkstörung). Dann greift kein
  Fallback, weil aus Systemsicht alles in Ordnung aussieht. Dafür bräuchte
  es eine echte Rückmeldung über die Wiedergabe, nicht nur über die
  Verbindung.
- Priorisierung WhatsApp vs. Signal als Messenger noch offen.

## Ein System, das mitwaechst - Stufen statt Varianten (Frage vom 2026-11-19, SEIT 2026-11-24 IM BAU)

> **Stephan, 2026-11-24:** „Lass uns jetzt schon die Schritte einbauen, denn
> dann können wir diese auch schon testen. Und wir können DialOS auch Usern an
> die Hand geben, die heute keine Beeinträchtigung haben!"

**Gebaut am 2026-11-24** - damit ist der Zeitpunkt „nicht vor der ersten
Auslieferung" weiter unten von Stephan bewusst vorgezogen:
- `dialos_stufe.py`: Stufe je Konto in `~/.config/dialos/stufe`, **ohne Datei
  Stufe 3** (das DialOS von vorher - bestehende Geräte merken nichts). Welche
  Ansage-Art ab welcher Stufe kommt: Begrüßung, Antwort, Rückfrage, Warnung in
  jeder Stufe; **Zustandswechsel** („Ton über Lautsprecher", „Internet
  hergestellt") erst ab Stufe 2.
- `dialos-say.py --art ART` schweigt, wenn die Art in der Stufe nicht dran ist.
- `dialos-stufe.py` wechselt (zeigen, mehr, weniger, setzen) und setzt **ab
  Stufe 1 Sehhilfen**: Schrift 1,25-fach, hoher Kontrast, Mauszeiger 48 - nur
  beim Überschreiten der Grenze zu Stufe 1, nie bei jedem Anmelden.
- Sprache: **„mehr Unterstützung"** / **„Unterstützung verringern"** (Stephans
  Wahl; „weniger Unterstützung" lag mit 0,82 genau auf der Schwelle).
- Fenster **„DialOS Unterstützung"** im Menü (`dialos-stufe-schalter.py`) -
  vier Knöpfe, derselbe Weg wie der Sprachbefehl.
- Stufe 0 hört nach der Begrüßung erst nach „Sprachsteuerung starten" zu - das
  war schon vorher so (Stephans Wahl bestätigt es).

**Seit dem 2026-11-24 auch:** „markierten Text vorlesen" über die eigene
GNOME-Erweiterung dialos@dialos.org. **Noch nicht gebaut:** den ganzen
Bildschirm vorlesen (bräuchte Orca); was Stufe 3
von Stufe 2 unterscheidet, ist noch offen - heute verhalten sie sich gleich.


> **Stephan, 2026-11-19, der erste Anlauf:** „Ich bin gerade beim
> überlegen, ob es nicht sinnvoll ist DialOS so aufzubauen, dass der Fokus
> auf Personen mit Beeinträchtigung liegt, wir aber auch eine Version für
> Personen ohne Beeinträchtigung fertig machen."

> **Und am selben Tag die Praezisierung, auf die es ankommt:** „Mein
> Gedanke war auch eher der, man startet als Mensch ohne Beeinträchtigung
> mit DialOS und um so stärker eine Beeinträchtigung wird um so mehr
> unterstützt DialOS. Ohne Betriebssystem wechsel usw."

**Nicht entschieden.** Festgehalten, damit die Frage nicht verloren geht -
und damit niemand sie noch einmal falsch versteht. Claude hat sie beim
ersten Mal als „zwei getrennte Fassungen" gelesen und mit dem Hinweis auf
GuideOS abgelehnt. **Dieser Einwand traf die Idee nicht** und ist hiermit
zurueckgenommen: GuideOS ist ein Einsteigersystem, es waechst nicht mit
und hat keine Sprachsteuerung, die man dazuschalten koennte.

**Warum der Gedanke traegt.** Blindheit ist meist kein Zustand, sondern
ein Verlauf - Makuladegeneration, Glaukom, diabetische Retinopathie,
Retinitis pigmentosa; motorisch MS, Parkinson, ALS. Kaum jemand wacht
blind auf.

Und der haerteste Moment in diesem Verlauf ist genau der **Wechsel**. Wer
mit 72 nicht mehr lesen kann, muesste nach heutigem Stand gleichzeitig ein
neues Betriebssystem lernen, Daten umziehen, einen Screenreader
beherrschen, neue Programme begreifen und Hilfe organisieren - in der
Lebensphase, in der Lernen am schwersten faellt und der Verlust frisch
ist. Das ist der Punkt, an dem Menschen aufhoeren, Computer zu benutzen:
nicht beim Sehverlust, sondern beim Umstieg.

Der Ansatz dreht das um: **Gelernt wird, solange Lernen leicht ist.** Wer
mit 65 und gutem Sehvermoegen „Brief schreiben" sagt, weil es bequemer ist
als tippen, kennt die Befehle schon, wenn er sie mit 75 braucht. Dann wird
nicht umgestellt, sondern zugeschaltet - dasselbe Geraet, dieselben Daten,
dieselben Befehle, derselbe Helfer.

Nebenbei loest das ein Verkaufsproblem: Niemand kauft gern „ein System
fuer Blinde" fuer den Vater, der langsam schlechter sieht - das fuehlt
sich an wie eine Kapitulation. Ein normaler Rechner, der spaeter hilft,
ist etwas, das man kauft.

**Technisch ist das ein Stufen-, kein Variantenkonzept** - und die
Bausteine liegen da. Die Optik-Umschaltung „auf Windows / auf Linux
umschalten" (seit 2026-08-16) zeigt, dass Profile im System funktionieren;
die Sprachsteuerung ist ein Dienst, der laeuft oder nicht; die Schalter in
`~/.config/dialos/` gelten pro Konto. Grober Entwurf, nicht entschieden:

| Stufe | Was an ist | Fuer wen |
|---|---|---|
| 0 | normaler Desktop, Sprachbefehle verfuegbar, **Begruessung ja**, sonst keine Ansagen | sieht gut, nutzt Sprache aus Bequemlichkeit |
| 1 | Vorlesen auf Zuruf, grosse Schrift, hoher Kontrast | Sehschwaeche, liest noch |
| 2 | Ansagen bei jedem Zustandswechsel, Frageton, Bestaetigungen | liest kaum noch |
| 3 | vollstaendig blind bedienbar, Bildschirm irrelevant | das heutige DialOS |

Der Wechsel von 2 auf 3 waere ein Sprachbefehl oder ein Handgriff des
Angehoerigen - keine Neuinstallation.

> **Stephan, 2026-11-24:** „Also die Begrüßung würde ich auch bei Stufe 0
> drin lassen!"

**Die Begruessung gehoert also zu jeder Stufe.** Das passt zum Kern: Wer
schon bei Stufe 0 von Michael begruesst wird, kennt die Stimme, wenn er sie
braucht. Offen bleibt fuer Stufe 0 nur, was NACH der Begruessung kommt -
Ansagen bei Zustandswechseln, und ob die Befehlserkennung ab dem Anmelden
zuhoert.

**Drei Punkte, die vor einer Entscheidung geklaert gehoeren.**

1. **Die Stufen kann man nicht am Schreibtisch festlegen.** Dafuer braucht
   es Menschen, die in Stufe 1 oder 2 leben - die gibt es im Projekt noch
   nicht. Alles oben ist ein Entwurf, kein Ergebnis.
2. **Jede Stufe braucht ihre eigene Abnahme.** Vier Stufen heissen
   vierfacher Pruefaufwand bei jedem Neuaufbau (alle vier Wochen), und das
   trifft dieselbe Person, die schon allein arbeitet. Billiger als zwei
   getrennte Varianten (zweite Paketliste, zweites Aufbau-Rezept, zweiter
   Satz Tests, alles zweisprachig), aber nicht kostenlos.
3. **Stufe 0 muss fuer sich stehen.** Ist sie nur „DialOS mit
   abgeschalteten Ansagen", dann ist sie ein Debian mit Extras - und
   niemand nimmt das statt Ubuntu. Sie braucht einen eigenen Grund, und
   der einzige, der traegt, ist das Mitwachsen selbst. Dann muss das aber
   auch der erste Satz auf der Website sein, nicht ein Nebensatz.

**Zeitpunkt:** nicht vor der ersten Auslieferung. DialOS hat kein Geraet
ausgeliefert, das Referenzgeraet ist nicht geprueft, Telefonie ist nicht
gebaut, die Installationsanleitung ist weiter der Pruefling. Die Idee
gehoert in die Produktplanung fuer die Zeit NACH dem ersten Kunden - aber
sie gehoert dort hin, und zwar weit oben.

## Projekt/Repository
- Logo: Erster Entwurf als Platzhalter vorhanden, Stephan arbeitet
  parallel an einem eigenen Design.

## Bereits entschieden (zur Vermeidung von Doppel-Diskussionen)
- Debian bleibt Basis (kein Wechsel zu atomarem System).
- Ersteinrichtung läuft vollständig sprachgeführt, auch für allein
  stehende Nutzer.
- Auslieferungsziel ist ein Laptop mit eingebauter SIM, Handy-Anbindung
  ist der Fallback.
- Kontakte werden laufend synchronisiert (CardDAV), nicht nur einmalig
  importiert.

## 2026-08-13: Bluetooth-Lautsprecher/Sprachausgabe manchmal nicht hörbar nach Login

**Symptom:** Nach dem Login blieb die Start-Ansage über den Bluetooth-
Lautsprecher (AIRHUG 01) intermittierend aus - mal funktionierte es, mal
nicht, ohne erkennbares Muster.

**Vermutete Hauptursache:** GNOME "Benutzer wechseln" (statt richtigem
Abmelden) ließ alte Sitzungen im Hintergrund aktiv - dabei liefen
zeitweise `nutzer`- und `dialosadmin`-Sitzung gleichzeitig auf `seat0`,
jede mit eigener `dialos-start-ansage.py`-Instanz (das Skript endet nie
von selbst wegen der Netzwerk-Hintergrundüberwachung). Mehrere Instanzen
konkurrierten vermutlich um `bluetooth_reconnect_alle()` und die
Audio-Stummschaltung in `dialos-say.py`.

**Fix (dialos-start-ansage.py):**
- `alte_instanz_beenden()`: Lock-Datei `/tmp/dialos-start-ansage.pid`,
  beendet beim Start eine evtl. noch laufende alte Instanz desselben
  Kontos (funktioniert nicht kontoübergreifend, da keine sudo-Rechte im
  Skript - das ist gewollt).
- `bluetooth_debug_snapshot()`: schreibt bei jedem Lauf zwei
  Zeitstempel-Schnappschuesse (`bluetoothctl info` je gekoppeltem Gerät +
  `pactl list sinks short` + `pactl get-default-sink`) nach
  `/tmp/dialos-bluetooth-debug.log`, direkt vor und nach dem
  Reconnect-Versuch.

**Praxis-Regel:** Kontowechsel immer über echtes **Abmelden**, nie über
"Benutzer wechseln" - sonst bleiben alte Sitzungen aktiv und konkurrieren
um Bluetooth-/Audio-Hardware.

**Status:** Nach dem Fix bisher kein erneuter Fehlschlag beobachtet,
u.a. bei einem echten Neustart mit Autologin für `nutzer`. Noch nicht
über einen längeren Zeitraum endgültig bestätigt - `/tmp/dialos-
bluetooth-debug.log` bei einem erneuten Auftreten prüfen.
