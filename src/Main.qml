import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "common/components"
import "features/player/components"
import "features/tracks/components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 800
    height: 600
    title: "playlistworks"

    property int selectedRow: -1

    Connections {
        target: playbackService

        function onRowSelectedChanged(row) {
        }
    }

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            Action {
                text: qsTr("Add Library Folder")
                onTriggered: libraryDirectoryDialog.open()
            }
            Action {
                text: qsTr("Scan Library")
                onTriggered: {
                    scanProgressDialog.open();
                    backend.scan_library();
                }
            }
            Action {
                text: qsTr("Quit")
                onTriggered: Qt.quit()
            }
        }
    }

    header: ToolBar {
        PlaybackControls {}
    }

    ColumnLayout {
        id: mainColumn
        anchors.fill: parent

        TrackTable {}
    }

    footer: ToolBar {}

    LibraryDirectoryDialog {
        id: libraryDirectoryDialog
    }

    Dialog {
        id: scanProgressDialog
        title: "Scanning Library"
        modal: true
        closePolicy: Dialog.NoAutoClose

        Label {
            text: "Scanning library files, please wait..."
        }

        BusyIndicator {
            running: true
        }

        Component.onCompleted: {
            backend.scanStarted.connect(() => {
                scanProgressDialog.open();
            });

            backend.scanFinished.connect(() => {
                scanProgressDialog.close();
            });

            backend.scanError.connect(errorMessage => {
                scanProgressDialog.close();
                errorDialog.text = errorMessage;
                errorDialog.open();
            });
        }
    }

    Dialog {
        id: errorDialog
        title: "Error"
        modal: true
        property string text: ""

        Label {
            text: errorDialog.text
        }

        standardButtons: Dialog.Ok
    }
}
