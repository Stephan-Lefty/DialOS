#!/usr/bin/env python3
"""
Erzeugt das Symbol von DialOS-Rhythmbox aus dem DialOS-App-Icon.

DialOS-Rhythmbox ist eine Erweiterung und soll auch so aussehen: derselbe
Kreis, dieselbe Dame, dieselbe tragende Hand, derselbe Blau-Grün-Verlauf.
Unterschied ist die rechte Hälfte - statt der Schallwellen steht dort ein
Mikrofon.

Die Vorlage wird nicht übermalt, sondern in eine Strichzeichnung mit
Transparenz zurückgerechnet (Weiß = durchsichtig, Farbe = Linie). Nur so
lassen sich die Schallwellen sauber entfernen und dieselbe Zeichnung auf
hellem wie dunklem Grund nutzen. Übernommen von
`Denkzettel/assets/icon-bauen.py` über `suche-icon-bauen.py`.

**Ersetzen, nicht addieren.** Die Lehre aus DialOS-Suche (2026-09-17)
steht in docs/erweiterungen.md: Stephans Entwurf hatte rechts DREI Objekte
und fiel bei 32 Pixeln durch, weil sie zu einem Klumpen verschmolzen. Der
erste Entwurf für Rhythmbox hatte Schallwellen UND Mikrofon - also zwei -
und ist am 2026-09-25 aus demselben Grund durchgefallen. Deshalb hier: die
Wellen raus, das Mikrofon an ihre Stelle.

DIESE DATEI FOLGT DIALOS: `rhythmbox-icon-light-*.png` hat die HELLE
Scheibe, `-dark-*.png` die dunkle - wie bei suche-icon-*, und damit
umgekehrt zu Denkzettel. Zwei gegenläufige Bedeutungen desselben Suffixes
im selben Ordner wären der sichere Weg, beim Einbinden die falsche Datei
zu erwischen.

Aufruf:

    python3 assets/rhythmbox-icon-bauen.py
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent
VORLAGE_STANDARD = ASSETS / "app-icon-light.png"

S = 4
N = 512 * S

CYAN = (0, 173, 212)
GRUEN = (98, 197, 0)
NAVY = (13, 27, 51)
WEISS = (255, 255, 255)

GRUND_HELL = WEISS        # rhythmbox-icon-light-*.png - helle Scheibe
GRUND_DUNKEL = NAVY       # rhythmbox-icon-dark-*.png  - dunkle Scheibe

# Bereich der drei Schallwellen in der Vorlage (512er-Koordinaten),
# übernommen aus suche-icon-bauen.py - es ist dieselbe Vorlage.
WELLEN = (306, 175, 425, 358)

MITTE = 255.5
MAX_RADIUS = 192

# Lage und Maße des Mikrofons, in 512er-Koordinaten.
MIK_MITTE = (358, 250)
MIK_BREITE = 46           # Breite der Kapsel
MIK_HOEHE = 84            # Höhe der Kapsel (inkl. der runden Enden)
MIK_STRICH = 11
MIK_BUEGEL = 34           # wie weit der Bügel die Kapsel umfasst
MIK_FUSS = 30             # Ständer unter der Kapsel

GROESSEN = (512, 256, 128, 64, 48, 32)


def strichzeichnung(vorlage: Path):
    """Vorlage in (Linien-RGBA, Kreisscheibe-Maske) zerlegen."""
    im = Image.open(vorlage).convert("RGBA").resize((N, N), Image.LANCZOS)
    scheibe = im.getchannel("A")
    rgb = im.convert("RGB").load()
    scheibe_px = scheibe.load()

    linien = Image.new("RGBA", (N, N))
    lp = linien.load()
    for y in range(N):
        for x in range(N):
            if scheibe_px[x, y] < 8:
                continue
            r, g, b = rgb[x, y]
            a = 255 - min(r, g, b)
            if a < 8:
                continue
            f = 255 / a
            lp[x, y] = (
                max(0, min(255, int(255 - (255 - r) * f))),
                max(0, min(255, int(255 - (255 - g) * f))),
                max(0, min(255, int(255 - (255 - b) * f))),
                min(a, scheibe_px[x, y]),
            )
    return linien, scheibe


def verlauf_maske(maske: Image.Image, c1, c2) -> Image.Image:
    g = Image.new("RGB", (N, N))
    d = ImageDraw.Draw(g)
    for i in range(N):
        t = i / (N - 1)
        d.line([(i, 0), (i, N)],
               fill=tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)))
    g = g.convert("RGBA")
    g.putalpha(maske)
    return g


def mikrofon(d, mitte, breite, hoehe, strich, buegel, fuss):
    """Mikrofon: gefüllte Kapsel, Bügel darum, kurzer Ständer.

    Die Kapsel ist gefüllt und nicht als Umriss gezeichnet - ein Umriss
    hätte bei 32 Pixeln innen keine zwei Pixel mehr und liefe zu. Gefüllt
    bleibt sie ein klarer senkrechter Block und ist damit von Denkzettels
    schrägem Stift und der runden Lupe der Suche unterscheidbar.

    Der Bügel ist der Teil, der aus dem Block ein Mikrofon macht. Er ist
    bewusst offen nach oben: So bleibt oben Luft zur Kapsel, statt bei
    kleinen Größen mit ihr zu einem Klotz zu verschmelzen.
    """
    cx, cy = mitte
    halb_b, halb_h = breite / 2, hoehe / 2

    # Kapsel (Rechteck mit halbrunden Enden)
    d.rounded_rectangle([cx - halb_b, cy - halb_h, cx + halb_b, cy + halb_h],
                        radius=halb_b, fill=255)

    # Bügel: Bogen unterhalb der Kapselmitte, links und rechts hochgezogen
    r = halb_b + buegel
    d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=160,
          fill=255, width=int(strich))

    # Ständer und Fuß
    y0 = cy + r - strich * 0.3
    y1 = y0 + fuss
    d.line([(cx, y0), (cx, y1)], fill=255, width=int(strich))
    d.line([(cx - fuss * 0.7, y1), (cx + fuss * 0.7, y1)],
           fill=255, width=int(strich))


def abstand_pruefen() -> float:
    """Weitester Punkt des Mikrofons von der Bildmitte, in 512er-Einheiten.

    Das Mikrofon darf den Ring der Vorlage nicht berühren, auch nicht bei
    32 Pixeln, wo ein Pixel gut 8 dieser Einheiten entspricht.
    """
    cx, cy = MIK_MITTE
    r = MIK_BREITE / 2 + MIK_BUEGEL
    ecken = [
        (cx - MIK_BREITE / 2, cy - MIK_HOEHE / 2),
        (cx + MIK_BREITE / 2, cy - MIK_HOEHE / 2),
        (cx - r, cy), (cx + r, cy),
        (cx - MIK_FUSS * 0.7, cy + r + MIK_FUSS),
        (cx + MIK_FUSS * 0.7, cy + r + MIK_FUSS),
    ]
    return max(math.hypot(x - MITTE, y - MITTE) for x, y in ecken) + MIK_STRICH / 2


def bauen(vorlage: Path, ziel: Path) -> None:
    weit = abstand_pruefen()
    if weit > MAX_RADIUS:
        raise SystemExit(
            f"Das Mikrofon reicht bis Radius {weit:.1f} und damit über die "
            f"erlaubten {MAX_RADIUS} hinaus - es würde den Ring berühren.")
    print(f"Mikrofon reicht bis Radius {weit:.1f} von erlaubten {MAX_RADIUS} - ok")

    linien, scheibe = strichzeichnung(vorlage)

    # Schallwellen entfernen - dieselbe Stelle, die Denkzettel freiräumt.
    kasten = tuple(int(v * S) for v in WELLEN)
    leer = Image.new("RGBA", (kasten[2] - kasten[0], kasten[3] - kasten[1]),
                     (0, 0, 0, 0))
    linien.paste(leer, (kasten[0], kasten[1]))

    maske = Image.new("L", (N, N), 0)
    mikrofon(ImageDraw.Draw(maske),
             (MIK_MITTE[0] * S, MIK_MITTE[1] * S),
             MIK_BREITE * S, MIK_HOEHE * S, MIK_STRICH * S,
             MIK_BUEGEL * S, MIK_FUSS * S)
    linien.alpha_composite(verlauf_maske(maske, CYAN, GRUEN))

    for grund, name in ((GRUND_HELL, "rhythmbox-icon-light"),
                        (GRUND_DUNKEL, "rhythmbox-icon-dark")):
        voll = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        scheibe_farbig = Image.new("RGBA", (N, N), grund + (255,))
        scheibe_farbig.putalpha(scheibe)
        voll.alpha_composite(scheibe_farbig)
        voll.alpha_composite(linien)
        for g in GROESSEN:
            pfad = ziel / f"{name}-{g}.png"
            voll.resize((g, g), Image.LANCZOS).save(pfad)
            print(f"  {pfad.name}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vorlage", type=Path, default=VORLAGE_STANDARD)
    p.add_argument("--ziel", type=Path, default=ASSETS)
    a = p.parse_args()
    bauen(a.vorlage, a.ziel)
