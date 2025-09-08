# eisenhower_benchmark.py

import csv
import json
import time
import re
import subprocess
from sklearn.metrics import precision_score, recall_score, f1_score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from difflib import SequenceMatcher
import nltk

# Ensure NLTK data is available
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

###############################
# Utility Functions
###############################

def normalize_quadrant(label: str) -> str:
    """Normalize quadrant labels to standard 4 categories."""
    if not label:
        return "Unknown"
    l = label.strip().lower()
    if "urgent" in l and "important" in l:
        if "not urgent" in l and "not important" in l:
            return "Not Urgent & Not Important"
        elif "not urgent" in l:
            return "Not Urgent & Important"
        elif "not important" in l:
            return "Urgent & Not Important"
        else:
            return "Urgent & Important"
    return "Unknown"

def jaccard_index(a, b):
    set_a, set_b = set(a.split()), set(b.split())
    return len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 0

def semantic_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

###############################
# Test Cases
###############################

test_cases = [
    ("Finish quarterly report", "Urgent & Important"),
    ("Plan team building event", "Not Urgent & Important"),
    ("Reply to casual emails", "Urgent & Not Important"),
    ("Read industry news", "Not Urgent & Not Important"),
    ("Prepare presentation for next week", "Urgent & Important"),
]

###############################
# Model Runner
###############################

def run_ollama(prompt):
    """Run ollama with subprocess and capture stdout/stderr/time."""
    start = time.time()
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1:8b"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=1200
        )
        stdout, stderr = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 1200
    elapsed = time.time() - start
    return stdout.strip(), stderr.strip(), elapsed

###############################
# Main Benchmark
###############################

def main():
    results_file = "results_eisenhower.csv"
    fieldnames = [
        "test_case", "task", "expected_quadrant", "predicted_quadrant",
        "thoughts", "raw_output", "valid_json",
        "accuracy", "semantic_similarity", "precision", "recall", "f1_score",
        "jaccard_index", "rouge_l", "bleu",
        "time_total", "time_thinking"
    ]

    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, (task, expected) in enumerate(test_cases, start=1):
            print(f"\n[INFO] Test case {i}: {task}")
            prompt = f"""
You are an assistant that classifies tasks into the Eisenhower Matrix.

The four quadrants are:
1. Urgent & Important
2. Not Urgent & Important
3. Urgent & Not Important
4. Not Urgent & Not Important

Return ONLY a JSON object with two fields:
- "quadrant": one of the four quadrant labels above
- "thoughts": your reasoning

Task: "{task}"
"""

            stdout, stderr, elapsed = run_ollama(prompt)
            raw_output = stdout
            print("[RAW OUTPUT]", raw_output[:300], "...\n")

            valid_json = False
            predicted, thoughts = "Unknown", ""
            time_thinking = 0.0

            # Try to extract JSON
            try:
                match = re.search(r"\{.*\}", raw_output, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    predicted = normalize_quadrant(data.get("quadrant", ""))
                    thoughts = data.get("thoughts", "")
                    valid_json = True
            except Exception as e:
                print(f"[ERROR] JSON parse failed: {e}")

            expected_norm = normalize_quadrant(expected)

                        # Metrics
            accuracy = int(predicted == expected_norm)
            sem_sim = semantic_similarity(expected_norm, predicted)

            precision = recall = f1 = 0.0
            if predicted != "Unknown":
                try:
                    precision = precision_score([expected_norm], [predicted], average="micro", zero_division=0)
                    recall = recall_score([expected_norm], [predicted], average="micro", zero_division=0)
                    f1 = f1_score([expected_norm], [predicted], average="micro", zero_division=0)
                except Exception as e:
                    print(f"[WARNING] Skipping precision/recall/f1 calculation: {e}")

            jaccard = jaccard_index(expected_norm, predicted)

            rouge = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            rouge_l = rouge.score(expected_norm, predicted)["rougeL"].fmeasure

            smoothie = SmoothingFunction().method4
            bleu = sentence_bleu([expected_norm.split()], predicted.split(), smoothing_function=smoothie)

            row = {
                "test_case": i,
                "task": task,
                "expected_quadrant": expected_norm,
                "predicted_quadrant": predicted,
                "thoughts": thoughts,
                "raw_output": raw_output,
                "valid_json": valid_json,
                "accuracy": accuracy,
                "semantic_similarity": sem_sim,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "jaccard_index": jaccard,
                "rouge_l": rouge_l,
                "bleu": bleu,
                "time_total": elapsed,
                "time_thinking": time_thinking
            }

            writer.writerow(row)
            print(f"[RESULT] Predicted={predicted}, Expected={expected_norm}, Acc={accuracy}, BLEU={bleu:.3f}, ROUGE-L={rouge_l:.3f}")

    print(f"\n[INFO] Benchmark completed. Results saved to {results_file}")


###############################
# Run
###############################

if __name__ == "__main__":
    main()

