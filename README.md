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
- ✅ **Epistemic Verification Gate** — structural + semantic + policy checks before any order is allowed to leave
- ✅ **Reasoning Lineage** — full trace of why a quote size / spread / skew was chosen
- ✅ **Grok / Multi-LLM Validation** — optional secondary verification via Grok (or any other LLM)
- ✅ **Cryptographic Attestation** — SHA-256 / Merkle proofs compatible with ERC-8004-GT style
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
git clone https://github.com/GravitOpenNetwork/gravit-easymm-poc.git
cd gravit-easymm-poc

cp .env.example .env
# (optional) add GROK_API_KEY if you want multi-LLM validation

pip install -r requirements.txt

# Run the pilot with three core scenarios
python pilot/run_pilot.py
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

---

## Relation to Existing Gravit PoCs

This repository follows the same pattern as:

- `gravit-dwf-poc` — capital markets & liquidity
- `gravit-sygnum-poc` — regulated AI-agent transactions
- `gravitnet-grok-poc` — multi-LLM verifiable integration
- `ERC-8004-GT` — epistemic proofs for agentic finance

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
