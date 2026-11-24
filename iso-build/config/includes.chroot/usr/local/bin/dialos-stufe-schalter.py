#!/usr/bin/env python3
"""DialOS: die Unterstützungsstufe per Mausklick wählen.

Stephan, 2026-11-24: „Der Umschalter funktioniert nur per Spracheingabe,
oder können wir optional ein kleines Tool wie einen Schalter fertig machen?
Dann könnte man das auch mal ausprobieren!"

Ein Fenster mit den vier Stufen. Ein Klick setzt die Stufe über
dialos-stufe.py - also genau wie der Sprachbefehl, mit Michaels Ansage danach
und denselben Sehhilfen. Es gibt nur EINEN Weg, eine Stufe zu setzen; dieses
Fenster ist eine zweite Tür dazu, kein zweites Schloss.

Gilt für das angemeldete Konto.
"""

import os
import subprocess
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import dialos_stufe as st  # noqa: E402

STUFE_SKRIPT = os.path.join(HIER, "dialos-stufe.py")

UNTERTITEL = {
    0: "Begrüßung, Antworten auf Zuruf. Für alle, die gut sehen.",
    1: "Dazu große Schrift, starker Kontrast, großer Mauszeiger.",
    2: "Dazu Ansagen, wenn sich etwas ändert - Ton, Internet.",
    3: "Volle Unterstützung - DialOS ohne Bildschirm bedienbar.",
}


class Fenster(Adw.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app, title="DialOS Unterstützung")
        self.set_default_size(520, -1)
        self.knoepfe = {}

        gruppe = Adw.PreferencesGroup(
            title="Wie viel soll DialOS unterstützen?",
            description="Die Stufe gilt für dieses Konto. Nach jedem Wechsel "
                        "sagt Michael, was jetzt gilt. Per Sprache geht es mit "
                        "„mehr Unterstützung“ und „Unterstützung verringern“.")
        erster = None
        for stufe in range(st.NIEDRIGSTE, st.HOECHSTE + 1):
            knopf = Gtk.CheckButton()
            if erster is None:
                erster = knopf
            else:
                knopf.set_group(erster)
            zeile = Adw.ActionRow(title=st.NAMEN[stufe], subtitle=UNTERTITEL[stufe])
            zeile.add_prefix(knopf)
            zeile.set_activatable_widget(knopf)
            gruppe.add(zeile)
            self.knoepfe[stufe] = knopf

        self.knoepfe[st.stufe()].set_active(True)
        for stufe, knopf in self.knoepfe.items():
            knopf.connect("toggled", self.gewaehlt, stufe)

        seite = Adw.PreferencesPage()
        seite.add(gruppe)
        aufbau = Adw.ToolbarView()
        aufbau.add_top_bar(Adw.HeaderBar())
        aufbau.set_content(seite)
        self.set_content(aufbau)

    def gewaehlt(self, knopf, stufe):
        # "toggled" kommt auch beim Abwaehlen - nur die neue Wahl zaehlt.
        if not knopf.get_active() or stufe == st.stufe():
            return
        subprocess.Popen([STUFE_SKRIPT, "setzen", str(stufe)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)


def main():
    app = Adw.Application(application_id="org.dialos.Stufe")
    app.connect("activate", lambda a: Fenster(a).present())
    return app.run([sys.argv[0]])


if __name__ == "__main__":
    sys.exit(main())
