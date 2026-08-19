[Deutsch](sicherheit-datenschutz.md) | [English](sicherheit-datenschutz.en.md)

# Sicherheit & Datenschutz

## Grundprinzip

Die Zielgruppe (blinde, motorisch eingeschränkte, teils ältere Menschen)
ist besonders vulnerabel. Datenschutz und Ausfallsicherheit haben deshalb
durchgehend Priorität vor Bequemlichkeit oder Erkennungsqualität:

- Spracherkennung läuft offline (Vosk/lokale Modelle), keine Cloud-Dienste.
- Sicherheitskritische Aktionen laufen immer über eine explizite
  Ja/Nein-Rückfrage.
- Es wird immer davon ausgegangen, dass jemand seine Zugangs-/Einrichtungsdaten
  nicht ohne Weiteres zur Verfügung stellen möchte (siehe
  [ersteinrichtung.md](ersteinrichtung.md), Abschnitt "Datenschutz-Varianten").

## Automatische Anmeldung

Der Login-Bildschirm entfällt komplett (GDM-Autologin), da er für die
Zielgruppe eine der größten Hürden wäre (Passwort blind tippen,
Login-Auswahl bedienen). Trade-off: physischer Zugriff auf das Gerät
bedeutet direkten Zugriff auf das System – das wird dadurch abgefedert,
dass `nutzer`s Daten auf einer eigenen, mit einem Hardware-Schlüssel
verschlüsselten Partition liegen und das Konto ohne diesen Schlüssel
gesperrt ist (siehe unten).

**Admin-Zugriff:** Das Autologin-Konto ist immer `nutzer`
(`AutomaticLogin=true`), das Admin-Konto `dialosadmin` bleibt aktiv, aber
ohne Autologin (`AutomaticLogin=false`) – siehe
`scripts/dialos-setup-nutzer.sh`. Für Eingriffe vor Ort oder per RustDesk
(nachdem `nutzer` per Sprachbefehl "Hilfe rufen" gesagt hat): `nutzer`
**richtig abmelden**, danach am GDM-Bildschirm als `dialosadmin` mit
Passwort anmelden. Setzt voraus, dass `dialosadmin` ein gültiges, nicht
gesperrtes Passwort hat.

