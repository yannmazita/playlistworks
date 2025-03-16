import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: statusBar
    Layout.fillWidth: true
    color: "#f0f0f0"
    property int songCount: backend.library.songModel.rowCount()
    
    property string repeatMode: "repeatAll"
    property bool repeatEnabled: false
    property bool shuffleEnabled: false
    
    Connections {
        target: backend
        function onScanFinished(error_paths) {
            statusBar.songCount = backend.library.songModel.rowCount();
        }
    }
    RowLayout {
        anchors.fill: parent
        
        ToolButton {
            id: shuffleButton
            text: qsTr("Shuffle")
            checkable: true
            checked: statusBar.shuffleEnabled
            
            background: Rectangle {
                implicitWidth: 60
                implicitHeight: 30
                color: shuffleButton.checked ? "#a0c0e0" : "#e0e0e0"
            }
            
            onClicked: {
                statusBar.shuffleEnabled = !statusBar.shuffleEnabled
                console.log("Shuffle mode:", statusBar.shuffleEnabled)
            }
        }
        
        // Group container for repeat controls
        Rectangle {
            Layout.preferredHeight: repeatButton.height
            Layout.preferredWidth: repeatButton.width + repeatOption.width
            color: "#e0e0e0"
            
            RowLayout {
                anchors.fill: parent
                spacing: 0
                
                ToolButton {
                    id: repeatButton
                    text: qsTr("Repeat")
                    checkable: true
                    checked: statusBar.repeatEnabled
                    
                    background: Rectangle {
                        color: repeatButton.checked ? "#a0c0e0" : "transparent"
                    }
                    
                    onClicked: {
                        statusBar.repeatEnabled = !statusBar.repeatEnabled
                        console.log("Repeat enabled:", statusBar.repeatEnabled)
                        console.log("Repeat mode:", statusBar.repeatEnabled ? statusBar.repeatMode : "off")
                    }
                }
                
                ToolButton {
                    id: repeatOption
                    text: qsTr("▼")
                    implicitWidth: 24
                    onClicked: repeatMenu.popup()
                    background: Rectangle {
                        color: "transparent"
                    }
                    
                    Menu {
                        id: repeatMenu
                        y: repeatOption.height
                        
                        ButtonGroup {
                            id: repeatGroup
                        }
                        
                        MenuItem {
                            id: repeatAllOption
                            checkable: true
                            checked: statusBar.repeatMode === "repeatAll"
                            text: qsTr("Repeat all")
                            property string property: "repeatAll"
                            ButtonGroup.group: repeatGroup
                            
                            onTriggered: {
                                statusBar.repeatMode = property
                                statusBar.repeatEnabled = true
                                repeatButton.checked = true
                                console.log("Repeat mode set to:", statusBar.repeatMode)
                            }
                        }
                        
                        MenuItem {
                            id: repeatTrackOption
                            checkable: true
                            checked: statusBar.repeatMode === "repeatTrack"
                            text: qsTr("Repeat this track")
                            property string property: "repeatTrack"
                            ButtonGroup.group: repeatGroup
                            
                            onTriggered: {
                                statusBar.repeatMode = property
                                statusBar.repeatEnabled = true
                                repeatButton.checked = true
                                console.log("Repeat mode set to:", statusBar.repeatMode)
                            }
                        }
                        
                        MenuItem {
                            id: oneSongOption
                            checkable: true
                            checked: statusBar.repeatMode === "oneSong"
                            text: qsTr("One song")
                            property string property: "oneSong"
                            ButtonGroup.group: repeatGroup
                            
                            onTriggered: {
                                statusBar.repeatMode = property
                                statusBar.repeatEnabled = true
                                repeatButton.checked = true
                                console.log("Repeat mode set to:", statusBar.repeatMode)
                            }
                        }
                    }
                }
            }
        }
        
        Text {
          id: statusBarText
          text: "Songs: " + statusBar.songCount
        }
    }
}
