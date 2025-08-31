import sys
from pathlib import Path
import json
import difflib
import csv
import datetime
import time
import subprocess

# Add your backend path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.backend.tiny_llama import TinyLlamaPlanner
from app.backend.deepseek_r1 import DeepseekR1Interface

RESULTS_FILE = f"benchmark_results_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

# -------------------------
# Utilities
# -------------------------
def similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def safe_float(s, default=0.0):
    try:
        return float(s)
    except (ValueError, TypeError):
        return default

def safe_int(s, default=0):
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default

# -------------------------
# Commit Summary Tests
# -------------------------
def run_commit_summary_tests(planner, model_name):
    cases = json.load(open("Draft_2/tests/commit_summary_tests.json"))
    results = []
    for case in cases:
        prompt = f"Summarize the following code changes as a git commit message:\n{case.get('diff', '')}"
        start = time.time()
        if model_name == "TinyLlama":
            output = planner.query_llm(prompt)
        else:
            output = planner.generate_response(prompt)
        elapsed = time.time() - start
        sim = similarity(case.get("expected", ""), output)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results.append({
            "timestamp": timestamp,
            "model": model_name,
            "task": "commit_summary",
            "input": case.get("diff", ""),
            "expected": case.get("expected", ""),
            "output": output,
            "similarity": round(safe_float(sim), 3),
            "time_taken_sec": round(elapsed, 3)
        })
    return results

# -------------------------
# Eisenhower Matrix Tests
# -------------------------
def run_eisenhower_tests(planner, model_name):
    cases = json.load(open("Draft_2/tests/eisenhower_tests.json"))
    results = []
    for case in cases:
        prompt = f"Sort these tasks into an Eisenhower matrix (Do First, Schedule, Delegate, Eliminate) in JSON format:\n{json.dumps(case.get('tasks', []))}"
        start = time.time()
        if model_name == "TinyLlama":
            output = planner.query_llm(prompt)
        else:
            output = planner.generate_response(prompt)
        elapsed = time.time() - start

        # Parse JSON safely
        try:
            parsed_result = json.loads(output)
        except json.JSONDecodeError:
            try:
                parsed_result = json.loads(output.replace("'", '"'))
            except:
                parsed_result = {}

        correct = 0
        total = len(case.get("expected", {}))
        tp = 0
        fp = 0
        for quadrant, ids in case.get("expected", {}).items():
            expected_set = set(ids)
            predicted_set = set(parsed_result.get(quadrant, []))
            if expected_set == predicted_set:
                correct += 1
            tp += len(expected_set & predicted_set)
            fp += len(predicted_set - expected_set)
        accuracy = correct / total if total else 0
        precision = tp / (tp + fp) if (tp + fp) else 0

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results.append({
            "timestamp": timestamp,
            "model": model_name,
            "task": "eisenhower",
            "input": json.dumps(case.get("tasks", [])),
            "expected": json.dumps(case.get("expected", {})),
            "output": output,
            "accuracy": round(safe_float(accuracy), 3),
            "precision": round(safe_float(precision), 3),
            "time_taken_sec": round(elapsed, 3)
        })
    return results

# -------------------------
# Sprint Planning Tests
# -------------------------
def run_sprint_planning_tests(planner, model_name):
    cases = json.load(open("Draft_2/tests/sprint_planning_tests.json"))
    results = []
    for case in cases:
        prompt = f"""
Plan a 2-week agile sprint for the following team and tasks. 
Constraints:
- Respect task dependencies
- Do not assign more hours than available
- Output JSON with format: {{'sprint_backlog': [{{'task_id': int, 'assignee': str, 'week': int}}]}}
Team: {json.dumps(case.get('team', {}))}
Tasks: {json.dumps(case.get('tasks', []))}
"""
        start = time.time()
        if model_name == "TinyLlama":
            output = planner.query_llm(prompt)
        else:
            output = planner.generate_response(prompt)
        elapsed = time.time() - start

        # Validate sprint plan
        score = 0
        try:
            parsed_result = json.loads(output)
        except json.JSONDecodeError:
            try:
                parsed_result = json.loads(output.replace("'", '"'))
            except:
                parsed_result = {}

        try:
            backlog = parsed_result.get("sprint_backlog", [])
            assigned_hours = {m: 0 for m in case.get("team", {})}
            deps_satisfied = True
            for entry in backlog:
                task = next((t for t in case.get("tasks", []) if t["id"] == entry.get("task_id")), None)
                if task:
                    assigned_hours[entry.get("assignee", "")] += task.get("estimate", 0)
                    for dep in task.get("dependencies", []):
                        dep_scheduled = any(
                            d.get("task_id") == dep for d in backlog if d.get("week", 0) < entry.get("week", 0)
                        )
                        if not dep_scheduled:
                            deps_satisfied = False
            hours_ok = all(
                assigned_hours[m] <= case['team'][m].get("available_hours", 0) for m in case.get("team", {})
            )
            score = int(deps_satisfied and hours_ok)
        except:
            score = 0

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results.append({
            "timestamp": timestamp,
            "model": model_name,
            "task": "sprint_planning",
            "input": f"team={json.dumps(case.get('team', {}))}, tasks={json.dumps(case.get('tasks', []))}",
            "expected": "Valid sprint plan respecting constraints",
            "output": output,
            "valid_plan": safe_int(score),
            "time_taken_sec": round(elapsed, 3)
        })
    return results

# -------------------------
# Save Results
# -------------------------
def save_results(all_results):
    keys = set()
    for r in all_results:
        keys.update(r.keys())
    keys = list(keys)
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_results)
    print(f"Results saved to {RESULTS_FILE}")

# -------------------------
# Main
# -------------------------
def main():
    results = []

    # TinyLlama via Ollama
    tiny_llama = TinyLlamaPlanner(model_name="tinyllama")
    results += run_commit_summary_tests(tiny_llama, "TinyLlama")
    results += run_eisenhower_tests(tiny_llama, "TinyLlama")
    results += run_sprint_planning_tests(tiny_llama, "TinyLlama")

    # Deepseek via Ollama
    deepseek = DeepseekR1Interface(model_name="deepseek")
    results += run_commit_summary_tests(deepseek, "Deepseek")
    results += run_eisenhower_tests(deepseek, "Deepseek")
    results += run_sprint_planning_tests(deepseek, "Deepseek")

    save_results(results)


if __name__ == "__main__":
    main()
