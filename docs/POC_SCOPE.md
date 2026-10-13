# PoC Scope — Gravit × EasyMM

## Goal

Demonstrate that every material market-making decision produced by EasyMM AI / algorithms can be verified by Gravit **before** it reaches the execution layer, producing a cryptographically attested proof that EasyMM can show to clients and (if needed) regulators.

## In Scope (Phase 1)

1. **Quote Size & Spread Adjustment**
2. **Inventory Rebalancing / Skew Decision**
3. **Crisis / High-Volatility Spread Widening**
4. **Pre-TGE / Launch Window Quoting Rules**

Each scenario:
- Receives a realistic decision proposal
- Runs through the full Epistemic Gate
- Emits either `APPROVED + Proof` or `REJECTED + structured reason`
- Records complete reasoning lineage

## Out of Scope (Phase 1)

- Real exchange connectivity / live order placement
- Full production adapter to EasyMM internal systems
- On-chain settlement of proofs (can be added later; see the GEVP agentic-finance profile)
- Multi-venue smart order routing verification
- Client portal UI (only a simple CLI + optional demo dashboard)

## Success Criteria

- All four scenarios run end-to-end in < 5 minutes
- Structural Gate correctly blocks policy violations
- Attestation is reproducible (same inputs → same trace_id)
- README + docs allow a third party to understand the value in < 10 minutes
- Code structure matches existing Gravit PoCs (dwf, sygnum, grok)

## Deliverables

- This repository
- Runnable pilot (`python pilot/run_pilot.py`)
- Architecture & integration notes
- Short one-pager that can be sent to Daniil Kozin
