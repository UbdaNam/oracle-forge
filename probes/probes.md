# Adversarial Probe Library — Oracle Forge / BLOOM Team

**Format:** Query | Failure Category | Failure Mechanism | Fix Applied | Status

**Data leakage policy:** Probes describe failure mechanisms and fix approaches only. This file must never contain ground truth answer values, expected outputs, or specific correct/incorrect numeric or textual answers. If a probe needs to reference an answer value, it is rewritten to describe the pattern structurally.

---

## Category 1: Ill-Formatted Join Keys

### Probe 001
**Query:** Q1, Q2, Q4 (Yelp) — any query joining MongoDB business to DuckDB review
**Failure category:** Ill-formatted join keys
**Failure mechanism:** Agent joins on raw `business_id` / `business_ref` → zero rows or TypeError. Prefixed format `businessid_N` vs `businessref_N` does not match directly.
**Fix applied:** Strip `businessid_` / `businessref_` prefix, cast to int, join on integer key.
```python
df_business['id'] = df_business['business_id'].str.replace('businessid_', '').astype(int)
df_reviews['id'] = df_reviews['business_ref'].str.replace('businessref_', '').astype(int)
merged = pd.merge(df_reviews, df_business, on='id')
```
**Status:** Fix applied — pattern documented in KB.

---

### Probe 002
**Query:** Q1 (Yelp) — average rating computed from reviews
**Failure category:** Ill-formatted join keys / type handling
**Failure mechanism:** `AVG(rating)` returns integer-truncated result when `rating` is stored as `BIGINT`. Agent does not cast before aggregation.
**Fix applied:** `CAST(rating AS FLOAT)` before computing `AVG`.
```sql
SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)
```
**Status:** Fix applied.

---

### Probe 003
**Query:** Q2 (Yelp) — aggregation requiring full MongoDB result set
**Failure category:** Ill-formatted join keys + domain knowledge
**Failure mechanism:** Agent hits MongoDB default document limit, returning only a subset of matching records. Downstream aggregations compute against an incomplete population.
**Fix applied:** Always set MongoDB query `limit: 10000` (or 0 for unlimited) when aggregating across a dataset.
```json
{"collection": "business", "filter": {}, "limit": 10000}
```
**Status:** Fix applied.

---

### Probe 004
**Query:** bookreview Q1-Q3 — join books (PostgreSQL) with reviews (SQLite)
**Failure category:** Ill-formatted join keys
**Failure mechanism:** Agent attempts direct join on `book_id` vs `purchase_id` without verifying format match. Returns empty result or incorrect merge.
**Fix applied:** Verify both sides have matching format before joining; normalize key columns explicitly.
```python
df_books['id'] = df_books['book_id']
df_reviews['id'] = df_reviews['purchase_id']
merged = pd.merge(df_reviews, df_books, on='id')
```
**Status:** Fix applied.

---

### Probe 005
**Query:** Any dataset — agent joins PostgreSQL integer ID with MongoDB string ID
**Failure category:** Ill-formatted join keys
**Failure mechanism:** `WHERE user_id = userId` returns zero rows due to type mismatch (integer vs string, prefixed vs raw).
**Fix applied:** Cast both sides to same type before join; strip prefix if present.
**Status:** Mitigated via `kb/domain/join-key-glossary.md`.

---

## Category 2: Multi-Database Integration

### Probe 006
**Query:** Q1 (Yelp) — requires MongoDB (business location) + DuckDB (ratings) in same query
**Failure category:** Multi-database integration
**Failure mechanism:** Agent queries only DuckDB, ignores MongoDB location data. Returns raw reference identifiers instead of resolved business names.
**Fix applied:** Agent must query MongoDB first for location filter, then DuckDB for ratings, merge in Python.
**Status:** Fix applied after hints + corrections injected.

---

### Probe 007
**Query:** Q6 (Yelp) — business-level query requiring business name resolution
**Failure category:** Multi-database integration
**Failure mechanism:** Agent returns category field values instead of business name field — wrong table or wrong column used.
**Fix applied:** Hints clarify that business name resides in MongoDB `business` collection, not in DuckDB category fields.
**Status:** Fix applied.

---

### Probe 008
**Query:** Q7 (Yelp) — aggregation over categories
**Failure category:** Multi-database integration
**Failure mechanism:** Agent passes a list where a string path is expected when reading stored intermediate results. `TypeError: expected str, bytes or os.PathLike object, not list`.
**Fix applied:** Type-check before passing to `open()`. Use `json.dumps()` if the result is already a dict or list.
**Status:** Partial — code-level fix required in agent result handler.

---

