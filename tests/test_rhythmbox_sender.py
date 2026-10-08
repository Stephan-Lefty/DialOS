#!/usr/bin/env python3
"""
Tests fuer dialos_rhythmbox_sender.py - die Arbeit hinter DialOS-Rhythmbox.

Geprueft wird ausschliesslich, was OHNE NETZ entscheidbar ist: die Wahl
der Adresse, die Sprechform-Vorschlaege, die Kollisionswarnung, die
Normalisierung der Bundeslaender und das Ausgabeformat. Die Abfragen
gegen radio-browser.info sind bewusst nicht dabei - ein Test, der fremde
Server braucht, faellt aus, wenn deren Betreiber etwas aendert, und sagt
dann nichts ueber unseren Quelltext aus.

Dass wirklich nichts ins Netz geht, wird nicht behauptet, sondern
erzwungen: setUpModule() haengt urllib und subprocess Waechter davor.
Ein Test, der es doch versucht, faellt durch.

Jeder Testfall hier gehoert zu einem Fehler, der am 2026-09-25 wirklich
passiert ist - nachzulesen im Aenderungsprotokoll unter 0.5.3.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request

MODULPFAD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")
sys.path.insert(0, MODULPFAD)

import dialos_rhythmbox_sender as rs      # noqa: E402


_echtes_urlopen = urllib.request.urlopen
_echter_run = subprocess.run


def setUpModule():
    """Netz und fremde Programme sperren, solange die Tests laufen."""
    def kein_netz(*a, **k):
        raise AssertionError(
            "Dieser Test hat das Netz angefasst. Tests muessen ohne "
            "radio-browser.info und ohne ffprobe auskommen.")

    urllib.request.urlopen = kein_netz
    subprocess.run = kein_netz


def tearDownModule():
    urllib.request.urlopen = _echtes_urlopen
    subprocess.run = _echter_run


class FreieZugaenglichkeit(unittest.TestCase):
    """Stephans Vorgabe vom 2026-09-25: „Wichtig ist das die Sender alle
    frei zugaenglich sind. Ohne einen Account oder so."

    Eine Adresse mit Sitzungskennung spielt im Augenblick oft noch - und
    verstummt Wochen spaeter ohne erkennbaren Grund. Fuer einen blinden
    Nutzer ist das der schlimmste Fehlerfall, weil er nicht nachsehen kann.
    """

    def test_sitzungskennung_erkannt(self):
        for url in [
            "https://f121.rndfnk.com/ard/swr/swr2/live/aac/96/stream.aac?sid=3K39",
            "http://beispiel.de/stream?token=abc",
            "http://beispiel.de/stream?aggregator=web&auth=xyz",
            "http://beispiel.de/stream?expires=1759190400",
            "http://beispiel.de/stream?listenerId=42",
        ]:
            with self.subTest(url=url):
                self.assertTrue(rs.braucht_zugang(url))

    def test_zugangsdaten_in_der_adresse(self):
        # http://name:wort@host/ - kommt in der Datenbank wirklich vor.
        self.assertTrue(rs.braucht_zugang("http://max:geheim@beispiel.de/stream"))

    def test_freie_adressen_bleiben_frei(self):
        for url in [
            "https://liveradio.swr.de/sw331ch/swr2/play.mp3",
            "http://onair.krone.at/kronehit.mp3",
            "http://radioeins.de/stream",
            # "aggregator" und "quality" sind harmlose Parameter. Frueher
            # haette ein zu grobes Muster sie mitgefangen und brauchbare
            # Sender aussortiert.
            "https://beispiel.de/stream?aggregator=web&quality=high",
        ]:
            with self.subTest(url=url):
                self.assertFalse(rs.braucht_zugang(url))

    def test_ersatzadressen_sind_selbst_frei(self):
        """Ein Ersatz mit Sitzungskennung waere schlimmer als keiner -
        er wuerde genau den Fehler festschreiben, den er beheben soll."""
        for name, url in rs.ERSATZ_ADRESSEN.items():
            with self.subTest(sender=name):
                self.assertFalse(rs.braucht_zugang(url))
                self.assertFalse(rs.ist_playlist(url))
                self.assertTrue(url.startswith(("http://", "https://")))


class Adresswahl(unittest.TestCase):
    """beste_adresse() - am 2026-09-25 an radioeins gelernt.

    radio-browser liefert zwei Felder. `url_resolved` ist meistens die
    bessere Wahl, bei der ARD-Verteilung aber gerade die falsche: Die
    Aufloesung haengt eine Sitzungskennung an, der rohe Einstieg
    (`http://radioeins.de/stream`) bleibt dauerhaft gueltig.
    """

    def test_aufgeloeste_adresse_ist_der_normalfall(self):
        sender = {"url": "http://beispiel.de/start",
                  "url_resolved": "https://cdn.beispiel.de/stream.mp3"}
        self.assertEqual(rs.beste_adresse(sender),
                         "https://cdn.beispiel.de/stream.mp3")

    def test_roher_einstieg_schlaegt_sitzungskennung(self):
        sender = {"url": "http://radioeins.de/stream",
                  "url_resolved": "https://f1.rndfnk.com/rbb/stream?sid=abc"}
        self.assertEqual(rs.beste_adresse(sender), "http://radioeins.de/stream")

    def test_beide_mit_kennung_bleibt_die_aufgeloeste(self):
        """Der SWR-Kultur-Fall: Ist auch die rohe Adresse verseucht, gibt
        es hier nichts zu retten. Der Aufrufer muss das merken - deshalb
        wird NICHT stillschweigend die rohe genommen."""
        sender = {"url": "https://a.de/stream?sid=1",
                  "url_resolved": "https://b.de/stream?sid=2"}
        self.assertEqual(rs.beste_adresse(sender), "https://b.de/stream?sid=2")
        self.assertTrue(rs.braucht_zugang(rs.beste_adresse(sender)))

    def test_nur_ein_feld_gefuellt(self):
        self.assertEqual(rs.beste_adresse({"url": "http://a.de/s",
                                           "url_resolved": ""}),
                         "http://a.de/s")
        self.assertEqual(rs.beste_adresse({"url": "",
                                           "url_resolved": "http://b.de/s"}),
                         "http://b.de/s")
        self.assertEqual(rs.beste_adresse({}), "")

    def test_leerzeichen_werden_abgeschnitten(self):
        self.assertEqual(rs.beste_adresse({"url_resolved": "  http://a.de/s  "}),
                         "http://a.de/s")


class FesterErsatz(unittest.TestCase):
    """adresse_waehlen() - der SWR-Kultur-Fall vom 2026-09-25.

    Bei diesem Sender tragen BEIDE Felder der Datenbank ein „sid", also
    kann beste_adresse() nichts retten. Am 2026-09-30 nachgesehen:
    `https://liveradio.swr.de/sw331ch/swr2/play.mp3` meldet sich als
    „SWR2 AAC 96" und ist der dauerhafte Einstieg - dass die
    ARD-Verteilung beim Aufloesen sid und token anhaengt, ist richtig so.
    """

    KAPUTT = {"url": "https://a.de/stream?sid=1",
              "url_resolved": "https://b.de/stream?sid=2"}

    def test_ersatz_wird_eingesetzt(self):
        url, hinweis = rs.adresse_waehlen("SWR Kultur", self.KAPUTT)
        self.assertEqual(url, rs.ERSATZ_ADRESSEN["SWR Kultur"])
        self.assertFalse(rs.braucht_zugang(url))
        self.assertIn("Ersatz", hinweis)

    def test_ohne_ersatz_bleibt_es_bei_der_warnung(self):
        """Ein Sender ohne hinterlegten Ersatz darf NICHT stillschweigend
        durchgehen - sonst verstummt er spaeter ohne erkennbaren Grund."""
        url, hinweis = rs.adresse_waehlen("Irgendein Sender", self.KAPUTT)
        self.assertTrue(rs.braucht_zugang(url))
        self.assertIn("Sitzungskennung", hinweis)

    def test_freie_adresse_bleibt_unberuehrt(self):
        """Repariert radio-browser.info den Eintrag, greift wieder die
        Datenbank. Der Ersatz faellt dann still aus dem Weg, statt eine
        irgendwann veraltete Adresse festzuschreiben."""
        heil = {"url": "", "url_resolved": "https://liveradio.swr.de/neu.mp3"}
        url, hinweis = rs.adresse_waehlen("SWR Kultur", heil)
        self.assertEqual(url, "https://liveradio.swr.de/neu.mp3")
        self.assertIsNone(hinweis)


class Verweise(unittest.TestCase):
    """ist_playlist() - der MDR-Fehler vom 2026-09-25.

    „MDR Aktuell" zeigte ueber eine .m3u-Datei auf einen Eintrag, hinter
    dem sich MDR KULTUR meldete. Aufgefallen ist das nur ueber den
    ICY-Namen. Seitdem werden blosse Verweise abgewertet: Sie sagen
    nichts darueber aus, was am Ende wirklich spielt.
    """

    def test_verweise_erkannt(self):
        for url in ["http://a.de/liste.m3u", "http://a.de/liste.M3U",
                    "http://a.de/liste.pls", "http://a.de/live.m3u8",
                    "http://a.de/liste.asx",
                    "http://a.de/liste.m3u?cb=123"]:
            with self.subTest(url=url):
                self.assertTrue(rs.ist_playlist(url))

    def test_streams_sind_keine_verweise(self):
        for url in ["http://a.de/stream.mp3", "http://a.de/stream",
                    "https://a.de/live.aac", "http://a.de/m3u-archiv/s.mp3"]:
            with self.subTest(url=url):
                self.assertFalse(rs.ist_playlist(url))


class Guete(unittest.TestCase):
    """Die Sortierung entscheidet, welcher von mehreren gleichnamigen
    Eintraegen in die Liste kommt. Geprueft wird die Reihenfolge, nicht
    der Zahlenwert - der Schluessel darf sich aendern, das Ergebnis nicht.
    """

    @staticmethod
    def _sender(url, **rest):
        eintrag = {"url": "", "url_resolved": url, "codec": "MP3",
                   "bitrate": 128, "votes": 0}
        eintrag.update(rest)
        return eintrag

    def test_sitzungskennung_landet_ganz_hinten(self):
        frei = self._sender("https://a.de/s.mp3")
        gebunden = self._sender("https://b.de/s.mp3?sid=1", votes=99999)
        self.assertEqual(sorted([gebunden, frei], key=rs.guete)[0], frei)

    def test_verweis_hinter_echtem_stream(self):
        stream = self._sender("https://a.de/s.mp3")
        verweis = self._sender("https://b.de/l.m3u", votes=99999)
        self.assertEqual(sorted([verweis, stream], key=rs.guete)[0], stream)

    def test_mp3_vor_anderen_formaten(self):
        mp3 = self._sender("https://a.de/s.mp3", codec="MP3")
        aac = self._sender("https://b.de/s.aac", codec="AAC")
        self.assertEqual(sorted([aac, mp3], key=rs.guete)[0], mp3)

    def test_https_vor_http(self):
        sicher = self._sender("https://a.de/s.mp3")
        unsicher = self._sender("http://b.de/s.mp3")
        self.assertEqual(sorted([unsicher, sicher], key=rs.guete)[0], sicher)

    def test_unsinnige_bitrate_hilft_nicht(self):
        """Angaben ueber 256 kbit/s sind in der Datenbank fast immer
        Unsinn (Werte wie 999999). Sie duerfen einen Eintrag nicht nach
        vorne bringen."""
        echt = self._sender("https://a.de/s.mp3", bitrate=192)
        behauptet = self._sender("https://b.de/s.mp3", bitrate=999999)
        self.assertEqual(sorted([behauptet, echt], key=rs.guete)[0], echt)


class Sprechformen(unittest.TestCase):
    """sprechform_vorschlag() - die Regeln aus docs/medienliste.md,
    so weit sie sich automatisch anwenden lassen."""

    def test_abkuerzungen_werden_buchstabiert(self):
        self.assertEqual(rs.sprechform_vorschlag("WDR 2"), "we de er zwei")
        self.assertEqual(rs.sprechform_vorschlag("MDR Sachsen"), "em de er sachsen")
        # "ef" steht NICHT im Wortschatz des kleinen Modells, "f" schon
        # (2026-09-30 gemessen; deckt sich mit Stephans Buchstaben-Messung
        # vom 2026-09-21, wo "ef", "vau" und "ix" fehlten).
        self.assertEqual(rs.sprechform_vorschlag("SRF 1"), "es er f eins")

    def test_ziffern_werden_ausgeschrieben(self):
        self.assertEqual(rs.sprechform_vorschlag("Bayern 3"), "bayern drei")
        self.assertEqual(rs.sprechform_vorschlag("SWR3"), "es we er drei")

    def test_gewoehnliche_namen_werden_nur_klein(self):
        self.assertEqual(rs.sprechform_vorschlag("Antenne Bayern"), "antenne bayern")
        self.assertEqual(rs.sprechform_vorschlag("Rock Antenne"), "rock antenne")

    def test_tabelle_schlaegt_die_regel(self):
        """Was sich nicht ableiten laesst, steht in SPRECHFORMEN - und
        muss Vorrang haben. „ORF Radio Salzburg" heisst im Alltag nur
        „radio salzburg"; das vorangestellte „o er ef" spricht niemand.
        Tirol ist seit 2026-10-08 „tiroler radio" - „radio tirol" lag zu
        nah an „radio einschalten"."""
        self.assertEqual(rs.sprechform_vorschlag("ORF Radio Salzburg"), "radio salzburg")
        self.assertEqual(rs.sprechform_vorschlag("ORF Radio Tirol"), "tiroler radio")
        self.assertEqual(rs.sprechform_vorschlag("Life Radio"), "life")
        self.assertEqual(rs.sprechform_vorschlag("1LIVE"), "eins live")
        self.assertEqual(rs.sprechform_vorschlag("Hitradio Oe3"), "ö drei")

    def test_keine_ascii_umschreibungen(self):
        """DIE TEURE LEHRE VOM 2026-09-30.

        Der Quelltext dieses Moduls kommt sonst ohne Umlaute aus, und die
        Sprechformen waren deshalb ebenfalls umschrieben: "kaernten",
        "zuerich", "fuenf", "oe". Gegen vosk-model-small-de-0.15 gemessen
        fehlt JEDE dieser Umschreibungen im Wortschatz, waehrend die
        Umlautfassung vorhanden ist. Vosk wirft ein fehlendes Wort STILL
        aus der Grammatik - 25 der 78 Sender waeren per Sprache
        unerreichbar gewesen, ohne dass irgendwo ein Fehler erschienen
        waere.
        """
        verdaechtig = ("ae", "oe", "ue", "ss")
        for land in rs.SENDER:
            for eintrag in rs.SENDER[land]:
                form = rs.sprechform_vorschlag(eintrag[0])
                for wort in form.split():
                    # "news", "blues", "premiere" und aehnliche sind echte
                    # Woerter mit diesen Buchstabenfolgen - geprueft wird
                    # deshalb gegen die Liste der bekannten Umschreibungen.
                    with self.subTest(sender=eintrag[0], wort=wort):
                        self.assertNotIn(
                            wort, ("kaernten", "zuerich", "wuerttemberg",
                                   "fuenf", "oberoesterreich",
                                   "niederoesterreich", "oe", "ef", "vau",
                                   "ix", "uepsilon", "zet"),
                            f"{eintrag[0]}: '{wort}' fehlt im Wortschatz")
        self.assertTrue(verdaechtig)      # Doku der geprueften Muster

    def test_immer_ein_ergebnis(self):
        """Der Vorschlag darf nie leer sein - ein leeres Feld in der
        Oberflaeche sieht aus wie ein Programmfehler."""
        for name in ["...", "???", "8", "X", "Radio!"]:
            with self.subTest(name=name):
                self.assertTrue(rs.sprechform_vorschlag(name).strip())

    def test_nie_grossbuchstaben_im_ergebnis(self):
        """Die Grammatik der Spracherkennung ist durchgehend klein."""
        for land in rs.SENDER:
            for eintrag in rs.SENDER[land]:
                vorschlag = rs.sprechform_vorschlag(eintrag[0])
                with self.subTest(sender=eintrag[0]):
                    self.assertEqual(vorschlag, vorschlag.lower())


