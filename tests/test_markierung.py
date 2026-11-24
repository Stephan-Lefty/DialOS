#!/usr/bin/env python3
"""
Tests fuer "markierten Text vorlesen" (dialos-markierung.py und die
GNOME-Erweiterung dialos@dialos.org), seit 2026-11-24.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import json
import os
import unittest

WURZEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot")
BIN = os.path.join(WURZEL, "usr", "local", "bin")
ERWEITERUNG = os.path.join(WURZEL, "usr", "share", "gnome-shell", "extensions",
                           "dialos@dialos.org")


def _laden(datei, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, datei))
    modul = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(modul)
    return modul


class Text(unittest.TestCase):

    def setUp(self):
        self.m = _laden("dialos-markierung.py", "dialos_markierung_test")

    def test_gdbus_ausgabe_wird_gelesen(self):
        self.assertEqual(self.m.gvariant_text("('Hallo Welt',)\n"), "Hallo Welt")
        self.assertEqual(self.m.gvariant_text("(\"Stephan's Brief\",)\n"), "Stephan's Brief")
        self.assertEqual(self.m.gvariant_text("('',)\n"), "")
        self.assertEqual(self.m.gvariant_text("Unsinn"), "")

    def test_stuecke_bleiben_unter_der_grenze(self):
        # dialos-say spielt hoechstens 60 s - laengere Stuecke brechen ab.
        text = " ".join(f"Das ist Satz Nummer {i} mit ein paar Woertern." for i in range(80))
        teile = self.m.stuecke(text)
        self.assertGreater(len(teile), 1)
        self.assertTrue(all(len(t) <= self.m.STUECK_ZEICHEN for t in teile))
        self.assertEqual(" ".join(teile), text)

    def test_nie_mitten_im_wort(self):
        langer_satz = "wort " * 200
        for teil in self.m.stuecke(langer_satz.strip()):
            self.assertFalse(teil.startswith("ort"))
            self.assertTrue(all(w == "wort" for w in teil.split()))

    def test_sehr_lang_wird_angekuendigt_und_gekuerzt(self):
        text, gekuerzt = self.m.zum_vorlesen("a " * 5000)
        self.assertTrue(gekuerzt)
        self.assertLessEqual(len(text), self.m.HOECHSTENS_ZEICHEN)

    def test_nichts_markiert_wird_gesagt(self):
        gesagt = []
        self.m.sprich = gesagt.append
        self.m.melde = lambda t: None
        self.m.markierung_holen = lambda: "   "
        self.m.main()
        self.assertEqual(gesagt, [self.m.ANSAGE_LEER])

    def test_erweiterung_fehlt_wird_gesagt(self):
        gesagt = []
        self.m.sprich = gesagt.append
        self.m.markierung_holen = lambda: None
        self.assertEqual(self.m.main(), 1)
        self.assertEqual(gesagt, [self.m.ANSAGE_FEHLT])


class Verdrahtung(unittest.TestCase):

    def test_satz_in_grammatik_und_uebersicht(self):
        d = _laden("dialos-sprachbefehl-desktop.py", "dialos_sb_markierung_test")
        self.assertIn("markierten text vorlesen", d.BEFEHLSSAETZE)
        self.assertIn("markierten text vorlesen", d.MARKIERUNG_SAETZE)
        self.assertNotIn("markierten text vorlesen", d.befehle_ohne_uebersicht())

    def test_erweiterung_passt_zum_werkzeug(self):
        with open(os.path.join(ERWEITERUNG, "metadata.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["uuid"], "dialos@dialos.org")
        self.assertIn("48", meta["shell-version"])
        with open(os.path.join(ERWEITERUNG, "extension.js"), encoding="utf-8") as f:
            js = f.read()
        with open(os.path.join(BIN, "dialos-markierung.py"), encoding="utf-8") as f:
            py = f.read()
        for teil in ("org.dialos.Shell", "/org/dialos/Shell", "MarkierungLesen"):
            self.assertIn(teil, js)
            self.assertIn(teil, py)
        self.assertIn("St.ClipboardType.PRIMARY", js)

    def test_wird_beim_anmelden_eingeschaltet(self):
        with open(os.path.join(WURZEL, "etc", "xdg", "autostart",
                               "dialos-gnome-erweiterung.desktop"), encoding="utf-8") as f:
            self.assertIn("Exec=gnome-extensions enable dialos@dialos.org", f.read())


if __name__ == "__main__":
    unittest.main()
