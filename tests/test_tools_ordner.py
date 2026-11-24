#!/usr/bin/env python3
"""
Jedes DialOS-Werkzeug liegt im Menue-Ordner "DialOS Tools" (Stephan,
2026-11-24). Der Ordner sammelt nach der Kategorie X-DialOS-Tools - fehlt sie
an einem neuen Werkzeug, steht es wieder lose im Menue. Dieser Test merkt es.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import configparser
import glob
import os
import unittest

WURZEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot")


class ToolsOrdner(unittest.TestCase):

    def test_jedes_werkzeug_traegt_die_kategorie(self):
        dateien = glob.glob(os.path.join(WURZEL, "usr", "share", "applications",
                                         "dialos-*.desktop"))
        self.assertTrue(dateien)
        for pfad in dateien:
            c = configparser.RawConfigParser(strict=False)
            c.read(pfad, encoding="utf-8")
            eintrag = c["Desktop Entry"]
            if eintrag.get("NoDisplay", "false").lower() == "true":
                continue
            with self.subTest(datei=os.path.basename(pfad)):
                self.assertIn("X-DialOS-Tools", eintrag.get("Categories", "").split(";"))

    def test_ordner_sammelt_nach_derselben_kategorie(self):
        with open(os.path.join(WURZEL, "usr", "local", "bin", "dialos-tools-ordner.sh"),
                  encoding="utf-8") as f:
            skript = f.read()
        self.assertIn("categories \"['X-DialOS-Tools']\"", skript)
        self.assertIn('name "DialOS Tools"', skript)
        self.assertTrue(os.path.exists(os.path.join(
            WURZEL, "etc", "xdg", "autostart", "dialos-tools-ordner.desktop")))


if __name__ == "__main__":
    unittest.main()
