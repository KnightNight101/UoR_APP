# DeepSeek R1 8B - Commit Summary Benchmark Report

## Full Test Results

| model          | test_type      |   accuracy |   precision |   recall |   f1_score |    time_s |
|:---------------|:---------------|-----------:|------------:|---------:|-----------:|----------:|
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 64.2068   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 42.6864   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 30.0737   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 42.3154   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 41.8298   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 44.7872   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 46.4307   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 42.7415   |
| deepseek-r1:8b | Commit Summary |   1        |  1          | 1        | 1          | 55.2842   |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0574713  | 1        | 0.108696   |  2.54953  |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0555556  | 1        | 0.105263   |  1.8756   |
| tinyllama:1.1b | Sprint Planner |   1        |  0.048      | 1        | 0.0916031  |  4.24457  |
| tinyllama:1.1b | Eisenhower     |   1        |  0.0344828  | 1        | 0.0666667  |  3.51377  |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0294118  | 1        | 0.0571429  |  2.7896   |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0294118  | 1        | 0.0571429  |  5.08549  |
| tinyllama:1.1b | Sprint Planner |   0.75     |  0.027027   | 0.75     | 0.0521739  |  3.1124   |
| tinyllama:1.1b | Sprint Planner |   1        |  0.026738   | 1        | 0.0520833  |  6.27021  |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0266667  | 1        | 0.0519481  |  3.33101  |
| tinyllama:1.1b | Eisenhower     |   0.666667 |  0.0258065  | 0.666667 | 0.0496894  |  2.9067   |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0252525  | 1        | 0.0492611  |  5.80204  |
| tinyllama:1.1b | Eisenhower     |   0.833333 |  0.0239234  | 0.833333 | 0.0465116  |  4.00044  |
| tinyllama:1.1b | Commit Summary |   1        |  0.0232558  | 1        | 0.0454545  |  1.07664  |
| tinyllama:1.1b | Eisenhower     |   0.833333 |  0.0218341  | 0.833333 | 0.0425532  |  5.12779  |
| tinyllama:1.1b | Sprint Planner |   0.666667 |  0.0217391  | 0.666667 | 0.0421053  |  3.81581  |
| tinyllama:1.1b | Commit Summary |   1        |  0.0212766  | 1        | 0.0416667  |  1.03511  |
| tinyllama:1.1b | Eisenhower     |   1        |  0.020339   | 1        | 0.0398671  |  4.98569  |
| tinyllama:1.1b | Sprint Planner |   1        |  0.0178571  | 1        | 0.0350877  |  4.85584  |
| tinyllama:1.1b | Eisenhower     |   0.666667 |  0.0140351  | 0.666667 | 0.0274914  |  5.5483   |
| tinyllama:1.1b | Eisenhower     |   0.6      |  0.0133929  | 0.6      | 0.0262009  |  4.09678  |
| tinyllama:1.1b | Sprint Planner |   0.25     |  0.0135135  | 0.25     | 0.025641   |  1.91099  |
| tinyllama:1.1b | Eisenhower     |   0.666667 |  0.0130719  | 0.666667 | 0.025641   |  2.81755  |
| tinyllama:1.1b | Sprint Planner |   0.5      |  0.0120482  | 0.5      | 0.0235294  |  5.80239  |
| tinyllama:1.1b | Sprint Planner |   0.5      |  0.0108696  | 0.5      | 0.0212766  |  5.74164  |
| tinyllama:1.1b | Commit Summary |   1        |  0.0106383  | 1        | 0.0210526  |  1.70038  |
| tinyllama:1.1b | Eisenhower     |   0.333333 |  0.0100503  | 0.333333 | 0.0195122  |  3.26919  |
| tinyllama:1.1b | Sprint Planner |   0.8      |  0.00917431 | 0.8      | 0.0181406  | 10.0189   |
| tinyllama:1.1b | Eisenhower     |   0.5      |  0.00587084 | 0.5      | 0.0116054  | 10.7237   |
| tinyllama:1.1b | Commit Summary |   1        |  0.00396825 | 1        | 0.00790514 |  5.65994  |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  2.32472  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  4.20582  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  7.34575  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  5.85588  |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  1.25719  |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  0.561472 |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  0.677793 |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  1.3351   |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  0.857977 |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  0.593059 |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  1.24578  |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  0.513068 |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  0.82516  |
| tinyllama:1.1b | Commit Summary |   0        |  0          | 0        | 0          |  1.3103   |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  2.96438  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  3.78722  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  3.77916  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  7.04562  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  4.83018  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  4.04296  |
| tinyllama:1.1b | Sprint Planner |   0        |  0          | 0        | 0          |  1.68041  |
| tinyllama:1.1b | Eisenhower     |   0        |  0          | 0        | 0          |  1.80875  |
| tinyllama:1.1b | Sprint Planner |   0        |  0          | 0        | 0          |  7.41251  |
| tinyllama:1.1b | Sprint Planner |   0        |  0          | 0        | 0          |  2.57457  |
| tinyllama:1.1b | Sprint Planner |   0        |  0          | 0        | 0          |  1.94418  |
| tinyllama:1.1b | Sprint Planner |   0        |  0          | 0        | 0          |  2.58781  |
| deepseek-r1:8b | Commit Summary |   0        |  0          | 0        | 0          | 39.2053   |

