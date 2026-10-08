#!/usr/bin/env python3
"""
dialos_rhythmbox_sender.py - die Arbeit hinter DialOS-Rhythmbox.

Radiosender aus Deutschland, Oesterreich und der Schweiz holen, pruefen und
als Medienliste, Wiedergabeliste oder Rhythmbox-Eintrag ausgeben.

Quelle ist radio-browser.info, dieselbe Datenbank, die auch Shortwave nutzt.

Beispiele:
    dialos_rhythmbox_sender.py pruefen                 Alle Sender antesten
    dialos_rhythmbox_sender.py pls ~/Musik             .pls-Dateien schreiben
    dialos_rhythmbox_sender.py rhythmbox               In Rhythmbox eintragen
    dialos_rhythmbox_sender.py liste --land AT         Nur oesterreichische Sender zeigen

Voraussetzungen: python3, curl. Fuer die gruendliche Pruefung: ffprobe (ffmpeg).
"""

import argparse
import concurrent.futures as futures
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- Senderwahl

# Anzeigename -> regulaerer Ausdruck auf den Namen in der Datenbank,
# wahlweise mit einem dritten Eintrag: einem Muster, das in der Stream-
# Adresse vorkommen muss.
#
# Warum das dritte Feld noetig ist: Bei der SRG heissen deutsche,
# franzoesische und italienische Fassung in der Datenbank teilweise gleich
# ("Radio Swiss Classic"). Ohne Pruefung der Adresse landete am 2026-09-25
# die italienische Fassung (rsc_it) in der Liste - aufgefallen ist das nur,
# weil der Stream selbst sich als "Swiss Classic I" meldete.
#
# Wer eigene Sender will: hier ergaenzen, Name genau wie in radio-browser.info.
SENDER = {
    "Deutschland": [
        ("Deutschlandfunk",             r"^deutschlandfunk \| dlf \| mp3"),
        ("Deutschlandfunk Kultur",      r"^deutschlandfunk kultur \| dlf \| mp3"),
        ("Deutschlandfunk Nova",        r"^deutschlandfunk nova.*mp3"),
        ("1LIVE",                       r"^1live$"),
        ("WDR 2",                       r"^wdr 2 rheinland$"),
        ("WDR 3",                       r"^wdr 3$"),
        ("WDR 4",                       r"^wdr ?4$"),
        ("WDR 5",                       r"^wdr 5$"),
        ("NDR 2",                       r"^ndr 2$"),
        ("NDR Info",                    r"^ndr info \(hamburg\)$"),
        ("NDR Kultur",                  r"^ndr kultur$"),
        ("N-JOY",                       r"^n-joy$"),
        ("Bayern 1",                    r"^bayern 1 oberbayern$"),
        ("Bayern 2",                    r"^bayern 2$"),
        ("Bayern 3",                    r"^bayern 3$"),
        ("BR-Klassik",                  r"^br.?klassik$"),
        ("BR24",                        r"^br24$"),
        ("hr3",                         r"^hr3$"),
        ("hr-iNFO",                     r"^hr.?info$"),
        ("SWR1 Baden-Wuerttemberg",     r"^swr1 bw$"),
        ("SWR3",                        r"^swr3$"),
        ("SWR Kultur",                  r"^swr kultur$|^swr2$"),
        ("MDR Aktuell",                 r"^mdr aktuell$"),
        ("MDR Jump",                    r"^mdr jump$"),
        ("MDR Kultur",                  r"^mdr kultur$"),
        ("MDR Sputnik",                 r"^mdr sputnik$"),
        ("radioeins",                   r"^radio ?eins$"),
        ("Inforadio",                   r"^inforadio$"),
        ("Fritz",                       r"^fritz$"),
        ("Antenne Bayern",              r"^antenne bayern$"),
        ("Rock Antenne",                r"^rock antenne$"),
        ("Oldie Antenne",               r"^oldie antenne$"),
        ("Radio BOB!",                  r"^radio bob!$"),
        ("bigFM",                       r"^bigfm deutschland$"),
        ("Hit Radio FFH",               r"^hit radio ffh$"),
        ("sunshine live",               r"^sunshine live$"),
        ("Klassik Radio",               r"^klassik radio - live$"),
        ("80s80s",                      r"^80s80s$"),
    ],
    "Oesterreich": [
        ("Oe1",                         r"^ö1 \| orf \| hq$"),
        ("Hitradio Oe3",                r"^orf hitradio ö3 \| hq$"),
        ("FM4",                         r"^fm4 \| orf \| hq$"),
        ("ORF Radio Wien",              r"^orf radio wien \| hq$"),
        ("ORF Radio Niederoesterreich", r"^orf radio niederösterreich \| hq$"),
        ("ORF Radio Oberoesterreich",   r"^orf radio oberösterreich \| hq$"),
        ("ORF Radio Steiermark",        r"^orf radio steiermark \| hq$"),
        ("ORF Radio Tirol",             r"^orf tirol hq$"),
        ("ORF Radio Salzburg",          r"^orf radio salzburg hq$"),
        ("ORF Radio Kaernten",          r"^orf radio kärnten$"),
        ("ORF Radio Vorarlberg",        r"^radio vorarlberg hq$"),
        ("ORF Radio Burgenland",        r"^orf radio burgenland"),
        ("Kronehit",                    r"^kronehit$"),
        ("Radio 88.6",                  r"^radio 88\.6$"),
        ("Antenne Steiermark",          r"^antenne steiermark$"),
        ("Antenne Kaernten",            r"^antenne kärnten$"),
        ("Energy Oesterreich",          r"^energy österreich$"),
        ("Life Radio",                  r"^life radio$"),
        ("Rock Antenne Oesterreich",    r"^rock antenne österreich$"),
        ("Radio Arabella Austropop",    r"^arabella austropop$"),
        ("LoungeFM",                    r"^lounge\.fm - 100% austria$"),
    ],
    "Schweiz": [
        ("SRF 1",                       r"^srf 1$", r"drs1|srf1"),
        ("SRF 2 Kultur",                r"^srf 2$", r"drs2|srf2"),
        ("SRF 3",                       r"^srf 3$", r"drs3|srf3"),
        ("SRF 4 News",                  r"^srf 4 news$", r"drs4news|srf4news"),
        ("SRF Musikwelle",              r"^(radio )?srf musikwelle$"),
        ("SRF Virus",                   r"^(radio )?srf virus$"),
        ("Radio Swiss Pop",             r"^radio swiss pop$", r"rsp"),
        ("Radio Swiss Jazz",            r"^radio swiss jazz$", r"rsj"),
        ("Radio Swiss Classic",         r"^radio swiss classic( german)?$", r"rsc_de"),
        ("RTS La Premiere",             r"^rts la première$", r"la-1ere|la1ere"),
        ("RTS Couleur 3",               r"^rts couleur 3$", r"couleur3|couleur-3"),
        ("Radio 24",                    r"^radio ?24$"),
        ("Radio Argovia",               r"^radio argovia$"),
        ("Radio Pilatus",               r"^radio pilatus$"),
        ("Radio FM1",                   r"^radio fm1$"),
        ("Energy Zuerich",              r"^energy zürich \(nrj\)$"),
        ("Energy Bern",                 r"^energy bern$"),
        ("Vintage Radio",               r"^vintage ?radio(\.ch)?$"),
        ("Virgin Radio Switzerland",    r"^virgin radio switzerland$"),
    ],
}

LAENDER = {"Deutschland": "DE", "Oesterreich": "AT", "Schweiz": "CH"}
KUERZEL = {v: k for k, v in LAENDER.items()}