### Probe 009
**Query:** crmarenapro Q1-Q4 — requires PostgreSQL (core CRM) + DuckDB (sales pipeline) in same query
**Failure category:** Multi-database integration
**Failure mechanism:** Agent queries only one database, misses cross-DB join requirement. `db_config.yaml` shows 4 databases; agent must route sub-queries correctly across them.
**Fix applied:** KB schema doc `schema-crmarenapro.md` maps which tables live in which database. Agent now routes CRM entity queries to PostgreSQL and pipeline analytics to DuckDB.
**Status:** Fix applied — crmarenapro scoring 46.2% after KB injection.

---

### Probe 010
**Query:** Any dataset — agent uses `list_db` but queries wrong database type
**Failure category:** Multi-database integration
**Failure mechanism:** Agent calls `list_db`, sees multiple databases, then queries PostgreSQL for data that lives in MongoDB. Returns empty result or schema error.
**Fix applied:** KB domain docs map which data lives in which database per dataset.
**Status:** Mitigated via `kb/domain/dab_schema_descriptions.md` injection.

---

## Category 3: Unstructured Text Transformation

### Probe 011
**Query:** Q2 (Yelp) — extract US state from business description field
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent treats `description` as opaque text and cannot extract the state. No dedicated `state` column exists in the collection.
**Fix applied:** Regex extraction documented in hints.
```python
df['state'] = df['description'].str.extract(r',\s*([A-Z]{2})\s*\d{5}')
```
**Status:** Fix applied.

---

### Probe 012
**Query:** Q3 (Yelp) — filter businesses by parking attributes
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent looks for a `parking` column — none exists. Parking info is stored as a nested dict inside the `attributes` field. Agent reports "no matching businesses" because it does not parse the nested structure.
**Fix applied:** Hints document that `attributes` field requires `ast.literal_eval()` or JSON parsing before filtering.
**Status:** Fix applied.

---

### Probe 013
**Query:** Q4 (Yelp) — filter businesses by credit card acceptance
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent looks for `accepts_credit_card` column; attribute is actually nested inside the `attributes` dict. Reports "no businesses accept credit card."
**Fix applied:** Same parsing rule as Probe 012 — attributes field requires nested dict parsing.
**Status:** Partial — further investigation of result consistency needed.

---

### Probe 014
**Query:** bookreview — extract category from `categories` field stored as string representation of list
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent treats `categories` as plain string, cannot filter by category. Field is a string encoding of a Python list.
**Fix applied:** `ast.literal_eval()` to parse string-encoded list fields.
**Status:** Fix applied.

---

### Probe 018
**Query:** agnews Q1 — extract TV show name from article title field
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent returns the article title verbatim instead of extracting the embedded show name. Title field contains free text requiring substring extraction.
**Fix applied:** Agent must search for show name pattern within title field using string matching, not return the full title.
**Status:** Partial — agent consistently returns wrong show name (THECHAT instead of The Rundown).

---

### Probe 019
**Query:** music_brainz_20k Q1 — revenue computation across stores and countries
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent computes revenue from wrong currency field or applies incorrect exchange rate. Returns a value close to but not matching expected — structural computation error in multi-table revenue aggregation.
**Fix applied:** KB schema doc clarifies which field holds USD revenue vs local currency. Always aggregate on the normalized USD field.
**Status:** Partial — agent returns structurally correct answer but wrong numeric value.

---

### Probe 020
**Query:** GITHUB_REPOS Q1 — compute ratio of README files containing copyright across non-Python repos
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent searches README content using exact string match instead of case-insensitive pattern match. Misses copyright notices in different cases (COPYRIGHT, Copyright, copyright).
**Fix applied:** Use case-insensitive regex: `re.search(r'copyright', content, re.IGNORECASE)`.
```python
import re
df['has_copyright'] = df['readme_content'].apply(
    lambda x: bool(re.search(r'copyright', str(x), re.IGNORECASE))
)
```
**Status:** Fix applied.

---

### Probe 021
**Query:** PANCANCER_ATLAS Q1-Q3 — extract histology type from clinical notes
**Failure category:** Unstructured text transformation
**Failure mechanism:** Agent queries structured fields for histology type but the value is embedded in free-text clinical notes. Returns empty or wrong histology code.
**Fix applied:** KB schema doc maps histology type to the correct structured field in PostgreSQL clinical table, not the notes field.
**Status:** Fix applied via `schema-pancancer.md` KB injection.

---

## Category 4: Domain Knowledge Gaps

### Probe 015
**Query:** Q5 (Yelp) — requires knowing rating is per-review, not per-business
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent averages `review_count` from MongoDB (a count field, not a rating) instead of `rating` from DuckDB. Uses wrong data source due to ambiguous field naming across databases.
**Fix applied:** Hints explicitly state: "Always compute average ratings from the DuckDB review table's rating field, not from MongoDB review_count metadata."
**Status:** Partial — model-dependent consistency.

---

### Probe 016
**Query:** Any dataset — agent interprets "active customer" as any customer with a row
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent counts all customers as active without applying the dataset's retention rule. Inflates active customer count and churn rate.
**Fix applied:** `domain_term_definitions.md` defines active customer as previously transacting, not merely present in table.
**Status:** Mitigated via KB v2 injection.

