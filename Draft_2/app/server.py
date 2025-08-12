import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "Draft_2/app/auth.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    project_id = data.get("project_id")
    title = data.get("title")
    description = data.get("description")
    status = data.get("status", "pending")
    assigned_to = data.get("assigned_to")
    deadline = data.get("deadline")  # ISO 8601 string expected

    if not project_id or not title:
        return jsonify({"error": "project_id and title are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tasks (project_id, title, description, status, assigned_to, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, title, description, status, assigned_to, deadline)
    )
    task_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify(task_row_to_dict(row)), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    fields = []
    values = []
    for key in ["title", "description", "status", "assigned_to", "deadline"]:
        if key in data:
            db_key = "due_date" if key == "deadline" else key
            fields.append(f"{db_key} = ?")
            values.append(data[key])
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    values.append(task_id)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
        values
    )
    conn.commit()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(task_row_to_dict(row))
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(task_row_to_dict(row))
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route("/tasks", methods=["GET"])
def list_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return jsonify([task_row_to_dict(row) for row in rows])

def task_row_to_dict(row):
    if not row:
        return None
    d = dict(row)
    # Map due_date to deadline in API
    d["deadline"] = d.pop("due_date", None)
    return d

if __name__ == "__main__":
    app.run(debug=True)