# --------------------------------------------------------- Feste Ersatzadressen
#
# Normalfall ist, dass beste_adresse() die dauerhafte Adresse aus den zwei
# Feldern der Datenbank waehlt. Das geht aber nur, solange EINES der beiden
# frei ist. Steht in beiden schon die aufgeloeste Adresse mit Sitzungskennung,
# ist der Eintrag in der Datenbank selbst kaputt - dann hilft nur eine von
# Hand nachgesehene Adresse.
#
# Hier gehoert nur hinein, was wirklich geprueft wurde: Adresse aufrufen,
# ICY-Namen mit dem erwarteten Sender vergleichen. Eine geratene Adresse ist
# schlimmer als gar keine, weil sie den Fehler unsichtbar macht.
#
# Angewendet wird der Ersatz NUR, wenn die Datenbankadresse tatsaechlich an
# einer Sitzung haengt. Repariert radio-browser.info den Eintrag, greift
# wieder die Datenbank - und der Ersatz faellt still aus dem Weg, statt eine
# irgendwann veraltete Adresse festzuschreiben.
ERSATZ_ADRESSEN = {
    # Geprueft 2026-09-25 und 2026-09-30: meldet sich als "SWR2 AAC 96".
    # In der Datenbank tragen bei diesem Sender BEIDE Felder ein "sid".
    # Diese Adresse ist der dauerhafte Einstieg; dass die ARD-Verteilung
    # beim Aufloesen sid/token anhaengt, ist richtig so - gespeichert wird
    # der Einstieg, genau wie bei radioeins.
    "SWR Kultur": "https://liveradio.swr.de/sw331ch/swr2/play.mp3",
}


# ------------------------------------------------- Bundeslaender und Kantone
#
# Das Feld "state" in der Datenbank wird von Hand gepflegt und ist
# entsprechend uneinheitlich: Am 2026-09-25 standen dort allein fuer
# Deutschland 53 Schreibweisen mit mindestens vier Sendern - "Bayern"
# neben "Bavaria", "NRW" neben "North Rhine-Westphalia" neben
# "north rhine westphalia". Wer nur nach einer Schreibweise sucht,
# uebersieht den groesseren Teil.
#
# Deshalb steht hier je Bundesland, wonach wirklich gefragt werden muss.
# Die Liste stammt nicht aus dem Kopf, sondern aus der Abfrage
# /json/states/<Land>/ - ergaenzt um die naheliegenden Schreibweisen,
# die heute (noch) keiner benutzt.

BUNDESLAENDER = {
    "Deutschland": {
        "Baden-Württemberg": ["Baden-Württemberg", "Baden-Wuerttemberg",
                              "Baden-Wurttemberg", "Baden Württemberg", "BW"],
        "Bayern": ["Bayern", "Bavaria", "BY"],
        "Berlin": ["Berlin", "Berlin-Brandenburg"],
        "Brandenburg": ["Brandenburg"],
        "Bremen": ["Bremen"],
        "Hamburg": ["Hamburg"],
        "Hessen": ["Hessen", "Hesse", "HE"],
        "Mecklenburg-Vorpommern": ["Mecklenburg-Vorpommern",
                                   "Mecklenburg-Western Pomerania", "MV"],
        "Niedersachsen": ["Niedersachsen", "Lower Saxony", "NDS"],
        "Nordrhein-Westfalen": ["Nordrhein-Westfalen", "North Rhine-Westphalia",
                                "NRW", "north-rhine-westphalia",
                                "north rhine westphalia", "Deutschland und NRW"],
        "Rheinland-Pfalz": ["Rheinland-Pfalz", "Rhineland-Palatinate", "RLP"],
        "Saarland": ["Saarland"],
        "Sachsen": ["Sachsen", "Saxony"],
        "Sachsen-Anhalt": ["Sachsen-Anhalt", "Saxony-Anhalt"],
        "Schleswig-Holstein": ["Schleswig-Holstein", "SH"],
        "Thüringen": ["Thüringen", "Thuringia", "Thueringen"],
    },
    "Oesterreich": {
        "Burgenland": ["Burgenland"],
        "Kärnten": ["Kärnten", "Carinthia", "Kaernten"],
        "Niederösterreich": ["Niederösterreich", "Lower Austria",
                             "Niederoesterreich"],
        "Oberösterreich": ["Oberösterreich", "Upper Austria", "Oberoesterreich"],
        "Salzburg": ["Salzburg"],
        "Steiermark": ["Steiermark", "Styria"],
        "Tirol": ["Tirol", "Tyrol"],
        "Vorarlberg": ["Vorarlberg"],
        "Wien": ["Wien", "Vienna"],
    },
    "Schweiz": {
        "Aargau": ["Aargau", "Argovia"],
        "Appenzell": ["Appenzell", "Appenzell Ausserrhoden",
                      "Appenzell Innerrhoden"],
        "Basel": ["Basel", "Basel-Stadt", "Basel-Landschaft", "Basle"],
        "Bern": ["Bern", "Kanton Bern", "Berne"],
        "Freiburg": ["Freiburg", "Fribourg"],
        "Genf": ["Genf", "Geneva", "Genève", "Geneve"],
        "Glarus": ["Glarus"],
        "Graubünden": ["Graubünden", "Grisons", "Graubuenden"],
        "Jura": ["Jura"],
        "Luzern": ["Luzern", "Lucerne"],
        "Neuenburg": ["Neuenburg", "Neuchatel", "Neuchâtel"],
        "Schaffhausen": ["Schaffhausen"],
        "Schwyz": ["Schwyz"],
        "Solothurn": ["Solothurn"],
        "St. Gallen": ["St. Gallen", "Sankt Gallen", "Saint Gallen", "St.Gallen"],
        "Tessin": ["Tessin", "Ticino"],
        "Thurgau": ["Thurgau"],
        "Unterwalden": ["Obwalden", "Nidwalden"],
        "Uri": ["Uri"],
        "Waadt": ["Waadt", "Vaud"],
        "Wallis": ["Wallis", "Valais"],
        "Zug": ["Zug"],
        "Zürich": ["Zürich", "Zurich", "Zuerich"],
        # Keine Kantone, aber in der Datenbank gepflegt und fuer die
        # Westschweiz die ergiebigste Angabe ueberhaupt (40 Sender).
        "Westschweiz (Romandie)": ["Suisse Romande", "Romandie"],
    },
}


#: Grosse Staedte je Land - als Startpunkt fuer die Stadtsuche. Die
#: Datenbank kennt kein Stadtfeld; gesucht wird deshalb im Sendernamen,
#: in den Schlagwoertern und im Feld "state" (das bei Stadtstaaten wie
#: Berlin oder Hamburg die Stadt enthaelt). Siehe stadt_suchen().
STAEDTE = {
    "Deutschland": ["Berlin", "Hamburg", "München", "Köln", "Frankfurt",
                    "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen",
                    "Bremen", "Dresden", "Hannover", "Nürnberg", "Duisburg",
                    "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster",
                    "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden", "Kiel",
                    "Mainz", "Magdeburg", "Freiburg", "Rostock", "Saarbrücken"],
    "Oesterreich": ["Wien", "Graz", "Linz", "Salzburg", "Innsbruck",
                    "Klagenfurt", "Villach", "Wels", "St. Pölten", "Dornbirn",
                    "Bregenz", "Steyr", "Feldkirch", "Seefeld"],
    "Schweiz": ["Zürich", "Genf", "Basel", "Bern", "Lausanne", "Winterthur",
                "Luzern", "St. Gallen", "Lugano", "Biel", "Thun", "Chur",
                "Schaffhausen", "Freiburg", "Neuenburg", "Sitten"],
}


#: Genres mit den Schlagwoertern, unter denen sie wirklich gepflegt sind.
#: Auch hier gilt die Synonym-Falle: "80s" und "80er" sind dasselbe, aber
#: zwei verschiedene Eintraege in der Datenbank.
GENRES = {
    "Nachrichten und Wort": ["news", "nachrichten", "talk", "information",
                             "public radio", "spoken word", "info"],
    "Pop und Charts": ["pop", "charts", "top 40", "hits", "pop music"],
    "Rock": ["rock", "classic rock", "alternative", "indie", "metal",
             "hard rock"],
    "Oldies und Schlager": ["oldies", "schlager", "volksmusik", "60s", "70s",
                            "evergreens"],
    "Achtziger und Neunziger": ["80s", "80er", "90s", "90er", "eighties",
                                "nineties"],
    "Klassik": ["classical", "klassik", "classic", "opera", "barock"],
    "Jazz und Blues": ["jazz", "blues", "swing", "soul"],
    "Elektronisch und Dance": ["electronic", "dance", "techno", "house",
                               "trance", "deep house", "edm"],
    "Ruhig und Lounge": ["chillout", "lounge", "ambient", "relax",
                         "easy listening"],
    "Country und Folk": ["country", "folk", "americana"],
    "Volksmusik und Heimat": ["volksmusik", "heimat", "blasmusik",
                              "volkstuemlich"],
    "Kirche und Glaube": ["christian", "gospel", "kirche", "religion"],
}

