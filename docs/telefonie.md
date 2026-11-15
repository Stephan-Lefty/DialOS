[Deutsch](telefonie.md) | [English](telefonie.en.md)

# Telefonie & Videocall

## Ziel

Telefonie (Festnetz-Ersatz + Handy) und Videocall sollen vollständig per
Sprachsteuerung nutzbar sein.

**Stand 2026-08-16: nichts davon ist umgesetzt.** Dieses Dokument
beschreibt durchgehend die Zielarchitektur, nicht den Ist-Zustand. Weder
ModemManager noch GNOME Calls stehen in der Paketliste, und das Testgerät
(ThinkPad T490) hat kein WWAN-Modul verbaut - praktische SIM-Tests sind
deshalb bisher gar nicht möglich (siehe
[hardware.md](hardware.md)).

## Auslieferungsziel: eingebaute SIM

Die eigentliche Standard-Konfiguration bei Auslieferung ist ein Laptop mit
**eingebauter, aktivierter SIM-Karte** (WWAN-Modul mit Sprachunterstützung,
siehe [hardware.md](hardware.md)). Eine SIM übernimmt sowohl Festnetz- als
auch Handy-Telefonie einheitlich, statt getrennter Lösungen wie
Fritzbox-SIP-Trunk und Handy-Kopplung zu pflegen – das war ursprünglich
angedacht, wurde aber zugunsten der SIM-Lösung verworfen, weil sie nicht
vom Heimnetz/Router des Nutzers abhängt und daher auch unterwegs
funktioniert. Bestehende Rufnummern des Nutzers können bei Bedarf per
Rufumleitung auf die neue SIM-Nummer gelegt werden, damit er unter der
gewohnten Nummer erreichbar bleibt.

Software: ModemManager + GNOME Calls als Softphone-Oberfläche.

## Alternative: Handy-Anbindung

Das System muss auch ohne eingebaute SIM funktionieren – der Nutzer kann
alternativ sein eigenes Handy anschließen. Das ist die flexible
Alternative/der Fallback, **nicht** der Regelfall.

