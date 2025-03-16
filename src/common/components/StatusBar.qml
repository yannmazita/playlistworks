# StatusBar.qml
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: statusBar
    Layout.fillWidth: true
    color: "#f0f0f0"
    property int songCount: backend.library.songModel.rowCount()

    // Repeat mode constants (mirroring PlaybackService)
    readonly property int repeatOff: 0
    readonly property int repeatAll: 1
    readonly property int repeatTrack: 2
    readonly property int repeatOneSong: 3

    // Helper function to get the currently active repeat mode
    function getActiveRepeatMode() {
        if (repeatAllOption.checked) return repeatAll;
        if (repeatTrackOption.checked) return repeatTrack;
        if (oneSongOption.checked) return repeatOneSong;
        return repeatOff; // Default to off
    }

    Connections {
        target: backend
        function onScanFinished(error_paths) {
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
            switch (repeatMode) {
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
                default: // repeatOff
                    repeatButton.checked = false;
            }
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
                    checked: backend.playback.repeatMode != repeatOff // Checked if not OFF
                    Layout.preferredHeight: shuffleButton.height

                    background: Rectangle {
                        color: repeatButton.checked ? "#a0c0e0" : "transparent"
                    }

                    onClicked: {
                        // Toggle between repeatOff and the active repeat mode
                        if (backend.playback.repeatMode === repeatOff) {
                            backend.playback.set_repeat_mode(getActiveRepeatMode());
                        } else {
                            backend.playback.set_repeat_mode(repeatOff);
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
                                backend.playback.set_repeat_mode(repeatAll);
                            }
                        }

                        MenuItem {
                            id: repeatTrackOption
                            checkable: true
                            text: qsTr("Repeat this track")
                            ButtonGroup.group: repeatGroup

                            onTriggered: {
                                backend.playback.set_repeat_mode(repeatTrack);
                            }
                        }

                        MenuItem {
                            id: oneSongOption
                            checkable: true
                            text: qsTr("One song")
                            ButtonGroup.group: repeatGroup

                            onTriggered: {
                                backend.playback.set_repeat_mode(repeatOneSong);
                            }
                        }
                    }
                }
            }
        }

        Text {
            id: statusBarText
            text: "Songs: " + statusBar.songCount
            Layout.alignment: Qt.AlignVCenter
        }
    }
}