# Server von radio-browser.info. Der erste, der antwortet, wird genommen.
SERVER = [
    "https://de1.api.radio-browser.info",
    "https://at1.api.radio-browser.info",
    "https://nl1.api.radio-browser.info",
    "https://all.api.radio-browser.info",
]

KOPF = {"User-Agent": "DialOS-Rhythmbox/1.0"}


# ---------------------------------------------------------------- Hilfsmittel

def sagen(text=""):
    print(text, flush=True)


def fehler(text):
    print(f"Fehler: {text}", file=sys.stderr, flush=True)


def hole(pfad, versuche_server=None):
    """Eine Abfrage an radio-browser.info, mit Ausweichservern."""
    letzter = None
    for basis in (versuche_server or SERVER):
        try:
            req = urllib.request.Request(basis + pfad, headers=KOPF)
            with urllib.request.urlopen(req, timeout=30) as antwort:
                return json.loads(antwort.read().decode("utf-8")), basis
        except Exception as e:      # Server weg, Zeitablauf, kaputtes JSON
            letzter = e
            continue
    raise RuntimeError(f"Kein radio-browser-Server erreichbar ({letzter})")


def ist_playlist(url):
    """Auf .m3u/.pls zeigende Adressen sind Verweise, keine Streams -
    und zeigen erfahrungsgemaess oefter auf den falschen Sender."""
    pfad = urllib.parse.urlparse(url).path.lower()
    return pfad.endswith((".m3u", ".m3u8", ".pls", ".asx"))


#: Abfragewerte, die eine Adresse an eine Sitzung oder einen Schluessel binden.
SITZUNGSFELDER = re.compile(
    r"(^|&)(token|auth|authkey|sid|session|hash|key|signature|expires|"
    r"listenerid|user|pass)=", re.I)


def braucht_zugang(url):
    """Haengt die Adresse an einer Sitzung, einem Schluessel oder einem Konto?

    Solche Adressen spielen im Augenblick oft noch, sind aber keine frei
    zugaengliche Quelle: Die Kennung stammt aus einer fremden Sitzung und
    laeuft ab. Auf einem Geraet, das jahrelang unbeaufsichtigt laufen
    soll, ist das eine Zeitbombe - der Sender verstummt irgendwann ohne
    erkennbaren Grund, und der blinde Nutzer kann nicht nachsehen, warum.

    Am 2026-09-25 betraf das zwei der 78 ausgewaehlten Sender (SWR Kultur
    und radioeins, beide mit einem "sid" der ARD-Verteilung).
    """
    zerlegt = urllib.parse.urlparse(url)
    if zerlegt.username or zerlegt.password:        # http://name:wort@host/
        return True
    return bool(SITZUNGSFELDER.search(zerlegt.query))


def beste_adresse(sender):
    """Die dauerhafte Adresse waehlen, nicht die aufgeloeste.

    radio-browser liefert zwei Felder. `url_resolved` ist die Adresse
    NACH allen Weiterleitungen - bei den meisten Sendern die bessere
    Wahl, weil sie einen Umweg spart. Bei der ARD-Verteilung ist sie
    aber gerade falsch: `http://radioeins.de/stream` ist der dauerhafte
    Einstieg, und die Aufloesung haengt eine Sitzungskennung an, die
    spaeter ablaeuft. Gespeichert gehoert dann der Einstieg.
    """
    roh = (sender.get("url") or "").strip()
    aufgeloest = (sender.get("url_resolved") or "").strip()
    if aufgeloest and braucht_zugang(aufgeloest) and roh and not braucht_zugang(roh):
        return roh
    return aufgeloest or roh


def adresse_waehlen(name, sender):
    """Die Adresse fuer einen kuratierten Sender, samt Hinweis fuer den Nutzer.

    Gibt (Adresse, Hinweis) zurueck; der Hinweis ist None, wenn alles in
    Ordnung ist. Gemeldet wird vom Aufrufer - diese Funktion bleibt
    absichtlich stumm, damit sie ohne Netz und ohne Ausgabe pruefbar ist.
    """
    url = beste_adresse(sender)
    if not braucht_zugang(url):
        return url, None
    ersatz = ERSATZ_ADRESSEN.get(name)
    if ersatz:
        return ersatz, (f"  {name}: Datenbankadresse haengt an einer "
                        "Sitzungskennung - fester Ersatz eingesetzt")
    return url, (f"{name}: alle Adressen haengen an einer Sitzungskennung "
                 "- der Sender kann spaeter ohne Grund verstummen")


def guete(sender):
    """Sortierschluessel: frei zugaenglicher MP3-Stream ueber https."""
    bitrate = sender.get("bitrate") or 0
    url = beste_adresse(sender)
    return (
        1 if braucht_zugang(url) else 0,        # Sitzungskennungen ganz nach hinten
        1 if ist_playlist(url) else 0,          # dann die blossen Verweise
        0 if (sender.get("codec") or "").upper() == "MP3" else 1,
        0 if url.startswith("https://") else 1,
        -(bitrate if bitrate <= 256 else 0),    # sehr hohe Angaben sind meist Unsinn
        -(sender.get("votes") or 0),
    )


# ------------------------------------------------------------ Freie Suche
#
# Anders als sender_holen() arbeitet die Suche nicht mit der kuratierten
# Liste, sondern fragt die Datenbank ab. Sie ist das Werkzeug, um die
# zehn Sender zu FINDEN, die der Nutzer dann wirklich hoert - nicht, um
# fuenfhundert in die Medienliste zu kippen. Die Regel "weniger ist mehr"
# aus medienliste.md bleibt unberuehrt.

def _suchabfrage(bedingungen, grenze=250):
    """Eine Abfrage an /json/stations/search."""
    bedingungen = dict(bedingungen)
    bedingungen.update({"hidebroken": "true", "order": "clickcount",
                        "reverse": "true", "limit": str(grenze)})
    pfad = "/json/stations/search?" + urllib.parse.urlencode(bedingungen)
    daten, _ = hole(pfad)
    return daten


def _aufbereiten(rohdaten, land, herkunft=""):
    """Rohdaten zu unserem Format, ohne Dubletten und ohne Zugangsschranken."""
    ergebnis = []
    for s in rohdaten:
        url = beste_adresse(s)
        if not url or braucht_zugang(url) or ist_playlist(url):
            continue
        ergebnis.append({
            "name": (s.get("name") or "").strip(),
            "land": land,
            "url": url,
            "uuid": s.get("stationuuid"),
            "codec": s.get("codec"),
            "bitrate": s.get("bitrate"),
            "seite": s.get("homepage") or "",
            "logo": s.get("favicon") or "",
            "bundesland": (s.get("state") or "").strip(),
            "schlagwoerter": (s.get("tags") or "").strip(),
            "stimmen": s.get("votes") or 0,
            "herkunft": herkunft,
        })
    return ergebnis


def _zusammenfuehren(teile):
    """Dubletten entfernen - erst nach Kennung, dann nach Adresse."""
    gesehen, ergebnis = set(), []
    for s in sorted(teile, key=guete_gefunden):
        schluessel = s.get("uuid") or s["url"]
        if schluessel in gesehen:
            continue
        # Denselben Sender zweimal unter verschiedenen Kennungen gibt es
        # reichlich - deshalb zusaetzlich ueber die Adresse pruefen.
        if s["url"] in gesehen:
            continue
        gesehen.add(schluessel)
        gesehen.add(s["url"])
        ergebnis.append(s)
    return ergebnis


def guete_gefunden(s):
    """Sortierung der Suchtreffer: brauchbarer Stream, dann Beliebtheit."""
    return (
        1 if ist_playlist(s["url"]) else 0,
        0 if (s.get("codec") or "").upper() == "MP3" else 1,
        0 if s["url"].startswith("https://") else 1,
        -(s.get("stimmen") or 0),
    )


def bundesland_suchen(land, bundesland, genre=None, grenze=250):
    """Alle Sender eines Bundeslandes - ueber alle Schreibweisen."""
    schreibweisen = BUNDESLAENDER.get(land, {}).get(bundesland)
    if not schreibweisen:
        raise ValueError(f"Unbekanntes Bundesland: {bundesland} ({land})")

    kuerzel = LAENDER[land]
    treffer = []
    for wort in schreibweisen:
        bedingungen = {"countrycode": kuerzel, "state": wort,
                       "stateExact": "true"}
        try:
            treffer += _aufbereiten(_suchabfrage(bedingungen, grenze), land,
                                    f"Bundesland {bundesland}")
        except RuntimeError as e:
            fehler(f"Abfrage fuer '{wort}' gescheitert: {e}")
    if genre:
        treffer = nach_genre_filtern(treffer, genre)
    return _zusammenfuehren(treffer)


