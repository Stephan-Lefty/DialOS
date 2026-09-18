#!/usr/bin/env python3
"""Screenshots und Anmeldeformular fuer den Test von DialOS Mobil.

  1. Die vier App-Screenshots in die Mediathek laden.
  2. Ein Contact-Form-7-Formular "DialOS Mobil - Testteilnahme" anlegen,
     das an kontakt@dialos.org zustellt.  <- das ist die Quelle der
     Wahrheit fuer dieses Formular, Aenderungen hier vornehmen.
  3. (abgeschaltet) Frueher: eine eigene Anmeldeseite /dialos-mobil-testen/.

ACHTUNG, Stand 20.08.2026: Schritt 3 ist AUS. Die Anmeldeseite ist auf
Stephans Wunsch entfallen, weil das Formular jetzt direkt in den beiden
Blog-Beitraegen steckt - eine Seite, die dasselbe noch einmal sagt, braucht
es dann nicht. Die alte Seite (id 204) liegt im Papierkorb. Wer sie wieder
will, setzt SEITE_ANLEGEN auf True; ansonsten stehen die Texte in
dialos-mobil-neuigkeit.py.

Bestehende Seiten und Formulare werden NICHT angefasst - insbesondere
nicht /datenschutzerklaerung/ (id 3) und nicht "Kontaktformular 1" (id 49).
"""
import base64
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path("/mnt/raid/eigene Daten/GitHub/Stephan-Lefty")
ENV = BASE / "DialOS/Wordpressinstallation/.env"
SHOTS = BASE / "DialOS-Mobil/screenshots"

SEITE_ANLEGEN = False  # siehe Kopf dieser Datei
PAGE_SLUG = "dialos-mobil-testen"
PAGE_TITLE = "DialOS Mobil testen – Testerinnen und Tester gesucht"
FORM_TITLE = "DialOS Mobil – Testteilnahme"
EMPFAENGER = "kontakt@dialos.org"

# Datei, Alternativtext (wird vorgelesen - deshalb beschreibend, nicht "Screenshot 1")
BILDER = [
    ("01_startseite_aus.png",
     "Startbildschirm von DialOS Mobil: ein sehr großer blauer Knopf mit der "
     "Aufschrift „Sprachsteuerung einschalten“ füllt die halbe Bildschirmhöhe.",
     "Ein einziger großer Knopf – mehr braucht die Startseite nicht."),
    ("02_startseite_hoert_zu.png",
     "Derselbe Bildschirm im eingeschalteten Zustand: Der Knopf ist rot und "
     "beschriftet mit „Sprachsteuerung ausschalten“, darüber steht, dass die "
     "App zuhört.",
     "Eingeschaltet: Die App hört auf das Aktivierungswort."),
    ("04_kontrastansicht.png",
     "Die kontraststarke Ansicht: schwarzer Hintergrund, leuchtend gelbe "
     "Schaltflächen und weiße Schrift.",
     "Kontraststarke Ansicht, auf Knopfdruck umschaltbar."),
    ("03_infos_einstellungen.png",
     "Die Seite „Infos & Einstellungen“ mit erklärenden Abschnitten zu "
     "Berechtigungen, Dauerbetrieb und Bedienung.",
     "Infos & Einstellungen – erklärt jede Berechtigung im Klartext."),
]


def load_env():
    cfg = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


cfg = load_env()
AUTH = base64.b64encode(
    f"{cfg['WP_USER']}:{cfg['WP_APP_PASSWORD']}".encode()
).decode()
WP = cfg["WP_URL"]


def call(method, route, payload=None):
    url = f"{WP}/wp-json/{route}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"FEHLER {e.code} bei {method} {route}:\n{e.read().decode()}",
              file=sys.stderr)
        raise


def upload(path: Path, alt: str):
    """Laedt ein Bild hoch - oder gibt das schon vorhandene zurueck."""
    slug = path.stem.replace("_", "-")
    vorhanden = call("GET", f"wp/v2/media?slug={slug}&context=edit")
    if vorhanden:
        print(f"  vorhanden: {path.name} -> id {vorhanden[0]['id']}")
        return vorhanden[0]

    body = path.read_bytes()
    req = urllib.request.Request(f"{WP}/wp-json/wp/v2/media", data=body,
                                 method="POST")
    req.add_header("Authorization", f"Basic {AUTH}")
    req.add_header("Content-Type", mimetypes.guess_type(path.name)[0])
    req.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
    with urllib.request.urlopen(req, timeout=180) as r:
        media = json.loads(r.read().decode())
    # Alternativtext nachtragen - beim Upload nimmt WordPress ihn nicht an.
    media = call("POST", f"wp/v2/media/{media['id']}",
                 {"alt_text": alt, "slug": slug})
    print(f"  hochgeladen: {path.name} -> id {media['id']}")
    return media


