import sqlite3

def print_files_table_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(files)")
    columns = cursor.fetchall()
    print("files table columns in", db_path)
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    print_files_table_schema("Draft_2/app/auth.db")