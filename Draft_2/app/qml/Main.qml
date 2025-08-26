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
            id: projectDetailsPage
            anchors.fill: parent
            visible: root.loggedIn && root.currentPage === "projectDetails"
            // Move title edit state to root for reliable access
            property var tabLabels: ["Tasks", "Gantt Chart", "Calendar", "Team"]

            // --- Tab Bar State ---
            property int selectedTabIndex: 0

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
                        // Optionally show error to user
                        deleteProjectDialog.close()
                        if (typeof log_event !== "undefined" && typeof log_event.log_event === "function") {
                            log_event.log_event("Project deletion failed: " + message)
                        }
                    }
                }
            }

            // Project Title Heading
            Item {
                id: projectTitleEditContainer
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.topMargin: 28
                anchors.leftMargin: 200
                width: 500
                height: 40

                // Normal display mode: plain text, clickable to edit
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
                        console.log("DEBUG: Project title clicked, switching to edit mode")
                        root.editingTitle = true
                        let proj = dashboardManager.projects.find(p => p.id === root.selectedProjectId)
                        root.editableTitle = proj && proj.name ? proj.name : ""
                        root.titleEditStatus = ""
                    }
                }

                // Edit mode: TextField + Save/Cancel, only visible when editing
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
                // Status message (optional, only in edit mode)
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
            // --- Vertical Tab Bar (right side, folder-style tabs) ---
            Column {
                id: verticalTabBar
                width: 120
                height: 260
                spacing: 0
                x: parent.width - 120
                y: 120
                z: 50
                // Only the Column itself uses x/y for positioning; children must NOT use anchors


                Repeater {
                    model: projectDetailsPage.tabLabels ? projectDetailsPage.tabLabels.length : 0
                    delegate: Rectangle {
                        width: 120
                        height: 48
                        color: index === projectDetailsPage.selectedTabIndex ? "#fff" : "#e9eef6"
                        border.color: index === projectDetailsPage.selectedTabIndex ? "#2255aa" : "#e9eef6"
                        border.width: 2
                        radius: 24
                        antialiasing: true

                        Component.onCompleted: {
                            console.log("DEBUG: TabBar delegate created. tabLabels =", projectDetailsPage.tabLabels, "index =", index, "selectedTabIndex =", projectDetailsPage.selectedTabIndex)
                            // Log all anchor properties for this delegate
                            console.log("DEBUG: TabBar delegate anchors:",
                                "top", parent.anchors && parent.anchors.top,
                                "bottom", parent.anchors && parent.anchors.bottom,
                                "verticalCenter", parent.anchors && parent.anchors.verticalCenter,
                                "fill", parent.anchors && parent.anchors.fill,
                                "centerIn", parent.anchors && parent.anchors.centerIn
                            );
                        }

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
                                console.log("DEBUG: Tab clicked. index =", index, "old selectedTabIndex =", projectDetailsPage.selectedTabIndex)
                                projectDetailsPage.selectedTabIndex = index
                                console.log("DEBUG: selectedTabIndex updated to", projectDetailsPage.selectedTabIndex)
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

Item {
    id: taskTab
    anchors.fill: parent
    // Hierarchical task/subtask tree/list
    Rectangle {
        id: taskTreeBox
        anchors.fill: parent
        color: "#f8f9fa"
        border.color: "#2255aa"
        border.width: 2
        radius: 16
        anchors.margins: 32

        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 8

            // Header row
            Row {
                spacing: 12
                Text { text: "Title"; font.bold: true; width: 120 }
                Text { text: "Description"; font.bold: true; width: 180 }
                Text { text: "Deadline"; font.bold: true; width: 90 }
                Text { text: "Owners"; font.bold: true; width: 90 }
                Text { text: "Dependencies"; font.bold: true; width: 110 }
                Text { text: "Hours (sum)"; font.bold: true; width: 70 }
                Text { text: "Verify"; font.bold: true; width: 60 }
                Text { text: "Status"; font.bold: true; width: 90 }
                Text { text: ""; width: 90 } // Actions
            }

            // Task/subtask rows (dynamic)
            Repeater {
                model: root.flatTaskList
                delegate: Row {
                    spacing: 12
                    Component.onCompleted: {
                        console.log("PERF: TaskTab delegate created for", modelData.title, "isSubtask:", modelData.isSubtask);
                    }
                    // Indent subtasks
                    Item { width: modelData.isSubtask ? 24 : 0 }
                    Text { text: modelData.title; width: 120 }
                    Text { text: modelData.description; width: 180 }
                    Text { text: modelData.deadline; width: 90 }
                    // Owners display (resolve user names if available)
                    Text {
                        width: 90
                        text: root.getOwnerNames(modelData.isSubtask, modelData.ownersDisplay)
                    }
                    // Dependencies display (resolve task/subtask titles)
                    Text {
                        width: 110
                        text: root.getDependencyTitles(modelData.dependenciesDisplay)
                    }

    // --- Add/Edit Subtask Dialog ---
    Dialog {
        id: subtaskDialog
        modal: true
        property bool editMode: false
        property int parentTaskIndex: -1
        property int editSubtaskIndex: -1
        property var subtaskData: {
            return {
                title: "",
                description: "",
                owner: null,
                dependencies: [],
                hours: 0,
                hoursVerify: 0,
                status: 0
            }
        }
        width: 480
        height: 500
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        Column {
            anchors.centerIn: parent
            spacing: 12
            Text { text: editMode ? "Edit Subtask" : "Add Subtask"; font.pixelSize: 22; font.bold: true }
            TextField { placeholderText: "Title"; text: subtaskDialog.subtaskData.title; onTextChanged: subtaskDialog.subtaskData.title = text }
            TextField { placeholderText: "Description"; text: subtaskDialog.subtaskData.description; onTextChanged: subtaskDialog.subtaskData.description = text }
            // Owner single-select
            ComboBox {
                id: subOwnerCombo
                width: 400
                model: userManager ? userManager.users : []
                textRole: "username"
                valueRole: "id"
                editable: false
                currentIndex: userManager && subtaskDialog.subtaskData.owner !== null ? userManager.users.findIndex(u => u.id === subtaskDialog.subtaskData.owner) : -1
                onActivated: {
                    if (Array.isArray(currentIndex)) {
                        // Multiple owners selected, prompt to duplicate
                        // TODO: Show duplication prompt
                    } else {
                        subtaskDialog.subtaskData.owner = userManager.users[currentIndex].id;
                    }
                }
            }
            // Dependencies multi-select (grouped by parent task)
            Rectangle {
                width: 400; height: 40; color: "#f8f9fa"; border.color: "#bbb"; border.width: 1; radius: 8
                property var selectedDeps: subtaskDialog.subtaskData.dependencies
                ComboBox {
                    id: subDepCombo
                    width: parent.width
                    model: root.tasksModel ? root.tasksModel : []
                    textRole: "title"
                    valueRole: "id"
                    editable: false
                    onActivated: {
                        let task = tasksModel[currentIndex];
                        let idx = parent.selectedDeps.indexOf(task.id);
                        if (idx === -1) parent.selectedDeps.push(task.id);
                        else parent.selectedDeps.splice(idx, 1);
                        subDepCombo.currentIndex = -1;
                    }
                    delegate: ItemDelegate {
                        width: parent.width
                        text: model.title
                        highlighted: parent.selectedDeps.indexOf(model.id) !== -1
                        onClicked: {
                            let idx = parent.selectedDeps.indexOf(model.id);
                            if (idx === -1) parent.selectedDeps.push(model.id);
                            else parent.selectedDeps.splice(idx, 1);
                            subDepCombo.currentIndex = -1;
                        }
                        background: Rectangle { color: parent.selectedDeps.indexOf(model.id) !== -1 ? "#e0f7fa" : "transparent" }
                    }
                }
            }
            TextField { placeholderText: "Hours to complete"; text: subtaskDialog.subtaskData.hours; inputMethodHints: Qt.ImhDigitsOnly; onTextChanged: subtaskDialog.subtaskData.hours = parseInt(text) }
            TextField { placeholderText: "Hours to verify"; text: subtaskDialog.subtaskData.hoursVerify; inputMethodHints: Qt.ImhDigitsOnly; onTextChanged: subtaskDialog.subtaskData.hoursVerify = parseInt(text) }
            ComboBox { width: 180; model: ["not yet started", "in progress", "being tested", "complete"]; currentIndex: subtaskDialog.subtaskData.status; onCurrentIndexChanged: subtaskDialog.subtaskData.status = currentIndex }
            Row {
                spacing: 16
                Button {
                    text: "Save"
                    onClicked: {
                        if (taskDialog.editMode) {
                            // Edit existing task
                            let t = tasksModel[taskDialog.editTaskIndex];
                            t.title = taskDialog.taskData.title;
                            t.description = taskDialog.taskData.description;
                            t.deadline = taskDialog.taskData.deadline;
                            t.owners = taskDialog.taskData.owners.slice();
                            t.dependencies = taskDialog.taskData.dependencies.slice();
                            t.hours = taskDialog.taskData.hours;
                            t.hoursVerify = taskDialog.taskData.hoursVerify;
                            t.status = taskDialog.taskData.status;
                        } else {
                            // Add new task
                            let newId = Math.max(0, ...tasksModel.map(t => t.id)) + 1;
                            tasksModel.push({
                                id: newId,
                                title: taskDialog.taskData.title,
                                description: taskDialog.taskData.description,
                                deadline: taskDialog.taskData.deadline,
                                owners: taskDialog.taskData.owners.slice(),
                                dependencies: taskDialog.taskData.dependencies.slice(),
                                hours: taskDialog.taskData.hours,
                                hoursVerify: taskDialog.taskData.hoursVerify,
                                status: taskDialog.taskData.status,
                                subtasks: []
                            });
                        }
                        taskDialog.close();
                    }
                }
                Button { text: "Cancel"; onClicked: subtaskDialog.close() }
            }
        }
    }
                    Text { text: modelData.hoursSum; width: 70 }
                    Text { text: modelData.hoursVerify; width: 60 }
                    ComboBox {
                        width: 90
                        model: ["not yet started", "in progress", "being tested", "complete"]
                        currentIndex: modelData.statusIndex
                        onCurrentIndexChanged: {
                            if (!modelData.isSubtask) {
                                let idx = tasksModel.findIndex(t => t.id === modelData.id);
                                if (idx !== -1) tasksModel[idx].status = currentIndex;
                            } else {
                                let parentIdx = tasksModel.findIndex(t => t.subtasks && t.subtasks.find(st => st.id === modelData.id));
                                let subIdx = tasksModel[parentIdx].subtasks.findIndex(st => st.id === modelData.id);
                                if (parentIdx !== -1 && subIdx !== -1) tasksModel[parentIdx].subtasks[subIdx].status = currentIndex;
                            }
                        }
                    }
                    Row {
                        spacing: 4
                        Button {
                            text: "Edit"
                            onClicked: {
                                if (!modelData.isSubtask) {
                                    taskDialog.editMode = true;
                                    taskDialog.editTaskIndex = tasksModel.findIndex(t => t.id === modelData.id);
                                    let t = tasksModel[taskDialog.editTaskIndex];
                                    taskDialog.taskData = {
                                        title: t.title,
                                        description: t.description,
                                        deadline: t.deadline,
                                        owners: t.owners.slice(),
                                        dependencies: t.dependencies.slice(),
                                        hours: t.hours,
                                        hoursVerify: t.hoursVerify,
                                        status: t.status
                                    };
                                    taskDialog.open();
                                } else {
                                    // Subtask edit
                                    let parentIdx = tasksModel.findIndex(t => t.subtasks && t.subtasks.find(st => st.id === modelData.id));
                                    let subIdx = tasksModel[parentIdx].subtasks.findIndex(st => st.id === modelData.id);
                                    subtaskDialog.editMode = true;
                                    subtaskDialog.parentTaskIndex = parentIdx;
                                    subtaskDialog.editSubtaskIndex = subIdx;
                                    let s = tasksModel[parentIdx].subtasks[subIdx];
                                    subtaskDialog.subtaskData = {
                                        title: s.title,
                                        description: s.description,
                                        owner: s.owner,
                                        dependencies: s.dependencies.slice(),
                                        hours: s.hours,
                                        hoursVerify: s.hoursVerify,
                                        status: s.status
                                    };
                                    subtaskDialog.open();
                                }
                            }
                        }
                        Button {
                            text: "Delete"
                            onClicked: {
                                if (!modelData.isSubtask) {
                                    let idx = tasksModel.findIndex(t => t.id === modelData.id);
                                    if (idx !== -1) tasksModel.splice(idx, 1);
                                } else {
                                    let parentIdx = tasksModel.findIndex(t => t.subtasks && t.subtasks.find(st => st.id === modelData.id));
                                    let subIdx = tasksModel[parentIdx].subtasks.findIndex(st => st.id === modelData.id);
                                    if (parentIdx !== -1 && subIdx !== -1) tasksModel[parentIdx].subtasks.splice(subIdx, 1);
                                }
                            }
                        }
                        Button {
                            text: "Add Subtask"
                            visible: !modelData.isSubtask
                            onClicked: {
                                subtaskDialog.editMode = false;
                                subtaskDialog.parentTaskIndex = tasksModel.findIndex(t => t.id === modelData.id);
                                subtaskDialog.editSubtaskIndex = -1;
                                subtaskDialog.subtaskData = {
                                    title: "",
                                    description: "",
                                    owner: null,
                                    dependencies: [],
                                    hours: 0,
                                    hoursVerify: 0,
                                    status: 0
                                };
                                subtaskDialog.open();
                            }
                        }
                    }
                }
            }

            // Add Task button
            Button {
                text: "Add Task"
                anchors.left: parent.left
                onClicked: {/* TODO: Open add task dialog */}
            }
        }
    }
    visible: projectDetailsPage.selectedTabIndex === 0

    // Placeholder for hierarchical task/subtask tree and controls
    // The full UI and logic will be implemented in the next steps
}
            }
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
// --- Add/Edit Task Dialog ---
Dialog {
    id: taskDialog
    modal: true
    property bool editMode: false
    property int editTaskIndex: -1
    property var taskData: null
    width: 480
    height: 520
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    Column {
        anchors.centerIn: parent
        spacing: 12
        Text { text: taskDialog.editMode ? "Edit Task" : "Add Task"; font.pixelSize: 22; font.bold: true }
        TextField { placeholderText: "Title"; text: taskDialog.taskData ? taskDialog.taskData.title : ""; onTextChanged: if (taskDialog.taskData) taskDialog.taskData.title = text }
        TextField { placeholderText: "Description"; text: taskDialog.taskData ? taskDialog.taskData.description : ""; onTextChanged: if (taskDialog.taskData) taskDialog.taskData.description = text }
        TextField { placeholderText: "Deadline (YYYY-MM-DD)"; text: taskDialog.taskData ? taskDialog.taskData.deadline : ""; onTextChanged: if (taskDialog.taskData) taskDialog.taskData.deadline = text }
        // Owners multi-select
        Rectangle {
            width: 400; height: 40; color: "#f8f9fa"; border.color: "#bbb"; border.width: 1; radius: 8
            property var selectedOwners: taskDialog.taskData ? taskDialog.taskData.owners : []
            ComboBox {
                id: ownerCombo
                width: parent.width
                model: userManager ? userManager.users : []
                textRole: "username"
                valueRole: "id"
                editable: false
                onActivated: {
                    let user = userManager.users[currentIndex];
                    let idx = parent.selectedOwners.indexOf(user.id);
                    if (idx === -1) parent.selectedOwners.push(user.id);
                    else parent.selectedOwners.splice(idx, 1);
                    ownerCombo.currentIndex = -1;
                }
                delegate: ItemDelegate {
                    width: parent.width
                    text: model.username
                    highlighted: parent.selectedOwners.indexOf(model.id) !== -1
                    onClicked: {
                        let idx = parent.selectedOwners.indexOf(model.id);
                        if (idx === -1) parent.selectedOwners.push(model.id);
                        else parent.selectedOwners.splice(idx, 1);
                        ownerCombo.currentIndex = -1;
                    }
                    background: Rectangle { color: parent.selectedOwners.indexOf(model.id) !== -1 ? "#e0f7fa" : "transparent" }
                }
            }
        }
        // Dependencies multi-select
        Rectangle {
            width: 400; height: 40; color: "#f8f9fa"; border.color: "#bbb"; border.width: 1; radius: 8
            property var selectedDeps: taskDialog.taskData ? taskDialog.taskData.dependencies : []
            ComboBox {
                id: depCombo
                width: parent.width
                model: root.tasksModel
                textRole: "title"
                valueRole: "id"
                editable: false
                onActivated: {
                    let task = tasksModel[currentIndex];
                    let idx = parent.selectedDeps.indexOf(task.id);
                    if (idx === -1) parent.selectedDeps.push(task.id);
                    else parent.selectedDeps.splice(idx, 1);
                    depCombo.currentIndex = -1;
                }
                delegate: ItemDelegate {
                    width: parent.width
                    text: model.title
                    highlighted: parent.selectedDeps.indexOf(model.id) !== -1
                    onClicked: {
                        let idx = parent.selectedDeps.indexOf(model.id);
                        if (idx === -1) parent.selectedDeps.push(model.id);
                        else parent.selectedDeps.splice(idx, 1);
                        depCombo.currentIndex = -1;
                    }
                    background: Rectangle { color: parent.selectedDeps.indexOf(model.id) !== -1 ? "#e0f7fa" : "transparent" }
                }
            }
        }
        TextField { placeholderText: "Hours to complete"; text: taskDialog.taskData ? taskDialog.taskData.hours : ""; inputMethodHints: Qt.ImhDigitsOnly; onTextChanged: if (taskDialog.taskData) taskDialog.taskData.hours = parseInt(text) }
        TextField { placeholderText: "Hours to verify"; text: taskDialog.taskData ? taskDialog.taskData.hoursVerify : ""; inputMethodHints: Qt.ImhDigitsOnly; onTextChanged: if (taskDialog.taskData) taskDialog.taskData.hoursVerify = parseInt(text) }
        ComboBox { width: 180; model: ["not yet started", "in progress", "being tested", "complete"]; currentIndex: taskDialog.taskData ? taskDialog.taskData.status : 0; onCurrentIndexChanged: if (taskDialog.taskData) taskDialog.taskData.status = currentIndex }
        Row {
            spacing: 16
            Button { text: "Save"; onClicked: {/* TODO: Save logic */} }
            Button { text: "Cancel"; onClicked: taskDialog.close() }
        }
    }
}
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
                id: calendarWidget
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
                    rows: calendarWidget.weeks
                    width: parent.width
                    height: parent.height - 40
            
                    Repeater {
                        model: calendarWidget.weeks * 7
                        delegate: Item {
                            width: parent.width / 7
                            height: (parent.height) / calendarWidget.weeks
                            property int dayNum: index - calendarWidget.firstDayOfWeek + 1
                            visible: dayNum > 0 && dayNum <= calendarWidget.daysInMonth
                            Rectangle {
                                width: parent.width
                                height: parent.height
                                color: (dayNum === calendarPage.calendarCurrentMonth.getDate() &&
                                        calendarPage.calendarCurrentMonth.getMonth() === calendarWidget.month &&
                                        calendarPage.calendarCurrentMonth.getFullYear() === calendarWidget.year)
                                    ? "#e0f7fa"
                                    : (Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(calendarWidget.year, calendarWidget.month, dayNum), "yyyy-MM-dd") ? "#e0f7fa" : "transparent")
                                border.color: (Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(calendarWidget.year, calendarWidget.month, dayNum), "yyyy-MM-dd")) ? "#2255aa" : "transparent"
                                border.width: (Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(calendarWidget.year, calendarWidget.month, dayNum), "yyyy-MM-dd")) ? 2 : 0
                                radius: 8
                                MouseArea {
                                    anchors.fill: parent
                                    enabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        calendarPage.calendarSelectedDate = new Date(calendarWidget.year, calendarWidget.month, dayNum)
                                    }
                                }
                                Text {
                                    anchors.centerIn: parent
                                    text: dayNum
                                    color: "#2255aa"
                                    font.pixelSize: 18
                                    font.bold: Qt.formatDate(calendarPage.calendarSelectedDate, "yyyy-MM-dd") === Qt.formatDate(new Date(calendarWidget.year, calendarWidget.month, dayNum), "yyyy-MM-dd")
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
                anchors.top: calendarWidget.bottom
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
                anchors.top: calendarWidget.bottom
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
 
    // --- All other code remains commented out below ---
    /*
    <rest of original file remains commented out>
    */

}
