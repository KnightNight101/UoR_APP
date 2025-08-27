# import datetime
# import traceback
# 
import datetime
from PySide6.QtCore import QObject, Signal, Slot, Property

def log_event(event):
    """Append event messages to the event log with timestamp and print to terminal."""
    LOG_FILE = "event_log.txt"
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] {event}")
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
# 
# from PySide6.QtCore import QObject, Signal, Property
# 
# # main.py - PySide6 QML migration entry point
# # -------------------------------------------
# # QML frontend, Python backend integration
# 
# Import required modules for PySide6 application and QML engine
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
class UserManager(QObject):
    usersChanged = Signal()

    def __init__(self):
        super().__init__()
        self._users = []
        self.loadUsers()

    @Slot()
    def loadUsers(self):
        try:
            from db import get_all_users
            self._users = [self._user_to_dict(u) for u in get_all_users()]
            self.usersChanged.emit()
        except Exception:
            self._users = []
            self.usersChanged.emit()

    @Property(list, notify=usersChanged)
    def users(self):
        return self._users

    def _user_to_dict(self, u):
        return {
            "id": getattr(u, "id", 0),
            "username": getattr(u, "username", ""),
        }
from PySide6.QtCore import QObject, Signal, Slot, Property

class LoginManager(QObject):
    loginResult = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        # Placeholder: in-memory user store
        self._users = {
            "alice": "password123",
            "bob": "securepass",
            "admin": "admin"
        }

    @Slot(str, str)
    def verify_credentials(self, username, password):
        """Check credentials and emit loginResult signal."""
        if username in self._users and self._users[username] == password:
            self.loginResult.emit(True, "Login successful")
        else:
            self.loginResult.emit(False, "Invalid username or password")

class EventLogEntry(QObject):
    timestampChanged = Signal()
    descriptionChanged = Signal()

    def __init__(self, timestamp, description):
        super().__init__()
        self._timestamp = timestamp
        self._description = description

    @Property(str, notify=timestampChanged)
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        if self._timestamp != value:
            self._timestamp = value
            self.timestampChanged.emit()

    @Property(str, notify=descriptionChanged)
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if self._description != value:
            self._description = value
            self.descriptionChanged.emit()

