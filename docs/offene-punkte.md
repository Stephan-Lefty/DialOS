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

## Sicherheit
- Wiederherstellungsweg für den USB-Sicherheits-Stick bei Verlust/Defekt:
  vorläufig als Master-Passphrase umgesetzt (zweiter LUKS-Schlüsselslot,
  wird bei jeder Installation vom Installer abgefragt) – ob das die
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

## Sprachsteuerung
- Konkrete Intent-Schicht (eigene Middleware vs. bestehendes Framework
  als Ausgangsbasis) noch nicht festgelegt.
- Wake-Word-Engine für Akku-sparendes Dauerlauschen noch nicht final
  entschieden (Vorschlag: openWakeWord).

## Telefonie
- Priorisierung WhatsApp vs. Signal als Messenger noch offen.

## Projekt/Repository
- GitHub-Repository für Stephan-OS noch nicht angelegt – lokal
  begonnen, Entscheidung öffentlich/privat und Zeitpunkt für den Push
  steht noch aus.
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
