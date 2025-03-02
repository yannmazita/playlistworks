import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: trackTable
    columnSpacing: 1
    rowSpacing: 1
    clip: true
    width: 600
    height: 400

    model: trackTableModel

    delegate: Text {
        text: display
    }
}
