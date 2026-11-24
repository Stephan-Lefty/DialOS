#!/usr/bin/env python3
"""
"Diktat abbrechen" im Diktat: ein Hinweis, kein Befehl (2026-11-24).

Ohne den Satz presste der Schluss-Erkenner ein gesprochenes "Diktat abbrechen"
auf einen Satz, den er kannte - in einem von 16 Piper-Laeufen auf "diktat
beenden", also SPEICHERN statt Verwerfen. Jetzt erkennt er ihn (16 von 16),
und Michael sagt, wie es richtig heisst.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import importlib.util
import json
import os
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")


def _laden():
    spec = importlib.util.spec_from_file_location(
        "dialos_diktat_hinweis", os.path.join(BIN, "dialos-diktat.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


class DiktatAbbrechen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = _laden()

    def test_steht_in_der_schluss_grammatik(self):
        self.assertIn("diktat abbrechen", json.loads(self.d.GRAMMATIK_SCHLUSS))

    def test_ist_kein_schluss(self):
        # Das ist der ganze Punkt: abbrechen darf NIE speichern.
        self.assertFalse(self.d.ist_schluss("diktat abbrechen"))
        self.assertTrue(self.d.ist_schluss("diktat beenden"))

    def test_laeuft_durch_die_befehls_sicherungen(self):
        # Ruhe davor/danach und Gegenprobe gelten fuer alles in BEFEHLE_IM_DIKTAT.
        self.assertIn(self.d.HINWEIS_DIKTAT_ABBRECHEN, self.d.BEFEHLE_IM_DIKTAT)
        self.assertEqual(self.d.BEFEHL_STAMM[self.d.HINWEIS_DIKTAT_ABBRECHEN], "abbrech")

    def test_hinweis_nennt_beide_richtigen_saetze(self):
        ansage = self.d.ANSAGE_DIKTAT_ABBRECHEN.lower()
        self.assertIn(self.d.BEFEHL_ABBRECHEN, ansage)      # alles verwerfen
        self.assertIn(self.d.SCHLUSSSATZ, ansage)           # diktat beenden

    def test_wird_ausgefuehrt_ohne_zu_speichern_oder_zu_verwerfen(self):
        with open(os.path.join(BIN, "dialos-diktat.py"), encoding="utf-8") as f:
            quelle = f.read()
        zweig = quelle.split('elif b["satz"] == HINWEIS_DIKTAT_ABBRECHEN:', 1)[1]
        zweig = zweig.split("elif b[\"satz\"]", 1)[0]
        self.assertIn("ANSAGE_DIKTAT_ABBRECHEN", zweig)
        self.assertNotIn("abgebrochen = True", zweig)
        self.assertNotIn("break", zweig)


if __name__ == "__main__":
    unittest.main()