# ---------------------------------------------------------------------------
# Bausteine fuer den Gutenberg-Inhalt
# ---------------------------------------------------------------------------
def h(level, text):
    attrs = f' {{"level":{level}}}' if level != 2 else ""
    return ("<!-- wp:heading" + attrs + " -->\n"
            + f'<h{level} class="wp-block-heading">{text}</h{level}>\n'
            + "<!-- /wp:heading -->")


def p(text):
    return f"<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->"


def liste(punkte):
    items = "".join(
        f"<!-- wp:list-item -->\n<li>{x}</li>\n<!-- /wp:list-item -->"
        for x in punkte
    )
    return ('<!-- wp:list -->\n<ul class="wp-block-list">'
            + items + "</ul>\n<!-- /wp:list -->")


def tabelle(kopf, zeilen):
    kopfzeile = "".join(f"<th>{c}</th>" for c in kopf)
    body = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in z) + "</tr>" for z in zeilen
    )
    return ('<!-- wp:table -->\n<figure class="wp-block-table"><table>'
            f"<thead><tr>{kopfzeile}</tr></thead><tbody>{body}</tbody>"
            "</table></figure>\n<!-- /wp:table -->")


def hinweis(text):
    """Farbig abgesetzter Kasten fuer das Wichtigste."""
    return ('<!-- wp:group {"style":{"border":{"left":{"color":"#1a73e8",'
            '"width":"4px"}},"spacing":{"padding":{"left":"1rem",'
            '"top":"0.5rem","bottom":"0.5rem"}}}} -->\n'
            '<div class="wp-block-group" style="border-left-color:#1a73e8;'
            'border-left-width:4px;padding-top:0.5rem;padding-left:1rem;'
            'padding-bottom:0.5rem">'
            + p(text) +
            "</div>\n<!-- /wp:group -->")


def galerie(medien):
    bilder = []
    for media, beschriftung in medien:
        voll = media["source_url"]
        bilder.append(
            f'<!-- wp:image {{"id":{media["id"]},"sizeSlug":"large",'
            '"linkDestination":"media"} -->\n'
            '<figure class="wp-block-image size-large">'
            f'<a href="{voll}"><img src="{voll}" alt="{media["alt_text"]}" '
            f'class="wp-image-{media["id"]}"/></a>'
            f'<figcaption class="wp-element-caption">{beschriftung}</figcaption>'
            "</figure>\n<!-- /wp:image -->"
        )
    return ('<!-- wp:gallery {"columns":4,"linkTo":"media"} -->\n'
            '<figure class="wp-block-gallery has-nested-images columns-4 '
            'is-cropped wp-block-gallery-is-layout-flex">'
            + "".join(bilder) +
            "</figure>\n<!-- /wp:gallery -->")


# ---------------------------------------------------------------------------
# 1. Screenshots
# ---------------------------------------------------------------------------
print("Screenshots:")
medien = []
for datei, alt, beschriftung in BILDER:
    pfad = SHOTS / datei
    if not pfad.is_file():
        sys.exit(f"Screenshot fehlt: {pfad}")
    medien.append((upload(pfad, alt), beschriftung))

# ---------------------------------------------------------------------------
# 2. Formular
# ---------------------------------------------------------------------------
# Keine eigene Ueberschrift im Formular: Die steht schon als <h2> auf der
# Seite. Doppelt bedeutet fuer einen Screenreader denselben Satz zweimal.
FORMULAR = """<label> Name
    [text* teilnehmer-name autocomplete:name] </label>

<label> Mailadresse (die des Google-Kontos auf dem Handy)
    [email* teilnehmer-email autocomplete:email] </label>

[honeypot hp-heimatstadt]

[submit "Senden"]"""

# Zum Honeypot (Plugin "CF7 Apps", 20.08.2026 eingebaut): Er erzeugt ein
# Feld mit zufaelligem Namen, dazu ein Zeit-Token gegen Sekundenschnelles
# Absenden. Wichtig fuer diese Zielgruppe: Das Feld wird per CSS-clip
# versteckt, nicht per display:none - ein Screenreader liest es also samt
# Label "Bitte lasse dieses Feld leer." vor. Genau so soll es sein. Wuerde
# es vor dem Screenreader verborgen, wuerde ein blinder Nutzer es womoeglich
# ausfuellen und seine Anmeldung waere lautlos verworfen.
# Falls der Honeypot je ersetzt wird: dieses Verhalten nachpruefen.

