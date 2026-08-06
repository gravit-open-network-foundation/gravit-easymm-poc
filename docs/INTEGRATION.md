# Integration Notes — EasyMM ↔ Gravit

## Current Status

EasyMM does not publish a public GitHub repository or open API for its market-making engines.  
Therefore this PoC uses a clean **adapter pattern**:

1. EasyMM side produces a `DecisionProposal` (JSON / internal object).
2. Adapter normalizes it into a Gravit `Claim`.
3. Epistemic Core verifies and returns an attestation.
4. Only after `APPROVED` does EasyMM allow the decision to proceed to execution.

## Recommended Integration Path

### Stage 1 — Simulation (this repo)
- All decisions are synthetic but realistic.
- Demonstrates value and technical feasibility.

### Stage 2 — Shadow Mode
- EasyMM continues to execute as today.
- Every decision is also sent to Gravit in parallel.
- Proofs are stored but do not block execution.
- Allows measurement of latency and rejection rate.

### Stage 3 — Gate Mode
- Critical decision types (inventory, crisis spreads, launch quoting) become blocking.
- Non-critical decisions can remain in shadow.

### Stage 4 — Client-facing Proofs
- EasyMM dashboard shows “Verified by Gravit” badges + downloadable attestations.
- Optional on-chain anchoring for highest-value clients.

## Data Contract (simplified)

```json
{
  "decision_id": "uuid",
  "type": "QUOTE_ADJUSTMENT | INVENTORY_REBALANCE | CRISIS_WIDEN | PRE_TGE_QUOTE",
  "symbol": "TOKEN/USDT",
  "proposed_action": { ... },
  "current_state": {
    "inventory": 0.18,
    "mid_price": 1.234,
    "volatility_regime": "elevated",
    "client_risk_limits": { ... }
  },
  "reasoning_chain": [
    {"step": 1, "text": "...", "source": "market_data"},
    {"step": 2, "text": "...", "source": "model_output"}
  ]
}
```

Gravit returns:

```json
{
  "status": "APPROVED | REJECTED",
  "trace_id": "sha256...",
  "confidence": 0.91,
  "policy_checks": [...],
  "attestation": { "merkle_root": "...", "proof": [...] },
  "rejection_reason": null
}
```

## Latency Target

- Structural Gate: < 5 ms
- Full verification (including optional LLM): < 150 ms (p99)
- Suitable for most market-making loops that are not pure HFT.
