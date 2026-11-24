"""Die Unterstützungsstufe eines Kontos - ein System, das mitwächst.

Stephans Idee vom 2026-11-19, am 2026-11-24 zum Bauen freigegeben: „Man
startet als Mensch ohne Beeinträchtigung mit DialOS, und um so stärker eine
Beeinträchtigung wird, um so mehr unterstützt DialOS. Ohne
Betriebssystemwechsel." Der ganze Gedanke steht in docs/offene-punkte.md.

    Stufe 0  sieht gut, nutzt Sprache aus Bequemlichkeit
    Stufe 1  Sehschwäche: dazu große Schrift, hoher Kontrast
    Stufe 2  liest kaum noch: dazu Ansagen bei jedem Zustandswechsel
    Stufe 3  vollständig blind bedienbar - das DialOS bis 2026-11-24

Die Stufen bauen AUFEINANDER auf: Jede ist die vorige plus etwas. Dann prüft
jede Stufe nur, was sie dazubringt, statt den vierfachen Aufwand zu kosten.

OHNE DATEI GILT STUFE 3 (Stephans Wahl, 2026-11-24). Ein Gerät, das vor den
Stufen eingerichtet wurde, verhält sich also genau wie vorher - niemand merkt
etwas, bis die Stufe bewusst gesetzt wird.

Die Stufe gilt je Konto und liegt in ~/.config/dialos/stufe - wie die übrigen
Schalter (frageton, mitschrift, desktop-stil).
"""

from __future__ import annotations

import os

NIEDRIGSTE = 0
HOECHSTE = 3
VORGABE = 3

NAMEN = {
    0: "Stufe null",
    1: "Stufe eins",
    2: "Stufe zwei",
    3: "Stufe drei",
}

# AB WELCHER STUFE EINE ANSAGE-ART GESPROCHEN WIRD.
#
# Begrüßung, Antwort, Rückfrage und Warnung gelten in JEDER Stufe: Die
# Begrüßung auf Stephans Wunsch („Die Begrüßung würde ich auch bei Stufe 0
# drin lassen!"), damit die Stimme vertraut ist, wenn sie gebraucht wird. Wer
# fragt, will eine Antwort; eine Frage muss gestellt werden; und vor einem
# leeren Akku zu warnen schadet niemandem.
#
# Ein ZUSTANDSWECHSEL ("Ton über Lautsprecher", "Internetverbindung
# hergestellt", "am Netz und lädt") ist für jemanden, der den Bildschirm
# sieht, Lärm - er sieht das Symbol. Erst wer kaum noch liest, braucht ihn.
AB_STUFE = {
    "begruessung": 0,
    "antwort": 0,
    "rueckfrage": 0,
    "warnung": 0,
    "zustand": 2,
}


def datei() -> str:
    return os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        "dialos", "stufe")


def stufe() -> int:
    """Die Stufe dieses Kontos. Fehlt oder stimmt die Datei nicht: VORGABE."""
    try:
        with open(datei(), encoding="utf-8") as f:
            wert = int(f.read().strip())
    except (OSError, ValueError):
        return VORGABE
    if NIEDRIGSTE <= wert <= HOECHSTE:
        return wert
    return VORGABE


def setzen(wert: int) -> int:
    """Setzt die Stufe, begrenzt auf 0 bis 3. Gibt die gesetzte zurück."""
    wert = max(NIEDRIGSTE, min(HOECHSTE, int(wert)))
    pfad = datei()
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad + ".neu", "w", encoding="utf-8") as f:
        f.write(f"{wert}\n")
    os.replace(pfad + ".neu", pfad)
    return wert


def ansage_erlaubt(art: str, aktuelle: int | None = None) -> bool:
    """Wird eine Ansage dieser Art in der aktuellen Stufe gesprochen?

    Eine unbekannte Art wird IMMER gesprochen: Ein Tippfehler im Aufrufer darf
    ein Gerät nicht stumm machen - für einen blinden Nutzer ist eine Ansage
    zu viel harmlos, eine zu wenig nicht.
    """
    if aktuelle is None:
        aktuelle = stufe()
    return aktuelle >= AB_STUFE.get(art, NIEDRIGSTE)
