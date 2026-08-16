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

DE_PAGE_ID = 24   # https://dialos.org/status/
EN_PAGE_ID = 138  # https://dialos.org/en/idea/

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
    """Escape text for HTML, keeping `code` spans as <code>...</code>."""
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for p in parts:
        if p.startswith('`') and p.endswith('`'):
            out.append(f'<code>{html.escape(p[1:-1])}</code>')
        else:
            out.append(html.escape(p))
    return ''.join(out)


def render_version_block(entry):
    version = entry["heading"].split()[0]
    heading_html = md_inline_to_html(entry["heading"])
    block = (
        '<!-- wp:heading {"level":3} -->\n'
        f'<h3 class="wp-block-heading">{heading_html}</h3>\n'
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


def render_section(entries, heading_html, extra_intro=""):
    parts = [heading_html, ""]
    if extra_intro:
        parts.append(extra_intro.rstrip("\n"))
        parts.append("")
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
    cmd = ["curl", "-sS", "-u", f"{wp_user}:{wp_pass}", "-X", method]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    cmd.append(f"{wp_url}/wp-json/wp/v2/pages/{path}")
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
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

    de_section = render_section(
        de_entries,
        '<!-- wp:heading -->\n<h2 class="wp-block-heading">Änderungsprotokoll</h2>\n<!-- /wp:heading -->',
    )
    en_section = render_section(
        en_entries,
        '<!-- wp:heading -->\n<h2 class="wp-block-heading">Changelog</h2>\n<!-- /wp:heading -->',
        extra_intro=EN_CONDENSED_NOTE,
    )

    sync_page(DE_PAGE_ID, DE_PREAMBLE_MARKER, DE_POSTAMBLE, de_section, wp_url, wp_user, wp_pass, dry_run)
    sync_page(EN_PAGE_ID, EN_PREAMBLE_MARKER, EN_POSTAMBLE, en_section, wp_url, wp_user, wp_pass, dry_run)


if __name__ == "__main__":
    main()
