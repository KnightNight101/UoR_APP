import csv
import time
import random
from pathlib import Path
import subprocess

# Path to save benchmark results
CSV_FILE = Path(__file__).parent.parent / "Test_Results" / "benchmark_results.csv"

def ensure_ollama():
    """
    Locate Ollama executable. Adjust path if needed.
    """
    default_path = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")
    if default_path.exists():
        return str(default_path)
    raise EnvironmentError("Ollama executable not found. Install Ollama first.")

def run_cmd(cmd, prompt=None, timeout=60):
    """
    Run a subprocess command with optional stdin input (prompt).
    Includes timeout protection and debugging logs.
    """
    print(f"[DEBUG] Running command: {cmd}")
    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        stdout, stderr = process.communicate(input=prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        print(f"[ERROR] Command timed out after {timeout} seconds")
        return ""

    elapsed = time.time() - start_time
    print(f"[DEBUG] Completed in {elapsed:.2f}s")
    print(f"[DEBUG] stdout (first 200 chars): {stdout[:200]}")
    print(f"[DEBUG] stderr (first 200 chars): {stderr[:200]}")

    if process.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}\nReturn code: {process.returncode}")
        return ""
    return stdout.strip()

def query_model(model_name, prompt):
    """
    Query a model via Ollama with a given prompt.
    Sends the prompt via stdin.
    """
    ollama_path = ensure_ollama()
    cmd = [ollama_path, "run", model_name]
    return run_cmd(cmd, prompt=prompt)

def generate_commit_summary_tests(n=15):
    """
    Generate synthetic test cases for commit summaries.
    Each test consists of a fake git diff and an expected placeholder summary.
    """
    tests = []
    for _ in range(n):
        diff_lines = [
            f"{random.choice(['+', '-'])} {random.randint(0, 999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')}"
            for _ in range(5)
        ]
        tests.append({"diff": "\n".join(diff_lines), "expected": "summary"})
    return tests

def evaluate_output(output, expected):
    """
    Very basic evaluation: check if the expected string is in the output.
    Replace with more robust evaluation logic later if needed.
    """
    return 1.0 if expected in output else 0.0

def save_csv(results, append=True):
    """
    Save benchmark results to CSV.
    """
    keys = results[0].keys()
    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if not file_exists or not append:
            writer.writeheader()
        writer.writerows(results)

def main():
    """
    Main benchmarking function:
    - Generates test cases
    - Runs them against the model
    - Records accuracy, precision, and runtime
    """
    model_name = "deepseek-r1:8b"
    test_name = "Commit Summary"
    tests = generate_commit_summary_tests()

    for idx, test_case in enumerate(tests, 1):
        print(f"[INFO] Running test case {idx}/{len(tests)} for {test_name} on model {model_name}")
        prompt = f"Summarize the following diff:\n{test_case['diff']}"
        start = time.time()
        output = query_model(model_name, prompt)
        elapsed = time.time() - start

        accuracy = evaluate_output(output, test_case.get("expected", ""))
        precision = accuracy

        print(f"[INFO] Test {idx} finished in {elapsed:.2f}s with accuracy={accuracy}")

        result_row = {
            "model": model_name,
            "test_type": test_name,
            "accuracy": accuracy,
            "precision": precision,
            "time_s": elapsed
        }
        save_csv([result_row], append=True)

if __name__ == "__main__":
    main()
