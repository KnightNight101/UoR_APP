import subprocess
from pathlib import Path

class DeepseekR1Interface:
    """
    Interface to Deepseek R1 8b model via Ollama local model runner.
    """

    def __init__(self, model_name="deepseek_r1_8b"):
        self.model_name = model_name
        if not Path("C:/Program Files/Ollama/ollama.exe").exists():
            raise EnvironmentError("Ollama executable not found. Install Ollama first.")

    def generate_response(self, prompt: str) -> str:
        """
        Run the prompt on Deepseek via Ollama CLI.
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
            print("Error running Deepseek via Ollama:", e)
            return ""
