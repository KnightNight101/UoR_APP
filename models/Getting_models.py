import subprocess
import shutil
from pathlib import Path
import sys

# -------------------------------
# Configuration
# -------------------------------
MODELS = [
    "tinyllama:1.1b",
    "deepseek-r1:8b",
    "deepseek-r1:32b"
]

# -------------------------------
# Helper Functions
# -------------------------------
def find_ollama():
    """
    Attempts to find the Ollama executable.
    Returns the path if found, else None.
    """
    # Check default Windows location
    default_path = Path("C:/Program Files/Ollama/ollama.exe")
    if default_path.exists():
        return default_path

    # Check in PATH
    path_in_system = shutil.which("ollama")
    if path_in_system:
        return Path(path_in_system)

    return None

def pull_model(ollama_path: Path, model_name: str):
    print(f"Pulling model {model_name}...")
    try:
        result = subprocess.run([str(ollama_path), "pull", model_name],
                                capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"Model {model_name} pulled successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error pulling model {model_name}:")
        print(e.stderr)

# -------------------------------
# Main
# -------------------------------
def main():
    ollama_path = find_ollama()
    if not ollama_path:
        print("Ollama executable not found.")
        print("Please install Ollama manually from https://ollama.com/download and ensure it is in PATH or in 'C:/Program Files/Ollama/'.")
        sys.exit(1)

    print(f"Ollama found at: {ollama_path}\n")

    for model in MODELS:
        pull_model(ollama_path, model)

if __name__ == "__main__":
    main()
