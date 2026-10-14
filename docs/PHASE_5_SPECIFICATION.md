# Phase 5: Live Execution & LangGraph Orchestration - Detailed Specification

> **Implementation status: ◐ OFFLINE‑COMPLETE, live deferred.** Implemented & offline‑testable in `new_pipeline/execution/`: the LangGraph Verdict→Grader→Risk‑Veto(Shield)→Execute graph, the deterministic FastMCP tools, the entity anonymizer (offline **gazetteer** `entity_anonymizer.py` + live **spaCy** `anonymizer_spacy.py`), the verdict/grader, and the append‑only veto/trade ledgers. **Genuinely remaining:** (1) wire a **live Ollama `LLMClient`** — today the verdict path uses `FakeLLMClient`; (2) the RAG engine uses a **hashing‑bag embedder placeholder** and `retrieve()` is **not yet wired into the graph**, so the agentic **evidence_for / evidence_against / missing_evidence** loop is unbuilt. See IMPLEMENTATION_STATUS §1–§2. *Original build spec; current state in `ARCHITECTURE_ROADMAP.md`.*

**Duration**: 2.5 weeks  
**Target Date**: Complete by early August (after Phase 4)  
**Success Criteria**: FastMCP server running; LangGraph state machine working; end-to-end verdict flow; LLM + quant fusion; 85%+ test coverage

---

## 1. Phase 5 Architecture Overview

### 1.1 System Context (Fusion of Quantitative + LLM)

```
┌────────────────────────────────────────────────────────────────────┐
│  PHASES 1-4 (Complete): Infrastructure, Features, Training, Eval  │
├────────────────────────────────────────────────────────────────────┤
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PHASE 5: LIVE EXECUTION & LANGGRAPH ORCHESTRATION          │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  LAYER 0: DETERMINISTIC FOUNDATION                          │  │
│  │  ├─ Shield Agent (Numba JIT, <100µs veto gates)            │  │
│  │  ├─ Risk calculations (Kelly sizing, slippage, liquidity)  │  │
│  │  ├─ Position tracking (current quantity, P&L)              │  │
│  │  └─ Alpaca real-time feed (price, volume, fundamentals)    │  │
│  │                                                              │  │
│  │  LAYER 1: FASTMCP BRIDGE (Deterministic ↔ LLM)             │  │
│  │  ├─ FastMCP server (Python sidecar process)                │  │
│  │  ├─ Tool registration (30+ quant functions exposed)        │  │
│  │  ├─ JSON-RPC interface (quant → LLM, LLM → quant)          │  │
│  │  ├─ Tool schemas (input/output specs)                      │  │
│  │  └─ Error handling (exceptions wrapped in JSON)            │  │
│  │                                                              │  │
│  │  LAYER 2: ENTITY ANONYMIZATION (Defeat look-ahead bias)    │  │
│  │  ├─ spaCy NER pipeline (extract entities)                  │  │
│  │  ├─ Entity masking (Apple → [COMPANY_A], ticker → [...])   │  │
│  │  ├─ Vectorized batch processing (100+ articles/sec)        │  │
│  │  └─ Reverse mapping (results → original entities)          │  │
│  │                                                              │  │
│  │  LAYER 3: RETRIEVAL AUGMENTED GENERATION (RAG)             │  │
│  │  ├─ Late chunking (preserve semantic context)              │  │
│  │  ├─ Vector embeddings (sentence-transformers)              │  │
│  │  ├─ Faiss index (fast similarity search)                   │  │
│  │  ├─ BM25 ranking (lexical fallback)                        │  │
│  │  └─ Reranking (LLM-based context scoring)                  │  │
│  │                                                              │  │
│  │  LAYER 4: LANGGRAPH STATE MACHINE (Agentic Orchestration)  │  │
│  │  ├─ State: {signal, context, grader_feedback, verdict}     │  │
│  │  ├─ Node: Verdict Engine (LLM generates alpha narrative)   │  │
│  │  ├─ Node: Grader (LLM validates verdict vs context)        │  │
│  │  ├─ Node: Risk Veto (Shield Agent kills bad verdicts)      │  │
│  │  ├─ Node: Execution (submit to Alpaca if approved)         │  │
│  │  └─ Edges: Conditional routing (pass/fail/retry)           │  │
│  │                                                              │  │
│  │  LAYER 5: VETO LEDGER & MONITORING                         │  │
│  │  ├─ Log all decisions (why approved/rejected)              │  │
│  │  ├─ Real-time dashboard (KPIs, veto reasons)               │  │
│  │  ├─ Alert system (anomalies, liquidity breaches)           │  │
│  │  └─ Trade log (fills, slippage, P&L)                       │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│       Uses all Phases 1-4 + Alpaca Live API                       │
│       Produces: Trade fills, ledgers, monitoring data             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/execution/            # ✨ NEW: Live execution module
├── __init__.py
├── alpaca_connector.py              # ✨ NEW: Real-time market data
├── mcp_server.py                    # ✨ NEW: FastMCP bridge
├── entity_anonymizer.py             # ✨ NEW: spaCy NER masking
├── rag_engine.py                    # ✨ NEW: Late chunking + Faiss
├── state_machine.py                 # ✨ NEW: LangGraph orchestrator
├── verdict_engine.py                # ✨ NEW: LLM verdict generation
├── grader.py                        # ✨ NEW: LLM verdict validation
├── veto_ledger.py                   # ✨ NEW: Audit trail
├── orchestrator.py                  # ✨ NEW: Live execution controller
└── tests/
    ├── test_alpaca_connector.py
    ├── test_mcp_server.py
    ├── test_entity_anonymizer.py
    ├── test_rag_engine.py
    ├── test_state_machine.py
    ├── test_verdict_engine.py
    ├── test_grader.py
    └── benchmarks/
        ├── bench_langgraph_latency.py
        └── bench_mcp_throughput.py
```

---

## 2. FastMCP Bridge: Deterministic ↔ LLM

