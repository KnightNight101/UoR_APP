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

## Backend Models, Logic, Event Logging, and LLM Integration

### 1. Models and Logic

- **Tasks & Subtasks**: Each project contains tasks, which may have subtasks. Both support titles, descriptions, deadlines, assignment to team members, and dependencies (stored as lists of task/subtask IDs).
- **Dependencies**: Tasks and subtasks can depend on others. Dependencies are enforced in plan generation and deadline calculation.
- **Deadlines**: Projects, tasks, and subtasks have deadlines. Deadlines are used in scheduling, plan verification, and LLM suggestions.
- **Team Member Assignment**: Tasks and subtasks can be assigned to project members. Assignment is tracked in the database and exposed to the UI.
- **Descriptions**: All tasks and subtasks support rich text descriptions for context and requirements.

### 2. Event Logging

- **All actions** (task/subtask creation, editing, recategorization, assignment, deadline changes, deletions) are logged to `event_log.txt` with timestamp, user, project, task/subtask, action type, and details.
- **LLM Suggestions**: When the LLM (TinyLlama) suggests a category, deadline, or plan, the suggestion and its reasoning are logged as structured events.
- **User Edits & Planning**: Manual changes by users (e.g., recategorization, assignment, deadline edits) are logged with before/after state and reasoning if provided.
- **Auditability**: The event log is append-only and accessible in the UI for audit and troubleshooting.

### 3. TinyLlama Integration

- **Time/Verification Suggestions**: The backend integrates TinyLlama to suggest deadlines and verify plan feasibility. Suggestions consider dependencies, deadlines, team availability, and 8-hour workdays.
- **Project Plan Generation**: TinyLlama can generate a project plan, assigning deadlines and resources while respecting dependencies and immovable deadlines.
- **Output & Reasoning Logging**: All LLM outputs (suggestions, plans, verifications) and their reasoning/context are logged to the event log for transparency.
- **API Methods**:
  - `suggest_time_for_task(task, project, team_members, immovable_deadlines=None)`: Suggests a deadline for a task.
  - `generate_project_plan(project_id)`: Generates a full project plan considering all constraints.
  - `verify_plan_feasibility(plan, immovable_deadlines=None)`: Verifies if a plan is feasible.

### 4. Plan Generation Logic

- **Dependencies**: Tasks/subtasks are scheduled respecting all dependencies (no task starts before its dependencies are complete).
- **Deadlines**: Both project-level and task-level deadlines are enforced. Immovable deadlines are strictly respected.
- **Team Availability**: Assignment considers team member workload and availability.
- **Workday Constraints**: Scheduling assumes 8-hour workdays for all team members.
- **Immovable Deadlines**: Tasks with fixed deadlines are never rescheduled beyond their set date.

### 5. QML-Exposed Backend APIs

All backend logic is exposed to the QML UI via PySide6 properties and slots, including:

- **Project and Task Management**:
  - `loadProjects(user_id)`
  - `projects` (Property)
  - `loadEisenhowerMatrixState(user_id, project_id)`
  - `eisenhowerMatrixState` (Property)
  - `setEisenhowerMatrixState(user_id, project_id, state_json)`
  - `recategorizeTaskOrSubtask(user_id, project_id, task_id, subtask_id, old_category, new_category)`
  - `suggestEisenhowerCategory(user_id, project_id, task_id, subtask_id)`

- **LLM Planning and Suggestions**:
  - `suggest_time_for_task`
  - `generate_project_plan`
  - `verify_plan_feasibility`

- **Event Logging**:
  - All significant actions and LLM interactions are logged and accessible via `EventLogBridge` and `LogEventBridge`.

---

This section provides a comprehensive overview of backend models, logic, event logging, LLM integration, plan generation, and QML-exposed APIs for developers and testers.
---
## Legacy API Documentation

The following sections are obsolete and retained for historical reference only. They do not reflect the current state of the application after rollback.

<!--
[All previous endpoint, model, and SDK documentation removed for clarity. See version control for historical details.]
-->

---

## Contact

For questions about the current application or future API plans, contact the development team.