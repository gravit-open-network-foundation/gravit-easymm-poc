from easymm_adapter.models import (
    DecisionProposal, DecisionType, MarketState, ProposedAction,
    ReasoningStep, ClientRiskLimits
)


def build_pre_tge_scenario() -> DecisionProposal:
    """
    Scenario 4: Pre-TGE / launch window — thin book, stricter controls.
    """
    return DecisionProposal(
        type=DecisionType.PRE_TGE_QUOTE,
        market_state=MarketState(
            symbol="NEW/USDT",
            mid_price=0.0120,
            best_bid=0.0118,
            best_ask=0.0122,
            inventory_ratio=0.05,
            volatility_regime="elevated",
            volume_24h_usd=320_000,
            client_limits=ClientRiskLimits(
                max_inventory_ratio=0.15,    # tighter for launch
                max_spread_bps=60,
            ),
        ),
        proposed_action=ProposedAction(
            side="both",
            bid_size=85_000,
            ask_size=85_000,
            bid_spread_bps=25,
            ask_spread_bps=28,
            urgency="high",
        ),
        reasoning_chain=[
            ReasoningStep(step=1, text="Launch window active — expected high retail flow", source_type="market_data", confidence=0.90),
            ReasoningStep(step=2, text="Inventory kept deliberately low (0.05) per launch playbook", source_type="risk_engine", confidence=0.98),
            ReasoningStep(step=3, text="Symmetric size + modest spread to bootstrap orderly book", source_type="model_output", confidence=0.86),
            ReasoningStep(step=4, text="All parameters inside tightened launch limits", source_type="risk_engine", confidence=0.99),
        ],
        metadata={"scenario": "pre_tge_launch", "phase": "T+0 to T+4h"},
    )