### 2.1 Theory: JSON-RPC Isolation

**Problem**: LLMs must NOT calculate risk or slippage (hallucination risk)

**Solution**: Expose all quantitative functions via FastMCP JSON-RPC server
- LLM calls: "execute_kelly_sizing(capital=100k, risk_distance=5.0, win_rate=0.6)"
- Server responds: `{"position_size": 8000, "stop_loss": 95.0}`
- No calculation leak into LLM context

### 2.2 Module: `execution/mcp_server.py`

**File: `execution/mcp_server.py`**

#### 2.2.1 MCP Tool Registration

**Class: `QuantumAvengerMCPServer`**

```python
from fastmcp import FastMCP, Context
import json

class QuantumAvengerMCPServer:
    """FastMCP server exposing all quant functions to LLM.
    
    Purpose:
        - Deterministic calculation engine for LLM
        - JSON-RPC interface (no code execution risk)
        - Schema validation (input/output types)
        - Prevents hallucination (forced use of real data)
    
    Methods:
        __init__: Initialize server + register tools
        run: Start listening on stdio
    """
    
    def __init__(self, config: AppConfig):
        """Initialize FastMCP server with tool registry.
        
        Args:
            config: Application configuration.
        
        Server Configuration:
            - name: "Quantum Avenger MCP Server"
            - version: "1.0.0"
            - capabilities: ["tools"]
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize FastMCP server
        self.mcp = FastMCP(
            name="Quantum Avenger MCP Server",
            version="1.0.0"
        )
        
        # Register all quant tools
        self._register_risk_tools()
        self._register_feature_tools()
        self._register_market_tools()
        self._register_position_tools()
        
        self.logger.info("MCP server initialized with 30+ tools")
    
    def _register_risk_tools(self) -> None:
        """Register risk management tools."""
        
        @self.mcp.tool()
        def calculate_kelly_position_size(
            account_capital: float,
            risk_distance: float,
            win_rate: float,
            win_loss_ratio: float = 1.0,
            conservative_factor: float = 0.75
        ) -> dict:
            """Calculate position size using Kelly criterion.
            
            Args:
                account_capital: Total account equity (USD).
                risk_distance: Distance to stop loss (USD/share).
                win_rate: Historical win rate (0-1).
                win_loss_ratio: Average win / average loss.
                conservative_factor: Kelly * this (typically 0.75).
            
            Returns:
                {
                    "position_size": int (shares),
                    "position_notional": float (USD),
                    "risk_amount": float (USD),
                    "kelly_pct": float (0-5%),
                    "explanation": str
                }
            
            Formula:
                Kelly % = (p*b - q) / b
                Capped at 5% of capital
                Applied with 0.75× conservative factor
            """
            from shields import calculate_kelly_position_size as calc_kelly
            
            result = calc_kelly(
                account_capital,
                risk_distance,
                win_rate,
                win_loss_ratio,
                conservative_factor
            )
            
            return {
                "position_size": result['size'],
                "position_notional": result['notional'],
                "risk_amount": result['risk_amount'],
                "kelly_pct": result['kelly_pct'],
                "explanation": f"Kelly={result['kelly_pct']:.2f}%, Conservative 0.75x applied"
            }
        
        @self.mcp.tool()
        def calculate_dynamic_slippage(
            order_size: float,
            adv_20: float,
            volume_today: float,
            volatility: float,
            regime: str = "normal"
        ) -> dict:
            """Calculate hydrodynamic market impact slippage.
            
            Args:
                order_size: Shares to order.
                adv_20: Average daily volume (20-day).
                volume_today: Today's volume so far.
                volatility: Current volatility (annualized).
                regime: Market regime ("normal" or "high_vol").
            
            Returns:
                {
                    "slippage_bps": float (basis points),
                    "slippage_usd": float,
                    "approval": bool (approved if < 50 bps limit),
                    "reasoning": str
                }
            
            Formula:
                S = c · σ · √(Q/V)
                c ≈ 0.5 (calibrated)
                Adjusted for regime (high_vol × 2.0)
            """
            from slippage import calculate_dynamic_slippage as calc_slip
            
            result = calc_slip(
                order_size,
                adv_20,
                volume_today,
                volatility,
                regime
            )
            
            return {
                "slippage_bps": result['slippage_bps'],
                "slippage_usd": result['slippage_usd'],
                "approval": result['slippage_bps'] < 50,
                "reasoning": f"Slippage = {result['slippage_bps']:.1f} bps ({'OK' if result['slippage_bps'] < 50 else 'REJECT'})"
            }
        
        @self.mcp.tool()
        def evaluate_risk_veto_gates(
            entry_price: float,
            atr: float,
            atr_multiplier: float,
            account_capital: float,
            max_risk_pct: float,
            current_qty: int,
            adv_20: float,
            volume_today: float,
            volatility: float
        ) -> dict:
            """Run all Shield Agent veto gates (deterministic, <100µs).
            
            Args:
                entry_price: Entry price (USD).
                atr: Average True Range.
                atr_multiplier: ATR × this for stop placement.
                account_capital: Account equity.
                max_risk_pct: Max risk per trade (%).
                current_qty: Current position size.
                adv_20: 20-day average daily volume.
                volume_today: Today's volume.
                volatility: Current volatility.
            
            Returns:
                {
                    "approved": bool,
                    "position_size": int,
                    "stop_loss": float,
                    "veto_reasons": List[str],
                    "gates_passed": Dict[str, bool]
                }
            
            Gates:
                1. Stop validity (stop > 0)
                2. Position sizing (Kelly-based)
                3. Liquidity (order ≤ 25% ADV)
                4. Slippage (< 50 bps)
                5. Portfolio reconciliation (delta > 0)
            """
            from shields import evaluate_risk_veto_gates as evaluate
            
            result = evaluate(
                entry_price,
                atr,
                atr_multiplier,
                account_capital,
                max_risk_pct,
                current_qty,
                adv_20,
                volume_today,
                volatility
            )
            
            return {
                "approved": result['approved'],
                "position_size": result['position_size'],
                "stop_loss": result['stop_loss'],
                "veto_reasons": result['veto_reasons'],
                "gates_passed": result['gates_passed']
            }
    
    def _register_feature_tools(self) -> None:
        """Register feature extraction tools (read-only)."""
        
        @self.mcp.tool()
        def get_atr(
            symbol: str,
            period: int = 14
        ) -> dict:
            """Get Average True Range for symbol.
            
            Args:
                symbol: Stock ticker (e.g., "AAPL").
                period: ATR lookback period (days).
            
            Returns:
                {
                    "symbol": str,
                    "atr": float,
                    "atr_percent": float,
                    "timestamp": str
                }
            """
            # Query live market data via Alpaca
            atr_value = self.market_data_cache.get_atr(symbol, period)
            return {
                "symbol": symbol,
                "atr": atr_value,
                "atr_percent": (atr_value / self.market_data_cache.last_price(symbol)) * 100,
                "timestamp": pd.Timestamp.now().isoformat()
            }
        
        @self.mcp.tool()
        def get_adv(
            symbol: str,
            period: int = 20
        ) -> dict:
            """Get Average Daily Volume.
            
            Returns:
                {
                    "symbol": str,
                    "adv": float,
                    "volume_today": float,
                    "volume_pct_of_adv": float
                }
            """
            adv = self.market_data_cache.get_adv(symbol, period)
            vol_today = self.market_data_cache.volume_today(symbol)
            return {
                "symbol": symbol,
                "adv": adv,
                "volume_today": vol_today,
                "volume_pct_of_adv": (vol_today / adv) * 100
            }
        
        @self.mcp.tool()
        def get_volatility(
            symbol: str,
            window: int = 15
        ) -> dict:
            """Get rolling volatility (annualized).
            
            Returns:
                {
                    "symbol": str,
                    "volatility_annual": float,
                    "regime": str ("normal" or "high_vol")
                }
            """
            vol = self.market_data_cache.get_volatility(symbol, window)
            regime = "high_vol" if vol > 0.30 else "normal"
            return {
                "symbol": symbol,
                "volatility_annual": vol,
                "regime": regime
            }
    
    def _register_market_tools(self) -> None:
        """Register market data query tools."""
        
        @self.mcp.tool()
        def get_price(symbol: str) -> dict:
            """Get real-time last price.
            
            Returns:
                {
                    "symbol": str,
                    "price": float,
                    "timestamp": str,
                    "bid_ask_spread_bps": float
                }
            """
            price = self.market_data_cache.last_price(symbol)
            bid, ask = self.market_data_cache.bid_ask(symbol)
            spread_bps = ((ask - bid) / ((bid + ask) / 2)) * 10000
            return {
                "symbol": symbol,
                "price": price,
                "bid_ask_spread_bps": spread_bps,
                "timestamp": pd.Timestamp.now().isoformat()
            }
        
        @self.mcp.tool()
        def get_open_interest(symbol: str) -> dict:
            """Get open interest / shares outstanding.
            
            Returns:
                {
                    "symbol": str,
                    "shares_outstanding": float,
                    "float": float,
                    "short_interest_pct": float
                }
            """
            # Query via SEC data or Alpaca fundamentals
            data = self.market_data_cache.get_fundamentals(symbol)
            return {
                "symbol": symbol,
                "shares_outstanding": data['shares_outstanding'],
                "float": data['float'],
                "short_interest_pct": data['short_interest_pct']
            }
    
    def _register_position_tools(self) -> None:
        """Register portfolio position tracking tools."""
        
        @self.mcp.tool()
        def get_current_position(symbol: str) -> dict:
            """Get current position for symbol.
            
            Returns:
                {
                    "symbol": str,
                    "quantity": int,
                    "avg_fill_price": float,
                    "current_price": float,
                    "unrealized_pnl": float,
                    "unrealized_pnl_pct": float
                }
            """
            pos = self.portfolio.get_position(symbol)
            current_price = self.market_data_cache.last_price(symbol)
            unrealized = (current_price - pos['avg_fill']) * pos['qty']
            unrealized_pct = (unrealized / (pos['avg_fill'] * pos['qty'])) * 100 if pos['qty'] > 0 else 0
            
            return {
                "symbol": symbol,
                "quantity": pos['qty'],
                "avg_fill_price": pos['avg_fill'],
                "current_price": current_price,
                "unrealized_pnl": unrealized,
                "unrealized_pnl_pct": unrealized_pct
            }
        
        @self.mcp.tool()
        def get_portfolio_metrics() -> dict:
            """Get overall portfolio metrics.
            
            Returns:
                {
                    "total_equity": float,
                    "cash": float,
                    "buying_power": float,
                    "total_pnl": float,
                    "total_pnl_pct": float,
                    "max_drawdown": float,
                    "sharpe_ratio": float
                }
            """
            metrics = self.portfolio.get_metrics()
            return {
                "total_equity": metrics['equity'],
                "cash": metrics['cash'],
                "buying_power": metrics['buying_power'],
                "total_pnl": metrics['total_pnl'],
                "total_pnl_pct": metrics['total_pnl_pct'],
                "max_drawdown": metrics['max_drawdown'],
                "sharpe_ratio": metrics['sharpe_ratio']
            }
    
    def run(self) -> None:
        """Start MCP server listening on stdio."""
        self.logger.info("Starting FastMCP server...")
        self.mcp.run(transport="stdio")
```

