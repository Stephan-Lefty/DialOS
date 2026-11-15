#!/bin/bash
# Misst, was DialOS an Hardware wirklich braucht - fuer docs/hardware.md.
#
# Die Tabelle dort stammt vom 2026-09-17. Seitdem sind Radio, Musik und
# Podcasts dazugekommen (Rhythmbox), das System wurde zweimal neu
# aufgebaut und rund 100 Updates eingespielt. Die Zahlen gehoeren also
# nachgemessen statt fortgeschrieben.
#
# Laeuft NUR am Geraet (T490). Am Arbeitsrechner gibt es weder Vosk noch
# Piper noch die Dienste - dort kaeme Unsinn heraus.
#
# Aufruf:
#   bash /media/dialosadmin/SanDisk-Extreme/DialOS/scripts/dialos-hardware-messen.sh
#
# Schreibt alles nach /tmp/dialos-hardware-messung.txt und zeigt es an.

ZIEL=/tmp/dialos-hardware-messung.txt

{
echo "DialOS Hardware-Messung"
echo "Datum: $(date '+%Y-%m-%d %H:%M')"
echo "Rechner: $(hostname)"
echo "========================================================"
echo

echo "--- Prozessor ---"
lscpu | grep -E "^(Modellname|Model name|CPU\(s\)|Thread|Kern|Core)" | sed 's/  */ /g'
echo -n "AVX2: "
grep -qm1 avx2 /proc/cpuinfo && echo "ja" || echo "NEIN - Parakeet laeuft dann nicht wie gemessen"
echo

echo "--- Arbeitsspeicher gesamt ---"
free -h | head -2
echo

echo "--- Was DialOS gerade belegt (nur laufende Prozesse) ---"
printf "%-34s %10s\n" "Prozess" "Speicher"
for muster in \
    "dialos-sprachbefehl-desktop" \
    "dialos-diktat" \
    "dialos-say" \
    "languagetool" \
    "rhythmbox" \
    "thunderbird" \
    "firefox" \
    "gnome-shell"
do
    # Summe ueber alle passenden Prozesse, in MB.
    mb=$(ps -eo rss,args --no-headers 2>/dev/null \
         | grep -i "$muster" | grep -v grep \
         | awk '{s+=$1} END {if (s>0) printf "%.0f", s/1024}')
    [ -n "$mb" ] && printf "%-34s %7s MB\n" "$muster" "$mb"
done
echo
echo "(Leer heisst: laeuft gerade nicht. Fuer eine vollstaendige Messung"
echo " vorher Radio einschalten und ein Diktat starten.)"
echo

echo "--- Platte ---"
df -h / /home 2>/dev/null | grep -vE "^tmpfs|^udev"
echo
echo "Belegung der Systempartition ohne /home:"
du -shx / 2>/dev/null | tail -1
echo

echo "--- Sprachmodelle und Stimmen ---"
for pfad in \
    /usr/local/share/vosk-model-de-small \
    ~/.local/share/vosk-model-de-small \
    /usr/local/share/vosk-model-de \
    /usr/local/share/dialos-parakeet \
    /usr/local/share/dialos-piper \
    /opt/LanguageTool*
do
    for p in $pfad; do
        [ -e "$p" ] && printf "%-46s %s\n" "$(basename "$p")" "$(du -sh "$p" 2>/dev/null | cut -f1)"
    done
done
echo

echo "--- Grafik (fuer Videowiedergabe) ---"
lspci 2>/dev/null | grep -iE "vga|display|3d" | sed 's/^/  /'
echo

echo "--- Audio ---"
echo -n "Eingaenge: "; pactl list short sources 2>/dev/null | wc -l
echo -n "Ausgaenge: "; pactl list short sinks 2>/dev/null | wc -l
echo

echo "--- Kernel und System ---"
uname -r
. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME"
echo
echo "========================================================"
echo "Diese Datei an ClaudIA geben - sie traegt die Zahlen in"
echo "docs/hardware.md und docs/hardware.en.md nach."
} > "$ZIEL" 2>&1

cat "$ZIEL"
echo
echo "Gespeichert unter: $ZIEL"
