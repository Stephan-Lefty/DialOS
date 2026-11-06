#!/usr/bin/env python3
"""
Tests fuer die Lizenzuebersicht am Geraet ("lizenzen vorlesen").

Parakeet steht unter CC-BY-4.0 und verlangt Namensnennung. Seit dem
2026-11-06 liegt die Uebersicht unter /usr/share/doc/dialos/lizenzen.txt,
DialOS liest sie auf Zuruf vor, und der Helfer oeffnet sie ueber
"DialOS Lizenzen" im Menue.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import os
import unittest

WURZEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot")
BIN = os.path.join(WURZEL, "usr", "local", "bin")
TEXT = os.path.join(WURZEL, "usr", "share", "doc", "dialos", "lizenzen.txt")


def _laden(datei, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, datei))
    modul = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(modul)
    return modul


class Text(unittest.TestCase):

    def setUp(self):
        with open(TEXT, encoding="utf-8") as f:
            self.inhalt = f.read()

    def test_namensnennung_fuer_parakeet(self):
        # Was CC-BY-4.0 verlangt: Urheber, Lizenz, Hinweis auf Aenderungen.
        for teil in ("Parakeet TDT 0.6B v3", "NVIDIA",
                     "Creative Commons Namensnennung 4.0",
                     "creativecommons.org/licenses/by/4.0", "sherpa-onnx",
                     "unverändert"):
            self.assertIn(teil, self.inhalt)

    def test_dialos_und_quelltext(self):
        self.assertIn("GNU General Public License, Version 3", self.inhalt)
        self.assertIn("github.com/Stephan-Lefty/DialOS", self.inhalt)


class Vorlesen(unittest.TestCase):

    def setUp(self):
        self.m = _laden("dialos-auskunft.py", "dialos_auskunft")

    def test_adressen_werden_nicht_vorgelesen(self):
        with open(TEXT, encoding="utf-8") as f:
            absaetze = self.m.lizenzen_absaetze(f.read())
        self.assertGreater(len(absaetze), 3)
        for absatz in absaetze:
            self.assertNotIn("://", absatz)
        self.assertTrue(any("Parakeet" in a for a in absaetze))

    def test_jeder_absatz_eine_ansage(self):
        gesagt = []
        self.m.sprich = gesagt.append
        self.m.LIZENZEN = TEXT
        self.assertEqual(self.m.lizenzen(), 0)
        with open(TEXT, encoding="utf-8") as f:
            erwartet = self.m.lizenzen_absaetze(f.read())
        self.assertEqual(gesagt, erwartet)

    def test_fehlende_datei_wird_gesagt(self):
        gesagt = []
        self.m.sprich = gesagt.append
        self.m.LIZENZEN = "/gibt/es/nicht.txt"
        self.assertEqual(self.m.lizenzen(), 1)
        self.assertEqual(gesagt, ["Ich kann die Lizenzen nicht finden."])


class Befehl(unittest.TestCase):

    def setUp(self):
        self.m = _laden("dialos-sprachbefehl-desktop.py", "dialos_sprachbefehl")

    def test_satz_in_grammatik_und_auskunft(self):
        self.assertIn("lizenzen vorlesen", self.m.BEFEHLSSAETZE)
        self.assertEqual(self.m.AUSKUNFT_SAETZE["lizenzen vorlesen"], "lizenzen")

    def test_steht_in_der_befehlsuebersicht(self):
        self.assertNotIn("lizenzen vorlesen", self.m.befehle_ohne_uebersicht())
        self.assertIn("Lizenzen", self.m.thema_text("fragen"))


if __name__ == "__main__":
    unittest.main()
