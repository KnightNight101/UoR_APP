import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

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
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20
                scale: loginScale
            
                // Logo at the top
                // Logo removed
            
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
                        AuthManager.login(username.text, password.text)
                    }
                }
                // Scaling/zoom controls for accessibility
                // Zoom controls removed; now only available in the settings page
            }
            property real loginScale: 1.0
            property string loginError: ""
            Connections {
                target: AuthManager
                function onLoginResult(success, message) {
                    if (success) {
                        loginError = ""
                        // Load projects and tasks for the user before navigating
                        if (AuthManager.user && AuthManager.user.id) {
                            console.log("DEBUG: After login, AuthManager.user =", AuthManager.user, "id =", AuthManager.user ? AuthManager.user.id : "undefined")
                            DashboardManager.loadProjects(AuthManager.user.id)
                            DashboardManager.loadTasks(AuthManager.user.id)
                            DashboardManager.loadMessages(AuthManager.user.id)
                        }
                        stack.push(dashboardPage)
                    } else {
                        loginError = message
                    }
                }
            }
            Label {
                text: loginError
                color: "red"
                visible: loginError.length > 0
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }

    Component {
        id: dashboardPage
        Item {
            property int currentTab: 0
            // Move TabBar to the top of the dashboard page
            TabBar {
                id: mainTabBar
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                currentIndex: currentTab
                onCurrentIndexChanged: {
                    currentTab = currentIndex
                    var tabNames = ["Dashboard", "Calendar", "Members", "Event Log"]
                    var tabName = tabNames[currentIndex] !== undefined ? tabNames[currentIndex] : "Unknown"
                    DashboardManager.logTabSwitch(tabName)
                    if (tabName === "Event Log") {
                        DashboardManager.loadEventLog(AuthManager.user ? AuthManager.user.id : 0)
                    }
                }
                TabButton { text: "Dashboard" }
                TabButton { text: "Calendar" }
                TabButton { text: "Members" }
                TabButton { text: "Event Log" }
            }

            Item {
                anchors.fill: parent
                // Use an inner Item to center the dashboard content responsively
                Item {
                    id: dashboardCenter
                    anchors.centerIn: parent
                    width: Math.min(parent.width * 0.95, 1200)
                    height: Math.min(parent.height * 0.95, 800)
                    Loader {
                        id: dashboardTabLoader
                        anchors.fill: parent
                        active: currentTab === 0
                        sourceComponent: dashboardTabContent
                    }
                    Loader {
                        id: calendarTabLoader
                        anchors.fill: parent
                        active: currentTab === 1
                        sourceComponent: calendarTabContent
                    }
                    Loader {
                        id: membersTabLoader
                        anchors.fill: parent
                        active: currentTab === 2
                        sourceComponent: membersTabContent
                    }
                    Loader {
                        id: eventLogTabLoader
                        anchors.fill: parent
                        active: currentTab === 3
                        sourceComponent: eventLogTabContent
                    }
                }
            }
        }
    }

    // --- Dashboard Tab Content ---
    Component {
        id: dashboardTabContent
        Item {
            anchors.fill: parent
            width: parent.width
            height: parent.height
            // Use RowLayout directly for 3 columns
            RowLayout {
                anchors.fill: parent
                spacing: 32

                // Column 1: Projects
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Label {
                        text: "Projects"
                        font.pixelSize: 20
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Button {
                        text: "Refresh Projects & Tasks"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: {
                            if (AuthManager.user && AuthManager.user.id) {
                                DashboardManager.loadProjects(AuthManager.user.id)
                                DashboardManager.loadTasks(AuthManager.user.id)
                            }
                        }
                    }
                    Button {
                        text: "Add Project"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: stack.push(projectCreationPage)
                    }
                    ListView {
                        id: projectListView
                        width: parent.width / 3 * 0.9
                        height: 160
                        model: DashboardManager && DashboardManager.projects ? DashboardManager.projects : []
                        delegate: Text {
                            text: model.name
                            font.pixelSize: 18
                            font.bold: true
                            color: "#333"
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            width: projectListView.width
                            height: 32
                        }
                        Component.onCompleted: {
                            console.log("DashboardManager.projects:", DashboardManager.projects, typeof DashboardManager.projects)
                        }
                    }
                }

                // Column 2: Subtasks (4 categories, drag-and-drop)
                ColumnLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "My Subtasks"
                        font.pixelSize: 20
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    // Four categories, drag-and-drop support (placeholder for now)
                    Repeater {
                        model: [
                            { label: "Important and Urgent", key: "important_urgent" },
                            { label: "Urgent", key: "urgent" },
                            { label: "Important", key: "important" },
                            { label: "Other", key: "other" }
                        ]
                        delegate: ColumnLayout {
                            Label { text: modelData.label; font.bold: true }
                            ListView {
                                width: parent.width * 0.9
                                height: 36
                                model: DashboardManager && DashboardManager.tasksByCategory ? DashboardManager.tasksByCategory[modelData.key] || [] : []
                                interactive: true
                                /* dragDropMode removed: not supported in QML ListView */
                                /* Drag-and-drop handled by DropArea below */
                                delegate: Rectangle {
                                    width: parent.width
                                    height: 32
                                    color: "#e3f2fd"
                                    border.color: "#90caf9"
                                    radius: 4
                                    Row {
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 10
                                        Text { text: model.title }
                                        Text { text: " (" + model.projectName + ")" }
                                        Text { text: model.status }
                                        Button {
                                            text: "Details"
                                            onClicked: {
                                                ProjectManager.loadTaskDetail(model.id)
                                                stack.push(taskDetailPage)
                                            }
                                        }
                                    }
                                }
                            }
                            DropArea {
                                Layout.alignment: Qt.AlignTop
                                onDropped: {
                                    if (drop && drop.source && drop.source.model && drop.source.model.id !== undefined) {
                                        ProjectManager.updateSubtaskCategory(drop.source.model.id, modelData.key)
                                        DashboardManager.loadTasks(AuthManager.user ? AuthManager.user.id : 0)
                                    }
                                }
                            }
                        }
                    }
                    Button {
                        text: "Add Subtask"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: stack.push(subtaskDetailPage)
                    }
                }

                // Column 3: Messages
                ColumnLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Messages"
                        font.pixelSize: 20
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Button {
                        text: "Send Message"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: stack.push(messagingPage)
                    }
                    ListView {
                        id: messageListView
                        width: parent.width / 3 * 0.9
                        height: 160
                        model: DashboardManager && DashboardManager.messages ? DashboardManager.messages : []
                        delegate: Rectangle {
                            width: messageListView.width
                            height: 32
                            color: "#fffde7"
                            border.color: "#ffe082"
                            radius: 4
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 10
                                Text { text: (model.sender ? model.sender + ": " : "") + model.content }
                            }
                        }
                        Component.onCompleted: {
                            console.log("DashboardManager.messages:", DashboardManager.messages, typeof DashboardManager.messages)
                        }
                    }
                }
            }
        }
    }

    // --- Project Creation Page ---
    Component {
        id: projectCreationPage
        Item {
            anchors.fill: parent
            property string createStatus: ""
            ColumnLayout {
                anchors.centerIn: parent
                anchors.margins: 32
                spacing: 16

                Label { text: "Create Project"; font.pixelSize: 22; Layout.alignment: Qt.AlignHCenter }
                TextField { id: projName; placeholderText: "Project Name"; Layout.fillWidth: true }
                TextField { id: projDesc; placeholderText: "Description"; Layout.fillWidth: true }
                TextField { id: projDeadline; placeholderText: "Deadline (YYYY-MM-DD)"; Layout.fillWidth: true }
                Button {
                    text: "Create"
                    Layout.fillWidth: true
                    onClicked: {
                        console.log("DEBUG: Creating project with AuthManager.user =", AuthManager.user, "id =", AuthManager.userId)
                        ProjectManager.createProject(
                            projName.text,
                            projDesc.text,
                            projDeadline.text,
                            AuthManager.userId
                        )
                    }
                }
                Connections {
                    target: ProjectManager
                    function onProjectCreated(success, message) {
                        createStatus = message
                        if (success) {
                            projName.text = ""
                            projDesc.text = ""
                            projDeadline.text = ""
                            if (AuthManager.user && AuthManager.user.id) {
                                DashboardManager.loadProjects(AuthManager.user.id)
                            }
                            stack.pop()
                        }
                    }
                }
                Label {
                    text: createStatus
                    color: createStatus.indexOf("success") >= 0 ? "green" : "red"
                    visible: createStatus.length > 0
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }

    // --- User Settings Page ---
    Component {
        id: userSettingsPage
        Item {
            id: userSettingsRoot

            ColumnLayout {
                anchors.centerIn: parent
                anchors.margins: 32
                spacing: 16

                Label {
                    text: "User Settings"
                    font.pixelSize: 22
                    Layout.alignment: Qt.AlignHCenter
                }
                Label {
                    text: AuthManager.user ? "Username: " + AuthManager.user.username : ""
                }
                // Add more user info fields as needed
                Button {
                    text: "Back"
                    onClicked: stack.pop()
                }
            }
        }
    }

    // Add User/Settings button to app bar
    ToolBar {
        id: appToolBar
        visible: stack.currentItem === dashboardPage
        anchors.top: parent.top
        anchors.right: parent.right
        height: 40
        z: 1
        RowLayout {
            anchors.right: parent.right
            spacing: 8
            ToolButton {
                text: "User/Settings"
                onClicked: stack.push(userSettingsPage)
            }
        }
    }

    // --- Messaging Page ---
    Component {
        id: messagingPage
        Item {
            id: messagingRoot

            ColumnLayout {
                anchors.centerIn: parent
                anchors.margins: 32
                spacing: 16

                Label {
                    text: "Messaging"
                    font.pixelSize: 22
                    Layout.alignment: Qt.AlignHCenter
                }
                ListView {
                    width: parent.width * 0.9
                    height: 200
                    model: DashboardManager.messages
                    delegate: Rectangle {
                        width: parent.width
                        height: 32
                        color: model.read ? "#f0f0f0" : "#fffde7"
                        border.color: "#ffe082"
                        radius: 3
                        RowLayout {
                            anchors.fill: parent
                            spacing: 8
                            Label { text: model.content }
                            Label { text: model.timestamp }
                        }
                    }
                }
                RowLayout {
                    spacing: 8
                    TextField {
                        id: messageInput
                        placeholderText: "Type a message"
                        Layout.fillWidth: true
                    }
                    Button {
                        text: "Send"
                        onClicked: {
                            // Example: send to user id 1 (replace with real recipient)
                            DashboardManager.sendMessage(AuthManager.user ? AuthManager.user.id : 0, 1, messageInput.text)
                            messageInput.text = ""
                        }
                    }
                }
                Button {
                    text: "Back"
                    onClicked: stack.pop()
                }
            }
        }
    }

    // Add Messaging button to app bar
    ToolBar {
        id: messagingToolBar
        visible: stack.currentItem === dashboardPage
        anchors.top: parent.top
        anchors.right: appToolBar.left
        height: 40
        z: 1
        RowLayout {
            anchors.right: parent.right
            spacing: 8
            ToolButton {
                text: "Messaging"
                onClicked: stack.push(messagingPage)
            }
        }
    }

    // --- Task/Subtask Detail Page ---
    Component {
        id: taskDetailPage
        Item {
            id: taskDetailRoot
            property var taskData: null
            ColumnLayout {
                anchors.centerIn: parent
                anchors.margins: 32
                spacing: 16
                Label {
                    text: taskData ? taskData.title : "Loading..."
                    font.pixelSize: 22
                    Layout.alignment: Qt.AlignHCenter
                }
                Label {
                    text: taskData ? "Status: " + taskData.status : ""
                    visible: taskData !== null
                }
                Label {
                    text: taskData ? "Due: " + taskData.due_date : ""
                    visible: taskData !== null && !!taskData.due_date
                }
                Label {
                    text: taskData ? "Assigned to: " + taskData.assigned_to : ""
                    visible: taskData !== null && !!taskData.assigned_to
                }
                Label {
                    text: taskData ? taskData.description : ""
                    visible: taskData !== null && !!taskData.description
                }
                Button {
                    text: "Back"
                    onClicked: stack.pop()
                }
            }
            Connections {
                target: ProjectManager
                function onTaskDetailLoaded(detail) {
                    taskDetailRoot.taskData = detail
                }
            }
        }
    }

    // --- Project Detail Page ---
    Component {
        id: projectDetailPage
        Item {
            id: projectDetailRoot
            property var projectData: null

            ColumnLayout {
                anchors.centerIn: parent
                anchors.margins: 32
                spacing: 16

                Label {
                    text: projectData ? projectData.name : "Loading..."
                    font.pixelSize: 22
                    Layout.alignment: Qt.AlignHCenter
                }
                Label {
                    text: projectData ? "Owner: " + projectData.owner : ""
                    visible: projectData !== null
                }
                Label {
                    text: projectData ? "Deadline: " + projectData.deadline : ""
                    visible: projectData !== null && !!projectData.deadline
                }
                Label {
                    text: projectData ? projectData.description : ""
                    visible: projectData !== null && !!projectData.description
                }
                Label {
                    text: "Tasks:"
                    font.bold: true
                    visible: projectData !== null && projectData.tasks && projectData.tasks.length > 0
                }
                ListView {
                    width: parent.width * 0.8
                    height: 120
                    model: projectData ? projectData.tasks : []
                    delegate: Rectangle {
                        width: parent.width
                        height: 36
                        color: "#e0f7fa"
                        border.color: "#00bcd4"
                        radius: 3
                        RowLayout {
                            anchors.fill: parent
                            spacing: 8
                            Label { text: model.title; font.bold: true }
                            Label { text: model.status }
                            Label { text: model.due_date ? "Due: " + model.due_date : "" }
                            Button {
                                text: "Subtask Details"
                                onClicked: {
                                    subtaskDetailPage.subtaskData = null
                                    ProjectManager.loadSubtaskDetail(model.id)
                                    stack.push(subtaskDetailPage)
                                }
                            }
                        }
                    }
                }
                Button {
                    text: "View Gantt Chart"
                    onClicked: {
                        ganttChartPage.ganttData = []
                        ProjectManager.loadGanttData(projectData ? projectData.id : 0)
                        stack.push(ganttChartPage)
                    }
                }
                Button {
                    text: "View Calendar"
                    onClicked: {
                        calendarPage.calendarData = []
                        ProjectManager.loadCalendarData(projectData ? projectData.id : 0)
                        stack.push(calendarPage)
                    }
                }
                Button {
                    text: "Back"
                    onClicked: stack.pop()
                }
            }
            Connections {
                target: ProjectManager
                function onProjectDetailLoaded(detail) {
                    projectDetailRoot.projectData = detail
                }
            }
        }
    }

    // --- Calendar Tab ---
    Component {
        id: calendarTabContent
        Item {
            anchors.fill: parent
            Label {
                text: "Calendar (placeholder)"
                anchors.centerIn: parent
                anchors.margins: 32
            }
        }
    }

    // --- Members Tab ---
    Component {
        id: membersTabContent
        Item {
            anchors.fill: parent
            Label {
                text: "Members & Users (placeholder)"
                anchors.centerIn: parent
                anchors.margins: 32
            }
        }
    }

    // --- Event Log Tab ---
    Component {
        id: eventLogTabContent
        Item {
            anchors.fill: parent
            ColumnLayout {
                anchors.centerIn: parent
                anchors.margins: 32
                spacing: 8
                Label {
                    text: "Event Log"
                    font.pixelSize: 20
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                ListView {
                    width: parent.width * 0.95
                    height: parent.height * 0.8
                    model: DashboardManager.eventLog ? DashboardManager.eventLog : []
                    delegate: Rectangle {
                        width: parent.width
                        height: 32
                        color: "#f3e5f5"
                        border.color: "#ab47bc"
                        radius: 4
                        Row {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 10
                            Text { text: model.timestamp }
                            Text { text: model.description }
                        }
                    }
                }
                Button {
                    text: "Refresh"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: DashboardManager.loadEventLog(AuthManager.user ? AuthManager.user.id : 0)
                }
            }
        }
    }
}