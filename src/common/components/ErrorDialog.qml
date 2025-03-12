import QtQuick
import QtQuick.Controls

Dialog {
    id: errorDialog
    title: "Error"
    modal: true
    property string text: ""

    Label {
        text: errorDialog.text
    }

    standardButtons: Dialog.Ok
}
