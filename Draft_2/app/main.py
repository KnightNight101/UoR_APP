import datetime
import traceback

def log_event(event):
    """Append event messages to the event log with timestamp."""
    LOG_FILE = "event_log.txt"
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event}\n")

def log_error(error_msg):
    """Append error messages to the event log and print to stderr."""
    LOG_FILE = "event_log.txt"
    timestamp = datetime.datetime.now().isoformat()
    full_msg = f"[ERROR] [{timestamp}] {error_msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")
    print(full_msg)

from PySide6.QtCore import QObject, Signal, Property

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
            log_event(f"User '{username}' logged in")
            self.loginResult.emit(True, "Login successful")
        else:
            log_event(f"Failed login attempt for user '{username}'")
            self.loginResult.emit(False, "Invalid username or password")

    @Property(object)
    def user(self):
        return self._user

    @Property(int)
    def userId(self):
        if self._user and hasattr(self._user, "id"):
            # If self._user is a SQLAlchemy model instance, id is a value; if it's a class, it's a Column
            user_id = getattr(self._user, "id", 0)
            if hasattr(user_id, "__call__"):
                # Defensive: if id is a callable (Column), return 0
                return 0
            try:
                return int(user_id)
            except Exception:
                return 0
        return 0

# get_user_projects, get_user_tasks, get_user_messages are now imported above

class DashboardManager(QObject):
    projectsChanged = Signal()
    tasksChanged = Signal()
    messagesChanged = Signal()
    eventLogChanged = Signal()

    def __init__(self):
        super().__init__()
        self._projects = []
        self._tasks = []
        self._messages = []
        self._event_log = []

    @Slot(int)
    def loadProjects(self, user_id):
        try:
            projects, _ = get_user_projects(user_id)
            print(f"[DEBUG] loadProjects: user_id={user_id}, projects_found={len(projects)}")
            for p in projects:
                print(f"[DEBUG] Project loaded: id={p.id}, name={p.name}, owner_id={p.owner_id}")
            self._projects = [self._project_to_dict(p) for p in projects]
            print(f"[DEBUG] self._projects after load: {self._projects}")
            log_event(f"Loaded projects for user_id={user_id}, count={len(projects)}")
            self.projectsChanged.emit()
        except Exception as e:
            log_error(f"Error loading projects for user_id={user_id}: {e}\n{traceback.format_exc()}")

    @Slot(int)
    def loadTasks(self, user_id):
        tasks = get_user_tasks(user_id)
        try:
            self._tasks = [self._task_to_dict(t) for t in tasks]
            log_event(f"Loaded tasks for user_id={user_id}")
            self.tasksChanged.emit()
        except Exception as e:
            log_error(f"Error loading tasks for user_id={user_id}: {e}\n{traceback.format_exc()}")

    @Slot(int)
    def loadMessages(self, user_id):
        messages = get_user_messages(user_id)
        try:
            self._messages = [self._message_to_dict(m) for m in messages]
            log_event(f"Loaded messages for user_id={user_id}")
            self.messagesChanged.emit()
        except Exception as e:
            log_error(f"Error loading messages for user_id={user_id}: {e}\n{traceback.format_exc()}")

    @Slot(int, int, str)
    def sendMessage(self, sender_id, recipient_id, content):
        from db import create_message
        result = create_message(sender_id, recipient_id, content)
        log_event(f"User {sender_id} sent message to {recipient_id}: '{content}'")
        # Optionally reload messages for sender after sending
        self.loadMessages(sender_id)

    @Slot(str)
    def logTabSwitch(self, tab_name):
        log_event(f"Switched to tab: {tab_name}")

    @Slot(int)
    def loadEventLog(self, user_id):
        try:
            with open("event_log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Parse lines into dicts with timestamp and description
            parsed = []
            for line in lines:
                if line.startswith("[") and "]" in line:
                    ts_end = line.find("]")
                    timestamp = line[1:ts_end]
                    description = line[ts_end+2:].strip()
                    parsed.append({"timestamp": timestamp, "description": description})
            self._event_log = parsed[-200:]  # Show last 200 events
            self.eventLogChanged.emit()
        except Exception as e:
            log_error(f"Error loading event log: {e}")
            self._event_log = []
            self.eventLogChanged.emit()

    @Property(list, notify=projectsChanged)
    def projects(self):
        return self._projects if self._projects else []

    @Property(list, notify=tasksChanged)
    def tasks(self):
        return self._tasks if self._tasks else []

    @Property(list, notify=messagesChanged)
    def messages(self):
        return self._messages if self._messages else []

    def _tasksByCategory_notify(self):
        self.tasksChanged.emit()

    @Property(list, notify=tasksChanged)
    def tasksByCategory(self):
        # Returns a list of dicts: [{key: category_key, tasks: [tasks]}]
        categories = ["important_urgent", "urgent", "important", "other"]
        result = []
        for key in categories:
            filtered = [t for t in self._tasks if t.get("category", "other") == key]
            result.append({"key": key, "tasks": filtered})
        return result

    @Property(list, notify=eventLogChanged)
    def eventLog(self):
        return self._event_log if self._event_log else []

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
            "category": getattr(t, "category", "other"),
            "projectName": getattr(t, "projectName", ""),
        }

    def _message_to_dict(self, m):
        return {
            "id": m.id,
            "content": m.content,
            "timestamp": str(m.timestamp),
            "read": m.read,
            "sender": getattr(m, "sender", ""),
        }

class ProjectManager(QObject):
    projectCreated = Signal(bool, str)
    projectDetailLoaded = Signal(object)
    subtaskDetailLoaded = Signal(object)
    ganttDataLoaded = Signal(object)
    calendarDataLoaded = Signal(object)
    taskDetailLoaded = Signal(object)

    @Slot(int)
    def loadTaskDetail(self, task_id):
        from db import get_task_by_id
        task = get_task_by_id(task_id)
        if task:
            detail = {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "due_date": str(task.due_date) if getattr(task, "due_date", None) not in (None, "") else "",
                "description": task.description,
                "assigned_to": getattr(task, "assigned_to", ""),
                "category": getattr(task, "category", "other"),
                "project_id": getattr(task, "project_id", None),
            }
            self.taskDetailLoaded.emit(detail)
        else:
            self.taskDetailLoaded.emit(None)

    @Slot(str, str, str, int)
    def createProject(self, name, description, deadline, owner_id):
        from db import create_project
        result = create_project(name, description, owner_id, [], deadline)
        if result:
            log_event(f"Project '{name}' created by user_id={owner_id}")
            self.projectCreated.emit(True, "Project created successfully")
        else:
            log_event(f"Failed to create project '{name}' by user_id={owner_id}")
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
                "due_date": str(subtask.due_date) if getattr(subtask, "due_date", None) not in (None, "") else "",
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
