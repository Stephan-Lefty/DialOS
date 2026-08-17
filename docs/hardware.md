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

**Zwingende Regel (Stephan, 2026-08-16): Der Rückfall auf die
eingebauten Lautsprecher und das eingebaute Mikrofon muss immer
gewährleistet sein.** Ein ausgeschaltetes, leeres oder nicht verbundenes
Headset darf DialOS nie stumm oder taub machen - für einen blinden Nutzer
wäre genau das der Totalausfall, weil er gar nicht bemerkt, dass das
Headset aus ist. Stand der Umsetzung und was daran noch offen ist: siehe
[offene-punkte.md](offene-punkte.md).

**Noch zu klären:** ob das Gerät seine eigenen Firmware-Ansagen
("verbunden", Akku-Warnung) auf Deutsch ausgibt. Über die
Bluetooth-Standardprofile lässt sich das nicht fernsteuern, es ist rein
geräteabhängig – bei einem System für blinde Nutzer aber nicht
nebensächlich, weil diese Ansagen der Nutzer zwangsläufig mithört.

## Reichweite und Tasten: warum ein Gerät nicht reicht

**Erkannt am 2026-08-17 durch Stephans Frage:** Der Laptop steht auf dem
Schreibtisch, der Bluetooth-Lautsprecher auf dem Wohnzimmertisch und
spielt Radio - wie ändert der Nutzer von dort die Lautstärke? Über das
eingebaute Mikrofon des Laptops gar nicht.

Das ist keine Feinheit, sondern trifft den vorgesehenen Regelfall.
Daraus folgt die Anforderung: **Das Eingabegerät muss dort sein, wo der
Nutzer ist. Das Ausgabegerät darf überall stehen.**

### Was der AIRHUG 01 kann - und was nicht

| | |
|---|---|
| A2DP (gute Wiedergabe) | `sources: 0` - **kein Mikrofon** |
| HFP (Mikrofon verfügbar) | Wiedergabe fällt auf 1 Kanal / 16000 Hz |
| Tasten am Gerät | erreichen den Laptop **nicht** |
| Lautstärketasten am Gerät | melden sich **nicht** am Rechner |
| Lautstärke **vom Rechner** setzen | funktioniert (am 2026-08-17 bei 10 % gegen 100 % gehört) |

Die ersten beiden Zeilen sind eine Eigenschaft von Bluetooth, keine
Konfigurationsfrage: Das Gerät kann nicht gleichzeitig gut klingen und
zuhören.

Die dritte und vierte Zeile sind am 2026-08-17 gemessen worden, auf zwei
**getrennten Wegen**, weil der erste allein nichts bewiesen hätte:

- **Tastencodes** (`/dev/input`): Der AIRHUG meldet sich als
  Eingabegerät („AIRHUG 01 (AVRCP)") und der Kernel führt Medientasten
  für ihn auf - gedrückt kommt aber **nichts** an, auch nicht während
  Audio läuft. In drei Durchgängen geprüft; die ersten beiden waren
  wertlos (einmal ging die Ausgabe im Puffer verloren, einmal scheiterte
  die Wiedergabe unter `sudo` an der PipeWire-Sitzung).
- **AVRCP-Lautstärke** (Senken-Lautstärke in PipeWire): Ein Lautsprecher
  kann seine Lautstärketasten auch auf diesem ganz anderen Kanal
  schicken, den ein Tastenleser prinzipiell nie sieht. Auch dort kommt
  nichts an - Stephans Beobachtung: „Die Lautstärke wird nur am Gerät
  gesteuert, ist aber nicht mit der Lautstärke von GNOME gekoppelt."

**Damit fällt die naheliegende Lösung aus**, per Tastendruck am
Lautsprecher kurz auf HFP zu schalten, zuzuhören und zurückzuschalten.

### Die Entkopplung gilt nur in EINE Richtung

**Richtigstellung vom 2026-08-17.** Hier stand zunächst, DialOS könne den
Lautsprecher überhaupt nicht regeln. Das war zu weit gegriffen und beruhte
darauf, dass ich „nicht gekoppelt" nicht nach Richtung getrennt hatte.
Nachgemessen im Hörvergleich:

- **Rechner → Gerät: funktioniert.** Bei 10 % gegen 100 % ist der
  Unterschied unüberhörbar. Ein Sprachbefehl „mach lauter" ist also
  umsetzbar.
- **Gerät → Rechner: funktioniert nicht.** Drückt jemand am AIRHUG Plus
  oder Minus, erfährt der Rechner nichts davon.

Was daraus praktisch folgt: DialOS kann die Lautstärke steuern, aber es
**weiß nicht, wo sie steht**, wenn jemand am Gerät gedreht hat. Hat der
Nutzer den AIRHUG am Rad heruntergedreht, hilft „mach lauter" nur, wenn
die Software-Lautstärke noch Spielraum hat - steht sie schon auf 100 %,
bleibt es leise, und die Ursache liegt außerhalb des Systems. Ein
Restrisiko, aber kein Ausschlusskriterium.

### Was bleibt

- **Zwei Geräte:** ein Mikrofon, das dauerhaft in HFP beim Nutzer bleibt,
  und getrennt davon der Lautsprecher in A2DP. Löst die Reichweite und
  die Qualität, kostet ein Gerät mehr zum Laden und Koppeln.
- **Anderer Lautsprecher**, dessen Tasten und Lautstärke den Rechner
  erreichen. Das ist eine Geräte-Eigenschaft, keine Bluetooth-Grenze -
  andere Freisprecheinrichtungen können beides.
- **Nur eingebautes Mikrofon** und die Auflage, dass der Laptop im selben
  Raum steht. Widerspricht dem Regelfall.

**Offen - Stephans Entscheidung** (siehe [../TODO.md](../TODO.md)). Bis
dahin bleibt es beim eingebauten Mikrofon, weil das wenigstens die
Ausgabequalität nicht beschädigt.

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
