#!/usr/bin/env python3
"""
Tests fuer die Selbstpruefung "ist die Ansage ueberhaupt zu hoeren?"
(dialos-say.py, eigenen_strom_pruefen).

Am 2026-08-24 kam jeder paplay-Strom stummgeschaltet zur Welt, weil PipeWire
sich das je Anwendung merkt. paplay gab 0 zurueck, aus_speicher() hielt die
Ansage fuer geglueckt - das Geraet war stumm, ohne dass irgendwo ein Fehler
stand. Seit dem 2026-11-06 sieht dialos-say nach, ob der eigene Strom stumm
ist, gibt ihn frei und schreibt es ins Protokoll.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import os
import time
import unittest

BIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iso-build", "config", "includes.chroot", "usr", "local", "bin")


def _laden():
    spec = importlib.util.spec_from_file_location(
        "dialos_say", os.path.join(BIN, "dialos-say.py"))
    modul = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(modul)
    return modul


class FalscherProzess:
    """Steht fuer ein laufendes paplay."""

    def __init__(self, pid=4711, laeuft=True, rueckgabe=0):
        self.pid = pid
        self.laeuft = laeuft
        self.rueckgabe = rueckgabe

    def poll(self):
        return None if self.laeuft else self.rueckgabe

    def wait(self, timeout=None):
        return self.rueckgabe


def strom(index, pid, stumm=False, prozent=65536, senke=59, name="paplay"):
    return {
        "index": index, "sink": senke, "mute": stumm,
        "volume": {"mono": {"value": prozent}},
        "properties": {"application.name": name,
                       "application.process.id": str(pid)},
    }


class Selbstpruefung(unittest.TestCase):

    def setUp(self):
        self.m = _laden()
        self.stroeme = []
        self.freigaben = []
        self.protokoll = []
        self.lauter = []
        self.senke_ist_stumm = False
        self.m.sink_inputs = lambda: self.stroeme
        self.m.set_mute = lambda i, s: self.freigaben.append((i, s))
        self.m.melde = self.protokoll.append
        self.m.senke_stumm = lambda i: self.senke_ist_stumm
        echt_run = self.m.subprocess.run

        def run(cmd, **kw):
            if cmd[:2] == ["pactl", "set-sink-input-volume"]:
                self.lauter.append(cmd[2])
                return None
            return echt_run(cmd, **kw)
        self.m.subprocess.run = run
        self.addCleanup(setattr, self.m.subprocess, "run", echt_run)

    def test_stummer_eigener_strom_wird_freigegeben(self):
        self.stroeme = [strom(200, 4711, stumm=True)]
        self.m.eigenen_strom_pruefen(FalscherProzess())
        self.assertEqual(self.freigaben, [(200, False)])
        self.assertTrue(any("WARNUNG" in z for z in self.protokoll))

    def test_eigener_strom_auf_null_prozent_wird_lauter(self):
        self.stroeme = [strom(200, 4711, prozent=0)]
        self.m.eigenen_strom_pruefen(FalscherProzess())
        self.assertEqual(self.lauter, ["200"])

    def test_hoerbarer_strom_bleibt_unberuehrt(self):
        self.stroeme = [strom(200, 4711)]
        self.m.eigenen_strom_pruefen(FalscherProzess())
        self.assertEqual(self.freigaben, [])
        self.assertEqual(self.protokoll, [])

    def test_fremder_stummer_strom_bleibt_stumm(self):
        # Ein stummes Radio gehoert dem Nutzer, nicht DialOS.
        self.stroeme = [strom(150, 999, stumm=True, name="rhythmbox"),
                        strom(200, 4711)]
        self.m.eigenen_strom_pruefen(FalscherProzess())
        self.assertEqual(self.freigaben, [])

    def test_stumme_ausgabe_wird_nur_gemeldet(self):
        self.stroeme = [strom(200, 4711)]
        self.senke_ist_stumm = True
        self.m.eigenen_strom_pruefen(FalscherProzess())
        self.assertEqual(self.freigaben, [])
        self.assertTrue(any("Tonausgabe" in z for z in self.protokoll))

    def test_kurzer_ton_haelt_nicht_auf(self):
        # Frageton schon vorbei, bevor er in der Liste stand.
        anfang = time.monotonic()
        self.m.eigenen_strom_pruefen(FalscherProzess(laeuft=False))
        self.assertLess(time.monotonic() - anfang, 0.2)

    def test_aus_speicher_prueft_den_strom(self):
        # Der Fall vom 2026-08-24: gespeicherte Ansage, stummer paplay-Strom.
        # Vor dem 2026-11-06 lief aus_speicher() ueber subprocess.run und
        # sah den Strom nie an.
        import tempfile
        ordner = tempfile.mkdtemp()
        self.m.SPEICHER = ordner
        open(os.path.join(ordner, self.m.speicher_schluessel("Hallo") + ".wav"),
             "w").close()
        self.stroeme = [strom(200, 4711, stumm=True)]
        echt_popen = self.m.subprocess.Popen
        self.addCleanup(setattr, self.m.subprocess, "Popen", echt_popen)
        self.m.subprocess.Popen = lambda *a, **kw: FalscherProzess()
        self.assertTrue(self.m.aus_speicher("Hallo"))
        self.assertEqual(self.freigaben, [(200, False)])


class TitelwechselWaehrendDerAnsage(unittest.TestCase):
    """Stephan, 2026-11-06: "da kommt nix". Rhythmbox wechselte waehrend einer
    Ansage den Titel; der neue Strom kam stumm zur Welt, freigegeben wurde nur
    die alte Strom-Nummer - die neue Sendung blieb stumm."""

    def setUp(self):
        self.m = _laden()
        self.freigaben = []
        self.m.set_mute = lambda i, s: self.freigaben.append((i, s))
        self.m.melde = lambda t: None

    def test_neuer_strom_derselben_anwendung_wird_freigegeben(self):
        self.m.sink_inputs = lambda: [strom(805, 1, stumm=True, name="Rhythmbox")]
        self.m.nach_namen_freigeben({"Rhythmbox"}, vorher_stumm={789})
        self.assertEqual(self.freigaben, [(805, False)])

    def test_vom_nutzer_stummgeschalteter_strom_bleibt_stumm(self):
        self.m.sink_inputs = lambda: [strom(700, 1, stumm=True, name="Rhythmbox")]
        self.m.nach_namen_freigeben({"Rhythmbox"}, vorher_stumm={700})
        self.assertEqual(self.freigaben, [])

    def test_fremde_anwendung_bleibt_unberuehrt(self):
        self.m.sink_inputs = lambda: [strom(900, 1, stumm=True, name="Firefox")]
        self.m.nach_namen_freigeben({"Rhythmbox"}, vorher_stumm=set())
        self.assertEqual(self.freigaben, [])


if __name__ == "__main__":
    unittest.main()
