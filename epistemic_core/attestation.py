from __future__ import annotations
from typing import Any
import hashlib
import json
from datetime import datetime, timezone


def create_attestation(claim: dict[str, Any], lineage: dict[str, Any], policy_checks: list[dict]) -> dict[str, Any]:
    """
    Create a simple but deterministic cryptographic attestation.
    Reproducible SHA-256 trace over the claim, lineage and policy checks.
    """
    material = {
        "claim_id": claim.get("claim_id"),
        "claim_type": claim.get("claim_type"),
        "symbol": claim.get("symbol"),
        "lineage_final_hash": lineage.get("final_hash"),
        "policy_checks": policy_checks,
        "timestamp": claim.get("timestamp"),  # the claim's own time, so the trace_id is reproducible
    }
    raw = json.dumps(material, sort_keys=True).encode()
    trace_id = hashlib.sha256(raw).hexdigest()

    return {
        "trace_id": trace_id,
        "merkle_root": lineage.get("final_hash"),
        "scheme": "gravit-easymm-v0.1",
        "material_hash": hashlib.sha256(raw).hexdigest(),
        "created_at": material["timestamp"],
    }
