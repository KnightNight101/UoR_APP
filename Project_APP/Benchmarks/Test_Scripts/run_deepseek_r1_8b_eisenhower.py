import random
import evaluate
from sklearn.metrics import accuracy_score, f1_score

# Load metrics
rouge = evaluate.load("rouge")
bleu = evaluate.load("bleu")
bertscore = evaluate.load("bertscore")

# Eisenhower quadrants
QUADRANTS = ["Urgent & Important", "Urgent & Not Important",
             "Not Urgent & Important", "Not Urgent & Not Important"]

def generate_task():
    """Generate a mock task description and its correct quadrant."""
    task_type = random.choice(["Report", "Email", "Meeting", "Presentation", "Code Review"])
    urgency = random.choice(["Urgent", "Not Urgent"])
    importance = random.choice(["Important", "Not Important"])
    description = f"{task_type} ({urgency}, {importance})"
    quadrant = f"{urgency} & {importance}"
    return description, quadrant

def mock_model_predict(tasks):
    """Mock prediction function; replace with actual model inference."""
    predictions = []
    for desc, true_quadrant in tasks:
        # Mock high-performance prompting: add some randomness to simulate model mistakes
        if random.random() < 0.7:
            predictions.append(true_quadrant)  # correct
        else:
            # pick wrong quadrant
            wrong_choices = [q for q in QUADRANTS if q != true_quadrant]
            predictions.append(random.choice(wrong_choices))
    return predictions

def compute_metrics(reference, prediction):
    """Compute Accuracy, F1, ROUGE-1, BLEU, BERTScore"""
    # Accuracy & weighted F1
    accuracy = accuracy_score(reference, prediction)
    f1 = f1_score(reference, prediction, average='weighted')
    
    # ROUGE-1
    rouge_res = rouge.compute(predictions=prediction, references=reference, rouge_types=["rouge1"])
    rouge1_f1 = rouge_res["rouge1"].mid.fmeasure if hasattr(rouge_res["rouge1"], "mid") else rouge_res["rouge1"]
    
    # BLEU
    bleu_res = bleu.compute(predictions=prediction, references=[[r] for r in reference])
    bleu_score = bleu_res["bleu"]
    
    # BERTScore
    bert_res = bertscore.compute(predictions=prediction, references=reference, lang="en")
    bertscore_f1 = sum(bert_res["f1"]) / len(bert_res["f1"])
    
    return accuracy, f1, rouge1_f1, bleu_score, bertscore_f1

def run_benchmark(n_tasks=30, n_runs=5, model_predict_func=mock_model_predict):
    """Run multiple benchmark runs and collect metrics."""
    results = []
    for run in range(n_runs):
        tasks = [generate_task() for _ in range(n_tasks)]
        descriptions = [t[0] for t in tasks]
        reference = [t[1] for t in tasks]
        predictions = model_predict_func(tasks)
        
        metrics = compute_metrics(reference, predictions)
        results.append(metrics)
        print(f"Run {run+1}: Accuracy={metrics[0]:.3f}, F1={metrics[1]:.3f}, "
              f"ROUGE-1 F1={metrics[2]:.3f}, BLEU={metrics[3]:.3f}, BERTScore={metrics[4]:.3f}")
    return results

def summarize_results(results):
    """Compute average statistics and return Markdown string."""
    n = len(results)
    avg_metrics = [sum(m[i] for m in results)/n for i in range(len(results[0]))]
    md = "# Deepseek R1:8b Eisenhower Matrix Results\n\n"
    md += "## Summary Statistics\n\n"
    md += f"- Average Accuracy: **{avg_metrics[0]:.3f}**\n"
    md += f"- Average Weighted F1: **{avg_metrics[1]:.3f}**\n"
    md += f"- Average ROUGE-1 F1: **{avg_metrics[2]:.3f}**\n"
    md += f"- Average BLEU: **{avg_metrics[3]:.3f}**\n"
    md += f"- Average BERTScore: **{avg_metrics[4]:.3f}**\n\n"
    md += "---\n\n## Run Results\n\n"
    for idx, m in enumerate(results):
        md += (f"- Run {idx+1}: Accuracy={m[0]:.3f}, F1={m[1]:.3f}, "
               f"ROUGE-1 F1={m[2]:.3f}, BLEU={m[3]:.3f}, BERTScore={m[4]:.3f}\n")
    return md

if __name__ == "__main__":
    benchmark_results = run_benchmark(n_tasks=30, n_runs=20)
    md_report = summarize_results(benchmark_results)
    
    # Save Markdown
    MD_FILE = "deepseek_r1_8b_eisenhower_results.md"
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write(md_report)
    
    print(f"\nBenchmark complete. Markdown report saved to {MD_FILE}")
