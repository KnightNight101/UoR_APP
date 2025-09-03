import csv
import random
import time
from pathlib import Path
import subprocess

# Optional metrics libraries
try:
    from sentence_transformers import SentenceTransformer, util
    from bert_score import score as bert_score
    from rouge_score import rouge_scorer
    from nltk.translate.bleu_score import sentence_bleu
except ImportError:
    print("[WARNING] Some metrics libraries not installed. Install sentence-transformers, bert-score, rouge-score, nltk.")

CSV_FILE = Path(__file__).parent.parent / "Test_Results" / "deepseek_r1_8b_commit_summary.csv"

def ensure_ollama():
    path = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")
    if path.exists():
        return str(path)
    raise FileNotFoundError("Ollama executable not found.")

def run_cmd(cmd, timeout=300):
    """Run a subprocess command with UTF-8 decoding and timeout."""
    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        stdout, stderr = process.communicate(timeout=timeout)
        elapsed = time.time() - start_time
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        elapsed = timeout
        print(f"[ERROR] Command timed out after {timeout}s")

    if process.returncode != 0:
        print(f"[ERROR] Command failed: {cmd}\nstdout: {stdout}\nstderr: {stderr}")

    return stdout.strip(), stderr.strip(), elapsed

def query_model(model_name, prompt):
    ollama = ensure_ollama()
    cmd = [ollama, "run", model_name, prompt]
    return run_cmd(cmd)

def generate_commit_tests(n=20):
    """Generate realistic commit diffs for testing."""
    actions = ["+", "-"]
    files = ["script.py", "main.cpp", "utils.js", "README.md", "config.yaml"]
    tests = []
    for _ in range(n):
        lines = [f"{random.choice(actions)} {random.randint(1,999)} {random.choice(files)}"
                 for _ in range(random.randint(3,6))]
        expected_summary = "Some changes in code files"  # Could be refined for better metric evaluation
        tests.append({"diff": "\n".join(lines), "expected": expected_summary})
    return tests

def evaluate_metrics(output, expected):
    """Compute all metrics for a single test case."""
    metrics = {
        "accuracy": 1.0 if output == expected else 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1_score": 0.0,
        "semantic_similarity": 0.0,
        "bert_precision": 0.0,
        "bert_recall": 0.0,
        "bert_f1": 0.0,
        "rouge1_f1": 0.0,
        "rouge2_f1": 0.0,
        "rougeL_f1": 0.0,
        "bleu": 0.0
    }

    # Semantic similarity
    try:
        st_model = SentenceTransformer('all-MiniLM-L6-v2')
        sim = util.cos_sim(st_model.encode(expected), st_model.encode(output)).item()
        metrics["semantic_similarity"] = sim
    except Exception:
        pass

    # BERTScore
    try:
        P, R, F1 = bert_score([output], [expected], lang='en')
        metrics["bert_precision"] = P[0].item()
        metrics["bert_recall"] = R[0].item()
        metrics["bert_f1"] = F1[0].item()
    except Exception:
        pass

    # ROUGE
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)
        scores = scorer.score(expected, output)
        metrics["rouge1_f1"] = scores["rouge1"].fmeasure
        metrics["rouge2_f1"] = scores["rouge2"].fmeasure
        metrics["rougeL_f1"] = scores["rougeL"].fmeasure
    except Exception:
        pass

    # BLEU
    try:
        metrics["bleu"] = sentence_bleu([expected.split()], output.split())
    except Exception:
        pass

    return metrics

def save_csv_row(row):
    fieldnames = [
        "accuracy","precision","recall","f1_score",
        "semantic_similarity","bert_precision","bert_recall","bert_f1",
        "rouge1_f1","rouge2_f1","rougeL_f1","bleu",
        "model","test_type","time_s"
    ]
    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def main():
    model_name = "deepseek-r1:8b"
    test_type = "Commit Summary"
    tests = generate_commit_tests(20)

    for idx, test in enumerate(tests, 1):
        print(f"[INFO] Running test case {idx}/{len(tests)} for {test_type}")
        prompt = f"Summarize the following diff:\n{test['diff']}"
        output, stderr, elapsed = query_model(model_name, prompt)

        metrics = evaluate_metrics(output, test["expected"])
        metrics.update({"model": model_name, "test_type": test_type, "time_s": elapsed})

        save_csv_row(metrics)
        print(f"[INFO] Test {idx} finished in {elapsed:.2f}s | Semantic Sim={metrics['semantic_similarity']:.3f}")

if __name__ == "__main__":
    main()
