[Deutsch](ersteinrichtung.md) | [English](ersteinrichtung.en.md)

# Ersteinrichtung & Rollout

## Zwei-Phasen-Provisionierung

**Präzisierung seit 2026-08-16 (Weg A):** Es gibt kein "Golden Image",
das vervielfältigt wird. Jedes Gerät wird einzeln im Büro aufgesetzt -
leere Platte, jeweils aktuelle Debian-13/GNOME-ISO von debian.org, danach
die drei DialOS-Skripte (siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md)). Ein Kunde bekommt nie einen
Installer zu sehen; Calamares und `dialos-install` sind deshalb entfallen.

**Stand 2026-09-25: Maßgeblich ist
[installationsanleitung.md](installationsanleitung.md)** (als PDF auf der
externen Platte neben dem Repository, damit sie auch dann greifbar ist, wenn
das Gerät gerade leer ist); das vollständige Rezept mit allen Begründungen
bleibt [Debian-zu-DialOS.md](Debian-zu-DialOS.md). Der Weg in Kurzform:
Debian 13 mit GNOME installieren, Konto genau `dialosadmin`, das Grundsystem
aktualisieren, die Claude-App aus Anthropics apt-Quelle einrichten (nur für
die Einrichtung, siehe [lizenzen.md](lizenzen.md)), dann
`dialos-full-office-setup.sh`, `dialos-setup-home-partition.sh` und
`dialos-buero-setup-abschliessen.sh`, danach `dialos-aufraeumen.sh` und
`dialos-menue-pro-konto.sh` (Anleitung Teil 4.4/4.5). „Die drei
DialOS-Skripte" oben ist damit überholt: Es sind drei Aufbau-Skripte plus
zwei zum Aufräumen, die bewusst getrennt bleiben, weil das Entfernen von
Paketen eine Handlung mit Blick auf die Liste bleiben soll. Eine ISO gibt es
nicht mehr, auch keine Referenz-ISO für beliebige Laptops; gesichert wird ein
fertiges Gerät als Rescuezilla-Abbild.

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

  **Stand 2026-09-25:** **Anna** (`de_DE-kerstin-low`, Tempo **0,95**) ist
  die Auslieferungsstimme, **Michael** (`de_DE-thorsten-high`, Tempo
  **0,88**) die zweite. Umgeschaltet wird mit
  `dialos-stimme.py setzen kerstin` bzw. `… setzen thorsten`, im Konto
  `nutzer` per Sprache, im Admin-Konto zusätzlich mit `Strg`+`Alt`+`S`. Anna
  installiert das Aufbau-Skript seit 2026-09-25 selbst (Schritt 16e) - beim
  Neuaufbau an dem Tag fehlte sie, weil der Doku-Schritt nie im Skript
  stand. Der Auswahldialog per Hörprobe bei der Ersteinrichtung ist
  weiterhin nicht gebaut (siehe unten).

  **Zwei statt vier, und das ist eine Verschärfung, keine Sparmaßnahme**
  (Stephan, 2026-08-20: „lieber 2 Stimmen optimiert als 8 Stimmen na es
  geht gerade so"). Der Grund liegt in dem, was am selben Tag gemessen
  wurde:

  - **Jede Stimme braucht ihre eigene Einstellung.** Das Sprechtempo ist
    nicht übertragbar: derselbe Satz braucht bei Thorsten 7,75 s mit
    Tempo 0,88, bei Kerstin 8,99 s mit demselben Wert (Messung vom
    2026-08-20). *(Dieser Satz war beim Berichtigen am 2026-08-22 halb
    überschrieben worden und stand seitdem als Satzbruch da; am 2026-09-25
    aus der Git-Historie wiederhergestellt.)* **Diese Zahlen waren falsch**
    (berichtigt am 2026-08-22): Sie stammen aus
    einem Erzeuger, der Kerstins 16-kHz-Rohdaten als 22050 Hz deklarierte -
    jede Kerstin-Probe lief damit 38 % zu schnell. Richtig gemessen braucht
    derselbe Satz bei Michael mit 0,88 rund 6,15 s und bei Anna mit 1,00 rund
    7,04 s; Anna ist also **14 % langsamer**, nicht gleichauf. Seit dem
    2026-08-22 steht Anna auf **0,95** - von Stephan aus korrekt erzeugten
    Proben gewählt. Und die
    Aussprache-Regeln („Tas tatur", „Ei Di", „Dial OS") sind auf Thorsten
    abgestimmt - ob Anna sie braucht, ist noch offen. **Überholt, entschieden
    am 2026-08-24 und 2026-09-14:** Anna sagt „Dial O S", Michael bleibt bei
    „Dial OS" (die Regel gilt je Stimme); „Tas tatur" und „Ei Di" gelten für
    beide Stimmen - von Stephan im echten Satz angehört. Genau diese
    Einzelarbeit ist der Punkt: Acht Stimmen hießen
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
  **Seit 2026-09-25 wird das Mailkonto über die Maske der persönlichen
  Daten angelegt** (`dialos-persoenliche-daten-maske.py`, die
  `dialos-mailkonto.py` aufruft; für das Konto `nutzer` über `pkexec`).
  Die Server kommen aus der Maske oder aus Mozillas Anbieter-Datenbank, das
  Passwort geht direkt in Thunderbirds verschlüsselten Passwortspeicher und
  in keine DialOS-Datei - Einzelheiten und Begründung in
  [sicherheit-datenschutz.md](sicherheit-datenschutz.md), Abschnitt
  „Zugangsdaten für Dienste". Am 2026-09-25 in beiden Konten am Gerät
  belegt. Der Grund für den Weg über die Maske (Stephan, 2026-09-25): alle
  Kundendaten an einer Stelle erfassen und von dort auf die Programme
  verteilen - „So kann ich nix übersehen."
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

## Fußzeile in die Mail eintragen (Pflichtschritt nach der Konto-Einrichtung)

**Überholt als Handschritt seit 2026-09-25:** Wird das Mailkonto über die
Maske angelegt (siehe oben), trägt `dialos-mailkonto.py` die Signatur im
selben Lauf mit ein. Außerdem setzt `dialos-mail-signatur.service` sie bei
jedem Anmelden nach. Der Aufruf von Hand ist nur noch nötig, wenn ein Konto an
der Maske vorbei (in Thunderbirds eigenem Assistenten) angelegt wurde und die
Fußzeile schon vor dem nächsten Anmelden tragen soll. Der
alte Stand bleibt hier stehen, weil er erklärt, warum die Signatur überhaupt
ein eigener Schritt ist:

Sobald das Mailkonto steht - egal ob nach Variante 1 oder 2 - fehlt noch
ein Schritt, und er lässt sich nicht vorziehen: Erst mit dem Konto gibt es
eine Identität, für die eine Signatur gesetzt werden kann. Bei geschlossenem
Thunderbird als der angemeldete Nutzer:

```bash
dialos-mail-signatur.py
```

Damit trägt jede Mail die Herkunftszeile aus
`/usr/local/share/dialos/fusszeile.txt`. Ohne diesen Aufruf geht das Gerät
ohne Fußzeile in Mails raus - am 2026-08-20 genau so passiert, weil das
Werkzeug zwar gebaut war, aber niemand es aufrief. Ohne Konto bricht das
Skript mit einem Hinweis ab, statt stillschweigend nichts zu tun.

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
