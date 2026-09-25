#!/usr/bin/env python3
"""Setzt die Grafik "Von Debian 13 + GNOME zu DialOS" als SVG und PNG.

Stephan am 2026-09-25: eine Grafik, wie aus Debian 13/GNOME DialOS wird -
mit einer Erklaerung rechts neben jedem Schritt, in den DialOS-Farben und
der DialOS-Schrift, im Repo abgelegt.

WARUM EIN ERZEUGER STATT EINER GEZEICHNETEN DATEI: Die Schritte folgen
docs/installationsanleitung.md, und die aendert sich - allein am 2026-09-25
kamen drei Schritte dazu. Eine von Hand gezeichnete Grafik waere beim
naechsten Mal still veraltet. Aendert sich die Anleitung, werden hier die
SCHRITTE angepasst und die Grafik neu gesetzt.

FARBEN aus dem Markenblatt (assets/brand-sheet.png) und dem Webseiten-Theme:
Verlauf Blau -> Tuerkis -> Gruen, Schriftzug-Dunkelblau, das Web-Gruen
#04b484 und fuer Text das dunkle #027a5c (WCAG-Kontrast, siehe Theme-CSS).
Blau steht fuer Handarbeit, Gruen fuer Skripte, das Dunkelblau des
Schriftzugs fuer das Ergebnis.

SCHRIFT: Quicksand - rund und geometrisch wie der DialOS-Schriftzug, auf dem
Geraet installiert. Wo sie fehlt (etwa in GitHubs Vorschau), faellt die SVG
auf eine Groteskschrift zurueck; das PNG ist mit Quicksand gesetzt.

Aufruf:  dialos-grafik-aufbau.py   schreibt assets/debian-zu-dialos.{svg,png}
"""

import html
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.normpath(os.path.join(HIER, "..", "assets", "debian-zu-dialos"))

NAVY = "#0b1a2e"
TEXT = "#2b3440"
LEISE = "#5b6675"
RAHMEN = "#cfd6df"
PFEIL = "#8a94a3"
FARBEN = {
    # Fuellung, Rand, Titel, Untertitel
    "hand": ("#e8f0fc", "#1a66d6", "#0b3d8c", "#1a57b8"),
    "skript": ("#e6f7f1", "#04b484", "#025c46", "#027a5c"),
    "ziel": (NAVY, NAVY, "#ffffff", "#7fd9b8"),
}
SCHRIFT = "Quicksand, 'Nunito', 'Noto Sans', 'DejaVu Sans', sans-serif"

# (Abschnitt, [(Art, Titel, Untertitel, [Erklaerungszeilen])])
ABSCHNITTE = [
    ("Basis - von Hand", [
        ("hand", "Debian 13 + GNOME installieren", "Konto dialosadmin, Platz frei lassen", [
            "Aktuelles Debian 13 mit GNOME vom USB-Stick. Das erste Konto heißt genau",
            "dialosadmin - die Skripte verlassen sich darauf. Nur EFI und 100 GB fürs",
            "System anlegen, der Rest bleibt frei für die verschlüsselte Nutzer-Partition."]),
        ("hand", "Grundsystem aktualisieren", "apt update und apt upgrade", [
            "Der Installations-Stick ist oft Wochen alt. Sicherheitskorrekturen und ein",
            "neuer Kernel kommen erst so ins System - alles Weitere baut auf dem",
            "aktuellen Stand auf. Danach einmal neu starten."]),
        ("hand", "Claude-App einrichten", "aus Anthropics Paketquelle", [
            "Claude hilft beim Aufbau mit. Die App kommt aus der offiziellen",
            "Paketquelle von Anthropic; der Schlüssel wird vorher am Fingerabdruck",
            "geprüft. Sie dient der Einrichtung im Büro."]),
    ]),
    ("Aufbau - per Skript", [
        ("skript", "Grundaufbau", "Stimmen, Erkenner, alle DialOS-Dateien", [
            "Pakete, Branding, Autologin, die Stimmen Anna und Michael, Vosk für die",
            "Befehle, Parakeet fürs Diktat, LanguageTool. Zum Schluss kommen alle",
            "DialOS-Dateien aufs Gerät, und die Dienste laufen für jedes Konto."]),
        ("skript", "Verschlüsselung", "nutzer-Partition, Swap, Sicherheits-Stick", [
            "Im freien Platz entstehen der verschlüsselte Swap und die Partition für",
            "die Daten des Nutzers. Der Schlüssel liegt auf dem Sicherheits-Stick -",
            "ohne Stick bleibt das Konto zu. Der Stick wird dabei neu angelegt."]),
        ("skript", "Nutzerkonto und Abschluss", "Konto nutzer, Autologin, erste Prüfung", [
            "Legt das Konto des Nutzers an, lässt es sich automatisch anmelden und",
            "öffnet die Maske für die persönlichen Daten. Am Ende prüft das Skript",
            "selbst, ob Gerät und Repository übereinstimmen."]),
        ("skript", "Aufräumen und Menü", "Unnötiges weg, Menü je Konto", [
            "Entfernt, was Debian mitbringt und DialOS nicht braucht - der Desktop",
            "wird vorher geschützt. Im Konto des Nutzers zeigt das Menü danach nur",
            "noch die DialOS-Programme; das Admin-Konto sieht weiter alles."]),
    ]),
    ("Einrichten und abnehmen", [
        ("hand", "Persönliche Daten und Mailkonto", "eine Maske für alles", [
            "Name, Anschrift, Telefon, Wetter-Ort und das Mailkonto samt Passwort.",
            "DialOS verteilt die Angaben an Brief, Wetter, Signatur und Thunderbird.",
            "Das Passwort liegt nur in Thunderbirds verschlüsseltem Speicher."]),
        ("skript", "Abnahme", "Prüfskripte und Sprachtest", [
            "Zwei Prüfskripte vergleichen Gerät und Repository und suchen Lücken im",
            "Konto des Nutzers. Dann der Sprachtest: „Sprachsteuerung starten“,",
            "„Wie spät ist es“, „Postfach öffnen“, „Brief schreiben“."]),
    ]),
]
ZIELSCHRITT = ("ziel", "DialOS 0.5.3", "Sprachsteuerung für beide Konten", [
    "Blinde und motorisch eingeschränkte Menschen bedienen den Rechner mit der",
    "Stimme - Briefe, Mails, Notizen, Suche, Uhrzeit und Wetter. Zum Schluss",
    "ein Rescuezilla-Abbild der Platte als Rückweg."])