#### 2.2.2 Error Handling & Validation

**Function: `validate_tool_input()`**

```python
def validate_tool_input(
    tool_name: str,
    input_dict: Dict,
    schema: Dict
) -> Tuple[bool, Optional[str]]:
    """Validate tool input against schema before execution.
    
    Args:
        tool_name: Name of tool being called.
        input_dict: Input parameters from LLM.
        schema: JSON schema specification.
    
    Returns:
        (is_valid, error_message)
    
    Validation Rules:
        1. All required fields present
        2. Type checking (float, int, str, bool)
        3. Range validation (e.g., 0 ≤ win_rate ≤ 1)
        4. Enum validation (e.g., regime in ["normal", "high_vol"])
    """
    from jsonschema import validate, ValidationError
    
    logger = get_logger(__name__)
    
    try:
        validate(instance=input_dict, schema=schema)
        logger.debug(f"Tool input valid: {tool_name}")
        return True, None
    except ValidationError as e:
        error_msg = f"Tool input validation failed ({tool_name}): {e.message}"
        logger.warning(error_msg)
        return False, error_msg
```

---

## 3. Entity Anonymization (Defeat Look-Ahead Bias)

### 3.1 Theory: NER Masking for LLM Safety

**Problem**: LLM might recognize "Apple" in news → hallucinate about stock direction

