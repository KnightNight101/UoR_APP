# db.py: Database connection and schema initialization for authentication/access control

import os
import bcrypt
# Local error logging to avoid circular import
def log_event(event):
    """Append event messages to the event log."""
    import datetime
    LOG_FILE = os.path.join(os.path.dirname(__file__), "event_log.txt")
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {event}\n")

def log_error(error_msg):
    """Append error messages to the event log and print to stderr."""
    import datetime, traceback, sys
    LOG_FILE = os.path.join(os.path.dirname(__file__), "event_log.txt")
    timestamp = datetime.datetime.now().isoformat()
    full_msg = f"[ERROR] [{timestamp}] {error_msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")
    print(full_msg, file=sys.stderr)

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, selectinload
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Boolean, Float

# --- Security Hardening: Data/File Encryption ---
from cryptography.fernet import Fernet

ENCRYPTION_KEY_PATH = os.path.join(os.path.dirname(__file__), 'filekey.key')
def get_encryption_key():
    if not os.path.exists(ENCRYPTION_KEY_PATH):
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_PATH, 'wb') as f:
            f.write(key)
    else:
        with open(ENCRYPTION_KEY_PATH, 'rb') as f:
            key = f.read()
    return key

fernet = Fernet(get_encryption_key())

def encrypt_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(filepath, 'wb') as f:
        f.write(encrypted)

def decrypt_file(filepath):
    with open(filepath, 'rb') as f:
        encrypted = f.read()
    try:
        data = fernet.decrypt(encrypted)
        with open(filepath, 'wb') as f:
            f.write(data)
    except Exception:
        pass  # Already decrypted or not encrypted


DB_PATH = os.getenv("AUTH_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth.db"))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association tables for many-to-many relationships
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# --- Calendar Event Models ---

event_invitees = Table(
    'event_invitees', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('status', String, default='pending')  # 'pending', 'accepted', 'declined'
)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    creator = relationship("User", back_populates="events_created")
    invitees = relationship(
        "User",
        secondary=event_invitees,
        back_populates="events_invited"
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    sso_provider = Column(String, nullable=True)  # SSO provider name
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    tenant = relationship("Tenant", back_populates="users")
    events_created = relationship("Event", back_populates="creator", cascade="all, delete-orphan")
    events_invited = relationship(
        "Event",
        secondary=event_invitees,
        back_populates="invitees"
    )

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    is_blacklisted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    deadline = Column(String, nullable=True)  # New: deadline as string (YYYY-MM-DD)
    tasks_json = Column(Text, nullable=True)       # Renamed from 'tasks' to avoid conflict
    created_at = Column(DateTime, server_default=func.current_timestamp())
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Relationships
    owner = relationship("User", backref="owned_projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    tenant = relationship("Tenant", back_populates="projects")

class ProjectMember(Base):
    __tablename__ = "project_members"
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String, default='member')
    joined_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", backref="project_memberships")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default='pending')
    assigned_to = Column(Integer, ForeignKey('users.id'))
    due_date = Column(DateTime)
    hours = Column(Float)  # Use Float for hours
    dependencies = Column(String)  # Use String for JSON-encoded dependencies
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", backref="assigned_tasks")

class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default='not yet started')
    assigned_to = Column(Integer, ForeignKey('users.id'))
    due_date = Column(DateTime)
    hours = Column(Float)  # Use Float for hours
    dependencies = Column(String)  # Use String for JSON-encoded dependencies
    category = Column(String, default='other')  # Added category column
    created_at = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    task = relationship("Task", backref="subtasks")
    assignee = relationship("User", backref="assigned_subtasks")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    subtask_id = Column(Integer, ForeignKey('subtasks.id'), nullable=True)  # NEW: Link to subtask
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.current_timestamp())
    description = Column(Text)
    # Relationships
    project = relationship("Project", backref="files")
    task = relationship("Task", backref="files")
    subtask = relationship("Subtask", backref="files")  # NEW: Relationship to subtask
    uploader = relationship("User", backref="uploaded_files")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.current_timestamp())
    read = Column(Boolean, default=False)
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    users = relationship("User", back_populates="tenant")
    projects = relationship("Project", back_populates="tenant")

class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    subtask_id = Column(Integer, ForeignKey('subtasks.id'), nullable=True)
    event_type = Column(String, nullable=False)  # e.g., recategorization, llm_suggestion, user_override
    old_category = Column(String, nullable=True)
    new_category = Column(String, nullable=True)
    reasoning = Column(Text, nullable=True)
    context_json = Column(Text, nullable=True)  # JSON-encoded context (prompt, LLM input/output, etc.)

    user = relationship("User")
    project = relationship("Project")
    task = relationship("Task")
    subtask = relationship("Subtask")

class EisenhowerMatrixState(Base):
    __tablename__ = "eisenhower_matrix_states"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    state_json = Column(Text, nullable=False)  # JSON: mapping of task/subtask IDs to categories
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    project = relationship("Project")
    user = relationship("User")

class FileVersion(Base):
    __tablename__ = "file_versions"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    repo_id = Column(Integer, ForeignKey('github_repos.id'), nullable=False)
    commit_hash = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    committed_at = Column(DateTime, server_default=func.current_timestamp())
    author = Column(String)

