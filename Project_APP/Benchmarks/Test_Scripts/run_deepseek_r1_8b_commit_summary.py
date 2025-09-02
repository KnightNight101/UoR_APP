import csv
import time
import random
from pathlib import Path
import subprocess

# Semantic similarity and summarization metrics
from sentence_transformers import SentenceTransformer, util
from bert_score import score
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu

# File paths
CSV_FILE = Path(__file__).parent.parent / "Test_Results" / "deepseek_r1_8b_commit_summary.csv"

# Load models for evaluation
sem_model = SentenceTransformer('all-MiniLM-L6-v2')
rouge_scorer_inst = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)

# -------- Utility Functions --------

def ensure_ollama():
    default_path = Path("C:/Users/yg838314/AppData/Local/Programs/Ollama/ollama.exe")
    if default_path.exists():
        return str(default_path)
    raise EnvironmentError("Ollama executable not found. Install Ollama first.")

def run_cmd(cmd, timeout=300):
    """Run subprocess command with timeout (default 5 min)."""
    print(f"[DEBUG] Running command: {cmd}")
    start_time = time.time()
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=timeout)
        stdout, stderr = result.stdout.strip(), result.stderr.strip()
        if result.returncode != 0:
            print(f"[ERROR] Command failed. stdout: {stdout}, stderr: {stderr}")
            return ""
        return stdout
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Command timed out after {timeout} seconds")
        return ""

def query_model(model_name, prompt):
    """Query the Ollama model."""
    ollama_path = ensure_ollama()
    safe_prompt = prompt.replace("\n", "\\n").replace('"', '\\"')
    cmd = [ollama_path, "run", model_name, safe_prompt]
    return run_cmd(cmd, timeout=300)

# -------- Test Case Generation --------

def generate_commit_summary_tests(n=20):
    """Generate commit diffs and expected summaries."""
    test_cases = []
    possible_changes = ['added function', 'removed line', 'updated variable', 'fixed bug', 'refactored code', 'updated README', 'changed comment']
    for _ in range(n):
        diff_lines = [f"{random.choice(['+','-'])} {random.randint(0,999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')}" for _ in range(5)]
        # Generate a "reasonable" expected summary
        expected_summary = random.choice(possible_changes)
        test_cases.append({"diff": "\n".join(diff_lines), "expected": expected_summary})
    return test_cases

# -------- Evaluation Metrics --------

def evaluate_output(output, expected):
    """Compute all metrics."""
    if not output:
        # Return 0 for all if model failed
        return {
            "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0,
            "semantic_similarity": 0.0, "bert_precision": 0.0, "bert_recall": 0.0,
            "bert_f1": 0.0, "rouge1_f1": 0.0, "rouge2_f1": 0.0, "rougeL_f1": 0.0,
            "bleu": 0.0
        }
    
    # Simple exact-match metrics
    accuracy = 1.0 if expected.lower() in output.lower() else 0.0
    precision = accuracy
    recall = accuracy
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    # Semantic similarity
    semantic_sim = util.cos_sim(sem_model.encode(output), sem_model.encode(expected)).item()

    # BERTScore
    bert_P, bert_R, bert_F1 = score([output], [expected], lang='en')
    bert_P, bert_R, bert_F1 = float(bert_P.mean()), float(bert_R.mean()), float(bert_F1.mean())

    # ROUGE
    rouge_scores = rouge_scorer_inst.score(expected, output)
    rouge1, rouge2, rougeL = rouge_scores['rouge1'].fmeasure, rouge_scores['rouge2'].fmeasure, rouge_scores['rougeL'].fmeasure

    # BLEU
    bleu = sentence_bleu([expected.split()], output.split())

    return {
        "accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1_score,
        "semantic_similarity": semantic_sim, "bert_precision": bert_P, "bert_recall": bert_R,
        "bert_f1": bert_F1, "rouge1_f1": rouge1, "rouge2_f1": rouge2, "rougeL_f1": rougeL,
        "bleu": bleu
    }

# -------- CSV Saving --------

def save_csv(results, append=True):
    keys = results[0].keys()
    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a" if append else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        if not file_exists or not append:
            writer.writeheader()
        writer.writerows(results)

# -------- Main Benchmark --------

def main():
    model_name = "deepseek-r1:8b"
    test_name = "Commit Summary"
    tests = generate_commit_summary_tests(n=20)

    for idx, test_case in enumerate(tests, 1):
        print(f"[INFO] Running test case {idx}/{len(tests)} for {test_name} on model {model_name}")
        prompt = f"Summarize the following diff:\n{test_case['diff']}"
        start_time = time.time()
        output = query_model(model_name, prompt)
        elapsed = time.time() - start_time

        metrics = evaluate_output(output, test_case["expected"])
        metrics.update({
            "model": model_name,
            "test_type": test_name,
            "time_s": elapsed
        })

        save_csv([metrics], append=True)
        print(f"[INFO] Test {idx} finished in {elapsed:.2f}s | Accuracy={metrics['accuracy']:.3f} "
              f"Precision={metrics['precision']:.3f} Recall={metrics['recall']:.3f} F1={metrics['f1_score']:.3f} "
              f"SemanticSim={metrics['semantic_similarity']:.3f} BERT_F1={metrics['bert_f1']:.3f} "
              f"ROUGE1_F1={metrics['rouge1_f1']:.3f} BLEU={metrics['bleu']:.3f}")

if __name__ == "__main__":
    main()
