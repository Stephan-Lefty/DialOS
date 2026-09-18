#!/usr/bin/env python3
"""Veroeffentlicht den Testeraufruf als Neuigkeit auf dialos.org.

Legt drei Dinge an bzw. aktualisiert sie (mehrfach ausfuehrbar):

  1. deutscher Beitrag  /dialos-mobil-tester-gesucht/
  2. englischer Beitrag /dialos-mobil-testers-wanted/
  3. Eintraege ganz oben in beiden Spalten der Seite /neuigkeiten/ (id 184)

Konventionen aus den bestehenden Beitraegen 185/186 uebernommen:
  - Erster Absatz ist der Sprachumschalter auf die jeweils andere Fassung.
  - Der englische Beitrag blendet die deutsche Meta-Zeile des Themes per
    CSS aus (auf seine eigene postid begrenzt) und setzt eine englische
    daneben. Deshalb wird er zweimal geschrieben: erst anlegen, um die ID
    zu erfahren, dann mit eingesetzter ID nachziehen.
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV = Path("/mnt/raid/eigene Daten/GitHub/Stephan-Lefty/DialOS/"
           "Wordpressinstallation/.env")

NEUIGKEITEN_ID = 184
DATENSCHUTZ = "https://dialos.org/dialos-mobil-datenschutz/"
REPO = "https://github.com/Stephan-Lefty/DialOS-Mobil"

SLUG_DE = "dialos-mobil-tester-gesucht"
SLUG_EN = "dialos-mobil-testers-wanted"
URL_DE = f"https://dialos.org/{SLUG_DE}/"
URL_EN = f"https://dialos.org/{SLUG_EN}/"

TITEL_DE = "DialOS Mobil sucht Testerinnen und Tester"
TITEL_EN = "DialOS Mobil is looking for testers"

DATUM_DE = "20. August 2026"
DATUM_EN = "20 August 2026"

# Bereits in der Mediathek (von dialos-mobil-tester-gesucht.py hochgeladen)
BILD_ID = 200
BILD_URL = ("https://dialos.org/wp-content/uploads/2026/08/"
            "01_startseite_aus-scaled.png")

# Dasselbe Formular wie auf /dialos-mobil-testen/ (CF7 id 205). Es direkt in
# den Beitrag zu setzen spart den Umweg ueber die Anmeldeseite - wer bis
# hierher gelesen hat, hat sich entschieden und soll nicht noch klicken
# muessen. CF7 kommt mit demselben Formular auf mehreren Seiten zurecht.
FORMULAR_KUERZEL = ('[contact-form-7 id="b923396" '
                    'title="DialOS Mobil – Testteilnahme"]')


def formular():
    return f"<!-- wp:shortcode -->\n{FORMULAR_KUERZEL}\n<!-- /wp:shortcode -->"


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
    f"{cfg['WP_USER']}:{cfg['WP_APP_PASSWORD']}".encode()).decode()
WP = cfg["WP_URL"]


def call(method, route, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{WP}/wp-json/{route}", data=data,
                                 method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"FEHLER {e.code} bei {method} {route}:\n{e.read().decode()}",
              file=sys.stderr)
        raise


def p(text):
    return f"<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->"


def h(level, text):
    attrs = f' {{"level":{level}}}' if level != 2 else ""
    return ("<!-- wp:heading" + attrs + " -->\n"
            + f'<h{level} class="wp-block-heading">{text}</h{level}>\n'
            + "<!-- /wp:heading -->")


def liste(punkte):
    items = "".join(f"<!-- wp:list-item -->\n<li>{x}</li>\n<!-- /wp:list-item -->"
                    for x in punkte)
    return ('<!-- wp:list -->\n<ul class="wp-block-list">' + items
            + "</ul>\n<!-- /wp:list -->")


def bild(alt, beschriftung):
    return (f'<!-- wp:image {{"id":{BILD_ID},"sizeSlug":"large",'
            '"linkDestination":"none","align":"center","width":"320px"} -->\n'
            '<figure class="wp-block-image aligncenter size-large '
            'is-resized">'
            f'<img src="{BILD_URL}" alt="{alt}" class="wp-image-{BILD_ID}" '
            'style="width:320px"/>'
            f'<figcaption class="wp-element-caption">{beschriftung}</figcaption>'
            "</figure>\n<!-- /wp:image -->")


def meta_en(post_id):
    """Englische Meta-Zeile; blendet die deutsche des Themes aus."""
    return ("<!-- wp:html -->\n<style>\n"
            f"body.postid-{post_id} p.meta {{ display: none; }}\n"
            "</style>\n"
            '<p class="meta"><i class="fa fa-clock-o"></i> '
            f"{DATUM_EN}\t\t\t\t\t\t"
            '<i class="fa fa-thumb-tack"></i> <strong>\t'
            '<a href="https://dialos.org/category/allgemein/" '
            'rel="category tag">Allgemein</a></strong></p>\n'
            "<!-- /wp:html -->")


# ---------------------------------------------------------------------------
# Deutscher Beitrag
# ---------------------------------------------------------------------------
INHALT_DE = "\n\n".join([
    p(f'<a href="{URL_EN}">English</a>'),

    p("<em>DialOS Mobil ist fertig und lässt sich bedienen. Bevor die App "
      "in den Play Store darf, verlangt Google einen geschlossenen Test mit "
      "mindestens zwölf Personen über vierzehn Tage. Genau die suche "
      "ich.</em>"),

    bild("Startbildschirm von DialOS Mobil: ein sehr großer blauer Knopf mit "
         "der Aufschrift „Sprachsteuerung einschalten“ füllt die halbe "
         "Bildschirmhöhe.",
         "Der ganze Startbildschirm. Mehr braucht er nicht."),

    h(2, "Worum es geht"),
    p("<strong>DialOS Mobil ist ein Telefon für Menschen, die ein Telefon "
      "nicht bedienen können.</strong> Wer blind ist oder die Hände nicht "
      "ruhig genug führt, scheitert am Touchscreen &#8211; nicht am "
      "Telefonieren. Die App dreht das um: Man sagt, wen man anrufen "
      "möchte, und sie ruft an. Kein Tippen, kein Zielen, kein Hinsehen."),

    p("Die Spracherkennung läuft <strong>vollständig auf dem Gerät</strong>. "
      "Die App hat nicht einmal eine Internetberechtigung &#8211; sie kann "
      "technisch gar nichts versenden. Deshalb funktioniert sie auch im "
      "Funkloch, im Keller und im Flugmodus. Sie ist der Handy-Ableger von "
      "DialOS, dem vollständig sprachgesteuerten Computer-System für "
      "dieselbe Zielgruppe."),

    h(2, "Warum es Tester braucht"),
    p("Google lässt neue Apps nicht ohne Weiteres in den Play Store. Für "
      "Konten wie meines gilt: erst ein <strong>geschlossener Test mit "
      "mindestens zwölf Personen über vierzehn Tage</strong>, dann die "
      "Freigabe. Gezählt wird die tatsächliche Nutzung, nicht die "
      "Anmeldung. Ohne diese zwölf Menschen bleibt die App liegen, so "
      "fertig sie auch ist."),

    h(2, "Was du dafür brauchst"),
    liste([
        "Ein <strong>Android-Handy ab Android 8</strong> &#8211; mit "
        "SIM-Karte. Ohne Telefonie kann die App nichts tun; WLAN-Tablets "
        "fallen deshalb aus.",
        "Ein <strong>Google-Konto</strong>, und zwar genau das, mit dem auf "
        "dem Handy der Play Store angemeldet ist.",
        "Die Bereitschaft, die App <strong>zwei Wochen</strong> installiert "
        "zu lassen und ab und zu zu benutzen.",
        "Rund <strong>50 MB</strong> Speicher &#8211; das deutsche "
        "Sprachmodell steckt mit in der App, damit nichts nachgeladen "
        "werden muss.",
    ]),

    h(2, "Die eine Frage, auf die es ankommt"),
    p("Wenn du nur eine einzige Sache zurückmeldest, dann bitte diese: "
      "<strong>Springt das Aktivierungswort „Sprachsteuerung starten“ bei "
      "deiner Stimme zuverlässig an?</strong> Bisher ist das nur mit einer "
      "einzigen Stimme geprüft &#8211; meiner. Und eine Sprachsteuerung, "
      "die nicht anspringt, ist wertlos. Alles andere ist willkommen, aber "
      "das ist der Punkt, an dem die App steht oder fällt."),

    h(2, "Was mit deinen Daten passiert"),
    p("Ehrlich gesagt: Deine E-Mail-Adresse muss ich an Google weitergeben. "
      "Anders funktioniert ein geschlossener Test im Play Store nicht "
      "&#8211; die Testerliste liegt in der Google Play Console. Name und "
      "Adresse werden ausschließlich für diesen Test verwendet und danach "
      "gelöscht."),
    p("<strong>Die App selbst sendet nach wie vor nichts</strong>, auch "
      "nicht in der Testfassung: keine Internetberechtigung, keine "
      "Absturzberichte, keine Auswertung. Nachzulesen in der "
      f'<a href="{DATENSCHUTZ}">Datenschutzerklärung</a> &#8211; und im '
      "Quelltext, denn DialOS Mobil ist quelloffen unter der Apache-Lizenz "
      f'2.0: <a href="{REPO}" target="_blank" rel="noreferrer noopener">'
      "github.com/Stephan-Lefty/DialOS-Mobil</a>"),

    h(2, "Ich will an dem Test teilnehmen!"),
    p("Zwei Felder, mehr brauche ich nicht. Ich melde mich, sobald alle "
      "Testerinnen und Tester zusammen sind &#8211; vorher passiert nichts. "
      "Das kann einige Wochen dauern; du musst nicht nachfragen."),
    formular(),
    # Der Datenschutzlink steht bewusst DIREKT AM FORMULAR, nicht nur weiter
    # oben im Text: Genau hier gibt jemand seine Daten her, und genau hier
    # will er nachlesen koennen, was damit geschieht.
    p(f'<em>Vorher nachlesen: <a href="{DATENSCHUTZ}">Datenschutzerklärung '
      "für DialOS Mobil</a> &#8211; die App sendet nichts, und dort steht "
      "im Einzelnen, warum sie es technisch gar nicht kann.</em>"),
])

# ---------------------------------------------------------------------------
# Englischer Beitrag
# ---------------------------------------------------------------------------
def inhalt_en(post_id):
    return "\n\n".join([
        meta_en(post_id),

        p(f'<a href="{URL_DE}">Deutsch</a>'),

        p("<em>DialOS Mobil is finished and works. Before it can go on the "
          "Play Store, Google requires a closed test with at least twelve "
          "people over fourteen days. Those are the people I am looking "
          "for.</em>"),

        # Der Hinweis steht bewusst GANZ OBEN und nicht am Ende: Wer kein
        # Deutsch spricht, soll das erfahren, bevor er sich anmeldet.
        p('<strong>Please note: the app’s voice control is German '
          "only.</strong> Every spoken command and every spoken reply is in "
          "German, and the offline speech model shipped with the app is a "
          "German one. You will only be able to test this app if you speak "
          "German. Other languages are planned, but none exist today "
          "&#8211; and testing a language you do not speak would tell "
          "neither of us anything."),

        bild("Home screen of DialOS Mobil: one very large blue button "
             "labelled „Sprachsteuerung einschalten“ fills half "
             "the screen height.",
             "The entire home screen. It needs nothing more."),

        h(2, "What it is"),
        p("<strong>DialOS Mobil is a phone for people who cannot operate a "
          "phone.</strong> If you are blind, or your hands do not hold "
          "steady, a touchscreen defeats you &#8211; not the phone call. "
          "This app turns that around: you say who you want to call, and it "
          "calls them. No typing, no aiming, no looking."),

        p("Speech recognition runs <strong>entirely on the device</strong>. "
          "The app does not even hold the internet permission &#8211; it is "
          "technically incapable of sending anything anywhere. That is also "
          "why it works with no signal, in a basement, and in flight mode. "
          "It is the phone companion to DialOS, a fully voice-operated "
          "computer system for the same people."),

        h(2, "Why testers are needed"),
        p("Google does not simply let new apps onto the Play Store. For "
          "accounts like mine the rule is: first a <strong>closed test with "
          "at least twelve people over fourteen days</strong>, then "
          "release. What counts is actual use, not sign-up. Without those "
          "twelve people the app sits still, however finished it is."),

        h(2, "What you need"),
        liste([
            "<strong>German.</strong> The voice interface exists in no other "
            "language yet.",
            "An <strong>Android phone running Android 8 or newer</strong> "
            "&#8211; with a SIM card. Without telephony the app can do "
            "nothing, so Wi-Fi-only tablets are out.",
            "A <strong>Google account</strong> &#8211; specifically the one "
            "the Play Store on that phone is signed in with.",
            "The willingness to leave the app installed for <strong>two "
            "weeks</strong> and use it now and then.",
            "About <strong>50 MB</strong> of storage &#8211; the German "
            "speech model ships inside the app so that nothing has to be "
            "downloaded later.",
        ]),

        h(2, "The one question that matters"),
        p("If you report back on a single thing, let it be this: "
          "<strong>does the wake phrase „Sprachsteuerung starten“ "
          "reliably trigger for your voice?</strong> So far it has been "
          "tested with exactly one voice &#8211; mine. And voice control "
          "that does not wake up is worthless. Everything else is welcome, "
          "but this is where the app stands or falls."),

        h(2, "What happens to your data"),
        p("Plainly: your e-mail address has to be passed on to Google. A "
          "closed test on the Play Store does not work any other way "
          "&#8211; the tester list lives in the Google Play Console. Your "
          "name and address are used for this test only and deleted "
          "afterwards."),
        p("<strong>The app itself still sends nothing</strong>, not even in "
          "the test build: no internet permission, no crash reports, no "
          "analytics. It is written down in the "
          f'<a href="{DATENSCHUTZ}">privacy policy</a> (German only, like '
          "every legal page on this site) &#8211; and readable "
          "in the source, because DialOS Mobil is open source under the "
          f'Apache License 2.0: <a href="{REPO}" target="_blank" '
          'rel="noreferrer noopener">github.com/Stephan-Lefty/'
          "DialOS-Mobil</a>"),

        h(2, "Ich will an dem Test teilnehmen! (sign up)"),
        p("Two fields, that is all I need. <em>The form is in German</em> "
          "&#8211; which, if you are eligible to test, will not be a "
          "problem. „Name“ is your name, „Mailadresse“ your e-mail address. "
          "I will get in touch once all testers are together; nothing "
          "happens before that, and there is no need to follow up."),
        formular(),
        p("<em>Worth reading first: the "
          f'<a href="{DATENSCHUTZ}">privacy policy for DialOS Mobil</a> '
          "&#8211; German only. The short version: the app sends nothing, "
          "and that page sets out why it is technically unable to.</em>"),
    ])


# ---------------------------------------------------------------------------
def schreibe_beitrag(slug, titel, inhalt, auszug, kommentare="open"):
    """kommentare: "open" fuer deutsche, "closed" fuer englische Beitraege.

    Entscheidung vom 20.08.2026: Die Website laeuft auf de_DE, also kaemen
    unter einem englischen Beitrag alle WordPress-Texte auf Deutsch heraus
    ("Schreibe einen Kommentar", "Antworten", "sagt:", deutsches Datum).
    Statt das aufwendig umzustellen, gibt es dort gar keine Kommentare.
    """
    vorhanden = call("GET", f"wp/v2/posts?slug={slug}&status=any&context=edit")
    nutzlast = {"title": titel, "slug": slug, "content": inhalt,
                "excerpt": auszug, "status": "publish", "categories": [1],
                "comment_status": kommentare, "ping_status": kommentare}
    if vorhanden:
        beitrag = call("POST", f"wp/v2/posts/{vorhanden[0]['id']}", nutzlast)
        print(f"  aktualisiert: {beitrag['link']}")
    else:
        beitrag = call("POST", "wp/v2/posts", nutzlast)
        print(f"  angelegt: {beitrag['link']}")
    return beitrag


print("Deutscher Beitrag:")
de = schreibe_beitrag(
    SLUG_DE, TITEL_DE, INHALT_DE,
    "Bevor DialOS Mobil in den Play Store darf, verlangt Google einen Test "
    "mit zwölf Personen über vierzehn Tage. Wer mitmachen möchte, braucht "
    "ein Android-Handy mit SIM-Karte und zwei Wochen Geduld.")

print("Englischer Beitrag:")
# Erst anlegen (ohne Meta-Zeile), um die ID zu bekommen ...
en = schreibe_beitrag(
    SLUG_EN, TITEL_EN, inhalt_en(0),
    "Before DialOS Mobil can go on the Play Store, Google requires a test "
    "with twelve people over fourteen days. Testers need an Android phone "
    "with a SIM card, two weeks of patience &#8211; and German.",
    kommentare="closed")
# ... dann mit eingesetzter ID nachziehen, damit das CSS greift.
en = call("POST", f"wp/v2/posts/{en['id']}", {"content": inhalt_en(en["id"])})
print(f"  Meta-Zeile auf postid-{en['id']} gesetzt")

# ---------------------------------------------------------------------------
# Eintraege auf /neuigkeiten/
# ---------------------------------------------------------------------------
print("Seite Neuigkeiten:")
seite = call("GET", f"wp/v2/pages/{NEUIGKEITEN_ID}?context=edit")
inhalt = seite["content"]["raw"]


def eintrag(url, titel, datum, text):
    return ("<!-- wp:heading {\"level\":3} -->\n"
            f'<h3><a href="{url}">{titel}</a></h3>\n<!-- /wp:heading -->\n\n'
            f"<!-- wp:paragraph -->\n<p><em>{datum}</em> — {text}</p>\n"
            "<!-- /wp:paragraph -->")


spalten = [
    ("<!-- wp:heading -->\n<h2>Deutsch</h2>\n<!-- /wp:heading -->",
     eintrag(URL_DE, TITEL_DE, DATUM_DE,
             "Zwölf Menschen mit einem Android-Handy, vierzehn Tage &#8211; "
             "so viel verlangt Google, bevor die App in den Play Store darf.")),
    ("<!-- wp:heading -->\n<h2>English</h2>\n<!-- /wp:heading -->",
     eintrag(URL_EN, TITEL_EN, DATUM_EN,
             "Twelve people with an Android phone, fourteen days &#8211; "
             "that is what Google asks before the app may go on the Play "
             "Store. German speakers only.")),
]

for ueberschrift, neuer in spalten:
    if ueberschrift not in inhalt:
        sys.exit(f"Spaltenueberschrift nicht gefunden:\n{ueberschrift}\n"
                 "Seite /neuigkeiten/ wurde offenbar umgebaut - Abbruch, "
                 "damit nichts zerschossen wird.")
    if neuer.split("\n")[1] in inhalt:
        print("  Eintrag steht schon drin, uebersprungen.")
        continue
    # Neueste Neuigkeit oben: direkt hinter die Spaltenueberschrift.
    inhalt = inhalt.replace(ueberschrift, ueberschrift + "\n\n" + neuer, 1)

call("POST", f"wp/v2/pages/{NEUIGKEITEN_ID}", {"content": inhalt})
print(f"  aktualisiert: https://dialos.org/neuigkeiten/")

print(f"\nFertig.\n  DE: {URL_DE}\n  EN: {URL_EN}\n"
      f"  Übersicht: https://dialos.org/neuigkeiten/")
