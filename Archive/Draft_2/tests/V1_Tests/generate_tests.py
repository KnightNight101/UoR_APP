import json
import random
import os
from pathlib import Path

TEST_DIR = Path("tests")
TEST_DIR.mkdir(exist_ok=True)

# ---------------------------
# Commit Summary Generator
# ---------------------------
def generate_commit_summary_cases(n=100):
    verbs = ["fix", "feat", "refactor", "chore", "docs", "test", "style", "perf"]
    changes = [
        ("print('hello')", "print('hello world')", "update greeting"),
        ("return a+b", "return a + b", "improve formatting"),
        ("data = fetch()", "data = clean(fetch())", "clean data before returning"),
        ("pwd == db[user]", "hash(pwd) == db[user]", "secure password check"),
        ("debug: true", "debug: false", "disable debug mode"),
        ("return {}", "return {\"status\": \"ok\"}", "add status response"),
        ("# no tests yet", "def test_status(): assert True", "add basic test"),
        ("logger.debug(x)", "logger.info(x)", "change logging level"),
        ("list()", "set()", "optimize data structure"),
        ("result = []", "result = {}", "switch result container"),
    ]
    cases = []
    for _ in range(n):
        verb = random.choice(verbs)
        before, after, desc = random.choice(changes)
        diff = f"--- a/file.py\n+++ b/file.py\n- {before}\n+ {after}"
        expected = f"{verb}: {desc}"
        cases.append({"diff": diff, "expected": expected})
    return cases

# ---------------------------
# Eisenhower Matrix Generator
# ---------------------------
def generate_eisenhower_cases(n=100):
    cases = []
    for _ in range(n):
        tasks = []
        expected = {"Do First": [], "Schedule": [], "Delegate": [], "Eliminate": []}
        for tid in range(1, random.randint(4, 6)):
            importance = random.randint(1, 5)
            urgency = random.randint(1, 5)
            task = {
                "id": tid,
                "name": f"Task {tid}",
                "importance": importance,
                "urgency": urgency
            }
            tasks.append(task)
            # Ground truth assignment
            if importance >= 4 and urgency >= 4:
                expected["Do First"].append(tid)
            elif importance >= 4 and urgency < 4:
                expected["Schedule"].append(tid)
            elif importance < 4 and urgency >= 4:
                expected["Delegate"].append(tid)
            else:
                expected["Eliminate"].append(tid)
        cases.append({"tasks": tasks, "expected": expected})
    return cases

# ---------------------------
# Sprint Planning Generator
# ---------------------------
def generate_sprint_cases(n=100):
    cases = []
    for _ in range(n):
        # Generate team
        members = random.choice([2, 3, 4])
        team = {}
        for i in range(members):
            name = f"Member{i+1}"
            team[name] = {"available_hours": random.randint(10, 25)}

        # Generate tasks with dependencies
        num_tasks = random.randint(3, 6)
        tasks = []
        for tid in range(1, num_tasks+1):
            est = random.randint(3, 10)
            if tid == 1:
                deps = []
            else:
                deps = random.sample(range(1, tid), k=random.randint(0, min(2, tid-1)))
            tasks.append({"id": tid, "name": f"Task {tid}", "estimate": est, "dependencies": deps})

        cases.append({"team": team, "tasks": tasks})
    return cases

# ---------------------------
# Main
# ---------------------------
def main():
    commit_cases = generate_commit_summary_cases(30)
    eisenhower_cases = generate_eisenhower_cases(20)
    sprint_cases = generate_sprint_cases(20)

    with open(TEST_DIR / "commit_summary_tests.json", "w") as f:
        json.dump(commit_cases, f, indent=2)

    with open(TEST_DIR / "eisenhower_tests.json", "w") as f:
        json.dump(eisenhower_cases, f, indent=2)

    with open(TEST_DIR / "sprint_planning_tests.json", "w") as f:
        json.dump(sprint_cases, f, indent=2)

    print("Test cases generated in /tests")

if __name__ == "__main__":
    main()
