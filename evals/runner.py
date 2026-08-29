import sys
import time
import os

# add parent dir so we can import agent_loop
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_loop import run
from evals.tasks import TASKS

def run_eval():
    results = []
    print(f"\n{'='*50}")
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
            run(task["prompt"])          # run the agent
            elapsed = time.time() - start
            passed = task["check"]()     # verify the output
        except Exception as e:
            elapsed = time.time() - start
            passed = False
            print(f"  ERROR: {e}")

        status = "PASS" if passed else "FAIL"
        results.append({
            "name": task["name"],
            "passed": passed,
            "time": elapsed
        })
        print(f"  [{status}] {elapsed:.1f}s\n")

    # summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_time = sum(r["time"] for r in results) / total

    print(f"{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"Avg time per task: {avg_time:.1f}s")
    print(f"{'='*50}")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark} {r['name']:<25} {r['time']:.1f}s")

if __name__ == "__main__":
    run_eval()
