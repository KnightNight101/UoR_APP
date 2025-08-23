import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

// Main.qml: QML migration scaffold
// TODO: Connect login logic and backend integration
// TODO: Replace placeholder dashboard with real content

ApplicationWindow {
    id: root
    visible: true
    width: 480
    height: 640
    title: qsTr("QML Migration Prototype")
    Material.theme: Material.Light

    // Simple stacked view for login and dashboard
    StackView {
        id: stack
        anchors.fill: parent
        initialItem: loginPage
    }

    Component {
        id: loginPage
        Item {
            anchors.fill: parent
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20

                Label {
                    text: qsTr("Login")
                    font.pixelSize: 28
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }
                TextField {
                    id: username
                    placeholderText: qsTr("Username")
                    Layout.fillWidth: true
                }
                TextField {
                    id: password
                    placeholderText: qsTr("Password")
                    echoMode: TextInput.Password
                    Layout.fillWidth: true
                }
                Button {
                    text: qsTr("Login")
                    Layout.fillWidth: true
                    onClicked: {
                        // TODO: Validate credentials with backend
                        stack.push(dashboardPage)
                    }
                }
            }
        }
    }

    Component {
        id: dashboardPage
        Item {
            anchors.fill: parent
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20

                Label {
                    text: qsTr("Dashboard (Placeholder)")
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }
                // TODO: Add dashboard widgets and navigation
            }
        }
    }
}