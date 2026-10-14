from __future__ import annotations

import os

import faiss
import numpy as np

from utils.config import FAISS_INDEX_PATH
from .embeddings import embed_query
from .indexer import build_index, load_index

_index: faiss.Index | None = None
_metadata: list[dict] | None = None


def _ensure_index(index_path: str = FAISS_INDEX_PATH) -> tuple[faiss.Index, list[dict]]:
    global _index, _metadata
    if _index is None:
        if not os.path.exists(os.path.join(index_path, "index.faiss")):
            print("FAISS index not found. Building from corpus...")
            build_index()
        _index, _metadata = load_index(index_path)
    return _index, _metadata


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Return the top-k most relevant chunks for the given query."""
    index, metadata = _ensure_index()

    query_vec = np.array([embed_query(query)], dtype="float32")
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = metadata[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)
    return results


def format_context(results: list[dict]) -> str:
    """Format retrieval results into a context string for the LLM."""
    if not results:
        return "No relevant documents found."
    parts = []
    for i, r in enumerate(results, 1):
        source = os.path.basename(r["source"])
        parts.append(f"[{i}] (source: {source}, score: {r['score']:.3f})\n{r['text']}")
    return "\n\n---\n\n".join(parts)
