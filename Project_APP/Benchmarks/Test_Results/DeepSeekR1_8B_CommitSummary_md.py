import pandas as pd
from pathlib import Path

CSV_FILE = Path(__file__).parent / "benchmark_results.csv"
MD_FILE = Path(__file__).parent / "deepseek_r1_8b_commit_summary.md"

def generate_mermaid_barchart(df, metric, title, label):
    """Generate a simple Mermaid bar chart for the given metric."""
    md = f"\n```mermaid\ngantt\n    title {title}\n"
    for idx, row in df.iterrows():
        value = row[metric] if pd.notnull(row[metric]) else 0
        md += f"    task{idx} :done, 0, {value:.2f}\n"
    md += "```\n"
    return md

def generate_md_report(csv_path, md_path, sort_metric="f1_score"):
    df = pd.read_csv(csv_path)

    # Handle missing sort metric gracefully
    if sort_metric not in df.columns:
        sort_metric = df.columns[0]  # fallback to first column
    df_sorted = df.sort_values(sort_metric, ascending=False)

    md = "# DeepSeek R1 8B - Commit Summary Benchmark Report\n\n"

    # Overview table
    md += "## Full Test Results\n\n"
    md += df_sorted.to_markdown(index=False) + "\n\n"

    # Top 5 / Worst 5
    md += "## Top 5 Test Cases\n\n"
    md += df_sorted.head(5).to_markdown(index=False) + "\n\n"

    md += "## Worst 5 Test Cases\n\n"
    md += df_sorted.tail(5).to_markdown(index=False) + "\n\n"

    # Generate Mermaid bar charts for all numeric metrics
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    ignore_cols = ["time_s"]  # optionally ignore time if you want a separate chart
    metrics_to_chart = [col for col in numeric_cols if col not in ignore_cols]

    for metric in metrics_to_chart:
        md += f"## {metric} per Test Case\n"
        md += generate_mermaid_barchart(df_sorted, metric, f"{metric} per Test Case", metric) + "\n"

    # Time chart separately
    if "time_s" in df.columns:
        md += generate_mermaid_barchart(df_sorted, "time_s", "Time Taken per Test Case (s)", "time_s")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    generate_md_report(CSV_FILE, MD_FILE)
