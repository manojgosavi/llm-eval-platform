from sentence_transformers import SentenceTransformer, util

_model = SentenceTransformer("all-MiniLM-L6-v2")


def score_semantic_similarity(actual_output: str, expected_output: str) -> float:
    """
    Score the semantic similarity of the output to the expected output.
    Returns a float between 0.0 and 1.0, where 1.0 means identical meaning.
    """
    embeddings = _model.encode([actual_output, expected_output])
    similarity = util.cos_sim(embeddings[0], embeddings[1])

    # cos_sim returns a tensor; extract the scalar float
    score = similarity.item()

    # clamp to 0-1 — in rare edge cases (very short/empty strings)
    # cosine similarity can dip slightly negative
    return max(0.0, min(1.0, score))
