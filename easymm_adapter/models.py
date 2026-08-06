from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class DecisionType(str, Enum):
    QUOTE_ADJUSTMENT = "QUOTE_ADJUSTMENT"
    INVENTORY_REBALANCE = "INVENTORY_REBALANCE"
    CRISIS_WIDEN = "CRISIS_WIDEN"
    PRE_TGE_QUOTE = "PRE_TGE_QUOTE"


class ReasoningStep(BaseModel):
    step: int
    text: str
    source_type: str  # market_data | model_output | risk_engine | human_override
    confidence: Optional[float] = None


class ClientRiskLimits(BaseModel):
    max_inventory_ratio: float = 0.35
    max_spread_bps: float = 120.0
    max_order_notional_usd: float = 250_000.0
    allow_crisis_widen: bool = True
    min_confidence: float = 0.73


class MarketState(BaseModel):
    symbol: str
    mid_price: float
    best_bid: float
    best_ask: float
    inventory_ratio: float          # -1 .. +1 (signed)
    volatility_regime: str          # calm | normal | elevated | crisis
    volume_24h_usd: float = 0.0
    client_limits: ClientRiskLimits = Field(default_factory=ClientRiskLimits)


class ProposedAction(BaseModel):
    side: Optional[str] = None      # buy | sell | both
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    bid_spread_bps: Optional[float] = None
    ask_spread_bps: Optional[float] = None
    target_inventory_ratio: Optional[float] = None
    urgency: str = "normal"         # normal | high | emergency


class DecisionProposal(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: DecisionType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    market_state: MarketState
    proposed_action: ProposedAction
    reasoning_chain: list[ReasoningStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    decision_id: str
    status: str                     # APPROVED | REJECTED
    trace_id: str
    confidence: float
    policy_checks: list[dict[str, Any]]
    attestation: dict[str, Any]
    rejection_reason: Optional[str] = None
    latency_ms: float = 0.0
