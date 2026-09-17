#!/usr/bin/env python3
"""DialOS: Brief als PDF nach DIN 5008 (Form B) - ENTWURF vom 2026-09-17.

Stephan am 2026-09-16: "Koennen wir den Aufbau des Briefes so machen, wie es die
DIN-Norm verlangt? Damit dann die PDF-Datei immer sauber erstellt wird, egal ob
diese dann gedruckt wird oder per Mail verschickt wird."

WARUM EIN EIGENER SATZ STATT DES BISHERIGEN BRIEFBOGENS: Der Briefbogen ist
reiner Text, mit Leerzeichen ausgerichtet und festbreit gedruckt
(dialos-archiv.py als_pdf). Ein Anschriftfeld, das genau im Fenster eines
Umschlags sitzt, Falzmarken und ein Informationsblock brauchen Positionen in
Millimetern - das geht nur mit echtem Satz. Hier: cairo fuer die Seite, Pango
fuer Schrift, Umbruch und Silben, beides auf jedem DialOS-Geraet vorhanden.

DIN 5008, FORM B (hochgestelltes Anschriftfeld ist Form A; B ist der uebliche
Geschaeftsbrief mit 45 mm Briefkopf), alle Masse ab linker/oberer Blattkante:
  Briefkopf            0-45 mm hoch
  Anschriftfeld        links 20 mm, oben 45 mm, 85 x 45 mm
    Zusatz-/Vermerkzone  oberste 17,7 mm (5 Zeilen) - hier die Ruecksendeangabe
    Anschriftzone        27,3 mm (9 Zeilen), Text 5 mm eingerueckt (= 25 mm)
  Informationsblock    links 125 mm, oben 50 mm
  Betreff              zwei Leerzeilen unter dem Anschriftfeld (98,5 mm)
  Textrand             links 25 mm, rechts 20 mm
  Falzmarken           105 mm und 210 mm, Lochmarke 148,5 mm
Der Text steht in 11 pt; kleiner als 10 pt verlangt die Norm nicht.

WOHER DIE TEILE KOMMEN:
  Absender, Kontakt, Unterschrift  persoenliche Daten (dialos-persoenliche-daten.py)
  Brieftext                        brief_text() aus dialos-diktat.py - Betreff, Absaetze, Gruss
  Empfaenger                       noch offen: wird eingesprochen (Brief-Ausbau)
  Fusszeile                        dialos-fusszeile.py, wie bisher

Aufruf (zum Pruefen, noch nicht im Diktat eingebunden):
  dialos-brief-din.py BRIEF.txt ZIEL.pdf [--empfaenger "Zeile|Zeile|..."]
                      [--daten PERSOENLICHE-DATEN.txt] [--png VORSCHAU.png]
BRIEF.txt darf der reine Brieftext (Betreff, Absaetze, Gruss) oder ein alter
Briefbogen von dialos-diktat.py sein - der wird zurueckgewandelt.
"""

import datetime
import importlib.util
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
RAND_LINKS, RAND_RECHTS = 25 * MM, 20 * MM
TEXTBREITE = SEITE_B - RAND_LINKS - RAND_RECHTS
SCHRIFT = "Liberation Sans, DejaVu Sans, Sans"
GROESSE = 11
FUSS_OBEN = 282 * MM          # darunter nur noch die Fusszeile
FOLGESEITE_OBEN = 25 * MM

HIER = os.path.dirname(os.path.abspath(__file__))
PERSOENLICHE_DATEN_SKRIPT = os.path.join(HIER, "dialos-persoenliche-daten.py")
FUSSZEILE_SKRIPT = os.path.join(HIER, "dialos-fusszeile.py")
UNTERSCHRIFT_HINWEIS = ("Dieser Brief wurde per Spracheingabe erstellt und "
                        "ist deshalb nicht unterschrieben.")
GRUSSFORMELN = ("mit freundlichen grüßen", "mit freundlichem gruß", "freundliche grüße",
                "viele grüße", "liebe grüße", "herzliche grüße", "beste grüße",
                "hochachtungsvoll")