def stadt_suchen(land, stadt, genre=None, grenze=150):
    """Sender einer Stadt - auf drei Wegen, weil es kein Stadtfeld gibt.

    Die Datenbank kennt Land und Bundesland, aber keine Stadt. Gesucht
    wird deshalb dreifach: im Sendernamen ("Radio Hamburg"), in den
    Schlagwoertern (viele Sender tragen ihre Stadt als Tag) und im Feld
    "state" - bei Stadtstaaten wie Berlin, Hamburg, Bremen oder Wien
    steht die Stadt naemlich genau dort.

    Jeder Weg allein laesst einen Teil aus; zusammen decken sie das
    meiste ab. Falsche Treffer sind dabei einkalkuliert - deshalb wird
    jeder Fund vor der Uebernahme angetestet.
    """
    kuerzel = LAENDER[land]
    treffer = []
    for bedingungen, weg in (
        ({"countrycode": kuerzel, "name": stadt}, "Name"),
        ({"countrycode": kuerzel, "tag": stadt, "tagExact": "true"}, "Schlagwort"),
        ({"countrycode": kuerzel, "state": stadt, "stateExact": "true"}, "Bundesland"),
    ):
        try:
            treffer += _aufbereiten(_suchabfrage(bedingungen, grenze), land,
                                    f"{stadt} ({weg})")
        except RuntimeError as e:
            fehler(f"Abfrage ueber {weg} gescheitert: {e}")
    if genre:
        treffer = nach_genre_filtern(treffer, genre)
    return _zusammenfuehren(treffer)


def genre_suchen(land, genre, grenze=250):
    """Sender eines Genres im ganzen Land - ueber alle Schlagwoerter."""
    woerter = GENRES.get(genre)
    if not woerter:
        raise ValueError(f"Unbekanntes Genre: {genre}")

    kuerzel = LAENDER[land]
    treffer = []
    for wort in woerter:
        bedingungen = {"countrycode": kuerzel, "tag": wort, "tagExact": "true"}
        try:
            treffer += _aufbereiten(_suchabfrage(bedingungen, grenze), land,
                                    f"Genre {genre}")
        except RuntimeError as e:
            fehler(f"Abfrage fuer '{wort}' gescheitert: {e}")
    return _zusammenfuehren(treffer)


def nach_genre_filtern(sender, genre):
    """Eine bereits geholte Liste auf ein Genre eindampfen."""
    woerter = {w.lower() for w in GENRES.get(genre, [])}
    if not woerter:
        return sender
    gefiltert = []
    for s in sender:
        eigene = {t.strip().lower() for t in s.get("schlagwoerter", "").split(",")}
        if eigene & woerter:
            gefiltert.append(s)
    return gefiltert


def frei_suchen(land, text, grenze=150):
    """Freitext im Sendernamen - der Rueckfall, wenn nichts anderes passt."""
    bedingungen = {"countrycode": LAENDER[land], "name": text}
    return _zusammenfuehren(
        _aufbereiten(_suchabfrage(bedingungen, grenze), land, f"Suche '{text}'"))


# ---------------------------------------------------------------- Sender holen

def sender_holen(laender):
    """Kuratierte Liste aus der Datenbank zusammenstellen."""
    ergebnis = []
    basis = None
    for land in laender:
        kuerzel = LAENDER[land]
        pfad = (f"/json/stations/bycountrycodeexact/{kuerzel}"
                "?order=clickcount&reverse=true&limit=800&hidebroken=true")
        rohdaten, basis = hole(pfad, [basis] if basis else None)
        sagen(f"  {land}: {len(rohdaten)} Sender in der Datenbank")

        for eintrag in SENDER[land]:
            name, muster = eintrag[0], eintrag[1]
            url_muster = eintrag[2] if len(eintrag) > 2 else None

            pat = re.compile(muster, re.I)
            treffer = [s for s in rohdaten if pat.match((s.get("name") or "").strip())]
            if url_muster:
                upat = re.compile(url_muster, re.I)
                treffer = [s for s in treffer
                           if upat.search(beste_adresse(s))]
            if not treffer:
                fehler(f"nicht gefunden: {name} ({land})")
                continue
            bester = sorted(treffer, key=guete)[0]
            beste_url, hinweis = adresse_waehlen(name, bester)
            if hinweis and name in ERSATZ_ADRESSEN:
                sagen(hinweis)
            elif hinweis:
                fehler(hinweis)
            ergebnis.append({
                "name": name,
                "land": land,
                "url": beste_url,
                "uuid": bester.get("stationuuid"),
                "codec": bester.get("codec"),
                "bitrate": bester.get("bitrate"),
                "seite": bester.get("homepage") or "",
                "logo": bester.get("favicon") or "",
            })
    return ergebnis


# ---------------------------------------------------------------- Pruefen

def kopfzeilen(url, zeit=12):
    """Kopfzeilen samt ICY-Feldern holen. Umlaute in Kopfzeilen sind oft
    falsch kodiert, deshalb wird hier nachsichtig dekodiert."""
    p = subprocess.run(
        ["curl", "-sL", "--max-time", str(zeit), "-o", os.devnull, "-D", "-",
         "-H", "Icy-MetaData: 1", "-A", KOPF["User-Agent"], "-r", "0-64000",
         "-w", "\nCODE=%{http_code}\n", url],
        capture_output=True)
    text = p.stdout.decode("utf-8", "replace")
    felder = {}
    for zeile in text.splitlines():
        m = re.match(r"(?i)^(icy-name|content-type):\s*(.+)$", zeile.strip())
        if m:
            felder[m.group(1).lower()] = m.group(2).strip()
        m = re.match(r"^CODE=(\d+)$", zeile.strip())
        if m:
            felder["code"] = m.group(1)
    return felder


def dekodieren(url, zeit=40):
    """ffprobe muss echte Audiodaten finden - der ehrliche Test."""
    if not shutil.which("ffprobe"):
        return None, "ffprobe fehlt"
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json",
             "-show_streams", "-show_format", "-user_agent", KOPF["User-Agent"],
             "-rw_timeout", "12000000", "-analyzeduration", "3000000",
             "-probesize", "600000", url],
            capture_output=True, text=True, errors="replace", timeout=zeit)
        daten = json.loads(p.stdout)
        spuren = [s for s in daten.get("streams", []) if s.get("codec_type") == "audio"]
        if not spuren:
            letzte = (p.stderr.strip().splitlines() or ["kein Audiostream"])[-1]
            return None, letzte[:80]
        spur = spuren[0]
        rate = spur.get("bit_rate") or daten.get("format", {}).get("bit_rate")
        return {
            "codec": spur.get("codec_name"),
            "kbps": int(int(rate) / 1000) if rate else None,
            "hz": spur.get("sample_rate"),
            "kanaele": spur.get("channels"),
            "laeuft": daten.get("format", {}).get("tags", {}).get("StreamTitle"),
        }, None
    except subprocess.TimeoutExpired:
        return None, "Zeitablauf"
    except Exception as e:
        return None, str(e)[:80]


def passt_name(erwartet, gemeldet):
    """Grober Abgleich zwischen unserem Namen und dem, was der Sender meldet."""
    if not gemeldet:
        return True     # viele Sender melden gar nichts - kein Verdacht
    a = re.sub(r"[^a-z0-9]", "", erwartet.lower())
    b = re.sub(r"[^a-z0-9]", "", gemeldet.lower())
    return bool(a and b and (a[:6] in b or b[:6] in a))


def pruefen(liste, gruendlich=True, parallel=8):
    def einer(s):
        felder = kopfzeilen(s["url"])
        s["icy"] = felder.get("icy-name", "")
        s["code"] = felder.get("code", "000")
        # 401/402/403 heisst: Es gibt etwas, aber nicht fuer jeden.
        s["zugang_noetig"] = (s["code"] in ("401", "402", "403")
                              or braucht_zugang(s["url"]))
        if gruendlich:
            s["audio"], s["problem"] = dekodieren(s["url"])
            s["laeuft"] = s["code"] in ("200", "206") and s["audio"] is not None
        else:
            s["audio"], s["problem"] = None, None
            s["laeuft"] = s["code"] in ("200", "206")
        s["namenszweifel"] = s["laeuft"] and not passt_name(s["name"], s["icy"])
        return s

    with futures.ThreadPoolExecutor(parallel) as ex:
        return list(ex.map(einer, liste))


