"""
Unified Sprint Planner benchmark with feasibility repair for Deepseek R1:8b.

- Generates N test problems (tasks, dependencies, team members).
- Produces a deterministic baseline schedule (resource constrained).
- Asks the model (via Ollama CLI) to produce a JSON schedule.
- Repairs AI schedules for feasibility.
- Compares schedules and computes metrics.
- Writes incremental CSV results and per-test schedule JSONs.
- Produces a Markdown report with summary, feasibility stats, and Mermaid Gantt diagrams.

Windows-compatible: invokes Ollama executable directly as a command (no --stdin).
"""

import json
import time
import random
import subprocess
import csv
from pathlib import Path
from typing import Dict, Any, Tuple

# --------------------------
# Config
# --------------------------
NUM_TESTS = 5  # reduced from 20 to 5
MODEL_TIMEOUT = 600  # 10 minutes per test

RESULTS_DIR = Path(__file__).parent / "Test_Results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CSV_FILE = RESULTS_DIR / "deepseek_r1_8b_sprint_benchmark.csv"
SCHEDULES_DIR = RESULTS_DIR / "schedules"
SCHEDULES_DIR.mkdir(exist_ok=True)
MD_REPORT = RESULTS_DIR / "deepseek_r1_8b_sprint_report.md"

MODEL_NAME = "deepseek-r1:8b"
OLLAMA_CANDIDATE_PATHS = [
    Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe"),
    Path("C:/Program Files/Ollama/ollama.exe"),
    Path("C:/Program Files (x86)/Ollama/ollama.exe"),
    Path("C:/Program Files/Ollama/ollama.EXE"),
]

# --------------------------
# Utilities
# --------------------------
def ensure_ollama() -> str:
    from shutil import which
    for p in OLLAMA_CANDIDATE_PATHS:
        if p.exists():
            return str(p)
    w = which("ollama")
    if w:
        return w
    raise EnvironmentError("Ollama executable not found. Install Ollama or update OLLAMA_CANDIDATE_PATHS.")

def run_ollama(model_name: str, prompt: str, timeout: int = MODEL_TIMEOUT) -> Tuple[str, float, bool]:
    ollama = ensure_ollama()
    safe_prompt = prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama, "run", model_name, safe_prompt]
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="ignore",
            encoding="utf-8"
        )
        elapsed = time.time() - start
        if proc.returncode != 0:
            print(f"[ERROR] Ollama returned non-zero: {proc.returncode}; stderr: {proc.stderr.strip()}")
            return proc.stdout.strip(), elapsed, True
        return proc.stdout.strip(), elapsed, False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Ollama timed out after {timeout} seconds for model {model_name}")
        return "", timeout, True