class Kollisionen(unittest.TestCase):
    """aehnliche_sprechformen() - docs/medienliste.md verlangt das
    ausdruecklich: „Keine zwei Eintraege, die aehnlich klingen."

    Der Nutzer kann nicht nachsehen, was gerade laeuft. Zwei
    verwechselbare Saetze heissen deshalb: Er bekommt gelegentlich den
    falschen Sender und erfaehrt nie, warum.
    """

    @staticmethod
    def _liste(*sprechformen):
        return [{"sprechform": s} for s in sprechformen]

    def test_gleiche_sprechform(self):
        paare = rs.aehnliche_sprechformen(self._liste("radio eins", "radio eins"))
        self.assertEqual(len(paare), 1)
        self.assertEqual(paare[0][2], "gleich")

    def test_eine_steckt_in_der_anderen(self):
        """Der gefaehrlichere Fall: Die Erkennung schlaegt schon beim
        kuerzeren Satz zu, der laengere ist damit unerreichbar."""
        paare = rs.aehnliche_sprechformen(self._liste("radio tirol",
                                                      "radio tirol sued"))
        self.assertEqual(len(paare), 1)
        self.assertEqual(paare[0][2], "eine steckt in der anderen")

    def test_umlaute_zaehlen_als_gleich(self):
        """„kaernten" und „kärnten" sind derselbe Laut - die Schreibweise
        darf die Warnung nicht aushebeln."""
        paare = rs.aehnliche_sprechformen(self._liste("radio kärnten",
                                                      "radio kaernten"))
        self.assertEqual(len(paare), 1)

    def test_echter_fund_vom_25_september(self):
        """Ueber die 78 gesammelten Sender meldete die Pruefung elf Paare,
        darunter dieses. Es steht hier als Beleg, dass die Schwelle nicht
        zu lasch eingestellt ist."""
        paare = rs.aehnliche_sprechformen(self._liste("we de er zwei",
                                                      "en de er zwei"))
        self.assertEqual(len(paare), 1)

    def test_deutlich_verschiedenes_wird_nicht_gemeldet(self):
        paare = rs.aehnliche_sprechformen(
            self._liste("deutschlandfunk", "antenne bayern", "oe drei",
                        "klassik radio"))
        self.assertEqual(paare, [])

    def test_leere_sprechform_wird_uebersprungen(self):
        """Ein leeres Feld ist kein Kollisionspartner, sonst waeren zwei
        noch nicht ausgefuellte Zeilen sofort „gleich"."""
        paare = rs.aehnliche_sprechformen(self._liste("", "", "radio eins"))
        self.assertEqual(paare, [])

    def test_liste_bleibt_unveraendert(self):
        eintraege = self._liste("radio eins", "radio eins")
        rs.aehnliche_sprechformen(eintraege)
        self.assertEqual(eintraege, self._liste("radio eins", "radio eins"))