BREITE = 1140
KX, KB, KH = 70, 340, 60        # Kasten: x, Breite, Hoehe
EX = KX + KB + 44               # Erklaerungsspalte
ZEILE = 20                      # Zeilenabstand der Erklaerung
ABSTAND = 26                    # zwischen zwei Kaesten
HOECHSTENS = 86                 # Zeichen je Erklaerungszeile


def t(s):
    return html.escape(s, quote=False)


def kasten(y, art, titel, unter, zeilen, teile):
    fuell, rand, tf, uf = FARBEN[art]
    mitte = y + KH / 2
    teile.append(f'<rect x="{KX}" y="{y}" width="{KB}" height="{KH}" rx="10" '
                 f'fill="{fuell}" stroke="{rand}" stroke-width="1.2"/>')
    teile.append(f'<text x="{KX + KB / 2}" y="{mitte - 10}" text-anchor="middle" '
                 f'dominant-baseline="central" font-size="17" font-weight="700" '
                 f'fill="{tf}">{t(titel)}</text>')
    teile.append(f'<text x="{KX + KB / 2}" y="{mitte + 12}" text-anchor="middle" '
                 f'dominant-baseline="central" font-size="13.5" font-weight="500" '
                 f'fill="{uf}">{t(unter)}</text>')
    # Erklaerung: senkrecht mittig zum Kasten
    start = mitte - (len(zeilen) - 1) * ZEILE / 2
    for i, z in enumerate(zeilen):
        if len(z) > HOECHSTENS:
            sys.exit(f"Erklaerungszeile zu lang ({len(z)} Zeichen): {z}")
        teile.append(f'<text x="{EX}" y="{start + i * ZEILE}" dominant-baseline="central" '
                     f'font-size="14.5" font-weight="500" fill="{TEXT}">{t(z)}</text>')
    # feine Verbindung Kasten -> Erklaerung
    teile.append(f'<line x1="{KX + KB + 8}" y1="{mitte}" x2="{EX - 12}" y2="{mitte}" '
                 f'stroke="{rand}" stroke-width="1" stroke-dasharray="2 4"/>')


def pfeil(y1, y2, teile):
    x = KX + KB / 2
    teile.append(f'<line x1="{x}" y1="{y1 + 3}" x2="{x}" y2="{y2 - 5}" stroke="{PFEIL}" '
                 f'stroke-width="1.4" marker-end="url(#spitze)"/>')


def os_lage():
    """Wo "OS" im Titel steht - gemessen mit Pango in derselben Schrift."""
    import gi
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo
    import cairo
    lay = PangoCairo.create_layout(cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)))
    lay.set_font_description(Pango.FontDescription.from_string("Quicksand Bold 32px"))
    vor = "Von Debian 13 + GNOME zu Dial"
    lay.set_text(vor, -1)
    x1 = 40 + lay.get_pixel_size()[0]
    lay.set_text(vor + "OS", -1)
    x2 = 40 + lay.get_pixel_size()[0]
    return x1, x2


