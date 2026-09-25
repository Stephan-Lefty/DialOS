#!/usr/bin/python3
"""DialOS: Eingabemaske fuer die persoenlichen Daten - auch fuer andere Konten.

Stephan am 2026-09-16: "Koennen wir eine richtige Eingabemaske erstellen, in der
man dann die ~/.config/dialos/persoenliche-daten.txt Datei befuellt. Auch die
von einem Nutzer, den ich einrichte?" - und: "Diese Maske muss fester
Bestandteil der Einrichtung von DialOS auf einem neuen Rechner sein."

FUER DEN SEHENDEN HELFER, nicht fuer den blinden Nutzer: Wer das Geraet
einrichtet, fuellt hier aus. Deshalb im Menue nur des Admin-Kontos (das
Nutzerkonto zeigt nur, was in dialos-menue-pro-konto.sh freigegeben ist).

DIE MASKE BAUT SICH AUS DER VORLAGE (persoenliche-daten-vorlage.txt):
Abschnitte, Reihenfolge und Hinweise stehen dort und nur dort, gelesen ueber
dialos-persoenliche-daten.py. Ein neues Feld in Vorlage und FELDER erscheint
hier von selbst. Gespeichert wird die Vorlage mit eingesetzten Werten - die
Datei bleibt also auch von Hand lesbar und bearbeitbar.

ANDERE KONTEN UEBER pkexec: Die Maske laeuft nie als root. Lesen und Schreiben
im fremden Konto macht /usr/local/sbin/dialos-persoenliche-daten-konto, das nur
diese eine Datei anfasst, ALS das Konto schreibt und sich weigert, wenn die
verschluesselte Partition nicht eingehaengt ist.

Aufruf:  dialos-persoenliche-daten-maske.py [--konto NAME]
"""

import importlib.util
import os
import pwd
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402

HIER = os.path.dirname(os.path.abspath(__file__))
# Neben der Maske zuerst: installiert ist das /usr/local/bin, im Repo die
# Arbeitskopie - so prueft man die Maske nie gegen ein altes Modul.
MODUL = os.path.join(HIER, "dialos-persoenliche-daten.py")
VORLAGE_DANEBEN = os.path.normpath(os.path.join(HIER, "..", "share", "dialos",
                                                "persoenliche-daten-vorlage.txt"))
HELFER = "/usr/local/sbin/dialos-persoenliche-daten-konto"
MAILKONTO = os.path.join(HIER, "dialos-mailkonto.py")
# In diesem Abschnitt der Vorlage steht das Passwortfeld (es selbst steht nie
# in der Datei - siehe dialos-mailkonto.py).
MAIL_ABSCHNITT = "E-Mail-Konto"
# Feste Auswahl statt Freitext, wo es nur wenige richtige Werte gibt.
AUSWAHL = {"anrede": ("", "Herr", "Frau"), "ansprache": ("", "Du", "Sie")}
LEER = "–"


def modul_laden():
    if not os.path.exists(MODUL):
        raise SystemExit(f"{MODUL} fehlt")
    spec = importlib.util.spec_from_file_location("persoenliche_daten", MODUL)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    if os.path.exists(VORLAGE_DANEBEN):
        modul.VORLAGE = VORLAGE_DANEBEN
    return modul


def personenkonten():
    """Echte Anmeldekonten, das eigene zuerst."""
    eigenes = pwd.getpwuid(os.getuid()).pw_name
    konten = [e.pw_name for e in pwd.getpwall()
              if 1000 <= e.pw_uid < 60000 and not e.pw_shell.endswith(("nologin", "false"))]
    return [eigenes] + sorted(k for k in konten if k != eigenes)


