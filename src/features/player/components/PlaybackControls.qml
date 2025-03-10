import QtQuick
import QtQuick.Controls
import QtMultimedia

Row {
    spacing: 10
    property int playbackValue : 3

    Component.onCompleted: {
      playButton.text = qsTr("Play");
    }

    Connections {
      target: playbackService
      function onPlaybackStateChanged(state) {
        if (playbackValue !== state) {
          playbackValue = state;
          if (playbackValue !== 1) {
            playButton.text = qsTr("Play");
          } else {
            playButton.text = qsTr("Pause");
          }
        }
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
        id: skipBackButton
        text: qsTr("Back")
        onClicked: {
            console.log("Clicked Back button");
        }
    }

    Button {
        id: skipForwardButton
        text: qsTr("Forward")
        onClicked: {
            console.log("Clicked Forward button");
        }
    }
}
