import sqlite3

def add_deadline_column(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE projects ADD COLUMN deadline TEXT;")
        print("Column 'deadline' added to 'projects' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e) or "already exists" in str(e):
            print("Column 'deadline' already exists.")
        else:
            print("Error:", e)
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    add_deadline_column("Draft_2/app/auth.db")