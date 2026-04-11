# Evaluation Harness

## Usage
```bash
cd oracle-forge
python eval/harness.py --dataset yelp --queries 1,2,3,4,5,6,7 --llm gemini-2.5-flash
```

## Score Log
`score_log.jsonl` — one entry per run, tracks pass@1 progression.

## Baseline — April 11, 2026
- Dataset: yelp (7 queries)
- Model: gemini-2.5-flash
- Score: 0/7 = 0% pass@1
- Main failures: no_tool_call (4), max_iterations (2), wrong answer (1)
