import QtQuick 2.0;
import calamares.slideshow 1.0;
Presentation
{
    id: presentation
    Timer {
        interval: 20000
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
    Slide {
        Image {
            id: background1
            source: "logo-full.png"
            width: 467; height: 280
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
        Text {
            anchors.horizontalCenter: background1.horizontalCenter
            anchors.top: background1.bottom
            text: qsTr("Willkommen bei DialOS.<br/>"+
                  "Der Rest der Installation läuft automatisch und ist in wenigen Minuten abgeschlossen.")
            wrapMode: Text.WordWrap
            width: 600
            horizontalAlignment: Text.Center
        }
    }
}
