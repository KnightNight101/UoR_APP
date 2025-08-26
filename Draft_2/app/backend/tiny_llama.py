import os
import json
from datetime import datetime, timedelta

from Draft_2.app.db import (
    log_structured_event, SessionLocal, Project, Task, Subtask, ProjectMember, User
)

class TinyLlamaPlanner:
    """
    Integrates TinyLlama for project plan generation and time/verification suggestions.
    All outputs and reasoning are logged to the event log.
    """

    def __init__(self, user_id=None):
        self.user_id = user_id

    def _log_llm_event(self, event_type, project_id=None, task_id=None, subtask_id=None, reasoning=None, context=None):
        with SessionLocal() as session:
            log_structured_event(
                session=session,
                event_type=event_type,
                user_id=self.user_id,
                project_id=project_id,
                task_id=task_id,
                subtask_id=subtask_id,
                reasoning=reasoning,
                context_json=context
            )

    def suggest_time_for_task(self, task: Task, project: Project, team_members: list, immovable_deadlines: list = None):
        """
        Suggests a deadline and verifies feasibility for a task using TinyLlama.
        Logs all outputs and reasoning.
        """
        # Placeholder: Replace with actual TinyLlama inference call
        suggestion = {
            "suggested_deadline": str(task.due_date or project.deadline),
            "reasoning": "Based on dependencies, team availability, and 8-hour workdays."
        }
        self._log_llm_event(
            event_type="llm_suggestion",
            project_id=project.id,
            task_id=task.id,
            reasoning=suggestion["reasoning"],
            context={"suggestion": suggestion}
        )
        return suggestion

    def generate_project_plan(self, project_id: int):
        """
        Generates a project plan considering dependencies, deadlines, team availability,
        8-hour workdays, and immovable deadlines. Logs all outputs and reasoning.
        """
        with SessionLocal() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                self._log_llm_event(
                    event_type="llm_plan_generation_failed",
                    project_id=project_id,
                    reasoning="Project not found.",
                    context=None
                )
                return None

            tasks = session.query(Task).filter(Task.project_id == project_id).all()
            members = session.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
            users = [session.query(User).filter(User.id == m.user_id).first() for m in members]

            # Placeholder: Replace with actual TinyLlama inference call
            plan = []
            for task in tasks:
                plan.append({
                    "task_id": task.id,
                    "title": task.title,
                    "assigned_to": task.assigned_to,
                    "deadline": str(task.due_date or project.deadline),
                    "dependencies": json.loads(task.dependencies) if task.dependencies else [],
                    "hours": task.hours or 8
                })

            reasoning = "Plan generated using dependencies, deadlines, team availability, and 8-hour workdays."
            self._log_llm_event(
                event_type="llm_plan_generated",
                project_id=project_id,
                reasoning=reasoning,
                context={"plan": plan}
            )
            return plan

    def verify_plan_feasibility(self, plan: list, immovable_deadlines: list = None):
        """
        Verifies if the plan is feasible given deadlines and constraints.
        Logs all outputs and reasoning.
        """
        # Placeholder: Replace with actual TinyLlama inference call
        feasible = True
        reasoning = "All tasks fit within deadlines and team constraints."
        self._log_llm_event(
            event_type="llm_plan_verification",
            reasoning=reasoning,
            context={"plan": plan, "feasible": feasible}
        )
        return {"feasible": feasible, "reasoning": reasoning}

# Example usage:
# planner = TinyLlamaPlanner(user_id=123)
# plan = planner.generate_project_plan(project_id=1)
# suggestion = planner.suggest_time_for_task(task, project, team_members)
# verification = planner.verify_plan_feasibility(plan)