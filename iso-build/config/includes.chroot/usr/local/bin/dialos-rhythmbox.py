#!/usr/bin/env python3
"""
DialOS-Rhythmbox - Sender auswaehlen, pruefen und zur Medienliste machen.

Holt Sender aus Deutschland, Oesterreich und der Schweiz von
radio-browser.info, testet sie an und macht daraus die Medienliste fuer
DialOS - wahlweise auch gleich Eintraege in Rhythmbox. Die Arbeit selbst
macht dialos_rhythmbox_sender.py, das im selben Verzeichnis liegen muss.

Start:  ./dialos-rhythmbox.py
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gst", "1.0")

from gi.repository import Adw, Gdk, Gio, GLib, Gst, Gtk  # noqa: E402

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))

import dialos_farben as farben  # noqa: E402
import dialos_rhythmbox_sender as rs  # noqa: E402

APP_ID = "org.dialos.Rhythmbox"
ZWISCHENSPEICHER = Path(GLib.get_user_cache_dir()) / "dialos-rhythmbox" / "sender.json"

CSS = f"""
.sender-liste row {{
  padding: 2px 0;
}}
.zustand-ok    {{ color: {farben.GRUEN}; font-weight: bold; }}
.zustand-tot   {{ color: {farben.ROT};   font-weight: bold; }}
.zustand-offen {{ color: {farben.GRAU_LEISE}; }}
.zustand-zweifel {{ color: {farben.BLAU_TIEF}; }}
.kopfzeile {{ font-weight: bold; }}
.sprechform-doppelt entry {{
  background-color: {farben.ROT};
  color: {farben.WEISS};
}}
.warnung {{ color: {farben.ROT}; font-weight: bold; }}
"""


def im_hauptfaden(funktion, *args):
    """GTK darf nur aus dem Hauptfaden heraus angefasst werden."""
    GLib.idle_add(funktion, *args, priority=GLib.PRIORITY_DEFAULT)


# --------------------------------------------------------------- Senderzeile

class SenderZeile(Adw.ActionRow):
    """Eine Zeile: Haken zum Auswaehlen, Name, Zustand, Vorhoeren."""

    def __init__(self, sender: dict, fenster: "Fenster") -> None:
        super().__init__()
        self.sender = sender
        self.fenster = fenster

        self.set_title(GLib.markup_escape_text(sender["name"]))
        self.set_subtitle(self._untertitel())
        self.set_activatable(True)

        self.haken = Gtk.CheckButton(active=False)
        self.haken.set_valign(Gtk.Align.CENTER)
        self.haken.set_tooltip_text("Diesen Sender in die Medienliste aufnehmen")
        self.haken.update_property(
            [Gtk.AccessibleProperty.LABEL], [f"{sender['name']} aufnehmen"])
        self.haken.connect("toggled", lambda *_: fenster.auswahl_geaendert())
        self.add_prefix(self.haken)
        self.set_activatable_widget(self.haken)

        # Die Sprechform ist der Satz, den der Nutzer spricht. Der Vorschlag
        # ist nur ein Vorschlag - hier wird er nachgebessert.
        sender.setdefault("sprechform", rs.sprechform_vorschlag(sender["name"]))
        self.sprechform = Gtk.Entry(text=sender["sprechform"])
        self.sprechform.set_valign(Gtk.Align.CENTER)
        self.sprechform.set_width_chars(20)
        self.sprechform.set_max_width_chars(20)
        self.sprechform.set_tooltip_text(
            "So sagt man es - klein, Zahlen als Wort")
        self.sprechform.update_property(
            [Gtk.AccessibleProperty.LABEL],
            [f"Sprechform fuer {sender['name']}"])
        self.sprechform.connect("changed", self._sprechform_geaendert)
        self.add_suffix(self.sprechform)

        self.zustand = Gtk.Label(label="ungeprueft")
        self.zustand.add_css_class("zustand-offen")
        self.zustand.set_valign(Gtk.Align.CENTER)
        self.zustand.set_width_chars(16)
        self.zustand.set_xalign(1.0)
        self.add_suffix(self.zustand)

        self.hoeren = Gtk.ToggleButton(icon_name="media-playback-start-symbolic")
        self.hoeren.set_valign(Gtk.Align.CENTER)
        self.hoeren.add_css_class("flat")
        self.hoeren.set_tooltip_text("Vorhoeren")
        self.hoeren.update_property(
            [Gtk.AccessibleProperty.LABEL], [f"{sender['name']} vorhoeren"])
        self.hoeren.connect("toggled", self._vorhoeren)
        self.add_suffix(self.hoeren)

    def _untertitel(self) -> str:
        s = self.sender
        teile = [t for t in (s.get("codec"), f"{s['bitrate']} kbit/s"
                             if s.get("bitrate") else None) if t]
        return GLib.markup_escape_text(" - ".join(teile) or s["url"][:60])

    def _sprechform_geaendert(self, eingabe: Gtk.Entry) -> None:
        self.sender["sprechform"] = eingabe.get_text().strip()
        self.fenster.auswahl_geaendert()

    def doppelt_markieren(self, doppelt: bool, grund: str = "") -> None:
        if doppelt:
            self.sprechform.add_css_class("sprechform-doppelt")
            self.sprechform.set_tooltip_text(grund)
        else:
            self.sprechform.remove_css_class("sprechform-doppelt")
            self.sprechform.set_tooltip_text(
                "So sagt man es - klein, Zahlen als Wort")

    def _vorhoeren(self, knopf: Gtk.ToggleButton) -> None:
        if knopf.get_active():
            self.fenster.abspielen(self.sender, self)
        else:
            self.fenster.anhalten()

    def hoeren_aus(self) -> None:
        """Von aussen zuruecksetzen, wenn ein anderer Sender uebernimmt."""
        self.hoeren.handler_block_by_func(self._vorhoeren)
        self.hoeren.set_active(False)
        self.hoeren.handler_unblock_by_func(self._vorhoeren)

    def zustand_zeigen(self) -> None:
        s = self.sender
        for klasse in ("zustand-ok", "zustand-tot", "zustand-offen",
                       "zustand-zweifel"):
            self.zustand.remove_css_class(klasse)

        if not s.get("laeuft"):
            self.zustand.set_text("nicht erreichbar")
            self.zustand.add_css_class("zustand-tot")
            self.zustand.set_tooltip_text(s.get("problem") or "")
            self.haken.set_active(False)
            return

        if s.get("namenszweifel"):
            self.zustand.set_text("Name pruefen")
            self.zustand.add_css_class("zustand-zweifel")
            self.zustand.set_tooltip_text(
                f"Der Sender meldet sich als: {s.get('icy')}")
            return

        audio = s.get("audio")
        self.zustand.set_text(f"{audio['kbps']} kbit/s" if audio and audio.get("kbps")
                              else "laeuft")
        self.zustand.add_css_class("zustand-ok")
        if audio and audio.get("laeuft"):
            self.zustand.set_tooltip_text(f"Gerade: {audio['laeuft']}")


# ------------------------------------------------------------------- Fenster

class Fenster(Adw.ApplicationWindow):

    def __init__(self, app: Adw.Application) -> None:
        super().__init__(application=app, title="DialOS-Rhythmbox")
        self.set_default_size(820, 700)
        self.set_icon_name(APP_ID)

        self.zeilen: list[SenderZeile] = []
        self.spieler: Gst.Element | None = None
        self.laeuft_gerade: SenderZeile | None = None
        self.arbeitet = False

        self.set_content(self._aufbau())
        self.connect("close-request", self._beim_schliessen)
        self.liste_holen(aus_zwischenspeicher=True)

    # -- Aufbau ------------------------------------------------------------

    def _aufbau(self) -> Gtk.Widget:
        aussen = Adw.ToolbarView()

        kopf = Adw.HeaderBar()
        self.knopf_holen = Gtk.Button(icon_name="view-refresh-symbolic")
        self.knopf_holen.set_tooltip_text("Senderliste neu aus dem Netz holen")
        self.knopf_holen.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Senderliste neu holen"])
        self.knopf_holen.connect("clicked", lambda *_: self.liste_holen())
        kopf.pack_start(self.knopf_holen)

        menue = Gio.Menu()
        menue.append("Alle auswaehlen", "win.alle")
        menue.append("Auswahl aufheben", "win.keine")
        menue.append("Nur laufende auswaehlen", "win.nur-laufende")
        menue.append("Sprechformen neu vorschlagen", "win.sprechformen")
        abschnitt = Gio.Menu()
        abschnitt.append("Markdown-Tabelle kopieren", "win.markdown")
        abschnitt.append("Als Wiedergabeliste speichern ...", "win.pls")
        menue.append_section(None, abschnitt)
        hilfe = Gio.Menu()
        hilfe.append("Ueber DialOS-Rhythmbox", "win.ueber")
        menue.append_section(None, hilfe)

        menue_knopf = Gtk.MenuButton(icon_name="open-menu-symbolic",
                                     menu_model=menue)
        menue_knopf.set_tooltip_text("Menue")
        menue_knopf.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Hauptmenue"])
        kopf.pack_end(menue_knopf)
        aussen.add_top_bar(kopf)

        for name, rueckruf in (("alle", lambda *_: self._haken_setzen(True)),
                               ("keine", lambda *_: self._haken_setzen(False)),
                               ("nur-laufende", lambda *_: self._nur_laufende()),
                               ("sprechformen", lambda *_: self._sprechformen_neu()),
                               ("markdown", lambda *_: self.markdown_kopieren()),
                               ("pls", lambda *_: self.pls_speichern()),
                               ("ueber", lambda *_: self.ueber_zeigen())):
            handlung = Gio.SimpleAction.new(name, None)
            handlung.connect("activate", rueckruf)
            self.add_action(handlung)

        aussen.add_top_bar(self._filterleiste())

        self.seiten = Adw.ToastOverlay()
        self.inhalt = Adw.PreferencesPage()
        self.seiten.set_child(self.inhalt)
        aussen.set_content(self.seiten)

        aussen.add_bottom_bar(self._fussleiste())
        return aussen

    # -- Filterleiste ------------------------------------------------------
    #
    # Stephans Aufbau vom 2026-09-25: "Land - Landesweite Sender,
    # Bundesland, Stadt oder so in der Art", und danach "Und dann noch nach
    # Genre". Die Suche dahinter steht seit demselben Tag im Modul und war
    # bis zum 2026-09-30 nur ueber die Kommandozeile bedienbar.
    #
    # WARUM LAND UND BEREICH GETRENNT SIND und nicht eine lange Liste:
    # Deutschland allein hat 16 Bundeslaender und 4 Grossstaedte, alle drei
    # Laender zusammen 49 Eintraege plus Genres. Eine Liste mit 60 Zeilen
    # findet niemand mehr durch.

    #: Die erste Zeile jeder Auswahl - sie muss ohne Nachdenken passen.
    ALLE_LAENDER = "Alle drei Länder"
    LANDESWEIT = "Landesweit"
    ALLE_GENRES = "Alle Genres"

    def _filterleiste(self) -> Gtk.Widget:
        leiste = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        leiste.set_margin_top(6)
        leiste.set_margin_bottom(6)
        leiste.set_margin_start(12)
        leiste.set_margin_end(12)

        self.wahl_land = Gtk.DropDown.new_from_strings(
            [self.ALLE_LAENDER] + list(rs.LAENDER))
        self.wahl_land.set_tooltip_text("Land")
        self.wahl_land.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Land"])
        self.wahl_land.connect("notify::selected",
                               lambda *_: self._land_geaendert())
        leiste.append(self.wahl_land)

        self.wahl_bereich = Gtk.DropDown.new_from_strings([self.LANDESWEIT])
        self.wahl_bereich.set_tooltip_text(
            "Landesweit, ein Bundesland oder eine Stadt")
        self.wahl_bereich.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Bereich"])
        leiste.append(self.wahl_bereich)

        self.wahl_genre = Gtk.DropDown.new_from_strings(
            [self.ALLE_GENRES] + list(rs.GENRES))
        self.wahl_genre.set_tooltip_text("Genre")
        self.wahl_genre.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Genre"])
        leiste.append(self.wahl_genre)

        self.suchfeld = Gtk.SearchEntry()
        self.suchfeld.set_placeholder_text("Name oder Schlagwort ...")
        self.suchfeld.set_hexpand(True)
        self.suchfeld.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Freie Suche"])
        self.suchfeld.connect("activate", lambda *_: self.suche_starten())
        leiste.append(self.suchfeld)

        self.knopf_suchen = Gtk.Button(label="Suchen")
        self.knopf_suchen.connect("clicked", lambda *_: self.suche_starten())
        leiste.append(self.knopf_suchen)

        # Zurueck zur kuratierten Liste. Ohne diesen Knopf waere die Suche
        # eine Einbahnstrasse: Wer einmal 155 Berliner Sender geholt hat,
        # kaeme nur ueber einen Neustart wieder zu den 78 geprueften.
        self.knopf_kuratiert = Gtk.Button(icon_name="go-home-symbolic")
        self.knopf_kuratiert.set_tooltip_text(
            "Zurück zur geprüften Liste der 78 Sender")
        self.knopf_kuratiert.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Zurück zur geprüften Liste"])
        self.knopf_kuratiert.connect(
            "clicked", lambda *_: self.liste_holen(aus_zwischenspeicher=True))
        leiste.append(self.knopf_kuratiert)

        self._land_geaendert()
        return leiste

    def _gewaehltes_land(self) -> str | None:
        """None heisst: alle drei Laender."""
        stelle = self.wahl_land.get_selected()
        if stelle < 1:
            return None
        return list(rs.LAENDER)[stelle - 1]

    def _land_geaendert(self) -> None:
        """Bereiche zum gewaehlten Land neu fuellen.

        Bundeslaender und Staedte gibt es nur je Land - "Tirol" unter
        Deutschland waere ein Eintrag, der nie einen Treffer liefert.
        """
        land = self._gewaehltes_land()
        eintraege = [self.LANDESWEIT]
        self._bereiche: list[tuple[str, str | None]] = [("landesweit", None)]

        if land:
            for name in rs.BUNDESLAENDER.get(land, {}):
                eintraege.append(name)
                self._bereiche.append(("bundesland", name))
            for name in rs.STAEDTE.get(land, []):
                # Der Zusatz ist keine Zier: Die Datenbank hat kein
                # Stadtfeld, die Suche ist eine Naeherung ueber Name,
                # Schlagwort und "state". Wer das nicht weiss, haelt
                # "Innsbruck: 1 Sender" fuer einen Fehler.
                eintraege.append(f"{name} (Näherung)")
                self._bereiche.append(("stadt", name))

        modell = Gtk.StringList.new(eintraege)
        self.wahl_bereich.set_model(modell)
        self.wahl_bereich.set_selected(0)
        self.wahl_bereich.set_sensitive(land is not None)
        if land is None:
            self.wahl_bereich.set_tooltip_text(
                "Bundesländer und Städte gibt es nur für ein einzelnes Land")
        else:
            self.wahl_bereich.set_tooltip_text(
                "Landesweit, ein Bundesland oder eine Stadt")

    def _gewaehltes_genre(self) -> str | None:
        stelle = self.wahl_genre.get_selected()
        if stelle < 1:
            return None
        return list(rs.GENRES)[stelle - 1]

    def _fussleiste(self) -> Gtk.Widget:
        kasten = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        kasten.set_margin_top(8)
        kasten.set_margin_bottom(10)
        kasten.set_margin_start(12)
        kasten.set_margin_end(12)

        self.balken = Gtk.ProgressBar()
        self.balken.set_show_text(False)
        self.balken.set_visible(False)
        kasten.append(self.balken)

        self.meldung = Gtk.Label(label="Bereit.", xalign=0.0)
        self.meldung.add_css_class("dim-label")
        self.meldung.set_wrap(True)
        kasten.append(self.meldung)

        knoepfe = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        knoepfe.set_halign(Gtk.Align.END)

        self.knopf_pruefen = Gtk.Button(label="Sender pruefen")
        self.knopf_pruefen.connect("clicked", lambda *_: self.pruefen_starten())
        knoepfe.append(self.knopf_pruefen)

        self.knopf_rhythmbox = Gtk.Button(label="In Rhythmbox uebernehmen")
        self.knopf_rhythmbox.connect(
            "clicked", lambda *_: self.uebernehmen("rhythmbox"))
        knoepfe.append(self.knopf_rhythmbox)

        # Der eigentliche Zweck: die Medienliste fuer DialOS.
        self.knopf_medienliste = Gtk.Button(label="Medienliste speichern")
        self.knopf_medienliste.add_css_class("suggested-action")
        self.knopf_medienliste.connect(
            "clicked", lambda *_: self.medienliste_speichern())
        knoepfe.append(self.knopf_medienliste)

        kasten.append(knoepfe)
        return kasten

    # -- Zustand -----------------------------------------------------------

    def sagen(self, text: str) -> None:
        self.meldung.set_text(text)

    def toast(self, text: str) -> None:
        self.seiten.add_toast(Adw.Toast.new(text))

    def _knoepfe_sperren(self, gesperrt: bool) -> None:
        self.arbeitet = gesperrt
        for k in (self.knopf_pruefen, self.knopf_rhythmbox,
                  self.knopf_medienliste, self.knopf_holen,
                  self.knopf_suchen, self.knopf_kuratiert,
                  self.wahl_land, self.wahl_genre, self.suchfeld):
            k.set_sensitive(not gesperrt)
        # Der Bereich bleibt gesperrt, solange kein einzelnes Land gewaehlt
        # ist - sonst hebt das Entsperren nach einer Suche eine Sperre auf,
        # die _land_geaendert() aus gutem Grund gesetzt hat.
        self.wahl_bereich.set_sensitive(
            not gesperrt and self._gewaehltes_land() is not None)

    def _haken_setzen(self, an: bool) -> None:
        for z in self.zeilen:
            z.haken.set_active(an)

    def _nur_laufende(self) -> None:
        for z in self.zeilen:
            z.haken.set_active(bool(z.sender.get("laeuft")))

    def gewaehlte(self) -> list[dict]:
        return [z.sender for z in self.zeilen if z.haken.get_active()]

    def _sprechformen_neu(self) -> None:
        for z in self.zeilen:
            z.sprechform.set_text(rs.sprechform_vorschlag(z.sender["name"]))

    def auswahl_geaendert(self) -> None:
        """Nach jeder Aenderung nachsehen, ob sich zwei Saetze zu aehnlich sind.

        Geprueft wird nur die getroffene Auswahl - zwei verwechselbare
        Sender, von denen keiner in die Liste kommt, sind kein Problem.
        """
        gewaehlt = [z for z in self.zeilen if z.haken.get_active()]
        for z in self.zeilen:
            z.doppelt_markieren(False)

        if not gewaehlt:
            self.sagen("Kein Sender ausgewaehlt. "
                       "Weniger ist mehr - zehn gut gewaehlte reichen.")
            return

        paare = rs.aehnliche_sprechformen([z.sender for z in gewaehlt])
        nach_sender = {id(z.sender): z for z in gewaehlt}
        for a, b, grund in paare:
            for eintrag, anderer in ((a, b), (b, a)):
                zeile = nach_sender.get(id(eintrag))
                if zeile is not None:
                    zeile.doppelt_markieren(
                        True,
                        f"Klingt zu aehnlich wie \"{anderer.get('sprechform')}\" "
                        f"({grund}). Die Spracherkennung wird beide "
                        "verwechseln.")

        leer = [z for z in gewaehlt if not z.sender.get("sprechform")]
        teile = [f"{len(gewaehlt)} Sender ausgewaehlt"]
        if paare:
            teile.append(f"{len(paare)} Paare klingen zu aehnlich "
                         "(rot markiert)")
        if leer:
            teile.append(f"{len(leer)} ohne Sprechform")
        self.sagen(". ".join(teile) + ".")

    # -- Liste holen -------------------------------------------------------

    def liste_holen(self, aus_zwischenspeicher: bool = False) -> None:
        if aus_zwischenspeicher and ZWISCHENSPEICHER.exists():
            try:
                import json
                with open(ZWISCHENSPEICHER, encoding="utf-8") as f:
                    self._liste_zeigen(json.load(f))
                self.sagen(f"{len(self.zeilen)} Sender aus dem Zwischenspeicher. "
                           "Zum Auffrischen oben auf den Pfeil.")
                return
            except Exception:
                pass    # kaputter Zwischenspeicher - dann eben aus dem Netz

        self._knoepfe_sperren(True)
        self.sagen("Senderliste von radio-browser.info holen ...")
        self.balken.set_visible(True)
        self.balken.pulse()

        def arbeit():
            try:
                liste = rs.sender_holen(list(rs.SENDER.keys()))
            except Exception as e:
                im_hauptfaden(self._holen_fehlgeschlagen, str(e))
                return
            im_hauptfaden(self._holen_fertig, liste)

        threading.Thread(target=arbeit, daemon=True).start()
        GLib.timeout_add(120, self._balken_pulsen)

    # -- Suchen ------------------------------------------------------------

    def suche_starten(self) -> None:
        """Die Filterleiste auswerten und in der Datenbank suchen.

        Gesucht wird IMMER frisch: Der Zwischenspeicher enthaelt die
        kuratierten 78, nicht die Treffer einer Abfrage. Ein Suchergebnis
        zwischenzuspeichern waere auch falsch - es gehoert zur Frage, die
        gerade gestellt wurde, nicht zum Programm.
        """
        if self.arbeitet:
            return
        land = self._gewaehltes_land()
        genre = self._gewaehltes_genre()
        text = self.suchfeld.get_text().strip()
        art, wert = self._bereiche[self.wahl_bereich.get_selected()]

        if not (land or genre or text):
            self.sagen("Wähle ein Land, ein Genre oder gib einen Suchbegriff "
                       "ein. Der Pfeil oben holt die geprüfte Liste zurück.")
            return

        laender = [land] if land else list(rs.LAENDER)
        self._knoepfe_sperren(True)
        self.balken.set_visible(True)
        self.balken.pulse()
        self.sagen(self._suchmeldung(art, wert, land, genre, text) + " ...")

        def arbeit():
            treffer, fehler = [], None
            try:
                for einzelland in laender:
                    if text:
                        gefunden = rs.frei_suchen(einzelland, text)
                        if genre:
                            gefunden = rs.nach_genre_filtern(gefunden, genre)
                    elif art == "bundesland":
                        gefunden = rs.bundesland_suchen(einzelland, wert, genre)
                    elif art == "stadt":
                        gefunden = rs.stadt_suchen(einzelland, wert, genre)
                    elif genre:
                        gefunden = rs.genre_suchen(einzelland, genre)
                    else:
                        # Land ohne alles: die kuratierten Sender dieses
                        # Landes, nicht die ganze Datenbank. Achthundert
                        # Zeilen sind keine Auswahl, sondern ein Haufen.
                        gefunden = rs.sender_holen([einzelland])
                    treffer.extend(gefunden)
            except Exception as e:                # noqa: BLE001
                fehler = str(e)
            im_hauptfaden(self._suche_fertig, treffer, fehler, art, wert,
                          land, genre, text)

        threading.Thread(target=arbeit, daemon=True).start()
        GLib.timeout_add(120, self._balken_pulsen)

    @staticmethod
    def _suchmeldung(art, wert, land, genre, text) -> str:
        teile = []
        if text:
            teile.append(f"Sender zu „{text}“")
        elif art == "bundesland":
            teile.append(f"Sender in {wert}")
        elif art == "stadt":
            teile.append(f"Sender in {wert}")
        else:
            teile.append("Sender")
        if genre:
            teile.append(f"im Genre {genre}")
        teile.append(f"in {land}" if land else "in allen drei Ländern")
        return " ".join(teile)

    def _suche_fertig(self, treffer, fehler, art, wert, land, genre,
                      text) -> None:
        self._knoepfe_sperren(False)
        self.balken.set_visible(False)
        if fehler:
            self.sagen(f"Die Suche ist gescheitert: {fehler}")
            self.toast("Keine Verbindung zu radio-browser.info")
            return

        self._liste_zeigen(treffer)
        was = self._suchmeldung(art, wert, land, genre, text)
        if not treffer:
            self.sagen(f"{was}: nichts gefunden. Der Pfeil oben holt die "
                       "geprüfte Liste zurück.")
            return

        hinweise = [f"{len(treffer)} Treffer für {was}."]
        if art == "stadt":
            # Ehrlichkeit statt Schein: Das TODO verlangt ausdruecklich,
            # die Naeherung anzuzeigen. Am 2026-09-25 gemessen: Berlin
            # 155 Treffer, Muenchen 28, Koeln 11, Innsbruck 1.
            hinweise.append("Die Stadtsuche ist eine Näherung - die Datenbank "
                            "hat kein Stadtfeld. Gesucht wird über Name, "
                            "Schlagwort und Bundesland.")
        hinweise.append("Diese Sender sind NICHT angetestet - dafür unten auf "
                        "„Sender prüfen“.")
        self.sagen(" ".join(hinweise))

    def _balken_pulsen(self) -> bool:
        if not self.arbeitet:
            return False
        self.balken.pulse()
        return True

    def _holen_fehlgeschlagen(self, meldung: str) -> None:
        self._knoepfe_sperren(False)
        self.balken.set_visible(False)
        self.sagen(f"Die Senderliste liess sich nicht holen: {meldung}")
        self.toast("Keine Verbindung zu radio-browser.info")

    def _holen_fertig(self, liste: list[dict]) -> None:
        self._knoepfe_sperren(False)
        self.balken.set_visible(False)
        self._liste_zeigen(liste)
        self._zwischenspeichern(liste)
        self.sagen(f"{len(liste)} Sender geholt. Mit 'Sender pruefen' antesten.")

    def _zwischenspeichern(self, liste: list[dict]) -> None:
        try:
            import json
            ZWISCHENSPEICHER.parent.mkdir(parents=True, exist_ok=True)
            schlank = [{k: v for k, v in s.items()
                        if k in ("name", "land", "url", "uuid", "codec",
                                 "bitrate", "seite")} for s in liste]
            with open(ZWISCHENSPEICHER, "w", encoding="utf-8") as f:
                json.dump(schlank, f, ensure_ascii=False, indent=1)
        except OSError:
            pass    # ohne Zwischenspeicher geht es auch, nur langsamer

    def _liste_zeigen(self, liste: list[dict]) -> None:
        # Eine PreferencesPage laesst sich nicht sauber leeren; beim
        # Auffrischen wird deshalb eine neue gebaut und ausgetauscht.
        neue_seite = Adw.PreferencesPage()
        self.zeilen = []

        for land in ("Deutschland", "Oesterreich", "Schweiz"):
            teil = [s for s in liste if s["land"] == land]
            if not teil:
                continue
            gruppe = Adw.PreferencesGroup(title=land)
            gruppe.set_description(f"{len(teil)} Sender")
            gruppe.add_css_class("sender-liste")
            for sender in teil:
                zeile = SenderZeile(sender, self)
                self.zeilen.append(zeile)
                gruppe.add(zeile)
            neue_seite.add(gruppe)

        self.inhalt = neue_seite
        self.seiten.set_child(neue_seite)

    # -- Pruefen -----------------------------------------------------------

    def pruefen_starten(self) -> None:
        if not self.zeilen:
            self.toast("Es ist noch keine Senderliste da.")
            return

        self._knoepfe_sperren(True)
        self.balken.set_visible(True)
        self.balken.set_fraction(0.0)
        gesamt = len(self.zeilen)
        self.sagen(f"0 von {gesamt} Sendern geprueft ...")
        fertig = {"n": 0}

        def einer(zeile: SenderZeile):
            geprueft = rs.pruefen([zeile.sender], gruendlich=True, parallel=1)[0]
            zeile.sender.update(geprueft)
            fertig["n"] += 1
            im_hauptfaden(self._einer_geprueft, zeile, fertig["n"], gesamt)

        def arbeit():
            import concurrent.futures as f
            with f.ThreadPoolExecutor(8) as ex:
                list(ex.map(einer, self.zeilen))
            im_hauptfaden(self._pruefen_fertig)

        threading.Thread(target=arbeit, daemon=True).start()

    def _einer_geprueft(self, zeile: SenderZeile, n: int, gesamt: int) -> None:
        zeile.zustand_zeigen()
        self.balken.set_fraction(n / gesamt)
        self.sagen(f"{n} von {gesamt} Sendern geprueft ...")

    def _pruefen_fertig(self) -> None:
        self._knoepfe_sperren(False)
        self.balken.set_visible(False)
        laufen = [z for z in self.zeilen if z.sender.get("laeuft")]
        tot = [z for z in self.zeilen if not z.sender.get("laeuft")]
        zweifel = [z for z in laufen if z.sender.get("namenszweifel")]

        text = f"{len(laufen)} von {len(self.zeilen)} Sendern laufen."
        if tot:
            text += ("  Nicht erreichbar und abgewaehlt: "
                     + ", ".join(z.sender["name"] for z in tot) + ".")
        if zweifel:
            text += ("  Bei diesen weicht der gemeldete Name ab: "
                     + ", ".join(z.sender["name"] for z in zweifel) + ".")
        self.sagen(text)
        self.toast(f"{len(laufen)} von {len(self.zeilen)} Sendern laufen")

    # -- Vorhoeren ---------------------------------------------------------

    def abspielen(self, sender: dict, zeile: SenderZeile) -> None:
        self.anhalten()
        if self.spieler is None:
            self.spieler = Gst.ElementFactory.make("playbin3", "spieler") \
                or Gst.ElementFactory.make("playbin", "spieler")
            if self.spieler is None:
                self.toast("GStreamer kann nicht abspielen.")
                return
            bus = self.spieler.get_bus()
            bus.add_signal_watch()
            bus.connect("message::error", self._spieler_fehler)

        self.spieler.set_property("uri", sender["url"])
        self.spieler.set_state(Gst.State.PLAYING)
        self.laeuft_gerade = zeile
        zeile.hoeren.set_icon_name("media-playback-stop-symbolic")
        self.sagen(f"Es laeuft: {sender['name']}")

    def anhalten(self) -> None:
        if self.spieler is not None:
            self.spieler.set_state(Gst.State.NULL)
        if self.laeuft_gerade is not None:
            self.laeuft_gerade.hoeren.set_icon_name("media-playback-start-symbolic")
            self.laeuft_gerade.hoeren_aus()
            self.laeuft_gerade = None

    def _spieler_fehler(self, bus, nachricht) -> None:
        fehler, _ = nachricht.parse_error()
        im_hauptfaden(self.toast, f"Abspielen gescheitert: {fehler.message}")
        im_hauptfaden(self.anhalten)

    # -- Uebernehmen -------------------------------------------------------

    def uebernehmen(self, ziel: str = "rhythmbox") -> None:
        gewaehlt = self.gewaehlte()
        if not gewaehlt:
            self.toast("Es ist kein Sender ausgewaehlt.")
            return

        programm = "Rhythmbox"
        if rs.laeuft_programm(ziel):
            self._hinweis(
                f"{programm} laeuft gerade",
                f"Bitte {programm} zuerst beenden. Sonst ueberschreibt das "
                "Programm beim Schliessen die Datenbank und die neuen Sender "
                "waeren wieder weg.")
            return

        ergebnis: dict = {}

        def arbeit():
            import contextlib
            import io
            ausgabe = io.StringIO()
            with contextlib.redirect_stdout(ausgabe), \
                 contextlib.redirect_stderr(ausgabe):
                geklappt = rs.rhythmbox_eintragen(gewaehlt)
            ergebnis["ok"] = geklappt
            ergebnis["text"] = ausgabe.getvalue().strip()
            im_hauptfaden(self._uebernehmen_fertig, programm, ergebnis)

        self._knoepfe_sperren(True)
        self.sagen(f"{len(gewaehlt)} Sender in {programm} eintragen ...")
        threading.Thread(target=arbeit, daemon=True).start()

    def _uebernehmen_fertig(self, programm: str, ergebnis: dict) -> None:
        self._knoepfe_sperren(False)
        text = ergebnis.get("text") or ""
        if ergebnis.get("ok"):
            self.sagen(f"In {programm} eingetragen. " + " ".join(text.split()))
            self.toast(f"In {programm} eingetragen")
        else:
            self._hinweis(f"In {programm} eintragen ist nicht gelungen",
                          text or "Unbekannter Fehler.")
            self.sagen("Es wurde nichts geaendert.")

    def medienliste_speichern(self) -> None:
        """Die Auswahl als medienliste.json fuer DialOS."""
        gewaehlt = self.gewaehlte()
        if not gewaehlt:
            self.toast("Es ist kein Sender ausgewaehlt.")
            return

        ohne = [s["name"] for s in gewaehlt if not s.get("sprechform")]
        if ohne:
            self._hinweis(
                "Es fehlen Sprechformen",
                "Ohne Sprechform kann DialOS den Sender nicht ansagen "
                "lassen. Betroffen: " + ", ".join(ohne))
            return

        paare = rs.aehnliche_sprechformen(gewaehlt)
        if paare:
            text = "\n".join(
                f"• \"{a['sprechform']}\" und \"{b['sprechform']}\" ({g})"
                for a, b, g in paare)
            frage = Adw.AlertDialog(
                heading="Diese Saetze klingen zu aehnlich",
                body="Die Spracherkennung wird sie verwechseln, und der "
                     "Nutzer kann nicht nachsehen, was gerade laeuft:\n\n"
                     + text + "\n\nTrotzdem speichern?")
            frage.add_response("zurueck", "Zurueck und aendern")
            frage.add_response("trotzdem", "Trotzdem speichern")
            frage.set_response_appearance("trotzdem",
                                          Adw.ResponseAppearance.DESTRUCTIVE)
            frage.set_default_response("zurueck")
            frage.connect("response", self._medienliste_trotzdem, gewaehlt)
            frage.present(self)
            return

        self._medienliste_ziel_waehlen(gewaehlt)

    def _medienliste_trotzdem(self, dialog, antwort, gewaehlt) -> None:
        if antwort == "trotzdem":
            self._medienliste_ziel_waehlen(gewaehlt)

    def _medienliste_ziel_waehlen(self, gewaehlt) -> None:
        """Der Dateidialog mit dem richtigen Ziel vorbelegt.

        Auf der Werkbank ist das die Datei im Repo-Baum - von dort spielt
        `dialos-aufspielen` sie aufs Geraet, die Auswahl geht also ueber
        git. Am Geraet selbst ist es die persoenliche Liste des Kontos.
        Aendern kann der Mensch das Ziel weiterhin; vorgeschlagen wird
        aber das, was tatsaechlich irgendwo ankommt.
        """
        ziel = rs.speicherziel()
        waehler = Gtk.FileDialog(title="Medienliste speichern",
                                 initial_name=os.path.basename(ziel))
        ordner = os.path.dirname(ziel)
        if os.path.isdir(ordner):
            waehler.set_initial_folder(Gio.File.new_for_path(ordner))
        waehler.save(self, None, self._medienliste_ziel_gewaehlt, gewaehlt)

    def _medienliste_ziel_gewaehlt(self, waehler, ergebnis, gewaehlt) -> None:
        try:
            datei = waehler.save_finish(ergebnis)
        except GLib.Error:
            return      # abgebrochen
        if datei is None or datei.get_path() is None:
            return
        pfad = datei.get_path()
        try:
            daten = rs.medienliste_schreiben(gewaehlt, pfad)
        except OSError as e:
            self._hinweis("Speichern gescheitert", str(e))
            return
        self.sagen(f"{len(daten['eintraege'])} Eintraege nach {pfad} "
                   "geschrieben.")
        # Der Weg ans Geraet ist nicht selbsterklaerend, und eine Datei,
        # die richtig liegt, aber nie aufgespielt wird, sieht von aussen
        # aus wie eine, die funktioniert.
        repo = rs.repo_liste()
        if repo and os.path.abspath(pfad) == os.path.abspath(repo):
            self.sagen("Das ist die Datei im Repo. Ans Geraet kommt sie "
                       "ueber git und dann 'sudo dialos-aufspielen "
                       "--wirklich'.")
        elif os.path.abspath(pfad) == os.path.abspath(rs.eigene_liste()):
            self.sagen("Das ist die persoenliche Liste dieses Kontos. "
                       "Sie gilt sofort und wird von keinem Aufspielen "
                       "ueberschrieben.")
        self.toast("Medienliste gespeichert")

    def markdown_kopieren(self) -> None:
        """Die Radio-Tabelle fuer medienliste.md in die Zwischenablage."""
        gewaehlt = self.gewaehlte()
        if not gewaehlt:
            self.toast("Es ist kein Sender ausgewaehlt.")
            return
        text = rs.markdown_tabelle(gewaehlt)
        anzeige = Gdk.Display.get_default()
        if anzeige is None:
            self.toast("Keine Zwischenablage verfuegbar.")
            return
        anzeige.get_clipboard().set(text)
        self.toast(f"Tabelle mit {len(gewaehlt)} Zeilen kopiert")
        self.sagen("Die Markdown-Tabelle liegt in der Zwischenablage - "
                   "sie passt in den Abschnitt 'Radio' von medienliste.md.")

    def pls_speichern(self) -> None:
        gewaehlt = self.gewaehlte()
        if not gewaehlt:
            self.toast("Es ist kein Sender ausgewaehlt.")
            return

        waehler = Gtk.FileDialog(title="Wohin sollen die Wiedergabelisten?")
        waehler.select_folder(self, None, self._pls_ziel_gewaehlt, gewaehlt)

    def _pls_ziel_gewaehlt(self, waehler, ergebnis, gewaehlt) -> None:
        try:
            ordner = waehler.select_folder_finish(ergebnis)
        except GLib.Error:
            return      # abgebrochen
        if ordner is None:
            return
        pfad = ordner.get_path()
        try:
            rs.pls_schreiben(gewaehlt, pfad)
        except OSError as e:
            self._hinweis("Speichern gescheitert", str(e))
            return
        self.sagen(f"{len(gewaehlt)} Sender nach {pfad} geschrieben.")
        self.toast("Wiedergabelisten gespeichert")

    # -- Kleinkram ---------------------------------------------------------

    def _hinweis(self, titel: str, text: str) -> None:
        d = Adw.AlertDialog(heading=titel, body=text)
        d.add_response("gut", "Verstanden")
        d.present(self)

    def ueber_zeigen(self) -> None:
        d = Adw.AboutDialog(
            application_name="DialOS-Rhythmbox",
            application_icon=APP_ID,
            developer_name="Stephan Roesner",
            version="1.0",
            comments=("Sender aus Deutschland, Oesterreich und der Schweiz "
                      "auswaehlen, antesten und daraus die Medienliste fuer "
                      "DialOS erzeugen - auf Wunsch auch gleich Eintraege in "
                      "Rhythmbox.\n\nDie Senderdaten stammen von "
                      "radio-browser.info, einer offenen Gemeinschafts-"
                      "datenbank ohne Konto und ohne Schluessel."),
            website="https://www.radio-browser.info/")
        d.present(self)

    def _beim_schliessen(self, *_args) -> bool:
        self.anhalten()
        return False


# ------------------------------------------------------------------ Programm

class Programm(Adw.Application):

    def __init__(self) -> None:
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    @staticmethod
    def _symbole_anmelden() -> None:
        """Macht das mitgelieferte Symbol auffindbar.

        Wer DialOS-Rhythmbox direkt aus dem entpackten Verzeichnis
        startet, hat das Symbol nicht im Symbolsatz des Systems. Der
        zusaetzliche Suchpfad sorgt dafuer, dass es trotzdem im Fenster,
        in der Fensterleiste und im Ueber-Dialog erscheint.
        """
        symbole = HIER / "assets" / "icons"
        anzeige = Gdk.Display.get_default()
        if symbole.is_dir() and anzeige is not None:
            Gtk.IconTheme.get_for_display(anzeige).add_search_path(str(symbole))

    def do_startup(self) -> None:
        Adw.Application.do_startup(self)
        Gst.init(None)
        self._symbole_anmelden()

        vorlage = Gtk.CssProvider()
        vorlage.load_from_data(CSS.encode("utf-8"))
        anzeige = Gdk.Display.get_default()
        if anzeige is not None:
            Gtk.StyleContext.add_provider_for_display(
                anzeige, vorlage, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        beenden = Gio.SimpleAction.new("quit", None)
        beenden.connect("activate", lambda *_: self.quit())
        self.add_action(beenden)
        self.set_accels_for_action("app.quit", ["<Control>q"])

    def do_activate(self) -> None:
        fenster = self.props.active_window or Fenster(self)
        fenster.present()


if __name__ == "__main__":
    sys.exit(Programm().run(sys.argv))
