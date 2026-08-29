
import json
import requests

ENDPOINT = "http://localhost:8080/v1/chat/completions"

# the tool we're exposing to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    }
]

# fake tool executor
def execute_tool(name, args):
    if name == "get_weather":
        return f"Weather in {args['city']}: 25°C, sunny"

# the loop
def run(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = requests.post(ENDPOINT, json={
            "messages": messages,
            "tools": tools,
            "max_tokens": 200
        }).json()

        choice = response["choices"][0]
        msg = choice["message"]
        messages.append(msg)

        # model wants to call a tool
        if choice["finish_reason"] == "tool_calls":
            for call in msg["tool_calls"]:
                result = execute_tool(
                    call["function"]["name"],
                    json.loads(call["function"]["arguments"])
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result
                })
        else:
            print("Model:", msg["content"])
            break

run("What's the weather in Paris?")
