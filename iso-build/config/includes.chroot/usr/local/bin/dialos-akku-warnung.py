#!/usr/bin/env python3
"""DialOS: warnt hoerbar, wenn der Akku zur Neige geht.

Stephans Vorgabe vom 2026-08-21: drei Warnungen bei 25 %, 15 % und 5 %, "bei
der letzten mit einer Ansage, das Geraet muss an die Netzdose".

WARUM DAS GNOME NICHT SCHON ERLEDIGT. GNOME warnt bei niedrigem Akku - mit
einer Bildschirmmeldung. Der Nutzer sieht sie nicht. Fuer ihn faehrt das Geraet
ohne Vorwarnung herunter, mitten im Satz, und er hat keine Moeglichkeit, die
Ursache zu erraten. Ein leerer Akku ist fuer ihn schwerer zu deuten als fast
jeder andere Fehler: Das Geraet antwortet einfach nicht mehr.

DREI STUFEN, DREI TONFAELLE. Bei 25 % eine schlichte Feststellung, bei 15 % ein
Rat, bei 5 % eine Aufforderung mit Namen. Dreimal derselbe Satz waere dreimal
dasselbe Gewicht - dann bliebe fuer den Ernstfall keine Steigerung uebrig. Der
Name steht nur in der letzten Ansage, aus demselben Grund: Wer ihn dauernd
hoert, ueberhoert ihn (siehe dialos-namen.py).

"STECKDOSE" STATT "NETZDOSE". Stephans Wort war "Netzdose"; gesprochen wird
"Steckdose", weil das jeder ohne Nachdenken versteht. Die Ansage muss auf
Anhieb sitzen - sie kommt in dem Moment, in dem wenig Zeit bleibt.

EINMAL JE ENTLADUNG. Jede Stufe meldet sich einmal, bis das Geraet wieder am
Netz haengt. Eine Warnung, die sich alle zwei Minuten wiederholt, wird zum
Geraeusch, und beim naechsten Mal hoert niemand mehr hin.

WAEHREND EINES DIKTATS: 25 % und 15 % warten. Eine Ansage mitten in einem Brief
laeuft in die Aufnahme - die Echo-Unterdrueckung faengt viel ab, aber der Nutzer
verliert den Faden. Die 5 % sprechen trotzdem: Ein unterbrochener Satz ist
besser als ein Geraet, das mitten im Brief ausgeht.

BESTAETIGUNG BEIM ANSTECKEN. Wurde gewarnt und haengt das Geraet danach am Netz,
sagt DialOS das einmal. Wer nicht sieht, ob der Stecker sitzt, braucht diese
Rueckmeldung - sonst bleibt die Frage offen, bis das Geraet ausgeht oder nicht.
"""

import os
import subprocess
import sys
import time

SAY = "/usr/local/bin/dialos-say.py"
NAMEN_SKRIPT = "/usr/local/bin/dialos-namen.py"
PROTOKOLL = os.path.join(os.path.expanduser("~"), "dialos-akku.log")
STROMVERSORGUNG = "/sys/class/power_supply"

# Die drei Stufen, von oben nach unten. Der Text steht hier und nicht verstreut
# im Ablauf - wer die Formulierung aendern will, findet sie an einer Stelle.
STUFEN = [
    (25, "Der Akku ist bei 25 Prozent.", False),
    (15, "Der Akku ist bei 15 Prozent. Du solltest das Gerät bald "
         "an die Steckdose hängen.", False),
    (5,  "Der Akku ist fast leer. Das Gerät muss jetzt an die Steckdose.", True),
]

ANSAGE_AM_NETZ = "Das Gerät hängt am Netz und lädt."

# Alle 60 s reicht: Von 25 % auf 15 % vergehen auf diesem Geraet Stunden.
# Unter 10 % wird schneller nachgesehen - dort zaehlt jede Minute, und der
# Abstand zwischen 5 % und "aus" ist kurz.
TAKT_S = 60.0
TAKT_KNAPP_S = 20.0
KNAPP_AB = 10

# Wieder scharf, wenn der Stand um diesen Abstand ueber die Stufe steigt. Ohne
# Abstand wuerde eine Stufe bei einem Stand, der um einen Punkt schwankt,
# mehrfach melden - Akkuanzeigen springen.
ABSTAND = 3


