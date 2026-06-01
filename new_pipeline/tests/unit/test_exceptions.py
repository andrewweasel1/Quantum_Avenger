from new_pipeline.core.exceptions import QuantumAvengerError, ConfigurationError


def test_custom_exception_hierarchy():
    exc = ConfigurationError("config failed")
    assert isinstance(exc, QuantumAvengerError)
    assert str(exc) == "config failed"
