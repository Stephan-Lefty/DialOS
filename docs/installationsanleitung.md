# DialOS von Null aufbauen

Diese Anleitung führt ein leeres ThinkPad zu einem fertigen DialOS - beide Konten, `dialosadmin` und `nutzer`. Sie ist für den Fall geschrieben, dass **kein Rechner zur Hand ist, der noch etwas weiß**: Während der Installation ist die Platte leer, die Claude-App ist weg, und auch der bisherige Gesprächsverlauf existiert nicht mehr.

> **Diese Anleitung vor dem Anfangen ausdrucken oder auf ein zweites Gerät legen.** Sie liegt auf derselben Platte, die während der Installation gebraucht wird - am Zielgerät ist sie dann nicht lesbar.

**Stand:** 25.09.2026, abends (Teil 2 ist jetzt wörtlich die offizielle Anleitung von Anthropic) · **Zeit:** ein halber Tag, davon viel Wartezeit · **Grundlage:** `docs/Debian-zu-DialOS.md` im Repo. Diese Anleitung ist die Kurzform für den Handgriff; das Rezept dort erklärt jeden Schritt und begründet ihn.

## Was bereitliegen muss

- **USB-Stick mit Debian 13 (trixie)**, aktuelle Netinst- oder DVD-Fassung von `debian.org`
- **Die externe Platte** mit diesem Repository (`SanDisk-Extreme`)
- **Die beiden Sicherheits-Sticks** `DIALOS-KEY` und `DIALOS-DATA`
- **Netzwerk**, Kabel oder WLAN, und das Netzteil - die Installation braucht beides durchgehend
- **Rescuezilla-Stick**, falls ein Abbild gezogen werden soll (Teil 0)

---

# Teil 0: Sichern, bevor gelöscht wird

Alles, was hier nicht gesichert wird, ist danach weg. Das Repository ist gesichert, sobald es **gepusht** ist - ein Commit allein genügt nicht.

## 0.1 Ist alles gepusht?

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo && git status --short \
  && git log origin/master..HEAD --oneline
```

Beide Ausgaben müssen **leer** sein. Steht dort etwas, erst committen und pushen.

## 0.2 Rescuezilla-Abbild - der Rückweg

Ohne Abbild gibt es keinen Weg zurück zum heutigen Stand. Vom Rescuezilla-Stick booten, „Backup" wählen, Ziel ist die externe Platte. Dauer etwa 30 bis 45 Minuten.

## 0.3 Was nicht im Repository liegt - und liegen darf

Diese Dinge gehören **bewusst** nicht ins öffentliche Repository und müssen einzeln gesichert werden:

- `~/.config/dialos/persoenliche-daten.txt` - **in beiden Konten**, also auch `/home/nutzer/...`
- Das Thunderbird-Profil mit dem Testkonto: `~/.thunderbird/`
- `~/Dokumente/` (Briefe, PDF-Archiv) und `~/Notizen/`
- Das persönliche Wörterbuch aus `~/.config/dialos/`

Zuerst das Admin-Konto:

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS && tar czf sicherung-admin.tar.gz \
  -C /home/dialosadmin .config/dialos .thunderbird Dokumente Notizen
```

Dann das Nutzerkonto - dafür braucht es `sudo`, weil das Verzeichnis dem anderen Konto gehört:

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS && sudo tar czf sicherung-nutzer.tar.gz \
  -C /home/nutzer .config/dialos
