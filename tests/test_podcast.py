#!/usr/bin/env python3
"""
Tests fuer dialos_podcast.py - das Lesen und Pruefen von RSS-Feeds.

Geprueft wird die Zerlegung, nicht das Abrufen: Der Feed kommt als Text
in den Test, nicht aus dem Netz. Damit bleiben die Faelle pruefbar, die
im Betrieb wirklich vorkommen - darunter der Fund vom 2026-10-05, dass
ein Feed 39 Eintraege und kein einziges Audio haben kann.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import importlib.util
import os
import subprocess
import sys
import unittest
import urllib.request

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")
sys.path.insert(0, BIN)

import dialos_podcast as pod               # noqa: E402

_echtes_urlopen = urllib.request.urlopen
_echter_run = subprocess.run


def setUpModule():
    def kein_netz(*a, **k):
        raise AssertionError("Dieser Test hat das Netz oder ein fremdes "
                             "Programm angefasst.")
    urllib.request.urlopen = kein_netz
    subprocess.run = kein_netz


def tearDownModule():
    urllib.request.urlopen = _echtes_urlopen
    subprocess.run = _echter_run


def feed(items, titel="Ein Podcast"):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
 <channel>
  <title>{titel}</title>
  <description>Beschreibung</description>
  {items}
 </channel>
</rss>"""


def item(titel, audio=None, datum=None, dauer=None):
    teile = [f"<title>{titel}</title>"]
    if audio:
        teile.append(f'<enclosure url="{audio}" type="audio/mpeg" '
                     'length="1000"/>')
    if datum:
        teile.append(f"<pubDate>{datum}</pubDate>")
    if dauer:
        teile.append(f"<itunes:duration>{dauer}</itunes:duration>")
    return "<item>" + "".join(teile) + "</item>"


class FeedLesen(unittest.TestCase):

    def test_einfacher_feed(self):
        kopf, folgen, meldung = pod.feed_lesen(
            feed(item("Folge 1", "https://a.de/1.mp3",
                      "Mon, 05 Oct 2026 08:00:00 +0200", "2:12")))
        self.assertEqual(meldung, "")
        self.assertEqual(kopf["titel"], "Ein Podcast")
        self.assertEqual(len(folgen), 1)
        self.assertEqual(folgen[0]["audio"], "https://a.de/1.mp3")
        self.assertEqual(folgen[0]["dauer"], 132)
        self.assertIsNotNone(folgen[0]["datum"])

    def test_feed_ohne_audio_ist_erkennbar(self):
        """DER FUND VOM 2026-10-05. Die Nachrichten-Feeds des
        Deutschlandfunks liefern 39 Eintraege und kein einziges
        <enclosure> - das sind Textartikel. Ein solcher Feed stuende in
        der Medienliste und machte nie einen Ton."""
        _, folgen, meldung = pod.feed_lesen(
            feed("".join(item(f"Artikel {i}") for i in range(39))))
        self.assertEqual(meldung, "")
        self.assertEqual(len(folgen), 39)
        self.assertEqual(sum(1 for f in folgen if f["audio"]), 0)
        self.assertIsNone(pod.neueste_folge(folgen))

    def test_html_statt_feed(self):
        """Der haeufigste Fehlgriff: Die Adresse zeigt auf eine
        Uebersichtsseite statt auf den Feed."""
        _, _, meldung = pod.feed_lesen(
            "<!DOCTYPE html><html><body>Podcast-Seite</body></html>")
        self.assertIn("HTML-Seite", meldung)

    def test_kaputtes_xml(self):
        _, _, meldung = pod.feed_lesen("<rss><channel><title>abgeschnitten")
        self.assertTrue(meldung)

    def test_leere_antwort(self):
        _, _, meldung = pod.feed_lesen("   ")
        self.assertEqual(meldung, "leere Antwort")

    def test_atom_wird_benannt_nicht_verschwiegen(self):
        """Atom kann das Modul nicht - das gehoert gesagt, statt einen
        leeren Feed zu melden."""
        _, _, meldung = pod.feed_lesen(
            '<feed xmlns="http://www.w3.org/2005/Atom"><title>A</title></feed>')
        self.assertIn("Atom", meldung)

    def test_neueste_zuerst(self):
        """Nach Datum sortiert, nicht in der Reihenfolge des Feeds."""
        _, folgen, _ = pod.feed_lesen(feed(
            item("alt", "https://a/1.mp3", "Mon, 28 Sep 2026 08:00:00 +0200")
            + item("neu", "https://a/2.mp3", "Mon, 05 Oct 2026 08:00:00 +0200")))
        self.assertEqual(folgen[0]["titel"], "neu")

    def test_ohne_datum_bleibt_die_reihenfolge(self):
        """Die meisten Anbieter stellen die neueste Folge nach vorn - das
        ist besser als zu raten."""
        _, folgen, _ = pod.feed_lesen(
            feed(item("zuerst", "https://a/1.mp3")
                 + item("danach", "https://a/2.mp3")))
        self.assertEqual(folgen[0]["titel"], "zuerst")

    def test_neueste_folge_ueberspringt_textbeitraege(self):
        """Manche Feeds mischen Text und Audio. Ein Eintrag ohne
        <enclosure> wuerde nur schweigen."""
        _, folgen, _ = pod.feed_lesen(
            feed(item("nur Text") + item("mit Ton", "https://a/2.mp3")))
        self.assertEqual(pod.neueste_folge(folgen)["titel"], "mit Ton")