def column_exists(conn, table, column):
    """Check if a column exists in a SQLite table."""
    result = conn.execute(text(f"PRAGMA table_info({table})"))
    return any(row['name'] == column for row in result.mappings())

# --- EventLog CRUD and helpers ---

def log_structured_event(
    session,
    event_type,
    user_id=None,
    project_id=None,
    task_id=None,
    subtask_id=None,
    old_category=None,
    new_category=None,
    reasoning=None,
    context_json=None
):
    """Log a structured event to the EventLog table."""
    from datetime import datetime
    import json
    event = EventLog(
        timestamp=datetime.utcnow(),
        user_id=user_id,
        project_id=project_id,
        task_id=task_id,
        subtask_id=subtask_id,
        event_type=event_type,
        old_category=old_category,
        new_category=new_category,
        reasoning=reasoning,
        context_json=json.dumps(context_json) if isinstance(context_json, dict) else context_json
    )
    session.add(event)
    session.commit()
    return event

def get_event_logs(project_id=None, user_id=None, limit=100):
    """Fetch event logs, optionally filtered by project or user."""
    with SessionLocal() as session:
        query = session.query(EventLog)
        if project_id:
            query = query.filter(EventLog.project_id == project_id)
        if user_id:
            query = query.filter(EventLog.user_id == user_id)
        return query.order_by(EventLog.timestamp.desc()).limit(limit).all()

# --- EisenhowerMatrixState CRUD ---

def get_eisenhower_matrix_state(project_id, user_id):
    """Get Eisenhower matrix state for a project/user."""
    with SessionLocal() as session:
        return session.query(EisenhowerMatrixState).filter(
            EisenhowerMatrixState.project_id == project_id,
            EisenhowerMatrixState.user_id == user_id
        ).order_by(EisenhowerMatrixState.updated_at.desc()).first()

def set_eisenhower_matrix_state(project_id, user_id, state_json):
    """Set or update Eisenhower matrix state for a project/user."""
    from datetime import datetime
    import json
    with SessionLocal() as session:
        state = session.query(EisenhowerMatrixState).filter(
            EisenhowerMatrixState.project_id == project_id,
            EisenhowerMatrixState.user_id == user_id
        ).first()
        if state:
            setattr(state, "state_json", json.dumps(state_json) if isinstance(state_json, dict) else state_json)
            setattr(state, "updated_at", datetime.utcnow())
        else:
            state = EisenhowerMatrixState(
                project_id=project_id,
                user_id=user_id,
                state_json=json.dumps(state_json) if isinstance(state_json, dict) else state_json,
                updated_at=datetime.utcnow()
            )
            session.add(state)
        session.commit()
        return state