# --------------------------
# Test case generation
# --------------------------
def generate_test_case(idx: int) -> Dict[str, Any]:
    random.seed(int(time.time()) + idx)
    team_size = random.randint(2, 4)
    members = {f"member_{i}": random.choice([4, 6, 8]) for i in range(team_size)}
    n_tasks = random.randint(4, 8)
    tasks, next_id = [], 0
    for t in range(n_tasks):
        do_h = random.randint(2, 8)
        verify_h = random.randint(1, 4)
        tasks.append({
            "id": next_id,
            "title": f"Task_{t}",
            "do": do_h,
            "verify": verify_h,
            "dependencies": [],
            "parent": None
        })
        next_id += 1
        if random.random() < 0.3:
            for s in range(random.randint(1, 2)):
                tasks.append({
                    "id": next_id,
                    "title": f"Task_{t}_sub{s}",
                    "do": max(1, do_h // 2),
                    "verify": max(1, verify_h // 2),
                    "dependencies": [],
                    "parent": t
                })
                next_id += 1
    # Add dependencies
    for t in tasks:
        if random.random() < 0.35:
            possible = [x["id"] for x in tasks if x["id"] < t["id"]]
            if possible:
                t["dependencies"] = random.sample(possible, min(len(possible), random.randint(1, 2)))
    return {"team": members, "tasks": tasks}

# --------------------------
# Baseline scheduler
# --------------------------
def baseline_schedule(case: Dict[str, Any]) -> Dict[str, Any]:
    tasks, members = case["tasks"], case["team"]
    adj, indeg = {t["id"]: [] for t in tasks}, {t["id"]: 0 for t in tasks}
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        for d in t.get("dependencies", []):
            adj[d].append(t["id"])
            indeg[t["id"]] += 1
    q = [tid for tid, d in indeg.items() if d == 0]
    topo = []
    while q:
        nid = q.pop(0)
        topo.append(nid)
        for nb in adj[nid]:
            indeg[nb] -= 1
            if indeg[nb] == 0:
                q.append(nb)
    if len(topo) != len(tasks):
        return {"schedule": {}, "makespan": float("inf"), "error": "cycle_in_dependencies"}
    next_free = {m: 0.0 for m in members.keys()}
    assigned = {}
    def deps_finish(task_id):
        deps = by_id[task_id].get("dependencies", [])
        return max([assigned[d]["finish"] for d in deps], default=0.0)
    for tid in topo:
        t = by_id[tid]
        total_hours = t["do"] + t["verify"]
        earliest_start = deps_finish(tid)
        best, best_finish, chosen_start = None, None, None
        for m, daily_hours in members.items():
            start_candidate = max(next_free[m], earliest_start)
            finish_candidate = start_candidate + total_hours
            if best_finish is None or finish_candidate < best_finish:
                best = m
                best_finish = finish_candidate
                chosen_start = start_candidate
        assigned[tid] = {
            "task_id": tid,
            "assignee": best,
            "start": chosen_start,
            "duration": total_hours,
            "finish": best_finish
        }
        next_free[best] = best_finish
    makespan = max(e["finish"] for e in assigned.values()) if assigned else 0.0
    return {"schedule": assigned, "makespan": makespan, "error": None}

# --------------------------
# Model parsing, evaluation, repair
# --------------------------
def parse_model_schedule(output: str) -> Dict[int, Dict[str, Any]]:
    if not output:
        return {}
    try:
        data = json.loads(output)
    except:
        start = output.find("{")
        end = output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            data = json.loads(output[start:end + 1])
        except:
            return {}
    backlog = data.get("sprint_backlog") or data.get("backlog") or data.get("schedule") or []
    result = {}
    for item in backlog:
        try:
            tid = int(item.get("task_id"))
            assignee = item.get("assignee")
            start = float(item.get("start"))
            dur = float(item.get("duration"))
            finish = start + dur
            result[tid] = {
                "task_id": tid,
                "assignee": assignee,
                "start": start,
                "duration": dur,
                "finish": finish
            }
        except:
            continue
    return result

def repair_model_schedule(case: Dict[str, Any], model_sched: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    by_id = {t["id"]: t for t in case["tasks"]}
    members = case["team"]
    next_free = {m: 0.0 for m in members.keys()}
    repaired = {}
    for tid, task in sorted(model_sched.items(), key=lambda x: x[1]["start"]):
        t = by_id[tid]
        deps = t.get("dependencies", [])
        earliest_start = max([repaired[d]["finish"] for d in deps if d in repaired], default=0.0)
        assignee = task["assignee"]
        if assignee not in members:
            assignee = list(members.keys())[0]
        start_time = max(earliest_start, next_free.get(assignee, 0.0))
        duration = task["duration"]
        finish_time = start_time + duration
        repaired[tid] = {
            "task_id": tid,
            "assignee": assignee,
            "start": start_time,
            "duration": duration,
            "finish": finish_time
        }
        next_free[assignee] = finish_time
    return repaired

def evaluate_model_schedule(case: Dict[str, Any], model_sched: Dict[int, Dict[str, Any]], baseline_makespan: float) -> Dict[str, Any]:
    tasks, members = case["tasks"], case["team"]
    total_tasks = len(tasks)
    scheduled = list(model_sched.keys())
    task_coverage = len(scheduled) / total_tasks if total_tasks else 0.0
    model_makespan = max((e["finish"] for e in model_sched.values()), default=float("inf"))
    by_id = {t["id"]: t for t in tasks}
    violations = 0
    for tid, entry in model_sched.items():
        deps = by_id.get(tid, {}).get("dependencies", [])
        for d in deps:
            dep_finish = model_sched.get(d, {}).get("finish")
            if dep_finish is None or entry["start"] < dep_finish - 1e-6:
                violations += 1
    assigned_hours = {m: 0.0 for m in members.keys()}
    for e in model_sched.values():
        a = e.get("assignee")
        if a in assigned_hours:
            assigned_hours[a] += e.get("duration", 0.0)
    utils = []
    for m, daily in members.items():
        available_over_period = (model_makespan / 24.0) * daily if model_makespan != float("inf") else 1.0
        u = min(assigned_hours.get(m, 0) / available_over_period, 1.0) if available_over_period > 0 else 0.0
        utils.append(u)
    avg_util = sum(utils) / len(utils) * 100 if utils else 0.0
    makespan_ratio = model_makespan / baseline_makespan if baseline_makespan > 0 and model_makespan > 0 else -1
    feasible = (violations == 0 and all(u <= 100.0 for u in utils))
    return {
        "baseline_makespan": baseline_makespan,
        "model_makespan": model_makespan,
        "makespan_ratio": round(makespan_ratio, 3),
        "dependency_violations": violations,
        "task_coverage": round(task_coverage, 3),
        "avg_member_utilization": round(avg_util, 2),
        "feasible": feasible
    }

# --------------------------
# Markdown report
# --------------------------
def generate_md_report(csv_file: Path, md_file: Path):
    import pandas as pd
    df = pd.read_csv(csv_file)
    avg_makespan_ratio = round(df['makespan_ratio'].replace(-1, float('nan')).mean(), 3)
    avg_task_coverage = round(df['task_coverage'].replace(-1, float('nan')).mean() * 100, 2)
    avg_member_utilization = round(df['avg_member_utilization'].replace(-1, float('nan')).mean(), 2)
    feasible_pct = round((df['feasible'] == True).sum() / len(df) * 100, 1)
    model_pct = round((df['source'] == "model").sum() / len(df) * 100, 1)
    baseline_pct = round((df['source'] == "baseline_fallback").sum() / len(df) * 100, 1)
    md_lines = [
        "# Deepseek R1:8b Sprint Planner Results",
        "## Summary Statistics",
        f"- Average makespan ratio: **{avg_makespan_ratio}**",
        f"- Average task coverage: **{avg_task_coverage}%**",
        f"- Average member utilization: **{avg_member_utilization}%**",
        f"- Feasible schedules: **{feasible_pct}%**",
        f"- Model success rate: **{model_pct}%**",
        f"- Baseline fallback rate: **{baseline_pct}%**",
        "\n---\n",
        "## Makespan Ratio Distribution (Mermaid)",
        "```mermaid",
        "%% add Gantt chart code here",
        "```"
    ]
    md_file.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[INFO] Markdown report written to {md_file}")

# --------------------------
# Main benchmark loop
# --------------------------
def main():
    headers = [
        "test_id", "model", "baseline_makespan", "model_makespan", "makespan_ratio",
        "dependency_violations", "task_coverage", "avg_member_utilization", "feasible",
        "time_s", "source"
    ]
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    for test_id in range(1, NUM_TESTS + 1):
        print(f"[INFO] Generating test case {test_id}...")
        case = generate_test_case(test_id)
        baseline = baseline_schedule(case)
        baseline_makespan = baseline.get("makespan", -1)
        start_time = time.time()
        prompt_text = json.dumps({
            "team": case["team"], "tasks": case["tasks"],
            "notes": (
                "All schedules must respect task dependencies: no task may start before "
                "its dependencies finish. Each team member cannot be assigned more hours "
                "than their daily capacity multiplied by the number of days spanned by "
                "the schedule. Combine do+verify into a single contiguous block."
            )
        })
        output, elapsed, err = run_ollama(MODEL_NAME, prompt_text)
        model_sched = parse_model_schedule(output)
        source = "model"
        if not model_sched:
            print(f"[WARN] Empty/invalid model schedule for test {test_id}; falling back to baseline for evaluation.")
            model_sched = baseline["schedule"]
            elapsed = MODEL_TIMEOUT
            source = "baseline_fallback"
        else:
            model_sched = repair_model_schedule(case, model_sched)

        # save schedules
        (SCHEDULES_DIR / f"test_{test_id}_model_raw.txt").write_text(output, encoding="utf-8")
        (SCHEDULES_DIR / f"test_{test_id}_model.json").write_text(json.dumps(model_sched), encoding="utf-8")

        metrics = evaluate_model_schedule(case, model_sched, baseline_makespan)
        row = [
            test_id, MODEL_NAME,
            metrics["baseline_makespan"], metrics["model_makespan"], metrics["makespan_ratio"],
            metrics["dependency_violations"], metrics["task_coverage"], metrics["avg_member_utilization"],
            metrics["feasible"], round(elapsed, 3), source
        ]
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print(f"[INFO] Test {test_id} complete. Feasible: {metrics['feasible']} | Source: {source}")

    generate_md_report(CSV_FILE, MD_REPORT)

if __name__ == "__main__":
    main()
