"""M1 trace-case regression test for C-002@11 (FM-03 ticket_trust)."""

import pytest

from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def test_seeded_regression_c002_fails_with_model_override():
    bad = investigate("seeded_regression", "C-002", 11)["trial"]
    assert bad["lab8_pass"] is False
    assert any(e.get("kind") == "model_override" for e in bad["events"])

    good = investigate("fixed", "C-002", 11)["trial"]
    assert good["lab8_pass"] is True
    assert not any(e.get("kind") == "model_override" for e in good["events"])
