"""Deterministic quant tool registry (the FastMCP surface, G1).

The LLM is forbidden from doing math; every quantity it needs comes from one of
these tools, which simply wrap the project's existing deterministic functions
(no logic duplication) and return structured JSON-shaped dicts. ``to_jsonrpc``
emits the JSON-RPC tool schema an MCP server (or a live FastMCP adapter)
advertises. Building the registry needs no network, so it is fully testable
offline.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    interpret_dsr,
)
from new_pipeline.evaluation.tearsheet import summary_metrics
from new_pipeline.features.shields import (
    calculate_kelly_position_size,
    enforce_volatility_stop,
    evaluate_risk_veto_gates,
)
from new_pipeline.features.slippage import hydrodynamic_slippage_bps
from new_pipeline.tournament.simulator import sharpe_ratio

_JSON_NUMBER = "number"
_JSON_ARRAY = "array"


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, str]
    handler: Callable[..., dict]

    def __call__(self, **kwargs) -> dict:
        return self.handler(**kwargs)

    def to_jsonrpc(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {key: {"type": kind} for key, kind in self.parameters.items()},
                "required": list(self.parameters),
            },
        }


@dataclass
class ToolRegistry:
    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def call(self, name: str, **kwargs) -> dict:
        return self._tools[name](**kwargs)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def schemas(self) -> list[dict]:
        return [tool.to_jsonrpc() for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)


def _veto_gates_tool(**kw) -> dict:
    approved, size = evaluate_risk_veto_gates(
        kw["entry_price"],
        kw["atr"],
        kw["atr_multiplier"],
        kw["account_capital"],
        kw["max_risk_pct"],
        kw["current_qty"],
        kw["adv_20"],
        kw["volume_today"],
        kw["volatility"],
    )
    return {"approved": bool(approved), "position_size": float(size)}


def _kelly_tool(**kw) -> dict:
    size = calculate_kelly_position_size(
        kw["entry_price"], kw["atr"], kw["atr_multiplier"],
        kw["account_capital"], kw["max_risk_pct"],
    )
    return {"position_size": float(size)}


def _vol_stop_tool(**kw) -> dict:
    stop, triggered = enforce_volatility_stop(
        kw["entry_price"], kw["atr"], kw["atr_multiplier"],
        kw["current_price"], kw["highest_price"],
    )
    return {"stop_level": float(stop), "triggered": bool(triggered)}


def _slippage_tool(**kw) -> dict:
    bps = hydrodynamic_slippage_bps(
        kw["order_notional"], kw["volatility"], kw["volume_today"],
        kw.get("slippage_constant", 0.5), kw.get("bps_scaler", 10000.0),
    )
    ceiling = kw.get("max_slippage_bps", 50.0)
    return {"slippage_bps": float(bps), "approval": bool(bps <= ceiling)}


def _sharpe_tool(**kw) -> dict:
    return {"sharpe": sharpe_ratio(kw["returns"])}


def _dsr_tool(**kw) -> dict:
    dsr = compute_deflated_sharpe_ratio(kw["returns"], kw["trial_sharpes"])
    return {"dsr": dsr, "verdict": interpret_dsr(dsr)}


def _expected_max_sharpe_tool(**kw) -> dict:
    return {"expected_max_sharpe": expected_max_sharpe(kw["var_trials"], kw["n_trials"])}


def _summary_tool(**kw) -> dict:
    return summary_metrics(kw["returns"])


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    _risk = {
        "entry_price": _JSON_NUMBER,
        "atr": _JSON_NUMBER,
        "atr_multiplier": _JSON_NUMBER,
        "account_capital": _JSON_NUMBER,
        "max_risk_pct": _JSON_NUMBER,
    }
    registry.register(
        Tool(
            "evaluate_risk_veto_gates",
            "Run the Shield Agent's five veto gates.",
            {**_risk, "current_qty": _JSON_NUMBER, "adv_20": _JSON_NUMBER,
             "volume_today": _JSON_NUMBER, "volatility": _JSON_NUMBER},
            _veto_gates_tool,
        )
    )
    registry.register(
        Tool("calculate_kelly_position_size", "Risk-based share count.", _risk, _kelly_tool)
    )
    registry.register(
        Tool(
            "enforce_volatility_stop",
            "Hard + trailing ATR stop and whether it is triggered.",
            {"entry_price": _JSON_NUMBER, "atr": _JSON_NUMBER, "atr_multiplier": _JSON_NUMBER,
             "current_price": _JSON_NUMBER, "highest_price": _JSON_NUMBER},
            _vol_stop_tool,
        )
    )
    registry.register(
        Tool(
            "calculate_dynamic_slippage",
            "Hydrodynamic slippage (bps) and whether it clears the ceiling.",
            {"order_notional": _JSON_NUMBER, "volatility": _JSON_NUMBER,
             "volume_today": _JSON_NUMBER},
            _slippage_tool,
        )
    )
    registry.register(Tool("sharpe_ratio", "Annualized Sharpe of a return series.",
                           {"returns": _JSON_ARRAY}, _sharpe_tool))
    registry.register(Tool("deflated_sharpe_ratio", "Deflated Sharpe probability + verdict.",
                           {"returns": _JSON_ARRAY, "trial_sharpes": _JSON_ARRAY}, _dsr_tool))
    registry.register(Tool("expected_max_sharpe", "Expected max Sharpe under the null.",
                           {"var_trials": _JSON_NUMBER, "n_trials": _JSON_NUMBER},
                           _expected_max_sharpe_tool))
    registry.register(Tool("summary_metrics", "Sharpe/drawdown/win-rate/profit-factor summary.",
                           {"returns": _JSON_ARRAY}, _summary_tool))
    return registry
