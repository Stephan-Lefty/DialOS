#!/usr/bin/env python3
"""DialOS: Hintergrundbild nach der Jahreszeit am Wohnort.

Stephan am 2026-09-16: "etwas Schwung in unser Wallpaper bringen" - vier Bilder
desselben Bergsees in Fruehling, Sommer, Herbst und Winter, und wenn die
Jahreszeit am Heimatort wechselt, wechselt das Bild von selbst.

KALENDARISCH, NICHT METEOROLOGISCH (Stephans Wahl): Der Fruehling beginnt mit
der Tagundnachtgleiche um den 20. Maerz, nicht am 1. Maerz. Die vier Zeitpunkte
werden jedes Jahr berechnet (Jean Meeus, "Astronomical Algorithms", Kap. 27:
Naeherung plus 24 periodische Glieder, genau auf wenige Minuten) und in der
Zeitzone des Geraets verglichen. Eine feste Datumstabelle waere um einen Tag
falsch, sobald der Beginn um Mitternacht herum liegt, und liefe irgendwann ab.

HEIMATORT: Auf der Suedhalbkugel sind die Jahreszeiten vertauscht. Das Land kommt
aus den persoenlichen Daten (~/.config/dialos/persoenliche-daten.txt); ohne
Angabe gilt die Nordhalbkugel - DialOS wird in Deutschland und Oesterreich
eingerichtet.

HELL UND DUNKEL (Stephans Wahl: "Auch Jahreszeit"): Beide Modi zeigen die
Jahreszeit. Gibt es wallpaper-<jahreszeit>-dark.png, nimmt der dunkle Modus
dieses Bild, sonst das helle.

EIN EIGENES BILD BLEIBT: Gewechselt wird nur, wenn gerade ein DialOS-Bild aus
/usr/share/backgrounds/dialos eingestellt ist. Wer ein Foto der Enkel als
Hintergrund hat, verliert es nicht beim naechsten Jahreszeitwechsel.

Laeuft als Nutzerdienst: beim Anmelden und stuendlich (dialos-jahreszeit.timer).
Geaendert wird nur, wenn sich etwas aendert - kein Flackern.

Aufruf:
  dialos-jahreszeit.py              Bild setzen, falls noetig
  dialos-jahreszeit.py --zeigen     Jahreszeitbeginn dieses Jahres und aktuelle Wahl
  dialos-jahreszeit.py --zeitpunkt 2026-12-21T12:00   Wahl fuer einen Zeitpunkt pruefen
"""

import datetime
import math
import os
import subprocess
import sys

ORDNER = "/usr/share/backgrounds/dialos"
SCHEMA = "org.gnome.desktop.background"
PERSOENLICHE_DATEN_SKRIPT = "/usr/local/bin/dialos-persoenliche-daten.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-jahreszeit.log")
JAHRESZEITEN = ("fruehling", "sommer", "herbst", "winter")
NAMEN = {"fruehling": "Frühling", "sommer": "Sommer", "herbst": "Herbst", "winter": "Winter"}
# Laender der Suedhalbkugel, so wie sie im Formular stehen koennten.
SUEDHALBKUGEL = {"australien", "neuseeland", "südafrika", "suedafrika", "argentinien", "chile",
                 "uruguay", "paraguay", "bolivien", "peru", "brasilien", "namibia", "botswana",
                 "simbabwe", "mosambik", "madagaskar", "lesotho", "eswatini", "sambia",
                 "angola", "malawi", "mauritius", "fidschi"}

# Meeus Tabelle 27.C (Jahre 2000-3000): mittlere Zeitpunkte als JDE, Y = (Jahr-2000)/1000
MITTEL = (
    (2451623.80984, 365242.37404, 0.05169, -0.00411, -0.00057),   # Maerz
    (2451716.56767, 365241.62603, 0.00325, 0.00888, -0.00030),    # Juni
    (2451810.21715, 365242.01767, -0.11575, 0.00337, 0.00078),    # September
    (2451900.05952, 365242.74049, -0.06223, -0.00823, 0.00032),   # Dezember
)
# Meeus Tabelle 27.B: A, B, C fuer S = Summe A*cos(B + C*T)
GLIEDER = (
    (485, 324.96, 1934.136), (203, 337.23, 32964.467), (199, 342.08, 20.186),
    (182, 27.85, 445267.112), (156, 73.14, 45036.886), (136, 171.52, 22518.443),
    (77, 222.54, 65928.934), (74, 296.72, 3034.906), (70, 243.58, 9037.513),
    (58, 119.81, 33718.147), (52, 297.17, 150.678), (50, 21.02, 2281.226),
    (45, 247.54, 29929.562), (44, 325.15, 31555.956), (29, 60.93, 4443.417),
    (18, 155.12, 67555.328), (17, 288.79, 4562.452), (16, 198.04, 62894.029),
    (14, 199.76, 31436.921), (12, 95.39, 14577.848), (12, 287.11, 31931.756),
    (12, 320.81, 34777.259), (9, 227.73, 1222.114), (8, 15.45, 16859.074),
)


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%m-%d %H:%M:%S} {text}\n")
    except OSError:
        pass