class Bundeslaender(unittest.TestCase):
    """Die Normalisierungstabelle ist der eigentliche Nutzen der Suche.

    Das Feld „state" wird von Hand gepflegt: Am 2026-09-25 standen allein
    fuer Deutschland 53 Schreibweisen mit mindestens vier Sendern.
    Nordrhein-Westfalen liefert ueber sechs Schreibweisen 494 Sender,
    ueber die amtliche allein nur 72.
    """

    def test_alle_laender_vertreten(self):
        self.assertEqual(set(rs.BUNDESLAENDER), set(rs.LAENDER))
        self.assertEqual(set(rs.STAEDTE), set(rs.LAENDER))

    def test_anzahl_stimmt(self):
        self.assertEqual(len(rs.BUNDESLAENDER["Deutschland"]), 16)
        self.assertEqual(len(rs.BUNDESLAENDER["Oesterreich"]), 9)

    def test_jedes_bundesland_hat_brauchbare_schreibweisen(self):
        """Mindestens eine, keine leere, keine doppelte.

        Eine feste Mindestzahl waere falsch: „Hamburg", „Salzburg" und
        „Zug" heissen in jeder Sprache gleich, da gibt es nichts zu
        normalisieren. Und der Schluessel muss NICHT selbst ein
        Suchbegriff sein - „Unterwalden" ist der Menuename fuer die
        beiden Halbkantone Obwalden und Nidwalden.
        """
        for land, tabelle in rs.BUNDESLAENDER.items():
            for name, schreibweisen in tabelle.items():
                with self.subTest(land=land, bundesland=name):
                    self.assertTrue(schreibweisen)
                    self.assertTrue(all(w.strip() for w in schreibweisen))
                    klein = [w.lower() for w in schreibweisen]
                    self.assertEqual(len(set(klein)), len(klein))

    def test_umlaute_haben_eine_ascii_fassung(self):
        """Hier liegt der eigentliche Nutzen der Tabelle.

        In radio-browser.info tippt jeder, was seine Tastatur hergibt -
        „Baden-Wuerttemberg" und „Baden-Wurttemberg" stehen neben der
        amtlichen Schreibweise. Wer nur nach dem Umlaut sucht, verliert
        genau die Eintraege, die von auslaendischen Tastaturen stammen.
        """
        umlaute = "äöüÄÖÜß"
        for land, tabelle in rs.BUNDESLAENDER.items():
            for name, schreibweisen in tabelle.items():
                if not any(z in name for z in umlaute):
                    continue
                with self.subTest(land=land, bundesland=name):
                    self.assertTrue(
                        any(not any(z in w for z in umlaute)
                            for w in schreibweisen),
                        f"{name} hat keine Schreibweise ohne Umlaut")

    def test_keine_doppelten_schreibweisen_je_land(self):
        """Eine Schreibweise, die zwei Bundeslaendern zugeordnet ist,
        wuerde dieselben Sender beiden zuschlagen."""
        for land, tabelle in rs.BUNDESLAENDER.items():
            gesehen = {}
            for name, schreibweisen in tabelle.items():
                for wort in schreibweisen:
                    schluessel = wort.lower()
                    with self.subTest(land=land, schreibweise=wort):
                        self.assertNotIn(
                            schluessel, gesehen,
                            f"„{wort}" f"“ steht bei {name} und "
                            f"bei {gesehen.get(schluessel)}")
                    gesehen[schluessel] = name

    def test_unbekanntes_bundesland_wird_abgewiesen(self):
        """Ohne Netz pruefbar, weil der Fehler vor der Abfrage kommt."""
        with self.assertRaises(ValueError):
            rs.bundesland_suchen("Deutschland", "Tirol")

    def test_genres_haben_schlagwoerter(self):
        for name, schlagwoerter in rs.GENRES.items():
            with self.subTest(genre=name):
                self.assertTrue(schlagwoerter)

    def test_staedte_ohne_dubletten(self):
        """Aus dieser Tabelle fuellt die Filterleiste ihre Auswahl. Ein
        doppelter Eintrag waere dort zweimal dasselbe zum Anklicken."""
        for land, staedte in rs.STAEDTE.items():
            with self.subTest(land=land):
                self.assertTrue(staedte)
                klein = [s.lower() for s in staedte]
                self.assertEqual(len(set(klein)), len(klein))

    def test_stadt_nicht_zugleich_bundesland(self):
        """Berlin, Hamburg und Bremen sind beides. Sie stehen deshalb in
        BEIDEN Tabellen und erscheinen in der Filterleiste zweimal - einmal
        als Bundesland, einmal als Stadt mit dem Zusatz „(Näherung)". Das
        ist gewollt und keine Dublette: Die beiden Wege fragen die Datenbank
        verschieden ab und liefern verschieden viele Sender. Der Test haelt
        nur fest, dass es wirklich diese drei sind - taucht ein viertes auf,
        gehoert nachgesehen, ob das Absicht war.
        """
        doppelt = {land: sorted(set(rs.BUNDESLAENDER.get(land, {}))
                                & set(rs.STAEDTE.get(land, [])))
                   for land in rs.LAENDER}
        self.assertEqual(doppelt["Deutschland"], ["Berlin", "Bremen", "Hamburg"])
        self.assertEqual(doppelt["Oesterreich"], ["Salzburg", "Wien"])
        # In der Schweiz ist das die Regel, nicht die Ausnahme: Neun
        # Kantone heissen wie ihre Hauptstadt.
        self.assertEqual(
            doppelt["Schweiz"],
            ["Basel", "Bern", "Freiburg", "Genf", "Luzern", "Neuenburg",
             "Schaffhausen", "St. Gallen", "Zürich"])


