import sqlite3

def table_exists(conn, table_name):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,)
    )
    return cursor.fetchone() is not None

def migrate():
    conn = sqlite3.connect("Draft_2/app/auth.db")
    try:
        if not table_exists(conn, "messages"):
            conn.execute(
                '''
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    recipient_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    read BOOLEAN NOT NULL DEFAULT 0
                );
                '''
            )
            print("Created 'messages' table.")
        else:
            print("'messages' table already exists. No changes made.")
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()