import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: settingsDialogRoot
    title: "Settings"
    modal: true
    parent: Overlay.overlay
    anchors.centerIn: parent
    standardButtons: Dialog.Ok | Dialog.Cancel
    width: 400
    height: 500

    Component.onCompleted: {
        let columns = backend.library.currentSongModel.availableColumns;
    }

    onAccepted: {
        let newVisibleColumns = [];
        for (let i = 0; i < columnRepeater.count; i++) {
            let checkBox = columnRepeater.itemAt(i);
            if (checkBox.checked) {
                newVisibleColumns.push(checkBox.columnId);
            }
        }
        backend.library.currentSongModel.visibleColumns = newVisibleColumns;
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 15

        GroupBox {
            title: "Visible Columns"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ScrollView {
                anchors.fill: parent
                clip: true

                ColumnLayout {
                    spacing: 10
                    width: parent.width

                    Repeater {
                        id: columnRepeater
                        model: backend.library.currentSongModel ? backend.library.currentSongModel.availableColumns : []

                        CheckBox {
                            property int columnId: modelData.id
                            text: modelData.name + " (ID: " + modelData.id + ")"
                            checked: backend.library.currentSongModel ? backend.library.currentSongModel.visibleColumns.includes(modelData.id) : false
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }

        Label {
            text: "* Title, Artist, and Album columns are available to toggle"
            font.italic: true
            Layout.fillWidth: true
        }
    }
}