def melde(text):
    try:
        with open(PROTOKOLL, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')}  {text}\n")
    except OSError:
        pass          # ein fehlendes Protokoll darf die Warnung nicht aufhalten


def anrede(satz):
    """Stellt den Nutzernamen voran - siehe dialos-namen.py.

    Geholt statt kopiert, und ein Ausfall des Moduls gibt den Satz unveraendert
    zurueck: Die Warnung darf nie davon abhaengen, dass ein Name eingetragen ist.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dialos_namen", NAMEN_SKRIPT)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.anrede(satz)
    except Exception:
        return satz


def sprich(text):
    try:
        if os.access(SAY, os.X_OK):
            subprocess.run([SAY, text], capture_output=True, timeout=60)
        else:
            print(text, flush=True)
    except Exception as fehler:
        melde(f"Ansage fehlgeschlagen: {fehler}")


def lies(pfad):
    try:
        with open(pfad, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def akku_pfad():
    """Der erste echte Akku. Ein Geraet ohne Akku ist zulaessig.

    Geprueft wird "type == Battery" UND das Vorhandensein von "capacity" -
    angeschlossene USB-Geraete melden sich ebenfalls als Stromversorgung
    (auf dem T490 zwei "ucsi-source-psy-..."), aber ohne Ladestand.
    """
    try:
        namen = sorted(os.listdir(STROMVERSORGUNG))
    except OSError:
        return None
    for name in namen:
        pfad = os.path.join(STROMVERSORGUNG, name)
        if lies(os.path.join(pfad, "type")) == "Battery" \
                and os.path.exists(os.path.join(pfad, "capacity")):
            return pfad
    return None


def am_netz():
    """Haengt das Geraet am Netz?

    Ueber die Netzteil-Anzeige und NICHT ueber den Akkustatus: Der meldete auf
    diesem Geraet "Not charging", waehrend das Netzteil steckte - eine
    Ladeschwelle haelt den Akku bei 78 % an. Wer "nicht am Laden" mit "am Akku"
    gleichsetzt, warnt bei gestecktem Kabel.
    """
    try:
        namen = sorted(os.listdir(STROMVERSORGUNG))
    except OSError:
        return True       # im Zweifel nicht warnen
    for name in namen:
        pfad = os.path.join(STROMVERSORGUNG, name)
        if lies(os.path.join(pfad, "type")) == "Mains":
            return lies(os.path.join(pfad, "online")) == "1"
    return True


def diktat_laeuft():
    ordner = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    return os.path.exists(os.path.join(ordner, "dialos-diktat-aktiv"))


def naechste_stufe(stand, erledigt):
    """Die tiefste noch offene Stufe, die der Stand erreicht hat.

    Tiefste und nicht hoechste: Faellt das Geraet im Ruhezustand von 30 % auf
    4 %, ist "fast leer" die richtige Ansage - nicht "25 Prozent". Die
    uebersprungenen Stufen gelten damit als erledigt.
    """
    offen = [s for s in STUFEN if s[0] not in erledigt and stand <= s[0]]
    return offen[-1] if offen else None


def main():
    pfad = akku_pfad()
    if not pfad:
        melde("kein Akku gefunden - Dienst beendet sich")
        return 0
    melde(f"=== Akku-Warnung gestartet, {os.path.basename(pfad)}, "
          f"Stufen {', '.join(str(s[0]) for s in STUFEN)} % ===")

    erledigt = set()
    gewarnt = False
    netz_vorher = None

    while True:
        try:
            stand_roh = lies(os.path.join(pfad, "capacity"))
            stand = int(stand_roh) if stand_roh.isdigit() else None
            netz = am_netz()

            if stand is None:
                melde(f"Ladestand nicht lesbar: {stand_roh!r}")
            elif netz:
                # Am Netz: alles zuruecksetzen, und einmal bestaetigen, falls
                # vorher gewarnt wurde.
                if erledigt:
                    melde(f"am Netz bei {stand} % - Stufen wieder scharf")
                erledigt.clear()
                if gewarnt:
                    sprich(ANSAGE_AM_NETZ)
                    melde("Ansage: am Netz")
                    gewarnt = False
            else:
                if netz_vorher:
                    melde(f"Netz getrennt bei {stand} %")
                # Stufen, die der Stand wieder deutlich ueberschritten hat,
                # werden erneut scharf.
                for grenze, _, _ in STUFEN:
                    if grenze in erledigt and stand > grenze + ABSTAND:
                        erledigt.discard(grenze)
                stufe = naechste_stufe(stand, erledigt)
                if stufe:
                    grenze, text, dringend = stufe
                    if diktat_laeuft() and not dringend:
                        melde(f"{stand} % - Stufe {grenze} wartet, Diktat laeuft")
                    else:
                        sprich(anrede(text) if dringend else text)
                        # Auch die uebersprungenen Stufen gelten als erledigt.
                        for g, _, _ in STUFEN:
                            if g >= grenze:
                                erledigt.add(g)
                        gewarnt = True
                        melde(f"{stand} % - Stufe {grenze} angesagt")
            netz_vorher = netz
            takt = TAKT_KNAPP_S if (stand is not None and stand <= KNAPP_AB
                                    and not netz) else TAKT_S
        except Exception as fehler:
            # Ein Aussetzer darf den Dienst nicht beenden. Ein stiller Ausfall
            # der Akkuwarnung faellt erst auf, wenn das Geraet ausgeht - und
            # dann ist es zu spaet, ihn zu bemerken.
            melde(f"Fehler im Durchlauf: {fehler}")
            takt = TAKT_S
        time.sleep(takt)


if __name__ == "__main__":
    sys.exit(main())