**Solution**: Replace all tradable entities with placeholders before LLM sees text
- "Apple Q4 earnings beat" → "[COMPANY_A] Q4 earnings beat"
- Result: "BULLISH" → Map back to Apple → Trade

### 3.2 Module: `execution/entity_anonymizer.py`

**File: `execution/entity_anonymizer.py`**

#### 3.2.1 Entity Extraction & Masking

**Class: `EntityAnonymizer`**

```python
import spacy
from typing import Tuple, Dict, List

class EntityAnonymizer:
    """Mask tradable entities before LLM processing.
    
    Purpose:
        - Extract named entities (companies, tickers, people)
        - Replace with [COMPANY_A], [PERSON_B], etc.
        - Preserve semantic meaning (LLM still understands context)
        - Prevent LLM hallucination about specific companies
    
    Methods:
        anonymize_text: Replace entities with placeholders.
        deanonymize_result: Map results back to original entities.
    """
    
    def __init__(self, portfolio_symbols: List[str]):
        """Initialize anonymizer with trading universe.
        
        Args:
            portfolio_symbols: List of ticker symbols (e.g., ["AAPL", "MSFT"]).
        """
        self.logger = get_logger(__name__)
        self.nlp = spacy.load("en_core_web_sm")
        self.portfolio_symbols = set(portfolio_symbols)
        
        # Build ticker → company name mapping (via Alpaca/yfinance)
        self.ticker_to_name = self._build_ticker_mapping()
        
        # Counter for entity IDs
        self.entity_counter = {}
        self.entity_map = {}  # entity_str → [ENTITY_X]
        self.reverse_map = {}  # [ENTITY_X] → entity_str
    
    def _build_ticker_mapping(self) -> Dict[str, str]:
        """Build ticker → company name mapping.
        
        Returns:
            {
                "AAPL": "Apple Inc.",
                "MSFT": "Microsoft Corporation",
                ...
            }
        """
        mapping = {}
        # Query Alpaca Assets API
        for symbol in self.portfolio_symbols:
            # Placeholder: real implementation queries Alpaca
            mapping[symbol] = f"Company_{symbol}"
        return mapping
    
    def anonymize_text(self, text: str) -> Tuple[str, Dict]:
        """Replace entities with placeholders.
        
        Args:
            text: Raw text (news, SEC filing, etc.).
        
        Returns:
            (anonymized_text, entity_mapping)
            where entity_mapping = {
                "AAPL": "[COMPANY_A]",
                "Tim Cook": "[PERSON_A]",
                ...
            }
        
        Process:
            1. Parse text with spaCy NER
            2. Extract ORG (company), PERSON, GPE (location), etc.
            3. Check if entity is in trading universe
            4. Replace with [TYPE_ID] placeholder
            5. Keep mapping for deanonymization
        """
        self.logger.info(f"Anonymizing text ({len(text)} chars)")
        
        doc = self.nlp(text)
        entity_mapping = {}
        anonymized_text = text
        
        # Sort by span length (longest first) to avoid partial replacements
        entities = sorted(doc.ents, key=lambda e: len(e.text), reverse=True)
        
        for ent in entities:
            entity_text = ent.text
            entity_label = ent.label_
            
            # Check if entity is tradable (ticker or company name)
            ticker = self._match_to_ticker(entity_text)
            
            if ticker:
                # Assign placeholder
                if ticker not in self.entity_counter:
                    self.entity_counter[ticker] = len(self.entity_counter)
                
                entity_id = self.entity_counter[ticker]
                placeholder = f"[COMPANY_{chr(65 + entity_id)}]"  # [COMPANY_A], etc.
                
                # Replace all occurrences
                anonymized_text = anonymized_text.replace(entity_text, placeholder)
                entity_mapping[ticker] = placeholder
                self.entity_map[entity_text] = placeholder
                self.reverse_map[placeholder] = ticker
        
        self.logger.info(f"Anonymized {len(entity_mapping)} entities")
        
        return anonymized_text, entity_mapping
    
    def _match_to_ticker(self, entity_text: str) -> Optional[str]:
        """Match entity text to trading symbol.
        
        Args:
            entity_text: Text from NER (e.g., "Apple Inc.", "AAPL").
        
        Returns:
            Ticker symbol if match found, else None.
        """
        # Direct ticker match
        if entity_text.upper() in self.portfolio_symbols:
            return entity_text.upper()
        
        # Company name match (fuzzy)
        entity_upper = entity_text.upper()
        for ticker, name in self.ticker_to_name.items():
            if ticker in self.portfolio_symbols:
                if name.upper().startswith(entity_upper[:4]):
                    return ticker
        
        return None
    
    def deanonymize_result(
        self,
        anonymized_result: str
    ) -> Tuple[str, Optional[str]]:
        """Map anonymized result back to original entity.
        
        Args:
            anonymized_result: LLM output (e.g., "BULLISH on [COMPANY_A]").
        
        Returns:
            (deanonymized_result, ticker)
            Example: ("BULLISH on Apple Inc.", "AAPL")
        """
        # Extract placeholder
        import re
        match = re.search(r'\[COMPANY_[A-Z]\]', anonymized_result)
        
        if not match:
            return anonymized_result, None
        
        placeholder = match.group()
        ticker = self.reverse_map.get(placeholder)
        
        if ticker:
            deanonymized = anonymized_result.replace(
                placeholder,
                self.ticker_to_name.get(ticker, ticker)
            )
            return deanonymized, ticker
        
        return anonymized_result, None
```

