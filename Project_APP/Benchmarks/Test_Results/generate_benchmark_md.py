import csv
from pathlib import Path

CSV_FILE = Path(__file__).parent / "benchmark_results.csv"
MD_FILE = Path(__file__).parent / "benchmark_results.md"

def generate_md_from_csv(csv_path, md_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        results = list(reader)

    md = "# LLM Benchmark Report\n\n"
    models = set(r["model"] for r in results)
    md += "## Model Performance Summary\n\n"
    md += "| Model | Commit Accuracy | Eisenhower Accuracy | Sprint Accuracy | Avg Time (s) |\n"
    md += "|-------|----------------|------------------|----------------|--------------|\n"

    for model in models:
        subset = [r for r in results if r["model"] == model]
        commit_acc = sum(float(r["accuracy"]) for r in subset if r["test_type"] == "Commit Summary") / max(1, len([r for r in subset if r["test_type"] == "Commit Summary"]))
        eisen_acc = sum(float(r["accuracy"]) for r in subset if r["test_type"] == "Eisenhower") / max(1, len([r for r in subset if r["test_type"] == "Eisenhower"]))
        sprint_acc = sum(float(r["accuracy"]) for r in subset if r["test_type"] == "Sprint Planner") / max(1, len([r for r in subset if r["test_type"] == "Sprint Planner"]))
        avg_time = sum(float(r["time_s"]) for r in subset) / max(1, len(subset))
        md += f"| {model} | {commit_acc:.3f} | {eisen_acc:.3f} | {sprint_acc:.3f} | {avg_time:.3f} |\n"

    md += "\n## Model Benchmark Diagram\n"
    md += "```mermaid\ngantt\n    title Model Task Execution Times\n"
    for r in results[:20]:  # show sample of 20 tasks
        md += f"    task{r['model'].replace(':','_')}_{r['test_type'].replace(' ','_')} :done, 0, {float(r['time_s']):.2f}s\n"
    md += "```\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    generate_md_from_csv(CSV_FILE, MD_FILE)