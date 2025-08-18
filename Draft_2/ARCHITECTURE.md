# Draft_2 Project Management Platform - System Architecture

## Overview

This document describes the architecture of the fully local, offline PyQt-based Project Management Platform. The application is a desktop solution with no web, HTTP, or remote dependencies. All data, authentication, and user interactions are handled locally on the user's machine.

---

## 1. Application Structure

The platform is implemented as a standalone PyQt application. The main modules and their responsibilities are:

- **[`main.py`](app/main.py:1)**: Entry point for the PyQt application. Initializes the main window, loads UI components, and manages application state.
- **[`db.py`](app/db.py:1)**: Handles all database operations using SQLite. Manages schema creation, user/project/task/file CRUD, queries, and Git-based document version control for LibreOffice files (using GitPython and ODFDiff).
- **Event Log (`event_log.txt`)**: Plaintext log file for recording significant application events, user actions, and errors for audit and debugging purposes.

All modules interact directly; there is no client-server separation or network communication.

---

## 2. Main Modules and Responsibilities

### main.py

- Initializes the PyQt application and main window.
- Handles navigation between authentication, dashboard, project/task management, and user/file management screens.
- Connects UI actions to backend logic (database, event logging).

### db.py

- Manages the local SQLite database.
- Provides functions for:
  - User authentication and management
  - Project and task CRUD operations
  - File metadata storage and access control
- Ensures all data remains local and secure.

### Event Log

- Appends timestamped entries for:
  - User logins/logouts
  - Project/task/file operations
  - Administrative actions
  - Errors and exceptions
- Used for troubleshooting and auditing.

---

## 3. Feature Implementation

### Authentication

- Local authentication using usernames and password hashes stored in SQLite.
- No external authentication providers or network requests.
- Login/logout events are recorded in the event log.

### Project & Task Management

- Projects and tasks are stored in the local database.
- Users can create, edit, assign, set deadlines, and delete projects and tasks via the PyQt interface.
- Task deadlines are stored and updated in the database and UI.
- All changes, including task edits and deletions, are logged.

### User & File Management

- User management (creation, update, deletion) is handled locally.
- Files are stored on the local filesystem; metadata and access rights are managed in the database.
- LibreOffice documents (ODT, ODS, etc.) are versioned using a local Git repository per file or project. Each edit/upload creates a Git commit, tracked in the database (`file_versions` table).
- File operations (add, remove, update, version, restore) are logged.

### Dashboard

- The dashboard provides an overview of projects, tasks, and recent activity.
- All data is loaded from the local database; no remote data sources.
- The dashboard and file management UI now include document versioning features: version history, diff viewing, and restore options for LibreOffice documents.

### Event Logging

- All significant actions are appended to `event_log.txt` with timestamps.
- The log is local and never transmitted externally.

---

## 3.1. Document Version Control Workflow

- When a LibreOffice document is uploaded or edited, the application uses GitPython to commit the new version to a local Git repository.
- The `file_versions` table records each commit, including commit hash, author, and timestamp.
- ODFDiff is used to provide semantic diffs between document versions, accessible from the UI.
- The file management UI allows users to view version history, compare versions, and restore previous versions.
- All versioning operations are local and offline, with no external dependencies.


## 4. Security and Offline Operation

- All data and authentication are handled locally.
- No web, HTTP, or remote dependencies.
- No external APIs, cloud storage, or network communication.
- The application can be used entirely offline.

---

## 5. Summary

This PyQt application is a fully local, offline project management tool. All features—including authentication, project/task management, user/file management, dashboard, and event logging—are implemented using local modules and resources. There are no web, HTTP, or remote dependencies of any kind.