# KB v2 - pass@1 Scoring Explanation

## What pass@1 means in DAB

In DataAgentBench (DAB), pass@1 is the first-answer correctness rate. Each query is scored only on the agent's first submitted response. If the first response is correct, the trial passes; if not, it fails. No retries, revisions, or later corrections are counted.

## How the evaluation works

- DAB includes 54 benchmark queries across 12 datasets.
- Each query is executed for at least 50 independent trials (n ≥ 50).
- For each trial, the first answer is judged correct or incorrect.
- pass@1 is calculated as:

  correct first responses ÷ total trials

  across all queries and trials.

## Why pass@1 is used

pass@1 is the chosen metric because it matches production expectations for a data analyst agent: deliver a correct answer on the first try. It rewards systems that combine correct reasoning, accurate tool execution, and precise context use in one pass.

## What good and poor scores look like

- The current best published DAB pass@1 score is 54.3% by PromptQL + Gemini 3.1 Pro.
- A strong score is near that benchmark.
- A weak score is substantially lower, meaning the agent often fails its first response.

## What this score measures in practice

pass@1 measures the agent's ability to:

- route queries across multiple database systems,
- resolve ill-formatted join keys,
- transform unstructured text into structured facts,
- apply domain knowledge correctly on the first attempt.

In production terms, it measures whether the agent is reliable at first delivery rather than recoverable after multiple attempts.

## Why measurable improvement matters

The challenge is built around measurable progress. Improving pass@1 between runs shows that the evaluation harness is capturing real gains in the agent's behavior and not just random variation. That improvement is the primary success signal for this benchmark.
