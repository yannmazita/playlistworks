import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "common/components"
import "features/player/components"
import "features/tracks/components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1280
    height: 720
    title: "playlistworks"

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            Action {
                text: qsTr("Add Library Folder")
                onTriggered: libraryDirectoryDialog.open()
            }
            Action {
                text: qsTr("Scan Library")
                onTriggered: console.log("Clicked Scan Library")
            }
            Action {
                text: qsTr("Quit")
                onTriggered: Qt.quit()
            }
        }
    }

    header: ToolBar {
        PlaybackControls {}
    }

    ColumnLayout {
        id: mainColumn
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width

        TrackTable {
            Layout.alignment: Qt.AlignHCenter
        }
    }

    footer: TabBar {}

    LibraryDirectoryDialog {
        id: libraryDirectoryDialog
    }
}
