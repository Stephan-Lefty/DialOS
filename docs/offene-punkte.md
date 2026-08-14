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
- Boot-Zeit-Tastenkombination für direkten `dialosadmin`-Zugriff (statt
  GNOME "Benutzer wechseln", siehe sicherheit-datenschutz.md, Abschnitt
  "Automatische Anmeldung"): technisch möglich (eigener früher Boot-Dienst,
  der kurz auf einen gehaltenen Tastendruck lauscht, z. B. über rohen
  `/dev/input`-Zugriff, und je nach Ergebnis per `gdbus` das Autologin-Ziel
  umbiegt), aber bewusst zurückgestellt – "Benutzer wechseln" funktioniert
  bereits zuverlässig ohne zusätzliche Boot-Software. Nur aufgreifen, falls
  sich "Benutzer wechseln" in der Praxis als zu umständlich erweist (z. B.
  Probleme beim Fernwarten per RustDesk mit dem GDM-Wechsel-Bildschirm).
  Risiko bei Umsetzung: sauberes Zeitfenster nötig, sonst könnte ein
  zufälliger Tastendruck während des normalen Kundenboots ungewollt den
  Admin-Pfad statt des normalen `nutzer`-Autologins auslösen.

## ISO-Build
- Rechtschreibprüfung (hunspell-de-de/hunspell-en-us, aspell) fehlt in
  der ISO: Das Paket `dictionaries-common`, von dem beide abhängen,
  scheitert reproduzierbar in der Docker-Chroot-Build-Umgebung
  (vermutlich fehlender D-Bus während der Paketkonfiguration). Für den
  ersten lauffähigen Build vorerst ausgelassen, muss nachgerüstet
  werden (ggf. Installation nach dem ersten Boot statt zur Build-Zeit).

## Sprachsteuerung
- Konkrete Intent-Schicht (eigene Middleware vs. bestehendes Framework
  als Ausgangsbasis) noch nicht festgelegt.
- Wake-Word-Engine für Akku-sparendes Dauerlauschen noch nicht final
  entschieden (Vorschlag: openWakeWord).

## Telefonie
- Priorisierung WhatsApp vs. Signal als Messenger noch offen.

## Projekt/Repository
- GitHub-Repository für DialOS noch nicht angelegt – lokal
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
