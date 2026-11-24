#!/bin/bash
# DialOS: legt im GNOME-Programmmenue den Ordner "DialOS Tools" an.
#
# Stephan, 2026-11-24: "Wenn wir fuer DialOS kleine Helfer bauen, dann waere
# es cool, wenn wir diese im Gnome Menue unter einem Reiter alle zusammen
# legen. Dann bleibt der Bildschirm und das Menue schoen aufgeraeumt!"
#
# DER ORDNER SAMMELT NACH KATEGORIE, nicht nach Liste: Jede .desktop-Datei mit
# "X-DialOS-Tools;" in Categories landet von selbst darin. Ein neues Werkzeug
# braucht nur diese Kategorie - hier muss niemand etwas nachtragen.
#
# WARUM BEI JEDEM ANMELDEN und nicht einmal per Systemvorgabe: Die Ordnerliste
# (org.gnome.desktop.app-folders folder-children) steht in bestehenden Konten
# schon fest eingetragen (am T490: System, Utilities, YaST, Pardus). Eine
# Vorgabe unter /etc/dconf greift dann nicht. Das Skript haengt den Ordner nur
# an, wenn er fehlt, und laesst alle anderen Ordner stehen. Mehrfaches
# Ausfuehren schadet nicht.
set -u

ID="DialOS-Tools"
PFAD="/org/gnome/desktop/app-folders/folders/$ID/"
SCHEMA="org.gnome.desktop.app-folders.folder:$PFAD"

liste=$(gsettings get org.gnome.desktop.app-folders folder-children 2>/dev/null) || exit 0
case "$liste" in
  *"'$ID'"*) ;;
  "@as []"|"[]") gsettings set org.gnome.desktop.app-folders folder-children "['$ID']" ;;
  *) gsettings set org.gnome.desktop.app-folders folder-children "${liste%]}, '$ID']" ;;
esac

gsettings set "$SCHEMA" name "DialOS Tools"
gsettings set "$SCHEMA" translate false
gsettings set "$SCHEMA" categories "['X-DialOS-Tools']"
