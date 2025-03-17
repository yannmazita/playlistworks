import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: sidebarRoot
    color: "#f0f0f0"

    function showLibrary() {
        songTableView.inPlaylistMode = false;
        songTableView.currentPlaylistId = -1;
    }

    function showPlaylist(playlistId) {
        songTableView.inPlaylistMode = true;
        songTableView.currentPlaylistId = playlistId;
        backend.playlist.setCurrentPlaylist(playlistId);
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
                showLibrary();
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

        ListView {
            id: playlistListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            model: backend.library.playlistModel

            delegate: Rectangle {
                width: playlistListView.width
                height: 50
                color: "transparent"

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        playlistListView.currentIndex = index;
                        showPlaylist(playlistId);
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
                        text: isDynamic ? "🔄" : ""
                        font.pixelSize: 16
                        ToolTip.text: isDynamic ? "Dynamic playlist: " + query : ""
                        ToolTip.visible: isDynamic && ma.containsMouse

                        MouseArea {
                            id: ma
                            anchors.fill: parent
                            hoverEnabled: true
                        }
                    }

                    Button {
                        text: "×"
                        width: 30
                        height: 30

                        onClicked: {
                            deleteConfirmDialog.playlistToDelete = playlistId;
                            deleteConfirmDialog.playlistName = name;
                            deleteConfirmDialog.open();
                        }
                    }
                }
            }

            highlight: Rectangle {
                color: "#d0d0ff"
                opacity: 0.5
            }

            highlightFollowsCurrentItem: true
        }
    }

    PlaylistDeletionDialog {
        id: deleteConfirmDialog
    }
}