- **Verbindungsweg**: USB-Kabel als primäre Methode (zuverlässiger als
  Bluetooth, lädt das Handy nebenbei mit, passt zum Prinzip "einmal
  anschließen und vergessen"). Bluetooth nur als Fallback, falls ein Kabel
  unpraktisch ist.
- **Internet**: USB-Tethering, funktioniert unabhängig von der
  Handy-Plattform.
- **Telefonie**: bei Android zusätzlich über GSConnect/KDE Connect möglich
  (Anrufe annehmen/starten vom Laptop aus). Bei iPhone wegen
  Apple-Beschränkungen nicht möglich – dort nur Internet-Tethering.
- **Fallback-Logik (Variante B, pro Funktion getrennt)**: Das Handy
  übernimmt, was es kann (Tethering immer, Telefonie nur bei Android).
  Fehlende Fähigkeiten (z. B. Telefonie bei iPhone) fallen automatisch auf
  die eingebaute SIM zurück, falls vorhanden. Keine manuelle Konfiguration
  nötig – passt zum Prinzip "gleich einfach für 18 wie 80".

### Zwingende Randbedingung

Der Nutzer bedient das angeschlossene Handy **nie selbst** – viele ältere
Nutzer kommen mit der Handy-Bedienung nicht zurecht. Das Handy wird
einmalig bei der Einrichtung angeschlossen/gekoppelt und bleibt danach
unangetastet (z. B. in einer Schublade). Jegliche Interaktion (anrufen,
rangehen, auflegen) läuft ausschließlich über die Sprachsteuerung am
Laptop.

## Geprüft: Telefonie über ein externes Modem (Stick)

**Stephans Frage vom 2026-11-15**, aufgekommen beim Konfigurieren des
ersten Referenzgeräts: Lässt sich die Telefonie von der eingebauten SIM
lösen und über ein externes Gerät erledigen? Das wäre unabhängig vom
Laptop-Modell, bei einem Defekt tauschbar und würde den Gerätekauf
entlasten.

**Technisch ja, aber nur mit bestimmten Modulen.** Ein Modem muss dafür
zweierlei können, und das ist nicht dasselbe:

1. **Sprachanrufe** – viele LTE-Module sind reine Datenmodems.
2. **Audio über USB** – das Gespräch muss auch beim Rechner ankommen.
   Etliche sprachfähige Module führen die Audiosignale nur über
   PCM-Pins heraus, die bei einem USB-Gehäuse nirgends angeschlossen
   sind.

Belegt funktioniert das mit dem **Quectel EC25-E**: Er meldet sich als
USB-Audiogerät (USB Audio Class) an, die Anrufsteuerung läuft über
AT-Befehle, und ModemManager mit GNOME Calls bedient ihn – also genau die
Architektur, die oben schon steht.

**Drei Einschränkungen, die bleiben:**

- **8 kHz, fest verdrahtet.** Die USB-Audio-Schnittstelle des EC25 ist in
  der Firmware auf 8 kHz festgelegt – Telefonqualität wie im Festnetz.
  Für Telefonie reicht das; HD-Voice ist damit ausgeschlossen.
- **Es gibt keinen fertigen Stick.** Den EC25 gibt es als M.2- oder
  Mini-PCIe-Modul; für USB braucht es ein Gehäuse, und das sind
  Bastlerprodukte. Bei einem Gerät, das fertig eingerichtet ausgeliefert
  wird, ist das ein weiteres Teil, das abfallen oder verlorengehen kann.
- **Die Antenne ist winzig.** Ein eingebautes WWAN-Modul nutzt die
  Antennen im Displayrahmen und hat spürbar besseren Empfang als ein
  Stick am USB-Anschluss.

## Vierte Möglichkeit: SIP über das Internet

Beim Prüfen der Stick-Frage fiel auf, dass eine Option bisher fehlte.
Verworfen wurde oben der **Fritzbox-SIP-Trunk**, und zwar weil er am
Router des Nutzers hängt. Ein SIP-Konto bei einem Anbieter hängt dagegen
nur am Internet – und das hat das Gerät ohnehin.

Das hätte Vorteile, die zum Projekt passen:

- **Kein sprachfähiges Modem nötig.** Ein reines Datenmodul genügt – auch
  das, was Lenovo im L14 standardmäßig verbaut (siehe
  [hardware.md](hardware.md)).
- **Eine Festnetznummer ist möglich**, samt Rufnummernmitnahme. Für
  jemanden, der seit Jahrzehnten dieselbe Nummer hat, ist das mehr wert
  als jede technische Eleganz.
- **Linphone lässt sich von außen steuern** – das ist das
  Auswahlkriterium aus [anwendungen.md](anwendungen.md).
- Keine zusätzliche Hardware, keine Modulfrage beim Gerätekauf.

## Was vor der Technik zu entscheiden ist: Notrufe

**Diese Frage entscheidet mit, ob Mobilfunk Pflicht ist oder Komfort** –
und sie ist bei dieser Zielgruppe keine Randnotiz.

Über Mobilfunk erreicht man 112 auch ohne Guthaben, ohne Vertrag und in
jedem erreichbaren Netz; der Standort wird mitgeliefert. Über VoIP ist
beides schwieriger: Die Standortübermittlung funktioniert anders, und bei
Internetausfall geht gar nichts.

Wer das Gerät benutzt, kann im Notfall nicht ersatzweise zum Handy
greifen und meist auch nicht aus dem Fenster rufen. Solange diese Frage
offen ist, bleibt die eingebaute SIM das Auslieferungsziel – SIP ist dann
eine Ergänzung für den Alltag, kein Ersatz.

**Empfehlung für den Gerätekauf (2026-11-15):** Die Telefonie-Entscheidung
vom Kauf trennen. Ein Datenmodul reicht fürs Erste, der M.2-Steckplatz
bleibt, und ein sprachfähiges Modul lässt sich später nachrüsten. SIP und
die Handy-Anbindung lassen sich in der Zwischenzeit ohne neue Hardware
ausprobieren.

## Videocall

Jitsi Meet im Browser als einfachste, kontofreie Lösung – Open Source,
direkt per Sprachbefehl mit einem Link startbar.

## Messenger (Textnachrichten, zusätzlich zur echten Telefonie)

Dient nur zum Schreiben/Empfangen von Nachrichten – Anrufe laufen immer
über SIM/Handy wie oben, nicht über den Messenger.

**Priorität: WhatsApp**, trotz der sonstigen Datenschutz-Linie des
Projekts – ausschlaggebend ist die Verbreitung: Familie/Freunde der
Nutzer haben mit deutlich höherer Wahrscheinlichkeit schon WhatsApp als
Signal, und Erreichbarkeit bestehender Kontakte zählt hier mehr als bei
den übrigen (rein internen) Systementscheidungen. Kein offizieller
WhatsApp-Linux-Client verfügbar, Umsetzung über WhatsApp Web im Browser
oder einen inoffiziellen Wrapper.

**Signal** (offizielle Linux-App, Sprach-/Videoanrufe, echte
Verschlüsselung) bleibt als datenschutzfreundlichere Option zusätzlich
verfügbar, aber nicht priorisiert.
