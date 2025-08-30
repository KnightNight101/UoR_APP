import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import difflib
import csv
import datetime
import time
from pathlib import Path
from app.backend.tiny_llama import TinyLlamaPlanner

planner = TinyLlamaPlanner()
RESULTS_FILE = f"benchmark_results_{datetime.date.today()}_debug.csv"

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

def query_llm_debug(prompt):
    print("\n--- LLM Prompt ---")
    print(prompt[:500])  # print first 500 chars
    start = time.time()
    try:
        output = planner.query_llm(prompt)
    except Exception as e:
        print(f"⚠️ LLM call failed: {e}")
        output = ""
    end = time.time()
    print(f"--- LLM Output ({end - start:.2f}s) ---")
    print(output[:500])
    return output

# -------------------------
# Commit Summary Tests
# -------------------------
def run_commit_summary_tests():
    cases = json.load(open("tests/commit_summary_tests.json"))
    results = []
    for case in cases:
        prompt = f"Summarize the following code changes as a git commit message:\n{case.get('diff', '')}"
        output = query_llm_debug(prompt)
        sim = similarity(case.get("expected", ""), output)
        results.append({
            "task": "commit_summary",
            "input": case.get("diff", ""),
            "expected": case.get("expected", ""),
            "output": output,
            "similarity": round(safe_float(sim), 3)
        })
    return results

# -------------------------
# Eisenhower Matrix Tests
# -------------------------
def run_eisenhower_tests():
    cases = json.load(open("tests/eisenhower_tests.json"))
    results = []
    for case in cases:
        prompt = f"Sort these tasks into an Eisenhower matrix (Do First, Schedule, Delegate, Eliminate) in JSON format:\n{json.dumps(case.get('tasks', []))}"
        output = query_llm_debug(prompt)
        accuracy = 0
        parsed_result = {}
        try:
            parsed_result = json.loads(output)
        except json.JSONDecodeError:
            # Try a simple fix (single quotes → double quotes)
            try:
                parsed_result = json.loads(output.replace("'", '"'))
            except:
                parsed_result = {}
        try:
            correct = 0
            total = len(case.get("expected", {}))
            for quadrant, ids in case.get("expected", {}).items():
                if set(ids) == set(parsed_result.get(quadrant, [])):
                    correct += 1
            accuracy = correct / total if total else 0
        except:
            accuracy = 0
        results.append({
            "task": "eisenhower",
            "input": json.dumps(case.get("tasks", [])),
            "expected": json.dumps(case.get("expected", {})),
            "output": output,
            "accuracy": round(safe_float(accuracy), 3)
        })
    return results

# -------------------------
# Sprint Planning Tests
# -------------------------
def run_sprint_planning_tests():
    cases = json.load(open("tests/sprint_planning_tests.json"))
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
        output = query_llm_debug(prompt)
        score = 0
        parsed_result = {}
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
                assigned_hours[m] <= case["team"][m].get("available_hours", 0) for m in case.get("team", {})
            )
            score = int(deps_satisfied and hours_ok)
        except:
            score = 0
        results.append({
            "task": "sprint_planning",
            "input": f"team={json.dumps(case.get('team', {}))}, tasks={json.dumps(case.get('tasks', []))}",
            "expected": "Valid sprint plan respecting constraints",
            "output": output,
            "valid_plan": safe_int(score)
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
    results += run_commit_summary_tests()
    results += run_eisenhower_tests()
    results += run_sprint_planning_tests()
    save_results(results)

if __name__ == "__main__":
    main()
