# Harness → omp Architecture Plan

Goal: rebuild the *concepts* behind Oh My Pi (omp) inside this project — same categories of
tool, same memory model, same orchestration idea — scaled to what a single local Gemma 4 E4B
process (8192 ctx, no sandboxing, no Rust runtime) can actually support. Scale is smaller;
architecture shape is the same.

Reference: omp exposes 16 tool capabilities (12 top-level + 4 `xd://` devices) plus a
three-part memory system (session event log, context spillover, cross-session FTS index).
Every section below names the omp capability it maps from, what it becomes here, and why the
scaled-down form still teaches the real mechanism.

## 1. Tool inventory mapping

| # | omp capability | What it actually does | Scaled equivalent here | New/changed file |
|---|---|---|---|---|
| 1 | `read` | file/dir/archive/db/url read, line ranges, **structural elision** (declarations-only summary, expand on demand) | keep `read_file`; add `start_line`/`end_line` args + directory listing; see 1a below for the elision half | `tools/read_file.py` |
| 2 | `write` | create/overwrite, archive/db entries | keep `write_file` as-is (no archive/db targets needed at this scale) | `tools/write_file.py` |
| 3 | `edit` | hash-anchored line-range patch language (`PUT`/`CUT`) | new **hashline edit tool**: snapshot a file's content hash on read, require that hash to apply a line-range patch — rejects edits against stale content | `tools/edit_file.py` |
| 4 | `grep` | regex search, any file type, line-range selectors | keep `search_code`; drop the `.py`-only filter, take an optional `file_glob` | `tools/search_code.py` |
| 5 | `glob` | pattern-based file discovery, gitignore-aware | keep `list_files`; add glob pattern arg (`fnmatch`) | `tools/list_files.py` |
| 6 | `bash` | persistent shell, async, timeout | keep `run_shell`; already has timeout — no change needed | `tools/run_shell.py` |
| 7 | `ast_edit` | ast-grep structural codemod, stage/resolve | Python-only: use the stdlib `ast` module to match/rewrite simple node patterns (e.g. rename a function, drop a call) — staged as a diff string, applied only on explicit confirm | `tools/ast_edit.py` |
| 8 | `lsp` | go-to-def, references, rename, diagnostics | Python-only, via `jedi`: `definition`, `references`, `rename` | `tools/lsp_tool.py` |
| 9 | `debug` | DAP breakpoints/stepping/stack inspect | wrap stdlib `bdb`/`pdb`: set a breakpoint line, run a script under it, report locals + stack at the stop | `tools/debug_tool.py` |
| 10 | `browser` | real Chromium via CDP, accessibility snapshots | `requests` + `readability`-style text extraction for a URL (no JS execution) — explicitly document this is a text-only subset, not a real browser | `tools/browser_lite.py` |
| 11 | `eval` | persistent kernel, state survives calls | one Python namespace dict kept alive for the life of a session, tool calls `exec()`/`eval()` against it | `tools/py_eval.py` |
| 12 | `task` | spawn a subagent with its own tool subset, block for its final answer | recursive `run()` call with a restricted `allowed_tools` list and its own `SessionLog`, invoked as `spawn_subagent(task, allowed_tools)` | `subagent.py` |
| 13 | `hub` | inter-agent messaging + supervise long-running background processes (dev servers, watchers) | messaging half only: parent passes a task string in, gets the subagent's final answer out (no async mailbox). Process-supervision half is a **non-goal** — this harness has no long-running services to babysit | `subagent.py` |
| 14 | `todo` | phased task tracking, separate from conversation | small JSON-backed todo list tool, reusing the existing `todos.json` file already in the repo | `tools/todo_tool.py` |
| 15 | `ask` | structured user clarification, blocking | terminal `input()` prompt with numbered options | `tools/ask_tool.py` |
| 16 | `web_search` | live external search | DuckDuckGo HTML endpoint scrape (no API key needed), parse top N results | `tools/web_search.py` |
| 17 | skills (`skill://`) | domain knowledge injected on demand | `skills/*.md` directory; a `list_skills`/`read_skill` tool pair lets the agent pull in project-specific guidance instead of it living in the system prompt permanently | `tools/skills_tool.py`, `skills/` |

### 1a. Structural code reads (distinct from `context_manager.py`)
`context_manager.py` currently stuffs whole matching files into the system prompt via BM25.
omp's `read` does something different on top of that: a `.py` file with no explicit line range
returns **signatures only** (`def`/`class` lines, docstrings, no bodies) with a footer naming
which ranges were elided; the agent re-requests only the specific range it needs. Implement this
as a `summarize_python(path)` helper (stdlib `ast`: walk top-level `FunctionDef`/`ClassDef`,
keep `lineno` so a follow-up `read_file(path, start_line, end_line)` can expand exactly that
span) used as `read_file`'s default mode for `.py` files over some size threshold. This is a
second, complementary lever on the same 8192-ctx problem `context_manager.py` already fights —
BM25 picks *which files*, elision picks *how much of each file*.

Non-goals (explicitly not replicated — not worth it at this scale):
- Rust rewrite / native engine — stays Python, this is a learning project not a perf project.
- Real sandboxing/permission prompts — single-user local script, out of scope.
- MCP protocol, plugin marketplace — no external plugin ecosystem to interoperate with.
- Real headless browser (Chromium/CDP) — `playwright` is a valid stretch goal later, not phase 1.
- `hub`'s process-supervision half (start/stop/log-follow a background service) — nothing here
  runs as a long-lived daemon.
