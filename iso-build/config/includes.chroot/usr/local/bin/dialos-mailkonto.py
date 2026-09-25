#!/usr/bin/python3
"""DialOS: legt das Mailkonto aus den persoenlichen Daten in Thunderbird an.

Stephan am 2026-09-25: "koennen nicht in der Maske der Persoenlichen Daten auch
gleich alles was fuer die Einrichtung von Thunderbird betrifft einpflegen" -
und: "Ich moechte gerne alle Kundendaten zentral erfassen und dann auf die
Programme verteilen! So kann ich nix uebersehen."

DIE MASKE ERFASST, DIESES WERKZEUG VERTEILT. Mailadresse, Benutzername und
Server stehen in ~/.config/dialos/persoenliche-daten.txt wie alle anderen
Kundendaten. Das Passwort NICHT: Es kommt ueber stdin und geht direkt in
Thunderbirds eigenen, verschluesselten Passwortspeicher (logins.json +
key4.db). In keiner DialOS-Datei steht es je.

LAEUFT ALS DAS KONTO SELBST - fuer ein fremdes Konto ruft die Maske es ueber
/usr/local/sbin/dialos-persoenliche-daten-konto (pkexec, runuser) auf.

DREI FALLEN, ALLE AM 2026-09-25 IN EINEM TEST-HEIMATVERZEICHNIS GEMESSEN:

1. Ein mit "thunderbird -CreateProfile" angelegtes Profil wird beim ersten
   echten Start NICHT benutzt: Thunderbird legt ein zweites an
   ("default-default") und bindet die Installation in installs.ini fest
   daran. Deshalb startet dieses Werkzeug Thunderbird einmal unsichtbar
   (--headless), laesst es sein Profil selbst waehlen und liest die Wahl aus
   installs.ini. Genau das Profil benutzt Thunderbird danach auch.
2. Konten gehoeren nach prefs.js, NICHT nach user.js wie die Signatur: user.js
   wird bei jedem Start ueber prefs.js gelegt - ein Konto, das der Helfer
   spaeter in der Oberflaeche dazunimmt, verschwaende beim naechsten Start
   wieder aus der Kontenliste. prefs.js schreibt Thunderbird beim Beenden
   selbst neu, deshalb muss es dabei geschlossen sein.
3. Thunderbird muss auch fuer logins.json geschlossen sein - es haelt den
   Passwortspeicher offen und schreibt ihn beim Beenden zurueck.

SERVER AUS DER ANBIETER-DATENBANK: Sind die Serverfelder leer, fragt das
Werkzeug Mozillas ISPDB (autoconfig.thunderbird.net) nach der Domain der
Mailadresse - dieselbe Quelle, die Thunderbirds eigener Assistent nimmt.
Was in der Maske steht, geht vor.

Aufruf:
  dialos-mailkonto.py pruefen                     was eingetragen wuerde, nichts aendern
  dialos-mailkonto.py einrichten [--passwort-stdin]
Rueckgabewerte: 0 ok, 2 Daten fehlen, 3 Thunderbird laeuft, 4 Server unbekannt,
5 Thunderbird/Passwortspeicher-Fehler.
"""

import base64
import configparser
import ctypes
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import uuid
import xml.etree.ElementTree as ET

PERSOENLICHE_DATEN_SKRIPT = "/usr/local/bin/dialos-persoenliche-daten.py"
HIER = os.path.dirname(os.path.abspath(__file__))
TB_ORDNER = os.path.join(os.path.expanduser("~"), ".thunderbird")
ISPDB = "https://autoconfig.thunderbird.net/v1.1/"
# socketType in Thunderbirds Einstellungen: 0 unverschluesselt, 2 STARTTLS, 3 SSL/TLS
SOCKET = {"SSL": 3, "STARTTLS": 2, "plain": 0}
# Steht in prefs.js, wenn das Konto von DialOS stammt - Wert: wann eingetragen.
MARKE = "dialos.mailkonto.eingetragen"


def fehler(text, code):
    print(text, file=sys.stderr)
    sys.exit(code)


