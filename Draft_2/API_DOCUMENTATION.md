# Project Management Platform API Documentation

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management Endpoints](#user-management-endpoints)
4. [Project Management Endpoints](#project-management-endpoints)
5. [Task Management Endpoints](#task-management-endpoints)
6. [File Management Endpoints](#file-management-endpoints)
7. [Role and Permission Endpoints](#role-and-permission-endpoints)
8. [Error Response Schema](#error-response-schema)
9. [Data Models](#data-models)
10. [Request/Response Examples](#requestresponse-examples)
11. [SDK Integration](#sdk-integration)
12. [Testing Guidelines](#testing-guidelines)

## API Overview

### Base URL and Versioning
- **Base URL**: `http://localhost:5000/api` (Development)
- **Production URL**: `https://your-domain.com/api`
- **API Version**: v1 (current)
- **Content Type**: `application/json`

### Authentication Methods
The API supports JWT-based authentication with the following flow:
1. Login with username/password to receive JWT token
2. Include token in Authorization header: `Bearer <token>`
3. Refresh tokens before expiration using refresh endpoint

### Response Formats
All responses return JSON with consistent structure:
```json
{
  "data": {},
  "message": "Success message",
  "status": "success|error",
  "timestamp": "2025-01-20T14:29:00Z"
}
```

### Error Handling Standards
- HTTP status codes follow REST conventions
- Error responses include detailed error messages
- Validation errors return field-specific error details
- Server errors return generic error messages for security

### Rate Limiting
- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- Rate limit headers included in responses

---

## Authentication Endpoints

### POST /api/auth/login
**Status**: Planned  
**Description**: Authenticate user and return JWT token

#### Request Body
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

#### Response (200 OK)
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "john_doe",
      "roles": ["user"]
    }
  },
  "message": "Login successful",
  "status": "success"
}
```

#### Error Responses
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

---

### POST /api/auth/logout
**Status**: Planned  
**Description**: Invalidate JWT token and logout user

#### Headers
```
Authorization: Bearer <token>
```

#### Response (200 OK)
```json
{
  "message": "Logout successful",
  "status": "success"
}
```

---

### POST /api/auth/refresh
**Status**: Planned  
**Description**: Refresh expired JWT token using refresh token

#### Request Body
```json
{
  "refresh_token": "string (required)"
}
```

#### Response (200 OK)
```json
{
  "data": {
    "token": "new_jwt_token",
    "expires_in": 3600
  },
  "message": "Token refreshed successfully",
  "status": "success"
}
```

---

### GET /api/auth/me
**Status**: Planned  
**Description**: Get current authenticated user information

#### Headers
```
Authorization: Bearer <token>
```

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "created_at": "2025-01-01T00:00:00Z",
    "roles": [
      {
        "id": 1,
        "name": "user",
        "description": "Standard user role"
      }
    ]
  },
  "status": "success"
}
```

---

## User Management Endpoints

### GET /api/users
**Status**: ✅ Implemented  
**Description**: List all users (admin only)

#### Headers
```
Authorization: Bearer <token>
```

#### Query Parameters
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)
- `search`: Search by username

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "username": "john_doe",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "username": "jane_smith",
      "created_at": "2025-01-02T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "pages": 1
  },
  "status": "success"
}
```

#### Permissions Required
- `users.read` or admin role

---

### GET /api/user-count
**Status**: ✅ Implemented  
**Description**: Get total count of users

#### Response (200 OK)
```json
{
  "data": {
    "count": 25
  },
  "status": "success"
}
```

---

### POST /api/users
**Status**: ✅ Implemented  
**Description**: Create new user

#### Request Body
```json
{
  "username": "string (required, 3-50 chars)",
  "password": "string (required, min 8 chars)",
  "role": "string (optional, default: 'user')"
}
```

#### Response (201 Created)
```json
{
  "data": {
    "id": 3,
    "username": "new_user",
    "created_at": "2025-01-20T14:29:00Z"
  },
  "message": "User created successfully",
  "status": "success"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Username already exists

#### Permissions Required
- `users.create` or admin role

---

### GET /api/users/{id}
**Status**: Planned  
**Description**: Get specific user details

#### Path Parameters
- `id`: User ID (integer)

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "created_at": "2025-01-01T00:00:00Z",
    "roles": [
      {
        "id": 1,
        "name": "user"
      }
    ],
    "projects": [
      {
        "id": 1,
        "name": "Project Alpha",
        "role": "owner"
      }
    ]
  },
  "status": "success"
}
```

#### Permissions Required
- `users.read` or own profile

---

### PUT /api/users/{id}
**Status**: Planned  
**Description**: Update user information

#### Path Parameters
- `id`: User ID (integer)

#### Request Body
```json
{
  "username": "string (optional)",
  "password": "string (optional, min 8 chars)"
}
```

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "username": "updated_username",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "message": "User updated successfully",
  "status": "success"
}
```

#### Permissions Required
- `users.update` or own profile

---

### DELETE /api/users/{id}
**Status**: Planned  
**Description**: Delete user account

#### Path Parameters
- `id`: User ID (integer)

#### Response (200 OK)
```json
{
  "message": "User deleted successfully",
  "status": "success"
}
```

#### Permissions Required
- `users.delete` or admin role

---

## Project Management Endpoints

### GET /api/projects
**Status**: Planned  
**Description**: List projects accessible to current user

#### Query Parameters
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20)
- `search`: Search by project name
- `owner_id`: Filter by owner ID
- `member`: Include projects where user is a member

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "name": "Project Alpha",
      "description": "Main development project",
      "created_at": "2025-01-01T00:00:00Z",
      "owner": {
        "id": 1,
        "username": "john_doe"
      },
      "member_count": 5,
      "task_count": 12,
      "user_role": "owner"
    }
  ],
  "status": "success"
}
```

---

### POST /api/projects
**Status**: Planned  
**Description**: Create new project

#### Request Body
```json
{
  "name": "string (required, max 100 chars)",
  "description": "string (optional, max 1000 chars)",
  "members": [
    {
      "user_id": 2,
      "role": "member"
    }
  ]
}
```

#### Response (201 Created)
```json
{
  "data": {
    "id": 2,
    "name": "New Project",
    "description": "Project description",
    "created_at": "2025-01-20T14:29:00Z",
    "owner_id": 1
  },
  "message": "Project created successfully",
  "status": "success"
}
```

---

### GET /api/projects/{id}
**Status**: Planned  
**Description**: Get project details

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "name": "Project Alpha",
    "description": "Main development project",
    "created_at": "2025-01-01T00:00:00Z",
    "owner": {
      "id": 1,
      "username": "john_doe"
    },
    "members": [
      {
        "user_id": 2,
        "username": "jane_smith",
        "role": "member",
        "joined_at": "2025-01-02T00:00:00Z"
      }
    ],
    "statistics": {
      "total_tasks": 12,
      "completed_tasks": 8,
      "pending_tasks": 4,
      "overdue_tasks": 1
    }
  },
  "status": "success"
}
```

