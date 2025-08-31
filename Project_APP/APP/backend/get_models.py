# get_ollama_models.py
import subprocess
import shutil
import sys
from pathlib import Path

# --------------------------
# Configuration
# --------------------------
MODELS = ["tinyllama:1.1b", "deepseek-r1:8b", "deepseek-r1:32b"]
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)
OLLAMA_EXECUTABLE = shutil.which("ollama") or Path("C:/Program Files/Ollama/ollama.exe")

# --------------------------
# Utility Functions
# --------------------------
def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"Command failed with code {result.returncode}")
    return result.stdout.strip()

def check_ollama():
    """Ensure Ollama is available."""
    if OLLAMA_EXECUTABLE and Path(OLLAMA_EXECUTABLE).exists():
        print(f"Ollama found at: {OLLAMA_EXECUTABLE}")
        return str(OLLAMA_EXECUTABLE)
    print("Ollama not found. Please install Ollama from https://ollama.com/download and ensure it is in PATH.")
    sys.exit(1)

def model_exists(model_name):
    """Check if Ollama model is already pulled."""
    try:
        output = run_cmd([OLLAMA_EXECUTABLE, "list"])
        return model_name in output
    except Exception as e:
        print(f"Failed to check existing models: {e}")
        return False

def pull_model(model_name):
    """Pull model via Ollama."""
    if model_exists(model_name):
        print(f"Model already exists: {model_name}")
    else:
        print(f"Pulling model: {model_name}")
        run_cmd([OLLAMA_EXECUTABLE, "pull", model_name])
        print(f"Successfully pulled {model_name}")

# --------------------------
# Main
# --------------------------
def main():
    ollama_path = check_ollama()
    for model in MODELS:
        pull_model(model)
    print("All models are ready!")

if __name__ == "__main__":
    main()
