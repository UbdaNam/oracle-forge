# Oracle Forge — BLOOM Team
**TRP1 FDE Programme · April 2026**

A production-grade natural language data analytics agent evaluated on the
DataAgentBench (DAB) benchmark — 54 queries, 12 datasets, 9 domains.

## Team
| Name | Email | Role |
|------|-------|------|
| Amir Ahmedin | shuaibahmedin@gmail.com | Driver |
| Nebiyou Abebe | nebiyouabebe6@gmail.com | Intelligence Officer |
| Ruth Solomon | ruthsoll87@gmail.com | Intelligence Officer |
| Efrata Wolde | ephratawolde990@gmail.com | Signal Corps |
| Abdurahim Miftah | abdugreat3@gmail.com | Signal Corps |

## Live Agent
- Server: `bloom.10academy.org`
- Connect: `ssh trp-bloom`
- Shared session: `tmux attach -t oracle-forge`

## Architecture

```
User Query (natural language)
        |
        v
  oracle_run.py          <-- Oracle Forge wrapper
        |
        | injects KB context (~16KB) via kb_injector.py
        |   Layer 1: schema hints  (--use_hints flag)
        |   Layer 2: domain knowledge  (kb/domain/*.md)
        |   Layer 3: corrections memory  (kb/corrections/corrections.md)
        v
  DataAgent  (DAB scaffold)
        |
   +---------+-----------+
   |         |           |
query_db  execute_python  return_answer
   |         |
   v         v
MongoDB    DuckDB         (Yelp dataset)
PostgreSQL SQLite         (other datasets)
        |
        v
  eval/harness.py        <-- scores pass@1, appends to score_log.jsonl
```

## Score Progression
| Date | Model | Hints | KB Injected | Score |
|------|-------|-------|-------------|-------|
| 2026-04-11 | gemini-2.5-flash | No | No | 0/7 = 0% |
| 2026-04-11 | gemini-3.1-pro-preview | Yes | No | 2/7 = 28.6% |
| 2026-04-13 | gemini-3.1-pro-preview | Yes | Yes | 4/7 = 57.1% |

## Setup
```bash
git clone https://github.com/IbnuEyni/oracle-forge.git
cd oracle-forge
git clone https://github.com/ucbepic/DataAgentBench.git
cd DataAgentBench
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
cp ../.env.example .env  # fill in OPENROUTER_API_KEY
```

## Run
```bash
# Single query
python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 \
  --llm google/gemini-3.1-pro-preview --iterations 20 --use_hints

# Full harness
python ~/oracle-forge/eval/harness.py --dataset yelp \
  --queries 1,2,3,4,5,6,7 --llm google/gemini-3.1-pro-preview
```

## Project Structure
```
oracle-forge/
├── agent/          # oracle_run.py, kb_injector.py, AGENT.md
├── kb/             # Knowledge Base (architecture, domain, evaluation, corrections)
├── eval/           # Evaluation harness + score_log.jsonl
├── probes/         # Adversarial probe library
├── planning/       # AI-DLC Inception documents
├── utils/          # join_key_resolver, mongo_helper, score_logger
├── signal/         # Signal Corps engagement log
└── results/        # DAB results JSON
```

## Benchmark Target
- Benchmark: DataAgentBench (54 queries, 12 datasets)
- Best published score: 54.3% (PromptQL + Gemini-3.1-Pro)
- Our target: Beat 38% pass@1 baseline
