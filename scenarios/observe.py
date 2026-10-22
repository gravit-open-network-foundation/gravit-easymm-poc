#!/usr/bin/env python3
"""
Observer mode: the same eight market-making decisions, executed by EasyMM's own
engine first and checked by Gravit only afterwards. Nothing is blocked; every
finding is signed, chained and sealed. Writes results/observer-*.json* (deterministic).
"""

import json
from pathlib import Path

from easymm_adapter.client import EasyMMAdapter
from easymm_adapter.models import DecisionProposal
from observer import PostTradeObserver, verify
from pilot.run_pilot import NOW, prepare
from scenarios.crisis_spread_widen import build_crisis_widen_scenario
from scenarios.inventory_rebalance import build_inventory_rebalance_scenario
from scenarios.pre_tge_launch import build_pre_tge_scenario
from scenarios.quote_adjustment import build_quote_adjustment_scenario

PERIOD = "2026-10-12"


def decisions():
    q = build_quote_adjustment_scenario
    yield "Quote size and spread adjustment", prepare(q(), 1)
    yield "Inventory rebalance (valid)", prepare(build_inventory_rebalance_scenario(violate_limit=False), 2)
    yield "Inventory rebalance (limit violated)", prepare(build_inventory_rebalance_scenario(violate_limit=True), 3)
    yield "Crisis spread widening", prepare(build_crisis_widen_scenario(), 4)
    yield "Pre-TGE launch quoting", prepare(build_pre_tge_scenario(), 5)
    yield "Market data not confirmed by any feed", prepare(q(), 6, feeds=())
    yield "Market data confirmed by a single feed", prepare(q(), 7, feeds=("feed-exchange-a",))
    yield "Agent used a price the feeds do not confirm", prepare(q(), 8, tamper_price=0.0921)


def main() -> int:
    feed, executed = {}, []
    for name, (proposal, records) in decisions():
        feed[proposal.decision_id] = records
        executed.append({"decision": proposal.model_dump(mode="json"), "executed_at": NOW, "scenario": name})

    adapter = EasyMMAdapter()

    def evaluate(rec):
        p = DecisionProposal.model_validate(rec["decision"])
        r = adapter.verify_decision(p, feed.get(p.decision_id, []), rec["executed_at"])
        return r.status == "APPROVED", r.rejection_reason or "consistent with policy and independently confirmed market data", \
            {"trace_id": r.trace_id, "confidence": r.confidence}

    obs = PostTradeObserver(evaluate, observer_id="observer-gravit-test")
    for rec in executed:
        e = obs.observe(rec)
        print(f"executed  {e['body']['finding']:10} {rec['scenario']:45} {e['body']['reason'][:70]}")
    seal = obs.seal(PERIOD)
    ok, why = verify(obs.entries, seal, seal["public_key"])
    print(f"\nseal {PERIOD}: {seal['entries']} decisions, {seal['exceptions']} exceptions, root {seal['merkle_root'][:16]}...  verify: {why}")

    out = Path(__file__).resolve().parent.parent / "results"
    out.mkdir(exist_ok=True)
    (out / "observer-log.jsonl").write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in obs.entries))
    (out / "observer-seal.json").write_text(json.dumps(seal, indent=1, sort_keys=True) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
