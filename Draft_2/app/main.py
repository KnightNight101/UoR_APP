from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QCoreApplication
import sys
import os
import json

# PyQt5 core widgets and utilities
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QFormLayout, QMessageBox, QInputDialog, QComboBox, QDialog, QDialogButtonBox,
    QTabWidget, QGroupBox, QSlider, QSpinBox, QDateEdit, QCalendarWidget
)
from PyQt5.QtCore import (
    Qt, QEvent, QSize, QObject, QDate, QDateTime
)
from PyQt5.QtGui import (
    QFont, QIcon, QPixmap, QCursor, QColor, QDrag
)

# Matplotlib for Gantt chart visualization
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime

# --- Utility: Logging ---
def log_event(event):
    """Append event messages to the event log."""
    import datetime
    LOG_FILE = "event_log.txt"
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event}\n")

def log_error(error_msg):
    """Append error messages to the event log and print to stderr."""
    import datetime, traceback, sys
    LOG_FILE = "event_log.txt"
    timestamp = datetime.datetime.now().isoformat()
    full_msg = f"[ERROR] [{timestamp}] {error_msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")
    print(full_msg, file=sys.stderr)

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
        # --- Save and Cancel Buttons ---
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.setMinimumWidth(100)
        self.cancel_btn.setMinimumWidth(100)
        self.save_btn.setStyleSheet("font-weight: bold;")
        self.cancel_btn.setStyleSheet("font-weight: bold;")
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.vlayout.addLayout(btn_layout)
        self.setLayout(self.vlayout)

        # Update leader list when members change
        self.member_list.itemSelectionChanged.connect(self.update_leader_list)
        # Auto-assign creator as leader on save
        self.save_btn.clicked.connect(self.ensure_creator_is_leader)
        self.cancel_btn.clicked.connect(self.go_back_to_dashboard)

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
            error_msg = "No current user context."
            log_error(error_msg)
            QMessageBox.warning(self, "Error", error_msg)
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
            # Validate assigned user ID: must be int and in selected members
            try:
                assigned = int(assigned) if assigned is not None else None
            except Exception:
                assigned = None
            member_ids = [self.member_list.item(i).data(32) for i in range(self.member_list.count()) if self.member_list.item(i).isSelected()]
            if assigned not in member_ids:
                assigned = None
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
            error_msg = "Project name is required."
            log_error(error_msg)
            QMessageBox.warning(self, "Validation Error", error_msg)
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
                # Navigate back to dashboard after successful creation
                self.go_back_to_dashboard()
            else:
                error_msg = "Failed to create project in database."
                log_error(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
        else:
            error_msg = "Database not available."
            log_error(error_msg)
            QMessageBox.warning(self, "Error", error_msg)


    def go_back_to_dashboard(self):
        # Find main window and return to dashboard
        log_event("User navigated back to dashboard (ProjectCreationPage)")
        mw = self.parent()
        # Use QMainWindow type check to avoid circular import
        from PyQt5.QtWidgets import QMainWindow
        while mw and not isinstance(mw, QMainWindow):
            mw = mw.parent()
        if mw and hasattr(mw, "stack") and hasattr(mw, "dashboard"):
            try:
                # Check if dashboard widget is deleted
                if mw.dashboard is None or not isinstance(mw.dashboard, QWidget) or mw.dashboard.parent() is None:
                    raise RuntimeError("Dashboard widget deleted")
                mw.stack.setCurrentWidget(mw.dashboard)
            except Exception:
                # Recreate dashboard if deleted
                mw.dashboard = DashboardView(main_window=mw, user=mw.current_user)
                mw.stack.addWidget(mw.dashboard)
                mw.stack.setCurrentWidget(mw.dashboard)
            log_event("Returned to Dashboard from Project Creation Page")

# Placeholder import for database models/utilities
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
try:
    import db
    # Debug logging: log value and type of db after import
    import sys
    db_type = type(db)
    db_repr = repr(db)
    debug_msg = f"[DEBUG] db module imported: value={db_repr}, type={db_type}"
    print(debug_msg, file=sys.stderr)
    with open("event_log.txt", "a", encoding="utf-8") as f:
        f.write(debug_msg + "\n")
except ImportError as e:
    import sys
    import traceback
    db = None
    error_msg = f"[ERROR] Failed to import db module: {e}"
    tb_str = traceback.format_exc()
    print(error_msg, file=sys.stderr)
    print(tb_str, file=sys.stderr)
    with open("event_log.txt", "a", encoding="utf-8") as f:
        f.write(error_msg + "\n")
        f.write(tb_str + "\n")

LOG_FILE = "event_log.txt"

# (Removed duplicate log_event and log_error definitions; see top of file)

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
        pixmap = QPixmap(user_icon_path)
        if not pixmap.isNull():
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
        logo_path = os.path.join(os.path.dirname(__file__), "..", "images", "logo.jpg")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToHeight(120, Qt.TransformationMode.SmoothTransformation))
        else:
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

        # --- Register Button ---
        # Registration button and dialog removed (broken and not supported)

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

class DashboardCategoryListWidget(QListWidget):
    """Custom QListWidget to support drag-and-drop of subtasks with custom widgets."""
    def __init__(self, category_key, dashboard_view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_key = category_key
        self.dashboard_view = dashboard_view
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)

    def mousePressEvent(self, event):
        self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if hasattr(self, "_drag_start_pos"):
            distance = (event.pos() - self._drag_start_pos).manhattanLength()
            if distance >= QApplication.startDragDistance():
                item = self.itemAt(self._drag_start_pos)
                if item:
                    mime = self.model().mimeData([self.indexFromItem(item)])
                    mime.setData("application/x-subtask-id", str(item.data(32)).encode())
                    drag = QDrag(self)
                    drag.setMimeData(mime)
                    drag.exec_(Qt.MoveAction)
                    return
        super().mouseMoveEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-subtask-id"):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-subtask-id"):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-subtask-id"):
            subtask_id_str = event.mimeData().data("application/x-subtask-id").data().decode()
            subtask_id = None
            if subtask_id_str.startswith("subtask:"):
                try:
                    subtask_id = int(subtask_id_str.split(":", 1)[1])
                except Exception:
                    subtask_id = None
            else:
                try:
                    subtask_id = int(subtask_id_str)
                except Exception:
                    subtask_id = None
            if subtask_id is not None:
                # Find previous category
                prev_category = None
                for cat_key, cat_list in self.dashboard_view.category_lists.items():
                    for i in range(cat_list.count()):
                        item = cat_list.item(i)
                        if item and item.data(32) == f"subtask:{subtask_id}":
                            prev_category = cat_key
                            break
                    if prev_category:
                        break
                # Update backend and log
                if prev_category != self.category_key:
                    if hasattr(self.dashboard_view, "user"):
                        username = getattr(self.dashboard_view.user, "username", "")
                    else:
                        username = ""
                    sub_obj = None
                    for i in range(self.count()):
                        item = self.item(i)
                        if item and item.data(32) == f"subtask:{subtask_id}":
                            sub_obj = item.data(33)
                            break
                    if not sub_obj:
                        # Try to get from previous list
                        prev_list = self.dashboard_view.category_lists.get(prev_category)
                        if prev_list:
                            for i in range(prev_list.count()):
                                item = prev_list.item(i)
                                if item and item.data(32) == f"subtask:{subtask_id}":
                                    sub_obj = item.data(33)
                                    break
                    sub_title = getattr(sub_obj, "title", "") if sub_obj else ""
                    cat_names = {
                        "important_urgent": "Important and Urgent",
                        "urgent": "Urgent",
                        "important": "Important",
                        "other": "Other"
                    }
                    prev_cat_name = cat_names.get(prev_category, prev_category)
                    new_cat_name = cat_names.get(self.category_key, self.category_key)
                    # Update DB
                    if db and hasattr(db, "update_subtask_category"):
                        db.update_subtask_category(subtask_id, self.category_key)
                    log_event(
                        f"Subtask {subtask_id} ('{sub_title}') moved from '{prev_cat_name}' to '{new_cat_name}' by user '{username}'"
                    )
                    self.dashboard_view.load_subtasks()
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
class DashboardSubtaskWidget(QWidget):
    """Dashboard subtask row: always shows status dropdown, click opens details."""
    def __init__(self, subtask, status, parent=None, project_name="N/A", on_status_changed=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QHBoxLayout, QLabel, QComboBox
        self.subtask = subtask
        self.status = status
        self.on_status_changed = on_status_changed
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.title_label = QLabel(f"<b>{getattr(subtask, 'title', '')}</b>")
        self.project_label = QLabel(f"Project: {project_name}")
        deadline_val = getattr(subtask, 'due_date', getattr(subtask, 'deadline', 'N/A'))
        deadline_str = "N/A"
        if deadline_val and deadline_val != "N/A":
            try:
                from datetime import datetime, date
                if isinstance(deadline_val, datetime):
                    deadline_str = deadline_val.date().isoformat()
                elif isinstance(deadline_val, date):
                    deadline_str = deadline_val.isoformat()
                else:
                    deadline_str = str(deadline_val).split()[0]
            except Exception:
                deadline_str = str(deadline_val)
        self.deadline_label = QLabel(f"Deadline: {deadline_str}")
        self.status_combo = QComboBox(self)
        self.status_combo.addItems(["Not Yet Started", "In Progress", "Completed"])
        self.status_combo.setCurrentText(self.status)
        self.status_combo.setMinimumWidth(140)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.project_label)
        self.layout.addWidget(self.deadline_label)
        self.layout.addWidget(self.status_combo)
        self.setLayout(self.layout)
        self.status_combo.activated.connect(self.handle_status_change)
        self.setCursor(Qt.PointingHandCursor)

    def handle_status_change(self, idx):
        new_status = self.status_combo.currentText()
        self.status = new_status
        if self.on_status_changed:
            self.on_status_changed(new_status)

