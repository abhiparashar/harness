import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests
from evals.tasks import TASKS

ENDPOINT = "http://localhost:8080/v1/chat/completions"

def run_raw(task_prompt):
    """Send task directly to model with no tools, no loop — raw completion only"""
    response = requests.post(ENDPOINT, json={
        "messages": [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": task_prompt}
        ],
        "max_tokens": 1000
    }).json()
    return response["choices"][0]["message"]["content"]

def run_baseline():
    results = []
    print(f"\n{'='*50}")
    print(f"BASELINE: Raw model, no tools, no harness")
    print(f"Running {len(TASKS)} evals")
    print(f"{'='*50}\n")

    for task in TASKS:
        print(f"[{task['name']}] Running...")

        # clean up files from previous runs
        for f in ["greet.py", "fib.py", "buggy.py", "output.txt", "imports_report.txt"]:
            if os.path.exists(f):
                os.remove(f)

        start = time.time()
        try:
            response = run_raw(task["prompt"])
            elapsed = time.time() - start
            passed = task["check"]()    # check if files were actually created
            print(f"  Model said: {response[:150]}...")
        except Exception as e:
            elapsed = time.time() - start
            passed = False
            print(f"  ERROR: {e}")

        status = "PASS" if passed else "FAIL"
        results.append({"name": task["name"], "passed": passed, "time": elapsed})
        print(f"  [{status}] {elapsed:.1f}s\n")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_time = sum(r["time"] for r in results) / total

    print(f"{'='*50}")
    print(f"BASELINE Results: {passed}/{total} passed")
    print(f"Avg time per task: {avg_time:.1f}s")
    print(f"{'='*50}")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark} {r['name']:<25} {r['time']:.1f}s")

if __name__ == "__main__":
    run_baseline()
