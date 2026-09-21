#!/usr/bin/env python3
"""Die Bruecke zwischen DialOS und Thunderbird - gestartet von Thunderbird selbst.

WARUM ES SIE GIBT (Stephans TODO vom 2026-09-18): DialOS hat Entwuerfe in die
mbox geschrieben, Kontakte in abook.sqlite und den Suchindex ueber die
Postfachdateien gebaut. Jeder dieser drei Wege hat einen Fehler erzeugt - LF
statt CR LF, "X-Mozilla-Status: 0008" (das heisst geloescht, nicht Entwurf),
und eine Warteschlange, weil in die Datenbank eines laufenden Thunderbird nicht
geschrieben werden darf. Dreimal dasselbe Muster: in fremde Dateiformate
schreiben, statt das Programm zu fragen, dem sie gehoeren.

WIE SIE LAEUFT: Thunderbird startet dieses Programm selbst (Native Messaging)
und spricht mit ihm ueber die Standardein- und -ausgabe. Nach aussen macht es
einen UNIX-Socket auf, und DialOS legt dort seine Bitte hinein. Die Bruecke
reicht sie durch und gibt die Antwort zurueck.

WARUM EIN SOCKET UND NICHT EINE DATEI: Eine Datei waere wieder ein Format, auf
das sich zwei Programme einigen muessten - genau der Fehler, den diese Bruecke
abloest. Ein Socket gibt es nur, solange Thunderbird laeuft, und das ist die
ehrliche Auskunft: Ist er weg, ist Thunderbird zu.

Aufruf (durch Thunderbird, nicht von Hand):
  dialos-thunderbird-bruecke.py

Zum Pruefen von Hand:
  dialos-thunderbird-bruecke.py --bitte '{"befehl": "hallo"}'
"""

import json
import os
import socket
import subprocess
import struct
import sys
import threading
import time

SOCKET_PFAD = os.path.join(
    os.environ.get("XDG_RUNTIME_DIR") or f"/tmp/dialos-{os.getuid()}",
    "dialos-thunderbird.sock")
PROTOKOLL = os.path.join(os.path.expanduser("~"), ".log", "dialos-thunderbird.log")
ANTWORT_ZEITGRENZE_S = 30.0
# Was nachgeholt wird, sobald Thunderbird da ist. Jedes Programm raeumt seine
# eigene Warteschlange ab - die Bruecke kennt deren Inhalt nicht und muss es
# auch nicht: Sie weiss nur, dass jetzt der Zeitpunkt dafuer ist.
NACHHOLER = (
    ("/usr/local/bin/dialos-mail-entwurf.py", "nachholen"),
)
# Erst wenn die Erweiterung sich gemeldet hat, kann etwas abgelegt werden.
# Thunderbird startet die Bruecke beim Verbinden - aber die Antwort auf die
# erste Bitte braucht noch einen Augenblick, bis Konten und Adressbuecher
# geladen sind.
VORLAUF_S = 8.0


def melde(text):
    try:
        os.makedirs(os.path.dirname(PROTOKOLL), exist_ok=True)
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')}  {text}\n")
    except OSError:
        pass


# --------------------------------------------------------- Native Messaging
# Das Protokoll ist schlicht: vier Byte Laenge (little endian), dann JSON.
def lesen():
    kopf = sys.stdin.buffer.read(4)
    if len(kopf) < 4:
        return None
    laenge = struct.unpack("<I", kopf)[0]
    roh = sys.stdin.buffer.read(laenge)
    return json.loads(roh.decode("utf-8"))


def schreiben(nachricht):
    roh = json.dumps(nachricht, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(roh)))
    sys.stdout.buffer.write(roh)
    sys.stdout.buffer.flush()


class Vermittlung:
    """Ordnet Antworten den Bitten zu - ueber eine laufende Nummer.

    Ein Strom, viele Fragen: Ohne Nummer koennte eine Antwort zur falschen
    Frage gehoeren, sobald zwei Bitten dicht hintereinander kommen.
    """

    def __init__(self):
        self.naechste = 1
        self.warten = {}
        self.schloss = threading.Lock()

    def nummer(self):
        with self.schloss:
            n = self.naechste
            self.naechste += 1
            self.warten[n] = {"ereignis": threading.Event(), "antwort": None}
            return n

    def antwort_da(self, nachricht):
        n = nachricht.get("nummer")
        with self.schloss:
            platz = self.warten.get(n)
        if platz is None:
            melde(f"Antwort ohne passende Bitte: {nachricht}")
            return
        platz["antwort"] = nachricht
        platz["ereignis"].set()

    def abholen(self, n):
        with self.schloss:
            platz = self.warten.get(n)
        if platz is None:
            return {"ok": False, "fehler": "Bitte unbekannt"}
        if not platz["ereignis"].wait(ANTWORT_ZEITGRENZE_S):
            antwort = {"ok": False, "fehler": "Thunderbird hat nicht geantwortet"}
        else:
            antwort = platz["antwort"]
        with self.schloss:
            self.warten.pop(n, None)
        return antwort


