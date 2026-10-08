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
        # Abspielen traegt seit 2026-10-08 in Rhythmbox' Datenbank ein - ohne
        # das hier schriebe jeder Testlauf in die ECHTE des Testenden.
        self.radio.RHYTHMDB = os.path.join(self.ordner, "rhythmdb.xml")
        self.radio.PROTOKOLL = os.path.join(self.ordner, "log")
        self.radio.sender_modul = lambda: rs
        self.gesagt, self.gerufen = [], []
        self.radio.sprich = self.gesagt.append
        self.radio.client = lambda *a, **k: self.gerufen.append(a) or True
        self.radio.laeuft = lambda: True
        # Rhythmbox wirklich zu beenden hiesse pgrep - nur vermerken.
        self.radio.rhythmbox_beenden = lambda: self.gerufen.append(("--quit",)) or True

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


class AmGeraetGefunden(RadioBasis):
    """Drei Fehler vom ersten Lauf am Geraet (2026-10-08)."""

    def test_unbekannter_sender_wird_vor_dem_abspielen_eingetragen(self):
        """--play-uri spielt nur, was in Rhythmbox' Datenbank steht - fuer
        alles andere meldet es Erfolg und bleibt still."""
        self.radio.laeuft = lambda: False
        self.radio.einschalten(self.rs, "ö drei")
        self.assertEqual(self.gespielt, ["https://b.at/oe3.mp3"])
        self.assertTrue(self.radio.rhythmbox_kennt("https://b.at/oe3.mp3"))
        # die ganze Liste auf einmal, damit Rhythmbox nur einmal zu muss
        self.assertTrue(self.radio.rhythmbox_kennt("https://a.de/dlf.mp3"))
        # kein Podcast-Feed als Radiosender
        self.assertFalse(self.radio.rhythmbox_kennt("https://d.de/feed"))

    def test_eingetragen_ohne_unbekannt_als_interpret(self):
        """Sonst sagt "Was laeuft gerade": "Unbekannt - Hitradio Oe3"."""
        self.radio.laeuft = lambda: False
        self.radio.einschalten(self.rs, "ö drei")
        with open(self.radio.RHYTHMDB, encoding="utf-8") as f:
            self.assertNotIn("Unbekannt", f.read())

    def test_bekannter_sender_ohne_neustart(self):
        """Steht er schon drin, wird Rhythmbox nicht geschlossen."""
        self.radio.laeuft = lambda: False
        self.radio.einschalten(self.rs, "ö drei")
        self.gerufen.clear()
        self.radio.laeuft = lambda: True
        self.radio.einschalten(self.rs, "ö drei")
        self.assertNotIn(("--quit",), self.gerufen)

    def test_lautstaerke_mit_deutschem_komma(self):
        """rhythmbox-client sagt "liegt bei 0,799988." - nicht "0.8"."""
        self.radio.client = lambda *a, **k: (
            "Wiedergabelautstärke liegt bei 0,799988." if k.get("hole_ausgabe")
            else self.gerufen.append(a) or True)
        self.radio.lautstaerke(+1)
        self.assertIn(("--set-volume", "0.90"), self.gerufen)
        self.assertNotIn(("--volume-up",), self.gerufen)

    def test_liedtitel_oder_nur_der_sender(self):
        n = self.radio.nur_sendername
        self.assertTrue(n("HITRADIO Ö3 - Livestream", "Hitradio Oe3"))
        self.assertTrue(n("Life Radio", "Life Radio"))
        self.assertTrue(n("", "Oe1"))
        self.assertFalse(n("coldplay - higher power", "Kronehit"))
        # Sendername IM Titel, und trotzdem ein Lied
        self.assertFalse(n("beabadoobee - Memories | FM4 Morning Show", "FM4"))

    def test_was_laeuft_sagt_das_lied(self):
        self.radio.client = lambda *a, **k: "Kronehit" if k.get("hole_ausgabe") else True
        self.radio.laufende_adresse = lambda: "http://x.at/kronehit.mp3"
        self.radio.icy_titel = lambda adresse: "coldplay - higher power"
        self.radio.was_laeuft()
        self.assertEqual(self.gesagt, ["Es läuft Kronehit: coldplay - higher power."])

    def test_was_laeuft_ohne_liedtitel_sagt_es_ehrlich(self):
        self.radio.client = lambda *a, **k: "Life Radio" if k.get("hole_ausgabe") else True
        self.radio.laufende_adresse = lambda: "http://x.at/life"
        self.radio.icy_titel = lambda adresse: "Life Radio"
        self.radio.was_laeuft()
        self.assertIn("keinen Liedtitel", self.gesagt[0])


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

    def test_mindestdauer_wird_an_das_podcast_modul_durchgereicht(self):
        """DIE VERDRAHTUNG, und sie ist aus einer Luecke entstanden
        (2026-10-08): Die Mutationsprobe hat `neueste_folge(folgen,
        eintrag.get("mindestdauer") or 0)` zu `neueste_folge(folgen)`
        gekuerzt - und ALLE Tests blieben gruen. Die Funktion war
        geprueft, die Liste war geprueft, nur die Leitung dazwischen
        nicht. Am Geraet haette der Nutzer eine Ankuendigung statt
        eines Hoerspiels gehoert, und niemand haette gewusst, warum.
        """
        with open(os.path.join(BIN, "dialos-radio.py"), encoding="utf-8") as f:
            quelle = f.read()
        self.assertIn("neueste_folge(folgen,", quelle,
                      "dialos-radio.py ruft neueste_folge ohne Mindestdauer")
        self.assertIn('mindestdauer', quelle,
                      "dialos-radio.py liest das Feld gar nicht")

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