def bericht(liste):
    sagen()
    sagen(f"{'':5}{'Sender':30}{'meldet sich als':32}{'Ton'}")
    sagen("-" * 96)
    for s in liste:
        if not s["laeuft"]:
            grund = s.get("problem") or s["code"]
            if s["code"] in ("401", "402", "403"):
                grund = f"HTTP {s['code']} - verlangt Zugangsdaten"
            sagen(f"TOT  {s['name'][:29]:30}{'':32}{grund}")
            continue
        a = s.get("audio")
        ton = (f"{a['codec']} {a['kbps'] or '?'}k {a['hz']}Hz" if a
               else f"HTTP {s['code']}")
        hinweis = "   <-- Name pruefen" if s["namenszweifel"] else ""
        if s.get("zugang_noetig"):
            hinweis = "   <-- nicht frei zugaenglich"
        sagen(f"OK   {s['name'][:29]:30}{(s['icy'] or '-')[:31]:32}{ton}{hinweis}")

    laufen = [s for s in liste if s["laeuft"]]
    sagen()
    sagen(f"{len(laufen)} von {len(liste)} Sendern laufen.")
    tot = [s for s in liste if not s["laeuft"]]
    if tot:
        sagen("Nicht erreichbar: " + ", ".join(s["name"] for s in tot))
    return laufen


# ---------------------------------------------------------------- Ausgabe

def pls_schreiben(liste, ziel):
    os.makedirs(ziel, exist_ok=True)
    geschrieben = []

    def eine_datei(sender, pfad):
        zeilen = ["[playlist]", f"NumberOfEntries={len(sender)}"]
        for i, s in enumerate(sender, 1):
            zeilen += [f"File{i}={s['url']}", f"Title{i}={s['name']}", f"Length{i}=-1"]
        zeilen.append("Version=2")
        with open(pfad, "w", encoding="utf-8") as f:
            f.write("\n".join(zeilen) + "\n")
        geschrieben.append(pfad)

    for nr, land in enumerate(sorted({s["land"] for s in liste}), 1):
        teil = [s for s in liste if s["land"] == land]
        eine_datei(teil, os.path.join(ziel, f"{nr:02d}-{land}.pls"))
    eine_datei(liste, os.path.join(ziel, "Alle-Sender.pls"))

    for p in geschrieben:
        sagen(f"  geschrieben: {p}")


def laeuft_programm(name):
    return subprocess.run(["pgrep", "-x", name], capture_output=True).returncode == 0


def rhythmbox_eintragen(liste):
    """Sender als Internetradio in die Rhythmbox-Datenbank eintragen."""
    if laeuft_programm("rhythmbox"):
        fehler("Rhythmbox laeuft noch. Bitte beenden - sonst wird die "
               "Datenbank beim Schliessen ueberschrieben.")
        return False

    pfad = os.path.expanduser("~/.local/share/rhythmbox/rhythmdb.xml")
    if not os.path.exists(pfad):
        fehler(f"{pfad} nicht gefunden. Rhythmbox einmal starten und wieder "
               "beenden, damit die Datenbank angelegt wird.")
        return False

    sicherung = f"{pfad}.sicherung-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(pfad, sicherung)
    sagen(f"  Sicherung: {sicherung}")

    baum = ET.parse(pfad)
    wurzel = baum.getroot()
    vorhanden = {e.findtext("location") for e in wurzel.findall("entry")}

    neu = 0
    for s in liste:
        if s["url"] in vorhanden:
            continue
        e = ET.SubElement(wurzel, "entry", {"type": "iradio"})
        for feld, wert in (("title", s["name"]), ("genre", "Radio"),
                           ("artist", "Unbekannt"), ("album", "Unbekannt"),
                           ("location", s["url"]), ("date", "0"),
                           ("mimetype", "application/octet-stream"),
                           ("mtime", "0"), ("first-seen", "0"),
                           ("play-count", "0"), ("rating", "0")):
            ET.SubElement(e, feld).text = wert
        neu += 1

    baum.write(pfad, encoding="UTF-8", xml_declaration=True)
    sagen(f"  {neu} Sender neu eingetragen, "
          f"{len(liste) - neu} waren schon vorhanden.")
    sagen("  Rhythmbox starten - die Sender stehen unter 'Radio'.")
    return True


def liste_zeigen(liste):
    for land in sorted({s["land"] for s in liste}):
        sagen(f"== {land} ==")
        for s in [x for x in liste if x["land"] == land]:
            sagen(f"{s['name']}")
            sagen(f"  {s['url']}")
        sagen()


# ------------------------------------------------------- Medienliste (DialOS)
#
# Format und Regeln stehen in docs/medienliste.md und docs/medien-konzept.md
# im DialOS-Repository. Kurz: Die Sprechform ist der Satz, den der Nutzer
# spricht - klein geschrieben, Zahlen als Wort ("oe drei", nicht "Hitradio
# OE3"). Zwei fast gleich klingende Eintraege sind ein Fehler, weil die
# Erkennung sie verwechselt und der blinde Nutzer nicht nachsehen kann.

# WARUM HIER UMLAUTE STEHEN UND KEINE UMSCHREIBUNGEN (2026-09-30):
# Der Quelltext dieses Moduls kommt sonst ohne Umlaute aus. Diese Tabellen
# sind die Ausnahme, und zwar eine gemessene: Sie erzeugen die Saetze, die
# der Nutzer SPRICHT, und die muessen im Wortschatz des Vosk-Modells
# stehen. Am 2026-09-30 gegen vosk-model-small-de-0.15 geprueft - jede
# ASCII-Umschreibung fehlte dort, jede Umlautfassung war vorhanden:
#
#   fuenf/fünf, kaernten/kärnten, zuerich/zürich, wuerttemberg/württemberg,
#   oberoesterreich/oberösterreich, oe/ö
#
# Ein Wort, das nicht im Wortschatz steht, wirft Vosk STILL aus der
# Grammatik. Der Sender waere dann per Sprache unerreichbar, und im
# Protokoll staende nur, dass nichts erkannt wurde. Vor der Korrektur
# betraf das 25 der 78 Sender.
ZIFFERN = {"0": "null", "1": "eins", "2": "zwei", "3": "drei", "4": "vier",
           "5": "fünf", "6": "sechs", "7": "sieben", "8": "acht",
           "9": "neun"}

#: Wie einzelne Buchstaben gesprochen werden, fuer Abkuerzungen wie WDR.
#:
#: Fuenf davon stehen NICHT als ausgeschriebener Name im Wortschatz -
#: "ef", "vau", "ix", "uepsilon" und "zet" fehlen alle. Das deckt sich mit
#: Stephans Buchstaben-Messung vom 2026-09-21 (Buchstabennamen 16 von 26,
#: dort schon "ef", "vau" und "ix" als fehlend benannt). Fuer sie steht
#: hier der blosse Buchstabe bzw. die Fassung, die das Modell kennt -
#: geprueft am 2026-09-30.
BUCHSTABEN = {"a": "a", "b": "be", "c": "ce", "d": "de", "e": "e",
              "f": "f",          # "ef" fehlt im Wortschatz
              "g": "ge", "h": "ha", "i": "i", "j": "jot", "k": "ka",
              "l": "el", "m": "em", "n": "en", "o": "o", "p": "pe",
              "q": "ku", "r": "er", "s": "es", "t": "te", "u": "u",
              "v": "v",          # "vau" fehlt
              "w": "we",
              "x": "x",          # "ix" fehlt
              "y": "ypsilon",    # "uepsilon" fehlt
              "z": "zett"}       # "zet" fehlt

