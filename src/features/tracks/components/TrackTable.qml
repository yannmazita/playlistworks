import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: trackTable
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true

    model: trackTableModel

    property int selectedRow: -1

    delegate: Rectangle {
        required property int row
        implicitWidth: Math.max(100, trackTable.width / 3)
        implicitHeight: 40
        color: mainWindow.selectedRow === row ? "#d0e8ff" : (row % 2 ? "#f0f0f0" : "white")
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
                mainWindow.selectedRow = row;
                playbackService.handleRowClick(row);
            }
            onDoubleClicked: {
                mainWindow.selectedRow = row;
                playbackService.handleRowClick(row);
                let trackPath = trackTableModel.data(trackTableModel.index(row, 0), Qt.UserRole + 4);
                playbackService.toggle_playback(trackPath);
            }
        }
    }
}