class AusgelieferteListe(unittest.TestCase):
    """Die Medienliste, die wirklich im Repo liegt und aufs Geraet geht.

    Bis zum 2026-10-05 gab es sie nicht - das Format stand, die Auswahl
    fehlte. Jetzt sind es zehn Sender, und dieser Test haelt fest, dass
    sie gueltig bleiben: Ein Tippfehler in einer Sprechform oder eine
    verlorene Adresse faellt sonst erst am Geraet auf, wo der Nutzer nur
    hoert, dass nichts kommt.
    """

    @classmethod
    def setUpClass(cls):
        cls.pfad = rs.repo_liste()
        with open(cls.pfad, encoding="utf-8") as f:
            cls.daten = json.load(f)
        cls.eintraege = cls.daten["eintraege"]

    def test_es_gibt_sie_ueberhaupt(self):
        self.assertTrue(os.path.isfile(self.pfad))
        self.assertRegex(self.daten["stand"], r"^\d{4}-\d{2}-\d{2}$")

    def test_hoechstens_zehn_je_land_und_gattung(self):
        """Stephans Vorgaben vom 2026-10-05, beide zusammen: „Ja lieber 10"
        und „wir müssen für alle Medien 3 Listen machen".

        Die Zahl gilt deshalb JE LAND, nicht fuer die ganze Datei - die
        Datei ist der Vorrat fuer drei Laender, und jedes Geraet sieht
        davon nur seines (siehe land_des_geraets). Ein frueherer Test
        verlangte hoechstens zehn insgesamt und schlug zu, sobald die
        zweite Landesliste dazukam.
        """
        gezaehlt = {}
        for eintrag in self.eintraege:
            schluessel = (eintrag.get("land") or "ohne", eintrag["art"])
            gezaehlt[schluessel] = gezaehlt.get(schluessel, 0) + 1
        self.assertTrue(gezaehlt, "die Liste ist leer")
        for (land, art), anzahl in gezaehlt.items():
            with self.subTest(land=land, art=art):
                self.assertLessEqual(
                    anzahl, 10,
                    f"{anzahl} Eintraege fuer {art} in {land} - "
                    "„weniger ist mehr“ gilt je Land")

    def test_jedes_land_wird_bedient(self):
        """DialOS ist fuer drei Laender. Eine Liste, die nur eines
        bedient, laesst zwei Drittel der Geraete ohne Radio."""
        laender = {e.get("land") for e in self.eintraege if e.get("land")}
        self.assertEqual(laender, {"DE", "AT", "CH"})

    def test_je_land_keine_kollision(self):
        """Entscheidend ist die Kollision INNERHALB eines Landes - nur
        die Saetze eines Landes kommen zusammen in die Grammatik. Zwei
        aehnliche Sprechformen in verschiedenen Laendern treffen sich
        auf keinem Geraet."""
        for land in ("DE", "AT", "CH"):
            teil = [e for e in self.eintraege if e.get("land") == land]
            with self.subTest(land=land):
                paare = rs.aehnliche_sprechformen(teil)
                self.assertEqual(
                    [(a["sprechform"], b["sprechform"]) for a, b, _ in paare],
                    [])

    def test_jeder_eintrag_vollstaendig(self):
        for eintrag in self.eintraege:
            with self.subTest(sender=eintrag.get("name")):
                for feld in ("art", "sprechform", "name", "quelle"):
                    self.assertTrue(eintrag.get(feld), f"{feld} fehlt")
                self.assertIn(eintrag["art"], rs.ARTEN)

    def test_keine_zugangsschranke(self):
        """Stephans Vorgabe vom 2026-09-25: „Ohne einen Account oder so."
        Hier gegen die ausgelieferte Datei geprueft, nicht nur gegen die
        Funktion."""
        for eintrag in self.eintraege:
            with self.subTest(sender=eintrag["name"]):
                self.assertFalse(rs.braucht_zugang(eintrag["quelle"]))
                self.assertFalse(rs.ist_playlist(eintrag["quelle"]))

    def test_jedes_land_hat_podcasts(self):
        """Dieselbe Begruendung wie beim Radio: Eine Gattung, die nur ein
        Land bedient, laesst zwei Drittel der Geraete ohne."""
        for land in ("DE", "AT", "CH"):
            with self.subTest(land=land):
                self.assertTrue(
                    [e for e in self.eintraege
                     if e.get("land") == land and e["art"] == "podcast"],
                    f"{land} hat keinen Podcast")

    def test_mindestdauer_ist_eine_sinnvolle_zahl(self):
        """Das Feld ist freiwillig - aber wenn es da ist, muss es eine
        Zahl in SEKUNDEN sein. Eine "20" (gemeint: Minuten) wuerde den
        Filter still unwirksam machen, weil jede Folge laenger ist."""
        for eintrag in self.eintraege:
            if "mindestdauer" not in eintrag:
                continue
            with self.subTest(name=eintrag["name"]):
                wert = eintrag["mindestdauer"]
                self.assertIsInstance(wert, int)
                self.assertGreaterEqual(
                    wert, 60, "unter einer Minute filtert nichts")
                self.assertLessEqual(
                    wert, 7200, "ueber zwei Stunden filtert alles weg")

    def test_mindestdauer_nur_wo_sie_gelesen_wird(self):
        """EIN FELD, DAS NICHTS TUT, IST SCHLIMMER ALS KEINS. Gelesen
        wird `mindestdauer` nur bei den Gattungen mit Folgen - ein
        Livestream hat keine, dort waere der Wert eine Behauptung ohne
        Wirkung. Wer das Feld spaeter bei Radio eintraegt, soll hier
        anschlagen und nicht am Geraet raetseln."""
        mit_folgen = ("podcast", "nachrichten-podcast", "hoerbuch")
        for eintrag in self.eintraege:
            if "mindestdauer" not in eintrag:
                continue
            with self.subTest(name=eintrag["name"]):
                self.assertIn(
                    eintrag["art"], mit_folgen,
                    f"{eintrag['art']} hat keine Folgen - "
                    "mindestdauer bleibt dort wirkungslos")

    def test_podcast_quellen_sind_feeds_keine_streams(self):
        """Ein Podcast-Eintrag, dessen Quelle direkt auf eine MP3 zeigt,
        liefert beim naechsten Abruf immer dieselbe Folge. Die Adresse
        muss der FEED sein, nicht die Datei."""
        for eintrag in self.eintraege:
            if eintrag["art"] not in ("podcast", "nachrichten-podcast"):
                continue
            with self.subTest(name=eintrag["name"]):
                quelle = eintrag["quelle"].lower().split("?")[0]
                for endung in (".mp3", ".m4a", ".aac", ".ogg", ".opus"):
                    self.assertFalse(
                        quelle.endswith(endung),
                        f"{quelle} ist eine Audiodatei, kein Feed")

    def test_keine_verwechselbaren_sprechformen_je_land(self):
        """Der Grund, warum es nur zehn je Land sind: Bei 78 Sendern
        meldet diese Pruefung zehn Paare, bei der getroffenen Auswahl
        nichts.

        GEPRUEFT WIRD JE LAND, nicht ueber die ganze Datei - seit dem
        2026-10-05 ist das zwingend: „landesweite nachrichten" steht
        dreimal darin, je Land mit einer anderen Quelle (tagesschau,
        Oe1 live, SRF). Ueber alle Laender gerechnet waere das eine
        Kollision; auf einem Geraet treffen sich die drei nie.
        """
        for land in ("DE", "AT", "CH"):
            teil = [e for e in self.eintraege if e.get("land") == land]
            with self.subTest(land=land):
                paare = rs.aehnliche_sprechformen(teil)
                self.assertEqual(
                    [(a["sprechform"], b["sprechform"], g)
                     for a, b, g in paare], [])

    def test_sprechformen_klein_und_ohne_umschreibung(self):
        for eintrag in self.eintraege:
            form = eintrag["sprechform"]
            with self.subTest(sender=eintrag["name"]):
                self.assertEqual(form, form.lower())
                for wort in form.split():
                    self.assertNotIn(wort, ("oe", "ef", "vau", "ix", "zet",
                                            "fuenf", "kaernten", "zuerich"))

    def test_das_radio_liest_sie(self):
        """Der ganze Weg in einem Test: Datei -> medienliste_lesen ->
        Sender finden, so wie dialos-radio.py es tut."""
        radio = _laden("dialos-radio.py", "radio_liste_test")
        # Ohne Landfilter, aber nur die Radiosender: Die Datei enthaelt
        # seit dem 2026-10-05 auch Nachrichten-Eintraege.
        nur_radio = [e for e in self.eintraege if e["art"] == "radio"]
        liste = rs.medienliste_lesen(art="radio", systemweit=self.pfad,
                                     persoenlich="/gibt/es/nicht.json",
                                     land=None)
        self.assertEqual(len(liste), len(nur_radio))
        for eintrag in liste:
            with self.subTest(sender=eintrag["name"]):
                gefunden, _ = radio.sender_finden(rs, liste,
                                                  eintrag["sprechform"])
                self.assertIsNotNone(gefunden)
                self.assertEqual(gefunden["name"], eintrag["name"])


