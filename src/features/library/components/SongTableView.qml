import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: songTableRoot
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true

    function getSourceModel() {
        return backend.library.currentSongModel
    }

    model: getSourceModel()

    delegate: Rectangle {
        required property int row
        implicitWidth: Math.max(100, songTableRoot.width / 3)
        implicitHeight: 40
        color: backend.library.songModel.selectedSongIndex === row ? "#d0e8ff" : (row % 2 ? "#f0f0f0" : "white")
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
                backend.playback.handleRowClick(row);
            }
            onDoubleClicked: {
                backend.playback.handleRowClick(row);
                let songPath = getSourceModel().data(getSourceModel().index(row, 0), Qt.UserRole + 4);
                backend.playback.toggle_playback(songPath);
            }
        }
    }
}