def holen(pfad, name):
    try:
        spec = importlib.util.spec_from_file_location(name, pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    except Exception:
        return None


# ------------------------------------------------------------------ Text zerlegen
def zerlegen(text):
    """Brieftext -> (betreff, [absaetze], gruss, name).

    Ein Absatz ist eine Liste von Zeilen - ein gesprochenes "neue Zeile" bleibt
    eine eigene Zeile, der Umbruch innerhalb einer Zeile macht Pango.
    """
    absaetze = [a.strip("\n") for a in re.split(r"\n\s*\n", text.strip()) if a.strip()]
    betreff = None
    if absaetze and absaetze[0].lower().startswith("betreff:"):
        erste, _, rest = absaetze[0].partition("\n")
        betreff = erste.split(":", 1)[1].strip()
        absaetze[0:1] = [rest] if rest.strip() else []
    gruss = name = None
    # Steht der Gruss noch im letzten Absatz ("... ueberweisen. Mit freundlichen
    # Gruessen\nName" - so schrieb das Diktat bis zum 2026-09-16), wird er abgetrennt.
    if absaetze:
        muster = re.compile(r"(?i)(?<=[.!?])\s+(" + "|".join(re.escape(g) for g in GRUSSFORMELN)
                            + r")\b")
        treffer = list(muster.finditer(absaetze[-1]))
        if treffer:
            letzter = treffer[-1]
            absaetze[-1:] = [absaetze[-1][:letzter.start()], absaetze[-1][letzter.start(1):]]
    if absaetze:
        zeilen = absaetze[-1].split("\n")
        if zeilen[0].strip().rstrip(",").lower() in GRUSSFORMELN:
            gruss = zeilen[0].strip().rstrip(",")
            name = " ".join(z.strip() for z in zeilen[1:] if z.strip()) or None
            absaetze.pop()
    return betreff, [a.split("\n") for a in absaetze], gruss, name


def aus_briefbogen(text):
    """Alter Briefbogen (reiner Text, Leerzeichen-Satz) -> Brieftext.

    Kopf bis zur Datumszeile weg, Hinweis und Fusszeile weg, und die Zeilen, die
    nur der Umbruch auf 76 Zeichen getrennt hat, wieder zusammen: Eine Zeile,
    die fast bis zum Rand reicht, war ein Umbruch; eine kurze war gewollt.
    """
    zeilen = text.split("\n")
    start = 0
    for i, zeile in enumerate(zeilen[:12]):
        if re.search(r"\b\d{1,2}\. \w+ \d{4}\s*$", zeile) and zeile.startswith("   "):
            start = i + 1
    rumpf = []
    for zeile in zeilen[start:]:
        if zeile.startswith("Dieser Brief wurde per Spracheingabe") or \
                "powered by DialOS" in zeile:
            break
        rumpf.append(zeile.rstrip())
    text = "\n".join(rumpf).strip("\n")
    text = re.sub(r"\nunterschrieben\.\s*$", "", text)
    ergebnis = []
    for absatz in re.split(r"\n\s*\n", text):
        teile = absatz.split("\n")
        verbunden = [teile[0]]
        for vorige, zeile in zip(teile, teile[1:]):
            # Die Laenge der VORIGEN Zeile im Briefbogen zaehlt, nicht die schon
            # verbundene - sonst haengte sich der Name unter dem Gruss mit an.
            if len(vorige) >= 60:
                verbunden[-1] += " " + zeile.strip()
            else:
                verbunden.append(zeile)
        ergebnis.append("\n".join(verbunden))
    return "\n\n".join(ergebnis)


# ------------------------------------------------------------------ Satz
def pango_kontext():
    """EIN Satz-Kontext ohne Hinting: Zeilenumbrueche sind in PDF und Vorschau gleich.

    Mit dem Hinting der jeweiligen Flaeche koennte eine Zeile im PDF anders
    umbrechen als beim Messen - dann fehlte am Seitenende eine Zeile.
    """
    kontext = PangoCairo.FontMap.get_default().create_context()
    optionen = cairo.FontOptions()
    optionen.set_hint_metrics(cairo.HINT_METRICS_OFF)
    optionen.set_hint_style(cairo.HINT_STYLE_NONE)
    PangoCairo.context_set_font_options(kontext, optionen)
    # 72 dpi: Eine Pango-Einheit ist ein Punkt der PDF-Seite, 11 pt bleiben 11 pt.
    PangoCairo.context_set_resolution(kontext, 72)
    return kontext


KONTEXT = pango_kontext()


class Satz:
    def __init__(self, stift):
        self.stift = stift

    def layout(self, text, groesse=GROESSE, fett=False, breite=None, markup=False):
        lay = Pango.Layout.new(KONTEXT)
        schrift = Pango.FontDescription.from_string(
            f"{SCHRIFT} {'Bold ' if fett else ''}{groesse}")
        lay.set_font_description(schrift)
        if breite:
            lay.set_width(int(breite * Pango.SCALE))
            lay.set_wrap(Pango.WrapMode.WORD_CHAR)
        if markup:
            lay.set_markup(text, -1)
        else:
            lay.set_text(text, -1)
        return lay

    def zeigen(self, lay, x, y, farbe=(0, 0, 0)):
        self.stift.set_source_rgb(*farbe)
        self.stift.move_to(x, y)
        PangoCairo.show_layout(self.stift, lay)
        return lay.get_pixel_size()[1]

    def text(self, text, x, y, **k):
        farbe = k.pop("farbe", (0, 0, 0))
        return self.zeigen(self.layout(text, **k), x, y, farbe)


def zeilenhoehe(satz, groesse=GROESSE):
    return satz.layout("Hg", groesse).get_pixel_size()[1]


def erste_seite(satz, daten, pd, empfaenger, datum):
    """Briefkopf, Anschriftfeld, Informationsblock, Marken."""
    s = satz.stift
    grau = (0.35, 0.35, 0.35)
    # Briefkopf: Name gross, Anschrift in einer Zeile darunter.
    name = pd.voller_name(daten) if (pd and daten) else ""
    anschrift = pd.absenderzeilen(daten)[1:] if (pd and daten) else []
    if name:
        satz.text(name, RAND_LINKS, 17 * MM, groesse=16, fett=True)
    if anschrift:
        satz.text(" · ".join(anschrift), RAND_LINKS, 26 * MM, groesse=9, farbe=grau)

    # Anschriftfeld: Ruecksendeangabe unten in der Vermerkzone, darunter Empfaenger.
    if name or anschrift:
        # Ohne Land: Es passt sonst nicht in die 80 mm, und fuer die Ruecksendung
        # reicht Strasse und Ort (das Land steht im Briefkopf).
        ohne_land = [z for z in anschrift if not (daten.get("land") and z == daten["land"].upper())]
        ruecksende = " · ".join(([name] if name else []) + ohne_land)
        lay = satz.layout(ruecksende, groesse=7)
        lay.set_width(int(80 * MM * Pango.SCALE))
        lay.set_ellipsize(Pango.EllipsizeMode.END)
        hoehe = lay.get_pixel_size()[1]
        satz.zeigen(lay, 25 * MM, (45 + 17.7) * MM - hoehe - 1 * MM, grau)
        s.set_source_rgb(*grau)
        s.set_line_width(0.3)
        s.move_to(25 * MM, (45 + 17.7) * MM - 0.8 * MM)
        s.line_to(25 * MM + min(lay.get_pixel_size()[0], 80 * MM), (45 + 17.7) * MM - 0.8 * MM)
        s.stroke()
    y = (45 + 17.7) * MM + 1 * MM
    for zeile in (empfaenger or [])[:9]:
        y += satz.text(zeile, 25 * MM, y, groesse=10)

    # Informationsblock.
    zeilen = []
    if daten:
        if name:
            zeilen.append(("Name", name))
        for schluessel, wort in (("festnetz_privat", "Telefon"), ("handy_privat", "Mobil"),
                                 ("mail", "E-Mail")):
            if daten.get(schluessel):
                zeilen.append((wort, daten[schluessel]))
    zeilen.append(("Datum", datum))
    y = 50 * MM
    for wort, wert in zeilen:
        satz.text(wort, 125 * MM, y, groesse=8, farbe=grau)
        y += satz.text(wert, 145 * MM, y, groesse=9, breite=45 * MM)
        y += 0.8 * MM

    # Falz- und Lochmarken am linken Rand.
    s.set_source_rgb(0.5, 0.5, 0.5)
    s.set_line_width(0.4)
    for hoehe, laenge in ((105, 5), (148.5, 8), (210, 5)):
        s.move_to(3 * MM, hoehe * MM)
        s.line_to((3 + laenge) * MM, hoehe * MM)
        s.stroke()


def fusszeile(satz, seite, seiten):
    fuss = holen(FUSSZEILE_SKRIPT, "fusszeile")
    text = fuss.text("dokument") if fuss else \
        "Dieses Dokument wurde per Spracheingabe powered by DialOS.org erstellt!"
    grau = (0.45, 0.45, 0.45)
    satz.text(text, RAND_LINKS, 287 * MM, groesse=7, farbe=grau)
    if seiten > 1:
        lay = satz.layout(f"Seite {seite} von {seiten}", groesse=7)
        satz.zeigen(lay, SEITE_B - RAND_RECHTS - lay.get_pixel_size()[0], 287 * MM, grau)


def bausteine(satz, betreff, absaetze, gruss, name, unterschrift_bild):
    """Alles ab dem Betreff als Folge von (art, layout_oder_bild, abstand_davor)."""
    zeile = zeilenhoehe(satz)
    teile = []
    if betreff:
        teile.append(("layout", satz.layout(betreff, fett=True, breite=TEXTBREITE), 0))
    for nummer, absatz in enumerate(absaetze):
        # Zwei Leerzeilen nach dem Betreff, eine zwischen Absaetzen.
        abstand = (2 * zeile if nummer == 0 and betreff else (zeile if nummer else 0))
        for i, z in enumerate(absatz):
            teile.append(("layout", satz.layout(z, breite=TEXTBREITE), abstand if i == 0 else 0))
    if gruss:
        teile.append(("layout", satz.layout(gruss, breite=TEXTBREITE), zeile))
        if unterschrift_bild:
            teile.append(("bild", unterschrift_bild, 0.5 * zeile))
            abstand_name = 0
        else:
            abstand_name = 3 * zeile
        if name:
            teile.append(("layout", satz.layout(name, breite=TEXTBREITE), abstand_name))
        if not unterschrift_bild:
            teile.append(("layout", satz.layout(UNTERSCHRIFT_HINWEIS, groesse=8,
                                                breite=TEXTBREITE), zeile))
    return teile


def unterschrift_laden(daten):
    pfad = (daten or {}).get("unterschrift_bild")
    if not pfad or not pfad.lower().endswith(".png") or not os.path.isfile(pfad):
        return None
    try:
        return cairo.ImageSurface.create_from_png(pfad)
    except Exception:
        return None


def zeichnen(flaeche_neu, text, daten=None, empfaenger=None, datum=None):
    """Setzt den Brief. flaeche_neu(seite) liefert je Seite (flaeche, stift, fertig)."""
    pd = holen(PERSOENLICHE_DATEN_SKRIPT, "persoenliche_daten")
    datum = datum or datetime.date.today().strftime("%d.%m.%Y")
    betreff, absaetze, gruss, name = zerlegen(text)
    if daten and pd:
        name = pd.unterschrift_name(daten) or name
    bild = unterschrift_laden(daten)

    # Erst messen, dann setzen: Fuer "Seite 1 von 2" muss die Seitenzahl vorher stehen.
    teile = bausteine(Satz(None), betreff, absaetze, gruss, name, bild)
    platzierung, seite, y = [], 1, 98.5 * MM
    # GRUSS, NAME UND HINWEIS BLEIBEN ZUSAMMEN: Ein "Mit freundlichen Gruessen"
    # allein unten auf der Seite und der Name oben auf der naechsten waere falsch.
    schluss_ab = next((i for i, t in enumerate(teile) if t[0] == "layout"
                       and gruss and t[1].get_text() == gruss), None)
    if schluss_ab is not None:
        schluss_hoehe = sum(t[2] + (t[1].get_pixel_size()[1] if t[0] == "layout" else 15 * MM)
                            for t in teile[schluss_ab:])
    for nummer, (art, inhalt, abstand) in enumerate(teile):
        if nummer == schluss_ab and y + schluss_hoehe > FUSS_OBEN:
            seite, y, abstand = seite + 1, FOLGESEITE_OBEN, 0
        if art == "layout":
            klein = inhalt.get_font_description().get_size() < 10 * Pango.SCALE
            for i in range(inhalt.get_line_count()):
                zeile = inhalt.get_line_readonly(i)
                _, logisch = zeile.get_pixel_extents()
                vor = abstand if i == 0 else 0
                if y + vor + logisch.height > FUSS_OBEN:
                    seite, y, vor = seite + 1, FOLGESEITE_OBEN, 0
                y += vor
                platzierung.append((seite, "zeile", (zeile, logisch.y, klein), y))
                y += logisch.height
        else:
            h = 15 * MM
            if y + abstand + h > FUSS_OBEN:
                seite, y, abstand = seite + 1, FOLGESEITE_OBEN, 0
            y += abstand
            platzierung.append((seite, "bild", (inhalt, h), y))
            y += h
    seiten = seite

    for nr in range(1, seiten + 1):
        flaeche, stift, fertig = flaeche_neu(nr)
        satz = Satz(stift)
        if nr == 1:
            erste_seite(satz, daten, pd, empfaenger, datum)
        for s_nr, art, was, y in platzierung:
            if s_nr != nr:
                continue
            if art == "bild":
                bild_flaeche, h = was
                skala = h / bild_flaeche.get_height()
                stift.save()
                stift.translate(RAND_LINKS, y)
                stift.scale(skala, skala)
                stift.set_source_surface(bild_flaeche, 0, 0)
                stift.paint()
                stift.restore()
                continue
            zeile, oben, klein = was
            grau = 0.3 if klein else 0
            stift.set_source_rgb(grau, grau, grau)
            # show_layout_line setzt auf die Grundlinie: logisch.y ist negativ.
            stift.move_to(RAND_LINKS, y - oben)
            PangoCairo.show_layout_line(stift, zeile)
        fusszeile(satz, nr, seiten)
        fertig()
    return seiten


def als_pdf(text, ziel, daten=None, empfaenger=None, datum=None):
    flaeche = cairo.PDFSurface(ziel, SEITE_B, SEITE_H)
    stift = cairo.Context(flaeche)

    def neu(seite):
        return flaeche, stift, flaeche.show_page
    seiten = zeichnen(neu, text, daten, empfaenger, datum)
    flaeche.finish()
    return seiten


def als_png(text, ziel, daten=None, empfaenger=None, datum=None, dpi=110):
    """Vorschau aller Seiten nebeneinander - nur zum Ansehen."""
    faktor = dpi / 72
    bilder = []

    def neu(seite):
        flaeche = cairo.ImageSurface(cairo.FORMAT_RGB24, int(SEITE_B * faktor), int(SEITE_H * faktor))
        stift = cairo.Context(flaeche)
        stift.set_source_rgb(1, 1, 1)
        stift.paint()
        stift.scale(faktor, faktor)
        bilder.append(flaeche)
        return flaeche, stift, lambda: None
    zeichnen(neu, text, daten, empfaenger, datum)
    breite = sum(b.get_width() for b in bilder) + 20 * (len(bilder) - 1)
    gesamt = cairo.ImageSurface(cairo.FORMAT_RGB24, breite, bilder[0].get_height())
    stift = cairo.Context(gesamt)
    stift.set_source_rgb(0.8, 0.8, 0.8)
    stift.paint()
    x = 0
    for b in bilder:
        stift.set_source_surface(b, x, 0)
        stift.paint()
        x += b.get_width() + 20
    gesamt.write_to_png(ziel)


def main():
    argumente = sys.argv[1:]
    optionen = {}
    for schalter in ("--empfaenger", "--daten", "--png", "--datum"):
        if schalter in argumente:
            i = argumente.index(schalter)
            optionen[schalter] = argumente[i + 1]
            del argumente[i:i + 2]
    if len(argumente) != 2:
        print(__doc__)
        return 2
    with open(argumente[0], encoding="utf-8") as f:
        text = f.read()
    if "powered by DialOS" in text or "Dieser Brief wurde per Spracheingabe" in text:
        text = aus_briefbogen(text)
    pd = holen(PERSOENLICHE_DATEN_SKRIPT, "persoenliche_daten")
    daten = pd.lesen(optionen.get("--daten")) if pd else {}
    empfaenger = optionen["--empfaenger"].split("|") if "--empfaenger" in optionen else None
    seiten = als_pdf(text, argumente[1], daten, empfaenger, optionen.get("--datum"))
    if "--png" in optionen:
        als_png(text, optionen["--png"], daten, empfaenger, optionen.get("--datum"))
    print(f"{argumente[1]}: {seiten} Seite(n)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
