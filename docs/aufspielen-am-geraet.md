# Aufspielen und Abnahme am Gerät

Diese Datei ist der Zettel für den Gang vom Arbeitsrechner ans Gerät. Sie
liegt im Repo, damit sie am Gerät selbst zur Hand ist - dort steht kein
Gesprächsverlauf vom Vortag zur Verfügung.

**Sie ist nur auf Deutsch.** Wie `docs/medienliste.md` und
`docs/installationsanleitung.md` richtet sie sich an den, der DialOS baut,
nicht an den, der es benutzt. Eine englische Fassung wäre Ballast.

Der allgemeine Ablauf gilt für jedes Aufspielen. Der Abschnitt
„Diesmal" am Ende ist datiert und wechselt.

---

## Vor dem Anfang: wo liegt was

| | |
|---|---|
| Repo am Gerät | `/media/dialosadmin/SanDisk-Extreme/DialOS/repo` |
| Quelle fürs Aufspielen | derselbe Baum, Unterordner `iso-build/config/includes.chroot` |
| Werkzeug | `/usr/local/sbin/dialos-aufspielen` |

Das installierte Skript kennt diesen Pfad fest. Ein Pfad als Argument wäre
genau das Schlupfloch, das die enge `sudoers`-Regel verhindern soll - die
Begründung steht im Kopf des Skripts.

Hängt die Platte woanders, schlägt das Skript mit `Quelle fehlt:` an, und
dann ist der Einhängepunkt zu richten, nicht das Skript.

---

## Schritt 1 - holen und trocken ansehen

```
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo && git pull && sudo /usr/local/sbin/dialos-aufspielen
```

Ohne `--wirklich` kopiert das Skript **nichts**. Es listet nur auf, welche
Dateien sich vom installierten Stand unterscheiden.

**Diese Liste ist zu lesen, nicht zu überblättern.** Sie ist die einzige
Stelle, an der auffällt, wenn etwas mitkommt, das niemand angefasst hat.

**Anhalten und nachsehen, wenn** in der Liste etwas aus `etc/` steht -
besonders `etc/sudoers.d/`. Dort liegen die Regeln, die Rechte vergeben.
Eine unerwartete Änderung daran ist kein Flüchtigkeitsfehler, sondern ein
Grund, erst die Herkunft zu klären.

---

## Schritt 2 - kopieren

```
sudo /usr/local/sbin/dialos-aufspielen --wirklich
```

Das Skript setzt die Rechte, die zum Ort gehören (`usr/local/bin` → 0755,
`usr/local/share` → 0644), lädt systemd neu und startet die DialOS-Dienste
neu, deren Datei sich geändert hat. Es installiert keine Pakete, löscht
nichts und fasst nichts außerhalb der bekannten Ziele an.

Danach gehören zwei Befehle dazu - **aber nur**, wenn in Schritt 1 eine
`.desktop`-Datei oder etwas unter `icons/` in der Liste stand. Sonst sind
sie überflüssig:

```
sudo update-desktop-database && sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
```

---

## Schritt 3 - fehlende Pakete

Pakete kommen über dasselbe Werkzeug, damit kein Passwort nötig ist:

```
sudo /usr/local/sbin/dialos-aufspielen --paket NAME
```

Das Skript lässt nur `install` zu. Ein Tippfehler kann damit nichts
**entfernen** - ein halb deinstalliertes GNOME ist auf einem Gerät, das nur
per Sprache bedient wird, ein Totalausfall. Nach dem Lauf zeigt es, was
`dpkg` wirklich meldet, nicht was beabsichtigt war.

---

## Schritt 4 - die zweite Pflichtprüfung

```
/usr/local/bin/dialos-grammatik-pruefen.py
```

Auf dem Arbeitsrechner läuft nur die **erste** Prüfung (`--nur-wortschatz`):
kennt das Vosk-Modell alle Wörter der Grammatik. Die **zweite** geht nur am
Gerät, weil dort Piper installiert ist: Piper spricht jeden Satz, Vosk hört
mit der vollständigen Grammatik zu, und es wird verglichen, was ankam.

Beides steht in `docs/sprachbefehle.md`. Ein Satz, der nur die erste
Prüfung bestanden hat, ist **nicht abgenommen**.

**Anhalten, wenn** die Prüfung ein Paar mit einem Abstand unter etwa 0,85
meldet. Zwei Sätze, die sich zu ähnlich klingen, treffen im Alltag den
falschen - und beim Radio heißt das, dass „abstellen" als „einschalten"
ankommt.

