# Testing Approach for Project Management Desktop Application

This document describes the current testing approach and relevant manual test scenarios for the local desktop application after rollback.

---

## Current Testing Approach

- **Automated tests:** No meaningful automated tests are present. The `tests/` directory contains only a placeholder.
- **Manual testing:** All testing is currently performed manually by the development team.
- **Test focus:** Manual tests focus on core workflows, UI interactions, and data integrity within the desktop application.

---

## Manual Test Scenarios

### 1. Task and Event Management

- **Create Task:** Add a new task via the desktop UI. Confirm it appears in the task list.
- **Edit Task:** Edit an existing task's details and verify changes persist.
- **Delete Task:** Remove a task and ensure it is no longer listed.
- **Create Event:** Add a calendar event and confirm it appears in the event list.
- **Edit/Delete Event:** Edit or delete an event and verify the change.

### 2. File Operations

- **Open/Save File:** Open and save files using the application's file dialogs.
- **File Encryption:** Confirm files are encrypted at rest (if feature is present).

### 3. User Management

- **Login:** Log in with valid and invalid credentials.
- **User Listing:** View the user list and confirm correct display.

### 4. UI/UX

- **Navigation:** Navigate between main screens (dashboard, tasks, events, files).
- **Responsiveness:** Resize the window and verify layout adapts.
- **Accessibility:** Attempt keyboard navigation for major actions.

---

## Notes

- No REST API endpoints are available for external testing.
- All test cases are executed manually using the desktop UI.
- Automated and integration testing should be reintroduced as features are redeveloped.

### DashboardManager Backend Testing (2025-08-26)

#### Chronology and Issue Resolution

- **Initial Test Failures:**
  The first test runs for [`Draft_2/tests/test_dashboard_manager.py`] failed due to a mismatch between Qt object types. Specifically, `qtbot.addWidget(dm)` was called on a `DashboardManager` instance, which is a `QObject` and not a `QWidget`. This caused test initialization errors.
- **Rectification:**
  The erroneous `qtbot.addWidget(dm)` call was removed, as it is unnecessary for `QObject` subclasses. After this fix, all tests executed as intended.
- **Final Results:**
  All dashboard-related backend tests now pass successfully.

#### Dashboard Test Coverage

Each test is described below with its purpose, relevance, and result:

- **`test_load_projects_and_matrix_state`**
  *What it covers:*
  Verifies that the dashboard can load projects for a user, retrieve Eisenhower matrix state for a project, and handle invalid user/project IDs gracefully.
  *Why it's relevant:*
  Ensures core data loading and error handling for the dashboard's main views.
  *Result:*
  Passed. Projects are loaded as lists with expected structure; invalid IDs yield empty results.

- **`test_recategorize_and_event_logging`**
  *What it covers:*
  Tests recategorization of tasks/subtasks and triggers event logging, including edge cases with invalid IDs.
  *Why it's relevant:*
  Confirms that user actions (like changing task urgency) are processed and logged, supporting auditability and correct UI feedback.
  *Result:*
  Passed. Recategorization works for valid and invalid IDs; event log update is triggered.

- **`test_llm_suggestion_and_reasoning_logging`**
  *What it covers:*
  Simulates LLM-based category suggestions and reasoning logging, including handling of unexpected LLM responses.
  *Why it's relevant:*
  Validates integration with AI-driven suggestions and robustness against malformed responses.
  *Result:*
  Passed. LLM suggestions are processed and logged; unexpected data is handled without error.

- **`test_qml_api_methods_exposed`**
  *What it covers:*
  Checks that all required dashboard methods are exposed to the QML frontend.
  *Why it's relevant:*
  Guarantees that the UI can interact with backend logic as intended.
  *Result:*
  Passed. All expected methods are present.

#### Deprecation Warning

- During test execution, a warning was raised:
  `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in Python 3.12.`
  This warning does **not** affect test outcomes or application behavior.

#### Test Command

Command used:
```
python -m pytest Draft_2/tests/test_dashboard_manager.py --tb=short -v
```

## Project Details Page Backend Testing Summary (2025-08-26)

### Backend Logic and API Endpoints

- **Project Creation:**
  `POST /projects`
  Payload:
  ```json
  {
    "name": "Project Name",
    "description": "Project description",
    "owner_id": 1,
    "members": [{"user_id": 1}],
    "deadline": "YYYY-MM-DD",
    "tasks": []
  }
  ```
  Creates a new project with metadata, deadline, description, and initial team members.

- **Project Metadata and Editing:**
  `GET /projects/<project_id>`
  Returns project details, including name, description, deadline, owner, and members.

  `PUT /projects/<project_id>`
  Updates project metadata (name, description) by owner.

- **Team Member Assignment:**
  `POST /projects/<project_id>/members`
  Adds a new member to the project.
  Payload:
  ```json
  {
    "user_id": 1,
    "new_member_id": 2,
    "role": "member"
  }
  ```

- **Event Logging:**
  All project creation and team assignment actions are logged to the `event_logs` table via the `log_structured_event` function.
  Event logs include action type, user, project, and timestamp.
  Example:
  - Project created
  - Member assigned

### Test Coverage

- Automated tests in [`test_project_details_backend.py`](Draft_2/tests/test_project_details_backend.py:1) cover:
  - Project creation with all fields (name, description, owner, members, deadline)
  - Team member assignment
  - Event logging for both actions (checked in `event_log.txt`)
  - Task and subtask creation/editing
  - LLM integration and plan generation

### Initial Failures

- Tests failed due to:
  - Missing `event_logs` table in the database schema.
  - Incorrect or incomplete payloads (missing required fields).
  - Test database not initialized with required users/projects.

### Rectifications

- Added `event_logs` table to schema and ensured migrations applied.
- Updated test payloads to match backend API requirements.
- Added setup steps in tests to create required users and projects before running API calls.

### Final Results

- All backend feature tests now pass after rectifications.
- Event logging for project creation and team assignment is verified by checking `event_log.txt` and database entries.
- API endpoints for project management, metadata, deadlines, descriptions, and team assignment are fully covered by tests.


## LLM Feature Set Test Results (2025-08-27)

### Multi-Factor Planner
- **test_generate_project_plan**: PASS
- **test_suggest_time_for_task**: PASS
- **test_verify_plan_feasibility**: PASS

### Eisenhower Matrix Categorization
- **test_suggest_eisenhower_category**: **FAIL**
  - **Error**: AttributeError: `<module 'Draft_2.app.main'>` does not have the attribute `update_subtask_category`
  - **Details**: The test attempts to patch or access `update_subtask_category` in `main.py`, but this function is missing. This prevents the Eisenhower matrix categorization feature from being fully tested.

### VCS Commit Summary
- **test_llm_commit_summary**: PASS

#### Summary
- **4/5 tests passed.**
- **1 test failed** due to a missing function in the codebase, not a logic error in the feature itself.
- **Recommendation**: Implement or restore `update_subtask_category` in [`Draft_2/app/main.py`] to enable full testing of the Eisenhower matrix categorization feature.

## Eisenhower Matrix Subtask Categorization & LLM Integration

All tests in [`Draft_2/tests/test_llm_features.py`] passed:

- Subtask Eisenhower matrix category updates are correctly applied and logged as structured events.
- LLM-driven category suggestions for subtasks are integrated and event-logged.
- All event log, LLM, and categorization features are verified by automated tests.

Test run: 5 passed, 0 failed.
