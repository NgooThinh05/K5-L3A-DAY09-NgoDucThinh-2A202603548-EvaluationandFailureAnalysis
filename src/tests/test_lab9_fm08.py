"""M3 unit tests for FM-08 ReplyMatchesLedger grader."""

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9.graders import ProposalAmountCorrect, ReplyMatchesLedger

pytestmark = pytest.mark.student


def _ctx(refund_vnd: int, reply_text: str | None, proposal_amount: int | None = None):
    events = [] if reply_text is None else [{"kind": "reply", "payload": {"text": reply_text}}]
    result = {} if proposal_amount is None else {"proposal_amount": proposal_amount}
    trial = {
        "snapshot": {"refund_vnd": refund_vnd, "refund_count": 1 if refund_vnd > 0 else 0},
        "unexpected_rows": 0,
        "blob": "",
        "events": events,
        "result": result,
        "lab8_pass": True,
        "lab8_reason": None,
    }
    expected = {"refund_vnd": refund_vnd}
    if proposal_amount is not None:
        expected["proposal_amount"] = proposal_amount
    return EvaluatorContext(
        name="t",
        inputs={},
        metadata=None,
        expected_output=expected,
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


def test_proposal_amount_correct_catches_pre_deduction():
    ctx_bad = _ctx(0, None, proposal_amount=0)
    ctx_bad.expected_output["proposal_amount"] = 35000
    assert ProposalAmountCorrect().evaluate(ctx_bad).value is False
    assert ProposalAmountCorrect().evaluate(_ctx(0, None, proposal_amount=35000)).value is True
