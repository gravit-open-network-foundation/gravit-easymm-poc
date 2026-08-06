from __future__ import annotations
from typing import Any
import hashlib
import json


def build_lineage(claim: dict[str, Any]) -> dict[str, Any]:
    """
    Build an ordered, hash-linked reasoning lineage.
    """
    steps = claim.get("reasoning_chain", [])
    lineage = []
    prev_hash = "genesis"

    for i, step in enumerate(steps):
        payload = {
            "index": i,
            "text": step.get("text", ""),
            "source_type": step.get("source_type", "unknown"),
            "prev_hash": prev_hash,
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        step_hash = hashlib.sha256(raw).hexdigest()
        payload["hash"] = step_hash
        lineage.append(payload)
        prev_hash = step_hash

    return {
        "steps": lineage,
        "final_hash": prev_hash,
        "length": len(lineage),
    }
