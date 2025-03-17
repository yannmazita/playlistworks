import QtQuick
import QtQuick.Controls

Dialog {
    id: libraryScanningDialogRoot
    title: "Scanning Library"
    modal: true
    closePolicy: Dialog.NoAutoClose

    Label {
        text: "Scanning library files, please wait..."
    }

    BusyIndicator {
        running: true
    }

    Component.onCompleted: {
        backend.scanStarted.connect(() => {
            libraryScanningDialog.open();
        });

        backend.scanFinished.connect(() => {
            libraryScanningDialog.close();
        });

        backend.scanError.connect(errorMessage => {
            libraryScanningDialog.close();
            errorDialog.text = errorMessage;
            errorDialog.open();
        });
    }
}
