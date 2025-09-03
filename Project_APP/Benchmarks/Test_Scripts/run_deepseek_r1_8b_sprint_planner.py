#!/usr/bin/env python3
"""
Unified Sprint Planner benchmark for Deepseek R1:8b with Windows-safe Unicode handling.

- Generates N test problems (tasks, dependencies, team members).
- Produces a deterministic baseline schedule.
- Queries the model via Ollama CLI with robust Unicode handling.
- Compares schedules and computes metrics.
- Writes incremental CSV results and per-test schedule JSONs.
- Produces a Markdown report with summary and Mermaid Gantt diagrams.
"""

import json
import time
import random
import subprocess
import csv
from pathlib import Path
from typing import List, Dict, Tuple, Any

# --------------------------
# Config
# --------------------------
NUM_TESTS = 20
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
]

MODEL_TIMEOUT = 300  # 5 minutes per test

# --------------------------
# Utilities
# --------------------------
def ensure_ollama() -> str:
    """Find Ollama executable on common Windows paths."""
    for p in OLLAMA_CANDIDATE_PATHS:
        if p.exists():
            return str(p)
    from shutil import which
    w = which("ollama")
    if w:
        return w
    raise EnvironmentError("Ollama executable not found. Install Ollama or update paths.")

def run_ollama(model_name: str, prompt: str, timeout: int = MODEL_TIMEOUT) -> Tuple[str, float, bool]:
    """
    Call Ollama run <model> <prompt> and return (stdout, elapsed_seconds, had_error_bool).
    Robust to Unicode errors on Windows.
    """
    ollama = ensure_ollama()
    safe_prompt = prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama, "run", model_name, safe_prompt]
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        elapsed = time.time() - start
        if proc.returncode != 0:
            print(f"[ERROR] Ollama returned {proc.returncode}; stderr: {proc.stderr.strip()}")
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
    # team members
    team_size = random.randint(2, 4)
    members = {f"member_{i}": random.choice([4,6,8]) for i in range(team_size)}
    # tasks + subtasks
    n_tasks = random.randint(4, 8)
    tasks = []
    next_id = 0
    for t in range(n_tasks):
        do_h = random.randint(2,8)
        verify_h = random.randint(1,4)
        tasks.append({"id": next_id, "title": f"Task_{t}", "do": do_h, "verify": verify_h, "dependencies": [], "parent": None})
        next_id += 1
        if random.random() < 0.3:
            num_sub = random.randint(1,2)
            for s in range(num_sub):
                do_s = max(1, do_h // (num_sub + 1))
                verify_s = max(1, verify_h // (num_sub + 1))
                tasks.append({"id": next_id, "title": f"Task_{t}_sub{s}", "do": do_s, "verify": verify_s, "dependencies": [], "parent": t})
                next_id += 1
    # dependencies DAG
    for t in tasks:
        if random.random() < 0.35:
            possible = [x["id"] for x in tasks if x["id"] < t["id"]]
            k = min(len(possible), random.randint(1,2))
            if k>0:
                t["dependencies"] = random.sample(possible, k)
    return {"team": members, "tasks": tasks}

# --------------------------
# Baseline scheduler
# --------------------------
def baseline_schedule(case: Dict[str, Any]) -> Dict[str, Any]:
    tasks = case["tasks"]
    members = case["team"]
    adj = {t["id"]: [] for t in tasks}
    indeg = {t["id"]: 0 for t in tasks}
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        for d in t.get("dependencies", []):
            adj[d].append(t["id"])
            indeg[t["id"]] += 1
    # Topo sort
    q = [tid for tid, d in indeg.items() if d==0]
    topo=[]
    while q:
        nid = q.pop(0)
        topo.append(nid)
        for nb in adj[nid]:
            indeg[nb]-=1
            if indeg[nb]==0:
                q.append(nb)
    if len(topo)!=len(tasks):
        return {"schedule": {}, "makespan": float("inf"), "error": "cycle_in_dependencies"}
    next_free = {m:0.0 for m in members.keys()}
    assigned = {}
    def deps_finish(tid):
        deps = by_id[tid].get("dependencies",[])
        if not deps: return 0.0
        return max(assigned[d]["finish"] for d in deps if d in assigned)
    for tid in topo:
        t = by_id[tid]
        total_hours = float(t["do"] + t["verify"])
        earliest_start = deps_finish(tid)
        best=None
        best_finish=None
        for m, daily_hours in members.items():
            start_candidate = max(next_free[m], earliest_start)
            finish_candidate = start_candidate + total_hours
            if best_finish is None or finish_candidate < best_finish:
                best= m
                best_finish= finish_candidate
                chosen_start = start_candidate
        assigned[tid]={"task_id": tid, "assignee": best, "start": chosen_start, "duration": total_hours, "finish": best_finish}
        next_free[best]=best_finish
    makespan=max(e["finish"] for e in assigned.values()) if assigned else 0.0
    return {"schedule": assigned, "makespan": makespan, "error": None}

# --------------------------
# Model parsing & evaluation
# --------------------------
def parse_model_schedule(output: str) -> Dict[int, Dict[str, Any]]:
    if not output: return {}
    try:
        data=json.loads(output)
    except Exception:
        start=output.find("{")
        end=output.rfind("}")
        if start==-1 or end==-1 or end<=start: return {}
        try: data=json.loads(output[start:end+1])
        except Exception: return {}
    backlog=data.get("sprint_backlog") or data.get("backlog") or data.get("schedule") or []
    result={}
    for item in backlog:
        try:
            tid=int(item.get("task_id"))
            a=item.get("assignee")
            start=float(item.get("start"))
            dur=float(item.get("duration"))
            result[tid]={"task_id":tid,"assignee":a,"start":start,"duration":dur,"finish":start+dur}
        except Exception:
            continue
    return result

def evaluate_model_schedule(case: Dict[str, Any], model_sched: Dict[int, Dict[str, Any]], baseline_makespan: float) -> Dict[str, Any]:
    tasks=case["tasks"]
    members=case["team"]
    total_tasks=len(tasks)
    scheduled=list(model_sched.keys())
    task_coverage=len(scheduled)/total_tasks if total_tasks else 0.0
    model_makespan=max(e["finish"] for e in model_sched.values()) if model_sched else float("inf")
    by_id={t["id"]: t for t in tasks}
    violations=0
    for tid, entry in model_sched.items():
        deps=by_id.get(tid, {}).get("dependencies",[])
        for d in deps:
            dep_finish=model_sched.get(d, {}).get("finish")
            if dep_finish is None or entry["start"]<dep_finish-1e-6: violations+=1
    assigned_hours={m:0.0 for m in members.keys()}
    for e in model_sched.values():
        a=e.get("assignee")
        if a in assigned_hours: assigned_hours[a]+=e.get("duration",0.0)
    utils=[]
    for m,daily in members.items():
        if model_makespan==float("inf") or model_makespan<=0: utils.append(0.0); continue
        available=(model_makespan/24.0)*daily
        util=(assigned_hours.get(m,0.0)/available) if available>0 else 0.0
        utils.append(min(util,1.0))
    avg_member_utilization=(sum(utils)/len(utils))*100.0 if utils else 0.0
    feasible=True
    for m,hours in assigned_hours.items():
        available=(model_makespan/24.0)*members[m] if model_makespan!=float("inf") else 0.0
        if available>0 and hours>available*1.05: feasible=False
    if violations>0: feasible=False
    makespan_ratio=model_makespan/baseline_makespan if baseline_makespan and baseline_makespan!=float("inf") else float("inf")
    return {
        "baseline_makespan": baseline_makespan,
        "model_makespan": model_makespan,
        "makespan_ratio": makespan_ratio,
        "dependency_violations": violations,
        "task_coverage": task_coverage,
        "avg_member_utilization": round(avg_member_utilization,3),
        "feasible": feasible
    }

# --------------------------
# CSV helpers
# --------------------------
CSV_FIELDS=[
    "test_id","model","baseline_makespan","model_makespan","makespan_ratio",
    "dependency_violations","task_coverage","avg_member_utilization","feasible",
    "time_s"
]

def write_csv_row(path: Path, row: Dict[str, Any]):
    file_exists = path.exists()
    with open(path,"a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists: writer.writeheader()
        writer.writerow(row)

# --------------------------
# Markdown report
# --------------------------
def generate_markdown_report(results_csv: Path, schedules_dir: Path, md_path: Path, top_k:int=3):
    import pandas as pd
    df=pd.read_csv(results_csv)
    df_sorted=df.sort_values("makespan_ratio",ascending=False)
    top_worst=df_sorted.head(top_k)
    top_best=df_sorted.tail(top_k).sort_values("makespan_ratio")
    md_lines=[]
    md_lines.append("# Deepseek R1:8b Sprint Planner Benchmark Report\n")
    md_lines.append("## Summary table (all tests)\n")
    md_lines.append(df.to_markdown(index=False))
    md_lines.append("\n---\n")
    md_lines.append(f"## Top {top_k} worst-performing tests (highest makespan_ratio)\n")
    md_lines.append(top_worst.to_markdown(index=False))
    md_lines.append("\n---\n")
    md_lines.append(f"## Top {top_k} best-performing tests (lowest makespan_ratio)\n")
    md_lines.append(top_best.to_markdown(index=False))
    md_lines.append("\n---\n")
    def mermaid_gantt_from_schedule(schedule: Dict[int, Dict[str, Any]], title:str)->str:
        lines=["```mermaid","gantt",f"    title {title}","    dateFormat  HH"]
        by_assignee={}
        for tid,e in schedule.items():
            a=e.get("assignee","unassigned")
            by_assignee.setdefault(a,[]).append(e)
        idx=0
        for assignee,tasks in by_assignee.items():
            lines.append(f"    section {assignee}")
            for e in tasks:
                start=int(round(e["start"]))
                dur=max(1,int(round(e["duration"])))
                label=f"Task_{e['task_id']}"
                lines.append(f"    {label} :{label}{idx}, {start}h, {dur}h")
                idx+=1
        lines.append("```")
        return "\n".join(lines)
    md_lines.append("## Sample Gantt comparisons (baseline vs model)\n")
    selected_tests=pd.concat([top_worst,top_best]).drop_duplicates(subset=["test_id"])
    for _,row in selected_tests.iterrows():
        tid=int(row["test_id"])
        md_lines.append(f"### Test {tid}\n")
        baseline_file=schedules_dir/f"test_{tid}_baseline.json"
        model_file=schedules_dir/f"test_{tid}_model.json"
        baseline_sched=json.loads(baseline_file.read_text(encoding="utf-8")) if baseline_file.exists() else {}
        model_sched=json.loads(model_file.read_text(encoding="utf-8")) if model_file.exists() else {}
        md_lines.append("#### Baseline Schedule\n")
        md_lines.append(mermaid_gantt_from_schedule(baseline_sched,f"Test {tid} - Baseline"))
        md_lines.append("\n#### Model Schedule\n")
        md_lines.append(mermaid_gantt_from_schedule(model_sched,f"Test {tid} - Model"))
        md_lines.append("\n---\n")
    md_path.write_text("\n\n".join(md_lines),encoding="utf-8")
    print(f"Markdown report written: {md_path}")

# --------------------------
# Main loop
# --------------------------
def main():
    print("Sprint Planner unified benchmark starting...")
    for i in range(NUM_TESTS):
        test_id=i+1
        case=generate_test_case(i)
        baseline=baseline_schedule(case)
        baseline_sched=baseline.get("schedule",{})
        baseline_makespan=baseline.get("makespan",float("inf"))
        baseline_serial={tid:{"task_id":tid,"assignee":v["assignee"],"start":v["start"],"duration":v["duration"],"finish":v["finish"]} for tid,v in baseline_sched.items()}
        (SCHEDULES_DIR/f"test_{test_id}_baseline.json").write_text(json.dumps(baseline_serial),encoding="utf-8")

        prompt_obj={
            "instruction":"Create a sprint plan for the following tasks. Respect dependencies. Assign tasks to team members and provide start time (hours from t=0) and duration (hours). Use a 24-hour day and assume members can work up to their daily available hours per day.",
            "team":case["team"],
            "tasks":case["tasks"],
            "output_schema":{"sprint_backlog":[{"task_id":"int","assignee":"str","start":"float","duration":"float"}]},
            "notes":"Start times should respect dependencies. Combine do+verify into a single contiguous block.",
            "example":{"sprint_backlog":[{"task_id":0,"assignee":"member_0","start":0.0,"duration":8.0}]}
        }
        prompt_text=json.dumps(prompt_obj,indent=2)
        print(f"[INFO] Test {test_id}: querying model...")
        output, elapsed, err = run_ollama(MODEL_NAME,prompt_text,timeout=MODEL_TIMEOUT)
        model_sched=parse_model_schedule(output)
        (SCHEDULES_DIR/f"test_{test_id}_model_raw.txt").write_text(output,encoding="utf-8")
        (SCHEDULES_DIR/f"test_{test_id}_model.json").write_text(json.dumps(model_sched),encoding="utf-8")

        metrics=evaluate_model_schedule(case,model_sched,baseline_makespan)
        row={
            "test_id": test_id,
            "model": MODEL_NAME,
            "baseline_makespan": round(metrics["baseline_makespan"],3) if metrics["baseline_makespan"]!=float("inf") else -1,
            "model_makespan": round(metrics["model_makespan"],3) if metrics["model_makespan"]!=float("inf") else -1,
            "makespan_ratio": round(metrics["makespan_ratio"],3) if metrics["makespan_ratio"]!=float("inf") else -1,
            "dependency_violations": metrics["dependency_violations"],
            "task_coverage": round(metrics["task_coverage"],3),
            "avg_member_utilization": metrics["avg_member_utilization"],
            "feasible": bool(metrics["feasible"]),
            "time_s": round(elapsed,3)
        }
        write_csv_row(CSV_FILE,row)
        print(f"[INFO] Test {test_id} done. baseline_makespan={row['baseline_makespan']}, model_makespan={row['model_makespan']}, violations={row['dependency_violations']}, coverage={row['task_coverage']}, time_s={row['time_s']}")

    try:
        generate_markdown_report(CSV_FILE,SCHEDULES_DIR,MD_REPORT,top_k=3)
    except Exception as e:
        print(f"[ERROR] Failed to generate markdown report: {e}")

if __name__=="__main__":
    main()
