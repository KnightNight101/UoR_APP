# sip import removed; handle deleted widget with try/except
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QFormLayout, QMessageBox, QInputDialog, QComboBox, QDialog, QDialogButtonBox,
    QTabWidget, QGroupBox, QSlider, QSpinBox, QDateEdit, QCalendarWidget
)
from PyQt5.QtCore import (
    Qt,
    QEvent,
    QSize,
    QObject,
    QDate,
    QDateTime,
)
# Remove explicit enum imports; use Qt.EnumType.EnumValue style for Pylance compatibility
# (Removed duplicate import of Qt and QEvent)
# Explicitly import all needed Qt constants for clarity
# (Removed duplicate import of Qt and related classes)
# For type checkers and linters, import Qt constants directly
# (Removed unnecessary alias imports)
from PyQt5.QtGui import (
    QFont, QIcon, QPixmap, QCursor, QColor
)
import json
import os

# --- Gantt Chart Imports ---
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
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
        self.deadline_input = QLineEdit()
        # --- Structured Tasks Section ---
        from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QSpinBox, QDateEdit

        self.tasks_group = QGroupBox("Tasks (Optional)")
        self.tasks_layout = QVBoxLayout()
        self.task_entries = []

        # Header row for tasks
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Title*"))
        header_layout.addWidget(QLabel("Deadline"))
        header_layout.addWidget(QLabel("Assigned User"))
        header_layout.addWidget(QLabel("Dependencies"))
        header_layout.addWidget(QLabel("Hours"))
        header_layout.addWidget(QLabel(""))  # For remove button
        self.tasks_layout.addLayout(header_layout)

        def add_task_row(prefill=None):
            row_layout = QHBoxLayout()
            title_input = QLineEdit()
            deadline_input = QDateEdit()
            deadline_input.setCalendarPopup(True)
            deadline_input.setDisplayFormat("yyyy-MM-dd")
            assigned_input = QComboBox()
            assigned_input.addItem("Unassigned", None)
            # Populate assigned_input with team members
            for i in range(self.member_list.count()):
                item = self.member_list.item(i)
                if item is not None:
                    assigned_input.addItem(item.text(), item.data(32))
            # --- Dependencies Multi-Select ---
            dependencies_input = QLineEdit()
            dependencies_input.setReadOnly(True)
            dep_select_btn = QPushButton("Select Dependencies")
            dep_ids = []

            def open_dep_dialog():
                dep_dialog = QDialog(self)
                dep_dialog.setWindowTitle("Select Dependencies")
                vbox = QVBoxLayout(dep_dialog)
                dep_list = QListWidget()
                dep_list.setSelectionMode(QListWidget.MultiSelection)
                # Populate with all other tasks' titles (exclude this row)
                for entry in self.task_entries:
                    if entry is widgets:
                        continue
                    title = entry["title"].text().strip() if entry["title"] is not None else ""
                    if title:
                        item = QListWidgetItem(title)
                        item.setData(32, entry)
                        dep_list.addItem(item)
                vbox.addWidget(dep_list)
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                vbox.addWidget(button_box)
                def accept():
                    dep_ids.clear()
                    selected_titles = []
                    for item in dep_list.selectedItems():
                        entry = item.data(32)
                        idx = self.task_entries.index(entry)
                        dep_ids.append(idx)
                        selected_titles.append(item.text() if item is not None else "")
                    dependencies_input.setText(", ".join(selected_titles))
                    dep_dialog.accept()
                button_box.accepted.connect(accept)
                button_box.rejected.connect(dep_dialog.reject)
                dep_dialog.exec_()
            dep_select_btn.clicked.connect(open_dep_dialog)

            hours_input = QSpinBox()
            hours_input.setMinimum(0)
            hours_input.setMaximum(1000)
            remove_btn = QPushButton("Remove")
            remove_btn.setMinimumWidth(80)
            remove_btn.setToolTip("Remove this task")
            dep_select_btn.setToolTip("Select dependencies for this task")
            widgets = {
                "title": title_input,
                "deadline": deadline_input,
                "assigned": assigned_input,
                "dependencies": dependencies_input,
                "dep_ids": dep_ids,
                "dep_select_btn": dep_select_btn,
                "hours": hours_input,
                "row_layout": row_layout
            }
            if prefill:
                title_input.setText(prefill.get("title", ""))
                if prefill.get("deadline"):
                    from PyQt5.QtCore import QDate
                    try:
                        y, m, d = map(int, prefill["deadline"].split("-"))
                        deadline_input.setDate(QDate(y, m, d))
                    except Exception:
                        pass
                assigned_idx = assigned_input.findData(prefill.get("assigned"))
                if assigned_idx >= 0:
                    assigned_input.setCurrentIndex(assigned_idx)
                dependencies_input.setText(prefill.get("dependencies", ""))
                hours_input.setValue(prefill.get("hours", 0))
            row_layout.addWidget(title_input)
            row_layout.addWidget(deadline_input)
            row_layout.addWidget(assigned_input)
            row_layout.addWidget(dependencies_input)
            row_layout.addWidget(dep_select_btn)
            row_layout.addWidget(hours_input)
            row_layout.addWidget(remove_btn)
            self.tasks_layout.addLayout(row_layout)
            self.task_entries.append(widgets)
            def remove_row():
                for w in widgets.values():
                    if hasattr(w, "deleteLater"):
                        w.deleteLater()
                self.tasks_layout.removeItem(row_layout)
                self.task_entries.remove(widgets)
            remove_btn.clicked.connect(remove_row)

        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(lambda: add_task_row())
        self.tasks_layout.addWidget(self.add_task_btn)
        self.tasks_group.setLayout(self.tasks_layout)

        form.addRow("Project Title*:", self.name_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Deadline (YYYY-MM-DD):", self.deadline_input)
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
        self.vlayout.addWidget(self.tasks_group)
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
                    item.setData(Qt.ItemDataRole.UserRole, user.id)  # 32 is Qt.UserRole
                    self.member_list.addItem(item)

    def update_leader_list(self):
        self.leader_list.clear()
        selected_items = self.member_list.selectedItems()
        for item in selected_items:
            if item is not None:
                leader_item = QListWidgetItem(item.text() if item is not None else "")
                leader_item.setData(Qt.ItemDataRole.UserRole, item.data(32))  # 32 is Qt.UserRole
                self.leader_list.addItem(leader_item)
        # Auto-select creator if present
        if self.current_user:
            for i in range(self.leader_list.count()):
                leader_item = self.leader_list.item(i)
                if leader_item and leader_item.text() is not None and str(self.current_user.id) in leader_item.text():
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
        deadline = self.deadline_input.text().strip()

        # Collect structured tasks
        tasks = []
        for widgets in getattr(self, "task_entries", []):
            title = widgets["title"].text().strip()
            deadline_val = widgets["deadline"].date().toString("yyyy-MM-dd") if widgets["deadline"].date().isValid() else ""
            assigned = widgets["assigned"].currentData()
            # Use dep_ids for dependencies as list of indices (simulate IDs for new tasks)
            dependencies = widgets.get("dep_ids", [])
            hours = widgets["hours"].value()
            if title:  # Only add tasks with a title
                tasks.append({
                    "title": title,
                    "deadline": deadline_val,
                    "assigned": assigned,
                    "dependencies": dependencies,
                    "hours": hours
                })

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
        if not members:
            members = []
        if not tasks:
            tasks = []

        # Use db.create_project (tasks is now a list of dicts, but DB logic not updated yet)
        if db:
            project = db.create_project(
                name=name,
                description=description,
                owner_id=creator_id,
                members=members,
                deadline=deadline if deadline else "",
                tasks=tasks
            )
            if project:
                log_event(f"Project '{name}' created by {creator_username} (ID {creator_id}). Members: {members}")
                QMessageBox.information(self, "Project Saved", f"Project '{name}' created successfully.")
                # Optionally clear form
                self.name_input.clear()
                self.desc_input.clear()
                self.deadline_input.clear()
                # Clear all task rows
                for widgets in getattr(self, "task_entries", []):
                    for w in widgets.values():
                        if hasattr(w, "deleteLater"):
                            w.deleteLater()
                self.task_entries.clear()
                self.member_list.clearSelection()
                self.leader_list.clearSelection()
            else:
                QMessageBox.warning(self, "Error", "Failed to create project in database.")
        else:
            QMessageBox.warning(self, "Error", "Database not available.")


# Placeholder import for database models/utilities
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

class UserSideMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Menu")
        self.setModal(True)
        self.setFixedWidth(260)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background: #f8f8f8;")
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        layout.addSpacing(8)
        font = QFont()
        font.setPointSize(12)
        # User icon
        icon_label = QLabel()
        user_icon_path = os.path.join(os.path.dirname(__file__), "..", "images", "user.jpg")
        if os.path.exists(user_icon_path):
            pixmap = QPixmap(user_icon_path)
            icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("User")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        # Menu options
        btn_perf = QPushButton("My Performance")
        btn_archived = QPushButton("Archived Projects")
        btn_settings = QPushButton("Settings")
        btn_logout = QPushButton("Log Out")
        for btn in [btn_perf, btn_archived, btn_settings, btn_logout]:
            btn.setFont(font)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(160)
            layout.addWidget(btn)
        layout.addStretch(1)
        self.setLayout(layout)
        btn_logout.clicked.connect(self.handle_logout)
        self._parent = parent

        # --- Connect Settings button to open SettingsDialog ---
        def open_settings():
            # Find main window
            mw = self.parent()
            while mw and not isinstance(mw, QMainWindow):
                mw = mw.parent()
            if mw:
                dlg = SettingsDialog(mw)
                dlg.exec_()
        btn_settings.clicked.connect(open_settings)

        # --- Event filter to close menu when clicking outside ---
        self._install_outside_click_filter()

    def _install_outside_click_filter(self):
        self._filter = _OutsideClickFilter(self)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self._filter)

    def closeEvent(self, event):
        # Remove event filter when dialog closes
        if hasattr(self, "_filter"):
            app = QApplication.instance()
            if app is not None:
                app.removeEventFilter(self._filter)
            del self._filter
        super().closeEvent(event)

    def mousePressEvent(self, event):
        # If click is outside the dialog, close it
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if not self.rect().contains(pos):
                self.reject()
                return
        super().mousePressEvent(event)

    def handle_logout(self):
        # Find main window and trigger logout
        app = QApplication.instance()
        if hasattr(app, "logout"):
            app.logout()
        self.accept()

