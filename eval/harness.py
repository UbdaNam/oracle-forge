"""
Oracle Forge Evaluation Harness
Runs DAB queries, validates against ground truth, produces pass@1 score log.
Usage: python eval/harness.py --dataset yelp --queries 1,2,3,4,5,6,7 --llm gemini-2.5-flash
"""
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

DAB_PATH = Path(__file__).parent.parent / "DataAgentBench"
SCORE_LOG = Path(__file__).parent / "score_log.jsonl"
sys.path.insert(0, str(DAB_PATH))


def get_latest_log(dataset: str, query_id: int) -> dict | None:
    log_dir = DAB_PATH / f"query_{dataset}" / f"query{query_id}" / "logs" / "data_agent"
    if not log_dir.exists():
        return None
    runs = sorted(log_dir.iterdir(), reverse=True)
    if not runs:
        return None
    with open(runs[0] / "final_agent.json") as f:
        return json.load(f)


def validate_query(dataset: str, query_id: int, llm_answer: str) -> tuple[bool, str]:
    validate_path = DAB_PATH / f"query_{dataset}" / f"query{query_id}" / "validate.py"
    if not validate_path.exists():
        return False, "No validate.py found"
    ns = {}
    exec(validate_path.read_text(), ns)
    return ns["validate"](llm_answer)


def run_harness(dataset: str, query_ids: list[int], llm: str, iterations: int = 10):
    print(f"\n{'='*60}")
    print(f"Oracle Forge Evaluation Harness")
    print(f"Dataset: {dataset} | Model: {llm} | Queries: {query_ids}")
    print(f"{'='*60}\n")

    # Run agent on each query
    os.chdir(DAB_PATH)
    for qid in query_ids:
        print(f"Running query {qid}...")
        os.system(f"cd {DAB_PATH} && source .venv/bin/activate && python run_agent.py --dataset {dataset} --query_id {qid} --llm {llm} --iterations {iterations} --root_name harness_run")

    # Collect and validate results
    results = []
    passed = 0

    for qid in query_ids:
        log = get_latest_log(dataset, qid)
        if not log:
            results.append({"query_id": qid, "passed": False, "reason": "no log found", "answer": ""})
            continue

        answer = log.get("final_result", "")
        terminate = log.get("terminate_reason", "")
        llm_calls = log.get("llm_call_count", 0)

        is_valid, reason = validate_query(dataset, qid, answer)
        if is_valid:
            passed += 1

        results.append({
            "query_id": qid,
            "passed": is_valid,
            "reason": reason,
            "answer": answer[:100] if answer else "EMPTY",
            "terminate_reason": terminate,
            "llm_calls": llm_calls,
        })

        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"  Q{qid}: {status} | {terminate} | {reason}")

    # Score
    total = len(query_ids)
    score = round(passed / total * 100, 1) if total else 0

    print(f"\n{'='*60}")
    print(f"SCORE: {passed}/{total} = {score}% pass@1")
    print(f"{'='*60}\n")

    # Save to score log
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "dataset": dataset,
        "llm": llm,
        "total": total,
        "passed": passed,
        "pass_at_1_pct": score,
        "results": results,
    }
    with open(SCORE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Score logged to {SCORE_LOG}")
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="yelp")
    parser.add_argument("--queries", default="1,2,3,4,5,6,7")
    parser.add_argument("--llm", default="gemini-2.5-flash")
    parser.add_argument("--iterations", type=int, default=10)
    args = parser.parse_args()

    query_ids = [int(q) for q in args.queries.split(",")]
    run_harness(args.dataset, query_ids, args.llm, args.iterations)
