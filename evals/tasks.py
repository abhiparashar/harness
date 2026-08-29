import os
import subprocess

# Each task has:
# - name: short identifier
# - prompt: what we send to the agent
# - check: function that returns True if agent succeeded

def file_exists(path):
    return os.path.exists(path)

def file_contains(path, text):
    try:
        return text in open(path).read()
    except:
        return False

def runs_without_error(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
    return result.returncode == 0

TASKS = [
    {
        "name": "write_hello",
        "prompt": "Write a Python function called greet(name) that returns 'Hello, <name>!' and save it to greet.py",
        "check": lambda: file_exists("greet.py") and file_contains("greet.py", "def greet")
    },
    {
        "name": "write_and_run",
        "prompt": "Write a Python script that prints the first 5 fibonacci numbers and save it to fib.py, then run it",
        "check": lambda: file_exists("fib.py") and runs_without_error("python3 fib.py")
    },
    {
        "name": "fix_bug",
        "prompt": "Write a Python file called buggy.py with this exact content: 'def add(a, b): return a - b' — then find the bug, fix it, and verify it works by running: python3 -c \"from buggy import add; assert add(2,3)==5, 'wrong'; print('OK')\"",
        "check": lambda: file_exists("buggy.py") and runs_without_error("python3 -c \"from buggy import add; assert add(2,3)==5; print('OK')\"")
    },
    {
        "name": "read_and_summarize",
        "prompt": "Read agent_loop.py and write a one-line description of what it does to output.txt",
        "check": lambda: file_exists("output.txt") and len(open("output.txt").read().strip()) > 20
    },
    {
        "name": "search_and_report",
        "prompt": "Search the current directory for all files that import 'requests' and write the list to imports_report.txt",
        "check": lambda: file_exists("imports_report.txt") and file_contains("imports_report.txt", "agent_loop")
    }
]
