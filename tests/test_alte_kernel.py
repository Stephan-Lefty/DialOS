#!/usr/bin/env python3
"""
Tests fuer dialos-alte-kernel: entfernt alte Kernel - und NUR alte Kernel.

Behalten werden immer der laufende, der neueste und der vorige. Am 2026-11-24
stuerzte der neue Kernel mit dem NVIDIA-Treiber ab - der vorige im Startmenue
war der Notausgang.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import importlib.machinery
import importlib.util
import os
import unittest

SBIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "sbin")


def _laden():
    pfad = os.path.join(SBIN, "dialos-alte-kernel")
    lader = importlib.machinery.SourceFileLoader("dialos_alte_kernel", pfad)
    spec = importlib.util.spec_from_loader("dialos_alte_kernel", lader)
    modul = importlib.util.module_from_spec(spec)
    lader.exec_module(modul)
    return modul


V = ["6.12.107+deb13-amd64", "6.12.111+deb13-amd64", "6.12.113+deb13-amd64",
     "6.12.115+deb13.1-amd64", "6.12.118+deb13-amd64"]
KERNEL = {f"linux-image-{v}": v for v in V}


class Auswahl(unittest.TestCase):

    def setUp(self):
        self.k = _laden()

    def test_der_fall_vom_24_november(self):
        # Fuenf Kernel, der neueste laeuft: drei weg, 115 bleibt als Notfall.
        weg = self.k.zu_entfernen(KERNEL, V[4])
        self.assertEqual(weg, [f"linux-image-{v}" for v in V[:3]])

    def test_direkt_nach_einem_update(self):
        # 118 installiert, laeuft aber noch nicht - es laeuft 115. Dann bleiben
        # 118 (Neustart), 115 (laeuft und ist der vorige).
        weg = self.k.zu_entfernen(KERNEL, V[3])
        self.assertEqual(weg, [f"linux-image-{v}" for v in V[:3]])

    def test_laufender_alter_kernel_bleibt_immer(self):
        # Jemand hat ueber das Startmenue einen alten Kernel gewaehlt.
        weg = self.k.zu_entfernen(KERNEL, V[1])
        self.assertNotIn(f"linux-image-{V[1]}", weg)
        self.assertEqual(weg, [f"linux-image-{V[0]}", f"linux-image-{V[2]}"])

    def test_zwei_kernel_nichts_zu_tun(self):
        zwei = {f"linux-image-{v}": v for v in V[3:]}
        self.assertEqual(self.k.zu_entfernen(zwei, V[4]), [])

    def test_versionen_werden_als_zahlen_sortiert(self):
        # 6.12.9 ist aelter als 6.12.10 - als Text waere es andersherum.
        kernel = {"linux-image-6.12.9+deb13-amd64": "6.12.9+deb13-amd64",
                  "linux-image-6.12.10+deb13-amd64": "6.12.10+deb13-amd64",
                  "linux-image-6.12.11+deb13-amd64": "6.12.11+deb13-amd64"}
        self.assertEqual(self.k.zu_entfernen(kernel, "6.12.11+deb13-amd64"),
                         ["linux-image-6.12.9+deb13-amd64"])

    def test_metapaket_ist_kein_kernel(self):
        self.assertIsNone(self.k.MUSTER.match("linux-image-amd64"))
        self.assertIsNone(self.k.MUSTER.match("linux-image-6.12.118+deb13-amd64-dbg"))


class Probe(unittest.TestCase):

    def setUp(self):
        self.k = _laden()

    def test_nur_kernel_ist_ok(self):
        sim = "Purg linux-image-6.12.107+deb13-amd64 [6.12.107-1]\n"
        ok, fremd = self.k.probe_nur_kernel(["linux-image-6.12.107+deb13-amd64"], sim)
        self.assertTrue(ok)
        self.assertEqual(fremd, [])

    def test_fremdes_paket_bricht_ab(self):
        # Wollte apt mehr mitnehmen, wird NICHTS entfernt.
        sim = ("Purg linux-image-6.12.107+deb13-amd64 [6.12.107-1]\n"
               "Remv gnome-shell [48.4-1]\n")
        ok, fremd = self.k.probe_nur_kernel(["linux-image-6.12.107+deb13-amd64"], sim)
        self.assertFalse(ok)
        self.assertEqual(fremd, ["gnome-shell"])

    def test_installieren_bricht_auch_ab(self):
        sim = ("Purg linux-image-6.12.107+deb13-amd64 [6.12.107-1]\n"
               "Inst irgendwas (1.0 Debian:13)\n")
        ok, _ = self.k.probe_nur_kernel(["linux-image-6.12.107+deb13-amd64"], sim)
        self.assertFalse(ok)


class Eingebunden(unittest.TestCase):

    def test_in_jedem_erfolgreichen_update_lauf(self):
        with open(os.path.join(SBIN, "dialos-systemupdate"), encoding="utf-8") as f:
            quelle = f.read()
        # Drei Wege enden mit datum_merken - vor jedem wird aufgeraeumt.
        self.assertEqual(quelle.count("alte_kernel_entfernen\n        datum_merken"), 3)
        self.assertIn("/usr/local/sbin/dialos-alte-kernel", quelle)

    def test_ist_ausfuehrbar(self):
        self.assertTrue(os.access(os.path.join(SBIN, "dialos-alte-kernel"), os.X_OK))


if __name__ == "__main__":
    unittest.main()
