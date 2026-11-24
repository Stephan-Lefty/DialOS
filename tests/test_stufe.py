#!/usr/bin/env python3
"""
Tests fuer die Unterstuetzungsstufen (dialos_stufe.py, dialos-stufe.py und
die Stellen, die sie lesen).

Stephan, 2026-11-24: "Lass uns jetzt schon die Schritte einbauen, denn dann
koennen wir diese auch schon testen." Vier Stufen, die aufeinander aufbauen;
ohne Datei gilt Stufe 3 - das DialOS von vorher.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")
sys.path.insert(0, BIN)


def _laden(datei, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, datei))
    modul = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(modul)
    return modul


class MitEigenemKonto(unittest.TestCase):
    """Jeder Test bekommt ein leeres ~/.config - nie das echte."""

    def setUp(self):
        self.ordner = tempfile.mkdtemp(prefix="dialos-stufe-test-")
        self.addCleanup(shutil.rmtree, self.ordner, True)
        alt = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.ordner
        self.addCleanup(lambda: os.environ.__setitem__("XDG_CONFIG_HOME", alt)
                        if alt is not None else os.environ.pop("XDG_CONFIG_HOME", None))
        self.st = _laden("dialos_stufe.py", "dialos_stufe_test")

    def schreiben(self, inhalt):
        os.makedirs(os.path.join(self.ordner, "dialos"), exist_ok=True)
        with open(os.path.join(self.ordner, "dialos", "stufe"), "w") as f:
            f.write(inhalt)


class Modul(MitEigenemKonto):

    def test_ohne_datei_stufe_drei(self):
        # Stephans Wahl: bestehende Geraete merken nichts.
        self.assertEqual(self.st.stufe(), 3)

    def test_kaputte_datei_stufe_drei(self):
        for inhalt in ("", "zwei", "7", "-1"):
            with self.subTest(inhalt=inhalt):
                self.schreiben(inhalt)
                self.assertEqual(self.st.stufe(), 3)

    def test_setzen_und_lesen(self):
        for wert in range(4):
            self.st.setzen(wert)
            self.assertEqual(self.st.stufe(), wert)

    def test_setzen_wird_begrenzt(self):
        self.assertEqual(self.st.setzen(9), 3)
        self.assertEqual(self.st.setzen(-4), 0)

    def test_begruessung_in_jeder_stufe(self):
        # "Die Begruessung wuerde ich auch bei Stufe 0 drin lassen!"
        for wert in range(4):
            self.assertTrue(self.st.ansage_erlaubt("begruessung", wert))

    def test_zustand_erst_ab_stufe_zwei(self):
        erwartet = {0: False, 1: False, 2: True, 3: True}
        for wert, soll in erwartet.items():
            self.assertEqual(self.st.ansage_erlaubt("zustand", wert), soll)

    def test_antwort_rueckfrage_warnung_immer(self):
        for art in ("antwort", "rueckfrage", "warnung"):
            self.assertTrue(self.st.ansage_erlaubt(art, 0))

    def test_unbekannte_art_wird_gesprochen(self):
        # Ein Tippfehler im Aufrufer darf kein Geraet stumm machen.
        self.assertTrue(self.st.ansage_erlaubt("zustnad", 0))

    def test_stufen_bauen_aufeinander_auf(self):
        # Was in einer Stufe gesprochen wird, wird in jeder hoeheren auch.
        for art in self.st.AB_STUFE:
            erlaubt = [self.st.ansage_erlaubt(art, w) for w in range(4)]
            self.assertEqual(erlaubt, sorted(erlaubt), art)


class SagtNichtsInNiedrigerStufe(MitEigenemKonto):
    """dialos-say.py --art zustand schweigt in Stufe 0 und 1."""

    def lauf(self, *argumente):
        say = _laden("dialos-say.py", "dialos_say_stufe_test")
        gemeldet = []
        say.melde = gemeldet.append

        def kein_ton(*a, **k):
            raise AssertionError("haette gesprochen")
        say.sink_inputs = kein_ton
        alt = sys.argv
        sys.argv = ["dialos-say.py", *argumente]
        self.addCleanup(setattr, sys, "argv", alt)
        try:
            say.main()
        except AssertionError:
            return gemeldet, True
        return gemeldet, False

    def test_stufe_null_schweigt(self):
        self.schreiben("0")
        gemeldet, gesprochen = self.lauf("--art", "zustand", "Ton über Laptop.")
        self.assertFalse(gesprochen)
        self.assertTrue(any("still" in z for z in gemeldet))

    def test_stufe_zwei_spricht(self):
        self.schreiben("2")
        _, gesprochen = self.lauf("--art", "zustand", "Ton über Laptop.")
        self.assertTrue(gesprochen)

    def test_ohne_art_wird_gesprochen(self):
        self.schreiben("0")
        _, gesprochen = self.lauf("Hallo.")
        self.assertTrue(gesprochen)


class Wechseln(MitEigenemKonto):

    def setUp(self):
        super().setUp()
        self.w = _laden("dialos-stufe.py", "dialos_stufe_wechsel_test")
        self.w.st = self.st
        self.gesagt, self.gsettings = [], []
        self.w.sprich = self.gesagt.append
        self.w.melde = lambda t: None
        self.w.gsettings = lambda *a: self.gsettings.append(a)

    def befehl(self, *argumente):
        alt = sys.argv
        sys.argv = ["dialos-stufe.py", *argumente]
        try:
            return self.w.main()
        finally:
            sys.argv = alt

    def test_weniger_von_der_vorgabe(self):
        self.befehl("weniger")
        self.assertEqual(self.st.stufe(), 2)
        self.assertTrue(self.gesagt[-1].startswith("Stufe zwei."))

    def test_mehr_geht_nicht_ueber_drei(self):
        self.befehl("mehr")
        self.assertEqual(self.st.stufe(), 3)
        self.assertIn("Mehr geht nicht", self.gesagt[-1])

    def test_weniger_geht_nicht_unter_null(self):
        self.st.setzen(0)
        self.befehl("weniger")
        self.assertEqual(self.st.stufe(), 0)
        self.assertIn("Weniger geht nicht", self.gesagt[-1])

    def test_sehhilfen_beim_ueberschreiten_der_stufe_eins(self):
        self.st.setzen(0)
        self.befehl("mehr")
        self.assertTrue(all(a[0] == "set" for a in self.gsettings))
        self.assertEqual(len(self.gsettings), len(self.w.SEHHILFEN))
        self.gsettings.clear()
        self.befehl("weniger")
        self.assertTrue(all(a[0] == "reset" for a in self.gsettings))

    def test_keine_sehhilfen_zwischen_zwei_und_drei(self):
        # Ein bestehendes Konto (Vorgabe 3) bekommt nicht ungefragt
        # neue Schrift, nur weil es auf Stufe 2 geht.
        self.befehl("weniger")
        self.assertEqual(self.gsettings, [])

    def test_helfer_setzt_still(self):
        self.befehl("setzen", "1", "--still")
        self.assertEqual(self.st.stufe(), 1)
        self.assertEqual(self.gesagt, [])


class Verdrahtung(unittest.TestCase):

    def test_saetze_in_grammatik_und_uebersicht(self):
        d = _laden("dialos-sprachbefehl-desktop.py", "dialos_sb_stufe_test")
        for satz, wert in (("mehr unterstützung", "mehr"),
                           ("unterstützung verringern", "weniger")):
            self.assertIn(satz, d.BEFEHLSSAETZE)
            self.assertEqual(d.STUFE_SAETZE[satz], wert)
            self.assertNotIn(satz, d.befehle_ohne_uebersicht())

    def test_schalter_nimmt_denselben_weg(self):
        """Das Fenster setzt die Stufe ueber dialos-stufe.py - mit Ansage und
        Sehhilfen wie der Sprachbefehl, nie an ihm vorbei."""
        with open(os.path.join(BIN, "dialos-stufe-schalter.py"), encoding="utf-8") as f:
            quelle = f.read()
        self.assertIn('[STUFE_SKRIPT, "setzen", str(stufe)]', quelle)
        self.assertNotIn("st.setzen(", quelle)
        desktop = os.path.join(os.path.dirname(os.path.dirname(BIN)), "..",
                               "usr", "share", "applications", "dialos-stufe.desktop")
        with open(os.path.normpath(desktop), encoding="utf-8") as f:
            self.assertIn("Exec=/usr/local/bin/dialos-stufe-schalter.py", f.read())

    def test_zustandswechsel_sind_markiert(self):
        for datei, stelle in (("dialos-ton-ausgabe.py", 'ANSAGE_INTERN, art="zustand"'),
                              ("dialos-start-ansage.py", 'hergestellt.",\n                    art="zustand"')):
            with open(os.path.join(BIN, datei), encoding="utf-8") as f:
                self.assertIn(stelle, f.read(), datei)


if __name__ == "__main__":
    unittest.main()
