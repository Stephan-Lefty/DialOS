#!/usr/bin/env python3
"""Legt die Datenschutzseite für DialOS Mobil auf dialos.org an.

Erzeugt eine NEUE Seite. Die bestehende Seite /datenschutzerklaerung/ (id 3),
die DialOS selbst betrifft, wird nicht angefasst.
"""
import base64
import json
import sys
import urllib.request
from pathlib import Path

ENV = Path("/mnt/raid/eigene Daten/GitHub/Stephan-Lefty/DialOS/Wordpressinstallation/.env")
SLUG = "dialos-mobil-datenschutz"
TITLE = "Datenschutzerklärung – DialOS Mobil (Android-App)"


def load_env():
    cfg = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def h(level, text):
    attrs = ' {"level":3}' if level == 3 else ""
    return (
        "<!-- wp:heading" + attrs + " -->\n"
        + '<h%d class="wp-block-heading">%s</h%d>\n' % (level, text, level)
        + "<!-- /wp:heading -->"
    )


def p(text):
    return f"<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->"


def table(rows, head=("Berechtigung", "Wozu sie gebraucht wird")):
    body = "".join(
        f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows
    )
    return (
        '<!-- wp:table -->\n<figure class="wp-block-table"><table>'
        f"<thead><tr><th>{head[0]}</th><th>{head[1]}</th></tr></thead>"
        f"<tbody>{body}</tbody></table></figure>\n<!-- /wp:table -->"
    )


