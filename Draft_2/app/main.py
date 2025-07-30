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
        if self.current_user:
            creator_id = self.current_user.id
            # Add creator to members if not present
            found = False
            for i in range(self.member_list.count()):
                member_item = self.member_list.item(i)
                if member_item and str(creator_id) in member_item.text():
                    member_item.setSelected(True)
                    found = True
            if not found:
                # Add creator to member list if not present
                item = QListWidgetItem(f"{creator_id}: {self.current_user.username}")
                item.setData(32, creator_id)
                self.member_list.addItem(item)
                item.setSelected(True)
            # Add creator to leaders if not present
            found_leader = False
            for i in range(self.leader_list.count()):
                leader_item = self.leader_list.item(i)
                if leader_item and str(creator_id) in leader_item.text():
                    leader_item.setSelected(True)
                    found_leader = True
            if not found_leader:
                leader_item = QListWidgetItem(f"{creator_id}: {self.current_user.username}")
                leader_item.setData(32, creator_id)
                self.leader_list.addItem(leader_item)
                leader_item.setSelected(True)
        # Continue with save logic (placeholder)
        QMessageBox.information(self, "Project Saved", "Project creation logic not implemented.")


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
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.layout = QVBoxLayout()
        self.stats_label = QLabel("Dashboard")
        self.layout.addWidget(self.stats_label)
        self.setLayout(self.layout)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        if db and self.user:
            projects, total = db.get_user_projects(self.user.id)
            stats = []
            for project in projects:
                project_id = getattr(project, "id", None)
                if project_id is not None:
                    stat = db.get_project_statistics(int(project_id), self.user.id)
                    if stat:
                        stats.append(f"Project: {project.name} | Tasks: {stat['total_tasks']} | Members: {stat['member_count']}")
            self.stats_label.setText("Dashboard\n" + "\n".join(stats))
        else:
            self.stats_label.setText("Dashboard\nNo data available.")

class ProjectTaskManagement(QWidget):
    def __init__(self, parent=None, user=None, main_window=None):
        super().__init__(parent)
        self.user = user
        self.main_window = main_window
        self.layout = QVBoxLayout()
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
        self.setLayout(self.layout)

        self.refresh_projects_btn.clicked.connect(self.load_projects)
        self.add_project_btn.clicked.connect(self.navigate_to_project_creation)
        self.project_list.itemClicked.connect(self.load_tasks)
        self.add_task_btn.clicked.connect(self.add_task)
        self.load_projects()

    def load_projects(self):
        self.project_list.clear()
        if db and self.user:
            projects, _ = db.get_user_projects(self.user.id)
            for project in projects:
                self.project_list.addItem(f"{project.id}: {project.name}")

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
            "Project/Task Management",
            "User/File Management",
            "Event Log",
            "Logout"
        ])
        main_layout.addWidget(self.nav_list, 1)

        # Stacked widget for views
        self.stack = QStackedWidget()
        self.dashboard = DashboardView()
        self.project_creation_page = ProjectCreationPage()
        self.project_task = ProjectTaskManagement(main_window=self)
        self.user_file = UserFileManagement()
        self.event_log = EventLogView()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.project_task)
        self.stack.addWidget(self.user_file)
        self.stack.addWidget(self.event_log)
        self.stack.addWidget(self.project_creation_page)
        main_layout.addWidget(self.stack, 4)

        self.nav_list.currentRowChanged.connect(self.display_view)
        self.nav_list.setCurrentRow(0)

        # Connect save button on project creation page to return to project/task management
        self.project_creation_page.save_btn.clicked.connect(self.return_to_project_task)

        log_event("Application started")

    def display_view(self, idx):
        if idx == 0:
            self.stack.setCurrentWidget(self.dashboard)
            log_event("Navigated to Dashboard")
        elif idx == 1:
            self.stack.setCurrentWidget(self.project_task)
            log_event("Navigated to Project/Task Management")
        elif idx == 2:
            self.stack.setCurrentWidget(self.user_file)
            log_event("Navigated to User/File Management")
        elif idx == 3:
            self.stack.setCurrentWidget(self.event_log)
            log_event("Viewed Event Log")
        elif idx == 4:
            self.logout()

    def show_project_creation_page(self):
        self.stack.setCurrentWidget(self.project_creation_page)
        log_event("Navigated to Project Creation Page")

    def return_to_project_task(self):
        self.stack.setCurrentWidget(self.project_task)
        log_event("Returned to Project/Task Management from Project Creation Page")

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
                # Re-instantiate views with user context
                self.main.dashboard = DashboardView(user=user)
                self.main.project_task = ProjectTaskManagement(user=user, main_window=self.main)
                self.main.user_file = UserFileManagement(user=user)
                self.main.stack.removeWidget(self.main.stack.widget(0))
                self.main.stack.removeWidget(self.main.stack.widget(0))
                self.main.stack.removeWidget(self.main.stack.widget(0))
                self.main.stack.insertWidget(0, self.main.dashboard)
                self.main.stack.insertWidget(1, self.main.project_task)
                self.main.stack.insertWidget(2, self.main.user_file)
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