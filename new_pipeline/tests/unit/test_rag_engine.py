from new_pipeline.execution.rag_engine import RagEngine, late_chunk


def test_late_chunk_splits_on_sentences():
    chunks = late_chunk("First sentence. Second sentence. Third one.", chunk_size=20, overlap=0)
    assert len(chunks) >= 2
    assert all(chunk for chunk in chunks)


def test_retrieve_returns_relevant_chunk_first():
    rag = RagEngine(top_k=1)
    rag.index(
        [
            "Apple expanded its AI workforce. Earnings beat estimates.",
            "Oil prices fell on demand worries. Energy stocks dropped.",
        ]
    )
    hits = rag.retrieve("AI workforce earnings")
    assert len(hits) == 1
    assert "AI workforce" in hits[0].text


def test_retrieve_on_empty_index():
    assert RagEngine().retrieve("anything") == []


def test_top_k_caps_results():
    rag = RagEngine(top_k=5)
    rag.index(["A cat sat.", "A dog ran.", "Birds fly high.", "Fish swim deep."])
    assert len(rag.retrieve("animals", top_k=2)) == 2
