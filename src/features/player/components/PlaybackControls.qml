import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Column {
    id: playbackControlsRoot
    anchors.fill: parent
    property int playbackValue: 1

    // Format time in MM:SS format
    function formatTime(ms) {
        if (ms <= 0)
            return "0:00";

        var seconds = Math.floor(ms / 1000);
        var minutes = Math.floor(seconds / 60);
        seconds = seconds % 60;

        return minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
    }

    function getSourceModel() {
        return backend.library.currentSongModel;
    }

    Component.onCompleted: {
        playButton.text = qsTr("Play");
    }

    Connections {
        target: backend.playback
        function onPlaybackStateChanged(state) {
            if (playbackValue !== state) {
                playbackValue = state;
                if (playbackValue !== 4) {
                    playButton.text = qsTr("Play");
                } else {
                    playButton.text = qsTr("Pause");
                }
            }
        }

        function onPositionChanged(position) {
            // Update slider without triggering valueChanged
            positionSlider.blockUpdate = true;
            positionSlider.value = position;
            positionSlider.blockUpdate = false;
        }

        function onDurationChanged(duration) {
            positionSlider.to = duration;
        }
        
        function onVolumeChanged(volume) {
            // Update slider without triggering valueChanged
            volumeSlider.blockUpdate = true;
            volumeSlider.value = volume;
            volumeSlider.blockUpdate = false;
        }

        function onMuteStateChanged(muted) {
            // Update mute button text
            muteButton.text = muted ? qsTr("Unmute") : qsTr("Mute");
        }
    }

    RowLayout {
        width: parent.width
        spacing: 5

        Text {
            text: formatTime(positionSlider.value)
            font.pixelSize: 12
            Layout.preferredWidth: 40
            horizontalAlignment: Text.AlignRight
        }

        Slider {
            id: positionSlider
            from: 0
            to: 1
            value: 0
            Layout.fillWidth: true

            // Prevent feedback loop when updating from position signals
            property bool blockUpdate: false

            onMoved: {
                if (!blockUpdate) {
                    backend.playback.seek(value);
                }
            }
        }

        Text {
            text: formatTime(positionSlider.to)
            font.pixelSize: 12
            Layout.preferredWidth: 40
        }
    }

    // Container volume and playback controls
    Item {
        width: parent.width
        height: Math.max(volumeControls.height, playbackControls.height)
        
        Row {
            id: volumeControls
            spacing: 5
            anchors.left: parent.left
            
            Button {
                id: muteButton
                text: backend.playback.isMuted ? qsTr("Unmute") : qsTr("Mute")
                width: 80
                onClicked: {
                    backend.playback.toggle_mute();
                }
            }
            
            Slider {
                id: volumeSlider
                from: 0.0
                to: 1.0
                value: backend.playback.volume
                width: 120
                
                // Prevent feedback loop when updating from volume signals
                property bool blockUpdate: false
                
                onMoved: {
                    if (!blockUpdate) {
                        backend.playback.volume = value;
                        // If muted, unmute when user adjusts volume
                        if (backend.playback.isMuted && value > 0) {
                            backend.playback.isMuted = false;
                        }
                    }
                }
            }
            
            Text {
                text: Math.round(volumeSlider.value * 100) + "%"
                font.pixelSize: 12
                width: 40
                verticalAlignment: Text.AlignVCenter
                height: volumeSlider.height
            }
        }

        Row {
            id: playbackControls
            spacing: 10
            anchors.horizontalCenter: parent.horizontalCenter

            Button {
                id: skipBackButton
                text: qsTr("Back")
                onClicked: {
                    backend.playback.skip_backward();
                }
            }

            Button {
                id: playButton
                onClicked: {
                    // If a song is already playing or paused, control that song
                    if (backend.playback.currentTrackPath) {
                        // Just toggle the current song's state without specifying a path
                        backend.playback.toggle_playback("");
                    } else
                    // Otherwise start playing the selected song
                    if (backend.library.songModel.selectedSongIndex !== -1) {
                        let songPath = getSourceModel().data(backend.library.songModel.index(getSourceModel().selectedSongIndex, 0), getSourceModel().pathRole);
                        backend.playback.toggle_playback(songPath);
                    }
                }
            }

            Button {
                id: skipForwardButton
                text: qsTr("Forward")
                onClicked: {
                    backend.playback.skip_forward();
                }
            }
        }
    }
}
