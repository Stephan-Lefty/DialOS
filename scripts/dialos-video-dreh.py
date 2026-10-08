#!/usr/bin/env python3
"""DialOS: das Vorfuehrvideo vollautomatisch drehen - Anna spielt die Nutzerin.

Drehbuch: docs/video-drehbuch.md. Stephan, 2026-10-05: ein Video, "wo das was
heute moeglich ist schon mal zu sehen und zu hoeren ist. Anna soll dabei den
Nutzer spielen" - mit Musterdaten, hochaufloesend, jede Stimme auf eigener Spur.

NICHTS IST GESTELLT. Annas Saetze gehen in ein virtuelles Mikrofon
(pw-loopback), und die echte Spracherkennung hoert sie wie einen Menschen vor
dem Geraet. Dafuer wird der Aufnahme-Strom der Echo-Unterdrueckung auf dieses
Mikrofon umgehaengt: Alle DialOS-Programme hoeren auf "dialos_mikrofon_ohne_echo",
also hoeren sie Anna auf dem Weg, den sie auch im Betrieb nehmen.

VOR DEM DREH MUSS DAS KONTO dialosadmin DIE SOUNDKARTE FREIGEBEN (Gruppe
"audio", Spracherkennung haelt das Mikrofon offen) - siehe Drehbuch, "Was die
ersten Drehs gelehrt haben".

VIER SCHRITTE, ZWEI KONTEN:
  vorbereiten    (dialosadmin)  Annas Saetze als WAV nach /var/tmp/dialos-video
  einrichten     (vorfuehrung)  Musterdaten, Mailkonto offline, Kontakt, OBS
  drehen         (vorfuehrung)  Aufnahme - laeuft ohne Fenster im Hintergrund
  alles          (vorfuehrung)  einrichten + Erststarts + drehen, fuehrt durch
                                (Kurzform: /var/tmp/dialos-video/los)
  nachbearbeiten (dialosadmin)  MP4 mit Mischung, beide Stimmen als WAV

/var/tmp/dialos-video IST DIE UEBERGABE zwischen den Konten: Die externe Platte
und das Heimatverzeichnis von dialosadmin kann das Vorfuehrkonto nicht lesen.

WARTEN AUF DIALOS, NICHT AUF DIE UHR: Nach jedem Satz wartet der Dreh, bis die
erwartete Ansage in ~/.log/dialos-say.log steht und danach Ruhe auf dem
Lautsprecher ist. Feste Wartezeiten gingen schief - das Diktat braucht beim
Start rund 9 s, eine Uhrzeit eine.

ANNAS SAETZE SIND VORHER GEPRUEFT (2026-10-05, offline gegen Vosk und Parakeet
mit kerstin-low, Tempo 0,95): Einzelwoerter fallen bei dieser Stimme durch -
"Milch" wurde "fest", "nein" wurde "ja" (!). Deshalb "Ja!"/"Nein!", Waren mit
Menge, der Kontakt mit Anrede und ein foermlicher Brief. Einzelheiten im
Drehbuch, Abschnitt "Annas Saetze".
"""

import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import uuid

UEBERGABE = "/var/tmp/dialos-video"
ANNA_ORDNER = os.path.join(UEBERGABE, "anna")
ERGEBNIS = os.path.join(UEBERGABE, "ergebnis")
PIPER_DIR = "/usr/local/share/dialos-piper"
ANNA_STIMME = "voices/de_DE-kerstin-low.onnx"
ANNA_TEMPO = "0.95"                 # wie DialOS' Anna (Stephans Wahl, 2026-09-14)

HEIM = os.path.expanduser("~")
DIALOS_CONF = os.path.join(HEIM, ".config", "dialos")
SAY_LOG = os.path.join(HEIM, ".log", "dialos-say.log")
OBS_CONF = os.path.join(HEIM, ".config", "obs-studio")
VIDEO_ORDNER = os.path.join(HEIM, "Videos", "DialOS")
DREH_LOG = os.path.join(HEIM, ".log", "dialos-video-dreh.log")

EINGANG = "dialos_anna_eingang"     # hier hinein spielt der Dreh Annas WAVs
MIKROFON = "dialos_anna_mikrofon"   # das sieht die Erkennung als Mikrofon
ERKENNER = "/usr/local/bin/dialos-sprachbefehl-desktop.py"

# --------------------------------------------------------------- Musterdaten
# Alles erfunden; example.org ist fuer Beispiele reserviert (RFC 2606).
MUSTERDATEN = {
    "Anrede": "Herr", "Vorname": "Max", "Name": "Mustermann",
    "Straße": "Musterstraße", "Hausnummer": "1", "Postleitzahl": "12345",
    "Ort": "Musterstadt", "Land": "Deutschland", "Länderkennzeichen": "DE",
    "E-Mail-Adresse": "max.mustermann@example.org",
    "Posteingang-Server": "imap.example.org", "Posteingang-Port": "993",
    "Postausgang-Server": "smtp.example.org", "Postausgang-Port": "587",
    "Grußformel": "Herzliche Grüße",
}
KONTAKT = {"name": "Frau Erika Musterfrau", "vorname": "Erika", "nachname": "Musterfrau",
           "strasse": "Beispielweg 7", "plz": "54321", "ort": "Beispielstadt",
           "mail": "erika.musterfrau@example.org"}

