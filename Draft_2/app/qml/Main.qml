/*
    Main.qml - Login Page Implementation

    This file defines the main application window and the login page UI for the QML-based desktop client.
    All code logic and UI structure are preserved; only comments have been added for clarity.
*/

import QtQuick 2.15          // Core QML types
import QtQuick.Controls 2.15 // UI controls (Button, TextField, etc.)
import QtQuick.Layouts 1.15  // Layout helpers (ColumnLayout, RowLayout, etc.)
import QtQuick.Controls 2.15 // For Calendar and Dialog types

// Optionally, you can set a style for controls (e.g., Material), but it's commented out here
// QtQuick.Controls.Controls.style: "Material"

// Main application window
ApplicationWindow {
    id: root
    visible: true
    width: 480
    height: 640
    title: qsTr("Login") // Window title
    property int selectedProjectId: -1

    onClosing: {
        if (root.loggedIn) {
            if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                log_event.log_event("User logged out (window closed)")
            }
            root.loggedIn = false
            root.loginUser = ""
            root.loginPass = ""
            root.currentPage = "dashboard"
        }
    }

    // Set solid white background for the window
    color: "white"
    // Navigation state
    onCurrentPageChanged: {
        if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
            log_event.log_event("Navigated to page: " + root.currentPage)
        }
        // Always refresh projects when navigating to dashboard
        if (root.currentPage === "dashboard" && AuthManager.userId > 0) {
            dashboardManager.loadProjects(AuthManager.userId)
        }
    }
    property string currentPage: "dashboard" // "dashboard" or "eventlog"

    // Reference to backend event log bridge
    property var eventLogBridge: null

    // --- Login Flow Logic ---
    property bool loggedIn: false      // Tracks login state
    property string loginUser: ""      // Stores username input
    property string loginPass: ""      // Stores password input
    property string loginError: ""     // Stores error message for invalid login

    onLoggedInChanged: {
        if (loggedIn && AuthManager.userId > 0) {
            dashboardManager.loadProjects(AuthManager.userId)
        }
    }
