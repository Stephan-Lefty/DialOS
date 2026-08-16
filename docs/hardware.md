[Deutsch](hardware.md) | [English](hardware.en.md)

# Hardware

## Zielgerät

Ein leichter Laptop, der nicht nur stationär zuhause, sondern auch auf
Reisen/unterwegs nutzbar ist. Das schließt reine USB-Stick-WWAN-Lösungen
tendenziell aus (Bruchgefahr, weniger robust) und spricht für ein fest
verbautes WWAN-Modul in einem leichten Business-Laptop.

Mit den zusätzlichen, stark hardwareabhängigen Funktionen (Sprachsteuerung,
Verschlüsselungs-Stick, ggf. WWAN-Telefonie) bewegt sich das Projekt von
"ISO für beliebigen Laptop" zu "ISO + definierte/empfohlene
Referenz-Hardware" – eine konkrete Modellfestlegung (z. B. ThinkPad-X1-Klasse)
steht noch aus.

## Referenz-Audiogerät (festgelegt 2026-08-16)

**AIRHUG 01** – Bluetooth-Headset, gleichzeitig Lautsprecher und
Mikrofon. Damit ist der wichtigste offene Hardware-Punkt entschieden:
Die Sprachsteuerung wird gegen dieses Gerät entwickelt und justiert.

Technische Eckdaten, ausgelesen am Referenzgerät:

| | |
|---|---|
| Bluetooth-Name | `AIRHUG 01` |
| Geräteklasse | `0x00240404` (Audio/Headset) |
| Profile | **A2DP** (Audio Sink) und **HFP** (Handsfree) |
| Akku-Meldung | über UPower, taucht in der Start-Ansage auf |

**Der entscheidende Punkt für die Sprachsteuerung:** Das Gerät kann
A2DP und HFP nicht gleichzeitig. A2DP liefert gute Wiedergabe, hat aber
keinen Mikrofonkanal; HFP bringt das Mikrofon, senkt dafür die
Wiedergabequalität deutlich. Deshalb schaltet
[`dialos-start-ansage.py`](../iso-build/config/includes.chroot/usr/local/bin/dialos-start-ansage.py)
vor einer Aufnahme auf `headset-head-unit` und danach zurück auf
`a2dp-sink` – dieser Profilwechsel ist keine Eigenart des Codes, sondern
eine Eigenschaft der Bluetooth-Profile selbst und wird bei jedem
vergleichbaren Headset nötig sein.

Warum ein Headset und nicht das eingebaute Laptop-Mikrofon: Der
Vergleichstest fiel eindeutig aus (siehe
[offene-punkte.md](offene-punkte.md), Abschnitt "Sprachsteuerung"). Das
eingebaute Mikrofon bleibt als noch nicht umgesetzter Rückfall gedacht.

**Noch zu klären:** ob das Gerät seine eigenen Firmware-Ansagen
("verbunden", Akku-Warnung) auf Deutsch ausgibt. Über die
Bluetooth-Standardprofile lässt sich das nicht fernsteuern, es ist rein
geräteabhängig – bei einem System für blinde Nutzer aber nicht
nebensächlich, weil diese Ansagen der Nutzer zwangsläufig mithört.

## Aktuelle Test-Hardware

- **Laptop**: Lenovo ThinkPad T490 – kein WWAN-/LTE-Modul verbaut.
- **Audio**: AIRHUG 01 (siehe oben) – seit 2026-08-16 Referenzgerät.
- **Eingabegeräte**: Logitech Pebble M350s (Maus) und Pebble K380s
  (Tastatur), beide über Bluetooth. Ihr Akkustand wird von der
  Start-Ansage vorgelesen – allerdings nur für Administratorkonten;
  `nutzer` bekommt bewusst nur Laptop und Lautsprecher genannt.
- **USB-Stick**: als Sicherheits-Stick (empfohlene Größe 64 GB, siehe
  [sicherheit-datenschutz.md](sicherheit-datenschutz.md)) - bisher
  irgendein vorhandener Stick, kein konkretes Referenzprodukt.
- **Android-Handy**: für Tests der Handy-Anbindung (USB-Tethering +
  GSConnect).

Da das Test-T490 kein WWAN-Modul hat, laufen die ersten praktischen Tests
über den Handy-Anbindungspfad (siehe [telefonie.md](telefonie.md)). Die
SIM-Variante muss auf passender Zusatzhardware nachgezogen werden.

## WWAN-Modul-Auswahl (für die SIM-Variante)

Nicht jedes LTE-Modem unterstützt Sprachanrufe (Voice/VoLTE über
ModemManager) – viele USB-/M.2-Module sind reine Datenmodems. Für
Telefonie über die eingebaute SIM muss gezielt ein sprachfähiges Modem
gewählt werden (z. B. Quectel EM7565, Sierra-Wireless-Module).

## Offene Punkte

- ~~Referenz-Audiogerät~~ – **entschieden am 2026-08-16: AIRHUG 01**
  (siehe oben).
- Referenz-Laptop-Modell noch nicht final festgelegt.
- Referenz-Sicherheits-Stick (Marke/Modell, USB-A vs. USB-C) noch nicht
  final festgelegt - empfohlene Größe (64 GB) und Dateisystem-Aufteilung
  (`DIALOS-KEY`/`DIALOS-DATA`) stehen bereits (siehe
  [sicherheit-datenschutz.md](sicherheit-datenschutz.md)), aber kein
  konkretes Produkt ausgewählt.
- Kein WWAN-Modul für praktische SIM-Tests vorhanden – muss beschafft werden.
