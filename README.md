# Gravit × EasyMM — Proof of Concept

**Verifiable Epistemic Layer for AI-Driven Crypto Market Making**

EasyMM provides institutional-grade liquidity, tight spreads and transparent market-making.  
Gravit adds a cryptographically attested epistemic verification layer so that every AI-generated quoting decision, inventory adjustment and risk action is:

- Semantically consistent
- Policy-compliant
- Adversarially resilient
- Fully auditable (reasoning lineage + Merkle proof)

This PoC demonstrates how EasyMM can offer clients **verifiable AI market making** — a clear differentiator against commodity MM firms.

---

## Why this matters

| Traditional MM | EasyMM + Gravit |
|----------------|-----------------|
| Black-box algorithms | Every decision carries a cryptographic proof |
| Limited audit trail | Complete reasoning lineage + policy check |
| Trust based on reputation | Trust based on verifiable epistemic guarantees |
| Hard to prove compliance | MiCAR / institutional-ready audit artifacts |

---

## Core Capabilities (PoC)

- ✅ **EasyMM Adapter** — clean interface that receives market-making decisions from EasyMM engines
- ✅ **Epistemic Verification Gate** — hard policy first; then the market data the decision relies on must be a *Verified Fact* for the public [Gravit Verifier](https://github.com/gravit-open-network-foundation/verifier) v0.6.0: signed records from ≥ 2 independent, registered data operators, bound to exactly that snapshot, fresh. The agent's self-reported confidences are recorded but never used to approve.
- ✅ **Reasoning Lineage** — full trace of why a quote size / spread / skew was chosen
- ⬜ **Grok / Multi-LLM Validation** — planned, not implemented (an earlier version marked it as done)
- ✅ **Cryptographic Attestation** — SHA-256 trace over the claim, lineage and policy checks, reproducible (uses the claim's own timestamp)
- ✅ **Client-facing Audit Trail** — real-time and historical proofs that EasyMM can show to projects & regulators
- ✅ **Risk & Inventory Policy Engine** — hard limits that cannot be overridden by the LLM/agent

---

## Architecture Overview

```
EasyMM Market-Making Engine
          │
          │  Decision Proposal
          ▼
┌─────────────────────────────────────┐
│         EasyMM Adapter              │
│  (normalizes quotes, inventory,     │
│   risk context, strategy state)     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│     Gravit Epistemic Core           │
│  • Structural Gate                  │
│  • Policy Compliance                │
│  • Semantic Consistency             │
│  • Adversarial Resilience           │
│  • Reasoning Lineage                │
└──────────────────┬──────────────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   APPROVED + Proof    REJECTED + Reason
          │
          ▼
   EasyMM Execution Layer
   (orders, inventory updates)
```

---

## Repository Structure

```
gravit-easymm-poc/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── docs/
│   ├── ARCHITECTURE.md
│   ├── POC_SCOPE.md
│   └── INTEGRATION.md
├── easymm_adapter/
│   ├── __init__.py
│   ├── client.py
│   ├── models.py
│   └── normalizer.py
├── epistemic_core/
│   ├── __init__.py
│   ├── gate.py
│   ├── policy.py
│   ├── lineage.py
│   └── attestation.py
├── market_making/
│   ├── __init__.py
│   ├── decisions.py
│   ├── inventory.py
│   └── risk_limits.py
├── scenarios/
│   ├── quote_adjustment.py
│   ├── inventory_rebalance.py
│   ├── crisis_spread_widen.py
│   └── pre_tge_launch.py
├── pilot/
│   ├── run_pilot.py
│   └── demo_dashboard.py
├── observability/
│   └── metrics.py
└── tests/
    └── test_gate.py
```

---

## Quick Start (5 minutes)

```bash
git clone https://github.com/gravit-open-network-foundation/gravit-easymm-poc.git
cd gravit-easymm-poc
make setup PYTHON=python3.12   # installs the Gravit Verifier at tag v0.6.0
make run                       # 8 scenarios -> results/pilot-results.json
make test
```

---

## Priority Verification Scenarios (Phase 1)

1. **Quote Size & Spread Adjustment**  
   AI proposes new bid/ask sizes and spreads → Gravit checks inventory, volatility regime, risk limits and reasoning consistency.

2. **Inventory Rebalancing Decision**  
   Engine wants to skew or flatten inventory → verification of risk policy + market impact rationale.

3. **Crisis / High-Volatility Spread Widening**  
   Sudden volatility spike → AI widens spreads → proof that the action is justified and within pre-agreed client parameters.

4. **Pre-TGE / Launch Quoting**  
   Special rules for thin books and launch windows → stricter policy + full lineage for exchange and project audit.

5–7. **Market data not independently confirmed** — no feed, a single feed, or feeds that attest a
   different price than the agent used → REJECTED, however confident the agent's reasoning sounds.

**Status:** runnable demonstration; market-data feeds, operators and keys are fictitious
**test fixtures**; no connection to EasyMM systems. CI regenerates `results/` on every change.

---

## Relation to Existing Gravit PoCs

This repository follows the same pattern as:

- `gravit-dwf-poc` — capital markets & liquidity
- `gravit-sygnum-poc` — regulated AI-agent transactions
- `gravitnet-grok-poc` — multi-LLM verifiable integration
- `gevp-agentic-finance-profile` (formerly ERC-8004-GT) — GEVP profile for agentic finance

---

## Contact & Next Steps

After the pilot is reviewed, the natural path is:

1. Joint technical workshop with EasyMM engineering
2. Mapping of real internal decision objects → Gravit Claim schema
3. Production adapter + optional on-chain attestation layer

**Gravit Open Network Foundation**  
https://gravit.space  
https://github.com/GravitOpenNetwork

---

*Hard Markets. Verifiable Wins.*
# gravit-easymm-poc
