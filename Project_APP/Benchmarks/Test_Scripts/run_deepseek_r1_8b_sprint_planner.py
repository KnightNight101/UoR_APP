#!/usr/bin/env python3
"""
Unified Sprint Planner benchmark with feasibility repair for Deepseek R1:8b.

- Generates N test problems (tasks, dependencies, team members).
- Produces a deterministic baseline schedule (resource constrained).
- Asks the model (via Ollama CLI) to produce a JSON schedule (multi-sprint capable).
- Parses/repairs AI schedules for feasibility (dependencies, capacity).
- Compares schedules and computes metrics.
- Writes incremental CSV results and per-test schedule JSONs.
- Produces a Markdown report with summary stats.

Windows-compatible: invokes Ollama executable directly as a command (no --stdin).
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
    Path("C:/Program Files/Ollama/ollama.EXE"),
]

MODEL_TIMEOUT = 300  # seconds

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
    """
    Run Ollama with the full prompt as one argument, using UTF-8 decoding and ignoring
    undecodable bytes to avoid Windows cp1252 crashes. Returns (stdout, elapsed_s, error_flag).
    """
    ollama = ensure_ollama()
    # Pass the prompt directly as one argument; Ollama CLI accepts: ollama run <model> "<prompt>"
    cmd = [ollama, "run", model_name, prompt]
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="ignore",  # prevent UnicodeDecodeError on Windows
        )
        elapsed = time.time() - start
        if proc.returncode != 0:
            print(f"[ERROR] Ollama returned non-zero: {proc.returncode}; stderr: {proc.stderr.strip()}")
            return proc.stdout.strip(), elapsed, True
        return proc.stdout.strip(), elapsed, False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Ollama timed out after {timeout} seconds for model {model_name}")
        return "", timeout, True

def extract_json_block(text: str) -> str:
    """
    Best-effort extraction of a JSON object from model output.
    Supports ```json fenced blocks and plain trailing explanations.
    Returns the JSON substring or "" if none found.
    """
    if not text:
        return ""
    # Prefer fenced ```json blocks
    fence_start = text.find("```json")
    if fence_start != -1:
        fence_start = fence_start + len("```json")
        fence_end = text.find("```", fence_start)
        if fence_end != -1:
            return text[fence_start:fence_end].strip()
    # Otherwise take the largest {...} slice
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()
    return ""

