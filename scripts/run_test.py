#!/usr/bin/env python3
"""
Single-test runner for Climate Benford analysis.

Usage:
    python run_test.py <test_id>
    python run_test.py wildfire_acreage
    python run_test.py --all          # Run all queued tests
"""

import json
import os
import sys
import fcntl
from datetime import datetime

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

from benford_core import run_analysis
from climate_fetchers import fetch_dataset, FETCHERS

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
QUEUE_PATH = os.path.join(PROJECT_DIR, "data", "test_queue.json")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results", "individual")
SUMMARY_PATH = os.path.join(PROJECT_DIR, "results", "summary.json")


def load_queue():
    with open(QUEUE_PATH, "r") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)


def update_queue_status(test_id, status):
    """Thread-safe queue status update using file locking."""
    with open(QUEUE_PATH, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        queue = json.load(f)
        for test in queue["tests"]:
            if test["id"] == test_id:
                test["status"] = status
                break
        f.seek(0)
        json.dump(queue, f, indent=2)
        f.truncate()
        fcntl.flock(f, fcntl.LOCK_UN)


def save_result(test_id, result):
    """Save individual result and update summary."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Save individual result
    result_path = os.path.join(RESULTS_DIR, f"{test_id}.json")
    result["timestamp"] = datetime.now().isoformat()
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {result_path}")

    # Update summary
    summary = {}
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, "r") as f:
            summary = json.load(f)

    if "tests" not in summary:
        summary["tests"] = {}

    summary["tests"][test_id] = {
        "verdict": result.get("verdict", "ERROR"),
        "n_positive": result.get("n_positive", 0),
        "delta_b": result.get("first_digit", {}).get("delta_b"),
        "mad": result.get("first_digit", {}).get("mad", {}).get("mad"),
        "chi2_p": result.get("first_digit", {}).get("chi_squared", {}).get("p_value"),
        "timestamp": result["timestamp"],
    }
    summary["last_updated"] = datetime.now().isoformat()
    summary["total_tests"] = len(summary["tests"])
    summary["verdicts"] = {}
    for t in summary["tests"].values():
        v = t["verdict"]
        summary["verdicts"][v] = summary["verdicts"].get(v, 0) + 1

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Updated: {SUMMARY_PATH}")


def run_single_test(test_id):
    """Run a single test: fetch data, analyze, save results."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_id}")
    print(f"{'='*60}\n")

    # Update queue
    update_queue_status(test_id, "in_progress")

    try:
        # Fetch data
        print(f"[1/3] Fetching data for {test_id}...")
        data = fetch_dataset(test_id)
        print(f"       Got {len(data)} values\n")

        # Run analysis
        print(f"[2/3] Running Benford analysis...")
        result = run_analysis(data, test_id=test_id)

        # Print summary
        if "error" in result:
            print(f"\n  ERROR: {result['error']}")
            update_queue_status(test_id, "error")
            return result

        fd = result["first_digit"]
        print(f"\n  RESULTS:")
        print(f"  N = {result['n_positive']:,}")
        print(f"  Verdict: {result['verdict']}")
        print(f"  Chi-squared p-value: {fd['chi_squared']['p_value']:.6f}")
        print(f"  MAD: {fd['mad']['mad']:.6f} ({fd['mad']['label']})")
        print(f"  delta_B: {fd['delta_b']:.6f}")
        print(f"  KS D-stat: {fd['ks_test']['d_statistic']:.6f}")
        print()
        print(f"  First-digit distribution:")
        print(f"  {'Digit':>5} {'Observed':>10} {'Benford':>10} {'Epsilon':>10}")
        print(f"  {'-'*5:>5} {'-'*10:>10} {'-'*10:>10} {'-'*10:>10}")
        for d in range(1, 10):
            obs = fd['observed_proportions'][d]
            exp = fd['expected_proportions'][d]
            eps = fd['per_digit_epsilon'][d]
            print(f"  {d:>5} {obs:>10.4f} {exp:>10.4f} {eps:>+10.4f}")

        # Save results
        print(f"\n[3/3] Saving results...")
        save_result(test_id, result)
        update_queue_status(test_id, "completed")

        print(f"\nTest {test_id} completed: {result['verdict']}")
        return result

    except Exception as e:
        print(f"\nERROR running {test_id}: {e}")
        import traceback
        traceback.print_exc()
        update_queue_status(test_id, "error")
        return {"test_id": test_id, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_test.py <test_id>")
        print("       python run_test.py --all")
        print(f"\nAvailable fetchers: {list(FETCHERS.keys())}")
        sys.exit(1)

    if sys.argv[1] == "--all":
        queue = load_queue()
        for test in queue["tests"]:
            if test["status"] == "queued" and test["id"] in FETCHERS:
                run_single_test(test["id"])
    else:
        test_id = sys.argv[1]
        run_single_test(test_id)


if __name__ == "__main__":
    main()
