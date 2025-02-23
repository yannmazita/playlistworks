import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "features/player/components"

Window {
    id: mainWindow
    visible: true
    width: 1280
    height: 720
    title: "playlistworks"

    ColumnLayout {
        id: mainColumn
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width

        PlaybackControls {
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