# --------------------------------------------------------------- Die Szenen
# (Annas Satz, erwartete Ansage, Ruhe danach in s, Pause danach in s)
# erwartet: Teil der naechsten Ansage | "" = irgendeine Ansage | None = keine
# (im Diktat spricht DialOS nicht - dann nur die Pause).
SZENEN = [
    ("1 Aufwachen", [
        ("Sprachsteuerung starten", "zu.", 1.2, 1.0),
    ]),
    ("2 Uhrzeit und Datum", [
        ("Wie viel Uhr ist es?", "Es ist", 1.2, 1.0),
        ("Welchen Tag haben wir?", "Heute ist", 1.2, 1.5),
    ]),
    ("3 Einkaufszettel", [
        ("Einkaufszettel aufnehmen", "Einkaufszettel schreiben", 1.2, 0.6),
        ("Ja!", "Ich schreibe mit", 1.2, 0.8),
        ("Zwei Liter Milch.", None, 0, 2.0),
        ("Ein Laib Brot.", None, 0, 2.0),
        ("Ein Kilo Äpfel.", None, 0, 2.5),
        ("Diktat beenden", "Diktat beendet", 1.5, 1.0),
        ("Einkaufszettel vorlesen", "", 2.5, 1.5),
    ]),
    ("4 Brief", [
        ("Brief schreiben", "neuen Brief", 1.2, 0.6),
        ("Ja!", "An wen geht der Brief", 1.2, 0.6),
        ("Frau Erika Musterfrau.", "In den Kontakten steht", 1.2, 0.6),
        ("Ja!", "Ich schreibe mit", 1.2, 0.8),
        ("Liebe Frau Musterfrau, vielen Dank für Ihren Besuch am Sonntag. "
         "Ich habe mich sehr gefreut. Herzliche Grüße", None, 0, 2.5),
        ("Diktat beenden", "", 1.5, 1.0),
        ("Brief vorlesen", "Brief als PDF speichern", 1.5, 1.0),
        ("Brief als PDF speichern", "PDF", 1.2, 0.5),
    ]),
    ("5 E-Mail", [
        ("E-Mail schreiben", "An wen soll die E-Mail gehen", 1.2, 0.6),
        ("Frau Erika Musterfrau.", "Stimmt das", 1.2, 0.6),
        ("Ja!", "Betreff", 1.2, 0.6),
        ("Eine Einladung zum Kaffee.", "Text der E-Mail", 1.2, 0.8),
        ("Hallo Erika, kommst Du am Samstag zum Kaffee? Viele Grüße", None, 0, 2.5),
        ("Diktat beenden", "verschicken", 1.2, 0.6),
        ("Nein!", "", 1.5, 1.5),
    ]),
    ("6 Programme", [
        ("Internet öffnen", "", 1.2, 5.0),
        ("Internet schließen", "Sage ja oder nein", 1.2, 0.6),
        ("Ja!", "", 1.2, 2.0),
    ]),
    ("7 Schluss", [
        ("Sprachsteuerung stoppen", "nicht mehr zu", 1.2, 3.0),
    ]),
]


def saetze():
    """Alle Saetze in Reihenfolge, mit laufender Nummer (= WAV-Name)."""
    nr = 0
    for szene, zeilen in SZENEN:
        for zeile in zeilen:
            nr += 1
            yield nr, szene, zeile


def melde(text):
    zeile = f"{time.strftime('%m-%d %H:%M:%S')}  {text}"
    print(zeile, flush=True)
    try:
        os.makedirs(os.path.dirname(DREH_LOG), exist_ok=True)
        with open(DREH_LOG, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass


# =============================================================== vorbereiten

def vorbereiten():
    """Annas Saetze erzeugen und die Uebergabe anlegen (Konto dialosadmin)."""
    os.makedirs(ANNA_ORDNER, exist_ok=True)
    os.makedirs(ERGEBNIS, exist_ok=True)
    os.chmod(UEBERGABE, 0o755)
    os.chmod(ANNA_ORDNER, 0o755)
    os.chmod(ERGEBNIS, 0o1777)          # das Vorfuehrkonto legt hier das Video ab
    for nr, _szene, (text, *_rest) in saetze():
        ziel = os.path.join(ANNA_ORDNER, f"{nr:02d}.wav")
        # Wie DialOS' Anna: kerstin-low, --noise_w 0 (jeder Lauf gleich),
        # Tempo 0,95. 48 kHz, weil OBS und der Schnitt damit arbeiten.
        befehl = (f"cd {PIPER_DIR} && printf %s \"$TEXT\" | ./piper/piper --model {ANNA_STIMME} "
                  f"--noise_w 0 --sentence_silence 0.5 --output_raw 2>/dev/null | "
                  f"sox -r 16000 -c 1 -b 16 -e signed-integer -t raw - -r 48000 -t wav "
                  f"\"$ZIEL\" tempo {ANNA_TEMPO} norm -3 pad 0.3 0.3")
        subprocess.run(["sh", "-c", befehl], check=True, env=dict(os.environ, TEXT=text, ZIEL=ziel))
        os.chmod(ziel, 0o644)
        print(f"  {nr:02d}  {text}")
    eigen = os.path.join(UEBERGABE, "dialos-video-dreh.py")
    shutil.copy(os.path.abspath(__file__), eigen)
    os.chmod(eigen, 0o755)
    print(f"\nFertig: {UEBERGABE}")
    return 0


# =============================================================== einrichten

def persoenliche_daten_schreiben():
    os.makedirs(DIALOS_CONF, exist_ok=True)
    vorlage = "/usr/local/share/dialos/persoenliche-daten-vorlage.txt"
    with open(vorlage, encoding="utf-8") as f:
        zeilen = f.read().splitlines()
    neu = []
    for zeile in zeilen:
        schluessel = zeile.split(":", 1)[0]
        if not zeile.startswith("#") and ":" in zeile and schluessel in MUSTERDATEN:
            zeile = f"{schluessel}: {MUSTERDATEN[schluessel]}"
        neu.append(zeile)
    pfad = os.path.join(DIALOS_CONF, "persoenliche-daten.txt")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(neu) + "\n")
    os.chmod(pfad, 0o600)
    melde(f"Musterdaten eingetragen: {pfad}")


