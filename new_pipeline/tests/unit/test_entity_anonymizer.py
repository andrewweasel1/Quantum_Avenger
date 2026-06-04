from new_pipeline.execution.entity_anonymizer import EntityAnonymizer


def test_masks_known_entities_and_roundtrips():
    anon = EntityAnonymizer(["Apple", "AAPL", "Microsoft"])
    original = "Apple and AAPL rose; Microsoft fell."
    result = anon.anonymize(original)
    assert "Apple" not in result.text
    assert "AAPL" not in result.text
    assert "[COMPANY_" in result.text
    assert EntityAnonymizer.deanonymize(result.text, result.mapping) == original


def test_longest_match_first():
    anon = EntityAnonymizer(["Apple", "Apple Inc"])
    result = anon.anonymize("Apple Inc reported earnings.")
    assert result.text.count("[COMPANY_") == 1  # "Apple Inc" masked as one entity
    assert "Inc" not in result.text


def test_case_insensitive():
    anon = EntityAnonymizer(["apple"])
    assert "Apple" not in anon.anonymize("Apple surged").text


def test_unknown_terms_untouched():
    result = EntityAnonymizer(["Apple"]).anonymize("Banana prices rose")
    assert result.text == "Banana prices rose"
    assert result.mapping == {}
