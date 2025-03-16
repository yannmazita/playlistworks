import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
                text: "Common Fields:"
                font.bold: true
            }
            Text {
                text: "These are known common fields, any metadata field in your audio files can be searched"
                font.italic: true
                color: "#666666"
                font.pixelSize: 12
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
                        text: "artist:\"Depeche Mode\" and date:<1990"
                        font.family: "Courier"
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "(genre:Hyperpop OR genre:\"Bubblegum Bass\") AND date:>2020"
                        font.family: "Courier"
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "!genre:jazz"
                        font.family: "Courier"
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "artist:Cool and !artist=\"LL Cool J\""
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
                text: "• Remember ANY field can be searched. This is the flexibility of the query language.\n• Text searches are case-insensitive\n• For exact matches, use quotes (myfield:\"\my match\")\n• For partial matches, don't use quotes (myfield:my match)\n• Use parentheses to control the order of evaluation\n• Combine multiple conditions with and/or operators"
                wrapMode: Text.WordWrap
            }

            Item {
                Layout.fillHeight: true
            }
        }
    }
}
