// Login Page Implementation
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

 // QtQuick.Controls.Controls.style: "Material"

// All other code remains commented out below

ApplicationWindow {
    id: root
    visible: true
    width: 480
    height: 640
    title: qsTr("Login")

    // Set solid white background for the window
    color: "white"

    // --- Centered Login Box ---
    // The login box is centered both vertically and horizontally
    Item {
        anchors.fill: parent

        // Use a parent Item to ensure perfect centering
        Rectangle {
            id: loginBox
            property int loginBoxWidth: 340
            property real fieldWidth: width * 0.75
            width: loginBoxWidth
            height: 400
            radius: 24
            color: "#ffffff"
            anchors.centerIn: parent
            border.color: "#4488cc"
            border.width: 2

            // Subtle shadow for visual depth
            // layer.enabled: true
            // layer.effect: DropShadow {
            //     color: "#22000000"
            //     radius: 24
            //     samples: 32
            //     verticalOffset: 4
            //     horizontalOffset: 0
            // }

            // Rectangle shadow replacement for DropShadow
            Rectangle {
                width: loginBox.width
                height: loginBox.height
                radius: 24
                color: "#22000044"
                anchors.centerIn: parent
                anchors.verticalCenterOffset: 6
                z: loginBox.z - 1
            }

            // Layout for vertical division (logo + fields)
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 32
                spacing: 0

                // --- Upper two thirds: Logo ---
                Item {
                    // Reduce logo area to move fields higher
                    Layout.preferredHeight: loginBox.height * 0.45
                    Layout.fillWidth: true

                    // Center the logo
                    Image {
                        source: "../../images/logo.jpg"
                        width: 100
                        height: 100
                        anchors.centerIn: parent
                        fillMode: Image.PreserveAspectFit
                    }
                }

                // --- Lower third: Input fields ---
                Item {
                    // Increase height for more space above fields
                    Layout.preferredHeight: loginBox.height * 0.55
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.top: parent.top
                        anchors.topMargin: 12
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 24

                        // Username input
                        TextField {
                            id: usernameField
                            placeholderText: qsTr("Username")
                            width: loginBox.fieldWidth
                            Layout.alignment: Qt.AlignHCenter
                            padding: 12
                            font.pixelSize: 18
                            Keys.onReturnPressed: enterButton.clicked()
                            /* background customization removed for Material style */
                        }

                        // Password input
                        TextField {
                            id: passwordField
                            placeholderText: qsTr("Password")
                            echoMode: TextInput.Password
                            width: loginBox.fieldWidth
                            Layout.alignment: Qt.AlignHCenter
                            padding: 12
                            font.pixelSize: 18
                            Keys.onReturnPressed: enterButton.clicked()
                            /* background customization removed for Material style */
                        }
                        // --- Material-style Enter Button ---
                        Button {
                            id: enterButton
                            text: qsTr("Enter")
                            width: loginBox.fieldWidth
                            Layout.alignment: Qt.AlignHCenter
                            height: 44
                            font.pixelSize: 18
                            /* background and contentItem customization removed for Material style */
                            onClicked: {
                                // Handle login logic here
                                // Example: console.log("Login attempted with", usernameField.text, passwordField.text)
                            }
                        }
                    }
                }
            }
        }
    }
                // --- FIX: Added missing closing braces for ColumnLayout, Item, and ApplicationWindow ---
}
 
    // --- All other code remains commented out below ---
    /*
    <rest of original file remains commented out>
    */
