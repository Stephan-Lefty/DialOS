#!/usr/bin/env python3
"""Sync the changelog from README.md/README.en.md to the WordPress
"Idee"/"Idea" pages. Run manually: ./sync-changelog.py [--dry-run]

The README.md/README.en.md on GitHub (master branch, fetched directly via
raw.githubusercontent.com) is the ONE source of truth for the changelog -
never the local git clone, which can silently fall behind (happened once
already: 113 commits stale). This script only touches the
"## Änderungsprotokoll" / "## Changelog" section of each WordPress page -
everything above it (intro text, Status, Dokumentation, Logo & Branding,
Testumgebung) and the closing "Euer Stephan" / "Yours, Stephan" paragraph
are left untouched.

Photos shown next to individual changelog entries are WordPress-only
decoration, not part of the README - see IMAGE_MAP below. New versions
without an entry there are simply rendered as text, no photo.
"""

import json
import os
import re
import subprocess
import sys
import html
import urllib.request

RAW_BASE = "https://raw.githubusercontent.com/Stephan-Lefty/DialOS/master"

DE_PAGE_ID = 24   # https://dialos.org/status/  - Kurzfassung
EN_PAGE_ID = 138  # https://dialos.org/en/idea/ - Kurzfassung
DE_FULL_PAGE_ID = 644   # https://dialos.org/aenderungsprotokoll/ - vollstaendig
EN_FULL_PAGE_ID = 645   # https://dialos.org/en/changelog/        - vollstaendig

DE_FULL_URL = "https://dialos.org/aenderungsprotokoll/"
EN_FULL_URL = "https://dialos.org/en/changelog/"

# Hoechstens so viele geschaetzte Zeilen je Version auf der Kurzseite
# (Stephan, 2026-09-22: "Für jede Version auf der status Seite maximal
# 15 Zeilen").
#
# Zwischendurch stand hier eine feste Anzahl von zwei Punkten. Stephan
# hat beide Fassungen nebeneinander gesehen und sich fuer diese hier
# entschieden: Das Zeilenmass fuellt den Platz, der zur Verfuegung
# steht, statt ihn bei kurzen Punkten zu verschenken - 0.5.2 bringt so
# sieben Stichworte unter, die alten Versionen ihre ein bis zwei.
MAX_ZEILEN = 15

# Zeichen je Zeile fuer die Schaetzung. 45 ist die HANDY-Breite, am
# 2026-09-22 bei 356 px Sichtfeld gemessen - nicht die Desktop-Breite.
# Wer vom Desktop ausgeht (rund 95 Zeichen), bekommt am Handy die
# dreifache Hoehe, und genau dort ist die Beschwerde entstanden.
ZEICHEN_JE_ZEILE = 45

# Verweise auf Dateien im Repo (docs/..., TODO.md) zeigen auf der Website
# ins Leere. Sie gehen deshalb auf GitHub - das Repo ist oeffentlich.
REPO_BLOB = "https://github.com/Stephan-Lefty/DialOS/blob/master/"

# version -> photo already used on the live page for that entry.
IMAGE_MAP = {
    "0.4.0": {"id": 94, "file": "Dialos-Beispiele3-1024x683.png", "width": "431px", "ratio": "1.4992892477398079"},
    "0.3.0": {"id": 90, "file": "Dialos-Beispiele1-1024x683.png", "width": "426px", "ratio": "1.4992892477398079"},
    "0.2.0": {"id": 96, "file": "Dialos-Beispiele2-1-1024x683.png", "width": "431px", "ratio": "1.4992892477398079"},
}

EN_CONDENSED_NOTE = (
    '<!-- wp:paragraph -->\n'
    '<p><em>This is a condensed summary. The full, technically detailed '
    'changelog is available on the&nbsp;'
    '<a href="https://dialos.org/status/" target="_blank" rel="noreferrer noopener">German page</a>'
    '&nbsp;and in the&nbsp;'
    '<a href="https://github.com/Stephan-Lefty/DialOS" target="_blank" rel="noreferrer noopener">GitHub repository</a>.</em></p>\n'
    '<!-- /wp:paragraph -->\n\n'
)

