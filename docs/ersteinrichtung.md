[Deutsch](ersteinrichtung.md) | [English](ersteinrichtung.en.md)

# Ersteinrichtung & Rollout

## Zwei-Phasen-Provisionierung

1. **Büro-Setup (Stephan)**: Ein generisches "Golden Image" wird komplett
   eingerichtet, inklusive Testlauf. Alles, was sich datenschutz- oder
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
auf Vosk+Piper-Basis, getriggert durch eine Erstlauf-Markerdatei),
aktuell noch nicht umgesetzt.

Vor Ort per Sprache erfragt werden nur:
- **Name** des Nutzers, mit Rückbestätigung ("Ich habe verstanden: Anna
  Schmidt. Stimmt das?") und Korrekturmöglichkeit.
- **Begrüßungsstimme**: Auswahl aus 2–3 Piper-Stimmen per Hörprobe
  ("die zweite", "die männliche Stimme").
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
