from easymm_adapter.models import (
    DecisionProposal, DecisionType, MarketState, ProposedAction,
    ReasoningStep, ClientRiskLimits
)


def build_inventory_rebalance_scenario(violate_limit: bool = False) -> DecisionProposal:
    """
    Scenario 2: Inventory rebalancing decision.
    Set violate_limit=True to demonstrate hard policy rejection.
    """
    target = 0.42 if violate_limit else 0.18

    return DecisionProposal(
        type=DecisionType.INVENTORY_REBALANCE,
        market_state=MarketState(
            symbol="PROJ/USDT",
            mid_price=0.0842,
            best_bid=0.0840,
            best_ask=0.0844,
            inventory_ratio=0.28,
            volatility_regime="normal",
            volume_24h_usd=1_850_000,
            client_limits=ClientRiskLimits(max_inventory_ratio=0.30),
        ),
        proposed_action=ProposedAction(
            target_inventory_ratio=target,
            urgency="high" if violate_limit else "normal",
        ),
        reasoning_chain=[
            ReasoningStep(step=1, text="Current inventory 0.28 approaching soft warning threshold", source_type="risk_engine", confidence=0.96),
            ReasoningStep(step=2, text="Order-flow imbalance suggests continued buying pressure", source_type="market_data", confidence=0.81),
            ReasoningStep(step=3, text=f"Propose target inventory {target}", source_type="model_output", confidence=0.88),
        ],
        metadata={"scenario": "inventory_rebalance", "intentional_violation": violate_limit},
    )
