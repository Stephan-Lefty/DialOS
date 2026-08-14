[Deutsch](sicherheit-datenschutz.md) | [English](sicherheit-datenschutz.en.md)

# Sicherheit & Datenschutz

## Grundprinzip

Die Zielgruppe (blinde, motorisch eingeschränkte, teils ältere Menschen)
ist besonders vulnerabel. Datenschutz und Ausfallsicherheit haben deshalb
durchgehend Priorität vor Bequemlichkeit oder Erkennungsqualität:

- Spracherkennung läuft offline (Vosk/lokale Modelle), keine Cloud-Dienste.
- Sicherheitskritische Aktionen laufen immer über eine explizite
  Ja/Nein-Rückfrage.
- Es wird immer davon ausgegangen, dass jemand seine Zugangs-/Einrichtungsdaten
  nicht ohne Weiteres zur Verfügung stellen möchte (siehe
  [ersteinrichtung.md](ersteinrichtung.md), Abschnitt "Datenschutz-Varianten").

## Automatische Anmeldung

Der Login-Bildschirm entfällt komplett (GDM-Autologin), da er für die
Zielgruppe eine der größten Hürden wäre (Passwort blind tippen,
Login-Auswahl bedienen). Trade-off: physischer Zugriff auf das Gerät
bedeutet direkten Zugriff auf das System – das wird durch die
Festplattenverschlüsselung mit Hardware-Schlüssel abgefedert (siehe unten).

**Admin-Zugriff:** Das Autologin-Konto ist immer `nutzer`
(`AutomaticLogin=true`), das Admin-Konto `dialosadmin` bleibt aktiv, aber
ohne Autologin (`AutomaticLogin=false`) – siehe
`scripts/dialos-setup-nutzer.sh`. Für Eingriffe vor Ort oder per RustDesk
(nachdem `nutzer` per Sprachbefehl "Hilfe rufen" gesagt hat): `nutzer`
**richtig abmelden**, danach am GDM-Bildschirm als `dialosadmin` mit
Passwort anmelden. Setzt voraus, dass `dialosadmin` ein gültiges, nicht
gesperrtes Passwort hat.