class Mindestdauer(unittest.TestCase):
    """Der Befund vom 2026-10-08: Sieben der dreissig ausgewaehlten Feeds
    mischen Einzelbeitraege mit ganzen Sendungen. "Deutschlandfunk
    Hintergrund" reicht von 1 bis 19 Minuten, der WDR-Hoerspiel-Speicher
    von 6 bis 74. Wer blind die neueste Folge nimmt, spielt dem Nutzer
    irgendwann eine Ankuendigung statt eines Hoerspiels vor - und fuer
    jemanden, der den Bildschirm nicht sieht, ist das von einem Fehler
    nicht zu unterscheiden."""

    def test_schnipsel_wird_uebersprungen(self):
        _, folgen, _ = pod.feed_lesen(feed(
            item("Ankuendigung", "https://a/1.mp3", dauer="1:30")
            + item("die Sendung", "https://a/2.mp3", dauer="52:00")))
        self.assertEqual(
            pod.neueste_folge(folgen, mindestdauer=1200)["titel"],
            "die Sendung")

    def test_ohne_mindestdauer_bleibt_es_beim_alten_verhalten(self):
        """Das Feld ist freiwillig. 23 der 30 Eintraege haben keins, und
        fuer die darf sich nichts aendern."""
        _, folgen, _ = pod.feed_lesen(feed(
            item("Ankuendigung", "https://a/1.mp3", dauer="1:30")
            + item("die Sendung", "https://a/2.mp3", dauer="52:00")))
        self.assertEqual(pod.neueste_folge(folgen)["titel"], "Ankuendigung")

    def test_folge_ohne_dauerangabe_gilt_als_lang_genug(self):
        """DER WICHTIGSTE FALL. SR2 und hr2 Doppelkopf liefern gar kein
        itunes:duration (gemessen 2026-10-08). Wer am fehlenden Feld
        aussortiert, loescht den ganzen Podcast - lautlos, denn es sieht
        aus wie ein leerer Feed.

        DIE REIHENFOLGE IM FEED IST HIER ABSICHT, und sie ist eine
        Korrektur an mir selbst (2026-10-08): Die erste Fassung dieses
        Tests stellte NUR die Folge ohne Angabe hinein. Die
        Mutationsprobe hat ihn danach fuer gruen erklaert, obwohl der
        Filter die Folge verwarf - denn ohne Treffer fiel die Funktion
        auf "die neueste mit Audio" zurueck, und das war dieselbe
        Folge. Der Test prueft seitdem mit einem zu kurzen Eintrag
        davor: Wer die Folge ohne Angabe verwirft, landet bei "zu
        kurz" und faellt auf.
        """
        _, folgen, _ = pod.feed_lesen(feed(
            item("zu kurz", "https://a/1.mp3", dauer="2:00")
            + item("ohne Angabe", "https://a/2.mp3")))
        self.assertEqual(
            pod.neueste_folge(folgen, mindestdauer=1200)["titel"],
            "ohne Angabe")

    def test_ist_nichts_lang_genug_kommt_die_neueste(self):
        """Lieber eine zu kurze Sendung als Stille: Der Nutzer hoert
        etwas und kann selbst urteilen, statt vor einem stummen Geraet
        zu sitzen."""
        _, folgen, _ = pod.feed_lesen(feed(
            item("kurz eins", "https://a/1.mp3", dauer="2:00")
            + item("kurz zwei", "https://a/2.mp3", dauer="3:00")))
        self.assertEqual(
            pod.neueste_folge(folgen, mindestdauer=1200)["titel"],
            "kurz eins")

    def test_ohne_audio_bleibt_es_bei_none(self):
        """Die Mindestdauer darf den Audio-Filter nicht aushebeln."""
        _, folgen, _ = pod.feed_lesen(feed(item("nur Text")))
        self.assertIsNone(pod.neueste_folge(folgen, mindestdauer=1200))

    def test_feed_pruefen_sieht_dieselbe_folge_an_die_gespielt_wird(self):
        """DIE ZWEITE VERDRAHTUNG - gefunden durch die Mutationsprobe am
        2026-10-08, nachdem die erste (dialos-radio.py) schon einen Test
        hatte.

        Wird `mindestdauer` hier nicht durchgereicht, prueft das Werkzeug
        den Einminueter und der Nutzer hoert die Stunde - oder umgekehrt.
        Eine Pruefung, die etwas anderes ansieht als den Betrieb, ist
        schlimmer als keine: Sie sagt "brauchbar" ueber eine Folge, die
        niemand spielt.

        `feed_holen` wird ersetzt statt das Netz zu benutzen - die
        Netzsperre dieses Moduls gilt auch hier.
        """
        echtes_holen = pod.feed_holen
        pod.feed_holen = lambda *a, **k: (feed(
            item("Ankuendigung", "https://a/1.mp3", dauer="1:00",
                 datum="Wed, 08 Oct 2026 08:00:00 +0200")
            + item("die Sendung", "https://a/2.mp3", dauer="52:00",
                   datum="Tue, 07 Oct 2026 08:00:00 +0200")), "")
        try:
            bericht = pod.feed_pruefen("https://egal", gruendlich=False,
                                       mindestdauer=1200)
            self.assertEqual(bericht["neueste"], "die Sendung")
            self.assertEqual(bericht["dauer"], 3120)
        finally:
            pod.feed_holen = echtes_holen

    def test_genau_auf_der_grenze_zaehlt_als_lang_genug(self):
        """Auch hier steht ein zu kurzer Eintrag VOR dem zu pruefenden,
        und aus demselben Grund wie oben: Ohne ihn faellt die Funktion
        auf "die neueste mit Audio" zurueck und liefert zufaellig das
        richtige Ergebnis. Die Mutationsprobe hat diesen Test beim
        ersten Lauf durchgelassen, als `>=` zu `>` wurde."""
        _, folgen, _ = pod.feed_lesen(feed(
            item("zu kurz", "https://a/1.mp3", dauer="2:00")
            + item("genau zwanzig", "https://a/2.mp3", dauer="20:00")))
        self.assertEqual(
            pod.neueste_folge(folgen, mindestdauer=1200)["titel"],
            "genau zwanzig")


