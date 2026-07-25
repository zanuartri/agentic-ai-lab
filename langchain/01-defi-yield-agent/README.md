# DeFi Yield Scout 🌾

A LangChain tool-calling agent that answers natural-language questions about
DeFi yield pools (APY, TVL, chain, stablecoin status) using live data from
the [DeFiLlama Yields API](https://yields.llama.fi/pools) — no API key
required for the data source.

```
> top 5 stablecoin yields on Ethereum with at least 1 million TVL
[agent calls get_top_yields(chain="Ethereum", min_tvl_usd=1_000_000, stablecoin_only=True), then summarizes]

> how about arbitrum?
[remembers the stablecoin + TVL filter from the previous turn, re-queries for Arbitrum]

> compare Curve vs Aave yields on Ethereum
[correctly says the data source doesn't cover Aave lending markets, instead of hallucinating numbers]
```

## Why this exists

Web3 yield hunting is something I already do manually — this agent automates
the "check a few chains, compare APYs, sanity-check the risk" loop I'd
otherwise do by hand across DeFiLlama tabs.

## Stack

- Python 3.11+
- LangChain 1.x (`create_agent`, built on LangGraph under the hood)
- `ChatOpenAI` client pointed at an OpenAI-spec compatible endpoint (works
  with OpenAI, OpenRouter, or any compatible gateway via `LLM_BASE_URL`)
- DeFiLlama Yields API — free, public, no auth

## How it works

```
User prompt (CLI, main.py)
   → create_agent(model, tools, system_prompt)   [agent.py]
        → tool: get_top_yields(chain, min_tvl_usd, stablecoin_only, top_n)  [tools.py]
             → fetch_pools()   raw GET to DeFiLlama
             → filter_pools()  filter + sort in plain Python
   → agent turns the filtered pools into a natural-language answer
```

Conversation history is kept in `main.py`'s `messages` list across turns, so
follow-up questions ("how about Arbitrum?") reuse filters from earlier in
the conversation without repeating them.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
python main.py
```

### Optional: LangSmith tracing

Add these to `.env` to see a full visual trace of every agent run (model
calls, tool calls with their exact arguments, token usage, latency) at
https://smith.langchain.com — no code changes needed, LangChain
auto-instruments when these env vars are set:

```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<your langsmith key>
LANGSMITH_PROJECT=defi-yield-scout
```

## What I learned building this

- **LangChain restructured its agent API in v1.0.** Tutorials referencing
  `AgentExecutor` / `create_tool_calling_agent` are targeting the pre-1.0
  API. As of `langchain==1.x`, the core package itself depends on
  `langgraph`, and the current recommended way to build a tool-calling agent
  is `create_agent(model, tools, system_prompt=...)` from `langchain.agents`
  — it returns a compiled LangGraph state machine, invoked with
  `{"messages": [...]}` instead of `{"input": "..."}`. The legacy API still
  exists in a separate `langchain-classic` package for anyone maintaining
  older code.
- **The tool's docstring is not a comment — it's the interface the LLM reads**
  to decide when and how to call the tool. Vague docstrings meant vague tool
  usage.
- **A well-behaved agent says "I don't have that data"** rather than
  inventing numbers — confirmed by asking it to compare Curve (in the
  dataset) vs. Aave (a lending protocol not covered by the yields endpoint).
- **Unbounded conversation history is a silent cost bomb.** Since the CLI
  resends the full `messages` list on every turn, token usage (and cost)
  grows with every follow-up question, not just with the complexity of the
  question itself — confirmed by inspecting per-turn token counts in
  LangSmith. Fixed by capping history to the last `MAX_HISTORY` messages in
  `main.py` before each invoke, at the cost of the agent forgetting turns
  older than that window.

## Known limitations

- Data source only covers DEX/AMM/vault yield pools, not lending markets
  like Aave/Compound.
- No caching — every query re-fetches the full pool list from DeFiLlama.
- Single-tool agent; doesn't cross-reference on-chain data or price feeds.
- Conversation memory is capped to the last `MAX_HISTORY` messages, so very
  long conversations lose earlier context.

## Possible next steps

- A `project` filter param to narrow results to a specific protocol
- Persist conversation history across CLI restarts
- Summarize old turns instead of hard-dropping them once `MAX_HISTORY` is hit
