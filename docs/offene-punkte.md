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
  nicht mit eingestecktem Kabel funktional geprueft (kein Kabel
  verfuegbar). SIM-Profil kann mangels WWAN-Hardware noch nicht angelegt
  werden - sobald vorhanden, dort ipv4.route-metric/ipv6.route-metric auf
  z. B. 900 setzen, damit SIM nur greift, wenn weder Kabel noch WLAN eine
  Route liefern.

## Sicherheit
- Wiederherstellungsweg für den USB-Sicherheits-Stick bei Verlust/Defekt:
  vorläufig als Master-Passphrase umgesetzt (zweiter LUKS-Schlüsselslot,
  wird beim Einrichten von `dialos-setup-home-partition.sh` abgefragt,
  mindestens 12 Zeichen) – ob das die
  endgültige Lösung sein soll (vs. Ersatz-Stick vs. kein Recovery) ist
  noch nicht final entschieden.
- Wie sudo/Admin-Rechte für den Standard-Benutzer ("nutzer") gehandhabt
  werden sollen, ist noch offen: normales Passwort (sicherer, aber die
  sprachgesteuerte Wartung muss das dann gezielt umgehen), auf einzelne
  Wartungsbefehle beschränktes passwortloses sudo, oder komplett
  passwortlos. Aktuell wird pro Build ein zufälliges Passwort erzeugt
  (nicht im Repo hinterlegt) statt eines festen Platzhalters.
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
- Rechtschreibprüfung (hunspell-de-de/hunspell-en-us, aspell) fehlt
  weiterhin. **Begründung überholt (korrigiert 2026-08-16):** Hier stand,
  `dictionaries-common` scheitere reproduzierbar in der
  Docker-Chroot-Build-Umgebung. Diese Umgebung gibt es seit dem Wechsel
  auf Weg A nicht mehr - die Pakete werden heute auf einem laufenden
  System per `apt` installiert, wo das Problem gar nicht auftritt. Es
  fehlt jetzt schlicht, weil es in keiner Paketliste steht. Damit ist es
  kein offener Punkt mehr, sondern eine konkrete Aufgabe (siehe
  [TODO.md](../TODO.md)).
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
  - **Mikrofon: umgesetzt.** `waehle_mikrofon_fuer_lautstaerke()` in
    `dialos-start-ansage.py` nimmt eine `bluez_input.`-Quelle, wenn eine
    da ist, sonst die erste Nicht-Monitor-Quelle - also das eingebaute
    Mikrofon.
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

  **Nicht abgedeckt und schwieriger:** ein Gerät, das *verbunden* ist,
  aber nichts überträgt (fast leerer Akku, Funkstörung). Dann greift kein
  Fallback, weil aus Systemsicht alles in Ordnung aussieht. Dafür bräuchte
  es eine echte Rückmeldung über die Wiedergabe, nicht nur über die
  Verbindung.
- Priorisierung WhatsApp vs. Signal als Messenger noch offen.

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
