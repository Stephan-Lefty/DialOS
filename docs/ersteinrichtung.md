[Deutsch](ersteinrichtung.md) | [English](ersteinrichtung.en.md)

# Ersteinrichtung & Rollout

## Zwei-Phasen-Provisionierung

**Präzisierung seit 2026-08-16 (Weg A):** Es gibt kein "Golden Image",
das vervielfältigt wird. Jedes Gerät wird einzeln im Büro aufgesetzt -
leere Platte, jeweils aktuelle Debian-13/GNOME-ISO von debian.org, danach
die drei DialOS-Skripte (siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md)). Ein Kunde bekommt nie einen
Installer zu sehen; Calamares und `dialos-install` sind deshalb entfallen.

1. **Büro-Setup (Stephan)**: Das Gerät wird komplett eingerichtet,
   inklusive Testlauf. Alles, was sich datenschutz- oder
   sicherheitstechnisch vorab erledigen lässt (siehe unten), passiert
   hier – nicht vor Ort.
2. **Versand**: Laptop und Sicherheits-Stick werden getrennt verschickt
   (siehe [sicherheit-datenschutz.md](sicherheit-datenschutz.md)).
3. **Vor-Ort-Einrichtung beim Nutzer**: Laptop ans Stromnetz, Stick
   anschließen, letzte Einstellungen vornehmen.

## Vor-Ort-Einrichtung ist zwingend rein per Sprache

Es gibt keine Ausnahme davon: Alle Berührungspunkte vor Ort müssen
entweder rein physisch (Stick einstecken, Strom anschließen) oder reiner
Sprachdialog sein – nichts darf Sehen, Tippen oder Lesen erfordern.
Konsequenz: Auch Dinge wie eine SIM-Aktivierung gehören ins Büro-Setup,
nicht vor Ort.

## Vollständig sprachgeführter Ersteinrichtungs-Assistent

Läuft beim allerersten Systemstart automatisch – unabhängig vom
"Hilfe rufen"-Befehl für RustDesk – und muss auch funktionieren, wenn der
Nutzer komplett allein ist. Neue Softwarekomponente (State-Machine-Dialog
auf Vosk+Piper-Basis, getriggert durch eine Erstlauf-Markerdatei).

**Stand 2026-08-16: nicht umgesetzt.** Was es davon schon gibt, ist die
Start-Ansage (`dialos-start-ansage.py`) samt der gesprochenen
Lautstärke-Frage - der erste echte Sprachdialog des Systems und damit
die Vorlage für diesen Assistenten (Ansage → Frage → Antwort per Vosk →
Ergebnis merken). Der Assistent selbst, mit Namenserfassung und
Stimmenauswahl, existiert noch nicht.