# Regex, not exact string: the live headings sometimes carry a leftover
# empty anchor tag (<h2 ...>Änderungsprotokoll<a ...></a></h2>) from an
# earlier README import - match loosely so that doesn't break the split.
DE_PREAMBLE_MARKER = re.compile(
    r'<!-- wp:heading -->\n<h2 class="wp-block-heading">Änderungsprotokoll.*?</h2>\n<!-- /wp:heading -->',
    re.S,
)
DE_POSTAMBLE = '<!-- wp:paragraph -->\n<p><strong><em>Euer Stephan</em></strong></p>\n<!-- /wp:paragraph -->'

EN_PREAMBLE_MARKER = re.compile(
    r'<!-- wp:heading -->\n<h2 class="wp-block-heading">Changelog.*?</h2>\n<!-- /wp:heading -->',
    re.S,
)
EN_POSTAMBLE = '<!-- wp:paragraph -->\n<p><strong><em>Yours, Stephan</em></strong></p>\n<!-- /wp:paragraph -->'


def parse_changelog(md_text, section_heading):
    """Parse a '## <section_heading>' section of a README into
    a list of {"heading": "0.4.0 (12.08.2026)", "bullets": [...]}."""
    lines = md_text.splitlines()
    start = None
    for i, l in enumerate(lines):
        if l.strip() == f"## {section_heading}":
            start = i + 1
            break
    if start is None:
        raise ValueError(f"Section '## {section_heading}' not found")
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break

    entries = []
    current = None
    for line in lines[start:end]:
        stripped = line.strip()
        if stripped.startswith("### "):
            if current:
                entries.append(current)
            current = {"heading": stripped[4:].strip(), "bullets": []}
        elif current is not None:
            if stripped.startswith("- "):
                current["bullets"].append(stripped[2:])
            elif stripped and current["bullets"]:
                # wrapped continuation line of the previous bullet
                current["bullets"][-1] += " " + stripped
    if current:
        entries.append(current)
    return entries


