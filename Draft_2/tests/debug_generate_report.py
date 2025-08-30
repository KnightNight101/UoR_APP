import csv
from pathlib import Path
import statistics
import re

# -------------------------
# Utilities
# -------------------------
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
    with open(file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

    commit = [r for r in results if r.get("task") == "commit_summary"]
    eisen = [r for r in results if r.get("task") == "eisenhower"]
    sprint = [r for r in results if r.get("task") == "sprint_planning"]

    commit_vals = [safe_float(r.get("similarity")) for r in commit]
    eisen_vals = [safe_float(r.get("accuracy")) for r in eisen]
    sprint_vals = [safe_int(r.get("valid_plan")) for r in sprint]

    avg_commit = round(statistics.mean(commit_vals), 3) if commit_vals else 0
    avg_eisen = round(statistics.mean(eisen_vals), 3) if eisen_vals else 0
    pct_sprint = round(100 * sum(sprint_vals) / len(sprint_vals), 1) if sprint_vals else 0

    return {
        "date": extract_date(file.name),
        "file": file.name,
        "commit": avg_commit,
        "eisen": avg_eisen,
        "sprint": pct_sprint,
        "commit_results": commit,
        "eisen_results": eisen,
        "sprint_results": sprint
    }

# -------------------------
# Trend Graph
# -------------------------
def make_trend_graph(metric_name, values, key):
    graph = ["```mermaid", "graph LR", f'    title["{metric_name} over time"]']
    nodes = []
    for i, entry in enumerate(values):
        val = entry[key]
        label = f'{entry["date"]}: {val}'
        node = f'N{i}["{label}"]'
        nodes.append(node)
    for i in range(len(nodes)-1):
        graph.append(f"    {nodes[i]} --> {nodes[i+1]}")
    for n in nodes:
        if n not in graph:
            graph.insert(2, f"    {n}")
    graph.append("```")
    return "\n".join(graph)

# -------------------------
# Generate Markdown Report
# -------------------------
def generate_report():
    files = sorted(Path(".").glob("benchmark_results_*.csv"))
    if not files:
        print(" No benchmark CSVs found")
        return

    summaries = [summarize_results(f) for f in files]
    latest = summaries[-1]
    REPORT_FILE = Path(files[-1]).with_suffix(".md")

    with open(REPORT_FILE, "w") as f:
        f.write(f"# LLM Benchmark Report\n\n")
        f.write(f"Latest source file: `{latest['file']}`\n\n")

        # Summary table of all runs
        f.write("## Benchmark Runs Summary\n\n")
        f.write("| Date | Commit Avg | Eisenhower Avg | Sprint Valid % |\n")
        f.write("|------|------------|----------------|----------------|\n")
        for s in summaries:
            f.write(f"| {s['date']} | {s['commit']} | {s['eisen']} | {s['sprint']} |\n")
        f.write("\n")

        # Latest snapshot metrics
        f.write("## Latest Metrics\n\n")
        f.write(f"- **Commit Summary Similarity (avg):** {latest['commit']}\n")
        f.write(f"- **Eisenhower Accuracy (avg):** {latest['eisen']}\n")
        f.write(f"- **Valid Sprint Plans (%):** {latest['sprint']}%\n\n")

        # Trend graphs
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

        # Include actual LLM outputs for latest run
        f.write("## Latest LLM Outputs\n\n")

        f.write("### Commit Summary Examples\n")
        for r in latest['commit_results']:
            f.write(f"- **Input Diff:** `{r['input'][:200]}...`\n")
            f.write(f"  \n  **Expected:** `{r['expected'][:200]}...`\n")
            f.write(f"  \n  **LLM Output:** `{r['output'][:300]}...`\n")
            f.write(f"  \n  **Similarity:** {r.get('similarity', 0)}\n\n")

        f.write("### Eisenhower Matrix Examples\n")
        for r in latest['eisen_results']:
            f.write(f"- **Input Tasks:** `{r['input'][:200]}...`\n")
            f.write(f"  \n  **Expected:** `{r['expected'][:200]}...`\n")
            f.write(f"  \n  **LLM Output:** `{r['output'][:300]}...`\n")
            f.write(f"  \n  **Accuracy:** {r.get('accuracy', 0)}\n\n")

        f.write("### Sprint Planning Examples\n")
        for r in latest['sprint_results']:
            f.write(f"- **Input:** `{r['input'][:200]}...`\n")
            f.write(f"  \n  **Expected:** `{r['expected']}`\n")
            f.write(f"  \n  **LLM Output:** `{r['output'][:300]}...`\n")
            f.write(f"  \n  **Valid Plan:** {r.get('valid_plan', 0)}\n\n")

    print(f"Report written to {REPORT_FILE}")

# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    generate_report()
