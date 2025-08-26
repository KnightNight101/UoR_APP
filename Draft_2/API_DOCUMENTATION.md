# API Documentation: Project Management Desktop Application

**Note:** The current application is a local desktop app. There is no REST API available for external integration or automation. The following documentation supersedes all previous API references.

---

## Current State

- **No REST API endpoints are available.**
- All features are accessed via the desktop UI.
- Any previously documented endpoints are not implemented in this version.

---

## Internal Interfaces

Some internal logic (for developers):

- The application uses local SQLite databases for data storage.
- Task, event, and file operations are performed via the desktop UI and internal Python classes.
- No HTTP endpoints are exposed for automation or integration.

---

## QML-Exposed Backend API

The following Python backend classes and methods are exposed to the QML UI via PySide6 properties and slots. These interfaces enable all dashboard, Eisenhower matrix, event logging, and LLM integration features.

### DashboardManager

- **projects**: `Property(list)`
  List of project dicts for the current user.

- **eisenhowerMatrixState**: `Property(QVariant)`
  Current Eisenhower matrix state for the selected user/project.

- **loadProjects(user_id)**: `@Slot(int)`
  Loads all projects for the given user.

- **loadEisenhowerMatrixState(user_id, project_id)**: `@Slot(int, int)`
  Loads Eisenhower matrix state for the given user/project.

- **setEisenhowerMatrixState(user_id, project_id, state_json)**: `@Slot(int, int, QVariant)`
  Updates Eisenhower matrix state for the given user/project.

- **recategorizeTaskOrSubtask(user_id, project_id, task_id, subtask_id, old_category, new_category)**: `@Slot(int, int, int, int, str, str)`
  Updates the category of a task/subtask and logs the event.

- **suggestEisenhowerCategory(user_id, project_id, task_id, subtask_id)**: `@Slot(int, int, int, int)`
  Calls the local LLM (TinyLlama) to suggest a category for a task/subtask, logs the suggestion, and updates state.

### Event Logging

- All recategorization and LLM suggestion actions are logged to `event_log.txt` with timestamp, user, project, task/subtask, old/new category, and reasoning.
- The event log is accessible in the UI via the `EventLogBridge` and `LogEventBridge` classes.

### QML Usage Example

```qml
// Accessing backend from QML
dashboardManager.loadProjects(userId)
dashboardManager.loadEisenhowerMatrixState(userId, projectId)
dashboardManager.setEisenhowerMatrixState(userId, projectId, state)
dashboardManager.recategorizeTaskOrSubtask(userId, projectId, taskId, subtaskId, oldCat, newCat)
dashboardManager.suggestEisenhowerCategory(userId, projectId, taskId, subtaskId)
```

---
## Legacy API Documentation

The following sections are obsolete and retained for historical reference only. They do not reflect the current state of the application after rollback.

<!--
[All previous endpoint, model, and SDK documentation removed for clarity. See version control for historical details.]
-->

---

## Contact

For questions about the current application or future API plans, contact the development team.