from new_pipeline.features.registry import FeatureMetadata, feature_registry
from new_pipeline.features.compiler import PandasFeatureCompiler


def test_feature_registry_can_register_and_query():
    feature_registry.clear()

    metadata = FeatureMetadata(
        name="test_feature",
        description="A synthetic test feature.",
        source="test",
        window="1d",
        dtype="float",
    )
    feature_registry.register("test_feature", metadata)

    assert "test_feature" in feature_registry.list_features()
    assert feature_registry.get("test_feature")["name"] == "test_feature"
    assert feature_registry.get("test_feature")["description"] == "A synthetic test feature."


def test_feature_compiler_registers_feature_metadata():
    feature_registry.clear()
    compiler = PandasFeatureCompiler()

    assert "returns" in feature_registry.list_features()
    assert feature_registry.get("atr_14")["window"] == "14d"
    assert feature_registry.get("average_volume_20")["dtype"] == "float"


def test_feature_registry_persists_and_loads(tmp_path):
    feature_registry.clear()

    metadata = FeatureMetadata(
        name="persist_feature",
        description="Persisted test feature.",
        source="test",
        window="1d",
        dtype="float",
    )
    feature_registry.register("persist_feature", metadata)

    path = tmp_path / "feature_registry_test.yaml"
    feature_registry.save(path)

    feature_registry.clear()
    assert feature_registry.list_features() == []

    feature_registry.load(path)
    assert "persist_feature" in feature_registry.list_features()
    assert feature_registry.get("persist_feature")["description"] == "Persisted test feature."
