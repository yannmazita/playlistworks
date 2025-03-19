import QtQuick
import QtQuick.Layouts

Item {
    id: songTableContainer
    Layout.fillWidth: true
    Layout.fillHeight: true
    property int selectedRow: -1

    Connections {
        target: backend.library.currentSelectionModel
        function onCurrentChanged() {
            let currentIndex = backend.library.currentSelectionModel.currentIndex;
            if (currentIndex.valid) {
                songTableContainer.selectedRow = currentIndex.row;
            } else {
                songTableContainer.selectedRow = -1;
            }
        }

        function onSelectionChanged() {
            let indexes = backend.library.currentSelectionModel.selectedIndexes;
            if (indexes.length > 0) {
                songTableContainer.selectedRow = indexes[0].row;
            }
        }
    }

    TableView {
        id: songTableRoot
        anchors.fill: parent
        clip: true

        model: backend.library.currentSongModel
        selectionModel: backend.library.currentSelectionModel

        delegate: Rectangle {
            required property int row
            implicitWidth: Math.max(100, songTableRoot.width / 3)
            implicitHeight: 40

            color: row === songTableContainer.selectedRow ? "#d0e8ff" : (row % 2 ? "#f0f0f0" : "white")
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
                    let modelIndex = getSourceModel().index(row, 0);
                    backend.library.setCurrentIndex(modelIndex);
                    songTableContainer.selectedRow = row;
                }
                onDoubleClicked: {
                    let modelIndex = getSourceModel().index(row, 0);
                    backend.library.setCurrentIndex(modelIndex);
                    songTableContainer.selectedRow = row;
                    let songPath = getSourceModel().data(modelIndex, Qt.UserRole + 4);
                    backend.playback.toggle_playback(songPath);
                }
            }
        }
    }

    function getSourceModel() {
        return backend.library.currentSongModel;
    }
}
