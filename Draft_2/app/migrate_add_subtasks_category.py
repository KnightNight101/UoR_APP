import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), "auth.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if category column exists
    cur.execute("PRAGMA table_info(subtasks)")
    columns = [row[1] for row in cur.fetchall()]
    if "category" not in columns:
        cur.execute("ALTER TABLE subtasks ADD COLUMN category TEXT DEFAULT 'other'")
        print("Added category column to subtasks table.")
    else:
        print("category column already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()