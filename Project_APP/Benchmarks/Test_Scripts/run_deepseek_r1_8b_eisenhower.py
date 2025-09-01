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
    print(f"[DEBUG] Running command: {cmd}")
    start_time = time.time()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    poll_interval = 5  # seconds
    last_print = start_time
    while True:
        if process.poll() is not None:
            break
        now = time.time()
        if now - last_print >= poll_interval:
            elapsed = int(now - start_time)
            print(f"[DEBUG] Model running... {elapsed} seconds elapsed")
            last_print = now
        time.sleep(1)
    stdout, stderr = process.communicate()
    print(f"[DEBUG] stdout: {stdout}")
    print(f"[DEBUG] stderr: {stderr}")
    if process.returncode != 0:
        print(f"Command failed: {cmd}\nReturn code: {process.returncode}\nstdout: {stdout}\nstderr: {stderr}")
        return ""
    return stdout.strip()

def query_model(model_name, prompt):
    ollama_path = ensure_ollama()
    safe_prompt = prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama_path, "run", model_name, safe_prompt]
    return run_cmd(cmd)

def generate_eisenhower_tests(n=15):
    tests = []
    for _ in range(n):
        tasks = [{"id": i, "title": f"Task_{random.randint(0,1000)}"} for i in range(random.randint(3,6))]
        tests.append({"tasks": tasks})
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
    model_name = "deepseek-r1:8b"
    test_name = "Eisenhower"
    tests = generate_eisenhower_tests()
    for idx, test_case in enumerate(tests, 1):
        print(f"[DEBUG] Running test case {idx}/15 for {test_name} on model {model_name}")
        task_list = "\n".join(f"- {t['title']}" for t in test_case['tasks'])
        prompt = f"Categorize these tasks using the Eisenhower matrix:\n{task_list}"
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