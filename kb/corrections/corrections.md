# Corrections Log
*Written by Driver after every observed agent failure. Read by agent at session start.*

---

## Correction 001 — 2026-04-11

**Query:** "Which U.S. state has the highest number of reviews, and what is the average rating of businesses in that state?"
**Dataset:** yelp | **Query ID:** 2

**What was wrong:**
Agent successfully retrieved MongoDB business data but then failed 9 times generating Python code to process it. Errors: `TypeError: list indices must be integers` and `SyntaxError: unterminated string`. The agent was treating the JSON result as a nested list and using integer indices instead of dictionary key access.

**Correct approach:**
- MongoDB query results are returned as a list of dictionaries
- Access fields with `record['field_name']` not `record[0]`
- When processing MongoDB results in execute_python, always use `pd.DataFrame(records)` first, then operate on the DataFrame
- State information in the Yelp dataset is extracted from the `description` field in the business collection using string parsing, not a dedicated `state` field

**Example correct code pattern:**
```python
import pandas as pd
# records is a list of dicts from MongoDB
df = pd.DataFrame(records)
# description field contains location info like "City, State"
df['state'] = df['description'].str.extract(r',\s*([A-Z]{2})')
```

---