def thunderbird_profil():
    import configparser
    ini = os.path.join(HEIM, ".thunderbird", "installs.ini")
    p = configparser.ConfigParser()
    p.read(ini)
    for abschnitt in p.sections():
        if p.has_option(abschnitt, "Default"):
            return os.path.join(HEIM, ".thunderbird", p.get(abschnitt, "Default"))
    return None


def thunderbird_einstellen(profil):
    """Offline, Entwuerfe lokal, keine Begruessungsfenster - per user.js."""
    zeilen = [
        # example.org hat keinen Mailserver - online kaeme eine Fehlermeldung ins Bild.
        'user_pref("offline.startup_state", 3);',
        # Ohne Server muessen Entwuerfe in die Lokalen Ordner.
        'user_pref("mail.identity.id1.draft_folder", "mailbox://nobody@Local%20Folders/Drafts");',
        'user_pref("mail.identity.id1.drafts_folder_picker_mode", "1");',
        'user_pref("mail.identity.id1.fcc_folder", "mailbox://nobody@Local%20Folders/Sent");',
        'user_pref("mail.identity.id1.fcc_folder_picker_mode", "1");',
        'user_pref("mail.shell.checkDefaultClient", false);',
        'user_pref("mailnews.start_page.enabled", false);',
        'user_pref("mail.rights.version", 1);',
        'user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);',
        'user_pref("app.donation.eoy.version.viewed", 999);',
    ]
    pfad = os.path.join(profil, "user.js")
    vorhanden = ""
    if os.path.isfile(pfad):
        with open(pfad, encoding="utf-8") as f:
            vorhanden = f.read()
    with open(pfad, "a", encoding="utf-8") as f:
        f.write("\n// DialOS-Vorfuehrung (dialos-video-dreh.py)\n")
        for z in zeilen:
            if z not in vorhanden:
                f.write(z + "\n")
    melde(f"Thunderbird offline, Entwuerfe lokal: {pfad}")


def kontakt_anlegen(profil):
    """Frau Erika Musterfrau, MIT Mailadresse - dialos-empfaenger.py kennt kein EMAIL-Feld."""
    pfad = os.path.join(profil, "abook.sqlite")
    v = sqlite3.connect(pfad)
    with v:
        v.execute("CREATE TABLE IF NOT EXISTS properties (card TEXT, name TEXT, value TEXT)")
        v.execute("CREATE TABLE IF NOT EXISTS lists (uid TEXT PRIMARY KEY, name TEXT, "
                  "nickName TEXT, description TEXT)")
        v.execute("CREATE TABLE IF NOT EXISTS list_cards (list TEXT, card TEXT, "
                  "PRIMARY KEY(list, card))")
        v.execute("CREATE INDEX IF NOT EXISTS properties_card ON properties(card)")
        v.execute("CREATE INDEX IF NOT EXISTS properties_name ON properties(name)")
        if v.execute("PRAGMA user_version").fetchone()[0] == 0:
            v.execute("PRAGMA user_version = 4")
        schon = v.execute("SELECT 1 FROM properties WHERE name='DisplayName' AND value=?",
                          (KONTAKT["name"],)).fetchone()
        if schon:
            melde("Kontakt ist schon da")
            return
        uid = str(uuid.uuid4())
        k = KONTAKT
        karte = "\r\n".join([
            "BEGIN:VCARD", "VERSION:4.0", f"UID:{uid}", f"FN:{k['name']}",
            f"N:{k['nachname']};{k['vorname']};;Frau;",
            f"ADR:;;{k['strasse']};{k['ort']};;{k['plz']};",
            f"EMAIL;PREF=1:{k['mail']}", "END:VCARD"]) + "\r\n"
        v.executemany("INSERT INTO properties (card, name, value) VALUES (?, ?, ?)", [
            (uid, "_vCard", karte), (uid, "DisplayName", k["name"]),
            (uid, "FirstName", k["vorname"]), (uid, "LastName", k["nachname"]),
            (uid, "PrimaryEmail", k["mail"]),
            (uid, "LastModifiedDate", str(int(time.time())))])
    v.close()
    melde(f"Kontakt angelegt: {KONTAKT['name']}")