---

### PUT /api/projects/{id}
**Status**: Planned  
**Description**: Update project information

#### Request Body
```json
{
  "name": "string (optional)",
  "description": "string (optional)"
}
```

#### Permissions Required
- Project owner or `projects.update`

---

### DELETE /api/projects/{id}
**Status**: Planned  
**Description**: Delete project (owner only)

#### Response (200 OK)
```json
{
  "message": "Project deleted successfully",
  "status": "success"
}
```

---

### GET /api/projects/{id}/members
**Status**: Planned  
**Description**: Get project members

#### Response (200 OK)
```json
{
  "data": [
    {
      "user_id": 1,
      "username": "john_doe",
      "role": "owner",
      "joined_at": "2025-01-01T00:00:00Z"
    },
    {
      "user_id": 2,
      "username": "jane_smith",
      "role": "member",
      "joined_at": "2025-01-02T00:00:00Z"
    }
  ],
  "status": "success"
}
```

---

### POST /api/projects/{id}/members
**Status**: Planned  
**Description**: Add member to project

#### Request Body
```json
{
  "user_id": "integer (required)",
  "role": "string (optional, default: 'member')"
}
```

#### Response (201 Created)
```json
{
  "data": {
    "user_id": 3,
    "username": "new_member",
    "role": "member",
    "joined_at": "2025-01-20T14:29:00Z"
  },
  "message": "Member added successfully",
  "status": "success"
}
```

