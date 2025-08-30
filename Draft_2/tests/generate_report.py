import csv
from pathlib import Path
import statistics

RESULTS_FILE = sorted(Path(".").glob("benchmark_results_*.csv"))[-1]  # latest file
REPORT_FILE = RESULTS_FILE.with_suffix(".md")

def generate_report():
    results = []
    with open(RESULTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

    # Group by task
    commit = [r for r in results if r["task"] == "commit_summary"]
    eisen = [r for r in results if r["task"] == "eisenhower"]
    sprint = [r for r in results if r["task"] == "sprint_planning"]

    # Aggregate metrics
    commit_similarities = [float(r.get("similarity", 0) or 0) for r in commit]
    eisen_acc = [float(r.get("accuracy", 0) or 0) for r in eisen]
    sprint_valid = [int(r.get("valid_plan", 0) or 0) for r in sprint]

    avg_commit = round(statistics.mean(commit_similarities), 3) if commit_similarities else 0
    avg_eisen = round(statistics.mean(eisen_acc), 3) if eisen_acc else 0
    pct_sprint = round(100 * sum(sprint_valid) / len(sprint_valid), 1) if sprint_valid else 0

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# LLM Benchmark Report\n\n")
        f.write(f"**Source file:** `{RESULTS_FILE.name}`\n\n")

        # Summary
        f.write("## Summary Metrics\n\n")
        f.write(f"- **Commit Summary Similarity (avg):** {avg_commit}\n")
        f.write(f"- **Eisenhower Accuracy (avg):** {avg_eisen}\n")
        f.write(f"- **Valid Sprint Plans (%):** {pct_sprint}%\n\n")

        # Mermaid charts
        f.write("## Performance Visualisation\n\n")

        # Commit summary chart
        if commit_similarities:
            f.write("### Commit Summaries\n")
            f.write("```mermaid\n")
            f.write("bar\n")
            f.write("  title Commit Summary Similarities\n")
            f.write("  x-axis Similarity\n")
            f.write("  y-axis Test Case\n")
            for i, sim in enumerate(commit_similarities, start=1):
                f.write(f"  \"Case {i}\" : {sim}\n")
            f.write("```\n\n")

        # Eisenhower chart
        if eisen_acc:
            f.write("### Eisenhower Matrix\n")
            f.write("```mermaid\n")
            f.write("bar\n")
            f.write("  title Eisenhower Accuracy\n")
            f.write("  x-axis Accuracy\n")
            f.write("  y-axis Test Case\n")
            for i, acc in enumerate(eisen_acc, start=1):
                f.write(f"  \"Case {i}\" : {acc}\n")
            f.write("```\n\n")

        # Sprint planning chart
        if sprint_valid:
            f.write("### Sprint Planning\n")
            f.write("```mermaid\n")
            f.write("pie showData\n")
            f.write("  title Sprint Planning Validity\n")
            f.write(f"  \"Valid\" : {sum(sprint_valid)}\n")
            f.write(f"  \"Invalid\" : {len(sprint_valid) - sum(sprint_valid)}\n")
            f.write("```\n\n")

        # Example outputs (qualitative)
        f.write("## Example Outputs\n\n")

        if commit:
            ex = commit[0]
            f.write("### Commit Summary Example\n")
            f.write(f"- **Input diff:** `{ex['input'][:60]}...`\n")
            f.write(f"- **Expected:** {ex['expected']}\n")
            f.write(f"- **Output:** {ex['output']}\n")
            f.write(f"- **Similarity:** {ex['similarity']}\n\n")

        if eisen:
            ex = eisen[0]
            f.write("### Eisenhower Example\n")
            f.write(f"- **Input tasks:** {ex['input']}\n")
            f.write(f"- **Expected:** {ex['expected']}\n")
            f.write(f"- **Output:** {ex['output']}\n")
            f.write(f"- **Accuracy:** {ex['accuracy']}\n\n")

        if sprint:
            ex = sprint[0]
            f.write("### Sprint Planning Example\n")
            f.write(f"- **Input:** {ex['input'][:80]}...\n")
            f.write(f"- **Output:** {ex['output']}\n")
            f.write(f"- **Valid Plan:** {ex['valid_plan']}\n\n")

    print(f" Report written to {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
