#!/usr/bin/env python3
"""DialOS: Bildschirmfoto auf Zuruf.

Stephans Wunsch vom 2026-08-21. Der Nutzer sieht den Bildschirm nicht - das
Foto ist deshalb nicht fuer ihn, sondern fuer den SEHENDEN HELFER und fuer den
Support: "Was steht da gerade?" laesst sich sonst nicht beantworten, ohne dass
jemand danebensitzt.

WARUM UEBER DAS PORTAL UND NICHT MIT EINEM WERKZEUG. Auf diesem Geraet ist
KEIN Bildschirmfoto-Werkzeug installiert (geprueft am 2026-08-21:
gnome-screenshot, grim, scrot, spectacle, flameshot - alle nicht da; xwd ist
X11 und unter Wayland nutzlos). Und die naheliegende Schnittstelle der
GNOME-Shell ist gesperrt:

    org.gnome.Shell.Screenshot.Screenshot
      -> GDBus.Error:...AccessDenied: Screenshot is not allowed

Uebrig bleibt das XDG-Portal, und das ist ohnehin der vorgesehene Weg. Mit
"interactive: false" liefert es das Bild OHNE Rueckfrage - geprueft, Antwort-
code 0. Das ist die entscheidende Eigenschaft: Ein Dialog, den der Nutzer
bestaetigen muesste, waere auf diesem Geraet dasselbe wie gar keine Funktion.

DER NAME KOMMT VON UNS, nicht vom Portal. Das Portal legt "Screenshot.png" an
und zaehlt hoch ("Screenshot-1.png"). Wer im Support drei Bilder bekommt, will
wissen, welches wann entstand - deshalb Datum und Uhrzeit im Namen, und ab in
den Ordner "Bildschirmfotos", den GNOME dafuer ohnehin vorsieht.

Aufruf:
    dialos-bildschirmfoto.py           Foto machen, Ergebnis ansagen
    dialos-bildschirmfoto.py --still   ohne Ansage (fuer Skripte)
"""

import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
NAMEN_SKRIPT = "/usr/local/bin/dialos-namen.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-bildschirmfoto.log")
WARTEZEIT_S = 15.0

ANSAGE_FERTIG = "Das Bildschirmfoto ist gespeichert."
ANSAGE_FEHLER = "Ich konnte kein Bildschirmfoto machen."


# WARUM IN EINEM VERSTECKTEN ORDNER (Stephan, 2026-08-22): Vorher lagen die
# Protokolle offen im Heimatverzeichnis - zehn laufende und fuenfzehn gedrehte
# Fassungen, also 25 Dateien zwischen "Notizen", "Dokumente" und "Bilder". Der
# Nutzer sieht sie nicht, aber ein sehender Helfer sucht dazwischen. In "~/.log"
# stoeren sie niemanden und sind trotzdem da, wo man sie vermutet.
#
# Der Ordner wird beim Schreiben angelegt, nicht vorausgesetzt: Ein neues Konto
# hat ihn noch nicht, und ein fehlendes Protokoll darf keine Ansage aufhalten.
def melde(text):
    os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')}  {text}\n")
    except OSError:
        pass


