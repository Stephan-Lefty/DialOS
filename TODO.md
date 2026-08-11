[Deutsch](TODO.md) | [English](TODO.en.md) | [Änderungsprotokoll](README.md#änderungsprotokoll)

# TODO

Laufende Liste offener Kleinigkeiten und nächster Schritte, die Stephan
oder Claude im Arbeitsalltag auffallen. Anders als
[Offene Punkte](docs/offene-punkte.md) (grundsätzliche, noch nicht
entschiedene Architekturfragen) sind das hier konkrete, abhakbare
Aufgaben. Erledigte Punkte werden aus dieser Datei gelöscht, nicht nur
abgehakt.

- [ ] Neuen Live-Boot-Test mit der ISO vom 11.08. durchführen, um die
  gesammelten Kosmetik-Fixes zu verifizieren: NTP-Client
  (systemd-timesyncd), größeres Partitionen-Fenster (1000x700),
  DialOS-Branding im Calamares-Assistenten selbst (über neuen
  Vendor-Overlay `/etc/penguins-eggs.d/brain.d/assets/calamares/`, da
  `eggs sysinstall` sein eigenes "eggs"-Branding live regeneriert und
  `/etc/calamares/branding/dialos/` dabei ignoriert - Details in
  CLAUDE.md), umbenanntes/gebrandetes Install-Icon
  (`/usr/share/applications/install-system.desktop`), und ob dadurch
  auch die Pinguin-Werbebilder während der Installation durch
  DialOS-Inhalt ersetzt werden.
- [ ] Calamares-Standort-Seite schlägt beim Live-Boot GeoIP-basiert oft
  einen falschen Standort vor (z. B. Rome statt Berlin) - kein
  dokumentierter Vendor-Override für `modules/locale.conf` gefunden
  (nur Branding ist offiziell überschreibbar). Bleibt vorerst
  Werkzeug-Einschränkung; installierende Person muss Standort beim
  Durchklicken manuell prüfen/korrigieren (unkritisch bei
  Zwei-Phasen-Provisionierung, da Endkunden den Installer nie sehen).
- [ ] Sprechgeschwindigkeit der Piper-Stimme sollte vom Nutzer individuell
  einstellbar sein (aktuell fest über `GenericRateMultiply` in der
  Piper-Config verdrahtet, `0.85` als Stephans persönliche Präferenz
  gewählt) - braucht eine echte Einstellmöglichkeit (z. B. GNOME-
  Barrierefreiheitseinstellungen oder eigener Sprachbefehl), nicht nur
  einen Config-Wert.
