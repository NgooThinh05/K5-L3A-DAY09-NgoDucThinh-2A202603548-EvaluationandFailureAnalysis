"""M3 unit tests for FM-08 ReplyMatchesLedger grader."""

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9.graders import ReplyMatchesLedger

pytestmark = pytest.mark.student


def _ctx(refund_vnd: int, reply_text: str | None):
    events = [] if reply_text is None else [{"kind": "reply", "payload": {"text": reply_text}}]
    trial = {
        "snapshot": {"refund_vnd": refund_vnd, "refund_count": 1 if refund_vnd > 0 else 0},
        "unexpected_rows": 0,
        "blob": "",
        "events": events,
        "result": {},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    return EvaluatorContext(
        name="t",
        inputs={},
        metadata=None,
        expected_output={"refund_vnd": refund_vnd},
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_reply_matches_ledger_passes_when_exact():
    assert ReplyMatchesLedger().evaluate(_ctx(20000, "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808.")).value is True


def test_reply_matches_ledger_flags_fm08_mismatch():
    res = ReplyMatchesLedger().evaluate(_ctx(20000, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."))
    assert res.value is False
    assert "35000" in (res.reason or "") and "20000" in (res.reason or "")


def test_reply_matches_ledger_allows_no_reply_event():
    assert ReplyMatchesLedger().evaluate(_ctx(35000, None)).value is True