class EventLogBridge(QObject):
    eventLogChanged = Signal()

    def __init__(self):
        super().__init__()
        self._event_log = []
        self.load_log()

    @Slot()
    def load_log(self):
        try:
            with open("event_log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            parsed = []
            for line in lines:
                if line.startswith("[") and "]" in line:
                    ts_end = line.find("]")
                    timestamp = line[1:ts_end]
                    description = line[ts_end+2:].strip()
                    parsed.append(EventLogEntry(timestamp, description))
            self._event_log = list(reversed(parsed[-200:]))  # Most recent at top
            self.eventLogChanged.emit()
        except Exception:
            self._event_log = []
            self.eventLogChanged.emit()

    @Property(list, notify=eventLogChanged)
    def eventLog(self):
        return self._event_log
class LogEventBridge(QObject):
    eventLogChanged = Signal()

    def __init__(self, event_log_bridge):
        super().__init__()
        self._event_log_bridge = event_log_bridge
        # Connect the underlying bridge's signal to this one
        self._event_log_bridge.eventLogChanged.connect(self.eventLogChanged)

    @Slot(str)
    def log_event(self, event):
        log_event(event)
        # Reload the log and emit eventLogChanged so QML updates immediately
        if hasattr(self._event_log_bridge, "load_log"):
            self._event_log_bridge.load_log()

    @Slot()
    def load_log(self):
        if hasattr(self._event_log_bridge, "load_log"):
            self._event_log_bridge.load_log()

    @Property(list, notify=eventLogChanged)
    def eventLog(self):
        return self._event_log_bridge.eventLog
from PySide6.QtCore import QUrl
# 
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from db import authenticate_user, get_user_projects, get_user_tasks, get_user_messages
# 
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
            self.userIdChanged.emit()
            log_event(f"User '{username}' logged in")
            self.loginResult.emit(True, "Login successful")
        else:
            log_event(f"Failed login attempt for user '{username}'")
            self.loginResult.emit(False, "Invalid username or password")

    @Property(object)
    def user(self):
        return self._user

    userIdChanged = Signal()

    @Property(int, notify=userIdChanged)
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
class DashboardManager(QObject):
    projectsChanged = Signal()
    eisenhowerMatrixStateChanged = Signal()

    def __init__(self):
        super().__init__()
        self._projects = []
        self._eisenhower_matrix_state = {}

    @Slot(int)
    def loadProjects(self, user_id):
        try:
            projects, _ = get_user_projects(user_id)
            print(f"[DEBUG] loadProjects: user_id={user_id}, projects_found={len(projects)}")
            for p in projects:
                print(f"[DEBUG] Project loaded: id={getattr(p, 'id', None)}, name={getattr(p, 'name', None)}")
            self._projects = [self._project_to_dict(p) for p in projects]
            self.projectsChanged.emit()
        except Exception as e:
            print(f"[DEBUG] loadProjects exception: {e}")
            self._projects = []
            self.projectsChanged.emit()

    @Slot(int, int)
    def loadEisenhowerMatrixState(self, user_id, project_id):
        """Fetch Eisenhower matrix state for a user/project and notify QML."""
        try:
            from db import get_eisenhower_matrix_state
            state_obj = get_eisenhower_matrix_state(project_id, user_id)
            import json
            if state_obj and state_obj.state_json:
                self._eisenhower_matrix_state = json.loads(state_obj.state_json)
            else:
                self._eisenhower_matrix_state = {}
            self.eisenhowerMatrixStateChanged.emit()
        except Exception as e:
            print(f"[DEBUG] loadEisenhowerMatrixState exception: {e}")
            self._eisenhower_matrix_state = {}
            self.eisenhowerMatrixStateChanged.emit()

    @Slot(int, int, 'QVariant')
    def setEisenhowerMatrixState(self, user_id, project_id, state_json):
        """Set Eisenhower matrix state for a user/project and notify QML."""
        try:
            from db import set_eisenhower_matrix_state
            import json
            set_eisenhower_matrix_state(project_id, user_id, state_json)
            self._eisenhower_matrix_state = state_json if isinstance(state_json, dict) else json.loads(state_json)
            self.eisenhowerMatrixStateChanged.emit()
        except Exception as e:
            print(f"[DEBUG] setEisenhowerMatrixState exception: {e}")

    @Property('QVariant', notify=eisenhowerMatrixStateChanged)
    def eisenhowerMatrixState(self):
        return self._eisenhower_matrix_state

    def _projectsChanged(self):
        pass

    @Property(list, notify=projectsChanged)
    def projects(self):
        import copy
        fresh = [copy.deepcopy(p) for p in self._projects] if self._projects else []
        return fresh

    def _project_to_dict(self, p):
        def safe_str(val):
            try:
                return str(val)
            except Exception:
                return ""
        def safe_int(val):
            try:
                return int(val)
            except Exception:
                return 0
        return {
            "id": safe_int(getattr(p, "id", 0)),
            "name": safe_str(getattr(p, "name", "")),
            "description": safe_str(getattr(p, "description", "")),
            "deadline": safe_str(getattr(p, "deadline", "")),
        }
    @Slot(int, int, int, int, str, str)
    def recategorizeTaskOrSubtask(self, user_id, project_id, task_id, subtask_id, old_category, new_category):
        """
        Backend support for drag-and-drop recategorization of tasks/subtasks.
        Logs all changes as events with timestamps.
        """
        try:
            from db import update_subtask_category, update_task, log_structured_event
            import datetime
            # Only one of task_id or subtask_id should be set
            if subtask_id and subtask_id > 0:
                update_subtask_category(subtask_id, new_category)
                log_structured_event(
                    None,  # session will be created inside
                    event_type="recategorization",
                    user_id=user_id,
                    project_id=project_id,
                    task_id=task_id if task_id > 0 else None,
                    subtask_id=subtask_id,
                    old_category=old_category,
                    new_category=new_category,
                    reasoning="User drag-and-drop recategorization",
                    context_json=None
                )
            elif task_id and task_id > 0:
                update_task(task_id, category=new_category)
                log_structured_event(
                    None,
                    event_type="recategorization",
                    user_id=user_id,
                    project_id=project_id,
                    task_id=task_id,
                    subtask_id=None,
                    old_category=old_category,
                    new_category=new_category,
                    reasoning="User drag-and-drop recategorization",
                    context_json=None
                )
            # Optionally reload Eisenhower matrix state
            self.loadEisenhowerMatrixState(user_id, project_id)
        except Exception as e:
            print(f"[DEBUG] recategorizeTaskOrSubtask exception: {e}")

    @Slot(int, int, int, int)
    def suggestEisenhowerCategory(self, user_id, project_id, task_id, subtask_id):
        """
        Integrate TinyLlama LLM to suggest Eisenhower matrix categorization for a task/subtask.
        Uses event logs as context and logs LLM suggestions with reasoning.
        """
        try:
            import requests
            import json
            from db import get_event_logs, log_structured_event, update_subtask_category

            # Gather context: last 50 event logs for this project/user
            logs = get_event_logs(project_id=project_id, user_id=user_id, limit=50)
            context = [
                {
                    "timestamp": str(getattr(e, "timestamp", "")),
                    "event_type": getattr(e, "event_type", ""),
                    "old_category": getattr(e, "old_category", ""),
                    "new_category": getattr(e, "new_category", ""),
                    "reasoning": getattr(e, "reasoning", ""),
                    "task_id": getattr(e, "task_id", None),
                    "subtask_id": getattr(e, "subtask_id", None),
                }
                for e in logs
            ]
            # Prepare payload for LLM
            payload = {
                "user_id": user_id,
                "project_id": project_id,
                "task_id": task_id,
                "subtask_id": subtask_id,
                "context": context
            }
            # Call TinyLlama container (assume HTTP API at localhost:8000/suggest)
            response = requests.post("http://localhost:8000/suggest", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                suggested_category = result.get("suggested_category")
                reasoning = result.get("reasoning", "")
                # Apply suggestion to subtask if subtask_id is set
                if subtask_id and subtask_id > 0 and suggested_category:
                    update_subtask_category(subtask_id, suggested_category)
                # Log LLM suggestion event
                log_structured_event(
                    None,
                    event_type="llm_suggestion",
                    user_id=user_id,
                    project_id=project_id,
                    task_id=task_id if task_id > 0 else None,
                    subtask_id=subtask_id if subtask_id > 0 else None,
                    old_category=None,
                    new_category=suggested_category,
                    reasoning=reasoning,
                    context_json={"llm_response": result, "llm_payload": payload}
                )
                # Optionally reload Eisenhower matrix state
                self.loadEisenhowerMatrixState(user_id, project_id)
            else:
                print(f"[DEBUG] LLM API error: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[DEBUG] suggestEisenhowerCategory exception: {e}")

#
# # get_user_projects, get_user_tasks, get_user_messages are now imported above
# 
# class DashboardManager(QObject):
#     projectsChanged = Signal()
#     tasksChanged = Signal()
#     messagesChanged = Signal()
#     eventLogChanged = Signal()
# 
#     @Slot(str)
#     def logNavigation(self, page_name):
# 
#     def __init__(self):
#         super().__init__()
#         self._projects = []
#         self._tasks = []
#         self._messages = []
#         self._event_log = []
# 
#     @Slot(int)
#     def loadProjects(self, user_id):
#         print(f"[DEBUG] loadProjects slot called with user_id={user_id} (type={type(user_id)})")
#         try:
#             projects, _ = get_user_projects(user_id)
#             print(f"[DEBUG] loadProjects: user_id={user_id}, projects_found={len(projects)}")
#             for p in projects:
#                 print(f"[DEBUG] Project loaded: id={p.id}, name={p.name}, owner_id={p.owner_id}")
#             self._projects = [self._project_to_dict(p) for p in projects]
#             print(f"[DEBUG] self._projects after load: {self._projects}")
#             print("[DEBUG] Python: Emitting projectsChanged signal")
#             self.projectsChanged.emit()
#         except Exception as e:
# 
#     @Slot(int)
#     def loadTasks(self, user_id):
#         tasks = get_user_tasks(user_id)
#         try:
#             self._tasks = [self._task_to_dict(t) for t in tasks]
#             self.tasksChanged.emit()
#         except Exception as e:
# 
#     @Slot(int)
#     def loadMessages(self, user_id):
#         messages = get_user_messages(user_id)
#         try:
#             self._messages = [self._message_to_dict(m) for m in messages]
#             self.messagesChanged.emit()
#         except Exception as e:
# 
#     @Slot(int, int, str)
#     def sendMessage(self, sender_id, recipient_id, content):
#         from db import create_message
#         result = create_message(sender_id, recipient_id, content)
#         # Optionally reload messages for sender after sending
#         self.loadMessages(sender_id)
# 
#     @Slot(str)
#     def logTabSwitch(self, tab_name):
# 
#     @Slot(int)
#     def loadEventLog(self, user_id):
#         try:
#             with open("event_log.txt", "r", encoding="utf-8") as f:
#                 lines = f.readlines()
#             # Parse lines into dicts with timestamp and description
#             parsed = []
#             for line in lines:
#                 if line.startswith("[") and "]" in line:
#                     ts_end = line.find("]")
#                     timestamp = line[1:ts_end]
#                     description = line[ts_end+2:].strip()
#                     parsed.append({"timestamp": timestamp, "description": description})
#             self._event_log = parsed[-200:]  # Show last 200 events
#             self.eventLogChanged.emit()
#         except Exception as e:
#             self._event_log = []
#             self.eventLogChanged.emit()
# 
#     @Property(list, notify=projectsChanged)
#     def projects(self):
#         import copy
#         fresh = [copy.deepcopy(p) for p in self._projects] if self._projects else []
#         print(f"[DEBUG] DashboardManager.projects property accessed, returning {len(fresh)} projects")
#         return fresh
# 
#     @Property(list, notify=tasksChanged)
#     def tasks(self):
#         return self._tasks if self._tasks else []
# 
#     @Property(list, notify=messagesChanged)
#     def messages(self):
#         return self._messages if self._messages else []
# 
#     @Property(list, notify=tasksChanged)
#     def tasksByCategory(self):
#         # Returns a list of dicts: [{key: category_key, tasks: [tasks]}]
#         categories = ["important_urgent", "urgent", "important", "other"]
#         result = []
#         for key in categories:
#             filtered = [t for t in self._tasks if t.get("category", "other") == key]
#             result.append({"key": key, "tasks": filtered})
#         return result
# 
#     @Property(list, notify=eventLogChanged)
#     def eventLog(self):
#         return self._event_log if self._event_log else []
# 
#     def _project_to_dict(self, p):
#         # Defensive: always provide all fields expected by QML, even if empty
#         def safe_str(val):
#             try:
#                 return str(val)
#             except Exception:
#                 return ""
#         def safe_int(val):
#             try:
#                 return int(val)
#             except Exception:
#                 return 0
#         def member_to_dict(m):
#             return {
#                 "username": safe_str(getattr(getattr(m, "user", None), "username", "")),
#                 "user_id": safe_int(getattr(m, "user_id", 0)),
#                 "role": safe_str(getattr(m, "role", "")),
#             }
#         def leader_to_dict(l):
#             return {
#                 "username": safe_str(getattr(getattr(l, "user", None), "username", "")),
#                 "user_id": safe_int(getattr(l, "user_id", 0)),
#             }
#         def subtask_to_dict(st):
#             return {
#                 "title": safe_str(getattr(st, "title", "")),
#                 "id": safe_int(getattr(st, "id", 0)),
#                 "status": safe_str(getattr(st, "status", "")),
#                 "due_date": safe_str(getattr(st, "due_date", "")),
#                 "assigned_to": safe_str(getattr(st, "assigned_to", "")),
#             }
#         def task_to_dict(t):
#             return {
#                 "id": safe_int(getattr(t, "id", 0)),
#                 "title": safe_str(getattr(t, "title", "")),
#                 "status": safe_str(getattr(t, "status", "")),
#                 "due_date": safe_str(getattr(t, "due_date", "")),
#                 "description": safe_str(getattr(t, "description", "")),
#                 "subtasks": [subtask_to_dict(st) for st in getattr(t, "subtasks", [])] if hasattr(t, "subtasks") and t.subtasks else []
#             }
#         return {
#             "id": safe_int(getattr(p, "id", 0)),
#             "name": safe_str(getattr(p, "name", "")),
#             "description": safe_str(getattr(p, "description", "")),
#             "deadline": safe_str(getattr(p, "deadline", "")),
#             "owner": safe_str(getattr(getattr(p, "owner", None), "username", "")),
#             "members": [member_to_dict(m) for m in getattr(p, "members", [])] if hasattr(p, "members") and p.members else [],
#             "leaders": [leader_to_dict(l) for l in getattr(p, "leaders", [])] if hasattr(p, "leaders") and p.leaders else [],
#             "tasks": [task_to_dict(t) for t in getattr(p, "tasks", [])] if hasattr(p, "tasks") and p.tasks else []
#         }
# 
#     def _task_to_dict(self, t):
#         return {
#             "id": t.id,
#             "title": t.title,
#             "status": t.status,
#             "due_date": str(t.due_date) if t.due_date else "",
#             "category": getattr(t, "category", "other"),
#             "projectName": getattr(t, "projectName", ""),
#         }
# 
#     def _message_to_dict(self, m):
#         return {
#             "id": m.id,
#             "content": m.content,
#             "timestamp": str(m.timestamp),
#             "read": m.read,
#             "sender": getattr(m, "sender", ""),
#         }
# 
class ProjectManager(QObject):
    # Signals for QML integration (required by task)
    projectCreated = Signal(bool, str)
    projectDeleted = Signal(bool, str)
    projectTitleUpdated = Signal(bool, str)
    # Existing signals
    projectDetailLoaded = Signal(object)
    subtaskDetailLoaded = Signal(object)
    ganttDataLoaded = Signal(object)
    calendarDataLoaded = Signal(object)
    taskDetailLoaded = Signal(object)
    membersChanged = Signal()
    leaderChanged = Signal()
    filterByMember = Signal(int)

    def __init__(self):
        super().__init__()
        self._members = []
        self._leader_id = None
        # Placeholder/in-memory project list for demo/testing
        self._placeholder_mode = True  # Set to False to use real DB logic
        self._projects = []

    @Slot(int, int)
    def deleteProject(self, project_id, user_id):
        """
        Delete a project and log the deletion event.
        Emits projectDeleted signal (success, message).
        """
        from db import delete_project, get_project_by_id, get_user_by_id
        try:
            project = get_project_by_id(project_id)
            user = get_user_by_id(user_id)
            project_name = getattr(project, "name", str(project_id)) if project else str(project_id)
            username = getattr(user, "username", str(user_id)) if user else str(user_id)
            success, msg = delete_project(project_id, user_id)
            if success:
                log_event(f"Project '{project_name}' deleted by {username}.")
                self.projectDeleted.emit(True, f"Project '{project_name}' deleted.")
            else:
                self.projectDeleted.emit(False, msg or "Failed to delete project.")
        except Exception as e:
            log_error(f"Error deleting project: {e}")
            self.projectDeleted.emit(False, "Error deleting project.")

    @Slot(int)
    def loadProjectMembers(self, project_id):
        """Load members for a project and emit membersChanged."""
        try:
            from db import get_project_members
            self._members = get_project_members(project_id)
            self.membersChanged.emit()
        except Exception as e:
            pass

    @Property(list, notify=membersChanged)
    def members(self):
        return [
            {
                "user_id": getattr(m, "user_id", None),
                "username": getattr(getattr(m, "user", None), "username", ""),
                "role": getattr(m, "role", ""),
            }
            for m in self._members
        ] if self._members else []

    @Slot(int, int, int, str)
    def addProjectMember(self, project_id, acting_user_id, new_member_id, role):
        """Add a member to a project (acting_user_id is the user performing the action)."""
        try:
            from db import add_project_member
            add_project_member(project_id, acting_user_id, new_member_id, role)
            self.loadProjectMembers(project_id)
        except Exception as e:
            pass

    @Slot(int, int)
    def assignProjectLeader(self, project_id, user_id):
        """Assign/change the leader for a project."""
        try:
            from db import update_project_leader
            update_project_leader(project_id, user_id)
            self.leaderChanged.emit()
            self.loadProjectMembers(project_id)
        except Exception as e:
            pass

    @Slot(int)
    def filterInfoByMember(self, user_id):
        """Emit signal to filter all info by member (for QML hover)."""
        self.filterByMember.emit(user_id)

    @Slot(int, str, str)
    def updateSubtaskCategory(self, subtask_id, from_category, to_category):
        """
        Update the category of a subtask and log the move event.
        """
        try:
            from db import update_subtask_category
            update_subtask_category(subtask_id, to_category)
        except Exception as e:
            pass

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
            self.projectCreated.emit(True, "Project created successfully")
        else:
            self.projectCreated.emit(False, "Failed to create project")

    @Slot(int, int)
    def loadGanttData(self, project_id, filter_user_id=-1):
        """
        Loads all tasks and subtasks for the project, including dependencies, durations, and assigned_to.
        If filter_user_id >= 0, only include tasks/subtasks assigned to that user.
        """
        from db import get_project_by_id, get_subtasks
        import json
        project = get_project_by_id(project_id)
        if project:
            items = []
            # Tasks
            for t in getattr(project, "tasks", []):
                if filter_user_id >= 0 and getattr(t, "assigned_to", None) != filter_user_id:
                    continue
                end = t.due_date
                duration = t.hours if hasattr(t, "hours") and t.hours else 1
                start = None
                if end and duration:
                    from datetime import timedelta
                    start = end - timedelta(hours=duration)
                # Parse dependencies
                deps = []
                if getattr(t, "dependencies", None):
                    try:
                        deps = json.loads(t.dependencies)
                    except Exception:
                        deps = []
                items.append({
                    "type": "task",
                    "id": t.id,
                    "title": t.title,
                    "start": str(start) if start else "",
                    "end": str(end) if end else "",
                    "duration": duration,
                    "assigned_to": getattr(t, "assigned_to", None),
                    "dependencies": deps,
                })
                # Subtasks
                for st in getattr(t, "subtasks", []):
                    if filter_user_id >= 0 and getattr(st, "assigned_to", None) != filter_user_id:
                        continue
                    st_end = st.due_date
                    st_duration = st.hours if hasattr(st, "hours") and st.hours else 1
                    st_start = None
                    if st_end and st_duration:
                        from datetime import timedelta
                        st_start = st_end - timedelta(hours=st_duration)
                    st_deps = []
                    if getattr(st, "dependencies", None):
                        try:
                            st_deps = json.loads(st.dependencies)
                        except Exception:
                            st_deps = []
                    items.append({
                        "type": "subtask",
                        "id": st.id,
                        "title": st.title,
                        "start": str(st_start) if st_start else "",
                        "end": str(st_end) if st_end else "",
                        "duration": st_duration,
                        "assigned_to": getattr(st, "assigned_to", None),
                        "dependencies": st_deps,
                        "parent_task_id": st.task_id,
                    })
            self.ganttDataLoaded.emit(items)
        else:
            self.ganttDataLoaded.emit([])

    @Slot(int, int)
    def loadCalendarData(self, project_id, filter_user_id=-1):
        """
        Loads all deadlines, tasks, subtasks, public holidays, and personal time off for all team members.
        If filter_user_id >= 0, only include items for that user.
        """
        from db import get_project_by_id
        import json
        project = get_project_by_id(project_id)
        # Demo: static public holidays and time off
        public_holidays = [
            {"type": "holiday", "title": "New Year's Day", "date": "2025-01-01"},
            {"type": "holiday", "title": "Good Friday", "date": "2025-04-18"},
            {"type": "holiday", "title": "Christmas Day", "date": "2025-12-25"},
        ]
        personal_time_off = [
            {"type": "pto", "user_id": 2, "title": "Alice PTO", "date": "2025-08-28"},
            {"type": "pto", "user_id": 3, "title": "Bob PTO", "date": "2025-09-02"},
        ]
        if project:
            events = []
            # Tasks
            for t in getattr(project, "tasks", []):
                if filter_user_id >= 0 and getattr(t, "assigned_to", None) != filter_user_id:
                    continue
                events.append({
                    "type": "task",
                    "id": t.id,
                    "title": t.title,
                    "due_date": str(t.due_date) if t.due_date else "",
                    "assigned_to": getattr(t, "assigned_to", None),
                })
                # Subtasks
                for st in getattr(t, "subtasks", []):
                    if filter_user_id >= 0 and getattr(st, "assigned_to", None) != filter_user_id:
                        continue
                    events.append({
                        "type": "subtask",
                        "id": st.id,
                        "title": st.title,
                        "due_date": str(st.due_date) if st.due_date else "",
                        "assigned_to": getattr(st, "assigned_to", None),
                        "parent_task_id": st.task_id,
                    })
            # Add public holidays and PTO (filter PTO by user if needed)
            events.extend(public_holidays)
            if filter_user_id >= 0:
                events.extend([pto for pto in personal_time_off if pto["user_id"] == filter_user_id])
            else:
                events.extend(personal_time_off)
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

    @Slot(int, str, str, int, str, float, object)
    def addTask(self, project_id, title, description, assigned_to, due_date, hours, dependencies):
        """Add a new task to a project, auto-assign if not set, create 'check progress' subtask."""
        try:
            from db import create_task
            import datetime, json
            if not assigned_to:
                assigned_to = self._get_current_user_id()
            due_dt = datetime.datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
            dep_list = dependencies if isinstance(dependencies, list) else json.loads(dependencies) if dependencies else []
            result = create_task(
                project_id=project_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                due_date=due_dt,
                hours=hours,
                dependencies=dep_list
            )
            self.loadProjectDetail(project_id, assigned_to)
        except Exception as e:
            pass

    @Slot(int, int, str, str, int, float, object)
    def editTask(self, task_id, project_id, title, description, assigned_to, hours, dependencies):
        """Edit an existing task."""
        try:
            from db import update_task
            import json
            dep_list = dependencies if isinstance(dependencies, list) else json.loads(dependencies) if dependencies else []
            update_task(
                task_id=task_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                hours=hours,
                dependencies=dep_list
            )
            self.loadProjectDetail(project_id, assigned_to)
        except Exception as e:
            pass

    @Slot(int, int)
    def deleteTask(self, task_id, project_id):
        """Delete a task from a project."""
        try:
            from db import delete_task
            delete_task(task_id)
            self.loadProjectDetail(project_id, self._get_current_user_id())
        except Exception as e:
            pass

    @Slot(int, int, str, str, int, float, object)
    def addSubtask(self, task_id, project_id, title, description, assigned_to, hours, dependencies):
        """Add a subtask to a task, auto-assign if not set, update 'check progress' deadline."""
        try:
            from db import create_subtask
            import datetime, json
            if not assigned_to:
                assigned_to = self._get_current_user_id()
            dep_list = dependencies if isinstance(dependencies, list) else json.loads(dependencies) if dependencies else []
            create_subtask(
                task_id=task_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                hours=hours,
                dependencies=dep_list
            )
            self.loadProjectDetail(project_id, assigned_to)
        except Exception as e:
            pass

    @Slot(int, int)
    def deleteSubtask(self, subtask_id, project_id):
        """Delete a subtask from a project."""
        try:
            from db import delete_subtask
            delete_subtask(subtask_id)
            self.loadProjectDetail(project_id, self._get_current_user_id())
        except Exception as e:
            pass

    def _get_current_user_id(self):
        try:
            from PySide6.QtQml import QQmlEngine
            ctx = QQmlEngine.contextForObject(self)
            if ctx and ctx.contextProperty("AuthManager"):
                auth = ctx.contextProperty("AuthManager")
                return getattr(auth, "userId", 0)
        except Exception:
            pass
        return 0

    @Slot(int, int, str)
    def updateProjectTitle(self, project_id, user_id, new_title):
        """
        Update the project title (name) for a given project.
        Emits projectTitleUpdated signal (success, message).
        """
        try:
            from db import update_project
            updated_project, err = update_project(project_id, user_id, name=new_title)
            if updated_project:
                self.projectTitleUpdated.emit(True, "Project title updated successfully.")
            else:
                msg = err or "Failed to update project title."
                self.projectTitleUpdated.emit(False, msg)
        except Exception as e:
            from traceback import format_exc
            log_error(f"Error updating project title: {e}\n{format_exc()}")
            self.projectTitleUpdated.emit(False, "Error updating project title.")
# 
# Entry point for launching the PySide6 application and loading QML

import os
import threading
import time
import requests
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from db import SessionLocal, Project, Task

PROJECT_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../project_files"))

class ProjectFileManager:
    def __init__(self, root_dir=PROJECT_ROOT_DIR):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)
        self.projects = []
        self._load_projects()
        self._setup_directories_and_git()
        self._start_file_watchdog()

    def _load_projects(self):
        with SessionLocal() as session:
            self.projects = session.query(Project).all()

    def _setup_directories_and_git(self):
        for project in self.projects:
            project_dir = os.path.join(self.root_dir, f"project_{project.id}")
            os.makedirs(project_dir, exist_ok=True)
            # Init git repo if not exists
            try:
                Repo(project_dir)
            except (InvalidGitRepositoryError, NoSuchPathError):
                Repo.init(project_dir)
            # Create task subdirectories (not subtasks)
            for task in getattr(project, "tasks", []):
                task_dir = os.path.join(project_dir, f"task_{task.id}")
                os.makedirs(task_dir, exist_ok=True)

    def _start_file_watchdog(self):
        event_handler = ProjectFileChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.root_dir, recursive=True)
        observer_thread = threading.Thread(target=observer.start, daemon=True)
        observer_thread.start()

