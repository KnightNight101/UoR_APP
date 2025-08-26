import sqlite3
from flask import Flask, request, jsonify
from Draft_2.app.db import (
    create_task as orm_create_task,
    get_task_by_id,
    get_project_by_id,
    get_user_by_id,
    log_structured_event,
    SessionLocal,
)
from Draft_2.app.backend.tiny_llama import TinyLlamaPlanner

app = Flask(__name__)
DB_PATH = "Draft_2/app/auth.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
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
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
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

# --- Calendar Event Endpoints ---

def event_row_to_dict(row):
    if not row:
        return None
    d = dict(row)
    d["start_datetime"] = d.get("start_datetime")
    d["end_datetime"] = d.get("end_datetime")
    d["creator_id"] = d.get("creator_id")
    return d

def invitee_row_to_dict(row):
    if not row:
        return None
    return {
        "user_id": row["user_id"],
        "status": row["status"]
    }

@app.route("/events", methods=["POST"])
def create_event():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    title = data.get("title")
    description = data.get("description")
    start_datetime = data.get("start_datetime")
    end_datetime = data.get("end_datetime")
    creator_id = data.get("creator_id")
    invitees = data.get("invitees", [])  # List of user_ids

    if not (title and start_datetime and end_datetime and creator_id):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO events (title, description, start_datetime, end_datetime, creator_id, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """,
        (title, description, start_datetime, end_datetime, creator_id)
    )
    event_id = cur.lastrowid

    for user_id in invitees:
        cur.execute(
            "INSERT INTO event_invitees (event_id, user_id, status) VALUES (?, ?, ?)",
            (event_id, user_id, "pending")
        )
    conn.commit()
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify(event_row_to_dict(row)), 201

@app.route("/events", methods=["GET"])
def list_events():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    conn = get_db()
    cur = conn.cursor()
    # Events created by user or where user is invited
    cur.execute("""
        SELECT DISTINCT e.*
        FROM events e
        LEFT JOIN event_invitees ei ON e.id = ei.event_id
        WHERE e.creator_id = ? OR ei.user_id = ?
    """, (user_id, user_id))
    rows = cur.fetchall()
    conn.close()
    return jsonify([event_row_to_dict(row) for row in rows])

@app.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Event not found"}), 404
    cur.execute("SELECT user_id, status FROM event_invitees WHERE event_id = ?", (event_id,))
    invitees = [invitee_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    event = event_row_to_dict(row)
    if event is not None:
        event["invitees"] = invitees
    return jsonify(event)

@app.route("/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.json
    fields = []
    values = []
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    for key in ["title", "description", "start_datetime", "end_datetime"]:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    values.append(event_id)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE events SET {', '.join(fields)} WHERE id = ?",
        values
    )
    # Optionally update invitees
    if data and "invitees" in data:
        cur.execute("DELETE FROM event_invitees WHERE event_id = ?", (event_id,))
        for user_id in data["invitees"]:
            cur.execute(
                "INSERT INTO event_invitees (event_id, user_id, status) VALUES (?, ?, ?)",
                (event_id, user_id, "pending")
            )
    conn.commit()
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify(event_row_to_dict(row))

@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM event_invitees WHERE event_id = ?", (event_id,))
    cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/events/<int:event_id>/invitees", methods=["POST"])
def manage_invitees(event_id):
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    add = data.get("add", [])
    remove = data.get("remove", [])
    conn = get_db()
    cur = conn.cursor()
    for user_id in add:
        cur.execute(
            "INSERT OR IGNORE INTO event_invitees (event_id, user_id, status) VALUES (?, ?, ?)",
            (event_id, user_id, "pending")
        )
    for user_id in remove:
        cur.execute(
            "DELETE FROM event_invitees WHERE event_id = ? AND user_id = ?",
            (event_id, user_id)
        )
    conn.commit()
    cur.execute("SELECT user_id, status FROM event_invitees WHERE event_id = ?", (event_id,))
    invitees = [invitee_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"invitees": invitees})

@app.route("/events/<int:event_id>/respond", methods=["POST"])
def respond_invitation(event_id):
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    user_id = data.get("user_id")
    status = data.get("status")  # "accepted" or "declined"
    if not (user_id and status in ("accepted", "declined")):
        return jsonify({"error": "user_id and valid status required"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE event_invitees SET status = ? WHERE event_id = ? AND user_id = ?",
        (status, event_id, user_id)
    )
    conn.commit()
    cur.execute("SELECT user_id, status FROM event_invitees WHERE event_id = ?", (event_id,))
    invitees = [invitee_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"invitees": invitees})

@app.route("/plan/generate", methods=["POST"])
def generate_project_plan():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Missing JSON body"}), 400
    project_id = data.get("project_id")
    user_id = data.get("user_id")
    if not project_id or not user_id:
        return jsonify({"error": "project_id and user_id required"}), 400
    planner = TinyLlamaPlanner(user_id=user_id)
    plan = planner.generate_project_plan(project_id)
    if plan is None:
        return jsonify({"error": "Plan generation failed"}), 500
    return jsonify({"plan": plan})

@app.route("/plan/suggest_time", methods=["POST"])
def suggest_time_for_task():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Missing JSON body"}), 400
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    if not task_id or not user_id:
        return jsonify({"error": "task_id and user_id required"}), 400
    with SessionLocal() as session:
        Task = get_task_by_id.__globals__["Task"]
        Project = get_project_by_id.__globals__["Project"]
        ProjectMember = get_project_by_id.__globals__["ProjectMember"]
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404
        project = session.query(Project).filter_by(id=task.project_id).first()
        if not project:
            return jsonify({"error": "Project not found"}), 404
        team_members = session.query(ProjectMember).filter_by(project_id=project.id).all()
        planner = TinyLlamaPlanner(user_id=user_id)
        suggestion = planner.suggest_time_for_task(task, project, team_members)
    return jsonify({"suggestion": suggestion})

@app.route("/plan/verify", methods=["POST"])
def verify_plan():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Missing JSON body"}), 400
    plan = data.get("plan")
    user_id = data.get("user_id")
    if not plan or not user_id:
        return jsonify({"error": "plan and user_id required"}), 400
    planner = TinyLlamaPlanner(user_id=user_id)
    result = planner.verify_plan_feasibility(plan)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)