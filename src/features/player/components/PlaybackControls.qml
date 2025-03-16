import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

Column {
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

    // Playback controls
    Row {
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
              }
              // Otherwise start playing the selected song
              else if (backend.library.songModel.selectedSongIndex !== -1) {
                  let songPath = backend.library.songModel.data(
                      backend.library.songModel.index(backend.library.songModel.selectedSongIndex, 0), 
                      Qt.UserRole + 4
                  );
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
