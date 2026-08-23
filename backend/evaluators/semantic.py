from fastembed import TextEmbedding
from numpy import dot
from numpy.linalg import norm

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _model


def score_semantic_similarity(actual_output: str, expected_output: str) -> float:
    """
    Score the semantic similarity of the output to the expected output.
    Returns a float between 0.0 and 1.0, where 1.0 means identical meaning.
    """
    model = _get_model()
    embeddings = list(model.embed([actual_output, expected_output]))
    a, b = embeddings[0], embeddings[1]
    score = float(dot(a, b) / (norm(a) * norm(b)))

    # clamp to 0-1 — in rare edge cases (very short/empty strings)
    # cosine similarity can dip slightly negative
    return max(0.0, min(1.0, score))
