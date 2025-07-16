# db.py: Database connection and schema initialization for authentication/access control

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_PATH = os.getenv("AUTH_DB_PATH", "auth.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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