**Wichtig, korrigiert am 2026-08-14:** GNOME **"Benutzer wechseln"**
(statt richtigem Abmelden) bewusst **vermeiden** – lässt `nutzer`s
Sitzung im Hintergrund aktiv. Laut Testbefund vom 2026-08-13 (siehe
[offene-punkte.md](offene-punkte.md), Eintrag "Bluetooth-Lautsprecher/
Sprachausgabe manchmal nicht hörbar nach Login") konkurrieren dann zwei
gleichzeitig laufende `dialos-start-ansage.py`-Instanzen (eine pro
Konto) um Bluetooth-Reconnect und Audio-Stummschaltung, was die
Sprachausgabe unzuverlässig macht. Der vorhandene Ein-Instanz-Lock in
`dialos-start-ansage.py` verhindert nur doppelte Anmeldungen
*desselben* Kontos, nicht das kontoübergreifende Nebeneinander, das
"Benutzer wechseln" erzeugt.

## Verschlüsselung von nutzers Daten + Sicherheits-Stick

**Design seit 2026-08-14** (ersetzt die ursprüngliche Ganze-Platte-
Verschlüsselung, siehe README-Änderungsprotokoll 0.5.0).

**Warum kein initramfs-Weg mehr:** Der reale Live-Boot-Test von
`dialos-install` mit LUKS-Ganze-Platte-Verschlüsselung ist am 14.08.
gescheitert. Grund war nicht ein einzelner Bug, sondern dass der ganze
LUKS/initramfs-Weg strukturell fehleranfällig ist: die Schlüsseldatei
musste exakt im richtigen Moment im initramfs verfügbar sein (ein Bug
hängte den Stick vor der `cryptsetup open`-Nutzung schon aus), und
selbst der Installer selbst lief nicht rund (ein `pkexec`-Bug ließ den
Datei-Speichern-Dialog für das Schlüssel-Backup lautlos scheitern). Ein
initramfs bietet kaum Fehlerausgabe/Debugging-Möglichkeiten für die
Zielgruppe vor Ort - jeder Fehler dort bedeutet ein nicht bootendes
Gerät ohne Hilfe von Stephan.

**Aktuelles Design:** Nicht mehr die ganze Platte, sondern nur eine
eigene Partition wird verschlüsselt, die ausschließlich `nutzer`s Daten
enthält - und diese Partition wird NICHT im initramfs, sondern nach dem
Boot in der normalen, schon laufenden Systemumgebung geöffnet:

- **root-Partition** (ext4, ~100 GiB): System + `dialosadmin`s Home,
  **unverschlüsselt**. Bootet immer ganz normal, keine initramfs-
  Fallstricke mehr.
- **`dialos-nutzer-home`-Partition** (LUKS2, Rest der Kapazität):
  enthält ausschließlich `/home/nutzer`. Wird per `blkid -L
  dialos-nutzer-home` gefunden (LUKS2-Label, kein `/etc/crypttab`-
  Eintrag nötig).
- Der Sicherheits-Stick trägt weiterhin die Schlüsseldatei auf der
  Partition `DIALOS-KEY` (**ext4**, damit die Datei unter Windows gar
  nicht erst lesbar ist, und mit `root:root 755` selbst unter Linux nur
  für root zugreifbar), plus einen zweiten Datenbereich `DIALOS-DATA`
  (**exFAT**, damit `nutzer` ihn als normalen mobilen Datenträger unter
  Windows/macOS/Linux nutzen kann).
- **Der Swap ist seit 2026-08-16 ebenfalls verschlüsselt** (8 GiB,
  Schlüssel pro Start neu aus `/dev/urandom`, Eintrag in
  `/etc/crypttab`). Sonst könnten `nutzer`s ausgelagerte Speicherseiten -
  offene Dokumente, Mails, Browserinhalte - am LUKS-Schutz vorbei im
  Klartext auf der Platte landen. Der Zufallsschlüssel schließt den
  Ruhezustand (Hibernate) endgültig aus; Suspend-to-RAM bleibt
  unberührt. Wichtig beim Nachbauen: Debian 13 braucht dafür das eigene
  Paket `systemd-cryptsetup`, sonst wird `/etc/crypttab` **ohne jede
  Fehlermeldung** ignoriert.
- `dialos-stick-gate.service` (systemd-oneshot, läuft bei **jedem
  Boot** vor `display-manager.service`) prüft, ob der Stick da ist:
  wenn ja, öffnet es `dialos-nutzer-home` mit dem Schlüssel vom Stick
  und mountet sie nach `/home/nutzer`; erst danach wird `nutzer`s
  Autologin aktiviert (`SetAutomaticLogin true` über AccountsService/
  `gdbus`, derselbe Mechanismus wie in `scripts/dialos-setup-nutzer.sh`
  und [Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 4). Schlägt
  irgendein Schritt fehl (kein Stick, falscher/beschädigter Stick,
  Home-Partition fehlt) bleibt `/home/nutzer` ein leeres Verzeichnis
  und Autologin wird deaktiviert - GDM zeigt den normalen Login-
  Bildschirm.
- **Zusätzlich wird `nutzer`s Konto ohne Stick gesperrt** (`usermod -L`,
  seit 2026-08-16). Der abgeschaltete Autologin allein reichte nicht:
  GDM zeigt ohne Stick weiterhin beide Konten, und wer `nutzer`s
  Zufallspasswort kannte - es steht einmalig im Terminal, wenn
  `dialos-setup-nutzer.sh` es würfelt - hätte sich trotzdem anmelden
  können, in eine Sitzung gegen ein leeres Verzeichnis auf der
  **unverschlüsselten** root-Partition. Die Reihenfolge ist dabei nicht
  beliebig: erst entsperren, dann Autologin setzen, weil AccountsService
  `SetAutomaticLogin` für ein gesperrtes Konto mit "user is locked"
  ablehnt. `dialosadmin` wird nie gesperrt.
- `dialosadmin` bleibt davon komplett unberührt: nie Autologin, immer
  normales getipptes Passwort am GDM-Screen, unabhängig vom Stick.

Damit ist die ursprüngliche Idealvorstellung für die Zielgruppe weiter
erfüllt (Stick rein → Gerät einschalten → System spricht den Nutzer
an, ohne Tippen/Ablesen), aber ohne die fragile initramfs-Kette - und
zusätzlich wird jetzt tatsächlich geschützt, was am Gerät am
sensibelsten ist: `nutzer`s eigene Daten. System-Dateien,
`dialosadmin`s Home und Logs bleiben bewusst unverschlüsselt (bewusster
Kompromiss - siehe README-Änderungsprotokoll 0.5.0 für die Abwägung).

**Am 2026-08-16 in beide Richtungen auf echter Hardware nachgewiesen**
(per Journal belegt): ohne Stick greifen fünf Ebenen gleichzeitig -
Stick physisch weg, LUKS-Container zu, `/home/nutzer` kein
Einhängepunkt, Konto auf `L`, keine `nutzer`-Sitzung. Mit Stick meldet
sich `nutzer` automatisch an, das Konto steht wieder auf `P`. Der
verschlüsselte Swap läuft in beiden Fällen, weil er am Zufallsschlüssel
hängt und nicht am Stick.

Skripte/Units:
`usr/local/sbin/dialos-rekey`,
`usr/local/sbin/dialos-stick-gate.sh`,
`etc/systemd/system/dialos-stick-gate.service` (alle im Repo unter
`iso-build/config/includes.chroot/`, Installation siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 12).

**Praxishinweise:**
- Der Stick sollte getrennt vom Laptop aufbewahrt werden (z. B. am
  Schlüsselbund), sonst bringt die Verschlüsselung wenig, falls beides
  zusammen entwendet wird.
- **Empfohlene Standardgröße: 64 GB.**
  `dialos-setup-home-partition.sh`/`dialos-rekey`
  partitionieren den Stick immer in `DIALOS-KEY` (2 GiB, Schlüssel) +
  `DIALOS-DATA` (Rest der Kapazität, allgemeiner Speicher) - bei 64 GB
  bleiben `nutzer` dadurch automatisch ca. 62 GB als mobiler
  Datenträger (z. B. für Fotos, Dokumente), den er unabhängig vom
  Gerät mitnehmen kann.
- `scripts/dialos-setup-nutzer.sh` (legt das `nutzer`-Konto im
  Büro-Setup an) prüft vor `adduser`, ob `/home/nutzer` schon gemountet
  ist, und bricht sonst kontrolliert ab - sonst würde `nutzer`s Home mit
  allen Skel-Standardeinstellungen versehentlich auf der
  unverschlüsselten root-Partition landen.

## Wiederherstellung bei Stick-Verlust

Drei Wege, je nach Situation:

1. **Wiederherstellungs-Passwort manuell eingeben, über `dialosadmin`.**
   Da `nutzer`s Home-Partition nicht mehr im initramfs geöffnet wird,
   gibt es keinen automatischen Passwort-Prompt mehr am Boot-Bildschirm
   - `dialosadmin`s eigener Login ist aber vom Stick völlig unabhängig
   und funktioniert immer per getipptem Passwort. Ablauf: als
   `dialosadmin` anmelden, Terminal öffnen,
   `sudo cryptsetup open --type luks2 $(sudo blkid -L dialos-nutzer-home) dialos-nutzer-home`
   ausführen (fragt nach dem Wiederherstellungs-Passwort), danach
   `sudo mount /home/nutzer && sudo /usr/local/sbin/dialos-stick-gate.sh`
   - schaltet `nutzer`s Autologin für diese Sitzung frei. Komplett
   offline, unabhängig vom Stick und vom Netzwerk – der einzige Weg,
   ein Gerät überhaupt wieder nutzbar zu machen, wenn nichts anderes
   erreichbar ist. Wird von Stephan telefonisch angeleitet oder von
   einer Vertrauensperson vor Ort eingetippt, nicht vom Endnutzer selbst
   gewusst. **Wichtig:** Das ist nur eine einmalige Freischaltung für
   die laufende Sitzung - nach einem Neustart ohne Stick greift wieder
   die normale Sperre; für eine dauerhafte Lösung Weg 2 nutzen.
2. **Neuen Stick per Fernwartung einrichten** (`dialos-rekey`, auf dem
   installierten System). Sobald das Gerät einmal läuft (z. B. nach Weg 1)
   und der Nutzer "Hilfe rufen" sagt, verbindet sich Stephan per RustDesk
   und richtet remote einen neuen Stick ein: neuer Schlüssel wird erzeugt,
   als LUKS-Schlüssel hinzugefügt, der alte (verlorene) Schlüssel-Slot wird
   entwertet, ein neues Wiederherstellungs-Passwort wird vergeben.
3. **Ersatz-Stick von Stephan anfertigen und per Post verschicken**, falls
   das Gerät gar nicht mehr bootet (auch Weg 1 nicht möglich, z. B.
   Hardware-Defekt oder Passwort nicht griffbereit). Dafür lädt Stephan
   das verschlüsselte Schlüssel-Backup dieses Nutzers aus der eigenen
   Nextcloud, entschlüsselt es lokal mit dem zugehörigen
   Wiederherstellungs-Passwort und schreibt den Schlüssel auf einen neuen
   Stick.

Für Weg 2 und 3 braucht es das **verschlüsselte Schlüssel-Backup**: Das
Einrichtungs-Skript (`dialos-setup-home-partition.sh`) und das
Rekey-Werkzeug (`dialos-rekey`)
verschlüsseln die kleine Schlüsseldatei (nicht die ganze Festplatte) mit
einem eigenen, zufällig erzeugten Backup-Passwort (`openssl rand
-base64 32`, verschlüsselt via `openssl enc -aes-256-cbc -pbkdf2`) und
bieten an, die Datei zu speichern – Stephan legt sie in seiner eigenen,
selbst gehosteten Nextcloud ab (eine Datei pro Nutzer/Gerät), statt bei
einem fremden Cloud-Anbieter.

**Wichtig: Das Backup-Passwort ist bewusst NICHT dasselbe wie das
Wiederherstellungs-Passwort** aus Weg 1/2 oben. Würde dieselbe
Passphrase für beides verwendet, könnte jeder mit Kenntnis des
Wiederherstellungs-Passworts und Zugriff auf die Nextcloud den
Schlüssel entschlüsseln – ganz ohne den physischen Stick, was den
eigentlichen Zweck der Stick-Bindung aushebeln würde. Das
Skript zeigt das generierte Backup-Passwort einmalig nach dem
Speichern an; Stephan muss es getrennt von der Nextcloud aufbewahren
(z. B. im eigenen Passwort-Manager), niemals zusammen mit der
Backup-Datei selbst.

## Zugangsdaten für Dienste (Mail und später mehr)

Entschieden mit Stephan am 2026-08-18. Anlass: DialOS liest und schreibt
Mail direkt über IMAP/SMTP, weil Thunderbird von außen nicht steuerbar ist
(siehe [anwendungen.md](anwendungen.md)). Damit braucht DialOS das
Mailbox-Passwort selbst.

**Entschieden: eine Datei in `/home/nutzer`, Rechte `0600`, Besitzer
`nutzer`.** Nicht der GNOME-Schlüsselbund, nicht der Sicherheits-Stick.

Der Grund ist der Aufbau, den es schon gibt: `/home/nutzer` liegt auf der
LUKS-Partition, die nur aufgeht, wenn der Stick beim Booten da war. **Eine
Datei dort hat damit genau den Schutz des Sticks** - ohne Stick kein
entschlüsseltes Home, ohne Home keine Zugangsdaten. Ohne eine Zeile
zusätzliche Technik.

**Warum nicht der Stick selbst**, obwohl er der naheliegende Ort wäre:

- Er trägt den LUKS-Schlüssel. Weitere Geheimnisse dort bedeuten, dass ein
  verlorener Stick auch den Mailzugang mitnimmt - und `dialos-rekey`
  ersetzt nur den LUKS-Schlüssel, nichts weiter.
- Er kann mitten in der Sitzung abgezogen werden, während das Home
  eingehängt bleibt. Alles, was danach Zugangsdaten braucht, fiele aus.
- Es wäre eine zweite Stelle zu pflegen, die dasselbe leistet wie die
  erste.

**Warum nicht der Schlüsselbund** - hier ist eine Empfehlung
zurückgenommen worden, die vorher in diesem Projekt ausgesprochen war:

- Er liegt selbst in `/home/nutzer`, also hinter derselben LUKS-Tür. Er
  fügt ein Schloss hinzu, aber **keinen neuen Schutz**: Ein Prozess, der
  als `nutzer` läuft und die Datei lesen könnte, kann genauso den
  entsperrten Schlüsselbund fragen.
- Dafür fügt er eine Fehlerquelle hinzu. `nutzer` wird **per Autologin**
  angemeldet (`AutomaticLogin=nutzer` in der GDM-Konfiguration), es gibt
  also kein Passwort, mit dem PAM den Anmelde-Schlüsselbund aufschließen
  könnte. Bleibt er gesperrt, erscheint ein **Passwortdialog, den der
  Nutzer nicht sehen kann** - und die Mail blockiert lautlos. Das ist für
  diese Zielgruppe der schlechteste denkbare Ausgang.
- **Nicht bewiesen, und die Entscheidung hängt nicht daran:** Gemessen
  wurde in `dialosadmin`, und dort ist der Schlüsselbund entsperrt
  (`Locked = false` über die Secret-Service-Schnittstelle) - aber dort
  wird ein Passwort eingegeben. Für `nutzer` unter Autologin ließe sich
  das nur durch eine Anmeldung als `nutzer` mit derselben Abfrage klären.
  Selbst ein entsperrter Schlüsselbund brächte nach dem Punkt oben keinen
  Zuwachs an Schutz.

**Was dabei bewusst in Kauf genommen wird:** Das Passwort liegt im
Klartext auf der Platte. Auf einer Partition, die nur mit dem Stick
aufgeht, in einer Datei, die nur `nutzer` lesen darf. Der Schlüsselbund
wäre in derselben Lage - sein Speicher liegt auch dort, und was ihn
aufschließt, muss ebenfalls irgendwo herkommen.

## Versand-Sicherheit

Laptop und Sicherheits-Stick sollen getrennt versendet werden
(unterschiedlicher Tag/Paketdienst), damit ein abgefangenes Paket allein
nutzlos ist.

## Protokolle: was DialOS über den Nutzer mitschreibt

Vier Programme schreiben mit - Befehlsdienst, Diktat, Auskunft und Notizen.
Das ist für die Fehlersuche unverzichtbar und war schon mehrfach der einzige
Weg, einen Fehler überhaupt zu finden. Es heißt aber auch: **auf dem Gerät
liegt, was der Nutzer gesagt hat.** Deshalb gehört hierher, was wo liegt und
wer es sehen kann.

| Datei | Inhalt | Rechte | Aufbewahrung |
|---|---|---|---|
| `~/dialos-sprachbefehl.log` | erkannte Befehle | 0644 (Standard-umask) | wächst, wird nicht gedreht |
| `~/dialos-diktat.log` | **jeder diktierte Satz wörtlich** | 0644 | wächst, wird nicht gedreht |
| `~/dialos-auskunft.log` | Fragen und Antworten | 0644 | wächst, wird nicht gedreht |
| `~/dialos-notiz.log` | Aktionen, **keine** Einträge | 0644 | wächst, wird nicht gedreht |
| `~/.local/share/dialos/support/befehle-JJJJ-MM-TT.log` | Befehle + erste Zeile eines Diktats | **0600** | **7 Tage**, räumt sich selbst |

Alle liegen in `/home/nutzer` und damit **innerhalb der verschlüsselten
Home-Partition** - ohne Sicherheits-Stick ist keines davon lesbar. Nach außen
geht keines: kein Programm von DialOS lädt ein Protokoll irgendwohin.

**Das Support-Protokoll ist die Datei, die weitergegeben werden soll**
(Stephans Wunsch vom 2026-08-19) - beim Anruf soll nachlesbar sein, was das
Gerät wirklich gehört hat. Genau deshalb ist es die einzige, die **filtert**:

- die Befehle vollständig,
- vom Diktierten nur die **erste Zeile**, auf 60 Zeichen gekürzt, danach nur
  noch die Anzahl der weiteren Zeilen,
- dazu der Zusammenhang als Überschrift (Diktat, Einkaufszettel, Frage an das
  System, später Mail und Brief).

Der Grund für die Grenze: `~/dialos-diktat.log` enthält jeden diktierten Satz
wörtlich, also den ganzen Brief. Eine Datei, die für einen fremden Helfer
gedacht ist, darf die Post des Nutzers nicht enthalten. Eine Zeile genügt, um
zu erkennen, **dass** etwas erfasst wurde und ob es Sinn ergab - und ohne den
Zusammenhang wäre auch die wertlos: „Milch" allein sagt niemandem etwas,
„Einkaufszettel: Milch" sagt alles.

Rechte bewusst 0600 auf die Datei und 0700 auf den Ordner: es steht darin, was
der Nutzer gesagt hat, und das ist nichts für andere Konten auf demselben
Gerät. Sieben Tage, weil ein Support-Fall in dieser Zeit besprochen ist; die
Mitschrift löscht ältere Tagesdateien beim Start und um Mitternacht selbst.

**Offen:** Die vier Programm-Protokolle wachsen unbegrenzt und werden nicht
gedreht - beim Diktat ist das nicht nur eine Platzfrage, sondern heißt, dass
jeder je diktierte Brief dauerhaft im Klartext liegt. Steht in `TODO.md`.

## Fernwartung (RustDesk)

- Open Source, selbst hostbar – passt zur Datenschutz-Linie des Projekts.
- **Relay**: zunächst der öffentliche rustdesk.com-Dienst, später (sobald
  das System stabil läuft) ein eigener Server (hbbs/hbbr). Migration ist
  ein bewusst offener Punkt für später.
- **Die ID wird per TTS vorgelesen**, ziffernweise in Vierergruppen und
  zweimal - ein blinder Nutzer kann sie nicht ablesen und nichts mitschreiben.
  Als Zahl gesprochen wäre sie unbrauchbar („achtundsechzig Millionen…").
- **Ein Einmalpasswort ist mit RustDesk 1.4.9 nicht zu haben** (fünf Wege am
  2026-08-19 geprüft, alle zu):
  - Das Einmalpasswort, das RustDesk selbst erzeugt, steht in **keiner Datei** -
    nur im Speicher und in der Oberfläche, für einen blinden Nutzer also
    nirgends.
  - `rustdesk --password <wert>` ist wirkungslos: als Nutzer, mit laufender
    Anwendung, mit laufendem systemd-Dienst **und als root**. Rückgabewert 0,
    aber das Feld bleibt leer.
  - `rustdesk --get-temp-password` kommt auch nach 40 s nicht zurück - es
    startet eine volle Instanz.
  - `rustdesk-utils`, das den Wert berechnen könnte, ist im Paket nicht
    enthalten.
  - Den Wert selbst zu schreiben fällt aus: RustDesk legt dort keinen einfachen
    Hash ab, sondern einen mit einem lokalen Schlüssel verschlüsselten Wert (wie
    bei `enc_id`, 70 Zeichen). Das nachzubauen wäre geraten und bräche bei der
    nächsten Version still.

  Das ist kein Fehler dieses Projekts: [rustdesk#5074](https://github.com/rustdesk/rustdesk/issues/5074)
  heißt „Permanent password not deployable without user interaction" und ist
  offen. **Das Passwort setzt der Betreuer deshalb einmal im Büro über die
  Oberfläche** - es steht in seinen Unterlagen und nicht im Raum des Kunden.
- **Stattdessen garantiert DialOS die Begrenzung über die LAUFZEIT**, und das
  ist der härtere Hebel: Solange RustDesk nicht läuft, ist keine Verbindung
  möglich - unabhängig davon, wer das Passwort kennt.
  - Es startet nie von selbst, nur auf „Hilfe rufen".
  - „Fernwartung beenden" beendet es.
  - Vergisst der Nutzer das, endet es **nach einer Stunde von selbst, mit
    Ansage** (Stephan, 2026-08-19). Drei Minuten vorher kommt eine Vorwarnung,
    und ein erneutes „Hilfe rufen" verlängert - damit wird ein Betreuer nicht
    mitten in der Arbeit abgeschnitten.
- **Die Ansage sagt genau das, statt etwas Falsches zu behaupten:** „Das
  Passwort kennt Dein Betreuer schon. Die Fernwartung läuft nur, bis Du sagst:
  Fernwartung beenden." Einem Nutzer, der den Bildschirm nicht sieht, eine
  falsche Sicherheit zu erzählen („das Passwort gilt nur für diesen Einsatz")
  wäre schlimmer, als ihm die richtige zu erklären.
- **Offen und in `TODO.md`:** Die Zeitgrenze ist **absolut** und nicht am
  Leerlauf orientiert, obwohl Leerlauf die richtige Semantik wäre - das Risiko
  ist eine offene Fernwartung, an der niemand hängt. Auf diesem Gerät hat sich
  aber noch nie jemand verbunden, die Signatur einer aktiven Verbindung ist also
  unbekannt, und sie zu raten wäre der schlechtere Fehler. `dialos-hilfe.py`
  notiert deshalb während jeder Sitzung Prozessanzahl und Protokollgröße; nach
  der ersten echten Verbindung lässt sich die Leerlauf-Erkennung daraus **belegt**
  bauen.
- **RustDesk telefoniert nach Hause:** Beim Start werden `api.rustdesk.com` und
  der Vermittlungsdienst kontaktiert (im Protokoll belegt). Das ist der Preis
  des öffentlichen Relays und ein weiterer Grund für den eigenen Server später.
- **Zusätzliche Sicherheitsschicht**: RustDesk läuft NICHT dauerhaft im
  Hintergrund/Autostart. Der Nutzer vor Ort muss RustDesk erst aktiv per
  Sprachbefehl starten (z. B. "Hilfe rufen") – erst danach ist eine
  Fernverbindung überhaupt möglich, trotz des dauerhaften Passworts.
  Konsequenz: "echte" Notfall-Fernwartung (Nutzer reagiert gar nicht mehr,
  System eingefroren) funktioniert damit bewusst nicht – nur aktiv vom
  Nutzer angeforderte Hilfe.

## System-Basis

Debian bleibt die Basis (kein Wechsel zu einem atomaren/unveränderlichen
System wie Fedora Atomic/Silverblue oder openSUSE Aeon) – Stephans
Priorität liegt auf Debians Stabilität und Hardware-Support gegenüber
eingebautem Atomic-Rollback. (Der ursprünglich mitgenannte Grund
"ausgereiftes live-build-Tooling" ist entfallen - live-build wird seit
2026-08-16 nicht mehr verwendet, siehe
[Debian-zu-DialOS.md](Debian-zu-DialOS.md), Schritt 16.)
Eine Rollback-Absicherung müsste bei Bedarf separat über Btrfs-Snapshots
nachgerüstet werden.
