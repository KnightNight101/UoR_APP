import csv
from pathlib import Path

CSV_FILE = Path(__file__).parent / "benchmark_results.csv"
MD_FILE = Path(__file__).parent / "benchmark_results.md"


def generate_md_from_csv(csv_path, md_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        results = list(reader)

    md = "# LLM Benchmark Report\n\n"

    # ------------------- Summary Table -------------------
    models = sorted(set(r["model"] for r in results))
    test_types = sorted(set(r["test_type"] for r in results))
    
    # Define all possible metrics
    metrics = ["accuracy", "precision", "recall", "f1_score"]

    md += "## Model Performance Summary\n\n"
    
    # Table headers
    headers = ["Model"]
    for test in test_types:
        headers += [f"{test} {m.capitalize()}" for m in metrics]
    headers.append("Avg Time (s)")
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for model in models:
        row = [model]
        subset = [r for r in results if r["model"] == model]
        for test in test_types:
            test_subset = [r for r in subset if r["test_type"] == test]
            for m in metrics:
                if test_subset and m in test_subset[0]:
                    value = sum(float(r[m]) for r in test_subset) / len(test_subset)
                else:
                    value = 0.0
                row.append(f"{value:.3f}")
        # Average time
        avg_time = sum(float(r.get("time_s", 0.0)) for r in subset) / len(subset) if subset else 0.0
        row.append(f"{avg_time:.2f}")
        md += "| " + " | ".join(row) + " |\n"

    # ------------------- Mermaid Diagram -------------------
    md += "\n## Model Benchmark Gantt Diagram\n"
    md += "```mermaid\ngantt\n    title LLM Task Execution Times\n    dateFormat  HH:mm:ss\n    axisFormat  %H:%M:%S\n"

    for model in models:
        model_subset = [r for r in results if r["model"] == model]
        current_time = 0
        for r in model_subset:
            task_name = f"{r['test_type'].replace(' ', '_')}_{int(current_time)}"
            duration = float(r.get("time_s", 0.0))
            md += f"    {task_name} :done, {int(current_time)}, {duration:.2f}\n"
            current_time += duration

    md += "```\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[INFO] Markdown report generated at {md_path}")

if __name__ == "__main__":
    generate_md_from_csv(CSV_FILE, MD_FILE)

    
print("Models found in CSV:", set(r["model"] for r in results))
print("Sample rows:", results[:5])