def obs_einrichten():
    """Profil und Szene "DialOS" wie in docs/video-aufnahme.md, Anna statt Raummikrofon."""
    profil = os.path.join(OBS_CONF, "basic", "profiles", "DialOS")
    szenen = os.path.join(OBS_CONF, "basic", "scenes")
    os.makedirs(profil, exist_ok=True)
    os.makedirs(szenen, exist_ok=True)
    os.makedirs(VIDEO_ORDNER, exist_ok=True)
    with open(os.path.join(OBS_CONF, "global.ini"), "w", encoding="utf-8") as f:
        f.write("[General]\nFirstRun=true\nEnableAutoUpdates=false\n\n"
                "[Basic]\nProfile=DialOS\nProfileDir=DialOS\n"
                "SceneCollection=DialOS\nSceneCollectionFile=DialOS\n\n"
                "[BasicWindow]\nSysTrayEnabled=true\nSysTrayWhenStarted=true\n"
                "SysTrayMinimizeToTray=true\n")
    with open(os.path.join(profil, "basic.ini"), "w", encoding="utf-8") as f:
        f.write("[General]\nName=DialOS\n\n"
                "[Video]\nBaseCX=1920\nBaseCY=1080\nOutputCX=1920\nOutputCY=1080\n"
                "FPSType=0\nFPSCommon=30\n\n"
                "[Audio]\nSampleRate=48000\nChannelSetup=Stereo\n\n"
                "[Output]\nMode=Advanced\n\n"
                f"[AdvOut]\nRecType=Standard\nRecFilePath={VIDEO_ORDNER}\n"
                "RecFormat2=mkv\nRecEncoder=obs_x264\nRecTracks=7\nRecRescale=false\n"
                "Track1Bitrate=320\nTrack2Bitrate=320\nTrack3Bitrate=320\n"
                "Track1Name=Mischung\nTrack2Name=Michael DialOS\nTrack3Name=Anna Nutzerin\n")
    # Konstante Qualitaet statt fester Bitrate: Die Schrift im Mitschrift-Fenster
    # muss gestochen scharf sein (Drehbuch, Abschnitt Bild).
    with open(os.path.join(profil, "recordEncoder.json"), "w", encoding="utf-8") as f:
        json.dump({"rate_control": "CRF", "crf": 16, "preset": "veryfast",
                   "profile": "high", "keyint_sec": 2}, f)
    pfad = os.path.join(szenen, "DialOS.json")
    if os.path.isfile(pfad):
        melde("OBS-Szene ist schon da - bleibt (sie traegt die Bildschirm-Freigabe)")
        return
    u = {n: str(uuid.uuid4()) for n in ("szene", "bild", "dialos", "anna")}

    def eintrag(name, nr):
        return {"name": name, "source_uuid": u[{"Bildschirm": "bild", "Michael DialOS": "dialos",
                                                 "Anna Nutzerin": "anna"}[name]],
                "visible": True, "locked": False, "rot": 0.0, "pos": {"x": 0.0, "y": 0.0},
                "scale": {"x": 1.0, "y": 1.0}, "align": 5, "bounds_type": 0,
                "bounds_align": 0, "bounds": {"x": 0.0, "y": 0.0}, "id": nr}
    quelle = lambda typ, name, schluessel, einstellungen, mixers: {
        "id": typ, "versioned_id": typ, "name": name, "uuid": u[schluessel],
        "settings": einstellungen, "mixers": mixers, "volume": 1.0, "muted": False,
        "enabled": True, "flags": 0, "sync": 0, "balance": 0.5, "monitoring_type": 0}
    daten = {
        "name": "DialOS", "current_scene": "DialOS", "current_program_scene": "DialOS",
        "scene_order": [{"name": "DialOS"}], "groups": [], "transitions": [],
        "current_transition": "Fade", "transition_duration": 300,
        "sources": [
            quelle("scene", "DialOS", "szene",
                   {"items": [eintrag("Bildschirm", 1), eintrag("Michael DialOS", 2),
                              eintrag("Anna Nutzerin", 3)],
                    "id_counter": 3, "custom_size": False}, 0),
            quelle("pipewire-screen-capture-source", "Bildschirm", "bild",
                   {"ShowCursor": False}, 0),
            # Bitmaske der Spuren: 1 = Spur 1, 2 = Spur 2, 4 = Spur 3.
            quelle("pulse_output_capture", "Michael DialOS", "dialos",
                   {"device_id": "default"}, 3),          # Spur 1 + 2
            quelle("pulse_input_capture", "Anna Nutzerin", "anna",
                   {"device_id": MIKROFON}, 5),           # Spur 1 + 3
        ],
    }
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=1)
    melde(f"OBS eingerichtet: {pfad}")


