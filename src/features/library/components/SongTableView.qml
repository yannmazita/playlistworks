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
        columnWidthProvider: function (column) {
            if (!model || !model.hasOwnProperty("visibleColumns") || !model.hasOwnProperty("columnWidths")) {
                console.warn("Model or required properties (visibleColumns/columnWidths) not available.");
                return 80; // Default width
            }

            let rawVisibleCols = model.visibleColumns;
            let widthMap = model.columnWidths;

            let jsVisibleCols;
            try {
                jsVisibleCols = Array.from(rawVisibleCols);
            } catch (e) {
                console.error("Failed to convert visibleColumns to JS Array:", e);
                console.log("Raw visibleColumns was:", rawVisibleCols, "Type:", typeof rawVisibleCols);
                jsVisibleCols = [];
            }

            if (!Array.isArray(jsVisibleCols) || typeof widthMap !== 'object' || widthMap === null) {
                console.warn(">>> Invalid type detected! jsVisibleCols isArray:", Array.isArray(jsVisibleCols), "columnWidths typeof:", typeof widthMap);
                return 80;
            }

            if (column >= 0 && column < jsVisibleCols.length) {
                let absoluteColumnId = jsVisibleCols[column];
                let key = String(absoluteColumnId);

                if (widthMap.hasOwnProperty(key)) {
                    let width = widthMap[key];
                    return (typeof width === 'number' && width > 0) ? width : 80;
                } else {
                    // This might happen if visibleColumns contains an ID not in columnWidths (shouldn't ideally)
                    console.log("No width defined in model.columnWidths for column ID:", absoluteColumnId, "(View column:", column, ", Key:", key + ")");
                }
            } else {
                // This might happen briefly during model resets or if column index is somehow invalid
                console.warn("Column index out of bounds:", column, "Visible columns count:", jsVisibleCols.length);
            }

            // Default width if specific width not found or index out of bounds
            return 80;
        }
        onWidthChanged: songTableRoot.forceLayout()

        delegate: Rectangle {
            required property int row
            implicitWidth: songTableRoot.columnWidthProvider(column)
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
