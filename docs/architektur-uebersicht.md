[Deutsch](architektur-uebersicht.md) | [English](architektur-uebersicht.en.md)

# Architektur-Übersicht

## Ziel

Stephan-OS ist eine auf Debian 13 (Trixie) + GNOME basierende Live-ISO für
Menschen, die einen Computer nur eingeschränkt nutzen können – insbesondere
blinde und motorisch eingeschränkte Personen. Das System soll vollständig
per Sprache bedienbar sein, inklusive der Systemwartung, und dabei gleich
einfach für eine 18-Jährige wie für einen 80-Jährigen funktionieren.

## Zielgruppe

Blinde und motorisch eingeschränkte Nutzer gleichermaßen, ohne Schwerpunkt
auf eine der beiden Gruppen. Das System muss deshalb sowohl exzellent
vorlesen (Bildschirminhalte, Benachrichtigungen, Rückfragen) als auch
vollständig ohne Tastatur/Maus bedienbar sein.

## Kernfunktionen

- Radio hören, Musik hören
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

## Software-Stack (Diskussionsstand, noch nicht umgesetzt)

| Bereich | Wahl | Begründung |
|---|---|---|
| Distribution | Debian 13 + GNOME, live-build | Beste Orca/AT-SPI-Integration, ausgereiftes ISO-Tooling, Hardware-Support |
| Spracherkennung (STT) | Vosk (deutsches Modell), offline | Datenschutz bei vulnerabler Zielgruppe, funktioniert auch unterwegs ohne Internet |
| Sprachausgabe (TTS) | Piper oder RHVoice | Natürlicher als espeak-ng, als Orca-Backend nutzbar |
| Intent-Erkennung | flexible/LLM-gestützte Zuordnung statt starrer Grammatik | Muss unterschiedliche Formulierungen derselben Absicht verstehen (18- bis 80-Jährige) |
| Low-Level-Desktopsteuerung | Numen (Wayland-nativ, Vosk-basiert) | Maus/Fenster-Steuerung für motorisch eingeschränkte Nutzer |
| Screenreader | Orca | Standard-GNOME-Screenreader, gekoppelt an Piper/RHVoice |
| Mail/Kalender/Kontakte | Thunderbird | Eine App für alle drei Funktionen, gute Orca-Unterstützung |
| Radio | Shortwave | GNOME-Internetradio-App |
| Musik | Rhythmbox/GNOME Music | — |
| Textverarbeitung | LibreOffice Writer | — |
| Browser | Firefox ESR | Für Suchfragen und ARD/ZDF-Mediatheken (kein nativer Linux-Client) |
| Fernwartung | RustDesk | Open Source, selbst hostbar, siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md) |
| Videocall | Jitsi Meet (Browser) | Kein Konto nötig, WebRTC |

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