```

Zum Schluss nachsehen, dass beide Dateien wirklich da sind und nicht nur ein paar Kilobyte groß:

```bash
ls -lh /media/dialosadmin/SanDisk-Extreme/DialOS/sicherung-*.tar.gz
```

> **Claudes Gedächtnis geht verloren, und zwar vollständig.** Der Chatverlauf, die Verbindungen der App und das Memory-System liegen auf der internen Platte. Was über den Tag hinaus wichtig ist, muss in `CLAUDE.md`, `TODO.md` oder `docs/` stehen - dort steht es auch.

---

# Teil 1: Debian 13 installieren

Ganz normal vom Debian-Stick booten, **ohne** Sonderzeilen im Startmenü. Die einzige Stelle, an der genau hingesehen werden muss, ist die Partitionierung.

1. Sprache **Deutsch**, Land **Österreich**, Zeitzone **Europe/Vienna** - so läuft das Referenzgerät, und das bleibt so. Für ein Gerät außerhalb Österreichs hier die passende Zeitzone wählen.
2. Netzwerk verbinden (Kabel oder WLAN) - der Installer lädt Pakete nach.
3. **Kein Wurzel-Passwort vergeben.** Bleibt das Feld leer, bekommt das erste Konto `sudo` - genau das wird gebraucht.
4. Das erste Konto heißt **`dialosadmin`** - Buchstabe für Buchstabe: d-i-a-l-o-s-a-d-m-i-n. Dieser Name steht in 30 Dateien, darunter die sudoers-Regeln. Ein anderer Name bricht nicht laut, sondern **lautlos**: Die Regeln greifen einfach nicht. **Vor dem Weiterklicken zweimal lesen** - am 25.09.2026 ist genau hier `dialosadim` entstanden, und der Aufbau musste von vorn beginnen.

## Die Partitionierung - der einzige heikle Schritt

**„Manuell" wählen**, nicht „Geführt". Es werden genau zwei Partitionen angelegt, und der Rest der Platte bleibt **unberührt**:

- **Erste Partition: 538 MB, „EFI-Systempartition".** Den Einbindungspunkt setzt der Installer selbst.
- **Zweite Partition: 100 GB, ext4, Einbindungspunkt `/`.**
- **Der ganze Rest bleibt frei** - nicht anlegen, nicht formatieren.

- **Keinen Swap anlegen.** Der kommt später verschlüsselt dazu, im freien Bereich.
- Warnt der Installer, es sei kein Swap eingerichtet: **bestätigen und weitermachen**.
- Der freie Rest ist der Zweck der Übung: Dort entstehen später der verschlüsselte Swap und `/home/nutzer`. Je größer die Platte, desto mehr Platz bekommt der Nutzer - ohne dass irgendwo eine Zahl anzupassen wäre.

5. Als Desktop **GNOME** wählen.

Nach dem Neustart: anmelden, Netzwerk verbinden, die externe Platte anstecken. Sie hängt dann unter `/media/dialosadmin/SanDisk-Extreme`.

> **Es gibt auch einen Weg ohne Handarbeit** - eine Preseed-Datei gibt dem Installer das Layout vor (`website/d-i/trixie/preseed.cfg`). Sie muss über einfaches HTTP erreichbar sein, und das Zielgerät wird gerade gelöscht, kann sie also nicht selbst ausliefern. Dafür bräuchte es einen **zweiten Rechner** im selben Netz (`./scripts/dialos-preseed-server.sh`). **`dialos.org` taugt nicht dafür** - am 25.09.2026 geprüft: Der Aufruf über HTTP wird auf HTTPS umgeleitet, und dort kommt HTML statt der Datei. Ohne zweiten Rechner sind die drei Punkte oben der Weg; sie nennen dieselben Werte.

---

# Teil 2: Die Claude-App installieren

Ab hier hilft Claude wieder mit - aber erst, wenn die App läuft. **Dieser Teil ist die offizielle Anleitung von Anthropic, Befehl für Befehl:** `code.claude.com/docs/en/desktop-linux`. Nichts ist dazugemischt. Weicht die Seite irgendwann von diesem Blatt ab, gilt die Seite - und dieses Blatt gehört nachgezogen.

> **Warum das so streng ist:** Die ersten beiden Fassungen dieses Teils haben am 25.09.2026 nicht funktioniert. Die erste holte den Schlüssel mit `curl`, bevor `curl` installiert war. Die zweite hatte eigene Zutaten dazugemischt, und im PDF brachen die langen Befehle mitten in der Adresse um. Stephan hat die App dann nach der offiziellen Seite installiert - damit ging es.

> **Lange Befehle stehen hier auf mehreren Zeilen.** Endet eine Zeile mit `\`, gehört die nächste noch zum selben Befehl. Der ganze Block wird **auf einmal** eingefügt (oder abgetippt) und dann einmal mit der Eingabetaste abgeschickt.

## 2.1 Werkzeuge für den Schlüssel

Der Schlüssel wird mit `curl` geladen und mit `gpg` geprüft. Auf einem frischen Debian fehlt mindestens `curl` - deshalb immer zuerst:

```bash
sudo apt install curl gnupg
```

Fragt apt „Möchten Sie fortfahren? [J/n]", mit der Eingabetaste bestätigen.

## 2.2 Den Schlüssel von Anthropic laden

```bash
sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc \
  https://downloads.claude.ai/claude-desktop/key.asc
