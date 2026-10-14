from __future__ import annotations

import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from utils.config import GCP_PROJECT, GCP_LOCATION

_model: TextEmbeddingModel | None = None


def _get_model() -> TextEmbeddingModel:
    global _model
    if _model is None:
        vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
        _model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    return _model


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Embed a list of texts using Vertex AI text-embedding-004."""
    model = _get_model()
    inputs = [TextEmbeddingInput(text=t, task_type=task_type) for t in texts]
    embeddings = model.get_embeddings(inputs)
    return [e.values for e in embeddings]


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query], task_type="RETRIEVAL_QUERY")[0]
