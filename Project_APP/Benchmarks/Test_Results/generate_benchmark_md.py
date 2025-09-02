import csv
from pathlib import Path

CSV_FILE = Path(__file__).parent / "benchmark_results.csv"
MD_FILE = Path(__file__).parent / "benchmark_results.md"

def generate_md_from_csv(csv_path, md_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        results = list(reader)

    md = "# LLM Benchmark Report\n\n"

    # Collect all models and test types
    models = sorted(set(r["model"] for r in results))
    test_types = sorted(set(r["test_type"] for r in results))

    # Table header
    md += "## Model Performance Summary\n\n"
    headers = ["Model", "Test Type", "Num Tests", "Accuracy (avg)", "Precision (avg)", "Time Avg (s)", "Time Min (s)", "Time Max (s)"]
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["-"*len(h) for h in headers]) + " |\n"

    # Summary metrics per model/test type
    for model in models:
        for test_type in test_types:
            subset = [r for r in results if r["model"] == model and r["test_type"] == test_type]
            if not subset:
                continue
            num_tests = len(subset)
            accuracy_vals = [min(float(r["accuracy"]),1.0) for r in subset]
            precision_vals = [min(float(r.get("precision",0)),1.0) for r in subset]
            times = [float(r["time_s"]) for r in subset]

            md += f"| {model} | {test_type} | {num_tests} | {sum(accuracy_vals)/num_tests:.3f} | {sum(precision_vals)/num_tests:.3f} | {sum(times)/num_tests:.3f} | {min(times):.3f} | {max(times):.3f} |\n"

    # Detailed per-test results
    md += "\n## Detailed Per-Test Results\n"
    for model in models:
        md += f"\n### Model: {model}\n"
        for test_type in test_types:
            subset = [r for r in results if r["model"] == model and r["test_type"] == test_type]
            if not subset:
                continue
            md += f"\n#### Test Type: {test_type}\n\n"
            md += "| Test # | Accuracy | Precision | Time (s) | Input / Task | Model Output |\n"
            md += "|--------|---------|-----------|-----------|---------------|--------------|\n"
            for idx, r in enumerate(subset, 1):
                # Use placeholders if the CSV doesn't include input/output columns
                input_tasks = r.get("input", "N/A").replace("\n","<br>")
                model_output = r.get("output", "N/A").replace("\n","<br>")
                accuracy = min(float(r["accuracy"]),1.0)
                precision = min(float(r.get("precision",0)),1.0)
                time_s = float(r["time_s"])
                md += f"| {idx} | {accuracy:.3f} | {precision:.3f} | {time_s:.2f} | {input_tasks} | {model_output} |\n"

    # Mermaid Gantt chart
    md += "\n## Model Benchmark Gantt Diagram\n"
    md += "```mermaid\ngantt\n    title Model Task Execution Times\n    dateFormat  SS\n"

    task_counter = 0
    for r in results:
        try:
            start_time = task_counter
            duration = float(r["time_s"])
            task_name = f"{r['model'].replace(':','_')}_{r['test_type'].replace(' ','_')}_{task_counter}"
            md += f"    {task_name} :done, {start_time}, {duration:.2f}\n"
            task_counter += int(duration) + 1  # sequential timing
        except Exception as e:
            print(f"[WARN] Skipping task for Gantt chart: {e}")

    md += "```\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[INFO] Markdown report generated at {md_path}")

if __name__ == "__main__":
    generate_md_from_csv(CSV_FILE, MD_FILE)
