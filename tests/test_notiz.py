#!/usr/bin/env python3
"""
Tests fuer dialos-notiz.py - Vorlesen von Brief, Notizen und Einkaufszettel.

Anlass (2026-10-08): "Brief vorlesen" brach seit dem 2026-09-21 mit
NameError ab, weil mail_vorlesbar() eine Funktion holen() aufrief, die nur
in dialos-diktat.py stand. Kein Compiler und kein Selbsttest findet einen
Namen, der erst beim Aufruf fehlt - ein Test, der die Funktion aufruft, schon.

Sprachausgabe wird nie wirklich aufgerufen.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import importlib.util
import os
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")


def _laden():
    spec = importlib.util.spec_from_file_location(
        "notiz_test", os.path.join(BIN, "dialos-notiz.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


class Vorlesbar(unittest.TestCase):

    def setUp(self):
        self.notiz = _laden()
        # Die Repo-Fassung des Diktats, nicht die installierte - der Test soll
        # auch auf dem Arbeitsrechner pruefen, was ausgeliefert wird.
        self.notiz.DIKTAT_SKRIPT = os.path.join(BIN, "dialos-diktat.py")

    def test_mailadresse_ohne_absturz(self):
        text = self.notiz.mail_vorlesbar("Schreib an erika.musterfrau@example.org bitte.")
        self.assertNotIn("@", text)
        self.assertIn("example", text)

    def test_text_ohne_mailadresse_bleibt(self):
        self.assertEqual(self.notiz.mail_vorlesbar("Liebe Frau Musterfrau."),
                         "Liebe Frau Musterfrau.")

    def test_holen_mit_fehlender_datei_gibt_ersatz(self):
        self.assertEqual(self.notiz.holen("/gibt/es/nicht.py", "x", ersatz="E"), "E")


if __name__ == "__main__":
    unittest.main()
