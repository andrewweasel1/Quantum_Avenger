"""Neural embedder for the RAG engine (live/heavy path).

Mirrors the FinBERT pattern: lazy import of ``sentence-transformers`` (installed
via ``requirements-fusion.txt``), coverage-omitted, and exercised by an
``importorskip`` test. Offline runs keep the deterministic ``HashingEmbedder``
default in ``rag_engine.py`` — this class swaps in behind the same
``embed(texts) -> ndarray`` interface via ``rag.embedder: sentence_transformer``.
"""

import numpy as np


class SentenceTransformerEmbedder:  # pragma: no cover - heavy weights (fusion host)
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float64)
