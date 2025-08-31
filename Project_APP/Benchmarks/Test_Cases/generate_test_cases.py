# generate_test_cases.py
import os
import json
from pathlib import Path
import random
import string

# --------------------------
# Paths
# --------------------------
BASE_DIR = Path(__file__).resolve().parent
TEST_CASES_DIR = BASE_DIR / "Test_Cases"
TEST_CASES_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------
# Utility Functions
# --------------------------
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --------------------------
# Commit Summary Test Cases
# --------------------------
def generate_commit_summary_cases(n=100):
    cases = []
    for i in range(n):
        diff_lines = [f"+ {random_string(20)}" for _ in range(random.randint(1, 5))]
        diff_lines += [f"- {random_string(20)}" for _ in range(random.randint(0, 3))]
        expected_commit = random_string(15)
        cases.append({
            "diff": "\n".join(diff_lines),
            "expected": expected_commit
        })
    path = TEST_CASES_DIR / "commit_summary_tests.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4)
    print(f"Generated {n} commit summary test cases -> {path}")

# --------------------------
# Eisenhower Test Cases
# --------------------------
def generate_eisenhower_cases(n=100):
    quadrants = ["Do First", "Schedule", "Delegate", "Eliminate"]
    cases = []
    for i in range(n):
        tasks = [{"id": j, "title": random_string(12)} for j in range(random.randint(3, 8))]
        expected = {q: random.sample([t["id"] for t in tasks], k=random.randint(0, len(tasks))) for q in quadrants}
        cases.append({
            "tasks": tasks,
            "expected": expected
        })
    path = TEST_CASES_DIR / "eisenhower_tests.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4)
    print(f"Generated {n} Eisenhower test cases -> {path}")

# --------------------------
# Sprint Planning Test Cases
# --------------------------
def generate_sprint_planning_cases(n=100):
    cases = []
    for i in range(n):
        num_tasks = random.randint(3, 8)
        tasks = []
        for t in range(num_tasks):
            tasks.append({
                "id": t,
                "title": random_string(12),
                "estimate": random.randint(1, 8),
                "dependencies": random.sample(range(t), k=random.randint(0, t)) if t > 0 else []
            })
        team = {
            f"user{u}": {"available_hours": 16} for u in range(random.randint(2, 4))
        }
        cases.append({
            "tasks": tasks,
            "team": team
        })
    path = TEST_CASES_DIR / "sprint_planning_tests.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4)
    print(f"Generated {n} sprint planning test cases -> {path}")

# --------------------------
# Main
# --------------------------
def main():
    generate_commit_summary_cases()
    generate_eisenhower_cases()
    generate_sprint_planning_cases()
    print("All test cases generated successfully!")

if __name__ == "__main__":
    main()
