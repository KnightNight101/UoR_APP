import csv
import time
import random
from pathlib import Path
import subprocess

# Path to save CSV results
CSV_FILE = Path(__file__).parent.parent / "Test_Results" / "benchmark_results.csv"

# Ollama executable checker
def ensure_ollama():
    default_path = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")
    if default_path.exists():
        return str(default_path)
    raise EnvironmentError("Ollama executable not found. Install Ollama first.")

# Run a subprocess command with timeout
def run_cmd(cmd, timeout_sec=300):
    """Runs a command with a timeout in seconds (default 5 minutes)."""
    print(f"[DEBUG] Running command: {cmd}")
    start_time = time.time()
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        stdout, stderr = process.communicate(timeout=timeout_sec)
        elapsed = time.time() - start_time
        print(f"[DEBUG] Completed in {elapsed:.2f}s")
        print(f"[DEBUG] stdout (first 200 chars): {stdout[:200]}")
        print(f"[DEBUG] stderr (first 200 chars): {stderr[:200]}")
        if process.returncode != 0:
            print(f"[ERROR] Command failed with return code {process.returncode}")
            return ""
        return stdout.strip()
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"[ERROR] Command timed out after {timeout_sec} seconds")
        return ""

# Query Ollama model
def query_model(model_name, prompt):
    ollama_path = ensure_ollama()
    safe_prompt = prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama_path, "run", model_name, safe_prompt]
    return run_cmd(cmd)

# Task-aware Eisenhower test case generator
def generate_eisenhower_tests(n=20):
    possible_tasks = [
        "Send project update email",
        "Write quarterly report",
        "Update automation scripts",
        "Run unit tests",
        "Fix critical bug in production",
        "Plan team meeting",
        "Prepare presentation slides",
        "Review pull requests",
        "Backup database",
        "Conduct code review",
        "Optimize deployment scripts",
        "Respond to client emails"
    ]
    tests = []
    for _ in range(n):
        task_sample = random.sample(possible_tasks, random.randint(3, 6))
        tasks = [{"id": i, "title": task} for i, task in enumerate(task_sample)]
        tests.append({"tasks": tasks})
    return tests

# Evaluate output
def evaluate_output(output, expected):
    # Placeholder: returns 1.0 if expected string is present
    return 1.0 if expected in output else 0.0

# Save results to CSV
def save_csv(results, append=True):
    if not results:
        return
    keys = results[0].keys()
    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if not file_exists or not append:
            writer.writeheader()
        writer.writerows(results)

# Main benchmark runner
def main():
    model_name = "deepseek-r1:8b"
    test_name = "Eisenhower"
    tests = generate_eisenhower_tests()
    
    for idx, test_case in enumerate(tests, 1):
        print(f"[INFO] Running test case {idx}/{len(tests)} for {test_name} on model {model_name}")
        task_list = "\n".join(f"- {t['title']}" for t in test_case['tasks'])
        prompt = f"Categorize these tasks using the Eisenhower matrix:\n{task_list}"
        start = time.time()
        output = query_model(model_name, prompt)
        elapsed = time.time() - start

        # For now, we do not have expected results; evaluate_output can be replaced with real logic later
        accuracy = evaluate_output(output, test_case.get("expected",""))
        precision = accuracy

        result_row = {
            "model": model_name,
            "test_type": test_name,
            "test_id": idx,
            "accuracy": accuracy,
            "precision": precision,
            "time_s": round(elapsed, 2)
        }
        save_csv([result_row], append=True)
        print(f"[INFO] Test {idx} finished in {elapsed:.2f}s with accuracy={accuracy}")

if __name__ == "__main__":
    main()
