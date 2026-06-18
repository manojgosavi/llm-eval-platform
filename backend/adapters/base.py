from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompletionResult:
    text: str
    model: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    max_tokens_requested: int
    context_used_pct: float
    was_truncated: bool


class BaseLLMAdapter(ABC):
    # model context windows — used to compute context_used_pct
    CONTEXT_WINDOWS = {
        "anthropic/claude-sonnet-4-6": 200000,
        "openai/gpt-4o": 128000,
        "openai/gpt-4o-mini": 128000,
        "gemini/gemini-3.5-flash": 1000000,
    }

    async def complete(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> CompletionResult:
        """
        Send a prompt to the LLM and return the structured result
        Every adapter should implement this method.
        """
        pass
