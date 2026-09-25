#!/usr/bin/env python3
"""Setzt eine Anleitung aus Markdown als PDF - cairo und Pango, wie der Brief.

WARUM EIN EIGENER SETZER (Stephan, 2026-09-25): Er wollte die
Installationsanleitung als PDF. Auf dem Geraet gibt es weder pandoc noch
weasyprint noch wkhtmltopdf; LibreOffice kann zwar HTML umwandeln, macht aus
Quelltextbloecken aber Fliesstext mit Trennstrichen. cairo und Pango liegen
ohnehin da - damit setzt DialOS schon den Brief nach DIN 5008.

WARUM DER INHALT IN MARKDOWN BLEIBT: Eine Anleitung, die nur als PDF
existiert, laesst sich nicht vergleichen, nicht durchsuchen und nicht
nachfuehren. Die Quelle liegt in docs/, das PDF wird daraus erzeugt - wie beim
Brief der Text neben dem Bogen.

Kann: # ## ### Ueberschriften, Absaetze, - Aufzaehlung, 1. Nummerierung,
Quelltextbloecke mit ```, Hinweise mit >, **fett**, `Befehl`, --- als Linie.
Mehr braucht eine Anleitung nicht, und mehr kann falsch aussehen.

Aufruf:
  dialos-anleitung-pdf.py docs/installationsanleitung.md [ziel.pdf]
"""

import html
import os
import re
import sys

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo  # noqa: E402

MM = 72 / 25.4
SEITE_B, SEITE_H = 210 * MM, 297 * MM
RAND_L, RAND_R = 22 * MM, 18 * MM
RAND_O, RAND_U = 20 * MM, 18 * MM
BREITE = SEITE_B - RAND_L - RAND_R
SCHRIFT = "Liberation Sans, DejaVu Sans, Sans"
FEST = "Liberation Mono, DejaVu Sans Mono, Monospace"
GROESSE = 10.5
GRAU = (0.42, 0.42, 0.42)
KASTEN = (0.94, 0.94, 0.94)
LINIE = (0.80, 0.80, 0.80)


def kontext():
    """Satz ohne Hinting - gemessene und gedruckte Zeilen sind dann gleich."""
    k = PangoCairo.FontMap.get_default().create_context()
    o = cairo.FontOptions()
    o.set_hint_metrics(cairo.HINT_METRICS_OFF)
    o.set_hint_style(cairo.HINT_STYLE_NONE)
    PangoCairo.context_set_font_options(k, o)
    PangoCairo.context_set_resolution(k, 72)
    return k


KONTEXT = kontext()


