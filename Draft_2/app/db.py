# db.py: Database connection and schema initialization for authentication/access control

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func

DB_PATH = os.getenv("AUTH_DB_PATH", "auth.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete")
    assigned_tasks = relationship("Task", back_populates="assignee", cascade="all, delete-orphan")
    assigned_subtasks = relationship("Subtask", back_populates="assignee", cascade="all, delete-orphan")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="owned_projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String)

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    due_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")

class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    due_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    task = relationship("Task", back_populates="subtasks")
    assignee = relationship("User", back_populates="assigned_subtasks")

# File management models

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer)
    mimetype = Column(String)
    uploaded_at = Column(DateTime, server_default=func.current_timestamp())
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    access_level = Column(String, nullable=False, default="private")  # 'private', 'project', 'public'
    edit_level = Column(String, nullable=False, default="owner")      # 'owner', 'project', 'any'

    owner = relationship("User", backref="files")
    project_links = relationship("ProjectFile", back_populates="file", cascade="all, delete-orphan")

    def can_user_access(self, user, project_ids=None):
        # Returns True if user can access this file
        if self.access_level == "public":
            return True
        if self.owner_id == user.id:
            return True
        if self.access_level == "project" and project_ids:
            return any(link.project_id in project_ids and link.can_view for link in self.project_links)
        return False

    def can_user_edit(self, user, project_ids=None):
        # Returns True if user can edit this file
        if self.edit_level == "any":
            return True
        if self.owner_id == user.id:
            return True
        if self.edit_level == "project" and project_ids:
            return any(link.project_id in project_ids and link.can_edit for link in self.project_links)
        return False

class ProjectFile(Base):
    __tablename__ = "project_files"
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), primary_key=True)
    can_edit = Column(Integer, nullable=False, default=0)
    can_view = Column(Integer, nullable=False, default=1)

    project = relationship("Project", backref="project_files")
    file = relationship("File", back_populates="project_links")

def init_db():
    """Initialize the database schema from schema.sql if tables do not exist."""
    with engine.connect() as conn:
        # Check if the 'users' table exists
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        )
        if not result.fetchone():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            conn.execute(text(schema_sql))
        # Create SQLAlchemy models if not present
        Base.metadata.create_all(bind=engine)

import bcrypt

def hash_password(plain_password: str) -> str:
    """
    Hash the password securely using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the hashed password.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username: str, plain_password: str, role: str = "user"):
    """
    Register a new user with a hashed password and role.
    """
    from sqlalchemy.exc import IntegrityError
    init_db()
    hashed_pw = hash_password(plain_password)
    with SessionLocal() as session:
        try:
            session.execute(
                text("INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"),
                {"username": username, "password": hashed_pw, "role": role}
            )
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False

def authenticate_user(username: str, plain_password: str) -> bool:
    """
    Authenticate a user by username and password.
    """
    init_db()
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT password FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()
        if result:
            return verify_password(plain_password, result[0])
        return False

def assign_role(username: str, new_role: str) -> bool:
    """
    Assign a new role to an existing user.
    """
    init_db()
    with SessionLocal() as session:
        result = session.execute(
            text("UPDATE users SET role = :role WHERE username = :username"),
            {"role": new_role, "username": username}
        )
        session.commit()
        return result.rowcount > 0