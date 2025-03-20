import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: playlistEditionDialogRoot
    title: "Edit Playlist"
    modal: true
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 400
    
    // Playlist details
    property int playlistId: -1
    property string playlistName: ""
    property string playlistQuery: ""
    property bool isDynamic: false
    
    function setPlaylistDetails(id, name, query, dynamic) {
        playlistId = id;
        playlistName = name;
        playlistQuery = query;
        isDynamic = dynamic;
        
        playlistNameField.text = name;
        dynamicPlaylistCheck.checked = dynamic;
        playlistQueryField.text = query;
    }
    
    ColumnLayout {
        width: parent.width
        
        Label {
            text: qsTr("Playlist Name:")
        }
        
        TextField {
            id: playlistNameField
            Layout.fillWidth: true
            placeholderText: "Enter playlist name"
            text: playlistEditionDialog.playlistName
        }
        
        CheckBox {
            id: dynamicPlaylistCheck
            text: qsTr("Dynamic Playlist")
            checked: playlistEditionDialog.isDynamic
        }
        
        Label {
            text: qsTr("Query:")
            visible: dynamicPlaylistCheck.checked
        }
        
        TextField {
            id: playlistQueryField
            Layout.fillWidth: true
            text: playlistEditionDialog.playlistQuery
            visible: dynamicPlaylistCheck.checked
            placeholderText: qsTr("Enter search query")
        }
    }
    
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    onAccepted: {
        if (playlistNameField.text.trim() !== "") {
            backend.library.updatePlaylist(
                playlistId, 
                playlistNameField.text, 
                dynamicPlaylistCheck.checked ? playlistQueryField.text : "", 
                dynamicPlaylistCheck.checked
            );
        }
    }
}
