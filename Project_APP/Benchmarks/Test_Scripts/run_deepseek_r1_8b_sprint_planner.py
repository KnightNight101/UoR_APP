# sprint_benchmark.py

import csv
import json
import time
import re
import os
import subprocess
import threading
from datetime import datetime, timedelta
from difflib import SequenceMatcher

###############################
# Config: team & sprint
###############################

TEAM_MEMBERS = [
    {"name": "Alice", "hours_per_day": 6},
    {"name": "Bob",   "hours_per_day": 4},
    {"name": "Charlie","hours_per_day": 8},
]

SPRINT_DAYS = 5
SPRINT_START = datetime.today().replace(hour=9, minute=0, second=0, microsecond=0)

THOUGHTS_DIR = "thoughts"
os.makedirs(THOUGHTS_DIR, exist_ok=True)

###############################
# Utility: availability map
###############################

def build_team_availability(team_members, sprint_days) -> dict:
    """
    Returns {member_name: total_available_hours_over_sprint}.
    """
    return {m["name"]: m["hours_per_day"] * sprint_days for m in team_members}

###############################
# Utility: live model runner
###############################

def run_ollama_live(prompt: str, timeout: int = 1200):
    """
    Run ollama with streaming output to terminal.
    Returns (stdout_text, stderr_text, elapsed_seconds)
    """
    stdout_lines = []
    stderr_lines = []

    def reader(stream, collector, label=""):
        try:
            for line_bytes in iter(stream.readline, b""):
                line = line_bytes.decode("utf-8", errors="replace")
                print(line, end="")
                collector.append(line)
        except Exception as e:
            print(f"[ERROR] Reader {label}: {e}")
        finally:
            try:
                stream.close()
            except Exception:
                pass

    start_time = time.time()
    proc = None
    try:
        proc = subprocess.Popen(
            ["ollama", "run", "deepseek-r1:8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        t_out = threading.Thread(target=reader, args=(proc.stdout, stdout_lines, "stdout"))
        t_err = threading.Thread(target=reader, args=(proc.stderr, stderr_lines, "stderr"))
        t_out.start()
        t_err.start()

        proc.stdin.write(prompt.encode("utf-8"))
        proc.stdin.close()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"\n[ERROR] Timeout expired after {timeout} seconds")

        t_out.join()
        t_err.join()

    except KeyboardInterrupt:
        if proc:
            proc.kill()
        print("\n[INFO] KeyboardInterrupt detected. Process killed.")
    except Exception as e:
        if proc:
            proc.kill()
        print(f"\n[ERROR] Exception in run_ollama_live: {e}")

    elapsed = time.time() - start_time
    return "".join(stdout_lines), "".join(stderr_lines), elapsed

###############################
# Utility: JSON extraction
###############################

JSON_ARRAY_RE = re.compile(
    r"```(?:json)?\s*(?P<fence>[\s\S]*?)```|(?P<nofence>\[[\s\S]*\])",
    re.IGNORECASE
)

def extract_json_array(raw_output: str):
    """
    Return first JSON array found. Handles fenced and unfenced outputs.
    """
    for m in JSON_ARRAY_RE.finditer(raw_output):
        blob = m.group("nofence") or m.group("fence")
        if blob is None:
            continue
        # If it was a fenced block, try to find the first [...] inside it
        if m.group("fence") is not None:
            arr = re.search(r"\[[\s\S]*\]", blob)
            if not arr:
                continue
            text = arr.group(0)
        else:
            text = blob
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed, text
        except Exception:
            continue
    # Fallback: naive search
    fallback = re.search(r"\[[\s\S]*\]", raw_output)
    if fallback:
        try:
            text = fallback.group(0)
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed, text
        except Exception:
            pass
    return None, None

###############################
# Metrics
###############################

def check_schedule_feasibility(tasks_predicted, sprint_start: datetime, sprint_days: int) -> float:
    """
    Score 0..1: proportion of tasks with valid ISO times, end >= start,
    and inside sprint window [sprint_start, sprint_start + sprint_days].
    """
    if not tasks_predicted:
        return 0.0

    ok = 0
    window_end = sprint_start + timedelta(days=sprint_days)
    for t in tasks_predicted:
        try:
            start = datetime.fromisoformat(t["start"])
            end = datetime.fromisoformat(t["end"])
            if end >= start and sprint_start <= start <= window_end and sprint_start <= end <= window_end:
                ok += 1
        except Exception:
            pass
    return ok / len(tasks_predicted)

def check_dependency_accuracy(tasks_expected, tasks_predicted) -> float:
    """
    Expected tasks declare dependencies by name.
    We check that in the predicted plan, each dependent starts
    at/after the dependency's end.
    """
    if not tasks_predicted:
        return 0.0

    expected_deps = {t["name"]: t.get("dependencies", []) for t in tasks_expected}
    pred_lookup = {t.get("name") or t.get("task"): t for t in tasks_predicted}

    total = 0
    correct = 0
    for name, deps in expected_deps.items():
        for d in deps:
            # count this dependency
            total += 1
            if name in pred_lookup and d in pred_lookup:
                try:
                    start = datetime.fromisoformat(pred_lookup[name]["start"])
                    dep_end = datetime.fromisoformat(pred_lookup[d]["end"])
                    if start >= dep_end:
                        correct += 1
                except Exception:
                    pass
    return (correct / total) if total else 0.0

def check_resource_balance(tasks_predicted, team_availability: dict) -> float:
    """
    Lower variance of (planned_hours / available_hours) => better (closer to 1).
    Convert to score 0..1 via 1/(1+variance).
    """
    if not tasks_predicted or not team_availability:
        return 0.0

    workload = {m: 0.0 for m in team_availability}
    for t in tasks_predicted:
        assignee = t.get("assignee")
        hours = float(t.get("hours", 0) or 0)
        if assignee in workload:
            workload[assignee] += hours

    ratios = []
    for m, avail in team_availability.items():
        if avail > 0:
            ratios.append(workload[m] / avail)

    if not ratios:
        return 0.0

    mean = sum(ratios) / len(ratios)
    var = sum((r - mean)**2 for r in ratios) / len(ratios)
    return 1.0 / (1.0 + var)

def check_time_utilization(tasks_predicted, team_availability: dict) -> float:
    """
    Planned hours / total available hours, capped at 1.0.
    """
    if not tasks_predicted or not team_availability:
        return 0.0
    planned = sum(float(t.get("hours", 0) or 0) for t in tasks_predicted)
    available = sum(team_availability.values())
    if available <= 0:
        return 0.0
    return min(planned / available, 1.0)

def check_effort_estimation(tasks_predicted, tasks_expected) -> float:
    """
    Compare predicted hours with expected duration_hours by matching on task name.
    Score = 1 - mean(relative error). 0 if no overlaps.
    """
    expected_map = {t["name"]: float(t.get("duration_hours", 0) or 0) for t in tasks_expected}
    errors = []
    for t in tasks_predicted:
        name = t.get("name") or t.get("task")
        if name in expected_map and expected_map[name] > 0:
            pred = float(t.get("hours", 0) or 0)
            exp = expected_map[name]
            errors.append(abs(pred - exp) / exp)

    if not errors:
        return 0.0
    mean_err = sum(errors) / len(errors)
    return max(0.0, 1.0 - mean_err)

def check_coverage(tasks_predicted, tasks_expected) -> float:
    """
    Fraction of expected tasks present by name.
    """
    if not tasks_predicted:
        return 0.0
    pred_names = {t.get("name") or t.get("task") for t in tasks_predicted}
    exp_names = {t["name"] for t in tasks_expected}
    if not exp_names:
        return 0.0
    return len(pred_names & exp_names) / len(exp_names)

def check_output_coherence(tasks_predicted) -> float:
    """
    Proportion of tasks that contain all required keys with valid-ish types.
    """
    if not tasks_predicted:
        return 0.0
    required = {"id", "name", "hours", "assignee", "start", "end"}
    ok = 0
    for t in tasks_predicted:
        if not isinstance(t, dict):
            continue
        if not required.issubset(t.keys()):
            continue
        # sanity checks
        try:
            _ = datetime.fromisoformat(t["start"])
            _ = datetime.fromisoformat(t["end"])
            _ = float(t["hours"])
            ok += 1
        except Exception:
            continue
    return ok / len(tasks_predicted)

def check_scalability(tasks_predicted, expected_count) -> float:
    if expected_count <= 0:
        return 0.0
    return min(1.0, len(tasks_predicted) / expected_count)

###############################
# Test Cases
###############################

TEST_CASES = [
    {
        "description": "Simple 3-task linear dependency",
        "tasks": [
            {"name": "Task A", "duration_hours": 8, "dependencies": [],          "assigned_to": "Alice"},
            {"name": "Task B", "duration_hours": 4, "dependencies": ["Task A"],  "assigned_to": "Bob"},
            {"name": "Task C", "duration_hours": 6, "dependencies": ["Task B"],  "assigned_to": "Charlie"},
        ]
    },
    {
        "description": "Parallel tasks with shared resources",
        "tasks": [
            {"name": "Design UI",           "duration_hours": 6,  "dependencies": [],                         "assigned_to": "Alice"},
            {"name": "Backend API",         "duration_hours": 12, "dependencies": [],                         "assigned_to": "Bob"},
            {"name": "Integration Testing", "duration_hours": 4,  "dependencies": ["Design UI", "Backend API"], "assigned_to": "Charlie"},
        ]
    },
    {
        "description": "Overbooked team member",
        "tasks": [
            {"name": "Task X", "duration_hours": 10, "dependencies": [],         "assigned_to": "Alice"},
            {"name": "Task Y", "duration_hours": 8,  "dependencies": ["Task X"], "assigned_to": "Alice"},
            {"name": "Task Z", "duration_hours": 6,  "dependencies": ["Task Y"], "assigned_to": "Bob"},
        ]
    },
    {
        "description": "Tasks without assigned member (model decides)",
        "tasks": [
            {"name": "Write Documentation",  "duration_hours": 6, "dependencies": []},
            {"name": "Code Review",          "duration_hours": 4, "dependencies": ["Write Documentation"]},
            {"name": "Deploy to Production", "duration_hours": 2, "dependencies": ["Code Review"]},
        ]
    },
    {
        "description": "Complex web with multiple dependencies",
        "tasks": [
            {"name": "Set up DB",            "duration_hours": 4, "dependencies": []},
            {"name": "Implement Auth",       "duration_hours": 6, "dependencies": ["Set up DB"]},
            {"name": "Frontend Layout",      "duration_hours": 5, "dependencies": []},
            {"name": "API Integration",      "duration_hours": 8, "dependencies": ["Implement Auth", "Frontend Layout"]},
            {"name": "End-to-End Testing",   "duration_hours": 6, "dependencies": ["API Integration"]},
        ]
    },
]

###############################
# Main
###############################

def main():
    results_file = "results_sprint.csv"
    fieldnames = [
        "test_case", "description", "valid_json", "raw_json",
        "schedule_feasibility", "dependency_accuracy", "resource_balance",
        "time_utilization", "effort_accuracy", "coverage",
        "output_coherence", "scalability",
        "time_total"
    ]

    team_availability = build_team_availability(TEAM_MEMBERS, SPRINT_DAYS)

    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, case in enumerate(TEST_CASES, start=1):
            desc = case["description"]
            tasks = case["tasks"]

            print(f"\n[INFO] Running test case {i}: {desc}")

            prompt = f"""
You are an Agile sprint planner.

Given:
- Sprint start: {SPRINT_START.isoformat()}
- Sprint length (days): {SPRINT_DAYS}
- Team availability (hours over sprint): {json.dumps(team_availability)}

Tasks (expected): {json.dumps(tasks, indent=2)}

Return ONLY a JSON array of task objects. Each object MUST include:
- "id" (string)
- "name" (string)
- "hours" (number)
- "assignee" (string)
- "start" (ISO 8601 datetime)
- "end"   (ISO 8601 datetime)

Constraints:
- Respect dependencies by starting a task only after all its dependencies end.
- Do not exceed each assignee's available hours over the sprint.
- Keep all start/end within the sprint window.
- Prefer balanced workload.

Respond with ONLY the JSON array. No prose.
""".strip()

            stdout, stderr, elapsed = run_ollama_live(prompt, timeout=1200)

            # Save full output (thoughts + JSON) for post-analysis
            thoughts_path = os.path.join(THOUGHTS_DIR, f"testcase_{i}.txt")
            with open(thoughts_path, "w", encoding="utf-8") as tf:
                tf.write(stdout)

            # Extract first JSON array
            tasks_predicted, raw_json = extract_json_array(stdout)
            valid_json = tasks_predicted is not None

            # Compute metrics only if we got valid JSON
            if valid_json:
                schedule_feasibility = check_schedule_feasibility(tasks_predicted, SPRINT_START, SPRINT_DAYS)
                dependency_accuracy = check_dependency_accuracy(tasks, tasks_predicted)
                resource_balance    = check_resource_balance(tasks_predicted, team_availability)
                time_utilization    = check_time_utilization(tasks_predicted, team_availability)
                effort_accuracy     = check_effort_estimation(tasks_predicted, tasks)
                coverage            = check_coverage(tasks_predicted, tasks)
                output_coherence    = check_output_coherence(tasks_predicted)
                scalability         = check_scalability(tasks_predicted, len(tasks))
            else:
                schedule_feasibility = 0.0
                dependency_accuracy  = 0.0
                resource_balance     = 0.0
                time_utilization     = 0.0
                effort_accuracy      = 0.0
                coverage             = 0.0
                output_coherence     = 0.0
                scalability          = 0.0

            # Write CSV row immediately after each test
            row = {
                "test_case": i,
                "description": desc,
                "valid_json": valid_json,
                "raw_json": raw_json or "",
                "schedule_feasibility": schedule_feasibility,
                "dependency_accuracy":  dependency_accuracy,
                "resource_balance":     resource_balance,
                "time_utilization":     time_utilization,
                "effort_accuracy":      effort_accuracy,
                "coverage":             coverage,
                "output_coherence":     output_coherence,
                "scalability":          scalability,
                "time_total": elapsed,
            }
            writer.writerow(row)
            f.flush()

            print(
                f"[RESULT] Feas={schedule_feasibility:.2f}, "
                f"Deps={dependency_accuracy:.2f}, "
                f"Balance={resource_balance:.2f}, "
                f"Util={time_utilization:.2f}, "
                f"Effort={effort_accuracy:.2f}, "
                f"Coverage={coverage:.2f}, "
                f"Coherence={output_coherence:.2f}, "
                f"Scalability={scalability:.2f}"
            )

if __name__ == "__main__":
    main()
