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
    // Navigation state
    property string currentPage: "dashboard" // "dashboard" or "eventlog"

    // Reference to backend event log bridge
    property var eventLogBridge: null

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
                                    if (typeof log_event.log_event === "function") log_event.log_event("User '" + root.loginUser + "' logged in")
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
        visible: root.loggedIn && root.currentPage === "dashboard"
// Spherical user icon button in top right corner (dashboard only)
Rectangle {
    id: userIconButton
    width: 48
    height: 48
    radius: 24
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.topMargin: 24
    anchors.rightMargin: 32
    color: "#ffffff"
    border.color: "#2255aa"
    border.width: 2
    z: 10

    // Spherical cropped image
    Image {
        id: userIconImg
        source: "../../images/user.jpg"
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        smooth: true
        clip: true
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: userMenu.open()
    }

    // Popup menu
    Menu {
        id: userMenu
        y: userIconButton.height + 8
        x: -userMenu.width + userIconButton.width
        MenuItem { text: "Profile" }
        MenuItem { text: "Calendar" }
        MenuItem { text: "File Manager" }
        MenuItem {
            text: "Event Log"
            onTriggered: {
                if (typeof log_event.log_event === "function") log_event.log_event("Navigated to Event Log page")
                root.currentPage = "eventlog"
                if (root.eventLogBridge) root.eventLogBridge.load_log()
            }
        }
        MenuItem { text: "Settings" }
        MenuItem {
            text: "Logout"
            onTriggered: {
                if (typeof log_event.log_event === "function") log_event.log_event("User '" + root.loginUser + "' logged out")
                root.loggedIn = false
                root.loginUser = ""
                root.loginPass = ""
                root.currentPage = "dashboard"
            }
        }
    }
}

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
                border.color: "#2255aa"
                border.width: 4
                z: 1
            
                // Heading in top 10% area
                Item {
                    width: parent.width
                    height: parent.height * 0.1
                    anchors.top: parent.top
                    Rectangle {
                        anchors.fill: parent
                        color: "transparent"
                        border.width: 0
                    }
                    Text {
                        text: "Projects"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 8
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignTop
                        font.pixelSize: 22
                        font.bold: true
                        color: "#2255aa"
                        padding: 8
                    }
                }
            }

            // TODO Box
            Rectangle {
                width: dashboardRow.dashBoxWidth
                height: dashboardRow.height
                radius: 24
                color: "#ffffff"
                border.color: "#2255aa"
                border.width: 4
                z: 1
            
                Item {
                    width: parent.width
                    height: parent.height * 0.1
                    anchors.top: parent.top
                    Rectangle {
                        anchors.fill: parent
                        color: "transparent"
                        border.width: 0
                    }
                    Text {
                        text: "Today's TODO"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 8
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignTop
                        font.pixelSize: 22
                        font.bold: true
                        color: "#2255aa"
                        padding: 8
                    }
                }
            }

            // Messages Box
            Rectangle {
                width: dashboardRow.dashBoxWidth
                height: dashboardRow.height
                radius: 24
                color: "#ffffff"
                border.color: "#2255aa"
                border.width: 4
                z: 1
            
                Item {
                    width: parent.width
                    height: parent.height * 0.1
                    anchors.top: parent.top
                    Rectangle {
                        anchors.fill: parent
                        color: "transparent"
                        border.width: 0
                    }
                    Text {
                        text: "Messages"
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 8
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignTop
                        font.pixelSize: 22
                        font.bold: true
                        color: "#2255aa"
                        padding: 8
                    }
                }
            }
        }
    }
        // --- Event Log Page (visible when logged in and currentPage is "eventlog") ---
        Item {
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "eventlog"

            // Top left back-to-dashboard button (visible on event log page)
            Button {
                text: "\u25C0 Dashboard"
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 24
                anchors.leftMargin: 32
                onClicked: root.currentPage = "dashboard"
                z: 100
            }

            Rectangle {
                id: eventLogBox
                width: Math.min(parent.width * 0.8, 600)
                height: Math.min(parent.height * 0.8, 500)
                color: "#ffffff"
                border.color: "#2255aa"
                border.width: 3
                radius: 24
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                z: 10

                Column {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 16

                    // Heading
                    Text {
                        text: "Event Log"
                        font.pixelSize: 28
                        font.bold: true
                        color: "#2255aa"
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    // Scrollable event list
                    Flickable {
                        id: eventLogFlick
                        width: parent.width
                        height: parent.height - 80
                        contentHeight: eventLogRepeater.height
                        clip: true

                        Rectangle {
                            width: parent.width
                            height: eventLogRepeater.height
                            color: "transparent"

                            Column {
                                id: eventLogRepeater
                                width: parent.width
                                Repeater {
                                    model: log_event ? log_event.eventLog : []
                                    delegate: Rectangle {
                                        width: parent.width
                                        height: 40
                                        color: index % 2 === 0 ? "#ffffff" : "#e9eef6"
                                        Row {
                                            anchors.verticalCenter: parent.verticalCenter
                                            spacing: 12
                                            Text {
                                                text: modelData.timestamp
                                                font.pixelSize: 14
                                                color: "#888"
                                                width: 160
                                                elide: Text.ElideRight
                                            }
                                            Text {
                                                text: modelData.description
                                                font.pixelSize: 16
                                                color: "#222"
                                                elide: Text.ElideRight
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Bottom row buttons
                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 16

                        Button {
                            text: "Refresh"
                            onClicked: {
                                if (log_event) log_event.load_log()
                            }
                        }
                        Button {
                            text: "Top"
                            onClicked: {
                                eventLogFlick.contentY = 0
                            }
                        }
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