## Top 5 Test Cases

| model          | test_type      |   accuracy |   precision |   recall |   f1_score |   time_s |
|:---------------|:---------------|-----------:|------------:|---------:|-----------:|---------:|
| deepseek-r1:8b | Commit Summary |          1 |           1 |        1 |          1 |  64.2068 |
| deepseek-r1:8b | Commit Summary |          1 |           1 |        1 |          1 |  42.6864 |
| deepseek-r1:8b | Commit Summary |          1 |           1 |        1 |          1 |  30.0737 |
| deepseek-r1:8b | Commit Summary |          1 |           1 |        1 |          1 |  42.3154 |
| deepseek-r1:8b | Commit Summary |          1 |           1 |        1 |          1 |  41.8298 |

## Worst 5 Test Cases

| model          | test_type      |   accuracy |   precision |   recall |   f1_score |   time_s |
|:---------------|:---------------|-----------:|------------:|---------:|-----------:|---------:|
| tinyllama:1.1b | Sprint Planner |          0 |           0 |        0 |          0 |  7.41251 |
| tinyllama:1.1b | Sprint Planner |          0 |           0 |        0 |          0 |  2.57457 |
| tinyllama:1.1b | Sprint Planner |          0 |           0 |        0 |          0 |  1.94418 |
| tinyllama:1.1b | Sprint Planner |          0 |           0 |        0 |          0 |  2.58781 |
| deepseek-r1:8b | Commit Summary |          0 |           0 |        0 |          0 | 39.2053  |

## accuracy per Test Case

