## QML Login Page UI

The QML-based login page (`app/qml/Main.qml`) provides a simple, user-friendly authentication interface for the desktop client. Its structure and design rationale are as follows:

- **ApplicationWindow**: Sets up the main window with a fixed size and a white background for a clean, modern look.
- **Login State Properties**: Tracks login status, username, password, and error messages using QML properties.
- **Login Page Layout**:
  - The login form is centered using an `Item` and a rounded `Rectangle` with a blue border for visual focus.
  - An optional shadow can be enabled for depth.
  - The upper two-thirds of the login box displays the application logo, reinforcing branding.
  - The lower third contains a vertical stack (`ColumnLayout`) of:
    - Username and password fields (with password masking)
    - A login button
    - An error message area for invalid credentials
- **Login Logic**: The login button checks for a non-empty username and a password of "password" (for demonstration). On success, the dashboard is shown; otherwise, an error message is displayed.
- **Design Rationale**:
  - The layout is responsive, with maximum width/height constraints for usability on various screen sizes.
  - Visual hierarchy is established by separating branding (logo) from interaction (inputs).
  - The use of QML's property bindings ensures real-time UI updates and a smooth user experience.
  - All UI elements are styled for clarity and accessibility.

For further customization or integration, see the detailed comments in [`Main.qml`](app/qml/Main.qml:1).

## Configuration

### Environment Variables

The application supports the following environment variables:

- `AUTH_DB_PATH` - Path to SQLite database (default: `auth.db`)
- `FLASK_ENV` - Flask environment (`development`/`production`)
- `FLASK_HOST` - Flask host (default: `0.0.0.0`)
- `FLASK_PORT` - Flask port (default: `5000`)

### Database Configuration

The application uses SQLite with the database path configurable via `AUTH_DB_PATH`. The database schema includes:

- **User Management**: [`users`](app/schema.sql:3), [`roles`](app/schema.sql:10), [`permissions`](app/schema.sql:16)
- **Projects**: [`projects`](app/schema.sql:40), [`project_members`](app/schema.sql:49)
- **Tasks**: [`tasks`](app/schema.sql:58), [`subtasks`](app/schema.sql:71)
- **Files**: [`files`](app/schema.sql:86), [`project_files`](app/schema.sql:99)
- **Version Control**: [`github_repos`](app/schema.sql:110), [`file_versions`](app/schema.sql:119)
    - [`file_versions`](app/schema.sql:119): Tracks every version of each document, including commit hash, author, timestamp, and links to the Git repository.
    - Relationships: Each file can have multiple versions; each version is linked to a Git commit and repository.

## Database Setup

### Initialize Database

```bash
# Initialize database with schema and create test admin user
python app/db.py
```

This will:
- Create the SQLite database at `app/auth.db`
- Initialize all database tables from the schema
- Create a test admin user (username: `admin`, password: `admin123`)

### Database Schema

The database will be automatically created with tables for:
- User authentication and role-based access control
- Project management with team assignments
- Task and subtask organization
- File management with access controls
- GitHub repository integration for version control

### Test Credentials

After running the database initialization, you can use these test credentials:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator

## API Endpoints

The Flask backend provides the following API endpoints:

### User Management
- `GET /api/users` - Get all users
- `GET /api/user-count` - Get total user count
- `POST /api/users` - Create new user
  ```json
  {
    "username": "string",
    "password": "string", 
    "role": "admin|user"
  }
  ```

### Response Format
Success responses return JSON with data or confirmation messages:
```json
{
  "message": "User created successfully"
}
```

Error responses include error details:
```json
{
  "error": "Username already exists"
}
```

**Note**: Additional endpoints for projects, tasks, and files are defined in the schema but not yet implemented in [`api_server.py`](app/api_server.py:1).

## Desktop Application Access

### Main Application

1. **Start the desktop application**: `python app/main.py`
2. The QML-based UI will launch as a native desktop window.

### Main Screens

- **Authentication** (Login dialog) - Login and registration interface
- **Dashboard** - Main task management with Eisenhower Matrix
  - Drag-and-drop task organization (QML native)
  - Set, edit, and delete task deadlines
  - Edit and delete tasks directly from the dashboard
  - Four priority categories: Urgent & Important, Urgent, Important, Others
  - Project overview panel
- **Project Creation** - Form to create new projects
- **Admin Dashboard** - Administrative tools
- **Employee List** - User management interface
- **Add User** - User registration form

### UI Features

- **QML/QtQuick Controls** - Modern, responsive desktop UI components
- **Native Drag & Drop** - Task organization using QML drag-and-drop
- **Consistent Desktop Experience** - Optimized for Windows, macOS, and Linux
- **Document Versioning UI** - File management screens include version history, diff viewing (with ODFDiff), and restore options for LibreOffice documents. Users can browse, compare, and revert document versions directly from the UI.

## Troubleshooting

### Common Issues

**Backend Issues:**

1. **`ModuleNotFoundError: No module named 'flask'`**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database connection errors**
   ```bash
   python app/db.py
   ```

3. **Port already in use (5000)**
   ```bash
   # Find and kill process using port 5000
   lsof -ti:5000 | xargs kill -9  # macOS/Linux
   netstat -ano | findstr :5000   # Windows
   ```

**Frontend Issues:**

1. **Dependencies not found**
   ```bash
   cd ui
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Build errors**
   ```bash
   npm run lint  # Check for syntax errors
   ```

3. **Port conflicts (5173)**
   - This port is not used in the QML desktop application. If you see port conflicts, ensure no other services are running on required backend ports.

**Docker Issues:**

1. **Build failures**
   ```bash
   docker system prune  # Clean up Docker cache
   docker build --no-cache -t draft2-app .
   ```

2. **Container won't start**
   ```bash
   docker logs <container-id>  # Check logs for errors
   ```

### Development Tips

- Use Python logging and print statements to debug backend logic
- Use QML's `console.log()` for debugging UI state changes
- Monitor terminal output for errors and status messages
- Check `event_log.txt` for application event logs

### Performance Considerations

- The QML desktop app launches instantly with Python and PySide6
- QtQuick Controls provide a consistent, professional UI
- SQLite is suitable for development but consider PostgreSQL for production
- Implement robust error handling in both Python and QML for production use

## Next Steps

For continued development:

1. **Complete API Implementation** - Implement remaining CRUD operations for projects, tasks, and files (including task deadlines, editing, and deletion)
2. **Authentication Integration** - Connect QML frontend to Flask authentication endpoints
3. **File Upload System** - Implement file management features
4. **Real-time Updates** - Add WebSocket support for collaborative features
5. **Testing** - Add comprehensive unit and integration tests
6. **Production Deployment** - Configure for production with proper environment variables and database

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make changes and test thoroughly
4. Commit changes (`git commit -am 'Add new feature'`)
5. Push to branch (`git push origin feature/new-feature`)
6. Create a Pull Request

## License

This project is part of an academic development effort. Please refer to your institution's guidelines for usage and distribution.