Vor Ort per Sprache erfragt werden nur:
- **Name** des Nutzers, mit Rückbestätigung ("Ich habe verstanden: Anna
  Schmidt. Stimmt das?") und Korrekturmöglichkeit.
- **Begrüßungsstimme**: Auswahl aus **zwei** Stimmen per Hörprobe -
  **Michael** (`de_DE-thorsten-high`) und **Anna**
  (`de_DE-kerstin-low`). Später jederzeit änderbar, nicht nur bei der
  Ersteinrichtung.

  **Zwei statt vier, und das ist eine Verschärfung, keine Sparmaßnahme**
  (Stephan, 2026-08-20: „lieber 2 Stimmen optimiert als 8 Stimmen na es
  geht gerade so"). Der Grund liegt in dem, was am selben Tag gemessen
  wurde:

  - **Jede Stimme braucht ihre eigene Einstellung.** Das Sprechtempo ist
    nicht übertragbar: derselbe Satz braucht bei Thorsten 7,75 s mit
    Tempo 0,88, bei Kerstin **8,99 s** mit demselben Wert. Und die
    Aussprache-Regeln („Tas tatur", „Ei Di", „Dial OS") sind auf Thorsten
    abgestimmt - ob Anna sie braucht, ist noch offen. Acht Stimmen hießen
    achtmal diese Arbeit, und ohne sie klingt jede einzelne schlechter als
    nötig.
  - **Für einen blinden Nutzer ist die Stimme nicht ein Merkmal, sondern
    die ganze Oberfläche.** Eine mittelmäßige Stimme ist deshalb kein
    Schönheitsfehler, den man mit Auswahl ausgleicht - eine große Auswahl
    mittelmäßiger Stimmen ist schlechter als zwei gute.
  - **Zwei decken die eigentliche Präferenz ab:** männlich oder weiblich.
    Alles darüber ist Geschmack, den man später ergänzen kann, wenn er
    verlangt wird.

  **Korrektur einer früheren Annahme:** Hier stand „jeweils höchste
  verfügbare Sprachqualität". Das ist bei den weiblichen Stimmen nicht
  erreichbar - Piper bietet für Deutsch nur `eva_k-x_low`, `kerstin-low`
  und `ramona-low`, alle mit **16 000 Hz** gegen Thorstens 22 050 Hz.
  Anna klingt hörbar rauher als Michael, und das ist keine
  Einstellungssache, sondern der Stand der verfügbaren Modelle.
- Ggf. Bestätigung vorbereiteter Konten (siehe Datenschutz-Varianten
  unten) – reine Ja/Nein-Antwort, kein Diktat.

**Wichtige Design-Einschränkung**: E-Mail-Adresse/Passwort werden nie
per Sprache diktiert – Spracherkennung ist bei Zeichenketten
fehleranfällig, und ein Passwort laut auszusprechen ist ein
Sicherheitsrisiko für sich.

## Datenschutz-Varianten für die Konto-Einrichtung

Nicht jeder Nutzer möchte seine Zugangsdaten (E-Mail, Kontakte) einfach
zur Verfügung stellen. Zwei Varianten:

- **Variante 1 – "Alle Daten liegen vor"**: Der Nutzer teilt Stephan
  vorab (z. B. telefonisch) die nötigen Zugangsdaten mit. Das Büro
  richtet E-Mail-Konto und CardDAV-Kontaktabgleich komplett fertig ein.
  Vor Ort bleibt nur noch Name + Begrüßungsstimme per Sprache.
- **Variante 2 – "Nutzer gibt alles selbst ein" (Datenschutz gewahrt)**:
  Nichts wird vorab weitergegeben. Der Sprachassistent führt vor Ort
  durch die komplette Einrichtung. Für Konten mit Passwortschutz wird auf
  den **OAuth-Device-Flow** zurückgegriffen (wie bei Smart-TV-Logins):
  Das System liest einen kurzen Code und eine kurze URL vor, der Nutzer
  bestätigt das auf seinem eigenen, bereits vertrauten Smartphone – das
  Passwort wird nie laut ausgesprochen, nie getippt, und Stephan bekommt
  es zu keinem Zeitpunkt zu sehen. Google unterstützt das nativ; bei
  iCloud eingeschränkter (ggf. App-spezifisches Passwort nötig, das der
  Nutzer selbst erzeugt).

## Kontaktdaten: laufende Synchronisation

Kontakte sollen **laufend** synchronisiert werden, nicht nur einmalig
importiert. Umsetzung: CardDAV-Verknüpfung einmalig im Büro einrichten
(sofern Google-/iCloud-Zugangsdaten vorab vorliegen), läuft danach
dauerhaft automatisch im Hintergrund – neue Kontakte auf dem Handy des
Nutzers erscheinen automatisch im Thunderbird-Adressbuch, ohne weitere
Aktion. Liegen die Zugangsdaten beim Verpacken noch nicht vor, kann die
Verknüpfung nachträglich per RustDesk-Fernwartung nachgeholt werden,
sobald der Nutzer einmal "Hilfe rufen" freigegeben hat. Als
plattformunabhängiger Fallback (falls kein Live-Sync gewünscht/möglich)
dient ein einmaliger vCard(.vcf)-Export/Import.

## Offene Punkte

- Wer letztlich Variante 1 oder 2 pro Nutzer entscheidet (Kontakt vorab
  mit Stephan) ist ein organisatorischer, kein technischer Punkt.
