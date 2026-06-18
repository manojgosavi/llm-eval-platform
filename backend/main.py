from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import select
from .adapters.base import BaseLLMAdapter, CompletionResult
from .adapters.claude import ClaudeAdapter
from .adapters.openai import OpenAIAdapter
from .adapters.gemini import GeminiAdapter

from .db import get_db, AsyncSession
from .models import EvalRun

from .evaluators.semantic import score_semantic_similarity
from .evaluators.llm_judge import score_llm_judge
from .models import EvalScore


load_dotenv()


class RunRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The prompt to evaluate")
    model: str = Field(
        default="anthropic/claude-sonnet-4-6", description="LiteLLM model string"
    )
    max_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    system_prompt: str | None = Field(
        default=None, description="Optional system prompt"
    )


class RunResponse(BaseModel):
    text: str
    model: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    max_tokens_requested: int
    context_used_pct: float
    was_truncated: bool
    created_at: datetime


class Config:
    from_attributes = True


class RunSummary(BaseModel):
    id: int
    prompt: str
    model: str
    latency_ms: float
    cost_usd: float
    was_truncated: bool
    created_at: datetime

    class Config:
        from_attributes = True


def get_adapter_for_model(model: str) -> BaseLLMAdapter:
    if model.startswith("anthropic/"):
        return ClaudeAdapter()
    elif model.startswith("openai/"):
        return OpenAIAdapter()
    elif model.startswith("gemini/"):
        return GeminiAdapter()
    else:
        raise ValueError(
            f"No adapter found for model '{model}'. "
            f"Expected prefix: anthropic/, openai/, or gemini/"
        )


app = FastAPI(
    title="LLM Eval Platform",
    description="A/B test and score LLM outputs across providers",
    version="0.1.0",
)


@app.get("/health")
async def health():
    """Quick Liveness check - useful for Docker and CLI"""
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(
    request: RunRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run a single prompt against a model and return
    completion + latency + cost + context metrics.
    """
    try:
        adapter = get_adapter_for_model(request.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        result: CompletionResult = await adapter.complete(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # persist the run
    db_run = EvalRun(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        model=result.model,
        max_tokens_requested=result.max_tokens_requested,
        temperature=request.temperature,
        response_text=result.text,
        latency_ms=result.latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=result.cost_usd,
        context_used_pct=result.context_used_pct,
        was_truncated=result.was_truncated,
    )
    db.add(db_run)
    await db.commit()
    await db.refresh(db_run)

    return RunResponse(
        text=result.text,
        model=result.model,
        latency_ms=result.latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=result.cost_usd,
        max_tokens_requested=request.max_tokens,
        context_used_pct=result.context_used_pct,
        was_truncated=result.was_truncated,
        created_at=db_run.created_at,
    )


@app.get("/runs", response_model=list[RunSummary])
async def list_runs(
    limit: int = 20,
    model: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List recent runs, optionally filtered by model.
    """
    query = select(EvalRun).order_by(EvalRun.created_at.desc()).limit(limit)
    if model:
        query = query.where(EvalRun.model == model)
    results = await db.execute(query)
    runs = results.scalars().all()
    return runs


@app.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch a single run by id."""
    result = await db.execute(select(EvalRun).where(EvalRun.id == run_id))
    run = result.scalar_one_or_none()

    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    return RunResponse(
        id=run.id,
        text=run.response_text,
        model=run.model,
        latency_ms=run.latency_ms,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        cost_usd=run.cost_usd,
        max_tokens_requested=run.max_tokens_requested,
        context_used_pct=run.context_used_pct,
        was_truncated=run.was_truncated,
        created_at=run.created_at,
    )


class ScoreResult(BaseModel):
    scorer_type: str
    score: float
    reasoning: str | None = None

    class Config:
        from_attributes = True


class ScoreRequest(BaseModel):
    expected_output: str | None = Field(
        default=None, description="Required for semantic similarity scoring"
    )
    run_semantic: bool = Field(default=True)
    run_judge: bool = Field(default=True)

    class Config:
        from_attributes = True


@app.post("/runs/{run_id}/score", response_model=list[ScoreResult])
async def score_run(
    run_id: int,
    request: ScoreRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. fetch the run — fail fast if it doesn't exist
    result = await db.execute(select(EvalRun).where(EvalRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    new_scores = []

    # 2. semantic similarity — only if expected_output was provided
    if request.run_semantic and request.expected_output:
        similarity = score_semantic_similarity(
            actual_output=run.response_text,
            expected_output=request.expected_output,
        )
        db_score = EvalScore(
            run_id=run.id,
            scorer_type="semantic_similarity",
            score=similarity,
            expected_output=request.expected_output,
        )
        db.add(db_score)
        new_scores.append(db_score)

    # 3. LLM-as-judge — independent of expected_output
    if request.run_judge:
        try:
            judge_result = await score_llm_judge(
                prompt=run.prompt,
                response_text=run.response_text,
            )
            db_score = EvalScore(
                run_id=run.id,
                scorer_type="llm_judge",
                score=judge_result["score"],
                reasoning=judge_result["reasoning"],
            )
            db.add(db_score)
            new_scores.append(db_score)
        except RuntimeError as e:
            # judge failed to return parseable output — don't crash the whole
            # request if semantic scoring already succeeded above
            raise HTTPException(status_code=502, detail=str(e))

    await db.commit()
    for s in new_scores:
        await db.refresh(s)

    return new_scores
