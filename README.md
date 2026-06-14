# LLM Eval Platform

An open-source platform to A/B test and score LLM outputs across providers
(Claude, GPT-4o, Gemini) using latency, cost, token, and semantic quality metrics.

## Stack
- **Backend** — FastAPI + litellm + SQLAlchemy + Postgres
- **Frontend** — React + Recharts *(coming)*
- **Infra** — Docker Compose

## Status
🚧 Active development — Week 1 complete (core eval loop)

## Run locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Architecture
*(diagram coming)*