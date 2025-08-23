from PySide6.QtCore import QObject, Signal, Property

class DashboardManager(QObject):
    projectsChanged = Signal()
    tasksChanged = Signal()
    messagesChanged = Signal()

    def __init__(self):
        super().__init__()
        self._projects = []
        self._tasks = []
        self._messages = []

    def getProjects(self):
        return self._projects

    def setProjects(self, value):
        if value is None:
            value = []
        self._projects = value
        self.projectsChanged.emit()

    def getTasks(self):
        return self._tasks

    def setTasks(self, value):
        if value is None:
            value = []
        self._tasks = value
        self.tasksChanged.emit()

    def getMessages(self):
        return self._messages

    def setMessages(self, value):
        if value is None:
            value = []
        self._messages = value
        self.messagesChanged.emit()

    projects = Property(list, getProjects, setProjects, notify=projectsChanged)
    tasks = Property(list, getTasks, setTasks, notify=tasksChanged)
    messages = Property(list, getMessages, setMessages, notify=messagesChanged)
# main.py - PySide6 QML migration entry point
# -------------------------------------------
# QML frontend, Python backend integration

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QObject, Slot, Signal, Property
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from db import authenticate_user, get_user_projects, get_user_tasks, get_user_messages

class AuthManager(QObject):
    loginResult = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self._user = None

    @Slot(str, str)
    def login(self, username, password):
        user = authenticate_user(username, password)
        if user:
            self._user = user
            self.loginResult.emit(True, "Login successful")
        else:
            self.loginResult.emit(False, "Invalid username or password")

    @Property(object)
    def user(self):
        return self._user

# get_user_projects, get_user_tasks, get_user_messages are now imported above

class DashboardManager(QObject):
    projectsChanged = Signal()
    tasksChanged = Signal()
    messagesChanged = Signal()

    def __init__(self):
        super().__init__()
        self._projects = []
        self._tasks = []
        self._messages = []

    @Slot(int)
    def loadProjects(self, user_id):
        projects, _ = get_user_projects(user_id)
        self._projects = [self._project_to_dict(p) for p in projects]
        self.projectsChanged.emit()

    @Slot(int)
    def loadTasks(self, user_id):
        tasks = get_user_tasks(user_id)
        self._tasks = [self._task_to_dict(t) for t in tasks]
        self.tasksChanged.emit()

    @Slot(int)
    def loadMessages(self, user_id):
        messages = get_user_messages(user_id)
        self._messages = [self._message_to_dict(m) for m in messages]
        self.messagesChanged.emit()

    @Slot(int, int, str)
    def sendMessage(self, sender_id, recipient_id, content):
        from db import create_message
        result = create_message(sender_id, recipient_id, content)
        # Optionally reload messages for sender after sending
        self.loadMessages(sender_id)

    @Property(object, notify=projectsChanged)
    def projects(self):
        return self._projects

    @Property(object, notify=tasksChanged)
    def tasks(self):
        return self._tasks

    @Property(object, notify=messagesChanged)
    def messages(self):
        return self._messages

    def _project_to_dict(self, p):
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "deadline": p.deadline,
        }

    def _task_to_dict(self, t):
        return {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "due_date": str(t.due_date) if t.due_date else "",
        }

    def _message_to_dict(self, m):
        return {
            "id": m.id,
            "content": m.content,
            "timestamp": str(m.timestamp),
            "read": m.read,
        }

class ProjectManager(QObject):
    projectCreated = Signal(bool, str)
    projectDetailLoaded = Signal(object)
    subtaskDetailLoaded = Signal(object)
    ganttDataLoaded = Signal(object)
    calendarDataLoaded = Signal(object)

    @Slot(str, str, str, int)
    def createProject(self, name, description, deadline, owner_id):
        from db import create_project
        result = create_project(name, description, owner_id, [], deadline)
        if result:
            self.projectCreated.emit(True, "Project created successfully")
        else:
            self.projectCreated.emit(False, "Failed to create project")

    @Slot(int)
    def loadGanttData(self, project_id):
        from db import get_project_by_id
        project = get_project_by_id(project_id)
        if project:
            tasks = []
            for t in getattr(project, "tasks", []):
                # Use due_date as end, estimate start as due_date - hours (if available)
                end = t.due_date
                duration = t.hours if hasattr(t, "hours") and t.hours else 1
                start = None
                if end and duration:
                    from datetime import timedelta
                    start = end - timedelta(hours=duration)
                tasks.append({
                    "id": t.id,
                    "title": t.title,
                    "start": str(start) if start else "",
                    "end": str(end) if end else "",
                    "duration": duration,
                })
            self.ganttDataLoaded.emit(tasks)
        else:
            self.ganttDataLoaded.emit([])

    @Slot(int)
    def loadCalendarData(self, project_id):
        from db import get_project_by_id
        project = get_project_by_id(project_id)
        if project:
            events = []
            for t in getattr(project, "tasks", []):
                events.append({
                    "id": t.id,
                    "title": t.title,
                    "due_date": str(t.due_date) if t.due_date else "",
                })
            self.calendarDataLoaded.emit(events)
        else:
            self.calendarDataLoaded.emit([])

    @Slot(int, int)
    def loadProjectDetail(self, project_id, user_id):
        from db import get_project_by_id
        project = get_project_by_id(project_id, user_id)
        if project:
            # Convert project and its tasks to dict for QML
            tasks = []
            for t in getattr(project, "tasks", []):
                tasks.append({
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "due_date": str(t.due_date) if t.due_date else "",
                    "description": t.description,
                })
            detail = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "deadline": project.deadline,
                "owner": getattr(project.owner, "username", ""),
                "tasks": tasks,
            }
            self.projectDetailLoaded.emit(detail)
        else:
            self.projectDetailLoaded.emit(None)

    @Slot(int)
    def loadSubtaskDetail(self, subtask_id):
        from db import get_subtask_by_id
        subtask = get_subtask_by_id(subtask_id)
        if subtask:
            detail = {
                "id": subtask.id,
                "title": subtask.title,
                "description": subtask.description,
                "status": subtask.status,
                "due_date": str(subtask.due_date) if subtask.due_date else "",
                "assigned_to": getattr(subtask.assignee, "username", ""),
                "category": subtask.category,
            }
            self.subtaskDetailLoaded.emit(detail)
        else:
            self.subtaskDetailLoaded.emit(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Expose AuthManager, DashboardManager, and ProjectManager to QML
    auth_manager = AuthManager()
    dashboard_manager = DashboardManager()
    project_manager = ProjectManager()
    engine.rootContext().setContextProperty("AuthManager", auth_manager)
    engine.rootContext().setContextProperty("DashboardManager", dashboard_manager)
    engine.rootContext().setContextProperty("ProjectManager", project_manager)

    # Load the QML UI
    qml_file = QUrl.fromLocalFile("Draft_2/app/qml/Main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
