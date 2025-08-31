import csv
from pathlib import Path
import statistics
import re

def extract_date(fname: str):
    """Extract YYYY-MM-DD from filename."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
    return m.group(1) if m else "unknown"

def safe_float(s, default=0.0):
    try:
        return float(s)
    except (ValueError, TypeError):
        return default

def safe_int(s, default=0):
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default

def summarize_results(file):
    results = []
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

    summary = {}
    models = set(r["model"] for r in results)
    for model in models:
        model_results = [r for r in results if r["model"] == model]
        commit = [safe_float(r.get("similarity")) for r in model_results if r.get("task") == "commit_summary"]
        eisen = [safe_float(r.get("accuracy")) for r in model_results if r.get("task") == "eisenhower"]
        precision = [safe_float(r.get("precision")) for r in model_results if r.get("task") == "eisenhower"]
        sprint = [safe_int(r.get("valid_plan")) for r in model_results if r.get("task") == "sprint_planning"]
        time_taken = [safe_float(r.get("time_taken_sec")) for r in model_results]

        summary[model] = {
            "commit_avg": round(statistics.mean(commit), 3) if commit else 0,
            "eisen_avg": round(statistics.mean(eisen), 3) if eisen else 0,
            "precision_avg": round(statistics.mean(precision), 3) if precision else 0,
            "sprint_pct": round(100 * sum(sprint) / len(sprint), 1) if sprint else 0,
            "avg_time_sec": round(statistics.mean(time_taken), 3) if time_taken else 0
        }
    return summary, extract_date(file.name), file.name

def make_mermaid_bar(title, values_dict):
    """
    Generate a mermaid horizontal bar chart for values per model.
    values_dict = {model_name: value}
    """
    lines = ["```mermaid", "bar"]
    lines.append(f"title {title}")
    for model, val in values_dict.items():
        lines.append(f"{model} : {val}")
    lines.append("```")
    return "\n".join(lines)

def generate_report():
    files = sorted(Path(".").glob("benchmark_results_*.csv"))
    if not files:
        print("No benchmark CSV files found")
        return

    latest_file = files[-1]
    summary, date_str, fname = summarize_results(latest_file)

    report_file = Path(latest_file).with_suffix(".md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# LLM Benchmark Report\n\n")
        f.write(f"Latest source file: `{fname}`\n\n")

        # Model summary table
        f.write("## Model Performance Summary\n\n")
        f.write("| Model | Commit Similarity (avg) | Eisenhower Accuracy (avg) | Eisenhower Precision (avg) | Sprint Valid % | Avg Time (s) |\n")
        f.write("|-------|--------------------------|----------------------------|-----------------------------|----------------|-------------|\n")
        for model, vals in summary.items():
            f.write(f"| {model} | {vals['commit_avg']} | {vals['eisen_avg']} | {vals['precision_avg']} | {vals['sprint_pct']}% | {vals['avg_time_sec']} |\n")

        # Mermaid charts for trends
        f.write("\n## Performance Charts\n\n")
        f.write("### Commit Similarity\n")
        f.write(make_mermaid_bar("Commit Similarity", {m: v["commit_avg"] for m, v in summary.items()}))
        f.write("\n\n### Eisenhower Accuracy\n")
        f.write(make_mermaid_bar("Eisenhower Accuracy", {m: v["eisen_avg"] for m, v in summary.items()}))
        f.write("\n\n### Eisenhower Precision\n")
        f.write(make_mermaid_bar("Eisenhower Precision", {m: v["precision_avg"] for m, v in summary.items()}))
        f.write("\n\n### Sprint Planning Validity (%)\n")
        f.write(make_mermaid_bar("Sprint Valid %", {m: v["sprint_pct"] for m, v in summary.items()}))
        f.write("\n\n### Average Inference Time (s)\n")
        f.write(make_mermaid_bar("Avg Time per Prompt (s)", {m: v["avg_time_sec"] for m, v in summary.items()}))

    print(f"Report written to {report_file}")

if __name__ == "__main__":
    generate_report()
