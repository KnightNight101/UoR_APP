import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QFormLayout, QMessageBox, QInputDialog, QComboBox, QDialog, QDialogButtonBox,
    QTabWidget, QGroupBox, QSlider, QSpinBox
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
import json
import os

# --- Gantt Chart Imports ---
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime

# --- Project Creation Page ---
class ProjectCreationPage(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        from datetime import datetime
        self.current_user = current_user
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(QLabel("Create New Project"))

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.start_date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.end_date_input = QLineEdit()
        form.addRow("Project Name:", self.name_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Start Date (YYYY-MM-DD):", self.start_date_input)
        form.addRow("End Date (YYYY-MM-DD):", self.end_date_input)

        # Team member selection
        self.member_list = QListWidget()
        self.member_list.setSelectionMode(QListWidget.MultiSelection)
        self.load_users()
        form.addRow("Select Team Members:", self.member_list)

        # Team leader selection (from selected members)
        self.leader_list = QListWidget()
        self.leader_list.setSelectionMode(QListWidget.MultiSelection)
        form.addRow("Assign Team Leaders:", self.leader_list)

        self.vlayout.addLayout(form)
        self.save_btn = QPushButton("Save")
        self.vlayout.addWidget(self.save_btn)
        self.setLayout(self.vlayout)

        # Update leader list when members change
        self.member_list.itemSelectionChanged.connect(self.update_leader_list)
        # Auto-assign creator as leader on save
        self.save_btn.clicked.connect(self.ensure_creator_is_leader)

    def load_users(self):
        self.member_list.clear()
        if db:
            with db.SessionLocal() as session:
                users = session.query(db.User).all()
                for user in users:
                    item = QListWidgetItem(f"{user.id}: {user.username}")
                    item.setData(32, user.id)  # 32 is Qt.UserRole
                    self.member_list.addItem(item)

    def update_leader_list(self):
        self.leader_list.clear()
        selected_items = self.member_list.selectedItems()
        for item in selected_items:
            if item is not None:
                leader_item = QListWidgetItem(item.text())
                leader_item.setData(32, item.data(32))  # 32 is Qt.UserRole
                self.leader_list.addItem(leader_item)
        # Auto-select creator if present
        if self.current_user:
            for i in range(self.leader_list.count()):
                leader_item = self.leader_list.item(i)
                if leader_item and str(self.current_user.id) in leader_item.text():
                    leader_item.setSelected(True)

    def ensure_creator_is_leader(self):
        # Ensure creator is in members and leaders
        if not self.current_user:
            QMessageBox.warning(self, "Error", "No current user context.")
            return

        creator_id = self.current_user.id
        creator_username = self.current_user.username

        # Ensure creator is in members and leaders
        member_ids = set()
        for i in range(self.member_list.count()):
            item = self.member_list.item(i)
            if item and item.isSelected():
                member_ids.add(item.data(32))
        if creator_id not in member_ids:
            # Add creator to member list if not present/selected
            item = QListWidgetItem(f"{creator_id}: {creator_username}")
            item.setData(32, creator_id)
            self.member_list.addItem(item)
            item.setSelected(True)
            member_ids.add(creator_id)

        # Update leader list to only include selected members
        self.update_leader_list()
        leader_ids = set()
        for i in range(self.leader_list.count()):
            item = self.leader_list.item(i)
            if item and item.isSelected():
                leader_ids.add(item.data(32))
        if creator_id not in leader_ids:
            # Add creator to leader list if not present/selected
            leader_item = QListWidgetItem(f"{creator_id}: {creator_username}")
            leader_item.setData(32, creator_id)
            self.leader_list.addItem(leader_item)
            leader_item.setSelected(True)
            leader_ids.add(creator_id)

        # Collect form data
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        start_date = self.start_date_input.text().strip()
        end_date = self.end_date_input.text().strip()

        # Validate required fields
        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name is required.")
            return

        # Prepare members list for db.create_project
        members = []
        for i in range(self.member_list.count()):
            item = self.member_list.item(i)
            if item and item.isSelected():
                uid = item.data(32)
                role = 'leader' if uid in leader_ids else 'member'
                members.append({'user_id': uid, 'role': role})

        # Use db.create_project
        if db:
            project = db.create_project(
                name=name,
                description=description,
                owner_id=creator_id,
                members=members
            )
            if project:
                # Optionally set start/end date if supported (not in schema, so log only)
                log_event(f"Project '{name}' created by {creator_username} (ID {creator_id}). Start: {start_date}, End: {end_date}. Members: {members}")
                QMessageBox.information(self, "Project Saved", f"Project '{name}' created successfully.")
                # Optionally clear form
                self.name_input.clear()
                self.desc_input.clear()
                self.start_date_input.clear()
                self.end_date_input.clear()
                self.member_list.clearSelection()
                self.leader_list.clearSelection()
            else:
                QMessageBox.warning(self, "Error", "Failed to create project in database.")
        else:
            QMessageBox.warning(self, "Error", "Database not available.")


# Placeholder import for database models/utilities
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
try:
    import db
except ImportError:
    db = None

LOG_FILE = "event_log.txt"

def log_event(event):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(event + "\n")

from PyQt5.QtGui import QPixmap

class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scale_factor = 1.7  # Match MainWindow default
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._base_font_size = self.font().pointSize()
        layout = QVBoxLayout()
        # --- Logo Placeholder ---
        logo_label = QLabel()
        try:
            pixmap = QPixmap("logo.png")
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(120, Qt.SmoothTransformation))
            else:
                logo_label.setText("[Logo Placeholder]")
        except Exception:
            logo_label.setText("[Logo Placeholder]")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        # --- End Logo Placeholder ---

        title = QLabel("Login")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        self.login_btn = QPushButton("Login")
        layout.addWidget(self.login_btn)
        self.setLayout(layout)
        self._apply_scale()

    def _apply_scale(self):
        def scale_widget(widget, factor):
            font = widget.font()
            font.setPointSizeF(self._base_font_size * factor)
            widget.setFont(font)
            for child in widget.findChildren(QWidget):
                try:
                    cfont = child.font()
                    cfont.setPointSizeF(self._base_font_size * factor)
                    child.setFont(cfont)
                except Exception:
                    pass
        scale_widget(self, self._scale_factor)

    def adjust_scale(self, delta=None, reset=False):
        if reset:
            self._scale_factor = 1.0
        elif delta is not None:
            if delta > 0:
                self._scale_factor = min(self._scale_factor + 0.1, self._max_scale)
            else:
                self._scale_factor = max(self._scale_factor - 0.1, self._min_scale)
        self._apply_scale()

class DashboardView(QWidget):
    def __init__(self, parent=None, user=None, main_window=None):
        super().__init__(parent)
        self.user = user
        self.main_window = main_window
        self.layout = QVBoxLayout()
        # --- Begin Project/Task Management widgets ---
        self.project_list = QListWidget()
        self.layout.addWidget(QLabel("Projects"))
        self.layout.addWidget(self.project_list)
        self.refresh_projects_btn = QPushButton("Refresh Projects")
        self.layout.addWidget(self.refresh_projects_btn)
        self.add_project_btn = QPushButton("Add Project")
        self.layout.addWidget(self.add_project_btn)
        self.task_list = QListWidget()
        self.layout.addWidget(QLabel("Tasks & Assigned Subtasks"))
        self.layout.addWidget(self.task_list)
        self.add_task_btn = QPushButton("Add Task")
        self.layout.addWidget(self.add_task_btn)
        # --- End Project/Task Management widgets ---

        self.setLayout(self.layout)
        self.refresh_projects_btn.clicked.connect(self.load_projects)
        self.add_project_btn.clicked.connect(self.navigate_to_project_creation)
        self.project_list.itemClicked.connect(self.handle_project_click)
        self.add_task_btn.clicked.connect(self.add_task)
        self.load_projects()

    def handle_project_click(self, item):
        # Get project details and navigate to detail page
        if db and self.user:
            # Try to get project by name (since only name is shown in list)
            project_name = item.text()
            projects, _ = db.get_user_projects(self.user.id)
            selected_project = None
            for project in projects:
                if getattr(project, "name", "") == project_name:
                    selected_project = project
                    break
            if selected_project and self.main_window:
                self.main_window.show_project_detail_page(selected_project)

    # Dashboard summary removed per UI simplification instructions.

    # --- Begin Project/Task Management logic (from ProjectTaskManagement) ---
    def load_projects(self):
        self.project_list.clear()
        if db and self.user:
            projects, _ = db.get_user_projects(self.user.id)
            for project in projects:
                self.project_list.addItem(f"{project.name}")

    def navigate_to_project_creation(self):
        if self.main_window:
            self.main_window.show_project_creation_page()

    def add_project(self):
        # Old dialog-based add_project, now unused
        pass

    def load_tasks(self, item):
        self.task_list.clear()
        if db and self.user:
            project_id = int(item.text().split(":")[0])
            tasks = db.get_tasks(project_id)
            for task in tasks:
                self.task_list.addItem(f"{task.id}: {task.title}")
            # Show assigned subtasks
            subtasks = []
            for task in tasks:
                if hasattr(db, "get_subtasks"):
                    try:
                        subs = db.get_subtasks(task.id)
                        for sub in subs:
                            if getattr(sub, "assigned_to", None) == self.user.id:
                                self.task_list.addItem(f"Subtask {sub.id}: {sub.title} (Task {task.title})")
                    except Exception:
                        pass

    def add_task(self):
        if db and self.user:
            current_project = self.project_list.currentItem()
            if not current_project:
                QMessageBox.warning(self, "No Project", "Select a project first.")
                return
            project_id = int(current_project.text().split(":")[0])
            title, ok = QInputDialog.getText(self, "Add Task", "Task Title:")
            if ok and title:
                from datetime import datetime
                task = db.create_task(
                    project_id=project_id,
                    title=title,
                    due_date=None  # No due_date input in this dialog, so pass None
                )
                if task:
                    log_event(f"Task '{title}' created in project {project_id} by user {self.user.username}")
                    self.load_tasks(current_project)
    # --- End Project/Task Management logic ---

# ProjectTaskManagement class removed; logic and widgets merged into DashboardView.

class UserFileManagement(QWidget):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.layout = QVBoxLayout()
        self.user_list = QListWidget()
        self.layout.addWidget(QLabel("Users"))
        self.layout.addWidget(self.user_list)

        # Add User and Edit User buttons (role-restricted)
        self.add_user_btn = QPushButton("Add User")
        self.edit_user_btn = QPushButton("Edit User Info")
        if self._can_manage_users():
            self.layout.addWidget(self.add_user_btn)
            self.layout.addWidget(self.edit_user_btn)
        self.refresh_users_btn = QPushButton("Refresh Users")
        self.layout.addWidget(self.refresh_users_btn)
        self.file_list = QListWidget()
        self.layout.addWidget(QLabel("Files"))
        self.layout.addWidget(self.file_list)
        self.refresh_files_btn = QPushButton("Refresh Files")
        self.layout.addWidget(self.refresh_files_btn)
        self.setLayout(self.layout)

        self.refresh_users_btn.clicked.connect(self.load_users)
        self.refresh_files_btn.clicked.connect(self.load_files)
        if self._can_manage_users():
            self.add_user_btn.clicked.connect(self.show_add_user_dialog)
            self.edit_user_btn.clicked.connect(self.show_edit_user_dialog)
        self.load_users()
        self.load_files()

    def _can_manage_users(self):
        # Only allow for admin, IT, or superuser roles
        if not self.user:
            return False
        role = getattr(self.user, "role", "").lower()
        return role in ["admin", "it", "superuser"]

    def load_users(self):
        self.user_list.clear()
        if db:
            # List all users (admin only in real app)
            with db.SessionLocal() as session:
                users = session.query(db.User).all()
                for user in users:
                    self.user_list.addItem(f"{user.id}: {user.username}")
    
    def show_add_user_dialog(self):
        # Dialog for onboarding a new user
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Add User")
        form = QFormLayout()
        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        role_input = QLineEdit()
        form.addRow("Username:", username_input)
        form.addRow("Password:", password_input)
        form.addRow("Role:", role_input)
        # Use a QWidget to hold the form
        form_widget = QWidget()
        form_widget.setLayout(form)
        dialog.layout().addWidget(form_widget, 0, 0, 1, dialog.layout().columnCount())
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = dialog.exec_()
        if result == QMessageBox.Ok:
            username = username_input.text().strip()
            password = password_input.text().strip()
            role = role_input.text().strip()
            if not username or not password or not role:
                QMessageBox.warning(self, "Validation Error", "All fields are required.")
                return
            if db:
                with db.SessionLocal() as session:
                    # Check if user exists
                    existing = session.query(db.User).filter_by(username=username).first()
                    if existing:
                        QMessageBox.warning(self, "Error", "Username already exists.")
                        return
                    new_user = db.User(username=username, password=password, role=role)
                    session.add(new_user)
                    session.commit()
                    QMessageBox.information(self, "Success", f"User '{username}' added.")
                    self.load_users()

    def show_edit_user_dialog(self):
        # Dialog for editing selected user info
        selected = self.user_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Select a user to edit.")
            return
        user_id = int(selected.text().split(":")[0])
        if db:
            with db.SessionLocal() as session:
                user = session.query(db.User).filter_by(id=user_id).first()
                if not user:
                    QMessageBox.warning(self, "Error", "User not found.")
                    return
                dialog = QMessageBox(self)
                dialog.setWindowTitle("Edit User Info")
                form = QFormLayout()
                username_input = QLineEdit(user.username)
                password_input = QLineEdit()
                password_input.setEchoMode(QLineEdit.Password)
                role_input = QLineEdit(user.role)
                form.addRow("Username:", username_input)
                form.addRow("Password (leave blank to keep):", password_input)
                form.addRow("Role:", role_input)
                form_widget = QWidget()
                form_widget.setLayout(form)
                dialog.layout().addWidget(form_widget, 0, 0, 1, dialog.layout().columnCount())
                dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                result = dialog.exec_()
                if result == QMessageBox.Ok:
                    new_username = username_input.text().strip()
                    new_password = password_input.text().strip()
                    new_role = role_input.text().strip()
                    if not new_username or not new_role:
                        QMessageBox.warning(self, "Validation Error", "Username and role are required.")
                        return
                    # Check for username conflict
                    if new_username != user.username:
                        existing = session.query(db.User).filter_by(username=new_username).first()
                        if existing:
                            QMessageBox.warning(self, "Error", "Username already exists.")
                            return
                    user.username = new_username
                    if new_password:
                        user.password = new_password
                    user.role = new_role
                    session.commit()
                    QMessageBox.information(self, "Success", f"User '{new_username}' updated.")
                    self.load_users()

    def load_files(self):
        self.file_list.clear()
        if db and self.user:
            projects, _ = db.get_user_projects(self.user.id)
            for project in projects:
                project_id = getattr(project, "id", None)
                if project_id is not None:
                    files = db.get_files(int(project_id))
                    for file in files:
                        self.file_list.addItem(f"{file.id}: {file.filename} (Project {project.name})")

class EventLogView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Event Log"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        self.refresh_btn = QPushButton("Refresh Log")
        layout.addWidget(self.refresh_btn)
        self.setLayout(layout)
        self.refresh_btn.clicked.connect(self.load_log)
        self.load_log()

    def load_log(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                self.log_text.setPlainText(f.read())
        except FileNotFoundError:
            self.log_text.setPlainText("No log entries yet.")

class GanttChartWidget(QWidget):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.figure = Figure(figsize=(7, 2))
        self.canvas = FigureCanvas(self.figure)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)
        self.plot_gantt()

    def plot_gantt(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if db and hasattr(db, "get_tasks"):
            tasks = db.get_tasks(self.project_id)
            bars = []
            labels = []
            colors = []
            yticks = []
            yticklabels = []
            min_date = None
            max_date = None
            y = 0
            for task in tasks:
                # Parse deadline and start date
                start = getattr(task, "start_date", None)
                end = getattr(task, "deadline", None)
                if not start:
                    start = getattr(task, "created_at", None)
                if not start:
                    start = getattr(task, "deadline", None)
                if not end:
                    end = getattr(task, "deadline", None)
                try:
                    start_dt = datetime.datetime.strptime(str(start), "%Y-%m-%d")
                except Exception:
                    start_dt = None
                try:
                    end_dt = datetime.datetime.strptime(str(end), "%Y-%m-%d")
                except Exception:
                    end_dt = None
                if start_dt and end_dt:
                    bars.append((mdates.date2num(start_dt), mdates.date2num(end_dt) - mdates.date2num(start_dt)))
                    labels.append(f"Task {getattr(task, 'id', '')}: {getattr(task, 'title', '')}")
                    yticks.append(y)
                    yticklabels.append(labels[-1])
                    y += 1
                    # Subtasks
                    if hasattr(db, "get_subtasks"):
                        try:
                            subs = db.get_subtasks(task.id)
                            for sub in subs:
                                sub_start = getattr(sub, "start_date", None)
                                sub_end = getattr(sub, "deadline", None)
                                if not sub_start:
                                    sub_start = getattr(sub, "created_at", None)
                                if not sub_start:
                                    sub_start = getattr(sub, "deadline", None)
                                if not sub_end:
                                    sub_end = getattr(sub, "deadline", None)
                                try:
                                    sub_start_dt = datetime.datetime.strptime(str(sub_start), "%Y-%m-%d")
                                except Exception:
                                    sub_start_dt = None
                                try:
                                    sub_end_dt = datetime.datetime.strptime(str(sub_end), "%Y-%m-%d")
                                except Exception:
                                    sub_end_dt = None
                                if sub_start_dt and sub_end_dt:
                                    bars.append((mdates.date2num(sub_start_dt), mdates.date2num(sub_end_dt) - mdates.date2num(sub_start_dt)))
                                    labels.append(f"  Subtask {getattr(sub, 'id', '')}: {getattr(sub, 'title', '')}")
                                    yticks.append(y)
                                    yticklabels.append(labels[-1])
                                    y += 1
                        except Exception:
                            pass
            for i, (start, duration) in enumerate(bars):
                ax.barh(i, duration, left=start, height=0.4, align='center', color="#6baed6")
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels)
            ax.xaxis_date()
            ax.set_xlabel("Date")
            ax.set_title("Gantt Chart: Tasks & Subtasks")
            self.figure.tight_layout()
        self.canvas.draw()

    def refresh(self):
        self.plot_gantt()

class ProjectDetailPage(QWidget):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.members = getattr(project, "members", [])
        self.member_usernames = [getattr(m, "username", str(m)) for m in self.members]
        self.member_ids = [getattr(m, "id", None) for m in self.members]
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Project Details</b>"))
        layout.addWidget(QLabel(f"Name: {getattr(project, 'name', '')}"))
        layout.addWidget(QLabel(f"Description: {getattr(project, 'description', '')}"))
        layout.addWidget(QLabel(f"Start Date: {getattr(project, 'start_date', '')}"))
        layout.addWidget(QLabel(f"End Date: {getattr(project, 'end_date', '')}"))
        # Team members
        members = self.members
        member_names = ", ".join(self.member_usernames) if members else "N/A"
        layout.addWidget(QLabel(f"Team Members: {member_names}"))
        # Leaders (if available)
        leaders = [m for m in members if getattr(m, "role", "") == "leader"] if members else []
        leader_names = ", ".join([getattr(m, "username", str(m)) for m in leaders]) if leaders else "N/A"
        layout.addWidget(QLabel(f"Leaders: {leader_names}"))

        # --- Task List Section ---
        layout.addWidget(QLabel("<b>Tasks</b>"))

        # Inline Add Task Form
        from PyQt5.QtWidgets import QHBoxLayout
        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task Name")
        self.deadline_input = QLineEdit()
        self.deadline_input.setPlaceholderText("Deadline (YYYY-MM-DD)")
        self.dependencies_input = QLineEdit()
        self.dependencies_input.setPlaceholderText("Dependencies (comma IDs)")
        self.assigned_input = QComboBox()
        self.assigned_input.addItem("Unassigned", None)
        for m in self.members:
            self.assigned_input.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
        self.add_task_inline_btn = QPushButton("Add Task")
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.deadline_input)
        form_layout.addWidget(self.dependencies_input)
        form_layout.addWidget(self.assigned_input)
        form_layout.addWidget(self.add_task_inline_btn)
        layout.addLayout(form_layout)

        # --- Gantt Chart Section ---
        self.gantt_chart = GanttChartWidget(getattr(self.project, "id", None))
        layout.addWidget(self.gantt_chart)

        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        self.load_tasks()

        self.add_task_inline_btn.clicked.connect(self.add_task_inline)
        self.task_list.itemClicked.connect(self.expand_task_item)

        # Delete Project button
        self.delete_btn = QPushButton("Delete Project")
        layout.addWidget(self.delete_btn)
        # Back button
        self.back_btn = QPushButton("Back to Dashboard")
        layout.addWidget(self.back_btn)
        self.setLayout(layout)
        self.back_btn.clicked.connect(self.go_back)
        self.delete_btn.clicked.connect(self.confirm_delete_project)

    def load_tasks(self):
        self.task_list.clear()
        if db and hasattr(self.project, "id"):
            tasks = db.get_tasks(self.project.id)
            for task in tasks:
                item = QListWidgetItem(f"{task.id}: {task.title} | Deadline: {getattr(task, 'deadline', 'N/A')} | Assigned: {getattr(task, 'assigned_to', 'Unassigned')}")
                item.setData(32, task.id)
                self.task_list.addItem(item)
        # Refresh Gantt chart after loading tasks
        if hasattr(self, "gantt_chart"):
            self.gantt_chart.refresh()

    def expand_task_item(self, item):
        task_id = item.data(32)
        if db and hasattr(db, "get_task") and hasattr(db, "get_subtasks"):
            try:
                task = db.get_task(task_id)
                subtasks = db.get_subtasks(task_id)
            except Exception:
                QMessageBox.warning(self, "Error", "Could not load task or subtasks.")
                return
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Task Details: {getattr(task, 'title', '')}")
            vbox = QVBoxLayout()
            vbox.addWidget(QLabel(f"Task: {getattr(task, 'title', '')}"))
            vbox.addWidget(QLabel(f"Deadline: {getattr(task, 'deadline', 'N/A')}"))
            vbox.addWidget(QLabel(f"Assigned: {getattr(task, 'assigned_to', 'Unassigned')}"))
            vbox.addWidget(QLabel("Subtasks:"))
            if subtasks:
                for sub in subtasks:
                    vbox.addWidget(QLabel(f"ID: {sub.id}, Name: {sub.title}, Deadline: {getattr(sub, 'deadline', 'N/A')}, Assigned: {getattr(sub, 'assigned_to', 'Unassigned')}"))
            else:
                vbox.addWidget(QLabel("No subtasks."))
            add_subtask_btn = QPushButton("Add Subtask")
            vbox.addWidget(add_subtask_btn)
            def add_subtask():
                self.show_add_subtask_dialog(task_id)
                dlg.accept()
            add_subtask_btn.clicked.connect(add_subtask)
            dlg.setLayout(vbox)
            dlg.exec_()

    def add_task_inline(self):
        from datetime import datetime
        title = self.title_input.text().strip()
        due_date_str = self.deadline_input.text().strip()
        dependencies = self.dependencies_input.text().strip()
        assigned_id = self.assigned_input.currentData()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Task name is required.")
            return
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except Exception:
                QMessageBox.warning(self, "Validation Error", "Deadline must be in YYYY-MM-DD format.")
                return
        if db:
            try:
                task = db.create_task(
                    project_id=self.project.id,
                    title=title,
                    due_date=due_date,
                    assigned_to=assigned_id
                    # dependencies ignored/stubbed
                )
            except Exception:
                QMessageBox.warning(self, "Error", "Failed to add task (DB error).")
                return
            if task:
                log_event(f"Task '{title}' added to project {self.project.id} by user. Due date: {due_date_str}, Dependencies: {dependencies}, Assigned: {assigned_id}")
                self.load_tasks()
                self.title_input.clear()
                self.deadline_input.clear()
                self.dependencies_input.clear()
                self.assigned_input.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Error", "Failed to add task.")

    def show_add_subtask_dialog(self, parent_task_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Subtask")
        form = QFormLayout()
        title_input = QLineEdit()
        deadline_input = QLineEdit()
        dependencies_input = QLineEdit()
        assigned_input = QComboBox()
        assigned_input.addItem("Unassigned", None)
        for m in self.members:
            assigned_input.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
        form.addRow("Subtask Name:", title_input)
        form.addRow("Deadline (YYYY-MM-DD):", deadline_input)
        form.addRow("Dependencies (comma IDs):", dependencies_input)
        form.addRow("Assign to:", assigned_input)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(button_box)
        dialog.setLayout(form)
        def on_accept():
            title = title_input.text().strip()
            deadline = deadline_input.text().strip()
            dependencies = dependencies_input.text().strip()
            assigned_id = assigned_input.currentData()
            if not title:
                QMessageBox.warning(self, "Validation Error", "Subtask name is required.")
                return
            if db and hasattr(db, "create_subtask"):
                try:
                    subtask = db.create_subtask(
                        parent_task_id=parent_task_id,
                        title=title,
                        deadline=deadline,
                        dependencies=dependencies,
                        assigned_to=assigned_id
                    )
                except Exception:
                    QMessageBox.warning(self, "Error", "Failed to add subtask (DB error).")
                    return
                if subtask:
                    log_event(f"Subtask '{title}' added to task {parent_task_id} by user. Deadline: {deadline}, Dependencies: {dependencies}, Assigned: {assigned_id}")
                    self.load_tasks()
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add subtask.")
        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dialog.reject)
        dialog.exec_()

    def go_back(self):
        # Find main window and return to dashboard
        mw = self.parent()
        while mw and not isinstance(mw, MainWindow):
            mw = mw.parent()
        if mw:
            mw.stack.setCurrentWidget(mw.dashboard)
            log_event("Returned to Dashboard from Project Detail Page")

    def confirm_delete_project(self):
        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to delete the project '{getattr(self.project, 'name', '')}'? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_project()

    def delete_project(self):
        # Delete the project from the database
        if db and hasattr(self.project, "id"):
            project_id = getattr(self.project, "id")
            project_name = getattr(self.project, "name", "")
            try:
                # Pass user_id if required by db.delete_project
                user_id = None
                mw = self.parent()
                while mw and not isinstance(mw, MainWindow):
                    mw = mw.parent()
                if mw and hasattr(mw, "current_user") and mw.current_user:
                    user_id = getattr(mw.current_user, "id", None)
                if user_id is not None:
                    result = db.delete_project(project_id, user_id)
                else:
                    result = db.delete_project(project_id)
                if result:
                    log_event(f"Project '{project_name}' (ID {project_id}) deleted.")
                    QMessageBox.information(self, "Project Deleted", f"Project '{project_name}' has been deleted.")
                    # Return to dashboard
                    mw = self.parent()
                    while mw and not isinstance(mw, MainWindow):
                        mw = mw.parent()
                    if mw:
                        mw.dashboard.load_projects()
                        mw.stack.setCurrentWidget(mw.dashboard)
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete project from database.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while deleting the project: {e}")
        else:
            QMessageBox.warning(self, "Error", "Database not available or project ID missing.")

class MainWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.setWindowTitle("PyQt Project Management App (Skeleton)")
        self.resize(800, 600)

        # --- DPI/UI scaling and zoom ---
        self._scale_factor = 1.7  # Set default UI scale factor to 170%
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._base_font_size = self.font().pointSize()
        self.installEventFilter(self)
        self.setMouseTracking(True)
        self.current_user = user

        # --- Initialize stack and related widgets early ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # --- Settings Tab ---
        self.tabs = QTabWidget()
        self.main_content_widget = QWidget()
        main_content_layout = QHBoxLayout(self.main_content_widget)

        # Navigation
        self.nav_list = QListWidget()
        self.nav_list.addItems([
            "Dashboard",
            "User/File Management",
            "Event Log",
            "Logout"
        ])
        main_content_layout.addWidget(self.nav_list, 1)

        # Stacked widget for views
        self.stack = QStackedWidget()
        self.dashboard = DashboardView(main_window=self)
        self.current_user = None  # Track current authenticated user
        self.project_creation_page = ProjectCreationPage(current_user=self.current_user)
        self.user_file = UserFileManagement()
        self.event_log = EventLogView()
        self.project_detail_page = None  # Will be set dynamically
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.user_file)
        self.stack.addWidget(self.event_log)
        self.stack.addWidget(self.project_creation_page)
        main_content_layout.addWidget(self.stack, 4)

        self.main_content_widget.setLayout(main_content_layout)
        self.tabs.addTab(self.main_content_widget, "Main")
        self._init_settings_tab()
        main_layout.addWidget(self.tabs)

        self.nav_list.currentRowChanged.connect(self.display_view)
        self.nav_list.setCurrentRow(0)

        # Connect save button on project creation page to return to dashboard
        self.project_creation_page.save_btn.clicked.connect(self.return_to_dashboard)

        log_event("Application started")

        # --- Launch maximized (not fullscreen) ---
        self.showMaximized()

        # --- Initial DPI scaling ---
        self._apply_scale()

        self._load_user_display_pref()

    def _load_user_display_pref(self):
        """
        Load the current user's display scaling/zoom preference and apply it to the UI.
        Tries to load from DB first, then falls back to a user-specific JSON file.
        """
        user = getattr(self, "current_user", None)
        if not user:
            return
        # Try DB first
        if db and hasattr(db, "get_user_display_pref"):
            try:
                pref = db.get_user_display_pref(user.id)
                if pref and "scale_factor" in pref:
                    self._scale_factor = pref["scale_factor"]
                    if hasattr(self, "scale_slider"):
                        self.scale_slider.setValue(int(self._scale_factor * 100))
                    if hasattr(self, "scale_spin"):
                        self.scale_spin.setValue(int(self._scale_factor * 100))
                    self._apply_scale()
                    return
            except Exception:
                pass
        # Fallback to file
        path = self._user_pref_path()
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    scale = data.get("scale_factor")
                    if scale:
                        self._scale_factor = scale
                        if hasattr(self, "scale_slider"):
                            self.scale_slider.setValue(int(scale * 100))
                        if hasattr(self, "scale_spin"):
                            self.scale_spin.setValue(int(scale * 100))
                        self._apply_scale()
            except Exception:
                pass

    def _user_pref_path(self):
        """
        Return the file path for the current user's display preferences.
        Stores preferences as a JSON file named after the user ID in the config directory.
        """
        if not self.current_user:
            return None
        config_dir = os.path.join(os.path.dirname(__file__), "..", "..", "config")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, f"user_pref_{self.current_user.id}.json")

        """
        Load the current user's display preferences (scaling/zoom) and apply them to the UI.
        Tries to load from DB first, then falls back to a user-specific JSON file.
        """
        user = getattr(self, "current_user", None)
        if not user:
            return
        # Try DB first
        if db and hasattr(db, "get_user_display_pref"):
            try:
                pref = db.get_user_display_pref(user.id)
                if pref and "scale_factor" in pref:
                    self._scale_factor = pref["scale_factor"]
                    self.scale_slider.setValue(int(self._scale_factor * 100))
                    self.scale_spin.setValue(int(self._scale_factor * 100))
                    self._apply_scale()
                    return
            except Exception:
                pass
        # Fallback to file
        path = self._user_pref_path()
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    scale = data.get("scale_factor")
                    if scale:
                        self._scale_factor = scale
                        self.scale_slider.setValue(int(scale * 100))
                        self.scale_spin.setValue(int(scale * 100))
                        self._apply_scale()
            except Exception:
                pass

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # --- Settings Tab ---
        self.tabs = QTabWidget()
        self.main_content_widget = QWidget()
        main_content_layout = QHBoxLayout(self.main_content_widget)

        # Navigation
        self.nav_list = QListWidget()
        self.nav_list.addItems([
            "Dashboard",
            "User/File Management",
            "Event Log",
            "Logout"
        ])
        main_content_layout.addWidget(self.nav_list, 1)

        # Stacked widget for views
        self.stack = QStackedWidget()
        self.dashboard = DashboardView(main_window=self)
        self.current_user = None  # Track current authenticated user
        self.project_creation_page = ProjectCreationPage(current_user=self.current_user)
        self.user_file = UserFileManagement()
        self.event_log = EventLogView()
        self.project_detail_page = None  # Will be set dynamically
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.user_file)
        self.stack.addWidget(self.event_log)
        self.stack.addWidget(self.project_creation_page)
        main_content_layout.addWidget(self.stack, 4)

        self.main_content_widget.setLayout(main_content_layout)
        self.tabs.addTab(self.main_content_widget, "Main")
        self._init_settings_tab()
        main_layout.addWidget(self.tabs)

        self.nav_list.currentRowChanged.connect(self.display_view)
        self.nav_list.setCurrentRow(0)

        # Connect save button on project creation page to return to dashboard
        self.project_creation_page.save_btn.clicked.connect(self.return_to_dashboard)

        log_event("Application started")

        # --- Launch maximized (not fullscreen) ---
        self.showMaximized()

        # --- Initial DPI scaling ---
        self._apply_scale()

    def _init_settings_tab(self):
        settings_widget = QWidget()
        vbox = QVBoxLayout(settings_widget)

        # Display Preferences Group
        display_group = QGroupBox("Display Preferences")
        display_layout = QVBoxLayout()

        # Scaling/Zoom controls
        scale_hbox = QHBoxLayout()
        scale_label = QLabel("Scaling / Zoom:")
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(int(self._min_scale * 100))
        self.scale_slider.setMaximum(int(self._max_scale * 100))
        self.scale_slider.setValue(int(self._scale_factor * 100))
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_spin = QSpinBox()
        self.scale_spin.setMinimum(int(self._min_scale * 100))
        self.scale_spin.setMaximum(int(self._max_scale * 100))
        self.scale_spin.setValue(int(self._scale_factor * 100))
        self.scale_spin.setSuffix("%")
        scale_hbox.addWidget(scale_label)
        scale_hbox.addWidget(self.scale_slider)
        scale_hbox.addWidget(self.scale_spin)
        display_layout.addLayout(scale_hbox)

        display_group.setLayout(display_layout)
        vbox.addWidget(display_group)
        vbox.addStretch(1)
        settings_widget.setLayout(vbox)
        self.tabs.addTab(settings_widget, "Settings")

        # Connect slider and spinbox to update scaling in real time
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        self.scale_spin.valueChanged.connect(self._on_scale_changed)
        self._syncing_scale = False

    def _on_scale_changed(self, value):
        if getattr(self, "_syncing_scale", False):
            return
        self._syncing_scale = True
        # Keep slider and spinbox in sync
        sender = self.sender()
        if sender == self.scale_slider:
            self.scale_spin.setValue(value)
        else:
            self.scale_slider.setValue(value)
        self._scale_factor = value / 100.0
        self._apply_scale()
        self._syncing_scale = False
        self._save_user_display_pref()

    def _apply_scale(self):
        # Recursively scale fonts and widgets
        def scale_widget(widget, factor):
            font = widget.font()
            font.setPointSizeF(self._base_font_size * factor)
            widget.setFont(font)
            for child in widget.findChildren(QWidget):
                try:
                    cfont = child.font()
                    cfont.setPointSizeF(self._base_font_size * factor)
                    child.setFont(cfont)
                except Exception:
                    pass
        scale_widget(self, self._scale_factor)

    def eventFilter(self, obj, event):
        # Zoom with Ctrl+Scroll
        if event.type() == QEvent.Wheel and (event.modifiers() & Qt.ControlModifier):
            delta = event.angleDelta().y()
            if delta > 0:
                self._scale_factor = min(self._scale_factor + 0.1, self._max_scale)
            else:
                self._scale_factor = max(self._scale_factor - 0.1, self._min_scale)
            self._apply_scale()
            return True
        # Zoom with Ctrl + Plus/Minus
        if event.type() == QEvent.KeyPress and (event.modifiers() & Qt.ControlModifier):
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                self._scale_factor = min(self._scale_factor + 0.1, self._max_scale)
                self._apply_scale()
                return True
            elif event.key() == Qt.Key_Minus:
                self._scale_factor = max(self._scale_factor - 0.1, self._min_scale)
                self._apply_scale()
                return True
            elif event.key() == Qt.Key_0:
                self._scale_factor = 1.0
                self._apply_scale()
                return True
        return super().eventFilter(obj, event)
    def display_view(self, index):
        """Switches the stacked view based on the selected navigation row."""
        if index == 0:
            self.stack.setCurrentWidget(self.dashboard)
        elif index == 1:
            self.stack.setCurrentWidget(self.user_file)
        elif index == 2:
            self.stack.setCurrentWidget(self.event_log)
        elif index == 3:
            # Trigger logout instead of showing project creation page
            app = QApplication.instance()
            if hasattr(app, "logout"):
                app.logout()
        else:
            # Default to dashboard if index is out of range
            self.stack.setCurrentWidget(self.dashboard)


    def return_to_dashboard(self):
        """Switch the view to the dashboard page."""
        self.dashboard.load_projects()
        self.stack.setCurrentWidget(self.dashboard)
        log_event("Returned to Dashboard from Project Creation Page")

