#!/usr/bin/env python3
"""Stellt die Kommentarfunktion auf dialos.org sprachweise ein.

Entscheidung vom 20.08.2026: Deutsche Beitraege behalten Kommentare,
englische bekommen keine. Dieses Skript setzt das im Datenbestand um:

  1. Bei allen englischen Beitraegen comment_status und ping_status
     auf "closed".
  2. Alle Selbst-Pingbacks in den Papierkorb (die Beitraege verlinken
     gegenseitig aufeinander, daraus macht WordPress automatisch
     Kommentare, die unter dem Text wie echte Wortmeldungen aussehen).

Englisch erkannt wird ueber die Konvention der Website: Jede englische
Fassung verlinkt oben auf die deutsche, Linktext genau "Deutsch".

Das Plugin wp-plugin/dialos-kommentare sorgt zusaetzlich dafuer, dass das
auch fuer kuenftige Beitraege ohne Zutun gilt - und dass unter den
deutschen Beitraegen die drei englischen Theme-Texte deutsch erscheinen.
Dieses Skript hier ist der einmalige Aufraeumteil; das Plugin ist die
Dauerloesung. Beides ist beliebig oft wiederholbar.
"""
import base64
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV = Path("/mnt/raid/eigene Daten/GitHub/Stephan-Lefty/DialOS/"
           "Wordpressinstallation/.env")

# Sprachumschalter am Kopf eines englischen Beitrags: <a href="...">Deutsch</a>
ENGLISCH = re.compile(r'<a\s[^>]*href="[^"]*"[^>]*>\s*Deutsch\s*</a>', re.I)


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
        print(f"  FEHLER {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return None


print("Beitraege durchsehen:")
beitraege = call("GET", "wp/v2/posts?per_page=100&status=any&context=edit") or []

for b in beitraege:
    ist_en = bool(ENGLISCH.search(b["content"]["raw"]))
    titel = b["title"]["raw"][:48]

    if not ist_en:
        print(f"  {b['id']:>4} deutsch   Kommentare bleiben offen   {titel}")
        continue

    if b["comment_status"] == "closed" and b["ping_status"] == "closed":
        print(f"  {b['id']:>4} englisch  schon geschlossen          {titel}")
        continue

    r = call("POST", f"wp/v2/posts/{b['id']}",
             {"comment_status": "closed", "ping_status": "closed"})
    if r:
        print(f"  {b['id']:>4} englisch  geschlossen                {titel}")

print("\nSelbst-Pingbacks:")
eigene = WP.rstrip("/")
zu_loeschen = []

for typ in ("pingback", "trackback"):
    for c in call("GET", f"wp/v2/comments?type={typ}&status=any"
                         "&per_page=100&context=edit") or []:
        if c.get("author_url", "").startswith(eigene):
            zu_loeschen.append(c)

if not zu_loeschen:
    print("  keine gefunden")

for c in zu_loeschen:
    # Ohne force=true landet der Kommentar im Papierkorb, nicht im Nichts.
    r = call("DELETE", f"wp/v2/comments/{c['id']}")
    zustand = (r or {}).get("status", "?")
    print(f"  id {c['id']} auf Beitrag {c['post']} -> {zustand} "
          f"({c['author_name'][:40]})")

print("\nFertig. Zum Gegenpruefen die beiden Beitraege im Browser oeffnen:")
print("  https://dialos.org/dialos-mobil-tester-gesucht/   (deutsch, "
      "Kommentare an)")
print("  https://dialos.org/dialos-mobil-testers-wanted/   (englisch, "
      "kein Kommentarbereich)")
