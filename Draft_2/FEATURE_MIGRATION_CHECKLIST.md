# Feature Migration Checklist: PyQt5 (`oldmain.py`) → PySide6 + QML

## 1. Core Pages & Navigation
- [ ] Login screen (logo, username/password, login button, scaling/zoom)
- [ ] Dashboard (tabbed: Dashboard, Calendar, Members, Event Log)
- [ ] Project Creation (with team member/leader selection, structured tasks)
- [ ] Project Detail (tabs: Team Members, Tasks, Gantt Chart, Calendar)
- [ ] Subtask Detail (with file management, VCS, LibreOffice integration)
- [ ] Messaging (send/receive, refresh, dialog)
- [ ] User/Settings dialogs (side menu, scaling, logout)
- [ ] Event Log (live updates, refresh, scroll to top)

## 2. Dashboard Features
- [ ] 3-column layout: Projects, My Subtasks (4 categories, drag/drop), Messages
- [ ] Project list: open detail, create project
- [ ] Subtask lists: 4 categories, drag-and-drop, status dropdown, open details
- [ ] Message list: refresh, send message dialog
- [ ] User icon/menu (top right): performance, archived, settings, logout

## 3. Project Creation
- [ ] Project name, description, deadline
- [ ] Team member selection (multi), leader selection (multi)
- [ ] Structured task entry (title, deadline, assigned, dependencies, hours)
- [ ] Add/remove task rows, dependency dialog
- [ ] Save/cancel, validation, auto-assign creator as leader

## 4. Project Detail
- [ ] Tabs: Team Members, Tasks, Gantt Chart, Calendar
- [ ] Team member list, add/change leader, roles
- [ ] Task list: add/edit/delete, dependencies, hours, assign, subtask conversion
- [ ] Subtask list: indented, edit/delete, parent task
- [ ] Gantt chart: filter by member, dependencies, hours
- [ ] Calendar: deadlines, events, holidays, PTO

## 5. Subtask Detail
- [ ] Subtask info: assigned, project, parent task, deadline
- [ ] File management: list, upload, delete, LibreOffice file creation
- [ ] VCS: status, history, diff, revert, commit
- [ ] Back navigation

## 6. Messaging
- [ ] Send message dialog (recipient, content)
- [ ] Message list (from/to, timestamp, refresh)

## 7. Event Log
- [ ] Live updates (append on actions)
- [ ] Refresh button
- [ ] Scroll to top

## 8. Settings/User Menu
- [ ] Scaling/zoom controls
- [ ] Logout
- [ ] Settings dialog

## 9. Connections & Logic
- [ ] All signal/slot connections (button clicks, list item clicks, drag/drop, dialog opens)
- [ ] All backend calls (db, file, VCS, etc.)
- [ ] All event logging (log_event, log_error)
- [ ] All navigation flows (stack, tab, dialog)

---

**Legend:**  
[ ] = Not started  
[-] = In progress  
[x] = Complete
