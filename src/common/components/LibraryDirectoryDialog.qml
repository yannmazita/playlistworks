import QtQuick.Dialogs
import QtCore

FolderDialog {
    id: libraryDirectoryRoot
    currentFolder: StandardPaths.standardLocations(StandardPaths.HomeLocation)[0]
    onAccepted: directoryHandler.handleDirectorySelected(selectedFolder)
}
