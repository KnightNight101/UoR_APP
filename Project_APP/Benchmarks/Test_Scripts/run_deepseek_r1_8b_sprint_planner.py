# sprint_benchmark.py

import csv
import json
import time
import re
import subprocess
import threading
from difflib import SequenceMatcher
import nltk
from datetime import datetime

# Ensure NLTK data is available
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

###############################
# Utility Functions
###############################

def semantic_similarity(a, b):
    """Compute simple similarity between two strings using SequenceMatcher."""
    return SequenceMatcher(None, a, b).ratio()

import subprocess
import time
import re

def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from text (e.g., spinners, colors).
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_ollama_live(prompt: str, model: str = "llama3.1:8b", timeout: int = 1200):
    """
    Run Ollama in non-interactive mode, capture stdout/stderr.
    Returns: stdout_clean, stderr_clean, elapsed_time
    """
    start_time = time.time()
    proc = None
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
    stdout_clean = strip_ansi(stdout)
    stderr_clean = strip_ansi(stderr)
    return stdout_clean, stderr_clean, elapsed

JSON_ARRAY_RE = re.compile(
    r"```(?:json)?\s*(?P<fence>[\s\S]*?)```|(?P<nofence>\[[\s\S]*\])",
    re.IGNORECASE
)

def extract_json_array(raw_output: str):
    """
    Finds the first JSON array in the model output.
    """
    match = re.search(r"\[.*?\]", raw_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return None
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
    for task in tasks_predicted:
        try:
            start = datetime.fromisoformat(task["start"])
            end = datetime.fromisoformat(task["end"])
            if end < start:
                feasible = False
            if (end - start).days > sprint_days:
                feasible = False
        except Exception:
            feasible = False
    return 1.0 if feasible else 0.0

def check_output_coherence(tasks_predicted):
    if not isinstance(tasks_predicted, list) or not tasks_predicted:
        return 0.0
    required_keys = {"id", "task", "hours", "assignee", "start", "end"}
    valid_count = sum(1 for t in tasks_predicted if isinstance(t, dict) and required_keys.issubset(t.keys()))
    return valid_count / len(tasks_predicted)

###############################
# Main
###############################

def main():
    results_file = "results_sprint.csv"
    fieldnames = [
        "test_case", "description", "valid_json",
        "raw_output_file", "thoughts_file",
        "schedule_feasibility", "output_coherence", "time_total"
    ]

    import os
    os.makedirs("outputs", exist_ok=True)

    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, case in enumerate(TEST_CASES, start=1):
            desc = case["description"]
            tasks = case["tasks"]

            print(f"\n[INFO] Running test case {i}: {desc}")

            prompt = f"""
You are an Agile sprint planner.

Rules:
1. Output only a JSON array of tasks. 
2. Do not include any explanations, thoughts, or text outside the JSON.
3. Each task object must contain: id, task, hours, assignee, start, end.
4. Each working day has 8 hours, sprint length is {sprint_days} days, sprint starts Monday 9am.
5. Respect dependencies, durations, and avoid overlaps.
6. If 'assigned_to' is missing, assign to any available member.

Return ONLY a JSON array of task objects. Each object MUST include:
- "id" (string)
- "name" (string)
- "hours" (number)
- "assignee" (string)
- "start" (ISO 8601 datetime)
- "end"   (ISO 8601 datetime)

            stdout, stderr, elapsed = run_ollama_live(prompt)
            raw_output = stdout + "\n" + stderr

            valid_json = False
            tasks_predicted = []

            try:
                tasks_predicted = extract_json_array(raw_output)
                valid_json = tasks_predicted is not None
            except Exception as e:
                print(f"[ERROR] JSON parse failed: {e}")

            schedule_feasibility = check_schedule_feasibility(tasks_predicted) if valid_json else 0
            output_coherence = check_output_coherence(tasks_predicted) if valid_json else 0

            raw_output_file = f"outputs/raw_output_case{i}.txt"
            thoughts_file = f"outputs/thoughts_case{i}.txt"

            with open(raw_output_file, "w", encoding="utf-8") as rf:
                rf.write(raw_output)
            with open(thoughts_file, "w", encoding="utf-8") as tf:
                tf.write(stderr)

            row = {
                "test_case": i,
                "description": desc,
                "valid_json": valid_json,
                "raw_output_file": raw_output_file,
                "thoughts_file": thoughts_file,
                "schedule_feasibility": schedule_feasibility,
                "output_coherence": output_coherence,
                "time_total": elapsed,
            }
            writer.writerow(row)
            f.flush()

            print(f"[RESULT] Feasibility={schedule_feasibility:.2f}, "
                  f"Coherence={output_coherence:.2f}, "
                  f"Time={elapsed:.1f}s")

if __name__ == "__main__":
    main()
