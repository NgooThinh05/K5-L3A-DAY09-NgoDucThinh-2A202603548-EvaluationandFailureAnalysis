"""M7 extra integrity tests covering hidden traps (duplicate rows, evaluator_failures, slice tampering)."""

import copy
import pytest

from lab9 import gate

pytestmark = pytest.mark.student

ROWS = [
    {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": ["denial"] if i < 2 else ["money_movement"]}
    for i in range(4)
    for s in (1, 2)
]
SPEC = {
    "eval_set_version": "v2",
    "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.8}}],
    "slices": [{"name": "denial", "metric": "pass_rate", "min": 0.9, "no_significant_drop": True, "blocking": True}],
}


def _rep(rows):
    return {
        "manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]},
        "rows": rows,
        "metrics": {"pass_rate": 1.0},
        "evaluator_failures": [],
    }


def test_advanced_integrity_rejects_duplicate_rows():
    base = _rep(copy.deepcopy(ROWS))
    dup = _rep(copy.deepcopy(ROWS[:-1]) + [copy.deepcopy(ROWS[0])])
    assert gate.integrity_check(dup, base, SPEC)


def test_advanced_integrity_rejects_evaluator_failures_on_green_run():
    base = _rep(copy.deepcopy(ROWS))
    bad = _rep(copy.deepcopy(ROWS))
    bad["evaluator_failures"] = ["E-001@1:SomeGrader:boom"]
    assert gate.integrity_check(bad, base, SPEC)


def test_advanced_integrity_rejects_slice_relabeling():
    base = _rep(copy.deepcopy(ROWS))
    tampered = _rep(copy.deepcopy(ROWS))
    tampered["rows"][0]["slices"] = []
    assert gate.integrity_check(tampered, base, SPEC)


def test_advanced_ratchet_rejects_dropped_slice_and_no_significant_drop():
    base = _rep(copy.deepcopy(ROWS))
    loose = copy.deepcopy(SPEC)
    loose["slices"][0].pop("no_significant_drop")
    assert gate.integrity_check(base, base, loose, SPEC)
