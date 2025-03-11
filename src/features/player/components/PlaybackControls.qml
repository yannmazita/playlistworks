import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

Column {
    spacing: 10
    property int playbackValue: 1
    
    // Format time in MM:SS format
    function formatTime(ms) {
        if (ms <= 0) return "0:00";
        
        var seconds = Math.floor(ms / 1000);
        var minutes = Math.floor(seconds / 60);
        seconds = seconds % 60;
        
        return minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
    }
    
    Component.onCompleted: {
        playButton.text = qsTr("Play");
    }
    
    Connections {
        target: playbackService
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
                    playbackService.seek(value);
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
                playbackService.skip_backward();
            }
        }
        
        Button {
            id: playButton
            onClicked: {
                if (trackTableModel.selectedTrackIndex !== -1) {
                    let trackPath = trackTableModel.data(
                        trackTableModel.index(trackTableModel.selectedTrackIndex, 0),
                        Qt.UserRole + 4
                    );
                    playbackService.toggle_playback(trackPath);
                } else if (playbackService.currentTrackPath) {
                    playbackService.toggle_playback();
                }
            }
        }
        
        Button {
            id: skipForwardButton
            text: qsTr("Forward")
            onClicked: {
                playbackService.skip_forward();
            }
        }
    }
}
