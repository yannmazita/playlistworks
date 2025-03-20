import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: playlistSidebarRoot
    color: "#f0f0f0"

    property int selectedPlaylistRow: -1

    Connections {
        target: backend.library.playlistSelectionModel
        function onCurrentChanged() {
            let currentIndex = backend.library.playlistSelectionModel.currentIndex;
            if (currentIndex.valid) {
                playlistSidebarRoot.selectedPlaylistRow = currentIndex.row;
            } else {
                playlistSidebarRoot.selectedPlaylistRow = -1;
            }
        }

        function onSelectionChanged() {
            let indexes = backend.library.playlistSelectionModel.selectedIndexes;
            if (indexes.length > 0) {
                playlistSidebarRoot.selectedPlaylistRow = indexes[0].row;
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Label {
            text: "Library"
            font.bold: true
            font.pixelSize: 18
        }

        Button {
            Layout.fillWidth: true
            text: "All Songs"
            onClicked: {
                backend.library.playlistMode = false;
                backend.library.playlistSelectionModel.clearSelection();
                playlistSidebarRoot.selectedPlaylistRow = -1;
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#c0c0c0"
        }

        Label {
            text: "Playlists"
            font.bold: true
            font.pixelSize: 18
        }

        TableView {
            id: playlistTableView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            columnSpacing: 0
            rowSpacing: 0
            width: parent.width

            columnWidthProvider: function (column) {
                return playlistTableView.width;
            }

            model: backend.library.playlistModel
            selectionModel: backend.library.playlistSelectionModel

            delegate: Rectangle {
                required property int row
                required property string name
                required property int playlistId
                required property bool isDynamic
                required property string query
                implicitWidth: playlistTableView.width
                height: 50

                color: row === playlistSidebarRoot.selectedPlaylistRow ? "#d0e8ff" : (row % 2 ? "#f0f0f0" : "white")
                border.color: "#e0e0e0"

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        backend.library.playlistMode = true;
                        let modelIndex = backend.library.playlistModel.index(row, 0);
                        backend.library.playlistSelectionModel.setCurrentIndex(modelIndex, ItemSelectionModel.ClearAndSelect | ItemSelectionModel.Current);
                        backend.library.setCurrentPlaylist(playlistId);

                        playlistSidebarRoot.selectedPlaylistRow = row;
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5

                    Label {
                        text: name
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Label {
                        text: isDynamic ? "✿" : ""
                        font.pixelSize: 16
                        ToolTip.text: isDynamic ? "Dynamic playlist: " + query : ""
                        ToolTip.visible: isDynamic && playlistLabelMouseArea.containsMouse

                        MouseArea {
                            id: playlistLabelMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                        }
                    }

                    ToolButton {
                        id: editPlaylistButton
                        text: qsTr("Edit")

                        onClicked: {
                            playlistEditionDialog.setPlaylistDetails(playlistId, name, query, isDynamic);
                            playlistEditionDialog.open();
                        }
                    }

                    ToolButton {
                        id: deletePlaylistButton
                        text: qsTr("Delete")

                        onClicked: {
                            deleteConfirmDialog.playlistToDelete = playlistId;
                            deleteConfirmDialog.playlistName = name;
                            deleteConfirmDialog.open();
                        }
                    }
                }
            }
        }
    }

    PlaylistDeletionDialog {
        id: deleteConfirmDialog
    }
    PlaylistEditionDialog {
        id: playlistEditionDialog
    }
}