---

## Task Management Endpoints

### GET /api/projects/{id}/tasks
**Status**: Planned  
**Description**: Get tasks for a specific project

#### Query Parameters
- `status`: Filter by task status (pending, in_progress, completed)
- `assigned_to`: Filter by assigned user ID
- `due_date_from`: Filter tasks due after date (ISO 8601)
- `due_date_to`: Filter tasks due before date (ISO 8601)
- `page`: Page number
- `limit`: Results per page

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "title": "Implement user authentication",
      "description": "Add JWT-based authentication system",
      "status": "in_progress",
      "priority": "high",
      "assigned_to": {
        "id": 2,
        "username": "jane_smith"
      },
      "due_date": "2025-01-25T00:00:00Z",
      "created_at": "2025-01-15T00:00:00Z",
      "subtask_count": 3,
      "completed_subtasks": 1
    }
  ],
  "status": "success"
}
```

---

### POST /api/projects/{id}/tasks
**Status**: Planned  
**Description**: Create new task in project

#### Request Body
```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (optional, max 2000 chars)",
  "assigned_to": "integer (optional)",
  "due_date": "string (optional, ISO 8601)",
  "priority": "string (optional: low, medium, high, urgent)",
  "status": "string (optional, default: 'pending')"
}
```

#### Response (201 Created)
```json
{
  "data": {
    "id": 2,
    "title": "New Task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "assigned_to": null,
    "due_date": null,
    "created_at": "2025-01-20T14:29:00Z",
    "project_id": 1
  },
  "message": "Task created successfully",
  "status": "success"
}
```

---

### GET /api/tasks/{id}
**Status**: Planned  
**Description**: Get task details with subtasks

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication system",
    "status": "in_progress",
    "priority": "high",
    "assigned_to": {
      "id": 2,
      "username": "jane_smith"
    },
    "due_date": "2025-01-25T00:00:00Z",
    "created_at": "2025-01-15T00:00:00Z",
    "project": {
      "id": 1,
      "name": "Project Alpha"
    },
    "subtasks": [
      {
        "id": 1,
        "title": "Design authentication flow",
        "status": "completed",
        "assigned_to": {
          "id": 2,
          "username": "jane_smith"
        }
      }
    ]
  },
  "status": "success"
}
```

---

### PUT /api/tasks/{id}
**Status**: Planned  
**Description**: Update task information

#### Request Body
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "status": "string (optional)",
  "priority": "string (optional)",
  "assigned_to": "integer (optional, null to unassign)",
  "due_date": "string (optional, ISO 8601, null to remove)"
}
```

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "title": "Updated task title",
    "status": "completed",
    "priority": "high",
    "assigned_to": {
      "id": 3,
      "username": "new_assignee"
    },
    "updated_at": "2025-01-20T14:29:00Z"
  },
  "message": "Task updated successfully",
  "status": "success"
}
```

---

### DELETE /api/tasks/{id}
**Status**: Planned  
**Description**: Delete task and all subtasks

#### Response (200 OK)
```json
{
  "message": "Task and all subtasks deleted successfully",
  "status": "success"
}
```

---

