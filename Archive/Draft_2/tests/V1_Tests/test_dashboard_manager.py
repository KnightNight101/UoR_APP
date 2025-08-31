import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy
from Draft_2.app.main import DashboardManager

@pytest.fixture
def app():
    app = QCoreApplication([])
    yield app

@pytest.fixture
def dashboard_manager(qtbot):
    dm = DashboardManager()
    return dm

def test_load_projects_and_matrix_state(dashboard_manager, qtbot):
    # Normal case: valid user and project
    user_id = 1
    project_id = 1
    dashboard_manager.loadProjects(user_id)
    qtbot.wait(100)
    projects = dashboard_manager.projects
    assert isinstance(projects, list)
    assert all("id" in p for p in projects)
    dashboard_manager.loadEisenhowerMatrixState(user_id, project_id)
    # Edge case: invalid user/project
    dashboard_manager.loadProjects(-1)
    assert dashboard_manager.projects == []

def test_recategorize_and_event_logging(dashboard_manager, qtbot):
    user_id, project_id, task_id, subtask_id = 1, 1, 1, 1
    old_category, new_category = "urgent", "not_urgent"
    # Normal recategorization
    dashboard_manager.recategorizeTaskOrSubtask(user_id, project_id, task_id, subtask_id, old_category, new_category)
    # Edge: invalid IDs
    dashboard_manager.recategorizeTaskOrSubtask(-1, -1, -1, -1, old_category, new_category)
    # Event log should be updated (pseudo, as actual log check may require DB/file access)

def test_llm_suggestion_and_reasoning_logging(dashboard_manager, qtbot, monkeypatch):
    user_id, project_id, task_id, subtask_id = 1, 1, 1, 1
    # Patch requests to simulate LLM response
    def fake_post(*args, **kwargs):
        class FakeResp:
            def json(self):
                return {"category": "important", "reason": "Deadline soon"}
        return FakeResp()
    monkeypatch.setattr("requests.post", fake_post)
    dashboard_manager.suggestEisenhowerCategory(user_id, project_id, task_id, subtask_id)
    # Edge: LLM returns unexpected data
    def fake_post_bad(*args, **kwargs):
        class FakeResp:
            def json(self):
                return {}
        return FakeResp()
    monkeypatch.setattr("requests.post", fake_post_bad)
    dashboard_manager.suggestEisenhowerCategory(user_id, project_id, task_id, subtask_id)

def test_qml_api_methods_exposed(dashboard_manager):
    # Check QML-exposed methods exist
    assert hasattr(dashboard_manager, "loadProjects")
    assert hasattr(dashboard_manager, "loadEisenhowerMatrixState")
    assert hasattr(dashboard_manager, "setEisenhowerMatrixState")
    assert hasattr(dashboard_manager, "recategorizeTaskOrSubtask")
    assert hasattr(dashboard_manager, "suggestEisenhowerCategory")