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
| Lautstärke **vom Rechner** setzen | funktioniert (2026-08-17 zweimal geprüft, zuletzt mit dem Gerät auf 100 %) |

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
  umsetzbar. **Zweimal geprüft**, beim zweiten Mal mit dem Gerät
  ausdrücklich auf 100 % und im Wechsel leise-laut-leise-laut - der
  erste Durchgang hätte sonst daran leiden können, dass das Gerät selbst
  leise stand.
- **Gerät → Rechner: funktioniert nicht.** Drückt jemand am AIRHUG Plus
  oder Minus, erfährt der Rechner nichts davon. **Am 2026-08-17 in drei
  Bedingungen nachgeprüft**, weil eine Beobachtung dem zu widersprechen
  schien (die Senke stand plötzlich auf 70 %): Tastendruck ohne Ton,
  Start einer Wiedergabe, und Tastendruck **während** laufender
  Wiedergabe - der Wert blieb jedes Mal unverändert. Die 70 % bleiben
  unerklärt, siehe [../TODO.md](../TODO.md).

### Wie die Lautstärke wirklich übertragen wird (gemessen 2026-08-17)

Das ist wichtiger als es klingt, weil die naheliegende Annahme falsch
ist - und mich zu einer Empfehlung verleitet hat, die ich zurücknehmen
musste:

| Weg | Was passiert | Wirkt es? |
|---|---|---|
| Senken-Lautstärke (GNOME-Regler, `pactl`) | Wert geht **per AVRCP ans Gerät**, das Signal bleibt unverändert | ja, hörbar |
| Dämpfung im Signal (sox, `paplay --volume`) | Signal verlässt den Laptop korrekt gedämpft | **nein** - der AIRHUG rechnet es weg |

Nachgewiesen am Monitor der Bluetooth-Senke, also an dem, was den Laptop
verlässt: Halbe Amplitude in der Datei ergibt dort **0,071559** gegen
**0,143117**, genau Faktor 0,5000. Senke auf 100 % gegen Senke auf 30 %
dagegen **beide Male 0,143117**, auf die letzte Stelle identisch. Die
Senken-Lautstärke wird also gar nicht ins Signal gerechnet, sondern dem
Gerät befohlen. Am eingebauten Lautsprecher ist die Dämpfung im Signal
umgekehrt hörbar (im Hörvergleich bestätigt).

**Zwei Folgerungen:**

- `bluez5.enable-hw-volume = false` wäre ein Fehler, obwohl es auf dem
  Papier genau das täte, was man will (Gerät bleibt auf 100 %, OS regelt).
  DialOS würde danach auf dem Weg dämpfen, der beim AIRHUG nichts
  bewirkt - es gäbe **überhaupt keine** Lautstärkeregelung mehr.
- „Ansagen leiser als Musik" ist am AIRHUG nicht erreichbar, weil dort
  nur die Geräte-Lautstärke wirkt und die für alles gilt. Ein
  AVRCP-Befehl kostet gemessen 19-36 ms, ein kurzes Absenken während der
  Ansage wäre also bezahlbar - Entscheidung offen, siehe `TODO.md`.

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

**Entschieden am 2026-08-17 (Stephan): vorerst die dritte Variante -
Eingabe immer das eingebaute Mikrofon**, Ausgabe der
Bluetooth-Lautsprecher solange er wirklich abspielt, sonst die
eingebauten. Externe Mikrofone werden erst zum Schluss wieder
betrachtet.

Das ist ausdrücklich **keine Notlösung**, sondern löst zwei Probleme mit,
die sonst eigens zu lösen wären:

1. **Die A2DP/HFP-Zwangswahl entfällt.** Solange DialOS nie ein
   Bluetooth-Mikrofon öffnet, kann das Gerät nicht in Telefonqualität
   rutschen. Diese Falle hat bisher die Tonqualität der Videoaufnahme
   gekostet und steckt in mehreren offenen Punkten - sie ist jetzt nicht
   gelöst, sondern unberührt.