class Zusammenfuehren(unittest.TestCase):
    """_zusammenfuehren() - Dubletten kosten Plaetze in einer Liste,
    die laut medienliste.md bewusst kurz bleiben soll."""

    @staticmethod
    def _treffer(uuid, url, **rest):
        eintrag = {"uuid": uuid, "url": url, "codec": "MP3", "stimmen": 0}
        eintrag.update(rest)
        return eintrag

    def test_gleiche_kennung_faellt_weg(self):
        ergebnis = rs._zusammenfuehren([
            self._treffer("u1", "https://a.de/s.mp3"),
            self._treffer("u1", "https://a.de/s.mp3"),
        ])
        self.assertEqual(len(ergebnis), 1)

    def test_gleiche_adresse_unter_zwei_kennungen(self):
        """Denselben Sender zweimal unter verschiedenen Kennungen gibt es
        in der Datenbank reichlich - deshalb zusaetzlich ueber die
        Adresse pruefen."""
        ergebnis = rs._zusammenfuehren([
            self._treffer("u1", "https://a.de/s.mp3"),
            self._treffer("u2", "https://a.de/s.mp3"),
        ])
        self.assertEqual(len(ergebnis), 1)

    def test_verschiedene_bleiben_erhalten(self):
        ergebnis = rs._zusammenfuehren([
            self._treffer("u1", "https://a.de/s.mp3"),
            self._treffer("u2", "https://b.de/s.mp3"),
        ])
        self.assertEqual(len(ergebnis), 2)

    def test_der_bessere_gewinnt(self):
        """Bei einer Dublette darf nicht der zufaellig erste bleiben,
        sondern der mit der brauchbareren Adresse."""
        ergebnis = rs._zusammenfuehren([
            self._treffer("u1", "https://a.de/liste.m3u", stimmen=500),
            self._treffer("u2", "https://a.de/liste.m3u", stimmen=1),
            self._treffer("u3", "https://b.de/s.mp3", stimmen=1),
        ])
        self.assertEqual(ergebnis[0]["url"], "https://b.de/s.mp3")

    def test_genrefilter(self):
        treffer = [
            {"name": "A", "schlagwoerter": "news,talk", "url": "https://a.de/s"},
            {"name": "B", "schlagwoerter": "techno", "url": "https://b.de/s"},
        ]
        gefiltert = rs.nach_genre_filtern(treffer, "Nachrichten und Wort")
        self.assertEqual([s["name"] for s in gefiltert], ["A"])


