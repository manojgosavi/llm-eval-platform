# LLM Eval Platform

An open-source platform to **A/B test and score LLM outputs** across providers — Claude, GPT-4o, and Gemini — using latency, cost, token, and semantic quality metrics.

**[Live Demo →](https://llm-eval-platform.vercel.app)**

---

## What it does

Most teams pick an LLM and stick with it. This platform makes it easy to run the same prompt across multiple models, compare results objectively, and track quality over time — so model choices are data-driven, not gut-feel.

- Run any prompt against Claude, GPT-4o, or Gemini in one API call
- Automatically capture latency, cost, token usage, and context window utilisation
- Score outputs using semantic similarity (fastembed embeddings) or LLM-as-judge (Claude)
- Browse run history and compare models on a React dashboard with Recharts visualisations
- Bring your own API keys — the server never stores credentials

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│         Dashboard · Run History · Run Detail            │
│              Vercel (static deploy)                      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS + CORS
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                         │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ClaudeAdapter│  │GeminiAdapter │  │ OpenAIAdapter  │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘ │
│         └────────────────┼──────────────────┘          │
│              litellm (unified LLM interface)             │
│                          │                               │
│         Retry/backoff · Factory pattern                  │
│                          │                               │
│              Postgres (SQLAlchemy/asyncpg)               │
│           eval_runs · eval_scores tables                 │
│              Render Web Service + Postgres               │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────┐
│               Scoring Microservice                       │
│                                                          │
│   /score/semantic  →  fastembed (BAAI/bge-small-en)     │
│   /score/judge     →  Claude as grader (temp=0.0)       │
│                                                          │
│              Render Web Service (free tier)              │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS v3 + Recharts |
| Backend | FastAPI + Python 3.12 + litellm |
| Database | Postgres + SQLAlchemy (async) + asyncpg + Alembic |
| Scoring | fastembed (semantic similarity) + Claude API (LLM judge) |
| LLM Providers | Anthropic Claude, Google Gemini, OpenAI GPT |
| Deploy | Render (backend + scoring) + Vercel (frontend) |

---

## Key Design Decisions

**Adapter pattern** — every LLM provider implements a common `BaseLLMAdapter` interface. Adding a new model is one new file, zero changes to core logic.

**Async throughout** — FastAPI + asyncpg + httpx means the server handles concurrent eval runs without blocking. Critical for running multiple models simultaneously.

**Scoring microservice** — semantic scoring (fastembed/sentence-transformers) is compute-heavy. Isolating it as a separate service keeps the main API lightweight and independently scalable.

**Bring-your-own-key** — API keys are held in browser localStorage and sent as request body fields over HTTPS. The server reads them per request and discards them — zero credential storage. Known limitation: localStorage is vulnerable to XSS; production hardening would use server-side encrypted key vault (tracked in MAN-44).

**Retry with exponential backoff** — transient errors (503, 429) are retried up to 3 times with jitter. Non-transient errors (401, 404) fail immediately without retry.

---

## Project Structure

```
llm-eval-platform/
├── backend/
│   ├── main.py               # FastAPI app, all endpoints
│   ├── db.py                 # async SQLAlchemy engine + session
│   ├── models.py             # EvalRun + EvalScore ORM models
│   ├── adapters/
│   │   ├── base.py           # BaseLLMAdapter + CompletionResult + retry logic
│   │   ├── claude.py         # Anthropic adapter
│   │   ├── gemini.py         # Google Gemini adapter
│   │   └── openai.py         # OpenAI adapter
│   └── evaluators/
│       ├── semantic.py       # HTTP client → scoring microservice
│       └── llm_judge.py      # HTTP client → scoring microservice
├── scoring-service/
│   ├── main.py               # FastAPI scoring endpoints
│   └── evaluators/
│       ├── semantic.py       # fastembed cosine similarity
│       └── llm_judge.py      # Claude-as-judge grader
├── frontend/
│   ├── src/
│   │   ├── api/client.js     # axios client + BYOK key injection
│   │   ├── hooks/useApiKeys.js
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── RunHistory.jsx
│   │   │   └── RunDetail.jsx
│   │   └── components/NavBar.jsx
│   └── vite.config.js
├── alembic/                  # database migrations
├── docker-compose.yml        # local Postgres
└── render.yaml               # Render deploy config
```

---

## Local Setup

### Prerequisites
- Python 3.12+
- Node.js 22+ (LTS)
- Docker (for local Postgres)

### Backend

```bash
git clone https://github.com/YOUR_USERNAME/llm-eval-platform
cd llm-eval-platform

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# add your API keys to .env

docker compose up -d        # starts Postgres on port 5433
alembic upgrade head        # creates tables

uvicorn backend.main:app --reload
# API running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Scoring Service

```bash
cd scoring-service
pip install -r requirements.txt
uvicorn main:app --reload --port 9000
# Scoring service running at http://localhost:9000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/run` | Run a prompt against a model |
| `GET` | `/runs` | List runs (filter by model, limit) |
| `GET` | `/runs/{id}` | Get single run detail |
| `POST` | `/runs/{id}/score` | Score a run (semantic + judge) |
| `GET` | `/runs/{id}/scores` | Get scores for a run |

### Example — run a prompt

```bash
curl -X POST https://llm-eval-platform-yfn0.onrender.com/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain what a feature store is.",
    "model": "gemini/gemini-3.5-flash",
    "max_tokens": 200,
    "gemini_api_key": "YOUR_GEMINI_KEY"
  }'
```

### Example — score a run

```bash
curl -X POST https://llm-eval-platform-yfn0.onrender.com/runs/1/score \
  -H "Content-Type: application/json" \
  -d '{
    "expected_output": "A feature store is a centralised repository for ML features.",
    "run_semantic": true,
    "run_judge": false
  }'
```

---

## Roadmap

- [ ] Playground UI — run prompts directly from the browser
- [ ] A/B comparison view — same prompt, two models side by side
- [ ] Server-side encrypted key vault + user auth (MAN-44)
- [ ] Retry logging surfaced in run detail UI
- [ ] OpenAI adapter live testing (pending API key)

---

## What I learned building this

This project was deliberately built to mirror real ML platform engineering concerns:

- **Adapter pattern** scales cleanly — adding a new LLM provider took ~30 lines
- **Async matters** — synchronous DB drivers inside async FastAPI caused subtle bugs that only surfaced under concurrency
- **Free tier constraints drive architecture** — sentence-transformers + torch (2GB) forced the scoring microservice split, which turned out to be the right architectural decision anyway
- **Environment variable discipline** — stale shell exports silently overriding `.env` files caused hours of debugging; the fix is always `echo $VAR` before assuming the file is wrong

---

*Built by [Manoj Gosavi](https://github.com/YOUR_USERNAME) — Senior Data Engineer transitioning to ML Platform Engineering*