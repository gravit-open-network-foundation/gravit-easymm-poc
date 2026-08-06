from easymm_adapter.models import (
    DecisionProposal, DecisionType, MarketState, ProposedAction,
    ReasoningStep, ClientRiskLimits
)


def build_crisis_widen_scenario() -> DecisionProposal:
    """
    Scenario 3: Sudden volatility spike → widen spreads aggressively.
    """
    return DecisionProposal(
        type=DecisionType.CRISIS_WIDEN,
        market_state=MarketState(
            symbol="PROJ/USDT",
            mid_price=0.0795,
            best_bid=0.0788,
            best_ask=0.0802,
            inventory_ratio=-0.09,
            volatility_regime="crisis",
            volume_24h_usd=4_200_000,
            client_limits=ClientRiskLimits(
                max_inventory_ratio=0.30,
                max_spread_bps=150,          # temporarily raised for crisis
                allow_crisis_widen=True,
            ),
        ),
        proposed_action=ProposedAction(
            side="both",
            bid_size=4_000,
            ask_size=4_000,
            bid_spread_bps=85,
            ask_spread_bps=95,
            urgency="emergency",
        ),
        reasoning_chain=[
            ReasoningStep(step=1, text="Realized vol spike > 3σ in last 8 minutes", source_type="market_data", confidence=0.97),
            ReasoningStep(step=2, text="Large sell wall appeared on major CEX", source_type="market_data", confidence=0.91),
            ReasoningStep(step=3, text="Client policy allows crisis widen up to 150 bps", source_type="risk_engine", confidence=0.99),
            ReasoningStep(step=4, text="Reduce size and widen both sides to protect inventory and clients", source_type="model_output", confidence=0.93),
        ],
        metadata={"scenario": "crisis_spread_widen"},
    )