blocks = [
    h(2, "Stand: 19.08.2026 · gültig ab App-Version 0.6.0"),

    p("<strong>DialOS Mobil sendet keine Daten. An niemanden.</strong>"),

    p("Die App besitzt keine Internetberechtigung. Sie kann technisch gar keine "
      "Verbindung aufbauen – weder zu einem Server des Anbieters noch zu Dritten. "
      "Es gibt keine Werbung, keine Analyse, keine Absturzberichte und keine "
      "Benutzerkonten."),

    p("Diese Erklärung betrifft ausschließlich die Android-App "
      "<strong>DialOS Mobil</strong>. Für die Website und das Desktop-System DialOS "
      'gilt die <a href="https://dialos.org/datenschutzerklaerung/">allgemeine '
      "Datenschutzerklärung</a>."),

    h(2, "Verantwortlich"),
    p("Stephan Rösner<br>E-Mail: "
      '<a href="mailto:info@naturlust.net">info@naturlust.net</a>'),

    h(2, "Welche Daten die App verarbeitet"),
    p("Alle nachfolgend genannten Daten werden <strong>ausschließlich auf dem "
      "Gerät</strong> verarbeitet und verlassen es zu keinem Zeitpunkt."),

    h(3, "Mikrofonaufnahmen"),
    p("Die Spracherkennung läuft offline mit "
      '<a href="https://alphacephei.com/vosk/" rel="noopener" target="_blank">Vosk</a>; '
      "das deutsche Sprachmodell ist in der App enthalten. Aufgenommener Ton wird "
      "unmittelbar in Text umgewandelt und danach verworfen. <strong>Es wird keine "
      "Tonaufnahme gespeichert</strong>, weder dauerhaft noch zwischengespeichert. "
      "Der erkannte Text bleibt nur so lange im Arbeitsspeicher, wie der laufende "
      "Sprachbefehl es erfordert."),

    h(3, "Kontakte"),
    p("Die App liest Namen, Rufnummern und deren Bezeichnung (Mobil, Privat, Arbeit) "
      "aus dem Adressbuch des Telefons, um einen gesprochenen Namen der richtigen "
      "Rufnummer zuzuordnen. Die Kontakte werden während der Laufzeit im "
      "Arbeitsspeicher gehalten und beim Beenden verworfen. <strong>Es wird keine "
      "Kopie des Adressbuchs angelegt.</strong>"),

    h(3, "Telefonie"),
    p("Die App wählt Rufnummern über den Telefonie-Dienst von Android. Sie führt "
      "<strong>kein Anrufprotokoll</strong> und liest das Anrufprotokoll des Systems "
      "nicht aus."),

    h(3, "Karteninformationen (SIM und eSIM)"),
    p("Bei Geräten mit mehreren Karten liest die App die Anzeigenamen der aktiven "
      "Karten, damit per Sprache gewählt werden kann, über welche telefoniert wird. "
      "Diese Angaben werden nicht gespeichert."),

    h(3, "Einstellungen"),
    p("Gespeichert werden ausschließlich die eigenen Einstellungen der App "
      "(Lautstärkestufe, Kontrastansicht, Autostart, Rückfrage vor dem Anruf) im "
      "privaten App-Speicher des Geräts."),

    h(2, "Berechtigungen und wofür sie gebraucht werden"),
    table([
        ("Mikrofon", "Sprachbefehle erkennen. Kernfunktion der App."),
        ("Kontakte lesen", "Gesprochenen Namen der Rufnummer zuordnen."),
        ("Telefonieren", "Den Anruf tatsächlich aufbauen."),
        ("Telefonstatus lesen", "Bei zwei Karten erkennen, welche zur Auswahl stehen."),
        ("Lautstärke ändern", "Die Ansagen beim Start auf eine hörbare Lautstärke setzen."),
        ("Benachrichtigungen", "Anzeigen, dass die Sprachsteuerung zuhört – für den Dauerbetrieb vorgeschrieben."),
        ("Beim Systemstart ausführen", "Die Sprachsteuerung nach einem Neustart wieder einschalten."),
        ("Akku-Optimierung ausnehmen", "Verhindern, dass Android den Dienst beendet und das Zuhören aufhört."),
    ]),
    p("Die App fordert <strong>keine</strong> Internetberechtigung an."),

    h(2, "Weitergabe an Dritte"),
    p("Findet nicht statt. Es gibt keine Empfänger, weil keine Daten das Gerät "
      "verlassen."),

    h(2, "Speicherdauer und Löschung"),
    p("Da nichts übertragen und nichts beim Anbieter gespeichert wird, entfällt eine "
      "Speicherfrist. Die auf dem Gerät gespeicherten Einstellungen werden mit der "
      "Deinstallation der App vollständig entfernt."),

    h(2, "Kinder"),
    p("Die App richtet sich nicht an Kinder und erhebt keine Daten über sie."),

    h(2, "Ihre Rechte"),
    p("Nach DSGVO stehen Ihnen Auskunft, Berichtigung, Löschung, Einschränkung, "
      "Datenübertragbarkeit und Widerspruch zu. Da der Anbieter keinerlei Daten über "
      "Sie erhält oder verarbeitet, laufen diese Rechte gegenüber dem Anbieter ins "
      "Leere – es gibt schlicht nichts, worüber Auskunft erteilt werden könnte. Für "
      'Fragen: <a href="mailto:info@naturlust.net">info@naturlust.net</a>'),

    h(2, "Nachprüfbar"),
    p("DialOS Mobil ist quelloffen unter der Apache-Lizenz 2.0. Wer wissen möchte, "
      "was die App tut, kann es nachlesen: "
      '<a href="https://github.com/Stephan-Lefty/DialOS-Mobil" rel="noopener" '
      'target="_blank">github.com/Stephan-Lefty/DialOS-Mobil</a>'),
]

content = "\n\n".join(blocks)

cfg = load_env()
auth = base64.b64encode(
    f"{cfg['WP_USER']}:{cfg['WP_APP_PASSWORD']}".encode()
).decode()


def call(method, route, payload=None):
    url = f"{cfg['WP_URL']}/wp-json/{route}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


# Gibt es die Seite schon? Dann aktualisieren statt doppelt anlegen.
existing = call("GET", f"wp/v2/pages?slug={SLUG}&status=any&context=edit")
payload = {
    "title": TITLE,
    "slug": SLUG,
    "content": content,
    "status": "publish",
}

if existing:
    page = call("POST", f"wp/v2/pages/{existing[0]['id']}", payload)
    print("aktualisiert:", page["link"])
else:
    page = call("POST", "wp/v2/pages", payload)
    print("angelegt:", page["link"])

print("Status:", page["status"], "| ID:", page["id"])
