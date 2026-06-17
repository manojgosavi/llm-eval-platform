from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from .db import Base


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
