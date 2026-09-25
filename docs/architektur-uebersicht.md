[Deutsch](architektur-uebersicht.md) | [English](architektur-uebersicht.en.md)

# Architektur-Übersicht

## Ziel

DialOS ist ein auf Debian 13 (Trixie) + GNOME 48 basierendes System für
Menschen, die einen Computer nur eingeschränkt nutzen können – insbesondere
blinde und motorisch eingeschränkte Personen. Es wird nicht als Live-ISO
verteilt, sondern im Büro auf jedem Gerät aus einer regulären
Debian-Installation aufgebaut (siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), maßgebliche Anleitung seit
2026-09-25: [installationsanleitung.md](installationsanleitung.md)). Eine ISO
gibt es nicht mehr, auch nicht als Sicherung: Ein fertiges Gerät wird als
Rescuezilla-Abbild gesichert. (Bis 2026-09-25 stand hier „eine ISO gibt es nur
noch als Sicherungs-Abbild" - das war seit dem Wechsel auf Rescuezilla am
2026-08-16 überholt.) Das System soll vollständig
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

## Software-Stack (Stand 2026-09-25)

Die Spalte "Stand" trennt Entschiedenes von Eingebautem: **installiert**
heißt, das Paket kommt aus der DialOS-Paketliste; **im Einsatz** heißt,
es wird von DialOS aktiv angesteuert; **geplant** heißt, entschieden,
aber noch nichts davon im System.

Die Tabelle ersetzt die Fassung vom 2026-08-16. Die alte steht in der
Git-Historie dieser Datei; sie war der Stand, bevor der erste Sprachbefehl
lief (hassil „noch keine Befehlsgrammatik", Vosk nur für die
Lautstärke-Frage). Zeilen, die seitdem niemand neu geprüft hat, sind als
solche markiert.

| Bereich | Wahl | Begründung | Stand |
|---|---|---|---|
| Distribution | Debian 13 + GNOME 48 | Beste Orca/AT-SPI-Integration, Hardware-Support; kein Sprung auf Debian 14 (entschieden 2026-09-18, siehe [offene-punkte.md](offene-punkte.md)) | im Einsatz |
| Befehlserkennung | Vosk 0.3.45, kleines deutsches Modell, **eingeschränkte Grammatik** (rund 64 Sätze) | Offline wegen Datenschutz; frei erkannt macht das Modell aus „gnome" zuverlässig „genug" - mit der Satzliste liegt es wörtlich richtig | im Einsatz, für alle Befehle und den Einkaufszettel |
| Satzvorlagen → Grammatik | [hassil](https://github.com/OHF-Voice/hassil) (Entscheidung 2026-08-13, statt Rhasspy) | Unterschiedliche Formulierungen derselben Absicht (18- bis 80-Jährige) aus einer Vorlage | im Einsatz, baut die Befehlsgrammatik |
| Freies Diktat (Brief, Notizen) | Parakeet TDT 0.6B v3 (int8) über sherpa-onnx, Modell unter `/usr/local/share/dialos-parakeet` | Prüfstand 2026-09-15: 2,8 % Wortfehler und alle Satzzeichen richtig, Vosk 12,7 % ohne Punkte | im Einsatz seit 2026-09-16 |
| Schreibhilfe | LanguageTool (lokal, Java) | Rechtschreibung und Grammatik im Diktat, offline | im Einsatz |
| Sprachausgabe (TTS) | Piper (RHVoice verworfen), Stimmen Anna (`de_DE-kerstin-low`, Auslieferung) und Michael (`de_DE-thorsten-high`) | Natürlicher als espeak-ng | im Einsatz, über ein speech-dispatcher-Generic-Modul |
| Audio | PipeWire mit Echo-Unterdrückung (`module-echo-cancel`, WebRTC), Quelle `dialos_mikrofon_ohne_echo` | Die Erkennung soll die eigene Ansage nicht mithören (rund 32 dB Dämpfung gemessen) | im Einsatz; die Sprachdienste wählen die Echo-Quelle selbst, Standard-Mikrofon für andere Programme bleibt bewusst das rohe (siehe [hardware.md](hardware.md)) |
| Mail/Kalender/Kontakte | Thunderbird + **DialOS-Brücke** (MailExtension `bruecke@dialos.org`, Native Messaging, per `policies.json` in jedem Profil) | Thunderbird legt selbst ab und sendet; DialOS hat keinen eigenen IMAP/SMTP-Zugang und braucht das Mailpasswort nicht (siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md)) | im Einsatz: Entwürfe, Senden, Kontakte; Mailkonto über die Maske der persönlichen Daten |
| Brief als PDF | eigener Erzeuger über cairo/Pango | Briefbogen nach DIN 5008, Fensterumschlag | im Einsatz |
| Low-Level-Desktopsteuerung | Numen (Wayland-nativ, Vosk-basiert) | Maus/Fenster-Steuerung für motorisch eingeschränkte Nutzer | geplant, nicht installiert (Stand 2026-08-16, nicht neu geprüft) |
| Screenreader | Orca | Standard-GNOME-Screenreader | installiert, Kopplung an Piper noch offen (Stand 2026-08-16, nicht neu geprüft) |
| Radio | heute Shortwave, künftig Rhythmbox | Shortwave ist von außen nicht steuerbar, siehe [anwendungen.md](anwendungen.md) | installiert, „Radio öffnen" öffnet Shortwave; Wechsel entschieden 2026-09-25, nicht gebaut |
| Musik, Podcasts, Hörbücher | Rhythmbox (ein Player für alles) | GNOME Music und GNOME Podcasts entfernt `dialos-aufraeumen.sh`, siehe [anwendungen.md](anwendungen.md) | installiert |
| Textverarbeitung | LibreOffice Writer | — | installiert |
| Browser | Firefox ESR | Für Suchfragen und ARD/ZDF-Mediatheken (kein nativer Linux-Client) | installiert, Startseite per Enterprise-Policy gesetzt |
| Fernwartung | RustDesk 1.4.9 (`.deb` von GitHub) | Open Source, selbst hostbar, siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md) | Paket installiert, Dienst aus; der Sprachbefehl „Hilfe rufen" ist gebaut, aber bewusst zurückgestellt (nicht in der Befehlsgrammatik) |
| Videocall | Jitsi Meet (Browser) | Kein Konto nötig, WebRTC | geplant |
| Telefonie | ModemManager + GNOME Calls | siehe [telefonie.md](telefonie.md) | geplant, nicht installiert (kein WWAN-Modul im Testgerät) |
| Einrichtung | Claude-Desktop-App (Anthropic, proprietär, aus deren apt-Quelle) | Hilft beim Aufbau und bei der Entwicklung | bisher nur auf dem Entwicklungsgerät; **ob sie auf Kundengeräten bleibt, ist offen** (siehe [lizenzen.md](lizenzen.md)) |

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