class Fenster(Adw.ApplicationWindow):
    def __init__(self, app, pd, konto_start):
        super().__init__(application=app, title="Persönliche Daten – DialOS")
        self.set_default_size(760, 900)
        self.pd = pd
        self.eigenes = pwd.getpwuid(os.getuid()).pw_name
        self.konten = personenkonten()
        self.konto = None
        self.unbekannt = []
        self.geaendert = False
        self.laedt = False
        self.felder = {}

        self.toasts = Adw.ToastOverlay()
        ansicht = Adw.ToolbarView()
        kopf = Adw.HeaderBar()
        ansicht.add_top_bar(kopf)

        beschriftungen = [f"{k} (dieses Konto)" if k == self.eigenes else k for k in self.konten]
        self.kontowahl = Gtk.DropDown.new_from_strings(beschriftungen)
        self.kontowahl.set_tooltip_text("Für welches Konto die Daten gelten")
        self.kontowahl.update_property([Gtk.AccessibleProperty.LABEL], ["Konto"])
        kopf.pack_start(self.kontowahl)

        self.speichern_knopf = Gtk.Button(label="Speichern")
        self.speichern_knopf.add_css_class("suggested-action")
        self.speichern_knopf.connect("clicked", lambda *_: self.speichern())
        kopf.pack_end(self.speichern_knopf)

        seite = Adw.PreferencesPage()
        kopfgruppe = Adw.PreferencesGroup(
            title="Persönliche Daten",
            description="Diese Angaben nutzt DialOS für Absender und Unterschrift im Brief, "
                        "für den Namen in den Ansagen und für das Wetter. Was nicht zutrifft, "
                        "bleibt leer. Pflichtfelder sind mit * markiert.")
        self.status = Adw.ActionRow(title="Datei")
        self.status.set_subtitle_selectable(True)
        kopfgruppe.add(self.status)
        seite.add(kopfgruppe)

        for abschnitt, felder in pd.aufbau():
            gruppe = Adw.PreferencesGroup(title=abschnitt)
            for schluessel, feld, pflicht, hinweis in felder:
                titel = feld + (" *" if pflicht else "")
                zeile = Adw.ActionRow(title=titel)
                if hinweis:
                    zeile.set_subtitle(hinweis)
                if schluessel in AUSWAHL:
                    eingabe = Gtk.DropDown.new_from_strings(
                        [w or LEER for w in AUSWAHL[schluessel]])
                    eingabe.connect("notify::selected", lambda *_: self.aendern())
                else:
                    eingabe = Gtk.Entry()
                    # Feste Breite: Alle Felder enden buendig, statt je nach Laenge
                    # der Beschriftung verschieden breit zu sein.
                    eingabe.set_width_chars(32)
                    eingabe.connect("changed", lambda *_: self.aendern())
                    eingabe.connect("activate", lambda *_: self.speichern())
                eingabe.set_valign(Gtk.Align.CENTER)
                eingabe.update_property([Gtk.AccessibleProperty.LABEL], [feld])
                if hinweis:
                    eingabe.update_property([Gtk.AccessibleProperty.DESCRIPTION], [hinweis])
                    eingabe.set_tooltip_text(hinweis)
                zeile.add_suffix(eingabe)
                zeile.set_activatable_widget(eingabe)
                gruppe.add(zeile)
                self.felder[schluessel] = eingabe
            if abschnitt == MAIL_ABSCHNITT:
                gruppe.add(self.passwortzeile())
            seite.add(gruppe)

        ansicht.set_content(seite)
        self.toasts.set_child(ansicht)
        self.set_content(self.toasts)

        self.kontowahl.connect("notify::selected", lambda *_: self.konto_gewechselt())
        self.connect("close-request", self.schliessen_pruefen)
        start = konto_start if konto_start in self.konten else self.eigenes
        self.kontowahl.set_selected(self.konten.index(start))
        if self.konten.index(start) == 0:
            self.konto_gewechselt()

    def passwortzeile(self):
        """Verdecktes Feld - wird NIE gespeichert, nur an Thunderbird weitergegeben."""
        zeile = Adw.ActionRow(title="Mail-Passwort")
        hinweis = ("Nur ausfüllen, wenn das Thunderbird-Konto jetzt angelegt oder das "
                   "Passwort geändert werden soll. Wird nicht in der Datei gespeichert, "
                   "sondern direkt in Thunderbirds verschlüsseltem Passwortspeicher. "
                   "Thunderbird muss dafür geschlossen sein.")
        zeile.set_subtitle(hinweis)
        self.passwort = Gtk.PasswordEntry(show_peek_icon=True)
        self.passwort.set_width_chars(32)
        self.passwort.set_valign(Gtk.Align.CENTER)
        self.passwort.update_property([Gtk.AccessibleProperty.LABEL], ["Mail-Passwort"])
        self.passwort.update_property([Gtk.AccessibleProperty.DESCRIPTION], [hinweis])
        self.passwort.connect("activate", lambda *_: self.speichern())
        zeile.add_suffix(self.passwort)
        zeile.set_activatable_widget(self.passwort)
        return zeile

    # ------------------------------------------------------------ Werte
    def aendern(self):
        if not self.laedt:
            self.geaendert = True

    def werte_holen(self):
        daten = {}
        for schluessel, eingabe in self.felder.items():
            if isinstance(eingabe, Gtk.DropDown):
                wert = AUSWAHL[schluessel][eingabe.get_selected()]
            else:
                wert = " ".join(eingabe.get_text().split())
            if wert:
                daten[schluessel] = wert
        return daten

    def werte_setzen(self, daten):
        self.laedt = True
        for schluessel, eingabe in self.felder.items():
            wert = daten.get(schluessel, "")
            if isinstance(eingabe, Gtk.DropDown):
                werte = AUSWAHL[schluessel]
                eingabe.set_selected(werte.index(wert) if wert in werte else 0)
            else:
                eingabe.set_text(wert)
        self.laedt = False
        self.geaendert = False

    def pfad_von(self, konto):
        return os.path.join(pwd.getpwnam(konto).pw_dir, ".config", "dialos",
                            "persoenliche-daten.txt")

    # ------------------------------------------------------------ Konto
    def konto_gewechselt(self):
        neu = self.konten[self.kontowahl.get_selected()]
        if neu == self.konto:
            return
        if self.geaendert and self.konto is not None:
            self.fragen("Änderungen verwerfen?",
                        f"Die Angaben für {self.konto} sind noch nicht gespeichert.",
                        "verwerfen", "Verwerfen",
                        lambda: self.laden(neu),
                        lambda: self.auswahl_zuruecksetzen())
            return
        self.laden(neu)

    def auswahl_zuruecksetzen(self):
        if self.konto in self.konten:
            self.laedt = True
            self.kontowahl.set_selected(self.konten.index(self.konto))
            self.laedt = False

    def laden(self, konto):
        pfad = self.pfad_von(konto)
        if konto == self.eigenes:
            self.unbekannt = []
            try:
                with open(pfad, encoding="utf-8") as f:
                    text = f.read()
                vorhanden = True
            except OSError:
                text, vorhanden = "", False
            self.geladen(konto, text, vorhanden)
            return
        self.set_sensitive(False)
        self.melden("Frage nach dem Administrator-Passwort …")
        prozess = Gio.Subprocess.new(["pkexec", HELFER, "lesen", konto],
                                     Gio.SubprocessFlags.STDOUT_PIPE
                                     | Gio.SubprocessFlags.STDERR_PIPE)
        prozess.communicate_utf8_async(None, None, self.fremd_gelesen, konto)

    def fremd_gelesen(self, prozess, ergebnis, konto):
        self.set_sensitive(True)
        try:
            _, ausgabe, fehler = prozess.communicate_utf8_finish(ergebnis)
        except GLib.Error as e:
            self.fehler_zeigen("Lesen fehlgeschlagen", e.message)
            self.auswahl_zuruecksetzen()
            return
        code = prozess.get_exit_status()
        if code == 0:
            self.geladen(konto, ausgabe or "", True)
        elif code == 4:
            self.geladen(konto, "", False)
        elif code in (126, 127):
            self.melden("Abgebrochen – kein Zugriff auf das andere Konto.")
            self.auswahl_zuruecksetzen()
        else:
            self.fehler_zeigen(f"Die Daten von {konto} lassen sich nicht lesen",
                               (fehler or "").strip() or f"Rückgabewert {code}")
            self.auswahl_zuruecksetzen()

    def geladen(self, konto, text, vorhanden):
        unbekannt = []
        daten = self.pd.aus_text(text, unbekannt)
        self.unbekannt = [z[2] for z in unbekannt]
        self.konto = konto
        self.werte_setzen(daten)
        pfad = self.pfad_von(konto)
        self.status.set_title(f"Konto {konto}")
        self.status.set_subtitle(pfad if vorhanden else f"{pfad} – noch nicht angelegt")
        if not vorhanden:
            self.melden(f"Für {konto} gibt es noch keine Daten – jetzt ausfüllen.")

    # ------------------------------------------------------------ Speichern
    def speichern(self):
        if self.konto is None:
            return
        daten = self.werte_holen()
        meldungen = self.pd.pruefen(daten, [])
        if meldungen:
            self.fragen("Noch nicht vollständig", "\n".join(meldungen),
                        "speichern", "Trotzdem speichern", lambda: self.schreiben(daten))
            return
        self.schreiben(daten)

    def schreiben(self, daten):
        text = self.pd.als_text(daten, unbekannte_zeilen=self.unbekannt)
        konto = self.konto
        if konto == self.eigenes:
            pfad = self.pfad_von(konto)
            try:
                alt = os.umask(0o077)
                try:
                    os.makedirs(os.path.dirname(pfad), exist_ok=True)
                    with open(pfad + ".neu", "w", encoding="utf-8") as f:
                        f.write(text)
                    os.chmod(pfad + ".neu", 0o600)
                    os.replace(pfad + ".neu", pfad)
                finally:
                    os.umask(alt)
            except OSError as e:
                self.fehler_zeigen("Speichern fehlgeschlagen", str(e))
                return
            self.gespeichert(konto)
            return
        self.set_sensitive(False)
        prozess = Gio.Subprocess.new(["pkexec", HELFER, "schreiben", konto],
                                     Gio.SubprocessFlags.STDIN_PIPE
                                     | Gio.SubprocessFlags.STDERR_PIPE)
        prozess.communicate_utf8_async(text, None, self.fremd_geschrieben, konto)

    def fremd_geschrieben(self, prozess, ergebnis, konto):
        self.set_sensitive(True)
        try:
            _, _, fehler = prozess.communicate_utf8_finish(ergebnis)
        except GLib.Error as e:
            self.fehler_zeigen("Speichern fehlgeschlagen", e.message)
            return
        code = prozess.get_exit_status()
        if code == 0:
            self.gespeichert(konto)
        elif code in (126, 127):
            self.melden("Nicht gespeichert – das Passwort wurde nicht bestätigt.")
        else:
            self.fehler_zeigen(f"Für {konto} nicht gespeichert",
                               (fehler or "").strip() or f"Rückgabewert {code}")

    def gespeichert(self, konto):
        self.geaendert = False
        self.status.set_subtitle(self.pfad_von(konto))
        self.melden(f"Gespeichert für {konto}.")
        # VERTEILEN: Steht ein Passwort im Feld, geht das Mailkonto nach
        # Thunderbird. Ohne Passwort bleibt Thunderbird unberuehrt - sonst
        # muesste es bei jedem Speichern (etwa einer neuen Telefonnummer)
        # geschlossen sein.
        passwort = self.passwort.get_text() if hasattr(self, "passwort") else ""
        if passwort:
            self.mailkonto_einrichten(konto, passwort)

    def mailkonto_einrichten(self, konto, passwort):
        if konto == self.eigenes:
            befehl = [MAILKONTO, "einrichten", "--passwort-stdin"]
        else:
            befehl = ["pkexec", HELFER, "mailkonto", konto]
        self.set_sensitive(False)
        self.melden("Richte das Mailkonto in Thunderbird ein …")
        prozess = Gio.Subprocess.new(befehl, Gio.SubprocessFlags.STDIN_PIPE
                                     | Gio.SubprocessFlags.STDOUT_PIPE
                                     | Gio.SubprocessFlags.STDERR_PIPE)
        prozess.communicate_utf8_async(passwort + "\n", None, self.mailkonto_fertig, konto)

    def mailkonto_fertig(self, prozess, ergebnis, konto):
        self.set_sensitive(True)
        try:
            _, ausgabe, fehler = prozess.communicate_utf8_finish(ergebnis)
        except GLib.Error as e:
            self.fehler_zeigen("Mailkonto nicht eingerichtet", e.message)
            return
        code = prozess.get_exit_status()
        if code == 0:
            self.passwort.set_text("")
            self.fehler_zeigen(f"Mailkonto für {konto} eingerichtet",
                               (ausgabe or "").strip())
        elif code in (126, 127):
            self.melden("Mailkonto nicht eingerichtet – das Passwort wurde nicht bestätigt.")
        else:
            self.fehler_zeigen(f"Mailkonto für {konto} nicht eingerichtet",
                               (fehler or "").strip() or f"Rückgabewert {code}")

    # ------------------------------------------------------------ Dialoge
    def melden(self, text):
        self.toasts.add_toast(Adw.Toast(title=text, timeout=4))

    def fehler_zeigen(self, titel, text):
        dialog = Adw.AlertDialog(heading=titel, body=text)
        dialog.add_response("ok", "OK")
        dialog.present(self)

    def fragen(self, titel, text, antwort, beschriftung, ja, nein=None):
        dialog = Adw.AlertDialog(heading=titel, body=text)
        dialog.add_response("zurueck", "Zurück")
        dialog.add_response(antwort, beschriftung)
        dialog.set_response_appearance(
            antwort, Adw.ResponseAppearance.DESTRUCTIVE if antwort == "verwerfen"
            else Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("zurueck")
        dialog.set_close_response("zurueck")

        def beantwortet(_, gewaehlt):
            if gewaehlt == antwort:
                ja()
            elif nein:
                nein()
        dialog.connect("response", beantwortet)
        dialog.present(self)

    def schliessen_pruefen(self, *_):
        if not self.geaendert:
            return False
        self.fragen("Ohne Speichern schließen?", "Die Änderungen gehen verloren.",
                    "verwerfen", "Schließen", self.erzwungen_schliessen)
        return True

    def erzwungen_schliessen(self):
        self.geaendert = False
        self.close()


def main():
    konto = None
    if "--konto" in sys.argv:
        i = sys.argv.index("--konto")
        konto = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
    pd = modul_laden()
    app = Adw.Application(application_id="org.dialos.PersoenlicheDaten",
                          flags=Gio.ApplicationFlags.NON_UNIQUE)
    app.connect("activate", lambda a: Fenster(a, pd, konto).present())
    return app.run([sys.argv[0]])


if __name__ == "__main__":
    sys.exit(main())
