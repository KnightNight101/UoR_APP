# sprint_benchmark.py

import csv
import json
import time
import re
import subprocess
from difflib import SequenceMatcher
import nltk
from datetime import datetime
from dateutil import parser
import os

# Ensure NLTK data is available
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

###############################
# Utility Functions
###############################

def semantic_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text (spinners, colors)."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_ollama_live(prompt: str, model: str = "llama3.1:8b", timeout: int = 600):
    """Run Ollama in non-interactive mode, capture stdout/stderr."""
    start_time = time.time()
    try:
        proc = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        stdout, stderr = proc.communicate(input=prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print(f"[ERROR] Timeout expired after {timeout} seconds")
    except Exception as e:
        proc.kill()
        stdout, stderr = "", str(e)
        print(f"[ERROR] Exception in run_ollama_live: {e}")
    elapsed = time.time() - start_time
    return strip_ansi(stdout), strip_ansi(stderr), elapsed

def extract_json_array(raw_output: str):
    """Extract the first JSON array found in the output."""
    match = re.search(r"\[.*?\]", raw_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return None
    return None

def parse_datetime_safe(dt_str):
    """Parse ISO or human-readable datetime, return None if invalid."""
    try:
        return parser.parse(dt_str)
    except Exception:
        return None

###############################
# Team & Sprint Settings
###############################

team_members = [
    {"name": "Alice", "hours_per_day": 6},
    {"name": "Bob", "hours_per_day": 4},
    {"name": "Charlie", "hours_per_day": 8},
]

sprint_days = 5
sprint_start_date = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0)

###############################
# Test Cases
###############################

test_cases = [
    {
        "description": "Simple 3-task linear dependency",
        "tasks": [
            {"id": "A", "name": "Task A", "duration_hours": 8, "dependencies": [], "assigned_to": "Alice"},
            {"id": "B", "name": "Task B", "duration_hours": 4, "dependencies": ["A"], "assigned_to": "Bob"},
            {"id": "C", "name": "Task C", "duration_hours": 6, "dependencies": ["B"], "assigned_to": "Charlie"},
        ]
    },
    {
        "description": "Parallel tasks with shared resources",
        "tasks": [
            {"id": "D", "name": "Design UI", "duration_hours": 6, "dependencies": [], "assigned_to": "Alice"},
            {"id": "E", "name": "Backend API", "duration_hours": 12, "dependencies": [], "assigned_to": "Bob"},
            {"id": "F", "name": "Integration Testing", "duration_hours": 4, "dependencies": ["D", "E"], "assigned_to": "Charlie"},
        ]
    },
    {
        "description": "Overbooked team member",
        "tasks": [
            {"id": "X", "name": "Task X", "duration_hours": 10, "dependencies": [], "assigned_to": "Alice"},
            {"id": "Y", "name": "Task Y", "duration_hours": 8, "dependencies": ["X"], "assigned_to": "Alice"},
            {"id": "Z", "name": "Task Z", "duration_hours": 6, "dependencies": ["Y"], "assigned_to": "Bob"},
        ]
    },
    {
        "description": "Tasks without assigned member",
        "tasks": [
            {"id": "D1", "name": "Write Documentation", "duration_hours": 6, "dependencies": []},
            {"id": "D2", "name": "Code Review", "duration_hours": 4, "dependencies": ["D1"]},
            {"id": "D3", "name": "Deploy to Production", "duration_hours": 2, "dependencies": ["D2"]},
        ]
    },
    {
        "description": "Complex web with multiple dependencies",
        "tasks": [
            {"id": "DB", "name": "Set up DB", "duration_hours": 4, "dependencies": []},
            {"id": "AUTH", "name": "Implement Auth", "duration_hours": 6, "dependencies": ["DB"]},
            {"id": "UI", "name": "Frontend Layout", "duration_hours": 5, "dependencies": []},
            {"id": "API", "name": "API Integration", "duration_hours": 8, "dependencies": ["AUTH", "UI"]},
            {"id": "TEST", "name": "End-to-End Testing", "duration_hours": 6, "dependencies": ["API"]},
        ]
    },
]

###############################
# Metrics
###############################

def check_schedule_feasibility(tasks_predicted, sprint_days=5):
    feasible = True
    for t in tasks_predicted:
        start = parse_datetime_safe(t.get("start"))
        end = parse_datetime_safe(t.get("end"))
        if not start or not end:
            feasible = False
        elif end < start or (end - start).days > sprint_days:
            feasible = False
    return 1.0 if feasible else 0.0

def check_output_coherence(tasks_predicted):
    if not isinstance(tasks_predicted, list) or not tasks_predicted:
        return 0.0
    required_keys = {"id", "task", "hours", "assignee", "start", "end"}
    valid_count = sum(1 for t in tasks_predicted if isinstance(t, dict) and required_keys.issubset(t.keys()))
    return valid_count / len(tasks_predicted)

def check_dependency_accuracy(tasks_predicted):
    task_map = {t["id"]: t for t in tasks_predicted}
    correct = 0
    total = 0
    for t in tasks_predicted:
        deps = t.get("dependencies", [])
        total += len(deps)
        for d in deps:
            dep_task = task_map.get(d)
            if not dep_task:
                continue
            t_start = parse_datetime_safe(t.get("start"))
            d_end = parse_datetime_safe(dep_task.get("end"))
            if t_start and d_end and t_start >= d_end:
                correct += 1
    return correct / total if total > 0 else 1.0

def check_resource_balance(tasks_predicted, team=team_members):
    availability = {m["name"]: m["hours_per_day"]*sprint_days for m in team}
    usage = {m["name"]:0 for m in team}
    for t in tasks_predicted:
        assignee = t.get("assignee")
        hours = t.get("hours", 0)
        if assignee in usage:
            usage[assignee] += hours
    ratios = [usage[m]/availability[m] for m in usage if availability[m]>0]
    mean_ratio = sum(ratios)/len(ratios) if ratios else 0
    variance = sum((r - mean_ratio)**2 for r in ratios)/len(ratios) if ratios else 0
    return 1/(1+variance) if variance>0 else 1.0

def check_time_utilization(tasks_predicted, team=team_members):
    total_planned = sum(t.get("hours",0) for t in tasks_predicted)
    total_available = sum(m["hours_per_day"]*sprint_days for m in team)
    utilization = total_planned/total_available if total_available>0 else 0
    return min(utilization, 1.0)

def check_effort_accuracy(tasks_predicted, tasks_expected):
    expected_map = {t["id"]: t.get("duration_hours",0) for t in tasks_expected}
    errors = []
    for t in tasks_predicted:
        tid = t.get("id")
        if tid in expected_map and expected_map[tid]>0:
            errors.append(abs(t.get("hours",0)-expected_map[tid])/expected_map[tid])
    return max(0, 1 - (sum(errors)/len(errors))) if errors else 1.0

def check_metrics(tasks_predicted, tasks_expected):
    return {
        "feasibility": check_schedule_feasibility(tasks_predicted),
        "coherence": check_output_coherence(tasks_predicted),
        "dependency_accuracy": check_dependency_accuracy(tasks_predicted),
        "resource_balance": check_resource_balance(tasks_predicted),
        "time_utilization": check_time_utilization(tasks_predicted),
        "effort_accuracy": check_effort_accuracy(tasks_predicted, tasks_expected),
    }

###############################
# Main
###############################

def main():
    results_file = "results_sprint.csv"
    fieldnames = [
        "test_case","description","valid_json","raw_output_file","thoughts_file",
        "feasibility","coherence","dependency_accuracy","resource_balance",
        "time_utilization","effort_accuracy","time_total"
    ]

    os.makedirs("outputs", exist_ok=True)

    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, case in enumerate(test_cases, start=1):
            print(f"\n[INFO] Running test case {i}: {case['description']}")

            base_prompt = f"""
You are an assistant that creates Agile sprint plans.
Rules:
1. Output only a JSON array of tasks.
2. Each task object must contain: id, task, hours, assignee, start, end.
3. Each working day has 8 hours, sprint length is {sprint_days} days, sprint starts Monday 9am.
4. Respect dependencies, durations, and avoid overlaps.
5. Assign tasks if 'assigned_to' missing.
Tasks:
{json.dumps(case['tasks'], indent=2)}
"""

            stdout, stderr, elapsed = run_ollama_live(base_prompt)
            raw_output = stdout + "\n" + stderr
            tasks_predicted = extract_json_array(raw_output)
            valid_json = tasks_predicted is not None

            # Reprompt if invalid or time utilization < 70%
            if not valid_json or (tasks_predicted and check_time_utilization(tasks_predicted) < 0.7):
                reprompt = ("Output must be valid JSON array of tasks only, "
                            "and improve time utilization to use at least 70% of total available hours.")
                stdout2, stderr2, elapsed2 = run_ollama_live(base_prompt + "\n" + reprompt)
                raw_output += "\n[REPROMPT]\n" + stdout2 + "\n" + stderr2
                tasks_predicted = extract_json_array(stdout2)
                valid_json = tasks_predicted is not None
                elapsed += elapsed2

            metrics = check_metrics(tasks_predicted, case['tasks']) if valid_json else {
                "feasibility":0,"coherence":0,"dependency_accuracy":0,
                "resource_balance":0,"time_utilization":0,"effort_accuracy":0
            }

            raw_output_file = f"outputs/raw_output_case{i}.txt"
            thoughts_file = f"outputs/thoughts_case{i}.txt"
            with open(raw_output_file,"w",encoding="utf-8") as rf:
                rf.write(raw_output)
            with open(thoughts_file,"w",encoding="utf-8") as tf:
                tf.write(stderr)

            row = {
                "test_case":i,
                "description":case["description"],
                "valid_json":valid_json,
                "raw_output_file":raw_output_file,
                "thoughts_file":thoughts_file,
                **metrics,
                "time_total":elapsed
            }
            writer.writerow(row)

            print(f"[RESULT] Feasibility={metrics['feasibility']:.2f}, "
                  f"Coherence={metrics['coherence']:.2f}, "
                  f"Dependency Accuracy={metrics['dependency_accuracy']:.2f}, "
                  f"Resource Balance={metrics['resource_balance']:.2f}, "
                  f"Time Utilization={metrics['time_utilization']:.2f}, "
                  f"Effort Accuracy={metrics['effort_accuracy']:.2f}, "
                  f"Time={elapsed:.1f}s")

if __name__ == "__main__":
    main()