def anrede(satz):
    """Nur fuer den Fehlerfall - siehe dialos-namen.py."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dialos_namen", NAMEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.anrede(satz)
    except Exception:
        return satz


def sprich(text):
    try:
        if os.access(SAY, os.X_OK):
            subprocess.run([SAY, text], capture_output=True, timeout=60)
        else:
            print(text, flush=True)
    except Exception as fehler:
        melde(f"Ansage fehlgeschlagen: {fehler}")


def bilderordner():
    try:
        p = subprocess.run(["xdg-user-dir", "PICTURES"],
                           capture_output=True, text=True, timeout=5)
        ziel = p.stdout.strip()
        if ziel and os.path.isdir(ziel):
            return ziel
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "Bilder")


def aufnehmen():
    """Ruft das Portal und gibt den Pfad der entstandenen Datei zurueck.

    Das Portal antwortet nicht auf den Aufruf, sondern spaeter mit einem
    Signal auf einem eigenen Objektpfad - deshalb der Umweg ueber die
    Hauptschleife. Der Pfad laesst sich vorher berechnen, sonst koennte man
    das Signal nicht abonnieren, bevor es kommt.
    """
    import gi
    gi.require_version("Gio", "2.0")
    from gi.repository import Gio, GLib

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    schleife = GLib.MainLoop()
    ergebnis = {}

    def antwort(conn, sender, pfad, iface, signal, params):
        code, daten = params.unpack()
        ergebnis["code"] = code
        ergebnis["uri"] = daten.get("uri", "")
        schleife.quit()

    marke = "dialos" + time.strftime("%H%M%S")
    eindeutig = bus.get_unique_name()[1:].replace(".", "_")
    pfad = f"/org/freedesktop/portal/desktop/request/{eindeutig}/{marke}"
    bus.signal_subscribe("org.freedesktop.portal.Desktop",
                         "org.freedesktop.portal.Request", "Response", pfad,
                         None, Gio.DBusSignalFlags.NONE, antwort)

    optionen = {"handle_token": GLib.Variant("s", marke),
                # OHNE Rueckfrage - siehe Kopf. Ein Dialog waere hier das
                # Ende der Funktion.
                "interactive": GLib.Variant("b", False),
                "modal": GLib.Variant("b", False)}
    bus.call_sync("org.freedesktop.portal.Desktop",
                  "/org/freedesktop/portal/desktop",
                  "org.freedesktop.portal.Screenshot", "Screenshot",
                  GLib.Variant("(sa{sv})", ("", optionen)),
                  None, Gio.DBusCallFlags.NONE, 5000, None)

    GLib.timeout_add_seconds(int(WARTEZEIT_S), lambda: (schleife.quit(), False)[1])
    schleife.run()

    if ergebnis.get("code") != 0:
        melde(f"Portal antwortete mit {ergebnis.get('code', 'gar nicht')}")
        return None
    uri = ergebnis.get("uri", "")
    if not uri.startswith("file://"):
        melde(f"unerwartete Antwort: {uri!r}")
        return None
    from urllib.parse import unquote, urlparse
    return unquote(urlparse(uri).path)


def einordnen(quelle):
    """Datum und Uhrzeit in den Namen, ab in den Bildschirmfoto-Ordner."""
    ordner = os.path.join(bilderordner(), "Bildschirmfotos")
    os.makedirs(ordner, exist_ok=True)
    ziel = os.path.join(ordner,
                        "bildschirmfoto-" + time.strftime("%Y-%m-%d-%H%M%S") + ".png")
    try:
        os.replace(quelle, ziel)
        return ziel
    except OSError as fehler:
        # Verschieben ueber Dateisystemgrenzen kann scheitern - dann bleibt
        # das Bild liegen, wo das Portal es hingelegt hat. Ein Foto am
        # falschen Ort ist besser als keins.
        melde(f"konnte nicht verschieben ({fehler}) - bleibt {quelle}")
        return quelle


def main():
    still = "--still" in sys.argv[1:]
    melde("=== Bildschirmfoto angefordert ===")
    try:
        quelle = aufnehmen()
    except Exception as fehler:
        melde(f"Portal nicht erreichbar: {fehler}")
        quelle = None
    if not quelle or not os.path.exists(quelle):
        melde("kein Bild entstanden")
        if not still:
            sprich(anrede(ANSAGE_FEHLER))
        return 1
    ziel = einordnen(quelle)
    groesse = os.path.getsize(ziel)
    melde(f"gespeichert: {ziel} ({groesse/1024:.0f} kB)")
    if not still:
        sprich(ANSAGE_FERTIG)
    print(ziel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
