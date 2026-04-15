# Shared Utility Library

Three reusable modules for Oracle Forge. Each is self-testing — run with `python utils/<module>.py` to verify.

---

## 1. join_key_resolver.py

Strips ID prefixes and merges two DataFrames on the normalized integer key.
Solves the DAB ill-formatted join key problem (Correction 002).

**Usage:**
```python
from utils.join_key_resolver import resolve_join_keys
merged = resolve_join_keys(
    df_business, 'business_id', 'businessid_',
    df_reviews,  'business_ref', 'businessref_'
)
```

**Test:** `python utils/join_key_resolver.py` → `join_key_resolver: PASS`

---

## 2. mongo_helper.py

Safe MongoDB query wrapper. Default `limit=10000` prevents the silent 5-document truncation bug (Correction 003).

**Usage:**
```python
from utils.mongo_helper import mongo_query
businesses = mongo_query('yelp_db', 'business', {'city': 'Indianapolis'})
```

**Test:** `python utils/mongo_helper.py` → `mongo_helper: PASS` (or SKIP if MongoDB not running locally)

---

## 3. score_logger.py

Appends a structured pass@1 result entry to `eval/score_log.jsonl`.

**Usage:**
```python
from utils.score_logger import log_score
log_score(
    dataset='yelp',
    llm='google/gemini-3.1-pro-preview',
    results=[{'query_id': 1, 'passed': True, 'answer': '3.55'}],
    notes='OpenRouter run with KB injection'
)
```

**Test:** `python utils/score_logger.py` → `score_logger: PASS`
