#!/usr/bin/env python3
"""
Tests fuer den MX-Hinweis im Mailkonto-Werkzeug (dialos-mailkonto.py).

Kennt die Anbieter-Datenbank eine eigene Domain nicht (dialos.org, spaeter
Kunden mit eigener Domain), sagte die Maske bis zum 2026-11-06 nur "Server
eintragen". Jetzt nennt sie den MX-Rechner der Domain als Hinweis - nie als
Wert, denn bei dialos.org ist der MX s111.goserver.host, der richtige
Posteingang aber imap.dialos.org.

Kein Netz noetig: Die DNS-Antwort wird hier von Hand gebaut.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import os
import struct
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")


def _laden():
    spec = importlib.util.spec_from_file_location(
        "dialos_mailkonto", os.path.join(BIN, "dialos-mailkonto.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def name(text):
    return b"".join(bytes([len(t)]) + t.encode() for t in text.split(".")) + b"\0"


def antwort(kennung, eintraege):
    """DNS-Antwort mit MX-Eintraegen [(vorrang, rechner)], Namen komprimiert."""
    kopf = struct.pack(">HHHHHH", kennung, 0x8180, 1, len(eintraege), 0, 0)
    frage = name("dialos.org") + struct.pack(">HH", 15, 1)
    teile = b""
    for vorrang, rechner in eintraege:
        # 0xC00C zeigt auf den Namen in der Frage (Kompression).
        daten = struct.pack(">H", vorrang) + name(rechner)
        teile += b"\xc0\x0c" + struct.pack(">HHIH", 15, 1, 300, len(daten)) + daten
    return kopf + frage + teile


class Antwort(unittest.TestCase):

    def setUp(self):
        self.m = _laden()

    def test_mx_wird_gelesen(self):
        a = antwort(4711, [(10, "s111.goserver.host")])
        self.assertEqual(self.m.mx_aus_antwort(a, 4711), ["s111.goserver.host"])

    def test_nach_vorrang_sortiert(self):
        a = antwort(1, [(20, "zweit.example.net"), (5, "erst.example.net")])
        self.assertEqual(self.m.mx_aus_antwort(a, 1),
                         ["erst.example.net", "zweit.example.net"])

    def test_fremde_kennung_wird_verworfen(self):
        a = antwort(1, [(10, "s111.goserver.host")])
        self.assertEqual(self.m.mx_aus_antwort(a, 2), [])

    def test_kaputte_antwort_ist_kein_absturz(self):
        self.assertEqual(self.m.mx_aus_antwort(b"\x00\x01", 1), [])


class Hinweis(unittest.TestCase):

    def setUp(self):
        self.m = _laden()

    def test_mit_mx(self):
        self.m.mx_rechner = lambda d: ["s111.goserver.host"]
        text = self.m.hinweis_ohne_server("dialos.org")
        self.assertIn("s111.goserver.host", text)
        self.assertIn("Kundenbereich", text)
        self.assertIn("NICHT der richtige Eintrag", text)

    def test_ohne_mx_nur_die_bitte(self):
        self.m.mx_rechner = lambda d: []
        text = self.m.hinweis_ohne_server("dialos.org")
        self.assertIn("in der Maske eintragen", text)
        self.assertNotIn("Hinweis", text)

    def test_maske_bekommt_den_hinweis(self):
        # Der Weg, den die Maske sieht: Rueckgabewert 4, Text auf stderr.
        self.m.aus_ispdb = lambda mail: None
        self.m.mx_rechner = lambda d: ["s111.goserver.host"]
        fehler = io.StringIO()
        with contextlib.redirect_stderr(fehler), \
                self.assertRaises(SystemExit) as ende:
            self.m.server_bestimmen({"mail": "info@dialos.org"})
        self.assertEqual(ende.exception.code, 4)
        self.assertIn("s111.goserver.host", fehler.getvalue())

    def test_mx_nie_als_wert(self):
        # Kennt die Datenbank die Domain, bleibt der MX aussen vor.
        self.m.aus_ispdb = lambda mail: (
            {"server": "imap.example.net", "port": "993", "socket": "SSL"},
            {"server": "smtp.example.net", "port": "465", "socket": "SSL"})
        self.m.mx_rechner = lambda d: self.fail("MX darf hier nicht gefragt werden")
        ein, aus, _ = self.m.server_bestimmen({"mail": "a@example.net"})
        self.assertEqual(ein["server"], "imap.example.net")


if __name__ == "__main__":
    unittest.main()
