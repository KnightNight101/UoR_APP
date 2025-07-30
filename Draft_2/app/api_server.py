from flask import Flask, request, jsonify, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import secrets
import os
from db import (
    SessionLocal, User, Project, ProjectMember, init_db, register_user, authenticate_user,
    get_user_by_id, store_refresh_token, validate_refresh_token,
    blacklist_refresh_token, init_roles_and_permissions, cleanup_expired_tokens,
    create_project, get_user_projects, get_project_by_id, update_project,
    delete_project, get_project_members, add_project_member, remove_project_member,
    get_project_statistics, encrypt_file, decrypt_file
)
from sqlalchemy import func

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

# --- Event Logging Utility ---
import threading
import traceback

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "event_log.txt")
_log_lock = threading.Lock()

def log_event(event_type, endpoint, method, request_data=None, action=None, result=None, error=None, status_code=None):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    log_line = (
        f"[{timestamp}] {event_type} | {method} {endpoint} | "
        f"Request: {repr(request_data)} | Action: {action} | "
        f"Result: {repr(result)} | Error: {repr(error)} | Status: {status_code}\n"
    )
    with _log_lock:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(log_line)

@app.before_request
def log_request():
    if request.path.startswith("/static"):
        return
    try:
        data = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                data = request.get_json(force=False, silent=True)
            except Exception:
                data = None
        log_event(
            event_type="REQUEST",
            endpoint=request.path,
            method=request.method,
            request_data=data if data is not None else dict(request.values),
            action="Received API call"
        )
    except Exception as e:
        log_event(
            event_type="LOGGING_ERROR",
            endpoint=request.path,
            method=request.method,
            error=f"Failed to log request: {repr(e)}"
        )

@app.after_request
def log_response(response):
    if request.path.startswith("/static"):
        return response
    try:
        log_event(
            event_type="RESPONSE",
            endpoint=request.path,
            method=request.method,
            status_code=response.status_code,
            result=response.get_data(as_text=True)[:500],  # Truncate for log size
            action="Sent API response"
        )
    except Exception as e:
        log_event(
            event_type="LOGGING_ERROR",
            endpoint=request.path,
            method=request.method,
            error=f"Failed to log response: {repr(e)}"
        )
    return response

@app.teardown_request
def log_teardown(exception):
    if exception:
        tb = traceback.format_exc()
        log_event(
            event_type="ERROR",
            endpoint=request.path,
            method=request.method,
            error=f"{repr(exception)}\n{tb}",
            action="Exception during request"
        )

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "API server is healthy"
    }), 200

import logging

