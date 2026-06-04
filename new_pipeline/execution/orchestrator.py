"""LangGraph trade orchestrator: Verdict -> Grader -> Risk-Veto -> Execute/Fallback.

The deterministic vs. probabilistic boundary in one place: the LLM nodes
(verdict, grader) produce only narrative stances; the Risk-Veto node calls the
Shield Agent (the exact function the backtest uses); execution goes through the
broker adapter. Every terminal outcome is appended to the veto ledger. A
rejected verdict is retried up to ``max_retries`` times before falling back.
"""

from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from new_pipeline.adapters.base import LLMClient, Verdict
from new_pipeline.core.logging import new_trace_id
from new_pipeline.execution.broker import BrokerAdapter
from new_pipeline.execution.grader import Grader
from new_pipeline.execution.verdict_engine import VerdictEngine
from new_pipeline.execution.veto_ledger import VetoLedger, VetoRecord
from new_pipeline.features.shields import evaluate_risk_veto_gates


@dataclass
class TradeRequest:
    signal: str
    symbol: str
    entry_price: float
    atr: float
    atr_multiplier: float
    account_capital: float
    max_risk_pct: float
    current_qty: float
    adv_20: float
    volume_today: float
    volatility: float
    context: list[str] = field(default_factory=list)
    dsr: float = 0.0


class _State(TypedDict, total=False):
    request: TradeRequest
    verdict: str
    grader_approved: bool
    grader_feedback: str
    shield_approved: bool
    position_size: float
    execution_id: str
    attempts: int
    outcome: str


class TradeOrchestrator:
    def __init__(
        self,
        llm: LLMClient,
        broker: BrokerAdapter,
        ledger: VetoLedger,
        max_retries: int = 3,
        tif: str = "day",
    ):
        self._verdict_engine = VerdictEngine(llm)
        self._grader = Grader(llm)
        self._broker = broker
        self._ledger = ledger
        self._max_retries = max_retries
        self._tif = tif
        self._app = self._build_graph()

    def run(self, request: TradeRequest) -> _State:
        return self._app.invoke({"request": request, "attempts": 0})

    def _build_graph(self):
        graph = StateGraph(_State)
        graph.add_node("verdict", self._verdict_node)
        graph.add_node("grader", self._grader_node)
        graph.add_node("risk_veto", self._risk_veto_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("fallback", self._fallback_node)
        graph.add_edge(START, "verdict")
        graph.add_edge("verdict", "grader")
        graph.add_conditional_edges(
            "grader",
            self._route_after_grader,
            {"approved": "risk_veto", "retry": "verdict", "reject": "fallback"},
        )
        graph.add_conditional_edges(
            "risk_veto",
            self._route_after_veto,
            {"execute": "execute", "veto": "fallback"},
        )
        graph.add_edge("execute", END)
        graph.add_edge("fallback", END)
        return graph.compile()

    # --- nodes -------------------------------------------------------------
    def _verdict_node(self, state: _State) -> dict:
        request = state["request"]
        verdict = self._verdict_engine.generate(request.signal, request.symbol, request.context)
        return {"verdict": verdict.stance, "attempts": state.get("attempts", 0) + 1}

    def _grader_node(self, state: _State) -> dict:
        request = state["request"]
        result = self._grader.grade(Verdict(state["verdict"], ""), request.context)
        return {"grader_approved": result.approved, "grader_feedback": result.feedback}

    def _risk_veto_node(self, state: _State) -> dict:
        request = state["request"]
        approved, size = evaluate_risk_veto_gates(
            request.entry_price,
            request.atr,
            request.atr_multiplier,
            request.account_capital,
            request.max_risk_pct,
            request.current_qty,
            request.adv_20,
            request.volume_today,
            request.volatility,
        )
        return {"shield_approved": bool(approved), "position_size": float(size)}

    def _execute_node(self, state: _State) -> dict:
        request = state["request"]
        limit_price = round(request.entry_price + 0.1 * request.atr, 2)
        receipt = self._broker.submit_order(
            {
                "symbol": request.symbol,
                "qty": int(state["position_size"]),
                "side": "buy",
                "limit_price": limit_price,
                "tif": self._tif,
            }
        )
        execution_id = str(receipt.get("order_id", new_trace_id()))
        self._ledger.append(
            VetoRecord(
                symbol=request.symbol,
                signal=request.signal,
                entry_price=request.entry_price,
                veto_reason="executed",
                veto_gate="none",
                dsr=request.dsr,
                position_size=int(state["position_size"]),
                execution_id=execution_id,
            )
        )
        return {"execution_id": execution_id, "outcome": "executed"}

    def _fallback_node(self, state: _State) -> dict:
        request = state["request"]
        if not state.get("grader_approved", False):
            gate, reason = "grader", "grader rejected after retries"
        else:
            gate, reason = "shield", "risk veto"
        self._ledger.append(
            VetoRecord(
                symbol=request.symbol,
                signal=request.signal,
                entry_price=request.entry_price,
                veto_reason=reason,
                veto_gate=gate,
                dsr=request.dsr,
                position_size=0,
                execution_id="",
            )
        )
        return {"outcome": "vetoed"}

    # --- routers -----------------------------------------------------------
    def _route_after_grader(self, state: _State) -> str:
        if state.get("grader_approved"):
            return "approved"
        if state.get("attempts", 0) < self._max_retries:
            return "retry"
        return "reject"

    def _route_after_veto(self, state: _State) -> str:
        return "execute" if state.get("shield_approved") else "veto"
