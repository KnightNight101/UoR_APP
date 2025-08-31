# LLM Benchmark Report

Latest source file: `benchmark_results_2025-08-31_14-08-09.csv`

## Model Performance Summary

| Model | Commit Similarity (avg) | Eisenhower Accuracy (avg) | Eisenhower Precision (avg) | Sprint Valid % |
|-------|--------------------------|----------------------------|-----------------------------|----------------|
| TinyLlama | 0.156 | 0.362 | 0.000 | 100.0% |
| Deepseek | 0.158 | 0.362 | 0.000 | 100.0% |

## Performance Trends Over Time (by model)

### Commit Similarity
```mermaid
graph LR
    "2025-08-31 TinyLlama: 0.156"
    "2025-08-31 Deepseek: 0.158"
```

### Eisenhower Accuracy
```mermaid
graph LR
    "2025-08-31 TinyLlama: 0.362"
    "2025-08-31 Deepseek: 0.362"
```

### Sprint Valid Plans (%)
```mermaid
graph LR
    "2025-08-31 TinyLlama: 100.0%"
    "2025-08-31 Deepseek: 100.0%"
```

## Per-Testcase Breakdown (Model Comparisons)

### Commit Summary

| Test Case | Model | Output (truncated) | Metric(s) |
|-----------|-------|---------------------|-----------|
| case_1 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.169 |
| case_2 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.189 |
| case_3 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.198 |
| case_4 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.141 |
| case_5 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.153 |
| case_6 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.106 |
| case_7 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.187 |
| case_8 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.137 |
| case_9 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.180 |
| case_10 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.083 |
| case_11 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.131 |
| case_12 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.180 |
| case_13 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.169 |
| case_14 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.083 |
| case_15 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.137 |
| case_16 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.171 |
| case_17 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.133 |
| case_18 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.161 |
| case_19 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.205 |
| case_20 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.140 |
| case_21 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.212 |
| case_22 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.151 |
| case_23 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.181 |
| case_24 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.189 |
| case_25 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.151 |
| case_26 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.162 |
| case_27 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.148 |
| case_28 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.115 |
| case_29 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.171 |
| case_30 | TinyLlama | [LLM STUB RESPONSE] Summarize the following code changes as a git commit message... | similarity=0.150 |
| case_1 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.190 |
| case_2 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.178 |
| case_3 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.220 |
| case_4 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.133 |
| case_5 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.144 |
| case_6 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.144 |
| case_7 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.176 |
| case_8 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.140 |
| case_9 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.169 |
| case_10 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.078 |
| case_11 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.144 |
| case_12 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.169 |
| case_13 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.190 |
| case_14 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.078 |
| case_15 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.140 |
| case_16 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.162 |
| case_17 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.125 |
| case_18 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.151 |
| case_19 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.192 |
| case_20 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.132 |
| case_21 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.199 |
| case_22 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.175 |
| case_23 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.205 |
| case_24 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.176 |
| case_25 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.175 |
| case_26 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.174 |
| case_27 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.160 |
| case_28 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.108 |
| case_29 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.162 |
| case_30 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Summarize the following code changes as a git com... | similarity=0.163 |

### Eisenhower

| Test Case | Model | Output (truncated) | Metric(s) |
|-----------|-------|---------------------|-----------|
| case_1 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_2 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_3 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.000, prec=0.000 |
| case_4 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_5 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_6 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.000, prec=0.000 |
| case_7 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_8 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_9 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_10 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_11 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_12 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_13 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_14 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.500, prec=0.000 |
| case_15 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_16 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.750, prec=0.000 |
| case_17 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_18 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.750, prec=0.000 |
| case_19 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_20 | TinyLlama | [LLM STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do First, Schedu... | acc=0.250, prec=0.000 |
| case_1 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_2 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_3 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.000, prec=0.000 |
| case_4 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_5 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_6 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.000, prec=0.000 |
| case_7 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_8 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_9 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_10 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_11 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_12 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_13 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_14 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.500, prec=0.000 |
| case_15 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_16 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.750, prec=0.000 |
| case_17 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_18 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.750, prec=0.000 |
| case_19 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |
| case_20 | Deepseek | [Deepseek R1 8b STUB RESPONSE] Sort these tasks into an Eisenhower matrix (Do Fi... | acc=0.250, prec=0.000 |

### Sprint Planning

| Test Case | Model | Output (truncated) | Metric(s) |
|-----------|-------|---------------------|-----------|
| case_1 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_2 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_3 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_4 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_5 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_6 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_7 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_8 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_9 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_10 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_11 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_12 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_13 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_14 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_15 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_16 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_17 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_18 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_19 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_20 | TinyLlama | [LLM STUB RESPONSE]  Plan a 2-week agile sprint for the following team and tasks... | valid=1 |
| case_1 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_2 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_3 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_4 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_5 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_6 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_7 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_8 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_9 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_10 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_11 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_12 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_13 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_14 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_15 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_16 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_17 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_18 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_19 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |
| case_20 | Deepseek | [Deepseek R1 8b STUB RESPONSE]  Plan a 2-week agile sprint for the following tea... | valid=1 |

## Model Disagreements

No disagreements found between models.