def beginn(jahr, nummer):
    """Beginn der Jahreszeit nummer (0=Maerz ... 3=Dezember) als UTC-Zeitpunkt."""
    y = (jahr - 2000) / 1000
    a, b, c, d, e = MITTEL[nummer]
    jde0 = a + b * y + c * y ** 2 + d * y ** 3 + e * y ** 4
    t = (jde0 - 2451545.0) / 36525
    w = math.radians(35999.373 * t - 2.47)
    dl = 1 + 0.0334 * math.cos(w) + 0.0007 * math.cos(2 * w)
    s = sum(ga * math.cos(math.radians(gb + gc * t)) for ga, gb, gc in GLIEDER)
    jde = jde0 + 0.00001 * s / dl
    # JDE ist Terrestrische Zeit; der Abstand zu UTC (rund 70 s) spielt fuer ein
    # Hintergrundbild keine Rolle.
    return (datetime.datetime(2000, 1, 1, 12, tzinfo=datetime.timezone.utc)
            + datetime.timedelta(days=jde - 2451545.0))


def jahreszeit_nord(zeitpunkt):
    """Jahreszeit auf der Nordhalbkugel fuer einen Zeitpunkt mit Zeitzone."""
    jahr = zeitpunkt.year
    if zeitpunkt < beginn(jahr, 0):
        return "winter"
    if zeitpunkt < beginn(jahr, 1):
        return "fruehling"
    if zeitpunkt < beginn(jahr, 2):
        return "sommer"
    if zeitpunkt < beginn(jahr, 3):
        return "herbst"
    return "winter"


def suedhalbkugel():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("persoenliche_daten", PERSOENLICHE_DATEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        land = modul.lesen().get("land", "")
    except Exception:
        return False
    return land.strip().lower() in SUEDHALBKUGEL


def jahreszeit(zeitpunkt, sued=False):
    nord = jahreszeit_nord(zeitpunkt)
    if not sued:
        return nord
    return JAHRESZEITEN[(JAHRESZEITEN.index(nord) + 2) % 4]


def bilder(zeit):
    hell = os.path.join(ORDNER, f"wallpaper-{zeit}.png")
    dunkel = os.path.join(ORDNER, f"wallpaper-{zeit}-dark.png")
    if not os.path.exists(dunkel):
        dunkel = hell
    return "file://" + hell, "file://" + dunkel


def gsettings_lesen(schluessel):
    ergebnis = subprocess.run(["gsettings", "get", SCHEMA, schluessel],
                              capture_output=True, text=True, timeout=10)
    return ergebnis.stdout.strip().strip("'")


def setzen(zeitpunkt):
    zeit = jahreszeit(zeitpunkt, suedhalbkugel())
    hell, dunkel = bilder(zeit)
    if not os.path.exists(hell[len("file://"):]):
        melde(f"Bild fehlt: {hell}")
        return 1
    jetzt_hell = gsettings_lesen("picture-uri")
    jetzt_dunkel = gsettings_lesen("picture-uri-dark")
    eigenes = [u for u in (jetzt_hell, jetzt_dunkel)
               if u and not u.startswith("file://" + ORDNER + "/")]
    if eigenes:
        # Ein selbst gewaehltes Bild bleibt unangetastet.
        return 0
    if (jetzt_hell, jetzt_dunkel) == (hell, dunkel):
        return 0
    subprocess.run(["gsettings", "set", SCHEMA, "picture-uri", hell], timeout=10)
    subprocess.run(["gsettings", "set", SCHEMA, "picture-uri-dark", dunkel], timeout=10)
    melde(f"Hintergrund: {NAMEN[zeit]} ({hell})")
    return 0


def main():
    jetzt = datetime.datetime.now().astimezone()
    if "--zeitpunkt" in sys.argv:
        i = sys.argv.index("--zeitpunkt")
        jetzt = datetime.datetime.fromisoformat(sys.argv[i + 1])
        if jetzt.tzinfo is None:
            jetzt = jetzt.astimezone()
        print(f"{jetzt:%Y-%m-%d %H:%M}: {NAMEN[jahreszeit(jetzt, suedhalbkugel())]}")
        return 0
    if "--zeigen" in sys.argv:
        for nummer, name in enumerate(("Frühling", "Sommer", "Herbst", "Winter")):
            print(f"{name:9s} beginnt {beginn(jetzt.year, nummer).astimezone():%d.%m.%Y %H:%M}")
        sued = suedhalbkugel()
        print(f"Jetzt: {NAMEN[jahreszeit(jetzt, sued)]}"
              f"{' (Südhalbkugel)' if sued else ''} -> {bilder(jahreszeit(jetzt, sued))[0]}")
        return 0
    return setzen(jetzt)


if __name__ == "__main__":
    sys.exit(main())
