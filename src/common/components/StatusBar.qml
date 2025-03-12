import QtQuick
import QtQuick.Layouts

Rectangle {
    Layout.fillWidth: true
    height: 30
    color: "#f0f0f0"

    RowLayout {
        anchors.fill: parent

        Text {
            text: "Songs: " + trackTableModel.rowCount()
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
