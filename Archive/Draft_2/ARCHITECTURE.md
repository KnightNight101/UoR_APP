# Draft_2 Project Management Platform - System Architecture

## Overview

This document describes the architecture of the fully local, offline PyQt (PySide6/QML) Project Management Platform. The application is a desktop solution with no web, HTTP, or remote dependencies. All data, authentication, user interactions, and document versioning are handled locally on the user's machine.

---

## 1. High-Level Architecture

```mermaid
flowchart TD
    QML[QML UI (Main.qml)]
    MainPy[main.py (PySide6 entry point)]
    Managers[Backend Managers<br/>(AuthManager, DashboardManager,<br/>ProjectManager, UserManager, LogEventBridge)]
    DB[db.py (SQLAlchemy ORM,<br/>roles, events, files, encryption)]
    Files[Local Filesystem<br/>(LibreOffice docs, event_log.txt)]
    Git[Local Git Repos<br/>(per file/project)]
    EventLog[event_log.txt]
    Images[UI Images & Diagrams]

    QML -- "Signals/Slots, Properties" --> MainPy
    MainPy -- "Exposes Managers to QML" --> Managers
    Managers -- "DB/API Calls" --> DB
    Managers -- "File Ops, Logging" --> Files
    DB -- "ORM, Encryption, Versioning" --> Files
    DB -- "Versioning Metadata" --> Git
    Managers -- "Event Logging" --> EventLog
    QML -- "Displays" --> Images
```

---

## 2. Module Breakdown

### 2.1 QML UI (`app/qml/Main.qml`)
- Defines all user interface pages: login, dashboard, project details, event log, calendar, project creation.
- Interacts with backend managers via exposed properties, signals, and slots.
- Handles navigation, user input, and displays data from backend.

### 2.2 PyQt Entry Point (`app/main.py`)
- Starts the PySide6 application and loads the QML UI.
- Instantiates and exposes backend managers to QML:
  - **AuthManager**: Authentication and user session.
  - **DashboardManager**: Loads projects/tasks for dashboard.
  - **ProjectManager**: Project/task CRUD, team management, Gantt/calendar data.
  - **UserManager**: User CRUD and lookup.
  - **LogEventBridge**: Event log access and updates.

### 2.3 Backend Core (`app/db.py`)
- SQLAlchemy ORM for all data: users, roles, permissions, projects, tasks, subtasks, files, events, messages.
- Handles:
  - Local authentication (bcrypt password hashes).
  - Role-based access control (admin/user/leader/member).
  - Project/task/subtask CRUD and assignment.
  - File metadata, upload, and access control.
  - Event and calendar management (events, invitees, PTO).
  - File versioning (GitPython, ODFDiff integration).
  - Data/file encryption (Fernet).
  - Event logging (append-only, local).
- All data is stored in local SQLite databases (`auth.db`, `app.db`).

### 2.4 File Versioning & Storage
- LibreOffice documents (ODT, ODS, etc.) are versioned using a local Git repository per file or project.
- Each edit/upload creates a Git commit, tracked in the `file_versions` table.
- ODFDiff is used for semantic diffs between document versions.
- Files are stored on the local filesystem; metadata and access rights are managed in the database.

### 2.5 Event Logging
- All significant actions (logins, CRUD, admin actions, errors) are appended to `event_log.txt` with timestamps.
- The log is local and never transmitted externally.
- The event log is accessible from the UI for audit and troubleshooting.

### 2.6 Security & Offline Operation
- All authentication, data, and file operations are handled locally.
- No web, HTTP, or remote dependencies.
- Data/file encryption is used for sensitive files.
- The application is fully usable offline.

### 2.7 UI Images & Diagrams
- UI wireframes and images are stored in [`images/`](images/), e.g., [`Dashboard_Wireframe.png`](images/Dashboard_Wireframe.png).
- Architecture diagrams (Mermaid or PNG) are referenced in this document.

---

