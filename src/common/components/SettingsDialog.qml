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

    property var currentModel: backend.library.currentSongModel

    // Define the desired canonical order of *all* columns.
    // This order determines the sequence in the table view when columns are visible.
    // Using the order derived from the default visible columns + the rest:
    // (#, Length, Title, Artist, Album, Genre, Date, Description, Album Artist, Composer, Disc, BPM, Comment, Compilation, Bitrate, Path)
    // Todo: Get it from python instead
    readonly property list<int> canonicalColumnOrder: [
        0, 13, 1, 2, 3, 4, 8, 5, 6, 7, 9, 10, 11, 12, 14, 15
    ]

    Component.onCompleted: {
        if (!currentModel) {
            console.warn("SettingsDialog: currentSongModel is not available on completion.");
        }
    }

    onAccepted: {
        if (!currentModel) {
            console.error("SettingsDialog: Cannot apply settings, currentSongModel is null.");
            return;
        }

        let checkboxStates = {};
        for (let i = 0; i < columnRepeater.count; i++) {
            let checkBox = columnRepeater.itemAt(i);
            if (checkBox) { // Basic check if item exists
                checkboxStates[checkBox.columnId] = checkBox.checked;
            } else {
                 console.warn("SettingsDialog: Repeater item at index", i, "is null/undefined.");
            }
        }

        let newVisibleColumns = [];
        for (let i = 0; i < canonicalColumnOrder.length; i++) {
            let columnId = canonicalColumnOrder[i];
            // If a column ID exists in the canonical list and its checkbox was checked, add it.
            if (checkboxStates.hasOwnProperty(columnId) && checkboxStates[columnId] === true) {
                newVisibleColumns.push(columnId);
            }
        }
        currentModel.visibleColumns = newVisibleColumns;
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
                        model: currentModel ? currentModel.availableColumns : []

                        delegate: CheckBox {
                            property int columnId: modelData.id // ID from availableColumns
                            text: modelData.name // Name from availableColumns
                            // Determine initial checked state by looking up ID in the model's current visible list
                            checked: {
                                if (!settingsDialogRoot.currentModel) return false;
                                // Ensure visibleColumns is treated as an array for includes()
                                var visible = settingsDialogRoot.currentModel.visibleColumns;
                                // QVariantList might not directly have .includes, safer check:
                                var isVisible = false;
                                if (Array.isArray(visible)) {
                                     isVisible = visible.includes(modelData.id);
                                // Assume QVariantList-like, iterate
                                } else {
                                     let jsVisible = Array.from(visible || []);
                                     isVisible = jsVisible.includes(modelData.id);
                                }
                                return isVisible;
                            }
                            Layout.fillWidth: true

                            ToolTip.visible: hovered
                            ToolTip.text: "Column ID: " + modelData.id
                        }
                    }
                }
            }
        }
    }
}
