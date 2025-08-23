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
            }
            property string loginError: ""
            Connections {
                target: AuthManager
                function onLoginResult(success, message) {
                    if (success) {
                        loginError = ""
                        // Load projects and tasks for the user before navigating
                        if (AuthManager.user && AuthManager.user.id) {
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
            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                TabBar {
                    id: mainTabBar
                    Layout.fillWidth: true
                    currentIndex: parent.currentTab
                    onCurrentIndexChanged: parent.currentTab = currentIndex
                    TabButton { text: "Dashboard" }
                    TabButton { text: "Calendar" }
                    TabButton { text: "Members" }
                    TabButton { text: "Event Log" }
                }

                Loader {
                    id: dashboardTabLoader
                    active: parent.currentTab === 0
                    sourceComponent: dashboardTabContent
                }
                Loader {
                    id: calendarTabLoader
                    active: parent.currentTab === 1
                    sourceComponent: calendarTabContent
                }
                Loader {
                    id: membersTabLoader
                    active: parent.currentTab === 2
                    sourceComponent: membersTabContent
                }
                Loader {
                    id: eventLogTabLoader
                    active: parent.currentTab === 3
                    sourceComponent: eventLogTabContent
                }
            }
        }
    }

    // --- Dashboard Tab Content ---
    Component {
        id: dashboardTabContent
        Item {
            RowLayout {
                anchors.fill: parent
                spacing: 32

                // Column 1: Projects
                ColumnLayout {
                    Layout.preferredWidth: parent.width / 3
                    Label {
                        text: "Projects"
                        font.pixelSize: 18
                        Layout.alignment: Qt.AlignHCenter
                    }
                    ListView {
                        id: projectListView
                        width: parent.width / 3 * 0.9
                        height: 160
                        model: DashboardManager.projects ? DashboardManager.projects : []
                        delegate: Rectangle {
                            width: projectListView.width
                            height: 40
                            color: "#f5f5f5"
                            border.color: "#cccccc"
                            radius: 4
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 10
                                Text { text: model.name; font.bold: true }
                                Text { text: " | " + model.status }
                                Button {
                                    text: "Open"
                                    onClicked: {
                                        ProjectManager.loadProject(model.id)
                                        stack.push(projectDetailPage)
                                    }
                                }
                            }
                        }
                        Component.onCompleted: {
                            console.log("DashboardManager.projects:", DashboardManager.projects, typeof DashboardManager.projects)
                        }
                    }
                    Button {
                        text: "Create Project"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: stack.push(projectCreationPage)
                    }
                }

                // Column 2: Subtasks (4 categories, 4 rows)
                ColumnLayout {
                    Layout.preferredWidth: parent.width / 3
                    Label {
                        text: "My Subtasks"
                        font.pixelSize: 18
                        Layout.alignment: Qt.AlignHCenter
                    }
                    // Four categories
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
                                model: DashboardManager.tasks ? DashboardManager.tasks : []
                                // TODO: Filtering by category must be handled in Python or with a QML ListModel
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
                                                ProjectManager.loadTask(model.id)
                                                stack.push(subtaskDetailPage)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Column 3: Messages
                ColumnLayout {
                    Layout.preferredWidth: parent.width / 3
                    Label {
                        text: "Messages"
                        font.pixelSize: 18
                        Layout.alignment: Qt.AlignHCenter
                    }
                    ListView {
                        id: messageListView
                        width: parent.width / 3 * 0.9
                        height: 160
                        model: DashboardManager.messages ? DashboardManager.messages : []
                        delegate: Rectangle {
                            width: messageListView.width
                            height: 32
                            color: "#fffde7"
                            border.color: "#ffe082"
                            radius: 4
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 10
                                Text { text: model.sender + ": " + model.content }
                            }
                        }
                        Component.onCompleted: {
                            console.log("DashboardManager.messages:", DashboardManager.messages, typeof DashboardManager.messages)
                        }
                    }
                    Button {
                        text: "Send Message"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: stack.push(messagingPage)
                    }
                    Button {
                        text: "Refresh"
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: DashboardManager.loadMessages(AuthManager.user ? AuthManager.user.id : 0)
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
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 16

                Label { text: "Create Project"; font.pixelSize: 22; Layout.alignment: Qt.AlignHCenter }
                TextField { id: projName; placeholderText: "Project Name"; Layout.fillWidth: true }
                TextField { id: projDesc; placeholderText: "Description"; Layout.fillWidth: true }
                TextField { id: projDeadline; placeholderText: "Deadline (YYYY-MM-DD)"; Layout.fillWidth: true }
                Button {
                    text: "Create"
                    Layout.fillWidth: true
                    onClicked: {
                        ProjectManager.createProject(
                            projName.text,
                            projDesc.text,
                            projDeadline.text,
                            AuthManager.user ? AuthManager.user.id : 0
                        )
                    }
                }
                property string createStatus: ""
                Connections {
                    target: ProjectManager
                    function onProjectCreated(success, message) {
                        createStatus = message
                        if (success) {
                            projName.text = ""
                            projDesc.text = ""
                            projDeadline.text = ""
                            // Optionally, navigate back to dashboard or refresh project list
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

    // --- Project Detail Page ---
    Component {
        id: projectDetailPage
        Item {
            id: projectDetailRoot
            property var projectData: null

            ColumnLayout {
                anchors.centerIn: parent
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
            }
        }
    }

    // --- Event Log Tab ---
    Component {
        id: eventLogTabContent
        Item {
            anchors.fill: parent
            Label {
                text: "Event Log (placeholder)"
                anchors.centerIn: parent
            }
        }
    }
}