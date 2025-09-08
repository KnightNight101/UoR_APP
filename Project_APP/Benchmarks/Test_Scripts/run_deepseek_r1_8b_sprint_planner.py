# sprint_benchmark.py

import csv
import json
import time
import re
import subprocess
from difflib import SequenceMatcher
import nltk
from datetime import datetime, timedelta


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
import threading

def run_ollama_live(prompt: str, timeout: int = 1200):
    """
    Run ollama in live mode with streaming stdout/stderr.
    Returns: stdout_text, stderr_text, elapsed_time
    """
    stdout_lines = []
    stderr_lines = []

    # Reader function for live printing
    def reader(stream, collector, label=""):
        try:
            for line_bytes in iter(stream.readline, b""):
                line = line_bytes.decode("utf-8", errors="replace")
                print(line, end="")  # live print
                collector.append(line)
        except Exception as e:
            print(f"[ERROR] Reader {label}: {e}")
        finally:
            stream.close()

    start_time = time.time()
    try:
        proc = subprocess.Popen(
            ["ollama", "run", "deepseek-r1:8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )

        # Start stdout and stderr reader threads
        t_out = threading.Thread(target=reader, args=(proc.stdout, stdout_lines, "stdout"))
        t_err = threading.Thread(target=reader, args=(proc.stderr, stderr_lines, "stderr"))
        t_out.start()
        t_err.start()

        # Send prompt
        proc.stdin.write(prompt.encode("utf-8"))
        proc.stdin.close()

        # Wait for process to finish or timeout
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"[ERROR] Timeout expired after {timeout} seconds")

        t_out.join()
        t_err.join()

    except KeyboardInterrupt:
        proc.kill()
        print("[INFO] KeyboardInterrupt detected. Process killed.")
    except Exception as e:
        proc.kill()
        print(f"[ERROR] Exception in run_ollama_live: {e}")

    elapsed = time.time() - start_time
    stdout_text = "".join(stdout_lines)
    stderr_text = "".join(stderr_lines)
    return stdout_text, stderr_text, elapsed




def extract_json_array(raw_output: str):
    """
    Finds the first JSON array in the model output.
    Strips code fences and leading explanations.
    """
    # Remove ```json fences
    cleaned = re.sub(r"^```json|```$", "", raw_output, flags=re.IGNORECASE).strip()
    # Find first JSON array
    match = re.search(r"\[.*?\]", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode failed: {e}")
            return None
    return None


def check_feasibility(plan, tasks, team, sprint_days):
    """
    Check if the model's sprint plan is feasible.
    
    - Dependencies are respected.
    - Assigned hours do not exceed team capacity.
    - Dates are within sprint_days.
    
    Returns: (feasible_bool, notes_list)
    """
    task_map = {t['name']: t for t in tasks}
    team_map = {m['name']: m['hours_per_day'] * sprint_days for m in team}
    feasible = True
    notes = []

    for t in plan:
        name = t.get('task')
        assigned = t.get('assigned_to')
        start = t.get('start')
        end = t.get('end')
        duration = t.get('duration_hours', 0)

        # Check if team member exists
        if assigned not in team_map:
            feasible = False
            notes.append(f"Unknown team member assigned to task {name}")
            continue

        # Check if assigned duration exceeds capacity
        if duration > team_map[assigned]:
            feasible = False
            notes.append(
                f"Task {name} assigned hours {duration} exceed {assigned}'s capacity {team_map[assigned]}"
            )

        # Check dependencies
        deps = task_map[name].get('dependencies', [])
        for d in deps:
            dep_task = next((x for x in plan if x['task'] == d), None)
            if not dep_task:
                feasible = False
                notes.append(f"Dependency {d} for task {name} not scheduled")
            else:
                dep_end = datetime.fromisoformat(dep_task['end'])
                task_start = datetime.fromisoformat(start)
                if task_start < dep_end:
                    feasible = False
                    notes.append(f"Task {name} starts before dependency {d} ends")

    return feasible, notes


###############################
# Team & Sprint Settings
###############################

# Define team members and their daily available hours
team_members = [
    {"name": "Alice", "hours_per_day": 6},
    {"name": "Bob", "hours_per_day": 4},
    {"name": "Charlie", "hours_per_day": 8},
]

# Sprint length in days
sprint_days = 5

# Sprint start date
sprint_start_date = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0)

###############################
# Test Cases
###############################

# Each test case is a dictionary:
# - 'tasks': list of tasks with dependencies, estimated hours, optional assigned_to
# - 'description': what the scenario is testing
test_cases = [
    {
        "description": "Simple 3-task linear dependency",
        "tasks": [
            {"name": "Task A", "duration_hours": 8, "dependencies": [], "assigned_to": "Alice"},
            {"name": "Task B", "duration_hours": 4, "dependencies": ["Task A"], "assigned_to": "Bob"},
            {"name": "Task C", "duration_hours": 6, "dependencies": ["Task B"], "assigned_to": "Charlie"},
        ]
    },
    {
        "description": "Parallel tasks with shared resources",
        "tasks": [
            {"name": "Design UI", "duration_hours": 6, "dependencies": [], "assigned_to": "Alice"},
            {"name": "Backend API", "duration_hours": 12, "dependencies": [], "assigned_to": "Bob"},
            {"name": "Integration Testing", "duration_hours": 4, "dependencies": ["Design UI", "Backend API"], "assigned_to": "Charlie"},
        ]
    },
    {
        "description": "Overbooked team member",
        "tasks": [
            {"name": "Task X", "duration_hours": 10, "dependencies": [], "assigned_to": "Alice"},
            {"name": "Task Y", "duration_hours": 8, "dependencies": ["Task X"], "assigned_to": "Alice"},
            {"name": "Task Z", "duration_hours": 6, "dependencies": ["Task Y"], "assigned_to": "Bob"},
        ]
    },
    {
        "description": "Tasks without assigned member (model decides)",
        "tasks": [
            {"name": "Write Documentation", "duration_hours": 6, "dependencies": []},
            {"name": "Code Review", "duration_hours": 4, "dependencies": ["Write Documentation"]},
            {"name": "Deploy to Production", "duration_hours": 2, "dependencies": ["Code Review"]},
        ]
    },
    {
        "description": "Complex web with multiple dependencies",
        "tasks": [
            {"name": "Set up DB", "duration_hours": 4, "dependencies": []},
            {"name": "Implement Auth", "duration_hours": 6, "dependencies": ["Set up DB"]},
            {"name": "Frontend Layout", "duration_hours": 5, "dependencies": []},
            {"name": "API Integration", "duration_hours": 8, "dependencies": ["Implement Auth", "Frontend Layout"]},
            {"name": "End-to-End Testing", "duration_hours": 6, "dependencies": ["API Integration"]},
        ]
    },
]


def extract_thoughts(raw_output: str, preview_lines: int = 10):
    """
    Grab the first N lines of the model's reasoning as 'thoughts'.
    """
    lines = raw_output.strip().splitlines()
    # Skip empty lines and "Thinking..." header
    meaningful = [l for l in lines if l.strip() and "Thinking" not in l][:preview_lines]
    return "\n".join(meaningful)


def main():
    results_file = "results_sprint_planner.csv"
    fieldnames = [
        "test_case", "description", "valid_json", "raw_output", "thoughts",
        "schedule_feasible", "dependency_accuracy", "resource_balance",
        "time_utilization", "makespan_hours", "task_alignment",
        "semantic_similarity", "precision", "recall", "f1_score",
        "jaccard_index", "rouge_l", "bleu",
        "time_total", "time_thinking"
    ]

    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, (desc, tasks) in enumerate(test_cases, start=1):
            print(f"\n[INFO] Running test case {i}: {desc}")

            # Build prompt
            prompt = f"""
You are an Agile sprint planner. 
Take the following tasks with estimates, dependencies, and team assignments, and return a sprint plan in JSON array format.

Each task object must contain:
- "id"
- "name"
- "hours"
- "assignee"
- "start"
- "end"

Respond with ONLY a JSON array, nothing else.
Tasks: {json.dumps(tasks, indent=2)}
"""

            # Run model
            stdout, stderr, elapsed = run_ollama_live(prompt)
            raw_output = stdout
            print("[RAW OUTPUT]", raw_output[:300], "...\n")

            # -------------------------
            # JSON Extraction & Parsing
            # -------------------------
            valid_json = False
            predicted_plan = extract_json_array(raw_output)
            valid_json = predicted_plan is not None
            if not valid_json:
                print("[WARN] Failed to parse JSON array from model output.")


            try:
                cleaned_output = raw_output.strip()
                cleaned_output = re.sub(r"^```json", "", cleaned_output, flags=re.IGNORECASE).strip()
                cleaned_output = re.sub(r"```$", "", cleaned_output).strip()

                match = re.search(r"\[.*\]", cleaned_output, re.DOTALL)
                if match:
                    predicted_plan = json.loads(match.group(0))
                    valid_json = True
                else:
                    print("[WARN] No JSON array found in output")

                # Capture reasoning if present
                thoughts_match = re.search(r'"thoughts"\s*:\s*"([^"]*)"', cleaned_output, re.DOTALL)
                if thoughts_match:
                    thoughts = thoughts_match.group(1)

            except Exception as e:
                print(f"[ERROR] JSON parse failed: {e}")

            # -------------------------
            # Evaluate Metrics
            # -------------------------
            metrics = {
                "feasibility": check_feasibility(predicted_plan),
                "deps": check_dependencies(tasks, predicted_plan),
                "balance": check_balance(predicted_plan),
                "utilization": check_utilization(predicted_plan),
                "effort": check_effort(tasks, predicted_plan),
                "coverage": check_coverage(tasks, predicted_plan),
                "coherence": check_coherence(predicted_plan),
                "scalability": check_scalability(predicted_plan),
            }

            # Log results to CSV
            row = {
                "test_case": i,
                "description": desc,
                "expected_tasks": json.dumps(tasks),
                "predicted_plan": json.dumps(predicted_plan) if valid_json else "",
                "thoughts": thoughts,
                "raw_output": raw_output,
                "valid_json": valid_json,
                "time_total": elapsed,
                **metrics
            }
            writer.writerow(row)
            f.flush()  # <-- ensures it's written immediately

            print(f"[RESULT] "
                  f"Feasibility={metrics['feasibility']:.2f}, "
                  f"Deps={metrics['deps']:.2f}, "
                  f"Balance={metrics['balance']:.2f}, "
                  f"Util={metrics['utilization']:.2f}, "
                  f"Effort={metrics['effort']:.2f}, "
                  f"Coverage={metrics['coverage']:.2f}, "
                  f"Coherence={metrics['coherence']:.2f}, "
                  f"Scalability={metrics['scalability']:.2f}")

def check_schedule_feasibility(tasks_predicted, sprint_days):
    """Check if predicted tasks have valid start/end dates within sprint window."""
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
    return feasible
def check_dependency_accuracy(tasks_expected, tasks_predicted):
    """Check how many dependencies are correctly respected."""
    dep_correct, dep_total = 0, 0
    expected_deps = {t["name"]: t["dependencies"] for t in tasks_expected}
    predicted_lookup = {t["name"]: t for t in tasks_predicted}

    for t in tasks_expected:
        name = t["name"]
        deps = t.get("dependencies", [])
        dep_total += len(deps)
        for d in deps:
            if name in predicted_lookup and d in predicted_lookup:
                try:
                    start = datetime.fromisoformat(predicted_lookup[name]["start"])
                    end_dep = datetime.fromisoformat(predicted_lookup[d]["end"])
                    if start >= end_dep:
                        dep_correct += 1
                except Exception:
                    pass

    return dep_correct / dep_total if dep_total > 0 else 0

def check_resource_balance(tasks_predicted, team_availability):
    """Check workload fairness across team members compared to availability."""
    workload = {m: 0 for m in team_availability.keys()}

    for t in tasks_predicted:
        assignee = t.get("assignee")
        hours = t.get("hours", 0)
        if assignee in workload:
            workload[assignee] += hours

    ratios = []
    for m, available in team_availability.items():
        if available > 0:
            ratios.append(workload[m] / available)

    if not ratios:
        return 0.0

    # Lower variance = better balance
    variance = sum((r - sum(ratios)/len(ratios))**2 for r in ratios) / len(ratios)
    return 1 / (1 + variance)

def check_time_utilization(tasks_predicted, team_availability):
    """Measure how well total planned hours fit into available hours."""
    total_planned = sum(t.get("hours", 0) for t in tasks_predicted)
    total_available = sum(team_availability.values())

    if total_available == 0:
        return 0.0

    utilization = total_planned / total_available
    return min(utilization, 1.0)  # cap at 1.0

def check_effort_estimation(tasks_predicted, tasks_expected):
    """Compare predicted task effort (hours) with expected values."""
    errors = []

    expected_map = {t["id"]: t.get("hours", 0) for t in tasks_expected}

    for t in tasks_predicted:
        tid = t.get("id")
        if tid in expected_map:
            predicted = t.get("hours", 0)
            expected = expected_map[tid]
            if expected > 0:
                errors.append(abs(predicted - expected) / expected)

    if not errors:
        return 0.0

    # Lower error = better, so convert to a score
    mean_error = sum(errors) / len(errors)
    return max(0.0, 1.0 - mean_error)

def check_coverage(tasks_predicted, tasks_expected):
    """Check how many expected tasks are included in the plan."""
    predicted_ids = {t.get("id") for t in tasks_predicted}
    expected_ids = {t.get("id") for t in tasks_expected}

    if not expected_ids:
        return 0.0

    covered = predicted_ids.intersection(expected_ids)
    return len(covered) / len(expected_ids)
def check_output_coherence(tasks_predicted):

    """Verify that the output has coherent structure and valid fields."""
    if not isinstance(tasks_predicted, list) or not tasks_predicted:
        return 0.0

    required_keys = {"id", "task", "hours", "assignee", "start", "end"}
    valid_count = 0

    for t in tasks_predicted:
        if not isinstance(t, dict):
            continue
        if required_keys.issubset(set(t.keys())):
            valid_count += 1

    return valid_count / len(tasks_predicted)

def check_scalability(tasks_predicted, expected_count):
    """Check if the model scales to larger sprint plans without truncation."""
    if expected_count == 0:
        return 0.0
    return min(1.0, len(tasks_predicted) / expected_count)

def main():
    results_file = "results_sprint.csv"
    fieldnames = [
        "test_case", "description", "valid_json", "thoughts", "raw_output",
        "schedule_feasibility", "dependency_accuracy", "resource_balance",
        "time_utilization", "effort_accuracy", "coverage",
        "output_coherence", "scalability",
        "time_total"
    ]

    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, case in enumerate(test_cases, start=1):
            print(f"\n[INFO] Running test case {i}: {case['description']}")

            # Prompt model
            prompt = f"""
You are an assistant that creates Agile sprint plans.

Each plan must output a JSON array of tasks with fields:
- id (string)
- task (string)
- hours (int)
- assignee (string)
- start (ISO datetime)
- end (ISO datetime)

Consider task dependencies, available hours, and resource balancing.
Ensure schedule is feasible.

Tasks:
{json.dumps(case['tasks'], indent=2)}
"""

            stdout, stderr, elapsed = run_ollama_live(prompt)
            raw_output = stdout
            print("[RAW OUTPUT]", raw_output[:400], "...\n")

            valid_json = False
            tasks_predicted, thoughts = [], ""

            # Parse JSON
            try:
                match = re.search(r"\[.*\]", raw_output, re.DOTALL)
                if match:
                    tasks_predicted = json.loads(match.group(0))
                    valid_json = True
                # Extract thoughts before JSON
                thoughts_match = re.split(r"\[", raw_output, 1)
                if len(thoughts_match) > 1:
                    thoughts = thoughts_match[0].strip()
            except Exception as e:
                print(f"[ERROR] JSON parse failed: {e}")

            # Metrics
            schedule_feasibility = check_schedule_feasibility(tasks_predicted) if valid_json else 0
            dependency_accuracy = check_dependency_accuracy(tasks_predicted, case['tasks']) if valid_json else 0
            resource_balance = check_resource_balance(tasks_predicted) if valid_json else 0
            time_utilization = check_time_utilization(tasks_predicted, case['resources']) if valid_json else 0
            effort_accuracy = check_effort_accuracy(tasks_predicted, case['tasks']) if valid_json else 0
            coverage = check_coverage(tasks_predicted, case['tasks']) if valid_json else 0
            output_coherence = check_output_coherence(tasks_predicted) if valid_json else 0
            scalability = check_scalability(tasks_predicted, len(case['tasks'])) if valid_json else 0

            # Save result
            row = {
                "test_case": i,
                "description": case["description"],
                "valid_json": valid_json,
                "thoughts": thoughts,
                "raw_output": raw_output,
                "schedule_feasibility": schedule_feasibility,
                "dependency_accuracy": dependency_accuracy,
                "resource_balance": resource_balance,
                "time_utilization": time_utilization,
                "effort_accuracy": effort_accuracy,
                "coverage": coverage,
                "output_coherence": output_coherence,
                "scalability": scalability,
                "time_total": elapsed,
            }
            writer.writerow(row)

            # Print live results
            print(f"[RESULT] Feasibility={schedule_feasibility:.2f}, "
                  f"Deps={dependency_accuracy:.2f}, Balance={resource_balance:.2f}, "
                  f"Util={time_utilization:.2f}, Effort={effort_accuracy:.2f}, "
                  f"Coverage={coverage:.2f}, Coherence={output_coherence:.2f}, "
                  f"Scalability={scalability:.2f}")

if __name__ == "__main__":
    main()
