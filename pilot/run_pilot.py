#!/usr/bin/env python3
"""
Gravit × EasyMM PoC — Pilot Runner
Runs the four priority verification scenarios.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from easymm_adapter.client import EasyMMAdapter
from scenarios.quote_adjustment import build_quote_adjustment_scenario
from scenarios.inventory_rebalance import build_inventory_rebalance_scenario
from scenarios.crisis_spread_widen import build_crisis_widen_scenario
from scenarios.pre_tge_launch import build_pre_tge_scenario

console = Console()


def run_scenario(name: str, proposal, adapter: EasyMMAdapter):
    console.print(f"\n[bold cyan]▶ {name}[/bold cyan]")
    result = adapter.verify_decision(proposal)

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
        build_quote_adjustment_scenario(),
        adapter,
    ))

    # 2a. Valid inventory rebalance
    results.append(run_scenario(
        "2a. Inventory Rebalance (valid)",
        build_inventory_rebalance_scenario(violate_limit=False),
        adapter,
    ))

    # 2b. Intentional policy violation
    results.append(run_scenario(
        "2b. Inventory Rebalance (policy violation demo)",
        build_inventory_rebalance_scenario(violate_limit=True),
        adapter,
    ))

    # 3. Crisis widen
    results.append(run_scenario(
        "3. Crisis / High-Volatility Spread Widening",
        build_crisis_widen_scenario(),
        adapter,
    ))

    # 4. Pre-TGE
    results.append(run_scenario(
        "4. Pre-TGE / Launch Quoting",
        build_pre_tge_scenario(),
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
    ]
    for name, r in zip(names, results):
        status = f"[green]{r.status}[/green]" if r.status == "APPROVED" else f"[red]{r.status}[/red]"
        table.add_row(name, status, str(r.confidence), str(r.latency_ms))

    console.print(table)
    console.print("\n[bold green]Pilot finished.[/bold green] All decision traces are reproducible via trace_id.")


if __name__ == "__main__":
    main()
