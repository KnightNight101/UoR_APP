#!/usr/bin/env python3
"""
Basic Ollama connectivity + model reasoning test

- Sends 5 prompts to a local Deepseek model.
- Captures both "thinking" trace and final output.
- Prints live to the terminal as it streams.
- Writes full logs to Test_Results/basic_test_output.txt
"""

import subprocess
from pathlib import Path
import sys

# -------------------
# Config
# -------------------
MODEL = "deepseek-r1:8b"
OLLAMA_PATH = r"C:\Users\KnightNight101\AppData\Local\Programs\Ollama\ollama.exe"
OUTPUT_FILE = Path(__file__).parent / "Test_Results" / "basic_test_output.txt"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

PROMPTS = [
    "hello world",
    "What are Asimov's three laws of robotics?",
    "Why is the sky blue?",
    "Tell me something interesting.",
    "How do I solve the quadratic formula?"
]

# -------------------
# Helpers
# -------------------
def run_prompt(prompt: str) -> str:
    """
    Run a single prompt through Ollama, stream stdout live,
    and return the full collected output.
    """
    cmd = [OLLAMA_PATH, "run", MODEL, prompt]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    output_lines = []
    print(f"\n[INFO] Prompt: {prompt}")
    print("-" * 60)

    for line in process.stdout:
        sys.stdout.write(line)   # live print to terminal
        sys.stdout.flush()
        output_lines.append(line)

    process.wait()
    print("-" * 60)
    return "".join(output_lines)

# -------------------
# Main
# -------------------
def main():
    all_results = []
    for i, prompt in enumerate(PROMPTS, start=1):
        result = run_prompt(prompt)
        all_results.append(f"\n### Prompt {i}: {prompt}\n{result}\n")

    OUTPUT_FILE.write_text("\n".join(all_results), encoding="utf-8")
    print(f"\n[INFO] All results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