def einrichten():
    if getpass_user() in ("dialosadmin", "nutzer"):
        print("Nur im Vorfuehrkonto - hier stehen echte Daten.", file=sys.stderr)
        return 2
    persoenliche_daten_schreiben()
    r = subprocess.run(["/usr/local/bin/dialos-mailkonto.py", "einrichten"])
    if r.returncode != 0:
        melde(f"Mailkonto: Rueckgabewert {r.returncode} - Ausgabe oben")
        return 1
    profil = thunderbird_profil()
    if not profil:
        melde("Kein Thunderbird-Profil gefunden")
        return 1
    thunderbird_einstellen(profil)
    kontakt_anlegen(profil)
    # Keine Benachrichtigung im Bild, kein dunkler Bildschirm mitten im Dreh.
    for schema, schluessel, wert in (
            ("org.gnome.desktop.notifications", "show-banners", "false"),
            ("org.gnome.desktop.session", "idle-delay", "uint32 0"),
            ("org.gnome.desktop.screensaver", "lock-enabled", "false")):
        subprocess.run(["gsettings", "set", schema, schluessel, wert])
    subprocess.run(["gnome-extensions", "enable", "ubuntu-appindicators@ubuntu.com"])
    obs_einrichten()
    melde("Einrichtung fertig.")
    return 0


