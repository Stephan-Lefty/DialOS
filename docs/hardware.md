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

## Aktuelle Test-Hardware

- **Laptop**: Lenovo ThinkPad T490 – kein WWAN-/LTE-Modul verbaut.
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

- Referenz-Laptop-Modell noch nicht final festgelegt.
- Referenz-Sicherheits-Stick (Marke/Modell, USB-A vs. USB-C) noch nicht
  final festgelegt - empfohlene Größe (64 GB) und Dateisystem-Aufteilung
  (`DIALOS-KEY`/`DIALOS-DATA`) stehen bereits (siehe
  [sicherheit-datenschutz.md](sicherheit-datenschutz.md)), aber kein
  konkretes Produkt ausgewählt.
- Kein WWAN-Modul für praktische SIM-Tests vorhanden – muss beschafft werden.