class App(QApplication):
    def __init__(self, argv):
        # Enable DPI scaling before QApplication is created
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        super().__init__(argv)
        self._logout_key = Qt.Key_Escape  # You can change this to another key if desired
        self.current_user = None  # Store authenticated user globally

        # Create the main window and stack
        self.window = QMainWindow()
        self.window.setWindowTitle("PyQt Project Management App")
        self.window.resize(800, 600)
        self.stack = QStackedWidget()
        self.login_page = LoginScreen()
        self.main_page = MainWindow()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.main_page)
        self.window.setCentralWidget(self.stack)
        self.stack.setCurrentWidget(self.login_page)
        self.window.showMaximized()

        # Connect login button
        self.login_page.login_btn.clicked.connect(self.authenticate)

        # Install event filter for logout and scaling
        self.window.installEventFilter(self)
        self.login_page.installEventFilter(self)

    def eventFilter(self, obj, event):
        # Logout key: ESC returns to login page and logs out
        if event.type() == QEvent.KeyPress and event.key() == self._logout_key:
            self.logout()
            return True

        # --- Zoom/scale logic for login page ---
        if obj == self.login_page:
            # Zoom with Ctrl+Scroll
            if event.type() == QEvent.Wheel and (event.modifiers() & Qt.ControlModifier):
                delta = event.angleDelta().y()
                self.login_page.adjust_scale(delta)
                return True
            # Zoom with Ctrl + Plus/Minus/0
            if event.type() == QEvent.KeyPress and (event.modifiers() & Qt.ControlModifier):
                if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                    self.login_page.adjust_scale(1)
                    return True
                elif event.key() == Qt.Key_Minus:
                    self.login_page.adjust_scale(-1)
                    return True
                elif event.key() == Qt.Key_0:
                    self.login_page.adjust_scale(reset=True)
                    return True

        return super().eventFilter(obj, event)

    def logout(self):
        # Switch to login page, clear user context
        self.stack.setCurrentWidget(self.login_page)
        self.login_page.username.clear()
        self.login_page.password.clear()
        self.current_user = None
        if hasattr(self.main_page, "current_user"):
            self.main_page.current_user = None
        log_event("User logged out (logout key pressed)")

    def authenticate(self):
        username = self.login_page.username.text()
        password = self.login_page.password.text()
        # Extra debug logging for widget state and db import
        with open("login_debug.log", "a", encoding="utf-8") as dbg:
            dbg.write(f"Attempt login: username={username!r}, password={password!r}\n")
            dbg.write(f"Username widget type: {type(self.login_page.username)}\n")
            dbg.write(f"Password widget type: {type(self.login_page.password)}\n")
            dbg.write(f"Username widget text(): {self.login_page.username.text()!r}\n")
            dbg.write(f"Password widget text(): {self.login_page.password.text()!r}\n")
            dbg.write(f"db module: {db!r}\n")
        if username and password and db:
            user = db.authenticate_user(username, password)
            with open("login_debug.log", "a", encoding="utf-8") as dbg:
                dbg.write(f"db.authenticate_user returned: {user}\n")
            if user:
                log_event(f"User '{username}' logged in")
                self.current_user = user
                # Re-instantiate main page with user context
                self.main_page = MainWindow(user=user)
                # Replace main page in stack
                self.stack.removeWidget(self.stack.widget(1))
                self.stack.addWidget(self.main_page)
                self.stack.setCurrentWidget(self.main_page)
                self.main_page.current_user = user
            else:
                log_event(f"Failed login attempt for user '{username}'")
                with open("login_debug.log", "a", encoding="utf-8") as dbg:
                    dbg.write("Login failed: Invalid username or password.\n")
                QMessageBox.warning(self.login_page, "Login Failed", "Invalid username or password.")
        else:
            with open("login_debug.log", "a", encoding="utf-8") as dbg:
                dbg.write(f"Login failed: Username or password not entered. username={username!r}, password={password!r}, db={db!r}\n")
            QMessageBox.warning(self.login_page, "Login Failed", "Enter username and password.")

if __name__ == "__main__":
    app = App(sys.argv)
    sys.exit(app.exec_())

# --- User display preference persistence logic for MainWindow ---

def _save_user_display_pref(self):
    user = getattr(self, "current_user", None)
    if not user:
        return
    # Try DB first
    if db and hasattr(db, "set_user_display_pref"):
        try:
            db.set_user_display_pref(user.id, {"scale_factor": self._scale_factor})
            return
        except Exception:
            pass
    # Fallback to file
    path = _user_pref_path(self)
    if path:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"scale_factor": self._scale_factor}, f)
        except Exception:
            pass


# Attach methods to MainWindow
MainWindow._save_user_display_pref = _save_user_display_pref
MainWindow._load_user_display_pref = _load_user_display_pref