### GET /api/tasks/{id}/subtasks
**Status**: Planned  
**Description**: Get all subtasks for a task

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "title": "Design authentication flow",
      "description": "Create wireframes and flow diagrams",
      "status": "completed",
      "assigned_to": {
        "id": 2,
        "username": "jane_smith"
      },
      "due_date": "2025-01-20T00:00:00Z",
      "created_at": "2025-01-15T00:00:00Z"
    }
  ],
  "status": "success"
}
```

---

### POST /api/tasks/{id}/subtasks
**Status**: Planned  
**Description**: Create new subtask

#### Request Body
```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (optional, max 1000 chars)",
  "assigned_to": "integer (optional)",
  "due_date": "string (optional, ISO 8601)",
  "status": "string (optional, default: 'pending')"
}
```

#### Response (201 Created)
```json
{
  "data": {
    "id": 2,
    "title": "New Subtask",
    "description": "Subtask description",
    "status": "pending",
    "assigned_to": null,
    "due_date": null,
    "created_at": "2025-01-20T14:29:00Z",
    "task_id": 1
  },
  "message": "Subtask created successfully",
  "status": "success"
}
```

---

## File Management Endpoints

### GET /api/files
**Status**: Planned  
**Description**: List accessible files

#### Query Parameters
- `project_id`: Filter by project ID
- `owner_id`: Filter by owner ID
- `access_level`: Filter by access level (private, project, public)
- `mimetype`: Filter by MIME type
- `page`: Page number
- `limit`: Results per page

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "filename": "project_requirements.pdf",
      "size": 2048576,
      "mimetype": "application/pdf",
      "uploaded_at": "2025-01-15T00:00:00Z",
      "owner": {
        "id": 1,
        "username": "john_doe"
      },
      "access_level": "project",
      "edit_level": "owner",
      "download_url": "/api/files/1/download",
      "shared_with": 5
    }
  ],
  "status": "success"
}
```

---

### POST /api/files
**Status**: Planned  
**Description**: Upload new file

#### Request (Multipart Form Data)
- `file`: File to upload (required)
- `access_level`: Access level (optional, default: 'private')
- `edit_level`: Edit level (optional, default: 'owner')
- `project_id`: Associate with project (optional)

#### Response (201 Created)
```json
{
  "data": {
    "id": 2,
    "filename": "uploaded_file.pdf",
    "size": 1024000,
    "mimetype": "application/pdf",
    "uploaded_at": "2025-01-20T14:29:00Z",
    "owner_id": 1,
    "access_level": "private",
    "edit_level": "owner",
    "path": "/uploads/2025/01/20/uploaded_file_abc123.pdf"
  },
  "message": "File uploaded successfully",
  "status": "success"
}
```

#### Error Responses
- `400 Bad Request`: No file provided or file too large
- `415 Unsupported Media Type`: File type not allowed

---

### GET /api/files/{id}
**Status**: Planned  
**Description**: Download file

#### Response (200 OK)
Binary file content with appropriate headers:
```
Content-Type: [file mimetype]
Content-Disposition: attachment; filename="[filename]"
Content-Length: [file size]
```

#### Error Responses
- `403 Forbidden`: No access to file
- `404 Not Found`: File not found

---

### PUT /api/files/{id}
**Status**: Planned  
**Description**: Update file metadata

#### Request Body
```json
{
  "filename": "string (optional)",
  "access_level": "string (optional)",
  "edit_level": "string (optional)"
}
```

#### Response (200 OK)
```json
{
  "data": {
    "id": 1,
    "filename": "updated_filename.pdf",
    "access_level": "public",
    "edit_level": "project",
    "updated_at": "2025-01-20T14:29:00Z"
  },
  "message": "File metadata updated successfully",
  "status": "success"
}
```

---

### DELETE /api/files/{id}
**Status**: Planned  
**Description**: Delete file (owner only)

#### Response (200 OK)
```json
{
  "message": "File deleted successfully",
  "status": "success"
}
```

---

### POST /api/files/{id}/share
**Status**: Planned  
**Description**: Share file with users or projects