MAIL_TEXT = """Neue Anmeldung zum Test von DialOS Mobil.

Name: [teilnehmer-name]
Mailadresse: [teilnehmer-email]

Diese Adresse muss in der Google Play Console unter
Geschlossener Test > Tester in die E-Mail-Liste eingetragen werden.

--
Gesendet vom Formular auf [_url]"""

# Kein Versprechen einer schnellen Rueckmeldung (Stephan, 20.08.2026): Er
# meldet sich erst, wenn alle Tester beisammen sind - nicht sofort nach der
# Anmeldung. Der Text sagt das ausdruecklich, damit niemand wartet oder
# nachfragt.
BESTAETIGUNG = """Hallo [teilnehmer-name],

danke fuer deine Anmeldung zum Test von DialOS Mobil!

Ich melde mich wieder, sobald alle Testerinnen und Tester zusammen sind.
Google verlangt mindestens 12 Personen, und erst wenn die vollstaendig
sind, trage ich alle Adressen in der Play Console ein und schicke euch
gemeinsam den Link zur Installation.

Wie lange das dauert, haengt davon ab, wie schnell sich genug Leute
finden - das koennen durchaus einige Wochen sein. Bis dahin ist fuer dich
nichts zu tun, und du musst auch nicht nachfragen. Du hoerst von mir.

Viele Gruesse
Stephan Roesner, DialOS
[_site_url]"""

# ACHTUNG, zwei Fallen im REST-Zugang von Contact Form 7 (geprueft an 6.1.7):
#
#   1. Ohne "?context=save" speichert der Endpunkt NICHT. Er antwortet
#      trotzdem mit HTTP 200 und einem vollstaendig aussehenden Formular -
#      nur mit "id": null. Das sieht wie ein Erfolg aus und ist keiner.
#   2. Beim Schreiben gehoeren form/mail/mail_2/messages auf die OBERSTE
#      Ebene, nicht unter "properties" - obwohl das Lesen sie genau dort
#      zurueckgibt. Unter "properties" werden sie stillschweigend verworfen,
#      und man bekommt die Standardvorlage unter eigenem Titel.
#
# Beides zusammen hat am 20.08.2026 dazu gefuehrt, dass die Seite mit
# id="None" im Shortcode veroeffentlicht wurde -> "Kontaktformular wurde
# nicht gefunden". Deshalb unten die Pruefung auf eine echte ID.
eigenschaften = {
    "form": FORMULAR,
    "mail": {
        "active": True,
        "subject": "[DialOS Mobil] Testanmeldung von [teilnehmer-name]",
        "sender": "DialOS <kontakt@dialos.org>",
        "recipient": EMPFAENGER,
        "body": MAIL_TEXT,
        "additional_headers": "Reply-To: [teilnehmer-email]",
        "attachments": "",
        "use_html": False,
        "exclude_blank": False,
    },
    "mail_2": {
        "active": True,
        "subject": "Deine Anmeldung zum Test von DialOS Mobil",
        "sender": "DialOS <kontakt@dialos.org>",
        "recipient": "[teilnehmer-email]",
        "body": BESTAETIGUNG,
        "additional_headers": f"Reply-To: {EMPFAENGER}",
        "attachments": "",
        "use_html": False,
        "exclude_blank": False,
    },
    "messages": {
        "mail_sent_ok": "Danke! Deine Anmeldung ist angekommen. Eine "
                        "Bestätigung geht dir gerade per E-Mail zu.",
        "mail_sent_ng": "Das Absenden hat leider nicht geklappt. Bitte "
                        "schreib uns direkt an kontakt@dialos.org.",
        "validation_error": "Bitte fülle beide Felder aus.",
        "invalid_required": "Bitte fülle dieses Feld aus.",
        "invalid_email": "Bitte gib eine gültige E-Mail-Adresse ein.",
    },
}

print("Formular:")
formulare = call("GET", "contact-form-7/v1/contact-forms")
treffer = [f for f in formulare if f["title"] == FORM_TITLE]
nutzlast = {"title": FORM_TITLE, "locale": "de_DE", **eigenschaften}

if treffer:
    formular_id = treffer[0]["id"]
    call("POST", f"contact-form-7/v1/contact-forms/{formular_id}?context=save",
         nutzlast)
    print(f"  aktualisiert: id {formular_id}")