class Senderliste(unittest.TestCase):
    """Die kuratierte Liste selbst - Fehler darin faellt sonst erst am
    Geraet auf, und dort hoert der Nutzer den falschen Sender."""

    def test_muster_sind_uebersetzbar(self):
        for land, eintraege in rs.SENDER.items():
            for eintrag in eintraege:
                with self.subTest(sender=eintrag[0]):
                    re.compile(eintrag[1], re.I)
                    if len(eintrag) > 2:
                        re.compile(eintrag[2], re.I)

    def test_keine_doppelten_anzeigenamen(self):
        """Zwei gleiche Namen ergaeben zwei Zeilen, die der Nutzer nicht
        auseinanderhalten kann - und eine davon gewinnt per Zufall."""
        alle = [e[0] for land in rs.SENDER for e in rs.SENDER[land]]
        doppelt = {n for n in alle if alle.count(n) > 1}
        self.assertEqual(doppelt, set())

    def test_ersatzadressen_gehoeren_zu_bekannten_sendern(self):
        """Ein Ersatz fuer einen Sender, den es in der Liste nicht gibt,
        wuerde nie greifen - und das faellt sonst niemandem auf."""
        alle = {e[0] for land in rs.SENDER for e in rs.SENDER[land]}
        for name in rs.ERSATZ_ADRESSEN:
            with self.subTest(sender=name):
                self.assertIn(name, alle)

    def test_srg_sender_pruefen_die_adresse(self):
        """Bei der SRG heissen deutsche, franzoesische und italienische
        Fassung in der Datenbank teilweise gleich. Am 2026-09-25 landete
        deshalb die italienische Fassung in der Liste. Wer „Swiss"
        heisst, braucht das dritte Feld."""
        for eintrag in rs.SENDER["Schweiz"]:
            if eintrag[0].startswith("Radio Swiss"):
                with self.subTest(sender=eintrag[0]):
                    self.assertEqual(len(eintrag), 3)


