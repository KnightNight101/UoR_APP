import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import difflib
import csv
import datetime
from pathlib import Path
from app.backend.tiny_llama import TinyLlamaPlanner
planner = TinyLlamaPlanner()

RESULTS_FILE = f"benchmark_results_{datetime.date.today()}.csv"

def similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def run_commit_summary_tests():
    cases = json.load(open("tests/commit_summary_tests.json"))
    results = []
    for case in cases:
        prompt = f"Summarize the following code changes as a git commit message:\n{case['diff']}"
        output = planner.query_llm(prompt)
        sim = similarity(case["expected"], output)
        results.append({
            "task": "commit_summary",
            "input": case["diff"],
            "expected": case["expected"],
            "output": output,
            "similarity": round(sim, 3)
        })
    return results

def run_eisenhower_tests():
    cases = json.load(open("tests/eisenhower_tests.json"))
    results = []
    for case in cases:
        prompt = f"Sort these tasks into an Eisenhower matrix (Do First, Schedule, Delegate, Eliminate) in JSON format: {json.dumps(case['tasks'])}"
        output = planner.query_llm(prompt)
        try:
            result = json.loads(output)
            correct = 0
            total = len(case["expected"])
            for quadrant, ids in case["expected"].items():
                if set(ids) == set(result.get(quadrant, [])):
                    correct += 1
            accuracy = correct / total
        except:
            accuracy = 0
        results.append({
            "task": "eisenhower",
            "input": json.dumps(case["tasks"]),
            "expected": json.dumps(case["expected"]),
            "output": output,
            "accuracy": round(accuracy, 3)
        })
    return results

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
Team: {json.dumps(case['team'])}
Tasks: {json.dumps(case['tasks'])}
"""
        output = planner.query_llm(prompt)
        try:
            result = json.loads(output)
            backlog = result.get("sprint_backlog", [])
            assigned_hours = {m: 0 for m in case["team"]}
            deps_satisfied = True
            for entry in backlog:
                task = next(t for t in case["tasks"] if t["id"] == entry["task_id"])
                assigned_hours[entry["assignee"]] += task["estimate"]
                for dep in task["dependencies"]:
                    dep_scheduled = any(
                        d["task_id"] == dep for d in backlog if d["week"] < entry["week"]
                    )
                    if not dep_scheduled:
                        deps_satisfied = False
            hours_ok = all(
                assigned_hours[m] <= case["team"][m]["available_hours"] for m in case["team"]
            )
            score = int(deps_satisfied and hours_ok)
        except:
            score = 0
        results.append({
            "task": "sprint_planning",
            "input": f"team={json.dumps(case['team'])}, tasks={json.dumps(case['tasks'])}",
            "expected": "Valid sprint plan respecting constraints",
            "output": output,
            "valid_plan": score
        })
    return results

def save_results(all_results):
    # Gather all unique keys from all result dicts
    keys = set()
    for r in all_results:
        keys.update(r.keys())
    keys = list(keys)
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_results)
    print(f"Results saved to {RESULTS_FILE}")

def main():
    results = []
    results += run_commit_summary_tests()
    results += run_eisenhower_tests()
    results += run_sprint_planning_tests()
    save_results(results)

if __name__ == "__main__":
    main()
