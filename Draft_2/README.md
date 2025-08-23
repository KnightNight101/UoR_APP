# Project Management Platform - Draft_2

A comprehensive project management platform built with Flask backend and React frontend, designed for team collaboration, task management, and file sharing.

## Project Overview

This application is a full-stack project management platform that provides:

- **User Authentication & Role-Based Access Control** - Secure login system with user roles and permissions
- **Project Management** - Create and manage projects with team assignments
- **Task & Subtask Management** - Organize work with draggable task boards (Eisenhower Matrix), set deadlines, edit and delete tasks
- **File Management** - Upload, share, and manage project files with access controls
- **Document Version Control** - Git-based versioning for LibreOffice documents (ODT, ODS, etc.) with full history and diff support
- **Team Collaboration** - Assign tasks, manage project members, and track progress
- **Admin Dashboard** - Administrative tools for user management and system oversight

## Prerequisites

Before running this application, ensure you have the following installed:

- **Python 3.11+** - Backend runtime
- **Node.js 16+** - Frontend runtime and package management
- **npm or yarn** - Package manager for React dependencies
- **Docker** (optional) - For containerized deployment
- **Git** - Version control (for cloning, development, and document versioning)
- **GitPython** - Python library for Git integration (installed via requirements.txt)
- **ODFDiff** - For LibreOffice document diffing (installed via requirements.txt)

## Quick Start Guide

### Option 1: Manual Setup (Recommended for Development)

1. **Clone and navigate to the project**:
```bash
cd Draft_2
```

2. **Setup Backend**:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize the database
python app/db.py

# Start the Flask API server
python app/api_server.py
```
The backend will run on `http://localhost:5000`

3. **Setup Frontend** (in a new terminal):
```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Start development server
npm run dev
```
The frontend will run on `http://localhost:5173`

### Option 2: Docker Deployment

```bash
# Build and run with Docker
docker build -t draft2-app .
docker run -p 2200:2200 draft2-app
```

## Document Version Control

The platform integrates Git-based version control for LibreOffice documents (ODT, ODS, etc.):

- **Automatic Versioning**: Every upload or edit of a LibreOffice document is committed to a dedicated Git repository.
- **History & Rollback**: Users can view the full version history, compare changes (using ODFDiff), and restore previous versions.
- **Collaboration**: Multiple users can work on documents with tracked changes and merge support.
- **UI Integration**: The file management UI provides version history, diff viewing, and restore options for each document.
- **Dependencies**: Uses GitPython for repository operations and ODFDiff for semantic document comparison.

## Development Setup

### Backend Setup

1. **Virtual Environment** (recommended):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Database Initialization**:
```bash
# Initialize database and create test admin user
python app/db.py
```

**Note**: The requirements.txt file now includes all necessary dependencies:
- Flask==3.0.0 (Web framework)
- SQLAlchemy==2.0.23 (Database ORM)
- bcrypt==4.1.2 (Password hashing)
- GitPython==3.1.40 (Git integration for document versioning)
- ODFDiff==2.3.0 (LibreOffice document diffing)

### Frontend Setup

1. **Install Dependencies**:
```bash
cd ui
npm install
```

2. **Development Scripts**:
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## Running the Application

### Development Mode

**Terminal 1 - Backend**:
```bash
cd Draft_2
python app/api_server.py
```

**Terminal 2 - Frontend**:
```bash
cd Draft_2/ui
npm run dev
```

### Production Mode

**Backend**:
```bash
# Set production environment
export FLASK_ENV=production  # Linux/macOS
set FLASK_ENV=production     # Windows

python app/api_server.py
```

**Frontend**:
```bash
cd ui
npm run build
npm run preview
```

### Access Points

- **Frontend Application**: `http://localhost:5173` (development) / `http://localhost:4173` (preview)
- **Backend API**: `http://localhost:5000`

## Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t draft2-project .

# Run the container
docker run -p 2200:2200 -p 5000:5000 draft2-project
```

### Docker Configuration

The [`Dockerfile`](Dockerfile:1) is configured to:
- Use Python 3.11 slim base image
- Create a non-root user for security
- Install Python dependencies
- Copy application code
- Expose port 2200 for SSH server
- Run the SSH server by default

**Note**: The current Dockerfile runs the SSH server. To run the Flask API server instead, modify the CMD instruction:
```dockerfile
CMD ["python", "app/api_server.py"]
```

## Project Structure

```
Draft_2/
├── app/                          # Backend Flask application
│   ├── api_server.py            # Flask API server (port 5000)
│   ├── db.py                    # Database models and connection
│   ├── schema.sql               # Database schema definition
│   └── auth.db                  # SQLite database (auto-generated)
├── ui/                          # React frontend application
│   ├── src/
│   │   ├── App.jsx              # Main React component with routing
│   │   ├── main.jsx             # React application entry point
│   │   ├── components/          # Reusable React components
│   │   │   └── Header.jsx       # Navigation header component
│   │   └── pages/               # React page components
│   │       ├── Authentication.jsx    # Login/signup page
│   │       ├── Dashboard.jsx         # Main dashboard with task boards
│   │       ├── ProjectCreation.jsx   # Project creation form
│   │       ├── AdminDashboard.jsx    # Administrative interface
│   │       ├── EmployeeList.jsx      # User management
│   │       ├── AddUser.jsx           # User creation form
│   │       ├── FileManagement.jsx    # File upload/management
│   │       └── TaskSubtaskManagement.jsx # Task organization
│   ├── public/                  # Static assets
│   ├── package.json             # Frontend dependencies
│   └── vite.config.js           # Vite configuration
├── config/                      # Configuration files
├── tests/                       # Test files
│   └── test_placeholder.py     # Placeholder test file
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .dockerignore               # Docker ignore patterns
└── README.md                   # This file
```

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

## Frontend Access

### Main Application

1. **Start the development server**: `npm run dev` in the `ui/` directory
2. **Open your browser**: Navigate to `http://localhost:5173`

### Available Pages

- **Authentication** (`/`) - Login and registration interface
- **Dashboard** (`/dashboard`) - Main task management with Eisenhower Matrix
  - Drag-and-drop task organization
  - Set, edit, and delete task deadlines
  - Edit and delete tasks directly from the dashboard
  - Four priority categories: Urgent & Important, Urgent, Important, Others
  - Project overview panel
- **Project Creation** (`/create-project`) - Form to create new projects
- **Admin Dashboard** (`/admin-dashboard`) - Administrative tools
- **Employee List** (`/employee-list`) - User management interface
- **Add User** (`/add-user`) - User registration form

### UI Features

- **Material-UI Components** - Professional, responsive design
- **Drag & Drop** - Task organization with `@hello-pangea/dnd`
- **React Router** - Client-side navigation
- **Responsive Design** - Works on desktop and mobile devices
- **Document Versioning UI** - File management screens now include version history, diff viewing (with ODFDiff), and restore options for LibreOffice documents. Users can browse, compare, and revert document versions directly from the UI.

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
   - Vite will automatically use the next available port
   - Check the terminal output for the actual URL

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

- Use browser developer tools to debug React components
- Check the browser console for JavaScript errors
- Monitor network requests to debug API calls
- Use `console.log()` for debugging React state changes

### Performance Considerations

- The React app uses Vite for fast development builds
- Material-UI components are optimized for production
- SQLite is suitable for development but consider PostgreSQL for production
- Implement proper error boundaries in React for production use

## Next Steps

For continued development:

1. **Complete API Implementation** - Implement remaining CRUD operations for projects, tasks, and files (including task deadlines, editing, and deletion)
2. **Authentication Integration** - Connect React frontend to Flask authentication endpoints  
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