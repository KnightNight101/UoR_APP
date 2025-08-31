-- PostgreSQL schema for UoR_APP

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    permissions TEXT[],
    twofa_enabled BOOLEAN DEFAULT FALSE,
    twofa_secret VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    deadline DATE
);

CREATE TABLE IF NOT EXISTS team_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    status VARCHAR(50),
    assignee_id INTEGER REFERENCES users(id),
    parent_task_id INTEGER REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS sub_tasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    status VARCHAR(50)
);