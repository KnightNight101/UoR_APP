import subprocess
import json
import time
import csv
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import single_meteor_score
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util
import Levenshtein

# -----------------------
# CONFIGURATION
# -----------------------
OLLAMA_PATH = r"C:\Users\KnightNight101\AppData\Local\Programs\Ollama\ollama.exe"
MODEL = "deepseek-r1:8b"
TIMEOUT = 600  # seconds
OUTPUT_CSV = r"C:\Users\KnightNight101\UoR_APP\commit_summary_results.csv"

# Initialize SBERT model for semantic similarity
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------
# TEST CASES
# -----------------------
test_cases = [
    {"diff": "Added function to calculate factorial", "reference_commit": "Add factorial function"},
    {"diff": "Fixed bug in user authentication logic", "reference_commit": "Fix authentication bug"},
    {"diff": "Refactored database connection module", "reference_commit": "Refactor DB connection module"},
    {"diff": "Updated README with installation instructions", "reference_commit": "Update README with install guide"},
    {"diff": "Removed deprecated login API endpoints", "reference_commit": "Remove deprecated login endpoints"}
]

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def run_ollama(prompt):
    start_time = time.time()
    try:
        proc = subprocess.run(
            [OLLAMA_PATH, "run", MODEL, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=TIMEOUT
        )
        elapsed = time.time() - start_time
        return proc.stdout.strip(), proc.stderr.strip(), elapsed
    except subprocess.TimeoutExpired:
        return "", "[TIMEOUT]", TIMEOUT

def evaluate_metrics(reference, hypothesis, thoughts):
    reference_tokens = word_tokenize(reference.lower())
    hypothesis_tokens = word_tokenize(hypothesis.lower())

    try:
        bleu = sentence_bleu([reference_tokens], hypothesis_tokens) * 100
    except:
        bleu = 0.0

    try:
        meteor = single_meteor_score(reference_tokens, hypothesis_tokens)
    except:
        meteor = 0.0

    rouge = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    rouge_l = rouge.score(reference, hypothesis)['rougeL'].fmeasure

    try:
        emb_ref = sbert_model.encode(reference, convert_to_tensor=True)
        emb_hyp = sbert_model.encode(hypothesis, convert_to_tensor=True)
        sem_sim = util.cos_sim(emb_ref, emb_hyp).item()
    except:
        sem_sim = 0.0

    edit_dist = Levenshtein.distance(reference, hypothesis)
    exact_match = int(reference.strip() == hypothesis.strip())
    instruction_adherence = int(thoughts.strip() == "")

    return {
        "BLEU": bleu,
        "METEOR": meteor,
        "ROUGE_L": rouge_l,
        "SemanticSim": sem_sim,
        "EditDist": edit_dist,
        "ExactMatch": exact_match,
        "InstructionAdherence": instruction_adherence
    }

# -----------------------
# MAIN LOOP
# -----------------------
results = []

for idx, case in enumerate(test_cases, start=1):
    print(f"[INFO] Test case {idx}")
    prompt = f"""You are a git commit summarizer.
Read the following diff and provide ONLY a concise commit message.
DO NOT provide explanations or reasoning.
Provide your commit message in JSON format: {{\"commit_msg\": \"...\", \"thoughts\": \"...\"}}

DIFF:
{case['diff']}"""

    stdout, stderr, elapsed = run_ollama(prompt)

    valid_json = True
    commit_msg = ""
    thoughts = ""

    if stdout:
        try:
            data = json.loads(stdout)
            commit_msg = data.get("commit_msg", "")
            thoughts = data.get("thoughts", "")
        except json.JSONDecodeError:
            valid_json = False
            commit_msg = stdout
            thoughts = ""
    else:
        valid_json = False
        commit_msg = ""
        thoughts = ""

    metrics = evaluate_metrics(case['reference_commit'], commit_msg, thoughts)

    row = {
        "test_case": idx,
        "diff": case['diff'],
        "reference_commit": case['reference_commit'],
        "commit_msg": commit_msg,
        "thoughts": thoughts,
        "valid_json": valid_json,
        "time_total": elapsed,
        **metrics
    }

    results.append(row)
    print(f"[RESULT] {row}\n")

# -----------------------
# SAVE CSV
# -----------------------
csv_columns = list(results[0].keys())
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_columns)
    writer.writeheader()
    writer.writerows(results)

print(f"[INFO] Results saved to {OUTPUT_CSV}")
