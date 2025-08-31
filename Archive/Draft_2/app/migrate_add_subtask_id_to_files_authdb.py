import sqlite3

def add_subtask_id_column(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check if column exists
    cursor.execute("PRAGMA table_info(files)")
    columns = [row[1] for row in cursor.fetchall()]
    if "subtask_id" not in columns:
        cursor.execute("ALTER TABLE files ADD COLUMN subtask_id INTEGER REFERENCES subtasks(id)")
        print("Added subtask_id column to files table.")
    else:
        print("subtask_id column already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_subtask_id_column("Draft_2/app/auth.db")