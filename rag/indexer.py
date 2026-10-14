from __future__ import annotations

import json
import os
import pathlib

import faiss
import numpy as np

from utils.config import CORPUS_DIR, FAISS_INDEX_PATH
from .embeddings import embed_texts

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def _load_corpus(corpus_dir: str = CORPUS_DIR) -> list[dict]:
    """Load all .txt and .md files from the corpus directory."""
    docs = []
    for path in pathlib.Path(corpus_dir).rglob("*"):
        if path.suffix in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8")
            docs.append({"source": str(path), "text": text})
    return docs


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Extend to next newline to avoid mid-sentence cuts
        if end < len(text):
            newline = text.find("\n", end)
            if newline != -1 and newline - end < 100:
                end = newline
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


def build_index(corpus_dir: str = CORPUS_DIR, index_path: str = FAISS_INDEX_PATH) -> None:
    """Load corpus, chunk, embed, and save FAISS index + metadata."""
    docs = _load_corpus(corpus_dir)
    if not docs:
        raise ValueError(f"No documents found in corpus directory: {corpus_dir}")

    chunks: list[dict] = []
    for doc in docs:
        for chunk in _chunk_text(doc["text"]):
            chunks.append({"source": doc["source"], "text": chunk})

    print(f"Embedding {len(chunks)} chunks from {len(docs)} documents...")
    # Embed in batches of 20 (API limit)
    batch_size = 20
    all_embeddings: list[list[float]] = []
    for i in range(0, len(chunks), batch_size):
        batch = [c["text"] for c in chunks[i : i + batch_size]]
        all_embeddings.extend(embed_texts(batch))

    vectors = np.array(all_embeddings, dtype="float32")
    dim = vectors.shape[1]

    index = faiss.IndexFlatIP(dim)  # Inner product (cosine after L2 norm)
    faiss.normalize_L2(vectors)
    index.add(vectors)

    os.makedirs(index_path, exist_ok=True)
    faiss.write_index(index, os.path.join(index_path, "index.faiss"))
    with open(os.path.join(index_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Index saved to {index_path}/ ({len(chunks)} vectors, dim={dim})")


def load_index(index_path: str = FAISS_INDEX_PATH) -> tuple[faiss.Index, list[dict]]:
    """Load FAISS index and metadata from disk."""
    index = faiss.read_index(os.path.join(index_path, "index.faiss"))
    with open(os.path.join(index_path, "metadata.json"), encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata
