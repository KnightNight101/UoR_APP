import QtQuick 2.15
import QtQuick.Controls 2.15

Page {
    id: settingsPage
    title: "Settings"

    Column {
        anchors.centerIn: parent
        spacing: 24

        Text {
            text: "Settings"
            font.pixelSize: 32
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Button {
            text: "Back to Dashboard"
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: {
                // Signal to parent to navigate back
                if (settingsPage.backToDashboard)
                    settingsPage.backToDashboard()
            }
        }
    }

    signal backToDashboard()
}