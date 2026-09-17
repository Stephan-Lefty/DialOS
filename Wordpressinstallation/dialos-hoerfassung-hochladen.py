#!/usr/bin/env python3
"""Lädt eine Hörfassung in die Mediathek und setzt den Audio-Block in den Beitrag.

Der Block kommt direkt hinter den Sprachmarker, damit der Flaggen-Umschalter
den Marker weiterhin als erstes Element findet - und damit die Hörfassung das
erste ist, was jemand sieht, der sie sucht.

Aufruf:  ./dialos-hoerfassung-hochladen.py <beitrags-id> <mp3-datei>
"""
import base64
import json
import mimetypes
import os
import re
import sys
import urllib.request

BASIS = os.path.dirname(os.path.abspath(__file__))
BESCHRIFTUNG = ("Diesen Beitrag anhören – gesprochen von Anna, "
                "der Stimme von DialOS")


def umgebung():
    werte = {}
    with open(os.path.join(BASIS, ".env")) as f:
        for zeile in f:
            zeile = zeile.strip()
            if zeile and not zeile.startswith("#") and "=" in zeile:
                k, v = zeile.split("=", 1)
                werte[k.strip()] = v.strip().strip('"').strip("'")
    return werte


U = umgebung()
WP = U["WP_URL"].rstrip("/")
AUTH = base64.b64encode(
    f"{U['WP_USER']}:{U['WP_APP_PASSWORD']}".encode()).decode()


def req(pfad, methode="GET", nutzlast=None, kopf=None):
    r = urllib.request.Request(
        f"{WP}{pfad}", method=methode,
        data=json.dumps(nutzlast).encode() if nutzlast is not None else None)
    r.add_header("Authorization", f"Basic {AUTH}")
    if nutzlast is not None:
        r.add_header("Content-Type", "application/json")
    for k, v in (kopf or {}).items():
        r.add_header(k, v)
    return json.load(urllib.request.urlopen(r))


def hochladen(datei, titel):
    name = os.path.basename(datei)
    with open(datei, "rb") as f:
        rohdaten = f.read()
    r = urllib.request.Request(f"{WP}/wp-json/wp/v2/media", method="POST",
                               data=rohdaten)
    r.add_header("Authorization", f"Basic {AUTH}")
    r.add_header("Content-Disposition", f'attachment; filename="{name}"')
    r.add_header("Content-Type", mimetypes.guess_type(name)[0] or "audio/mpeg")
    medium = json.load(urllib.request.urlopen(r))
    # Titel und Alternativtext nachtragen - die Mediathek übernimmt sonst den
    # Dateinamen, und der taugt als Beschriftung nichts.
    req(f"/wp-json/wp/v2/media/{medium['id']}", "POST",
        {"title": titel, "caption": BESCHRIFTUNG})
    return medium


def block(medien_id, url):
    return (
        f'<!-- wp:audio {{"id":{medien_id}}} -->\n'
        f'<figure class="wp-block-audio"><audio controls src="{url}">'
        f'</audio><figcaption class="wp-element-caption">{BESCHRIFTUNG}'
        f'</figcaption></figure>\n'
        f'<!-- /wp:audio -->\n\n')


def main():
    beitrag_id = int(sys.argv[1])
    datei = sys.argv[2]

    b = req(f"/wp-json/wp/v2/posts/{beitrag_id}?context=edit"
            "&_fields=content,title,link")
    titel = re.sub(r"<[^>]+>", "", b["title"]["rendered"])
    inhalt = b["content"]["raw"]

    if "wp-block-audio" in inhalt:
        print("Der Beitrag hat bereits einen Audio-Block - nichts geändert.")
        return 0

    medium = hochladen(datei, f"Hörfassung: {titel}")
    url = medium["source_url"]
    print(f"Hochgeladen: {url}  (Medien-ID {medium['id']})")

    # Hinter den Sprachmarker setzen, sonst ganz nach oben.
    marker = re.search(
        r'<!-- wp:paragraph \{"className":"dialos-lang-marker"\} -->.*?'
        r'<!-- /wp:paragraph -->\n\n', inhalt, re.S)
    if marker:
        neu = inhalt[:marker.end()] + block(medium["id"], url) + inhalt[marker.end():]
    else:
        neu = block(medium["id"], url) + inhalt

    req(f"/wp-json/wp/v2/posts/{beitrag_id}", "POST", {"content": neu})
    kontrolle = req(f"/wp-json/wp/v2/posts/{beitrag_id}?context=edit"
                    "&_fields=content")["content"]["raw"]
    print(f"Block gesetzt: {'wp-block-audio' in kontrolle}")
    print(f"Beitrag: {b['link']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
