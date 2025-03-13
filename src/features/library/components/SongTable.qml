import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: songTable
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true

    model: songModel

    delegate: Rectangle {
        required property int row
        implicitWidth: Math.max(100, songTable.width / 3)
        implicitHeight: 40
        color: songModel.selectedSongIndex === row ? "#d0e8ff" : (row % 2 ? "#f0f0f0" : "white")
        border.color: "#e0e0e0"

        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
            text: display
            elide: Text.ElideRight
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                playbackService.handleRowClick(row);
            }
            onDoubleClicked: {
                playbackService.handleRowClick(row);
                let songPath = songModel.data(songModel.index(row, 0), Qt.UserRole + 4);
                playbackService.toggle_playback(songPath);
            }
        }
    }
}
