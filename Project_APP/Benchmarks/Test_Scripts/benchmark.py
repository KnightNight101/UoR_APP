import json
import csv
import subprocess
import time
from pathlib import Path
import random

# ----------------------------
# Config Paths
# ----------------------------
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR.parent / "Test_Results"
RESULTS_DIR.mkdir(exist_ok=True)
CSV_FILE = RESULTS_DIR / f"benchmark_results.csv"
MD_FILE = RESULTS_DIR / f"benchmark_results.md"

# ----------------------------
# Models to benchmark
# ----------------------------
MODELS = ["tinyllama:1.1b", "deepseek-r1:8b"]

# ----------------------------
# Utility functions
# ----------------------------
def ensure_ollama():
    # Try default Windows path
    default_path = Path("C:/Users/KnightNight101/AppData/Local/Programs/Ollama/ollama.exe")
    if default_path.exists():
        return str(default_path)
    raise EnvironmentError("Ollama executable not found. Install Ollama first.")

def run_cmd(cmd):
    """Run a subprocess command and return stdout."""
    try:
        print(f"[DEBUG] Running command: {cmd}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
        print(f"[DEBUG] stdout: {result.stdout}")
        print(f"[DEBUG] stderr: {result.stderr}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}\nReturn code: {e.returncode}\nstdout: {e.stdout}\nstderr: {e.stderr}")
        return ""

def query_model(model_name, prompt):
    """
    Run a prompt on the model using Ollama CLI (Windows-compatible).
    Escapes newlines and quotes to prevent CLI errors.
    """
    ollama_path = ensure_ollama()
    # Sanitize prompt: remove leading + or - and escape line breaks & quotes
    safe_prompt = "\n".join([line[2:] if line.startswith(("+", "-")) else line for line in prompt.splitlines()])
    safe_prompt = safe_prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama_path, "run", model_name, safe_prompt]
    return run_cmd(cmd)

# ----------------------------
# Test Case Generators
# ----------------------------
def generate_commit_summary_tests(n=100):
    tests = []
    for _ in range(n):
        diff_lines = [f"{random.choice(['+', '-'])} {random.randint(0, 999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')}" for _ in range(5)]
        tests.append({"diff": "\n".join(diff_lines), "expected": "summary"})
    return tests

def generate_eisenhower_tests(n=100):
    tests = []
    for _ in range(n):
        tasks = [{"id": i, "title": f"Task_{random.randint(0,1000)}"} for i in range(random.randint(3,6))]
        tests.append({"tasks": tasks})
    return tests

def generate_sprint_planning_tests(n=100):
    tests = []
    for _ in range(n):
        tasks = [{"id": i, "title": f"Task_{random.randint(0,1000)}",
                  "estimate": random.randint(1,8),
                  "dependencies": random.sample(range(i), k=random.randint(0, i) if i>0 else 0)} for i in range(random.randint(3,6))]
        tests.append({"tasks": tasks})
    return tests

# ----------------------------
# Metrics
# ----------------------------
def evaluate_output(output, expected):
    # Placeholder: treat exact match as accuracy=1 else 0
    return 1.0 if expected in output else 0.0

# ----------------------------
# Benchmarking function
# ----------------------------
def run_benchmark_for_model(model_name):
    results = []

    test_sets = [
        ("Commit Summary", generate_commit_summary_tests),
        ("Eisenhower", generate_eisenhower_tests),
        ("Sprint Planner", generate_sprint_planning_tests)
    ]

    for test_name, generator in test_sets:
        tests = generator()
        for test_case in tests:
            # Format prompt for each test type
            if test_name == "Commit Summary":
                prompt = f"Summarize the following diff:\n{test_case['diff']}"
            elif test_name == "Eisenhower":
                task_list = "\n".join(f"- {t['title']}" for t in test_case['tasks'])
                prompt = f"Categorize these tasks using the Eisenhower matrix:\n{task_list}"
            elif test_name == "Sprint Planner":
                task_list = "\n".join(f"- {t['title']} (estimate: {t['estimate']})" for t in test_case['tasks'])
                prompt = f"Plan a sprint with these tasks:\n{task_list}"
            else:
                prompt = str(test_case)

            start = time.time()
            output = query_model(model_name, prompt)
            elapsed = time.time() - start

            accuracy = evaluate_output(output, test_case.get("expected",""))
            precision = accuracy  # placeholder, could be refined
            results.append({
                "model": model_name,
                "test_type": test_name,
                "accuracy": accuracy,
                "precision": precision,
                "time_s": elapsed
            })
    return results

# ----------------------------
# CSV and Markdown Reporting
# ----------------------------
def save_csv(results):
    keys = results[0].keys()
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)

def generate_md(results):
    md = "# LLM Benchmark Report\n\n"
    models = set(r["model"] for r in results)
    md += "## Model Performance Summary\n\n"
    md += "| Model | Commit Accuracy | Eisenhower Accuracy | Sprint Accuracy | Avg Time (s) |\n"
    md += "|-------|----------------|------------------|----------------|--------------|\n"

    for model in models:
        subset = [r for r in results if r["model"]==model]
        commit_acc = sum(r["accuracy"] for r in subset if r["test_type"]=="Commit Summary")/len(subset)
        eisen_acc = sum(r["accuracy"] for r in subset if r["test_type"]=="Eisenhower")/len(subset)
        sprint_acc = sum(r["accuracy"] for r in subset if r["test_type"]=="Sprint Planner")/len(subset)
        avg_time = sum(r["time_s"] for r in subset)/len(subset)
        md += f"| {model} | {commit_acc:.3f} | {eisen_acc:.3f} | {sprint_acc:.3f} | {avg_time:.3f} |\n"

    md += "\n## Model Benchmark Diagram\n"
    md += "```mermaid\ngantt\n    title Model Task Execution Times\n"
    for r in results[:20]:  # show sample of 20 tasks
        md += f"    task{r['model'].replace(':','_')}_{r['test_type'].replace(' ','_')} :done, 0, {r['time_s']:.2f}s\n"
    md += "```\n"

    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(md)

# ----------------------------
# Main
# ----------------------------
def main():
    print("Checking models...")
    ollama_path = ensure_ollama()
    for model in MODELS:
        # Check if model exists
        out = run_cmd([ollama_path, "list"])
        if model in out:
            print(f"Model already exists: {model}")
        else:
            print(f"Pulling model: {model}")
            run_cmd([ollama_path, "pull", model])

    all_results = []
    for model_name in MODELS:
        print(f"Benchmarking {model_name}...")
        all_results += run_benchmark_for_model(model_name)

    if all_results:
        save_csv(all_results)
        generate_md(all_results)
        print(f"Benchmark completed! Results saved to {CSV_FILE} and {MD_FILE}")

if __name__ == "__main__":
    main()
