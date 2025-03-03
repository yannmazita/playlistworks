import QtQuick.Dialogs
import QtCore

FolderDialog {
    currentFolder: StandardPaths.standardLocations(StandardPaths.HomeLocation)[0]
    onAccepted: directoryHandler.handleDirectorySelected(selectedFolder)
}