#### Request Body
```json
{
  "users": [1, 2, 3],
  "projects": [1],
  "can_edit": false
}
```

#### Response (200 OK)
```json
{
  "message": "File shared successfully",
  "data": {
    "shared_with_users": 3,
    "shared_with_projects": 1
  },
  "status": "success"
}
```

---

## Role and Permission Endpoints

### GET /api/roles
**Status**: Planned  
**Description**: List all available roles

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "name": "admin",
      "description": "System administrator with full access",
      "permissions": [
        {
          "id": 1,
          "name": "users.create"
        },
        {
          "id": 2,
          "name": "users.read"
        }
      ]
    },
    {
      "id": 2,
      "name": "user",
      "description": "Standard user role",
      "permissions": [
        {
          "id": 3,
          "name": "projects.create"
        }
      ]
    }
  ],
  "status": "success"
}
```

---

### GET /api/permissions
**Status**: Planned  
**Description**: List all available permissions

#### Response (200 OK)
```json
{
  "data": [
    {
      "id": 1,
      "name": "users.create",
      "description": "Create new users"
    },
    {
      "id": 2,
      "name": "users.read",
      "description": "View user information"
    },
    {
      "id": 3,
      "name": "projects.create",
      "description": "Create new projects"
    }
  ],
  "status": "success"
}
```

---

### POST /api/users/{id}/roles
**Status**: Planned  
**Description**: Assign role to user

#### Request Body
```json
{
  "role_id": "integer (required)"
}
```

#### Response (201 Created)
```json
{
  "message": "Role assigned successfully",
  "data": {
    "user_id": 1,
    "role_id": 2,
    "role_name": "user"
  },
  "status": "success"
}
```

#### Permissions Required
- `users.manage_roles` or admin role

---

### DELETE /api/users/{id}/roles/{role_id}
**Status**: Planned  
**Description**: Remove role from user

#### Response (200 OK)
```json
{
  "message": "Role removed successfully",
  "status": "success"
}
```

---

## Error Response Schema

All error responses follow this standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": ["Field-specific error messages"]
    }
  },
  "status": "error",
  "timestamp": "2025-01-20T14:29:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict (e.g., duplicate username)
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

---

## Data Models

### User Model
```json
{
  "id": "integer",
  "username": "string",
  "password_hash": "string (never returned in responses)",
  "created_at": "string (ISO 8601)",
  "roles": ["array of role objects"],
  "projects": ["array of project objects where user is owner/member"]
}
```

### Project Model
```json
{
  "id": "integer",
  "name": "string",
  "description": "string|null",
  "created_at": "string (ISO 8601)",
  "owner_id": "integer",
  "owner": "user object",
  "members": ["array of project member objects"],
  "tasks": ["array of task objects"]
}
```

### Task Model
```json
{
  "id": "integer",
  "project_id": "integer",
  "title": "string",
  "description": "string|null",
  "status": "string (pending|in_progress|completed|cancelled)",
  "priority": "string (low|medium|high|urgent)",
  "assigned_to": "integer|null",
  "due_date": "string (ISO 8601)|null",
  "created_at": "string (ISO 8601)",
  "project": "project object",
  "assignee": "user object|null",
  "subtasks": ["array of subtask objects"]
}
```

### File Model
```json
{
  "id": "integer",
  "filename": "string",
  "path": "string",
  "size": "integer (bytes)",
  "mimetype": "string",
  "uploaded_at": "string (ISO 8601)",
  "owner_id": "integer",
  "access_level": "string (private|project|public)",
  "edit_level": "string (owner|project|any)",
  "owner": "user object",
  "projects": ["array of associated project objects"]
}
```

### Role Model
```json
{
  "id": "integer",
  "name": "string",
  "description": "string|null",
  "permissions": ["array of permission objects"]
}
```

### Permission Model
```json
{
  "id": "integer",
  "name": "string",
  "description": "string|null"
}
```

---

## Request/Response Examples

### Complete User Registration and Project Creation Flow

#### 1. Create User Account
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123",
    "role": "user"
  }'
```

