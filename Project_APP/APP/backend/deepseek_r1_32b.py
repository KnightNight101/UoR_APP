import subprocess
from pathlib import Path

class DeepSeekR1_32B:
    """
    Interface to DeepSeek R1 32B via Ollama local model runner.
    """

    def __init__(self, model_name="deepseek-r1:32b"):
        self.model_name = model_name
        if not Path("C:/Program Files/Ollama/ollama.exe").exists():
            raise EnvironmentError("Ollama executable not found. Install Ollama first.")

    def query_llm(self, prompt: str) -> str:
        """
        Run the prompt on DeepSeek R1 32B via Ollama CLI.
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
            print("Error running DeepSeek R1 32B via Ollama:", e)
            return ""
