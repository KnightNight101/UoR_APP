import sqlite3

def add_dependencies_column(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE tasks ADD COLUMN dependencies TEXT;")
        print("Column 'dependencies' added to 'tasks' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e) or "already exists" in str(e):
            print("Column 'dependencies' already exists.")
        else:
            print("Error:", e)
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    add_dependencies_column("Draft_2/app/auth.db")