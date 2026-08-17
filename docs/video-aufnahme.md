[Deutsch](video-aufnahme.md) | [English](video-aufnahme.en.md)

# Vorführvideos aufnehmen

Wie DialOS gefilmt wird, damit Sprachausgabe und Spracheingabe getrennt
im Schnitt ankommen. Eingerichtet und belegt am 2026-08-17.

## Was sich nicht aufnehmen lässt - und warum

Zwei Grenzen bestimmen den ganzen Ablauf. Sie lassen sich nicht
umprogrammieren:

- **Der Systemstart.** Zum Zeitpunkt des Bootens läuft noch keine
  Aufnahmesoftware.
- **Der Benutzerwechsel.** Der Rekorder läuft *innerhalb* einer Sitzung
  und stirbt beim Abmelden.

Für beides braucht es eine **Kamera auf einem Stativ**. Das ist keine
Notlösung: Der AIRHUG ist ein Lautsprecher, kein Ohrhörer - die Kamera
nimmt Michaels Ansage *und* die gesprochenen Befehle im Raum auf, also
genau das, was ein Besucher hören würde. Für „Gerät einschalten, Stick
steckt, es meldet sich von selbst" ist das sogar überzeugender als eine
Bildschirmaufnahme.

Alles, was **innerhalb einer Sitzung** passiert - die Desktop-Umschaltung
zum Beispiel - wird mit OBS aufgenommen, weil dort der Bildschirminhalt
zählt.

## OBS: die Einrichtung

Paket `obs-studio` (Debian 13: 30.2.3). Die Konfiguration liegt in
`~/.config/obs-studio/` und besteht aus drei Dateien:

| Datei | Zweck |
|---|---|
| `global.ini` | wählt Profil und Szenensammlung „DialOS" vor, überspringt den Einrichtungsassistenten |
| `basic/profiles/DialOS/basic.ini` | Ausgabemodus, Auflösung, **`RecTracks=7`** |
| `basic/scenes/DialOS.json` | Szene mit drei Quellen und der Spurzuordnung |

**`RecTracks=7` ist der entscheidende Wert.** Es ist eine Bitmaske:
1 = Spur 1, 2 = Spur 2, 4 = Spur 3, zusammen 7. Ohne sie schreibt OBS nur
eine gemischte Spur, und der Schnitt wäre nicht mehr zu trennen.

Welche Quelle auf welcher Spur landet, steht in der Szene als `mixers`
(gleiche Bitmaske pro Quelle):

| Spur | Inhalt | `mixers` |
|---|---|---|
| 1 | Mischung aus beidem - nur als Referenz beim Sichten | – |
| 2 | **DialOS-Stimme**, Mitschnitt der Ausgabe | `3` (Spur 1+2) |
| 3 | **Mikrofon**, die gesprochenen Befehle | `5` (Spur 1+3) |

Aufnahmen landen in `~/Videos/DialOS`, 1920×1080 bei 30 Bildern/s
(herunterskaliert von 3072×1728), Format **MKV**. MKV bewusst statt MP4:
Bricht die Aufnahme ab, ist eine MKV noch brauchbar, eine MP4 wäre
verloren. Kdenlive liest beides.

**Die Spuren tragen in der Datei keine Namen.** Die Einträge unter
`[AudioTracks]` in `basic.ini` wirken nur in der OBS-Oberfläche, nicht in
der MKV. Im Schnittprogramm heißen sie also schlicht 1, 2, 3 - die
Reihenfolge oben gilt.

## Die zwei Fallen, die den Ton ruinieren

Beide sind am 2026-08-17 real aufgetreten, jeweils kurz vor der Aufnahme:

**1. Das Headset fällt auf Telefonqualität.** Der AIRHUG kann A2DP und
HFP nicht gleichzeitig. Sobald irgendetwas sein Mikrofon öffnet, schaltet
er auf `headset-head-unit` - und ausgerechnet die Stimme, die aufgenommen
werden soll, klingt danach nach Telefon. Am Mitschnitt direkt ablesbar:

| Profil | Mitschnitt der Ausgabe |
|---|---|
| `headset-head-unit` (HFP) | 1 Kanal, 16000 Hz |
| `a2dp-sink` | 2 Kanäle, 48000 Hz |

Deshalb ist in der Szene **fest das eingebaute Mikrofon** eingetragen,
nicht „Standard". Vor jeder Aufnahme prüfen:

```bash
pactl list cards | grep -A1 "Name: bluez" ; pactl list short sources | grep bluez_output
```

Steht dort HFP, zurückschalten:

```bash
pactl set-card-profile bluez_card.<MAC> a2dp-sink
```

**2. Etwas greift doch zum Bluetooth-Mikrofon.** Dagegen hilft, das
eingebaute Mikrofon zur Standard-Eingabe zu machen - dann kann kein
Programm es aus Versehen erwischen:

```bash
pactl set-default-source alsa_input.pci-0000_00_1f.3.analog-stereo
```

## Ablauf einer Aufnahme

In OBS unter **Einstellungen → Hotkeys** „Aufnahme starten/beenden" auf
`F9`/`F10` legen. Das muss in der Oberfläche passieren: OBS schreibt seine
Konfiguration beim Beenden zurück und überschreibt Änderungen an den
Dateien, die währenddessen entstehen.

1. OBS starten, mit `Super`+`H` wegminimieren (im GNOME-Standard gibt es
   keinen Minimieren-Knopf in der Titelleiste, nur Schließen)
2. `F9`, zwei Sekunden Ruhe
3. Vorführen, dabei sprechen
4. `F10`

Zwei Dinge, die beim Ansehen sonst irritieren und keine Fehler sind:
Zwischen gesprochenem Befehl und Reaktion liegt gut eine Sekunde - der
Dienst wartet auf die Sprechpause. Und **während DialOS spricht, hört es
bewusst nicht zu**; ein Befehl mitten in die Ansage hinein wird
ignoriert (siehe [sprachbefehle.md](sprachbefehle.md)).

## Beim Schnitt

Das eingebaute Mikrofon hört den AIRHUG-Lautsprecher **mit**. Spur 3
enthält also auch Michael, nur dumpfer. Beim Mischen Spur 3 leiser
ziehen und Michaels Stimme aus Spur 2 nehmen, sonst klingt es doppelt.