```mermaid
gantt
    title accuracy per Test Case
    task64 :done, 0, 1.00
    task57 :done, 0, 1.00
    task56 :done, 0, 1.00
    task62 :done, 0, 1.00
    task63 :done, 0, 1.00
    task61 :done, 0, 1.00
    task59 :done, 0, 1.00
    task58 :done, 0, 1.00
    task55 :done, 0, 1.00
    task45 :done, 0, 1.00
    task40 :done, 0, 1.00
    task50 :done, 0, 1.00
    task29 :done, 0, 1.00
    task35 :done, 0, 1.00
    task47 :done, 0, 1.00
    task49 :done, 0, 0.75
    task43 :done, 0, 1.00
    task41 :done, 0, 1.00
    task24 :done, 0, 0.67
    task37 :done, 0, 1.00
    task15 :done, 0, 0.83
    task9 :done, 0, 1.00
    task26 :done, 0, 0.83
    task51 :done, 0, 0.67
    task6 :done, 0, 1.00
    task16 :done, 0, 1.00
    task52 :done, 0, 1.00
    task20 :done, 0, 0.67
    task22 :done, 0, 0.60
    task48 :done, 0, 0.25
    task19 :done, 0, 0.67
    task38 :done, 0, 0.50
    task36 :done, 0, 0.50
    task3 :done, 0, 1.00
    task25 :done, 0, 0.33
    task42 :done, 0, 0.80
    task33 :done, 0, 0.50
    task12 :done, 0, 1.00
    task0 :done, 0, 0.00
    task30 :done, 0, 0.00
    task31 :done, 0, 0.00
    task32 :done, 0, 0.00
    task7 :done, 0, 0.00
    task5 :done, 0, 0.00
    task4 :done, 0, 0.00
    task11 :done, 0, 0.00
    task10 :done, 0, 0.00
    task14 :done, 0, 0.00
    task13 :done, 0, 0.00
    task1 :done, 0, 0.00
    task2 :done, 0, 0.00
    task8 :done, 0, 0.00
    task28 :done, 0, 0.00
    task27 :done, 0, 0.00
    task18 :done, 0, 0.00
    task21 :done, 0, 0.00
    task23 :done, 0, 0.00
    task17 :done, 0, 0.00
    task44 :done, 0, 0.00
    task34 :done, 0, 0.00
    task39 :done, 0, 0.00
    task46 :done, 0, 0.00
    task54 :done, 0, 0.00
    task53 :done, 0, 0.00
    task60 :done, 0, 0.00
```

## precision per Test Case

```mermaid
gantt
    title precision per Test Case
    task64 :done, 0, 1.00
    task57 :done, 0, 1.00
    task56 :done, 0, 1.00
    task62 :done, 0, 1.00
    task63 :done, 0, 1.00
    task61 :done, 0, 1.00
    task59 :done, 0, 1.00
    task58 :done, 0, 1.00
    task55 :done, 0, 1.00
    task45 :done, 0, 0.06
    task40 :done, 0, 0.06
    task50 :done, 0, 0.05
    task29 :done, 0, 0.03
    task35 :done, 0, 0.03
    task47 :done, 0, 0.03
    task49 :done, 0, 0.03
    task43 :done, 0, 0.03
    task41 :done, 0, 0.03
    task24 :done, 0, 0.03
    task37 :done, 0, 0.03
    task15 :done, 0, 0.02
    task9 :done, 0, 0.02
    task26 :done, 0, 0.02
    task51 :done, 0, 0.02
    task6 :done, 0, 0.02
    task16 :done, 0, 0.02
    task52 :done, 0, 0.02
    task20 :done, 0, 0.01
    task22 :done, 0, 0.01
    task48 :done, 0, 0.01
    task19 :done, 0, 0.01
    task38 :done, 0, 0.01
    task36 :done, 0, 0.01
    task3 :done, 0, 0.01
    task25 :done, 0, 0.01
    task42 :done, 0, 0.01
    task33 :done, 0, 0.01
    task12 :done, 0, 0.00
    task0 :done, 0, 0.00
    task30 :done, 0, 0.00
    task31 :done, 0, 0.00
    task32 :done, 0, 0.00
    task7 :done, 0, 0.00
    task5 :done, 0, 0.00
    task4 :done, 0, 0.00
    task11 :done, 0, 0.00
    task10 :done, 0, 0.00
    task14 :done, 0, 0.00
    task13 :done, 0, 0.00
    task1 :done, 0, 0.00
    task2 :done, 0, 0.00
    task8 :done, 0, 0.00
    task28 :done, 0, 0.00
    task27 :done, 0, 0.00
    task18 :done, 0, 0.00
    task21 :done, 0, 0.00
    task23 :done, 0, 0.00
    task17 :done, 0, 0.00
    task44 :done, 0, 0.00
    task34 :done, 0, 0.00
    task39 :done, 0, 0.00
    task46 :done, 0, 0.00
    task54 :done, 0, 0.00
    task53 :done, 0, 0.00
    task60 :done, 0, 0.00
```

