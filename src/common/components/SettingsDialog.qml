// SettingsDialog.qml
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
    
    property var songModel: backend.library.currentSongModel
    
    onAccepted: {
        // Apply visible columns setting
        let newVisibleColumns = [];
        for (let i = 0; i < columnRepeater.count; i++) {
            let checkBox = columnRepeater.itemAt(i);
            if (checkBox.checked) {
                newVisibleColumns.push(checkBox.columnName);
            }
        }
        songModel.setVisibleColumns(newVisibleColumns);
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
                        model: songModel ? songModel.getAllAvailableColumns() : []
                        
                        CheckBox {
                            property string columnName: modelData
                            text: modelData  // Display the column name
                            checked: songModel ? songModel.isColumnVisible(modelData) : false
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
        
        Label {
            text: "* ID and Path columns are always present but may be hidden from view"
            font.italic: true
            Layout.fillWidth: true
        }
    }
    
    Component.onCompleted: {
        if (songModel) {
            // Force update checkboxes based on current visible columns
            for (let i = 0; i < columnRepeater.count; i++) {
                let checkBox = columnRepeater.itemAt(i);
                checkBox.checked = songModel.isColumnVisible(checkBox.columnName);
            }
        }
    }
}
