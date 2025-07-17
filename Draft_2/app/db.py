# db.py: Database connection and schema initialization for authentication/access control

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func

DB_PATH = os.getenv("AUTH_DB_PATH", "auth.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    # Relationships omitted for brevity

# ... [other model definitions unchanged] ...

def init_db():
    """Initialize the database schema if tables do not exist."""
    Base.metadata.create_all(bind=engine)

# ... [rest of file unchanged] ...