import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

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

    HorizontalHeaderView {
        id: horizontalHeader
        syncView: songTableRoot
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        clip: true
    }

    TableView {
        id: songTableRoot
        anchors.top: horizontalHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true

        model: backend.library.currentSongModel
        selectionModel: backend.library.currentSelectionModel

        delegate: Rectangle {
            required property int row
            implicitWidth: 100
            implicitHeight: 40

            color: row === songTableContainer.selectedRow ? "#d0e8ff" : (row % 2 ? "#f0f0f0" : "white")
            border.color: "#e0e0e0"

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 10
                width: parent.width - 20
                text: display
                elide: Text.ElideRight
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    let modelIndex = getSourceModel().index(row, 0);
                    backend.library.setCurrentIndex(modelIndex);
                }
                onDoubleClicked: {
                    let modelIndex = getSourceModel().index(row, 0);
                    let pathRole = getSourceModel().pathRole;
                    backend.library.setCurrentIndex(modelIndex);
                    let songPath = getSourceModel().data(modelIndex, pathRole);
                    backend.playback.toggle_playback(songPath);
                }
            }
        }
    }

    function getSourceModel() {
        return backend.library.currentSongModel;
    }
}
