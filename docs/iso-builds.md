[Deutsch](iso-builds.md) | [English](iso-builds.en.md)

# Abbild-Verzeichnis

Sicherungs-Abbilder (Rescuezilla/Clonezilla, siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 16) werden **nicht**
in Git versioniert - mehrere GB pro Datei, GitHub blockt einzelne Dateien
über 100 MB ohnehin. Hier steht nur dieses schlanke Verzeichnis, damit
nachvollziehbar bleibt, welches Abbild zu welchem Code-Stand gehört, ohne
die Datei selbst zu versionieren.

## Aufräumaktion vom 2026-08-16

**Acht alte ISOs wurden bewusst gelöscht** (rund 59 GB) - das ist keine
Datenpanne, sondern eine Entscheidung. Alle stammten aus der
Penguins-Eggs-Zeit, die am selben Tag entfallen ist (siehe Schritt 16),
und bildeten Systemstände ab, die der Neuaufbau vom 2026-08-16 deutlich
überholt hat. Prüfsummen lagen für keine davon vor, nur für die unten
verbliebene.

Gelöscht: `DialOS-Clone-mit-home.iso`, `DialOS-live.iso`,
`DialOS-Live-0.1.iso`, `DialOS-Live-0.2.0.iso`, `DialOS-Live-0.3.0.iso`,
`DialOS-Live-0.4.0.iso`, `DialOS-Live-0.5.0.iso`,
`DialOS-Live-0.5.0-clone.iso`.

## Aktueller Bestand

| Version | Dateiname | Datum | Commit | SHA256 | Ablageort |
|---|---|---|---|---|---|
| 0.5.1 | `DialOS-Live-0.5.1-clone.iso` | 2026-08-16 | `ac89f26` | `73378ae3da384e28ef1123c0efad9e98122c8c12ae4edbd26dc8496ce587ed32` | nur externe Platte, `DialOS-ISOs/` |

**Diese Datei bleibt bewusst liegen, bis das erste Rescuezilla-Abbild da
ist** (Stephans Entscheidung, 2026-08-16). Sie war das Sicherheitsnetz
für den End-to-end-Test des neuen Aufbauwegs - der ist bestanden, ihr
Zweck also erfüllt. Sie existiert aber nirgendwo sonst und ließe sich
nicht neu erzeugen, weil der Bauweg dahinter entfallen ist. Deshalb erst
löschen, wenn der Ersatz vorhanden ist: So steht nie ein Moment ganz ohne
Rückfallebene.

## Beim Erstellen eines neuen Abbilds eintragen

Rescuezilla erzeugt Verzeichnisse, keine einzelne Datei - die Prüfsumme
bezieht sich daher sinnvollerweise auf das Archiv oder entfällt.
Festhalten lohnt sich in jedem Fall der Commit-Stand, zu dem das Abbild
gehört:

```bash
git log -1 --format=%H
```

Und **was im Abbild fehlt**: Die LUKS-Partition `dialos-nutzer-home` wird
bewusst nicht mitgesichert (Begründung in Schritt 16). Ein Abbild stellt
also root und EFI wieder her, nicht `nutzer`s Daten.
