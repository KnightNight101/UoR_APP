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