class Ausgabeformat(unittest.TestCase):
    """medienliste_bauen() - das Format aus docs/medienliste.md.
    DialOS liest diese Datei spaeter direkt; ein umbenanntes Feld faellt
    erst dort auf."""

    PROBE = [{"name": "WDR 2", "land": "Deutschland",
              "url": "https://a.de/s.mp3", "uuid": "u1",
              "codec": "MP3", "bitrate": 128,
              "seite": "https://wdr.de", "logo": ""}]

    def test_aufbau(self):
        liste = rs.medienliste_bauen(self.PROBE)
        self.assertEqual(set(liste), {"stand", "eintraege"})
        self.assertRegex(liste["stand"], r"^\d{4}-\d{2}-\d{2}$")

    def test_felder_je_eintrag(self):
        eintrag = rs.medienliste_bauen(self.PROBE)["eintraege"][0]
        self.assertEqual(set(eintrag),
                         {"art", "sprechform", "name", "land", "quelle",
                          "stationuuid"})

    def test_land_als_kuerzel(self):
        """In der Medienliste steht das Kuerzel, nicht der ausgeschriebene
        Name - so steht es im Konzept."""
        eintrag = rs.medienliste_bauen(self.PROBE)["eintraege"][0]
        self.assertEqual(eintrag["land"], "DE")

    def test_sprechform_wird_ergaenzt_aber_nicht_ueberschrieben(self):
        eigene = [dict(self.PROBE[0], sprechform="mein sender")]
        gebaut = rs.medienliste_bauen(eigene)["eintraege"][0]
        self.assertEqual(gebaut["sprechform"], "mein sender")

        ohne = rs.medienliste_bauen(self.PROBE)["eintraege"][0]
        self.assertEqual(ohne["sprechform"], "we de er zwei")

    def test_stationuuid_ist_dabei(self):
        """Ein Feld mehr als urspruenglich vorgeschlagen: DialOS soll bei
        einem ausgefallenen Stream die aktuelle Adresse nachschlagen
        koennen. Ohne die Kennung geht das nicht."""
        eintrag = rs.medienliste_bauen(self.PROBE)["eintraege"][0]
        self.assertEqual(eintrag["stationuuid"], "u1")


class Uebergabestelle(unittest.TestCase):
    """Die zwei Ebenen der Medienliste - Beschluss vom 2026-09-30.

    Der Grund steht in der NIEMALS-Liste von dialos-aufspielen: Am
    2026-08-22 standen in `piper-generic.conf` Konfiguration UND die vom
    Nutzer gewaehlte Stimme in einer Datei; das naechste Aufspielen hat
    die Wahl stillschweigend zurueckgesetzt. Bei der Medienliste steht
    dieselbe Falle offen, und sie traefe den Nutzer haerter: Sein
    Lieblingssender waere weg, ohne dass er nachsehen koennte, warum.
    """

    def test_systemliste_liegt_im_aufgespielten_baum(self):
        """Nur was unter /usr/local/share liegt, nimmt dialos-aufspielen
        mit. `docs/medienliste.json` waere eine Sackgasse."""
        self.assertTrue(rs.SYSTEMLISTE.startswith("/usr/local/share/dialos/"))

    def test_repo_pfad_passt_zum_systempfad(self):
        """Beide Pfade muessen dieselbe Datei meinen, sonst spielt
        dialos-aufspielen sie an eine andere Stelle."""
        self.assertTrue(rs.REPO_TEILPFAD.endswith(
            rs.SYSTEMLISTE.lstrip("/").replace("/", os.sep)))

    def test_eigene_liste_im_konto(self):
        self.assertTrue(rs.eigene_liste().startswith(os.path.expanduser("~")))
        self.assertIn(os.path.join(".config", "dialos"), rs.eigene_liste())

    def test_repo_liste_wird_hier_gefunden(self):
        """Dieses Modul liegt im Repo-Baum, also muss die Suche greifen -
        sonst schluege die Oberflaeche am falschen Ort zu speichern vor."""
        repo = rs.repo_liste()
        self.assertIsNotNone(repo)
        self.assertTrue(os.path.isdir(os.path.dirname(repo)),
                        f"Zielordner fehlt: {os.path.dirname(repo)}")

    def test_speicherziel_bevorzugt_das_repo(self):
        self.assertEqual(rs.speicherziel(), rs.repo_liste())

    def test_persoenliche_eintraege_liegen_oben(self):
        """Wer einen Sender selbst aufnimmt, darf einen mitgelieferten
        ersetzen - sonst haette er zwei Eintraege mit demselben Satz."""
        with TempListen(
            system=[{"art": "radio", "sprechform": "radio eins",
                     "quelle": "https://alt.de/s.mp3"}],
            eigen=[{"art": "radio", "sprechform": "radio eins",
                    "quelle": "https://neu.de/s.mp3"}]) as (sys_pfad, eig_pfad):
            liste = rs.medienliste_lesen(systemweit=sys_pfad,
                                         persoenlich=eig_pfad)
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0]["quelle"], "https://neu.de/s.mp3")

    def test_beide_ebenen_werden_zusammengefuehrt(self):
        with TempListen(
            system=[{"art": "radio", "sprechform": "radio eins"}],
            eigen=[{"art": "radio", "sprechform": "antenne bayern"}]
        ) as (sys_pfad, eig_pfad):
            liste = rs.medienliste_lesen(systemweit=sys_pfad,
                                         persoenlich=eig_pfad)
        self.assertEqual({e["sprechform"] for e in liste},
                         {"radio eins", "antenne bayern"})

    def test_klanggleiche_eintraege_zaehlen_als_einer(self):
        """„radio kärnten" und „radio kaernten" sind derselbe Satz."""
        with TempListen(
            system=[{"art": "radio", "sprechform": "radio kaernten"}],
            eigen=[{"art": "radio", "sprechform": "radio kärnten"}]
        ) as (sys_pfad, eig_pfad):
            liste = rs.medienliste_lesen(systemweit=sys_pfad,
                                         persoenlich=eig_pfad)
        self.assertEqual(len(liste), 1)

    def test_fehlende_dateien_sind_der_normalfall(self):
        """Am frischen Geraet gibt es noch keine persoenliche Liste. Das
        darf nichts kosten und nichts melden."""
        liste = rs.medienliste_lesen(systemweit="/gibt/es/nicht.json",
                                     persoenlich="/auch/nicht.json")
        self.assertEqual(liste, [])

    def test_kaputte_datei_legt_nicht_das_radio_lahm(self):
        with TempListen(system=[{"art": "radio", "sprechform": "radio eins"}],
                        eigen="das ist kein JSON") as (sys_pfad, eig_pfad):
            liste = rs.medienliste_lesen(systemweit=sys_pfad,
                                         persoenlich=eig_pfad)
        self.assertEqual(len(liste), 1)

    def test_arten_stimmen_mit_der_doku_ueberein(self):
        """Die Gattungen stehen an zwei Stellen: als Konstante hier und
        als Beispiel in docs/medienliste.md. Laufen sie auseinander,
        schreibt die App ein „art", das DialOS spaeter nicht kennt - und
        der Eintrag faellt lautlos aus der Ansage."""
        doku = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs", "medienliste.md")
        with open(doku, encoding="utf-8") as f:
            text = f.read()
        genannt = set(re.findall(r'"art":\s*"([a-z-]+)"', text))
        self.assertTrue(genannt, "in medienliste.md steht kein Beispiel mehr")
        self.assertEqual(genannt, set(rs.ARTEN))

    def test_nach_gattung_filtern(self):
        """Radio, Nachrichten, Podcast und Hoerbuch stehen in DERSELBEN
        Datei und werden ueber `art` unterschieden."""
        with TempListen(
            system=[{"art": "radio", "sprechform": "radio eins"},
                    {"art": "podcast", "sprechform": "lage der nation"},
                    {"art": "hoerbuch", "sprechform": "die verwandlung"}],
            eigen=[]) as (sys_pfad, eig_pfad):
            nur_radio = rs.medienliste_lesen(art="radio", systemweit=sys_pfad,
                                             persoenlich=eig_pfad)
            alles = rs.medienliste_lesen(systemweit=sys_pfad,
                                         persoenlich=eig_pfad)
        self.assertEqual(len(nur_radio), 1)
        self.assertEqual(len(alles), 3)

    def test_doppelte_ueber_gattungsgrenzen_hinweg(self):
        """Der Nutzer spricht einen Satz, keine Gattung. Ein Podcast und
        ein Radiosender mit derselben Sprechform waeren fuer ihn
        ununterscheidbar - deshalb entdoppelt die Pruefung ueber alle
        Gattungen, auch wenn nachher nur eine abgefragt wird."""
        with TempListen(
            system=[{"art": "podcast", "sprechform": "radio eins"},
                    {"art": "radio", "sprechform": "radio eins"}],
            eigen=[]) as (sys_pfad, eig_pfad):
            liste = rs.medienliste_lesen(systemweit=sys_pfad,
                                         persoenlich=eig_pfad)
            radios = rs.medienliste_lesen(art="radio", systemweit=sys_pfad,
                                          persoenlich=eig_pfad)
        self.assertEqual(len(liste), 1)
        # Der Podcast stand zuerst und hat den Satz belegt; der
        # gleichnamige Radiosender faellt weg statt danebenzustehen.
        self.assertEqual(radios, [])


