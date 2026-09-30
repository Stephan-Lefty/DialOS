#!/usr/bin/env python3
"""
Tests fuer dialos-radio.py - den Leser der Medienliste.

Geprueft wird, was ohne Geraet entscheidbar ist: die Auswahl des Senders,
das Merken des zuletzt gehoerten, die Ansagen bei leerer Liste - und vor
allem die Stellen, an denen zwei Dateien zusammenpassen muessen.

Der letzte Punkt ist der wichtigere. Ein Satz in der Grammatik, zu dem
keine Aktion gehoert, ist stumm; eine Aktion, deren Argument
dialos-radio.py nicht kennt, faellt erst am Geraet auf - und dort hoert
der Nutzer nur, dass nichts passiert.

Rhythmbox wird nie wirklich aufgerufen: `client` und `sprich` werden
ersetzt. Ein Test, der den Player startet, oeffnet ein Fenster und
spielt Ton - auf dem Rechner dessen, der die Tests laufen laesst.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")
sys.path.insert(0, BIN)


def _laden(datei, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, datei))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


import dialos_rhythmbox_sender as rs      # noqa: E402

_echtes_urlopen = urllib.request.urlopen
_echter_run = subprocess.run


def setUpModule():
    """Netz und fremde Programme sperren - wie in test_rhythmbox_sender.py."""
    def kein_netz(*a, **k):
        raise AssertionError("Dieser Test hat das Netz oder ein fremdes "
                             "Programm angefasst.")
    urllib.request.urlopen = kein_netz
    subprocess.run = kein_netz


def tearDownModule():
    urllib.request.urlopen = _echtes_urlopen
    subprocess.run = _echter_run


class RadioBasis(unittest.TestCase):
    """Gemeinsamer Aufbau: geladenes Modul mit abgefangenen Aussenwirkungen."""

    SENDER = [
        {"art": "radio", "sprechform": "deutschlandfunk",
         "name": "Deutschlandfunk", "quelle": "https://a.de/dlf.mp3"},
        {"art": "radio", "sprechform": "ö drei",
         "name": "Hitradio Ö3", "quelle": "https://b.at/oe3.mp3"},
        {"art": "radio", "sprechform": "radio kärnten",
         "name": "ORF Radio Kärnten", "quelle": "https://c.at/k.mp3"},
        {"art": "podcast", "sprechform": "lage der nation",
         "name": "Lage der Nation", "quelle": "https://d.de/feed"},
    ]

    def setUp(self):
        self.radio = _laden("dialos-radio.py", "radio_test")
        self.ordner = tempfile.mkdtemp(prefix="dialos-radio-test-")
        liste = os.path.join(self.ordner, "medienliste.json")
        with open(liste, "w", encoding="utf-8") as f:
            json.dump({"stand": "2026-09-30", "eintraege": self.SENDER}, f,
                      ensure_ascii=False)

        self.rs = rs
        self._alte_systemliste = rs.SYSTEMLISTE
        self._alte_eigene = rs.eigene_liste
        rs.SYSTEMLISTE = liste
        rs.eigene_liste = lambda: os.path.join(self.ordner, "eigen.json")

        self.radio.ZULETZT = os.path.join(self.ordner, "zuletzt.txt")
        self.radio.PROTOKOLL = os.path.join(self.ordner, "log")
        self.radio.sender_modul = lambda: rs
        self.gesagt, self.gerufen = [], []
        self.radio.sprich = self.gesagt.append
        self.radio.client = lambda *a, **k: self.gerufen.append(a) or True
        self.radio.laeuft = lambda: True

    def tearDown(self):
        rs.SYSTEMLISTE = self._alte_systemliste
        rs.eigene_liste = self._alte_eigene
        shutil.rmtree(self.ordner, ignore_errors=True)

    @property
    def gespielt(self):
        """Die Adressen, die an Rhythmbox gegangen waeren."""
        return [a[1] for a in self.gerufen if a and a[0] == "--play-uri"]


class Senderwahl(RadioBasis):

    def test_nur_radio_keine_podcasts(self):
        """Die Medienliste enthaelt alle Gattungen. Wer "Radio einschalten"
        sagt, will keinen Podcast - der laeuft ueber einen eigenen Befehl
        und hat eine Merkposition, die ein Radiosender nicht hat."""
        self.radio.einschalten(self.rs)
        self.assertNotIn("lage der nation", " ".join(self.gesagt))

    def test_auswahl_statt_raten(self):
        """Noch nie gehoert und mehrere zur Wahl: Es wird NICHT der erste
        gespielt. Ein Geraet, das ungefragt etwas anderes spielt als
        erwartet, ist fuer einen blinden Nutzer nicht zu korrigieren."""
        self.radio.einschalten(self.rs)
        self.assertEqual(self.gespielt, [])
        self.assertIn("Welchen Sender", " ".join(self.gesagt))

    def test_sender_beim_namen(self):
        self.radio.einschalten(self.rs, "ö drei")
        self.assertEqual(self.gespielt, ["https://b.at/oe3.mp3"])

    def test_umlaut_und_umschreibung_sind_derselbe_sender(self):
        """Der Erkenner liefert "kärnten", die Liste kann "kaernten"
        enthalten - beides ist derselbe gesprochene Satz."""
        self.radio.einschalten(self.rs, "radio kaernten")
        self.assertEqual(self.gespielt, ["https://c.at/k.mp3"])

    def test_zuletzt_gehoerter_beim_naechsten_mal(self):
        """Wer einschaltet, will meistens dasselbe wie gestern."""
        self.radio.einschalten(self.rs, "ö drei")
        self.gerufen.clear()
        self.radio.einschalten(self.rs)
        self.assertEqual(self.gespielt, ["https://b.at/oe3.mp3"])

    def test_gemerkter_sender_faellt_aus_der_liste(self):
        """Wird ein Sender aus der Medienliste entfernt, darf das
        Einschalten nicht ins Leere laufen - es fragt dann wieder."""
        with open(self.radio.ZULETZT, "w", encoding="utf-8") as f:
            f.write("gibt es nicht mehr\n")
        self.radio.einschalten(self.rs)
        self.assertEqual(self.gespielt, [])
        self.assertIn("Welchen Sender", " ".join(self.gesagt))

    def test_unbekannter_sender_wird_gesagt(self):
        self.radio.einschalten(self.rs, "antenne bayern")
        self.assertEqual(self.gespielt, [])
        self.assertIn("nicht in der Liste", " ".join(self.gesagt))

    def test_mehrdeutiges_wird_nicht_geraten(self):
        """"radio" passt auf "radio kärnten" - aber wenn mehrere passen,
        wird nachgefragt statt geraten. Ein falscher Sender ist schlimmer
        als eine Rueckfrage."""
        mehr = list(self.SENDER) + [
            {"art": "radio", "sprechform": "radio wien", "name": "Radio Wien",
             "quelle": "https://e.at/w.mp3"}]
        with open(rs.SYSTEMLISTE, "w", encoding="utf-8") as f:
            json.dump({"stand": "x", "eintraege": mehr}, f, ensure_ascii=False)
        self.radio.einschalten(self.rs, "radio")
        self.assertEqual(self.gespielt, [])
        self.assertIn("mehrere", " ".join(self.gesagt))

    def test_eindeutiger_anfang_genuegt(self):
        """Verschluckt der Erkenner ein Wort, soll der Sender trotzdem
        gefunden werden - solange nur EINER passt."""
        self.radio.einschalten(self.rs, "deutschland")
        self.assertEqual(self.gespielt, ["https://a.de/dlf.mp3"])

    def test_naechster_sender_geht_im_kreis(self):
        self.radio.einschalten(self.rs, "radio kärnten")   # letzter Eintrag
        self.gerufen.clear()
        self.radio.naechster(self.rs)
        self.assertEqual(self.gespielt, ["https://a.de/dlf.mp3"])

    def test_eintrag_ohne_adresse(self):
        with open(rs.SYSTEMLISTE, "w", encoding="utf-8") as f:
            json.dump({"stand": "x", "eintraege": [
                {"art": "radio", "sprechform": "kaputt", "name": "Kaputt",
                 "quelle": ""}]}, f, ensure_ascii=False)
        self.radio.einschalten(self.rs, "kaputt")
        self.assertEqual(self.gespielt, [])
        self.assertIn("keine Adresse", " ".join(self.gesagt))


class LeereListe(RadioBasis):
    """Der Zustand eines frisch aufgebauten Geraets - und damit der erste,
    den ein Nutzer erlebt."""

    def setUp(self):
        super().setUp()
        rs.SYSTEMLISTE = "/gibt/es/nicht.json"

    def test_ehrliche_ansage(self):
        self.radio.einschalten(self.rs)
        gesagt = " ".join(self.gesagt)
        self.assertIn("noch keine Sender", gesagt)
        # Der Weg gehoert dazu, nicht nur das Problem.
        self.assertIn("DialOS-Rhythmbox", gesagt)

    def test_kein_dateipfad_in_der_ansage(self):
        """Wer den Bildschirm nicht sieht, kann mit einem Pfad nichts
        anfangen - der gehoert ins Protokoll, nicht in die Ansage."""
        self.radio.einschalten(self.rs)
        self.assertNotIn("/", " ".join(self.gesagt))


class Steuerung(RadioBasis):

    def test_ausschalten_wenn_nichts_laeuft(self):
        """Die Regel "anders sagen, wenn sich nichts geaendert hat" -
        sonst klingt ein wirkungsloser Befehl wie ein erfolgreicher."""
        self.radio.laeuft = lambda: False
        self.radio.ausschalten()
        self.assertIn("läuft gerade nichts", " ".join(self.gesagt))
        self.assertEqual(self.gerufen, [])

    def test_ausschalten(self):
        self.radio.ausschalten()
        self.assertIn(("--stop",), self.gerufen)

    def test_lautstaerke_in_stufen(self):
        self.radio.client = lambda *a, **k: (
            "0.50" if k.get("hole_ausgabe") else self.gerufen.append(a) or True)
        self.radio.lautstaerke(+1)
        self.assertIn("Lauter.", self.gesagt)

    def test_lauter_geht_nicht_mehr(self):
        self.radio.client = lambda *a, **k: (
            "1.0" if k.get("hole_ausgabe") else self.gerufen.append(a) or True)
        self.radio.lautstaerke(+1)
        self.assertIn("Lauter geht nicht.", self.gesagt)


class PasstZumSprachdienst(unittest.TestCase):
    """Die Stellen, an denen zwei Dateien uebereinstimmen muessen.

    Genau hier entstehen die Fehler, die niemand beim Lesen sieht: ein
    Satz in der Grammatik ohne Aktion bleibt stumm, ein Argument mit
    Tippfehler faellt erst am Geraet auf."""

    @classmethod
    def setUpClass(cls):
        # Der Dienst meldet beim Laden, dass er Erweiterungen, Programme
        # und Medienliste nicht findet - er sucht sie unter /usr/local/bin,
        # und dort liegen sie nur am Geraet. Das ist richtig so und kein
        # Testfehler, macht die Ausgabe aber unlesbar.
        import contextlib
        import io
        with contextlib.redirect_stderr(io.StringIO()):
            cls.dienst = _laden("dialos-sprachbefehl-desktop.py", "dienst_test")
        cls.grammatik = json.loads(cls.dienst.GRAMMATIK_AN)

    def test_jeder_radio_satz_steht_in_der_grammatik(self):
        """Ein Satz, der nicht in der Grammatik steht, wird nie erkannt -
        die Aktion dazu ist dann tot."""
        for satz in self.dienst.RADIO_SAETZE:
            with self.subTest(satz=satz):
                self.assertIn(satz, self.grammatik)

    def test_jedes_argument_kennt_dialos_radio(self):
        """Der Wert der Tabelle wird dialos-radio.py als Befehl
        uebergeben. Ein Tippfehler faellt sonst erst am Geraet auf, und
        dort hoert der Nutzer nur, dass nichts passiert."""
        with open(os.path.join(BIN, "dialos-radio.py"), encoding="utf-8") as f:
            quelle = f.read()
        for argument in set(self.dienst.RADIO_SAETZE.values()):
            with self.subTest(argument=argument):
                self.assertIn(f'befehl == "{argument}"', quelle)

    def test_radio_steht_nicht_mehr_unter_den_wuenschen(self):
        """"radio einschalten" gab bis zum 2026-09-30 die Antwort "kann
        ich noch nicht". Bleibt der Eintrag stehen, verdeckt er den
        gebauten Befehl."""
        for satz in ("radio einschalten", "musik abspielen"):
            with self.subTest(satz=satz):
                self.assertNotIn(satz, self.dienst.WUNSCH_SAETZE)

    def test_radio_befehle_sind_in_der_uebersicht(self):
        """Ein Befehl, den niemand nennt, ist fuer einen blinden Nutzer so
        gut wie nicht vorhanden (Lehre vom 2026-09-18, damals bei
        "unterlagen durchsuchen")."""
        self.assertEqual(self.dienst.befehle_ohne_uebersicht(), [])
        text = self.dienst.thema_text("radio")
        self.assertIn("Radio einschalten", text)
        self.assertIn("Radio abstellen", text)

    def test_ein_und_ausschalten_klingen_nicht_gleich(self):
        """Mit DialOS' eigener Kollisionspruefung gerechnet. "radio
        ausschalten" lag bei 0,82 - genau auf der Schwelle, und ein
        verwechseltes Ein- mit Ausschalten ist nicht zu durchschauen."""
        paare = rs.aehnliche_sprechformen(
            [{"sprechform": s} for s in self.dienst.RADIO_SAETZE])
        self.assertEqual(paare, [])

    def test_kein_radio_satz_kollidiert_mit_einem_bestehenden(self):
        eintraege = [{"sprechform": s} for s in self.grammatik if s != "[unk]"]
        radio = set(self.dienst.RADIO_SAETZE)
        treffer = [(a["sprechform"], b["sprechform"], grund)
                   for a, b, grund in rs.aehnliche_sprechformen(eintraege)
                   if a["sprechform"] in radio or b["sprechform"] in radio]
        self.assertEqual(treffer, [])

    def test_sendersaetze_sind_ganze_saetze(self):
        """Ein Befehl ist nie ein Einzelwort - ein beilaeufiges
        "Deutschlandfunk" im Gespraech darf nichts ausloesen. Dieselbe
        Regel, an der am 2026-08-16 "windows" gescheitert ist."""
        gebaut = self.dienst.radio_saetze_lesen()
        for satz in gebaut:
            with self.subTest(satz=satz):
                self.assertGreaterEqual(len(satz.split()), 2)
                self.assertTrue(satz.endswith(" einschalten"))


if __name__ == "__main__":
    unittest.main()
