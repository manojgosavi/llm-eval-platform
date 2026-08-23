import os
import httpx

SCORING_SERVICE_URL = os.getenv("SCORING_SERVICE_URL", "http://localhost:9000")


async def score_semantic_similarity(
    actual_output: str,
    expected_output: str,
) -> float:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SCORING_SERVICE_URL}/score/semantic",
            json={
                "actual_output": actual_output,
                "expected_output": expected_output,
            },
        )
        response.raise_for_status()
        return response.json()["score"]
