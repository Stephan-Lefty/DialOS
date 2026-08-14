[Deutsch](iso-builds.md) | [English](iso-builds.en.md)

# ISO-Builds

Gebaute Live-/Installations-Images (`eggs produce`, siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 16) werden **nicht**
in Git versioniert - mehrere GB pro Datei, GitHub blockt einzelne
Dateien über 100 MB ohnehin. Stattdessen: Datei liegt in Stephans
selbst gehosteter Nextcloud (gleicher Gedanke wie bei den
verschlüsselten Schlüssel-Backups, siehe
[sicherheit-datenschutz.md](sicherheit-datenschutz.md)), hier im Repo
steht nur dieses schlanke Verzeichnis - damit bleibt nachvollziehbar,
welche ISO zu welchem Code-Stand gehört, ohne die Datei selbst zu
versionieren.

## Beim Bauen einer neuen ISO eintragen

```bash
sha256sum DialOS-Live-X.Y.Z.iso
git log -1 --format=%H
```

| Version | Dateiname | Datum | Commit | SHA256 | Ablageort |
|---|---|---|---|---|---|
| _(Vorlage)_ | `DialOS-Live-X.Y.Z.iso` | JJJJ-MM-TT | `abcdef1` | `…` | Nextcloud-Pfad |

## Bisherige Builds

Noch nicht nachgetragen - die beiden bisher gebauten 0.5.0-Test-ISOs
(`DialOS-Live-0.5.0.iso`, `DialOS-Live-0.5.0-clone.iso`, siehe
[README-Änderungsprotokoll](../README.md#änderungsprotokoll)) liegen
nicht mehr lokal vor, Prüfsumme/Commit-Zuordnung lassen sich im
Nachhinein nicht mehr zuverlässig ermitteln. Ab dem nächsten Build oben
in die Tabelle eintragen.
