#!/bin/sh
# DialOS: Wachposten fuer die Synthese-Kette in
# /etc/speech-dispatcher/modules/piper-generic.conf.
#
# Diese Datei wird dort in GenericExecuteSynth als ERSTES Glied einer
# &&-Kette aufgerufen:
#
#   cd /usr/local/share/dialos-piper && ./check_piper_voice.sh $VOICE && ... | piper ...
#
# Sie fehlte bis 2026-08-16 komplett - weder im Repo noch auf dem System,
# und in der Doku nicht erwaehnt. Folge: Das erste Glied der Kette schlug
# mit "Datei oder Verzeichnis nicht gefunden" fehl, das && brach ab, und es
# wurde NIE etwas synthetisiert. Die Sprachausgabe blieb damit vollstaendig
# stumm, ohne sichtbare Fehlermeldung - das Anzeige-Icon erschien, weil
# dialos-tts-indicator.py unabhaengig davon laeuft.
#
# Auf dem alten Testgeraet existierte die Datei offenbar als manuell
# angelegter Rest und ist bei einem Reinstall verlorengegangen - genau die
# Sorte Luecke, die docs/Debian-zu-DialOS.md schliessen soll.
#
# Aufgabe: pruefen, ob die angeforderte Stimme ueberhaupt vorhanden ist.
# Fehlt sie, bricht die Kette hier kontrolliert ab, statt piper mit einem
# nicht existierenden Modell zu starten.
set -eu

VOICE="${1:-}"
VOICES_DIR="/usr/local/share/dialos-piper/voices"

if [ -z "$VOICE" ]; then
  echo "check_piper_voice.sh: keine Stimme angegeben" >&2
  exit 1
fi

if [ ! -f "$VOICES_DIR/$VOICE.onnx" ] || [ ! -f "$VOICES_DIR/$VOICE.onnx.json" ]; then
  echo "check_piper_voice.sh: Stimme '$VOICE' fehlt in $VOICES_DIR" >&2
  echo "check_piper_voice.sh: erwartet werden $VOICE.onnx und $VOICE.onnx.json" >&2
  exit 1
fi

exit 0
