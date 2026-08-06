from easymm_adapter.models import (
    DecisionProposal, DecisionType, MarketState, ProposedAction,
    ReasoningStep, ClientRiskLimits
)


def build_quote_adjustment_scenario() -> DecisionProposal:
    """
    Scenario 1: Normal quote size & spread adjustment under elevated volatility.
    """
    return DecisionProposal(
        type=DecisionType.QUOTE_ADJUSTMENT,
        market_state=MarketState(
            symbol="PROJ/USDT",
            mid_price=0.0842,
            best_bid=0.0840,
            best_ask=0.0844,
            inventory_ratio=0.12,
            volatility_regime="elevated",
            volume_24h_usd=1_850_000,
            client_limits=ClientRiskLimits(max_inventory_ratio=0.30, max_spread_bps=90),
        ),
        proposed_action=ProposedAction(
            side="both",
            bid_size=12_500,
            ask_size=11_800,
            bid_spread_bps=18,
            ask_spread_bps=22,
            urgency="normal",
        ),
        reasoning_chain=[
            ReasoningStep(step=1, text="Volatility regime elevated (realized vol +40% vs 7d avg)", source_type="market_data", confidence=0.94),
            ReasoningStep(step=2, text="Inventory still within comfortable band (0.12 < 0.30)", source_type="risk_engine", confidence=0.99),
            ReasoningStep(step=3, text="Widen ask slightly more than bid to lean against mild long inventory", source_type="model_output", confidence=0.87),
            ReasoningStep(step=4, text="Proposed spreads remain well inside client max 90 bps", source_type="risk_engine", confidence=0.99),
        ],
        metadata={"scenario": "quote_adjustment", "client": "demo-project-alpha"},
    )