def md_inline_to_html(text):
    """Escape text for HTML, keeping `code` spans as <code>...</code>
    and **bold** as <strong>...</strong>.

    Fettschrift kam am 2026-09-17 dazu. Bis dahin wandelte diese Funktion nur
    Code-Spannen um; die aelteren Changelog-Eintraege benutzten keine
    Fettschrift, deshalb fiel es nie auf. Im Abschnitt 0.5.2 stehen 76 Zeilen
    mit **...** - ohne diese Ergaenzung waeren die Sternchen woertlich auf der
    Seite gelandet. Gefunden im --dry-run, also bevor etwas veroeffentlicht
    wurde.

    WARUM MIT PLATZHALTERN und nicht einfach nacheinander: Fettschrift darf
    eine Code-Spanne UMSCHLIESSEN - im Quelltext steht zum Beispiel
    "**`dialos-aufspielen` zaehlt ein Manifest jetzt wie eine Aenderung**".
    Wer zuerst an den Backticks zerlegt, zerreisst dabei das Sternchen-Paar:
    Das oeffnende landet im einen Stueck, das schliessende im naechsten, und
    heraus kommt verschraenktes Markup. Deshalb werden die Code-Spannen durch
    Platzhalter ersetzt, dann wird der ganze Text in einem Stueck maskiert und
    fett gesetzt, und erst zum Schluss kommen die Code-Spannen zurueck.

    Die Platzhalter nutzen \x00, weil html.escape() das Zeichen nicht
    anfasst und es in einem Changelog nicht vorkommt.
    """
    spannen = []

    def merken(treffer):
        spannen.append(treffer.group(0)[1:-1])
        return f"\x00{len(spannen) - 1}\x00"

    if text.count('`') % 2:
        print(f"  WARNUNG: ungerade Zahl Backticks - {text[:80]}...",
              file=sys.stderr)
    if text.count('**') % 2:
        print(f"  WARNUNG: ungerade Zahl ** - {text[:80]}...", file=sys.stderr)

    mit_platzhaltern = re.sub(r'`[^`]+`', merken, text)
    ergebnis = html.escape(mit_platzhaltern)
    # re.DOTALL, weil Fettschrift im README ueber Zeilenumbrueche laeuft -
    # die Eintraege sind auf 79 Zeichen umbrochen, eine fette Ueberschrift
    # passt oft nicht in eine Zeile. Ohne DOTALL blieben genau diese
    # Sternchen stehen (2026-09-17 auf der englischen Idee-Seite gefunden).
    ergebnis = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', ergebnis,
                      flags=re.DOTALL)
    # Kursiv NUR fuer einzelne Woerter. Ein gieriges *...* waere hier
    # gefaehrlich: Im Protokoll stehen Dateinamen mit Platzhalter
    # ("suche-icon-light-*.png und suche-icon-dark-*.png"), und deren beide
    # Sternchen wuerden sonst zu einem Kursiv-Bereich zusammengezogen - aus
    # zwei Dateinamen wird ein halber. Deshalb: kein Leerzeichen, kein Punkt,
    # kein Schraegstrich im Inhalt. Gemessen am 2026-09-17: 26 von 27 Stellen
    # sind einzelne Woerter, der eine Rest ist genau dieses Dateinamen-Paar.
    ergebnis = re.sub(r'\*([^*\s/.]+)\*', r'<em>\1</em>', ergebnis)
    if '*' in ergebnis:
        print(f"  WARNUNG: einzelnes * bleibt stehen - {text[:80]}...",
              file=sys.stderr)

    # Links. Dazugekommen am 2026-09-22, und zwar aus demselben Grund wie
    # die Fettschrift am 2026-09-17: Diese Funktion kannte die Form nicht,
    # also landete sie WOERTLICH auf der Seite. Auf /status/ standen 17
    # Stueck, Besucher lasen dort
    # "[rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074)".
    # Aufgefallen ist es nur nebenbei, beim Suchen nach zu langen
    # Zeichenketten - genau diese Adressen machten die Seite auf dem Handy
    # breiter als den Bildschirm.
    #
    # Zwei Sorten Ziel, und sie brauchen verschiedene Behandlung:
    #   [Text](https://...)  -> echter Verweis, neues Fenster
    #   [Text](docs/foo.md)  -> ein PFAD IM REPO. Auf der Website gibt es
    #                           kein docs/, der Verweis liefe ins Leere.
    #                           Geht deshalb auf GitHub; das Repo ist
    #                           oeffentlich, also ist das Ziel echt.
    # Anker (#abschnitt) bleiben, wie sie sind - sie zeigen auf dieselbe
    # Seite. Die Maskierung ist vorher passiert, deshalb steht im Text an
    # dieser Stelle "&quot;" statt '"'; das Ziel wird trotzdem noch einmal
    # durch quote() geschickt, damit ein Anfuehrungszeichen im Pfad das
    # href nicht aufbrechen kann.
    def link(treffer):
        beschriftung, ziel = treffer.group(1), treffer.group(2)
        if ziel.startswith(("http://", "https://")):
            adresse = ziel
            extra = ' target="_blank" rel="noreferrer noopener"'
        elif ziel.startswith("#"):
            adresse = ziel
            extra = ''
        else:
            adresse = REPO_BLOB + ziel.lstrip("./")
            extra = ' target="_blank" rel="noreferrer noopener"'
        adresse = adresse.replace('"', "&quot;")
        return f'<a href="{adresse}"{extra}>{beschriftung}</a>'

    ergebnis = re.sub(r'\[([^\]\[]+)\]\(([^)\s]+)\)', link, ergebnis)
    if re.search(r'\[[^\]\[]+\]\(', ergebnis):
        print(f"  WARNUNG: Link bleibt stehen - {text[:80]}...",
              file=sys.stderr)

    for nummer, inhalt in enumerate(spannen):
        ergebnis = ergebnis.replace(f"\x00{nummer}\x00",
                                    f'<code>{html.escape(inhalt)}</code>')
    return ergebnis