2. **Ein abschaltbares Mikrofon ist ein Risiko für die ganze
   Tonausgabe.** Hängt die Echo-Unterdrückung daran, nimmt sein Ausfall
   alles mit - am 2026-08-17 genau so passiert, Details in
   `Debian-zu-DialOS.md`, Schritt 11f. Ein eingebautes Mikrofon kann man
   nicht ausschalten.

Der Preis ist die Reichweite: Sprachsteuerung nur am Laptop. Genau
deshalb bleibt die Suche nach einem externen Mikrofon auf der Liste, nur
eben nicht als Voraussetzung für alles andere.

## Zwei Geräte statt einem (Entscheidung 2026-08-17)

Aus den Messungen weiter oben folgt: Ein einzelnes Bluetooth-Gerät kann
nicht beides. Stephans Entscheidung ist deshalb ein **Paar**:

| Aufgabe | Gerät | Weg |
|---|---|---|
| Sprachausgabe, Musik, Radio | AIRHUG 01, bleibt | Bluetooth A2DP |
| Spracheingabe | Funkmikrofon mit USB-Empfänger | USB Audio Class |

**Warum kein zweites Bluetooth-Gerät:** Das brächte die HFP-Falle zurück,
die den ganzen Vormittag des 2026-08-17 gekostet hat. Ein Funkmikrofon
mit USB-Empfänger meldet sich dagegen als gewöhnliche USB-Soundkarte -
kein Profil, kein A2DP/HFP-Konflikt, keine Kopplung, und der Lautsprecher
bleibt völlig unangetastet.

### Anforderungen an das Mikrofon

- **Kein Akku im Dauerbetrieb**, oder wenigstens Betrieb am Netzteil.
  Das ist die härteste Anforderung, und sie stammt aus der Zielgruppe:
  Ein leerer Sender macht das System **taub**, und ein blinder Nutzer
  findet die Ursache nicht - sie liegt außerhalb des Systems. Dieselbe
  Sorte Fehler wie die entkoppelte Gerätelautstärke.
- **USB Audio Class**, damit es unter Linux ohne Treiber läuft.
- Reichweite über eine Wohnung, also mindestens 15-20 m durch Wände.

### Bluetooth oder USB? Zu prüfen, nicht entschieden

**Stand 2026-08-17.** Zuerst war USB gesetzt, weil es die HFP-Falle
umgeht. Stephans Einwand hat einen Punkt aufgedeckt, der dagegensteht -
und ausgerechnet die härteste Anforderung von oben betrifft:

| | Bluetooth-Mikrofon | USB-Funkmikrofon |
|---|---|---|
| **Akkustand sichtbar** | **ja**, über BlueZ - die Start-Ansage liest ihn heute schon vor und könnte warnen | **nein**, der Empfänger ist nur eine Soundkarte |
| Störung der Musik | **Risiko**: dauerhaft offenes HFP belegt fortlaufend Funkzeit auf demselben Adapter, über den der AIRHUG spielt | keine gemeinsame Zeitplanung, weil am Bluetooth-Stack vorbei |
| Profil-Konflikt | betrifft nur das Mikrofon-Gerät selbst, nicht den Lautsprecher | gar keiner |

Der Unterschied ist also nicht „gut gegen schlecht", sondern **welchen
Fehler man lieber hätte**: ein Mikrofon, das unbemerkt leer wird, oder
Radio, das während des Zuhörens stottern könnte.

Dass A2DP bei gleichzeitig offener SCO-Verbindung einbricht, ist ein
bekanntes Problem und hängt vom Adapter ab - **das lässt sich nur am
Gerät klären, nicht durch Nachlesen.**

**Vorgehen (Stephan, 2026-08-17):** Zuerst ein **preiswertes
Bluetooth-Mikrofon zum Ausprobieren** - koppeln, Radio laufen lassen,
zuhören lassen, hinhören ob es stottert. Fällt der Test gut aus, ist es
die bessere Lösung, weil der Akkustand sichtbar bleibt. Fällt er schlecht
aus, weiß man es für 30 Euro statt für 150, und USB ist die
Rückfallebene.