---

## Schritt 5 - proben, was auf der Werkbank nicht geht

**Diese Reihenfolge ist nicht beliebig.** Der erste Punkt kommt zuerst,
weil ein Radio, das sich nicht mehr abstellen lässt, schlimmer ist als
keins.

### Die Sätze, die es zu proben gibt

Alle brauchen das Auslösewort vorweg, wie jeder DialOS-Befehl.

| Satz | was passiert |
|---|---|
| radio einschalten | zuletzt gehörter Sender, sonst Rückfrage |
| musik abspielen | dasselbe |
| **radio abstellen** | anhalten - **nicht** „radio ausschalten" |
| was läuft gerade | Ansage von Sender und Titel |
| lauter machen / leiser machen | feste Stufen |
| nächster sender | nächster Eintrag der Liste |
| regionale nachrichten | nur AT belegt (ORF Radio Tirol) |
| landesweite nachrichten | je Land ein anderer Anbieter |
| nachrichten vorlesen / was gibt es neues | die passende Ebene von selbst |

**„radio ausschalten" gibt es nicht, und das ist kein Versehen.** Der Satz
lag mit 0,82 zu nah an „radio einschalten" - ein Zahlendreher im Gehör, und
das Radio geht an statt aus. „Stoppen" wurde auch verworfen: Es ist das
Kernwort von „sprachsteuerung stoppen", und ein Befehl, der versehentlich
die Sprachsteuerung abschaltet, macht das Gerät unbedienbar.

**Ein Sender wird mit `<Sprechform> einschalten` gewählt**, etwa „ö drei
einschalten" - nicht mit dem blanken Namen. Ein Befehl ist ein ganzer Satz,
sonst würde ein beiläufiges „Deutschlandfunk" im Gespräch das Radio
anwerfen. Daran ist am 2026-08-16 schon „windows" als Einzelwort
gescheitert.

**Bei den Nachrichten ist die Sprechform dagegen schon der Satz.**
„Regionale nachrichten einschalten" spricht niemand. Zwei Wörter mit
eindeutigem erstem Wort reichen, ein beiläufiges „Nachrichten" löst nichts
aus.

Welche Sätze das Gerät tatsächlich kennt, sagt es selbst:

```
/usr/local/bin/dialos-radio.py liste
```

### 5a. Befehlserkennung bei laufendem Radio

Radio an, und dann - mit Ton aus den Lautsprechern - den Abstellsatz
sprechen. Die Echo-Unterdrückung ist nie mit echtem Eigenton geprüft
worden; auf dem Arbeitsrechner ging das nicht.

Wenn der Dienst den Befehl nicht versteht, ist der Ausweg über das
Terminal:

```
/usr/local/bin/dialos-radio.py aus
```

Falls auch das nicht greift, bleibt `rhythmbox-client --stop`. Dass dieser
Ausweg vorher bekannt ist, gehört zur Probe.

### 5b. Spielt der Stream überhaupt

```
/usr/local/bin/dialos-radio.py liste && /usr/local/bin/dialos-radio.py --debug einschalten
```

`liste` zeigt, was nach dem Landfilter übrig ist. `--debug` schreibt die
Ausgabe zusätzlich aufs Terminal, sonst spricht das Programm nur.

### 5c. Was läuft gerade

```
rhythmbox-client --no-present --print-playing
```

Die Ansage „Was läuft gerade" hängt daran, dass bei einem **Stream** der
ICY-Titel kommt - nicht nur der Sendername. Ob das so ist, ist offen.

### 5d. MPRIS, für die Merkposition später

```
rhythmbox-client --no-present --check-running; ls -l /usr/lib/x86_64-linux-gnu/rhythmbox/plugins/mpris/
```

Die Hörbücher brauchen eine Merkposition, und `rhythmbox-client` allein
kann sie nicht - es hat nur `--seek`. Offen ist, ob das Plugin aktiv ist
und ob `Position` bei einem Stream etwas Sinnvolles liefert. Das ist keine
Abnahme für heute, nur die Messung, die der Hörbuch-Teil braucht.

---

## Schritt 6 - Abnahme der Konten

```
/media/dialosadmin/SanDisk-Extreme/DialOS/repo/scripts/dialos-nutzerkonto-pruefen.sh
```