class ProjectFileChangeHandler(FileSystemEventHandler):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def on_modified(self, event):
        self._handle_event(event)

    def on_created(self, event):
        self._handle_event(event)

    def _handle_event(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        project_dir = self._find_project_dir(file_path)
        if project_dir:
            try:
                repo = Repo(project_dir)
                rel_path = os.path.relpath(file_path, project_dir)
                repo.index.add([rel_path])
                # Generate commit summary using LLM
                summary = self._get_llm_commit_summary(file_path)
                repo.index.commit(summary or "Auto-commit: file changed")
            except Exception as e:
                print(f"[VCS] Error handling file change: {e}")

    def _find_project_dir(self, file_path):
        # Find the nearest parent directory that matches a project directory
        abs_root = os.path.abspath(self.manager.root_dir)
        abs_path = os.path.abspath(file_path)
        if not abs_path.startswith(abs_root):
            return None
        parts = abs_path[len(abs_root):].strip(os.sep).split(os.sep)
        if parts:
            project_dir = os.path.join(abs_root, parts[0])
            if os.path.isdir(project_dir):
                return project_dir
        return None

    def _get_llm_commit_summary(self, file_path):
        # Placeholder: call LLM endpoint for commit summary
        try:
            resp = requests.post("http://localhost:8000/llm/commit_summary", json={"file_path": file_path}, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("summary", "")
        except Exception as e:
            print(f"[LLM] Commit summary error: {e}")
        return None

if __name__ == "__main__":
    # Start project file manager (creates dirs, sets up git, starts watcher)
    pfm = ProjectFileManager()

    # Create the Qt application
    app = QApplication(sys.argv)

    # Create the QML application engine
    engine = QQmlApplicationEngine()

    # Expose log_event to QML
    event_log_bridge = EventLogBridge()
    log_event_bridge = LogEventBridge(event_log_bridge)
    engine.rootContext().setContextProperty("log_event", log_event_bridge)

    # Expose AuthManager to QML
    auth_manager = AuthManager()
    engine.rootContext().setContextProperty("AuthManager", auth_manager)
    # Expose DashboardManager to QML
    dashboard_manager = DashboardManager()
    engine.rootContext().setContextProperty("dashboardManager", dashboard_manager)
    # Expose ProjectManager to QML
    project_manager = ProjectManager()
    engine.rootContext().setContextProperty("projectManager", project_manager)
    # Expose UserManager to QML
    user_manager = UserManager()
    engine.rootContext().setContextProperty("userManager", user_manager)

    # Expose LoginManager to QML
    login_manager = LoginManager()
    engine.rootContext().setContextProperty("loginManager", login_manager)

    qml_file = QUrl.fromLocalFile("Draft_2/app/qml/Main.qml")
    engine.load(qml_file)

    # Exit if QML failed to load
    if not engine.rootObjects():
        sys.exit(-1)
    # Start the Qt event loop
    sys.exit(app.exec())
