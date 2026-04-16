# AI-DLC Inception Document — Sprint 2
**Team:** BLOOM | **Driver:** Amir Ahmedin | **Date:** April 2026

---

## 1. Press Release (What We Are Building)

The BLOOM team has extended Oracle Forge from a single-dataset agent to a full-scale
benchmark competitor. Sprint 2 delivers: all 12 DAB datasets running, 50 trials per query
for statistically valid pass@1 scoring, a 15+ probe adversarial library documenting every
failure mode found, and a submitted GitHub PR to the DataAgentBench leaderboard. The agent
now uses GPT-4o via OpenRouter with 3 context layers injected at session start — schema
knowledge, domain knowledge, and a corrections log that grows with every failure. The final
pass@1 score across all 54 queries is submitted publicly and the team's architecture is
documented for the research community.

---

## 2. What We Are NOT Building

- A new agent from scratch — we extend Oracle Forge from Sprint 1
- A web UI — still command line only
- A fine-tuned model — GPT-4o via OpenRouter as-is

---

## 3. Honest FAQ — User Perspective

**Q: What's new in Sprint 2 vs Sprint 1?**
A: Sprint 1 proved the approach on Yelp (7 queries, 57.1% pass@1). Sprint 2 runs all 54
queries across 12 datasets and submits to the public DAB leaderboard.

**Q: Will the score be higher than 28.1%?**
A: On Yelp yes — we fixed the BIGINT CAST bug and MongoDB limit bug. Across all 54 queries
the score will likely be lower (20-35%) because other datasets need their own hints files
and we haven't tuned them yet.

**Q: How do we know the submission is valid?**
A: DAB requires 50 trials per query. We run 50 trials, collect results JSON, submit via
GitHub PR to ucbepic/DataAgentBench. The leaderboard validates our results.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of Sprint 2?**
A: Running 50 trials × 54 queries = 2,700 API calls. At OpenRouter pricing and rate limits
this needs to be spread across multiple days or run in parallel.

**Q: What could go wrong?**
A: OpenRouter rate limits or cost overruns. Datasets we haven't seen before may have new
join key formats or schema quirks we haven't documented. PostgreSQL datasets need databases
loaded before running.

**Q: What dependencies exist outside our control?**
A: OpenRouter API availability. DAB repository accepting our PR. EC2 server uptime.

---

## 5. Self-Correction Loop (Sprint 2 Extension)

Sprint 1 established the loop. Sprint 2 closes it:

```
detect → diagnose → retry → log → KB update → re-run → score improves
```

Every new failure found in Sprint 2 gets:
1. Logged in `kb/corrections/corrections.md`
2. Fixed in the dataset hints file
3. Re-run to confirm fix
4. Score delta recorded in `eval/score_log.jsonl`

---

## 6. Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| LLM | google/gemini-3.1-pro-preview via OpenRouter | Best accuracy confirmed in Sprint 1 (28.1% on Yelp) |
| Trials per query | 50 | DAB leaderboard requirement |
| Dataset priority | Yelp → bookreview → googlelocal → agnews → stockmarket → rest | Start with confirmed working, expand |
| Submission format | DAB GitHub PR | Required by benchmark |

---

## 7. Definition of Done

### Final Milestone — April 18

- [ ] Agent runs on all 12 DAB datasets without crashing
- [ ] Hints file created and tested for at least 6 datasets
- [ ] 50 trials completed for all 54 queries
- [ ] Results JSON formatted per DAB submission spec
- [ ] GitHub PR opened to ucbepic/DataAgentBench with pass@1 score
- [ ] Score log shows improvement from Sprint 1 baseline (0%) to Sprint 2 final
- [ ] Adversarial probe library: 15+ probes across 3+ failure categories in probes/probes.md
- [ ] Demo video recorded (max 8 minutes, no login required)
- [ ] Signal Corps: 2 articles published, benchmark X thread live
- [ ] AI-DLC Operations document for Sprint 2 committed

---

## 8. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|------|-------------|------|----------------------|--------|
| | Nebiyou Abebe | Intelligence Officer | | |
| | Ruth Solomon | Intelligence Officer | | |
| | Abdurahim Miftah | Signal Corps | | |
| | Efrata Wolde | Signal Corps | | |
| | Amir Ahmedin | Driver | | |

**Status:** ⏳ Pending team approval at next mob session.

---

> ⚠️ CONSTRUCTION BEGINS ONLY AFTER ALL TEAM MEMBERS APPROVE ABOVE.

---

*AI-DLC Phase: INCEPTION | Next phase: CONSTRUCTION (requires full team approval)*