else:
    angelegt = call("POST", "contact-form-7/v1/contact-forms?context=save",
                    nutzlast)
    formular_id = angelegt.get("id")
    if not formular_id:
        sys.exit("Contact Form 7 hat kein Formular angelegt (id ist null). "
                 "Ohne Formular waere der Shortcode auf der Seite kaputt - "
                 "Abbruch, bevor etwas veroeffentlicht wird.")
    # Beim Anlegen uebernimmt CF7 nur Titel und Sprache. Der eigentliche
    # Inhalt muss in einem zweiten Aufruf hinterher.
    call("POST", f"contact-form-7/v1/contact-forms/{formular_id}?context=save",
         nutzlast)
    print(f"  angelegt: id {formular_id}")

# Der Hash steht nur in der Liste, nicht in der Einzelabfrage.
formular = [f for f in call("GET", "contact-form-7/v1/contact-forms")
            if f["id"] == formular_id][0]

# Gegenprobe: Steht wirklich unser Feld drin, oder die CF7-Standardvorlage?
gespeichert = call("GET", f"contact-form-7/v1/contact-forms/{formular_id}")
if "teilnehmer-email" not in gespeichert["properties"]["form"]["content"]:
    sys.exit("Das Formular enthaelt nicht die erwarteten Felder - CF7 hat die "
             "Vorlage behalten. Abbruch, bevor die Seite darauf verweist.")

kuerzel = f'[contact-form-7 id="{formular["hash"]}" title="{FORM_TITLE}"]'

# ---------------------------------------------------------------------------
# 3. Die Seite
# ---------------------------------------------------------------------------
GITHUB = ('<a href="https://github.com/Stephan-Lefty/DialOS-Mobil" '
          'rel="noopener" target="_blank">github.com/Stephan-Lefty/DialOS-Mobil</a>')
DATENSCHUTZ = ('<a href="https://dialos.org/dialos-mobil-datenschutz/">'
               "Datenschutzerklärung für DialOS Mobil</a>")

