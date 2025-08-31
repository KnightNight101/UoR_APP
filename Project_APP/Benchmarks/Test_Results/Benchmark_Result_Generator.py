import csv
from pathlib import Path
import datetime

# -------------------------
# Paths
# -------------------------
RESULTS_DIR = Path(__file__).parent
REPORT_MD = RESULTS_DIR / f"benchmark_report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

# automatically pick the latest CSV file
csv_files = sorted(RESULTS_DIR.glob("benchmark_results_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
if not csv_files:
    raise FileNotFoundError(f"No benchmark CSV files found in {RESULTS_DIR}")
RESULTS_CSV = csv_files[0]

print(f"Using benchmark CSV: {RESULTS_CSV}")

# -------------------------
# Utilities
# -------------------------
def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# -------------------------
# Aggregate Results
# -------------------------
def aggregate_results(rows):
    summary = {}
    for r in rows:
        model = r.get("model", "")
        task = r.get("task", "")
        if model not in summary:
            summary[model] = {"commit": [], "eisenhower": [], "sprint": [], "time": []}

        if task == "commit_summary":
            summary[model]["commit"].append(safe_float(r.get("similarity", 0.0)))
        elif task == "eisenhower":
            summary[model]["eisenhower"].append({
                "accuracy": safe_float(r.get("accuracy", 0.0)),
                "precision": safe_float(r.get("precision", 0.0))
            })
        elif task == "sprint_planning":
            summary[model]["sprint"].append(safe_float(r.get("valid_plan", 0)))
        summary[model]["time"].append(safe_float(r.get("time_taken_sec", 0.0)))
    return summary

# -------------------------
# Generate Markdown
# -------------------------
def generate_md(summary):
    lines = []
    lines.append("# LLM Benchmark Report\n")
    lines.append(f"Latest source file: `{RESULTS_CSV.name}`\n")
    
    lines.append("## Model Performance Summary\n")
    lines.append("| Model | Commit Similarity (avg) | Eisenhower Accuracy (avg) | Eisenhower Precision (avg) | Sprint Valid % | Avg Time (s) |")
    lines.append("|-------|--------------------------|----------------------------|-----------------------------|----------------|-------------|")
    
    for model, data in summary.items():
        commit_avg = round(sum(data["commit"]) / len(data["commit"]), 3) if data["commit"] else 0.0
        eisen_accuracy = round(sum(d["accuracy"] for d in data["eisenhower"]) / len(data["eisenhower"]), 3) if data["eisenhower"] else 0.0
        eisen_precision = round(sum(d["precision"] for d in data["eisenhower"]) / len(data["eisenhower"]), 3) if data["eisenhower"] else 0.0
        sprint_valid = round(sum(data["sprint"]) / len(data["sprint"]) * 100, 1) if data["sprint"] else 0.0
        avg_time = round(sum(data["time"]) / len(data["time"]), 3) if data["time"] else 0.0
        lines.append(f"| {model} | {commit_avg} | {eisen_accuracy} | {eisen_precision} | {sprint_valid}% | {avg_time} |")

    # Performance trends (mermaid)
    lines.append("\n## Performance Trends Over Time (by model)\n")
    
    # Commit similarity
    lines.append("### Commit Similarity")
    lines.append("```mermaid")
    lines.append("graph LR")
    for model, data in summary.items():
        commit_avg = round(sum(data["commit"]) / len(data["commit"]), 3) if data["commit"] else 0.0
        lines.append(f'    "{model}: {commit_avg}"')
    lines.append("```")

    # Eisenhower Accuracy
    lines.append("\n### Eisenhower Accuracy")
    lines.append("```mermaid")
    lines.append("graph LR")
    for model, data in summary.items():
        accuracy_avg = round(sum(d["accuracy"] for d in data["eisenhower"]) / len(data["eisenhower"]), 3) if data["eisenhower"] else 0.0
        lines.append(f'    "{model}: {accuracy_avg}"')
    lines.append("```")

    # Sprint valid plans
    lines.append("\n### Sprint Valid Plans (%)")
    lines.append("```mermaid")
    lines.append("graph LR")
    for model, data in summary.items():
        sprint_valid = round(sum(data["sprint"]) / len(data["sprint"]) * 100, 1) if data["sprint"] else 0.0
        lines.append(f'    "{model}: {sprint_valid}%"')
    lines.append("```")

    return "\n".join(lines)

# -------------------------
# Main
# -------------------------
def main():
    with open(RESULTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    summary = aggregate_results(rows)
    md_content = generate_md(summary)
    
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"Markdown report generated: {REPORT_MD}")

if __name__ == "__main__":
    main()
