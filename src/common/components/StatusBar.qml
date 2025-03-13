import QtQuick
import QtQuick.Layouts

Rectangle {
    id: statusBar
    Layout.fillWidth: true
    height: 30
    color: "#f0f0f0"
    property int songCount: songModel.rowCount()

    Connections {
        target: backend
        function onScanFinished(error_paths) {
            statusBar.songCount = songModel.rowCount();
        }
    }

    RowLayout {
        anchors.fill: parent

        Text {
            id: statusBarText
            text: "Songs: " + statusBar.songCount
        }

        /*
        Text {
            text: currentPlaylistName
        }
        */

        Item {
            Layout.fillWidth: true
        }
    }
}
