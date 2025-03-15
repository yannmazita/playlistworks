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

    // Dialog for showing search syntax help
    Dialog {
        id: helpDialog
        title: "Help - Query Syntax"
        modal: true
        anchors.centerIn: parent
        width: 600
        height: 500
        standardButtons: Dialog.Close

        ScrollView {
            anchors.fill: parent
            clip: true

            ColumnLayout {
                width: helpDialog.width - 40
                spacing: 10

                Text {
                    Layout.fillWidth: true
                    text: "Query Syntax for Dynamic Playlists"
                    font.pixelSize: 18
                    font.bold: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    color: "#d0d0d0"
                }

                Text {
                    Layout.fillWidth: true
                    text: "Basic Search"
                    font.pixelSize: 16
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: "Simple text searches will match any song where any field contains the text."
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: "Examples: Beatles, 1970, Rock"
                    wrapMode: Text.WordWrap
                    font.italic: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    color: "#d0d0d0"
                    Layout.topMargin: 5
                }

                Text {
                    Layout.fillWidth: true
                    text: "Structured Queries"
                    font.pixelSize: 16
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: "Searchable Fields:"
                    font.bold: true
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 5

                    Text {
                        text: "title"
                        font.bold: true
                    }
                    Text {
                        text: "Song title (text)"
                    }

                    Text {
                        text: "artist"
                        font.bold: true
                    }
                    Text {
                        text: "Artist name (text)"
                    }

                    Text {
                        text: "album"
                        font.bold: true
                    }
                    Text {
                        text: "Album name (text)"
                    }

                    Text {
                        text: "genre"
                        font.bold: true
                    }
                    Text {
                        text: "Music genre (text)"
                    }

                    Text {
                        text: "date"
                        font.bold: true
                    }
                    Text {
                        text: "Release date"
                    }

                    Text {
                        text: "path"
                        font.bold: true
                    }
                    Text {
                        text: "File path (text)"
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: "Comparison Operators:"
                    font.bold: true
                    Layout.topMargin: 5
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 5

                    Text {
                        text: "="
                        font.bold: true
                    }
                    Text {
                        text: "Equality (works with all fields)"
                    }

                    Text {
                        text: "contains"
                        font.bold: true
                    }
                    Text {
                        text: "Substring match (for text fields)"
                    }

                    Text {
                        text: "<, <="
                        font.bold: true
                    }
                    Text {
                        text: "Less than, less than or equal (for numbers)"
                    }

                    Text {
                        text: ">, >="
                        font.bold: true
                    }
                    Text {
                        text: "Greater than, greater than or equal (for numbers)"
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: "Logical Operators:"
                    font.bold: true
                    Layout.topMargin: 5
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 5

                    Text {
                        text: "and"
                        font.bold: true
                    }
                    Text {
                        text: "Both conditions must be true"
                    }

                    Text {
                        text: "or"
                        font.bold: true
                    }
                    Text {
                        text: "At least one condition must be true"
                    }

                    Text {
                        text: "( )"
                        font.bold: true
                    }
                    Text {
                        text: "Parentheses for grouping expressions"
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: "Query Structure:"
                    font.bold: true
                    Layout.topMargin: 5
                }

                Text {
                    Layout.fillWidth: true
                    text: "field operator value [logical_operator field operator value]..."
                    font.family: "Courier"
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: "Values can be enclosed in single or double quotes: \"value\" or 'value'"
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: "Examples:"
                    font.bold: true
                    Layout.topMargin: 10
                }

                Rectangle {
                    Layout.fillWidth: true
                    color: "#f0f0f0"
                    Layout.preferredHeight: examplesColumn.height + 20
                    radius: 5

                    ColumnLayout {
                        id: examplesColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 10
                        spacing: 10

                        Text {
                            Layout.fillWidth: true
                            text: "genre=\"Rock\" and date<1980"
                            font.family: "Courier"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "artist contains \"Beatles\" or artist contains \"Queen\""
                            font.family: "Courier"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "date>=1970 and date<1980 and genre=\"Rock\""
                            font.family: "Courier"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "(artist=\"Michael Jackson\" or artist=\"Prince\") and date>1980"
                            font.family: "Courier"
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "album contains \"Greatest\" or title contains \"Love\""
                            font.family: "Courier"
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: "Tips:"
                    font.bold: true
                    Layout.topMargin: 10
                }

                Text {
                    Layout.fillWidth: true
                    text: "• Text searches are case-insensitive\n• For exact matches, use the equality operator (=)\n• For partial matches, use the contains operator\n• Use parentheses to control the order of evaluation\n• Combine multiple conditions with and/or operators"
                    wrapMode: Text.WordWrap
                }

                Item {
                    Layout.fillHeight: true
                }
            }
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