def daten_lesen():
    modul = os.path.join(HIER, "dialos-persoenliche-daten.py")
    if not os.path.exists(modul):
        modul = PERSOENLICHE_DATEN_SKRIPT
    spec = importlib.util.spec_from_file_location("persoenliche_daten", modul)
    pd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pd)
    return pd, pd.lesen()


# ------------------------------------------------------------------ Server
def aus_ispdb(mail):
    """Server aus Mozillas Anbieter-Datenbank, oder None."""
    domain = mail.rsplit("@", 1)[-1].lower()
    try:
        with urllib.request.urlopen(ISPDB + domain, timeout=10) as antwort:
            wurzel = ET.fromstring(antwort.read())
    except Exception:
        return None
    ein = next((s for s in wurzel.iter("incomingServer") if s.get("type") == "imap"), None)
    aus = next((s for s in wurzel.iter("outgoingServer") if s.get("type") == "smtp"), None)
    if ein is None or aus is None:
        return None

    def werte(s):
        return {"server": s.findtext("hostname", ""), "port": s.findtext("port", ""),
                "socket": s.findtext("socketType", "SSL"),
                "benutzer": s.findtext("username", "%EMAILADDRESS%")}
    return werte(ein), werte(aus)


def server_bestimmen(daten):
    """(eingang, ausgang, quelle) - jeweils dict mit server/port/socket/benutzer."""
    mail = daten.get("mail", "")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", mail):
        fehler("Keine gueltige E-Mail-Adresse in den persoenlichen Daten.", 2)
    benutzer = daten.get("mail_benutzer") or mail
    if daten.get("imap_server") and daten.get("smtp_server"):
        ein_port = daten.get("imap_port") or "993"
        aus_port = daten.get("smtp_port") or "587"
        ein = {"server": daten["imap_server"], "port": ein_port,
               "socket": "SSL" if ein_port == "993" else "STARTTLS"}
        aus = {"server": daten["smtp_server"], "port": aus_port,
               "socket": "SSL" if aus_port == "465" else "STARTTLS"}
        quelle = "persoenliche Daten"
    else:
        gefunden = aus_ispdb(mail)
        if not gefunden:
            fehler("Die Server fuer " + mail.rsplit("@", 1)[-1] + " stehen nicht in der "
                   "Anbieter-Datenbank. Bitte Posteingang- und Postausgang-Server in der "
                   "Maske eintragen.", 4)
        ein, aus = gefunden
        # Was in der Maske steht, geht vor - auch einzeln.
        for d, praefix in ((ein, "imap"), (aus, "smtp")):
            if daten.get(praefix + "_server"):
                d["server"] = daten[praefix + "_server"]
            if daten.get(praefix + "_port"):
                d["port"] = daten[praefix + "_port"]
        quelle = "Anbieter-Datenbank (ISPDB)"
    # Benutzername: aus der Maske, sonst die Vorgabe des Anbieters
    # (%EMAILADDRESS% bzw. %EMAILLOCALPART%), sonst die Mailadresse.
    for d in (ein, aus):
        if daten.get("mail_benutzer"):
            d["benutzer"] = daten["mail_benutzer"]
        else:
            d["benutzer"] = (d.get("benutzer") or "%EMAILADDRESS%") \
                .replace("%EMAILADDRESS%", mail) \
                .replace("%EMAILLOCALPART%", mail.split("@")[0]) or benutzer
    return ein, aus, quelle


# ------------------------------------------------------------------ Profil
def thunderbird_laeuft():
    ergebnis = subprocess.run(["pgrep", "-u", str(os.getuid()), "-x", "thunderbird"],
                              capture_output=True)
    if ergebnis.returncode == 0:
        return True
    ergebnis = subprocess.run(["pgrep", "-u", str(os.getuid()), "-f",
                               "/usr/lib/thunderbird/thunderbird"], capture_output=True)
    return ergebnis.returncode == 0


def profil_aus_installs():
    ini = os.path.join(TB_ORDNER, "installs.ini")
    if not os.path.exists(ini):
        return None
    cp = configparser.ConfigParser()
    cp.read(ini)
    for abschnitt in cp.sections():
        pfad = cp[abschnitt].get("Default")
        if pfad:
            voll = pfad if os.path.isabs(pfad) else os.path.join(TB_ORDNER, pfad)
            if os.path.isdir(voll):
                return voll
    return None


