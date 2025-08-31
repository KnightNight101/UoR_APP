import sqlite3

def migrate():
    import os
    db_path = os.path.join(os.path.dirname(__file__), "auth.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if tasks_json column exists
    cur.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cur.fetchall()]
    if "tasks_json" not in columns:
        cur.execute("ALTER TABLE projects ADD COLUMN tasks_json TEXT")
        print("Added tasks_json column to projects table.")
    else:
        print("tasks_json column already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()