class _OutsideClickFilter(QObject):
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            # Only act if dialog is visible and modal
            if self.dialog.isVisible() and self.dialog.isModal():
                # Map global click position to dialog coordinates
                pos = self.dialog.mapFromGlobal(event.globalPos())
                if not self.dialog.rect().contains(pos):
                    self.dialog.reject()
        return False
# (Removed duplicate import of QPixmap)

class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scale_factor = 1.7  # Match MainWindow default
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._base_font_size = self.font().pointSize()

        # Outer layout to center the login box
        outer_layout = QVBoxLayout()
        outer_layout.addStretch(1)

        # --- Logo Placeholder ---
        logo_label = QLabel()
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "images", "logo.jpg")
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(120, Qt.TransformationMode.SmoothTransformation))
            else:
                logo_label.setText("[Logo Placeholder]")
        except Exception:
            logo_label.setText("[Logo Placeholder]")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(logo_label)
        # --- End Logo Placeholder ---

        # Login box frame
        from PyQt5.QtWidgets import QFrame
        login_box = QFrame()
        login_box.setObjectName("loginBox")
        login_box.setFrameShape(QFrame.StyledPanel)
        login_box.setFrameShadow(QFrame.Raised)
        login_box.setStyleSheet("""
            QFrame#loginBox {
                background: rgba(255,255,255,0.92);
                border-radius: 16px;
                border: 2px solid #4a90e2;
                max-width: 340px;
                min-width: 260px;
                padding: 32px 28px 28px 28px;
                margin: 0 auto;
                box-shadow: 0 4px 24px rgba(0,0,0,0.10);
            }
        """)

        box_layout = QVBoxLayout(login_box)
        box_layout.setSpacing(18)
        box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        box_layout.addWidget(title)

        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)
        box_layout.addLayout(form)

        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(36)
        box_layout.addWidget(self.login_btn)

        login_box.setLayout(box_layout)

        # Center the login box
        box_container = QHBoxLayout()
        box_container.addStretch(1)
        box_container.addWidget(login_box, alignment=Qt.AlignmentFlag.AlignCenter)
        box_container.addStretch(1)
        outer_layout.addLayout(box_container)
        outer_layout.addStretch(2)

        self.setLayout(outer_layout)
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