class NachrichtenInDerListe(unittest.TestCase):
    """Die Nachrichten-Eintraege der ausgelieferten Liste.

    Sie werden vom Sprachdienst zu Saetzen gemacht (siehe
    nachrichten_saetze_lesen) - aber erst, wenn die Liste an ihrem Platz
    unter /usr/local/share liegt. Auf dem Arbeitsrechner ist das nicht
    so, deshalb pruefen diese Tests die DATEI, nicht den Dienst.
    """

    @classmethod
    def setUpClass(cls):
        with open(rs.repo_liste(), encoding="utf-8") as f:
            cls.alle = json.load(f)["eintraege"]
        cls.nachrichten = [e for e in cls.alle
                           if e["art"].startswith("nachrichten")]

    def test_es_gibt_nachrichten(self):
        self.assertTrue(self.nachrichten)

    def test_jedes_land_hat_landesweite_nachrichten(self):
        """Ohne sie waere „landesweite nachrichten" auf dem Geraet ein
        Satz, der nichts findet."""
        for land in ("DE", "AT", "CH"):
            mit_satz = {e["sprechform"] for e in self.nachrichten
                        if e.get("land") == land}
            with self.subTest(land=land):
                self.assertIn("landesweite nachrichten", mit_satz)

    def test_saetze_sind_mindestens_zwei_woerter(self):
        """Ein Einzelwort waere ein Befehl, der im Gespraech ausloest -
        dieselbe Regel, an der am 2026-08-16 „windows" gescheitert ist.
        Der Sprachdienst verwirft kuerzere Sprechformen deshalb."""
        for eintrag in self.nachrichten:
            with self.subTest(sender=eintrag["name"]):
                self.assertGreaterEqual(
                    len(eintrag["sprechform"].split()), 2)

    def test_art_passt_zur_quelle(self):
        """Ein Podcast-Eintrag braucht einen Feed, ein Sender einen
        Stream. Waere die Art falsch, wuerde dialos-radio.py den Feed als
        Stream abspielen - und der Nutzer hoerte XML-Rauschen oder
        nichts."""
        for eintrag in self.nachrichten:
            with self.subTest(sender=eintrag["name"]):
                self.assertIn(eintrag["art"],
                              ("nachrichten-sender", "nachrichten-podcast"))
                self.assertTrue(eintrag["quelle"].startswith("http"))

    def test_oesterreich_laeuft_live(self):
        """Stephans Entscheidung vom 2026-10-05, und sie hat einen Grund:
        Fuer Oesterreich gibt es kein Kurznachrichten-Format als Podcast
        - der Oe3-Feed ist abgeschaltet, Oe1 Journale ist mit 60 Minuten
        ein ganzes Mittagsjournal."""
        at = [e for e in self.nachrichten if e.get("land") == "AT"]
        self.assertTrue(at)
        for eintrag in at:
            with self.subTest(sender=eintrag["name"]):
                self.assertEqual(eintrag["art"], "nachrichten-sender")


class Modulsuche(unittest.TestCase):
    """dialos-radio.py muss sein Modul finden, auch im Repo-Baum.

    Am 2026-10-05 endete `dialos-radio.py liste` auf dem Arbeitsrechner
    mit Rueckgabewert 1 und OHNE EIN WORT Ausgabe: Der Pfad zum Modul war
    fest auf /usr/local/bin verdrahtet, und der Fehlschlag ging nur ins
    Protokoll. Ein stiller Fehlschlag ist genau das, was dieses Projekt
    sonst ueberall vermeidet.
    """

    def test_modul_wird_neben_dem_programm_gefunden(self):
        radio = _laden("dialos-radio.py", "radio_suche_test")
        self.assertTrue(os.path.isfile(radio.SENDER_MODUL))
        self.assertEqual(os.path.dirname(radio.SENDER_MODUL), BIN)

    def test_fehlschlag_wird_gemeldet(self):
        """Nicht nur ins Protokoll, sondern auf stderr - wer von Hand
        prueft, muss den Grund sehen."""
        with open(os.path.join(BIN, "dialos-radio.py"), encoding="utf-8") as f:
            quelle = f.read()
        self.assertIn("file=sys.stderr", quelle)


if __name__ == "__main__":
    unittest.main()
