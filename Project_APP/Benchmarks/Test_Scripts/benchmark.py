import csv
import time
import random
from pathlib import Path
import subprocess

# CSV file to store benchmark results
CSV_FILE = Path(__file__).parent.parent / "Test_Results" / "benchmark_results.csv"

def ensure_ollama():
    """Locate the Ollama executable on Windows."""
    default_path = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")
    if default_path.exists():
        return str(default_path)
    raise EnvironmentError("Ollama executable not found. Install Ollama first.")

def run_cmd(cmd, timeout=300):
    """
    Run a command with timeout (default 5 minutes per test) and return stdout.
    Returns empty string on failure.
    """
    print(f"[DEBUG] Running command: {cmd}")
    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace"
        )
        stdout, stderr = process.communicate(timeout=timeout)
        elapsed = time.time() - start_time
        if process.returncode != 0:
            print(f"[ERROR] Command failed: {cmd}\nReturn code: {process.returncode}\nstdout: {stdout}\nstderr: {stderr}")
            return "", elapsed
        return stdout.strip(), elapsed
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        elapsed = time.time() - start_time
        print(f"[ERROR] Command timed out after {timeout} seconds.\nstdout: {stdout}\nstderr: {stderr}")
        return "", elapsed

def query_model(model_name, prompt):
    """Run the model on the given prompt."""
    ollama_path = ensure_ollama()
    safe_prompt = prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama_path, "run", model_name, safe_prompt]
    return run_cmd(cmd)

def save_csv(results, append=True):
    """Save results to CSV immediately after each test case."""
    if not results:
        return
    keys = results[0].keys()
    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if not file_exists or not append:
            writer.writeheader()
        writer.writerows(results)

def evaluate_output(output, expected):
    """Basic evaluation metrics (can be expanded)."""
    accuracy = 1.0 if expected in output else 0.0
    precision = accuracy  # placeholder, replace with proper metric if available
    recall = accuracy     # placeholder
    f1 = accuracy         # placeholder
    return accuracy, precision, recall, f1

def generate_commit_summary_tests(n=15):
    """Generate synthetic commit diffs for testing."""
    tests = []
    for _ in range(n):
        diff_lines = [
            f"{random.choice(['+', '-'])} {random.randint(0, 999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')}" 
            for _ in range(5)
        ]
        tests.append({"diff": "\n".join(diff_lines), "expected": "summary"})
    return tests

def main():
    model_name = "deepseek-r1:8b"
    test_name = "Commit Summary"
    tests = generate_commit_summary_tests(n=20)
    
    for idx, test_case in enumerate(tests, 1):
        print(f"[INFO] Running test case {idx}/{len(tests)} for {test_name} on model {model_name}")
        prompt = f"Summarize the following diff:\n{test_case['diff']}"
        output, elapsed = query_model(model_name, prompt)
        accuracy, precision, recall, f1 = evaluate_output(output, test_case.get("expected", ""))
        
        result_row = {
            "model": model_name,
            "test_type": test_name,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "time_s": elapsed
        }
        save_csv([result_row], append=True)
        print(f"[INFO] Test {idx} finished in {elapsed:.2f}s | Accuracy={accuracy:.3f} Precision={precision:.3f} Recall={recall:.3f} F1={f1:.3f}")

if __name__ == "__main__":
    main()
