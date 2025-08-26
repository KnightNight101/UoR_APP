import pytest
from Draft_2.app.server import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Ensure required user and project exist in the DB for tests
    import sqlite3
    conn = sqlite3.connect("Draft_2/app/auth.db")
    cur = conn.cursor()
    # Create user with id=1 if not exists
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (1, "testuser"))
    # Create project with id=1 if not exists
    cur.execute("INSERT OR IGNORE INTO projects (id, name) VALUES (?, ?)", (1, "Test Project"))
    conn.commit()
    conn.close()
    with app.test_client() as client:
        yield client

def test_create_and_edit_task_with_dependencies(client):
    # Create a task
    response = client.post("/tasks", json={
        "project_id": 1,
        "title": "Main Task",
        "description": "Test task",
        "deadline": "2025-09-01",
        "assigned_to": 1
    })
    assert response.status_code == 201
    task_id = response.get_json()["id"]

    # Create a subtask with dependency on main task
    response = client.post("/tasks", json={
        "project_id": 1,
        "title": "Subtask",
        "description": "Depends on main",
        "deadline": "2025-09-02",
        "assigned_to": 2
    })
    assert response.status_code == 201
    subtask_id = response.get_json()["id"]

    # Edit subtask
    response = client.put(f"/tasks/{subtask_id}", json={
        "description": "Updated desc",
        "deadline": "2025-09-03"
    })
    assert response.status_code == 200

def test_event_logging_for_actions(client):
    # Create event
    response = client.post("/events", json={
        "title": "User Edit Event",
        "description": "User edited a task",
        "start_datetime": "2025-09-01T10:00:00",
        "end_datetime": "2025-09-01T11:00:00",
        "creator_id": 1
    })
    assert response.status_code == 201
    event_id = response.get_json()["id"]

    # List events
    response = client.get("/events?user_id=1")
    assert response.status_code == 200
    events = response.get_json()
    assert any(e["id"] == event_id for e in events)

def test_llm_suggestion_and_logging(client, monkeypatch):
    # Mock TinyLlamaPlanner
    def fake_suggest_time_for_task(*args, **kwargs):
        return {"suggested_time": "2025-09-04", "reasoning": "Test reasoning"}
    monkeypatch.setattr("Draft_2.app.backend.tiny_llama.TinyLlamaPlanner.suggest_time_for_task", fake_suggest_time_for_task)

    # Call suggest_time endpoint
    response = client.post("/plan/suggest_time", json={
        "task_id": 1,
        "user_id": 1
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "suggestion" in data

def test_generate_project_plan_and_verify(client, monkeypatch):
    # Mock TinyLlamaPlanner
    def fake_generate_project_plan(*args, **kwargs):
        return [{"task_id": 1, "start": "2025-09-01", "end": "2025-09-02"}]
    def fake_verify_plan_feasibility(*args, **kwargs):
        return {"feasible": True, "reasoning": "All deadlines met"}
    monkeypatch.setattr("Draft_2.app.backend.tiny_llama.TinyLlamaPlanner.generate_project_plan", fake_generate_project_plan)
    monkeypatch.setattr("Draft_2.app.backend.tiny_llama.TinyLlamaPlanner.verify_plan_feasibility", fake_verify_plan_feasibility)

    # Generate plan
    response = client.post("/plan/generate", json={"project_id": 1, "user_id": 1})
    assert response.status_code == 200
    plan = response.get_json()["plan"]
    assert isinstance(plan, list)

    # Verify plan
    response = client.post("/plan/verify", json={"plan": plan, "user_id": 1})
    assert response.status_code == 200
    result = response.get_json()
    assert result["feasible"] is True

def test_backend_api_for_qml_ui(client):
    # List tasks
    response = client.get("/tasks")
    assert response.status_code == 200
    # List events
    response = client.get("/events?user_id=1")
    assert response.status_code == 200
    # Get task
    response = client.post("/tasks", json={
        "project_id": 1,
        "title": "QML Task",
        "description": "For QML UI",
        "deadline": "2025-09-05",
        "assigned_to": 1
    })
    task_id = response.get_json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200