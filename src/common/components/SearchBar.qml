import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

RowLayout {
    Layout.fillWidth: true
    spacing: 10

    property string currentQuery: ""

    signal search(string query)
    signal clearSearch

    Text {
        text: "Search:"
        font.pixelSize: 16
    }

    TextField {
        id: searchField
        Layout.fillWidth: true
        placeholderText: "Enter search query (e.g., artist=\"The Knife\" or genre=\"Tech House\")"
        text: currentQuery

        onAccepted: search(text)
    }

    Button {
        text: "Search"
        onClicked: search(searchField.text)
    }

    Button {
        text: "Clear"
        onClicked: clearSearch()
    }
}
