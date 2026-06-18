from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from .db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)

    # what was asked
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    model = Column(String, nullable=False, index=True)
    max_tokens_requested = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)

    # what came back
    response_text = Column(Text, nullable=False)

    # metrics
    latency_ms = Column(Float, nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    context_used_pct = Column(Float, nullable=False)
    was_truncated = Column(Boolean, nullable=False)

    # metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    scores = relationship(
        "EvalScore", back_populates="run", cascade="all, delete-orphan"
    )


class EvalScore(Base):
    __tablename__ = "eval_scores"

    id = Column(Integer, primary_key=True, index=True)

    run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False, index=True)
    scorer_type = Column(String, nullable=False)  # "semantic_similarity" | "llm_judge"
    score = Column(Float, nullable=False)  # normalized 0.0-1.0
    reasoning = Column(Text, nullable=True)  # judge's explanation, null for semantic
    expected_output = Column(
        Text, nullable=True
    )  # what we compared against, for semantic

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    run = relationship("EvalRun", back_populates="scores")
