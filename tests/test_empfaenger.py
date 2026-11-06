#!/usr/bin/env python3
"""
Tests fuer dialos-empfaenger.py - welches Thunderbird-Profil die Kontaktsuche liest.

Anlass (2026-10-08): Mit zwei Profilen, die beide ein Mailkonto haben, las
die Kontaktsuche das alphabetisch erste - Thunderbird oeffnete aber das aus
installs.ini. Ein Kontakt "stand nicht in den Kontakten", obwohl er in dem
Adressbuch stand, das der Nutzer sieht.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import importlib.util
import os
import shutil
import tempfile
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")

spec = importlib.util.spec_from_file_location("empfaenger_test",
                                              os.path.join(BIN, "dialos-empfaenger.py"))
em = importlib.util.module_from_spec(spec)
spec.loader.exec_module(em)


class Profilwahl(unittest.TestCase):

    def setUp(self):
        self.heim = tempfile.mkdtemp(prefix="dialos-empfaenger-test-")
        self.tb = os.path.join(self.heim, ".thunderbird")
        for name in ("aaa.default", "zzz.default-default"):
            os.makedirs(os.path.join(self.tb, name))
            with open(os.path.join(self.tb, name, "prefs.js"), "w") as f:
                f.write('user_pref("mail.identity.id1.useremail", "x@example.org");\n')

    def tearDown(self):
        shutil.rmtree(self.heim, ignore_errors=True)

    def _installs(self, standard):
        with open(os.path.join(self.tb, "installs.ini"), "w") as f:
            f.write(f"[FDC34C9F024745EB]\nDefault={standard}\nLocked=1\n")

    def test_installs_ini_hat_vorrang(self):
        """Das Profil, das Thunderbird oeffnet - nicht das alphabetisch erste."""
        self._installs("zzz.default-default")
        self.assertEqual(os.path.basename(em.profil(self.heim)), "zzz.default-default")

    def test_ohne_installs_ini_die_alte_regel(self):
        self.assertEqual(os.path.basename(em.profil(self.heim)), "aaa.default")

    def test_installs_ini_auf_totes_profil_faellt_zurueck(self):
        self._installs("gibt-es-nicht")
        self.assertEqual(os.path.basename(em.profil(self.heim)), "aaa.default")

    def test_kein_thunderbird(self):
        shutil.rmtree(self.tb)
        self.assertIsNone(em.profil(self.heim))


if __name__ == "__main__":
    unittest.main()
