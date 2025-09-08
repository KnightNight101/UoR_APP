#!/usr/bin/env python3
"""
Simplified Sprint Planner benchmark for model evaluation.
- 5 test cases, simple tasks to guarantee model output.
- Keeps all evaluation metrics.
- Uses stdin to reliably send prompt to Ollama.
"""

import json
import time
import subprocess
import csv
from pathlib import Path
from typing import Dict, Any, Tuple

# --------------------------
# Config
# --------------------------
NUM_TESTS = 5
MODEL_TIMEOUT = 600  # seconds
RESULTS_DIR = Path(__file__).parent / "Test_Results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CSV_FILE = RESULTS_DIR / "simple_sprint_benchmark.csv"
SCHEDULES_DIR = RESULTS_DIR / "schedules"
SCHEDULES_DIR.mkdir(exist_ok=True)
MD_REPORT = RESULTS_DIR / "simple_sprint_report.md"

MODEL_NAME = "deepseek-r1:8b"
OLLAMA_PATH = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")

# --------------------------
# Utilities
# --------------------------
def run_ollama(prompt: str) -> Tuple[str, float, bool]:
    """Run Ollama with stdin input, live printing output."""
    start = time.time()
    try:
        proc = subprocess.Popen(
            [str(OLLAMA_PATH), "run", MODEL_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        stdout, stderr = proc.communicate(input=prompt, timeout=MODEL_TIMEOUT)
        elapsed = time.time() - start
        if proc.returncode != 0:
            print(f"[ERROR] Ollama returned {proc.returncode}: {stderr.strip()}")
            return stdout.strip(), elapsed, True
        return stdout.strip(), elapsed, False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Ollama timed out after {MODEL_TIMEOUT} seconds")
        proc.kill()
        return "", MODEL_TIMEOUT, True

# --------------------------
# Simplified test cases
# --------------------------
def generate_test_case(idx: int) -> Dict[str, Any]:
    team = {f"member_{i}": 8 for i in range(2 + idx % 2)}  # 2–3 members
    tasks = []
    for t in range(3 + idx % 3):  # 3–5 tasks
        tasks.append({
            "id": t,
            "title": f"Task_{t}",
            "do": 2,
            "verify": 1,
            "dependencies": [t-1] if t > 0 else [],
            "parent": None
        })
    return {"team": team, "tasks": tasks}

# --------------------------
# Baseline scheduler (unchanged)
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
    for tid in topo:
        t = by_id[tid]
        total_hours = t["do"] + t["verify"]
        earliest_start = max([assigned[d]["finish"] for d in t.get("dependencies", [])], default=0.0)
        best, best_finish = None, None
        for m in members.keys():
            start_candidate = max(next_free[m], earliest_start)
            finish_candidate = start_candidate + total_hours
            if best_finish is None or finish_candidate < best_finish:
                best = m
                best_finish = finish_candidate
        assigned[tid] = {
            "task_id": tid,
            "assignee": best,
            "start": max(next_free[best], earliest_start),
            "duration": total_hours,
            "finish": best_finish
        }
        next_free[best] = best_finish
    makespan = max(e["finish"] for e in assigned.values()) if assigned else 0.0
    return {"schedule": assigned, "makespan": makespan, "error": None}

# --------------------------
# Model parsing and repair
# --------------------------
def parse_model_schedule(output: str) -> Dict[int, Dict[str, Any]]:
    try:
        data = json.loads(output)
    except:
        return {}
    result = {}
    for item in data.get("sprint_backlog") or []:
        try:
            tid = int(item["task_id"])
            start = float(item["start"])
            dur = float(item["duration"])
            result[tid] = {
                "task_id": tid,
                "assignee": item["assignee"],
                "start": start,
                "duration": dur,
                "finish": start + dur
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
        earliest_start = max([repaired[d]["finish"] for d in t.get("dependencies", []) if d in repaired], default=0.0)
        assignee = task["assignee"] if task["assignee"] in members else list(members.keys())[0]
        start_time = max(earliest_start, next_free[assignee])
        repaired[tid] = {
            "task_id": tid,
            "assignee": assignee,
            "start": start_time,
            "duration": task["duration"],
            "finish": start_time + task["duration"]
        }
        next_free[assignee] = repaired[tid]["finish"]
    return repaired

# --------------------------
# Evaluation metrics
# --------------------------
def evaluate_model_schedule(case: Dict[str, Any], model_sched: Dict[int, Dict[str, Any]], baseline_makespan: float) -> Dict[str, Any]:
    tasks, members = case["tasks"], case["team"]
    model_makespan = max((e["finish"] for e in model_sched.values()), default=float("inf"))
    violations = 0
    for tid, entry in model_sched.items():
        deps = next((t["dependencies"] for t in tasks if t["id"] == tid), [])
        for d in deps:
            dep_finish = model_sched.get(d, {}).get("finish", 0)
            if entry["start"] < dep_finish - 1e-6:
                violations += 1
    assigned_hours = {m: 0.0 for m in members.keys()}
    for e in model_sched.values():
        a = e["assignee"]
        if a in assigned_hours:
            assigned_hours[a] += e["duration"]
    utils = []
    for m, daily in members.items():
        available = (model_makespan / 24.0) * daily if model_makespan != float("inf") else 1.0
        u = min(assigned_hours.get(m, 0) / available, 1.0) if available > 0 else 0.0
        utils.append(u)
    avg_util = sum(utils)/len(utils)*100 if utils else 0.0
    makespan_ratio = model_makespan / baseline_makespan if baseline_makespan > 0 else -1
    feasible = violations == 0 and all(u <= 100 for u in utils)
    return {
        "baseline_makespan": baseline_makespan,
        "model_makespan": model_makespan,
        "makespan_ratio": round(makespan_ratio, 3),
        "dependency_violations": violations,
        "task_coverage": round(len(model_sched)/len(tasks),3),
        "avg_member_utilization": round(avg_util,2),
        "feasible": feasible
    }

# --------------------------
# Main benchmark
# --------------------------
def main():
    headers = [
        "test_id","model","baseline_makespan","model_makespan","makespan_ratio",
        "dependency_violations","task_coverage","avg_member_utilization","feasible","time_s","source"
    ]
    if not CSV_FILE.exists():
        with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow(headers)

    for test_id in range(1, NUM_TESTS+1):
        print(f"\n[INFO] Test case {test_id}")
        case = generate_test_case(test_id)
        baseline = baseline_schedule(case)
        baseline_makespan = baseline["makespan"]
        prompt = json.dumps({
            "team": case["team"], "tasks": case["tasks"],
            "notes": "Respect dependencies, assign each task to a team member, combine do+verify."
        })
        output, elapsed, err = run_ollama(prompt)
        print(output)  # live terminal output

        model_sched = parse_model_schedule(output)
        source = "model"
        if not model_sched:
            print(f"[WARN] Invalid model output, falling back to baseline")
            model_sched = baseline["schedule"]
            elapsed = MODEL_TIMEOUT
            source = "baseline_fallback"
        else:
            model_sched = repair_model_schedule(case, model_sched)

        # save schedules
        (SCHEDULES_DIR/f"test_{test_id}_model_raw.txt").write_text(output, encoding="utf-8")
        (SCHEDULES_DIR/f"test_{test_id}_model.json").write_text(json.dumps(model_sched), encoding="utf-8")

        metrics = evaluate_model_schedule(case, model_sched, baseline_makespan)
        row = [
            test_id, MODEL_NAME, metrics["baseline_makespan"], metrics["model_makespan"], metrics["makespan_ratio"],
            metrics["dependency_violations"], metrics["task_coverage"], metrics["avg_member_utilization"],
            metrics["feasible"], round(elapsed,3), source
        ]
        with open(CSV_FILE,"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow(row)
        print(f"[INFO] Test {test_id} complete | Feasible: {metrics['feasible']} | Source: {source}")

if __name__=="__main__":
    main()
