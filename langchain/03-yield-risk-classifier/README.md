# Yield Risk Classifier ⚖️

An agent that takes DeFi yield pools and classifies each one's risk level
with a forced structured output (Pydantic schema), instead of free-form
text — so the result can be consumed by another system (a report generator,
a dashboard, an alert bot), not just read by a human.

Reuses the `get_top_yields` tool from [project 01](../01-defi-yield-agent).
New concept vs. project 01/02: `response_format` — the model's final answer
is validated against a schema before you get it back.

```
> assess the risk of the top stablecoin pool on Ethereum
{"assessments": [{"pool_name": "supernova-cl EURC-USDC", "apy": 736.17, "risk_level": "high", "recommended": false, ...}]}

> assess the risk of the top 5 yield pools on Arbitrum, not just stablecoins
[returns 5 distinct assessments in one call, each with pool-specific reasoning]

> assess the risk of a pool that doesn't exist, like "fakecoin-9000"
[forced to fill the schema anyway — improvises apy=0.0, explains "not found" in reasons, defaults to risk_level="high"]
```

## Stack

- Python 3.11+
- LangChain `create_agent` with `response_format=ToolStrategy(...)`
- Pydantic for the output schema
- Same `get_top_yields` tool and DeFiLlama data source as project 01

## How it works

```
question
   → create_agent (tools=[get_top_yields], response_format=ToolStrategy(PoolRiskAssessments))
        → model calls get_top_yields to fetch real pool data
        → model MUST end by calling a synthetic "structured output" tool
          matching the PoolRiskAssessments schema (tool_choice="required")
   → result["structured_response"] — a validated PoolRiskAssessments object,
     not free text
```

`PoolRiskAssessments` wraps a `list[PoolRiskAssessment]` so the same schema
handles both a single pool and a batch of pools consistently — one wrapper
object either way, `assessments` has 1 or N items.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
# copy tools.py from project 01 into this folder
python main.py
```

**Provider note:** structured output via `ToolStrategy` requires the model
to support `tool_choice: "required"`. Not every OpenAI-spec compatible
model/gateway does — `deepseek-v4-flash`/`-pro` and `qwen3.7-max` on this
project's gateway rejected it with a generic 400, while `glm-5.2`,
`grok-4.5`, `kimi-k3`, and `minimax-m3` worked. If you hit an opaque 400 on a
request that has no `response_format`-free equivalent problem, check
`tool_choice` support before assuming it's your code.

## What I learned building this

- **Forced structured output needs `tool_choice: "required"` under the
  hood**, which not every provider/gateway supports — confirmed by testing
  the same request across ~6 models on one gateway and finding a clean
  split between models that accepted it and ones that returned an opaque
  `400 Upstream request failed`. Enabling `OPENAI_LOG=debug` on the
  underlying `openai` client was what actually surfaced the real request
  payload and pinned down `tool_choice` as the cause — the LangChain/OpenAI
  error message alone didn't say why.
- **Field names in your schema can silently collide with field names in
  raw tool data.** The output schema had a `pool` field, and the tool's raw
  DeFiLlama data *also* has a field literally named `pool` (an internal
  UUID) alongside `symbol`/`project` (human-readable). The model picked the
  UUID — almost certainly because the field names matched exactly, not
  because it reasoned about which one made sense. Renaming the schema
  field to `pool_name` and being explicit in the prompt about what it
  should contain fixed it.
- **A schema doesn't guarantee good reasoning, only good shape.** Verified
  separately: risk assessments actually varied with real signals (APY
  magnitude, TVL, DeFiLlama's own down-prediction confidence, outlier
  flags) rather than defaulting to one risk level for everything.
- **Forcing structured output removes the model's ability to just say "I
  don't know."** Project 01/02 could freely answer "I don't have that
  data" in prose. Here, asked to assess a nonexistent pool
  ("fakecoin-9000"), the model had no schema-valid way to express "not
  found" — it improvised (`apy: 0.0`, explained the situation in `reasons`,
  defaulted to `risk_level: "high"`). Reasonable, but not something the
  schema guarantees; it depends on the model's judgment call every time.

## Known limitations

- No explicit "not found" / "insufficient data" representation in the
  schema — a nonexistent or data-poor pool gets an improvised assessment
  instead of a clean refusal (see above). A `found: bool` field or optional
  numeric fields would make this explicit rather than implicit.
- Depends on a provider that supports `tool_choice: "required"`; not
  portable across every OpenAI-spec compatible endpoint without checking
  first.
- No conversation memory — same as project 02, each question is
  independent.

## Possible next steps

- Add an explicit `found: bool` (or similar) field to the schema so "no
  data" has a defined shape instead of relying on model improvisation
- Batch-classify project 01's full top-N list and render a summary table
  (pool, risk_level, recommended) as a script output
