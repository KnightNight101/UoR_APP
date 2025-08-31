import sqlite3
import os

def inspect_db(db_path):
    print(f"Database: {db_path}")
    if not os.path.exists(db_path):
        print("  [ERROR] Database file does not exist.")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    if not tables:
        print("  [No tables found]")
        conn.close()
        return
    for table in tables:
        print(f"  Table: {table}")
        cursor.execute(f"PRAGMA table_info('{table}')")
        columns = cursor.fetchall()
        if not columns:
            print("    [No columns found]")
        else:
            print("    Columns:")
            for col in columns:
                # col: (cid, name, type, notnull, dflt_value, pk)
                print(f"      - {col[1]} ({col[2]})")
    conn.close()
    print()

if __name__ == "__main__":
    inspect_db('Draft_2/app/app.db')
    inspect_db('Draft_2/app/auth.db')