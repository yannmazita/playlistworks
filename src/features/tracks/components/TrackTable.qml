import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: trackTable
    columnSpacing: 1
    rowSpacing: 1
    clip: true
    width: mainWindow.width
    height: mainWindow.height - 200

    model: trackTableModel

    delegate: Rectangle {
        implicitWidth: 500
        implicitHeight: 50
        border.width: 1

        Text {
            text: display
        }
    }
}
