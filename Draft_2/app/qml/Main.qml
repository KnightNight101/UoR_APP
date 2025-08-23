/*
    Main.qml - Login Page Implementation

    This file defines the main application window and the login page UI for the QML-based desktop client.
    All code logic and UI structure are preserved; only comments have been added for clarity.
*/

import QtQuick 2.15          // Core QML types
import QtQuick.Controls 2.15 // UI controls (Button, TextField, etc.)
import QtQuick.Layouts 1.15  // Layout helpers (ColumnLayout, RowLayout, etc.)

// Optionally, you can set a style for controls (e.g., Material), but it's commented out here
// QtQuick.Controls.Controls.style: "Material"

// Main application window
ApplicationWindow {
    id: root
    visible: true
    width: 480
    height: 640
    title: qsTr("Login") // Window title

    // Set solid white background for the window
    color: "white"

    // --- Login Flow Logic ---
    property bool loggedIn: false      // Tracks login state
    property string loginUser: ""      // Stores username input
    property string loginPass: ""      // Stores password input
    property string loginError: ""     // Stores error message for invalid login

    // --- Login Page UI (visible when not logged in) ---
    Item {
        anchors.fill: parent
        visible: !root.loggedIn // Show this page only if not logged in

        // Centered login box
        Rectangle {
            id: loginBox
            width: Math.min(parent.width * 0.8, 340)   // Responsive width, max 340px
            height: Math.min(parent.height * 0.6, 420) // Responsive height, max 420px
            color: "#ffffff"
            border.color: "#4488cc" // Blue border
            border.width: 2
            radius: 24              // Rounded corners
            anchors.centerIn: parent

            // Optional shadow for depth (currently hidden)
            Rectangle {
                anchors.fill: parent
                color: "#22000044"      // Semi-transparent shadow color
                radius: 24
                anchors.verticalCenterOffset: 8
                z: -1
                visible: false          // Set to true to enable shadow
            }

            // Vertical layout for logo and input fields
            Column {
                anchors.fill: parent
                spacing: 0

                // --- Logo area (upper two thirds of box) ---
                Item {
                    height: parent.height * 2 / 3
                    width: parent.width
                    anchors.horizontalCenter: parent.horizontalCenter

                    Image {
                        id: logoImg
                        source: "../../images/logo.jpg" // App logo
                        width: 120
                        height: 120
                        anchors.centerIn: parent
                        fillMode: Image.PreserveAspectFit // Maintain aspect ratio
                    }
                }

                // --- Input fields area (lower third of box) ---
                Item {
                    height: parent.height / 3
                    width: parent.width
                    anchors.horizontalCenter: parent.horizontalCenter

                    // Stack input fields and button vertically
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 10

                        // Username input
                        TextField {
                            id: usernameField
                            placeholderText: "Username"
                            text: root.loginUser
                            onTextChanged: root.loginUser = text // Bind to property
                            Layout.preferredWidth: 200
                        }
                        // Password input (masked)
                        TextField {
                            id: passwordField
                            placeholderText: "Password"
                            echoMode: TextInput.Password // Hide input text
                            text: root.loginPass
                            onTextChanged: root.loginPass = text // Bind to property
                            Layout.preferredWidth: 200
                        }
                        // Login button
                        Button {
                            text: "Login"
                            Layout.preferredWidth: 200
                            onClicked: {
                                // Simple login logic: password must be "password" and username not empty
                                if (root.loginPass === "password" && root.loginUser.length > 0) {
                                    root.loggedIn = true
                                    root.loginError = ""
                                    root.visibility = "Maximized"
                                } else {
                                    root.loginError = "Invalid credentials"
                                }
                            }
                        }
                        // Error message display
                        Text {
                            text: root.loginError
                            color: "red"
                            visible: root.loginError.length > 0
                            font.pixelSize: 14
                        }
                    }
                }
            }
        }
    }

    // --- Dashboard Page (visible when logged in) ---
    Item {
        anchors.fill: parent
        visible: root.loggedIn

        // Center the dashboard group
        RowLayout {
            id: dashboardRow
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            width: implicitWidth
            height: parent.height * 0.6
            spacing: 32

            // Dashboard Box Style
            property int dashBoxWidth: 180

            // Projects Box
            Rectangle {
                width: dashboardRow.dashBoxWidth
                height: dashboardRow.height
                radius: 24
                color: "#ffffff"
                border.color: "#4488cc"
                border.width: 2

                // Subtle shadow
                Rectangle {
                    width: parent.width
                    height: parent.height
                    radius: 24
                    color: "#22000044"
                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: 6
                    z: parent.z - 1
                }

                // Heading
                Text {
                    text: "Projects"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 32
                    font.pixelSize: 22
                    font.bold: true
                    color: "#4488cc"
                }
            }

            // TODO Box
            Rectangle {
                width: dashboardRow.dashBoxWidth
                height: dashboardRow.height
                radius: 24
                color: "#ffffff"
                border.color: "#4488cc"
                border.width: 2

                Rectangle {
                    width: parent.width
                    height: parent.height
                    radius: 24
                    color: "#22000044"
                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: 6
                    z: parent.z - 1
                }

                Text {
                    text: "Today's TODO"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 32
                    font.pixelSize: 22
                    font.bold: true
                    color: "#4488cc"
                }
            }

            // Messages Box
            Rectangle {
                width: dashboardRow.dashBoxWidth
                height: dashboardRow.height
                radius: 24
                color: "#ffffff"
                border.color: "#4488cc"
                border.width: 2

                Rectangle {
                    width: parent.width
                    height: parent.height
                    radius: 24
                    color: "#22000044"
                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: 6
                    z: parent.z - 1
                }

                Text {
                    text: "Messages"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 32
                    font.pixelSize: 22
                    font.bold: true
                    color: "#4488cc"
                }
            }
        }
    }
    // --- All other code remains commented out below ---
}
 
    // --- All other code remains commented out below ---
    /*
    <rest of original file remains commented out>
    */
