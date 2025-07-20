# db.py: Database connection and schema initialization for authentication/access control

import os
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func

DB_PATH = os.getenv("AUTH_DB_PATH", "app/auth.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default='pending')
    assigned_to = Column(Integer, ForeignKey('users.id'))
    due_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())

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
                    if statement.strip():
                        conn.execute(text(statement.strip()))
                conn.commit()
        
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username: str, password: str, role: str = "user") -> bool:
    """Register a new user with hashed password."""
    try:
        with SessionLocal() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"User {username} already exists")
                return False
            
            # Create new user
            password_hash = hash_password(password)
            new_user = User(
                username=username,
                password_hash=password_hash
            )
            
            session.add(new_user)
            session.commit()
            print(f"User {username} created successfully")
            return True
            
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with username and password."""
    try:
        with SessionLocal() as session:
            user = session.query(User).filter(User.username == username).first()
            if user and verify_password(password, user.password_hash):
                return True
            return False
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return False

def get_user_by_username(username: str):
    """Get user by username."""
    try:
        with SessionLocal() as session:
            return session.query(User).filter(User.username == username).first()
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

# Initialize database on module import
if __name__ == "__main__":
    init_db()
    # Create a test admin user
    register_user("admin", "admin123", "admin")
    print("Test admin user created: admin/admin123")