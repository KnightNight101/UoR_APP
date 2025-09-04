import subprocess

MODEL = "deepseek-r1:8b"
PROMPT = "hello world"

OLLAMA_PATH = r"C:\Users\KnightNight101\AppData\Local\Programs\Ollama\ollama.exe"

print("[INFO] Sending prompt to Ollama...")
result = subprocess.run(
    [OLLAMA_PATH, "run", MODEL, PROMPT],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="ignore"
)

print("[INFO] Return code:", result.returncode)
print("[STDOUT]")
print(result.stdout)
print("[STDERR]")
print(result.stderr)