class LandDesGeraets(unittest.TestCase):
    """DialOS ist fuer Deutschland, Oesterreich UND die Schweiz.

    Stephan am 2026-10-05: „Wir muessen ja immer fuer 3 Laender denken" und
    „Das Land wuerde ich immer an die Nutzerdaten verknuepfen". Eine Liste,
    die auf jedem Geraet dasselbe anbietet, haette auf zwei Dritteln der
    Geraete Saetze, die ins Leere gehen - „radio tirol einschalten" nuetzt
    einem Schweizer Nutzer nichts.
    """

    def _daten(self, zeile):
        ordner = tempfile.mkdtemp(prefix="dialos-daten-")
        self.addCleanup(shutil.rmtree, ordner, True)
        pfad = os.path.join(ordner, "persoenliche-daten.txt")
        with open(pfad, "w", encoding="utf-8") as f:
            f.write("# Kommentar\nVorname: Max\n" + zeile + "\nOrt: Irgendwo\n")
        return pfad

    def test_schreibweisen_werden_erkannt(self):
        """Der Mensch tippt in die Maske, was ihm einfaellt."""
        for wert, erwartet in (("Deutschland", "DE"), ("DE", "DE"),
                               ("D", "DE"), ("Germany", "DE"),
                               ("Österreich", "AT"), ("Oesterreich", "AT"),
                               ("AT", "AT"), ("Austria", "AT"),
                               ("Schweiz", "CH"), ("CH", "CH"),
                               ("Suisse", "CH"), ("switzerland", "CH")):
            with self.subTest(wert=wert):
                self.assertEqual(
                    rs.land_des_geraets(self._daten(f"Land: {wert}")), erwartet)

    def test_leeres_feld_ist_kein_fehler(self):
        """Der Normalfall vor dem Ausfuellen. Der Aufrufer zeigt dann
        ALLES - ein leeres Feld darf das Radio nicht abschalten."""
        self.assertIsNone(rs.land_des_geraets(self._daten("Land:")))
        self.assertIsNone(rs.land_des_geraets(self._daten("Ort: Nur ein Ort")))

    def test_fehlende_datei_ist_kein_fehler(self):
        self.assertIsNone(rs.land_des_geraets("/gibt/es/nicht.txt"))

    def test_unbekanntes_land_schaltet_nicht_ab(self):
        """Steht dort „Italien", ist das kein DialOS-Land - aber der Nutzer
        soll trotzdem Radio hoeren koennen."""
        self.assertIsNone(rs.land_des_geraets(self._daten("Land: Italien")))

    def test_kommentarzeile_zaehlt_nicht(self):
        ordner = tempfile.mkdtemp(prefix="dialos-daten-")
        self.addCleanup(shutil.rmtree, ordner, True)
        pfad = os.path.join(ordner, "d.txt")
        with open(pfad, "w", encoding="utf-8") as f:
            f.write("# Land: Deutschland\nLand: Schweiz\n")
        self.assertEqual(rs.land_des_geraets(pfad), "CH")


