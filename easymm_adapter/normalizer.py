from .models import DecisionProposal


def normalize_proposal(proposal: DecisionProposal) -> dict:
    """
    Convert EasyMM DecisionProposal into a Gravit-compatible Claim payload.
    This is the only place that knows about EasyMM-specific shapes.
    """
    return {
        "claim_id": proposal.decision_id,
        "claim_type": proposal.type.value,
        "symbol": proposal.market_state.symbol,
        "timestamp": proposal.timestamp.isoformat(),
        "context": {
            "inventory_ratio": proposal.market_state.inventory_ratio,
            "volatility_regime": proposal.market_state.volatility_regime,
            "mid_price": proposal.market_state.mid_price,
            "client_limits": proposal.market_state.client_limits.model_dump(),
        },
        "proposed_action": proposal.proposed_action.model_dump(),
        "reasoning_chain": [step.model_dump() for step in proposal.reasoning_chain],
        "metadata": proposal.metadata,
    }
