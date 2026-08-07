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
legt zusätzlich ein Wiederherstellungs-Passwort als zweiten LUKS-Slot an
(siehe unten), kopiert das laufende System auf die Platte und richtet
den Bootloader ein. Gedacht für dich/Techniker im Büro-Setup, nicht für
die Vor-Ort-Einrichtung – deshalb bewusst nicht sprachgesteuert.

**Praxishinweise:**
- Der Stick sollte getrennt vom Laptop aufbewahrt werden (z. B. am
  Schlüsselbund), sonst bringt die Verschlüsselung wenig, falls beides
  zusammen entwendet wird.
- **Offen**: Wiederherstellungsweg, falls der Stick verloren geht oder
  kaputt ist (Optionen: Master-Passphrase bei einer Vertrauensperson
  hinterlegen, ein baugleicher Ersatz-Stick, oder bewusst kein Recovery –
  noch nicht entschieden).

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
