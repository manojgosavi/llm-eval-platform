import time
import litellm
from litellm import AuthenticationError, RateLimitError, APIError

from .base import BaseLLMAdapter, CompletionResult


class ClaudeAdapter(BaseLLMAdapter):
    DEFAULT_MODEL = "anthropic/claude-sonnet-4-6"

    async def complete(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> CompletionResult:

        context_window = self.CONTEXT_WINDOWS.get(model, 100000)

        try:
            start = time.perf_counter()
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "context": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            latency_ms = (time.perf_counter() - start) * 1000

        except AuthenticationError:
            raise ValueError("Invalid Antropic API key. Check your .env file.")
        except RateLimitError:
            raise RuntimeError(
                f"Rate limit exceeded for model {model}. Back off and retry."
            )
        except APIError as e:
            raise RuntimeError(f"Anthropic API error for model {model}: str{e}")

        # extract from litellm response
        text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost_usd = litellm.completion_cost(completion_response=response)

        # derive our computed fields
        was_truncated = output_tokens >= max_tokens
        context_used_pct = round(
            (input_tokens + output_tokens) / context_window * 100, 2
        )

        return CompletionResult(
            text=text,
            model=model,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(cost_usd, 6),
            max_tokens_requested=max_tokens,
            context_used_pct=context_used_pct,
            was_truncated=was_truncated,
        )
