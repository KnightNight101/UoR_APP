# import datetime
# import traceback
# 
import datetime

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
from PySide6.QtCore import QObject, Signal, Slot, Property

class EventLogEntry(QObject):
    def __init__(self, timestamp, description):
        super().__init__()
        self._timestamp = timestamp
        self._description = description

    @Property(str)
    def timestamp(self):
        return self._timestamp

    @Property(str)
    def description(self):
        return self._description

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
# class ProjectManager(QObject):
#     projectCreated = Signal(bool, str)
#     projectDetailLoaded = Signal(object)
#     subtaskDetailLoaded = Signal(object)
#     ganttDataLoaded = Signal(object)
#     calendarDataLoaded = Signal(object)
#     taskDetailLoaded = Signal(object)
#     membersChanged = Signal()
#     leaderChanged = Signal()
#     filterByMember = Signal(int)
# 
#     def __init__(self):
#         super().__init__()
#         self._members = []
#         self._leader_id = None
# 
#     @Slot(int)
#     def loadProjectMembers(self, project_id):
#         """Load members for a project and emit membersChanged."""
#         try:
#             from db import get_project_members
#             self._members = get_project_members(project_id)
#             self.membersChanged.emit()
#         except Exception as e:
# 
#     @Property(list, notify=membersChanged)
#     def members(self):
#         return [
#             {
#                 "user_id": getattr(m, "user_id", None),
#                 "username": getattr(getattr(m, "user", None), "username", ""),
#                 "role": getattr(m, "role", ""),
#             }
#             for m in self._members
#         ] if self._members else []
# 
#     @Slot(int, int, int, str)
#     def addProjectMember(self, project_id, acting_user_id, new_member_id, role):
#         """Add a member to a project (acting_user_id is the user performing the action)."""
#         try:
#             from db import add_project_member
#             add_project_member(project_id, acting_user_id, new_member_id, role)
#             self.loadProjectMembers(project_id)
#         except Exception as e:
# 
#     @Slot(int, int)
#     def assignProjectLeader(self, project_id, user_id):
#         """Assign/change the leader for a project."""
#         try:
#             from db import update_project_leader
#             update_project_leader(project_id, user_id)
#             self.leaderChanged.emit()
#             self.loadProjectMembers(project_id)
#         except Exception as e:
# 
#     @Slot(int)
#     def filterInfoByMember(self, user_id):
#         """Emit signal to filter all info by member (for QML hover)."""
#         self.filterByMember.emit(user_id)
# 
#     @Slot(int, str, str)
#     def updateSubtaskCategory(self, subtask_id, from_category, to_category):
#         """
#         Update the category of a subtask and log the move event.
#         """
#         try:
#             from db import update_subtask_category
#             update_subtask_category(subtask_id, to_category)
#         except Exception as e:
# 
#     @Slot(int)
#     def loadTaskDetail(self, task_id):
#         from db import get_task_by_id
#         task = get_task_by_id(task_id)
#         if task:
#             detail = {
#                 "id": task.id,
#                 "title": task.title,
#                 "status": task.status,
#                 "due_date": str(task.due_date) if getattr(task, "due_date", None) not in (None, "") else "",
#                 "description": task.description,
#                 "assigned_to": getattr(task, "assigned_to", ""),
#                 "category": getattr(task, "category", "other"),
#                 "project_id": getattr(task, "project_id", None),
#             }
#             self.taskDetailLoaded.emit(detail)
#         else:
#             self.taskDetailLoaded.emit(None)
# 
#     @Slot(str, str, str, int)
#     def createProject(self, name, description, deadline, owner_id):
#         from db import create_project
#         result = create_project(name, description, owner_id, [], deadline)
#         if result:
#             self.projectCreated.emit(True, "Project created successfully")
#         else:
#             self.projectCreated.emit(False, "Failed to create project")
# 
#     @Slot(int, int)
#     def loadGanttData(self, project_id, filter_user_id=-1):
#         """
#         Loads all tasks and subtasks for the project, including dependencies, durations, and assigned_to.
#         If filter_user_id >= 0, only include tasks/subtasks assigned to that user.
#         """
#         from db import get_project_by_id, get_subtasks
#         import json
#         project = get_project_by_id(project_id)
#         if project:
#             items = []
#             # Tasks
#             for t in getattr(project, "tasks", []):
#                 if filter_user_id >= 0 and getattr(t, "assigned_to", None) != filter_user_id:
#                     continue
#                 end = t.due_date
#                 duration = t.hours if hasattr(t, "hours") and t.hours else 1
#                 start = None
#                 if end and duration:
#                     from datetime import timedelta
#                     start = end - timedelta(hours=duration)
#                 # Parse dependencies
#                 deps = []
#                 if getattr(t, "dependencies", None):
#                     try:
#                         deps = json.loads(t.dependencies)
#                     except Exception:
#                         deps = []
#                 items.append({
#                     "type": "task",
#                     "id": t.id,
#                     "title": t.title,
#                     "start": str(start) if start else "",
#                     "end": str(end) if end else "",
#                     "duration": duration,
#                     "assigned_to": getattr(t, "assigned_to", None),
#                     "dependencies": deps,
#                 })
#                 # Subtasks
#                 for st in getattr(t, "subtasks", []):
#                     if filter_user_id >= 0 and getattr(st, "assigned_to", None) != filter_user_id:
#                         continue
#                     st_end = st.due_date
#                     st_duration = st.hours if hasattr(st, "hours") and st.hours else 1
#                     st_start = None
#                     if st_end and st_duration:
#                         from datetime import timedelta
#                         st_start = st_end - timedelta(hours=st_duration)
#                     st_deps = []
#                     if getattr(st, "dependencies", None):
#                         try:
#                             st_deps = json.loads(st.dependencies)
#                         except Exception:
#                             st_deps = []
#                     items.append({
#                         "type": "subtask",
#                         "id": st.id,
#                         "title": st.title,
#                         "start": str(st_start) if st_start else "",
#                         "end": str(st_end) if st_end else "",
#                         "duration": st_duration,
#                         "assigned_to": getattr(st, "assigned_to", None),
#                         "dependencies": st_deps,
#                         "parent_task_id": st.task_id,
#                     })
#             self.ganttDataLoaded.emit(items)
#         else:
#             self.ganttDataLoaded.emit([])
# 
#     @Slot(int, int)
#     def loadCalendarData(self, project_id, filter_user_id=-1):
#         """
#         Loads all deadlines, tasks, subtasks, public holidays, and personal time off for all team members.
#         If filter_user_id >= 0, only include items for that user.
#         """
#         from db import get_project_by_id
#         import json
#         project = get_project_by_id(project_id)
#         # Demo: static public holidays and time off
#         public_holidays = [
#             {"type": "holiday", "title": "New Year's Day", "date": "2025-01-01"},
#             {"type": "holiday", "title": "Good Friday", "date": "2025-04-18"},
#             {"type": "holiday", "title": "Christmas Day", "date": "2025-12-25"},
#         ]
#         personal_time_off = [
#             {"type": "pto", "user_id": 2, "title": "Alice PTO", "date": "2025-08-28"},
#             {"type": "pto", "user_id": 3, "title": "Bob PTO", "date": "2025-09-02"},
#         ]
#         if project:
#             events = []
#             # Tasks
#             for t in getattr(project, "tasks", []):
#                 if filter_user_id >= 0 and getattr(t, "assigned_to", None) != filter_user_id:
#                     continue
#                 events.append({
#                     "type": "task",
#                     "id": t.id,
#                     "title": t.title,
#                     "due_date": str(t.due_date) if t.due_date else "",
#                     "assigned_to": getattr(t, "assigned_to", None),
#                 })
#                 # Subtasks
#                 for st in getattr(t, "subtasks", []):
#                     if filter_user_id >= 0 and getattr(st, "assigned_to", None) != filter_user_id:
#                         continue
#                     events.append({
#                         "type": "subtask",
#                         "id": st.id,
#                         "title": st.title,
#                         "due_date": str(st.due_date) if st.due_date else "",
#                         "assigned_to": getattr(st, "assigned_to", None),
#                         "parent_task_id": st.task_id,
#                     })
#             # Add public holidays and PTO (filter PTO by user if needed)
#             events.extend(public_holidays)
#             if filter_user_id >= 0:
#                 events.extend([pto for pto in personal_time_off if pto["user_id"] == filter_user_id])
#             else:
#                 events.extend(personal_time_off)
#             self.calendarDataLoaded.emit(events)
#         else:
#             self.calendarDataLoaded.emit([])
# 
#     @Slot(int, int)
#     def loadProjectDetail(self, project_id, user_id):
#         from db import get_project_by_id
#         project = get_project_by_id(project_id, user_id)
#         if project:
#             # Convert project and its tasks to dict for QML
#             tasks = []
#             for t in getattr(project, "tasks", []):
#                 tasks.append({
#                     "id": t.id,
#                     "title": t.title,
#                     "status": t.status,
#                     "due_date": str(t.due_date) if t.due_date else "",
#                     "description": t.description,
#                 })
#             detail = {
#                 "id": project.id,
#                 "name": project.name,
#                 "description": project.description,
#                 "deadline": project.deadline,
#                 "owner": getattr(project.owner, "username", ""),
#                 "tasks": tasks,
#             }
#             self.projectDetailLoaded.emit(detail)
#         else:
#             self.projectDetailLoaded.emit(None)
# 
#     @Slot(int)
#     def loadSubtaskDetail(self, subtask_id):
#         from db import get_subtask_by_id
#         subtask = get_subtask_by_id(subtask_id)
#         if subtask:
#             detail = {
#                 "id": subtask.id,
#                 "title": subtask.title,
#                 "description": subtask.description,
#                 "status": subtask.status,
#                 "due_date": str(subtask.due_date) if getattr(subtask, "due_date", None) not in (None, "") else "",
#                 "assigned_to": getattr(subtask.assignee, "username", ""),
#                 "category": subtask.category,
#             }
#             self.subtaskDetailLoaded.emit(detail)
#         else:
#             self.subtaskDetailLoaded.emit(None)
#     @Slot(int, str, str, int, str, float, object)
#     def addTask(self, project_id, title, description, assigned_to, due_date, hours, dependencies):
#         """Add a new task to a project, auto-assign if not set, create 'check progress' subtask."""
#         try:
#             from db import create_task
#             import datetime, json
#             if not assigned_to:
#                 assigned_to = self._get_current_user_id()
#             due_dt = datetime.datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
#             dep_list = dependencies if isinstance(dependencies, list) else json.loads(dependencies) if dependencies else []
#             result = create_task(
#                 project_id=project_id,
#                 title=title,
#                 description=description,
#                 assigned_to=assigned_to,
#                 due_date=due_dt,
#                 hours=hours,
#                 dependencies=dep_list
#             )
#             self.loadProjectDetail(project_id, assigned_to)
#         except Exception as e:
# 
#     @Slot(int, int, str, str, int, float, object)
#     def editTask(self, task_id, project_id, title, description, assigned_to, hours, dependencies):
#         """Edit an existing task."""
#         try:
#             from db import update_task
#             import json
#             dep_list = dependencies if isinstance(dependencies, list) else json.loads(dependencies) if dependencies else []
#             update_task(
#                 task_id=task_id,
#                 title=title,
#                 description=description,
#                 assigned_to=assigned_to,
#                 hours=hours,
#                 dependencies=dep_list
#             )
#             self.loadProjectDetail(project_id, assigned_to)
#         except Exception as e:
# 
#     @Slot(int, int)
#     def deleteTask(self, task_id, project_id):
#         """Delete a task from a project."""
#         try:
#             from db import delete_task
#             delete_task(task_id)
#             self.loadProjectDetail(project_id, self._get_current_user_id())
#         except Exception as e:
# 
#     @Slot(int, int, str, str, int, float, object)
#     def addSubtask(self, task_id, project_id, title, description, assigned_to, hours, dependencies):
#         """Add a subtask to a task, auto-assign if not set, update 'check progress' deadline."""
#         try:
#             from db import create_subtask
#             import datetime, json
#             if not assigned_to:
#                 assigned_to = self._get_current_user_id()
#             dep_list = dependencies if isinstance(dependencies, list) else json.loads(dependencies) if dependencies else []
#             create_subtask(
#                 task_id=task_id,
#                 title=title,
#                 description=description,
#                 assigned_to=assigned_to,
#                 hours=hours,
#                 dependencies=dep_list
#             )
#             self.loadProjectDetail(project_id, assigned_to)
#         except Exception as e:
# 
#     @Slot(int, int)
#     def deleteSubtask(self, subtask_id, project_id):
#         """Delete a subtask from a project."""
#         try:
#             from db import delete_subtask
#             delete_subtask(subtask_id)
#             self.loadProjectDetail(project_id, self._get_current_user_id())
#         except Exception as e:
# 
#     def _get_current_user_id(self):
#         try:
#             from PySide6.QtQml import QQmlEngine
#             ctx = QQmlEngine.contextForObject(self)
#             if ctx and ctx.contextProperty("AuthManager"):
#                 auth = ctx.contextProperty("AuthManager")
#                 return getattr(auth, "userId", 0)
#         except Exception:
#             pass
#         return 0
# 
# Entry point for launching the PySide6 application and loading QML
if __name__ == "__main__":
    # Create the Qt application
    app = QApplication(sys.argv)

    # Create the QML application engine
    engine = QQmlApplicationEngine()

    # Load the main QML file
    # Expose log_event to QML
    event_log_bridge = EventLogBridge()
    log_event_bridge = LogEventBridge(event_log_bridge)
    engine.rootContext().setContextProperty("log_event", log_event_bridge)
     
    qml_file = QUrl.fromLocalFile("Draft_2/app/qml/Main.qml")
    engine.load(qml_file)

    # Exit if QML failed to load
    if not engine.rootObjects():
        sys.exit(-1)
    # Start the Qt event loop
    sys.exit(app.exec())
