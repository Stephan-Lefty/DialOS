#!/usr/bin/env python3
"""
Tests fuer die Mikrofon-Marke ("dialos-diktat-aktiv").

Solange ein Dialog das Mikrofon hat, haelt sich die Befehlserkennung heraus.
Bis zum 2026-10-08 legten Diktat, Notiz und Update-Lauf die Marke LEER an -
die Erkennung hielt sie dann fuer belegt, solange die Datei existierte. Starb
eines dieser Programme, blieb die Sprachsteuerung bis zum Neustart taub
(beim Dreh des Vorfuehrvideos dreimal passiert). Jetzt steht die PID darin,
und die Erkennung raeumt eine verwaiste Marke selbst weg.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import glob
import importlib.util
import io
import os
import re
import subprocess
import tempfile
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")


def _laden(datei, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, datei))
    modul = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(modul)
    return modul


class Wache(unittest.TestCase):
    """Die Pruefung in der Befehlserkennung."""

    @classmethod
    def setUpClass(cls):
        cls.dienst = _laden("dialos-sprachbefehl-desktop.py", "dienst_marke_test")

    def setUp(self):
        self.ordner = tempfile.mkdtemp(prefix="dialos-marke-test-")
        self.dienst.DIKTAT_MARKE = os.path.join(self.ordner, "dialos-diktat-aktiv")
        self.dienst.melde = lambda *a, **k: None

    def _marke(self, inhalt):
        with open(self.dienst.DIKTAT_MARKE, "w", encoding="utf-8") as f:
            f.write(inhalt)

    def test_keine_marke_heisst_frei(self):
        self.assertFalse(self.dienst.diktat_laeuft())

    def test_verwaiste_marke_wird_weggeraeumt(self):
        tot = subprocess.Popen(["true"])
        tot.wait()
        self._marke(f"{tot.pid} dialos-diktat\n")
        self.assertFalse(self.dienst.diktat_laeuft())
        self.assertFalse(os.path.exists(self.dienst.DIKTAT_MARKE))

    def test_lebender_besitzer_haelt_das_mikrofon(self):
        self._marke(f"{os.getpid()} dialos-diktat\n")
        self.assertTrue(self.dienst.diktat_laeuft())

    def test_alte_leere_marke_gilt_weiter_als_belegt(self):
        """Rueckwaertskompatibel - aber keiner legt sie mehr so an (unten)."""
        self._marke("")
        self.assertTrue(self.dienst.diktat_laeuft())


class Besitzer(unittest.TestCase):
    """Wer die Marke anlegt, schreibt seine PID hinein."""

    def test_kein_programm_legt_sie_leer_an(self):
        leer = re.compile(r"MARKE\w*\s*,\s*\"w\"\)\.close\(\)")
        treffer = [os.path.basename(p) for p in glob.glob(os.path.join(BIN, "*.py"))
                   if leer.search(open(p, encoding="utf-8").read())]
        self.assertEqual(treffer, [])

    def test_notiz_schreibt_ihre_pid(self):
        notiz = _laden("dialos-notiz.py", "notiz_marke_test")
        ordner = tempfile.mkdtemp(prefix="dialos-marke-test-")
        notiz.FREMDE_AUFNAHME_MARKE = os.path.join(ordner, "dialos-diktat-aktiv")
        notiz.marke_setzen()
        with open(notiz.FREMDE_AUFNAHME_MARKE, encoding="utf-8") as f:
            self.assertEqual(int(f.read().split()[0]), os.getpid())


if __name__ == "__main__":
    unittest.main()
