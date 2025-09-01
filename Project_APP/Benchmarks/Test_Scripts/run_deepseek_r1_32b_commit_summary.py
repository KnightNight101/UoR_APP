import csv
import time
import random
from pathlib import Path
import subprocess

CSV_FILE = Path(__file__).parent.parent / "Test_Results" / "benchmark_results.csv"

def ensure_ollama():
    default_path = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")
    if default_path.exists():
        return str(default_path)
    raise EnvironmentError("Ollama executable not found. Install Ollama first.")

def run_cmd(cmd):
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
    ollama_path = ensure_ollama()
    safe_prompt = "\n".join([line[2:] if line.startswith(("+", "-")) else line for line in prompt.splitlines()])
    safe_prompt = safe_prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama_path, "run", model_name, safe_prompt]
    return run_cmd(cmd)

def generate_commit_summary_tests(n=15):
    tests = []
    for _ in range(n):
        diff_lines = [f"{random.choice(['+', '-'])} {random.randint(0, 999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')}" for _ in range(5)]
        tests.append({"diff": "\n".join(diff_lines), "expected": "summary"})
    return tests

def evaluate_output(output, expected):
    return 1.0 if expected in output else 0.0

def save_csv(results, append=True):
    keys = results[0].keys()
    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if not file_exists or not append:
            writer.writeheader()
        writer.writerows(results)

def main():
    model_name = "deepseek-r1:32b"
    test_name = "Commit Summary"
    tests = generate_commit_summary_tests()
    for idx, test_case in enumerate(tests, 1):
        print(f"[DEBUG] Running test case {idx}/15 for {test_name} on model {model_name}")
        prompt = f"Summarize the following diff:\n{test_case['diff']}"
        start = time.time()
        output = query_model(model_name, prompt)
        elapsed = time.time() - start
        accuracy = evaluate_output(output, test_case.get("expected",""))
        precision = accuracy
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