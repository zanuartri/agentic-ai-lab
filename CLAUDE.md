# agentic-ai-lab

Learning-in-public monorepo for a career switch into AI agent engineering.
Each numbered folder under a framework directory (`langchain/`,
later `langgraph/`, `deepagents/`) is a self-contained portfolio project.

## Working agreement (important — read before helping with any project here)

The point of this repo is for the user to learn LangChain/LangGraph/agentic
patterns hands-on, not to have code generated for them. When helping with
a project's implementation:

- Give specs, step-by-step tasks, and explain concepts — don't write the
  learning code yourself unless explicitly asked ("tulis kodenya",
  "gimana kodenya?"). Even then, keep explaining what each line does.
- It's fine to write directly: READMEs, `.gitignore`, `LICENSE`, git/GitHub
  setup, and file/folder scaffolding (empty dirs, file names) — the
  "don't code for me" rule is specifically about the framework/Python logic
  being practiced.
- Prefer flat file layout per project (`agent.py`, `tools.py`, `main.py` at
  the project root) over `src/`-nested layout — these are small
  single-purpose scripts, not installable packages.
- Env vars for LLM config use `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`
  (OpenAI-spec compatible client via `ChatOpenAI`), not `OPENAI_*` — lets
  the user point at any compatible provider/gateway.

## Conventions

- Each project folder has its own README with: what it does, setup steps,
  "what I learned," and known limitations — that's the living roadmap/status
  for that project, check it before assuming what's done.
- New projects get the next number in sequence within their framework
  folder (`langchain/02-...`, etc.).
- Root `.gitignore` covers `.venv/`, `__pycache__/`, `.env`,
  `.claude/settings.local.json` for all projects. A project only needs its
  own `.gitignore` for project-specific generated/cloned data (e.g. a cloned
  docs repo, a persisted vector store) that the root patterns don't cover.

## Current state

- `langchain/01-defi-yield-agent` — done. LangChain `create_agent`
  tool-calling agent over the DeFiLlama yields API, LangSmith tracing
  wired, conversation-history cost bug found & fixed.
- `langchain/02-defi-docs-rag` — done. RAG agent over Uniswap's docs
  (Chroma + Ollama local embeddings + ChatOpenAI generation), grounded
  answers with source citations.
