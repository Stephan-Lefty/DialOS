#!/usr/bin/env python3
"""
Erzeugt das Icon der Erweiterung DialOS-Suche aus dem DialOS-App-Icon.

Abgeleitet von `Denkzettel/assets/icon-bauen.py` - dieselbe Technik, weil sie
dort schon einmal genau dieses Problem gelöst hat: Die Vorlage wird nicht
übermalt, sondern in eine Strichzeichnung mit Transparenz zurückgerechnet
(Weiß = durchsichtig, Farbe = Linie). Nur so lassen sich die Schallwellen
sauber entfernen und dieselbe Zeichnung auf hellem wie dunklem Grund nutzen.

WARUM NICHT STEPHANS ENTWURF DIREKT (`suche-icon-entwurf.png`, 2026-09-17):
Der Entwurf zeigt rechts DREI Objekte - Dokument, Briefumschlag und Lupe.
Gemessen fällt er dadurch bei 32 Pixeln durch: Die drei verschmelzen zu einem
Klumpen, während DialOS und Denkzettel dort klar bleiben. Für die rechte
Hälfte stehen bei 32 px nur etwa 14 x 20 Pixel zur Verfügung. Stilistisch
sitzt der Entwurf; er bleibt als Vorlage der Idee liegen.

DIE LUPE WIRD GEZEICHNET, NICHT AUSGESCHNITTEN. Aus dem Entwurf kopiert käme
sie mit den Schnittkanten des überlappenden Briefumschlags. Gezeichnet hat sie
saubere Kanten, freie Größe und kann den Platz allein nutzen. Denkzettel hat
den Stift aus demselben Grund gezeichnet.

ZWEI VARIANTEN WURDEN GEBAUT UND VERGLICHEN (2026-09-17), damit es niemand ein
zweites Mal prüft:

  "nur Lupe"      - Schallwellen entfernt, Lupe an ihrer Stelle. GEWÄHLT.
                    Bei 32 px klar als Kreis mit Griff lesbar und von DialOS
                    (Wellen) wie Denkzettel (Stift) eindeutig unterscheidbar.
  "Wellen + Lupe" - näher an Stephans Entwurf, aber VERWORFEN: Bei 32 px
                    überlagern sich Wellen und Ring zu demselben Klumpen, den
                    der Entwurf schon hatte. Zwei Elemente sind an dieser
                    Stelle eines zu viel - genau die Lehre aus dem Entwurf.

Das Ergebnis folgt damit dem Muster der Familie: Denkzettel ersetzt die
Schallwellen durch den Stift, DialOS-Suche durch die Lupe. Ersetzen, nicht
ergänzen.

Aufruf (die DialOS-Vorlage liegt im selben Ordner):

    python3 assets/suche-icon-bauen.py
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent
VORLAGE_STANDARD = ASSETS / "app-icon-light.png"

S = 4            # Supersampling gegen Treppenkanten
N = 512 * S      # Arbeitsgröße

CYAN = (0, 173, 212)      # aus dem DialOS-Icon abgetastet
GRUEN = (98, 197, 0)
NAVY = (13, 27, 51)       # Hintergrund der dunklen DialOS-Variante
WEISS = (255, 255, 255)

# ACHTUNG, HIER WEICHT DIESE DATEI VON DENKZETTEL AB - gemessen am 2026-09-17,
# damit es niemand ein zweites Mal prüft. DialOS und Denkzettel benennen ihre
# beiden Fassungen GEGENLÄUFIG:
#
#   DialOS/assets/app-icon-light.png          Scheibe rgb(254,255,255)  hell
#   DialOS/assets/app-icon-dark.png           Scheibe rgb(  4, 22, 47)  dunkel
#   Denkzettel/assets/app-icon-dark.png       Scheibe rgb(255,255,255)  HELL
#
# Bei Denkzettel heißt "-dark" also "Datei für dunkle Umgebungen" (Stephans
# Entscheidung vom 2026-08-24), bei DialOS heißt "-dark" schlicht "dunkles
# Icon". Beide sind für sich stimmig; zusammen sind sie eine Falle.
#
# DIESE DATEI FOLGT DIALOS, weil sie im DialOS-Repo liegt und ihre Ergebnisse
# in demselben Ordner neben app-icon-light.png und app-icon-dark.png landen.
# Zwei gegenläufige Bedeutungen desselben Suffixes im selben Ordner wären der
# sichere Weg, beim Einbinden die falsche Datei zu erwischen - und ein falsches
# Icon fällt einem blinden Nutzer nie auf, dem sehenden Helfer aber sofort.
GRUND_HELL = WEISS        # suche-icon-light-*.png  - helle Scheibe
GRUND_DUNKEL = NAVY       # suche-icon-dark-*.png   - dunkle Scheibe

# Bereich der drei Schallwellen in der Vorlage (512er-Koordinaten),
# übernommen aus Denkzettels icon-bauen.py - es ist dieselbe Vorlage.
WELLEN = (306, 175, 425, 358)

# Der Ring der Vorlage liegt je nach Richtung bei Radius 215-236 (Mitte
# 255,5). Alles Neue bleibt innerhalb von MAX_RADIUS - die Lupe darf den Bogen
# nicht berühren, auch nicht bei 32 Pixeln, wo ein Pixel gut 8 Einheiten dieser
# 512er-Koordinaten entspricht.
MITTE = 255.5
MAX_RADIUS = 192

# Lage und Maße der Lupe, in 512er-Koordinaten. Der erste Versuch (Mitte
# 368/266, Griff 30) hat die Prüfung unten mit 193,6 gerissen - deshalb steht
# sie hier und ist keine Zierde.
LUPE_MITTE = (360, 262)
LUPE_RADIUS = 52
LUPE_STRICH = 11
LUPE_WINKEL = 42          # Griff nach rechts unten, weg von Gesicht und Hand
LUPE_GRIFF = 26

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
            a = 255 - min(r, g, b)          # Deckkraft = Abstand zu Weiß
            if a < 8:
                continue
            f = 255 / a                      # Farbe auf volle Sättigung zurück
            lp[x, y] = (
                max(0, min(255, int(255 - (255 - r) * f))),
                max(0, min(255, int(255 - (255 - g) * f))),
                max(0, min(255, int(255 - (255 - b) * f))),
                min(a, scheibe_px[x, y]),
            )
    return linien, scheibe


def verlauf_maske(maske, c1, c2):
    """Graustufen-Maske mit waagrechtem Farbverlauf einfärben."""
    g = Image.new("RGB", (N, N))
    d = ImageDraw.Draw(g)
    for i in range(N):
        t = i / (N - 1)
        d.line([(i, 0), (i, N)],
               fill=tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)))
    g = g.convert("RGBA")
    g.putalpha(maske)
    return g


def lupe(d, mitte, radius, strich, winkel_grad, griff_laenge):
    """Lupe: Ring plus Griff mit abgerundetem Ende.

    Der Ring ist die Form, die bei 32 Pixeln überlebt - ein Kreis bleibt auch
    als Klumpen ein Kreis. Der Griff ist deshalb bewusst kurz: Er erklärt die
    Form bei 512 Pixeln, trägt aber nichts mehr, wenn nur wenige Pixel da sind,
    und je länger er ist, desto näher kommt er dem Bogen.
    """
    cx, cy = mitte
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              outline=255, width=int(strich))

    a = math.radians(winkel_grad)
    dx, dy = math.cos(a), math.sin(a)
    x0, y0 = cx + dx * (radius - strich * 0.2), cy + dy * (radius - strich * 0.2)
    x1, y1 = cx + dx * (radius + griff_laenge), cy + dy * (radius + griff_laenge)
    griff = strich * 1.5
    d.line([(x0, y0), (x1, y1)], fill=255, width=int(griff))
    h = griff / 2
    d.ellipse([x1 - h, y1 - h, x1 + h, y1 + h], fill=255)


def abstand_pruefen():
    """Berührt die Lupe den Bogen der Vorlage? VOR dem Zeichnen prüfen.

    Nicht Feinschliff: Ein Strich, der den Ring berührt, sieht bei 512 Pixeln
    nach Absicht aus und bei 32 nach einem Fehler. Der erste Entwurf dieser
    Datei ist hier aufgelaufen (193,6 gegen 192), und zwar am Griffende.
    """
    cx, cy = LUPE_MITTE
    ring = math.hypot(cx - MITTE, cy - MITTE) + LUPE_RADIUS + LUPE_STRICH / 2
    a = math.radians(LUPE_WINKEL)
    gx = cx + math.cos(a) * (LUPE_RADIUS + LUPE_GRIFF)
    gy = cy + math.sin(a) * (LUPE_RADIUS + LUPE_GRIFF)
    griff = math.hypot(gx - MITTE, gy - MITTE) + LUPE_STRICH * 0.75
    weit = max(ring, griff)
    if weit > MAX_RADIUS:
        raise SystemExit(
            f"Lupe ragt bis {weit:.1f}, erlaubt sind {MAX_RADIUS}. "
            "LUPE_MITTE, LUPE_RADIUS oder LUPE_GRIFF anpassen.")
    return weit


def bauen(vorlage: Path, ziel: Path):
    weit = abstand_pruefen()
    print(f"Lupe reicht bis Radius {weit:.1f} von erlaubten {MAX_RADIUS} - ok")

    linien, scheibe = strichzeichnung(vorlage)

    # Schallwellen entfernen - dieselbe Stelle, die Denkzettel freiräumt.
    kasten = tuple(int(v * S) for v in WELLEN)
    leer = Image.new("RGBA", (kasten[2] - kasten[0], kasten[3] - kasten[1]), (0, 0, 0, 0))
    linien.paste(leer, (kasten[0], kasten[1]))

    maske = Image.new("L", (N, N), 0)
    lupe(ImageDraw.Draw(maske),
         (LUPE_MITTE[0] * S, LUPE_MITTE[1] * S),
         LUPE_RADIUS * S, LUPE_STRICH * S, LUPE_WINKEL, LUPE_GRIFF * S)
    linien.alpha_composite(verlauf_maske(maske, CYAN, GRUEN))

    for grund, name in ((GRUND_HELL, "suche-icon-light"),
                        (GRUND_DUNKEL, "suche-icon-dark")):
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
    p = argparse.ArgumentParser()
    p.add_argument("--vorlage", type=Path, default=VORLAGE_STANDARD)
    p.add_argument("--ziel", type=Path, default=ASSETS)
    a = p.parse_args()
    bauen(a.vorlage, a.ziel)
