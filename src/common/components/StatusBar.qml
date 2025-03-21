import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: statusBar
    Layout.fillWidth: true
    color: "#f0f0f0"
    property int songCount: backend.library.songModel.rowCount()
    property bool isScanning: false
    property string scanningMessage: "Scanning library files..."

    // Repeat mode constants (mirroring PlaybackService)
    readonly property int repeatOff: 0
    readonly property int repeatAll: 1
    readonly property int repeatTrack: 2
    readonly property int repeatOneSong: 3

    function getActiveRepeatMode() {
        if (repeatAllOption.checked)
            return repeatAll;
        if (repeatTrackOption.checked)
            return repeatTrack;
        if (oneSongOption.checked)
            return repeatOneSong;
        return repeatOff; // Default to off
    }

    Connections {
        target: backend.library
        function onSongsChanged() {
            statusBar.songCount = backend.library.songModel.rowCount();
        }
        function onCurrentPlaylistSongsChanged() {
            statusBar.songCount = backend.library.songModel.rowCount();
        }
    }

    Connections {
        target: backend.playback

        onShuffleModeChanged: {
            shuffleButton.checked = shuffleMode;
        }

        onRepeatModeChanged: {
            // Update repeat button and menu selection
            switch (backend.playback.repeatMode) {
            case repeatAll:
                repeatButton.checked = true;
                repeatAllOption.checked = true;
                break;
            case repeatTrack:
                repeatButton.checked = true;
                repeatTrackOption.checked = true;
                break;
            case repeatOneSong:
                repeatButton.checked = true;
                oneSongOption.checked = true;
                break;
            default:
                // repeatOff
                repeatButton.checked = false;
            }
        }
    }

    Connections {
        target: backend
        function onScanStarted() {
            statusBar.isScanning = true;
        }
        function onScanFinished() {
            statusBar.isScanning = false;
        }
        function onScanError(errorMessage) {
            statusBar.isScanning = false;
            errorDialog.text = errorMessage;
            errorDialog.open();
        }
    }

    RowLayout {
        anchors.fill: parent

        ToolButton {
            id: shuffleButton
            text: qsTr("Shuffle")
            checkable: true
            checked: backend.playback.shuffleMode
            Layout.preferredHeight: 40

            background: Rectangle {
                color: shuffleButton.checked ? "#a0c0e0" : "transparent"
            }

            onClicked: {
                backend.playback.toggle_shuffle();
            }
        }

        Rectangle {
            Layout.preferredHeight: shuffleButton.height
            Layout.preferredWidth: repeatButton.width + repeatOption.width
            color: "#e0e0e0"

            RowLayout {
                anchors.fill: parent
                spacing: 0

                ToolButton {
                    id: repeatButton
                    text: qsTr("Repeat")
                    checkable: true
                    checked: backend.playback.repeatMode != repeatOff
                    Layout.preferredHeight: shuffleButton.height

                    background: Rectangle {
                        color: repeatButton.checked ? "#a0c0e0" : "transparent"
                    }

                    onClicked: {
                        // Toggle between repeatOff and the active repeat mode
                        if (backend.playback.repeatMode === repeatOff) {
                            backend.playback.repeatMode = getActiveRepeatMode();
                        } else {
                            backend.playback.repeatMode = repeatOff;
                        }
                    }
                }

                ToolButton {
                    id: repeatOption
                    text: qsTr("▼")
                    implicitWidth: 24
                    Layout.preferredHeight: shuffleButton.height

                    onClicked: repeatMenu.popup()

                    Menu {
                        id: repeatMenu
                        y: repeatOption.height
                        ButtonGroup {
                            id: repeatGroup
                        }

                        MenuItem {
                            id: repeatAllOption
                            checkable: true
                            text: qsTr("Repeat all")
                            ButtonGroup.group: repeatGroup

                            onTriggered: {
                                backend.playback.repeatMode = repeatAll;
                            }
                        }

                        MenuItem {
                            id: repeatTrackOption
                            checkable: true
                            text: qsTr("Repeat this track")
                            ButtonGroup.group: repeatGroup

                            onTriggered: {
                                backend.playback.repeatMode = repeatTrack;
                            }
                        }

                        MenuItem {
                            id: oneSongOption
                            checkable: true
                            text: qsTr("One song")
                            ButtonGroup.group: repeatGroup

                            onTriggered: {
                                backend.playback.repeatMode = repeatOneSong;
                            }
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
        }

        Text {
            id: statusBarText
            text: "Songs: " + statusBar.songCount
            Layout.alignment: Qt.AlignVCenter
            Layout.rightMargin: 10
        }

        // Scanning status indicator
        RowLayout {
            visible: statusBar.isScanning
            spacing: 5
            Layout.rightMargin: 10

            BusyIndicator {
                running: statusBar.isScanning
                Layout.preferredHeight: 24
                Layout.preferredWidth: 24
            }

            Text {
                text: statusBar.scanningMessage
                font.italic: true
            }
        }
    }
}
