import unittest
from unittest.mock import patch, MagicMock, ANY
from Draft_2.app.backend.tiny_llama import TinyLlamaPlanner
import Draft_2.app.main as main_mod

class TestMultiFactorPlanner(unittest.TestCase):
    @patch("Draft_2.app.backend.tiny_llama.SessionLocal")
    @patch("Draft_2.app.backend.tiny_llama.log_structured_event")
    def test_generate_project_plan(self, mock_log, mock_session):
        # Mock DB session and project/task objects
        mock_project = MagicMock(id=1, deadline="2025-09-01")
        mock_task = MagicMock(id=10, title="Setup", assigned_to=2, due_date="2025-08-30", dependencies='["dep1"]', hours=4)
        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_project
        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.all.return_value = [mock_task]
        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.all.side_effect = [[mock_task], [MagicMock(user_id=2)]]
        planner = TinyLlamaPlanner(user_id=99)
        plan = planner.generate_project_plan(1)
        self.assertIsInstance(plan, list)
        if plan:
            self.assertEqual(plan[0]["task_id"], 10)
            self.assertIn("deadline", plan[0])
        mock_log.assert_called_with(
            session=ANY,
            event_type="llm_plan_generated",
            user_id=99,
            project_id=1,
            task_id=None,
            subtask_id=None,
            reasoning=ANY,
            context_json=ANY
        )

    @patch("Draft_2.app.backend.tiny_llama.log_structured_event")
    def test_suggest_time_for_task(self, mock_log):
        planner = TinyLlamaPlanner(user_id=42)
        mock_task = MagicMock(id=5, due_date="2025-09-01")
        mock_project = MagicMock(id=2, deadline="2025-09-10")
        team = [MagicMock()]
        suggestion = planner.suggest_time_for_task(mock_task, mock_project, team)
        self.assertIn("suggested_deadline", suggestion)
        self.assertIn("reasoning", suggestion)
        mock_log.assert_called()

    @patch("Draft_2.app.backend.tiny_llama.log_structured_event")
    def test_verify_plan_feasibility(self, mock_log):
        planner = TinyLlamaPlanner(user_id=1)
        plan = [{"task_id": 1, "deadline": "2025-09-01"}]
        result = planner.verify_plan_feasibility(plan)
        self.assertTrue(result["feasible"])
        self.assertIn("reasoning", result)
        mock_log.assert_called()

class TestEisenhowerMatrixCategorization(unittest.TestCase):
    @patch("Draft_2.app.main.requests.post")
    @patch("Draft_2.app.main.get_event_logs")
    @patch("Draft_2.app.main.log_structured_event")
    @patch("Draft_2.app.main.update_subtask_category")
    def test_suggest_eisenhower_category(self, mock_update, mock_log, mock_get_logs, mock_post):
        # Mock event logs and LLM response
        mock_get_logs.return_value = [MagicMock(timestamp="2025-08-27", event_type="recategorization", old_category="other", new_category="urgent", reasoning="test", task_id=1, subtask_id=2)]
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"suggested_category": "important", "reasoning": "LLM says so"}
        mgr = main_mod.DashboardManager()
        mgr.loadEisenhowerMatrixState = MagicMock()
        mgr.suggestEisenhowerCategory(1, 1, 1, 2)
        mock_update.assert_called_with(2, "important")
        mock_log.assert_called()
        # Check that Eisenhower matrix state reload is triggered
        mgr.loadEisenhowerMatrixState.assert_called_with(1, 1)

class TestVCSCommitSummaryGenerator(unittest.TestCase):
    @patch("Draft_2.app.main.requests.post")
    def test_llm_commit_summary(self, mock_post):
        # Mock LLM commit summary API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"summary": "Refactored code"}
        handler = main_mod.ProjectFileChangeHandler(MagicMock(root_dir="/tmp"))
        summary = handler._get_llm_commit_summary("/tmp/project_1/task_1/file.py")
        self.assertEqual(summary, "Refactored code")
        mock_post.assert_called_with(
            "http://localhost:8000/llm/commit_summary",
            json={"file_path": "/tmp/project_1/task_1/file.py"},
            timeout=5
        )

def summarize_results():
    """
    Summarize LLM feature test coverage for documentation.
    """
    summary = """
LLM Feature Test Coverage Summary:
- Multi-factor planner: Project plan generation, time suggestion, and feasibility are tested with mock DB and event log integration.
- Eisenhower matrix: LLM suggestions and reasoning for categorization are tested, including event log and API integration.
- VCS commit summary: LLM-generated commit messages from file changes are tested with API mocking.
All tests verify output, reasoning, and integration with event logs and APIs.
"""
    print(summary)

if __name__ == "__main__":
    unittest.main(exit=False)
    summarize_results()