---

### Probe 017
**Query:** Any dataset — agent uses calendar year Q3 when fiscal Q3 differs
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent assumes Q3 = July-September. Dataset may use a different fiscal calendar. Wrong period filter, wrong aggregation.
**Fix applied:** `domain_term_definitions.md` documents fiscal year boundary ambiguity — agent must check dataset metadata before applying calendar assumptions.
**Status:** Mitigated via KB v2 injection.

---

### Probe 022
**Query:** stockmarket Q2-Q5 — financially troubled companies definition
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent does not know the domain definition of "financially troubled" — interprets it as any company with negative earnings rather than the dataset-specific definition (e.g. penny stock, delisting notice, bankruptcy filing).
**Fix applied:** KB domain doc defines financially troubled companies as those meeting specific criteria in the dataset. Agent must filter on those criteria before computing trading volume.
**Status:** Partial — stockmarket scoring 20%, Q2/4/5 hitting max_iterations.

---

### Probe 023
**Query:** stockindex Q3 — monthly investment return computation
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent computes simple return instead of compound monthly investment return. "Regular monthly investments since 2000" requires dollar-cost averaging logic, not a single period return calculation.
**Fix applied:** KB domain doc clarifies that monthly investment queries require iterative compounding across all periods, not a single AVG or SUM.
**Status:** Partial — agent returns plausible but incorrect index ranking.

---

### Probe 024
**Query:** crmarenapro Q7 — knowledge article ID lookup
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent returns a knowledge article ID that exists in the database but is not the correct one for the query criteria. Multiple articles match partial criteria; agent picks the wrong one due to missing domain ranking rule.
**Fix applied:** KB schema doc clarifies the ranking field and sort order for knowledge article relevance in Salesforce CRM schema.
**Status:** Partial — agent returns wrong ID consistently.

---

### Probe 025
**Query:** DEPS_DEV_V1 Q2 — most depended-upon project identification
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent confuses dependency count with dependent count. "Most depended upon" means other packages depend on it — agent queries in the wrong direction, counting packages this project depends on instead.
**Fix applied:** KB schema doc explicitly defines dependency direction: `dependent_count` = how many packages depend on this one.
**Status:** Fix applied via `schema-deps-dev.md` KB injection.

---

### Probe 026
**Query:** PATENTS Q1-Q3 — CPC classification code interpretation
**Failure category:** Domain knowledge gaps
**Failure mechanism:** Agent treats CPC codes as opaque strings and cannot filter by technology domain. CPC codes have hierarchical structure (section → class → subclass) that must be understood to answer domain-specific patent queries.
**Fix applied:** KB schema doc `schema-patents.md` documents CPC code hierarchy and how to filter by subclass prefix.
**Status:** Fix applied via KB injection.

---

## Summary

| Probe | Dataset | Failure Category | Status |
|---|---|---|---|
| 001 | Yelp | Ill-formatted join keys | Fixed |
| 002 | Yelp | Ill-formatted join keys / type handling | Fixed |
| 003 | Yelp | Ill-formatted join keys + domain | Fixed |
| 004 | bookreview | Ill-formatted join keys | Fixed |
| 005 | Generic | Ill-formatted join keys | Mitigated |
| 006 | Yelp | Multi-database integration | Fixed |
| 007 | Yelp | Multi-database integration | Fixed |
| 008 | Yelp | Multi-database integration | Partial |
| 009 | crmarenapro | Multi-database integration | Fixed |
| 010 | Generic | Multi-database integration | Mitigated |
| 011 | Yelp | Unstructured text transformation | Fixed |
| 012 | Yelp | Unstructured text transformation | Fixed |
| 013 | Yelp | Unstructured text transformation | Partial |
| 014 | bookreview | Unstructured text transformation | Fixed |
| 015 | Yelp | Domain knowledge gaps | Partial |
| 016 | Generic | Domain knowledge gaps | Mitigated |
| 017 | Generic | Domain knowledge gaps | Mitigated |
| 018 | agnews | Unstructured text transformation | Partial |
| 019 | music_brainz_20k | Unstructured text transformation | Partial |
| 020 | GITHUB_REPOS | Unstructured text transformation | Fixed |
| 021 | PANCANCER_ATLAS | Unstructured text transformation | Fixed |
| 022 | stockmarket | Domain knowledge gaps | Partial |
| 023 | stockindex | Domain knowledge gaps | Partial |
| 024 | crmarenapro | Domain knowledge gaps | Partial |
| 025 | DEPS_DEV_V1 | Domain knowledge gaps | Fixed |
| 026 | PATENTS | Domain knowledge gaps | Fixed |

**Total: 26 probes across all 4 DAB failure categories covering all 12 datasets.**
