#!/bin/bash
# Prueft, ob im Konto "nutzer" alles angekommen ist, was pro Konto liegt.
#
# WARUM ES DAS GIBT (Stephan, 2026-09-21): "Alles was wir jetzt auch bei den
# installierten Programmen machen und nicht exklusiv fuer Dialosadmin ist, muss
# dann auch sofort im Nutzer Konto zur Verfuegung stehen. Sonst uebersehen wir
# was." Anlass war die Thunderbird-Erweiterung: von Hand installiert und damit
# nur im Profil von dialosadmin - ein ganzer Tag Arbeit waere im Konto des
# Kunden wirkungslos gewesen, ohne eine einzige Fehlermeldung.
#
# DIESELBE UEBERLEGUNG WIE BEI dialos-installstand.sh: Eine Regel, an die
# jemand denken muss, haelt bis zum naechsten langen Tag. Ein Werkzeug haelt.
#
# Aufruf:  sudo /media/.../repo/scripts/dialos-nutzerkonto-pruefen.sh
set -u
KONTO="${1:-nutzer}"
HEIM="/home/$KONTO"
FEHLT=0

if [ "$(id -u)" -ne 0 ]; then
    echo "Bitte mit sudo aufrufen - /home/$KONTO gehoert einem anderen Konto." >&2
    exit 2
fi
if [ ! -d "$HEIM" ]; then
    echo "Kein Heimatverzeichnis $HEIM - Konto vorhanden?" >&2
    exit 2
fi

sagen() { printf '  %-12s %s\n' "$1" "$2"; }
fehlt()  { sagen "FEHLT" "$1"; FEHLT=$((FEHLT+1)); }
da()     { sagen "da" "$1"; }

echo "=== Thunderbird-Profile von $KONTO ==="
PROFILE=$(find "$HEIM/.thunderbird" -maxdepth 1 -type d -name "*.default*" 2>/dev/null)
if [ -z "$PROFILE" ]; then
    fehlt "kein Thunderbird-Profil (Thunderbird im Konto nie gestartet?)"
else
    for P in $PROFILE; do
        echo "  [$P]"
        if ls "$P"/extensions/bruecke@dialos.org* >/dev/null 2>&1; then
            da "MailExtension bruecke@dialos.org"
        else
            fehlt "MailExtension bruecke@dialos.org"
        fi
        if [ -f "$P/user.js" ]; then
            grep -q 'spellchecker.dictionary' "$P/user.js" && da "user.js: Woerterbuch" || fehlt "user.js: spellchecker.dictionary"
            grep -q 'mail.identity' "$P/user.js" && da "user.js: Signatur" || fehlt "user.js: Signatur (mail.identity)"
        else
            fehlt "user.js im Profil"
        fi
    done
fi

echo "=== Dienste und Timer (systemd --user) ==="
# DREI ORTE, NICHT EINER - und das war beim ersten Lauf am 2026-09-21 der
# Grund fuer neun falsche Meldungen: Ein Dienst kann SYSTEMWEIT eingeschaltet
# sein (/etc/systemd/user/*.target.wants, gilt fuer jedes Konto), pro Konto
# (~/.config/systemd/user/*.target.wants) - oder gar nicht, weil ihn ein Timer
# startet und er selbst nie eingeschaltet wird. Wer nur den zweiten Ort
# ansieht, meldet alles als fehlend, was richtig eingerichtet ist.
eingeschaltet() {
    local name="$1" heim="$2"
    for ziel in default.target.wants timers.target.wants; do
        [ -e "/etc/systemd/user/$ziel/$name" ] && { echo "systemweit"; return; }
        [ -e "$heim/.config/systemd/user/$ziel/$name" ] && { echo "im Konto"; return; }
    done
    echo "nein"
}
for EINHEIT in /etc/systemd/user/dialos-*; do
    [ -e "$EINHEIT" ] || continue
    NAME=$(basename "$EINHEIT")
    # Ein Dienst, zu dem ein gleichnamiger Timer gehoert, wird VON DIESEM
    # gestartet - er muss selbst nicht eingeschaltet sein.
    if [ "${NAME%.service}" != "$NAME" ] && [ -e "/etc/systemd/user/${NAME%.service}.timer" ]; then
        sagen "Timer" "$NAME (wird vom Timer gestartet)"
        continue
    fi
    WO_NUTZER=$(eingeschaltet "$NAME" "$HEIM")
    WO_ADMIN=$(eingeschaltet "$NAME" "/home/dialosadmin")
    if [ "$WO_NUTZER" != "nein" ]; then
        da "$NAME ($WO_NUTZER)"
    elif [ "$WO_ADMIN" != "nein" ]; then
        # DAS IST DER INTERESSANTE FALL: bei dialosadmin von Hand
        # eingeschaltet, beim Nutzer nie - genau die Schieflage, gegen die
        # dieses Werkzeug geschrieben wurde.
        fehlt "$NAME (nur bei dialosadmin, $WO_ADMIN)"
    else
        sagen "aus" "$NAME (bei keinem Konto eingeschaltet)"
    fi
done

echo "=== Autostart ==="
# Die DialOS-Autostarts liegen systemweit in /etc/xdg/autostart und gelten
# damit fuer jedes Konto; hier wird nur geprueft, ob dialosadmin zusaetzlich
# etwas von Hand eingetragen hat, das dem Nutzer fehlt.
ls /etc/xdg/autostart/ 2>/dev/null | grep -c dialos | xargs -I{} echo "  {} systemweite DialOS-Autostarts (gelten fuer alle Konten)"
for EINTRAG in /home/dialosadmin/.config/autostart/*.desktop; do
    [ -e "$EINTRAG" ] || continue
    NAME=$(basename "$EINTRAG")
    case "$NAME" in
        *claude*|*Claude*) continue ;;          # Entwicklerwerkzeug
    esac
    [ -e "$HEIM/.config/autostart/$NAME" ] && da "$NAME" || fehlt "$NAME"
done

echo "=== Schalter unter ~/.config/dialos ==="
for DATEI in frageton persoenliche-daten.txt; do
    [ -e "$HEIM/.config/dialos/$DATEI" ] && da "$DATEI" || fehlt "$DATEI"
done

echo
if [ "$FEHLT" -eq 0 ]; then
    echo "Im Konto $KONTO fehlt nichts."
else
    echo "$FEHLT Punkt(e) fehlen im Konto $KONTO - siehe oben."
fi
exit 0
