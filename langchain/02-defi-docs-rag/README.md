# Uniswap Docs Q&A 📚

A RAG (Retrieval-Augmented Generation) agent that answers questions about
Uniswap by retrieving relevant chunks from its official docs, instead of
relying on the LLM's own (possibly outdated) knowledge.

Different pattern from [project 01](../01-defi-yield-agent): that one called
a live API for fresh data, this one grounds answers in a fixed set of
documents you provide.

```
> what is a concentrated liquidity position in uniswap v3?
[retrieves relevant chunks, answers grounded in the docs, cites source files]

> how does aave calculate borrowing interest?
[correctly says "I don't know" — Aave isn't covered by these docs, instead of answering from general LLM knowledge]

> what's the difference between v3 and v4?
[pulls chunks from multiple different doc sections and synthesizes a multi-point comparison]
```

## Stack

- Python 3.11+
- LangChain (`langchain-community`, `langchain-text-splitters`)
- `OllamaEmbeddings` (`nomic-embed-text`, local, free, no rate limits) for
  embeddings — kept separate from the chat LLM, since embedding runs once
  per chunk (thousands of calls) while the LLM only runs per question
- `Chroma` (`langchain-chroma`) as a local, on-disk vector store
- `ChatOpenAI` pointed at an OpenAI-spec compatible endpoint for generation
  (this instance uses Gemini's OpenAI-compat layer)
- Source: [Uniswap docs](https://github.com/Uniswap/docs) (`content/` folder,
  288 `.mdx` files, cloned locally — not committed to this repo)

## How it works

```
ingest.py (run once, or whenever the docs change)
   uniswap-docs/content/**/*.mdx
        → DirectoryLoader + TextLoader          load raw docs
        → RecursiveCharacterTextSplitter        chunk (1000 chars, 200 overlap)
        → OllamaEmbeddings + Chroma             embed + persist to ./chroma-db

agent.py / main.py (run per question)
   question
        → retriever.invoke(question)            fetch top-k similar chunks
        → prompt with chunks injected as context
        → ChatOpenAI                            answer, grounded in context only
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in LLM_API_KEY / LLM_BASE_URL / LLM_MODEL

# needs Ollama running locally with the embedding model pulled:
ollama pull nomic-embed-text

git clone https://github.com/Uniswap/docs.git uniswap-docs

python ingest.py   # one-time: chunk + embed + persist to ./chroma-db
python main.py     # ask questions
```

## What I learned building this

- **OpenAI-compatible endpoints don't all implement the same subset of the
  spec.** Gemini's compatibility layer supports embeddings, but
  `langchain_openai`'s default `OpenAIEmbeddings` behavior (tokenizing input
  via `tiktoken` into token arrays before sending) isn't accepted by it —
  fixed with `check_embedding_ctx_length=False` to send raw strings instead.
  Then hit Gemini's free-tier batch limit (max 100 items/request) and
  per-minute rate limit — the kind of constraint that only shows up once you
  actually run something at scale, not from reading docs.
- **Embeddings and the chat LLM don't have to be the same provider.**
  Switched embeddings to a local Ollama model (`nomic-embed-text`) to avoid
  API rate limits entirely for the ~2,400-chunk one-time ingest, while
  keeping the chat LLM on a hosted API. This is a common pattern: embedding
  is called far more often (once per chunk) than generation (once per
  question).
- **A retriever finds semantically similar chunks, not keyword matches** —
  confirmed by querying "what's the difference between v3 and v4" and
  getting chunks from subgraph docs, custom-accounting guides, and a
  dedicated v4-vs-v3 doc, none of which necessarily share exact wording with
  the question.
- **The prompt has to explicitly permit "I don't know."** Without that
  instruction, LLMs tend to fall back on general knowledge when retrieved
  context doesn't cover a question — the Aave test above only worked because
  the system prompt says to admit it directly.

## Known limitations

- No re-ingestion logic — if the docs repo updates, you have to re-run
  `ingest.py` from scratch (no incremental/diff-based updates).
- Fixed `k=4` retrieved chunks regardless of question complexity or context
  window budget.
- No conversation memory — each question is answered independently, unlike
  project 01's multi-turn agent.
- Chunking is purely character-count based; doesn't respect markdown
  structure, so a chunk can cut across headers/sections.

## Possible next steps

- Compare grounded vs. ungrounded answers side by side (ask the LLM the same
  question with and without retrieval) as a concrete before/after
- Add conversation memory on top of retrieval (follow-up questions)
- Re-rank retrieved chunks before generation instead of using raw similarity
  order
