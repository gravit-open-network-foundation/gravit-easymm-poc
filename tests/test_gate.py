from epistemic_core.gate import EpistemicGate
from scenarios.quote_adjustment import build_quote_adjustment_scenario
from scenarios.inventory_rebalance import build_inventory_rebalance_scenario
from easymm_adapter.normalizer import normalize_proposal


def test_quote_adjustment_approved():
    gate = EpistemicGate()
    proposal = build_quote_adjustment_scenario()
    claim = normalize_proposal(proposal)
    result = gate.verify(claim)
    assert result["status"] == "APPROVED"
    assert result["confidence"] > 0.7
    assert result["trace_id"]


def test_inventory_violation_rejected():
    gate = EpistemicGate()
    proposal = build_inventory_rebalance_scenario(violate_limit=True)
    claim = normalize_proposal(proposal)
    result = gate.verify(claim)
    assert result["status"] == "REJECTED"
    assert "Policy violation" in result["rejection_reason"]
