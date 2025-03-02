import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "features/player/components"
import "features/tracks/components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1280
    height: 720
    title: "playlistworks"

    menuBar: MenuBar {}
    header: ToolBar {}
    footer: TabBar {}

    ColumnLayout {
        id: mainColumn
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width

        PlaybackControls {
            Layout.alignment: Qt.AlignHCenter
        }
        TrackTable {
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
