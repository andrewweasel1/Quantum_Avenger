from new_pipeline.execution.mcp_tools import build_default_registry


def test_registry_builds_tools():
    registry = build_default_registry()
    assert len(registry) >= 8
    assert "evaluate_risk_veto_gates" in registry.names()


def test_tool_call_returns_structured_dict():
    out = build_default_registry().call(
        "calculate_kelly_position_size",
        entry_price=100.0,
        atr=1.0,
        atr_multiplier=2.0,
        account_capital=100000.0,
        max_risk_pct=0.02,
    )
    assert out["position_size"] == 1000.0


def test_jsonrpc_schema_shape():
    schema = build_default_registry().get("calculate_dynamic_slippage").to_jsonrpc()
    assert schema["name"] == "calculate_dynamic_slippage"
    assert schema["inputSchema"]["type"] == "object"
    assert "order_notional" in schema["inputSchema"]["properties"]


def test_dsr_tool_matches_function():
    out = build_default_registry().call(
        "deflated_sharpe_ratio",
        returns=[0.01, -0.005, 0.02, 0.0, 0.015] * 20,
        trial_sharpes=[0.1, 0.2, 0.15],
    )
    assert 0.0 <= out["dsr"] <= 1.0
    assert out["verdict"] in {"overfit", "insignificant", "promote"}
