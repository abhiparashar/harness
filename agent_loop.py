import json
import requests
from tools.read_file import read_file
from tools.write_file import write_file
from tools.run_shell import run_shell
from tools.list_files import list_files
from context_manager import get_relevant_files

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
    ,{
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"}
                },
                "required": ["directory"]
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
    elif name == "list_files":
        return str(list_files(**args))
    return "unknown tool"

# the agent loop
def run(task):
    # get relevant files and inject into system prompt
    relevant = get_relevant_files('.', task)
    context = "\n\n".join([f"# {path}\n{content}" for path, content in relevant])
    messages = [
        {"role": "system", "content": f"You are a coding agent. You MUST call tools using the tool_calls mechanism. NEVER write tool calls as text or markdown. ALWAYS verify code after writing it. For Flask/server apps, verify by running 'python3 -c \"import <module>; print(OK)\"' to check syntax — never start a server directly as it will hang.\n\nRelevant files in this project:\n{context}"},
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

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Task: ")
    run(task)