class CalendarTabWidget(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        layout = QVBoxLayout()
        # Add "week" heading above the calendar's week numbers
        week_heading = QLabel("week")
        week_heading.setAlignment(Qt.AlignmentFlag.AlignLeft)
        week_heading.setStyleSheet("font-weight: bold; margin-left: 32px;")
        layout.addWidget(week_heading)
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
        """
        Populate the calendar with all deadlines relevant to the user:
        - Project deadlines (always)
        - All tasks assigned to the user (even if they have subtasks)
        - All subtasks assigned to the user
        - Public holidays and personal time off
        """
        self.events_by_date = {}
        if db and self.user:
            # --- Projects the user is a member of ---
            if hasattr(db, "get_user_projects"):
                projects, _ = db.get_user_projects(self.user.id)
                for project in projects:
                    # Project deadline
                    deadline = getattr(project, "deadline", None)
                    if deadline:
                        self._add_event(deadline, f"Project Deadline: {getattr(project, 'name', '')}")
            # --- Tasks assigned to the user ---
            if hasattr(db, "get_user_tasks"):
                tasks = db.get_user_tasks(self.user.id)
                for task in tasks:
                    t_deadline = getattr(task, "deadline", getattr(task, "due_date", None))
                    pname = getattr(task, "project_name", "")
                    if t_deadline:
                        self._add_event(t_deadline, f"Task: {getattr(task, 'title', '')} (Project: {pname})")
            # --- Subtasks assigned to the user ---
            if hasattr(db, "get_user_subtasks"):
                subtasks = db.get_user_subtasks(self.user.id)
                for sub in subtasks:
                    s_deadline = getattr(sub, "due_date", getattr(sub, "deadline", None))
                    pname = getattr(sub, "project_name", "")
                    tname = getattr(sub, "parent_task_title", "")
                    label = f"Subtask: {getattr(sub, 'title', '')}"
                    if tname:
                        label += f" (Task: {tname})"
                    if pname:
                        label += f" (Project: {pname})"
                    if s_deadline:
                        self._add_event(s_deadline, label)
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
        # Ensure eventFilter is installed on self so drop events are caught
        self.installEventFilter(self)
        from PyQt5.QtWidgets import QGridLayout, QFrame, QMenu, QAction
        from PyQt5.QtGui import QIcon, QPixmap, QCursor
        from PyQt5.QtCore import QDateTime

        self.user = user
        # Ensure main_window is set, fallback to parent chain if not provided
        if main_window is not None:
            self.main_window = main_window
        else:
            mw = self.parent()
            from PyQt5.QtWidgets import QMainWindow
            while mw and not isinstance(mw, QMainWindow):
                mw = mw.parent()
            self.main_window = mw

        # --- Tabs for Dashboard, Calendar, Members, and Event Log ---
        self.tabs = QTabWidget()
        self.dashboard_tab = QWidget()
        self.calendar_tab = CalendarTabWidget(user=self.user)
        self.members_tab = QWidget()
        self.event_log_tab = EventLogView()

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
            cat_list = DashboardCategoryListWidget(cat_key, self)
            cat_list.setObjectName(cat_key)
            cat_list.setStyleSheet("QListWidget::item:selected { background: #e0f7fa; } QListWidget { border: 1px solid #bbb; }")
            subtask_col.addWidget(cat_list)
            self.category_lists[cat_key] = cat_list
        subtask_col.addStretch(1)

        # --- Column 3: Messages ---
        message_col = QVBoxLayout()
        message_col.addWidget(QLabel("<b>Messages</b>"))
        self.message_list = QListWidget()
        message_col.addWidget(self.message_list)
        self.refresh_messages_btn = QPushButton("Refresh Messages")
        message_col.addWidget(self.refresh_messages_btn)
        self.send_message_btn = QPushButton("Send Message")
        message_col.addWidget(self.send_message_btn)
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
        if not icon_pixmap.isNull():
            self.user_icon_btn.setIcon(QIcon(icon_pixmap))
        else:
            self.user_icon_btn.setText("User")
        self.user_icon_btn.setIconSize(QSize(32, 32))
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
        self.tabs.addTab(self.members_tab, "Members & Users")
        self.tabs.addTab(self.event_log_tab, "Event Log")

        # --- Setup Members Tab ---
        members_layout = QVBoxLayout()

        # Refresh event log tab on tab change
        def refresh_event_log_on_tab(idx):
            if self.tabs.tabText(idx) == "Event Log":
                self.event_log_tab.load_log()
        self.tabs.currentChanged.connect(refresh_event_log_on_tab)
        members_layout.addWidget(QLabel("<b>Members</b>"))
        self.members_list = QListWidget()
        members_layout.addWidget(self.members_list)
        members_layout.addWidget(QLabel("<b>Registered Users</b>"))
        self.users_list = QListWidget()
        members_layout.addWidget(self.users_list)
        self.members_tab.setLayout(members_layout)
        self.load_members_and_users()

    def load_members_and_users(self):
        self.members_list.clear()
        self.users_list.clear()
        if db:
            # Members: users who are part of any project
            member_ids = set()
            with db.SessionLocal() as session:
                if hasattr(db, "Project") and hasattr(db, "User"):
                    projects = session.query(db.Project).all()
                    for project in projects:
                        if hasattr(project, "members"):
                            for m in project.members:
                                member_ids.add(getattr(m, "id", None))
                    members = session.query(db.User).filter(db.User.id.in_(member_ids)).all() if member_ids else []
                    for m in members:
                        self.members_list.addItem(f"{m.username} ({getattr(m, 'role', '')})")
                    # Registered users: all users
                    users = session.query(db.User).all()
                    for u in users:
                        self.users_list.addItem(f"{u.username} ({getattr(u, 'role', '')})")

        # --- User side menu ---
        self.user_icon_btn.clicked.connect(self.show_user_side_menu)

        # --- Connect signals and load data ---
        self.add_project_btn.clicked.connect(self.log_and_navigate_to_project_creation)
        self.project_list.itemClicked.connect(self.log_and_handle_project_click)
        for cat_list in self.category_lists.values():
            cat_list.itemDoubleClicked.connect(self.log_and_show_subtask_details)
        self.load_projects()
        self.load_subtasks()
        self.load_messages()
        self.refresh_messages_btn.clicked.connect(self.log_and_refresh_messages)
        self.send_message_btn.clicked.connect(self.log_and_show_send_message_dialog)

    def log_and_navigate_to_project_creation(self):
        log_event("User clicked 'Create Project' button")
        self.navigate_to_project_creation()
    # Removed navigate_to_project_detail to fix recursion error
    def log_and_handle_project_click(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        project_obj = item.data(Qt.ItemDataRole.UserRole + 1) if item is not None else None
        log_event(f"User selected project from dashboard: id={project_id}, name={item.text() if item else ''}")
        # Debug: log main_window and project_obj before navigation
        log_event(f"DEBUG: main_window={self.main_window}, project_obj={project_obj}")
        # Navigate to project detail page directly using the stored project object
        if db and self.user and project_id is not None and self.main_window and project_obj is not None:
            log_event("DEBUG: Calling show_project_detail_page")
            self.main_window.show_project_detail_page(project_obj)
        else:
            log_event(f"DEBUG: Navigation not performed. db={db}, user={self.user}, project_id={project_id}, main_window={self.main_window}, project_obj={project_obj}")

    def log_and_show_subtask_details(self, item):
        # Try to get subtask title from the custom widget if item.text() is empty
        title = ""
        if item:
            title = item.text()
            if not title:
                parent_list = item.listWidget() if hasattr(item, "listWidget") else None
                if parent_list:
                    widget = parent_list.itemWidget(item)
                    if widget and hasattr(widget, "title_label"):
                        title = widget.title_label.text()
        log_event(f"User opened subtask details: item={title}")
        self.show_subtask_details(item)

    def log_and_refresh_messages(self):
        log_event("User clicked 'Refresh Messages'")
        self.load_messages()

    def log_and_show_send_message_dialog(self):
        log_event("User clicked 'Send Message'")
        self.show_send_message_dialog()

    def handle_project_click(self, item):
        # Get project details and navigate to detail page
        if db and self.user:
            project_id = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
            if project_id is not None:
                projects, _ = db.get_user_projects(self.user.id)
                selected_project = next((p for p in projects if getattr(p, "id", None) == project_id), None)
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
                item = QListWidgetItem(f"{project.name}")
                item.setData(Qt.ItemDataRole.UserRole, getattr(project, "id", None))
                item.setData(Qt.ItemDataRole.UserRole + 1, project)  # Store the full project object
                self.project_list.addItem(item)

    def navigate_to_project_creation(self):
        if self.main_window:
            self.main_window.show_project_creation_page()

    def load_subtasks(self):
        """
        Populate the dashboard's subtask columns for the current user.
        Each subtask always shows a status dropdown. Clicking opens details.
        """
        # Clear all categories
        for cat_list in self.category_lists.values():
            cat_list.clear()
        # Subtasks assigned to the user
        if db and self.user and hasattr(db, "get_user_subtasks"):
            subtasks = db.get_user_subtasks(self.user.id)
            for sub in subtasks:
                cat = getattr(sub, "category", "other")
                if cat not in self.category_lists:
                    cat = "other"
                # Fetch project name for this subtask
                project_name = "N/A"
                try:
                    task_id = getattr(sub, "task_id", None)
                    if not isinstance(task_id, int):
                        if task_id is not None:
                            if hasattr(task_id, "id"):
                                task_id = task_id.id
                            else:
                                try:
                                    task_id = int(task_id)
                                except Exception:
                                    task_id = None
                        else:
                            task_id = None
                    if isinstance(task_id, int) and hasattr(db, "get_task_by_id"):
                        parent_task = db.get_task_by_id(task_id)
                        if parent_task and hasattr(parent_task, "project_id") and hasattr(db, "get_project_by_id"):
                            project_id = getattr(parent_task, "project_id", None)
                            if not isinstance(project_id, int):
                                if project_id is not None:
                                    if hasattr(project_id, "id"):
                                        project_id = project_id.id
                                    else:
                                        try:
                                            project_id = int(project_id)
                                        except Exception:
                                            project_id = None
                                else:
                                    project_id = None
                            if isinstance(project_id, int):
                                project = db.get_project_by_id(project_id)
                                if project and hasattr(project, "name"):
                                    pname = getattr(project, "name", None)
                                    if pname is not None:
                                        project_name = str(pname)
                except Exception:
                    pass
                # Use empty string for item text to avoid overlay, rely on custom widget for display
                item = QListWidgetItem("")
                item.setData(32, f"subtask:{sub.id}")
                item.setData(33, sub)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                db_status = getattr(sub, "status", None)
                if db_status in (None, "", "pending", "not yet started"):
                    ui_status = "Not Yet Started"
                elif db_status == "in_progress":
                    ui_status = "In Progress"
                elif db_status == "completed":
                    ui_status = "Completed"
                else:
                    ui_status = str(db_status)
                item.setData(34, ui_status)
                # Always show status dropdown, and connect click to details
                def make_status_changed(item_ref, sub_ref):
                    def on_status_changed(new_status):
                        item_ref.setData(34, new_status)
                        # Map UI status to DB status
                        if new_status == "Not Yet Started":
                            db_status_val = "not yet started"
                        elif new_status == "In Progress":
                            db_status_val = "in_progress"
                        elif new_status == "Completed":
                            db_status_val = "completed"
                        else:
                            db_status_val = new_status
                        if hasattr(db, "update_subtask_status"):
                            try:
                                db.update_subtask_status(sub_ref.id, db_status_val)
                            except Exception:
                                pass
                        log_event(f"Subtask {sub_ref.id} status changed to '{db_status_val}'")
                        # Refresh event log and dashboard
                        if hasattr(self, "event_log_tab"):
                            self.event_log_tab.load_log()
                        self.load_subtasks()
                        if hasattr(self, "main_window") and hasattr(self.main_window, "project_detail_page") and self.main_window.project_detail_page:
                            self.main_window.project_detail_page.load_tasks()
                    return on_status_changed
                def make_on_click(item_ref):
                    def on_click():
                        self.show_subtask_details(item_ref)
                    return on_click
                widget = DashboardSubtaskWidget(
                    sub, ui_status, project_name=str(project_name) if project_name else "N/A",
                    on_status_changed=make_status_changed(item, sub)
                )
                self.category_lists[cat].addItem(item)
                self.category_lists[cat].setItemWidget(item, widget)
        # Remove all task display from dashboard (only subtasks shown)
        # Connect single click to open details
        for cat_list in self.category_lists.values():
            try:
                cat_list.itemClicked.disconnect()
            except Exception:
                pass
            def make_item_clicked_handler(cat_list_ref):
                def handler(item):
                    # Only handle if item is a subtask (data(32) starts with "subtask:")
                    if item is None or not item.data(32):
                        return
                    subtask_id_str = item.data(32)
                    if isinstance(subtask_id_str, str) and subtask_id_str.startswith("subtask:"):
                        cat_list_ref.setCurrentItem(item)
                        self.show_subtask_details(item)
                return handler
            cat_list.itemClicked.connect(make_item_clicked_handler(cat_list))

    # inline_edit_subtask_status is now obsolete and not used

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
                        subtask_id_raw = item.data(32)
                        # Extract numeric subtask ID if in "subtask:123" format
                        subtask_id = None
                        if isinstance(subtask_id_raw, str) and subtask_id_raw.startswith("subtask:"):
                            try:
                                subtask_id = int(subtask_id_raw.split(":", 1)[1])
                            except Exception:
                                subtask_id = subtask_id_raw
                        else:
                            subtask_id = subtask_id_raw
                        # Find previous category
                        prev_category = None
                        for prev_key, prev_list in self.category_lists.items():
                            if prev_key != cat_key:
                                for i in range(prev_list.count()):
                                    prev_item = prev_list.item(i)
                                    prev_id = prev_item.data(32) if prev_item else None
                                    if prev_id == subtask_id_raw:
                                        prev_category = prev_key
                                        break
                                if prev_category:
                                    break
                        # Only log and update if category changed
                        if prev_category != cat_key:
                            # Update category in DB if possible
                            if db and hasattr(db, "update_subtask_category"):
                                # Only call if subtask_id is int
                                if isinstance(subtask_id, int):
                                    db.update_subtask_category(subtask_id, cat_key)
                            # Log event with timestamp, previous and new category, and subtask title
                            timestamp = datetime.datetime.now().isoformat()
                            username = getattr(self.user, 'username', '')
                            sub_obj = item.data(33)
                            sub_title = getattr(sub_obj, "title", "")
                            log_event(
                                f"[{timestamp}] Subtask {subtask_id} ('{sub_title}') moved from '{prev_category}' to '{cat_key}' by user '{username}'"
                            )
                    break
            # Log event before reload, using readable category names
            cat_names = {
                "important_urgent": "Important and Urgent",
                "urgent": "Urgent",
                "important": "Important",
                "other": "Other"
            }
            prev_cat_name = cat_names.get(prev_category, prev_category)
            new_cat_name = cat_names.get(cat_key, cat_key)
            log_event(
                f"Subtask {subtask_id} ('{sub_title}') moved from '{prev_cat_name}' to '{new_cat_name}' by user '{username}'"
            )
            self.load_subtasks()
        return super().eventFilter(obj, event)

    def show_send_message_dialog(self):
        if not db or not self.user:
            QMessageBox.warning(self, "Error", "Database or user context not available.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Send Message")
        layout = QVBoxLayout(dialog)
        user_combo = QComboBox()
        # Populate with all users except self
        with db.SessionLocal() as session:
            users = session.query(db.User).all()
            for u in users:
                if getattr(u, "id", None) != getattr(self.user, "id", None):
                    user_combo.addItem(getattr(u, "username", str(u)), getattr(u, "id", None))
        layout.addWidget(QLabel("Recipient:"))
        layout.addWidget(user_combo)
        msg_edit = QTextEdit()
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(msg_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        def send():
            recipient_id = user_combo.currentData()
            content = msg_edit.toPlainText().strip()
            sender_id = getattr(self.user, "id", None)
            if sender_id is None:
                error_msg = "User ID is missing."
                log_error(error_msg)
                QMessageBox.warning(dialog, "Error", error_msg)
                return
            if not recipient_id or not content:
                error_msg = "Recipient and message are required."
                log_error(error_msg)
                QMessageBox.warning(dialog, "Validation Error", error_msg)
                return
            result = db.create_message(sender_id, recipient_id, content)
            if result:
                QMessageBox.information(dialog, "Success", "Message sent.")
                self.load_messages()
                dialog.accept()
            else:
                error_msg = "Failed to send message."
                log_error(error_msg)
                QMessageBox.warning(dialog, "Error", error_msg)
        button_box.accepted.connect(send)
        button_box.rejected.connect(dialog.reject)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_subtask_details(self, item):
        # Show subtask details page in main window stack
        log_event("DEBUG: ENTER show_subtask_details")
        try:
            subtask_id = item.data(32)
            log_event(f"DEBUG: show_subtask_details called with item.data(32)={subtask_id}")
            if isinstance(subtask_id, str) and subtask_id.startswith("subtask:"):
                try:
                    subtask_id_int = int(subtask_id.split(":", 1)[1])
                except Exception as e:
                    log_event(f"DEBUG: Failed to parse subtask_id from {subtask_id}: {e}")
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Error", "Invalid subtask ID.")
                    return
                subtask_id = subtask_id_int
            log_event(f"DEBUG: Parsed subtask_id={subtask_id}")
            sub = db.get_subtask_by_id(subtask_id)
            log_event(f"DEBUG: get_subtask_by_id({subtask_id}) returned: {sub}")
            if not sub:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "Subtask not found.")
                return
            # Find parent task and project
            parent_task = None
            project = None
            task_id = getattr(sub, "task_id", None)
            if task_id and hasattr(db, "get_task_by_id"):
                parent_task = db.get_task_by_id(task_id)
                if parent_task and hasattr(parent_task, "project_id") and hasattr(db, "get_project_by_id"):
                    project = db.get_project_by_id(getattr(parent_task, "project_id", None))
                # Assigned users
                assigned_to = getattr(sub, "assigned_to", None)
                assigned_names = ""
                if assigned_to:
                    if isinstance(assigned_to, (list, tuple)):
                        names = []
                        for uid in assigned_to:
                            if db and hasattr(db, "User") and hasattr(db, "SessionLocal"):
                                with db.SessionLocal() as session:
                                    user = session.query(db.User).filter_by(id=uid).first()
                                    if user:
                                        names.append(getattr(user, "username", str(uid)))
                        assigned_names = ", ".join(names)
                    else:
                        if db and hasattr(db, "User") and hasattr(db, "SessionLocal"):
                            with db.SessionLocal() as session:
                                user = session.query(db.User).filter_by(id=assigned_to).first()
                                if user:
                                    assigned_names = getattr(user, "username", str(assigned_to))
                                else:
                                    assigned_names = str(assigned_to)
                else:
                    assigned_names = "Unassigned"
                # Deadline
                deadline = getattr(sub, "due_date", getattr(sub, "deadline", "N/A"))
                # Subtask name
                subtask_name = getattr(sub, "title", "")
                # Project name
                project_name = getattr(project, "name", "N/A") if project else "N/A"
                # Parent task name
                parent_task_name = getattr(parent_task, "title", "N/A") if parent_task else "N/A"
                log_event("DEBUG: PRE-NAVIGATION BLOCK")
                # Show details page
                mw = getattr(self, "main_window", None)
                from PyQt5.QtWidgets import QMainWindow, QMessageBox
                log_event(f"DEBUG: show_subtask_details direct main_window={mw}, type={type(mw)}")
                if mw and hasattr(mw, "stack"):
                    log_event(f"DEBUG: mw.stack={getattr(mw, 'stack', None)}, type={type(getattr(mw, 'stack', None))}")
                    mw.stack.addWidget(SubtaskDetailPage(
                        subtask_name=subtask_name,
                        assigned_names=assigned_names,
                        project_name=project_name,
                        parent_task_name=parent_task_name,
                        deadline=deadline,
                        parent=mw
                    ))
                    mw.stack.setCurrentIndex(mw.stack.count() - 1)
                else:
                    # Fallback: try parent traversal
                    parent = self.parent() if hasattr(self, "parent") else None
                    while parent and not isinstance(parent, QMainWindow):
                        parent = parent.parent()
                    log_event(f"DEBUG: show_subtask_details fallback parent={parent}, type={type(parent)}")
                    if parent and hasattr(parent, "stack"):
                        parent.stack.addWidget(SubtaskDetailPage(
                            subtask_name=subtask_name,
                            assigned_names=assigned_names,
                            project_name=project_name,
                            parent_task_name=parent_task_name,
                            deadline=deadline,
                            parent=parent
                        ))
                        parent.stack.setCurrentIndex(parent.stack.count() - 1)
                    else:
                        log_event(f"DEBUG: MainWindow or stack not found in fallback, parent={parent}, has_stack={hasattr(parent, 'stack')}")
                        QMessageBox.warning(self, "Navigation Error", "Could not find main window or stack for navigation.")
        except Exception as e:
            log_event(f"DEBUG: Exception in show_subtask_details: {e}")
            import traceback
            log_event(traceback.format_exc())

class SubtaskDetailPage(QWidget):
    def __init__(self, subtask_name, assigned_names, project_name, parent_task_name, deadline, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import (
            QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy,
            QFileDialog, QListWidget, QListWidgetItem, QMessageBox, QDialog, QDialogButtonBox
        )
        import shutil
        import re
        import uuid
        import platform
        import subprocess

        # --- DB import for file association ---
        # Use global db module (already imported at top)

        self._subtask_name = subtask_name
        self._assigned_names = assigned_names
        self._project_name = project_name
        self._parent_task_name = parent_task_name
        self._deadline = deadline
        self._parent = parent

        # --- Subtask context: get subtask, task, project IDs ---
        self._subtask_id = None
        self._task_id = None
        self._project_id = None
        self._current_user_id = None

        # Get current user ID from parent if available
        if parent and hasattr(parent, "main_window") and hasattr(parent.main_window, "current_user"):
            user = getattr(parent.main_window, "current_user", None)
            if user and hasattr(user, "id"):
                self._current_user_id = user.id

        # Get subtask, task, project IDs from db using subtask_name and parent_task_name/project_name
        if db and hasattr(db, "SessionLocal"):
            with db.SessionLocal() as session:
                subtask = None
                if subtask_name and parent_task_name and project_name:
                    project = getattr(db, "Project", None)
                    task_model = getattr(db, "Task", None)
                    subtask_model = getattr(db, "Subtask", None)
                    if project and task_model and subtask_model:
                        project_obj = session.query(project).filter(project.name == project_name).first()
                        if project_obj:
                            self._project_id = project_obj.id
                            task_obj = session.query(task_model).filter(
                                task_model.title == parent_task_name,
                                task_model.project_id == project_obj.id
                            ).first()
                            if task_obj:
                                self._task_id = task_obj.id
                                subtask_obj = session.query(subtask_model).filter(
                                    subtask_model.title == subtask_name,
                                    subtask_model.task_id == task_obj.id
                                ).first()
                                if subtask_obj:
                                    self._subtask_id = subtask_obj.id

        layout = QVBoxLayout()
        # Top row: header left, back button right
        top_row = QHBoxLayout()
        header = QLabel(f"<h2>{subtask_name}</h2>")
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_row.addWidget(header)
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(60, 28)
        back_btn.setStyleSheet("font-size:10pt; padding:2px 8px;")
        top_row.addStretch(1)
        top_row.addWidget(back_btn)
        layout.addLayout(top_row)
        # Row of details
        row = QHBoxLayout()
        row.addWidget(QLabel(f"<b>Assigned:</b> {assigned_names}"))
        row.addWidget(QLabel(f"<b>Project:</b> {project_name}"))
        row.addWidget(QLabel(f"<b>Parent Task:</b> {parent_task_name}"))
        row.addWidget(QLabel(f"<b>Deadline:</b> {deadline}"))
        row_widget = QWidget()
        row_widget.setLayout(row)
        layout.addWidget(row_widget)

        # --- LibreOffice Integration UI ---
        file_btn_row = QHBoxLayout()
        self.create_odt_btn = QPushButton("New Writer (.odt)")
        self.create_ods_btn = QPushButton("New Calc (.ods)")
        self.create_odp_btn = QPushButton("New Impress (.odp)")
        self.upload_btn = QPushButton("Upload LibreOffice File")
        file_btn_row.addWidget(self.create_odt_btn)
        file_btn_row.addWidget(self.create_ods_btn)
        file_btn_row.addWidget(self.create_odp_btn)
        file_btn_row.addWidget(self.upload_btn)
        layout.addLayout(file_btn_row)

        # File list
        self.file_list = QListWidget()
        layout.addWidget(QLabel("LibreOffice Files:"))
        layout.addWidget(self.file_list)

        # --- VCS Panel ---
        vcs_panel = QVBoxLayout()
        self.vcs_group = QGroupBox("Version Control")
        vcs_panel_layout = QVBoxLayout()
        self.vcs_status_label = QLabel("Status: -")
        vcs_panel_layout.addWidget(self.vcs_status_label)
        self.vcs_history_list = QListWidget()
        vcs_panel_layout.addWidget(QLabel("History:"))
        vcs_panel_layout.addWidget(self.vcs_history_list)
        self.vcs_diff_btn = QPushButton("Show Diff")
        self.vcs_revert_btn = QPushButton("Revert to Selected")
        self.vcs_commit_btn = QPushButton("Commit Changes")
        self.vcs_edit_btn = QPushButton("Edit in App")
        # self.vcs_open_btn = QPushButton("Open in LibreOffice")  # Disabled external editing
        vcs_panel_layout.addWidget(self.vcs_diff_btn)
        vcs_panel_layout.addWidget(self.vcs_revert_btn)
        vcs_panel_layout.addWidget(self.vcs_commit_btn)
        vcs_panel_layout.addWidget(self.vcs_edit_btn)
        # vcs_panel_layout.addWidget(self.vcs_open_btn)  # Disabled external editing
        self.vcs_diff_output = QTextEdit()
        self.vcs_diff_output.setReadOnly(True)
        vcs_panel_layout.addWidget(QLabel("Diff Output:"))
        vcs_panel_layout.addWidget(self.vcs_diff_output)
        self.vcs_group.setLayout(vcs_panel_layout)
        vcs_panel.addWidget(self.vcs_group)

        # Add VCS panel to the main layout (right side)
        main_hbox = QHBoxLayout()
        main_hbox.addLayout(layout, 3)
        main_hbox.addLayout(vcs_panel, 2)
        self.setLayout(main_hbox)

        # --- File logic state ---
        self._file_dir = None  # Will be set by backend logic

        # --- Connect buttons ---
        self.create_odt_btn.clicked.connect(lambda: self._handle_create_libreoffice_file("odt"))
        self.create_ods_btn.clicked.connect(lambda: self._handle_create_libreoffice_file("ods"))
        self.create_odp_btn.clicked.connect(lambda: self._handle_create_libreoffice_file("odp"))
        self.upload_btn.clicked.connect(self._handle_upload_libreoffice_file)
        self.file_list.itemDoubleClicked.connect(self._handle_open_libreoffice_file)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.vcs_edit_btn.clicked.connect(self._handle_edit_in_app)
        self.file_list.customContextMenuRequested.connect(self._show_file_context_menu)
        self.file_list.currentItemChanged.connect(self._on_file_selected)

        self.vcs_diff_btn.clicked.connect(self._on_vcs_diff)
        self.vcs_revert_btn.clicked.connect(self._on_vcs_revert)
        self.vcs_commit_btn.clicked.connect(self._on_vcs_commit)
        # self.vcs_open_btn.clicked.connect(self._on_vcs_open)  # Disabled external editing

        # --- Load file list on init ---
        self._refresh_file_list()

        def go_back():
            mw = self.parent()
            from PyQt5.QtWidgets import QMainWindow
            while mw and not isinstance(mw, QMainWindow):
                mw = mw.parent()
            if mw and hasattr(mw, "stack") and mw.stack.count() > 1:
                mw.stack.setCurrentIndex(0)
        back_btn.clicked.connect(go_back)

    # --- VCS UI Methods ---

    def _on_file_selected(self, current, previous):
        if not current:
            self._current_file_path = None
            self.vcs_status_label.setText("Status: -")
            self.vcs_history_list.clear()
            self.vcs_diff_output.clear()
            return
        import os
        fname = current.text()
        self._current_file_path = os.path.join(self._file_dir, fname)
        self._update_vcs_status_and_history()

    def _handle_edit_in_app(self):
        """Open the selected ODF file in the ODFEditorWidget."""
        from odf_editor_widget import ODFEditorWidget
        from PyQt5.QtWidgets import QMessageBox

        item = self.file_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No File Selected", "Please select a file to edit.")
            return

        import os
        fname = item.text()
        file_path = os.path.join(self._file_dir, fname)
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"File does not exist:\n{file_path}")
            return

        # Launch the ODF editor as a dialog
        editor = ODFEditorWidget(odf_path=file_path, parent=self)
        editor.setWindowTitle(f"Editing: {fname}")
        editor.setMinimumSize(800, 600)
        editor.show()

    def _update_vcs_status_and_history(self):
        from vcs import VCS
        import os
        self.vcs_status_label.setText("Status: ...")
        self.vcs_history_list.clear()
        self.vcs_diff_output.clear()
        if not self._current_file_path or not os.path.exists(self._current_file_path):
            self.vcs_status_label.setText("Status: File not found")
            return
        try:
            vcs = VCS(self._file_dir)
            # Status: check if file is latest/modified/uncommitted
            rel_path = os.path.relpath(self._current_file_path, self._file_dir)
            git_status = vcs.repo.git.status("--porcelain", rel_path)
            if not git_status:
                self.vcs_status_label.setText("Status: Latest (Committed)")
            elif git_status.startswith(" M"):
                self.vcs_status_label.setText("Status: Modified (Uncommitted)")
            else:
                self.vcs_status_label.setText(f"Status: {git_status.strip()}")
            # History
            history = vcs.get_history(self._current_file_path)
            self._vcs_history = history
            for h in history:
                item = QListWidgetItem(f"{h['timestamp']} | {h['author']} | {h['message']}")
                item.setData(32, h["commit_hash"])
                self.vcs_history_list.addItem(item)
        except Exception as e:
            self.vcs_status_label.setText(f"Status: Error: {e}")

    def _on_vcs_diff(self):
        # Show diff between two selected commits
        selected = self.vcs_history_list.selectedItems()
        if len(selected) != 2:
            self.vcs_diff_output.setPlainText("Select two commits to diff.")
            return
        commit1 = selected[0].data(32)
        commit2 = selected[1].data(32)
        from vcs import VCS
        try:
            vcs = VCS(self._file_dir)
            diff = vcs.get_diff(self._current_file_path, commit1, commit2)
            self.vcs_diff_output.setPlainText(diff)
        except Exception as e:
            self.vcs_diff_output.setPlainText(f"Diff error: {e}")

    def _on_vcs_revert(self):
        # Revert file to selected commit
        selected = self.vcs_history_list.selectedItems()
        if len(selected) != 1:
            self.vcs_diff_output.setPlainText("Select one commit to revert to.")
            return
        commit = selected[0].data(32)
        from vcs import VCS
        try:
            vcs = VCS(self._file_dir)
            vcs.revert_file(self._current_file_path, commit)
            self._update_vcs_status_and_history()
            self.vcs_diff_output.setPlainText(f"Reverted to {commit}.")
        except Exception as e:
            self.vcs_diff_output.setPlainText(f"Revert error: {e}")

    def _on_vcs_commit(self):
        # Commit current file changes
        from vcs import VCS
        from PyQt5.QtWidgets import QInputDialog
        try:
            vcs = VCS(self._file_dir)
            author = str(self._current_user_id)
            msg, ok = QInputDialog.getText(self, "Commit Message", "Enter commit message:")
            if not ok or not msg.strip():
                return
            vcs.add_and_commit(self._current_file_path, author, msg.strip())
            self._update_vcs_status_and_history()
            self.vcs_diff_output.setPlainText("Committed changes.")
        except Exception as e:
            self.vcs_diff_output.setPlainText(f"Commit error: {e}")

    # def _on_vcs_open(self):
    #     # Disabled: external editing not allowed.
    #     pass

    # --- LibreOffice Integration Methods ---

    def _get_file_dir(self):
        import os
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "files"))
        dir_path = os.path.join(
            base_dir,
            str(self._project_id) if self._project_id else "unknown_project",
            str(self._task_id) if self._task_id else "unknown_task",
            str(self._subtask_id) if self._subtask_id else "unknown_subtask"
        )
        os.makedirs(dir_path, exist_ok=True)
        self._file_dir = dir_path
        return dir_path

    def _sanitize_filename(self, filename):
        import re
        filename = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
        return filename

    def _unique_filename(self, filename):
        import os
        dir_path = self._get_file_dir()
        base, ext = os.path.splitext(filename)
        candidate = filename
        i = 1
        while os.path.exists(os.path.join(dir_path, candidate)):
            candidate = f"{base}_{i}{ext}"
            i += 1
        return candidate

    def _validate_libreoffice_filetype(self, filename):
        allowed = [".odt", ".ods", ".odp"]
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed

    def _refresh_file_list(self):
        # List all LibreOffice files for this subtask from DB
        self._get_file_dir()
        self.file_list.clear()
        if not self._project_id or not self._subtask_id:
            return
        files = db.get_files(self._project_id, subtask_id=self._subtask_id)
        for f in files:
            if self._validate_libreoffice_filetype(f.filename):
                item = QListWidgetItem(f.filename)
                item.setData(32, f.id)
                self.file_list.addItem(item)

    def _handle_create_libreoffice_file(self, ext):
        import os
        import datetime
        self._get_file_dir()
        name_map = {"odt": "NewDocument.odt", "ods": "NewSpreadsheet.ods", "odp": "NewPresentation.odp"}
        filename = self._unique_filename(name_map[ext])
        file_path = os.path.join(self._file_dir, filename)
        # Create empty file
        with open(file_path, "wb") as f:
            f.write(b"")
        # Register in DB
        if self._project_id and self._subtask_id and self._current_user_id:
            db.create_file(
                project_id=self._project_id,
                filename=filename,
                filepath=file_path,
                uploaded_by=self._current_user_id,
                description=None,
                task_id=self._task_id,
                subtask_id=self._subtask_id
            )
            # --- VCS Integration ---
            try:
                from vcs import VCS
                project_dir = self._get_file_dir()
                vcs = VCS(project_dir)
                author = str(self._current_user_id)
                vcs.add_and_commit(file_path, author, f"Initial commit for {filename}")
            except Exception as e:
                log_error(f"VCS error (create): {e}")
        # Open the new file in the in-app ODF editor
        from odf_editor_widget import ODFEditorWidget
        editor = ODFEditorWidget(odf_path=file_path, parent=self)
        editor.setWindowTitle(f"Editing: {filename}")
        editor.setMinimumSize(800, 600)
        editor.show()
        self._refresh_file_list()

    def _handle_upload_libreoffice_file(self):
        import os
        import shutil
        self._get_file_dir()
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilters(["LibreOffice Files (*.odt *.ods *.odp)"])
        if dlg.exec_():
            selected = dlg.selectedFiles()
            if not selected:
                return
            src = selected[0]
            fname = os.path.basename(src)
            fname = self._sanitize_filename(fname)
            if not self._validate_libreoffice_filetype(fname):
                QMessageBox.warning(self, "Invalid File", "Only .odt, .ods, .odp files are allowed.")
                return
            fname = self._unique_filename(fname)
            dst = os.path.join(self._file_dir, fname)
            if os.path.exists(dst):
                QMessageBox.warning(self, "File Exists", "A file with this name already exists.")
                return
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to upload file: {e}")
                return
            # Register in DB
            if self._project_id and self._subtask_id and self._current_user_id:
                db.create_file(
                    project_id=self._project_id,
                    filename=fname,
                    filepath=dst,
                    uploaded_by=self._current_user_id,
                    description=None,
                    task_id=self._task_id,
                    subtask_id=self._subtask_id
                )
            # --- VCS Integration ---
            try:
                from vcs import VCS
                project_dir = self._get_file_dir()
                vcs = VCS(project_dir)
                author = str(self._current_user_id)
                vcs.add_and_commit(dst, author, f"Upload {fname}")
            except Exception as e:
                log_error(f"VCS error (upload): {e}")
            self._refresh_file_list()

    def _handle_open_libreoffice_file(self, item):
        # Disabled: external editing not allowed. Use in-app editor instead.
        from odf_editor_widget import ODFEditorWidget
        from PyQt5.QtWidgets import QMessageBox
        import os
        file_id = item.data(32)
        file_path = None
        if file_id:
            f = db.get_file_by_id(file_id)
            if f:
                file_path = f.filepath
        if not file_path:
            file_path = os.path.join(self._file_dir, item.text())
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"File does not exist:\n{file_path}")
            return
        editor = ODFEditorWidget(odf_path=file_path, parent=self)
        editor.setWindowTitle(f"Editing: {os.path.basename(file_path)}")
        editor.setMinimumSize(800, 600)
        editor.show()

    # def _launch_libreoffice(self, file_path):
    #     # Disabled: external editing not allowed.
    #     pass

    def _show_file_context_menu(self, pos):
        from PyQt5.QtWidgets import QMenu
        item = self.file_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        # open_action = menu.addAction("Open")  # Disabled external editing
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.file_list.mapToGlobal(pos))
        # if action == open_action:
        #     self._handle_open_libreoffice_file(item)
        if action == delete_action:
            self._handle_delete_libreoffice_file(item)

    def _handle_delete_libreoffice_file(self, item):
        import os
        from PyQt5.QtWidgets import QMessageBox
        file_id = item.data(32)
        file_path = None
        if file_id:
            f = db.get_file_by_id(file_id)
            if f:
                file_path = f.filepath
        if not file_path:
            file_path = os.path.join(self._file_dir, item.text())
        try:
            os.remove(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not delete file: {e}")
            return
        # Remove from DB
        if file_id:
            db.delete_file(file_id)
        self._refresh_file_list()

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
                        error_msg = "Username and role are required."
                        log_error(error_msg)
                        QMessageBox.warning(self, "Validation Error", error_msg)
                        return
                    # Check for username conflict
                    if new_username != user.username:
                        existing = session.query(db.User).filter_by(username=new_username).first()
                        if existing:
                            error_msg = "Username already exists."
                            log_error(error_msg)
                            QMessageBox.warning(self, "Error", error_msg)
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
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Log")
        self.top_btn = QPushButton("Back to Top")
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.top_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.refresh_btn.clicked.connect(self.load_log)
        self.top_btn.clicked.connect(self.scroll_to_top)
        self.load_log()

    def scroll_to_top(self):
        self.log_text.moveCursor(self.log_text.textCursor().Start)

    def load_log(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                lines.reverse()
                self.log_text.setPlainText("".join(lines))
        except FileNotFoundError:
            self.log_text.setPlainText("No log entries yet.")

class GanttChartWidget(QWidget):
    def __init__(self, project_id, members=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.members = members or []
        self.selected_member_id = None

        from PyQt5.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QVBoxLayout
        self.figure = Figure(figsize=(7, 2))
        self.canvas = FigureCanvas(self.figure)
        # --- Allow the canvas to expand and fill available space ---
        self.canvas.setSizePolicy(self.canvas.sizePolicy().Expanding, self.canvas.sizePolicy().Expanding)
        # Remove fixed size constraints to let the chart auto-scale

        # Member list on the left
        hbox = QHBoxLayout()
        self.member_list = QListWidget()
        self.member_list.setMaximumWidth(180)
        self.member_list.addItem("All Members")
        self.member_id_map = {0: None}
        for m in self.members:
            # Try to get username as a plain string, avoiding SQLAlchemy columns
            username = None
            # If m is a ProjectMember, try m.user.username, else m.username, else fallback
            if hasattr(m, "user") and hasattr(m.user, "username"):
                username = getattr(m.user, "username", None)
            if not username and hasattr(m, "username"):
                val = getattr(m, "username")
                # If it's a SQLAlchemy column, skip
                if isinstance(val, str):
                    username = val
            if not username and hasattr(m, "user_id"):
                # Try to fetch from db if possible
                try:
                    if db and hasattr(db, "User") and hasattr(db, "SessionLocal"):
                        with db.SessionLocal() as session:
                            user_obj = session.query(db.User).filter_by(id=getattr(m, "user_id", None)).first()
                            if user_obj and hasattr(user_obj, "username"):
                                db_username = getattr(user_obj, "username")
                                if isinstance(db_username, str):
                                    username = db_username
                except Exception:
                    pass
            if not username or not isinstance(username, str):
                username = str(getattr(m, "user_id", getattr(m, "id", "Unknown")))
            uid = getattr(m, "user_id", getattr(m, "id", None))
            item = QListWidgetItem(str(username))
            item.setData(32, uid)
            self.member_list.addItem(item)
            self.member_id_map[self.member_list.count() - 1] = uid

        self.member_list.setCurrentRow(0)
        self.member_list.setMouseTracking(True)
        self.member_list.itemEntered.connect(self.on_member_hover)
        self.member_list.itemClicked.connect(self.on_member_click)
        self.member_list.viewport().installEventFilter(self)

        hbox.addWidget(self.member_list)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas, 1)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

        self._hover_member_id = None
        self._clicked_member_id = None

        self.plot_gantt()

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if obj == self.member_list.viewport():
            if event.type() == QEvent.Leave:
                self._hover_member_id = None
                self.plot_gantt()
        return super().eventFilter(obj, event)

    def on_member_hover(self, item):
        uid = item.data(32)
        self._hover_member_id = uid
        self.plot_gantt()

    def on_member_click(self, item):
        uid = item.data(32)
        self._clicked_member_id = uid
        self.plot_gantt()

    def plot_gantt(self):
        """
        Plot the Gantt chart with consistent scaling and vertical centering.
        Handles cases with few bars, identical start/end dates, and always sets axis limits.
        """
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            bars = []
            labels = []
            y = 0
            bar_positions = {}
            dep_links = []

            # Determine which member filter is active: hover (temporary) or click (locked)
            filter_uid = self._hover_member_id if self._hover_member_id is not None else self._clicked_member_id

            if db and hasattr(db, "get_tasks"):
                tasks = db.get_tasks(self.project_id)
                for task in tasks:
                    assigned_to = getattr(task, "assigned_to", None)
                    # Only filter if a member is actually selected/hovered
                    if filter_uid is not None and assigned_to != filter_uid:
                        continue
                    try:
                        log_event(
                            f"Gantt DEBUG: Task ID={getattr(task, 'id', None)}, Title='{getattr(task, 'title', '')}', "
                            f"Assigned={assigned_to}, Start={getattr(task, 'start_date', None)}, Created={getattr(task, 'created_at', None)}, "
                            f"Deadline={getattr(task, 'deadline', None)}, Due={getattr(task, 'due_date', None)}"
                        )
                    except Exception as e:
                        log_event(f"Gantt DEBUG: Failed to log task info: {e}")
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
                        try:
                            start_dt = datetime.datetime.strptime(str(start), "%Y-%m-%d")
                        except Exception:
                            start_dt = datetime.datetime.strptime(str(start), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        start_dt = None
                    try:
                        try:
                            end_dt = datetime.datetime.strptime(str(end), "%Y-%m-%d")
                        except Exception:
                            end_dt = datetime.datetime.strptime(str(end), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        end_dt = None
                    hours = getattr(task, "hours", 0) or 0
                    task_id = getattr(task, "id", None)
                    # --- Calculate total hours for this task (own + all subtasks) ---
                    total_sub_hours = 0
                    subtask_info = []
                    if hasattr(db, "get_subtasks"):
                        try:
                            task_id_val = getattr(task, "id", None)
                            subs = db.get_subtasks(task_id_val) if task_id_val is not None else []
                            for sub in subs:
                                sub_assigned = getattr(sub, "assigned_to", None)
                                if filter_uid is not None and sub_assigned != filter_uid:
                                    continue
                                sub_hours = getattr(sub, "hours", 0) or 0
                                total_sub_hours += sub_hours
                                subtask_info.append(sub)
                        except Exception as e:
                            log_error(f"Gantt subtask error: {e}")
                    total_hours = hours + total_sub_hours
                    if start_dt and end_dt:
                        bars.append((mdates.date2num(start_dt), mdates.date2num(end_dt) - mdates.date2num(start_dt)))
                        label_hours = f" | Hours: {hours}"
                        if total_sub_hours > 0:
                            label_hours += f" (+{total_sub_hours} subtask{'s' if len(subtask_info) != 1 else ''}) = {total_hours}"
                        labels.append(f"Task {task_id}: {getattr(task, 'title', '')}{label_hours}")
                        bar_positions[("task", task_id)] = (y, mdates.date2num(start_dt), mdates.date2num(end_dt))
                        dependencies = getattr(task, "dependencies", [])
                        if dependencies:
                            for dep_id in dependencies:
                                dep_links.append((("task", dep_id), ("task", task_id)))
                        y += 1
                    # --- Now add subtasks as bars and labels ---
                    if hasattr(db, "get_subtasks"):
                        try:
                            for sub in subtask_info:
                                sub_assigned = getattr(sub, "assigned_to", None)
                                if filter_uid is not None and sub_assigned != filter_uid:
                                    continue
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
                                    try:
                                        sub_start_dt = datetime.datetime.strptime(str(sub_start), "%Y-%m-%d %H:%M:%S")
                                    except Exception:
                                        sub_start_dt = None
                                try:
                                    sub_end_dt = datetime.datetime.strptime(str(sub_end), "%Y-%m-%d")
                                except Exception:
                                    try:
                                        sub_end_dt = datetime.datetime.strptime(str(sub_end), "%Y-%m-%d %H:%M:%S")
                                    except Exception:
                                        sub_end_dt = None
                                sub_hours = getattr(sub, "hours", 0) or 0
                                sub_id = getattr(sub, "id", None)
                                if sub_start_dt and sub_end_dt:
                                    bars.append((mdates.date2num(sub_start_dt), mdates.date2num(sub_end_dt) - mdates.date2num(sub_start_dt)))
                                    label_sub_hours = f" | Hours: {sub_hours}"
                                    labels.append(f"  Subtask {sub_id}: {getattr(sub, 'title', '')}{label_sub_hours}")
                                    bar_positions[("subtask", sub_id)] = (y, mdates.date2num(sub_start_dt), mdates.date2num(sub_end_dt))
                                    sub_dependencies = getattr(sub, "dependencies", [])
                                    if sub_dependencies:
                                        for dep_id in sub_dependencies:
                                            dep_key = ("subtask", dep_id) if ("subtask", dep_id) in bar_positions else ("task", dep_id)
                                            dep_links.append((dep_key, ("subtask", sub_id)))
                                    y += 1
                        except Exception as e:
                            log_error(f"Gantt subtask error: {e}")

            if bars:
                for i, (start, duration) in enumerate(bars):
                    ax.barh(i, duration, left=start, height=0.4, align='center', color="#6baed6")
                ax.set_yticks(range(len(labels)))
                ax.set_yticklabels(labels)
                ax.xaxis_date()
                ax.set_xlabel("Date")
                ax.set_title("Gantt Chart: Tasks & Subtasks")
                for from_key, to_key in dep_links:
                    if from_key in bar_positions and to_key in bar_positions:
                        from_y, _, from_end = bar_positions[from_key]
                        to_y, to_start, _ = bar_positions[to_key]
                        ax.annotate(
                            '',
                            xy=(to_start, to_y),
                            xytext=(from_end, from_y),
                            arrowprops=dict(arrowstyle="->", color="red", lw=1.5, shrinkA=5, shrinkB=5),
                            annotation_clip=False
                        )
                # --- Consistent axis scaling and vertical centering ---
                starts = [start for start, duration in bars]
                ends = [start + duration for start, duration in bars]
                min_start = min(starts)
                max_end = max(ends)
                # Ensure minimum padding for identical dates
                pad = max((max_end - min_start) * 0.05, 1 if max_end == min_start else 0.5)
                ax.set_xlim(min_start - pad, max_end + pad)
                # Vertically center if few bars
                n_bars = len(labels)
                if n_bars < 5:
                    center_offset = (5 - n_bars) / 2
                    ax.set_ylim(-0.5 + center_offset, n_bars - 0.5 + center_offset)
                else:
                    ax.set_ylim(-0.5, n_bars - 0.5)
            else:
                ax.text(0.5, 0.5, "No tasks to display", ha='center', va='center', fontsize=12, transform=ax.transAxes)
                ax.set_axis_off()
            # --- Always use fixed ylim for consistent plot size (5 bars) ---
            ax.set_ylim(-0.5, 4.5)
            # Use tight_layout to optimize margins and fill space
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            log_error(f"Gantt plot_gantt error: {e}")

    def refresh(self):
        self.plot_gantt()

class ProjectDetailPage(QWidget):
    def expand_task_item(self, item):
        # Remove any existing editor
        self._remove_task_editor()
        if not item:
            return
        raw_id = item.data(32)
        if not db or not hasattr(self.project, "id"):
            return

        # Detect if this is a subtask or task
        if isinstance(raw_id, str) and raw_id.startswith("subtask:"):
            subtask_id = int(raw_id.split(":", 1)[1])
            subtask = None
            if hasattr(db, "get_subtasks"):
                # Search all subtasks for this project
                tasks = db.get_tasks(self.project.id)
                for t in tasks:
                    task_id_val = getattr(t, "id", None)
                    if task_id_val is not None:
                        for sub in db.get_subtasks(task_id_val):
                            if getattr(sub, "id", None) == subtask_id:
                                subtask = sub
                                break
                    if subtask:
                        break
            if not subtask:
                return

            def save_subtask_callback(subtask_obj, title, deadline, assigned_to, hours, dependencies):
                if db and hasattr(db, "update_subtask"):
                    db.update_subtask(
                        subtask_obj.id,
                        title=title,
                        due_date=deadline,
                        assigned_to=assigned_to,
                        dependencies=dependencies,
                        hours=hours
                    )
                    self.load_tasks()

            def delete_subtask_callback(subtask_obj):
                if db and hasattr(db, "delete_subtask"):
                    db.delete_subtask(subtask_obj.id)
                    self.load_tasks()

            editor = TaskEditWidget(subtask, self.members, save_subtask_callback, delete_subtask_callback, parent=self.task_list)
            self.task_list.setItemWidget(item, editor)
            self._current_task_editor_item = item
            return

        # Otherwise, treat as Task
        task_id = raw_id
        # Find the task object
        tasks = db.get_tasks(self.project.id)
        task = next((t for t in tasks if getattr(t, "id", None) == task_id), None)
        if not task:
            return

        def save_callback(task_obj, title, deadline, assigned_to, hours, dependencies):
            if db and hasattr(db, "update_task"):
                db.update_task(
                    task_obj.id,
                    title=title,
                    due_date=deadline,
                    assigned_to=assigned_to,
                    dependencies=dependencies,
                    hours=hours
                )
                self.load_tasks()

        def delete_callback(task_obj):
            if db:
                # Delete all subtasks before deleting the task
                if hasattr(db, "get_subtasks") and hasattr(db, "delete_subtask"):
                    subtasks = db.get_subtasks(task_obj.id)
                    for sub in subtasks:
                        db.delete_subtask(getattr(sub, "id", None))
                if hasattr(db, "delete_task"):
                    db.delete_task(task_obj.id)
                self.load_tasks()

        editor = TaskEditWidget(task, self.members, save_callback, delete_callback, parent=self.task_list)
        self.task_list.setItemWidget(item, editor)
        self._current_task_editor_item = item

    def _remove_task_editor(self):
        # Remove the editor widget from the current item if present
        if hasattr(self, "_current_task_editor_item") and self._current_task_editor_item:
            # Only try to remove if the item still exists in the list
            try:
                idx = self.task_list.row(self._current_task_editor_item)
                if idx != -1:
                    self.task_list.setItemWidget(self._current_task_editor_item, None)
            except RuntimeError:
                pass  # Item was already deleted
            self._current_task_editor_item = None

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.members = getattr(project, "members", [])
        self.member_usernames = [getattr(m, "username", str(m)) for m in self.members]
        self.member_ids = [getattr(m, "id", None) for m in self.members]
        self.current_user = None
        mw = self.parent()
        while mw and not hasattr(mw, "current_user"):
            mw = mw.parent()
        if mw and hasattr(mw, "current_user"):
            self.current_user = getattr(mw, "current_user", None)

        self.tabs = QTabWidget()
        self.init_team_members_tab()
        self.init_tasks_tab()
        self.init_gantt_tab()
        self.init_calendar_tab()

    def init_gantt_tab(self):
        """Add the Gantt chart tab to the project detail page and assign to self.gantt_chart for refresh."""
        tab = QWidget()
        layout = QVBoxLayout()
        self.gantt_chart = GanttChartWidget(getattr(self.project, "id", None), members=self.members)
        layout.addWidget(self.gantt_chart)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Gantt Chart")
        # Refresh Gantt chart when the tab is selected
        def on_tab_changed(idx):
            if self.tabs.tabText(idx) == "Gantt Chart" and hasattr(self, "gantt_chart"):
                self.gantt_chart.refresh()
        self.tabs.currentChanged.connect(on_tab_changed)

        # Main layout for the project details page
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(f"<b>{getattr(self.project, 'name', '')}</b>"))

        # --- Project Deadline Edit ---
        from PyQt5.QtWidgets import QDateEdit, QHBoxLayout, QPushButton, QMessageBox
        from PyQt5.QtCore import QDate
        deadline_layout = QHBoxLayout()
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        # Set current deadline if available
        deadline_val = getattr(self.project, "deadline", None)
        if deadline_val:
            try:
                y, m, d = map(int, str(deadline_val).split("-"))
                self.deadline_edit.setDate(QDate(y, m, d))
            except Exception:
                self.deadline_edit.setDate(QDate.currentDate())
        else:
            self.deadline_edit.setDate(QDate.currentDate())
        deadline_layout.addWidget(QLabel("Project Deadline:"))
        deadline_layout.addWidget(self.deadline_edit)
        self.save_deadline_btn = QPushButton("Save Deadline")
        deadline_layout.addWidget(self.save_deadline_btn)
        vbox.addLayout(deadline_layout)
        self.save_deadline_btn.clicked.connect(self.save_project_deadline)

        # --- Delete Project Button ---
        self.delete_project_btn = QPushButton("Delete Project")
        vbox.addWidget(self.delete_project_btn)
        self.delete_project_btn.clicked.connect(self.delete_project)

        vbox.addWidget(self.tabs)
        # Back button
        self.back_btn = QPushButton("Back to Dashboard")
        self.back_btn.clicked.connect(self.log_and_go_back)
        vbox.addWidget(self.back_btn)
        self.setLayout(vbox)
        # Ensure tasks are loaded and displayed on page load
        self.load_tasks()

    def refresh_task_dropdowns(self):
        # Refresh parent_task_dropdown and any dependency dropdowns after task creation
        if hasattr(self, "parent_task_dropdown"):
            self.parent_task_dropdown.clear()
            self.parent_task_dropdown.addItem("Select parent task", None)
            if db and hasattr(self.project, "id"):
                tasks = db.get_tasks(self.project.id)
                for t in tasks:
                    self.parent_task_dropdown.addItem(f"{t.id}: {t.title}", t.id)
        # Also refresh dependency selection input if needed
        # (If you have a dependency dropdown, refresh it here as well)

    def delete_project(self):
        # Simple wrapper for project deletion logic
        from PyQt5.QtWidgets import QMessageBox
        if db and hasattr(self.project, "id"):
            project_id = getattr(self.project, "id")
            project_name = getattr(self.project, "name", "")
            # --- Confirmation popup before deletion ---
            confirm = QMessageBox.question(
                self,
                "Confirm Project Deletion",
                f"Are you sure you want to delete the project '{project_name}'?\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
            try:
                user_id = None
                mw = self.parent()
                while mw and not hasattr(mw, "current_user"):
                    mw = mw.parent()
                if mw and hasattr(mw, "current_user") and mw.current_user:
                    user_id = getattr(mw.current_user, "id", None)
                # --- Delete all subtasks for all tasks in this project before deleting the project ---
                if db and hasattr(db, "get_tasks") and hasattr(db, "get_subtasks") and hasattr(db, "delete_subtask"):
                    tasks = db.get_tasks(project_id)
                    for task in tasks:
                        task_id = getattr(task, "id", None)
                        if task_id is not None:
                            subtasks = db.get_subtasks(task_id)
                            for sub in subtasks:
                                sub_id = getattr(sub, "id", None)
                                if sub_id is not None:
                                    db.delete_subtask(sub_id)
                if user_id is not None:
                    result = db.delete_project(project_id, user_id)
                else:
                    result = None
                if result:
                    log_event(f"Project '{project_name}' (ID {project_id}) deleted.")
                    QMessageBox.information(self, "Project Deleted", f"Project '{project_name}' has been deleted.")
                    # Return to dashboard
                    mw = self.parent()
                    from PyQt5.QtWidgets import QMainWindow, QWidget
                    while mw and not isinstance(mw, QMainWindow):
                        mw = mw.parent()
                    if mw:
                        try:
                            if mw.dashboard is None or not isinstance(mw.dashboard, QWidget) or mw.dashboard.parent() is None:
                                raise RuntimeError("Dashboard widget deleted")
                            mw.dashboard.load_projects()
                            mw.stack.setCurrentWidget(mw.dashboard)
                        except Exception:
                            mw.dashboard = DashboardView(main_window=mw, user=mw.current_user)
                            mw.stack.addWidget(mw.dashboard)
                            mw.stack.setCurrentWidget(mw.dashboard)
                        # Always refresh project list after navigation
                        if hasattr(mw.dashboard, "load_projects"):
                            mw.dashboard.load_projects()
                else:
                    error_msg = "Failed to delete project from database."
                    log_error(error_msg)
                    QMessageBox.warning(self, "Error", error_msg)
            except Exception as e:
                error_msg = f"An error occurred while deleting the project: {e}"
                log_error(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
        else:
            error_msg = "Database not available or project ID missing."
            log_error(error_msg)
            QMessageBox.warning(self, "Error", error_msg)

    def save_project_deadline(self):
        from PyQt5.QtWidgets import QMessageBox
        new_deadline = self.deadline_edit.date().toString("yyyy-MM-dd")
        if db and hasattr(self.project, "id"):
            try:
                with db.SessionLocal() as session:
                    project = session.query(db.Project).filter_by(id=self.project.id).first()
                    if project:
                        # Use db.update_project to update deadline
                        user_id = None
                        mw = self.parent()
                        while mw and not hasattr(mw, "current_user"):
                            mw = mw.parent()
                        if mw and hasattr(mw, "current_user"):
                            user_id = getattr(mw, "current_user", None)
                            if hasattr(user_id, "id"):
                                user_id = user_id.id
                        if user_id is not None:
                            db.update_project(self.project.id, user_id, description=None, name=None)
                            # Now update deadline directly via SQLAlchemy if needed
                            db.update_project(self.project.id, user_id, description=None, name=None)
                            # Now update deadline using update_project
                            setattr(project, "deadline", str(new_deadline))
                            session.commit()
                            QMessageBox.information(self, "Success", "Project deadline updated.")
                            self.project.deadline = str(new_deadline)
                            self.load_tasks()
                        else:
                            QMessageBox.warning(self, "Error", "User context not found.")
                    else:
                        QMessageBox.warning(self, "Error", "Project not found.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to update deadline: {e}")
        else:
            QMessageBox.warning(self, "Error", "Database not available.")


    def log_and_go_back(self):
        log_event("User clicked 'Back to Dashboard' on Project Detail Page")
        self.go_back()

    def go_back(self):
        # Robustly find MainWindow and show dashboard
        mw = self.parent()
        from PyQt5.QtWidgets import QMainWindow
        while mw and not isinstance(mw, QMainWindow):
            mw = mw.parent()
        if mw and hasattr(mw, "stack") and hasattr(mw, "dashboard"):
            try:
                if mw.dashboard is None or not isinstance(mw.dashboard, QWidget) or mw.dashboard.parent() is None:
                    raise RuntimeError("Dashboard widget deleted")
                mw.stack.setCurrentWidget(mw.dashboard)
            except Exception:
                from Draft_2.app.main import DashboardView
                mw.dashboard = DashboardView(main_window=mw, user=getattr(mw, "current_user", None))
                mw.stack.addWidget(mw.dashboard)
                mw.stack.setCurrentWidget(mw.dashboard)
            log_event("Returned to Dashboard from Project Detail Page")

    # Removed duplicate/legacy init_gantt_tab to avoid confusion and ensure correct Gantt chart refresh.

    def init_calendar_tab(self):
        tab = CalendarTabWidget(user=self.current_user)
        self.tabs.addTab(tab, "Calendar")

    def init_team_members_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        # Member list with roles
        self.member_list = QListWidget()
        self.member_list.setSelectionMode(QListWidget.SingleSelection)
        self.refresh_member_list()
        layout.addWidget(QLabel("Team Members:"))
        layout.addWidget(self.member_list)
        # Add member controls
        add_layout = QHBoxLayout()
        self.add_member_combo = QComboBox()
        self.add_member_combo.setEditable(True)
        self.populate_add_member_combo()
        add_layout.addWidget(QLabel("Add Member:"))
        add_layout.addWidget(self.add_member_combo)
        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Role (optional)")
        add_layout.addWidget(self.role_input)
        self.add_member_btn = QPushButton("Add")
        self.add_member_btn.clicked.connect(self.add_member_to_project)
        add_layout.addWidget(self.add_member_btn)
        layout.addLayout(add_layout)
        # Change leader button
        self.change_leader_btn = QPushButton("Change Team Leader")
        self.change_leader_btn.clicked.connect(self.show_change_leader_dialog)
        layout.addWidget(self.change_leader_btn)
        # Info label
        self.member_info_label = QLabel("Hover over a member to filter tasks and Gantt chart.")
        layout.addWidget(self.member_info_label)
        self.member_list.itemEntered.connect(self.filter_by_member)
        self.member_list.setMouseTracking(True)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Team Members")

    def refresh_member_list(self):
        self.member_list.clear()
        for m in self.members:
            # Avoid DetachedInstanceError: fetch user info by user_id using a new session
            user_id = getattr(m, "user_id", None)
            project_role = getattr(m, "role", None)
            username = str(user_id)
            company_role = None
            if db and user_id is not None:
                with db.SessionLocal() as session:
                    user_obj = session.query(db.User).filter_by(id=user_id).first()
                    if user_obj:
                        username = getattr(user_obj, "username", str(user_id))
                        company_role = getattr(user_obj, "role", None)
            display_role = project_role if project_role else (company_role if company_role else "member")
            item = QListWidgetItem(f"{username} ({display_role})")
            item.setData(Qt.ItemDataRole.UserRole, user_id)
            self.member_list.addItem(item)

    def populate_add_member_combo(self):
        self.add_member_combo.clear()
        if db:
            with db.SessionLocal() as session:
                users = session.query(db.User).all()
                for user in users:
                    user_id = getattr(user, "id", None)
                    username = getattr(user, "username", "")
                    if user_id is not None and username:
                        self.add_member_combo.addItem(str(username), int(user_id))

    def add_member_to_project(self):
        user_id = self.add_member_combo.currentData()
        role = self.role_input.text().strip()
        if user_id and db and hasattr(self.project, "id"):
            if hasattr(db, "add_project_member"):
                # user_id is the current user (for permission), new_member_id is the selected user
                current_user_id = None
                mw = self.parent()
                while mw and not hasattr(mw, "current_user"):
                    mw = mw.parent()
                if mw and hasattr(mw, "current_user"):
                    current_user_id = getattr(mw, "current_user", None)
                    if hasattr(current_user_id, "id"):
                        if hasattr(current_user_id, "id"):
                            current_user_id = getattr(current_user_id, "id", None)
                if user_id is not None and current_user_id is not None:
                    db.add_project_member(self.project.id, current_user_id, user_id, role)
            self.refresh_members_from_db()
            self.refresh_member_list()
            self.populate_add_member_combo()
            # Also reload task assignment combos if present
            if hasattr(self, "task_assigned_combo"):
                self.task_assigned_combo.clear()
                self.task_assigned_combo.addItem("Unassigned", None)
                for m in self.members:
                    self.task_assigned_combo.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
            if hasattr(self, "assigned_input"):
                self.assigned_input.clear()
                self.assigned_input.addItem("Unassigned", None)
                for m in self.members:
                    self.assigned_input.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))

    def refresh_members_from_db(self):
        if db and hasattr(self.project, "id"):
            with db.SessionLocal() as session:
                proj = session.query(db.Project).filter_by(id=self.project.id).first()
                self.members = getattr(proj, "members", [])
                self.member_usernames = [getattr(m, "username", str(m)) for m in self.members]
                self.member_ids = [getattr(m, "id", None) for m in self.members]

    def filter_by_member(self, item):
        member_id = item.data(Qt.ItemDataRole.UserRole)
        # TODO: Filter tasks and Gantt chart by member_id

    def show_change_leader_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Change Team Leader")
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Select new team leader:"))
        combo = QComboBox()
        for m in self.members:
            username = getattr(m, "username", str(m))
            uid = getattr(m, "id", None)
            combo.addItem(username, uid)
        vbox.addWidget(combo)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)
        dlg.setLayout(vbox)
        def on_accept():
            new_leader_id = combo.currentData()
            if new_leader_id and db and hasattr(db, "update_project_leader"):
                # db.update_project_leader(getattr(self.project, "id", None), new_leader_id)  # Not implemented
                # Optionally, show a message or implement leader change logic here
                self.refresh_members_from_db()
                self.refresh_member_list()
            dlg.accept()
        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dlg.reject)
        dlg.exec_()

    def init_tasks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        # Add Task Form
        from PyQt5.QtWidgets import QCheckBox
        form_layout = QHBoxLayout()
        self.task_title_input = QLineEdit()
        self.task_title_input.setPlaceholderText("Task Name")
        self.task_deadline_input = QDateEdit()
        self.task_deadline_input.setCalendarPopup(True)
        self.task_deadline_input.setDisplayFormat("yyyy-MM-dd")
        self.task_deadline_input.setDate(QDate.currentDate())
        self.task_assigned_combo = QComboBox()
        self.task_assigned_combo.addItem("Unassigned", None)
        for m in self.members:
            self.task_assigned_combo.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
        self.task_hours_input = QSpinBox()
        self.task_hours_input.setMinimum(0)
        self.task_hours_input.setMaximum(1000)
        self.task_hours_input.setPrefix("Hours: ")
        self.task_dep_input = QLineEdit()
        self.task_dep_input.setReadOnly(True)
        self.task_dep_btn = QPushButton("Select Dependencies")
        self.task_dep_btn.clicked.connect(self.select_task_dependencies)
        self.task_dep_ids = []

        # --- Subtask UI ---
        self.make_subtask_checkbox = QCheckBox("Make as sub task")
        self.parent_task_dropdown = QComboBox()
        self.parent_task_dropdown.setVisible(False)
        self.parent_task_dropdown.addItem("Select parent task", None)
        if db and hasattr(self.project, "id"):
            tasks = db.get_tasks(self.project.id)
            for t in tasks:
                self.parent_task_dropdown.addItem(f"{t.id}: {t.title}", t.id)
        def on_subtask_checkbox_changed(state):
            self.parent_task_dropdown.setVisible(self.make_subtask_checkbox.isChecked())
        self.make_subtask_checkbox.stateChanged.connect(on_subtask_checkbox_changed)

        form_layout.addWidget(self.task_title_input)
        form_layout.addWidget(self.task_deadline_input)
        form_layout.addWidget(self.task_assigned_combo)
        form_layout.addWidget(self.task_hours_input)
        form_layout.addWidget(self.task_dep_input)
        form_layout.addWidget(self.task_dep_btn)
        form_layout.addWidget(self.make_subtask_checkbox)
        form_layout.addWidget(self.parent_task_dropdown)
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(self.add_task)
        form_layout.addWidget(self.add_task_btn)
        layout.addLayout(form_layout)
        # Task List
        self.task_list = QListWidget()
        self.task_list.itemClicked.connect(self.expand_task_item)
        layout.addWidget(self.task_list)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Tasks")
    def load_tasks(self):
        self.task_list.clear()
        if db and hasattr(self.project, "id"):
            tasks = db.get_tasks(self.project.id)
            for task in tasks:
                # Add main task item
                item = QListWidgetItem(f"{task.id}: {task.title} | Deadline: {getattr(task, 'deadline', 'N/A')} | Assigned: {getattr(task, 'assigned_to', 'Unassigned')}")
                item.setData(32, task.id)
                self.task_list.addItem(item)
                # Add subtasks indented under the task
                if hasattr(db, "get_subtasks"):
                    task_id_val = getattr(task, "id", None)
                    subtasks = db.get_subtasks(task_id_val) if task_id_val is not None else []
                    for sub in subtasks:
                        sub_item = QListWidgetItem(f"    ↳ {sub.id}: {sub.title} | Deadline: {getattr(sub, 'due_date', 'N/A')} | Assigned: {getattr(sub, 'assigned_to', 'Unassigned')}")
                        sub_item.setData(32, f"subtask:{sub.id}")
                        font = sub_item.font()
                        font.setItalic(True)
                        sub_item.setFont(font)
                        self.task_list.addItem(sub_item)
        # Refresh Gantt chart after loading tasks
        if hasattr(self, "gantt_chart") and self.gantt_chart is not None:
            self.gantt_chart.refresh()
        # (Removed recursive call to self.load_tasks() to prevent infinite recursion)

    def select_task_dependencies(self):
        dep_dialog = QDialog(self)
        dep_dialog.setWindowTitle("Select Dependencies")
        vbox = QVBoxLayout(dep_dialog)
        dep_list = QListWidget()
        dep_list.setSelectionMode(QListWidget.MultiSelection)
        if db and hasattr(self.project, "id"):
            tasks = db.get_tasks(self.project.id)
            for task in tasks:
                if hasattr(task, "id") and hasattr(task, "title"):
                    item = QListWidgetItem(f"Task {task.id}: {task.title}")
                    item.setData(32, ("task", task.id))
                    dep_list.addItem(item)
                    # Add subtasks for this task
                    if hasattr(db, "get_subtasks"):
                        subs = db.get_subtasks(task.id)
                        for sub in subs:
                            sub_item = QListWidgetItem(f"Subtask {sub.id}: {sub.title}")
                            sub_item.setData(32, ("subtask", sub.id))
                            dep_list.addItem(sub_item)
        # Pre-select existing dependencies
        for i in range(dep_list.count()):
            item = dep_list.item(i)
            if item and item.data(32) in [(("task", tid) if isinstance(tid, int) else tid) for tid in self.task_dep_ids]:
                item.setSelected(True)
            elif item and isinstance(item.data(32), tuple) and item.data(32)[1] in self.task_dep_ids:
                item.setSelected(True)
        vbox.addWidget(dep_list)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)
        def accept():
            self.task_dep_ids.clear()
            selected_titles = []
            for item in dep_list.selectedItems():
                dep_val = item.data(32)
                if isinstance(dep_val, tuple):
                    self.task_dep_ids.append(dep_val)
                else:
                    self.task_dep_ids.append(dep_val)
                selected_titles.append(item.text() if item is not None else "")
            self.task_dep_input.setText(", ".join(selected_titles))
            dep_dialog.accept()
        button_box.accepted.connect(accept)
        button_box.rejected.connect(dep_dialog.reject)
        dep_dialog.exec_()

    def add_task(self):
        title = self.task_title_input.text().strip()
        due_date_qdate = self.task_deadline_input.date()
        due_date_obj = due_date_qdate.toPyDate()
        assigned_id = self.task_assigned_combo.currentData()
        hours = self.task_hours_input.value()
        dependencies = self.task_dep_ids
        if not title or not db or not hasattr(self.project, "id"):
            return

        import datetime as dt

        # If "Make as sub task" is checked and a parent is selected, create subtask
        if hasattr(self, "make_subtask_checkbox") and self.make_subtask_checkbox.isChecked():
            parent_task_id = self.parent_task_dropdown.currentData()
            if parent_task_id:
                db.create_subtask(
                    task_id=parent_task_id,
                    title=title,
                    due_date=dt.datetime.combine(due_date_obj, dt.time.min) if due_date_obj else None,
                    assigned_to=assigned_id,
                    dependencies=dependencies,
                    hours=hours
                )
                log_event(
                    f"Subtask added: '{title}' | Parent Task: {parent_task_id} | Project: '{getattr(self.project, 'name', 'N/A')}' | Deadline: {due_date_obj} | Hours: {hours}"
                )
                self.load_tasks()
                self.refresh_task_dropdowns()
                self.task_title_input.clear()
                self.task_deadline_input.setDate(QDate.currentDate())
                self.task_assigned_combo.setCurrentIndex(0)
                self.task_hours_input.setValue(0)
                self.task_dep_input.clear()
                self.task_dep_ids.clear()
                self.make_subtask_checkbox.setChecked(False)
                self.parent_task_dropdown.setCurrentIndex(0)
                return

        # Otherwise, create as Task
        db.create_task(
            project_id=self.project.id,
            title=title,
            due_date=dt.datetime.combine(due_date_obj, dt.time.min) if due_date_obj else None,
            assigned_to=assigned_id,
            dependencies=dependencies,
            hours=hours
        )
        log_event(
            f"Task added: '{title}' | Project: '{getattr(self.project, 'name', 'N/A')}' | Deadline: {due_date_obj} | Hours: {hours} | Assigned to: {assigned_id}"
        )
        self.load_tasks()
        # Refresh parent_task_dropdown after loading tasks
        if hasattr(self, "parent_task_dropdown"):
            self.parent_task_dropdown.clear()
            self.parent_task_dropdown.addItem("Select parent task", None)
            if db and hasattr(self.project, "id"):
                tasks = db.get_tasks(self.project.id)
                for t in tasks:
                    self.parent_task_dropdown.addItem(f"{t.id}: {t.title}", t.id)
        self.task_title_input.clear()
        self.task_deadline_input.setDate(QDate.currentDate())
        self.task_assigned_combo.setCurrentIndex(0)
        self.task_hours_input.setValue(0)
        self.task_dep_input.clear()
        self.task_dep_ids.clear()
        self.make_subtask_checkbox.setChecked(False)
        self.parent_task_dropdown.setCurrentIndex(0)

