# Persistent Memory Agent

A LangChain `create_agent` with checkpointer-backed conversation memory —
history survives process restarts via a `thread_id`, instead of the
in-process message list project 01 used.

```
> top 3 stablecoin yields on Ethereum
[agent calls get_top_yields(...), summarizes]

> how about arbitrum?
[remembers the stablecoin filter from the previous turn — same as project 01]

(exit, close the terminal entirely, reopen, python main.py, same thread id)
> what did we talk about before?
[recaps the earlier conversation accurately — proof persistence survived a real process restart, not just the input loop]
```

## Why this exists

Project 01 and 02's READMEs both note the same limitation: no real
conversation memory (01 truncates a Python list per-process; 02/03 treat
every question independently). This project fixes that properly using
LangGraph's checkpointer, which `create_agent` already supports as a
built-in argument.

## Stack

- Python 3.11+
- LangChain 1.x (`create_agent`)
- `langgraph-checkpoint-sqlite` (`SqliteSaver`)
- Reuses project 01's `get_top_yields` DeFiLlama tool, to prove memory and
  tool-calling work together

## How it works

```
User prompt (CLI, main.py)
   → executor.invoke({"messages": [...]}, config={"configurable": {"thread_id": ...}})
        → SqliteSaver loads/saves the full message history for that thread_id
             in checkpoints.db, keyed by thread_id
        → create_agent(model, tools, system_prompt, checkpointer)   [agent.py]
             → tool: get_top_yields(...)   [tools.py, copied from project 01]
   → agent replies using the reloaded history + tool results
```

Unlike project 01, `main.py` sends only the *new* user message each turn —
the checkpointer reconstructs the rest from `checkpoints.db`. Different
`thread_id` values are fully isolated conversations sharing the same
database file.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
python main.py
```

## What I learned building this

- **`SqliteSaver` lives in a separate package** (`langgraph-checkpoint-sqlite`),
  not `langgraph` core — easy to miss since `InMemorySaver` ships inside
  `langgraph.checkpoint.memory` with no extra install.
- **`SqliteSaver(conn)` vs. `SqliteSaver.from_conn_string(...)`.** The docs
  mostly show `from_conn_string` used as a context manager
  (`with SqliteSaver.from_conn_string(...) as checkpointer:`), which doesn't
  fit a module-level `executor` that outlives a single `with` block. Passing
  a plain `sqlite3.connect(...)` connection straight into the constructor
  works and is simpler for a script that just imports `agent.py` once.
- **`check_same_thread=False` is required** on the sqlite connection —
  LangGraph can touch the connection from a different thread than the one
  that created it, and sqlite3 refuses cross-thread access by default.
- **The checkpointer, not the app code, owns history now.** Project 01 had
  to manually append to and truncate a `messages` list every turn. Here
  `main.py` just sends the latest message plus a `thread_id` — genuinely
  less code than the "naive" version, not just a different flavor of it.
- **Persistence is real, not simulated.** Verified by fully exiting the
  Python process (not just looping in the same run) and asking the same
  `thread_id` to recap the conversation — it did, correctly, from
  `checkpoints.db` on disk.

## Known limitations

- No history trimming — every turn resends the entire stored conversation
  to the model, so token cost grows unbounded the same way project 01's did
  before its `MAX_HISTORY` cap (this project has no cap at all yet).
- `checkpoints.db` grows forever; nothing prunes old threads.
- Single local Sqlite file, not suited for multi-process/concurrent access
  (`PostgresSaver` would be the production equivalent).

## Possible next steps

- Add `trim_messages` (token-based, not message-count-based like project
  01's `MAX_HISTORY`) before each invoke
- A way to list/delete old `thread_id`s from `checkpoints.db`
- Try `PostgresSaver` to compare the setup against `SqliteSaver`