---

## 4. Retrieval Augmented Generation (RAG) with Late Chunking

### 4.1 Theory: Semantic Context Preservation

**Problem**: Chunking text loses semantic boundaries (mid-sentence splits)

**Solution**: Late chunking (chunk after embedding, not before)
1. Embed full document
2. Split into semantic chunks (via paragraph/sentence boundaries)
3. Preserve context through chunk overlap

### 4.2 Module: `execution/rag_engine.py`

**File: `execution/rag_engine.py`**

#### 4.2.1 Late Chunking & Embedding

**Class: `RAGEngine`**

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGEngine:
    """Retrieval Augmented Generation with late chunking.
    
    Purpose:
        - Index unstructured text (news, 10-Ks, analyst reports)
        - Retrieve semantically similar context for LLM
        - Preserve chunk boundaries (late chunking)
        - Rank results (Faiss + BM25 + reranking)
    
    Methods:
        index_document: Add document to knowledge base.
        retrieve_context: Get top-k relevant chunks.
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_dim: int = 384,
        chunk_overlap: int = 100
    ):
        """Initialize RAG engine.
        
        Args:
            model_name: Hugging Face model ID.
            vector_dim: Embedding dimension.
            chunk_overlap: Character overlap between chunks.
        """
        self.logger = get_logger(__name__)
        
        # Load embedding model
        self.embed_model = SentenceTransformer(model_name)
        self.vector_dim = vector_dim
        self.chunk_overlap = chunk_overlap
        
        # Initialize Faiss index
        self.index = faiss.IndexFlatL2(vector_dim)
        self.chunk_store = []  # List of (text, source, timestamp)
        
        # Initialize BM25 (lexical fallback)
        self.bm25_retriever = None
        
        self.logger.info(f"RAG engine initialized ({model_name})")
    
    def late_chunk(
        self,
        text: str,
        chunk_size: int = 256,
        overlap: int = 100
    ) -> List[str]:
        """Chunk text while preserving semantic boundaries.
        
        Args:
            text: Full document text.
            chunk_size: Target chunk size (characters).
            overlap: Overlap between chunks.
        
        Returns:
            List of chunks with preserved boundaries.
        
        Algorithm:
            1. Split by sentence (not mid-sentence)
            2. Group sentences until chunk_size exceeded
            3. Add overlap from previous chunk
            4. Return chunks preserving full sentences
        """
        import re
        
        # Split by sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if chunks:
                    # Add last 'overlap' chars from previous chunk
                    overlap_text = chunks[-1][-overlap:] if len(chunks[-1]) > overlap else chunks[-1]
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        self.logger.info(f"Late chunked: {len(text)} chars → {len(chunks)} chunks")
        
        return chunks
    
    def index_document(
        self,
        text: str,
        source: str,
        sector: str = "general"
    ) -> None:
        """Index document and add to knowledge base.
        
        Args:
            text: Document text.
            source: Source identifier (URL, filepath, etc.).
            sector: Sector tag (for filtering).
        """
        self.logger.info(f"Indexing document: {source}")
        
        # Late chunk
        chunks = self.late_chunk(text)
        
        # Embed chunks
        embeddings = self.embed_model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to Faiss index
        self.index.add(embeddings)
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            self.chunk_store.append({
                'text': chunk,
                'source': source,
                'sector': sector,
                'timestamp': pd.Timestamp.now(),
                'chunk_idx': i
            })
        
        self.logger.info(f"Indexed {len(chunks)} chunks from {source}")
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        sector_filter: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve top-k relevant chunks for query.
        
        Args:
            query: LLM query (e.g., "Is Apple expanding in AI?").
            top_k: Number of chunks to return.
            sector_filter: Optional sector to filter by.
        
        Returns:
            List of {
                'text': chunk text,
                'source': source,
                'relevance_score': float (0-1),
                'chunk_idx': int
            }
        
        Algorithm:
            1. Embed query
            2. Faiss search (vector similarity)
            3. BM25 search (lexical match, fallback)
            4. Rerank results (LLM-based)
            5. Return top-k
        """
        self.logger.debug(f"Retrieving context for query: {query[:50]}...")
        
        if len(self.chunk_store) == 0:
            self.logger.warning("No chunks indexed yet")
            return []
        
        # Embed query
        query_embedding = self.embed_model.encode(query, show_progress_bar=False)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Faiss search
        distances, indices = self.index.search(query_embedding, top_k * 2)  # Get 2x candidates
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # Invalid index
                continue
            
            chunk_meta = self.chunk_store[idx]
            
            # Apply sector filter if specified
            if sector_filter and chunk_meta['sector'] != sector_filter:
                continue
            
            # Normalize distance to relevance score (0-1)
            relevance = 1.0 / (1.0 + dist)
            
            results.append({
                'text': chunk_meta['text'],
                'source': chunk_meta['source'],
                'relevance_score': relevance,
                'chunk_idx': chunk_meta['chunk_idx'],
                'sector': chunk_meta['sector']
            })
        
        # Return top-k
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)[:top_k]
```

---

## 5. LangGraph State Machine

### 5.1 Theory: Agentic Orchestration with Feedback Loops

**Design**: State machine with self-correcting nodes
- Verdict Engine generates alpha narrative
- Grader validates verdict against context
- If invalid → retry (up to 3 times)
- If valid → pass to Shield Agent
- If Shield Agent rejects → fallback to passive

### 5.2 Module: `execution/state_machine.py`

**File: `execution/state_machine.py`**

#### 5.2.1 LangGraph State Definition

**Class: `OrchestratorState`**

```python
from langgraph.graph import StateGraph, END
from typing import Annotated
import operator