#: Sender, deren uebliche Sprechform sich nicht ableiten laesst.
SPRECHFORMEN = {
    "Hitradio Oe3": "ö drei",
    "Oe1": "ö eins",
    "FM4": "f em vier",
    "1LIVE": "eins live",
    "N-JOY": "en joy",
    "hr3": "ha er drei",
    "hr-iNFO": "ha er info",
    "BR24": "be er vierundzwanzig",
    "bigFM": "big f em",
    "Radio 88.6": "achtundachtzig sechs",
    "80s80s": "achtziger",
    "SRF 4 News": "es er f vier news",
    "Radio 24": "radio vierundzwanzig",
    # Zusammengeschriebene Namen kennt das Modell nur getrennt - am
    # 2026-09-30 geprueft: "radioeins", "kronehit", "inforadio",
    # "musikwelle" und "austropop" fehlen alle, die zwei Woerter nicht.
    "radioeins": "radio eins",
    "Kronehit": "krone hit",
    "Inforadio": "info radio",
    "SRF Musikwelle": "es er f musik welle",
    "Radio Arabella Austropop": "radio arabella austro pop",
    "SWR1 Baden-Wuerttemberg": "es we er eins baden württemberg",
    "WDR 5": "we de er fünf",
    "Hit Radio FFH": "hit radio f f ha",
    # Die ORF-Regionalsender heissen im Alltag nur nach ihrem Land. Das
    # vorangestellte "o er ef" spricht niemand, und kurze Saetze erkennt
    # Vosk zuverlaessiger.
    "ORF Radio Wien": "radio wien",
    # AUSNAHME TIROL (Stephan, 2026-10-08): "radio tirol einschalten" und auch
    # "tirol einschalten" klingen nach DialOS' Kollisionspruefung zu nah an
    # "radio einschalten" - wer den zuletzt gehoerten Sender will, bekaeme
    # Radio Tirol. "tiroler radio" ist frei und steht im Wortschatz. Die
    # uebrigen Regionalsender haben dasselbe Muster und brauchen dieselbe
    # Pruefung, sobald einer in die Medienliste kommt.
    "ORF Radio Tirol": "tiroler radio",
    # Dasselbe bei Life Radio (2026-10-08): "life radio einschalten" lag zu
    # nah an "radio einschalten", "life einschalten" ist frei.
    "Life Radio": "life",
    "ORF Radio Salzburg": "radio salzburg",
    "ORF Radio Steiermark": "radio steiermark",
    "ORF Radio Kaernten": "radio kärnten",
    "ORF Radio Vorarlberg": "radio vorarlberg",
    "ORF Radio Burgenland": "radio burgenland",
    "ORF Radio Oberoesterreich": "radio oberösterreich",
    "ORF Radio Niederoesterreich": "radio niederösterreich",
    "Antenne Kaernten": "antenne kärnten",
    "Energy Zuerich": "energy zürich",
    "Radio FM1": "f em eins",
    "RTS La Premiere": "la premiere",
    "MDR Jump": "em de er jump",
    "Radio BOB!": "bob",
    "LoungeFM": "lounge f em",
    # KEINE SPRECHFORM MOEGLICH: "Radio Argovia". Weder "argovia" noch
    # "argovja" steht im Wortschatz des kleinen Modells (2026-09-30
    # geprueft), und der Name laesst sich nicht sinnvoll in bekannte
    # Woerter zerlegen. Der Sender bleibt ueber die Oberflaeche
    # waehlbar, ist aber per Sprache nicht erreichbar - das gehoert dem
    # Menschen gesagt, statt still eine Sprechform zu erfinden, die nie
    # erkannt wird.
}

#: Sender, fuer die es keine sprechbare Form gibt - siehe oben.
OHNE_SPRECHFORM = ("Radio Argovia",)


def sprechform_vorschlag(name):
    """Ein Vorschlag, kein Ergebnis - nachbessern ist ausdruecklich vorgesehen.

    Die Regeln aus medienliste.md, so weit sie sich automatisch anwenden
    lassen: klein schreiben, Ziffern als Wort, reine Grossbuchstaben-
    Abkuerzungen buchstabieren. Was dabei schief klingt, korrigiert der
    Mensch - deshalb steht das Feld in der Oberflaeche zum Aendern offen.
    """
    if name in SPRECHFORMEN:
        return SPRECHFORMEN[name]

    teile = []
    for wort in re.split(r"[\s\-_/]+", name.strip()):
        if not wort:
            continue
        # Reine Abkuerzung aus Grossbuchstaben (WDR, SRF, ORF, MDR ...)
        kern = re.sub(r"[^A-Za-zÄÖÜäöü]", "", wort)
        if len(kern) >= 2 and kern.isupper() and len(kern) <= 4:
            teile.append(" ".join(BUCHSTABEN.get(b.lower(), b.lower())
                                  for b in kern))
            ziffern = re.sub(r"[^0-9]", "", wort)
            if ziffern:
                teile.append(" ".join(ZIFFERN[z] for z in ziffern))
            continue
        # Sonst: Ziffern ausschreiben, Rest klein
        stueck = []
        for zeichen in wort:
            if zeichen.isdigit():
                stueck.append(" " + ZIFFERN[zeichen] + " ")
            elif zeichen.isalnum() or zeichen in "äöüß":
                stueck.append(zeichen.lower())
        wort_neu = "".join(stueck).strip()
        if wort_neu:
            teile.append(wort_neu)

    ergebnis = " ".join(" ".join(teile).split())
    return ergebnis or name.lower()


def _klangform(text):
    """Grobe Lautgestalt, um Verwechselbares zu finden."""
    t = text.lower().strip()
    t = (t.replace("ä", "a").replace("ö", "o").replace("ü", "u")
          .replace("ß", "s").replace("ae", "a").replace("oe", "o")
          .replace("ue", "u"))
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return " ".join(t.split())


def aehnliche_sprechformen(eintraege, schwelle=0.82):
    """Paare, die sich zu aehnlich anhoeren - medienliste.md verlangt das.

    Gemeldet wird beides: sehr aehnliche Zeichenfolgen und der Fall, dass
    eine Sprechform vollstaendig am Anfang einer anderen steckt ("radio
    tirol" in "radio tirol sued"). Der zweite Fall ist der gefaehrlichere,
    weil die Erkennung dann schon beim kuerzeren Satz zuschlaegt.
    """
    import difflib

    paare = []
    daten = [(e, _klangform(e.get("sprechform") or "")) for e in eintraege]
    for i in range(len(daten)):
        eintrag_a, a = daten[i]
        if not a:
            continue
        for j in range(i + 1, len(daten)):
            eintrag_b, b = daten[j]
            if not b:
                continue
            if a == b:
                grund = "gleich"
            elif a.startswith(b + " ") or b.startswith(a + " "):
                grund = "eine steckt in der anderen"
            elif difflib.SequenceMatcher(None, a, b).ratio() >= schwelle:
                grund = "klingt sehr aehnlich"
            else:
                continue
            paare.append((eintrag_a, eintrag_b, grund))
    return paare


def medienliste_bauen(liste, art="radio"):
    """Die gewaehlten Sender im Austauschformat aus medienliste.md."""
    eintraege = []
    for s in liste:
        eintraege.append({
            "art": art,
            "sprechform": s.get("sprechform") or sprechform_vorschlag(s["name"]),
            "name": s["name"],
            "land": LAENDER.get(s["land"], s["land"]),
            "quelle": s["url"],
            # Nicht im Vorschlag von medienliste.md, aber das Konzept
            # verlangt es: ueber die UUID findet DialOS eine neue Adresse,
            # wenn ein Stream ausfaellt.
            "stationuuid": s.get("uuid", ""),
        })
    return {"stand": time.strftime("%Y-%m-%d"), "eintraege": eintraege}


