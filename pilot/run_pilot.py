#!/usr/bin/env python3
"""
Gravit × EasyMM PoC — Pilot Runner
Runs the four priority verification scenarios.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from datetime import datetime, timezone

from easymm_adapter.client import EasyMMAdapter
from easymm_adapter.normalizer import normalize_proposal
from epistemic_core.market_evidence import attest, snapshot
from scenarios.quote_adjustment import build_quote_adjustment_scenario
from scenarios.inventory_rebalance import build_inventory_rebalance_scenario
from scenarios.crisis_spread_widen import build_crisis_widen_scenario
from scenarios.pre_tge_launch import build_pre_tge_scenario

console = Console()


AS_OF = datetime(2026, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
NOW = "2026-10-12T12:00:00Z"


def prepare(proposal, n: int, feeds=("feed-exchange-a", "feed-exchange-b"), tamper_price: float | None = None):
    """Fixed id and time (reproducible), plus signed market-data records from independent feeds."""
    proposal.decision_id = f"easymm-demo-{n:02d}"
    proposal.timestamp = AS_OF
    claim = normalize_proposal(proposal)
    snap = snapshot(claim)
    if tamper_price is not None:  # a feed attests a different price than the agent used
        snap = {**snap, "mid_price": tamper_price}
    return proposal, [attest(f, proposal.decision_id, snap, NOW) for f in feeds]


def run_scenario(name: str, prepared, adapter: EasyMMAdapter):
    proposal, records = prepared
    console.print(f"\n[bold cyan]▶ {name}[/bold cyan]")
    result = adapter.verify_decision(proposal, records, NOW)

    status_color = "green" if result.status == "APPROVED" else "red"
    console.print(f"  Status      : [{status_color}]{result.status}[/{status_color}]")
    console.print(f"  Trace ID    : {result.trace_id[:16]}…")
    console.print(f"  Confidence  : {result.confidence}")
    console.print(f"  Latency     : {result.latency_ms} ms")

    if result.rejection_reason:
        console.print(f"  [red]Reason     : {result.rejection_reason}[/red]")

    # Show policy summary
    passed = sum(1 for c in result.policy_checks if c["passed"])
    total = len(result.policy_checks)
    console.print(f"  Policy      : {passed}/{total} checks passed")

    return result


def main():
    console.print(Panel.fit(
        "[bold]Gravit × EasyMM — Epistemic Verification Pilot[/bold]\n"
        "Verifiable AI decisions for crypto market making",
        border_style="blue",
    ))

    adapter = EasyMMAdapter()

    results = []

    # 1. Normal quote adjustment
    results.append(run_scenario(
        "1. Quote Size & Spread Adjustment",
        prepare(build_quote_adjustment_scenario(), 1),
        adapter,
    ))

    # 2a. Valid inventory rebalance
    results.append(run_scenario(
        "2a. Inventory Rebalance (valid)",
        prepare(build_inventory_rebalance_scenario(violate_limit=False), 2),
        adapter,
    ))

    # 2b. Intentional policy violation
    results.append(run_scenario(
        "2b. Inventory Rebalance (policy violation demo)",
        prepare(build_inventory_rebalance_scenario(violate_limit=True), 3),
        adapter,
    ))

    # 3. Crisis widen
    results.append(run_scenario(
        "3. Crisis / High-Volatility Spread Widening",
        prepare(build_crisis_widen_scenario(), 4),
        adapter,
    ))

    # 4. Pre-TGE
    results.append(run_scenario(
        "4. Pre-TGE / Launch Quoting",
        prepare(build_pre_tge_scenario(), 5),
        adapter,
    ))

    # 5. Market data only asserted by the agent (no independent feed)
    results.append(run_scenario(
        "5. Market data not confirmed by any feed",
        prepare(build_quote_adjustment_scenario(), 6, feeds=()),
        adapter,
    ))

    # 6. Two keys, one data operator? No: one feed only
    results.append(run_scenario(
        "6. Market data confirmed by a single feed",
        prepare(build_quote_adjustment_scenario(), 7, feeds=("feed-exchange-a",)),
        adapter,
    ))

    # 7. Feeds attest a different price than the agent used
    results.append(run_scenario(
        "7. Agent used a price the feeds do not confirm",
        prepare(build_quote_adjustment_scenario(), 8, tamper_price=0.0921),
        adapter,
    ))

    # Summary table
    table = Table(title="\nPilot Summary", show_header=True, header_style="bold")
    table.add_column("Scenario", style="cyan")
    table.add_column("Status")
    table.add_column("Confidence")
    table.add_column("Latency (ms)")

    names = [
        "Quote Adjustment",
        "Inventory (valid)",
        "Inventory (violation)",
        "Crisis Widen",
        "Pre-TGE Launch",
        "No feed confirmation",
        "Single feed only",
        "Price not confirmed",
    ]
    for name, r in zip(names, results):
        status = f"[green]{r.status}[/green]" if r.status == "APPROVED" else f"[red]{r.status}[/red]"
        table.add_row(name, status, str(r.confidence), str(r.latency_ms))

    console.print(table)
    import json
    from pathlib import Path
    out = Path(__file__).resolve().parent.parent / "results"
    out.mkdir(exist_ok=True)
    (out / "pilot-results.json").write_text(json.dumps(
        [{"scenario": n, "decision_id": r.decision_id, "status": r.status, "trace_id": r.trace_id,
          "confidence": r.confidence, "reason": r.rejection_reason} for n, r in zip(names, results)],
        indent=2, ensure_ascii=False) + "\n")
    console.print("\n[bold green]Pilot finished.[/bold green] Results in results/pilot-results.json (reproducible).")


if __name__ == "__main__":
    main()
