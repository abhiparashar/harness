"""
What the raw model says when asked to write and run code — no tools, no harness.
The model describes the steps but cannot actually create files or run anything.
Run this to see the difference yourself.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

ENDPOINT = "http://localhost:8080/v1/chat/completions"

tasks = [
    "Write a Python function called greet(name) that returns 'Hello, <name>!' and save it to greet.py",
    "Write a Python script that prints the first 5 fibonacci numbers, save it to fib.py, then run it",
]

for task in tasks:
    print(f"\nTask: {task}")
    print("-" * 60)

    response = requests.post(ENDPOINT, json={
        "messages": [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": task}
        ],
        "max_tokens": 300
    }).json()

    print("Model says:")
    print(response["choices"][0]["message"]["content"])
    print()
    print("greet.py exists?", os.path.exists("greet.py"))  # always False
    print("fib.py exists?  ", os.path.exists("fib.py"))    # always False