def medienliste_schreiben(liste, pfad, art="radio"):
    daten = medienliste_bauen(liste, art)
    ordner = os.path.dirname(os.path.abspath(pfad))
    if ordner:
        os.makedirs(ordner, exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return daten


# ------------------------------------------------ Wo die Medienliste liegt
#
# ZWEI EBENEN, und der Grund dafuer steht in der NIEMALS-Liste von
# dialos-aufspielen: Am 2026-08-22 standen in piper-generic.conf zwei
# Dinge in einer Datei - die Konfiguration aus dem Repo UND die vom
# Nutzer gewaehlte Stimme. Beim naechsten Aufspielen war die Wahl
# stillschweigend zurueckgesetzt, waehrend das Geraet sich weiter mit dem
# anderen Namen vorstellte.
#
# Dieselbe Falle steht hier offen: Die Senderauswahl kommt aus dem Repo,
# aber der Nutzer soll eigene Sender aufnehmen koennen. Beides in eine
# Datei zu schreiben hiesse, seine Sender beim naechsten Aufspielen zu
# loeschen - auf einem Geraet, dessen Nutzer nicht nachsehen kann, warum
# sein Lieblingssender verschwunden ist.
#
# Deshalb, wie bei den persoenlichen Daten:
#
#   /usr/local/share/dialos/medienliste.json   Auslieferungszustand,
#                                              kommt aus dem Repo,
#                                              wird aufgespielt
#   ~/.config/dialos/medienliste.json          was der Nutzer selbst
#                                              hinzufuegt, je Konto,
#                                              wird NIE ueberschrieben

#: Die Gattungen, die im Feld "art" stehen duerfen - genau die aus
#: docs/medienliste.md. Alle vier liegen in DERSELBEN Datei; sie
#: unterscheiden sich nicht im Format, sondern in diesem einen Wert.
#:
#: Warum "nachrichten" zweimal vorkommt: Am 2026-09-25 war noch offen,
#: was "Nachrichten hoeren" ausloesen soll - einen Nachrichtensender live
#: oder die neueste Folge einer Kurznachrichten-Sendung. Beides ist
#: moeglich und darf nebeneinander stehen, deshalb zwei Werte statt einer
#: Entscheidung, die noch niemand getroffen hat.
ARTEN = (
    "radio",                # ein Sender, laeuft live
    "nachrichten-sender",   # dasselbe, aber als Antwort auf "Nachrichten"
    "nachrichten-podcast",  # neueste Folge einer Kurznachrichten-Sendung
    "podcast",              # RSS-Feed, neueste Folge oder Merkposition
    "hoerbuch",             # Datei auf der Platte oder auf DIALOS-DATA
)

#: Die Liste, die mit dem Geraet ausgeliefert wird.
SYSTEMLISTE = "/usr/local/share/dialos/medienliste.json"

#: Wo dieselbe Datei im Repo-Baum liegt - von dort spielt sie
#: dialos-aufspielen auf.
REPO_TEILPFAD = os.path.join("iso-build", "config", "includes.chroot",
                             "usr", "local", "share", "dialos",
                             "medienliste.json")


def eigene_liste():
    """Die persoenliche Ergaenzung des angemeldeten Kontos."""
    return os.path.join(os.path.expanduser("~"), ".config", "dialos",
                        "medienliste.json")


def repo_liste():
    """Der Platz im Repo-Baum - oder None, wenn wir nicht darin liegen.

    Dieselbe Technik wie _quelle_finden() in dialos-aufspielen: Wir
    suchen die Marke iso-build/config/includes.chroot im eigenen Pfad.
    Am Geraet liegt dieses Modul unter /usr/local/bin und findet sie
    nicht - dort gibt es kein Repo, und das ist richtig so.
    """
    hier = os.path.dirname(os.path.abspath(__file__))
    marke = os.path.join("iso-build", "config", "includes.chroot")
    if marke not in hier:
        return None
    baum = hier[:hier.index(marke)]
    return os.path.join(baum, REPO_TEILPFAD)


def speicherziel():
    """Was die Oberflaeche zum Speichern vorschlagen soll.

    Auf der Werkbank (im Repo-Baum) ist das die Datei, die spaeter
    aufgespielt wird - so geht die Auswahl ueber git ans Geraet. Am
    Geraet selbst ist es die persoenliche Liste des Kontos; dorthin darf
    ein normaler Nutzer schreiben, und kein Aufspielen raeumt sie weg.
    """
    return repo_liste() or eigene_liste()


#: Wie das Feld "Land" aus den persoenlichen Daten gemeint sein kann.
#: Der Mensch tippt in die Maske, was ihm einfaellt - "Österreich", "AT",
#: "A" oder "Austria". Wer nur auf eine Schreibweise prueft, schaltet dem
#: Nutzer das halbe Radio ab und sagt ihm nicht, warum.
LANDESNAMEN = {
    "DE": ("de", "d", "deutschland", "germany", "bundesrepublik deutschland"),
    "AT": ("at", "a", "oesterreich", "österreich", "austria"),
    "CH": ("ch", "schweiz", "switzerland", "suisse", "svizzera",
           "confoederatio helvetica"),
}

PERSOENLICHE_DATEN = os.path.join(os.path.expanduser("~"), ".config", "dialos",
                                  "persoenliche-daten.txt")


def land_des_geraets(pfad=None):
    """DE, AT, CH - oder None, wenn nichts Verwertbares dasteht.

    WARUM AUS DEN PERSOENLICHEN DATEN (Stephan, 2026-10-05: "Das Land
    wuerde ich immer an die Nutzerdaten verknuepfen. Da haben wir ja
    bereits eine Maske wo man die Nutzerdaten eingibt"): DialOS ist fuer
    Deutschland, Oesterreich UND die Schweiz. Eine Medienliste, die auf
    jedem Geraet dieselben Sender anbietet, haette auf zwei Dritteln der
    Geraete Saetze, die ins Leere gehen - "radio tirol einschalten" nuetzt
    einem Schweizer Nutzer nichts.
    Die Maske dafuer gibt es seit dem 2026-09-16, samt Feld "Land".

    NONE IST KEIN FEHLER, sondern der Normalfall vor dem Ausfuellen. Der
    Aufrufer zeigt dann ALLES - ein leeres Feld darf das Radio nicht
    abschalten. Das waere derselbe stille Fehlschlag, den dieses Projekt
    sonst ueberall vermeidet, nur schlimmer: Der Nutzer wuerde denken,
    das Geraet sei kaputt.
    """
    try:
        with open(pfad or PERSOENLICHE_DATEN, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None

    wert = ""
    for zeile in text.splitlines():
        if zeile.lstrip().startswith("#") or ":" not in zeile:
            continue
        name, _, rest = zeile.partition(":")
        if name.strip().lower() == "land":
            wert = rest.strip().lower()
            break
    if not wert:
        return None
    for kuerzel, namen in LANDESNAMEN.items():
        if wert in namen:
            return kuerzel
    return None


def _liste_laden(pfad):
    """Eine Datei lesen, oder eine leere Liste. Fehler sind hier kein
    Grund abzubrechen: Eine fehlende persoenliche Liste ist der
    Normalfall, und eine kaputte darf nicht das ganze Radio lahmlegen."""
    try:
        with open(pfad, encoding="utf-8") as f:
            daten = json.load(f)
    except (OSError, ValueError):
        return []
    eintraege = daten.get("eintraege") if isinstance(daten, dict) else daten
    return eintraege if isinstance(eintraege, list) else []


def medienliste_lesen(art=None, systemweit=None, persoenlich=None,
                      land="aus den daten"):
    """Beide Ebenen zusammengefuehrt - das, was DialOS ansagen kann.

    Die persoenliche Liste liegt oben: Wer einen Sender selbst aufnimmt,
    hat damit auch das Recht, einen mitgelieferten zu ersetzen. Verglichen
    wird ueber die Klangform, nicht ueber die Zeichenkette - "radio
    kaernten" und "radio kärnten" sind derselbe Satz, und zwei Eintraege
    dafuer waeren genau die Verwechslung, die medienliste.md verbietet.

    `art` grenzt auf eine Gattung ein ("radio", "nachrichten", "podcast",
    "hoerbuch"). Die Doppelten-Pruefung laeuft aber IMMER ueber alle
    Gattungen: Der Nutzer sagt einen Satz, keine Gattung - ein Podcast
    und ein Radiosender mit derselben Sprechform waeren fuer ihn
    ununterscheidbar, auch wenn sie im Format verschiedene Felder haben.

    `land` grenzt auf DE, AT oder CH ein. Standardmaessig kommt es aus den
    persoenlichen Daten des Kontos (Stephan, 2026-10-05); None zeigt
    alles. Die systemweite Liste DARF Eintraege fuer alle drei Laender
    haben - sie ist der Vorrat, nicht das Angebot. Was davon in die
    Grammatik kommt, entscheidet dieses Feld.

    Die PERSOENLICHE Liste wird NICHT nach Land gefiltert: Wer einen
    Sender selbst aufnimmt, hat ihn gewollt - auch den auslaendischen.
    Ein Filter, der die eigene Eingabe des Nutzers verwirft, waere
    dieselbe Anmassung wie eine ueberschriebene Stimmwahl.
    """
    systemweit = SYSTEMLISTE if systemweit is None else systemweit
    persoenlich = eigene_liste() if persoenlich is None else persoenlich
    if land == "aus den daten":
        land = land_des_geraets()

    ergebnis, gesehen = [], set()
    for pfad, mit_landfilter in ((persoenlich, False), (systemweit, True)):
        for eintrag in _liste_laden(pfad):
            if not isinstance(eintrag, dict):
                continue

            # ERST FILTERN, DANN ENTDOPPELN - die Reihenfolge ist nicht
            # beliebig (2026-10-05 beim Bau der Nachrichten gefunden).
            # Dieselbe Sprechform darf je Land auf eine ANDERE Quelle
            # zeigen: "landesweite nachrichten" bringt in Deutschland die
            # tagesschau, in der Schweiz SRF. Lief die Entdoppelung
            # zuerst, ueberlebte nur der erste der drei Eintraege - und
            # auf zwei Dritteln der Geraete haette der Satz auf eine
            # auslaendische Quelle gezeigt oder gefehlt.
            #
            # Ein Eintrag OHNE Land gilt ueberall - etwa ein Podcast oder
            # ein Hoerbuch, das an kein Land gebunden ist.
            if (mit_landfilter and land and eintrag.get("land")
                    and eintrag["land"] != land):
                continue

            schluessel = _klangform(eintrag.get("sprechform") or "")
            if not schluessel or schluessel in gesehen:
                continue
            gesehen.add(schluessel)

            if art is not None and eintrag.get("art") != art:
                continue
            ergebnis.append(eintrag)
    return ergebnis


def markdown_tabelle(liste):
    """Die Radio-Tabelle aus medienliste.md, zum Einsetzen ins Repository."""
    zeilen = ["| So sagt man es | Sender | Land | Quelle | Bemerkung |",
              "|---|---|---|---|---|"]
    for s in liste:
        sprechform = s.get("sprechform") or sprechform_vorschlag(s["name"])
        land = LAENDER.get(s["land"], s["land"])
        zeilen.append(f"| {sprechform} | {s['name']} | {land} | {s['url']} |  |")
    return "\n".join(zeilen) + "\n"


# ---------------------------------------------------------------- Ablauf

def main():
    p = argparse.ArgumentParser(
        description="Radiosender aus DE/AT/CH holen, pruefen und einbinden.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    p.add_argument("befehl",
                   choices=["pruefen", "liste", "pls", "rhythmbox",
                            "medienliste", "suchen", "bundeslaender", "genres"],
                   help="was getan werden soll")
    p.add_argument("ziel", nargs="?", default=".",
                   help="Zielverzeichnis (bei 'pls') bzw. Zieldatei "
                        "(bei 'medienliste')")
    p.add_argument("--land", action="append", choices=["DE", "AT", "CH"],
                   help="nur dieses Land (mehrfach moeglich)")
    p.add_argument("--schnell", action="store_true",
                   help="ohne ffprobe pruefen (nur Erreichbarkeit)")
    p.add_argument("--ohne-pruefung", action="store_true",
                   help="gar nicht pruefen, alles uebernehmen")
    p.add_argument("--speichern", metavar="DATEI",
                   help="geholte Liste als JSON sichern")
    p.add_argument("--laden", metavar="DATEI",
                   help="Liste aus JSON laden statt aus dem Netz holen")
    p.add_argument("--bundesland", metavar="NAME",
                   help="nur dieses Bundesland bzw. dieser Kanton (bei 'suchen')")
    p.add_argument("--stadt", metavar="NAME",
                   help="nur diese Stadt (bei 'suchen')")
    p.add_argument("--genre", metavar="NAME",
                   help="nur dieses Genre (bei 'suchen')")
    p.add_argument("--text", metavar="WORT",
                   help="Freitext im Sendernamen (bei 'suchen')")
    args = p.parse_args()

    laender = ([KUERZEL[k] for k in args.land] if args.land
               else list(SENDER.keys()))

    if args.befehl == "bundeslaender":
        for land in laender:
            sagen(f"== {land} ==")
            for name, schreibweisen in BUNDESLAENDER[land].items():
                sagen(f"  {name:26} (gesucht wird auch nach: "
                      f"{', '.join(schreibweisen[1:]) or 'nichts weiter'})")
            sagen()
        return 0

    if args.befehl == "genres":
        for name, woerter in GENRES.items():
            sagen(f"  {name:28} {', '.join(woerter)}")
        return 0

    if args.befehl == "suchen":
        if len(laender) != 1:
            fehler("Bitte genau ein Land angeben, etwa --land DE")
            return 1
        land = laender[0]
        try:
            if args.bundesland:
                liste = bundesland_suchen(land, args.bundesland, args.genre)
                was = f"Bundesland {args.bundesland}"
            elif args.stadt:
                liste = stadt_suchen(land, args.stadt, args.genre)
                was = f"Stadt {args.stadt}"
            elif args.genre:
                liste = genre_suchen(land, args.genre)
                was = f"Genre {args.genre}"
            elif args.text:
                liste = frei_suchen(land, args.text)
                was = f"Suche '{args.text}'"
            else:
                fehler("Bitte angeben, wonach gesucht werden soll: "
                       "--bundesland, --stadt, --genre oder --text")
                return 1
        except ValueError as e:
            fehler(str(e))
            return 1

        sagen(f"{len(liste)} Sender gefunden - {was}, {land}.")
        if not liste:
            return 0
        if args.ohne_pruefung:
            for s in liste:
                s.update(laeuft=True, icy="", code="-", audio=None,
                         problem=None, namenszweifel=False)
            for s in liste:
                sagen(f"  {s['name'][:44]:46} {s['bundesland'][:18]:20} "
                      f"{s['stimmen']:>5} Stimmen")
            return 0
        sagen("Gefundene Sender antesten ...")
        liste = pruefen(liste, gruendlich=not args.schnell)
        bericht(liste)
        if args.speichern:
            with open(args.speichern, "w", encoding="utf-8") as f:
                json.dump([s for s in liste if s["laeuft"]], f,
                          ensure_ascii=False, indent=1)
            sagen(f"Gefundene und laufende Sender gesichert: {args.speichern}")
        return 0

    if args.laden:
        with open(args.laden, encoding="utf-8") as f:
            liste = [s for s in json.load(f) if s["land"] in laender]
        sagen(f"{len(liste)} Sender aus {args.laden} geladen.")
    else:
        sagen("Senderliste von radio-browser.info holen ...")
        try:
            liste = sender_holen(laender)
        except RuntimeError as e:
            fehler(str(e))
            return 1
        sagen(f"{len(liste)} Sender ausgewaehlt.")

    if args.speichern:
        with open(args.speichern, "w", encoding="utf-8") as f:
            json.dump(liste, f, ensure_ascii=False, indent=1)
        sagen(f"Liste gesichert: {args.speichern}")

    if args.befehl == "liste":
        liste_zeigen(liste)
        return 0

    if args.ohne_pruefung:
        for s in liste:
            s.update(laeuft=True, icy="", code="-", audio=None,
                     problem=None, namenszweifel=False)
        laufen = liste
    else:
        sagen("Sender antesten (das dauert etwa eine Minute) ...")
        liste = pruefen(liste, gruendlich=not args.schnell)
        laufen = bericht(liste)

    if not laufen:
        fehler("Kein einziger Sender erreichbar - Netzverbindung pruefen.")
        return 1

    sagen()
    if args.befehl == "pruefen":
        return 0
    if args.befehl == "pls":
        pls_schreiben(laufen, os.path.expanduser(args.ziel))
        return 0
    if args.befehl == "medienliste":
        ziel = os.path.expanduser(
            args.ziel if args.ziel != "." else "medienliste.json")
        for s in laufen:
            s.setdefault("sprechform", sprechform_vorschlag(s["name"]))
        daten = medienliste_schreiben(laufen, ziel)
        sagen(f"  {len(daten['eintraege'])} Eintraege nach {ziel} geschrieben.")
        doppelt = aehnliche_sprechformen(daten["eintraege"])
        if doppelt:
            sagen()
            sagen("Diese Sprechformen liegen zu dicht beieinander - die "
                  "Spracherkennung wird sie verwechseln:")
            for a, b, grund in doppelt:
                sagen(f"  \"{a['sprechform']}\" und \"{b['sprechform']}\" "
                      f"({grund})")
            sagen("Bitte in der Datei nachbessern.")
        else:
            sagen("  Keine verwechselbaren Sprechformen gefunden.")
        return 0
    if args.befehl == "rhythmbox":
        return 0 if rhythmbox_eintragen(laufen) else 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sagen("\nAbgebrochen.")
        sys.exit(130)