**Wichtig, korrigiert am 2026-08-14:** GNOME **"Benutzer wechseln"**
(statt richtigem Abmelden) bewusst **vermeiden** – lässt `nutzer`s
Sitzung im Hintergrund aktiv. Laut Testbefund vom 2026-08-13 (siehe
[offene-punkte.md](offene-punkte.md), Eintrag "Bluetooth-Lautsprecher/
Sprachausgabe manchmal nicht hörbar nach Login") konkurrieren dann zwei
gleichzeitig laufende `dialos-start-ansage.py`-Instanzen (eine pro
Konto) um Bluetooth-Reconnect und Audio-Stummschaltung, was die
Sprachausgabe unzuverlässig macht. Der vorhandene Ein-Instanz-Lock in
`dialos-start-ansage.py` verhindert nur doppelte Anmeldungen
*desselben* Kontos, nicht das kontoübergreifende Nebeneinander, das
"Benutzer wechseln" erzeugt.

## Festplattenverschlüsselung mit USB-Schlüssel

Der PC soll nur booten/entsperren, wenn ein bestimmter USB-Stick
eingesteckt ist. Umsetzung: **LUKS-Festplattenverschlüsselung mit einer
Schlüsseldatei auf dem USB-Stick** – ein Skript im initramfs wartet beim
Boot auf den Stick und entsperrt die Platte automatisch, sobald er erkannt
wird, ganz ohne Passworteingabe. Fehlt der Stick, bleibt das System
verschlüsselt.

Kombiniert mit Autologin ergibt das einen für die Zielgruppe idealen
Ablauf: Stick rein → Gerät einschalten → System ist sofort einsatzbereit
und spricht den Nutzer an, ohne dass irgendwo getippt oder etwas
abgelesen werden muss.

**Installation:** Aus der laufenden Live-Session heraus gibt es dafür ein
eigenes Installations-Werkzeug (`dialos-install`, per Programm-Menü
aufrufbar) statt eines Standard-Installers wie Calamares – dessen
LUKS-Modul ist auf ein getipptes Passwort ausgelegt, nicht auf unser
Stick-Schlüssel-Konzept. Das Werkzeug partitioniert die Zielfestplatte,
erzeugt einen zufälligen Schlüssel auf dem gewählten Sicherheits-Stick,
legt zusätzlich ein Wiederherstellungs-Passwort (mind. 12 Zeichen) als
zweiten LUKS-Slot an (siehe unten), kopiert das laufende System auf die
Platte und richtet
den Bootloader ein. Gedacht für dich/Techniker im Büro-Setup, nicht für
die Vor-Ort-Einrichtung – deshalb bewusst nicht sprachgesteuert.

**Praxishinweise:**
- Der Stick sollte getrennt vom Laptop aufbewahrt werden (z. B. am
  Schlüsselbund), sonst bringt die Verschlüsselung wenig, falls beides
  zusammen entwendet wird.

## Sicherheits-Stick als Anwesenheits-Token (Autologin-Gate)

**Ergänzung seit 2026-08-14**, unabhängig von der Verschlüsselung oben.

**Warum:** Der reale Live-Boot-Test von `dialos-install` mit dem
Sicherheits-Stick ist am 14.08. gescheitert. Grund war nicht ein
einzelner Bug, sondern dass der ganze LUKS/initramfs-Weg strukturell
fehleranfällig ist: die Schlüsseldatei muss exakt im richtigen Moment
im initramfs verfügbar sein (ein Bug hängte den Stick vor der
`cryptsetup open`-Nutzung schon aus), und selbst der Installer selbst
lief nicht rund (ein `pkexec`-Bug ließ den Datei-Speichern-Dialog für
das Schlüssel-Backup lautlos scheitern, siehe README-Änderungsprotokoll
0.5.0). Ein initramfs bietet kaum Fehlerausgabe/Debugging-Möglichkeiten
für die Zielgruppe vor Ort - jeder Fehler dort bedeutet ein
nicht bootendes Gerät ohne Hilfe von Stephan. Statt den fragilen Weg
weiter zu flicken, gibt es jetzt zusätzlich einen viel robusteren,
rein softwarebasierten Anwesenheits-Check, der komplett in einer schon
laufenden, normalen Systemumgebung läuft (kein initramfs, keine
`pkexec`/xdg-portal-Fallstricke) - unabhängig vom initramfs/LUKS-Weg
oben:

- Ein systemd-Dienst (`dialos-stick-gate.service`, läuft als oneshot vor
  `display-manager.service`) prüft bei **jedem Boot**, ob eine Partition
  mit Label `DIALOS-KEY` gefunden wird (`blkid -L DIALOS-KEY`, mit
  kurzer Wiederholschleife für nachhinkende USB-Erkennung).
- Stick da: Autologin für `nutzer` wird aktiviert
  (`SetAutomaticLogin true` über AccountsService/`gdbus`, derselbe
  Mechanismus wie in `scripts/dialos-setup-nutzer.sh` und
  [Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 4).
- Stick fehlt: Autologin für `nutzer` wird deaktiviert
  (`SetAutomaticLogin false`). GDM zeigt den normalen Login-Bildschirm -
  darauf ist praktisch nur `dialosadmin` nutzbar, da `nutzer`s Passwort
  ein zufälliger, niemandem bekannter String ist.
- `dialosadmin` bleibt davon komplett unberührt: nie Autologin, immer
  normales getipptes Passwort am GDM-Screen, wie bisher.

Skript: `usr/local/sbin/dialos-stick-gate.sh`, Unit:
`etc/systemd/system/dialos-stick-gate.service` (beide im Repo unter
`iso-build/config/includes.chroot/`, Installation siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 12).

**Wichtige Einschränkung:** Das ist ein reiner **Zugriffs-Filter beim
Login**, keine Verschlüsselung. Die Festplatte selbst bleibt durch
dieses Gate ungeschützt - wer sie ausbaut oder das Gerät von einem
Live-USB bootet, liest alle Daten direkt, unabhängig davon, ob der
Stick dabei ist. Diese Lücke schließt weiterhin nur die LUKS-
Verschlüsselung oben. Ob die LUKS-Verschlüsselung (mit ihrer
fehleranfälligen initramfs-Installation) langfristig neben diesem Gate
bestehen bleibt oder entfällt, ist eine offene Entscheidung (siehe
TODO.md) - aktuell laufen beide Mechanismen unabhängig nebeneinander.

## Wiederherstellung bei Stick-Verlust

Drei Wege, je nach Situation:

1. **Wiederherstellungs-Passwort direkt am Boot-Bildschirm eintippen.**
   Funktioniert sofort, komplett offline, unabhängig vom Stick und vom
   Netzwerk – der einzige Weg, ein Gerät überhaupt wieder zum Laufen zu
   bringen, wenn nichts anderes erreichbar ist. Wird von Stephan
   telefonisch angeleitet oder von einer Vertrauensperson vor Ort
   eingetippt, nicht vom Endnutzer selbst gewusst.
2. **Neuen Stick per Fernwartung einrichten** (`dialos-rekey`, auf dem
   installierten System). Sobald das Gerät einmal läuft (z. B. nach Weg 1)
   und der Nutzer "Hilfe rufen" sagt, verbindet sich Stephan per RustDesk
   und richtet remote einen neuen Stick ein: neuer Schlüssel wird erzeugt,
   als LUKS-Schlüssel hinzugefügt, der alte (verlorene) Schlüssel-Slot wird
   entwertet, ein neues Wiederherstellungs-Passwort wird vergeben.
3. **Ersatz-Stick von Stephan anfertigen und per Post verschicken**, falls
   das Gerät gar nicht mehr bootet (auch Weg 1 nicht möglich, z. B.
   Hardware-Defekt oder Passwort nicht griffbereit). Dafür lädt Stephan
   das verschlüsselte Schlüssel-Backup dieses Nutzers aus der eigenen
   Nextcloud, entschlüsselt es lokal mit dem zugehörigen
   Wiederherstellungs-Passwort und schreibt den Schlüssel auf einen neuen
   Stick.

Für Weg 2 und 3 braucht es das **verschlüsselte Schlüssel-Backup**: Der
Installer (`dialos-install`) und das Rekey-Werkzeug (`dialos-rekey`)
verschlüsseln die kleine Schlüsseldatei (nicht die ganze Festplatte) mit
einem eigenen, zufällig erzeugten Backup-Passwort (`openssl rand
-base64 32`, verschlüsselt via `openssl enc -aes-256-cbc -pbkdf2`) und
bieten an, die Datei zu speichern – Stephan legt sie in seiner eigenen,
selbst gehosteten Nextcloud ab (eine Datei pro Nutzer/Gerät), statt bei
einem fremden Cloud-Anbieter.

**Wichtig: Das Backup-Passwort ist bewusst NICHT dasselbe wie das
Wiederherstellungs-Passwort** aus Weg 1/2 oben. Würde dieselbe
Passphrase für beides verwendet, könnte jeder mit Kenntnis des
Wiederherstellungs-Passworts und Zugriff auf die Nextcloud den
Schlüssel entschlüsseln – ganz ohne den physischen Stick, was den
eigentlichen Zweck der Stick-Bindung aushebeln würde. Das
Skript zeigt das generierte Backup-Passwort einmalig nach dem
Speichern an; Stephan muss es getrennt von der Nextcloud aufbewahren
(z. B. im eigenen Passwort-Manager), niemals zusammen mit der
Backup-Datei selbst.

## Versand-Sicherheit

Laptop und Sicherheits-Stick sollen getrennt versendet werden
(unterschiedlicher Tag/Paketdienst), damit ein abgefangenes Paket allein
nutzlos ist.

## Fernwartung (RustDesk)

- Open Source, selbst hostbar – passt zur Datenschutz-Linie des Projekts.
- **Relay**: zunächst der öffentliche rustdesk.com-Dienst, später (sobald
  das System stabil läuft) ein eigener Server (hbbs/hbbr). Migration ist
  ein bewusst offener Punkt für später.
- **Unbeaufsichtigter Zugriff** läuft mit einem dauerhaften Passwort,
  damit ein Helfer auch reinkommt, wenn der Nutzer gerade nicht reagieren
  kann. Für blinde Nutzer muss die RustDesk-ID/das Passwort per TTS
  vorgelesen werden, da sie nicht selbst ablesbar sind.
- **Zusätzliche Sicherheitsschicht**: RustDesk läuft NICHT dauerhaft im
  Hintergrund/Autostart. Der Nutzer vor Ort muss RustDesk erst aktiv per
  Sprachbefehl starten (z. B. "Hilfe rufen") – erst danach ist eine
  Fernverbindung überhaupt möglich, trotz des dauerhaften Passworts.
  Konsequenz: "echte" Notfall-Fernwartung (Nutzer reagiert gar nicht mehr,
  System eingefroren) funktioniert damit bewusst nicht – nur aktiv vom
  Nutzer angeforderte Hilfe.

## System-Basis

Debian bleibt die Basis (kein Wechsel zu einem atomaren/unveränderlichen
System wie Fedora Atomic/Silverblue oder openSUSE Aeon) – Stephans
Priorität liegt auf Debians Stabilität, Hardware-Support und dem
ausgereiften live-build-Tooling gegenüber eingebautem Atomic-Rollback.
Eine Rollback-Absicherung müsste bei Bedarf separat über Btrfs-Snapshots
nachgerüstet werden.