class LandFilter(unittest.TestCase):
    """Die systemweite Liste ist der Vorrat, nicht das Angebot."""

    SENDER = [
        {"art": "radio", "sprechform": "deutschlandfunk", "land": "DE",
         "quelle": "https://a/1"},
        {"art": "radio", "sprechform": "radio tirol", "land": "AT",
         "quelle": "https://a/2"},
        {"art": "radio", "sprechform": "radio swiss jazz", "land": "CH",
         "quelle": "https://a/3"},
        # Ohne Land - etwa ein Podcast, der an kein Land gebunden ist.
        {"art": "podcast", "sprechform": "lage der nation",
         "quelle": "https://a/4"},
    ]

    def test_nur_das_eigene_land(self):
        with TempListen(system=self.SENDER, eigen=[]) as (sysp, eigp):
            liste = rs.medienliste_lesen(art="radio", systemweit=sysp,
                                         persoenlich=eigp, land="AT")
        self.assertEqual([e["sprechform"] for e in liste], ["radio tirol"])

    def test_ohne_land_gilt_alles(self):
        """None heisst: nichts ausgefuellt - dann wird nichts versteckt."""
        with TempListen(system=self.SENDER, eigen=[]) as (sysp, eigp):
            liste = rs.medienliste_lesen(art="radio", systemweit=sysp,
                                         persoenlich=eigp, land=None)
        self.assertEqual(len(liste), 3)

    def test_eintrag_ohne_landfeld_gilt_ueberall(self):
        with TempListen(system=self.SENDER, eigen=[]) as (sysp, eigp):
            liste = rs.medienliste_lesen(art="podcast", systemweit=sysp,
                                         persoenlich=eigp, land="CH")
        self.assertEqual([e["sprechform"] for e in liste], ["lage der nation"])

    def test_gleiche_sprechform_je_land_andere_quelle(self):
        """DER FUND VOM 2026-10-05, beim Bau der Nachrichten.

        „landesweite nachrichten" soll in Deutschland die tagesschau
        bringen, in der Schweiz SRF - also dieselbe Sprechform, je Land
        eine andere Quelle. Lief die Entdoppelung VOR dem Landfilter,
        ueberlebte nur der erste der drei Eintraege, und auf zwei
        Dritteln der Geraete zeigte der Satz ins Ausland oder fehlte.
        """
        drei = [
            {"art": "nachrichten-podcast", "sprechform": "landesweite nachrichten",
             "land": "DE", "quelle": "https://de/feed"},
            {"art": "nachrichten-sender", "sprechform": "landesweite nachrichten",
             "land": "AT", "quelle": "https://at/stream"},
            {"art": "nachrichten-podcast", "sprechform": "landesweite nachrichten",
             "land": "CH", "quelle": "https://ch/feed"},
        ]
        with TempListen(system=drei, eigen=[]) as (sysp, eigp):
            for land, erwartet in (("DE", "https://de/feed"),
                                   ("AT", "https://at/stream"),
                                   ("CH", "https://ch/feed")):
                with self.subTest(land=land):
                    liste = rs.medienliste_lesen(systemweit=sysp,
                                                 persoenlich=eigp, land=land)
                    self.assertEqual(len(liste), 1)
                    self.assertEqual(liste[0]["quelle"], erwartet)

    def test_ohne_land_bleibt_nur_einer(self):
        """Ohne gesetztes Land greift die Entdoppelung wie bisher - sonst
        stuenden drei gleichlautende Saetze in der Grammatik, und die
        Erkennung muesste raten."""
        drei = [{"art": "nachrichten-podcast", "sprechform": "landesweite nachrichten",
                 "land": k, "quelle": f"https://{k}/x"} for k in ("DE", "AT", "CH")]
        with TempListen(system=drei, eigen=[]) as (sysp, eigp):
            liste = rs.medienliste_lesen(systemweit=sysp, persoenlich=eigp,
                                         land=None)
        self.assertEqual(len(liste), 1)

    def test_eigene_auswahl_wird_nicht_gefiltert(self):
        """Wer einen auslaendischen Sender selbst aufnimmt, hat ihn
        gewollt. Ein Filter auf die eigene Eingabe waere dieselbe
        Anmassung wie eine ueberschriebene Stimmwahl."""
        eigen = [{"art": "radio", "sprechform": "bayern drei", "land": "DE",
                  "quelle": "https://b/1"}]
        with TempListen(system=self.SENDER, eigen=eigen) as (sysp, eigp):
            liste = rs.medienliste_lesen(art="radio", systemweit=sysp,
                                         persoenlich=eigp, land="CH")
        formen = [e["sprechform"] for e in liste]
        self.assertIn("bayern drei", formen)        # eigene Wahl bleibt
        self.assertIn("radio swiss jazz", formen)   # passendes Land
        self.assertNotIn("radio tirol", formen)     # fremdes Land, gefiltert


class TempListen:
    """Zwei Medienlisten in einem Wegwerf-Ordner."""

    def __init__(self, system, eigen):
        self.system, self.eigen = system, eigen

    def _schreiben(self, pfad, inhalt):
        with open(pfad, "w", encoding="utf-8") as f:
            if isinstance(inhalt, str):
                f.write(inhalt)
            else:
                json.dump({"stand": "2026-09-30", "eintraege": inhalt}, f,
                          ensure_ascii=False)

    def __enter__(self):
        self.ordner = tempfile.mkdtemp(prefix="dialos-medienliste-")
        sys_pfad = os.path.join(self.ordner, "system.json")
        eig_pfad = os.path.join(self.ordner, "eigen.json")
        self._schreiben(sys_pfad, self.system)
        self._schreiben(eig_pfad, self.eigen)
        return sys_pfad, eig_pfad

    def __exit__(self, *_):
        shutil.rmtree(self.ordner, ignore_errors=True)


class NetzSperre(unittest.TestCase):
    """Beweist, dass die Sperre oben wirklich greift - sonst waere die
    Zusicherung „laeuft ohne Netz" nur eine Behauptung."""

    def test_sperre_greift(self):
        with self.assertRaises(AssertionError):
            urllib.request.urlopen("https://de.api.radio-browser.info/")


if __name__ == "__main__":
    unittest.main()