class Dauer(unittest.TestCase):
    """iTunes schreibt die Dauer in drei Formaten."""

    def test_formate(self):
        for wert, erwartet in (("132", 132), ("2:12", 132),
                               ("1:02:03", 3723), ("0:45", 45)):
            with self.subTest(wert=wert):
                self.assertEqual(pod._dauer_in_sekunden(wert), erwartet)

    def test_unbrauchbares(self):
        for wert in ("", None, "zwei Minuten", "x:y"):
            with self.subTest(wert=wert):
                self.assertIsNone(pod._dauer_in_sekunden(wert))


class Schwellen(unittest.TestCase):
    """Die beiden Zahlen, die eine Entscheidung tragen."""

    def test_tot_nach_tagen_ist_grosszuegig(self):
        """Eine Kurznachrichten-Sendung erscheint mehrmals taeglich. Die
        Schwelle muss aber einen Wochenend-Podcast ueberleben, sonst
        sortiert sie Brauchbares aus."""
        self.assertGreaterEqual(pod.TOT_NACH_TAGEN, 8)

    def test_kurz_bis_sekunden(self):
        """"tagesschau in 100 Sekunden" lief am 2026-10-05 mit 2:12 - die
        Schwelle muss deutlich darueber liegen, denn gemeint ist die
        Grenze zum Magazin, nicht zur Sendelaenge."""
        self.assertGreater(pod.KURZ_BIS_SEKUNDEN, 132)


class Modulbindung(unittest.TestCase):
    """Die Audiopruefung kommt aus dem Sender-Modul, nicht doppelt."""

    def test_sendermodul_wird_gefunden(self):
        self.assertTrue(os.path.isfile(pod.SENDER_MODUL))

    def test_dekodieren_wird_benutzt_statt_nachgebaut(self):
        """Eine zweite Fassung der Audiopruefung liefe beim naechsten
        Fehler auseinander - dieselbe Ueberlegung wie bei
        medienliste_lesen()."""
        with open(os.path.join(BIN, "dialos_podcast.py"), encoding="utf-8") as f:
            quelle = f.read()
        self.assertIn("rs.dekodieren(", quelle)
        # Kein eigener ffprobe-AUFRUF - das Wort darf im erklaerenden
        # Kommentar stehen, nur nicht in einer Befehlsliste. Ein zu
        # grober Test hat hier zuerst auf den eigenen Docstring
        # angeschlagen (2026-10-05).
        self.assertNotIn('"ffprobe"', quelle)
        self.assertNotIn("'ffprobe'", quelle)


if __name__ == "__main__":
    unittest.main()