def warteschlangen_abarbeiten():
    """Vorgemerktes nachholen, jetzt wo Thunderbird laeuft.

    DAS IST STEPHANS WAHL VOM 2026-09-21 ("Vormerken und nachholen"): Ist
    Thunderbird zu, wenn DialOS einen Entwurf ablegen will, sagt DialOS das und
    merkt ihn vor. Nachgeholt wird nicht beim Anmelden - da laeuft Thunderbird
    ja meist noch nicht -, sondern genau hier: Thunderbird hat die Bruecke
    gestartet, also ist es da.
    """
    time.sleep(VORLAUF_S)
    for befehl in NACHHOLER:
        if not os.path.exists(befehl[0]):
            continue
        try:
            fertig = subprocess.run(list(befehl), capture_output=True, text=True,
                                    timeout=120)
            ausgabe = (fertig.stdout or fertig.stderr or "").strip()
            if ausgabe:
                melde(f"Nachholen {os.path.basename(befehl[0])}: {ausgabe[:200]}")
        except (OSError, subprocess.SubprocessError) as fehler:
            melde(f"Nachholen fehlgeschlagen ({befehl[0]}): {fehler}")


def socket_bedienen(vermittlung):
    """Nimmt Bitten von DialOS entgegen - eine Zeile JSON je Verbindung."""
    try:
        os.unlink(SOCKET_PFAD)
    except OSError:
        pass
    horcher = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    horcher.bind(SOCKET_PFAD)
    # NUR FUER DEN ANGEMELDETEN NUTZER: Im Socket stehen Mailadressen und
    # Betreffzeilen - er gehoert niemandem sonst.
    os.chmod(SOCKET_PFAD, 0o600)
    horcher.listen(4)
    melde(f"Socket offen: {SOCKET_PFAD}")
    while True:
        verbindung, _ = horcher.accept()
        threading.Thread(target=bitte_bearbeiten, args=(verbindung, vermittlung),
                         daemon=True).start()


def bitte_bearbeiten(verbindung, vermittlung):
    try:
        roh = b""
        while not roh.endswith(b"\n"):
            stueck = verbindung.recv(4096)
            if not stueck:
                break
            roh += stueck
        if not roh.strip():
            return
        bitte = json.loads(roh.decode("utf-8"))
        nummer = vermittlung.nummer()
        bitte["nummer"] = nummer
        melde(f"Bitte {nummer}: {bitte.get('befehl')}")
        schreiben(bitte)
        antwort = vermittlung.abholen(nummer)
        melde(f"Antwort {nummer}: {antwort}")
        verbindung.sendall((json.dumps(antwort, ensure_ascii=False) + "\n").encode("utf-8"))
    except Exception as fehler:            # noqa: BLE001 - jede Ursache zaehlt
        melde(f"Bitte fehlgeschlagen: {fehler}")
        try:
            verbindung.sendall(
                (json.dumps({"ok": False, "fehler": str(fehler)}) + "\n").encode("utf-8"))
        except OSError:
            pass
    finally:
        verbindung.close()


def fragen(bitte, zeitgrenze=ANTWORT_ZEITGRENZE_S):
    """Von aussen: eine Bitte an Thunderbird schicken. Antwort oder Fehler-dict.

    DAS IST DER WEG, DEN DIALOS NIMMT - nicht der Socket selbst. Faellt die
    Bruecke aus, kommt hier eine klare Auskunft zurueck, und der Nutzer hoert
    sie, statt vor einem stummen Geraet zu stehen.
    """
    if not os.path.exists(SOCKET_PFAD):
        return {"ok": False, "fehler": "Thunderbird läuft nicht"}
    try:
        verbindung = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        verbindung.settimeout(zeitgrenze)
        verbindung.connect(SOCKET_PFAD)
        verbindung.sendall((json.dumps(bitte, ensure_ascii=False) + "\n").encode("utf-8"))
        roh = b""
        while not roh.endswith(b"\n"):
            stueck = verbindung.recv(4096)
            if not stueck:
                break
            roh += stueck
        verbindung.close()
        return json.loads(roh.decode("utf-8")) if roh.strip() else {
            "ok": False, "fehler": "keine Antwort"}
    except OSError as fehler:
        return {"ok": False, "fehler": f"Brücke nicht erreichbar: {fehler}"}


def main():
    if "--bitte" in sys.argv:
        bitte = json.loads(sys.argv[sys.argv.index("--bitte") + 1])
        print(json.dumps(fragen(bitte), ensure_ascii=False, indent=1))
        return 0

    melde("=== Brücke gestartet (von Thunderbird) ===")
    vermittlung = Vermittlung()
    threading.Thread(target=socket_bedienen, args=(vermittlung,), daemon=True).start()
    threading.Thread(target=warteschlangen_abarbeiten, daemon=True).start()
    try:
        while True:
            nachricht = lesen()
            if nachricht is None:
                break
            vermittlung.antwort_da(nachricht)
    except Exception as fehler:            # noqa: BLE001
        melde(f"Abbruch: {fehler}")
    finally:
        try:
            os.unlink(SOCKET_PFAD)
        except OSError:
            pass
        melde("=== Brücke beendet (Thunderbird ist zu) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
