import csv
from pathlib import Path
import statistics
import re

def extract_date(fname: str):
    """Extract YYYY-MM-DD from filename."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
    return m.group(1) if m else "unknown"

def summarize_results(file):
    results = []
    with open(file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

    commit = [r for r in results if r["task"] == "commit_summary"]
    eisen = [r for r in results if r["task"] == "eisenhower"]
    sprint = [r for r in results if r["task"] == "sprint_planning"]

    commit_vals = [float(r.get("similarity", 0) or 0) for r in commit]
    eisen_vals = [float(r.get("accuracy", 0) or 0) for r in eisen]
    sprint_vals = [int(r.get("valid_plan", 0) or 0) for r in sprint]

    avg_commit = round(statistics.mean(commit_vals), 3) if commit_vals else 0
    avg_eisen = round(statistics.mean(eisen_vals), 3) if eisen_vals else 0
    pct_sprint = round(100 * sum(sprint_vals) / len(sprint_vals), 1) if sprint_vals else 0

    return {
        "date": extract_date(file.name),
        "file": file.name,
        "commit": avg_commit,
        "eisen": avg_eisen,
        "sprint": pct_sprint
    }

def make_trend_graph(metric_name, values, key):
    """
    Mermaid graph LR trendline with nodes for each date.
    values = list of dicts with 'date' and metric.
    """
    graph = ["```mermaid", "graph LR", f'    title["{metric_name} over time"]']
    nodes = []
    for i, entry in enumerate(values):
        val = entry[key]
        label = f'{entry["date"]}: {val}'
        node = f'N{i}["{label}"]'
        nodes.append(node)
    # connect nodes with arrows
    for i in range(len(nodes) - 1):
        graph.append(f"    {nodes[i]} --> {nodes[i+1]}")
    # add final nodes
    if nodes:
        graph.insert(2, f"    {nodes[0]}")
        graph.extend([f"    {n}" for n in nodes[1:]])
    graph.append("```")
    return "\n".join(graph)

def generate_report():
    files = sorted(Path(".").glob("benchmark_results_*.csv"))
    if not files:
        print("No benchmark CSVs found")
        return

    summaries = [summarize_results(f) for f in files]

    latest = summaries[-1]
    REPORT_FILE = Path(files[-1]).with_suffix(".md")

    with open(REPORT_FILE, "w") as f:
        f.write(f"# LLM Benchmark Report\n\n")
        f.write(f"Latest source file: `{latest['file']}`\n\n")

        # Latest snapshot summary
        f.write("## Latest Metrics\n\n")
        f.write(f"- **Commit Summary Similarity (avg):** {latest['commit']}\n")
        f.write(f"- **Eisenhower Accuracy (avg):** {latest['eisen']}\n")
        f.write(f"- **Valid Sprint Plans (%):** {latest['sprint']}%\n\n")

        # Trends section
        if len(summaries) > 1:
            f.write("## Performance Trends Over Time\n\n")

            f.write("### Commit Summaries\n")
            f.write(make_trend_graph("Commit Summary Similarities", summaries, "commit"))
            f.write("\n\n")

            f.write("### Eisenhower Matrix\n")
            f.write(make_trend_graph("Eisenhower Accuracy", summaries, "eisen"))
            f.write("\n\n")

            f.write("### Sprint Planning\n")
            f.write(make_trend_graph("Sprint Planning Validity %", summaries, "sprint"))
            f.write("\n\n")

    print(f"Report written to {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
