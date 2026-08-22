import json
import litellm
from dotenv import load_dotenv

load_dotenv()  # ensure ANTHROPIC_API_KEY is available even when this module
# is imported/run standalone, not just via main.py

JUDGE_MODEL = "anthropic/claude-sonnet-4-6"

JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator assessing the quality of an AI assistant's response.

Original prompt given to the assistant:
{prompt}

Assistant's response:
{response}

Evaluate the response on a scale of 1-5 based on:
- Accuracy: Is the information correct?
- Relevance: Does it directly address the prompt?
- Clarity: Is it well-organized and easy to understand?

Return ONLY a valid JSON object in this exact format, with no other text:
{{"score": <integer 1-5>, "reasoning": "<one sentence explanation>"}}
"""


async def score_llm_judge(prompt: str, response_text: str) -> dict:
    """
    Uses an LLM to judge response quality.
    Returns {"score": float (0.0-1.0, normalized), "reasoning": str}
    """
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(prompt=prompt, response=response_text)

    judge_response = await litellm.acompletion(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": judge_prompt}],
        max_tokens=200,
        temperature=0.0,  # we want consistent, deterministic grading — not creative variation
    )

    raw_text = judge_response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_text)
        raw_score = int(parsed["score"])
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, KeyError, ValueError):
        # the judge didn't return valid JSON — don't crash the whole request,
        # surface this clearly instead so we know scoring failed for this run
        raise RuntimeError(f"Judge returned unparseable output: {raw_text[:200]}")

    # normalize 1-5 scale to 0.0-1.0, consistent with our semantic scorer
    normalized_score = (raw_score - 1) / 4  # 1->0.0, 3->0.5, 5->1.0

    return {"score": normalized_score, "reasoning": reasoning}
