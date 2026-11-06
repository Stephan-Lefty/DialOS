#!/usr/bin/env python3
"""
Tests fuer das Herunterladen von Podcast-Folgen (dialos_podcast.py,
folge_herunterladen) und dafuer, dass die Nachrichten sie benutzen.

Die Probe am Geraet vom 2026-11-06: Rhythmbox spielt eine HTTPS-Adresse
nur, wenn sie in seiner Datenbank steht - jede neue Folge hiess also
Rhythmbox beenden, Datenbank beschreiben, neu starten, und das laufende
Radio brach ab. Als lokale Datei spielt dieselbe Folge sofort, ohne
Neustart. Seitdem werden Folgen heruntergeladen statt gestreamt.

Kein Netz, kein curl: Popen wird ersetzt.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import test_radio                          # noqa: E402
from test_radio import BIN, RadioBasis     # noqa: E402,F401

sys.path.insert(0, BIN)
import dialos_podcast as pod               # noqa: E402

setUpModule = test_radio.setUpModule
tearDownModule = test_radio.tearDownModule

AUDIO = "https://cdn.example.de/audio/2026/1106/AU-20261106-1106-4900.mp3"


class FalschesCurl:
    """Steht fuer curl: schreibt die Zieldatei, oder eben nicht."""

    aufrufe = []

    def __init__(self, befehl, inhalt=b"ID3 Ton", rueckgabe=0, langsam=False):
        FalschesCurl.aufrufe.append(befehl)
        self.ziel = befehl[befehl.index("-o") + 1]
        self.rueckgabe = rueckgabe
        self.langsam = langsam
        self.getoetet = False
        if inhalt:
            with open(self.ziel, "wb") as f:
                f.write(inhalt)

    def wait(self, timeout=None):
        if self.langsam:
            self.langsam = False
            raise subprocess.TimeoutExpired("curl", timeout)
        return self.rueckgabe

    def kill(self):
        self.getoetet = True


class Herunterladen(unittest.TestCase):

    def setUp(self):
        self.wurzel = tempfile.mkdtemp(prefix="dialos-folgen-test-")
        self.addCleanup(shutil.rmtree, self.wurzel, True)
        FalschesCurl.aufrufe = []
        self.echt = subprocess.Popen
        self.addCleanup(setattr, subprocess, "Popen", self.echt)
        self.art = {}
        subprocess.Popen = lambda befehl, **kw: FalschesCurl(befehl, **self.art)

    def holen(self, audio=AUDIO, **kw):
        return pod.folge_herunterladen(audio, "tagesschau in 100 Sekunden",
                                       wurzel=self.wurzel, **kw)

    def test_liegt_danach_als_datei_da(self):
        pfad, meldung = self.holen()
        self.assertEqual(meldung, "")
        self.assertTrue(pfad.endswith(".mp3"))
        with open(pfad, "rb") as f:
            self.assertEqual(f.read(), b"ID3 Ton")
        self.assertEqual([d for d in os.listdir(os.path.dirname(pfad))
                          if d.endswith(".teil")], [])

    def test_zweimal_dieselbe_folge_wird_nicht_neu_geholt(self):
        self.holen()
        self.holen()
        self.assertEqual(len(FalschesCurl.aufrufe), 1)

    def test_neue_folge_loescht_die_alte(self):
        alt, _ = self.holen()
        neu, _ = self.holen(AUDIO.replace("1106-4900", "1206-5000"))
        self.assertNotEqual(alt, neu)
        self.assertFalse(os.path.exists(alt))
        self.assertEqual(os.listdir(os.path.dirname(neu)), [os.path.basename(neu)])

    def test_fehlschlag_hinterlaesst_nichts(self):
        self.art = {"rueckgabe": 22}
        pfad, meldung = self.holen()
        self.assertEqual(pfad, "")
        self.assertIn("22", meldung)
        ordner = os.path.join(self.wurzel, "tagesschau-in-100-sekunden")
        self.assertEqual(os.listdir(ordner), [])

    def test_leere_antwort_gilt_als_fehlschlag(self):
        self.art = {"inhalt": b""}
        pfad, meldung = self.holen()
        self.assertEqual(pfad, "")
        self.assertTrue(meldung)

    def test_lange_wartezeit_wird_angesagt(self):
        self.art = {"langsam": True}
        angesagt = []
        pfad, _ = self.holen(bei_wartezeit=lambda: angesagt.append(True))
        self.assertEqual(angesagt, [True])
        self.assertTrue(os.path.isfile(pfad))

    def test_kurze_folge_bleibt_still(self):
        angesagt = []
        self.holen(bei_wartezeit=lambda: angesagt.append(True))
        self.assertEqual(angesagt, [])

    def test_ordnername_ohne_umlaute_und_leerzeichen(self):
        self.assertEqual(pod._ordnername("Ö1 Betrifft: Geschichte"),
                         "oe1-betrifft-geschichte")
        self.assertEqual(pod._ordnername("???"), "podcast")


class NachrichtenAlsDatei(RadioBasis):
    """Die Nachrichten holen die Folge als Datei - ohne Rhythmbox-Neustart."""

    SENDER = RadioBasis.SENDER + [
        {"art": "nachrichten-podcast", "sprechform": "landesweite nachrichten",
         "name": "tagesschau in 100 Sekunden",
         "quelle": "https://www.tagesschau.de/feed.xml"},
    ]

    def setUp(self):
        super().setUp()
        test = self
        self.geholt = []

        class Pod:
            def feed_holen(self, url):
                return "<rss/>", ""

            def feed_lesen(self, text):
                return {}, [{"titel": "100 Sekunden", "audio": AUDIO,
                             "datum": 1.0, "dauer": 135}], ""

            def neueste_folge(self, folgen, mindestdauer=0):
                return folgen[0]

            def folge_herunterladen(self, audio, name, bei_wartezeit=None):
                test.geholt.append((audio, name))
                return os.path.join(test.ordner, "folgen", "a b.mp3"), ""

        self.radio.podcast_modul = lambda: Pod()
        # Kein echter Player, kein Waechter-Prozess.
        self.radio.wiedergabe_status = lambda: ""
        self.radio.nachrichten_waechter_starten = lambda uri, vorher: None

    def test_spielt_die_datei_nicht_die_adresse(self):
        self.assertEqual(self.radio.nachrichten(self.rs, "landesweite nachrichten"), 0)
        self.assertEqual(self.geholt, [(AUDIO, "tagesschau in 100 Sekunden")])
        self.assertEqual(len(self.gespielt), 1)
        self.assertTrue(self.gespielt[0].startswith("file://"))
        self.assertTrue(self.gespielt[0].endswith("/a%20b.mp3"))

    def test_kein_neustart_und_kein_datenbank_eintrag(self):
        # Der Fehler vom 2026-10-08: Jede neue Folge beendete Rhythmbox.
        self.radio.nachrichten(self.rs, "landesweite nachrichten")
        self.assertNotIn(("--quit",), self.gerufen)
        self.assertFalse(os.path.exists(self.radio.RHYTHMDB))

    def test_erst_ansage_dann_wiedergabe(self):
        # Stephans Frage vom 2026-11-06: Lief die Folge zuerst, schaltete die
        # Ansage sie stumm - die ersten drei Sekunden gingen verloren.
        ablauf = []
        self.radio.sprich = lambda text: ablauf.append(("sagt", text))
        self.radio.client = lambda *a, **k: ablauf.append(("spielt",) + a) or True
        self.radio.nachrichten(self.rs, "landesweite nachrichten")
        arten = [schritt[0] for schritt in ablauf]
        self.assertEqual(arten, ["sagt", "spielt"])
        self.assertEqual(ablauf[0][1], "tagesschau in 100 Sekunden.")

    def test_rhythmbox_startet_schon_waehrend_der_ansage(self):
        # 2026-11-06: 2,3 s Pause nach der Ansage, solange Rhythmbox startete.
        ablauf = []
        self.radio.laeuft = lambda: False
        self.radio.vorwaermen = lambda: ablauf.append("vorwaermen")
        self.radio.sprich = lambda text: ablauf.append("sagt")
        self.radio.client = lambda *a, **k: ablauf.append(a[0]) or True
        self.radio.nachrichten(self.rs, "landesweite nachrichten")
        self.assertEqual(ablauf, ["vorwaermen", "sagt", "--play-uri"])

    def test_vorwaermen_haelt_nichts_an(self):
        # 2026-11-06: "--pause" kam bei kaltem Rhythmbox erst NACH dem Start
        # des Senders an und hielt ihn nach 0,4 s wieder an.
        aufrufe = []
        echt = subprocess.Popen
        self.addCleanup(setattr, subprocess, "Popen", echt)
        subprocess.Popen = lambda befehl, **kw: aufrufe.append(befehl) or None
        radio = test_radio._laden("dialos-radio.py", "radio_vorwaermen")
        radio.laeuft = lambda: False
        radio.melde = lambda t: None
        radio.vorwaermen()
        self.assertEqual(len(aufrufe), 1)
        self.assertNotIn("--pause", aufrufe[0])
        self.assertNotIn("--play", aufrufe[0])
        self.assertIn("--print-playing", aufrufe[0])

    def test_fehlgeschlagenes_holen_wird_gesagt(self):
        self.radio.podcast_modul().__class__.folge_herunterladen = \
            lambda s, a, n, bei_wartezeit=None: ("", "curl 6")
        self.assertEqual(self.radio.nachrichten(self.rs, "landesweite nachrichten"), 1)
        self.assertIn("Ich konnte die Nachrichten nicht laden.", self.gesagt)
        self.assertEqual(self.gespielt, [])


class NachDenNachrichten(RadioBasis):
    """Stephan, 2026-11-06: Nach dem Ende kam nur Stille - auch das Radio von
    vorher nicht. Jetzt fragt Michael oder sagt, dass es zu Ende ist."""

    def setUp(self):
        super().setUp()
        self.radio.CACHE = os.path.join(self.ordner, "cache")
        self.radio.WAECHTER = os.path.join(self.radio.CACHE, "waechter")
        self.radio.RADIO_AUS_DATEI = os.path.join(self.radio.CACHE, "radio-aus")
        self.status = ["Playing", "Playing", "Stopped"]
        self.adresse = "file:///folge.mp3"
        self.radio.wiedergabe_status = lambda: self.status.pop(0) if self.status else "Stopped"
        self.radio.laufende_adresse = lambda: self.adresse
        self.fragen = []
        self.antwort = True
        test = self

        class Notiz:
            def mit_rueckfrage(self, frage, bei_nein, bei_nichts):
                test.fragen.append(frage)
                return test.antwort
        self.radio.rueckfrage_modul = lambda: Notiz()

    def ende(self, vorher=""):
        return self.radio.nachrichten_ende("file:///folge.mp3", vorher, warten=0)

    def test_ohne_radio_vorher_nur_der_hinweis(self):
        self.ende()
        self.assertEqual(self.gesagt, ["Die Nachrichten sind zu Ende."])
        self.assertEqual(self.fragen, [])

    def test_mit_radio_vorher_wird_gefragt(self):
        self.ende("ö drei")
        self.assertEqual(len(self.fragen), 1)
        self.assertIn("Soll ich Hitradio Ö3 wieder einschalten?", self.fragen[0])
        self.assertTrue(self.fragen[0].endswith("Sage ja oder nein."))
        self.assertEqual(self.gespielt, ["https://b.at/oe3.mp3"])

    def test_bei_nein_bleibt_es_still(self):
        self.antwort = False
        self.ende("ö drei")
        self.assertEqual(self.gespielt, [])

    def test_vom_nutzer_abgestellt_kein_hinweis(self):
        os.makedirs(self.radio.CACHE, exist_ok=True)
        self.status = ["Playing"] * 50
        echt = self.radio.wiedergabe_status

        def status():
            open(self.radio.RADIO_AUS_DATEI, "w").close()
            return echt()
        self.radio.wiedergabe_status = status
        self.ende("ö drei")
        self.assertEqual(self.gesagt, [])
        self.assertEqual(self.fragen, [])

    def test_umgeschaltet_kein_hinweis(self):
        self.status = ["Playing"] * 5
        self.adresse = "https://a.de/dlf.mp3"
        self.ende("ö drei")
        self.assertEqual(self.gesagt, [])
        self.assertEqual(self.fragen, [])

    def test_neuere_nachrichten_uebernehmen(self):
        echt = self.radio.wiedergabe_status

        def status():
            with open(self.radio.WAECHTER, "w") as f:
                f.write("anderer")
            return echt()
        self.radio.wiedergabe_status = status
        self.ende()
        self.assertEqual(self.gesagt, [])

    def test_ausschalten_setzt_die_marke(self):
        self.radio.client = lambda *a, **k: True
        self.radio.ausschalten()
        self.assertTrue(os.path.exists(self.radio.RADIO_AUS_DATEI))


class WaechterWirdGestartet(NachrichtenAlsDatei):

    def test_merkt_sich_den_sender_von_vorher(self):
        gestartet = []
        self.radio.nachrichten_waechter_starten = lambda uri, vorher: gestartet.append((uri, vorher))
        self.radio.wiedergabe_status = lambda: "Playing"
        self.radio.laufende_adresse = lambda: "https://b.at/oe3.mp3"
        self.radio.nachrichten(self.rs, "landesweite nachrichten")
        self.assertEqual(len(gestartet), 1)
        self.assertTrue(gestartet[0][0].startswith("file://"))
        self.assertEqual(gestartet[0][1], "ö drei")


if __name__ == "__main__":
    unittest.main()
