// DialOS-Erweiterung fuer GNOME Shell (seit 2026-11-24).
//
// WARUM ES SIE GIBT: Unter Wayland darf ein Programm ohne eigenes Fenster den
// markierten Text nicht lesen - gemessen am 2026-11-24, GTK meldete eine
// leere Zwischenablage. Die Shell selbst darf es immer. Diese Erweiterung
// reicht genau das an DialOS weiter, ueber D-Bus, und sonst nichts.
//
// SCHNITTSTELLE: org.dialos.Shell auf dem Sitzungsbus, Objekt /org/dialos/Shell,
// Methode MarkierungLesen() -> s. Leer, wenn nichts markiert ist.
//
// BEWUSST KLEIN: Jede Methode hier ist etwas, das jedes Programm dieser
// Sitzung abfragen kann. Was dazukommt (Fensterwechsel, siehe TODO.md), wird
// einzeln begruendet.

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const SCHNITTSTELLE = `
<node>
  <interface name="org.dialos.Shell">
    <method name="MarkierungLesen">
      <arg type="s" direction="out" name="text"/>
    </method>
  </interface>
</node>`;

export default class DialOSErweiterung extends Extension {
    enable() {
        this._dienst = Gio.DBusExportedObject.wrapJSObject(SCHNITTSTELLE, this);
        this._dienst.export(Gio.DBus.session, '/org/dialos/Shell');
        this._name = Gio.bus_own_name_on_connection(
            Gio.DBus.session, 'org.dialos.Shell', Gio.BusNameOwnerFlags.NONE, null, null);
    }

    disable() {
        if (this._dienst) {
            this._dienst.unexport();
            this._dienst = null;
        }
        if (this._name) {
            Gio.bus_unown_name(this._name);
            this._name = 0;
        }
    }

    // "...Async": GJS reicht die Anfrage durch, die Antwort kommt, sobald die
    // Shell den Text hat.
    MarkierungLesenAsync(_parameter, anfrage) {
        St.Clipboard.get_default().get_text(St.ClipboardType.PRIMARY, (_ablage, text) => {
            anfrage.return_value(new GLib.Variant('(s)', [text ?? '']));
        });
    }
}
