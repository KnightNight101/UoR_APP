import sqlite3

DB_PATH = "Draft_2/app/app.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Check if subtask_id already exists
    cur.execute("PRAGMA table_info(files);")
    columns = [row[1] for row in cur.fetchall()]
    if "subtask_id" in columns:
        print("subtask_id column already exists.")
        return
    # Add the column
    cur.execute("ALTER TABLE files ADD COLUMN subtask_id INTEGER REFERENCES subtasks(id);")
    conn.commit()
    print("subtask_id column added to files table.")
    conn.close()

if __name__ == "__main__":
    migrate()