## recall per Test Case

```mermaid
gantt
    title recall per Test Case
    task64 :done, 0, 1.00
    task57 :done, 0, 1.00
    task56 :done, 0, 1.00
    task62 :done, 0, 1.00
    task63 :done, 0, 1.00
    task61 :done, 0, 1.00
    task59 :done, 0, 1.00
    task58 :done, 0, 1.00
    task55 :done, 0, 1.00
    task45 :done, 0, 1.00
    task40 :done, 0, 1.00
    task50 :done, 0, 1.00
    task29 :done, 0, 1.00
    task35 :done, 0, 1.00
    task47 :done, 0, 1.00
    task49 :done, 0, 0.75
    task43 :done, 0, 1.00
    task41 :done, 0, 1.00
    task24 :done, 0, 0.67
    task37 :done, 0, 1.00
    task15 :done, 0, 0.83
    task9 :done, 0, 1.00
    task26 :done, 0, 0.83
    task51 :done, 0, 0.67
    task6 :done, 0, 1.00
    task16 :done, 0, 1.00
    task52 :done, 0, 1.00
    task20 :done, 0, 0.67
    task22 :done, 0, 0.60
    task48 :done, 0, 0.25
    task19 :done, 0, 0.67
    task38 :done, 0, 0.50
    task36 :done, 0, 0.50
    task3 :done, 0, 1.00
    task25 :done, 0, 0.33
    task42 :done, 0, 0.80
    task33 :done, 0, 0.50
    task12 :done, 0, 1.00
    task0 :done, 0, 0.00
    task30 :done, 0, 0.00
    task31 :done, 0, 0.00
    task32 :done, 0, 0.00
    task7 :done, 0, 0.00
    task5 :done, 0, 0.00
    task4 :done, 0, 0.00
    task11 :done, 0, 0.00
    task10 :done, 0, 0.00
    task14 :done, 0, 0.00
    task13 :done, 0, 0.00
    task1 :done, 0, 0.00
    task2 :done, 0, 0.00
    task8 :done, 0, 0.00
    task28 :done, 0, 0.00
    task27 :done, 0, 0.00
    task18 :done, 0, 0.00
    task21 :done, 0, 0.00
    task23 :done, 0, 0.00
    task17 :done, 0, 0.00
    task44 :done, 0, 0.00
    task34 :done, 0, 0.00
    task39 :done, 0, 0.00
    task46 :done, 0, 0.00
    task54 :done, 0, 0.00
    task53 :done, 0, 0.00
    task60 :done, 0, 0.00
```

## f1_score per Test Case

