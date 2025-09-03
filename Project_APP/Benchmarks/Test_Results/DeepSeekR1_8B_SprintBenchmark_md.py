import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import io

# Input CSV and output MD
CSV_FILE = Path(r"C:\Users\yg838314\Documents\UoR_App\UoR_APP\Project_APP\Benchmarks\Test_Scripts\Test_Results\deepseek_r1_8b_sprint_benchmark.csv")
MD_FILE = Path(r"C:\Users\yg838314\Documents\UoR_App\UoR_APP\Project_APP\Benchmarks\Test_Results\deepseek_r1_8b_sprint_report.md")



def generate_md(csv_file, md_file, top_k=5):
    try:
        # Try normal load
        df = pd.read_csv(csv_file)
    except pd.errors.ParserError:
        print("[!] ParserError: Found malformed rows, attempting recovery...")
        # Read manually and skip bad lines
        df = pd.read_csv(csv_file, on_bad_lines='skip')
        print(f"[!] Skipped malformed rows. Remaining rows: {len(df)}")

        print(f"[+] Loaded {len(df)} rows with columns: {list(df.columns)}")

def fig_to_svg(fig):
    """Convert Matplotlib figure to inline SVG string."""
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def generate_md(csv_file, md_file, top_k=5):
    df = pd.read_csv(csv_file)

    # Filter out failed runs (-1 makespan_ratio)
    df_valid = df[df["makespan_ratio"] > 0]

    # Summary stats
    avg_ratio = df_valid["makespan_ratio"].mean()
    avg_cov = df_valid["task_coverage"].mean()
    avg_util = df_valid["avg_member_utilization"].mean()
    feasible_pct = 100 * df_valid["feasible"].mean()

    # Ranking
    best = df_valid.nsmallest(top_k, "makespan_ratio")
    worst = df_valid.nlargest(top_k, "makespan_ratio")

    md_lines = []
    md_lines.append("# Deepseek R1:8b Sprint Planner Results\n")

    # Summary
    md_lines.append("## Summary Statistics\n")
    md_lines.append(f"- Average makespan ratio: **{avg_ratio:.3f}**\n")
    md_lines.append(f"- Average task coverage: **{avg_cov:.2%}**\n")
    md_lines.append(f"- Average member utilization: **{avg_util:.2f}%**\n")
    md_lines.append(f"- Feasible schedules: **{feasible_pct:.1f}%**\n")
    md_lines.append("\n---\n")

    # Mermaid chart (bar chart for makespan ratios)
    md_lines.append("## Makespan Ratio Distribution (Mermaid)\n")
    md_lines.append("```mermaid")
    md_lines.append("bar")
    md_lines.append("    title Makespan Ratios by Test ID")
    for _, row in df.iterrows():
        ratio = row["makespan_ratio"] if row["makespan_ratio"] > 0 else 0
        md_lines.append(f'    "{int(row["test_id"])}" : {ratio:.2f}')
    md_lines.append("```")
    md_lines.append("\n---\n")

    # Top / Worst
    md_lines.append(f"## Top {top_k} Best Tests\n")
    md_lines.append(best.to_markdown(index=False))
    md_lines.append("\n\n")
    md_lines.append(f"## Top {top_k} Worst Tests\n")
    md_lines.append(worst.to_markdown(index=False))
    md_lines.append("\n---\n")

    # Inline SVG plots
    md_lines.append("## Metrics Over Tests (SVG Plots)\n")

    # Plot 1: makespan ratios
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["test_id"], df["makespan_ratio"].replace(-1, 0), marker="o")
    ax.set_title("Makespan Ratios per Test")
    ax.set_xlabel("Test ID")
    ax.set_ylabel("Makespan Ratio")
    svg_str = fig_to_svg(fig)
    md_lines.append("<details><summary>Click to expand Makespan Ratio plot</summary>\n")
    md_lines.append(svg_str)
    md_lines.append("</details>\n")

    # Plot 2: task coverage
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["test_id"], df["task_coverage"], marker="x", color="green")
    ax.set_title("Task Coverage per Test")
    ax.set_xlabel("Test ID")
    ax.set_ylabel("Coverage")
    svg_str = fig_to_svg(fig)
    md_lines.append("<details><summary>Click to expand Task Coverage plot</summary>\n")
    md_lines.append(svg_str)
    md_lines.append("</details>\n")

    # Plot 3: utilization
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["test_id"], df["avg_member_utilization"], marker="s", colimport pandas as pd

def generate_md(csv_file, md_file, top_k=5):
    try:
        df = pd.read_csv(csv_file)
    except pd.errors.ParserError:
        print("[!] ParserError: Found malformed rows, attempting recovery...")
        df = pd.read_csv(csv_file, on_bad_lines="skip")
        print(f"[!] Skipped malformed rows. Remaining rows: {len(df)}")

    # --- Your existing code continues unchanged below ---
    # For example:
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# Sprint Planner Benchmark Report\n\n")
        f.write(f"Source CSV: `{csv_file}`\n\n")
        f.write(f"Total Runs: {len(df)}\n\n")

        # Summary statistics
        f.write("## Summary Statistics\n\n")
        f.write(df.describe().to_markdown() + "\n\n")

        # Top K results by makespan ratio (best efficiency)
        if "makespan_ratio" in df.columns:
            top = df.sort_values("makespan_ratio").head(top_k)
            f.write(f"## Top {top_k} Results (by makespan ratio)\n\n")
            f.write(top.to_markdown(index=False) + "\n\n")

        # Full table
        f.write("## Full Results\n\n")
        f.write(df.to_markdown(index=False) + "\n")
or="purple")
    ax.set_title("Average Member Utilization per Test")
    ax.set_xlabel("Test ID")
    ax.set_ylabel("Utilization (%)")
    svg_str = fig_to_svg(fig)
    md_lines.append("<details><summary>Click to expand Utilization plot</summary>\n")
    md_lines.append(svg_str)
    md_lines.append("</details>\n")

    md_file.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[INFO] Markdown report generated: {md_file}")

if __name__ == "__main__":
    generate_md(CSV_FILE, MD_FILE, top_k=5)