class SubtaskWidget(QWidget):
    def __init__(self, title, deadline, project_name, progress, last_updated, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
        layout = QVBoxLayout()
        title_label = QLabel(f"<b>{title}</b>")
        project_label = QLabel(f"Project: {project_name}")
        deadline_label = QLabel(f"Deadline: {deadline}")
        last_updated_label = QLabel(f"Last updated: {last_updated}")
        progress_bar = QProgressBar()
        try:
            progress_val = int(progress)
        except Exception:
            progress_val = 0
        progress_bar.setValue(progress_val)
        progress_bar.setFormat(f"Progress: {progress_val}%")
        progress_bar.setTextVisible(True)
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        # Layout arrangement
        layout.addWidget(title_label)
        info_layout = QHBoxLayout()
        info_layout.addWidget(project_label)
        info_layout.addWidget(deadline_label)
        info_layout.addWidget(last_updated_label)
        layout.addLayout(info_layout)
        layout.addWidget(progress_bar)
        self.setLayout(layout)

class CalendarTabWidget(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.event_list = QListWidget()
        layout.addWidget(self.calendar)
        layout.addWidget(QLabel("Events on Selected Date:"))
        layout.addWidget(self.event_list)
        self.setLayout(layout)
        self.calendar.selectionChanged.connect(self.update_event_list)
        self.events_by_date = {}
        self.load_events()

    def load_events(self):
        self.events_by_date = {}
        if db and self.user:
            # --- Deadlines, Tasks, Subtasks ---
            if hasattr(db, "get_user_projects"):
                projects, _ = db.get_user_projects(self.user.id)
                for project in projects:
                    # Project deadline
                    deadline = getattr(project, "deadline", None)
                    if deadline:
                        self._add_event(deadline, f"Project Deadline: {getattr(project, 'name', '')}")
                    # Tasks
                    if hasattr(db, "get_tasks"):
                        project_id = getattr(project, "id", None)
                        if project_id is not None:
                            tasks = db.get_tasks(project_id)
                        else:
                            tasks = []
                        for task in tasks:
                            t_deadline = getattr(task, "deadline", None)
                            if t_deadline:
                                self._add_event(t_deadline, f"Task: {getattr(task, 'title', '')} (Project: {getattr(project, 'name', '')})")
                            # Subtasks
                            if hasattr(db, "get_subtasks"):
                                task_id = getattr(task, "id", None)
                                if task_id is not None:
                                    subtasks = db.get_subtasks(task_id)
                                else:
                                    subtasks = []
                                for sub in subtasks:
                                    s_deadline = getattr(sub, "deadline", None)
                                    if s_deadline:
                                        self._add_event(s_deadline, f"Subtask: {getattr(sub, 'title', '')} (Task: {getattr(task, 'title', '')})")
            # --- Public Holidays ---
            if hasattr(db, "get_public_holidays"):
                holidays = getattr(db, "get_public_holidays", lambda: [])()
                for hol in holidays:
                    hol_date = getattr(hol, "date", None)
                    hol_name = getattr(hol, "name", "Public Holiday")
                    if hol_date:
                        self._add_event(hol_date, f"Public Holiday: {hol_name}")
            # --- Personal Time Off ---
            if hasattr(db, "get_personal_time_off"):
                ptos = getattr(db, "get_personal_time_off", lambda user_id: [])(self.user.id)
                for pto in ptos:
                    pto_date = getattr(pto, "date", None)
                    reason = getattr(pto, "reason", "Personal Time Off")
                    if pto_date:
                        self._add_event(pto_date, f"Personal Time Off: {reason}")

    def _add_event(self, date_str, desc):
        # Accepts date_str in "YYYY-MM-DD" or date object
        from PyQt5.QtCore import QDate
        if isinstance(date_str, str):
            try:
                y, m, d = map(int, date_str.split("-"))
                qdate = QDate(y, m, d)
            except Exception:
                return
        elif hasattr(date_str, "year") and hasattr(date_str, "month") and hasattr(date_str, "day"):
            qdate = QDate(date_str.year, date_str.month, date_str.day)
        else:
            return
        if qdate not in self.events_by_date:
            self.events_by_date[qdate] = []
        self.events_by_date[qdate].append(desc)

    def update_event_list(self):
        selected = self.calendar.selectedDate()
        self.event_list.clear()
        events = self.events_by_date.get(selected, [])
        if events:
            for e in events:
                self.event_list.addItem(e)
        else:
            self.event_list.addItem("No events.")

class DashboardView(QWidget):
    def __init__(self, parent=None, user=None, main_window=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QGridLayout, QFrame, QMenu, QAction
        from PyQt5.QtGui import QIcon, QPixmap, QCursor
        from PyQt5.QtCore import QDateTime

        self.user = user
        self.main_window = main_window

        # --- Tabs for Dashboard and Calendar ---
        self.tabs = QTabWidget()
        self.dashboard_tab = QWidget()
        self.calendar_tab = CalendarTabWidget(user=self.user)

        # --- Main layout: 3 columns, visually centered ---
        main_layout = QHBoxLayout(self.dashboard_tab)
        main_layout.setSpacing(32)
        main_layout.setContentsMargins(48, 32, 48, 32)
        main_layout.addStretch(2)  # Extra stretch for better centering

        # --- Column 1: Projects ---
        project_col = QVBoxLayout()
        project_col.addWidget(QLabel("<b>Projects</b>"))
        self.project_list = QListWidget()
        project_col.addWidget(self.project_list)
        self.add_project_btn = QPushButton("Create Project")
        project_col.addWidget(self.add_project_btn)
        project_col.addStretch(1)

        # --- Column 2: Subtasks (4 drag-and-drop categories) ---
        subtask_col = QVBoxLayout()
        subtask_col.addWidget(QLabel("<b>My Subtasks</b>"))
        categories = [
            ("Important and Urgent", "important_urgent"),
            ("Urgent", "urgent"),
            ("Important", "important"),
            ("Other", "other"),
        ]
        self.category_lists = {}
        for cat_name, cat_key in categories:
            cat_label = QLabel(cat_name)
            cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtask_col.addWidget(cat_label)
            cat_list = QListWidget()
            cat_list.setObjectName(cat_key)
            cat_list.setAcceptDrops(True)
            cat_list.setDragEnabled(True)
            cat_list.setDragDropMode(QListWidget.InternalMove)
            cat_list.setDefaultDropAction(Qt.DropAction.MoveAction)
            cat_list.setSelectionMode(QListWidget.SingleSelection)
            cat_list.setStyleSheet("QListWidget::item:selected { background: #e0f7fa; } QListWidget { border: 1px solid #bbb; }")
            subtask_col.addWidget(cat_list)
            self.category_lists[cat_key] = cat_list
            cat_list.installEventFilter(self)
        subtask_col.addStretch(1)

        # --- Column 3: Messages ---
        message_col = QVBoxLayout()
        message_col.addWidget(QLabel("<b>Messages</b>"))
        self.message_list = QListWidget()
        message_col.addWidget(self.message_list)
        self.refresh_messages_btn = QPushButton("Refresh Messages")
        message_col.addWidget(self.refresh_messages_btn)
        message_col.addStretch(1)

        # --- Assemble columns ---
        main_layout.addLayout(project_col, 2)
        main_layout.addSpacing(24)
        main_layout.addLayout(subtask_col, 4)
        main_layout.addSpacing(24)
        main_layout.addLayout(message_col, 2)
        main_layout.addStretch(2)  # Extra stretch for better centering

        # --- User Icon (top right) ---
        user_icon_layout = QHBoxLayout()
        user_icon_layout.addStretch(1)
        self.user_icon_btn = QPushButton()
        icon_pixmap = QPixmap("Draft_2/images/user.jpg")
        self.user_icon_btn.setIcon(QIcon(icon_pixmap))
        self.user_icon_btn.setIconSize(QSize(32, 32))
        self.user_icon_btn.setText("")
        self.user_icon_btn.setFixedSize(48, 48)
        self.user_icon_btn.setStyleSheet("border: none;")
        self.user_icon_btn.setToolTip("Open user menu")
        user_icon_layout.addWidget(self.user_icon_btn)
        user_icon_layout.setContentsMargins(0, 0, 0, 0)

        # --- Vertically center the main layout ---
        wrapper = QVBoxLayout()
        wrapper.addLayout(user_icon_layout)
        wrapper.addStretch(1)
        wrapper.addWidget(self.tabs)
        wrapper.addStretch(1)
        self.setLayout(wrapper)

        # Add tabs
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.calendar_tab, "Calendar")

        # --- User side menu ---
        self.user_icon_btn.clicked.connect(self.show_user_side_menu)

        # --- Connect signals and load data ---
        self.add_project_btn.clicked.connect(self.navigate_to_project_creation)
        self.project_list.itemClicked.connect(self.handle_project_click)
        for cat_list in self.category_lists.values():
            cat_list.itemDoubleClicked.connect(self.show_subtask_details)
        self.load_projects()
        self.load_subtasks()
        self.load_messages()
        self.refresh_messages_btn.clicked.connect(self.load_messages)

    def handle_project_click(self, item):
        # Get project details and navigate to detail page
        if db and self.user:
            project_name = item.text() if item is not None else ""
            projects, _ = db.get_user_projects(self.user.id)
            selected_project = None
            for project in projects:
                if getattr(project, "name", "") == project_name:
                    selected_project = project
                    break
            if selected_project and self.main_window:
                self.main_window.show_project_detail_page(selected_project)

    def show_user_side_menu(self):
        # Show the custom side menu dialog at the right edge, below the icon
        menu = UserSideMenu(self)
        # Position the dialog at the top right of the main window
        global_pos = self.user_icon_btn.mapToGlobal(self.user_icon_btn.rect().bottomRight())
        # Offset to align with the right edge of the window
        menu.move(global_pos.x() - menu.width(), global_pos.y())
        menu.exec_()

    def load_projects(self):
        self.project_list.clear()
        if db and self.user:
            projects, _ = db.get_user_projects(self.user.id)
            for project in projects:
                self.project_list.addItem(f"{project.name}")

    def navigate_to_project_creation(self):
        if self.main_window:
            self.main_window.show_project_creation_page()

    def load_subtasks(self):
        # Clear all categories
        for cat_list in self.category_lists.values():
            cat_list.clear()
        if db and self.user and hasattr(db, "get_user_subtasks"):
            subtasks = getattr(db, "get_user_subtasks", lambda user_id: [])(self.user.id)
            for sub in subtasks:
                # Determine category (stub: use sub.category if exists, else "other")
                cat = getattr(sub, "category", "other")
                if cat not in self.category_lists:
                    cat = "other"
                # Create custom widget for subtask
                widget = SubtaskWidget(
                    title=getattr(sub, "title", ""),
                    deadline=getattr(sub, "deadline", "N/A"),
                    project_name=getattr(sub, "project_name", "N/A"),
                    progress=getattr(sub, "progress", 0),
                    last_updated=getattr(sub, "last_updated", "N/A")
                )
                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())
                item.setData(32, sub.id)
                self.category_lists[cat].addItem(item)
                self.category_lists[cat].setItemWidget(item, widget)

    def load_messages(self):
        self.message_list.clear()
        if db and self.user and hasattr(db, "get_user_messages"):
            messages = getattr(db, "get_user_messages", lambda user_id: [])(self.user.id)
            for msg in messages:
                sender = getattr(msg, 'sender', 'Unknown')
                content = getattr(msg, 'content', '')
                timestamp = getattr(msg, 'timestamp', '')
                # Distinguish between messages sent by the user and others
                if hasattr(self.user, 'username') and sender == self.user.username:
                    display_sender = "You"
                else:
                    display_sender = sender
                item = QListWidgetItem(f"From: {display_sender}\n{content}\n{timestamp}")
                # Optionally, style messages from others differently
                if display_sender != "You":
                    item.setBackground(QColor("lightgray"))
                self.message_list.addItem(item)

    def eventFilter(self, obj, event):
        # Enhanced drag-and-drop between category lists with move event recording
        from PyQt5.QtCore import QEvent
        import datetime
        if event.type() == QEvent.Type.Drop and obj in self.category_lists.values():
            # Find which category this list is
            for cat_key, cat_list in self.category_lists.items():
                if obj is cat_list:
                    # Get dropped item
                    item = cat_list.currentItem()
                    if item:
                        subtask_id = item.data(32)
                        # Find previous category
                        prev_category = None
                        for prev_key, prev_list in self.category_lists.items():
                            if prev_key != cat_key:
                                for i in range(prev_list.count()):
                                    prev_item = prev_list.item(i)
                                    if prev_item and prev_item.data(32) == subtask_id:
                                        prev_category = prev_key
                                        break
                                if prev_category:
                                    break
                        # Only log and update if category changed
                        if prev_category != cat_key:
                            # Update category in DB if possible
                            if db and hasattr(db, "update_subtask_category"):
                                if hasattr(db, "update_subtask_category"):
                                    db.update_subtask_category(subtask_id, cat_key)
                            # Log event with timestamp, previous and new category
                            timestamp = datetime.datetime.now().isoformat()
                            username = getattr(self.user, 'username', '')
                            log_event(
                                f"[{timestamp}] Subtask {subtask_id} moved from '{prev_category}' to '{cat_key}' by user '{username}'"
                            )
                    break
            self.load_subtasks()
        return super().eventFilter(obj, event)

    def show_subtask_details(self, item):
        # Show subtask details dialog
        subtask_id = item.data(32)
        if db and hasattr(db, "get_subtask"):
            sub = getattr(db, "get_subtask", lambda subtask_id: None)(subtask_id)
            msg = f"Title: {getattr(sub, 'title', '')}\nDeadline: {getattr(sub, 'deadline', '')}\nProject: {getattr(sub, 'project_name', '')}\nProgress: {getattr(sub, 'progress', 0)}%\nLast updated: {getattr(sub, 'last_updated', '')}"
            QMessageBox.information(self, "Subtask Details", msg)

    # Dashboard summary removed per UI simplification instructions.

# ProjectTaskManagement class removed; logic and widgets merged into DashboardView.

class UserFileManagement(QWidget):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self._layout = QVBoxLayout()
        self.user_list = QListWidget()
        self._layout.addWidget(QLabel("Users"))
        self._layout.addWidget(self.user_list)

        # Add User and Edit User buttons (role-restricted)
        self.add_user_btn = QPushButton("Add User")
        self.edit_user_btn = QPushButton("Edit User Info")
        if self._can_manage_users():
            self._layout.addWidget(self.add_user_btn)
            self._layout.addWidget(self.edit_user_btn)
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
        # Use a QDialog with a layout, not QMessageBox for custom forms
        layout = QVBoxLayout(dialog)
        layout.addWidget(form_widget)
        dialog.setLayout(layout)
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
        user_id = int(selected.text().split(":")[0]) if selected is not None else None
        if db:
            with db.SessionLocal() as session:
                user = session.query(db.User).filter_by(id=user_id).first()
                if not user:
                    QMessageBox.warning(self, "Error", "User not found.")
                    return
                dialog = QMessageBox(self)
                dialog.setWindowTitle("Edit User Info")
                form = QFormLayout()
                username_input = QLineEdit(str(user.username))
                password_input = QLineEdit()
                password_input.setEchoMode(QLineEdit.Password)
                role_input = QLineEdit(user.role)
                form.addRow("Username:", username_input)
                form.addRow("Password (leave blank to keep):", password_input)
                form.addRow("Role:", role_input)
                form_widget = QWidget()
                form_widget.setLayout(form)
                layout = QVBoxLayout(dialog)
                layout.addWidget(form_widget)
                dialog.setLayout(layout)
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
                    # If using SQLAlchemy hybrid properties, assign to user.username directly if possible
                    try:
                        # For SQLAlchemy, assign to user.username if it's a property, else use setattr
                        try:
                            if hasattr(type(user), "username") and not isinstance(getattr(type(user), "username"), property):
                                setattr(user, "username", str(new_username))
                            else:
                                user.username = str(new_username)
                        except Exception:
                            pass
                    except Exception:
                        pass
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
        bars = []
        labels = []
        y = 0
        # For dependency arrows
        bar_positions = {}  # id -> (y, start, end)
        dep_links = []      # (from_id, to_id, from_type, to_type)
        if db and hasattr(db, "get_tasks"):
            tasks = db.get_tasks(self.project_id)
            for task in tasks:
                # Parse start and end dates (support both deadline and due_date)
                start = getattr(task, "start_date", None)
                end = getattr(task, "deadline", None)
                if not start:
                    start = getattr(task, "created_at", None)
                if not start:
                    start = getattr(task, "deadline", None)
                if not end:
                    end = getattr(task, "due_date", None)
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
                hours = getattr(task, "hours", None)
                task_id = getattr(task, "id", None)
                if start_dt and end_dt:
                    bars.append((mdates.date2num(start_dt), mdates.date2num(end_dt) - mdates.date2num(start_dt)))
                    label_hours = f" | Hours: {hours}" if hours is not None else ""
                    labels.append(f"Task {task_id}: {getattr(task, 'title', '')}{label_hours}")
                    bar_positions[("task", task_id)] = (y, mdates.date2num(start_dt), mdates.date2num(end_dt))
                    # Collect dependencies for this task
                    dependencies = getattr(task, "dependencies", [])
                    if dependencies:
                        for dep_id in dependencies:
                            dep_links.append((("task", dep_id), ("task", task_id)))
                    y += 1
                    # Subtasks
                    if hasattr(db, "get_subtasks"):
                        try:
                            task_id = getattr(task, "id", None)
                            if task_id is not None:
                                subs = db.get_subtasks(task_id)
                            else:
                                subs = []
                            for sub in subs:
                                sub_start = getattr(sub, "start_date", None)
                                sub_end = getattr(sub, "deadline", None)
                                if not sub_start:
                                    sub_start = getattr(sub, "created_at", None)
                                if not sub_start:
                                    sub_start = getattr(sub, "deadline", None)
                                if not sub_end:
                                    sub_end = getattr(sub, "due_date", None)
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
                                sub_hours = getattr(sub, "hours", None)
                                sub_id = getattr(sub, "id", None)
                                if sub_start_dt and sub_end_dt:
                                    bars.append((mdates.date2num(sub_start_dt), mdates.date2num(sub_end_dt) - mdates.date2num(sub_start_dt)))
                                    label_sub_hours = f" | Hours: {sub_hours}" if sub_hours is not None else ""
                                    labels.append(f"  Subtask {sub_id}: {getattr(sub, 'title', '')}{label_sub_hours}")
                                    bar_positions[("subtask", sub_id)] = (y, mdates.date2num(sub_start_dt), mdates.date2num(sub_end_dt))
                                    # Collect dependencies for this subtask
                                    sub_dependencies = getattr(sub, "dependencies", [])
                                    if sub_dependencies:
                                        for dep_id in sub_dependencies:
                                            # Try to infer if dep_id is a subtask or task (assume subtask if present in bar_positions)
                                            dep_key = ("subtask", dep_id) if ("subtask", dep_id) in bar_positions else ("task", dep_id)
                                            dep_links.append((dep_key, ("subtask", sub_id)))
                                    y += 1
                        except Exception:
                            pass
        if bars:
            for i, (start, duration) in enumerate(bars):
                ax.barh(i, duration, left=start, height=0.4, align='center', color="#6baed6")
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels)
            ax.xaxis_date()
            ax.set_xlabel("Date")
            ax.set_title("Gantt Chart: Tasks & Subtasks")
            # Draw dependency arrows
            for from_key, to_key in dep_links:
                if from_key in bar_positions and to_key in bar_positions:
                    from_y, _, from_end = bar_positions[from_key]
                    to_y, to_start, _ = bar_positions[to_key]
                    # Draw arrow from end of dependency to start of dependent
                    ax.annotate(
                        '',
                        xy=(to_start, to_y),
                        xytext=(from_end, from_y),
                        arrowprops=dict(arrowstyle="->", color="red", lw=1.5, shrinkA=5, shrinkB=5),
                        annotation_clip=False
                    )
            self.figure.tight_layout()
        else:
            ax.text(0.5, 0.5, "No tasks to display", ha='center', va='center', fontsize=12, transform=ax.transAxes)
            ax.set_axis_off()
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
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.refresh_members()

    def refresh_members(self):
        # Clear layout except for persistent widgets
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self.members = getattr(self.project, "members", [])
        self.member_usernames = [getattr(m, "username", str(m)) for m in self.members]
        self.member_ids = [getattr(m, "id", None) for m in self.members]
        self.vbox.addWidget(QLabel("<b>Project Details</b>"))
        self.vbox.addWidget(QLabel(f"Name: {getattr(self.project, 'name', '')}"))
        self.vbox.addWidget(QLabel(f"Description: {getattr(self.project, 'description', '')}"))
        self.vbox.addWidget(QLabel(f"Start Date: {getattr(self.project, 'start_date', '')}"))
        self.vbox.addWidget(QLabel(f"End Date: {getattr(self.project, 'end_date', '')}"))
        # Team members (interactive with hover tooltips)
        members = self.members
        from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QDialog, QDialogButtonBox
        member_row = QHBoxLayout()
        member_row.addWidget(QLabel("Team Members:"))
        if members:
            for m in members:
                username = getattr(m, "username", str(m))
                project_role = getattr(m, "role", None)
                company_role = getattr(m, "company_role", None)
                # Fallback: if no project role, use company role or "member"
                display_role = project_role if project_role else (company_role if company_role else "member")
                info = f"Username: {username}\nRole: {display_role}"
                if project_role and company_role and project_role != company_role:
                    info += f"\nCompany Role: {company_role}"
                # Add more info if needed
                member_label = QLabel(username)
                member_label.setStyleSheet("padding: 2px 8px; border: 1px solid #bbb; border-radius: 8px; margin-right: 6px;")
                member_label.setToolTip(info)
                member_row.addWidget(member_label)
        else:
            member_row.addWidget(QLabel("N/A"))
        self.vbox.addLayout(member_row)
        # Leaders (if available)
        leaders = [m for m in members if getattr(m, "role", "") == "leader"] if members else []
        leader_names = ", ".join([getattr(m, "username", str(m)) for m in leaders]) if leaders else "N/A"
        self.leader_label = QLabel(f"Leaders: {leader_names}")
        self.vbox.addWidget(self.leader_label)

        # --- Change Leader UI ---
        # Only show if user has permission (leader or admin/superuser/it)
        self.current_user = None
        mw = self.parent()
        while mw and not hasattr(mw, "current_user"):
            mw = mw.parent()
        if mw and hasattr(mw, "current_user"):
            self.current_user = getattr(mw, "current_user", None)

        def _has_leader_permission():
            if not self.current_user:
                return False
            user_id = getattr(self.current_user, "id", None)
            user_role = getattr(self.current_user, "role", "").lower()
            # Allow if user is a project leader or admin/it/superuser
            if user_role in ["admin", "it", "superuser"]:
                return True
            for m in leaders:
                if getattr(m, "id", None) == user_id:
                    return True
            return False

        if _has_leader_permission() and len(self.members) > 1:
            self.change_leader_btn = QPushButton("Change Team Leader")
            self.vbox.addWidget(self.change_leader_btn)
            self.change_leader_btn.clicked.connect(self.show_change_leader_dialog)

        # ... rest of the UI setup (tasks, buttons, etc.) ...
        # You may need to re-add other widgets here if they depend on member/leader state.

    def show_change_leader_dialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("Change Team Leader")
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Select new team leader:"))
        combo = QComboBox()
        member_id_map = {}
        for m in self.members:
            username = getattr(m, "username", str(m))
            uid = getattr(m, "id", None)
            combo.addItem(username, uid)
            member_id_map[uid] = m
        # Preselect current leader if possible
        current_leader = next((m for m in self.members if getattr(m, "role", "") == "leader"), None)
        if current_leader:
            idx = combo.findData(getattr(current_leader, "id", None))
            if idx >= 0:
                combo.setCurrentIndex(idx)
        vbox.addWidget(combo)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)
        dlg.setLayout(vbox)

        def on_accept():
            new_leader_id = combo.currentData()
            if new_leader_id is None:
                QMessageBox.warning(self, "Error", "Please select a team member.")
                return
            # Call backend to update leader
            if db and hasattr(db, "update_project_leader"):
                try:
                    if hasattr(db, "update_project_leader"):
                        result = db.update_project_leader(getattr(self.project, "id", None), new_leader_id)
                    else:
                        result = None
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to update leader: {e}")
                    return
            else:
                # Fallback: update member roles directly if possible
                try:
                    if hasattr(db, "SessionLocal") and hasattr(db, "Project"):
                        with db.SessionLocal() as session:
                            project = session.query(db.Project).filter_by(id=getattr(self.project, "id", None)).first()
                    else:
                        project = None
                        if not project:
                            QMessageBox.warning(self, "Error", "Project not found.")
                            return
                        # Remove 'leader' from all, set to 'member'
                        for m in project.members:
                            if hasattr(m, "role"):
                                m.role = "member"
                        # Set new leader
                        for m in project.members:
                            if getattr(m, "id", None) == new_leader_id:
                                m.role = "leader"
                        session.commit()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to update leader: {e}")
                    return
            # Refresh UI
            self.refresh_leader_label(new_leader_id)
            QMessageBox.information(self, "Success", "Team leader updated.")
            dlg.accept()

        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dlg.reject)
        dlg.exec_()

    def refresh_leader_label(self, new_leader_id):
        # Update the label to reflect the new leader
        for m in self.members:
            if hasattr(m, "role"):
                m.role = "leader" if getattr(m, "id", None) == new_leader_id else "member"
        leader_names = ", ".join([getattr(m, "username", str(m)) for m in self.members if getattr(m, "role", "") == "leader"])
        self.leader_label.setText(f"Leaders: {leader_names if leader_names else 'N/A'}")

        # --- Task List Section ---
        self.vbox.addWidget(QLabel("<b>Tasks</b>"))

        # Inline Add Task Form
        from PyQt5.QtWidgets import QHBoxLayout
        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task Name")
        from PyQt5.QtCore import QDate
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("yyyy-MM-dd")
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setDisplayFormat("yyyy-MM-dd")
        self.dependencies_input = QLineEdit()
        self.dependencies_input.setReadOnly(True)
        self.dep_select_btn = QPushButton("Select Dependencies")
        self.dep_ids = []
        
        # --- Hours input for tasks ---
        self.hours_input = QSpinBox()
        self.hours_input.setMinimum(0)
        self.hours_input.setMaximum(1000)
        self.hours_input.setPrefix("Hours: ")
        
        def open_dep_dialog():
            dep_dialog = QDialog(self)
            dep_dialog.setWindowTitle("Select Dependencies")
            vbox = QVBoxLayout(dep_dialog)
            dep_list = QListWidget()
            dep_list.setSelectionMode(QListWidget.MultiSelection)
            # Populate with all other tasks in the project
            if db and hasattr(self.project, "id"):
                tasks = db.get_tasks(self.project.id)
                for task in tasks:
                    if hasattr(task, "id") and hasattr(task, "title"):
                        item = QListWidgetItem(f"{task.id}: {task.title}")
                        item.setData(32, task.id)
                        dep_list.addItem(item)
            vbox.addWidget(dep_list)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            vbox.addWidget(button_box)
            def accept():
                self.dep_ids.clear()
                selected_titles = []
                for item in dep_list.selectedItems():
                    tid = item.data(32)
                    self.dep_ids.append(tid)
                    selected_titles.append(item.text() if item is not None else "")
                self.dependencies_input.setText(", ".join(selected_titles))
                dep_dialog.accept()
            button_box.accepted.connect(accept)
            button_box.rejected.connect(dep_dialog.reject)
            dep_dialog.exec_()
        self.dep_select_btn.clicked.connect(open_dep_dialog)
        self.assigned_input = QComboBox()
        self.assigned_input.addItem("Unassigned", None)
        for m in self.members:
            self.assigned_input.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
        self.add_task_inline_btn = QPushButton("Add Task")
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.deadline_input)
        form_layout.addWidget(self.dependencies_input)
        form_layout.addWidget(self.assigned_input)
        form_layout.addWidget(self.dep_select_btn)
        form_layout.addWidget(self.hours_input)
        form_layout.addWidget(self.add_task_inline_btn)
        self.vbox.addLayout(form_layout)

        # --- Gantt Chart Section ---
        self.gantt_chart = GanttChartWidget(getattr(self.project, "id", None))
        self.vbox.addWidget(self.gantt_chart)

        self.task_list = QListWidget()
        self.vbox.addWidget(self.task_list)
        self.load_tasks()

        self.add_task_inline_btn.clicked.connect(self.add_task_inline)
        self.task_list.itemClicked.connect(self.expand_task_item)

        # Delete Project button
        self.delete_btn = QPushButton("Delete Project")
        self.vbox.addWidget(self.delete_btn)
        # Back button
        self.back_btn = QPushButton("Back to Dashboard")
        self.vbox.addWidget(self.back_btn)
        self.setLayout(self.vbox)
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
                task = getattr(db, "get_task", lambda task_id: None)(task_id)
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
        title = self.title_input.text().strip()
        due_date_qdate = self.deadline_input.date()
        due_date_obj = due_date_qdate.toPyDate()  # QDate -> Python date
        dependencies = self.dep_ids
        assigned_id = self.assigned_input.currentData()
        hours = self.hours_input.value()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Task name is required.")
            return
        if db:
            try:
                task = db.create_task(
                    project_id=self.project.id,
                    title=title,
                    # Convert date to datetime if needed
                    due_date=(
                        datetime.datetime.combine(due_date_obj, datetime.time.min)
                        if due_date_obj is not None
                        else None
                    ),
                    assigned_to=assigned_id,
                    dependencies=dependencies,
                    hours=hours
                )
            except Exception:
                QMessageBox.warning(self, "Error", "Failed to add task (DB error).")
                return
            if task:
                log_event(f"Task '{title}' added to project {self.project.id} by user. Due date: {due_date_obj}, Dependencies: {dependencies}, Assigned: {assigned_id}, Hours: {hours}")
                self.load_tasks()
                # Also reload subtasks for all tasks to reflect new "check progress" subtask
                if hasattr(self, "task_list"):
                    for i in range(self.task_list.count()):
                        item = self.task_list.item(i)
                        if item:
                            self.expand_task_item(item)
                self.title_input.clear()
                self.deadline_input.clear()
                self.dependencies_input.clear()
                self.dep_ids.clear()
                self.assigned_input.setCurrentIndex(0)
                self.hours_input.setValue(0)
            else:
                QMessageBox.warning(self, "Error", "Failed to add task.")

    def show_add_subtask_dialog(self, parent_task_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Subtask")
        form = QFormLayout()
        title_input = QLineEdit()
        from PyQt5.QtCore import QDate
        deadline_input = QDateEdit()
        deadline_input.setCalendarPopup(True)
        deadline_input.setDisplayFormat("yyyy-MM-dd")
        deadline_input.setDate(QDate.currentDate())
        dependencies_input = QLineEdit()
        dependencies_input.setReadOnly(True)
        dep_select_btn = QPushButton("Select Dependencies")
        dep_ids = []
        
        # --- Hours input for subtasks ---
        hours_input = QSpinBox()
        hours_input.setMinimum(0)
        hours_input.setMaximum(1000)
        hours_input.setPrefix("Hours: ")
        
        def open_dep_dialog():
            dep_dialog = QDialog(dialog)
            dep_dialog.setWindowTitle("Select Dependencies")
            vbox = QVBoxLayout(dep_dialog)
            dep_list = QListWidget()
            dep_list.setSelectionMode(QListWidget.MultiSelection)
            # Populate with all other tasks and subtasks in the project
            if db and hasattr(self.project, "id"):
                tasks = db.get_tasks(self.project.id)
                for task in tasks:
                    if hasattr(task, "id") and hasattr(task, "title"):
                        item = QListWidgetItem(f"Task {task.id}: {task.title}")
                        item.setData(32, ("task", task.id))
                        dep_list.addItem(item)
                        # Add subtasks
                        if hasattr(db, "get_subtasks"):
                            task_id = getattr(task, "id", None)
                            if task_id is not None:
                                subs = db.get_subtasks(task_id)
                            else:
                                subs = []
                            for sub in subs:
                                item2 = QListWidgetItem(f"Subtask {sub.id}: {sub.title}")
                                item2.setData(32, ("subtask", sub.id))
                                dep_list.addItem(item2)
            vbox.addWidget(dep_list)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            vbox.addWidget(button_box)
            def accept():
                dep_ids.clear()
                selected_titles = []
                for item in dep_list.selectedItems():
                    kind, id_ = item.data(32)
                    dep_ids.append((kind, id_))
                    selected_titles.append(item.text() if item is not None else "")
                dependencies_input.setText(", ".join(selected_titles))
                dep_dialog.accept()
            button_box.accepted.connect(accept)
            button_box.rejected.connect(dep_dialog.reject)
            dep_dialog.exec_()
        dep_select_btn.clicked.connect(open_dep_dialog)
        
        assigned_input = QComboBox()
        assigned_input.addItem("Unassigned", None)
        for m in self.members:
            assigned_input.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
        form.addRow("Subtask Name:", title_input)
        form.addRow("Deadline (YYYY-MM-DD):", deadline_input)
        form.addRow("Dependencies:", dependencies_input)
        form.addRow("", dep_select_btn)
        form.addRow("Assign to:", assigned_input)
        form.addRow("Hours:", hours_input)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(button_box)
        dialog.setLayout(form)
        def on_accept():
            title = title_input.text().strip()
            deadline = deadline_input.date().toString("yyyy-MM-dd")
            dependencies = [id_ for kind, id_ in dep_ids]
            assigned_id = assigned_input.currentData()
            hours = hours_input.value()
            if not title:
                QMessageBox.warning(self, "Validation Error", "Subtask name is required.")
                return
            if db and hasattr(db, "create_subtask"):
                try:
                    # Adjust parameter names to match expected signature
                    subtask = db.create_subtask(
                        task_id=parent_task_id,
                        title=title,
                        # Convert deadline string to datetime if needed
                        due_date=datetime.datetime.strptime(deadline, "%Y-%m-%d") if deadline else None,
                        dependencies=dependencies,
                        assigned_to=assigned_id,
                        hours=hours
                    )
                except Exception:
                    QMessageBox.warning(self, "Error", "Failed to add subtask (DB error).")
                    return
                if subtask:
                    log_event(f"Subtask '{title}' added to task {parent_task_id} by user. Deadline: {deadline}, Dependencies: {dependencies}, Assigned: {assigned_id}, Hours: {hours}")
                    self.load_tasks()
                    # Also reload subtasks for this task to reflect "check progress" deadline update
                    self.expand_task_item(self.task_list.currentItem() if hasattr(self, "task_list") else None)
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add subtask.")
        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dialog.reject)
        dialog.exec_()

    def go_back(self):
        # Find main window and return to dashboard
        mw = self.parent()
        # Import MainWindow locally to avoid NameError
        from Draft_2.app.main import MainWindow
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

class SettingsDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedWidth(350)
        self.main_window = main_window

        vbox = QVBoxLayout(self)

        # Display Preferences Group
        display_group = QGroupBox("Display Preferences")
        display_layout = QVBoxLayout()

        # Scaling/Zoom controls
        scale_hbox = QHBoxLayout()
        scale_label = QLabel("Scaling / Zoom:")
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(int(main_window._min_scale * 100))
        self.scale_slider.setMaximum(int(main_window._max_scale * 100))
        self.scale_slider.setValue(int(main_window._scale_factor * 100))
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_spin = QSpinBox()
        self.scale_spin.setMinimum(int(main_window._min_scale * 100))
        self.scale_spin.setMaximum(int(main_window._max_scale * 100))
        self.scale_spin.setValue(int(main_window._scale_factor * 100))
        self.scale_spin.setSuffix("%")
        scale_hbox.addWidget(scale_label)
        scale_hbox.addWidget(self.scale_slider)
        scale_hbox.addWidget(self.scale_spin)
        display_layout.addLayout(scale_hbox)

        display_group.setLayout(display_layout)
        vbox.addWidget(display_group)
        vbox.addStretch(1)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)

        # Connect slider and spinbox to update scaling in real time
        self._syncing_scale = False
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        self.scale_spin.valueChanged.connect(self._on_scale_changed)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def _on_scale_changed(self, value):
        if self._syncing_scale:
            return
        self._syncing_scale = True
        sender = self.sender()
        if sender == self.scale_slider:
            self.scale_spin.setValue(value)
        else:
            self.scale_slider.setValue(value)
        self.main_window._scale_factor = value / 100.0
        self.main_window._apply_scale()
        self._syncing_scale = False
        self.main_window._save_user_display_pref()
class MainWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        # Ensure scaling attributes are always initialized before any access
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._scale_factor = 1.7
        self._base_font_size = self.font().pointSize()
        self.setWindowTitle("PyQt Project Management App (Skeleton)")
        self.resize(800, 600)
        self.stack = QStackedWidget(self)
        self.current_user = user
        self.dashboard = DashboardView(main_window=self, user=self.current_user)
        self.stack.addWidget(self.dashboard)
        self.setCentralWidget(self.stack)
        self.project_creation_page = None
        self.project_detail_page = None

    def show_project_creation_page(self):
        while True:
            try:
                if self.project_creation_page is not None and self.project_creation_page in [self.stack.widget(i) for i in range(self.stack.count())]:
                    self.stack.removeWidget(self.project_creation_page)
                self.project_creation_page = ProjectCreationPage(parent=self, current_user=self.current_user)
                self.stack.addWidget(self.project_creation_page)
                self.stack.setCurrentWidget(self.project_creation_page)
                break
            except RuntimeError:
                # QStackedWidget deleted or error during addWidget/setCurrentWidget, recreate and retry
                self.stack = QStackedWidget(self)
                self.setCentralWidget(self.stack)

    def show_project_detail_page(self, project):
        try:
            if (
                hasattr(self, "stack")
                and self.stack is not None
                and self.project_detail_page is not None
                and self.project_detail_page in [self.stack.widget(i) for i in range(self.stack.count())]
            ):
                # normal logic here
                pass
        except RuntimeError:
            # Widget has been deleted, handle gracefully (e.g., ignore or recreate stack)
            return
            self.stack.removeWidget(self.project_detail_page)
        self.project_detail_page = ProjectDetailPage(project, parent=self)
        self.stack.addWidget(self.project_detail_page)
        self.stack.setCurrentWidget(self.project_detail_page)

        # --- DPI/UI scaling and zoom ---
        self._scale_factor = 1.7  # Set default UI scale factor to 170%
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._base_font_size = self.font().pointSize()
        self.installEventFilter(self)
        self.setMouseTracking(True)
        # self.current_user = user  # Removed: 'user' is not defined in this scope

        # --- Only show the main dashboard ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        self.dashboard = DashboardView(main_window=self, user=self.current_user)
        main_layout.addWidget(self.dashboard)

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
                pref = getattr(db, "get_user_display_pref", lambda user_id: None)(user.id)
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

        # Only show the main dashboard
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        self.dashboard = DashboardView(main_window=self, user=self.current_user)
        main_layout.addWidget(self.dashboard)

        log_event("Application started")

        # --- Launch maximized (not fullscreen) ---
        self.showMaximized()

        # --- Initial DPI scaling ---
        self._apply_scale()

    # Settings tab and related logic removed; settings will be moved to a dialog accessible from the user icon menu.

    # _on_scale_changed removed; scaling logic will be handled in the settings dialog.

    def _save_user_display_pref(self):
        """
        Save the current user's display scaling/zoom preference to persistent storage.
        Tries to save to DB first, then falls back to a user-specific JSON file.
        """
        user = getattr(self, "current_user", None)
        if not user:
            return
        # Try DB first
        if db and hasattr(db, "set_user_display_pref"):
            try:
                if hasattr(db, "set_user_display_pref"):
                    db.set_user_display_pref(user.id, {"scale_factor": self._scale_factor})
                return
            except Exception:
                pass
        # Fallback to file
        path = self._user_pref_path()
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"scale_factor": self._scale_factor}, f)
            except Exception:
                pass

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
        if event.type() == QEvent.Type.Wheel and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            delta = event.angleDelta().y()
            if delta > 0:
                self._scale_factor = min(self._scale_factor + 0.1, self._max_scale)
            else:
                self._scale_factor = max(self._scale_factor - 0.1, self._min_scale)
            self._apply_scale()
            return True
        # Zoom with Ctrl + Plus/Minus
        if event.type() == QEvent.Type.KeyPress and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self._scale_factor = min(self._scale_factor + 0.1, self._max_scale)
                self._apply_scale()
                return True
            elif event.key() == Qt.Key.Key_Minus:
                self._scale_factor = max(self._scale_factor - 0.1, self._min_scale)
                self._apply_scale()
                return True
            elif event.key() == Qt.Key.Key_0:
                self._scale_factor = 1.0
                self._apply_scale()
                return True
        return super().eventFilter(obj, event)
    # Removed navigation and tab logic; only dashboard is shown.

class App(QApplication):
    def __init__(self, argv):
        # Enable DPI scaling before QApplication is created
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        super().__init__(argv)
        self._logout_key = Qt.Key.Key_Escape  # You can change this to another key if desired
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
        if event.type() == QEvent.Type.KeyPress and event.key() == self._logout_key:
            self.logout()
            return True

        # --- Zoom/scale logic for login page ---
        if obj == self.login_page:
            # Zoom with Ctrl+Scroll
            if event.type() == QEvent.Type.Wheel and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                delta = event.angleDelta().y()
                self.login_page.adjust_scale(delta)
                return True
            # Zoom with Ctrl + Plus/Minus/0
            if event.type() == QEvent.Type.KeyPress and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                    self.login_page.adjust_scale(1)
                    return True
                elif event.key() == Qt.Key.Key_Minus:
                    self.login_page.adjust_scale(-1)
                    return True
                elif event.key() == Qt.Key.Key_0:
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
