[Deutsch](TODO.md) | [English](TODO.en.md) | [Änderungsprotokoll](README.md#änderungsprotokoll)

# TODO

Laufende Liste offener Kleinigkeiten und nächster Schritte, die Stephan
oder Claude im Arbeitsalltag auffallen. Anders als
[Offene Punkte](docs/offene-punkte.md) (grundsätzliche, noch nicht
entschiedene Architekturfragen) sind das hier konkrete, abhakbare
Aufgaben. Erledigte Punkte werden aus dieser Datei gelöscht, nicht nur
abgehakt.

- [ ] Calamares im echten Live-Boot testen (nicht nur direkt auf dem
  installierten System) - `eggs sysinstall` sollte dank
  `.HasCalamares`-Erkennung automatisch Calamares statt Krill starten.
  Dabei auch einmal komplett durchklicken (inkl. Partitionierung) auf
  einem Testgerät/einer VM, nicht auf dem T490 selbst.
- [ ] Perspektivisch: neuen ISO-Build mit allen gesammelten Fixes
  (Bootscreen, Avatar-Skript, Calamares-Branding, Piper-TTS)
  erstellen.
- [ ] Sprechgeschwindigkeit der Piper-Stimme sollte vom Nutzer individuell
  einstellbar sein (aktuell fest über `GenericRateMultiply` in der
  Piper-Config verdrahtet, `0.85` als Stephans persönliche Präferenz
  gewählt) - braucht eine echte Einstellmöglichkeit (z. B. GNOME-
  Barrierefreiheitseinstellungen oder eigener Sprachbefehl), nicht nur
  einen Config-Wert.
- [ ] Live-Desktop-Icon für die Installation: `.desktop`-Datei mit Icon,
  die `sudo eggs sysinstall` ausführt, auf dem Live-Boot-Desktop
  bereitstellen (nicht dem installierten System). Erfordert erst zu
  klären, welchen Live-User/Desktop-Pfad `eggs`/`coa` beim ISO-Build für
  das generische (nicht `-clone-`) Image tatsächlich verwendet.
