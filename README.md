# Coding Agent Harness

A local coding agent built from scratch to learn how AI harnesses work.
Runs on Apple Silicon via llama.cpp + Gemma 4 E4B — no cloud, no abstractions.

## What this is

A minimal Claude Code-style agent: tool loop + local LLM + 5 tools.
Built step by step to understand how harnesses actually work under the hood.

## Stack

- **Engine**: llama.cpp (built from source, Metal GPU acceleration)
- **Model**: Gemma 4 E4B instruction tuned, Q4_K_M quantized (~5GB)
- **Protocol**: OpenAI-compatible REST API via llama-server
- **Language**: Python, raw — no LiteLLM, no LangChain

## How it works

```
user task
    ↓
agent_loop.py → llama-server (port 8080)
    ↓
model returns tool_calls
    ↓
execute tool (read/write/run/search)
    ↓
send result back to model
    ↓
loop until model returns final answer
```

## Tools

| Tool | What it does |
|---|---|
| `run_shell.py` | Run shell commands, capture stdout/stderr/exit_code |
| `read_file.py` | Read any file contents |
| `write_file.py` | Create or overwrite files |
| `search_code.py` | Regex search across Python files |
| `list_files.py` | List all files in a directory |

## Setup

### 1. Build llama.cpp
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j$(sysctl -n hw.logicalcpu)
```

### 2. Download model
```bash
curl -L -o gemma4-e4b.gguf "https://huggingface.co/bartowski/google_gemma-4-E4B-it-GGUF/resolve/main/google_gemma-4-E4B-it-Q4_K_M.gguf"
```

### 3. Start server
```bash
cd llama.cpp
./build/bin/llama-server --model ~/llama.cpp/gemma4-e4b.gguf --ctx-size 8192 --n-gpu-layers 99 --port 8080
```

### 4. Run agent
```bash
cd harness
python3 agent_loop.py
```

## What the agent can do

- Write code and run it to verify
- Self-correct errors (e.g. `python` → `python3`)
- Read existing files and reason about them
- Search across a codebase
- Fix bugs it introduces itself

## Eval results

Same model (Gemma 4 E4B), same tasks — harness is 100% of the capability:

| | No Harness (raw model) | With Harness |
|---|---|---|
| **Score** | 0/5 (0%) | 5/5 (100%) |
| **Avg time per task** | 22.3s | 32.4s |

Without a harness the model describes what it would do but cannot act — no file system access, no execution, just text.
The extra 10s with harness is the tool execution round-trips, not model slowness.

Run evals yourself:
```bash
# with harness
python3 -m evals.runner

# raw model, no tools
python3 -m evals.baseline_runner
```

## What is next

- BM25 ranking in context_manager for smarter file selection on large codebases
- Multi-file coding tasks end to end