class OrchestratorState:
    """LangGraph state for signal → verdict → execution.
    
    Attributes:
        signal: Initial buy/sell signal from model.
        symbol: Ticker symbol.
        entry_price: Entry price (USD).
        context: Retrieved documents (RAG output).
        verdict: LLM verdict ("BULLISH", "BEARISH", "NEUTRAL").
        grader_feedback: Grader validation comment.
        grader_approved: Boolean approval from grader.
        shield_approved: Boolean approval from Shield Agent.
        position_size: Final position size (if approved).
        stop_loss: Stop loss price.
        execution_id: Trade ID (if executed).
        rejection_reason: Why rejected (if rejected).
        attempts: Retry counter.
    """
    
    signal: str  # "BUY" or "SELL"
    symbol: str
    entry_price: float
    context: List[Dict]  # From RAG
    verdict: str = ""
    grader_feedback: str = ""
    grader_approved: bool = False
    shield_approved: bool = False
    position_size: int = 0
    stop_loss: float = 0.0
    execution_id: str = ""
    rejection_reason: str = ""
    attempts: int = 0  # Retry counter
```

#### 5.2.2 State Machine Nodes

**Class: `OrchestratorStateMachine`**

```python
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI

class OrchestratorStateMachine:
    """Multi-node state machine with feedback loops.
    
    Nodes:
        1. Verdict Engine → Generate narrative
        2. Grader → Validate verdict
        3. Risk Veto → Shield Agent approval
        4. Execute → Submit trade
        5. Fallback → Passive mode
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize LLMs
        self.verdict_llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.1  # Low temperature for consistency
        )
        self.grader_llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.0  # Deterministic grading
        )
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph state machine.
        
        Graph topology:
            START
              ↓
            VERDICT_ENGINE
              ↓
            GRADER
            ↙     ↘
        PASS(✓)   FAIL(✗)
          ↓         ↓
        RISK_VETO  RETRY?
        ↙     ↘     ↓ (attempts < 3)
      PASS   FAIL  GRADER (loop)
        ↓     ↓     ↓ (attempts ≥ 3)
      EXEC  FALLBACK
        ↓     ↓
        END←←←→
        """
        
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes
        workflow.add_node("verdict_engine", self._node_verdict_engine)
        workflow.add_node("grader", self._node_grader)
        workflow.add_node("risk_veto", self._node_risk_veto)
        workflow.add_node("execute", self._node_execute)
        workflow.add_node("fallback", self._node_fallback)
        
        # Add edges
        workflow.add_edge("START", "verdict_engine")
        workflow.add_edge("verdict_engine", "grader")
        
        # Conditional: grader pass/fail
        workflow.add_conditional_edges(
            "grader",
            self._grader_decision,
            {
                "pass": "risk_veto",
                "retry": "verdict_engine",  # Loop on failure
                "reject": "fallback"  # Max attempts exceeded
            }
        )
        
        # Conditional: risk veto pass/fail
        workflow.add_conditional_edges(
            "risk_veto",
            self._risk_decision,
            {
                "pass": "execute",
                "reject": "fallback"
            }
        )
        
        # Terminal nodes
        workflow.add_edge("execute", END)
        workflow.add_edge("fallback", END)
        
        return workflow.compile()
    
    def _node_verdict_engine(self, state: OrchestratorState) -> OrchestratorState:
        """Generate alpha narrative from context.
        
        Input: signal + context
        Output: verdict
        
        Prompt:
            "Given the signal '{signal}' for {symbol} at ${entry_price}
             and the following context:
             {context}
             
             Generate a concise verdict ('BULLISH', 'BEARISH', 'NEUTRAL')
             with 1-2 sentence rationale."
        """
        self.logger.info(f"Generating verdict for {state.symbol}")
        
        # Format context for LLM
        context_str = "\n".join([
            f"- {chunk['source']}: {chunk['text'][:100]}..."
            for chunk in state.context[:3]
        ])
        
        prompt = f"""
        Signal: {state.signal}
        Symbol: {state.symbol}
        Entry Price: ${state.entry_price}
        
        Context:
        {context_str}
        
        Generate a trading verdict (BULLISH/BEARISH/NEUTRAL) with brief rationale.
        """
        
        response = self.verdict_llm.invoke(prompt)
        state.verdict = response.content
        
        self.logger.info(f"Verdict: {state.verdict}")
        
        return state
    
    def _node_grader(self, state: OrchestratorState) -> OrchestratorState:
        """Validate verdict against context (self-correcting).
        
        Input: verdict + context
        Output: grader_approved (bool), grader_feedback (str)
        
        Grader prompt:
            "Verdict: {verdict}
             Context: {context}
             
             Is this verdict supported by the context?
             Answer: YES/NO
             Feedback: ..."
        """
        self.logger.info(f"Grading verdict for {state.symbol}")
        
        context_str = "\n".join([
            f"- {chunk['text'][:100]}..."
            for chunk in state.context[:3]
        ])
        
        prompt = f"""
        Verdict: {state.verdict}
        
        Supporting Context:
        {context_str}
        
        Is this verdict logically supported by the context?
        Answer YES or NO with brief explanation.
        """
        
        response = self.grader_llm.invoke(prompt)
        grader_text = response.content
        
        # Parse response
        is_approved = "YES" in grader_text.upper()
        state.grader_approved = is_approved
        state.grader_feedback = grader_text
        state.attempts += 1
        
        self.logger.info(f"Grader: {'APPROVED' if is_approved else 'REJECTED'} (attempt {state.attempts})")
        
        return state
    
    def _grader_decision(self, state: OrchestratorState) -> str:
        """Route based on grader verdict.
        
        Returns: "pass", "retry", or "reject"
        """
        if state.grader_approved:
            return "pass"
        elif state.attempts < 3:
            return "retry"
        else:
            state.rejection_reason = "Max retry attempts exceeded"
            return "reject"
    
    def _node_risk_veto(self, state: OrchestratorState) -> OrchestratorState:
        """Run Shield Agent veto gates.
        
        Input: verdict (approved by grader)
        Output: shield_approved, position_size, stop_loss
        """
        self.logger.info(f"Running risk veto for {state.symbol}")
        
        # Query MCP tools
        atr_response = self._call_mcp("get_atr", {"symbol": state.symbol})
        atr = atr_response['atr']
        
        vol_response = self._call_mcp("get_volatility", {"symbol": state.symbol})
        volatility = vol_response['volatility_annual']
        
        adv_response = self._call_mcp("get_adv", {"symbol": state.symbol})
        adv_20 = adv_response['adv']
        vol_today = adv_response['volume_today']
        
        # Run veto gates
        veto_response = self._call_mcp(
            "evaluate_risk_veto_gates",
            {
                "entry_price": state.entry_price,
                "atr": atr,
                "atr_multiplier": 2.0,
                "account_capital": self.config.execution.account_capital,
                "max_risk_pct": self.config.execution.max_risk_per_trade,
                "current_qty": 0,  # Placeholder
                "adv_20": adv_20,
                "volume_today": vol_today,
                "volatility": volatility
            }
        )
        
        state.shield_approved = veto_response['approved']
        state.position_size = veto_response['position_size']
        state.stop_loss = veto_response['stop_loss']
        
        if not state.shield_approved:
            state.rejection_reason = "; ".join(veto_response['veto_reasons'])
        
        self.logger.info(f"Shield Agent: {'APPROVED' if state.shield_approved else 'REJECTED'}")
        
        return state
    
    def _risk_decision(self, state: OrchestratorState) -> str:
        """Route based on Shield Agent approval.
        
        Returns: "pass" or "reject"
        """
        return "pass" if state.shield_approved else "reject"
    
    def _node_execute(self, state: OrchestratorState) -> OrchestratorState:
        """Submit trade to Alpaca.
        
        Input: position_size, entry_price
        Output: execution_id
        """
        self.logger.info(f"Executing trade: {state.signal} {state.position_size} {state.symbol}")
        
        try:
            order = self._submit_alpaca_order(
                symbol=state.symbol,
                qty=state.position_size,
                side=state.signal.lower(),
                stop_price=state.stop_loss
            )
            
            state.execution_id = order.id
            self.logger.info(f"Order submitted: {state.execution_id}")
            
        except Exception as e:
            state.rejection_reason = f"Execution error: {str(e)}"
            self.logger.error(state.rejection_reason)
        
        return state
    
    def _node_fallback(self, state: OrchestratorState) -> OrchestratorState:
        """Fallback: no trade executed.
        
        Log reason and continue monitoring.
        """
        self.logger.warning(f"Fallback for {state.symbol}: {state.rejection_reason}")
        
        return state
    
    def _call_mcp(self, tool_name: str, params: Dict) -> Dict:
        """Call FastMCP tool (placeholder).
        
        Real implementation would use JSON-RPC client.
        """
        # Placeholder: real implementation calls MCP server
        return {}
    
    def _submit_alpaca_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        stop_price: float
    ) -> Dict:
        """Submit order to Alpaca (placeholder).
        
        Args:
            symbol: Ticker.
            qty: Shares.
            side: "buy" or "sell".
            stop_price: Stop loss.
        
        Returns:
            Order object with ID.
        """
        # Placeholder: real implementation uses Alpaca API
        return {'id': 'order_123'}
    
    def invoke(self, initial_state: OrchestratorState) -> OrchestratorState:
        """Run state machine.
        
        Args:
            initial_state: Initial input state.
        
        Returns:
            Final state with execution result.
        """
        result = self.graph.invoke(initial_state)
        return result
