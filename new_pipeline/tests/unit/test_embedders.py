"""Sentence-transformer embedder (fusion host only; importorskip-gated)."""

import pytest


def test_sentence_transformer_embedder_normalizes():
    pytest.importorskip("sentence_transformers")
    import numpy as np
    from new_pipeline.execution.embedders import SentenceTransformerEmbedder

    embedder = SentenceTransformerEmbedder()
    vectors = embedder.embed(["alpha beats earnings", "beta misses badly"])
    assert vectors.shape[0] == 2
    np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1.0, rtol=1e-5)


def test_build_rag_engine_sentence_transformer_path_requires_dep():
    pytest.importorskip("sentence_transformers")
    from new_pipeline.config import reload_config
    from new_pipeline.execution.rag_engine import build_rag_engine

    cfg = reload_config()
    cfg.rag.embedder = "sentence_transformer"
    engine = build_rag_engine(cfg)
    assert type(engine.embedder).__name__ == "SentenceTransformerEmbedder"
