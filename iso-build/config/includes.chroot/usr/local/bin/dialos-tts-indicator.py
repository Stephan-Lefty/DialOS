#!/usr/bin/env python3
"""DialOS: Statusleisten-Icon, das anzeigt, wenn gerade eine Sprachausgabe
laeuft (siehe dialos-say.py). Nuetzlich vor allem, wenn die Lautstaerke zu
leise eingestellt ist - eine sehende Person sieht dann trotzdem am
Panel-Icon, dass gerade etwas gesprochen wird/wurde.

Technik: Pollt regelmaessig eine Markierungsdatei (siehe
MARKIERUNGSDATEI), die dialos-say.py beim Start/Ende jeder Ansage
anlegt/loescht, und schaltet ein AppIndicator3-Icon im GNOME-Panel
entsprechend sichtbar/unsichtbar (IndicatorStatus ACTIVE/PASSIVE - kein
Neuerzeugen des Icons noetig, nur Sichtbarkeit umschalten).

VORAUSSETZUNG (noch nicht auf echter Hardware verifiziert):
- GNOME-Shell-Erweiterung "AppIndicator and KStatusNotifierItem Support"
  (Paket gnome-shell-extension-appindicator, UUID
  ubuntu-appindicators@ubuntu.com) muss aktiviert sein.
- python3-gi und die AppIndicator3-GObject-Introspection-Bindings muessen
  installiert sein (siehe Installationsblock/Kommentar unten).
"""
import os

import gi

gi.require_version("Gtk", "3.0")
try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
except ValueError:
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3
from gi.repository import GLib, Gtk

def markierungsdatei():
    """Muss exakt denselben Pfad liefern wie dialos-say.py.

    Pro Konto eigener Pfad - bis 2026-08-16 stand hier ein fester Name in
    /tmp, den sich alle Konten teilten. Folge (live beobachtet): nutzers
    Ansage legte die Datei an, und danach zeigte dialosadmins Panel
    dauerhaft das Sprechen-Icon, obwohl dort nichts sprach. Begruendung
    ausfuehrlich in dialos-say.py.
    """
    basis = os.environ.get("XDG_RUNTIME_DIR")
    if basis and os.path.isdir(basis):
        return os.path.join(basis, "dialos-sprachausgabe-aktiv")
    return f"/tmp/dialos-sprachausgabe-aktiv-{os.getuid()}"


MARKIERUNGSDATEI = markierungsdatei()
PRUEF_INTERVALL_MS = 200


class SprachausgabeIndikator:
    def __init__(self):
        self.indikator = AppIndicator3.Indicator.new(
            "dialos-sprachausgabe",
            "audio-speakers-symbolic",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indikator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        self.indikator.set_title("DialOS: Sprachausgabe aktiv")
        # AppIndicator3 braucht ein Menue, um zuverlaessig zu funktionieren -
        # ein leeres Menue reicht, wir wollen keine Klick-Interaktion.
        self.indikator.set_menu(Gtk.Menu())
        self.sichtbar = False
        GLib.timeout_add(PRUEF_INTERVALL_MS, self._pruefen)

    def _pruefen(self):
        aktiv = os.path.exists(MARKIERUNGSDATEI)
        if aktiv != self.sichtbar:
            self.indikator.set_status(
                AppIndicator3.IndicatorStatus.ACTIVE
                if aktiv
                else AppIndicator3.IndicatorStatus.PASSIVE
            )
            self.sichtbar = aktiv
        return True  # True = GLib-Timeout weiterlaufen lassen


if __name__ == "__main__":
    SprachausgabeIndikator()
    Gtk.main()
