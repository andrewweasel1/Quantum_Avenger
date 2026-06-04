"""Retrieval-Augmented context for the LLM, offline by default.

"Late chunking": split a document on sentence boundaries with character overlap
so semantic units stay intact. Retrieval blends a lexical score (BM25) with a
dense cosine score from a pluggable embedder; the offline default is a
deterministic hashing embedder (no model download). A sentence-transformers
embedder can be swapped in behind the same ``embed`` interface later.
"""

import hashlib
import re
from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _stable_hash(token: str) -> int:
    return int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big")


def late_chunk(text: str, chunk_size: int = 512, overlap: int = 100) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > chunk_size:
            chunks.append(current.strip())
            current = current[-overlap:] if overlap else ""
        current = f"{current} {sentence}".strip()
    if current.strip():
        chunks.append(current.strip())
    return chunks


class HashingEmbedder:
    """Deterministic bag-of-hashed-tokens embedder (offline; no weights)."""

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float64)
        for i, text in enumerate(texts):
            for token in _tokenize(text):
                vectors[i, _stable_hash(token) % self.dim] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0.0:
                vectors[i] /= norm
        return vectors


@dataclass
class RetrievedChunk:
    text: str
    score: float


class RagEngine:
    def __init__(self, embedder=None, top_k: int = 5, chunk_size: int = 512, overlap: int = 100):
        self.embedder = embedder or HashingEmbedder()
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._chunks: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._bm25: BM25Okapi | None = None

    def index(self, documents: list[str]) -> None:
        chunks: list[str] = []
        for document in documents:
            chunks.extend(late_chunk(document, self.chunk_size, self.overlap))
        self._chunks = chunks
        if not chunks:
            return
        self._embeddings = self.embedder.embed(chunks)
        self._bm25 = BM25Okapi([_tokenize(chunk) for chunk in chunks])

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        if not self._chunks:
            return []
        k = top_k or self.top_k
        query_vector = self.embedder.embed([query])[0]
        dense = self._embeddings @ query_vector  # cosine (rows are unit-normalized)
        lexical = np.asarray(self._bm25.get_scores(_tokenize(query)), dtype=np.float64)
        if lexical.max() > 0.0:
            lexical = lexical / lexical.max()
        combined = 0.5 * dense + 0.5 * lexical
        order = np.argsort(combined)[::-1][:k]
        return [RetrievedChunk(self._chunks[i], float(combined[i])) for i in order]
