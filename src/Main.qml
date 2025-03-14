import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "common/components"
import "features/player/components"
import "features/library/components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 800
    height: 600
    title: "playlistworks"

    LibraryDirectoryDialog {
        id: libraryDirectoryDialog
    }
    LibraryScanningDialog {
        id: libraryScanningDialog
    }
    ErrorDialog {
        id: errorDialog
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
                    libraryScanningDialog.open();
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
        Layout.fillWidth: true

        SearchBar {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
        }

        SongTableView {
            id: songTable
        }
    }

    footer: ToolBar {
        StatusBar {
            id: statusBar
        }
    }
}
