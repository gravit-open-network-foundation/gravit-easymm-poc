from __future__ import annotations
from typing import Any
from .policy import PolicyEngine
from .lineage import build_lineage
from .attestation import create_attestation


class EpistemicGate:
    """
    Structural Gate — the only component that can approve a decision.
    LLM output (if any) is advisory only and never enters the decision function.
    """

    def __init__(self, min_confidence: float = 0.73):
        self.policy = PolicyEngine()
        self.min_confidence = min_confidence

    def verify(self, claim: dict[str, Any]) -> dict[str, Any]:
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

        # 3. Simple confidence heuristic (can be replaced by multi-LLM later)
        confidences = [s.get("confidence") for s in reasoning if s.get("confidence") is not None]
        confidence = sum(confidences) / len(confidences) if confidences else 0.85

        if confidence < self.min_confidence:
            lineage = build_lineage(claim)
            attestation = create_attestation(claim, lineage, policy_checks)
            return {
                "status": "REJECTED",
                "trace_id": attestation["trace_id"],
                "confidence": confidence,
                "policy_checks": policy_checks,
                "attestation": attestation,
                "rejection_reason": f"Confidence {confidence:.2f} below threshold {self.min_confidence}",
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
            "rejection_reason": None,
        }
