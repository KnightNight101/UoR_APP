"""Migration script to add events and event_invitees tables for calendar event persistence."""

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Table, MetaData
import os

DB_PATH = os.getenv("AUTH_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth.db"))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
metadata = MetaData()

def upgrade():
    # Create events table
    events = Table(
        "events", metadata,
        Column("id", Integer, primary_key=True),
        Column("title", String, nullable=False),
        Column("description", Text),
        Column("start_datetime", DateTime, nullable=False),
        Column("end_datetime", DateTime, nullable=False),
        Column("creator_id", Integer, ForeignKey("users.id"), nullable=False),
        Column("created_at", DateTime),
    )
    # Create event_invitees table
    event_invitees = Table(
        "event_invitees", metadata,
        Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
        Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
        Column("status", String, default="pending"),
    )
    metadata.create_all(engine, tables=[events, event_invitees])
    print("Migration complete: events and event_invitees tables created.")

if __name__ == "__main__":
    upgrade()