### 2.8 Dashboard Logic, Eisenhower Matrix & LLM Integration

#### DashboardManager (Backend/QML API)
- Exposes user projects and Eisenhower matrix state to QML via properties and slots.
- Methods:
  - `loadProjects(user_id)`: Loads all projects for a user.
  - `projects` (Property): List of project dicts for QML.
  - `loadEisenhowerMatrixState(user_id, project_id)`: Loads Eisenhower matrix state for a user/project.
  - `eisenhowerMatrixState` (Property): Current Eisenhower matrix state (QML-accessible).
  - `setEisenhowerMatrixState(user_id, project_id, state_json)`: Updates Eisenhower matrix state.
- All methods are exposed to QML and update UI via signals.

#### Recategorization & Event Logging
- `recategorizeTaskOrSubtask(user_id, project_id, task_id, subtask_id, old_category, new_category)`:
  - Called by QML on drag-and-drop between Eisenhower matrix categories.
  - Updates category in DB and logs a structured event (with timestamp, user, project, task/subtask, old/new category, reasoning).
  - Event log is append-only (`event_log.txt`) and accessible in the UI.
- All recategorization and significant actions are logged for auditability.

#### TinyLlama/LLM Integration
- `suggestEisenhowerCategory(user_id, project_id, task_id, subtask_id)`:
  - Gathers recent event logs as context.
  - Calls TinyLlama LLM via local HTTP API (`http://localhost:8000/suggest`) to get category suggestion and reasoning.
  - Applies suggestion (if subtask) and logs the LLM suggestion event with full context and LLM response.
  - All LLM interactions are local; no external network calls.

#### QML API Exposure
- All backend logic for dashboard, Eisenhower matrix, recategorization, and LLM integration is exposed to QML via PySide6 properties and slots.
- QML UI interacts with backend by calling these slots and observing property changes (signals).

---
- **Dashboard/Eisenhower Matrix**: QML UI interacts with `DashboardManager` to fetch/update projects and Eisenhower matrix state.
- **Recategorization**: QML triggers `recategorizeTaskOrSubtask` on drag-and-drop; backend updates DB and logs event.
- **LLM Integration**: QML calls `suggestEisenhowerCategory`; backend gathers context, calls TinyLlama, applies/logs suggestion, and updates UI.
---

## 3. Data & Control Flow

- **UI → Backend**: QML UI calls backend manager methods via signals/slots for all actions (login, CRUD, navigation).
- **Backend → UI**: Backend managers emit signals and expose properties to update the UI with new data.
- **Database**: All persistent data is stored in local SQLite databases, accessed via SQLAlchemy ORM.
- **Files**: User files are stored locally; versioned files are managed by GitPython and tracked in the database.
- **Event Log**: All actions are logged locally and can be viewed in the UI.
- **Calendar/Events**: Calendar and event features are managed locally, with support for team events, invitees, and PTO.

---

## 4. Notable Features & Changes After Rollback

- **No client-server separation**: All logic is local; [`server.py`](app/server.py) is not used in the main flow.
- **Modern QML UI**: All user interaction is via QML, with backend managers exposed for logic.
- **Role-based access control**: Users have roles (admin, user, leader, member) with permissions managed in the database.
- **Event & Calendar system**: Local management of events, invitees, and personal time off.
- **File encryption**: Sensitive files are encrypted using Fernet.
- **Document versioning**: All document changes are versioned locally with GitPython and ODFDiff.
- **Offline-first**: No network or cloud dependencies.

---

## 5. Example UI Wireframe

See [`images/Dashboard_Wireframe.png`](images/Dashboard_Wireframe.png) for a visual overview of the dashboard layout.

---

## 6. Summary

This PyQt (PySide6/QML) application is a fully local, offline project management tool. All features—including authentication, project/task management, user/file management, dashboard, event logging, calendar/events, and document versioning—are implemented using local modules and resources. There are no web, HTTP, or remote dependencies of any kind.
