from __future__ import annotations
from typing import Any
from .policy import PolicyEngine
from .lineage import build_lineage
from .attestation import create_attestation
from .market_evidence import MarketEvidenceVerifier


class EpistemicGate:
    """
    Structural Gate — the only component that can approve a decision.
    LLM output (if any) is advisory only and never enters the decision function.
    """

    def __init__(self, evidence: MarketEvidenceVerifier | None = None):
        self.policy = PolicyEngine()
        self.evidence = evidence or MarketEvidenceVerifier()

    def verify(self, claim: dict[str, Any], market_records: list | None = None,
               evaluation_time: str | None = None) -> dict[str, Any]:
        # 1. Hard policy first
        policy_checks = self.policy.check(claim)
        if not self.policy.all_passed(policy_checks):
            failed = [c for c in policy_checks if not c["passed"]]
            reason = "; ".join(f"{c['rule']}={c['value']} (limit {c['limit']})" for c in failed)
            lineage = build_lineage(claim)
            attestation = create_attestation(claim, lineage, policy_checks)
            return {
                "status": "REJECTED",
                "trace_id": attestation["trace_id"],
                "confidence": 0.0,
                "policy_checks": policy_checks,
                "attestation": attestation,
                "rejection_reason": f"Policy violation: {reason}",
            }

        # 2. Basic semantic / completeness checks
        reasoning = claim.get("reasoning_chain", [])
        if not reasoning:
            lineage = build_lineage(claim)
            attestation = create_attestation(claim, lineage, policy_checks)
            return {
                "status": "REJECTED",
                "trace_id": attestation["trace_id"],
                "confidence": 0.0,
                "policy_checks": policy_checks,
                "attestation": attestation,
                "rejection_reason": "Empty reasoning chain — no basis for action",
            }

        # 3. The market data the decision relies on must be independently corroborated
        #    (Gravit Verifier v0.6.0). The agent's self-reported confidences are NOT used.
        ev = self.evidence.verify(claim, market_records or [], evaluation_time or claim["timestamp"])
        confidence = round(float(ev["honest_share"]), 3) if ev["verified"] else 0.0
        if not ev["verified"]:
            lineage = build_lineage(claim)
            attestation = create_attestation(claim, lineage, policy_checks)
            return {
                "status": "REJECTED",
                "trace_id": attestation["trace_id"],
                "confidence": 0.0,
                "policy_checks": policy_checks,
                "attestation": attestation,
                "market_evidence": ev,
                "rejection_reason": f"Market data not independently corroborated: {ev['status']} ({ev['state']}) — {ev['reason']}",
            }

        # 4. All good → approve + attest
        lineage = build_lineage(claim)
        attestation = create_attestation(claim, lineage, policy_checks)

        return {
            "status": "APPROVED",
            "trace_id": attestation["trace_id"],
            "confidence": round(confidence, 3),
            "policy_checks": policy_checks,
            "attestation": attestation,
            "market_evidence": ev,
            "rejection_reason": None,
        }
