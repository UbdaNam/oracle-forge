# AGENT.md — Oracle Forge

## Architecture
Oracle Forge extends the DAB built-in DataAgent with 3 context layers:

1. **Schema & Metadata** — loaded via `--use_hints` (db_description_withhint.txt per dataset)
2. **Domain Knowledge** — KB documents in kb/domain/ (join keys, failure categories, field inventory)
3. **Corrections Memory** — kb/corrections/corrections.md injected at session start via kb_injector.py

## Key Design Decisions
- Base: DAB built-in DataAgent (common_scaffold/DataAgent.py)
- LLM: gemini-3.1-pro-preview via Google OpenAI-compatible API
- Databases: PostgreSQL (Docker), MongoDB (system), SQLite, DuckDB
- KB injection: monkey-patch on DataAgent.__init__ appends corrections to db_description

## How to Run

### With OpenRouter (current — instructor-approved API)
```bash
cd ~/DataAgentBench
source .venv/bin/activate
# Set your key in .env: OPENROUTER_API_KEY=<your_key>
# Model name must contain "openrouter" — use the openrouter/<model> format
python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 --llm openrouter/google/gemini-2.5-pro-preview --iterations 20 --use_hints
```

### With Gemini direct (earlier runs, now replaced by OpenRouter)
```bash
python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 --llm gemini-3.1-pro-preview --iterations 20 --use_hints
```

## Score History

| Date | Model | API | Hints | KB Injected | Dataset | Score |
|------|-------|-----|-------|-------------|---------|-------|
| 2026-04-11 | gemini-2.5-flash | Gemini direct | No | No | yelp | 0/7 = 0% |
| 2026-04-11 | gemini-3.1-pro-preview | Gemini direct | Yes | No | yelp | 2/7 = 28.6% |
| 2026-04-13 | gemini-3.1-pro-preview | Gemini direct | Yes | Yes | yelp | 4/7 = 57.1% |
| 2026-04-15+ | openrouter/<model> | OpenRouter | Yes | Yes | yelp | — (add results here) |

## What Worked
- Structural hints (join key patterns, state extraction regex)
- gemini-3.1-pro-preview significantly better than gemini-2.5-flash
- --use_hints flag essential — without it agent makes no tool calls
- KB injection (domain knowledge + corrections) confirmed wired via kb_injector.py
- OpenRouter supported natively in DataAgent.py — model name must contain "openrouter"

## What Did Not Work
- gemini-2.5-flash: MALFORMED_FUNCTION_CALL errors
- Answer-specific hints: overfitting — reverted
- 10 iterations: insufficient for complex multi-DB queries, 20 needed