- `issue://`/`pr://` (GitHub API integration), `ssh://` (remote host access), `mcp://` (MCP
  resource fetch) — no external accounts/hosts this project needs to reach.
- Model/thinking-level switching, multi-provider credential pinning — one fixed local model,
  one unauthenticated `localhost` endpoint; nothing to switch between or authenticate against.
- `memory://` shared scratch files between agents — folded into `subagent.py` instead: a
  parent can just pass the child's return value forward directly, no separate scratch channel
  needed at this scale.

## 2. Memory architecture (three mechanisms, as inspected in omp's own `~/.omp/agent/`)

### 2a. Session event log — `memory/session_log.py`
- `SessionLog`: one JSONL file per run at `sessions/<cwd-slug>/<timestamp>_<session_id>.jsonl`.
- Every event: `{id, parent_id, type, ts, ...}` — `parent_id` chains to the prior event's `id`
  (a tree, not a flat list), matching the real structure found in omp's own transcripts.
- Event types: `session` (start marker), `message` (verbatim copy of every dict appended to the
  `messages` list — system/user/assistant/tool), `tool_call`/`tool_result` (narration metadata,
  separate from the `message` event that carries the actual payload).
- `SessionLog.resume(session_id)`: locate the file, replay `type == "message"` events back into
  a `messages` list, continue `parent_id` chaining from the last event.

### 2b. Context spillover — `memory/artifacts.py`
- `maybe_spill(text, artifacts_dir, artifact_id)`: text over ~1500 chars (tuned for the 8192-ctx
  budget) gets written to `<session-dir>/<artifact_id>.log`; the message going back to the model
  gets a truncated preview + `artifact://<id>` reference instead of the full blob.
- `read_artifact(artifacts_dir, artifact_id)`: recovers the full content on demand.
- New tool `read_artifact(artifact_id)` — mirrors omp's own `artifact://<id>` recovery footer.

### 2c. Cross-session recall — `memory/history_db.py`
- SQLite `history.db` at repo root: `history(id, session_id, prompt, cwd, created_at)` +
  FTS5 virtual table `history_fts` (confirmed available in this Python build) +
  `session_titles(session_id, title, updated_at)`.
- `record_prompt()` per run, `set_title()` (heuristic: first ~8 words of the task, no extra
  model call), `search(query)` via FTS5 `MATCH`, ranked.

### 2d. Wiring into `agent_loop.py`
- `run(task, session_id=None)`: fresh session logs system+user messages; given `session_id`,
  resumes via `SessionLog.resume()` + `replay_messages()`.
- Every `messages.append(...)` gets a matching `session.log_message(...)`.
- Every tool dispatch logs `tool_call` before executing, `tool_result` (with artifact ref if
  spilled) after.
- CLI: `--search "<query>"`, `--resume <session_id> "<task>"`.
- `evals/runner.py` needs no change — `run(task["prompt"])` still matches (`session_id` defaults
  to `None`).

### 2e. Usage telemetry (`agent.db` equivalent — operational, not conversational)
omp keeps a *separate* database from session history for `model_usage`, `model_perf`, and
`command_usage` — counters and latency, not conversation content. Add a `usage` table to
`history.db`: `usage(tool_name, session_id, latency_ms, ok, created_at)`, one row per
`execute_tool()` call. Gives a real answer to "which tool gets called most / is slowest /
fails most" instead of eyeballing terminal output — directly useful for tightening the eval
harness (`evals/runner.py` already times whole tasks; this adds per-tool granularity).

## 3. Build order (phased, each phase independently testable against `evals/`)

1. **Foundation** — `memory/session_log.py` (no dependents yet, testable standalone: write a
   session, resume it, replay matches).
2. **Context budget** — `memory/artifacts.py` + `read_artifact` tool, wired into the existing
   tool-result path in `agent_loop.py`.
3. **Recall** — `memory/history_db.py` + `--search`/`--resume` CLI flags.
4. **Structural editing** — `edit_file.py` (hashline patch) alongside `write_file.py`; update
   the agent's system prompt to prefer `edit_file` for modifications, `write_file` for new files.
5. **Search/discovery upgrades** — generalize `search_code` (any extension) and `list_files`
   (glob pattern).
6. **Code intelligence** — `lsp_tool.py` (jedi), `ast_edit.py` (stdlib `ast`), `debug_tool.py`
   (`bdb`/`pdb`).
7. **External I/O** — `web_search.py`, `browser_lite.py`.
8. **Orchestration** — `subagent.py` (recursive `run()` with a restricted tool allowlist),
   `todo_tool.py` (JSON-backed), `ask_tool.py`.
9. **Skills** — `skills/` directory + `skills_tool.py`, migrate any standing project guidance
   out of the hardcoded system prompt string in `agent_loop.py` into a skill file.
10. **Telemetry** — `usage` table in `history.db`, one row logged per `execute_tool()` call.
11. **Eval expansion** — add `evals/tasks.py` entries that specifically exercise each new tool
    (resume a session, force a spill + recovery, trigger a hashline conflict, spawn a subagent)
    so regressions show up the same way the original 5-tool harness did.

## 4. Verification per phase
- Phases 1–3 (memory): unit-level, no model needed — call the module functions directly, assert
  file/DB state.
- Phases 4–9 (tools): one real `run()` call per new tool through the live `llama-server`,
  confirm the tool fires and the result is correct — same pattern as the original harness's
  manual verification.
- Phase 10: assert a `usage` row is written per tool call, no model needed.
- Phase 11: full `python3 -m evals.runner` pass, compare pass rate / avg time against the
  existing baseline (5/5, 28.8s) to confirm added surface area didn't regress the core loop.
