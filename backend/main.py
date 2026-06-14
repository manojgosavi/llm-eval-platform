import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field

from adapters.base import BaseLLMAdapter, CompletionResult
from adapters.claude import ClaudeAdapter

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


def get_adapter() -> BaseLLMAdapter:
    return ClaudeAdapter()


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
    adapter: BaseLLMAdapter = Depends(get_adapter),
):
    """
    Run a single prompt against a model and return
    completion + latency + cost + context metrics.
    """
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
    )
