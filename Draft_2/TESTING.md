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