#### 2. Login to Get Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

#### 3. Create Project
```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Project",
    "description": "A sample project for testing",
    "members": [
      {
        "user_id": 2,
        "role": "member"
      }
    ]
  }'
```

#### 4. Create Task in Project
```bash
curl -X POST http://localhost:5000/api/projects/1/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT-based authentication system",
    "priority": "high",
    "assigned_to": 2,
    "due_date": "2025-01-25T00:00:00Z"
  }'
```

#### 5. Upload Project File
```bash
curl -X POST http://localhost:5000/api/files \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@requirements.pdf" \
  -F "access_level=project" \
  -F "project_id=1"
```

---

## SDK Integration

### JavaScript/TypeScript Frontend Integration

#### API Client Setup
```javascript
class ApiClient {
  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('jwt_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error?.message || 'Request failed');
    }

    return data;
  }

  // Authentication
  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    this.token = data.data.token;
    localStorage.setItem('jwt_token', this.token);
    return data;
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' });
    this.token = null;
    localStorage.removeItem('jwt_token');
  }

  // Users
  async getUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/users${query ? `?${query}` : ''}`);
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Projects
  async getProjects(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/projects${query ? `?${query}` : ''}`);
  }

  async createProject(projectData) {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  async getProject(id) {
    return this.request(`/projects/${id}`);
  }

  // Tasks
  async getProjectTasks(projectId, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/projects/${projectId}/tasks${query ? `?${query}` : ''}`);
  }

  async createTask(projectId, taskData) {
    return this.request(`/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId, updates) {
    return this.request(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // File upload
  async uploadFile(file, metadata = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.entries(metadata).forEach(([key, value]) => {
      formData.append(key, value);
    });

    return this.request('/files', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }
}

// Usage example
const api = new ApiClient();

// Login and create project
async function createProjectWorkflow() {
  try {
    await api.login('john_doe', 'password123');
    
    const project = await api.createProject({
      name: 'New Project',
      description: 'Project created via API',
    });
    
    const task = await api.createTask(project.data.id, {
      title: 'First task',
      priority: 'high',
      due_date: '2025-01-25T00:00:00Z',
    });
    
    console.log('Project and task created successfully!');
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

#### React Hook Integration
```javascript
// hooks/useApi.js
import { useState, useEffect, useContext, createContext } from 'react';
import ApiClient from './ApiClient';

const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [api] = useState(new ApiClient());
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('jwt_token');
      if (token) {
        try {
          const userData = await api.request('/auth/me');
          setUser(userData.data);
        } catch (error) {
          localStorage.removeItem('jwt_token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [api]);

  return (
    <ApiContext.Provider value={{ api, user, setUser, loading }}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within ApiProvider');
  }
  return context;
};

// Custom hooks for specific resources
export const useProjects = () => {
  const { api } = useApi();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchProjects = async (params = {}) => {
    setLoading(true);
    try {
      const response = await api.getProjects(params);
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (projectData) => {
    const response = await api.createProject(projectData);
    setProjects(prev => [...prev, response.data]);
    return response;
  };

  return {
    projects,
    loading,
    fetchProjects,
    createProject,
  };
};
```

---

## Testing Guidelines

### Unit Testing API Endpoints

#### Test Setup (Python/pytest)
```python
import pytest
import json
from app.api_server import app
from app.db import SessionLocal, User, Project

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(client):
    # Create test user and login
    response = client.post('/api/users', 
        json={'username': 'testuser', 'password': 'testpass123'})
    
    login_response = client.post('/api/auth/login',
        json={'username': 'testuser', 'password': 'testpass123'})
    
    token = login_response.json['data']['token']
    return {'Authorization': f'Bearer {token}'}

def test_get_users(client, auth_headers):
    response = client.get('/api/users', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert 'data' in data
    assert isinstance(data['data'], list)

def test_create_user(client):
    user_data = {
        'username': 'newuser',
        'password': 'password123',
        'role': 'user'
    }
    response = client.post('/api/users', json=user_data)
    assert response.status_code == 201
    data = response.json
    assert data['data']['username'] == 'newuser'

def test_create_project(client, auth_headers):
    project_data = {
        'name': 'Test Project',
        'description': 'A test project'
    }
    response = client.post('/api/projects', 
        json=project_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json
    assert data['data']['name'] == 'Test Project'

def test_authentication_required(client):
    response = client.get('/api/users')
    assert response.status_code == 401
```

#### Integration Testing (JavaScript/Jest)
```javascript
// tests/api.test.js
import ApiClient from '../src/ApiClient';

describe('API Integration Tests', () => {
  let api;
  let testUser;

  beforeAll(async () => {
    api = new ApiClient('http://localhost:5000/api');
    
    // Create test user
    testUser = await api.request('/users', {
      method: 'POST',
      body: JSON.stringify({
        username: 'testuser',
        password: 'testpass123'
      })
    });
  });

  beforeEach(async () => {
    // Login before each test
    await api.login('testuser', 'testpass123');
  });

  afterEach(async () => {
    // Cleanup after each test
    await api.logout();
  });

  test('should create and retrieve project', async () => {
    const projectData = {
      name: 'Integration Test Project',
      description: 'Created by integration test'
    };

    const created = await api.createProject(projectData);
    expect(created.data.name).toBe(projectData.name);

    const retrieved = await api.getProject(created.data.id);
    expect(retrieved.data.id).toBe(created.data.id);
    expect(retrieved.data.name).toBe(projectData.name);
  });

  test('should create task and subtasks', async () => {
    // Create project first
    const project = await api.createProject({
      name: 'Task Test Project'
    });

    // Create task
    const task = await api.createTask(project.data.id, {
      title: 'Test Task',
      priority: 'high'
    });

    expect(task.data.title).toBe('Test Task');
    expect(task.data.priority).toBe('high');

    // Create subtask
    const subtask = await api.request(`/tasks/${task.data.id}/subtasks`, {
      method: 'POST',
      body: JSON.stringify({
        title: 'Test Subtask'
      })
    });

    expect(subtask.data.title).toBe('Test Subtask');
    expect(subtask.data.task_id).toBe(task.data.id);
  });

  test('should handle file upload', async () => {
    const file = new Blob(['test content'], { type: 'text/plain' });
    file.name = 'test.txt';

    const uploaded = await api.uploadFile(file, {
      access_level: 'private'
    });

    expect(uploaded.data.filename).toBe('test.txt');
    expect(uploaded.data.access_level).toBe('private');
  });
});
```

### Load Testing
```bash
# Using Apache Bench (ab)
ab -n 1000 -c 10 -H "Authorization: Bearer YOUR_TOKEN" \
   http://localhost:5000/api/users

# Using curl for basic endpoint testing
curl -w "@curl-format.txt" -o /dev/null -s \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/projects
```

### API Documentation Testing
```bash
# Test all endpoints return valid JSON
endpoints=(
  "/api/users"
  "/api/user-count"
  "/api/projects"
  "/api/roles"
  "/api/permissions"
)

for endpoint in "${endpoints[@]}"; do
  echo "Testing $endpoint"
  curl -s -H "Authorization: Bearer $TOKEN" \
       "http://localhost:5000$endpoint" | jq empty
  if [ $? -eq 0 ]; then
    echo "✓ Valid JSON"
  else
    echo "✗ Invalid JSON"
  fi
done
```

---

## Implementation Status Legend

- ✅ **Implemented**: Feature is complete and functional
- 🔄 **In Progress**: Feature is being developed
- 📋 **Planned**: Feature is documented and planned for development
- ❌ **Not Implemented**: Feature is not yet started

---

This documentation will be updated as new endpoints are implemented and existing ones are modified. For the most current API status, refer to the implementation status indicators next to each endpoint.