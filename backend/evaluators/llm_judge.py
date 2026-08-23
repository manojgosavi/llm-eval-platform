import os

import httpx

SCORING_SERVICE_URL = os.getenv("SCORING_SERVICE_URL", "http://localhost:9000")


async def score_llm_judge(
    prompt: str,
    response_text: str,
    api_key: str | None = None,
) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{SCORING_SERVICE_URL}/score/judge",
            json={
                "prompt": prompt,
                "response_text": response_text,
                "api_key": api_key,
            },
        )
        response.raise_for_status()
        return response.json()
