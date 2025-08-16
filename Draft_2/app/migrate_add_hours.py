import sqlite3

def add_hours_column(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE tasks ADD COLUMN hours REAL;")
        print("Column 'hours' added to 'tasks' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e) or "already exists" in str(e):
            print("Column 'hours' already exists.")
        else:
            print("Error:", e)
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    add_hours_column("Draft_2/app/auth.db")