def anker(version):
    """'0.5.2' -> 'v0-5-2' - taugt als HTML-Kennung und als Sprungziel."""
    return "v" + re.sub(r"[^0-9a-zA-Z]+", "-", version).strip("-")



def zeilen_schaetzen(text):
    """Wie viele Zeilen belegt dieser Stichpunkt auf einem Handy?

    Grob, aber in die richtige Richtung grob: Markup zaehlt nicht mit,
    der sichtbare Text schon. Mindestens eine Zeile, auch fuer drei
    Woerter.
    """
    sichtbar = html.unescape(re.sub(r"<[^>]+>", "", text))
    return max(1, -(-len(sichtbar) // ZEICHEN_JE_ZEILE))


def punkt_kuerzen(text):
    """Der eine Satz, der diesen Stichpunkt ausmacht.

    Gemessen am 2026-09-22: In 0.5.2, 0.5.1 und 0.5.0 beginnt so gut wie
    jeder Punkt mit einem fett gesetzten Kopf (53 von 53, 138 von 138,
    48 von 52), und der ist im Schnitt 57 bis 81 Zeichen lang, waehrend
    der ganze Punkt auf 939 bis 1318 kommt. Die Kurzfassung ist also
    laengst geschrieben - sie steht zwischen den Sternchen. Das Skript
    muss nichts zusammenfassen und behauptet damit auch nichts.

    Die alten Versionen (0.4.0 und aelter) kennen keine fetten Koepfe,
    haben dafuer aber kurze Punkte (Ø 260 bis 529 Zeichen). Dort tut es
    der erste Satz.
    """
    t = re.sub(r"\s+", " ", text).strip()
    if t.startswith("**"):
        ende = t.find("**", 2)
        if ende > 2:
            return t[2:ende].strip()
    m = re.match(r"(.+?[.!?])(?:\s|$)", t)
    return m.group(1) if m else t


def render_version_kurz(entry, ziel_url, mehr_text, alle_text):
    """Ein knapper Block je Version, mit Verweis auf die volle Liste.

    Die Punkte werden von oben genommen, solange das Zeilenmass reicht -
    KEINE selbst erfundene Zusammenfassung. Im Protokoll steht das
    Neueste oben, die Kurzfassung ist damit "was zuletzt passiert ist",
    und das ist eine Aussage, die auch stimmt. Eine automatisch
    gebastelte Zusammenfassung waere eine Behauptung ueber Wichtigkeit,
    die das Skript nicht treffen kann.

    Mindestens ein Punkt wird immer gezeigt, auch wenn er allein schon
    ueber dem Mass liegt - ein Block mit Ueberschrift und ohne Inhalt
    waere schlechter als einer, der etwas zu lang ist.
    """
    version = entry["heading"].split()[0]
    heading_html = md_inline_to_html(entry["heading"])
    ziel = f"{ziel_url}#{anker(version)}"

    block = (
        '<!-- wp:heading {"level":3} -->\n'
        f'<h3 class="wp-block-heading">'
        f'<a href="{ziel}">{heading_html}</a></h3>\n'
        '<!-- /wp:heading -->\n\n'
    )

    gewaehlt, zeilen = [], 0
    for b in entry["bullets"]:
        gerendert = md_inline_to_html(punkt_kuerzen(b))
        n = zeilen_schaetzen(gerendert)
        if gewaehlt and zeilen + n > MAX_ZEILEN:
            break
        gewaehlt.append(gerendert)
        zeilen += n

    items = "\n\n".join(
        f'<!-- wp:list-item -->\n<li>{g}</li>\n<!-- /wp:list-item -->'
        for g in gewaehlt
    )
    block += f'<!-- wp:list -->\n<ul class="wp-block-list">{items}</ul>\n<!-- /wp:list -->\n\n'

    block += (
        '<!-- wp:paragraph -->\n'
        f'<p><a href="{ziel}">{alle_text}</a></p>\n'
        '<!-- /wp:paragraph -->'
    )
    return block


def render_version_block(entry):
    version = entry["heading"].split()[0]
    heading_html = md_inline_to_html(entry["heading"])
    block = (
        '<!-- wp:heading {"level":3} -->\n'
        f'<h3 class="wp-block-heading" id="{anker(version)}">{heading_html}</h3>\n'
        '<!-- /wp:heading -->\n\n'
    )

    img = IMAGE_MAP.get(version)
    if img:
        block += (
            f'<!-- wp:image {{"id":{img["id"]},"width":"{img["width"]}","height":"auto",'
            f'"aspectRatio":"{img["ratio"]}","sizeSlug":"large","linkDestination":"none","align":"right"}} -->\n'
            f'<figure class="wp-block-image alignright size-large is-resized">'
            f'<img src="https://dialos.org/wp-content/uploads/2026/08/{img["file"]}" alt="" '
            f'class="wp-image-{img["id"]}" '
            f'style="aspect-ratio:{img["ratio"]};width:{img["width"]};height:auto"/></figure>\n'
            '<!-- /wp:image -->\n\n'
        )

    items = "\n\n".join(
        f'<!-- wp:list-item -->\n<li>{md_inline_to_html(b)}</li>\n<!-- /wp:list-item -->'
        for b in entry["bullets"]
    )
    block += f'<!-- wp:list -->\n<ul class="wp-block-list">{items}</ul>\n<!-- /wp:list -->'
    return block


def render_section(entries, heading_html, extra_intro="", kurz=None):
    """kurz = None -> volle Liste; sonst dict mit ziel/mehr/alle/hinweis."""
    parts = [heading_html, ""]
    if extra_intro:
        parts.append(extra_intro.rstrip("\n"))
        parts.append("")
    if kurz:
        parts.append(kurz["hinweis"].rstrip("\n"))
        parts.append("")
        parts.append("\n\n".join(
            render_version_kurz(e, kurz["ziel"], kurz["mehr"], kurz["alle"])
            for e in entries))
    else:
        parts.append("\n\n".join(render_version_block(e) for e in entries))
    return "\n".join(parts)


def fetch_readme(filename):
    """Fetch a README straight from GitHub - never the local clone."""
    url = f"{RAW_BASE}/{filename}"
    with urllib.request.urlopen(url, timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f"GitHub gab HTTP {r.status} für {url} zurück")
        return r.read().decode("utf-8")


def wp_api(method, path, wp_url, wp_user, wp_pass, body=None):
    """Ein Aufruf an die WordPress-Schnittstelle.

    Der Rumpf geht ueber die STANDARDEINGABE an curl (-d @-), nicht als
    Kommandozeilen-Argument. Am 2026-09-17 ist genau das gescheitert:
    "OSError: [Errno 7] Argument list too long". Das Aenderungsprotokoll war
    ueber die Laengengrenze des Betriebssystems fuer Argumente gewachsen
    (unter Linux rund 128 kB je Argument). Vorher lief es jahrelang, weil der
    Text kleiner war - ein Fehler, der mit dem Projekt mitwaechst und
    irgendwann zuschlaegt, ohne dass sich am Code etwas geaendert haette.
    """
    cmd = ["curl", "-sS", "-u", f"{wp_user}:{wp_pass}", "-X", method]
    eingabe = None
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", "@-"]
        eingabe = json.dumps(body)
    cmd.append(f"{wp_url}/wp-json/wp/v2/pages/{path}")
    r = subprocess.run(cmd, input=eingabe, capture_output=True, text=True,
                       check=True)
    return json.loads(r.stdout)


def sync_page(page_id, preamble_marker, postamble, new_section, wp_url, wp_user, wp_pass, dry_run):
    current = wp_api("GET", f"{page_id}?context=edit&_fields=content", wp_url, wp_user, wp_pass)
    content = current["content"]["raw"]

    m = preamble_marker.search(content)
    if not m:
        raise ValueError(f"Preamble marker not found in page {page_id} - page structure may have changed, aborting.")
    if postamble not in content:
        raise ValueError(f"Postamble not found in page {page_id} - page structure may have changed, aborting.")

    preamble = content[:m.start()]
    new_content = preamble + new_section + "\n\n" + postamble

    if dry_run:
        print(f"--- Vorschau Seite {page_id} (nicht gespeichert) ---")
        print(new_section[:2000])
        print("...\n")
        return

    result = wp_api("PUT", str(page_id), wp_url, wp_user, wp_pass, {"content": new_content})
    print(f"Seite {page_id}: {'OK' if 'id' in result else result}")


def main():
    dry_run = "--dry-run" in sys.argv

    wp_url = os.environ["WP_URL"]
    wp_user = os.environ["WP_USER"]
    wp_pass = os.environ["WP_APP_PASSWORD"]

    de_md = fetch_readme("README.md")
    en_md = fetch_readme("README.en.md")

    de_entries = parse_changelog(de_md, "Änderungsprotokoll")
    en_entries = parse_changelog(en_md, "Changelog")

    if not de_entries or not en_entries:
        print("Kein Änderungsprotokoll/Changelog in den READMEs gefunden - Abbruch.", file=sys.stderr)
        sys.exit(1)

    de_heading = '<!-- wp:heading -->\n<h2 class="wp-block-heading">Änderungsprotokoll</h2>\n<!-- /wp:heading -->'
    en_heading = '<!-- wp:heading -->\n<h2 class="wp-block-heading">Changelog</h2>\n<!-- /wp:heading -->'

    # Die beiden Kurzseiten. Der Hinweis steht bewusst UEBER den Bloecken:
    # Wer hier landet, soll sofort wissen, dass er eine Auswahl sieht.
    de_kurz = render_section(
        de_entries, de_heading,
        kurz={
            "ziel": DE_FULL_URL,
            "hinweis": (
                '<!-- wp:paragraph -->\n'
                '<p><em>Je Version das Neueste in Kürze. Die Versionsnummer '
                f'führt zur vollständigen Liste im <a href="{DE_FULL_URL}">'
                'Änderungsprotokoll</a>.</em></p>\n'
                '<!-- /wp:paragraph -->'
            ),
            "mehr": "Und {anzahl} weitere Änderungen in dieser Version",
            "alle": "Alle Änderungen",
        },
    )
    en_kurz = render_section(
        en_entries, en_heading, extra_intro=EN_CONDENSED_NOTE,
        kurz={
            "ziel": EN_FULL_URL,
            "hinweis": (
                '<!-- wp:paragraph -->\n'
                '<p><em>The most recent items per release. The version number '
                f'leads to the full list in the <a href="{EN_FULL_URL}">'
                'changelog</a>.</em></p>\n'
                '<!-- /wp:paragraph -->'
            ),
            "mehr": "And {anzahl} more changes in this release",
            "alle": "All changes",
        },
    )

    # Die beiden vollstaendigen Seiten - unveraendert das, was bisher auf
    # /status/ und /en/idea/ stand.
    de_voll = render_section(de_entries, de_heading)
    en_voll = render_section(en_entries, en_heading)

    sync_page(DE_PAGE_ID, DE_PREAMBLE_MARKER, DE_POSTAMBLE, de_kurz, wp_url, wp_user, wp_pass, dry_run)
    sync_page(EN_PAGE_ID, EN_PREAMBLE_MARKER, EN_POSTAMBLE, en_kurz, wp_url, wp_user, wp_pass, dry_run)
    sync_page(DE_FULL_PAGE_ID, DE_PREAMBLE_MARKER, DE_POSTAMBLE, de_voll, wp_url, wp_user, wp_pass, dry_run)
    sync_page(EN_FULL_PAGE_ID, EN_PREAMBLE_MARKER, EN_POSTAMBLE, en_voll, wp_url, wp_user, wp_pass, dry_run)


if __name__ == "__main__":
    main()
