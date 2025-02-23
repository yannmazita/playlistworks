import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    Button {
        id: playPauseButton
        text: "Play/Pause"
        onClicked: {
            console.log("Clicked Play/Pause button");
        }
    }

    Button {
        id: stopPause
        text: "Stop"
        onClicked: {
            console.log("Clicked Stop button");
        }
    }

    Button {
        id: skipBack
        text: "Back"
        onClicked: {
            console.log("Clicked Back button");
        }
    }

    Button {
        id: skipForward
        text: "Forward"
        onClicked: {
            console.log("Clicked Forward button");
        }
    }
}
