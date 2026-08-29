# Coding Agent Harness — Learning Plan

## Where we are
- Built llama.cpp from source on Apple M5
- Running Gemma 4 E4B (MoE, instruction tuned, Q4_K_M) via llama-server on port 8080
- Basic tool loop working in harness.py (messages → tool_calls → execute → tool_result → loop)
- All 5 tools built and tested: run_shell, read_file, write_file, search_code, list_files
- agent_loop.py wired with context_manager — agent writes code, self-corrects, reads, searches, fixes bugs
- Eval framework built — baseline (no harness) vs harness measured

## Model
- File: ~/llama.cpp/gemma4-e4b.gguf
- Start server: cd ~/llama.cpp && ./build/bin/llama-server --model ~/llama.cpp/gemma4-e4b.gguf --ctx-size 8192 --n-gpu-layers 99 --port 8080

## What we are building
A coding agent equivalent to Claude Code — locally, from scratch.

## Structure
harness/
├── harness.py             # done — basic tool loop
├── agent_loop.py          # done — full coding agent wired with all tools
├── tools/
│   ├── run_shell.py       # done — execute shell commands, capture output
│   ├── read_file.py       # done — read any file contents
│   ├── write_file.py      # done — create or overwrite files
│   └── search_code.py     # done — regex search across Python files
├── context_manager.py     # done — keyword-scored file selection for 8k context window

## Build order
1. ✅ run_shell.py
2. ✅ read_file.py + write_file.py
3. ✅ search_code.py + list_files.py
4. ✅ agent_loop.py — full coding agent
5. ✅ context_manager.py — keyword-based file relevance scoring
6. ✅ evals/runner.py + evals/baseline_runner.py — measured harness impact

## Eval results
| | No Harness | With Harness |
|---|---|---|
| Score | 0/5 (0%) | 5/5 (100%) |
| Avg time | 22.3s | 32.4s |

## Known limits
- 8192 context vs Claude Code's 200k — need smart context management
- Gemma 4 E4B reasoning < Claude Sonnet — expect ~30% of Claude Code capability
- No multimodal in GGUF version (text + function calling only)

## Next session
- BM25 ranking in context_manager — weight rare keywords higher for smarter file selection
- Multi-file coding task — give agent a real project to build end to end