// Load projects after login or when userId changes
Connections {
    target: AuthManager
    onUserIdChanged: {
        if (AuthManager.userId > 0) {
            dashboardManager.loadProjects(AuthManager.userId)
        }
    }
}

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
                            height: 40
                            horizontalAlignment: TextInput.AlignLeft
                        }
                        // Password input (masked)
                        TextField {
                            id: passwordField
                            placeholderText: "Password"
                            echoMode: TextInput.Password // Hide input text
                            text: root.loginPass
                            onTextChanged: root.loginPass = text // Bind to property
                            Layout.preferredWidth: 200
                            height: 40
                        }
                        // Login button
                        Button {
                            text: "Login"
                            Layout.preferredWidth: 200
                            onClicked: {
                                // Only call AuthManager.login; do not set loggedIn here
                                AuthManager.login(root.loginUser, root.loginPass);
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
                // Handle login result and set loggedIn only after AuthManager.userId is set
                Connections {
                    target: AuthManager
                    function onLoginResult(success, message) {
                        if (success && AuthManager.userId > 0) {
                            root.loggedIn = true;
                            root.loginError = "";
                            root.visibility = "Maximized";
                            if (typeof log_event.log_event === "function") log_event.log_event("User '" + root.loginUser + "' logged in");
                        } else {
                            root.loginError = message;
                        }
                    }
                }
            }
        }
    }

    // --- Dashboard Page (visible when logged in) ---
    Item {
        anchors.fill: parent
        Component.onCompleted: {
            console.log("DEBUG: Dashboard visible. dashboardManager.projects =", dashboardManager.projects)
        }
        visible: root.loggedIn && root.currentPage === "dashboard"

        // --- User Icon and Menu (top right) ---
        Rectangle {
            id: userIcon
            width: 48
            height: 48
            radius: 24
            color: "#e9eef6"
            border.color: "#2255aa"
            border.width: 2
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.topMargin: 24
            anchors.rightMargin: 32
            z: 100
            clip: true

            Image {
                id: userImg
                source: "../../images/user.jpg"
                anchors.fill: parent
                anchors.margins: 0
                fillMode: Image.PreserveAspectCrop
                smooth: true
            }

            MouseArea {
                id: userMouseArea
                anchors.fill: parent
                onClicked: userMenu.open()
                cursorShape: Qt.PointingHandCursor
            }

            Menu {
                id: userMenu
                x: userIcon.width - width
                y: userIcon.height
                MenuItem { text: "Profile"; onTriggered: {/* TODO: Implement profile navigation */} }
                MenuItem { text: "Calendar"; onTriggered: {/* TODO: Implement calendar navigation */} }
                MenuItem { text: "File Manager"; onTriggered: {/* TODO: Implement file manager navigation */} }
                MenuItem { text: "Event Log"; onTriggered: root.currentPage = "eventlog" }
                MenuItem { text: "Settings"; onTriggered: {/* TODO: Implement settings navigation */} }
                MenuSeparator { }
                MenuItem { text: "Logout"; onTriggered: {
                    if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                        log_event.log_event("User logged out")
                    }
                    root.loggedIn = false; root.loginUser = ""; root.loginPass = ""; root.currentPage = "dashboard";
                } }
            }
        }

        // Dashboard layout matching latest CSS coordinates and sizes
        Item {
            width: 1500
            height: 900
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            // Sidebar (ProjectsBox)
            Rectangle {
                id: sidebar
                x: 0
                y: 0
                width: 444.44
                height: 900
                color: "#f8f9fa"
                border.color: "#000"
                border.width: 1
                radius: 25

                // Projects box container
                Column {
                    id: projectsBox
                    width: parent.width
                    height: parent.height - 60
                    y: 35
                    spacing: 0

                    // Sidebar heading "Projects"
                    Row {
                        spacing: 8
                        height: 70
                        anchors.horizontalCenter: parent.horizontalCenter
                        // Projects heading and blue "+" link
                        Text {
                            text: "Projects"
                            font.pixelSize: 58
                            color: "#000"
                            font.family: "Inter"
                            font.bold: false
                            verticalAlignment: Text.AlignVCenter
                        }
                        Text {
                            text: "+"
                            font.pixelSize: 58
                            color: "#2255aa"
                            font.family: "Inter"
                            font.bold: true
                            verticalAlignment: Text.AlignVCenter
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.currentPage = "createProject"
                            }
                        }
                    }

                    // Project list below heading (dynamic, selectable)
                    ScrollView {
                        id: projectListScroll
                        width: parent.width
                        height: parent.height - 200 // Leaves space for heading and add button
                        anchors.top: parent.top
                        anchors.topMargin: 70
                        clip: true
                        // horizontalScrollBarPolicy removed (not supported in QtQuick.Controls 2.x)

                        Column {
                            id: projectListColumn
                            width: parent.width
                            spacing: 6
                            Repeater {
                                model: dashboardManager.projects
                                Rectangle {
                                    width: parent.width
                                    height: 24
                                    color: "#ffffff"
                                    border.color: "transparent"
                                    border.width: 0
                                    radius: 6
                                    visible: true
                                    clip: true
    
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            root.selectedProjectId = modelData.id
                                            if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                                                let pname = (modelData.name && modelData.name.length > 0) ? modelData.name : "(Untitled Project)";
                                                log_event.log_event("Navigated to project details: " + pname);
                                            }
                                            root.currentPage = "projectDetails"
                                        }
                                    }
    
                                    Text {
                                        text: (modelData.name && modelData.name.length > 0) ? modelData.name : "(Untitled)"
                                        font.pixelSize: 16
                                        color: "#2255aa"
                                        verticalAlignment: Text.AlignVCenter
                                        leftPadding: 8
                                        elide: Text.ElideRight
                                        width: parent.width - 16
                                    }
                                }
                            }
                        }
                    }

                    // Floating add button at bottom of projects box

                }
            }

            // Main area (ToDoListBox)
            Rectangle {
                id: mainContent
                x: sidebar.x + sidebar.width + (60 * (parent.width / 1920))
                y: 0
                width: 1000
                height: 900
                color: "#fff"
                border.color: "#000"
                border.width: 1
                radius: 25

                // Main heading "To Do Today"
                Text {
                    text: "To Do Today"
                    y: 35
                    width: 344
                    height: 70
                    font.pixelSize: 58
                    color: "#000"
                    font.family: "Inter"
                    font.bold: false
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                // Group 3: Quadrant grid and dividers, positioned absolutely in ToDoListBox
                Item {
                    id: group3
                    x: 55
                    y: 125
                    width: 900
                    height: 650

                    // Important and Urgent
                    Rectangle {
                        x: 0
                        y: 0
                        width: 450
                        height: 325
                        color: "#f5f5f5"
                        border.color: "#bbb"
                        border.width: 1
                        radius: 12
                    }
                    // Important
                    Rectangle {
                        x: 450
                        y: 0
                        width: 450
                        height: 325
                        color: "#f5f5f5"
                        border.color: "#bbb"
                        border.width: 1
                        radius: 12
                    }
                    // Urgent
                    Rectangle {
                        x: 0
                        y: 325
                        width: 450
                        height: 325
                        color: "#f5f5f5"
                        border.color: "#bbb"
                        border.width: 1
                        radius: 12
                    }
                    // Other
                    Rectangle {
                        x: 450
                        y: 325
                        width: 450
                        height: 325
                        color: "#f5f5f5"
                        border.color: "#bbb"
                        border.width: 1
                        radius: 12
                    }
                    // Divider 1 (horizontal)
                    Rectangle {
                        x: 0
                        y: 325
                        width: 900
                        height: 5
                        color: "#000"
                    }
                    // Divider 2 (vertical)
                    Rectangle {
                        x: 450
                        y: 0
                        width: 5
                        height: 650
                        color: "#000"
                    }
                }
            }
        }
    }
        // --- Project Details Page (visible when logged in and currentPage is "projectDetails") ---
        Item {
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "projectDetails"

            // Top left back-to-dashboard button
            Button {
                text: "\u25C0 Dashboard"
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 24
                anchors.leftMargin: 32
                onClicked: root.currentPage = "dashboard"
                z: 100
            }

            // Delete Project Button (top left, next to Dashboard)
            Button {
                id: deleteProjectBtn
                text: "Delete Project"
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 24
                anchors.leftMargin: 180
                z: 100
                onClicked: deleteProjectDialog.open()
            }

            // Delete Confirmation Dialog
            Dialog {
                id: deleteProjectDialog
                modal: true
                x: (parent.width - width) / 2
                y: (parent.height - height) / 2
                standardButtons: Dialog.NoButton
                width: 340
                height: 180

                Rectangle {
                    anchors.fill: parent
                    color: "#fff"
                    radius: 12
                    border.color: "#2255aa"
                    border.width: 2

                    Column {
                        anchors.centerIn: parent
                        spacing: 24

                        Text {
                            text: "Are you sure you want to delete this project?"
                            font.pixelSize: 18
                            color: "#222"
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            width: 300
                        }

                        Row {
                            spacing: 24
                            anchors.horizontalCenter: parent.horizontalCenter

                            Button {
                                text: "Cancel"
                                onClicked: deleteProjectDialog.close()
                            }
                            Button {
                                text: "Delete"
                                onClicked: {
                                    projectManager.deleteProject(root.selectedProjectId, AuthManager.userId)
                                }
                            }
                        }
                    }
                }
            }
    
            // Listen for projectDeleted signal to handle UI after deletion
            Connections {
                target: projectManager
                function onProjectDeleted(success, message) {
                    if (success) {
                        deleteProjectDialog.close()
                        root.currentPage = "dashboard"
                        dashboardManager.loadProjects(AuthManager.userId)
                        if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                            log_event.log_event(message)
                        }
                    } else {
                        // Optionally show error to user
                        deleteProjectDialog.close()
                        if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                            log_event.log_event("Project deletion failed: " + message)
                        }
                    }
                }
            }

            // Project Title Heading
            Text {
                id: projectDetailsTitle
                text: {
                    // Find the selected project by ID
                    let proj = dashboardManager.projects.find(p => p.id === root.selectedProjectId)
                    proj && proj.name && proj.name.length > 0 ? proj.name : "(Untitled Project)"
                }
                font.pixelSize: 32
                font.bold: true
                color: "#2255aa"
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 28
                anchors.leftMargin: 200
            }

            // Log event when page is shown
            Component.onCompleted: {
                if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                    let proj = dashboardManager.projects.find(p => p.id === root.selectedProjectId)
                    let pname = proj && proj.name && proj.name.length > 0 ? proj.name : "(Untitled Project)"
                    log_event.log_event("Opened project details: " + pname)
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
                        // removed anchors.horizontalCenter for Column child
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
                    
                        // --- Project Creation Page ---
                    }
                }
            }
        }
        // --- Project Creation Page (top-level, always available) ---
        Item {
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "createProject"
    
            Rectangle {
                width: 600
                height: 500
                color: "#fff"
                border.color: "#2255aa"
                border.width: 3
                radius: 24
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                z: 10
    
                Column {
                    anchors.centerIn: parent
                    spacing: 16
    
                    Text {
                        text: "Create a new project"
                        font.pixelSize: 32
                        font.bold: true
                        color: "#2255aa"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
    
                    // Title
                    TextArea {
                        id: projectNameField
                        placeholderText: "Title"
                        width: 400
                        height: 40
                    }
                    // Description
                    TextArea {
                        id: projectDescField
                        placeholderText: "Description"
                        width: 400
                        height: 80
                    }
                    // Team members multi-select dropdown
                    Rectangle {
                        width: 400
                        height: 48
                        color: "#f8f9fa"
                        border.color: "#bbb"
                        border.width: 1
                        radius: 8
    
                        property var selectedMembers: []
    
                        ComboBox {
                            id: teamCombo
                            width: parent.width
                            model: userManager.users
                            textRole: "username"
                            valueRole: "id"
                            editable: false
                            onActivated: {
                                if (userManager.users.length > 0) {
                                    let user = userManager.users[currentIndex];
                                    let idx = parent.selectedMembers.indexOf(user.id);
                                    if (idx === -1) {
                                        parent.selectedMembers.push(user.id);
                                    } else {
                                        parent.selectedMembers.splice(idx, 1);
                                    }
                                    // Force ComboBox to reset so user can select again
                                    teamCombo.currentIndex = -1;
                                }
                            }
                            delegate: ItemDelegate {
                                width: parent.width
                                text: model.username
                                highlighted: parent.selectedMembers.indexOf(model.id) !== -1
                                onClicked: {
                                    let idx = parent.selectedMembers.indexOf(model.id);
                                    if (idx === -1) {
                                        parent.selectedMembers.push(model.id);
                                    } else {
                                        parent.selectedMembers.splice(idx, 1);
                                    }
                                    teamCombo.currentIndex = -1;
                                }
                                background: Rectangle {
                                    color: parent.selectedMembers.indexOf(model.id) !== -1 ? "#e0f7fa" : "transparent"
                                }
                            }
                        }
                        // Show selected members below
                        Flow {
                            anchors.top: teamCombo.bottom
                            anchors.topMargin: 4
                            spacing: 8
                            Repeater {
                                model: parent.selectedMembers
                                Rectangle {
                                    color: "#e0f7fa"
                                    radius: 6
                                    border.color: "#2255aa"
                                    border.width: 1
                                    height: 28
                                    width: 100
                                    Text {
                                        anchors.centerIn: parent
                                        text: {
                                            var user = userManager.users.find(u => u.id === modelData)
                                            return user ? user.username : ""
                                        }
                                        color: "#2255aa"
                                        font.pixelSize: 14
                                    }
                                }
                            }
                        }
                    }
                    // Deadline picker
                    Row {
                        spacing: 8
                        width: 400
                        // Fallback: Simple date picker using ComboBoxes
                        Row {
                            spacing: 8
                            property int selectedYear: (new Date()).getFullYear()
                            property int selectedMonth: (new Date()).getMonth() + 1
                            property int selectedDay: (new Date()).getDate()
    
                            ComboBox {
                                id: yearCombo
                                width: 80
                                model: {
                                    let years = [];
                                    let thisYear = (new Date()).getFullYear();
                                    for (let y = thisYear; y <= thisYear + 5; ++y) years.push(y);
                                    return years;
                                }
                                onCurrentIndexChanged: parent.selectedYear = model[currentIndex]
                                currentIndex: 0
                            }
                            ComboBox {
                                id: monthCombo
                                width: 60
                                model: [1,2,3,4,5,6,7,8,9,10,11,12]
                                onCurrentIndexChanged: parent.selectedMonth = model[currentIndex]
                                currentIndex: (new Date()).getMonth()
                            }
                            ComboBox {
                                id: dayCombo
                                width: 60
                                model: {
                                    let daysInMonth = new Date(parent.selectedYear, parent.selectedMonth, 0).getDate();
                                    let days = [];
                                    for (let d = 1; d <= daysInMonth; ++d) days.push(d);
                                    return days;
                                }
                                onCurrentIndexChanged: parent.selectedDay = model[currentIndex]
                                currentIndex: (new Date()).getDate() - 1
                            }
                            Text {
                                text: "Deadline: " + parent.selectedYear + "-" +
                                    ("0" + parent.selectedMonth).slice(-2) + "-" +
                                    ("0" + parent.selectedDay).slice(-2)
                            }
                        }
                    }
    
                    // Bottom buttons
                    Row {
                        spacing: 24
                        anchors.horizontalCenter: parent.horizontalCenter
    
                        Button {
                            text: "Let's get started"
                            onClicked: {
                                let deadline =
                                    yearCombo.model[yearCombo.currentIndex] + "-" +
                                    ("0" + monthCombo.model[monthCombo.currentIndex]).slice(-2) + "-" +
                                    ("0" + dayCombo.model[dayCombo.currentIndex]).slice(-2);
                                projectManager.createProject(
                                    projectNameField.text,
                                    projectDescField.text,
                                    deadline,
                                    AuthManager.userId
                                    // TODO: Pass selectedMembers to backend if supported
                                )
                            }
                        }
                        Button {
                            text: "Cancel"
                            onClicked: {
                                root.currentPage = "dashboard"
                            }
                        }
                    }
                    Text {
                        id: createProjectStatus
                        color: "red"
                        font.pixelSize: 16
                    }
                }
    
                Connections {
                    target: projectManager
                    function onProjectCreated(success, message) {
                        createProjectStatus.text = message
                        if (success) {
                            root.currentPage = "dashboard"
                            dashboardManager.loadProjects(AuthManager.userId)
                        }
                    }
                }
            }
        }
    
        // --- All other code remains commented out below ---
 
    // --- All other code remains commented out below ---
    /*
    <rest of original file remains commented out>
    */

}

