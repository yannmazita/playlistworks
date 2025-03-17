import QtQuick
import QtQuick.Controls

Dialog {
    id: deleteConfirmDialogRoot
    title: "Delete Playlist"
    modal: true
    anchors.centerIn: parent

    property int playlistToDelete: -1
    property string playlistName: ""

    function showLibrary() {
        songTableView.inPlaylistMode = false;
        songTableView.currentPlaylistId = -1;
    }

    Text {
        text: "Are you sure you want to delete the playlist '" + deleteConfirmDialogRoot.playlistName + "'?"
        width: 300
        wrapMode: Text.WordWrap
    }

    standardButtons: Dialog.Yes | Dialog.No

    onAccepted: {
        backend.library.deletePlaylist(playlistToDelete);
        showLibrary();
    }
}