class TaskEditWidget(QWidget):
    def __init__(self, task, members, save_callback, delete_callback, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QDateEdit, QComboBox, QSpinBox, QPushButton, QCheckBox
        from PyQt5.QtCore import QDate
        import json

        self.task = task
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_input = QLineEdit(getattr(task, "title", ""))
        layout.addWidget(self.title_input)

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        deadline_val = getattr(task, "due_date", None)
        if not deadline_val:
            deadline_val = getattr(task, "deadline", None)
        if deadline_val:
            try:
                if hasattr(deadline_val, "strftime"):
                    self.deadline_input.setDate(QDate(deadline_val.year, deadline_val.month, deadline_val.day))
                else:
                    y, m, d = map(int, str(deadline_val).split("-"))
                    self.deadline_input.setDate(QDate(y, m, d))
            except Exception:
                self.deadline_input.setDate(QDate.currentDate())
        else:
            self.deadline_input.setDate(QDate.currentDate())
        layout.addWidget(self.deadline_input)

        self.assigned_input = QComboBox()
        self.assigned_input.addItem("Unassigned", None)
        for m in members:
            user_obj = getattr(m, "user", None)
            username = getattr(user_obj, "username", str(user_obj)) if user_obj else str(m)
            uid = getattr(user_obj, "id", None) if user_obj else getattr(m, "user_id", None)
            self.assigned_input.addItem(username, uid)
        assigned_id = getattr(task, "assigned_to", None)
        if assigned_id:
            idx = self.assigned_input.findData(assigned_id)
            if idx >= 0:
                self.assigned_input.setCurrentIndex(idx)
        layout.addWidget(self.assigned_input)

        self.hours_input = QSpinBox()
        self.hours_input.setMinimum(0)
        self.hours_input.setMaximum(1000)
        hours_val = getattr(task, "hours", 0) or 0
        self.hours_input.setValue(int(hours_val))
        layout.addWidget(self.hours_input)

        self.dep_btn = QPushButton("Deps")
        self.dep_ids = []
        try:
            self.dep_ids = json.loads(getattr(task, "dependencies", "[]") or "[]")
        except Exception:
            self.dep_ids = []
        self.dep_btn.clicked.connect(self.open_dep_dialog)
        layout.addWidget(self.dep_btn)

        # --- Subtask conversion UI ---
        self.make_subtask_checkbox = QCheckBox("Make as sub task")
        self.parent_task_dropdown = QComboBox()
        self.parent_task_dropdown.addItem("Select parent task", None)
        # Always show the checkbox and dropdown in edit UI
        self.parent_task_dropdown.setVisible(self.make_subtask_checkbox.isChecked())
        parent_project_id = None
        # --- Prevent conversion if Task has subtasks ---
        if db is not None and hasattr(task, "id") and hasattr(db, "get_subtasks") and not hasattr(task, "task_id"):
            task_id_val = getattr(task, "id", None)
            if task_id_val is not None:
                subtasks = db.get_subtasks(task_id_val)
                if subtasks:
                    self.make_subtask_checkbox.setEnabled(False)
                    self.make_subtask_checkbox.setToolTip("Cannot convert a task with subtasks into a subtask.")
        if parent is not None and hasattr(parent, "project") and db is not None and hasattr(parent.project, "id"):
            parent_project_id = parent.project.id
            if parent_project_id:
                tasks = db.get_tasks(parent_project_id)
                for t in tasks:
                    if getattr(t, "id", None) != getattr(task, "id", None):
                        self.parent_task_dropdown.addItem(f"{t.id}: {t.title}", t.id)
        def on_subtask_checkbox_changed(state):
            self.parent_task_dropdown.setVisible(self.make_subtask_checkbox.isChecked())
        self.make_subtask_checkbox.stateChanged.connect(on_subtask_checkbox_changed)
        layout.addWidget(self.make_subtask_checkbox)
        layout.addWidget(self.parent_task_dropdown)

        # If this is a subtask, pre-check and select parent
        if hasattr(task, "task_id"):
            self.make_subtask_checkbox.setChecked(True)
            self.parent_task_dropdown.setVisible(True)
            idx = self.parent_task_dropdown.findData(getattr(task, "task_id", None))
            if idx >= 0:
                self.parent_task_dropdown.setCurrentIndex(idx)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)

    def open_dep_dialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QListWidgetItem
        dep_dialog = QDialog(self)
        dep_dialog.setWindowTitle("Select Dependencies")
        vbox = QVBoxLayout(dep_dialog)
        dep_list = QListWidget()
        dep_list.setSelectionMode(QListWidget.MultiSelection)
        parent_widget = self.parent()
        if parent_widget is not None and hasattr(parent_widget, "project") and hasattr(parent_widget.project, "id"):
            db_mod = __import__("Draft_2.app.db", fromlist=["get_tasks", "get_subtasks"])
            project_id = parent_widget.project.id
            tasks = db_mod.get_tasks(project_id)
            for t in tasks:
                if hasattr(t, "id") and hasattr(t, "title"):
                    item = QListWidgetItem(f"Task {t.id}: {t.title}")
                    item.setData(32, ("task", t.id))
                    dep_list.addItem(item)
                    # Add subtasks for this task
                    if hasattr(db_mod, "get_subtasks"):
                        subs = db_mod.get_subtasks(t.id)
                        for sub in subs:
                            sub_item = QListWidgetItem(f"Subtask {sub.id}: {sub.title}")
                            sub_item.setData(32, ("subtask", sub.id))
                            dep_list.addItem(sub_item)
        # Pre-select existing dependencies
        for i in range(dep_list.count()):
            item = dep_list.item(i)
            if item and item.data(32) in [(("task", tid) if isinstance(tid, int) else tid) for tid in self.dep_ids]:
                item.setSelected(True)
            # Also support legacy int-only dep_ids for backward compatibility
            elif item and isinstance(item.data(32), tuple) and item.data(32)[1] in self.dep_ids:
                item.setSelected(True)
        vbox.addWidget(dep_list)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)
        def accept():
            self.dep_ids.clear()
            for item in dep_list.selectedItems():
                dep_val = item.data(32)
                # Store as (kind, id) tuple if possible, else just id
                if isinstance(dep_val, tuple):
                    self.dep_ids.append(dep_val)
                else:
                    self.dep_ids.append(dep_val)
            dep_dialog.accept()
        button_box.accepted.connect(accept)
        button_box.rejected.connect(dep_dialog.reject)
        dep_dialog.exec_()

    def save(self):
        import datetime as dt
        is_subtask = hasattr(self.task, "task_id")
        make_subtask = self.make_subtask_checkbox.isChecked()
        parent_task_id = self.parent_task_dropdown.currentData() if make_subtask else None

        # Convert Task to Subtask
        if not is_subtask and make_subtask and parent_task_id:
            if db and hasattr(self.task, "id") and hasattr(db, "get_subtasks"):
                subtasks = db.get_subtasks(self.task.id)
                if subtasks:
                    QMessageBox.warning(self, "Conversion Not Allowed", "Cannot convert a task with subtasks into a subtask.")
                    return
                db.delete_task(self.task.id)
                db.create_subtask(
                    task_id=parent_task_id,
                    title=self.title_input.text().strip(),
                    due_date=dt.datetime.combine(self.deadline_input.date().toPyDate(), dt.time.min),
                    assigned_to=self.assigned_input.currentData(),
                    dependencies=self.dep_ids,
                    hours=self.hours_input.value()
                )
                parent_widget = self.parent()
                if parent_widget is not None and hasattr(parent_widget, "load_tasks"):
                    parent_widget.load_tasks()
                return

        # Convert Subtask to Task
        if is_subtask and not make_subtask:
            if db and hasattr(self.task, "id"):
                db.delete_subtask(self.task.id)
            if db and hasattr(self.parent(), "project"):
                parent_widget = self.parent()
                if parent_widget is not None and hasattr(parent_widget, "project"):
                    db.create_task(
                        project_id=parent_widget.project.id,
                        title=self.title_input.text().strip(),
                        due_date=dt.datetime.combine(self.deadline_input.date().toPyDate(), dt.time.min),
                        assigned_to=self.assigned_input.currentData(),
                        dependencies=self.dep_ids,
                        hours=self.hours_input.value()
                    )
            parent_widget = self.parent()
            if parent_widget is not None and hasattr(parent_widget, "load_tasks"):
                parent_widget.load_tasks()
            return

        # Normal save (edit task or subtask)
        self.save_callback(
            self.task,
            self.title_input.text().strip(),
            self.deadline_input.date().toPyDate(),
            self.assigned_input.currentData(),
            self.hours_input.value(),
            self.dep_ids
        )

    def delete(self):
        self.delete_callback(self.task)

    # Removed duplicate/legacy expand_task_item to avoid method conflict.

    def show_add_subtask_dialog(self, parent_task_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Subtask")
        form = QFormLayout()
        title_input = QLineEdit()
        deadline_input = QDateEdit()
        deadline_input.setCalendarPopup(True)
        deadline_input.setDisplayFormat("yyyy-MM-dd")
        deadline_input.setDate(QDate.currentDate())
        dependencies_input = QLineEdit()
        dependencies_input.setReadOnly(True)
        dep_select_btn = QPushButton("Select Dependencies")
        dep_ids = []
        hours_input = QSpinBox()
        hours_input.setMinimum(0)
        hours_input.setMaximum(1000)
        hours_input.setPrefix("Hours: ")
        assigned_input = QComboBox()
        assigned_input.addItem("Unassigned", None)
        for m in self.members:
            assigned_input.addItem(getattr(m, "username", str(m)), getattr(m, "id", None))
        def open_dep_dialog():
            dep_dialog = QDialog(dialog)
            dep_dialog.setWindowTitle("Select Dependencies")
            vbox = QVBoxLayout(dep_dialog)
            dep_list = QListWidget()
            dep_list.setSelectionMode(QListWidget.MultiSelection)
            if db and hasattr(self.project, "id"):
                tasks = db.get_tasks(self.project.id)
                for task in tasks:
                    if hasattr(task, "id") and hasattr(task, "title"):
                        item = QListWidgetItem(f"Task {task.id}: {task.title}")
                        item.setData(32, ("task", task.id))
                        dep_list.addItem(item)
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
                db.create_subtask(
                    task_id=parent_task_id,
                    title=title,
                    due_date=datetime.datetime.strptime(deadline, "%Y-%m-%d") if deadline else None,
                    dependencies=dependencies,
                    assigned_to=assigned_id,
                    hours=hours
                )
                self.load_tasks()
                dialog.accept()
        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dialog.reject)
        dialog.exec_()