def profil_sicherstellen():
    """Das Profil, das Thunderbird wirklich benutzt - notfalls von ihm anlegen lassen."""
    profil = profil_aus_installs()
    if profil:
        return profil
    # Falle 1: Thunderbird waehlt sein Profil selbst. Einmal unsichtbar starten,
    # warten bis installs.ini da ist, dann ordentlich beenden (SIGTERM).
    umgebung = {k: v for k, v in os.environ.items()
                if k not in ("DISPLAY", "WAYLAND_DISPLAY")}
    prozess = subprocess.Popen(["thunderbird", "--headless"], env=umgebung,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            time.sleep(1)
            profil = profil_aus_installs()
            if profil and os.path.exists(os.path.join(profil, "prefs.js")):
                time.sleep(3)
                break
    finally:
        prozess.terminate()
        try:
            prozess.wait(timeout=20)
        except subprocess.TimeoutExpired:
            prozess.kill()
            prozess.wait()
    profil = profil_aus_installs()
    if not profil:
        fehler("Thunderbird hat kein Profil angelegt.", 5)
    return profil


# ------------------------------------------------------------------ prefs.js
def js(wert):
    if isinstance(wert, bool):
        return "true" if wert else "false"
    if isinstance(wert, int):
        return str(wert)
    return json.dumps(wert, ensure_ascii=False)


def einstellungen(daten, ein, aus):
    mail = daten["mail"]
    name = " ".join(daten[k] for k in ("titel", "vorname", "name") if daten.get(k))
    e = {
        "mail.accountmanager.accounts": "account1,account2",
        "mail.accountmanager.defaultaccount": "account1",
        "mail.accountmanager.localfoldersserver": "server2",
        "mail.account.account1.identities": "id1",
        "mail.account.account1.server": "server1",
        "mail.account.account2.server": "server2",
        "mail.account.lastKey": 2,
        "mail.identity.id1.fullName": name or mail,
        "mail.identity.id1.useremail": mail,
        "mail.identity.id1.smtpServer": "smtp1",
        "mail.identity.id1.valid": True,
        "mail.server.server1.type": "imap",
        "mail.server.server1.hostname": ein["server"],
        "mail.server.server1.port": int(ein["port"]),
        "mail.server.server1.socketType": SOCKET.get(ein["socket"], 3),
        "mail.server.server1.userName": ein["benutzer"],
        "mail.server.server1.name": mail,
        "mail.server.server1.authMethod": 3,
        "mail.server.server1.login_at_startup": True,
        "mail.server.server1.check_new_mail": True,
        "mail.server.server2.type": "none",
        "mail.server.server2.hostname": "Local Folders",
        "mail.server.server2.userName": "nobody",
        "mail.server.server2.name": "Lokale Ordner",
        "mail.smtpservers": "smtp1",
        "mail.smtp.defaultserver": "smtp1",
        "mail.smtpserver.smtp1.hostname": aus["server"],
        "mail.smtpserver.smtp1.port": int(aus["port"]),
        "mail.smtpserver.smtp1.try_ssl": SOCKET.get(aus["socket"], 2),
        "mail.smtpserver.smtp1.username": aus["benutzer"],
        "mail.smtpserver.smtp1.authMethod": 3,
        "mail.smtpserver.smtp1.description": mail,
        # Kein "Als Standard-Mailprogramm festlegen?" beim ersten Start - den
        # Dialog sieht der blinde Nutzer nicht, und er haelt das Fenster auf.
        "mail.shell.checkDefaultClient": False,
    }
    return e


def prefs_schreiben(profil, werte):
    """Traegt die Kontowerte in prefs.js ein - ersetzt, nie verdoppelt.

    ERKENNUNG UEBER EINE EINSTELLUNG, NICHT UEBER KOMMENTARE: Thunderbird
    schreibt prefs.js beim Beenden neu und wirft dabei jede Kommentarzeile weg
    (am 2026-09-25 im Test gesehen). Die Marke MARKE ueberlebt das.
    """
    pfad = os.path.join(profil, "prefs.js")
    try:
        with open(pfad, encoding="utf-8") as f:
            zeilen = f.read().splitlines()
    except OSError:
        zeilen = []

    def schluessel(zeile):
        treffer = re.match(r'\s*user_pref\("([^"]+)"', zeile)
        return treffer.group(1) if treffer else None

    vorhanden = {schluessel(z) for z in zeilen}
    # Hat jemand in der Oberflaeche selbst ein Konto angelegt, bricht das
    # Werkzeug ab, statt die Kontenliste zu ueberschreiben.
    if "mail.accountmanager.accounts" in vorhanden and MARKE not in vorhanden:
        fehler("In diesem Profil gibt es schon ein Mailkonto, das nicht von DialOS stammt. "
               "Nichts geaendert - bitte in Thunderbird selbst anpassen.", 5)
    eigene = set(werte) | {MARKE}
    zeilen = [z for z in zeilen if schluessel(z) not in eigene]
    zeilen += [f"user_pref({js(k)}, {js(v)});" for k, v in werte.items()]
    zeilen.append(f"user_pref({js(MARKE)}, {js(time.strftime('%Y-%m-%d %H:%M'))});")
    with open(pfad + ".neu", "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen) + "\n")
    os.chmod(pfad + ".neu", 0o600)
    os.replace(pfad + ".neu", pfad)


# ------------------------------------------------------------------ Passwort
class SECItem(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint), ("data", ctypes.c_void_p), ("len", ctypes.c_uint)]


def nss_laden():
    for pfad in ("/usr/lib/thunderbird/libnss3.so", "libnss3.so",
                 "/usr/lib/x86_64-linux-gnu/libnss3.so"):
        try:
            return ctypes.CDLL(pfad)
        except OSError:
            continue
    fehler("libnss3 nicht gefunden - Passwort nicht gespeichert.", 5)


def verschluesseln(nss, klartext):
    daten = klartext.encode("utf-8")
    puffer = ctypes.create_string_buffer(daten, len(daten))
    eingabe = SECItem(0, ctypes.cast(puffer, ctypes.c_void_p), len(daten))
    schluessel = SECItem(0, None, 0)
    ausgabe = SECItem(0, None, 0)
    if nss.PK11SDR_Encrypt(ctypes.byref(schluessel), ctypes.byref(eingabe),
                           ctypes.byref(ausgabe), None) != 0:
        fehler("Verschluesseln im Passwortspeicher fehlgeschlagen.", 5)
    roh = ctypes.string_at(ausgabe.data, ausgabe.len)
    nss.SECITEM_ZfreeItem(ctypes.byref(ausgabe), 0)
    return base64.b64encode(roh).decode("ascii")


def entschluesseln(nss, text):
    roh = base64.b64decode(text)
    puffer = ctypes.create_string_buffer(roh, len(roh))
    eingabe = SECItem(0, ctypes.cast(puffer, ctypes.c_void_p), len(roh))
    ausgabe = SECItem(0, None, 0)
    if nss.PK11SDR_Decrypt(ctypes.byref(eingabe), ctypes.byref(ausgabe), None) != 0:
        return None
    klar = ctypes.string_at(ausgabe.data, ausgabe.len).decode("utf-8")
    nss.SECITEM_ZfreeItem(ctypes.byref(ausgabe), 0)
    return klar


def passwort_speichern(profil, eintraege):
    """eintraege: [(ursprung, benutzer, passwort)] - z. B. ("imap://imap.gmx.net", ...)."""
    nss = nss_laden()
    nss.NSS_InitReadWrite.argtypes = [ctypes.c_char_p]
    nss.PK11_GetInternalKeySlot.restype = ctypes.c_void_p
    nss.PK11_NeedUserInit.argtypes = [ctypes.c_void_p]
    nss.PK11_InitPin.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    nss.PK11_FreeSlot.argtypes = [ctypes.c_void_p]
    if nss.NSS_InitReadWrite(("sql:" + profil).encode()) != 0:
        fehler("Passwortspeicher des Profils laesst sich nicht oeffnen.", 5)
    try:
        slot = nss.PK11_GetInternalKeySlot()
        # Frisches Profil: key4.db hat noch keinen Schluessel - mit leerem
        # Hauptpasswort anlegen, wie Thunderbird es selbst tut.
        if slot and nss.PK11_NeedUserInit(slot):
            nss.PK11_InitPin(slot, None, b"")
        if slot:
            nss.PK11_FreeSlot(slot)
        pfad = os.path.join(profil, "logins.json")
        try:
            with open(pfad, encoding="utf-8") as f:
                speicher = json.load(f)
        except (OSError, ValueError):
            speicher = {"nextId": 1, "logins": [], "potentiallyVulnerablePasswords": [],
                        "dismissedBreachAlertsByLoginGUID": {}, "version": 3}
        jetzt = int(time.time() * 1000)
        for ursprung, benutzer, passwort in eintraege:
            speicher["logins"] = [l for l in speicher["logins"]
                                  if not (l.get("hostname") == ursprung and
                                          entschluesseln(nss, l["encryptedUsername"]) == benutzer)]
            speicher["logins"].append({
                "id": speicher["nextId"], "hostname": ursprung, "httpRealm": ursprung,
                "formSubmitURL": None, "usernameField": "", "passwordField": "",
                "encryptedUsername": verschluesseln(nss, benutzer),
                "encryptedPassword": verschluesseln(nss, passwort),
                "guid": "{" + str(uuid.uuid4()) + "}", "encType": 1,
                "timeCreated": jetzt, "timeLastUsed": jetzt,
                "timePasswordChanged": jetzt, "timesUsed": 1})
            speicher["nextId"] += 1
        with open(pfad + ".neu", "w", encoding="utf-8") as f:
            json.dump(speicher, f)
        os.chmod(pfad + ".neu", 0o600)
        os.replace(pfad + ".neu", pfad)
        # Gegenprobe: jedes Passwort muss sich wieder entschluesseln lassen.
        for ursprung, benutzer, passwort in eintraege:
            treffer = [l for l in speicher["logins"] if l["hostname"] == ursprung]
            if not treffer or entschluesseln(nss, treffer[-1]["encryptedPassword"]) != passwort:
                fehler(f"Gegenprobe fehlgeschlagen fuer {ursprung}.", 5)
    finally:
        nss.NSS_Shutdown()


# ------------------------------------------------------------------ Ablauf
def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("pruefen", "einrichten"):
        fehler(__doc__, 2)
    _, daten = daten_lesen()
    ein, aus, quelle = server_bestimmen(daten)
    print(f"Mailadresse:  {daten['mail']}")
    print(f"Posteingang:  {ein['server']}:{ein['port']} ({ein['socket']}), Benutzer {ein['benutzer']}")
    print(f"Postausgang:  {aus['server']}:{aus['port']} ({aus['socket']}), Benutzer {aus['benutzer']}")
    print(f"Quelle:       {quelle}")
    if sys.argv[1] == "pruefen":
        return 0

    passwort = ""
    if "--passwort-stdin" in sys.argv:
        passwort = sys.stdin.read().rstrip("\n")
    if thunderbird_laeuft():
        fehler("Thunderbird laeuft - bitte schliessen, dann erneut speichern.", 3)
    profil = profil_sicherstellen()
    if thunderbird_laeuft():
        time.sleep(3)
        if thunderbird_laeuft():
            fehler("Thunderbird laeuft noch - nichts geaendert.", 3)
    prefs_schreiben(profil, einstellungen(daten, ein, aus))
    print(f"Profil:       {profil}")
    if passwort:
        passwort_speichern(profil, [
            (f"imap://{ein['server']}", ein["benutzer"], passwort),
            (f"smtp://{aus['server']}", aus["benutzer"], passwort)])
        print("Passwort:     im Passwortspeicher von Thunderbird (Posteingang und Postausgang)")
    else:
        print("Passwort:     keins angegeben - Thunderbird fragt beim ersten Abruf")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as unerwartet:
        fehler(f"Unerwarteter Fehler: {unerwartet}", 5)