def init_db():
    """Initialize the database schema if tables do not exist."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Load schema from SQL file if it exists
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema SQL statements
            with engine.connect() as conn:
                for statement in schema_sql.split(';'):
                    stmt = statement.strip()
                    if not stmt:
                        continue
                    # Handle ALTER TABLE ... ADD COLUMN idempotently
                    if stmt.upper().startswith("ALTER TABLE"):
                        import re
                        m = re.match(
                            r"ALTER TABLE\s+([^\s]+)\s+ADD COLUMN\s+([^\s]+)\s", stmt, re.IGNORECASE
                        )
                        if m:
                            table, column = m.group(1), m.group(2)
                            if column_exists(conn, table, column):
                                continue  # Skip if column exists
                    try:
                        conn.execute(text(stmt))
                    except Exception as e:
                        # Log and skip duplicate column errors
                        if "duplicate column name" in str(e) or "already exists" in str(e):
                            continue
                        else:
                            raise
                conn.commit()
        
        # Seed roles/permissions and default admin user
        seed_admin_and_roles()

        print("Database initialized successfully")
        return True
    except Exception as e:
        log_error(f"Error initializing database: {e}")
        return False

# Ensure roles/permissions and default admin user are seeded on DB init
def seed_admin_and_roles():
    """Seed default roles/permissions and admin user if missing."""
    init_roles_and_permissions()
    register_user("admin", "admin123", "admin")

# Task CRUD functions
from typing import Optional, List

def create_task(
    project_id: int,
    title: str,
    description: Optional[str] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[datetime] = None,
    hours: Optional[float] = None,
    dependencies: Optional[List[int]] = None
):
    import json
    import traceback
    print(f"[DEBUG] create_task called (project_id={project_id}, title={title})")
    try:
        with SessionLocal() as session:
            print("[DEBUG] create_task: Session started")
            task = Task(
                project_id=project_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                due_date=due_date,
                hours=hours,
                dependencies=json.dumps(dependencies) if dependencies is not None else None
            )
            session.add(task)
            session.commit()
            print(f"[DEBUG] create_task: Task committed (id={task.id})")
            # Log event for task creation
            try:
                project = session.query(Project).filter(Project.id == project_id).first()
                project_name = getattr(project, "name", str(project_id)) if project else str(project_id)
                assigned_user = "Unassigned"
                if assigned_to:
                    user_obj = session.query(User).filter(User.id == assigned_to).first()
                    if user_obj:
                        assigned_user = getattr(user_obj, "username", str(assigned_to))
                log_event(
                    f"Task added: '{title}' | Project: '{project_name}' | Deadline: {due_date} | Hours: {hours} | Assigned to: {assigned_user}"
                )
            except Exception as e:
                log_error(f"Failed to log task creation event: {e}")
            # After creating the task, create the "check progress" subtask
            # The deadline is the same as the task's due_date (since no other subtasks yet)
            if task.id is not None:
                subtask = Subtask(
                    task_id=task.id,
                    title="check progress",
                    assigned_to=assigned_to,
                    due_date=due_date,
                    category="important_urgent",
                    status="not yet started"
                )
                session.add(subtask)
                session.commit()
                print(f"[DEBUG] create_task: Subtask committed (id={subtask.id})")
            # Return a plain dict with the task id as an int to avoid DetachedInstanceError
            return {"id": int(task.id) if hasattr(task, "id") and not isinstance(task.id, Column) else task.id}
    except Exception as e:
        import traceback
        log_error(f"Error creating task: {e}\n{traceback.format_exc()}")
        return None

def get_tasks(project_id: int):
    try:
        with SessionLocal() as session:
            return session.query(Task).filter(Task.project_id == project_id).all()
    except Exception as e:
        log_error(f"Error getting tasks: {e}")
        return []

def get_user_tasks(user_id: int):
    """
    Return all Task objects assigned to the given user across all projects.
    """
    try:
        with SessionLocal() as session:
            return session.query(Task).filter(Task.assigned_to == user_id).all()
    except Exception as e:
        log_error(f"Error getting user tasks: {e}")
        return []

def get_user_subtasks(user_id: int):
    """
    Return all Subtask objects assigned to the given user across all projects.
    """
    try:
        with SessionLocal() as session:
            return session.query(Subtask).filter(Subtask.assigned_to == user_id).all()
    except Exception as e:
        log_error(f"Error getting user subtasks: {e}")
        return []

def update_subtask_status(subtask_id: int, status: str):
    """
    Update the status of a subtask (Not Yet Started, In Progress, Completed).
    """
    try:
        with SessionLocal() as session:
            subtask = session.query(Subtask).filter(Subtask.id == subtask_id).first()
            if subtask:
                subtask.status = status
                session.commit()
                return True
    except Exception as e:
        log_error(f"Error updating subtask status: {e}")
    return False

def get_task_by_id(task_id: int):
    try:
        with SessionLocal() as session:
            return session.query(Task).filter(Task.id == task_id).first()
    except Exception as e:
        log_error(f"Error getting task: {e}")
        return None

def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[datetime] = None,
    hours: Optional[float] = None,
    dependencies: Optional[List[int]] = None
):
    import json
    try:
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            if title is not None:
                task.title = title  # type: ignore
            if description is not None:
                task.description = description  # type: ignore
            if status is not None:
                task.status = status  # type: ignore
            if assigned_to is not None:
                task.assigned_to = assigned_to  # type: ignore
            if due_date is not None:
                task.due_date = due_date  # type: ignore
            if hours is not None:
                task.hours = hours  # type: ignore
            if dependencies is not None:
                task.dependencies = json.dumps(dependencies)  # type: ignore
            session.commit()
            return task
    except Exception as e:
        log_error(f"Error updating task: {e}")
        return None

def delete_task(task_id: int):
    try:
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            session.delete(task)
            session.commit()
            return True
    except Exception as e:
        log_error(f"Error deleting task: {e}")
        return False

# Subtask CRUD functions

def create_subtask(
    task_id: int,
    title: str,
    description: Optional[str] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[datetime] = None,
    hours: Optional[float] = None,
    dependencies: Optional[List[int]] = None
):
    import json
    try:
        with SessionLocal() as session:
            subtask = Subtask(
                task_id=task_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                due_date=due_date,
                hours=hours,
                dependencies=json.dumps(dependencies) if dependencies is not None else None,
                category="important_urgent" if title == "check progress" else "other",
                status="not yet started"
            )
            session.add(subtask)
            session.commit()
            # After adding a subtask, update "check progress" subtask deadline if it exists
            # Find all subtasks for this task except "check progress"
            other_subtasks = session.query(Subtask).filter(
                Subtask.task_id == task_id,
                Subtask.title != "check progress"
            ).all()
            # Find the "check progress" subtask
            check_progress_subtask = session.query(Subtask).filter(
                Subtask.task_id == task_id,
                Subtask.title == "check progress"
            ).first()
            if check_progress_subtask:
                # Find the earliest deadline among other subtasks (if any)
                earliest = None
                for s in other_subtasks:
                    if s.due_date is not None and not isinstance(s.due_date, Column):
                        if earliest is None or (earliest is not None and s.due_date < earliest):
                            earliest = s.due_date
                if earliest is not None:
                    check_progress_subtask.due_date = earliest
                    session.commit()
            return subtask
    except Exception as e:
        log_error(f"Error creating subtask: {e}")
        return None

def get_subtasks(task_id: int):
    try:
        with SessionLocal() as session:
            return session.query(Subtask).filter(Subtask.task_id == task_id).all()
    except Exception as e:
        log_error(f"Error getting subtasks: {e}")
def get_subtask_by_id(subtask_id: int):
    """Return a Subtask object by its ID."""
    try:
        with SessionLocal() as session:
            return session.query(Subtask).filter(Subtask.id == subtask_id).first()
    except Exception as e:
        log_error(f"Error getting subtask by id: {e}")
        return None

        return []

def update_subtask(
    subtask_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[datetime] = None,
    hours: Optional[float] = None,
    dependencies: Optional[List[int]] = None
):
    import json
    try:
        with SessionLocal() as session:
            subtask = session.query(Subtask).filter(Subtask.id == subtask_id).first()
            if not subtask:
                return None
            if title is not None:
                subtask.title = title  # type: ignore
            if description is not None:
                subtask.description = description  # type: ignore
            if status is not None:
                subtask.status = status  # type: ignore
            if assigned_to is not None:
                subtask.assigned_to = assigned_to  # type: ignore
            if due_date is not None:
                subtask.due_date = due_date  # type: ignore
            if hours is not None:
                subtask.hours = hours  # type: ignore
            if dependencies is not None:
                subtask.dependencies = json.dumps(dependencies)  # type: ignore
            session.commit()
            return subtask
    except Exception as e:
        log_error(f"Error updating subtask: {e}")
        return None

def delete_subtask(subtask_id: int):
    try:
        with SessionLocal() as session:
            subtask = session.query(Subtask).filter(Subtask.id == subtask_id).first()
            if not subtask:
                return False
            session.delete(subtask)
            session.commit()
            return True
    except Exception as e:
        log_error(f"Error deleting subtask: {e}")
        return False

def update_subtask_category(subtask_id: int, category: str):
    """Update the category of a subtask."""
    try:
        with SessionLocal() as session:
            subtask = session.query(Subtask).filter(Subtask.id == subtask_id).first()
            if not subtask:
                return None
            subtask.category = category  # type: ignore
            session.commit()
            return subtask
    except Exception as e:
        log_error(f"Error updating subtask category: {e}")
        return None

# Message CRUD functions
def create_message(sender_id: int, recipient_id: int, content: str):
    try:
        with SessionLocal() as session:
            msg = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content
            )
            session.add(msg)
            session.commit()
            return msg
    except Exception as e:
        log_error(f"Error creating message: {e}")
        return None

def get_user_messages(user_id: int):
    try:
        with SessionLocal() as session:
            messages = session.query(Message).filter(
                Message.recipient_id == user_id
            ).order_by(Message.timestamp.desc()).all()
            return messages
    except Exception as e:
        log_error(f"Error getting user messages: {e}")
        return []

def mark_message_read(message_id: int):
    try:
        with SessionLocal() as session:
            msg = session.query(Message).filter(Message.id == message_id).first()
            if not msg:
                return False
            setattr(msg, "read", True)
            session.commit()
            return True
    except Exception as e:
        log_error(f"Error marking message as read: {e}")
        return False

def delete_message(message_id: int):
    try:
        with SessionLocal() as session:
            msg = session.query(Message).filter(Message.id == message_id).first()
            if not msg:
                return False
            session.delete(msg)
            session.commit()
            return True
    except Exception as e:
        log_error(f"Error deleting message: {e}")
        return False

# File CRUD functions

def log_file_version(file_id: int, repo_id: int, commit_hash: str, version: int, committed_at, author: str):
    """
    Log a new file version in the file_versions table.
    """
    try:
        with SessionLocal() as session:
            fv = FileVersion(
                file_id=file_id,
                repo_id=repo_id,
                commit_hash=commit_hash,
                version=version,
                committed_at=committed_at,
                author=author
            )
            session.add(fv)
            session.commit()
            return fv
    except Exception as e:
        log_error(f"Error logging file version: {e}")
        return None
def create_file(project_id: int, filename: str, filepath: str, uploaded_by: int, description: Optional[str] = None, task_id: Optional[int] = None, subtask_id: Optional[int] = None):
    try:
        with SessionLocal() as session:
            file = File(
                project_id=project_id,
                filename=filename,
                filepath=filepath,
                uploaded_by=uploaded_by,
                description=description,
                task_id=task_id,
                subtask_id=subtask_id
            )
            session.add(file)
            session.commit()
            return file
    except Exception as e:
        log_error(f"Error creating file: {e}")
        return None

def get_files(project_id: int, task_id: Optional[int] = None, subtask_id: Optional[int] = None):
    try:
        with SessionLocal() as session:
            query = session.query(File).filter(File.project_id == project_id)
            if task_id:
                query = query.filter(File.task_id == task_id)
            if subtask_id:
                query = query.filter(File.subtask_id == subtask_id)
            return query.all()
    except Exception as e:
        log_error(f"Error getting files: {e}")
        return []

def get_file_by_id(file_id: int):
    try:
        with SessionLocal() as session:
            return session.query(File).filter(File.id == file_id).first()
    except Exception as e:
        log_error(f"Error getting file: {e}")
        return None

def update_file(file_id: int, filename: Optional[str] = None, description: Optional[str] = None):
    try:
        with SessionLocal() as session:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return None
            if filename:
                file.filename = filename  # type: ignore
            if description is not None:
                file.description = description  # type: ignore
            session.commit()
            return file
    except Exception as e:
        log_error(f"Error updating file: {e}")
        return None

def delete_file(file_id: int):
    try:
        with SessionLocal() as session:
            file = session.query(File).filter(File.id == file_id).first()
            if not file:
                return False
            session.delete(file)
            session.commit()
            return True
    except Exception as e:
        log_error(f"Error deleting file: {e}")
        return False

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username: str, password: str, role: str = "user") -> bool:
    """Register a new user with hashed password and assign role."""
    try:
        with SessionLocal() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                log_error(f"User {username} already exists")
                return False
            
            # Create new user
            password_hash = hash_password(password)
            new_user = User(
                username=username,
                password_hash=password_hash
            )
            
            session.add(new_user)
            session.flush()  # Get user ID
            
            # Assign role to user
            role_obj = session.query(Role).filter(Role.name == role).first()
            if not role_obj:
                # Create role if missing
                role_obj = Role(name=role, description=f"Auto-created role: {role}")
                session.add(role_obj)
                session.flush()
            new_user.roles.append(role_obj)
            
            session.commit()
            # Optionally log user creation as event, not error
            return True
            
    except Exception as e:
        log_error(f"Error registering user: {e}")
        return False

def authenticate_user(username: str, password: str):
    """Authenticate a user with username and password. Returns user object if valid."""
    try:
        with SessionLocal() as session:
            user = session.query(User).filter(
                User.username == username,
                User.is_active == True
            ).first()
            with open("login_debug.log", "a", encoding="utf-8") as dbg:
                dbg.write(f"[DEBUG] authenticate_user: username={username!r}, user_found={user is not None}\n")
                if user:
                    dbg.write(f"[DEBUG] authenticate_user: user.id={user.id}, user.username={user.username}, user.password_hash={user.password_hash!r}\n")
            if user and isinstance(user.password_hash, str):
                password_check = verify_password(password, user.password_hash)
                with open("login_debug.log", "a", encoding="utf-8") as dbg:
                    dbg.write(f"[DEBUG] authenticate_user: verify_password result={password_check}\n")
                if password_check:
                    # Load roles for the user
                    user_with_roles = session.query(User).options(
                        selectinload(User.roles)
                    ).filter(User.id == user.id).first()
                    with open("login_debug.log", "a", encoding="utf-8") as dbg:
                        dbg.write(f"[DEBUG] authenticate_user: returning user_with_roles={user_with_roles is not None}\n")
                    return user_with_roles
            return None
    except Exception as e:
        with open("login_debug.log", "a", encoding="utf-8") as dbg:
            dbg.write("[DEBUG] Exception in authenticate_user, about to call log_error\n")
        log_error(f"Error authenticating user: {e}")
        with open("login_debug.log", "a", encoding="utf-8") as dbg:
            dbg.write("[DEBUG] Finished calling log_error in authenticate_user\n")
        return None

def get_user_by_username(username: str):
    """Get user by username with roles loaded."""
    try:
        with SessionLocal() as session:
            return session.query(User).options(
                selectinload(User.roles)
            ).filter(User.username == username).first()
    except Exception as e:
        log_error(f"Error getting user: {e}")
        return None

def get_user_by_id(user_id: int):
    """Get user by ID with roles loaded."""
    try:
        with SessionLocal() as session:
            return session.query(User).options(
                selectinload(User.roles)
            ).filter(User.id == user_id).first()
    except Exception as e:
        log_error(f"Error getting user by ID: {e}")
        return None
def get_all_users():
    """Return all User objects."""
    try:
        with SessionLocal() as session:
            return session.query(User).all()
    except Exception as e:
        log_error(f"Error getting all users: {e}")
        return []

def store_refresh_token(user_id: int, token: str, expires_at: datetime) -> bool:
    """Store a refresh token for a user."""
    try:
        with SessionLocal() as session:
            refresh_token = RefreshToken(
                token=token,
                user_id=user_id,
                expires_at=expires_at
            )
            session.add(refresh_token)
            session.commit()
            return True
    except Exception as e:
        log_error(f"Error storing refresh token: {e}")
        return False

def validate_refresh_token(token: str):
    """Validate a refresh token and return the associated user."""
    try:
        with SessionLocal() as session:
            refresh_token = session.query(RefreshToken).filter(
                RefreshToken.token == token,
                RefreshToken.is_blacklisted == False,
                RefreshToken.expires_at > datetime.utcnow()
            ).first()
            
            if refresh_token:
                if isinstance(refresh_token.user_id, int):
                    return get_user_by_id(refresh_token.user_id)
                return None
            return None
    except Exception as e:
        log_error(f"Error validating refresh token: {e}")
        return None

def blacklist_refresh_token(token: str) -> bool:
    """Blacklist a refresh token (logout)."""
    try:
        with SessionLocal() as session:
            refresh_token = session.query(RefreshToken).filter(
                RefreshToken.token == token
            ).first()
            
            if refresh_token:
                # Update the blacklist status
                session.query(RefreshToken).filter(RefreshToken.token == token).update({
                    RefreshToken.is_blacklisted: True
                })
                session.commit()
                return True
            return False
    except Exception as e:
        log_error(f"Error blacklisting refresh token: {e}")
        return False

def cleanup_expired_tokens():
    """Remove expired refresh tokens."""
    try:
        with SessionLocal() as session:
            expired_tokens = session.query(RefreshToken).filter(
                RefreshToken.expires_at < datetime.utcnow()
            )
            count = expired_tokens.count()
            expired_tokens.delete()
            session.commit()
            print(f"Cleaned up {count} expired tokens")
            return True
    except Exception as e:
        log_error(f"Error cleaning up expired tokens: {e}")
        return False

# Project Management Functions

from typing import Optional

def create_project(
    name: Optional[str],
    description: Optional[str] = None,
    owner_id: Optional[int] = None,
    members: Optional[list] = None,
    deadline: Optional[str] = None,
    tasks: Optional[list] = None
):
    """Create a new project with optional initial members, deadline, and tasks. Logs event to EventLog."""
    import json
    import traceback
    print(f"[DEBUG] create_project called (name={name}, owner_id={owner_id})")
    if members is None:
        members = []
    if tasks is None:
        tasks = []
    try:
        with SessionLocal() as session:
            print("[DEBUG] create_project: Session started")
            # Create the project
            project = Project(
                name=name,
                description=description,
                owner_id=owner_id,
                deadline=deadline,
                tasks_json=json.dumps(tasks) if tasks is not None else json.dumps([])
            )
            session.add(project)
            session.flush()  # Get project ID

            # Add owner as a member with 'owner' role
            # Always add owner as a member, even if owner_id is 0
            if owner_id is not None:
                owner_membership = ProjectMember(
                    project_id=project.id if not isinstance(project.id, Column) else project.id.default,
                    user_id=owner_id,
                    role='owner'
                )
                session.add(owner_membership)
                # Log event for owner assignment
                log_structured_event(
                    session,
                    event_type="project_owner_assigned",
                    user_id=owner_id,
                    project_id=project.id,
                    reasoning="Owner assigned to new project"
                )

            # Add initial members if provided
            if members:
                for member_data in members:
                    user_id = member_data.get('user_id')
                    role = member_data.get('role', 'member')
                    if user_id and user_id != owner_id:  # Don't duplicate owner
                        member = ProjectMember(
                            project_id=project.id,
                            user_id=user_id,
                            role=role
                        )
                        session.add(member)
                        # Log event for member assignment
                        log_structured_event(
                            session,
                            event_type="project_member_assigned",
                            user_id=user_id,
                            project_id=project.id,
                            reasoning=f"User assigned as {role} to project"
                        )

            # --- Create real Task rows for each task in tasks ---
            from datetime import datetime as dt
            for task in tasks:
                title = task.get("title")
                deadline_val = task.get("deadline")
                assigned = task.get("assigned")
                dependencies = task.get("dependencies", [])
                hours = task.get("hours", 0)
                # Parse deadline string to datetime.date if possible
                due_date = None
                if deadline_val:
                    try:
                        due_date = dt.strptime(deadline_val, "%Y-%m-%d")
                    except Exception:
                        due_date = None
                # Use create_task to ensure subtasks etc. are created
                session.flush()  # Ensure project.id is assigned an integer value
                real_project_id = getattr(project, "id", None)
                if isinstance(real_project_id, int):
                    print(f"[DEBUG] create_project: Calling create_task inside session (project_id={real_project_id}, title={title})")
                    create_task(
                        project_id=real_project_id,
                        title=title,
                        assigned_to=assigned,
                        due_date=due_date,
                        hours=hours,
                        dependencies=dependencies
                    )
                else:
                    raise ValueError("Project ID was not assigned correctly.")

            # Log event for project creation
            log_structured_event(
                session,
                event_type="project_created",
                user_id=owner_id,
                project_id=project.id,
                reasoning="Project created"
            )

            session.commit()
            print("[DEBUG] create_project: Session committed")

            # Return project with relationships loaded
            return session.query(Project).options(
                selectinload(Project.owner),
                selectinload(Project.members)
            ).filter(Project.id == project.id).first()

    except Exception as e:
        import traceback
        log_error(f"Error creating project: {e}\n{traceback.format_exc()}")
        return None

def get_user_projects(user_id: int, page: int = 1, limit: int = 20, search: Optional[str] = None):
    """Get projects accessible to a user (owned or member of)."""
    try:
        with SessionLocal() as session:
            # Base query for projects the user can access
            query = session.query(Project).join(
                ProjectMember, Project.id == ProjectMember.project_id
            ).filter(ProjectMember.user_id == user_id)
            
            # Add search filter if provided
            if search:
                query = query.filter(Project.name.ilike(f'%{search}%'))
            
            # Add pagination
            offset = (page - 1) * limit
            projects = query.options(
                selectinload(Project.owner),
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.tasks).selectinload(Task.subtasks)
            ).offset(offset).limit(limit).all()
            
            # Get total count for pagination
            total = query.count()
            
            return projects, total
            
    except Exception as e:
        log_error(f"Error getting user projects: {e}")
        return [], 0

def get_project_by_id(project_id: int, user_id: Optional[int] = None):
    """Get project by ID with permission checking."""
    try:
        with SessionLocal() as session:
            project = session.query(Project).options(
                selectinload(Project.owner),
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.tasks)
            ).filter(Project.id == project_id).first()
            
            if not project:
                return None
            
            # Check if user has access (if user_id provided)
            if user_id:
                has_access = session.query(ProjectMember).filter(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                ).first() is not None
                
                if not has_access:
                    return None
            
            return project
            
    except Exception as e:
        log_error(f"Error getting project: {e}")
        return None

def update_project(project_id: int, user_id: int, name: Optional[str] = None, description: Optional[str] = None):
    """Update project details (owner or admin only)."""
    try:
        with SessionLocal() as session:
            # Check if user has permission to update
            membership = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.role.in_(['owner', 'admin'])
            ).first()
            
            if not membership:
                return None, "Permission denied"
            
            # Get and update project
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None, "Project not found"
            
            if name:
                project.name = name  # type: ignore
            if description is not None:
                project.description = description  # type: ignore
            
            session.commit()
            
            # Return updated project with relationships
            return session.query(Project).options(
                selectinload(Project.owner),
                selectinload(Project.members).selectinload(ProjectMember.user)
            ).filter(Project.id == project_id).first(), None
            
    except Exception as e:
        log_error(f"Error updating project: {e}")
        return None, str(e)

def delete_project(project_id: int, user_id: int):
    """Delete project (owner only)."""
    try:
        with SessionLocal() as session:
            # Check if user is the owner
            project = session.query(Project).filter(
                Project.id == project_id,
                Project.owner_id == user_id
            ).first()
            
            if not project:
                return False, "Project not found or permission denied"
            
            session.delete(project)
            session.commit()
            return True, None
            
    except Exception as e:
        log_error(f"Error deleting project: {e}")
        return False, str(e)

def get_project_members(project_id: int, user_id: Optional[int] = None):
    """Get project members."""
    try:
        with SessionLocal() as session:
            # Check access if user_id provided
            if user_id:
                has_access = session.query(ProjectMember).filter(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                ).first() is not None
                
                if not has_access:
                    return []
            
            members = session.query(ProjectMember).options(
                selectinload(ProjectMember.user)
            ).filter(ProjectMember.project_id == project_id).all()
            
            return members
            
    except Exception as e:
        log_error(f"Error getting project members: {e}")
        return []

def add_project_member(project_id: int, user_id: int, new_member_id: int, role: str = 'member'):
    """Add member to project (owner or admin only). Logs event to EventLog."""
    try:
        with SessionLocal() as session:
            # Check if user has permission to add members
            membership = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.role.in_(['owner', 'admin'])
            ).first()
            
            if not membership:
                return None, "Permission denied"
            
            # Check if new member already exists
            existing = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == new_member_id
            ).first()
            
            if existing:
                return None, "User is already a member"
            
            # Check if new member user exists
            new_user = session.query(User).filter(User.id == new_member_id).first()
            if not new_user:
                return None, "User not found"
            
            # Add new member
            new_member = ProjectMember(
                project_id=project_id,
                user_id=new_member_id,
                role=role
            )
            session.add(new_member)
            # Log event for member assignment
            log_structured_event(
                session,
                event_type="project_member_assigned",
                user_id=new_member_id,
                project_id=project_id,
                reasoning=f"User assigned as {role} to project"
            )
            session.commit()
            
            # Return new member with user info
            return session.query(ProjectMember).options(
                selectinload(ProjectMember.user)
            ).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == new_member_id
            ).first(), None
            
    except Exception as e:
        log_error(f"Error adding project member: {e}")
        return None, str(e)

def remove_project_member(project_id: int, user_id: int, member_id: int):
    """Remove member from project (owner or admin only, cannot remove owner).
    Implements fallback logic for key roles (e.g., leader/admin): if a key role is vacated, it is reassigned to the next most senior member.
    """
    try:
        with SessionLocal() as session:
            # Check if user has permission to remove members
            user_membership = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.role.in_(['owner', 'admin'])
            ).first()
            
            if not user_membership:
                return False, "Permission denied"
            
            # Get member to remove
            member_to_remove = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == member_id
            ).first()
            
            if not member_to_remove:
                return False, "Member not found"
            
            # Cannot remove project owner
            if getattr(member_to_remove, "role", None) == 'owner':
                return False, "Cannot remove project owner"
            
            key_roles = ['leader', 'admin']
            removed_role = member_to_remove.role if member_to_remove.role in key_roles else None

            session.delete(member_to_remove)
            session.commit()

            # Fallback logic: if a key role is vacated, assign it to the next most senior member
            if removed_role is not None:
                # Find all remaining members except owner, ordered by joined_at
                remaining_members = session.query(ProjectMember).filter(
                    ProjectMember.project_id == project_id,
                    ProjectMember.role != 'owner'
                ).order_by(ProjectMember.joined_at.asc()).all()
                if remaining_members:
                    # Prefer next admin if available, else next by seniority
                    next_admin = None
                    for m in remaining_members:
                        if getattr(m, "role", None) == 'admin':
                            next_admin = m
                            break
                    fallback_member = next_admin if next_admin else remaining_members[0]
                    fallback_member.role = removed_role
                    session.commit()
            return True, None
            
    except Exception as e:
        log_error(f"Error removing project member: {e}")
        return False, str(e)

def get_project_statistics(project_id: int, user_id: Optional[int] = None):
    """Get project statistics."""
    try:
        with SessionLocal() as session:
            # Check access if user_id provided
            if user_id is not None:
                has_access = session.query(ProjectMember).filter(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                ).first() is not None

                if not has_access:
                    return {}

            # Count tasks by status
            task_stats = session.query(
                Task.status,
                func.count(Task.id).label('count')
            ).filter(Task.project_id == project_id).group_by(Task.status).all()

            # Count members
            member_count = session.query(func.count(ProjectMember.user_id)).filter(
                ProjectMember.project_id == project_id
            ).scalar() or 0

            # Build statistics
            stats = {
                'total_tasks': sum(getattr(stat, 'count', 0) for stat in task_stats),
                'member_count': member_count,
                'task_status_breakdown': {stat.status: stat.count for stat in task_stats}
            }

            # Handle edge case for project_id == 0 (invalid)
            if project_id == 0:
                return {}

            return stats

    except Exception as e:
        log_error(f"Error getting project statistics: {e}")
        return {}

def update_project_leader(project_id: int, new_leader_id: int):
    """
    Assign/change the leader for a project.
    Sets all other members' roles to 'member' except the owner.
    """
    try:
        with SessionLocal() as session:
            # Get all members except owner
            members = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.role != 'owner'
            ).all()
            # Set all to 'member'
            for m in members:
                setattr(m, "role", 'member')
            # Set new leader
            new_leader = session.query(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == new_leader_id
            ).first()
            if new_leader:
                setattr(new_leader, "role", 'leader')
                session.commit()
                log_event(f"Changed leader to user {new_leader_id} for project {project_id}")
                return True
            else:
                return False
    except Exception as e:
        log_error(f"Error updating project leader: {e}")
        return False

def init_roles_and_permissions():
    """Initialize default roles and permissions."""
    try:
        with SessionLocal() as session:
            # Create default roles if they don't exist
            admin_role = session.query(Role).filter(Role.name == "admin").first()
            if not admin_role:
                admin_role = Role(name="admin", description="System administrator with full access")
                session.add(admin_role)
            
            user_role = session.query(Role).filter(Role.name == "user").first()
            if not user_role:
                user_role = Role(name="user", description="Standard user role")
                session.add(user_role)
            
            # Create default permissions
            permissions_data = [
                ("users.create", "Create new users"),
                ("users.read", "View user information"),
                ("users.update", "Update user information"),
                ("users.delete", "Delete users"),
                ("projects.create", "Create new projects"),
                ("projects.read", "View project information"),
                ("projects.update", "Update project information"),
                ("projects.delete", "Delete projects"),
                ("tasks.create", "Create new tasks"),
                ("tasks.read", "View task information"),
                ("tasks.update", "Update task information"),
                ("tasks.delete", "Delete tasks"),
                ("files.create", "Upload files"),
                ("files.read", "Access files"),
                ("files.update", "Modify files"),
                ("files.delete", "Delete files"),
            ]
            
            created_permissions = []
            for perm_name, perm_desc in permissions_data:
                existing_perm = session.query(Permission).filter(Permission.name == perm_name).first()
                if not existing_perm:
                    permission = Permission(name=perm_name, description=perm_desc)
                    session.add(permission)
                    created_permissions.append(permission)
                else:
                    created_permissions.append(existing_perm)
            
            session.flush()
            
            # Assign all permissions to admin role
            for permission in created_permissions:
                if permission not in admin_role.permissions:
                    admin_role.permissions.append(permission)
            
            # Assign basic permissions to user role
            user_permissions = ["projects.create", "projects.read", "tasks.create", "tasks.read", "tasks.update", "files.create", "files.read"]
            for perm_name in user_permissions:
                permission = session.query(Permission).filter(Permission.name == perm_name).first()
                if permission and permission not in user_role.permissions:
                    user_role.permissions.append(permission)
            
            session.commit()
            print("Default roles and permissions initialized")
            return True
    except Exception as e:
        log_error(f"Error initializing roles and permissions: {e}")
        return False

# Initialize database on module import
if __name__ == "__main__":
    print("Initializing database...")
    init_db()
if __name__ == "__main__":
    # Create a user for each role in the database with password "password"
    with SessionLocal() as session:
        roles = session.query(Role).all()
        for role in roles:
            username = role.name
            # Avoid duplicate users
            existing_user = session.query(User).filter(User.username == username).first()
            if not existing_user:
                register_user(str(username), "password", str(role.name))
        print("Created users for roles:", [role.name for role in roles])
    print("Database initialization completed!")