def auszeichnen(text):
    """**fett** und `Befehl` in Pango-Markup - und alles andere entschaerfen."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`",
                  lambda m: f'<span font_family="{FEST}" size="93%">{m.group(1)}</span>',
                  text)
    # Verweise wie [Text](ziel) auf den Text zusammenziehen - ein Link, den
    # niemand anklicken kann, ist auf Papier nur Klammergebirge.
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", text)
    return text


class Blatt:
    """Eine Seite nach der anderen, mit Fusszeile und Seitenzahl."""

    def __init__(self, ziel, titel):
        self.flaeche = cairo.PDFSurface(ziel, SEITE_B, SEITE_H)
        self.stift = cairo.Context(self.flaeche)
        self.titel = titel
        self.seite = 1
        self.y = RAND_O

    def layout(self, text, groesse=GROESSE, fett=False, fest=False,
               breite=BREITE, markup=True):
        lay = Pango.Layout.new(KONTEXT)
        familie = FEST if fest else SCHRIFT
        lay.set_font_description(Pango.FontDescription.from_string(
            f"{familie} {'Bold ' if fett else ''}{groesse}"))
        lay.set_width(int(breite * Pango.SCALE))
        lay.set_wrap(Pango.WrapMode.WORD_CHAR)
        if markup:
            lay.set_markup(text, -1)
        else:
            lay.set_text(text, -1)
        return lay

    def hoehe(self, lay):
        return lay.get_pixel_size()[1]

    def platz(self, hoehe):
        """Passt das noch? Sonst neue Seite - VOR dem Zeichnen gefragt."""
        if self.y + hoehe > SEITE_H - RAND_U - 6 * MM:
            self.neue_seite()

    def neue_seite(self):
        self.fusszeile()
        self.stift.show_page()
        self.seite += 1
        self.y = RAND_O

    def fusszeile(self):
        lay = self.layout(f'<span foreground="#6b6b6b">{html.escape(self.titel)}'
                          f'  ·  Seite {self.seite}</span>', groesse=8.5)
        self.stift.move_to(RAND_L, SEITE_H - RAND_U)
        PangoCairo.show_layout(self.stift, lay)

    def schreiben(self, lay, x=RAND_L, abstand=0.0):
        self.stift.set_source_rgb(0, 0, 0)
        self.stift.move_to(x, self.y)
        PangoCairo.show_layout(self.stift, lay)
        self.y += self.hoehe(lay) + abstand

    def fertig(self):
        self.fusszeile()
        self.flaeche.finish()


def setzen(quelle, ziel):
    zeilen = open(quelle, encoding="utf-8").read().splitlines()
    titel = next((z[2:].strip() for z in zeilen if z.startswith("# ")), "DialOS")
    blatt = Blatt(ziel, titel)
    i = 0
    nummer = 0
    erste = True
    while i < len(zeilen):
        z = zeilen[i]
        # --- Quelltextblock: als Ganzes, mit grauem Kasten
        if z.startswith("```"):
            block = []
            i += 1
            while i < len(zeilen) and not zeilen[i].startswith("```"):
                block.append(zeilen[i])
                i += 1
            i += 1
            lay = blatt.layout(html.escape("\n".join(block)), groesse=9,
                               fest=True, breite=BREITE - 8 * MM)
            h = blatt.hoehe(lay)
            blatt.platz(h + 7 * MM)
            blatt.stift.set_source_rgb(*KASTEN)
            blatt.stift.rectangle(RAND_L - 2 * MM, blatt.y - 2 * MM,
                                  BREITE + 4 * MM, h + 4 * MM)
            blatt.stift.fill()
            blatt.schreiben(lay, x=RAND_L + 1 * MM, abstand=5 * MM)
            continue
        # --- Ueberschriften
        if z.startswith("# "):
            if not erste:
                blatt.neue_seite()
            erste = False
            lay = blatt.layout(auszeichnen(z[2:]), groesse=19, fett=True)
            blatt.schreiben(lay, abstand=1.5 * MM)
            blatt.stift.set_source_rgb(*LINIE)
            blatt.stift.rectangle(RAND_L, blatt.y, BREITE, 0.8)
            blatt.stift.fill()
            blatt.y += 5 * MM
        elif z.startswith("## "):
            lay = blatt.layout(auszeichnen(z[3:]), groesse=14, fett=True)
            blatt.platz(blatt.hoehe(lay) + 14 * MM)   # nie allein am Fuss
            blatt.y += 3 * MM
            blatt.schreiben(lay, abstand=2.5 * MM)
        elif z.startswith("### "):
            lay = blatt.layout(auszeichnen(z[4:]), groesse=11.5, fett=True)
            blatt.platz(blatt.hoehe(lay) + 12 * MM)
            blatt.y += 2 * MM
            blatt.schreiben(lay, abstand=1.5 * MM)
        # --- Hinweis
        elif z.startswith("> "):
            block = []
            while i < len(zeilen) and zeilen[i].startswith("> "):
                block.append(zeilen[i][2:])
                i += 1
            lay = blatt.layout(auszeichnen(" ".join(block)), breite=BREITE - 6 * MM)
            h = blatt.hoehe(lay)
            blatt.platz(h + 6 * MM)
            blatt.stift.set_source_rgb(0.25, 0.25, 0.25)
            blatt.stift.rectangle(RAND_L, blatt.y - 1 * MM, 1.2 * MM, h + 2 * MM)
            blatt.stift.fill()
            blatt.schreiben(lay, x=RAND_L + 5 * MM, abstand=4 * MM)
            continue
        # --- Aufzaehlung und Nummerierung
        elif z.startswith("- "):
            lay = blatt.layout(auszeichnen(z[2:]), breite=BREITE - 6 * MM)
            blatt.platz(blatt.hoehe(lay))
            punkt = blatt.layout("•")
            blatt.stift.set_source_rgb(0, 0, 0)
            blatt.stift.move_to(RAND_L, blatt.y)
            PangoCairo.show_layout(blatt.stift, punkt)
            blatt.schreiben(lay, x=RAND_L + 5 * MM, abstand=1.5 * MM)
        elif re.match(r"^\d+\. ", z):
            nummer = int(z.split(".", 1)[0])
            rest = z.split(". ", 1)[1]
            lay = blatt.layout(auszeichnen(rest), breite=BREITE - 8 * MM)
            blatt.platz(blatt.hoehe(lay))
            zahl = blatt.layout(f"<b>{nummer}.</b>")
            blatt.stift.set_source_rgb(0, 0, 0)
            blatt.stift.move_to(RAND_L, blatt.y)
            PangoCairo.show_layout(blatt.stift, zahl)
            blatt.schreiben(lay, x=RAND_L + 7 * MM, abstand=1.5 * MM)
        elif z.strip() == "---":
            blatt.platz(6 * MM)
            blatt.stift.set_source_rgb(*LINIE)
            blatt.stift.rectangle(RAND_L, blatt.y + 2 * MM, BREITE, 0.6)
            blatt.stift.fill()
            blatt.y += 6 * MM
        elif not z.strip():
            blatt.y += 2.2 * MM
        else:
            lay = blatt.layout(auszeichnen(z))
            blatt.platz(blatt.hoehe(lay))
            blatt.schreiben(lay, abstand=1.2 * MM)
        i += 1
    blatt.fertig()
    return blatt.seite


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    quelle = sys.argv[1]
    ziel = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(quelle)[0] + ".pdf"
    seiten = setzen(quelle, ziel)
    print(f"{ziel} - {seiten} Seiten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
