import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from evaluators.semantic import score_semantic_similarity
from evaluators.llm_judge import score_llm_judge

load_dotenv()

app = FastAPI(
    title="LLM Eval — Scoring Service",
    version="0.1.0",
)


class SemanticRequest(BaseModel):
    actual_output: str
    expected_output: str


class JudgeRequest(BaseModel):
    prompt: str
    response_text: str
    api_key: str | None = None


class ScoreResult(BaseModel):
    score: float
    reasoning: str | None = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/score/semantic", response_model=ScoreResult)
async def semantic(request: SemanticRequest):
    try:
        score = score_semantic_similarity(
            actual_output=request.actual_output,
            expected_output=request.expected_output,
        )
        return ScoreResult(score=score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score/judge", response_model=ScoreResult)
async def judge(request: JudgeRequest):
    try:
        result = await score_llm_judge(
            prompt=request.prompt,
            response_text=request.response_text,
            api_key=request.api_key,
        )
        return ScoreResult(score=result["score"], reasoning=result["reasoning"])
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