# --------------------------
# Test case generation
# --------------------------
def generate_test_case(idx: int) -> Dict[str, Any]:
    # Make deterministic per test id for reproducibility
    random.seed(10_000 + idx)
    team_size = random.randint(2, 4)
    members = {f"member_{i}": random.choice([4, 6, 8]) for i in range(team_size)}  # hours/day capacity
    n_tasks = random.randint(5, 9)

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
        # Optional subtasks
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
# Baseline scheduler (greedy RCPSP with topo order)
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

    next_free = {m: 0.0 for m in members.keys()}  # in hours
    assigned = {}

    def deps_finish(task_id):
        deps = by_id[task_id].get("dependencies", [])
        return max([assigned[d]["finish"] for d in deps if d in assigned], default=0.0)

    for tid in topo:
        t = by_id[tid]
        total_hours = t["do"] + t["verify"]
        earliest_start = deps_finish(tid)

        best, best_finish, chosen_start = None, None, None
        for m in members.keys():
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
# Parsing/repair
# --------------------------
def parse_model_schedule(output: str, case: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """
    Parse model output supporting:
      - new multi-sprint schema: {"sprints":[{tasks:[{id, assigneeId?, duration?, ...}], teamMembers:[{id,name}]}]}
      - old backlog-style: {"sprint_backlog" | "backlog" | "schedule":[{task_id, assignee, start, duration}]}

    Returns internal normalized dict: {task_id: {task_id, assignee, start, duration, finish}}
    where start is in hours; if not provided, we will set start=0 and let repair re-place it.
    """
    txt = extract_json_block(output) or output
    if not txt:
        return {}

    try:
        data = json.loads(txt)
    except Exception:
        # last resort: try to slice braces
        start = txt.find("{")
        end = txt.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            data = json.loads(txt[start:end+1])
        except Exception:
            return {}

    # If multi-sprint schema present
    result: Dict[int, Dict[str, Any]] = {}
    by_id = {t["id"]: t for t in case["tasks"]}
    case_members = list(case["team"].keys())  # enforce known members
    member_fallback = case_members[0] if case_members else "member_0"

    if isinstance(data, dict) and "sprints" in data and isinstance(data["sprints"], list):
        # Build a per-sprint member map (id->name), but coerce to known case members
        for sp in data["sprints"]:
            tasks = sp.get("tasks", []) or []
            team_members = sp.get("teamMembers", []) or []
            id_to_name = {}
            for tm in team_members:
                try:
                    # Prefer exact case member names; otherwise map to first known member
                    nm = tm.get("name") or tm.get("id") or ""
                    if nm in case["team"]:
                        id_to_name[tm.get("id")] = nm
                    else:
                        # Keep id mapping but will coerce later
                        id_to_name[tm.get("id")] = str(nm)
                except Exception:
                    pass

            for item in tasks:
                # Only accept tasks that exist in the generated case
                tid_raw = item.get("id")
                try:
                    tid = int(tid_raw) if isinstance(tid_raw, (int, str)) and str(tid_raw).isdigit() else None
                except Exception:
                    tid = None
                if tid is None or tid not in by_id:
                    continue

                # Duration — prefer model's provided, else compute from case
                dur = item.get("duration")
                if not isinstance(dur, (int, float)) or dur <= 0:
                    dur = by_id[tid]["do"] + by_id[tid]["verify"]

                # Assignee — prefer assigneeId/name mapped to known members
                assignee = None
                if "assigneeId" in item:
                    assignee = id_to_name.get(item["assigneeId"])
                if not assignee:
                    nm = item.get("assignee") or item.get("assigneeName")
                    if isinstance(nm, str) and nm in case["team"]:
                        assignee = nm
                if not assignee or assignee not in case["team"]:
                    assignee = member_fallback

                # Start — optional; we will repair anyway
                start_v = item.get("start")
                start = float(start_v) if isinstance(start_v, (int, float, str)) and str(start_v).replace(".", "", 1).isdigit() else 0.0
                finish = start + float(dur)

                result[tid] = {
                    "task_id": tid,
                    "assignee": assignee,
                    "start": float(start),
                    "duration": float(dur),
                    "finish": float(finish)
                }

        return result

    # Fallback to old backlog-like schema
    backlog = data.get("sprint_backlog") or data.get("backlog") or data.get("schedule") or []
    if isinstance(backlog, list):
        for item in backlog:
            try:
                tid = int(item.get("task_id"))
                if tid not in by_id:
                    continue
                assignee = item.get("assignee") or member_fallback
                if assignee not in case["team"]:
                    assignee = member_fallback
                dur = float(item.get("duration") or (by_id[tid]["do"] + by_id[tid]["verify"]))
                start = float(item.get("start") or 0.0)
                result[tid] = {
                    "task_id": tid,
                    "assignee": assignee,
                    "start": start,
                    "duration": dur,
                    "finish": start + dur
                }
            except Exception:
                continue

    return result

def repair_model_schedule(case: Dict[str, Any], model_sched: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Feasibility repair:
      - Topological order on case graph
      - Respect dependencies
      - Respect single-resource usage per member (no overlap)
      - Keep model's chosen assignee when possible, else assign least-loaded member
      - Duration = case (do+verify) if missing/invalid
    """
    tasks = case["tasks"]
    members = case["team"]
    by_id = {t["id"]: t for t in tasks}

    # Build topo order
    adj, indeg = {t["id"]: [] for t in tasks}, {t["id"]: 0 for t in tasks}
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
        # cycle: return what we can from model (won't be feasible anyway)
        return model_sched

    # Initialize availability and build repaired
    next_free = {m: 0.0 for m in members.keys()}
    repaired: Dict[int, Dict[str, Any]] = {}

    def deps_finish(task_id):
        deps = by_id[task_id].get("dependencies", [])
        # use repaired if present, else model_sched if dependency wasn't in output yet
        times = []
        for d in deps:
            if d in repaired:
                times.append(repaired[d]["finish"])
            elif d in model_sched:
                times.append(model_sched[d]["finish"])
        return max(times) if times else 0.0

    # Pre-compute member load to pick least-loaded when assignee missing
    def least_loaded_member() -> str:
        return min(next_free.items(), key=lambda kv: kv[1])[0]

    for tid in topo:
        base = by_id[tid]
        total_hours = float(base["do"] + base["verify"])
        src = model_sched.get(tid, {})
        chosen_assignee = src.get("assignee") if src.get("assignee") in members else least_loaded_member()

        earliest = deps_finish(tid)
        start_candidate = max(next_free[chosen_assignee], earliest)
        finish_candidate = start_candidate + total_hours

        repaired[tid] = {
            "task_id": tid,
            "assignee": chosen_assignee,
            "start": start_candidate,
            "duration": total_hours,
            "finish": finish_candidate
        }
        next_free[chosen_assignee] = finish_candidate

    return repaired

# --------------------------
# Evaluation
# --------------------------
def evaluate_model_schedule(case: Dict[str, Any], model_sched: Dict[int, Dict[str, Any]], baseline_makespan: float) -> Dict[str, Any]:
    tasks, members = case["tasks"], case["team"]
    total_tasks = len(tasks)
    scheduled = list(model_sched.keys())
    task_coverage = len(scheduled) / total_tasks if total_tasks else 0.0

    model_makespan = max((e["finish"] for e in model_sched.values()), default=0.0)
    if model_makespan <= 0:
        model_makespan = 0.0

    by_id = {t["id"]: t for t in tasks}
    violations = 0
    for tid, entry in model_sched.items():
        deps = by_id.get(tid, {}).get("dependencies", [])
        for d in deps:
            dep_finish = model_sched.get(d, {}).get("finish")
            if dep_finish is None:
                violations += 1
            elif entry["start"] < dep_finish - 1e-6:
                violations += 1

    # Utilization (approx): capacity over the period implied by makespan
    assigned_hours = {m: 0.0 for m in members.keys()}
    for e in model_sched.values():
        a = e.get("assignee")
        if a in assigned_hours:
            assigned_hours[a] += e.get("duration", 0.0)

    utils = []
    if model_makespan > 0:
        for m, daily in members.items():
            available_over_period = (model_makespan / 24.0) * daily
            u = min(assigned_hours.get(m, 0.0) / available_over_period, 1.0) if available_over_period > 0 else 0.0
            utils.append(u)
        avg_util = (sum(utils) / len(utils) * 100.0) if utils else 0.0
    else:
        avg_util = 0.0

    makespan_ratio = (model_makespan / baseline_makespan) if (baseline_makespan > 0 and model_makespan > 0) else -1
    feasible = (violations == 0 and (all(u <= 1.0 for u in utils) if utils else False))

    return {
        "baseline_makespan": round(baseline_makespan, 3) if baseline_makespan != float("inf") else -1,
        "model_makespan": round(model_makespan, 3) if model_makespan != float("inf") else -1,
        "makespan_ratio": round(makespan_ratio, 3) if makespan_ratio != -1 else -1,
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
    md_lines = [
        "# Deepseek R1:8b Sprint Planner Results",
        "## Summary Statistics",
        f"- Average makespan ratio: **{avg_makespan_ratio}**",
        f"- Average task coverage: **{avg_task_coverage}%**",
        f"- Average member utilization: **{avg_member_utilization}%**",
        f"- Feasible schedules: **{feasible_pct}%**",
        "\n---\n",
        "## Makespan Ratio Distribution (Mermaid)",
        "```mermaid",
        "%% add Gantt chart code here",
        "```"
    ]
    md_file.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[INFO] Markdown report written to {md_file}")

# --------------------------
# Prompt builder (strict, multi-sprint, schema-locked)
# --------------------------
def build_prompt(case: Dict[str, Any]) -> str:
    """
    Force the model to:
      - Use EXACT task IDs and durations (do+verify)
      - Use ONLY provided team member keys as assignees
      - Return STRICT JSON with a 'sprints' array
      - Provide at least 2 sprints total
    We do NOT require start times; the repair phase will schedule feasibly.
    """
    team = case["team"]
    tasks = case["tasks"]
    members_list = list(team.keys())
    # Precompute canonical durations we expect the model to use
    task_brief = [
        {
            "id": t["id"],
            "title": t["title"],
            "duration_hours": t["do"] + t["verify"],
            "dependencies": t.get("dependencies", []),
        }
        for t in tasks
    ]
    # Compose strict instruction
    prompt = (
        "Return ONLY valid JSON (no markdown, no commentary). "
        "Produce a multi-sprint agile plan using this schema:\n"
        "{\n"
        '  "sprints": [\n'
        "    {\n"
        '      "id": "SPRINT-1",\n'
        '      "startDate": "2025-01-01",\n'
        '      "endDate": "2025-01-14",\n'
        '      "description": "Auto-planned sprint.",\n'
        '      "teamMembers": [ { "id": 1, "name": "'
        + members_list[0]
        + '" }'
        + (
            "".join(
                f', {{ "id": {i+1}, "name": "{members_list[i]}" }}'
                for i in range(1, len(members_list))
            )
            if len(members_list) > 1
            else ""
        )
        + " ],\n"
        '      "tasks": [ { "id": 0, "assigneeId": 1, "duration": 1 } ]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Create AT LEAST 2 sprints in total. You may distribute tasks across them.\n"
        "- You MUST use ONLY these assignee names: "
        + ", ".join(members_list)
        + ". If you use assigneeId, map them to those names.\n"
        "- You MUST use EXACT task ids and durations from the provided list below.\n"
        "- Each task must include either assigneeId or assignee/name.\n"
        "- Do NOT invent new tasks or members.\n"
        "- You may omit start times; durations are in hours.\n"
        "- Respect dependencies: a task cannot start before all its dependencies have finished.\n"
        "- Output strictly the JSON object, no extra text.\n\n"
        "Provided tasks (id, duration_hours, dependencies):\n"
        + json.dumps(task_brief, separators=(",", ":"))
        + "\n"
    )
    return prompt

# --------------------------
# Main benchmark loop
# --------------------------
def main():
    headers = [
        "test_id",
        "model",
        "baseline_makespan",
        "model_makespan",
        "makespan_ratio",
        "dependency_violations",
        "task_coverage",
        "avg_member_utilization",
        "feasible",
        "time_s",
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

        prompt_text = build_prompt(case)
        output, elapsed, err = run_ollama(MODEL_NAME, prompt_text)

        # Save raw model output
        (SCHEDULES_DIR / f"test_{test_id}_model_raw.txt").write_text(output, encoding="utf-8")

        # Parse -> repair
        parsed = parse_model_schedule(output, case)
        if not parsed:
            print(f"[WARN] Empty/invalid model schedule for test {test_id}; falling back to baseline for evaluation.")
            parsed = {}  # let repair place everything
        repaired = repair_model_schedule(case, parsed)

        # Save parsed/repaired schedules
        (SCHEDULES_DIR / f"test_{test_id}_model_parsed.json").write_text(json.dumps(parsed, indent=2), encoding="utf-8")
        (SCHEDULES_DIR / f"test_{test_id}_model_repaired.json").write_text(json.dumps(repaired, indent=2), encoding="utf-8")

        metrics = evaluate_model_schedule(case, repaired, baseline_makespan)

        # If the model failed completely, repaired will still schedule everything feasibly; no inf metrics.
        row = [
            test_id,
            MODEL_NAME,
            metrics["baseline_makespan"],
            metrics["model_makespan"],
            metrics["makespan_ratio"],
            metrics["dependency_violations"],
            metrics["task_coverage"],
            metrics["avg_member_utilization"],
            metrics["feasible"],
            round(elapsed, 3),
        ]
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(f"[INFO] Test {test_id} complete. Feasible: {metrics['feasible']}")

    generate_md_report(CSV_FILE, MD_REPORT)

if __name__ == "__main__":
    main()
