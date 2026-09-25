<!--
Entwurf fuer eine Neuigkeit auf dialos.org - von Stephan am 2026-09-25
freigegeben ("Passt so"). NOCH NICHT VEROEFFENTLICHT: Die WordPress-
Zugangsdaten (.env) liegen auf dem zweiten Rechner, nicht auf dem T490.
Offen vor dem Veroeffentlichen: englische Fassung und Hoerfassung (wie bei
den bisherigen Beitraegen), und der Absatz zum Mikrofon ist seit dem Abend des
2026-09-25 auf dem geklaerten Stand (zu fruehes Antworten, nicht das Mikrofon).
-->

# Ein Gerät, eine Anleitung, ein Nachmittag

Am 25. September wurde das DialOS-Testgerät komplett gelöscht und neu aufgebaut: leere Platte, frisches Debian, beide Konten neu. Nicht, weil etwas kaputt war, sondern um eine Frage zu beantworten: Lässt sich DialOS aus der eigenen Anleitung heraus nachbauen, ohne dass jemand im Kopf hat, was fehlt?

Die Antwort ist: fast. Und das „fast" ist der eigentliche Gewinn dieses Tages.

Die Anleitung war dabei selbst der Prüfling. Jeder Handgriff, der nicht darin stand, galt als Lücke und wurde sofort nachgetragen. Es wurden acht.

Die ernsteste war eine, die gar nicht aufgetreten ist. Beim Einrichten des Sicherheits-Sticks bietet DialOS eine Liste an, welches Gerät dafür gelöscht werden soll. In dieser Liste stand gleichrangig neben dem Stick auch die externe Festplatte mit allen Sicherungen. Ein Klick daneben, und alles wäre weg gewesen. Aufgefallen ist das beim Durchsehen vor dem Start, nicht durch einen Schaden. Seitdem erscheinen Laufwerke, die gerade in Gebrauch sind, gar nicht mehr in dieser Liste.

Die hörbarste Lücke kam nach dem Neustart. Die Stimme sprach zu schnell und stellte sich mit dem falschen Namen vor. Die zweite Stimme, Anna, war zwar eingestellt, aber nie installiert worden. Dieser Schritt stand nur in der Beschreibung, nicht im Aufbau-Skript. Dasselbe Muster wie so oft: Was nur aufgeschrieben ist, wird beim nächsten Mal vergessen. Was im Skript steht, nicht.

Der Rest war kleiner, aber genauso lehrreich: Befehle, die im PDF mitten in einer Internetadresse umbrachen. Ein Einrichtungs-Skript, dem in der Anleitung das „sudo" fehlte. Kein Hinweis darauf, dass ein bereits benutzter Sicherheits-Stick vorher gesichert werden muss. Und kein Hinweis darauf, das frisch installierte System zuerst auf den neuesten Stand zu bringen.

Und eine Frage, die zuerst nach einem Fehler aussah: Im neuen Nutzerkonto ließ sich die erste Frage des Geräts, die nach der Lautstärke, nicht beantworten. Der Verdacht fiel aufs Mikrofon. Es lag aber an der Reihenfolge: Die Antwort kam, bevor das Gerät zuhörte. Beim zweiten Versuch, mit etwas Geduld, hat es geklappt. Dabei fiel noch etwas auf: In beiden Konten war das Mikrofon ohne Echo-Unterdrückung eingestellt. DialOS selbst wählt das richtige von allein, andere Programme nicht. Das soll künftig von Anfang an stimmen.

Die Anleitung ist danach von zehn auf zwölf Seiten gewachsen. Jede neue Zeile darin ist ein Fehler, den beim nächsten Gerät niemand mehr machen muss.
