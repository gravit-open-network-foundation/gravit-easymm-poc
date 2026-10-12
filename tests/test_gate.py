from epistemic_core.gate import EpistemicGate
from easymm_adapter.normalizer import normalize_proposal
from pilot.run_pilot import NOW, prepare
from scenarios.inventory_rebalance import build_inventory_rebalance_scenario
from scenarios.quote_adjustment import build_quote_adjustment_scenario


def check(prepared):
    proposal, records = prepared
    return EpistemicGate().verify(normalize_proposal(proposal), records, NOW)


def test_quote_adjustment_approved_with_two_independent_feeds():
    r = check(prepare(build_quote_adjustment_scenario(), 1))
    assert r["status"] == "APPROVED" and r["market_evidence"]["state"] == "Verified Fact"


def test_inventory_violation_rejected_by_policy():
    r = check(prepare(build_inventory_rebalance_scenario(violate_limit=True), 3))
    assert r["status"] == "REJECTED" and "Policy violation" in r["rejection_reason"]


def test_agent_confidence_alone_never_approves():
    # high self-reported confidences in the reasoning chain, but no independent market data
    r = check(prepare(build_quote_adjustment_scenario(), 6, feeds=()))
    assert r["status"] == "REJECTED"


def test_single_feed_is_not_enough():
    r = check(prepare(build_quote_adjustment_scenario(), 7, feeds=("feed-exchange-a",)))
    assert r["status"] == "REJECTED"


def test_price_mismatch_is_rejected():
    r = check(prepare(build_quote_adjustment_scenario(), 8, tamper_price=0.0921))
    assert r["status"] == "REJECTED" and r["market_evidence"]["records_bound"] == 0


def test_trace_id_is_reproducible():
    a = check(prepare(build_quote_adjustment_scenario(), 1))["trace_id"]
    b = check(prepare(build_quote_adjustment_scenario(), 1))["trace_id"]
    assert a == b
