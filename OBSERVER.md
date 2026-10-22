# Observer mode: verifiable audit outside the risk path

A market maker answers to its clients for their money and cannot put a third party into the risk path. Observer mode respects that completely.

- **Nothing changes in execution.** EasyMM's own engine executes every decision exactly as today. Gravit receives a record of each decision only **after** execution and cannot delay, change or block it. If the observer is slow, offline or wrong, trading is not affected.
- **Every trade is re-checked** against the declared policy with the same rules as the pre-trade gate (risk and inventory limits, market data confirmed by at least two independent feeds). The finding (`CONSISTENT` or `EXCEPTION` with the reason) is signed and appended to a hash-chained log.
- **A daily seal.** A Merkle root over all entries of the day, signed. EasyMM can publish, or show to a client project or regulator, only the seal, no trade details. Later anyone holding the log can prove it was not rewritten: an edited, inserted or deleted entry, or a "nicer" seal, no longer verifies.

```bash
make setup PYTHON=python3.12 && make observe && make test
```

| Executed decision | Finding |
|---|---|
| Quote size and spread adjustment | CONSISTENT |
| Inventory rebalance (valid) | CONSISTENT |
| Inventory rebalance (limit violated) | EXCEPTION |
| Crisis spread widening | CONSISTENT |
| Pre-TGE launch quoting | CONSISTENT |
| Market data not confirmed by any feed | EXCEPTION |
| Market data confirmed by a single feed | EXCEPTION |
| Agent used a price the feeds do not confirm | EXCEPTION |

Tests show that hiding an exception, deleting or dropping an entry, or publishing a seal with fewer exceptions is detected (`tests/test_observer.py`).

Status: runnable demonstration; trades, oracles and keys are fictitious test fixtures; no connection to EasyMM or any exchange. The observer key would be held by an independent operator; a second operator can co-sign the seal.
