import QtQuick
import QtQuick.Controls

Dialog {
    id: errorDialogRoot
    title: "Error"
    modal: true
    property string text: ""

    Label {
        text: errorDialogRoot.text
    }

    standardButtons: Dialog.Ok
}
