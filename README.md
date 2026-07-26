# agentic-ai-lab

Learning-in-public repo for my switch into AI agent engineering. Each numbered
folder is a self-contained project, built while learning a specific
framework — LangChain first, then LangGraph, deepagents, and whatever comes
next.

## Projects

| # | Project | Framework | What it does |
|---|---------|-----------|---------------|
| 01 | [defi-yield-agent](./langchain/01-defi-yield-agent) | LangChain | Tool-calling agent that answers natural-language questions about DeFi yield pools using live DeFiLlama data |
| 02 | [defi-docs-rag](./langchain/02-defi-docs-rag) | LangChain | RAG agent that answers questions about Uniswap grounded in its official docs |
| 03 | [yield-risk-classifier](./langchain/03-yield-risk-classifier) | LangChain | Classifies DeFi pool risk with forced structured (Pydantic) output instead of free text |
| 04 | [persistent-memory-agent](./langchain/04-persistent-memory-agent) | LangChain | Agent with SqliteSaver checkpointer memory that survives a full process restart |

Every project folder has its own README with setup instructions, what I
learned, and known limitations.