@app.route("/db_status", methods=["GET"])
def db_status():
    from db import engine
    from sqlalchemy import text
    logger = logging.getLogger("db_status")
    if not logger.hasHandlers():
        logging.basicConfig(level=logging.INFO)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful for /db_status endpoint.")
        return jsonify({
            "db_connected": True,
            "status": "ok",
            "message": "Database connection successful"
        }), 200
    except Exception as e:
        logger.error(f"Database connection failed on /db_status endpoint: {repr(e)}", exc_info=True)
        return jsonify({
            "db_connected": False,
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 503

# --- Security Hardening: Session Management ---
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

import csv
from io import StringIO, BytesIO
from flask import send_file
from fpdf import FPDF

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# --- SSO Provider Configuration ---
app.config['SSO_PROVIDERS'] = {
    "google": {
        "client_id": "GOOGLE_CLIENT_ID",
        "client_secret": "GOOGLE_CLIENT_SECRET",
        "redirect_uri": "http://localhost:5000/api/auth/sso/callback"
    },
    "azure": {
        "client_id": "AZURE_CLIENT_ID",
        "client_secret": "AZURE_CLIENT_SECRET",
        "redirect_uri": "http://localhost:5000/api/auth/sso/callback"
    }
}

jwt = JWTManager(app)

# --- Security Hardening: Rate Limiting ---
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour", "20 per minute"]
)


# JWT Token Blacklist (in production, use Redis or database)
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if JWT token has been blacklisted."""
    return jwt_payload['jti'] in blacklisted_tokens

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired JWT tokens."""
    return jsonify({
        'error': {
            'code': 'AUTHENTICATION_ERROR',
            'message': 'Token has expired'
        },
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid JWT tokens."""
    return jsonify({
        'error': {
            'code': 'AUTHENTICATION_ERROR',
            'message': 'Invalid token'
        },
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """Handle missing JWT tokens."""
    return jsonify({
        'error': {
            'code': 'AUTHENTICATION_ERROR',
            'message': 'Authorization token is required'
        },
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 401

# Authentication Endpoints

# --- SSO Login Endpoint (Scaffold) ---
@app.route("/api/auth/sso/login", methods=["POST"])
def sso_login():
    """
    Placeholder for SSO login. Accepts provider and initiates SSO flow.
    """
    data = request.get_json()
    provider = data.get("provider")
    if provider not in app.config['SSO_PROVIDERS']:
        return jsonify({
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Unsupported SSO provider"
            },
            "status": "error"
        }), 400
    # TODO: Implement actual SSO flow (redirect, token exchange, etc.)
    return jsonify({
        "message": f"Initiate SSO login for provider: {provider}",
        "status": "success"
    }), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT tokens."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username and password are required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Initialize database and authenticate user
        init_db()
        user = authenticate_user(username, password)
        
        if not user:
            return jsonify({
                'error': {
                    'code': 'AUTHENTICATION_ERROR',
                    'message': 'Invalid credentials'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 401
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token_str = create_refresh_token(identity=user.id)
        
        # Store refresh token in database
        expires_at = datetime.utcnow() + timedelta(days=30)
        store_refresh_token(user.id, refresh_token_str, expires_at)
        
        # Get user roles
        roles = [role.name for role in user.roles] if user.roles else []
        
        return jsonify({
            'token': access_token,
            'refresh_token': refresh_token_str,
            'expires_in': 3600,  # 1 hour
            'user': {
                'id': user.id,
                'username': user.username,
                'roles': roles
            },
            'message': 'Login successful',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        log_event(
            event_type="ERROR",
            endpoint=request.path,
            method=request.method,
            request_data=request.get_json(silent=True),
            error=repr(e),
            action="Exception in /api/auth/refresh"
        )
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user and blacklist tokens."""
    try:
        # Get the JWT token ID to blacklist it
        jti = get_jwt()['jti']
        blacklisted_tokens.add(jti)
        
        # Also blacklist refresh token if provided
        data = request.get_json()
        if data and 'refresh_token' in data:
            blacklist_refresh_token(data['refresh_token'])
        
        return jsonify({
            'message': 'Logout successful',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/auth/refresh", methods=["POST"])
def refresh():
    """Refresh JWT access token using refresh token."""
    try:
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Refresh token is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        refresh_token_str = data['refresh_token']
        
        # Validate refresh token
        user = validate_refresh_token(refresh_token_str)
        if not user:
            return jsonify({
                'error': {
                    'code': 'AUTHENTICATION_ERROR',
                    'message': 'Invalid or expired refresh token'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 401
        
        # Create new access token
        new_access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'data': {
                'token': new_access_token,
                'expires_in': 3600
            },
            'message': 'Token refreshed successfully',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        log_event(
            event_type="ERROR",
            endpoint=request.path,
            method=request.method,
            error=repr(e),
            action="Exception in /api/auth/me"
        )
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current authenticated user information."""
    try:
        current_user_id = get_jwt_identity()
        user = get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'User not found'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 404
        
        # Get user roles with permissions
        roles_data = []
        if user.roles:
            for role in user.roles:
                roles_data.append({
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                })
        
        return jsonify({
            'data': {
                'id': user.id,
                'username': user.username,
                'created_at': user.created_at.isoformat() + 'Z',
                'roles': roles_data
            },
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

# Protected User Management Endpoints

@app.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    """List all users (admin only)."""
    try:
        init_db()
        with SessionLocal() as session:
            users = session.query(User).all()
            user_list = []
            for user in users:
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "created_at": user.created_at.isoformat() + 'Z' if user.created_at else None,
                }
                user_list.append(user_data)
        
        return jsonify({
            'data': user_list,
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/user-count", methods=["GET"])
@jwt_required()
def get_user_count():
    """Get total count of users."""
    try:
        init_db()
        with SessionLocal() as session:
            count = session.query(func.count(User.id)).scalar()
        
        return jsonify({
            'data': {'count': count},
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/users", methods=["POST"])
@jwt_required()
def create_user():
    """Create new user (admin only)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "user")
        
        if not username or not password:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username and password are required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Validate username length
        if len(username) < 3 or len(username) > 50:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username must be between 3 and 50 characters'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Validate password length
        if len(password) < 8:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Password must be at least 8 characters long'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        success = register_user(username, password, role)
        if success:
            # Get the created user
            user = authenticate_user(username, password)
            return jsonify({
                'data': {
                    'id': user.id if user else None,
                    'username': username,
                    'created_at': datetime.utcnow().isoformat() + 'Z'
                },
                'message': 'User created successfully',
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 201
        else:
            return jsonify({
                'error': {
                    'code': 'CONFLICT',
                    'message': 'Username already exists'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 409
            
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

# Project Management Endpoints

@app.route("/api/projects", methods=["GET"])
@jwt_required()
def get_projects():
    """List projects accessible to current user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 items per page
        search = request.args.get('search')
        
        # Get user's projects
        projects, total = get_user_projects(current_user_id, page, limit, search)
        
        # Format project data
        project_list = []
        for project in projects:
            # Get user's role in this project
            user_role = None
            for member in project.members:
                if member.user_id == current_user_id:
                    user_role = member.role
                    break
            
            # Count tasks and members
            task_count = len(project.tasks) if project.tasks else 0
            member_count = len(project.members) if project.members else 0
            
            project_data = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat() + 'Z' if project.created_at else None,
                "owner": {
                    "id": project.owner.id,
                    "username": project.owner.username
                } if project.owner else None,
                "member_count": member_count,
                "task_count": task_count,
                "user_role": user_role
            }
            project_list.append(project_data)
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        
        return jsonify({
            'data': project_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': pages
            },
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects", methods=["POST"])
@jwt_required()
def create_project_endpoint():
    """Create new project."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        name = data.get("name")
        description = data.get("description")
        members = data.get("members", [])
        
        if not name:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Project name is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Validate name length
        if len(name) > 100:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Project name must be 100 characters or less'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Validate description length
        if description and len(description) > 1000:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Project description must be 1000 characters or less'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Create project
        project = create_project(name, description, current_user_id, members)
        
        if not project:
            return jsonify({
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'Failed to create project'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500
        
        return jsonify({
            'data': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat() + 'Z' if project.created_at else None,
                'owner_id': project.owner_id
            },
            'message': 'Project created successfully',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project_details(project_id):
    """Get project details."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get project with permission checking
        project = get_project_by_id(project_id, current_user_id)
        
        if not project:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Project not found or access denied'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 404
        
        # Get project statistics
        stats = get_project_statistics(project_id, current_user_id)
        
        # Format members data
        members_data = []
        if project.members:
            for member in project.members:
                member_data = {
                    "user_id": member.user_id,
                    "username": member.user.username if member.user else None,
                    "role": member.role,
                    "joined_at": member.joined_at.isoformat() + 'Z' if member.joined_at else None
                }
                members_data.append(member_data)
        
        # Build response
        project_data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat() + 'Z' if project.created_at else None,
            "owner": {
                "id": project.owner.id,
                "username": project.owner.username
            } if project.owner else None,
            "members": members_data,
            "statistics": stats or {
                "total_tasks": 0,
                "member_count": len(members_data),
                "task_status_breakdown": {}
            }
        }
        
        return jsonify({
            'data': project_data,
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project_endpoint(project_id):
    """Update project information."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        name = data.get("name")
        description = data.get("description")
        
        # Validate input
        if name and len(name) > 100:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Project name must be 100 characters or less'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        if description and len(description) > 1000:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Project description must be 1000 characters or less'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Update project
        updated_project, error = update_project(project_id, current_user_id, name, description)
        
        if error:
            if error == "Permission denied":
                return jsonify({
                    'error': {
                        'code': 'AUTHORIZATION_ERROR',
                        'message': 'Insufficient permissions to update project'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 403
            elif error == "Project not found":
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Project not found'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 404
            else:
                return jsonify({
                    'error': {
                        'code': 'SERVER_ERROR',
                        'message': 'Failed to update project'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 500
        
        return jsonify({
            'data': {
                'id': updated_project.id,
                'name': updated_project.name,
                'description': updated_project.description,
                'created_at': updated_project.created_at.isoformat() + 'Z' if updated_project.created_at else None,
                'owner': {
                    "id": updated_project.owner.id,
                    "username": updated_project.owner.username
                } if updated_project.owner else None
            },
            'message': 'Project updated successfully',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project_endpoint(project_id):
    """Delete project (owner only)."""
    try:
        current_user_id = get_jwt_identity()
        
        success, error = delete_project(project_id, current_user_id)
        
        if not success:
            if error == "Project not found or permission denied":
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Project not found or insufficient permissions'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 404
            else:
                return jsonify({
                    'error': {
                        'code': 'SERVER_ERROR',
                        'message': 'Failed to delete project'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 500
        
        return jsonify({
            'message': 'Project deleted successfully',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/members", methods=["GET"])
@jwt_required()
def get_project_members_endpoint(project_id):
    """Get project members."""
    try:
        current_user_id = get_jwt_identity()
        
        members = get_project_members(project_id, current_user_id)
        
        if members is None:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Project not found or access denied'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 404
        
        # Format members data
        members_data = []
        for member in members:
            member_data = {
                "user_id": member.user_id,
                "username": member.user.username if member.user else None,
                "role": member.role,
                "joined_at": member.joined_at.isoformat() + 'Z' if member.joined_at else None
            }
            members_data.append(member_data)
        
        return jsonify({
            'data': members_data,
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/members", methods=["POST"])
@jwt_required()
def add_project_member_endpoint(project_id):
    """Add member to project."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        new_member_id = data.get("user_id")
        role = data.get("role", "member")
        
        if not new_member_id:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'User ID is required'
                },
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Add member to project
        new_member, error = add_project_member(project_id, current_user_id, new_member_id, role)
        
        if error:
            if error == "Permission denied":
                return jsonify({
                    'error': {
                        'code': 'AUTHORIZATION_ERROR',
                        'message': 'Insufficient permissions to add members'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 403
            elif error == "User is already a member":
                return jsonify({
                    'error': {
                        'code': 'CONFLICT',
                        'message': 'User is already a member of this project'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 409
            elif error == "User not found":
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'User not found'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 404
            else:
                return jsonify({
                    'error': {
                        'code': 'SERVER_ERROR',
                        'message': 'Failed to add member'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 500
        
        return jsonify({
            'data': {
                "user_id": new_member.user_id,
                "username": new_member.user.username if new_member.user else None,
                "role": new_member.role,
                "joined_at": new_member.joined_at.isoformat() + 'Z' if new_member.joined_at else None
            },
            'message': 'Member added successfully',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/members/<int:member_id>", methods=["DELETE"])
@jwt_required()
def remove_project_member_endpoint(project_id, member_id):
    """Remove member from project."""
    try:
        current_user_id = get_jwt_identity()
        
        success, error = remove_project_member(project_id, current_user_id, member_id)
        
        if not success:
            if error == "Permission denied":
                return jsonify({
                    'error': {
                        'code': 'AUTHORIZATION_ERROR',
                        'message': 'Insufficient permissions to remove members'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 403
            elif error == "Member not found":
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Member not found in this project'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 404
            elif error == "Cannot remove project owner":
                return jsonify({
                    'error': {
                        'code': 'AUTHORIZATION_ERROR',
                        'message': 'Cannot remove project owner'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 403
            else:
                return jsonify({
                    'error': {
                        'code': 'SERVER_ERROR',
                        'message': 'Failed to remove member'
                    },
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 500
        
        return jsonify({
            'message': 'Member removed successfully',
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'An unexpected error occurred'
            },
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

# Task Management Endpoints
from db import (
    create_task, get_tasks, get_task_by_id, update_task, delete_task,
    create_file, get_files, get_file_by_id, update_file, delete_file
)

@app.route("/api/projects/<int:project_id>/tasks", methods=["GET"])
@jwt_required()
def list_tasks(project_id):
    """List all tasks for a project."""
    try:
        current_user_id = get_jwt_identity()
        tasks = get_tasks(project_id)
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assigned_to": task.assigned_to,
                "due_date": task.due_date.isoformat() + 'Z' if task.due_date else None,
                "created_at": task.created_at.isoformat() + 'Z' if task.created_at else None
            })
        return jsonify({
            "data": task_list,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/tasks", methods=["POST"])
@jwt_required()
def create_task_endpoint(project_id):
    """Create a new task for a project."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        assigned_to = data.get("assigned_to")
        due_date = data.get("due_date")
        if not title:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Task title is required"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
        due_date_obj = datetime.fromisoformat(due_date) if due_date else None
        task = create_task(project_id, title, description, assigned_to, due_date_obj)
        if not task:
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Failed to create task"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        return jsonify({
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assigned_to": task.assigned_to,
                "due_date": task.due_date.isoformat() + 'Z' if task.due_date else None,
                "created_at": task.created_at.isoformat() + 'Z' if task.created_at else None
            },
            "message": "Task created successfully",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 201
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task_endpoint(project_id, task_id):
    """Get details of a specific task."""
    try:
        task = get_task_by_id(task_id)
        if not task or task.project_id != project_id:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        return jsonify({
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assigned_to": task.assigned_to,
                "due_date": task.due_date.isoformat() + 'Z' if task.due_date else None,
                "created_at": task.created_at.isoformat() + 'Z' if task.created_at else None
            },
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task_endpoint(project_id, task_id):
    """Update a task."""
    try:
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        status = data.get("status")
        assigned_to = data.get("assigned_to")
        due_date = data.get("due_date")
        due_date_obj = datetime.fromisoformat(due_date) if due_date else None
        task = update_task(task_id, title, description, status, assigned_to, due_date_obj)
        if not task or task.project_id != project_id:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        return jsonify({
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assigned_to": task.assigned_to,
                "due_date": task.due_date.isoformat() + 'Z' if task.due_date else None,
                "created_at": task.created_at.isoformat() + 'Z' if task.created_at else None
            },
            "message": "Task updated successfully",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task_endpoint(project_id, task_id):
    """Delete a task."""
    try:
        task = get_task_by_id(task_id)
        if not task or task.project_id != project_id:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        success = delete_task(task_id)
        if not success:
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Failed to delete task"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        return jsonify({
            "message": "Task deleted successfully",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

# File Management Endpoints
@app.route("/api/projects/<int:project_id>/files", methods=["GET"])
@jwt_required()
def list_files(project_id):
    """List all files for a project."""
    try:
        files = get_files(project_id)
        file_list = []
        for file in files:
            file_list.append({
                "id": file.id,
                "filename": file.filename,
                "description": file.description,
                "uploaded_by": file.uploaded_by,
                "uploaded_at": file.uploaded_at.isoformat() + 'Z' if file.uploaded_at else None,
                "task_id": file.task_id,
                "filepath": file.filepath
            })
        return jsonify({
            "data": file_list,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/files", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def upload_file_endpoint(project_id):
    """Upload a new file to a project (encrypted)."""
    try:
        current_user_id = get_jwt_identity()
        if 'file' not in request.files:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "No file part in request"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
        file_obj = request.files['file']
        filename = file_obj.filename
        description = request.form.get("description")
        task_id = request.form.get("task_id")
        # Save file to disk (encrypted)
        # Use absolute path for uploads, prevent overwrite, validate file type
        upload_dir = os.path.abspath(os.path.join("uploads", str(project_id)))
        os.makedirs(upload_dir, exist_ok=True)
        # Prevent file overwrite
        safe_filename = secrets.token_hex(8) + "_" + os.path.basename(filename)
        filepath = os.path.join(upload_dir, safe_filename)
        # Basic file extension validation (allow only .pdf, .docx, .xlsx, .png, .jpg, .txt)
        allowed_ext = {'.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg', '.txt'}
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_ext:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid file type"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
        try:
            file_obj.save(filepath)
        except Exception as e:
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Failed to save file: {str(e)}"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        # Encrypt after saving, handle encryption errors
        try:
            encrypt_file(filepath)
        except Exception as e:
            os.remove(filepath)
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Encryption failed: {str(e)}"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        file_record = create_file(project_id, safe_filename, filepath, current_user_id, description, int(task_id) if task_id else None)
        if not file_record:
            os.remove(filepath)
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Failed to save file record"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        return jsonify({
            "data": {
                "id": file_record.id,
                "filename": file_record.filename,
                "description": file_record.description,
                "uploaded_by": file_record.uploaded_by,
                "uploaded_at": file_record.uploaded_at.isoformat() + 'Z' if file_record.uploaded_at else None,
                "task_id": file_record.task_id,
                "filepath": file_record.filepath
            },
            "message": "File uploaded successfully (encrypted)",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 201
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/files/<int:file_id>", methods=["GET"])
@jwt_required()
@limiter.limit("30 per minute")
def get_file_endpoint(project_id, file_id):
    """Get details of a specific file (decrypted on access)."""
    try:
        file = get_file_by_id(file_id)
        if not file or file.project_id != project_id:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "File not found"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        # Decrypt file for access (temporary)
        # Decrypt file for access (temporary), handle errors
        try:
            decrypt_file(file.filepath)
        except Exception as e:
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Decryption failed: {str(e)}"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        return jsonify({
            "data": {
                "id": file.id,
                "filename": file.filename,
                "description": file.description,
                "uploaded_by": file.uploaded_by,
                "uploaded_at": file.uploaded_at.isoformat() + 'Z' if file.uploaded_at else None,
                "task_id": file.task_id,
                "filepath": file.filepath
            },
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/files/<int:file_id>", methods=["PUT"])
@jwt_required()
def update_file_endpoint(project_id, file_id):
    """Update file metadata."""
    try:
        data = request.get_json()
        filename = data.get("filename")
        description = data.get("description")
        file = update_file(file_id, filename, description)
        if not file or file.project_id != project_id:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "File not found"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        return jsonify({
            "data": {
                "id": file.id,
                "filename": file.filename,
                "description": file.description,
                "uploaded_by": file.uploaded_by,
                "uploaded_at": file.uploaded_at.isoformat() + 'Z' if file.uploaded_at else None,
                "task_id": file.task_id,
                "filepath": file.filepath
            },
            "message": "File updated successfully",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/files/<int:file_id>", methods=["DELETE"])
@jwt_required()
def delete_file_endpoint(project_id, file_id):
    """Delete a file."""
    try:
        file = get_file_by_id(file_id)
        if not file or file.project_id != project_id:
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "File not found"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        success = delete_file(file_id)
        if not success:
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Failed to delete file"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        return jsonify({
            "message": "File deleted successfully",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

# List/upload files for a specific task
@app.route("/api/projects/<int:project_id>/tasks/<int:task_id>/files", methods=["GET"])
@jwt_required()
def list_task_files(project_id, task_id):
    """List all files for a specific task."""
    try:
        files = get_files(project_id, task_id)
        file_list = []
        for file in files:
            file_list.append({
                "id": file.id,
                "filename": file.filename,
                "description": file.description,
                "uploaded_by": file.uploaded_by,
                "uploaded_at": file.uploaded_at.isoformat() + 'Z' if file.uploaded_at else None,
                "task_id": file.task_id,
                "filepath": file.filepath
            })
        return jsonify({
            "data": file_list,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route("/api/projects/<int:project_id>/tasks/<int:task_id>/files", methods=["POST"])
@jwt_required()
def upload_task_file_endpoint(project_id, task_id):
    """Upload a file for a specific task."""
    try:
        current_user_id = get_jwt_identity()
        if 'file' not in request.files:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "No file part in request"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
        file_obj = request.files['file']
        filename = file_obj.filename
        description = request.form.get("description")
        # Use absolute path for uploads, prevent overwrite, validate file type
        upload_dir = os.path.abspath(os.path.join("uploads", str(project_id), "tasks", str(task_id)))
        os.makedirs(upload_dir, exist_ok=True)
        safe_filename = secrets.token_hex(8) + "_" + os.path.basename(filename)
        filepath = os.path.join(upload_dir, safe_filename)
        allowed_ext = {'.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg', '.txt'}
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_ext:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid file type"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
        try:
            file_obj.save(filepath)
        except Exception as e:
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Failed to save file: {str(e)}"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        try:
            encrypt_file(filepath)
        except Exception as e:
            os.remove(filepath)
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Encryption failed: {str(e)}"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        file_record = create_file(project_id, safe_filename, filepath, current_user_id, description, task_id)
        if not file_record:
            os.remove(filepath)
            return jsonify({
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Failed to save file record"
                },
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 500
        return jsonify({
            "data": {
                "id": file_record.id,
                "filename": file_record.filename,
                "description": file_record.description,
                "uploaded_by": file_record.uploaded_by,
                "uploaded_at": file_record.uploaded_at.isoformat() + 'Z' if file_record.uploaded_at else None,
                "task_id": file_record.task_id,
                "filepath": file_record.filepath
            },
            "message": "File uploaded successfully",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 201
    except Exception as e:
        return jsonify({
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred"
            },
            "status": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500

# Initialize database and roles on startup
def initialize_application():
    """Initialize database, roles, and permissions."""
    try:
        print("Initializing application...")
        init_db()
        init_roles_and_permissions()
        cleanup_expired_tokens()
        print("Application initialized successfully")
    except Exception as e:
        print(f"Error initializing application: {e}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Endpoint not found'
        },
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'error': {
            'code': 'METHOD_NOT_ALLOWED',
            'message': 'Method not allowed for this endpoint'
        },
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': {
            'code': 'SERVER_ERROR',
            'message': 'Internal server error'
        },
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 500

if __name__ == "__main__":
    import threading
    import time

    # Ensure all Flask setup and route registration is complete before starting any threads or the server
    initialize_application()

    # PyInstaller compatibility: import pywebview inside main guard
    try:
        import webview
    except ImportError:
        webview = None

    def run_flask():
        # Flask's reloader must be disabled in threads
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

    print("Starting API server on http://localhost:5000")
    print("API Base URL: http://localhost:5000/api")
    print("\nAvailable Authentication Endpoints:")
    print("POST /api/auth/login - User login")
    print("POST /api/auth/logout - User logout")
    print("POST /api/auth/refresh - Refresh JWT token")
    print("GET  /api/auth/me - Get current user info")
    print("\nProtected User Endpoints:")
    print("GET  /api/users - List all users")
    print("POST /api/users - Create new user")
    print("GET  /api/user-count - Get user count")
    print("\nProject Management Endpoints:")
    print("GET  /api/projects - List user's projects")
    print("POST /api/projects - Create new project")
    print("GET  /api/projects/{id} - Get project details")
    print("PUT  /api/projects/{id} - Update project")
    print("DELETE /api/projects/{id} - Delete project")
    print("GET  /api/projects/{id}/members - Get project members")
    print("POST /api/projects/{id}/members - Add project member")
    print("DELETE /api/projects/{id}/members/{member_id} - Remove project member")

    # Start Flask server in a background thread (after all setup and route registration)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait for the server to be up before opening the UI
    def wait_for_server(url, timeout=15):
        import urllib.request
        start = time.time()
        while time.time() - start < timeout:
            try:
                with urllib.request.urlopen(url) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                time.sleep(0.5)
        return False

    server_ready = wait_for_server("http://localhost:5000/health")

    if webview is not None and server_ready:
        # Launch pywebview window as desktop UI
        webview.create_window("Project Management App", "http://localhost:5000", width=1200, height=800)
        webview.start()
    elif not server_ready:
        print("Error: Flask server did not start in time.")
    else:
        print("pywebview is not installed. Please install it to use the desktop UI.")


# --- Analytics Endpoints ---

@app.route("/api/analytics/project_stats", methods=["GET"])
@jwt_required()
def analytics_project_stats():
    """Return project statistics for all projects."""
    try:
        with SessionLocal() as session:
            projects = session.query(Project).all()
            stats = []
            for project in projects:
                stat = {
                    "project_id": project.id,
                    "name": project.name,
                    "created_at": project.created_at.isoformat() + 'Z' if project.created_at else None,
                    "task_count": len(project.tasks) if hasattr(project, "tasks") and project.tasks else 0,
                    "member_count": len(project.members) if hasattr(project, "members") and project.members else 0,
                }
                stats.append(stat)
        return jsonify({"data": stats, "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": {"code": "SERVER_ERROR", "message": str(e)}, "status": "error"}), 500

@app.route("/api/analytics/user_activity", methods=["GET"])
@jwt_required()
def analytics_user_activity():
    """Return user activity statistics."""
    try:
        with SessionLocal() as session:
            users = session.query(User).all()
            activity = []
            for user in users:
                projects_count = session.query(ProjectMember).filter(ProjectMember.user_id == user.id).count()
                tasks_count = session.query(Task).filter(Task.assigned_to == user.id).count()
                activity.append({
                    "user_id": user.id,
                    "username": user.username,
                    "created_at": user.created_at.isoformat() + 'Z' if user.created_at else None,
                    "projects_count": projects_count,
                    "tasks_count": tasks_count,
                })
        return jsonify({"data": activity, "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": {"code": "SERVER_ERROR", "message": str(e)}, "status": "error"}), 500

@app.route("/api/analytics/export", methods=["GET"])
@jwt_required()
def analytics_export():
    """Export analytics data as CSV or PDF."""
    export_type = request.args.get("type", "csv")
    try:
        with SessionLocal() as session:
            projects = session.query(Project).all()
            stats = []
            for project in projects:
                stat = {
                    "Project ID": project.id,
                    "Name": project.name,
                    "Created At": project.created_at.isoformat() + 'Z' if project.created_at else "",
                    "Task Count": len(project.tasks) if hasattr(project, "tasks") and project.tasks else 0,
                    "Member Count": len(project.members) if hasattr(project, "members") and project.members else 0,
                }
                stats.append(stat)
            if not stats:
                return jsonify({"error": {"code": "NOT_FOUND", "message": "No analytics data available"}, "status": "error"}), 404
            if export_type == "csv":
                si = StringIO()
                writer = csv.DictWriter(si, fieldnames=list(stats[0].keys()))
                writer.writeheader()
                writer.writerows(stats)
                output = BytesIO()
                output.write(si.getvalue().encode("utf-8"))
                output.seek(0)
                return send_file(output, mimetype="text/csv", as_attachment=True, download_name="project_analytics.csv")
            elif export_type == "pdf":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for stat in stats:
                    for k, v in stat.items():
                        pdf.cell(0, 10, f"{k}: {v}", ln=1)
                    pdf.cell(0, 10, "", ln=1)
                pdf_output = BytesIO(pdf.output(dest='S').encode('latin1'))
                pdf_output.seek(0)
                return send_file(pdf_output, mimetype="application/pdf", as_attachment=True, download_name="project_analytics.pdf")
            else:
                return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Invalid export type"}, "status": "error"}), 400
    except Exception as e:
        return jsonify({"error": {"code": "SERVER_ERROR", "message": str(e)}, "status": "error"}), 500