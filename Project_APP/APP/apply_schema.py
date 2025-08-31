import sqlite3

def apply_schema(db_path, schema_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        print("Schema applied successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_schema("Draft_2/app/auth.db", "Draft_2/app/schema_clean.sql")