# Telefonie & Videocall

## Ziel

Telefonie (Festnetz-Ersatz + Handy) und Videocall sollen vollständig per
Sprachsteuerung nutzbar sein.

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

## Videocall

Jitsi Meet im Browser als einfachste, kontofreie Lösung – Open Source,
direkt per Sprachbefehl mit einem Link startbar.

## Messenger (optional)

Kein offizieller WhatsApp-Linux-Client verfügbar, nur WhatsApp Web im
Browser oder inoffizielle Wrapper. Da es hier um Erreichbarkeit
bestehender Kontakte geht, bleibt WhatsApp trotz der sonstigen
Datenschutz-Linie des Projekts eine sinnvolle Option; als
datenschutzfreundlichere Alternative kommt **Signal** (offizielle
Linux-App, Sprach-/Videoanrufe) parallel in Frage. Priorisierung noch offen.
