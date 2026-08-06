from __future__ import annotations
from typing import Any


class PolicyEngine:
    """
    Hard policy rules that cannot be overridden by any LLM or agent.
    These run first in the Structural Gate.
    """

    def check(self, claim: dict[str, Any]) -> list[dict[str, Any]]:
        checks = []
        ctx = claim.get("context", {})
        action = claim.get("proposed_action", {})
        limits = ctx.get("client_limits", {})

        inv = abs(ctx.get("inventory_ratio", 0.0))
        max_inv = limits.get("max_inventory_ratio", 0.35)
        checks.append({
            "rule": "max_inventory_ratio",
            "passed": inv <= max_inv,
            "value": inv,
            "limit": max_inv,
        })

        # Spread checks
        for side in ("bid_spread_bps", "ask_spread_bps"):
            spread = action.get(side)
            if spread is not None:
                max_spread = limits.get("max_spread_bps", 120.0)
                checks.append({
                    "rule": f"max_{side}",
                    "passed": spread <= max_spread,
                    "value": spread,
                    "limit": max_spread,
                })

        # Crisis widen permission
        if claim.get("claim_type") == "CRISIS_WIDEN":
            allowed = limits.get("allow_crisis_widen", True)
            checks.append({
                "rule": "allow_crisis_widen",
                "passed": allowed,
                "value": allowed,
                "limit": True,
            })

        # Target inventory must also respect limit
        target = action.get("target_inventory_ratio")
        if target is not None:
            checks.append({
                "rule": "target_inventory_within_limit",
                "passed": abs(target) <= max_inv,
                "value": abs(target),
                "limit": max_inv,
            })

        return checks

    def all_passed(self, checks: list[dict[str, Any]]) -> bool:
        return all(c["passed"] for c in checks)