Dieses Skript wird **nicht aufgespielt** - es liegt nur im Repo, nicht
unter `includes.chroot`. Es ist Werkzeug des Bauens, nicht Teil des
Geräts, und auf einem Kundengerät hätte es nichts zu suchen.

In **beiden** Konten laufen lassen (`dialosadmin` und `nutzer`). Der
Abschnitt „=== Radio ===" meldet eine fehlende systemweite Liste als
Mangel, eine fehlende persönliche nur als Auskunft - denn die persönliche
darf fehlen, das ist der Normalfall bei einem frischen Konto.

---

## Was auffällt, aber kein Fehler ist

**Das Gerät zeigt nicht alle 34 Einträge der Medienliste.** Der Landfilter
liest das Land aus `persoenliche-daten.txt` und lässt nur durch, was dazu
passt:

| Land | Radio | Nachrichten | sichtbar |
|---|---|---|---|
| DE | 10 | 1 | 11 |
| AT | 10 | 2 | 12 |
| CH | 10 | 1 | 11 |

Steht in den Nutzerdaten **kein** Land, kommen alle 34 - das ist Absicht,
sieht aber nach einem Fehler aus.

**Die persönliche Liste wird nie gefiltert.** Was der Nutzer selbst
aufnimmt, bleibt sichtbar, auch wenn es aus einem anderen Land kommt. Er
hat es ausgesucht; ihn danach zu bevormunden wäre falsch.

**`Radio Argovia` hat keine Sprechform.** Das Vosk-Modell kennt „argovia"
nicht, und ein Sender, der per Sprache nicht erreichbar ist, soll auch
nicht so tun. Er steht in `OHNE_SPRECHFORM` und ist nur im Fenster
anwählbar.

---

## Diesmal: Radio und Medienliste (Stand 2026-10-08)

Auf der Werkbank fertig und noch nie am Gerät gelaufen. **Diese Tabelle ist
eine Erwartung, keine Tatsache** - was wirklich abweicht, sagt der trockene
Lauf aus Schritt 1. Weicht beides voneinander ab, hat das Skript recht:

Belegt geändert sind seit dem letzten Aufspielen `dialos-radio.py`,
`dialos_podcast.py`, `dialos_rhythmbox_sender.py`,
`dialos-sprachbefehl-desktop.py` und `medienliste.json`. Die Filterleiste
in `dialos-rhythmbox.py` und der Modellfund in
`dialos-grammatik-pruefen.py` sind vom 30.09. und kommen voraussichtlich
mit, falls seither nicht aufgespielt wurde.

Keine `.desktop`-Datei und kein Symbol ist dabei - Schritt 2 braucht also
seine beiden Zusatzbefehle diesmal nicht.

| Datei | was sie tut |
|---|---|
| `dialos-radio.py` | **neu** - der Leser: einschalten, sender, aus, lauter, leiser, was-laeuft, naechster, liste, nachrichten |
| `dialos_podcast.py` | **neu** - RSS lesen und prüfen, für die Nachrichten-Folgen |
| `dialos_rhythmbox_sender.py` | Landfilter, zwei Listenebenen, Sprechformen |
| `dialos-rhythmbox.py` | Filterleiste im Fenster |
| `dialos-sprachbefehl-desktop.py` | sieben Radio-Sätze, Nachrichten-Sätze |
| `dialos-grammatik-pruefen.py` | findet das Modell jetzt an zwei Orten, `--nur-wortschatz` |
| `medienliste.json` | 34 Einträge: 30 Radio (10 je Land) + 4 Nachrichten |
| `dialos-nutzerkonto-pruefen.sh` | Abschnitt „=== Radio ===" |

**Fehlendes Paket:** `ffmpeg`. Es steht seit dem 2026-09-30 in
`desktop.list.chroot`, aber ein vorher aufgebautes Gerät hat es nicht.
Ohne `ffprobe` prüft die Senderliste nur, ob der Server antwortet - nicht,
ob Ton kommt.

```
sudo /usr/local/sbin/dialos-aufspielen --paket ffmpeg
```

`apt-get install` setzt ein neu installiertes Paket von selbst auf
„manuell", `autoremove` holt es also nicht wieder weg. Zur Sicherheit
nachsehen:

```
apt-mark showmanual | grep -x ffmpeg
```

**Die Nachrichten sind je Land verschieden gebaut**, und zwar nicht aus
Bequemlichkeit:

| Land | Satz | was kommt | Form |
|---|---|---|---|
| DE | „landesweite nachrichten" | tagesschau in 100 Sekunden | Podcast, neueste Folge (2:12) |
| CH | „landesweite nachrichten" | SRF Nachrichten | Podcast, neueste Folge (5:54) |
| AT | „landesweite nachrichten" | Ö1 | **Livestream** |
| AT | „regionale nachrichten" | ORF Radio Tirol | **Livestream** |

Für Österreich gibt es keinen brauchbaren Kurznachrichten-Feed: Der
Ö3-Feed ist abgeschaltet, die Ö1-Journale laufen 60 Minuten. Deshalb dort
der Livestream - Stephans Entscheidung vom 2026-10-05: „Für Österreich die
stündlichen Nachrichten live".

**Weltweite Nachrichten fehlen mit Absicht.** Die Deutsche Welle bietet nur
ein Lernformat an („langsam gesprochene Nachrichten"), und das ist für
jemanden, der sich informieren will, das falsche Angebot.

**Was danach ins TODO zurückgehört:** ob 5a bestanden ist, ob
`--print-playing` den ICY-Titel liefert und was MPRIS gesagt hat. Der
Hörbuch-Teil wartet auf diese drei Antworten.

### Ergebnis vom 2026-10-08 (erster Lauf am T490)

**Der trockene Lauf hatte recht, nicht die Tabelle:** Es kamen 15 Dateien,
darunter `dialos-rhythmbox.py`, `dialos_farben.py`, die `.desktop`-Datei und
sechs Symbole - die Zusatzbefehle aus Schritt 2 waren also doch nötig.
`ffmpeg` war schon da (für das Vorführvideo am 2026-10-05 installiert).

**Die drei Antworten, auf die der Hörbuch-Teil wartet:**

1. **5a bestanden.** „Radio abstellen" wirkte bei laufendem Ö3 aus den
   Lautsprechern - die Echo-Unterdrückung hielt den Eigenton nicht für einen
   Befehl.
2. **`--print-playing` liefert den ICY-Titel NICHT** - auch nicht `%st` und
   nicht MPRIS, nur den Sendernamen (gegengeprüft mit Kronehit, das
   „coldplay - higher power" mitschickte). `dialos-radio.py` liest den Titel
   jetzt selbst aus dem Stream. Nebenbefund: Ö3 schickt mal Liedtitel, mal
   nur „HITRADIO Ö3 - Livestream"; Life Radio nie.
3. **MPRIS:** Plugin aktiv, liegt aber unter
   `/usr/lib/x86_64-linux-gnu/rhythmbox/plugins/mpris` (oben berichtigt).
   Beim Stream zählt `Position` mit (4 s, 7 s), `CanSeek` ist `false`,
   `mpris:length` 0, `xesam:url` liefert die Adresse. Ob `SetPosition` bei
   einer Datei greift, ist damit noch nicht gemessen - das ist der nächste
   Schritt für die Hörbücher.

**Drei Fehler, die nur am Gerät auffallen konnten - alle behoben:**

- **`--play-uri` spielt nur, was in Rhythmbox' Datenbank steht.** Für jede
  andere Adresse meldet es Erfolg und bleibt still. Auf dem Arbeitsrechner
  standen die Sender schon drin. `dialos-radio.py` trägt jetzt vor dem
  Abspielen die ganze Medienliste ein (Rhythmbox dafür einmal zu).
- **Lauter/leiser:** `--print-volume` meldet „0,799988" mit deutschem Komma.
- **Die Grammatik am Arbeitsrechner ist unvollständig:** Medienliste und
  Programme liegen nur am Gerät unter `/usr/local/bin`. Erst hier schlugen
  zwei Tests an - „radio ausschalten" stand noch in `dialos-programm.py`
  (jetzt gestrichen, ebenso „musik ausschalten"), „radio tirol" und „life
  radio" klangen zu nah an „radio einschalten" (jetzt „tiroler radio" und
  „life"), und Sender wie Programme fehlten in der Befehlsübersicht.
  **Folge für die Werkbank:** Ein grüner Testlauf dort beweist für diese
  Prüfungen nichts - `python3 -m unittest discover -s tests` gehört nach
  dem Aufspielen auch am Gerät ausgeführt. Hier: 143 Tests grün, 79 Sätze
  wörtlich erkannt.