bloecke = [
    p("<strong>DialOS Mobil ist ein Telefon für Menschen, die ein Telefon "
      "nicht bedienen können.</strong> Wer blind ist oder die Hände nicht "
      "ruhig genug führt, scheitert am Touchscreen – nicht am Telefonieren. "
      "Man sagt, wen man anrufen möchte, und die App ruft an. Die "
      "Spracherkennung läuft dabei vollständig auf dem Gerät; die App hat "
      "nicht einmal eine Internetberechtigung."),

    p("Die App ist fertig und läuft. Bevor sie in den Play Store darf, "
      "verlangt Google einen <strong>geschlossenen Test mit mindestens "
      "12 Personen über 14 Tage</strong>. Genau dafür suchen wir dich."),

    h(2, "So sieht sie aus"),
    galerie(medien),

    h(2, "So läuft ein Anruf"),
    tabelle(["Wer", "Was gesagt wird"], [
        ("Du", "„Sprachsteuerung starten“"),
        ("App", "„Sprachsteuerung bereit. Wen möchten Sie anrufen?“"),
        ("Du", "„Max Mustermann anrufen“"),
        ("App", "„Soll ich Max Mustermann auf Mobil anrufen? Sagen Sie Ja oder Nein.“"),
        ("Du", "„Ja“"),
        ("App", "„Ich rufe Max Mustermann an.“"),
    ]),
    p("Der Bildschirm bleibt dabei unberührt."),

    h(2, "Was du zum Mitmachen brauchst"),
    tabelle(["Voraussetzung", "Warum"], [
        ("Ein Android-Handy ab Android 8",
         "Ältere Fassungen unterstützt die App nicht."),
        ("Eine SIM-Karte im Gerät",
         "Ohne Telefonie kann die App nichts tun. WLAN-Tablets fallen deshalb "
         "aus – Google bietet die App dort gar nicht erst an."),
        ("Ein Google-Konto",
         "Der Test läuft über den Play Store. Wichtig: Es muss genau die "
         "Adresse sein, mit der auf dem Handy der Play Store angemeldet ist. "
         "Sonst taucht die App dort nie auf."),
        ("Deutsch",
         "Die Sprachbedienung gibt es bislang nur auf Deutsch."),
        ("14 Tage Geduld",
         "Google zählt die tatsächliche Nutzung, nicht die Anmeldung. Die App "
         "sollte die zwei Wochen über installiert bleiben und ab und zu "
         "benutzt werden."),
        ("Rund 50 MB",
         "So groß ist der Download – das deutsche Sprachmodell steckt mit "
         "drin, damit nichts nachgeladen werden muss."),
    ]),

    h(2, "Drei Dinge, die wir vorher gesagt haben wollen"),
    liste([
        "<strong>Die App hört dauerhaft zu</strong> – sonst könnte sie auf "
        "das Aktivierungswort nicht reagieren. Das kostet spürbar Akku. "
        "Gehört wird ausschließlich auf dem Gerät, aufgezeichnet wird nichts.",
        "<strong>DialOS Mobil ersetzt keinen Notruf.</strong> Ein Notruf darf "
        "nie von einer Spracherkennung abhängen. Dafür bleibt die eingebaute "
        "Notruffunktion des Telefons zuständig.",
        "<strong>Im Play Store heißt die App zunächst „org.dialos.mobil "
        "(unreviewed)“</strong> statt „DialOS Mobil“ – nicht erschrecken. "
        "Google zeigt bis zur ersten Prüfung nur den technischen Namen an.",
    ]),

    h(2, "Worauf wir besonders achten"),
    p("Wenn du eine einzige Sache zurückmeldest, dann bitte diese: "
      "<strong>Wie zuverlässig springt das Aktivierungswort „Sprachsteuerung "
      "starten“ bei dir an?</strong> Das ist der Punkt, den wir bisher nur "
      "mit einer einzigen Stimme geprüft haben – und eine Sprachsteuerung, "
      "die nicht anspringt, ist wertlos. Alles andere ist willkommen, aber "
      "das ist die Frage, auf die es ankommt."),

    h(2, "Was mit deinen Daten passiert"),
    p("Ehrlich gesagt: Deine E-Mail-Adresse müssen wir an Google "
      "weitergeben. Anders funktioniert ein geschlossener Test im Play Store "
      "nicht – die Testerliste liegt in der Google Play Console. Name und "
      "Adresse aus dem Formular gehen per E-Mail an "
      f"<a href=\"mailto:{EMPFAENGER}\">{EMPFAENGER}</a>, werden "
      "ausschließlich für diesen Test verwendet und nach dessen Ende "
      "gelöscht. Ein Widerruf per formloser E-Mail genügt jederzeit."),
    p("<strong>Die App selbst sendet nach wie vor nichts.</strong> Das gilt "
      "auch in der Testfassung: keine Internetberechtigung, keine "
      "Absturzberichte, keine Auswertung. Nachzulesen in der "
      f"{DATENSCHUTZ} – und im Quelltext, denn DialOS Mobil ist quelloffen "
      f"unter der Apache-Lizenz 2.0: {GITHUB}"),

    h(2, "Ich will an dem Test teilnehmen!"),
    p("Zwei Felder, mehr brauche ich nicht. Ich melde mich, sobald alle "
      "Testerinnen und Tester zusammen sind &#8211; vorher passiert nichts. "
      "Das kann einige Wochen dauern; du musst nicht nachfragen."),
    f"<!-- wp:shortcode -->\n{kuerzel}\n<!-- /wp:shortcode -->",
]

inhalt = "\n\n".join(bloecke)

if not SEITE_ANLEGEN:
    print(f"\nFertig. Formular-ID: {formular_id} | Shortcode: {kuerzel}")
    print("Die Anmeldeseite wird nicht mehr angelegt - das Formular steht in "
          "den Beitraegen (siehe dialos-mobil-neuigkeit.py).")
    raise SystemExit

print("Seite:")
vorhanden = call("GET", f"wp/v2/pages?slug={PAGE_SLUG}&status=any&context=edit")
nutzlast = {
    "title": PAGE_TITLE,
    "slug": PAGE_SLUG,
    "content": inhalt,
    "status": "publish",
    "excerpt": "Für die Freigabe im Play Store braucht DialOS Mobil 12 "
               "Testerinnen und Tester über 14 Tage. Hier steht, was dazu "
               "nötig ist – und hier kann man sich anmelden.",
}
if vorhanden:
    seite = call("POST", f"wp/v2/pages/{vorhanden[0]['id']}", nutzlast)
    print(f"  aktualisiert: {seite['link']}")
else:
    seite = call("POST", "wp/v2/pages", nutzlast)
    print(f"  angelegt: {seite['link']}")

print(f"\nFertig. Status: {seite['status']} | Seiten-ID: {seite['id']} "
      f"| Formular-ID: {formular['id']}")
print(f"Adresse: {seite['link']}")
