# Symbole in diesem Ordner

## `dialos-fenster-symbolic.svg`

Symbol auf dem Startknopf, wenn die Windows-Optik aktiv ist (siehe
[Debian-zu-DialOS.md](../../../../../../../docs/Debian-zu-DialOS.md),
Schritt 11b). Vier Kacheln im Quadrat, ohne Rahmen.

**Bewusst nicht das Windows-Logo von Microsoft.** DialOS wird verkauft,
und ein fremdes Markenzeichen auf dem Startknopf eines verkauften Geräts
wäre ein Markenrechtsproblem. ArcMenu selbst weist im Quelltext darauf
hin, dass seine Distributions-Icons Marken ihrer Inhaber sind, und
liefert genau deshalb kein Windows-Symbol mit. Vier Kacheln im Quadrat
sind eine allgemeine, seit Langem übliche Form für "Fenster" bzw.
"Übersicht" - GNOME selbst benutzt sie als `view-grid-symbolic`.

## Regel für Symbol-Icons (teuer gelernt am 2026-08-16)

**Die Datei muss nach der XML-Zeile SOFORT mit `<svg` beginnen. Kein
Kommentar davor.** Deshalb steht die Erklärung hier und nicht in der
Datei selbst.

GNOME Shell färbt Icons, deren Name auf `-symbolic.svg` endet, in die
Vordergrundfarbe der Leiste um. Dafür baut es die Datei beim Laden um -
und stolpert über alles, was vor dem `<svg>`-Tag steht. Das Ergebnis ist
kein Fehler und keine Meldung, sondern eine **volle weiße Fläche** auf
dem Knopf. Genau das ist hier zweimal passiert, bis der Vergleich mit
`/usr/share/icons/Adwaita/symbolic/actions/view-grid-symbolic.svg` es
gezeigt hat.

Zwei Folgerungen daraus:

- **Vorlage ist immer eine Adwaita-Datei.** Neue Symbole so bauen, dass
  ein `diff` gegen eine Adwaita-Datei (mit ausgeblendeten Pfaddaten)
  keinen Unterschied zeigt: XML-Zeile, `<svg height="16px"
  viewBox="0 0 16 16" width="16px" …>`, ein einzelner `<path>` mit
  `fill="#2e3436"` direkt am Element, `</svg>`.
- **Ein selbst gerendertes Vorschaubild beweist nichts.** librsvg
  zeichnet die Datei so, wie sie dasteht, und zeigt sie deshalb auch
  dann korrekt an, wenn GNOME sie später zerlegt. Die einzige gültige
  Prüfung ist ein Blick auf die echte Leiste.

Zum Ausprobieren ohne Root-Rechte lässt sich der Pfad vorübergehend auf
eine Kopie im eigenen Home zeigen:

```bash
gsettings set org.gnome.shell.extensions.arcmenu custom-menu-button-icon \
  "'$HOME/.local/share/dialos/dialos-fenster-symbolic.svg'"
```

(Falls `gsettings` "Kein derartiges Schema" meldet:
`GSETTINGS_SCHEMA_DIR=/usr/share/gnome-shell/extensions/arcmenu@arcmenu.com/schemas`
davorsetzen - Debians ArcMenu-Paket legt sein Schema in den falschen
Ordner, siehe Schritt 11b.)
