# Architecture — Gravit × EasyMM PoC

## 1. High-level Flow

```
┌──────────────────────┐
│  EasyMM MM Engine    │  (proprietary quoting, inventory, risk)
└──────────┬───────────┘
           │ DecisionProposal
           ▼
┌──────────────────────┐
│   EasyMM Adapter     │  • Normalize internal objects
│                      │  • Enrich with market context
│                      │  • Produce Gravit Claim
└──────────┬───────────┘
           │ Claim + Context
           ▼
┌──────────────────────┐
│  Epistemic Core      │
│  ┌────────────────┐  │
│  │ Structural Gate│  │  ← hard policy (inventory, limits, KYC flags)
│  └───────┬────────┘  │
│          ▼           │
│  ┌────────────────┐  │
│  │ Semantic Check │  │  ← consistency of reasoning chain
│  └───────┬────────┘  │
│          ▼           │
│  ┌────────────────┐  │
│  │ Adversarial    │  │  ← detect manipulative / inconsistent logic
│  └───────┬────────┘  │
│          ▼           │
│  ┌────────────────┐  │
│  │ Lineage +      │  │  ← SHA-256 trace + Merkle proof
│  │ Attestation    │  │
│  └───────┬────────┘  │
└──────────┼───────────┘
           │
     ┌─────┴─────┐
     │           │
 APPROVED     REJECTED
 + Proof      + Reason code
     │
     ▼
 EasyMM Execution
```

## 2. Key Components

### EasyMM Adapter (`easymm_adapter/`)
- Accepts EasyMM-native decision objects (quotes, skew, inventory targets).
- Converts them into a standard Gravit `Claim` + `Context`.
- Never executes anything — pure translation + enrichment layer.

### Epistemic Core (`epistemic_core/`)
- **Structural Gate** — deterministic policy checks that an LLM cannot override.
- **Policy Engine** — client-specific and global risk limits.
- **Lineage** — ordered list of reasoning steps with source types.
- **Attestation** — cryptographic commitment (SHA-256 trace; decision records per GEVP/VEDS).

### Market Making Domain (`market_making/`)
- Domain models for quote decisions, inventory state, volatility regimes.
- Used both by scenarios and by the adapter.

### Scenarios (`scenarios/`)
- Concrete, runnable examples of the four priority verification cases.

## 3. Trust Properties

| Property | How it is enforced |
|----------|--------------------|
| No self-attestation | Agent cannot put its own confidence into the decision function |
| LLM cannot override | Structural Gate is the only component that can approve |
| Full auditability | Every input is hashed into the trace_id |
| Policy is hard | Risk limits are evaluated before any semantic score |
| Deterministic proofs | Same inputs always produce the same attestation |

## 4. Extensibility

- Add new policy rules → `epistemic_core/policy.py`
- Add new decision types → `market_making/decisions.py` + adapter
- Plug real EasyMM internal API → replace simulation in adapter
- Optional on-chain anchoring → anchor the GEVP decision record