# Moved and properly indented inside ProjectDetailPage class:
# Remove stray global definition of init_gantt_tab (if present)

    def init_calendar_tab(self):
        tab = CalendarTabWidget(user=self.current_user)
        self.tabs.addTab(tab, "Calendar")


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
                error_msg = "Please select a team member."
                log_error(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
                return
            # Call backend to update leader
            if db and hasattr(db, "update_project_leader"):
                try:
                    if hasattr(db, "update_project_leader"):
                        # result = db.update_project_leader(getattr(self.project, "id", None), new_leader_id)  # Not implemented
                        result = None
                    else:
                        result = None
                except Exception as e:
                    error_msg = f"Failed to update leader: {e}"
                    log_error(error_msg)
                    QMessageBox.warning(self, "Error", error_msg)
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
                            error_msg = "Project not found."
                            log_error(error_msg)
                            QMessageBox.warning(self, "Error", error_msg)
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
                    error_msg = f"Failed to update leader: {e}"
                    log_error(error_msg)
                    QMessageBox.warning(self, "Error", error_msg)
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


    def _remove_task_editor(self):
        # Remove the editor widget from the current item if present
        if hasattr(self, "_current_task_editor_item") and self._current_task_editor_item:
            self.task_list.setItemWidget(self._current_task_editor_item, None)
            self._current_task_editor_item = None
    # Removed duplicate expand_task_item (should only exist once in ProjectDetailPage)

    # Removed duplicate _remove_task_editor (should only exist once in ProjectDetailPage)




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
                        # Always require user_id for delete_project
                        if user_id is not None:
                            result = db.delete_project(project_id, user_id)
                        else:
                            result = None
                if result:
                    log_event(f"Project '{project_name}' (ID {project_id}) deleted.")
                    QMessageBox.information(self, "Project Deleted", f"Project '{project_name}' has been deleted.")
                    # Return to dashboard
                    mw = self.parent()
                    while mw and not isinstance(mw, MainWindow):
                        mw = mw.parent()
                    if mw:
                        try:
                            if mw.dashboard is None or not isinstance(mw.dashboard, QWidget) or mw.dashboard.parent() is None:
                                raise RuntimeError("Dashboard widget deleted")
                            mw.dashboard.load_projects()
                            mw.stack.setCurrentWidget(mw.dashboard)
                        except Exception:
                            mw.dashboard = DashboardView(main_window=mw, user=mw.current_user)
                            mw.stack.addWidget(mw.dashboard)
                            mw.stack.setCurrentWidget(mw.dashboard)
                else:
                    error_msg = "Failed to delete project from database."
                    log_error(error_msg)
                    QMessageBox.warning(self, "Error", error_msg)
            except Exception as e:
                error_msg = f"An error occurred while deleting the project: {e}"
                log_error(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
        else:
            error_msg = "Database not available or project ID missing."
            log_error(error_msg)
            QMessageBox.warning(self, "Error", error_msg)

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
                self.stack.removeWidget(self.project_detail_page)
                self.project_detail_page.deleteLater()
        except RuntimeError:
            # Widget has been deleted, handle gracefully (e.g., ignore or recreate stack)
            return
        self.project_detail_page = ProjectDetailPage(project, parent=self)
        self.stack.addWidget(self.project_detail_page)
        self.stack.setCurrentWidget(self.project_detail_page)
        log_event("Navigated to Project Detail Page")
        # Do not reset central widget or dashboard here; just update the stack.

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
                    # db.set_user_display_pref(user.id, {"scale_factor": self._scale_factor})  # Not implemented
                    pass
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

    def closeEvent(self, event):
        """Automatically log out the user when the main window is closed."""
        if hasattr(self, "current_user") and self.current_user:
            self.current_user = None
            log_event("User automatically logged out on program close")
        super().closeEvent(event)

class App(QApplication):
    def __init__(self, argv):
        # Enable DPI scaling before QApplication is created
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        super().__init__(argv)
        # self._logout_key = Qt.Key.Key_Escape  # Escape key no longer triggers logout
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

        # Install event filter for scaling only (logout on Esc disabled)
        self.window.installEventFilter(self)
        self.login_page.installEventFilter(self)

    def eventFilter(self, obj, event):
        # Escape key no longer triggers logout or navigation to login page
        # if event.type() == QEvent.Type.KeyPress and event.key() == self._logout_key:
        #     self.logout()
        #     return True

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
        username = self.login_page.username.text().strip()
        password = self.login_page.password.text().strip()
        # Extra debug logging for widget state and db import
        with open("login_debug.log", "a", encoding="utf-8") as dbg:
            dbg.write(f"Attempt login: username={username!r}, password={password!r}\n")
            dbg.write(f"Username widget type: {type(self.login_page.username)}\n")
            dbg.write(f"Password widget type: {type(self.login_page.password)}\n")
            dbg.write(f"Username widget text(): {self.login_page.username.text()!r}\n")
            dbg.write(f"Password widget text(): {self.login_page.password.text()!r}\n")
            dbg.write(f"db module: {db!r}\n")
        # Log after stripping
        with open("login_debug.log", "a", encoding="utf-8") as dbg:
            dbg.write(f"After strip: username={username!r}, password={password!r}\n")
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
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = App(sys.argv)
    sys.exit(app.exec_())

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Use direct reference if MainWindow is defined in this file
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
