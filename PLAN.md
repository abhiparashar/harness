# Coding Agent Harness — Learning Plan

## Where we are
- Built llama.cpp from source on Apple M5
- Running Gemma 4 E4B (MoE, instruction tuned, Q4_K_M) via llama-server on port 8080
- Basic tool loop working in harness.py (messages → tool_calls → execute → tool_result → loop)
- Fake get_weather tool confirmed working end to end
- All 4 tools built and tested: run_shell, read_file, write_file, search_code
- agent_loop.py wired — agent wrote code, self-corrected python→python3 error, read and summarized a file

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
└── context_manager.py     # next — smart file selection for 8k context window

## Build order
1. ✅ run_shell.py
2. ✅ read_file.py + write_file.py
3. ✅ search_code.py
4. ✅ agent_loop.py — agent proved capable: writes code, self-corrects, reads and summarizes files
5. context_manager.py — smart file selection so we don't blow 8k context
6. Give agent a real multi-file coding task end to end

## Known limits
- 8192 context vs Claude Code's 200k — need smart context management
- Gemma 4 E4B reasoning < Claude Sonnet — expect ~30% of Claude Code capability
- No multimodal in GGUF version (text + function calling only)

## Next session: build context_manager.py
- Goal: rank files by relevance to the task before putting them in context
- Approach: start simple (file size + keyword match), then add BM25 ranking