def alles():
    """Ein Befehl fuer Stephan im Vorfuehrkonto: einrichten, die zwei Erststarts, drehen.

    Im Vorfuehrkonto gibt es kein Claude zum Abschreiben - deshalb fuehrt
    dieser Schritt selbst durch und wartet auf die zwei Handgriffe, die kein
    Skript abnehmen darf (die Bildschirm-Freigabe ist GNOMEs Sicherheitsfrage).
    """
    if einrichten() != 0:
        input("\nDie Einrichtung ist nicht durchgelaufen (siehe oben). Enter beendet.")
        return 1
    print("\n1) OBS startet gleich und fragt, welcher Bildschirm aufgenommen werden soll.\n"
          "   Bildschirm waehlen, \"Erlauben\" klicken (\"Merken\" anhaken, falls da).\n"
          "   Danach OBS ueber das Kreuz oben rechts schliessen.")
    subprocess.run(["obs", "--disable-shutdown-check"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("\n2) Firefox startet einmal - die Begruessung soll nicht im Video stehen.\n"
          "   Alles wegklicken, dann Firefox schliessen.")
    subprocess.run(["firefox-esr"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    input("\n3) Bereit. Enter druecken - das Fenster schliesst sich, nach 10 Sekunden\n"
          "   beginnt der Dreh. Rund 5 Minuten nichts anfassen. ")
    return drehen()


def getpass_user():
    import getpass
    return getpass.getuser()


# =============================================================== drehen

class Pegel(threading.Thread):
    """Lauscht am Lautsprecher-Ausgang mit: Spricht DialOS gerade?"""

    SCHWELLE = 300                  # RMS, 16 bit; Annas/Michaels Sprache liegt weit darueber

    def __init__(self):
        super().__init__(daemon=True)
        self.zuletzt_laut = 0.0
        self.laute_bloecke = []         # Zeitpunkte lauter 100-ms-Bloecke
        self.prozess = subprocess.Popen(
            ["parec", "--device=@DEFAULT_MONITOR@", "--rate=16000", "--channels=1",
             "--format=s16le", "--latency-msec=50", "--client-name=dialos-video-pegel"],
            stdout=subprocess.PIPE)

    def run(self):
        import array
        while True:
            daten = self.prozess.stdout.read(3200)      # 100 ms
            if not daten:
                return
            werte = array.array("h", daten)
            rms = (sum(w * w for w in werte) / len(werte)) ** 0.5
            if rms > self.SCHWELLE:
                self.zuletzt_laut = time.time()
                self.laute_bloecke.append(self.zuletzt_laut)
                del self.laute_bloecke[:-200]

    def laut_seit(self, zeitpunkt):
        """Wie viele laute 100-ms-Bloecke seit zeitpunkt."""
        return sum(1 for t in self.laute_bloecke if t >= zeitpunkt)

    def ruhig_seit(self):
        return time.time() - self.zuletzt_laut


def geraete(art):
    zeilen = subprocess.run(["pactl", "list", "short", art], capture_output=True,
                            text=True).stdout.splitlines()
    return [z.split("\t")[1] for z in zeilen if "\t" in z]


def ton_holen():
    """Die Soundkarte ins Vorfuehrkonto holen. (Lautsprecher, Mikrofon) oder ("", "").

    ERSTER DREH, 2026-10-05: Der Standard-Lautsprecher war "auto_null" - die
    Nirgendwo-Ausgabe. Das Konto dialosadmin steht in der Gruppe "audio" und
    behaelt die Soundkarte auch im Hintergrund; seine Spracherkennung hat das
    Mikrofon dauernd offen. Das PipeWire des Vorfuehrkontos fand deshalb beim
    Anmelden keine Karte und sucht von selbst nicht noch einmal. Darum: Das
    andere Konto gibt die Karte vorher frei (siehe Drehbuch), und hier wird
    PipeWire neu gestartet, damit es neu sucht.
    """
    subprocess.run(["systemctl", "--user", "restart", "pipewire.service",
                    "pipewire-pulse.service", "wireplumber.service", "filter-chain.service"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        echt = [n for n in geraete("sinks") if n.startswith(("alsa_output.", "bluez_output."))]
        if echt:
            break
        time.sleep(0.5)
    else:
        return "", ""
    time.sleep(2)                       # Echo-Unterdrueckung und Dienste nachziehen lassen
    mikrofone = [n for n in geraete("sources") if n.startswith("alsa_input.")]
    subprocess.run(["pactl", "set-default-sink", echt[0]])
    if mikrofone:
        subprocess.run(["pactl", "set-default-source", mikrofone[0]])
    return echt[0], (mikrofone[0] if mikrofone else "")


def hinweis(text):
    """Sichtbar statt hoerbar - fuer den Fall, dass es keinen Ton gibt."""
    melde(text.replace("\n", " "))
    subprocess.run(["zenity", "--warning", "--title=DialOS-Vorführung", f"--text={text}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ansage(text):
    """Rueckmeldung an Stephan - nur ausserhalb der Aufnahme benutzen."""
    subprocess.run(["/usr/local/bin/dialos-say.py", text], capture_output=True, timeout=60)


def say_log_laenge():
    try:
        return os.path.getsize(SAY_LOG)
    except OSError:
        return 0


def say_log_neu(ab):
    try:
        with open(SAY_LOG, encoding="utf-8", errors="replace") as f:
            f.seek(ab)
            return f.read()
    except OSError:
        return ""


def echo_umhaengen(quelle):
    """Den Aufnahme-Strom der Echo-Unterdrueckung an quelle haengen."""
    try:
        stroeme = json.loads(subprocess.run(["pactl", "-f", "json", "list", "source-outputs"],
                                            capture_output=True, text=True).stdout or "[]")
    except ValueError:
        stroeme = []
    for strom in stroeme:
        if strom.get("properties", {}).get("node.name") == "dialos.echo.aufnahme":
            r = subprocess.run(["pactl", "move-source-output", str(strom["index"]), quelle])
            melde(f"Echo-Unterdrueckung hoert jetzt: {quelle} (Rueckgabe {r.returncode})")
            return r.returncode == 0
    melde("!! Aufnahme-Strom der Echo-Unterdrueckung nicht gefunden")
    return False


def erkenner_neu_starten():
    subprocess.run(["pkill", "-f", ERKENNER])
    time.sleep(1.5)
    # Als eigene Einheit, nicht als Kind dieses Skripts - sonst stirbt die
    # Erkennung mit dem Dreh. Name wie beim Autostart.
    # Popen, NICHT run: "systemd-run --scope" fuehrt das Programm im
    # Vordergrund aus und kehrt erst zurueck, wenn es endet - die Erkennung
    # endet nie. Am 2026-10-05 hing der erste Dreh genau hier, vor der Aufnahme.
    subprocess.Popen(["systemd-run", "--user", "--scope", "--collect", "--quiet",
                      f"--unit=app-gnome-dialos\\x2dsprachbefehl\\x2ddesktop-video{int(time.time())}",
                      "--", ERKENNER],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(4)


def anna_spricht(nr):
    wav = os.path.join(ANNA_ORDNER, f"{nr:02d}.wav")
    subprocess.run(["pw-play", f"--target={EINGANG}",
                    "--properties={ application.name = dialos-video-anna }", wav])


def warten(pegel, ab, erwartet, ruhe, zeitgrenze=45):
    if erwartet is None:
        return True
    bis = time.time() + zeitgrenze
    while time.time() < bis:
        neu = say_log_neu(ab)
        if neu.strip() and erwartet in neu:
            break
        time.sleep(0.2)
    else:
        melde(f"  !! erwartete Ansage kam nicht: {erwartet!r} - neu im Protokoll: "
              f"{say_log_neu(ab).strip()[-200:]!r}")
        return False
    # Die Zeile steht im Protokoll, sobald die Ansage beginnt - der Ton kommt
    # bis zu zwei Sekunden spaeter (Piper rechnet erst). Erst auf SPRACHE warten,
    # dann auf Ruhe; sonst gaelte die Stille VOR der Ansage schon als ihr Ende.
    # MINDESTENS 5 LAUTE BLOECKE (0,5 s): Beim ersten Dreh (2026-10-05) kam vor
    # der Frage ein kurzer Ton - der galt als Ansage, die Stille danach als ihr
    # Ende, und Annas "Ja!" fiel mitten in Michaels Frage.
    gefunden = time.time()
    while pegel.laut_seit(gefunden - 0.5) < 5 and time.time() - gefunden < 15:
        time.sleep(0.1)
    while pegel.ruhig_seit() < ruhe and time.time() - gefunden < 120:
        time.sleep(0.1)
    return True


def drehen():
    if getpass_user() in ("dialosadmin", "nutzer"):
        print("Nur im Vorfuehrkonto.", file=sys.stderr)
        return 2
    if "--im-hintergrund" not in sys.argv:
        # Ein haengengebliebener frueherer Dreh belegt den Einheitennamen.
        subprocess.run(["systemctl", "--user", "stop", "dialos-video-dreh"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["systemctl", "--user", "reset-failed", "dialos-video-dreh"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Das Terminal waere sonst im Bild. Der Dreh laeuft als eigene Einheit
        # weiter, dieses Fenster geht zu.
        subprocess.run(["systemd-run", "--user", "--collect", "--quiet",
                        "--unit=dialos-video-dreh", sys.executable, os.path.abspath(__file__),
                        "drehen", "--im-hintergrund"], check=True)
        print("Der Dreh beginnt in 10 Sekunden. Dieses Fenster schliesst sich.\n"
              f"Protokoll: {DREH_LOG}")
        time.sleep(2)
        os.kill(os.getppid(), signal.SIGHUP)
        return 0

    time.sleep(8)
    melde("=== Dreh beginnt ===")
    prozesse = []
    mikrofon_vorher = ""
    # Ein frueherer Dreh-Stand legte hier eine Mikrofonwahl ab - die darf nicht
    # liegen bleiben, sonst hoert die Befehlserkennung an der Echo-Unterdrueckung vorbei.
    try:
        os.remove(os.path.join(DIALOS_CONF, "befehl-mikrofon"))
    except OSError:
        pass
    obs = None
    abbruch = "Der Dreh ist abgebrochen."
    os.makedirs(VIDEO_ORDNER, exist_ok=True)
    vorher = set(os.listdir(VIDEO_ORDNER))
    try:
        lautsprecher, mikrofon_vorher = ton_holen()
        melde(f"Lautsprecher {lautsprecher!r}, Mikrofon {mikrofon_vorher!r}")
        if not lautsprecher:
            hinweis("Der Dreh ist abgebrochen: Im Vorführkonto gibt es keinen Lautsprecher.\n\n"
                    "Die Soundkarte ist noch von einem anderen Konto belegt. "
                    "Zurück zu dialosadmin wechseln und Claude Bescheid sagen.")
            abbruch = False
            return 1
        ansage("Der Dreh beginnt. Bitte nichts anfassen, bis ich sage, dass er fertig ist.")
        # Das virtuelle Mikrofon: hinein eine Senke, heraus eine Quelle.
        prozesse.append(subprocess.Popen(
            ["pw-loopback", "-n", "dialos-anna", "-c", "1", "-m", "[ MONO ]",
             # Niedrigste Prioritaet: Im frischen Vorfuehrkonto ist noch kein
             # Standardgeraet gespeichert - sonst koennte WirePlumber die Senke
             # zum Lautsprecher machen, und Michael spraeche in Annas Mikrofon.
             "--capture-props", f"media.class=Audio/Sink node.name={EINGANG} "
                                "node.description=DialOS-Vorfuehrung-Eingang "
                                "priority.session=1 priority.driver=1",
             "--playback-props", f"media.class=Audio/Source node.name={MIKROFON} "
                                 "node.description=DialOS-Vorfuehrung-Mikrofon "
                                 "priority.session=1 priority.driver=1"],
            stdout=open(DREH_LOG, "a"), stderr=subprocess.STDOUT))
        time.sleep(2)
        # DAUERND STILLE HINEIN: Ohne Strom schlaeft der Knoten ein, und beim
        # Aufwachen geht der Anfang verloren. Beim dritten Dreh (2026-10-05)
        # kam von Annas "Ja!" (0,7 s) nur eine Zehntelsekunde an.
        prozesse.append(subprocess.Popen(
            ["pw-cat", "--playback", f"--target={EINGANG}", "--rate=48000", "--channels=1",
             "--format=s16", "--properties={ application.name = dialos-video-stille }", "-"],
            stdin=open("/dev/zero", "rb"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        # Beim ersten Dreh stieg pw-loopback sofort aus - ohne dass es jemand merkte.
        if prozesse[0].poll() is not None:
            melde(f"!! virtuelles Mikrofon ist ausgestiegen (Rueckgabe {prozesse[0].returncode})")
            return 1
        # Im frischen Vorfuehrkonto ist kein Standardgeraet gespeichert, und
        # WirePlumber nahm beim ersten Dreh (2026-10-05) trotz niedriger
        # Prioritaet Annas Eingang als Lautsprecher. Deshalb ausdruecklich
        # zuruecksetzen - und erst abbrechen, wenn auch das nicht hilft.
        for geraet, art in ((lautsprecher, "sink"), (mikrofon_vorher, "source")):
            if geraet:
                subprocess.run(["pactl", f"set-default-{art}", geraet])
        time.sleep(1)
        standard = subprocess.run(["pactl", "get-default-sink"], capture_output=True,
                                  text=True).stdout.strip()
        if standard == EINGANG or not standard.startswith(("alsa_", "bluez_")):
            melde(f"!! Standard-Lautsprecher ist {standard!r} - Abbruch")
            ansage("Der Dreh ist abgebrochen. Der Lautsprecher ließ sich nicht einstellen.")
            abbruch = False             # schon angesagt
            return 1
        # DIE ECHO-UNTERDRUECKUNG HOERT ANNA ZU. Alle DialOS-Programme - Befehle,
        # Diktat, Rueckfragen, Mail - hoeren auf "dialos_mikrofon_ohne_echo";
        # nur die Befehlserkennung kennt eine Mikrofonwahl. Beim dritten Dreh
        # (2026-10-05) hoerte die Befehlserkennung Anna, die Rueckfrage danach
        # aber ins Leere ("Ich habe nichts verstanden"). Deshalb wird der
        # Aufnahme-Strom der Echo-Unterdrueckung auf Annas Mikrofon umgehaengt -
        # dann laeuft alles auf dem Weg, den es auch im Betrieb nimmt.
        if not echo_umhaengen(MIKROFON):
            ansage("Der Dreh ist abgebrochen. Ich kann das Mikrofon nicht umstellen.")
            abbruch = False
            return 1
        erkenner_neu_starten()
        pegel = Pegel()
        pegel.start()

        obs = subprocess.Popen(["obs", "--startrecording", "--minimize-to-tray",
                                "--disable-shutdown-check", "--profile", "DialOS",
                                "--collection", "DialOS", "--scene", "DialOS"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            if set(os.listdir(VIDEO_ORDNER)) - vorher:
                break
            time.sleep(0.5)
        else:
            melde("!! OBS nimmt nicht auf - Abbruch")
            ansage("Der Dreh ist abgebrochen. Die Aufnahme ist nicht angelaufen.")
            abbruch = False
            return 1
        time.sleep(3)

        for nr, szene, (text, erwartet, ruhe, pause) in saetze():
            melde(f"[{szene}] {nr:02d} Anna: {text}")
            ab = say_log_laenge()
            anna_spricht(nr)
            if not warten(pegel, ab, erwartet, ruhe):
                melde("!! Szene laeuft nicht wie im Drehbuch - Dreh abgebrochen")
                abbruch = f"Der Dreh ist bei Szene {szene.split()[0]} abgebrochen."
                break
            time.sleep(pause)
        else:
            melde("=== alle Szenen durch ===")
            abbruch = None
        time.sleep(3)
    finally:
        if obs and obs.poll() is None:
            obs.send_signal(signal.SIGINT)
            try:
                obs.wait(30)
            except subprocess.TimeoutExpired:
                obs.terminate()
        # Aufraeumen - auch bei Abbruch: Echo-Unterdrueckung zurueck aufs
        # eingebaute Mikrofon, Erkennung neu.
        if mikrofon_vorher:
            echo_umhaengen(mikrofon_vorher)
        for p in prozesse:
            p.terminate()
        erkenner_neu_starten()
        # Nur eine Aufnahme aus DIESEM Lauf - sonst laege nach einem Abbruch
        # eine alte Datei als Ergebnis da.
        neueste = sorted((os.path.join(VIDEO_ORDNER, n)
                          for n in set(os.listdir(VIDEO_ORDNER)) - vorher),
                         key=os.path.getmtime)
        if neueste:
            ziel = os.path.join(ERGEBNIS, "dialos-vorfuehrung.mkv")
            shutil.copy(neueste[-1], ziel)
            os.chmod(ziel, 0o644)
            melde(f"Video: {ziel}")
        # Das Protokoll immer - gerade nach einem Abbruch wird es gebraucht.
        try:
            shutil.copy(DREH_LOG, os.path.join(ERGEBNIS, "dreh.log"))
            os.chmod(os.path.join(ERGEBNIS, "dreh.log"), 0o644)
        except OSError:
            pass
        # NACH der Aufnahme - steht also nicht im Video.
        if abbruch is None:
            ansage("Der Dreh ist fertig. Du kannst zurück wechseln.")
        elif abbruch:
            ansage(abbruch)
    return 0


# =============================================================== nachbearbeiten

def nachbearbeiten():
    mkv = os.path.join(ERGEBNIS, "dialos-vorfuehrung.mkv")
    ziel = sys.argv[2] if len(sys.argv) > 2 else ERGEBNIS
    os.makedirs(ziel, exist_ok=True)
    schritte = [
        # Web-Fassung: Bild + Mischung (Spur 1).
        ["ffmpeg", "-y", "-i", mkv, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
         os.path.join(ziel, "dialos-vorfuehrung.mp4")],
        ["ffmpeg", "-y", "-i", mkv, "-map", "0:a:1", "-ac", "1", "-c:a", "pcm_s24le",
         os.path.join(ziel, "dialos-vorfuehrung-dialos.wav")],
        ["ffmpeg", "-y", "-i", mkv, "-map", "0:a:2", "-ac", "1", "-c:a", "pcm_s24le",
         os.path.join(ziel, "dialos-vorfuehrung-anna.wav")],
    ]
    for s in schritte:
        r = subprocess.run(s, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:], file=sys.stderr)
            return 1
        print("  " + s[-1])
    return 0


def main():
    befehl = sys.argv[1] if len(sys.argv) > 1 else ""
    return {"vorbereiten": vorbereiten, "einrichten": einrichten, "drehen": drehen, "alles": alles,
            "nachbearbeiten": nachbearbeiten}.get(befehl, lambda: print(__doc__) or 2)()


if __name__ == "__main__":
    sys.exit(main())