```

**Klappt es, erscheint gar nichts.** Nur bei einem Fehler steht dort eine Zeile, die mit `curl:` beginnt.

## 2.3 Prüfen, dass der Schlüssel wirklich von Anthropic ist

```bash
gpg --show-keys /usr/share/keyrings/claude-desktop-archive-keyring.asc
```

In der Ausgabe muss dieser Fingerabdruck stehen:

```text
31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE
```

Steht dort etwas anderes, oder meldet gpg, die Datei lasse sich nicht öffnen oder enthalte keine gültigen OpenPGP-Daten: **nicht weitermachen.** Prüfen, ob das Netz steht, und 2.2 wiederholen. Ein fehlender oder falscher Schlüssel fällt sonst erst später auf, als `NO_PUBKEY BAA929FF1A7ECACE` bei `apt update`.

## 2.4 Die Paketquelle eintragen

```bash
echo "deb [arch=amd64,arm64 \
signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] \
https://downloads.claude.ai/claude-desktop/apt/stable stable main" \
  | sudo tee /etc/apt/sources.list.d/claude-desktop.list
```

Das Terminal wiederholt danach die eingetragene Zeile - **eine** lange Zeile, die mit `deb [arch=amd64,arm64 signed-by=` beginnt und mit `stable main` endet. So sieht es richtig aus.

## 2.5 Die App installieren

```bash
sudo apt update && sudo apt install claude-desktop
```

Wieder mit der Eingabetaste bestätigen. Dabei kommen auch QEMU und die Virtualisierungspakete mit - die braucht nur der Cowork-Bereich der App, sie schaden aber nicht.

## 2.6 Starten und anmelden

Übersichtstaste drücken, **„Claude"** eintippen, starten - oder im Terminal `claude-desktop`. Dann mit dem Anthropic-Konto anmelden (claude.ai-Abo). Die App **nie mit `sudo` starten**: Als root bricht sie mit „Running as root without --no-sandbox is not supported" ab.

Das Kommandozeilen-Werkzeug `claude` braucht es an dieser Stelle **nicht** - die App bringt Claude Code mit. `nodejs`, `npm` und `@anthropic-ai/claude-code` installiert das Aufbau-Skript in Teil 4.

## 2.7 Wenn etwas nicht klappt

- **`command not found` bei curl oder gpg:** 2.1 fehlt oder ist abgebrochen - wiederholen.
- **`NO_PUBKEY BAA929FF1A7ECACE` bei `apt update`:** Der Schlüssel fehlt oder ist falsch. 2.2 und 2.3 wiederholen.
- **`E: Unable to locate package claude-desktop`:** apt kennt die Paketquelle nicht. Nachsehen mit `cat /etc/apt/sources.list.d/claude-desktop.list` - dort muss die `deb`-Zeile aus 2.4 stehen. Fehlt sie oder ist die Datei leer: 2.4 wiederholen, dann 2.5.
- **Aktualisiert wird die App später mit dem System** (`sudo apt update && sudo apt upgrade`, oder über die Update-Automatik von DialOS). Sie aktualisiert sich unter Linux nicht selbst.

---

# Teil 3: In der Claude-App - Schritt für Schritt

1. **App starten**, falls sie nicht schon läuft - wie in 2.6.
2. **Anmelden** mit dem üblichen Konto. Das dauert wenige Sekunden - die Anmeldung lässt sich nicht sichern und nicht wiederherstellen, sie wird jedes Mal neu gemacht.
3. **Ordner freigeben:** In der App den Arbeitsordner wählen und auf `/media/dialosadmin/SanDisk-Extreme/DialOS/repo` zeigen. **Ohne diesen Schritt sieht Claude das Repository nicht** - und damit weder die Doku noch die Skripte.
4. **Prüfen, ob es sitzt:** Claude bitten, `CLAUDE.md` zu lesen. Kommt eine Zusammenfassung des Projektstands, ist die Verbindung da.
5. **Den ersten Auftrag geben.** Dieser Satz genügt:

> „Wir bauen das Gerät gerade neu auf. Lies CLAUDE.md und docs/Debian-zu-DialOS.md und sag mir, welcher Schritt als Nächstes dran ist."

6. **GitHub-Zugang einrichten** - das geht nur von Hand, kein Skript und keine KI kann es übernehmen. Zuerst `git`, das ein frisches Debian nicht mitbringt (das Aufbau-Skript installiert es erst in Teil 4, gebraucht wird es hier):

```bash
sudo apt install git
```

Dann das Einrichtungs-Skript - **mit `sudo`**, und danach der erste Push **ohne** `sudo` (er fragt nach Benutzername und Token):

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo \
  && sudo ./scripts/dialos-claude-setup.sh && git push
```

> **Hier stand bis zum 25.09.2026 der Aufruf ohne `sudo`** - das Skript bricht dann sofort mit „Bitte mit sudo ausfuehren" ab. Es braucht root, weil es eine alte sudoers-Datei entfernt; die Git-Einstellungen trägt es trotzdem für `dialosadmin` ein, nicht für root.

Das Skript legt den Symlink `~/DialOS`, trägt Name und E-Mail für Git ein und schaltet den Zugangsdaten-Speicher an. Beim **ersten** `git push` fragt Git einmalig nach Benutzername und Token; danach merkt es sich beides.

> **Die Verbindungen der App selbst - Ordner-Connector und GitHub-Integration - lassen sich nicht sichern.** Es gibt dafür keinen Wiederherstellungsweg, weder per Skript noch in der App. Sie werden nach jeder Neuinstallation neu eingerichtet; deshalb steht Schritt 3 hier so ausführlich.

---

# Teil 4: DialOS aufbauen - drei Befehle

Die Reihenfolge und das `sudo` sind nicht beliebig. Der erste Befehl richtet Dateien im Heimatverzeichnis ein, der zweite braucht die grafische Umgebung für seine Dialoge - beide laufen deshalb **ohne** `sudo`.

## 4.1 Grundaufbau (ohne sudo)

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo && ./scripts/dialos-full-office-setup.sh
```

Das dauert am längsten: Pakete, Branding, Autologin, Piper-Sprachausgabe, GNOME-Erweiterungen, Vosk, Parakeet, LanguageTool - und seit dem 25.09.2026 als **Schritt 16** das Aufspielen aller DialOS-Dateien über `dialos-aufspielen`, das Einschalten der Dienste für **alle** Konten und den Bau der Thunderbird-Erweiterung.

## 4.2 Verschlüsseltes Heimatverzeichnis (ohne sudo, Stick stecken)

> **Der Stick wird dabei KOMPLETT gelöscht - beide Bereiche, auch `DIALOS-DATA` mit dem PDF-Archiv des Nutzers.** Ist es ein schon benutzter Stick, vorher den Ordner `DialOS-Archiv/` darauf auf die externe Platte kopieren. Der alte Schlüssel darauf ist nach dem Neuaufbau ohnehin wertlos.

> **Eingehängte Laufwerke bietet das Skript seit dem 25.09.2026 nicht mehr an.** Vorher stand die externe Arbeitsplatte gleichrangig neben dem Stick in der Liste - ein Klick daneben hätte Repository, Rescuezilla-Abbild und Sicherungen gelöscht. Hängt GNOME den Stick beim Anstecken selbst ein (bei einem alten Stick passiert das mit `DIALOS-DATA`), ihn in der Dateiverwaltung **auswerfen** (nicht abziehen), sonst steht er nicht zur Wahl.

Erst den Stick `DIALOS-KEY` anstecken, dann:

```bash
/usr/local/sbin/dialos-setup-home-partition.sh
```

Das Skript holt sich die Rechte selbst über `pkexec`. Unter `sudo` fehlt ihm die grafische Umgebung, und es bricht ohne verständliche Meldung ab.

## 4.3 Nutzerkonto und Abschluss (mit sudo, Stick stecken lassen)

```bash
sudo ./scripts/dialos-buero-setup-abschliessen.sh dialosadmin
```

Legt `nutzer` an, richtet das Autologin ein, setzt den Frageton für `nutzer`, öffnet die Maske für die persönlichen Daten und prüft am Ende selbst nach, ob Gerät und Repository übereinstimmen und im Nutzerkonto nichts fehlt.

Danach **einmal neu starten**.

---

# Teil 5: Was nur von Hand geht

Alles hier braucht Zugangsdaten oder ein Urteil - beides kann kein Skript liefern.

- **Persönliche Daten** für beide Konten in der Maske ausfüllen: Name, Anschrift, Telefon, E-Mail, Ort fürs Wetter. Ohne sie hat der Brief keinen Absender und das Wetter keinen Ort.
- **Thunderbird einrichten**: Konto anlegen, Passwort eintippen. Die DialOS-Brücke wird dabei **von selbst** installiert, weil sie über `policies.json` in jedes Profil kommt.
- **Stimme wählen**: Michael oder Anna, mit `Strg`+`Alt`+`S` umschalten. Die Wahl bleibt beim Aufspielen unangetastet.
- **Bluetooth-Lautsprecher** koppeln, falls verwendet.
- **GitHub-Token** beim ersten `git push` eintippen (siehe Teil 3).

---

# Teil 6: Abnahme

Ein Aufbau, der durchläuft, beweist noch nicht, dass er vollständig war.

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo \
  && ./scripts/dialos-installstand.sh --befehl
```

Erwartet wird: nur die bewussten Ausnahmen weichen ab - die gewählte Stimme, die Bluetooth-Kopplung und die zurückgestellte Fernwartung.

```bash
sudo /media/dialosadmin/SanDisk-Extreme/DialOS/repo/scripts/dialos-nutzerkonto-pruefen.sh
```

Erwartet wird: nichts fehlt. Solange in `nutzer` noch kein Mailkonto eingerichtet ist, meldet es „noch kein Thunderbird-Profil" - das ist kein Mangel.

**Zum Schluss die Stimme selbst:** Am Nutzerkonto anmelden und sprechen.

- „Sprachsteuerung starten" → „Ich höre Dir zu."
- „Wie spät ist es" → Uhrzeit
- „Postfach öffnen" → Thunderbird startet
- „Brief schreiben" → der Empfängerdialog beginnt

Läuft das, ist das Gerät fertig.

---

# Teil 7: Wenn etwas schiefgeht

- **Die Partitionierung sieht anders aus als erwartet:** Im Installer zurückgehen und die Partitionstabelle prüfen - es dürfen nur die EFI- und die 100-GB-Partition angelegt sein, der Rest muss als „FREIER SPEICHER" dastehen. Ist die ganze Platte belegt, findet Teil 4.2 später keinen Platz für `/home/nutzer`.
- **Ein Aufbau-Skript bricht ab:** Es lässt sich einzeln fortsetzen, zum Beispiel `./scripts/dialos-full-office-setup.sh 15_vosk`. Die Schrittnamen stehen im Skript unter `ALLE_SCHRITTE`.
- **Die Sprachsteuerung reagiert nicht:** Nach dem Aufspielen neuer Sätze einmal ab- und anmelden - die Grammatik wird beim Start gelesen. Protokolle liegen in `~/.log/`.
- **Beim Kontonamen vertippt** (am 25.09.2026 passiert: `dialosadim`): Der sichere Weg ist, Teil 1 **noch einmal** zu machen - so wurde es am 25.09.2026 auch entschieden. Solange außer der Claude-App nichts eingerichtet ist, kostet das nur eine halbe Stunde. Umbenennen über ein Hilfskonto (`usermod -l`, `groupmod -n`) ginge auch, ist aber **nie erprobt** und deshalb hier nicht als Anleitung aufgeführt.
- **Alles zurück:** Vom Rescuezilla-Stick booten und das Abbild aus Teil 0 zurückspielen.

> **Jeder Handgriff, der in dieser Anleitung fehlt, ist eine Lücke - kein Missgeschick.** Beim Neuaufbau am 25.09.2026 war die Anleitung selbst der Prüfling. Was von Hand nachgeholt werden musste, gehört sofort hier hinein und in `docs/Debian-zu-DialOS.md`.
