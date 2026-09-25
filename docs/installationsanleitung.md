# DialOS von Null aufbauen

Diese Anleitung führt ein leeres ThinkPad zu einem fertigen DialOS - beide Konten, `dialosadmin` und `nutzer`. Sie ist für den Fall geschrieben, dass **kein Rechner zur Hand ist, der noch etwas weiß**: Während der Installation ist die Platte leer, die Claude-App ist weg, und auch der bisherige Gesprächsverlauf existiert nicht mehr.

> **Diese Anleitung vor dem Anfangen ausdrucken oder auf ein zweites Gerät legen.** Sie liegt auf derselben Platte, die während der Installation gebraucht wird - am Zielgerät ist sie dann nicht lesbar.

**Stand:** 25.09.2026, nachmittags · **Zeit:** ein halber Tag, davon viel Wartezeit · **Grundlage:** `docs/Debian-zu-DialOS.md` im Repo. Diese Anleitung ist die Kurzform für den Handgriff; das Rezept dort erklärt jeden Schritt und begründet ihn.

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
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo && git status --short && git log origin/master..HEAD --oneline
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
cd /media/dialosadmin/SanDisk-Extreme/DialOS && tar czf sicherung-admin.tar.gz -C /home/dialosadmin .config/dialos .thunderbird Dokumente Notizen
```

Dann das Nutzerkonto - dafür braucht es `sudo`, weil das Verzeichnis dem anderen Konto gehört:

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS && sudo tar czf sicherung-nutzer.tar.gz -C /home/nutzer .config/dialos
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
4. Das erste Konto heißt **`dialosadmin`**. Dieser Name steht in Skripten und Doku; ein anderer Name bricht beides.

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

Ab hier hilft Claude wieder mit - aber erst, wenn die App läuft. Die drei Befehle stehen nirgends sonst; sie stammen aus der Befehlsgeschichte des bisherigen Geräts.

## 2.1 Paketquelle und Schlüssel

```bash
sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
```

```bash
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list
```

## 2.2 App installieren

```bash
sudo apt update && sudo apt install -y curl claude-desktop
```

Fehlt `curl` noch, vorher `sudo apt install -y curl` - auf einer frischen Debian-Installation ist es nicht immer dabei.

## 2.3 Claude Code auf der Kommandozeile

Die App bringt die Oberfläche, das Kommandozeilen-Werkzeug kommt über npm:

```bash
sudo apt install -y nodejs npm && sudo npm install -g @anthropic-ai/claude-code
```

> **`sudo` ist hier Pflicht:** Debians npm schreibt nach `/usr/local`, und dort darf `dialosadmin` nicht schreiben. Ohne `sudo` bricht es mit `EACCES` ab.

---

# Teil 3: In der Claude-App - Schritt für Schritt

1. **App starten**: Übersichtstaste drücken, „Claude" eintippen, starten.
2. **Anmelden** mit dem üblichen Konto. Das dauert wenige Sekunden - die Anmeldung lässt sich nicht sichern und nicht wiederherstellen, sie wird jedes Mal neu gemacht.
3. **Ordner freigeben:** In der App den Arbeitsordner wählen und auf `/media/dialosadmin/SanDisk-Extreme/DialOS/repo` zeigen. **Ohne diesen Schritt sieht Claude das Repository nicht** - und damit weder die Doku noch die Skripte.
4. **Prüfen, ob es sitzt:** Claude bitten, `CLAUDE.md` zu lesen. Kommt eine Zusammenfassung des Projektstands, ist die Verbindung da.
5. **Den ersten Auftrag geben.** Dieser Satz genügt:

> „Wir bauen das Gerät gerade neu auf. Lies CLAUDE.md und docs/Debian-zu-DialOS.md und sag mir, welcher Schritt als Nächstes dran ist."

6. **GitHub-Zugang einrichten** - das geht nur von Hand, kein Skript und keine KI kann es übernehmen:

```bash
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo && ./scripts/dialos-claude-setup.sh
```

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
cd /media/dialosadmin/SanDisk-Extreme/DialOS/repo && ./scripts/dialos-installstand.sh --befehl
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
- **Alles zurück:** Vom Rescuezilla-Stick booten und das Abbild aus Teil 0 zurückspielen.

> **Jeder Handgriff, der in dieser Anleitung fehlt, ist eine Lücke - kein Missgeschick.** Beim Neuaufbau am 25.09.2026 war die Anleitung selbst der Prüfling. Was von Hand nachgeholt werden musste, gehört sofort hier hinein und in `docs/Debian-zu-DialOS.md`.
