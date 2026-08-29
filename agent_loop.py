import json
import requests
from tools.read_file import read_file
from tools.write_file import write_file
from tools.run_shell import run_shell
from tools.search_code import search_code

ENDPOINT = "http://localhost:8080/v1/chat/completions"

# tell the model what tools exist and what they do
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command and return output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for a pattern in Python files",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "pattern": {"type": "string"}
                },
                "required": ["directory", "pattern"]
            }
        }
    }
]

# routes tool name to actual function
def execute_tool(name, args):
    if name == "read_file":
        return str(read_file(**args))
    elif name == "write_file":
        return str(write_file(**args))
    elif name == "run_shell":
        return str(run_shell(**args))
    elif name == "search_code":
        return str(search_code(**args))
    return "unknown tool"

# the agent loop
def run(task):
    messages = [
        {"role": "system", "content": "You are a coding agent. Use tools to complete tasks. Always run code after writing it to verify it works."},
        {"role": "user", "content": task}
    ]

    while True:
        response = requests.post(ENDPOINT, json={
            "messages": messages,
            "tools": tools,
            "max_tokens": 2000
        }).json()

        choice = response["choices"][0]
        msg = choice["message"]
        messages.append(msg)

        if choice["finish_reason"] == "tool_calls":
            for call in msg["tool_calls"]:
                name = call["function"]["name"]
                args = json.loads(call["function"]["arguments"])
                print(f">> Tool: {name}({args})")         # show what agent is doing
                result = execute_tool(name, args)
                print(f">> Result: {result[:200]}")       # show first 200 chars of result
                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result
                })
        else:
            print("\nAgent:", msg["content"])
            break

run("Read harness.py, understand what it does, then write a one paragraph summary to summary.txt")
