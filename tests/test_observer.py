import copy
import json
from pathlib import Path

from observer import verify
from scenarios.observe import main

RESULTS = Path(__file__).resolve().parent.parent / "results"


def load():
    assert main() == 0
    entries = [json.loads(l) for l in (RESULTS / "observer-log.jsonl").read_text().splitlines()]
    return entries, json.loads((RESULTS / "observer-seal.json").read_text())


def test_findings_match_the_pre_trade_gate_but_nothing_is_blocked():
    entries, seal = load()
    pilot = json.loads((RESULTS / "pilot-results.json").read_text())
    assert [e["body"]["finding"] == "CONSISTENT" for e in entries] == [r["status"] == "APPROVED" for r in pilot]
    assert seal["entries"] == 8 and seal["exceptions"] == 4
    assert verify(entries, seal, seal["public_key"]) == (True, "log matches the seal")


def test_any_rewrite_of_history_is_detected():
    entries, seal = load()
    pk = seal["public_key"]
    edited = copy.deepcopy(entries)
    edited[2]["body"]["finding"] = "CONSISTENT"
    assert not verify(edited, seal, pk)[0]
    assert not verify(entries[:1] + entries[2:], seal, pk)[0]
    assert not verify(entries, dict(seal, exceptions=0), pk)[0]
