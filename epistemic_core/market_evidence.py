"""
Market data the decision relies on, corroborated by independent data operators.

The agent's own confidence values are never used to approve a decision (they
are self-reported). Instead, the market snapshot the decision is based on must
be a "Verified Fact" for the public Gravit Verifier v0.5.0: signed records from
at least two independent, registered data operators, bound to exactly this
snapshot, and fresh. TEST keys only (derived from public seeds).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from gravit_verifier import EpistemicState, EvidenceRecord, VerificationRequest, VerifierKernel
from gravit_verifier.loader import load_bindings_from_dir
from gravit_verifier.registry import (TrustRoot, VerifierRegistry, key_id_for, registry_signing_message,
                                      signing_message)

FEEDS = {  # data producer -> operator (legal entity); fictitious, test keys
    "feed-exchange-a": "Example Exchange A Ltd",
    "feed-exchange-b": "Example Exchange B GmbH",
    "feed-aggregator-c": "Example Market Data AG",
}
BINDINGS = Path(os.environ.get("GRAVIT_BINDINGS", Path(__file__).resolve().parent.parent / ".deps" / "verifier" / "bindings"))


def snapshot(claim: dict[str, Any]) -> dict[str, Any]:
    c = claim["context"]
    return {"symbol": claim["symbol"], "mid_price": c["mid_price"], "best_bid": c["best_bid"],
            "best_ask": c["best_ask"], "volatility_regime": c["volatility_regime"], "as_of": claim["timestamp"]}


def snapshot_hash(snap: dict[str, Any]) -> str:
    return hashlib.sha3_256(json.dumps(snap, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _key(name: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"gravit-easymm-test:" + name.encode()).digest())


def _pub(name: str) -> bytes:
    return _key(name).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def _doc(o: Any) -> bytes:
    return (json.dumps(o, indent=1, sort_keys=True) + "\n").encode()


def demo_registry() -> VerifierRegistry:
    roots = [f"root-{i}" for i in range(1, 6)]
    tr = TrustRoot.from_bytes(_doc({"trust_root_version": 1, "threshold": 3, "root_keys": [
        {"key_id": key_id_for(_pub(r)), "public_key": base64.b64encode(_pub(r)).decode()} for r in roots]}))
    reg = _doc({"registry_version": 1, "verifiers": [
        {"key_id": key_id_for(_pub(n)), "public_key": base64.b64encode(_pub(n)).decode(), "operator": op, "revoked": False}
        for n, op in FEEDS.items()]})
    msg = registry_signing_message(reg)
    sigs = "".join(f"{key_id_for(_pub(r))} {base64.b64encode(_key(r).sign(msg)).decode()}\n" for r in roots[:3])
    return VerifierRegistry.from_bytes(reg, sigs, tr)


def attest(feed: str, claim_id: str, snap: dict[str, Any], timestamp: str) -> EvidenceRecord:
    """A data operator's signed statement that this market snapshot is correct."""
    r = EvidenceRecord(record_id=f"{feed}:{claim_id}", theta=0.97, result=True, verifier_id=feed, timestamp=timestamp,
                       provenance=FEEDS.get(feed, "unregistered"), integrity_hash=snapshot_hash(snap),
                       key_id=key_id_for(_pub(feed)))
    r.signature = base64.b64encode(_key(feed).sign(signing_message(f"market:{claim_id}", r))).decode()
    return r


class MarketEvidenceVerifier:
    def __init__(self, registry: VerifierRegistry | None = None, freshness_seconds: int = 60) -> None:
        self.kernel = VerifierKernel(registry or demo_registry())
        for b in load_bindings_from_dir(BINDINGS):
            self.kernel.load_binding(b)
        self.freshness = freshness_seconds

    def verify(self, claim: dict[str, Any], records: list[EvidenceRecord], evaluation_time: str) -> dict[str, Any]:
        snap = snapshot(claim)
        h = snapshot_hash(snap)
        bound = [r for r in records if r.integrity_hash == h]
        d = self.kernel.verify(VerificationRequest(
            artifact_id=f"market:{claim['claim_id']}", claimed_state=EpistemicState.VERIFIED_FACT, evidence=bound,
            context={"evaluation_time": evaluation_time, "freshness_max_age_seconds": self.freshness}))
        nal = d.convergence_metrics.get("CANON-NAL-001", {}) if isinstance(d.convergence_metrics, dict) else {}
        return {"verified": d.final_epistemic_state == EpistemicState.VERIFIED_FACT and d.status.value == "SUCCESS",
                "state": d.final_epistemic_state.value if d.final_epistemic_state else None,
                "status": d.status.value, "reason": d.reason, "decision_id": d.decision_id,
                "records_bound": len(bound), "records_offered": len(records), "snapshot_sha3": h,
                "honest_share": nal.get("h", 0.0)}
