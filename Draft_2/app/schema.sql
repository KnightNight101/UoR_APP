-- User authentication and access control schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, -- Store only password hashes, never plaintext
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Multi-tenancy: Tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add tenant_id to users
-- NOTE: This ALTER TABLE is handled idempotently in db.py and is safe to keep here.
ALTER TABLE users ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);


CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Project management schema

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    deadline TEXT, -- New: deadline for the project
    tasks TEXT,    -- New: JSON-encoded list of tasks (optional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);
-- Migration: Add deadline column to projects if not present
ALTER TABLE projects ADD COLUMN deadline TEXT;

-- Add tenant_id to projects
-- NOTE: This ALTER TABLE is handled idempotently in db.py and is safe to keep here.
ALTER TABLE projects ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);

-- Migration: Add hours and dependencies to tasks if not present
ALTER TABLE tasks ADD COLUMN hours REAL;
ALTER TABLE tasks ADD COLUMN dependencies TEXT;

-- Migration: Add hours and dependencies to subtasks if not present
ALTER TABLE subtasks ADD COLUMN hours REAL;
ALTER TABLE subtasks ADD COLUMN dependencies TEXT;


CREATE TABLE IF NOT EXISTS project_members (
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    assigned_to INTEGER,
    due_date TIMESTAMP,
    hours REAL, -- New: estimated/actual hours for the task
    dependencies TEXT, -- New: JSON-encoded list of task/subtask IDs this task depends on
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    assigned_to INTEGER,
    due_date TIMESTAMP,
    hours REAL, -- New: estimated/actual hours for the subtask
    dependencies TEXT, -- New: JSON-encoded list of task/subtask IDs this subtask depends on
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- File management schema

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    size INTEGER,
    mimetype TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id INTEGER NOT NULL,
    access_level TEXT NOT NULL DEFAULT 'private', -- 'private', 'project', 'public'
    edit_level TEXT NOT NULL DEFAULT 'owner',    -- 'owner', 'project', 'any'
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_files (
    project_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    can_edit BOOLEAN NOT NULL DEFAULT 0,
    can_view BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (project_id, file_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);
-- GitHub repository integration schema

CREATE TABLE IF NOT EXISTS github_repos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    repo_url TEXT NOT NULL,
    access_token TEXT, -- Store securely, consider encryption in production
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS file_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    repo_id INTEGER NOT NULL,
    commit_hash TEXT NOT NULL,
    version INTEGER NOT NULL,
    committed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author TEXT,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (repo_id) REFERENCES github_repos(id) ON DELETE CASCADE
);