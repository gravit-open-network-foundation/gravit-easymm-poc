from __future__ import annotations
import time
from .models import DecisionProposal, VerificationResult
from .normalizer import normalize_proposal
from epistemic_core.gate import EpistemicGate


class EasyMMAdapter:
    """
    Thin adapter that EasyMM systems would call.
    In production this would sit next to the MM engine.
    """

    def __init__(self, gate: EpistemicGate | None = None):
        self.gate = gate or EpistemicGate()

    def verify_decision(self, proposal: DecisionProposal) -> VerificationResult:
        start = time.perf_counter()
        claim = normalize_proposal(proposal)
        result = self.gate.verify(claim)
        latency = (time.perf_counter() - start) * 1000

        return VerificationResult(
            decision_id=proposal.decision_id,
            status=result["status"],
            trace_id=result["trace_id"],
            confidence=result["confidence"],
            policy_checks=result["policy_checks"],
            attestation=result["attestation"],
            rejection_reason=result.get("rejection_reason"),
            latency_ms=round(latency, 2),
        )
