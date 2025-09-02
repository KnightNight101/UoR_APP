# LLM Benchmark Report

## Model Performance Summary

| Model | Commit Summary Accuracy | Commit Summary Precision | Commit Summary Recall | Commit Summary F1_score | Eisenhower Accuracy | Eisenhower Precision | Eisenhower Recall | Eisenhower F1_score | Sprint Planner Accuracy | Sprint Planner Precision | Sprint Planner Recall | Sprint Planner F1_score | Avg Time (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tinyllama:1.1b | 0.267 | 0.004 | 0.267 | 0.008 | 0.355 | 0.009 | 0.355 | 0.018 | 0.623 | 0.021 | 0.623 | 0.040 | 3.58 |

## Model Benchmark Gantt Diagram
```mermaid
gantt
    title LLM Task Execution Times
    dateFormat  HH:mm:ss
    axisFormat  %H:%M:%S
    Commit_Summary_0 :done, 0, 2.32
    Commit_Summary_2 :done, 2, 0.51
    Commit_Summary_2 :done, 2, 0.83
    Commit_Summary_3 :done, 3, 1.70
    Commit_Summary_5 :done, 5, 0.68
    Commit_Summary_6 :done, 6, 0.56
    Commit_Summary_6 :done, 6, 1.04
    Commit_Summary_7 :done, 7, 1.26
    Commit_Summary_8 :done, 8, 1.31
    Commit_Summary_10 :done, 10, 1.08
    Commit_Summary_11 :done, 11, 0.86
    Commit_Summary_12 :done, 12, 1.34
    Commit_Summary_13 :done, 13, 5.66
    Commit_Summary_19 :done, 19, 1.25
    Commit_Summary_20 :done, 20, 0.59
    Eisenhower_20 :done, 20, 4.00
    Eisenhower_24 :done, 24, 4.99
    Eisenhower_29 :done, 29, 4.04
    Eisenhower_34 :done, 34, 3.78
    Eisenhower_37 :done, 37, 2.82
    Eisenhower_40 :done, 40, 5.55
    Eisenhower_46 :done, 46, 7.05
    Eisenhower_53 :done, 53, 4.10
    Eisenhower_57 :done, 57, 4.83
    Eisenhower_62 :done, 62, 2.91
    Eisenhower_65 :done, 65, 3.27
    Eisenhower_68 :done, 68, 5.13
    Eisenhower_73 :done, 73, 3.79
    Eisenhower_77 :done, 77, 2.96
    Eisenhower_80 :done, 80, 3.51
    Eisenhower_83 :done, 83, 4.21
    Eisenhower_87 :done, 87, 7.35
    Eisenhower_95 :done, 95, 5.86
    Eisenhower_101 :done, 101, 10.72
    Eisenhower_111 :done, 111, 1.81
    Sprint_Planner_113 :done, 113, 2.79
    Sprint_Planner_116 :done, 116, 5.74
    Sprint_Planner_122 :done, 122, 5.80
    Sprint_Planner_127 :done, 127, 5.80
    Sprint_Planner_133 :done, 133, 7.41
    Sprint_Planner_141 :done, 141, 1.88
    Sprint_Planner_143 :done, 143, 3.33
    Sprint_Planner_146 :done, 146, 10.02
    Sprint_Planner_156 :done, 156, 6.27
    Sprint_Planner_162 :done, 162, 1.68
    Sprint_Planner_164 :done, 164, 2.55
    Sprint_Planner_166 :done, 166, 2.57
    Sprint_Planner_169 :done, 169, 5.09
    Sprint_Planner_174 :done, 174, 1.91
    Sprint_Planner_176 :done, 176, 3.11
    Sprint_Planner_179 :done, 179, 4.24
    Sprint_Planner_183 :done, 183, 3.82
    Sprint_Planner_187 :done, 187, 4.86
    Sprint_Planner_192 :done, 192, 2.59
    Sprint_Planner_195 :done, 195, 1.94
```