**Unabhängig davon zu bauen:** Der Sprachdienst misst ohnehin laufend den
Pegel. Kommt über Minuten hinweg **gar nichts** an, obwohl die Quelle da
ist, kann er das ansagen („Ich höre nichts mehr vom Mikrofon"). Das
ersetzt keine Akkuanzeige, fängt aber genau den Ausfall ab, der den
Nutzer sonst ratlos zurückließe - und wirkt bei beiden Bauarten.

### Der USB-Weg ist auf diesem Gerät bewiesen (2026-08-17)

Die offene Frage „erscheint ein Funkmikrofon mit USB-Empfänger unter
Linux als Soundkarte?" ist beantwortet - mit Hardware, die Stephan schon
besaß: einem **TeckNet TK-HS005** Headset mit 2,4-GHz-USB-Dongle.

| | |
|---|---|
| USB-Kennung | `10d6:dd00` |
| Hersteller **laut Gerät** | „Generic" |
| Produkt laut Gerät | `TK-HS005-PHONE` |
| Marke | **TeckNet** - nur aufgedruckt, nicht im Deskriptor |
| Chipsatz | Actions Semiconductor |

Eingesteckt meldet es sich ohne Treiber und ohne Kopplung als
Soundkarte - und, entscheidend, mit einem Profil, das **Ausgabe und
Eingabe gleichzeitig** führt:

```
output:analog-stereo+input:mono-fallback   (sinks: 1, sources: 1)
```

Genau das kann Bluetooth nicht: Beim AIRHUG hat jedes A2DP-Profil
`sources: 0`, man muss zwischen gutem Klang und Mikrofon wählen. Beim
USB-Gerät gibt es diese Wahl nicht, weil sie nicht nötig ist. Und es
belegt keine Funkzeit auf dem Bluetooth-Adapter - das Risiko
„Musik stottert" entfällt beim USB-Weg vollständig.

**Was das Gerät nicht taugt:** als Referenz-Hardware. Der Hersteller
steht nirgends im Deskriptor, „Actions Semiconductor" ist nur der
Chiplieferant, und derselbe Chip im selben Gehäuse wird unter beliebig
vielen Markennamen verkauft. Ein Gerät, das man über Jahre nachkaufen
können muss, sollte identifizierbar sein. Als **Beweis, dass der Weg
funktioniert**, hat es seinen Zweck erfüllt.

### Geprüft und verworfen: Godox Cube-SC Kit2 (2026-08-17)

2,4-GHz-Funkmikrofon mit USB-C-Empfänger, rund 60-80 €. Auf Stephans
Vorschlag geprüft.

**Was dafür sprach:** Der Empfänger unterstützt ausdrücklich **UAC** und
ist für den PC-Einsatz vorgesehen - beste Voraussetzung, dass er unter
Linux ohne Treiber läuft. 300 m Reichweite, 48 kHz/24 Bit,
Rauschunterdrückung, zwei Sender im Set, deutlich günstiger als der
Lark M2.

**Warum es trotzdem ausscheidet:** Die Sender laden **ausschließlich über
Kontakte im Ladecase** - keine eigene Ladebuchse. Damit ist
Dauerbetrieb am Netzteil ausgeschlossen; nach 8-10 Stunden muss der
Sender ins Case, und das System ist so lange taub. Das ist genau die
Anforderung, die weiter oben als härteste bestimmt wurde.

Dazu: **Der Akkustand ist für DialOS unsichtbar.** Godox zeigt ihn in
einer Handy-App - die es unter Linux nicht gibt und die ein blinder
Nutzer ohnehin nicht bedienen könnte.

**Wofür es trotzdem taugt:** als **Testgerät für den USB-Weg**. Es
beantwortet für wenig Geld, ob ein 2,4-GHz-Mikrofon unter Linux als
Soundkarte erscheint und wie die Erkennung damit klappt. Nur die
Akkufrage lässt es offen - und die beantwortet der Bluetooth-Test
besser.

**Eine Sache könnte es retten**, die sich aus keiner Beschreibung ergibt:
ob der Sender **im geöffneten Case betrieben** werden kann, also dauerhaft
gedockt und geladen. Wäre das so, wäre es die gesuchte Netzteil-Lösung.
Frage an den Händler oder Fall fürs Rückgaberecht.

*(Die Laufzeitangaben widersprechen sich zwischen den Händlern: mal 8,
mal 10 Stunden je Sender; „30 Stunden" bezieht sich immer auf das
Ladecase. Am Kern ändert das nichts.)*

### Kandidaten für die USB-Rückfallebene

- **[Hollyland Lark M2](https://www.hollyland.com/product/lark-m2)**
  (~120-150 €): USB-C-Empfänger mit ausdrücklicher UAC-Unterstützung,
  10 h pro Sender, Ladecase für insgesamt 30 h, zwei Sender im Set.
  **Vor dem Kauf zu klären:** ob der Sender dauerhaft am Netzteil laufen
  kann - davon hängt ab, ob die Akku-Anforderung erfüllt ist. Linux wird
  nirgends ausdrücklich genannt; UAC-Geräte laufen dort üblicherweise
  ohne Treiber, aber „üblicherweise" ist kein Beleg.
- **[Cubilux WM-C1BK](https://www.cubilux.com/products/usb-c-wireless-lavalier-microphone)**:
  nennt Linux ausdrücklich, deutlich billiger - aber keine belastbaren
  Angaben zu Reichweite und Laufzeit gefunden.

**Geprüft und verworfen:** USB-Konferenzmikrofon an einer aktiven
USB-Verlängerung. Technisch die sauberste Lösung - kein Akku, immer an,
nichts zu laden. Aber ein Kabel quer durchs Wohnzimmer ist bei einem
blinden Nutzer eine **Stolperfalle**. Für ein Testgerät brauchbar, für
ein Kundengerät nicht.

**Prüfung nach dem Kauf**, dauert eine Stunde: einstecken,
`pactl list sources` - erscheint das Gerät, ist die halbe Miete drin.
Danach Reichweite in der Wohnung und Erkennungsqualität gegen das
eingebaute Mikrofon.

### Telefonie und Videocall: welches Gerät?

**Noch nicht zu entscheiden** - Telefonie ist nicht umgesetzt (siehe
[telefonie.md](telefonie.md)). Festgehalten als Entscheidungsvorlage,
damit die Überlegung nicht verlorengeht:

Der naheliegende Weg wäre, für ein Gespräch auf **HFP** zu schalten: Der
AIRHUG wird zum Freisprecher, Mikrofon und Wiedergabe aus einem Gerät.
Telefonqualität ist bei einem Telefonat kein Verlust.

Der bessere Weg ist vermutlich, **gar nicht umzuschalten**: Eingang das
USB-Mikrofon, Ausgang der AIRHUG in A2DP. Dann läuft das Gespräch in
**beide** Richtungen in voller Qualität statt in Telefonqualität. Zwei
weitere Gründe sprechen dafür: Das Profilwechsel-Problem entfällt
vollständig (es ist am 2026-08-17 dreimal hängengeblieben), und die
Echo-Unterdrückung ist ohnehin schon eingerichtet.

**Der Vorbehalt dazu:** Bei getrenntem Lautsprecher und Mikrofon hört der
Gesprächspartner sich selbst, wenn die Echo-Unterdrückung nicht greift -
und im Gespräch ist sie anspruchsvoller als in unserem bisherigen Fall.
Wir rechnen bisher nur die *eigene* Ansage heraus; bei einem Gespräch
läuft der Ton gleichzeitig in beide Richtungen. Die gemessenen 32 dB sind
ein gutes Zeichen, aber kein Beweis für den Gesprächsfall.

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