def svg_bauen():
    teile = []
    y = 150
    letzter_unten = None
    for name, schritte in ABSCHNITTE:
        oben = y
        y += 42
        for i, (art, titel, unter, zeilen) in enumerate(schritte):
            if letzter_unten is not None:
                pfeil(letzter_unten, y, teile)
            kasten(y, art, titel, unter, zeilen, teile)
            letzter_unten = y + KH
            y += KH + (ABSTAND if i < len(schritte) - 1 else 0)
        unten = y + 18
        teile.insert(0, f'<rect x="40" y="{oben}" width="{BREITE - 80}" height="{unten - oben}" '
                        f'rx="14" fill="none" stroke="{RAHMEN}" stroke-width="1" '
                        f'stroke-dasharray="5 5"/>'
                        f'<text x="{EX}" y="{oben + 22}" dominant-baseline="central" '
                        f'font-size="14" font-weight="700" fill="{LEISE}">{t(name)}</text>')
        y = unten + 34
    pfeil(letzter_unten, y, teile)
    kasten(y, *ZIELSCHRITT, teile)
    y += KH + 44
    # Legende
    lx = KX
    for art, text in (("hand", "von Hand"), ("skript", "per Skript"), ("ziel", "Ergebnis")):
        fuell, rand, _, _ = FARBEN[art]
        teile.append(f'<rect x="{lx}" y="{y - 8}" width="16" height="16" rx="4" '
                     f'fill="{fuell}" stroke="{rand}" stroke-width="1.2"/>')
        teile.append(f'<text x="{lx + 24}" y="{y}" dominant-baseline="central" '
                     f'font-size="14" font-weight="500" fill="{LEISE}">{text}</text>')
        lx += 150
    teile.append(f'<text x="{BREITE - 40}" y="{y}" text-anchor="end" dominant-baseline="central" '
                 f'font-size="13" font-weight="500" fill="{LEISE}">'
                 f'Nach docs/installationsanleitung.md · dialos.org</text>')
    hoehe = int(y + 40)

    OS_X1, OS_X2 = os_lage()
    kopf = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{BREITE}" height="{hoehe}" viewBox="0 0 {BREITE} {hoehe}" role="img" font-family="{SCHRIFT}">
<title>Von Debian 13 + GNOME zu DialOS 0.5.3</title>
<desc>Aufbau eines DialOS-Geräts in drei Abschnitten - Basis von Hand, Aufbau per Skript, Einrichten und abnehmen - mit einer Erklärung zu jedem Schritt.</desc>
<defs>
<linearGradient id="marke" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#0a5fd6"/><stop offset="0.5" stop-color="#0f9fb0"/><stop offset="1" stop-color="#5cbf2a"/>
</linearGradient>
<!-- Verlauf fuer "OS" in Nutzer-Koordinaten: bezogen auf die ganze Zeile
     kam bei den zwei Buchstaben nur das gruene Ende an (2026-09-25 gesehen). -->
<linearGradient id="marke-os" gradientUnits="userSpaceOnUse" x1="{OS_X1}" y1="0" x2="{OS_X2}" y2="0">
<stop offset="0" stop-color="#0a5fd6"/><stop offset="0.5" stop-color="#0f9fb0"/><stop offset="1" stop-color="#5cbf2a"/>
</linearGradient>
<marker id="spitze" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="{PFEIL}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect width="{BREITE}" height="{hoehe}" fill="#ffffff"/>
<text x="40" y="62" font-size="32" font-weight="700" fill="{NAVY}">Von Debian 13 + GNOME zu Dial<tspan id="os" fill="url(#marke-os)">OS</tspan></text>
<text x="40" y="98" font-size="16" font-weight="500" fill="{LEISE}">So wird aus einem frisch installierten Debian ein Rechner, der sich mit der Stimme bedienen lässt.</text>
<rect x="40" y="116" width="{BREITE - 80}" height="4" rx="2" fill="url(#marke)"/>
'''
    return kopf + "\n".join(teile) + "\n</svg>\n", hoehe


def png_setzen(svg_pfad, png_pfad, hoehe):
    import cairo
    import gi
    gi.require_version("Rsvg", "2.0")
    from gi.repository import Rsvg
    handle = Rsvg.Handle.new_from_file(svg_pfad)
    massstab = 2
    flaeche = cairo.ImageSurface(cairo.FORMAT_ARGB32, BREITE * massstab, hoehe * massstab)
    stift = cairo.Context(flaeche)
    ansicht = Rsvg.Rectangle()
    ansicht.x, ansicht.y = 0, 0
    ansicht.width, ansicht.height = BREITE * massstab, hoehe * massstab
    handle.render_document(stift, ansicht)
    flaeche.write_to_png(png_pfad)


def main():
    svg, hoehe = svg_bauen()
    with open(ZIEL + ".svg", "w", encoding="utf-8") as f:
        f.write(svg)
    png_setzen(ZIEL + ".svg", ZIEL + ".png", hoehe)
    print(f"{ZIEL}.svg und .png - {BREITE} x {hoehe}")


if __name__ == "__main__":
    main()