```mermaid
gantt
    title f1_score per Test Case
    task64 :done, 0, 1.00
    task57 :done, 0, 1.00
    task56 :done, 0, 1.00
    task62 :done, 0, 1.00
    task63 :done, 0, 1.00
    task61 :done, 0, 1.00
    task59 :done, 0, 1.00
    task58 :done, 0, 1.00
    task55 :done, 0, 1.00
    task45 :done, 0, 0.11
    task40 :done, 0, 0.11
    task50 :done, 0, 0.09
    task29 :done, 0, 0.07
    task35 :done, 0, 0.06
    task47 :done, 0, 0.06
    task49 :done, 0, 0.05
    task43 :done, 0, 0.05
    task41 :done, 0, 0.05
    task24 :done, 0, 0.05
    task37 :done, 0, 0.05
    task15 :done, 0, 0.05
    task9 :done, 0, 0.05
    task26 :done, 0, 0.04
    task51 :done, 0, 0.04
    task6 :done, 0, 0.04
    task16 :done, 0, 0.04
    task52 :done, 0, 0.04
    task20 :done, 0, 0.03
    task22 :done, 0, 0.03
    task48 :done, 0, 0.03
    task19 :done, 0, 0.03
    task38 :done, 0, 0.02
    task36 :done, 0, 0.02
    task3 :done, 0, 0.02
    task25 :done, 0, 0.02
    task42 :done, 0, 0.02
    task33 :done, 0, 0.01
    task12 :done, 0, 0.01
    task0 :done, 0, 0.00
    task30 :done, 0, 0.00
    task31 :done, 0, 0.00
    task32 :done, 0, 0.00
    task7 :done, 0, 0.00
    task5 :done, 0, 0.00
    task4 :done, 0, 0.00
    task11 :done, 0, 0.00
    task10 :done, 0, 0.00
    task14 :done, 0, 0.00
    task13 :done, 0, 0.00
    task1 :done, 0, 0.00
    task2 :done, 0, 0.00
    task8 :done, 0, 0.00
    task28 :done, 0, 0.00
    task27 :done, 0, 0.00
    task18 :done, 0, 0.00
    task21 :done, 0, 0.00
    task23 :done, 0, 0.00
    task17 :done, 0, 0.00
    task44 :done, 0, 0.00
    task34 :done, 0, 0.00
    task39 :done, 0, 0.00
    task46 :done, 0, 0.00
    task54 :done, 0, 0.00
    task53 :done, 0, 0.00
    task60 :done, 0, 0.00
```


```mermaid
gantt
    title Time Taken per Test Case (s)
    task64 :done, 0, 64.21
    task57 :done, 0, 42.69
    task56 :done, 0, 30.07
    task62 :done, 0, 42.32
    task63 :done, 0, 41.83
    task61 :done, 0, 44.79
    task59 :done, 0, 46.43
    task58 :done, 0, 42.74
    task55 :done, 0, 55.28
    task45 :done, 0, 2.55
    task40 :done, 0, 1.88
    task50 :done, 0, 4.24
    task29 :done, 0, 3.51
    task35 :done, 0, 2.79
    task47 :done, 0, 5.09
    task49 :done, 0, 3.11
    task43 :done, 0, 6.27
    task41 :done, 0, 3.33
    task24 :done, 0, 2.91
    task37 :done, 0, 5.80
    task15 :done, 0, 4.00
    task9 :done, 0, 1.08
    task26 :done, 0, 5.13
    task51 :done, 0, 3.82
    task6 :done, 0, 1.04
    task16 :done, 0, 4.99
    task52 :done, 0, 4.86
    task20 :done, 0, 5.55
    task22 :done, 0, 4.10
    task48 :done, 0, 1.91
    task19 :done, 0, 2.82
    task38 :done, 0, 5.80
    task36 :done, 0, 5.74
    task3 :done, 0, 1.70
    task25 :done, 0, 3.27
    task42 :done, 0, 10.02
    task33 :done, 0, 10.72
    task12 :done, 0, 5.66
    task0 :done, 0, 2.32
    task30 :done, 0, 4.21
    task31 :done, 0, 7.35
    task32 :done, 0, 5.86
    task7 :done, 0, 1.26
    task5 :done, 0, 0.56
    task4 :done, 0, 0.68
    task11 :done, 0, 1.34
    task10 :done, 0, 0.86
    task14 :done, 0, 0.59
    task13 :done, 0, 1.25
    task1 :done, 0, 0.51
    task2 :done, 0, 0.83
    task8 :done, 0, 1.31
    task28 :done, 0, 2.96
    task27 :done, 0, 3.79
    task18 :done, 0, 3.78
    task21 :done, 0, 7.05
    task23 :done, 0, 4.83
    task17 :done, 0, 4.04
    task44 :done, 0, 1.68
    task34 :done, 0, 1.81
    task39 :done, 0, 7.41
    task46 :done, 0, 2.57
    task54 :done, 0, 1.94
    task53 :done, 0, 2.59
    task60 :done, 0, 39.21
```
