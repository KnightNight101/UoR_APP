#!/usr/bin/env python3
"""
Eisenhower Matrix Benchmark for enterprise-scale tasks.

- Generates N test cases of tasks with priorities and importance/urgency.
- Queries a model to sort tasks into Eisenhower quadrants.
- Evaluates performance with classification metrics and NLP metrics:
  accuracy, weighted accuracy, F1 per quadrant, confusion matrix, ROUGE, BLEU, BERTScore.
- Produces CSV and Markdown reports with summaries and distributions.

Requirements:
- nltk, rouge_score, bert_score, pandas
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any
import csv
import numpy as np

# NLP metrics
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import score as bert_score

# Classification metrics
from sklearn.metrics import f1_score, confusion_matrix

# --------------------------
# Config
# --------------------------
NUM_TESTS = 20
RESULTS_DIR = Path(__file__).parent / "Test_Results"
RESULTS_DIR.mkdir(exist_ok=True)
CSV_FILE = RESULTS_DIR / "eisenhower_benchmark.csv"
MD_FILE = RESULTS_DIR / "eisenhower_benchmark.md"

QUADRANTS = ["Urgent & Important", "Not Urgent & Important", "Urgent & Not Important", "Not Urgent & Not Important"]
QUADRANT_WEIGHTS = {
    "Urgent & Important": 4,
    "Not Urgent & Important": 3,
    "Urgent & Not Important": 2,
    "Not Urgent & Not Important": 1
}

MODEL_NAME = "your-model-name"  # replace with actual model call function
MODEL_TIMEOUT = 300  # seconds

# --------------------------
# Utilities
# --------------------------
def generate_test_case(idx: int, num_tasks: int = 10) -> List[Dict[str, Any]]:
    """
    Generate a list of tasks with title and importance/urgency.
    """
    random.seed(idx)
    tasks = []
    for i in range(num_tasks):
        title = f"Task_{i}"
        urgency = random.choice([True, False])
        importance = random.choice([True, False])
        quadrant = (
            "Urgent & Important" if urgency and importance else
            "Not Urgent & Important" if not urgency and importance else
            "Urgent & Not Important" if urgency and not importance else
            "Not Urgent & Not Important"
        )
        tasks.append({"id": i, "title": title, "urgency": urgency, "importance": importance, "quadrant": quadrant})
    return tasks

def run_model(tasks: List[Dict[str, Any]]) -> List[str]:
    """
    Strict prompt to the model to sort tasks into quadrants.
    Returns a list of predicted quadrants in order of tasks.
    """
    # Here, replace with actual model call, e.g., via OpenAI, Ollama, etc.
    # For demonstration, we do a random placeholder
    preds = []
    for t in tasks:
        preds.append(random.choice(QUADRANTS))
    return preds

# --------------------------
# NLP metrics
# --------------------------
def compute_rouge(preds: List[str], truths: List[str]) -> float:
    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
    scores = []
    for p, t in zip(preds, truths):
        scores.append(scorer.score(t, p)['rouge1'].fmeasure)
    return np.mean(scores)

def compute_bleu(preds: List[str], truths: List[str]) -> float:
    smoothie = SmoothingFunction().method4
    scores = []
    for p, t in zip(preds, truths):
        scores.append(sentence_bleu([t.split()], p.split(), smoothing_function=smoothie))
    return np.mean(scores)

def compute_bertscore(preds: List[str], truths: List[str]) -> float:
    P, R, F1 = bert_score(preds, truths, lang='en', rescale_with_baseline=True)
    return F1.mean().item()

# --------------------------
# Evaluation
# --------------------------
def evaluate(preds: List[str], truths: List[str]) -> Dict[str, Any]:
    metrics = {}
    # Basic classification metrics
    metrics["accuracy"] = sum(p == t for p, t in zip(preds, truths)) / len(truths)
    metrics["weighted_accuracy"] = sum(QUADRANT_WEIGHTS[t] if p==t else 0 for p,t in zip(preds, truths)) / sum(QUADRANT_WEIGHTS[t] for t in truths)
    metrics["f1"] = {q: f1_score([1 if t==q else 0 for t in truths],
                                 [1 if p==q else 0 for p in preds],
                                 zero_division=0)
                     for q in QUADRANTS}
    metrics["confusion"] = confusion_matrix(truths, preds, labels=QUADRANTS).tolist()
    
    # NLP metrics
    metrics["rouge"] = compute_rouge(preds, truths)
    metrics["bleu"] = compute_bleu(preds, truths)
    metrics["bertscore"] = compute_bertscore(preds, truths)
    
    return metrics

# --------------------------
# CSV helpers
# --------------------------
CSV_FIELDS = ["test_id","accuracy","weighted_accuracy","rouge","bleu","bertscore"] + QUADRANTS + ["confusion"]

def write_csv_row(path: Path, row: Dict[str, Any]):
    file_exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# --------------------------
# Markdown report
# --------------------------
def generate_md_report(csv_file: Path, md_file: Path):
    import pandas as pd
    df = pd.read_csv(csv_file)
    md_lines = []
    md_lines.append("# Deepseek R1:8b Eisenhower Matrix Results\n")
    md_lines.append("## Summary Statistics\n")
    md_lines.append(f"- Average accuracy: **{df['accuracy'].mean():.3f}**")
    md_lines.append(f"- Average weighted accuracy: **{df['weighted_accuracy'].mean():.3f}**")
    md_lines.append(f"- Average ROUGE-1 F1: **{df['rouge'].mean():.3f}**")
    md_lines.append(f"- Average BLEU: **{df['bleu'].mean():.3f}**")
    md_lines.append(f"- Average BERTScore: **{df['bertscore'].mean():.3f}**")
    md_lines.append("\n---\n")
    md_file.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Markdown report written: {md_file}")

# --------------------------
# Main
# --------------------------
def main():
    for i in range(NUM_TESTS):
        test_id = i + 1
        tasks = generate_test_case(i, num_tasks=15)
        truths = [t["quadrant"] for t in tasks]
        preds = run_model(tasks)
        metrics = evaluate(preds, truths)
        
        row = {
            "test_id": test_id,
            "accuracy": metrics["accuracy"],
            "weighted_accuracy": metrics["weighted_accuracy"],
            "rouge": metrics["rouge"],
            "bleu": metrics["bleu"],
            "bertscore": metrics["bertscore"]
        }
        for q in QUADRANTS:
            row[q] = metrics["f1"][q]
        row["confusion"] = json.dumps(metrics["confusion"])
        write_csv_row(CSV_FILE, row)
        print(f"Test {test_id} done.")

    generate_md_report(CSV_FILE, MD_FILE)

if __name__ == "__main__":
    main()
