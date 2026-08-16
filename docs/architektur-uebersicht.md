[Deutsch](architektur-uebersicht.md) | [English](architektur-uebersicht.en.md)

# Architektur-Übersicht

## Ziel

DialOS ist ein auf Debian 13 (Trixie) + GNOME 48 basierendes System für
Menschen, die einen Computer nur eingeschränkt nutzen können – insbesondere
blinde und motorisch eingeschränkte Personen. Es wird nicht als Live-ISO
verteilt, sondern im Büro auf jedem Gerät aus einer regulären
Debian-Installation aufgebaut (siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md)); eine ISO gibt es nur noch
als Sicherungs-Abbild. Das System soll vollständig
per Sprache bedienbar sein, inklusive der Systemwartung, und dabei gleich
einfach für eine 18-Jährige wie für einen 80-Jährigen funktionieren.

## Zielgruppe

Blinde und motorisch eingeschränkte Nutzer gleichermaßen, ohne Schwerpunkt
auf eine der beiden Gruppen. Das System muss deshalb sowohl exzellent
vorlesen (Bildschirminhalte, Benachrichtigungen, Rückfragen) als auch
vollständig ohne Tastatur/Maus bedienbar sein.

## Kernfunktionen

- Radio hören, Musik hören, Podcasts hören
- Briefe/Texte schreiben
- Browser für Suchfragen
- Mediatheken (ARD, ZDF) nutzen
- E-Mails schreiben/verschicken
- Terminkalender mit Erinnerungen
- Zentrale, laufend synchronisierte Kontaktdatenbank
- Telefonie (Festnetz-Ersatz + Handy) und Videocall
- Optional: WhatsApp/Signal als Messenger
- Text-to-Speech (Bildschirm vorlesen)
- Systemwartung vollständig per Sprachsteuerung
- Fernwartung für Support durch Angehörige/Techniker (RustDesk)

Details siehe [telefonie.md](telefonie.md), [sicherheit-datenschutz.md](sicherheit-datenschutz.md),
[sprachsteuerung.md](sprachsteuerung.md), [ersteinrichtung.md](ersteinrichtung.md).

## Software-Stack (Stand 2026-08-16)

Die Spalte "Stand" trennt Entschiedenes von Eingebautem: **installiert**
heißt, das Paket kommt aus der DialOS-Paketliste; **im Einsatz** heißt,
es wird von DialOS aktiv angesteuert; **geplant** heißt, entschieden,
aber noch nichts davon im System.

| Bereich | Wahl | Begründung | Stand |
|---|---|---|---|
| Distribution | Debian 13 + GNOME 48 | Beste Orca/AT-SPI-Integration, Hardware-Support | im Einsatz |
| Spracherkennung (STT) | Vosk 0.3.45 (deutsche Modelle groß + klein), offline | Datenschutz bei vulnerabler Zielgruppe, funktioniert auch unterwegs ohne Internet | installiert, erste produktive Nutzung: Lautstärke-Abfrage bei der Start-Ansage |
| Sprachausgabe (TTS) | Piper (RHVoice verworfen) | Natürlicher als espeak-ng, als Orca-Backend nutzbar | im Einsatz, über ein speech-dispatcher-Generic-Modul |
| Intent-Erkennung | [hassil](https://github.com/OHF-Voice/hassil) (Entscheidung 2026-08-13, statt Rhasspy) | Muss unterschiedliche Formulierungen derselben Absicht verstehen (18- bis 80-Jährige) | installiert, aber noch keine Befehlsgrammatik hinterlegt |
| Low-Level-Desktopsteuerung | Numen (Wayland-nativ, Vosk-basiert) | Maus/Fenster-Steuerung für motorisch eingeschränkte Nutzer | geplant, nicht installiert |
| Screenreader | Orca | Standard-GNOME-Screenreader | installiert, Kopplung an Piper noch offen |
| Mail/Kalender/Kontakte | Thunderbird | Eine App für alle drei Funktionen, gute Orca-Unterstützung | installiert, als Standard für `mailto:`/`text/calendar` gesetzt |
| Radio | Shortwave | GNOME-Internetradio-App | installiert |
| Musik | Rhythmbox/GNOME Music | — | installiert |
| Podcasts | GNOME Podcasts | — | installiert |
| Textverarbeitung | LibreOffice Writer | — | installiert |
| Browser | Firefox ESR | Für Suchfragen und ARD/ZDF-Mediatheken (kein nativer Linux-Client) | installiert, Startseite per Enterprise-Policy gesetzt |
| Fernwartung | RustDesk | Open Source, selbst hostbar, siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md) | installiert, Autostart bewusst abgeschaltet |
| Videocall | Jitsi Meet (Browser) | Kein Konto nötig, WebRTC | geplant |
| Telefonie | ModemManager + GNOME Calls | siehe [telefonie.md](telefonie.md) | geplant, nicht installiert (kein WWAN-Modul im Testgerät) |

## Design-Prinzipien

- **Offline-first**: Spracherkennung und -ausgabe laufen lokal, keine
  Cloud-Abhängigkeit – wichtig für Datenschutz bei einer vulnerablen
  Zielgruppe und für Nutzung unterwegs ohne verlässliches Internet.
- **Sicherheit vor Bequemlichkeit**: Sicherheitskritische Aktionen
  (Systemwartung, Freigabe der Fernwartung) laufen immer über eine
  explizite Ja/Nein-Rückfrage, unabhängig davon, wie der Sprachbefehl
  erkannt wurde.
- **Kein Sehen/Tippen/Lesen nötig**: Weder bei der täglichen Nutzung noch
  bei der Ersteinrichtung vor Ort darf etwas vorausgesetzt werden, das
  Sehen, Tippen oder Lesen erfordert.
- **Generationsübergreifend einfach**: Keine auswendig zu lernenden
  Befehlswörter, geduldige und nachfragende statt abbrechende
  Sprachdialoge, keine Fachbegriffe.
