import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "common/components"
import "features/player/components"
import "features/playlists/components"
import "features/library/components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 800
    height: 600
    title: "playlistworks"

    HelpDialog {
        id: helpDialog
    }
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
        Menu {
            title: qsTr("Help")
            Action {
                text: qsTr("Query Syntax")
                onTriggered: helpDialog.open()
            }
        }
    }

    header: ToolBar {
        PlaybackControls {
            id: playbackControls
        }
    }

    SplitView {
        anchors.fill: parent

        PlaylistSidebar {
            id: playlistSidebar
            SplitView.preferredWidth: 300
            SplitView.minimumWidth: 200
        }

        ColumnLayout {
            id: mainColumn
            SplitView.fillWidth: true

            SearchBar {
                id: searchBar
                Layout.fillWidth: true
                Layout.preferredHeight: 80
            }

            SongTableView {
                id: songTableView
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }

    footer: ToolBar {
        StatusBar {
            id: statusBar
        }
    }
}