```

---

## 6. Veto Ledger & Audit Trail

### 6.1 Module: `execution/veto_ledger.py`

**Class: `VetoLedger`**

```python
class VetoLedger:
    """Comprehensive audit trail for all decisions.
    
    Methods:
        record_veto: Log rejection reason.
        get_veto_stats: Analyze rejection patterns.
        get_active_trades: List live positions.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.ledger_path = f"{config.execution.ledger_dir}/veto_ledger.parquet"
        
        # Initialize Parquet schema
        self.schema = pa.schema([
            ('timestamp', pa.timestamp('ns')),
            ('symbol', pa.string()),
            ('signal', pa.string()),
            ('entry_price', pa.float64()),
            ('veto_reason', pa.string()),
            ('veto_gate', pa.string()),  # Which gate rejected
            ('dsr', pa.float64()),
            ('position_size', pa.int32()),
            ('execution_id', pa.string())
        ])
    
    def record_veto(
        self,
        symbol: str,
        signal: str,
        entry_price: float,
        veto_reason: str,
        veto_gate: str,
        dsr: float = None,
        position_size: int = 0,
        execution_id: str = ""
    ) -> None:
        """Record veto decision.
        
        Args:
            symbol: Ticker.
            signal: "BUY" or "SELL".
            entry_price: Entry price.
            veto_reason: Why rejected.
            veto_gate: Which gate rejected ("grader", "shield", "execution").
            dsr: Deflated Sharpe Ratio (if from evaluation).
            position_size: Intended position size.
            execution_id: Order ID (if executed).
        """
        record = {
            'timestamp': pd.Timestamp.now(),
            'symbol': symbol,
            'signal': signal,
            'entry_price': entry_price,
            'veto_reason': veto_reason,
            'veto_gate': veto_gate,
            'dsr': dsr or 0.0,
            'position_size': position_size,
            'execution_id': execution_id
        }
        
        # Append to Parquet
        table = pa.Table.from_pylist([record], schema=self.schema)
        
        if os.path.exists(self.ledger_path):
            existing = pq.read_table(self.ledger_path)
            combined = pa.concat_tables([existing, table])
            pq.write_table(combined, self.ledger_path)
        else:
            pq.write_table(table, self.ledger_path)
        
        self.logger.info(f"Recorded veto: {symbol} {signal} ({veto_gate})")
    
    def get_veto_stats(self, window_days: int = 7) -> Dict:
        """Analyze veto patterns.
        
        Returns:
            {
                'total_vetoes': int,
                'top_gates': [(gate, count), ...],
                'top_reasons': [(reason, count), ...],
                'symbol_vetoes': {symbol: count, ...}
            }
        """
        if not os.path.exists(self.ledger_path):
            return {'total_vetoes': 0}
        
        df = pq.read_table(self.ledger_path).to_pandas()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter recent
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=window_days)
        df = df[df['timestamp'] > cutoff]
        
        return {
            'total_vetoes': len(df),
            'top_gates': df['veto_gate'].value_counts().head(5).to_dict(),
            'top_reasons': df['veto_reason'].value_counts().head(5).to_dict(),
            'symbol_vetoes': df['symbol'].value_counts().to_dict()
        }
```

---

## 7. Implementation Checklist - Phase 5

### Week 1-2: FastMCP & Entity Handling

- [ ] **Day 1-2**: FastMCP server setup
  - [ ] Initialize FastMCP server
  - [ ] Register risk management tools (Kelly, slippage, veto gates)
  - [ ] Unit tests: `test_mcp_server.py`

- [ ] **Day 2-3**: Market data tools
  - [ ] Register market data tools (price, volume, ATR)
  - [ ] Register portfolio tools (position, metrics)
  - [ ] Integration with Alpaca API

- [ ] **Day 3-4**: Entity anonymization
  - [ ] Implement spaCy NER pipeline
  - [ ] Build ticker mapping
  - [ ] Test masking/deanonymization

- [ ] **Day 4-5**: RAG engine
  - [ ] Late chunking implementation
  - [ ] Sentence-transformers embedding
  - [ ] Faiss index + retrieval

### Week 3: LangGraph & Orchestration

- [ ] **Day 6-7**: LangGraph setup
  - [ ] Define OrchestratorState
  - [ ] Build state machine graph
  - [ ] Unit tests: `test_state_machine.py`

- [ ] **Day 7-8**: Node implementations
  - [ ] Verdict Engine node (LLM generation)
  - [ ] Grader node (validation)
  - [ ] Risk Veto node (Shield Agent)
  - [ ] Execute + Fallback nodes

- [ ] **Day 8-9**: Integration
  - [ ] MCP ↔ LangGraph integration
  - [ ] Entity anonymization flow
  - [ ] End-to-end tests

- [ ] **Day 9-10**: Monitoring & optimization
  - [ ] Veto ledger implementation
  - [ ] Performance profiling
  - [ ] All tests 85%+ coverage

---

## 8. Success Criteria

| Criterion | Test | Expected |
|-----------|------|----------|
| FastMCP startup | `test_mcp_server_init()` | ✓ Server listening |
| Tool registration | `test_tool_schemas()` | ✓ 30+ tools registered |
| Entity masking | `test_entity_masking()` | ✓ "Apple" → "[COMPANY_A]" |
| RAG retrieval | `test_rag_retrieval()` | ✓ Top-k context returned |
| LangGraph flow | `test_graph_execution()` | ✓ State transitions correct |
| Verdict generation | `test_verdict_engine()` | ✓ LLM returns verdict |
| Grading logic | `test_grader_node()` | ✓ Validates verdict |
| Risk veto | `test_risk_veto_node()` | ✓ Rejects bad trades |
| Execution | `test_execute_node()` | ✓ Order submitted to Alpaca |
| Ledger tracking | `test_veto_ledger()` | ✓ Decisions logged |

---

## 9. Performance Targets

| Component | Target |
|-----------|--------|
| MCP tool latency | < 10ms per call |
| Entity masking | < 100ms per 1000 chars |
| RAG retrieval | < 200ms for top-5 |
| LangGraph cycle | < 5 seconds (LLM dominant) |
| Alpaca submission | < 100ms |
| Full decision pipeline | < 10 seconds |

---

## 10. Integration with Phases 1-4 & Handoff to Phase 6

### 10.1 Phase Dependencies

- **Phase 1**: Config, logging, exceptions
- **Phase 2**: Feature engine, Shield Agent
- **Phase 3**: Tournament results (for hyperparameters)
- **Phase 4**: DSR thresholds, promotion registry

### 10.2 Outputs for Phase 6 (Dashboard)

- Veto ledger (parquet format)
- Trade log + fills
- KPI metrics (Sharpe, win rate, max drawdown)
- Real-time position updates

---

## 11. Deliverables Summary - Phase 5

### Codebase
- [ ] `/new_pipeline/execution/mcp_server.py` (400+ lines)
- [ ] `/new_pipeline/execution/entity_anonymizer.py` (250+ lines)
- [ ] `/new_pipeline/execution/rag_engine.py` (300+ lines)
- [ ] `/new_pipeline/execution/state_machine.py` (500+ lines)
- [ ] `/new_pipeline/execution/veto_ledger.py` (150+ lines)
- [ ] 100+ unit tests + benchmarks

### Live Capabilities
- [ ] FastMCP server running (30+ tools)
- [ ] Real-time data feed from Alpaca
- [ ] Entity anonymization working
- [ ] LangGraph state machine orchestrating
- [ ] Veto ledger tracking all decisions

### Performance
- [ ] MCP tools <10ms latency
- [ ] Full pipeline <10 seconds
- [ ] Alpaca integration tested
- [ ] 85%+ test coverage

---

**Next**: After Phase 5 completion, proceed to [Phase 6: Dashboard & Monitoring](PHASE_6_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)
- [Phase 4: Statistical Evaluation & Promotion](PHASE_4_SPECIFICATION.md)
