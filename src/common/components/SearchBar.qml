import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: searchBarRoot
    color: "#f0f0f0"

    property bool inPlaylistMode: false

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 5

        RowLayout {
            Layout.fillWidth: true

            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "Search library or create dynamic playlist..."
                font.pixelSize: 16

                onTextChanged: {
                    backend.library.searchSongs(text);
                }
            }

            Button {
                text: "Clear"
                onClicked: {
                    searchField.text = "";
                }
            }

            Button {
                text: "Create Playlist"
                onClicked: {
                    createPlaylistDialog.open();
                }
            }

            Button {
                text: "?"
                onClicked: {
                    helpDialog.open();
                }
            }
        }

        Label {
            id: queryExampleLabel
            text: "Examples: artist:\"The Knife\", (genre:Hyperpop OR genre:\"Bubblegum Bass\") AND date:>2020, !genre:jazz"
            font.italic: true
            color: "#666666"
            font.pixelSize: 12
        }
    }

    // Dialog for creating a new playlist
    Dialog {
        id: createPlaylistDialog
        title: "Create Playlist"
        modal: true
        anchors.centerIn: parent
        width: 400

        ColumnLayout {
            width: parent.width

            Label {
                text: "Playlist Name:"
            }

            TextField {
                id: playlistNameField
                Layout.fillWidth: true
                placeholderText: "Enter playlist name"
            }

            CheckBox {
                id: dynamicPlaylistCheck
                text: "Dynamic Playlist"
                checked: searchField.text !== ""
            }

            Label {
                text: "Query:"
                visible: dynamicPlaylistCheck.checked
            }

            TextField {
                id: playlistQueryField
                Layout.fillWidth: true
                text: searchField.text
                visible: dynamicPlaylistCheck.checked
                placeholderText: "Enter search query"
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            if (playlistNameField.text.trim() !== "") {
                backend.library.createPlaylist(playlistNameField.text, dynamicPlaylistCheck.checked ? playlistQueryField.text : "", dynamicPlaylistCheck.checked);
                playlistNameField.text = "";
                playlistQueryField.text = "";
            }
        }
    }
}
