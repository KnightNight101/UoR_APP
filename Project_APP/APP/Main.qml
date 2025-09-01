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
    // --- Project title inline edit state (moved from project details page for global access) ---
    property bool editingTitle: false
    onEditingTitleChanged: {
        console.log("DEBUG: editingTitle changed to", editingTitle)
    }
    property string editableTitle: ""
    property string titleEditStatus: ""
    // --- Tasks Model and Flat List Cache ---
    property var tasksModel: []
    property var flatTaskList: []
    // Update flatTaskList whenever tasksModel changes
    onTasksModelChanged: {
        flatTaskList = getFlatTaskList();
    }

    // Log whenever userManager.users changes
    Connections {
        target: userManager
        function onUsersChanged() {
            console.log("QML LOG: userManager.users changed:", userManager ? userManager.users : "undefined")
        }
    }

    // --- Helper functions for tasks/subtasks ---
    function getFlatTaskList() {
        var start = Date.now();
        if (!root.tasksModel || !Array.isArray(root.tasksModel)) {
            console.log("ERROR: getFlatTaskList called but root.tasksModel is", root.tasksModel);
            return [];
        }
        console.log("PERF: getFlatTaskList called at", start);
        var flat = [];
        for (var i = 0; i < root.tasksModel.length; ++i) {
            var t = root.tasksModel[i];
            if (!t) continue;
            var subtasksSum = 0;
            if (t.subtasks && Array.isArray(t.subtasks) && t.subtasks.length > 0) {
                for (var j = 0; j < t.subtasks.length; ++j) {
                    if (t.subtasks[j] && typeof t.subtasks[j].hours === "number")
                        subtasksSum += t.subtasks[j].hours;
                }
            }
            flat.push({
                isSubtask: false,
                id: t.id,
                title: t.title,
                description: t.description,
                deadline: t.deadline,
                ownersDisplay: t.owners ? t.owners.join(",") : "",
                dependenciesDisplay: t.dependencies ? t.dependencies.join(",") : "",
                hoursSum: subtasksSum > 0 ? subtasksSum : t.hours,
                hoursVerify: t.hoursVerify,
                statusIndex: t.status
            });
            if (t.subtasks && Array.isArray(t.subtasks) && t.subtasks.length > 0) {
                for (var j = 0; j < t.subtasks.length; ++j) {
                    var s = t.subtasks[j];
                    if (!s) continue;
                    flat.push({
                        isSubtask: true,
                        id: s.id,
                        title: s.title,
                        description: s.description,
                        deadline: "",
                        ownersDisplay: s.owner,
                        dependenciesDisplay: s.dependencies ? s.dependencies.join(",") : "",
                        hoursSum: s.hours,
                        hoursVerify: s.hoursVerify,
                        statusIndex: s.status
                    });
                }
            }
        }
        var end = Date.now();
        console.log("PERF: getFlatTaskList finished at", end, "duration:", (end - start), "ms");
        return flat;
    }

    function getDependencyTitles(depString) {
        var start = Date.now();
        console.log("PERF: getDependencyTitles called at", start, "depString:", depString);
        var deps = ("" + depString).split(",");
        var titles = [];
        for (var i = 0; i < deps.length; ++i) {
            var depId = deps[i];
            if (!depId || depId === "undefined") continue;
            var t = root.tasksModel.find(function(t) { return t.id == depId; });
            if (t) titles.push(t.title);
            else {
                for (var j = 0; j < root.tasksModel.length; ++j) {
                    var s = root.tasksModel[j].subtasks ? root.tasksModel[j].subtasks.find(function(st) { return st.id == depId; }) : null;
                    if (s) titles.push(s.title);
                }
            }
        }
        var end = Date.now();
        console.log("PERF: getDependencyTitles finished at", end, "duration:", (end - start), "ms");
        return titles.join(", ");
    }

    function getOwnerNames(isSubtask, ownersDisplay) {
        var start = Date.now();
        console.log("PERF: getOwnerNames called at", start, "isSubtask:", isSubtask, "ownersDisplay:", ownersDisplay);
        if (isSubtask) {
            var user = userManager && userManager.users ? userManager.users.find(function(u) { return u.id === ownersDisplay; }) : null;
            var result = user ? user.username : ownersDisplay;
            var end = Date.now();
            console.log("PERF: getOwnerNames finished at", end, "duration:", (end - start), "ms");
            return result;
        } else {
            if (!userManager || !userManager.users) {
                var end = Date.now();
                console.log("PERF: getOwnerNames finished at", end, "duration:", (end - start), "ms");
                return ownersDisplay;
            }
            var names = [];
            var ids = ("" + ownersDisplay).split(",");
            for (var i = 0; i < ids.length; ++i) {
                var user = userManager.users.find(function(u) { return u.id == ids[i]; });
                if (user) names.push(user.username);
            }
            var result = names.join(", ");
            var end = Date.now();
            console.log("PERF: getOwnerNames finished at", end, "duration:", (end - start), "ms");
            return result;
        }
    }

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
    property string currentPage: "dashboard" // "dashboard", "eventlog", "settings"

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
    function onUserIdChanged() {
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
                MenuItem { text: "Calendar"; onTriggered: { root.currentPage = "calendar" } }
                MenuItem { text: "File Manager"; onTriggered: {/* TODO: Implement file manager navigation */} }
                MenuItem { text: "Event Log"; onTriggered: root.currentPage = "eventlog" }
                MenuItem {
                    text: "Settings"
                    onTriggered: {
                        root.currentPage = "settings"
                        if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                            log_event.log_event("Navigated to settings page")
                        }
                    }
                }
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
                        Layout.alignment: Qt.AlignHCenter
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
                        y: 70
                        clip: true
                        // horizontalScrollBarPolicy removed (not supported in QtQuick.Controls 2.x)

                        Column {
                            id: projectListColumn
                            width: parent.width
                            spacing: 6
                            Repeater {
                                model: dashboardManager ? dashboardManager.projects : []
                                Component.onCompleted: {
                                    if (!dashboardManager)
                                        console.log("DEBUG: dashboardManager is null at project list")
                                }
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
            id: projectDetailsPage
            Component.onCompleted: {
                console.log("DEBUG: projectDetailsPage Component.onCompleted")
            }
            onVisibleChanged: {
                console.log("DEBUG: projectDetailsPage visible =", visible)
            }
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "projectDetails"
            property var tabLabels: ["Tasks", "Gantt Chart", "Calendar", "Team"]
            property int selectedTabIndex: 0

            // Main content rectangle (SVG spec)
            // Top bar row (Back to Dashboard + Project Title) above the main rectangle
            Row {
                id: topBarRow
                x: 45
                y: 80
                width: 900
                height: 48
                spacing: 24

                Button {
                    text: "\u25C0 Dashboard"
                    onClicked: root.currentPage = "dashboard"
                    z: 100
                }

                // Project Title Heading (inline edit)
                Item {
                    id: projectTitleEditContainer
                    width: 500
                    height: 40

                    Text {
                        id: projectDetailsTitle
                        visible: !root.editingTitle
                        text: {
                            let proj = dashboardManager.projects.find(p => p.id === root.selectedProjectId)
                            proj && proj.name && proj.name.length > 0 ? proj.name : "(Untitled Project)"
                        }
                        font.pixelSize: 32
                        font.bold: true
                        color: "#2255aa"
                    }
                    MouseArea {
                        anchors.fill: parent
                        enabled: projectDetailsTitle.visible
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            root.editingTitle = true
                            if (!dashboardManager)
                                console.log("DEBUG: dashboardManager is null at project title edit")
                            let proj = dashboardManager ? dashboardManager.projects.find(p => p.id === root.selectedProjectId) : null
                            root.editableTitle = proj && proj.name ? proj.name : ""
                            root.titleEditStatus = ""
                        }
                    }

                    Row {
                        visible: !!root.editingTitle
                        spacing: 8
                        TextField {
                            id: titleEditField
                            text: root.editableTitle || ""
                            font.pixelSize: 32
                            width: 320
                            selectByMouse: true
                            onTextChanged: root.editableTitle = text
                            focus: true
                            Keys.onReturnPressed: saveTitleBtn.clicked()
                        }
                        Button {
                            id: saveTitleBtn
                            text: "Save"
                            onClicked: {
                                if ((root.editableTitle || "").trim().length === 0) {
                                    root.titleEditStatus = "Title cannot be empty."
                                    return
                                }
                                projectManager.updateProjectTitle(
                                    root.selectedProjectId,
                                    AuthManager.userId,
                                    root.editableTitle
                                )
                            }
                        }
                        Button {
                            text: "Cancel"
                            onClicked: {
                                root.editingTitle = false
                                root.titleEditStatus = ""
                            }
                        }
                    }
                    Text {
                        text: root.titleEditStatus || ""
                        color: (root.titleEditStatus === "Project title updated successfully.") ? "green" : "red"
                        font.pixelSize: 14
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.topMargin: 44
                        visible: !!root.editingTitle && (root.titleEditStatus || "").length > 0
                    }
                }
            }

            Rectangle {
                id: projectDetailsMainRect
                x: 45
                y: 131
                width: 1666
                height: 921
                color: "#D9D9D9"
                radius: 18

                // Delete Project Button (top right)
                Button {
                    id: deleteProjectBtn
                    text: "Delete Project"
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.topMargin: 24
                    anchors.rightMargin: 32
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
                            deleteProjectDialog.close()
                            if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                                log_event.log_event("Project deletion failed: " + message)
                            }
                        }
                    }
                }

                // Project Title Heading

                // --- Vertical Tab Bar removed from here; moved to right sidebar ---

                // --- Tab Content (all tabs inside main rectangle) ---
                Item {
                    id: tabContentContainer
                    anchors.fill: parent
                    anchors.margins: 80
                    // Tasks Tab
                    Item {
                        id: taskTab
                        anchors.fill: parent
                        visible: projectDetailsPage.selectedTabIndex === 0
                        Text {
                            anchors.centerIn: parent
                            text: "Tasks tab content goes here."
                            color: "#2255aa"
                            font.pixelSize: 28
                            font.bold: true
                        }
                    }
                    // Gantt Chart Tab
                    Item {
                        id: ganttTab
                        anchors.fill: parent
                        visible: projectDetailsPage.selectedTabIndex === 1
                        Text {
                            anchors.centerIn: parent
                            text: "Gantt Chart tab content goes here."
                            color: "#2255aa"
                            font.pixelSize: 28
                            font.bold: true
                        }
                    }
                    // Calendar Tab
                    Item {
                        id: calendarTab
                        anchors.fill: parent
                        visible: projectDetailsPage.selectedTabIndex === 2
                        // --- Basic Month Calendar (no events, no dialogs, no backend) ---
                        property date calendarCurrentMonth: new Date()
                        property date calendarSelectedDate: new Date()

                        // Top bar with month navigation
                        Rectangle {
                            width: parent.width
                            height: 48
                            color: "#fff"
                            border.color: "#2255aa"
                            border.width: 2
                            radius: 12
                            anchors.top: parent.top
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.topMargin: 8

                            Row {
                                anchors.centerIn: parent
                                spacing: 24

                                Button {
                                    text: "<"
                                    onClicked: {
                                        let d = new Date(calendarTab.calendarCurrentMonth)
                                        d.setMonth(d.getMonth() - 1)
                                        calendarTab.calendarCurrentMonth = d
                                    }
                                }
                                Text {
                                    text: Qt.formatDate(calendarTab.calendarCurrentMonth, "MMMM yyyy")
                                    font.pixelSize: 20
                                    color: "#2255aa"
                                    font.bold: true
                                    verticalAlignment: Text.AlignVCenter
                                }
                                Button {
                                    text: ">"
                                    onClicked: {
                                        let d = new Date(calendarTab.calendarCurrentMonth)
                                        d.setMonth(d.getMonth() + 1)
                                        calendarTab.calendarCurrentMonth = d
                                    }
                                }
                            }
                        }

                        // Month view
                        Item {
                            id: projectCalendarWidget
                            width: Math.min(parent.width, 520)
                            height: Math.min(parent.height - 70, 340)
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 64

                            property int year: calendarTab.calendarCurrentMonth.getFullYear()
                            property int month: calendarTab.calendarCurrentMonth.getMonth()
                            property int firstDayOfWeek: (new Date(year, month, 1)).getDay() // 0=Sun
                            property int daysInMonth: (new Date(year, month + 1, 0)).getDate()
                            property int weeks: Math.ceil((firstDayOfWeek + daysInMonth) / 7)

                            // Weekday headers
                            Row {
                                anchors.top: parent.top
                                anchors.left: parent.left
                                anchors.right: parent.right
                                spacing: 0
                                width: parent.width
                                Repeater {
                                    model: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                                    delegate: Rectangle {
                                        width: parent.width / 7
                                        height: 28
                                        color: "#e9eef6"
                                        border.color: "#2255aa"
                                        border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData
                                            color: "#2255aa"
                                            font.pixelSize: 14
                                            font.bold: true
                                        }
                                    }
                                }
                            }

                            // Month grid
                            Grid {
                                id: projectCalendarGrid
                                anchors.top: parent.top
                                anchors.topMargin: 32
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.margins: 8
                                columns: 7
                                rows: projectCalendarWidget.weeks
                                width: parent.width - 16
                                height: parent.height - 40
                            
                                Repeater {
                                    model: projectCalendarWidget.weeks * 7
                                    delegate: Item {
                                        width: parent.width / 7
                                        height: (parent.height) / projectCalendarWidget.weeks
                                        property int dayNum: index - projectCalendarWidget.firstDayOfWeek + 1
                                        visible: dayNum > 0 && dayNum <= projectCalendarWidget.daysInMonth
                                        Rectangle {
                                            width: parent.width
                                            height: parent.height
                                            color: (Qt.formatDate(calendarTab.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(projectCalendarWidget.year, projectCalendarWidget.month, dayNum), "yyyy-MM-dd"))
                                                ? "#e0f7fa"
                                                : "transparent"
                                            border.color: (Qt.formatDate(calendarTab.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(projectCalendarWidget.year, projectCalendarWidget.month, dayNum), "yyyy-MM-dd")) ? "#2255aa" : "transparent"
                                            border.width: (Qt.formatDate(calendarTab.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(projectCalendarWidget.year, projectCalendarWidget.month, dayNum), "yyyy-MM-dd")) ? 2 : 0
                                            radius: 6
                                            MouseArea {
                                                anchors.fill: parent
                                                enabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    calendarTab.calendarSelectedDate = new Date(projectCalendarWidget.year, projectCalendarWidget.month, dayNum)
                                                }
                                            }
                                            Text {
                                                anchors.centerIn: parent
                                                text: dayNum
                                                color: "#2255aa"
                                                font.pixelSize: 16
                                                font.bold: Qt.formatDate(calendarTab.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(projectCalendarWidget.year, projectCalendarWidget.month, dayNum), "yyyy-MM-dd")
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    // Team Tab
                    Item {
                        id: teamTab
                        anchors.fill: parent
                        visible: projectDetailsPage.selectedTabIndex === 3

                        // Refresh users and log when tab becomes visible
                        property bool wasVisible: false
                        onVisibleChanged: {
                            if (visible && !wasVisible) {
                                if (typeof userManager !== "undefined" && typeof userManager.loadUsers === "function") {
                                    userManager.loadUsers();
                                    console.log("QML LOG: Called userManager.loadUsers() on Team tab entry");
                                }
                                if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                                    log_event.log_event("Navigated to Team tab");
                                }
                                wasVisible = true;
                            } else if (!visible) {
                                wasVisible = false;
                            }
                        }

                        // --- Team Management UI ---
                        Column {
                            anchors.fill: parent
                            spacing: 24

                            Component.onCompleted: {
                                console.log("QML LOG: Team tab loaded. userManager.users =", userManager ? userManager.users : "undefined")
                            }

                            // Add Team Member Row
                            Row {
                                spacing: 12
                                ComboBox {
                                    id: addTeamUserCombo
                                    width: 200
                                    model: userManager ? userManager.users : []
                                    textRole: "username"
                                    valueRole: "id"
                                    editable: false

                                    onModelChanged: {
                                        console.log("QML LOG: ComboBox model changed. New model =", model)
                                    }
                                }
                                TextField {
                                    id: addTeamRoleField
                                    width: 160
                                    placeholderText: "Role"
                                }
                                Button {
                                    text: "Add"
                                    // No logic required at this stage
                                }
                            }

                            // Team Members Table Header
                            Row {
                                spacing: 12
                                width: parent.width
                                Text { text: "Member"; font.bold: true; width: 200 }
                                Text { text: "Role"; font.bold: true; width: 160 }
                                Text { text: ""; width: 100 }
                            }

                            // Team Members List (UI only, no backend logic)
                            Column {
                                spacing: 8
                                Repeater {
                                    model: projectManager && projectManager.currentProjectTeam ? projectManager.currentProjectTeam : []
                                    delegate: Row {
                                        spacing: 12
                                        width: parent.width
                                        Text {
                                            width: 200
                                            text: {
                                                var user = userManager && userManager.users
                                                    ? userManager.users.find(u => u.id === modelData.userId)
                                                    : null;
                                                return user ? user.username : modelData.userId;
                                            }
                                        }
                                        Text {
                                            width: 160
                                            text: modelData.role
                                        }
                                        Button {
                                            text: "Remove team member"
                                            // No logic required at this stage
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Right sidebar rectangle (SVG spec)
            Rectangle {
                id: projectDetailsSidebar
                x: 1742
                y: 131
                width: 149
                height: 921
                color: "#D9D9D9"
                radius: 18

                // --- Vertical Tab Bar (now in right sidebar) ---
                Column {
                    id: verticalTabBar
                    width: parent.width
                    height: 260
                    spacing: 0
                    anchors.top: parent.top
                    anchors.topMargin: 120
                    anchors.horizontalCenter: parent.horizontalCenter
                    z: 50

                    Repeater {
                        model: projectDetailsPage.tabLabels ? projectDetailsPage.tabLabels.length : 0
                        delegate: Rectangle {
                            width: parent.width
                            height: 48
                            color: index === projectDetailsPage.selectedTabIndex ? "#fff" : "#e9eef6"
                            border.color: index === projectDetailsPage.selectedTabIndex ? "#2255aa" : "#e9eef6"
                            border.width: 2
                            radius: 24
                            antialiasing: true

                            Row {
                                spacing: 0
                                Rectangle {
                                    width: 6
                                    height: parent.height
                                    color: index === projectDetailsPage.selectedTabIndex ? "#2255aa" : "transparent"
                                    radius: 3
                                }
                                Text {
                                    verticalAlignment: Text.AlignVCenter
                                    horizontalAlignment: Text.AlignHCenter
                                    text: projectDetailsPage.tabLabels[index]
                                    color: "#2255aa"
                                    font.pixelSize: 16
                                    font.bold: index === projectDetailsPage.selectedTabIndex
                                }
                            }

                            MouseArea {
                                width: parent.width
                                height: parent.height
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    projectDetailsPage.selectedTabIndex = index
                                }
                            }
                        }
                    }
                }
            }
// --- Task Tab UI (visible when "Tasks" tab is selected) ---
    // --- Frontend model for tasks and subtasks (demo, replace with backend binding as needed) ---
    // property var tasksModel: [] // Moved to ApplicationWindow root

    // Helper to flatten tasks and subtasks for display
    // (Moved to ApplicationWindow root scope below)
// Helper to resolve owner names for display in QML Text


// === MOVE ALL HELPERS TO ROOT SCOPE ===

// (Insert after ApplicationWindow { ... properties ... } and before any Item/Rectangle)

// --- INSERT AT LINE 32 (after ApplicationWindow properties, before onClosing) ---


// === END INSERT ===

// Remove all helper function definitions from inside Item/Rectangle blocks below

/* === RESTORED TASK TAB UI: Only tab container, no dialogs or editing features === */
// Removed duplicate tab Item blocks after refactor. Tab content is now handled inside Rectangle's tabContentContainer.
/* === GANTT CHART TAB UI === */
// Removed duplicate tab Item blocks after refactor. Tab content is now handled inside Rectangle's tabContentContainer.
/* === CALENDAR TAB UI === */
// Removed duplicate tab Item blocks after refactor. Tab content is now handled inside Rectangle's tabContentContainer.
/* === TEAM TAB UI === */
// Removed duplicate tab Item blocks after refactor. Tab content is now handled inside Rectangle's tabContentContainer.
            // DEBUG: Centered debug rectangle for layout testing
            }
            // Listen for projectTitleUpdated signal
            // Listen for projectTitleUpdated signal
            Connections {
                target: projectManager
                function onProjectTitleUpdated(success, message) {
                    root.titleEditStatus = message
                    if (success) {
                        dashboardManager.loadProjects(AuthManager.userId)
                        root.editingTitle = false
                        // Optionally, refresh project details if needed
                    }
                }
            }

            // Log event when page is shown
            Component.onCompleted: {
                if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                    let proj = dashboardManager.projects.find(p => p.id === root.selectedProjectId)
                    let pname = proj && proj.name && proj.name.length > 0 ? proj.name : "(Untitled Project)"
                    log_event.log_event("Opened project details: " + pname)
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
/* === ADD/EDIT TASK DIALOG COMMENTED OUT FOR TAB TESTING ===
// --- Add/Edit Task Dialog ---
Dialog {
    id: taskDialog
    // ... (all add/edit task dialog UI and logic commented out) ...
}
=== END ADD/EDIT TASK DIALOG === */
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
                            model: userManager ? userManager.users : []
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

        // --- Calendar Page (visible when logged in and currentPage is "calendar") ---
        Item {
            id: calendarPage
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "calendar"
            // Back to Dashboard Button
            Button {
                text: "\u25C0 Dashboard"
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 24
                anchors.leftMargin: 32
                z: 100
                onClicked: root.currentPage = "dashboard"
            }
        
            // --- Calendar State ---
            property date calendarCurrentMonth: new Date()
            property date calendarSelectedDate: new Date()
            property var calendarEvents: ({}) // { "yyyy-MM-dd": [ {title, desc, time} ] }
            property bool addEventDialogOpen: false
            property bool takeTimeOffDialogOpen: false
            property string newEventTitle: ""
            property string newEventDesc: ""
            property string newEventTime: ""

            // --- Top Bar with Navigation ---
            Rectangle {
                width: 600
                height: 60
                color: "#fff"
                border.color: "#2255aa"
                border.width: 2
                radius: 16
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 32

                Row {
                    anchors.centerIn: parent
                    spacing: 24

                    Button {
                        text: "<"
                        onClicked: {
                            let d = new Date(calendarPage.calendarCurrentMonth)
                            d.setMonth(d.getMonth() - 1)
                            calendarPage.calendarCurrentMonth = d
                        }
                    }
                    Text {
                        text: Qt.formatDate(calendarPage.calendarCurrentMonth, "MMMM yyyy")
                        font.pixelSize: 24
                        color: "#2255aa"
                        font.bold: true
                        verticalAlignment: Text.AlignVCenter
                    }
                    Button {
                        text: ">"
                        onClicked: {
                            let d = new Date(calendarPage.calendarCurrentMonth)
                            d.setMonth(d.getMonth() + 1)
                            calendarPage.calendarCurrentMonth = d
                        }
                    }
                }
            }

            // --- Calendar Month View ---
            Item {
                id: mainCalendarWidget
                anchors.top: parent.top
                anchors.topMargin: 110
                anchors.horizontalCenter: parent.horizontalCenter
                width: 600
                height: 400
            
                property int year: calendarPage.calendarCurrentMonth.getFullYear()
                property int month: calendarPage.calendarCurrentMonth.getMonth()
                property int firstDayOfWeek: (new Date(year, month, 1)).getDay() // 0=Sun
                property int daysInMonth: (new Date(year, month + 1, 0)).getDate()
                property int weeks: Math.ceil((firstDayOfWeek + daysInMonth) / 7)
            
                // Weekday headers
                Row {
                    anchors.top: parent.top
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 0
                    width: parent.width
                    Repeater {
                        model: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                        delegate: Rectangle {
                            width: parent.width / 7
                            height: 32
                            color: "#e9eef6"
                            border.color: "#2255aa"
                            border.width: 1
                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                color: "#2255aa"
                                font.pixelSize: 16
                                font.bold: true
                            }
                        }
                    }
                }
            
                // Month grid
                Grid {
                    id: calendarGrid
                    anchors.top: parent.top
                    anchors.topMargin: 40
                    anchors.horizontalCenter: parent.horizontalCenter
                    columns: 7
                    rows: mainCalendarWidget.weeks
                    width: parent.width
                    height: parent.height - 40
            
                    Repeater {
                        model: mainCalendarWidget.weeks * 7
                        delegate: Item {
                            width: parent.width / 7
                            height: (parent.height) / mainCalendarWidget.weeks
                            property int dayNum: index - mainCalendarWidget.firstDayOfWeek + 1
                            visible: dayNum > 0 && dayNum <= mainCalendarWidget.daysInMonth
                            Rectangle {
                                width: parent.width
                                height: parent.height
                                color: (dayNum === calendarPage.calendarCurrentMonth.getDate() &&
                                        calendarPage.calendarCurrentMonth.getMonth() === mainCalendarWidget.month &&
                                        calendarPage.calendarCurrentMonth.getFullYear() === mainCalendarWidget.year)
                                    ? "#e0f7fa"
                                    : (Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(mainCalendarWidget.year, mainCalendarWidget.month, dayNum), "yyyy-MM-dd") ? "#e0f7fa" : "transparent")
                                border.color: (Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(mainCalendarWidget.year, mainCalendarWidget.month, dayNum), "yyyy-MM-dd")) ? "#2255aa" : "transparent"
                                border.width: (Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(mainCalendarWidget.year, mainCalendarWidget.month, dayNum), "yyyy-MM-dd")) ? 2 : 0
                                radius: 8
                                MouseArea {
                                    anchors.fill: parent
                                    enabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        calendarPage.calendarSelectedDate = new Date(mainCalendarWidget.year, mainCalendarWidget.month, dayNum)
                                    }
                                }
                                Text {
                                    anchors.centerIn: parent
                                    text: dayNum
                                    color: "#2255aa"
                                    font.pixelSize: 18
                                    font.bold: Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(mainCalendarWidget.year, mainCalendarWidget.month, dayNum), "yyyy-MM-dd")
                                }
                            }
                        }
                    }
                }
            }

            // Take Time Off Dialog
            Dialog {
                id: takeTimeOffDialog
                modal: true
                visible: calendarPage.takeTimeOffDialogOpen
                width: 400
                height: 320
                x: (parent.width - width) / 2
                y: (parent.height - height) / 2
                property date startDate: new Date()
                property date endDate: new Date()
                property string reason: ""
                onAccepted: {
                    let d = new Date(startDate);
                    while (d <= endDate) {
                        let key = Qt.formatDate(d, "yyyy-MM-dd");
                        if (!calendarPage.calendarEvents[key])
                            calendarPage.calendarEvents[key] = [];
                        calendarPage.calendarEvents[key].push({
                            title: "Time Off",
                            desc: reason,
                            time: "",
                            type: "timeoff"
                        });
                        d.setDate(d.getDate() + 1);
                    }
                    calendarPage.takeTimeOffDialogOpen = false;
                    reason = "";
                }
                onRejected: {
                    calendarPage.takeTimeOffDialogOpen = false;
                    reason = "";
                }
                Rectangle {
                    anchors.fill: parent
                    color: "#fff"
                    radius: 12
                    border.color: "#2255aa"
                    border.width: 2
                    Column {
                        anchors.centerIn: parent
                        spacing: 16
                        Text {
                            text: "Take Time Off"
                            font.pixelSize: 22
                            color: "#2255aa"
                            font.bold: true
                        }
                        Row {
                            spacing: 8
                            Text {
                                text: "Start:"
                            }
                            TextField {
                                width: 120
                                text: Qt.formatDate(takeTimeOffDialog.startDate, "yyyy-MM-dd")
                                readOnly: true
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: takeTimeOffDialog.startDate = calendarPage.calendarSelectedDate
                                }
                            }
                            Text {
                                text: "End:"
                            }
                            TextField {
                                width: 120
                                text: Qt.formatDate(takeTimeOffDialog.endDate, "yyyy-MM-dd")
                                readOnly: true
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: takeTimeOffDialog.endDate = calendarPage.calendarSelectedDate
                                }
                            }
                        }
                        TextField {
                            placeholderText: "Reason (optional)"
                            text: takeTimeOffDialog.reason
                            onTextChanged: takeTimeOffDialog.reason = text
                            width: 300
                        }
                        Row {
                            spacing: 16
                            Button {
                                text: "Confirm"
                                onClicked: takeTimeOffDialog.accepted()
                            }
                            Button {
                                text: "Cancel"
                                onClicked: takeTimeOffDialog.rejected()
                            }
                        }
                    }
                }
            }

            // --- Calendar Action Buttons Row ---
            Row {
                anchors.top: mainCalendarWidget.bottom
                anchors.topMargin: 16
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 16

                Button {
                    text: "Add Event/Task"
                    onClicked: calendarPage.addEventDialogOpen = true
                }
                Button {
                    text: "Take Time Off"
                    onClicked: calendarPage.takeTimeOffDialogOpen = true
                }
                Button {
                    text: "Import iCal (.ics)"
                    onClicked: {
                        if (typeof backend !== "undefined" && backend.importICal)
                            backend.importICal();
                    }
                }
                Button {
                    text: "Export as iCal (.ics)"
                    onClicked: {
                        if (typeof backend !== "undefined" && backend.exportICal)
                            backend.exportICal();
                    }
                }
            }

            // --- Events/Tasks List for Selected Date ---
            Rectangle {
                width: 600
                height: 180
                color: "#f8f9fa"
                border.color: "#2255aa"
                border.width: 2
                radius: 16
                anchors.top: mainCalendarWidget.bottom
                anchors.topMargin: 64
                anchors.horizontalCenter: parent.horizontalCenter

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    Text {
                        text: "Events/Tasks for " + Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd")
                        font.pixelSize: 20
                        color: "#2255aa"
                        font.bold: true
                    }

                    Repeater {
                        model: (calendarPage.calendarEvents[Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd")] || [])
                        delegate: Rectangle {
                            width: parent.width
                            height: 40
                            color: "#fff"
                            border.color: "#bbb"
                            border.width: 1
                            radius: 8
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 12
                                Text {
                                    text: modelData.time
                                    font.pixelSize: 14
                                    color: "#888"
                                    width: 60
                                }
                                Text {
                                    text: modelData.title
                                    font.pixelSize: 16
                                    color: "#2255aa"
                                    font.bold: true
                                }
                                Text {
                                    text: modelData.desc
                                    font.pixelSize: 14
                                    color: "#222"
                                }
                            }
                        }
                    }
                    // If no events
                    Text {
                        text: (calendarPage.calendarEvents[Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd")] || []).length === 0 ? "No events/tasks for this date." : ""
                        color: "#888"
                        font.pixelSize: 16
                    }
                }
            }

            // --- Add Event/Task Dialog ---
            Dialog {
                id: addEventDialog
                modal: true
                visible: calendarPage.addEventDialogOpen
                width: 400
                height: 320
                x: (parent.width - width) / 2
                y: (parent.height - height) / 2
                onAccepted: {
                    let key = Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd")
                    if (!calendarPage.calendarEvents[key])
                        calendarPage.calendarEvents[key] = []
                    calendarPage.calendarEvents[key].push({
                        title: calendarPage.newEventTitle,
                        desc: calendarPage.newEventDesc,
                        time: calendarPage.newEventTime
                    })
                    // Reset fields
                    calendarPage.newEventTitle = ""
                    calendarPage.newEventDesc = ""
                    calendarPage.newEventTime = ""
                    calendarPage.addEventDialogOpen = false
                }
                onRejected: {
                    calendarPage.addEventDialogOpen = false
                }
                Rectangle {
                    anchors.fill: parent
                    color: "#fff"
                    radius: 12
                    border.color: "#2255aa"
                    border.width: 2

                    Column {
                        anchors.centerIn: parent
                        spacing: 16
                        Text {
                            text: "Add Event/Task"
                            font.pixelSize: 22
                            color: "#2255aa"
                            font.bold: true
                        }
                        TextField {
                            placeholderText: "Title"
                            text: calendarPage.newEventTitle
                            onTextChanged: calendarPage.newEventTitle = text
                            width: 300
                        }
                        TextField {
                            placeholderText: "Description"
                            text: calendarPage.newEventDesc
                            onTextChanged: calendarPage.newEventDesc = text
                            width: 300
                        }
                        TextField {
                            placeholderText: "Time (e.g. 14:00)"
                            text: calendarPage.newEventTime
                            onTextChanged: calendarPage.newEventTime = text
                            width: 300
                            // --- Loading Overlay (must be last so it overlays all content) ---
                            Rectangle {
                                id: loadingOverlay
                                anchors.fill: parent
                                color: "#ffffffcc"
                                visible: loadingManager ? loadingManager.loading : false
                                z: 9999
                                Component.onCompleted: {
                                    if (!loadingManager)
                                        console.log("DEBUG: loadingManager is null at loadingOverlay")
                                }
                        
                                Column {
                                    anchors.centerIn: parent
                                    spacing: 24
                                    ProgressBar {
                                        id: progressBar
                                        width: 240
                                        from: 0
                                        to: 1
                                        value: loadingManager ? loadingManager.progress : 0
                                        Component.onCompleted: {
                                            if (!loadingManager)
                                                console.log("DEBUG: loadingManager is null at progressBar")
                                        }
                                    }
                                    Text {
                                        text: "Loading, please wait..."
                                        font.pixelSize: 20
                                        color: "#2255aa"
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                            }
                        }
                        Row {
                            spacing: 16
                            Button {
                                text: "Add"
                                onClicked: addEventDialog.accepted()
                            }
                            Button {
                                text: "Cancel"
                                onClicked: addEventDialog.rejected()
                            }
                        }
                    }
                }
            }
        }

        // --- Settings Page (visible when logged in and currentPage is "settings") ---
        Item {
            id: settingsPage
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "settings"

            // Top bar row with back button and title (top left of the page)
            Row {
                spacing: 16
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 24
                anchors.leftMargin: 32

                Button {
                    text: "\u25C0 Dashboard"
                    onClicked: {
                        root.currentPage = "dashboard"
                        if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                            log_event.log_event("Returned to dashboard from settings")
                        }
                    }
                    z: 100
                }
                Text {
                    text: "Settings"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#2255aa"
                    verticalAlignment: Text.AlignVCenter
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            // Centered content box for settings content (empty for now)
            Rectangle {
                width: 600
                height: 400
                color: "#fff"
                border.color: "#2255aa"
                border.width: 3
                radius: 24
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                z: 10
            }
        }

    // --- All other code remains commented out below ---
    /*
    <rest of original file remains commented out>
    */

}
