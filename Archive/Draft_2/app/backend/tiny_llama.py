import subprocess
from pathlib import Path

class TinyLlamaPlanner:
    """
    Interface to TinyLlama 1.1b via Ollama local model runner.
    """

    def __init__(self, model_name="tinyllama"):
        self.model_name = model_name
        # Ensure Ollama is installed
        if not Path("C:/Program Files/Ollama/ollama.exe").exists():
            raise EnvironmentError("Ollama executable not found. Install Ollama first.")

    def query_llm(self, prompt: str) -> str:
        """
        Run the prompt on TinyLlama via Ollama CLI.
        """
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name, "--prompt", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print("Error running TinyLlama via Ollama:", e)
            return ""
