from abc import ABC
from dataclasses import dataclass
import litellm
import asyncio
import random


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

    # transient errors worth retrying — everything else fails immediately
    RETRYABLE_EXCEPTIONS = (
        litellm.exceptions.RateLimitError,
        litellm.exceptions.ServiceUnavailableError,
    )

    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # seconds — doubles each attempt

    async def complete_with_retry(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> CompletionResult:
        """
        Send a prompt to the LLM and return the structured result
        Retries on transient errors.
        """
        last_exception = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return await self.complete(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            except self.RETRYABLE_EXCEPTIONS as e:
                last_exception = e
                if attempt == self.MAX_RETRIES:
                    break  # out of retries, raise the last exception

                delay = (self.BASE_DELAY * (2 ** (attempt - 1))) + random.uniform(
                    0, 0.5
                )  # exponential backoff with jitter
                print(
                    f"[retry] attempt {attempt}/{self.MAX_RETRIES} failed "
                    f"({type(e).__name__}). Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            except RuntimeError:
                raise RuntimeError(
                    f"Request failed after {self.MAX_RETRIES} attempts. "
                    f"Last error: {str(last_exception)}"
                )

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
