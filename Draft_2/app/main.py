import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QFormLayout, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt

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

class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Login"))
        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        self.login_btn = QPushButton("Login")
        layout.addWidget(self.login_btn)
        self.register_btn = QPushButton("Register")
        layout.addWidget(self.register_btn)
        self.setLayout(layout)

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
        self.layout.addWidget(QLabel("Tasks"))
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

    def add_task(self):
        if db and self.user:
            current_project = self.project_list.currentItem()
            if not current_project:
                QMessageBox.warning(self, "No Project", "Select a project first.")
                return
            project_id = int(current_project.text().split(":")[0])
            title, ok = QInputDialog.getText(self, "Add Task", "Task Title:")
            if ok and title:
                task = db.create_task(project_id=project_id, title=title)
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
        self.load_users()
        self.load_files()

    def load_users(self):
        self.user_list.clear()
        if db:
            # List all users (admin only in real app)
            with db.SessionLocal() as session:
                users = session.query(db.User).all()
                for user in users:
                    self.user_list.addItem(f"{user.id}: {user.username}")

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

class ProjectDetailPage(QWidget):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Project Details</b>"))
        layout.addWidget(QLabel(f"Name: {getattr(project, 'name', '')}"))
        layout.addWidget(QLabel(f"Description: {getattr(project, 'description', '')}"))
        layout.addWidget(QLabel(f"Start Date: {getattr(project, 'start_date', '')}"))
        layout.addWidget(QLabel(f"End Date: {getattr(project, 'end_date', '')}"))
        # Team members
        members = getattr(project, "members", [])
        member_names = ", ".join([getattr(m, "username", str(m)) for m in members]) if members else "N/A"
        layout.addWidget(QLabel(f"Team Members: {member_names}"))
        # Leaders (if available)
        leaders = [m for m in members if getattr(m, "role", "") == "leader"] if members else []
        leader_names = ", ".join([getattr(m, "username", str(m)) for m in leaders]) if leaders else "N/A"
        layout.addWidget(QLabel(f"Leaders: {leader_names}"))
        # Back button
        self.back_btn = QPushButton("Back to Dashboard")
        layout.addWidget(self.back_btn)
        self.setLayout(layout)
        self.back_btn.clicked.connect(self.go_back)

    def go_back(self):
        # Find main window and return to dashboard
        mw = self.parent()
        while mw and not isinstance(mw, MainWindow):
            mw = mw.parent()
        if mw:
            mw.stack.setCurrentWidget(mw.dashboard)
            log_event("Returned to Dashboard from Project Detail Page")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Project Management App (Skeleton)")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # Navigation
        self.nav_list = QListWidget()
        self.nav_list.addItems([
            "Dashboard",
            "User/File Management",
            "Event Log",
            "Logout"
        ])
        main_layout.addWidget(self.nav_list, 1)

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
        main_layout.addWidget(self.stack, 4)

        self.nav_list.currentRowChanged.connect(self.display_view)
        self.nav_list.setCurrentRow(0)

        # Connect save button on project creation page to return to dashboard
        self.project_creation_page.save_btn.clicked.connect(self.return_to_dashboard)

        log_event("Application started")

    def display_view(self, idx):
        if idx == 0:
            self.stack.setCurrentWidget(self.dashboard)
            log_event("Navigated to Dashboard")
        elif idx == 1:
            self.stack.setCurrentWidget(self.user_file)
            log_event("Navigated to User/File Management")
        elif idx == 2:
            self.stack.setCurrentWidget(self.event_log)
            log_event("Viewed Event Log")
        elif idx == 3:
            self.logout()

    def show_project_creation_page(self):
        # Always update ProjectCreationPage with current user before showing
        self.project_creation_page.current_user = self.current_user
        self.stack.setCurrentWidget(self.project_creation_page)
        log_event("Navigated to Project Creation Page")

    def show_project_detail_page(self, project):
        # Remove previous detail page if exists
        if self.project_detail_page:
            self.stack.removeWidget(self.project_detail_page)
        self.project_detail_page = ProjectDetailPage(project, parent=self)
        self.stack.addWidget(self.project_detail_page)
        self.stack.setCurrentWidget(self.project_detail_page)
        log_event(f"Viewed details for project '{getattr(project, 'name', '')}'")

    def return_to_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)
        log_event("Returned to Dashboard from Project Creation Page")

    def logout(self):
        log_event("User logged out")
        QMessageBox.information(self, "Logout", "You have been logged out.")
        self.close()

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.login = LoginScreen()
        self.main = MainWindow()
        self.login.login_btn.clicked.connect(self.authenticate)
        self.login.show()
        self.current_user = None  # Store authenticated user globally

    def authenticate(self):
        username = self.login.username.text()
        password = self.login.password.text()
        # Extra debug logging for widget state and db import
        with open("login_debug.log", "a", encoding="utf-8") as dbg:
            dbg.write(f"Attempt login: username={username!r}, password={password!r}\n")
            dbg.write(f"Username widget type: {type(self.login.username)}\n")
            dbg.write(f"Password widget type: {type(self.login.password)}\n")
            dbg.write(f"Username widget text(): {self.login.username.text()!r}\n")
            dbg.write(f"Password widget text(): {self.login.password.text()!r}\n")
            dbg.write(f"db module: {db!r}\n")
        if username and password and db:
            user = db.authenticate_user(username, password)
            with open("login_debug.log", "a", encoding="utf-8") as dbg:
                dbg.write(f"db.authenticate_user returned: {user}\n")
            if user:
                log_event(f"User '{username}' logged in")
                self.login.close()
                # Set user context globally and in main window
                self.current_user = user
                self.main.current_user = user
                # Re-instantiate views with user context
                self.main.dashboard = DashboardView(user=user, main_window=self.main)
                self.main.user_file = UserFileManagement(user=user)
                self.main.project_creation_page = ProjectCreationPage(current_user=user)
                # Remove all widgets from the stack
                while self.main.stack.count() > 0:
                    self.main.stack.removeWidget(self.main.stack.widget(0))
                self.main.stack.insertWidget(0, self.main.dashboard)
                self.main.stack.insertWidget(1, self.main.user_file)
                self.main.stack.insertWidget(2, self.main.event_log)
                self.main.stack.insertWidget(3, self.main.project_creation_page)
                self.main.show()
            else:
                log_event(f"Failed login attempt for user '{username}'")
                with open("login_debug.log", "a", encoding="utf-8") as dbg:
                    dbg.write("Login failed: Invalid username or password.\n")
                QMessageBox.warning(self.login, "Login Failed", "Invalid username or password.")
        else:
            with open("login_debug.log", "a", encoding="utf-8") as dbg:
                dbg.write(f"Login failed: Username or password not entered. username={username!r}, password={password!r}, db={db!r}\n")
            QMessageBox.warning(self.login, "Login Failed", "Enter username and password.")

if __name__ == "__main__":
    app = App(sys.argv)
    sys.exit(app.exec_())